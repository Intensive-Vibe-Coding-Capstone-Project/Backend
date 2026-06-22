# Decisions Log (append-only)

> Quick decisions. If a decision is architectural, also create an ADR in `docs/01-architecture/adr/`.

| Date | Decision | Why | By |
|------|----------|-----|-----|
| 2026-06-22 | Adopt a context-engineering docs system (`docs/`, `context/`, `.claude/skills/`). | Enables Loop Engineering; serves Kaggle/onboarding/release. | team |
| 2026-06-22 | Use Agent Skills; treat `skill-creator` as optional accelerator. | Skills aid the dev loop; not needed to ship. | team |
| 2026-06-22 | Default stack: Python/FastAPI + Gemini + Chroma (proposed). | Google course + Kaggle reproducibility. | team (confirm) |
| 2026-06-22 | **Confirm vector store = Chroma** (local persistent). | Easiest reproducible-on-Kaggle option; revisit pgvector only at deploy. | team |
| 2026-06-22 | **Gemini ids:** rescue=`gemini-2.5-flash`, reasoning=`gemini-2.5-pro`, embeddings=`gemini-embedding-001`; SDK = `google-genai`. | Flash = low-latency rescue (<4s budget); Pro for hard reasoning; one vendor for keys. All in `config.py`, not hard-coded. | team |
| 2026-06-22 | **Python `>=3.11`** (dev on 3.14 local). | Matches conventions; modern typing; CI pins 3.11/3.12. | team |
| 2026-06-22 | Backend skeleton: `src/cue/` package layout, FastAPI app factory, `pydantic-settings` config, `pytest`, `ruff`, GitHub Actions CI stub. | D1 roadmap deliverable; sets the loop's foundation. | team |
| 2026-06-22 | Provider interfaces for embeddings + generation (`gemini`/`fake`, `auto` resolves on key) behind protocols. | Keeps tests + CI hermetic and keyless; live Gemini used only when a key is present. | team |
| 2026-06-22 | Two-layer grounding for `/rescue`: retrieval score threshold → hard bridge (no LLM call); prompt rule → soft refusal. | Prevents hallucination even on borderline retrieval; `rescue_min_score` tunable in D6. | team |
| 2026-06-22 (D6) | **Refusal detection is the primary grounding guard**; `rescue_min_score` demoted to a 0.4 floor. | QA found Gemini embeddings are anisotropic (nonsense scores ~0.6 on short text) — similarity threshold alone is unreliable; trusting the model's refusal is robust. | QA |
| 2026-06-22 (D6) | Retry transient Gemini 5xx (3 attempts) in `GeminiGenerator`; cap `max_output_tokens`. | A live tool should ride out a transient 503; capping output cuts latency/cost. Persistent failure still degrades to the safe bridge. | QA |
| 2026-06-22 (D8) | **STT: defer real audio; MVP ingests transcript TEXT over `WS /stream`.** Audio STT (Gemini live / Google STT) is stretch (D11). | Risk register: ship the text path first; audio is hard to test/reproduce for Kaggle. Resolves the open STT tech-stack item. | team |
| 2026-06-22 | Session/turn persistence via **stdlib `sqlite3`** at `CUE_DB_PATH` (`./cue.db`, gitignored). | Persists across restarts (live demo); zero new deps; Kaggle-reproducible; matches tech-stack (SQLite dev → Postgres deploy). | team |
| 2026-06-23 (D11) | **Keyword + silence auto-triggers** in the auto-scan (`auto_reason` → keyword > silence > periodic). Keyword/silence relax the min-chars gate; all auto modes still dedup on an unchanged window + suppress ungrounded bridges. | Fires fast when the speaker stumbles ("good question") or stalls (>10s silence), without spamming on a quiet/unchanged window. Lexical keyword match = provider-independent + deterministic. | team |
| 2026-06-23 (D11) | **Live grounding eval still BLOCKED — now by free-tier daily quota** (`gemini-2.5-flash` = 20 generate/day, HTTP 429). Code degrades gracefully (429 → bridge, no crash/hallucination). | Earlier block was a 503 outage; today it's quota. The reproducible offline gate stays the CI signal. **D13 risk:** budget the 13-case eval + demo against 20/day, or enable billing / raise `scan_interval_s` for the live demo (each scan with new speech = 1 generate). | team |
