"""Rescue orchestrator: build grounded prompt -> Gemini -> speakable script.

The core. Combines retrieved passages + transcript window + persona/style, and
returns a short line-by-line rescue script with citations. Lands D4.
"""
