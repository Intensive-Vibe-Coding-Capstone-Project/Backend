"""Trigger engine: decide when to fire a rescue from the transcript.

Two modes:
- ``manual`` — the speaker pressed the button; rescue on the current window now.
- ``periodic`` — the ~30s auto-scan; fire only on new, substantial content and
  suppress ungrounded bridges so the auto-scan stays quiet unless it has
  something genuinely grounded to offer.

Every fire records the exchange as a turn in the session history.
"""

from __future__ import annotations

from typing import Literal

from cue.config import get_settings
from cue.rescue import service as rescue_service
from cue.rescue.models import RescueResponse
from cue.sessions import service as sessions_service
from cue.transcript import service as transcript_service

Mode = Literal["manual", "periodic"]

# Last window we fired on, per session — dedups repeated periodic scans.
_LAST_FIRED: dict[str, str] = {}


def should_fire(window_text: str, last_fired: str | None, min_chars: int) -> bool:
    """Periodic gate: enough new speech to be worth a scan."""
    text = window_text.strip()
    if len(text) < min_chars:
        return False
    return text != last_fired


def fire(session_id: str, mode: Mode) -> RescueResponse | None:
    """Run a trigger. Returns the rescue to surface, or None if nothing to fire.

    Records a turn whenever a rescue is surfaced.
    """
    settings = get_settings()
    window = transcript_service.get_window(session_id).strip()
    if not window:
        return None

    if mode == "periodic" and not should_fire(
        window, _LAST_FIRED.get(session_id), settings.trigger_min_chars
    ):
        return None

    _LAST_FIRED[session_id] = window
    response = rescue_service.generate_rescue(window)  # no session_id: record below
    if mode == "periodic" and not response.grounded:
        return None  # keep the auto-scan quiet unless it has grounded help

    sessions_service.record_turn(session_id, window, response)
    return response


def reset(session_id: str | None = None) -> None:
    """Clear dedup state (tests / when a session ends)."""
    if session_id is None:
        _LAST_FIRED.clear()
    else:
        _LAST_FIRED.pop(session_id, None)
