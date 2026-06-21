"""
Tests for the FastAPI application endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


class TestHealthEndpoints:
    """Test health check endpoints."""

    def test_root_endpoint(self):
        """Root should return app info."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert "docs" in data

    def test_health_check(self):
        """Health check should return healthy status."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "services" in data


class TestDocumentEndpoints:
    """Test document API endpoints."""

    def test_list_documents_empty(self):
        """Should return empty list when no documents uploaded."""
        response = client.get("/api/v1/documents/")
        assert response.status_code == 200
        assert response.json() == []

    def test_get_nonexistent_document(self):
        """Should return 404 for non-existent document."""
        response = client.get("/api/v1/documents/nonexistent_id")
        assert response.status_code == 404

    def test_delete_nonexistent_document(self):
        """Should return 404 when deleting non-existent document."""
        response = client.delete("/api/v1/documents/nonexistent_id")
        assert response.status_code == 404


class TestChatEndpoints:
    """Test chat API endpoints."""

    def test_list_conversations_empty(self):
        """Should return empty list when no conversations exist."""
        response = client.get("/api/v1/chat/history")
        assert response.status_code == 200
        assert response.json() == []

    def test_get_nonexistent_conversation(self):
        """Should return 404 for non-existent conversation."""
        response = client.get("/api/v1/chat/history/nonexistent_id")
        assert response.status_code == 404

    def test_send_chat_message(self):
        """Should process a chat message and return a response."""
        response = client.post(
            "/api/v1/chat/",
            json={"message": "What is the quarterly revenue?"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert "conversation_id" in data
        assert "formatted_lines" in data


class TestVoiceEndpoints:
    """Test voice API endpoints."""

    def test_analyze_signals_normal_text(self):
        """Should analyze text and return no signals for normal speech."""
        response = client.post(
            "/api/v1/voice/analyze-signals",
            params={
                "text": "Our quarterly revenue increased by 15 percent",
                "language": "en",
                "pause_duration_ms": 0,
                "timestamp_ms": 0,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "signals" in data
        assert data["needs_assistance"] is False

    def test_analyze_signals_difficulty_text(self):
        """Should detect signals when difficulty keywords are present."""
        response = client.post(
            "/api/v1/voice/analyze-signals",
            params={
                "text": "Hmm, that's a good question, let me check that",
                "language": "en",
                "pause_duration_ms": 15000,
                "timestamp_ms": 0,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["signals"]) > 0
        assert data["needs_assistance"] is True
