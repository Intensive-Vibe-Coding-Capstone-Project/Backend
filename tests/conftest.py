"""Shared pytest fixtures."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from cue.api.app import create_app
from cue.ingestion import service


@pytest.fixture(autouse=True)
def _clear_registry() -> None:
    """Isolate tests: empty the in-memory document registry before each test."""
    service.clear()


@pytest.fixture
def client() -> TestClient:
    """A TestClient bound to a fresh app instance."""
    return TestClient(create_app())
