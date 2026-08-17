# Part A5 — Consignee, Delivery Execution & Proof of Delivery

*Agent A5. ID block 500-599. See spine.md for canonical model; this part is not a standalone BRD.*

## A5.1 The structural problem this section exists to solve

The consignee holds no account, accepted no terms, and has no relationship to the platform — yet
their physical act (signing the BOL/delivery receipt clear or with exception) closes custody, and
under the spine's lifecycle (`DELIVERED → POD_CAPTURED → INVOICE_ISSUED`) triggers the invoice A6
issues and supplies the evidence A8's Carmack claim path depends on. A stranger with no stake in the
platform's integrity holds the pen that settles the transaction. Every requirement below exists to
make that act **provable, attributable, and honest by construction**, since it cannot be made
contractual.

`[ASSUMPTION: the consignee named on the BOL is the shipper's customer, not a platform party, with
no pre-existing account | conf: high]` — consistent with spine §1.

## A5.2 Consignee as stakeholder (formal RACI owned by A9)

A5 defines the consignee's rights and delivery-side events; A9 owns the stakeholder map/RACI. Flag
for A9: the consignee is a **non-transacting stakeholder with outsized leverage** — able to stall
settlement by refusing, disputing, or simply not being present, with no account to suspend and no
rating to threaten. A9 should model an exception-desk role for consignee-side stalls, since no other
party has authority over them.

## A5.3 Business Requirements

| ID | Requirement | MoSCoW | Traces | Acceptance condition | Source |
|---|---|---|---|---|---|
| BR-500 | A signed BOL/delivery receipt (the POD) is captured for every load before `POD_CAPTURED`; no shipment reaches `INVOICE_ISSUED` without a linked POD. | Must | OBJ-004, 006 | State transition is blocked in the absence of the record. | Derived, spine |
| BR-501 | POD records whether delivery was signed **clear** or **with exception** as a mandatory discrete field, distinct from freetext. | Must | OBJ-004, 007 | Field cannot be blank; values are mutually exclusive and machine-readable, not inferred from prose. | Derived; classification.md |
| BR-502 | "Received," "received in good condition," and "received and accepted" are kept as three separately capturable facts, never one implied status. | Must | OBJ-004 | Physical receipt can be recorded without implying condition or acceptance sign-off. | Derived; task brief |
| BR-503 | Where delivered quantity/condition differs from the BOL, POD captures a structured OS&D notation: type (over/short/damage), quantity/unit, and whose count (carrier's, consignee's, disputed). | Must | OBJ-004, 007 | OS&D is a queryable structured field, not narrative-only. | Derived |
| BR-504 | A distinct, time-stamped channel exists for damage discovered **after** signing (concealed damage), separate from at-delivery exception capture, routed to A8's claim path. | Must | OBJ-004 | Stored as its own linked record type; never overwrites the original exception field. | Derived |
| BR-505 | A clear-signed POD is flagged as materially weakening a later claim relative to an exception-signed POD; a data-integrity flag, not a liability ruling (A8 adjudicates). | Must | OBJ-004, 007 | BR-501's field is surfaced to A8's workflow without re-interpreting freetext. | Derived |
| BR-506 | Full refusal is a distinct outcome (`DELIVERY_REFUSED`) with a required reason code; blocks invoice generation for that leg pending A4's custody-return decision and A6's accessorial handling. | Must | OBJ-004, 005 | No delivery invoice line generates while in this state. | Derived; spine states |
| BR-507 | Partial acceptance is capturable at line/unit level: accepted portion gets its own clear/exception POD; refused portion flagged separately for A4. | Must | OBJ-004, 005 | Shipment supports split POD status, not one status for the whole load. | Derived |
| BR-508 | Acceptance under protest or a disputed count is a POD notation distinct from ordinary exception, preserving both parties' stated counts. | Must | OBJ-004, 007 | Schema stores carrier- and consignee-asserted counts separately when they diverge. | Derived |
| BR-509 | Where no receiver is present or hours are closed, a distinct `DELIVERY_ATTEMPTED_NO_RECEIVER` event is recorded with arrival timestamp; custody stays with the carrier, no POD created. | Must | OBJ-004 | Exists as a first-class record feeding A4's redelivery logic, not a blank/failed attempt. | Derived; extends spine per §3 |
| BR-510 | A signature is accepted from whoever is physically present and authorized by the receiving facility, without requiring a platform account or pre-registration. | Must | OBJ-004, 006 | POD capture succeeds for an unregistered signer; requirement is name/role capture, not identity verification. | Derived; spine §1 |
| BR-511 | POD captures the signer's printed name and stated role/affiliation as given at the scene, retained permanently. | Must | OBJ-004, 006 | Signer-name field is non-blank on every POD; absence is itself an exception. | Derived |
| BR-512 | POD content, once captured, is provably fixed; any later addition/correction is a separately time-stamped addendum, never an overwrite. | Must | OBJ-004, 006, 007 | Retrieval shows original capture plus an ordered addendum trail; no field silently changes. | Derived; no capture tech named, per hard rule |
| BR-513 | The system can demonstrate a POD corresponds to the freight and location actually delivered, without prescribing capture method. | Must | OBJ-004, 006 | POD links to the shipment's declared freight (A1) and delivery location; missing linkage is flagged incomplete. | Derived; anti-fraud |
| BR-514 | The pickup-stage BOL and the signed delivery record are one continuous, linked document chain, not two independent records. | Must | OBJ-004 | Querying a POD returns unbroken lineage from pickup BOL to delivery signature. | Derived |
| BR-515 | Arrival and departure time at the drop are captured as delivery-side events, independent of any charge calculation, feeding A4's exception classification and A6's detention/lumper model. | Must | OBJ-004, 005 | Timestamps exist as queryable fields on every shipment reaching `AT_DROP`. | Derived; scope split |
| BR-516 | Where a lumper service is engaged, that fact and any receipt offered are captured as a delivery-side event feeding A6's charge model; no fee amount or rule is defined here. | Should | OBJ-005 | Lumper-engaged flag and attached proof exist when applicable. | Derived; scope split |
| BR-517 | Consignee contact data supplied by the shipper is used only for delivery notification and POD-evidentiary purposes, without requiring an account; the applicable privacy regime and consent mechanics are `→ A7`. | Must | OBJ-007 | Consignee data fields are scoped to delivery + evidentiary use only; no secondary-use field exists without an A7-defined basis. | Derived; spine §0 |
| BR-518 | POD records (incl. exceptions and addenda) are retained for a period aligned to Carmack claim/suit exposure. `[NEEDS INPUT: exact retention duration — A7 to confirm against statutory minimums]` | Must | OBJ-004, 007 | A defined, non-zero, cited retention value exists before go-live. | `[NEEDS INPUT]` |

## A5.4 Clear vs. exception — why it decides everything downstream

A POD signed **clear** is the carrier's strongest evidence freight arrived intact; one signed **with
exception** preserves the consignee's/shipper's contrary position. A8's claim viability and A6's
decision to hold an invoice line pending dispute both read off this one field. The platform does not
adjudicate condition — it ensures the field is never blank, never inferred, never editable after the
fact (BR-501, BR-512).

## A5.5 Refusal & partial-acceptance outcome matrix

| Scenario | Custody outcome | Driver-facing outcome | Invoice-trigger outcome | Downstream owner |
|---|---|---|---|---|
| Full refusal, no damage claimed | `DELIVERY_REFUSED`; carrier retains custody | Holds freight, awaits return/reconsignment instruction | No delivery line; accessorial may apply | A4, A6 |
| Full refusal, damage claimed | `DELIVERY_REFUSED` + OS&D reason | Same | Line held pending claim (mirrors `INVOICE_ISSUED`/`FINALISED`) | A4, A6, A8 |
| Partial acceptance | Split: accepted portion signed, refused portion flagged | Departs with refused portion | Prorated on accepted count; remainder held | A4, A6 |
| Acceptance under protest / disputed count | Completes; POD flagged disputed, not clean-clear | Departs normally | Proceeds but flagged for review | A6, A8 |
| Consignee absent / hours closed | `DELIVERY_ATTEMPTED_NO_RECEIVER`; carrier retains custody | Departs without signature, freight retained | No trigger until a POD exists | A4 |
| Signer present, unclear authority | Completes per BR-510; role captured for evidentiary weight | Not blocked on verifying authority | Proceeds normally | — |

**Who is allowed to sign:** the person at the dock — clerk, guard, warehouse worker — is rarely a
corporate officer with authority to bind the consignee. Requiring verified authority would stop
deliveries completing in the real world. BR-510/511 capture identity-as-stated rather than
identity-as-verified, leaving "who actually signed" an A8 claim-time weighing question, not a
platform-time blocker.

## A5.6 POD fraud — requirement, not typology

Three patterns are structurally in scope for A5 to make provable-against, though A8 owns typology,
detection scoring and penalties: a forged signature, a POD photographed against freight other than
what was declared, and a POD captured before delivery actually occurred. BR-512/513 state the
requirement — content fixed at capture, attributable to the actual scene — without naming a capture
technology, per the hard rule against solution language. `→ A8` for detection and consequence.

## CHALLENGE: OS&D is a POD notation, not a lifecycle state

The spine's exception-state table lists `PARTIAL_DELIVERY / SHORT_DELIVERY / OS&D` as one row. These
differ in kind. `PARTIAL_DELIVERY` is a **custody fork** — some freight reaches the consignee, some
does not, and A4 must route the remainder. `SHORT_DELIVERY`/`OS&D` are frequently just **POD
content** — a fully-transferred, fully-signed load whose count or condition differs from
declaration, with nothing physically routed elsewhere. Forcing OS&D into its own lifecycle branch
would fork the state machine for what is often a data field on an otherwise-normal `DELIVERED →
POD_CAPTURED` transition. Recommendation: keep `PARTIAL_DELIVERY` and the new
`DELIVERY_ATTEMPTED_NO_RECEIVER` (BR-509) as true states; model over/short/damage as a structured POD
notation (BR-503) that can attach to `DELIVERED`, `PARTIAL_DELIVERY`, or `DELIVERY_REFUSED` alike.
Assembler/A10 to confirm or override.

## A5.7 Edge Case register

| ID | Trigger | What happens | Who decides | Unresolved |
|---|---|---|---|---|
| EC-500 | Full refusal, no defect claimed | `DELIVERY_REFUSED`, reason logged | Driver at scene; A4 routes custody | Return-cost allocation `→ A6` |
| EC-501 | Full refusal citing transit damage | `DELIVERY_REFUSED` + OS&D damage notation | Driver logs; A8 opens claim | Evidence standard — no tech prescribed |
| EC-502 | Partial refusal, some units damaged | Split POD (BR-507) | Driver, line-level | Downstream invoicing support for splits `→ A6` |
| EC-503 | Shortage, counts differ | OS&D "short" + disputed-count field | Dual counts recorded, unreconciled | Whose count is believed `→ A8` |
| EC-504 | Overage — extra units delivered | OS&D "over" notation | Driver logs; consignee may refuse excess only | Excess routing `→ A4` |
| EC-505 | Concealed damage after clear signature | Post-delivery report (BR-504), linked to original POD | Reported by consignee/shipper; A8 assesses | Reporting window `[NEEDS INPUT → A7/A8]` |
| EC-506 | Consignee signs clear without inspecting | Stored as clear per BR-501; not detectable at capture | Undetectable at capture time | Real-world limit, not solvable by requirement (hard rule 8) |
| EC-507 | No receiver present | `DELIVERY_ATTEMPTED_NO_RECEIVER` (BR-509) | Driver logs arrival/departure | Redelivery cadence/cost `→ A4/A6` |
| EC-508 | Receiving hours closed on arrival | Same as EC-507 | Driver logs | Appointment-fault attribution `→ A4` |
| EC-509 | Guard/security signs, no inspection authority | Accepted per BR-510; role captured | Recorded as-stated | Evidentiary weight `→ A8` |
| EC-510 | Signer refuses to sign, takes freight anyway | Freight leaves custody with no POD | Driver logs the refusal itself | Requirement cannot force a signature; gap is recorded, not closed |
| EC-511 | Multi-stop load, one consignee refuses shared freight | `DELIVERY_REFUSED` at that stop only | A4 routes remaining stops | Cross-stop dependency `→ A4` |
| EC-512 | POD capture fails at the scene | No POD; blocked from `POD_CAPTURED` (BR-500) | System blocks progression | Fallback path unspecified — no tech prescribed |
| EC-513 | POD content inconsistent with location/transit record | Flagged per BR-513 linkage check | A8 investigates | Detection threshold/consequence `→ A8` |
| EC-514 | Unattended delivery, no signature taken | Custody notionally transferred, no POD; high-risk gap | Should not be permitted per BR-500 | Whether platform can technically prevent it is operational, not systemic |
| EC-515 | Consignee disputes the signature is theirs later | POD stands as captured (BR-512); dispute is claim-time | A8 | Identity-verification standard deliberately unset — a Boss/counsel question |
| EC-516 | Facility requires a lumper; carrier disputes fee | Lumper event captured (BR-516); fee dispute is a charge question | A6 | Fee-liability rule `→ A6` |
| EC-517 | Detention accrues from slow consignee unloading | Arrival/departure captured (BR-515); fault not attributed here | A4 classification, A6 charge | Fault-attribution rule `→ A4/A6` |
| EC-518 | Reconsignment requested at the dock | Not a delivery event; treated as a new instruction | A1/A4 | Whether permitted mid-trip `→ A1/A4` |
| EC-519 | Temp-sensitive/hazmat freight, consignee lacks receiving equipment | Refusal/exception path per BR-506/503 applies | Driver logs; A2 defines equipment/class rules | Pre-screening consignee capability `[NEEDS INPUT]` |
| EC-520 | Signer/facility is a third-party forwarder, not the named consignee | Accepted per BR-510; identity mismatch flagged | Recorded; A8 weighs at claim time | Should mismatch block POD capture `[NEEDS INPUT]` |

## Out of scope for A5

Transit-stage events and reroute (A4); Carmack liability allocation, claim adjudication, fraud
penalties (A8); invoice amount, charge lines, factoring (A6); regulatory citation depth and privacy
mechanics (A7); pickup-stage BOL creation and freight declaration (A1); consignee's formal RACI
placement (A9).
