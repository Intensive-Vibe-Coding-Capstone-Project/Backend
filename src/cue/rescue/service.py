"""Rescue orchestrator: retrieve -> ground -> generate a speakable script.

The core grounding rule lives here: if retrieval has no support (no passages, or
the top score is below `rescue_min_score`), return a safe bridge line WITHOUT
calling the model. Otherwise the model only sees retrieved passages, and every
response carries its citations. See docs/02-engineering/rescue-prompt.md.
"""

from __future__ import annotations

from cue.config import get_settings
from cue.rag import index
from cue.rescue.generator import get_generator
from cue.rescue.models import Citation, RescueResponse
from cue.rescue.prompt import build_prompt

# Safe fallback when nothing supports an answer (no LLM call, no invented facts).
BRIDGE_LINE = (
    "That's a great question — let me give you the precise detail on that in just a moment."
)


def _bridge() -> RescueResponse:
    return RescueResponse(script=BRIDGE_LINE, lines=[BRIDGE_LINE], grounded=False, citations=[])


def generate_rescue(question: str, k: int | None = None) -> RescueResponse:
    """Produce a grounded rescue script (or a bridge line if unsupported)."""
    settings = get_settings()
    k = k if k is not None else settings.retrieval_k

    passages = index.query(question, k)[: settings.rescue_max_passages]
    supported = bool(passages) and passages[0].score >= settings.rescue_min_score
    if not supported:
        return _bridge()

    text = get_generator(settings).generate(build_prompt(question, passages))
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        return _bridge()

    citations = [
        Citation(
            doc_id=p.doc_id,
            filename=p.filename,
            chunk_index=p.chunk_index,
            score=p.score,
        )
        for p in passages
    ]
    return RescueResponse(
        script="\n".join(lines),
        lines=lines,
        grounded=True,
        citations=citations,
    )
