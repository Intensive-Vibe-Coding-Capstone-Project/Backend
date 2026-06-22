"""Transcript data models."""

from __future__ import annotations

from pydantic import BaseModel, Field


class TranscriptSegment(BaseModel):
    """A chunk of recognized speech with the epoch time it arrived."""

    text: str
    ts: float  # epoch seconds


class TranscriptMessage(BaseModel):
    """Inbound WS payload: a transcript segment (ts defaults to server time)."""

    text: str = Field(min_length=1)
    ts: float | None = None
