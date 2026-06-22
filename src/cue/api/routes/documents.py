"""Document ingestion endpoints: upload + list."""

from __future__ import annotations

from fastapi import APIRouter, File, HTTPException, UploadFile

from cue.config import get_settings
from cue.ingestion import service
from cue.ingestion.errors import (
    DocumentParseError,
    EmptyDocumentError,
    FileTooLargeError,
    UnsupportedDocTypeError,
)
from cue.ingestion.models import DocumentMeta

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("", status_code=201, response_model=DocumentMeta)
async def upload_document(file: UploadFile = File(...)) -> DocumentMeta:
    """Upload + parse a document (pdf/docx/txt/pptx/epub) into normalized text."""
    data = await file.read()
    filename = file.filename or "upload"
    try:
        doc = service.ingest(filename, data)
    except UnsupportedDocTypeError as exc:
        raise HTTPException(status_code=415, detail=str(exc)) from exc
    except FileTooLargeError as exc:
        raise HTTPException(status_code=413, detail=str(exc)) from exc
    except (EmptyDocumentError, DocumentParseError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    return DocumentMeta.from_doc(doc, get_settings().preview_chars)


@router.get("", response_model=list[DocumentMeta])
def list_documents() -> list[DocumentMeta]:
    """List ingested documents (metadata + preview, not full text)."""
    preview_chars = get_settings().preview_chars
    return [DocumentMeta.from_doc(doc, preview_chars) for doc in service.list_documents()]
