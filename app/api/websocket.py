"""
WebSocket handler for real-time communication.
Supports streaming chat responses and voice interaction.
"""

import json
import logging
import uuid
from datetime import datetime
from fastapi import WebSocket, WebSocketDisconnect

from app.agents.orchestrator import agent_orchestrator
from app.services.signals.detector import signal_detector
from app.models.schemas import Language

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages active WebSocket connections."""

    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        """Accept and register a new WebSocket connection."""
        await websocket.accept()
        self.active_connections[client_id] = websocket
        logger.info(f"WebSocket connected: {client_id} (total: {len(self.active_connections)})")

    def disconnect(self, client_id: str):
        """Remove a disconnected client."""
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            logger.info(f"WebSocket disconnected: {client_id} (total: {len(self.active_connections)})")

    async def send_json(self, client_id: str, data: dict):
        """Send JSON data to a specific client."""
        ws = self.active_connections.get(client_id)
        if ws:
            await ws.send_json(data)

    async def broadcast(self, data: dict):
        """Broadcast JSON data to all connected clients."""
        for client_id, ws in self.active_connections.items():
            try:
                await ws.send_json(data)
            except Exception as e:
                logger.error(f"Failed to broadcast to {client_id}: {e}")


# Singleton connection manager
manager = ConnectionManager()


async def websocket_endpoint(websocket: WebSocket):
    """
    Main WebSocket endpoint handler.

    Client → Server events:
    - chat_message: {message, conversation_id?}
    - voice_stream_start: {language, mode}
    - voice_chunk: {audio_data}  (base64)
    - voice_stream_end: {}
    - signal_check: {text, pause_duration_ms?, language?}

    Server → Client events:
    - response_chunk: {text, is_final}
    - signal_detected: {type, confidence, trigger}
    - suggestion: {text, sources}
    - error: {code, message}
    - connected: {client_id}
    """
    client_id = f"ws_{uuid.uuid4().hex[:8]}"
    await manager.connect(websocket, client_id)

    # Send connection confirmation
    await manager.send_json(client_id, {
        "event": "connected",
        "client_id": client_id,
        "timestamp": datetime.utcnow().isoformat(),
    })

    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                event = message.get("event", "unknown")

                if event == "chat_message":
                    await _handle_chat_message(client_id, message)
                elif event == "signal_check":
                    await _handle_signal_check(client_id, message)
                elif event == "voice_stream_start":
                    await _handle_voice_start(client_id, message)
                elif event == "voice_chunk":
                    await _handle_voice_chunk(client_id, message)
                elif event == "voice_stream_end":
                    await _handle_voice_end(client_id, message)
                elif event == "ping":
                    await manager.send_json(client_id, {"event": "pong"})
                else:
                    await manager.send_json(client_id, {
                        "event": "error",
                        "code": "unknown_event",
                        "message": f"Unknown event type: {event}",
                    })

            except json.JSONDecodeError:
                await manager.send_json(client_id, {
                    "event": "error",
                    "code": "invalid_json",
                    "message": "Invalid JSON payload",
                })

    except WebSocketDisconnect:
        manager.disconnect(client_id)
    except Exception as e:
        logger.error(f"WebSocket error for {client_id}: {e}")
        manager.disconnect(client_id)


async def _handle_chat_message(client_id: str, message: dict):
    """Process a chat message and stream the response."""
    query = message.get("message", "")
    doc_ids = message.get("document_ids")

    if not query:
        await manager.send_json(client_id, {
            "event": "error",
            "code": "empty_message",
            "message": "Message cannot be empty",
        })
        return

    # Send acknowledgment
    await manager.send_json(client_id, {
        "event": "response_chunk",
        "text": "",
        "is_final": False,
        "status": "processing",
    })

    # Process through agent pipeline
    result = await agent_orchestrator.process_query(
        query=query,
        doc_ids=doc_ids,
    )

    # Stream response line by line (lyrics-style)
    for i, line in enumerate(result.get("formatted_lines", [])):
        is_last = i == len(result.get("formatted_lines", [])) - 1
        await manager.send_json(client_id, {
            "event": "response_chunk",
            "text": line,
            "is_final": is_last,
            "line_index": i,
        })

    # Send sources
    sources = result.get("sources", [])
    if sources:
        await manager.send_json(client_id, {
            "event": "sources",
            "sources": [
                {
                    "document": s.document if hasattr(s, "document") else s.get("document", ""),
                    "relevance": s.relevance if hasattr(s, "relevance") else s.get("relevance", 0),
                }
                for s in sources
            ],
        })


async def _handle_signal_check(client_id: str, message: dict):
    """Check text for difficulty signals."""
    text = message.get("text", "")
    pause_ms = message.get("pause_duration_ms", 0)
    language = message.get("language", "en")

    signal_detector.set_language(Language(language))
    result = signal_detector.full_analysis(
        text=text,
        pause_duration_ms=pause_ms,
    )

    if result.needs_assistance:
        # Send detected signals
        for signal in result.signals:
            await manager.send_json(client_id, {
                "event": "signal_detected",
                "type": signal.type.value,
                "confidence": signal.confidence,
                "trigger": signal.trigger,
                "suggested_action": signal.suggested_action,
            })


async def _handle_voice_start(client_id: str, message: dict):
    """Handle the start of a voice stream."""
    language = message.get("language", "en")
    await manager.send_json(client_id, {
        "event": "voice_stream_started",
        "language": language,
    })
    logger.info(f"Voice stream started for {client_id} (lang: {language})")


async def _handle_voice_chunk(client_id: str, message: dict):
    """Handle incoming audio chunks."""
    # TODO: Process audio chunks for real-time STT (Day 5)
    pass


async def _handle_voice_end(client_id: str, message: dict):
    """Handle the end of a voice stream."""
    await manager.send_json(client_id, {
        "event": "voice_stream_ended",
    })
    logger.info(f"Voice stream ended for {client_id}")
