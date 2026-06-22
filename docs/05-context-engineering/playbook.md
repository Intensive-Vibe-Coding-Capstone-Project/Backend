# Context Engineering Playbook

How we feed the *right* information to our agents (Claude during dev; Gemini at runtime) so they produce reliable work. This is the operating manual for everything in `docs/`, `.claude/`, and `context/`.

## 1. The three levels (your framing)

1. **Prompt Engineering** — craft a single good instruction.
2. **Context Engineering** — curate the *whole* working set an agent sees: docs, conventions, state, tools, examples. ← *this folder system lives here.*
3. **Loop Engineering** — agents iterate in a loop (plan → dev → QA → repeat) with context updated each cycle. ← *see `docs/03-agents/loop-overview.md`.*

Good Loop Engineering is impossible without good Context Engineering. This system is the substrate.

## 2. The artifact system (what lives where)

| Layer | Folder | Changes… | Purpose |
|-------|--------|----------|---------|
| **Entry context** | `CLAUDE.md` | rarely | Always-loaded map. Short & true. |
| **Stable knowledge** | `docs/` | per decision | PRD, architecture, conventions, agent specs, delivery. The "why/what/how". |
| **Living memory** | `context/` | every session | progress, decisions log, active tasks, glossary. The "where we are now". |
| **Procedures** | `.claude/skills/` | per workflow | Reusable, named, on-demand instructions ("how to do X here"). |
| **Raw intent** | `MeetingMinute/` | as captured | Source of truth for what was actually agreed. |

**Progressive disclosure:** `CLAUDE.md` is always loaded; everything else is pulled *on demand* by the agent (or by a skill) when relevant. This keeps the context window focused and cheap.

**One source of truth:** each fact lives in exactly one place; everywhere else links to it. Stale duplication is the main failure mode — avoid it.

## 3. Decision: do we need `skill-creator`?

**`skill-creator`** (github.com/anthropics/skills) is a meta-skill that *helps you author Agent Skills* — it scaffolds the folder, writes a valid `SKILL.md`, and packages it.

- **Necessary?** No. A Skill is just a folder with a `SKILL.md` (YAML frontmatter: `name`, `description` + a markdown body). You can hand-write them — we already did (`.claude/skills/`).
- **Useful?** Yes, as an accelerator/teacher when you create several skills or want them validated/packaged. Recommended to **install it once and use it to bootstrap or audit** new skills, then maintain by hand.
- **Scope caveat:** Agent Skills are a **Claude/Anthropic feature → they serve our *development* loop**, not the shipped Gemini product. Don't try to ship them inside Cue; the product's "agents" are Gemini tools/sub-agents.

**Verdict:** Adopt **Skills** (high value for the loop). Treat **`skill-creator`** as an optional convenience — install it to scaffold/validate, but don't depend on it.

## 4. When to write a Skill vs a doc

- **Doc (`docs/`)** = knowledge you *read* (facts, decisions, specs).
- **Skill (`.claude/skills/`)** = a *procedure you repeat* ("create a new RAG endpoint", "run the QA gate", "generate the Kaggle writeup"). If you've explained "how to do X here" twice, make it a skill.

## 5. The session loop (do this every work session)

1. **Load:** read `CLAUDE.md` → `context/progress.md` → relevant `docs/`.
2. **Plan:** use `/plan-feature` to break the task into steps grounded in the docs.
3. **Build:** implement following `docs/02-engineering/conventions.md`.
4. **Verify:** run `/qa-review` (tests + grounding + latency gate).
5. **Close the loop:** update `context/progress.md`; append decisions to `context/decisions-log.md`; add an ADR if architectural; update `docs/` if a fact changed.

## 6. How this serves every downstream goal

- **Development:** consistent context → faster, less-broken agent output.
- **Kaggle submission:** `docs/04-delivery/kaggle-submission.md` + skills assemble the writeup from existing artifacts.
- **Deployment:** architecture + ADRs + setup docs are deployment-ready.
- **Onboarding:** a new member reads `CLAUDE.md` → `docs/` → `context/progress.md` and is current in ~30 min.
- **Release / promotion:** PRD + demo script + use cases are the raw material for the landing page and pitch.
