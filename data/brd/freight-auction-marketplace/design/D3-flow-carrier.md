*Page: 📄 11 · Flow — Carrier / Dispatcher. Agent D3. Screens cited from `frd-F9-dashboards-screens.md`
(`SCR-9nn`). New screens `[NEW]`, justified inline. Built = verified in `prototype.html`.*

## 0. Two carriers, one product

**`OWNER_OPERATOR` (ROLE-216)** = union of `CARRIER_OWNER` ∪ `CARRIER_DRIVER` — one login is company,
equipment owner and driver at once. **`CARRIER_DISPATCHER` (ROLE-211)** runs a roster it doesn't
drive. Same screens serve both; divergence is **who fills the tuple** at S26 and never "who may
accept an award" (owner-operator is a union, not blocked by any maker-checker rule — §4.5).

## 1. Onboarding & vetting (`FRD` §5.2, §15)

FR-103: login and document vetting are **independent gates** — an unvetted org sees the shell but
cannot bid (PERM-215 needs `eligible_load`).

| S | Frame | User sees | User does | System does | Goes to | If it fails |
|---|---|---|---|---|---|---|
| S1 | `[NEW]` Carrier · Sign-up · Default. *F9 has no carrier onboarding screen, only SCR-940 (ops queue).* | Org-type + owner-operator toggle (skips forced second user, FR-102) | Enters MC/USDOT | Org created `PENDING_VERIFICATION` | S2 | Duplicate MC → account-exists error |
| S2 | `[NEW]` · IAL2 proofing | Doc + liveness (FR-101) | Uploads ID | Identity check queued | S3 | Unreadable → inline retake |
| S3 | `[NEW]` · Document upload | Checklist: authority cert, COI (BR-204), safety consent, W-9, first driver's CDL | Uploads each; saves partial | `CredentialDocument` rows, source=self-reported | S4 | Missing doc → `ERR-500`, field named |
| S4 | `[NEW]` Vetting Status · Pending. *No carrier-facing counterpart to SCR-940 exists.* | "Under review," which checks auto-cleared vs. await reviewer (Partial data) | Browses read-only; cannot open SCR-911 | Ops reviews via SCR-940 | Branch 1.1 | Upstream feed unreachable → stale flag, never auto-fails (§15.3) |
| S5 | `[NEW]` · Rejected | Named reason per element (FR-1302) | Re-uploads failing doc only | Addendum record | S4 | — |
| S6 | `[NEW]` · Approved | "Eligible to bid" | Continues | Org enters eligible pool (per-load computed, not a flag) | S10 | — |
| S7 | SCR-915 Roster · Empty (owner-operator pre-filled self+one truck) | Prompt to add tractor/trailer/driver | Adds records | Verifier+time-attributed (FR-735) | S8 | Trailer type outside taxonomy → flagged, not blocked |
| S8 | SCR-915 · Default | Expiry countdown per doc (BR-220) | — | — | S10 | Already-expired credential → asset shows `Error`, excluded pre-bid |

**Branch 1.1 — vetting outcome**

| Condition | Destination | Consequence |
|---|---|---|
| Approved (PERM-240) | S6 | Enters pool; eligibility still per-load, not wholesale |
| Rejected | S5 | Reasons + re-submit loop |
| Pending, automation clear | S4 | No shortcut — human approval required (BR-908) |
| Overridden despite FAIL | S6, flagged | Named-person override (PERM-260); addendum not edit; itself evidence later (FR-1352) — carrier sees only "approved" |
| Org suspended post-approval | `[SCR-910] · Permission denied` (built) | New bids/awards blocked; in-flight untouched (BR-230) |

## 2. Load board — eligibility is per-tuple, not per-carrier

`[SCR-910] Load Board · Default` — **built**. Filter chips (All eligible / Reefer / Dry van / Closing
soon) built and verified.

| S | Frame | User sees | User does | System does | Goes to | If it fails |
|---|---|---|---|---|---|---|
| S10 | `[SCR-910] · Default` (built) | Only loads with ≥1 eligible tuple — filtered server-side, never client-hidden (non-eligible = not-found, PERM-230) | Filters, saves view | Re-evaluated per current asset/driver availability | S10 | — |
| S11 | `[SCR-910] · Loading` | Row skeletons | — | — | S10 | Timeout → Error, retry |
| S12 | `[SCR-910] · Empty` | Reason named ("reefer at capacity through Wed"), never a bare grid | Adjusts availability or waits | — | S10 on match | — |
| S13 | `[SCR-910] · Permission denied` (built) | Named reason (COI lapse), one-click remediation | Uploads renewal | Single-doc re-review | S6-equiv | — |
| S14 | `[SCR-910] · Stale data` | "Showing cached board, reconnecting" | Retries | Re-syncs | S10 | Persistent offline → badge, cached list, no phantom bid affordance |

**Non-obvious:** a listed load is not a bid-time guarantee — FR-600 re-checks per bid. A truck visible
now can lose eligibility to a double-booking the instant before submit. Must read as normal (BR-200),
named plainly in S17, not a bug.

## 3. Placing a bid — built, state machine verified

`[SCR-911] Bid & Comparison` — **built** (bid panel). Countdown, eligible-count, own-bid-only
visibility all live.

| S | Frame | User sees | User does | System does | Goes to | If it fails |
|---|---|---|---|---|---|---|
| S15 | `· idle` (built) | Price field, countdown, eligible-count, note that rival amounts are hidden | Enters price, submits | `Idempotency-Key` attached | S16 | Malformed → inline `ERR-501` |
| S16 | `· submitting` (built) | Spinner, button disabled, no double-submit | — | `eligibility()` re-checked live | S17/S18 | Network drop → retried same key, never a silent duplicate |
| S17 | `· rejected [NEW state]` | Explicit reason + failing tuple element, never bare "failed" | Fixes element or picks another truck | Logged as attempt only, never a bid row | S15 | — |
| S18 | `· submitted` (built) | "Bid received — $X, locked until close" — explicit, never silent | Watches or leaves | — | S18/S19 | — |
| S19 | `· outbid` (built) | "You've been outbid," prior amount shown, new field pre-focused | Re-bids or lets stand | New bid supersedes for ranking; both retained | S16 | Below `min_decrement` (`DEC-311`) → `ERR-512`, field-level |
| S20 | `· withdrawn` | "Withdrawn — recorded against your history" | — | Policy-gated (`[NEEDS INPUT]`) | S15 | Post-close withdrawal → decline-equivalent, penalty implication shown |

**Anti-pattern check:** the built states already avoid it — every price change re-renders the panel's
headline confirmed number. A toast fading without changing that number is the rejected pattern; do
not regress when wiring real data.

**Branch 3.1 — bid outcomes**

| Outcome | Frame | Consequence |
|---|---|---|
| Accepted, standing | S18 | Locked, superseded only by a lower valid bid |
| Outbid | S19 | Forces explicit re-bid decision, never auto-rebids |
| Rejected — ineligible | S17 | Never ranked; attempt only |
| Withdrawn pre-close | S20 | Against bidder's own standing, not visible to rivals |
| Closed, not selected | Post-close card: "not selected," no clearing price (§4.4 mask) | No action |

## 4. The rival-visibility fork — build-blocking, not decided here

`DEC-302`/`303` open; F2's mask table (§4.4) defaults **rival amounts ✗ always, identities ✗ never**
— S15-S19 already assume the conservative default. Same `bid-panel` component, three swappable
shapes, **none selected**:

| Option | Adds | UI consequence | Risk |
|---|---|---|---|
| **(a) None** (built default) | Nothing beyond own bid + countdown + count | Cleanest, least informative | Weak signal for re-bid decisions |
| **(b) Rank-only** | "#2 of 5 eligible" badge | No amount ever rendered | At small decrements, rank alone leaks approximate price (EC-908) |
| **(c) Leading-price band** | Rounded range | Must never render exact figure | Named leak vector as decrements shrink (F2 finding) |

**CHALLENGE:** shipping past (a) without `DEC-302`/`303` locked risks a `BR-717` violation in
production, not a UI bug — same challenge F9 §2.2 already filed. D3 confirms the built default is
safe; (b)/(c) are component-ready, not wired.

## 5. Winning — award accept, decline, lapse

F10's finding, load-bearing here: **a missed `award.confirmed` is an uncollected load** — costliest
notification failure in the system (`EVT-1006`, T0, multi-channel, escalates to voice/ops if
unacknowledged, §12.5).

| S | Frame | User sees | User does | System does | Goes to | If it fails |
|---|---|---|---|---|---|---|
| S21 | `[NEW]` Award Notification & Accept · Default. *F9's carrier section has no accept-award screen; SCR-903 is shipper-side only.* Full-screen interrupt, never a dismissible toast (mirrors SCR-920). | Rate (linehaul+FSC+accessorials, BR-600), pickup window, countdown to lapse (`[NEEDS INPUT]` window) | Accept / Decline | Accept → `AWARDED → AWARD_ACCEPTED`; rate confirmation ack required | S22/S23 | Idempotency-Key required; double-tap accept is a no-op |
| S22 | `· Accepted` | Confirmation, "assign driver & truck next" | Proceeds | Asset-lock candidate begins (finalises S27) | S27 | — |
| S23 | `· Declined` | Confirmation, no invented penalty framing | — | `AWARD_DECLINED` → cascade/re-auction (`DEC-309`) | exits | — |
| S24 | `· Lapsed` | "Expired — no response in time" | — | `AWARD_LAPSED` automatic | exits | **The failure F10 names costliest** — see 5.1 |
| S25 | `[SCR-916]` Settlement · Default | Rate confirmation on file | — | — | S27 | — |

**Branch 5.1 — award outcome**

| Outcome | Trigger | Consequence |
|---|---|---|
| Accepted | Explicit tap in window | → S27 assignment |
| Declined | Explicit tap | Cascade/re-auction per `DEC-309`; no re-offer absent that decision |
| Lapsed | No response before window closes | Same fork; T0 voice/ops-page escalation exists specifically so S21 is never missed |

## 6. Assigning driver and truck — owner-operator vs dispatcher diverge

`[SCR-912] Fleet Assignment` — spec only. Tractor/trailer independent assets (FR-700); HOS is Option
B — bounded attested feasibility flag, never a duty log (`DEC-700`, §9.6).

| S | Frame | User sees | User does | System does | Goes to | If it fails |
|---|---|---|---|---|---|---|
| S26 | `[SCR-912] · Default` — **owner-op**: pre-filled self+sole truck, one confirm | Pre-bound tuple | Confirms | `EquipmentPairing` bound; eligibility re-run | S28 | — |
| S26d | `[SCR-912] · Default` — **dispatcher**: driver/tractor/trailer pickers, `AVAILABLE`-only per window | Roster filtered by time-window (FR-720) | Selects each independently | Same binding call | S28 | Committed-elsewhere pick → `ERR-537`, shown disabled with reason pre-selection |
| S27 | `· Contested` (EC-913) | "Truck B unavailable — bound to LD-48xxx" | Picks another asset | Optimistic lock; losing dispatcher sees this live | S26d | — |
| S28 | `· HOS check` | "Checking…" then FEASIBLE/INFEASIBLE, never silent | — | Attested hours vs. estimated transit (FR-750/751) | S29/S30 | Signal source down → "not evaluated," never false-safe green (EC-912) |
| S29 | `· Valid` | Bound tuple, dispatch-ready | Confirms | `Assignment` finalised; asset lock applied | S32 | — |
| S30 | `· Error — HOS infeasible` | Named reason | Reassigns, or overrides if `DEC-701`=warn-only | Hard-block vs. warn is `[NEEDS INPUT]` | S26d/S29 | — |
| S31 | `· Error — document lapsed` | Named credential + blocked asset | Renews or picks another asset | That asset only excluded; award unaffected unless BR-218/219 timing | S26d | — |

**Branch 6.1 — assignment outcome**

| Condition | Destination | Consequence |
|---|---|---|
| Valid, HOS feasible | S29 | Dispatch-ready |
| HOS infeasible | S30 | Block or warn per `DEC-701`, never silent |
| Document lapsed on selected asset | S31 | Asset excluded; award untouched unless lapse timing hits BR-218/219 |
| Two dispatchers race one asset | S27 | Loser sees explicit contested state, no silent overwrite |

## 7. Dispatch & en-route management

`[SCR-913]` Active Loads (exception-forward, like SCR-900) and `[SCR-914]` Breakdown Report — spec
only.

| S | Frame | User sees | User does | System does | Goes to | If it fails |
|---|---|---|---|---|---|---|
| S32 | `[SCR-913] · Default` | Every truck in flight, exceptions ranked above on-track | Drills into a trip | — | S33 | — |
| S33 | `· trip detail`, pre-pickup | Bound tuple vs. expected | Substitutes driver/truck before pickup | Re-checks eligibility on new tuple (FR-713) | S26d | New tuple fails gate → substitution blocked, original stands |
| S34 | `· trip detail`, post-pickup | Same UI, flagged "requires a custody event" | Substitutes | Logged requester+reason; award record unchanged | S32 | Undisclosed swap → fraud queue (EC-709: trailer-VIN mismatch is a named gap) |
| S35 | `[SCR-914] · Report breakdown` | Category picker (BR-405), evidence, relief request | Submits | `TRANSIT_EXCEPTION` case → SCR-930 (ops, built) | S32, flagged | Owner-operator, no org substitute (EC-705): "no internal relay available" shown explicitly, not hidden as generic error |
| S36 | Pickup arrival check (driver-side, SCR-922/923, out of D3 ownership) | — | Arriving driver+tractor+trailer checked against bound tuple (BR-221/227) | Match proceeds; mismatch holds+flags | S37/fraud | **Arriving tuple ≠ bound tuple is the double-brokering signal (BR-221/224/806)** — the one check dispatcher cannot self-clear; routes to ops |
| S37 | `[SCR-913] · in transit` | Exact position (own fleet, PERM-261), ETA, milestones | Messages driver | — | delivery flow | Stale >2h → flagged banner, never hidden (BR-401) |

## 8. Getting paid

`[SCR-916] Settlement Status` — spec only.

| S | Frame | User sees | User does | System does | Goes to | If it fails |
|---|---|---|---|---|---|---|
| S38 | `· Default` | Rate confirmation + accessorials + FSC, reconciled total (BR-601) | Reviews | Invoice composed against rate confirmation | S39 | Bid *is* the rate-confirmation base by construction (BR-307) — no mismatch state possible |
| S39 | `· Partial data` | Some lines `HELD` (OS&D/dispute), rest paying standard cycle (BR-603) | Contacts ops on held line | Clean lines settle independently | S40 | — |
| S40 | `· factored` | Remit-to shows factor's instructions, never carrier's own bank details, once NOA on file (BR-606/608) | Reviews, cannot override without sign-off | 100% payable routes to factor of record | S41 | Forged/expired NOA → `ERR-557`, flagged to fraud, held not misrouted |
| S41 | `· quick-pay offer` | Elective, disabled while any line `HELD` (BR-609/610) | Elects or declines | Funded from platform capital/financing partner | S42 | — |
| S42 | `· Settled` | Payout confirmed, 1099-NEC accrual updated | — | Load → `COMPLETED` | exits | Undisclosed factoring found mid-dispute → `ERR-560`, held, never double-paid |

---

**Counts.** 42 numbered steps (S1-S42, S26/S26d owner-operator/dispatcher split) across 9 sub-flows ·
frames: 3 built (`SCR-910`, `SCR-911`, `SCR-930` referenced) + 13 spec-only F9 screens
(`SCR-912`-`916` + states) + 9 `[NEW]` (sign-up ×3, vetting status ×3, award accept/decline/lapse ×3)
· 5 branch tables (§1.1, §3.1, §5.1, §6.1, plus the eligibility-reasons pattern repeated inline at
S17/S26d/S30/S31 rather than tabled twice).
