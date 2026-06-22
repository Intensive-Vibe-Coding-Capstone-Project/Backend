# Kaggle Submission — Writeup Template

> Assemble from existing artifacts (PRD, system-design, demo). Use `/kaggle-writeup` to draft. Fill before D13 (Sat 4 Jul).

## 1. Title & one-liner
Cue — an AI agent that helps speakers recover in real time from hard questions and slips, grounded in their own documents.

## 2. Problem & who it's for
(From PRD §1, §3.) Students, office workers, content creators freeze on unexpected questions / mistakes.

## 3. What it does (use cases)
The 4 use cases (PRD §4): hard Q mid-talk, hard Q in Q&A, live-sale slip, recording flow break.

## 4. How it works (architecture)
Embed the diagram from `system-design.md`. Explain: ingestion → RAG → trigger → Gemini rescue → lyric rendering.

## 5. AI agent design
- Runtime: Gemini-based rescue orchestrator (RAG + transcript + trigger).
- Built with **Loop Engineering** (planner/dev/QA) + Context Engineering (this docs system). Show the loop diagram — this is a course differentiator.

## 6. Demo
- Link to demo video + screenshots. Walk through one use case end to end. See `demo-script.md`.

## 7. Reproducibility
- Notebook/steps to run: deps (pinned), env vars (which keys, how to set in Kaggle Secrets), sample docs, sample run.
- Note model ids, vector store, seeds.

## 8. Results / eval
- Grounding rate on the eval set; latency numbers; what worked / limits.

## 9. Business impact
- Time-to-recover ↓; confidence ↑; fewer on-stage errors for KOLs/presenters.

## 10. Future work
- Auto triggers, full duplex audio, multi-language, deploy, team workspaces (PRD §7 "out").

## Submission checklist
- [ ] Writeup complete  - [ ] Reproducible notebook/demo  - [ ] Video  - [ ] Repo link + README  - [ ] Keys handled via Kaggle Secrets  - [ ] Dry-run from clean env
