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

- **D2 ✅ Document ingestion (dev done, pending QA)** — `ingestion/` module (models, errors, parser registry for pdf/docx/txt/pptx/epub → normalized text, service with in-memory registry) + `POST /documents` & `GET /documents` wired into the app. Domain errors map to 415/413/422 via the `{error,detail}` envelope. Embedding/store deferred to D3.
- **D2 ✅ Tests green** — `pytest` **19/19** (per-parser extraction on runtime-generated samples, normalization, service registry, size/empty guards, endpoint happy-path + 415/422). `ruff` + `format` clean. CI now installs `.[dev,parsers]`.

## In progress
- D2 → hand off to `/qa-review` (grounding N/A this step; check latency + error handling).
- D1 wrap-up: optional — fill team roles in roadmap.

## Next (per roadmap)
- D3: chunk/embed/store — Gemini embeddings → Chroma; replace in-memory registry (keep ingest/get/list shape). Install `.[rag]`.
- D4: `POST /rescue` (text) → retrieve → Gemini → grounded script.

## Blockers / open questions
- STT vendor (decide D8) and demo hosting still open — not blocking Week 1.
- Team roles to fill in roadmap.
- Note: deps install fine on local Python 3.14; CI pins 3.11/3.12. Watch for chromadb/google-genai 3.14 wheel issues when installing `.[rag]` on D3.

## Last updated
2026-06-22 — by: D2 dev (document ingestion)
