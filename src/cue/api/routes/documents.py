"""Document ingestion endpoints: upload + list."""

from __future__ import annotations

from fastapi import APIRouter, File, HTTPException, UploadFile

from cue.ingestion import service
from cue.ingestion.errors import (
    DocumentParseError,
    EmptyDocumentError,
    FileTooLargeError,
    UnsupportedDocTypeError,
)
from cue.ingestion.models import DocumentMeta
from cue.rag import index

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("", status_code=201, response_model=DocumentMeta)
async def upload_document(file: UploadFile = File(...)) -> DocumentMeta:
    """Upload a document (pdf/docx/txt/pptx/epub): parse, chunk, embed, and index it."""
    data = await file.read()
    filename = file.filename or "upload"
    try:
        parsed = service.parse_upload(filename, data)
    except UnsupportedDocTypeError as exc:
        raise HTTPException(status_code=415, detail=str(exc)) from exc
    except FileTooLargeError as exc:
        raise HTTPException(status_code=413, detail=str(exc)) from exc
    except (EmptyDocumentError, DocumentParseError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    return index.index_document(parsed)


@router.get("", response_model=list[DocumentMeta])
def list_documents() -> list[DocumentMeta]:
    """List indexed documents (metadata + preview, not full text)."""
    return index.list_documents()
