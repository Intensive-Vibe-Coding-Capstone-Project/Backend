"""Text embedding providers behind a single `Embedder` interface.

`GeminiEmbedder` calls the live API; `FakeEmbedder` is deterministic and offline
so tests and keyless CI stay green. `get_embedder()` picks one from config.
"""

from __future__ import annotations

import hashlib
import math
import re
from typing import Protocol, runtime_checkable

from cue.config import Settings, get_settings

_TOKEN = re.compile(r"[a-z0-9]+")


@runtime_checkable
class Embedder(Protocol):
    """Embeds text into fixed-length vectors."""

    @property
    def dim(self) -> int: ...

    def embed_documents(self, texts: list[str]) -> list[list[float]]: ...

    def embed_query(self, text: str) -> list[float]: ...


class FakeEmbedder:
    """Deterministic offline embedder: hashed bag-of-words, L2-normalized.

    Not semantically meaningful, but stable and overlap-sensitive — enough to
    exercise chunking, storage, and ranking without network or keys.
    """

    def __init__(self, dim: int = 256) -> None:
        self._dim = dim

    @property
    def dim(self) -> int:
        return self._dim

    def _embed(self, text: str) -> list[float]:
        vec = [0.0] * self._dim
        for token in _TOKEN.findall(text.lower()):
            bucket = int(hashlib.md5(token.encode()).hexdigest(), 16) % self._dim
            vec[bucket] += 1.0
        norm = math.sqrt(sum(value * value for value in vec)) or 1.0
        return [value / norm for value in vec]

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self._embed(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        return self._embed(text)


class GeminiEmbedder:
    """Live embeddings via the google-genai SDK (task-typed for retrieval)."""

    def __init__(self, api_key: str, model: str, batch_size: int = 100) -> None:
        from google import genai

        self._client = genai.Client(api_key=api_key)
        self._model = model
        self._batch_size = batch_size
        self._dim: int | None = None

    @property
    def dim(self) -> int:
        if self._dim is None:
            self._dim = len(self.embed_query("dimension probe"))
        return self._dim

    def _embed(self, texts: list[str], task_type: str) -> list[list[float]]:
        from google.genai import types

        config = types.EmbedContentConfig(task_type=task_type)
        vectors: list[list[float]] = []
        for i in range(0, len(texts), self._batch_size):
            batch = texts[i : i + self._batch_size]
            result = self._client.models.embed_content(
                model=self._model, contents=batch, config=config
            )
            vectors.extend(list(e.values) for e in result.embeddings)
        return vectors

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        return self._embed(texts, "RETRIEVAL_DOCUMENT")

    def embed_query(self, text: str) -> list[float]:
        return self._embed([text], "RETRIEVAL_QUERY")[0]


def get_embedder(settings: Settings | None = None) -> Embedder:
    """Build the configured embedder (`gemini` or `fake`, resolving `auto`)."""
    settings = settings or get_settings()
    if settings.active_embeddings_provider == "gemini":
        return GeminiEmbedder(
            api_key=settings.gemini_api_key,
            model=settings.embedding_model,
            batch_size=settings.embedding_batch_size,
        )
    return FakeEmbedder(dim=settings.embedding_dim)
