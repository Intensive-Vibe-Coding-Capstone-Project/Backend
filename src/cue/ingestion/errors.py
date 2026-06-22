"""Domain errors for ingestion. The API layer maps these to HTTP status codes."""

from __future__ import annotations


class IngestionError(Exception):
    """Base class for all ingestion failures."""


class UnsupportedDocTypeError(IngestionError):
    """The uploaded file's extension is not a supported document type."""


class FileTooLargeError(IngestionError):
    """The upload exceeds the configured size limit."""


class EmptyDocumentError(IngestionError):
    """Parsing succeeded but yielded no usable text (e.g. a scanned PDF)."""


class DocumentParseError(IngestionError):
    """A parser library failed to read the document."""
