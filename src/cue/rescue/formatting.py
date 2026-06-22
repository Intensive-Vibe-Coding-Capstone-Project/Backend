"""Render a rescue script as short, speakable "lyric" lines."""

from __future__ import annotations


def _wrap(line: str, max_chars: int) -> list[str]:
    """Greedily wrap one line onto <= max_chars at word boundaries."""
    if len(line) <= max_chars:
        return [line]
    wrapped: list[str] = []
    current = ""
    for word in line.split():
        if current and len(current) + 1 + len(word) > max_chars:
            wrapped.append(current)
            current = word
        else:
            current = f"{current} {word}".strip()
    if current:
        wrapped.append(current)
    return wrapped


def to_lyric_lines(text: str, max_chars: int) -> list[str]:
    """Split model output into short lines: honor existing line breaks, then wrap.

    Keeps each line within `max_chars` (never splitting a word) so the UI can
    render it karaoke / lyric style.
    """
    lines: list[str] = []
    for raw in text.splitlines():
        stripped = raw.strip()
        if stripped:
            lines.extend(_wrap(stripped, max_chars))
    return lines
