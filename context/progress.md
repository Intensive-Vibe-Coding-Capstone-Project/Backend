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
- **D5 ✅ Sessions + history + lyric formatting (dev done)** — `sessions/` module: stdlib sqlite3 store (sessions + turns), models, service; `POST /sessions`, `GET /sessions/{id}` (404 if absent), `GET /sessions`. `POST /rescue` takes optional `session_id` → records the turn (unknown session → 404). `rescue/formatting.to_lyric_lines` wraps scripts to ≤`lyric_max_chars` (42). **Robustness:** generation failures (e.g. transient Gemini 503) degrade to the safe bridge line instead of 500.
- **D5 ✅ Verified** — `pytest` **36/36** keyless (temp sqlite per test). **Live full-stack smoke passed**: create session → real Gemini rescue w/ `session_id` → history shows the turn (lyric lines + citations) → **persists across a fresh store instance**. (Hit a transient Gemini 503 first; retry succeeded — now handled gracefully.)
- **D6 ✅ QA + harden (dev done)** — grounding eval expanded to **13 Q/A** + reusable `tests/eval/run_eval.py` (accuracy + latency, exits non-zero <90%). Hardening: **refusal detection** (model "I don't have…" → grounded=False) is now the primary grounding guard; `rescue_min_score` demoted to a 0.4 floor (Gemini embeddings are anisotropic — even nonsense ~0.6 on short text); `max_output_tokens` cap; **retry-on-503** (3 attempts) + existing graceful bridge; fake embedder now tokenizes on word chars. `pytest` **37/37** keyless.

## QA verdict (D6) — CONDITIONAL PASS
- **Offline grounding gate: PASS** — deterministic 13-case eval classifies correctly (fake embedder, threshold 0.3); 37/37 tests; ruff clean. This is the reproducible CI gate.
- **Live grounding eval: BLOCKED by a sustained Gemini Flash 503 outage** during D6. Healthy-API run earlier showed on-topic grounding working (the misses were the now-fixed threshold/refusal issues; refusal detection verified fixing off-topic). **Re-run `run_eval.py` in a healthy window before submission (D12/D13).**
- **Latency: OVER budget** — healthy rescues ~5–8s vs ~4s (PRD §8). Mitigation = token streaming (deferred to D8+ streaming work); output capped. Degraded/bridge path is <4s.
- **Edge cases:** empty store → bridge ✓; unsupported type → 415 ✓; empty/oversized → 422/413 ✓; missing session → 404 ✓; transient 503 → retry then graceful bridge ✓.
- **Robustness:** the rescue path never hard-fails (retry + bridge + refusal detection).

- **D7 ✅ Frontend integration — text path (dev done)** — single static demo page (`frontend/index.html`) served by FastAPI at `/ui` (`/` redirects); exercises upload → start session → ask → karaoke lyric-line render + grounded badge + citations + history. Mounted at `/ui` (not `/`) so the API `{error,detail}` 404 envelope is preserved. `pytest` **40/40**. **HTTP smoke passed**: `/`, `/ui/`, `/health`, upload, session, rescue, history all work over the network (rescue returned a graceful bridge — Gemini still in its 503 window).

## Week 1 ✅ — text path works end to end (upload → index → ask-in-session → grounded lyric script + citations + history), demoable in the browser. Tagged **`v0.1-text`**.

- **D8 ✅ Streaming transcript ingest (dev done)** — `transcript/` module: `TranscriptBuffer` (rolling, timestamped, `window(s)` + `silence_seconds`, injectable clock), per-session `service` (validate session, append, window, silence), and `WS /stream/{session_id}` that ingests transcript text and acks `{segments, window_chars, silence_s}` (rejects unknown session with close 4404). **STT decision:** MVP = transcript text over WS; audio STT is stretch (D11). `pytest` **46/46** keyless (TestClient WS).
- **D9 ✅ Trigger engine (dev done)** — `triggers/engine.py`: `fire(session_id, mode)` — **manual** (rescue on the current window now) + **periodic** (gated by `should_fire`: min-chars + dedup vs last fire, and ungrounded bridges suppressed so the 30s auto-scan stays quiet). Records the turn on every fire. WS protocol extended: `{type:"trigger"}` → push `{type:"rescue", mode, ...}`; per-connection periodic asyncio scan task; sends serialized with a lock; the LLM call runs via `asyncio.to_thread` (doesn't block the event loop). `pytest` **52/52** keyless.

## In progress
- D6 follow-ups before submit: re-run live `run_eval.py` for a real grounding rate; address latency via streaming.
- D1 wrap-up: optional — fill team roles in roadmap.

## Next (per roadmap)
- **D10: Slip / flow detection** — diff the spoken transcript window vs the prepared script → detect divergence (wrong brand / off-flow) → correction script (PRD use cases 3 & 4).

## Blockers / open questions
- STT vendor (decide D8) and demo hosting still open — not blocking Week 1.
- Team roles to fill in roadmap.
- Note: deps install fine on local Python 3.14; CI pins 3.11/3.12. Watch for chromadb/google-genai 3.14 wheel issues when installing `.[rag]` on D3.

## Last updated
2026-06-22 — by: D9 trigger engine (manual + periodic scan over WS)
