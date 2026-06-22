"""Session endpoints: start a session and read its turn history."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from cue.sessions import service
from cue.sessions.models import SessionCreate, SessionDetail, SessionMeta

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("", status_code=201, response_model=SessionMeta)
def create_session(body: SessionCreate | None = None) -> SessionMeta:
    """Start a new session."""
    title = body.title if body else None
    session = service.create_session(title)
    return SessionMeta(**session.model_dump(), turn_count=0)


@router.get("", response_model=list[SessionMeta])
def list_sessions() -> list[SessionMeta]:
    """List sessions (newest first), each with its turn count."""
    return service.list_sessions()


@router.get("/{session_id}", response_model=SessionDetail)
def get_session(session_id: str) -> SessionDetail:
    """Return a session with its full, ordered turn history."""
    detail = service.get_session_detail(session_id)
    if detail is None:
        raise HTTPException(status_code=404, detail=f"Session not found: {session_id}")
    return detail
