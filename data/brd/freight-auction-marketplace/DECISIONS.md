# Decision log

## DEC-LOCK-003 — The platform IS the broker

**Decided by Boss, 2026-07-30.** Boss's words: *"client broker nhi h hamara system brocker h."*

**What was decided.** The client is not an existing licensed broker. **The platform itself performs
the brokerage** — it arranges transportation for compensation between shipper and carrier. This is
A6's model (b), A7's answer (B), and it resolves A8's `DEC-801`.

**The one clarification that matters.** FMCSA operating authority is issued to a **legal entity**, not
to software, and the surety bond is posted by an entity. So in practice: **the company that operates
this platform becomes a licensed property broker.** That entity holds the authority, posts the bond,
carries the record-keeping duty, and is the defendant when a claim is filed. "The system is the
broker" is the right description of what the product does; the obligations land on whoever runs it.

### What this closes

Five sections of the BRD were provisional pending this answer. All five now resolve:

| Was open | Now |
|---|---|
| A6 — who invoices whom | Platform invoices the shipper; platform pays the carrier separately. It is a principal on both sides, not a pass-through. |
| A7 — the client's regulatory posture | Property broker. OP-1 registration, **BMC-84 surety bond, $75,000** (see correction below), BOC-3 process agents. |
| A8 — the platform's legal position | Broker, not motor carrier, not software vendor. |
| A9 — who signs off | The operating entity is the sponsor, not a third-party client-of-a-client. |
| A10 — the revenue model | A **spread**, not a licence fee: the difference between the shipper rate and the carrier rate. A10's research puts incumbent broker gross margins around 13-16%, which caps the realistic take. |

### What this now obligates — none of it optional

> **CORRECTION — the bond amount is $75,000, not $150,000.** Jarvis told Boss $150,000 earlier in the
> session, sourced from trade reporting and from a comment position rather than from the regulation.
> The economics agent challenged the figure; Jarvis then read the CFR text directly:
> *"A broker must have a surety bond or trust fund of $75,000 in effect."*
> — [49 CFR § 387.307 (Cornell LII)](https://www.law.cornell.edu/cfr/text/49/387.307)
>
> What actually took effect on **16 January 2026** is the Broker Financial Responsibility rule's
> *compliance* provisions — assets readily available, immediate-suspension mechanics, eligible BMC-85
> trustees — **not an increase in the amount.** A late-February-2026 ANPRM floats $75k → $100k, which
> commits FMCSA to nothing. Budget **$75,000, with a $100,000 sensitivity.**
>
> **And the more important point, which the amount was distracting from:** the real 2026 change is
> that a bond drawdown can now **suspend the broker's operating authority on a short cure window.**
> In a business whose bond is drawn against by carrier non-payment claims, the exposure is not the
> premium — it is that a single unresolved carrier claim can stop the company from operating. That
> belongs in the risk register, not the cost line.

1. **49 CFR Part 371 record-keeping**, including each transacting party's right to review the record
   of their transaction. A marketplace that sets the price sits directly on this rule.
2. **Negligent selection lands on the platform.** After *Montgomery v. Caribe Transport II* (SCOTUS,
   14 May 2026, unanimous) the preemption defence is gone, and the platform is now the broker who
   chose the carrier. **This is why the eligibility gate (DEC-LOCK-001) stops being prudent design
   and becomes the defence itself**, and why the award's selection record — who was excluded and
   why — is evidence rather than logging.
3. **Working capital becomes a balance-sheet problem, not a feature.** Shippers pay on terms; carriers
   want money fast. As principal on both sides, the platform owns that gap. Every figure is still
   `[NEEDS INPUT]`, but the shape of the business is now a financed one.
4. **Factoring and Notices of Assignment become mandatory handling**, not an edge case — carriers will
   assign their receivable *against the platform*, and paying the carrier instead of its factor can
   mean paying twice.
5. **Contingent cargo and contingent auto-liability cover.** Under Carmack the motor carrier bears
   cargo liability, not the broker — but a broker that holds itself out as arranging carriage can be
   found to have acted as a carrier, and general-freight carriers are not federally required to carry
   cargo insurance at all (FMCSA removed that in 2011). The gap is real and it is the platform's.
6. **W-9 collection and 1099-NEC reporting** on carrier payments.

### One thing this makes *simpler*, worth stating

The money-transmitter question recedes. A platform that routes *other people's* money between two
parties raises state money-transmission and MSB licensing questions. A broker of record is moving
**its own** receivables and payables — it owes the carrier because it contracted with the carrier.
That is ordinary commercial credit, not money transmission. Confirm with counsel, but this reading
removes a licensing programme A6 and A7 had both flagged as a pre-launch cost.

### The spread is a mandatory, carrier-reviewable record — found 2026-07-30, verified verbatim

The regulatory agent surfaced this and Jarvis verified it directly against the CFR text. It is the
most consequential finding of this revision round, more so than the bond figure.

**49 CFR § 371.3** requires the per-transaction record to include *"the amount of compensation
received by the broker for the brokerage service performed and the name of the payer"* and *"the
amount of any freight charges collected by the broker and the date of payment to the carrier."*
It then provides: *"Each party to a brokered transaction has the right to review the record of the
transaction required to be kept by these rules."* Retention: three years.
— [49 CFR § 371.3 (Cornell LII)](https://www.law.cornell.edu/cfr/text/49/371.3)

**So the carrier has a federal right to ask what the platform made on their load.** This exists today,
independent of the long-pending transparency rulemaking. Waiver enforceability is unsettled.

**Why this matters beyond compliance — it collides with two other findings:**

| Agent | Position |
|---|---|
| R1 (money) | The shipper-facing invoice must be **all-in**, never itemising carrier cost versus platform fee — itemising it is one of the things that weakens the not-money-transmission reading. |
| R4 (economics) | Scored disintermediation risk down from 16 to 9, resting substantially on the spread being invisible: *"the shipper never sees `C_carrier`, the carrier never sees `P_shipper`."* |
| R2 (regulatory) | § 371.3 gives the carrier a reviewable right to exactly that figure. |

R1 and R2 can coexist — an all-in invoice plus a detailed record disclosed on request. **R4's argument
is the one that weakens.** The improvement in disintermediation resistance was partly built on the
spread being structurally hidden; it is hidden by default but not by right.

**The instruction that follows:** do not plan on spread opacity as a switching cost. A serious carrier
will ask, and the platform must answer. Whatever holds the transaction has to be something else —
coverage certainty, payment speed, or defensible vetting. Those are all things the platform can
actually deliver; secrecy is not one of them.

### Still open, and not answered by this

- The safety floor the eligibility gate actually applies (A2's `DEC-201`).
- Who funds the payment-terms gap, and on what terms.
- Q2 in `NEXT-STEPS.md` remains the most important unanswered question: **what is the platform
  actually being paid to fix?** Being the broker settles the *legal shape* of the business. It does
  not tell us why a shipper leaves their current broker for this one.

> **OPEN CONFLICT — needs a business decision, not a design one. Found 2026-07-30 by the shipper-flow
> design agent, which flagged it rather than choosing.**
>
> **Can a shipper cancel a load after the freight has been picked up?** The two documents contradict
> each other:
> - `BRD-v1.md` **BR-144** — cancellation is unavailable once the load reaches `PICKED_UP`.
> - `FRD-v1.md` — its own state adjacency permits `IN_TRANSIT → CANCELLED_BY_SHIPPER (charged)`, and
>   `EC-509` explicitly allows post-pickup, pre-delivery cancellation *with a financial consequence*.
>
> These cannot both be built. The real question is operational: **once a truck is loaded and moving,
> may the shipper recall it, and at what cost?** The permissive reading needs a charge model and a
> return-to-origin path (which is itself one of the six lifecycle states with no screen — see
> `DESIGN-GAPS.md`). The restrictive reading is simpler but means a shipper whose customer just
> cancelled has no route except letting the freight arrive somewhere nobody wants it.
>
> The design map followed the FRD reading so the flow could be completed, and marked it. Nothing is
> built on it yet.

Decisions Boss has actually made, with the reasoning that was in front of him. Anything not on this
list is still open and must stay tagged `[NEEDS INPUT]` in the BRD — do not promote an assumption to
a decision by writing it confidently.

---

## DEC-LOCK-001 — Award rule: lowest bid **within a carrier-eligibility gate**

**Decided by Boss, 2026-07-29.** Boss's words: *"isliye ham phle carrier eligibility bhi check
krenge. which is very important."*

**What was decided.** Carrier eligibility is checked **first**. The auction ranks on price **inside**
the qualified pool. Lowest bid still wins — but only among carriers that cleared the gate.

**What did NOT change.** The mechanism Boss designed is intact: price decides, ranking is mechanical,
there is no human discretion and no back-room selection. The gate sits *before* the auction, it does
not reach into it.

**Why.** Three agents working independently — A7 (regulatory), A8 (liability) and A10 (business
model) — converged on price-only award being the product's central weakness, for two separate
reasons:

1. **Legal.** *Montgomery v. Caribe Transport II, LLC*, No. 24-1238, 608 U.S. \_\_\_ (2026), decided
   14 May 2026, unanimous (Barrett, J.). The Supreme Court held a state-law negligent-hiring claim
   against a freight broker is not preempted by the FAAAA — it falls inside the safety exception. The
   broker was C.H. Robinson; the Seventh Circuit was reversed. The preemption defence that killed
   these claims at the pleading stage is gone nationwide. Verified independently by Jarvis against
   supremecourt.gov, Justia and Faegre Drinker, after three agents reported it.
   Under the old rule, price-only award was a risk to note. Under this one, the award record is the
   plaintiff's exhibit.
2. **Empirical.** Convoy — the best-funded attempt at exactly this business in the US, roughly $1.1B
   raised, shut down October 2023 — **never awarded on price alone.** Its instant-bidding algorithm
   weighted a carrier quality score (service level, on-time rate, app engagement) alongside price
   specifically so a strong carrier could win without being cheapest. Verified by Jarvis against
   FreightWaves, CCJ and Logistics Management. The operator with the most data in this category
   rejected price-only award while it was still well funded.

**Consequences to carry through the BRD.**
- A3's mechanism options must each carry the gate; "price-only across all comers" is no longer a
  neutral fork (A7's challenge, accepted).
- The award must emit an immutable **selection record** — authority status, safety snapshot,
  insurance evidence, gate applied, and who was excluded and why (A8's BR-802). This is one
  requirement shared with A3, not two.
- A2's eligibility function is now load-bearing for the whole product, not a filter.

**Still open, and not decided by this:** what the safety floor actually is — which FMCSA signals,
at what level, rechecked how often. That is a real decision with a real supply cost (A2's DEC-201)
and it needs the client.

---

## DEC-LOCK-002 — The platform's own data assets are in scope as a differentiator

**Decided by Boss, 2026-07-29.** Boss's words: *"then we have usa routes data, mechanic data,
fuelstation etc."*

**What was decided.** Boss's existing US truck-data platform (`~/Documents/truck-intel`) is treated
as an available asset for this product, not a separate project.

**Verified inventory** (counted directly from the running database, 2026-07-29 — not estimated):

**Restated per-table-per-licence after A12's challenge.** The first version of this table merged
permissive and share-alike layers into single rows — it put Overture `core.fuel_places` and ODbL
`osm.fuel_stations` on one line and omitted the ODbL table entirely, which is the one actually served
by the existing `/v1/fuel` endpoint. That is a licence-blind inventory, and scoping a re-architecture
against it would have aimed at the wrong asset. A12 was right to file it. Corrected:

| Table | Rows | Upstream | Licence posture |
|---|---|---|---|
| `core.truck_routes` | 454,830 | NTAD / BTS-FHWA | US government work — unrestricted public use |
| `core.bridges` | 629,710 | FHWA National Bridge Inventory | US government work |
| `core.tunnels` | 580 | FHWA National Tunnel Inventory | US government work |
| `core.parking_sites` | 1,915 | NTAD Truck Stop Parking (BTS) | US government work |
| `core.fuel_prices` | 17,089 | EIA weekly on-highway diesel | US government work — on the client's own API key |
| `core.fuel_places` | 151,767 | **Overture** | Permissive — verified today as **not** OSM-derived |
| `core.mechanic_shops` | 11,759 | **Overture** | Permissive — same verification |
| `osm.fuel_stations` | **108,056** | **OpenStreetMap** | **ODbL — share-alike** |
| `osm.weigh_points` | 3,773 | **OpenStreetMap** | **ODbL — share-alike** |
| `osm.rest_areas` | 5,452 | **OpenStreetMap** | **ODbL — share-alike** |
| `osm.truck_repair` | 763 | **OpenStreetMap** | **ODbL — share-alike** |
| `core.live_events` | 10,636 | WZDx (AZ/KS/MN/WA) · NWS · Caltrans | State works — terms **unverified per state** |

Two things this table now makes visible that the old one hid. First, the two largest POI layers are
**permissive**, not share-alike — which is a much better starting position than assumed. Second, the
ODbL layers are real and they are what the existing fuel endpoint serves.

**The architectural constraint, stated plainly.** Under ODbL, a rendered map, a corridor summary or a
computed cost floor is a *Produced Work* — attribution only, and the client's product stays
proprietary. An endpoint that returns OSM records as JSON is re-utilisation into a publicly-used
*Derivative Database*, which obliges offering recipients the database or a full alterations file.
The rule that keeps both the layers and the client's proprietary posture: **ODbL layers are consumed
as Produced Works only and never cross the API boundary.**

**AAA diesel — checked directly, not assumed.** A12 recommended dropping the AAA price scraper
because gasprices.aaa.com grants only personal, non-commercial use and separately prohibits archiving
and distribution. Jarvis verified the live state: `AAA_PRICES_ENABLED` is set nowhere,
`core.fuel_prices` contains **only** `eia_diesel` rows and zero AAA rows, and the script records its
own terms verbatim and stays off unless explicitly switched on. **The guard is holding and there is
no live exposure.** The BRD must nonetheless not plan on AAA data — EIA stays the source of record.

**Why this matters strategically.** A10's finding was that price discovery in US truckload is
already solved — DAT and Truckstop sell it cheaply — so "cheaper price" cannot be the wedge. What is
actually scarce is coverage certainty, defensible carrier selection, and freedom from fraud. These
data layers point at exactly those, and at two specific problems the agents flagged as the hardest
in the whole document:

- **Post-award re-trade at the dock** — A3 named this the mechanism's biggest practical leak.
  Truck-legal mileage plus current diesel gives a defensible cost floor for a lane, which makes a
  bid that *cannot* be performed visible before it is awarded rather than after the freight is on
  the floor.
- **Mid-trip breakdown with freight already loaded** — A4 called this genuinely hard and did not
  hand-wave it. A mechanic layer is an operational answer rather than a policy sentence.

**Open and not decided by this:** whether each source's licence permits use inside a client's
commercial product. Government sources are the strong case; OSM-derived layers carry share-alike
obligations and any scraped price feed carries terms-of-use risk. Under review — see part A12.

---

### Correction to DEC-LOCK-002's rationale, 2026-07-29 — filed against Jarvis, not Boss

The rationale above was written by Jarvis and it **overreached**. A11 was briefed to be skeptical
about exactly this and it pushed back on the framing rather than absorbing it. The pushback is
accepted and recorded here rather than quietly edited away.

**What was wrong.** The rationale reached for these data layers as an answer to A10's
disintermediation problem — what holds a transaction on the platform once the two sides have each
other's number. A11's verdict: that is the **weakest** of the seven candidate capabilities, not the
strongest, and treating it as the answer is motivated reasoning. Trucker Path and DAT Trucker Tools
already give a better "helpful trucking data" layer to millions of drivers for free or near-free; a
mid-backfill personal database does not beat them on coverage or freshness, and a determined
shipper-carrier pair routes around it anyway.

**What survives, and it is real.** Two capabilities hold up on merit and tie directly to named
failure modes elsewhere in this document:

1. **Route feasibility at auction time** — the strongest. Whether a given load on given equipment can
   lawfully run a lane, before bids are taken. Jarvis verified the schema supports it rather than
   assuming: tunnels carry hazmat restriction and vertical clearance on **580 of 580** rows; bridges
   carry weight posting status on **623,367 of 629,710** (99.0%) and operating rating on 98.9%.
   Vertical clearance is present on 161,112 (25.6%), which is the subset that actually has a measured
   overhead restriction rather than a coverage gap.
2. **Fuel-based cost floor as a *signal*** — narrow but genuine, aimed at A3's RSK-303 post-award
   re-trade leak, whose root cause is a bid that could never be performed. A11 was explicit that this
   is fuel-only, is **not** a rate engine, and must flag rather than block so it does not reach into
   A3's bid mechanics.

**What was cut.** A11 rejected detention/dwell evidence outright — none of these layers produce a
custody timestamp, so that connection did not exist. And it downgraded disintermediation from an
asserted moat to a measured feature tied to A10's leakage KPI.

**The honest position, therefore:** this asset is a legitimate feature set that strengthens two
specific requirements. It is **not** a moat, and the BRD must not present it as one.
