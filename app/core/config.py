"""
Core configuration module.
Loads environment variables and provides typed settings for the application.
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # ── Application ──────────────────────────────────────────
    app_name: str = "AI Presentation Assistant"
    app_version: str = "0.1.0"
    app_env: str = Field(default="development", alias="APP_ENV")
    app_port: int = Field(default=8000, alias="APP_PORT")
    app_host: str = Field(default="0.0.0.0", alias="APP_HOST")
    debug: bool = Field(default=True, alias="DEBUG")

    # ── Google AI / Gemini ───────────────────────────────────
    google_api_key: str = Field(default="", alias="GOOGLE_API_KEY")
    gemini_model: str = Field(default="gemini-2.0-flash", alias="GEMINI_MODEL")

    # ── Firebase ─────────────────────────────────────────────
    firebase_project_id: str = Field(default="", alias="FIREBASE_PROJECT_ID")
    firebase_private_key: Optional[str] = Field(default=None, alias="FIREBASE_PRIVATE_KEY")
    firebase_client_email: Optional[str] = Field(default=None, alias="FIREBASE_CLIENT_EMAIL")

    # ── Google Cloud ─────────────────────────────────────────
    gcp_project_id: Optional[str] = Field(default=None, alias="GCP_PROJECT_ID")
    gcs_bucket_name: Optional[str] = Field(default=None, alias="GCS_BUCKET_NAME")

    # ── ChromaDB ─────────────────────────────────────────────
    chromadb_path: str = Field(default="./chroma_db", alias="CHROMADB_PATH")

    # ── Voice Settings ───────────────────────────────────────
    default_language: str = Field(default="en", alias="DEFAULT_LANGUAGE")
    signal_detection_sensitivity: float = Field(
        default=0.7, alias="SIGNAL_DETECTION_SENSITIVITY"
    )

    # ── CORS ─────────────────────────────────────────────────
    cors_origins: str = Field(
        default="http://localhost:3000,http://localhost:8080",
        alias="CORS_ORIGINS",
    )

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse comma-separated CORS origins into a list."""
        return [origin.strip() for origin in self.cors_origins.split(",")]

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


@lru_cache()
def get_settings() -> Settings:
    """Cached settings singleton — loaded once per process."""
    return Settings()
