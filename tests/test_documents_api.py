"""Endpoint tests for POST /documents and GET /documents."""

from __future__ import annotations

from fastapi.testclient import TestClient

from tests import sample_docs

SENTINEL = "Cue rescues your presentation"


def test_upload_then_list(client: TestClient) -> None:
    resp = client.post(
        "/documents",
        files={"file": ("notes.txt", sample_docs.make_txt_bytes(SENTINEL), "text/plain")},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["doc_type"] == "txt"
    assert body["char_count"] > 0
    assert SENTINEL in body["preview"]
    doc_id = body["id"]

    listing = client.get("/documents")
    assert listing.status_code == 200
    items = listing.json()
    assert [item["id"] for item in items] == [doc_id]
    assert "text" not in items[0]  # list view is metadata + preview only


def test_upload_pdf(client: TestClient) -> None:
    resp = client.post(
        "/documents",
        files={"file": ("deck.pdf", sample_docs.make_pdf_bytes(SENTINEL), "application/pdf")},
    )
    assert resp.status_code == 201
    assert resp.json()["doc_type"] == "pdf"


def test_unsupported_type_returns_415(client: TestClient) -> None:
    resp = client.post(
        "/documents",
        files={"file": ("evil.exe", b"MZ\x00\x00", "application/octet-stream")},
    )
    assert resp.status_code == 415
    assert set(resp.json().keys()) == {"error", "detail"}


def test_empty_document_returns_422(client: TestClient) -> None:
    resp = client.post(
        "/documents",
        files={"file": ("blank.txt", b"   \n\t  ", "text/plain")},
    )
    assert resp.status_code == 422
    assert set(resp.json().keys()) == {"error", "detail"}


def test_missing_file_returns_422(client: TestClient) -> None:
    resp = client.post("/documents")
    assert resp.status_code == 422
    assert resp.json()["error"] == "validation_error"
