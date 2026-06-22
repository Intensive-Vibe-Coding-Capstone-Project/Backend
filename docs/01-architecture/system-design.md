# System Design — "Cue"

## High-level flow

```
                 ┌──────────────┐
  Upload docs ──▶│  Ingestion   │── parse → chunk → embed ─▶ ┌────────────┐
  (pdf/docx/...) └──────────────┘                            │ Vector DB  │
                                                             └─────┬──────┘
  Mic / audio ──▶ STT (stream) ──▶ Transcript buffer ──┐           │ retrieve
                                                        ▼           ▼
                                              ┌───────────────────────────┐
   Trigger (button / 30s / keyword / silence)─▶│  Rescue Orchestrator      │──▶ Gemini ──▶ rescue script
                                              └───────────────────────────┘                 │
                                                        │ persist turn                       ▼
                                                        ▼                          line-by-line render
                                                  Session store                     (lyrics style)
```

## Components (backend = this repo)

1. **Ingestion service** — accepts uploads, routes to parser by type (pdf/docx/txt/pptx/epub), normalizes to text, chunks, embeds (Gemini embeddings), writes to vector DB with metadata (doc id, source, position).
2. **Retrieval** — given a query (typed question or transcript window), embed + top-k similarity search, return passages with citations.
3. **Rescue Orchestrator** — the core. Builds the prompt from: retrieved passages + recent transcript window + prepared-script (for slip/flow detection) + persona/style. Calls Gemini, returns a short speakable script.
4. **Transcript pipeline** — streaming STT → rolling buffer per session (timestamps for silence detection + windowing).
5. **Trigger engine** — manual button, periodic 30s tick, keyword matcher, silence detector. Decides when to call the orchestrator and with what window.
6. **Session/history store** — sessions, turns (question → script), uploaded-doc refs.
7. **API + realtime** — REST for upload/rescue/history; WebSocket or SSE for live transcript + streamed script tokens.

## Key endpoints (draft — see api-spec.md)

- `POST /documents` — upload + ingest. `GET /documents` — list.
- `POST /sessions` — start session (binds a doc set). `GET /sessions/{id}` — history.
- `POST /rescue` — `{session_id, question | transcript_window, mode}` → rescue script (+ citations).
- `WS /stream` (or `GET /stream` SSE) — push audio/transcript, receive triggers + streamed scripts.

## Cross-cutting

- **Grounding:** orchestrator must answer only from retrieved context; if unsupported, return a safe "bridge" line, not a hallucination.
- **Latency budget (~4s):** parallelize retrieve+format; Gemini Flash for generation; stream tokens.
- **Slip/flow detection:** diff transcript window against prepared script embeddings → flag divergence → correction-mode prompt.
- **Privacy:** user docs + audio are sensitive — document retention + key handling in setup/ADR before any deploy.
