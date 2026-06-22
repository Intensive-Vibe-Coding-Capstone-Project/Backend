# PRD — "Cue" (Real-time Presentation Rescue Agent)

Status: Draft v1 · Owner: team · Source: `MeetingMinute/21_6_2026.md`

## 1. Problem

People who present, sell live, or record content prepare heavily, but get caught off-guard by:
- a hard / unexpected audience question (mid-talk or in Q&A),
- saying the wrong thing (e.g. a KOL naming the wrong brand — "Shopee" instead of "TikTokShop"),
- losing the script / breaking the intended flow while recording.

Today they freeze, or stall while they manually search an AI chatbot. We remove that gap.

## 2. Solution

An AI agent that already knows the user's prepared material (RAG over their uploaded docs) and listens to the talk. When a rescue is needed it returns a short, logical, **ready-to-speak script**, displayed line-by-line like song lyrics so it's easy to read aloud.

## 3. Users / personas

- **Student presenter** — defends a final project; needs grounded answers to deep follow-up questions.
- **Office worker** — pitches/reports; needs to stay on-message under pressure.
- **Content creator / KOL** — live selling or recording; needs instant correction of slips and flow.

## 4. Core use cases (from meeting)

1. **Hard question mid-talk** — after slide 5/15 someone asks a deep domain question. Presenter repeats the question aloud; app sends it to the agent (which has the prepared context) and returns the next lines to say.
2. **Hard question in Q&A** — same, after the full talk.
3. **Live-sale slip** — periodic scan (~30s) detects the spoken brand name diverges from the prepared script → warns + provides a correction line.
4. **Recording flow break** — creator forgets/misstates the script → app detects and suggests how to recover or re-shoot the beat.

## 5. Trigger model (when does the agent fire?)

- **Manual** — user presses a "rescue" button (most reliable; MVP default).
- **Periodic** — analyze the last window of speech every ~30s.
- **Keyword/phrase** — "Hmm, that's a good question", "Let me check that", "That's an interesting question"…
- **Silence** — speaking pauses > ~10s.

## 6. Features

- Upload & parse documents: **pdf, docx, txt, epub, ppt/pptx**.
- RAG over uploaded docs (chunk → embed → retrieve).
- Gemini-style chat UI.
- Conversation / session history.
- Real-time voice: speech → text → grounded answer.
- Signal detection (keywords / silence / periodic) to decide when to generate a rescue.
- Rescue script rendering: one paragraph, split into easy-to-read lines.

## 7. Scope for the 2-week capstone

**In (MVP):** doc upload+parse, RAG index, session model, **manual + periodic** trigger, rescue-script generation grounded in docs, lyric-style rendering, history. STT via a streaming-capable API.

**Stretch (if time):** keyword + silence auto-triggers, fully live bi-directional audio, multi-language, fine-tuned signal detection, auth/multi-user polish.

**Out (post-capstone):** payments, team workspaces, mobile app, offline mode.

## 8. Success metrics

- Rescue script returned in **< ~4s** after trigger.
- Answers are **grounded** (cite/derive from uploaded docs) in ≥ ~90% of test prompts.
- End-to-end demo runs all 4 use cases without manual fixups.
- Kaggle submission complete with writeup + reproducible notebook/demo.

## 9. Open questions

- Exact Gemini model(s) + STT service — see `docs/01-architecture/tech-stack.md`.
- Vector store choice for the Kaggle-reproducible build.
- Team size / role split — fill into `docs/04-delivery/roadmap.md`.
