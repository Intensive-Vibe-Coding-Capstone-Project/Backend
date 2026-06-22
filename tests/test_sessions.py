"""Tests for the session store, lyric formatting, and session endpoints."""

from __future__ import annotations

from fastapi.testclient import TestClient

from cue.ingestion.models import DocType, ParsedDocument
from cue.rag import index
from cue.rescue.formatting import to_lyric_lines
from cue.rescue.models import Citation, RescueResponse
from cue.sessions import service


def _index_doc() -> None:
    text = "Cue returns a grounded rescue script when the speaker faces a hard question."
    index.index_document(
        ParsedDocument(
            id="d1", filename="d1.txt", doc_type=DocType.txt, char_count=len(text), text=text
        )
    )


# --- store / service ---------------------------------------------------------


def test_create_and_get_session_empty() -> None:
    session = service.create_session(title="Demo talk")
    detail = service.get_session_detail(session.id)
    assert detail is not None
    assert detail.title == "Demo talk"
    assert detail.turns == []


def test_record_turn_round_trips() -> None:
    session = service.create_session()
    response = RescueResponse(
        script="line one\nline two",
        lines=["line one", "line two"],
        grounded=True,
        citations=[Citation(doc_id="d1", filename="d1.txt", chunk_index=0, score=0.9)],
    )
    service.record_turn(session.id, "what is cue?", response)

    detail = service.get_session_detail(session.id)
    assert len(detail.turns) == 1
    turn = detail.turns[0]
    assert turn.question == "what is cue?"
    assert turn.lines == ["line one", "line two"]
    assert turn.grounded is True
    assert turn.citations[0].doc_id == "d1"


# --- lyric formatting --------------------------------------------------------


def test_to_lyric_lines_wraps_long_text() -> None:
    text = "This is a fairly long single line that should wrap into several short lyric lines."
    lines = to_lyric_lines(text, max_chars=20)
    assert len(lines) > 1
    assert all(len(line) <= 20 for line in lines)
    assert " ".join(lines) == text  # no words lost


# --- endpoints ---------------------------------------------------------------


def test_session_endpoints_record_rescue_turn(client: TestClient) -> None:
    _index_doc()
    created = client.post("/sessions", json={"title": "Q&A"})
    assert created.status_code == 201
    session_id = created.json()["id"]

    rescue = client.post(
        "/rescue",
        json={"question": "grounded rescue script hard question", "session_id": session_id},
    )
    assert rescue.status_code == 200

    detail = client.get(f"/sessions/{session_id}")
    assert detail.status_code == 200
    body = detail.json()
    assert body["title"] == "Q&A"
    assert len(body["turns"]) == 1
    assert body["turns"][0]["grounded"] is True


def test_get_missing_session_404(client: TestClient) -> None:
    resp = client.get("/sessions/nope")
    assert resp.status_code == 404
    assert set(resp.json().keys()) == {"error", "detail"}


def test_rescue_with_unknown_session_404(client: TestClient) -> None:
    resp = client.post("/rescue", json={"question": "anything", "session_id": "ghost"})
    assert resp.status_code == 404
    assert set(resp.json().keys()) == {"error", "detail"}
