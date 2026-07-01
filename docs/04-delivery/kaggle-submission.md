# Kaggle Submission — Cue

> Capstone for *5-Day AI Agents: Intensive Vibe Coding Course with Google*.
> Assembled from project artifacts (PRD, system-design, demo script, D12 QA/eval). Numbers are **measured**, not aspirational.

## 1. Title & one-liner

**Cue** — an AI agent that helps speakers recover in real time from hard questions and slips, generating a short, ready-to-read **rescue script grounded in their own documents**, shown line-by-line like song lyrics.

## 2. Problem & who it's for

People who present, sell live, or record content prepare heavily but get caught off-guard by (a) a hard/unexpected question, (b) saying the wrong thing (a KOL naming the wrong brand), or (c) losing the script mid-recording. Today they freeze, or stall while googling. Cue removes that gap.

**Users:** student presenters defending a project, office workers pitching under pressure, and content creators / KOLs selling or recording live.

## 3. What it does (use cases)

All four PRD use cases are covered end-to-end in the backend:

1. **Hard question mid-talk** — repeat the question aloud → `POST /rescue` (or the live WS trigger) → grounded next-lines to say.
2. **Hard question in Q&A** — same path, after the talk.
3. **Live-sale slip** — the ~30s scan detects the spoken brand diverging from the prepared script → a correction line.
4. **Recording flow break** — off-flow speech (low overlap with the prepared script) → a recovery suggestion.

## 4. How it works (architecture)

```
                 ┌──────────────┐
  Upload docs ──▶│  Ingestion   │── parse → chunk → embed ─▶ ┌────────────┐
  (pdf/docx/...) └──────────────┘                            │ Chroma DB  │
                                                             └─────┬──────┘
  Transcript ──▶ WS /stream ──▶ Transcript buffer ──┐              │ retrieve
  (text MVP)                                         ▼              ▼
                                          ┌───────────────────────────┐
   Trigger (button / 30s / keyword /      │    Rescue Orchestrator     │──▶ Gemini Flash ──▶ rescue script
   silence)──────────────────────────────▶│  (RAG + window + script)   │            │
                                          └───────────────────────────┘            ▼
                                                    │ persist turn        line-by-line render
                                                    ▼                       (lyrics style)
                                              Session store (SQLite)
```

**Pipeline:** ingestion (parse pdf/docx/txt/pptx/epub → normalize → chunk → Gemini embeddings → Chroma) → retrieval (top-k with citations `doc_id:chunk_index`) → rescue orchestrator (builds the prompt from retrieved passages + transcript window + prepared script) → Gemini Flash → lyric-line rendering. Sessions/turns persist in SQLite; the live path streams transcript over WebSocket and fires triggers.

**Grounding (two layers + a guard):** a retrieval score floor hard-bridges obviously-empty retrieval *without* an LLM call; the prompt instructs "answer only from context, else return a safe bridge line"; and **refusal detection** is the primary guard (a model "I don't have that" → `grounded=False`). A rescue with no support returns a safe **bridge line**, never an invented fact.

## 5. AI agent design

- **Product runtime:** a Gemini-based **rescue orchestrator** — a RAG agent that fuses retrieved passages, the rolling transcript window, and the prepared script, then decides between a grounded script and a safe refusal. A **trigger engine** (manual / periodic / keyword / silence) decides *when* it fires; a lexical **slip detector** (brand + off-flow) covers the live-sale / recording cases. Providers sit behind protocols (`gemini` | `fake` | `auto`), so the whole system runs deterministically offline.
- **How we built it — Loop Engineering** (a course differentiator): three Claude-Code agents drive development. **These agents build the app; they are not the app.**

```
   ┌──────────┐     plan      ┌──────────┐    code     ┌──────────┐
   │ PLANNER  │ ───────────▶ │   DEV    │ ─────────▶ │    QA    │
   └──────────┘               └──────────┘             └────┬─────┘
        ▲                                                   │ pass/fail
        │            update context (progress, decisions)   │
        └───────────────────────────────────────────────────┘
```

One trip = one roadmap task, grounded in a **Context Engineering** docs system (`docs/` + `context/` + `.claude/skills/`). The QA agent gate (this submission's eval) is part of that loop.

## 6. Demo

~3-minute walkthrough (script in `docs/04-delivery/demo-script.md`): hook → upload + index → **use case 1** (hard Q → grounded lyric script) → **use case 3** (wrong brand → correction line) → architecture + loop diagram → impact. The text-path UI at `/ui` exercises upload → session → ask → lyric render + citations + history; the live panel connects to `WS /stream`, streams transcript, and shows mode/grounded/slip badges.

> **Video:** https://youtu.be/9WT2cFZ4iuA — ~2–3 min ad-style walkthrough (AuroraBuds Pro scenario): upload/index → hard question → grounded karaoke rescue → on-purpose brand slip caught live.

## 7. Reproducibility

- **Python** ≥3.11 (developed on 3.14; CI pins 3.11/3.12).
- **Install:** `pip install -e ".[dev,parsers,rag]"`.
- **Pinned dep floors** (`pyproject.toml`): `fastapi>=0.115`, `pydantic>=2.7`, `google-genai>=0.3`, `chromadb>=0.5`, parsers `pypdf`/`python-docx`/`python-pptx`/`ebooklib`.
- **Models / store (in `config.py`, not hard-coded):** rescue = `gemini-2.5-flash` (temp 0.3, capped output), embeddings = `gemini-embedding-001`, vector store = **Chroma** (local persistent), sessions = SQLite.
- **Secrets:** `GEMINI_API_KEY` only — set via **Kaggle Secrets** (or `.env` locally; `.env` is gitignored, no key is committed). Overrides are `CUE_*` env vars (`CUE_CHROMA_DIR`, `CUE_DB_PATH`, `CUE_MAX_UPLOAD_MB`, thresholds).
- **Determinism:** with **no key**, embeddings + generation fall back to deterministic **fakes**, so `pytest` and the offline eval are fully reproducible (no network). Live runs use Gemini Flash at temp 0.3.
- **Run:** `pytest` (keyless) · `cue` (dev server, `/ui`) · `python tests/eval/run_eval.py` (grounding + latency; live with a key, offline without).

## 8. Results / eval (measured)

**Offline gate (reproducible CI signal):**
- `pytest` **66/66** green, keyless; `ruff check` + `format --check` clean.
- 13-case grounding eval classifies grounded-vs-bridge **correctly (13/13)** on the deterministic fake embedder.

**Live eval (real Gemini, D12 / 2026-06-24):**
- **Grounding: 11/13 = 85%** classification accuracy — **below the ≥90% target (PRD §8).**
  - On-topic: **10/10** grounded correctly, with citations.
  - Off-topic: **1/3** correctly refused; **2/3 leaked** (returned a grounded script for an unrelated question).
- **Latency:** p50 **4.08s** (≈ the ~4s budget), p95/max **7.60s** (over budget).

**What worked:** end-to-end grounding on real prepared content is reliable (10/10); no hard failures — every error path degrades to the safe bridge (transient 5xx auto-retries; 429 → bridge, no crash/hallucination).

**Known limit (honest):** off-topic over-grounding. Gemini embeddings are anisotropic — even nonsense scores above the `rescue_min_score` floor — so the LLM gets called, and refusal detection (the primary guard) caught only 2/3 off-topic cases this run. **Fix planned before final submit:** strengthen the refusal prompt and/or add a post-generation relevance check; do *not* over-tighten the score floor (it would start refusing real content). The free-tier limit is **5 requests/minute**, so the live eval must be throttled (~14s/case) to read a clean number.

## 9. Business impact

Time-to-recover drops from "freeze + google" to a few seconds of ready-to-read script; presenters stay on-message and on-brand; KOLs catch slips live instead of in the edit. The output is grounded in the user's *own* material, so it sounds like them — not a generic chatbot.

## 10. Future work

Per PRD §7 "stretch/out": fully bi-directional **live audio STT** (MVP ingests transcript text), token **streaming** to cut p95 latency, multi-language, fine-tuned signal detection, auth / team workspaces, and deploy (Cloud Run + pgvector). Immediate next: close the off-topic grounding gap to clear ≥90%.

## Submission checklist

- [x] Writeup complete (this file)
- [x] Reproducible run path (deps pinned, keyless fakes, `run_eval.py`, model ids/store documented) — **dry-run from a clean env still owed**
- [x] Demo video — https://youtu.be/9WT2cFZ4iuA
- [x] Repo link + README (polished)
- [x] Keys handled via Kaggle Secrets / `.env` (no key committed)
- [ ] **Grounding ≥90% before final submit** — currently 85% live (off-topic leak); fix outstanding
- [ ] Notebook packaged for Kaggle (or link the repo + run steps)
