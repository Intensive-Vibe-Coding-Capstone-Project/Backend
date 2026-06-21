"""
Document management API routes.
Upload, list, and delete documents.
"""

import logging
from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import Optional

from app.models.schemas import (
    DocumentUploadResponse,
    DocumentResponse,
    DocumentStatus,
    URLImportRequest,
)
from app.services.documents.processor import document_service
from app.services.rag.engine import rag_engine

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_documents(files: list[UploadFile] = File(...)):
    """
    Upload one or more documents for processing.
    Supported formats: PDF, DOCX, TXT, EPUB, PPT, PPTX
    """
    document_ids = []
    errors = []

    for upload_file in files:
        try:
            # Validate file type
            doc_type = document_service.get_document_type(upload_file.filename)

            # Save the file
            file_path, doc_id, size_bytes = await document_service.save_upload(
                upload_file.filename, upload_file
            )
            document_ids.append(doc_id)

            # Register the document
            document_service.register_document(
                doc_id=doc_id,
                filename=upload_file.filename,
                doc_type=doc_type,
                size_bytes=size_bytes,
            )

            # Extract text and add to RAG
            try:
                text = await document_service.extract_text(file_path, doc_type)
                chunk_count = await rag_engine.add_document(
                    doc_id=doc_id,
                    filename=upload_file.filename,
                    text=text,
                )
                document_service.update_status(doc_id, DocumentStatus.READY, chunk_count)
                logger.info(
                    f"Processed {upload_file.filename}: {chunk_count} chunks"
                )
            except Exception as e:
                logger.error(f"Failed to process {upload_file.filename}: {e}")
                document_service.update_status(doc_id, DocumentStatus.ERROR)
                errors.append(f"{upload_file.filename}: {str(e)}")

        except ValueError as e:
            errors.append(str(e))
        except Exception as e:
            errors.append(f"{upload_file.filename}: {str(e)}")

    if not document_ids:
        raise HTTPException(
            status_code=400,
            detail=f"No documents were processed. Errors: {'; '.join(errors)}",
        )

    message = f"{len(document_ids)} document(s) uploaded"
    if errors:
        message += f" ({len(errors)} error(s): {'; '.join(errors)})"

    return DocumentUploadResponse(
        document_ids=document_ids,
        status="processing" if any(
            document_service.get_document(did) and
            document_service.get_document(did).status == DocumentStatus.PROCESSING
            for did in document_ids
        ) else "ready",
        message=message,
    )


@router.post("/url", response_model=DocumentUploadResponse)
async def import_from_url(request: URLImportRequest):
    """Import a document from a URL (Google Drive, YouTube, website)."""
    # TODO: Implement URL fetching for different source types
    raise HTTPException(
        status_code=501,
        detail="URL import is not yet implemented. Coming in Day 3.",
    )


@router.get("/", response_model=list[DocumentResponse])
async def list_documents():
    """List all uploaded documents."""
    return document_service.list_documents()


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(document_id: str):
    """Get a specific document by ID."""
    doc = document_service.get_document(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


@router.delete("/{document_id}")
async def delete_document(document_id: str):
    """Delete a document and its vector embeddings."""
    doc = document_service.get_document(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # Remove from vector store
    await rag_engine.delete_document_chunks(document_id)
    # Remove from document store
    document_service.delete_document(document_id)

    return {"message": f"Document {document_id} deleted successfully"}
