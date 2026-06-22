"""Tests for chunking, the fake embedder, and the index/store round-trip."""

from __future__ import annotations

import math

from cue.config import Settings
from cue.ingestion.models import DocType, ParsedDocument
from cue.rag import index
from cue.rag.chunking import chunk_text
from cue.rag.embeddings import FakeEmbedder, GeminiEmbedder, get_embedder

LOREM = (
    "Cue helps a speaker recover in real time. "
    "When a hard question lands the agent returns a grounded rescue script. "
    "It reads line by line like song lyrics so it is easy to speak aloud. "
) * 6


def test_chunk_text_covers_and_overlaps() -> None:
    chunks = chunk_text(LOREM, size=120, overlap=30)
    assert len(chunks) > 1
    assert [c.index for c in chunks] == list(range(len(chunks)))
    assert all(c.text for c in chunks)
    assert all(len(c.text) <= 120 for c in chunks)
    # Adjacent chunks share overlapping content.
    first_tail = chunks[0].text[-15:]
    assert first_tail.split()[-1] in chunks[1].text


def test_chunk_text_short_returns_single_chunk() -> None:
    chunks = chunk_text("just a short note", size=800, overlap=120)
    assert len(chunks) == 1
    assert chunks[0].text == "just a short note"


def test_fake_embedder_is_deterministic_and_normalized() -> None:
    emb = FakeEmbedder(dim=64)
    v1 = emb.embed_query("grounded rescue script")
    v2 = emb.embed_query("grounded rescue script")
    assert v1 == v2
    assert len(v1) == 64
    assert math.isclose(math.sqrt(sum(x * x for x in v1)), 1.0, rel_tol=1e-6)
    assert emb.embed_query("totally different words") != v1


def test_get_embedder_factory_respects_provider() -> None:
    # Init kwargs outrank env vars; field name for `embeddings_provider`, alias
    # `GEMINI_API_KEY` for the key.
    fake_settings = Settings(_env_file=None, embeddings_provider="fake")
    assert isinstance(get_embedder(fake_settings), FakeEmbedder)

    # auto + key present -> resolves to the live Gemini embedder (no network on init).
    gemini_settings = Settings(_env_file=None, embeddings_provider="auto", GEMINI_API_KEY="x")
    assert gemini_settings.active_embeddings_provider == "gemini"
    assert isinstance(get_embedder(gemini_settings), GeminiEmbedder)


def test_index_and_query_roundtrip() -> None:
    doc = ParsedDocument(
        id="doc1",
        filename="talk.txt",
        doc_type=DocType.txt,
        char_count=len(LOREM),
        text=LOREM,
    )
    meta = index.index_document(doc)
    assert meta.id == "doc1"
    assert meta.n_chunks >= 1

    listed = index.list_documents()
    assert [d.id for d in listed] == ["doc1"]
    assert listed[0].n_chunks == meta.n_chunks

    passages = index.query("grounded rescue script", k=3)
    assert passages
    assert all(p.doc_id == "doc1" for p in passages)
    assert passages[0].citation_id.startswith("doc1:")
    # Scores are sorted best-first.
    assert passages == sorted(passages, key=lambda p: p.score, reverse=True)
