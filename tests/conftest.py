"""Shared pytest fixtures."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from cue.api.app import create_app
from cue.config import get_settings
from cue.rag import store


@pytest.fixture(autouse=True)
def _isolate_store(tmp_path, monkeypatch) -> None:
    """Give each test a fresh Chroma dir and the offline fake embedder.

    Keeps the suite hermetic and keyless: env vars override any local `.env`,
    so tests never hit the network even when a real GEMINI_API_KEY is present.
    """
    monkeypatch.setenv("CUE_CHROMA_DIR", str(tmp_path / "chroma"))
    monkeypatch.setenv("CUE_EMBEDDINGS_PROVIDER", "fake")
    monkeypatch.setenv("CUE_GENERATION_PROVIDER", "fake")
    get_settings.cache_clear()
    store.reset_cache()
    yield
    get_settings.cache_clear()
    store.reset_cache()


@pytest.fixture
def client() -> TestClient:
    """A TestClient bound to a fresh app instance."""
    return TestClient(create_app())
