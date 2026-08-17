# EDITH — Engineer-First UX + Plain-Language Content System
**Date:** 2026-06-10
**Author:** product-manager-agent (Jarvis specialist)
**Status:** Build-ready spec — frontend engineer implements this verbatim
**Audience:** Maintenance engineers at Indian steel plants (shift-based, practical, engineering-trained, not data-science trained)
**Make-or-break criterion (client-stated):** Every engineer must always understand what EDITH is telling them. If an engineer feels lost, the project fails.

---

## 0. TL;DR

EDITH currently speaks ML. Engineers speak maintenance. This spec defines the translation layer, the guided answer structure, the proactive copilot, the three missing features (Start Here / Downstream Impact / Feedback), and the one-screen information architecture. The result: an engineer who picks up the dashboard cold understands what's wrong, how urgent it is, what to do, and what parts they need — without asking a single question.

---

## 1. Engineer Jobs-to-be-Done

These are the six questions a maintenance engineer asks, in urgency order. Every EDITH feature maps to one of them.

| Priority | Job (the real question) | Current EDITH coverage | This spec adds |
|---|---|---|---|
| J1 | "Which machine do I look at first?" | None — engineer scans the strip manually | START HERE banner with ranked reason |
| J2 | "Is this machine OK right now?" | Health strip (green/yellow/red) — no plain-language reason | VERDICT header: 1-line status + cause |
| J3 | "How long do I have and what happens if I wait?" | RUL in cycles, no time unit, no consequence | Plain-language urgency ("14 days, or bearing seizes") |
| J4 | "What exactly do I do, step by step?" | Numbered steps exist — sometimes jargon-heavy | Plain imperative steps, max 3 visible, expand for more |
| J5 | "What parts do I need and are they in stock?" | In the card but not prominently surfaced | Parts mini-table always-visible in ACT NOW state |
| J6 | "What downstream trouble am I preventing?" | Not surfaced at all | Inline downstream impact line, data-gated |

**Design rule:** J1 is answered before the engineer touches anything. J2 is answered in 1 second. J3–J5 are answered without a scroll. J6 is there when they need justification to escalate.

---

## 2. Plain-Language Content System

### 2.1 Voice Definition

EDITH speaks like a senior maintenance colleague — experienced, calm, direct, never alarmist, never hedging.

**Voice rules (non-negotiable):**
- **Short sentences.** Max 15 words per sentence. Two sentences > one compound sentence.
- **Imperative verbs for actions.** "Lubricate the bearing" not "It is recommended to apply lubricant."
- **Present-tense status.** "Bearing is wearing" not "Bearing wear has been detected."
- **No passive voice** in VERDICT or steps.
- **No confidence-hedging in headlines.** Not "may possibly indicate." If the model says 87% — write "Bearing wear detected (high confidence)." Confidence scores go in technical details.
- **Context on every number.** Never "78°C" alone. Always "78°C — 3°C above the alarm limit (75°C)."
- **No jargon in headlines.** BPFO, anomaly_score, FFT, ISO codes: they belong in "Why (technical details)" only.
- **Avoid negatives.** "Replace within 14 days" not "Do not delay replacement past 14 days."

### 2.2 Jargon-to-Plain-Language Translation Table

This table is the content system. Frontend renders the plain-language string. Technical original is available in the "Why" expand section only.

| Original (what the ML/sensor system produces) | Plain-language render (what the engineer reads) | Technical term placement |
|---|---|---|
| `RUL: 1014 cycles` | `~42 days of safe run-time remaining` | "Why" section: "RUL 1014 cycles at current load" |
| `RUL: 240 cycles` | `~10 days of safe run-time remaining` | "Why" section |
| `RUL: 48 cycles` | `~2 days of safe run-time remaining — act today` | "Why" section |
| `fault_class: outer_race_fatigue_spall_BPFO` | `Outer-race bearing wear (fatigue pitting)` | "Why" section: fault_class label |
| `fault_class: inner_race_defect_BPFI` | `Inner-race bearing damage` | "Why" section |
| `fault_class: rolling_element_defect_BSF` | `Rolling-element (ball) bearing damage` | "Why" section |
| `fault_class: cage_defect_FTF` | `Bearing cage wear` | "Why" section |
| `fault_class: gear_mesh_wear` | `Gear-tooth wear` | "Why" section |
| `fault_class: unbalance` | `Shaft imbalance` | "Why" section |
| `fault_class: misalignment` | `Shaft misalignment` | "Why" section |
| `fault_class: lubrication_starvation` | `Insufficient lubrication` | "Why" section |
| `anomaly_score: 0.87` | `Unusual behaviour detected (high confidence)` | "Why" section: anomaly score |
| `anomaly_score: 0.62` | `Unusual behaviour detected (moderate confidence)` | "Why" section |
| `anomaly_score: 0.41` | `Minor deviation from normal — monitor` | "Why" section |
| `BPFO: 3.2× nominal` | `Bearing vibration is 3× the safe limit` | "Why" section: BPFO value |
| `temperature: 78°C (alarm: 75°C)` | `Temperature is 3°C above the alarm limit (75°C)` | "Why" section: raw values |
| `vibration_rms: 12.4 g (alarm: 8.0 g)` | `Vibration is 1.5× the alarm limit (8.0 g)` | "Why" section |
| `ISO 15243` | Not in headline. Cited as: "Per ISO 15243 bearing failure analysis" | "Why" section only |
| `ISO 10816` | Not in headline. Cited as: "Per ISO 10816 vibration severity" | "Why" section only |
| `severity: P1` | `Critical — act today` | "How urgent" line |
| `severity: P2` | `Action needed within 7 days` | "How urgent" line |
| `severity: P3` | `Monitor — no immediate action` | "How urgent" line |
| `fault_code: F-0047` | Not in headline. Cited as: "Ref: F-0047" in "Why" section | "Why" section |
| `bearing_defect_frequency_outer_race` | `Outer-race bearing damage` | "Why" section |
| `SOP-MNT-047` | Not in headline. Cited as: "SOP-MNT-047 step 3" in steps footnote | "Why" section |
| `anomaly detected at 2026-06-10T14:32:11Z` | `Detected at 2:32 PM today` | Plain timestamp in alert card |
| `threshold_type: alarm` | `ALARM` (red badge) | Badge in alert card |
| `threshold_type: warning` | `WARNING` (yellow badge) | Badge in alert card |
| `spare_status: in_stock` | `In stock` (green dot) | Parts table |
| `spare_status: low_stock` | `Low stock — reserve now` (yellow dot) | Parts table |
| `spare_status: out_of_stock` | `Not in stock` (red dot) + lead time | Parts table |
| `lead_time_days: 7` | `7-day delivery` | Parts table |

**NEEDS INPUT:** Confirm cycle-to-day conversion factor per asset type. The table above assumes ~24 cycles/day. If different assets run at different cycle rates, the conversion table must be per-asset-type in the data layer.

### 2.3 RUL Unit Conversion Logic

Raw RUL is in cycles. Display in days. Rule: `days = floor(RUL_cycles / asset_cycles_per_day)`. Round to nearest integer. Display as:

- `> 60 days` → "More than 60 days of safe run-time remaining"
- `31–60 days` → "~[N] days of safe run-time remaining"
- `15–30 days` → "~[N] days of safe run-time remaining — schedule replacement"
- `8–14 days` → "[N] days of safe run-time remaining — order parts now"
- `3–7 days` → "[N] days of safe run-time remaining — act this week"
- `1–2 days` → "[N] day(s) of safe run-time remaining — act today"
- `0 days` → "Safe run-time exhausted — isolate immediately"

---

## 3. Guided Answer Structure

### 3.1 Card Layer Order

Every EDITH answer, for any concern, follows this exact order. No deviation.

```
┌─────────────────────────────────────────────────────┐
│  VERDICT BADGE + ONE-LINE STATUS         [always]   │
│  e.g., [ACT NOW] Drive-end bearing is              │
│  vibrating 3× beyond safe limits.                  │
│  Isolate and replace today.                         │
├─────────────────────────────────────────────────────┤
│  WHAT'S HAPPENING                        [always]   │
│  2-3 plain sentences.                               │
├─────────────────────────────────────────────────────┤
│  HOW URGENT                              [always]   │
│  One line: time + consequence of inaction.          │
├─────────────────────────────────────────────────────┤
│  WHAT TO DO NOW                          [always]   │
│  Steps 1–3 (imperative verbs). "Show N more" if    │
│  >3 steps.                                          │
├─────────────────────────────────────────────────────┤
│  PARTS YOU'LL NEED             [ACT NOW/ACT WITHIN] │
│  Mini table: Part | Stock | Lead time | Qty.        │
│  (Collapsed for WATCH/HEALTHY)                      │
├─────────────────────────────────────────────────────┤
│  IF UNADDRESSED   [only if downstream data exists]  │
│  One line: consequence + cost/defect estimate.      │
├─────────────────────────────────────────────────────┤
│  WAS THIS RIGHT?                         [always]   │
│  ✓ Yes, correct  |  Edit — it was actually…        │
├─────────────────────────────────────────────────────┤
│  ▼ Show technical details  (expand)                 │
│  Full step list · Evidence · Citations · Raw values │
└─────────────────────────────────────────────────────┘
```

### 3.2 Section-by-Section Spec

**VERDICT (always visible)**
- Large text, 1 sentence, max 20 words.
- Colored badge precedes: `[ACT NOW]` red / `[ACT WITHIN N DAYS]` amber / `[WATCH]` yellow / `[HEALTHY]` green.
- Template: `[BADGE] [Component] is [plain state]. [Plain action].`
- Examples:
  - `[ACT NOW] Drive-end bearing is vibrating 3× beyond safe limits. Isolate and replace today.`
  - `[ACT WITHIN 14 DAYS] Outer-race bearing wear detected. Order the replacement bearing this week.`
  - `[WATCH] Gearbox temperature is slowly rising. Check lubrication at next routine inspection.`
  - `[HEALTHY] Mill drive is running normally. Next check: 18 Jun.`

**WHAT'S HAPPENING (always visible)**
- 2–3 sentences. Plain language. No jargon in this section.
- Sentence 1: What is wrong (or right).
- Sentence 2: What the sensor data shows in plain terms.
- Sentence 3: What this likely means in mechanical terms.
- Example (ACT NOW): "The drive-end bearing is showing very high vibration — 12.4 g against the 8.0 g alarm limit. This pattern matches outer-race fatigue wear: small surface pits are forming on the bearing's outer ring. Left unaddressed, the bearing will seize and the drive will stop."
- Example (WATCH): "The gearbox temperature has climbed from 65°C to 71°C over the last 3 days. This is still below the 75°C alarm, but the upward trend is a sign that lubrication may be degrading. No immediate action required — check lubrication at next inspection."

**HOW URGENT (always visible)**
- One sentence. Time + consequence.
- Templates by state:
  - ACT NOW: "This cannot wait — every hour of operation increases the risk of a sudden stop."
  - ACT WITHIN N DAYS: "You have [N] days before the risk of failure rises sharply. The replacement bearing takes [lead time] to arrive."
  - WATCH: "No immediate risk. If the trend continues unchecked, it may become critical within [estimated timeframe]."
  - HEALTHY: "No action needed. RUL is [N] days — next scheduled check on [date]."

**WHAT TO DO NOW (always visible)**
- Numbered list. Imperative verbs. Plain language. Max 3 steps visible; "Show N more steps" button if >3.
- Each step: one action + essential detail (which tool, which spec, which part).
- No passive voice. No "it should be ensured that."
- Example (ACT NOW, bearing replacement):
  1. "Isolate the mill drive from the power panel and lock out the switch (LOTO procedure)."
  2. "Confirm the replacement bearing is at the stores — SKF 6312 2Z (part #ST-0047)."
  3. "Contact your shift supervisor and raise a work order before starting the replacement."
  - [Show 4 more steps]

**PARTS YOU'LL NEED (always visible for ACT NOW/ACT WITHIN, collapsed for WATCH/HEALTHY)**

Render as a compact table:

| Part | In Stock? | Lead Time | Quantity |
|---|---|---|---|
| Bearing SKF 6312 2Z | In stock (3 units) | — | 1 |
| Bearing grease Shell Tellus 46 | In stock | — | 200 g |
| Locknut SKF KM 12 | Not in stock | 5-day delivery | 1 |

- Green dot = in stock. Yellow dot = low stock. Red dot = not in stock.
- If any part is "not in stock" and lead time > RUL days: display a one-line warning in red: "Note: [Part name] delivery is [N] days — longer than your remaining safe run-time. Order today."

**IF UNADDRESSED (conditional: only renders if downstream defect/cost data exists in DB)**
- One line. Format: "If unaddressed: [consequence] within [timeframe]. [Cost/defect estimate]."
- Examples:
  - "If unaddressed: surface defects on the rolled coil expected within 2 shifts. ~₹45,000/hr production loss."
  - "If unaddressed: Entry Coiler stops, Line 3 halts. ~4 hours downtime if bearing fails completely."
  - "If unaddressed: gearbox oil contamination may spread to adjacent bearings within 7 days."
- If no data: section does not render. Do not show a placeholder.

**WAS THIS RIGHT? (always visible after a recommendation is given)**
See Section 7c for the full micro-interaction spec.

**SHOW TECHNICAL DETAILS (expand-only)**
- Full step list (steps 4+ if truncated).
- Evidence: sensor readings with plain interpretation + raw values.
- Anomaly scores, fault classification codes, BPFO values.
- ISO/SOP citations.
- ML model confidence score.
- Raw timestamp.

---

## 4. Per-Asset VERDICT Header

This is the one-line status an engineer reads in 1 second when looking at the left health strip or the center focused-asset panel. It is the first thing the eye lands on.

### 4.1 Four States — Copy Templates

**State 1: HEALTHY**
- Badge color: Green
- Template: `[Asset name] is running normally. Next check: [date].`
- Example: `Hot Mill Drive is running normally. Next check: 18 Jun.`
- Sub-text (small, below): `All sensors within safe range.`

**State 2: WATCH**
- Badge color: Yellow
- Template: `[Component] is showing early signs of [plain fault]. Check [plain action] by [timeframe].`
- Example: `Gearbox is showing early signs of wear. Check lubrication by Friday.`
- Sub-text: `No immediate action — monitor daily.`

**State 3: ACT WITHIN [N] DAYS**
- Badge color: Amber
- Template: `[Component] needs replacement within [N] days. [One action to take now — usually ordering].`
- Example: `Drive-end bearing needs replacement within 14 days. Order the bearing now — 7-day delivery.`
- Sub-text: `Parts required — check stock.`

**State 4: ACT NOW**
- Badge color: Red (with pulse animation — a slow 2s pulse, not flickering)
- Template: `[Component] is [plain critical condition]. [Immediate single action].`
- Example: `Drive-end bearing is vibrating 3× beyond the safe limit. Isolate and replace today.`
- Sub-text: `Critical — cannot wait.`

### 4.2 Health Strip Entry (left panel)

Each of the 15 assets renders as one row:
```
● [Color dot]  [Asset Name]             [State badge]
               [One-line VERDICT copy]
```
Example:
```
● [RED]  Hot Mill Drive                 [ACT NOW]
         Bearing vibrating 3× safe limit
```
Clicking any row focuses that asset in the center panel and scrolls the EDITH answer card into view.

### 4.3 State Transition Logic

| Condition | State |
|---|---|
| All sensors within normal bands AND RUL > 60 days | HEALTHY |
| Any sensor in WARNING band OR RUL 15–60 days OR anomaly_score 0.40–0.69 | WATCH |
| Any sensor approaching ALARM (within 20% of alarm value) OR RUL 3–14 days OR anomaly_score 0.70–0.89 | ACT WITHIN N DAYS |
| Any sensor in ALARM band OR RUL < 3 days OR anomaly_score ≥ 0.90 OR confirmed fault class | ACT NOW |

**NEEDS INPUT:** Confirm threshold proximity definition (20% of alarm value) with the ML team. The state transition thresholds should be configurable per asset type in the backend, not hardcoded in frontend.

---

## 5. Proactive, State-Aware Copilot Guidance

The copilot never shows a blank "Ask me anything." Instead, it shows 3 suggestion chips above the input, each with a WHY subtitle. Chips change when the focused asset's state changes.

### 5.1 Chip Spec

Each chip is a clickable button. Layout:
```
┌────────────────────────────────────────┐
│  [Primary chip text]                   │
│  [Small WHY subtitle — grey, smaller]  │
└────────────────────────────────────────┘
```
Clicking a chip fires it as a copilot query — as if the engineer typed it. The input field populates with the chip text for transparency, then auto-submits.

### 5.2 Chips by Asset State

**HEALTHY state (3 chips):**
1. Primary: "When is the next scheduled maintenance for this asset?"
   WHY: "Plan ahead — avoid reactive repairs."
2. Primary: "How much bearing life is remaining and when was it last serviced?"
   WHY: "Lubrication history affects remaining life."
3. Primary: "What is the downtime history for this asset?"
   WHY: "Spot patterns before the next failure."

**WATCH state (3 chips):**
1. Primary: "What is most likely causing this temperature rise?" (or relevant sensor trend)
   WHY: "[Sensor name] has been climbing for [N] days — narrow it down."
2. Primary: "Should I move up the next inspection date?"
   WHY: "An early check now could prevent an emergency stop."
3. Primary: "What happens if this trend continues unchecked for 2 weeks?"
   WHY: "Know the risk before deciding whether to act."

**ACT WITHIN N DAYS state (3 chips):**
1. Primary: "Show me the full bearing replacement procedure, step by step."
   WHY: "Plan the work before the [N]-day window closes."
2. Primary: "Are all the parts in stock, or do I need to order now?"
   WHY: "Delivery may take longer than your remaining safe run-time."
3. Primary: "What is the risk if I delay the replacement by one week?"
   WHY: "Understand the consequence before deciding."

**ACT NOW state (3 chips):**
1. Primary: "Walk me through the safe isolation steps for this machine."
   WHY: "Safety comes first before any repair work begins."
2. Primary: "Who do I need to inform right now?"
   WHY: "This needs shift supervisor + stores notified immediately."
3. Primary: "Is there a temporary safe fix to keep running for a few hours if a shutdown is not possible right now?"
   WHY: "In case a full stop is not immediately possible."

### 5.3 Chip Refresh Logic

Chips refresh when:
- The focused asset changes (engineer clicks a different asset on the left strip).
- The focused asset's state changes (a new alert comes in, changing WATCH → ACT NOW).
- The engineer submits a question from a chip (chips reload with the next logical follow-up set after EDITH answers).

After a chip is used, remove it and replace with the next most relevant chip. Don't show the same chip twice in a session unless the state resets.

---

## 6. Feature Discovery + Onboarding Hints

For every panel and feature: a one-line hint that appears ONLY when the panel has no data yet (first use, or empty state). The hint teaches what the panel does and why it matters.

### 6.1 Hint Copy per Panel

**Left panel — Asset Health Strip (empty or first session):**
> "All 15 assets at a glance. Red = act now. Yellow = watch. Green = all clear. Tap any asset to focus."

**Center panel — Focused Asset (no asset selected):**
> "Select an asset from the left to see live sensor readings and EDITH's diagnosis."

**Center panel — Live Sensor Graphs (first time for this asset):**
> "The shaded band is the safe operating range. A reading touching or crossing the edge means investigate now."

**Center panel — EDITH Answer Card (first use, no alert triggered):**
> "When a sensor crosses a threshold, EDITH's diagnosis appears here automatically. You can also ask EDITH anything about this machine."

**Right panel — Alerts Feed (no alerts):**
> "No alerts right now. When a sensor crosses a safe limit, the alert appears here instantly. ALARM (red) = act now. WARNING (yellow) = early sign."

**Right panel — Copilot Input (first use):**
> "Ask EDITH anything about this machine — history, procedures, spare parts. Use the suggestions above to get started."

**START HERE Banner (not yet triggered — only show hint if engineer hovers the "?" icon):**
> "When multiple machines need work, EDITH ranks which to fix first — by line criticality, safety risk, and parts availability."

**Downstream Impact section (data not yet linked):**
> "Once process-defect data is connected, EDITH will show how this machine's condition affects rolled-coil quality and throughput."

**Feedback section (never used):**
> "Tell EDITH if its recommendation was right. Your input directly improves the system's accuracy."

### 6.2 Hint Display Rules

- Hints are single-line, grey, small text (14px), centered in the empty panel.
- Hints disappear the moment the panel has real data.
- Hints never animate, never pulse, never distract.
- Do not show hints on panels that have real data — even if the data is sparse.

---

## 7. Three Missing Features — Contextual, Not Clutter

### 7a. Bottleneck "Start Here" Banner

**Purpose:** When multiple assets need action, the engineer should not have to decide which one first. EDITH decides and states why.

**Trigger condition:**
- ≥ 2 assets are in ACT NOW OR ACT WITHIN state simultaneously.
- (If only 1 asset needs action, no banner — the VERDICT header on that asset is sufficient.)

**Position:** Full-width banner, top of screen, above all panels. Highest visual priority.

**Copy template:**
> "[N] machines need your attention — start with [Asset Name] because [plain reason]."
> [Focus [Asset Name] →]  [See all N →]  [✕ Dismiss]

**[plain reason] selection logic — pick the highest-priority reason that applies:**
1. "it is safety-critical and could injure someone if it fails" (asset tagged safety-critical in config)
2. "its bearing is failing faster than the spare can arrive — [lead time] delivery, [N] days RUL"
3. "it blocks the [line name] — if it stops, [N] downstream assets stop too"
4. "the spare is in stock today — replacement is straightforward"

**Banner priority ranking algorithm (descending priority):**
1. Safety-critical tag on the asset
2. (RUL days) < (spare lead time days) — ordering too late
3. Downstream impact score (blocks critical line)
4. RUL ascending (lowest safe run-time first)
5. Spare availability (in-stock preferred, avoids ordering delay)

**Concrete copy examples:**
- "3 machines need your attention — start with Hot Mill Drive because it blocks Line 3 and the spare is in stock."
- "2 machines need your attention — start with Roughing Mill Bearing because it is safety-critical and must be acted on today."
- "4 machines need your attention — start with Entry Coiler — the spare takes 12 days to arrive and RUL is 9 days."

**Dismiss behavior:** Clicking ✕ dismisses for the current session. If a new asset enters ACT NOW after dismissal, the banner re-appears. Dismissal does not persist across sessions.

**"See all N →" link:** Opens a side drawer listing all assets in ACT NOW/ACT WITHIN state, sorted by the same priority algorithm, each with a one-line reason. Engineer can click any to focus it.

### 7b. Downstream Impact

**Purpose:** Give engineers the language to justify urgent maintenance to supervisors. "EDITH says the coil will have surface defects in 2 shifts" is actionable. "RUL 240 cycles" is not.

**Position:** Inline, below the Steps section, above the Feedback section in the EDITH answer card. Part of the always-visible card area in ACT NOW and ACT WITHIN states.

**Trigger:** Only renders if the DB has a linked defect event or cost-impact record for this asset's failure mode. If no data, the section is absent — not a placeholder, not "N/A."

**Copy template:**
> "If unaddressed: [plain defect or event] within [timeframe]. [Estimated impact]."

**[plain defect or event] language rules:**
- Surface defects → "surface defects on the rolled coil"
- Dimensional deviation → "dimensional variation in the finished product"
- Production stop → "[Asset name] stops, [downstream asset/line] halts"
- Contamination spread → "oil contamination spreads to adjacent bearings"
- Quality rejection → "coils likely to fail quality inspection"

**[Estimated impact] format:**
- If cost data available: "~₹[X,XXX]/hr production loss" or "~[N] hours downtime"
- If defect-count data available: "Expected [N] defective coils per shift"
- If no quantitative data: omit the cost estimate. Do not fabricate. Write only: "Surface defects on the rolled coil expected within 2 shifts."

**Concrete examples:**
- "If unaddressed: surface defects on the rolled coil expected within 2 shifts. ~₹45,000/hr production loss."
- "If unaddressed: Entry Coiler stops, Line 3 halts. Estimated 4 hours downtime if bearing fails completely."
- "If unaddressed: gearbox oil contamination may spread to adjacent bearings within 7 days."
- "If unaddressed: dimensional variation in hot-rolled strip expected when RUL reaches zero."

**NEEDS INPUT:** Confirm which defect event types are already linked in the database to which equipment failure modes. The content layer needs a `defect_link` table: `{asset_id, fault_class, defect_type, estimated_timeframe, estimated_cost_per_hr}`.

### 7c. Feedback Loop

**Purpose:** Close the loop between EDITH's recommendation and what the engineer actually did. This is the only source of ground truth for model improvement. It also signals to the engineer that their expertise is valued.

**Position:** Last line in the EDITH answer card (above "Show technical details"), always visible after a recommendation is given.

**States:**

**State 1 — Default (recommendation just given):**
```
Was this right?   ✓ Yes, correct   |   Edit — it was actually…
```
Both options are inline, no modal, no page navigation.

**State 2 — After "Yes, correct" click:**
```
Got it — thank you. This helps EDITH improve.
```
This line fades out after 3 seconds. Card returns to its default view.

**State 3 — After "Edit — it was actually…" click:**
An inline form expands below (no modal, no new page):
```
What was the actual issue?
[Text input: e.g., "It was a misalignment, not a bearing fault"]

What was the right fix?
[Text input: e.g., "We realigned the coupling — no bearing replaced"]

[Submit]  [Cancel]
```
- Both fields are optional but at least one must be filled to enable Submit.
- Submit is a plain "Submit" button, not "Submit feedback."

**State 4 — After Submit:**
```
Noted — EDITH will factor this in. Thank you.
```
Fades out after 3 seconds.

**Data contract:** On submit, POST to `/api/feedback` with:
```json
{
  "asset_id": "...",
  "alert_id": "...",
  "recommendation_id": "...",
  "confirmed": true | false,
  "engineer_note_issue": "...",
  "engineer_note_fix": "...",
  "timestamp": "...",
  "engineer_id": "..."
}
```
Fire-and-forget. No loading state. Optimistic UI — assume success.

---

## 8. Information Architecture

### 8.1 One-Screen Layout

```
╔══════════════════════════════════════════════════════════════════════════╗
║  START HERE BANNER (full width, appears only when ≥2 assets need action) ║
╠══════════════╦═══════════════════════════════════╦══════════════════════╣
║              ║                                   ║  ALERTS FEED         ║
║  ASSET       ║  FOCUSED ASSET NAME + STATUS      ║  ─────────────────   ║
║  HEALTH      ║  ──────────────────────────────   ║  🔴 ALARM            ║
║  STRIP       ║  [VERDICT BADGE + 1-LINE STATUS]  ║  [sensor] = [value]  ║
║              ║                                   ║  [asset] · [time]    ║
║  ● Asset 🔴  ║  LIVE SENSOR GRAPHS               ║                      ║
║  ● Asset 🟡  ║  (Vibration / Temp / etc.)        ║  🟡 WARNING          ║
║  ● Asset 🟢  ║  threshold bands shown            ║  [sensor] = [value]  ║
║  ● Asset 🟢  ║                                   ║  [asset] · [time]    ║
║  ● Asset 🟡  ║  EDITH ANSWER CARD                ║                      ║
║  ...         ║  ─────────────────                ║  ─────────────────   ║
║              ║  VERDICT (large, always)          ║  EDITH SUGGESTS      ║
║  [tap any    ║  WHAT'S HAPPENING (always)        ║                      ║
║   to focus]  ║  HOW URGENT (always)              ║  [Chip 1 + WHY]      ║
║              ║  WHAT TO DO NOW (always)          ║  [Chip 2 + WHY]      ║
║              ║    1. Step 1                      ║  [Chip 3 + WHY]      ║
║              ║    2. Step 2                      ║                      ║
║              ║    3. Step 3                      ║  ─────────────────   ║
║              ║    [Show N more]                  ║  ASK EDITH           ║
║              ║  PARTS NEEDED (ACT NOW/WITHIN)    ║  [_________________] ║
║              ║  IF UNADDRESSED (conditional)     ║  [Send]              ║
║              ║  WAS THIS RIGHT? ✓ | Edit         ║                      ║
║              ║  [▼ Technical details]            ║                      ║
╚══════════════╩═══════════════════════════════════╩══════════════════════╝
```

### 8.2 Eye Priority Order

The engineer's eye should travel in this order:

1. **START HERE banner** (full-width top, red/amber — only when active) — J1 answered immediately.
2. **VERDICT header** (center panel, large text, colored badge) — J2 answered in 1 second.
3. **ACT NOW alerts** (right panel, red, newest first) — real-time urgency signal.
4. **WHAT TO DO NOW steps** (center, below verdict) — J4 answered without scrolling.
5. **PARTS NEEDED** (center, below steps) — J5 answered without scrolling.
6. **Asset health strip** (left, at a glance) — plant-level overview.
7. **EDITH suggestion chips** (right, below alerts) — proactive guidance.
8. **Live sensor graphs** (center, visual evidence) — supports J3.
9. **Ask EDITH input** (right, bottom) — available when needed.

### 8.3 What is Always Visible (No Scroll, No Expand)

- Asset health strip (all 15 assets with dot + one-liner)
- Focused asset VERDICT header
- Live sensor graph for the most critical sensor
- EDITH answer card: VERDICT + WHAT'S HAPPENING + HOW URGENT + WHAT TO DO NOW (steps 1–3) + PARTS (in ACT NOW/WITHIN)
- Alerts feed (newest 5 alerts)
- Copilot: 3 chips + input

### 8.4 What is One-Click Away (Not Always Visible)

- Full step list (steps 4+)
- Technical details (fault codes, ML scores, citations, raw sensor values)
- Parts table for WATCH/HEALTHY assets
- IF UNADDRESSED section for WATCH/HEALTHY (visible by default for ACT NOW/WITHIN)
- All alerts history (beyond newest 5)
- "See all N machines needing attention" drawer (from START HERE banner)

### 8.5 What Appears Contextually (Not Always Rendered)

- START HERE banner: only when ≥2 assets in ACT NOW or ACT WITHIN
- EDITH answer card: only when there is an alert or the engineer has asked a question
- IF UNADDRESSED section: only when downstream defect data exists for this asset+fault
- Feedback section: only after EDITH has provided a recommendation
- "Parts not in stock — order now" warning: only when a required part is out of stock and lead time > RUL days

---

## 9. Anti-Patterns

These patterns will confuse or overwhelm a plant engineer. Each has a rule to prevent it.

| Anti-pattern | Why it fails | Rule |
|---|---|---|
| **Jargon in headlines** (BPFO, anomaly_score 0.87, FFT peaks) | Engineer cannot act on ML terminology; they distrust what they don't understand | Jargon NEVER appears in VERDICT, WHAT'S HAPPENING, or HOW URGENT. It lives in "Show technical details" only. |
| **Unanchored numbers** ("78°C", "12.4 g", "1014 cycles") | Numbers mean nothing without context and a safe-limit reference | Every number in the visible card has its unit + the safe limit comparison: "78°C — 3°C above the alarm limit (75°C)." |
| **Confidence hedging in the main card** ("may possibly indicate", "87% probability of", "potential fault") | Engineers need a clear verdict, not a probability distribution | VERDICT and WHAT'S HAPPENING use definitive statements. Confidence scores go in technical details. |
| **Passive-voice recommendations** ("It is recommended that lubricant be replaced") | Passive voice creates ambiguity about who acts and when | Steps use imperative verbs. "Lubricate the bearing with Shell Tellus 46 (2 pumps)." |
| **Blank copilot** (just an input box with "Ask me anything") | Forces cognitive work on an already-busy engineer | 3 state-aware chips always precede the input. Never render the input alone. |
| **Orphaned alerts** (alert card with no link to the EDITH diagnosis) | Alert creates urgency but gives no resolution path | Every alert card has a one-line VERDICT and a "See EDITH's diagnosis →" link that focuses the asset. |
| **Alert flood** (15 separate alerts for the same asset) | Visual noise; engineer cannot triage | Alerts are grouped by asset. "5 alerts on Hot Mill Drive" as one collapsed item. Expand to see all. |
| **Always-on empty panels** ("No defect data yet" section permanently visible) | Empty panels erode trust and clutter the screen | Sections with no data (IF UNADDRESSED, Downstream Impact) are absent, not placeholders. |
| **Steps with jargon** ("Apply ISO VG 46 lubricant per OEM spec") | Engineer pauses to interpret instead of acting | Steps name the actual product: "Lubricate with Shell Tellus 46." Technical references go in the step footnote. |
| **Severity labels without time** ("P2 — Moderate") | "Moderate" is not actionable | Every severity label must be translated to a time and action: "Action needed within 7 days." |
| **Multiple simultaneous animations** (pulsing dots + scrolling alerts + animated graphs) | Sensory overload; attention is pulled everywhere | Only ACT NOW badges pulse (slow 2s pulse). Everything else is static. Graphs animate on load only. |
| **Nested sub-steps** (1. Step → 1a. sub-step → 1a-i. detail) | Engineers lose their place in the procedure | Steps are flat numbered lists, max 2 levels (main step + single sub-step). No deeper nesting. |
| **Cost estimates on every card** | Feels like monitoring software, not a colleague | Downstream cost/defect appears only in ACT NOW and ACT WITHIN, and only when the data exists. Never fabricated. |

---

## 10. Open Questions (NEEDS INPUT)

These must be resolved before the frontend engineer implements sections that depend on them.

| # | Question | Impact | Owner |
|---|---|---|---|
| OQ-1 | What is the cycles-per-day figure per asset type? Needed for RUL → days conversion. | Section 2.3 — all RUL display strings | ML / process team |
| OQ-2 | What is the `defect_link` table schema? Which fault classes are currently linked to product defect types? | Section 7b — IF UNADDRESSED section | Data / ML team |
| OQ-3 | What is the engineer's primary device: desktop monitor, tablet, or shared workstation? Screen size determines how much fits above the fold. | Section 8 — layout proportions | Plant ops / client |
| OQ-4 | Is `engineer_id` available from the session/auth layer for the feedback payload? | Section 7c — feedback API contract | Backend / auth team |
| OQ-5 | Which assets are tagged "safety-critical"? This drives START HERE banner priority #1. | Section 7a — banner priority algorithm | Plant safety team |
| OQ-6 | Are the downstream cost figures (₹/hr) available per asset per failure mode, or estimated? | Section 7b — cost strings | Process / finance team |
| OQ-7 | Should the "Show technical details" expand section be visible to all engineers or only to senior engineers / supervisors (role-based)? | Section 3.2 — expand section access | Client product owner |

---

## 11. Non-Goals (Explicitly Out of Scope for This Spec)

1. Redesigning the alert stream format, SSE protocol, or backend sensor ingestion.
2. Adding new ML models or changing anomaly detection thresholds.
3. Building a mobile app or responsive mobile view — this spec is for the existing desktop cockpit.
4. A separate "reports" or "export to PDF" feature.
5. Multi-language (Hindi UI) — English-only per client brief; Hinglish-comfortable audience reads English fine in a professional tool context.
6. Real-time collaboration / multi-engineer concurrent view.
7. The copilot's AI reasoning layer — this spec defines what EDITH says and how it presents it, not how the LLM generates the content.

---

## 12. Success Metrics

**Leading metrics (measurable within days/weeks of launch):**
- Time-to-first-action after an ALARM alert: target < 3 minutes (baseline: NEEDS INPUT, measure from SSE timestamp to work-order creation timestamp)
- Copilot chip click rate: target ≥ 60% of copilot sessions use a chip (vs. free-text) — confirms chips are useful
- "Was this right? Yes" rate: target ≥ 75% of recommendations confirmed correct within 48 hours of being acted on
- Feedback submission rate: target ≥ 30% of ACT NOW recommendations receive feedback within 7 days

**Lagging metrics (business outcomes, weeks/months):**
- Unplanned downtime per asset per month: target direction — down vs. pre-EDITH baseline
- Defective coil events linked to equipment condition: target direction — down
- Mean time between emergency stops: target direction — up
- Engineer trust score: quarterly survey, target ≥ 4.2/5.0 on "EDITH tells me what I need to know, clearly"

**NEEDS INPUT:** Baseline measurements for all lagging metrics. Cannot set targets without baseline.

---

*Spec version: 1.0 | 2026-06-10 | product-manager-agent*
*Next action: Frontend engineer reviews Sections 3, 4, 5, 7, 8 for implementation feasibility. OQ-1 through OQ-7 resolved in parallel.*
