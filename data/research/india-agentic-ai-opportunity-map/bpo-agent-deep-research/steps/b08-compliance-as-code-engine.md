# B08 — Compliance-as-Code Engine
## Machine-Enforced RBI / IRDAI / DPDP Rules + Consent Ledger

> **Context:** India-market, multilingual (Hindi + regional + Hinglish), RBI/IRDAI/DPDP-compliant, action-taking voice+chat contact-center agent for mid-market BPOs.
> **Research date:** 2026-06-24
> **Automation readiness:** 8 / 10

---

## 1. What Is This Step

In a live BPO contact-center conversation, a human compliance officer and the floor agent together enforce a dense, overlapping set of rules BEFORE, DURING, and AFTER every call. The rules come from at least five distinct regulators simultaneously:

| Regulator | Core contact-center obligations |
|---|---|
| **TRAI / TCCCPR 2018 + Feb 2025 amend.** | DND scrub, DLT header/template registration, 10 AM–7 PM calling window (promo), 140-series for promo / 1600-series for BFSI |
| **RBI Fair Practices Code** | 8 AM–7 PM calling window (collections), daily contact-frequency caps, mandatory disclosures (lender ID, grievance redressal), no abusive language, 100% call recording, purpose-specific consent per Digital Lending Directions 2025 |
| **IRDAI** | AI self-identification, free-look period disclosure, prohibition on mis-selling, policyholder right to human escalation at any moment |
| **DPDP Act 2023 + Rules 2025 (notified Nov 2025, operative May 2027)** | Free/specific/informed/revocable consent before processing, purpose limitation, data minimisation, 72-hour breach notification, data principal rights (access / correction / erasure), 7-year consent record retention, registered Consent Manager integration (operative Nov 2026) |
| **RBI IT Outsourcing Master Direction 2023** | Data localisation (India only), cyber-incident reporting within 6 hours, board-approved outsourcing policy |

A human agent doing this step well is simultaneously:
- A legal analyst (knows which rule applies to this call type)
- A real-time monitor (detects when a conversation drifts toward a violation)
- A consent steward (captures, records, and acts on consent signals)
- An audit clerk (generates a trail the regulator can inspect)

---

## 2. Human Micro-Steps (Atomic Decomposition)

These are the smallest cognitive + mechanical + emotional sub-skills a skilled human compliance agent exercises on EVERY interaction:

### Pre-Call Phase

1. **Contact-list eligibility check** — Before dialing, verify this number is not DND-registered (scrub against NCPR/TRAI). TRAI DND registrations update daily; stale scrubs are a violation.
2. **Consent pre-flight** — Confirm that a valid, purpose-specific, logged consent exists for THIS call type (collections vs. cross-sell vs. policy renewal). If not, do not call.
3. **Calling-window gate** — Check current time against the allowed window: 10 AM–7 PM for TRAI promo, 8 AM–7 PM for RBI collections. Reject if outside.
4. **Frequency throttle check** — Look up how many times this borrower/customer has been contacted today, this week, this cooling-off period. Block if limit hit.
5. **Number-series routing** — Assign the correct outbound number series: 140 (promotional), 1600 (BFSI regulated), or normal CLI (transactional within 30 min of customer action per Feb 2025 TRAI amendment).
6. **DLT template selection** — Match the call's content type to the exact pre-registered DLT template. Unregistered content cannot be delivered.
7. **Sector-specific flag** — Tag call as RBI / IRDAI / neutral so mid-call rules load correctly.

### Call Opening Phase

8. **Mandatory AI/bot disclosure** — If AI-driven call: state at the very start that this is an automated system (per DPDP Rules + IT Rules 2026 amendment). Human agents note this too in insurance calls.
9. **Identity + lender / company disclosure** — State lender name and loan reference number (RBI FPC) or policy number (IRDAI) within the first 30 seconds.
10. **Recording consent capture** — Inform customer that call is being recorded; capture affirmative or note the legal basis for recording without affirmative (transactional basis).
11. **Opt-out offer** — Offer DNC/opt-out mechanism at call start (TRAI + DPDP).
12. **Purpose statement** — State the purpose of the call explicitly. DPDP purpose-limitation principle requires this.

### Mid-Call Phase

13. **Banned-phrase monitoring (self-monitoring)** — Human agent continuously self-monitors against prohibited phrases: threats, mention of family/employer, false claims of legal action (RBI FPC). Supervisor also listens on sampled calls.
14. **Script adherence check** — Ensure conversation stays within registered DLT template structure. Material deviations void the compliance cover.
15. **Data minimisation discipline** — Do not ask for or record data fields beyond what the purpose requires. Collecting contact lists, gallery access, etc. is explicitly prohibited under RBI digital lending.
16. **Consent change detection** — If customer says "stop calling me" / "remove my number" / "I withdraw consent" — human must recognise this in any language/dialect including Hinglish/regional, stop the call, and trigger opt-out workflow.
17. **Human-escalation provision** — In insurance calls, if customer asks for a human, transfer immediately. IRDAI mandates this.
18. **Free-look period + grievance disclosure** — In insurance, proactively state free-look period. In all RBI-regulated calls, state grievance redressal mechanism.
19. **Sensitive-topic detection** — If conversation enters prohibited territory (suicide, domestic violence, health data collection not authorised), escalate or terminate.

### Call Closing Phase

20. **Commitment logging** — Manually note any commitment made (payment date, call-back time, claim reference number). These become audit artifacts.
21. **Consent confirmation record** — Write down or click-confirm that consent was active, what it covered, and that it was not withdrawn.
22. **Call recording upload** — Ensure recording is saved to compliant storage (India-resident, per RBI data localisation).
23. **Disposition coding** — Tag call outcome in CRM with compliance-relevant codes: contacted / no-response / opt-out / grievance-raised.

### Post-Call / Batch Phase

24. **Retention timer set** — Record how long this interaction data must be held (7 years for DPDP consent records; sector-specific for call recordings; 24-hour rule for data externally processed then returned, per RBI digital lending).
25. **Breach watch** — If any data was exposed or accessed incorrectly, note for 72-hour RBI/DPDP breach reporting window.
26. **Audit log assembly** — Compile the full interaction record: timestamp, agent ID, customer ID, consent status, disclosures made, commitments, recording URL, disposition. This is the raw material for regulatory inspections.
27. **DND update propagation** — If customer opted out during call, propagate suppression across all channels (SMS, WhatsApp, email, future calls) within the platform.
28. **Frequency counter update** — Increment the borrower/customer contact counter for today, week, cooling-off period.

---

## 3. Agent Approach — 2026 AI Techniques Per Sub-Step

### Architecture Overview

```
[Pre-flight Policy Engine] → [Call Orchestrator + Real-time Guardrail Layer]
         ↓                              ↓
[Consent Ledger API]          [STT + Compliance NER + Intent Classifier]
         ↓                              ↓
[Violation Event Bus]         [Post-call Audit Assembler]
         ↓
[Regulatory Reporting API]
```

### Layer 1: Pre-Call Policy Engine (Compliance-as-Code)

**Technique:** Open Policy Agent (OPA) with Rego policies encoding each regulator's rules as machine-checkable predicates.

```rego
# Example: RBI collections calling window
package rbi.fpc

default allow_call = false

allow_call {
    call_type == "collections"
    current_hour_ist >= 8
    current_hour_ist < 19
    not dnd_registered
    daily_contact_count < max_daily_contacts
    not in_cooling_off_period
}
```

Each pre-flight step (1–7 above) maps to an OPA policy evaluation. The call is only initiated if `allow_call = true` on ALL active policy packages (TRAI, RBI, IRDAI, DPDP). This is a synchronous sub-50ms evaluation before any telephony action.

**DND scrub:** TRAI NCPR API → daily delta sync into Redis sorted set → O(1) lookup per number. Refresh via cron every 24h + on-demand before campaign launch.

**Consent pre-flight:** Consent Ledger read API (see Layer 3). Query by `(customer_id, purpose_code)` → returns `{valid: bool, expires_at, purpose, given_at, channel}`.

**Number-series routing:** Rule table keyed on `(sector, call_type, is_within_30min_of_action)` → deterministic. No LLM involved.

### Layer 2: Real-Time Conversation Guardrails

**Technique:** Dual-layer guard during live call.

**Layer 2a — Deterministic guardrails (OPA / rule engine):**
- Calling-window hard stop: if call is still active past the window boundary, trigger graceful termination script.
- Frequency counter: after N seconds, check if this is call #N+1 beyond daily limit (edge case: call started within window, running long).
- Opt-out phrase detection: STT stream → keyword regex + phoneme matcher for opt-out signals in Hindi/Hinglish ("band karo", "mat karo", "remove karo", "DND pe daalo").

**Layer 2b — LLM guardrails (NeMo Guardrails / custom):**
- **Input rail:** Classify every incoming utterance for: (a) consent withdrawal signal, (b) grievance, (c) request for human, (d) prohibited topic entry.
- **Output rail:** Before the AI speaks, check response against: banned-phrase list (threats, abusive language, false legal claims), IRDAI disclosure requirements (has free-look been mentioned this call?), RBI FPC disclosure checklist (has lender ID + grievance mechanism been stated?).
- **Dialog rail:** Track conversation state machine — `[OPENED → DISCLOSED → CONSENTED → ACTIVE → CLOSING → LOGGED]`. State transitions gated by compliance checkpoints.

**STT for real-time compliance:** Sarvam Saaras v3 (19.31% WER on IndicVoices, best-in-class for Hindi + 9 other Indian languages, code-mixing / Hinglish support, speaker diarization). Streaming transcription with <300ms chunk latency over WebSocket. Deepgram Nova 3 as fallback for low-latency English segments.

**Compliance NER on transcript:** Fine-tuned IndicBERT / MuRIL model classifying tokens into: `[OPT_OUT_SIGNAL, GRIEVANCE, REQUEST_HUMAN, THREAT_PHRASE, SENSITIVE_DATA, COMMITMENT]`. Runs on each 3-second transcript chunk. P95 latency target: 150ms.

### Layer 3: Consent Ledger

**Design:** Append-only event store. No UPDATE / DELETE on consent events. Every consent action is an immutable record.

```json
{
  "event_id": "uuid-v7",
  "customer_id": "CUST-123",
  "timestamp_utc": "2026-06-24T09:15:00Z",
  "timestamp_ist": "2026-06-24T14:45:00+05:30",
  "event_type": "CONSENT_GRANTED",
  "purpose_code": "COLLECTIONS_CALL",
  "channel": "IVR_OTP",
  "regulator_scope": ["RBI_FPC", "DPDP"],
  "call_id": "CALL-456",
  "agent_id": "AI-AGENT-01",
  "payload_hash": "sha256:...",
  "merkle_prev": "sha256:...",
  "signed_by": "rsa2048:consent-ledger-key-v2"
}
```

**Implementation options:**

| Option | Stack | When to use |
|---|---|---|
| A — PostgreSQL append-only | pg with row-level `INSERT`-only policy + TimescaleDB for time-series queries. SHA-256 chain-linking in app layer. | Simplest, sufficient for <10M events/day. DPDP-compliant today. |
| B — Apache Kafka + Kafka Streams | Events in Kafka topic (immutable by design). Kafka Streams materialised view for current consent state. | High-throughput BPOs (>10M calls/day), event-replay for audit. |
| C — Hyperledger Fabric (permissioned blockchain) | Immutable ledger, DPB-auditable. | Only if regulator mandates blockchain-level non-repudiation. Overhead not justified by current DPDP rules. |

**Recommended: Option A for mid-market BPO, Option B at scale.**

DPDP Consent Manager registration (operative Nov 2026): the ledger must expose a standard API compatible with registered Consent Manager intermediaries (Leegality/Consently/consent.in). This means: `GET /consent/{customer_id}/{purpose}`, `POST /consent/withdraw`, `GET /consent/history/{customer_id}`.

**Right to erasure vs. immutability paradox:** DPDP grants right to erasure. Consent events must be retained 7 years (per rules). Resolution: mark record as `{erased: true}` and null PII fields while retaining the structural chain (event_id, timestamp, hashes). The consent FACT persists; the personal DATA is erased. Legally defensible interpretation per DPO-India guidance.

### Layer 4: Post-Call Audit Assembler

**Technique:** Structured extraction pipeline.

1. Full call transcript (Sarvam STT, diarized, timestamped per utterance).
2. Compliance checkpoint log (which disclosures were made + at what timestamp).
3. Consent ledger events from this call (granted / unchanged / withdrawn).
4. Commitments extracted: Claude Haiku / GPT-4o-mini with tool-use schema to extract `{commitment_type, amount, date, call_timestamp}`.
5. Violation flags: list of any guardrail events triggered during call.
6. Disposition code from CRM.
7. Assembly into `InteractionAuditRecord` (Pydantic schema, validated) → write to audit store.

Audit records encrypted at rest (AES-256), stored in India-resident data centre (AWS ap-south-1 / Azure India Central), retention-tagged per regulator.

**Automated regulatory report generation:** Monthly aggregation (Polars + DuckDB) → `ComplianceMetricReport` → structured JSON → API endpoint for RBI / IRDAI submission tooling.

---

## 4. Concrete 2026 Stack

| Component | Tool / Vendor | Notes |
|---|---|---|
| **Policy engine** | OPA (open-source, CNCF) + Rego | Apple hired OPA maintainers Aug 2025; community still active. Cedar (AWS) as alternative — more readable, strongly typed. |
| **DND scrub** | TRAI NCPR API + Redis | Daily delta sync. In-house or via Exotel's ULVNO infrastructure (DoT-compliant by default). |
| **STT (real-time, Indian languages)** | Sarvam Saaras v3 | 19.31% WER on IndicVoices, Hinglish/code-mix support, speaker diarization. Streaming WebSocket API. |
| **STT (English fallback / low latency)** | Deepgram Nova 3 | <300ms streaming latency; fails on Hindi — use only for English segments. |
| **Real-time compliance NER** | Fine-tuned MuRIL / IndicBERT | Classify: opt-out signals, threats, grievances, sensitive data. Run on 3s transcript chunks. |
| **LLM guardrails** | NVIDIA NeMo Guardrails v0.11+ | Input/output/dialog rails. Colang config files per regulator. OR custom LangGraph state machine (more control). |
| **Conversation state machine** | LangGraph | Compliance checkpoint nodes. Explicit state: `PRE_CALL → OPENING → ACTIVE → CLOSING → POST_CALL`. |
| **Consent Ledger DB** | PostgreSQL 16 + TimescaleDB / Apache Kafka | Append-only schema. SHA-256 Merkle chain. RSA-2048 signing. |
| **Consent Manager API** | Leegality Consent.in / Consently (Bhashini-powered, 22 Indian languages) | DPB-registered CM integration point. REST + webhooks. |
| **PII redaction** | Microsoft Presidio (open-source) | Strip Aadhaar, PAN, phone, account numbers from logs/transcripts before non-essential storage. |
| **Audit store** | PostgreSQL + S3-compatible (India-resident) | AES-256 encryption at rest, 7-year retention for consent, sector-specific for call recordings. |
| **Observability** | Langfuse / Phoenix Arize | Trace every LLM call: prompt, output, tokens, latency, guardrail decisions, cost. |
| **Compliance reporting** | DuckDB + Polars + FastAPI | Monthly metric aggregation and regulatory report generation. |
| **Telephony + number series routing** | Exotel (ULVNO, DoT-compliant) / Rootle | 140-series promo, 1600-series BFSI, automatic routing enforcement. |
| **QA / 100% call monitoring** | Convin.ai (Bengaluru) / Observe.AI | Post-call 100% audit, real-time violation flagging, custom compliance scorecards. |

---

## 5. Benchmarks

| Metric | Human | AI (2026) | Source |
|---|---|---|---|
| Calling-hour violations | 3–7% | 0% (structurally impossible) | CarmaOne [sourced] |
| Language/tone violations | 8–12% | 0% (banned-phrase guard) | CarmaOne [sourced] |
| Frequency-limit breaches | 15–20% | 0% (OPA hard gate) | CarmaOne [sourced] |
| Call recording coverage | 70–85% | 100% | CarmaOne [sourced] |
| Mandatory disclosure completion | 60–75% | 100% | CarmaOne [sourced] |
| Overall FPC compliance rate | 87–92% | 99.97% | CarmaOne [sourced] |
| Real-time violation detection rate | ~30% (sampled QA) | >70% (live), 100% post-call | Convin [sourced] |
| STT WER Hindi (Sarvam Saaras v3) | N/A | 19.31% on IndicVoices | Sarvam AI [sourced] |
| OPA policy eval latency | N/A | <50ms p99 | OPA docs [estimate] |
| Pre-call policy check latency (all 7 checks) | 30–90s (human lookup) | <200ms (automated) | [estimate] |
| Consent ledger write latency (PostgreSQL) | N/A | <10ms p99 | [estimate] |
| Post-call audit assembly (full record) | 5–15 min (human) | <30s (automated pipeline) | [estimate] |
| TRAI enforcement action threshold | — | 47,000+ numbers disconnected Q1 2026 by TRAI's own AI | AutoInterviewAI [sourced] |
| RBI FPC penalty per violation | — | ₹5L–₹2Cr | CarmaOne [sourced] |
| DPDP max penalty (consent breach) | — | ₹250 crore | DPDP Act [sourced] |

---

## 6. Failure Modes

1. **Hinglish / code-mixed opt-out miss:** Agent says "haan, mat karo ab" (colloquial for "stop now"). STT may transcribe correctly but NER model trained on clean Hindi fails to classify as opt-out. Customer continues receiving calls → DPDP violation + customer complaint.

2. **TRAI DND list staleness:** DND scrub runs daily at 2 AM, but customer registered DND at 3 AM. Agent calls at 10 AM → violation. Redis cache is 31 hours stale at worst. Fix: real-time scrub on every dial-attempt via TRAI API (adds ~100ms latency).

3. **OPA policy drift:** A new RBI circular is issued (RBI issues ~147 circulars per 2022–2025). Rego policies are not updated within the grace period. Engine enforces old rules → systemic violation across thousands of calls. Fix: regulatory watch agent + policy-as-code CI/CD pipeline.

4. **Consent ledger–CRM sync lag:** Consent withdrawn in ledger but CRM still shows active → outbound campaign fires before sync propagates. Fix: event-driven architecture (Kafka consumer updates CRM within seconds), not batch sync.

5. **Cross-channel suppression failure:** Customer opts out on voice call but gets an SMS campaign 2 hours later because opt-out propagation to SMS platform is batched. Fix: real-time event bus; opt-out is a Tier-1 event that blocks ALL channels immediately.

6. **Regional language opt-out miss (Tamil/Telugu/Marathi):** Sarvam Saaras v3 covers 10 languages but WER for Telugu is 46.5% (vs. 19.31% for Hindi). Opt-out phrase in Telugu might be mistranscribed. Fix: multilingual opt-out phrase bank with fuzzy phoneme matching as fallback.

7. **Right-to-erasure vs. audit-trail conflict:** Customer invokes DPDP erasure right. System erases PII but retains anonymised audit record. Regulator (RBI) demands full call recording for 5 years. Conflict between two regulatory obligations. Fix: tiered retention policy with legal opinion per record type; preserve minimal identifiers needed for regulatory purpose only.

8. **Hallucinated disclosure confirmation:** LLM output rail certifies "grievance disclosure made" but the disclosure was garbled or cut off by call drop. Audit log shows compliant but call was not. Fix: disclosure detection via NER on transcript, not LLM self-reporting.

9. **Consent manager API downtime:** Registered DPB Consent Manager (operative Nov 2026) goes down. Pre-call consent check fails open or closed? If open → compliance risk. If closed → revenue loss. Fix: local consent cache with TTL + fallback to fail-safe mode (only transactional calls with existing consent proceed).

10. **Aadhaar / PAN leakage in transcript:** Customer reads out their Aadhaar number during call. STT captures it. Transcript written to log without PII redaction → data exposure violation. Fix: Presidio redaction on transcript stream before any persistence.

---

## 7. Gap to Full Adaptation

### What AI Still Cannot Do as Well as a Human

**Gap 1 — Novel regulatory interpretation.** A new RBI circular uses ambiguous language. A senior compliance officer reads it, interprets intent, and updates the floor procedure within days. The AI's OPA policies require an engineer to manually update Rego code. Until the policy file is updated and deployed, the engine runs on stale rules. **Path to close:** Build a regulatory-watch agent that monitors RBI/IRDAI/DPDP/TRAI websites for new circulars, uses Claude Opus to extract affected policy dimensions, generates a Rego policy diff, queues for human approval, and auto-deploys post-approval. Target: <48h circular-to-deployment cycle.

**Gap 2 — Multilingual nuanced consent withdrawal.** "Bhai, yeh sab band kar" (informal Hindi: "brother, stop all this") is an opt-out signal a human agent instantly recognises across dozens of dialectal variants. Current NER models miss regional colloquialisms and indirect refusals. **Path to close:** Train a multilingual intent classifier (opt-out-specific) on 10,000+ annotated opt-out utterances across 10 Indian languages + Hinglish. Use active learning: flag uncertain cases for human labeling, retrain weekly. Target: >95% recall on opt-out signals.

**Gap 3 — Real-time ethical judgment.** Customer reveals they are in financial distress ("ghar mein koi kaam nahi, bache bhookhe hain"). A human agent recognises this crosses into a sensitive context requiring empathy, possible escalation, and non-hardship of a vulnerable person. RBI's "fair practices" expect this. Current LLMs may detect the sentiment but don't consistently trigger the right protocol. **Path to close:** Vulnerable-customer detection classifier → mandatory human escalation. NeMo Guardrails dialog rail: if `vulnerable_customer_detected → MUST_ESCALATE`.

**Gap 4 — Cross-session consent memory.** If a customer withdraws consent on Day 1 (call 1), then calls inbound on Day 3 (call 2), the inbound call should still honour the withdrawn consent for outbound campaigns. Current implementations often silo per-call consent state. **Path to close:** Persistent customer consent profile in ledger, queried at the start of EVERY interaction regardless of channel or direction.

**Gap 5 — Regulator-facing narrative explanation.** During an RBI inspection, a compliance officer can explain WHY a policy decision was made for a specific customer on a specific date, with reasoning. AI produces structured logs but cannot yet generate a coherent, auditor-facing narrative from those logs. **Path to close:** LLM-powered audit narrative generator (Claude Sonnet) trained on past inspection Q&A formats. Takes structured audit record → generates prose explanation → human reviews before submission.

---

## 8. HITL Triggers

| Situation | Trigger | Action |
|---|---|---|
| New regulatory circular | Regulatory watch agent flags new circular | Human compliance officer reads + approves Rego policy diff before deploy |
| Novel compliance edge case | OPA returns `indeterminate` (rule coverage gap) | Route call to human supervisor immediately |
| Vulnerable customer signal | `vulnerable_customer_score > 0.7` | Mandatory human transfer, freeze outbound campaign for this customer |
| Customer files grievance during call | `grievance_event` in NLP output | Human grievance officer takes over; log to grievance register |
| DPDP erasure request | `erasure_request_detected` | Legal + DPO review queue; execute within statutory period |
| Data breach event | Any unexpected PII access log | Human CISO + DPO within 72 hours (DPDP + RBI mandate) |
| OPA policy evaluation error | Policy engine throws exception | Fail-safe: block call, escalate to human; never fail open on compliance |
| Regulator audit / inspection | RBI/IRDAI inspection scheduled | Human compliance team takes primary with AI-generated audit package as support |

---

## 9. Automation Readiness: 8 / 10

**Why 8 and not 10:**
- Deterministic pre-flight checks (DND, time-window, frequency, consent): **10/10 automatable right now**.
- Real-time disclosure enforcement: **9/10** — high confidence, occasional STT failure in noisy environments.
- Consent ledger capture + audit assembly: **9/10** — well-solved engineering problem.
- Multilingual opt-out detection in all regional languages: **6/10** — WER too high for Tamil/Telugu/Odia edge cases.
- Novel regulatory interpretation: **3/10** — always needs human in the approval loop.
- Vulnerable-customer ethical routing: **5/10** — detection is getting better but recall is not yet reliable enough to stake compliance on.

Weighted average: ~8.

---

## 10. Build Spec

### What to Build

**Phase 1 (P0 — ship first, blocks everything):**
- [ ] OPA policy bundle: `rbi_fpc.rego`, `trai_tcccpr.rego`, `irdai_norms.rego`, `dpdp_consent.rego`. Parameterised by `call_type`, `sector`, `customer_id`.
- [ ] Pre-call policy evaluation service: FastAPI endpoint, OPA sidecar, <200ms p99. Returns `{allow: bool, reason: string, blocking_rule: string}`.
- [ ] Consent ledger: PostgreSQL append-only schema + REST API (`grant`, `withdraw`, `query`, `history`).
- [ ] DND scrub integration: daily NCPR delta sync + Redis cache + per-dial lookup.
- [ ] TRAI DLT template registry: template store + template-ID injection into every outbound dial.

**Phase 2 (P1 — compliance during call):**
- [ ] Sarvam Saaras v3 streaming STT integration: WebSocket, 3s chunk processing.
- [ ] Opt-out NER model: MuRIL fine-tuned on 10K annotated opt-out utterances (Hindi, Hinglish, + 4 high-volume regional languages). Threshold: >95% recall.
- [ ] NeMo Guardrails config: dialog rail implementing `PRE_CALL → OPENING_DISCLOSURE_CHECK → ACTIVE → OPT_OUT_WATCH → CLOSING_DISCLOSURE_CHECK → POST_CALL`.
- [ ] Disclosure checklist tracker: per-call state tracking which mandatory disclosures have been delivered. Block call closure if incomplete.

**Phase 3 (P2 — audit + reporting):**
- [ ] Post-call audit assembler: Pydantic `InteractionAuditRecord`, assembles transcript + consent events + disclosure log + commitments + violations → audit store.
- [ ] PII redaction: Presidio on transcript stream before persistence.
- [ ] Regulatory report generator: DuckDB aggregation + structured JSON + narrative generator (Claude Haiku).
- [ ] Regulatory watch agent: RSS/scrape RBI/IRDAI/DPDP/TRAI sites, LLM extraction of policy changes, Rego diff generation, PR + human approval workflow.

### Data Needed

- Annotated opt-out utterance corpus: 10,000+ examples, 10 Indian languages + Hinglish. Sources: existing call recordings, synthetic data via Sarvam TTS, human labeling.
- RBI/IRDAI/DPDP/TRAI regulatory corpus: all circulars 2019–present, parsed to structured policy summaries. Input for regulatory watch agent.
- Historical compliance violation cases: ground-truth for evaluating false-negative rate.

### Eval Metrics (gate to ship)

| Metric | Gate |
|---|---|
| OPA pre-call false-negative rate (let a violating call through) | <0.01% |
| Opt-out recall across Hindi + Hinglish | ≥95% |
| Opt-out recall across regional languages (Tamil, Telugu, Marathi, Bengali) | ≥85% |
| Mandatory disclosure detection accuracy (did AI confirm disclosure actually happened?) | ≥98% |
| Consent ledger write success rate | ≥99.99% |
| Pre-call policy evaluation latency p99 | <200ms |
| Audit record assembly completeness (all fields populated) | 100% |
| PII redaction recall on Aadhaar/PAN/phone | ≥99.9% |

---

## 11. India Specifics

### Hinglish / Regional Language Nuances

- **Opt-out in Hinglish is highly indirect.** "Yaar choddo na" (bro, just leave it) is an opt-out. "Band karo ye bakwaas" (stop this nonsense). Training corpus must include colloquial, rude, and indirect variants.
- **Code-switching within a sentence.** "Please mujhe DND pe daal do" (please put me on DND). STT must handle mid-sentence language switch. Sarvam Saaras v3 is the only production model with explicit code-mixing support for this.
- **Regional formal honorifics affect tone classifiers.** Tamil "inga paarunga" vs. "da" register — tone classifiers trained on North Indian Hindi will mis-classify Tamil formal speech as neutral when it's actually polite refusal.
- **Hinglish grievance expressions.** "Main complaint karna chahta hun" vs. "Mujhe complaint karni hai" vs. "Shikayat karni hai" — NER must handle all variants.

### Regulatory Nuances

- **TRAI Feb 2025 amendment is retroactively stricter.** Transactional calls are now ONLY those triggered within 30 minutes of a customer action. Many existing "transactional" call lists became non-compliant overnight.
- **DPDP Rules operative May 2027 but Consent Manager registry operative Nov 2026.** Build the consent ledger now; integrate with registered CMs when registry goes live. Don't wait.
- **RBI 1600-series mandate is LIVE NOW** for BFSI entities, not a future requirement. Many mid-market BPOs are still on normal CLIs — immediate enforcement risk.
- **IRDAI mis-selling liability.** If an AI agent mis-sells an insurance product, the insurance company is liable even if the error was in the AI script. This makes IRDAI the most legally consequential regulator for insurance BPOs. Every insurance product feature claim needs to be schema-validated against the insurer's product database before the AI speaks it.
- **RBI data localisation.** ALL data must be stored in India (ap-south-1 / Azure India Central / Jio Cloud). Sending call recordings or transcripts through US-based LLM APIs without Data Processing Agreements is a violation. Use on-premise LLM inference or India-regional endpoints.
- **DPDP children's data.** If any contact might be a minor (e.g., student loan products), verifiable parental consent is required before ANY data processing. This must be a blocking gate in the pre-call policy engine.
- **RBI 6-hour cyber incident reporting.** Any breach or suspected breach must be reported to the RE within 6 hours of detection. Auto-alert pipeline is non-negotiable.

### Vendor Landscape (India-Specific)

| Vendor | Role | India-specific |
|---|---|---|
| **Exotel** | Telephony + number series routing | ULVNO (DoT-compliant), 1600/140 routing, DLT integration |
| **Rootle.ai** | Voice AI compliance platform | DPDP-ready, TRAI/RBI/IRDAI/SEBI, audit-ready logs |
| **Sarvam AI** | Hindi + regional STT/TTS | Unicorn as of Jun 2026, $234M raised, Saaras v3 SOTA |
| **Convin.ai** | 100% call QA + real-time compliance | Bengaluru-based, BPO-focused, real-time violation alerts |
| **Leegality / Consent.in** | DPDP consent ledger + CM integration | Bhashini-powered 22-language support, DPB registration track |
| **Consently** | Enterprise DPDP compliance | Bhashini multilingual, consent lifecycle APIs |
| **CarmaOne.ai** | RBI-compliant AI collections | FPC-specific, 99.97% compliance rate claim |

---

## 12. References

- [AI Calling Compliance in India 2026 — DPDP, TRAI DLT, RBI Guide](https://www.autointerviewai.com/blog/ai-calling-india-dpdp-trai-dlt-compliance-complete-guide-2026)
- [RBI Compliant AI Collections Guide India 2026 — CarmaOne](https://www.carmaone.ai/blog/rbi-compliant-ai-collections-guide-india-2026)
- [Voice AI Compliance in India — Rootle.ai](https://rootle.ai/voice-ai-compliance/)
- [DPDP Act 2023 + Rules 2025 — EY India](https://www.ey.com/en_in/insights/cybersecurity/transforming-data-privacy-digital-personal-data-protection-rules-2025)
- [Consent Management Under DPDP Act — DPO India](https://www.dpo-india.com/Blogs/consent-management-india-dpdp-act/)
- [DPDP + RBI Dual Compliance BFSI 2026 — TCSA](https://www.tcsa.in/resources/dpdp-compliance-bfsi-rbi-guidelines)
- [Interplay DPDP + RBI/IRDAI/SEBI/TRAI — DPO India](https://www.dpo-india.com/Blogs/interplay-india%E2%80%99s-dpdp-act/)
- [Sarvam Saaras v3 ASR — Sarvam AI](https://www.sarvam.ai/blogs/asr)
- [Open Policy Agent — OPA](https://www.openpolicyagent.org/)
- [NVIDIA NeMo Guardrails](https://docs.nvidia.com/nemo/guardrails/latest/index.html)
- [Convin Real-Time Compliance Monitoring](https://convin.ai/solutions/use-case/avoid-call-center-compliance-violation)
- [RBI IT Outsourcing Master Directions 2023](https://fidcindia.org.in/wp-content/uploads/2023/04/RBI-OUTSOURCING-OF-IT-SERVICES-10-04-23.pdf)
- [RBI Digital Lending Directions 2025 — Legal500](https://www.legal500.com/developments/thought-leadership/reserve-bank-of-india-digital-lending-directions-2025-brief-overview-analysis/)
- [TRAI DND Compliance for AI Outbound Calling India 2026 — Caller Digital](https://www.caller.digital/blog/trai-dnd-compliance-ai-outbound-calling-india)
- [Best DPDPA Consent Management Platform India 2026 — Consently](https://www.consently.in/blog/best-dpdpa-consent-management-platform-for-fintechs-india-2026)
- [OPA vs Cedar vs Zanzibar — OSO HQ](https://www.osohq.com/learn/opa-vs-cedar-vs-zanzibar)
- [LLM Guardrails for Fintech — Maxim AI](https://www.getmaxim.ai/articles/llm-guardrails-for-fintech-compliance-hallucination-prevention-and-audit-trails/)
- [Exotel Scaling Voice AI](https://exotel.com/blog/scaling-voice-ai-exotel-operational-playbook/)

---

*Document generated by ml-engineer-agent, Jarvis system. Research date 2026-06-24. Validate regulatory specifics against primary RBI/IRDAI/TRAI/MeitY sources before production implementation.*
