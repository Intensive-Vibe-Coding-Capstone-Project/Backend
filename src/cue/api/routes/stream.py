"""Streaming transcript ingest over WebSocket (D8).

Client sends JSON transcript segments; the server appends them to the session's
rolling buffer and acks with the current window/silence state. The D9 trigger
engine will read that buffer to decide when to fire a rescue.
"""

from __future__ import annotations

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import ValidationError

from cue.config import get_settings
from cue.sessions.errors import SessionNotFoundError
from cue.transcript import service
from cue.transcript.models import TranscriptMessage

router = APIRouter()

# WebSocket close code for "session not found" (app-specific, 4000-4999 range).
SESSION_NOT_FOUND = 4404


@router.websocket("/stream/{session_id}")
async def stream(websocket: WebSocket, session_id: str) -> None:
    await websocket.accept()
    try:
        service.ensure_session(session_id)
    except SessionNotFoundError:
        await websocket.close(code=SESSION_NOT_FOUND)
        return

    settings = get_settings()
    try:
        while True:
            data = await websocket.receive_json()
            try:
                message = TranscriptMessage(**data)
            except ValidationError:
                await websocket.send_json({"type": "error", "detail": "invalid transcript message"})
                continue

            segment = service.append_segment(session_id, message.text, message.ts)
            window = service.get_window(session_id, settings.transcript_window_s)
            await websocket.send_json(
                {
                    "type": "ack",
                    "segments": service.segment_count(session_id),
                    "window_chars": len(window),
                    "silence_s": round(service.silence_seconds(session_id), 3),
                    "last_ts": segment.ts,
                }
            )
    except WebSocketDisconnect:
        return
