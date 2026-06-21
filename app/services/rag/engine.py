"""
RAG (Retrieval-Augmented Generation) engine service.
Manages document chunking, embedding, vector storage,
and context-aware retrieval using ChromaDB + Gemini.
"""

import logging
import uuid
from typing import Optional

from app.core.config import get_settings
from app.models.schemas import SourceReference

logger = logging.getLogger(__name__)


class RAGEngine:
    """
    RAG engine that chunks documents, stores embeddings in ChromaDB,
    and retrieves relevant context for answering user questions.
    """

    def __init__(self):
        self._collection = None
        self._client = None
        self._initialized = False

    async def initialize(self):
        """Lazy-initialize ChromaDB client and collection."""
        if self._initialized:
            return

        try:
            import chromadb

            settings = get_settings()
            self._client = chromadb.PersistentClient(path=settings.chromadb_path)
            self._collection = self._client.get_or_create_collection(
                name="presentation_docs",
                metadata={"hnsw:space": "cosine"},
            )
            self._initialized = True
            logger.info(
                f"ChromaDB initialized at {settings.chromadb_path} "
                f"(collection: presentation_docs, "
                f"existing docs: {self._collection.count()})"
            )
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            raise

    def chunk_text(
        self,
        text: str,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
    ) -> list[str]:
        """
        Split document text into overlapping chunks for embedding.
        Uses LangChain's RecursiveCharacterTextSplitter for smart splitting.
        """
        try:
            from langchain_text_splitters import RecursiveCharacterTextSplitter

            splitter = RecursiveCharacterTextSplitter(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                length_function=len,
                separators=["\n\n", "\n", ". ", " ", ""],
            )
            chunks = splitter.split_text(text)
            logger.info(f"Split text into {len(chunks)} chunks (size={chunk_size}, overlap={chunk_overlap})")
            return chunks
        except ImportError:
            # Fallback: simple chunking if langchain not available
            logger.warning("langchain_text_splitters not available, using simple chunking")
            return self._simple_chunk(text, chunk_size, chunk_overlap)

    def _simple_chunk(self, text: str, chunk_size: int, overlap: int) -> list[str]:
        """Fallback chunking without langchain."""
        chunks = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunks.append(text[start:end])
            start = end - overlap
        return chunks

    async def add_document(
        self,
        doc_id: str,
        filename: str,
        text: str,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
    ) -> int:
        """
        Chunk a document and add all chunks to the vector store.
        Returns the number of chunks created.
        """
        await self.initialize()

        chunks = self.chunk_text(text, chunk_size, chunk_overlap)
        if not chunks:
            logger.warning(f"No chunks generated for document {doc_id}")
            return 0

        # Prepare data for ChromaDB
        ids = [f"{doc_id}_chunk_{i}" for i in range(len(chunks))]
        metadatas = [
            {
                "doc_id": doc_id,
                "filename": filename,
                "chunk_index": i,
                "total_chunks": len(chunks),
            }
            for i in range(len(chunks))
        ]

        # Add to ChromaDB (it generates embeddings automatically
        # using its default embedding function)
        self._collection.add(
            documents=chunks,
            ids=ids,
            metadatas=metadatas,
        )

        logger.info(f"Added {len(chunks)} chunks for document {doc_id} ({filename})")
        return len(chunks)

    async def query(
        self,
        query_text: str,
        n_results: int = 5,
        doc_ids: Optional[list[str]] = None,
    ) -> list[dict]:
        """
        Query the vector store for relevant document chunks.
        Optionally filter by specific document IDs.
        """
        await self.initialize()

        where_filter = None
        if doc_ids:
            where_filter = {"doc_id": {"$in": doc_ids}}

        results = self._collection.query(
            query_texts=[query_text],
            n_results=n_results,
            where=where_filter,
            include=["documents", "metadatas", "distances"],
        )

        # Format results
        formatted = []
        if results and results["documents"]:
            for i, doc in enumerate(results["documents"][0]):
                metadata = results["metadatas"][0][i] if results["metadatas"] else {}
                distance = results["distances"][0][i] if results["distances"] else 0.0
                formatted.append({
                    "text": doc,
                    "metadata": metadata,
                    "relevance": 1 - distance,  # convert distance to similarity
                })

        logger.info(f"Query returned {len(formatted)} results for: '{query_text[:50]}...'")
        return formatted

    async def get_context_for_query(
        self,
        query: str,
        doc_ids: Optional[list[str]] = None,
        max_context_length: int = 4000,
    ) -> tuple[str, list[SourceReference]]:
        """
        Build a context string and source references for the LLM.
        Returns (context_string, source_references).
        """
        results = await self.query(query, n_results=5, doc_ids=doc_ids)

        context_parts = []
        sources = []
        total_length = 0

        for result in results:
            text = result["text"]
            if total_length + len(text) > max_context_length:
                break

            context_parts.append(text)
            total_length += len(text)

            sources.append(SourceReference(
                document=result["metadata"].get("filename", "Unknown"),
                chunk_id=result["metadata"].get("doc_id", ""),
                relevance=result["relevance"],
                text_preview=text[:150] + "..." if len(text) > 150 else text,
            ))

        context = "\n\n---\n\n".join(context_parts)
        return context, sources

    async def delete_document_chunks(self, doc_id: str):
        """Remove all chunks for a specific document."""
        await self.initialize()

        # Get all chunk IDs for this document
        results = self._collection.get(
            where={"doc_id": doc_id},
            include=[],
        )
        if results and results["ids"]:
            self._collection.delete(ids=results["ids"])
            logger.info(f"Deleted {len(results['ids'])} chunks for document {doc_id}")

    async def get_stats(self) -> dict:
        """Get vector store statistics."""
        await self.initialize()
        return {
            "total_chunks": self._collection.count(),
            "collection_name": "presentation_docs",
        }


# Singleton instance
rag_engine = RAGEngine()
