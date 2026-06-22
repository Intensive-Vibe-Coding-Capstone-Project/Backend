# Active Tasks (the loop's worklist)

> Planner fills this; Dev/QA work it; clear done items to progress.md.

## Today (D1 ✅ done)
- [x] Confirm tech stack + log it. — Chroma + Gemini ids + py≥3.11 (decisions-log, tech-stack).
- [x] FastAPI skeleton + `.env` + lint + test runner. — `src/cue/`, ruff, pytest 4/4 green, CI stub.
- [x] Choose vector store; install deps. — Chroma; core+dev installed in `.venv` (py 3.14).

## Backlog (next up)
- [ ] `POST /documents` ingestion + parsers (pdf/docx/txt/pptx/epub) — D2 — endpoint accepts upload, routes by type, returns normalized text; unit tests on sample files. Install `.[parsers]`.
- [ ] Chunking + Gemini embeddings + vector write/read — D3 — Install `.[rag]`.
- [ ] `POST /rescue` (text) → retrieve → Gemini → grounded script.
- [ ] Session model + history.
- [ ] Grounding eval set (10–15 Q/A).

## Format
`- [ ] <task> — owner — acceptance criteria`
