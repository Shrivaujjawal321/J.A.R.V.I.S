# Patient Engagement, Scheduling & Adherence Agent — India Build-Ready Blueprint

**Opportunity ID:** 18
**Slug:** `patient-engagement-scheduling-adherence-agent`
**Industry:** Healthcare & Hospitals (India)
**Agent class:** Patient Outreach & Adherence Agent (multi-agent, closed-loop)
**Composite score:** 7.85 / 10
**Author:** Principal Enterprise Architect + AI Product Strategist
**Date:** 2026-06-23
**Status:** Investor-grade blueprint — founder-ready

---

## One-line pitch

A closed-loop, multilingual, voice-first agentic system that **predicts who will no-show, autonomously rebooks them, and chases post-discharge adherence until the loop closes** — turning a hospital's biggest silent revenue leak (~18.8% no-shows) into recovered OPD revenue and lower readmissions, under DPDP-Act consent gating.

---

## 1. Problem & Business Case

### 1.1 The pain, sharpened

Indian hospitals lose money in three quiet ways that current tools do **not** fix:

1. **No-shows.** Outpatient no-show rates cluster around **18.8%** (sourced benchmark, Frontiers Digital Health 2025), and Indian-specific reporting puts urban private + government OPD no-shows as high as **23-30%** ([DocTrue](https://www.doctrue.in/blogs/no-show-cancelation-in-india); systematic review average **23%**, [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC11231932/)). Every missed slot is a perishable, non-recoverable inventory loss — the doctor-hour cannot be resold after the fact.
2. **Weak follow-up & medication adherence.** Post-op and chronic patients drift off therapy; non-adherence drives avoidable readmissions, complications, and lost CLV. Reminders today are one-way SMS blasts — no escalation when a red flag appears.
3. **Overloaded call centers.** Human agents spend most cycles on repetitive reminder/reschedule calls in the wrong language, leaving high-value clinical queries under-served and cost-per-contact high.

### 1.2 Why generic reminder tools fail in India specifically

- **Language reality:** A Hindi/English IVR fails a Marathi, Tamil, Telugu, Bengali, or Kannada patient. Generic reminders get ignored → no behavior change.
- **One-way, not risk-stratified:** Blasting every patient the same reminder wastes spend on patients who'd show anyway and under-touches the high-risk ones.
- **No autonomy:** Existing tools remind; they do not *act* (rebook, fill freed slots, escalate). The loop never closes.
- **Channel mismatch:** WhatsApp has ~98% open rates and ~67% of Indian patients prefer it for health comms ([SparkTG](https://sparktg.com/blog/whatsapp-business-api-healthcare-patient-communication)); SMS/IVR-only stacks leave that engagement on the table.

### 1.3 Quantified cost of inaction

**Reference hospital:** 1,000 OPD visits/day, ₹600 average realized revenue/visit, 300 operating days/yr.

| Driver | Math | Annual loss |
|---|---|---|
| No-show revenue forgone (15% conservative) | 1,000 × 15% × ₹600 × 300 | **₹2.7 Cr** [estimate] |
| No-show revenue forgone (18.8% benchmark) | 1,000 × 18.8% × ₹600 × 300 | **₹3.38 Cr** [estimate] |
| Avoidable readmissions / adherence drift | ~₹0.5–1.0 Cr (program-dependent) | **₹0.5–1.0 Cr** [estimate] |
| Call-center cost (reminder/reschedule labor) | 20 agents × ₹3.5 L fully loaded × ~50% deflectable | **₹0.35 Cr** [estimate] |

**Total addressable bleed per reference hospital ≈ ₹3.5–4.4 Cr/yr [estimate].** Even a 30–40% recovery is a ₹1.0–1.7 Cr/yr swing — vastly above any realistic software fee, which is what makes the ROI math fundable.

> **Cost-of-inaction headline:** for a 1,000-OPD/day hospital at 18.8% no-show and ₹600/visit ≈ **₹3.3 Cr/yr forgone** [estimate]; the 18.8% benchmark itself is sourced (Frontiers).

---

## 2. Agent Architecture

### 2.1 Design philosophy

A **router-orchestrated, planner-driven, worker-executed, critic-gated** multi-agent system. Three domain agents (Outreach, Adherence, Triage) sit under one orchestrator with shared memory and a hard **DPDP consent gate** + **clinical human-in-loop (HITL)** layer. Voice and WhatsApp are channels, not agents.

### 2.2 Agents

| Agent | Role | Key tools | Pattern |
|---|---|---|---|
| **Orchestrator / Router** | Classifies every inbound/outbound event, routes to the right domain agent, holds the plan & state machine | Event classifier, policy engine, consent-check tool | Router + Planner |
| **No-Show Risk Model (service, not LLM)** | Scores each upcoming appointment 0–1 for no-show probability | Gradient-boosted model (XGBoost/LightGBM) on appt history + features | Deterministic worker |
| **Outreach Agent** | Risk-stratified multilingual reminders; confirms / cancels / **auto-rebooks**; backfills freed slots from waitlist | HIS scheduling API, WhatsApp send/template, voice (TTS/STT), slot-search, waitlist tool | Worker |
| **Adherence Agent** | Med-refill nudges, post-op check-in scripts, symptom self-report capture, **red-flag escalation** | Scheduled check-in engine, symptom rubric, refill calendar, escalation tool | Worker |
| **Triage Agent** | Routes inbound symptom/admin queries to the correct department or human; non-diagnostic | Department directory RAG, symptom-to-dept classifier, FAQ RAG | Worker |
| **Critic / Guardrail Agent** | Reviews any outbound clinical-adjacent message before send; blocks hallucinated medical advice, PII leaks, off-policy language | LLM-as-judge + rule filters + regex PII scrubber | Critic |
| **Consent & Compliance Gate** | Hard gate: no contact without valid DPDP consent + channel opt-in; logs purpose, retention, withdrawal | Consent ledger, DPDP policy rules | Deterministic gate |
| **HITL Bridge** | Surfaces clinical escalations & low-confidence cases to nurse/coordinator queue | Nurse console, ticketing, callback scheduler | Human-in-loop |

### 2.3 Memory

- **Short-term (episodic):** per-conversation state (language, channel, last intent) — Redis / in-conversation context.
- **Long-term (patient profile):** preferred language, channel opt-ins, prior no-show pattern, adherence streak, consent state — vector + structured store (Postgres + pgvector).
- **Semantic / knowledge:** hospital department directory, prep instructions, drug-refill schedules, escalation rubrics — RAG index.
- **Audit memory:** immutable log of every decision, message, consent event, and override (DPDP + clinical traceability).

### 2.4 Reasoning trace (example)

```
Trigger: Appointment T-24h, patient P-4471, Dr. Mehta Cardiology OPD
1. Consent Gate → consent=VALID (WhatsApp opt-in, purpose=appt-reminder) ✔
2. Risk Model → no_show_prob = 0.71 (HIGH) → escalate touch intensity
3. Router → Outreach Agent
4. Outreach Agent:
   - patient.lang = Tamil → render Tamil WhatsApp template
   - Critic → message clean, no clinical claims ✔ → SEND
   - T-3h no response → trigger voice call (Tamil TTS) with confirm/reschedule IVR-NLU
   - Patient says "can't come, knee pain" → intent=RESCHEDULE+symptom
   - Slot tool → next Cardiology slot in 2 days → propose → patient confirms → REBOOK in HIS
   - Freed slot → Waitlist tool → offer to P-9920 (waitlisted) → BACKFILL
5. Symptom "knee pain" → Triage Agent → suggests Orthopedics; offers booking (no diagnosis)
6. Outcome logged to audit memory + risk-model feedback loop
```

### 2.5 Text architecture diagram

```
                 ┌────────────────────────────────────────────┐
                 │            EVENTS / TRIGGERS                 │
                 │  HIS appt feed · inbound WA/voice · cron     │
                 └───────────────────┬────────────────────────┘
                                     │
                          ┌──────────▼───────────┐
                          │  CONSENT & DPDP GATE  │  ← blocks if no valid consent
                          └──────────┬───────────┘
                                     │
                          ┌──────────▼───────────┐
                          │ ORCHESTRATOR / ROUTER │  (planner + state machine)
                          └─┬─────────┬─────────┬─┘
            ┌───────────────┘         │         └───────────────┐
   ┌────────▼────────┐      ┌─────────▼────────┐      ┌─────────▼────────┐
   │ OUTREACH AGENT  │      │ ADHERENCE AGENT  │      │  TRIAGE AGENT     │
   │ remind/rebook/  │      │ refill/post-op/  │      │ symptom→dept route│
   │ waitlist backfill│     │ red-flag escalate│      │ FAQ/admin RAG     │
   └────┬───────┬────┘      └────────┬─────────┘      └────────┬─────────┘
        │       │                    │                         │
   ┌────▼───────▼────────────────────▼─────────────────────────▼────┐
   │           NO-SHOW RISK MODEL · TOOLS · RAG KNOWLEDGE            │
   │  HIS sched · WhatsApp BSP · Voice STT/TTS · slot/waitlist · CRM │
   └────────────────────────────┬───────────────────────────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │  CRITIC / GUARDRAIL AGENT │ ← every clinical-adjacent msg
                    └────────────┬─────────────┘
                                 │  (escalation / low-confidence)
                    ┌────────────▼────────────┐
                    │   HITL BRIDGE → NURSE    │ ← clinical red flags
                    └──────────────────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │   IMMUTABLE AUDIT LOG    │ (DPDP + clinical trace)
                    └──────────────────────────┘
```

---

## 3. Multi-Agent Workflow (trigger → output)

### Flow A — Pre-appointment (no-show prevention + rebooking)

1. **Trigger:** HIS emits upcoming appointments (T-72h / T-24h / T-3h windows).
2. **Consent Gate (HITL-adjacent):** verify DPDP consent + channel opt-in. No consent → no outbound; queue a one-time consent-collection message only if a lawful basis exists.
3. **Risk scoring:** No-Show Risk Model scores each appt. Stratify: Low (light single WhatsApp), Medium (WhatsApp + reminder), High (WhatsApp → voice escalation).
4. **Outreach Agent** sends language-matched WhatsApp; on no-response, escalates to voice call.
5. **Branch on response:** Confirm → done. Cancel/Reschedule → Outreach Agent auto-proposes slots → **rebooks in HIS**.
6. **Slot recovery:** freed slot → Waitlist tool offers it to next eligible patient → **backfill**.
7. **🟡 HITL checkpoint:** any clinical content in patient's reply (symptoms, distress) → routed to Triage/HITL, never auto-answered with medical advice.
8. **Output:** updated schedule, confirmations, recovered revenue event, model feedback.

### Flow B — Post-discharge / adherence

1. **Trigger:** discharge event or chronic-care cohort enrollment (cron-scheduled check-in plan).
2. **Consent Gate** re-verified for adherence purpose.
3. **Adherence Agent** runs scripted multilingual check-ins (Day 1/3/7/30), med-refill nudges, symptom self-report capture.
4. **Red-flag rubric:** "fever > 3 days," "wound discharge," "chest pain," etc. → **🔴 HARD HITL escalation** to nurse queue with full context. Agent never triages emergencies itself.
5. **Refill loop:** detects refill-due → nudge → (optional) pharmacy/order handoff.
6. **Output:** adherence status, escalations resolved, readmission-risk flags.

### Flow C — Inbound triage

1. **Trigger:** patient initiates on WhatsApp/voice.
2. **Consent + intent classification** → Router.
3. **Triage Agent:** admin/FAQ → answered from RAG; symptom → routed to correct department + booking offer (**no diagnosis**); clinical urgency → 🔴 HITL.
4. **Critic** gates every outbound message.
5. **Output:** resolved query, booking, or warm human handoff.

**HITL checkpoints (explicit):**
- 🟡 Soft: low-confidence intent, ambiguous reschedule, sentiment-negative replies → coordinator.
- 🔴 Hard: any clinical red flag, emergency keyword, consent withdrawal mid-flow, vulnerable patient → nurse, immediately, with the agent standing down.

---

## 4. Data Sources & Integrations

### 4.1 Systems to connect

| System | Examples (India context) | Data used | Integration mode |
|---|---|---|---|
| **HIS / HMIS scheduling** | KareXpert, MocDoc, Insta HMS, Birlamedisoft, Medeil, custom Oracle/Cerner/Epic at large chains | appointments, slots, departments, doctors | REST/HL7/FHIR R4; DB connector fallback |
| **EMR / EHR** | Clinical notes, discharge summaries, problem list | adherence context, post-op plans | FHIR R4 (preferred), read-only |
| **CRM** | Salesforce Health Cloud, LeadSquared, Zoho, in-house | contact, language, consent, history | API |
| **WhatsApp Business Platform** | Meta Cloud API via BSP (Gupshup, Interakt, AiSensy, Infobip) | messaging channel | BSP API + templates |
| **Voice / telephony** | Exotel, Knowlarity, Twilio, Plivo + STT/TTS | inbound/outbound voice | SIP / API |
| **Pharmacy / e-prescription** | In-house or partner | refill status | API (phase 2) |
| **Identity / ABHA** | Ayushman Bharat Health Account (ABDM) | patient identity linkage (optional) | ABDM sandbox APIs |

### 4.2 Data contracts (illustrative)

- **Appointment event:** `{appt_id, patient_id, dept, doctor_id, slot_ts, status, channel_prefs, consent_state}`
- **Consent record:** `{patient_id, purpose, channel, granted_ts, expiry, withdrawal_ts?, source}`
- **Outcome event:** `{appt_id, action[remind|reschedule|backfill|escalate], result, latency, revenue_recovered?}`
- **Escalation:** `{patient_id, trigger, severity, context_blob, assigned_nurse, sla_ts}`

### 4.3 Where data is siloed today

- Scheduling lives in HIS; consent lives nowhere structured (paper/verbal); language preference is rarely captured; call-center logs are unstructured; adherence data doesn't exist post-discharge. **The wedge is partly a data-unification play** — the agent is the first system that writes a clean, consent-tagged, multilingual patient interaction ledger.

---

## 5. Automation vs Human

| Fully automated | Human-in-the-loop / human-only |
|---|---|
| Risk scoring & stratification | Any clinical diagnosis or treatment advice |
| Multilingual reminders (WhatsApp + voice) | Red-flag symptom triage / emergencies |
| Confirm / cancel / **auto-reschedule** | Consent-withdrawal disputes |
| Waitlist **backfill** of freed slots | Vulnerable/elderly patients flagged for human touch |
| Refill nudges & scheduled check-ins | Low-confidence intent (soft escalation) |
| FAQ / admin / department routing | Complaint / grievance handling |
| Audit logging & DPDP record-keeping | Final clinical sign-off on adherence escalations |

Target: **~70–80% of reminder/reschedule/FAQ volume automated**, with clinical judgment always human.

---

## 6. Tech Stack (2026)

- **Orchestration:** **LangGraph** (stateful graph, durable checkpoints, HITL interrupts) as primary; Agent SDK patterns for tool-use. State machine fits the router→worker→critic→HITL topology cleanly.
- **LLMs:**
  - Reasoning/orchestration: a strong frontier model (Claude / GPT-class) for planner + Triage.
  - **Indian-language NLU/generation:** Sarvam-M / Krutrim / fine-tuned open models (Llama/Gemma) for Hindi + 10+ regional languages; fallback to frontier for hard cases. Multilingual quality is the moat — invest here.
  - Cheap/fast model (Haiku/Flash-class) for classification, the Critic, and high-volume routing.
- **Voice:** STT (Sarvam/Whisper-fine-tuned for Indian accents + code-mixing), TTS (Indian-language neural voices). Streaming, barge-in capable.
- **No-show risk model:** XGBoost/LightGBM (interpretable, cheap, retrainable) — not an LLM. Features: lead time, history, day/time, distance proxy, weather, prior no-shows, payment status.
- **RAG/retrieval:** pgvector or Qdrant; hybrid (BM25 + dense); for department directory, prep instructions, FAQs. Small, curated, low-hallucination corpus.
- **Eval & guardrails:** Promptfoo/Ragas for offline evals; **LLM-as-judge Critic** in-line; PII scrubbing; medical-advice refusal classifier; "never diagnose" hard rule; red-team suite for jailbreaks ("just tell me what medicine to take").
- **Channels:** WhatsApp via BSP (Gupshup/Interakt/Infobip); telephony via Exotel/Twilio.
- **Backend:** Python (FastAPI), Postgres + pgvector, Redis, event bus (Kafka/Redis Streams).
- **Deployment:**
  - **Cloud/VPC default** for mid-market (faster, cheaper).
  - **On-prem / VPC-isolated** option for large hospital chains with PHI residency demands — containerized (Docker/K8s), with open-weight Indian-language models running locally so PHI never leaves the perimeter. **This on-prem option is a sales unlock for tier-1 chains.**
- **Compliance tooling:** consent ledger, immutable audit log, 72-hour breach-notification hooks (DPDP Rules 2025), data-retention scheduler.

---

## 7. Expected ROI & Payback

**Per reference hospital (1,000 OPD/day):**

| Lever | Conservative annual value |
|---|---|
| No-show recovery (recover 30% of ₹3.3 Cr bleed) | **₹1.0 Cr** [estimate] |
| Call-center deflection (50% of ₹0.35 Cr) | **₹0.17 Cr** [estimate] |
| Readmission/adherence improvement | **₹0.25–0.5 Cr** [estimate] |
| **Total annual value** | **₹1.4–1.7 Cr** [estimate] |

**Pricing:** SaaS ₹15–40 L/yr per hospital (tiered by bed/OPD volume) + usage (WhatsApp/voice pass-through). Even at the top of range, value:price ≈ **4–8×**.

**Payback: 3–6 months** from recovered no-show revenue alone — the system is self-funding fast and the highest-AI-feasibility item in the set (score 9/10). This is what makes the buyer's yes easy.

---

## 8. Implementation Complexity, Risks & Mitigations

**Overall complexity: MEDIUM.** Hard parts are integrations and multilingual voice quality, not the agent logic.

| Risk | Severity | Mitigation |
|---|---|---|
| HIS integration heterogeneity (every hospital different) | High | Adapter layer + FHIR-first; ship 3–5 prebuilt connectors (KareXpert, MocDoc, Insta) covering majority of mid-market; DB-connector fallback |
| Multilingual voice quality / code-mixing | High | Indian-language fine-tunes (Sarvam/Krutrim); WhatsApp-first (text easier) then voice; human fallback always available |
| **DPDP Act 2023 + Rules 2025 compliance** | High | Hard consent gate, purpose-limitation, 72h breach notice, retention scheduler, consent-manager integration, audit log. Build compliance as core, not bolt-on ([KPMG](https://kpmg.com/in/en/insights/2025/12/the-privacy-prescription-impact-of-dpdp-act-and-rules-in-healthcare-and-life-sciences-sector.html); [EY](https://www.ey.com/en_in/insights/cybersecurity/transforming-data-privacy-digital-personal-data-protection-rules-2025)) |
| Clinical liability (agent gives advice) | Critical | "Never diagnose" hard rule + Critic + red-flag HITL; non-diagnostic positioning; clinical sign-off on all escalations |
| WhatsApp template approval / policy limits | Medium | Pre-approved utility templates; BSP partnership; opt-in hygiene |
| Patient trust / opt-out | Medium | Transparent identity, easy opt-out, value-first messaging |
| Model drift on no-show prediction | Medium | Continuous retraining loop from outcome events; monitor AUC |

---

## 9. TAM / SAM / SOM (India) — with math

**TAM (patient-engagement / CX tech for Indian healthcare):**
India digital health is ~USD 17.8–19.1 B in 2025 ([Custom Market Insights](https://www.custommarketinsights.com/report/india-digital-health-market/); [IMARC](https://www.imarcgroup.com/india-digital-health-market)). Patient-engagement/CX is a sub-slice. Bottom-up: ~50,000+ hospitals + large clinic base; ~3,000–4,000 are realistic software buyers (mid-to-large). At ₹25 L/yr blended ACV → 4,000 × ₹25 L ≈ **₹1,000 Cr**; widen to all engagement-tech spend → **₹2,500–3,500 Cr TAM** [estimate].

**SAM (DPDP-ready, multilingual, agentic-addressable — mid/large hospitals + chains + diagnostic networks willing to buy autonomous engagement):**
~2,000 institutions × ₹25–50 L ACV → **~₹1,000 Cr** [estimate].

**SOM (3-yr realistic capture):**
~3–5% of SAM with focused GTM on 5–6 hospital chains + mid-market → 150–250 hospitals × ~₹50–70 L blended (incl. usage) → **₹120–180 Cr** [estimate].

| Layer | Value | Basis |
|---|---|---|
| TAM | ₹2,500–3,500 Cr | engagement/CX tech slice of India digital health |
| SAM | ~₹1,000 Cr | ~2,000 buyable institutions × ₹25–50 L |
| SOM (3yr) | ₹120–180 Cr | 150–250 hospitals at blended ACV |

All tagged **[estimate]** — directional, bottom-up, defensible.

---

## 10. Competitive Landscape

| Player | What they do | Gap we exploit |
|---|---|---|
| **VoiceOC** | Hospital conversational engagement, WhatsApp/voice | Reminder-grade; limited autonomous risk-stratified rebooking + closed-loop adherence |
| **NiceHMS / HMS vendors** | HMS with reminder modules | Reminders bolted on; no agentic autonomy, no multilingual voice depth |
| **Practo / DocsApp** | Booking marketplace + reminders | Marketplace, not deep hospital-ops agent; one-way reminders |
| **VoiceOC / Gupshup / Interakt / AiSensy** | WhatsApp BSP + bots | Channel/bot layer, not risk-stratified autonomous rebooking + adherence loop |
| **Global (Notable, Hyro, Memora Health, Klara)** | Agentic patient engagement (US) | Not India-localized: no Indian-language voice, no DPDP/ABDM fit, US pricing |

**The wedge:** *Autonomous, risk-stratified rebooking + closed-loop multilingual adherence with voice* — a combination none of the incumbents deliver. Today's tools **remind**; we **act and close the loop**. India-native language + DPDP-native compliance + on-prem option is the defensible local moat against US entrants.

---

## 11. Startup Verdict

**Verdict: BUILD (fundable, high-conviction) — with disciplined clinical-safety and integration execution.**

**Probability of success: Moderately-High.** Reasons:
- **Demand is non-speculative** — no-shows are a quantified, sourced, universal pain with a 3–6 month payback. Buyers don't need education on *why*, only on *trust*.
- **Highest AI feasibility (9/10)** of the opportunity set; the hard tech (multilingual voice, risk model, autonomy) is buildable with 2026 stacks.
- **Localization + compliance = real moat** vs both reminder-grade incumbents and US agentic players.

**Risks to the thesis:** integration drag (long sales + per-HIS engineering), clinical liability, and BSPs/HMS vendors adding "agentic" features. These are executional, not existential.

**GTM motion:**
1. **Land** with the no-show ROI wedge (self-funding, easy yes) at 2–3 lighthouse mid-market hospital chains.
2. **Prove** recovered-revenue dashboard → reference-sell into chains.
3. **Expand** to adherence + triage (higher stickiness, more data moat).
4. Channel: co-sell with HMS vendors + BSPs; direct enterprise for tier-1 chains (on-prem).

**Ideal ICP:** Mid-to-large multi-specialty hospital chains and diagnostic networks, 500–5,000 OPD/day, multi-state (so multilingual is a *requirement* not a nicety), with a digital-health champion in leadership and existing HIS. Secondary: large single-site tertiary hospitals.

**Moat (compounding):**
1. **Data moat** — proprietary consent-tagged, multilingual interaction + outcome ledger improves the risk model nobody else has.
2. **Language moat** — fine-tuned Indian-language voice/NLU is expensive to replicate.
3. **Compliance moat** — DPDP-native + ABDM-ready + on-prem option.
4. **Integration moat** — prebuilt HIS connectors create switching cost.

**Bottom line:** This is a fundable seed-stage company with a clear, sourced pain, fast payback, defensible localization moat, and a credible path to ₹120–180 Cr SOM in 3 years. The risk is execution (integrations + clinical safety), not market.

---

## Sources

- [Frontiers / PMC — online scheduling & no-show rate (18.8% benchmark)](https://www.frontiersin.org/journals/digital-health/articles/10.3389/fdgth.2025.1567397/full)
- [DocTrue — India no-show / cancellation cost](https://www.doctrue.in/blogs/no-show-cancelation-in-india)
- [PMC — systematic review of no-show rates (23% avg)](https://pmc.ncbi.nlm.nih.gov/articles/PMC11231932/)
- [SparkTG — WhatsApp Business API for healthcare (open/preference rates)](https://sparktg.com/blog/whatsapp-business-api-healthcare-patient-communication)
- [Custom Market Insights — India digital health market](https://www.custommarketinsights.com/report/india-digital-health-market/)
- [IMARC — India digital health market size](https://www.imarcgroup.com/india-digital-health-market)
- [KPMG — DPDP Act impact on healthcare & life sciences](https://kpmg.com/in/en/insights/2025/12/the-privacy-prescription-impact-of-dpdp-act-and-rules-in-healthcare-and-life-sciences-sector.html)
- [EY — DPDP Rules 2025](https://www.ey.com/en_in/insights/cybersecurity/transforming-data-privacy-digital-personal-data-protection-rules-2025)

*Figures tagged [estimate] are directional bottom-up models, not audited market data.*
