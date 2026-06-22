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

## D3 — Chunk + embed + store (dev done ✅, pending /qa-review)
Goal: on upload, chunk → embed (Gemini, fake fallback) → store in Chroma; `GET /documents` reads the store; unit-tested `query(question,k)` ready for D4. Serves PRD §4 (RAG index). MVP. Retrieval endpoint is D4.
- [x] Install `.[rag]` (google-genai 2.9.0, chromadb 1.5.9) — dev — both import on py3.14; watch-item closed; CI installs `.[dev,parsers,rag]`.
- [x] `config.py` + `.env.example`: `embeddings_provider` (auto|gemini|fake), `embedding_dim`, `embedding_batch_size`, `chroma_collection`; `active_embeddings_provider` — dev — auto→gemini iff key present.
- [x] `rag/chunking.py`: boundary-aware `chunk_text` → `Chunk(index,text,start,end)` — dev — covers text, overlaps adjacent, no mid-word cuts; unit-tested.
- [x] `rag/embeddings.py`: `Embedder` protocol + `GeminiEmbedder` (RETRIEVAL_DOCUMENT/QUERY, batched) + `FakeEmbedder` + `get_embedder()` — dev — fake deterministic+normalized; factory honors provider/key.
- [x] `rag/models.py` + `rag/store.py`: `Passage` (citation_id) + Chroma cosine store (add/list/query/get/delete), telemetry off, EF disabled — dev — add→list→query round-trips.
- [x] `rag/index.py`: `index_document` (chunk→embed→store) + `query` — dev — stores N chunks; query returns ranked, cited passages.
- [x] Rewire `POST/GET /documents` to the store; `service.parse_upload` is parse-only; conftest isolates temp Chroma + fake embedder — dev — endpoints report `n_chunks`; pytest 24/24 keyless; ruff clean; live Gemini smoke passed.

## Backlog (next up)
- [ ] `POST /rescue` (text) → retrieve → Gemini → grounded script — D4 — uses `rag.index.query`.
- [ ] Session model + history.
- [ ] Grounding eval set (10–15 Q/A).

## Format
`- [ ] <task> — owner — acceptance criteria`
