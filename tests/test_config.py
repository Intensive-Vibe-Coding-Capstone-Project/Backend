"""Settings tests — defaults and env overrides."""

from __future__ import annotations

from cue.config import Settings


def test_defaults() -> None:
    settings = Settings(_env_file=None)
    assert settings.env == "dev"
    assert settings.rescue_model == "gemini-2.5-flash"
    assert settings.reasoning_model == "gemini-2.5-pro"
    assert settings.embedding_model == "gemini-embedding-001"
    assert settings.retrieval_k == 5
    assert settings.gemini_configured is False


def test_env_override(monkeypatch) -> None:
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setenv("CUE_RETRIEVAL_K", "8")
    settings = Settings(_env_file=None)
    assert settings.gemini_configured is True
    assert settings.retrieval_k == 8
