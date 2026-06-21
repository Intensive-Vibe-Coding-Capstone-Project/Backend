"""
Signal detection service.
Detects when a presenter is struggling based on keywords,
pauses, hesitation patterns, and filler words.
"""

import logging
import re
from typing import Optional

from app.models.schemas import (
    SignalDetectionResult,
    SignalAnalysisResponse,
    SignalType,
    Language,
)

logger = logging.getLogger(__name__)


# ── Keyword Patterns ─────────────────────────────────────────

DIFFICULTY_KEYWORDS: dict[Language, list[str]] = {
    Language.ENGLISH: [
        "hmm, that's a good question",
        "let me check that",
        "that's an interesting question",
        "i'm not sure about that",
        "let me think about that",
        "good question",
        "i'll have to get back to you",
        "let me look into that",
        "that's a tough one",
        "i need to verify that",
        "hold on a moment",
        "let me see",
    ],
    Language.VIETNAMESE: [
        "để tôi xem lại phần đó",
        "hmm, đó là một câu hỏi hay",
        "câu hỏi hay đấy",
        "để tôi kiểm tra lại",
        "tôi không chắc lắm",
        "để tôi nghĩ đã",
        "chờ tôi một chút",
        "để tôi tìm lại",
        "câu hỏi khó đấy",
        "tôi cần xem lại",
    ],
}

FILLER_WORDS: dict[Language, list[str]] = {
    Language.ENGLISH: ["um", "uh", "uhh", "umm", "er", "ah", "like", "you know", "well"],
    Language.VIETNAMESE: ["ờ", "ừm", "à", "ơ", "thì", "kiểu", "nói chung là"],
}


class SignalDetector:
    """
    Analyzes text transcriptions to detect signals that a presenter
    is struggling and might need AI assistance.
    """

    def __init__(self, sensitivity: float = 0.7, language: Language = Language.ENGLISH):
        self.sensitivity = sensitivity
        self.language = language

    def analyze_text(self, text: str, timestamp_ms: int = 0) -> list[SignalDetectionResult]:
        """
        Analyze transcribed text for difficulty signals.
        Returns a list of detected signals.
        """
        signals: list[SignalDetectionResult] = []
        text_lower = text.lower().strip()

        # Check for keyword matches
        for keyword in DIFFICULTY_KEYWORDS.get(self.language, []):
            if keyword in text_lower:
                confidence = self._calculate_keyword_confidence(keyword, text_lower)
                if confidence >= self.sensitivity:
                    signals.append(SignalDetectionResult(
                        type=SignalType.KEYWORD_DETECTED,
                        confidence=confidence,
                        trigger=keyword,
                        timestamp_ms=timestamp_ms,
                        suggested_action="provide_answer",
                    ))

        # Check for filler word density
        filler_count = self._count_fillers(text_lower)
        if filler_count > 0:
            word_count = len(text_lower.split())
            filler_ratio = filler_count / max(word_count, 1)
            # High filler ratio suggests hesitation
            if filler_ratio > 0.15:
                signals.append(SignalDetectionResult(
                    type=SignalType.FILLER_WORDS,
                    confidence=min(filler_ratio * 3, 1.0),
                    trigger=f"{filler_count} filler words in {word_count} words",
                    timestamp_ms=timestamp_ms,
                    suggested_action="suggest_talking_points",
                ))

        # Check for repetition (sign of struggling)
        repetition_score = self._check_repetition(text_lower)
        if repetition_score > 0.3:
            signals.append(SignalDetectionResult(
                type=SignalType.HESITATION,
                confidence=repetition_score,
                trigger="Repetitive speech pattern detected",
                timestamp_ms=timestamp_ms,
                suggested_action="provide_context",
            ))

        return signals

    def analyze_pause(self, pause_duration_ms: int, timestamp_ms: int = 0) -> Optional[SignalDetectionResult]:
        """
        Analyze a silence/pause duration.
        Returns a signal if the pause is long enough.
        """
        # Threshold: pauses longer than 10 seconds indicate difficulty
        pause_threshold_ms = 10_000  # 10 seconds
        if pause_duration_ms >= pause_threshold_ms:
            # Confidence increases with longer pauses, capped at 1.0
            confidence = min(pause_duration_ms / 20_000, 1.0)
            return SignalDetectionResult(
                type=SignalType.LONG_PAUSE,
                confidence=confidence,
                trigger=f"Pause of {pause_duration_ms / 1000:.1f} seconds",
                timestamp_ms=timestamp_ms,
                suggested_action="provide_answer",
            )
        return None

    def full_analysis(
        self,
        text: str,
        pause_duration_ms: int = 0,
        timestamp_ms: int = 0,
    ) -> SignalAnalysisResponse:
        """
        Perform a complete analysis of text and pause data.
        Returns a comprehensive signal analysis response.
        """
        signals = self.analyze_text(text, timestamp_ms)

        if pause_duration_ms > 0:
            pause_signal = self.analyze_pause(pause_duration_ms, timestamp_ms)
            if pause_signal:
                signals.append(pause_signal)

        # Determine if assistance is needed
        needs_assistance = any(s.confidence >= self.sensitivity for s in signals)
        overall_confidence = max((s.confidence for s in signals), default=0.0)

        return SignalAnalysisResponse(
            signals=signals,
            needs_assistance=needs_assistance,
            overall_confidence=overall_confidence,
        )

    def _calculate_keyword_confidence(self, keyword: str, text: str) -> float:
        """Calculate confidence based on keyword match quality."""
        # Exact phrase match gets higher confidence
        if keyword == text.strip():
            return 0.95
        # Keyword at the start of the text
        if text.startswith(keyword):
            return 0.9
        # Keyword somewhere in the text
        return 0.8

    def _count_fillers(self, text: str) -> int:
        """Count filler words in the text."""
        count = 0
        fillers = FILLER_WORDS.get(self.language, [])
        words = text.split()
        for word in words:
            if word in fillers:
                count += 1
        return count

    def _check_repetition(self, text: str) -> float:
        """
        Check for word/phrase repetition that indicates struggling.
        Returns a repetition score between 0 and 1.
        """
        words = text.split()
        if len(words) < 4:
            return 0.0

        # Check for consecutive repeated words
        repeats = 0
        for i in range(1, len(words)):
            if words[i] == words[i - 1]:
                repeats += 1

        return min(repeats / len(words) * 5, 1.0)

    def set_language(self, language: Language):
        """Update the detection language."""
        self.language = language

    def set_sensitivity(self, sensitivity: float):
        """Update the detection sensitivity (0.0 to 1.0)."""
        self.sensitivity = max(0.0, min(1.0, sensitivity))


# Singleton instance with default settings
signal_detector = SignalDetector()
