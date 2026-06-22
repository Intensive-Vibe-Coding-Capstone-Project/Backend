---
name: rag-endpoint
description: Dev-agent procedure to add or change a RAG/ingestion/rescue endpoint in Cue's FastAPI backend, following project conventions and grounding rules. Trigger words: add endpoint, ingestion, retrieval, rescue endpoint, embed, vector store, RAG feature.
---

# Build a RAG endpoint (Dev agent)

Implement an ingestion / retrieval / rescue endpoint consistently.

## Before coding
- Read `docs/01-architecture/system-design.md` (component + endpoint), `tech-stack.md`, and `docs/02-engineering/conventions.md`.
- Confirm there's a Planner plan + acceptance criteria in `context/active-tasks.md`.

## Steps
1. **Contract:** define pydantic request/response models. Match endpoint naming in system-design.
2. **Wire the module:** put logic in the right package (`ingestion/`, `rag/`, `rescue/`…); keep core logic pure, I/O at edges.
3. **Ingestion endpoints:** route by file type → parse → normalize → chunk (config-driven size/overlap) → embed (Gemini) → store with metadata (doc id, source, position).
4. **Retrieval/rescue endpoints:** embed query (question or transcript window) → top-k search → build a **grounded** prompt (passages + transcript + style) → Gemini Flash → return script **with citations**. If no support, return a safe bridge line.
5. **Config not magic numbers:** model id, k, chunk size, thresholds → settings.
6. **Tests:** unit tests for the endpoint; add RAG cases to the grounding eval set.
7. **Latency:** parallelize retrieve/format; stream tokens if it helps perceived speed.

## After coding
- Update `context/progress.md`. Hand to `/qa-review`.

## Guardrails
- Never generate ungrounded rescue content. Always pass + cite retrieved context.
- Don't commit/push unless asked. Don't hardcode secrets.
