# B12 — Observability & Cost-per-Resolution / COGS Control
## Per-turn traces, model routing economics, and margin protection for India BPO AI agents

> **Step classification:** Infrastructure / FinOps / MLOps cross-cutting concern
> **Scope:** Every LLM call in every other step (A01–A17, B01–B11) flows through this layer.
> **Research date:** 2026-06-24
> **Applies to:** India-market, multilingual (Hindi + regional + Hinglish), RBI/IRDAI/DPDP-compliant, action-taking voice+chat contact-center agent

---

## 1. What This Step Actually Is

In a human BPO, "observability & cost control" is a **management and back-office function**, not something an individual agent does consciously. The *human agent* is unaware of per-turn cost accounting — they just talk. The cost tracking is done by:

- **Workforce Management (WFM) systems** — tracks agent time, AHT, login/logout, wrap-up codes
- **Quality Monitoring (QM) teams** — samples and scores calls post-hoc
- **Finance / BI teams** — aggregates cost per contact, cost per resolution, gross margin per client account
- **Supervisor dashboards** — real-time occupancy, queue depth, SLA breach alerts

In an **AI agent system**, this management layer collapses into a **runtime engineering component** that must replicate ALL of the above — in real time, at sub-second granularity, per-turn, per-tenant — because there is no human supervisor watching a queue dashboard. The AI system must be its own WFM + QM + FinOps + Supervisor.

This makes B12 a **non-negotiable foundation**. Without it: runaway costs, no margin visibility, no SLA enforcement, no regulatory audit trail, and no ability to route queries to the right model tier.

---

## 2. Human Micro-Steps (Atomic Decomposition)

These are the smallest cognitive + mechanical + institutional moves that produce "observability & cost control" in a human BPO operation. They are distributed across multiple roles but must all be replicated by the AI system.

### 2.1 — Per-Interaction Time Capture
- **H-1:** Agent clocks in/out of the telephony system (Avaya, Genesys, NICE). ACD (Automatic Call Distributor) records exact start timestamp.
- **H-2:** Agent presses "ACW" (After Call Work) button at call end. This transitions status and starts the ACW timer.
- **H-3:** Agent selects disposition code (e.g., "Complaint Resolved," "Escalated to L2," "Follow-up Required") from a dropdown. This encodes resolution type.
- **H-4:** Agent clicks "Ready" to return to queue. System records ACW duration and total handle time.
- **H-5:** WFM system aggregates: talk time + hold time + ACW = AHT. Stored in database by agent ID, queue ID, date.

### 2.2 — Resolution Quality Self-Assessment
- **H-6:** Agent mentally judges: "Did I resolve this?" — first-contact resolution judgment based on whether customer seemed satisfied and whether issue was closed.
- **H-7:** Agent may add a note in CRM: "Customer confirmed problem fixed" or "Promised callback in 48h." This is the only per-interaction quality signal at creation time.
- **H-8:** Agent escalates or transfers if unresolved — this flags the interaction as FCR=false in WFM.

### 2.3 — Post-Hoc QA Sampling
- **H-9:** QA analyst pulls a random 2–5% sample of calls from the call recording system (Verint, NICE).
- **H-10:** QA analyst listens to full recording, scores against a rubric (compliance, tone, accuracy, AHT, resolution). This is done 24–72 hours after the call.
- **H-11:** QA score is logged in the QM platform. Outliers trigger coaching.
- **H-12:** QA team computes weekly/monthly agent-level and team-level QA averages. These feed into SLA reports to clients.

### 2.4 — Cost Attribution by Client/Queue
- **H-13:** Finance team maps agent FTE costs (salary + benefits + overhead = total cost) ÷ total calls handled = cost per call per agent.
- **H-14:** Finance maps agent calls to client account codes. Invoices are generated on cost-per-call or cost-per-FTE basis.
- **H-15:** Finance computes gross margin per client: (client contract price per call) − (fully-loaded agent cost per call) − (technology cost per call) = margin.
- **H-16:** Margin report is reviewed weekly/monthly by ops manager. If margin <15%, remediation (reduce staffing, renegotiate contract, or improve AHT) is triggered.

### 2.5 — Model-Equivalent: Queue/Skill Routing Economics
- **H-17:** Supervisor observes queue depth and skill-match. Decides manually whether to "bleed" a complex-skill queue into lower-skilled agents to reduce wait time (accepting lower quality). This is the human equivalent of model routing.
- **H-18:** Supervisor tracks real-time cost of queue spillover: a senior agent handling a simple inquiry costs more than necessary.

### 2.6 — Anomaly Detection & Escalation
- **H-19:** QA team flags AHT spikes: if call average is 6min but today's is 14min, investigate. Usually means system outage, difficult issue type, or undertrained agents.
- **H-20:** Finance flags cost overruns: if invoice total is 20%+ over plan, escalate to ops manager. Root cause analysis follows.
- **H-21:** Supervisor escalates to IT if call recording or CRM is down — observability infrastructure itself needs monitoring.

### 2.7 — Regulatory Audit Trail (India-specific)
- **H-22:** Compliance officer ensures all calls are recorded and stored for mandated duration (RBI: 5 years for financial calls, IRDAI: specific policy-related calls, CERT-In: 180-day log retention).
- **H-23:** On regulatory request (RBI audit, consumer forum case), compliance officer retrieves specific call recording + disposition log + agent ID + timestamp chain. This is a manual retrieval process taking hours to days.
- **H-24:** Compliance officer ensures PII in call notes is handled per DPDP data minimization principles — sensitive data is not retained beyond necessary period.

---

## 3. Agent Approach — How a 2026 AI System Performs Each Sub-Step

### 3.1 — Per-Turn Trace Emission (replaces H-1 through H-5)

**Pattern:** OpenTelemetry GenAI Conventions + LLM Harness Layer

Every LLM call is wrapped at the harness layer (not at the model provider SDK level) with a structured span that carries:

```python
# OpenTelemetry GenAI span attributes (MANDATORY per OTel 2026 conventions)
gen_ai.system = "anthropic"             # or "openai", "google"
gen_ai.request.model = "claude-haiku-4-5"
gen_ai.usage.input_tokens = 1847        # raw count from API response
gen_ai.usage.output_tokens = 312
gen_ai.usage.cached_read_tokens = 1200  # Anthropic cache hit
gen_ai.usage.cached_write_tokens = 0

# Custom attribution namespace (per-tenant BPO requirement)
bpo.tenant_id = "HDFC_CC_PROD"
bpo.session_id = "sess_98f3a2"          # conversation ID
bpo.turn_number = 4                     # which turn in this conversation
bpo.intent_class = "balance_inquiry"    # from intent classifier
bpo.model_tier = "cheap"               # cheap | premium | cascade_escalated
bpo.tool_calls_fired = 2               # number of tool invocations this turn
bpo.rag_chunks_retrieved = 3           # RAG context tokens injected
bpo.resolution_outcome = null          # filled at conversation end
```

Token cost is computed at harness layer using a **pricing table** (not hardcoded in model provider SDK, because prices change):

```python
PRICING = {
    "claude-haiku-4-5":   {"input": 1.0, "output": 5.0, "cached_read": 0.10, "cached_write": 1.25},  # $/MTok
    "claude-sonnet-4-6":  {"input": 3.0, "output": 15.0, "cached_read": 0.30, "cached_write": 3.75},
    "claude-opus-4-8":    {"input": 15.0,"output": 75.0, "cached_read": 1.50, "cached_write": 18.75},
}

def compute_turn_cost(model: str, usage: dict) -> float:
    p = PRICING[model]
    cost_usd = (
        (usage["input_tokens"] - usage["cached_read_tokens"]) / 1e6 * p["input"]
        + usage["cached_read_tokens"] / 1e6 * p["cached_read"]
        + usage.get("cached_write_tokens", 0) / 1e6 * p["cached_write"]
        + usage["output_tokens"] / 1e6 * p["output"]
    )
    return cost_usd
```

**Key engineering insight:** Emit raw token counters, not pre-computed cost. Pricing tables change; counters don't. Recompute cost on analytics read.

The four token layers are tracked separately:
- **Prompt layer:** system prompt + few-shots (usually cached)
- **Tool layer:** tool schemas + tool-call results returned to model
- **Memory/RAG layer:** retrieved context chunks injected
- **Response layer:** completion tokens (priced 4-5x input at most providers)

### 3.2 — Resolution Quality Signal (replaces H-6 through H-8)

**Pattern:** Automated CSAT proxy + LLM-as-judge post-call scoring

At conversation end, a lightweight Haiku-class model scores the conversation on 4 rubrics:
- **Resolution:** Was the stated intent resolved? (binary + confidence)
- **Compliance:** Were mandatory disclosures made? (binary, from B08 compliance-as-code engine)
- **Tone:** Was language appropriate? (1–5 Likert)
- **Accuracy:** Were all factual claims grounded in retrieved knowledge? (via RAG faithfulness check)

This replaces the 2–5% sampled QA human review (H-9 through H-12) with **100% coverage at <$0.001 per conversation** using Haiku.

```python
# Post-conversation LLM-as-judge (runs async, does not block customer)
judge_prompt = """
You are a QA auditor for an India BPO contact center.
Score this conversation on: resolution (0/1), compliance (0/1), tone (1-5), accuracy (1-5).
Return JSON only: {"resolution": 1, "compliance": 1, "tone": 4, "accuracy": 4, "fcr": true}
CONVERSATION: {transcript}
"""
# Model: claude-haiku-4-5, cached system prompt, ~800 token input, ~80 token output
# Cost: ~$0.0008 per conversation
```

The resolution flag (fcr=true/false) is written back to the trace and feeds into cost-per-resolution calculation.

### 3.3 — Real-Time Cost Attribution (replaces H-13 through H-16)

**Pattern:** Per-span cost rollup + nightly margin report

The trace backend (Langfuse self-hosted / ClickHouse) aggregates costs along three dimensions:
1. **Per-conversation:** `SUM(turn_cost)` across all spans with same `session_id`
2. **Per-tenant:** `SUM(conversation_cost)` grouped by `tenant_id` — maps to BPO client
3. **Per-intent:** `AVG(conversation_cost)` by `intent_class` — identifies expensive query types

**Cost-per-resolution formula:**
```
CPR = SUM(all_turn_costs_in_conversation) 
      + telephony_cost_per_minute × avg_conversation_duration_minutes
      + stt_cost_per_second × avg_audio_seconds
      + tts_cost_per_character × avg_tts_chars
      + embedding_cost (RAG retrieval)
      + vector_db_cost (per-query)
```

Typical fully-loaded CPR breakdown for an India BPO AI agent (2026 estimates):
| Component | Cost (INR) |
|---|---|
| LLM turns (3-8 turns, Haiku-dominant) | ₹0.20 – ₹0.60 |
| Telephony / CPaaS (Exotel/Plivo) | ₹0.50 – ₹2.00 |
| ASR (Sarvam AI / Deepgram) | ₹0.10 – ₹0.40 |
| TTS (Azure Neural / Sarvam) | ₹0.05 – ₹0.20 |
| RAG retrieval + reranking | ₹0.02 – ₹0.10 |
| Observability infra (Langfuse self-hosted) | ₹0.01 – ₹0.05 |
| **Total AI CPR** | **₹0.88 – ₹3.35** |
| **Human agent CPR (benchmark)** | **₹35 – ₹200** |
| **AI cost reduction** | **60–97%** |

### 3.4 — Model Routing Economics (replaces H-17 through H-18)

**Pattern:** Three-layer cascade routing with RouteLLM / classifier-based gating

The routing system operates on three layers with increasing latency:

**Layer 1 — Rule-based (< 1ms):**
```python
CHEAP_INTENTS = {"balance_inquiry", "statement_request", "branch_locator", "faq_lookup"}
PREMIUM_INTENTS = {"complaint_escalation", "fraud_dispute", "policy_interpretation", "loan_restructuring"}

def route_by_intent(intent: str, confidence: float) -> str:
    if intent in CHEAP_INTENTS and confidence > 0.85:
        return "claude-haiku-4-5"
    if intent in PREMIUM_INTENTS:
        return "claude-sonnet-4-6"
    return "cascade"  # proceed to Layer 2
```

**Layer 2 — Embedding classifier (~ 5ms):**
- Uses a fine-tuned BGE-M3 classifier trained on 5,000 labeled BPO queries
- Predicts "complexity score" 0–1
- Score < 0.4 → Haiku; 0.4–0.75 → Sonnet; > 0.75 → Opus
- BGE-M3 chosen for Indic language support

**Layer 3 — Cascade (adds 1 full LLM RTT, ~500ms):**
- Route to Haiku first
- If response confidence < threshold OR contains hedging language → escalate to Sonnet
- Sonnet handles if needed; Opus reserved for genuine edge cases only

**Cost impact of routing (2026 benchmarks):**
| Traffic Split | Cost Reduction vs All-Opus |
|---|---|
| 70% Haiku / 30% Sonnet | ~56–69% input token savings |
| 80% Haiku / 20% Sonnet | ~64–79% savings |
| 90% Haiku / 8% Sonnet / 2% Opus | ~82–88% savings |

Source: LLMRouterBench (2026), RouteLLM paper (85% cost reduction at 95% of GPT-4 quality).

**Prompt caching economics (layered on top of routing):**
- System prompt (1,000–3,000 tokens) is stable across all calls in a BPO deployment
- With Anthropic prompt caching: cached reads cost 10% of list price
- Production cache hit rates with stable system prompts: **80–95%** 
- Result: 59–66% additional cost reduction on input token spend

Combined savings of routing + caching: **85–93% vs naive all-Opus uncached** [estimate].

### 3.5 — Anomaly Detection & Kill Switches (replaces H-19 through H-21)

**Pattern:** Statistical process control on span metrics + hard budget enforcer

Five anomaly signals with automated responses:

| Signal | Detection | Response |
|---|---|---|
| Tool-call loop | Same tool called 5+ times with identical args in 1 session | Terminate session, emit alert |
| Prompt bloat | 10%+ week-over-week token growth on same route | Alert + prompt audit trigger |
| Cache miss storm | Hit rate drops from >70% to <40% in 1 hour | Page on-call, check system prompt changes |
| Model escalation drift | Haiku→Sonnet escalation rate spikes from 20% to 60%+ | Alert + routing classifier audit |
| Tenant cost spike | Single tenant daily spend 3x above baseline | Cap enforced, Slack alert |

**Budget enforcer (hard, not soft):**
```python
# Infrastructure-layer enforcement — not an alert, but a kill
class BudgetEnforcer:
    def __init__(self, per_session_cap_usd=0.50, per_tenant_daily_cap_usd=500.0):
        self.caps = {...}
    
    async def check_before_llm_call(self, session_id, tenant_id, estimated_tokens):
        session_spend = await self.get_session_spend(session_id)
        if session_spend + estimated_cost > self.per_session_cap_usd:
            raise BudgetExhausted("Session cap reached — escalate to human")
        tenant_spend = await self.get_tenant_daily_spend(tenant_id)
        if tenant_spend > self.per_tenant_daily_cap_usd:
            raise TenantCapReached("Tenant daily budget exhausted")
```

This is infrastructure-level enforcement (not alert-based) — per "The $47,000 Agent Loop" incident archetype where alerts lag actual spend by minutes.

### 3.6 — Regulatory Audit Trail (replaces H-22 through H-24)

**Pattern:** Immutable append-only trace log with PII redaction layer

Per DPDP Act + RBI + CERT-In requirements:
- Every conversation span is written to an **immutable WORM log** (AWS S3 Object Lock / Azure Immutable Blob / on-prem WORM storage for data residency compliance)
- PII (Aadhaar, PAN, phone, name, account numbers) is **redacted from trace payloads before logging** using a Presidio-based pre-processor
- The redacted trace ID maps to a PII vault (encrypted, separate, RBAC-controlled)
- Retention: 5 years for BFSI (RBI), 3 years for insurance (IRDAI), 180 days minimum (CERT-In)
- On-demand audit retrieval: conversation ID → full trace, redacted + PII-gated

---

## 4. Tooling Stack (2026, Named, Versioned)

### Observability Layer
| Tool | Role | Deployment |
|---|---|---|
| **Langfuse v3** (ClickHouse-backed, post-Jan 2026 acquisition) | Primary trace store, cost dashboard, prompt versioning | Self-hosted on AWS Mumbai (ap-south-1) for DPDP data residency |
| **Arize Phoenix** | ML-rigor drift detection, embedding analysis, eval primitives | Self-hosted or cloud (if data residency satisfied) |
| **OpenTelemetry GenAI SDK** | Span emission standard — instrument once, export anywhere | In-process, sidcar pattern |
| **ClickHouse** | Time-series analytics on trace data, fast aggregations | Mumbai region, self-managed |
| **Grafana** | Real-time dashboards, alerting, ops visibility | Self-hosted |

### Cost Attribution & Budget Enforcement
| Tool | Role |
|---|---|
| **Portkey AI Gateway** | Request interception, routing, guardrails, cost metering; SOC2-compliant; 250+ models | 
| **Waxell SDK / LiteLLM** | Infrastructure-level budget caps, kill switches |
| **Custom pricing engine** | Pricing table + token splitter (separates prompt/tool/memory/response layers) |

### Model Routing
| Tool | Role |
|---|---|
| **RouteLLM** (open source, 2024 Stanford paper, production 2025–26) | Trained routers: matrix factorization + LLM judge + BERT classifier |
| **LiteLLM proxy** | Multi-model gateway, cost-based routing, 100+ providers |
| **NotDiamond** | Quality-aware ML routing; 50-100ms classifier overhead; SaaS or self-hosted |
| **BGE-M3** (BAAI, via HuggingFace) | Indic-language-capable embedding classifier for complexity scoring |
| **Portkey** | Conditional routing + semantic caching (cache same/similar queries) |

### Prompt Caching
| Tool | Role |
|---|---|
| **Anthropic prompt caching** (`cache_control: {type: "ephemeral"}`) | 90% cost reduction on cached reads; production hit rates 80–95% |
| **Portkey semantic cache** | Cache similar (not identical) queries via embedding match; 15–30% additional deflection |

### Compliance / PII Logging
| Tool | Role |
|---|---|
| **Microsoft Presidio** | PII detection + redaction before trace emission |
| **AWS S3 Object Lock / Azure Immutable Blob** | WORM-compliant trace archival |
| **HashiCorp Vault** | PII vault, RBAC-controlled, separate from trace store |

---

## 5. Benchmarks

| Metric | Value | Source |
|---|---|---|
| RouteLLM cost reduction on MT Bench | 85% cost reduction at 95% GPT-4 quality | [sourced — RouteLLM paper, LLMRouterBench 2026] |
| Rule-based routing latency overhead | <1ms | [sourced — digitalapplied.com 2026] |
| Embedding classifier routing overhead | ~5ms | [sourced — digitalapplied.com 2026] |
| ML classifier routing overhead | 50–100ms | [sourced — digitalapplied.com 2026] |
| Prompt caching hit rate (stable system prompt) | 80–95% | [sourced — projectdiscovery.io, web2md.org 2026] |
| Prompt caching cost reduction (Anthropic) | 90% on cached reads | [sourced — Anthropic docs] |
| Combined routing + caching savings vs naive | 85–93% | [estimate — compound of above] |
| Human CPR (India voice, inbound) | ₹35–₹200 | [sourced — crescendo.ai, squadstack.ai 2026] |
| AI CPR (fully-loaded, India) | ₹0.88–₹3.35 | [estimate — constructed from component benchmarks] |
| Cost reduction AI vs human (India BPO) | 60–97% | [sourced — crescendo.ai, rits.center 2026] |
| Human QA coverage | <5% of interactions | [sourced — rits.center 2026] |
| AI QA coverage (LLM-as-judge) | 100% of interactions | [estimate — standard pattern] |
| LLM-as-judge cost per conversation | <$0.001 (Haiku 4.5) | [estimate — constructed from Haiku pricing] |
| LLM FCR rate for eligible intents | 55–70% | [sourced — fin.ai 2026] |
| Human FCR rate (target) | 70–85% | [sourced — bpoinsighthub.com 2026] |
| Span-level token visibility overhead | <2% latency | [estimate] |
| Budget enforcer kill-switch latency | <5ms | [estimate — in-memory Redis check] |
| Cache miss detection lag | <60 seconds (streaming metrics) | [estimate] |
| CERT-In log retention requirement | 180 days minimum | [sourced — autointerviewai.com 2026] |
| RBI log retention (BFSI calls) | 5 years | [sourced — autointerviewai.com 2026] |

---

## 6. Failure Modes

### 6.1 — Silent Cost Accumulation (most dangerous)
**What:** Agent loop fires 12 tool calls in one session (API retry loop, malformed tool response). No alert fires because per-session spend is $0.80 vs $5 cap — individually fine. But 10,000 sessions/day × $0.80 = $8,000/day vs expected $2,000/day.
**Why:** Span-level aggregation lag. Dashboards update every 5min; billing compiles hourly.
**Detection:** Z-score anomaly on per-session token count, not just spend. Alert if session token count > 3SD above 7-day baseline.

### 6.2 — Silent Quality Regression from Over-Routing to Cheap Models
**What:** Routing classifier shifts 90% of traffic to Haiku. Cost drops 70%. But Haiku hallucinates on edge-case regulatory queries (IRDAI policy terms). CSAT drops 12 points over 3 weeks.
**Why:** Quality degradation is diffuse — no single incident, just gradual customer dissatisfaction. Cost dashboards are green.
**Detection:** CI eval gate on routing changes (50–500 representative cases, LLM-as-judge, before routing config deploys). Mandatory — not optional.

### 6.3 — Cache Miss Storm
**What:** A system prompt update (small change to compliance disclosure wording) invalidates the cache prefix. Cache hit rate drops from 84% to 7% overnight.
**Why:** Even one token change before a cache breakpoint invalidates everything downstream.
**Detection:** Cache hit rate time-series alert. Threshold: drop >30pp from 24h baseline triggers immediate page.
**Fix:** Always put stable content at top of system prompt. Test cache structure after every prompt edit.

### 6.4 — Prompt Bloat Creep
**What:** RAG retrieval gradually injects more context as knowledge base grows. 90 days after launch, average turn token count is 40% higher than at launch. Costs 40% more than budgeted.
**Why:** No token budget on RAG retrieval. Reranker returns top-10, but new docs are longer.
**Detection:** Week-over-week average input token count per route. >10% growth triggers audit.
**Fix:** Hard token caps on RAG injection (e.g., max 2,000 tokens of retrieved context regardless of reranker output).

### 6.5 — Tenant Cost Attribution Drift
**What:** New feature adds a background summarization call that doesn't carry `tenant_id` tag. All summarization costs pool into "unattributed" bucket. BPO margin reports become inaccurate for Client X.
**Why:** Retroactive tag addition from logs always misses edge cases.
**Fix:** Enforce `tenant_id` at middleware level — any LLM call without tenant context throws `MissingAttributionError` in non-prod, silent-fallback-to-unattributed in prod with alert.

### 6.6 — India Regulatory Non-Compliance in Trace Logs
**What:** PII (customer's PAN number, Aadhaar mentioned mid-conversation) appears unredacted in Langfuse trace. DPDP audit finds this. Penalty up to ₹250 crore.
**Why:** PII redaction runs as post-processor, but trace is emitted before redaction completes. Race condition.
**Fix:** Redaction MUST run synchronously in the span finalizer, before any network write to trace backend. Never async.

### 6.7 — Model Tier Escalation Drift
**What:** Intent classifier degrades (distribution shift as new query types emerge). Escalation rate from Haiku→Sonnet drifts from 20% to 55% over 60 days. Costs increase 2.3x without any routing config change.
**Why:** Classifier was trained on historical data; new intents aren't in the taxonomy.
**Detection:** Weekly routing tier distribution report. >5pp shift from baseline triggers retraining job.

---

## 7. Gap to Full Adaptation

### What agents cannot yet do as well as humans:

**Gap 1 — Margin negotiation and contract-level awareness:** A human BPO ops manager knows the *contract terms* with Client X — specific SLAs, penalty clauses, volume commitments, price per tier. When costs spike, they can decide to absorb it vs. bill overage vs. renegotiate. An AI system today has no model of the commercial contract layer. This gap requires: structured contract data feed into the observability system, and a business rules engine that maps operational metrics to commercial obligations.

**Gap 2 — Cross-session attribution for non-linear resolution:** A customer calls back 3 days later for a related issue. A human QA analyst listening to both calls can attribute both to the *same underlying problem* (e.g., wrong address in system → bill delivery failure → refund call). AI attribution today is session-scoped. True CPR for multi-touchpoint issues is invisible.
- **Path to close:** Customer journey graph — link sessions via customer_id + topic embedding similarity within a configurable time window (e.g., 30 days). Attribute shared issues to a "problem resolution unit" cost.

**Gap 3 — Explaining cost spikes to non-technical stakeholders:** A human ops manager can say to the client: "Costs were higher this week because we had 3 regulatory audits and a product recall inquiry surge." An AI system produces data, not explanations.
- **Path to close:** LLM-generated weekly cost narrative (Sonnet-class, analyzing the trace data) — "Cost per resolution increased 23% this week primarily due to a 40% surge in {complaint_type} intents, which route to Sonnet-tier and carry 3.2x average token count vs. FAQ intents."

**Gap 4 — Adaptive routing without labelled outcome data:** RouteLLM and classifier-based routers need labelled training data (query → correct model tier). In a new BPO deployment, this data doesn't exist.
- **Path to close:** Cold-start with conservative rule-based routing (only Haiku for proven-safe intents, Sonnet for everything else). Collect 2,000–5,000 conversations with LLM-as-judge outcome labels. Fine-tune BGE-M3 classifier. Deploy routing in shadow mode for 1 week, compare outcome vs. naive. Go live.

**Gap 5 — Total COGS visibility beyond LLM spend:** Human ops managers track ALL costs: rent, electricity, attrition, training. AI systems today track LLM + ASR + TTS + telephony — but miss: GPU server depreciation, engineering maintenance cost, compliance audit costs. True COGS comparison requires FinOps tooling that aggregates cloud bills, not just LLM API bills.

---

## 8. HITL Trigger

**Fully automatable for routine observability (no human needed for):**
- Per-turn trace emission
- Cost rollup and dashboard
- Cache hit rate monitoring
- Budget enforcement (kill switches)
- LLM-as-judge QA scoring (100% coverage)
- Alert routing to on-call

**Human MUST take over when:**
1. **Budget anomaly with unclear root cause:** Spend 5x above baseline, no automated alert explains why → SRE on-call must investigate.
2. **Regulatory audit request:** RBI/IRDAI/consumer forum requests specific call recording and audit trail → compliance officer retrieves and prepares (automated retrieval, but human presents and certifies).
3. **Routing decision with major quality impact:** Routing config change affects >10% of traffic AND CI eval shows quality within 2pp of threshold → human engineer reviews before deploy.
4. **New intent type with no routing label:** Novel query type that doesn't fit existing classifier → human labels first 50 examples before routing classifier is updated.
5. **Contract-level cost conversation with BPO client:** AI produces the data; a human account manager has the commercial discussion.

---

## 9. Automation Readiness: 7 / 10

**Rationale:**
- Per-turn tracing, cost rollup, cache optimization, budget enforcement, and anomaly detection are **fully automatable today** with Langfuse + OTel + Portkey + RouteLLM stack — rated 9/10 on their own.
- The overall score is dragged to 7/10 by: (a) cross-session problem attribution being unsolved, (b) regulatory audit trail compliance requiring human certification in India, (c) routing cold-start requiring human-labelled data, and (d) contract-layer cost governance being a human relationship.
- Specifically for India: DPDP compliance adds engineering complexity that is solvable but adds 4–6 weeks of data-pipeline work that most vendors don't pre-package.

---

## 10. Build Specification

### What to implement (in priority order):

**P0 — Per-turn trace harness (Week 1-2)**
- Wrap ALL LLM calls in OTel GenAI spans
- Emit: model, tokens (4 types), session_id, tenant_id, turn_number, intent_class, tool_calls_fired
- Ship to: Langfuse self-hosted (AWS Mumbai, ap-south-1)
- Cost computation: harness-layer pricing table, not provider SDK
- Gate: 100% span coverage (no LLM call without trace)

**P0 — PII redaction pipeline (Week 1-2, parallel)**
- Presidio Hindi model + English model + Aadhaar/PAN regex patterns
- Run synchronously before ANY span write to Langfuse
- Separate PII vault (Vault Enterprise, RBAC)
- Gate: 0 PII tokens in Langfuse after redaction (audited by regex scan on 1,000 samples)

**P1 — Model routing layer (Week 2-3)**
- Layer 1: Rule-based intent → tier map (<1ms)
- Layer 2: BGE-M3 complexity classifier (~5ms)
- Layer 3: Cascade (Haiku first, escalate on low confidence)
- Prompt caching: `cache_control: ephemeral` on system prompt + knowledge base prefix
- Gate: cost-per-resolved-session < ₹4.00 on production traffic; quality (LLM-as-judge) within 3pp of all-Sonnet baseline

**P1 — LLM-as-judge post-call scorer (Week 3)**
- Haiku-based async scorer: resolution, compliance, tone, accuracy
- Write FCR flag back to trace
- Gate: correlation with human QA sample ≥ 0.80 Pearson r on 200-call pilot set

**P2 — Budget enforcement (Week 3-4)**
- Per-session cap: $0.50 (soft alert at $0.30, hard kill at $0.50)
- Per-tenant daily cap: configurable per contract (default $500)
- Implementation: Redis-backed counter + pre-call check in harness layer
- Gate: zero budget overruns in 30-day production soak

**P2 — Anomaly detection alerts (Week 4)**
- Tool-call loop detector (same tool × 5 identical args → terminate)
- Cache hit rate monitor (30pp drop → page)
- Token bloat monitor (10%+ week-over-week → Slack alert)
- Escalation drift monitor (>5pp shift → weekly report)
- Gate: mean time to detection < 5 minutes for cache miss storm scenario

**P3 — Cost narrative generator (Week 5-6)**
- Weekly Sonnet-generated cost narrative from ClickHouse query results
- Covers: top 5 cost drivers, % change vs prior week, routing efficiency, cache performance
- Delivered: Telegram (internal ops) + email (BPO client weekly report)

### Data needed:
- 2,000+ labelled (query, correct_model_tier) pairs for routing classifier training
- PII patterns dictionary (Aadhaar format, PAN format, India phone number formats, IFSC codes)
- Client contract data (cost ceilings per tenant, SLA thresholds)
- Historical call data for baseline token-count distributions by intent type

### Eval metrics gating "this step is good enough to ship":
1. **Span coverage:** 100% of LLM calls have complete OTel span (no orphaned calls)
2. **Cost accuracy:** Computed cost vs. actual provider invoice within ±3%
3. **Cache hit rate:** ≥ 70% on production traffic after prompt structure optimization
4. **Routing quality:** LLM-as-judge score on routed traffic within 3pp of all-Sonnet baseline
5. **PII leak rate:** 0 PII tokens in trace store (verified by automated scanner on 1,000-call sample)
6. **Budget enforcement:** 0 overruns in 30-day soak test
7. **Anomaly detection MTTD:** < 5 minutes for 4/5 anomaly types on synthetic injection test

---

## 11. India Specifics

### Language and Routing Complexity
- **Hinglish and code-mix:** Same intent expressed in English ("what is my balance"), Hindi ("mera balance kya hai"), and Hinglish ("mera balance kitna hai yaar") must map to the SAME routing tier. BGE-M3 handles this — it was pretrained on multilingual data including Hindi — but the training set for the complexity classifier must include all three variants per intent.
- **Regional language surges:** A bank with significant Tamil Nadu or Maharashtra presence will see Tamil / Marathi intents during regional festivals or state-specific regulatory events. Routing classifiers must degrade gracefully to Sonnet-tier on unrecognized languages rather than routing to Haiku (which has weaker Indic language capability than Sonnet/Gemini Flash 2.0).
- **Script mixing in transcripts:** Customer might say "mujhe ₹5000 ka NEFT karna hai" — the trace must handle ₹ symbol, devanagari transliterations, and numeric amounts without tokenization artifacts corrupting cost calculations.

### Regulatory Observability Requirements (India-specific)

**DPDP Act 2023 (Digital Personal Data Protection):**
- Penalty up to ₹250 crore for significant breaches
- Trace logs = data processing activity → must be covered by the organization's privacy notice
- Data minimization: trace logs should capture intent + tokens + costs, NOT full conversation text (full text goes to separate encrypted storage with access controls)
- Customer right to erasure: if customer requests deletion, ALL traces referencing that customer_id must be purged — design trace schema with `customer_id` as an indexed, deletable field

**RBI Compliance (BFSI BPO clients):**
- All calls involving financial transactions: 5-year retention
- AI disclosure at call start must be confirmed in trace (compliance-as-code flag from B08)
- Human escalation path must always exist — budget enforcement kill switch must trigger graceful handoff, not abrupt termination

**IRDAI (Insurance BPO clients):**
- Free-look period disclosure: confirmed in trace
- Material terms confirmation: each key term disclosure must be a checkpointed event in the trace
- Policy sale call recordings: full audio + transcript stored, 3-year minimum

**CERT-In (all operators):**
- 180-day minimum log retention for ALL system events
- Incident reporting within 6 hours for major security breaches
- Trace infrastructure itself must be covered by the incident response plan

**TRAI DLT (Outbound calling):**
- All outbound AI calls must use DLT-registered headers
- TRAI ML systems detect uniform call durations (an AI calling at exactly 2:30 every time will be flagged) — inject deliberate duration variance in observation; monitor for TRAI anomaly signals

### Data Residency Requirement
- **Langfuse MUST be self-hosted in AWS ap-south-1 (Mumbai) or Azure Central India**
- Cloud-hosted Langfuse (EU servers) would violate RBI payment data storage directive and likely DPDP cross-border transfer restrictions for BFSI clients
- Model inference: if using closed APIs (Anthropic, OpenAI), conversation content crosses borders — requires DPA agreements and privacy notice disclosure; for BFSI clients, consider Bedrock (AWS Mumbai region) or Azure OpenAI (Central India) for in-region inference

### Cost Benchmarks (India-specific)
| Metric | Value |
|---|---|
| Human agent fully-loaded hourly cost (Delhi/Mumbai) | ₹150–₹400/hour (including floor space, manager, attrition cost) |
| Human CPR inbound (simple to complex) | ₹35–₹200 |
| AI CPR (as computed above, fully-loaded) | ₹0.88–₹3.35 |
| Annual attrition cost per replaced agent | ₹80,000–₹1,50,000 (recruitment + training + ramp) |
| AI attrition cost | ₹0 (model upgrade is opex, not hiring) |
| India telephony cost per minute (Exotel/Plivo) | ₹0.30–₹0.80/min |
| Sarvam AI ASR cost | ~₹0.50–₹1.00 per 100 seconds |

---

## 12. Reference Architecture Diagram (Text)

```
INCOMING CALL/CHAT
        │
        ▼
[B01 Voice Pipeline] ──────────────────────────────────────────────────────────┐
        │                                                                       │
        ▼                                                                       │
[A04 Intent Classifier] ──→ intent_class + confidence                          │
        │                                                                       │
        ▼                                                                       │
┌───────────────────────────────────────────────────────────────────────┐      │
│  B12 ROUTING LAYER (pre-LLM)                                          │      │
│  Layer 1: Rule-based intent→tier map (<1ms)                           │      │
│  Layer 2: BGE-M3 complexity classifier (~5ms)                         │      │
│  Layer 3: Cascade trigger flag                                        │      │
│  → model_tier: cheap|premium|cascade                                  │      │
│  → cache_hit_check: prompt prefix preloaded?                          │      │
└──────────────────────────┬────────────────────────────────────────────┘      │
                           │                                                    │
                           ▼                                                    │
┌───────────────────────────────────────────────────────────────────────┐      │
│  B12 BUDGET ENFORCER (pre-LLM call)                                   │      │
│  - Check session_spend vs per_session_cap                             │      │
│  - Check tenant_daily_spend vs per_tenant_daily_cap                  │      │
│  - KILL: raise BudgetExhausted → HITL escalation                     │      │
└──────────────────────────┬────────────────────────────────────────────┘      │
                           │                                                    │
                           ▼                                                    │
┌───────────────────────────────────────────────────────────────────────┐      │
│  PII REDACTION (synchronous, before span write)                       │      │
│  Presidio (Hindi + English) + custom India PII patterns               │      │
└──────────────────────────┬────────────────────────────────────────────┘      │
                           │                                                    │
                           ▼                                                    │
             [LLM API] (Haiku / Sonnet / Opus)                                 │
              Anthropic prompt caching ACTIVE on system prompt prefix           │
                           │                                                    │
                           ▼                                                    │
┌───────────────────────────────────────────────────────────────────────┐      │
│  B12 SPAN EMITTER (post-LLM call, synchronous)                        │      │
│  - 4-layer token split (prompt/tool/memory/response)                  │      │
│  - Compute turn_cost via pricing table                                │      │
│  - Emit OTel GenAI span with full attribution tags                    │      │
│  - Write to Langfuse (self-hosted, AWS Mumbai)                        │      │
└──────────────────────────┬────────────────────────────────────────────┘      │
                           │                                                    │
                           ▼                                                    │
             [Continue conversation loop] ──────────────────────────────────────┘
                           │
              (at conversation END)
                           ▼
┌───────────────────────────────────────────────────────────────────────┐
│  B12 POST-CALL SCORER (async, Haiku-class)                            │
│  - LLM-as-judge: resolution, compliance, tone, accuracy               │
│  - Write FCR flag + QA scores to trace                                │
│  - Write to WORM audit log (S3 Object Lock, 5yr retention)            │
└──────────────────────────┬────────────────────────────────────────────┘
                           │
                           ▼
┌───────────────────────────────────────────────────────────────────────┐
│  B12 ANALYTICS LAYER (ClickHouse + Grafana)                           │
│  - Real-time: cache hit rate, tier distribution, session costs        │
│  - Hourly: tenant cost rollup, CPR by intent, anomaly Z-scores        │
│  - Weekly: routing efficiency, prompt bloat, quality correlation      │
│  - Alerting: PagerDuty/Slack for anomaly signals                      │
└───────────────────────────────────────────────────────────────────────┘
```

---

## 13. Key Engineering Decisions & Rationale

| Decision | Chosen | Rejected alternatives | Why |
|---|---|---|---|
| Trace backend | Langfuse v3 (self-hosted, ClickHouse) | LangSmith (US servers), Arize cloud | DPDP data residency; Langfuse is MIT, ClickHouse-native for fast aggregations |
| Routing | BGE-M3 + RouteLLM (Layer 2 + 3) | NotDiamond SaaS, OpenRouter | Data sovereignty; BGE-M3 has Indic language support; RouteLLM is open-source |
| Budget enforcement | Infrastructure-level (Redis + harness kill) | Alert-based (Grafana alert → Slack → human) | Alerts lag; runaway costs happen in minutes |
| PII redaction | Synchronous Presidio in span finalizer | Async post-processor | Race condition risk; DPDP requires no-PII-in-trace at write time |
| Prompt caching | Anthropic native (`cache_control: ephemeral`) | Manual prompt compression | 90% cost reduction, no quality trade-off, zero latency penalty after first cache write |
| Audit log | WORM S3 Object Lock | Regular database | RBI/IRDAI compliance; tamper-proof for regulatory disputes |

---

## Sources

- [Langfuse — OTel Integration](https://langfuse.com/integrations/native/opentelemetry)
- [Braintrust — Best LLM Cost Tracking 2026](https://www.braintrust.dev/articles/best-tools-tracking-llm-costs-2026)
- [digitalapplied.com — LLM Agent Cost Attribution Guide 2026](https://www.digitalapplied.com/blog/llm-agent-cost-attribution-guide-production-2026)
- [digitalapplied.com — LLM Model Routing 2026](https://www.digitalapplied.com/blog/llm-model-routing-2026-cost-quality-optimization-engineering-guide)
- [rits.center — AI Contact Center: Cost Per Call to Cost Per Resolution](https://rits.center/blog/ai-contact-center-transformation-from-cost-per-call-to-cost-per-resolution)
- [crescendo.ai — Outsourced Call Center Pricing Guide 2026](https://www.crescendo.ai/blog/outsourced-call-center-pricing-guide)
- [squadstack.ai — AI Contact Center ROI India](https://www.squadstack.ai/voicebot/ai-contact-center-roi-ai-page)
- [autointerviewai.com — AI Calling Compliance India 2026: DPDP, TRAI DLT, RBI](https://www.autointerviewai.com/blog/ai-calling-india-dpdp-trai-dlt-compliance-complete-guide-2026)
- [LLMRouterBench arxiv 2026](https://arxiv.org/html/2601.07206v1)
- [Waxell — AI Agent Token Budget Enforcement](https://waxell.ai/blog/ai-agent-token-budget-enforcement)
- [projectdiscovery.io — How We Cut LLM Costs 59% With Prompt Caching](https://projectdiscovery.io/blog/how-we-cut-llm-cost-with-prompt-caching)
- [Portkey — Enterprise-grade AI Gateway](https://portkey.ai/features/ai-gateway)
- [fin.ai — ROI of AI Customer Service 2026](https://fin.ai/learn/roi-ai-customer-service-agents-benchmarks)
- [Arize Phoenix vs Langfuse comparison](https://langfuse.com/faq/all/best-phoenix-arize-alternatives)
- [aigrants.in — AI Observability Platforms for Indian Startups](https://aigrants.in/topics/ai-observability-platforms-for-indian-startups)
