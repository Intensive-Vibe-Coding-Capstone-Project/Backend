# Active Tasks (the loop's worklist)

> Planner fills this; Dev/QA work it; clear done items to progress.md.

## Recently done (details in progress.md)
- [x] D2 — Document ingestion: `POST/GET /documents`, 5 parsers → normalized text.
- [x] D3 — Chunk + embed + store: `rag/` (chunking, embeddings, Chroma store, index); uploads indexed; live Gemini verified. pytest 24/24.
- [x] D4 — RAG retrieval + generation: `POST /rescue` → grounded Gemini Flash script + citations; offline fake generator; prompt v1 doc; grounding eval seed. pytest 29/29; live smoke passed.
- [x] D5 — Sessions + history + lyric formatting: sqlite3 store, `POST/GET /sessions`, `session_id` on `/rescue` records turns, `to_lyric_lines`; generation failures degrade to bridge. pytest 36/36; live full-stack smoke + persistence verified.

## D6 — QA + harden (next, end of Week 1)
Goal: grounding eval set 10–15 Q/A, latency check, error handling; tune `rescue_min_score`. QA-agent pass + fix top issues.
- [ ] Expand `tests/eval/grounding.jsonl` to 10–15 Q/A and add a live (keyed) eval runner — owner — grounded ≥ ~90%.
- [ ] Latency check on `/rescue` (retrieve + generate) vs ~4s budget — owner — measured, logged.
- [ ] Tune `rescue_min_score` + consider refusal detection (report grounded=False when the model bridges) — owner — fewer false-grounded.
- [ ] `/qa-review` gate over D2–D5; fix top issues.

## Format
`- [ ] <task> — owner — acceptance criteria`
