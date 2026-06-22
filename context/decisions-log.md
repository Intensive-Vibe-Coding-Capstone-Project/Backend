# Decisions Log (append-only)

> Quick decisions. If a decision is architectural, also create an ADR in `docs/01-architecture/adr/`.

| Date | Decision | Why | By |
|------|----------|-----|-----|
| 2026-06-22 | Adopt a context-engineering docs system (`docs/`, `context/`, `.claude/skills/`). | Enables Loop Engineering; serves Kaggle/onboarding/release. | team |
| 2026-06-22 | Use Agent Skills; treat `skill-creator` as optional accelerator. | Skills aid the dev loop; not needed to ship. | team |
| 2026-06-22 | Default stack: Python/FastAPI + Gemini + Chroma (proposed). | Google course + Kaggle reproducibility. | team (confirm) |
