# Active Tasks (the loop's worklist)

> Planner fills this; Dev/QA work it; clear done items to progress.md.

## Recently done (details in progress.md)
- [x] D2 — Document ingestion: `POST/GET /documents`, 5 parsers → normalized text.
- [x] D3 — Chunk + embed + store: `rag/` (chunking, embeddings, Chroma store, index); uploads indexed; live Gemini verified. pytest 24/24.
- [x] D4 — RAG retrieval + generation: `POST /rescue` → grounded Gemini Flash script + citations; offline fake generator; prompt v1 doc; grounding eval seed. pytest 29/29; live smoke passed.

## Backlog (next up)
- [ ] Session model + persist Q→script turns; `GET /sessions/{id}`; lyric-line formatting — D5.
- [ ] Grounding eval expansion to 10–15 Q/A + tune `rescue_min_score` / refusal detection — D6.

## Format
`- [ ] <task> — owner — acceptance criteria`
