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
