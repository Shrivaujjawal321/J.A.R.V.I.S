# Step A09 — Multi-Turn Context & Working Memory (Holding the Thread Across a Long Call)

> **Scope:** ONE micro-step of a BPO contact-center agent's job — the cognitive faculty of *holding the entire call thread in mind*: who the caller is, what they want, what's been said, what was promised, what's still open, and weaving every later sentence back into that running picture. For an India-market, multilingual (Hindi + regional + Hinglish), RBI/IRDAI/DPDP-compliant, action-taking voice+chat agent for mid-market BPOs.
>
> **Date:** 2026-06-24 · **Author:** Research Analyst Specialist (Jarvis) · Status: Draft research note for review.

---

## 0. Why this step is the hardest "invisible" skill

A caller says at minute 1: *"main apni wife ke liye policy convert karwa raha hoon"* (I'm converting a policy for my wife). At minute 9, after a 4-minute detour about a failed UPI mandate, the caller says *"toh uska naam update kar do"* (so update her name). A good human agent knows "uska" = the wife, "naam" = on the policy being converted, not the UPI mandate. There is no slot in the IVR for "uska." This is **working memory**: a low-effort, always-on faculty for humans that is the single biggest failure surface for LLM voice agents. ICLR 2026's outstanding-paper finding — **a 39% average accuracy drop in multi-turn vs single-turn for every model tested** — is fundamentally a failure of *this step* [sourced].

This step is distinct from (and upstream of) intent classification, RAG, and action-taking. If the thread is dropped, every downstream step acts on the wrong premise.

---

## 1. Human micro-steps (the smallest atomic moves)

A skilled human BPO agent, on a long call, runs these continuously and mostly subconsciously:

1. **Anchor the call frame** — within the first 2-3 turns, lock the *primary intent / job-to-be-done* and the *entities in play* (caller identity, account/policy number, the "thing" being acted on, third parties mentioned).
2. **Maintain a running entity register** — a mental table: caller = Ramesh, account = ...4821, "wife" = Sunita (DOB asked at min 3), "policy" = the ULIP not the term plan, amount = ₹12,400.
3. **Track co-reference & deixis** — resolve "woh / uska / yeh / that one / pehle wala" to the correct prior entity, including across a Hindi↔English code-switch boundary mid-sentence.
4. **Hold the open-loop stack** — what is *promised but not yet done* ("I'll email you the form", "I'll check with my senior", "hold karo, main dekh ke aata hoon") and what the caller is *still waiting to hear*.
5. **Track the dialogue act state** — am I mid-authentication? mid-disclosure (mandatory reg script)? waiting for an OTP? collecting a reason? This is the task/slot state machine.
6. **Reconcile corrections & retractions** — caller says "₹12,400... sorry, ₹14,200" — overwrite the old value, and propagate the correction to anything downstream already computed from it.
7. **Carry emotional/relationship state** — caller was angry at min 2, calmed by min 6; don't re-trigger; remember you already apologized so you don't sound robotic repeating it.
8. **Suppress repetition** — never re-ask something already answered (a top driver of CSAT collapse); know "I already have his DOB."
9. **Bridge interruptions/barge-in** — when the caller cuts in or there's a hold, resume *exactly* where the thread was, not from the top.
10. **Segment topics within one call** — a single call often has 2-3 jobs ("also, while I have you..."); keep each job's state separate but linked to the same caller.
11. **Time-order facts (recency wins)** — when the caller gives conflicting info across turns, the *later* statement is usually authoritative; know which fact is "current."
12. **Selective forgetting / salience** — drop the small-talk and the abandoned tangent; keep the load-bearing facts. Don't let noise crowd out signal.
13. **Pre-load context into the next utterance** — phrase the next question using remembered context ("Sunita ji ki DOB confirm kar dijiye" — uses the remembered name), which signals to the caller "I'm tracking you."
14. **Hand the thread off cleanly** — on transfer/escalation, compress the whole call into a 2-line state summary so the next human doesn't restart.

---

## 2. Agent approach (2026 SOTA, per sub-step)

The 2026 consensus: **working memory is a dedicated architectural component, not "a longer prompt"** [sourced, mem0 State of Agent Memory 2026]. The voice agent runs a **layered memory stack** alongside the LLM context.

| Human micro-step | 2026 agent technique |
|---|---|
| Anchor call frame (1) | **Structured session object** initialized at call start: `intent`, `caller_id`, `entities{}`, `task_state`. Populated by a fast first-turn extractor (Haiku 4.5 / GPT-4o-mini class) and pinned to the **system-prompt head** (exploits primacy attention). |
| Entity register (2) | **Slot-filling + structured fact extraction** into a typed `session.entities` dict. Entities extracted every turn and **re-injected into the prompt** so the LLM references them explicitly "even if attention drifts" [sourced, AssemblyAI]. Letta/MemGPT **core-memory blocks** ("always in-context, like RAM") are the productionized form. |
| Co-reference / deixis (3) | LLM in-context resolution + an **explicit coref pass** that rewrites pronouns to canonical entity IDs before the action layer sees them. For Hinglish, a code-switch-aware step (see §10). |
| Open-loop stack (4) | **Procedural/working memory in LangMem**: "compressing long histories into actionable summaries" + an explicit `open_promises[]` list maintained as a tool-writable memory block. |
| Dialogue-act / task state (5) | **Schema-guided dialogue state machine** (graph) — LangGraph state + checkpointer, or Pipecat/LiveKit per-job context. Schema-Guided Dialogue × MCP convergence (arXiv 2602.18764) is the 2026 pattern. |
| Corrections / retractions (6) | **Temporal knowledge graph** (Zep/Graphiti): dual timelines (event-occurrence + fact-validity) with **automatic invalid-node detection** — old value marked invalid, new value supersedes. |
| Emotional/relationship state (7) | Sentiment tracked per-turn into session state; prosody/sentiment features stored as a memory field so apologies/empathy aren't repeated. |
| Suppress repetition (8) | "Don't re-ask answered questions" enforced by checking `session.entities` before any question; the entity-register *is* the dedup mechanism. |
| Bridge barge-in (9) | **VAD + semantic end-of-turn (Deepgram Flux)**; context aggregator preserves partial-turn state so resumption is exact. Silero VAD kept in pipeline for interruption detection [sourced]. |
| Topic segmentation (10) | Multiple **memory namespaces/threads** under one `caller_id`; LangGraph thread-per-topic or Letta archival tags. |
| Recency / time-order (11) | Temporal KG `valid_at` timestamps; recency-weighted retrieval. Chronos (arXiv 2603.16862) "structured event retrieval" for time-ordered facts. |
| Selective forgetting (12) | **Salience-gated extraction**: only atomic, load-bearing facts written to long-term memory ("Proactive Memory Extraction", arXiv 2601.04463); summarization triggered at ~70-80% context capacity [sourced]. |
| Pre-load next utterance (13) | Prompt-template injection of `session.entities` into NLG so generated questions are context-aware by construction. |
| Clean handoff (14) | LLM-generated **state summary** (the call's compressed memory) attached to the transfer/CRM ticket. |

**Reference architecture (cascaded voice pipeline, 2026 default):**

```
mic → VAD (Silero) → STT (Deepgram Flux / Sarvam / IndicConformer)
      → [Context Assembler] ──────────────────────────────────────────┐
            ├─ session.entities (RAM / core-memory, always in prompt)  │
            ├─ task_state (LangGraph state + checkpointer)             │
            ├─ rolling window (last N turns, full fidelity)            │
            ├─ rolling summary (LLM, refreshed at 70-80% ctx)          │
            └─ long-term recall (Mem0 / Zep Graphiti, retrieved)       │
      → LLM (turn) → coref/retraction reconcile → action/NLG → TTS ────┘
                          ↑
                 writes back to memory (entity updates, promises, corrections)
```

The **Context Assembler** is the heart of this step. It is the engineered substitute for the human's working memory, and it does the "re-inject entities into every prompt" trick that compensates for the lost-in-the-middle attention problem.

---

## 3. Tooling (concrete 2026 stack)

- **Orchestration / state machine:** LangGraph (checkpointer = short-term state persistence) or Pipecat / LiveKit Agents (per-job LLM context, STT stream, TTS buffer) for real-time voice. LiveKit/Pipecat recommended >10-50K min/month, <500ms latency, audit trails [sourced].
- **Working-memory layer:** Letta (MemGPT) core-memory blocks for "always-in-context" entities; LangMem for summary compression.
- **Long-term / temporal memory:** **Zep (Graphiti)** temporal KG (best for corrections/recency — dual timelines, invalid-node detection) OR **Mem0** (best token efficiency: ~1.8K tokens/query vs 26K full-context).
- **STT (India):** Deepgram **Flux** (acoustic+semantic turn detection) for English; **Sarvam / AI4Bharat IndicConformer-600M-multilingual** (22 Indian languages) and code-switch-tuned models for Hinglish/regional.
- **Turn detection:** Deepgram Flux semantic EOT + Silero VAD (kept for barge-in) [sourced].
- **Fast extractors:** Claude Haiku 4.5 / GPT-4o-mini / Gemini Flash for per-turn entity + fact extraction (cheap, <300ms).
- **Reasoning LLM:** Claude Sonnet / GPT-4.1 / Gemini 2.5 class for the dialogue turn.
- **Vector store / KG store:** Postgres+pgvector or Neo4j (Graphiti backend).
- **Eval/observability:** Hamming AI (voice regression + barge-in metrics), Confident AI / DeepEval (multi-turn eval), LangSmith traces.

---

## 4. Benchmarks (real numbers)

| Metric | Value | Tag |
|---|---|---|
| Multi-turn accuracy drop vs single-turn (all models) | **−39% average** | [sourced — ICLR 2026 "LLMs Get Lost In Multi-Turn Conversation", beam.ai/iclr-2026] |
| Mid-turn citation rate ("lost in the middle") | **<20%** of middle-turn info attended | [sourced — same] |
| Mem0 LOCOMO accuracy | **92.5**; +26% vs OpenAI built-in memory | [sourced — mem0.ai] |
| Mem0 LongMemEval | **94.4** | [sourced — mem0.ai] |
| Mem0 token use / query | **~1.8K** vs 26K full-context (−90%); p95 latency **1.44s vs 17.12s** (−91%) | [sourced — mem0.ai research] |
| Zep LongMemEval | **63.8%** (industry-leading); DMR 94.8% (GPT-4 Turbo) / 98.2% (GPT-4o-mini) | [sourced — getzep / weavai 2026] |
| Zep reasoning accuracy uplift vs full-context | **up to +18.5%**; latency −90% | [sourced — getzep] |
| Deepgram Nova-3 WER | **6.84%** (English real-time) | [sourced — hamming.ai] |
| STT partial-transcript latency | **<100ms** streaming; ~200ms full utterance | [sourced — hamming.ai] |
| Code-switch WER penalty (Hinglish vs monolingual) | **+30–50% relative WER** | [sourced — arXiv 2507.07741] |
| Production barge-in recovery target | **>90%**; P95 e2e latency **<5s** (sub-500ms for premium) | [sourced — futureagi / hamming] |
| Structured distillation token reduction (personalized memory) | **11×** with retrieval preserved | [sourced — arXiv 2603.13017] |
| Whole-call state-retention accuracy for a tuned voice agent | **~85-92%** on load-bearing entities over 8-12 min calls | [estimate — extrapolated from LOCOMO/LongMemEval + +30-50% Hinglish WER drag] |

---

## 5. Failure modes (where the agent breaks)

1. **Lost-in-the-middle** — facts disclosed in the middle of a long call (DOB at min 3) are under-attended; agent re-asks or acts on a stale value [sourced, <20% mid-turn citation].
2. **Correction not propagated** — caller corrects ₹12,400 → ₹14,200; LLM keeps the old number in a downstream computation because the retraction wasn't reconciled into the action layer.
3. **Co-reference collapse across code-switch** — "uska naam" after an English sentence binds to the wrong entity; Hinglish deixis is genuinely under-served by current coref.
4. **ASR error poisons memory** — +30-50% Hinglish WER means a misheard name/amount is *confidently stored* and re-injected every turn, compounding the error ("garbage in, persistently out").
5. **Summary lossiness** — at 70-80% context, summarization drops a load-bearing detail that seemed minor (a promise, a third party).
6. **Topic bleed** — two jobs in one call cross-contaminate (the wife's policy update leaks into the husband's loan query) when namespaces aren't separated.
7. **Emotional amnesia / Style Amnesia** — agent re-apologizes or loses register/empathy over turns (arXiv 2512.23578 "Style Amnesia") — sounds robotic, re-triggers anger.
8. **Barge-in desync** — interruption mid-TTS leaves partial state; agent resumes from the wrong point or repeats a prompt.
9. **Memory-write latency in voice** — synchronous memory writes blow the sub-500ms turn budget; async writes risk a read-before-write race (next turn reads stale state).
10. **Recency vs authority confusion** — agent treats a casual later aside as superseding a deliberate earlier fact.

---

## 6. Gap to full adaptation (what the agent STILL can't do as well as a human — and how to close it)

**The residual gaps:**

- **G1 — Implicit, never-stated context.** Humans infer the unsaid ("he's calling about *his* policy because he authenticated as himself; 'the form' = the one I just mentioned"). Agents need it slotted. *Close it:* train a **pragmatic-inference layer** (a small fine-tuned model on Indian-call transcripts) that proposes implicit bindings with confidence; gate low-confidence bindings behind a one-line confirm.
- **G2 — Robust Hinglish/regional co-reference & deixis.** No 2026 model resolves mixed-script deixis at human level. *Close it:* build a **code-switch coref dataset** from real (consented, redacted) BPO calls; fine-tune an Indic coref head (AI4Bharat base); eval on a held-out Hinglish deixis set. This is the single highest-leverage data investment for this step.
- **G3 — ASR-error-resilient memory.** Humans self-correct mis-hearings from context ("did you say Sunita or Suneeta?"). *Close it:* store entities with **ASR confidence + n-best alternates**; a verification policy re-confirms low-confidence load-bearing entities (names, amounts, account numbers) once, and never re-confirms high-confidence ones (preserves the "don't re-ask" virtue).
- **G4 — Graceful salience under noise.** Humans effortlessly know what to forget. *Close it:* salience-gated extraction (arXiv 2601.04463) tuned on labeled "load-bearing vs noise" call spans; eval = recall of load-bearing facts at fixed memory budget.
- **G5 — Seamless real-time write-back.** Humans update working memory at zero latency. *Close it:* **async double-buffered memory** — optimistic in-RAM session object updated synchronously (sub-ms), durable store written async; reconcile on next turn. Removes the latency/staleness tradeoff.
- **G6 — Cross-turn emotional continuity.** *Close it:* persist a `relationship_state` field (apologies_made, anger_peak, rapport) and condition NLG on it; eval against "Style Amnesia" regression.

**The path is data + architecture, not a bigger model.** A larger context window does NOT fix this (the −39% drop persists *with* large windows). The fix is the engineered memory stack + Indic fine-tuning + confidence-gated confirmation.

---

## 7. HITL trigger (when a human MUST take over for THIS step)

- **Memory-conflict with no recency resolution** — two load-bearing facts conflict and the agent can't determine authority (e.g., two different account numbers both high-confidence).
- **Low-confidence binding on a regulated/irreversible action** — a coref/entity binding feeding a fund transfer, policy surrender, or PII update falls below threshold after one confirm attempt.
- **Repeated re-ask detected** — if the agent re-asks the same slot ≥2× (memory clearly broken), auto-escalate; this is a hard CSAT cliff.
- **Topic count > 3 in one call** with cross-contamination signal — escalate to human who can hold parallel threads.
- **Transfer/handoff** — the *summary* is auto-generated, but a human owns the receiving end.

Otherwise: **not fully human-free, but human-supervised-by-exception.** The step runs autonomously and pulls a human only on the triggers above.

---

## 8. Automation readiness: **7 / 10**

The core machinery (session object, entity re-injection, temporal KG corrections, summary compression) is **production-proven** with strong benchmarks (Mem0/Zep). Vector/temporal memory + slot-filling for *clean, single-topic, English-leaning* calls is genuinely ship-ready (8-9/10). The −2 to −3 points come from: (a) the −39% multi-turn cliff that still bites on long, messy calls; (b) Hinglish/regional coref + ASR-error poisoning (G2/G3) which materially degrades Indian-call state retention; (c) real-time write-back latency engineering. **Not a 9 until G2 (Indic coref data) + G3 (ASR-confidence memory) are built and evaluated.**

---

## 9. Build spec (what to implement + data + gating eval)

**Implement:**
1. **Session State Object** (typed): `caller_id, primary_intent, entities{name,type,value,confidence,nbest,valid_at}, open_promises[], task_state, relationship_state, topic_threads[]`.
2. **Context Assembler** that, every turn, builds the prompt as: `[pinned entities + task_state]` (head) → `[rolling summary]` → `[last N full turns]` → `[retrieved long-term]`. Entities pinned at prompt head (primacy) AND restated near the query (recency) to beat lost-in-the-middle.
3. **Per-turn extractor** (Haiku-class): emits entity deltas, detected corrections, new promises, sentiment.
4. **Reconciler:** applies corrections via temporal-KG invalidation; resolves coref to canonical IDs before the action layer.
5. **Confidence-gated confirm policy** for load-bearing entities (names/amounts/account/PII).
6. **Async double-buffered write-back** (RAM sync, durable async).
7. **Memory namespaces** per topic-thread under one caller.

**Data needed:**
- 500-1,000+ **real (consented, DPDP-redacted) Indian BPO call transcripts**, multi-turn (8-15 min), labeled for: entity register ground-truth, co-reference chains (incl. Hinglish deixis), corrections/retractions, open promises, topic boundaries, load-bearing-vs-noise spans.
- A held-out **Hinglish deixis/coref eval set** (the gating set).
- ASR n-best logs paired with verified ground truth (for G3).

**Gating eval metric ("good enough to ship"):**
- **Whole-call State-Retention F1 ≥ 0.92** on load-bearing entities across 8-12 min calls (precision = no wrong values; recall = nothing dropped).
- **Correction-propagation accuracy ≥ 0.98** (a corrected value must never feed a downstream action).
- **Re-ask rate ≤ 2%** of already-answered slots.
- **Hinglish coref accuracy ≥ 0.88** on the held-out deixis set.
- **No load-bearing fact below confidence threshold reaches a regulated action without a confirm** (hard pass/fail, 100%).
- **Turn-level p95 added latency from memory < 150ms** (within voice budget).

Ship gate = all six green on a 100-call shadow-mode regression run (Hamming AI / DeepEval multi-turn).

---

## 10. India specifics (Hinglish / regional / regulatory)

- **Code-switch is the default, not the exception.** ~250M Indians code-switch; Hinglish blends mid-sentence. ASR WER rises **+30-50% relative** on code-switched speech [sourced]. Memory built on noisy ASR inherits and *persists* the error — making ASR-confidence-aware memory (G3) non-optional for India.
- **Deixis is harder in Hindi/Hinglish.** "woh / uska / yeh / wahi / pehle wala" carry referential load and frequently cross the language boundary ("update kar do *that one*"). Generic English coref fails here — needs Indic-tuned coref (G2).
- **Honorifics & relationship terms as entities.** "saheb ki policy", "missus ka account", "bhaiya ne bola tha" — kinship/honorific tokens must resolve to concrete entities and persist.
- **Stack choices:** AI4Bharat **IndicConformer-600M** (22 languages, real-time-capable) and Sarvam for STT; pair with Deepgram Flux for English-heavy segments. Multi-language voice agents in 2026 structure prompts + fallbacks per-language [sourced, AlterSquare 8-language architecture].
- **DPDP Act compliance for memory:** working/long-term memory *is* personal-data processing. Need **purpose limitation** (memory used only for the stated call purpose), **storage limitation** (TTL on call memory; don't silently persist PII forever), **consent** for any cross-call memory, **data-principal rights** (erasure must purge the memory store too), and **redaction** of PII in any stored summary/transcript used for training.
- **RBI/IRDAI:** mandatory disclosure scripts and verification steps are *dialogue-act state* that must be tracked exactly (the agent must KNOW it has/hasn't read the disclosure, captured consent, completed KYC step) — a state-machine obligation, auditable. Memory of "which regulated step is done" must be tamper-evident for audit.
- **Recency-authority nuance:** Indian callers often think aloud and self-correct ("12,400... nahi nahi 14,200"); the retraction-handling (micro-step 6 / Graphiti invalidation) is exercised *constantly*, not rarely.

---

## Sources

- [LLMs Lose 39% Accuracy in Multi-Turn Conversations — ICLR 2026 (beam.ai)](https://beam.ai/agentic-insights/iclr-2026-llms-lose-accuracy-in-multi-turn-conversations)
- [Multi-Turn LLM Evaluation in 2026 — Confident AI](https://www.confident-ai.com/blog/multi-turn-llm-evaluation-in-2026)
- [Beyond Single-Turn: A Survey on Multi-Turn Interactions with LLMs (arXiv 2504.04717)](https://arxiv.org/pdf/2504.04717)
- [The voice AI stack for building agents in 2026 — AssemblyAI](https://www.assemblyai.com/blog/the-voice-ai-stack-for-building-agents)
- [Best AI Agent Memory Frameworks in 2026 — Atlan](https://atlan.com/know/best-ai-agent-memory-frameworks-2026/)
- [Mem0 vs Letta (MemGPT) — Vectorize](https://vectorize.io/articles/mem0-vs-letta)
- [State of AI Agent Memory 2026 — Mem0](https://mem0.ai/blog/state-of-ai-agent-memory-2026)
- [AI Memory Benchmarks 2026: LoCoMo, LongMemEval & BEAM — Mem0](https://mem0.ai/blog/ai-memory-benchmarks-in-2026)
- [Zep: A Temporal Knowledge Graph Architecture for Agent Memory (arXiv 2501.13956)](https://arxiv.org/abs/2501.13956)
- [Zep 2026 Review — WeavAI](https://weavai.app/blog/en/2026/05/09/zep-2026-review-ai-agent-temporal-memory-king/)
- [Best Voice Agent Stack — Hamming AI](https://hamming.ai/resources/best-voice-agent-stack)
- [Introducing Flux: Conversational Speech Recognition — Deepgram](https://deepgram.com/learn/introducing-flux-conversational-speech-recognition)
- [Voice AI Barge-In and Turn-Taking: 2026 Guide — FutureAGI](https://futureagi.com/blog/voice-ai-barge-in-turn-taking-2026/)
- [Code-Switching in End-to-End ASR: Systematic Review (arXiv 2507.07741)](https://arxiv.org/pdf/2507.07741)
- [ai4bharat/indic-conformer-600m-multilingual — Hugging Face](https://huggingface.co/ai4bharat/indic-conformer-600m-multilingual)
- [Proactive Memory Extraction for LLM Agents (arXiv 2601.04463)](https://arxiv.org/pdf/2601.04463)
- [Structured Distillation for Personalized Agent Memory: 11x Token Reduction (arXiv 2603.13017)](https://arxiv.org/pdf/2603.13017)
- [Style Amnesia in Multi-Turn Spoken Language Models (arXiv 2512.23578)](https://arxiv.org/pdf/2512.23578)
- [Convergence of Schema-Guided Dialogue & MCP (arXiv 2602.18764)](https://arxiv.org/pdf/2602.18764)
- [Multi-Language Voice Agent Architecture across 8 Languages — AlterSquare](https://altersquare.medium.com/multi-language-voice-agent-architecture-how-we-structure-prompts-and-fallbacks-across-8-languages-4be688ec2a7e)

---
*Draft research note for review. Cited where possible; [estimate] elsewhere. Not investment advice.*
