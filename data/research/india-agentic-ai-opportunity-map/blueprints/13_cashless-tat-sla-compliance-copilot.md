# Cashless TAT/SLA Compliance Copilot — Build-Ready Blueprint

**Category:** Claims SLA Orchestration / Compliance Agent
**Industry:** Insurance (Health, Life, General) — India
**Composite opportunity score:** 8.05 / 10
**Document type:** Investor- and engineering-ready blueprint
**Last updated:** 2026-06-23

> **One-line pitch:** An autonomous multi-agent copilot that watches every in-flight cashless claim against IRDAI's hard regulatory clocks (1-hour auth, 3-hour discharge, 30-day reimbursement), predicts which claims will breach, and chases the missing documents across hospital + TPA + policyholder *before* the clock expires — turning a reactive penalty-exposure problem into a measurable, auditable compliance machine.

---

## 1. Problem & Business Case

### 1.1 What changed (why now)

IRDAI's **Master Circular on Health Insurance Business (29 May 2024)** — which superseded 55 prior circulars — locked in hard, non-negotiable turnaround clocks that are now fully live and enforced:

- **Cashless authorization within 1 hour** of receiving the request from the hospital.
- **Final discharge authorization within 3 hours** of the discharge request. *"In no case shall the policyholder be made to wait to be discharged."* Any additional hospital charges from a >3-hour delay must be borne **from the insurer's shareholder fund** — i.e., it hits profit, not the policyholder.
- **Reimbursement claims settled within ~30 days** (with penal interest at bank rate + 2% on delay).
- **₹5,000/day penalty** for non-compliance with Insurance Ombudsman awards (under the Insurance Ombudsman Rules) plus penal interest.

(Sources: [IRDAI Master Circular, 29 May 2024](https://irdai.gov.in/documents/37343/365525/); [Life Insurance International](https://www.lifeinsuranceinternational.com/news/irdai-cashless-claim-approval/); [Policybazaar](https://www.policybazaar.com/health-insurance/general-info/news/no-more-waiting-irdai-mandates-cashless-claim-within-hour/))

### 1.2 The operational reality (the complication)

The clocks are hard; the operating model is soft. Today a cashless claim crosses **3-4 organizational boundaries** — hospital insurance desk → TPA → insurer claims team → (back to hospital for missing docs) — coordinated over **email, phone, and WhatsApp**. The handoff between **TPA and insurer is the single biggest breakage point**, and it is not instrumented or agent-coordinated.

Consequences visible in the data:
- **Health insurance now accounts for ~75–80% of all insurance grievances** in India and complaints have **doubled in six years** ([Insurance Business Mag](https://www.insurancebusinessmag.com/asia/news/life-insurance/latest-india-data-finds-complaints-clustered-in-insurance-segment-565197.aspx)).
- The TPA layer alone processes **>1 crore (10M+) health claims/year**; Medi Assist alone handles **10M+ claims annually across 32 insurer partners and 28.5K provider tie-ups** ([Medi Assist](https://mediassisttpa.in/)).
- Star Health logged **~51 complaints per 100,000 insured** — the highest in the CIO table — illustrating how TAT/grievance exposure varies wildly by carrier.

### 1.3 Why existing approaches fail

| Current approach | Why it fails the 2026 clock |
|---|---|
| MIS / BI dashboards | Report breaches **after** they happen. Lagging, not leading. |
| Workflow queues (TPA tools) | Track status but don't autonomously act, chase, or re-route. |
| Email/phone document chasing | Human-paced, business-hours-bound, untracked, lossy at handoffs. |
| Escalation desks | Trigger only after a human notices the SLA is already amber/red. |

Nobody has a system that **predicts** a breach hours ahead and **autonomously closes the gap** (chasing docs, re-routing, escalating) while leaving the medical adjudication to a human.

### 1.4 Quantified cost of inaction

For a **large health insurer / large TPA** processing ~3-5M cashless claims/year:

| Cost driver | Annual estimate (₹) | Basis |
|---|---|---|
| Ombudsman award penalties (₹5,000/day × delayed awards) + penal interest | ₹3-8 Cr [estimate] | Hundreds of adverse awards × multi-week delays |
| >3-hr discharge overruns charged to shareholder fund | ₹4-12 Cr [estimate] | Per-incident hospital surcharges × breach volume |
| Reimbursement penal interest (bank rate +2%) | ₹2-6 Cr [estimate] | Delayed-settlement pool |
| Manual chasing / ops labor (BPO + escalation desks) | ₹6-15 Cr [estimate] | Headcount currently absorbing the coordination |
| NPS / persistency drag, regulatory scrutiny, brand | Hard to bound; material | Health = ~75-80% of complaints |
| **Aggregate exposure (large carrier)** | **₹15-40 Cr/yr [estimate]** | Sum of above, conservative |

**Bottom line:** the penalty and remediation cost is large enough that even a single-digit-Cr SaaS contract pays for itself in one quarter once breach rate drops.

---

## 2. Agent Architecture

### 2.1 Design philosophy

A **router-orchestrated planner-worker pattern** with a dedicated critic/guardrail layer and an always-on audit ledger. The key constraint: agents **coordinate and chase, they do not adjudicate the medical/financial merit of a claim** — that stays human-in-the-loop. This keeps us on the right side of IRDAI and limits liability.

### 2.2 The agents

| # | Agent | Role | Tools | Memory |
|---|---|---|---|---|
| 0 | **Orchestrator (Router/Planner)** | Owns the claim lifecycle; decides which worker acts next; maintains per-claim plan + state machine | LangGraph state graph, claim state store, policy ruleset | Per-claim working memory (graph state) |
| 1 | **SLA-Clock Agent** | Computes time-remaining against each IRDAI timer for every in-flight claim; emits amber/red events | Timer service, IRDAI rule engine (1h/3h/30d), business-calendar handling | Short-term (per-claim clock state) |
| 2 | **Risk-Predictor Agent** | Scores P(breach) using claim features (doc completeness, TPA, hospital, hour-of-day, claim type) | ML model (gradient-boost + LLM reasoning over notes), feature store | Long-term (historical breach patterns) |
| 3 | **Document-Chaser Agent** | Autonomously requests missing docs from hospital/TPA/policyholder in vernacular | WhatsApp Business API, email, voice (TTS/IVR), doc-checklist tool, OCR/IDP for inbound docs | Per-claim conversation memory + doc-requirement KB |
| 4 | **Router/Escalation Agent** | Re-assigns or escalates stuck claims to the right human/queue before breach | Ticketing API, ACL/queue routing, on-call/escalation matrix | Org routing graph |
| 5 | **Audit Agent** | Logs every event, decision, and message with timestamp + reason → immutable IRDAI proof trail | Append-only ledger, evidence packager, reg-report generator | Long-term immutable store |
| 6 | **Critic / Guardrail Agent** | Validates each outbound action (no PII leaks, no medical advice, vernacular correctness, no over-chasing) before it executes | Policy LLM, PII scrubber, rate-limiter, prompt-injection filter | Policy KB |

### 2.3 Orchestration pattern

```
                          ┌──────────────────────────────────────┐
   CLAIM EVENTS  ───────► │        ORCHESTRATOR (Router/Planner)   │
  (PAS, TPA feed,         │     LangGraph state machine per claim   │
   NHCX, hospital)        └───┬───────────┬───────────┬───────────┘
                              │           │           │
                  ┌───────────▼──┐  ┌─────▼──────┐  ┌─▼────────────┐
                  │ SLA-Clock    │  │ Risk-      │  │ Document-     │
                  │ Agent (1)    │  │ Predictor  │  │ Chaser (3)    │
                  │ time-to-     │  │ Agent (2)  │  │ WA/email/voice│
                  │ breach       │  │ P(breach)  │  │ vernacular    │
                  └──────┬───────┘  └─────┬──────┘  └──────┬───────┘
                         │                │                │
                         └────────┬───────┴────────┬───────┘
                                  │                │
                        ┌─────────▼──────┐   ┌─────▼──────────┐
                        │ Router/Escalate│   │ CRITIC/GUARDRAIL│ ◄─ every
                        │ Agent (4)      │   │ Agent (6)       │    outbound
                        └─────────┬──────┘   └─────┬──────────┘    action
                                  │                │
                       ┌──────────▼────────────────▼─────────┐
                       │   HUMAN-IN-THE-LOOP (Claims Manager) │
                       │   approves AUTH / DENY / final pay   │
                       └──────────────┬───────────────────────┘
                                      │
                              ┌───────▼────────┐
                              │  AUDIT AGENT(5)│ ──► immutable IRDAI
                              │  append-only   │      evidence ledger
                              └────────────────┘
```

**Reasoning trace (per claim):** Orchestrator records a structured trace — `event → clock state → risk score → chosen action → critic verdict → execution result → audit hash` — so every autonomous step is explainable and replayable for a regulator.

### 2.4 Memory model

- **Working memory:** LangGraph per-claim graph state (current node, doc checklist, clock).
- **Episodic:** conversation history per claim (vernacular chase threads).
- **Semantic/long-term:** vector + relational store of doc-requirement rules, hospital/TPA behavior profiles, historical breach patterns (feeds Risk-Predictor).
- **Immutable ledger:** append-only audit store (WORM/hash-chained) for IRDAI proof.

---

## 3. Multi-Agent Workflow (Trigger → Output)

```
TRIGGER: New cashless pre-auth / discharge request lands (PAS or TPA feed or NHCX)
   │
1. SLA-Clock Agent starts the relevant IRDAI timer (1h auth / 3h discharge / 30d reimb)
   │
2. Risk-Predictor Agent scores P(breach) using doc completeness + hospital/TPA history
   │      ├─ LOW risk  → monitor only
   │      └─ MED/HIGH  → activate Document-Chaser
   │
3. Document-Chaser Agent identifies missing docs vs requirement KB; sends vernacular
   request via WhatsApp/email/voice to hospital desk → TPA → policyholder (in order)
   │      ◄── Critic/Guardrail validates each message (PII, no medical advice, tone)
   │
4. Inbound docs auto-ingested (OCR/IDP) → checklist updated → clock re-evaluated
   │
5. If clock crosses AMBER (e.g., 40% time left) and risk still HIGH:
        Router/Escalation Agent re-assigns to a senior queue / on-call manager
   │
6. ══ HUMAN-IN-THE-LOOP CHECKPOINT ══
   Claims Manager reviews complete packet → APPROVES authorization / DENIAL / final pay
   (Agents NEVER make the medical/financial adjudication.)
   │
7. Decision pushed back to PAS/TPA/hospital; policyholder notified in vernacular
   │
8. Audit Agent writes immutable record of the full trace → IRDAI-ready evidence
   │
OUTPUT: Claim authorized/settled within SLA + complete audit trail + breach analytics
```

**Human-in-the-loop checkpoints (explicit):**
- **HITL-1 (mandatory):** Final authorization / denial / payment decision — always human.
- **HITL-2 (configurable):** Approving escalation to external parties or regulator-facing communications.
- **HITL-3 (configurable, early rollout):** Manager sign-off on autonomous chase messages until trust is established ("supervised autonomy" → "full autonomy" graduation).

---

## 4. Data Sources & Integrations

### 4.1 Systems to connect

| System | Role | Where data is siloed today |
|---|---|---|
| **PAS (Policy Admin System)** | Policy, member, coverage, exclusions | Core insurer DB (often legacy: mainframe, Oracle, in-house) |
| **Claims Management System** | Claim status, history, adjudication notes | Separate from PAS; TPA-side copies diverge |
| **TPA portals/feeds** (Medi Assist, Vidal, Paramount, MD India, Health India) | Claim intake, hospital coordination | Each TPA = separate portal/API; weak insurer sync |
| **NHCX (National Health Claims Exchange)** | Standardized claim exchange rails (ABDM) | Emerging; adoption uneven — strategic integration |
| **HIS / Hospital insurance-desk systems** | Discharge request, bills, clinical docs | Fragmented across thousands of hospitals |
| **WhatsApp Business API** | Vernacular chasing channel | New channel to instrument |
| **Document repository / DMS** | Claim documents, KYC, bills | Scattered; needs IDP/OCR layer |
| **Ticketing (Freshdesk/Zendesk/ServiceNow)** | Escalation + grievance tracking | Often separate from claims flow |
| **Ombudsman / grievance case log** | Adverse awards, penalty tracking | Manual spreadsheets / siloed CRM |

### 4.2 Data contracts

- **Inbound:** event-driven claim updates (webhook/Kafka where possible; nightly batch + polling fallback for legacy PAS). Canonical claim schema mapped via an integration adapter layer.
- **Outbound:** decisions written back to PAS/TPA via API or RPA where no API exists (many TPA portals lack open APIs → RPA bridge as a stopgap).
- **NHCX-first strategy:** as NHCX adoption grows, treat it as the standardized backbone, reducing per-TPA bespoke integration.
- **PII/PHI:** all health data classified; field-level encryption; DPDP-Act-aligned consent and data-residency (India).

---

## 5. Automation Opportunities vs. What Stays Human

| Stays autonomous (agents) | Stays human (HITL) |
|---|---|
| Clock tracking against IRDAI timers | Medical necessity / coverage adjudication |
| Breach-risk prediction & prioritization | Final authorization / denial decision |
| Missing-document identification | Final reimbursement payment approval |
| Vernacular document chasing (WA/email/voice) | Regulator-facing official communications (review) |
| Inbound doc ingestion (OCR/IDP) + checklist | Disputed/fraud-flagged claim handling |
| Stuck-claim re-routing & escalation | Exception/edge-case judgment |
| Immutable audit logging + reg reporting | Policy-interpretation gray areas |

**Automation potential: High.** ~70-80% of the *coordination* workload (chasing, routing, logging) is automatable; the ~20-30% of *judgment* work stays human — which is exactly what keeps the product defensible and compliant.

---

## 6. Tech Stack (2026)

| Layer | Choice | Rationale |
|---|---|---|
| **Orchestration** | LangGraph (stateful graph) + a thin Agent-SDK layer | Per-claim state machines, deterministic checkpoints, replayable traces — ideal for regulated workflows |
| **Reasoning models** | Tiered: small/fast model (Llama-3.x / Mistral / Claude Haiku-class) for routing & chasing; frontier model (Claude/GPT-class) for ambiguous reasoning | Cost control; most steps are cheap, few need frontier reasoning |
| **Vernacular NLG/NLU** | Indic-tuned LLM (e.g., Sarvam / Krutrim / IndicTrans-class) for Hindi + regional languages | Document chasing must work in policyholder's language |
| **Risk model** | Gradient-boosted trees (XGBoost/LightGBM) + LLM feature extraction over notes | Tabular + unstructured hybrid; explainable |
| **Document IDP** | OCR + layout model (Docling / LayoutLM-class) + structured extraction | Inbound bills, discharge summaries, KYC |
| **RAG / retrieval** | Hybrid (BM25 + dense) over doc-requirement KB, IRDAI circulars, policy wordings | Grounds chasing & compliance reasoning in actual rules |
| **Eval & guardrails** | Promptfoo/Braintrust-style eval suite; PII scrubber; prompt-injection filter; output policy classifier | Regulated domain — every outbound message must pass guardrails |
| **Audit ledger** | Append-only, hash-chained store (Postgres + WORM or QLDB-equivalent) | Tamper-evident IRDAI proof |
| **Messaging** | WhatsApp Business API (BSP), SMTP, voice/IVR (TTS) | Multi-channel chasing |
| **Integration** | Kafka/webhooks + REST adapters + RPA bridge for portal-only TPAs | Legacy reality |
| **Deployment** | **VPC / on-prem first**, cloud-managed optional | Indian insurers + health data → strong data-residency + on-prem demand; offer self-hosted models for PHI-sensitive carriers |

**Deployment note:** Lead with a **VPC/on-prem reference architecture** (open-weight Indic + reasoning models self-hosted) because large insurers/TPAs will resist sending PHI to third-party cloud APIs. Offer a managed-cloud tier for smaller TPAs to accelerate land.

---

## 7. Expected ROI + Payback

| Metric | Target | Window |
|---|---|---|
| Cashless-auth SLA breach rate | ↓ 40-70% | 3-6 months |
| >3-hr discharge overruns (shareholder-fund cost) | ↓ 50%+ | 3-6 months |
| Ombudsman adverse awards / penalty days | ↓ 30-50% | 6-12 months |
| Manual chasing labor | ↓ 40-60% | 3-9 months |
| NPS / persistency on health line | measurable uplift | 6-12 months |

**Payback:** A ₹1-3 Cr/yr platform contract against ₹15-40 Cr/yr [estimate] exposure for a large carrier implies **payback in 3-6 months** and a **>5-10x first-year ROI** even on conservative breach-reduction assumptions. ROI is unusually *legible* here because penalties and overruns are line-itemized — the buyer can attribute savings directly.

---

## 8. Implementation Complexity, Risks & Mitigations

**Overall complexity: Medium.** The AI is tractable (coordination, not adjudication). The hard part is **integration across PAS + N TPAs + thousands of hospitals**, not the agents.

| Risk | Severity | Mitigation |
|---|---|---|
| TPA/PAS lack open APIs (portal-only) | High | RPA bridge + NHCX-first roadmap; partner with a TPA as design partner |
| PHI/DPDP data-residency & consent | High | On-prem/VPC deploy, field-level encryption, consent management, India residency |
| Over-chasing / policyholder annoyance | Med | Critic agent rate-limits; channel/quiet-hour rules; escalation ladder |
| Wrong autonomous action in regulated flow | High | HITL on all decisions; supervised-autonomy graduation; full audit trace |
| Indic NLG quality across dialects | Med | Indic-tuned models + human-reviewed templates for first N months |
| Hallucinated doc requirements | Med | RAG-grounded in policy wordings + IRDAI circulars; deterministic checklist rules |
| Adoption inertia at insurers/TPAs | Med | Lead with penalty-savings ROI; pilot on one product line; outcome-based pricing option |
| Liability if breach still occurs | Med | Position as "compliance copilot + evidence trail," not a guarantee; SLA-uplift metrics, not absolute promises |

---

## 9. TAM / SAM / SOM — India (show the math)

**Anchors:**
- India processes **>1 crore (10M+) health claims/year via TPAs alone**; total cashless+reimbursement volume across health + general is far higher.
- Health insurance line growing ~25-27% YoY; ~30+ insurers + ~12 major TPAs + thousands of hospitals.

**TAM (claims-ops compliance tooling, health + general):**
- ~40-50 insurers + ~12 major TPAs as potential buyers.
- Plausible per-large-buyer spend ₹1-3 Cr/yr; mid/small ₹20-60 L/yr.
- **TAM ≈ ₹800-1,200 Cr/yr [estimate]** (compliance + claims-ops orchestration tooling across health + general).

**SAM (serviceable — carriers/TPAs with material cashless volume + budget for autonomy):**
- The ~15-20 large health insurers + top ~6-8 TPAs that carry the bulk of cashless volume and penalty exposure.
- **SAM ≈ ₹300-450 Cr/yr [estimate].**

**SOM (3-year obtainable):**
- Win 8-15 mid/large carriers + 2-4 TPA platforms at ₹1-3 Cr each, plus a smaller-buyer SaaS tail.
- **SOM ≈ ₹40-80 Cr/yr [estimate]** by year 3.

```
TAM  ₹800-1,200 Cr  ████████████████████  (all India claims-ops compliance tooling)
SAM  ₹300-450  Cr   ███████               (large carriers/TPAs with cashless volume + budget)
SOM  ₹40-80    Cr   █                      (8-15 carriers + 2-4 TPAs in 3 yrs)
```

---

## 10. Competitive Landscape

| Player | What they have | Gap (our wedge) |
|---|---|---|
| **TPAs** (Medi Assist, Vidal, Paramount, MD India, Health India) | Workflow queues, claim intake, scale | Workflow ≠ autonomy; no predictive breach prevention; they *are* the breakage point we instrument |
| **BPOs / claims-ops outsourcers** | Manual document chasing, headcount | Human-paced, business-hours, untracked, expensive — exactly what we automate |
| **Core insurance platforms** (in-house PAS, legacy claims systems) | System of record | Report breaches after the fact; no agentic chasing/routing |
| **Health-claims fintechs / cashless networks** | Faster intake, hospital UX | Front-door focus, not back-office SLA-compliance orchestration |
| **Global insurtech AI** (Shift Technology, Sprout.ai, etc.) | Claims AI (fraud, automation) | Not built for **2026 IRDAI timers**, NHCX, vernacular WhatsApp chasing, or India on-prem reality |
| **Generic agentic-AI platforms** | Horizontal orchestration | No insurance/IRDAI domain depth, no compliance evidence trail |

**The wedge:** *No agentic SLA-compliance copilot is purpose-built for the live 2026 IRDAI clocks.* Our defensibility = (1) regulation-specific rule engine + audit trail, (2) the TPA-insurer handoff is precisely where everyone breaks and no one coordinates with agents, (3) vernacular autonomous chasing + India on-prem deployment, (4) NHCX-native posture as the standard rails mature.

---

## 11. Startup Verdict

**Verdict: BUILD — fundable, high-conviction, but design-partner-gated.**

**Probability of success: Medium-High (~60-65% to a real, defensible business [estimate]),** conditional on landing a TPA or large insurer design partner in the first 6 months.

**Why fundable:**
- **Regulation is the demand engine.** Live, dated, penalized mandates (₹5,000/day, shareholder-fund overruns) create non-discretionary, board-level urgency — the rare "must-buy, not nice-to-have."
- **Legible ROI.** Savings are line-itemized (penalties, overruns, interest, labor) → easy enterprise sale.
- **Clear white space.** TPAs have workflow but not autonomy; nobody is agent-coordinating the TPA-insurer handoff.
- **Composite 8.05**, with urgency 10 and pain 9 — the strongest possible buyer-pull combination.

**Key risks to the thesis:** integration drag across legacy PAS + portal-only TPAs; a large TPA building this in-house; data-residency/PHI friction. All are executional, not existential.

**GTM motion:**
1. **Land** with 1-2 design partners (one TPA + one large health insurer) on a single product line, supervised-autonomy mode, outcome-tied pricing.
2. **Prove** breach-rate and penalty reduction in one quarter; publish the audit-trail evidence story.
3. **Expand** to full autonomy + more product lines; **NHCX-native** as standard rails mature; cross-sell general insurance.
4. Pricing: hybrid **platform subscription (₹/year per carrier) + per-claim usage**, with an **outcome/penalty-savings share** option to de-risk the buyer.

**Ideal ICP:**
- **Primary:** Large standalone health insurers + top-tier TPAs (>2M cashless claims/yr) with visible grievance/penalty exposure (e.g., the high-complaint-ratio carriers).
- **Secondary:** General insurers' health lines; mid TPAs via managed-cloud tier.
- **Champion:** Chief Claims Officer / Head of Health Claims / Compliance head — owns the penalty P&L line.

**Moat:**
- IRDAI-specific compliance rule engine + tamper-evident audit trail (regulatory trust compounds).
- Proprietary breach-prediction model trained on cross-carrier/TPA claim behavior (data network effect).
- Deep TPA + NHCX integrations (switching cost).
- Vernacular chasing + India on-prem reference architecture (hard for global insurtech to replicate quickly).

---

## Sources

- [IRDAI Master Circular on Health Insurance Business, 29 May 2024 (PDF)](https://irdai.gov.in/documents/37343/365525/)
- [IRDAI mandates 3-hour cashless claim approval — Life Insurance International](https://www.lifeinsuranceinternational.com/news/irdai-cashless-claim-approval/)
- [IRDAI mandates cashless claim within an hour — Policybazaar](https://www.policybazaar.com/health-insurance/general-info/news/no-more-waiting-irdai-mandates-cashless-claim-within-hour/)
- [Health insurance = ~75-80% of complaints — Insurance Business Mag](https://www.insurancebusinessmag.com/asia/news/life-insurance/latest-india-data-finds-complaints-clustered-in-insurance-segment-565197.aspx)
- [Medi Assist — scale and grievance/SLA data](https://mediassisttpa.in/)
- [India Insurance TPA Market — NextMSC](https://www.nextmsc.com/report/india-insurance-tpa-market)
- [Health insurance complaints surging — Insurance Samadhan](https://www.insurancesamadhan.com/blog/health-insurance-complaints-in-india-are-surging-what-policyholders-need-to-know-and-how-to-protect-yourself/)

*Figures tagged [estimate] are analytical estimates for blueprint purposes, not audited market figures.*
