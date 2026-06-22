"""Rescue-script generators behind one `Generator` interface.

`GeminiGenerator` calls Gemini Flash; `FakeGenerator` is offline and grounded
(it only reflects retrieved passage text, never invents) so tests and keyless CI
stay green. `get_generator()` picks one from config.
"""

from __future__ import annotations

import logging
import re
import time
from typing import Protocol, runtime_checkable

from cue.config import Settings, get_settings
from cue.rescue.prompt import RescuePrompt

logger = logging.getLogger(__name__)

_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")


@runtime_checkable
class Generator(Protocol):
    """Turns a built prompt into rescue-script text (newline-separated lines)."""

    def generate(self, prompt: RescuePrompt) -> str: ...


class FakeGenerator:
    """Offline, deterministic, grounded: echo the top passages' sentences as lines.

    Never fabricates — output is drawn only from retrieved passage text.
    """

    def __init__(self, max_lines: int = 4) -> None:
        self._max_lines = max_lines

    def generate(self, prompt: RescuePrompt) -> str:
        lines: list[str] = []
        for passage in prompt.passages:
            for sentence in _SENTENCE_SPLIT.split(passage.text.strip()):
                sentence = sentence.strip()
                if sentence:
                    lines.append(sentence)
                if len(lines) >= self._max_lines:
                    return "\n".join(lines)
        return "\n".join(lines)


class GeminiGenerator:
    """Live rescue generation via Gemini Flash (low temperature for fidelity)."""

    def __init__(
        self,
        api_key: str,
        model: str,
        temperature: float,
        max_output_tokens: int,
        max_attempts: int = 3,
    ) -> None:
        from google import genai

        self._client = genai.Client(api_key=api_key)
        self._model = model
        self._temperature = temperature
        self._max_output_tokens = max_output_tokens
        self._max_attempts = max(1, max_attempts)

    def generate(self, prompt: RescuePrompt) -> str:
        from google.genai import types
        from google.genai.errors import ServerError

        config = types.GenerateContentConfig(
            system_instruction=prompt.system_instruction,
            temperature=self._temperature,
            max_output_tokens=self._max_output_tokens,
        )
        for attempt in range(1, self._max_attempts + 1):
            try:
                response = self._client.models.generate_content(
                    model=self._model, contents=prompt.user_message, config=config
                )
                return (response.text or "").strip()
            except ServerError:
                # Transient 5xx (e.g. 503 high demand) — back off briefly and retry.
                if attempt == self._max_attempts:
                    raise
                logger.warning("Gemini 5xx on attempt %d/%d; retrying", attempt, self._max_attempts)
                time.sleep(0.8 * attempt)
        raise RuntimeError("unreachable")  # pragma: no cover


def get_generator(settings: Settings | None = None) -> Generator:
    """Build the configured generator (`gemini` or `fake`, resolving `auto`)."""
    settings = settings or get_settings()
    if settings.active_generation_provider == "gemini":
        return GeminiGenerator(
            api_key=settings.gemini_api_key,
            model=settings.rescue_model,
            temperature=settings.rescue_temperature,
            max_output_tokens=settings.rescue_max_output_tokens,
            max_attempts=settings.rescue_max_attempts,
        )
    return FakeGenerator()
