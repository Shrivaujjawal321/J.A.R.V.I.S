# Freight Reverse-Auction Marketplace — Complete Design Map

A US-jurisdiction freight marketplace where shippers post loads and carriers bid the price DOWN — the lowest qualified bid wins. This document is the complete, step-by-step design of the product: 138 user steps across four personas, 24 branch points, 41 screens, 19 known gaps and 3 decisions still open.

Every step below states six things: the screen the user is looking at, what they see, what they do, what the system does behind it, where they go next, and what happens when it fails. Nothing here is illustrative — it is the specification.

## How this document is organised

1. **The five participants** — who touches the product, and the one who never gets a screen.
2. **The load lifecycle** — the single chain of custody, and every handover in it.
3. **Four persona flows** — Shipper, Carrier/Dispatcher, Driver, Platform Ops/Admin. Each flow is grouped into stages; each stage lists its steps; each step is fully defined.
4. **Screen inventory** — every screen, its persona, and whether it is built or still on paper.
5. **Known gaps** — what the design audit found missing, ranked by consequence.
6. **Open decisions** — the forks nobody has settled yet, with the consequence of each option.
7. **Cross-cutting rules** — offline behaviour, permissions, screen states, accessibility.
8. **ID glossary** — how to read the reference codes used throughout.

# 1. The five participants

Four personas have screens. The fifth signs the document that closes the shipment and releases the money — and has no screen at all.

## 1.1 Shipper

Posts the load, watches the auction, awards it, tracks the freight, approves the invoice. Their declaration of weight, hazmat and dock access is what every bid is priced against — under-declare and the load gets re-priced or refused at the dock.

- **Design page:** 10
- **Steps in this flow:** 44
- **Stages:** 9

## 1.2 Carrier / Dispatcher

Bids on loads, accepts or declines the award, assigns a driver and a truck, manages the run, gets paid. Eligibility is checked per driver-plus-equipment combination, not per company — a carrier can be eligible for one load and invisible on the next.

- **Design page:** 11
- **Steps in this flow:** 42
- **Stages:** 7

## 1.3 Driver (mobile)

One phone, one job at a time. Arrives, counts the freight, captures documents and signatures, drives, reports problems, delivers. Every capture works offline first — a signature is never blocked by a dead signal.

- **Design page:** 12
- **Steps in this flow:** 25
- **Stages:** 5

## 1.4 Platform Ops / Admin

Works the exception queue, resolves what the automation could not, vets carriers, reviews fraud, and reads the audit trail. The safety net for every other flow.

- **Design page:** 13-14
- **Steps in this flow:** 27
- **Stages:** 7

## 1.5 Consignee — the receiver

The party who signs for the freight on the driver's phone. They never create an account, never install anything, and have no screen of their own anywhere in the product. Their entire surface is a tokenised, expiring, single-purpose link. Their signature is what moves the load to POD_CAPTURED and opens the invoice.

- **Screens owned:** none — see the gap register
- **Why it matters:** the participant with the most influence over when money moves is specified only as an API contract

# 2. The load lifecycle — one baton, four hands

A load moves through one chain of states. At every point exactly one participant is holding the baton, the others are only watching. These are the handovers, in order.

## 2.1 DRAFT → PUBLISHED

- **Who acts:** Shpr (`SHIPPER_LOAD_POSTER`)
- **What they see:** `[SCR-901]` multi-step form, autosaved draft
- **Who is only notified:** — (`EVT-1000`, T3, Shpr IA only)

## 2.2 AUCTION_OPEN → EXTENDED → CLOSED

- **Who acts:** Shpr watches; eligible Disp bid
- **What they see:** `[SCR-902]` live bids (Shpr) / `[SCR-911]` bid loop (Disp)
- **Who is only notified:** Ineligible carriers: nothing — `PERM-230` denies to not-found

## 2.3 AUCTION_FAILED_*

- **Who acts:** Shpr
- **What they see:** `[SCR-902]` failed, named reason
- **Who is only notified:** Disp: `EVT-1004` DG only

## 2.4 AWARD_PENDING → AWARDED

- **Who acts:** System re-verifies; Disp accepts/declines (`PERM-217`)
- **What they see:** Shpr: `[SCR-903]` "verifying" (`EC-902`) → outcome. Disp: no dedicated screen — see §6
- **Who is only notified:** Ops: `EVT-1005` DG

## 2.5 AWARD_ACCEPTED

- **Who acts:** Disp (`+ACCEPT_AWARD`)
- **What they see:** Fleet binding at `[SCR-912]`
- **Who is only notified:** Shpr `EVT-1010` IA,EM

## 2.6 AWARD_DECLINED/LAPSED/VOIDED_INELIGIBLE

- **Who acts:** Nobody — this is where the baton drops
- **What they see:** Shpr `[SCR-903]` sees decline/lapse
- **Who is only notified:** Ops `EVT-1008`/`1009` — no queue owns it, §6

## 2.7 PICKUP_SCHEDULED → AT_PICKUP

- **Who acts:** Drv
- **What they see:** `[SCR-922]` arrival/departure
- **Who is only notified:** Shpr `[SCR-904]`, Disp `[SCR-913]`

## 2.8 CARRIER_NO_SHOW/SHIPPER_NOT_READY/PICKUP_REFUSED

- **Who acts:** Ops if unresolved
- **What they see:** No dedicated SCR-, folds into exception banners
- **Who is only notified:** Both sides `EVT-1014/1015/1016`

## 2.9 PICKED_UP → IN_TRANSIT

- **Who acts:** Drv
- **What they see:** `[SCR-920]` one primary action
- **Who is only notified:** Shpr `[SCR-904]`, Disp `[SCR-913]`

## 2.10 TRANSIT_EXCEPTION

- **Who acts:** Drv or Disp reports; Ops resolves
- **What they see:** `[SCR-925]`/`[SCR-914]` → `[SCR-930]`/`[SCR-931]`
- **Who is only notified:** Shpr `EVT-1021` IA,EM

## 2.11 AT_DROP → DELIVERED/DELIVERY_ATTEMPTED_NO_RECEIVER

- **Who acts:** Drv captures; consignee signs on the driver's device
- **What they see:** `[SCR-924]` forced choice
- **Who is only notified:** Cnsg: OOB link only, never in-app

## 2.12 PARTIAL_DELIVERY

- **Who acts:** Drv
- **What they see:** No line-level UI named — §6

## 2.13 DELIVERY_REFUSED → RETURN_TO_ORIGIN

- **Who acts:** Drv/Ops
- **What they see:** RTO has no SCR- at all — §6
- **Who is only notified:** Shpr `EVT-1026` T0

## 2.14 POD_CAPTURED → INVOICE_ISSUED → SETTLED

- **Who acts:** Shpr approves/disputes; Disp views
- **What they see:** `[SCR-906]`, `[SCR-916]`
- **Who is only notified:** Ops `EVT-1041` line-held → DG only, not real-time

## 2.15 ExceptionCase any type, OPEN → RESOLVED

- **Who acts:** Ops (`PLATFORM_EXCEPTION_DESK`)
- **What they see:** `[SCR-930]`→`[SCR-931]`
- **Who is only notified:** Shpr/Disp per §12.1's matrix

# 3. Shipper flow — 44 steps

Design page 10. Source file `D2-flow-shipper.md`.

## 3.1 Onboarding and first load

*Stage as written in the spec: 1. Onboarding and first load (F1 §5.2/5.3).*

### 3.1 · Step S1 — Org Setup · Details

- **Screen:** `[NEW] Org Setup · Details`
- **User sees:** Org-type (SHIPPER), legal name, EIN, admin credentials
- **User does:** Submits
- **System does:** `ENT-300 Organization(SHIPPER)` + `ENT-301 User` as `SHIPPER_ORG_ADMIN` (FR-100)
- **Goes to:** S2
- **If it fails:** `ERR-500/501` field errors; dedupe check `[NEEDS INPUT]`

### 3.1 · Step S2 — Org Setup · Verification pending

- **Screen:** `[NEW] Org Setup · Verification pending`
- **User sees:** "Verifying" — IAL1 + domain-verified email (FR-104)
- **User does:** Waits; can already log in
- **System does:** `PENDING_VERIFICATION`; login allowed, publish is not (FR-103)
- **Goes to:** S3 on pass
- **If it fails:** Fail → `[NEW] Verification failed`, reason shown, resubmit

### 3.1 · Step S3 — Org Setup · Payment standing

- **Screen:** `[NEW] Org Setup · Payment standing`
- **User sees:** Standing/credit check status (BR-104/105)
- **User does:** Submits reference `[NEEDS INPUT: check standard]`
- **System does:** Dated standing record on a re-check cycle
- **Goes to:** S4
- **If it fails:** Below threshold → org exists but publish-blocked, reason shown (BR-107)

### 3.1 · Step S4 — Org Setup · Invite team

- **Screen:** `[NEW] Org Setup · Invite team`
- **User sees:** Invite by email/phone, role picker (ROLE-201/202/203/204)
- **User does:** Sends invite(s), or skips (owner-op, FR-102)
- **System does:** Single-use, expiring, role-tagged invite (FR-106)
- **Goes to:** SCR-900
- **If it fails:** Bounce/expiry → resend on same frame

### 3.1 · Step S5 — SCR-900 · Loads dashboard · Empty

- **Screen:** SCR-900 · Loads dashboard · Empty `[BUILT]`
- **User sees:** "No loads yet — publish one"
- **User does:** Clicks Post a load
- **Goes to:** SCR-901 Step 1
- **If it fails:** n/a — valid first-run state

### 3.1 · Step S6 — SCR-900 · Loads dashboard · Default

- **Screen:** SCR-900 · Loads dashboard · Default `[BUILT]`
- **User sees:** Exceptions ranked above on-track loads
- **User does:** Browses, opens a load
- **System does:** Reads `own_org`/`own_site` scope (PERM-206)
- **Goes to:** Relevant screen per row status
- **If it fails:** `ERR-531` on stale/out-of-scope link — not-found, never forbidden

### 3.1 · Rules for this stage

- Permission. `SHIPPER_LOAD_POSTER` (ROLE-201) sees/publishes `own_site` only; only `SHIPPER_ORG_ADMIN` (ROLE-200) sees org-wide and cancels post-award (PERM-201–204)

## 3.2 Post a load — the declaration

*Stage as written in the spec: 2. Post a load — the declaration (BR-110–127, SCR-901 [BUILT]).*

### 3.2 · Step S7 — SCR-901 · Step 1 Lane & schedule

- **Screen:** SCR-901 · Step 1 Lane & schedule `[BUILT]`
- **User sees:** Addresses, appointment windows, tight-window hint
- **User does:** Fills, clicks Next
- **System does:** Autosaves (BR-103/125)
- **Goes to:** Step 2
- **If it fails:** `ERR-500` named field; `ERR-504` if drop precedes pickup

### 3.2 · Step S8 — SCR-901 · Step 2 Equipment & cargo

- **Screen:** SCR-901 · Step 2 Equipment & cargo `[BUILT]`
- **User sees:** Trailer type (closed set incl. tanker, BR-111) — the shipper's only hard equipment choice; Tractor requirement is a soft preference only, since tractor and trailer are matched independently at bid time (`ENT-303`/`ENT-304`, no FK)
- **User does:** Picks trailer; reefer shows temp range; enters commodity/weight/dims; toggles hazmat + declared value
- **System does:** Validates `ERR-505` conflicts (e.g. temp range on dry van)
- **Goes to:** Step 3
- **If it fails:** `ERR-503` out-of-range weight; `ERR-505` equipment conflict

### 3.2 · Step S9 — SCR-901 · Step 3 Auction settings

- **Screen:** SCR-901 · Step 3 Auction settings `[BUILT]`
- **User sees:** Duration, optional ceiling, anti-snipe/early-close toggles
- **User does:** Sets parameters
- **System does:** Ceiling math validated
- **Goes to:** Step 4
- **If it fails:** `ERR-523` ceiling ≤0 or ≤ min decrement

### 3.2 · Step S10 — SCR-901 · Step 4 Review & publish

- **Screen:** SCR-901 · Step 4 Review & publish `[BUILT]`
- **User sees:** Full summary; commitment banner: bids priced against this declaration, dock discrepancy carries consequences (BR-121)
- **User does:** Acknowledges, clicks Publish
- **System does:** `ERR-507` completeness check, then `PUBLISHED`; declaration snapshot retained immutably (BR-122)
- **Goes to:** SCR-900 new row; `AUCTION_OPEN` per duration
- **If it fails:** `ERR-507` names the missing field, doesn't silently reject

### 3.2 · Step S11 — SCR-901 · Partial (autosaved draft)

- **Screen:** SCR-901 · Partial (autosaved draft) `[BUILT]`
- **User sees:** "Draft autosaved 12s ago"
- **User does:** Leaves, returns
- **System does:** Draft persists per user
- **Goes to:** Resumes at last step
- **If it fails:** Desk offline-draft persistence `[NEEDS INPUT]`

### 3.2 · Step S12 — SCR-900 · Draft row

- **Screen:** SCR-900 · Draft row `[BUILT]`
- **User sees:** 0 bids, "Continue draft"
- **User does:** Clicks through
- **Goes to:** SCR-901, resumes

### 3.2 · Branch point 1 — Field / Risk

3 outcomes.

- **Gross weight**
    - Risk: #1 re-trade cause — carrier re-weighs, mismatch, re-prices/refuses (BR-120)
    - Warning (built): Inline on the field
- **Hazmat flag**
    - Risk: Narrows pool; flagging after bids exist forces re-listing
    - Warning (built): Inline on checkbox
- **Dock access / load type**
    - Risk: Wrong dock type at arrival misses the appointment
    - Warning (built): Inline hint

### 3.2 · Rules for this stage

- Permission. `SHIPPER_LOAD_POSTER` publishes `own_site` (PERM-201); `SHIPPER_ORG_ADMIN` publishes org-wide (PERM-202). A viewer (ROLE-202) reaching SCR-901 sees Permission-denied, not a blank form

## 3.3 Auction open → watching bids

*Stage as written in the spec: 3. Auction open → watching bids (BR-301–318, SCR-902 [BUILT]).*

### 3.3 · Step S13 — SCR-902 · Live

- **Screen:** SCR-902 · Live `[BUILT]`
- **User sees:** Best eligible bid (`aria-live="polite"`), countdown, "14 eligible · 6 excluded" strip
- **User does:** Expands exclusion reasons
- **System does:** Lists reasons — insurance lapse, org suspension, no reefer trailer, related-party (BR-316)
- **Goes to:** Stays live, updates
- **If it fails:** Feed stalls → Stale, timestamped

### 3.3 · Step S14 — SCR-902 · Bid feed row is-new

- **Screen:** SCR-902 · Bid feed row `is-new` `[BUILT]`
- **User sees:** New bid: price, timestamp, authority type (motor carrier vs broker, BR-313)
- **User does:** Watches
- **System does:** Broker bids carry a visible flag icon
- **If it fails:** Undisclosed broker bid never reaches feed — `ERR-519` upstream

### 3.3 · Step S15 — SCR-902 · Extended

- **Screen:** SCR-902 · Extended `[BUILT]`
- **User sees:** "Extended +5min — not a reset, earlier bids stand"
- **User does:** Watches
- **System does:** `AUCTION_OPEN → AUCTION_EXTENDED`
- **Goes to:** Live

### 3.3 · Step S16 — SCR-902 · Thin market

- **Screen:** SCR-902 · Thin market `[BUILT]`
- **User sees:** "Only 1 bidder at close" — labelled, not competitive
- **User does:** Watches
- **System does:** EC-908 labelling; DEC-310 mechanism open, not decided here
- **Goes to:** Close per DEC-310

### 3.3 · Step S17 — SCR-902 · Closing — verifying

- **Screen:** SCR-902 · Closing — verifying `[BUILT]`
- **User sees:** "Verifying eligibility — not yet awarded"
- **User does:** Watches
- **System does:** `AWARD_PENDING` re-runs winner's gate (BR-302, EC-902)
- **Goes to:** S18 pass
- **If it fails:** Fail → `AWARD_VOIDED_INELIGIBLE`, `ERR-514`, cascades DEC-309

### 3.3 · Step S18 — SCR-902 · Failed (3 reasons)

- **Screen:** SCR-902 · Failed (3 reasons) `[BUILT]`
- **User sees:** "No bids" / "No eligible carrier" / "All bids above your limit"
- **User does:** Amends & republishes, or escalates
- **System does:** `AUCTION_FAILED_NO_BIDS`/`_NO_ELIGIBLE_CARRIER`/`_ALL_ABOVE_LIMIT`
- **Goes to:** Shipper decides next
- **If it fails:** — this *is* the failure frame

### 3.3 · Branch point 1 — Condition / Destination

3 outcomes.

- **Carrier passes gate**
    - Destination: Ranked, priced in feed
- **Carrier fails gate**
    - Destination: Never ranked (BR-301)
    - Consequence: Named in exclusion list (selection record)
- **Winner fails re-verify at close**
    - Destination: `AWARD_VOIDED_INELIGIBLE`
    - Consequence: `ERR-514`, cascades DEC-309 or re-auctions

### 3.3 · Branch point 2 — Condition / Shipper sees

3 outcomes.

- **New low bid arrives**
    - Shipper sees: Hero amount updates, feed flashes
    - Consequence: Prior bidder's status changes on *their* screen, not shown here (BR-314)
- **Bid withdrawn pre-close**
    - Shipper sees: Bid count decrements
    - Consequence: Recorded against bidder (BR-308), not named to shipper
- **Auction closes**
    - Shipper sees: Best bid freezes into `AWARD_PENDING`
    - Consequence: S17

### 3.3 · Rules for this stage

- Branch — eligibility
- Branch — bid accepted / outbid (shipper-visible only):

## 3.4 Award — the unresolved fork

*Stage as written in the spec: 4. Award — the unresolved fork (BR-155, DEC-307, EC-325 — same question, build-blocking).*

### 3.4 · Step S19 — SCR-903 · Verifying

- **Screen:** SCR-903 · Verifying
- **User sees:** "Re-verifying," mirrors S17 (EC-902)
- **User does:** Waits
- **System does:** Gate re-run on winner
- **Goes to:** S20a/b
- **If it fails:** `AWARD_VOIDED_INELIGIBLE` → S18-style failure

### 3.4 · Step S20a — SCR-903 · Awarded (informational)

- **Screen:** SCR-903 · Awarded (informational)
- **User sees:** Winning carrier, price, authority type
- **User does:** Views selection-record excerpt (BR-303)
- **System does:** `AWARDED` → carrier's own accept/decline/lapse
- **Goes to:** S21

### 3.4 · Step S20b — SCR-903 · Award pending shipper review

- **Screen:** SCR-903 · Award pending shipper review `[NEW, contingent]`
- **User sees:** Winning bid + reason-code picker tied to on-file carrier data (BR-156, never free text)
- **User does:** Accepts, or declines with required reason code
- **System does:** Accept → as A; Decline → logged, actor + reason (BR-306), cascades DEC-309
- **Goes to:** S21 or cascade
- **If it fails:** Decline without valid code → blocked at form

### 3.4 · Step S21 — SCR-903 · Award accepted

- **Screen:** SCR-903 · Award accepted
- **User sees:** Rate confirmation generated (BR-600)
- **User does:** Views
- **System does:** `AWARD_ACCEPTED`, binding rate confirmation
- **Goes to:** SCR-904 pickup scheduling

### 3.4 · Step S22 — SCR-903 · Award declined / lapsed

- **Screen:** SCR-903 · Award declined / lapsed
- **User sees:** "Carrier declined" / "window expired"
- **User does:** Waits, or notified of cascade (EC-909 — Boss's call whether winner is told)
- **System does:** `AWARD_DECLINED`/`AWARD_LAPSED` → DEC-309 cascade or re-auction
- **Goes to:** S13 (re-auction) or S20a (cascade winner)
- **If it fails:** Pool exhausted → routes to S18

### 3.4 · Branch point 1 — Condition / Destination

4 outcomes.

- **Carrier accepts in window**
    - Destination: `AWARD_ACCEPTED`
    - Consequence: Binding rate confirmation, pickup opens
- **Carrier declines**
    - Destination: `AWARD_DECLINED`
    - Consequence: DEC-309 cascade or re-auction — mechanism open
- **Window lapses**
    - Destination: `AWARD_LAPSED`
    - Consequence: Same DEC-309 fork
- **(B only) Shipper declines lowest qualified bid**
    - Destination: Logged, reason-coded
    - Consequence: Same DEC-309 fork — not a new one

### 3.4 · Rules for this stage

- Branch — award accepted / declined / lapsed
- CHALLENGE: SCR-903 differs materially between branches — B needs a reason-code picker and review gate A never renders. Cannot be "built either way later" without rework; DEC-307/BR-155/EC-325 should lock before SCR-903 leaves spec

## 3.5 Amendment while bids are live

*Stage as written in the spec: 5. Amendment while bids are live (BR-135/136).*

### 3.5 · Step S23 — SCR-901 · Amend attempt (post-first-bid)

- **Screen:** SCR-901 · Amend attempt (post-first-bid)
- **User sees:** Material fields (weight beyond tolerance, equipment, commodity, hazmat, either address) read-only
- **User does:** Attempts to edit
- **System does:** Blocked at the field
- **Goes to:** S24
- **If it fails:** `ERR-513 LOAD_AMENDMENT_BLOCKED_LIVE_AUCTION`

### 3.5 · Step S24 — SCR-901 · Withdraw & republish (modal)

- **Screen:** SCR-901 · Withdraw & republish (modal)
- **User sees:** "Material change withdraws this auction; all current bids are lost."
- **User does:** Confirms, or cancels
- **System does:** Withdraws auction, voids bids; opens SCR-901 pre-filled for fresh publish
- **Goes to:** S7 (new cycle)
- **If it fails:** Cancel → returns to SCR-902 unchanged

### 3.5 · Step S25 — SCR-901 · Amend (pre-bid)

- **Screen:** SCR-901 · Amend (pre-bid)
- **User sees:** Direct field edit, no warning
- **User does:** Edits freely
- **System does:** Allowed pre-first-bid (BR-135)
- **Goes to:** Re-publish
- **If it fails:** Same `ERR-500`-class validation as S7

### 3.5 · Rules for this stage

- withdraw-and-republish, never a live edit

## 3.6 Cancellation at each stage

*Stage as written in the spec: 6. Cancellation at each stage (BR-140–145, TONU).*

### 3.6 · Step S26 — SCR-900/902 · Cancel (pre-award)

- **Screen:** SCR-900/902 · Cancel (pre-award)
- **User sees:** "Cancel this load"
- **User does:** Confirms
- **System does:** Removed from auction, no standing record (BR-140)
- **Goes to:** SCR-900, row removed

### 3.6 · Step S27 — SCR-904 · Cancel modal · post-award pre-dispatch

- **Screen:** SCR-904 · Cancel modal · post-award pre-dispatch
- **User sees:** "Awarded, not yet dispatched — standing event, no fee."
- **User does:** Confirms
- **System does:** Standing event logged, no TONU (BR-141)
- **Goes to:** SCR-900

### 3.6 · Step S28 — SCR-904 · Cancel modal · post-dispatch pre-pickup

- **Screen:** SCR-904 · Cancel modal · post-dispatch pre-pickup
- **User sees:** "Truck already moving — this creates a TONU claim."
- **User does:** Confirms
- **System does:** TONU claim created, evidenced by dispatch fact (BR-142, standard `[NEEDS INPUT]`)
- **Goes to:** SCR-907 Claim Intake
- **If it fails:** Mandatory warning, not skippable

### 3.6 · Step S29 — SCR-904 · Cancel modal · mid-transit [per CHALLENGE]

- **Screen:** SCR-904 · Cancel modal · mid-transit `[per CHALLENGE]`
- **User sees:** "In transit — charged cancellation, linehaul-to-point + return costs."
- **User does:** Confirms
- **System does:** `IN_TRANSIT → CANCELLED_BY_SHIPPER(charged) → RETURN_TO_ORIGIN`
- **Goes to:** SCR-904 RTO tracking

### 3.6 · Step S30 — SCR-904 · Cancel unavailable · post-delivery

- **Screen:** SCR-904 · Cancel unavailable · post-delivery
- **User sees:** "Delivered — raise a claim or dispute instead."
- **User does:** Redirected
- **System does:** `ERR-516`
- **Goes to:** SCR-906/SCR-907
- **If it fails:** n/a — correct terminal state

### 3.6 · Step S31 — SCR-904 · SHIPPER_NOT_READY

- **Screen:** SCR-904 · `SHIPPER_NOT_READY`
- **User sees:** Distinct from carrier no-show, flagged shipper-caused
- **User does:** Acknowledges
- **System does:** TONU + detention claim against shipper (BR-143)
- **Goes to:** SCR-907

### 3.6 · Rules for this stage

- CHALLENGE: BR-144 says cancellation is "unavailable once `PICKED_UP`," but the FRD's own §3.3 adjacency lists `IN_TRANSIT → CANCELLED_BY_SHIPPER(charged)`, and `EC-509` reads *"shipper cancels post-pickup, pre-delivery: allowed, with a financial consequence — contrast `ERR-516`,"* which only fires at/after `POD_CAPTURED`. Two source docs disagree on the cutoff. This flow follows the FRD reading (cancel allowed through `IN_TRANSIT`, blocked from `POD_CAPTURED` on) — a real conflict to reconcile before build, not a design choice
- Permission. Pre-award cancel: `SHIPPER_LOAD_POSTER` (own authored loads) or `SHIPPER_ORG_ADMIN` org-wide (PERM-203/204). Post-award: `SHIPPER_ORG_ADMIN` only

## 3.7 Tracking to delivery

*Stage as written in the spec: 7. Tracking to delivery (BR-401/403).*

### 3.7 · Step S32 — SCR-904 · Default

- **Screen:** SCR-904 · Default `[BUILT]`
- **User sees:** Custody timeline; position at corridor/ETA band only (PERM-212) — never exact coordinates, that's the carrier's own view
- **User does:** Watches, messages ops
- **System does:** Renders custody events as they land

### 3.7 · Step S33 — SCR-904 · Stale

- **Screen:** SCR-904 · Stale
- **User sees:** "No status update — 4h12m," flagged not hidden (BR-401)
- **User does:** Messages carrier/ops
- **System does:** Missed-interval detection — the honest common case for small carriers
- **Goes to:** SCR-905/930 escalation

### 3.7 · Step S34 — SCR-904 · Transit exception

- **Screen:** SCR-904 · Transit exception
- **User sees:** Categorised sub-type, never a generic "delay" (BR-405)
- **User does:** Views, messages ops
- **System does:** Logged as accessorial-dispute evidence

### 3.7 · Rules for this stage

- Truck-is-dark honesty. SCR-904 never fabricates a position or a false-confident ETA when the feed is absent — it shows Stale, timestamped. Honest default for the small-carrier segment

## 3.8 Delivery outcome and invoice consequence

*Stage as written in the spec: 8. Delivery outcome and invoice consequence (§7.4 state table, BR-501–514).*

### 3.8 · Step S35 — SCR-904 · Delivered clear

- **Screen:** SCR-904 · Delivered clear
- **User sees:** "No exceptions"
- **User does:** Views
- **System does:** `DELIVERED → POD_CAPTURED`, lines undisputed (BR-601)
- **Goes to:** SCR-906 clean invoice

### 3.8 · Step S36 — SCR-904 · Delivered with exception

- **Screen:** SCR-904 · Delivered with exception
- **User sees:** Type/quantity/whose-count — a notation on `DELIVERED`, not a separate state (§7.4)
- **User does:** Views, may escalate
- **System does:** Line moves to `HELD` (BR-603)
- **Goes to:** SCR-906 mixed lines

### 3.8 · Step S37 — SCR-904 · Partial delivery

- **Screen:** SCR-904 · Partial delivery
- **User sees:** Genuine custody fork — some freight delivered, remainder routed
- **User does:** Views split status
- **System does:** Delivered portion invoices; remainder tracked, possible claim
- **Goes to:** SCR-906 + SCR-907

### 3.8 · Step S38 — SCR-904 · Delivery refused

- **Screen:** SCR-904 · Delivery refused
- **User sees:** Full refusal recorded
- **User does:** Initiates claim if warranted
- **System does:** → `RETURN_TO_ORIGIN`, no clean POD
- **Goes to:** SCR-907, RTO charges

### 3.8 · Step S39 — SCR-904 · No receiver

- **Screen:** SCR-904 · No receiver
- **User sees:** Arrival timestamp only, no POD, carrier retains custody (BR-509)
- **User does:** Arranges redelivery
- **System does:** Detention may accrue
- **Goes to:** Redelivery / SCR-907

### 3.8 · Branch point 1 — Outcome / Invoice effect

5 outcomes.

- **Clean**
    - Invoice effect: All lines settle undisputed
- **Exception (notation)**
    - Invoice effect: Affected line `HELD`; rest settle (BR-603)
- **Partial**
    - Invoice effect: Split — delivered lines settle, remainder pends claim/RTO
- **Refused**
    - Invoice effect: RTO charges added; original linehaul disputed
- **No receiver**
    - Invoice effect: No invoice trigger yet — redelivery or RTO next

### 3.8 · Rules for this stage

- Branch — delivery outcome → invoice

## 3.9 Invoice review and dispute

*Stage as written in the spec: 9. Invoice review and dispute (BR-600–604).*

### 3.9 · Step S40 — SCR-906 · Default (clean)

- **Screen:** SCR-906 · Default (clean)
- **User sees:** Lines reconciled to rate confirmation + accessorials (BR-601)
- **User does:** Approves
- **System does:** `INVOICE_ISSUED → INVOICE_FINALISED`
- **Goes to:** SETTLED

### 3.9 · Step S41 — SCR-906 · Partial (mixed held/clear)

- **Screen:** SCR-906 · Partial (mixed held/clear)
- **User sees:** Held and clear lines rendered distinctly, never blended
- **User does:** Approves clean lines; disputes the held one
- **System does:** Partial settlement — clean lines pay, held stays open (BR-603)
- **Goes to:** SETTLED (clean) / S42 (held)

### 3.9 · Step S42 — SCR-906 · Dispute a line

- **Screen:** SCR-906 · Dispute a line
- **User sees:** Structured form, references line + evidence
- **User does:** Submits
- **System does:** Opens `ExceptionCase(DISPUTE_MONEY)`; provisional invoice stands
- **Goes to:** SCR-905 tracks open exception

### 3.9 · Step S43 — SCR-906 · Resolved — credit note

- **Screen:** SCR-906 · Resolved — credit note
- **User sees:** Credit note references disputed line + claim ID, never a silent net (BR-604)
- **User does:** Views resolution
- **System does:** `ExceptionCase → RESOLVED`
- **Goes to:** SETTLED
- **If it fails:** Unresolved past window → escalation, cadence `[NEEDS INPUT]`

### 3.9 · Branch point 1 — Condition / Destination

4 outcomes.

- **All lines evidenced**
    - Destination: `SETTLED`
    - Consequence: Standard terms apply (BR-611, days `[NEEDS INPUT]`)
- **Line(s) disputed**
    - Destination: `HELD`; rest settle independently (BR-603)
    - Consequence: `ExceptionCase(DISPUTE_MONEY)` per line
- **Resolved shipper-favor**
    - Destination: Credit note, references claim ID
    - Consequence: Line re-enters settlement
- **Resolved carrier-favor**
    - Destination: Written disallowance (claims-desk side)
    - Consequence: Line settles at original amount

### 3.9 · Rules for this stage

- Branch — invoice clean / disputed

## 3.10 Summary

### 3.10 · Rules for this stage

- Counts. 43 steps (S1–S43), 9 flows, 20 frames (4 `[BUILT]`: SCR-900/901/902/904; 2 `[NEW]`: Org Setup + sub-states), 6 branch tables (eligibility, bid outcome, award outcome, cancellation-by-stage, delivery outcome, invoice clean/disputed) per spine §5
- Built vs. specified. Loads dashboard, Post a Load, Auction Watch, Shipment Tracker are real and verified, including non-default states. Award Monitor, Exception Inbox, Invoice Approval, Claim Intake, Standing History are spec-only
- Three questions only Boss can answer. 1. May the shipper decline the lowest qualified bidder (BR-155/DEC-307/EC-325)? Branches A/B in §4 build different SCR-903 screens — asked three times in source docs, answered zero. 2. Does a cascade winner get told they were second choice (EC-909)? Privacy vs. transparency. 3. What is the dispatch-proof standard (BR-142) that flips a cancel from free to a TONU claim? One `[NEEDS INPUT]` decides whether S27 or S28 fires for the same clock-time cancel
- CHALLENGE filed. §6 — BR-144 conflicts with the FRD's own `IN_TRANSIT → CANCELLED_BY_SHIPPER(charged)` adjacency and `EC-509`'s post-pickup-pre-delivery allowance. Followed the FRD reading; needs reconciliation before S29 is built either way
- Most likely abandonment point. Not the declaration form (scaffolded, autosaved) or auction watch (passive). It's S18 — "all bids above your limit" on SCR-902: shipper set a ceiling in good faith, market cleared above it, only paths forward are republish-and-wait or escalate — both slower than the original need, and the only failure state here with no structured next-best-action attached

# 4. Carrier / Dispatcher flow — 42 steps

Design page 11. Source file `D3-flow-carrier.md`.

## 4.1 Two carriers, one product

*Stage as written in the spec: 0. Two carriers, one product.*

### 4.1 · Rules for this stage

- `OWNER_OPERATOR` (ROLE-216) = union of `CARRIER_OWNER` ∪ `CARRIER_DRIVER` — one login is company, equipment owner and driver at once. `CARRIER_DISPATCHER` (ROLE-211) runs a roster it doesn't drive. Same screens serve both; divergence is who fills the tuple at S26 and never "who may accept an award" (owner-operator is a union, not blocked by any maker-checker rule — §4.5)

## 4.2 Onboarding & vetting

*Stage as written in the spec: 1. Onboarding & vetting (FRD §5.2, §15).*

### 4.2 · Step S1 — Carrier · Sign-up · Default. *F9 has no carrier onboarding screen, only…

- **Screen:** `[NEW]` Carrier · Sign-up · Default. *F9 has no carrier onboarding screen, only SCR-940 (ops queue).*
- **User sees:** Org-type + owner-operator toggle (skips forced second user, FR-102)
- **User does:** Enters MC/USDOT
- **System does:** Org created `PENDING_VERIFICATION`
- **Goes to:** S2
- **If it fails:** Duplicate MC → account-exists error

### 4.2 · Step S2 — IAL2 proofing

- **Screen:** `[NEW]` · IAL2 proofing
- **User sees:** Doc + liveness (FR-101)
- **User does:** Uploads ID
- **System does:** Identity check queued
- **Goes to:** S3
- **If it fails:** Unreadable → inline retake

### 4.2 · Step S3 — Document upload

- **Screen:** `[NEW]` · Document upload
- **User sees:** Checklist: authority cert, COI (BR-204), safety consent, W-9, first driver's CDL
- **User does:** Uploads each; saves partial
- **System does:** `CredentialDocument` rows, source=self-reported
- **Goes to:** S4
- **If it fails:** Missing doc → `ERR-500`, field named

### 4.2 · Step S4 — Vetting Status · Pending. *No carrier-facing counterpart to SCR-940…

- **Screen:** `[NEW]` Vetting Status · Pending. *No carrier-facing counterpart to SCR-940 exists.*
- **User sees:** "Under review," which checks auto-cleared vs. await reviewer (Partial data)
- **User does:** Browses read-only; cannot open SCR-911
- **System does:** Ops reviews via SCR-940
- **Goes to:** Branch 1.1
- **If it fails:** Upstream feed unreachable → stale flag, never auto-fails (§15.3)

### 4.2 · Step S5 — Rejected

- **Screen:** `[NEW]` · Rejected
- **User sees:** Named reason per element (FR-1302)
- **User does:** Re-uploads failing doc only
- **System does:** Addendum record
- **Goes to:** S4

### 4.2 · Step S6 — Approved

- **Screen:** `[NEW]` · Approved
- **User sees:** "Eligible to bid"
- **User does:** Continues
- **System does:** Org enters eligible pool (per-load computed, not a flag)
- **Goes to:** S10

### 4.2 · Step S7 — SCR-915 Roster · Empty (owner-operator pre-filled self+one truck)

- **Screen:** SCR-915 Roster · Empty (owner-operator pre-filled self+one truck)
- **User sees:** Prompt to add tractor/trailer/driver
- **User does:** Adds records
- **System does:** Verifier+time-attributed (FR-735)
- **Goes to:** S8
- **If it fails:** Trailer type outside taxonomy → flagged, not blocked

### 4.2 · Step S8 — SCR-915 · Default

- **Screen:** SCR-915 · Default
- **User sees:** Expiry countdown per doc (BR-220)
- **Goes to:** S10
- **If it fails:** Already-expired credential → asset shows `Error`, excluded pre-bid

### 4.2 · Branch point 1 — Condition / Destination

5 outcomes.

- **Approved (PERM-240)**
    - Destination: S6
    - Consequence: Enters pool; eligibility still per-load, not wholesale
- **Rejected**
    - Destination: S5
    - Consequence: Reasons + re-submit loop
- **Pending, automation clear**
    - Destination: S4
    - Consequence: No shortcut — human approval required (BR-908)
- **Overridden despite FAIL**
    - Destination: S6, flagged
    - Consequence: Named-person override (PERM-260); addendum not edit; itself evidence later (FR-1352) — carrier sees only "approved"
- **Org suspended post-approval**
    - Destination: `[SCR-910] · Permission denied` (built)
    - Consequence: New bids/awards blocked; in-flight untouched (BR-230)

### 4.2 · Rules for this stage

- Branch 1.1 — vetting outcome

## 4.3 Load board — eligibility is per-tuple, not per-carrier

*Stage as written in the spec: 2. Load board — eligibility is per-tuple, not per-carrier.*

### 4.3 · Step S10 — [SCR-910] · Default (built)

- **Screen:** `[SCR-910] · Default` (built)
- **User sees:** Only loads with ≥1 eligible tuple — filtered server-side, never client-hidden (non-eligible = not-found, PERM-230)
- **User does:** Filters, saves view
- **System does:** Re-evaluated per current asset/driver availability
- **Goes to:** S10

### 4.3 · Step S11 — [SCR-910] · Loading

- **Screen:** `[SCR-910] · Loading`
- **User sees:** Row skeletons
- **Goes to:** S10
- **If it fails:** Timeout → Error, retry

### 4.3 · Step S12 — [SCR-910] · Empty

- **Screen:** `[SCR-910] · Empty`
- **User sees:** Reason named ("reefer at capacity through Wed"), never a bare grid
- **User does:** Adjusts availability or waits
- **Goes to:** S10 on match

### 4.3 · Step S13 — [SCR-910] · Permission denied (built)

- **Screen:** `[SCR-910] · Permission denied` (built)
- **User sees:** Named reason (COI lapse), one-click remediation
- **User does:** Uploads renewal
- **System does:** Single-doc re-review
- **Goes to:** S6-equiv

### 4.3 · Step S14 — [SCR-910] · Stale data

- **Screen:** `[SCR-910] · Stale data`
- **User sees:** "Showing cached board, reconnecting"
- **User does:** Retries
- **System does:** Re-syncs
- **Goes to:** S10
- **If it fails:** Persistent offline → badge, cached list, no phantom bid affordance

### 4.3 · Rules for this stage

- Non-obvious: a listed load is not a bid-time guarantee — FR-600 re-checks per bid. A truck visible now can lose eligibility to a double-booking the instant before submit. Must read as normal (BR-200), named plainly in S17, not a bug

## 4.4 Placing a bid — built, state machine verified

*Stage as written in the spec: 3. Placing a bid — built, state machine verified.*

### 4.4 · Step S15 — idle (built)

- **Screen:** `· idle` (built)
- **User sees:** Price field, countdown, eligible-count, note that rival amounts are hidden
- **User does:** Enters price, submits
- **System does:** `Idempotency-Key` attached
- **Goes to:** S16
- **If it fails:** Malformed → inline `ERR-501`

### 4.4 · Step S16 — submitting (built)

- **Screen:** `· submitting` (built)
- **User sees:** Spinner, button disabled, no double-submit
- **System does:** `eligibility()` re-checked live
- **Goes to:** S17/S18
- **If it fails:** Network drop → retried same key, never a silent duplicate

### 4.4 · Step S17 — rejected

- **Screen:** `· rejected [NEW state]`
- **User sees:** Explicit reason + failing tuple element, never bare "failed"
- **User does:** Fixes element or picks another truck
- **System does:** Logged as attempt only, never a bid row
- **Goes to:** S15

### 4.4 · Step S18 — submitted (built)

- **Screen:** `· submitted` (built)
- **User sees:** "Bid received — $X, locked until close" — explicit, never silent
- **User does:** Watches or leaves
- **Goes to:** S18/S19

### 4.4 · Step S19 — outbid (built)

- **Screen:** `· outbid` (built)
- **User sees:** "You've been outbid," prior amount shown, new field pre-focused
- **User does:** Re-bids or lets stand
- **System does:** New bid supersedes for ranking; both retained
- **Goes to:** S16
- **If it fails:** Below `min_decrement` (`DEC-311`) → `ERR-512`, field-level

### 4.4 · Step S20 — withdrawn

- **Screen:** `· withdrawn`
- **User sees:** "Withdrawn — recorded against your history"
- **System does:** Policy-gated (`[NEEDS INPUT]`)
- **Goes to:** S15
- **If it fails:** Post-close withdrawal → decline-equivalent, penalty implication shown

### 4.4 · Branch point 1 — Outcome / Frame

5 outcomes.

- **Accepted, standing**
    - Frame: S18
    - Consequence: Locked, superseded only by a lower valid bid
- **Outbid**
    - Frame: S19
    - Consequence: Forces explicit re-bid decision, never auto-rebids
- **Rejected — ineligible**
    - Frame: S17
    - Consequence: Never ranked; attempt only
- **Withdrawn pre-close**
    - Frame: S20
    - Consequence: Against bidder's own standing, not visible to rivals
- **Closed, not selected**
    - Frame: Post-close card: "not selected," no clearing price (§4.4 mask)
    - Consequence: No action

### 4.4 · Rules for this stage

- Anti-pattern check: the built states already avoid it — every price change re-renders the panel's headline confirmed number. A toast fading without changing that number is the rejected pattern; do not regress when wiring real data
- Branch 3.1 — bid outcomes

## 4.5 The rival-visibility fork — build-blocking, not decided here

*Stage as written in the spec: 4. The rival-visibility fork — build-blocking, not decided here.*

### 4.5 · Branch point 1 — Option / Adds

3 outcomes.

- **(a) None (built default)**
    - Adds: Nothing beyond own bid + countdown + count
    - UI consequence: Cleanest, least informative
    - Risk: Weak signal for re-bid decisions
- **(b) Rank-only**
    - Adds: "#2 of 5 eligible" badge
    - UI consequence: No amount ever rendered
    - Risk: At small decrements, rank alone leaks approximate price (EC-908)
- **(c) Leading-price band**
    - Adds: Rounded range
    - UI consequence: Must never render exact figure
    - Risk: Named leak vector as decrements shrink (F2 finding)

### 4.5 · Rules for this stage

- CHALLENGE: shipping past (a) without `DEC-302`/`303` locked risks a `BR-717` violation in production, not a UI bug — same challenge F9 §2.2 already filed. D3 confirms the built default is safe; (b)/(c) are component-ready, not wired

## 4.6 Winning — award accept, decline, lapse

*Stage as written in the spec: 5. Winning — award accept, decline, lapse.*

### 4.6 · Step S21 — Award Notification & Accept · Default. *F9's carrier section has no…

- **Screen:** `[NEW]` Award Notification & Accept · Default. *F9's carrier section has no accept-award screen; SCR-903 is shipper-side only.* Full-screen interrupt, never a dismissible toast (mirrors SCR-920)
- **User sees:** Rate (linehaul+FSC+accessorials, BR-600), pickup window, countdown to lapse (`[NEEDS INPUT]` window)
- **User does:** Accept / Decline
- **System does:** Accept → `AWARDED → AWARD_ACCEPTED`; rate confirmation ack required
- **Goes to:** S22/S23
- **If it fails:** Idempotency-Key required; double-tap accept is a no-op

### 4.6 · Step S22 — Accepted

- **Screen:** `· Accepted`
- **User sees:** Confirmation, "assign driver & truck next"
- **User does:** Proceeds
- **System does:** Asset-lock candidate begins (finalises S27)
- **Goes to:** S27

### 4.6 · Step S23 — Declined

- **Screen:** `· Declined`
- **User sees:** Confirmation, no invented penalty framing
- **System does:** `AWARD_DECLINED` → cascade/re-auction (`DEC-309`)
- **Goes to:** exits

### 4.6 · Step S24 — Lapsed

- **Screen:** `· Lapsed`
- **User sees:** "Expired — no response in time"
- **System does:** `AWARD_LAPSED` automatic
- **Goes to:** exits
- **If it fails:** The failure F10 names costliest — see 5.1

### 4.6 · Step S25 — [SCR-916] Settlement · Default

- **Screen:** `[SCR-916]` Settlement · Default
- **User sees:** Rate confirmation on file
- **Goes to:** S27

### 4.6 · Branch point 1 — Outcome / Trigger

3 outcomes.

- **Accepted**
    - Trigger: Explicit tap in window
    - Consequence: → S27 assignment
- **Declined**
    - Trigger: Explicit tap
    - Consequence: Cascade/re-auction per `DEC-309`; no re-offer absent that decision
- **Lapsed**
    - Trigger: No response before window closes
    - Consequence: Same fork; T0 voice/ops-page escalation exists specifically so S21 is never missed

### 4.6 · Rules for this stage

- Branch 5.1 — award outcome

## 4.7 Assigning driver and truck — owner-operator vs dispatcher diverge

*Stage as written in the spec: 6. Assigning driver and truck — owner-operator vs dispatcher diverge.*

### 4.7 · Step S26 — [SCR-912] · Default — owner-op: pre-filled self+sole truck, one confirm

- **Screen:** `[SCR-912] · Default` — owner-op: pre-filled self+sole truck, one confirm
- **User sees:** Pre-bound tuple
- **User does:** Confirms
- **System does:** `EquipmentPairing` bound; eligibility re-run
- **Goes to:** S28

### 4.7 · Step S26d — [SCR-912] · Default — dispatcher: driver/tractor/trailer pickers,…

- **Screen:** `[SCR-912] · Default` — dispatcher: driver/tractor/trailer pickers, `AVAILABLE`-only per window
- **User sees:** Roster filtered by time-window (FR-720)
- **User does:** Selects each independently
- **System does:** Same binding call
- **Goes to:** S28
- **If it fails:** Committed-elsewhere pick → `ERR-537`, shown disabled with reason pre-selection

### 4.7 · Step S27 — Contested (EC-913)

- **Screen:** `· Contested` (EC-913)
- **User sees:** "Truck B unavailable — bound to LD-48xxx"
- **User does:** Picks another asset
- **System does:** Optimistic lock; losing dispatcher sees this live
- **Goes to:** S26d

### 4.7 · Step S28 — HOS check

- **Screen:** `· HOS check`
- **User sees:** "Checking…" then FEASIBLE/INFEASIBLE, never silent
- **System does:** Attested hours vs. estimated transit (FR-750/751)
- **Goes to:** S29/S30
- **If it fails:** Signal source down → "not evaluated," never false-safe green (EC-912)

### 4.7 · Step S29 — Valid

- **Screen:** `· Valid`
- **User sees:** Bound tuple, dispatch-ready
- **User does:** Confirms
- **System does:** `Assignment` finalised; asset lock applied
- **Goes to:** S32

### 4.7 · Step S30 — Error — HOS infeasible

- **Screen:** `· Error — HOS infeasible`
- **User sees:** Named reason
- **User does:** Reassigns, or overrides if `DEC-701`=warn-only
- **System does:** Hard-block vs. warn is `[NEEDS INPUT]`
- **Goes to:** S26d/S29

### 4.7 · Step S31 — Error — document lapsed

- **Screen:** `· Error — document lapsed`
- **User sees:** Named credential + blocked asset
- **User does:** Renews or picks another asset
- **System does:** That asset only excluded; award unaffected unless BR-218/219 timing
- **Goes to:** S26d

### 4.7 · Branch point 1 — Condition / Destination

4 outcomes.

- **Valid, HOS feasible**
    - Destination: S29
    - Consequence: Dispatch-ready
- **HOS infeasible**
    - Destination: S30
    - Consequence: Block or warn per `DEC-701`, never silent
- **Document lapsed on selected asset**
    - Destination: S31
    - Consequence: Asset excluded; award untouched unless lapse timing hits BR-218/219
- **Two dispatchers race one asset**
    - Destination: S27
    - Consequence: Loser sees explicit contested state, no silent overwrite

### 4.7 · Rules for this stage

- Branch 6.1 — assignment outcome

## 4.8 Dispatch & en-route management

*Stage as written in the spec: 7. Dispatch & en-route management.*

### 4.8 · Step S32 — [SCR-913] · Default

- **Screen:** `[SCR-913] · Default`
- **User sees:** Every truck in flight, exceptions ranked above on-track
- **User does:** Drills into a trip
- **Goes to:** S33

### 4.8 · Step S33 — trip detail, pre-pickup

- **Screen:** `· trip detail`, pre-pickup
- **User sees:** Bound tuple vs. expected
- **User does:** Substitutes driver/truck before pickup
- **System does:** Re-checks eligibility on new tuple (FR-713)
- **Goes to:** S26d
- **If it fails:** New tuple fails gate → substitution blocked, original stands

### 4.8 · Step S34 — trip detail, post-pickup

- **Screen:** `· trip detail`, post-pickup
- **User sees:** Same UI, flagged "requires a custody event"
- **User does:** Substitutes
- **System does:** Logged requester+reason; award record unchanged
- **Goes to:** S32
- **If it fails:** Undisclosed swap → fraud queue (EC-709: trailer-VIN mismatch is a named gap)

### 4.8 · Step S35 — [SCR-914] · Report breakdown

- **Screen:** `[SCR-914] · Report breakdown`
- **User sees:** Category picker (BR-405), evidence, relief request
- **User does:** Submits
- **System does:** `TRANSIT_EXCEPTION` case → SCR-930 (ops, built)
- **Goes to:** S32, flagged
- **If it fails:** Owner-operator, no org substitute (EC-705): "no internal relay available" shown explicitly, not hidden as generic error

### 4.8 · Step S36 — Pickup arrival check (driver-side, SCR-922/923, out of D3 ownership)

- **Screen:** Pickup arrival check (driver-side, SCR-922/923, out of D3 ownership)
- **User does:** Arriving driver+tractor+trailer checked against bound tuple (BR-221/227)
- **System does:** Match proceeds; mismatch holds+flags
- **Goes to:** S37/fraud
- **If it fails:** Arriving tuple ≠ bound tuple is the double-brokering signal (BR-221/224/806) — the one check dispatcher cannot self-clear; routes to ops

### 4.8 · Step S37 — [SCR-913] · in transit

- **Screen:** `[SCR-913] · in transit`
- **User sees:** Exact position (own fleet, PERM-261), ETA, milestones
- **User does:** Messages driver
- **Goes to:** delivery flow
- **If it fails:** Stale >2h → flagged banner, never hidden (BR-401)

## 4.9 Getting paid

*Stage as written in the spec: 8. Getting paid.*

### 4.9 · Step S38 — Default

- **Screen:** `· Default`
- **User sees:** Rate confirmation + accessorials + FSC, reconciled total (BR-601)
- **User does:** Reviews
- **System does:** Invoice composed against rate confirmation
- **Goes to:** S39
- **If it fails:** Bid *is* the rate-confirmation base by construction (BR-307) — no mismatch state possible

### 4.9 · Step S39 — Partial data

- **Screen:** `· Partial data`
- **User sees:** Some lines `HELD` (OS&D/dispute), rest paying standard cycle (BR-603)
- **User does:** Contacts ops on held line
- **System does:** Clean lines settle independently
- **Goes to:** S40

### 4.9 · Step S40 — factored

- **Screen:** `· factored`
- **User sees:** Remit-to shows factor's instructions, never carrier's own bank details, once NOA on file (BR-606/608)
- **User does:** Reviews, cannot override without sign-off
- **System does:** 100% payable routes to factor of record
- **Goes to:** S41
- **If it fails:** Forged/expired NOA → `ERR-557`, flagged to fraud, held not misrouted

### 4.9 · Step S41 — quick-pay offer

- **Screen:** `· quick-pay offer`
- **User sees:** Elective, disabled while any line `HELD` (BR-609/610)
- **User does:** Elects or declines
- **System does:** Funded from platform capital/financing partner
- **Goes to:** S42

### 4.9 · Step S42 — Settled

- **Screen:** `· Settled`
- **User sees:** Payout confirmed, 1099-NEC accrual updated
- **System does:** Load → `COMPLETED`
- **Goes to:** exits
- **If it fails:** Undisclosed factoring found mid-dispute → `ERR-560`, held, never double-paid

### 4.9 · Rules for this stage

- Counts. 42 numbered steps (S1-S42, S26/S26d owner-operator/dispatcher split) across 9 sub-flows · frames: 3 built (`SCR-910`, `SCR-911`, `SCR-930` referenced) + 13 spec-only F9 screens (`SCR-912`-`916` + states) + 9 `[NEW]` (sign-up ×3, vetting status ×3, award accept/decline/lapse ×3) · 5 branch tables (§1.1, §3.1, §5.1, §6.1, plus the eligibility-reasons pattern repeated inline at S17/S26d/S30/S31 rather than tabled twice)

# 5. Driver (mobile) flow — 25 steps

Design page 12. Source file `D4-flow-driver.md`.

## 5.1 Preamble

### 5.1 · Rules for this stage

- New screens, justified: - `[NEW] SCR-927` Driver · Invite Accept & Device Bind — F1 §5.3/§9 requires this handshake; F9 has no screen for it. - `[NEW] SCR-928` Driver · Sync Held for Review — FR-901/`ERR-550`–`553` route offline conflicts to a human queue; needs its own honest frame, distinct from ordinary pending-sync. - `[NEW] SCR-929` Driver · Session Ended — FR-128/FR-150/FR-152 revoke a device or session; driver needs to see *why*, not a blank login screen

## 5.2 Device onboarding

*Stage as written in the spec: 1. Device onboarding.*

### 5.2 · Step S1 — Invite Accept · Default

- **Screen:** `[NEW SCR-927] Invite Accept · Default`
- **User sees:** Carrier org name, dispatcher name, role, one "Accept" button
- **User does:** Taps accept
- **System does:** Validates single-use, expiring, phone-bound invite token (FR-106)
- **Goes to:** S2
- **If it fails:** Token expired/used → `Error`: "This invite has expired — ask your dispatcher to resend"

### 5.2 · Step S2 — OTP verify

- **Screen:** `[NEW SCR-927] · OTP verify`
- **User sees:** SMS code field, large numeric keypad
- **User does:** Enters 6-digit code
- **System does:** Verifies phone (FR-108); rate-limits retries
- **Goes to:** S3
- **If it fails:** Mismatch → inline retry; exhausted → "Ask your dispatcher to resend the invite"

### 5.2 · Step S3 — PIN/biometric setup

- **Screen:** `[NEW SCR-927] · PIN/biometric setup`
- **User sees:** Set local unlock
- **User does:** Sets PIN or enrolls biometric
- **System does:** Local-unlock layer atop server session (FR-112), never a substitute for it
- **Goes to:** S4
- **If it fails:** Biometric unavailable → PIN-only fallback, no dead end

### 5.2 · Step S4 — Device bind

- **Screen:** `[NEW SCR-927] · Device bind`
- **User sees:** "This phone is now your Jarvis Freight device"
- **User does:** Confirms
- **System does:** Refresh token bound to device/install id (FR-123); old device (if any) unaffected unless explicitly deregistered
- **Goes to:** S5

### 5.2 · Step S5 — Language

- **Screen:** `[NEW SCR-927] · Language`
- **User sees:** EN/ES toggle, persists
- **User does:** Picks language
- **System does:** Stored on driver record (BR-914)
- **Goes to:** S6

### 5.2 · Step S6 — [SCR-920] Today · Empty or Default

- **Screen:** `[SCR-920] Today · Empty` or `Default`
- **User sees:** No assignment yet, or today's load
- **User does:** Waits, or acts on S7+
- **Goes to:** §2

### 5.2 · Rules for this stage

- Lost phone mid-trip: admin deregisters the device (FR-128) → refresh token invalidated server-side → next app open shows `[NEW SCR-929] Session Ended` ("Your access was ended by Ironhide Trucking — call dispatch"), never a bare login screen implying the driver did something wrong. Admin re-invites on a replacement device → S1–S6 again; FR-153 requires the admin to bind the replacement session to the in-flight load before any further driver-scoped action — the trip/custody record itself persisted untouched (FR-152)
- Driver leaves carrier mid-trip: identical `SESSION_REVOKED` → `SCR-929`. The FRD names an honest gap here (EC-107): revoking the session does nothing to the loaded truck still parked somewhere. Flagged in the closing questions
- Not invented: EC-103 (shared family device, no "switch driver" flow) is explicitly unspecified in F1 — surfaced here, not guessed

## 5.3 Today's assignment — [SCR-920] · Default

*Stage as written in the spec: 2. Today's assignment — [SCR-920] · Default (built).*

### 5.3 · Rules for this stage

- HOS is deliberately not a live countdown. `DEC-700` is unresolved (Option A/B/C, §9.6 FRD). This design assumes Option B's shape only as a *badge*, never a ticking clock: `FEASIBLE` / `INFEASIBLE` / `Hours: not evaluated` (EC-912's honest default). A raw hours-remaining display would itself be Option C — the system-of-record posture already rejected by the minimisation constraint. If Boss locks Option A, the badge is deleted, not hidden
- The dark-driver case is designed by omission, on purpose. Nothing on `SCR-920` nags the driver to "check in." `NO_UPDATE_RECEIVED` (BR-401) is ops's and the shipper's problem to chase (F9 §4's notification table), not friction pushed back onto a driver who may have no signal at all

## 5.4 Heading to pickup

*Stage as written in the spec: 3. Heading to pickup.*

### 5.4 · Step S7 — [SCR-920] Today · Default

- **Screen:** `[SCR-920] Today · Default`
- **User sees:** "Start navigation" CTA
- **User does:** Taps
- **System does:** Hands off to external nav app
- **Goes to:** `[SCR-921]`
- **If it fails:** No nav app installed → inline "Open in browser maps" fallback

### 5.4 · Step S8 — [SCR-921] Navigation Handoff

- **Screen:** `[SCR-921] Navigation Handoff`
- **User sees:** One-tap confirmation only; app owns no in-app map
- **User does:** Confirms
- **System does:** Deep-links out
- **Goes to:** External app
- **If it fails:** Deep-link fails → returns to `SCR-920` with address copy-to-clipboard

### 5.4 · Step S9 — [SCR-922] Arrival Capture · Default

- **Screen:** `[SCR-922] Arrival Capture · Default`
- **User sees:** Geofence-assisted "You've arrived" prompt, or manual "I'm here"
- **User does:** Confirms arrival; enters/scans tractor plate + trailer VIN if not auto-paired
- **System does:** Geofence entry (FR-819 debounced) + FR-140 timestamp; compares tuple to bound Assignment
- **Goes to:** Branch — §5.1
- **If it fails:** No geofence on file → manual-only arrival, flagged `Partial data`

### 5.4 · Step S10 — Branch outcome

- **Screen:** Branch outcome
- **Goes to:** Match → `SCR-923`; Mismatch → `SCR-922 · Held`
- **If it fails:** See §5.1

## 5.5 The pickup handover — highest-risk event in the system

*Stage as written in the spec: 4. The pickup handover — highest-risk event in the system.*

### 5.5 · Step S11 — [SCR-923] Document Capture · Structured count

- **Screen:** `[SCR-923] Document Capture · Structured count`
- **User sees:** Declared vs. actual: piece/pallet count, weight if declared, condition, seal number
- **User does:** Confirms or edits against declared
- **System does:** Builds pickup record per BR-400
- **Goes to:** S12
- **If it fails:** Count doesn't match declaration → `Discrepancy hold`, see §5.2

### 5.5 · Step S12 — [SCR-923] · Photo

- **Screen:** `[SCR-923] · Photo`
- **User sees:** Camera CTA, BOL + seal + condition
- **User does:** Takes ≥1 photo
- **System does:** Unreadable image flagged before accept, not silently stored (BR-400/408, `ERR-506`)
- **Goes to:** S13
- **If it fails:** No camera permission → text-only notation fallback (EC-910), never blocks

### 5.5 · Step S13 — [SCR-923] · Dual acknowledgement

- **Screen:** `[SCR-923] · Dual acknowledgement`
- **User sees:** Same signature-pad component as POD (reused, not reinvented)
- **User does:** Driver + shipper rep each sign, printed name + role
- **System does:** BR-400 requires both acknowledgements + timestamp before `PICKED_UP` is reachable
- **Goes to:** S14
- **If it fails:** Shipper rep unavailable/refuses → cannot proceed to `PICKED_UP`; routes to §5.2's not-ready/refused branch

### 5.5 · Step S14 — [SCR-923] · Submitted

- **Screen:** `[SCR-923] · Submitted`
- **User sees:** "Pickup recorded" confirmation
- **System does:** Load state → `PICKED_UP`; F8 milestone `loaded` (claimed)
- **Goes to:** `[SCR-920] In transit`
- **If it fails:** Offline → queued locally, `Pending sync` (see §8)

## 5.6 Branch tables

*Stage as written in the spec: 5. Branch tables.*

### 5.6 · Branch point 1 — Condition / Destination

3 outcomes.

- **Driver session + entered tractor/trailer match bound Assignment tuple**
    - Destination: `SCR-922 · Arrival confirmed`
    - Consequence: FR-140 timestamp+geofence logged; → `SCR-923`
- **Disclosed, pre-approved relay/drop-and-hook substitution**
    - Destination: `SCR-922 · Arrival confirmed`
    - Consequence: Re-verified tuple, no case opened (FR-713)
- **Mismatch — wrong driver, wrong tractor, wrong trailer, undisclosed swap**
    - Destination: `SCR-922 · Held pending verification`
    - Consequence: FR-139 suspends further session-scoped actions on this load; `ExceptionCase(FRAUD_REVIEW)` opens (BR-806); driver sees "Dispatch is verifying this pickup — call them" and a Call button, never a raw `ARRIVAL_MISMATCH` code

### 5.6 · Branch point 2 — Condition / Destination

8 outcomes.

- **Ready, count/condition matches, correct equipment**
    - Destination: `SCR-923` proceeds → `PICKED_UP`
    - Consequence: Milestone `loaded` claimed
- **Freight not ready**
    - Destination: `SCR-922 · Not ready` (reason: not-ready / dock closed)
    - Consequence: `SHIPPER_NOT_READY`; TONU flag → §8.6 accessorial
- **Freight differs from declaration**
    - Destination: `SCR-923 · Discrepancy hold`
    - Consequence: BR-406 hold; resolution outcome (substitution confirmed vs. held) recorded before loading continues
- **Wrong equipment (trailer type mismatch)**
    - Destination: `SCR-922 · Refused`
    - Consequence: `PICKUP_REFUSED`, `EQUIPMENT_TYPE_MISMATCH`
- **Unsafe load**
    - Destination: `SCR-922 · Refused` (reason: unsafe)
    - Consequence: `PICKUP_REFUSED`, reason `UNSAFE_LOAD`, same-shift ops review
- **Seal missing where required**
    - Destination: `SCR-923 · Condition note`
    - Consequence: Logged, not blocking, re-verified at drop (BR-408) unless hazmat mandates it (BR-719)
- **Detention accruing**
    - Destination: `SCR-920` banner + `SCR-923` timer
    - Consequence: `detention_candidate_minutes` computed (FR-821); informational only, never blocks the driver
- **Lumper fee at pickup**
    - Destination: `SCR-923 · Lumper flag` (receipt photo)
    - Consequence: `CHALLENGE`: BR-516 scopes lumper capture to *delivery* only; the same event happens at pickup docks. Recommend the identical flag+receipt affordance at both ends

### 5.6 · Branch point 3 — Condition / Destination

4 outcomes.

- **Delivered clean**
    - Destination: `SCR-924` Step 3→6→7 (Clean path)
    - Consequence: `DELIVERED → POD_CAPTURED`; invoice opens clean
- **Delivered with exception (OS&D)**
    - Destination: `SCR-924` Step 3→3b→4(photo mandatory)→5→6→7
    - Consequence: OS&D notation (BR-503); invoice line held pending §8.9
- **Full refusal**
    - Destination: `SCR-922/924 · Refused` [specified, not yet built]
    - Consequence: `DELIVERY_REFUSED`, required reason code, `RETURN_TO_ORIGIN` custody event; no invoice line (BR-506)
- **Nobody present / hours closed**
    - Destination: `SCR-922 · No receiver` [spec only]
    - Consequence: `DELIVERY_ATTEMPTED_NO_RECEIVER`; arrival timestamp only, no POD, forced-choice screen never reached (BR-509)

### 5.6 · Branch point 4 — Condition / Destination

4 outcomes.

- **Queue applies cleanly, causal order matches canonical state**
    - Destination: Silent — "Delivered — recorded"
    - Consequence: EC-510, indistinguishable from a live submit
- **Load state advanced while dark (reassigned/cancelled/already-captured elsewhere)**
    - Destination: `[NEW SCR-928] Held for review`
    - Consequence: `ERR-550`→`524`; routed to human queue, never last-write-wins
- **Queue exceeds retention before reconnect**
    - Destination: `[NEW SCR-928] · Expired`
    - Consequence: `ERR-551`; ops-assisted recovery only
- **Device clock skew flags a money-bearing timestamp untrusted**
    - Destination: `[NEW SCR-928] · Timestamp held`
    - Consequence: `ERR-552`; same human-queue path

## 5.7 In transit

*Stage as written in the spec: 6. In transit.*

### 5.7 · Step S15 — [SCR-920] In transit · Default

- **Screen:** `[SCR-920] In transit · Default`
- **User sees:** ETA, next stop, exception banner if any, Report-a-problem always visible
- **User does:** Mostly nothing — position is passive (FR-800), not a manual check-in chore
- **System does:** Pings feed milestones/ETA (F8); `NO_UPDATE_RECEIVED` if dark, driver never nagged
- **Goes to:** S16/S17

### 5.7 · Step S16 — [SCR-925] Report a Problem · Category

- **Screen:** `[SCR-925] Report a Problem · Category`
- **User sees:** Breakdown / weather-closure / reefer-alarm / accident / theft / OOS-order / other
- **User does:** Picks category, attaches photo or voice note
- **System does:** `TRANSIT_EXCEPTION` sub-type opens (BR-405); high-priority sync queue if offline
- **Goes to:** `[SCR-920]` w/ open-exception card
- **If it fails:** Offline → queues, `Pending sync` badge, never silently dropped

### 5.7 · Step S17 — [SCR-920] · Interrupt (system-pushed)

- **Screen:** `[SCR-920] · Interrupt` (system-pushed)
- **User sees:** Full-screen, non-dismissible — e.g. telematics-detected reefer alarm
- **User does:** Acknowledges / calls dispatch
- **System does:** Full-screen interrupt per F9 §4 rule — never a toast for anything blocking
- **Goes to:** Back to Today or `SCR-925` for detail

### 5.7 · Step S18 — Driver truly dark (no signal, no update)

- **Screen:** Driver truly dark (no signal, no update)
- **User sees:** Last-known cached state stays visible, age-labelled
- **User does:** Nothing — by design
- **System does:** `NO_UPDATE_RECEIVED` flag visible to ops/shipper only
- **Goes to:** resumes at reconnect

## 5.8 Delivery and POD — [SCR-924]

*Stage as written in the spec: 7. Delivery and POD — [SCR-924] (built).*

### 5.8 · Step P1 — [SCR-924] POD · Arrival

- **Screen:** [SCR-924] POD · Arrival
- **User sees:** Arrival at drop confirmed
- **User does:** Confirms arrival
- **System does:** Count/condition folded into this screen
- **Goes to:** P2
- **If it fails:** Offline → captured locally, Pending sync
- **Note:** transcribed from the flow's prose description, not from a step table

### 5.8 · Step P2 — [SCR-924] POD · Forced choice

- **Screen:** [SCR-924] POD · Forced choice
- **User sees:** "Delivered clean" vs "Report exception" — no pre-selection, role="group"
- **User does:** Must pick one — Continue stays disabled until then
- **System does:** BR-501/502/505/512 satisfied by construction — no combined "confirm delivery" button
- **Goes to:** P3 clean · P3b exception
- **If it fails:** No default means no accidental clean-close
- **Note:** transcribed from the flow's prose description, not from a step table

### 5.8 · Step P3b — [SCR-924] POD · Exception detail

- **Screen:** [SCR-924] POD · Exception detail
- **User sees:** Type / qty / whose-count — structured, notes supplement only
- **User does:** Records the exception
- **System does:** OS&D notation (BR-503); invoice line held
- **Goes to:** P4
- **If it fails:** Same tap-count to signature as the clean path — exception is not punished with friction
- **Note:** transcribed from the flow's prose description, not from a step table

### 5.8 · Step P4 — [SCR-924] POD · Photo

- **Screen:** [SCR-924] POD · Photo
- **User sees:** Camera — optional on clean, mandatory on exception
- **User does:** Captures photo
- **System does:** Unreadable image flagged before accept (ERR-506)
- **Goes to:** P5
- **If it fails:** No camera permission → text-only notation fallback (EC-910)
- **Note:** transcribed from the flow's prose description, not from a step table

### 5.8 · Step P5 — [SCR-924] POD · Signature

- **Screen:** [SCR-924] POD · Signature
- **User sees:** Consignee signs on the DRIVER's device — printed name + role, no account
- **User does:** Consignee signs
- **System does:** Canvas aria-label'd; signature never blocked by connectivity (EC-901, FR-124)
- **Goes to:** P6
- **If it fails:** Consignee absent → DELIVERY_ATTEMPTED_NO_RECEIVER
- **Note:** transcribed from the flow's prose description, not from a step table

### 5.8 · Step P6 — [SCR-924] POD · Read-only confirm

- **Screen:** [SCR-924] POD · Read-only confirm
- **User sees:** Everything captured, read-only
- **User does:** Reviews, submits
- **System does:** DELIVERED → POD_CAPTURED; record fixed once captured (BR-512)
- **Goes to:** P7
- **If it fails:** Later addition must be a separately timestamped addendum
- **Note:** transcribed from the flow's prose description, not from a step table

### 5.8 · Step P7 — [SCR-924] POD · Pending sync

- **Screen:** [SCR-924] POD · Pending sync
- **User sees:** sync-pill--pending — "captured locally, will upload the moment you're back online"
- **User does:** Nothing
- **System does:** Invoice opens clean, or line held pending claim
- **Goes to:** Carrier §8 / Shipper §9
- **If it fails:** Sync conflict → [NEW SCR-928] human reconciliation queue
- **Note:** transcribed from the flow's prose description, not from a step table

### 5.8 · Rules for this stage

- not punished with extra friction, matching the brief
- Concealed-damage addendum (BR-504): reachable later from load history, always linked to the original POD, never overwriting it — [specified, not yet built], its own frame, same signature component, one field: "What was found, when."

## 5.9 Summary

### 5.9 · Rules for this stage

- 6-line summary. Mapped the driver's full journey from SMS invite through device bind, arrival identity match, pickup's dual-signature handover, in-transit passivity-by-design, to the built forced-choice POD and its pending-sync/conflict handling. `SCR-920` and `SCR-924` confirmed built and correct against BR-501/502/505/512. Added three new screens (`SCR-927`–`929`) F9 never specified for invite/device-bind, sync-conflict, and session-ended. Deliberately did not design a live HOS countdown — `DEC-700` is unresolved and a countdown would itself be the rejected Option C. Named one BRD gap (lumper capture scoped delivery-only) and one operational gap (revocation doesn't move a loaded truck)
- Counts: ~28 steps (S1–S18 plus onboarding S1–S6 and pickup S11–S14) · 10 frames referenced (7 existing `SCR-` IDs, 3 new) · 4 branch tables (§5.1–5.4, 20 rows total)
- Built vs. specified: `SCR-920` (Today) and `SCR-924` (POD capture, full 7-step sequence) are built and verified in `prototype.html`. `SCR-921/922/923/925/926` and all three `[NEW]` screens are specified only
- Three sharpest questions only Boss can answer: 1. `DEC-700` — HOS Option A (nothing shown) or Option B (bounded feasibility badge)? Assumed B's shape here but builds nothing live without the lock. 2. Session revocation when a driver leaves mid-trip kills the *app*, not the *truck* — freight is still physically on a road. Is there an operational handoff process, or does this stay a gap? 3. Lumper-fee capture is written into the BRD as delivery-side only (BR-516) — should pickup-side fees get the identical affordance, or is that intentionally out of scope?
- `CHALLENGE`: see §5.2 — BR-516 scopes lumper-fee capture to the delivery side only; recommend the identical flag+receipt affordance at pickup too, not left uncaptured there
- The single moment where a bad UI decision costs the most real money: the forced-choice screen in `SCR-924`. A clear-signed POD materially weakens a later cargo claim (BR-505) — any UI that makes "clean" the path of least resistance (a default, a faster tap-count, a friendlier colour) quietly biases drivers toward under-reporting real damage, and every under-reported load is a claim someone cannot win later. The built version already gets this right — no default, equal visual weight, equal tap-count — and that correctness must survive any future redesign untouched

# 6. Platform Ops / Admin flow — 27 steps

Design page 13-14. Source file `D5-flow-ops-admin.md`.

## 6.1 Preamble

### 6.1 · Branch point 1 — SCR / Screen

8 outcomes.

- **SCR-930**
    - Screen: Exception Work Queue
    - Status: Built — Default(open)/Empty/Contested, `prototype.html`
- **SCR-931**
    - Screen: Exception Detail & Resolution
    - Status: Spec only
- **[NEW] SCR-934**
    - Screen: Configuration Console
    - Status: Not in F9 — FR-1142/1145 need a governed-settings surface
- **[NEW] SCR-935**
    - Screen: Impersonation Console
    - Status: Not in F9 — F9 only names a banner (§11.5), no screen
- **SCR-940**
    - Screen: Carrier Vetting Queue
    - Status: Spec only
- **SCR-941**
    - Screen: Fraud Case Review
    - Status: Spec only
- **SCR-942**
    - Screen: Selection Record / Audit Viewer
    - Status: Spec only
- **SCR-943**
    - Screen: Enforcement Action
    - Status: Spec only

### 6.1 · Rules for this stage

- Queue composition, once. SCR-930 unions two sources, never conflated visually: Load-state exceptions (`CARRIER_NO_SHOW`, `TRANSIT_EXCEPTION`, `DELIVERY_REFUSED`, `PICKUP_REFUSED`, `SHIPPER_NOT_READY` — single-valued, §3.3) and `ExceptionCase` records (`FRAUD_REVIEW`, `CARGO_INTEGRITY`, `CARGO_CLAIM`, `DISPUTE_FREIGHT`/`MONEY`, `CARRIER_ENFORCEMENT_COLLISION` — many-per-load, `ENT-324`). A row's case-type badge is absent for the former, present for the latter

## 6.2 Exception Work Queue

*Stage as written in the spec: 1. Exception Work Queue (SCR-930).*

### 6.2 · Step S1 — [SCR-930]·Default

- **Screen:** `[SCR-930]·Default`
- **User sees:** Swimlanes by domain (FR-1102); money-at-risk / freight-in-motion / time-criticality as three separate signals, never one score (FR-1103); action attached per row
- **User does:** Scans, opens "Urgent" cross-domain view (FR-1104)
- **System does:** Queries `ExceptionCase.status=OPEN|IN_REVIEW` ∪ open Load-state exceptions
- **Goes to:** S2 or SCR-931
- **If it fails:** No `PERM-236` → `Permission denied`; no rows → `Empty` (built)

### 6.2 · Step S2 — same

- **Screen:** same
- **User sees:** Unclaimed row, Claim button
- **User does:** Clicks Claim
- **System does:** `PERM-236`, `granted_case` binds this case only
- **Goes to:** Row → "Claimed by you"
- **If it fails:** Race with another claimant → S3 (EC-1100)

### 6.2 · Step S3 — [SCR-930]·Contested (built)

- **Screen:** `[SCR-930]·Contested` (built)
- **User sees:** "Claimed by X," action disabled
- **User does:** Reads only — platform-wide read stays (FR-1108)
- **System does:** No write path for this actor
- **Goes to:** stays S1
- **If it fails:** Contest state is itself terminal for the loser

### 6.2 · Step S4 — [SCR-931]·Default

- **Screen:** `[SCR-931]·Default`
- **User sees:** Full context, prior actions, handoff note
- **User does:** Escalates (reason required, FR-1107) or works case
- **System does:** `case.status→IN_REVIEW`; escalation → `PLATFORM_SENIOR_REVIEWER`
- **Goes to:** S5
- **If it fails:** Missing reason → inline error

### 6.2 · Step S5 — [SCR-931]·Resolved

- **Screen:** `[SCR-931]·Resolved`
- **User sees:** Resolution type/actor/reason, linked downstream action (FR-1110)
- **User does:** Confirms
- **System does:** `status→RESOLVED|CLOSED_UNRESOLVED`, addendum-only
- **Goes to:** S1, row removed
- **If it fails:** Already resolved by another actor → `ERR-529`/`567`

### 6.2 · Branch point 1 — Condition / Destination

5 outcomes.

- **Unclaimed, claim succeeds**
    - Destination: S4, `IN_REVIEW`
    - Consequence: Off others' unclaimed filter, still platform-visible
- **Claimed near-simultaneously by two**
    - Destination: Contested
    - Consequence: First commit wins; loser sees who, can't duplicate
- **Fraud case = double-brokering/identity-theft, freight-in-motion**
    - Destination: Auto-escalate, senior tier
    - Consequence: No human gate — FR-1107
- **Claim nears 30/120/60-day mark**
    - Destination: Auto-escalate
    - Consequence: `[NEEDS INPUT]` window; statutory floor never configurable down
- **Manual escalation**
    - Destination: Reason required
    - Consequence: Logged, senior tier notified

### 6.2 · Rules for this stage

- Shift handoff: no staffing model exists (`DEP-900`) — FR-1108 keeps every open case, claimed or not, platform-wide visible; the handoff note is the only mechanism, not a roster. `FR-1106` auto- return threshold `[NEEDS INPUT]` — an abandoned claim ages visibly (EC-1101), never silently reassigns
- Branch — claim/contest/escalate

## 6.3 Working three case kinds

*Stage as written in the spec: 2. Working three case kinds (SCR-931).*

### 6.3 · Branch point 1 — Kind / State

3 outcomes.

- **Carrier no-show at dock**
    - State: `·No-show`
    - Actions available: Contact carrier, reassign via cascade/re-auction (FR-1124 — ops picks *path*, never hand-picks a winner outside ranked pool), log ground
    - Never available: Force-award off-pool
    - Traces: BR-301/304, `DEC-309`
- **Insurance lapse mid-trip**
    - State: `·Vetting-lapse-in-flight`
    - Actions available: Flag tuple, pin freight-in-motion (FR-1103/1115), require ID/doc re-check at drop, monitor
    - Never available: Auto-abort the physical trip — settled, BR-218/219, FR-1310
    - Traces: FR-1115
- **Delivery refused, freight on truck**
    - State: `·Delivery-refused`
    - Actions available: Log reason, route `RETURN_TO_ORIGIN`, open `DISPUTE_FREIGHT` if contested, coordinate RTO
    - Never available: Mark `DELIVERED` by ops fiat
    - Traces: §3.3, BR-813

### 6.3 · Rules for this stage

- CHALLENGE: `ENT-324.case_type`'s six values have no slot for two items F11's own prose opens: FR-1115's `vetting-lapse-in-flight` tag, and §7.8/EC-1205/1211's offline-sync reconciliation item (§3 below). Both "open a case, route to §13" in text but can't persist as typed `ExceptionCase` today. Recommend adding `VETTING_LAPSE`/`DATA_RECONCILIATION` before build proceeds past mock data

## 6.4 Offline-POD sync conflict

*Stage as written in the spec: 3. Offline-POD sync conflict (SCR-931, new state).*

### 6.4 · Step S1 — [SCR-931]·Sync conflict

- **Screen:** `[SCR-931]·Sync conflict`
- **User sees:** Competing captures side by side: device-local time, server-received time, each event's assumed precondition state vs. current canonical state
- **User does:** Opens item (auto-routed, never a generic exception)
- **System does:** `ERR-550`/`553` surfaces raw events, neither applied
- **Goes to:** S2

### 6.4 · Step S2 — same

- **Screen:** same
- **User sees:** Evidence per candidate (photo/signature/exception note), clock-skew flag if `ERR-552` present
- **User does:** Compares, picks authoritative capture or requests both preserved sequentially (addendum, never overwrite — FR-1129/BR-512)
- **System does:** Nothing auto-resolves
- **Goes to:** S3
- **If it fails:** Evidence gap (e.g. missing photo) → flagged, choice not forced

### 6.4 · Step S3 — Sync conflict·Resolved

- **Screen:** `·Sync conflict·Resolved`
- **User sees:** Chosen event applied; superseded event retained, linked
- **User does:** Confirms with named reason (mirrors FR-1123)
- **System does:** Canonical write proceeds; addendum shows both attempts
- **Goes to:** Load resumes lifecycle
- **If it fails:** State advanced again meanwhile → re-enters S1, not auto-retried

## 6.5 Support impersonation

*Stage as written in the spec: 4. Support impersonation ([NEW] SCR-935).*

### 6.5 · Step S1 — [SCR-935]·Initiate

- **Screen:** `[SCR-935]·Initiate`
- **User sees:** Target user, scope (whole-account read vs. one named load), reason field
- **User does:** Fills fields, fresh MFA (FR-148)
- **System does:** Validates scope vs `granted_case`; consent per FR-1133 (`[NEEDS INPUT]` implicit-ToS vs. explicit)
- **Goes to:** S2
- **If it fails:** Target under own open fraud case → blocked (EC-1104)

### 6.5 · Step S2 — Active session + persistent banner on every touched screen

- **Screen:** `·Active session` + persistent banner on every touched screen
- **User sees:** "Viewing as {user}, ticket {id}, expires {t}," read-only content
- **User does:** Browses read-only
- **System does:** Every render tags `actor_user_id`≠`real_actor_user_id`, audited (FR-149)
- **Goes to:** S3 or auto-expire
- **If it fails:** Screen involves an identity-bound action (accept award, sign POD, change payee/banking) → controls hard-disabled (FR-1135)

### 6.5 · Step S3 — Write-as confirm

- **Screen:** `·Write-as confirm`
- **User sees:** "Acting on behalf of user X, ticket Y" modal
- **User does:** Confirms mutating action
- **System does:** Separate audit entry; identity-bound actions still excluded unconditionally
- **Goes to:** Action executes, logged
- **If it fails:** Cancel/mismatch → no-op

### 6.5 · Step S4 — Expired

- **Screen:** `·Expired`
- **User sees:** "Session ended," no replay of live content (EC-1116)
- **User does:** Requests new session if needed
- **System does:** Server-side time-box, `[NEEDS INPUT]` duration
- **Goes to:** S1

### 6.5 · Branch point 1 — Scope / Read

2 outcomes.

- **Whole-account**
    - Read: ✓
    - Write: Only via S3, never identity-bound actions
- **One named load**
    - Read: ✓, scoped
    - Write: Same S3 gate, narrower `granted_case`

## 6.6 Configuration

*Stage as written in the spec: 5. Configuration ([NEW] SCR-934).*

### 6.6 · Step S1 — [SCR-934]·List

- **Screen:** `[SCR-934]·List`
- **User sees:** All 11 parameters + gate-policy tier, each with version/author/date
- **User does:** Selects a parameter
- **System does:** Read scoped `PLATFORM_CONFIG_ADMIN`/`PERM-264` only
- **Goes to:** S2
- **If it fails:** Wrong role → denied — `PLATFORM_CARRIER_VETTING` explicitly excluded from gate edits (FR-1145)

### 6.6 · Step S2 — Edit

- **Screen:** `·Edit`
- **User sees:** New value, effective-date, mandatory reason
- **User does:** Submits
- **System does:** New versioned row, attributed, dated (FR-1144); never overwrites prior
- **Goes to:** S3
- **If it fails:** Missing reason → blocked

### 6.6 · Step S3 — Applied

- **Screen:** `·Applied`
- **User sees:** "Applies to auctions not yet published" (or immediate if a runtime-behaviour parameter)
- **System does:** `AUCTION_OPEN` instances untouched (FR-1143); award record stores governing version (FR-650)
- **Goes to:** S1
- **If it fails:** Mid-`AUCTION_OPEN` edit for a value-locking parameter → queues for future auctions only (EC-1105), not rejected

## 6.7 Carrier vetting queue

*Stage as written in the spec: 6. Carrier vetting queue (SCR-940).*

### 6.7 · Step S1 — [SCR-940]·Default

- **Screen:** `[SCR-940]·Default`
- **User sees:** Candidates (new + re-verifying, tagged distinct — FR-1114), freight-in-motion pinned (FR-1115)
- **User does:** Opens candidate
- **System does:** Scoped `PLATFORM_CARRIER_VETTING`, `platform_wide`
- **Goes to:** S2
- **If it fails:** Empty → `Empty`

### 6.7 · Step S2 — Evidence

- **Screen:** `·Evidence`
- **User sees:** Per-tuple evidence + last-verified time for all six elements; COI shown insurer-confirmed vs. carrier-uploaded, never equivalent (FR-1111); specific equipment/driver record, never carrier rollup (FR-1116)
- **User does:** Decides APPROVE/REJECT/HOLD-FOR-INFO/CONDITIONAL, reason always required
- **System does:** Writes decision; non-bidding until explicit APPROVE (BR-908)
- **Goes to:** S3
- **If it fails:** No reason → blocked

### 6.7 · Step S3a — Approve

- **Screen:** `·Approve`
- **User sees:** Confirm
- **User does:** Approves
- **System does:** `PERM-240`, approver≠editor (maker-checker)
- **Goes to:** Resolved
- **If it fails:** Self-approve → denied

### 6.7 · Step S3b — Override(FAIL→approve)

- **Screen:** `·Override(FAIL→approve)`
- **User sees:** Automated-FAIL banner, mandatory per-element justification, "needs second approver"
- **User does:** Submits
- **System does:** `PERM-260` writes addendum type `OVERRIDDEN`, every failed element cited individually (FR-1351) — never blanket
- **Goes to:** S4
- **If it fails:** Missing per-element justification → blocked (FR-1352)

### 6.7 · Step S4 — Second approve

- **Screen:** `·Second approve`
- **User sees:** Full override context, first reviewer named
- **User does:** Distinct `PLATFORM_SENIOR_REVIEWER` approves/rejects
- **System does:** Bid-eligibility flips only on second approve
- **Goes to:** Resolved
- **If it fails:** No second approver on shift → stalls, no safe default (EC-1106)

### 6.7 · Branch point 1 — Outcome / Destination

4 outcomes.

- **APPROVE (gate passed)**
    - Destination: Bid-eligible immediately
    - Consequence: Single approver, maker≠checker
- **REJECT (even if all checks passed)**
    - Destination: Non-bidding
    - Consequence: Reviewer discretion permitted, BR-908
- **Override FAIL→APPROVE**
    - Destination: Held pending second approver
    - Consequence: Never single-actor; addendum evidence trail
- **HOLD-FOR-INFO**
    - Destination: Re-queued
    - Consequence: No bidding meanwhile

### 6.7 · Rules for this stage

- Branch — vetting decision

## 6.8 Fraud review

*Stage as written in the spec: 7. Fraud review (SCR-941).*

### 6.8 · Step S1 — [SCR-941]·Default

- **Screen:** `[SCR-941]·Default`
- **User sees:** Case from arrival mismatch (driver/tractor/MC≠awarded tuple, BR-221/224 — flagship signal) or anomaly/contact/remit-change (FR-1117), triggering signal typed
- **User does:** Opens case
- **System does:** Scoped `PLATFORM_FRAUD_REVIEWER`
- **Goes to:** S2

### 6.8 · Step S2 — Evidence

- **Screen:** `·Evidence`
- **User sees:** Signal+evidence, award/selection record, vetting history, cross-load pattern view, comms log (FR-1118)
- **User does:** Investigates
- **System does:** Read-only aggregation
- **Goes to:** S3
- **If it fails:** Cross-case pattern can't auto-classify — flagged for human (EC-1115)

### 6.8 · Step S3 — Classify

- **Screen:** `·Classify`
- **User sees:** Four outcomes: double-brokering / identity-theft / disclosed-and-revetted (closes, no case) / indeterminate-escalate
- **User does:** Selects
- **System does:** `fraud.classified`; disclosed-and-revetted closes but review stays on record (EC-1107)
- **Goes to:** S4 or resolved

### 6.8 · Step S4 — Containment (freight in motion)

- **Screen:** `·Containment (freight in motion)`
- **User sees:** No cancel affordance — absent. Available: withhold payment/settlement, flag `custody-under-investigation`, require ID re-check at drop, generate LE/insurer referral (FR-1120)
- **User does:** Applies containment
- **System does:** Suspension halts new bids/awards, doesn't strand the load (BR-818/FR-1121)
- **Goes to:** Monitors to resolution
- **If it fails:** Plainly stated: cannot recall a truck in transit — a real ceiling

### 6.8 · Branch point 1 — Path / Protects

2 outcomes.

- **Disclose pre-resolution**
    - Protects: Fair notice, due process, may surface a legitimate explanation early
    - Costs: Tips off real fraud mid-investigation, risks evidence/asset flight
- **Withhold pending resolution**
    - Protects: Containment integrity, referral packet's evidentiary value
    - Costs: Flagged carrier can't respond; due-process exposure if wrong

### 6.8 · Branch point 2 — Outcome / Destination

3 outcomes.

- **Cleared (disclosed-and-revetted)**
    - Destination: Closes
    - Consequence: Review stays on record
- **Contained, freight in motion**
    - Destination: Stays open, monitored
    - Consequence: No cancel path exists structurally
- **Escalated**
    - Destination: Senior tier
    - Consequence: Litigation hold if theft/injury/fatality/open claim (BR-819) — never deletable after

### 6.8 · Rules for this stage

- Disclosure question — mapped both ways, not picked (`[NEEDS INPUT]`, FR-1120):
- Branch — fraud outcome

## 6.9 Overrides

*Stage as written in the spec: 8. Overrides.*

### 6.9 · Branch point 1 — Override / Where

5 outcomes.

- **Force stuck transition**
    - Where: SCR-931
    - Gate: Named actor, reason, before/after, audited (FR-1123); blocked/warned if an open fraud case exists (EC-1114)
- **Re-award after decline/lapse/void**
    - Where: SCR-931
    - Gate: Same gate + ranked pool; ops picks cascade-vs-re-auction, never a specific carrier (FR-1124)
- **Waive charge / claim payout**
    - Where: SCR-931 / collections
    - Gate: Requester≠approver, second approver above `[NEEDS INPUT]` threshold
- **Reinstate suspended carrier**
    - Where: SCR-943
    - Gate: Second approver≠suspender (FR-1127); blocked while a fraud case is open (EC-1102)
- **Force-award to gate-failed carrier**
    - Where: Nowhere — no affordance exists, any tier
    - Gate: FR-1128: refused outright — the action is absent, not disabled

### 6.9 · Branch point 2 — Type / Destination

2 outcomes.

- **Overridable**
    - Destination: Executes, named actor+reason, audited
    - Consequence: Reversible only by a new logged event, never edited history
- **Never overridable**
    - Destination: No control renders
    - Consequence: Gate bypass, POD/selection-record edits, re-ordering a closed auction, self-approval — structurally absent

### 6.9 · Rules for this stage

- Branch — permitted/refused

## 6.10 Audit review

*Stage as written in the spec: 9. Audit review (SCR-942).*

### 6.10 · Step S1 — [SCR-942]·Search

- **Screen:** `[SCR-942]·Search`
- **User sees:** Search by load/carrier/date; entitled-party framing (49 CFR 371)
- **User does:** Searches
- **System does:** `PLATFORM_AUDITOR` (`platform_wide`, read-only, PERM-250/251) or ops via `granted_case`
- **Goes to:** S2
- **If it fails:** No match → `Empty`

### 6.10 · Step S2 — Record

- **Screen:** `·Record`
- **User sees:** Full 371.3 six-element package + selection record + custody events, from stored snapshot alone (FR-1200, no live re-query)
- **User does:** Views, exports
- **System does:** Read path independent of transactional write path (NFR-1229)
- **Goes to:** S3
- **If it fails:** Export target unreachable → retry, never a partial silent file

### 6.10 · Step S3 — Exported

- **Screen:** `·Exported`
- **User sees:** Confirmation, `trace_id`
- **System does:** Cross-org audit access itself audited, bounded to ops (NFR-1230)

### 6.10 · Rules for this stage

- Counts: 9 flows (30 steps across 9 tables) · 8 frames (6 F9 + 2 `[NEW]`) · 8 branch tables · 1 `CHALLENGE`. All screens are permission-aware (§4); ops access is bound to `granted_case` — the case being worked, not the whole platform — everywhere except `PLATFORM_AUDITOR`/`PLATFORM_ADMIN` (`platform_wide` by design, both structurally read-only or identity-only)
- Built vs. spec: SCR-930 alone is built (Default-open, Empty, static Contested). SCR-931, SCR-934[NEW], SCR-935[NEW], SCR-940, SCR-941, SCR-942, SCR-943 are specified, not built
- Three questions only Boss can answer: 1. Fraud disclosure (§7, FR-1120) — does the suspect carrier see the flag before resolution? Containment and fair notice pull opposite ways; no default exists. 2. `EC-1106` — second approver required but none on shift: spec says "stalls, no safe default." Is that acceptable at launch, or does Boss want a named fallback escalation despite the weaker segregation-of-duty? 3. This doc's `CHALLENGE` — extend `ENT-324.case_type` now, or leave `VETTING_LAPSE`/sync-conflict items un-typed and queue-unioned without a formal case record?
- Screen whose absence hurts day one most: SCR-931. SCR-930 lists work, but claim/escalate/resolve and the §3 sync adjudication have nowhere to execute — a queue showing what's broken with no tool to fix it, on freight moving 24/7 with no staffing model defined yet

# 7. Screen inventory

41 screens — 31 canonical plus 10 added during the design pass. 8 are built and verified in the working prototype; one more is built up to a fork that is still undecided. A screen with six states is six frames; the core state set every screen must answer for is Default, Loading, Empty, Partial data, Stale data, Permission denied, Error and Offline.

## 7.1 Shipper screens

### SCR-900 · Load Dashboard

- **State:** Built and verified
- **Detail:** Built
- **Specified in:** F9, D2

### SCR-901 · Post a Load

- **State:** Built and verified
- **Detail:** Built
- **Specified in:** F9, D2

### SCR-902 · Auction Watch

- **State:** Built and verified
- **Detail:** Built
- **Specified in:** F9, D2

### SCR-903 · Award & Accept-Flow Monitor

- **State:** Specified only
- **Detail:** Spec only — blocked on DEC-307 (§4)
- **Specified in:** F9, D2

### SCR-904 · Shipment Tracker

- **State:** Built and verified
- **Detail:** Built (shipment-detail)
- **Specified in:** F9, D2

### SCR-905 · Exception Inbox

- **State:** Specified only
- **Detail:** Spec only
- **Specified in:** F9, D2

### SCR-906 · Invoice Approval

- **State:** Specified only
- **Detail:** Spec only
- **Specified in:** F9, D2

### SCR-907 · Claim Intake

- **State:** Specified only
- **Detail:** Spec only
- **Specified in:** F9, D2

### SCR-908 · Standing & Cancellation History

- **State:** Specified only
- **Detail:** Spec only — unfulfillable, orphan BR-106
- **Specified in:** F9, D2, D6

### SCR-909 · Org Setup & Verification

- **State:** Specified only — new screen added in the design pass
- **Detail:** Spec only
- **Specified in:** D2 §1, assembler ID

## 7.2 Carrier screens

### SCR-910 · Load Board

- **State:** Built and verified
- **Detail:** Built
- **Specified in:** F9, D3

### SCR-911 · Bid & Comparison

- **State:** Partially built
- **Detail:** Built up to rival-visibility fork
- **Specified in:** F9, D3 — blocked, DEC-302/303 (§4)

### SCR-912 · Fleet Assignment

- **State:** Specified only
- **Detail:** Spec only
- **Specified in:** F9, D3

### SCR-913 · Active Loads

- **State:** Specified only
- **Detail:** Spec only
- **Specified in:** F9, D3

### SCR-914 · Breakdown / Exception Report

- **State:** Specified only
- **Detail:** Spec only
- **Specified in:** F9, D3

### SCR-915 · Driver & Equipment Roster

- **State:** Specified only
- **Detail:** Spec only
- **Specified in:** F9, D3

### SCR-916 · Settlement Status

- **State:** Specified only
- **Detail:** Spec only
- **Specified in:** F9, D3

### SCR-917 · Carrier Sign-up & Vetting Intake

- **State:** Specified only — new screen added in the design pass
- **Detail:** Spec only
- **Specified in:** D3 §1, assembler ID

### SCR-918 · Vetting Status

- **State:** Specified only — new screen added in the design pass
- **Detail:** Spec only
- **Specified in:** D3 §1, assembler ID

### SCR-919 · Award Notification & Accept

- **State:** Specified only — new screen added in the design pass
- **Detail:** Spec only — closes D6's gap 7
- **Specified in:** D3 §5, assembler ID

## 7.3 Driver screens

### SCR-920 · Today (home)

- **State:** Built and verified
- **Detail:** Built
- **Specified in:** F9, D4

### SCR-921 · Navigation Handoff

- **State:** Specified only
- **Detail:** Spec only — thinnest F9 spec
- **Specified in:** F9, D4

### SCR-922 · Arrival / Departure Capture

- **State:** Specified only
- **Detail:** Spec only
- **Specified in:** F9, D4

### SCR-923 · Document Capture

- **State:** Specified only
- **Detail:** Spec only
- **Specified in:** F9, D4

### SCR-924 · POD Capture

- **State:** Built and verified
- **Detail:** Built (full 7-step)
- **Specified in:** F9, D4

### SCR-925 · Report a Problem

- **State:** Specified only
- **Detail:** Spec only
- **Specified in:** F9, D4

### SCR-926 · Language & Support

- **State:** Specified only
- **Detail:** Spec only — thin
- **Specified in:** F9, D4

### SCR-927 · Invite Accept & Device Bind

- **State:** Specified only — new screen added in the design pass
- **Detail:** Spec only
- **Specified in:** [NEW], D4

### SCR-928 · Sync Held for Review

- **State:** Specified only — new screen added in the design pass
- **Detail:** Spec only
- **Specified in:** [NEW], D4

### SCR-929 · Session Ended

- **State:** Specified only — new screen added in the design pass
- **Detail:** Spec only
- **Specified in:** [NEW], D4

## 7.4 Ops screens

### SCR-930 · Exception Work Queue

- **State:** Built and verified
- **Detail:** Built (Default/Empty/Contested)
- **Specified in:** F9, D5

### SCR-931 · Exception Detail & Resolution

- **State:** Specified only
- **Detail:** Spec only
- **Specified in:** F9, D5

### SCR-932 · Claims Desk

- **State:** Specified only
- **Detail:** No design coverage at all
- **Specified in:** F9 — see DESIGN-GAPS.md row 2

### SCR-933 · Silence / No-Response Monitor

- **State:** Specified only
- **Detail:** No design coverage at all
- **Specified in:** F9 — see DESIGN-GAPS.md row 2

### SCR-934 · Configuration Console

- **State:** Specified only — new screen added in the design pass
- **Detail:** Spec only
- **Specified in:** [NEW], D5

### SCR-935 · Impersonation Console

- **State:** Specified only — new screen added in the design pass
- **Detail:** Spec only
- **Specified in:** [NEW], D5

## 7.5 Admin screens

### SCR-940 · Carrier Vetting Queue

- **State:** Specified only
- **Detail:** Spec only — unreachable in built shell
- **Specified in:** F9, D5

### SCR-941 · Fraud Case Review

- **State:** Specified only
- **Detail:** Spec only — unreachable in built shell
- **Specified in:** F9, D5

### SCR-942 · Selection Record / Audit Viewer

- **State:** Specified only
- **Detail:** Spec only — unreachable in built shell
- **Specified in:** F9, D5

### SCR-943 · Enforcement Action

- **State:** Specified only
- **Detail:** Spec only — unreachable in built shell
- **Specified in:** F9, D5

## 7.6 No page owns this screens

### SCR-950 · Consignee Delivery Link

- **State:** Specified only — new screen added in the design pass
- **Detail:** Recommended, not yet specified as frames
- **Specified in:** D6 §3

# 8. Known gaps — what is missing

19 findings from the design audit, ranked by what happens if the product ships as-is. None of these were resolved during the design pass; they are stated so they cannot be rediscovered late.

## 8.1 AWARD_LAPSED / AWARD_VOIDED_INELIGIBLE has no ops resolution home

- **What is missing:** These two award outcomes are not among `ENT-324.case_type`'s six values, so `SCR-930`'s Exception Work Queue never ingests them (H2/H6 in the cross-flow map). Ops is paged (`EVT-1008`/`1009`) but has no screen, queue row, or case record to work against
- **Found by:** `D6` (H2, H6, §6 item 3); cross-referenced against `D5`'s independent `CHALLENGE` that `ENT-324` structurally excludes it
- **Consequence if shipped as-is:** F10 names a missed `award.confirmed` the single most expensive failure mode in the whole system — an uncollected load. The operational recovery for that exact failure currently has no tool. This is not a missing nice-to-have; it is the costliest gap in the product with the least coverage
- **What closing it requires:** Extend `ENT-324.case_type` (ties directly to row 6) and add a resolution frame/state — either a new `SCR-931` case kind alongside no-show / vetting-lapse / delivery-refused, or a dedicated queue lane on `SCR-930`. Needs a product decision on which

## 8.2 SCR-932 (Claims Desk) and SCR-933 (Silence/No-Response Monitor) have zero…

- **What is missing:** Both are F9-specified Ops screens (§1.4) that `D6`'s own frame index (§5) attributes to "13 / D5" — but `D5`'s delivered file never mentions either `SCR-` ID once. No anatomy, no states, no step table, no branch table exists for either screen anywhere in D1-D6
- **Found by:** Assembler (cross-check between D6's frame index and D5's actual content — neither D5 nor D6 flagged the omission itself)
- **Consequence if shipped as-is:** Claims Desk governs the Carmack 30/120/60-day statutory clock (`BR-807`/`808`) — a real legal deadline with financial consequence if missed. Silence/No-Response Monitor is the operational catch for `BR-401`/`409`'s missed-status-interval detection — the mechanism `D2`'s own shipper flow (`SCR-904` Stale state) depends on ops actually working. Two screens carrying legal-clock and detection responsibility are going to engineering with no design review at all — exactly the class of miss this whole audit exists to catch
- **What closing it requires:** A follow-up design pass — re-scope `D5` or dispatch a focused agent — specifically for `SCR-932` and `SCR-933` before either reaches build

## 8.3 The Consignee has no SCR- ID anywhere in F9's 31-screen inventory

- **What is missing:** The party whose signature triggers `POD_CAPTURED → INVOICE_ISSUED` and effectively closes the shipment has no reviewed screen. Their entire surface is defined only at the API/entity layer: physical signature captured on the *driver's* device (`SCR-924`), a tokenised read link (`API-112`), and a tokenised action link (`API-113`) — none of it has been through a UX pass for expiry, wrong-load, already-used, or forwarded-to-the-wrong-person states
- **Found by:** `D6` (§3, §6 item 1)
- **Consequence if shipped as-is:** The highest-stakes actor outside the four core personas is being built straight from an API contract. Failure modes are real and already named in the FRD (opened after expiry → generic 401, no consignee-specific error code; forwarded to the wrong person → accepted risk, not a bug; used twice → rejected correctly) but none has been through a screen-state design pass — they will be built ad hoc by whoever implements the API contract literally
- **What closing it requires:** `D6`'s recommended `[NEW] SCR-950` (Default/Expired/Used/Wrong-load) — but see the structural note below: no page in the spine's page tree currently owns a Consignee flow at all. That is a level-up gap from the screen gap itself

## 8.4 PARTIAL_DELIVERY has no line-level split-POD UI

- **What is missing:** `BR-507` requires line-level split capture when some freight delivers and the remainder is routed elsewhere. `SCR-924`'s actual F9 spec (§3) describes only the binary "Delivered CLEAR" vs. "Delivered WITH EXCEPTION" forced choice — no split-line frame exists. `D2`'s shipper-side flow (S37) describes the *outcome* of a partial delivery after the fact but that is not a capture UI
- **Found by:** `D6` (§6, lifecycle-state audit), cross-referenced against `BR-507` directly
- **Consequence if shipped as-is:** `SCR-924` is the screen that legally fixes the delivery record (`BR-512` — fixed once captured, any later addition is a separately timestamped addendum). A genuine, common custody outcome has no matching capture path on that screen as specified — a driver facing a real partial delivery has no honest way to record it in the current design, only a binary choice that doesn't fit the situation
- **What closing it requires:** A new `SCR-924` sub-state/frame for line-level split capture (per-line clear/exception/quantity), matched to `BR-507`, preserving the existing "no default, equal tap-count" discipline `D4` calls the product's single most consequential correctness property

## 8.5 SOURCE CONFLICT — BR-144 contradicts the FRD's own state model on post-pickup…

- **What is missing:** `BR-144` (BRD) says cancellation is unavailable once `PICKED_UP`. The FRD's own §3.3 state adjacency permits `IN_TRANSIT → CANCELLED_BY_SHIPPER(charged)`, and `EC-509` explicitly reads *"shipper cancels post-pickup, pre-delivery: allowed, with a financial consequence"* — contrasted against `ERR-516`, which only fires at/after `POD_CAPTURED`. Two source documents disagree on where the cutoff actually is
- **Found by:** `D2` (§6, filed as `CHALLENGE`, explicitly not decided by the design agent)
- **Consequence if shipped as-is:** Whichever reading ships, the other governing document is directly contradicted. A shipper could be told cancellation is categorically impossible mid-transit by one spec path, and be charged a mid-transit cancellation fee for the identical action under another. If this reaches production un-reconciled, it is a real billing/legal exposure, not a UI inconsistency. This is a business decision, not a design call — `D2` correctly followed the FRD reading for its own flow (S29) and flagged rather than resolved it
- **What closing it requires:** Boss (or whoever owns BRD/FRD reconciliation) picks the actual cutoff and the losing document gets corrected. Design cannot resolve a contradiction between its two source-of-truth documents

## 8.6 ENT-324.case_type has no slot for VETTING_LAPSE or DATA_RECONCILIATION

- **What is missing:** `FR-1115`'s vetting-lapse-in-flight tag and §7.8/`EC-1205`/`1211`'s offline-POD-sync-reconciliation item both instruct "open a case, route to ops" in FRD prose, but `ENT-324`'s six case-type values (`FRAUD_REVIEW`, `CARGO_INTEGRITY`, `CARGO_CLAIM`, `DISPUTE_FREIGHT`, `DISPUTE_MONEY`, `CARRIER_ENFORCEMENT_COLLISION` — verified directly against `FRD-v1.md` line 234) do not include either
- **Found by:** `D5` (`CHALLENGE`, §2) — accepted by the manager
- **Consequence if shipped as-is:** `SCR-931`'s own "Vetting-lapse-in-flight" state (§2) and "Sync conflict" state (§3) are designed against a data-model enum value that does not exist. Two real ops workflows — an insurance lapse discovered while freight is physically in motion, and a POD sync conflict that decides who gets paid — have UI designed for them but no way to persist as a typed case today
- **What closing it requires:** Add `VETTING_LAPSE` and `DATA_RECONCILIATION` to `ENT-324.case_type` before `SCR-931` leaves spec. Small schema change, blocking dependency for a screen already designed around it

## 8.7 Carrier award accept/decline (PERM-217) had no screen claiming it — RECONCILED

- **What is missing:** `D6` filed a `CHALLENGE` against `D3`/F9: `SCR-911`'s "outcome" state is documented as read-only narrative, but the accept/decline action has to live somewhere and no F9 screen claims it. Independently, in the same design pass, `D3` had already added three `[NEW]` frames for exactly this (§5 — Award Notification & Accept, assembled as `SCR-919`)
- **Found by:** `D6` (challenge) + `D3` (independent fix, same round)
- **Consequence if shipped as-is:** If left unreconciled, this would have shipped as a real screen gap on the single action F10 names as gating the system's costliest failure mode (row 1). It does not ship unreconciled — D3's answer satisfies D6's own second recommended option ("or specify a `[NEW]` screen"). The only residual risk is implementation duplicating the control across `SCR-911`'s outcome state *and* `SCR-919`
- **What closing it requires:** Confirm with `frontend-engineer-agent`: `SCR-911`'s outcome state stays read-only narrative; the accept/decline control lives solely on `SCR-919`. No further design work needed — this is now a wiring instruction, not an open gap

## 8.8 Admin/Fraud (SCR-940-943) has no entry point in the built persona switcher

- **What is missing:** `prototype.html`'s shell implements four persona buttons — Shipper, Carrier, Ops, Driver. Admin/Fraud is a fifth flow page (spine page 14) with zero of its four screens reachable from the running build, regardless of how complete their specs are
- **Found by:** `D6` (§4, §6 item 6)
- **Consequence if shipped as-is:** The entire vetting/fraud/audit/enforcement surface — the layer carrying maker-checker overrides and the `Montgomery`-driven immutable selection record that `DEC-LOCK-001` made load-bearing for the whole product — is unreachable today. This is a wiring gap, not a spec gap, but it fully blocks verification of anything D5 designs for pages 14
- **What closing it requires:** A fifth persona-switch entry (or a role-gated sub-nav under an existing persona). `frontend-engineer-agent` task, not a design task — flagged here so it isn't lost between design and build

## 8.9 No Cancel Load confirmation frame exists at any stage

- **What is missing:** `PERM-203`/`204` define who may cancel and when; no `SCR-` renders the cancel action or its confirmation state. `D2` §6 wrote step-level cancel-modal *copy* for four distinct stages (pre-award / post-award pre-dispatch / post-dispatch pre-pickup / mid-transit) but none of it is a reviewed frame with its own states
- **Found by:** `D6` (§6 item 4)
- **Consequence if shipped as-is:** Cancellation is one of the highest-liability action families in the product — it produces TONU claims, RTO charges, and (per row 5) sits directly on top of an unresolved source conflict. It currently exists only as prose inside a flow table, not as a component-level frame anyone can implement consistently across the four stages
- **What closing it requires:** Promote `D2` §6's four cancel-modal variants to a named frame set (attach to `SCR-904`/`900`), each carrying its own state per spine §3. Cannot fully close until row 5 (the BR-144/FRD conflict) is also resolved, since the mid-transit variant's copy depends on the answer

## 8.10 RETURN_TO_ORIGIN has no tracking screen for any persona

- **What is missing:** RTO exists as a `Custody Event` type (`ENT-315`) but no `SCR-` shows RTO progress. Three separate flows route freight there — `D2` S29/S38 (shipper cancellation, delivery refusal), `D4` §5.3 (driver, full refusal), `D5` §2 (ops, delivery-refused case kind) — and all three reference "RTO tracking" as a destination that does not structurally exist as a frame
- **Found by:** `D6` (§6 item, lifecycle-state audit)
- **Consequence if shipped as-is:** Freight physically moving back to origin, accruing real detention/RTO charges, has no dedicated view for shipper, carrier, or ops to watch it happen — three independently-designed flows all point at the same missing screen
- **What closing it requires:** A shared RTO progress frame, most naturally a `SCR-904`/`913` sub-state, that all three personas' existing flow references can point to consistently instead of a named-but-nonexistent destination

## 8.11 CANCELLED_BY_SHIPPER has no confirmation frame as its own named state

- **What is missing:** Overlaps row 9's remedy but named specifically by `D6`'s lifecycle-state audit as a state with no screen rendering it distinctly
- **Found by:** `D6` (§6, lifecycle-state audit)
- **Consequence if shipped as-is:** Same consequence family as row 9 — a permitted, BR-cited action with no reviewed confirmation UI. Listed separately because it is one of the six explicitly-audited lifecycle states, not because the remedy differs
- **What closing it requires:** Same remedy as row 9 — the mid-transit cancel-modal variant *is* this state's confirmation frame once built

## 8.12 CARRIER_NO_SHOW has no dedicated named state at the ops/shipper-facing layer

- **What is missing:** Folds into a generic exception banner rather than a distinct, colour+icon+text-labelled state per `D1`'s status discipline. `D5`'s Exception Detail (`SCR-931`) does give it a named "No-show" case kind (§2), but that is the ops working-surface, not a shipper- or dashboard-facing named state
- **Found by:** `D6` (§6, lifecycle-state audit)
- **Consequence if shipped as-is:** Weakens the "status is always colour + icon + text, never one generic look" rule `D1` sets as non-negotiable — three named, BR-cited failure states (this row + 13 + 14) currently share one undifferentiated banner treatment on `SCR-900`/`904`/`930`
- **What closing it requires:** Confirm `SCR-931`'s "No-show" state (already designed) is sufficient at the ops layer; add an equivalent named state to shipper- and queue-facing screens rather than a shared generic banner

## 8.13 SHIPPER_NOT_READY has no dedicated named state at the ops/carrier-facing layer

- **What is missing:** Same pattern as row 12 — `D4` §5.2 gives it a driver-side branch ("Not ready," `SHIPPER_NOT_READY` → TONU flag) but no distinct named state exists on the screens ops or the carrier actually work from
- **Found by:** `D6` (§6, lifecycle-state audit)
- **Consequence if shipped as-is:** Same consequence family as row 12 — this state carries a real financial consequence (TONU/detention against the shipper, `BR-143`) and currently reads as generic on the screens where a dispatcher or ops reviewer would need to distinguish it at a glance
- **What closing it requires:** Same remedy pattern as row 12

## 8.14 PICKUP_REFUSED has no dedicated named state at the ops/shipper-facing layer

- **What is missing:** Same pattern again — `D4` §5.2 names it clearly at the driver layer (`SCR-922 · Refused`, reason `EQUIPMENT_TYPE_MISMATCH`/`UNSAFE_LOAD`) but it has no equivalent named state upstream
- **Found by:** `D6` (§6, lifecycle-state audit)
- **Consequence if shipped as-is:** Same consequence family as rows 12-13
- **What closing it requires:** Same remedy pattern as row 12

## 8.15 Lumper-fee capture is delivery-side only; no pickup-side capture affordance

- **What is missing:** `BR-516` scopes the lumper-fee flag+receipt-photo affordance to delivery (`SCR-924`) only. The identical accessorial event happens at pickup docks, and `SCR-923` (pickup Document Capture) has no equivalent field
- **Found by:** `D4` (`CHALLENGE`, §5.2) — accepted
- **Consequence if shipped as-is:** Legitimate pickup-side lumper fees go uncaptured at the point of occurrence, creating an under-collection or after-the-fact dispute risk at settlement (`SCR-916`) with no photo evidence trail to support the claim
- **What closing it requires:** Add the identical flag+receipt-photo affordance to `SCR-923` that already exists on `SCR-924`, scoped by `BR-516`'s pattern

## 8.16 SCR-908 (Standing & Cancellation History) is structurally unfulfillable

- **What is missing:** Depends on an upstream feed (`BR-106`) that is an orphan requirement — it doesn't exist elsewhere in the BRD/FRD. Already correctly identified and handled: the screen renders "not yet available," never fabricates a value (`EC-907`, resolved as a rendering rule)
- **Found by:** F9 itself (`EC-907`) — reconfirmed by `D2` and `D6`
- **Consequence if shipped as-is:** Low near-term risk precisely because the honest-rendering rule is already locked. The screen simply ships permanently empty (a correct, labelled empty state) until `BR-106` is ever built upstream
- **What closing it requires:** No design action needed. A product/data decision on whether `BR-106`'s upstream feed is ever built — outside this register's scope

## 8.17 ExceptionCase.RESOLVED confirmation trigger for…

- **What is missing:** `EVT-1049` is new at the assembly layer; `SCR-931`'s generic "Resolve" action (S5) is the *presumed* trigger for closing these three case kinds, but this was never checked against F9's original prose. `D5` §2 already shows three genuinely different action sets per case kind (no-show / vetting-lapse / delivery-refused) — the same rigor has not yet been applied to the resolve/close action specifically
- **Found by:** `D6` (§6, coverage audit)
- **Consequence if shipped as-is:** Low probability but real: if fraud-case resolution needs senior-tier sign-off (as `D5` §7's own containment/classify flow implies) while a single generic "Resolve" button exists on `SCR-931`, a fraud closure could be under-gated relative to what `D5`'s own fraud-review flow requires
- **What closing it requires:** Confirm `SCR-931`'s Resolve action forks by `case_type` with the same distinctness `D5` §2 already applies to the three other case kinds, specifically checking the fraud-closure gate against `D5` §7's classify/contain flow

## 8.18 banner--attention CSS modifier was used in markup but never defined — CLOSED

- **What is missing:** The auction-extended banner (`awExtendedBanner`) stacked `.banner--attention` with `.banner--stale`; because `--attention` had no CSS definition, it silently fell through to `--stale`'s styling. Separately, the thin-market banner had no styling at all
- **Found by:** `D1` (`CHALLENGE`)
- **Consequence if shipped as-is:** Fixed by the manager in `prototype.html`. Recorded here so it is not rediscovered — the auction-extended banner had been silently inheriting stale styling, and the thin-market banner had no styling at all, before the fix
- **What closing it requires:** Closed. No further action

## 8.19 [hidden] attribute was losing to component display rules — CLOSED

- **What is missing:** Component rules that set an explicit `display` value beat the UA stylesheet's `[hidden]{display:none}`, so stale banners and empty states stayed visibly rendered across every preview state in `prototype.html`
- **Found by:** Manager (assembler), during this assembly pass
- **Consequence if shipped as-is:** Fixed — a global `[hidden]{display:none !important}` rule corrected 14 affected elements. Recorded here so it is not rediscovered
- **What closing it requires:** Closed. No further action

# 9. Open decisions

Three forks are still open. Each is stated with its options and the consequence of each — none is decided here, because each is a business call rather than a design one.

## 9.1 DEC-302/303 — Rival-bid visibility on SCR-911

- Three agents converged independently on this being unresolved and consequential: F6 found "sealed +
- standing-best-flag" a false middle ground; F2 proved it leaks rival prices by construction —
- repeated decrements binary-search the true price even with amounts hidden; F9 shipped `SCR-911` on the
- conservative default specifically to avoid a `BR-717` violation in production
- | Option | Adds | Consequence |
- |---|---|---|
- | (a) None — built default | Own bid + countdown + eligible-count only | Cleanest, least informative; weak re-bid signal |
- | (b) Rank-only | "#2 of 5 eligible" badge, no amount | At small decrements, rank alone leaks approximate price (`EC-908`) |
- | (c) Leading-price band | Rounded range, never exact | Named leak vector as decrements shrink (F2's finding) |
- Consequence of not deciding: `SCR-911` is feature-complete as a swappable component on all three
- shapes but cannot ship past (a) until `DEC-302`/`303` locks — shipping past it without a decision risks
- a `BR-717` violation in production, not a UI bug

## 9.2 DEC-307 / BR-155 / EC-325 — May the shipper decline the lowest qualified bidder?

- Asked independently in three separate documents and answered in none of them
- | Branch | `SCR-903` shape | Consequence |
- |---|---|---|
- | A — No decline right (`BR-304`, mechanical) | Pure accept/monitor screen | Simpler; matches "price decides, no human discretion" (`DEC-LOCK-001`) |
- | B — Decline right, structured reason required | Adds a reason-code picker tied to on-file carrier data, feeding the immutable selection record (`ENT-312`) | Materially different screen — not a variant of A, cannot be "built either way later" without rework |
- Consequence of not deciding: `D2` flags this as the flow's single most-abandonment-prone failure
- state has no bearing here, but `SCR-903` itself cannot leave spec — the two branches are structurally
- different screens, and D2's own `CHALLENGE` says so explicitly

## 9.3 DEC-700 — HOS: planning signal vs. system of record

- | Option | Shape | Consequence |
- |---|---|---|
- | A | No hours UI anywhere | Simplest; no feasibility signal to driver or dispatcher |
- | B — assumed by `D4`/`D3` for spec purposes only | Bounded `FEASIBLE`/`INFEASIBLE` badge, never a ticking clock (`EC-912`'s "not evaluated" honest default) | `SCR-920`/`SCR-915`/`SCR-912` designed against this shape; not wired, nothing renders without the lock |
- | C | Full RODS dashboard | Reverses an already-locked data-minimisation constraint (§14/F12) — F7 and the assembler both recommend against this |
- Consequence of not deciding: `SCR-920` and `SCR-915` cannot finalize; if Boss locks Option A, the
- badge design in `D4`/`D3` is deleted, not hidden — it was never meant to survive that outcome

# 10. Cross-cutting rules

## 10.1 Offline is the default assumption, not an edge case

- Every driver capture — arrival, documents, problem reports, proof of delivery — is written locally first and synced on reconnect
- A captured signature is never blocked by connectivity
- Pending uploads show the same "captured locally, will upload when you are back online" pill everywhere
- A sync conflict is never resolved on the phone and never shown to the driver as their problem — it becomes a human reconciliation item for ops

## 10.2 Permission decides visibility, not just access

- A carrier who is not eligible for a load does not see a locked load — they see nothing at all
- Out-of-scope links return not-found rather than forbidden, so nobody can enumerate what exists
- Within a shipper org, a load poster sees their own site; only the org admin sees org-wide and can cancel after award

## 10.3 Every screen answers for eight states

- Default, Loading, Empty, Partial data, Stale data, Permission denied, Error, Offline
- Plus Contested, where two people can act on the same record at once
- A screen specified only in its default state is not specified

## 10.4 Status is never colour alone

- Every status is colour plus icon plus text, so it survives colour-blindness and greyscale printing
- The status palette is colour-blind-safe; dark mode is the primary theme
- Numerics are tabular so columns of money and weight line up
- Focus rings are at least 2px and meet 3:1 contrast; the whole product targets WCAG 2.2 AA

## 10.5 The rules that carry legal weight

- The shipper's load declaration is snapshotted immutably at publish — bids are priced against that snapshot
- The eligibility decision, including every reason a carrier was excluded, is retained as a selection record
- Proof of delivery is fixed once captured; anything found later is a separately timestamped addendum, never an edit
- Pickup requires both the driver's and the shipper representative's acknowledgement before the load can move

# 11. How to read the reference codes

- **SCR-nnn** — a screen (frame) in the design — SCR-901 is Post a Load
- **S1, S2, S3a** — a numbered step inside one persona flow
- **BR-nnn** — a business rule from the requirements document
- **FR-nnn** — a functional requirement from the functional spec
- **ERR-nnn** — a named error the user can actually hit
- **EC-nnn** — an edge case the spec commits to handling
- **ENT-nnn** — a data entity — ENT-300 is an Organization
- **EVT-nnnn** — a system event that notifies somebody
- **PERM-nnn** — a row in the permission matrix
- **ROLE-nnn** — a user role — ROLE-201 is a shipper load poster
- **API-nnn** — an API contract, used where a participant has no screen
- **DEC-nnn** — a decision, either locked or still open
- **F1…F13** — the functional requirement documents the design was built from
- **TONU** — truck ordered, not used — a cancellation charge after a carrier has been dispatched
- **OS&D** — over, short and damaged — the exception notation on a delivery
- **HOS** — hours of service — the federal limit on how long a driver may legally drive
- **POD** — proof of delivery

---

Sources: `design/D2-flow-shipper.md`, `design/D3-flow-carrier.md`, `design/D4-flow-driver.md`, `design/D5-flow-ops-admin.md`, `design/D6-cross-flow-map.md`, `DESIGN-STRUCTURE.md`, `DESIGN-GAPS.md`. 138 steps, 24 branch points, 41 screens, 19 gaps, 3 open decisions.
