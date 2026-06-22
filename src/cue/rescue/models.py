"""Request/response models for the rescue endpoint."""

from __future__ import annotations

from pydantic import BaseModel, Field, field_validator


class RescueRequest(BaseModel):
    """A typed (or repeated) question to rescue."""

    question: str = Field(min_length=1, description="The question to answer from the docs.")
    k: int | None = Field(default=None, ge=1, le=20, description="Override retrieval top-k.")

    @field_validator("question")
    @classmethod
    def _not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("question must not be blank")
        return value.strip()


class Citation(BaseModel):
    """A source passage backing the rescue script."""

    doc_id: str
    filename: str
    chunk_index: int
    score: float


class RescueResponse(BaseModel):
    """A grounded rescue script, ready to read line by line."""

    script: str
    lines: list[str]
    grounded: bool
    citations: list[Citation]
