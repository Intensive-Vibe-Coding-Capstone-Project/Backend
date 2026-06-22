"""Ingestion service: validate + parse an uploaded file into a `ParsedDocument`.

Parsing only — storage now lives in the RAG layer (`cue.rag.index`), which
chunks, embeds, and persists to Chroma. The documents route composes the two.
"""

from __future__ import annotations

import uuid

from cue.config import get_settings
from cue.ingestion import parsers
from cue.ingestion.errors import EmptyDocumentError, FileTooLargeError
from cue.ingestion.models import ParsedDocument


def parse_upload(filename: str, data: bytes) -> ParsedDocument:
    """Validate size, parse by type, normalize, and assign an id.

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

    return ParsedDocument(
        id=uuid.uuid4().hex,
        filename=filename,
        doc_type=doc_type,
        char_count=len(text),
        text=text,
    )
