# Cue — Test & Demo Runbook: "AuroraBuds Pro" livestream

A self-contained scenario that exercises **all 4 PRD use cases** and every trigger, with expected outputs. The product is **fictional on purpose** — the only correct answers live in the uploaded docs, so a right answer *proves* grounding (the model can't fall back on training data).

## The scenario
You are a KOL doing a **TikTok Shop livestream** selling **AuroraBuds Pro** wireless earbuds (by fictional "Lumen Audio"). You uploaded your spec sheet, FAQ, and campaign notes. During the stream you hit hard buyer questions, almost name the wrong shopping channel / a competitor, and drift off-script — Cue rescues each.

## Materials (upload these)
- `01-aurorabuds-spec.txt` — specs (battery, ANC, latency, water rating, Adaptive Sound Map…)
- `02-aurorabuds-faq.txt` — warranty, returns, fit, gym use, compatibility…
- `03-aurorabuds-campaign.txt` — TikTok-Shop-exclusive, price, voucher, offers
- `prepared-script.txt` — your intended livestream open (bind this to the session for slip detection)

**Forbidden terms** (the brands/channels you must NOT say on stream): `Shopee`, `Lazada`, `AirPods`, `Sony`

---

## Setup
```bash
pip install -e ".[dev,parsers,rag]"
cp .env.example .env        # put your GEMINI_API_KEY in .env
# Demo pacing: make auto-triggers fire fast but stay under the 5-req/min free-tier cap
#   (PowerShell)  $env:CUE_SCAN_INTERVAL_S = "12"
#   (bash)        export CUE_SCAN_INTERVAL_S=12
cue                         # serves http://127.0.0.1:8000  (UI at /ui)
```
> Live calls use Gemini Flash. **Free tier = 5 generate/min.** Each rescue or slip-correction = 1 call, so space them ~12s+ apart (or record in takes). Without a key, everything runs on deterministic fakes — good for a dry run, but answers won't be "real".

---

## Walkthrough (UI at http://127.0.0.1:8000/ui/)

### 0. Index your material
**Panel 1 · Upload** → upload all three `.txt` docs. Each shows as indexed with a chunk count.

### 1. Use case 1/2 — hard question (manual rescue)
**Panel 2 · Start session.** Then **Panel 3 · Ask** these one at a time (expected grounded answer in parentheses):

| Ask | Expected (grounded, from docs) |
|---|---|
| How long does the battery last, and how much with the case? | 9h per charge (7h ANC on), **32h with the case** |
| Are these okay for the gym or running in the rain? | **IPX5** sweat/splash resistant, secure fit, **not** for swimming |
| What actually makes the sound "personalized"? | **Adaptive Sound Map** — 10-sec ear scan tunes the EQ |
| What's the latency for mobile gaming? | **Game Mode 38 ms** via the Lumen L1 chip |
| What warranty and return window do I get? | **18-month** warranty; **14-day** returns |
| Do all the features work on iPhone? | Yes — BT 5.3; Adaptive Sound Map/EQ via the **Lumen app** on iOS & Android |

✅ **Pass = each renders line-by-line (karaoke), `grounded` badge is green, and citations point at the right file.** Watch that the numbers match the docs exactly (that's true grounding, not a guess).

### 2. Bind your script (enables slip detection)
**Panel 4 · Prepared script** → paste `prepared-script.txt`, set **Forbidden terms** to `Shopee, Lazada, AirPods, Sony`, Save.

### 3. Go live
**Panel 5 · Live transcript (WS)** → **Connect.** Now type spoken lines as if talking.

**Use case 3 — brand/channel slip.** Type:
> `Honestly these sound better than the AirPods, and you can grab them on Shopee too!`

Click **Check slip** → expect a **correction** (`kind: brand`, `wrong_terms: [AirPods, Shopee]`) steering you back to AuroraBuds on TikTok Shop. ✅

**Use case 4 — flow break (off-script).** (Reconnect or let the window roll so chit-chat dominates.) Type:
> `Oh by the way, did anyone catch the football last night? It went to penalties and I forgot to set my alarm this morning.`

Click **Check slip** → expect a **correction** (`kind: off_flow`) nudging you back to the prepared script. ✅
> Why it fires: this line shares <30% of its words with your script (the off-flow threshold).

**Keyword auto-trigger.** Type a stumble that still mentions the product:
> `Hmm, that's a really good question — what's the battery again?`

Within one scan interval, expect a pushed **rescue** with `mode: keyword`. ✅

**Silence auto-trigger.** Stop typing for >10s while connected → within a scan, expect a pushed **rescue** with `mode: silence` on the last window. ✅

**Manual trigger.** Click **Rescue now** any time → pushed **rescue** with `mode: manual`. ✅

### 4. History
**Panel 6 · Session history** → every rescue turn recorded with its citations. ✅

---

## The honest edge case (test privately — do NOT put in the public video yet)
**Off-topic probe.** Ask something with no support in the docs:
> `What's a good recipe for chocolate-chip cookies?`

**Expected:** a safe **bridge** line ("I don't have that in your notes…"), `grounded` = false, no invented facts.
**Reality today:** this is Cue's known weak spot — the D12 live eval measured **85%**, because off-topic questions leak past the guard about **1 in 3** times and get a confident-looking answer. Probe it a few times; if you see a made-up answer, that's the exact defect we're fixing next (strengthen the refusal guard + add a post-generation relevance check). Keep it out of the public demo until it's green.

---

## API / WebSocket equivalents (for precise/automated testing)
```bash
# Upload
curl -F "file=@samples/aurorabuds/01-aurorabuds-spec.txt" http://127.0.0.1:8000/documents
# (repeat for 02 and 03)

# Start a session  ->  copy the returned "id"
curl -X POST http://127.0.0.1:8000/sessions -H "Content-Type: application/json" -d '{"title":"AuroraBuds livestream"}'

# Hard question (records the turn in the session)
curl -X POST http://127.0.0.1:8000/rescue -H "Content-Type: application/json" \
  -d '{"session_id":"<ID>","question":"How long does the battery last, and how much with the case?"}'

# Bind the prepared script + forbidden terms (204 No Content on success)
curl -X PUT http://127.0.0.1:8000/sessions/<ID>/script -H "Content-Type: application/json" \
  -d '{"text":"<paste prepared-script.txt>","forbidden_terms":["Shopee","Lazada","AirPods","Sony"]}'
```
**WebSocket** `ws://127.0.0.1:8000/stream/<ID>` — send JSON:
- `{"text":"...spoken words..."}` → ack `{type:"ack", segments, window_chars, silence_s, last_ts}`
- `{"type":"trigger"}` → `{type:"rescue", mode:"manual", lines, grounded, citations}` (or `{type:"none"}`)
- `{"type":"check_slip"}` → `{type:"correction", kind, wrong_terms, lines, message}` (or `{type:"none"}`)
- The server also pushes `rescue` (mode `periodic`/`keyword`/`silence`) and `correction` on its own every `CUE_SCAN_INTERVAL_S`.

---

## ~3-minute YouTube storyboard
1. **Hook (15s):** "Ever frozen on a question mid-livestream? Cue answers in your own words." 
2. **Setup (20s):** upload the 3 docs → "indexed".
3. **Hard question (40s):** ask the gym/water question → grounded lyric script + citation; read it aloud. (Pick the answer that best shows a doc-specific fact, e.g. IPX5 or 38 ms.)
4. **Slip (40s):** bind script → type the "AirPods / Shopee" line → correction appears.
5. **Under the hood (30s):** show the architecture + Loop-Engineering diagram — "built by agents, context-engineered."
6. **Close (15s):** impact + what's next.

> Capture the latency on screen. Keep ~12s between live calls to respect the 5/min cap, or stitch clean takes.
