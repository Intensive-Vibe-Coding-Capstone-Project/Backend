# API Endpoints Reference

> **Base URL:** `http://localhost:8000/api/v1`
> **WebSocket:** `ws://localhost:8000/ws`

## REST Endpoints

### Documents

#### `POST /documents/upload`
Upload one or more documents for processing.

**Request:**
- `Content-Type: multipart/form-data`
- `files`: One or more files (PDF, DOCX, TXT, EPUB, PPT)

**Response:**
```json
{
  "document_ids": ["doc_abc123", "doc_def456"],
  "status": "processing",
  "message": "2 documents uploaded and being processed"
}
```

#### `POST /documents/url`
Fetch and process a document from a URL.

**Request:**
```json
{
  "url": "https://drive.google.com/...",
  "type": "google_drive"  // google_drive | youtube | website
}
```

#### `GET /documents`
List all uploaded documents for the current user.

#### `DELETE /documents/{document_id}`
Delete a specific document and its embeddings.

---

### Chat

#### `POST /chat`
Send a text message and get a RAG-powered response.

**Request:**
```json
{
  "message": "What are the key findings from the quarterly report?",
  "conversation_id": "conv_123",  // optional, creates new if omitted
  "document_ids": ["doc_abc123"]  // optional, searches all if omitted
}
```

**Response:**
```json
{
  "response": "Based on the quarterly report...",
  "sources": [
    {"document": "Q4_Report.pdf", "page": 12, "relevance": 0.95}
  ],
  "conversation_id": "conv_123",
  "confidence": 0.92
}
```

#### `GET /chat/history`
Get conversation history.

#### `GET /chat/history/{conversation_id}`
Get messages for a specific conversation.

---

### Voice

#### `POST /voice/transcribe`
Transcribe audio to text.

**Request:**
- `Content-Type: multipart/form-data`
- `audio`: Audio file (WAV, MP3, WebM)
- `language`: `en` | `vi`

#### `POST /voice/analyze-signals`
Analyze audio for presentation difficulty signals.

---

### Settings

#### `GET /settings`
Get user preferences.

#### `PUT /settings`
Update user preferences (language, signal sensitivity, etc.).

---

## WebSocket Events

### Connection
```javascript
const ws = new WebSocket('ws://localhost:8000/ws?token=YOUR_AUTH_TOKEN');
```

### Client → Server Events

| Event | Payload | Description |
|-------|---------|-------------|
| `chat_message` | `{message, conversation_id}` | Send a chat message |
| `voice_stream_start` | `{language, mode}` | Start voice streaming |
| `voice_chunk` | `{audio_data}` | Send audio chunk (base64) |
| `voice_stream_end` | `{}` | End voice streaming |

### Server → Client Events

| Event | Payload | Description |
|-------|---------|-------------|
| `response_chunk` | `{text, is_final}` | Streaming response text |
| `signal_detected` | `{type, confidence}` | Difficulty signal detected |
| `suggestion` | `{text, sources}` | Proactive suggestion |
| `error` | `{code, message}` | Error notification |

---

## Data Schemas

### Document
```json
{
  "id": "doc_abc123",
  "filename": "presentation.pdf",
  "type": "pdf",
  "size_bytes": 1048576,
  "chunk_count": 42,
  "status": "ready",
  "uploaded_at": "2026-06-22T10:00:00Z"
}
```

### Conversation
```json
{
  "id": "conv_123",
  "title": "Q4 Report Discussion",
  "messages": [...],
  "document_ids": ["doc_abc123"],
  "created_at": "2026-06-22T10:00:00Z",
  "updated_at": "2026-06-22T11:30:00Z"
}
```

### Signal Detection
```json
{
  "type": "hesitation",
  "confidence": 0.87,
  "trigger": "Hmm, that's a good question",
  "timestamp_ms": 45230,
  "suggested_action": "provide_answer"
}
```
