# Multi-Agent Architecture

> **Project:** AI-Powered Presentation Assistant
> **Pattern:** Loop Engineering (Planning → QA → Dev)

## Overview

This project follows two distinct architectural concepts:

1. **Development Methodology** — Loop Engineering with 3 AI Agents used to *build* the website
2. **Runtime Architecture** — The actual application pipeline that serves user requests

These are separate concerns and should not be confused.

---

## Part 1: Development Methodology — Loop Engineering

The website is **developed** using a Loop Engineering approach with 3 specialized AI Agents. These agents assist the development team during the coding process — they do **NOT** run as part of the deployed application.

```
┌─────────────────────────────────────────────────┐
│            Loop Engineering Cycle                │
│         (Development Process Only)               │
└─────────────────────┬───────────────────────────┘
                      │
         ┌────────────▼────────────┐
         │    Planning Agent       │
         │  (Analyzes requirements,│
         │   designs architecture, │
         │   plans sprints)        │
         └────────────┬────────────┘
                      │
         ┌────────────▼────────────┐
         │      Dev Agent          │
         │  (Writes code,          │
         │   implements features,  │
         │   builds the system)    │
         └────────────┬────────────┘
                      │
         ┌────────────▼────────────┐
         │      QA Agent           │
         │  (Tests code quality,   │
         │   reviews output,       │
         │   validates correctness)│
         └────────────┬────────────┘
                      │
                      ▼
              ┌───────────────┐
              │  Feedback Loop│──► Back to Planning
              │  (if issues)  │    Agent for next
              └───────────────┘    iteration
```

### Planning Agent (Development)
**Role:** Project Architect & Sprint Planner

**What it does during development:**
- Analyze project requirements from meeting minutes
- Design system architecture and data flows
- Break down features into implementable tasks
- Plan sprint schedules and priorities
- Create documentation structure

### Dev Agent (Development)
**Role:** Code Implementation

**What it does during development:**
- Write application code (FastAPI, services, models)
- Implement features based on the Planning Agent's design
- Create database schemas and API endpoints
- Build frontend components
- Write configuration files

### QA Agent (Development)
**Role:** Quality Assurance & Code Review

**What it does during development:**
- Review generated code for correctness
- Write and run unit/integration tests
- Validate API responses against specifications
- Check for bugs, edge cases, and security issues
- Request re-implementation if quality threshold not met

> [!IMPORTANT]
> These 3 agents are the **development tools**, not the product's features.
> They help the team build the website using an iterative loop.

---

## Part 2: Runtime Architecture — Application Pipeline

The deployed application uses a **Gemini-powered RAG pipeline** to serve user requests. This is what actually runs when users interact with the website.

```
┌──────────────────────────────────────────────────┐
│                    User Request                   │
│         (Question, Voice Input, Document)         │
└──────────────────────┬───────────────────────────┘
                       │
                       ▼
              ┌──────────────────┐
              │   FastAPI        │ ◄── REST + WebSocket
              │   API Gateway    │     Entry point
              └────────┬─────────┘
                       │
          ┌────────────┼────────────┐
          │            │            │
          ▼            ▼            ▼
   ┌────────────┐ ┌─────────┐ ┌──────────┐
   │  Document  │ │  Chat   │ │  Voice   │
   │  Upload    │ │  Query  │ │  Input   │
   └─────┬──────┘ └────┬────┘ └─────┬────┘
         │             │            │
         ▼             │            ▼
   ┌────────────┐      │     ┌──────────┐
   │  Text      │      │     │  STT     │
   │  Extraction│      │     │ (Gemini) │
   └─────┬──────┘      │     └─────┬────┘
         │             │           │
         ▼             │           ▼
   ┌────────────┐      │     ┌──────────┐
   │  Chunking  │      │     │  Signal  │
   │  + Embed   │      │     │ Detector │
   └─────┬──────┘      │     └─────┬────┘
         │             │           │
         ▼             ▼           ▼
   ┌─────────────────────────────────────┐
   │         RAG Engine (ChromaDB)        │
   │  ┌─────────────────────────────┐    │
   │  │  1. Query vector store      │    │
   │  │  2. Retrieve relevant chunks│    │
   │  │  3. Build context           │    │
   │  │  4. Generate answer (Gemini)│    │
   │  │  5. Format as lyrics-style  │    │
   │  └─────────────────────────────┘    │
   └──────────────────┬──────────────────┘
                      │
                      ▼
              ┌──────────────────┐
              │   User Response  │
              │  (Lyrics format) │
              │  + Source refs   │
              │  + Confidence    │
              └──────────────────┘
```

### Application Components

| Component | Technology | Purpose |
|-----------|-----------|---------|
| API Gateway | FastAPI | REST + WebSocket entry point |
| Document Processor | PyPDF2, python-docx, etc. | Extract text from uploaded files |
| RAG Engine | ChromaDB + Gemini | Vector search + LLM answer generation |
| Signal Detector | Pattern matching + AI | Detect presenter difficulty signals |
| Voice Pipeline | Gemini STT | Convert speech to text |

### Processing Flow for Chat Queries

```
User Question
     │
     ▼
RAG Retrieval (ChromaDB)
  → Query vector store for top-5 similar chunks
  → Filter by document_ids (if specified)
  → Build context string (max 4000 chars)
     │
     ▼
Gemini LLM Generation
  → System prompt with document context
  → Generate document-grounded answer
  → Format as lyrics-style (one point per line)
     │
     ▼
Response to User
  → Formatted lines (lyrics display)
  → Source document references
  → Confidence score (0.0–1.0)
```

---

## Relationship Between the Two

```
┌─────────────────────────────────────────────┐
│         DEVELOPMENT TIME                     │
│                                              │
│  Planning Agent ──► Dev Agent ──► QA Agent   │
│       │                               │      │
│       └──── feedback loop ◄───────────┘      │
│                    │                         │
│                    ▼                         │
│            Produces the code for:            │
└─────────────────────┬───────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────┐
│         RUNTIME (Deployed App)               │
│                                              │
│  User → API → Document Processing            │
│             → RAG Engine (ChromaDB + Gemini) │
│             → Signal Detection               │
│             → Lyrics-style Response          │
└─────────────────────────────────────────────┘
```

> The Loop Engineering agents **build** the application.
> The application itself uses a **RAG pipeline** to serve users.

---

## State Management

Using application-level state management:
- **Session State:** Current conversation context, active documents
- **User State:** Preferences, language selection, upload history
- **Application State:** ChromaDB collection stats, service health
