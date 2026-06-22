"""Trigger engine: decide when to fire a rescue from the transcript.

Modes:
- ``manual`` — the speaker pressed the button; rescue on the current window now.
- ``periodic`` — the ~30s auto-scan; fire only on new, substantial content.
- ``keyword`` — an urgent phrase ("good question", "let me think") appeared;
  fire even on a short window.
- ``silence`` — the speaker went quiet past ``silence_threshold_s``; fire on the
  last thing they said in case they're stuck.

Auto modes (everything but ``manual``) never re-fire on an unchanged window and
suppress ungrounded bridges, so the scan stays quiet unless it has something
genuinely grounded to offer. Every fire records the exchange as a turn.
"""

from __future__ import annotations

from typing import Literal

from cue.config import Settings, get_settings
from cue.rescue import service as rescue_service
from cue.rescue.models import RescueResponse
from cue.sessions import service as sessions_service
from cue.transcript import service as transcript_service

Mode = Literal["manual", "periodic", "keyword", "silence"]

# Last window we fired on, per session — dedups repeated auto scans.
_LAST_FIRED: dict[str, str] = {}


def should_fire(window_text: str, last_fired: str | None, min_chars: int) -> bool:
    """Periodic gate: enough new speech to be worth a scan."""
    text = window_text.strip()
    if len(text) < min_chars:
        return False
    return text != last_fired


def matched_keyword(window_text: str, keywords: list[str]) -> str | None:
    """The first urgent keyword present in the window (case-insensitive)."""
    low = window_text.lower()
    for keyword in keywords:
        if keyword.lower() in low:
            return keyword
    return None


def fire(session_id: str, mode: Mode) -> RescueResponse | None:
    """Run a trigger. Returns the rescue to surface, or None if nothing to fire.

    Records a turn whenever a rescue is surfaced.
    """
    settings = get_settings()
    window = transcript_service.get_window(session_id).strip()
    if not window:
        return None

    if mode != "manual":
        if window == _LAST_FIRED.get(session_id):
            return None  # never re-fire on an unchanged window
        if mode == "periodic" and len(window) < settings.trigger_min_chars:
            return None  # keyword/silence relax the length gate; periodic doesn't

    _LAST_FIRED[session_id] = window
    response = rescue_service.generate_rescue(window)  # no session_id: record below
    if mode != "manual" and not response.grounded:
        return None  # keep the auto-scan quiet unless it has grounded help

    sessions_service.record_turn(session_id, window, response)
    return response


def auto_reason(session_id: str, settings: Settings) -> Mode | None:
    """Why the auto-scan should fire now, or None. Keyword > silence > periodic."""
    window = transcript_service.get_window(session_id).strip()
    if not window:
        return None
    if matched_keyword(window, settings.trigger_keywords):
        return "keyword"
    if transcript_service.silence_seconds(session_id) >= settings.silence_threshold_s:
        return "silence"
    if should_fire(window, _LAST_FIRED.get(session_id), settings.trigger_min_chars):
        return "periodic"
    return None


def auto_fire(session_id: str) -> tuple[RescueResponse | None, Mode | None]:
    """Run one auto-scan: pick the reason (keyword/silence/periodic) and fire it."""
    mode = auto_reason(session_id, get_settings())
    if mode is None:
        return None, None
    return fire(session_id, mode), mode


def reset(session_id: str | None = None) -> None:
    """Clear dedup state (tests / when a session ends)."""
    if session_id is None:
        _LAST_FIRED.clear()
    else:
        _LAST_FIRED.pop(session_id, None)
