# Marketplace Payment Reconciliation & Claims-Recovery Agent
### A build-ready blueprint for an autonomous settlement-recon + claims-filing agent for Indian e-commerce sellers

> **One-line pitch:** An autonomous agent that doesn't just *flag* the money marketplaces silently skim from sellers — it *files and chases the claim to closure* across Amazon, Flipkart, Meesho and Nykaa, before the 7–60 day claim window slams shut.

> **Composite score:** 8.6 / 10 · **Industry:** E-commerce & Quick Commerce (India) · **Complexity:** Medium · **Automation potential:** High

---

## 0. The 30-Second Investor Thesis

Indian marketplace sellers lose **1–5% of revenue** to wrong commissions, mis-charged shipping, un-reimbursed lost/damaged inventory, TCS errors and return-adjustment leakage. Manual VLOOKUP reconciliation catches roughly **half** of it, and the recoverable half **expires** inside 7–60 day claim windows. Existing tools (Unicommerce, evanik, SellerApp, sellerrocket; globally GETIDA/Carbon6) **stop at the variance report** or run it as a **manual human service taking ~25% of recovery**. Nobody in India has shipped an agent that **drafts, files, and pursues every claim to credit autonomously**.

This is one of the cleanest ROI sells in Indian SaaS: the product **pays for itself in month one** out of money the seller had already written off. The wedge is the *autonomy* layer on top of a recon problem that is already validated by a half-dozen service businesses.

---

## 1. Problem & Business Case

### 1.1 What actually leaks

When a seller sells on a marketplace, the marketplace nets out a stack of deductions before paying the seller:

| Leakage category | What goes wrong | Typical claim window |
|---|---|---|
| **FEE — Commission** | Wrong category commission %, commission charged on cancelled/returned orders | 7–30 days (Flipkart), 60 days (Amazon FBA) |
| **FEE — Shipping/Weight** | Weight-slab over-charge (actual 450g billed as 1kg), wrong zone, double freight | 7–30 days |
| **TAX — TCS (Sec 52)** | TCS over-collected or GSTR-8 mismatch vs the seller's GSTR-2B | Raise before 10th of next month for GSTR-8 correction |
| **LOST / DAMAGED** | FBA/marketplace-warehouse units lost in inward, damaged in handling, customer-return not returned to inventory | Amazon: **60 days** (down from 18 months pre-2024) |
| **RETURN ADJUSTMENT** | Refund charged to seller but unit never came back, or returned damaged but not flagged | 7–30 days |
| **ROUNDING / DUPLICATE** | Duplicate fee lines, paise-level rounding drift across thousands of orders | 7–30 days |

### 1.2 Why this is getting *worse*, not better (the "why now")

- **Amazon's March 2025 reimbursement policy change:** lost/damaged inventory is now reimbursed at **manufacturing cost, not retail selling price** — sellers report recovery amounts dropping **50–75%** *unless* cost documentation (supplier invoices, per-unit cost) is submitted within 60 days. This turns reimbursement from "click a button" into a **document-assembly + deadline problem** — exactly an agent's job. (Source: Seller Labs, 2025; SalesDuo, 2025.)
- **Shrinking windows:** Amazon's lost/damaged claim window collapsed from 18 months to **60 days**. Flipkart GSTR-8 corrections must be raised **before the 10th of the following month**. Manual processes cannot keep pace at scale.
- **Multi-marketplace sprawl:** A serious seller now runs Amazon + Flipkart + Meesho + Nykaa + Quick-commerce (Blinkit/Zepto/Instamart) simultaneously — each with its own settlement format, portal, and dispute flow. Reconciliation surface area has multiplied.

### 1.3 Quantified cost of inaction

- Manual VLOOKUP recon catches only **~51% of variances**; an automated, line-level match pushes that to **~88%** [estimate, sector-sourced via Unicommerce/sellerrocket]. The gap — **~37 percentage points of variances** — is recoverable money that today silently expires.
- For a **₹100 Cr/yr GMV seller**, 1–5% leakage = **₹1–5 Cr/yr**; of which the recoverable-but-unclaimed slice (the part past the catch-rate gap and inside-window) is conservatively **₹40–80 lakh/yr** [estimate].
- Sellers onboarding to automated recovery typically recover **₹1–5 lakh in the first month** alone (back-claims still inside window) [estimate, sector-sourced].
- **The permanence trap:** unlike most cost problems, leaked money past the claim deadline is **gone forever**. Every week of inaction permanently destroys recoverable funds. This is what makes urgency a 9/10.

---

## 2. Agent Architecture

### 2.1 Orchestration pattern

A **Planner → Router → specialist Workers → Critic** topology with a shared blackboard memory and a **human-in-the-loop (HITL) gate** on high-value or low-confidence claims. The Planner owns the per-seller recovery campaign; the Router dispatches each variance to the right worker chain; the Critic validates every drafted claim before filing and every "credit confirmed" before closing.

This is **not** a single mega-prompt. It is a deterministic recon core (cheap, auditable, no hallucination tolerance) wrapped by LLM agents only where judgement and language generation are genuinely needed (classification edge cases, claim drafting, portal navigation, follow-up correspondence).

### 2.2 The agents

| # | Agent | Role | Key tools | LLM-heavy? |
|---|---|---|---|---|
| **A0** | **Campaign Planner** | Owns the recovery campaign per seller per settlement cycle; sequences recon → draft → file → follow-up; enforces budgets & deadlines | Scheduler, deadline-calendar, state store | Light (planning) |
| **A1** | **Recon Engine** | Deterministically matches settlement-report lines ↔ orders/returns; computes expected vs actual; emits raw variances | Polars/DuckDB matching, fee-schedule lookup, fuzzy order-id join | **No — deterministic** |
| **A2** | **Variance Classifier** | Labels each variance: FEE / TAX / ROUNDING / LOST-DAMAGED / RETURN-ADJ / DUPLICATE; assigns confidence + recoverability | RAG over fee schedules & policy docs, classifier model | Yes |
| **A3** | **Evidence Assembler** | Gathers the proof pack per claim: order id, settlement line, fee-schedule citation, supplier invoice (for cost-basis FBA claims), return tracking | Doc store, OCR for invoices, GST/order API pulls | Medium |
| **A4** | **Claim Drafter** | Composes each dispute in the **correct per-marketplace format & tone** (Amazon case, Flipkart SPF ticket, Meesho support, GSTR-8 correction note) | Per-marketplace templates, RAG over policy, generation model | Yes |
| **A5** | **Filer / Portal Operator** | Submits via API where available, else drives the seller portal (browser automation); captures case ID | Marketplace seller APIs, browser-automation (CDP/Playwright), CAPTCHA-pause | Medium |
| **A6** | **Follow-up & SLA Tracker** | Tracks case SLA, sends polite escalations, parses marketplace replies, re-files on rejection with stronger evidence | Email/portal poller, reply-parser, escalation templates | Yes |
| **A7** | **Credit Reconciler** | Confirms the credit actually landed in a later settlement, attributes it to the claim, closes the loop, books it to Tally/Zoho | Settlement re-match, accounting connector | Light |
| **A8** | **Critic / Guardrail** | Validates every drafted claim (factual grounding, no over-claiming, within window, evidence attached) before A5 files; validates every "closed" before A7 books | Verification rubric, policy checker, value-threshold gate | Yes |

### 2.3 Memory design

- **Episodic** (per claim): full reasoning trace, evidence pack, every portal interaction, marketplace replies — the audit log a seller/CA can defend.
- **Semantic / knowledge** (shared): vectorised + structured store of marketplace fee schedules, dispute-success patterns ("Flipkart accepts weight-slab disputes when you attach the carrier manifest"), rejection-reason → counter-argument mappings. **This is the compounding moat** — the more claims filed, the smarter the drafting/follow-up.
- **Procedural**: per-marketplace filing playbooks (API contracts + portal click-paths), versioned because portals change.
- **Working / blackboard**: the live campaign state shared across A0–A8 for one settlement cycle.

### 2.4 Text diagram

```
                         ┌──────────────────────────┐
  Settlement report ───▶ │   A0  CAMPAIGN PLANNER     │ ◀── deadline calendar
  Order/return data ──▶  │  (sequences + budgets +    │
  Fee schedules (RAG) ─▶ │     deadline enforcement)  │
  GSTR-8 / GSTR-2B ───▶  └────────────┬──────────────┘
                                      │ dispatch
                         ┌────────────▼──────────────┐
                         │   A1  RECON ENGINE          │  deterministic
                         │  (Polars/DuckDB match,      │  match rate 51%→88%
                         │   expected vs actual)       │
                         └────────────┬──────────────┘
                                      │ raw variances
                         ┌────────────▼──────────────┐
                         │  A2  VARIANCE CLASSIFIER    │  FEE/TAX/ROUNDING/
                         │  (+confidence,recoverable?) │  LOST-DAMAGED/RETURN
                         └────────────┬──────────────┘
                                      │
                ┌─────────────────────┼──────────────────────┐
                ▼                                            ▼
   ┌────────────────────────┐                  ┌────────────────────────┐
   │ A3 EVIDENCE ASSEMBLER   │                  │   ROUTER (per claim)    │
   │ proof pack + invoices   │                  │ pick marketplace flow   │
   └────────────┬───────────┘                  └────────────┬───────────┘
                ▼                                            ▼
   ┌────────────────────────┐                  ┌────────────────────────┐
   │   A4  CLAIM DRAFTER     │ ───────────────▶ │  A8 CRITIC / GUARDRAIL  │
   │ per-marketplace format  │                  │ grounded? in-window?    │
   └────────────────────────┘                  │ over-claim? evidence?   │
                                                └────────────┬───────────┘
                            ┌────── reject/redraft ──────────┤
                            │                                ▼ pass
            ╔═══════════════▼═══════════════╗   ┌────────────────────────┐
            ║  HITL GATE  (value > ₹X or     ║──▶│  A5 FILER / PORTAL OP   │
            ║   confidence < Y → approve)    ║   │ API or browser submit   │
            ╚═══════════════════════════════╝   └────────────┬───────────┘
                                                             │ case IDs
                                              ┌──────────────▼───────────┐
                                              │ A6 FOLLOW-UP / SLA TRACKER│
                                              │ chase, parse, re-file     │
                                              └──────────────┬───────────┘
                                                             │ credited
                                              ┌──────────────▼───────────┐
                                              │  A7 CREDIT RECONCILER     │
                                              │ confirm in settlement,    │
                                              │ book to Tally/Zoho, close │
                                              └───────────────────────────┘
```

---

## 3. Multi-Agent Workflow (trigger → output)

1. **Trigger.** New settlement report drops (weekly/biweekly per marketplace) OR a deadline-watcher fires (claim window closing in N days). A0 opens a campaign.
2. **Ingest & normalise.** Connectors pull settlement reports, order/return data, and fee schedules; normalise to a canonical settlement schema (each marketplace mapped once).
3. **Recon (A1, deterministic).** Line-level match of settlement ↔ orders ↔ returns. Compute expected fee/TCS/shipping from published schedules; diff against actual. Emit raw variances. **No LLM here** — fully auditable arithmetic.
4. **Classify (A2).** Each variance → category + confidence + "recoverable?" + claim-window deadline. Uses RAG over fee/policy docs for edge cases.
5. **Evidence (A3).** Assemble the proof pack per recoverable variance. For Amazon lost/damaged post-March-2025, pull **supplier invoice / per-unit manufacturing cost** (the new mandatory doc).
6. **Draft (A4).** Compose each claim in the right format: Amazon case, Flipkart SPF ticket, Meesho/Nykaa support, or a GSTR-8 correction note for the CA.
7. **🔴 CRITIC GATE (A8).** Every draft validated: claim is grounded in the evidence, not over-claimed, inside the window, evidence attached, dedupe vs already-filed. Fail → bounce back to A4 (max N redraft loops, then escalate to human).
8. **🟡 HUMAN-IN-THE-LOOP GATE.** Claims **above a configurable value threshold** (e.g. > ₹10,000) OR **below a confidence threshold** queue for one-tap seller approval. Everything else auto-proceeds. *(This is the only mandatory human checkpoint — by design, low-risk high-volume claims flow autonomously.)*
9. **File (A5).** Submit via seller API where available; otherwise drive the portal via browser automation (using the seller's own logged-in session; CAPTCHA → pause-and-notify). Capture the case/dispute ID.
10. **Follow-up (A6).** Poll case status against SLA. Parse marketplace replies. On "need more info" → re-supply from evidence pack. On rejection → redraft with a stronger counter-argument (learned pattern). Escalate stale cases.
11. **Confirm credit (A7).** When a later settlement shows the credit, match it to the claim, mark recovered, **book the entry to Tally/Zoho Books**, close the loop.
12. **Output.** A live recovery dashboard: ₹ recovered, in-flight, recovered-vs-leaked %, match-rate, claims by stage, and a per-claim audit trail. Monthly recovery statement the seller's CA can rely on.

---

## 4. Data Sources & Integrations

### 4.1 Systems to connect

| Layer | System | What we pull / push | Today's silo |
|---|---|---|---|
| **Marketplace — Amazon** | SP-API (Settlement reports, FBA inventory, Reimbursements), Seller Central case log | Settlements, lost/damaged, fees | Locked in Seller Central; manual CSV export |
| **Marketplace — Flipkart** | Flipkart Seller API / Seller Hub | Settlement, commission, shipping, returns | Portal-only for many flows |
| **Marketplace — Meesho** | Meesho Supplier panel / API | Payments, returns, penalties | Largely portal |
| **Marketplace — Nykaa / Quick-comm** | Nykaa seller portal; Blinkit/Zepto/Instamart panels | Settlement & deductions | Mostly portal, no clean API |
| **Accounting** | **Tally Prime** (TDL/ODBC/connector), **Zoho Books API** | Book recovered credits, reconcile ledgers | Disconnected from marketplace data |
| **Tax / Compliance** | **GST portal — GSTR-8** (TCS filed by marketplace) vs seller **GSTR-2B/2A** | TCS mismatch detection, correction notes | CA does this manually, monthly |
| **Fee schedules** | Published marketplace rate cards (commission, weight-slab, closing fees) | Ground truth for "expected" charges | PDF/HTML, change frequently → RAG + versioning |
| **Logistics** | Carrier manifests / weight data (where available) | Evidence for weight-slab disputes | Often only on portal |

### 4.2 Data contracts

- **Canonical Settlement Schema:** one normalised model `{order_id, sku, gmv, commission_actual, commission_expected, shipping_actual, shipping_expected, tcs_actual, tcs_expected, return_flag, settlement_date, marketplace}` — every marketplace mapped to this once. All downstream agents operate on the canonical model, so adding a marketplace = one adapter, not a rewrite.
- **Evidence Pack contract:** `{claim_id, variance_ref, fee_schedule_citation, source_docs[], cost_invoice?, window_deadline, confidence}`.
- **Claim Outcome contract:** `{claim_id, case_id, status, marketplace_reply, credited_amount, credited_settlement_ref, audit_trail[]}`.

### 4.3 Integration reality check

API coverage is uneven: **Amazon SP-API is rich**, Flipkart is partial, **Meesho/Nykaa/quick-comm are largely portal-only.** Architecture must therefore be **API-first with a browser-automation fallback** that operates the seller's authenticated session — this is also the single biggest moat and the biggest ops risk (portals change; ToS).

---

## 5. Automation vs Human

| Fully autonomous (Tier 1–2) | Human-in-the-loop (Tier 3) |
|---|---|
| Settlement ingest & normalisation | Approve claims **above ₹ value threshold** |
| Deterministic recon & variance detection | Approve **low-confidence** classifications |
| Variance classification (high-confidence) | First-time onboarding of a new marketplace flow |
| Evidence assembly (incl. invoice OCR) | Anything the Critic flags as ambiguous/risky |
| Claim drafting | CAPTCHA / 2FA interrupts (pause-and-notify) |
| Filing low-value, high-confidence claims | Reviewing systemic disputes (escalation to marketplace account manager) |
| SLA follow-up & polite escalation | Sign-off on the monthly recovery statement (optional) |
| Credit confirmation & accounting book-back | |

Design principle: **autonomy scales with confidence × inverse-value.** Thousands of small, high-confidence claims flow without a human; the rare large or fuzzy ones get a one-tap approval. This keeps the seller in control of money-moving actions while still automating the 90% tail that manual processes never get to.

---

## 6. Tech Stack (2026)

| Concern | Choice | Why |
|---|---|---|
| **Recon core** | **Polars / DuckDB** on the canonical schema | Deterministic, fast on millions of lines, zero hallucination, fully auditable |
| **Orchestration** | **LangGraph** (stateful graph, HITL interrupts, checkpointing) primary; Claude Agent SDK for the worker agents | Native human-in-loop interrupts + durable state = exactly this workflow; graph maps 1:1 to the agent diagram |
| **Reasoning models** | **Claude (Sonnet-tier)** for drafting/follow-up/critic; **a small fast model (Haiku-tier)** for high-volume classification; reserve a frontier model only for hard edge cases | Cost discipline — classification runs at scale, so route cheap; drafting & critic need judgement |
| **Retrieval / RAG** | Hybrid (BM25 + vector) over fee schedules, policy docs, dispute-pattern KB; rerank | Fee schedules change; grounded citations are mandatory to avoid over-claiming |
| **Browser automation** | **Playwright / Chrome DevTools Protocol**, scout-then-act on ARIA tree, CAPTCHA-pause, operates seller's authenticated session | Portal fallback where no API; survives DOM changes better than selector scripts |
| **OCR / doc** | Layout-aware OCR for supplier invoices (cost-basis FBA claims) | March-2025 Amazon rule makes invoice cost extraction mandatory |
| **Eval / guardrails** | Promptfoo/Ragas-style eval suite on classification + drafting; the **A8 Critic** as runtime guardrail; value-threshold + window-deadline hard gates; **over-claim detector** (never claim more than evidence supports) | Filing a wrong/inflated claim damages the seller's standing with the marketplace — guardrails are non-negotiable |
| **State / memory** | Postgres (campaign + claim state, audit trail) + vector store (dispute-pattern KB) | Auditability is a feature for sellers and their CAs |
| **Deployment** | **Multi-tenant cloud (VPC-isolated per tenant)** default; **on-prem / private-VPC option** for ₹100 Cr+ sellers and aggregators who treat settlement data as sensitive | Indian mid-market accepts cloud; large/enterprise + aggregators often demand VPC/on-prem — offer both |
| **Security** | Per-tenant credential vault, scoped marketplace API tokens, no plaintext portal passwords, full action audit log | Handling financial data + acting in seller's account demands least-privilege + traceability |

---

## 7. Expected ROI & Payback

- **Self-funding by construction.** First-month recovery (back-claims still inside window) of **₹1–5 lakh** typically exceeds the entire annual subscription — payback is **within the first settlement cycle (days–weeks), not months.**
- For a ₹100 Cr seller recovering ₹40–80 lakh/yr [estimate] against a SaaS+success fee that nets the seller the large majority, ROI is comfortably **>10x.**
- Against the brief's 3–12 month anchor, this sits at the **extreme fast end (<1 month effective payback)** — among the cleanest ROI stories in Indian SaaS, because the product recovers *cash the customer had already written off.*
- **Pricing implication:** a **hybrid model** — modest SaaS base (predictable revenue, covers recon/compute) **+ a success fee on recovered funds (10–15%, undercutting the 25% global service standard of GETIDA/Carbon6)** — aligns incentives and makes the buy a no-brainer. The success fee is the growth engine; the SaaS base is the floor.

---

## 8. Implementation Complexity, Risks & Mitigations

**Overall complexity: Medium.** The recon core is well-understood; the *autonomy* (filing + follow-up to closure across heterogeneous portals) is the genuinely hard, defensible part.

| Risk | Severity | Mitigation |
|---|---|---|
| **Portal changes break automation** (no/partial APIs on Meesho/Nykaa/quick-comm) | High | ARIA-tree scout-then-act (resilient to DOM drift); API-first with browser fallback; per-marketplace playbook versioning + monitoring; human-pause on anomaly |
| **Marketplace ToS / account standing** — automated filing could be throttled or flagged | High | Ethical pacing, daily caps, operate seller's own session with consent, never over-claim (Critic gate), prefer official APIs; position as "assisting the seller," seller approves money-moving actions |
| **Over-claiming / wrong claims** harm seller's relationship with marketplace | High | A8 Critic hard-gate: every claim grounded in evidence + within window; over-claim detector; HITL on high-value |
| **Amazon March-2025 cost-basis rule** shrinks reimbursements & adds doc burden | Medium | Built-in invoice OCR + cost-doc assembly is turned into a *feature/wedge* — most manual sellers can't keep up with the 60-day doc requirement |
| **Shrinking claim windows** (60 days / GSTR-8 by 10th) | Medium | Deadline-watcher trigger; campaign Planner prioritises by expiry; first-month back-claim sweep on onboarding |
| **Data sensitivity / trust** — handling settlement + GST data | Medium | VPC isolation, on-prem option, credential vault, full audit trail, SOC2-track |
| **False sense of completeness** (seller assumes 100% caught) | Low–Med | Transparent match-rate reporting; show "estimated remaining leakage" honestly |
| **Classification accuracy on edge cases** | Medium | Deterministic recon does the heavy lifting; LLM only classifies; eval suite + confidence-gated HITL |

---

## 9. TAM / SAM / SOM — India (with math)

> All figures **[estimate]**, triangulated from public sources (see Sources). Leakage logic: India online-retail GMV ≈ **$70 Bn (~₹5.8 lakh Cr) FY25**, projected ~$214 Bn by FY30 (ICICI Securities). Third-party-seller GMV is a large share of marketplace GMV; recoverable leakage ≈ a sliver of that seller GMV.

**TAM (total recoverable leakage, India):**
- Take **third-party seller GMV ≈ ₹2.5–3 lakh Cr/yr** [estimate] (marketplace 3P portion of total e-retail).
- Recoverable leakage ≈ **0.5–1% of that GMV** (the *recoverable-and-claimable* slice, narrower than total 1–5% leakage).
- → **TAM ≈ ₹1,500–2,500 Cr/yr** of recoverable leakage. *The "value-at-stake" market; the SaaS-capturable portion is a fraction of this.*

**SAM (serviceable — mid-to-large multi-marketplace sellers):**
- The sellers worth automating are the **multi-marketplace mid-large cohort** (roughly tens of thousands of sellers, the heavy tail of Amazon's ~700k + Flipkart + Meesho's ~400k + Nykaa).
- They hold the majority of leak-able GMV. Their recoverable leakage ≈ **₹400–700 Cr/yr** [estimate].

**SOM (3-year obtainable):**
- Realistic share of SAM with a focused India GTM: **~10–15%** → **₹50–100 Cr/yr of recovered funds run-rate** [estimate].
- At a blended monetisation of ~15–25% of recovered funds (SaaS base + success fee), that's a **₹10–25 Cr/yr revenue SOM** [estimate] — a credible Series-A-scale standalone business, larger if quick-commerce settlement recon is bolted on.

**Sensitivity:** the single biggest swing variable is **what fraction of recoverable leakage is actually claimable inside-window with proper evidence** — the product's match-rate and speed *directly expand its own TAM* by rescuing money that would otherwise expire.

---

## 10. Competitive Landscape & Wedge

| Player | Type | Strength | Gap (our wedge) |
|---|---|---|---|
| **Unicommerce** | India, recon module in OMS | Distribution, OMS install base | Stops at variance flagging; not autonomous claim filing |
| **evanik** | India, seller tools | Recon reports | Report-led, manual claims |
| **SellerApp** | India/global analytics | Analytics depth | Insights, not end-to-end recovery to closure |
| **sellerrocket** | India, **service-led** | Hands-on recovery service | Human service = doesn't scale, opaque, slow |
| **ReconPe / SaySeller / gonukkad** | India, recon tools | Cheap recon | Flag-only; no autonomous filing |
| **GETIDA / Carbon6 (Seller Investigators)** | Global (Amazon-centric) | Mature recovery, **25% success fee** | Amazon-only, US/EU focus, **not built for India's Flipkart/Meesho/Nykaa/GSTR-8 reality**, large manual-ops component |
| **TrueOps / Refully** | Global | Lower fees (10–18%) | Amazon-only, no India multi-marketplace, no GST/TCS |

**The wedge, in one sentence:** *Every incumbent stops at the variance report or runs recovery as a slow human service taking ~25%.* We are the **only end-to-end autonomous claims-to-closure agent built natively for India's multi-marketplace + GST/TCS reality**, charging a lower success fee because the work is automated.

**Defensibility / moat (compounding):**
1. **Dispute-pattern knowledge base** — every filed claim teaches the system which arguments + evidence win on which marketplace. Incumbents' reports don't generate this loop.
2. **Per-marketplace filing playbooks** (API + portal) — hard, unglamorous integration work that compounds and is painful to replicate.
3. **GST/TCS + GSTR-8 native** — global tools simply don't have this; Indian tools don't have the autonomy.
4. **Outcome-aligned pricing** — success fee on real recovery builds trust no flag-only tool can match.

---

## 11. Startup Verdict

### Verdict: **BUILD** — fundable, high-probability standalone startup.

**Probability of success: High (≈ 65–70%)** for reaching a venture-scale Indian SaaS outcome, conditional on nailing the portal-automation/ToS execution risk.

**Why it's fundable:**
- **Validated pain, validated willingness-to-pay** — a half-dozen service businesses already exist on this exact problem; we're productising + automating the bottleneck (filing/follow-up) they do by hand.
- **Cleanest-possible ROI sell** — pays for itself in month one from money already written off. Shortest sales cycle in the category.
- **Outcome-based pricing** kills the "is it worth it?" objection — the buyer risks nothing.
- **Real moat** via the dispute-pattern flywheel + integration depth + GST-native positioning.
- **Tailwinds** — shrinking claim windows + Amazon's cost-basis rule make the *manual* alternative strictly worse, widening the wedge.

**Key risk that caps the probability:** marketplace **ToS + portal-automation durability** and **account-standing sensitivity**. Mitigated by API-first design, ethical pacing, never over-claiming, operating with seller consent on their own session, and HITL on money-moving high-value actions.

**GTM motion:**
1. **Wedge product = Amazon + Flipkart reimbursement/recovery on success-fee-only** (zero-risk to seller, fastest land). Land with the first-month back-claim sweep — instant visible ₹ recovered.
2. **Expand** to Meesho/Nykaa/quick-commerce + full recon + GST/TCS module → move to hybrid SaaS+success-fee.
3. **Channel:** partner with **CAs / accounting firms / OMS vendors / seller-aggregators (roll-ups)** who own seller relationships and feel this pain in bulk.
4. **Land-and-expand within aggregators** — a single roll-up brings dozens of seller accounts.

**Ideal ICP:** multi-marketplace seller / brand / aggregator doing **₹10 Cr–₹500 Cr GMV/yr**, selling on 2+ marketplaces incl. FBA, with messy manual reconciliation and a finance/CA function that already knows money is leaking but can't chase it. Sweet spot: **roll-ups and aggregators** (concentrated demand, sticky, high LTV).

**Moat summary:** dispute-pattern KB (data flywheel) × per-marketplace filing playbooks (integration moat) × GST/TCS-native (geographic moat) × outcome-aligned pricing (trust moat). None of the four exists together in any incumbent today.

---

## Sources

- [Amazon FBA inventory reimbursement policy — Seller Central](https://sellercentral.amazon.com/help/hub/reference/external/G200213130?locale=en-US)
- [Amazon FBA Reimbursement Guide 2025 — SalesDuo](https://salesduo.com/blog/amazon-fba-reimbursement-claim-guide/)
- [Amazon's 2025 Reimbursement Policy Update (manufacturing-cost basis) — Seller Labs](https://www.sellerlabs.com/blog/amazon-2025-fba-reimbursement-policy-change/)
- [Amazon Reimbursement Policy details & updates — Carbon6](https://www.carbon6.io/blog/amazon-reimbursement-policy/)
- [Flipkart Seller Settlement Reconciliation: TCS, Fees — TransactIG](https://www.terra-insight.com/insights/flipkart-seller-settlement-reconciliation/)
- [Amazon & Flipkart Payments Reconciliation Guide — Unicommerce](https://unicommerce.com/blog/amazon-flipkart-payment-reconciliation-guide/)
- [Flipkart Payment Reconciliation and Settlement Error Guide — sellerrocket](https://sellerrocket.in/flipkart-payment-reconciliation.html)
- [Flipkart Settlement Reports & Reconciliation 2026 — gonukkad](https://www.gonukkad.com/blog/flipkart-settlement-reports-reconciliation)
- [Seller Investigators (Carbon6) — Amazon reimbursement software & 25% fee](https://www.carbon6.io/seller-investigators/)
- [Best Amazon Reimbursement Software 2026 (GETIDA/TrueOps/Refully fees) — Levi's Toolbox](https://levistoolbox.com/best-amazon-reimbursement-software/)
- [India E-commerce market size & seller counts — IBEF](https://www.ibef.org/industry/ecommerce)
- [India e-comm to hit $214 Bn by FY30 (ICICI Securities) — Brands Awareness](https://www.brandsawareness.com/business/flipkart-leads-gmv-maus-as-india-e-comm-market-may-hit-214-bn-by-fy30-icici-securities/)
- [India E-Commerce Marketplaces 2025 (Amazon/Flipkart/Meesho GMV) — MerchantSpring](https://merchantspring.io/resources/india-ecommerce-marketplaces-social-quick-commerce-2025)

*Figures tagged [estimate] are triangulated, not audited. Validate seller-GMV split and recoverable-leakage % with a design-partner cohort before fundraising.*
