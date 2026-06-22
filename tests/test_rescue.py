"""Tests for the rescue orchestrator + POST /rescue (offline fake generator)."""

from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient

from cue.ingestion.models import DocType, ParsedDocument
from cue.rag import index
from cue.rescue import service

EVAL_PATH = Path(__file__).parent / "eval" / "grounding.jsonl"


def _index(text: str, doc_id: str = "d1") -> None:
    index.index_document(
        ParsedDocument(
            id=doc_id,
            filename=f"{doc_id}.txt",
            doc_type=DocType.txt,
            char_count=len(text),
            text=text,
        )
    )


def test_supported_question_is_grounded_with_citations() -> None:
    _index("Cue returns a grounded rescue script when the speaker faces a hard question.")
    resp = service.generate_rescue("grounded rescue script hard question")
    assert resp.grounded is True
    assert resp.lines
    assert resp.citations and resp.citations[0].doc_id == "d1"
    assert "rescue" in resp.script.lower()


def test_unsupported_question_returns_bridge() -> None:
    _index("Cue returns a grounded rescue script when the speaker faces a hard question.")
    resp = service.generate_rescue("banana umbrella helicopter spaceship volcano")
    assert resp.grounded is False
    assert resp.citations == []
    assert resp.script == service.BRIDGE_LINE


def test_generation_failure_degrades_to_bridge(monkeypatch) -> None:
    _index("Cue returns a grounded rescue script when the speaker faces a hard question.")

    class _Boom:
        def generate(self, prompt):
            raise RuntimeError("simulated Gemini 503")

    monkeypatch.setattr(service, "get_generator", lambda settings=None: _Boom())
    resp = service.generate_rescue("grounded rescue script hard question")
    assert resp.grounded is False
    assert resp.script == service.BRIDGE_LINE


def test_model_refusal_is_reported_as_ungrounded(monkeypatch) -> None:
    _index("Cue returns a grounded rescue script when the speaker faces a hard question.")

    class _Refuser:
        def generate(self, prompt):
            return "I don't have that information in the provided documents."

    monkeypatch.setattr(service, "get_generator", lambda settings=None: _Refuser())
    resp = service.generate_rescue("grounded rescue script hard question")
    assert resp.grounded is False
    assert resp.citations == []


def test_rescue_endpoint_returns_script(client: TestClient) -> None:
    _index("The periodic scan inspects the transcript every thirty seconds for trouble.")
    resp = client.post("/rescue", json={"question": "periodic scan transcript thirty seconds"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["grounded"] is True
    assert body["lines"]
    assert body["citations"][0]["filename"].endswith(".txt")


def test_rescue_endpoint_blank_question_422(client: TestClient) -> None:
    resp = client.post("/rescue", json={"question": "   "})
    assert resp.status_code == 422
    assert resp.json()["error"] == "validation_error"


def test_grounding_eval_seed() -> None:
    """The seeded grounding cases must classify grounded vs bridge correctly."""
    records = [json.loads(line) for line in EVAL_PATH.read_text(encoding="utf-8").splitlines()]
    assert len(records) >= 5
    for i, rec in enumerate(records):
        _index(rec["doc"], doc_id=f"eval{i}")
    for rec in records:
        resp = service.generate_rescue(rec["question"])
        assert resp.grounded is rec["expect_grounded"], rec["id"]
