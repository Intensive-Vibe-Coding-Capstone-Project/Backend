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
- **D10 ✅ Slip / flow detection (dev done)** — prepared script bound per session (`PUT /sessions/{id}/script`, sqlite columns + migration). `triggers/slip.py`: **lexical** detection (provider-independent) — `detect_brand_slip` (forbidden term as a whole word) + `detect_off_flow` (spoken/script word-overlap < `slip_min_overlap`); `check()` builds a correction grounded in the prepared script (generator + templated fallback). WS: `{type:"check_slip"}` → push `{type:"correction", kind, wrong_terms, lines}`; also run in the periodic scan. `pytest` **60/60** keyless.

## ✅ All 4 PRD use cases covered — #1/#2 hard question (`/rescue`), #3 live-sale brand slip + #4 recording flow break (slip detection).

- **D11 ✅ Stretch triggers + UX polish (dev done)** — `triggers/engine.py`: **keyword + silence auto-triggers**. `matched_keyword` (urgent phrases from `trigger_keywords` config) + `auto_reason(session_id)` picks **keyword > silence > periodic**; keyword/silence relax the `trigger_min_chars` gate while all auto modes still dedup on an unchanged window and suppress ungrounded bridges. `auto_fire()` runs one scan and returns `(response, mode)`; WS auto-scan now surfaces the real mode. **UI polish** (`frontend/index.html`): new panels for a **prepared script** (`PUT /sessions/{id}/script` → enables slip alerts) and a **live transcript over WS** (connect, type lines, "Rescue now" / "Check slip", live karaoke render with mode/`grounded`/slip badges + event log). `pytest` **66/66** keyless; ruff clean.

- **D12 ⚠️ QA + eval pass — verdict FAIL vs grounding target (2026-06-24)** — Full `qa-review` over D2–D11. **Tests:** `pytest` **66/66** keyless, ruff check + format clean. **Edge cases / envelope:** 415 / 422 / 413 (oversized→`FileTooLargeError`) / 404 (`{error,detail}`), WS unknown session close 4404, unsupported question + generation failure → graceful bridge — all verified. **Live grounding eval finally ran clean** (throttled ~14s/case to beat the real free-tier limit, which is **5 req/min**, not 20/day): **11/13 = 85% — UNDER the ≥90% target.** All 10 on-topic cases ground correctly (10/10); off-topic refusal **leaked on 2/3** — `off1` ("banana umbrella…") and `off3` ("recipe chocolate cake…") returned grounded scripts for nonsense, only `off2` refused. **Latency (live):** p50 **4.08s** (≈budget), p95/max **7.60s** (over ~4s). Root cause = the D6-flagged risk, now confirmed live: anisotropic embeddings let all 3 off-topic Qs clear the 0.4 `rescue_min_score` floor → LLM called, and refusal detection (primary guard) caught only 1/3. Offline deterministic gate stays green (CI signal).

- **D13 ✅ Kaggle submission writeup assembled (2026-06-24)** — filled `docs/04-delivery/kaggle-submission.md` from artifacts (PRD, system-design, demo-script, D12 eval): problem/users, 4 use cases, architecture + Loop-Engineering diagrams, AI-agent design, reproducibility (pinned deps, `GEMINI_API_KEY`→Kaggle Secrets, model ids, keyless fakes), and an **honest §8 results** section (offline 66/66 + 13/13 classify; live **85%** with the off-topic leak + p95 7.6s disclosed, not hidden). README Status refreshed to the real built state. **Remaining manual gaps (user):** record the demo video, package the Kaggle notebook (or link the repo + run steps), and the actual Submit. **Blocking a clean ≥90% submit:** the D12 grounding fix is still open.

- **Demo enablement ✅ Voice input (2026-06-24)** — added a 🎤 Speak button to the live panel (`frontend/index.html`) using the browser **Web Speech API**: recognized phrases stream into the existing `WS /stream` text ingest (interim preview in the box, final phrases auto-sent). Frontend-only, no key/cost, Chrome/Edge. Added a fictional **AuroraBuds Pro** demo kit (`samples/aurorabuds/`: 3 docs + prepared script + RUNBOOK) and a `Youtube_demo.md` recording guide. `test_ui` green.

- **Submission ✅ Video recorded + Kaggle notebook assembled (2026-07-01)** — demo video published (https://youtu.be/9WT2cFZ4iuA) and linked in `kaggle-submission.md` §6 + checklist. Built the runnable Kaggle notebook `cue-5-day-ai-agents-intensive-vibe-coding-cours.ipynb`: story + architecture/loop diagrams, then a **keyless deterministic** demo (`pip install "cue[rag] @ git+…"` → set `CUE_*_PROVIDER=fake` + `CUE_RESCUE_MIN_SCORE=0.3` → index an inline AuroraBuds FAQ → on-topic **grounds** w/ citations, off-topic **bridges**), an honest §results (offline 66/66 + 13/13; live 85% + p95 7.6s), and an optional live-Gemini cell (reads a `GEMINI_API_KEY` Kaggle Secret, skips cleanly if absent). Cells verified against the venv (on-topic score 0.576, off-topic grounded=False). **Remaining manual: import notebook to Kaggle → Save & Run All (public) → each teammate submits a Writeup.** Grounding fix still open (submit at 85% honest OR land the fix for ≥90%).

## In progress
- **D12 follow-up (gates a clean submit):** fix off-topic over-grounding → live grounding ≥90% (strengthen refusal prompt / add post-gen relevance check; min_score tuning is delicate). Latency via token streaming vs p95 7.6s.
- **D13 manual steps:** demo video, Kaggle notebook packaging, final Submit — owner.
- D1 wrap-up: optional — fill team roles in roadmap.

## Next (per roadmap)
- Land the D12 grounding fix → re-run live eval (≥90%) → finalize the writeup checklist → **Submit**. Then D14 buffer/retro.

## Blockers / open questions
- STT vendor (decide D8) and demo hosting still open — not blocking Week 1.
- Team roles to fill in roadmap.
- Note: deps install fine on local Python 3.14; CI pins 3.11/3.12. Watch for chromadb/google-genai 3.14 wheel issues when installing `.[rag]` on D3.

## Last updated
2026-06-24 — by: D13 Kaggle writeup assembled (honest eval: live 85%, offline green) + README polish. Manual gaps: video, notebook, Submit; grounding fix still gates a clean ≥90% submit.
