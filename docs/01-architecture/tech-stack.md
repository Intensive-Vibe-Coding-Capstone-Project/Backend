# Tech Stack (recommended default — CONFIRM/EDIT)

> This is a sensible default given: a Google course, Kaggle submission, and this being the **backend** repo. Change anything before D1 ends and log the change in `context/decisions-log.md`.

## Product runtime ("Cue")

| Concern | Choice | Notes |
|---------|--------|-------|
| Language / framework | **Python ≥3.11 + FastAPI** | async, great for streaming (WS/SSE), Kaggle-friendly. Dev on local 3.14; CI pins 3.11/3.12. |
| LLM | **Google Gemini** via `google-genai` SDK — rescue=`gemini-2.5-flash`, reasoning=`gemini-2.5-pro` | it's a Google course; model ids live in `config.py`. |
| Embeddings | **`gemini-embedding-001`** | one vendor = simpler keys. |
| Vector store | **Chroma** ✅ (local persistent, reproducible) | Confirmed D1. Revisit pgvector only at deploy. |
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

## Decisions resolved (D1, 2026-06-22)

- [x] Gemini model ids — rescue=`gemini-2.5-flash`, reasoning=`gemini-2.5-pro`, embeddings=`gemini-embedding-001` (SDK `google-genai`). Region/quota: use API key default; confirm quota when first calling D3.
- [x] Vector store — **Chroma** (local persistent at `./.chroma`).
- [x] Python — **≥3.11** (dev 3.14, CI 3.11/3.12).

- [x] STT (D8) — **defer audio; MVP ingests transcript text over `WS /stream`.** Audio STT (Gemini live / Google STT) is stretch (D11).

## Decisions still open

- [ ] Hosting for any live demo (Cloud Run / Kaggle notebook only).
