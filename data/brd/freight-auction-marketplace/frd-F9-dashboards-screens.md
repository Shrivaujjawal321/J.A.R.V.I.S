# F9 — Dashboards & Screens per Persona

**Scope.** Screen inventory, IA, required states, field-usability constraints for five personas. No visual design, no component library, no layout. Every `SCR-`/`FR-` traces to a BRD `BR-`/`OBJ-`. IDs `900–999`. Not owned here: auction mechanism (→F6), eligibility logic (→F2), notification transport (→F10), error taxonomy (→F5), HOS computation (→F7).

**Core state set — mandatory on every screen below unless noted:** Loading · Empty · Partial data · Stale data · Permission-denied · Error · Offline · Contested (in-progress-by-someone-else). Table rows list only *additional/notable* states.

**FR-900** Every `SCR-` in this document shall implement the core state set as a first-class render, not a spinner-then-blank fallback. *Traces: OBJ-002/OBJ-004/OBJ-006. Source: derived, Boss's "kuch bhi chutna nahi chahiye" extended to UI.*

**IA principle carried through every persona:** exceptions surface above normal status, never buried in a uniform list (spine §7.3, A9's "desk behind the software") — Linear-dense triage, not Notion-airy browsing.

---

## 1. Screen inventory

### 1.1 Shipper coordinator (desk)

| ID | Screen | Purpose | Key actions | Notable states | Traces |
|---|---|---|---|---|---|
| SCR-900 | Load Dashboard | Home; exceptions ranked above on-track loads | Publish, filter, jump to any load | Empty = "no loads — publish one" | BR-100/102, OBJ-002 |
| SCR-901 | Post a Load | Structured multi-step declaration | Save draft, publish, ack BR-121 warning | Partial = autosaved draft; Error names the missing field | BR-110–127 |
| SCR-902 | Auction Watch | Live view of one open auction | Watch bids arrive, early-close (if DEC-308 permits), pre-bid cancel | See §2.1 | BR-301–318 →F6 |
| SCR-903 | Award & Accept-Flow Monitor | Track AWARD_PENDING → ACCEPTED | View selection-record excerpt (BR-303), see decline/lapse | Transient "re-verifying" state | BR-303, BR-309 |
| SCR-904 | Shipment Tracker | Pickup→transit→drop for one load | View custody events, message ops | Stale = missed interval flagged, not hidden (BR-401) | BR-401/403 |
| SCR-905 | Exception Inbox (org-scoped) | Only this shipper's open exceptions | Acknowledge, respond, escalate | Empty is a genuinely good state, shown as such | BR-913 |
| SCR-906 | Invoice Approval | Review/approve/dispute lines | Approve clean lines, dispute one line without blocking the rest | Partial = mixed held/clear lines rendered distinctly | BR-601–604 |
| SCR-907 | Claim Intake | Raise a Carmack claim | Submit §370.3-minimum fields, track status | — | BR-807 |
| SCR-908 | Standing & Cancellation History | Own org's record | View only | Depends on an orphan upstream field (BR-106) — see EC-907 | BR-105/145 |

### 1.2 Carrier dispatcher (desk or phone)

| ID | Screen | Purpose | Key actions | Notable states | Traces |
|---|---|---|---|---|---|
| SCR-910 | Load Board | Browse loads this org is eligible for | Filter, sort, open an auction | Permission-denied if org-wide gate fails (e.g. suspended, BR-229) | BR-200–217 |
| SCR-911 | Bid & Comparison Screen | **Core loop** — bid under a live timer | Submit, withdraw pre-close (BR-308), view own bid history | See §2.2 | BR-301/307/308/314/717 |
| SCR-912 | Fleet Assignment | Bind driver+truck to an accepted award | Confirm tuple (BR-212), see overlap conflict (BR-214) | Contested = two dispatchers, same truck (EC-913) | BR-212–215 |
| SCR-913 | Active Loads (multi-truck) | Every truck in flight, exceptions ranked first | Drill into one trip, message driver | Same exception-forward pattern as SCR-900 | BR-401/405 |
| SCR-914 | Breakdown / Exception Report | Report a `TRANSIT_EXCEPTION` sub-type | Pick category (BR-405), attach evidence, request relief | — | BR-402/405 |
| SCR-915 | Driver & Equipment Roster | Manage availability | Self-declare unavailable (BR-216), see expiry alerts (BR-220) | Error = expired document blocks new assignment | BR-209–220 |
| SCR-916 | Settlement Status | Per-load payable + factoring/NOA state | View, contact ops to dispute | — | BR-605/606 |

### 1.3 Driver (phone, one-handed, gloves, sun/dark, poor connectivity, possibly Spanish)

| ID | Screen | Purpose | Key actions | Notable states | Traces |
|---|---|---|---|---|---|
| SCR-920 | Today (home) | One current assignment, one primary action | Start nav, call dispatch, report a problem | Offline = last-known assignment cached, badged, never blank | BR-910 |
| SCR-921 | Navigation Handoff | Hand off to an external nav app | One tap; no in-app map surface owned here | — | derived |
| SCR-922 | Arrival / Departure Capture | Check in/out at pickup and drop | Confirm arrival, confirm departure | Offline = queued locally, syncs on reconnect (FR-901) | BR-403 |
| SCR-923 | Document Capture | Photo of BOL, seal, condition at pickup | Take, retake, confirm | Error = unreadable image flagged before accept, not silently stored | BR-400/408 |
| SCR-924 | POD Capture | Clear-vs-exception signature — see §3 | — | — | BR-500–514 |
| SCR-925 | Report a Problem | Entry point to any transit exception | Category, voice-note or photo, submit | Offline = high-priority sync queue | BR-405 |
| SCR-926 | Language & Support | Toggle English/Spanish; call/text dispatch or ops | — | — | BR-914 |

### 1.4 Platform ops / exception desk

| ID | Screen | Purpose | Key actions | Notable states | Traces |
|---|---|---|---|---|---|
| SCR-930 | Exception Work Queue | Ranked — what's broken, action attached; **not** a dashboard | Claim, act, reassign, escalate | Contested = claimed by another (EC-904); Stale = unclaimed past `[NEEDS INPUT: threshold]` | BR-913, spine §7.3 |
| SCR-931 | Exception Detail & Resolution | Full context: load, custody events, prior actions | Resolve, request info, escalate to fraud (SCR-941) | — | BR-913 |
| SCR-932 | Claims Desk | Every open Carmack claim against its 30/120/60-day clock | Acknowledge, request evidence, decide, issue disallowance | Stale = obligation date approaching/missed, escalating visually | BR-807/808 |
| SCR-933 | Silence / No-Response Monitor | Loads flagged for missed status interval (BR-401) or no-show risk | Contact carrier, escalate | Empty is the goal state | BR-401/409 |

### 1.5 Platform admin / fraud reviewer

| ID | Screen | Purpose | Key actions | Notable states | Traces |
|---|---|---|---|---|---|
| SCR-940 | Carrier Vetting Queue | New/re-verifying carriers awaiting explicit ops approval | Approve, reject, request evidence | Partial = some automated checks cleared, some pending | BR-908, BR-201–208 |
| SCR-941 | Fraud Case Review | Classified case from BR-806 (double-broker / identity theft / disclosed substitution) | Classify, escalate, notify counterparties | — | BR-806 |
| SCR-942 | Selection Record / Audit Viewer | Reproduce any award's full immutable record | Search, export, view exclusions + reasons | — | BR-303, BR-706 |
| SCR-943 | Enforcement Action | Apply graduated penalty | Warn / restrict / suspend / remove, log ground + evidence + appeal | Contested = live in-flight load exists under a suspending carrier | BR-817/818 |

---

## 2. Auction screens — the product's heart

### 2.1 Shipper's Auction Watch (SCR-902)

States beyond core: **live** (bids arriving, running low bid + eligible-bidder count, countdown as `aria-live="polite"`); **extended** (`AUCTION_EXTENDED` — visually distinct, never a silent reset); **thin-market** (pool/bid count below labelled threshold, BR-318, EC-908); **closing** (brief lock while `AWARD_PENDING` re-verifies, shown as "verifying," never already-awarded, avoiding false relief then reversal); **failed** (`_NO_BIDS`/`_NO_ELIGIBLE_CARRIER`/`_ALL_ABOVE_LIMIT`, each a distinct named reason). Shipper sees price, timestamp, carrier authority type (BR-313) per bid, and a standing indicator where BR-106's feed exists — this is the shipper's own auction, not a bidder view, so BR-717 does not apply here.

### 2.2 Carrier's Bid & Comparison Screen (SCR-911)

The dispatcher's core loop, and the screen most exposed to an unresolved fork: **what a bidder sees of rivals is undecided** (DEC-302/303), and BR-717 forbids exposing another bid's value or identity absent a documented decision. Built with rival-visibility as a swappable parameter, three states ready for whichever F6 locks: **(a) none** — own bid + timer + eligible-count only; **(b) rank-only** — "#2 of 5 eligible," no amounts; **(c) leading-price band** — rounded, never exact. **Default: (a) none** — the conservative BR-717 reading. Other states: **submitted** (locked per DEC-311's decrement rule, if any); **withdrawn** (BR-308, recorded against the bidder); **ineligible** (BR-301 — a failing tuple never reaches this screen; dispatcher sees why on SCR-915 instead); **outcome** (won/lost/cascaded-in, EC-909).

**CHALLENGE:** shipping a bid screen against an undecided disclosure boundary risks a BR-717 violation in production, not a UI bug, if the default proves too permissive later. F6/Boss should lock DEC-302/303 before SCR-911 builds past "none."

---

## 3. POD capture flow (SCR-924) — carries the entire commercial settlement

Sequence, each its own screen state, never skippable: **(1) Arrival** confirmed (geofence-assisted or manual, SCR-922). **(2) Count/condition entry** against declared (BR-400 lineage). **(3) The forced choice** — full-screen, two-option: **"Delivered CLEAR"** vs **"Delivered WITH EXCEPTION."** No pre-selection, no default path; continue is disabled until one is explicitly chosen (BR-501/502 keep "received," "received in good condition," "received and accepted" three separate facts, never one implied checkbox). Exception forces a structured sub-screen before signature is reachable: type (over/short/damage), quantity/unit, whose count (BR-503/508) — free text supplements, never substitutes. **(4) Photo evidence** — optional on clear, **mandatory** on exception. **(5) Signature** — from whoever is present, no account required; printed name + stated role captured, never inferred (BR-510/511). **(6) Confirmation** — read-only summary before submit, since BR-512 makes the record fixed once captured; any later addition is a separately timestamped addendum, never an overwrite.

**Additional screen:** concealed-damage/addendum entry (BR-504), reachable later, always linked to the original POD, never replacing it. `DELIVERY_ATTEMPTED_NO_RECEIVER` is its own outcome (BR-509) — arrival timestamp recorded, no POD, forced-choice screen never reached.

**FR-903** The clear/exception screen shall never render a default selection, a "skip" affordance, or one combined "confirm delivery" button implying clear. *Traces: BR-501/505, OBJ-004. Source: task brief.*

**Offline:** the sequence must complete and persist locally without connectivity, syncing with a visible "pending sync" state — a captured signature is never lost. `[ASSUMPTION: offline-first capture required given stated field conditions | conf: high — inferred, no BR states it explicitly]`.

---

## 4. Exception desk (SCR-930) and notifications-in-app

**Queue ranking dimensions** (mechanism only, no invented thresholds): severity class (custody/safety > commercial > informational), age since trigger, proximity to a regulatory clock (e.g. Carmack's 30/120/60-day marks, BR-807), and `FRAUD_SUSPECTED`/`CARRIER_SUSPENDED_IN_FLIGHT` always surfacing above routine items (A8 §8.9.10). Every row carries the action already attached — a linked resolution screen, not a re-triage step.

**Notifications land per persona** (F10 owns delivery/transport; this is where they render):

| Persona | Landing surface |
|---|---|
| Shipper coordinator | Banner atop SCR-900 for own-org exceptions + SCR-905 inbox; routed to the posting user specifically (BR-911) |
| Carrier dispatcher | Badge on SCR-910/913; breakdown/expiry alerts route to SCR-914/915 |
| Driver | Full-screen interrupt on SCR-920, never a dismissible toast for anything blocking; optional audio cue, eyes-on-road context |
| Ops desk | Queue re-sort (SCR-930) + distinct cue for a newly-critical item |
| Admin/fraud | Case appears in SCR-941; cadence `[NEEDS INPUT: real-time or digest]` |
| Consignee | **No in-app surface** — BR-912 requires out-of-band delivery, explicit "delivery status unknown," never a false confirmed-read |

---

## 5. Accessibility & field usability (WCAG 2.2 AA minimum, non-negotiable)

- **Target size:** driver-screen elements meet SC 2.5.8 (≥24×24 CSS px), generously above the floor given gloves.
- **Contrast:** AA 4.5:1 baseline; driver screens target AAA 7:1 for sunlight legibility, with a high-contrast/dark pair (`prefers-color-scheme`) at parity, never one mode bolted-on.
- **One-handed:** primary actions in the reachable thumb zone; no two-hand gesture or precision drag (2.5.7 — single-pointer alternative wherever drag is used).
- **Language:** English/Spanish minimum on every driver screen and support path (BR-914); persists across sessions.
- **Low-literacy-safe:** icon **+** short label always paired, never icon-only (with `aria-label` regardless) — a stressed tap needs a label, not just an icon.
- **Connectivity:** every driver screen degrades gracefully — cached last-known state, explicit "offline, will sync," no infinite spinner, no data loss on a dropped connection mid-capture.
- **Motion:** `prefers-reduced-motion` → timers and queue re-sorts fade/step, never spin.
- **Screen-reader narrative:** auction updates `aria-live="polite"`; close/award `aria-live="assertive"`; POD forced-choice has a linear reading order, default never implied visually-only.
- **Desk screens:** keyboard-complete, logical focus order, dense layout — appropriate for a trained, stationary user, unlike the driver.

---

## 6. Edge case register (`EC-900`–`EC-914`)

| ID | Trigger | Behaviour | Who decides | Unresolved? |
|---|---|---|---|---|
| EC-900 | Two dispatchers act on same truck at once (SCR-912/913) | Optimistic lock; second actor sees "updated by X, refresh" | Convention | No |
| EC-901 | Driver phone loses connectivity mid-POD (SCR-924) | Local draft persists, syncs on reconnect, "pending sync" badge | Resolved (FR-901) | No |
| EC-902 | Shipper watches SCR-902 during `AWARD_PENDING` re-verify | Transient "verifying eligibility," not premature award | Resolved | No |
| EC-903 | Rival-visibility level on SCR-911 (DEC-303) | Defaults to "none" until DEC-303 locks | F6/Boss | **Yes — §2.2** |
| EC-904 | Ops queue item claimed by a second user (SCR-930) | "Already claimed by X"; duplicate resolution blocked | Resolved | No |
| EC-905 | Consignee reports damage minutes after signing "clear" | Only path is the addendum channel (BR-504); original never overwritten | Resolved | No |
| EC-906 | Spanish-speaking driver hits an English error code | Maps `ERR-` codes (→F5) to localized strings, never raw codes | F5/F10 | Partially |
| EC-907 | SCR-908's standing indicator has no upstream feed (BR-106 orphan) | Renders "not yet available," never fabricates a value | Rendering rule set; orphan remains | Yes (upstream) |
| EC-908 | Auction has exactly one bidder (EC-304) | Both screens label it "thin market," not competitive | Labelling resolved; DEC-310 open | Yes (mechanism) |
| EC-909 | Award cascades to next bidder after a decline (DEC-309) | Does new winner's screen disclose the cascade? | Boss — privacy vs transparency | **Yes** |
| EC-910 | Driver has no camera permission (SCR-923/924) | Degrades to text-only notation; signature never blocked by missing photo unless exception path requires one | Resolved | No |
| EC-911 | Exception lands for a shipper org itself suspended (BR-107) mid-flight | Queue item surfaces both facts together | Resolved | No |
| EC-912 | SCR-920 has no HOS-feasibility signal from F7 | Shows "not evaluated," never a false-safe green light | F7 dependency | Depends on F7 |
| EC-913 | Two trucks, one org, overlapping window (BR-214) on SCR-912 | Truck B shows "unavailable for this window" | Resolved | No |
| EC-914 | Fraud reviewer (SCR-941) has case open when BR-818 suspension hits an in-flight load | Shows "recovery protocol active," never "frozen" | Resolved | No |

---

## 7. Open questions this domain cannot resolve alone

`[NEEDS INPUT]`: exception-queue stale-threshold value (SCR-930); real-time vs. digest cadence for fraud review (SCR-941); whether a cascade winner is told (EC-909, Boss's call); DEC-302/303 rival-visibility resolution before SCR-911 ships past its "none" default.
