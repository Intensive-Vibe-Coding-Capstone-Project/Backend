"""Health / readiness endpoints."""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from cue import __version__
from cue.config import get_settings

router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    status: str
    version: str
    env: str
    gemini_configured: bool


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """Liveness probe + a quick view of what's wired up.

    `gemini_configured` is False until a `GEMINI_API_KEY` is set — useful while
    the LLM path is still being built (D3+).
    """
    settings = get_settings()
    return HealthResponse(
        status="ok",
        version=__version__,
        env=settings.env,
        gemini_configured=settings.gemini_configured,
    )
