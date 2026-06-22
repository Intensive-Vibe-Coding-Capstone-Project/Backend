"""Build the grounded rescue prompt. Mirrors docs/02-engineering/rescue-prompt.md.

Keep this file and that doc in sync — the doc is the source of truth.
"""

from __future__ import annotations

from dataclasses import dataclass

from cue.rag.models import Passage

SYSTEM_INSTRUCTION = (
    "You are Cue, a real-time presentation rescue assistant. A speaker needs a "
    "short, confident, ready-to-speak answer grounded ONLY in the provided source "
    "passages.\n"
    "Rules:\n"
    "- Use ONLY the passages. Never add outside facts.\n"
    "- If the passages do not support an answer, reply with a brief bridge line "
    "that stalls gracefully WITHOUT inventing facts.\n"
    "- Output 2-6 short spoken lines, one phrase per line. No markdown, no bullets.\n"
    "- Be calm, on-message, and concise."
)


@dataclass(frozen=True)
class RescuePrompt:
    """Everything a generator needs: the strings for an LLM and the structured
    passages for the offline fake generator."""

    question: str
    passages: list[Passage]
    system_instruction: str
    user_message: str


def format_passages(passages: list[Passage]) -> str:
    return "\n".join(f"[{i + 1}] (source: {p.filename}) {p.text}" for i, p in enumerate(passages))


def build_prompt(question: str, passages: list[Passage]) -> RescuePrompt:
    user_message = (
        f"QUESTION:\n{question}\n\n"
        f"SOURCE PASSAGES:\n{format_passages(passages)}\n\n"
        "Write the rescue script now (short spoken lines only)."
    )
    return RescuePrompt(
        question=question,
        passages=passages,
        system_instruction=SYSTEM_INSTRUCTION,
        user_message=user_message,
    )
