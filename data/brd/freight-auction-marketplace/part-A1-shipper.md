# Part A1 — Shipper Domain

**Scope:** shipper onboarding/credit standing, the load object and freight declaration, pickup/drop
specification, shipper-side lifecycle (publish commitment, amendment, cancellation, TONU, re-trade).
Not owned here: bid mechanics (A3), pricing/invoicing (A6), FMCSA/broker regulation (A7), carrier
eligibility (A2), consignee POD (A5), liability adjudication and ratings (A8).

## 1. Shipper onboarding & organisational model

| ID | Requirement | Pri | Traces | Acceptance | Source |
|---|---|---|---|---|---|
| BR-100 | Shipper registers as an **organisation** supporting multiple authorised users, not one login. | Must | OBJ-002 | Org has ≥1 user; adding users needs no re-registration. | derived |
| BR-101 | Org roles distinguish a **post-only user** from one authorised to cancel/amend. | Should | OBJ-002/006 | Post-only user's cancel/amend calls are rejected. | derived; RBAC detail → A9 |
| BR-102 | Every publish/amend/cancel action records the **named user** and timestamp. | Must | OBJ-006 | Each state transition has an attributable user ID. | derived |
| BR-103 | Org supports **multiple ship-from/ship-to sites**, independently selectable per load. | Must | OBJ-002 | 3-site shipper needs no separate accounts. | `[ASSUMPTION: shippers commonly multi-site \| conf: high]` |
| BR-104 | Org's legal identity (EIN or equivalent) is verified before first publish. | Must | OBJ-006/007 | Unverified org cannot reach PUBLISHED. | `[NEEDS INPUT: identity-check method]` |

## 2. Shipper credit standing

A carrier's dominant fear in brokered freight is non-payment; a lowest-bid auction sharpens it since
the winner has the thinnest margin to absorb a slow payer. Letting a shipper publish is an implicit
platform assertion about that shipper's ability to pay.

| ID | Requirement | Pri | Traces | Acceptance | Source |
|---|---|---|---|---|---|
| BR-105 | A **payment-standing check** gates first publish and re-verifies on a recurring cycle. | Must | OBJ-006 | Org has a dated standing record with a re-check schedule. | `[NEEDS INPUT: check standard]` |
| BR-106 | A **payment-reliability signal** (e.g. days-to-pay) is shown to bidders pre-bid, without raw financials. | Should | OBJ-006 | Auction view shows a standing indicator, no financial detail. | derived → A6/A9 |
| BR-107 | A shipper whose standing drops below threshold is **suspended from new publishes**; loads in flight are unaffected. | Must | OBJ-006 | Suspended org's publish blocked; open loads unchanged. | `[NEEDS INPUT: threshold]` |
| BR-108 | An org with an **open unresolved non-payment dispute** cannot publish. | Should | OBJ-006 | Publish rejected while dispute open. | derived → A8 |

## 3. The load object — freight declaration

The declared load is what every bid prices against. The dominant cause of post-award re-trade or
dock refusal in US truckload is under-declaration at publish. Comparability of bids depends on every
field below being mandatory, not optional.

| ID | Requirement | Pri | Traces | Acceptance | Source |
|---|---|---|---|---|---|
| BR-110 | Load cannot reach PUBLISHED without commodity, weight, equipment type, piece/pallet count, and both appointment windows. | Must | OBJ-001/002/004 | Publish blocked, missing field named. | Boss intake happy path |
| BR-111 | **Equipment type** is a closed set (dry van, reefer, flatbed, step deck, power-only, ≥). | Must | OBJ-001/002 | Publish rejects types outside the set. | `[ASSUMPTION: closed list not free text \| conf: high]` |
| BR-112 | Reefer loads require a mandatory **temperature range** (or ambient/protect-from-freeze). | Must | OBJ-001/004 | Reefer load without temp value cannot publish. | derived |
| BR-113 | Load requires declared **dimensions** sufficient for legal-load/equipment-fit checks. | Must | OBJ-001 | Publish blocked without dimensions where fit isn't self-evident. | derived |
| BR-114 | Load declares **live-load vs. drop-and-hook** (with a dock-time estimate for live) and **appointment type per stop** (FCFS vs. scheduled, with window). | Must | OBJ-001/002/004 | Both stops carry load type and explicit appointment type. | derived |
| BR-116 | Load declares **dock vs. ground access**, needed unload equipment (e.g. liftgate), and whether a **lumper is expected**, per stop. | Should | OBJ-001/004 | Access, equipment, lumper fields all visible per stop. | derived |
| BR-118 | Load flags **hazmat** and captures what a carrier needs to self-assess authority to haul it. | Must | OBJ-004/007 | Hazmat-flagged load blocks publish without sub-fields. | derived → A7 |
| BR-119 | Load flags **high-value/theft-attractive freight**, independent of hazmat. | Should | OBJ-006 | Flag settable independent of hazmat status. | derived → A2/A8 |
| BR-120 | **Weight** is a single mandatory numeric field, no default, no placeholder. | Must | OBJ-001 | Publish blocked if weight is blank, zero, or system-default. | derived |
| BR-121 | Publish flow states bids were priced against this declaration and that a material dock discrepancy carries consequences (§7-8); shipper must acknowledge. | Must | OBJ-001/006 | Acknowledgement required to complete publish. | derived — core anti-under-declaration control |
| BR-122 | The original declared load is retained **immutably**, even after later amendment. | Must | OBJ-006 | Pre-amendment version is retrievable, timestamped. | derived → A8 evidence |

**Who bears the cost of an under-declaration is out of this domain's scope** — A8 owns the allocation,
A4 owns the dock event (`PICKUP_REFUSED`). This domain owns only that the declaration is mandatory,
structured, and acknowledged (BR-121).

## 4. Pickup / drop specification

| ID | Requirement | Pri | Traces | Acceptance | Source |
|---|---|---|---|---|---|
| BR-125 | Load requires a full address, named on-site contact, and site hours at both stops. | Must | OBJ-002/004 | Publish blocked without resolvable address/contact per stop. | derived |
| BR-126 | Stop-specific instructions (dock #, gate code) are attachable, visible **only post-award**. | Should | OBJ-002 | Hidden pre-award; visible post-award. | `[ASSUMPTION: withheld to prevent lane-shopping \| conf: med]` |
| BR-127 | Release 1 supports **exactly one origin and one destination** per load. | Must | scope | Load cannot be created with >1 pickup or drop. | Boss intake gives single-lane path; see §10 |

## 5. Publishing a load — what it commits the shipper to

| ID | Requirement | Pri | Traces | Acceptance | Source |
|---|---|---|---|---|---|
| BR-130 | Publish is a binding commitment to make declared freight available, as declared, at the declared window, absent a §7 cancellation. | Must | OBJ-006 | Commitment statement shown and confirmed at publish. | derived |
| BR-131 | Publish commits the org to **honour the awarded rate** once accepted, outside the §6-7 paths. | Must | OBJ-001/006 | Accepted award cannot be unilaterally repriced by the shipper. | derived |
| BR-132 | A shipper cannot publish a **second load against the same declared freight** while one referencing it is open. | Should | OBJ-006 | Duplicate-freight publish blocked or flagged. | `[ASSUMPTION: platform can detect duplicate freight \| conf: low]` |
| BR-133 | Once PUBLISHED, auction timing/closure is entirely A3's; this domain does not own it. | Must | boundary | — | spine §6 |

## 6. Amendment after publish

Boss's happy path has no amendment step; every item below is derived from freight being physical and
time-sensitive.

| ID | Requirement | Pri | Traces | Acceptance | Source |
|---|---|---|---|---|---|
| BR-135 | Amendment allowed only in DRAFT / PUBLISHED-pre-bid; once ≥1 bid exists, direct field edits are blocked. | Must | OBJ-006 | Amend call on a load with ≥1 bid is rejected. | derived |
| BR-136 | A **material amendment** (weight beyond tolerance, equipment, commodity, hazmat status, either address) post-first-bid forces **withdraw-and-republish**, not in-place edit. | Must | OBJ-001/006 | Material-field amend attempt triggers withdraw path. | `[NEEDS INPUT: tolerance value]` |
| BR-137 | A **non-material amendment** (contact, dock instruction, gate code) is editable through AWARD_ACCEPTED without voiding the award. | Should | OBJ-002 | Non-material field edits succeed post-award. | derived |
| BR-138 | A BR-136 withdrawal after an award exists is logged under **§7's cancellation ladder**, not a free redo. | Must | OBJ-006 | Post-award withdrawal creates a cancellation record. | derived — closes a dodge path |
| BR-139 | Withdrawal notifies all bidders/awarded carrier **at the same moment** it takes effect. | Must | OBJ-002/006 | No party learns of it later than the shipper's action time. | derived → A3/A9 |

## 7. Cancellation ladder, including TONU

**CHALLENGE (accepted, spine rev.2):** a carrier turned away at origin has incurred a real cost
through no fault of its own — different from a no-show. `SHIPPER_NOT_READY` is now distinct from
`CARRIER_NO_SHOW`; the ladder below depends on it.

| Stage | Trigger | TONU claim? | Notes |
|---|---|---|---|
| Pre-award | Cancel before any award | No | No truck committed |
| Post-award, pre-dispatch | Cancel after AWARD_ACCEPTED, before dispatch | No — standing record attaches | Lane opportunity lost only |
| Post-dispatch, pre-arrival | Cancel after truck en route | **Yes** | Amount → A6 |
| At-dock (`SHIPPER_NOT_READY`) | Carrier arrives, freight/site not ready | **Yes** + detention | Distinct from `CARRIER_NO_SHOW` |
| Post-pickup | Attempted cancel after `PICKED_UP` | N/A | Becomes RTO (A4) / liability (A8) |

| ID | Requirement | Pri | Traces | Acceptance | Source |
|---|---|---|---|---|---|
| BR-140 | Pre-award cancel is free of consequence beyond removal from the auction. | Must | OBJ-006 | No standing record raised. | derived |
| BR-141 | Post-award pre-dispatch cancel records a standing event without a TONU claim. | Should | OBJ-006 | Standing shows cancel; no TONU line created. | derived |
| BR-142 | Post-dispatch cancel generates a **TONU-eligible claim** to A6, evidenced by dispatch fact. | Must | OBJ-006 | Claim record created on cancel after dispatch. | `[NEEDS INPUT: dispatch-proof standard]` |
| BR-143 | On-time carrier arrival against an unready shipper always enters `SHIPPER_NOT_READY`, generating TONU + detention claims, **never** `CARRIER_NO_SHOW`. | Must | OBJ-004/006 | State never mislabels shipper fault as carrier fault. | derived, spine rev.2 |
| BR-144 | Cancellation is unavailable once `PICKED_UP`; custody-holding freight is A4 (RTO) / A8 (liability) territory. | Must | boundary | Cancel action rejected post-`PICKED_UP`. | spine §3 |
| BR-145 | Standing record (BR-105/106) shows cancellations **by stage**, not one aggregate count. | Should | OBJ-006 | Carrier viewing standing sees stage-level breakdown. | derived |

## 8. Re-trade after award — shipper-side handling

Re-trade: carrier wins low, then demands more near pickup with no time left to re-auction. **A3 owns
preventing it on the bid side; this domain owns the shipper's entitlement when it happens.**

| ID | Requirement | Pri | Traces | Acceptance | Source |
|---|---|---|---|---|---|
| BR-150 | Shipper may **reject a post-award rate demand** and treat it as a carrier-side award failure, without triggering §7's ladder against itself. | Must | OBJ-001/006 | Rejected demand creates no shipper cancellation record. | derived → A3/A8 |
| BR-151 | If the shipper accepts a re-trade under time pressure, the change is recorded as an **exception to the original award**, not an overwrite. | Should | OBJ-006 | Both original award and accepted change remain visible. | derived |
| BR-152 | Every re-trade attempt is logged against the carrier, accepted or not. | Should | OBJ-006 | Demand is logged regardless of outcome. | derived → A2/A8 |

## 9. Declining the lowest bidder

Boss's design is strict lowest-bid-wins. Whether the shipper may decline that award on
safety/reliability grounds sits on the negligent-selection collision in spine §0/§4 — an
undocumented override is arguably worse claim evidence than no override at all. Flagged, not
resolved, here.

| ID | Requirement | Pri | Traces | Acceptance | Source |
|---|---|---|---|---|---|
| BR-155 | `[NEEDS INPUT]` Whether a shipper may decline an award to the lowest bidder, and on what basis, is undecided — a joint Boss/A3/A8 call. | Must | OBJ-006 | Resolved once decided upstream. | spine §4 |
| BR-156 | If a decline right is granted, it requires a **structured reason code** tied to objective carrier data already on file — not free-text override. | Should | OBJ-006/007 | Decline without a structured reason is rejected. | derived, conditional on BR-155 |

## 10. Explicitly out of scope for release 1

**Multi-stop loads, partial/LTL freight, and appointment-critical (hard-window, penalty-bearing)
loads are out of scope for release 1.** Boss's happy path is single-pickup, single-drop, full
truckload; nothing in the intake describes multiple stops, split freight, or window penalties. A
real US shipper book routinely includes all three — a **named, dated exclusion** in the assembler's
scope table, not a silent gap.

---

## Edge Case Register (A1)

| ID | Trigger | What happens | Who decides | Unresolved |
|---|---|---|---|---|
| EC-100 | Published field technically present but implausible (weight = 1) | `[NEEDS INPUT]` no sanity-check policy | Platform rule, undefined | Whether/what plausibility bounds exist |
| EC-101 | Same freight referenced by two open loads, same org | BR-132 flags should-block | A1/A9 | Detection mechanism unresolved |
| EC-103 | Declared vs. scale weight at pickup — small margin vs. large mismatch | Small: BR-121 notice, A8 allocates. Large: carrier refuses, `PICKUP_REFUSED` | A4 detects / A8 allocates | No tolerance band defined; evidence sufficiency of BR-122 record |
| EC-105 | Carrier dispatches, shipper cancels before arrival | TONU-eligible, BR-142 | A6 computes | Proof-of-dispatch standard undefined |
| EC-106 | Carrier on time; dock occupied, or site unreachable (locked gate/wrong address) | `SHIPPER_NOT_READY`, BR-143 | A4 state / A6 amount | Detention clock rule; shipper-fault vs. data-quality failure at publish |
| EC-108 | Awarded carrier demands more the night before pickup | Reject without penalty, BR-150 | A1 (shipper) / A3 (carrier consequence) | Repeat-offender auto-action — A2/A8 |
| EC-109 | Shipper accepts re-trade under time pressure | Exception to award, BR-151 | A1 | Should this ever be disallowed outright — Boss policy call |
| EC-110 | Shipper wants to decline lowest/only bidder, safety concern | `[NEEDS INPUT]`, BR-155 | Boss/A3/A8 jointly | Entire mechanism undecided |
| EC-111 | Material amendment needed after bidding started | Withdraw-and-republish, logged as cancel, BR-136/138 | A1 | "Material" tolerance not supplied |
| EC-112 | Shipper standing degrades mid-auction (post-publish, pre-award) | Not addressed — BR-107 only gates publish | A1/A6 | Should an in-flight auction be pulled |
| EC-114 | Shipper wants a multi-stop or partial-load shipment | Out of scope release 1 (§10) | Boss roadmap decision | Not designed this release |
| EC-115 | Freight later found hazmat, not flagged at publish | Declaration failure, same family as EC-103 | A4 detects / A7 exposure / A8 liability | Under-declaration or a distinct hazmat failure — cross-agent |
