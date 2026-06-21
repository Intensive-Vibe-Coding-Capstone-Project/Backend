"""Core package — configuration, security, and shared dependencies."""

from app.core.config import get_settings, Settings

__all__ = ["get_settings", "Settings"]
