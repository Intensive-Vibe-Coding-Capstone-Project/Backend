"""Health endpoint smoke tests — proves the app boots and routes resolve."""

from __future__ import annotations

from fastapi.testclient import TestClient

from cue import __version__


def test_health_ok(client: TestClient) -> None:
    resp = client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert body["version"] == __version__
    assert body["env"] in {"dev", "prod"}
    assert isinstance(body["gemini_configured"], bool)


def test_unknown_route_uses_error_shape(client: TestClient) -> None:
    resp = client.get("/does-not-exist")
    assert resp.status_code == 404
    body = resp.json()
    # Consistent error envelope per conventions: {error, detail}
    assert set(body.keys()) == {"error", "detail"}
