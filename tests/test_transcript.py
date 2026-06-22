"""Tests for the transcript buffer, service, and WS /stream endpoint."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from cue.sessions import service as sessions_service
from cue.sessions.errors import SessionNotFoundError
from cue.transcript import service
from cue.transcript.buffer import TranscriptBuffer

# --- buffer (deterministic clock) -------------------------------------------


def test_buffer_window_and_silence() -> None:
    clock = {"t": 1000.0}
    buf = TranscriptBuffer(clock=lambda: clock["t"])

    buf.append("old segment")  # ts=1000
    clock["t"] = 1025.0
    buf.append("recent segment")  # ts=1025
    clock["t"] = 1030.0

    assert buf.segment_count() == 2
    # Window of last 10s at t=1030 keeps only the 1025 segment.
    assert buf.window_text(10.0) == "recent segment"
    # Window of 60s keeps both.
    assert "old segment" in buf.window_text(60.0)
    assert buf.silence_seconds() == pytest.approx(5.0)


def test_buffer_silence_empty_is_zero() -> None:
    assert TranscriptBuffer().silence_seconds() == 0.0


# --- service ----------------------------------------------------------------


def test_service_append_and_window() -> None:
    # Segments use the real clock; a wide window keeps both. (Deterministic
    # windowing is covered at the buffer level above.)
    session = sessions_service.create_session()
    service.ensure_session(session.id)
    service.append_segment(session.id, "hello")
    service.append_segment(session.id, "world")
    assert service.segment_count(session.id) == 2
    assert service.get_window(session.id, seconds=1000.0) == "hello world"


def test_service_unknown_session_raises() -> None:
    with pytest.raises(SessionNotFoundError):
        service.ensure_session("ghost")


# --- WS endpoint ------------------------------------------------------------


def test_ws_stream_appends_and_acks(client: TestClient) -> None:
    session = client.post("/sessions", json={}).json()
    with client.websocket_connect(f"/stream/{session['id']}") as ws:
        ws.send_json({"text": "they just asked about pricing"})
        ack = ws.receive_json()
        assert ack["type"] == "ack"
        assert ack["segments"] == 1
        assert ack["window_chars"] > 0

        ws.send_json({"text": "and about the roadmap"})
        ack2 = ws.receive_json()
        assert ack2["segments"] == 2


def test_ws_stream_rejects_unknown_session(client: TestClient) -> None:
    with client.websocket_connect("/stream/ghost") as ws:
        with pytest.raises(WebSocketDisconnect) as exc:
            ws.receive_json()
    assert exc.value.code == 4404
