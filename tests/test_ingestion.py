"""Unit tests for parsers + the parse-only ingestion service."""

from __future__ import annotations

import pytest

from cue.ingestion import parsers, service
from cue.ingestion.errors import (
    EmptyDocumentError,
    FileTooLargeError,
    UnsupportedDocTypeError,
)
from cue.ingestion.models import DocType
from tests import sample_docs

SENTINEL = "Cue rescues your presentation"

# (filename, bytes-factory, expected DocType)
CASES = [
    ("notes.txt", sample_docs.make_txt_bytes, DocType.txt),
    ("notes.pdf", sample_docs.make_pdf_bytes, DocType.pdf),
    ("notes.docx", sample_docs.make_docx_bytes, DocType.docx),
    ("notes.pptx", sample_docs.make_pptx_bytes, DocType.pptx),
    ("notes.epub", sample_docs.make_epub_bytes, DocType.epub),
]


@pytest.mark.parametrize("filename,factory,expected_type", CASES)
def test_parse_extracts_text(filename, factory, expected_type) -> None:
    doc_type, text = parsers.parse(filename, factory(SENTINEL))
    assert doc_type == expected_type
    assert SENTINEL in text


def test_detect_doc_type_unsupported() -> None:
    with pytest.raises(UnsupportedDocTypeError):
        parsers.detect_doc_type("malware.exe")


def test_normalize_collapses_whitespace_and_controls() -> None:
    raw = "Hello   world\x00\t\n\n\n\nGoodbye   \n"
    assert parsers.normalize_text(raw) == "Hello world\n\nGoodbye"


def test_parse_upload_assigns_id_and_count() -> None:
    doc = service.parse_upload("notes.txt", sample_docs.make_txt_bytes(SENTINEL))
    assert doc.id
    assert doc.doc_type == DocType.txt
    assert doc.char_count == len(doc.text)
    assert SENTINEL in doc.text


def test_parse_upload_rejects_empty_document() -> None:
    with pytest.raises(EmptyDocumentError):
        service.parse_upload("blank.txt", b"   \n\t  ")


def test_parse_upload_rejects_oversized_file(monkeypatch) -> None:
    from cue.config import get_settings

    monkeypatch.setenv("CUE_MAX_UPLOAD_MB", "0")  # nothing is small enough
    get_settings.cache_clear()
    with pytest.raises(FileTooLargeError):
        service.parse_upload("notes.txt", sample_docs.make_txt_bytes(SENTINEL))
