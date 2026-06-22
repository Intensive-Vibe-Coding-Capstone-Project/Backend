---
name: kaggle-writeup
description: Assemble the Kaggle submission writeup for Cue from existing project artifacts (PRD, architecture, demo, eval results). Use near submission (D13) or to refresh the draft. Trigger words: kaggle, submission, writeup, submit the project, competition entry.
---

# Generate the Kaggle writeup

Build the submission from artifacts that already exist — don't invent; pull and summarize.

## Sources to read
- `docs/00-product/PRD.md` (problem, users, use cases, scope, metrics)
- `docs/01-architecture/system-design.md` + `tech-stack.md` (how it works)
- `docs/03-agents/loop-overview.md` (Loop Engineering — a course differentiator)
- `docs/04-delivery/demo-script.md` (demo) + latest eval/latency numbers from QA
- `docs/04-delivery/kaggle-submission.md` (the template to fill)

## Steps
1. Fill each section of `kaggle-submission.md` from the sources above; keep prose tight and concrete.
2. Emphasize the **AI agent design** + **Loop/Context Engineering** story — include the diagrams.
3. Reproducibility: list pinned deps, env vars (→ Kaggle Secrets), sample docs, run steps, model ids, seeds.
4. Insert real results: grounding rate, latency, what worked / limits.
5. Run the submission checklist at the bottom of the template; flag anything missing.

## Output
A completed `kaggle-submission.md` + a checklist of remaining gaps. Don't submit on the user's behalf; surface the final artifact for review.

## Guardrails
- Don't overstate results — report measured numbers only.
- Ensure no secrets/keys are embedded in the notebook or writeup.
