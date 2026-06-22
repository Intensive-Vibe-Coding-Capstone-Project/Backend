# Active Tasks (the loop's worklist)

> Planner fills this; Dev/QA work it; clear done items to progress.md.

## D2 — Document ingestion (dev done ✅, pending /qa-review)
Goal: upload pdf/docx/txt/pptx/epub → normalized text + metadata; `GET /documents` lists. Serves PRD §4 (all use cases). MVP. Embed/store is D3 — D2 keeps parsed docs in an in-memory registry only.
- [x] Install `.[parsers]` (pypdf, python-docx, python-pptx, ebooklib) — dev — installed in `.venv`; CI installs `.[dev,parsers]`.
- [x] `ingestion/models.py`: `ParsedDocument` + `DocumentMeta` (StrEnum `DocType`) — dev — models validate.
- [x] `ingestion/parsers.py`: dispatch-by-type → normalized text (lazy lib imports) — dev — 5 types parse on runtime samples; unknown → `UnsupportedDocTypeError`.
- [x] `ingestion/service.py` + `errors.py`: parse → normalize → in-memory registry; size/empty guards — dev — ingest/get/list covered.
- [x] `api/routes/documents.py`: `POST /documents` 201 + meta; `GET /documents` list; wired — dev — 201+id; 415/413/422 via `{error,detail}`.
- [x] `tests/`: per-parser + endpoint tests, runtime-generated fixtures — dev — pytest 19/19, ruff clean.

## Backlog (next up)
- [ ] Chunking + Gemini embeddings + vector write/read — D3 — Install `.[rag]`.
- [ ] `POST /rescue` (text) → retrieve → Gemini → grounded script.
- [ ] Session model + history.
- [ ] Grounding eval set (10–15 Q/A).

## Format
`- [ ] <task> — owner — acceptance criteria`
