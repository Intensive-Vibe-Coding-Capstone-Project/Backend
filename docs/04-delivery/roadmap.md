# 2-Week Roadmap — "Cue" Capstone

Window: **Mon 22 Jun → Sun 5 Jul 2026** · Submission target: **Sat 4 Jul** (1-day buffer before Sun 5).

> Fill in team + roles at the bottom. Daily rhythm follows Loop Engineering (`docs/03-agents/loop-overview.md`): **plan → dev → QA → update context**.

## MVP definition (must ship)

Upload docs → RAG index → **manual "rescue" button** + **periodic 30s scan** → grounded rescue script rendered line-by-line → session history. STT via streaming API. Everything reproducible for Kaggle.

Auto keyword/silence triggers and full live duplex audio are **stretch**, attempted only after MVP is green.

---

## Week 1 — Foundation + RAG core (Mon 22 → Sun 28 Jun)

**Goal by Sun 28:** a user can upload docs and get a grounded rescue script from a typed/pasted question. No voice yet.

| Day | Focus | Concrete output |
|-----|-------|-----------------|
| **D1 Mon 22** | Setup + context system | This docs/skills scaffold; confirm tech stack (`tech-stack.md`); repo skeleton (FastAPI app, env, lint, CI stub); decide vector store. |
| **D2 Tue 23** | Document ingestion | Upload endpoint + parsers for pdf/docx/txt/pptx/epub → normalized text. Unit tests on sample files. |
| **D3 Wed 24** | Chunk + embed + store | Chunking strategy, Gemini embeddings, vector store write/read. `POST /documents`, `GET /documents`. |
| **D4 Thu 25** | RAG retrieval + generation | `POST /rescue` (text question) → retrieve → Gemini prompt → grounded script. Prompt v1 in `docs/02-engineering/`. |
| **D5 Fri 26** | Sessions + history | Session model, persist Q→script turns, `GET /sessions/{id}`. Lyric-line formatting of output. |
| **D6 Sat 27** | QA + harden | QA agent pass: grounding eval set (10–15 Q/A), latency check, error handling. Fix top issues. |
| **D7 Sun 28** | Integrate w/ frontend (text path) | End-to-end text demo with the frontend repo. Tag `v0.1-text`. |

**Week 1 exit criteria:** text-only rescue works end to end, grounded, < ~4s, with history. Demoable.

---

## Week 2 — Voice, triggers, polish, submit (Mon 29 → Sun 5 Jul)

**Goal by Sat 4:** all 4 use cases demoable; Kaggle submission complete.

| Day | Focus | Concrete output |
|-----|-------|-----------------|
| **D8 Mon 29** | Streaming transcript ingest | STT integration; `WS /stream` or SSE; rolling transcript buffer per session. |
| **D9 Tue 30** | Trigger engine | Manual button → uses last transcript window. Periodic 30s scan → rescue if relevant. Wire to `/rescue`. |
| **D10 Wed 1 Jul** | Slip / flow detection | Compare spoken transcript vs prepared script → detect divergence (wrong brand, off-flow) → correction script. (Use case 3 & 4.) |
| **D11 Thu 2** | Stretch triggers + polish | Keyword + silence auto-triggers (if MVP solid). UX polish on line rendering, latency, edge cases. |
| **D12 Fri 3** | Full QA + eval | QA agent: run all 4 use cases, grounding + latency eval, bug bash. Freeze features. |
| **D13 Sat 4** | **Kaggle submission** | Reproducible notebook/demo, writeup (`kaggle-submission.md`), demo video, README polish. **Submit.** |
| **D14 Sun 5** | Buffer / retro | Fix-only. Record retro + post-capstone roadmap. Tag `v1.0`. |

**Week 2 exit criteria:** all 4 use cases run in a recorded demo; Kaggle entry submitted with reproducible artifact + writeup.

---

## Risk register (watch these)

| Risk | Mitigation |
|------|-----------|
| Real-time voice is hard | MVP uses manual + periodic triggers; live duplex is stretch. Ship text path Week 1 first. |
| Latency > 4s | Cache embeddings; small retrieval k; use Gemini Flash for generation; stream tokens to UI. |
| Grounding / hallucination | Strict RAG prompt, citations, refusal when no support; eval set gate before submit. |
| Doc parser edge cases (ppt/epub) | Test with real files D2; fall back to text extraction lib (unstructured) if needed. |
| Scope creep | Keep MVP/stretch split (this file + PRD §7). QA agent enforces "done". |
| Kaggle reproducibility | Pin deps, seed, document keys/secrets handling early (D1), dry-run notebook D12. |

## Cadence

- Daily 15-min standup → update `context/active-tasks.md` + `context/progress.md`.
- Decisions → `context/decisions-log.md` (and an ADR if architectural).
- Use `/plan-feature`, `/qa-review`, `/rag-endpoint`, `/kaggle-writeup` skills to stay consistent.

## Team & roles (fill in)

- Member A — …
- Member B — …
- (Backend / Frontend / RAG / QA / Kaggle owner)
