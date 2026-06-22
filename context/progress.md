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
- **D3 ✅ Chunk + embed + store (dev done)** — `rag/` module: boundary-aware `chunking`, `Embedder` protocol with `GeminiEmbedder` (live) + deterministic `FakeEmbedder` (offline) + `get_embedder()` factory, Chroma `VectorStore` (cosine, citations `doc_id:chunk_index`), `index.index_document/query`. `POST /documents` now parses → chunks → embeds → indexes; `GET /documents` reads the store with `n_chunks`. In-memory registry retired.
- **D3 ✅ Verified** — `.[rag]` (chromadb 1.5.9 + google-genai 2.9.0) installs clean on **Python 3.14** (watch-item closed). `pytest` **24/24** keyless (fake embedder, temp Chroma per test). **Live smoke passed**: real `gemini-embedding-001` (3072-dim) → Chroma → ranked retrieval. Gemini key valid (works with `AQ.` format).
- **D4 ✅ Rescue endpoint (dev done)** — `rescue/` module: prompt v1 (`docs/02-engineering/rescue-prompt.md`), `Generator` protocol with `GeminiGenerator` (gemini-2.5-flash, temp 0.3) + offline `FakeGenerator` + factory, orchestrator with two-layer grounding (retrieval threshold → hard bridge; prompt rule → soft refusal), `POST /rescue` → script + lines + citations. Seeded `tests/eval/grounding.jsonl` (5 cases).
- **D4 ✅ Verified** — `pytest` **29/29** keyless (fake generator+embedder; grounding seed gate passes). **Live smoke passed**: supported Q → grounded line-by-line script + citation (score 0.68); unsupported Q → graceful refusal, no hallucination. Fixed a latent D1 bug: validation-error handler now runs `exc.errors()` through `jsonable_encoder`.

## In progress
- D4 → hand off to `/qa-review` (latency + grounding eval).
- D1 wrap-up: optional — fill team roles in roadmap.

## Next (per roadmap)
- D5: session model + persist Q→script turns; `GET /sessions/{id}`; lyric-line formatting refinement.

## Watch / tune
- `rescue_min_score=0.25` is lenient for single-doc corpora with Gemini embeddings (off-topic still scored >0.25 in smoke). Tune in D6 grounding eval; consider refusal detection so grounded=False is reported when the model bridges.

## Blockers / open questions
- STT vendor (decide D8) and demo hosting still open — not blocking Week 1.
- Team roles to fill in roadmap.
- Note: deps install fine on local Python 3.14; CI pins 3.11/3.12. Watch for chromadb/google-genai 3.14 wheel issues when installing `.[rag]` on D3.

## Last updated
2026-06-22 — by: D4 dev (rescue endpoint)
