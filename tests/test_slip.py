"""Tests for slip/flow detection, the set-script endpoint, and the WS path."""

from __future__ import annotations

from fastapi.testclient import TestClient

from cue.sessions import service as sessions_service
from cue.sessions.models import PreparedScript
from cue.transcript import service as transcript_service
from cue.triggers import slip

SCRIPT = (
    "Today we are selling on TikTokShop. Add the product to your cart and check out "
    "securely with the official app."
)
FORBIDDEN = ["Shopee", "Lazada"]

ON_SCRIPT = "add the product to your cart and check out with the official app"
BRAND_SLIP = "great deal, just go to Shopee and grab it over there"
OFF_TOPIC = "my cat jumped over the fence chasing a butterfly in the garden"


def _session_with_script() -> str:
    session = sessions_service.create_session()
    sessions_service.set_prepared_script(
        session.id, PreparedScript(text=SCRIPT, forbidden_terms=FORBIDDEN)
    )
    return session.id


# --- detection units ---------------------------------------------------------


def test_detect_brand_slip() -> None:
    assert slip.detect_brand_slip("go to Shopee now", FORBIDDEN) == ["Shopee"]
    assert slip.detect_brand_slip("all good here", FORBIDDEN) == []


def test_off_flow_detection() -> None:
    assert slip.detect_off_flow(ON_SCRIPT, SCRIPT, 0.3) is False
    assert slip.detect_off_flow(OFF_TOPIC, SCRIPT, 0.3) is True


# --- check() integration -----------------------------------------------------


def test_check_brand_slip() -> None:
    sid = _session_with_script()
    transcript_service.append_segment(sid, BRAND_SLIP)
    correction = slip.check(sid)
    assert correction is not None
    assert correction.kind == "brand"
    assert correction.wrong_terms == ["Shopee"]
    assert correction.lines


def test_check_off_flow() -> None:
    sid = _session_with_script()
    transcript_service.append_segment(sid, OFF_TOPIC)
    correction = slip.check(sid)
    assert correction is not None
    assert correction.kind == "off_flow"


def test_check_on_script_returns_none() -> None:
    sid = _session_with_script()
    transcript_service.append_segment(sid, ON_SCRIPT)
    assert slip.check(sid) is None


def test_check_without_script_returns_none() -> None:
    session = sessions_service.create_session()
    transcript_service.append_segment(session.id, BRAND_SLIP)
    assert slip.check(session.id) is None


# --- endpoint + WS -----------------------------------------------------------


def test_set_script_endpoint(client: TestClient) -> None:
    session = client.post("/sessions", json={}).json()
    resp = client.put(
        f"/sessions/{session['id']}/script",
        json={"text": SCRIPT, "forbidden_terms": FORBIDDEN},
    )
    assert resp.status_code == 204

    missing = client.put("/sessions/ghost/script", json={"text": "x"})
    assert missing.status_code == 404


def test_ws_check_slip_pushes_correction(client: TestClient) -> None:
    session = client.post("/sessions", json={}).json()
    client.put(
        f"/sessions/{session['id']}/script",
        json={"text": SCRIPT, "forbidden_terms": FORBIDDEN},
    )
    with client.websocket_connect(f"/stream/{session['id']}") as ws:
        ws.send_json({"text": BRAND_SLIP})
        ws.receive_json()  # ack
        ws.send_json({"type": "check_slip"})
        msg = ws.receive_json()
        assert msg["type"] == "correction"
        assert msg["kind"] == "brand"
        assert msg["wrong_terms"] == ["Shopee"]
