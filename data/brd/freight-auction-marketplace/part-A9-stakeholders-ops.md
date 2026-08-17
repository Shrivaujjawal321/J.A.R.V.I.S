# Part A9 — Stakeholders, Roles & Permissions, Platform Operations

**Freight Auction Marketplace (US Domestic Truckload) — Agent A9 · ID block 900-999 · Spine rev. 2 (2026-07-29)**

**Owns:** stakeholder map & RACI · roles/permissions as a business model · platform operations & exception desk · support model · notification matrix · staffing implications.
**References, does not restate:** eligibility criteria (A2), auction/bid mechanics (A3), custody execution (A4), delivery/POD content (A5), payment mechanics (A6), regulatory citation (A7), liability adjudication (A8), business model/unit economics (A10).

---

## 9.1 Stakeholder Map

Three roles were supplied (spine §1). At least eight are actually in the room, and the split matters because interest and influence run in opposite directions for the party who matters most at the point of failure. The mechanism (spine §4) is explicitly built to compress the carrier's price; the consignee inherits whatever that compression produces — a re-traded pickup, a rushed driver, a damaged pallet — and holds no seat at all.

| Stakeholder | Signs up? | Primary interest | Influence over outcome | Conflict / note |
|---|---|---|---|---|
| **Shipper** | Yes | Lowest cost, on-time, low claims | High — sets terms, runs the auction | Captures the price benefit the mechanism produces but does not fully bear the service-quality risk that comes with it |
| **Carrier — asset-holder** | Yes | Win at a price that covers cost, get paid on time | Medium — bids into a price war it doesn't set | The mechanism structurally pressures its margin; the carrier most willing to underbid is not necessarily the most capable (spine §4, winner's curse) |
| **Carrier — broker/agent** | Yes | Same, plus margin on re-brokered capacity | Medium | Its bid may not represent a truck it controls — the direct driver of double-brokering risk (→ A2, A8) |
| **Dispatcher** | Via carrier account, not independently | Book efficiently for a fleet it represents — often several trucks | Medium; de facto decision-maker for small/mid carriers | Frequently the *only* real point of contact on the carrier side; not itself a licensed or account-holding entity — a business-model gap, not an edge case |
| **Driver** | Rarely, directly | Get paid, run legal HOS, not be blamed for exceptions not of their making | Low formally, absolute in practice at both custody handovers | Bound by the account's bid/award decisions with no platform authority of their own; the person actually present when a claim-deciding signature happens |
| **Factoring company** | No | Be paid instead of the carrier once a Notice of Assignment is filed | Low platform-facing, high financially | Legally entitled to redirect payment (→ A6); a role model that only has "carrier gets paid" cannot represent it |
| **Receiver / Consignee** | **No** | Correct, undamaged, on-time freight; accurate paperwork | **None, formally** | Holds the clear-vs-exception signature that a Carmack claim lives or dies on, can refuse freight, absorbs every downstream failure — and agreed to none of the auction, the carrier choice, or the price |
| **Dock / receiving staff** | No | Get the truck unloaded and off the dock | None, formally | Often not the same legal person as "the consignee" (a third-party DC, a night-shift employee) — the hand that signs is frequently not the party with a stake in the outcome |
| **Shipper's own customer** | No | The freight arrives | None | `[ASSUMPTION: in the common case the consignee IS the shipper's customer, but a third-party DC / cross-dock pattern is also plausible and changes who should be contacted | conf: med]` |
| **Insurer (cargo / auto liability)** | No — has a policy relationship with carrier/broker, not the platform | Loss ratio; only valid claims paid | Low day-to-day, decisive at claim time | Its coverage terms bound what the platform can promise a claimant (→ A8) |
| **Claims adjuster** | No | Adjudicate to policy terms | Medium, at claim time only | Can reach a conclusion in tension with the platform's own claims desk — role split unresolved, see 9.4 |
| **Platform / Operator (the client)** | n/a | The marketplace runs, is trusted, is lawful | Total — writes every rule | May itself carry broker liability (spine §0) — unresolved and blocking |
| **Platform Ops staff** | Employed by operator, not a marketplace "user" | Keep the marketplace operating | High, operational, invisible in a software-only model | The function §9.4 describes in full |

---

## 9.2 Governance — Who at the Client Signs Off

The sponsor of this BRD's authorship is Boss; the sponsor of the *platform* is the client (classification.md). Those are not the same accountable party, and the exemplar RACI convention (named person, per anti-patterns.md #6) cannot be honored here without inventing names. Every "Accountable" cell below is a blocking gap, not a formatting placeholder.

| Governance decision | Accountable (client-side) | Consulted | Informed |
|---|---|---|---|
| Business requirements sign-off (this BRD) | `[NEEDS INPUT: named client business sponsor + title]` | Boss (author), client platform-ops lead `[NEEDS INPUT]` | All ten agent domain owners |
| UAT acceptance | `[NEEDS INPUT: named client UAT owner]` | Client legal/compliance `[NEEDS INPUT]` | Boss |
| Does the client hold, or intend to obtain, FMCSA broker authority (spine §0) | `[NEEDS INPUT — highest-value open question in the entire document]` | Client counsel | A2, A3, A7, A8 — every area touching selection or liability |
| Accept lowest-bid-only vs. a qualified alternative (spine §4; A3 supplies the option set) | `[NEEDS INPUT: who at the client owns acceptance of negligent-selection risk]` | Client risk/legal | A2, A3, A7, A8 |
| State privacy compliance posture (CCPA/CPRA and peer statutes) | `[NEEDS INPUT]` | Client counsel | A7 |
| Claims-desk vs. insurer-adjuster authority split (9.1, 9.4) | `[NEEDS INPUT]` | Client operations, carrier's/broker's insurer | A8 |

---

## 9.3 Roles & Permissions as a Business Model

**A carrier with several trucks, a dispatcher, and multiple drivers is the normal case, not an advanced one — so is a shipper with several sites and several people posting loads.** The role model must be built for that from day one.

**9.3.1 Carrier-side account structure**

| Role | Default authority | Note |
|---|---|---|
| Account owner (holder of FMCSA authority) | All: bid, accept award, manage drivers/trucks/equipment, control payee-of-record, grant/revoke sub-permissions | The legally accountable entity |
| Dispatcher | Bidding by default if granted; **accept-award only if separately granted** (BR-902) | Not a licensed entity of its own; represents the account, doesn't own it |
| Driver | Executes pickup/transit/drop; POD signature treated as carrier-binding (BR-903); may hold no platform login at all | Distinct legal person — own HOS/CDL record lives with A2, not here |

**9.3.2 Shipper-side account structure**

| Role | Default authority | Note |
|---|---|---|
| Account admin | All: manage sites/users, cancel any load on the account, own invoice disputes | |
| Site/location poster | Publish loads for their site; cannot cancel another poster's load without an admin grant (BR-904) | Normal case, multi-site shippers |
| Billing/finance contact | Views and disputes invoices (→ A6) | Frequently a different person from the poster |

**9.3.3 Cross-cutting authority matrix**

| Action | Who may do it | Requirement |
|---|---|---|
| Publish a load | Shipper poster or admin | BR-901 |
| Bid on a load | Carrier account owner, or a bid-permitted dispatcher | BR-900 |
| **Accept an award** (creates a binding rate confirmation) | Carrier account owner, or a user *separately* granted accept-award authority | BR-902 |
| **Sign a POD** | The driver physically present at drop; the signature binds the carrier account that holds the award | BR-903 |
| Cancel a shipment (shipper side) | Original poster or shipper account admin | BR-904 |
| Decline/cancel an accepted award (carrier side) | Same authority tier as accept-award | BR-905 |
| Raise a claim | Shipper, or platform ops relaying a consignee-observed exception the consignee has no account to enter directly | BR-906 |
| Settle a claim or waive a charge | A platform-ops role only — never the transacting shipper or carrier acting alone | BR-907 |
| Approve a carrier onto the platform | A platform-ops role; a human decision point, not a fully automated pass | BR-908 |
| Change payee-of-record (factoring redirect) | Carrier account owner only, never a dispatcher | BR-909 |

### Requirements

| ID | Requirement | Traces to | Priority | Source | Acceptance |
|---|---|---|---|---|---|
| BR-900 | The platform shall support one carrier account representing multiple trucks and multiple drivers, with one or more dispatcher users holding individually grantable permissions distinct from the account owner. | OBJ-003, OBJ-006 | Must | Derived (spine §1/§2 + Boss's "asset trucks") | Given a carrier account with 3 trucks and 2 dispatchers, when the owner grants "bid" to Dispatcher A only, then Dispatcher B cannot submit a bid on that account's behalf. |
| BR-901 | The platform shall support one shipper account representing multiple sites/locations and multiple authorized posting users. | OBJ-002 | Must | Derived | Given a shipper account with 2 site posters, when Poster A publishes a load, then Poster B can view it but cannot edit or cancel it without an admin grant. |
| BR-902 | Accepting an award shall require a permission distinct from bidding, held by the account owner or an explicitly granted user. | OBJ-006, OBJ-007 | Must | Derived from spine §4's negligent-selection collision + carrier org reality | Given a dispatcher holds bid-only permission, when they attempt to accept an award, then the system rejects the action. |
| BR-903 | A driver's signature at delivery shall be treated as binding on the carrier account holding the award, regardless of whether the driver holds an individual platform login. | OBJ-004 | Must | `[ASSUMPTION: driver signature = carrier-binding is the accepted freight-industry convention | conf: high]` | Given a driver without platform credentials signs a delivery receipt, when POD is captured, then it is recorded against the carrier account, not against an unlinked individual. |
| BR-904 | Shipment cancellation shall be restricted to the original poster or a shipper-account admin. | OBJ-001 | Must | Derived | → A1 owns cancellation consequences; this BR covers authority only. |
| BR-905 | Declining or cancelling an accepted award shall require the same authority tier as accepting it (BR-902). | OBJ-006 | Must | Derived | → A3 owns the resulting state (`AWARD_DECLINED`); this BR covers who may trigger it. |
| BR-906 | The platform shall provide a path for consignee-observed exception information (damage, shortage) to enter the claim record without requiring a consignee account — via driver exception notation, dock contact, or shipper relay. | OBJ-004, OBJ-006 | Must | Derived from spine §0 (Carmack) + §1 (no consignee signup) | `[NEEDS INPUT: does the client want a lightweight, account-free consignee input link, or purely relay-through-shipper?]` |
| BR-907 | Waiving a charge or approving a claim payout shall require a platform-ops role distinct from any shipper, carrier, or dispatcher role. | OBJ-005, OBJ-006 | Must | Derived | Given a carrier requests a charge waiver on its own invoice, when the request is processed, then approval requires a platform-ops actor, logged separately from the requester. |
| BR-908 | Approving a carrier onto the platform (applied → eligible-to-bid) shall require action by a platform-ops role; it shall not be a fully automated pass even where every data check clears. | OBJ-006, OBJ-007 | Must | `[ASSUMPTION: a documented human review step is part of the negligent-selection defense named in spine §0 | conf: med]` | Given a new carrier passes every automated vetting check (→ A2), when onboarding completes, then the account remains non-bidding until a platform-ops actor records an explicit approval. |
| BR-909 | The platform shall represent a "payee of record" attribute on a carrier account, distinct from the carrier itself, settable only by the carrier account owner, to reflect a Notice of Assignment on file. | OBJ-005 | Must | Derived; → A6 owns payment mechanics, A9 owns change-authority | Given a dispatcher attempts to change payee-of-record, when submitted, then the system rejects it. |
| BR-910 | The platform shall be able to represent which specific driver and truck are executing an awarded load, distinct from which carrier account won it. | OBJ-004 | Must | Derived; → A2/A4 own the operational record | Given an award is accepted, when a driver/truck is assigned, then HOS, custody, and POD-signing responsibility trace to that individual driver record. |
| BR-911 | Where a shipper account has multiple posting users, state-change notifications for a load shall route to the specific user who posted it, not to a generic account inbox only. | OBJ-002 | Should | Derived | Given Poster A publishes a load, when it is awarded, then Poster A (not only the account admin) is notified. |
| BR-912 | Notifications addressed to the consignee shall be delivered through a contact channel supplied at load creation, not through an in-app mechanism, and the platform shall record that delivery/read confirmation is unavailable for this channel. | OBJ-004, OBJ-006 | Must | Derived, spine §1 "does not sign up" | Given a consignee contact is supplied at load creation, when a pickup or exception notification fires, then it is sent out-of-band and the record shows "delivery status unknown," not a false confirmed-read state. |
| BR-913 | Every exception state enumerated in spine §3 shall resolve to a defined platform-ops role accountable for it. | OBJ-006 | Must | Boss's mandate (spine §3, "nothing may be missed") extended to operations | See §9.4 table — every row has a "who" column populated or flagged `[NEEDS INPUT]`. |
| BR-914 | Driver-facing support shall be available in both English and Spanish at minimum. | OBJ-004, OBJ-006 | Must | `[ASSUMPTION: Spanish is the highest-priority second language across the US truckload driver workforce | conf: high, no cited percentage — confirm with client]` | Given a driver requests support in Spanish, when contact is made, then resolution proceeds without requiring the driver to switch to English. |

---

## 9.4 Platform Operations — the Desk Behind the Software

Every exception state in spine §3 lands on a human. A model that specifies the software states and not the operational function reading them describes something that cannot run.

| Function | Triggered by | What the function does | Note |
|---|---|---|---|
| Carrier vetting / onboarding review | New carrier application | Confirms FMCSA authority, insurance, safety data before approval (BR-908); criteria owned by A2 | Cannot be zero-touch given the negligent-selection exposure named in spine §0 |
| Continuous re-verification | Ongoing — insurance lapse, authority revocation, safety-score change | Monitors active carriers against FMCSA data sources; must be able to suspend bid/award eligibility mid-cycle | A carrier eligible at award time can become ineligible before pickup — a real timing gap (EC-905) |
| Exception desk | `SHIPPER_NOT_READY`, `CARRIER_NO_SHOW`, `PICKUP_REFUSED`, `TRANSIT_EXCEPTION`, `DELIVERY_REFUSED`, `PARTIAL_DELIVERY`/`OS&D`, `RETURN_TO_ORIGIN` (spine §3) | Real-time triage: contacts shipper/carrier/driver, decides reroute vs. RTO vs. escalate, feeds outcomes back to A4/A5 process | These fire whenever freight moves — nights, weekends, holidays; a business-hours-only model leaves the highest-risk hours uncovered |
| Claims intake | `CLAIM_OPEN`, `DAMAGED`/`LOST`/`PILFERED` | Receives the report — including a consignee-observed one relayed per BR-906 — assembles the BOL exception record, hands to A8's adjudication and/or the insurer's adjuster | Two possible adjudicators (9.1); role split `[NEEDS INPUT]` |
| Fraud review | Double-brokering flags, identity-theft signals, fictitious-pickup pattern (detection logic → A2, A8) | Human review of flagged accounts/loads, potentially while freight is already in motion | Highest-consequence desk given spine §0's fraud framing (EC-906) |
| Dispute-resolution ops | `DISPUTED`, `CLOSED_UNRESOLVED` | Operates the process A8 defines; is not itself the adjudication authority | |
| Collections | Non-payment beyond agreed terms (→ A6) | Follow-up function; interacts with payee-of-record (BR-909) | |
| After-hours coverage | Any of the above, outside business hours | Freight picks up, transits, and breaks down nights, weekends, and holidays | No coverage model, staffing size, or SLA is specified here — that is a client operating decision this BRD cannot invent numbers for (hard rule §7.1) |

`RSK-900` | Risk that a dispatcher accepts an award beyond authority granted internally by the carrier, creating a rate confirmation the carrier later disputes | Mitigation: BR-902's explicit permission requirement, plus a carrier-visible audit log of who accepted what | Owner: platform (design); residual agency risk inside the carrier's own org is not the platform's to police.

`RSK-901` | Risk that platform-ops function is understaffed relative to 24/7 freight movement, leaving exception states unresolved overnight | No number is asserted; qualitative risk only | Owner: `[NEEDS INPUT: client operations lead]`.

`DEP-900` | Platform-ops staffing plan and after-hours coverage model | Owner: client, not resolvable inside this BRD | `[NEEDS INPUT]`.

---

## 9.5 Notification Matrix

| State change (spine §3) | Notified | Told what | Channel note |
|---|---|---|---|
| `PUBLISHED` | Eligible carriers (per A2/A3 matching) | New load available to bid | In-app |
| `AUCTION_CLOSED` / `AWARDED` | Shipper; winning carrier; losing bidders | Outcome; losers told the load is no longer open | In-app |
| `AWARD_ACCEPTED` / `AWARD_DECLINED` | Shipper | Confirmed carrier, or that the award lapsed and re-auction is needed | In-app |
| `PICKUP_SCHEDULED` | Shipper, carrier, driver, **and consignee via out-of-band contact (BR-912)** | Pickup window; downstream delivery ETA if calculable | Consignee has no account |
| `CARRIER_NO_SHOW` / `SHIPPER_NOT_READY` / `PICKUP_REFUSED` | Shipper, carrier, exception desk | The exception and the next step being taken | |
| `PICKED_UP` / `IN_TRANSIT` | Shipper; consignee (ETA) via out-of-band contact | Custody confirmed; in-transit status | |
| `TRANSIT_EXCEPTION` | Shipper, consignee (ETA impact), exception desk | Nature of exception; revised ETA if known | |
| `AT_DROP` / `DELIVERED` / `POD_CAPTURED` | Shipper | Delivery confirmed, clear vs. exception notation | Consignee was physically present — no separate notification needed |
| `DELIVERY_REFUSED` / `PARTIAL_DELIVERY` / `OS&D` | Shipper, carrier, exception + claims desk | Nature of shortfall, next step | |
| `INVOICE_ISSUED` / `INVOICE_FINALISED` | Shipper (payer); carrier or its payee-of-record (BR-909) | Invoice content (→ A6) | |
| `CLAIM_OPEN` / `DISPUTED` | Shipper, carrier, claims desk, insurer's adjuster where applicable | Claim status | |
| `SETTLED` / `COMPLETED` | Shipper, carrier | Final confirmation | |

**Honest note:** the consignee receives operational notifications it needs to do its job (pickup window, ETA, exceptions affecting arrival) through a contact channel, never through platform-of-record notices about bids, awards, or invoices — because it has no account to receive them into. No requirement in this document should be read as implying otherwise.

---

## 9.6 Support Model

Users on this platform include drivers on the road, mid-shift, under Hours-of-Service pressure, frequently unable to read or type safely while moving. Support that assumes a desk worker's attention span and full keyboard access will fail exactly the population most likely to need it during an active exception (breakdown, refusal, accident). BR-914 states the requirement for English-and-Spanish support; this document deliberately does not choose a channel technology (phone, SMS, in-app chat, or otherwise) — that is a solution decision, not a business requirement.

`NFR-900` | Category: Accessibility/Usability | Requirement: driver-facing support must not require sustained reading or typing while the vehicle is in motion, consistent with distracted-driving norms | Target: qualitative, business-level — no channel prescribed | Measurement: support-flow review against the requirement at design time.

`NFR-901` | Category: Security / Auditability | Requirement: every permission grant or revocation (bid, accept-award, claim-waiver, payee-of-record change) is logged with actor, timestamp, and account | Target: 100% of grant/revoke events logged, retained for a period sufficient to support a Carmack claim/suit-limitation window (exact period → A7) | Measurement: audit-log completeness review.

---

## Edge Case Register

| EC-ID | Trigger | What happens | Who decides | Unresolved |
|---|---|---|---|---|
| EC-900 | Dispatcher accepts an award beyond authority granted internally by the carrier | A binding rate confirmation exists platform-side; carrier disputes internally | Platform enforces BR-902; internal carrier authority isn't the platform's to police | Whether the platform bears exposure for correctly honoring a permission the carrier misused internally |
| EC-901 | Two posting users at one shipper account publish overlapping loads for the same physical freight | Two live auctions exist for one shipment | Shipper-account admin, once caught | Platform has no independent way to detect duplicate freight without shipper self-report |
| EC-902 | Driver signs POD without verified linkage to the account holding the award (BR-910 not yet resolved) | POD is captured from an unverified individual | Treated as carrier-binding by convention (BR-903) | Whether driver-load linkage should be required *before* a POD signature is accepted as binding |
| EC-903 | Factoring company files a Notice of Assignment after an invoice has already issued to the carrier directly | Two parties both have a claim to the same payment | → A6 for mechanics; A9 flags payee-of-record authority (BR-909) must exist before, not after | Retroactive correction process undefined |
| EC-904 | Dock staff refuses to sign anything at delivery | No POD exists | → A5 owns delivery execution | Whether "refused to sign" becomes its own captured exception state |
| EC-905 | Carrier's insurance lapses mid-trip, after award, before delivery | Carrier is technically ineligible while freight is in its custody | Re-verification desk (9.4) | No clean action exists — freight already in transit cannot be un-shipped |
| EC-906 | Fraud review flags an already-awarded carrier while the load is physically in motion | Freight is in the custody of a party the platform now distrusts | Fraud review desk | No defined response short of recovery/law enforcement, outside platform authority |
| EC-907 | An exception occurs at `AT_PICKUP` or `AT_DROP` outside staffed hours | No human is available to triage in real time | Client operating decision (RSK-901) | After-hours coverage model is `[NEEDS INPUT]` |
| EC-908 | Driver identity, account holder, and dispatcher are three different people, and something goes wrong | Unclear who the platform contacts first | Exception desk, using BR-910's linkage record | Escalation order across three parties is undefined |
| EC-909 | Insurer's claims adjuster and the platform's own claims desk reach different conclusions on the same claim | Conflicting outcomes reach shipper/carrier | `[NEEDS INPUT]` | Authority split (9.1, 9.4) is unresolved |
| EC-910 | Consignee is not the shipper's actual customer (third-party DC / cross-dock) | Exception contact may reach a party with no stake in resolving anything quickly | Shipper, at load creation, by supplying the correct contact | `[ASSUMPTION]` in 9.1 needs client confirmation of which pattern dominates |
| EC-911 | A small carrier's sole dispatcher is unreachable during an active exception | No one on the carrier side can respond | Exception desk escalates to account owner or driver directly | Whether the platform requires a secondary contact per carrier account is undecided |
| EC-912 | Exception occurs and the driver is Spanish-primary while the desk contact is English-only | Resolution delayed at the highest-risk moment (breakdown, refusal, accident) | Support model (9.6) | BR-914 states the requirement; implementation is open |

---

**What A9 cannot do without a real person in the room:** name the client-side approvers in 9.2, size the platform-ops function or its after-hours coverage (RSK-901, DEP-900), or resolve the claims-desk/insurer-adjuster authority split (EC-909) — these need the client's own org chart and risk appetite, not more drafting.
