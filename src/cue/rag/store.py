"""Chroma-backed vector store: persist chunk embeddings and search them.

One collection holds all document chunks (cosine space). Document-level
metadata is reconstructed by aggregating chunk metadata, so no second store is
needed. Embeddings are always supplied by the caller — Chroma's default
embedding function is disabled to avoid any model download.
"""

from __future__ import annotations

from functools import lru_cache

import chromadb

from cue.config import Settings, get_settings
from cue.ingestion.models import DocType, DocumentMeta
from cue.rag.chunking import Chunk
from cue.rag.models import Passage


class VectorStore:
    """Thin wrapper over a single Chroma collection."""

    def __init__(self, path: str, collection_name: str, preview_chars: int = 200) -> None:
        self._preview_chars = preview_chars
        client = chromadb.PersistentClient(
            path=path,
            settings=chromadb.Settings(anonymized_telemetry=False),
        )
        self._collection = client.get_or_create_collection(
            name=collection_name,
            embedding_function=None,
            metadata={"hnsw:space": "cosine"},
        )

    def add_document(
        self,
        *,
        doc_id: str,
        filename: str,
        doc_type: DocType,
        char_count: int,
        chunks: list[Chunk],
        embeddings: list[list[float]],
    ) -> None:
        """Store all chunks of one document with shared doc-level metadata."""
        self._collection.add(
            ids=[f"{doc_id}:{chunk.index}" for chunk in chunks],
            embeddings=embeddings,
            documents=[chunk.text for chunk in chunks],
            metadatas=[
                {
                    "doc_id": doc_id,
                    "filename": filename,
                    "doc_type": str(doc_type),
                    "char_count": char_count,
                    "chunk_index": chunk.index,
                }
                for chunk in chunks
            ],
        )

    def query(self, embedding: list[float], k: int) -> list[Passage]:
        """Return the top-`k` most similar chunks as cited passages."""
        result = self._collection.query(
            query_embeddings=[embedding],
            n_results=k,
            include=["documents", "metadatas", "distances"],
        )
        documents = result["documents"][0]
        metadatas = result["metadatas"][0]
        distances = result["distances"][0]
        passages: list[Passage] = []
        for text, meta, distance in zip(documents, metadatas, distances, strict=True):
            passages.append(
                Passage(
                    doc_id=str(meta["doc_id"]),
                    filename=str(meta["filename"]),
                    chunk_index=int(meta["chunk_index"]),
                    text=text,
                    score=1.0 - float(distance),  # cosine distance -> similarity
                )
            )
        return passages

    def list_documents(self) -> list[DocumentMeta]:
        """Aggregate stored chunks back into one metadata record per document."""
        result = self._collection.get(include=["documents", "metadatas"])
        by_doc: dict[str, DocumentMeta] = {}
        previews: dict[str, str] = {}
        for text, meta in zip(result["documents"], result["metadatas"], strict=True):
            doc_id = str(meta["doc_id"])
            if doc_id not in by_doc:
                by_doc[doc_id] = DocumentMeta(
                    id=doc_id,
                    filename=str(meta["filename"]),
                    doc_type=DocType(str(meta["doc_type"])),
                    char_count=int(meta["char_count"]),
                    n_chunks=0,
                    preview="",
                )
            by_doc[doc_id].n_chunks += 1
            if int(meta["chunk_index"]) == 0:
                previews[doc_id] = text[: self._preview_chars]

        for doc_id, doc in by_doc.items():
            doc.preview = previews.get(doc_id, "")
        return list(by_doc.values())

    def get_document(self, doc_id: str) -> DocumentMeta | None:
        for doc in self.list_documents():
            if doc.id == doc_id:
                return doc
        return None

    def delete_document(self, doc_id: str) -> None:
        self._collection.delete(where={"doc_id": doc_id})

    def count(self) -> int:
        return self._collection.count()


@lru_cache
def _build_store(path: str, collection_name: str, preview_chars: int) -> VectorStore:
    return VectorStore(path, collection_name, preview_chars)


def get_store(settings: Settings | None = None) -> VectorStore:
    """Return the cached vector store for the configured Chroma dir/collection."""
    settings = settings or get_settings()
    return _build_store(settings.chroma_dir, settings.chroma_collection, settings.preview_chars)


def reset_cache() -> None:
    """Drop cached store clients (used by tests between temp dirs)."""
    _build_store.cache_clear()
