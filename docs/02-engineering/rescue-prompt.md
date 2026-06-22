# Rescue Prompt — v1 (D4)

> Single source of truth for how Cue turns retrieved passages + a question into a
> grounded, speakable rescue script. The code in `src/cue/rescue/prompt.py`
> mirrors this file — change them together.

## Goal

Given the speaker's question (or repeated audience question) and the top-k
passages retrieved from their own uploaded documents, produce a **short,
ready-to-speak rescue script** that is **grounded only in those passages** and
shown **line by line** (karaoke / lyric style).

## Hard rules (grounding)

1. **Answer only from the provided passages.** Do not use outside knowledge.
2. If the passages do **not** support an answer, **do not invent one.** Return a
   safe **bridge line** that buys time without asserting unsupported facts
   (e.g. "That's a great question — let me come back to it with the exact detail
   in a moment.").
3. **Cite** the passages used by their `[n]` marker.
4. Keep it **speakable**: short lines, plain spoken language, no markdown, no
   bullet characters, no stage directions. 2–6 lines, each a breath-sized phrase.
5. Stay on the speaker's side and on-message; never contradict their material.

## Inputs assembled by the code

- `question` — the typed/repeated question.
- `passages` — numbered `[1..k]`, each `"[n] (source: <filename>) <text>"`.
- (Later: prepared-script + transcript window for slip/flow detection — D10.)

## Prompt shape

**System instruction:**

```
You are Cue, a real-time presentation rescue assistant. A speaker needs a short,
confident, ready-to-speak answer grounded ONLY in the provided source passages.
Rules:
- Use ONLY the passages. Never add outside facts.
- If the passages do not support an answer, reply with a brief bridge line that
  stalls gracefully WITHOUT inventing facts.
- Output 2-6 short spoken lines, one phrase per line. No markdown, no bullets.
- Be calm, on-message, and concise.
```

**User message:**

```
QUESTION:
{question}

SOURCE PASSAGES:
{numbered_passages}

Write the rescue script now (short spoken lines only).
```

## Output contract

The model returns plain text lines. The orchestrator (`rescue/service.py`):
- splits non-empty lines into `lines[]` and joins them into `script`,
- sets `grounded=True` when retrieval had support (≥ `rescue_min_score`), else
  short-circuits to a **bridge** response (`grounded=False`) **without calling
  the model** when there are no/low-score passages,
- attaches `citations[]` (doc_id, filename, chunk_index, score) for the passages
  shown to the model.

## Tuning knobs (config, not magic numbers)

- `rescue_model` (default `gemini-2.5-flash`) — low latency for the ~4s budget.
- `rescue_temperature` (default `0.3`) — low, for faithful grounded phrasing.
- `retrieval_k` — passages retrieved.
- `rescue_max_passages` — passages actually shown to the model.
- `rescue_min_score` — below this top score → treat as unsupported → bridge.

## Bridge line (no-support fallback)

A fixed, safe line returned without an LLM call:

> "That's a great question — let me give you the precise detail on that in just a moment."
