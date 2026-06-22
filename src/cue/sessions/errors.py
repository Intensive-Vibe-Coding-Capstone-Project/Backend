"""Domain errors for sessions."""

from __future__ import annotations


class SessionNotFoundError(Exception):
    """Referenced a session id that does not exist."""
