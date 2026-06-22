"""Session orchestration over the store."""

from __future__ import annotations

from cue.rescue.models import RescueResponse
from cue.sessions.models import Session, SessionDetail, SessionMeta, Turn
from cue.sessions.store import get_store


def create_session(title: str | None = None) -> Session:
    return get_store().create_session(title)


def list_sessions() -> list[SessionMeta]:
    return get_store().list_sessions()


def session_exists(session_id: str) -> bool:
    return get_store().session_exists(session_id)


def get_session_detail(session_id: str) -> SessionDetail | None:
    store = get_store()
    session = store.get_session(session_id)
    if session is None:
        return None
    return SessionDetail(**session.model_dump(), turns=store.get_turns(session_id))


def record_turn(session_id: str, question: str, response: RescueResponse) -> Turn:
    """Append a rescue exchange to a session's history."""
    return get_store().add_turn(
        session_id=session_id,
        question=question,
        script=response.script,
        lines=response.lines,
        grounded=response.grounded,
        citations=response.citations,
    )
