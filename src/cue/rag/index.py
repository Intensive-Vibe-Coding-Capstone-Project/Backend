"""Indexing + retrieval orchestration: the seam between ingestion and the store.

`index_document` is called by `POST /documents` after parsing; `query` is the
read path D4's `/rescue` will use to retrieve grounded passages.
"""

from __future__ import annotations

from cue.config import get_settings
from cue.ingestion.models import DocumentMeta, ParsedDocument
from cue.rag import chunking
from cue.rag.embeddings import get_embedder
from cue.rag.models import Passage
from cue.rag.store import get_store


def index_document(doc: ParsedDocument) -> DocumentMeta:
    """Chunk, embed, and store a parsed document. Returns its public metadata."""
    settings = get_settings()
    chunks = chunking.chunk_text(doc.text, settings.chunk_size, settings.chunk_overlap)
    embeddings = get_embedder(settings).embed_documents([chunk.text for chunk in chunks])

    get_store(settings).add_document(
        doc_id=doc.id,
        filename=doc.filename,
        doc_type=doc.doc_type,
        char_count=doc.char_count,
        chunks=chunks,
        embeddings=embeddings,
    )

    return DocumentMeta(
        id=doc.id,
        filename=doc.filename,
        doc_type=doc.doc_type,
        char_count=doc.char_count,
        n_chunks=len(chunks),
        preview=doc.text[: settings.preview_chars],
    )


def list_documents() -> list[DocumentMeta]:
    return get_store().list_documents()


def get_document(doc_id: str) -> DocumentMeta | None:
    return get_store().get_document(doc_id)


def query(question: str, k: int | None = None) -> list[Passage]:
    """Embed a question and return the top-`k` grounded passages with citations."""
    settings = get_settings()
    k = k if k is not None else settings.retrieval_k
    embedding = get_embedder(settings).embed_query(question)
    return get_store(settings).query(embedding, k)
