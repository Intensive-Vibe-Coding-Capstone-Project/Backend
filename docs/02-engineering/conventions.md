# Engineering Conventions

> All code (human or agent) follows this. Keep it short; link out for detail.

## Language & layout
- Python 3.11+, FastAPI. `src/cue/` package; `tests/` mirrors it.
- Modules: `ingestion/`, `rag/`, `rescue/`, `transcript/`, `triggers/`, `sessions/`, `api/`, `config.py`.

## Style
- Format with `ruff format`; lint with `ruff`. Type hints required on public functions.
- Names: clear over clever. No abbreviations except well-known (id, db, llm).
- Functions small and single-purpose; push I/O to the edges, keep core logic pure/testable.

## Config & secrets
- All config via `pydantic-settings` from `.env`. **Never commit keys.** Provide `.env.example`.
- Model ids, k, chunk size, thresholds = config, not magic numbers.

## LLM / RAG rules
- Generation must be **grounded**: pass retrieved passages; instruct "answer only from context; if unsupported, return a safe bridge line."
- Always return citations (doc id + passage) with a rescue script.
- Default model: Gemini Flash for rescue; escalate to Pro only when needed.

## API
- REST: nouns + verbs per `system-design.md`. Validate with pydantic models. Consistent error shape `{error, detail}`.
- Realtime via WebSocket; stream tokens where it cuts perceived latency.

## Testing
- `pytest`. Every feature ships with unit tests. RAG features also add to the grounding eval set.
- Acceptance criteria (from the planner) must be met before QA passes.

## Git
- Branch per feature off `main`. Small commits. Conventional-ish messages.
- No commit/push unless asked. Don't skip hooks.

## Definition of Done
1. Code + tests pass. 2. Grounded + within latency. 3. `context/progress.md` updated. 4. Docs/ADR updated if a fact/decision changed.
