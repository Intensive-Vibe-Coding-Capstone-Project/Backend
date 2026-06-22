---
name: plan-feature
description: Planner-agent procedure. Use when starting a new feature/task for Cue — breaks a roadmap goal into ordered, testable steps grounded in the docs, and updates context/active-tasks.md. Trigger words: plan, break down, design the work for, next feature.
---

# Plan a feature (Planner agent)

Turn a goal into an executable plan grounded in this project's context.

## Steps
1. **Load context:** read `CLAUDE.md`, `context/progress.md`, `context/active-tasks.md`, and the relevant `docs/` file(s) (PRD, system-design, conventions).
2. **Clarify the goal:** restate it in one sentence + name the use case it serves (PRD §4). Confirm it's in MVP scope (roadmap / PRD §7); if stretch, say so.
3. **Decompose:** list ordered steps. For each: the files touched, the approach, and a one-line acceptance criterion.
4. **Risks:** note the top 1–3 risks + mitigations (latency, grounding, parser edge cases…).
5. **Acceptance criteria:** define "done" for the whole feature (testable; include grounding + latency where relevant).
6. **Write it down:** add tasks to `context/active-tasks.md` in the format `- [ ] <task> — owner — acceptance`. Do **not** start coding here.

## Output
A short plan (goal, steps, risks, acceptance) + updated `context/active-tasks.md`. Hand off to the Dev agent.

## Guardrails
- Keep features small — one trip around the loop. If big, split.
- Everything must trace to a doc; if a needed fact is missing, flag it instead of inventing.
