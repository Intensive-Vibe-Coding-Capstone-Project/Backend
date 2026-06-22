# Active Tasks (the loop's worklist)

> Planner fills this; Dev/QA work it; clear done items to progress.md.

## Recently done (details in progress.md)
- [x] D2 — Document ingestion: `POST/GET /documents`, 5 parsers → normalized text.
- [x] D3 — Chunk + embed + store: `rag/` (chunking, embeddings, Chroma store, index); uploads indexed; live Gemini verified. pytest 24/24.
- [x] D4 — RAG retrieval + generation: `POST /rescue` → grounded Gemini Flash script + citations; offline fake generator; prompt v1 doc; grounding eval seed. pytest 29/29; live smoke passed.
- [x] D5 — Sessions + history + lyric formatting: sqlite3 store, `POST/GET /sessions`, `session_id` on `/rescue` records turns, `to_lyric_lines`; generation failures degrade to bridge. pytest 36/36; live full-stack smoke + persistence verified.
- [x] D6 — QA + harden: eval → 13 Q/A + `run_eval.py`; refusal detection (primary grounding guard) + score floor 0.4 + output cap + retry-on-503. pytest 37/37. Verdict CONDITIONAL PASS (offline gate green; live eval blocked by Gemini outage; latency over budget → streaming).

## D6 follow-ups (before submission)
- [ ] Re-run live `tests/eval/run_eval.py` in a healthy-API window → record real grounding rate (target ≥90%) — owner.
- [ ] Latency: stream tokens to cut perceived time vs ~4s budget — owner — tackle with D8+ streaming.

- [x] D7 — Frontend integration (text path): static demo UI served at `/ui` (upload → session → ask → lyric render + citations + history). pytest 40/40; HTTP smoke passed. **Pending: tag `v0.1-text`.**

## Week 2 (next up)
- [ ] D8 — Streaming transcript ingest: STT + `WS /stream` or SSE + rolling per-session transcript buffer.
- [ ] D9 — Trigger engine: manual button + periodic 30s scan → `/rescue` on the transcript window.

## Format
`- [ ] <task> — owner — acceptance criteria`
