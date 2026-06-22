# Progress (living state — update every session)

> Single source of "where we are right now". Newest at top.

## Current phase
Week 1 / Setup (Day 1, Mon 22 Jun 2026).

## Done
- Repo init; meeting minute captured.
- Context-engineering docs system + starter skills scaffolded.
- **D1 ✅ Tech stack confirmed** — Chroma vector store, Gemini ids (flash/pro/`gemini-embedding-001`, `google-genai` SDK), Python ≥3.11. Logged in decisions-log + tech-stack.
- **D1 ✅ FastAPI skeleton** — `src/cue/` package (api app factory + `/health`, `config.py` via pydantic-settings, error envelope, feature-module stubs), `pyproject.toml` (deps + ruff + pytest), `.env.example`, `.gitignore`.
- **D1 ✅ Toolchain verified** — venv (py 3.14), `pip install -e ".[dev]"`, `ruff check`/`format --check` clean, **4/4 pytest green**. CI stub at `.github/workflows/ci.yml` (3.11/3.12).

## In progress
- D1 wrap-up: optional — fill team roles in roadmap.

## Next (per roadmap)
- D2: document ingestion `POST /documents` + parsers (pdf/docx/txt/pptx/epub) → normalized text + unit tests. Install `.[parsers]`.
- D3: chunk/embed/store (Gemini embeddings → Chroma). Install `.[rag]`.

## Blockers / open questions
- STT vendor (decide D8) and demo hosting still open — not blocking Week 1.
- Team roles to fill in roadmap.
- Note: deps install fine on local Python 3.14; CI pins 3.11/3.12. Watch for chromadb/google-genai 3.14 wheel issues when installing `.[rag]` on D3.

## Last updated
2026-06-22 — by: D1 dev (FastAPI skeleton)
