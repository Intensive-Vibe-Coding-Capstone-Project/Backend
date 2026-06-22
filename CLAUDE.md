# CLAUDE.md — Agent Context (read this first)

> This file is auto-loaded into every Claude Code / agent session. Keep it **short, current, and true**. It is the entry point to the whole context system. When something here goes stale, fix it immediately.

## 1. What we are building

**Product (codename: "Cue")** — a web app that helps a speaker *recover in real time* when they hit an unexpected question or mistake during a presentation, live sale, or video shoot.

Flow: the user uploads their source documents → we index them (RAG) → during the talk we listen / receive transcript → when a "rescue" is needed (button press, periodic scan every ~30s, urgent keyword, or long silence) we generate a grounded, ready-to-read **rescue script** displayed line-by-line (karaoke / lyrics style).

Target users: students, office workers, content creators / KOLs.

This is the **capstone** for *5-Day AI Agents: Intensive Vibe Coding Course with Google*. Final deliverable is submitted on **Kaggle**.

## 2. Two layers — do not confuse them

| Layer | What it is | Tech |
|-------|-----------|------|
| **The Product** | The "Cue" app we ship & submit on Kaggle | **Google Gemini** + Python/FastAPI (this repo = backend) + a separate frontend repo |
| **The Dev Workflow** | How *we* build it ("Loop Engineering": planner → dev → QA agents) | **Claude Code** + Agent **Skills** in `.claude/skills/` + this docs system |

> Agent **Skills** are a Claude feature → they power our *development* loop, not the shipped Gemini product. The product's "agents" are Gemini tools/sub-agents.

## 3. Repo map

- `MeetingMinute/` — raw meeting notes (source of truth for intent)
- `docs/00-product/` — PRD, personas, use cases (the *what* and *why*)
- `docs/01-architecture/` — system design, data model, tech stack, ADRs (the *how*)
- `docs/02-engineering/` — conventions, API spec, testing, setup
- `docs/03-agents/` — Loop Engineering specs (planner / dev / QA agents)
- `docs/04-delivery/` — 2-week roadmap, Kaggle submission, demo script
- `docs/05-context-engineering/` — the playbook for this whole system
- `.claude/skills/` — reusable agent procedures (plan-feature, qa-review, rag-endpoint, kaggle-writeup)
- `context/` — **living working memory**: progress, decisions log, active tasks, glossary

## 4. Operating rules for agents

1. **Read before you write.** Start a task by reading `context/progress.md` + the relevant `docs/` file.
2. **One source of truth per fact.** Don't duplicate. Link instead.
3. **Close the loop.** After a change: update `context/progress.md` and, if a decision was made, append to `context/decisions-log.md`.
4. **Ground every product answer in the user's documents** (RAG). No hallucinated rescue scripts.
5. **MVP first.** See `docs/04-delivery/roadmap.md` for what is in/out of the 2-week scope.
6. Follow `docs/02-engineering/conventions.md` for all code.

## 5. Status

- Phase: **Setup / Week 1** (see roadmap). Greenfield backend.
- Stack is a recommended default — confirm/adjust in `docs/01-architecture/tech-stack.md`.
