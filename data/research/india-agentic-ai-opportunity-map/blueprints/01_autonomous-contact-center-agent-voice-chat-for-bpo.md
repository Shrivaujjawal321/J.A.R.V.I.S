# Autonomous Contact-Center Agent (Voice + Chat) for Indian BPO
### A build-ready blueprint for an agentic, multilingual Customer-Experience platform

**Industry:** IT Services & BPO / GCC (India)
**Agent type:** Multilingual Customer-Experience Agent (voice + chat)
**Composite opportunity score:** 9.2 / 10
**Document status:** Investor- and build-ready blueprint
**Last updated:** 2026-06-23

> **One-line pitch:** The per-seat BPO model is being repriced to per-resolution. We give mid-market Indian BPOs an RBI/IRDAI-compliant, regional-language agentic CX stack — outcome-priced — so they keep their contracts instead of losing them to AI-native vendors.

---

## Executive Summary (Pyramid Principle)

**Governing thought:** A focused startup can win the Indian mid-market BPO CX automation segment by combining (a) deep regional-language *voice* (not just chat), (b) *compliant action execution* for regulated workflows, and (c) *per-resolution* pricing — three things the crowded incumbent field has each only partially solved.

1. **The market is repricing in real time.** AI interactions cost ~$0.50 vs ~$6.00 human and absorb 60–90% of typical workloads at 10–30% of cost. BPOs that don't build agentic capacity lose contracts; those that do escape an 30–120% attrition treadmill. Urgency = 10/10.
2. **The pain is existential and quantified.** A 5,000-seat BPO carries ~₹225 Cr/yr cost base; ~50% is automatable ⇒ **~₹110 Cr/yr** either saved or lost to a competitor [estimate].
3. **The incumbents leave a clean wedge.** Sarvam (model layer), Gnani (BFSI voice biometrics), Yellow.ai (chat-first), Uniphore/Observe.ai (analytics/QA), global Retell/Lorikeet (voice infra) — none packages *regional voice + compliant action + outcome pricing for mid-market BPOs that can't build in-house*.
4. **The technology is finally ready.** Hindi/regional voice was the historical blocker; 2026 Indic ASR/TTS (Sarvam, Bhashini, ElevenLabs multilingual, Cartesia) + sub-700ms streaming pipelines now clear the quality bar. AI feasibility = 8/10.
5. **The ROI is fast.** 50–70% cost-to-serve reduction + 100% QA coverage (vs ~2% manual sampling) ⇒ **3–6 month payback**.

**Verdict:** Fundable, but *not* as another horizontal voice-agent platform. Fundable as a **vertical, compliance-first, outcome-priced CX layer for Indian mid-market BPOs and the captives/GCCs that serve BFSI, telecom, and e-commerce**. Probability of building a venture-scale outcome: **Medium-High (≈60–65%)**, gated on regulated-action execution + a proprietary QA/eval flywheel becoming the moat.

---

## I. Situation · Complication · Question

- **Situation:** India holds ~40% of the global BPM market; the IT-BPM sector tracks toward the ~US$350B mark, with BPM exports ~US$43B and domestic BPM ~US$5.7B (Source: NASSCOM / IBEF, 2024–26). The contact-center seat is the atomic unit of this economy.
- **Complication:** The seat is being economically dismantled. AI handles 60–90% of routine interactions at 10–30% of the cost, and buyers (BFSI, telecom, e-com, GCCs) are starting to demand per-resolution, not per-seat, contracts. Simultaneously the labor base is unstable: 30–50% attrition (collections/inside-sales 80–120%), each exit costing $10k–20k, on a fully-loaded $1,200–2,400/agent/month base inflating 9–14%/yr.
- **Question:** *Should we build a venture-scale agentic CX platform for Indian BPOs, and if so, with what architecture, wedge, pricing, and GTM to win against an already-crowded field?*

---

## II. Issue Tree (MECE)

```
Should we build the Autonomous Contact-Center Agent for Indian BPO?
├── 1. Is the problem real & valuable?
│   ├── Cost base at risk (attrition + wage inflation + repricing)
│   └── Buyer willingness to switch to per-resolution
├── 2. Is it technically feasible in 2026?
│   ├── Regional-language voice quality (the historical blocker)
│   ├── Multi-turn reasoning + graceful escalation
│   └── Compliant action execution across backend systems
├── 3. Can we win vs incumbents?
│   ├── Where do Sarvam/Gnani/Yellow/Uniphore/Observe/Retell/Lorikeet stop?
│   └── What is the defensible wedge + moat?
├── 4. What is the unit economics / ROI story?
│   ├── Cost-to-serve reduction
│   ├── Payback window
│   └── Pricing model (per-resolution vs seat vs hybrid)
└── 5. What are the risks & what kills this?
    ├── Regulatory (RBI/IRDAI/DPDP)
    ├── Distribution (BPOs build in-house / incumbents bundle)
    └── Margin compression (model/telephony cost = COGS)
```

---

## 1. Problem & Business Case

### The four compounding cost vectors

| Vector | Magnitude | Source |
|---|---|---|
| Attrition (voice/chat) | 30–50% general; 80–120% collections/inside-sales | Industry norm [estimate] |
| Cost per exit | $10k–20k (rehire + ramp + lost productivity) | Industry norm [estimate] |
| Fully-loaded agent cost | $1,200–2,400/mo | Industry norm [estimate] |
| Wage inflation | 9–14%/yr | Industry norm [estimate] |
| Cost per interaction | ~$0.50 AI vs ~$6.00 human | Opportunity brief [estimate] |

### Quantified cost of inaction

For a **5,000-seat BPO** at **~₹4.5L loaded/seat/yr ≈ ₹225 Cr/yr** cost base, ~50% of volume is automatable ⇒ **~₹110 Cr/yr** is "in play" — saved if captured internally, *transferred to a competitor* if not [estimate].

The asymmetry is the point: this is not a cost-optimization "nice-to-have." It is a **contract-retention** problem. When an AI-native vendor underbids on a per-resolution basis, the legacy per-seat BPO cannot match the price without the same capability — so the revenue, not just the cost, is at risk.

### Why existing approaches fail

Current stack = **IVR + scripted chatbots + RPA**, with humans still doing the bulk. Scripted bots can't:
- handle multi-turn reasoning or context carry-over,
- escalate gracefully with a warm summary,
- act across backend systems (refunds, KYC, tickets), and
- historically, hold Hindi/regional-language voice quality.

The 2026 unlock: Indic ASR/TTS quality + low-latency streaming + tool-using LLMs collapse all four failures simultaneously.

---

## 2. Agent Architecture

A **router-orchestrated, supervisor + specialist-worker pattern** with a persistent shared session memory and a critic loop. The orchestrator is a planner/router; specialist agents are tool-bound workers; a QA/Compliance critic scores every turn and every call.

### Agents

| Agent | Role | Key tools | Memory |
|---|---|---|---|
| **Orchestrator (Router/Planner)** | Detects language + intent, routes to the right worker, manages turn-taking, owns the HITL decision (confidence/emotion thresholds). | Intent classifier, language-ID, confidence scorer, sentiment/emotion model, policy engine | Session state (turn history, slots, customer ID) |
| **Conversation Agent** | The voice/chat persona. Streaming ASR→LLM→TTS; barge-in handling; multilingual incl. Hindi + regional + code-mixed. | Indic ASR, streaming LLM, Indic TTS, barge-in/VAD, code-switch handling | Short-term dialogue buffer |
| **Knowledge Agent** | Answers from KB/policy/product docs via hybrid RAG + reranking. Cites source for auditability. | Hybrid retriever (BM25 + dense), reranker, doc store, citation formatter | Vector + doc cache |
| **Action Agent** | Executes refunds, ticket creation, KYC updates, address/plan changes via backend APIs — *idempotent, with compliance gating*. | CRM API, core-system APIs, payment/refund API, ticketing API, idempotency keys | Action ledger (audit trail) |
| **Escalation / Warm-Handoff Agent** | Transfers to a human with a structured summary (intent, sentiment, steps tried, suggested resolution). | Telephony transfer (SIP/CTI), summary generator, agent-desktop push | Handoff record |
| **QA / Compliance Agent (Critic)** | Scores **100%** of interactions for script adherence + regulatory compliance (RBI/IRDAI/DPDP), flags violations, feeds the eval flywheel. | Rubric scorer, PII/redaction, regulatory rule engine, drift detector | QA datastore (gold labels, scores) |

### Orchestration pattern

- **Router/Planner** at the top (lightweight, fast model) → decides which worker(s) handle the turn.
- **Workers** run concurrently where safe (e.g., Knowledge retrieval while Conversation streams a filler).
- **Critic** (QA/Compliance) runs *inline* for high-risk turns (regulated actions) and *batch* for 100% post-call scoring.
- **Shared memory**: per-session state object + long-term customer memory (last N interactions, preferences, language) + organizational memory (KB embeddings, QA gold set).

### Text diagram

```
                         ┌─────────────────────────────────────────┐
   Inbound call/chat ───►│        ORCHESTRATOR (Router/Planner)      │
   (Telephony / WA API)  │  lang-ID · intent · confidence · emotion  │
                         │  HITL decision · turn-taking · policy     │
                         └───┬─────────┬──────────┬──────────┬───────┘
                             │         │          │          │
              ┌──────────────▼──┐ ┌────▼──────┐ ┌─▼─────────┐ ┌▼──────────────┐
              │ CONVERSATION    │ │ KNOWLEDGE │ │  ACTION   │ │  ESCALATION/   │
              │ ASR→LLM→TTS     │ │ Hybrid RAG│ │ APIs +    │ │  WARM HANDOFF  │
              │ Indic + barge-in│ │ + rerank  │ │ idempotent│ │  → human + sum │
              └──────────────┬──┘ └────┬──────┘ └─┬─────────┘ └┬──────────────┘
                             │         │          │            │
                  ┌──────────▼─────────▼──────────▼────────────▼─────────┐
                  │   SHARED MEMORY: session state · customer LT memory   │
                  │            · KB vectors · action ledger               │
                  └───────────────────────────┬──────────────────────────┘
                                               │ (inline on regulated turns,
                                               │  100% batch post-call)
                                  ┌────────────▼──────────────┐
                                  │  QA / COMPLIANCE (CRITIC)  │
                                  │ rubric · RBI/IRDAI/DPDP    │
                                  │ PII redact · eval flywheel │
                                  └────────────────────────────┘
```

### Reasoning trace (example, collections call in Hindi)

1. Orchestrator: lang=hi-IN, intent=`payment_query`, customer verified, sentiment=neutral, confidence=0.91 → route to Conversation + Knowledge.
2. Knowledge: retrieves outstanding-amount policy + due-date rules (cited).
3. Conversation: states balance, offers options in Hindi.
4. Customer requests a payment-plan change → intent escalates to `restructure_request` (regulated). Orchestrator flags **mandatory HITL** (lending action). 
5. Escalation Agent generates summary, warm-transfers to human collections agent.
6. QA/Compliance: scores the full call (script adherence 96%, no DPDP violation, regulated action correctly handed off) → logged.

---

## 3. Multi-Agent Workflow (with HITL checkpoints)

```
TRIGGER: inbound voice call / WhatsApp / chat  ──or──  outbound campaign dial
   │
   ▼
[1] Orchestrator: identify language + intent + customer (CRM lookup)
   │        ⚑ HITL-CHECK A: low-confidence intent OR unverified identity → human
   ▼
[2] Branch by intent:
   │
   ├─ Informational ───► Knowledge Agent (RAG + citation) ──► Conversation answers
   │
   ├─ Transactional ──► Action Agent
   │        ⚑ HITL-CHECK B: regulated action (lending/insurance per RBI/IRDAI)
   │                       → MANDATORY human confirmation before execute
   │        ⚑ HITL-CHECK C: high $ value / irreversible → confirm
   │        else → execute idempotently → confirm to customer
   │
   └─ Complex / emotional ─► Escalation Agent
            ⚑ HITL-CHECK D: sentiment=anger/distress OR explicit "agent" request
                          → warm handoff with summary
   │
   ▼
[3] Resolution captured (resolved / escalated / follow-up scheduled)
   │
   ▼
[4] QA/Compliance Agent scores 100% of the interaction (async)
   │        → violations queue for supervisor review (HITL-CHECK E)
   ▼
[5] Outputs: CRM update · disposition code · transcript · QA score · audit log
   │
   ▼
[6] Eval flywheel: low-score / flagged calls → gold-label → fine-tune / prompt-tune
```

**HITL checkpoints summarized:**
- **A** — low confidence or unverified identity.
- **B** — *mandatory* human for regulated actions (lending, insurance).
- **C** — high-value/irreversible transactions.
- **D** — high emotion or explicit human request.
- **E** — supervisor review of QA-flagged calls.

---

## 4. Data Sources & Integrations

### Systems to connect

| Layer | Systems (India-relevant) | What flows |
|---|---|---|
| **Telephony / CPaaS** | Ozonetel, Exotel, Twilio, Genesys, Knowlarity, Servetel | Inbound/outbound voice, SIP/CTI transfer, call recording |
| **Messaging** | WhatsApp Business API (Meta/BSP: Gupshup, AiSensy), RCS, web chat | Async + chat sessions |
| **CRM** | Salesforce, Zoho, LeadSquared, Freshdesk/Freshworks, Kapture, MS Dynamics | Customer profile, history, disposition, ticketing |
| **Core systems** | Core banking (Finacle/Flexcube), policy admin (insurance), telecom OSS/BSS, e-com OMS, ERP (SAP/Oracle/Tally for SMB clients) | Balances, refunds, KYC, plan/policy changes |
| **Knowledge** | Confluence/SharePoint/Notion KBs, product & policy PDFs, SOP docs | RAG corpus |
| **Identity / payments** | UIDAI/DigiLocker (KYC), UPI/payment gateways (Razorpay/PayU) | Verification, collections payment links |
| **Compliance / language** | Bhashini (govt Indic stack), DPDP consent manager | Language assets, consent ledger |

### Data contracts (essential discipline)

- **Inbound event schema:** `{channel, lang, customer_id, intent, transcript, sentiment, confidence, consent_flag}`.
- **Action request schema:** `{action_type, params, idempotency_key, compliance_class, hitl_required:bool}`.
- **QA record schema:** `{interaction_id, rubric_scores{}, violations[], pii_redacted:bool, gold_label?}`.
- Every action writes to an **immutable audit ledger** (regulator-ready).

### Where data is siloed today

Transcripts live in the telephony recorder, customer state in the CRM, truth in core systems, knowledge in static PDFs/wikis — none joined in real time. The platform's first job is to be the **real-time join layer** across telephony ⇄ CRM ⇄ core ⇄ KB, with consent and audit threaded through.

---

## 5. Automation vs Human

| Stays automated (agentic) | Stays human (HITL / human-led) |
|---|---|
| FAQ / informational queries | Regulated actions: lending decisions, insurance underwriting (RBI/IRDAI mandate human) |
| Balance / status / order tracking | High-emotion / vulnerable-customer interactions |
| Refunds, cancellations, address/plan changes (idempotent, gated) | Complex disputes, retention/negotiation edge cases |
| KYC data capture (human confirms regulated finalization) | Final sign-off on high-value/irreversible transactions |
| Appointment scheduling, reminders, payment-link sends | Sales close for high-ticket / advisory products |
| 100% QA scoring + compliance flagging | Supervisor review of flagged calls; coaching |
| First-line collections reminders (non-coercive) | Hardship restructuring, legal-sensitive collections |

**Design principle:** Automate the *volume*, route the *risk* and the *empathy* to humans. The target is not 100% deflection — it is 60–90% deflection with **graceful, summarized** handoff so human time is spent only where it compounds value.

---

## 6. Tech Stack (2026)

| Layer | Choice (primary → alternates) | Why |
|---|---|---|
| **Indic ASR** | Sarvam / Bhashini → Whisper-large-v3 fine-tuned, AssemblyAI | Code-mixed Hindi + regional accuracy is the moat input |
| **Indic TTS** | Sarvam TTS / Cartesia / ElevenLabs multilingual | Sub-200ms, natural prosody in 10+ Indian languages |
| **Reasoning LLM** | Claude (Sonnet-tier) / GPT-class for complex; Sarvam-M / Llama-Indic fine-tunes for on-prem/cost | Tool use + multi-turn reasoning; Indic open models for VPC/cost control |
| **Router/classifier** | Small fast model (Haiku-tier / fine-tuned distil) | Cheap, low-latency routing |
| **Orchestration** | LangGraph (stateful graph + HITL interrupts) → Agent SDK, CrewAI | Native interrupt/resume = clean HITL checkpoints |
| **Voice pipeline** | Pipecat / LiveKit Agents (streaming, barge-in, VAD) | Real-time orchestration of ASR↔LLM↔TTS |
| **RAG** | Hybrid (BM25 + dense) + reranker (Cohere/bge), vector DB (Qdrant/pgvector) | Citation-grounded KB answers |
| **Eval / guardrails** | Promptfoo/Braintrust + Ragas for RAG; NeMo Guardrails / custom rule engine; PII redaction | 100% QA flywheel + compliance gating |
| **Telephony** | Ozonetel/Exotel/Twilio + SIP; WhatsApp via BSP | India-native CPaaS coverage |
| **Deployment** | **VPC / on-prem option mandatory** (BFSI data localization, RBI/DPDP); managed cloud for SMB BPOs | Indian enterprises frequently require in-country VPC/on-prem |
| **Observability** | OpenTelemetry traces per turn, per-agent latency budgets, cost-per-resolution dashboard | Latency (<700ms turn) + COGS control are survival metrics |

**Deployment posture:** Offer three tiers — (1) **multi-tenant SaaS** for SMB/mid BPOs, (2) **single-tenant VPC** for regulated clients, (3) **on-prem/air-gapped** with Indic open models for Tier-1 BFSI. Data residency in India is non-negotiable for the BFSI ICP.

---

## 7. Expected ROI

| Metric | Before | After (target) |
|---|---|---|
| Cost per interaction | ~$6.00 (human) | ~$0.50–$1.80 (AI + escalations blended) |
| Cost-to-serve | baseline | **−50% to −70%** |
| QA coverage | ~2% manual sampling | **100% automated** |
| Attrition exposure | 30–120% | materially reduced (fewer rote seats) |
| Payback | — | **3–6 months** |

**Worked example (per 100 deflected seats):** 100 seats × ~₹4.5L/yr ≈ ₹4.5 Cr/yr human cost. At 60–70% automation with AI cost-to-serve ~25–35% of human, net saving ≈ **₹2.0–2.7 Cr/yr per 100 seats**, against a platform cost a fraction of that ⇒ payback well inside 6 months [estimate].

**Pricing model:** Lead with **per-resolution** (₹/successful resolution, voice priced above chat — mirrors Lorikeet's ~$1.00 voice / ~$0.80 chat and Yellow.ai's ~$0.99/resolution benchmarks) plus a **platform/QA-coverage** subscription. Outcome pricing is the wedge: it aligns with the buyer's own repricing pressure and de-risks adoption.

---

## 8. Implementation Complexity & Risks

**Overall complexity: Medium** (Conversation + Knowledge are near-commodity; Action + Compliance are where the hard, defensible engineering lives).

| Risk | Severity | Mitigation |
|---|---|---|
| **Regulatory** (RBI/IRDAI human-in-loop, DPDP consent/localization) | High | Mandatory HITL on regulated actions; consent ledger; in-country VPC/on-prem; legal review per vertical before go-live |
| **Regional voice quality** (accents, code-mixing, noise) | High | Indic-fine-tuned ASR + continuous gold-labeling from QA flywheel; per-language SLAs |
| **Action execution errors** (wrong refund, bad KYC) | High | Idempotency keys, dry-run + confirmation gates, value thresholds, full audit ledger, rollback runbooks |
| **Latency** (turn >700ms breaks UX) | Medium | Streaming pipeline, filler responses, co-located inference, model routing |
| **Margin compression** (model + telephony = COGS eats outcome price) | Medium | Open Indic models for high-volume tiers; cache; route cheap model for routine intents |
| **Distribution** (BPOs build in-house / incumbents bundle) | High | Sell speed-to-value + compliance + outcome pricing; land mid-market that *can't* build; partner-led GTM |
| **Hallucination on policy** | Medium | Citation-grounded RAG only; refuse-and-escalate on low retrieval confidence |

---

## 9. TAM / SAM / SOM (India) — show the math

| Tier | Value | Derivation |
|---|---|---|
| **TAM** | **₹20,000+ Cr** | Total India BPM CX spend addressable by voice/chat automation across BFSI, telecom, e-com, GCC captives [estimate]. Anchored to India BPM (domestic ~US$5.7B + large export base; ~40% global BPM share — NASSCOM/IBEF). |
| **SAM** | **₹6,000 Cr** | The voice/chat-automatable slice (~30% of TAM): routine, high-volume, deflectable interaction spend that a compliant agent can absorb [estimate]. |
| **SOM** | **₹300–500 Cr / 3 yr** | ~5–8% of SAM captured by year 3 via mid-market + GCC land-and-expand; ~40–80 logos at ₹4–8 Cr ACV blended [estimate]. |

> All figures tagged **[estimate]**; refine with NASSCOM BPM CX cut + bottom-up logo modeling pre-Series A.

---

## 10. Competitive Landscape

| Player | Strength | Gap (our wedge) |
|---|---|---|
| **Sarvam AI** | Sovereign Indic model layer; ~$1.5B valuation, $300M Series B (2026) | Model/platform layer, not a packaged BPO CX *product* with compliant action + outcome pricing. (Likely a **supplier**, not a head-on competitor.) |
| **Gnani.ai** | Enterprise voice + biometrics, Tier-1 BFSI; raised $10M (Aavishkaar, 2026) | Enterprise/Tier-1 focused; mid-market + outcome pricing under-served |
| **Yellow.ai** | Chat-first, broad enterprise, $0.99/resolution model | Chat-led; deep *voice* + India-regulated action execution thinner |
| **Uniphore** | Enterprise CX + analytics, global | Analytics/assist-heavy; premium, not mid-market outcome-priced |
| **Observe.ai** | QA/analytics + VoiceAI agents (~$69/agent/mo benchmark) | QA-led DNA; regulated *action* execution + Indic voice depth not the core |
| **CoRover** | Indic conversational (e.g., public-sector deployments) | Breadth over BPO-grade compliant action + 100% QA flywheel |
| **Retell / Lorikeet (global)** | Best-in-class voice infra; Lorikeet ~$1.00 voice / $0.80 chat resolution | US-centric; Indic regional voice + RBI/IRDAI compliance not native |

**The wedge (white space):** *Regional-language voice depth* **+** *RBI/IRDAI-compliant action execution* **+** *outcome (per-resolution) pricing*, packaged for **mid-market BPOs and GCC captives that cannot build in-house**. No incumbent owns all three for this buyer.

**The moat (built, not bought):**
1. **Compliance-as-code** — a maintained RBI/IRDAI/DPDP rule engine + audit ledger that is painful for a horizontal vendor to replicate per-vertical.
2. **QA/eval flywheel** — 100% scored calls → proprietary Indic gold-label dataset → better routing/refusal/voice over time. Data network effect.
3. **Backend action integrations** — certified connectors to core banking / OSS-BSS / OMS with idempotency + rollback (high switching cost once live).

---

## 11. Startup Verdict

**Verdict: BUILD — as a vertical, compliance-first, outcome-priced CX platform. Not as another horizontal voice bot.**

**Probability of venture-scale success: Medium-High (~60–65%).**

- **Tailwinds (why it works):** existential, time-boxed buyer pain (urgency 10/10); a clean three-part white space; technology readiness in 2026; fast, demonstrable ROI; favorable Indic AI funding climate (Sarvam, Gnani capitalized — validates category and supplies the model layer).
- **Headwinds (why it might not):** crowded field; distribution risk (BPOs/incumbents can move down-market); COGS/margin pressure from model+telephony; regulatory drag slowing regulated-vertical go-lives.

**GTM motion:**
- **Wedge use-case first:** start with **collections reminders + L1 support deflection** (highest attrition, clearest ROI, lower regulatory bar than lending decisions) → expand into KYC, retention, inside-sales.
- **Land-and-expand** per BPO account/campaign; price per-resolution + platform fee.
- **Partner-led:** co-sell with CPaaS (Ozonetel/Exotel) and BSPs; ride their distribution into mid-market.
- **Proof asset:** a 2-week pilot on one campaign with a 100%-QA dashboard and per-resolution cost delta — the buyer's CFO closes the deal.

**Ideal ICP:**
- **Primary:** Indian **mid-market BPOs (500–5,000 seats)** serving BFSI/telecom/e-com, with high attrition and per-seat contracts under repricing pressure, *unable to build in-house*.
- **Secondary:** **GCC/captive contact centers** needing compliant Indic automation with VPC/on-prem residency.

**Moat:** compliance-as-code + the QA/eval data flywheel + deep certified backend-action connectors — defensibility that grows with usage, not just with features.

---

## Appendix — 30/60/90 Day Action Plan

| Window | Action | Owner (placeholder) |
|---|---|---|
| **0–30d** | Validate ICP with 5 mid-market BPO CXOs; lock wedge use-case (collections/L1); bottom-up TAM refresh w/ NASSCOM CX cut; spec data contracts | Founder/CEO |
| **31–60d** | Build MVP: Conversation + Knowledge + Escalation in Hindi + 2 regional langs on LangGraph + Pipecat; one CPaaS + one CRM connector; QA scorer v1 | CTO / ML lead |
| **61–90d** | Run 2-week paid pilot on one campaign; ship 100%-QA dashboard + per-resolution cost-delta report; add Action Agent w/ HITL gates for non-regulated actions; sign LOI #2 | CTO + GTM lead |

---

### Sources
- [Sarvam raises $300M Series B](https://www.sarvam.ai/announcing-series-b) · [Sarvam AI — Wikipedia](https://en.wikipedia.org/wiki/Sarvam_AI)
- [Gnani.ai raises $10M to build sovereign AI voice agents — Inc42](https://inc42.com/buzz/gnani-ai-raises-10-mn-to-build-sovereign-ai-voice-agents/) · [Gnani.ai — Tracxn](https://tracxn.com/d/companies/gnaniai/__HbhTx0tzmN_Y8M3tPRjgMkbW8KU6xj26TL-3mQqK-7A)
- [Yellow.ai pricing](https://yellow.ai/pricing/)
- [Lorikeet — voice AI for fintech workflows / pricing](https://www.lorikeetcx.ai/articles/best-voice-ai-complex-fintech-workflows-2026)
- [Retell AI pricing](https://www.retellai.com/pricing) · [Retell AI 2026 pricing breakdown](https://www.retellai.com/blog/ai-voice-agent-pricing-full-cost-breakdown-platform-comparison-roi-analysis)
- [Observe.AI pricing](https://www.observe.ai/pricing) · [Observe.AI VoiceAI agents — VentureBeat](https://venturebeat.com/ai/observe-launches-voiceai-agents-to-automate-customer-call-centers-with-realistic-humanlike-voices-that-dont-interrupt)
- [NASSCOM — Evolution of BPM Services](https://nasscom.in/knowledge-center/publications/evolution-bpm-services-cost-outcomes-and-growth) · [IBEF — Indian IT & BPM analysis](https://www.ibef.org/industry/indian-it-and-ites-industry-analysis-presentation)
- [AI contact center: cost-per-call to cost-per-resolution](https://rits.center/blog/ai-contact-center-transformation-from-cost-per-call-to-cost-per-resolution)
