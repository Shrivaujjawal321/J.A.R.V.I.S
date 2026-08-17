# B05 — Memory Architecture (Session + Customer Long-Term + Org Memory; Personalization)

**Chunk:** Memory architecture (session + customer long-term + org memory; personalization)
**Context:** India-market, multilingual (Hindi + regional + Hinglish), RBI/IRDAI/DPDP-compliant, action-taking voice+chat contact-center agent for mid-market BPOs.
**Last updated:** 2026-06-24
**Research depth:** First-principles + 2026 SOTA (Mem0, Zep/Graphiti, GAAMA, LangMem, MemGPT literature, DPDP Rules 2025, RBI data localization mandate)

---

## 1. Why Memory Is the Hardest Unsolved Problem in Contact-Center AI

A skilled BPO agent knows who they're talking to *before* they say "hello." They recall the complaint filed three weeks ago, sense that this is the customer's fourth call on the same issue, notice that the last agent promised a callback that never came, and frame their opening accordingly. This contextual awareness — across time, channels, and the customer's emotional arc — is what separates a 9 CSAT from a 4.

No amount of LLM reasoning ability compensates for memory failure. An agent that hallucinates a customer's loan account number, misremembers a previous commitment, or treats a platinum-tier customer like a first-timer causes active damage. This is why memory is architecturally upstream of everything else: routing, intent, compliance, resolution — all depend on it.

---

## 2. Human Micro-Steps — What a Skilled Agent Actually Does

Decomposed to atomic cognitive + mechanical sub-steps:

### 2.1 Pre-Call Orientation (T-minus 5s to T-0)

**MS-1 — Screen pop recognition**
Agent glances at the CTI/CRM screen pop (triggered by ANI or customer-entered IVR DNIS). They scan: account tier, open tickets, last-contact date, channel of last interaction, agent notes from last call.

**MS-2 — Emotional priming from history signals**
Agent reads tone signals from CRM notes: "Customer escalated to supervisor on prior call," "promised refund on 2026-06-10, not yet processed." They consciously adjust their opening tone — more empathetic, more proactive in acknowledging delay.

**MS-3 — Ticket clustering (mental grouping)**
Agent mentally groups the visible tickets into themes — not just "3 open tickets" but "all 3 are about the same UPI transaction dispute, progressive escalation." This mental clustering shapes their opening hypothesis about call purpose.

**MS-4 — Priority cue detection**
Agent spots VIP/tier markers, regulatory-sensitive flags ("RBI complaint filed", "IRDAI grievance"), or legal escalation signals. These override standard playbooks.

### 2.2 Opening / Verification (T=0 to T=60s)

**MS-5 — Identity verification with context recall**
Agent verifies: name, DOB, registered mobile, policy/account number. Simultaneously cross-checks verbal answer against what CRM shows — detects inconsistencies (possible fraud or wrong account lookup).

**MS-6 — Warm contextualization opening**
Agent does NOT start with "how can I help you today?" if context shows a follow-up call. Instead: "I can see you called earlier about your claim — let me pull that up for you." This signals memory continuity to the customer.

**MS-7 — Language/dialect calibration**
Agent detects customer's code-switching pattern in the first sentence: pure Hindi, Hinglish, English, Tamil-English mix. Agent mirrors that register for the rest of the call.

### 2.3 Intra-Call Context Management (T=60s to resolution)

**MS-8 — Working memory maintenance**
Agent mentally tracks: what has been said THIS call, what was promised on previous calls, which parts of the issue are already resolved. This is the "session" memory layer — no CRM needed, held in active working memory.

**MS-9 — Contradiction detection**
If the customer says "I was told I'd get a refund in 3 days" but CRM shows no refund promise was logged, agent must decide: believe customer, or flag discrepancy. This is a higher-order memory reconciliation task.

**MS-10 — Promise registry**
Agent mentally (and sometimes on a notepad/screen sticky) tracks commitments made THIS call: "I'll escalate this within 2 hours," "I'll send you an email with the status by EOD." These need to be logged before call end.

**MS-11 — Organizational memory lookup**
Agent knows (from training + experience) product-specific quirks, current outages, known policy changes, escalation paths for this BPO client. This is procedural/semantic org-level memory — not customer-specific.

**MS-12 — Regulatory compliance recall**
For RBI/IRDAI-governed interactions (banking, insurance), agent recalls mandatory disclosure requirements: must inform about charges, must get explicit consent for auto-renewal, must read specific script for grievance acknowledgment. This is procedurally stored, not looked up each time.

### 2.4 Post-Call (ACW — After Call Work, T=resolution to T+3min)

**MS-13 — Memory consolidation (CRM note writing)**
Agent summarizes the call: what the customer said, what was promised, what action was taken, next follow-up date. This is the act of *writing* short-term session memory into long-term customer memory. Quality here determines whether the next agent starts cold or warm.

**MS-14 — Memory decay management**
Agent decides what to log vs. omit. Not everything should persist. A customer's complaint about hold music is noise. A customer's stated preference for email-only communication is signal. Humans make this judgment call implicitly; it is rarely formalized.

**MS-15 — Cross-channel memory sync**
If the customer also emailed or chatted, the agent checks whether the email thread gives more context than the CRM note. This cross-channel reconciliation is ad-hoc, error-prone, and rarely done well under time pressure.

---

## 3. Agent Approach — 2026 AI Implementation Per Micro-Step

### 3.1 Four-Layer Memory Architecture

Production contact-center AI requires four distinct memory layers, each with different persistence horizon, retrieval mechanism, and regulatory treatment:

```
Layer 1: Working / In-Context Memory
  - Scope: Current conversation turn window
  - Storage: LLM context window (128K–1M tokens on Claude 4.x / Gemini 2.x)
  - Managed by: Prompt engineering, turn history truncation policy
  - Latency: 0ms (already in context)

Layer 2: Session Memory
  - Scope: Current call/chat session (typically 5–45 min)
  - Storage: Redis (in-memory, sub-5ms P99 reads)
  - Managed by: Conversation state machine, session state dict
  - Latency: 3–8ms P99 read

Layer 3: Customer Long-Term Memory
  - Scope: Customer's lifetime across all sessions, channels, agents
  - Storage: Mem0 / Zep+Graphiti / custom hybrid (vector + graph)
  - Managed by: Memory extraction pipeline post-session + async during session
  - Latency: 30–80ms P99 read (retrieval from vector/graph store)

Layer 4: Organizational / Procedural Memory
  - Scope: BPO client's policies, product knowledge, compliance scripts, known outages
  - Storage: Knowledge base (RAG), fine-tuned adapters, structured tool-callable config
  - Managed by: Weekly KB refresh cron, fine-tune cycle on policy updates
  - Latency: 50–120ms P99 (RAG retrieval + rerank)
```

### 3.2 Micro-Step to Agent Technique Mapping

**MS-1 (Screen pop) → Pre-call context assembly pipeline**
Triggered on call connect event (CTI webhook). Parallel fanout:
- Fetch customer record from CRM API (Salesforce / Freshdesk / Zoho): <50ms
- Query Layer-3 memory (Mem0 `search(user_id, query="recent issues and preferences", top_k=10)`): <80ms
- Pull open tickets from ticketing system: <30ms
Assemble into a structured `CustomerContext` Pydantic model injected at the TOP of the system prompt. All three queries fire in `asyncio.gather`.

**MS-2 (Emotional priming) → Sentiment trajectory extraction**
Mem0/Zep stores not raw transcripts but extracted memories including sentiment facts: "Customer expressed strong frustration about refund delay on 2026-06-10 (confidence: high)." Injected as `<customer_sentiment_history>` block. LLM opening turn is conditioned on this.

**MS-3 (Ticket clustering) → Automated theme clustering on retrieved tickets**
Open tickets fetched from CRM are passed through a lightweight structured-output call (Haiku 4.x with JSON schema) that clusters them by root issue, deduplicates, and identifies escalation trajectory. Output injected as `<ticket_summary>` with cluster labels.

**MS-4 (Priority detection) → Rule-based + ML priority flag**
Hard rules: if CRM tier = "Platinum" OR open_complaint_type CONTAINS "RBI_Grievance" → inject `<priority_level>HIGH</priority_level>` + corresponding playbook pointer. No LLM needed for this — deterministic business logic.

**MS-5 (Identity verification) → Structured verification flow with real-time cross-check**
Agent asks for OVs (ownership verification questions). Customer answers are extracted via ASR + NER (Sarvam-STT for Hindi/Hinglish or Bhashini API). Extracted values checked against CRM record via exact/fuzzy match. Mismatch → route to supervisor. Match → set `auth_state = VERIFIED` in session Redis.

**MS-6 (Warm contextualization) → Context-aware opening generation**
System prompt instructs the LLM: if `prior_calls > 0` AND `open_issues_exist`, do NOT use generic greeting. Instead use a template that references the most recent issue. Few-shot examples cached in system prompt with `cache_control: {type: "ephemeral"}`.

**MS-7 (Language calibration) → Language detection + register mirroring**
First customer utterance passed through IndicLID (Indian Language Identifier, Bhashini stack) or Sarvam's language detection API. Detected language + code-switching ratio updates `session.language_profile`. System prompt instructs LLM to mirror detected register. This is re-evaluated every 3 turns for code-switch drift.

**MS-8 (Working memory) → Long-context window, structured turn log**
Within a session, all turns are kept in a sliding context window. A `ConversationBuffer` in Redis (JSON) stores structured turn objects: `{speaker, text, detected_intent, entities_extracted, timestamp}`. Truncation policy: keep last 20 turns verbatim + extractive summary of earlier turns (DistilBART or Haiku summarizer).

**MS-9 (Contradiction detection) → Cross-source reconciliation prompt**
When customer makes a factual claim ("I was told X"), the system runs a targeted memory query: `mem.search(user_id, query="promise OR commitment related to [entity]")`. Retrieved memories + CRM notes are passed to a structured-output chain that returns `{contradiction_found: bool, confidence: float, resolution: enum[TRUST_CUSTOMER, TRUST_CRM, ESCALATE]}`.

**MS-10 (Promise registry) → Real-time commitment extraction**
Every agent turn is passed through a lightweight streaming NER model (fine-tuned on BPO conversations) that detects commitment phrases: "I will", "you will receive", "by [date]", "I am escalating". Extracted commitments stored to a `promises` list in session state. At session end, promises are bulk-written to CRM + Mem0.

**MS-11 (Org memory) → RAG over KB + Pinned procedure nodes**
Organizational memory is a separate retrieval pipeline: hybrid BM25 + dense search over the BPO client's policy KB (Qdrant or Weaviate). For compliance scripts (mandatory disclosures), these are NOT retrieved by RAG — they are pinned as tool-callable functions: `get_grievance_script(category)` returns the exact verbatim script. No hallucination risk on hard-compliance text.

**MS-12 (Regulatory recall) → Structured compliance decision tree**
RBI/IRDAI mandatory disclosures encoded as a deterministic FSM (finite state machine) triggered by specific intents (e.g., `intent=LOAN_CLOSURE` triggers RBI pre-payment disclosure). LLM is instructed to call `run_compliance_check(intent, product_type)` before responding on regulated topics. This is deterministic code, not LLM judgment.

**MS-13 (CRM note writing) → Async post-session memory consolidation**
On call end event, a background worker fires:
1. Full transcript → Haiku 4.x with structured-output prompt → extracts: summary, sentiment, key facts, commitments, preferred channel, unresolved issues → writes to CRM (via API) + Mem0 (as new memories)
2. Fact deduplication: Mem0 / Graphiti's entity resolution prevents "email only" being stored 3 times
3. Memory quality scoring: a lightweight scorer checks for vague/empty summaries before write (rejects summaries below length threshold or containing filler phrases)

**MS-14 (Memory decay) → Tiered TTL + salience scoring**
Not all memories persist equally. Implementation:
- Operational memories (open ticket status) — TTL 30 days, auto-expire
- Preference memories (language preference, communication channel) — TTL 365 days, auto-refresh on confirmation
- Commitment memories — TTL until closed/resolved, no auto-expire
- Sentiment trajectory — rolling window of last 10 sessions, oldest drops off
Salience score (Haiku-computed at write time): `0.0-1.0`. Memories below `0.3` are stored but deprioritized in retrieval.

**MS-15 (Cross-channel sync) → Unified event stream into memory layer**
All channels (voice, chat, email, WhatsApp) write to a common event bus (Kafka or AWS EventBridge). Memory ingestion consumer subscribes and processes all events into the same Mem0 user_id space. Cross-channel deduplication by content hash + entity overlap.

---

## 4. Tooling — Concrete 2026 Stack

### Core Memory Engines

| Component | Tool | Why |
|---|---|---|
| Long-term customer memory | **Mem0 v2** (managed) or self-hosted OSS | Most widely adopted, 48K GitHub stars, $24M Series A Oct 2025. LoCoMo: 92.5%, LongMemEval: 94.4% [sourced] |
| Temporal/relationship memory | **Zep v2 + Graphiti** | DMR: 94.8% vs MemGPT 93.4% [sourced]. 90% latency reduction vs context-stuffing. Tracks fact lifecycle with temporal bounds — critical for "when was this promised?" |
| Hybrid graph+associative | **GAAMA** (research, not yet prod) | LoCoMo-10: 79.1% mean reward, +4.2pp over tuned RAG. Better for multi-hop cross-session reasoning [sourced, arxiv 2603.27910] |
| Procedural/self-updating | **LangMem SDK** (LangChain) | Agents rewrite own system prompt instructions from feedback. NOT for latency-sensitive paths — batch/background only |
| Session state | **Redis** (Upstash for serverless, ElastiCache for AWS) | Sub-5ms P99, TTL support, JSON native |
| Vector store (org KB) | **Qdrant** or **Weaviate** | Hybrid BM25 + dense, reranking, metadata filtering |
| Graph store (customer relationships) | **Neo4j v5.x** | Graphiti backend, temporal edge properties |
| Customer profile DB | **Postgres + pgvector** | Structured facts + vector search in one store for low-complexity deployments |

### LLM Layer

| Task | Model | Why |
|---|---|---|
| Context assembly, reasoning | **Claude Sonnet 4.x** | 200K+ context, tool use, prompt caching |
| Memory extraction (post-session) | **Claude Haiku 4.x** | Cost-efficient for high-volume write path; structured output via tool use |
| Language detection | **Sarvam-STT / Bhashini API** | 22 Indian scheduled languages + dialects + Hinglish. Bhashini-v2 (early 2026): tribal and regional dialect improvements [sourced] |
| Entity NER for promises | **Fine-tuned mBERT or IndicBERT** | Sub-20ms inference on CPU, BPO-domain fine-tuned |
| Contradiction resolution | **Claude Sonnet 4.x** with structured tool use | Needs reasoning depth; Haiku fails on subtle contradictions |

### Integration Layer

| Need | Tool |
|---|---|
| CRM write | Salesforce REST API / Freshdesk API / Zoho CRM |
| Event bus | Apache Kafka (on-prem BPO) / AWS EventBridge (cloud) |
| Observability | Langfuse (traces) + Prometheus/Grafana (latency metrics) |
| Compliance audit log | Immutable append-only store (WORM S3 / AWS Compliance) — required by DPDP |
| Consent management | Purpose-built consent ledger (DPDP Rules 2025 mandated) |

---

## 5. Benchmarks

| Metric | Value | Source |
|---|---|---|
| Mem0 LoCoMo accuracy | 92.5% | [sourced — mem0.ai blog, April 2026] |
| Mem0 LongMemEval accuracy | 94.4% | [sourced — mem0.ai blog, April 2026] |
| Mem0 BEAM (10M tokens) | 48.6% | [sourced — mem0.ai blog, April 2026] |
| Mem0 tokens per retrieval (LoCoMo) | ~6,956 | [sourced — mem0.ai blog] |
| Zep DMR accuracy | 94.8% | [sourced — callsphere.ai, arxiv 2501.13956] |
| Zep vs Mem0 LongMemEval delta | Zep +15pp (63.8% vs 49.0% GPT-4o) | [sourced — atlan.com] |
| Zep latency reduction vs context-stuffing | 90% | [sourced — callsphere.ai] |
| Zep per-episode cost | ~500-2000 input + 200-800 output tokens | [sourced — callsphere.ai] |
| Zep memory footprint per conversation | 600K+ tokens | [sourced — Mem0 paper critique] |
| GAAMA LoCoMo-10 mean reward | 79.1% (+4.2pp vs RAG baseline) | [sourced — arxiv 2603.27910] |
| MemMachine LoCoMo with GPT-4.1-mini | 0.9169 | [sourced — arxiv 2604.04853] |
| LongMemEvalS (systematic ablation, ICLR 2025) | 93.0% overall | [sourced — arxiv search] |
| Sub-100ms customer profile read P99 | Achievable with Redis (<5ms) + pre-warm on CTI event | [estimate] |
| Pre-call context assembly latency (parallel fetch) | 80-120ms P95 | [estimate based on CRM API + Mem0 latency profile] |
| Post-session memory write (async) | 3-8s background worker | [estimate] |
| MINJA memory injection attack success rate | >95% against production agents | [sourced — NeurIPS 2025, Dong et al.] |
| CRM note quality improvement (AI vs human) | ~40% reduction in missing fields | [estimate, BPO case studies] |
| Cross-channel identity resolution accuracy | ~85-92% with fuzzy match + entity linking | [estimate] |

---

## 6. Failure Modes

**FM-1: Memory hallucination / confabulation**
The LLM generates plausible-sounding but fabricated memories. E.g., "You mentioned last time that you prefer SMS communication" when no such preference exists. Root cause: memory injection into prompt being over-trusted without confidence scoring. Mitigation: never surface memory without confidence score + source attribution. Agent says "I see a note from your last call saying X" — always attributing to the source.

**FM-2: Memory poisoning (MINJA attack)**
Attackers (or even adversarial customers) can inject false memories through conversational manipulation. NeurIPS 2025 showed >95% success rate. A customer says "as I mentioned, you agreed to a full waiver last time" — if the agent's memory layer lacks a write-integrity mechanism, this claim could be stored as fact. Mitigation: write-time validation (only write memories from agent-side facts, not customer assertions), source-tagging (flag memories as `source=customer_claim` vs `source=agent_confirmed`).

**FM-3: Staleness — outdated memory surfaced as current truth**
Customer changed address 3 months ago. Old address is retrieved as top-k result. Memory system lacks proper temporal invalidation. This is exactly what Zep/Graphiti solves with `invalid_at` timestamps, but naive vector stores don't handle it.

**FM-4: Cross-customer memory bleed**
Bug in user_id scoping causes memories from Customer A to be retrieved for Customer B. Catastrophic in financial/insurance context. Root cause: missing user_id filter in vector search (easy to accidentally omit in LangChain-style code). Mitigation: mandatory metadata filter enforced at the retrieval layer, never optional.

**FM-5: Over-personalization — creeping out the customer**
Agent references preferences the customer doesn't remember sharing, or references details that feel surveillance-like. OP-Bench (arxiv 2601.13722) benchmarks this: models that use memory too aggressively score lower on user trust. Mitigation: memory injection guidelines (only reference memory when directly relevant, use indirect phrasing "I see we've chatted before about X" not "I know you prefer Y").

**FM-6: Context window overflow at scale**
For long-tenure customers with 100+ interactions, naive memory injection floods the context window. Zep's memory footprint can exceed 600K tokens per conversation. Mitigation: use retrieval-augmented memory (not full-history injection), k-top retrieval with relevance scoring, hierarchical summarization (rolling summaries for old sessions, verbatim for recent 3-5).

**FM-7: Hinglish / multilingual entity mismatch**
Customer says "mera account number teen sau paanch sau..." (Hindi numerals). Memory was stored with English numerals "3505". Entity matching fails. Root cause: lacking a normalization layer for Indian-language number words, transliterations, and mixed-script entities. Mitigation: normalization pipeline (IndicNLP transliteration + numeral conversion) applied at BOTH write and read time.

**FM-8: Post-session write failure**
Network timeout or API failure during the async post-session memory write loses the ACW data. No retry → next agent starts cold again. Mitigation: dead-letter queue on Kafka, retry with exponential backoff, alerting on failure rate > 2%.

**FM-9: Memory without temporal reasoning — "which promise is current?"**
Flat vector stores retrieve the most semantically similar memory, not the most recent. A customer who asked for a refund in January and was denied, then successfully received one in April — a naive system might retrieve the January denial as the answer to "what happened with my refund?" Mitigation: Zep/Graphiti temporal graph, or explicit recency weighting in retrieval.

**FM-10: Regulatory over-retention**
Storing customer memories beyond the DPDP-mandated retention period, or storing sensitive categories (health, religion, financial distress signals) without explicit consent. Mitigation: retention policy engine with auto-purge, sensitive-category classifier at write time, consent ledger gating.

---

## 7. Gap to Full Adaptation

### What the agent cannot yet match the human on:

**Gap 1: Implicit emotional memory**
A skilled human agent remembers not just facts but emotional texture — "this customer was close to crying last time, tread carefully." Current AI memory stores explicit facts and sentiment labels but lacks the nuanced "felt sense" of a prior interaction's emotional weight. Closing path: store not just sentiment polarity but intensity, context, and trigger entity. Train memory retrieval to surface emotional warnings, not just informational facts.

**Gap 2: Organizational tribal knowledge**
Human agents accumulate implicit procedural knowledge through hallway conversations, supervisor tips, overheard calls: "when you get a complaint about the XYZ product, always loop in the technical team before telling the customer anything." This tacit org knowledge is never in the official KB. Closing path: automated extraction from call recordings + supervisor escalation patterns (what actions expert agents take that KB says nothing about) → infer implicit procedural rules → write to org memory.

**Gap 3: Cross-session narrative coherence**
Humans build a narrative about a customer across calls: "This person has been struggling since the monsoon floods." AI memory retrieves facts but doesn't build coherent narrative arcs. GAAMA's "reflection" node type (higher-order synthesis memories) is the closest current work. Closing path: post-session reflection pass — after every 5 sessions with a customer, run a synthesis prompt that generates a "customer narrative summary" stored as a first-class memory entity.

**Gap 4: Judgment on what to forget**
Humans naturally suppress irrelevant noise. AI systems that score everything equally create retrieval noise over time. Current TTL + salience scoring is a proxy but lacks the contextual judgment of "this complaint was resolved; don't keep bringing it up." Closing path: resolution-triggered memory archival (when a ticket closes, mark associated memories as `status=resolved`; retrieval deprioritizes resolved memories unless explicitly queried).

**Gap 5: Cross-language entity resolution in memory**
Matching "Rajesh Kumar" (English CRM) with "राजेश कुमार" (Hindi transcript) with "Rajesh ji" (Hinglish call) is an unsolved hard problem at scale. Current entity linking fails on transliterations, honorifics, and regional name variations. Closing path: IndicBERT-based entity resolution layer fine-tuned on Indian name variants + fuzzy phonetic matching (Soundex variants for Indian phonology).

---

## 8. HITL Trigger

This step is NOT fully automatable without human oversight in the following cases:

1. **Identity verification failure or mismatch** — when verification signals conflict (customer says one thing, CRM shows another). Agent must pause and route to senior agent.

2. **Regulatory-sensitive memory decisions** — determining whether a specific customer conversation falls under "sensitive personal data" categories under DPDP (financial distress, health data) requiring special consent. This classification call should have human review for the first 90 days of deployment, then can be automated once classifier accuracy > 97%.

3. **Memory contradiction with legal consequence** — if memory shows a commitment was made but CRM shows no record, and the customer is asserting this in a formal grievance, a human must adjudicate. Automated systems should escalate, not decide.

4. **Data subject rights requests under DPDP** — when a customer invokes Right to Erasure or Right to Access their stored data. The verification and execution of these rights requires human oversight (legal exposure).

5. **Memory poisoning detection** — if the system flags a potential adversarial injection attempt (unusually specific false claims, attempts to override documented facts), escalate to human review rather than storing.

For all other memory operations (session tracking, preference storage, org KB retrieval, post-call CRM write, context assembly), the step is fully automatable.

---

## 9. Automation Readiness Score: 7/10

**Rationale:**
- Session memory (Layer 1-2): **9/10** — well-solved, Redis + sliding window. Production-ready.
- Customer long-term memory retrieval: **7/10** — Mem0/Zep production-quality, but temporal reasoning and cross-language entity resolution still have failure modes.
- Post-call memory consolidation (write path): **8/10** — async pipeline well-understood, write quality is the bottleneck (not tech, but prompt engineering quality).
- Cross-channel memory sync: **6/10** — channel fragmentation + event-stream plumbing is complex, data quality across channels varies wildly in India (WhatsApp vs voice vs email).
- Organizational procedural memory: **8/10** — RAG is mature; the gap is keeping KB fresh and extracting implicit procedural knowledge.
- DPDP/RBI regulatory compliance of memory system: **5/10** — technically achievable but requires significant legal + engineering co-design; consent ledger + retention engine add 3-6 months of compliance-specific development.

**Blocker to 9/10:** Hinglish/multilingual entity resolution + regulatory compliance of the memory layer.

---

## 10. Build Spec

### What to Implement

**Phase 1 (Weeks 1-4): Foundation**
- Session memory: Redis with `session:{call_id}` key, JSON schema, 4-hour TTL
- Pre-call context assembly: Async parallel fetch (CRM + Mem0 + ticketing) on CTI webhook, assemble `CustomerContext` Pydantic model
- Language detection on first utterance: Bhashini API or Sarvam-STT wrapper, update `session.language_profile`
- System prompt injection: `CustomerContext` → `<customer_context>` XML block at top of system prompt with `cache_control: {type: "ephemeral"}` on the stable org-knowledge suffix

**Phase 2 (Weeks 5-8): Long-term memory**
- Mem0 integration: `mem.add(user_id, messages)` on session end, `mem.search(user_id, query)` on call connect
- Salience scorer: Haiku-based, runs at write time, attaches `salience_score` to each memory
- Source tagging: every memory gets `{source: "agent_confirmed" | "customer_claim" | "system_inferred"}` tag
- Retention policy: TTL by memory type (see MS-14 mapping above)
- Consent gate: no memory write without `consent.status == ACTIVE` for the user

**Phase 3 (Weeks 9-12): Advanced**
- Zep/Graphiti integration for temporal fact tracking (parallel to Mem0 for critical commitment memories)
- Promise registry: streaming NER during call, bulk write on end
- Contradiction detection: structured-output chain triggered on customer factual claims
- Cross-channel event consumer: Kafka consumer writing all channel events to unified memory layer
- DPDP compliance: sensitive-category classifier at write time, consent ledger, audit log (WORM)

**Phase 4 (Weeks 13-16): India-specific hardening**
- IndicBERT-based entity resolution for cross-language name/entity matching
- Numeral normalization pipeline (Hindi word numbers → digits → match CRM)
- Hinglish entity normalization
- Memory injection defense: source trust scoring, write-integrity validation
- Post-session reflection synthesis (every 5 sessions → customer narrative summary)

### Data Needed

1. **Historical call transcripts** (minimum 10K calls per BPO client domain) — for fine-tuning entity extraction + promise NER
2. **CRM data schema** — to map extraction fields to writable CRM slots
3. **Annotated memory quality examples** — 500+ examples of good vs. bad post-call CRM notes for write-quality scorer training
4. **Compliance taxonomy** — RBI/IRDAI mandatory disclosure scripts per product type (verbatim, from legal)
5. **Customer consent records** — existing consent database to bootstrap consent ledger
6. **Language distribution sample** — 1K calls labeled by language mix to calibrate IndicLID thresholds

### Eval Metric Gate ("Good Enough to Ship")

| Metric | Gate Threshold | Measurement Method |
|---|---|---|
| Pre-call context recall accuracy | >90% of customer facts correctly surfaced | Annotated golden set of 200 customer profiles; human eval |
| Memory write quality (CRM note completeness) | >85% of required fields populated correctly | Schema-based validator + human spot-check on 10% |
| Cross-session continuity (customer recognizes context) | CSAT delta > +0.5 on "agent remembered my issue" item | A/B test: memory-enabled vs. cold-start agent |
| Contradiction detection precision | >80% true positive | Annotated test set of 100 calls with known discrepancies |
| Promise registry completeness | >90% of stated commitments extracted | Human QA on 50 calls |
| Memory retrieval latency | P95 < 100ms pre-call assembly | Prometheus histogram |
| False memory rate (hallucination) | <2% of surfaced memories fabricated | Adversarial test set with known non-existent memories |
| DPDP consent gate failure rate | 0% — no write without active consent | Automated audit on 100% of writes |

---

## 11. India Specifics

### Linguistic Nuances

**Hinglish code-switching in memory:**
Over 350 million Indians use Hinglish [sourced — kveeky.com]. A customer's stated preference "mujhe email pe bata do" (tell me by email) must be stored as a language-agnostic preference fact: `{preference: "communication_channel", value: "email"}`, not as raw text. If stored as raw text, future retrieval with "email preference" query may not surface it due to Hindi token mismatch.

**Script mixing:**
Same entity can appear in Devanagari (हिंदी), Roman transliteration (Hindi), or mixed script within a single call. Entity resolution must handle all three. IndicBERT and MuRIL are the two best embeddings for cross-script entity similarity.

**Honorific suffixes as noise:**
"Sharma ji", "Sharma sahab", "Mr. Sharma", "Sharmaji" are all the same person. Standard NER strips these inconsistently. Custom tokenizer needed for Indian name + honorific patterns.

**Regional language memory:**
Bhashini-v2 (launched early 2026) covers tribal and regional dialect variants with improved accuracy. For BPOs serving Tier-2/3 India customers (NBFC, microfinance, regional insurance), regional language memory is mandatory. Org KB must have content in regional languages, not just Hindi and English.

### Regulatory Compliance

**DPDP Act 2023 / DPDP Rules 2025 (hard deadline: 13 May 2027):**
- Memory system is a "data fiduciary" under DPDP — must collect only data with explicit consent tied to a specific purpose
- Customers can invoke Right to Erasure → all Mem0/Zep memories for that user_id must be purged within 72 hours (DPDP Rule 12)
- Right to Access → customer can request a machine-readable export of all stored memories
- Consent must be granular: separate consent for "using call history for training" vs. "using history for personalization"
- Sensitive personal data (financial distress indicators, health-related complaints) requires explicit opt-in consent, not just implied consent

**RBI Data Localization (Payment System Operators):**
- All payment-related customer data must be stored on servers physically located in India
- If BPO client is a PSO or bank: vector database (Qdrant/Weaviate) and graph store (Neo4j) must be deployed on India-region cloud (AWS ap-south-1, Azure India Central, GCP asia-south1) or on-premises
- Foreign SaaS memory services (Mem0 Cloud, Zep Cloud US) are NOT compliant for payment data — must self-host or use India-region managed option

**IRDAI (Insurance):**
- Policyholder data, claims history, underwriting-relevant facts stored in memory must reside in Indian data centers
- Call recording consent must be captured in customer's stated language (not just English)
- Memory of policyholder complaints must be retained for 3 years (IRDAI Grievance Redressal Guidelines)

**Practical implication:**
For RBI/IRDAI-governed BPO clients, Mem0 and Zep must be self-hosted on India-region infrastructure. This adds 2-4 weeks of DevOps setup but is non-negotiable. AWS ap-south-1 + Amazon RDS Postgres + Amazon ElastiCache (Redis) + self-hosted Qdrant on EKS is the most common production pattern for compliant Indian deployment.

### BPO Operational Nuances

**Agent tenure is low in India — memory system compensates:**
Average BPO agent tenure in India is 12-18 months. Memory system must capture tacit knowledge from experienced agents before they leave. Structured knowledge extraction from top-performer call recordings is a competitive moat.

**Customer literacy variance:**
Customers calling from Tier-2/3 cities may be using shared mobile numbers (family phone). Memory must not assume 1 phone number = 1 person. Identity verification layer must be robust before writing to customer memory.

**WhatsApp is primary async channel in India:**
Unlike Western markets where email dominates async, WhatsApp is the primary async contact channel for Indian customers. Memory system must ingest WhatsApp Business API webhooks and cross-reference with voice call history.

**Festival-driven contact spikes:**
Deepawali, Eid, year-end: contact volume spikes 3-5x. Memory layer must be designed for burst reads (pre-call context assembly at 5x normal RPS). Redis cluster with read replicas, Mem0 with connection pooling, pre-warm cache on predicted spikes.

---

## 12. Framework Decision Matrix

| Scenario | Recommended Memory Stack | Why |
|---|---|---|
| Small BPO (<100 agents), quick start | Mem0 managed cloud + Redis + CRM API | Fastest to production, 2-min setup, handles most cases |
| RBI/IRDAI-regulated BPO | Self-hosted Mem0 OSS + Zep/Graphiti + Neo4j + Qdrant on AWS ap-south-1 | Data localization compliance |
| High commitment tracking need (loans, insurance claims) | Zep v2 + Graphiti (temporal graph) primary + Mem0 as fallback | Temporal reasoning for "what was promised when" |
| Multi-language regional BPO | Bhashini API + IndicBERT entity resolution + Mem0 with custom normalization | Handles 22 languages + scripts |
| Large BPO (>1000 agents), org knowledge critical | Qdrant (org KB RAG) + Zep (customer memory) + LangMem (procedural, background) | Separation of concerns, each layer optimized |

---

## 13. References

- [Mem0 State of AI Agent Memory 2026](https://mem0.ai/blog/state-of-ai-agent-memory-2026) — LoCoMo 92.5%, LongMemEval 94.4%, BEAM benchmarks
- [Zep Temporal Knowledge Graph — arxiv 2501.13956](https://arxiv.org/abs/2501.13956) — Graphiti architecture paper
- [GAAMA — arxiv 2603.27910](https://arxiv.org/abs/2603.27910) — Graph Augmented Associative Memory, LoCoMo-10 79.1%
- [MemMachine — arxiv 2604.04853](https://arxiv.org/html/2604.04853v1) — 0.9169 LoCoMo with GPT-4.1-mini
- [Zep vs Mem0 benchmarks — atlan.com](https://atlan.com/know/zep-vs-mem0/)
- [Best AI Memory Frameworks 2026 — atlan.com](https://atlan.com/know/best-ai-agent-memory-frameworks-2026/)
- [DPDP Act Compliance for Contact Centers — gistly.ai](https://www.gistly.ai/blog/dpdp-act-compliance-contact-centers)
- [DPDP Rules 2025 — EY India](https://www.ey.com/en_in/insights/cybersecurity/decoding-the-digital-personal-data-protection-act-2023)
- [RBI Data Localization — Opsio](https://opsiocloud.com/in/knowledge-base/data-localization-in-india-rbi/)
- [Zep v2 + Graphiti Production Analysis — callsphere.ai](https://callsphere.ai/blog/vw3g-zep-memory-v2-temporal-knowledge-graph-graphiti-2026)
- [OP-Bench: Over-Personalization — arxiv 2601.13722](https://arxiv.org/pdf/2601.13722)
- [Memory Poisoning Attack Surface 2026 — llms3.com](https://llms3.com/blog/when-memory-became-the-attack-surface-may-2026)
- [MINJA NeurIPS 2025 — almcorp.com summary](https://almcorp.com/blog/ai-memory-poisoning-prompt-injection-attacks/)
- [Sarvam AI 2026 — explainx.ai](https://explainx.ai/blog/india-sovereign-ai-status-indiaai-mission-2026)
- [Bhashini-v2 multilingual AI India — business-standard.com](https://www.business-standard.com/technology/tech-news/india-ai-impact-summit-multilingual-multimodal-ai-public-digital-systems-126021000954_1.html)
- [Hinglish multilingual voice AI India — kveeky.com](https://kveeky.com/news/transforming-customer-support-with-multilingual-voice-ai-in-india)
- [Sub-100ms latency optimization — engrxiv.org](https://engrxiv.org/preprint/view/4918)
- [LangMem SDK — atlan.com](https://atlan.com/know/long-term-memory-langchain-agents/)
- [ASAPP: AI agent memory in CX — asapp.com](https://www.asapp.com/blog/from-models-to-memory-the-next-big-leap-in-ai-agents-in-customer-experience)
- [Redis AI agent memory architecture — redis.io](https://redis.io/blog/ai-agent-memory-stateful-systems/)
- [Survey of AI Agent Memory Frameworks 2026 — graphlit.com](https://www.graphlit.com/blog/survey-of-ai-agent-memory-frameworks)

---

*Document owner: Jarvis ML Engineering Specialist*
*For: India Agentic AI Opportunity Map — BPO Contact Center Agent Research*
*Classification: Internal research use*
