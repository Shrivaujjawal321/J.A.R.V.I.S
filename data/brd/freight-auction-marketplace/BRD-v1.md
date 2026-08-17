# Business Requirements Document — US Freight Reverse-Auction Marketplace

## Document Control

| Field | Value |
|---|---|
| Document Title | Business Requirements Document — US Freight Reverse-Auction Marketplace |
| Document ID | BRD-FREIGHTAUCTION-2026-001 |
| Version | 1.0 |
| Status | Draft |
| Author | Jarvis (assembler), synthesizing twelve parallel domain drafts (A1–A12) |
| Business Sponsor | `[NEEDS INPUT: named client business sponsor + title — A9 §5.2]`. Document commissioned by Boss (Ujjawal); the platform's client sponsor is a separate, currently unnamed party (classification.md). |
| Date Created | 2026-07-29 |
| Readiness Score | 58/100 — see Appendix, Readiness Report. **Structural score, not a validity score — read the caveat before citing this number.** |

**Change Log**

| Version | Date | Author | Change | Approved By |
|---|---|---|---|---|
| 1.0 | 2026-07-29 | Jarvis (assembler) | Initial assembly from spine.md + DECISIONS.md + intake/classification + twelve agent parts (A1–A12) | `[NEEDS INPUT]` |

---

## 1. Executive Summary

Boss specified a US freight reverse-auction marketplace in one paragraph: shipper posts a load, eligible carriers bid, lowest bid wins, freight moves pickup-to-drop, POD triggers an invoice. Twelve domain drafts and this assembly turned that into 212 business requirements, a 46-entry assumptions register, a 50-entry risk register, and a canonical exception-state model covering 227 named edge cases — and surfaced, in the process, that the mechanism as specified collides directly with a US Supreme Court decision handed down eleven weeks ago. On 14 May 2026, *Montgomery v. Caribe Transport II, LLC* removed the legal shield that previously protected freight brokers from being sued for *how* they picked a carrier. A platform that awards strictly on price, with FMCSA safety data available and unused, now manufactures the evidence against itself. Boss's own response to this, made the same day this document was assembled, is the fact that keeps the project's core premise intact: carrier eligibility is checked *first*, structurally, and price still decides — but only inside that qualified pool (DEC-LOCK-001). That single decision is what stops OBJ-001 (cheaper) and OBJ-004/006/007 (safer, provable, lawfully defensible) from being flatly incompatible; it does not make them fully aligned, and this document deliberately keeps that tension visible rather than smoothing it into false consensus.

What is genuinely decided: the award mechanism's legal precondition (DEC-LOCK-001), the treatment of the client's existing US truck-data platform as an in-scope, licence-audited product asset rather than an assumed moat (DEC-LOCK-002, corrected mid-project after the manager's own overreach was caught and filed against itself), and a canonical lifecycle spanning 24 states from `DRAFT` through `COMPLETED`, reconciling three independently-proposed exception-state sets into one. What is not decided, and cannot be decided by drafting: whether the client already holds FMCSA broker authority — a single fork that, this assembly found, was asked five separate times across five separate domains without ever being tied together as one decision, and that resolves the money model, the money-transmission licensing question, and half the liability analysis in one motion the moment it is answered. Nor is the business premise itself validated: the Five Whys ladder this document is required to run terminates in an honest unknown — no named shipper has confirmed that price, rather than vetting, fraud exposure, or back-office burden, is actually the pain being solved, and the best-funded prior attempt at exactly this business (Convoy, ~$1.1B raised) shut down in 2023 having never run a price-only auction itself.

This document cannot state what the project is worth or when it lands — no baseline, target, or timeline was supplied, and none is invented here; every such field in §2 and §15 is honestly `[NEEDS INPUT]` rather than a plausible-sounding guess. Its readiness score (58/100, Appendix) measures structural completeness, not correctness, and says so explicitly. What it can state is the priority order for what happens next: resolve §13.1's regulatory-status fork, run the P0 shipper-validation gate before another line of requirements is drafted against an unvalidated premise, and close the live data-licensing exposure at `DEC-1200` before any endpoint already in production ships to a client. Everything else in this BRD is ready for that conversation, not a substitute for it.

---

## 2. Business Objectives

Boss supplied a mechanism (reverse auction, lowest bid wins) and a happy-path sequence, not a set of objectives (intake.md). The seven objectives below were pre-allocated by the spine (§5) before any agent drafted, and their wording was refined by A10 from the assembled evidence — IDs are fixed, targets are not. **No target, baseline, or date below is invented; every one is `[NEEDS INPUT]`.**

| ID | Objective | Baseline | Target | Measurement method | Date | Owner |
|---|---|---|---|---|---|---|
| OBJ-001 | Lower landed cost per load vs. the shipper's current allocation method, **without degrading on-time or claim performance below that method's baseline** (A10 refinement, adopted) | `[NEEDS INPUT]` — no current-method baseline supplied | `[NEEDS INPUT]` | Pre-platform baseline, same lane, compared to platform-awarded price (KPI-1004) | `[NEEDS INPUT]` | `[NEEDS INPUT]` |
| OBJ-002 | Cut elapsed time and human touches from "load ready" to "carrier committed" | `[NEEDS INPUT]` | `[NEEDS INPUT]` | `PUBLISHED` → `AWARD_ACCEPTED` interval; touch-count sampling (KPI-1003, KPI-303) | `[NEEDS INPUT]` | `[NEEDS INPUT]` |
| OBJ-003 | Raise carrier equipment utilisation by giving carriers access to load flow they cannot reach today | `[NEEDS INPUT]` | `[NEEDS INPUT]` | Awards to carriers with no prior tie to the shipper (KPI-1012 repeat/leakage cohort) | `[NEEDS INPUT]` | `[NEEDS INPUT]` |
| OBJ-004 | Make every delivery provable, in a form that survives a Carmack claim | `[NEEDS INPUT]` | `[NEEDS INPUT]` | % loads with a signed BOL, clear-or-exception notation (KPI-1005/1007) | `[NEEDS INPUT]` | `[NEEDS INPUT]` |
| OBJ-005 | Right invoice, right party, right reporting, on time — including factored receivables | `[NEEDS INPUT]` | `[NEEDS INPUT]` | Invoice-exception rate; on-time settlement rate | `[NEEDS INPUT]` | `[NEEDS INPUT]` |
| OBJ-006 | Keep the platform trustworthy enough that strangers transact high-value freight on it, under active fraud pressure | `[NEEDS INPUT]` | `[NEEDS INPUT]` | Fraud events / 1,000 loads (KPI-1009) | `[NEEDS INPUT]` | `[NEEDS INPUT]` |
| OBJ-007 | Operate lawfully across the brokerage, transport-safety, and state privacy regimes this flow touches, **with carrier selection documented to a defensible standard post-*Montgomery*** (A10 refinement, adopted) | `[NEEDS INPUT]` | `[NEEDS INPUT]` | A7 compliance audit; vetting/selection record present on every award (BR-303) | `[NEEDS INPUT]` | `[NEEDS INPUT]` |

### 2.1 The tension inside this objective set — carried forward, not smoothed over

**A10 filed a challenge against its own spine-assigned wording, and the assembler is carrying it rather than resolving it, per the task brief's explicit instruction.** OBJ-001 (cheaper) and OBJ-004/OBJ-006/OBJ-007 (safer, provable, lawfully defensible selection) pull in opposite directions under a strict price-only award rule. This is not a drafting inconsistency to be edited away — it is the central design fact of this project:

> Under a price-only rule these are not merely in tension: after *Montgomery v. Caribe Transport II, LLC* (14 May 2026), pursuing OBJ-001 via a documented lowest-bid rule manufactures evidence against OBJ-007. Spine §4 called lowest-bid "a strong commitment with documented failure modes" — written before this ruling was in view. The legal weather has changed. — A10, §2 CHALLENGE

**DEC-LOCK-001 (2026-07-29, Boss) resolves the sharpest edge of this tension, but does not remove it.** Boss decided carrier eligibility is checked *first*; price still decides *within* the qualified pool (see DECISIONS.md, reproduced in full at §13.1). That keeps OBJ-001's mechanism intact while giving OBJ-007 a gate to point to. It does **not** resolve which objective wins when they still conflict inside the qualified pool — e.g., a qualified carrier with a marginally worse safety percentile still wins on price alone under DEC-LOCK-001. **Not all seven objectives can be Must simultaneously; this document does not choose for Boss which one yields.** All seven are carried as stated; §14 Risk Register and §8.3 (Auction & Bidding) carry the consequences as named, scored risks rather than silently absorbing them.

### 2.2 What this document is explicitly NOT deciding on objectives

Whether OBJ-001 should be formally demoted below OBJ-006/OBJ-007 in priority (A10's proposed resolution) is a decision for Boss, not the assembler. This BRD presents the tension; it does not resolve it.

---

## 3. Background / Problem Statement

### 3.1 What Boss supplied, and what he did not

Boss supplied a **mechanism** — three roles (shipper, carrier, receiver), a reverse auction with lowest-bid-wins allocation, and a happy-path sequence (`Shipper → Shipment → Auction → Eligible Carrier → Carrier Bid → Lowest Bid → Pickup → Transit → Drop → POD → Invoice generation → Shipment Complete`) — not a validated business problem (intake.md). A Five Whys ladder was mandatory and blocking per classification.md; A10 ran it against the current US truckload market. It terminates in an **unknown**, not a resolved chain:

| # | Question | Answer | Status |
|---|---|---|---|
| W1 | Why auction a load at all? | Because on some loads the shipper cannot get a truck at an acceptable price, or search effort is high. | **Unknown here** — no shipper, lane, or current method supplied. `[NEEDS INPUT: which shipper, which lanes, failing how — covered how today?]` |
| W2 | Why does the routing guide fail? | Contract carriers reject tenders when spot pays better; US tender rejections are at their highest since 2022, spot linehaul passed contract for the first time since 2021. | Known market-wide; unverified against this client |
| W3 | Why is spot capacity scarce now? | Capacity exited the market: for-hire carriers ~241,000 (Jun 2020) → 475,000+ (Jul 2023); 100,000+ authorities revoked/deactivated 2023–24; net revocations +16% H1-2025 vs H1-2024. | Known |
| W4 | Why hasn't price discovery already solved it? | **It largely has.** DAT and Truckstop dominate US spot price discovery and already sell lane-rate analytics and instant booking; reverse-auction procurement products exist (Emerge, Sleek). The residual pain is not "I don't know the price" — it is coverage certainty, vetting, and admin burden. | Known — **this finding undercuts the stated wedge and is the single most important market fact in this document** |
| W5 | So why does anyone still lose money on this? | Unconfirmed candidates: (a) vetting a stranger carrier is slow and legally hazardous; (b) fraud makes cheap capacity practically unusable; (c) the shipper's own back office (tender → rate confirmation → BOL → invoice → claim) is manual; (d) small shippers have no broker relationship at all. | **Unknown — the largest gap in this document.** `[NEEDS INPUT: which of (a)–(d) applies, and to whom]` |

**This BRD proceeds without W1 and W5 answered.** Every requirement below is well-formed against the *mechanism* Boss described; none of it has been validated against a *named shipper's* actual pain. A10's P0 phase gate (§17.2) makes this explicit as a precondition on build, not an afterthought.

### 3.2 Current state and cost of inaction

**Market cost of the status quo, cited, not estimated by the assembler:**

- US/Canada cargo-theft losses ≈ **$725M in 2025**, up ~60% on ~$455M in 2024, over 2,646 confirmed incidents, average loss per theft $273,990 (up 36%); strategic deception-based theft now roughly a third of cargo crime (Verisk CargoNet, cited A8 §8.7, A10 §3.1).
- Double-brokering losses estimated by TIA at **~$700M–$1B/year**; FMCSA broker-fraud complaints rose from ~2,000 (2021) to 8,000+ (2025) (A10 §3.1).
- **This is a trust problem before it is a price problem** — the Five Whys ladder (§3.1, W4) and the fraud-cost figures above point the same direction independently.

**What the best-funded prior attempt at this exact business proved, and did not solve:**

Convoy raised ~$1.1B, was valued at ~$3.8B, and shut down in October 2023 with no buyer. Its post-mortem cited no physical stickiness (no trailers, drop network, or exclusive capacity) and that market share was bought with unattractive freight (A10 §3.2, citing CNBC/Forbes/Truckstop). **Convoy's own auction was never price-only** — it scored a carrier-quality signal alongside price specifically so a strong carrier could win without being cheapest (FreightWaves 2019, cited DEC-LOCK-002 and A10 §3.2). This is direct evidence against the premise Boss supplied (lowest-bid-only), from the operator that held the most data in this category. Transfix killed its SPAC and sold its brokerage in 2022; Uber Freight, the best-capitalised survivor, reached breakeven Adjusted EBITDA only in 2025, its first profitable year in three-plus (A10 §3.2). Incumbent brokerage gross margins (C.H. Robinson NAST 14.6% FY25; RXO brokerage 13.3–14.8% across 2025) place a hard ceiling on any spread-based take rate this platform could sustain (A10 §3.2, §3.7).

**The legal fact that post-dates the intake framing entirely:** On 14 May 2026 the US Supreme Court decided *Montgomery v. Caribe Transport II, LLC*, No. 24-1238, 608 U.S. ___ (2026) (unanimous, Barrett, J.), holding that the FAAAA safety exception preserves state-law negligent-hiring claims against brokers in all fifty states — ending the preemption defence that previously killed these claims at the pleading stage in several circuits (A7 §7.3, A8 §8.3, A10 §3.3, sources cited there). **An award rule documented as "lowest bid wins," with FMCSA safety data available and unused, is now the exact fact pattern plaintiffs' counsel look for after a serious crash** — and the platform's own award log becomes the evidence, for or against it. This was decided *after* the spine's first revision was written and materially changes the risk calculus behind the stated mechanism; see DEC-LOCK-001 for how Boss's design responded.

**The freight cycle has also turned against a pure lowest-bid design.** Cass truckload linehaul was +5.6% YoY (April 2026), spot roughly +25% YoY — a tightening market gives carriers pricing power and makes a price-only mechanism harder to run, not easier (A10 §3.2, RSK-1009).

### 3.3 What this document is explicitly NOT deciding

- **Whether the client already holds FMCSA broker authority, carrier authority, both, or neither**, and whether the platform itself arranges transport for compensation or is software run by a third party holding authority (spine §0; A7 §7.1; A8 §8.1 `DEC-801`; A9 §9.2). **This is the single highest-leverage open question in the entire document** — see §3.4 below, where the assembler surfaces that it is asked five separate times across five separate parts without being tied together as one decision.
- **Which of the three money models (A6 §1: pass-through software / broker of record / commission-only marketplace) the client intends.** This is upstream of nearly every A6 requirement and much of A7's money-transmission analysis.
- Whether OBJ-001 should be formally subordinated to OBJ-006/OBJ-007 (§2.1).
- The actual safety floor for A2's eligibility gate — which FMCSA signals, at what level, rechecked how often (DEC-LOCK-001; A2 DEC-201).
- Whether a shipper may decline the lowest qualified bidder on safety/reliability grounds (A1 BR-155; A3 DEC-307; A3 EC-325 — the same open question, asked three times by two agents; see §3.4).
- Geography beyond "US domestic"; whether intrastate lanes, hazmat, temperature-controlled, or high-value freight are in scope for release 1 (A1 §10; A7 ASM-701–703; A8 ASM-801–806).
- Numbers: no rate, threshold, penalty amount, retention period, staffing level, or target metric appears anywhere in this document unless it was supplied by Boss or a cited external source. Every gap is tagged `[NEEDS INPUT]`, not filled.

### 3.4 A finding no single domain agent could see: the same blocking question, asked five times

Reading all twelve parts together surfaces something invisible to any one of them: **the client's regulatory posture (broker / carrier / vendor / neither) and the money-movement model are, functionally, one decision — but they were asked as five separate, unlinked `[NEEDS INPUT]` items**, each drafted by an agent that could only see its own domain:

| Where it is asked | Framing used | Cross-reference to the others |
|---|---|---|
| A6 §1 | "Which of the three models — pass-through / broker of record / commission-only — does the client intend?" | None — A6 does not cite A7 or A8's version of the same question |
| A7 §7.1 | "Does the client hold FMCSA broker authority, carrier authority, both, or neither?" (four-way fork A/B/C/D) | References A3/A10 on consequence, not A6 or A8 on the same fork |
| A7 §7.4 | Money-transmission fork M1/M2/M3, explicitly escalated to payments counsel | Says "routed here by A6" but A6's §1 model choice and A7's M1/M2/M3 are not mapped to each other 1:1 |
| A8 §8.1 `DEC-801` | Platform legal position P1/P2/P3 (broker / carrier / vendor), gating cargo-loss and selection-tort exposure | Cites §8.4–§8.6 "all turn on this" but does not cross-reference A6 §1 or A7 §7.1 by name |
| A9 §9.2 | Governance row: "Does the client hold, or intend to obtain, FMCSA broker authority" — flagged "highest-value open question in the entire document" | Correctly identifies the stakes; does not link to A6/A7/A8's parallel framings |
| A10 RSK-1010 | "No broker authority — unlawful to arrange for compensation without it; decides take-rate vs SaaS" | Names the strategic consequence; does not merge with the other four |

**These are not five different questions — they are one fork (client's FMCSA/legal posture) with two derived forks (A6's money model, A7's money-transmission fork) that each collapse once the first is answered.** No agent was positioned to see this, because each was scoped to its own ID block and forbidden from reading past its lane (spine §6). The assembler's finding: **answering "does the client hold broker authority, and does the platform ever touch the money" resolves A6 §1, A7 §7.1, A7 §7.4, A8 §8.1, and half of A9 §9.2 in one motion.** This is presented as a single blocking decision at §13.1 rather than five scattered ones.

---

## 4. Project Scope

| # | In Scope (Release 1) | Phase/MoSCoW | # | Out of Scope | Rationale for exclusion / where the work went instead |
|---|---|---|---|---|---|
| 1 | Three roles: Shipper, Carrier (asset-holder), Carrier (broker/agent); Receiver/Consignee as a non-account-holding fourth party | R1 · Must | 1 | Multi-stop loads | Boss's happy path is single-origin, single-destination; no multi-stop field exists in the load object (A1 §10). Deferred to a named future release. |
| 2 | Single-origin, single-destination, full-truckload freight | R1 · Must | 2 | Partial / LTL freight | Same basis as #1 (A1 §10). |
| 3 | Reverse auction, lowest-bid-wins **within a carrier-eligibility gate** (DEC-LOCK-001) | R1 · Must | 3 | Appointment-critical / hard-window, penalty-bearing loads | Not described in the happy path; no penalty-accrual model exists anywhere in the requirements (A1 §10). |
| 4 | Carrier eligibility tuple: entity, authority, insurance, safety signal, equipment, driver (A2 §A2.1) | R1 · Must | 4 | Hazmat freight | `[ASSUMPTION: no hazmat phase 1 \| conf: low]` (A7 ASM-703, A8 ASM-806) — flagged low-confidence; if wrong, BR-719/BR-118 and the entire hazmat regulatory surface (49 CFR 171-180) activate. Not designed against in this release. |
| 5 | Pickup → transit → drop custody chain, with structured pickup and delivery records (BOL/POD) | R1 · Must | 5 | Temperature-controlled / high-value specialisation beyond basic flagging | `[ASSUMPTION: no such specialisation phase 1 \| conf: low]` (A8 ASM-806). Basic reefer temperature field and high-value flag exist (A1 BR-112, BR-119) but no specialised handling logic. |
| 6 | Carmack-governed liability allocation, claims path, insurance structure | R1 · Must | 6 | Household goods carriage | `[ASSUMPTION: not household goods \| conf: med]` (A7 ASM-702, A8 ASM-802) — household-goods carriers remain subject to cargo-insurance rules this design assumes are not required (A8 §8.6). |
| 7 | Invoicing, settlement, factoring/NOA handling, W-9/1099 | R1 · Must | 7 | Intrastate-only lanes | `[NEEDS INPUT]` (A7 §7.1) — federal analysis in this document does not cover state-regulated intrastate carriage; counsel question per lane if added. |
| 8 | FMCSA/broker regulatory compliance surface, state privacy notice for the non-account-holding consignee | R1 · Must | 8 | Money-transmission licensing under Model M3 (platform holds funds) | Not ruled out, but requires payments counsel before design (A7 §7.4) — see §13.1. |
| 9 | Fraud typology detection signals (double brokering, identity theft, fictitious pickup) at the design-requirement level | R1 · Must | 9 | Detention/dwell evidence as a data-asset capability | A11 explicitly rejected this as a standalone capability — no layer in the truck-intel dataset produces a custody timestamp (A11 §11.1 capability 6, §11.4). A4's own BR-403 already owns arrival/departure timestamp capture independently. |
| 10 | Stakeholder roles/permissions model for multi-truck carriers and multi-site shippers | R1 · Must | 10 | Disintermediation defence via the data-asset layer | Downgraded by A11 from an asserted moat to a measured, unproven feature (A11 §11.3; DECISIONS.md correction to DEC-LOCK-002). Not sold as a retention mechanism in this release. |
| 11 | Route-feasibility check (bridge/tunnel/hazmat-restriction) at auction time, using the client's existing truck-intel data platform (DEC-LOCK-002) | R1 · Should | 11 | Any capability drawing on an ODbL-licensed layer (`osm.*`) as a served record, rather than an aggregated Produced Work | Blocked on `DEC-1200` (A12 §2) — architecture must resolve ODbL §4.4/§4.6 exposure before any OSM-derived record crosses an API boundary. See §8.11 (A12) and the explicit capability-level flags in §8.9 (A11). |
| 12 | Fuel-only cost-floor signal at bid time (flag, not block) | R1 · Should | 12 | AAA/OPIS scraped daily diesel pricing | **Hard exclusion.** AAA's terms prohibit commercial use, archiving, and distribution; the existing codebase already gates this off by default (A12 §1 row 16, §6). Must never ship enabled in a client build (BR-1204). |
| 13 | Mechanic-shop directory (breakdown recovery), disclosed as a directory, not a dispatch or availability guarantee | R1 · Could | 13 | Live parking/rest-area occupancy | No live occupancy signal exists in any source; static site lists only (A11 §11.1 capability 4). Advisory-only framing required wherever surfaced (BR-1108). |
| 14 | WZDx work-zone / NWS weather / Caltrans chain-control context on `TRANSIT_EXCEPTION` events | R1 · Could, **geographically bounded** | 14 | National live-event coverage | Work-zone feeds cover only AZ/KS/MN/WA; chain controls cover only CA; both are licence-`Unverified` pending A12 §7 counsel review. Presenting this as national coverage would misrepresent the feature (A11 §11.4; A12 §5). |

**Scope note on hazmat, household goods, and specialised freight:** three separate low-confidence assumptions (A7 ASM-703, A8 ASM-802/806) independently exclude the same class of freight from release 1. This is presented as one scope line (#4/#5/#6 above) rather than three, but the confidence is explicitly **low** — this is the exclusion most likely to be wrong and most expensive to retrofit if so, because it touches insurance (A8 §8.6), regulatory citation (A7 T-21), and the load-declaration schema (A1 §3) simultaneously.

---

## 5. Stakeholder Analysis + RACI

**Governance gap, stated plainly rather than papered over (A9 §9.2):** the exemplar RACI convention (named individual, per anti-patterns.md #6) cannot be honoured for the client-side governance rows below, because no client-side names were supplied anywhere in the twelve parts. Every "Accountable" cell in §5.2 is a genuine blocking gap, not a formatting placeholder — this document does not invent a name to satisfy the anti-pattern checker.

### 5.1 Stakeholder map

Three roles were supplied by Boss (spine §1: Shipper, Carrier, Receiver). **At least eight are actually in the room** (A9 §9.1), and the split matters because interest and influence run in opposite directions for the party who matters most at the point of failure: the mechanism is explicitly built to compress the carrier's price, and the consignee inherits whatever that compression produces — a re-traded pickup, a rushed driver, a damaged pallet — while holding no seat at all.

| Stakeholder | Signs up? | Primary interest | Influence over outcome | Conflict / note |
|---|---|---|---|---|
| **Shipper** | Yes | Lowest cost, on-time, low claims | High — sets terms, runs the auction | Captures the price benefit the mechanism produces but does not fully bear the service-quality risk that comes with it |
| **Carrier — asset-holder** | Yes | Win at a price that covers cost, get paid on time | Medium — bids into a price war it doesn't set | The mechanism structurally pressures its margin; the carrier most willing to underbid is not necessarily the most capable (RSK-301, winner's curse) |
| **Carrier — broker/agent** | Yes | Same, plus margin on re-brokered capacity | Medium | Its bid may not represent a truck it controls — the direct driver of double-brokering risk (→ §8.2 A2, §8.9 A8) |
| **Dispatcher** | Via carrier account, not independently | Book efficiently for a fleet it represents — often several trucks | Medium; de facto decision-maker for small/mid carriers | Frequently the *only* real point of contact on the carrier side; not itself a licensed or account-holding entity — a business-model gap, not an edge case |
| **Driver** | Rarely, directly | Get paid, run legal HOS, not be blamed for exceptions not of their making | Low formally, absolute in practice at both custody handovers | Bound by the account's bid/award decisions with no platform authority of their own; the person actually present when a claim-deciding signature happens |
| **Factoring company** | No | Be paid instead of the carrier once a Notice of Assignment is filed | Low platform-facing, high financially | Legally entitled to redirect payment (→ §8.6 A6); a role model that only has "carrier gets paid" cannot represent it |
| **Receiver / Consignee** | **No** | Correct, undamaged, on-time freight; accurate paperwork | **None, formally** | Holds the clear-vs-exception signature a Carmack claim lives or dies on, can refuse freight, absorbs every downstream failure — and agreed to none of the auction, the carrier choice, or the price |
| **Dock / receiving staff** | No | Get the truck unloaded and off the dock | None, formally | Often not the same legal person as "the consignee" (a third-party DC, a night-shift employee) — the hand that signs is frequently not the party with a stake in the outcome |
| **Shipper's own customer** | No | The freight arrives | None | `[ASSUMPTION: in the common case the consignee IS the shipper's customer, but a third-party DC/cross-dock pattern is also plausible and changes who should be contacted \| conf: med]` (A9 §9.1; ASM-035 in §11) |
| **Insurer (cargo / auto liability)** | No — policy relationship with carrier/broker, not the platform | Loss ratio; only valid claims paid | Low day-to-day, decisive at claim time | Its coverage terms bound what the platform can promise a claimant (→ §8.9 A8 §8.6) |
| **Claims adjuster** | No | Adjudicate to policy terms | Medium, at claim time only | May reach a conclusion in tension with the platform's own claims desk — role split unresolved (§5.2 row 6) |
| **Platform / Operator (the client)** | n/a | The marketplace runs, is trusted, is lawful | Total — writes every rule | May itself carry broker liability (§3.4) — unresolved and blocking |
| **Platform Ops staff** | Employed by operator, not a marketplace "user" | Keep the marketplace operating | High, operational, invisible in a software-only model | The function §7.3 describes in full |

### 5.2 Governance — who at the client signs off

| Governance decision | Accountable (client-side) | Consulted | Informed | RACI (Requirements sign-off) | RACI (UAT sign-off) |
|---|---|---|---|---|---|
| Business requirements sign-off (this BRD) | `[NEEDS INPUT: named client business sponsor + title]` | Boss (author), client platform-ops lead `[NEEDS INPUT]` | All twelve domain owners | A: `[NEEDS INPUT]` | I |
| UAT acceptance | `[NEEDS INPUT: named client UAT owner]` | Client legal/compliance `[NEEDS INPUT]` | Boss | C | A: `[NEEDS INPUT]` |
| Does the client hold, or intend to obtain, FMCSA broker authority (§3.4) | `[NEEDS INPUT — highest-value open question in the entire document]` | Client counsel | A2, A3, A7, A8, A9 — every area touching selection or liability | C | I |
| Accept lowest-bid-only vs. a qualified alternative (§2.1; A3 supplies the option set at §8.3) | `[NEEDS INPUT: who at the client owns acceptance of negligent-selection risk]` | Client risk/legal | A2, A3, A7, A8 | C | I |
| State privacy compliance posture (CCPA/CPRA and peer statutes) | `[NEEDS INPUT]` | Client counsel | A7 | C | I |
| Claims-desk vs. insurer-adjuster authority split (§5.1 row "Claims adjuster"; §7.3) | `[NEEDS INPUT]` | Client operations, carrier's/broker's insurer | A8 | C | I |

**Escalation path for conflicts:** not specified by any of the twelve parts. `[NEEDS INPUT]` — this BRD cannot invent an escalation chain without a client org chart (A9's closing limitation, §9 "What A9 cannot do").

---

## 6. Current State (As-Is) Process

**Honesty note before this section: current-state data was supplied for exactly one segment of the lifecycle (pickup → transit → drop), and even that is hypothesised, not observed.** No shipper, carrier, or client operating data was supplied for the pre-auction (shipper sourcing) or post-delivery (settlement) segments — only A4 (Fulfilment) produced a formal as-is map, and it is explicitly tagged `[ASSUMPTION: baseline dispatch is phone/fax/paper-coordinated, industry-typical for small-to-mid carriers | conf: med]`. This is itself a finding, not a gap to quietly fill: **A10's P0 phase gate (§17.2) requires exactly this data — a named shipper stating what it does today and what that costs — before build, and this document cannot supply it.**

### 6.1 As-Is — Pickup through Drop (hypothesised, industry-typical, phone/fax/paper-coordinated dispatch)

| Step | Actor | Action | Pain point |
|---|---|---|---|
| 2.1 | Carrier dispatcher | Confirms load/window by phone/fax/email | Appointment lives only in someone's memory or inbox |
| 2.2 | Driver | Arrives at shipper dock | No system verifies driver/truck identity against the carrier actually booked |
| 2.3 | Shipper dock staff | Loads freight; paper BOL, driver signs | No timestamp, no photo, no system copy — no symmetric proof-of-readiness record for either party |
| 2.4 | Driver | Departs | Nobody knows the truck left until someone calls to ask |
| 2.5 | Driver | Drives; HOS logged on a device disconnected from shipper/broker | Detention and delay are invisible until disputed after the fact |
| 2.6 | Dispatcher | Learns of an exception only when the driver calls | No structured exception log → accessorial billing disputes have no evidence |
| 2.7 | Driver | Arrives at receiver dock | Handoff to delivery execution (§8.5, A5) |

### 6.2 What is NOT modelled here, and why

No current-state map exists for: how a shipper sources a carrier today (phone, load board, broker relationship, contract routing guide — A10's W1/W2 partially answer this at the market level but not for a named shipper); how disputes and claims are handled today; how invoices are reconciled today. **These gaps are not silently absorbed into a "current process improves" narrative in §7** — §7 below is explicitly split into a mirrored portion (6.1's steps, 1:1) and an unmirrored target-state extension covering the segments §6.1 never described.

---

## 7. Future State (To-Be) Process

### 7.1 To-Be — mirrors §6.1's numbering 1:1

| Step | Actor | Action | What changes |
|---|---|---|---|
| 2.1 | Platform | Award converts to an accepted rate confirmation (A6 BR-600); appointment window is a structured field (A1 BR-114) | Removes the phone-call-only appointment |
| 2.2 | Platform | Captures driver identity and equipment against the *awarded* carrier at check-in; mismatch flagged before loading (A2 BR-221) | Closes the double-brokering blind spot (→ A8 fraud classification, §8.9) |
| 2.3 | Shipper dock / Driver | Structured pickup event — count, condition, seal, dual signature (the BOL) — captured at tender (A4 BR-400) | Closes the proof-of-readiness gap A1 identified |
| 2.4 | Platform | State moves to `PICKED_UP` the instant the BOL is captured | Departure is no longer a phone call |
| 2.5 | Carrier/Driver | Status update required within a defined interval `[NEEDS INPUT: reporting interval]` (A4 BR-401); a missed interval is itself a flagged event | Silence becomes visible, not invisible |
| 2.6 | Carrier/Driver | Any transit exception reported as a categorised, timestamped event (A4 BR-405) | Accessorial disputes now have evidence (→ A6 §8.6) |
| 2.7 | — | Arrival `AT_DROP` | Handoff to delivery execution (A5) |

**Honest limit carried forward from A4:** some carriers, particularly small ones, will not proactively report anything absent a call. Step 2.5 does not make them report — it makes the platform's knowledge state honest (flagged-unknown, not falsely-assumed-fine), which is the most a requirement can guarantee without prescribing a solution.

### 7.2 To-Be — unmirrored extension (target-state only; no current-state baseline exists for this segment)

| Step | Actor | Action |
|---|---|---|
| 1.1 | Shipper | Registers org, publishes a fully-declared load (commodity, weight, equipment, dimensions, appointment windows) — A1 §1–§3 |
| 1.2 | Platform | Auction opens; eligible carriers (A2's tuple, computed per load) bid; ineligible bids are never ranked (A3 BR-301) |
| 1.3 | Platform | Auction closes; award goes to the lowest bid inside the eligible pool (DEC-LOCK-001); the award record is frozen and reproducible (A3/A8 merged BR-303, §8.11) |
| 1.4 | Carrier | Accepts award, creating a binding rate confirmation (A6 BR-600) |
| 3.1 | Consignee | Signs the delivery receipt clear or with exception (A5 BR-501); this single field decides most downstream claim outcomes |
| 3.2 | Platform | Invoice issues at `POD_CAPTURED`; undisputed lines settle on the standard cycle, disputed lines hold independently (A6 BR-603) |
| 3.3 | Platform | Shipment reaches `COMPLETED` once every held line resolves — a claim closes, an accessorial is evidenced, or a dispute window lapses (A6 §3) |

### 7.3 The desk behind the software

Every exception state below lands on a human. A9's finding, carried forward without softening: **a model that specifies software states and not the operational function reading them describes something that cannot run.** Carrier vetting review, continuous re-verification, an exception desk, claims intake, fraud review, dispute-resolution ops, and collections are all named functions with no staffing size, coverage model, or SLA specified anywhere in the twelve parts — that is a client operating decision this document cannot invent numbers for (A9 §7.4, DEP-900, RSK-901).

### 7.4 Canonical exception-state table (assembler-reconciled)

**This is the assembler's most consequential single act of reconciliation.** Three agents proposed additional exception states independently: A5 (`DELIVERY_ATTEMPTED_NO_RECEIVER`, plus an argument that OS&D is POD *content*, not a custody fork), A3 (`AUCTION_FAILED_ALL_ABOVE_LIMIT`, `AWARD_VOIDED_INELIGIBLE`, `AUCTION_EXTENDED`), A8 (`FRAUD_SUSPECTED`, `RECOVERY`, `CARRIER_SUSPENDED_IN_FLIGHT`). None of the three could see the other two's additions. Reconciled below into one table, each state's origin marked.

**Decision on A5's OS&D challenge: accepted.** The spine's original table listed `PARTIAL_DELIVERY / SHORT_DELIVERY / OS&D` as one row. A5's argument is adopted without modification: `PARTIAL_DELIVERY` is a genuine **custody fork** (some freight reaches the consignee, some does not, and A4 must route the remainder); `SHORT_DELIVERY`/`OS&D` is frequently just **POD content** — a fully-transferred, fully-signed load whose count or condition differs from declaration, with nothing physically routed elsewhere. Forcing OS&D into its own lifecycle branch would fork the state machine for what is often a data field on an otherwise-normal `DELIVERED → POD_CAPTURED` transition. **Reasoning for accepting rather than overriding:** A5 owns POD content and delivery execution end to end (spine §6), and its argument is internally consistent with how A8 already treats the clear-vs-exception field (§8.9, A8 §8.2) — OS&D is evidentiary content on a claim, not a distinct custody state, and A4's `PARTIAL_DELIVERY` already exists to carry the genuine custody fork. No agent's model breaks if this is adopted; A3's and A8's own tables never actually branch logic on an `OS&D` *state* separately from the POD fields A5 defines. Table below reflects this: OS&D is modelled as a structured **notation** (A5 BR-503) attachable to `DELIVERED`, `PARTIAL_DELIVERY`, or `DELIVERY_REFUSED`, not as a state of its own.

| State | Enters from | Owning domain | Origin |
|---|---|---|---|
| `DRAFT → PUBLISHED → AUCTION_OPEN → AUCTION_CLOSED → AWARDED → AWARD_ACCEPTED → PICKUP_SCHEDULED → AT_PICKUP → PICKED_UP → IN_TRANSIT → AT_DROP → DELIVERED → POD_CAPTURED → INVOICE_ISSUED → INVOICE_FINALISED → SETTLED → COMPLETED` | Happy path | Spine | Boss intake, expanded |
| `AUCTION_EXTENDED` | AUCTION_OPEN | Auction | A3 (anti-snipe DEC-305, or thin-market re-open DEC-310) |
| `AUCTION_FAILED_NO_BIDS` | AUCTION_CLOSED | Auction | Spine, retained |
| `AUCTION_FAILED_NO_ELIGIBLE_CARRIER` | AUCTION_OPEN | Carrier eligibility / Auction | Spine, retained |
| `AUCTION_FAILED_ALL_ABOVE_LIMIT` | AUCTION_CLOSED | Auction | A3 (DEC-306 reserve/ceiling) |
| `AWARD_PENDING` | Winner determined | Auction | A3 (gate re-verification window before commitment) |
| `AWARD_VOIDED_INELIGIBLE` | AWARD_PENDING | Auction / Carrier eligibility | A3 (gate fails on re-verification at award) |
| `AWARD_DECLINED` / `AWARD_LAPSED` | AWARDED | Auction | Spine, retained |
| `SHIPPER_NOT_READY` | AT_PICKUP | Shipper / Fulfilment | Spine rev.2 (A1 challenge, accepted) — distinct from `CARRIER_NO_SHOW`; carrier arrived on time, shipper/freight was not ready |
| `CARRIER_NO_SHOW` | PICKUP_SCHEDULED | Fulfilment | Spine, retained |
| `PICKUP_REFUSED` | AT_PICKUP | Fulfilment | Spine, retained (freight differs from declaration, unsafe load, wrong equipment) |
| `TRANSIT_EXCEPTION` | IN_TRANSIT | Fulfilment | Spine, retained; A4 requires a categorised sub-type on every occurrence (BR-405), never a generic "delay" flag |
| `DELIVERY_ATTEMPTED_NO_RECEIVER` | AT_DROP | Receiver / POD | A5 (BR-509) — no receiver present or hours closed; custody stays with the carrier, no POD created |
| `DELIVERY_REFUSED` (full) | AT_DROP | Receiver / POD | Spine, retained |
| `PARTIAL_DELIVERY` | AT_DROP | Receiver / POD | Spine, retained — genuine custody fork |
| `RETURN_TO_ORIGIN` | Post-refusal | Fulfilment | Spine, retained |
| `DAMAGED` / `LOST` / `PILFERED` | Any custody state | Liability & trust | Spine, retained |
| `FRAUD_SUSPECTED` | Pre-pickup onward | Liability & trust | A8 — distinct from `DISPUTED`: attaches pre-pickup, suppresses payment, triggers third-party notification |
| `RECOVERY` | From `LOST`/`PILFERED` | Liability & trust | A8 — believed stolen and actively being recovered; physically distinct from a closed `LOST` |
| `CARRIER_SUSPENDED_IN_FLIGHT` | Any custody state, carrier under enforcement | Liability & trust / Ops | A8 — party-level enforcement colliding with a live shipment; access is not simply cut (A8 §8.10) |
| `CLAIM_OPEN` | DELIVERED onward, and earlier | Liability & trust | Spine, retained (Carmack) |
| `DISPUTED` | Any state | Liability & trust | Spine, retained |
| `CLOSED_UNRESOLVED` | DISPUTED | Liability & trust | Spine, retained |

**OS&D, over/short/damage:** a structured notation (type: over/short/damage; quantity/unit; whose count) attachable to `DELIVERED`, `PARTIAL_DELIVERY`, or `DELIVERY_REFUSED` (A5 BR-503) — not a state in the table above. A5's CHALLENGE is adopted for this reason.

---

## 8. Business Requirements

Organised by domain (matching the twelve agents' ID blocks, spine §5), because at this scale a single flat 212-row table serves no reader. **No ID collisions exist across domains** — the spine's per-agent numeric blocks (§5) prevented that structurally. The reconciliation work in this section is: (a) one requirement merge (BR-303/BR-802 → §8.3/§8.9 below), (b) one requirement narrowed to stop re-deriving another domain's evidentiary fact (BR-806, §8.9), (c) prose cross-reference pointers resolved to real IDs where the assembler could verify them, and (d) a small number of genuine orphans flagged rather than silently resolved. Full detail on all of this is in `assembly-report.md`.

### 8.1 Shipper Domain (A1, BR-100–156)

*Not owned here: bid mechanics (§8.3), pricing/invoicing (§8.6), FMCSA/broker regulation (§8.7), carrier eligibility (§8.2), consignee POD (§8.5), liability adjudication and ratings (§8.9).*

| ID | Requirement | Pri | Traces | Acceptance | Source |
|---|---|---|---|---|---|
| BR-100 | Shipper registers as an organisation supporting multiple authorised users, not one login. | Must | OBJ-002 | Org has ≥1 user; adding users needs no re-registration. | derived |
| BR-101 | Org roles distinguish a post-only user from one authorised to cancel/amend. | Should | OBJ-002/006 | Post-only user's cancel/amend calls are rejected. | derived; resolves to A9 BR-901/BR-904 (site poster vs. account admin) |
| BR-102 | Every publish/amend/cancel action records the named user and timestamp. | Must | OBJ-006 | Each state transition has an attributable user ID. | derived |
| BR-103 | Org supports multiple ship-from/ship-to sites, independently selectable per load. | Must | OBJ-002 | 3-site shipper needs no separate accounts. | `[ASSUMPTION — see §11 ASM-001]` |
| BR-104 | Org's legal identity (EIN or equivalent) is verified before first publish. | Must | OBJ-006/007 | Unverified org cannot reach PUBLISHED. | `[NEEDS INPUT: identity-check method]` |
| BR-105 | A payment-standing check gates first publish and re-verifies on a recurring cycle. | Must | OBJ-006 | Org has a dated standing record with a re-check schedule. | `[NEEDS INPUT: check standard]` |
| BR-106 | A payment-reliability signal (e.g. days-to-pay) is shown to bidders pre-bid, without raw financials. | Should | OBJ-006 | Auction view shows a standing indicator, no financial detail. | derived — **ORPHAN, see §8.12**: no A6 or A9 requirement implements the bidder-facing display this depends on |
| BR-107 | A shipper whose standing drops below threshold is suspended from new publishes; loads in flight are unaffected. | Must | OBJ-006 | Suspended org's publish blocked; open loads unchanged. | `[NEEDS INPUT: threshold]` |
| BR-108 | An org with an open unresolved non-payment dispute cannot publish. | Should | OBJ-006 | Publish rejected while dispute open. | derived — resolves to A8's `DISPUTED` state (§7.4) generally; **no A8 requirement specifically gates re-publish on an open dispute — partial orphan, see §8.12** |
| BR-110 | Load cannot reach PUBLISHED without commodity, weight, equipment type, piece/pallet count, and both appointment windows. | Must | OBJ-001/002/004 | Publish blocked, missing field named. | Boss intake happy path |
| BR-111 | Equipment type is a closed set (dry van, reefer, flatbed, step deck, power-only, ≥). | Must | OBJ-001/002 | Publish rejects types outside the set. | `[ASSUMPTION — see §11 ASM-002]` |
| BR-112 | Reefer loads require a mandatory temperature range (or ambient/protect-from-freeze). | Must | OBJ-001/004 | Reefer load without temp value cannot publish. | derived |
| BR-113 | Load requires declared dimensions sufficient for legal-load/equipment-fit checks. | Must | OBJ-001 | Publish blocked without dimensions where fit isn't self-evident. | derived |
| BR-114 | Load declares live-load vs. drop-and-hook (with a dock-time estimate for live) and appointment type per stop (FCFS vs. scheduled, with window). | Must | OBJ-001/002/004 | Both stops carry load type and explicit appointment type. | derived; charge treatment → §8.6 A6 (accessorial table) |
| BR-116 | Load declares dock vs. ground access, needed unload equipment (e.g. liftgate), and whether a lumper is expected, per stop. | Should | OBJ-001/004 | Access, equipment, lumper fields all visible per stop. | derived |
| BR-118 | Load flags hazmat and captures what a carrier needs to self-assess authority to haul it. | Must | OBJ-004/007 | Hazmat-flagged load blocks publish without sub-fields. | derived; regulatory depth → §8.7 A7 T-21, BR-719 |
| BR-119 | Load flags high-value/theft-attractive freight, independent of hazmat. | Should | OBJ-006 | Flag settable independent of hazmat status. | derived → §8.2 A2, §8.9 A8 |
| BR-120 | Weight is a single mandatory numeric field, no default, no placeholder. | Must | OBJ-001 | Publish blocked if weight is blank, zero, or system-default. | derived |
| BR-121 | Publish flow states bids were priced against this declaration and that a material dock discrepancy carries consequences; shipper must acknowledge. | Must | OBJ-001/006 | Acknowledgement required to complete publish. | derived — core anti-under-declaration control |
| BR-122 | The original declared load is retained immutably, even after later amendment. | Must | OBJ-006 | Pre-amendment version is retrievable, timestamped. | derived → §8.9 A8 evidence |
| BR-125 | Load requires a full address, named on-site contact, and site hours at both stops. | Must | OBJ-002/004 | Publish blocked without resolvable address/contact per stop. | derived |
| BR-126 | Stop-specific instructions (dock #, gate code) are attachable, visible only post-award. | Should | OBJ-002 | Hidden pre-award; visible post-award. | `[ASSUMPTION — see §11 ASM-003]` |
| BR-127 | Release 1 supports exactly one origin and one destination per load. | Must | scope | Load cannot be created with >1 pickup or drop. | Boss intake; see §4 scope table |
| BR-130 | Publish is a binding commitment to make declared freight available, as declared, at the declared window, absent a §8.1 cancellation-ladder exit. | Must | OBJ-006 | Commitment statement shown and confirmed at publish. | derived |
| BR-131 | Publish commits the org to honour the awarded rate once accepted, outside the amendment/cancellation/re-trade paths below. | Must | OBJ-001/006 | Accepted award cannot be unilaterally repriced by the shipper. | derived |
| BR-132 | A shipper cannot publish a second load against the same declared freight while one referencing it is open. | Should | OBJ-006 | Duplicate-freight publish blocked or flagged. | `[ASSUMPTION — see §11 ASM-004]` |
| BR-133 | Once PUBLISHED, auction timing/closure is entirely §8.3's; this domain does not own it. | Must | boundary | — | spine §6 |
| BR-135 | Amendment allowed only in DRAFT / PUBLISHED-pre-bid; once ≥1 bid exists, direct field edits are blocked. | Must | OBJ-006 | Amend call on a load with ≥1 bid is rejected. | derived |
| BR-136 | A material amendment (weight beyond tolerance, equipment, commodity, hazmat status, either address) post-first-bid forces withdraw-and-republish, not in-place edit. | Must | OBJ-001/006 | Material-field amend attempt triggers withdraw path. | `[NEEDS INPUT: tolerance value]` |
| BR-137 | A non-material amendment (contact, dock instruction, gate code) is editable through AWARD_ACCEPTED without voiding the award. | Should | OBJ-002 | Non-material field edits succeed post-award. | derived |
| BR-138 | A BR-136 withdrawal after an award exists is logged under §8.1's cancellation ladder, not a free redo. | Must | OBJ-006 | Post-award withdrawal creates a cancellation record. | derived — closes a dodge path |
| BR-139 | Withdrawal notifies all bidders/awarded carrier at the same moment it takes effect. | Must | OBJ-002/006 | No party learns of it later than the shipper's action time. | derived → §8.3 A3, §8.4 A9 notification matrix |
| BR-140 | Pre-award cancel is free of consequence beyond removal from the auction. | Must | OBJ-006 | No standing record raised. | derived |
| BR-141 | Post-award pre-dispatch cancel records a standing event without a TONU claim. | Should | OBJ-006 | Standing shows cancel; no TONU line created. | derived |
| BR-142 | Post-dispatch cancel generates a TONU-eligible claim, evidenced by dispatch fact. | Must | OBJ-006 | Claim record created on cancel after dispatch. | `[NEEDS INPUT: dispatch-proof standard]`; **charge amount → §8.6 A6 TONU accessorial row, BR-601/602. Cross-referenced both directions — see §8.6.** |
| BR-143 | On-time carrier arrival against an unready shipper always enters `SHIPPER_NOT_READY`, generating TONU + detention claims, never `CARRIER_NO_SHOW`. | Must | OBJ-004/006 | State never mislabels shipper fault as carrier fault. | derived, spine rev.2; **charge amount → §8.6 A6 TONU/Detention rows. Cross-referenced both directions — see §8.6.** |
| BR-144 | Cancellation is unavailable once `PICKED_UP`; custody-holding freight is §8.4 (RTO) / §8.9 (liability) territory. | Must | boundary | Cancel action rejected post-`PICKED_UP`. | spine §3 |
| BR-145 | Standing record (BR-105/106) shows cancellations by stage, not one aggregate count. | Should | OBJ-006 | Carrier viewing standing sees stage-level breakdown. | derived |
| BR-150 | Shipper may reject a post-award rate demand and treat it as a carrier-side award failure, without triggering the cancellation ladder against itself. | Must | OBJ-001/006 | Rejected demand creates no shipper cancellation record. | derived → §8.3 A3 BR-310/311 (re-trade recording); no specific A8 requirement exists on the shipper-protection side — partial orphan, see §8.12 |
| BR-151 | If the shipper accepts a re-trade under time pressure, the change is recorded as an exception to the original award, not an overwrite. | Should | OBJ-006 | Both original award and accepted change remain visible. | derived → §8.3 A3 BR-310 |
| BR-152 | Every re-trade attempt is logged against the carrier, accepted or not. | Should | OBJ-006 | Demand is logged regardless of outcome. | derived → §8.2 A2 (carrier record), §8.3 A3 BR-311 |
| BR-155 | `[NEEDS INPUT]` Whether a shipper may decline an award to the lowest bidder, and on what basis, is undecided — a joint Boss/A3/A8 call. **The same open question as A3's DEC-307 and EC-325 (§8.3) — one decision, asked three times; see §13.1.** | Must | OBJ-006 | Resolved once decided upstream. | spine §4 |
| BR-156 | If a decline right is granted, it requires a structured reason code tied to objective carrier data already on file — not free-text override. | Should | OBJ-006/007 | Decline without a structured reason is rejected. | derived, conditional on BR-155 |

**Explicitly out of scope for release 1 (A1 §10):** multi-stop loads, partial/LTL freight, appointment-critical hard-window penalty-bearing loads — see §4 scope table, items 1–3.

### 8.2 Carrier, Equipment & Eligibility Domain (A2, BR-200–230)

*Excludes bid/award mechanics (§8.3), payouts (§8.6), fraud typology & penalties (§8.9), regulatory citation depth (§8.7) — referenced, not restated.*

**A carrier is never eligible in the abstract.** Eligibility is a fact about one tuple — carrier entity, operating authority, one insured equipment asset, one licensed driver with hours available — evaluated against one load at one point in time.

| Tuple element | Must be true simultaneously |
|---|---|
| Carrier entity | Onboarded, active, not suspended; role = asset-holder or broker/agent |
| Operating authority | Active FMCSA authority matching declared role; not revoked/out-of-service |
| Insurance | COI on file, not expired, covers the specific equipment asset |
| Safety signal | Rating + CSA/SMS data on file and current; considered per DEC-LOCK-001, not necessarily a hard gate beyond it (§8.2 DEC-201) |
| Equipment asset | Type matches load; status = AVAILABLE for the load window; not committed elsewhere |
| Driver | Active CDL of required class; Clearinghouse status clear; HOS capacity sufficient |

| ID | Requirement | Pri | Traces | Source | Acceptance |
|---|---|---|---|---|---|
| BR-200 | System shall compute eligibility per load, at bid submission, from the six tuple elements — never a static per-carrier flag set at onboarding. | Must | OBJ-004/006 | derived + spine §2 | A carrier with an expired COI is blocked from bidding same-day the COI lapses, no manual step. Out of scope: how §8.3 applies this gate. |
| BR-201 | Verify FMCSA authority (MC/USDOT) status at onboarding and recheck recurringly. | Must | OBJ-006 | derived | Status + check timestamp recorded; cadence `[NEEDS INPUT]` |
| BR-202 | Capture authority age at onboarding as a distinct field, not merged into pass/fail. | Must | OBJ-006 | research, 2026 — no universal day-threshold found; none invented | Visible at review; no auto-block on age alone (§8.2 DEC-201) |
| BR-203 | Capture declared role — asset-holder vs. broker/agent — with different required documents per role. | Must | OBJ-006 | spine §1 | Broker path requires broker authority + bond evidence, not equipment records |
| BR-204 | Require a COI naming the platform/broker as certificate holder, showing auto-liability + cargo cover + expiry, before bidding. | Must | OBJ-006 | research, 2026 — minimums → §8.7 A7 T-09 | No COI → `INELIGIBLE_NO_COI`, blocks all bids |
| BR-205 | Capture safety rating and CSA/SMS BASIC data at onboarding, refresh recurringly. | Must | OBJ-006 | research, 2026 | "Last refreshed" timestamp visible at award review |
| BR-206 | Collect W-9 before first payout eligibility. | Must | OBJ-005 | Boss intake | Precondition §8.6 A6 BR-612 checks; A2 only collects/stores |
| BR-207 | Verify legal name/address on onboarding record vs. FMCSA SAFER record; flag mismatch. | Should | OBJ-006 | research, 2026 | Mismatch holds onboarding, not silently accepted |
| BR-208 | Verify identity of the individual completing onboarding (authorized signer). | Should | OBJ-006 | `[ASSUMPTION — see §11 ASM-005]` | ID document on file, reviewable |
| BR-209 | Maintain equipment registry per carrier: type, VIN, plate, covering insurance policy. | Must | OBJ-003/004 | spine §2 | Every bid resolves to a specific equipment record, not a carrier-level claim |
| BR-210 | Maintain driver registry: CDL number/class/state, status. | Must | OBJ-006 | spine §0 | Driver record independent of account holder |
| BR-211 | Capture Clearinghouse query status (pre-employment, annual) per driver. | Should | OBJ-006 | classification.md | Field present; regulatory depth → §8.7 A7 |
| BR-212 | Bind driver + equipment + carrier at dispatch acceptance — the executable tuple instance. | Must | OBJ-004/006 | derived | This binding is what's checked against physical arrival at pickup (BR-221) |
| BR-213 | Record equipment ownership/lease status as informational field, not a gate. | Could | OBJ-003 | `[ASSUMPTION — see §11 ASM-006]` | Not used as a hard eligibility gate absent Boss instruction |
| BR-214 | Treat each equipment asset's availability as a time-windowed state; prevent the same asset counting eligible for two loads with overlapping pickup-to-delivery windows. | Must | OBJ-003/004 | derived (spine §2) | An asset committed to Load A (Mon 08:00–Wed 14:00) is not eligible for an overlapping Load B, but is eligible for Load C starting Wed 18:00. |
| BR-215 | Lock a committed asset on award acceptance; release on completion/cancellation/lapse. | Must | OBJ-003 | derived | No manual step to lock capacity post-award |
| BR-216 | Allow carrier self-declared unavailability (maintenance, personal), independent of any award. | Should | OBJ-003 | `[ASSUMPTION — see §11 ASM-007]` | Self-declared assets excluded from eligibility computation |
| BR-217 | Track expiry of authority, COI, CDL; move affected entity to `INELIGIBLE_FOR_NEW_BIDS` automatically on lapse. | Must | OBJ-006 | derived | Blocks new bids same-day; does not touch loads already past pickup |
| BR-218 | Lapse between award and pickup flags the award for ops review, does not auto-cancel. | Must | OBJ-006 | task brief | Award state unchanged automatically; exception queued → §7.3 A9 |
| BR-219 | Lapse after custody transfer (mid-transit) flags the trip for ops review, no automatic transit action. | Must | OBJ-006 | task brief | No auto-stop/recall/penalty at this layer; liability → §8.9, transit action → §8.4 |
| BR-220 | Send advance-expiry reminders before authority/insurance/CDL lapse. | Should | OBJ-006 | `[ASSUMPTION — see §11 ASM-008]` | Cadence `[NEEDS INPUT]` |
| **BR-221** | Re-verify **at pickup** that the driver and equipment physically presenting match the tuple bound at dispatch (BR-212) — driver identity vs. CDL on file, VIN/plate vs. registered equipment. **This is the evidentiary trigger A8's fraud classification (§8.9 BR-806) consumes — see the explicit cross-reference there. A2 records the fact; A2 does not classify it (BR-225).** | Must | OBJ-006 | research, 2026 — regime depth → §8.7 A7 | A mismatch on either produces a hold state and a signal to the exception path; never a silent proceed. Out of scope: fraud classification/penalty/claim consequence (§8.9); the pickup workflow itself (§8.4). |
| BR-222 | Record which entity is contractually carrier-of-record for each award (asset-holder or broker/agent). | Must | OBJ-006 | derived | Carrier-of-record queryable independent of who physically executes |
| BR-223 | If the winning bidder is a broker/agent, the downstream executing asset-carrier must independently hold `ELIGIBLE` status before dispatch confirms. | Must | OBJ-006 | derived | Closes the unvetted-sub-carrier gap; broker cannot dispatch an unvetted carrier |
| **BR-224** | Treat undisclosed post-award substitution of carrier/equipment/driver as a policy-violation signal, distinct from disclosed, re-vetted substitution. **Paired with BR-221 as the evidentiary basis A8 consumes for double-brokering classification (§8.9 BR-806) — do not re-derive.** | Must | OBJ-006 | task brief | Undisclosed → signal to §8.9; disclosed + still-eligible → normal operational path |
| BR-225 | A2 shall NOT classify fraud, apply penalties, or resolve liability from a mismatch signal. | Must | OBJ-006 | scope boundary (spine §6) | Output is a fact record, not a verdict — enforced by the BR-806 rewrite at §8.9 |
| BR-226 | At onboarding, verify contact details (phone/email/address) independently of the FMCSA record where possible. | Should | OBJ-006 | research, 2026 | Source of each contact field (self-reported vs. verified) recorded |
| BR-227 | At dispatch/pickup, re-verify driver + truck against records on file, not against what the arriving party presents unverified. | Must | OBJ-006 | research, 2026 | Same mechanism as BR-221; explicitly covers impostor, not only re-broker case |
| BR-228 | Flag last-minute dispatch-contact changes (new phone/email) not matching the onboarding record. | Should | OBJ-006 | research, 2026 (fictitious-pickup pattern) | Routes to review, not hard block (legitimate changes occur) |
| BR-229 | Suspending/removing a carrier moves it to `INELIGIBLE` for all new bids/awards immediately. | Must | OBJ-006 | derived | No new bid or award possible post-suspension |
| BR-230 | Suspension shall NOT automatically alter a load already past pickup with that carrier. | Must | OBJ-006 | task brief | In-flight load flagged for ops handling (§7.3 A9/§8.4 A4); not stranded by a database flag |

**DEC-201 — Verification rigour vs. liquidity (open, Boss decides):** three options carried forward unchanged from A2 — (A) uniform high bar before any bidding, (B) light bar to bid / heavy bar to win-dispatch, (C) baseline bids with tiered award review. No default picked; whichever is chosen must reach §8.3, since it changes how fast `AWARDED` reaches `AWARD_ACCEPTED`. Full trade-off table preserved in the source part; summarised at RSK-020/021 (§14).

### 8.3 Auction & Bidding Mechanism Domain (A3, BR-301–318)

*Not here: eligibility (§8.2), settlement (§8.6), fraud and penalties (§8.9), regulation (§8.7).*

**4.1 The legal constraint that bounds the mechanism.** In the US a party that selects a motor carrier for a shipper can be sued for negligent selection, and the selection criteria become discovery evidence. This is settled law nationwide since *Montgomery v. Caribe Transport II, LLC* (§3.2). **Minimum defensible design, binding on every option in this section:**

1. Price ranks *within* a pool; it does not define the pool (DEC-LOCK-001).
2. The gate is written, versioned, applied identically to every bidder (§8.2 owns content); no silent admission of a failing carrier.
3. Eligibility re-verified at award — authority and insurance lapse between bid and award.
4. The award record is the evidence (BR-303, merged below), retained for the limitation period `[NEEDS INPUT: retention]`.
5. Every override named, reasoned, logged.

**DEC-LOCK-001 supersedes DEC-301's original framing.** A3's part recorded "Boss-supplied: lowest bid wins" as unre-litigated, with *Montgomery* changing only the gate's *status* from preference to precondition. Boss's actual decision, made the same day, goes further: eligibility is explicitly checked *first*, structurally, not merely recommended as a precondition — see DECISIONS.md, reproduced at §13.1.

| State | Trigger | To |
|---|---|---|
| `AUCTION_EXTENDED` | Anti-snipe (DEC-305) or thin-market re-open (DEC-310) | CLOSED |
| `AUCTION_CLOSED` | Close time or early close (DEC-308) | AWARD_PENDING · FAILED_NO_BIDS · FAILED_ALL_ABOVE_LIMIT |
| `AWARD_PENDING` | Winner determined, gate re-verified | ACCEPTED · DECLINED · LAPSED · VOIDED_INELIGIBLE |
| `AWARD_DECLINED`/`AWARD_LAPSED` | Refusal / expiry | Cascade (DEC-309) or re-auction |
| `AWARD_VOIDED_INELIGIBLE` | Gate fails on re-verification | Cascade or re-auction |
| `AUCTION_FAILED_NO_BIDS` | Zero bids at close | DEC-310 |
| `AUCTION_FAILED_ALL_ABOVE_LIMIT` | All bids above ceiling (DEC-306) | Re-auction · accept · fall back |

**Parameters that must be decided before this can operate — none invented, all `[NEEDS INPUT]`:** DEC-302 open vs. sealed bidding · DEC-303 standing best price vs. rank-only · DEC-304 auction duration · DEC-305 anti-snipe extension vs. hard close · DEC-306 reserve/ceiling price · **DEC-307 may the shipper decline the winner? — highest-consequence fork, same question as A1 BR-155 and EC-325 below; one decision, see §13.1** · DEC-308 shipper early close · DEC-309 decline cascade vs. re-auction · DEC-310 thin-market degradation · DEC-311 minimum decrement · DEC-312 overnight/weekend/holiday close.

| ID | Requirement | MoSCoW | Traces | Acceptance | Source |
|---|---|---|---|---|---|
| BR-301 | Only a carrier passing §8.2's gate for *this load* may bid; an ineligible price is never recorded or ranked. | Must | 002/006/007 | No audited auction ranks a gate-fail bid. | §4.1 above |
| BR-302 | Eligibility re-verified at award; failure → `AWARD_VOIDED_INELIGIBLE` before commitment. | Must | 006/007 | Gate result timestamped at/after close on every award. | §4.1 above |
| **BR-303** | **Merged requirement — see §8.9 for the reconciliation note; A8's BR-802 is retired into this ID.** The award record **is** the selection record: authority status, safety snapshot, insurance evidence, gate version, every bid with time, winner, rule applied, and every excluded bidder with the specific reason for exclusion. | Must | 006/007 | Reproducible from stored data alone; shows why the winner won *and* who was excluded, without live-source lookups. | 49 CFR 371 → §8.7 A7; §8.9 A8; *Montgomery* |
| BR-304 | Award to the lowest bid in the eligible pool, tie-broken per BR-305. | Must | 001 | Winner is the minimum-price eligible bid, else override logged. | **Boss** (DEC-LOCK-001) |
| BR-305 | Lowest-price ties resolve by a pre-published deterministic order. | Must | 001/006 | Same inputs, same winner; order published beforehand. | `[NEEDS INPUT: earliest / safety / on-time / random — safety is most defensible post-*Montgomery*]` |
| BR-306 | Any gate or award override attributed to a named person, with a reason. | Must | 006/007 | No override lacks identity and reason. | §4.1 above |
| BR-307 | A bid is a firm commitment to move the load at that price on stated terms until close. | Must | 002 | Accepted bid = rate-confirmation price → §8.6 A6 BR-600. | derived |
| BR-308 | Pre-close withdrawal only under stated policy; recorded against the bidder. | Should | 006 | Withdrawals on the bidder record → §8.2 A2/§8.9 A8. | `[NEEDS INPUT]` |
| BR-309 | Acceptance runs on a bounded window; expiry → `AWARD_LAPSED` → DEC-309. | Must | 002 | Nothing sits in AWARD_PENDING past the window. | `[NEEDS INPUT]` |
| BR-310 | Any post-award price change, including at the dock, recorded with requester, reason, amount, approver; unrecorded changes are unpayable. | Must | 001/005/006 | Settled = awarded bid plus approved changes. | RSK-003 (§14) |
| BR-311 | Re-trade frequency and magnitude tracked per carrier and lane, exposed to §8.2 A2 and §8.9 A8. | Must | 001/006 | Per-carrier re-trade rate queryable. | derived; consumes A1's BR-150–152 record |
| BR-312 | Bidder identity resolves to verified operating authority; bidding under one while operating under another is blocked. | Must | 006/007 | No award where identity and authority disagree. | → §8.2 A2 |
| BR-313 | Broker-authority-only bidder flagged at bid time; shipper sees it pre-award. | Must | 006/007 | Authority-type flag on every bid. | spine §1 |
| BR-314 | Bidder-visible data must not let bidders infer rivals' identity or pricing across auctions. | Should | 006 | No rival-identifying field. | → §8.7 A7 |
| BR-315 | Bid patterns monitored for rotation, coordinated withdrawal and price alignment on repeat lanes. | Should | 006/007 | Flags actioned or dismissed with reason. | Sherman §1 |
| BR-316 | Parties under common ownership or control may not bid twice in one auction. | Must | 006 | Related-entity second bids rejected. | derived |
| BR-317 | Shipper, operator and related parties may not bid. | Must | 001/006 | No bid traces to shipper or operator. | anti-shill |
| BR-318 | Where pool size or bid count falls below the competitive threshold, the auction is labelled; DEC-310 applies. | Must | 001/003 | Every award carries bid-count and pool size. | derived |

**Thin markets (§4.5, A3):** a one-bidder auction is not an auction — "lowest bid wins" against one bidder awards at the bidder's ask with no tension, arguably worse than a negotiated rate. DEC-310 remains fully open: award anyway / extend-reopen / ceiling-test-only / fall back to posted rate / escalate to human desk (§7.3 A9) — each with a stated trade-off, no default picked.

**Mechanism alternatives (§4.7, A3) — carried in full, options only, no recommendation overriding Boss's design:** lowest-bid-among-qualified (the §4.1 minimum, already DEC-LOCK-001) · best-value scoring (price + safety + on-time — the one at-scale precedent, Convoy, used this) · reserve/ceiling · second-price/Vickrey (flagged as unused in US freight, shill-objection risk) · hybrid assign-then-auction · instant-book at a posted rate (abandons the premise). `[ASSUMPTION — see §11 ASM-014]`: shippers will trade latency for price and record — flagged by A3 itself as "the premise the business rests on."

**Edge cases (30 total, EC-301–330) preserved in full — selected highest-consequence ones:** EC-304 (exactly one bid, §4.5) · EC-307 (tie where one bidder is worse on safety — **the former RSK-308 territory; see §14 for the assembler's decision**) · **EC-325 (shipper refuses the lowest qualified bidder — Boss's call, same question as DEC-307 and A1's BR-155, §13.1)**. Full 30-row register retained verbatim in the source part; not reproduced here to avoid duplicating 30 rows already fully itemised, cross-referenced at §19 Appendices.

**A3's own stated limits (carried forward, not softened):** four things need a person in the room, not analysis — how stringent the §4.1 gate must be to satisfy the client's insurer post-*Montgomery* (counsel + underwriter); whether shipper discretion at award suits that insurer (DEC-307); realistic duration against real pickup lead times (DEC-304 — a shipper); whether carriers bid against a binding rule with no deposit (ASM-014, §11).

### 8.4 Fulfilment: Pickup, Transit, Drop (A4, BR-400–409)

*Handover at the drop (acceptance/refusal, OS&D, BOL exception notation) is §8.5's; liability outcome and Carmack claim mechanics are §8.9's; charge amounts are §8.6's — this domain defines the event and its evidence, not the dollar figure.*

| ID | Requirement | MoSCoW | Traces | Source |
|---|---|---|---|---|
| **BR-400** | The platform shall require a structured pickup record — piece/pallet count, weight if declared, visible condition, seal number if sealed, and driver + shipper-representative acknowledgement — captured at the moment freight is tendered, before the shipment can transition to `PICKED_UP`. | Must | 004/006 | derived from §8.1 A1's proof-of-readiness finding + Carmack evidentiary structure. Acceptance: no shipment reaches `PICKED_UP` without a pickup record bearing both acknowledgements and a timestamp. |
| **BR-401** | The platform shall require a shipment status update at least every `[NEEDS INPUT: reporting interval]` while `IN_TRANSIT`, and shall itself flag — rather than silently tolerate — any interval in which no update is received. | Must | 002/004 | derived. Acceptance: every `IN_TRANSIT` shipment either has a status update within the interval, or carries an active "no update received" flag visible to platform and shipper. |
| **BR-402** | Where a carrier fails after pickup (breakdown beyond repair window, HOS exhaustion with no relief driver, impound, abandonment), the platform shall require a new custody event — including a fresh condition/count record — at the point freight physically transfers to a different truck or driver, regardless of whether the carrier of record changes. | Must | 004/006 | derived. Acceptance: every truck-to-truck transfer has its own timestamped custody record, distinct from the original pickup record. Not in scope: who arranges/pays for the transload (§8.6); a fast re-award for the remaining leg (§8.3); liability during the gap (§8.9). |
| **BR-403** | The platform shall capture, for every pickup and every drop, an arrival timestamp and a release/departure timestamp, independent of whether a charge is ultimately billed. | Should | 005 | derived, cross §8.6. Acceptance: every custody-relevant stop has both timestamps recorded or an explicit reason why one is missing. Feeds §8.6's detention accessorial directly. |
| BR-404 | Record `RETURN_TO_ORIGIN` as a distinct state, with its own custody event, when refused freight is brought back. | Must | 004 | derived |
| BR-405 | Record a `TRANSIT_EXCEPTION` sub-category on every occurrence, not a generic "delay" flag. | Must | 004/006 | derived |
| BR-406 | On a driver/equipment mismatch at pickup, shipment shall not proceed to loading until a resolution outcome (substitution confirmed vs. held) is recorded. | Must | 006 | derived, cross §8.2 BR-221/224, §8.9 |
| BR-407 | Live-load/drop-and-hook shall be captured at award and compared against pickup reality; mismatch recorded as an event. | Should | 005 | derived → §8.6 accessorial |
| BR-408 | Seal number, where sealed, recorded at pickup and re-verified at drop (§8.5 A5 executes; A4 supplies the origin value). | Should | 004 | derived |
| BR-409 | Repeated failure to provide a status update (BR-401) beyond a longer threshold becomes a flaggable pattern visible to §8.2's carrier scoring. | Could | 006 | derived |

**Pickup failure modes and in-transit exceptions (full tables preserved verbatim in the source part, 12 + 9 rows):** carrier no-show → `CARRIER_NO_SHOW`; wrong equipment → `PICKUP_REFUSED`; driver/truck mismatch → held pending verification, **signal to §8.2/§8.9, never a silent proceed**; freight not ready → `SHIPPER_NOT_READY`; HOS limit reached (a scheduled certainty on longer lanes, not an anomaly, per 49 CFR 395 — a legal constraint, not a business choice) → `TRANSIT_EXCEPTION` (HOS); breakdown, accident, weather/closure, reefer failure, cargo theft, roadside OOS order, impound, driver abandonment — each its own categorised `TRANSIT_EXCEPTION` sub-type per BR-405.

**Mid-trip reassignment (§6, A4) — genuinely hard, carried forward without simplification:** once freight is on a specific truck it is not a re-auctionable line item; moving it (a transload) is itself a custody event with its own condition-check, new BOL leg, and cost. Three sub-paths, none resolvable by A4 alone: relay (same carrier substitutes driver/truck — identity re-verification per BR-221 still applies), transload to a new carrier (a genuine second custody handover), or wait-for-repair (no custody event, detention-equivalent delay accrues). `[NEEDS INPUT: does the platform arrange mid-trip reassignment, or does the failed carrier remain contractually obligated to resolve it?]`

**A4's own honest limit:** actual call/message volume per load, how detention is currently evidenced (if at all), whether small carriers already run an ELD-linked app, and what fraction of loads today involve a driver who isn't who the dispatcher named — none of this is answerable from documents; it requires observing a real dispatch desk.

### 8.5 Consignee, Delivery Execution & Proof of Delivery (A5, BR-500–518)

*Transit-stage events and reroute (§8.4); Carmack liability allocation, claim adjudication, fraud penalties (§8.9); invoice amount, charge lines, factoring (§8.6); regulatory citation depth and privacy mechanics (§8.7); pickup-stage BOL creation and freight declaration (§8.1); consignee's formal RACI placement (§5, A9).*

**The structural problem this section exists to solve:** the consignee holds no account, accepted no terms, and has no relationship to the platform — yet their physical act (signing the BOL/delivery receipt clear or with exception) closes custody, triggers the invoice (§8.6), and supplies the evidence the Carmack claim path (§8.9) depends on. Every requirement below exists to make that act provable, attributable, and honest by construction, since it cannot be made contractual.

| ID | Requirement | MoSCoW | Traces | Acceptance condition | Source |
|---|---|---|---|---|---|
| BR-500 | A signed BOL/delivery receipt (the POD) is captured for every load before `POD_CAPTURED`; no shipment reaches `INVOICE_ISSUED` without a linked POD. | Must | 004/006 | State transition is blocked in the absence of the record. | derived, spine |
| BR-501 | POD records whether delivery was signed clear or with exception as a mandatory discrete field, distinct from freetext. | Must | 004/007 | Field cannot be blank; values are mutually exclusive and machine-readable, not inferred from prose. | derived; classification.md |
| BR-502 | "Received," "received in good condition," and "received and accepted" are kept as three separately capturable facts, never one implied status. | Must | 004 | Physical receipt can be recorded without implying condition or acceptance sign-off. | derived; task brief |
| BR-503 | Where delivered quantity/condition differs from the BOL, POD captures a structured OS&D notation: type (over/short/damage), quantity/unit, and whose count. **This is the canonical home for OS&D per §7.4's reconciliation — a notation, not a lifecycle state.** | Must | 004/007 | OS&D is a queryable structured field, not narrative-only. | derived |
| BR-504 | A distinct, time-stamped channel exists for damage discovered after signing (concealed damage), separate from at-delivery exception capture, routed to §8.9's claim path. | Must | 004 | Stored as its own linked record type; never overwrites the original exception field. | derived |
| BR-505 | A clear-signed POD is flagged as materially weakening a later claim relative to an exception-signed POD; a data-integrity flag, not a liability ruling (§8.9 adjudicates). | Must | 004/007 | BR-501's field is surfaced to §8.9's workflow without re-interpreting freetext. | derived |
| BR-506 | Full refusal is a distinct outcome (`DELIVERY_REFUSED`) with a required reason code; blocks invoice generation for that leg pending §8.4's custody-return decision and §8.6's accessorial handling. | Must | 004/005 | No delivery invoice line generates while in this state. | derived; spine states |
| BR-507 | Partial acceptance is capturable at line/unit level: accepted portion gets its own clear/exception POD; refused portion flagged separately for §8.4. | Must | 004/005 | Shipment supports split POD status, not one status for the whole load. | derived |
| BR-508 | Acceptance under protest or a disputed count is a POD notation distinct from ordinary exception, preserving both parties' stated counts. | Must | 004/007 | Schema stores carrier- and consignee-asserted counts separately when they diverge. | derived |
| BR-509 | Where no receiver is present or hours are closed, a distinct `DELIVERY_ATTEMPTED_NO_RECEIVER` event is recorded with arrival timestamp; custody stays with the carrier, no POD created. | Must | 004 | Exists as a first-class record feeding §8.4's redelivery logic. | derived; extends spine per §7.4 |
| BR-510 | A signature is accepted from whoever is physically present and authorized by the receiving facility, without requiring a platform account or pre-registration. | Must | 004/006 | POD capture succeeds for an unregistered signer; requirement is name/role capture, not identity verification. | derived; spine §1 |
| BR-511 | POD captures the signer's printed name and stated role/affiliation as given at the scene, retained permanently. | Must | 004/006 | Signer-name field is non-blank on every POD; absence is itself an exception. | derived |
| BR-512 | POD content, once captured, is provably fixed; any later addition/correction is a separately time-stamped addendum, never an overwrite. | Must | 004/006/007 | Retrieval shows original capture plus an ordered addendum trail. | derived |
| BR-513 | The system can demonstrate a POD corresponds to the freight and location actually delivered, without prescribing capture method. | Must | 004/006 | POD links to the shipment's declared freight (§8.1) and delivery location; missing linkage flagged incomplete. | derived; anti-fraud |
| BR-514 | The pickup-stage BOL and the signed delivery record are one continuous, linked document chain, not two independent records. | Must | 004 | Querying a POD returns unbroken lineage from pickup BOL to delivery signature. | derived |
| BR-515 | Arrival and departure time at the drop are captured as delivery-side events, independent of any charge calculation, feeding §8.4's exception classification and §8.6's detention/lumper model. | Must | 004/005 | Timestamps exist as queryable fields on every shipment reaching `AT_DROP`. | derived; scope split |
| BR-516 | Where a lumper service is engaged, that fact and any receipt offered are captured as a delivery-side event feeding §8.6's charge model; no fee amount or rule is defined here. | Should | 005 | Lumper-engaged flag and attached proof exist when applicable. | derived; scope split |
| BR-517 | Consignee contact data supplied by the shipper is used only for delivery notification and POD-evidentiary purposes, without requiring an account; the applicable privacy regime and consent mechanics → §8.7 A7. | Must | 007 | Consignee data fields scoped to delivery + evidentiary use only; no secondary-use field without an A7-defined basis. | derived; spine §0 |
| BR-518 | POD records (incl. exceptions and addenda) are retained for a period aligned to Carmack claim/suit exposure. | Must | 004/007 | A defined, non-zero, cited retention value exists before go-live. | `[NEEDS INPUT: exact retention duration — §8.7 A7 to confirm against statutory minimums]` |

**Refusal & partial-acceptance outcome matrix (full 6-row table preserved in source):** full refusal no damage → `DELIVERY_REFUSED`, no delivery line, accessorial may apply (§8.4/§8.6); full refusal with damage → `DELIVERY_REFUSED` + OS&D, line held pending claim (§8.4/§8.6/§8.9); partial acceptance → split POD, prorated invoice, remainder held; acceptance under protest → completes, flagged for review (§8.6/§8.9); consignee absent → `DELIVERY_ATTEMPTED_NO_RECEIVER`, no invoice trigger until a POD exists.

**Who is allowed to sign:** the person at the dock is rarely a corporate officer with authority to bind the consignee. Requiring verified authority would stop deliveries completing in the real world. BR-510/511 capture identity-as-stated rather than identity-as-verified, leaving "who actually signed" a §8.9 claim-time weighing question, not a platform-time blocker.

### 8.6 Money, Invoicing & Settlement (A6, BR-600–614)

*Regulatory licensing this money movement may trigger is §8.7's; unit economics/take-rate strategy is §17's (A10); claim adjudication outcomes are §8.9's.*

**§1. Who invoices whom — the load-bearing open decision, and half of the five-times-asked fork at §3.4.** `[NEEDS INPUT: which of the three models does the client intend?]`

| Model | Structure | Platform requires | Consequence |
|---|---|---|---|
| **A — Pass-through software** | Carrier invoices shipper directly; platform never touches the freight charge | No broker authority; no BMC-84 bond (confirm with §8.7) | Cannot monetize a spread; revenue is a listing/subscription/transaction fee. No credit risk, no factoring exposure on the freight leg — but weak control over collection quality |
| **B — Broker of record (buy/sell)** | Platform contracts separately with shipper and carrier, invoices the shipper the sell rate, pays the carrier the buy rate, keeps the spread | FMCSA property broker authority, BMC-84 bond / BMC-85 trust, BOC-3 (§8.7 owns citation) — plus working capital or a financing facility | Closest fit to the stated auction → invoice flow. Platform carries shipper credit risk, owns factoring/NOA handling, can offer quick pay. Highest capital and compliance burden |
| **C — Commission-only marketplace** | Carrier invoices shipper directly; platform separately bills its own commission/fee | May still trigger money-transmission review if funds pass through even transiently (→ §8.7) | Capital-light like A, monetizable like B, but not party of record on the freight contract — weaker leverage when an invoice is disputed |

| ID | Requirement | MoSCoW | Traces | Source | Acceptance |
|---|---|---|---|---|---|
| BR-600 | Generate a rate confirmation at `AWARD_ACCEPTED` carrying the winning bid as base linehaul rate, the fuel-surcharge method, and the applicable accessorial rate table, requiring carrier acknowledgement before `PICKUP_SCHEDULED`. | Must | 005/002 | derived from spine §3 + intake happy path | No load reaches `PICKUP_SCHEDULED` without an acknowledged rate confirmation on file. |
| BR-601 | Final invoice amount = rate-confirmation base rate + verified accessorials actually triggered + fuel surcharge per the confirmed method − any short-pay/OS&D deduction pending an §8.9 claim. The bid alone is never the invoice. | Must | 005 | task mandate (§8.4/§8.5 define triggering events; this domain defines charge treatment) | Invoice line-item total reconciles to rate confirmation + accessorial log. |
| BR-602 | Every accessorial line shall carry documentary evidence (timestamp log, signed BOL exception, lumper receipt) before moving from `INVOICE_ISSUED` to `INVOICE_FINALISED`. | Must | 005 | derived | No accessorial line finalises without an attached evidence artifact. |
| BR-603 | Allow partial settlement: undisputed lines pay on the standard cycle while disputed lines stay `HELD`, rather than blocking the whole invoice on one open item. | Must | 005 | A6 challenge, accepted into spine §3 | A load with one OS&D line and nine clean lines settles the nine without waiting on the one. |
| BR-604 | A short-pay or deduction against a finalised invoice shall generate a credit note referencing the specific invoice line and linked §8.9 claim/dispute ID; never a silent net. | Must | 005/006 | derived — unexplained deductions are a leading carrier-trust complaint in this market | Every deduction has a credit note with a claim-ID reference. |
| BR-605 | In Model B, carrier payable and shipper receivable shall be tracked as two independently timed obligations against the same finalised invoice. | Should | 005 | derived from broker buy/sell structure | Carrier payment status is queryable independent of shipper collection status. |
| BR-606 | Capture, at carrier onboarding and per-load, whether the receivable is factored, and if so the factor's name and remit-to instructions, sourced from a signed NOA document, never from carrier self-declaration alone. | Must | 005/006 | spine §0 money-movement row | No carrier payment issues without an NOA-status check on the paying record. |
| BR-607 | Only one active NOA per carrier is honored at a time; a new NOA is accepted only against a signed Release from the prior factor or documented NOA expiry. | Must | 006 | derived — double-factoring is a known US freight fraud pattern | — |
| BR-608 | Where a valid NOA is on file, all payable amounts route to the factor's remit-to instructions, not the carrier's own bank details, with no manual override absent a compliance sign-off. | Must | 005 | derived | A payment run for a factored carrier routes 100% to the factor of record. |
| BR-609 | Offer quick pay as an elective, per-invoice or per-carrier-tier option, funded from platform working capital or a third-party invoice-financing partner. | Should | 003/005 | spine money-movement row + industry convention `[verify — cite a factoring/quick-pay industry source before build]` | — |
| BR-610 | Quick pay is disabled by default on any invoice carrying a held/disputed line. | Should | 006 | derived | Quick-pay election is blocked while any line is `HELD`. |
| BR-611 | Standard payment terms to shippers and standard payout timing to carriers shall each be an explicit, documented figure, never left implicit. | Must | 005 | `[NEEDS INPUT]` | Rate confirmation and shipper contract both state a term in days. |
| BR-612 | Collect a completed Form W-9 from every US carrier before its first payment. | Must | 007 | IRS Form W-9 instructions | No first payment issues without a W-9 on file. Consumes §8.2 BR-206's collection. |
| BR-613 | Track cumulative annual payments per carrier and generate Form 1099-NEC data for carriers meeting the IRS reporting threshold. | Must | 007 | IRS Form 1099-NEC instructions `[verify current threshold before build]` | — |
| BR-614 | The platform-revenue mechanism (subscription, listing fee, or buy/sell spread) is set by the §1 model choice and shall be stated explicitly on every invoice or billing statement. | Must | 005 | derived | An invoice states, unambiguously, what the platform charged and to whom. |

**Accessorial charge treatment (full table, cross-references added by the assembler):**

| Accessorial | Triggering event (owner) | Charge treatment | Cross-ref |
|---|---|---|---|
| Detention | Free time exceeded at pickup/drop | Per-hour rate beyond `[NEEDS INPUT: free-time hours]`, requires timestamped arrival/departure evidence | ↔ §8.4 A4 BR-403 (timestamps); ↔ §8.1 A1 BR-143 |
| TONU | `SHIPPER_NOT_READY` / `CANCELLED_BY_SHIPPER` post-dispatch | Flat fee `[NEEDS INPUT]`, no linehaul charge | **↔ §8.1 A1 BR-142/143 — trigger defined there, amount defined here; both sides now explicitly cross-reference each other per the task brief's requirement.** |
| Layover | Overnight hold not attributable to carrier | Flat per-night fee `[NEEDS INPUT]` | ↔ §8.4 A4 |
| Lumper fee | Third-party load/unload labor paid by carrier | Reimbursed at receipted cost, not estimated | ↔ §8.5 A5 BR-516 |
| Driver assist | Carrier performs load/unload beyond standard | Flat or hourly `[NEEDS INPUT]` | ↔ §8.4/§8.5 |
| Stop-off | Additional pickup/drop point | Per-stop fee `[NEEDS INPUT]` | ↔ §8.1 A1 (out of scope R1, §4) |
| Redelivery / reconsignment | `DELIVERY_REFUSED` or destination change | Additional linehaul segment + admin fee | ↔ §8.5 A5 |
| Fuel surcharge (FSC) | Applies to every load | Indexed method `[NEEDS INPUT: index + update cadence]` on rate confirmation, not renegotiable post-award | — |
| OS&D deduction | Shortage/damage at delivery, adjudicated | Held against `INVOICE_ISSUED`, released or finalised only on §8.9 claim outcome | ↔ §8.5 A5 BR-503; §8.9 A8 |

### 8.7 Regulatory & Compliance Surface — USA (A7, BR-701–720)

*General regulatory awareness, not legal advice; certifies nothing. §8.7.9 = what only counsel resolves. §8.9 (A8) owns liability allocation; §8.2 (A2) owns vetting execution.*

**Threshold question — what is the client? (Half of the five-times-asked fork, §3.4.)** 49 U.S.C. §13102: arranging transport of property for compensation is brokerage; operating the truck is motor carriage — separate authorities. `[NEEDS INPUT: Does the client hold FMCSA broker authority, carrier authority, both, or neither — and will the platform itself arrange transport for compensation, or be software run by a third party holding the authority?]`

| Answer | Consequence |
|---|---|
| **A — licensed property broker** | Part 371/bond/BOC-3/UCR surface is the client's, as is negligent-selection exposure. BR-701–708 become Must. |
| **B — carrier bidding its own loads** | Conflict of interest in an auction it runs; Parts 387/391/395/382 attach directly. Neutrality disclosure → §8.3, §17. |
| **C — software vendor, tenant holds authority** | Duties sit with the tenant; platform still stores the evidence they are judged on. |
| **D — neither, yet sets price and awards** | The classic unauthorised-brokerage fact pattern. Counsel question, not design question. |

| ID | Requirement | MoSCoW | Acceptance | Source |
|---|---|---|---|---|
| BR-701 | Operator status (broker/carrier/vendor) recorded as a documented decision with authority evidence before any load is published. | Must | No load reaches PUBLISHED while status unset. | §7.1 above |
| BR-702 | Where broker authority held, current bond/trust + BOC-3 evidence held with pre-expiry alerting. | Must | Expiry simulation alerts operator and blocks new awards. | 387.307; Pt 366 |
| BR-703 | Six broker-record elements captured per brokered load, retained ≥3 yrs. | Must | 20-load sample: all six present; retention job proves horizon. | 371.3 |
| BR-704 | Each party can obtain that transaction's record via a defined path; request + response logged. | Must | A shipper and a carrier each request one; both served, both logged. | 371.3 |
| BR-705 | Authority status + Part 387 insurance evaluated at award, not only onboarding, and frozen into the award record. | Must | Award replays the exact state used; later source changes do not alter it. | 387.9; feeds §8.3's merged BR-303 |
| BR-706 | Award record preserves safety/eligibility data at award, criteria applied, any override identity. | Must | Decision basis reproducible from stored data alone. | *Montgomery*; **this is the same content requirement as the merged BR-303 (§8.3) — presented here as the regulatory citation for it, not a separate artifact** |
| BR-707 | Per-carrier attestation: CDL validity, Clearinghouse currency, D&A programme — dated, attributable — with no storage of Clearinghouse or D&A results. | Must | Attestation attributable; no field holds a test result. | 382.701; 391.51 |
| BR-708 | Pickup/delivery windows checked for HOS feasibility; infeasible ones flagged pre-auction. | Should | Infeasible window raises pre-publication flag; flag + response logged. | 395.3 |
| BR-709 | No ELD/HOS data ingested, stored or displayed absent documented lawful basis + retention rule. | Must | No such field exists without a recorded authorising decision. | — |
| BR-710 | Re-brokering prohibited, or only on recorded written shipper consent; party taking possession recorded and reconciled against awarded carrier. | Must | Mismatch raises exception before departure; consent retrievable. | consumes §8.2 BR-221/224 |
| BR-711 | Declared value + released-value term captured at load creation pre-bid, immutable once the auction opens. | Must | Post-AUCTION_OPEN edit rejected and logged. | §14706 |
| BR-712 | Delivery record captures clear-vs-exception, exception text, signing party. | Must | No shipment reaches POD_CAPTURED without it. | Carmack; = §8.5 A5 BR-501, cited here as the regulatory basis |
| BR-713 | Claim and suit windows recorded per shipment from the governing document; no platform term shortens them. | Must | Displayed dates match the governing document. | §14706(e); → §8.9 A8 BR-808 |
| BR-714 | Notice at/before collection to every individual whose data is collected, including an unregistered consignee — categories, purposes, retention, rights. | Must | Unregistered consignee reaches notice + rights path from the delivery message alone. | §7.7 below; consumed by §8.5 A5 BR-517 |
| BR-715 | Personal data retained per explicit per-class schedule separating rule-fixed from business-decided periods. | Must | Every personal-data class maps to a §7.7 row. | §7.7 below |
| BR-716 | Rights requests (access, deletion, correction, opt-out) received, verified, actioned, logged within the requester's state period. | Must | Per state, end-to-end test yields a logged, timed response. | 20 state statutes 2026 `[verify per state]` |
| BR-717 | Competitor bid values/identities not disclosed beyond what a documented decision authorises. | Must | No bidder-facing view exposes another bid amount or identity. | 15 U.S.C. §1; = §8.3 A3 BR-314 |
| BR-718 | Repeat-lane bidding monitored for rotation, clustering, withdrawal signatures; detections routed to a named reviewer. | Should | Seeded rotation pattern detected and routed. | = §8.3 A3 BR-315 |
| BR-719 | Hazmat loads flagged at creation, blocked from award absent authority, endorsement, applicable Part 387 limit. | Must (if in scope) | Flagged load not awardable without the evidence. | 387.9; Pt 172; consumes §8.1 A1 BR-118 |
| BR-720 | Each party's regulatory obligations stated in version-controlled terms, acceptance recorded per version. | Must | Accepted version + timestamp retrievable per user. | derived |

**Money movement — escalation, not analysis (§7.4, the second half of the five-times-asked fork, §3.4).** A7 will not opine on whether the platform is a money transmitter or which state licences it needs — federal MSB status (31 CFR 1010.100(ff)(5)) and state money-transmitter licensing are fact-specific, counsel questions. Fork preserved: **M1** shipper pays carrier direct, platform bills a fee (weakest settlement guarantee) · **M2** funds via licensed processor/bank, platform never holds (vendor dependency) · **M3** platform holds and disburses (raises federal MSB + state MTL — highest cost). `[NEEDS INPUT: M1, M2 or M3? §8.6 A6 cannot finalise settlement requirements without it.]`

**Retention by data class (§7.7) — no "Open" period filled with an invented number:**

| Class | Period | Fixed by | Holder |
|---|---|---|---|
| Broker transaction record | ≥3 yrs | 371.3 | Platform-as-broker |
| Driver RODS / ELD support | ≥6 months | 395.8(k) | Carrier, not platform |
| Driver qualification file | Employment +3 yrs | 391.51 | Carrier |
| D&A testing records | To 5 yrs by type | 382.401 | Carrier |
| BOL / POD / exception notation | **Open** | Not fixed; claim/suit horizon | Platform + carrier |
| Bid history, award decision basis | **Open** | No rule found; litigation-evidence value argues long | Platform |
| Consignee contact data | **Open** | State statutes require a stated purpose-limited period, not a number | Platform |
| Financial/settlement records | **Open** → §8.6 A6 | Tax/reporting rules | Platform |

**§7.9 Counsel handoff (10 items, preserved in full):** (1) whether the design constitutes property brokerage and which authority to obtain; (2) post-*Montgomery* negligent-selection exposure of a lowest-bid award and what selection standard is defensible; (3) enforceability of a waiver of the 371.3 review right; (4) whether platform terms may address Carmack claim/suit windows; (5) money transmission — federal MSB status and state licensing, no M3 without it; (6) state privacy applicability, consignee notice for a non-registered party; (7) antitrust review of bid-information disclosure; (8) re-brokering consent terms and remedies; (9) retention periods for every "Open" class in §7.7; (10) insurance programme design.

**CHALLENGE, carried forward and acted on:** A7's original text argued spine §4's "surfaced as a requirement or risk" framing for negligent selection is understated post-*Montgomery* — it is a precondition on the award mechanism, not a risk line. **The assembler's decision on this challenge, and its direct consequence for A3's RSK-308, is recorded at §14.**

### 8.8 Stakeholders, Roles & Permissions, Platform Operations (A9, BR-900–914)

*References, does not restate: eligibility criteria (§8.2), auction/bid mechanics (§8.3), custody execution (§8.4), delivery/POD content (§8.5), payment mechanics (§8.6), regulatory citation (§8.7), liability adjudication (§8.9), business model/unit economics (§17, A10). Stakeholder map and governance table already presented at §5; this subsection carries the roles/permissions requirements and the operational desk model.*

**A carrier with several trucks, a dispatcher, and multiple drivers is the normal case, not an advanced one — so is a shipper with several sites and several people posting loads. The role model is built for that from day one.**

| ID | Requirement | Traces to | Priority | Source | Acceptance |
|---|---|---|---|---|---|
| BR-900 | Support one carrier account representing multiple trucks and multiple drivers, with one or more dispatcher users holding individually grantable permissions distinct from the account owner. | 003/006 | Must | derived (spine §1/§2 + Boss's "asset trucks") | Given a carrier account with 3 trucks and 2 dispatchers, when the owner grants "bid" to Dispatcher A only, then Dispatcher B cannot submit a bid on that account's behalf. |
| BR-901 | Support one shipper account representing multiple sites/locations and multiple authorized posting users. | 002 | Must | derived; resolves §8.1 A1 BR-101 | Given a shipper account with 2 site posters, when Poster A publishes a load, then Poster B can view it but cannot edit or cancel it without an admin grant. |
| BR-902 | Accepting an award shall require a permission distinct from bidding, held by the account owner or an explicitly granted user. | 006/007 | Must | derived from §2 negligent-selection collision + carrier org reality | Given a dispatcher holds bid-only permission, when they attempt to accept an award, then the system rejects the action. |
| BR-903 | A driver's signature at delivery shall be treated as binding on the carrier account holding the award, regardless of whether the driver holds an individual platform login. | 004 | Must | `[ASSUMPTION — see §11 ASM-032]` | Given a driver without platform credentials signs a delivery receipt, when POD is captured, then it is recorded against the carrier account, not against an unlinked individual. |
| BR-904 | Shipment cancellation shall be restricted to the original poster or a shipper-account admin. | 001 | Must | derived | → §8.1 A1 owns cancellation consequences; this covers authority only. |
| BR-905 | Declining or cancelling an accepted award shall require the same authority tier as accepting it (BR-902). | 006 | Must | derived | → §8.3 A3 owns the resulting state (`AWARD_DECLINED`); this covers who may trigger it. |
| BR-906 | Provide a path for consignee-observed exception information (damage, shortage) to enter the claim record without requiring a consignee account — via driver exception notation, dock contact, or shipper relay. | 004/006 | Must | derived from spine §0 (Carmack) + §1 (no consignee signup) | `[NEEDS INPUT: does the client want a lightweight, account-free consignee input link, or purely relay-through-shipper?]` — **overlaps with §8.5 A5 BR-504's concealed-damage channel and §8.9 A8 BR-807's claim intake; not a conflict, three domains converging on the same requirement from three angles, consolidated here as the account/authority layer over A5's content layer and A8's adjudication layer.** |
| BR-907 | Waiving a charge or approving a claim payout shall require a platform-ops role distinct from any shipper, carrier, or dispatcher role. | 005/006 | Must | derived | Given a carrier requests a charge waiver on its own invoice, when the request is processed, then approval requires a platform-ops actor, logged separately from the requester. |
| BR-908 | Approving a carrier onto the platform shall require action by a platform-ops role; not a fully automated pass even where every data check clears. | 006/007 | Must | `[ASSUMPTION — see §11 ASM-033]` | Given a new carrier passes every automated vetting check (→ §8.2), when onboarding completes, then the account remains non-bidding until a platform-ops actor records an explicit approval. |
| BR-909 | Represent a "payee of record" attribute on a carrier account, distinct from the carrier itself, settable only by the carrier account owner, to reflect a Notice of Assignment on file. | 005 | Must | derived; → §8.6 A6 owns payment mechanics | Given a dispatcher attempts to change payee-of-record, when submitted, then the system rejects it. Consistent with §8.6 A6 BR-606–608. |
| BR-910 | Represent which specific driver and truck are executing an awarded load, distinct from which carrier account won it. | 004 | Must | derived; → §8.2/§8.4 own the operational record | Given an award is accepted, when a driver/truck is assigned, then HOS, custody, and POD-signing responsibility trace to that individual driver record. |
| BR-911 | Where a shipper account has multiple posting users, state-change notifications for a load shall route to the specific user who posted it. | 002 | Should | derived | Given Poster A publishes a load, when it is awarded, then Poster A (not only the account admin) is notified. |
| BR-912 | Notifications addressed to the consignee shall be delivered through a contact channel supplied at load creation, not through an in-app mechanism, and the platform shall record that delivery/read confirmation is unavailable for this channel. | 004/006 | Must | derived, spine §1 "does not sign up" | Given a consignee contact is supplied at load creation, when a pickup or exception notification fires, then it is sent out-of-band and the record shows "delivery status unknown," not a false confirmed-read state. |
| BR-913 | Every exception state enumerated in §7.4's canonical table shall resolve to a defined platform-ops role accountable for it. | 006 | Must | Boss's mandate ("nothing may be missed") extended to operations | See §8.8 operations table below — every row has a "who" column populated or flagged `[NEEDS INPUT]`. |
| BR-914 | Driver-facing support shall be available in both English and Spanish at minimum. | 004/006 | Must | `[ASSUMPTION — see §11 ASM-034]` | Given a driver requests support in Spanish, when contact is made, then resolution proceeds without requiring the driver to switch to English. |

**Platform Operations — the desk behind the software (full table, referenced at §7.3):** carrier vetting/onboarding review, continuous re-verification, exception desk, claims intake, fraud review, dispute-resolution ops, collections, after-hours coverage. **No coverage model, staffing size, or SLA is specified for any of these — a client operating decision this BRD cannot invent numbers for.**

**Notification matrix (13-row table, preserved in source part):** every spine §3 state change mapped to who is notified, told what, and via which channel — with the explicit honest note that the consignee receives operational notifications (pickup window, ETA, exceptions) through an out-of-band contact channel, **never** through platform-of-record notices about bids, awards, or invoices, because it has no account to receive them into.

**A9's own stated limits:** naming the client-side approvers (§5.2), sizing the platform-ops function or its after-hours coverage, or resolving the claims-desk/insurer-adjuster authority split — these need the client's own org chart and risk appetite, not more drafting.

### 8.9 Liability, Trust, Fraud and Disputes (A8, BR-801–821) — includes the assembler's merge and rewrite

*Owns: custody-chain liability, cargo loss/damage/theft/shortage, Carmack claims, insurance, ratings, fraud, disputes, penalties. Not here: regulatory citation depth (§8.7), auction mechanics (§8.3), invoicing mechanics (§8.6). Not legal advice — citations exist so counsel can verify them. `[inference]` = analysis, not a legal conclusion.*

**8.9.1 The platform's own legal position governs everything below — `DEC-801` `[NEEDS INPUT]`.** Under Carmack the motor carrier bears cargo liability; a property broker arranges carriage and generally does not, but is exposed in tort for negligent selection. Three positions, none chosen: **P1** licensed broker (cargo-loss exposure generally low, selection-tort exposure high and now nationwide) · **P2** carrier/dual authority (directly liable, full load value; heaviest insurance burden) · **P3** software vendor to brokers (cheapest legally, but strained if the platform's own algorithm awards `[inference]`). **This is the same fork as §3.4/§13.1's regulatory-status question — not a fourth framing, the same one, and is treated as such at §13.1.**

**8.9.3 Negligent selection — the defining exposure for this product.** *Montgomery v. Caribe Transport II, LLC* (14 May 2026, unanimous) held the FAAAA safety exception encompasses state-law negligent-hiring claims against brokers — broker selection exposure is no longer circuit-dependent. Awarding strictly to the lowest bid with FMCSA safety data available and unused is the fact pattern plaintiffs' counsel look for after a serious crash `[inference]`. The defence is a contemporaneous record of why this carrier was fit.

**8.9.4 Carmack claims path, end to end:** filing floor not under 9 months from delivery; suit floor not under 2 years from written disallowance (§14706(e)(1)); valid claim per 49 CFR §370.3; acknowledge in writing within 30 days (§370.5); pay/decline/firm-compromise within 120 days, then status every 60 days (§370.9). `[NEEDS INPUT: may freight charges be offset against an open cargo claim? → §8.6 A6 — genuinely unresolved on both sides, not an orphan, see §8.12.]`

**8.9.6 Insurance structure — the verified gap most people miss:** FMCSA eliminated the cargo-insurance filing requirement for most for-hire general-freight carriers effective 21 March 2011 (household-goods carriers/forwarders remain subject, 75 FR 35367). A carrier can hold valid authority and Part 387 auto-liability cover and carry **zero** cargo insurance — cargo cover here is a commercial eligibility requirement the platform imposes, or it is absent.

**8.9.7 Fraud typologies (FR-1 through FR-14, full table preserved in source):** double brokering, carrier identity theft, fictitious pickup, driver absconding, strategic theft, forged POD, shipper-contact collusion, bid rigging, shill/spoiler bidding, phantom-load document harvesting, inflated accessorial claims, payment redirect/fake NOA, inflated cargo claims, rating manipulation. Verisk CargoNet: 2025 US/Canada cargo-theft losses ≈$725M, up ~60% on 2024. **Price-only award structurally selects for FR-1, FR-2, FR-3, FR-9** `[inference]` — the lowest bidder can be lowest precisely because it never intends to perform the movement it priced.

**8.9.9 Ratings — the tension flagged to §8.3:** a rating system on top of a pure lowest-price mechanism changes no award outcome. It becomes real only if it gates eligibility (§8.2), enters the award function (§8.3), or triggers suspension (here). §8.3 must decide and state which — BR-816 forces the decision, does not make it.

**8.9.10 Penalties, suspension, removal:** graduated — warning → bid restriction → suspension → removal, each with recorded ground, evidence, appeal. Suspension stops new bids/awards but does not strand freight already in a truck by default; on cargo-integrity grounds (FR-1/2/3/4) a recovery protocol triggers instead, and access is not simply cut.

| ID | Requirement | MoSCoW | Traces | Acceptance | Source |
|---|---|---|---|---|---|
| BR-801 | Record contracting carrier, broker, and who bears cargo liability, per `DEC-801`. | Must | 006/007 | No shipment reaches AWARDED without the liable party named. | spine §0 |
| **BR-802 — RETIRED, merged into §8.3's BR-303.** | Capture at award an immutable selection record: authority status, safety snapshot, insurance evidence, gate applied, bidders excluded and why, basis of award. | — | 006/007 | — | **Merge reasoning:** A3 explicitly wrote its BR-303 as "the award record **is** A8's selection record — one requirement, not two" and named A8's BR-802 by ID. Cross-checked against A8's actual BR-802 text above: content matches field-for-field (authority status, safety snapshot, insurance evidence, gate applied/version, exclusions with reasons). A3's BR-303 additionally specifies "every bid with time, winner, rule" — a superset, not a conflict. **Verdict: A3's merge claim is correct; content is what A8 asked for.** Canonical ID is BR-303 (§8.3) because the award-time artifact is generated by the auction domain; A8 consumes it as its own selection-record requirement by reference, not by restating it. |
| BR-803 | Refuse award to any bidder failing the eligibility gate, regardless of price. | Must | 006 | No award where gate status was FAIL. | derived; = §8.3 A3 BR-301/302 |
| BR-804 | Re-verify authority and insurance at award and again at pickup; source COIs from the insurer or agent, contracting entity as certificate holder with cancellation notice. | Must | 006 | No pickup on stale verification; carrier-supplied PDFs never suffice. | §8.6 (this domain), FR-2 |
| BR-805 | Require cargo cover as commercial eligibility; record limit against declared value. | Must | 004/006 | Loads over the carrier's limit flag pre-award. | 75 FR 35367 `[verify]` |
| **BR-806** | **Rewritten by the assembler — see reasoning below.** On receipt of §8.2's BR-221/224 mismatch signal (driver/tractor/MC at pickup does not match the awarded tuple, or an undisclosed post-award substitution), open a fraud-classification case within the same shift, distinguishing double-brokering (undisclosed substitution, FR-1) from carrier identity theft (impostor on a real MC's credentials, FR-2) from a disclosed, re-vetted substitution (no case opened). | Must | 004/006 | A BR-221/224 signal produces a classified case outcome, not a raw re-verification — the verification act itself already happened at §8.2. | FR-1/2/3; consumes §8.2 BR-221/224 |
| BR-807 | Provide claim intake capturing §370.3 minimum content, timestamped, and track the 30/120/60-day obligations with overdue escalation. | Must | 004/007 | No submission without shipment identity, liability assertion, amount; every open claim shows its next obligation date. | §370.3/.5/.9 |
| BR-808 | Never enforce under 9 months to file or 2 years to sue from written disallowance; issue and retain a dated written disallowance on decline. | Must | 004/007 | Floors not configurable downward; every decline retains a notice. | §14706(e)(1) |
| BR-809 | Bind every claim to origin BOL and the clear/exception delivery signature. | Must | 004 | No adjudication without both, or their absence noted. | → §8.4 A4, §8.5 A5 |
| BR-810 | Where released value is offered, present ≥2 priced liability levels at load creation, record the choice, print it on the BOL pre-pickup. | Should | 004/007 | Every limited load has a pre-dispatch recorded choice. | *Hughes Aircraft* `[verify]` |
| BR-811 | Separate freight from money disputes at intake — distinct evidence, owners, targets. | Must | 004/005 | No queue holds both types. | `[NEEDS INPUT: targets]` |
| BR-812 | Verify out-of-band changes to banking, remit-to, email domain or factoring before payment or award. | Must | 005/006 | Zero payments on an unverified change. | FR-2/12 → §8.6 A6 |
| BR-813 | Restrict credential downloads to counterparties on an awarded load. | Should | 006 | No bulk credential retrieval without an award. | FR-10 |
| BR-814 | Detect award-pattern anomalies: lane rotation, single-contact win concentration, implausible underbidding. | Should | 006 | Named patterns raise a reviewable alert. | FR-7/8/9 → §8.3 A3, §8.7 A7 |
| BR-815 | Permit ratings only from a party to a completed shipment; separate objective events from stars. | Must | 006 | No rating without a matching completed shipment. | FR-14 |
| BR-816 | State whether reputation gates eligibility, enters award, or is informational only. | Must | 001/006 | Decision documented; mechanism matches it. | §8.9.9 → §8.3 A3 |
| BR-817 | Apply graduated enforcement with recorded ground, evidence, appeal route. | Must | 006 | Every action has all four fields populated. | §8.9.10 |
| BR-818 | Suspension halts new bids/awards without stranding in-flight freight, except on cargo-integrity grounds where the recovery protocol applies. | Must | 004/006 | No suspension costs a live load its visibility or custody accountability. | §8.9.10 |
| BR-819 | Preserve vetting/selection/communication records of suspended or removed parties; litigation hold on serious injury, fatality, theft, claim. | Must | 007 | Removal never deletes selection evidence; holds immutable and exportable. | §8.9.3 |
| BR-820 | Notify shipper, consignee, insurer on loss, theft, non-delivery, refusal, with recorded time. | Must | 004 | All such events produce timestamped notifications. | → §8.5 A5, §8.8 A9 |
| BR-821 | State, per counsel, whether freight charges may be offset against an open cargo claim. | Must | 005 | Rule documented and applied consistently. | `[NEEDS INPUT]` → §8.6 A6 |

**BR-806 rewrite reasoning (task requirement 3, second item):** A2's original text explicitly named this exact split: "A2 owns identity/eligibility: who is contractually permitted to move the freight, and whether the truck/driver that shows up matches the award. A8 owns fraud typology and consequence on this evidence." A8's original BR-806 text read "Verify at pickup that driver, tractor, MC match the awarded carrier; open a case on mismatch" — this restates the *verification act* A2's BR-221 already owns and performs, rather than consuming its output. Left unedited, two domains would both claim to "verify" the same physical fact at pickup, with no clear system-of-record for which one actually runs the check. The rewrite above removes the re-verification clause entirely from BR-806 and starts it from "on receipt of the BR-221/224 signal" — A2 now unambiguously owns the fact-finding act (BR-221/224, BR-225 explicitly forbids A2 from classifying), and A8 unambiguously owns everything downstream of that fact (classification, case, consequence). No content is lost — A8's acceptance condition changes from "mismatch blocks pickup, opens a case" (which duplicated A4's BR-406 blocking behaviour too) to "a classified case outcome," which is the analytical step only A8 was ever positioned to own.

**8.9.13 CHALLENGE, carried forward: the spine's exception-state list understates trust states.** `FRAUD_SUSPECTED`, `RECOVERY`, `CARRIER_SUSPENDED_IN_FLIGHT` — all three accepted into the canonical table at §7.4.

**What this domain cannot do:** resolve `DEC-801` (client and counsel); confirm what the client's policies actually exclude (needs the wordings and an insurance broker); decide whether charges may be offset against an open claim (counsel); read the *Montgomery* slip opinion in full before BR-303/706 is built (counsel).

### 8.10 Platform Data Assets as Product Capability (A11, BR-1100–1109)

*Not here: carrier eligibility (§8.2), bid/award mechanics (§8.3), fulfilment events (§8.4), liability/fraud (§8.9), licensing legal clearance (§8.11, A12 — referenced only).*

**What this asset actually is:** seven verified layers from the client's existing `~/Documents/truck-intel` platform (DEC-LOCK-002). A reference dataset, not a live operational feed. Nothing here substitutes for a carrier's own safety record (§8.2/§8.7 own that), and nothing here is a rate quote.

| # | Capability | Verdict | **A12 licence dependency — added by the assembler per the task brief's explicit instruction** |
|---|---|---|---|
| 1 | Route feasibility at auction time (BR-1100–1102) | **Strong** — closest layer to national government-source coverage (NTAD/FHWA) | **None.** NTAD truck routes, bridges, tunnels are US-government works, unrestricted public use (§8.11 row 1–3). Safe to build on without a licence decision pending. |
| 2 | Fuel-cost floor / below-cost signal (BR-1103–1105) | **Moderate** — real signal, badly named if oversold | **None**, on the client's own EIA API key (§8.11 row 5, BR-1208). Not blocked. |
| 3 | Breakdown recovery / mechanic directory (BR-1106) | **Moderate** — shortens search, doesn't solve the problem | **None** as described — `core.mechanic_shops` is Overture-sourced, permissive licence (§8.11 row 13), not the ODbL `osm.truck_repair` table. Safe as scoped. |
| 4 | HOS-aware transit planning / parking (BR-1108) | **Weak-moderate** — advisory only | **Yes — partially blocked.** The federal `core.parking_sites` component (1,915 rows, NTAD) is safe; the `osm.rest_areas` component (5,452 rows) is **ODbL, blocked on `DEC-1200`** (§8.11 §2/§5) until the platform commits to serving it as an aggregated Produced Work only, or accepts the §4.6 alterations-file obligation. **BR-1108 as originally drafted did not name this — the assembler has added the dependency explicitly below rather than presenting the capability as uniformly available.** |
| 5 | ETA credibility — work zones, weather, chain controls (BR-1107) | **Moderate, geographically bounded** | **Yes — significantly blocked.** NWS weather is safe (US government work). Work-zone feeds (AZ/KS/MN/WA) are **Unverified — treat as No until cleared** (§8.11 row 6-9: all four feeds return `feed_info.license = null`, no redistribution grant located). Caltrans chain controls are **Unverified that the site-content licence reaches the machine feed** (§8.11 row 10). **BR-1107's original acceptance condition ("attached events carry source feed + geography") already implies bounded coverage but did not flag the licence status as unresolved — added below.** |
| 6 | Detention/dwell evidence | **Reject as a standalone capability** — no layer generates a custody timestamp; A4's BR-403 already owns this independently | Moot — not shipped |
| 7 | Disintermediation answer | **Reject the "hold" framing** — downgraded to a measured feature (KPI-1012), not a moat | Moot — not sold as retention |

**Amended BR-1108 (parking/rest-area disclosure, licence dependency made explicit):** "Any parking or rest-area location surfaced to a driver/carrier carries an explicit disclosure that no live occupancy signal exists for it. **Rest-area records sourced from the ODbL layer (`osm.rest_areas`) are surfaced only as an aggregated Produced Work (e.g., 'rest areas near this corridor') and never as individually attributable OSM records, pending resolution of `DEC-1200` (§8.11).**" MoSCoW: Must. Traces: 006. Source: anti-dark-pattern; FTC deceptive-practice avoidance + A12 §2.

**Amended BR-1107 (work-zone/weather/chain-control context, licence dependency made explicit):** "While `IN_TRANSIT`, a live work-zone, weather, or chain-control event intersecting the shipment's route, within a covered feed's geography, attaches to the shipment's status/exception record rather than surfacing only as a generic delay. **Work-zone (AZ/KS/MN/WA) and Caltrans chain-control sourcing remain `Unverified` per A12 §8.11 and shall not surface in a client build, or shall surface only with a visible 'licence pending' internal flag, until a written term or grant is confirmed; NWS weather is unaffected and may ship now.**" MoSCoW: Should. Traces: 002/004. Source: → §8.4 A4 BR-401/405; A12 §5.

**The disintermediation question — skeptical, by instruction (§11.3, A11).** A10 named five plausible holds against leakage (money, risk-transfer, vetting-as-service, volume, contract). Data assets are not on that list and A11 does not think they belong there as a sixth: a route-feasibility check, a fuel-cost floor, a mechanic directory, a parking suggestion are each cheap to reproduce once a shipper-carrier pair has run a lane together — session-level utility, not relationship-level lock-in, and this competes against products (Trucker Path, DAT Trucker Tools) that already publish this cheaply or free at scale to millions of drivers. **Ship these as trust-and-efficiency features under OBJ-001/004/006, and measure it (BR-1109); do not represent them to Boss or a client as the disintermediation answer.**

**A11's own stated limits:** the actual attribute schema behind the bridge/tunnel counts (a database check Boss can run directly, ASM-041 §11); counsel/A7 on whether a fuel-only floor logged in the selection record helps or hurts the *Montgomery* defence — could read as diligence, or as an admission the platform knew a bid was suspect and awarded anyway; licensing counsel on OSM/EIA/Overture terms before any layer ships commercially (→ §8.11); a real dispatcher's reaction to the mechanic directory — whether it is worth anything next to their own phone list.

### 8.11 Data Licensing and Commercial-Use Review (A12, BR-1200–1210)

*Stress-test of DEC-LOCK-002: may the client's data platform be redistributed inside a third party's proprietary commercial product, per source, and what obligation attaches. Not legal advice — a surface-and-controls map, not a clearance.*

**CHALLENGE to DEC-LOCK-002, accepted and reflected in DECISIONS.md already:** the original inventory table was licence-blind, merging permissive and share-alike layers into single rows. Restated per-table-per-licence in DECISIONS.md (reproduced there in full) and in the per-source register below.

**Per-source register (16 rows, full detail preserved in the source part; summarised by disposition):**

| Disposition | Layers | Obligation |
|---|---|---|
| **Yes — safe** (US government works) | Truck routes (454,830) · Bridges (629,710) · Tunnels (580) · Truck parking (1,915) · Fuel prices (17,089, on client's own key) · NWS alerts (with UA + contact) · Census CBP | Attribution requested, not required; carry the upstream's own advisory verbatim (e.g., NTAD "not for enforcement/navigation") |
| **Yes-with-obligation** (Overture, CDLA-Permissive/Apache) | Fuel places (151,767) · Mechanic shops (11,759) · ATP hours/chain badge (CC0) | `© Overture Maps Foundation`; preserve Foursquare NOTICE |
| **Yes-with-obligation, the obligation is the problem** (ODbL) | Fuel stations (108,056) · Weigh points (3,773) · Rest areas (5,452) · Truck repair (763) · OSM ways | Attribution + **share-alike** — see `DEC-1200` below |
| **Unverified — treat as No until cleared** | WZDx AZ/KS/MN/WA (all four return `feed_info.license = null`) · Caltrans machine-feed reach · NY/NJ licence registries · EIA API-key registration terms | Counsel handoff item; no redistribution grant located |
| **No — hard stop** | AAA daily diesel scrape (`scripts/aaa_prices.py`) | Personal/non-commercial only; "archive" and "distribute" both explicitly named and prohibited; commercial use "strictly prohibited." **Already gated off by default in the codebase** (`AAA_PRICES_ENABLED` unset, zero rows in production); the requirement below (BR-1204) makes it impossible to ship enabled, closing the residual build-gate risk. |

**`DEC-1200` (open) — the ODbL question, the one issue that can force re-architecture.** ODbL §4.5(b): a rendered map, corridor summary, or computed cost floor is a Produced Work, exempt from share-alike — attribution only, proprietary posture intact. ODbL §4.4/§4.6: an endpoint returning OSM records as JSON, a bulk/CSV export, or a feed a client's customer can pull is re-utilisation into a Derivative Database, which if publicly used must be offered as the whole database or a machine-readable alterations file. **The system is already architected for the right answer** — ODbL data isolated in its own schema, joined at query time rather than copied — but the serving boundary is undecided: today's `/v1/fuel` endpoint emits ODbL records directly, i.e. the wrong-hand pattern. Three options, none chosen: (a) ODbL layers consumed as Produced Works only, never emitted as records — the only option that keeps both the layers and the client's proprietary posture; (b) publish the ODbL-derived layer under ODbL with a §4.6 alterations file; (c) drop OSM, re-source the affected layers.

| ID | MoSCoW | Requirement | Acceptance condition |
|---|---|---|---|
| BR-1200 | Must | Every response, screen, export and document from an attribution-bearing source carries that source's notice. | Automated check per payload; existing ODbL check extended to Overture/Foursquare/ATP/Caltrans/NWS. |
| BR-1201 | Must | Every stored record carries machine-readable licence + attribution + provenance. | Any row returns source id, licence id, attribution, observed-at date. |
| BR-1202 | Must | ODbL stays structurally isolated; no ODbL attribute value reaches a permissive table. | Existing invariant test runs in CI and blocks release. |
| BR-1203 | Must | The ODbL serving boundary is enforced in code per `DEC-1200`. | (a) no endpoint/export returns `osm.*` rows, asserted by test; or (b) a §4.6 alterations file is published and reachable. |
| BR-1204 | Must | No source forbidding commercial use exists in a client-facing build. | Build gate fails if `aaa_daily` (or any non-commercial-flagged source) is enabled, in schema, or holds rows. |
| BR-1205 | Must | A licence register — source, URL, licence, verified-on date, evidence excerpt, obligation — ships to the client. | 100% of live sources; no entry older than the BR-1206 re-verification window. |
| BR-1206 | Should | Terms are re-verified on a cadence and the evidence archived (dated copy), not linked. | Every source has an in-window evidence artefact. |
| BR-1207 | Must | Advisory layers show the upstream's own limitation verbatim. | Notice on every surface; not suppressible by a query parameter. |
| BR-1208 | Must | Every upstream credential/identity (EIA key, NWS UA + contact) belongs to the operating client. | No personal key or contact string in client deployment config — closes the risk that Boss's personal EIA key ships in a client product. |
| BR-1209 | Should | Every Unverified layer is flagged off by default and unsellable as a contracted feature until cleared. | Flag exists; feature list excludes it. **This is the mechanism by which §8.10's amended BR-1107 is enforced, not just stated.** |
| BR-1210 | Must | The client agreement sets per-layer downstream rights (sublicence, resale, export) and passes upstream obligations through. | Data-terms schedule matches the BR-1205 register line by line. | **counsel** |

**Safe to build on now (full list, no licence decision pending):** NTAD truck routes, tunnels, truck parking, FHWA NBI bridges, EIA prices (client's own key), NWS alerts (with UA + contact), Overture fuel places, Overture mechanic shops, ATP hours/chain (CC0), Census CBP. **"Safe" means safe *with* BR-1200/1201/1207 — never bare.**

**Needs a licence decision before it can be sold:** all four `osm.*` tables (fuel stations, weigh points, rest areas, truck repair) — blocked on `DEC-1200`; WZDx AZ/KS/MN/WA — blocked on a written term or grant, per state; Caltrans — usable if counsel accepts `conditions-of-use` reaching the machine feed; NY/NJ licence registries — blocked on ToU.

**Drop or replace:** AAA daily diesel scrape — remove from the client build entirely; replace with EIA regional weekly (already the source of record) or a paid OPIS licence if daily station-level price is a contracted feature.

**§8.11.7 Counsel handoff (8 items, preserved in full):** (1) whether serving `osm.*` records through an API is Derivative-Database re-utilisation or a Produced Work — `DEC-1200` turns on this; (2) whether the client's architecture triggers its own §4.6 disclosure; (3) whether `conditions-of-use` reaches the Caltrans machine feed; (4) redistribution rights for the four WZDx feeds and NY/NJ registry ToU, state by state; (5) residual exposure from historical AAA collection; (6) whether the EIA API registration ToS binds independently of public-domain status; (7) the client agreement's data-terms schedule, warranties and indemnities; (8) CFAA/contract exposure from any scraped source, separate from copyright.

### 8.12 Cross-reference resolution — orphans, and the requirements that were never fully closed

**Scope of this pass.** The twelve parts contain roughly 250 prose cross-reference pointers (`→ A6`, `→ A3`, etc. — agents were explicitly forbidden from inventing cross-block IDs, spine §5). The assembler resolved the pointers named explicitly in the task brief with full rigor (§8.3/§8.9 merge, §8.2/§8.9 BR-221/224 consumption, §8.1/§8.6 TONU cross-references, §7.4 OS&D reconciliation) and resolved a further representative sample across every domain while assembling §8.1–§8.11 above (inline, as "resolves to X" or "= X" annotations). **A full line-by-line audit of all ~250 pointers was not performed — that would be a second engagement's worth of work — and this document says so rather than implying false completeness.** The following are the genuine orphans and partial orphans surfaced during this pass:

| # | Origin | Pointer | What it needs | Status |
|---|---|---|---|---|
| 1 | A1 BR-106 | "→ A6/A9" — payment-reliability signal shown to bidders pre-bid | A6 or A9 requirement to render a standing indicator on the bid/auction view | **True orphan.** Neither A6 nor A9 contains a requirement to surface this. No requirement currently implements what BR-106 depends on. |
| 2 | A1 BR-108 | "derived → A8" — open non-payment dispute blocks shipper re-publish | An A8 requirement that gates *shipper* publish rights on an open *money* dispute | **Partial orphan.** A8 covers `DISPUTED` generically (§8.9.8, EC-8xx) but has no requirement that closes the loop back onto A1's publish gate. A8's dispute framework and A1's publish gate are two ends of the same rope that were never explicitly tied. |
| 3 | A1 BR-150–152 / A3 DEP-303 | "→ A8" — re-trade attempts logged against the carrier, exposed to A8 | An A8 requirement that ingests re-trade/decline/lapse events into carrier fitness scoring | **Partial orphan.** A8's BR-814 ("detect award-pattern anomalies") is adjacent but does not name re-trade frequency as an input. A3's BR-311 tracks the data; no A8 requirement consumes it into a fitness or suspension decision. |
| 4 | A8 §8.9.4 / A6 §1 | "`[NEEDS INPUT]` may freight charges be offset against an open cargo claim → A6" | Explicit rule | **Not an orphan — consistently unresolved on both sides.** A6's closest adjacent item (EC-608, deduction exceeding remaining payable) does not answer the offset question either. Both domains independently deferred to counsel; this is agreement, not a gap in cross-referencing. Flagged so it is not mistaken for an orphan at UAT time. |

**Why only four are reported, given ~250 pointers exist:** the large majority of pointers resolved cleanly on inspection — either to a named requirement in the target domain (the common case, and the reason each domain's ID block scheme worked) or to a target domain's general framework (a state, a table, a section) where the source agent's phrasing ("→ A8", "cross A6") was intentionally coarse rather than claiming a specific ID. Coarse-but-real is not the same failure mode as orphaned. The four above are the ones where the assembler could not find *any* landing point, or found only a landing point that doesn't close the specific loop the source requirement asserted.

---

## 9. Functional Requirements Boundary

Detailed functional requirements are out of scope for this document and will be maintained in a companion FRD. This BRD defines business need and outcome only. Where a requirement above references a specific technical mechanism (e.g., "COI naming the platform as certificate holder," "structured pickup record"), that is the business-level *shape* of the evidence required, not a system design — no database, API, screen layout, or vendor is specified anywhere in §8, per the hard rule every one of the twelve source parts operated under (spine §7.3).

---

## 10. Non-Functional Requirements

Business-level only. Categories considered: performance, scalability, availability, security, usability, compliance, maintainability, retention, localisation, accessibility, auditability, minimisation, integrity. **Localisation and portability were explicitly considered and judged not applicable** — single jurisdiction (US), no duty found beyond the rights-request portability already covered under Compliance (A7).

| ID | Category | Requirement | Target | Measurement Method |
|---|---|---|---|---|
| NFR-701 | Retention | Broker transaction records | ≥3 yrs (49 CFR 371.3) | Restore a record ≥3 yrs old |
| NFR-702 | Retention | Retention beyond the regulatory floor | `[NEEDS INPUT: not fixed by 371.3; do not set without counsel]` | Signed-off schedule |
| NFR-703 | Auditability | Award decisions immutable, replayable | 100% reproducible from stored basis | Quarterly replay, random sample |
| NFR-704 | Auditability | Write-once log of create/modify/delete on load, bid, award, eligibility, POD, claim — actor, before/after, timestamp | 100% entity coverage | Tamper test + coverage report |
| NFR-705 | Auditability | Records furnishable electronically | Designed against the pending 48-hr FMCSA transparency proposal `[verify — not yet final]` | Timed retrieval drill |
| NFR-706 | Security | Driver/consignee data encrypted in transit + at rest, access role-restricted | Attempts logged | Access review; penetration test |
| NFR-707 | Security | Authority/insurance docs segregated, every view attributable | 100% of views logged | Access-log sample |
| NFR-708 | Compliance | Rights-request response | Shortest applicable state period `[verify per state]` | Request-log ageing report |
| NFR-709 | Compliance | Notice reachable by an unregistered consignee | ≤1 step from any delivery message | Test with unregistered recipient |
| NFR-710 | Minimisation | No ELD/HOS, Clearinghouse or D&A data stored | Zero such fields absent a documented lawful-basis decision | Schema review each release |
| NFR-711 | Availability | Evidence retrieval independent of the transactional path | Works while auction/award degraded | Failover drill |
| NFR-712 | Integrity | POD/BOL artefacts tamper-evident | Post-capture alteration detectable | Integrity check on sample |
| NFR-900 | Accessibility/Usability | Driver-facing support must not require sustained reading or typing while the vehicle is in motion, consistent with distracted-driving norms | Qualitative, business-level — no channel prescribed | Support-flow review against the requirement at design time |
| NFR-901 | Security/Auditability | Every permission grant or revocation (bid, accept-award, claim-waiver, payee-of-record change) is logged with actor, timestamp, and account | 100% of grant/revoke events logged, retained for a period sufficient to support a Carmack claim/suit-limitation window (exact period → §8.7 A7) | Audit-log completeness review |
| NFR-1200 | Integrity/Compliance | Attribution and licence notices survive caching, pagination, partial responses, and error paths | Contract test on every response shape | Automated per-payload check, extended from the existing ODbL smoke test |

**Considered and judged not applicable, stated explicitly (per anti-patterns.md #5, vague-NFR avoidance and the template's explicit instruction to state non-applicable categories):** Localisation (single US jurisdiction, no multi-language product surface beyond BR-914's English/Spanish support requirement, which is a Usability/Accessibility item, not localisation). Portability — no duty found beyond the state-privacy rights-response portability already covered under NFR-708.

---

## 11. Assumptions Register

**This section is assembler-owned per spine §8 — no drafting agent could produce it, since each saw only its own tags.** Every `[ASSUMPTION]` tag across all twelve parts is swept below into one continuous ID sequence (ASM-001–046). **Owner and Validation Date are `[NEEDS INPUT]` for every single row without exception** — none of the twelve parts assigned an owner or a validation date to any assumption; the assembler does not invent one to make the table look complete. Impact-if-wrong is the assembler's synthesis of what the originating agent already said would break, not new information. Confidence is carried verbatim from the source.

| # | Assumption | Origin | Confidence | Impact if Wrong | Owner | Validation Method | Validation-by Date |
|---|---|---|---|---|---|---|---|
| ASM-001 | Shippers commonly operate multiple ship-from/ship-to sites | A1 BR-103 | High | Multi-site org model (BR-103) is over-engineered for a single-site client; low cost if wrong | `[NEEDS INPUT]` | Client discovery interview | `[NEEDS INPUT]` |
| ASM-002 | Equipment type should be a closed set, not free text | A1 BR-111 | High | Free-text equipment breaks BR-111's publish gate and A2's eligibility matching (§8.2) | `[NEEDS INPUT]` | Compare against 2–3 real shipper load-tender forms | `[NEEDS INPUT]` |
| ASM-003 | Stop-specific instructions should be withheld pre-award to prevent lane-shopping | A1 BR-126 | Medium | If wrong, withholding this data needlessly slows carrier planning without preventing anything | `[NEEDS INPUT]` | Carrier interview on planning needs | `[NEEDS INPUT]` |
| ASM-004 | The platform can technically detect duplicate-freight publishes | A1 BR-132 | Low | BR-132 cannot be built as specified; duplicate-freight fraud (double-listing the same load) goes undetected | `[NEEDS INPUT]` | Technical feasibility spike | `[NEEDS INPUT]` |
| ASM-005 | Identity verification of the onboarding signer is expected at this platform's trust tier | A2 BR-208 | Medium | Onboarding friction added for no fraud-reduction benefit if the market doesn't expect it | `[NEEDS INPUT]` | Compare against 2–3 competitor onboarding flows (DAT, Truckstop) | `[NEEDS INPUT]` |
| ASM-006 | Equipment ownership/lease status is informational only, not an eligibility gate | A2 BR-213 | Medium | If wrong, leased equipment carries a fitness signal the platform is ignoring — RSK-021 (§14) | `[NEEDS INPUT]` | Insurance-broker / underwriter consult | `[NEEDS INPUT]` |
| ASM-007 | Carriers need self-service unavailability declaration, independent of any award | A2 BR-216 | High | Low cost if wrong — a convenience feature, not a control | `[NEEDS INPUT]` | Carrier user research | `[NEEDS INPUT]` |
| ASM-008 | Advance-expiry reminders reduce unplanned authority/insurance/CDL lapses | A2 BR-220 | High | Feature has no measurable effect on lapse rate; low cost if wrong, this is a Should not a Must | `[NEEDS INPUT]` | A/B on lapse rate post-launch | `[NEEDS INPUT]` |
| ASM-009 | Most US trucking companies run very few trucks; owner-operators are a large share of capacity (well-established market structure, not dataset-sourced for this engagement) | A2 §DEC-201 preamble | High | DEC-201's Option A (uniform high bar) would exclude exactly the supply OBJ-003 needs, more severely than modelled, if this structural read is wrong | `[NEEDS INPUT]` | Cite FMCSA/ATA fleet-size distribution data directly | `[NEEDS INPUT]` |
| ASM-010 | Enough eligible carriers per lane will bid to make competition real | A3 ASM-301 | Low | The entire mechanism collapses to a one-bidder negotiation (§4.5); this is the premise of "auction" itself | `[NEEDS INPUT]` | KPI-01 (bids per closed auction) measured against a real lane in P1 (§17.2) | `[NEEDS INPUT]` |
| ASM-011 | Carriers will treat a bid as binding without a deposit | A3 ASM-302 | Low | Bid integrity (BR-307) has no enforcement mechanism if this is wrong — bids become non-binding quotes | `[NEEDS INPUT]` | Carrier interview / pilot bid-honour rate | `[NEEDS INPUT]` |
| ASM-012 | A shipper can meaningfully state a ceiling/reserve price | A3 ASM-303 | Medium | DEC-306 (reserve price) is unusable as a design lever if shippers can't or won't state one | `[NEEDS INPUT]` | Shipper interview | `[NEEDS INPUT]` |
| ASM-013 | FMCSA safety data stays current enough at bid time to gate on | A3 ASM-304 | Medium | The DEC-LOCK-001 gate is only as good as its data freshness; a stale gate is a false defensible-selection record (RSK, §14) | `[NEEDS INPUT]` | Compare SAFER/SMS update cadence against auction cycle time | `[NEEDS INPUT]` |
| ASM-014 | Shippers will trade latency (auction time) for a lower price and a defensible record — "the premise the business rests on" (A3's own words) | A3 §4.7 | Low | If wrong, the entire mechanism loses to instant-book/posted-rate competitors on the one dimension shippers actually value; **this is the single highest-stakes assumption in the document alongside ASM-018/A10's W5** | `[NEEDS INPUT]` | A10's P0/P1 phase gates (§17.2) — named shipper validation before build | `[NEEDS INPUT]` |
| ASM-015 | Baseline dispatch today is phone/fax/paper-coordinated, industry-typical for small-to-mid carriers | A4 §1 (stated twice in source, deduplicated here) | Medium | The entire §6/§7.1 current-state/future-state delta is calibrated against the wrong baseline if a carrier segment already runs ELD-linked apps | `[NEEDS INPUT]` | Observe a real dispatch desk (A4's own stated limit) | `[NEEDS INPUT]` |
| ASM-016 | A "pickup record" distinct from, but structurally mirroring, the delivery BOL/POD is the correct data model | A4 §3 (stated twice in source, deduplicated here) | High | If wrong, BR-400's origin-baseline function fails to give A8's claim path a true comparison point | `[NEEDS INPUT]` | Data-model review against a real BOL/POD pair | `[NEEDS INPUT]` |
| ASM-017 | The consignee named on the BOL is the shipper's customer, not a platform party, with no pre-existing account | A5 §A5.1 | High | Low cost if wrong in the common case; see ASM-035 for the specific third-party-DC variant | `[NEEDS INPUT]` | Shipper customer-base sample | `[NEEDS INPUT]` |
| ASM-018 | "Invoice generation" in Boss's happy path means a platform-generated invoice artifact at minimum, independent of the §8.6 money-model choice | A6 ASM-600 | Low | If wrong, the entire §8.6 requirement set is scoped to the wrong artifact — resolved once §8.6 §1's model choice is made | `[NEEDS INPUT]` | Resolved automatically once §13.1's fork is answered | `[NEEDS INPUT]` |
| ASM-019 | NOA/Release documents arrive as uploaded artifacts, not a live factor-company API feed | A6 ASM-601 | Medium | BR-606–608's verification workflow is designed for the wrong integration pattern if factors expect API-based NOA exchange | `[NEEDS INPUT]` | Factor-company outreach (2–3 major freight factors) | `[NEEDS INPUT]` |
| ASM-020 | Interstate, for-hire, domestic truckload; no household goods | A7 ASM-701 | Medium | If wrong, the entire Carmack/Part-371/387 regulatory frame in §8.7 is the wrong frame for a material share of freight | `[NEEDS INPUT]` | Client scope confirmation | `[NEEDS INPUT]` |
| ASM-021 | No household goods in scope | A7 ASM-702 | Medium | Duplicate risk surface to ASM-026 (A8's version of the same assumption) — see §14's cross-reference note | `[NEEDS INPUT]` | Client scope confirmation | `[NEEDS INPUT]` |
| ASM-022 | No hazmat in phase 1 | A7 ASM-703 | Low | Blocks BR-719's sizing; if wrong, a live regulatory surface (49 CFR 171-180, UCR, permits) is entirely undesigned | `[NEEDS INPUT]` | Client scope confirmation — flagged low-confidence by A7 itself | `[NEEDS INPUT]` |
| ASM-023 | Platform employs no drivers | A7 ASM-704 | High | If wrong, an entire employer-side regulatory surface (payroll, workers' comp, direct HOS liability) activates that this document never designed for | `[NEEDS INPUT]` | Client business-model confirmation | `[NEEDS INPUT]` |
| ASM-024 | FMCSA public safety data (SAFER/SMS/CSA) stays available for vetting | A7 ASM-705 | Medium | DEC-LOCK-001's entire gate mechanism depends on this data source remaining public and queryable | `[NEEDS INPUT]` | Monitor FMCSA data-access policy | `[NEEDS INPUT]` |
| ASM-025 | Interstate domestic truckload, so Carmack applies; intrastate follows state law | A8 ASM-801 | Medium | Same underlying assumption as ASM-020 (A7) and ASM-039 (A10) — three domains independently converged on it; see §14's cross-domain note | `[NEEDS INPUT]` | Client scope confirmation | `[NEEDS INPUT]` |
| ASM-026 | General freight, not household goods — what makes the cargo-insurance gap (§8.9.6) live | A8 ASM-802 | Medium | If household goods are in scope, carriers ARE required to carry cargo insurance and §8.9.6's entire framing inverts | `[NEEDS INPUT]` | Client scope confirmation | `[NEEDS INPUT]` |
| ASM-027 | Contingent cargo insurance commonly excludes double-brokered and impersonation losses | A8 ASM-803 | Medium | If wrong, RSK-024's mitigation (policy-wording review) is unnecessary, but this cannot be assumed away — the wording review still needs to happen either way | `[NEEDS INPUT]` | Insurance-broker policy-wording review (A8's own stated limit) | `[NEEDS INPUT]` |
| ASM-028 | The consignee, who never signed up, is nonetheless a likely claimant | A8 ASM-804 | Medium | If wrong, BR-906's consignee-relay claim path is over-built relative to actual claim-filing patterns | `[NEEDS INPUT]` | Claims-data review once live | `[NEEDS INPUT]` |
| ASM-029 | The platform holds claim and selection evidence rather than relying on carriers to hold it | A8 ASM-805 | Medium | If wrong, BR-819's evidence-preservation duty sits with the wrong party at litigation time | `[NEEDS INPUT]` | Resolved by `DEC-801` (§8.9.1) | `[NEEDS INPUT]` |
| ASM-030 | No hazmat, high-value, or temperature-controlled specialisation in phase 1 | A8 ASM-806 | Low | Same family as ASM-022; if wrong, §8.9.6's insurance-structure analysis is materially incomplete for the freight actually moving | `[NEEDS INPUT]` | Client scope confirmation — flagged low-confidence by A8 itself | `[NEEDS INPUT]` |
| ASM-031 | Cargo-insurance exclusion wording varies by policy (a general caution, not a specific claim) | A8 §8.9.6 inline | Medium | Low cost if wrong — this is a caution against over-generalising, not a load-bearing design assumption | `[NEEDS INPUT]` | Insurance-broker consult | `[NEEDS INPUT]` |
| ASM-032 | A driver's signature is binding on the carrier account by accepted freight-industry convention | A9 BR-903 | High | If wrong, POD capture (§8.5) has no clear legal binding mechanism back to the account that must pay/be paid | `[NEEDS INPUT]` | Confirm against carrier contract templates / counsel | `[NEEDS INPUT]` |
| ASM-033 | A documented human review step at carrier approval is part of the negligent-selection defence | A9 BR-908 | Medium | If wrong, BR-908's human-in-the-loop gate is a cost with no defensive legal value | `[NEEDS INPUT]` | Counsel confirmation, tied to §8.7 §7.9 item 2 | `[NEEDS INPUT]` |
| ASM-034 | Spanish is the highest-priority second language across the US truckload driver workforce (no cited percentage) | A9 BR-914 | High, but explicitly uncited | If wrong, BR-914's language investment misses the actual highest-need population | `[NEEDS INPUT]` | Client to confirm against its own driver-workforce demographics | `[NEEDS INPUT]` |
| ASM-035 | In the common case the consignee IS the shipper's customer; a third-party DC/cross-dock pattern is also plausible | A9 §9.1 | Medium | If the third-party-DC pattern dominates, exception contact (BR-912) routinely reaches a party with no stake in resolving anything quickly (EC-910) | `[NEEDS INPUT]` | Client customer-base sample, same as ASM-017 | `[NEEDS INPUT]` |
| ASM-036 | Carrier-first seeding is cheaper than shipper-first seeding | A10 ASM-1001 | Medium | Seeding budget misallocated if wrong (§17.2 cold-start plan) | `[NEEDS INPUT]` | Pilot CAC comparison, both sides | `[NEEDS INPUT]` |
| ASM-037 | Liquidity is per-lane-per-day, never national | A10 ASM-1002 | High | A national launch at the same carrier count yields zero density everywhere if wrong — directly shapes the P1 phasing gate (§17.2) | `[NEEDS INPUT]` | KPI-01 measured per lane during P1 | `[NEEDS INPUT]` |
| ASM-038 | Sustainable take rate is bounded by incumbent gross margins (13.3–14.8%) | A10 ASM-1003 | Medium | Revenue model overstates margin if the platform can command a premium incumbents cannot | `[NEEDS INPUT]` | Compare realised take rate against CHR/RXO disclosed margins post-launch | `[NEEDS INPUT]` |
| ASM-039 | Client intends to intermediate (broker/carrier), not license software | A10 ASM-1004 | Low | Same underlying fork as ASM-020/ASM-025 and the whole of §13.1 — the unit-economics model and the regulatory surface both change if wrong (RSK, §14) | `[NEEDS INPUT]` | Resolved by §13.1's single blocking decision | `[NEEDS INPUT]` |
| ASM-040 | Loads are US domestic interstate truckload | A10 ASM-1005 | Medium | Cross-border/intrastate/LTL change the unit-economics model materially — third independent convergence with ASM-020/ASM-025 | `[NEEDS INPUT]` | Client scope confirmation | `[NEEDS INPUT]` |
| ASM-041 | Bridge/tunnel records carry attribute-level clearance/weight/hazmat detail, not only location | A11 ASM-1100 | Low | BR-1100's route-feasibility check cannot be built as specified if attributes are location-only | `[NEEDS INPUT]` | **A11's own stated fix: a direct database schema check Boss can run — not a research question** | `[NEEDS INPUT]` |
| ASM-042 | The 17,089-row diesel-price table is granular enough (state/corridor) to beat one national average for BR-1103's fuel-floor calculation | A11 ASM-1101 | Medium | BR-1103's fuel-cost floor degrades to a blunter, less useful national-average signal if wrong | `[NEEDS INPUT]` | Confirm table grain against schema | `[NEEDS INPUT]` |
| ASM-043 | The client's product is proprietary/closed, not open-source | A12 ASM-1200 | High | `DEC-1200`'s entire ODbL-containment analysis (§8.11) assumes a closed product; an open-source posture changes the ODbL calculus substantially | `[NEEDS INPUT]` | Client product-licensing confirmation | `[NEEDS INPUT]` |
| ASM-044 | Delivery is a hosted service, not a database handover to the client | A12 ASM-1201 | Low | "Materially changes §2" (A12's own words) — the ODbL answer differs across hosted-API / embedded-dataset / database-handover; flagged `[NEEDS INPUT]` at A12 §1 directly | `[NEEDS INPUT]` | Client deployment-model confirmation | `[NEEDS INPUT]` |
| ASM-045 | Today's Overture terms apply unchanged to release 2026-06-17.0 | A12 ASM-1202 | Medium | The "safe" classification for the two largest POI layers (fuel places, mechanic shops) depends on this holding | `[NEEDS INPUT]` | Re-verify per A12's own BR-1206 cadence | `[NEEDS INPUT]` |
| ASM-046 | No upstream source changed its terms since the registry's 2026-07-22/24 checks | A12 ASM-1203 | Medium | Any per-source disposition in §8.11's register could be stale by the time this document is read | `[NEEDS INPUT]` | Re-verify per BR-1206 | `[NEEDS INPUT]` |

**Cross-domain convergence, visible only at assembly (see §3.4 for the fuller pattern):** ASM-020 (A7), ASM-025 (A8), and ASM-040 (A10) are, in substance, the same assumption — "this is US domestic interstate truckload" — reached independently by three agents that could not see each other's work. Independent convergence is evidence *for* the assumption; it is also a single point of failure that would simultaneously invalidate three domains' analyses if wrong, not three independent risks. Treated as such in §14's risk register.

---

## 12. Dependencies

| # | Dependency | Owning domain | Expected date | Impact if late |
|---|---|---|---|---|
| DEP-201 | Auction engine must call the eligibility function per-load, per-bidder, at bid time and again at award confirmation | §8.3 ← §8.2 | `[NEEDS INPUT]` | DEC-LOCK-001's gate cannot be enforced without this call existing |
| DEP-202 | Insurance minimums, authority-age thresholds, Clearinghouse cadence need regulatory citation depth §8.2 doesn't own | §8.2 ← §8.7 | `[NEEDS INPUT]` | Eligibility gate (§8.2) ships with placeholder thresholds |
| DEP-203 | Every "flagged for ops review" outcome (BR-218/219/230) assumes an exception desk exists | §8.2 ← §8.8 (Ops) | `[NEEDS INPUT]` | Flags accumulate with no one to action them |
| DEP-301 | §8.2's eligibility gate callable per-load, per-bidder, at award | §8.3 ← §8.2 | `[NEEDS INPUT]` | Same as DEP-201, cross-listed by A3 independently |
| DEP-302 | §8.6 honours the awarded bid as rate-confirmation price; rejects unrecorded changes | §8.6 ← §8.3 | `[NEEDS INPUT]` | Re-trade at the dock (RSK-003) becomes unenforceable |
| DEP-303 | §8.9's carrier record accepts re-trade, decline, lapse events | §8.9 ← §8.3 | `[NEEDS INPUT]` | **Partial orphan — see §8.12 item 3.** No confirmed landing requirement exists yet on the §8.9 side. |
| DEP-304 | §8.7 rules on the antitrust posture of DEC-302/303 (open vs. sealed bidding; standing-best vs. rank-only) pre-launch | §8.3 ← §8.7 | `[NEEDS INPUT]` | Auction format choice made without antitrust clearance |
| DEP-900 | Platform-ops staffing plan and after-hours coverage model | §8.8 (Ops) ← Client | `[NEEDS INPUT]` | Not resolvable inside this BRD — a client operating decision |
| DEP-1100 | §8.2's eligibility tuple consumes route-feasibility state alongside it, but route-feasibility is **not** part of carrier-fitness eligibility (lane-legality, not carrier fitness) | §8.2 ← §8.10 (A11) | `[NEEDS INPUT]` | Route-feasibility silently miscategorised as a carrier trust signal if not kept distinct |
| DEP-1101 | BR-1103's fuel-floor flag and BR-1105's override land inside the merged §8.3 BR-303 selection record, not a separate one | §8.3 ← §8.10 (A11) | `[NEEDS INPUT]` | Two competing "award record" artifacts if not enforced |
| DEP-1102 | BR-1106/1107 attach to §8.4's existing `TRANSIT_EXCEPTION` and status-update events; no new state machine | §8.4 ← §8.10 (A11) | `[NEEDS INPUT]` | State-machine sprawl if a parallel exception model is built |
| DEP-1103 | Licensing review (RSK-042, §14) gates whether any OSM-derived layer ships commercially at all | §8.10 (A11) ← §8.11 (A12) | `[NEEDS INPUT]` | Capabilities 4/5 (§8.10) ship with an unresolved legal exposure if this gate isn't enforced pre-launch |

---

## 13. Constraints

Hard numbers only, or a hard rule the platform must not violate. "Limited budget and time" is not a constraint and does not appear here.

### 13.1 The single blocking decision this document could not make for Boss

**This is the assembler's consolidation of the finding at §3.4, restated here as a formal constraint because everything else in §12/§14/§17 downstream of it is provisional until it is answered.** One decision — the client's FMCSA/legal posture — was asked five separate times across five parts (A6 §1, A7 §7.1, A7 §7.4, A8 §8.1 `DEC-801`, A9 §9.2). Answering it resolves all five in one motion:

| If the client's answer is... | A6 §1 money model | A7 §7.1 fork | A8 §8.1 `DEC-801` | Consequence for §17 unit economics |
|---|---|---|---|---|
| Licensed property broker | Model B (broker of record) is the natural fit | Answer A | P1 | Take-rate model viable; highest capital + compliance cost; BR-701-708 become Must |
| Carrier bidding its own loads | Model A or B | Answer B | P2 | Conflict-of-interest disclosure required in the auction it runs (§8.3, §17); heaviest insurance burden |
| Software vendor, tenant holds authority | Model A or C | Answer C | P3 | SaaS/subscription model, not take-rate; RSK-034 (§14) — the whole unit-economics structure at §17 changes |
| Neither, yet sets price and awards | None are lawful as designed | Answer D | — | Unauthorised-brokerage fact pattern; counsel question, not a design question — blocks everything |

**`CON-013`:** No load may reach `PUBLISHED` until this decision is recorded with authority evidence (A7 BR-701). **`CON-014`:** No settlement requirement in §8.6 can be finalised until the money-transmission fork (M1/M2/M3, §8.7 §7.4) is answered downstream of the table above.

### 13.2 Other hard constraints, carried forward

| ID | Constraint |
|---|---|
| CON-301 (A3) | Auction tension depends on pool depth **per lane**, not platform size — a platform with two carriers on a lane runs a two-carrier auction, not a national one. → §17 |
| CON-701 (A7) | No publish before operator status (BR-701) is set |
| CON-702 (A7) | No award without frozen authority + insurance evidence in the award record |
| CON-703 (A7) | No ELD/Clearinghouse/D&A test-result data stored, absent a documented lawful basis |
| CON-1200 (A12) | Upstream rate limits/throttles (NWS, ArcGIS, S3) cap the freshness a client SLA can promise |
| CON-1201 (A12) | Four WZDx feeds and three Caltrans feeds are keyless, contractless, and revocable at will by the issuing state — no committed uptime exists to build an SLA against |

**Regulatory floor constraints (not invented, cited):** BMC-84 surety bond / BMC-85 trust minimum **$75,000** while broker authority is active (49 CFR 387.307) — reported rising to **$150,000 from July 2026** (RSK, §14, cited source). For-hire interstate carriers, GVWR ≥10,001 lb, non-hazmat: **$750,000** minimum public liability; **$5,000,000** for specified bulk hazmat; **$1,000,000** for oil/listed hazmat (49 CFR 387.9). Carmack claim floor: not under **9 months** to file; not under **2 years** to sue from written disallowance (49 U.S.C. §14706(e)). These are the only numeric floors in this document that are not `[NEEDS INPUT]` — every one is a federal regulatory citation, not an estimate.

---

## 14. Risk Register

Category column added by the assembler to every risk (the rubric requires it; none of the twelve source parts' risk tables carried one). Cross-linked to the assumptions (§11) each depends on where applicable.

### 14.1 The assembler's decision on RSK-308 (task requirement 4)

**A3's RSK-308** ("Negligent selection — Price-only award; FMCSA data available, unused. No preemption shield post-*Montgomery*; the §4.1 gate is the only mitigation left") was carried in A3's own risk register, cross-referenced from A3 §4.1 and EC-307. A3 explicitly deferred the call on where it belongs to the assembler or A7, because it is cross-referenced from both a design precondition (§4.1) and an edge case (EC-307). **A7 filed a CHALLENGE** arguing this is no longer a risk-register line at all post-*Montgomery* — it is a **precondition on the award mechanism itself**.

**Decision: A7's challenge is accepted. RSK-308 is retired as a standalone risk-register entry.**

**Reasoning.** A risk-register entry, by convention, describes one of several probability-weighted outcomes that management can accept, mitigate, or transfer at its discretion — the register exists to let a business consciously choose its risk tolerance. RSK-308 as A3 originally framed it ("price-only award with FMCSA data unused") described exactly that kind of choice — *if* Boss chose to run an ungated price-only auction, this was the risk of doing so. But DEC-LOCK-001 (§2.1, §13.1) has already foreclosed that choice: **every mechanism option A3 presents at §8.3 runs on a gated pool; "price-only across all comers" is explicitly no longer a neutral fork available to select** (A3 §4.7: "every option below runs on a gated pool"). A risk that describes a design choice which the design no longer permits is not a residual risk — it is dead-letter text describing a state the document itself forbids. The substance A3's RSK-308 was protecting against has migrated from "a risk we might run" to "a precondition we have already built into every option" (§8.3 §4.1, points 1–5). That migration is exactly what a *precondition* is, and A7's characterisation is the more accurate one.

**What survives, and where it lives now, so nothing is silently dropped:**
- The **precondition itself** — price ranks within a gated pool, never defines it — is stated in full at §8.3 §4.1, and is now cross-referenced from EC-307 (tie where one bidder is worse on safety) rather than from a risk ID that no longer exists.
- The **residual risk that remains even after the gate exists** — the gate is imperfectly specified, imperfectly applied, or a genuinely qualified carrier still causes a serious accident — is not the same risk as RSK-308 and already has two homes, independently written by two agents who could not see each other's version: **RSK-014 (formerly A7's RSK-701)** and **RSK-025 (formerly A8's RSK-801)**. These are near-duplicates of each other (both: "serious-injury crash despite / because of the award rule, carrier awarded on price alone") and are cross-referenced against each other below rather than merged into one ID, since the task brief asked the assembler to decide RSK-308's home specifically, not to further consolidate A7 and A8's own registers. **Flagged as a finding no single agent could see** (§3.4-style): three separate parts (A3, A7, A8) each wrote their own version of "price-only award is a negligent-selection risk," and after DEC-LOCK-001 only two of the three versions still describe a genuine residual risk — the third (A3's) describes something the design no longer allows to happen.

### 14.2 Consolidated risk register (renumbered RSK-001…, origin preserved)

| ID | Risk | Category | P | I | Score | Origin | Mitigation | Owner |
|---|---|---|---|---|---|---|---|---|
| RSK-001 | Winner's curse — winner most underestimated cost, likeliest to re-trade or fail | Mechanism | 4 | 4 | 16 | A3 RSK-301 | §8.3 gate + BR-310 (recorded re-trade) | `[NEEDS INPUT]` |
| RSK-002 | Adverse selection — cheapest via a deficiency the gate misses (maintenance, unpaid drivers, minimum-only insurance) | Mechanism | 4 | 4 | 16 | A3 RSK-302 | §8.2 gate scope decision (DEC-201) | `[NEEDS INPUT]` |
| RSK-003 | **Post-award re-trade at the dock** — the biggest practical leak; a competitive award becomes a hostage negotiation, erasing OBJ-001 | Mechanism | 4 | 5 | 20 | A3 RSK-303 | BR-310 (recorded, unpayable if unrecorded); A11's fuel-floor flag (BR-1103) | `[NEEDS INPUT]` |
| RSK-004 | Service-quality collapse — only price is measured, so on-time/communication/claims decay | Mechanism | 4 | 4 | 16 | A3 RSK-304 | BR-816 (ratings decision, §8.9) | `[NEEDS INPUT]` |
| RSK-005 | Fraud attraction — double brokering, identity theft, fictitious pickup follow price-only award | Fraud | 4 | 5 | 20 | A3 RSK-305 | §8.2 BR-221/224 → §8.9 BR-806 | `[NEEDS INPUT]` |
| RSK-006 | Collusion / bid rotation — repeat carriers learn the lane's rotation | Legal/Antitrust | 3 | 5 | 15 | A3 RSK-306 | §8.3 BR-315; §8.7 BR-718 | `[NEEDS INPUT]` |
| RSK-007 | Shill / spoiler bids | Fraud | 3 | 3 | 9 | A3 RSK-307 | §8.3 BR-316/317 | `[NEEDS INPUT]` |
| — | ~~RSK-308 Negligent selection~~ | — | — | — | — | A3 | **Retired — see §14.1. Superseded by the precondition at §8.3 §4.1 and by RSK-014/RSK-025 below.** | — |
| RSK-008 | Bidder fatigue — low win rates or advisory awards → bidding stops → pool collapses with OBJ-001 | Mechanism | 4 | 4 | 16 | A3 RSK-309 | DEC-307 resolution (§13.1-adjacent) | `[NEEDS INPUT]` |
| RSK-009 | SAFER/FMCSA data staleness — slow recheck cadence lets a carrier present eligible after real-world lapse | Data/Compliance | `[NEEDS INPUT]` | `[NEEDS INPUT]` | — | A2 RSK-201 | Recheck cadence decision (open) | `[NEEDS INPUT]` |
| RSK-010 | DEC-201 Option A, if chosen unqualified, suppresses small-fleet/owner-operator liquidity (OBJ-003) | Commercial | `[NEEDS INPUT]` | `[NEEDS INPUT]` | — | A2 RSK-202 | DEC-201 decision (§8.2) | `[NEEDS INPUT]` |
| RSK-011 | Negligent-selection claim after a serious accident on a price-only award | Legal | 4 | 5 | 20 | A7 RSK-701 | §8.3 gate (DEC-LOCK-001); §8.7 BR-705/706; **cross-ref RSK-025 (A8's version, same fact pattern)** | `[NEEDS INPUT]` |
| RSK-012 | Unauthorised-brokerage finding under §13.1 answer D | Legal | 3 | 5 | 15 | A7 RSK-702 | Resolve §13.1 pre-launch | `[NEEDS INPUT]` |
| RSK-013 | Unlicensed money transmission under Model M3 | Legal | 3 | 5 | 15 | A7 RSK-703 | Payments counsel; no M3 without it (§8.7 §7.4) | `[NEEDS INPUT]` |
| RSK-014 | Incomplete 371.3 broker record | Compliance | 3 | 3 | 9 | A7 RSK-704 | §8.7 BR-703 | `[NEEDS INPUT]` |
| RSK-015 | Consignee privacy complaint, unconsented party | Legal/Privacy | 3 | 3 | 9 | A7 RSK-705 | §8.7 BR-714 | `[NEEDS INPUT]` |
| RSK-016 | Antitrust exposure from the bid-transparency design | Legal/Antitrust | 2 | 5 | 10 | A7 RSK-706 | §8.7 §7.9 item 7 (counsel) | `[NEEDS INPUT]` |
| RSK-017 | Serious-injury crash; carrier awarded on price alone, safety data unused | Legal | 2 | 5 | 10 | A8 RSK-801 | §8.9 BR-802 (merged into BR-303) + BR-803 | `[NEEDS INPUT]` |
| RSK-018 | Double-brokered load lost; carrier cargo and contingent cargo insurance both exclude it | Fraud/Insurance | 3 | 5 | 15 | A8 RSK-802 | §8.9 BR-804/806 + policy-wording review (ASM-027) | `[NEEDS INPUT]` |
| RSK-019 | Identity theft on a real MC's authority with a forged COI | Fraud | 4 | 5 | 20 | A8 RSK-803 | §8.9 BR-804/806/812 | `[NEEDS INPUT]` |
| RSK-020 | Platform found to have acted as a carrier despite intending broker/vendor status | Legal | 2 | 5 | 10 | A8 RSK-804 | Resolve `DEC-801` / §13.1 pre-build | `[NEEDS INPUT]` |
| RSK-021 | Claim denied — signed clear, damage reported late | Legal/Claims | 4 | 3 | 12 | A8 RSK-805 | §8.5 BR-504 (concealed-damage channel) | `[NEEDS INPUT]` |
| RSK-022 | Ratings built then ignored by a price-only mechanism | Mechanism | 4 | 3 | 12 | A8 RSK-806 | §8.9 BR-816 forces the decision | `[NEEDS INPUT]` |
| RSK-023 | Suspension strands freight mid-transit | Operational | 2 | 5 | 10 | A8 RSK-807 | §8.9 BR-818 | `[NEEDS INPUT]` |
| RSK-024 | Released-value limitation unenforceable; full-value exposure lands | Legal | 3 | 4 | 12 | A8 RSK-808 | §8.9 BR-810 | `[NEEDS INPUT]` |
| RSK-025 | Serious-injury crash after the award rule, safety data available, unused — **same fact pattern as RSK-011 (A7); not merged into one ID per the task brief's scope, but flagged as a near-duplicate finding no single agent could see** | Legal | 3 | 5 | 15 | A8 §8.9.3 narrative (distinct from RSK-801/RSK-017 above — this is the negligent-selection framing specifically, not the crash-outcome framing) | Same as RSK-011 | `[NEEDS INPUT]` |
| RSK-026 | Risk that a dispatcher accepts an award beyond authority granted internally by the carrier, creating a rate confirmation the carrier later disputes | Operational | `[NEEDS INPUT]` | `[NEEDS INPUT]` | — | A9 RSK-900 | §8.8 BR-902 + carrier-visible audit log | Platform (design) |
| RSK-027 | Platform-ops function understaffed relative to 24/7 freight movement, leaving exception states unresolved overnight | Operational | `[NEEDS INPUT]` | `[NEEDS INPUT]` | — | A9 RSK-901 | No number asserted — qualitative only | `[NEEDS INPUT: client operations lead]` |
| RSK-028 | Premise wrong — pain is coverage/vetting/admin, not price; sells against a solved problem (§3.1 W4) | Strategic | 4 | 5 | 20 | A10 RSK-1001 | P0 gate (§17.2); W5 answered by real shippers | Sponsor |
| RSK-029 | Negligent-selection tail post-*Montgomery* — one verdict exceeds cumulative margin | Legal | 3 | 5 | 15 | A10 RSK-1002 | Lowest-bid-among-qualified (DEC-LOCK-001); §8.2 gate | Sponsor + counsel |
| RSK-030 | Disintermediation — parties go direct after first match; LTV collapses | Commercial | 4 | 4 | 16 | A10 RSK-1003 | Fund one hold (§17.1); KPI-13 | Commercial |
| RSK-031 | Cold start never reached — liquidity spread thin; failed auctions poison both sides | Commercial | 4 | 4 | 16 | A10 RSK-1004 | Lane-dense seeding; failure state only after fallback (§8.3) | Commercial |
| RSK-032 | Cost-to-serve doesn't fall — `c_ops` flat with volume; the category's actual killer per Convoy's post-mortem | Financial | 4 | 5 | 20 | A10 RSK-1005 | KPI-12; P3 kill gate | Ops |
| RSK-033 | Fraud loss exceeds margin — double brokering, identity theft, fictitious pickup follow price-only award | Fraud | 4 | 5 | 20 | A10 RSK-1006 | §8.2 gate; KPI-10 | Risk |
| RSK-034 | Incumbent response — load boards add auction at subscription price; CHR/RXO undercut off a 13–15% margin base | Competitive | 4 | 4 | 16 | A10 RSK-1007 | Differentiate on a non-price hold | Sponsor |
| RSK-035 | Capital intensity — paying carriers before shippers pay consumes working capital linearly with GMV | Financial | 3 | 5 | 15 | A10 RSK-1008 | Model `c_capital`; cap float | Finance |
| RSK-036 | Freight-cycle exposure — model conceived for a loose market; 2026 spot +25% YoY | Market | 4 | 4 | 16 | A10 RSK-1009 | Stress-test tight-market case pre-launch | Sponsor |
| RSK-037 | No broker authority — unlawful to arrange for compensation without it; decides take-rate vs. SaaS | Regulatory | 3 | 5 | 15 | A10 RSK-1010 | Resolve §13.1 first | Sponsor |
| RSK-038 | Regulatory cost step-up — broker surety/trust minimum reported rising to $150,000 from July 2026 | Regulatory | 3 | 3 | 9 | A10 RSK-1011 | Fixed cost, not per-load; §8.7 confirms | Finance |
| RSK-039 | Antitrust surface — repeat lowest-bid auctions on fixed lanes create a bid-rotation pattern | Legal | 2 | 4 | 8 | A10 RSK-1012 | Bid-pattern monitoring (§8.3 BR-315) | Counsel |
| RSK-040 | Predecessor risk ignored — rebuilding what Convoy built with ~$1.1B, on less capital | Strategic | 3 | 4 | 12 | A10 RSK-1013 | Written differentiation vs. the three failures before P1 | Sponsor |
| RSK-041 | Fuel-only floor mistaken (internally or by counsel) for a full cost/rate floor, informing a decision it can't support | Mechanism/Data | 3 | 4 | 12 | A11 RSK-1100 | BR-1104's mandatory disclosure | `[NEEDS INPUT]` |
| RSK-042 | Route-feasibility false negative (an attribute simply absent from a record, not a real restriction) wrongly flags a legal load | Data | 3 | 3 | 9 | A11 RSK-1101 | ASM-041 verification | `[NEEDS INPUT]` |
| RSK-043 | Source licensing unresolved (OSM share-alike; scraped/derived price feeds' terms) — a shipped feature may need pulling post-launch | Legal/Data | 2 | 4 | 8 | A11 RSK-1102 | §8.11 `DEC-1200` | A12 |
| RSK-044 | Live-event coverage (4 states + CA) creates a false impression of national ETA/disruption coverage if not disclosed per-lane | Data | 3 | 3 | 9 | A11 RSK-1103 | Amended BR-1107 (§8.10) | `[NEEDS INPUT]` |
| RSK-045 | Scraped AAA diesel data reaches a client build | Legal | Low | High | — | A12 RSK-1200 | BR-1204 build gate | `[NEEDS INPUT]` |
| RSK-046 | ODbL records leave via endpoint or export and pull §4.6 onto the client's own database — **already happening today via `/v1/fuel`** | Legal/Data | Medium | High | — | A12 RSK-1201 | `DEC-1200` resolution — the single highest-urgency item in §8.11 | `[NEEDS INPUT]` |
| RSK-047 | Unverified state feeds contracted as features, then cut off | Operational/Legal | Medium | Medium | — | A12 RSK-1202 | BR-1209 (flagged off by default) | `[NEEDS INPUT]` |
| RSK-048 | Attribution stripped in a client-side redesign, silently | Legal | Medium | Medium | — | A12 RSK-1203 | BR-1200 automated per-payload check | `[NEEDS INPUT]` |
| RSK-049 | Boss's personal EIA key ships in a client product | Operational | Medium | Low-Medium | — | A12 RSK-1204 | BR-1208 | `[NEEDS INPUT]` |
| RSK-050 | Advisory routing presented as legal compliance — the largest non-licence exposure, landing on §8.9's negligent-selection surface | Legal | Medium | High | — | A12 RSK-1205 | BR-1207 (upstream limitation shown verbatim) | `[NEEDS INPUT]` |

---

## 15. Success Metrics / KPIs

**Loop-closing check performed:** every metric below traces to an objective already stated in §2 or a pain point already cited in §3; no new number is introduced here that wasn't already `[NEEDS INPUT]` upstream.

| ID | Metric | Baseline | Target | Measurement Method | Owner | Traces to |
|---|---|---|---|---|---|---|
| KPI-01 | Bids per closed auction (density) | `[NEEDS INPUT]` | ≥ n\* `[NEEDS INPUT]` | Auction log | Ops | OBJ-003 |
| KPI-02 | Coverage rate: published → award accepted | `[NEEDS INPUT]` | `[NEEDS INPUT]` | Lifecycle states | Ops | OBJ-002 |
| KPI-03 | Time to cover (`PUBLISHED`→`AWARD_ACCEPTED`) | `[NEEDS INPUT]` | `[NEEDS INPUT]` | State timestamps | Ops | OBJ-002 |
| KPI-04 | Award price vs. external lane benchmark | `[NEEDS INPUT]` | `[NEEDS INPUT]` | Third-party rate index | Commercial | OBJ-001 |
| **KPI-05 ⚖** | **On-time pickup + on-time delivery** | `[NEEDS INPUT]` | ≥ pre-platform baseline | POD/BOL timestamps (§8.5) | Ops | OBJ-001/004 |
| **KPI-06 ⚖** | **No-show + award-decline + re-trade at pickup** | `[NEEDS INPUT]` | `[NEEDS INPUT]` | Lifecycle exception states | Ops | OBJ-001 |
| **KPI-07 ⚖** | **Claims per 100 loads; claim $ per load** | `[NEEDS INPUT]` | `[NEEDS INPUT]` | Claims register (§8.9) | Risk | OBJ-004 |
| **KPI-08 ⚖** | **Safety profile of awarded carriers** — FMCSA BASIC percentile / authority age | `[NEEDS INPUT]` | No award outside §8.2's floor | Vetting record | Compliance | OBJ-007 |
| **KPI-09 ⚖** | **Double-brokering / identity-theft events per 1,000 loads** | `[NEEDS INPUT]` | `[NEEDS INPUT]` | Fraud register (§8.9) | Risk | OBJ-006 |
| KPI-10 | Contribution margin per load (`CM`) | `[NEEDS INPUT]` | > 0 before scaling spend | Finance | Finance | OBJ-001 |
| KPI-11 | `c_ops` per load and exception rate | `[NEEDS INPUT]` | Falling with volume | Ops time study | Ops | OBJ-002 |
| KPI-12 | Repeat rate and off-platform leakage — pairs matched here whose next load goes elsewhere | `[NEEDS INPUT]` | `[NEEDS INPUT]` | Pair cohort | Commercial | OBJ-003 |
| KPI-13 | CAC payback months, per side | `[NEEDS INPUT]` | `[NEEDS INPUT]` | Finance cohort | Finance | OBJ-003 |
| KPI-14 | Award-to-acceptance and lapse rates | `[NEEDS INPUT]` | `[NEEDS INPUT]` | Lifecycle states | Ops | OBJ-002 |
| KPI-15 | Re-trade rate: settled ≠ awarded, plus magnitude | `[NEEDS INPUT]` | `[NEEDS INPUT]` | Rate confirmation vs. final invoice (§8.6) | Finance | OBJ-001/005 |
| KPI-16 | Coverage-failure rate: auctions ending `FAILED_*` | `[NEEDS INPUT]` | `[NEEDS INPUT]` | Auction log | Ops | OBJ-002 |
| KPI-17 | Share of awards where the winner was not lowest | `[NEEDS INPUT]` | `[NEEDS INPUT]` | Award record (§8.3 merged BR-303) | Compliance | OBJ-006 |

**⚖ = counter-metric.** KPI-05 through KPI-09 exist specifically to catch the mechanism optimising price while destroying reliability and safety — carried forward from A10 without softening: **if KPI-04 (award price) improves while any of KPI-05–09 degrades, the mechanism is working exactly as designed, and the design is wrong.**

---

## 16. Acceptance Criteria

**Scoping decision, stated rather than silently under-delivered:** with 212 requirements across twelve domains, producing a full, independently-worded Given/When/Then block for every single one would mostly restate the Acceptance column already present in §8's tables — those acceptance conditions are already written as single verifiable clauses and are QA-testable without re-interpretation, satisfying the underlying rubric requirement even where they are not formatted as three explicit clauses. **Full Given/When/Then is provided below only for the highest-consequence requirements** — the merged award/selection record, the eligibility gate, and the requirements A9 already wrote in strict Given/When/Then form (BR-900–914, reproduced in §8.8). All other requirements' Acceptance columns in §8 are QA-ready and expandable to Given/When/Then 1:1 by whoever writes the test plan — this is a scoping choice for document length, not a coverage gap, and is recorded as such in `assembly-report.md`.

| AC ID | Given | When | Then |
|---|---|---|---|
| AC-BR301.1 | A carrier bids on a load without a current, matching COI on file | The bid is submitted | The bid is rejected before it is recorded or ranked in the auction |
| AC-BR302.1 | An award is about to be confirmed | The system re-checks authority and insurance at that moment | If either has lapsed since bid time, the award transitions to `AWARD_VOIDED_INELIGIBLE` before any commitment is made |
| AC-BR303.1 | An auction closes and an award is made | Anyone with access authority queries the award record later | The record reproduces, without live-source lookups: authority status, safety snapshot, insurance evidence, gate version, every bid with timestamp, the winner, the rule applied, and every excluded bidder with a stated reason |
| AC-BR303.2 | A plaintiff's counsel subpoenas the award record for a specific load after an accident (per A8's EC-824) | The record is retrieved | It shows why the winning carrier was selected and that FMCSA safety data was available and considered, not merely that the lowest price won |
| AC-BR400.1 | Freight is tendered at origin | The driver and shipper representative complete pickup | The shipment cannot transition to `PICKED_UP` without a pickup record bearing piece/pallet count, condition, seal number (if sealed), and both acknowledgements, timestamped |
| AC-BR501.1 | A consignee receives freight at the drop | The delivery receipt is signed | The record captures clear-or-exception as a mandatory discrete field; the field cannot be left blank or inferred from freetext |
| AC-BR603.1 | An invoice has nine clean lines and one line with an open OS&D dispute | The settlement cycle runs | The nine clean lines settle on schedule; the disputed line remains `HELD` independently, without blocking the other nine |
| AC-BR806.1 | §8.2's BR-221/224 signal fires (driver/tractor/MC mismatch at pickup) | The fraud-review desk receives it | A classified case (double-brokering / identity theft / disclosed substitution — no case) opens within the same shift, without re-running the verification A2 already performed |

**Go-live readiness checklist (requirement-referenced, sign-off authority per §5.2 — currently `[NEEDS INPUT]` throughout):**

| # | Checklist item | References | Sign-off authority |
|---|---|---|---|
| 1 | §13.1's regulatory-posture decision is recorded with authority evidence | CON-013, BR-701 | `[NEEDS INPUT: named client sponsor]` |
| 2 | The DEC-LOCK-001 gate is implemented and passes an audit sample showing no gate-fail award | BR-301–303 | `[NEEDS INPUT]` |
| 3 | A2's eligibility tuple computation is live and per-load, not a static onboarding flag | BR-200 | `[NEEDS INPUT]` |
| 4 | Every "Open" retention period in §8.7 §7.7 has been closed by counsel, not left at "Open" | §8.7 §7.7 | `[NEEDS INPUT: counsel]` |
| 5 | `DEC-1200` (ODbL serving boundary) is enforced in code, tested, and does not currently emit `osm.*` records over the live `/v1/fuel` endpoint (RSK-046) | BR-1203 | `[NEEDS INPUT]` |
| 6 | AAA scraped pricing is confirmed absent from the client build (build-gate test passes) | BR-1204 | `[NEEDS INPUT]` |
| 7 | Platform-ops staffing and after-hours coverage model exists, even if minimal | DEP-900 | `[NEEDS INPUT: client operations lead]` |
| 8 | A10's P0 phase gate has been run against at least one named shipper (§17.2) | RSK-028 | Sponsor |

---

## 17. Cost-Benefit / Business Case

**Anti-fabrication note, stated plainly rather than papered over: no unit-economics number appears anywhere in this section.** Boss supplied no volume, rate, or cost data (intake.md), and no TAM figure is asserted — vendor market-size estimates for this category diverge sharply and none was independently verified for this engagement (A10). What follows is the cost *structure* and the phase-gated investment logic A10 built in place of a numbers-based ROI, which this document cannot honestly produce.

### 17.1 Cost structure (equation, not a number)

`CM = (P_shipper − C_carrier) − c_ops − c_risk − c_capital − c_payment`

| Variable | Meaning | Real number owned by |
|---|---|---|
| `P_shipper` / `C_carrier` | Price charged / winning bid paid | `[NEEDS INPUT]` — §8.6 / §8.3 |
| `t` = take rate = `(P_shipper − C_carrier)/P_shipper` | Capped by incumbent gross margin — 13.3–14.8% (C.H. Robinson NAST, RXO brokerage, FY25, §3.2) | `[NEEDS INPUT]` |
| `c_ops` | `exception_rate × handling_minutes × loaded_labour_rate` | §8.8 (A9) |
| `c_risk` | `Σ (p_i × L_i)` over claim, fraud, no-show, negligent-selection tail | §8.9 (A8) |
| `c_capital` | `C_carrier × r × days_pay_gap / 365` | §8.6 (A6) |
| `c_payment` | Processing, factoring/NOA handling, 1099 admin | §8.6 (A6) |

`LTV_side = CM × loads_per_period × periods_retained` · `Payback = CAC_side ÷ (CM × loads_per_month)` · `Effective_CAC = (CAC_shipper + CAC_carrier) ÷ loads_before_leakage`

**Three hinge variables, carried forward without softening:** (1) `c_ops` at scale — Convoy's own post-mortem cited cost-to-serve, not price, as the actual failure driver; if `c_ops` nears take-rate dollars, volume cannot fix it. (2) `periods_retained` net of leakage — the disintermediation problem (§17.1 below). (3) `c_risk` post-*Montgomery* — a fat tail, not an average; one adverse verdict is a solvency event, not a line-item.

### 17.2 Phasing — what each release must *prove*, with a named kill criterion

**This is the investment-gating mechanism in lieu of a numbers-based ROI table.** Nothing beyond P1's lane class is built before P2 and P3 report.

| Phase | Must prove | Kill criterion |
|---|---|---|
| **P0 Premise** (no build) | Named shippers have loads they fail to cover at an acceptable price, and can say what they do today | Pain is admin/vetting, not price ⇒ re-scope entirely (§3.1 W5) |
| **P1 Liquidity**, one lane class | Density ≥ n\* from carriers passing §8.2's floor | Density unreachable inside budget |
| **P2 Fulfilment integrity** | KPI-05/06/07/09 (§15) ≥ incumbent baseline | Price wins, service loses ⇒ mechanism refuted |
| **P3 Unit economics** | `CM > 0` after real `c_ops` | Ops cost eats the take rate |
| **P4 Retention** | Repeat without leakage (KPI-12) | Leakage caps LTV below CAC ⇒ a matcher, not a business |

### 17.3 Disintermediation — the hold this document cannot assume is funded

Trading contacts on load #1 and booking load #2 direct is ordinary in US truckload; something other than the match must hold a pair on-platform. Five candidate holds, none funded by default: money (pay carrier faster than shipper pays platform — needs working capital, §8.6), risk transfer (platform carries claim + fraud loss — needs insurance/reserves), vetting-as-service (continuous FMCSA/insurance monitoring — needs ops cost, §8.2/§8.8), volume (aggregated flow no single shipper can offer — circular, needs liquidity first), contract (non-circumvention clause — weak, costly, hostile to enforce). **§8.10 (A11) explicitly rejected the client's own data-asset platform as a sixth hold** — session-level utility, not relationship-level lock-in. `[NEEDS INPUT: which hold will the client fund? If none, leakage is the base case, not a risk.]`

### 17.4 Downside case

If none of §17.3's holds are funded and P0's premise (§3.1 W1/W5) resolves to "the pain was price, and price is already solved by DAT/Truckstop" (§3.2 W4's own finding), this platform becomes, at best, a one-shot matcher with no repeat business (EC-1009, A10) — the CAC is spent once per pair and never recovered, regardless of what `CM` per load looks like in isolation. This is the single most likely failure mode named across all twelve parts, independently arrived at by A3 (§8.3, "the premise the business rests on," ASM-014) and A10 (§3.1, W4/W5).

### 17.5 "Do nothing" — the evaluated alternative

Per template requirement, the status quo is not silently assumed inferior. Shippers today have DAT, Truckstop, contract routing guides, and broker relationships — instruments that already perform price discovery well (§3.1 W4). The case *for* building is narrower than "better pricing": it rests on coverage certainty, vetting, admin burden, and fraud-resistance (§3.1 W5) — none of which is validated against a named shipper in this document. **Doing nothing costs Boss's client nothing beyond the status quo's already-known pain (cargo theft ~$725M/yr industry-wide, double-brokering ~$700M–$1B/yr, §3.2) — it does not cost the client the unvalidated upside this document also cannot quantify.**

### 17.6 Unquantified benefits — quarantined, not folded into the (absent) ROI

Per template requirement, these are named but never averaged into a return figure, because none is measured: a defensible, auditable selection record as a genuine legal asset post-*Montgomery* (§8.3 BR-303) rather than a pure cost centre; route-feasibility and fuel-floor signals reducing two specific named failure modes (§8.10) without being sold as a moat; a documented compliance posture (§8.7) that is itself a sales asset to risk-averse enterprise shippers, unmeasured here.

---

## 18. Glossary

| Term | Definition |
|---|---|
| **BOL** | Bill of Lading — the contract of carriage and the document the delivery signature sits on. "POD" in this market normally means a signed BOL / delivery receipt. |
| **POD** | Proof of Delivery — the signed BOL/delivery receipt, clear or with exception. |
| **OS&D** | Over, Short & Damage — a structured notation on a POD describing a quantity/condition discrepancy against the original BOL. Modelled as POD content, not a lifecycle state (§7.4). |
| **Carmack Amendment** | 49 U.S.C. §14706 — the federal regime governing interstate cargo loss and damage liability, including statutory minimum claim-filing (9 months) and suit-limitation (2 years) periods. |
| **FMCSA** | Federal Motor Carrier Safety Administration — the federal regulator of motor carriers and property brokers. |
| **MC / USDOT number** | Operating-authority identifiers issued by FMCSA; motor carrier and property broker are separate authorities. |
| **COI** | Certificate of Insurance. |
| **CDL** | Commercial Driver's License. |
| **HOS** | Hours of Service (49 CFR Part 395) — the federal limit on how long a driver may drive/be on duty. |
| **ELD** | Electronic Logging Device — the mandated device recording HOS compliance. |
| **TONU** | Truck Ordered Not Used — a fee owed to a carrier when a shipment is cancelled after the truck has been dispatched. |
| **NOA** | Notice of Assignment — the legal document directing payment to a factor instead of the carrier once a receivable is factored. |
| **CSA / SMS** | Compliance, Safety, Accountability program / Safety Measurement System — FMCSA's carrier safety-scoring framework (BASICs). |
| **BMC-84 / BMC-85** | Surety bond / trust fund instruments satisfying a property broker's financial-responsibility requirement (49 CFR 387.307). |
| **BOC-3** | Designation of process agents a broker/carrier must file per state of operation (49 CFR Part 366). |
| **49 CFR Part 371 / 387 / 395** | Federal regulations governing, respectively: property broker record-keeping; carrier/broker financial responsibility (insurance minimums); Hours of Service. |
| **Clearinghouse** | The FMCSA Drug & Alcohol Clearinghouse — the database of driver D&A violations, queried at pre-employment and annually. |
| **Reefer** | Refrigerated / temperature-controlled trailer equipment. |
| **Deadhead** | Empty miles driven by a truck with no freight, e.g. repositioning after delivery. |
| **Detention** | The accessorial charge owed when a carrier is held beyond agreed free time at a pickup or drop. |
| **Lumper** | A third-party laborer paid to load or unload a truck. |
| **Double brokering** | A carrier that wins a load re-brokers it, undisclosed, to a second, often unvetted, carrier — a major fraud vector in this market. |
| **Negligent selection** | A tort claim against the party (typically a broker) that selected a motor carrier, alleging the selection itself was unreasonably careless — the central legal exposure this document addresses, post-*Montgomery*. |
| **Montgomery** | *Montgomery v. Caribe Transport II, LLC*, 608 U.S. ___ (2026) — the Supreme Court decision removing FAAAA preemption as a defence to state-law negligent-selection claims against brokers, nationwide. |
| **MoSCoW** | Must / Should / Could / Won't — the prioritisation scheme used throughout §8. |
| **INVEST** | Independent / Negotiable / Valuable / Estimable / Small / Testable — the user-story quality standard (referenced but not separately re-run here; see `assembly-report.md`). |
| **RACI** | Responsible / Accountable / Consulted / Informed — the governance-role framework used in §5. |
| **ODbL** | Open Database License — the share-alike open data licence governing the OpenStreetMap-derived layers in §8.11. |
| **Produced Work** (ODbL term) | An aggregated/rendered output (e.g. a map, a corridor summary) derived from ODbL data that is exempt from share-alike obligations, distinct from serving the underlying records directly. |
| **NTAD / FHWA** | National Transportation Atlas Database / Federal Highway Administration — the US-government source of the truck-route, bridge, and tunnel data referenced in §8.10/§8.11. |
| **WZDx** | Work Zone Data Exchange — the state-DOT work-zone feed format referenced in §8.10/§8.11. |

---

## 19. Appendices

| Appendix | Purpose |
|---|---|
| A. `spine.md` | The canonical model all twelve parts drafted against — jurisdiction, entities, lifecycle, ID allocation, scope boundaries. Referenced throughout §2–§8; not reproduced in full here. |
| B. `DECISIONS.md` | The two locked decisions (DEC-LOCK-001, DEC-LOCK-002) and the two corrections filed against the manager, reproduced in relevant part at §2.1, §3.2, §4, §8.11. |
| C. `intake.md` | Boss's verbatim intake and the supplied-vs-not-supplied split underlying §3.1. |
| D. `classification.md` | The initial business-type and compliance-surface classification, including the mid-project jurisdiction correction (India → USA). |
| E. `part-A1-shipper.md` through `part-A12-data-licensing.md` | The twelve source drafts. Full edge-case registers (227 rows total across all twelve parts) are preserved in these source files at their original fidelity and are referenced, not fully reproduced, in §8 above to manage document length — see `assembly-report.md` for the per-part count and the reasoning behind this scoping choice. |
| F. `assembly-report.md` | The companion document to this BRD: every ID remap, de-dup, orphan, unresolved cross-reference, and per-section word count. |

**Full edge-case registers, not reproduced verbatim in §8:** A1 (12 rows) · A2 (15) · A3 (30) · A4 (25) · A5 (21) · A6 (10) · A7 (27) · A8 (42) · A9 (13) · A10 (11) · A11 (15) · A12 (6) — **227 total**, satisfying Boss's "nothing may be missed" mandate (spine §3) at the source-part level. Summarised and cross-referenced at point of relevance throughout §8; the assembler judged reproducing all 227 rows a second time in this document to be exactly the kind of padding anti-patterns.md warns against, given they already exist, fully itemised, in the twelve source files this BRD is built from and points to.

---

## 20. Sign-off / Approval Matrix

| Name | Role | Approving WHAT exactly | Date |
|---|---|---|---|
| `[NEEDS INPUT: named client business sponsor]` | Business Sponsor | Business requirements only — §2 through §17 as the client's stated need, not the specific `[NEEDS INPUT]` items still open | `[NEEDS INPUT]` |
| `[NEEDS INPUT: named client UAT owner]` | UAT Owner | §16 acceptance criteria and go-live checklist | `[NEEDS INPUT]` |
| `[NEEDS INPUT: named client counsel]` | Legal Sign-off | §8.7 §7.9, §8.9's `DEC-801`, §8.11 §7 — the counsel-handoff items specifically, not the document as a whole | `[NEEDS INPUT]` |
| Boss (Ujjawal) | Document commissioner / process owner | Process and structural completeness of this BRD as an artifact — **not** business validity, per the anti-patterns meta-rule (§Appendix below) | 2026-07-29 |

**No signature on this document should be read as validating the business premise (§3.1 W1/W5) or resolving §13.1's blocking decision.** Those require, respectively, a named shipper and the client's own counsel — neither of which this document had access to.

---

## Appendix — Readiness Report

**Score: 58/100.**

**The mandatory honesty caveat, stated first because it matters more than the number:** this score measures *structural* quality — ID discipline, traceability, MoSCoW/priority coverage, acceptance-condition presence, assumption-tagging discipline. **It does not, and cannot, measure whether these are the *right* requirements**, because the business premise underlying them (§3.1, W1 and W5) was never validated against a real shipper, and the single highest-leverage decision in the document (§13.1) was never made. A document can score high here and still be wrong about what the business needs — this is the anti-patterns meta-rule, and it is deliberately not smoothed over by the number above.

| Criterion | Score /100 | Basis |
|---|---|---|
| ID discipline / no collisions | 95 | Spine's per-agent block allocation (§5) worked as designed; zero collisions found across 212 requirements. One deliberate merge (BR-303/BR-802), one deliberate retirement (RSK-308), both reasoned and documented. |
| Traceability (requirement → objective) | 85 | Every requirement in §8 carries an OBJ trace. Weakness: several traces are compound (e.g. "006/007") without indicating which is primary, and four genuine orphans exist (§8.12). |
| MoSCoW / Fibonacci-equivalent prioritisation | 80 | MoSCoW applied consistently across all twelve domains. This document does not carry Fibonacci story-point estimates — that is an FRD/delivery-planning artifact, explicitly out of scope per §9. |
| Gherkin-grade acceptance criteria | 55 | High-consequence requirements have full Given/When/Then (§16); the remaining ~200 have single-clause verifiable acceptance conditions in §8, QA-testable but not reformatted into three explicit clauses — a stated scoping choice, not an oversight, but it is real and it lowers this sub-score honestly. |
| Anti-fabrication discipline | 90 | Every number in this document is either a Boss-supplied fact, a cited external source (regulatory citation, market data), or explicitly `[NEEDS INPUT]`/`[ASSUMPTION]`. Zero invented thresholds, rates, or dates. Deduction only for the residual honesty that a full 250-pointer cross-reference audit was not exhaustively completed (§8.12). |
| Compliance-awareness | 90 | DPDP/India-law content: zero residual instances found (verified — see `assembly-report.md`). US regime coverage (FMCSA, Carmack, CCPA/CPRA, Sherman Act, *Montgomery*) is extensive and current to 2026-07-29. |
| **Business validity (the axis this score cannot certify)** | **Not scored — see caveat above** | W1/W5 unanswered; §13.1 unanswered; ASM-014's premise ("shippers will trade latency for price and record") unvalidated. A high structural score must never be read as implying these are correct. |

**Top fixes, in priority order:** (1) Answer §13.1 — one decision resolves five `[NEEDS INPUT]` items simultaneously. (2) Run A10's P0 phase gate against a named shipper before writing another line of §8's content further. (3) Resolve `DEC-1200` (§8.11) before `/v1/fuel` or any ODbL-sourced endpoint ships in a client build — this is a live exposure today, not a future one (RSK-046). (4) Close the four orphans at §8.12. (5) Get counsel time against §8.7 §7.9 and §8.9's `DEC-801` — both are named, bounded, and ready for a lawyer, not further drafting.

---









