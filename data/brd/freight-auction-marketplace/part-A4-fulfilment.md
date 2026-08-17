# Part A4 — Fulfilment: Pickup, Transit, Drop

**Scope:** custody from `AWARD_ACCEPTED`/`PICKUP_SCHEDULED` through `AT_PICKUP` → `PICKED_UP` →
`IN_TRANSIT` → `AT_DROP`. Handover *at* the drop (acceptance/refusal, OS&D, BOL exception notation)
is A5's; liability outcome and Carmack claim mechanics are A8's; charge amounts are A6's — A4 defines
the *event* and its evidence, not the dollar figure. Software meets physics here: every requirement
below exists because a phone call is not evidence and an unscanned paper signature is not a
system-of-record.

---

## 1. As-Is (hypothesised) — pickup through drop today

No shipper/carrier operating data was supplied. This is a **hypothesised** baseline, industry-typical
for phone/fax/paper-coordinated truckload dispatch, tagged accordingly.

| Step | Actor | Action | Pain point |
|---|---|---|---|
| 2.1 | Carrier dispatcher | Confirms load/window by phone/fax/email | Appointment lives only in someone's memory or inbox |
| 2.2 | Driver | Arrives at shipper dock | **No system verifies driver/truck identity against the carrier actually booked** |
| 2.3 | Shipper dock staff | Loads freight; paper BOL, driver signs | No timestamp, no photo, no system copy — **A1's finding: no symmetric proof-of-readiness record** |
| 2.4 | Driver | Departs | Nobody knows the truck left until someone calls to ask |
| 2.5 | Driver | Drives; HOS logged on a device disconnected from shipper/broker | Detention and delay invisible until disputed after the fact |
| 2.6 | Dispatcher | Learns of an exception only when the driver calls | No structured exception log → accessorial billing disputes have no evidence |
| 2.7 | Driver | Arrives at receiver dock | Handoff to A5 |

`[ASSUMPTION: baseline dispatch is phone/fax/paper-coordinated, industry-typical for small-to-mid
carriers | conf: med]`

## 2. To-Be — mirrors §1 numbering

| Step | Actor | Action | What changes |
|---|---|---|---|
| 2.1 | Platform | Award converts to an accepted rate confirmation; appointment window is a structured field | Removes the phone-call-only appointment |
| 2.2 | Platform | Captures driver identity and equipment against the *awarded* carrier at check-in; mismatch flagged before loading | Closes the double-brokering blind spot (→ A2, A8) |
| 2.3 | Shipper dock / Driver | Structured pickup event — count, condition, seal, dual signature (the BOL) — captured at tender | Closes A1's proof-of-readiness gap |
| 2.4 | Platform | State moves to `PICKED_UP` the instant the BOL is captured | Departure is no longer a phone call |
| 2.5 | Carrier/Driver | Status update required within a defined interval `[NEEDS INPUT]`; a missed interval is itself a flagged event | Silence becomes visible, not invisible |
| 2.6 | Carrier/Driver | Any transit exception reported as a categorised, timestamped event | Accessorial disputes now have evidence (→ A6) |
| 2.7 | — | Arrival `AT_DROP` | Handoff to A5 |

**Cannot be resolved by asking Boss more questions** — requires observing a real dispatch desk:
actual call/message volume per load, how detention is currently evidenced (if at all), whether small
carriers already run an ELD-linked app, and what fraction of loads today involve a driver who isn't
who the dispatcher named.

---

## 3. The pickup handover — the highest-risk event on this side of the trip

Under Carmack, the BOL signed at origin is the fact every downstream shortage/damage claim is
measured against. If origin condition/count isn't captured at tender, a receiver's claim at drop has
nothing to compare against — A8 inherits an unwinnable dispute.

> **BR-400 | Must Have | Traces: OBJ-004, OBJ-006 | Source: derived from A1's finding + Carmack
> evidentiary structure**
>
> The platform shall require a structured pickup record — piece/pallet count, weight if declared,
> visible condition, seal number if sealed, and driver + shipper-representative acknowledgement — to
> be captured at the moment freight is tendered, before the shipment can transition to `PICKED_UP`.
> *Acceptance: no shipment reaches `PICKED_UP` without a pickup record bearing both acknowledgements
> and a timestamp. Not in scope: the record's format (solution layer).*

This is the "proof of readiness" A1 flagged missing on the shipper side — the record serves double
duty: it evidences the freight was ready and tendered, and is the origin baseline the drop-side POD
(A5) is compared against.

`[ASSUMPTION: a "pickup record" distinct from but structurally mirroring the delivery BOL/POD is the
correct model | conf: high]`

---

## 4. Pickup failure modes

| Trigger | State/flag | Who records | Downstream |
|---|---|---|---|
| Carrier fails to arrive within window | `CARRIER_NO_SHOW` | Shipper/platform, on expiry | → A3 (re-run award) |
| Late arrival within grace tolerance `[NEEDS INPUT]` | Late-arrival flag | Shipper | Detention candidate (§7) |
| **Wrong equipment type** on-site | `PICKUP_REFUSED` (equipment) | Shipper, at check-in | → A2 (eligibility), A6 (cost) |
| Driver/truck ≠ awarded carrier | Held pending verification, load withheld | Platform, at check-in | **→ A2/A8 — double-brokering signal, do not proceed silently** |
| Freight not ready / origin unreachable | `SHIPPER_NOT_READY` | Shipper or carrier, present party | → A1 |
| Freight differs from declaration (weight/count/commodity) | `PICKUP_REFUSED` or exception-noted | Driver, countersigned by shipper | → A8 if material |
| Wait exceeds free time `[NEEDS INPUT]` | Detention-accruing | Carrier + shipper ack | → A6 (§7) |
| Lumper required, fee paid | Lumper-fee event | Payer, at time of payment | → A6 (who bears it) |
| Live-load/drop-hook at pickup ≠ what was declared at award | Mismatch flag | Shipper or driver | → A6, A1 |
| Load unsafe or improperly secured | `PICKUP_REFUSED` (safety) | Driver — right and duty to refuse | → A8 |
| Appointment missed, no notice | Missed-appointment flag | Present party | → A6 |
| Dock closed at scheduled time | Dock-closed flag | Carrier | → A1 |
| Seal missing/broken at pickup | Seal-exception flag | Driver + shipper | → A8 (custody integrity) |

---

## 5. In-transit reality

| Trigger | State/flag | Who records | Downstream |
|---|---|---|---|
| Driver hits an Hours-of-Service limit — **a scheduled certainty on longer lanes, not an anomaly** | `TRANSIT_EXCEPTION` (HOS) | Driver's ELD is the legal record; carrier reports the stop | Cross-refs A7 (49 CFR 395 — legal constraint, not a business choice) |
| Mechanical breakdown | `TRANSIT_EXCEPTION` (breakdown) | Carrier | → A6 (delay accessorial) |
| Accident | `TRANSIT_EXCEPTION` (accident) | Carrier + law-enforcement record where applicable | → A8, A7 |
| Weather event or road closure | `TRANSIT_EXCEPTION` (weather/closure) | Carrier | Outside carrier's control — distinguish from carrier-caused delay |
| Reefer failure / temperature excursion (temp-controlled loads) | `TRANSIT_EXCEPTION` (reefer) | Carrier, with unit temp record if available | → A8 (cargo condition), A1 (temp requirement declared) |
| Cargo theft, incl. strategic theft at truck stops and staged/fictitious pickups | `TRANSIT_EXCEPTION` (theft) | Carrier reports; platform flags for investigation | **→ A8 (fraud typology), A2 (carrier identity re-check)** |
| Roadside inspection results in an out-of-service order | `TRANSIT_EXCEPTION` (OOS) | Carrier; FMCSA inspection record exists independently | → A2 (safety record), A7 |
| Truck or freight impounded | `TRANSIT_EXCEPTION` (impound) | Carrier, or platform on failure to report | → A8, needs §6 reassignment |
| Driver abandons the load | `TRANSIT_EXCEPTION` (abandonment) | Platform, on confirmed non-contact past `[NEEDS INPUT]` interval | **→ A8 (fraud/negligent-selection review), A2** |

**Visibility — the business requirement, without naming a mechanism:**

> **BR-401 | Must Have | Traces: OBJ-002, OBJ-004 | Source: derived**
>
> The platform shall require a shipment status update at least every `[NEEDS INPUT: reporting
> interval]` while `IN_TRANSIT`, and shall itself flag — rather than silently tolerate — any interval
> in which no update is received.
> *Acceptance: every `IN_TRANSIT` shipment either has a status update within the interval, or carries
> an active "no update received" flag visible to the platform and the shipper. Not in scope: the
> update mechanism itself.*

Honesty about the limit: some carriers, particularly small ones, won't proactively report anything
absent a call. This requirement doesn't make them report — it makes the platform's knowledge state
honest (flagged-unknown, not falsely-assumed-fine), which is the most a requirement can guarantee
without dictating a solution.

---

## 6. Mid-trip reassignment — freight already loaded, carrier fails after pickup

Genuinely hard. Once freight is on a specific truck it is not a re-auctionable line item the way an
unpicked-up load is — it is physically wherever that truck stopped, and moving it to another truck
(a transload) is itself a custody event with its own condition-check, new BOL leg, and cost.

> **BR-402 | Must Have | Traces: OBJ-004, OBJ-006 | Source: derived**
>
> Where a carrier fails after pickup (breakdown beyond repair window, HOS exhaustion with no relief
> driver, impound, abandonment), the platform shall require a new custody event — including a fresh
> condition/count record — at the point freight physically transfers to a different truck or driver,
> regardless of whether the carrier of record changes.
> *Acceptance: every truck-to-truck transfer has its own timestamped custody record, distinct from
> the original pickup record. Not in scope: who arranges/pays for the transload (A6); a fast re-award
> for the remaining leg (A3); liability during the gap (A8).*

Three sub-paths, none of which A4 can pick alone: (a) **relay** — same carrier substitutes
driver/truck, custody arguably doesn't break, but §4 identity re-verification still applies;
(b) **transload to a new carrier** — a genuine second custody handover, with its own cost and
liability-gap question; (c) **wait for repair** — no custody event, but a detention-equivalent delay
accrues. `[NEEDS INPUT: does the platform arrange mid-trip reassignment, or does the failed carrier
remain contractually obligated to resolve it?]` — a policy decision, not a fact A4 can supply.

---

## 7. Detention and accessorial events (event only — charge is A6's)

> **BR-403 | Should Have | Traces: OBJ-005 | Source: derived, cross A6**
>
> The platform shall capture, for every pickup and every drop, an arrival timestamp and a
> release/departure timestamp, independent of whether a charge is ultimately billed.
> *Acceptance: every custody-relevant stop has both timestamps recorded or an explicit reason why one
> is missing. Not in scope: free-time thresholds, rate, or who pays (A6).*

Lumper fees follow the same discipline: A4 records *that* a fee was incurred, amount, payer, and a
receipt reference; A6 decides who ultimately bears it.

---

## 8. Business Requirements (additional)

| ID | Requirement | MoSCoW | Traces | Source |
|---|---|---|---|---|
| BR-404 | Record `RETURN_TO_ORIGIN` as a distinct state, with its own custody event, when refused freight is brought back | Must | OBJ-004 | derived |
| BR-405 | Record a `TRANSIT_EXCEPTION` sub-category on every §5 occurrence, not a generic "delay" flag | Must | OBJ-004, OBJ-006 | derived |
| BR-406 | On a §4 driver/equipment mismatch, shipment shall not proceed to loading until a resolution outcome (substitution confirmed vs held) is recorded | Must | OBJ-006 | derived, cross A2/A8 |
| BR-407 | Live-load/drop-and-hook shall be captured at award and compared against pickup reality; mismatch recorded as an event | Should | OBJ-005 | derived |
| BR-408 | Seal number, where sealed, recorded at pickup and re-verified at drop (A5 executes; A4 supplies origin value) | Should | OBJ-004 | derived |
| BR-409 | Repeated failure to provide a status update (BR-401) beyond a longer threshold becomes a flaggable pattern visible to A2's scoring | Could | OBJ-006 | derived |

---

## 9. Edge Case register (dense — pickup through drop)

| EC | Trigger | State | Who decides/records | Unresolved |
|---|---|---|---|---|
| EC-400 | Carrier no-show at pickup window | `CARRIER_NO_SHOW` | Shipper/platform | Grace tolerance `[NEEDS INPUT]` |
| EC-401 | Late arrival within tolerance | Late-arrival flag | Shipper | Tolerance value `[NEEDS INPUT]` |
| EC-402 | Wrong equipment type on-site | `PICKUP_REFUSED` | Shipper | Whether carrier gets one substitution attempt before re-award |
| EC-403 | Driver/truck ≠ awarded carrier | Held-pending-verification | Platform | Verification method is solution layer; policy on how long to hold is open |
| EC-404 | Freight not ready / origin unreachable | `SHIPPER_NOT_READY` | Shipper/carrier | A1 owns consequence |
| EC-405 | Freight differs from declaration | `PICKUP_REFUSED` or exception-noted | Driver+shipper | Materiality threshold for refusal vs note-and-proceed `[NEEDS INPUT]` |
| EC-406 | Wait exceeds free time | Detention-accruing | Carrier+shipper | Free-time hours (A6/`[NEEDS INPUT]`) |
| EC-407 | Lumper fee incurred | Lumper-fee event | Payer | Reimbursement policy (A6) |
| EC-408 | Live-load/drop-hook mismatch | Mismatch flag | Shipper/driver | Accessorial rate (A6) |
| EC-409 | Unsafe/improperly secured load | `PICKUP_REFUSED` | Driver | Re-inspection path after correction |
| EC-410 | Appointment missed, no notice | Missed-appointment flag | Present party | Fault attribution rule `[NEEDS INPUT]` |
| EC-411 | Dock closed at scheduled time | Dock-closed flag | Carrier | Rescheduling authority (A1?) |
| EC-412 | Seal missing/broken at pickup | Seal-exception flag | Driver+shipper | Whether this alone blocks pickup |
| EC-413 | HOS limit reached mid-transit | `TRANSIT_EXCEPTION` (HOS) | Driver ELD/carrier | Relay-driver arrangement is carrier's own ops, not platform's — boundary `[NEEDS INPUT]` |
| EC-414 | Breakdown | `TRANSIT_EXCEPTION` (breakdown) | Carrier | Repair-window threshold before reassignment triggers |
| EC-415 | Accident | `TRANSIT_EXCEPTION` (accident) | Carrier/law enforcement | — |
| EC-416 | Weather/closure | `TRANSIT_EXCEPTION` (weather) | Carrier | Distinguishing carrier-fault delay from force majeure |
| EC-417 | Reefer failure/temp excursion | `TRANSIT_EXCEPTION` (reefer) | Carrier | Temp-log availability varies by equipment — cannot assume |
| EC-418 | Cargo theft / staged pickup | `TRANSIT_EXCEPTION` (theft) | Carrier report/platform flag | Detection is largely reactive; needs A8 fraud model |
| EC-419 | Roadside OOS order | `TRANSIT_EXCEPTION` (OOS) | Carrier | Whether platform pulls FMCSA inspection data independently (A2) |
| EC-420 | Impound | `TRANSIT_EXCEPTION` (impound) | Carrier/platform | Triggers §6 reassignment |
| EC-421 | Driver abandonment | `TRANSIT_EXCEPTION` (abandonment) | Platform on non-contact | Non-contact threshold `[NEEDS INPUT]`; feeds A8 |
| EC-422 | Status update silent past interval | Stale-tracking flag | Platform | Interval `[NEEDS INPUT]`; cannot force a non-reporting carrier |
| EC-423 | Mid-trip reassignment needed | Custody re-chain (§6) | Platform, policy-dependent | Who arranges/pays `[NEEDS INPUT]`; feeds A3/A6/A8 |
| EC-424 | Refusal requires freight return | `RETURN_TO_ORIGIN` | Shipper/carrier | Cost allocation (A6) |

`[ASSUMPTION: pickup-record and delivery-BOL are structurally parallel documents | conf: high]`
`[ASSUMPTION: baseline dispatch today is phone/fax/paper | conf: med]`
`[NEEDS INPUT: reporting interval for in-transit status]`
`[NEEDS INPUT: detention free-time threshold]`
`[NEEDS INPUT: whether platform or carrier arranges mid-trip reassignment]`
`[NEEDS INPUT: non-contact threshold before flagging driver abandonment]`
