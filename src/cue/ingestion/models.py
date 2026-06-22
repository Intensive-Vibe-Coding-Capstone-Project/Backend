"""Ingestion data models: parsed documents and their public metadata."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel


class DocType(StrEnum):
    """Supported source document types (by file extension)."""

    pdf = "pdf"
    docx = "docx"
    txt = "txt"
    pptx = "pptx"
    epub = "epub"


class ParsedDocument(BaseModel):
    """A document after parsing+normalization. Internal record (holds full text)."""

    id: str
    filename: str
    doc_type: DocType
    char_count: int
    text: str


class DocumentMeta(BaseModel):
    """Public, list-safe view of a document (no full text — only a short preview)."""

    id: str
    filename: str
    doc_type: DocType
    char_count: int
    preview: str

    @classmethod
    def from_doc(cls, doc: ParsedDocument, preview_chars: int) -> DocumentMeta:
        return cls(
            id=doc.id,
            filename=doc.filename,
            doc_type=doc.doc_type,
            char_count=doc.char_count,
            preview=doc.text[:preview_chars],
        )
