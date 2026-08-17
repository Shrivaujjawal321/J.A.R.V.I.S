# D2 — Shipper Flow (Figma page 10 · Flow — Shipper)

`SCR-` IDs cite `frd-F9-dashboards-screens.md` §1.1. Every screen inherits F9's core state set
(Default/Loading/Empty/Partial/Stale/Permission-denied/Error/Offline, FR-900) even where a step below
names only the state that matters. `[BUILT]` = verified in `prototype.html` (SCR-900/901/902/904).
Two new frames: F9's inventory starts post-auth; org creation/first invite (F1 FR-100/101/104/106)
has no screen anywhere in F9 — `[NEW] Org Setup & Verification` fills that gap only.

---

## 1. Onboarding and first load (F1 §5.2/5.3)

| Step | Frame | User sees | User does | System does | Goes to | If it fails |
|---|---|---|---|---|---|---|
| S1 | `[NEW] Org Setup · Details` | Org-type (SHIPPER), legal name, EIN, admin credentials | Submits | `ENT-300 Organization(SHIPPER)` + `ENT-301 User` as `SHIPPER_ORG_ADMIN` (FR-100) | S2 | `ERR-500/501` field errors; dedupe check `[NEEDS INPUT]` |
| S2 | `[NEW] Org Setup · Verification pending` | "Verifying" — IAL1 + domain-verified email (FR-104) | Waits; can already log in | `PENDING_VERIFICATION`; login allowed, publish is not (FR-103) | S3 on pass | Fail → `[NEW] Verification failed`, reason shown, resubmit |
| S3 | `[NEW] Org Setup · Payment standing` | Standing/credit check status (BR-104/105) | Submits reference `[NEEDS INPUT: check standard]` | Dated standing record on a re-check cycle | S4 | Below threshold → org exists but publish-blocked, reason shown (BR-107) |
| S4 | `[NEW] Org Setup · Invite team` | Invite by email/phone, role picker (ROLE-201/202/203/204) | Sends invite(s), or skips (owner-op, FR-102) | Single-use, expiring, role-tagged invite (FR-106) | SCR-900 | Bounce/expiry → resend on same frame |
| S5 | SCR-900 · Loads dashboard · Empty `[BUILT]` | "No loads yet — publish one" | Clicks Post a load | — | SCR-901 Step 1 | n/a — valid first-run state |
| S6 | SCR-900 · Loads dashboard · Default `[BUILT]` | Exceptions ranked above on-track loads | Browses, opens a load | Reads `own_org`/`own_site` scope (PERM-206) | Relevant screen per row status | `ERR-531` on stale/out-of-scope link — not-found, never forbidden |

**Permission.** `SHIPPER_LOAD_POSTER` (ROLE-201) sees/publishes `own_site` only; only
`SHIPPER_ORG_ADMIN` (ROLE-200) sees org-wide and cancels post-award (PERM-201–204).

---

## 2. Post a load — the declaration (BR-110–127, SCR-901 `[BUILT]`)

Three fields carry re-trade risk if under-declared, and the built UI warns inline on each:

| Field | Risk | Warning (built) |
|---|---|---|
| Gross weight | #1 re-trade cause — carrier re-weighs, mismatch, re-prices/refuses (BR-120) | Inline on the field |
| Hazmat flag | Narrows pool; flagging after bids exist forces re-listing | Inline on checkbox |
| Dock access / load type | Wrong dock type at arrival misses the appointment | Inline hint |

| Step | Frame | User sees | User does | System does | Goes to | If it fails |
|---|---|---|---|---|---|---|
| S7 | SCR-901 · Step 1 Lane & schedule `[BUILT]` | Addresses, appointment windows, tight-window hint | Fills, clicks Next | Autosaves (BR-103/125) | Step 2 | `ERR-500` named field; `ERR-504` if drop precedes pickup |
| S8 | SCR-901 · Step 2 Equipment & cargo `[BUILT]` | **Trailer type** (closed set incl. tanker, BR-111) — the shipper's only hard equipment choice; **Tractor requirement** is a soft preference only, since tractor and trailer are matched independently at bid time (`ENT-303`/`ENT-304`, no FK) | Picks trailer; reefer shows temp range; enters commodity/weight/dims; toggles hazmat + declared value | Validates `ERR-505` conflicts (e.g. temp range on dry van) | Step 3 | `ERR-503` out-of-range weight; `ERR-505` equipment conflict |
| S9 | SCR-901 · Step 3 Auction settings `[BUILT]` | Duration, optional ceiling, anti-snipe/early-close toggles | Sets parameters | Ceiling math validated | Step 4 | `ERR-523` ceiling ≤0 or ≤ min decrement |
| S10 | SCR-901 · Step 4 Review & publish `[BUILT]` | Full summary; commitment banner: bids priced against this declaration, dock discrepancy carries consequences (BR-121) | Acknowledges, clicks Publish | `ERR-507` completeness check, then `PUBLISHED`; declaration snapshot retained immutably (BR-122) | SCR-900 new row; `AUCTION_OPEN` per duration | `ERR-507` names the missing field, doesn't silently reject |
| S11 | SCR-901 · Partial (autosaved draft) `[BUILT]` | "Draft autosaved 12s ago" | Leaves, returns | Draft persists per user | Resumes at last step | Desk offline-draft persistence `[NEEDS INPUT]` |
| S12 | SCR-900 · Draft row `[BUILT]` | 0 bids, "Continue draft" | Clicks through | — | SCR-901, resumes | n/a |

**Permission.** `SHIPPER_LOAD_POSTER` publishes `own_site` (PERM-201); `SHIPPER_ORG_ADMIN` publishes
org-wide (PERM-202). A viewer (ROLE-202) reaching SCR-901 sees Permission-denied, not a blank form.

---

## 3. Auction open → watching bids (BR-301–318, SCR-902 `[BUILT]`)

Eligibility gate runs before ranking (`DEC-LOCK-001`, settled). SCR-902's **"N eligible · M excluded,"
each reason named** is primary content — the live front-end of the *Montgomery*-era selection record
(`ENT-312`), not a buried detail.

| Step | Frame | User sees | User does | System does | Goes to | If it fails |
|---|---|---|---|---|---|---|
| S13 | SCR-902 · Live `[BUILT]` | Best eligible bid (`aria-live="polite"`), countdown, "14 eligible · 6 excluded" strip | Expands exclusion reasons | Lists reasons — insurance lapse, org suspension, no reefer trailer, related-party (BR-316) | Stays live, updates | Feed stalls → **Stale**, timestamped |
| S14 | SCR-902 · Bid feed row `is-new` `[BUILT]` | New bid: price, timestamp, authority type (motor carrier vs broker, BR-313) | Watches | Broker bids carry a visible flag icon | — | Undisclosed broker bid never reaches feed — `ERR-519` upstream |
| S15 | SCR-902 · Extended `[BUILT]` | "Extended +5min — not a reset, earlier bids stand" | Watches | `AUCTION_OPEN → AUCTION_EXTENDED` | Live | n/a |
| S16 | SCR-902 · Thin market `[BUILT]` | "Only 1 bidder at close" — labelled, not competitive | Watches | EC-908 labelling; DEC-310 mechanism open, **not decided here** | Close per DEC-310 | — |
| S17 | SCR-902 · Closing — verifying `[BUILT]` | "Verifying eligibility — not yet awarded" | Watches | `AWARD_PENDING` re-runs winner's gate (BR-302, EC-902) | S18 pass | Fail → `AWARD_VOIDED_INELIGIBLE`, `ERR-514`, cascades DEC-309 |
| S18 | SCR-902 · Failed (3 reasons) `[BUILT]` | "No bids" / "No eligible carrier" / "All bids above your limit" | Amends & republishes, or escalates | `AUCTION_FAILED_NO_BIDS`/`_NO_ELIGIBLE_CARRIER`/`_ALL_ABOVE_LIMIT` | Shipper decides next | — this *is* the failure frame |

**Branch — eligibility.**

| Condition | Destination | Consequence |
|---|---|---|
| Carrier passes gate | Ranked, priced in feed | — |
| Carrier fails gate | Never ranked (BR-301) | Named in exclusion list (selection record) |
| Winner fails re-verify at close | `AWARD_VOIDED_INELIGIBLE` | `ERR-514`, cascades DEC-309 or re-auctions |

**Branch — bid accepted / outbid** (shipper-visible only):

| Condition | Shipper sees | Consequence |
|---|---|---|
| New low bid arrives | Hero amount updates, feed flashes | Prior bidder's status changes on *their* screen, not shown here (BR-314) |
| Bid withdrawn pre-close | Bid count decrements | Recorded against bidder (BR-308), not named to shipper |
| Auction closes | Best bid freezes into `AWARD_PENDING` | S17 |

---

## 4. Award — the unresolved fork (BR-155, DEC-307, EC-325 — same question, build-blocking)

Both branches mapped; neither picked.

| Step | Frame | User sees | User does | System does | Goes to | If it fails |
|---|---|---|---|---|---|---|
| S19 | SCR-903 · Verifying | "Re-verifying," mirrors S17 (EC-902) | Waits | Gate re-run on winner | S20a/b | `AWARD_VOIDED_INELIGIBLE` → S18-style failure |
| S20a **[Branch A — no decline right, BR-304 mechanical]** | SCR-903 · Awarded (informational) | Winning carrier, price, authority type | Views selection-record excerpt (BR-303) | `AWARDED` → carrier's own accept/decline/lapse | S21 | — |
| S20b **[Branch B — decline right, if BR-155/DEC-307 lock this way]** | SCR-903 · Award pending shipper review `[NEW, contingent]` | Winning bid + reason-code picker tied to on-file carrier data (BR-156, never free text) | Accepts, or declines with required reason code | Accept → as A; Decline → logged, actor + reason (BR-306), cascades DEC-309 | S21 or cascade | Decline without valid code → blocked at form |
| S21 | SCR-903 · Award accepted | Rate confirmation generated (BR-600) | Views | `AWARD_ACCEPTED`, binding rate confirmation | SCR-904 pickup scheduling | — |
| S22 | SCR-903 · Award declined / lapsed | "Carrier declined" / "window expired" | Waits, or notified of cascade (EC-909 — Boss's call whether winner is told) | `AWARD_DECLINED`/`AWARD_LAPSED` → DEC-309 cascade or re-auction | S13 (re-auction) or S20a (cascade winner) | Pool exhausted → routes to S18 |

**Branch — award accepted / declined / lapsed.**

| Condition | Destination | Consequence |
|---|---|---|
| Carrier accepts in window | `AWARD_ACCEPTED` | Binding rate confirmation, pickup opens |
| Carrier declines | `AWARD_DECLINED` | DEC-309 cascade or re-auction — mechanism open |
| Window lapses | `AWARD_LAPSED` | Same DEC-309 fork |
| (B only) Shipper declines lowest qualified bid | Logged, reason-coded | Same DEC-309 fork — not a new one |

**CHALLENGE:** SCR-903 differs materially between branches — B needs a reason-code picker and review
gate A never renders. Cannot be "built either way later" without rework; DEC-307/BR-155/EC-325 should
lock before SCR-903 leaves spec.

---

## 5. Amendment while bids are live (BR-135/136)

Declaration snapshot is immutable once bids exist so bids stay comparable — a material change forces
**withdraw-and-republish**, never a live edit.

| Step | Frame | User sees | User does | System does | Goes to | If it fails |
|---|---|---|---|---|---|---|
| S23 | SCR-901 · Amend attempt (post-first-bid) | Material fields (weight beyond tolerance, equipment, commodity, hazmat, either address) read-only | Attempts to edit | Blocked at the field | S24 | `ERR-513 LOAD_AMENDMENT_BLOCKED_LIVE_AUCTION` |
| S24 | SCR-901 · Withdraw & republish (modal) | "Material change withdraws this auction; all current bids are lost." | Confirms, or cancels | Withdraws auction, voids bids; opens SCR-901 pre-filled for fresh publish | S7 (new cycle) | Cancel → returns to SCR-902 unchanged |
| S25 | SCR-901 · Amend (pre-bid) | Direct field edit, no warning | Edits freely | Allowed pre-first-bid (BR-135) | Re-publish | Same `ERR-500`-class validation as S7 |

Non-material amendment tolerance `[NEEDS INPUT: BR-136]` — no live-edit path is specified; flagged, not invented.

---

## 6. Cancellation at each stage (BR-140–145, TONU)

**CHALLENGE:** BR-144 says cancellation is "unavailable once `PICKED_UP`," but the FRD's own §3.3
adjacency lists `IN_TRANSIT → CANCELLED_BY_SHIPPER(charged)`, and `EC-509` reads *"shipper cancels
post-pickup, pre-delivery: allowed, with a financial consequence — contrast `ERR-516`,"* which only
fires at/after `POD_CAPTURED`. Two source docs disagree on the cutoff. This flow follows the FRD
reading (cancel allowed through `IN_TRANSIT`, blocked from `POD_CAPTURED` on) — a real conflict to
reconcile before build, not a design choice.

| Step | Frame | User sees | User does | System does | Goes to | If it fails |
|---|---|---|---|---|---|---|
| S26 | SCR-900/902 · Cancel (pre-award) | "Cancel this load" | Confirms | Removed from auction, no standing record (BR-140) | SCR-900, row removed | — |
| S27 | SCR-904 · Cancel modal · post-award pre-dispatch | "Awarded, not yet dispatched — standing event, no fee." | Confirms | Standing event logged, no TONU (BR-141) | SCR-900 | — |
| S28 | SCR-904 · Cancel modal · post-dispatch pre-pickup | "Truck already moving — this creates a TONU claim." | Confirms | TONU claim created, evidenced by dispatch fact (BR-142, standard `[NEEDS INPUT]`) | SCR-907 Claim Intake | Mandatory warning, not skippable |
| S29 | SCR-904 · Cancel modal · mid-transit `[per CHALLENGE]` | "In transit — charged cancellation, linehaul-to-point + return costs." | Confirms | `IN_TRANSIT → CANCELLED_BY_SHIPPER(charged) → RETURN_TO_ORIGIN` | SCR-904 RTO tracking | — |
| S30 | SCR-904 · Cancel unavailable · post-delivery | "Delivered — raise a claim or dispute instead." | Redirected | `ERR-516` | SCR-906/SCR-907 | n/a — correct terminal state |
| S31 | SCR-904 · `SHIPPER_NOT_READY` | Distinct from carrier no-show, flagged shipper-caused | Acknowledges | TONU + detention claim against shipper (BR-143) | SCR-907 | — |

**Permission.** Pre-award cancel: `SHIPPER_LOAD_POSTER` (own authored loads) or `SHIPPER_ORG_ADMIN`
org-wide (PERM-203/204). Post-award: `SHIPPER_ORG_ADMIN` only.

---

## 7. Tracking to delivery (BR-401/403)

| Step | Frame | User sees | User does | System does | Goes to | If it fails |
|---|---|---|---|---|---|---|
| S32 | SCR-904 · Default `[BUILT]` | Custody timeline; position at **corridor/ETA band** only (PERM-212) — never exact coordinates, that's the carrier's own view | Watches, messages ops | Renders custody events as they land | — | — |
| S33 | SCR-904 · Stale | "No status update — 4h12m," flagged not hidden (BR-401) | Messages carrier/ops | Missed-interval detection — the honest common case for small carriers | SCR-905/930 escalation | — |
| S34 | SCR-904 · Transit exception | Categorised sub-type, never a generic "delay" (BR-405) | Views, messages ops | Logged as accessorial-dispute evidence | — | — |

**Truck-is-dark honesty.** SCR-904 never fabricates a position or a false-confident ETA when the feed
is absent — it shows **Stale**, timestamped. Honest default for the small-carrier segment.

---

## 8. Delivery outcome and invoice consequence (§7.4 state table, BR-501–514)

| Step | Frame | User sees | User does | System does | Goes to | If it fails |
|---|---|---|---|---|---|---|
| S35 | SCR-904 · Delivered clear | "No exceptions" | Views | `DELIVERED → POD_CAPTURED`, lines undisputed (BR-601) | SCR-906 clean invoice | — |
| S36 | SCR-904 · Delivered with exception | Type/quantity/whose-count — a **notation on `DELIVERED`**, not a separate state (§7.4) | Views, may escalate | Line moves to `HELD` (BR-603) | SCR-906 mixed lines | — |
| S37 | SCR-904 · Partial delivery | Genuine custody fork — some freight delivered, remainder routed | Views split status | Delivered portion invoices; remainder tracked, possible claim | SCR-906 + SCR-907 | — |
| S38 | SCR-904 · Delivery refused | Full refusal recorded | Initiates claim if warranted | → `RETURN_TO_ORIGIN`, no clean POD | SCR-907, RTO charges | — |
| S39 | SCR-904 · No receiver | Arrival timestamp only, no POD, carrier retains custody (BR-509) | Arranges redelivery | Detention may accrue | Redelivery / SCR-907 | — |

**Branch — delivery outcome → invoice.**

| Outcome | Invoice effect |
|---|---|
| Clean | All lines settle undisputed |
| Exception (notation) | Affected line `HELD`; rest settle (BR-603) |
| Partial | Split — delivered lines settle, remainder pends claim/RTO |
| Refused | RTO charges added; original linehaul disputed |
| No receiver | No invoice trigger yet — redelivery or RTO next |

---

## 9. Invoice review and dispute (BR-600–604)

| Step | Frame | User sees | User does | System does | Goes to | If it fails |
|---|---|---|---|---|---|---|
| S40 | SCR-906 · Default (clean) | Lines reconciled to rate confirmation + accessorials (BR-601) | Approves | `INVOICE_ISSUED → INVOICE_FINALISED` | SETTLED | — |
| S41 | SCR-906 · Partial (mixed held/clear) | Held and clear lines rendered distinctly, never blended | Approves clean lines; disputes the held one | Partial settlement — clean lines pay, held stays open (BR-603) | SETTLED (clean) / S42 (held) | — |
| S42 | SCR-906 · Dispute a line | Structured form, references line + evidence | Submits | Opens `ExceptionCase(DISPUTE_MONEY)`; provisional invoice stands | SCR-905 tracks open exception | — |
| S43 | SCR-906 · Resolved — credit note | Credit note references disputed line + claim ID, never a silent net (BR-604) | Views resolution | `ExceptionCase → RESOLVED` | SETTLED | Unresolved past window → escalation, cadence `[NEEDS INPUT]` |

**Branch — invoice clean / disputed.**

| Condition | Destination | Consequence |
|---|---|---|
| All lines evidenced | `SETTLED` | Standard terms apply (BR-611, days `[NEEDS INPUT]`) |
| Line(s) disputed | `HELD`; rest settle independently (BR-603) | `ExceptionCase(DISPUTE_MONEY)` per line |
| Resolved shipper-favor | Credit note, references claim ID | Line re-enters settlement |
| Resolved carrier-favor | Written disallowance (claims-desk side) | Line settles at original amount |

---

## Summary

**Counts.** 43 steps (S1–S43), 9 flows, 20 frames (4 `[BUILT]`: SCR-900/901/902/904; 2 `[NEW]`: Org
Setup + sub-states), 6 branch tables (eligibility, bid outcome, award outcome, cancellation-by-stage,
delivery outcome, invoice clean/disputed) per spine §5.

**Built vs. specified.** Loads dashboard, Post a Load, Auction Watch, Shipment Tracker are real and
verified, including non-default states. Award Monitor, Exception Inbox, Invoice Approval, Claim
Intake, Standing History are spec-only.

**Three questions only Boss can answer.**
1. May the shipper decline the lowest qualified bidder (BR-155/DEC-307/EC-325)? Branches A/B in §4
   build different SCR-903 screens — asked three times in source docs, answered zero.
2. Does a cascade winner get told they were second choice (EC-909)? Privacy vs. transparency.
3. What is the dispatch-proof standard (BR-142) that flips a cancel from free to a TONU claim? One
   `[NEEDS INPUT]` decides whether S27 or S28 fires for the same clock-time cancel.

**CHALLENGE filed.** §6 — BR-144 conflicts with the FRD's own `IN_TRANSIT →
CANCELLED_BY_SHIPPER(charged)` adjacency and `EC-509`'s post-pickup-pre-delivery allowance. Followed
the FRD reading; needs reconciliation before S29 is built either way.

**Most likely abandonment point.** Not the declaration form (scaffolded, autosaved) or auction watch
(passive). It's **S18 — "all bids above your limit"** on SCR-902: shipper set a ceiling in good faith,
market cleared above it, only paths forward are republish-and-wait or escalate — both slower than the
original need, and the only failure state here with no structured next-best-action attached.
