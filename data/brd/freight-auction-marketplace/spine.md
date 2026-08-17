# Spine — canonical model, ID allocation, and agent scope boundaries

**Authored by Jarvis (manager role) BEFORE any agent was dispatched.** This exists because a smoke
test run earlier today proved that fanning agents out without a shared skeleton produces orphaned
IDs, duplicated requirements, and an assumptions register that is incomplete by construction. Every
agent reads this file first and works inside it.

This spine is **canonical but contestable**. If an agent believes a state, entity or boundary here is
wrong, it must say so explicitly in a `CHALLENGE:` block rather than silently diverging. Divergence
without a challenge is the failure mode this file exists to prevent.

**Revision 2 (2026-07-29).** Jurisdiction corrected to **USA** on Boss's instruction. Three agent
challenges from revision 1 accepted and folded in: carrier split into asset-holder vs broker
(A2), invoice split into provisional vs final (A6), and `SHIPPER_NOT_READY` added as a state
distinct from `CARRIER_NO_SHOW` (A1).

---

## 0. Jurisdiction — USA. Read this before anything else.

The client is US-based and the system operates in the United States. **No India-law concept applies
anywhere in this document.** If you have background knowledge of Indian freight regulation, discard
it here — GST, e-way bills, consignment notes under the Carriage by Road Act, DPDP, and RBI payment
rules are all irrelevant and their appearance in output is an error.

The US regimes that actually govern this business, by area:

| Area | Governing reality |
|---|---|
| Who may arrange freight | FMCSA operating authority. **Motor carrier** and **property broker** are different authorities. Arranging transport for compensation between shipper and carrier is brokerage. |
| Broker obligations | 49 CFR Part 371 · **BMC-84 surety bond / BMC-85 trust fund** · **BOC-3** process agents · broker record-keeping and the parties' right to review the transaction record |
| Cargo loss & damage | **Carmack Amendment, 49 U.S.C. §14706** — the federal regime, with statutory minimum claim-filing and suit-limitation periods |
| The delivery document | **Bill of Lading**; delivery signed *clear* or *with exception*. "POD" here means a signed BOL / delivery receipt. |
| Carrier fitness | 49 CFR Part 387 financial responsibility · FMCSA SAFER / SMS / CSA data · operating-authority status and age |
| Driver | CDL · Hours of Service (49 CFR 395) and the ELD mandate · drug & alcohol testing and the FMCSA Clearinghouse |
| Broker's selection exposure | **Negligent selection / vicarious liability.** US plaintiffs sue the broker that chose the carrier. Selection criteria become evidence. |
| Fraud pressure | **Double brokering, carrier identity theft, fictitious pickup** — acute in this market and structurally drawn to price-only award |
| Money movement | State money transmission / MSB registration if funds are held · **freight factoring and Notices of Assignment** · W-9 and 1099-NEC |
| Privacy | **CCPA/CPRA and other state comprehensive privacy statutes.** No federal omnibus. Driver and consignee data in scope. |
| Competition | Sherman Act §1 — bid rigging on repeat lanes |

**The sharpest collision in this project:** Boss's design awards strictly to the **lowest bid**, and
US law exposes a broker to **negligent selection** claims based on *how it chose the carrier*. Those
two facts point in opposite directions. Every agent whose area touches selection, safety, liability
or auction rules must engage with this rather than route around it.

**Do not assume the client already holds broker authority.** Whether the client is a licensed broker,
a motor carrier, or a software vendor selling to licensed brokers is unresolved and is the highest-
value open question in the document. Treat it as `[NEEDS INPUT]`, never as settled.

---

## 1. Roles

| Role | Definition | Signs up? | Pays / is paid |
|---|---|---|---|
| **Shipper** | Owns the freight. Creates the shipment, runs the auction, wants it moved. | Yes | Pays (mechanism open) |
| **Carrier — asset-holder** | Holds FMCSA motor-carrier authority and operates the truck. | Yes | Is paid (mechanism open) |
| **Carrier — broker/agent** | Arranges capacity it does not own. **A distinct FMCSA authority.** Bidding by this party raises double-brokering questions. | Yes | Is paid (mechanism open) |
| **Receiver / Consignee** | Destination party. Takes delivery, signs the BOL. | **NO — does not sign up** | Neither, normally |
| **Platform / Operator (the client)** | Runs the marketplace, sets eligibility and auction rules, resolves disputes. **May itself be a regulated broker — unresolved.** | n/a | Revenue model open |
| **Driver** | Physically moves the truck. Often not the account holder. Distinct legal person with their own licensing and HOS constraints. | Open | Open |

**Do not flatten Receiver into Shipper.** The consignee is affected by every outcome, holds the
signature that closes the shipment and triggers the invoice, can refuse the freight — and never
agreed to anything. Their exception notation on the BOL is what makes or breaks a cargo claim. The
same applies to Driver vs Carrier: driver personal data, licensing and hours sit on a person who is
usually not the account holder.

**The asset-holder / broker split is load-bearing** (A2's challenge, accepted). A model where
"carrier = truck owner" cannot represent the party that actually books much of US truckload capacity,
and cannot detect double brokering — which is currently one of the most damaging frauds in this
market.

---

## 2. Core entities

`Shipper` · `Carrier (asset-holder)` · `Carrier (broker/agent)` · `Receiver/Consignee` · `Driver` ·
`Truck/Equipment (asset)` · `Shipment/Load` · `Freight` · `Auction` · `Bid` · `Award` ·
`Rate confirmation` · `Trip` · `Custody event` · `Bill of Lading` · `Delivery receipt (POD)` ·
`Invoice` · `Payment/Settlement` · `Claim` · `Dispute` · `Rating` ·
`Document` (operating authority, certificate of insurance, CDL, permits)

**Equipment is an asset with its own lifecycle and eligibility state** — type (dry van, reefer,
flatbed, step deck, tanker, power-only), capacity, current availability, and the insurance and
authority that cover it. A carrier is not eligible in the abstract; a *carrier-with-a-specific-
available-compliant-truck-and-a-legal-driver* is eligible for a *specific* load. A2 owns this.

---

## 3. Canonical shipment lifecycle (business states)

Boss's stated happy path, expanded. Happy path in bold.

```
DRAFT → **PUBLISHED** → **AUCTION_OPEN** → **AUCTION_CLOSED** → **AWARDED** → AWARD_ACCEPTED
      → PICKUP_SCHEDULED → AT_PICKUP → **PICKED_UP** → **IN_TRANSIT** → AT_DROP → **DELIVERED**
      → **POD_CAPTURED** → **INVOICE_ISSUED** → INVOICE_FINALISED → SETTLED → **COMPLETED**
```

`INVOICE_ISSUED` vs `INVOICE_FINALISED` (A6's challenge, accepted): an invoice can carry lines that
settle immediately alongside lines held pending a claim finding. One state could not hold both.

**Custody chain — liability follows custody:**
`Shipper holds` → *(handover at pickup)* → `Carrier holds` → *(handover at drop)* → `Consignee holds`

The two handover moments are the highest-risk events in the system. Condition, count, damage and
proof all concentrate there, and under Carmack the BOL notation at those moments is the evidence a
claim lives or dies on.

**Exception and terminal states (non-exhaustive — extend within your own area):**

| State | Enters from | Owning agent |
|---|---|---|
| `AUCTION_FAILED_NO_BIDS` | AUCTION_CLOSED | A3 |
| `AUCTION_FAILED_NO_ELIGIBLE_CARRIER` | AUCTION_OPEN | A2 / A3 |
| `AWARD_DECLINED` / `AWARD_LAPSED` | AWARDED | A3 |
| `CANCELLED_BY_SHIPPER` | any pre-pickup state, and post-pickup with consequences | A1 |
| `SHIPPER_NOT_READY` — freight not ready or origin unreachable | AT_PICKUP | A1 / A4 |
| `CARRIER_NO_SHOW` | PICKUP_SCHEDULED | A4 |
| `PICKUP_REFUSED` (freight differs from declaration, unsafe load) | AT_PICKUP | A4 |
| `TRANSIT_EXCEPTION` (breakdown, accident, HOS exhaustion, weather, closure, impound) | IN_TRANSIT | A4 |
| `DELIVERY_REFUSED` (full) | AT_DROP | A5 |
| `PARTIAL_DELIVERY` / `SHORT_DELIVERY` / `OS&D` | AT_DROP | A5 |
| `DAMAGED` / `LOST` / `PILFERED` | any custody state | A8 |
| `RETURN_TO_ORIGIN` | post-refusal | A4 / A5 |
| `CLAIM_OPEN` (Carmack) | DELIVERED onward, and earlier | A8 |
| `DISPUTED` | any state | A8 |
| `CLOSED_UNRESOLVED` | DISPUTED | A8 |

**Mandate:** every agent must enumerate the exception states *in its own area* exhaustively, in an
Edge Case register. Boss's instruction was explicit — nothing may be missed. A named, scored,
unresolved edge case is a success. A silently unconsidered one is the failure.

---

## 4. The contestable design commitment

Boss specified **lowest bid wins**. This is recorded as a supplied decision, not re-litigated as a
preference — but it is a strong commitment with documented failure modes, and in the US it also
carries a legal exposure. A BRD that absorbs it silently is negligent. It must appear as an explicit
decision with a rationale slot, and its consequences must be surfaced as requirements or risks:

- **Negligent selection exposure** — selecting on price alone, with safety data available and unused,
  is the fact pattern US plaintiffs' counsel look for after a serious accident
- Winner's curse → the winner may be the carrier who most underestimated the cost, which correlates
  with the carrier most likely to fail the load or re-trade the price at pickup
- Service-quality collapse under price-only competition
- Adverse selection → the cheapest bidder may be cheapest because of a deficiency that is not visible
- **Fraud attraction** → double brokering and fictitious pickup follow price-only award
- Collusion / bid rotation among repeat carriers on the same lane
- Shill or spoiler bidding

A3 owns the mechanism analysis and must present alternatives (lowest-bid-among-qualified, best-value
scoring, reserve price, second-price, assign-then-auction) **as options with trade-offs for Boss to
choose from** — not as a recommendation that overrides his stated design.

---

## 5. ID allocation — no collisions, no placeholders

Every agent uses **its own numeric block** for every prefix. Agent N owns `N×100` to `N×100+99`.

| Agent | Block |
|---|---|
| A1 | 100-199 |
| A2 | 200-299 |
| A3 | 300-399 |
| A4 | 400-499 |
| A5 | 500-599 |
| A6 | 600-699 |
| A7 | 700-799 |
| A8 | 800-899 |
| A9 | 900-999 |
| A10 | 1000-1099 |

Prefixes: `BR-` business requirement · `NFR-` non-functional · `CON-` constraint · `DEP-` dependency ·
`RSK-` risk · `ASM-` assumption · `EC-` edge case · `KPI-` metric · `DEC-` design decision.

**Objectives are pre-allocated here** so every agent can trace upward without guessing. Provisional;
A10 may refine wording, not IDs.

| ID | Provisional objective (all targets `[NEEDS INPUT]` — no numbers are invented) |
|---|---|
| OBJ-001 | Reduce the cost a shipper pays to move a load, versus their current allocation method |
| OBJ-002 | Reduce the time and effort to find and commit a carrier for a load |
| OBJ-003 | Raise carrier equipment utilisation by giving carriers access to load flow they cannot reach today |
| OBJ-004 | Make delivery verifiable — every load provably delivered, in a form that survives a cargo claim |
| OBJ-005 | Make the money flow correct and timely: right invoice, right party, right reporting, on time |
| OBJ-006 | Keep the platform trustworthy enough that strangers transact high-value freight on it, under active fraud pressure |
| OBJ-007 | Operate lawfully across the brokerage, transport-safety, and state privacy regimes the flow touches |

**Never invent a cross-block ID.** If your requirement depends on another agent's area, write
`→ A6 (invoicing)` in prose. The assembler resolves it. Do not write `BR-6xx` yourself.

---

## 6. Agent scope boundaries — who owns what, and what you must NOT write

Overlap is the enemy. If a topic is listed as another agent's, reference it and move on.

| Agent | Owns | Must NOT write |
|---|---|---|
| **A1 Shipper** | Shipper onboarding/credit, load creation & declaration, freight description, pickup/drop specification, shipper cancellation & consequences, shipper-side lifecycle | Auction rules (A3), pricing (A6) |
| **A2 Carrier & equipment** | Carrier onboarding & FMCSA vetting, authority/insurance/safety verification, equipment & driver records, **eligibility criteria and matching**, capacity, broker-vs-asset-holder distinction, double-brokering detection | Bid mechanics (A3), payouts (A6), fraud typology & penalties (A8) |
| **A3 Auction & bidding** | Auction lifecycle, bid rules, eligibility-gate application, award & tie-breaks, failure paths, anti-gaming, mechanism alternatives & trade-offs | Who is eligible (A2 defines), settlement (A6) |
| **A4 Fulfilment** | Pickup → transit → drop execution, custody handovers, tracking & visibility, transit exceptions, HOS/detention events, reroute, RTO | POD acceptance (A5), liability outcome (A8) |
| **A5 Receiver & POD** | Consignee rights, delivery execution, BOL/delivery-receipt capture & content, clear-vs-exception notation, refusal & partial acceptance, OS&D, proof-chain integrity | Transit ops (A4), claim adjudication (A8) |
| **A6 Money** | Charge model & accessorials, invoice generation & content, rate confirmation, settlement & payment terms, factoring/NOA handling, W-9/1099, platform revenue mechanics | Regulatory-regime analysis (A7), unit economics (A10) |
| **A7 Regulatory** | FMCSA authority & broker obligations, 49 CFR 371, bond/BOC-3, Part 387, HOS/ELD, CDL/Clearinghouse, hazmat, money-transmission trigger, CCPA/state privacy, antitrust surface | Tax/charge mechanics (A6), liability allocation (A8) |
| **A8 Liability & trust** | Carmack liability allocation, cargo loss/damage/theft, claims path, insurance structure, negligent-selection exposure, fraud typologies incl. double brokering, ratings, disputes, penalties | Regulatory citation (A7), auction mechanics (A3) |
| **A9 Stakeholders & ops** | Stakeholder map & RACI, roles/permissions model, platform ops & exception desk, support model, notification matrix, staffing implications | Business model (A10), domain flows (A1-A8) |
| **A10 Business model** | Problem statement & Five Whys, US market & competitive landscape, unit economics structure, liquidity/cold-start, KPIs, strategic risks, phasing | Operational requirements (A1-A9) |

---

## 7. Hard rules — identical for all ten agents

1. **Anti-fabrication.** If it was not in the intake, an answered question, or a cited source, it is
   an ASSUMPTION. Tag inline: `[ASSUMPTION: <statement> | conf: high/med/low]`. Where even an
   assumption is unsafe: `[NEEDS INPUT: <the exact question Boss must answer>]`. **A confident
   unsourced number is worse than a blank.** Never invent volumes, rates, thresholds, timelines,
   market sizes, bond amounts, insurance minimums, or percentages. Cite them or tag them.
2. **US only.** No India-law concepts. See §0.
3. **No solution language.** No tech stack, no database, no API, no screen layout, no vendor. State
   *what* outcome the business needs and *why*, verifiably. This is the model's default gradient —
   fight it actively.
4. **Every requirement:** stable ID from your block · MoSCoW tag · upward trace to an OBJ · a
   verifiable acceptance condition · a Source field (`Boss intake` / `derived` / `[ASSUMPTION]` /
   citation).
5. **Edge cases are the deliverable, not the appendix.** Boss's instruction: nothing may be missed.
   Every agent ends with an `EC-` register: trigger, what happens, who decides, what is unresolved.
   Dense table, not prose.
6. **Word budget: 2,000-2,500 words. Hard ceiling 2,500.** Tables count. Prose thin, tables rich.
   Write to length the first time — two agents in revision 1 burned their run drafting 4,200+ words
   and then rewriting. Plan the section, then write it once.
7. **Challenge, don't diverge.** Disagree with the spine in a `CHALLENGE:` block. Revision 2 accepted
   three such challenges — they work.
8. **Say what you cannot do.** Some things need a real carrier, a real shipper, a broker, or counsel
   in the room. Name them as such instead of asking three more questions to fake coverage.

---

## 8. Output

Each agent writes exactly one file:
`data/brd/freight-auction-marketplace/part-A<N>-<slug>.md`

§11 Assumptions Register and §1 Executive Summary are **assembler-owned**, not agent-owned — the
smoke test proved a parallel drafting agent cannot produce them correctly, because it can only see
its own tags. Do not write them.
