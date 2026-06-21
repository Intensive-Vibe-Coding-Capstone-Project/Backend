# Data Flow Architecture

> **Project:** AI-Powered Presentation Assistant
> **Last Updated:** 2026-06-21

## 1. Document Upload Flow

```
User uploads file(s)
    │
    ▼
POST /api/v1/documents/upload
    │
    ├─ Validate file type (PDF/DOCX/TXT/EPUB/PPT)
    │
    ├─ Save to disk (./uploads/)
    │
    ├─ Extract text content
    │    ├─ PDF → PyPDF2
    │    ├─ DOCX → python-docx
    │    ├─ TXT → direct read
    │    ├─ EPUB → ebooklib + BeautifulSoup
    │    └─ PPTX → python-pptx
    │
    ├─ Chunk text (RecursiveCharacterTextSplitter)
    │    ├─ chunk_size: 1000 chars
    │    └─ chunk_overlap: 200 chars
    │
    ├─ Generate embeddings (ChromaDB default)
    │
    └─ Store in ChromaDB collection: "presentation_docs"
         └─ metadata: {doc_id, filename, chunk_index, total_chunks}
```

## 2. Chat Query Flow (RAG Pipeline)

```
User sends message
    │
    ▼
POST /api/v1/chat/
    │
    ├─ Create/retrieve conversation
    │
    ├─ RAG Pipeline
    │    │
    │    ├─ [1] Query Analysis
    │    │    └─ Analyzes query, determines retrieval strategy
    │    │
    │    ├─ [2] Vector Retrieval (ChromaDB)
    │    │    ├─ Query ChromaDB for top-5 similar chunks
    │    │    ├─ Filter by document_ids (if specified)
    │    │    └─ Build context string (max 4000 chars)
    │    │
    │    ├─ [3] Gemini LLM Generation
    │    │    ├─ Receives: query + document context
    │    │    ├─ Generates: document-grounded answer
    │    │    └─ Formats: lyrics-style (one point per line)
    │    │
    │    └─ [4] Response Validation
    │         ├─ Checks: factual accuracy, hallucinations
    │         ├─ If OK → return response
    │         └─ If issues → regenerate (max 1 retry)
    │
    ├─ Store messages in conversation history
    │
    └─ Return ChatMessageResponse
         ├─ response (full text)
         ├─ formatted_lines (lyrics-style array)
         ├─ sources (document references)
         └─ confidence (0.0-1.0)
```

## 3. Real-Time WebSocket Flow

```
Client connects: ws://localhost:8000/ws
    │
    ├─ Server assigns client_id
    ├─ Sends: {event: "connected", client_id: "ws_abc123"}
    │
    ▼
Bidirectional communication loop:
    │
    ├─ Client → "chat_message"
    │    └─ Server streams response_chunks (lyrics lines)
    │
    ├─ Client → "signal_check" {text, pause_ms}
    │    └─ Server sends signal_detected events (if any)
    │
    ├─ Client → "voice_stream_start"
    │    ├─ Client → "voice_chunk" (audio data)
    │    ├─ Client → "voice_stream_end"
    │    └─ Server processes: STT → Signal Detection → RAG → Response
    │
    └─ Client → "ping"
         └─ Server → "pong"
```

## 4. Signal Detection Flow

```
Voice transcript / text input
    │
    ▼
Signal Detector
    │
    ├─ Keyword matching (English/Vietnamese)
    │    └─ "Hmm, that's a good question" → confidence 0.8+
    │
    ├─ Filler word density
    │    └─ >15% filler ratio → flag hesitation
    │
    ├─ Repetition analysis
    │    └─ Consecutive repeated words → hesitation signal
    │
    ├─ Pause duration
    │    └─ >10 seconds → long_pause signal
    │
    └─ Combined analysis
         ├─ needs_assistance: bool (any signal > sensitivity)
         ├─ overall_confidence: max signal confidence
         └─ signals: list of detected signals
```

## 5. Storage Architecture

```
┌─────────────────────────────────────────────┐
│              Storage Layer                   │
├─────────────────────────────────────────────┤
│                                             │
│  ChromaDB (Vector Store)                    │
│  ├─ Collection: "presentation_docs"         │
│  ├─ Embeddings: auto-generated              │
│  └─ Path: ./chroma_db/                      │
│                                             │
│  File System (Uploads)                      │
│  ├─ Path: ./uploads/                        │
│  └─ Format: {doc_id}_{filename}             │
│                                             │
│  In-Memory (MVP Phase)                      │
│  ├─ Documents registry                      │
│  ├─ Conversations                           │
│  └─ Messages                                │
│                                             │
│  Firebase (Production - Day 8+)             │
│  ├─ Authentication                          │
│  ├─ Firestore: conversations, user prefs    │
│  └─ Cloud Storage: document files           │
│                                             │
└─────────────────────────────────────────────┘
```
