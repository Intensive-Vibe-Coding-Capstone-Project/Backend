"""Slip / flow detection (PRD use cases 3 & 4).

Compares the spoken transcript window against the session's prepared script:
- **brand slip** — the speaker said a forbidden term (e.g. a competitor's name);
- **off-flow** — the spoken window barely overlaps the prepared script.

Detection is lexical (deterministic, provider-independent). The correction text
is generated grounded in the prepared script, with a templated fallback so it
still works offline / during a Gemini outage.
"""

from __future__ import annotations

import logging
import re
from typing import Literal

from pydantic import BaseModel

from cue.config import Settings, get_settings
from cue.rag.models import Passage
from cue.rescue.formatting import to_lyric_lines
from cue.rescue.generator import get_generator
from cue.rescue.prompt import RescuePrompt
from cue.sessions import service as sessions_service
from cue.transcript import service as transcript_service

logger = logging.getLogger(__name__)

_TOKEN = re.compile(r"[a-z0-9]+")

CORRECTION_SYSTEM = (
    "You are Cue, helping a speaker stay on message. They have drifted from their "
    "prepared script. Using ONLY the prepared script, write a short, calm spoken "
    "correction (2-4 short lines, no markdown) that points out the slip and gives "
    "the on-message wording. Never invent facts beyond the script."
)


class SlipCorrection(BaseModel):
    kind: Literal["brand", "off_flow"]
    wrong_terms: list[str]
    lines: list[str]
    message: str


def detect_brand_slip(spoken: str, forbidden_terms: list[str]) -> list[str]:
    """Forbidden terms that appear (as whole words) in the spoken window."""
    low = spoken.lower()
    found = []
    for term in forbidden_terms:
        if re.search(rf"\b{re.escape(term.lower())}\b", low):
            found.append(term)
    return found


def overlap_ratio(spoken: str, prepared: str) -> float:
    """Fraction of spoken word-tokens that also appear in the prepared script."""
    spoken_tokens = set(_TOKEN.findall(spoken.lower()))
    if not spoken_tokens:
        return 1.0
    prepared_tokens = set(_TOKEN.findall(prepared.lower()))
    return len(spoken_tokens & prepared_tokens) / len(spoken_tokens)


def detect_off_flow(spoken: str, prepared: str, min_overlap: float) -> bool:
    return overlap_ratio(spoken, prepared) < min_overlap


def _build_correction_prompt(
    prepared: str, spoken: str, kind: str, wrong: list[str]
) -> RescuePrompt:
    passage = Passage(
        doc_id="script", filename="prepared_script", chunk_index=0, text=prepared, score=1.0
    )
    issue = (
        f"They said an off-brand term: {', '.join(wrong)}."
        if kind == "brand"
        else "They have drifted off the prepared script."
    )
    user_message = (
        f"PREPARED SCRIPT:\n{prepared}\n\n"
        f"WHAT THEY JUST SAID:\n{spoken}\n\n"
        f"ISSUE: {issue}\n\n"
        "Write the short spoken correction now."
    )
    return RescuePrompt(
        question=spoken,
        passages=[passage],
        system_instruction=CORRECTION_SYSTEM,
        user_message=user_message,
    )


def _correction_lines(settings: Settings, prepared: str, spoken: str, kind: str, wrong: list[str]):
    try:
        text = get_generator(settings).generate(
            _build_correction_prompt(prepared, spoken, kind, wrong)
        )
        lines = to_lyric_lines(text, settings.lyric_max_chars)
        if lines:
            return lines
    except Exception:
        logger.exception("Slip correction generation failed; using templated fallback")

    fallback = (
        f"Quick correction — you said {', '.join(wrong)}. Use the prepared wording."
        if kind == "brand"
        else "Let's get back on track — return to your prepared script."
    )
    return to_lyric_lines(fallback, settings.lyric_max_chars)


def check(session_id: str) -> SlipCorrection | None:
    """Detect a slip in the recent window and return a grounded correction."""
    settings = get_settings()
    script = sessions_service.get_prepared_script(session_id)
    if script is None or not script.text.strip():
        return None

    spoken = transcript_service.get_window(session_id).strip()
    if len(spoken) < settings.trigger_min_chars:
        return None

    wrong = detect_brand_slip(spoken, script.forbidden_terms)
    off_flow = detect_off_flow(spoken, script.text, settings.slip_min_overlap)
    if not wrong and not off_flow:
        return None

    kind: Literal["brand", "off_flow"] = "brand" if wrong else "off_flow"
    lines = _correction_lines(settings, script.text, spoken, kind, wrong)
    return SlipCorrection(kind=kind, wrong_terms=wrong, lines=lines, message="\n".join(lines))
