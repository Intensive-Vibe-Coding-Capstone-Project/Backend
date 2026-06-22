"""Ingestion service: turn an uploaded file into a stored `ParsedDocument`.

D2 keeps parsed documents in a process-local in-memory registry. D3 replaces
this with chunk -> embed -> Chroma; the registry interface stays the same shape
(ingest / get / list) so callers don't change.
"""

from __future__ import annotations

import uuid

from cue.config import get_settings
from cue.ingestion import parsers
from cue.ingestion.errors import EmptyDocumentError, FileTooLargeError
from cue.ingestion.models import ParsedDocument

# Process-local store. Swapped for the vector store in D3.
_REGISTRY: dict[str, ParsedDocument] = {}


def ingest(filename: str, data: bytes) -> ParsedDocument:
    """Validate, parse, normalize, and store an uploaded document.

    Raises `FileTooLargeError`, `UnsupportedDocTypeError`, `DocumentParseError`,
    or `EmptyDocumentError` on bad input.
    """
    settings = get_settings()
    max_bytes = settings.max_upload_mb * 1024 * 1024
    if len(data) > max_bytes:
        raise FileTooLargeError(
            f"File is {len(data) / 1_048_576:.1f} MB; limit is {settings.max_upload_mb} MB."
        )

    doc_type, text = parsers.parse(filename, data)
    if not text.strip():
        raise EmptyDocumentError(
            f"No extractable text in '{filename}' (it may be empty, scanned, or image-only)."
        )

    doc = ParsedDocument(
        id=uuid.uuid4().hex,
        filename=filename,
        doc_type=doc_type,
        char_count=len(text),
        text=text,
    )
    _REGISTRY[doc.id] = doc
    return doc


def get_document(doc_id: str) -> ParsedDocument | None:
    return _REGISTRY.get(doc_id)


def list_documents() -> list[ParsedDocument]:
    return list(_REGISTRY.values())


def clear() -> None:
    """Drop all stored documents (used by tests)."""
    _REGISTRY.clear()
