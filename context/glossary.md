# Glossary

- **Cue** — our product codename (real-time presentation rescue agent).
- **Rescue script** — the short, ready-to-speak answer the agent returns, rendered line-by-line.
- **Trigger** — what makes the agent fire: manual button, periodic 30s scan, keyword, or silence.
- **Grounding** — answering only from the user's uploaded docs (via RAG), never invented.
- **Slip detection** — noticing the spoken transcript diverges from the prepared script (e.g. wrong brand).
- **RAG** — Retrieval-Augmented Generation: retrieve relevant passages, then generate with them.
- **Loop Engineering** — building via a plan→dev→QA agent loop with context updated each cycle.
- **Skill** — a reusable, named procedure for our dev agents, in `.claude/skills/`.
- **Lyric/karaoke rendering** — splitting the answer into one line per phrase for easy reading aloud.
