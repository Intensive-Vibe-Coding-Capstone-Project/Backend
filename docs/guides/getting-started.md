# Getting Started Guide

> **Project:** AI-Powered Presentation Assistant
> **Prerequisites:** Python 3.10+, Node.js 18+, Git

## Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/Intensive-Vibe-Coding-Capstone-Project/Backend.git
cd Backend
```

### 2. Set Up Python Environment
```bash
# Install Python 3.12 (if not already installed)
brew install python@3.12

# Create and activate virtual environment
/usr/local/bin/python3.12 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment Variables
```bash
cp .env.example .env
# Edit .env with your API keys:
# - GOOGLE_API_KEY=your_gemini_api_key
# - FIREBASE_PROJECT_ID=your_firebase_project
```

### 4. Get a Gemini API Key
1. Visit [Google AI Studio](https://aistudio.google.com/apikey)
2. Click "Create API Key"
3. Copy the key to your `.env` file

> **Note:** The app works without a Gemini API key in "mock mode" — it will use placeholder responses. Set the key for real AI-powered responses.

### 5. Run the Development Server
```bash
# Start the FastAPI backend
uvicorn app.main:app --reload --port 8000
```

### 6. Access the Application
- **API Documentation (Swagger):** http://localhost:8000/docs
- **Alternative API Docs (ReDoc):** http://localhost:8000/redoc
- **Health Check:** http://localhost:8000/health
- **WebSocket:** ws://localhost:8000/ws

## Project Structure
```
Backend/
├── app/                        # Main application code
│   ├── __init__.py
│   ├── main.py                 # FastAPI entry point
│   ├── agents/                 # AI Agent definitions (Loop Engineering)
│   │   ├── __init__.py
│   │   └── orchestrator.py     # Planning → Dev → QA pipeline
│   ├── api/                    # API layer
│   │   ├── __init__.py
│   │   ├── websocket.py        # WebSocket real-time handler
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── documents.py    # Document upload/management
│   │       ├── chat.py         # Chat with RAG responses
│   │       └── voice.py        # Voice & signal detection
│   ├── core/                   # Configuration & shared deps
│   │   ├── __init__.py
│   │   └── config.py           # Settings from .env
│   ├── models/                 # Pydantic schemas
│   │   ├── __init__.py
│   │   └── schemas.py          # Request/response models
│   ├── services/               # Business logic
│   │   ├── __init__.py
│   │   ├── documents/
│   │   │   ├── __init__.py
│   │   │   └── processor.py    # Document parsing (PDF, DOCX, etc.)
│   │   ├── rag/
│   │   │   ├── __init__.py
│   │   │   └── engine.py       # RAG engine with ChromaDB
│   │   ├── signals/
│   │   │   ├── __init__.py
│   │   │   └── detector.py     # Presenter signal detection
│   │   └── voice/
│   │       └── __init__.py     # Voice processing (Day 5)
│   └── utils/
│       └── __init__.py
├── tests/                      # Test files
│   ├── unit/
│   │   ├── test_api.py         # API endpoint tests
│   │   └── test_signal_detector.py
│   └── integration/
├── docs/                       # Documentation
├── scripts/                    # Utility scripts
├── .env.example                # Environment template
├── .gitignore                  # Git ignore rules
├── requirements.txt            # Python dependencies
├── pyproject.toml              # Project configuration
└── README.md                   # Project overview
```

## Available API Endpoints

### Documents
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/documents/upload` | Upload documents (PDF, DOCX, TXT, EPUB, PPT) |
| `POST` | `/api/v1/documents/url` | Import from URL (coming soon) |
| `GET` | `/api/v1/documents/` | List all documents |
| `GET` | `/api/v1/documents/{id}` | Get document details |
| `DELETE` | `/api/v1/documents/{id}` | Delete a document |

### Chat
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/chat/` | Send message, get RAG response |
| `GET` | `/api/v1/chat/history` | List conversations |
| `GET` | `/api/v1/chat/history/{id}` | Get conversation detail |
| `DELETE` | `/api/v1/chat/history/{id}` | Delete conversation |

### Voice & Signals
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/voice/transcribe` | Transcribe audio (Day 5) |
| `POST` | `/api/v1/voice/analyze-signals` | Detect difficulty signals |

### WebSocket
| Endpoint | Events |
|----------|--------|
| `ws://localhost:8000/ws` | `chat_message`, `signal_check`, `voice_stream_*` |

## Running Tests
```bash
# Run all tests
.venv/bin/pytest tests/ -v

# Run only signal detector tests
.venv/bin/pytest tests/unit/test_signal_detector.py -v

# Run only API tests
.venv/bin/pytest tests/unit/test_api.py -v
```

## Team Workflow
1. Create feature branch: `git checkout -b feature/your-feature`
2. Make changes and test locally
3. Push and create Pull Request
4. Get code review from team member
5. Merge to main after approval
