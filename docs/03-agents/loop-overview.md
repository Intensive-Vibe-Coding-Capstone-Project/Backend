# Loop Engineering — Dev Agents Overview

We build "Cue" using a 3-agent loop. **These agents build the app; they are not the app.** They run inside Claude Code, guided by this docs system and the skills in `.claude/skills/`.

## The loop

```
   ┌──────────┐     plan      ┌──────────┐    code     ┌──────────┐
   │ PLANNER  │ ───────────▶ │   DEV    │ ─────────▶ │    QA    │
   └──────────┘               └──────────┘             └────┬─────┘
        ▲                                                   │ pass/fail
        │            update context (progress, decisions)   │
        └───────────────────────────────────────────────────┘
```

One trip around the loop = one feature/task from `context/active-tasks.md`.

## Roles

### 1. Planner agent
- **Input:** a goal from the roadmap + current `context/progress.md`.
- **Does:** break it into ordered, testable steps; identify files, risks, acceptance criteria; ground each step in `docs/`.
- **Output:** a task plan + updated `context/active-tasks.md`.
- **Skill:** `/plan-feature`.

### 2. Dev agent
- **Input:** the plan.
- **Does:** implement following `docs/02-engineering/conventions.md`; write code + unit tests; keep changes scoped.
- **Output:** working code + tests + a short change note.
- **Skill:** `/rag-endpoint` (and feature-specific skills as we add them).

### 3. QA agent
- **Input:** the change + acceptance criteria.
- **Does:** run tests; check **grounding** (answers come from docs), **latency** (<~4s), edge cases; verify the acceptance criteria. Files bugs back to Dev.
- **Output:** pass/fail + issue list; gate before merge/submit.
- **Skill:** `/qa-review`.

## Loop rules

- Don't start Dev without a Planner plan; don't merge without a QA pass.
- After every loop: **update `context/progress.md`**; log decisions in `context/decisions-log.md`.
- Keep loops small — one task, one trip. Big tasks → split in Planner.
- The roadmap (`docs/04-delivery/roadmap.md`) sets the day's targets; the loop executes them.
