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

    # --- Sessions / output ---
    db_path: str = "cue.db"  # stdlib sqlite3 store for sessions + turns
    lyric_max_chars: int = 42  # max chars per rendered rescue line

    # --- Embeddings ---
    # auto = use Gemini when a key is present, else the offline fake embedder.
    embeddings_provider: Literal["auto", "gemini", "fake"] = "auto"
    embedding_dim: int = 256  # fake embedder dimension (Gemini sets its own)
    embedding_batch_size: int = 100

    # --- RAG / retrieval ---
    chroma_dir: str = ".chroma"
    chroma_collection: str = "cue_documents"
    chunk_size: int = 800
    chunk_overlap: int = 120
    retrieval_k: int = 5

    @property
    def active_embeddings_provider(self) -> Literal["gemini", "fake"]:
        """Resolve `auto` to a concrete provider based on key presence."""
        if self.embeddings_provider == "auto":
            return "gemini" if self.gemini_configured else "fake"
        return self.embeddings_provider

    # --- Rescue / generation ---
    generation_provider: Literal["auto", "gemini", "fake"] = "auto"
    rescue_temperature: float = 0.3
    rescue_max_passages: int = 5
    rescue_max_output_tokens: int = 512  # short spoken script; caps generation latency
    rescue_max_attempts: int = 3  # retry transient Gemini 5xx before bridging
    # Cheap floor that skips the LLM when retrieval clearly returns nothing.
    # NOT the main grounding guard: Gemini embeddings are anisotropic (even
    # nonsense scores ~0.6 on short text), so refusal detection on the model's
    # output is the real signal. The fake embedder is on a different scale, so
    # tests override this via CUE_RESCUE_MIN_SCORE.
    rescue_min_score: float = 0.4
    rescue_timeout_s: float = 4.0

    @property
    def active_generation_provider(self) -> Literal["gemini", "fake"]:
        """Resolve `auto` to a concrete generation provider based on key presence."""
        if self.generation_provider == "auto":
            return "gemini" if self.gemini_configured else "fake"
        return self.generation_provider

    @property
    def gemini_configured(self) -> bool:
        """True when a Gemini API key is present (gates live LLM calls)."""
        return bool(self.gemini_api_key)


@lru_cache
def get_settings() -> Settings:
    """Return the process-wide cached settings instance."""
    return Settings()
