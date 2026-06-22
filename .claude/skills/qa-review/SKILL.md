---
name: qa-review
description: QA-agent gate for Cue. Use after a code change to verify tests, grounding, and latency before merge or Kaggle submission. Trigger words: QA, review change, verify, is this done, acceptance check, gate.
---

# QA review (QA agent — the gate)

Independently verify a change meets the Definition of Done before it merges.

## Steps
1. **Load criteria:** read the feature's acceptance criteria (`context/active-tasks.md`) + `docs/02-engineering/conventions.md` (Definition of Done).
2. **Run tests:** execute `pytest`. All green? List any failures with the exact output.
3. **Grounding check (RAG features):** run the grounding eval set — do answers come only from the uploaded docs, with citations? Flag any hallucination or unsupported claim. A rescue with no support must return a safe bridge line, not invented facts.
4. **Latency check:** measure rescue path; must be within ~4s (PRD §8). Report numbers.
5. **Edge cases:** empty/huge docs, unsupported file type, no retrieval hits, very long transcript window, concurrent sessions.
6. **Verdict:** PASS or FAIL. On FAIL, file a concise issue list back to Dev (what, where, expected vs actual).

## Output
PASS/FAIL + evidence (test output, grounding rate, latency) + issue list. Report faithfully — never claim pass on unrun or failing tests.

## Guardrails
- Don't fix code here; you are the independent check. Bounce issues to the Dev agent.
- Nothing ships to Kaggle without a PASS on the full eval set.
