# Pre-Authorization & TPA Coordination Agent — Build-Ready Blueprint

**Agent type:** Pre-Auth Orchestration Agent (multi-agent)
**Industry:** Healthcare & Hospitals — India
**Composite opportunity score:** 8.35 / 10
**Document status:** Investor-ready founder blueprint
**Last updated:** 2026-06-23

---

## 0. TL;DR (Governing Thought)

> **Build it.** Pre-authorization is the single most painful, most quantifiable bottleneck in the Indian hospital revenue cycle, and IRDAI has just made it a *regulatory* problem (1-hour pre-auth / 3-hour discharge mandates), not just an operational one. A hospital-side agentic packet-assembly + multi-payer coordination layer is fundable, defensible, and deployable in 8–12 weeks. The durable moat is **not** portal scraping (NHCX will erode that) — it is the **clinical-documentation-to-payer-packet intelligence + cross-payer SLA orchestration + denial-prevention loop** that sits on the hospital side of the wire regardless of transport.

Three supporting arguments:

1. **The pain is regulatory now, not just operational.** IRDAI's 2024–25 rules force insurers to clear discharge in 3 hours and *pay the bed-block cost if they breach* — but the bottleneck has shifted to the **hospital's ability to assemble a complete, query-proof packet fast enough**. That is exactly where an agent wins. (Source: PolicyBazaar/IRDAI, 2025)
2. **The market is real and underserved standalone.** ~12 major TPAs + 30+ insurers, ~2.25 crore claims/yr through TPAs (69% of all claims), each with bespoke portals, formats and SLAs. Pre-auth automation is mostly bundled inside HIS/RCM suites and done poorly; standalone autonomous agents are nascent. (Source: IRDAI Annual Report 2024-25)
3. **NHCX is a tailwind, not a threat — if you build on the hospital side.** NHCX standardizes the *transport* (FHIR), which kills the "portal scraping" thesis over 3–5 years but *amplifies* demand for the part that NHCX does NOT solve: turning messy EMR/clinical notes + billing estimate into a complete, payer-specific, denial-proof claim. (Source: NHA/Nathealth NHCX brief, 2025)

---

## 1. Problem & Business Case

### 1.1 The problem, sharpened

Cashless pre-authorization is the gate between a treated patient and a discharged, paid-for patient. Today an insurance-desk executive at a hospital:

- Logs into **a different portal per TPA/insurer** (Medi Assist, Paramount, Vidal, MD India, Health India, plus in-house insurer desks — 12+ TPAs, 30+ insurers).
- Manually re-keys patient + clinical + billing data into each portal's bespoke format.
- Emails/faxes supporting documents (discharge summary, investigation reports, line-of-treatment).
- **Phones and chases** for approval status, and reactively answers payer queries ("send updated estimate", "justify ICU days", "attach OT notes").
- Repeats this across dozens of in-flight cases simultaneously, with zero parallelism.

The result: **the bottleneck is now the hospital desk, not the insurer.** IRDAI data shows 87% of pre-auths clear within 1 hour and 97% of discharges within 3 hours *once a complete request reaches the insurer* — meaning the residual delay and denial risk lives in **packet completeness and query turnaround on the hospital side.**

### 1.2 Why the current approach fails (root cause)

| Failure mode | Root cause |
|---|---|
| Slow initial submission | Manual re-keying across N portals; no parallelism |
| Approval delays | Incomplete/incorrect packets trigger payer queries (round-trips) |
| Denials & deductions | Wrong codes, missing justification, format mismatch per payer |
| Bed-block at discharge | Final authorization stuck on a query the desk answers reactively |
| No visibility | Discharge desk has no real-time status; patient waits, bed stays occupied |

This is a **pure human-throughput + documentation-quality bottleneck.** Humans cannot parallel-process across dozens of portals or *proactively* pre-empt payer queries.

### 1.3 Cost of inaction (quantified)

**Bed-block (primary cost):**
- Forgone contribution per blocked bed-day in metro tertiary care: **₹8,000–15,000/bed-day** `[estimate]`.
- A 400-bed metro tertiary hospital with ~30% cashless mix, conservatively 25–40 discharge-delay bed-days/month from pre-auth lag.
- **Annualized bed-block leakage: ₹2.4–7.2 Cr/yr per large hospital** `[estimate]` (25–40 bed-days/mo × ₹8–15k × 12).

**Cash-flow / working-capital cost:**
- Delayed approvals → delayed settlement → larger receivables. On a ₹150–300 Cr cashless throughput, a 5–7 day DSO improvement frees **₹2–6 Cr of working capital** `[estimate]`.

**Denial / deduction leakage:**
- Industry deduction rates of 5–12% on cashless claims `[estimate]`; even a 1–2pp reduction via better packets is **₹1.5–6 Cr/yr recovered** `[estimate]` at scale.

**Soft costs:** patient churn from discharge-day friction, NPS damage, insurance-desk overtime/attrition.

> **Combined cost of inaction for a single large metro hospital: ₹5–15 Cr/yr** `[estimate]`. The sourced anchor: 20–30% TAT improvement is achievable (Medicon), and IRDAI now penalizes insurers for >3hr discharge breaches — making *hospital-side completeness* the binding constraint.

---

## 2. Agent Architecture

### 2.1 Design philosophy

A **planner-router → specialist workers → critic** topology with a shared case memory and a hard human-in-the-loop gate before any external submission. Each "agent" is a bounded specialist with its own tools and prompt; the orchestrator owns state, retries, and SLA timers.

### 2.2 Agents

| # | Agent | Role | Tools | Memory |
|---|---|---|---|---|
| 0 | **Orchestrator / Planner** | Owns case state machine, routes work, enforces per-payer SLA timers, escalates | State store, SLA timer service, payer-rule registry | Case memory (long-term) |
| 1 | **Document-Assembly Agent** | Pulls EMR + billing estimate, extracts diagnosis/procedure/line-of-treatment, builds payer-specific packet, maps to payer codes | HIS/EMR connector, billing connector, OCR/IDP, ICD-10/PCS + procedure-code mapper, payer-template engine, RAG over payer rulebooks | Case + payer-rule KB |
| 2 | **Completeness Critic** | Validates packet against payer-specific checklist *before* human review; predicts likely query/denial | RAG over historical queries/denials, rule validator, denial-prediction model | Denial/query history |
| 3 | **Submission Agent** | Submits via **NHCX/FHIR API where available**, falls back to browser automation per portal | NHCX FHIR client, browser-automation runtime (scout-then-fill), portal schema registry | Portal schema KB |
| 4 | **Follow-up Agent** | Polls status, detects pending/query states, **drafts proactive responses to payer queries**, re-submits deltas | Status pollers, NHCX status API, browser pollers, RAG over query-resolution playbook | Case + playbook KB |
| 5 | **Status-Sync Agent** | Pushes real-time status to discharge desk / HIS / dashboards / WhatsApp to desk | HIS write-back, dashboard API, notification service | Case memory |
| 6 | **Guardrail/Compliance layer** (cross-cutting) | PII redaction, consent (ABDM) checks, audit trail, no-PHI-to-LLM enforcement, action allow-list | DLP/redaction, consent ledger, audit logger | Immutable audit log |

### 2.3 Orchestration pattern

- **Router/Planner** = LangGraph state machine. Nodes = agents; edges = case-state transitions (`INTAKE → ASSEMBLE → CRITIC → HUMAN_REVIEW → SUBMIT → FOLLOWUP → SYNC → CLOSED`).
- **Workers** = Agents 1–5 run as graph nodes; Follow-up runs as a recurring background loop with SLA timers.
- **Critic** = Agent 2 gates the flow; if it predicts a query/denial, it loops back to Assembly with specific fixes *before* a human ever sees it.
- **Memory** = (a) **Case memory** (per-claim working state, JSON), (b) **Payer-rule KB** (vector + structured rules per TPA/insurer), (c) **Denial/query history** (the compounding moat — every resolved query trains the Critic).

### 2.4 Reasoning trace (per case, auditable)

```
[INTAKE]    Trigger: discharge initiated / pre-auth requested for Case #C-8842
[ASSEMBLE]  Patient: M/54, Dx: Acute MI (I21.9), Proc: PTCA + 1 stent (PCS 02703)
            Payer: Star Health via Medi Assist TPA → template MA-CARDIAC-v4 selected
            Pulled: discharge summary, angio report, billing estimate ₹2.85L
[CRITIC]    Checklist 14/15 passed. MISSING: ICU justification note (payer historically
            queries cardiac ICU >2 days). Confidence packet clears w/o query: 0.62 → LOOP BACK
[ASSEMBLE]  Auto-drafted ICU justification from clinical notes; re-scored 0.91
[HUMAN]     ⛔ GATE → Insurance exec reviews packet → approves (2 min)
[SUBMIT]    NHCX FHIR Claim bundle posted (Medi Assist live on NHCX) → ack CLM-77231
[FOLLOWUP]  T+38min: payer query "confirm stent invoice". Drafted response + attached
            invoice → resubmitted (no human needed, allow-listed delta)
[SYNC]      T+52min: APPROVED ₹2.71L. Pushed to discharge desk + HIS. Bed freed.
[CLOSE]     TAT 52min vs 4.5hr baseline. Logged to denial/query KB.
```

### 2.5 Text architecture diagram

```
                         ┌────────────────────────────────────────┐
   Trigger               │        ORCHESTRATOR / PLANNER           │
 (HIS pre-auth /  ─────► │   LangGraph state machine + SLA timers  │
  discharge event)       │   + Payer-rule registry + retries       │
                         └───┬───────────┬───────────┬───────────┬─┘
                             │           │           │           │
                   ┌─────────▼──┐  ┌─────▼─────┐ ┌───▼────┐ ┌────▼─────┐
                   │ 1. DOC      │  │ 2.CRITIC  │ │ 3.SUB- │ │ 4.FOLLOW │
                   │ ASSEMBLY    │◄─┤completeness│ │ MISSION│ │   -UP    │
                   │ EMR+bill→   │  │+denial    │ │NHCX/   │ │chase+    │
                   │ payer packet│  │ predict   │ │browser │ │query ans │
                   └──┬──────────┘  └───────────┘ └───┬────┘ └────┬─────┘
                      │                                │           │
        ┌─────────────▼────────────┐                  │           │
        │   ⛔ HUMAN-IN-LOOP GATE   │                  │           │
        │ Insurance exec reviews    │                  │           │
        │ packet BEFORE submit      │                  │           │
        └─────────────┬─────────────┘                 │           │
                      │ approve                        │           │
                      └────────────────────────────────┘           │
                                                                    │
                         ┌──────────────────────────────────┐      │
                         │      5. STATUS-SYNC AGENT          │◄─────┘
                         │  real-time → discharge desk/HIS    │
                         └──────────────────────────────────┘
   ──────────────────────────────────────────────────────────────────────
   CROSS-CUTTING:  6. GUARDRAIL/COMPLIANCE (PII redaction · ABDM consent ·
                      audit log · no-PHI-to-LLM · action allow-list)
   MEMORY:  Case memory · Payer-rule KB (RAG) · Denial/Query history (moat)
   DATA IN: HIS/EMR · Billing/Estimate · TPA portal schemas · ABDM/NHCX
```

---

## 3. Multi-Agent Workflow (Trigger → Output)

1. **Trigger** — HIS emits a pre-auth-needed or discharge-initiated event (webhook/poll). Orchestrator opens a case.
2. **Intake & resolve payer** — Identify insurer + TPA, select the payer-specific template + rule set from the Payer-rule registry.
3. **Document Assembly (Agent 1)** — Pull EMR (diagnosis, procedure, line of treatment, clinical notes), billing estimate, prior reports. Run IDP/OCR on scanned docs. Map to ICD-10 / procedure codes. Build the payer-specific packet.
4. **Completeness Critic (Agent 2)** — Validate against payer checklist + historical query patterns. Predict query/denial probability. If risk high → **loop back to Assembly** with specific fixes (auto-draft justifications, flag missing docs). Iterate until confidence threshold met.
5. **⛔ HUMAN-IN-THE-LOOP GATE #1 (mandatory)** — Insurance executive reviews the assembled packet + Critic's notes; edits/approves. **No external submission without this approval.**
6. **Submission (Agent 3)** — Prefer **NHCX/FHIR API** if payer is live on NHCX; else browser-automate the specific TPA portal (scout-then-fill, schema-registry-driven). Capture acknowledgement ID.
7. **Follow-up (Agent 4)** — Background loop polls status against per-payer SLA timer. On a payer query: draft a response from clinical/billing data + query-resolution playbook.
   - **⛔ HUMAN-IN-THE-LOOP GATE #2 (configurable)** — Low-risk, allow-listed query responses (attach invoice, resend report) can auto-send; **clinical/financial-judgment responses require exec approval.**
8. **Status-Sync (Agent 5)** — Push real-time status (pending/query/approved/amount/denial) to discharge desk, HIS, dashboard, and a WhatsApp/Telegram channel for the desk.
9. **Close & learn** — On approval/denial, write outcome + every query to the Denial/Query history KB → the Critic gets smarter (compounding moat).
10. **Output** — Faster, query-proof approvals; real-time discharge-desk visibility; a denial-prevention dataset that improves weekly.

---

## 4. Data Sources & Integrations

### 4.1 Systems to connect

| System | Role | Data pulled/pushed | Integration path |
|---|---|---|---|
| **HIS / EMR** (e.g., Medical Mantra, Birlamedisoft, Insta by Practo, MocDoc, Napier, Akhil/Medixcel; some on Epic/Cerner in large chains) | Source of clinical + admin data | Patient demographics, diagnosis, procedure, line of treatment, clinical notes, discharge summary | HL7 v2 / FHIR API where present; DB read connector or HL7 listener for legacy |
| **Billing / estimate module** | Cost packet | Itemized estimate, package rates, room category, implant invoices | API or DB connector (often same HIS vendor) |
| **TPA / insurer portals** (Medi Assist, Paramount, Vidal, MD India, Health India + insurer desks) | Submission + status | Pre-auth form, doc upload, query inbox, approval status | **NHCX FHIR API (preferred)**; browser automation fallback per portal |
| **ABDM / NHCX** | Standardized transport + consent | Claim bundle (FHIR), coverage eligibility, status, ABHA-linked records | NHCX FHIR client + ABDM consent manager |
| **LIS / RIS / PACS** (optional) | Investigation reports | Lab/radiology reports for justification | HL7/FHIR or report-export connector |
| **Notification layer** | Desk visibility | Status push | WhatsApp Business API / Telegram / dashboard |

### 4.2 Data contracts (canonical internal model)

Normalize everything into one internal **Claim Case object**:
`{ case_id, patient(ABHA?, demographics), payer{insurer, tpa, policy}, clinical{dx[], proc[], notes, los}, billing{estimate, line_items, implants}, documents[], packet{template_id, fields, attachments}, status_history[], queries[], outcome }`.

Map this once to each payer's schema. NHCX-live payers get the FHIR `Claim`/`CommunicationRequest` bundle; legacy portals get the field-map.

### 4.3 Where data is siloed today

- Clinical data sits in **HIS/EMR** but is unstructured (free-text notes, scanned reports).
- Billing sits in a **separate module**, often reconciled manually with clinical.
- Payer requirements live in **tribal knowledge of desk staff** + scattered portal UIs — *no machine-readable rulebook exists.* Capturing this into the Payer-rule KB is the core data-collection act and a moat.

---

## 5. Automation vs Human

| Step | Automation | Human |
|---|---|---|
| Pull EMR + billing | ✅ Full | — |
| Code mapping (ICD/procedure) | ✅ With confidence; low-confidence flagged | Confirm flagged codes |
| Packet assembly | ✅ Full | — |
| Completeness/denial check | ✅ Full | — |
| **Packet sign-off before submit** | — | ✅ **Mandatory gate** |
| Portal submission (NHCX/browser) | ✅ Full | — |
| Status polling | ✅ Full | — |
| Routine query response (attach doc) | ✅ Auto (allow-listed) | — |
| Clinical/financial-judgment query | Draft only | ✅ Approve |
| Final discharge decision | — | ✅ Human |
| Edge cases / appeals / denials | Draft + assemble evidence | ✅ Decide & escalate |

**Principle:** automate keystrokes, retrieval, validation, and chasing; keep clinical and financial *judgment* + the pre-submission sign-off human. This is also the regulatory-defensible posture.

---

## 6. Tech Stack (2026)

| Layer | Choice | Why |
|---|---|---|
| **Orchestration** | **LangGraph** (state-machine multi-agent) | Explicit state, deterministic retries, SLA timers, HITL interrupts, auditability — better than free-form agent loops for a compliance-heavy flow |
| **LLM (reasoning)** | Claude (Sonnet-class) or GPT-class for assembly/critic; **on-prem/VPC option via Llama-3.x / Qwen-class served on vLLM** for hospitals refusing cloud PHI | Tiered: cloud for non-PHI reasoning, local for PHI-bearing steps |
| **Document intelligence** | Layout-aware IDP (Docling / Azure Doc Intelligence / on-prem Surya+OCR) | Discharge summaries, scanned reports |
| **RAG / retrieval** | Hybrid (BM25 + dense) over payer rulebooks + denial history; reranker | Payer-rule retrieval + query-resolution playbook |
| **Browser automation** | Playwright + CDP, scout-then-fill (ARIA-tree based) | Survives portal DOM changes; fallback where no NHCX |
| **NHCX/FHIR** | NRCES FHIR R4 profiles + NHCX client | Standardized transport (future-proof) |
| **Eval / guardrails** | Promptfoo/Inspect eval suite; PII/DLP redaction; action allow-list; structured-output validation (Pydantic) | No-PHI-to-cloud-LLM enforcement; injection defense on portal content |
| **Observability** | OTel traces per agent + immutable audit log | Every action traceable for IRDAI/insurer audits |
| **Deployment** | **VPC/on-prem default for large hospitals; managed-cloud for small/mid** | Indian tertiary hospitals + chains demand data residency / on-prem. Offer both. |
| **Data store** | Postgres (case state) + vector DB (Qdrant/pgvector) + object store (docs) | Standard, on-prem-friendly |

**Deployment stance:** Hybrid by design. PHI-bearing steps can run on-prem/VPC with local models; orchestration + non-PHI reasoning can be cloud. This dual-mode is itself a sales unlock in India.

---

## 7. Expected ROI & Payback

**Per large metro hospital (illustrative, `[estimate]`):**

- Bed-block recovery: ₹2.4–7.2 Cr/yr
- Working-capital / DSO improvement: ₹2–6 Cr one-time + ongoing
- Denial-leakage reduction (1–2pp): ₹1.5–6 Cr/yr
- Desk labor reallocation (2–4 FTE): ₹0.15–0.4 Cr/yr

**Combined annual value: ₹6–19 Cr `[estimate]`.**

**Pricing:** SaaS ₹3–8 L/mo per large hospital (or per-claim ₹15–40) → ₹0.4–1.0 Cr/yr.

**Payback: 3–5 months** (consistent with the opportunity's stated ROI). Even on the conservative floor (₹6 Cr value vs ₹1 Cr price), value:price is ~6:1 — a clean enterprise-software ROI story.

---

## 8. Implementation Complexity, Risks & Mitigations

**Complexity: Medium.** The agent logic is tractable; the integration surface (HIS heterogeneity + payer portals) is the real work.

| Risk | Severity | Mitigation |
|---|---|---|
| **HIS fragmentation** (dozens of vendors, legacy DBs) | High | Build 3–5 connectors for the top HIS vendors first; generic HL7/DB connector; partner with 1–2 HIS vendors for OEM distribution |
| **Portal automation brittleness** | Medium | Prefer NHCX FHIR; scout-then-fill browser automation; schema registry + self-heal alerts |
| **NHCX commoditizes submission** (3–5yr) | Medium | Don't bet on scraping — bet on packet intelligence + denial prevention + cross-payer orchestration (NHCX doesn't solve these) |
| **PHI/data-privacy (DPDP Act, ABDM consent)** | High | On-prem/VPC mode, PII redaction before any cloud LLM, ABDM consent ledger, immutable audit log, DPO-friendly DPA |
| **Wrong code/packet → wrong claim** | High | Mandatory human sign-off gate; Critic confidence thresholds; never auto-submit clinical-judgment content |
| **Payer/TPA resistance to automation** | Medium | Position as completeness-improver (fewer queries helps payers too); align with IRDAI 3-hr mandate |
| **Long enterprise sales cycle** | Medium | Land with single high-pain dept (cashless desk), expand; per-claim pricing lowers buying friction |
| **Liability for denials** | High | Contractually a decision-support + automation tool; human-in-loop documented; no clinical advice |

---

## 9. TAM / SAM / SOM (India) — with math

**Anchors:** ~2.25 Cr claims/yr via TPAs (69% of all claims, IRDAI 2024-25); ~12 major TPAs + 30+ insurers; pre-auth automation is a subset of RCM.

- **TAM** = full India hospital pre-auth/cashless-coordination software opportunity.
  - ~2.25 Cr TPA claims/yr + ~1 Cr in-house ≈ ~3.2 Cr cashless claims/yr.
  - Capturable software value ₹50–80/claim (blended) → **₹1,500–2,500 Cr/yr TAM** `[estimate]`. (Matches the opportunity's stated TAM.)

- **SAM** = hospitals digitized enough to integrate (mid-large + chains with HIS/ABDM readiness), realistically ~40–50% of cashless volume in next 3–4 yrs.
  - ~40% of TAM → **~₹800 Cr SAM** `[estimate]`.

- **SOM (3-yr)** = beachhead of 150–300 mid/large hospitals + 2–3 chains at ₹0.4–1.0 Cr/yr each.
  - 200 hospitals × ₹0.6 Cr avg = ₹120 Cr → **₹100–150 Cr SOM (3-yr)** `[estimate]`.

> Math is intentionally conservative; the binding constraint on SOM is HIS-integration throughput and enterprise sales cycle, not demand.

---

## 10. Competitive Landscape

| Player | Type | Strength | Gap / wedge for us |
|---|---|---|---|
| **HIS/RCM suites** (Birlamedisoft, Insta/Practo, MocDoc, Napier, Medixcel) | Bundled module | Already inside hospital | Pre-auth is a weak bolt-on; no autonomous agent, no denial-prevention, no cross-payer orchestration |
| **TPA-side platforms** (Medi Assist, Vidal, MDIndia tech) | Payer-side | Own the portal | Optimize for payer, not hospital; hospital still does the work |
| **NHCX / ABDM** | Govt rails | Standardizes transport | Solves the wire, NOT packet assembly, denial prevention, or chasing — leaves our core untouched |
| **Indian RCM/automation startups** (e.g., medical-back-office / claims-automation entrants) | Emerging | AI-forward | Mostly billing/coding focus or US-market; standalone autonomous *hospital-side pre-auth agent* is nascent |
| **Global RCM AI** (Akasa, US prior-auth players) | Global | Mature US prior-auth | US-market, US payers — not India TPA/NHCX-native |

**The wedge:** A **hospital-side, NHCX-native, denial-preventing, cross-payer pre-auth agent** with mandatory human sign-off. No incumbent owns (a) clinical-note → payer-packet intelligence + (b) proactive query handling + (c) a compounding denial/query dataset. That triad is the defensible product.

---

## 11. Startup Verdict

**Verdict: BUILD (fundable, with a focused wedge).**

**Probability of success: Moderate-High** for a team that nails HIS integration + a denial-prevention dataset; Moderate if it competes on portal-scraping alone (NHCX risk).

**Why fundable:**
- Quantified, board-level pain (bed-block + cash flow + denials), 3–5 mo payback.
- Regulatory tailwind (IRDAI 1hr/3hr mandates) + infra tailwind (NHCX) create *urgency now*.
- 92% of healthcare investors report rising interest in AI/automation RCM (Black Book 2025); Indian health-tech VCs (HealthQuad, Axilor, Fireside) active.

**GTM motion:**
1. **Land** with the cashless desk of 5–10 high-volume metro tertiary hospitals; per-claim pricing to lower friction; prove TAT + denial-rate deltas in 60–90 days.
2. **Expand** to full RCM-adjacent (eligibility, final-claim, appeals).
3. **Distribute** via OEM partnership with 1–2 HIS vendors + ride NHCX onboarding incentives (₹500/claim DHIS).

**Ideal ICP:** Metro/Tier-1 tertiary hospitals (200+ beds) and small-to-mid hospital chains with ≥25% cashless mix, an existing HIS, and ABDM/NHCX intent. Decision-makers: CFO + RCM/insurance-desk head.

**Moat:**
- **Data moat** — proprietary cross-payer denial/query corpus that no incumbent has; compounds weekly.
- **Integration moat** — top-HIS connectors + payer-rule KB are slow to replicate.
- **Switching cost** — once it sits in the discharge-to-cash loop with audit trails, ripping it out is painful.
- **Regulatory posture** — human-in-loop + on-prem option = enterprise-trustable.

**The one thing to get right:** Do **not** build a portal-scraping company. Build a **packet-intelligence + denial-prevention** company that *also* automates submission. That survives NHCX and is the real franchise.

---

## Sources

- [PolicyBazaar — IRDAI mandates cashless claim within an hour (2025)](https://www.policybazaar.com/health-insurance/general-info/news/no-more-waiting-irdai-mandates-cashless-claim-within-hour/)
- [AngelOne — Cashless claim authorisation time & IRDAI rules 2025](https://www.angelone.in/news/personal-finance/cashless-health-insurance-claim-authorisation-in-2025-how-long-does-it-take-irdai-s-new-rules-and-data)
- [Ditto — Cashless claim timelines in India](https://joinditto.in/articles/health-insurance/cashless-health-insurance-claims-timelines/)
- [IRDAI — List of TPAs](https://irdai.gov.in/list-of-tpas)
- [NYVO — TPA in health insurance India explained](https://nyvo.in/resources/claims/tpa-explained)
- [Nathealth — National Health Claims Exchange brief (2025)](https://nathealthindia.org/wp-content/uploads/2025/06/National-Health-Claims-Exchange_Latest.pdf)
- [ABDM — NHCX](https://hcxbeta.nha.gov.in/)
- [NRCES — FHIR Implementation Guide for ABDM (NHCX profiles)](https://nrces.in/ndhm/fhir/r4/hcx-profile.html)
- [Black Book / PharmiWeb — AI RCM startups surge 2025](https://www.pharmiweb.com/press-release/2025-06-25/ai-rcm-startups-surge-black-book-unveils-2025s-12-fastest-rising-healthcare-revenue-cycle-innovato)
- [Menlo Ventures — 2025 State of AI in Healthcare](https://menlovc.com/perspective/2025-the-state-of-ai-in-healthcare/)
- [StartUs Insights — Healthcare RPA companies](https://www.startus-insights.com/innovators-guide/healthcare-rpa-companies/)

*Figures tagged `[estimate]` are modeled, not measured. TAT improvement (20–30%) and IRDAI/NHCX/TPA figures are sourced above.*
