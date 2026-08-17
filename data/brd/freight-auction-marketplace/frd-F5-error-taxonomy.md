# F5 — Error taxonomy and failure semantics

ID block: `ERR-500`–`599` (67 allocated, 33 reserved) · `EC-500`–`599` (F5's own block, distinct
from the BRD-phase `EC-1xx`–`9xx`, cited below by reference).

**Method note.** F3's FRD state-machine output did not exist yet. Class 3 is generated from the
BRD's reconciled table (`BRD-v1.md` §7.4, 24 states, superseding spine.md §3's shorter list). If F3
diverges, class 3 regenerates mechanically.

Envelope is `frd-spine.md` §4, unchanged: `{error:{code, message, field?, details, trace_id}}`.
Each row below adds an `ERR-` id (this document's) and an HTTP status to that contract.

---

## 1. Validation — `ERR-500`–`509`

| ID | Code | HTTP | Trigger |
|---|---|---|---|
| 500 | `REQUIRED_FIELD_MISSING` | 400 | Declared field absent (weight, commodity, pickup window) |
| 501 | `FIELD_TYPE_INVALID` | 400 | Wrong type/format (date, enum, currency) |
| 502 | `FIELD_VALUE_IMPLAUSIBLE` | 422 | Valid but implausible (weight = 1 lb) — EC-100, `[NEEDS INPUT]` bounds |
| 503 | `FIELD_VALUE_OUT_OF_RANGE` | 400 | Negative weight/price, zero dimensions |
| 504 | `STOP_SEQUENCE_INVALID` | 400 | Drop scheduled before pickup, or before publish time |
| 505 | `EQUIPMENT_ATTRIBUTE_CONFLICT` | 422 | Impossible pairing — temp range on a dry van, hazmat class on unplacarded equipment (A2 taxonomy) |
| 506 | `DOCUMENT_FORMAT_UNSUPPORTED` | 400 | Uploaded document unreadable/unverifiable |
| 507 | `DECLARATION_INCOMPLETE_FOR_PUBLISH` | 422 | Individually-valid fields, still fails the publish gate (A1) |
| 508 | `IDENTIFIER_MALFORMED` | 400 | Malformed resource id / idempotency key |
| 509 | `PAGINATION_CURSOR_INVALID` | 400 | Expired or tampered cursor (frd-spine §4) |

## 2. Business-rule violations — `ERR-510`–`523`

Pure business conditions, not reducible to a transition guard alone (guards that *are* pure
state-machine conditions live in class 3, cross-referenced from here).

| ID | Code | HTTP | Trigger | Traces to |
|---|---|---|---|---|
| 510 | `BID_BELOW_ELIGIBILITY_FLOOR` | 422 | Bid from a carrier failing A2's gate | DEC-LOCK-001 (canonical example, frd-spine §4) |
| 511 | `BID_WINDOW_CLOSED` | 409 | Bid submitted after `AUCTION_CLOSED` | A3; state-derived, → `ERR-525` |
| 512 | `BID_BELOW_MINIMUM_DECREMENT` | 422 | Undercuts by less than the platform floor | DEC-311, `[NEEDS INPUT]` value |
| 513 | `LOAD_AMENDMENT_BLOCKED_LIVE_AUCTION` | 409 | Amendment attempted once bids exist | A1 BR-136/138 |
| 514 | `CARRIER_INELIGIBLE_FOR_AWARD` | 409 | Award target fails gate on re-verification | A2 + DEC-LOCK-001; state `AWARD_VOIDED_INELIGIBLE` |
| 515 | `POD_PRECONDITION_NOT_MET` | 409 | POD submitted before pickup is recorded | A5 BR-500; state-derived, → `ERR-527` |
| 516 | `CANCELLATION_BLOCKED_POST_DELIVERY` | 409 | Cancel attempted at/after `POD_CAPTURED` | spine §3 custody chain — contrast `EC-509` (pre-delivery, allowed with charge) |
| 517 | `AWARD_ACCEPTANCE_WINDOW_EXPIRED` | 409 | Accept attempted after lapse | A3 BR-309, DEC-309 |
| 518 | `DUPLICATE_FREIGHT_REFERENCE` | 422 | Same freight, two open loads, same org, once detected | A1 BR-132; EC-101 detection gap `[NEEDS INPUT]` |
| 519 | `BROKER_BID_UNDISCLOSED` | 422 | Broker bids without required disclosure | A3 BR-313, EC-319; A7 EC-706 — contrast `EC-512` (disclosed, permitted) |
| 520 | `COMMON_OWNERSHIP_BID_REJECTED` | 409 | Second bid from a commonly-owned entity | A3 BR-316 |
| 521 | `PERMIT_OR_ENDORSEMENT_MISSING` | 422 | Load needs an endorsement no bidder holds | A2/A3, EC-330 |
| 522 | `CARRIER_STANDING_SUSPENDED` | 403 | Action by a suspended carrier/org | A8/A9 BR-902, EC-213, EC-826 |
| 523 | `RESERVE_CEILING_MATH_INVALID` | 422 | Ceiling ≤ 0 or ≤ minimum decrement | DEC-306 |

## 3. State-machine violations — `ERR-524`–`529`

**Generation rule.** For every state `S`, `allowed_next(S)` = states whose "enters from" cell names
`S` in BRD-v1 §7.4. A transition request whose target ∉ `allowed_next(current)` is rejected as
`ERR-524`, with `details.allowed_next` listing the legal set — never a bare 409.

Adjacency (24 states, by reference not restated in full): `DRAFT→{PUBLISHED}`;
`PUBLISHED→{AUCTION_OPEN, CANCELLED_BY_SHIPPER}`; `AUCTION_OPEN→{AUCTION_EXTENDED, AUCTION_CLOSED,
AUCTION_FAILED_NO_ELIGIBLE_CARRIER, CANCELLED_BY_SHIPPER}`; `AUCTION_CLOSED→{AWARD_PENDING,
AUCTION_FAILED_NO_BIDS, AUCTION_FAILED_ALL_ABOVE_LIMIT}`; `AWARD_PENDING→{AWARDED,
AWARD_VOIDED_INELIGIBLE}`; `AWARDED→{AWARD_ACCEPTED, AWARD_DECLINED, AWARD_LAPSED}`;
`AWARD_ACCEPTED→{PICKUP_SCHEDULED, CANCELLED_BY_SHIPPER}`; `PICKUP_SCHEDULED→{AT_PICKUP,
CARRIER_NO_SHOW, CANCELLED_BY_SHIPPER}`; `AT_PICKUP→{PICKED_UP, SHIPPER_NOT_READY, PICKUP_REFUSED}`;
`PICKED_UP→{IN_TRANSIT}`; `IN_TRANSIT→{AT_DROP, TRANSIT_EXCEPTION, DAMAGED/LOST/PILFERED,
FRAUD_SUSPECTED, CARRIER_SUSPENDED_IN_FLIGHT, CANCELLED_BY_SHIPPER(charged)}`;
`AT_DROP→{DELIVERED, PARTIAL_DELIVERY, DELIVERY_REFUSED, DELIVERY_ATTEMPTED_NO_RECEIVER}`;
`DELIVERED→{POD_CAPTURED, CLAIM_OPEN}`; `POD_CAPTURED→{INVOICE_ISSUED}`;
`INVOICE_ISSUED→{INVOICE_FINALISED}`; `INVOICE_FINALISED→{SETTLED}`; `SETTLED→{COMPLETED}`.
`DISPUTED` reachable from any state; `CLAIM_OPEN` from `DELIVERED` onward and earlier.

| ID | Code | HTTP | Trigger |
|---|---|---|---|
| 524 | `STATE_TRANSITION_INVALID` | 409 | Generic — target ∉ `allowed_next(current)` |
| 525 | `AUCTION_ALREADY_CLOSED` | 409 | Bid/withdraw attempted once `AUCTION_CLOSED`+ — instance of 524, ties `ERR-511` |
| 526 | `LOAD_NOT_YET_PUBLISHED` | 409 | Action requiring `PUBLISHED`+ attempted on `DRAFT` |
| 527 | `CUSTODY_PRECONDITION_NOT_MET` | 409 | Transit/drop/POD action attempted before `PICKED_UP` — generalises "POD before pickup" |
| 528 | `TERMINAL_STATE_IMMUTABLE` | 409 | Mutation attempted on `COMPLETED`/`CLOSED_UNRESOLVED`/a cancelled terminal |
| 529 | `CONCURRENT_TRANSITION_SUPERSEDED` | 409 | Target state changed between the client's read and write — optimistic-lock mismatch, → class 5 |

## 4. Authorization — `ERR-530`–`533`

F2 owns the boundary; this is the code shape it emits through. **Rule:** default to
`RESOURCE_NOT_FOUND` whenever an actor knowing a resource *exists* is itself sensitive (another
shipper's `DRAFT`, a competing carrier's bid). Use `ACCESS_DENIED` only when the actor is already a
visible party to the resource (a carrier bidding on the load) but lacks that action's permission —
enumeration isn't a risk once the relationship is already mutually known.

| ID | Code | HTTP | Trigger |
|---|---|---|---|
| 530 | `NOT_AUTHENTICATED` | 401 | Missing/invalid/expired token (F1) |
| 531 | `RESOURCE_NOT_FOUND` | 404 | Doesn't exist **or** exists-but-invisible, indistinguishably |
| 532 | `ACCESS_DENIED` | 403 | Known relationship, wrong role/permission for this action (frd-spine §3) |
| 533 | `SCOPE_CONDITION_NOT_MET` | 403 | Permission exists abstractly; `own_org`/`own_site`/`assigned_load`/`eligible_load` fails at evaluation |

## 5. Concurrency and race — `ERR-534`–`539`

Two bids at the same instant resolve **silently** (deterministic receipt-sequence order, `EC-500`) —
no code. Everything else here **must surface**; silent resolution would misattribute money/custody.

| ID | Code | HTTP | Trigger | Traces to |
|---|---|---|---|---|
| 534 | `AWARD_TARGET_BID_WITHDRAWN` | 409 | Award computed against a bid withdrawn in the same window | A3 EC-311/312, DEC-309 cascade |
| 535 | `POD_ALREADY_CAPTURED` | 409 | Second POD write for a load that already has one | second-actor race, not a replay |
| 536 | `INVOICE_ALREADY_ISSUED` | 409 | Duplicate invoice generation for one load | A6 |
| 537 | `TRUCK_ALREADY_COMMITTED` | 409 | Two dispatchers assign one truck to overlapping windows | A2 EC-206 — should be prevented structurally; this is the guard when it isn't |
| 538 | `ELIGIBILITY_LAPSED_MID_AUCTION` | 409 | Bid voided — authority/insurance lapses between bid and close | A3 EC-303/320 |
| 539 | `CLAIM_CONCURRENT_UPDATE` | 409 | Two desks (insurer, platform ops) write conflicting claim outcomes | A9 EC-909-adjacent, optimistic lock |

## 6. Idempotency — `ERR-540`–`543`

Replay with an **identical** key and **identical** payload is not an error — return the original
response verbatim, no new side effect. The trap is the other two cases:

| ID | Code | HTTP | Trigger |
|---|---|---|---|
| 540 | `IDEMPOTENCY_KEY_REPLAY_MISMATCH` | 409 | Same key, **different** payload — never processed as new, never served stale (frd-spine §4, the genuine trap) |
| 541 | `IDEMPOTENCY_KEY_REUSE_ACROSS_RESOURCE` | 409 | Same key bound to a different endpoint/resource than first use |
| 542 | `IDEMPOTENCY_KEY_IN_PROGRESS` | 409 | Retry fired while the first attempt with this key is still executing — client backs off, `Retry-After` |
| 543 | `IDEMPOTENCY_KEY_EXPIRED` | 409 | Key presented after retention window; original result unrecoverable (frd-spine §4: "≥24h", exact value `[NEEDS INPUT]`) |

## 7. External dependency failure — `ERR-544`–`549`

Per-dependency posture — **stop / degrade / proceed-and-flag** — answered once, not per-incident.
**BRD A2's rule governs throughout: a physical trip is never auto-aborted by a data problem**
(BR-218/219, EC-202/203). Degrade/proceed-and-flag responses are **200s with a warning in `details`**;
only STOP produces an `ERR-`.

| ID | Code | HTTP | Dependency | Posture |
|---|---|---|---|---|
| 544 | `ELIGIBILITY_SOURCE_UNAVAILABLE_NO_FALLBACK` | 422 | FMCSA authority/safety feed | Degrade on cached snapshot within a grace window `[NEEDS INPUT]`; STOP only with no cache at all |
| 545 | `INSURANCE_VERIFICATION_UNAVAILABLE_NO_FALLBACK` | 422 | COI verification | Same posture; STOP only with no COI on file or grace exceeded |
| 546 | `SETTLEMENT_PROVIDER_UNAVAILABLE` | 503 | Payment/settlement | Degrade — queue settlement, hold only `INVOICE_FINALISED→SETTLED`; never touches custody states |
| 547 | `DOCUMENT_STORE_UNAVAILABLE` | 503 | Document/image store (COI, BOL, POD) | STOP where the document is structurally required — mitigated by offline queueing, class 8 |
| 548 | `ESIGN_PROVIDER_UNAVAILABLE` | 503 | e-sign / rate-confirmation | `[NEEDS INPUT]` whether mandatory for `AWARD_ACCEPTED`; STOP if so |
| 549 | `UPSTREAM_DEPENDENCY_TIMEOUT` | 504 | Any uncatalogued upstream call | Generic fallback |

**Telematics/tracking is the one dependency with no STOP path at all** — always proceed-and-flag;
stale-tracking is `EC-502`, never an error, never halts or reverses a trip.

## 8. Offline and mobile — `ERR-550`–`553`

**Rule.** The canonical state machine, not wall-clock sync order, is authoritative. A queued event is
accepted at sync **only if still a legal transition from the load's current state**. If canonical
state moved on while offline (ops recorded `DELIVERY_REFUSED` while a driver's `POD_CAPTURED` sits
queued), the event is **rejected and routed to human reconciliation** — never silently applied, never
silently dropped. Either silent choice can misdirect money; this rule picks a visible failure over a
silent wrong one.

| ID | Code | HTTP | Trigger |
|---|---|---|---|
| 550 | `OFFLINE_QUEUE_CONFLICT_STATE_ADVANCED` | 409 | Queued event's precondition state no longer matches canonical state at sync — → `ERR-524` |
| 551 | `OFFLINE_QUEUE_EXPIRED` | 409 | Queued action exceeds retention before sync; discarded, re-capture required (`[NEEDS INPUT]` retention) |
| 552 | `OFFLINE_TIMESTAMP_UNTRUSTED` | 422 | Device clock skew exceeds tolerance on a money-bearing timestamp — detention, HOS (`[NEEDS INPUT]` tolerance) |
| 553 | `OFFLINE_SYNC_ORDER_AMBIGUOUS` | 409 | Multiple queued events for one load sync out of causal order — routed to reconciliation |

## 9. Money-adjacent failures — `ERR-554`–`560`

| ID | Code | HTTP | Trigger | Traces to |
|---|---|---|---|---|
| 554 | `PAYOUT_BLOCKED_CLAIM_OPEN` | 409 | Full settlement attempted while any invoice line is claim-held | A6 issued/finalised split |
| 555 | `DEDUCTION_EXCEEDS_PAYABLE` | 422 | OS&D deduction produces a negative balance | A6 EC-608, `[NEEDS INPUT]` recovery |
| 556 | `ACCESSORIAL_EVIDENCE_MISSING` | 422 | Claimed accessorial has no supporting record (e.g. detention log) | A6 EC-604, `[NEEDS INPUT]` default policy |
| 557 | `FACTORING_NOA_INVALID` | 422 | Forged or expired Notice of Assignment | A6 EC-602; flagged to A8 as fraud |
| 558 | `FACTORING_NOA_RELEASE_PENDING` | 409 | Carrier switched factors; prior NOA on file, no signed Release | A6 EC-603 |
| 559 | `PAYEE_OF_RECORD_AMBIGUOUS` | 409 | Broker-vs-asset-holder payee undetermined at settlement | A6 EC-607, `[NEEDS INPUT]` payee rule |
| 560 | `PAYMENT_HELD_DOUBLE_PAY_RISK` | 409 | Platform-initiated hold — undisclosed factoring found mid-dispute, after direct payment | BRD A6 (paying carrier not its factor risks paying twice) |

## 10. Generic / system — `ERR-561`–`566`

| ID | Code | HTTP | Trigger |
|---|---|---|---|
| 561 | `RATE_LIMIT_EXCEEDED` | 429 | Per frd-spine §4 headers; limits `[NEEDS INPUT]` |
| 562 | `INTERNAL_ERROR` | 500 | Unclassified — generic user message, detail only in logs + `trace_id` |
| 563 | `SERVICE_UNAVAILABLE_MAINTENANCE` | 503 | Planned maintenance window |
| 564 | `METHOD_NOT_ALLOWED_ON_RESOURCE` | 405 | Verb misuse — e.g. delete on an immutable audit record |
| 565 | `REQUEST_ENTITY_TOO_LARGE` | 413 | Document/image upload exceeds size limit `[NEEDS INPUT]` |
| 566 | `API_VERSION_UNSUPPORTED` | 410 | Deprecated/unsupported version requested |

---

## 11. Partial-failure handling

The mutating core of any transaction is atomic at the DB boundary; **side effects are decoupled and
retried independently** — a failed `load.awarded` webhook never rolls back the committed award
(frd-spine §4 event convention). Any batch/bulk endpoint returns a per-item result array with a
per-item envelope, not one aggregate status; whether batch endpoints exist is `[NEEDS INPUT]` (F4).

## 12. Human-safe messaging — two layers, one code

`message` is always safe for a user; `details` is structured and machine-safe (field names,
`allowed_next`, a `warning` object) — **never** a raw exception, stack trace, SQL constraint, or
vendor name. Same code, two renderings:

- **Driver (mobile), `DOCUMENT_STORE_UNAVAILABLE`:** "Couldn't save the delivery photo — it's saved
  on your phone and uploads automatically. Nothing is lost." *(no code shown, offline-queue implied)*
- **Integrating TMS (API), same code:** full envelope — `code`, `message`, `details:{retry_after,
  queued:true}`, `trace_id` — for programmatic retry logic.

The `code`→driver-copy mapping is a presentation-layer table, not a new error class — F9/F10 own it.

---

## 13. `EC-` register — failures the system absorbs, not rejects

| ID | Trigger | Behaviour | Who decides | Unresolved |
|---|---|---|---|---|
| EC-500 | Two bids at the same instant | Resolved silently, deterministic receipt-sequence order | Platform | Sequencing granularity `[NEEDS INPUT]` |
| EC-501 | Idempotent replay, identical key + payload | Original response returned verbatim, no new side effect | Platform | — |
| EC-502 | Telematics/tracking feed goes silent | Stale-tracking flag only; trip never auto-aborted | Platform (A2 BR-219) | Silence interval `[NEEDS INPUT]` |
| EC-503 | COI/authority lapses between `AWARDED` and `PICKUP_SCHEDULED` | Flagged for ops review, not auto-cancelled | A9 | Grace window `[NEEDS INPUT]` |
| EC-504 | Authority/insurance lapses mid-transit, post-custody-transfer | Flagged, no automatic transit action | A9/A4 | — |
| EC-505 | Consignee signs clear without inspecting | Stored as clear; undetectable at capture, not a system failure | — | Real-world limit, not solvable in software |
| EC-506 | Declared vs. scale weight, small margin | Notice only, not rejected (large mismatch → `PICKUP_REFUSED`, a state transition, not this) | A4/A8 | Tolerance band `[NEEDS INPUT]` |
| EC-507 | Ceiling set below plausible market rate | Warned at publish, never blocks | Shipper | — |
| EC-508 | Detention accrues from slow unloading | Timestamp fact captured; fault attribution deferred | A5/A6 | Fault rule `[NEEDS INPUT]` |
| EC-509 | Shipper cancels post-pickup, pre-delivery | Allowed, with a financial consequence (TONU/partial-haul) — contrast `ERR-516` | A1/A6 | — |
| EC-510 | Offline event syncs in causal order matching canonical state | Applied silently, no reconciliation needed | Platform | — |
| EC-511 | Awarded carrier declines | First-class outcome (`AWARD_DECLINED`), cascades per DEC-309 | Platform | Cascade vs. re-auction `[NEEDS INPUT]` |
| EC-512 | Winner holds broker authority, disclosed | Permitted, subject to disclosure — contrast `ERR-519` (undisclosed) | A2/A3 | — |
| EC-513 | Very-new authority bids | Age visible at review, no auto-block on age alone | Boss (DEC-201) | Threshold `[NEEDS INPUT]` |
| EC-514 | Exact tie at lowest price | Tie-break rule resolves deterministically | Platform (A3 BR-305) | Which order `[NEEDS INPUT]` |

---

**Counts.** ERR codes: 67 (500–566, 33 reserved). Classes: 10. EC- register: 15. `[NEEDS INPUT]` tags: 21.
