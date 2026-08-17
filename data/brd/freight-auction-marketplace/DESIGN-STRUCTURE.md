# Design Structure — Freight Reverse-Auction Marketplace

**Assembled from D1-D6** (`design/D1-foundations-components.md` … `D6-cross-flow-map.md`), each authored
independently against `design-spine.md`. This document is the reader's map; it references the six
source files for depth rather than reproducing them. The companion file, **`DESIGN-GAPS.md`, is the
more load-bearing of the two outputs** — read it before treating anything here as build-ready.

---

## 0 · Cover — orient in 60 seconds

**What this is.** A Figma-style structure map — pages → frames → components → prototype wiring — for a
US freight reverse-auction marketplace serving five personas: Shipper, Carrier (owner-operator +
dispatcher), Driver (mobile), Platform Ops, Platform Admin/Fraud. A sixth party, the Consignee, has no
design surface at all today — see §5 and `DESIGN-GAPS.md` row 3.

**Build state, honestly.** 8 of 31 F9-specified screens are **built and verified** in `prototype.html`
(9 screen loads across 4 personas, 0 failures, 0 console errors, 0 external requests):
`SCR-900, 901, 902, 904, 910, 920, 924, 930`. **Everything else in this document is specified only —
paper, not running code.** Nowhere below should "designed" be read as "shipped."

**The number that matters most.** 41 frames are indexed (31 F9-canonical + 10 `[NEW]`), 19 distinct
gaps/conflicts/defects are on record, 1 of those is a genuine contradiction between the BRD and the FRD
(not a design question — a business decision), and 2 are already closed. The single highest-consequence
finding: the platform's own costliest documented failure mode (`AWARD_LAPSED`/`AWARD_VOIDED_INELIGIBLE`
— an uncollected load) **has no screen where ops can resolve it**, because the data model that would
let it queue as a case structurally excludes it. See `DESIGN-GAPS.md` row 1.

**Three decisions block further build** and are not resolved here — rival-bid visibility, whether a
shipper may decline the lowest qualified bidder, and HOS signal-vs-record. §7 below states each with
its options and consequences, unresolved, as instructed.

**How to use this document.** §1 walks the page tree, citing D1-D6 for the substance. §2 is the
consolidated frame index — every `SCR-` ID, who owns it, whether it's built. §3 condenses the gap
register (full ranked table lives in `DESIGN-GAPS.md`). §4 states the three build-blocking decisions.
Nothing here resolves a `[NEEDS INPUT]` or invents a screen, token, or number beyond what D1-D6 sourced.

---

## 1 · Page-by-page structure (spine §2 page tree)

### 📄 00 · Cover
This document's own §0.

### 📄 01 · Foundations (`D1`)
Dark-primary/light-parity token system, sourced entirely from `prototype.html`'s live CSS custom
properties — nothing invented. IBM colour-blind-safe five-hue status set, darkened for light-mode AA.
System font stack, `tabular-nums` on all numeric cells. 9-step spacing scale, 4 radius steps, 2 shadow
tiers. Motion: reduced-motion kill-switch already shipping; the load-bearing rule is **highlight-once-
then-settle** — no live row (new bid, queue re-sort, countdown crossing final) pulses continuously.
Two token categories are explicitly `[NEEDS INPUT]` to formalize: the type scale (14 de-facto sizes,
no formal array) and motion durations (6 inline values, no token object). See `D1` §01.

### 📄 02 · Components (`D1`)
25 components documented — 20 built-and-observed against the running prototype, 2 spec-only from
scratch (Modal/Sheet; Toast — **D1 recommends not building Toast**, since the prototype already proves
inline state-swap + `aria-live` resolves bid outcome, POD submit, and claim without a third notification
surface), 3 built-base-with-a11y-gaps flagged inline (Form field's missing `aria-describedby`/
`aria-live` wiring; Skeleton's missing `aria-busy`; Signature pad's WCAG 2.5.7 keyboard/switch-access
gap). Every component traces to one of the 8 built screens. See `D1` §02 for the full state matrix per
component (rest/hover/focus/active/disabled/loading/error/selected/read-only).

### 📄 03 · Patterns (`D1`)
Five reusable shapes: dense table (sticky header, 2 pinned columns, exception-forward grouping), multi-
step form (step-pill progress, inline validation, read-only review step), timeline (scheduled-vs-actual
shown together, exceptions physically break the spine), work-queue (severity chip, one attached action,
claimed-by-name on contest), and the universal 8-state set (+Contested) every F9 screen must declare.
See `D1` §03.

### 📄 10 · Flow — Shipper (`D2`)
43 steps across 9 sub-flows: onboarding (2 `[NEW]` frames — org setup has no F9 screen at all),
Post a Load (`SCR-901`, built, 4-step form), Auction Watch (`SCR-902`, built, eligibility-gate-first
per `DEC-LOCK-001`), the unresolved Award fork (`SCR-903`, blocked on §4's DEC-307 question),
amendment/withdraw-republish, cancellation-by-stage (flags the BR-144/FRD contradiction — §3 below),
tracking (`SCR-904`, built, "truck-is-dark" honesty — never fabricates position), delivery outcome →
invoice consequence, and invoice review/dispute. See `D2` for the full step tables and 6 branch tables.

### 📄 11 · Flow — Carrier / Dispatcher (`D3`)
42 steps across 9 sub-flows, covering the union case `OWNER_OPERATOR` (owner+driver in one login) and
`CARRIER_DISPATCHER` (roster it doesn't drive) through the same screens. Onboarding/vetting has **no
F9 screen at all** (3 `[NEW]` frames, assembled as `SCR-917`/`918` below). Load Board (`SCR-910`, built)
and Bid & Comparison (`SCR-911`, built up to the rival-visibility fork — §4). **Award accept/decline
closes a gap D6 independently flagged** — 3 `[NEW]` frames, assembled as `SCR-919`. Fleet Assignment
(owner-op vs dispatcher diverge structurally), dispatch/en-route, and settlement/factoring. See `D3` for
the full state machine (bid idle→submitting→rejected→submitted→outbid→withdrawn is fully built) and 5
branch tables.

### 📄 12 · Flow — Driver, mobile (`D4`)
~28 steps: device onboarding (3 `[NEW]` frames — invite accept, sync-held-for-review, session-ended,
assembled as `SCR-927`-`929`), today's assignment (`SCR-920`, built, deliberately not a live HOS
countdown), heading to pickup, the pickup handover (dual-signature, highest-risk event pre-delivery), in
transit (passivity-by-design — driver is never nagged to check in), and delivery/POD (`SCR-924`, built,
full 7-step forced-choice sequence — **the single most consequential screen in the product**, already
correct by construction: no default, equal tap-count for clean vs exception). See `D4` for 4 branch
tables (arrival match/mismatch, pickup proceed/refuse/not-ready, delivery clean/exception/refused/
nobody-there, sync success/conflict).

### 📄 13 · Flow — Platform Ops (`D5`)
Exception Work Queue (`SCR-930`, built) and Exception Detail & Resolution (`SCR-931`, spec only,
covering three case kinds with one surface, forking action sets not the frame). Offline-POD sync
conflict is `SCR-931`'s highest-stakes new state (never last-write-wins). Configuration Console and
Impersonation Console are `[NEW]` (`SCR-934`/`935`) — neither had an F9 screen, only a permission row or
a named banner. **`SCR-932` (Claims Desk) and `SCR-933` (Silence/No-Response Monitor) are F9-specified
Ops screens that received zero design coverage in `D5`'s delivered file** — an assembler finding, not
one D5 or D6 flagged; see `DESIGN-GAPS.md` row 2.

### 📄 14 · Flow — Admin / Fraud review (`D5`)
Carrier Vetting Queue (`SCR-940`, maker-checker override chain), Fraud Case Review (`SCR-941`, four
classifications, **no cancel-in-transit affordance exists structurally** — a stated ceiling, not an
oversight), Selection Record/Audit Viewer (`SCR-942`, the *Montgomery*-driven immutable record), and
Enforcement Action (`SCR-943`). **Zero of these four screens is reachable from the built persona
switcher** — see `DESIGN-GAPS.md` row 8.

### 📄 20 · Cross-flow map (`D6`, assembler-extended)
The shared lifecycle table (one baton, four hands — and a fifth, the Consignee, with none), the six
cross-persona handoffs (H1-H6, each with its own failure mode), the consignee problem in full (§5
below), navigation/IA rules (permission-denied must render identical to not-found on enumeration-
sensitive screens), and the consolidated frame index (§2 below, extended from `D6` §5 with assembler-
assigned IDs for D2/D3's unnumbered `[NEW]` frames).

### 📄 90 · Deprecated / parked
Empty. No frame has been deprecated in this phase.

---

## 2 · Consolidated frame index

**31 F9-canonical + 10 `[NEW]`.** Where D2 and D3 left new frames unnumbered, the assembler assigned IDs
in the next free block on each page to avoid collision — see the collision note under the table.

| SCR | Screen | Persona / Page | Status | Source |
|---|---|---|---|---|
| 900 | Load Dashboard | Shipper / 10 | **Built** | F9, `D2` |
| 901 | Post a Load | Shipper / 10 | **Built** | F9, `D2` |
| 902 | Auction Watch | Shipper / 10 | **Built** | F9, `D2` |
| 903 | Award & Accept-Flow Monitor | Shipper / 10 | Spec only — blocked on DEC-307 (§4) | F9, `D2` |
| 904 | Shipment Tracker | Shipper / 10 | **Built** (`shipment-detail`) | F9, `D2` |
| 905 | Exception Inbox | Shipper / 10 | Spec only | F9, `D2` |
| 906 | Invoice Approval | Shipper / 10 | Spec only | F9, `D2` |
| 907 | Claim Intake | Shipper / 10 | Spec only | F9, `D2` |
| 908 | Standing & Cancellation History | Shipper / 10 | Spec only — unfulfillable, orphan `BR-106` | F9, `D2`, `D6` |
| **[NEW] 909** | Org Setup & Verification | Shipper / 10 | Spec only | `D2` §1, assembler ID |
| 910 | Load Board | Carrier / 11 | **Built** | F9, `D3` |
| 911 | Bid & Comparison | Carrier / 11 | **Built up to rival-visibility fork** | F9, `D3` — blocked, DEC-302/303 (§4) |
| 912 | Fleet Assignment | Carrier / 11 | Spec only | F9, `D3` |
| 913 | Active Loads | Carrier / 11 | Spec only | F9, `D3` |
| 914 | Breakdown / Exception Report | Carrier / 11 | Spec only | F9, `D3` |
| 915 | Driver & Equipment Roster | Carrier / 11 | Spec only | F9, `D3` |
| 916 | Settlement Status | Carrier / 11 | Spec only | F9, `D3` |
| **[NEW] 917** | Carrier Sign-up & Vetting Intake | Carrier / 11 | Spec only | `D3` §1, assembler ID |
| **[NEW] 918** | Vetting Status | Carrier / 11 | Spec only | `D3` §1, assembler ID |
| **[NEW] 919** | Award Notification & Accept | Carrier / 11 | Spec only — **closes D6's gap 7** | `D3` §5, assembler ID |
| 920 | Today (home) | Driver / 12 | **Built** | F9, `D4` |
| 921 | Navigation Handoff | Driver / 12 | Spec only — thinnest F9 spec | F9, `D4` |
| 922 | Arrival / Departure Capture | Driver / 12 | Spec only | F9, `D4` |
| 923 | Document Capture | Driver / 12 | Spec only | F9, `D4` |
| 924 | POD Capture | Driver / 12 | **Built** (full 7-step) | F9, `D4` |
| 925 | Report a Problem | Driver / 12 | Spec only | F9, `D4` |
| 926 | Language & Support | Driver / 12 | Spec only — thin | F9, `D4` |
| 927 | Invite Accept & Device Bind | Driver / 12 | Spec only | `[NEW]`, `D4` |
| 928 | Sync Held for Review | Driver / 12 | Spec only | `[NEW]`, `D4` |
| 929 | Session Ended | Driver / 12 | Spec only | `[NEW]`, `D4` |
| 930 | Exception Work Queue | Ops / 13 | **Built** (Default/Empty/Contested) | F9, `D5` |
| 931 | Exception Detail & Resolution | Ops / 13 | Spec only | F9, `D5` |
| 932 | Claims Desk | Ops / 13 | **No design coverage at all** | F9 — see `DESIGN-GAPS.md` row 2 |
| 933 | Silence / No-Response Monitor | Ops / 13 | **No design coverage at all** | F9 — see `DESIGN-GAPS.md` row 2 |
| 934 | Configuration Console | Ops / 13 | Spec only | `[NEW]`, `D5` |
| 935 | Impersonation Console | Ops / 13 | Spec only | `[NEW]`, `D5` |
| 940 | Carrier Vetting Queue | Admin/Fraud / 14 | Spec only — unreachable in built shell | F9, `D5` |
| 941 | Fraud Case Review | Admin/Fraud / 14 | Spec only — unreachable in built shell | F9, `D5` |
| 942 | Selection Record / Audit Viewer | Admin/Fraud / 14 | Spec only — unreachable in built shell | F9, `D5` |
| 943 | Enforcement Action | Admin/Fraud / 14 | Spec only — unreachable in built shell | F9, `D5` |
| **[NEW] 950** | Consignee Delivery Link | **No page owns this** | Recommended, not yet specified as frames | `D6` §3 |

**8/41 built** (900, 901, 902, 904, 910, 920, 924, 930) — matches the spine's stated count exactly.
**2 F9-specified screens (932, 933) have zero design authorship anywhere in D1-D6.**

**On `[NEW]` frame collisions.** No two agents independently claimed the same numeric ID — D2 and D3
left their new frames unnumbered (named only, e.g. "`[NEW]` Org Setup · Details"), while D4 (927-929)
and D5 (934-935) self-assigned into free blocks that happened not to overlap. The assembler filled D2's
and D3's frames into the next free slot per page (909, 917-919) to keep the index collision-free and
sequential. **The one real reconciliation needed was semantic, not numeric:** D6 filed a `CHALLENGE`
that carrier award accept/decline (`PERM-217`) had no claimed screen; D3, working in parallel, had
already added the exact frames needed. They agree — D3's answer is the `[NEW]` screen path D6 offered
as one of two options. Assigned `SCR-919`; engineering should keep `SCR-911`'s read-only "outcome" state
(F9 §2.2) and `SCR-919`'s accept/decline control from duplicating one action across two frames.

**Structural gap no individual agent could see:** `[NEW] SCR-950` (Consignee) has nowhere to live. The
spine's own page tree (§2) lists only five flow pages — Shipper, Carrier, Driver, Platform Ops,
Admin/Fraud — with no Consignee page. D6 correctly diagnosed the *screen* gap but the *page-tree* gap
sits one level up, invisible to an agent working inside a single page's scope. This document does not
resolve it; it is flagged in `DESIGN-GAPS.md` and needs a spine-level amendment (a page 15, or a
consignee sub-section under 20 · Cross-flow map) before `SCR-950` can be built as a real frame.

---

## 3 · Gap register (condensed — full ranked table in `DESIGN-GAPS.md`)

19 rows on record: 12 from D6's coverage audit, 1 accepted challenge from D5 (`ENT-324` missing case
types), 1 accepted challenge from D4 (lumper-fee pickup-side gap), 1 genuine BRD/FRD source conflict
from D2 (not a design question), 2 already-closed defects, and 2 the assembler found during this pass
(`SCR-932`/`933` uncovered; the page-tree gap above, folded into `SCR-950`'s row). **Every gap any agent
found is preserved — none was dropped at assembly.** Full table, ranked by consequence, with what
closing each one requires: `DESIGN-GAPS.md`.

Top of that ranking, in one line each:
1. `AWARD_LAPSED`/`AWARD_VOIDED_INELIGIBLE` has no ops resolution home — the system's own costliest
   named failure has no tool to fix it.
2. `SCR-932`/`SCR-933` — two statutory-clock-bearing Ops screens with zero design authorship.
3. The Consignee has no `SCR-` ID anywhere — the party whose signature closes the money loop.
4. `PARTIAL_DELIVERY` has no line-level split-POD UI, though `BR-507` requires one.
5. `BR-144` (BRD) contradicts the FRD's own `IN_TRANSIT → CANCELLED_BY_SHIPPER(charged)` adjacency and
   `EC-509` — a source conflict, not a design call.

---

## 4 · Build-blocking decisions (unresolved — options and consequences only)

### DEC-302/303 — Rival-bid visibility on `SCR-911`

Three agents converged independently on this being unresolved and consequential: F6 found "sealed +
standing-best-flag" a false middle ground; **F2 proved it leaks rival prices by construction** —
repeated decrements binary-search the true price even with amounts hidden; F9 shipped `SCR-911` on the
conservative default specifically to avoid a `BR-717` violation in production.

| Option | Adds | Consequence |
|---|---|---|
| (a) None — **built default** | Own bid + countdown + eligible-count only | Cleanest, least informative; weak re-bid signal |
| (b) Rank-only | "#2 of 5 eligible" badge, no amount | At small decrements, rank alone leaks approximate price (`EC-908`) |
| (c) Leading-price band | Rounded range, never exact | Named leak vector as decrements shrink (F2's finding) |

**Consequence of not deciding:** `SCR-911` is feature-complete as a swappable component on all three
shapes but cannot ship past (a) until `DEC-302`/`303` locks — shipping past it without a decision risks
a `BR-717` violation in production, not a UI bug.

### DEC-307 / `BR-155` / `EC-325` — May the shipper decline the lowest qualified bidder?

Asked independently in three separate documents and answered in none of them.

| Branch | `SCR-903` shape | Consequence |
|---|---|---|
| A — No decline right (`BR-304`, mechanical) | Pure accept/monitor screen | Simpler; matches "price decides, no human discretion" (`DEC-LOCK-001`) |
| B — Decline right, structured reason required | Adds a reason-code picker tied to on-file carrier data, feeding the immutable selection record (`ENT-312`) | Materially different screen — not a variant of A, cannot be "built either way later" without rework |

**Consequence of not deciding:** `D2` flags this as the flow's single most-abandonment-prone failure
state has no bearing here, but `SCR-903` itself cannot leave spec — the two branches are structurally
different screens, and D2's own `CHALLENGE` says so explicitly.

### DEC-700 — HOS: planning signal vs. system of record

| Option | Shape | Consequence |
|---|---|---|
| A | No hours UI anywhere | Simplest; no feasibility signal to driver or dispatcher |
| B — assumed by `D4`/`D3` for spec purposes only | Bounded `FEASIBLE`/`INFEASIBLE` badge, never a ticking clock (`EC-912`'s "not evaluated" honest default) | `SCR-920`/`SCR-915`/`SCR-912` designed against this shape; **not wired**, nothing renders without the lock |
| C | Full RODS dashboard | **Reverses an already-locked data-minimisation constraint** (§14/F12) — F7 and the assembler both recommend against this |

**Consequence of not deciding:** `SCR-920` and `SCR-915` cannot finalize; if Boss locks Option A, the
badge design in `D4`/`D3` is deleted, not hidden — it was never meant to survive that outcome.

---

## Handoff

Implementation → `frontend-engineer-agent` (React 19 + Tailwind 4 + shadcn/ui v4; tokens map directly to
a Tailwind 4 `@theme` block per `D1`). A11y audit pre-ship → coordinate `frontend-engineer-agent`
(axe-core in the same PR that builds each `[SPEC-gap]` component `D1` flags). The three decisions in §4
need Boss, not either agent. The `DESIGN-GAPS.md` register — especially rows 1, 2, 5, and 6 — should be
triaged before `SCR-911`, `SCR-924`'s partial-delivery state, `SCR-931`, or the Admin/Fraud persona entry
are built.
