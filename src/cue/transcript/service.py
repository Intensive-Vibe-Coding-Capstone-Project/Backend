"""Per-session transcript buffers.

In-memory: a live transcript is ephemeral (persisted *turns* live in the session
store). Validation happens once on connect via `ensure_session`; the append hot
path stays cheap.
"""

from __future__ import annotations

from cue.config import get_settings
from cue.sessions import service as sessions_service
from cue.sessions.errors import SessionNotFoundError
from cue.transcript.buffer import TranscriptBuffer
from cue.transcript.models import TranscriptSegment

_BUFFERS: dict[str, TranscriptBuffer] = {}


def ensure_session(session_id: str) -> None:
    """Raise `SessionNotFoundError` if the session does not exist."""
    if not sessions_service.session_exists(session_id):
        raise SessionNotFoundError(session_id)


def _buffer(session_id: str) -> TranscriptBuffer:
    return _BUFFERS.setdefault(session_id, TranscriptBuffer())


def append_segment(session_id: str, text: str, ts: float | None = None) -> TranscriptSegment:
    return _buffer(session_id).append(text, ts)


def get_window(session_id: str, seconds: float | None = None) -> str:
    seconds = seconds if seconds is not None else get_settings().transcript_window_s
    return _buffer(session_id).window_text(seconds)


def silence_seconds(session_id: str) -> float:
    return _buffer(session_id).silence_seconds()


def segment_count(session_id: str) -> int:
    return _buffer(session_id).segment_count()


def reset(session_id: str | None = None) -> None:
    """Drop buffers (used by tests / when a session ends)."""
    if session_id is None:
        _BUFFERS.clear()
    else:
        _BUFFERS.pop(session_id, None)
