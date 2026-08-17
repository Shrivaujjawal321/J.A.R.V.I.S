# Step A01 — Call Routing & Context Load
### (CTI screen-pop · who is calling & why · history pull)

**Domain:** India-market, multilingual (Hindi + regional + Hinglish), RBI/IRDAI/DPDP-compliant, action-taking voice+chat contact-center agent for mid-market BPOs.
**Scope of this dossier:** ONLY the "front door" of every interaction — the 0–8 seconds between a call/chat landing and the agent having full context. Everything downstream (greeting, intent handling, resolution) is OUT of scope.
**Date:** 2026-06-24

---

## 0. Why this step matters (first principles)

This is the **identity + context resolution layer**. Before a single word is exchanged, a skilled human agent has silently answered four questions:

1. **WHO** is this (account match, confidence, is it really them)?
2. **WHY** are they likely calling (predicted intent from history + IVR path + recency)?
3. **WHAT** do I need on screen (the 3–5 facts that will actually matter)?
4. **HOW risky** is this (fraud, deepfake, VIP, vulnerable, compliance flag)?

Get this wrong and *everything* downstream is wrong: wrong language, wrong account, wrong tone, a customer who has to repeat themselves, or — worst — data leaked to an impostor. In a voice agent this step is **pre-turn**: it must complete during the ring / first 1–2 seconds of audio, because the agent's very first sentence ("Namaste Rahul ji, aapke October ke payment ke baare mein?") is the payoff of getting it right.

For a BPO, this step is also the **AHT lever** (industry: context auto-load + AI summary saves 15–30s/call [sourced: Five9/CCpro 2026 guides]) and the **compliance gate** (DPDP purpose-limitation + RBI/IRDAI authentication happen here, not later).

---

## 1. Human micro-steps (the atomic decomposition — the core ask)

A skilled BPO agent does the following in ~3–6 seconds, mostly subconsciously:

| # | Micro-step | Type | What's actually happening in the human's head |
|---|-----------|------|----------------------------------------------|
| 1 | **Read the ANI / DNIS / IVR path off the soft-phone before answering** | mechanical+cognitive | "Number is +9198…, came in on the *credit-card collections* queue, picked option 2 = dispute. So this is probably a dispute, not a payment." |
| 2 | **Glance the screen-pop & confirm it loaded the right record** | mechanical | Eyes jump to name + last-4 of account; "did CTI pop the right person or a household-shared number?" |
| 3 | **Resolve identity ambiguity** | judgment | Number maps to 2 accounts (joint card / family plan) — pick the likely one or hold both. Or no-match → mentally switch to "cold" script. |
| 4 | **Form a why-hypothesis** | predictive | Cross-reference: open ticket? failed payment 2 days ago? last call's unresolved promise? recent SMS/email? → "90% this is about the EMI bounce." |
| 5 | **Scan history for the 3 facts that matter** | prioritization | Not the whole 360 — just: balance/status, last interaction outcome, any open promise/complaint, sentiment of last call. |
| 6 | **Detect VIP / vulnerable / repeat-caller flags** | judgment+emotional | "5th call this week → frustrated, escalate-prone. Be soft." Or "Priority/HNI tag → white-glove." |
| 7 | **Decide language register before speaking** | judgment | From past-interaction language tag + region of number + name → "open in Hindi, mirror to Hinglish if they code-switch." |
| 8 | **Smell-test for fraud / wrong-person** | judgment+emotional | Voice doesn't match expected age/gender on file; caller "fishing" for info; agitation pattern → raise auth bar mentally. |
| 9 | **Pre-load the likely tool/workflow** | mechanical | Open the dispute form / payment screen *before* the customer asks, so resolution is instant. |
| 10 | **Set the auth level required** | compliance judgment | "This is a balance query → 2-factor enough. They'll want a fund transfer → full KYC + OTP." (RBI/IRDAI graduated auth.) |
| 11 | **Carry forward cross-channel state** | cognitive | "They WhatsApp'd us an hour ago and abandoned — continue that thread, don't restart." |
| 12 | **Discard noise / suppress wrong-pop** | judgment | Screen-popped record is stale or clearly wrong → ignore it and start clean rather than be misled. |

The genius of the human is steps 4, 6, 7, 8 — **probabilistic intent + risk + register inference from sparse, messy signals**, done in parallel with zero latency budget. Steps 1, 2, 5, 9 are mechanical and already automatable.

---

## 2. Agent approach — how a 2026 AI agent does each micro-step

The 2026 pattern is a **pre-turn context-assembly pipeline** that runs during ring/SIP-INVITE and the first 1–2s of audio, feeding a context object into the LLM's system prompt *before* it speaks. Architecture: an **orchestrator** (LangGraph / Pipecat flow) firing **parallel tool calls** (MCP/function-calling), with a **predictive-prefetch RAG layer** (Salesforce VoiceAgentRAG dual-agent pattern) so context retrieval doesn't blow the 200ms voice budget.

| Human µ-step | Agent technique (named) |
|---|---|
| 1. ANI/DNIS/IVR read | **SIP/CTI metadata extraction** at INVITE: ANI, DNIS, SIP headers, IVR-path variables passed as a structured context token from the ACD (Exotel/Ozonetel/Twilio/Genesys). Deterministic, no model. |
| 2. Confirm record | **Deterministic CRM lookup** by ANI → CRM API / Data 360 (`Customer.find(phone)`). Returns 0/1/N matches with a confidence field. |
| 3. Identity ambiguity | **Entity-resolution / identity-graph** query (Pindrop ANI-Validation–style or in-house). On N-match → disambiguation policy: hold candidate set, resolve via first-utterance name/DOB or voice-biometric speaker-ID. |
| 4. Why-hypothesis | **Next-best-intent prediction**: (a) feature-rule layer (open ticket, T-2 failed payment, last-call unresolved) + (b) a small classifier / LLM (GPT-5-nano / Gemini-3-Flash) over a compact "recent-events" prompt → ranked intent distribution. |
| 5. 3 facts that matter | **VoiceAgentRAG "Slow Thinker" prefetch** + a **context-summarizer** (Haiku-4.5/Gemini-Flash) that compresses 360 → a 4–6 line "what you need to know" card. Salience ranking, not full dump. |
| 6. VIP/vulnerable/repeat flags | **Feature flags from CRM/CDP** + a churn/frustration model over interaction history (call count last 7d, last sentiment, NPS). Deterministic thresholds + model score. |
| 7. Language register | **Language-preference resolution**: stored `preferred_language` tag → fallback to LID (language-ID) from first 1–2s audio (Sarvam/Gnani Prisma) + region-from-ANI prior. Sets ASR/TTS locale + system-prompt register. |
| 8. Fraud smell-test | **Pindrop Phoneprinting / ANI-Validation risk score** (1,300+ acoustic features) + **deepfake/synthetic-speech detection** + **voice biometric speaker verification** (Gnani Armour365/Inya Shield). Returns risk score → gates auth level. |
| 9. Pre-load workflow | **Speculative tool-warming**: orchestrator pre-instantiates the predicted workflow's tools/forms based on µ-step 4's top intent (MCP tool pre-bind). |
| 10. Auth level | **Policy engine / rules-as-code** (OPA-style or a decision table): intent class + risk score + requested-action sensitivity → required auth tier (RBI/IRDAI graduated auth). |
| 11. Cross-channel state | **Unified session memory** (Sarvam Samvaad / Decagon cross-channel memory; or a session store keyed on customer_id) → pull last N events across voice/WA/web/chat. |
| 12. Suppress wrong-pop | **Confidence gating**: if match confidence < τ or staleness > threshold, do NOT inject the record into the prompt; treat as cold + verify. Prevents hallucinated personalization. |

**Key 2026 design move:** assemble a single typed **`CallContext` object** (Pydantic) and inject it as a *grounded* system-prompt block. The LLM never *infers* who's calling — it's *told*, with confidence scores, and instructed to verify before acting on anything sensitive.

---

## 3. Tooling — concrete 2026 stack

**Telephony / CTI / SIP layer (India):**
- Exotel, Ozonetel CloudAgent, Knowlarity, Twilio (Programmable Voice + SIP), Genesys Cloud CX, Amazon Connect. These expose ANI/DNIS/IVR-path as call variables / SIP headers and a screen-pop/CTI event.
- For India-native: **Exotel/Ozonetel** are the default mid-market BPO CPaaS; both integrate with Gnani/Sarvam.

**Voice runtime / orchestration:**
- **Pipecat** or **LiveKit Agents** (real-time pipeline, barge-in, full-duplex), or **Vapi** / **Retell** as managed.
- **LangGraph** for the pre-turn context-assembly state machine (parallel tool nodes, conditional auth branch).

**ASR / TTS / LID (Indic):**
- **Sarvam** (Samvaad, 11 Indian languages, sub-500ms) [sourced], **Gnani Prisma v2.5** ASR (claims >Sarvam accuracy, 40+ langs, code-switch-trained) [sourced], **Google Chirp/Gemini Live 3.1**, **ElevenLabs** TTS for fallback.

**Reasoning / classification models:**
- Intent/why-prediction & summarization: **GPT-5-nano**, **Gemini 3 Flash** (~1.35s TTFT) [sourced], **Claude Haiku 4.5** — small/fast, not the conversational brain.
- Conversational brain (downstream): GPT-realtime-1.5 (0.82s S2S TTFT) / Gemini 3.1 Flash Live / Nova 2 Sonic [sourced].

**Context retrieval:**
- **Salesforce VoiceAgentRAG** dual-agent memory router (Fast Talker + Slow Thinker), Qdrant/Pinecone vector DB, OpenAI `text-embedding-3-small`/3-large or Cohere multilingual embeddings for Indic [sourced].
- **MCP (Model Context Protocol)** tools wrapping CRM (Salesforce Data 360 "Headless 360", Zoho, LeadSquared, in-house core-banking/policy-admin APIs).

**Identity / fraud / biometrics:**
- **Pindrop** (Phoneprinting, ANI Validation, Continuous Scoring, deepfake detection — 80% fraud detection @ <0.5% FP [sourced]).
- **Gnani Armour365 / Inya Shield** (India voice biometrics, BFSI) [sourced].
- In-house identity-graph for ANI→account entity resolution.

**Policy / compliance:**
- **OPA (Open Policy Agent)** or a decision-table service for graduated-auth rules (RBI/IRDAI).
- Consent ledger / DPDP consent-manager integration (DPDP Phase II consent-manager regime, effective Nov 2026).

**Glue:** Pydantic v2 `CallContext` schema, Redis for session/cross-channel state, OpenTelemetry for per-stage latency tracing.

---

## 4. Benchmarks (real numbers)

| Metric | Value | Source |
|---|---|---|
| Intent-recognition accuracy on support queries (modern AI agents) | **92%** | 2026 industry benchmarks [sourced — Medium/Voiso, CCpro 2026 guides] |
| Screen-pop / CRM context push target | **≤ 2s** (route+pop within 700ms of intent classification in tested impls) | [sourced — Five9/Voiso 2026] |
| AHT reduction from context auto-load + AI summary | **15–30s/call** | [sourced — 2026 CC stack guides] |
| VoiceAgentRAG retrieval latency (cache hit) | **0.35ms** (110ms→0.35ms, 316× speedup) | [sourced — Salesforce/MarkTechPost 2026] |
| VoiceAgentRAG cache hit rate | **75% avg, 95% best, 45% worst** | [sourced — arXiv 2603.02206] |
| Voice response budget for "natural" feel | **~200ms** | [sourced — VoiceAgentRAG] |
| Indic voice agent end-to-end latency (Sarvam Samvaad) | **sub-500ms** | [sourced — Sarvam] |
| S2S TTFT range (frontier voice models, Apr 2026) | **0.78s (Grok) – 2.98s (Gemini 3.1 Flash Live)**; gpt-realtime-1.5 0.82s; Nova 2 Sonic 1.14s | [sourced — softcery/Coval 2026] |
| Voice-biometric auth time vs manual KBA | **<5s vs 45–60s** | [sourced — Gnani/TruthScan 2026] |
| Pindrop fraud detection rate / false-positive | **80% / <0.5% FP**; Continuous Scoring +22% fraud @ 90% accuracy | [sourced — Pindrop 2026] |
| Deepfake fraud-attempt increase (drives auth need) | **+1,300%** | [sourced — TruthScan 2026] |
| Identity-resolution accuracy (ANI→account, clean) | **~95–98%** [estimate, deterministic match on registered number] | [estimate] |
| ANI→account on shared/family numbers | **drops to ~60–75%** [estimate] — major failure surface | [estimate] |

---

## 5. Failure modes (where the agent breaks)

1. **ANI is spoofed or absent.** India has **not** fully implemented STIR/SHAKEN [sourced] — caller-ID authentication at carrier level is weak. ANI is more reliable than caller-ID but **ANI matching without ANI-validation can bind a spoofed number to a real account** [sourced — Pindrop]. → confident wrong-pop = data leak.
2. **Shared / family / business numbers.** One ANI → many people. Agent pops the account-holder, but the caller is the spouse/son. Personalizing ("Namaste Rahul ji") to the wrong human is a DPDP + trust failure.
3. **No-match (new SIM, ported number, withheld CLI, calling from a friend's phone).** ~10–20% of inbound. Predictive intent has nothing to work with → cold-start.
4. **Stale / conflicting CRM.** Mid-market BPOs run fragmented systems (core banking + ticketing + CDP). 360 view is partial or contradictory → wrong why-hypothesis, wrong tool pre-load.
5. **Wrong language pick.** Region-of-number prior misleads (a Tamil speaker on a Delhi number). Opening in the wrong language is an instant rapport killer in India.
6. **Latency budget blown.** Cold cache (VoiceAgentRAG 45% worst-case hit rate) + a slow legacy core-banking API (2–5s) → the agent either stalls awkwardly or speaks before context arrives.
7. **Deepfake / cloned voice passes biometric.** +1,300% deepfake attempts; even 80% detection means 20% slip → fraudster gets white-glove treatment.
8. **Over-trust hallucinated personalization.** If the record is injected without confidence gating, the LLM cheerfully invents continuity ("aapke pichle complaint ke baare mein") on a wrong/stale record.
9. **DPDP purpose-limitation breach.** Pulling full history "just in case" when consent covered only a narrow purpose → up to ₹250 cr penalty exposure [sourced].
10. **Cross-channel desync.** WhatsApp thread and voice session don't share state → customer repeats themselves, the thing the human does effortlessly (µ-step 11).

---

## 6. Gap to full adaptation (what the agent STILL can't match — Boss's key concern)

The mechanical 80% (ANI read, CRM pop, summary card, flag surfacing, auth gating) is **already at or above human** in 2026 — faster, never forgets to check a flag, parallelized. The **residual 20% is the human's probabilistic, sparse-signal judgment**:

| Gap | Why agent is weaker | Concrete path to close it |
|---|---|---|
| **Why-hypothesis from thin/ambiguous signal** | Human fuses faint cues (time of day, a half-finished WhatsApp, "this customer always calls about X on payday") into a sharp prior. Agent's intent model is generic. | Train a **per-tenant next-best-intent model** on that BPO's own interaction logs (call+IVR-path+recency+outcome → realized intent). Online-learn. Eval: top-1 intent-prediction accuracy vs human-agent post-call labels. |
| **Shared-number / wrong-person disambiguation without friction** | Human softly probes ("aap Rahul ji bol rahe hain?") and reads the answer. Agent either over-asks (annoying) or assumes (dangerous). | **Adaptive disambiguation policy** tuned on confidence: a single graceful confirm utterance + voice-biometric speaker-ID to silently split household speakers. Build a household-speaker enrollment over time. |
| **Reading emotional/fraud "smell" pre-conversation** | Human senses "this feels off" from micro-cues. Agent only has explicit signals. | Fuse **acoustic risk (Pindrop) + behavioral (call velocity, navigation) + content (first-utterance evasiveness)** into a single pre-turn risk score; continuous-scoring look-back so risk updates mid-call. |
| **Knowing what NOT to load** | Human ignores the 357 irrelevant fields and the stale pop. Agent tends to dump or over-trust. | **Salience model + confidence gating**; train the summarizer on human-agent "what I actually used" labels (post-call: which facts did the resolution touch). |
| **Graceful cold-start** | Human improvises warmth on a no-match. Agent feels robotic when it has nothing. | A dedicated **cold-start persona policy** + progressive profiling that collects identity conversationally without sounding like an interrogation. |
| **Cross-system truth reconciliation** | Human knows "core banking is right, the CDP is a day stale." | A **source-of-truth priority + freshness layer** in the identity graph; per-field trust weights. |

**Bottom line:** to *fully* adapt, the differentiator is **per-tenant supervised learning on the BPO's own logs** (intent, salience, register) + **multi-signal risk fusion** + **confidence-gated grounding so the LLM never over-trusts**. None of this needs new model breakthroughs — it's a data + policy + eval-harness engineering effort. That's why this step is high on the readiness scale.

---

## 7. HITL trigger (when a human MUST take over)

This step is **assistive-first** for the human and **autonomous-with-guardrails** for a full AI agent. A human (or the AI escalating to one) MUST take over when:

- **Identity confidence below threshold AND a sensitive action is requested** (fund transfer, KYC change, policy surrender) → hard stop to verified human / step-up auth.
- **Fraud/deepfake risk score above threshold** → route to fraud desk, do not personalize, do not disclose account data.
- **N-match unresolved after one disambiguation attempt** on a sensitive line.
- **Vulnerable-customer or distress flag** + high-stakes context (collections, grievance) — RBI/IRDAI fair-practice + reputational.
- **CRM systems down / context-load failed** → degrade gracefully to human rather than fly blind.
- **DPDP consent missing for the data the workflow would need** → cannot pull history; human handles with explicit consent capture.

For *low-risk read-only intents* (balance, status, store hours) with high identity confidence → **none, fully automatable**.

---

## 8. Automation readiness: **8 / 10**

Rationale: The mechanical core (ANI/DNIS read, CRM pop, summary card, flag surfacing, language preference, auth gating) is **production-proven and at/above human speed** today. Intent prediction at 92% [sourced] and sub-2s context push [sourced] are real. The 2-point gap is the residual judgment (shared-number disambiguation, fraud-smell, thin-signal why-inference, cold-start grace) and the brittle India infra reality (no STIR/SHAKEN → spoofable ANI, fragmented mid-market CRMs). Those are **data/policy engineering gaps, not capability gaps** — which is exactly why this scores high. With per-tenant tuning + confidence gating it reaches 9.

---

## 9. Build spec (what to implement, data, eval gate)

**Implement:**
1. **`CallContext` assembler** (LangGraph pre-turn graph): parallel nodes — `sip_meta` → `crm_lookup` → `identity_resolve` → `risk_score` → `intent_predict` → `context_summarize` → `auth_policy` → emit typed Pydantic object.
2. **Identity-graph service**: ANI → {account candidates, confidence, household flag}; integrates Pindrop/Gnani risk score.
3. **Next-best-intent model** (per-tenant): inputs = ANI, DNIS, IVR-path, last-N events, recency features → intent distribution.
4. **Context summarizer** (Haiku/Flash): 360 → ≤6-line salience card, confidence-gated injection.
5. **Auth-policy decision table** (OPA): (intent, risk, action-sensitivity) → auth tier, mapped to RBI/IRDAI.
6. **VoiceAgentRAG prefetch layer** for any unstructured knowledge needed.
7. **Confidence gate**: suppress record injection if match-confidence < τ or staleness > T.

**Data needed:**
- Historical call logs with: ANI, IVR-path, timestamp, realized intent (post-call label), resolution facts touched, final language, fraud outcome.
- CRM/CDP/core-banking API access (read), identity/household mappings.
- Voice-biometric enrollments (consented) for speaker-ID.
- Labeled fraud/no-fraud calls for risk-model calibration.

**Eval metrics that gate "good enough to ship":**
- **Identity precision ≥ 99.5%** on sensitive-action paths (wrong-person on a transaction is unacceptable); recall ≥ 95% on clean numbers.
- **Wrong-pop / wrong-personalization rate ≤ 0.5%** (mirrors Pindrop FP bar).
- **Next-best-intent top-1 ≥ human baseline** (measure vs human-agent post-call label; target ≥ 70%, stretch 80%).
- **Context-ready latency p95 ≤ 1.5s** (so the agent's first sentence is informed).
- **Summary salience hit-rate ≥ 90%** (the facts the card surfaced are the facts the resolution used).
- **Fraud detection ≥ 80% @ FP < 0.5%** (Pindrop parity).
- **Zero DPDP purpose-limitation violations** in audit replay.

Ship gate = ALL of the above met on a held-out replay of 2–4 weeks of real tenant traffic.

---

## 10. India specifics (Hinglish / regional / regulatory)

- **No STIR/SHAKEN in India (2026).** Caller-ID is spoofable; ANI more reliable but un-validated ANI is a known leak vector [sourced]. → identity must NOT rest on ANI alone; layer voice-biometrics + knowledge/OTP. TRAI is *exploring* the framework but it's not live.
- **DPDP Act timeline:** Phase I live (Nov 2025, Board constituted); **consent-manager regime Phase II Nov 2026**; substantive obligations Phase III **May 2027** [sourced]. Purpose-limitation + granular consent are binding — **pull only the history the consented purpose covers**, not the whole 360. Penalties up to **₹250 crore** [sourced].
- **Mandatory IVR recording-consent disclosure** ("call is being recorded for X purpose; press 1 to consent") — affirmative consent captured at the front door [sourced]. The context-load step must read and honor the consent state.
- **RBI / IRDAI graduated authentication:** read-only (balance/status) = low auth; financial action / KYC / policy change = step-up (OTP + identity). Bake into the auth-policy table.
- **Language/register:** preferred-language tag is the strongest signal; fallback = LID on first 1–2s audio. **Code-switching (Hinglish) is the norm**, not an edge case — Gnani Prisma v2.5 and Sarvam are **trained on code-switched Indic audio** [sourced]. Register decision must support "open in Hindi, mirror to English on code-switch."
- **Regional priors from number series are weak** (heavy porting, migration) — use as a tiebreaker only, never as the primary language decision.
- **Shared-number reality is higher in India** (family plans, kirana/SME numbers, one phone per household) → household disambiguation matters more here than in Western markets.
- **India-native vendors to build on:** Sarvam (Samvaad, sovereign, 11 langs), Gnani (Inya/Armour365/Assist365, BFSI biometrics, 30M+ daily convos [sourced]), Exotel/Ozonetel CPaaS, Caller Digital (TRAI/DPDP-compliant templates [sourced]).

---

### Sources
- Voiso / Medium — 2026 Contact Center Tech Stack: https://medium.com/@voiso/contact-center-technology-stack-e2825b906db3
- CCpro — Contact Center CTI 2026: https://ccproconsulting.com/contact-center-cti-computer-telephony-integration/
- Five9 CTI / Screen Pop: https://www.five9.com/products/capabilities/inbound/cti-computer-telephony-integration
- Salesforce VoiceAgentRAG (MarkTechPost): https://www.marktechpost.com/2026/03/30/salesforce-ai-research-releases-voiceagentrag-a-dual-agent-memory-router-that-cuts-voice-rag-retrieval-latency-by-316x/
- VoiceAgentRAG paper: https://arxiv.org/html/2603.02206v2
- Softcery — Best LLMs for Voice Agents 2026: https://softcery.com/lab/ai-voice-agents-choosing-the-right-llm
- Coval — Voice AI Models 2026: https://www.coval.ai/blog/voice-ai-models-2026/
- Sarvam Samvaad: https://www.sarvam.ai/products/conversational-agents
- Gnani Prisma v2.5 (Medianama): https://www.medianama.com/2026/06/223-gnani-ai-prisma-v2-5-speech-recognition-model-better-accuracy-sarvam/
- Caller Digital — Top 10 Voice AI Agents India 2026: https://caller.digital/blog/top-10-voice-ai-agents-india-2026
- Pindrop — fraud / ANI validation / continuous scoring: https://www.pindrop.com/article/continuous-scoring-fraud-look-back/ , https://www.pindrop.com/blog/ani-validation-fixing-the-game-of-telephone
- TruthScan — 2026 Caller Authentication Guide: https://truthscan.com/blog/caller-authentication/
- Gistly — DPDP Act Compliance for Contact Centers: https://www.gistly.ai/blog/dpdp-act-compliance-contact-centers
- EY — DPDP Act 2023 + Rules 2025 timeline: https://www.ey.com/en_in/insights/cybersecurity/decoding-the-digital-personal-data-protection-act-2023
- ClearTouch — India call recording compliance: https://www.cleartouch.in/blog/call-center-audio-recording-legal-requirements-in-india/
- STIR/SHAKEN status (ESET / Wikipedia): https://en.wikipedia.org/wiki/STIR/SHAKEN
- 8x8 inbound call flow / screen-pop: https://docs.8x8.com/8x8WebHelp/contact-center/agent-workspace/Content/inbound-phone-call-flow.htm
- Novelvox — Customer identification & authentication guide: https://www.novelvox.com/guides/customer-identification-and-authentication/

*Draft research note for review. Cited where possible; [estimate] elsewhere. Not investment advice.*
