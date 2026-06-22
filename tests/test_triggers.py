"""Tests for the trigger engine and the WS manual-trigger path."""

from __future__ import annotations

import time

from fastapi.testclient import TestClient

from cue.config import get_settings
from cue.ingestion.models import DocType, ParsedDocument
from cue.rag import index
from cue.sessions import service as sessions_service
from cue.transcript import service as transcript_service
from cue.triggers import engine

# A doc + an overlapping transcript window so retrieval grounds the rescue.
DOC = "Cue returns a grounded rescue script when the speaker faces a hard question."
WINDOW = "they just asked for the grounded rescue script for a hard question"
OFF_TOPIC = "banana umbrella helicopter spaceship volcano picnic"


def _index_doc() -> None:
    index.index_document(
        ParsedDocument(
            id="d1", filename="d1.txt", doc_type=DocType.txt, char_count=len(DOC), text=DOC
        )
    )


# --- should_fire -------------------------------------------------------------


def test_should_fire_min_chars_and_dedup() -> None:
    assert engine.should_fire("tiny", None, min_chars=20) is False
    long_text = "a reasonably long transcript window"
    assert engine.should_fire(long_text, None, min_chars=20) is True
    assert engine.should_fire(long_text, long_text, min_chars=20) is False  # unchanged


# --- fire --------------------------------------------------------------------


def test_manual_fire_grounds_and_records_turn() -> None:
    _index_doc()
    session = sessions_service.create_session()
    transcript_service.append_segment(session.id, WINDOW)

    resp = engine.fire(session.id, "manual")
    assert resp is not None
    assert resp.grounded is True

    detail = sessions_service.get_session_detail(session.id)
    assert len(detail.turns) == 1
    assert detail.turns[0].question == WINDOW


def test_manual_fire_empty_window_returns_none() -> None:
    session = sessions_service.create_session()
    assert engine.fire(session.id, "manual") is None


def test_periodic_suppresses_ungrounded_and_dedups() -> None:
    _index_doc()
    session = sessions_service.create_session()

    # Off-topic window -> bridge -> suppressed on a periodic scan.
    transcript_service.append_segment(session.id, OFF_TOPIC)
    assert engine.fire(session.id, "periodic") is None
    assert sessions_service.get_session_detail(session.id).turns == []

    # Grounded window -> fires once...
    transcript_service.append_segment(session.id, " " + WINDOW)
    first = engine.fire(session.id, "periodic")
    assert first is not None and first.grounded is True
    # ...and dedups on an unchanged window.
    assert engine.fire(session.id, "periodic") is None


# --- keyword + silence auto-triggers (D11) -----------------------------------


def test_matched_keyword() -> None:
    kws = get_settings().trigger_keywords
    assert engine.matched_keyword("hmm, that's a good question really", kws) == "good question"
    assert engine.matched_keyword("just carrying on as normal here", kws) is None


def test_auto_reason_keyword_beats_length_gate() -> None:
    session = sessions_service.create_session()
    # "good question" is only 13 chars — under trigger_min_chars (20) — so a
    # plain periodic scan wouldn't fire, but the keyword reason still does.
    transcript_service.append_segment(session.id, "good question")
    assert engine.auto_reason(session.id, get_settings()) == "keyword"


def test_auto_fire_keyword_grounds_and_records() -> None:
    _index_doc()
    session = sessions_service.create_session()
    transcript_service.append_segment(session.id, "good question — " + WINDOW)
    response, mode = engine.auto_fire(session.id)
    assert mode == "keyword"
    assert response is not None and response.grounded is True
    assert len(sessions_service.get_session_detail(session.id).turns) == 1


def test_auto_fire_silence_when_speaker_pauses() -> None:
    _index_doc()
    session = sessions_service.create_session()
    # Last utterance landed 12s ago: inside the 30s window but past the 10s
    # silence threshold, and it carries no keyword -> "silence".
    transcript_service.append_segment(session.id, WINDOW, ts=time.time() - 12)
    response, mode = engine.auto_fire(session.id)
    assert mode == "silence"
    assert response is not None and response.grounded is True


def test_auto_fire_periodic_on_fresh_content() -> None:
    _index_doc()
    session = sessions_service.create_session()
    transcript_service.append_segment(session.id, WINDOW)  # recent, no keyword
    response, mode = engine.auto_fire(session.id)
    assert mode == "periodic"
    assert response is not None
    # Dedups: unchanged window yields nothing on the next scan.
    assert engine.auto_fire(session.id) == (None, None)


def test_auto_fire_quiet_when_idle() -> None:
    session = sessions_service.create_session()
    assert engine.auto_fire(session.id) == (None, None)


# --- WS manual trigger -------------------------------------------------------


def test_ws_manual_trigger_pushes_rescue(client: TestClient) -> None:
    _index_doc()
    session = client.post("/sessions", json={}).json()
    with client.websocket_connect(f"/stream/{session['id']}") as ws:
        ws.send_json({"text": WINDOW})
        ws.receive_json()  # transcript ack

        ws.send_json({"type": "trigger"})
        msg = ws.receive_json()
        assert msg["type"] == "rescue"
        assert msg["mode"] == "manual"
        assert msg["lines"]


def test_ws_manual_trigger_empty_returns_none(client: TestClient) -> None:
    session = client.post("/sessions", json={}).json()
    with client.websocket_connect(f"/stream/{session['id']}") as ws:
        ws.send_json({"type": "trigger"})
        assert ws.receive_json()["type"] == "none"
