# 🎙️ AI-Powered Presentation Assistant

> **Capstone Project** — 5-Day AI Agents: Intensive Vibe Coding Course With Google

An AI-powered website that helps users answer unexpected questions during presentations, live streams, and content creation by leveraging uploaded documents and real-time voice/text analysis.

## ✨ Features

- 📄 **Document Upload** — Support for PDF, DOCX, TXT, EPUB, PPT
- 🔗 **URL Import** — Fetch documents from Google Drive, YouTube, websites
- 💬 **Real-time Chat** — Gemini-style interface with RAG-powered responses
- 🎤 **Voice Input** — Real-time speech recognition and conversation
- 🔍 **Signal Detection** — AI detects when you're struggling during a presentation
- 📜 **Lyrics Display** — Answers displayed line-by-line like song lyrics
- 📚 **Conversation History** — Keep track of all your sessions
- 🌐 **Multilingual** — English and Vietnamese support

## 🏗️ Architecture

Developed using a **Loop Engineering** pattern with 3 AI Agents for the development process:
- **Planning Agent** — Designs architecture and plans sprints
- **Dev Agent** — Implements features and writes code
- **QA Agent** — Tests quality and validates correctness

The deployed application uses a **Gemini-powered RAG pipeline** with real-time signal detection.

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| Backend | FastAPI (Python) |
| AI Framework | Google ADK |
| LLM | Gemini 2.0 |
| Vector DB | ChromaDB |
| Database | Firebase |
| Frontend | Next.js + React |
| Deployment | Google Cloud Run |

## 🚀 Quick Start

```bash
# Clone the repo
git clone https://github.com/Intensive-Vibe-Coding-Capstone-Project/Backend.git
cd Backend

# Set up Python environment
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Add your GOOGLE_API_KEY to .env

# Run the server
uvicorn app.main:app --reload
```

## 📖 Documentation

See the [Documentation Hub](./docs/README.md) for:
- [Architecture](./docs/architecture/system-overview.md)
- [API Reference](./docs/api/rest-endpoints.md)
- [Getting Started Guide](./docs/guides/getting-started.md)
- [Installed Skills](./docs/skills/installed-skills.md)

## 📦 Skills & Resources

This project leverages the following GitHub repositories:

| Repository | Purpose |
|-----------|---------|
| [google/skills](https://github.com/google/skills) | Official Google Cloud skills |
| [antigravity-awesome-skills](https://github.com/sickn33/antigravity-awesome-skills) | 1,500+ community skills |
| [google/adk-python](https://github.com/google/adk-python) | Agent Development Kit |
| [google/adk-samples](https://github.com/google/adk-samples) | ADK sample implementations |
| [agent-starter-pack](https://github.com/GoogleCloudPlatform/agent-starter-pack) | Production templates |

## 👥 Team

Capstone group for the 5-Day AI Agents Intensive Vibe Coding Course With Google.

## 📄 License

This project is part of the Google AI Agents course capstone submission.
