"""
Pydantic models (schemas) for API request/response validation.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, UTC
from enum import Enum


# ── Enums ────────────────────────────────────────────────────


class DocumentType(str, Enum):
    PDF = "pdf"
    DOCX = "docx"
    TXT = "txt"
    EPUB = "epub"
    PPT = "ppt"
    PPTX = "pptx"


class DocumentStatus(str, Enum):
    UPLOADING = "uploading"
    PROCESSING = "processing"
    READY = "ready"
    ERROR = "error"


class URLSourceType(str, Enum):
    GOOGLE_DRIVE = "google_drive"
    YOUTUBE = "youtube"
    WEBSITE = "website"


class Language(str, Enum):
    ENGLISH = "en"
    VIETNAMESE = "vi"


class SignalType(str, Enum):
    HESITATION = "hesitation"
    LONG_PAUSE = "long_pause"
    KEYWORD_DETECTED = "keyword_detected"
    FILLER_WORDS = "filler_words"
    WRONG_INFO = "wrong_info"


# ── Document Schemas ─────────────────────────────────────────


class DocumentResponse(BaseModel):
    """Response after uploading a document."""
    id: str
    filename: str
    type: DocumentType
    size_bytes: int
    chunk_count: int = 0
    status: DocumentStatus = DocumentStatus.PROCESSING
    uploaded_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class DocumentUploadResponse(BaseModel):
    """Response for batch document upload."""
    document_ids: list[str]
    status: str = "processing"
    message: str


class URLImportRequest(BaseModel):
    """Request to import a document from a URL."""
    url: str
    type: URLSourceType = URLSourceType.WEBSITE


# ── Chat Schemas ─────────────────────────────────────────────


class ChatMessageRequest(BaseModel):
    """Incoming chat message from the user."""
    message: str
    conversation_id: Optional[str] = None
    document_ids: Optional[list[str]] = None


class SourceReference(BaseModel):
    """A reference to a source document chunk."""
    document: str
    page: Optional[int] = None
    chunk_id: str = ""
    relevance: float = 0.0
    text_preview: str = ""


class ChatMessageResponse(BaseModel):
    """AI-generated response to a chat message."""
    response: str
    sources: list[SourceReference] = []
    conversation_id: str
    confidence: float = 0.0
    formatted_lines: list[str] = []  # lyrics-style line-by-line


# ── Conversation Schemas ─────────────────────────────────────


class ConversationSummary(BaseModel):
    """Summary of a conversation for the history list."""
    id: str
    title: str
    message_count: int = 0
    document_ids: list[str] = []
    created_at: datetime
    updated_at: datetime


class MessageRecord(BaseModel):
    """A single message in a conversation."""
    id: str
    role: str  # "user" or "assistant"
    content: str
    sources: list[SourceReference] = []
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))


class ConversationDetail(BaseModel):
    """Full conversation with all messages."""
    id: str
    title: str
    messages: list[MessageRecord] = []
    document_ids: list[str] = []
    created_at: datetime
    updated_at: datetime


# ── Voice Schemas ────────────────────────────────────────────


class TranscriptionResponse(BaseModel):
    """Response from voice transcription."""
    text: str
    language: Language
    confidence: float
    duration_ms: int


class SignalDetectionResult(BaseModel):
    """A detected difficulty signal."""
    type: SignalType
    confidence: float
    trigger: str  # the phrase or event that triggered detection
    timestamp_ms: int
    suggested_action: str = "provide_answer"


class SignalAnalysisResponse(BaseModel):
    """Response from signal analysis."""
    signals: list[SignalDetectionResult]
    needs_assistance: bool = False
    overall_confidence: float = 0.0


# ── Settings Schemas ─────────────────────────────────────────


class UserSettings(BaseModel):
    """User preferences."""
    language: Language = Language.ENGLISH
    signal_sensitivity: float = Field(default=0.7, ge=0.0, le=1.0)
    auto_detect_signals: bool = True
    voice_enabled: bool = True


# ── Health Check ─────────────────────────────────────────────


class HealthCheckResponse(BaseModel):
    """Health check response."""
    status: str = "healthy"
    version: str
    environment: str
    services: dict[str, str] = {}
