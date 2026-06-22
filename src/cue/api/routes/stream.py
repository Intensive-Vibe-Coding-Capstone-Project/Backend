"""Streaming transcript ingest + triggers over WebSocket (D8 + D9).

Client sends JSON messages:
- ``{"type": "transcript", "text": ...}`` — append to the session buffer (acked).
- ``{"type": "trigger"}`` — manual rescue on the current transcript window.

The server also runs a periodic auto-scan (every ``scan_interval_s``) that fires
on new grounded content, an urgent keyword, or a silence gap. Rescues are pushed
as ``{"type": "rescue", "mode": "manual"|"periodic"|"keyword"|"silence", ...}``;
slip corrections as ``{"type": "correction", ...}``.
"""

from __future__ import annotations

import asyncio
import contextlib

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import ValidationError

from cue.config import get_settings
from cue.rescue.models import RescueResponse
from cue.sessions.errors import SessionNotFoundError
from cue.transcript import service
from cue.transcript.models import TranscriptMessage
from cue.triggers import engine as triggers
from cue.triggers import slip
from cue.triggers.slip import SlipCorrection

router = APIRouter()

# WebSocket close code for "session not found" (app-specific, 4000-4999 range).
SESSION_NOT_FOUND = 4404


def _rescue_payload(response: RescueResponse, mode: str) -> dict:
    return {
        "type": "rescue",
        "mode": mode,
        "script": response.script,
        "lines": response.lines,
        "grounded": response.grounded,
        "citations": [c.model_dump() for c in response.citations],
    }


def _correction_payload(correction: SlipCorrection) -> dict:
    return {
        "type": "correction",
        "kind": correction.kind,
        "wrong_terms": correction.wrong_terms,
        "lines": correction.lines,
        "message": correction.message,
    }


@router.websocket("/stream/{session_id}")
async def stream(websocket: WebSocket, session_id: str) -> None:
    await websocket.accept()
    try:
        service.ensure_session(session_id)
    except SessionNotFoundError:
        await websocket.close(code=SESSION_NOT_FOUND)
        return

    settings = get_settings()
    send_lock = asyncio.Lock()

    async def send(payload: dict) -> None:
        async with send_lock:
            await websocket.send_json(payload)

    async def auto_scan() -> None:
        while True:
            await asyncio.sleep(settings.scan_interval_s)
            response, mode = await asyncio.to_thread(triggers.auto_fire, session_id)
            if response is not None and mode is not None:
                await send(_rescue_payload(response, mode))
            correction = await asyncio.to_thread(slip.check, session_id)
            if correction is not None:
                await send(_correction_payload(correction))

    scan_task = asyncio.create_task(auto_scan())
    try:
        while True:
            data = await websocket.receive_json()
            if data.get("type") == "trigger":
                response = await asyncio.to_thread(triggers.fire, session_id, "manual")
                await send(_rescue_payload(response, "manual") if response else {"type": "none"})
                continue

            if data.get("type") == "check_slip":
                correction = await asyncio.to_thread(slip.check, session_id)
                await send(_correction_payload(correction) if correction else {"type": "none"})
                continue

            try:
                message = TranscriptMessage(**data)
            except ValidationError:
                await send({"type": "error", "detail": "invalid transcript message"})
                continue

            segment = service.append_segment(session_id, message.text, message.ts)
            window = service.get_window(session_id, settings.transcript_window_s)
            await send(
                {
                    "type": "ack",
                    "segments": service.segment_count(session_id),
                    "window_chars": len(window),
                    "silence_s": round(service.silence_seconds(session_id), 3),
                    "last_ts": segment.ts,
                }
            )
    except WebSocketDisconnect:
        pass
    finally:
        scan_task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await scan_task
