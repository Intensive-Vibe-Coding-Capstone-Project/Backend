"""Rescue orchestrator: retrieve -> ground -> generate a speakable script.

The core grounding rule lives here: if retrieval has no support (no passages, or
the top score is below `rescue_min_score`), return a safe bridge line WITHOUT
calling the model. Otherwise the model only sees retrieved passages, and every
response carries its citations. See docs/02-engineering/rescue-prompt.md.

An optional `session_id` records the exchange in the session history (D5).
"""

from __future__ import annotations

import logging

from cue.config import Settings, get_settings
from cue.rag import index
from cue.rescue.formatting import to_lyric_lines
from cue.rescue.generator import get_generator
from cue.rescue.models import Citation, RescueResponse
from cue.rescue.prompt import build_prompt
from cue.sessions import service as sessions_service
from cue.sessions.errors import SessionNotFoundError

logger = logging.getLogger(__name__)

# Safe fallback when nothing supports an answer (no LLM call, no invented facts).
BRIDGE_LINE = (
    "That's a great question — let me give you the precise detail on that in just a moment."
)

# If the model says it can't answer from the passages, treat it as unsupported.
# This is the primary grounding guard (the score floor is just a pre-filter):
# embedding similarity alone is unreliable for short queries.
_REFUSAL_MARKERS = (
    "i don't have",
    "i do not have",
    "don't have that",
    "do not have that",
    "don't cover",
    "do not cover",
    "not covered",
    "isn't covered",
    "no information",
    "no relevant",
    "no details",
    "cannot answer",
    "can't answer",
    "unable to answer",
    "doesn't mention",
    "don't mention",
    "not mentioned",
)


def _is_refusal(text: str) -> bool:
    lowered = text.lower()
    return any(marker in lowered for marker in _REFUSAL_MARKERS)


def _bridge() -> RescueResponse:
    return RescueResponse(script=BRIDGE_LINE, lines=[BRIDGE_LINE], grounded=False, citations=[])


def _build_response(question: str, k: int | None, settings: Settings) -> RescueResponse:
    k = k if k is not None else settings.retrieval_k
    passages = index.query(question, k)[: settings.rescue_max_passages]
    supported = bool(passages) and passages[0].score >= settings.rescue_min_score
    if not supported:
        return _bridge()

    try:
        text = get_generator(settings).generate(build_prompt(question, passages))
    except Exception:
        # A live tool must never hard-fail on the rescue path (e.g. a transient
        # Gemini 503) — degrade to the safe bridge line instead.
        logger.exception("Rescue generation failed; returning bridge line")
        return _bridge()

    if _is_refusal(text):
        # The model judged the passages insufficient — report unsupported.
        return _bridge()

    lines = to_lyric_lines(text, settings.lyric_max_chars)
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


def generate_rescue(
    question: str, k: int | None = None, session_id: str | None = None
) -> RescueResponse:
    """Produce a grounded rescue script (or bridge), optionally recording a turn.

    Raises `SessionNotFoundError` if `session_id` is given but does not exist.
    """
    settings = get_settings()
    if session_id is not None and not sessions_service.session_exists(session_id):
        raise SessionNotFoundError(session_id)

    response = _build_response(question, k, settings)

    if session_id is not None:
        sessions_service.record_turn(session_id, question, response)
    return response
