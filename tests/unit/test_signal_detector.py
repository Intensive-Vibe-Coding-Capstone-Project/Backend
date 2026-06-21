"""
Tests for the signal detection service.
"""

import pytest
from app.services.signals.detector import SignalDetector, signal_detector
from app.models.schemas import SignalType, Language


class TestSignalDetector:
    """Test suite for the SignalDetector class."""

    def setup_method(self):
        """Create a fresh detector for each test."""
        self.detector = SignalDetector(sensitivity=0.7, language=Language.ENGLISH)

    # ── Keyword Detection ────────────────────────────────────

    def test_detects_english_difficulty_keyword(self):
        """Should detect known difficulty phrases in English."""
        signals = self.detector.analyze_text("Hmm, that's a good question, let me think")
        assert len(signals) > 0
        keyword_signals = [s for s in signals if s.type == SignalType.KEYWORD_DETECTED]
        assert len(keyword_signals) > 0

    def test_detects_vietnamese_difficulty_keyword(self):
        """Should detect known difficulty phrases in Vietnamese."""
        self.detector.set_language(Language.VIETNAMESE)
        signals = self.detector.analyze_text("Để tôi xem lại phần đó")
        keyword_signals = [s for s in signals if s.type == SignalType.KEYWORD_DETECTED]
        assert len(keyword_signals) > 0

    def test_no_false_positive_on_normal_speech(self):
        """Should not detect signals in normal speech."""
        signals = self.detector.analyze_text(
            "The quarterly revenue grew by 15 percent year over year"
        )
        keyword_signals = [s for s in signals if s.type == SignalType.KEYWORD_DETECTED]
        assert len(keyword_signals) == 0

    # ── Filler Word Detection ────────────────────────────────

    def test_detects_high_filler_ratio(self):
        """Should detect excessive filler words."""
        signals = self.detector.analyze_text("um uh well um like you know um")
        filler_signals = [s for s in signals if s.type == SignalType.FILLER_WORDS]
        assert len(filler_signals) > 0

    def test_ignores_low_filler_ratio(self):
        """Should not flag text with few filler words."""
        signals = self.detector.analyze_text(
            "The revenue was strong this quarter um reaching new highs across all segments"
        )
        filler_signals = [s for s in signals if s.type == SignalType.FILLER_WORDS]
        assert len(filler_signals) == 0

    # ── Pause Detection ──────────────────────────────────────

    def test_detects_long_pause(self):
        """Should detect pauses longer than 10 seconds."""
        signal = self.detector.analyze_pause(12000)  # 12 seconds
        assert signal is not None
        assert signal.type == SignalType.LONG_PAUSE
        assert signal.confidence > 0

    def test_ignores_short_pause(self):
        """Should not flag short pauses."""
        signal = self.detector.analyze_pause(5000)  # 5 seconds
        assert signal is None

    # ── Full Analysis ────────────────────────────────────────

    def test_full_analysis_combines_signals(self):
        """Full analysis should combine text and pause signals."""
        result = self.detector.full_analysis(
            text="Hmm, that's a good question",
            pause_duration_ms=15000,
        )
        assert result.needs_assistance is True
        assert result.overall_confidence > 0
        assert len(result.signals) >= 1

    def test_full_analysis_no_assistance_needed(self):
        """Full analysis should report no assistance for normal speech."""
        result = self.detector.full_analysis(
            text="Our Q4 results show strong growth",
            pause_duration_ms=2000,
        )
        assert result.needs_assistance is False

    # ── Configuration ────────────────────────────────────────

    def test_sensitivity_adjustment(self):
        """Higher sensitivity should detect more signals."""
        self.detector.set_sensitivity(0.1)
        low_sens_signals = self.detector.analyze_text("Hmm, that's a good question")

        self.detector.set_sensitivity(0.99)
        high_sens_signals = self.detector.analyze_text("Hmm, that's a good question")

        # Lower sensitivity threshold → more signals pass through
        assert len(low_sens_signals) >= len(high_sens_signals)

    def test_language_switching(self):
        """Should correctly switch between languages."""
        self.detector.set_language(Language.VIETNAMESE)
        assert self.detector.language == Language.VIETNAMESE

        self.detector.set_language(Language.ENGLISH)
        assert self.detector.language == Language.ENGLISH


class TestSignalDetectorSingleton:
    """Test the singleton instance."""

    def test_singleton_exists(self):
        """The singleton signal_detector should be importable."""
        assert signal_detector is not None
        assert isinstance(signal_detector, SignalDetector)
