"""Rolling, timestamped transcript buffer for one session.

Pure in-memory logic with an injectable clock so windowing and silence
detection are deterministic in tests. The D9 trigger engine reads `window()` /
`silence_seconds()` from here.
"""

from __future__ import annotations

import time
from collections.abc import Callable

from cue.transcript.models import TranscriptSegment


class TranscriptBuffer:
    """Append-only transcript with time-windowed reads."""

    def __init__(self, clock: Callable[[], float] = time.time) -> None:
        self._clock = clock
        self._segments: list[TranscriptSegment] = []

    def append(self, text: str, ts: float | None = None) -> TranscriptSegment:
        segment = TranscriptSegment(text=text, ts=ts if ts is not None else self._clock())
        self._segments.append(segment)
        return segment

    def window(self, seconds: float, now: float | None = None) -> list[TranscriptSegment]:
        """Segments received within the last `seconds`."""
        cutoff = (now if now is not None else self._clock()) - seconds
        return [seg for seg in self._segments if seg.ts >= cutoff]

    def window_text(self, seconds: float, now: float | None = None) -> str:
        return " ".join(seg.text for seg in self.window(seconds, now))

    def full_text(self) -> str:
        return " ".join(seg.text for seg in self._segments)

    def silence_seconds(self, now: float | None = None) -> float:
        """Seconds since the last segment (0.0 if empty)."""
        if not self._segments:
            return 0.0
        return max(0.0, (now if now is not None else self._clock()) - self._segments[-1].ts)

    def segment_count(self) -> int:
        return len(self._segments)

    def clear(self) -> None:
        self._segments.clear()
