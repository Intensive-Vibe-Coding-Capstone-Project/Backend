# 🎬 Youtube_demo.md — Recording guide for the "Cue" ad demo

A careful, camera-ready script to record a ~2–3 minute advertisement-style demo of **Cue**, using the **AuroraBuds Pro** scenario in [samples/aurorabuds/](samples/aurorabuds/). Follow it top to bottom: pre-flight → record scene by scene → tips → publish.

> **The story you're selling:** a creator doing a TikTok Shop livestream gets hit with a hard question and *almost says the wrong brand* — and Cue rescues them in real time, in their own words, grounded in their own docs. The **"make a mistake on purpose"** beat (Scene 4) is the centerpiece.

---

## Part A — Pre-flight (do this BEFORE you hit record)

### A1. Environment
```bash
pip install -e ".[dev,parsers,rag]"
cp .env.example .env          # put a WORKING GEMINI_API_KEY in .env
```

### A2. Clean slate (so the History panel isn't cluttered with old runs) — non-destructive
Point the DB + index at fresh demo folders instead of deleting anything:
```powershell
# PowerShell
$env:CUE_DB_PATH     = "$PWD\demo\cue.db"
$env:CUE_CHROMA_DIR  = "$PWD\demo\chroma"
$env:CUE_SCAN_INTERVAL_S = "12"   # auto-triggers fire in ~12s, not 30s — watchable on camera
cue
```
```bash
# bash equivalent
export CUE_DB_PATH=./demo/cue.db CUE_CHROMA_DIR=./demo/chroma CUE_SCAN_INTERVAL_S=12
cue
```
Open **http://127.0.0.1:8000/** (redirects to the `/ui` demo page).

### A3. Quota & pacing (READ THIS — it's the #1 thing that ruins a take)
- Free tier = **5 Gemini calls/minute**. Every **rescue** and every **slip correction** is **1 call**.
- This demo makes ~4–6 live calls. **Leave ~12s between live actions**, or record each scene as its own take. If you rush, you'll get a 429 and Cue will show the safe "bridge" line instead of a real answer.
- Do a **silent rehearsal run first** (off-camera) to warm up — but that burns quota too, so rehearse, then wait ~60s before the real take.

### A4. Safety / do-not-show
- ❌ **Never show `.env`, the terminal line where you paste the key, or `/docs` request samples that echo the key.** Close those tabs.
- ❌ **Do not record the off-topic probe** ("cookie recipe") — it's the known 85% weak spot and may leak a fake answer on camera. Keep it out of the ad.
- 🔁 Rotate the API key after publishing (the screen recording could leak it if you're not careful).

### A5. Recording setup
- **Screen recorder:** OBS / built-in. 1080p, 30fps. Capture **system audio off** (or low) so only your voiceover is heard, unless you want the click sounds.
- **Browser zoom:** Ctrl+ `+` to ~125–150% so the karaoke lines and the green **grounded** / red **alert** badges read clearly on small screens.
- **Window:** just the browser, full-screen, no bookmarks bar, no other tabs. Use a clean profile.
- **Mic:** record voiceover live, or narrate in post. Aim for an upbeat, confident "ad" tone.
- Have this file open on a second monitor / phone to follow along.

### A6. 🎤 Real-time speaking (the live voice input)
The live panel now has a **🎤 Speak** button (browser speech recognition → streamed straight into Cue).
- Use **Chrome or Edge** (the API isn't in Firefox). The first click asks for **microphone permission** — allow it *before* recording so the prompt isn't on camera.
- **Connect** the WS first; then click **🎤 Speak** (it turns red and pulses). Talk normally — words preview in the box, and each finished phrase is sent automatically (no Enter needed). Click **🛑 Stop** to end.
- Speak clearly at a normal pace; pause briefly between sentences so each phrase finalizes cleanly.
- You can still **type** a line and hit Send/Enter for precise, repeatable takes — mix both as you like.

---

## Part B — The recording script (scene by scene)

Total target: **~2:30**. Each scene lists: **[Action]** what you do on screen · **[Say]** voiceover · **[See]** what must appear for a good take · **[~time]**.

### Scene 0 — Hook (problem) · ~12s
- **[Action]** Open on the clean `/ui` page (or a quick shot of a creator on a livestream — stock/B-roll optional).
- **[Say]** *"You're live. Someone drops a hard question — or you blank on a detail. You freeze. What if you had a teleprompter that actually knows your product… and writes your next line in real time?"*
- **[See]** The Cue title and the clean panels.

### Scene 1 — Upload your material · ~18s
- **[Action]** **Panel 1 · Upload** → add all three files: `01-aurorabuds-spec.txt`, `02-aurorabuds-faq.txt`, `03-aurorabuds-campaign.txt`.
- **[Say]** *"First, I give Cue my own material — my spec sheet, my FAQ, my campaign notes. It reads and indexes everything in seconds."*
- **[See]** Each doc appears as **indexed** with a chunk count. ✅ *(zoom in on the chunk counts)*

### Scene 2 — Start the session · ~8s
- **[Action]** **Panel 2 · Start session** (title it `AuroraBuds livestream`).
- **[Say]** *"I start my livestream session…"*
- **[See]** A session id / "session started".

### Scene 3 — The hard question (the "wow") · ~30s
- **[Action]** **Panel 3 · Ask** → paste **one** question (pick the most impressive — the gym/water one is great because the IPX5 detail is clearly from *your* doc):
  > `Are these okay to wear at the gym or running in the rain?`
- **[Say]** *"A viewer asks if they're gym-proof. I don't scramble — I press rescue."*
- **[See]** A **grounded** (green badge) script renders **line by line, karaoke style** — mentioning **IPX5 / sweat resistant / not for swimming** — with a **citation** chip pointing at the FAQ doc. ✅
- **[Say, reading the lines aloud]** *"…and Cue feeds me the exact words — from MY docs, with the source. That's IPX5 sweat resistance, secure fit, just not for swimming."*

> 💡 Capture the response time on screen if you can — it lands around ~4s.

### Scene 4 — ⭐ Make a mistake ON PURPOSE (the centerpiece) · ~35s
First bind your script so Cue knows what "on-message" means:
- **[Action]** **Panel 4 · Prepared script** → paste the contents of `prepared-script.txt`; set **Forbidden terms** to:
  > `Shopee, Lazada, AirPods, Sony`
  Save.
- **[Say]** *"Here's the magic. I tell Cue my script — and the brands I must NOT say on a TikTok Shop exclusive. Now watch me slip up on purpose."*
- **[Action]** **Panel 5 · Live transcript (WS)** → **Connect** → click **🎤 Speak** and *say the slip line out loud* (or type it), then click **Check slip**:
  > `Honestly these sound way better than the AirPods, and you can grab them on Shopee too!`
- **[See]** A red **alert/correction** appears — `kind: brand`, flagging **AirPods** and **Shopee** — with a calm on-message correction line steering back to AuroraBuds on TikTok Shop. ✅
- **[Say]** *"Instantly — Cue catches it. Wrong channel, wrong brand, and it hands me the on-message fix. No awkward pause, no lost sale."*

### Scene 5 — (Optional) Drift off-script · ~20s
- **[Action]** Still in **Panel 5**, *say* (🎤) an off-topic ramble and **Check slip**:
  > `Oh by the way, did anyone catch the football last night? It went to penalties and I forgot my alarm.`
- **[See]** A correction with `kind: off_flow` — *"let's get back on track, return to your prepared script."* ✅
- **[Say]** *"Ramble off-script? It nudges me right back."*

### Scene 6 — (Optional) Under the hood · ~20s
- **[Action]** Cut to the architecture + Loop-Engineering diagrams (from [docs/01-architecture/system-design.md](docs/01-architecture/system-design.md) and [docs/03-agents/loop-overview.md](docs/03-agents/loop-overview.md)). Optionally show a keyword auto-trigger: type `Hmm, that's a really good question — what's the battery again?` and let it auto-push a `mode: keyword` rescue.
- **[Say]** *"Under the hood: retrieval over your docs, grounded generation with Google Gemini, triggers for button, silence, and keywords — and it was built agent-first with a planner/dev/QA loop."*
- **[See]** Diagrams; (optional) an auto-pushed rescue card.

### Scene 7 — Close / call to action · ~12s
- **[Say]** *"Cue. Your real-time rescue, grounded in your own words. Never freeze on stage again."*
- **[Action]** End card: product name + one-liner + repo/Kaggle link.

---

## Part C — Copy-paste inputs (exact)

**Hard question (Scene 3):**
```
Are these okay to wear at the gym or running in the rain?
```
**Backup questions (if you want more takes):**
```
What actually makes the sound "personalized"?
How long does the battery last, and how much with the case?
What's the latency for mobile gaming?
```
**Forbidden terms (Scene 4):**
```
Shopee, Lazada, AirPods, Sony
```
**Brand-slip line (Scene 4):**
```
Honestly these sound way better than the AirPods, and you can grab them on Shopee too!
```
**Off-script line (Scene 5):**
```
Oh by the way, did anyone catch the football last night? It went to penalties and I forgot my alarm.
```
**Prepared script (Scene 4):** paste the full contents of [samples/aurorabuds/prepared-script.txt](samples/aurorabuds/prepared-script.txt).

---

## Part D — Recording & pacing tips
- **One scene = one take.** Record Scenes 3, 4, 5 separately with a ~12s gap between live calls; stitch in editing. This dodges the 5-calls/min cap entirely.
- **Watch the badge color**, not just the text: green **grounded** = good take; if you see the generic **bridge** line on an on-topic question, you hit a 429 — wait 60s and retry.
- **Expected latency** is ~4s; don't cut it out — showing the real wait builds trust. You can speed-ramp it 1.5× in post if it drags.
- Keep mouse movements slow and deliberate; pause on the citation chip and the badges so viewers register them.

## Part E — If something goes wrong (fallbacks)
- **429 / "bridge" line on a real question:** quota hit. Wait ~60s; or switch to a billed key; or record that scene later.
- **Gemini outage / weird answer:** re-run; the answer varies slightly (temp 0.3). Pick the cleanest take.
- **Totally stuck on live calls:** you can still demo upload + indexing + the live slip-detection UI (slip detection is *lexical*, so the brand/off-flow catch works even without a great generation) — the correction text falls back to a templated line.

## Part F — Post-production & publishing
- **Captions/subtitles:** add them — most social viewers watch muted.
- **On-screen labels:** pop a small caption per scene ("Upload your docs", "Ask anything", "Caught the slip in real time").
- **Latency overlay:** optionally show the ~4s timer to prove it's live.
- **Music:** upbeat, low under the voiceover.
- **Length:** a tight **60–90s** cut for ads/social; keep the **~2:30** full version for the Kaggle/YouTube writeup.
- **Title ideas:** "Cue — never freeze on a question mid-livestream" · "An AI teleprompter that knows YOUR product".
- **Description:** one-liner + "grounded in your own documents, powered by Google Gemini" + repo/Kaggle link. **Do not** paste any API key.

---

### Honesty note (for you, not the viewer)
Everything above showcases Cue's **strong** path — grounded answers on real content (measured 10/10) and live slip detection. The one thing we deliberately **don't** film is the off-topic refusal (currently ~85%, leaks ~1/3). Once that fix lands and the eval clears ≥90%, you can safely add an "ask it something irrelevant → it refuses honestly" beat, which is itself a great trust-building scene.
