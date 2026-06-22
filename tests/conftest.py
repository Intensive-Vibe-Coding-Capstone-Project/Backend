"""Shared pytest fixtures."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from cue.api.app import create_app
from cue.config import get_settings
from cue.rag import store
from cue.sessions import store as session_store
from cue.transcript import service as transcript_service


@pytest.fixture(autouse=True)
def _isolate_store(tmp_path, monkeypatch) -> None:
    """Give each test a fresh Chroma dir and the offline fake embedder.

    Keeps the suite hermetic and keyless: env vars override any local `.env`,
    so tests never hit the network even when a real GEMINI_API_KEY is present.
    """
    monkeypatch.setenv("CUE_CHROMA_DIR", str(tmp_path / "chroma"))
    monkeypatch.setenv("CUE_DB_PATH", str(tmp_path / "cue.db"))
    monkeypatch.setenv("CUE_EMBEDDINGS_PROVIDER", "fake")
    monkeypatch.setenv("CUE_GENERATION_PROVIDER", "fake")
    # The fake embedder scores on a different scale than Gemini; the production
    # default (0.6) is Gemini-tuned, so tests use a fake-appropriate threshold.
    monkeypatch.setenv("CUE_RESCUE_MIN_SCORE", "0.3")
    get_settings.cache_clear()
    store.reset_cache()
    session_store.reset_cache()
    transcript_service.reset()
    yield
    get_settings.cache_clear()
    store.reset_cache()
    session_store.reset_cache()
    transcript_service.reset()


@pytest.fixture
def client() -> TestClient:
    """A TestClient bound to a fresh app instance."""
    return TestClient(create_app())
