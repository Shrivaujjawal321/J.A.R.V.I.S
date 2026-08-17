# FRD F6 — Auction & Bidding Engine

**Owns:** auction lifecycle execution · bid intake/validation · eligibility-gate application ·
award execution · the selection record · anti-gaming controls · timers/closing.
**Consumes, does not define:** eligibility *computation* (six-element tuple, BRD A2/BR-200) is
invoked as an external function; **no FRD agent currently owns carrier/authority/insurance/safety
vetting** (F7 = driver/equipment/HOS only) — see `CHALLENGE`. Entities/states = F3's; permission
scoping/bid-visibility = F2's; error taxonomy/concurrency mechanism = F5's; API catalogue = F4's.
IDs `FR-600…`, `API-600…`, `EVT-600…`, `EC-600…`. Inherited states (BRD §8.3): `AUCTION_OPEN →
AUCTION_EXTENDED → AUCTION_CLOSED → AWARD_PENDING → AWARD_ACCEPTED / AWARD_DECLINED /
AWARD_LAPSED / AWARD_VOIDED_INELIGIBLE`; terminal: `AUCTION_FAILED_NO_BIDS`,
`AUCTION_FAILED_NO_ELIGIBLE_CARRIER`, `AUCTION_FAILED_ALL_ABOVE_LIMIT`.

## 1. Eligibility gate — computed per tuple, re-evaluated twice, never cached as a set

**FR-600.** At `AUCTION_OPEN` the eligible pool is *not* materialised as a fixed list. Each bid
submission triggers a fresh call to `eligibility(carrier, authority, insurance, safety_signal,
truck, driver, load) → {status: ELIGIBLE|INELIGIBLE, reasons[], gate_version, evaluated_at}`
(BR-200/BR-301). A truck ELIGIBLE at open and committed elsewhere five minutes later is
INELIGIBLE at its own bid attempt — checked at the moment of the act, never off an earlier
snapshot.

**FR-601.** Bid submission is rejected (`BID_CARRIER_INELIGIBLE`, `details.reasons[]` from the
gate) if the tuple fails at submission. An ineligible price is never recorded as a bid row
(BR-301) — only as a rejected-attempt event (§6 input).

**FR-602.** At `AUCTION_CLOSED → AWARD_PENDING` the engine re-runs `eligibility()` for every
recorded bid, in price order, **not just the apparent winner** — voiding the leader must fall
through without a second pass (BR-302). First tuple to re-pass becomes the candidate; every tuple
checked (pass or fail) is written to the selection record (§2) with its own `gate_version` and
`evaluated_at`, since gate data can differ between bid time and award time.

**FR-603.** A candidate that re-fails does not silently drop — the bid row transitions to
`VOIDED_INELIGIBLE_AT_AWARD` and the loop continues down price order. Pool exhausted with no pass
→ `AUCTION_FAILED_NO_ELIGIBLE_CARRIER` even though bids existed at close (EC-620).

**FR-604.** `eligibility()`'s data freshness is out of F6's control — F6 records `gate_version`
and `evaluated_at` and assumes nothing about currency. `[NEEDS INPUT: max staleness the gate may
answer from — owning agent unresolved, see CHALLENGE]`.

## 2. The selection record — evidence, written progressively, sealed at award

Not a log line; a reconstructable exhibit (BR-303, merged BR-802). Three append-only write points
on the same `selection_record` keyed to the auction:

| Write point | Trigger | Content appended |
|---|---|---|
| **Per bid** | Each valid bid accepted (FR-610) | bidder org, tuple ref, price, server-receive timestamp, idempotency key, gate result + `gate_version` at that instant |
| **At close** | `AUCTION_CLOSED` (FR-630) | frozen bid-price ordering, tie-break rule applied if any (BR-305), close-job run id, closing timestamp, pool size/bid count (BR-318) |
| **At award** | `AWARD_PENDING` resolves | for every candidate walked in FR-602: gate result + version + evidence pointers (authority status, safety snapshot, insurance evidence — as returned by the vetting function, not re-derived here); the winner; the rule applied (BR-304/305); **every excluded bidder with the specific reason** (price rank, gate fail, related-party, malformed, withdrawn) |

**FR-605.** Immutable once each write point completes — no field updated in place; a correction is
a new addendum row referencing the original (mirrors A5's BR-512). Retention
`[NEEDS INPUT: Carmack/negligent-selection limitation period, A7/A8 to confirm]`.

**FR-606.** Reconstructable **from stored data alone**, no live re-query of authority/insurance/
safety sources at read time — the acceptance test for BR-303.

**FR-607.** Every gate or ranking override (FR-640) is written with the overriding user's identity
and stated reason (BR-306); an override with no identity/reason cannot be persisted.

## 3. Bid intake and validation

**FR-610.** `POST /v1/loads/{id}/bids` requires an `Idempotency-Key` header (frd-spine §4); a
retried key with identical payload returns the original bid, not a duplicate (`BID_DUPLICATE` if
payload differs under the same key).

| Case | Result | Error code |
|---|---|---|
| Below configured floor (DEC-306, if set) | Rejected, not recorded | `BID_BELOW_CEILING` *(ceiling is a max, not a floor — see §7 DEC-306; a literal reserve-floor is not in BRD scope, flag if Boss wants one)* |
| Malformed (missing tuple ref, non-numeric price, wrong currency) | Rejected | `BID_MALFORMED`, `field` set |
| From now-ineligible carrier | Rejected, logged as attempt | `BID_CARRIER_INELIGIBLE` |
| After close (`AUCTION_CLOSED`+) | Rejected | `AUCTION_CLOSED` |
| Duplicate idempotency key, same payload | Original bid returned, 200 not 201 | — |
| Duplicate key, different payload | Rejected | `BID_DUPLICATE` |
| Withdrawal pre-close | Allowed only if DEC-`[NEEDS INPUT]` policy permits; recorded against bidder regardless (BR-308) | `BID_WITHDRAWN` (informational, not error, on success) |
| Withdrawal post-close, pre-award | Treated as a decline-equivalent, not a clean withdrawal (EC-312) | `BID_WITHDRAWAL_POST_CLOSE` |
| Re-trade / unrecorded price change post-award | Never silently accepted; requires a recorded change object (requester, reason, amount, approver) or it is unpayable (BR-310) | `RETRADE_UNRECORDED` |

**FR-611.** An accepted bid is a firm commitment until close (BR-307); no in-place price edit — a
changed price is a new bid superseding the prior one for ranking, both retained in the record.

**FR-612.** Re-trade attempts (accepted or rejected) increment a per-carrier, per-lane counter
(BR-311), read by the carrier-vetting domain and A8's fraud/trust surface — consumers, not owners.

## 4. Timers and closing — a missed close has money attached

**FR-630.** Close runs via a scheduled job holding an exclusive, idempotent close-token per
auction (`(auction_id, scheduled_close_at)`); a second invocation for the same token is a no-op
returning the already-recorded close event, not re-closing (`AUCTION_ALREADY_CLOSED`). Locking
primitive itself → F5/F12.

**FR-631.** If the close job is late (down, backlog), the auction stays `AUCTION_OPEN` past
nominal close; on recovery it closes **using bids that existed at the nominal boundary**, not at
recovery time — late-arriving bids in the gap are rejected as `AUCTION_CLOSED`, timestamp-
adjudicated, never silently included. `[NEEDS INPUT: grace-period auto-extend instead — DEC-312]`.

**FR-632.** If the system was down across a scheduled close entirely, on restart every auction
past its nominal close time is closed against its frozen boundary bid set before new bid intake
resumes for it — closing is prioritised over intake so nothing sits open indefinitely.

**FR-633.** Anti-snipe extension (DEC-305), if enabled, triggers on a bid inside the configured
window before close and extends by the configured increment; count and total elapsed extension
are capped `[NEEDS INPUT]` and written to the close event (feeds EC-328/EC-614).

**FR-634.** `AWARD_PENDING` is time-boxed (BR-309); expiry with no accept/decline moves to
`AWARD_LAPSED` automatically — also a scheduled job under FR-630's exactly-once guarantee.

## 5. Failure paths → F3 states

| BRD condition | State | F6 behaviour |
|---|---|---|
| Zero bids at close | `AUCTION_FAILED_NO_BIDS` | Selection record still written (empty), pool size 0 |
| No eligible carrier at open, or all bids fail FR-602 | `AUCTION_FAILED_NO_ELIGIBLE_CARRIER` | Every rejected/voided attempt retained as evidence |
| All bids above shipper ceiling (DEC-306) | `AUCTION_FAILED_ALL_ABOVE_LIMIT` | Bids retained; accept-above-ceiling choice `[NEEDS INPUT]` |
| Exact tie at lowest eligible price | Resolved before state change | Deterministic pre-published order (BR-305), `[NEEDS INPUT: basis]` |
| Winner declines / never responds | `AWARD_DECLINED` / `AWARD_LAPSED` (FR-634) | → DEC-309 cascade-vs-re-auction, `[NEEDS INPUT]` |
| Award lapses/declines/voids | Cascade or re-auction | Cascade re-walks FR-602's list from where it stopped; re-auction opens a new instance referencing the failed one |
| Bid withdrawn pre-award | Per §3 table | Recorded regardless of outcome |
| Close falls outside business hours | Executes unless DEC-312 sets supervised-hours-only | Award clock (FR-634) still runs; weekend pause `[NEEDS INPUT]` |

## 6. Anti-gaming controls

| Pattern | Detected how | Recorded | Ops-desk action |
|---|---|---|---|
| Shill/spoiler bidding | Bidder org resolved against shipper/platform org at submission (BR-317) | Hard-blocked, not just flagged | None — rejected inline |
| Related-party double bid (BR-316) | Ownership-link check from carrier-vetting domain, at bid time | Second bid rejected, first stands | None — rejected inline |
| Broker bids as broker-of-record and via undisclosed sub-carrier | Identity/authority-type resolution flags broker bids visibly (BR-312/313) | Flag visible pre-award | Shipper/ops decide at award, not auto-blocked |
| Collusion / rotation on a repeat lane (Sherman Act §1) | Pattern monitor over BR-311's re-trade counter + win/price history per carrier-lane (BR-315) | Flagged, never auto-penalised | Ops/counsel — F6 does not adjudicate antitrust exposure |
| Bid-shading / probing (rapid churn, EC-329) | Bid-revision rate per bidder per auction | Flagged when DEC-303 = standing-best | `[NEEDS INPUT: rate-limit threshold]` — may throttle, not just flag |
| Implausible low bid (curse/error/fraud, EC-318) | Compared to fuel-floor cost *signal* (DEC-LOCK-002, flag-only per A11) | Flagged in selection record | Ops warn-or-hold `[NEEDS INPUT]` |

**FR-640.** Every flag is written to the selection record at the write point it occurred (§2);
flags never silently gate an award — proceeding despite an open flag requires FR-607's override.

## 7. Configurability — the eleven open parameters as settings, not constants

Each is a field on a per-auction, shipper-overridable **auction ruleset** (→ F3 for the entity),
never a hard-coded value. All defaults `[NEEDS INPUT]` — none chosen here.

| DEC | Setting | Type | Default |
|---|---|---|---|
| DEC-302 | `bid_visibility_mode` | enum `OPEN` \| `SEALED` | `[NEEDS INPUT]` |
| DEC-303 | `price_disclosure_mode` | enum `STANDING_BEST` \| `RANK_ONLY` | `[NEEDS INPUT]` |
| DEC-304 | `duration_seconds`, `duration_basis` | int, enum `FIXED`\|`SHIPPER_SET` | `[NEEDS INPUT]` |
| DEC-305 | `anti_snipe_enabled`, `extension_window_seconds`, `extension_increment_seconds`, `max_extensions` | bool/int | `[NEEDS INPUT]` |
| DEC-306 | `ceiling_price`, `ceiling_disclosed` | decimal, bool | `[NEEDS INPUT]` |
| DEC-307 | `shipper_decline_right` | enum `NONE`\|`STRUCTURED_REASON_REQUIRED` (BR-156) | `[NEEDS INPUT]` — Boss decision pending |
| DEC-308 | `shipper_early_close_allowed` | bool | `[NEEDS INPUT]` |
| DEC-309 | `award_failure_mode` | enum `CASCADE`\|`RE_AUCTION` | `[NEEDS INPUT]` |
| DEC-310 | `thin_market_mode` | enum, see §8 | `[NEEDS INPUT]` |
| DEC-311 | `min_decrement` | decimal | `[NEEDS INPUT]` |
| DEC-312 | `close_calendar` | enum `ANY_TIME`\|`BUSINESS_HOURS_ONLY`\|`PAUSE_WEEKENDS` | `[NEEDS INPUT]` |

**FR-650.** Ruleset changes mid-auction are blocked; a ruleset is fixed at `AUCTION_OPEN` and
carried into the selection record's close-event (§2) so a later dispute can prove which rules
governed that specific auction — settings drift must never be retroactive.

## 8. Thin-market behaviour

**FR-660.** `bid_count < 2` or `eligible_pool_size < 2` at close sets `thin_market = true` on the
close event (BR-318) regardless of outcome. **A one-bidder auction is not awarded silently as a
normal close.** Per `thin_market_mode` (DEC-310): `AWARD_ANYWAY` (labelled in the record),
`EXTEND_AND_REOPEN` (bounded retry count, `[NEEDS INPUT]`), `CEILING_TEST_ONLY` (requires DEC-306
set), `FALLBACK_POSTED_RATE` (outside this engine's scope — hands off to a non-auction flow),
`ESCALATE_TO_OPS_DESK`. No default; F6 refuses to silently treat a one-bid close as competitive.

## 9. API surface (F6's own resources; catalogue conventions → F4)

| ID | Endpoint | Notes |
|---|---|---|
| API-600 | `POST /v1/loads/{id}/bids` | Idempotency-Key required |
| API-601 | `DELETE /v1/loads/{id}/bids/{bid_id}` | Withdrawal, subject to policy |
| API-602 | `GET /v1/loads/{id}/auction` | State + DEC-303 price disclosure, scoped by F2 |
| API-603 | `GET /v1/loads/{id}/selection-record` | Ops + involved parties only, scoped by F2 |
| API-604 | `POST /v1/loads/{id}/award/accept\|decline` | Idempotency-Key required |
| API-605 | `POST /v1/loads/{id}/award/override` | FR-607 identity+reason required |

## 10. Events

EVT-600–614: `auction.opened/extended/closed/failed_no_bids/failed_no_eligible_carrier/
failed_all_above_limit` · `bid.accepted/rejected` · `award.pending/accepted/declined/lapsed/
voided_ineligible` · `retrade.flagged` · `anti_gaming.flagged`.

## 11. Edge case register

| ID | Trigger | Behaviour | Decides | Unresolved |
|---|---|---|---|---|
| EC-600 | Truck eligible at open, committed before its bid | FR-600 re-checks per bid; rejected | Automatic | — |
| EC-601 | Truck eligible at bid, lapses before award | FR-602 walks to next candidate | Automatic | — |
| EC-602 | Every bid fails re-verification at award | `AUCTION_FAILED_NO_ELIGIBLE_CARRIER` despite bids existing | Automatic | Re-auction default? |
| EC-603 | Close job runs twice (retry/crash-restart) | FR-630 token → no-op | Automatic | — |
| EC-604 | Close job late by minutes/hours | FR-631 closes against nominal boundary, not run-time | Automatic | Grace-extend instead? `[NEEDS INPUT]` |
| EC-605 | System down across scheduled close | FR-632 closes on restart before new intake | Automatic | — |
| EC-606 | Award-lapse job itself fails to run | Award sits in `AWARD_PENDING` past window undetected | — | Needs a watchdog; owner `[NEEDS INPUT]` |
| EC-607 | Bid arrives in the gap between boundary and actual (late) close run | Rejected `AUCTION_CLOSED`, timestamp-adjudicated | Automatic | — |
| EC-608 | Two bids at the same server timestamp | Needs sub-ms/sequence tiebreak | Platform | Granularity `[NEEDS INPUT]` |
| EC-609 | Idempotency key reused, different payload / retried after drop | `BID_DUPLICATE` on mismatch; original returned on true retry | Automatic | — |
| EC-611 | Withdrawal request post-close, pre-award | Treated as decline-equivalent | Policy | Distinct penalty from true decline? |
| EC-612/613 | Re-trade demanded at dock — shipper refuses / accepted under pressure | No cancellation ladder on refusal (BR-150); acceptance = exception record, not overwrite (BR-151) | Automatic | — |
| EC-614 | Anti-snipe extension chain runs past pickup lead time | FR-633 cap; hard stop if exceeded | Platform | Cap value `[NEEDS INPUT]` |
| EC-615 | Shipper cancels mid-auction | Auction voided, bidders notified same instant | Automatic → F10 | — |
| EC-616 | Load materially amended mid-auction (A1 BR-136) | Bids priced against stale freight — must void | Automatic | Re-auction vs re-bid `[NEEDS INPUT]` |
| EC-618 | Repeated re-auctions produce no bids | Freight ages against appointment, no cap | Ops | Cap-before-escalation `[NEEDS INPUT]` |
| EC-619 | Ruleset changed while auction open | FR-650 blocks; rejected | Automatic | — |
| EC-621 | Broker wins, downstream asset-carrier not yet vetted | Award proceeds provisionally; dispatch-gate (A2 BR-223) blocks dispatch, not this engine | Automatic + external gate | — |
| EC-622 | Thin-market threshold met only after a late withdrawal | Recompute `thin_market` at close, not at last-bid time | Automatic | — |
| EC-623 | Standing-best price mode leaks rival cost structure over repeat lane | Feeds §6 pattern monitor | Ops/counsel | Fix is DEC-303's choice |
| EC-624 | Override forces award despite an open anti-gaming flag | Requires FR-607 identity+reason; never silent | Named person | — |
| EC-625 | Selection-record write fails mid-transaction | Award must not reach `AWARD_PENDING` without a complete write | Automatic | Mechanism → F5/F12 |

*(Restates BRD's EC-301–330 as system behaviour; EC-319/321/330 resolve inside the eligibility
function §1 consumes, not restated here.)*

---

**CHALLENGE:** frd-spine §5 has no FRD owner for carrier/authority/insurance/safety **vetting and
eligibility computation** (BRD A2's core content) — F7 covers only driver/equipment/HOS, narrower
than A2. F6 depends on an `eligibility()` function (§1) with no FRD home. Recommend widening F7 or
assigning a dedicated block before assembly, or the gate is under-specified end to end.
