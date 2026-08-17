# RA-Bill & Working-Capital Recovery Agent ("Cash Chaser") — Build-Ready Blueprint

**Industry:** Construction & Infrastructure (EPC) — India
**Agent class:** Billing & Receivables Recovery (multi-agent)
**Composite opportunity score:** 9 / 10
**Document type:** Investor + engineering blueprint (founder-ready)
**Prepared:** 2026-06-23

> **Governing thought (Pyramid Principle):** EPC contractors in India are sitting on the worst cash-conversion in years — only ~29% of FY26 operating profit arrived as cash, the rest trapped in unbilled work, slow RA bills, retention and disputed claims. An EPC-native multi-agent system that *auto-generates RA bills from measurement books, files them on owner portals, reconciles certified-vs-paid-vs-retention, and runs MSME-Act-aware autonomous collections* attacks the single largest, most quantifiable pain in the sector — with a payback measured in **months, not years**. This is the highest-conviction quick-win in the India agentic-AI opportunity map.

---

## I. Situation · Complication · Question (SCQ)

- **Situation.** India's EPC sector is large and growing in topline (large diversified EPC revenue projected +9–11% in FY26, per Crisil). RA bills (Running Account bills) are the lifeblood payment instrument — periodic interim invoices for progressive work, built from measurement books (MB) + BOQ, validated against contract, and filed on owner/PSU portals.
- **Complication.** Topline grew but **cash didn't**. Cash collected from operations fell to ~**29% of operating profit in FY26**, versus a historical average near **65%** (Source: The Core, 2026). Of every ₹100 of profit, ~₹71 is stuck — in unpaid bills, retention money, unbilled work, and disputed claims. Government/PSU tender awards also fell ~18% in FY26, so the *existing* order book must be monetised harder. ERPs record bills but don't auto-generate them from MBs, don't validate against contract, don't file on owner portals, and don't run escalating evidence-backed follow-up. The MSMED Act's statutory 3×-bank-rate delayed-payment interest and Section 43B(h) tax disallowance are under-leveraged as collection levers.
- **Question.** Can a multi-agent AI system materially compress the RA-bill-to-cash cycle for Indian EPC contractors — enough to be a fundable, defensible SaaS business?

**Answer:** Yes — high conviction. The pain is acute, quantifiable in ₹, regulation is creating new collection leverage right now, and no incumbent owns the *EPC-native RA-bill auto-prep + portal filing + MSME-aware autonomous collections* wedge.

---

## II. Problem & Business Case

### 2.1 The pain, sharpened

The contractor is effectively extending an **interest-free loan to the owner**. Work is executed and certified, but cash lags by 90–180+ days across four leak points:

1. **RA-bill prep latency.** Billing engineers manually compile MBs + BOQ into RA bills. A single RA bill on a large package can take days; errors trigger rejection and re-cycling.
2. **Filing friction.** Each owner/PSU runs its own e-billing portal (NHAI, railways, state PWDs, private owners). Manual upload + format mismatch + missing annexures = rejection.
3. **Reconciliation gap.** Certified ≠ billed ≠ paid ≠ retention-released. Tracking lives in spreadsheets; nobody has a single real-time AR truth.
4. **Ad-hoc collections.** Follow-up is calls/emails when someone remembers. No escalation ladder, no evidence package, no statutory-interest leverage.

### 2.2 Cost of inaction (quantified)

| Metric | Value | Source / basis |
|---|---|---|
| Cash collected vs operating profit, FY26 | ~29% (vs ~65% historical) | The Core, 2026 |
| Profit trapped per ₹100 of profit | ~₹71 | Derived from above |
| On a ₹100 cr operating-profit contractor | ₹71 cr blocked | Direct |
| Interest drag financing that block @ ~10% | **~₹7.1 cr / year** | [estimate] |
| On a ₹500 cr-revenue contractor (≈₹50 cr OP @10% margin) | ~₹35 cr blocked → ~₹3.5 cr/yr drag | [estimate] |

**Value created.** Cutting Days Sales Outstanding (DSO) by **15–30 days** on a ₹500 cr-revenue contractor frees **tens of crore** of working capital. Interest savings alone repay the SaaS in **2–4 months** [estimate]. Add MSMED-Act statutory interest recovery (3× RBI bank rate, compounded monthly — a hard legal right that *cannot be waived by contract*) and the recovery upside grows further.

### 2.3 Why now

- **Acute cash crunch** (29% conversion is a multi-year low) makes CFOs receptive to a cash-recovery tool *this quarter*.
- **MSMED Act + Section 43B(h)** (effective FY24, biting through FY26) gives MSE sub-contractors and MSME-registered EPC players a statutory interest + tax-disallowance hammer that is currently under-used. The agent operationalises this.
- **Agentic AI is now reliable enough** for document-grounded extraction + tool-calling + human-in-loop workflows at enterprise quality.

---

## III. Agent Architecture

### 3.1 Orchestration pattern

**Planner → Router → Specialist Workers → Critic**, with a shared **Project Ledger** (long-term memory) and **per-task scratchpad** (short-term memory). A supervising **Orchestrator (Planner)** decomposes the goal ("get RA bills filed and paid for Project X"), routes to the right worker agent, and a **Critic/Validator** gates every externally-visible artifact (bill, filing, demand notice) before a human checkpoint.

This is a *supervised hierarchical* topology — not a free-for-all swarm — because every output touches money, contracts, and statutory exposure. Determinism and auditability beat autonomy here.

### 3.2 The agents

| # | Agent | Role | Key tools | Memory |
|---|---|---|---|---|
| 0 | **Orchestrator / Planner** | Decompose goal, sequence work, route, manage HITL gates, maintain state | LangGraph state machine, task queue, policy engine | Project Ledger (R/W) |
| 1 | **Bill-Prep Agent** | Generate RA bill from MB + BOQ; compute quantities, rates, deductions, taxes; validate against contract clauses | MB/BOQ parser (OCR + table extraction), contract RAG, quantity calculator, GST/tax engine | Contract index, rate library |
| 2 | **Contract-Compliance Critic** | Adversarially check the draft bill vs contract: rates, ceilings, price escalation, retention %, deduction rules, ceiling on variation | Contract RAG, rules engine, diff/anomaly detector | Contract index |
| 3 | **Filing Agent** | Format + submit RA bill to the correct owner/PSU e-billing portal; attach annexures; capture acknowledgement/submission ID | Portal connectors (RPA + API where available), document assembler, format validator | Portal-spec registry |
| 4 | **Reconciliation Agent** | Track certified vs billed vs paid vs retention-due vs retention-released; flag short-payments & deductions | ERP-AR connector, bank/GST reconciliation, ledger differ | Project Ledger (R/W) |
| 5 | **Collections Agent** | Run escalating, evidence-backed follow-up; compute MSMED statutory interest; draft demand / interest / legal-escalation notices | Email/WhatsApp/letter drafting, MSMED interest calculator, escalation-ladder policy, evidence packager | AR aging, comms history |
| 6 | **Audit/Trace Logger** | Immutable reasoning trace + decision log for every money-touching action (compliance + dispute defence) | Append-only event store | Audit store |

### 3.3 Text diagram

```
                              ┌──────────────────────────┐
   Trigger (MB closed /       │   ORCHESTRATOR / PLANNER  │
   billing cycle / payment    │   (LangGraph supervisor)  │
   due / portal update)  ───▶ │  decompose · route · gate │
                              └─────────────┬────────────┘
                                            │ routes
        ┌───────────────┬───────────────────┼───────────────────┬────────────────┐
        ▼               ▼                    ▼                   ▼                ▼
 ┌────────────┐  ┌──────────────┐    ┌──────────────┐   ┌──────────────┐  ┌──────────────┐
 │ Bill-Prep  │  │  Compliance  │    │   Filing     │   │ Reconcilia-  │  │ Collections  │
 │  Agent (1) │─▶│  Critic (2)  │─┐  │  Agent (3)   │   │ tion Agt (4) │  │  Agent (5)   │
 └─────┬──────┘  └──────────────┘ │  └──────┬───────┘   └──────┬───────┘  └──────┬───────┘
       │   MB+BOQ → draft RA bill │         │ submit          │ track          │ chase
       ▼                          ▼         ▼                 ▼                ▼
 ┌─────────────────────────────────────────────────────────────────────────────────────┐
 │  SHARED PROJECT LEDGER (long-term memory)  +  AUDIT/TRACE STORE (agent 6, append-only) │
 │  contracts · BOQ · MB · rate library · AR aging · portal IDs · comms · reasoning trace │
 └─────────────────────────────────────────────────────────────────────────────────────┘

 HUMAN-IN-LOOP GATES:
   ⛔ G1  Billing Head approves draft RA bill  ── before Filing Agent submits
   ⛔ G2  Finance approves legal/MSME escalation ── before demand/legal notice goes out
   (optional) ⛔ G3  CFO approves write-off / settlement on disputed claims
```

### 3.4 Memory design

- **Long-term (Project Ledger):** per-project graph — contract terms, BOQ, MB history, rate library, AR aging, portal submission IDs, payment certificates. Vector + structured store (RAG over contracts; SQL/columnar over financials).
- **Short-term (scratchpad):** per-task working state for a single bill/collection cycle, discarded after gate-pass.
- **Episodic (Audit/Trace):** append-only log of every agent decision with inputs, retrieved evidence, model output, and human action — for dispute defence and regulator/owner audit.

---

## IV. Multi-Agent Workflow (trigger → output)

```
TRIGGER: MB for billing period closed  OR  scheduled billing cycle  OR  payment overdue
   │
1. Orchestrator opens a Billing Task; pulls contract + BOQ + MB from Project Ledger.
   │
2. Bill-Prep Agent → parses MB (OCR + table extraction), maps line items to BOQ,
   computes quantities × rates, applies deductions (retention, advance recovery, LD),
   computes GST → produces DRAFT RA BILL + line-by-line reasoning trace.
   │
3. Compliance Critic → diffs draft vs contract (rates, ceilings, escalation, retention %,
   variation limits). Flags anomalies. If FAIL → loops back to Bill-Prep with reasons.
   │
   ⛔ G1  HUMAN: Billing Head reviews draft + flags → APPROVE / EDIT / REJECT.
   │  (approve)
4. Filing Agent → assembles annexures, formats to the specific owner portal spec,
   submits via portal connector (API or RPA), captures acknowledgement/submission ID,
   writes ID to Ledger.
   │
5. Reconciliation Agent (continuous) → polls ERP-AR + portal + bank/GST; tracks
   CERTIFIED vs BILLED vs PAID vs RETENTION. Detects short-payment / unexplained deduction
   / certification delay → raises a Collection Task.
   │
6. Collections Agent → builds AR aging; selects escalation rung per policy:
       Rung 1: polite reminder (auto, email/WhatsApp)
       Rung 2: certified-vs-paid discrepancy notice + evidence pack (auto-draft)
       Rung 3: MSMED statutory-interest demand (3× RBI bank rate, compounded) [if MSE]
       Rung 4: legal escalation / MSEFC Samadhaan filing draft
   │
   ⛔ G2  HUMAN: Finance approves any Rung-3/4 (statutory/legal) notice before it sends.
   │  (approve)
7. OUTPUT: filed RA bills, real-time AR truth dashboard, recovered cash, statutory-interest
   claims, full audit trace. Orchestrator updates Ledger + closes/loops tasks.
```

**What's autonomous vs gated:** Steps 1–3, 5, 6-Rung-1, and all reconciliation/drafting run autonomously. **G1 (file a bill)** and **G2 (legal/MSME escalation)** are hard human gates — these are money- and reputation-bearing and must never auto-fire.

---

## V. Data Sources & Integrations

| System | Role | Integration | Siloed today? |
|---|---|---|---|
| **Measurement Books (MB)** | Source of executed quantities | OCR + table extraction (PDF/scans), or digital-MB API (Powerplay/Zepth/in-house) | Yes — paper/PDF/site app, not in ERP |
| **BOQ** | Contract line items + rates | Excel/PDF parse; ERP project module | Partially — Excel-bound |
| **Contract / Agreement** | Rates, retention %, escalation, LD, variation rules | Document RAG (clause-level) | Yes — PDF in a folder |
| **ERP — SAP / Oracle / Tally / in-house** | AR ledger, payment certificates, GL | OData/BAPI (SAP), REST (Oracle), Tally XML/ODBC | Records bills; can't generate/file/chase |
| **Owner / PSU e-billing portals** | Bill submission + certification status | API where available; RPA (DOM/ARIA-tree) elsewhere | Heavily siloed, per-owner |
| **GST (GSTN/IRP)** | Tax validation, e-invoice, recon | GSP API | Separate |
| **Banking / payments** | Payment confirmation, reconciliation | Bank statement API / account aggregator | Separate |
| **MSME Samadhaan / MSEFC** | Statutory delayed-payment filing | Portal connector + doc assembler | Manual today |
| **Comms — email / WhatsApp Business** | Collections outreach | SMTP/Graph + WhatsApp Cloud API | Ad-hoc |

**Data contracts.** Define typed schemas (Pydantic v2 / JSON Schema) for: `MeasurementEntry`, `BOQLine`, `RABillDraft`, `ContractTerms`, `ARLedgerEntry`, `CertificationStatus`, `CollectionAction`. Every connector must emit validated, source-tagged records into the Ledger; reject-and-quarantine on schema violation.

---

## VI. Automation vs Human

| Stays autonomous | Stays human (gated) |
|---|---|
| MB/BOQ parsing & quantity computation | Approving the RA bill before filing (G1) |
| Draft RA-bill generation + tax calc | Approving statutory/legal escalation (G2) |
| Contract-compliance diff & anomaly flags | Settlement / write-off decisions (G3, optional) |
| Portal formatting + submission mechanics | Negotiation calls with owner officials |
| Reconciliation (certified/billed/paid/retention) | Relationship-sensitive judgement calls |
| AR aging, Rung-1 reminders, evidence packaging | Final sign-off on MSEFC Samadhaan filing |
| MSMED interest computation, notice drafting | — |
| Audit-trace logging | — |

Target: **~80% of effort automated**, with humans spending their time only on the two highest-stakes approvals and relationship work.

---

## VII. Tech Stack (2026)

- **Reasoning models:** Frontier model (Claude / GPT-class) for planning, contract reasoning, notice drafting; a cheaper fast model (Haiku/mini-class) for routing, extraction QA, and reminder drafting. **Document VLM** for MB/BOQ table & scan extraction.
- **Orchestration:** **LangGraph** (stateful supervisor graph, deterministic gates, checkpointing/resume) — or Agent SDK equivalent. Hard HITL interrupt nodes at G1/G2.
- **Retrieval / RAG:** Hybrid (BM25 + dense) over contracts/BOQ with clause-level chunking + a reranker; structured retrieval (SQL/DuckDB) over financials. **No free-text math** — quantities/interest computed by deterministic tools, never the LLM.
- **Connectors:** SAP (OData/BAPI), Oracle/Tally adapters, GST GSP, WhatsApp Cloud API; **RPA layer** (Playwright + ARIA-tree scout-then-act) for owner portals lacking APIs.
- **Eval & guardrails:** Promptfoo/Inspect-style eval suites on a gold set of MBs+contracts → bills; numeric-accuracy checks (bill totals must reconcile to the rupee); PII/contract-confidentiality guardrails; injection defence on portal/email inputs; the **Compliance Critic** as a model-level guardrail; **100% human gate** on money-out actions.
- **Deployment:** **VPC / on-prem-first** is mandatory — contract terms, rates, and AR are highly sensitive and competitively explosive. Offer (a) customer-VPC deployment, (b) on-prem with self-hosted open-weight models for the most conservative PSUs/large EPCs, (c) SaaS-multitenant only for SMB tier. Region-pinned (India) data residency.

---

## VIII. Expected ROI & Payback

**Worked example — ₹500 cr-revenue EPC contractor:**

- DSO compression: **15–30 days** → frees **~₹20–40 cr** working capital [estimate].
- Interest saved @ ~10%: **~₹2–4 cr / year** [estimate].
- Plus: MSMED statutory-interest recovery, fewer rejected bills (faster certification), reclaimed billing-engineer hours.
- SaaS price (anchor): **₹40–80 lakh / year** for a contractor this size (value-based, a fraction of interest saved).
- **Payback: 2–4 months** on interest savings alone. The recovered working capital is the headline; the SaaS fee is rounding error against it.

**Implementation ROI window:** 3–6 months to first measurable cash impact (pilot on 2–3 live projects), full payback inside the first year. Anchors squarely in the 3–12 month target.

---

## IX. Implementation Complexity, Risks & Mitigations

**Overall complexity: Medium.** The AI (extraction, reasoning, drafting) is well within 2026 capability. The hard parts are *integration breadth* and *trust*.

| Risk | Severity | Mitigation |
|---|---|---|
| Owner-portal fragmentation (no APIs, frequent UI change) | High | ARIA-tree scout-then-act RPA (survives DOM change); start with top-5 owner portals by ₹ exposure; HITL fallback for new portals |
| Numeric/contract errors in bills (money-bearing) | High | Deterministic calc tools, Compliance Critic, rupee-level reconciliation gate, mandatory G1 human approval |
| Data-security / contract confidentiality | High | VPC/on-prem-first, India data residency, RBAC, audit trace, optional self-hosted models |
| ERP heterogeneity (SAP vs Tally vs custom) | Medium | Adapter pattern + typed data contracts; start with SAP + Tally (covers most) |
| Adoption / change resistance from billing teams | Medium | Position as assistant that removes drudgery + keeps human in control; show ₹ recovered fast |
| MSMED/legal misfire damaging owner relationship | Medium | G2 finance gate on all statutory/legal notices; tone-graduated escalation ladder |
| Hallucinated clause interpretation | Medium | Clause-level RAG with citations; Critic cross-check; human gate |

---

## X. TAM / SAM / SOM (India) — with math

> All figures **[estimate]**, triangulated for sizing direction, not precision.

- **TAM ≈ ₹2,000 cr/yr** — total addressable spend for billing + AR automation across the Indian EPC universe. *Rough basis:* EPC is a multi-lakh-crore output sector; assume the addressable pool of mid/large contractors with meaningful RA-bill volume can justify ~₹2,000 cr/yr of billing/AR-automation software spend.
- **SAM ≈ ₹500 cr/yr** — contractors large enough (≳₹100 cr revenue) with the digital maturity + working-capital pain to buy an EPC-native agentic product in the next 3–5 years (~25% of TAM).
- **SOM (3-yr) ≈ ₹60 cr/yr** — realistic capture: land ~75–120 contractors at ₹40–80 lakh ACV. ~12% of SAM. *Math:* 100 logos × ₹60 lakh avg ACV = ₹60 cr.

**Expansion vectors beyond core:** % of statutory interest recovered (success fee), sub-contractor payables side, supply-chain financing referral fees, multi-project portfolio analytics.

---

## XI. Competitive Landscape & Wedge

| Player | What they do | Gap vs this opportunity |
|---|---|---|
| **HighRadius** (global AR/O2C) | Enterprise AR automation, cash app | Not EPC-native; no RA-bill prep from MB/BOQ, no Indian owner-portal filing, no MSMED leverage |
| **SAP/Oracle billing modules** | Record bills, AR ledger | Don't *generate* bills from MBs, don't validate vs contract, don't file on portals, don't chase |
| **Powerplay** | Field progress + labour + some billing/MB on mobile | Strong field capture, weak on contract-validated auto-bill + portal filing + autonomous statutory collections |
| **Zepth / RealX / construction ERPs** | Project mgmt, BOQ, estimating | Tracking/recording, not agentic auto-prep + autonomous evidence-backed recovery |
| **Generic collections SaaS** | Dunning workflows | Industry-agnostic; no EPC contract logic, no MSMED-Act engine, no portal mechanics |

**The wedge (unowned today):** *EPC-native* RA-bill auto-prep **from measurement book + BOQ, contract-validated**, **filed on Indian owner/PSU portals**, with **MSMED-Act-aware autonomous, evidence-backed collections** — end-to-end, MB-to-cash. Nobody connects all four. The defensibility compounds with the contract/rate/portal-spec knowledge graph and the audit-trace dataset of what actually gets bills certified and paid.

---

## XII. Startup Verdict

**Verdict: BUILD — fundable, high-conviction quick-win.**

**Probability of success: High** (relative to the opportunity map). Rationale:
- **Pain is acute and ₹-quantified** (29% cash conversion; ~₹71 of every ₹100 profit trapped) — CFOs feel it *this quarter*.
- **Payback in months** makes the buying decision near-trivial; you sell against an interest line, not a software budget.
- **Regulatory tailwind** (MSMED Act + 43B(h)) creates a fresh, under-used collection lever the product monetises.
- **Clear unowned wedge** — incumbents are either generic (HighRadius/SAP) or stop at tracking (Powerplay/Zepth).
- **Risks are integration/trust, not science** — solvable with VPC deployment, deterministic calc, and human gates.

**GTM motion:** Land via the **CFO / Finance Controller** (cash is their pain) with a **pilot on 2–3 live projects**, priced on a *share of working-capital/interest saved* to crush adoption friction; prove ₹ recovered in 60–90 days; expand portfolio-wide; then land-and-expand into payables + portfolio analytics. Direct/founder-led enterprise sales for large EPCs; partner channel (ERP integrators, construction-software resellers) for mid-market.

**Ideal ICP:** Indian EPC/infra contractors, **₹100 cr–₹2,000 cr revenue**, heavy government/PSU client mix (worst payment delays), SAP or Tally on the back end, MSME-registered or with large MSE sub-contractor base (maximises statutory leverage), with an internal cash-conversion crisis already on the board agenda.

**Moat:** (1) Proprietary **owner-portal-spec + contract-clause + rate knowledge graph** that's painful to rebuild; (2) **outcome data** on what gets bills certified and paid faster (a learning flywheel); (3) **switching cost** once it's the system of record for AR truth; (4) **regulatory-engine depth** (MSMED interest + Samadhaan) that generic players won't bother to build for one vertical.

---

## Sources

- [Built On Credit: Unpaid Government Bills Are Squeezing India's EPC Contractors — The Core](https://www.thecore.in/opinion/the-plinth/government-bills-epc-contractors-lt-ncc-limited-865850)
- [EPC revenue to grow 9–11% in FY26: Crisil — IBEF](https://www.ibef.org/news/revenue-of-large-diversified-engineering-procurement-and-construction-epc-companies-to-grow-9-11-in-fy26-crisil)
- [EPC Sector Revenue Growth to Slow in FY26 — India Ratings (NBMCW)](https://www.nbmcw.com/news/epc-sector-revenue-growth-to-slow-in-fy26-india-ratings-research.html)
- [Delayed Payments to MSEs under the MSME Act, 2006 — Lexology](https://www.lexology.com/library/detail.aspx?g=dc0c35e8-d98e-4e84-a05f-fa7a5213c3bd)
- [MSME Samadhaan — Delayed Payment Monitoring System](https://samadhaan.msme.gov.in/)
- [India MSME 45-Day Payment Rule: Section 43B(h) Explained](https://invoicedataextraction.com/blog/india-msme-45-day-payment-rule)
- [Running Bill (RA Bill) in Construction India 2026 — Construction Estimator India](https://constructionestimatorindia.com/running-bill-ra-bill-in-construction-india/)
- [Best Construction Management Software for Indian Contractors 2026 — Nway ERP](https://www.nwayerp.com/best-construction-management-software-india-2026/)

*Figures tagged [estimate] are sizing approximations for direction, not audited values.*
