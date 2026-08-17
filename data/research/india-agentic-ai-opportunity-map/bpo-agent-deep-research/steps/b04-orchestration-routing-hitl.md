# B04 — Agent Orchestration, Routing & HITL Interrupts

**Research date:** 2026-06-24
**Scope:** India-market, multilingual (Hindi + regional + Hinglish), RBI/IRDAI/DPDP-compliant, action-taking voice+chat contact-center agent for mid-market BPOs
**Step:** Agent orchestration, routing & HITL interrupts — LangGraph/Agent-SDK, planner, resume

---

## 1. The Human Job — What a Skilled Agent ACTUALLY Does

A senior BPO contact-center agent performing routing, triage, and escalation management is executing a dense set of cognitive + mechanical micro-decisions. Broken into atomic sub-skills:

### 1.1 Intent Recognition at First Utterance

- **Phoneme-to-meaning chain.** Before the caller finishes their sentence, the agent is already building a probabilistic model of what they want. This is not keyword spotting — it is semantic inference under acoustic noise, accent variation, and code-mixing.
- **Dialect and register detection.** A caller saying "mera loan ka EMI schedule bhejiye" vs. "mujhe apna loan statement chahiye" vs. "I need my loan amortisation schedule" all map to the same downstream intent (loan statement). The agent collapses these into one intent with zero conscious thought.
- **Latent signal reading.** Prosody (speed, pitch, pauses), background noise (crying baby = stressed customer), and sentence fragments all feed into the agent's internal routing model before the intent is even articulated.
- **Ambiguity flagging.** If the first 5 seconds don't resolve intent above an internal threshold, the agent runs a clarification probe — exactly one, targeted, in the same dialect as the caller.

### 1.2 Context Assembly (Pre-Routing)

- **Caller identity resolution.** Cross-match phone number (ANI), stated name, or spoken account number against CRM in parallel with listening.
- **Account state loading.** While the caller is speaking, the agent is mentally (or screen-refreshing) pulling: account status, last interaction, open tickets, flags (DNC, VIP, dispute-in-progress, KYC-pending).
- **Session history recall.** If this is a call-back or continuation, the agent reconstructs the prior context — "they called yesterday about an EMI bounce, so this is probably follow-up."
- **Policy envelope retrieval.** Agent knows — without looking it up — what actions they can take: can they waive a fee? Extend a deadline? Which of these need supervisor approval?

### 1.3 Intent-to-Skill Mapping (The Routing Decision)

- **Intent classification.** Assign the resolved intent to an internal taxonomy: billing, technical, compliance, dispute, account-management, product-inquiry, regulatory-complaint, etc.
- **Skill-set matching.** Map the intent to the right agent/team. In a BPO: L1 (general), L2 (billing-specialist), L3 (technical-specialist), supervisor (complaints, exceptions), legal/compliance desk.
- **Queue state awareness.** The agent knows — from a real-time wallboard or pure experience — that "billing queue is backed up 12 minutes, but tech is free." This affects whether they attempt partial resolution themselves vs. transfer immediately.
- **Transfer type selection.** Cold transfer (drop, connect) vs. warm transfer (brief human-to-human handoff) vs. conference transfer (three-way, stay involved) vs. hold-and-callback. Each has protocol.
- **Priority tagging.** Escalation priority: urgent (threat of legal, press, high-value account in jeopardy) vs. normal vs. deferred. Urgent skips queue.

### 1.4 Warm Handoff Execution

- **Context briefing to receiving agent.** "Yeh customer ka naam Ramesh hai, 4th floor ka complaint hai, EMI bounce wali. Unhone already receipt bhej di WhatsApp pe, aapko sirf verify karna hai." — verbal summary in 15–30 seconds.
- **State transfer completeness check.** Confirm receiving agent has account pulled up before disconnecting.
- **Customer hold management.** Place customer on hold, brief the receiver, reconnect — all within a window that doesn't exceed patient tolerance (~90 seconds before CSAT drops).
- **Dual-call coordination.** During a warm transfer the agent is simultaneously: keeping the customer calm (on hold or live), briefing the receiver, and maintaining their own composure.

### 1.5 HITL Escalation Decision

- **Confidence threshold self-monitoring.** Agent continuously monitors: "Can I resolve this?" If resolution probability drops below an internal threshold — due to policy ambiguity, emotional volatility, or out-of-scope request — the escalation decision fires.
- **Escalation trigger categorization.** Six distinct trigger types:
  1. Customer explicitly requests supervisor/manager
  2. Transaction value above agent's authority (e.g., waiver > ₹5,000)
  3. Regulatory/legal signal (customer mentions consumer court, SEBI, press)
  4. Emotional state — distress, aggression, crying
  5. Policy ambiguity — agent doesn't know what the right answer is
  6. Identity verification failure — suspect fraud
- **Escalation path selection.** Route to: L2 specialist, supervisor, compliance desk, fraud team, or legal. Different triggers map to different paths.
- **Interrupt timing.** Human agent knows when NOT to interrupt the current customer flow — e.g., wait for the customer to finish their complaint before announcing transfer, not mid-sentence.

### 1.6 State Preservation and Resume

- **CRM wrap-up codes.** Before or immediately after transfer, tag the interaction: call reason, resolution type, disposition code, escalation flag.
- **Contextual note entry.** Free-text or structured note in CRM that the next agent (human or AI) picks up — everything they need to NOT ask the customer to repeat themselves.
- **SLA timestamp marking.** Note the time of escalation so the receiving agent's SLA clock starts correctly.
- **Post-resolution follow-up flag.** If the issue requires follow-up (callback, email confirmation, document sent), flag it with due date.

### 1.7 Sentiment and Relationship Management Throughout

- **Real-time sentiment calibration.** Continuously adjusting tone, vocabulary, pace to match and de-escalate the customer's emotional state. A frustrated customer gets slower, softer speech.
- **Language-switching.** Mid-call, if a customer switches from English to Hindi to Telugu, the agent follows — fluidly, without making it awkward.
- **Trust signaling.** Phrases like "main dekh leta hun / lete hun" ("let me look into this") buy 10–15 seconds of customer patience while the agent loads context.

---

## 2. Agent Architecture — How a 2026 AI System Does Each Sub-Step

### 2.1 The Orchestration Layer: LangGraph StateGraph

**Architecture:** LangGraph `StateGraph` with a Supervisor node (Planner) + N Skill-Worker nodes.

**State schema:**
```python
from typing import Annotated, Literal
from langgraph.graph import MessagesState
from pydantic import BaseModel

class ContactCenterState(MessagesState):
    # Call context
    caller_id: str
    ani: str
    session_id: str
    
    # Intent layer
    intent: str | None
    intent_confidence: float
    language: Literal["hi", "en", "hinglish", "ta", "te", "mr", "bn", "kn"]
    sub_intent: str | None
    
    # CRM context
    account_loaded: bool
    account_summary: dict
    open_tickets: list[dict]
    
    # Routing
    assigned_skill: str | None
    escalation_reason: str | None
    escalation_priority: Literal["low", "normal", "urgent", "critical"] | None
    transfer_type: Literal["cold", "warm", "conference"] | None
    
    # HITL
    hitl_requested: bool
    hitl_context_pack: dict | None
    
    # Compliance
    recording_disclosure_done: bool
    consent_captured: bool
    dpdp_purpose_flag: str | None
    dlt_entity_id: str | None
    
    # Audit
    turns: Annotated[list[dict], list.__add__]
    escalation_timestamp: str | None
    disposition_code: str | None
```

**Supervisor (Planner) node:**
- Model: Claude Sonnet 4.6 (routing + reasoning, deterministic at temperature=0)
- Runs intent classification → skill mapping → routing decision
- Uses structured output (tool-call) to emit routing decisions — never free-text
- Enforces `max_recursion=15` in code, not in prompt

**Worker nodes:**
- Model: Claude Haiku 4.5 (597ms TTFT, within voice latency budget)
- Each worker has a scoped tool set — billing-worker cannot call refund-tool
- Workers return via `Command(goto="supervisor")` not `END` — supervisor always re-evaluates

**HITL Interrupt:**
```python
graph.add_node("hitl_gate", hitl_gate_fn)
graph.compile(
    checkpointer=PostgresSaver(conn),
    interrupt_before=["hitl_gate"]
)
# Resume:
graph.invoke(
    Command(resume={"human_decision": "APPROVED", "approver_id": "SUP_002"}),
    config={"configurable": {"thread_id": session_id}}
)
```

### 2.2 Intent Classification Sub-Step

**Technique:** Two-stage cascade
- Stage 1: Embedding-based zero-shot classifier (IndicBERT or Sarvam-M embeddings) — 30–50ms, 22 intent classes, threshold 0.70
- Stage 2 (on low confidence): Claude Haiku 4.5 with structured tool call — 600ms TTFT

**Multilingual handling:**
- Sarvam Saaras v3 ASR for voice (Hindi + 10 Indian languages, <500ms latency)
- IndicBERT or Sarvam-M for code-mixed Hinglish NLU
- Language detection (langdetect + custom Hinglish model) runs in parallel with ASR

**Output schema (tool call):**
```python
class IntentResult(BaseModel):
    primary_intent: str       # from 22-class taxonomy
    sub_intent: str | None
    confidence: float         # 0-1
    language: str             # ISO + "hinglish"
    ambiguity_probe: str | None  # clarifying question if confidence < 0.70
    routing_hint: str         # e.g., "billing_l2", "tech_l1", "supervisor"
```

### 2.3 Context Assembly Sub-Step

**Technique:** Parallel async tool calls
- `fetch_account(ani)` → CRM API (Salesforce/Freshdesk/Zoho)
- `fetch_open_tickets(account_id)` → ticketing system
- `fetch_last_interaction(account_id)` → interaction history
- All three fire simultaneously, gated by `asyncio.gather` in the entry node

**Latency:** CRM round-trip target <200ms (p95). If >200ms, agent uses a placeholder and loads async.

### 2.4 Skill-Worker Dispatch Sub-Step

**Technique:** Supervisor node emits routing tool call:
```python
class RoutingDecision(BaseModel):
    target_worker: Literal[
        "billing_l1", "billing_l2", 
        "tech_l1", "tech_l2",
        "compliance_desk",
        "fraud_team",
        "supervisor",
        "human_hitl"
    ]
    priority: Literal["low", "normal", "urgent", "critical"]
    transfer_type: Literal["cold", "warm", "conference"]
    context_summary: str   # 2-3 sentence brief for receiving agent
    compliance_flags: list[str]
```

**Queue awareness:** Supervisor node has read access to a real-time queue-state tool that returns agent availability + queue depth. This is NOT an LLM judgment — it is a deterministic function call.

### 2.5 HITL Interrupt + Resume Pattern

**Pattern:** LangGraph `interrupt_before` on the `action_execution` node.

**Five escalation patterns in use (LiveKit HITL taxonomy):**

| Pattern | When | Blocking? |
|---|---|---|
| Interrupt-and-resume | Real-time approval needed, active call | Yes — call paused |
| Human-as-tool | Fetch human input as one tool among many | Yes — async wait |
| Approval gate | High-value action pre-authorization | Yes — caller on hold |
| Sampled review | QA/compliance spot-check (5–20%) | No — post-hoc |
| Exception-only | Auto-approve unless flag triggers | No — async |

**Context pack (evidence passed to human agent):**
```json
{
  "transcript": [...],
  "intent": "loan_waiver_request",
  "confidence": 0.91,
  "account_summary": {...},
  "open_tickets": [...],
  "sentiment_score": -0.73,
  "frustration_level": "high",
  "policy_flags": ["waiver_above_authority", "third_call_this_week"],
  "compliance_notes": ["RBI FPC: 3rd contact today — at limit"],
  "actions_attempted": ["balance_check_done", "waiver_denied_by_system"],
  "recommended_action": "escalate_to_supervisor_with_exception_authority"
}
```

**Resume latency SLA:** Human agents must acknowledge within 5 minutes (voice) / 30 minutes (chat async). Timeout triggers auto-callback scheduling.

### 2.6 Warm Transfer Execution Sub-Step

**Technique (voice path):** LiveKit `WarmTransferTask`
1. Caller placed on hold (filler audio)
2. Outbound SIP dial to supervisor (`CreateSIPParticipant`)
3. Audio context brief played to supervisor (TTS-generated from `context_summary`)
4. Supervisor joins caller room (`MoveParticipant`)
5. AI agent disconnects
6. Both sides now in direct call

**Chat path:** Conversation thread handed to human agent via CCaaS platform (Freshdesk/Zendesk/Sprinklr) with full context pack injected as internal note.

### 2.7 State Persistence + Resume

**Checkpointer:** PostgresSaver (production) / AsyncSqliteSaver (dev)
- Checkpoint write latency: <15ms (under 10KB state)
- State survives daemon restart, network failure, agent crash
- Resume via `thread_id` — exact graph position restored, no re-execution of completed nodes

---

## 3. Tooling — Concrete 2026 Stack

| Layer | Tool / Library | Version / Notes |
|---|---|---|
| Orchestration | LangGraph | 0.4.x, StateGraph + supervisor pattern |
| LLM — Planner | Claude Sonnet 4.6 | Temperature 0, routing decisions, structured tool-call output |
| LLM — Workers | Claude Haiku 4.5 | 597ms TTFT, within voice latency budget |
| LLM — Escalation Judgment | Claude Sonnet 4.6 | When confidence < 0.65 |
| ASR (Hindi/Indian langs) | Sarvam Saaras v3 | 11 Indian languages, <500ms, enterprise API |
| NLU / Embeddings | Sarvam-M or IndicBERT | Code-mixed Hinglish, 22-class intent taxonomy |
| TTS | Sarvam Bulbul v2 or Smallest.ai | Natural Hindi voice, <150ms synthesis |
| Voice infra | LiveKit | SIP bridge, WarmTransferTask, room management |
| Checkpointing | PostgresSaver (LangGraph) | Durable, exactly-once, resume-from-exact-point |
| Structured outputs | Pydantic v2 + Claude tool-use | Every node boundary, zero free-text parsing |
| Observability | Langfuse + Arize Phoenix | Per-turn trace, latency, confidence, cost |
| Compliance audit | Custom JSONL + S3 | 100% call log retention, DPDP-compliant |
| CRM integration | Freshdesk / Zoho CRM MCP tool | Async fetch, <200ms p95 |
| Queue awareness | Real-time queue API tool | Deterministic Python function, not LLM call |
| HITL platform | Supervisor console (custom React) | Shows context pack, approve/reject/redirect |
| Sentiment | Amazon Comprehend Detect Sentiment (India region) or custom IndicSentiment | Real-time, per-utterance |
| Secondary framework (alt) | Claude Agent SDK | If single-model-family deploy; event-stream interrupts |

---

## 4. Benchmarks

| Metric | Number | Tag |
|---|---|---|
| Intent classification accuracy (English) | 98.49% | [sourced — ScienceDirect 2026 BPO NLU study] |
| Intent classification accuracy (Hindi) | 96.41% | [sourced — ScienceDirect 2026 BPO NLU study] |
| Intent classification accuracy (GPT-5, Hinglish hierarchical) | hF1 = 0.784 | [sourced — 2026 Mumbai urban health query study] |
| Intent classification accuracy (Sarvam-M, Hinglish) | hF1 = 0.757 | [sourced — same study, best open-weight Indian model] |
| Best-in-class routing accuracy (Swiss Life Germany IVR replacement) | 96% | [sourced — Lorikeet CX Benchmarks 2026] |
| Top-performing routing claim (billing/account access) | 98%, zero hallucinations | [sourced — Fini Labs 2026] |
| Routing accuracy threshold for acceptable misroute rate (1 in 20) | 95% | [sourced — Retell AI/Lorikeet] |
| Sarvam conversational AI latency (voice) | <500ms | [sourced — Sarvam product page] |
| Claude Haiku 4.5 TTFT (medium prompt) | 597ms | [sourced — CallSphere sub-agent post 2026] |
| Voice agent p50 end-to-end response latency | 1.4–1.7s | [sourced — Parloa agentic latency guide] |
| Voice agent p99 end-to-end response latency | 8–15s | [sourced — Hamming AI voice agent evaluation metrics] |
| Acceptable conversational latency ceiling | 800ms (caller notices if higher) | [sourced — Retell AI 2026] |
| HITL approval decision time (with context pack) | 10–30 seconds | [sourced — LiveKit HITL blog] |
| HITL approval decision time (without context) | minutes | [sourced — LiveKit HITL blog] |
| LangGraph checkpoint write latency (SQLite, <10KB state) | <15ms | [sourced — LangGraph docs / Kalvium Labs blog] |
| LangGraph token cost per task | $0.08 | [sourced — QubitTool framework comparison] |
| Claude Agent SDK token cost per task | $0.15 | [sourced — QubitTool framework comparison] |
| CrewAI token cost per task | $0.12 (but 3x tokens of LangGraph) | [sourced — QubitTool framework comparison] |
| Escalation rate trajectory (Month 1 → Month 6) | 30% → 5% | [sourced — LiveKit HITL blog] |
| FCR improvement value per 1% improvement | $50K–$80K saved (repeat contacts) | [sourced — Lorikeet 2026 benchmarks] |
| CSAT: AI-handled vs human-handled | 4.10/5 vs 4.30/5 (0.20 gap) | [sourced — Lorikeet 2026 benchmarks] |
| CSAT gap: structured intents (password reset) | Near parity | [sourced — Lorikeet 2026 benchmarks] |
| CSAT gap: sentiment-heavy (complaints) | Significant gap remains | [sourced — Lorikeet 2026 benchmarks] |
| AI call handling target for healthy BPO | 30–50% of volume | [sourced — Natterbox 2026 benchmarks] |
| Human FCR floor | >75% | [sourced — Natterbox 2026 benchmarks] |
| India BFSI voice-to-WhatsApp deflection rate (top-quartile) | 41% | [estimate — ElisionTec India BFSI data] |

---

## 5. Failure Modes

### 5.1 Intent Misclassification Under Code-Mixing

**What breaks:** When a caller alternates mid-sentence between Hindi, English, and a regional language (Hinglish + Tamil fragments are common in Chennai BPOs), the intent classifier trained on single-language corpora fails. The supervisor routes to the wrong worker.

**Why:** IndicBERT and even Sarvam-M trained primarily on Hindi-English; tri-lingual mixing is an underrepresented distribution in training data. The semantic boundary of the intent can shift with code-switches.

**Cascade:** Wrong worker gets the call, can't resolve, re-routes (adds 30–60 seconds), customer frustration rises, sentiment deteriorates, HITL triggers — but now the context pack the human gets is muddied.

### 5.2 Supervisor Node Routing Loop

**What breaks:** LLM-based supervisor gets into a circular routing pattern — sends to billing-l2, gets back a "cannot resolve," routes back to billing-l2 with marginally different instructions, ad infinitum.

**Why:** Without a hard-coded `max_iterations` in Python (not in the prompt), the graph recurses until timeout or context window fills.

**Fix:** `recursion_limit=15` enforced in `StateGraph.compile()`. Any breach triggers immediate HITL escalation with the full routing history attached.

### 5.3 Stale Context Pack on HITL Handoff

**What breaks:** Human supervisor receives context pack that was correct 3 minutes ago but the customer has since volunteered new information (account number, new complaint, emotional state change) — human makes a decision based on stale data.

**Why:** Context pack is assembled at interrupt-time, not at resume-time. Any turns between interrupt and human pickup are not in the pack.

**Fix:** Context pack must be assembled at `interrupt_before` AND refreshed with all subsequent turns if the human takes >30 seconds to respond. Diff-highlighting: show what changed since interrupt was triggered.

### 5.4 Compliance Disclosure Race Condition

**What breaks:** In a complex orchestration — e.g., supervisor routes mid-conversation to billing-l2, which routes to a collections worker — the TRAI-mandated recording disclosure ("yeh call recording ho rahi hai") may not have been delivered in the opening utterance, or it was delivered by the wrong worker in the wrong language.

**Why:** Disclosure responsibility is not pinned to any single node; each worker assumes another did it.

**Fix:** Compliance guard-node runs as `interrupt_before` on every worker node. Checks `state.recording_disclosure_done == True` before proceeding. If False, executes disclosure before any other action. This is a hard gate, not a soft check.

### 5.5 LLM-Hallucinated Policy Application

**What breaks:** A worker LLM invents a policy ("aap ko 3 din mein refund milega") that does not exist, commits it verbally to the customer, but cannot execute it via tool call because the refund-tool rejects the timeline.

**Why:** Worker models operating at temperature > 0 can fabricate policy details when the policy is not in their context.

**Fix:** All policy answers must come from a policy RAG retrieval + citation, not LLM generation. Workers are constrained to only state what a policy tool call returns. If policy tool returns null/empty, worker must acknowledge uncertainty and escalate.

### 5.6 Warm Transfer Audio Latency Spike

**What breaks:** The warm transfer sequence (hold → dial supervisor → brief → move → disconnect) takes 90–180 seconds. Customer hears silence/hold music; 15% of customers hang up before reconnect.

**Why:** SIP outbound dial + room migration + audio handover adds compounding latency. If the supervisor is not available, the sequence fails mid-way.

**Fix:** Pre-allocate supervisor capacity (never 100% utilization). Use filler speech ("Ek minute main supervisor se baat kar ke aata hun, please hold karein") before initiating transfer. Hard timeout 5 minutes — if supervisor not available, offer callback.

### 5.7 Checkpoint Corruption Under High Load

**What breaks:** Under concurrent load (100+ simultaneous calls), PostgresSaver checkpoint writes can conflict if not using row-level locking per thread_id.

**Why:** Multiple workers writing to same checkpoint row.

**Fix:** Thread-ID-scoped row locks. LangSmith Deployment's managed checkpointing handles this with exactly-once semantics.

### 5.8 DLT Template Mismatch (India-specific)

**What breaks:** TRAI DLT requires that outbound messages (WhatsApp, SMS) use pre-registered templates. If the agent dynamically constructs a message that doesn't match a registered template, the message is blocked by the telco — and the customer receives nothing.

**Why:** LLM-generated free-text responses are not DLT templates.

**Fix:** All outbound notifications (SMS, WhatsApp) must use pre-registered template slots filled from structured data. LLM is never the final generator of outbound comms — it fills template variables, not the template itself.

---

## 6. Gap to Full Adaptation — Human vs. Agent

### 6.1 What the Agent CANNOT Do as Well as a Human (Today)

**A. Tri-lingual mid-sentence code-switching**
A skilled Chennai BPO agent handles a caller who says: "Naan enna panrathu theriyala... mera account mein kuch problem ho rahi hai... can you check?" (Tamil + Hindi + English) fluidly. Current NLU models — including Sarvam-M — are not yet trained on three-language mixed corpora at scale.

*Path to close:* Fine-tune Sarvam-105B or a multilingual LLM on proprietary BPO call transcripts tagged with tri-lingual mixing. Budget: 10K labeled hours of code-switched audio across Tamil+Hindi+English, Telugu+Hindi+English, Kannada+Hindi+English. Eval metric: intent accuracy on code-switched test set > 94%.

**B. Implicit emotional de-escalation**
A human agent feels the caller's emotional state shifting and micro-adjusts in real time — a slightly softer tone, a pause, a gentle "samajh sakta hun aapki problem" — without triggering a formal escalation. The AI equivalent (sentiment-triggered tone change in TTS) is a blunt instrument. It detects frustration at utterance level, not at word-within-utterance level, and the TTS voice shift is perceptible and slightly robotic.

*Path to close:* Emotion-aware TTS (ElevenLabs Emotional TTS / Sarvam Bulbul emotional variants) with sub-utterance sentiment detection. Requires fine-tuned prosody models. 12–18 months from production-grade for Hindi/Hinglish.

**C. Policy ambiguity navigation**
When a policy is genuinely ambiguous, a skilled agent applies judgment — they weigh the customer's history, the risk to the company, and makes a call. The AI today can only (a) escalate to HITL or (b) apply the most conservative policy reading. It cannot exercise genuine discretion.

*Path to close:* RLHF on supervisor-approved vs. supervisor-overridden decisions. Build a "policy judgment" eval set from historical escalation outcomes. Train a DPO-fine-tuned policy-reasoning model on these. 6–12 months of data collection + fine-tuning.

**D. Relationship continuity across sessions**
A long-tenure BPO agent remembers that "Mrs. Sharma always calls on the 5th of the month about her FD interest credit and needs reassurance." This isn't in the CRM — it's in the agent's head. The AI has no equivalent of this implicit relational memory.

*Path to close:* Episodic memory layer (ChromaDB or Pinecone with per-customer vector store) capturing interaction patterns, stated preferences, recurring issues. Auto-populated from call summaries. Needs 6–12 months of data accumulation per customer before it equals long-tenure human recall.

**E. Improvisation when systems fail**
If the CRM goes down mid-call, a human agent improvises — takes notes on paper, asks targeted questions, commits to a callback. The AI agent, without its tool calls returning, typically fails gracefully but cannot improvise around the failure.

*Path to close:* Graceful degradation mode: agent switches to "manual-note collection" mode when tool calls time out, gathers structured information verbally, creates an offline work order. Requires deliberate engineering, not just better models.

---

## 7. HITL Trigger Conditions

The following conditions MUST trigger human takeover. "None — fully automatable" is NOT the classification here; this step has mandatory HITL for both regulatory and quality reasons.

| Trigger | Rationale | Priority |
|---|---|---|
| Customer explicitly requests supervisor/manager | Statutory right (RBI FPC) | Critical — immediate |
| Transaction / exception value above agent authority (e.g., waiver > ₹5,000) | Policy — financial authority limit | Urgent |
| Legal / regulatory threat stated by customer ("consumer court", "SEBI complaint", "press") | Legal exposure | Critical |
| Sentiment score < -0.8 AND 2+ consecutive turns | Emotional crisis | Urgent |
| Intent confidence < 0.55 after clarification probe | Model uncertainty | Normal |
| Identity verification failure (3 failed attempts) | Fraud risk + KYC/AML mandate | Critical |
| Routing loop detected (>3 worker re-routes) | System failure | Urgent |
| RBI FPC: 3rd contact same borrower same day | Regulatory hard limit | Critical — must stop call |
| DPDP consent not capturable (customer refuses) | Cannot proceed legally | Normal — offer callback |
| Any action not in worker's tool-set authority | Tool policy enforcement | Normal |
| Compliance flag: recording disclosure not delivered in opening 30 seconds | TRAI/DPDP requirement | Critical — disclosure must happen |

---

## 8. Automation Readiness: 6/10

**Rationale:**

The orchestration and routing layer is technically well-solved (LangGraph + LLM supervisor = production-grade in 2025–2026). The HITL interrupt mechanics are mature (interrupt_before/after with PostgresSaver). The failure is not in the framework — it is in the data and compliance layers specific to India.

**What's ready (pushing toward 8–9):**
- LangGraph StateGraph with supervisor + interrupt — proven in production
- Structured output routing decisions — eliminates hallucination in routing
- Claude Haiku 4.5 at 597ms — within voice latency budget
- Sarvam Saaras v3 for Hindi/Indian-language ASR — production-grade
- HITL approval pattern — LiveKit warm transfer is production-shipped

**What's not ready (pulling down to 6):**
- Tri-lingual code-switching NLU — training data deficit
- Compliance orchestration (DPDP + TRAI DLT + RBI FPC) — requires custom guard nodes; not plug-and-play
- Policy judgment under ambiguity — requires fine-tuning + historical data
- Emotional de-escalation via TTS — Hindi prosody models immature
- Per-BPO intent taxonomy mapping — each BPO has its own taxonomy; zero-shot mapping is ~85%, needs supervised fine-tuning to reach 96%+

---

## 9. Build Spec

### 9.1 What to Implement

**Module B04: Orchestration + Routing + HITL Engine**

**Components:**

1. **ContactCenterStateGraph** — LangGraph `StateGraph` with:
   - `entry_node`: parallel async CRM fetch + ASR transcription + disclosure check
   - `intent_classifier_node`: two-stage (IndicBERT/Sarvam-M → Haiku fallback)
   - `supervisor_node`: Sonnet 4.6, temperature=0, structured routing tool-call
   - `skill_worker_nodes`: per-skill (billing_l1, billing_l2, tech_l1, tech_l2, compliance, fraud)
   - `compliance_gate_node`: hard gate before every worker — checks disclosure, consent, DLT template
   - `hitl_gate_node`: assembles context pack, emits interrupt, waits for resume
   - `warm_transfer_node`: LiveKit WarmTransferTask
   - `wrap_up_node`: CRM disposition code + JSONL audit entry

2. **Intent Taxonomy** — 22-class taxonomy, per-BPO fine-tunable:
   - Billing (6 sub-classes), Technical (4), Account Management (3), Compliance (2), Product Inquiry (3), Dispute (2), Fraud (2)

3. **HITL Console** — React UI for supervisor:
   - Receives context pack via WebSocket
   - Displays: transcript, intent, confidence, sentiment trend, account history, policy flags
   - Actions: APPROVE / DENY / REDIRECT / MODIFY + free-text note
   - SLA countdown timer (5-minute window for voice)

4. **Compliance Audit Log** — JSONL per call:
   - Fields: call_id, session_id, dlt_entity_id, recording_disclosure_ts, consent_captured, language, turns[], routing_decisions[], hitl_events[], disposition_code
   - Retention: 5 years (DPDP + TRAI minimum)

5. **Queue State Tool** — Deterministic Python function:
   - Returns: {worker_type: str, available_agents: int, queue_depth: int, estimated_wait_seconds: int}
   - Called every routing decision; never cached > 5 seconds

### 9.2 Data Required

| Data | Volume | Purpose |
|---|---|---|
| Labeled intent dataset (Hindi + Hinglish + English) | Minimum 5,000 per intent class (22 classes = 110K examples) | Fine-tune IndicBERT / Sarvam-M intent classifier |
| Historical escalation records (trigger type + outcome) | 50K examples | Train confidence thresholds for HITL triggers |
| BPO-specific intent taxonomy | 1 per BPO client | Customize 22-class base taxonomy |
| CRM schema for each BPO | 1 per client | Account fetch tool definitions |
| DLT-registered template list | Per BPO, per telecom operator | Outbound comms compliance |
| Call recordings (consented) | 1,000 hours minimum | ASR fine-tuning for BPO-specific accent/domain vocabulary |
| Supervisor escalation outcomes (approved/denied/modified) | 10K examples | RLHF signal for policy judgment model (Phase 2) |

### 9.3 Eval Metric Gates

The step is considered "good enough to ship" when ALL of the following pass:

| Eval | Metric | Pass Threshold |
|---|---|---|
| Intent classification accuracy (Hindi + Hinglish test set, 1K examples) | Accuracy | ≥ 94% |
| Routing correctness (given correct intent, right worker dispatched) | Accuracy | ≥ 97% |
| HITL trigger false-positive rate (HITL triggered when not needed) | FPR | ≤ 8% |
| HITL trigger false-negative rate (HITL NOT triggered when needed) | FNR | ≤ 2% (safety-critical) |
| Compliance gate pass-rate (disclosure delivered in opening 30s) | Rate | 100% (hard gate) |
| Warm transfer success rate (caller stays through transfer) | Rate | ≥ 85% |
| End-to-end routing latency (ASR finish → worker first token) | p95 | ≤ 1.2s |
| LangGraph checkpoint write latency | p99 | ≤ 50ms |
| DLT template compliance rate | Rate | 100% (hard gate) |
| HITL context pack staleness (pack refreshed if resume > 30s after interrupt) | Coverage | 100% |

**Eval framework:** Promptfoo for LLM routing decisions + custom pytest harness for compliance gates + Langfuse for live production monitoring.

**CI gate:** Every PR to the routing layer runs the full eval suite. Any metric drop below threshold = PR blocked.

---

## 10. India Specifics

### 10.1 Linguistic

**Hinglish is the dominant register in North Indian BPOs.** A caller from Delhi or Lucknow will naturally say "mere account mein koi issue hai, please fix karo" — English verbs conjugated in Hindi grammar. The NLU layer must handle this without mapping it to English or Hindi monolingual intent spaces.

**South Indian BPOs** deal with Tamil-Hindi-English, Telugu-Hindi-English mixing. These are distinct distributions from Hinglish and need separate training data.

**Formality register shifts by language.** A caller may be casual in Hindi ("bhai, kya ho gaya?") but formal in English ("I would like to escalate this matter"). The sentiment and urgency detection must account for register, not just language.

**Language-switch mid-complaint** is culturally normal and signals emotional escalation. If a caller switches from English to Hindi mid-sentence, it often means they are dropping code-switching effort under stress — treat this as an implicit frustration signal.

### 10.2 Regulatory

**TRAI DLT (Phase 3, 2026):**
- Every outbound voice call and message must use a pre-registered DLT header and template
- The orchestration layer must validate the `dlt_entity_id` and `template_id` before any outbound call/SMS/WhatsApp is initiated
- Non-compliance: telco blocks the message; RBI/TRAI can impose license penalties

**DPDP Act 2023 (Digital Personal Data Protection):**
- Explicit consent must be captured and logged before any personal data processing
- Purpose limitation: if consent was given for "loan collections," the agent cannot use that data for "product upsell" routing without fresh consent
- Erasure rights: if a customer invokes data erasure, all call recordings and transcripts must be deletion-flagged and the CRM purged within mandated window
- Penalty: up to ₹250 crore per breach
- Compliance gate in orchestration: `consent_captured == True` AND `dpdp_purpose_flag` matches the current workflow before ANY CRM write or data processing

**RBI Fair Practices Code (BFSI):**
- Max 3 contacts per borrower per day (voice call counts as one contact)
- Call window: 8:00 AM – 7:00 PM only
- Language disclosure mandatory: agent must state the language of the call
- Recording disclosure in opening utterance
- Supervisor escalation path must always be offered
- The routing layer must track `daily_contact_count` per borrower and hard-stop at 3

**IRDAI (Insurance):**
- Telecalling norms for insurance: mandatory disclosure of caller identity, product being discussed, and do-not-disturb compliance
- Claims routing must follow IRDAI TAT (Turnaround Time) mandates — routing decisions that delay a claim beyond TAT trigger regulatory risk

### 10.3 Infrastructure

**Most mid-market Indian BPOs run hybrid telephony** — some on-premise Avaya/Cisco EPABX, some on cloud (Exotel, MCUBE, Knowlarity). The orchestration layer must integrate via SIP trunk or WebRTC, not just cloud-native APIs. LiveKit's SIP bridge handles this.

**Internet reliability in Tier-2/3 cities.** BPO agents in Nagpur, Jaipur, Indore — typical expansion cities for mid-market BPOs — may have 30–50ms additional latency compared to metro agents. The p99 latency budget must account for this.

**WhatsApp deflection** is not optional — it is the primary async channel. The routing layer must have a first-class `deflect_to_whatsapp` worker node for intents suitable for async resolution (document upload, status check, receipt delivery).

---

## References

- [LangGraph Supervisor Patterns 2026](https://www.lifetideshub.com/langgraph-supervisor-patterns-2026/)
- [LangGraph Multi-Agent Orchestration Enterprise Guide](https://devops.gheware.com/blog/posts/langgraph-multi-agent-orchestration-enterprise-2026.html)
- [Claude Agent SDK HITL — npm cloudbase example](https://www.npmjs.com/package/@cloudbase/agent-examples-claude-agent-human-in-the-loop)
- [Anthropic — Effective Harnesses for Long-Running Agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)
- [AI Agent Framework Showdown 2026: LangGraph vs CrewAI vs AG2 vs Claude SDK](https://qubittool.com/blog/ai-agent-framework-comparison-2026)
- [LiveKit — Human-in-the-Loop Pattern for Voice Agents](https://livekit.com/blog/human-in-the-loop-voice-agents)
- [HITL Escalation Design for AI Agents 2026](https://www.digitalapplied.com/blog/human-in-the-loop-escalation-design-ai-agents-2026)
- [Contact Center Benchmarks 2026 — Lorikeet CX](https://www.lorikeetcx.ai/articles/contact-center-benchmarks)
- [AI Voice Agents for Intent-Based Call Routing 2026 — Fini Labs](https://www.usefini.com/guides/ai-voice-agents-intent-based-call-routing)
- [Sarvam AI Conversational Agents](https://www.sarvam.ai/products/conversational-agents)
- [Sub-Agent Pattern with Haiku 4.5 — CallSphere Blog](https://callsphere.ai/blog/td30-anth-haiku45-subagent)
- [Agentic AI Latency — Parloa](https://www.parloa.com/knowledge-hub/agentic-ai-latency/)
- [Voice Agent Evaluation Metrics — Hamming AI](https://hamming.ai/resources/voice-agent-evaluation-metrics-guide)
- [AI Calling Compliance India 2026 — DPDP TRAI DLT RBI](https://www.autointerviewai.com/blog/ai-calling-india-dpdp-trai-dlt-compliance-complete-guide-2026)
- [India BPO Contact Center Benchmarks 2026 — ElisionTec](https://www.elisiontec.com/how-leading-indian-banks-are-outperforming-2026-contact-center-benchmarks/)
- [COMI-LINGUA Dataset — Code-Mixed Hindi-English NLP 2026](https://arxiv.org/pdf/2503.21670)
- [Hinglish Intent Classification — ScienceDirect 2026](https://www.sciencedirect.com/org/science/article/pii/S1438887126002645)
- [RBI DPDP Dual Compliance BFSI 2026](https://www.tcsa.in/resources/dpdp-compliance-bfsi-rbi-guidelines)
- [LangGraph in Production — Kalvium Labs](https://www.kalviumlabs.ai/blog/langgraph-in-production-stateful-multi-step-agents/)
- [AI Agent Failure Modes — Galileo](https://galileo.ai/blog/agent-failure-modes-guide)
- [Building HITL Agentic Workflows — Towards Data Science](https://towardsdatascience.com/building-human-in-the-loop-agentic-workflows/)
