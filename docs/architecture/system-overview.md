# System Architecture Overview

> **Project:** AI-Powered Presentation Assistant
> **Last Updated:** 2026-06-21

## System Components

### 1. Frontend Layer
- **Technology:** Next.js + React
- **Key Pages:** Chat interface, Document upload, Settings, History
- **Real-time:** WebSocket connection for streaming responses
- **Voice:** Web Audio API for voice capture

### 2. Backend API Layer
- **Technology:** FastAPI (Python)
- **Endpoints:** REST API + WebSocket
- **Auth:** Firebase Authentication
- **Rate Limiting:** Per-user API throttling

### 3. AI Processing Layer
- **RAG Engine:** Retrieves relevant document chunks via ChromaDB, generates Gemini-powered answers
- **Signal Detector:** Identifies presenter difficulty via keywords, pauses, and hesitation patterns
- **Response Formatter:** Structures answers in lyrics-style for easy live reading

> **Note:** The project follows a *Loop Engineering* development methodology using 3 AI Agents (Planning, QA, Dev) to **build** this application. These agents are development tools, not runtime components. See [Agent Architecture](./agent-architecture.md) for details.

### 4. Core Pipeline
- **Document Processor:** Ingests PDF, DOCX, TXT, EPUB, PPT
- **RAG Engine:** Retrieval-Augmented Generation with ChromaDB
- **Signal Detector:** Identifies presenter difficulty via keywords/pauses
- **Voice Pipeline:** STT → Processing → TTS

### 5. Storage Layer
- **Vector DB:** ChromaDB (dev) → pgvector (production)
- **File Storage:** Google Cloud Storage
- **Conversations:** Firebase Firestore
- **Cache:** Redis (optional)

## Data Flow

```
User Input (Voice/Text/File)
    │
    ▼
API Gateway (FastAPI)
    │
    ├── File Upload → Document Processor → Chunking → Embeddings → Vector DB
    │
    ├── Text Chat → RAG Engine → Gemini LLM → Response
    │
    └── Voice Input → STT → Signal Detection → RAG → TTS → Voice Response
```

## Key Design Decisions

1. **ChromaDB over pgvector initially:** Faster development, embedded mode, no external DB needed
2. **FastAPI over Django/Flask:** Native async, WebSocket support, automatic OpenAPI docs
3. **Google ADK for agents:** Native Gemini integration, multi-agent orchestration
4. **Firebase for auth/storage:** Quick setup, real-time sync, free tier available
