# Tech Stack (recommended default — CONFIRM/EDIT)

> This is a sensible default given: a Google course, Kaggle submission, and this being the **backend** repo. Change anything before D1 ends and log the change in `context/decisions-log.md`.

## Product runtime ("Cue")

| Concern | Choice | Notes |
|---------|--------|-------|
| Language / framework | **Python + FastAPI** | async, great for streaming (WS/SSE), Kaggle-friendly. |
| LLM | **Google Gemini** (Flash for rescue/low-latency, Pro for hard reasoning) | it's a Google course; keep model id in config. |
| Embeddings | **Gemini text embeddings** | one vendor = simpler keys. |
| Vector store | **Chroma** (local, reproducible) — or **pgvector** if we want SQL | Chroma is easiest for Kaggle repro; revisit for deploy. |
| Doc parsing | `pypdf`, `python-docx`, `python-pptx`, `ebooklib`, `unstructured` (fallback) | one parser per type, normalize to text. |
| Speech-to-text | **Google Cloud Speech-to-Text** or **Gemini live audio** | needs streaming; spike on D8. |
| Realtime transport | **WebSocket** (FastAPI) | SSE acceptable for one-way streamed scripts. |
| Storage | SQLite (dev) → Postgres (deploy) | sessions, turns, doc metadata. |
| Config / secrets | `.env` + pydantic-settings | never commit keys; document for Kaggle. |
| Tests | `pytest` + a grounding eval harness | gate before submission. |

## Frontend (separate repo)

- Gemini-style chat UI (React/Next.js), karaoke/lyric line renderer, mic capture, live session view.

## Dev workflow (how we build it)

- **Claude Code** + Agent **Skills** (`.claude/skills/`) + this docs system.
- Loop Engineering: planner / dev / QA agents (`docs/03-agents/`).
- Optional: install Anthropic **`skill-creator`** to scaffold/validate new skills.

## Decisions still open

- [ ] Confirm Gemini model ids + region/quota.
- [ ] STT vendor (Google STT vs Gemini live) — decide D8.
- [ ] Vector store final (Chroma vs pgvector).
- [ ] Hosting for any live demo (Cloud Run / Kaggle notebook only).
