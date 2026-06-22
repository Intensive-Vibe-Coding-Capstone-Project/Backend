# Cue — Real-time Presentation Rescue Agent (Backend)

> Capstone for *5-Day AI Agents: Intensive Vibe Coding Course with Google*.

**Cue** helps a speaker recover in real time from a hard question or a slip — by generating a short, ready-to-read **rescue script** grounded in the user's own uploaded documents (RAG), shown line-by-line like song lyrics.

## Who & why
Students, office workers, and content creators / KOLs who present, sell live, or record — and need an instant, on-message recovery instead of freezing or googling.

## How it works
Upload docs → index (RAG) → during the talk, a trigger (button / 30s scan / keyword / silence) sends the recent transcript to a Gemini-based orchestrator → returns a grounded rescue script. See [system design](docs/01-architecture/system-design.md).

## Start here (onboarding)
1. [CLAUDE.md](CLAUDE.md) — project map & rules (read first).
2. [docs/00-product/PRD.md](docs/00-product/PRD.md) — what & why.
3. [docs/01-architecture/](docs/01-architecture/) — system design, tech stack, ADRs.
4. [docs/04-delivery/roadmap.md](docs/04-delivery/roadmap.md) — the 2-week plan.
5. [context/progress.md](context/progress.md) — where we are right now.

## Setup (dev)
Requires **Python ≥3.11** (developed on 3.14).
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate   ·   macOS/Linux: source .venv/bin/activate
pip install -e ".[dev]"          # core + test/lint toolchain
cp .env.example .env             # then add your GEMINI_API_KEY

ruff check . && ruff format --check .   # lint
pytest                                   # tests
cue                                      # run dev server at http://127.0.0.1:8000  (docs at /docs)
```
Optional dependency groups land as features do: `pip install -e ".[parsers]"` (D2 doc parsing), `".[rag]"` (D3 Gemini + Chroma).

## How we build it
**Loop Engineering** (planner → dev → QA agents) on top of a **Context Engineering** docs system, using **Claude Code** + Agent Skills in [.claude/skills/](.claude/skills/). See the [playbook](docs/05-context-engineering/playbook.md).

> The **product** runs on Google Gemini; **Claude Code + Skills** are our development tooling. Two different layers.

## Repo layout
```
src/cue/     backend package: api/, config.py, ingestion/, rag/, rescue/, transcript/, triggers/, sessions/
tests/       pytest suite (mirrors src/cue)
docs/        product, architecture, engineering, agents, delivery, context-engineering
context/     living memory: progress, decisions, tasks, glossary
.claude/skills/  reusable agent procedures
MeetingMinute/   raw intent
```

## Status
Greenfield · Week 1 / Setup. Tech stack proposed in [tech-stack.md](docs/01-architecture/tech-stack.md) (confirm before building).
