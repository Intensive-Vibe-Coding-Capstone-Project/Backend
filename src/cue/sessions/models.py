"""Session + turn models and their API schemas."""

from __future__ import annotations

from datetime import UTC, datetime

from pydantic import BaseModel

from cue.rescue.models import Citation


def now_iso() -> str:
    """Current UTC time as an ISO-8601 string (used for created_at)."""
    return datetime.now(UTC).isoformat()


class Turn(BaseModel):
    """One recorded rescue exchange within a session."""

    id: str
    session_id: str
    question: str
    script: str
    lines: list[str]
    grounded: bool
    citations: list[Citation]
    created_at: str


class Session(BaseModel):
    """A conversation/talk grouping a sequence of turns."""

    id: str
    title: str | None = None
    created_at: str


class SessionCreate(BaseModel):
    """Request body for starting a session."""

    title: str | None = None


class SessionMeta(Session):
    """List-safe session view with a turn count (no turn bodies)."""

    turn_count: int = 0


class SessionDetail(Session):
    """A session with its full, ordered turn history."""

    turns: list[Turn]
