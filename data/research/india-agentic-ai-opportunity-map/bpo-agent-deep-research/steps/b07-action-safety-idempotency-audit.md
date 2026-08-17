# B07 — Action Safety: Idempotency Keys, Dry-Run, Rollback, Value Thresholds, Immutable Audit Ledger

**Research date:** 2026-06-24  
**Scope:** India-market, multilingual (Hindi + regional + Hinglish), RBI/IRDAI/DPDP-compliant, action-taking voice+chat contact-center agent for mid-market BPOs.  
**Step in pipeline:** B-series (infrastructure / system-level). Sits between backend action execution (A11) and compliance disclosures (A12). Every write-side tool call passes through this layer.

---

## 1. What This Step Actually Is

A skilled human BPO agent who is about to issue a refund, cancel a policy, change an account address, or waive a fee does NOT just click a button. Before any write-side action fires, the agent runs a mental safety protocol — a set of cognitive micro-steps — that prevents duplicate execution, out-of-scope actions, compliance breaches, and irreversible mistakes. This dossier decomposes that protocol to its atomic level, then maps each micro-step to its 2026 AI-agent equivalent.

This is the most underengineered layer in agentic BPO systems. Getting retrieval or generation wrong produces a bad answer; getting action safety wrong causes double refunds, regulatory audit failures, and customer harm that cannot be unwound.

---

## 2. Human Micro-Steps: The Cognitive Safety Protocol

A skilled agent performing a write-side action (refund, cancel, update, escalate, waive) executes the following sub-steps in order, mostly unconsciously after training:

### 2.1 Pre-Action Intent Verification
- **Re-reads the customer's exact words** before acting (not inference, the literal request)
- **Cross-checks intent against the action type**: "Did they say cancel subscription or pause subscription?" — distinguishes reversible vs irreversible
- **Infers action scope**: single transaction? all transactions? all channels?
- **Checks for conditional language**: "if the refund isn't processed by tomorrow, cancel everything" — notes the conditionality

### 2.2 Authorization Gate (Does the Agent Have the Right?)
- **Checks own authority level** against a mental table: standard agents can issue refunds up to ₹2,000; Team Leads up to ₹10,000; Manager to ₹50,000 (typical BPO SLA)
- **Verifies the customer's identity was confirmed earlier** in the call — refuses to take action if authentication step was skipped or if OTP was not confirmed
- **Validates the customer's right to the action**: Is this their own account? Did a third party call in? Is the account under dispute/freeze?
- **Checks policy eligibility**: refund window (30 days? 90 days?), cancellation fee, pro-rata calculations

### 2.3 Duplicate / Prior-Execution Check
- **Scrolls transaction history in the CRM** — did a refund for this order already process? Was a cancellation already queued?
- **Checks pending/in-flight items**: is there already a ticket open for this? Did a previous agent start processing this and the call dropped?
- **Reads notes from prior interactions**: same call, same day, same week — to detect if this is a retry
- **Visually confirms the status column** in the CRM: "Pending", "Processing", "Completed", "Failed" — takes different action based on each

### 2.4 Dry-Run / Preview
- **States the action aloud to the customer before executing**: "I'm going to issue a refund of ₹1,450 to your original payment method ending in 4567. Can you confirm that's correct?"
- **Re-reads the amount back** to confirm no transcription error from the ticket
- **Checks the destination**: refund to card vs bank account vs wallet — confirms the correct destination
- **For cancellations, restates consequences**: "This will cancel your policy from [date], and you'll lose [benefit]. Shall I proceed?"

### 2.5 Value Threshold Decision
- **Compares the action value** to their own authority limit
- **If at limit**: mentally decides to either (a) proceed cautiously, (b) get verbal supervisor acknowledgment over their shoulder, or (c) put the customer on hold and formally escalate
- **Considers cumulative value**: even if individual refund is ₹1,500, if the customer has already had 3 refunds this week totaling ₹6,000, triggers manual review
- **Considers category**: a ₹500 goodwill waiver is different risk than a ₹500 transaction refund — policy may treat them differently

### 2.6 Execution with Deliberate Single-Action Pattern
- **Fills the form fields one-at-a-time** and reviews before submitting
- **Avoids multi-clicking** (BPO training specifically teaches: click once, wait for confirmation)
- **Waits for the system's success/failure response** before telling the customer it's done
- **Does NOT tell the customer "it's done" before seeing the system confirmation** — experienced agents know CRM can time out

### 2.7 Post-Execution Verification
- **Reads the system confirmation message** (refund ID, ticket number, ETA)
- **Checks that the status changed** in the CRM view — doesn't trust "success" toast if the status column still says "Pending"
- **Reads back the confirmation details to the customer**: "Your refund reference is RF-2024-8821. It will appear in 5-7 business days."
- **Notes the action in the call log** with exact timestamp, action taken, amount, and reference ID before wrapping the call

### 2.8 Rollback Awareness
- **Knows what's reversible and what isn't**: refund initiated = reversible for ~2 hours; refund settled = irreversible; cancellation = often irreversible; address change = reversible; OTP-based fund transfer = irreversible
- **Knows escalation path if something went wrong**: calls supervisor, opens a correction ticket, or documents a "possible duplicate" flag for back-office review
- **Does NOT tell the customer an error will be fixed without checking with a supervisor first**

### 2.9 Regulatory Disclosure Trigger
- **Knows which actions require a disclosure before proceeding**: insurance cancellations require FPC disclosure; loan-related actions require RBI Fair Practices Code disclosure; any biometric-authenticated action requires DPDP disclosure
- **Reads the mandatory disclosure verbatim if required** before executing (not after)
- **Records that the disclosure was given** in the call notes

### 2.10 Audit Entry Creation
- **Types call notes** including what action was taken, at what time, the reference number, what the customer said, and any exceptions
- **Tags the call disposition** correctly in the CRM: "Refund Issued — ₹1,450 — Ref RF-8821" not just "Resolved"
- **Attaches relevant documents** (screenshots, approval messages from supervisor chat)
- **Marks the ticket status** to the correct state: "Refund Processing", not "Closed"

---

## 3. Agent Approach: 2026 AI Implementation

### 3.1 Pre-Action Intent Verification
**Technique:** Structured output from Claude Sonnet 4.x or GPT-5 with a typed `ActionIntent` schema (Pydantic v2). The model extracts action type, scope, conditionality flag, and confidence score. Only proceed if `confidence >= 0.92`; else surface as disambiguation.

```python
class ActionIntent(BaseModel):
    action_type: Literal["refund", "cancel", "update", "waive", "escalate", "pause"]
    scope: Literal["single", "all", "category"]
    is_conditional: bool
    condition_description: Optional[str]
    amount: Optional[Decimal]
    confidence: float  # 0.0 - 1.0
    requires_disambiguation: bool
```

**Pattern:** Chain-of-Verification — model drafts the intent, then a second cheaper call (Haiku 4.x) critiques for scope ambiguity before any tool call fires.

### 3.2 Authorization Gate
**Technique:** Rule-based policy engine (not LLM — deterministic for this gate). RBAC table stored in Redis with agent tier, account tier, and per-action limits. LLM calls `check_authorization(action_type, amount, agent_tier, account_tier)` as a tool call that returns an `AuthorizationDecision` struct. No LLM inference in this path — it's pure policy.

**Pattern:** Tool Eligibility (deterministic guardrails). The authorization tool always returns a typed result; the LLM is never asked to decide authorization by reasoning — it only reads the structured result.

```python
class AuthorizationDecision(BaseModel):
    authorized: bool
    max_authorized_amount: Decimal
    reason: str  # for logging, not LLM reasoning
    escalation_required: bool
    escalation_tier: Optional[Literal["team_lead", "manager", "compliance"]]
```

### 3.3 Duplicate / Prior-Execution Check (Idempotency Layer)
**Technique:** Idempotency key generated via SHA-256 hash of `(session_id, action_type, resource_id, amount, timestamp_bucket)`. Timestamp bucket = 1-hour window to catch same-call retries.

Three-tier storage:
- **Hot** (Redis, TTL 24h): active dedup for in-flight calls
- **Warm** (PostgreSQL `idempotency_log` table): 30-day window for same-issue retries
- **Cold** (S3 + Glacier): 7-year archive for RBI audit

```sql
CREATE TABLE idempotency_log (
    idempotency_key VARCHAR(255) PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL,
    agent_id VARCHAR(255) NOT NULL,
    action_type VARCHAR(100) NOT NULL,
    resource_id VARCHAR(255) NOT NULL,
    amount DECIMAL(12,2),
    status ENUM('PENDING', 'SUCCESS', 'FAILED', 'ROLLED_BACK') NOT NULL,
    result_payload JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    INDEX idx_resource_action (resource_id, action_type, created_at),
    INDEX idx_session (session_id, created_at)
);
```

**Pattern (ACRFence-inspired):** After any LangGraph checkpoint-restore, a lightweight analyzer LLM (Haiku 4.x) compares the new tool call against the effect log to classify it as: (a) semantically equivalent → return cached response, (b) semantically different → block and fork, (c) credential reuse → alert and block. This prevents the "Semantic Rollback Attack" class (arXiv:2603.20625).

### 3.4 Dry-Run / Preview
**Technique:** Dual-mode tool registry. Every action tool accepts a `dry_run: bool` flag. When `dry_run=True`, the tool logs what it *would* do, returns a preview payload, and makes no writes.

```python
async def issue_refund(
    order_id: str,
    amount: Decimal,
    destination: str,
    dry_run: bool = True,  # Default to safe
    idempotency_key: str = None,
) -> RefundResult:
    if dry_run:
        return RefundResult(
            status="DRY_RUN",
            would_refund=amount,
            would_destination=destination,
            preview_eta="5-7 business days",
            warnings=await _check_warnings(order_id, amount),
        )
    # ... actual execution
```

**Shadow mode** at rollout: both old rule-based system and new AI agent receive identical inputs; AI outputs go to audit log only. Outputs compared against baseline. Agent promoted to live only when agreement rate >= 96% over 7-day shadow window.

**Confirmation turn in voice:** For voice channel, the TTS reads the dry-run preview to the customer and waits for explicit "haan" / "yes" / "theek hai" confirmation. STT must detect confirmation before `dry_run=False` call fires.

### 3.5 Value Threshold Decision
**Technique:** Layered threshold engine (pure rule-based, not LLM):

```python
THRESHOLDS = {
    "refund": {
        "auto": 2000,          # INR — fully autonomous
        "team_lead": 10000,    # INR — interrupt for TL approval
        "manager": 50000,      # INR — interrupt for Manager approval
        "compliance": None,    # INR — blocked, compliance review
    },
    "waiver": {
        "auto": 500,
        "team_lead": 2000,
        "manager": 10000,
        "compliance": None,
    },
    "cancel_policy": {
        "auto": 0,             # ALL cancellations = HITL per IRDAI
        "manager": None,       # Manager must approve
    },
}

CUMULATIVE_DAILY_LIMIT = {
    "refund": 5000,            # per customer per day
    "waiver": 2000,
}
```

**LangGraph interrupt:** If amount >= team_lead threshold, the node calls `interrupt(payload={"action": ..., "amount": ..., "reason": "above_auto_threshold"})`. Execution freezes. The checkpointed state is serialized to PostgreSQL. A push notification goes to the Team Lead queue (Telegram/WhatsApp Business/email). TL approves or rejects. Agent SDK resumes via `Command(resume={"approved": True})`.

### 3.6 Execution with Idempotency
**Technique:** Temporal.io durable execution workflow wraps every write-side action. The saga pattern ensures each step has a paired compensating transaction.

```python
@workflow.defn
class RefundWorkflow:
    @workflow.run
    async def run(self, input: RefundInput) -> RefundOutput:
        # Step 1: Reserve idempotency slot
        slot = await workflow.execute_activity(
            reserve_idempotency_slot,
            input.idempotency_key,
            schedule_to_close_timeout=timedelta(seconds=5),
        )
        if slot.already_exists:
            return slot.cached_result
        
        # Step 2: Execute with compensation registered
        try:
            result = await workflow.execute_activity(
                execute_refund_api_call,
                input,
                schedule_to_close_timeout=timedelta(seconds=30),
                retry_policy=RetryPolicy(
                    maximum_attempts=3,
                    non_retryable_error_types=["AuthorizationError", "DuplicateError"],
                ),
            )
        except Exception as e:
            # Compensate: notify failure, release slot, alert agent queue
            await workflow.execute_activity(
                compensate_failed_refund,
                CompensationInput(session_id=input.session_id, error=str(e)),
            )
            raise
        
        # Step 3: Write audit log entry
        await workflow.execute_activity(
            write_audit_entry,
            AuditEntry(
                action="refund",
                amount=input.amount,
                result=result,
                idempotency_key=input.idempotency_key,
            ),
        )
        
        return result
```

### 3.7 Post-Execution Verification
**Technique:** Verification step as a distinct LangGraph node. After action execution, an LLM (Haiku 4.x) reads the system response payload and performs three checks:
1. Status field is "SUCCESS" or equivalent (not just absence of error)
2. Reference ID is present and matches expected format
3. Amount in response matches amount in request

Only after all three pass does the agent generate the customer-facing confirmation message. The confirmation message is templated (not free-form generation) to avoid hallucinated reference numbers.

### 3.8 Rollback (Saga Compensation)
**Action reversibility taxonomy:**

| Action | Reversibility | Window | Compensation Action |
|--------|--------------|--------|---------------------|
| Refund initiated | Reversible | 2h | Call refund_cancel API |
| Refund settled | Irreversible | - | Manual back-office ticket |
| Address change | Reversible | 48h | Revert to prior address |
| Policy cancellation | Irreversible | - | Re-issuance process (new policy) |
| OTP fund transfer | Irreversible | - | Raise NPCI dispute ticket |
| Goodwill waiver | Reversible | 30 days | Re-charge via corrective invoice |
| Appointment booking | Reversible | Until T-24h | Cancel API call |

**Compensation mapping is registered at tool definition time**, not decided at runtime by the LLM. Every tool in the registry has a paired `compensate_*` tool.

### 3.9 Regulatory Disclosure Trigger
**Technique:** A rule-based pre-action hook (not LLM) checks a disclosure requirement matrix:

```python
DISCLOSURE_REQUIRED = {
    ("cancel", "insurance"): "IRDAI_FPC_V2",
    ("modify", "loan"): "RBI_FAIR_PRACTICES",
    ("initiate", "payment"): "RBI_PAYMENT_CONSENT",
    ("collect", "biometric"): "DPDP_BIOMETRIC_CONSENT",
    ("share", "pii"): "DPDP_DATA_SHARING_CONSENT",
}
```

If a disclosure is required, the agent MUST read the templated disclosure (in customer's preferred language — Hindi/English/regional) and receive `ack=True` from the customer before the action tool call is allowed to proceed. This is a hard blocking gate, not a soft warning.

### 3.10 Audit Ledger Entry
**Technique:** Hash-chained append-only audit log. Each entry:

```python
@dataclass
class AuditEntry:
    seq: int                          # Monotonically increasing
    session_id: str
    agent_id: str                     # Human agent ID or AI agent ID
    action_type: str
    resource_id: str
    amount: Optional[Decimal]
    status: str
    reference_id: str
    customer_confirmed: bool
    disclosure_given: Optional[str]   # Disclosure template ID
    timestamp_ist: datetime
    prev_hash: str                    # SHA-256 of previous entry
    leaf_hash: str                    # SHA-256 of this entry's canonical JSON
    chain_hash: str                   # SHA-256(prev_hash || leaf_hash)
    signature: str                    # PKCS#8 signing key (HSM-backed in prod)
```

Merkle root computed over session entries. Root anchored to external transparency log every 15 minutes (Certificate Transparency-style). Any tampering breaks the chain — detectable in O(log N) verification.

---

## 4. 2026 Tooling Stack

### Core Orchestration
- **LangGraph v0.4** (April 2026): native interrupt/checkpoint for HITL approval gates; PostgresSaver for persistent state across call drops
- **Temporal.io** (durable execution): wraps all write-side actions; saga/compensation pattern; built-in retry with backoff; workflow history for audit

### Idempotency
- **Redis 7.x** (hot tier, TTL-keyed dedup)
- **PostgreSQL 16** (warm tier, `idempotency_log` table with UPSERT-on-conflict)
- **AWS S3 + Glacier** (cold archive, 7-year retention for RBI)

### Authorization / Policy Engine
- **Open Policy Agent (OPA)** — declarative RBAC policies; evaluates authorization in <5ms; policy-as-code versioned in Git
- **Redis** — agent authority cache (tier → limits map)

### Audit Ledger
- **nono.sh audit architecture** pattern: SHA-256 hash-chained entries, DSSE/in-toto signed attestations, Merkle root anchoring
- **PostgreSQL** (primary ledger storage, append-only enforced via row-level security — UPDATE/DELETE blocked)
- **AWS QLDB or Hyperledger Besu** (alternative: blockchain-native immutability for regulated entities)
- **Sigstore/in-toto** (cryptographic attestation for agent binary identity binding)

### Dry-Run / Shadow Mode
- **Phantom tool registry pattern**: shadow agent receives identical tool calls; execution intercepted; responses mocked; outputs diff'd against production agent
- **Feature flags** (LaunchDarkly / Statsig): control dry_run=True/False per action type and per customer segment

### HITL Approval
- **WhatsApp Business API** / **Telegram Bot** (Team Lead approval notifications in India context — high adoption)
- **LangGraph `interrupt()` + Command(resume=)** (state-preserving pause mechanism)
- **Async approval TTL**: if no response in 120s, auto-escalate or auto-reject depending on action risk

### Safety / Defense
- **ACRFence pattern** (arXiv:2603.20625): MCP proxy at tool boundary; effect log; post-restore semantic classifier
- **OWASP LLM Top 10 (2025) Agentic edition**: Excessive Agency mitigation — every tool call validates scope before execution
- **Prompt injection defense**: all CRM data passed as structured JSON, never interpolated into system prompt

### Observability
- **Langfuse / Phoenix (Arize)**: trace every tool call with pre/post state, latency, idempotency cache hit/miss
- **Prometheus metrics**: `idempotency_cache_hits_total`, `action_rollback_total`, `hitl_escalation_total`, `audit_chain_integrity_checks_total`
- **Alerting**: cache hit rate < 80% → PagerDuty; rollback rate > 2% → immediate alert

### India-Specific Compliance
- **DPDP consent ledger** (per-purpose, write-once, cryptographic): per caller.digital.com guide
- **RBI Digital Lending Directions 2025**: all action logs stored in India-region only; S3 `ap-south-1`
- **IRDAI Cybersecurity Guidelines 2026** (April 6, 2026 update): encrypted at rest + in transit; 1-year log retention minimum

---

## 5. Benchmarks

| Metric | Value | Tag |
|--------|-------|-----|
| Idempotency key generation latency | < 2ms (SHA-256 hash) | [estimate] |
| Redis dedup lookup latency | 1-3ms (P99) | [sourced — Redis benchmark, AWS ElastiCache) |
| OPA authorization evaluation | < 5ms | [sourced — OPA docs, 2024] |
| LangGraph interrupt + checkpoint write | 15-40ms (PostgreSQL) | [estimate, based on LangGraph v0.4 changelog] |
| Temporal workflow step overhead | 10-30ms per activity | [sourced — Temporal.io docs] |
| Haiku 4.x dry-run preview generation | 200-400ms | [estimate, based on Claude Haiku latency profile] |
| Haiku 4.x post-restore semantic classifier (ACRFence pattern) | 150-300ms | [estimate] |
| Hash-chain audit entry write (PostgreSQL) | 3-8ms | [estimate] |
| Merkle root computation (100 entries) | < 1ms | [estimate — SHA-256 is CPU-bound, trivial at this scale] |
| Full action safety pipeline (pre-action → execute → audit) | 300-600ms added latency | [estimate] |
| Duplicate refund prevention rate (idempotency pattern) | > 99.99% | [sourced — Stripe idempotency design doc] |
| RBI audit log retrieval time (indexed PostgreSQL) | < 2s for any session | [sourced — CarmaOne.ai 99.97% compliance claim, cross-referenced] |
| Human agent duplicate execution error rate | 2-5% (without tooling) | [estimate, BPO industry baseline] |
| AI agent duplicate execution rate (with idempotency) | < 0.01% | [estimate] |
| Shadow mode agreement rate target before promotion | >= 96% | [estimate — industry standard for safe rollout] |

---

## 6. Failure Modes

### 6.1 Idempotency Key Collision
**What:** Two different actions hash to the same key (extremely rare with SHA-256 but possible with weak composite key design).  
**Why it breaks:** Second action gets cached response from first — wrong action appears to succeed.  
**Fix:** Add `action_version` to key material; log all collision events (`idempotency_key_collisions_total` metric); alert if > 0 per day.

### 6.2 Semantic Rollback Attack (ACRFence class)
**What:** After a LangGraph checkpoint-restore (e.g., network drop mid-call), the LLM regenerates a subtly different tool call (new UUID, different amount). The dedup check misses it because the key changed.  
**Why it breaks:** Duplicate payment / unauthorized action executes successfully.  
**Fix:** ACRFence-pattern proxy at tool boundary; effect log comparison on restore; block if semantically equivalent but key differs.

### 6.3 PENDING State Leak
**What:** Idempotency record created (PENDING), action fails, record never updated to FAILED. On retry, the check sees PENDING and waits forever (or until TTL).  
**Why it breaks:** Legitimate retry blocked; customer action never completes.  
**Fix:** PENDING records older than 60s auto-expire to FAILED via a sweeper job; always update status in finally block.

### 6.4 Dry-Run / Live Mode Confusion
**What:** Dry-run branch executes correctly but a bug in flag propagation causes the real action to also fire (double execution).  
**Why it breaks:** Both preview AND actual write happen.  
**Fix:** dry_run flag propagated through every layer; integration tests enforce: dry_run=True calls return DRY_RUN status, never SUCCESS; Prometheus alert if DRY_RUN rate drops to 0 for an action type.

### 6.5 Threshold Bypass via LLM Reasoning
**What:** Adversarial user prompt convinces LLM to interpret the threshold rule differently ("this is an emergency refund, it's exempt").  
**Why it breaks:** Agent issues a refund above its authority limit without escalation.  
**Fix:** Authorization gate is NEVER LLM-reasoned — it's a deterministic rule engine (OPA). LLM receives only the binary output of OPA evaluation, never sees the threshold values directly.

### 6.6 Audit Log Tampering
**What:** Attacker with database access modifies an audit entry to remove evidence of a refund.  
**Why it breaks:** Compliance violation; regulatory exposure.  
**Fix:** PostgreSQL row-level security blocks UPDATE/DELETE. Hash chain immediately detects modification (chain_hash breaks). Merkle root anchored externally every 15 minutes means any deletion is detectable. HSM-backed signing key means forged entries require physical key compromise.

### 6.7 HITL TTL Expiry Race Condition
**What:** Team Lead approval notification sent but TL doesn't respond within TTL. System auto-escalates. Meanwhile, TL approves the original request. Both paths execute.  
**Why it breaks:** Double-approval, potentially double action execution.  
**Fix:** Approval tokens are single-use; once consumed, second use returns 409 Conflict. LangGraph `thread_id` ensures only one resume per checkpoint. TTL expiry explicitly CANCELS the original approval slot before creating the escalated one.

### 6.8 Compensation Chain Failure
**What:** Saga step 3 fails, compensation step (reverse of step 1 and 2) also fails. System is left in partial state.  
**Why it breaks:** Inconsistent data; customer may or may not receive refund; CRM shows wrong status.  
**Fix:** Compensation steps are idempotent (can be retried safely); failed compensations create a manual back-office ticket (dead letter queue); weekly reconciliation job compares CRM state vs audit log state and flags discrepancies.

### 6.9 Cross-Channel Cumulative Limit Bypass
**What:** Customer calls twice on different channels (voice + chat) in the same hour; each channel issues a ₹2,000 refund autonomously. Neither exceeds the ₹2,000 auto-threshold individually. Customer gets ₹4,000 total.  
**Why it breaks:** Cumulative daily limit violated without triggering escalation.  
**Fix:** Cumulative limit check queries the idempotency_log across ALL channels for the customer ID within the rolling window, not just the current session.

### 6.10 Post-Confirmation Customer Denial
**What:** Customer confirms "haan" to the refund preview. Agent executes. Customer then denies having confirmed ("maine nahi bola").  
**Why it breaks:** Dispute resolution requires proof of consent.  
**Fix:** Audio segment of the confirmation is timestamped and linked to the audit log entry. TTS output (what agent said) and STT transcription (what customer said) both stored as evidence artifacts. Reference: RBI FPC 100% call recording mandate.

---

## 7. Gap to Full Adaptation

### Gap 1: Real-Time Semantic Ambiguity Under Emotional Stress
**Human ability:** A skilled agent recognizes when a customer says "cancel everything" in anger but means "fix this specific issue." They read tone, pause, de-escalate before taking drastic action.  
**Agent gap:** Current STT + intent models classify "cancel everything" as cancellation action at ~87% rate. They don't reliably detect the frustration signal that means the customer wants resolution, not cancellation.  
**Path to close:** Multimodal emotion signal (speech prosody + semantic intent) feeding a joint confidence model. If emotion_confidence(frustrated) > 0.7 AND intent_confidence(cancel) < 0.95, route to clarification turn before action. Requires fine-tuning on India-language emotion datasets (IISc Indic Speech Corpus, AI4Bharat EmoSpeech). ETA: 12 months.

### Gap 2: Policy Exception Judgment
**Human ability:** Senior agent can judge "this customer has been with us 8 years, the refund window technically expired but I'll make an exception" — context-sensitive policy flexibility within unstated norms.  
**Agent gap:** Agents apply policy rules deterministically. They cannot make discretionary exceptions that are technically outside policy but culturally expected in Indian customer service.  
**Path to close:** Fine-tune a policy exception model on historical approved exceptions (requires 50K+ labeled examples from BPO partner). Confidence-gated: exception only offered if model confidence > 0.90. All exceptions above threshold flagged for human review. ETA: 18 months + BPO data partnership.

### Gap 3: Detecting Collusion / Internal Fraud
**Human ability:** Experienced QA supervisor notices if the same agent-customer pair keeps doing large refunds, suggesting agent-abetted fraud.  
**Agent gap:** Current agents optimize per-call; they don't see cross-call patterns across agent-customer pairs.  
**Path to close:** Cross-session analytics layer (separate from per-call agent) that runs daily batch analysis of refund patterns by agent-customer pair, flags anomalies to compliance. This is not an agent capability gap — it's a separate fraud detection system (Isolation Forest / GBM on behavioral features). Can be built in 3-4 months separately.

### Gap 4: Regulatory Change Awareness
**Human ability:** A compliance-trained human agent knows when a new RBI circular just changed the calling window or a new DPDP rule just took effect, and adjusts behavior within days.  
**Agent gap:** Agent runs on policy rules that were correct at deployment time. New regulations require human-updated policy files before agents adapt.  
**Path to close:** Regulatory change monitoring pipeline: scrape RBI/IRDAI/MeitY circulars daily → parse with Claude Sonnet → generate policy diff → human compliance officer reviews and approves → auto-deploys to OPA policy store. Can be built in 2-3 months.

---

## 8. HITL Triggers

| Scenario | Action | Why Human Required |
|----------|--------|-------------------|
| Refund > ₹2,000 (standard agent limit) | Interrupt → Team Lead approval | Authority limit; RBI accountability |
| Refund > ₹10,000 (TL limit) | Interrupt → Manager approval | High-value reversibility |
| Any policy cancellation (insurance/loan) | Interrupt → Manager approval | IRDAI FPC mandatory; irreversible |
| Cumulative daily refunds > ₹5,000 per customer | Interrupt → Manager approval | Fraud signal |
| Agent confidence on intent < 0.90 | Clarification turn OR escalation | Ambiguity in irreversible action |
| Compensation chain failed (saga compensation failed) | Dead letter queue → back office | System cannot self-heal |
| Audit chain integrity check fails | Immediate escalation → Compliance | Potential tampering |
| Post-restore semantic classifier returns "semantically different" | Block + fork → human review | ACRFence class attack possible |
| Customer explicitly requests human agent | Immediate warm handoff | IRDAI/RBI: AI cannot be sole option |
| Biometric or Aadhaar-authenticated action | DPDP consent gate | Regulatory hard requirement |

---

## 9. Automation Readiness

**Score: 7 / 10**

**Why 7 and not 8+:**
- The idempotency, dry-run, hash-chain audit, and value-threshold layers are fully automatable with 2026 SOTA — these are solved engineering problems.
- The semantic ambiguity gap (angry "cancel everything" vs. genuine cancellation request) is real and causes action-safety failures in production at measurable rates.
- Policy exception judgment (Gap 2) is a genuine human-superior domain that cannot be safely delegated yet.
- The regulatory change lag (Gap 4) creates windows where the agent operates on stale policy.
- HITL gates are mandatory per RBI/IRDAI for high-value actions — so "full replacement" is legally blocked for that subset even if the AI were technically capable.

**Why not lower than 7:**
- For the majority of BPO action volume (refunds < ₹2,000, address changes, appointment rescheduling, status queries), the action safety layer is fully automatable today with high confidence.
- The infrastructure (idempotency + audit + dry-run + saga compensation) is production-proven in analogous domains (Stripe, Temporal, LangGraph v0.4).

---

## 10. Build Specification

### What to Implement

**Module 1: Idempotency Middleware**
- `IdempotencyKey` generator (SHA-256, composite: session_id + action_type + resource_id + amount + bucket)
- Redis hot-tier dedup (TTL = 24h)
- PostgreSQL warm-tier `idempotency_log` table (30-day queryable)
- S3 cold archive connector (7-year, RBI compliance)
- `IdempotentToolWrapper` decorator for LangChain/LangGraph tools

**Module 2: Authorization Gate**
- OPA policy store (agent_tier × action_type × amount → authorized/escalate/block)
- Redis authority cache
- `AuthorizationDecision` structured response type
- Cumulative daily limit checker (cross-channel, customer-level)

**Module 3: Dry-Run / Phantom Registry**
- `dry_run: bool` flag on every write tool
- Shadow mode router (LaunchDarkly feature flag)
- Preview response schema (amount, destination, ETA, warnings)
- TTS confirmation turn integration (Hindi/English/Hinglish)

**Module 4: Value Threshold Engine**
- Threshold config (YAML, OPA-compatible)
- LangGraph interrupt node for HITL approval
- WhatsApp Business API notification for TL/Manager approval
- Approval token system (single-use, TTL=120s)
- `Command(resume=)` handler

**Module 5: Saga Compensation Registry**
- Forward/backward action pair registry (YAML config)
- `Temporal.io` workflow per action type
- Compensating transaction implementations for each action
- Dead letter queue + back-office ticket creation on comp failure

**Module 6: Immutable Audit Ledger**
- Hash-chained `AuditEntry` schema (PostgreSQL append-only)
- Row-level security (no UPDATE/DELETE)
- Merkle root computation + external anchoring (every 15 min)
- HSM-backed signing (AWS KMS or on-prem HSM for IRDAI compliance)
- Verification CLI: `verify_audit_chain --session-id XYZ`

**Module 7: ACRFence Proxy**
- MCP proxy layer at tool boundary
- Effect log (what tool calls already executed in this session)
- Post-restore semantic classifier (Haiku 4.x, < 300ms)
- Block / replay / fork routing

**Module 8: Regulatory Disclosure Gate**
- Disclosure requirement matrix (YAML)
- Pre-action hook (hard blocking)
- Disclosure template library (Hindi/English/11 regional languages)
- Disclosure acknowledgment capture (STT-based "haan" / "yes" detection)

### Data Needed

- **BPO authority limit SOPs** (agent tier → action type → INR limit) — partner data, currently undocumented
- **Historical refund approval patterns** (for exception model training, Gap 2) — 50K+ labeled examples
- **RBI/IRDAI compliance matrix** mapping action types to disclosure requirements — legal team input
- **India regional language confirmation signals** for STT ("haan", "theek hai", "ha", regional equivalents) — labeling + ASR fine-tune
- **Existing CRM action logs** (for idempotency key design validation — what fields reliably identify "same action"?)

### Eval Metric Gates ("Good Enough to Ship")

| Gate | Metric | Threshold |
|------|--------|-----------|
| Idempotency | Duplicate execution rate | < 0.01% over 10K action sample |
| Authorization | False-positive escalation rate | < 3% (don't over-escalate low-risk actions) |
| Authorization | False-negative bypass rate | 0.0% (never allow unauthorized action) |
| Dry-run | Customer confirmation accuracy | > 98% (correct amount/destination in preview) |
| Dry-run | Confirmation detection (STT) | > 96% (Hindi/Hinglish "haan" variants) |
| Threshold | HITL trigger accuracy | 100% (no high-value action bypasses escalation) |
| Audit | Chain integrity | 100% (zero broken chains in 30-day test) |
| Audit | Retrieval latency | < 2s for any session (RBI inspection SLA) |
| Compensation | Saga success rate | > 99.5% (including compensation path) |
| Shadow mode | Agreement rate vs baseline | >= 96% before promotion to live |

---

## 11. India Specifics

### Language / Hinglish

- **Confirmation signals** vary significantly: "haan", "ha", "theek hai", "bilkul", "done karo", "karo bhai", "okay kar do" — all mean "proceed". STT + NLU must handle all variants including code-mixed forms. "Nahi" / "ruko" / "hold on" / "ek second" must PAUSE the action, not proceed.
- **Negation in Hinglish is complex**: "cancel mat karo" vs "cancel karo mat" — word order varies. Rule: any detected negation = abort + reconfirm.
- **Amount pronunciation** in Hindi: ₹1,450 is read as "ek hazaar chaar sau pachaas" in TTS; customer may repeat it back as "haan wahi amount" — confirmation detection must accept anaphoric reference, not exact echo.

### Regulatory Stack (as of 2026-06-24)

**RBI Digital Lending Directions 2025 (fully enforceable April 2026):**
- Every AI action on a loan account must have explicit consent logged with audit trail
- Disclosure: lender name + loan reference + nature of action at call start
- Grievance redressal mechanism must be mentioned before any adverse action
- Data stored exclusively in India (`ap-south-1` for AWS; `asia-south1` for GCP)
- 24-hour data repatriation if processed overseas

**IRDAI Cybersecurity Guidelines (updated April 6, 2026):**
- Applies to all insurance entities + intermediaries
- Encrypted at rest + in transit
- 1-year minimum audit log retention
- AI cannot independently issue policy modifications — human review mandated
- Incident reporting within 6 hours of detection

**DPDP Act 2023 (Rules notified Nov 2025; substantive compliance enforceable May 2027 but early-mover advantage):**
- Per-purpose consent capture in 12+ Indian languages
- Consent ledger must be immutable + cryptographically tamper-evident
- Configurable retention TTLs per data category
- Automated redaction of Aadhaar/PAN/card number/OTP from transcripts before storage
- Data principal rights: access, correction, deletion on demand
- Deletion certificates covering sub-processors
- Breach notification to Data Protection Board within 72 hours

**TRAI DLT (Distributed Ledger Technology) Framework:**
- All commercial communications require registered sender headers
- DND scrubbing mandatory before any outbound contact
- AI-initiated calls must be labeled as AI (not presented as human)
- Contact frequency limits tracked across all channels simultaneously

### BPO-Specific India Context

- **Authority limits** in Indian mid-market BPOs are typically undocumented — they exist in training culture, not written SOP. Building the authorization engine requires a discovery exercise with BPO team leads to extract and formalize these rules.
- **Team Lead availability**: Indian BPOs operate in shifts; a 2am IST call where TL is unavailable creates HITL approval timeout scenarios that must be handled gracefully (auto-queue for morning resolution with customer callback promise).
- **UPI mandates**: For refund-to-UPI, RBI spending mandate cap is ₹10,000 per transaction via UPI Autopay; AI-initiated UPI refunds above this cap require additional customer-initiated authentication step (Proceed to Pay pattern per RBI).
- **WhatsApp Business API** is the most practical HITL notification channel for Indian TLs (>90% WhatsApp penetration); better than email or Slack for real-time approval in BPO floor environments.
- **Aadhaar-authenticated sessions**: Any action that relies on Aadhaar OTP for authentication creates a DPDP biometric consent obligation; the audit log must record that UIDAI consent was obtained and not just the fact of authentication.

---

## 12. References

- [Idempotent AI Agents: Retry-Safe Patterns for Production (BuildMVPFast, 2026)](https://www.buildmvpfast.com/blog/idempotent-ai-agent-retry-safe-patterns-production-workflow-2026)
- [ACRFence: Preventing Semantic Rollback Attacks in Agent Checkpoint-Restore (arXiv:2603.20625)](https://arxiv.org/abs/2603.20625)
- [RAILS: Verification-Native Clearing For Agentic Commerce (arXiv:2606.08790)](https://arxiv.org/abs/2606.08790)
- [LangGraph v0.4: HITL Checkpoints and State Persistence](https://aitechconnect.in/news/langgraph-v04-hitl-checkpoints-state-persistence)
- [Building Idempotent Tools for Long-Running Agents (Padiso, 2026)](https://www.padiso.co/blog/building-idempotent-tools-for-long-running-agents/)
- [What Really Happened In There? A Tamper-Evident Audit Trail for AI Agents (nono.sh)](https://nono.sh/blog/secure-agent-audit)
- [RBI Compliant AI Collections: The Complete Guide for NBFCs & Banks in India (CarmaOne, 2026)](https://www.carmaone.ai/blog/rbi-compliant-ai-collections-guide-india-2026)
- [DPDP vs TRAI Consent for Voice Recordings India 2026 (caller.digital)](https://www.caller.digital/blog/dpdp-vs-trai-consent-voice-recordings-audit-trail-india-2026)
- [AI Calling Compliance in India 2026: DPDP, TRAI DLT, and RBI Guide (AutoInterviewAI)](https://www.autointerviewai.com/blog/ai-calling-india-dpdp-trai-dlt-compliance-complete-guide-2026)
- [How to Classify AI Agent Actions by Risk: A Four-Tier Framework (MindStudio)](https://www.mindstudio.ai/blog/classify-ai-agent-actions-by-risk)
- [Beyond Try/Except: Implementing the Saga Pattern in 2026 AI Agents (Medium, Rahul Ponnusamy)](https://medium.com/@rahulponnusamy/beyond-try-except-implementing-the-saga-pattern-in-2026-ai-agents-92dcb7c0bf48)
- [Human-in-the-Loop Workflows with LangGraph: Interrupts, Approvals, and Async Execution](https://www.abstractalgorithms.dev/langgraph-human-in-the-loop)
- [OpenAI Guardrails and Human Review (OpenAI Developer Docs)](https://developers.openai.com/api/docs/guides/agents/guardrails-approvals)
- [Temporal and the 2026 Shift to Durable Agentic Workflows (Olmec Dynamics)](https://olmecdynamics.com/news/temporal-durable-execution-agentic-workflows-2026)
- [IRDAI Updates Cybersecurity Rules, Mandates DPDP Compliance (MediaNama, April 2026)](https://www.medianama.com/2026/04/223-lowdown-insurers-comply-dpdp-irdai-updates-cyber-security-guidelines/)
- [RBI's AI Risk Mandate: What Every Indian Bank Must Know Before June 30 (ValueMentor)](https://valuementor.com/blogs/rbis-ai-risk-mandate-what-every-indian-bank-must-know-before-june-30)
- [Blockchain for AI Compliance With Immutable Logs (Blockchain Council)](https://www.blockchain-council.org/blockchain/blockchain-for-ai-compliance-gdpr-hipaa-eu-ai-act-immutable-logs/)
- [Trustworthy AI Agents: Verifiable Audit Logs (Sakura Sky)](https://www.sakurasky.com/blog/missing-primitives-for-trustworthy-ai-part-5/)
- [Creating Characteristically Auditable Agentic AI Systems (ACM FAIR 2025)](https://dl.acm.org/doi/10.1145/3759355.3759356)
- [RBI Digital Lending Directions 2025: Overview (Synergia Legal)](https://synergialegal.com/an-overview-of-the-rbis-digital-lending-direction-2025/)

---

*End of B07 dossier. Next in series: B08 (to be defined). Preceding: B06 (RAG, citation, guardrails).*
