"""RAG data models shared across the store / index / rescue layers."""

from __future__ import annotations

from pydantic import BaseModel


class Passage(BaseModel):
    """A retrieved chunk with its citation and similarity score.

    `doc_id` + `chunk_index` form the stable citation id (`doc_id:chunk_index`)
    so rescue answers (D4) can cite source passages verbatim.
    """

    doc_id: str
    filename: str
    chunk_index: int
    text: str
    score: float

    @property
    def citation_id(self) -> str:
        return f"{self.doc_id}:{self.chunk_index}"
