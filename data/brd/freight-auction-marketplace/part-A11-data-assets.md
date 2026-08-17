# Part A11 — Platform Data Assets as Product Capability

**Scope:** convert Boss's US truck-data platform (`~/Documents/truck-intel`, PostGIS; DEC-LOCK-002)
into business requirements, judged capability-by-capability on merit. **Not here:** carrier
eligibility (A2), bid/award mechanics (A3), fulfilment events (A4), liability/fraud (A8), licensing
legal clearance (A12 — referenced only). **ID block: 1100-1199.**

---

## 11.0 What this asset actually is

Seven verified layers, counted from the live database (DEC-LOCK-002 table, reproduced there — not
repeated here to save budget). It is a **reference dataset**, not a live operational feed: bridges,
tunnels and truck-designated routes are structural facts that change slowly; diesel is a weekly
series; live events are a narrow, named subset of states. Nothing in this asset is a substitute for
a carrier's own safety record (A2/A7 own that), and nothing here is a rate quote. Every capability
below is judged against that standard, not against what would be nice if the data were more complete.

---

## 11.1 Capability assessment — merit, honestly

| # | Capability | Problem it addresses | Strengthens | Cannot do | Verdict |
|---|---|---|---|---|---|
| 1 | Route feasibility at auction time | Load awarded to equipment that cannot lawfully run the lane (bridge weight/clearance, hazmat tunnel ban) | A3's award record (BR-303); OBJ-004/006 | Confirm permit-based exceptions; cover the last mile off the designated network; guarantee attribute completeness per record | **Strong** — closest layer to national government-source coverage (NTAD/FHWA) |
| 2 | Fuel-cost floor / below-cost signal | A3's RSK-301/303 — winner's curse, post-award re-trade | A3 selection record | Price wage, insurance, maintenance, tolls, deadhead, detention — i.e. is **not** a cost-recovery floor | **Moderate** — real signal, badly named if oversold |
| 3 | Breakdown recovery (mechanic layer) | A4's mid-trip failure with freight loaded | A4 §6 reassignment path | Confirm a shop is open, has capacity, or services heavy trucks; 11,759 shops is not uniform US coverage | **Moderate** — shortens search, doesn't solve the problem |
| 4 | HOS-aware transit planning / parking | US truck-parking scarcity interacting with HOS | A4 §5 transit visibility | Confirm live occupancy — 1,915 parking + 5,452 rest-area rows are static site lists, not availability | **Weak-moderate** — advisory only, say so explicitly |
| 5 | ETA credibility (work zones, weather, chain controls) | A4 TRANSIT_EXCEPTION credibility; shipper-visible delay explanation | A4 BR-401/405 | Claim national coverage — work zones cover 4 states (AZ/KS/MN/WA), chain controls are CA-only; NWS weather is the only near-national layer | **Moderate, geographically bounded** |
| 6 | Detention/dwell evidence | A6 billable events; A5 delivery-side facts | — | Nothing in this asset generates a custody timestamp | **Reject as a standalone capability** — see §11.4 |
| 7 | Disintermediation answer | A10's leakage-is-the-base-case finding | — | Hold a matched pair on the platform for the *next* load | **Reject the "hold" framing** — see §11.3 |

---

## 11.2 Business requirements

> **BR-1100** | **Must Have** | **Traces: OBJ-004, OBJ-006** | **Source: DEC-LOCK-002; derived**
>
> Before an auction opens, or at latest before award, the platform shall determine whether a lawful
> truck-designated route exists between origin and destination for the equipment type declared on the
> load, and shall flag any bridge or tunnel on the most direct such route whose recorded clearance,
> weight limit, or hazmat restriction conflicts with the load as declared.
> *Acceptance: every load carries a route-feasibility state — PASS, FLAG (with the specific record and
> restriction cited), or UNKNOWN — before award; UNKNOWN is a valid, visible state, never silently
> defaulted to PASS. Not in scope: permit-based exceptions to a posted limit; routing beyond the
> designated network (dock-to-highway last mile).*

> **BR-1103** | **Must Have** | **Traces: OBJ-001, OBJ-006** | **Source: DEC-LOCK-002; A3 RSK-301/303**
>
> At bid time, the platform shall compute a fuel-only cost estimate for the lane — truck-legal loaded
> mileage on the designated network, multiplied by a current diesel price for the corridor — and shall
> **flag, not block**, any bid at or below that estimate as *priced under fuel cost alone*, before
> award. Bid mechanics (whether a flagged bid can proceed) remain A3's.
> *Acceptance: every award record (A3 BR-303) carrying a flagged bid shows the flag and the estimate
> it was compared against. Not in scope: wage, insurance, maintenance, toll, deadhead, or detention
> cost — this estimate does not include them.*

| ID | Requirement | MoSCoW | Traces | Acceptance | Source |
|---|---|---|---|---|---|
| BR-1101 | Route-feasibility state (BR-1100) visible to a carrier **before** it bids, not only at award, so ineligible equipment self-selects out | Should | 001/003 | FLAG/PASS/UNKNOWN shown on the load listing pre-bid | → A3 BR-301 |
| BR-1102 | A FLAG state surfaces the specific restriction and the record it came from, not a bare fail | Should | 004/006 | Flagged loads cite the bridge/tunnel record and the limit exceeded | Derived, mirrors A3 BR-303's evidentiary standard |
| BR-1104 | The fuel-only estimate (BR-1103) is labelled and disclosed as fuel-cost-only; never presented as a full operating-cost floor or a savings/rate claim | Must | 006/007 | No surfaced copy implies total cost or guaranteed savings | Derived — anti-deceptive-claim guard |
| BR-1105 | Where an award proceeds on a bid flagged under BR-1103, the proceed decision is captured the same way any A3 override is — named party, reason | Should | 006 | No flagged-and-awarded bid lacks an override record | → A3 BR-306 |
| BR-1106 | On a `TRANSIT_EXCEPTION` (breakdown) event, the platform surfaces known repair-shop locations near the breakdown point, labelled as a directory — not a dispatch, not an availability guarantee | Should | 004 | Surfaced list cites source and an "unconfirmed availability" disclosure | → A4 §6 |
| BR-1107 | While `IN_TRANSIT`, a live work-zone, weather, or chain-control event intersecting the shipment's route, **within a covered feed's geography**, attaches to the shipment's status/exception record rather than surfacing only as a generic delay | Should | 002/004 | Attached events carry source feed + geography; absence outside covered geography is never shown as "route clear" | → A4 BR-401/405 |
| BR-1108 | Any parking or rest-area location surfaced to a driver/carrier carries an explicit disclosure that no live occupancy signal exists for it | Must | 006 | No parking suggestion appears without the disclosure | Anti-dark-pattern; FTC deceptive-practice avoidance |
| BR-1109 | Usage of data-asset features (1-5), per shipper-carrier pair, is tracked against A10's KPI-1012 (repeat/leakage cohort), to test — not assert — whether data-tool usage correlates with retained repeat business | Should | 003; cross A10 KPI-1012 | Leakage rate reported segmented by data-tool usage vs. not, on a defined cadence | Derived — converts §11.3 into a measured question |

---

## 11.3 The disintermediation question — skeptical, by instruction

A10 named five plausible holds against leakage — money, risk-transfer, vetting-as-service, volume,
contract — and flagged leakage as the base case if the client funds none (§3.5). Data assets are not
on that list, and I don't think they belong there as a sixth. A route-feasibility check, a fuel-cost
floor, a mechanic directory, a parking suggestion — each is cheap to reproduce **once**. A
shipper-carrier pair that has run a lane together learns, for free, that it's legal, roughly what it
costs in fuel, and where the truck breaks down — no repeat platform mediation required to keep that
value. This is session-level utility, not relationship-level lock-in. It also competes against
products that already publish this cheaply or free at scale: Trucker Path and DAT's Trucker Tools
crowdsource parking, fuel and repair data to millions of drivers; a mid-backfill personal database is
not going to out-cover them (§11.4). A10's own market finding cuts the same way: incumbent load
boards monetise data/tools by **subscription**, not by using them to hold a specific matched
transaction on-platform (§3.2).

**My read:** ship these as trust-and-efficiency features under OBJ-001/004/006, and measure it
(BR-1109). They are not a credible answer to A10's disintermediation question, and should not be
represented to Boss or a client as one.

---

## 11.4 Mandatory honesty — limits, and what I would cut

- **This is a personal-project database mid-backfill, not a production service.** No SLA, no uptime
  commitment, no support desk exists for it, and every requirement above silently assumes the pipeline
  stays maintained — that maintenance commitment is outside this BRD's scope entirely.
- **Coverage is uneven, and no percentage appears anywhere in this document** because none has been
  verified. 454,830 route rows and 629,710 bridge rows *sound* national — NTAD/FHWA is the closest
  thing the US has to national government coverage, which is why capability 1 is the strongest of the
  seven — but a government source is not the same claim as a complete one.
- **Freshness varies sharply by layer.** Structural data (bridges, tunnels, routes) changes slowly and
  is plausibly current for months; EIA diesel is a weekly series; live events are only as fresh as the
  last pull and cover a **named subset** of states (work zones: AZ/KS/MN/WA; chain controls: CA only).
  Treating that subset as national coverage would misrepresent the feature on every other lane.
- **A fuel-only floor is not a rate engine.** It prices one input and nothing else — no wage,
  insurance, maintenance, toll, deadhead reposition, or detention risk. Honestly described, it's a
  floor-on-a-floor: a bid below it cannot cover fuel alone (a real signal, RSK-301/303); a bid above it
  says nothing about whether the carrier can actually perform the load.
- **None of this substitutes for the FMCSA safety data A2's gate needs.** This asset has zero rows of
  carrier safety data. It cannot gate eligibility, cannot satisfy *Montgomery*'s documented-selection
  standard, and must never be represented to counsel or an insurer as part of the safety floor A2/A7
  own.
- **What I would cut.** Capability 6 (detention/dwell evidence) does not belong in this BRD — no layer
  here generates a custody timestamp, A4's BR-403 already owns arrival/departure capture
  independently, and the one honest connection (live-event context corroborating a stop) is already
  covered by BR-1107 under capability 5. A separate capability manufactures a link that isn't there.
  I'd also downgrade capability 7 from "hold" to "feature" — build it, measure it, don't sell it as the
  thing keeping a pair on-platform.

---

## 11.5 Risks, assumptions, dependencies

| ID | Item |
|---|---|
| RSK-1100 | Fuel-only floor mistaken (internally or by counsel) for a full cost/rate floor, informing a decision it can't support. P3 I4 |
| RSK-1101 | Route-feasibility false negative (an attribute simply absent from a record, not a real restriction) wrongly flags a legal load. P3 I3 → OBJ-002 |
| RSK-1102 | Source licensing unresolved (OSM share-alike; scraped/derived price feeds' terms) — a shipped feature may need pulling post-launch. P2 I4 → **A12** |
| RSK-1103 | Live-event coverage (4 states + CA) creates a false impression of national ETA/disruption coverage if not disclosed per-lane. P3 I3 |
| ASM-1100 | `[ASSUMPTION: bridge/tunnel records carry attribute-level clearance/weight/hazmat detail, not only location | conf: low]` `[NEEDS INPUT: confirm schema against the live database]` |
| ASM-1101 | `[ASSUMPTION: the 17,089-row diesel-price table is granular enough (state/corridor) to beat one national average for BR-1103 | conf: med]` `[NEEDS INPUT: confirm grain]` |
| DEP-1100 | → A2: route-feasibility state consumed alongside the eligibility tuple at bid/award, but is **not** part of A2's carrier-eligibility definition (lane-legality, not carrier fitness) |
| DEP-1101 | → A3: BR-1103's flag and BR-1105's override land inside A3's award/selection record (BR-303), not a separate one |
| DEP-1102 | → A4: BR-1106/1107 attach to A4's existing `TRANSIT_EXCEPTION` and status-update events; no new state machine |
| DEP-1103 | → A12: licensing review (RSK-1102) gates whether any OSM-derived layer ships commercially at all |

---

## 11.6 Edge case register

| ID | Trigger | What happens | Who decides | Unresolved |
|---|---|---|---|---|
| EC-1100 | Route record stale vs. a current permit/closure | Treated as advisory, not authoritative | Platform | Refresh cadence `[NEEDS INPUT]` |
| EC-1101 | Bridge/tunnel record has no hazmat field populated | Silence ≠ clear; must not read as PASS | Platform (ASM-1100) | Schema confirmation |
| EC-1102 | Diesel price lags a spot spike at bid time | Floor understates real fuel cost | Platform | Refresh cadence `[NEEDS INPUT]` |
| EC-1103 | Floor computed on zero-deadhead loaded miles | Legitimate bid includes reposition cost the floor never saw | Platform | BR-1104 disclosure carries this |
| EC-1104 | Carrier bids below floor for a legitimate reason (fuel contract, covered backhaul) | Flag ≠ proof of curse or fraud | A3 (award proceeds or not) | Override always logged (BR-1105) |
| EC-1105 | Zero mechanic shops within a useful radius of breakdown | Thin-coverage corridor, directory returns nothing | Carrier's own resources | No fallback defined |
| EC-1106 | Listed shop closed, or doesn't service heavy trucks despite tag | Directory is wrong; no verification step | Carrier discovers on call | BR-1106's disclosure exists for this |
| EC-1107 | Work-zone feed state outside AZ/KS/MN/WA | Corridor context silently absent, not "clear" | Platform | Must be disclosed, not just true |
| EC-1108 | NWS alert zone broader than the lane segment | Over-broad trigger, low signal-to-noise | Platform | Filtering rule `[NEEDS INPUT]` |
| EC-1109 | Chain-control data outside CA | Feature silently absent there | Platform | Same as EC-1107 |
| EC-1110 | Listed parking site full or closed | No live signal exists to know | Driver | BR-1108's disclosure exists for this |
| EC-1111 | A feasibility FLAG is wrong, shipper cancels a fine load | False-positive cost to OBJ-002 | Shipper | Appeal/override path `[NEEDS INPUT]` |
| EC-1112 | Carrier disputes a FLAG as incorrect | No resolution path defined | — | `[NEEDS INPUT]` |
| EC-1113 | A data source's licence prohibits commercial redistribution | Feature must be pulled post-launch | A12/counsel | `[NEEDS INPUT]` — RSK-1102 |
| EC-1114 | Asset backfill incomplete for a state at launch | Feature silently absent, not "checked, clear" there | Platform | Must be stated per-lane, not asserted globally |

---

**A11 limits.** Four things need a person, not more analysis: (1) the actual attribute schema behind
the bridge/tunnel counts — whether clearance, weight and hazmat fields exist per record or only
location (ASM-1100) is a database check Boss can run directly, not a research question; (2) counsel/A7
on whether a fuel-only floor logged in A3's selection record helps or hurts the *Montgomery* defence —
it could read as diligence, or as an admission the platform knew a bid was suspect and awarded anyway;
(3) licensing counsel on OSM/EIA/Overture terms before any layer ships commercially (→ A12); (4) a real
dispatcher's reaction to BR-1106 — whether a static shop directory is worth anything next to their own
phone list, or is noise.
