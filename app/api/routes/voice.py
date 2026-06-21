"""
Voice and signal detection API routes.
Handles voice transcription and presenter difficulty signal analysis.
"""

import logging
from fastapi import APIRouter, UploadFile, File, HTTPException, Query

from app.models.schemas import (
    TranscriptionResponse,
    SignalAnalysisResponse,
    Language,
)
from app.services.signals.detector import signal_detector

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/voice", tags=["Voice"])


@router.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe_audio(
    audio: UploadFile = File(...),
    language: Language = Query(default=Language.ENGLISH),
):
    """
    Transcribe audio to text using Gemini STT.
    Supported formats: WAV, MP3, WebM
    """
    # TODO: Implement Gemini STT integration in Day 5
    # For now, return a placeholder
    raise HTTPException(
        status_code=501,
        detail="Voice transcription will be implemented in Day 5 (Voice & Signals sprint).",
    )


@router.post("/analyze-signals", response_model=SignalAnalysisResponse)
async def analyze_signals(
    text: str,
    language: Language = Query(default=Language.ENGLISH),
    pause_duration_ms: int = Query(default=0, ge=0),
    timestamp_ms: int = Query(default=0, ge=0),
):
    """
    Analyze text transcript for presentation difficulty signals.
    Detects keywords, filler words, repetition, and long pauses
    that indicate the presenter needs help.
    """
    # Update detector settings
    signal_detector.set_language(language)

    # Run full analysis
    result = signal_detector.full_analysis(
        text=text,
        pause_duration_ms=pause_duration_ms,
        timestamp_ms=timestamp_ms,
    )

    return result


@router.post("/analyze-audio-signals", response_model=SignalAnalysisResponse)
async def analyze_audio_signals(
    audio: UploadFile = File(...),
    language: Language = Query(default=Language.ENGLISH),
):
    """
    Analyze audio directly for difficulty signals.
    Combines STT with signal detection in one call.
    """
    # TODO: Implement combined audio analysis in Day 5
    raise HTTPException(
        status_code=501,
        detail="Audio signal analysis will be implemented in Day 5.",
    )
