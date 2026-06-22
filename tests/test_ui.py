"""The demo UI is served and does not shadow the API error envelope."""

from __future__ import annotations

from fastapi.testclient import TestClient


def test_ui_index_served(client: TestClient) -> None:
    resp = client.get("/ui/")
    assert resp.status_code == 200
    assert "text/html" in resp.headers["content-type"]
    assert "Cue" in resp.text


def test_root_redirects_to_ui(client: TestClient) -> None:
    resp = client.get("/", follow_redirects=False)
    assert resp.status_code == 307
    assert resp.headers["location"] == "/ui/"


def test_unknown_api_path_still_uses_error_envelope(client: TestClient) -> None:
    # Mounting the UI must not turn unknown API routes into static 404s.
    resp = client.get("/definitely-not-a-route")
    assert resp.status_code == 404
    assert set(resp.json().keys()) == {"error", "detail"}
