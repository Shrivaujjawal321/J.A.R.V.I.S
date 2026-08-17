# Part A2 — Carrier, Equipment & Eligibility

**Owner:** A2. **ID block:** 200-299. **Jurisdiction:** USA. Owns carrier onboarding/vetting,
equipment/driver records, capacity, document lifecycle, and the definition of **Eligible Carrier**,
computed per load. Excludes bid/award mechanics (A3), payouts (A6), fraud typology & penalties (A8),
regulatory citation depth (A7) — referenced, not restated.

---

## A2.1 The eligibility model

A carrier is never eligible in the abstract. Eligibility is a fact about one tuple — carrier entity,
operating authority, one insured equipment asset, one licensed driver with hours available —
evaluated against one load at one point in time. The same carrier can be `ELIGIBLE` for Load A and
`INELIGIBLE` for Load B posted an hour later, because its only reefer is already committed.

| Tuple element | Must be true simultaneously |
|---|---|
| Carrier entity | Onboarded, active, not suspended; role = asset-holder or broker/agent |
| Operating authority | Active FMCSA authority matching declared role; not revoked/out-of-service |
| Insurance | COI on file, not expired, covers the specific equipment asset |
| Safety signal | Rating + CSA/SMS data on file and current; considered, not necessarily a hard gate (§A2.9) |
| Equipment asset | Type matches load; status = AVAILABLE for the load window; not committed elsewhere |
| Driver | Active CDL of required class; Clearinghouse status clear; HOS capacity sufficient |

`BR-200` | **Must** | Traces: OBJ-004, OBJ-006 | Source: derived from intake + spine §2
System shall compute eligibility **per load, at bid submission** from the six tuple elements — never
a static per-carrier flag set at onboarding. *Acceptance: a carrier with an expired COI is blocked
from bidding same-day the COI lapses, no manual step.* Out of scope: how A3 applies this gate.

---

## A2.2 Carrier onboarding & FMCSA vetting

2026 industry baseline: verify active authority against SAFER, pull CSA/SMS data, confirm insurance,
collect W-9 [research, 2026]. **Montgomery v. Caribe Transport II** (SCOTUS, May 2026) shifted broker
exposure toward documented selection tied to available FMCSA safety data at award time [research,
2026 — legal depth is A8/A7's]. Capturing that signal at award is an A2 requirement regardless of how
A8 later scores liability from it.

| ID | Requirement | Pri | Traces | Source | Acceptance |
|---|---|---|---|---|---|
| BR-201 | Verify FMCSA authority (MC/USDOT) status at onboarding and recheck recurringly | Must | OBJ-006 | derived | Status + check timestamp recorded; cadence `[NEEDS INPUT]` |
| BR-202 | Capture **authority age** at onboarding as a distinct field, not merged into pass/fail | Must | OBJ-006 | research, 2026 [verify: no universal day-threshold found; none invented] | Visible at review; no auto-block on age alone (§A2.9) |
| BR-203 | Capture declared role — asset-holder vs broker/agent — with different required documents per role | Must | OBJ-006 | spine §1 | Broker path requires broker authority + bond evidence, not equipment records |
| BR-204 | Require a COI naming the platform/broker as certificate holder, showing auto-liability + cargo cover + expiry, before bidding | Must | OBJ-006 | research, 2026 [verify minimums — A7] | No COI → `INELIGIBLE_NO_COI`, blocks all bids |
| BR-205 | Capture safety rating and CSA/SMS BASIC data at onboarding, refresh recurringly | Must | OBJ-006 | research, 2026 | "Last refreshed" timestamp visible at award review |
| BR-206 | Collect W-9 before first payout eligibility | Must | OBJ-005 (A6 executes) | Boss intake | On file precondition A6 checks; A2 only collects/stores |
| BR-207 | Verify legal name/address on onboarding record vs FMCSA SAFER record; flag mismatch | Should | OBJ-006 | research, 2026 | Mismatch holds onboarding, not silently accepted |
| BR-208 | Verify identity of the individual completing onboarding (authorized signer) | Should | OBJ-006 | `[ASSUMPTION: expected at this trust tier | conf: med]` | ID document on file, reviewable |

---

## A2.3 Equipment & driver records

| ID | Requirement | Pri | Traces | Source | Acceptance |
|---|---|---|---|---|---|
| BR-209 | Maintain equipment registry per carrier: type, VIN, plate, covering insurance policy | Must | OBJ-003/004 | spine §2 | Every bid resolves to a specific equipment record, not a carrier-level claim |
| BR-210 | Maintain driver registry: CDL number/class/state, status | Must | OBJ-006 | spine §0 | Driver record independent of account holder |
| BR-211 | Capture Clearinghouse query status (pre-employment, annual) per driver | Should | OBJ-006 | classification.md | Field present; regulatory depth is A7's |
| BR-212 | Bind driver + equipment + carrier at dispatch acceptance — the executable tuple instance | Must | OBJ-004/006 | derived | This binding is what's checked against the physical arrival at pickup (§A2.6) |
| BR-213 | Record equipment ownership/lease status as informational field, not a gate | Could | OBJ-003 | `[ASSUMPTION: informational only | conf: med]` | Not used as a hard eligibility gate absent Boss instruction |

---

## A2.4 Capacity & double-commit prevention

`BR-214` | **Must** | Traces: OBJ-003/004 | Source: derived (spine §2)
Treat each equipment asset's availability as a **time-windowed state**; prevent the same asset
counting eligible for two loads with overlapping pickup-to-delivery windows. *Acceptance: an asset
committed to Load A (Mon 08:00–Wed 14:00) is not eligible for an overlapping Load B, but is eligible
for Load C starting Wed 18:00.*

| ID | Requirement | Pri | Traces | Source | Acceptance |
|---|---|---|---|---|---|
| BR-215 | Lock a committed asset on award acceptance; release on completion/cancellation/lapse | Must | OBJ-003 | derived | No manual step to lock capacity post-award |
| BR-216 | Allow carrier self-declared unavailability (maintenance, personal), independent of any award | Should | OBJ-003 | `[ASSUMPTION: self-service needed | conf: high]` | Self-declared assets excluded from eligibility computation |

---

## A2.5 Document lifecycle — expiry and lapse

| ID | Requirement | Pri | Traces | Source | Acceptance |
|---|---|---|---|---|---|
| BR-217 | Track expiry of authority, COI, CDL; move affected entity to `INELIGIBLE_FOR_NEW_BIDS` automatically on lapse | Must | OBJ-006 | derived | Blocks new bids same-day; does not touch loads already past pickup |
| BR-218 | Lapse **between award and pickup** flags the award for ops review, does not auto-cancel | Must | OBJ-006 | task brief | Award state unchanged automatically; exception queued → A9/A4 |
| BR-219 | Lapse **after custody transfer** (mid-transit) flags the trip for ops review, no automatic transit action | Must | OBJ-006 | task brief | No auto-stop/recall/penalty at A2 layer; liability → A8, transit action → A4 |
| BR-220 | Send advance-expiry reminders before authority/insurance/CDL lapse | Should | OBJ-006 | `[ASSUMPTION: reduces unplanned lapses | conf: high]` | Cadence `[NEEDS INPUT]` |

---

## A2.6 Broker vs asset-holder, and double-brokering detection

A broker-authority bidder is legitimate, and the double-brokering vector when it wins and re-brokers
undisclosed. A2 owns identity/eligibility: who is contractually permitted to move the freight, and
whether the truck/driver that shows up matches the award. A8 owns fraud typology and consequence on
this evidence.

`BR-221` | **Must** | Traces: OBJ-006 | Source: research, 2026 (load-tracking that the actual carrier
matches the contracted carrier) [verify: regime depth via A7]
Re-verify **at pickup** that the driver and equipment physically presenting match the tuple bound at
dispatch (BR-212) — driver identity vs CDL on file, VIN/plate vs registered equipment. *Acceptance:
a mismatch on either produces a hold state and a signal to the exception path; never a silent
proceed.* Out of scope: fraud classification/penalty/claim consequence (A8); the pickup workflow
itself (A4).

| ID | Requirement | Pri | Traces | Source | Acceptance |
|---|---|---|---|---|---|
| BR-222 | Record which entity is contractually carrier-of-record for each award (asset-holder or broker/agent) | Must | OBJ-006 | derived | Carrier-of-record queryable independent of who physically executes |
| BR-223 | If the winning bidder is a broker/agent, the downstream executing asset-carrier must independently hold `ELIGIBLE` status before dispatch confirms | Must | OBJ-006 | derived | Closes the unvetted-sub-carrier gap; broker cannot dispatch an unvetted carrier |
| BR-224 | Treat undisclosed post-award substitution of carrier/equipment/driver as a policy-violation signal, distinct from disclosed, re-vetted substitution | Must | OBJ-006 | task brief | Undisclosed → signal to A8; disclosed + still-eligible → normal operational path |
| BR-225 | A2 shall NOT classify fraud, apply penalties, or resolve liability from a mismatch signal | Must | OBJ-006 | scope boundary (spine §6) | A2 output is a fact record, not a verdict |

---

## A2.7 Carrier identity theft / fictitious pickup

An impostor using a real carrier's authority and insurance is distinct from double brokering — the
carrier of record is itself defrauded.

| ID | Requirement | Pri | Traces | Source | Acceptance |
|---|---|---|---|---|---|
| BR-226 | At onboarding, verify contact details (phone/email/address) independently of the FMCSA record where possible | Should | OBJ-006 | research, 2026 | Source of each contact field (self-reported vs verified) recorded |
| BR-227 | At dispatch/pickup, re-verify driver + truck against records on file, not against what the arriving party presents unverified | Must | OBJ-006 | research, 2026 | Same mechanism as BR-221; explicitly covers impostor, not only re-broker case |
| BR-228 | Flag last-minute dispatch-contact changes (new phone/email) not matching the onboarding record | Should | OBJ-006 | research, 2026 (fictitious-pickup pattern) | Routes to review, not hard block (legitimate changes occur) |

---

## A2.8 Suspension / removal and in-flight loads

| ID | Requirement | Pri | Traces | Source | Acceptance |
|---|---|---|---|---|---|
| BR-229 | Suspending/removing a carrier moves it to `INELIGIBLE` for all new bids/awards immediately | Must | OBJ-006 | derived | No new bid or award possible post-suspension |
| BR-230 | Suspension shall NOT automatically alter a load already past pickup with that carrier | Must | OBJ-006 | task brief | In-flight load flagged for ops handling (A9/A4); not stranded by a database flag |

---

## A2.9 DEC-201 — Verification rigour vs liquidity

Most US trucking companies run very few trucks; owner-operators are a large share of capacity
`[ASSUMPTION: well-established market structure, not dataset-sourced here | conf: high]`. A
large-fleet-calibrated vetting bar removes the supply OBJ-003 needs. Genuine trade-off — Boss decides.

| Option | Description | Pros | Cons |
|---|---|---|---|
| **A — Uniform high bar** | Full vetting (age, CSA, identity) required before bidding at all | Strongest fraud/negligent-selection defense | Excludes much of small-fleet/owner-operator supply; hurts OBJ-003 |
| **B — Light bar to bid, heavy bar to win/dispatch** | Baseline (authority + insurance + W-9) unlocks bidding; full stack gates award/dispatch only | Open, liquid bidding pool; vetting cost spent only on winners | Unvetted bidders can see rates/lanes before ever being checked |
| **C — Baseline bids, tiered award review** | Same light baseline; award review tiered by risk signal — clean carriers auto-clear, flagged ones route to manual review | Matches per-load eligibility model already adopted; scales effort to risk | Needs a risk-scoring policy A2 cannot invent numbers for; may collide with A3's award-timer cadence |

No default picked. Whichever is chosen must be told to A3 — it changes how fast `AWARDED` reaches
`AWARD_ACCEPTED`.

---

## A2.10 Edge Case register

| ID | Trigger | What happens | Who decides | Unresolved |
|---|---|---|---|---|
| EC-201 | Very new authority bids on a load | Age visible at review; no auto-block per current spec | Boss (via DEC-201) | Threshold value `[NEEDS INPUT]` |
| EC-202 | COI expires between `AWARDED` and `PICKUP_SCHEDULED` | Flagged for ops review, not auto-cancelled | A9 | Grace window before ops must act `[NEEDS INPUT]` |
| EC-203 | Authority/insurance lapses mid-transit, post-custody-transfer | Flagged, no automatic transit action | A9/A4 (trip), A8 (liability) | — |
| EC-204 | FMCSA suspends/revokes authority mid-flight-load | Same as EC-203 | A9/A4/A8 | Polling cadence for FMCSA-side revocation `[NEEDS INPUT]` |
| EC-205 | Truck/driver at pickup doesn't match awarded tuple | Hold state, signal to exception path | A4 (pickup), A8 (classification) | Whether a disclosed, re-vetted substitute can proceed same-day, or must always delay |
| EC-206 | Same asset shows committed to overlapping windows | Prevented structurally (BR-214/215); occurrence = data defect | A2 | — |
| EC-207 | Broker wins, can't secure a matching asset-carrier before dispatch | Cannot confirm dispatch without an independently eligible carrier (BR-223) | A3 (award lapse/extend?) | Award-lapse handling on this path is A3's |
| EC-208 | Impostor uses a real carrier's authority/insurance docs | Caught at physical handoff via BR-227, not necessarily before | A8 (classification), A4 (halt) | Pre-award detection from onboarding data alone is not fully solvable by A2 |
| EC-209 | Driver's HOS exhausted mid-route, no eligible substitute on file | Not an A2 re-eligibility event once dispatched — a transit exception | A4 | A2 only owns whether a replacement driver must re-pass BR-210/212 |
| EC-210 | CDL suspended/revoked between onboarding and later dispatch | Driver ineligible for new bindings; doesn't retroactively affect an already-dispatched trip with a different driver | A2 | Recheck cadence `[NEEDS INPUT]` |
| EC-211 | Same entity holds both broker and asset-holder authority, bids under both on one lane | Both roles individually valid (BR-203); not automatically fraudulent | A8 (anti-gaming rule?), A3 (bid-rule interaction) | Needs a real broker/carrier in the room to assess (§8 hard rule) `[NEEDS INPUT]` |
| EC-212 | Equipment fails roadworthiness/inspection after being marked available | No inspection-status feed defined in this engagement | A2 (record capacity) | External inspection-status ingestion `[NEEDS INPUT]` |
| EC-213 | Suspended carrier has multiple loads mid-trip across shippers | Each flagged independently (BR-230); suspension doesn't cascade-cancel | A9, per load | Whether carrier may still *complete* dispatched loads is the assumed default `[NEEDS INPUT]` if harder removal wanted |
| EC-214 | W-9 legal name ≠ FMCSA authority legal name | Held for manual review at onboarding (extends BR-207) | A2 (gate); A6 consumes resolved W-9 | — |
| EC-215 | `AUCTION_OPEN` closes with zero carriers meeting the full tuple | `AUCTION_FAILED_NO_ELIGIBLE_CARRIER` | A2 (why none qualified) / A3 (auction outcome) | Whether shipper sees the reason (e.g. "no reefer in window") or just a failure `[NEEDS INPUT]` |

---

## A2.11 Dependencies and risks

| ID | Item |
|---|---|
| DEP-201 | → A3: auction engine must call A2's eligibility function at bid time and again at award confirmation |
| DEP-202 | → A7: insurance minimums, authority-age thresholds, Clearinghouse cadence need regulatory citation depth A2 doesn't own |
| DEP-203 | → A9: every "flagged for ops review" outcome (BR-218/219/230) assumes an exception desk exists |
| RSK-201 | SAFER/FMCSA data staleness — slow recheck cadence lets a carrier present eligible after real-world lapse. Mitigation: cadence decision (open). |
| RSK-202 | DEC-201 Option A, unqualified, suppresses small-fleet/owner-operator liquidity (OBJ-003). |
