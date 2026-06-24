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

- [x] D8 — Streaming transcript ingest: `transcript/` (buffer + service), `WS /stream/{session_id}` ingest+ack, STT decision (text-over-WS; audio stretch). pytest 46/46.

- [x] D9 — Trigger engine: `triggers/engine.py` (manual + periodic, should_fire dedup + ungrounded suppression, records turn); WS `{type:"trigger"}` + periodic scan task (send lock, to_thread). pytest 52/52.

- [x] D10 — Slip / flow detection: prepared script per session (`PUT /sessions/{id}/script`), lexical brand + off-flow detection, correction grounded in script, WS `{type:"check_slip"}` + periodic slip. pytest 60/60. **All 4 use cases now covered.**

- [x] D11 — Stretch triggers + UX polish: keyword + silence auto-triggers (`matched_keyword` + `auto_reason`/`auto_fire`, keyword > silence > periodic; auto modes dedup + suppress ungrounded); demo UI gains a prepared-script panel (`PUT /sessions/{id}/script`) + a live-transcript WS panel (connect, send lines, manual trigger, check-slip, live karaoke render + badges + log). pytest 66/66.

## D12 — Full QA + eval pass — verdict: **FAIL vs grounding target**
- [x] Ran `qa-review` over the whole pipeline (D2–D11): pytest **66/66** keyless, ruff clean, edge cases + `{error,detail}` envelope verified (415/422/413/404, WS 4404, generation failure → bridge).
- [x] Live grounding rate via a **throttled** run (the real free-tier cap is **5 req/min**, not 20/day — throttling beats it): **11/13 = 85%** — UNDER the ≥90% target. All 10 on-topic cases ground correctly; off-topic refusal leaked on 2/3 (`off1`, `off3` returned grounded scripts for nonsense; `off2` refused).
- [x] Latency (live): p50 **4.08s** (≈budget), p95/max **7.60s** (over ~4s). Mitigation = token streaming (still deferred).

## D12 follow-up — fix before final Submit (blocks a clean ≥90%)
- [ ] **Off-topic over-grounding:** all 3 off-topic Qs pass the `rescue_min_score` 0.4 floor (anisotropic embeddings) → LLM called; refusal detection caught only 1/3 — Dev — get live grounding ≥90%. Options: strengthen the refusal prompt (primary guard, per D6 decision) and/or add a post-gen relevance check; min_score tuning is delicate (all 10 grounded cases must stay grounded).
- [ ] Latency: token streaming to cut perceived time vs p95 7.6s — Dev — within demo budget.

## D13 — Kaggle submission
- [x] Assemble `docs/04-delivery/kaggle-submission.md` from artifacts with an honest §8 (offline 66/66 + 13/13 classify; live 85% + off-topic leak + p95 7.6s disclosed). README Status refreshed.
- [ ] Record demo video per `demo-script.md` — owner.
- [ ] Package the Kaggle notebook (or link repo + run steps); dry-run from a clean env — owner.
- [ ] Final Submit on Kaggle (after the grounding fix lands ≥90%) — owner.

## Backlog
- [ ] Latency: stream tokens to cut perceived time vs ~4s budget (D8+ streaming) — owner.
- [ ] Audio STT (Gemini live / Google STT) — stretch beyond the text path.
- [ ] Demo cost: each auto-scan with new speech = 1 Gemini generate; the binding free-tier cap is **5 req/min** (gemini-2.5-flash), so consider raising `scan_interval_s`, throttling, or enabling billing for the live demo.

## Format
`- [ ] <task> — owner — acceptance criteria`
