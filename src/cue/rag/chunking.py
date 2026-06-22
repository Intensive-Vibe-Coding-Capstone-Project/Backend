"""Split normalized document text into overlapping, boundary-aware chunks."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Chunk:
    """A contiguous slice of a document's text."""

    index: int
    text: str
    start: int
    end: int


def chunk_text(text: str, size: int, overlap: int) -> list[Chunk]:
    """Chunk `text` into ~`size`-char pieces overlapping by `overlap` chars.

    Breaks on the nearest whitespace before the hard limit so chunks don't split
    mid-word. Overlap carries context across boundaries for better retrieval.
    """
    if size <= 0:
        raise ValueError("size must be positive")
    if overlap < 0:
        raise ValueError("overlap must be non-negative")
    overlap = min(overlap, size - 1)

    text = text.strip()
    n = len(text)
    chunks: list[Chunk] = []
    start = 0
    index = 0

    while start < n:
        end = min(start + size, n)
        # Prefer a whitespace boundary within the last `overlap` chars of the window.
        if end < n:
            boundary = max(
                text.rfind(" ", start + 1, end),
                text.rfind("\n", start + 1, end),
            )
            if boundary > start:
                end = boundary

        piece = text[start:end].strip()
        if piece:
            chunks.append(Chunk(index=index, text=piece, start=start, end=end))
            index += 1

        if end >= n:
            break
        start = max(end - overlap, start + 1)

    return chunks
