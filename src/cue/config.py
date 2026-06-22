"""Application configuration, loaded from environment / `.env`.

Single source of truth for runtime config. Per conventions: model ids, k,
chunk sizes, thresholds are config — never magic numbers in code. Import the
cached `get_settings()` accessor rather than instantiating `Settings` directly.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Typed settings read from environment variables / `.env`.

    Env var names use the `CUE_` prefix (e.g. `CUE_RESCUE_MODEL`), except the
    Gemini API key which uses the conventional `GEMINI_API_KEY`.
    """

    model_config = SettingsConfigDict(
        env_prefix="CUE_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- App ---
    env: Literal["dev", "prod"] = "dev"
    log_level: str = "INFO"

    # --- Gemini (google-genai) ---
    gemini_api_key: str = Field(default="", alias="GEMINI_API_KEY")
    rescue_model: str = "gemini-2.5-flash"
    reasoning_model: str = "gemini-2.5-pro"
    embedding_model: str = "gemini-embedding-001"

    # --- Ingestion ---
    max_upload_mb: int = 20
    preview_chars: int = 200

    # --- RAG / retrieval ---
    chroma_dir: str = ".chroma"
    chunk_size: int = 800
    chunk_overlap: int = 120
    retrieval_k: int = 5

    # --- Latency / generation ---
    rescue_timeout_s: float = 4.0

    @property
    def gemini_configured(self) -> bool:
        """True when a Gemini API key is present (gates live LLM calls)."""
        return bool(self.gemini_api_key)


@lru_cache
def get_settings() -> Settings:
    """Return the process-wide cached settings instance."""
    return Settings()
