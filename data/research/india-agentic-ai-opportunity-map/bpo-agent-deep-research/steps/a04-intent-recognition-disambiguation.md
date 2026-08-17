# Step A04 — Intent Recognition & Disambiguation
### (figuring out the REAL ask under a vague request)

> Deep-research dossier for the India-market, multilingual (Hindi + regional + Hinglish), RBI/IRDAI/DPDP-compliant, action-taking voice+chat contact-center agent for mid-market BPOs.
> Scope: ONLY the intent-recognition + disambiguation micro-step. Engineer-buildable.
> Date: 2026-06-24. Status: Draft research note for review. Cited where possible; [UNSOURCED]/[estimate] elsewhere. Not investment advice.

---

## 0. Why this step is the spine of the whole agent

Every downstream action — slot-filling, tool calls, RBI/IRDAI-mandated disclosures, escalation — is conditioned on **getting the intent right**. Infra dashboards can be green while customers abandon because the agent misclassified intent or lost dialog state ([sourced: AssemblyAI / Retell voice-agent architecture posts, 2026]). The hardest part is not classifying a clean utterance; it is recovering the **real ask under a vague, emotional, code-mixed, half-spoken request** ("mera paisa atak gaya", "wo wala kaam nahi hua", "EMI ka kuch problem hai") — and deciding, in <1s, whether to **commit, clarify, or hand off**.

This step has a critical regulated nuance: **"I want to know about my loan" ≠ "I want to pay my loan"** — the NLU layer must distinguish them reliably ([sourced: awaaz.ai domain-specific-NLU-for-financial-conversations guide, 2026]), because the second triggers a money-movement flow with RBI/DPDP obligations.

---

## 1. Human micro-steps (the atomic moves a skilled agent actually makes)

A skilled BPO agent does NOT run a classifier. They run a fast loop of perception → hypothesis → cheap test. Decomposed:

1. **Catch the literal words** — parse the surface utterance even when grammatically broken / code-mixed / disfluent ("haan wo… EMI… nahi cut hua na is baar").
2. **Strip the noise** — discard fillers, repeats, self-corrections, background chatter; keep the load-bearing tokens.
3. **Map register + emotion** — read tone (angry / panicked / confused / casual) because emotion reshapes intent priority (panic about "paisa atak gaya" = failed transaction, not a balance query).
4. **Form 2-3 candidate intents** — hold a small hypothesis set, not one guess ("could be: failed-payment-reversal, EMI-bounce, or general-EMI-info").
5. **Pull context priors** — silently weight candidates using who's calling: recent transaction, product held, last ticket, IVR path taken, time of month (1st-5th = salary/EMI window).
6. **Estimate own confidence** — gut-check "do I actually know what they want?" — the meta-cognitive move machines lack natively.
7. **Decide: commit / clarify / probe / escalate** — if confident → proceed; if 2-3 live candidates → ask ONE sharp disambiguating question; if totally lost or emotionally charged → soothe + escalate.
8. **Craft a minimal clarifying question** — not "please rephrase" but a targeted either/or that maximally splits the hypothesis set ("aapko EMI ki info chahiye ya payment karni hai?").
9. **Detect multi-intent / hidden intent** — notice the caller actually wants two things ("EMI bounce hua AUR late fee waive karwana hai") or that the stated ask masks the real one ("cancel my policy" often = "I'm angry about a charge").
10. **Re-anchor on new info** — update the hypothesis live as the caller answers, without forcing them back to a script.
11. **Confirm understanding in their words** — reflect back ("toh aap keh rahe hain ki is mahine ki EMI cut nahi hui, sahi?") before acting — the trust + safety checkpoint.
12. **Log the resolved intent + reason** — mentally tag it for the wrap-up / next agent.

The compressed essence: **hold a hypothesis set, weight it with context + emotion, know your own confidence, and ask the one question that splits it fastest.**

---

## 2. Agent approach — how a 2026 AI agent does each sub-step

| Human micro-step | 2026 agent technique |
|---|---|
| 1. Catch literal words | Streaming Indic ASR with **codemix output mode** (Sarvam **Saaras v3**, AI4Bharat **IndicConformer**) feeding **partial transcripts** to the NLU so reasoning starts on partials (speculative inference) ([sourced: Sarvam models page; AssemblyAI latency post, 2026]). |
| 2. Strip noise | LLM-native disfluency robustness + a light **normalization pass** (Hinglish transliteration → canonical form via Sarvam translit / IndicXlit). |
| 3. Map register + emotion | **Paralinguistic emotion head** on audio (prosody) + text-sentiment; speech-to-speech models (gpt-realtime-1.5, Gemini 3.1 Flash Live, Nova 2 Sonic) carry prosody natively ([sourced: softcery/Retell 2026 voice posts]). Emotion becomes a **prior weight**, not a separate output. |
| 4. Form 2-3 candidates | LLM emits a **distribution / top-k intents with calibrated scores**, NOT a single argmax. Few-shot or fine-tuned classifier over a curated taxonomy. |
| 5. Pull context priors | **RAG over the customer 360** (CRM/core-banking/policy record, last txn, last ticket) injected into the prompt; re-rank candidate intents by context. |
| 6. Estimate confidence | **Conformal prediction (CICC)** turns raw scores into a *prediction set* with statistical coverage guarantee (≥1-α) — this is the machine analog of "do I actually know?" ([sourced: Hengst & Wolter, CICC, NAACL Findings 2024]). |
| 7. Commit / clarify / escalate | **CICC decision rule**: set size 1 → commit; set size 2..th (th=7, Miller's cognitive-load limit) → clarify; set > th or empty → rephrase-request or human handoff ([sourced: CICC paper]). |
| 8. Craft clarifying question | LLM generates a **minimal disambiguating either/or** seeded by the conformal set members (so the question is grounded in the *actual* live candidates, not generic). |
| 9. Multi-intent / hidden intent | **Multi-label intent head** + an "implied-need" reasoning step; OOS/secondary-intent detection via internal-representation methods (>5% F1 gain on Mistral-7B) ([sourced: arXiv 2507.22289 / 2410.01627]). |
| 10. Re-anchor live | **Dialog-state tracking** maintained as a rolling structured state object (LangGraph / Pipecat flow state), updated each turn instead of re-classifying from scratch. |
| 11. Confirm in their words | Templated **reflective confirmation** in the caller's language/register before any Tier-2/3 action — also satisfies DPDP purpose-confirmation. |
| 12. Log intent + reason | Structured trace (intent, conformal set, confidence, chosen action, asr_confidence) to the observability layer for audit + eval. |

**Architectural pattern (recommended): hybrid cascade.**
A lightweight encoder (fine-tuned IndicBERT/MuRIL or sentence-transformer) does first-pass classification on every turn; an **uncertainty router** sends only the *uncertain* turns to a large LLM (Sarvam-30B / GPT-class) — matching full-LLM accuracy within ~2% while cutting latency ~50% ([sourced: Arora et al. 2024 hybrid; uncertainty-routing results]). This is the only way to hit voice latency budgets at BPO call volumes.

---

## 3. Tooling — concrete 2026 stack

- **ASR (Indic, codemix):** Sarvam **Saaras v3** (23 langs, codemix mode, diarization) or **AI4Bharat IndicConformer** (open, on-prem); Bhashini for govt/sovereign needs.
- **Transliteration/normalization:** Sarvam translit / **IndicXlit** (AI4Bharat) for Hinglish → Devanagari/canonical.
- **First-pass intent (cheap tier):** fine-tuned **MuRIL / IndicBERT** or sentence-transformer + linear head; or frozen-encoder + Mahalanobis prototypes (5MB state, 455 QPS, zero-forgetting class-incremental) for cheap taxonomy growth ([sourced: search result on incremental encoder].
- **Heavy tier (uncertain turns):** **Sarvam-30B / Sarvam-105B** (sovereign, India-hosted, DPDP-friendly) or GPT-class via private endpoint; chain-of-thought + adaptive in-context examples.
- **Confidence / clarify gate:** **CICC** (conformal layer) over the classifier — `mapie`-style conformal wrapper, α tuned on a held-out calibration set, th=7.
- **Speech-to-speech option (lowest latency):** gpt-realtime-1.5 / Gemini 3.1 Flash Live / Amazon Nova 2 Sonic / open Ultravox v0.7 — but verify Indic+codemix quality before trusting on the heavy tier.
- **Dialog/state + orchestration:** **Pipecat** or **LiveKit Agents** (voice), **LangGraph** for the intent→clarify→act graph; flowchart-guided / orchestration-free patterns for compliance traceability ([sourced: arXiv 2602.15377]).
- **Customer-360 RAG:** vector store + structured CRM/core-banking lookup as tool calls, injected as context priors.
- **Eval/observability:** Sarvam's **Intent Score** (LLM-judge binary: is core meaning preserved) + custom suite; voice-AI observability stack (FutureAGI-style) tracing per-turn intent, conformal set, latency.
- **Telephony/compliance:** TRAI DLT-registered SIP trunk; consent + disclosure prompt module; audit-trail logger.

---

## 4. Benchmarks (real numbers)

- **CICC conformal clarification** ([sourced: Hengst & Wolter 2024]):
  - Banking77: 98% coverage, **73% single-intent** (commit-without-asking) rate, avg clarification set 2.84.
  - CLINC150: 99% coverage, 97% single-intent, set 2.66.
  - HWU64: 95% coverage, 82% single-intent, set 2.81.
  - ATIS: 99% coverage, 98% single-intent, set 2.54.
  - Interpretation: on a hard banking taxonomy, ~27% of turns *should* trigger a clarify — confirming clarification is a first-class path, not an error.
- **IntentGPT (unsup. intent discovery):** 96.06% NMI / 84.76% ARI on CLINC150 ([sourced: IntentGPT 2024]).
- **Hybrid encoder+LLM uncertainty routing:** within **~2% of full-LLM accuracy at ~50% latency** ([sourced: Arora et al. 2024]).
- **OOS detection:** internal-representation method +>5% F1 on Mistral-7B ([sourced: arXiv 2410.01627 / 2507.22289]).
- **Few-shot human gap:** LLMs still **~30 absolute points below humans** in few-shot intent recognition ([sourced: arXiv 2410.01627]) — the core "full-adaptation" gap.
- **Voice latency budget:** good 2026 voice LLM TTFT **150–300ms**; speech-to-speech end-to-end TTFT **0.8–3s** ([sourced: softcery/Retell/AssemblyAI 2026]). Intent decision must fit inside this.
- **Hinglish in-domain intent accuracy (banking/telecom):** **~88–93%** top-1 with a fine-tuned MuRIL/IndicBERT + curated taxonomy [estimate, no clean public BPO-Hinglish benchmark exists].

---

## 5. Failure modes

- **Codemix ASR error cascades** — wrong transliteration ("EMI" vs "MI", "loan" vs "lon") flips intent before NLU sees it; ASR confidence must gate NLU.
- **Taxonomy granularity trap** — OOS/clarify quality depends heavily on label scope & granularity; too coarse → wrong commits, too fine → endless clarifying ([sourced: arXiv 2410.01627]).
- **Emotion-blind misprioritization** — treating a panicked "paisa atak gaya" as a calm balance query.
- **Hidden/secondary intent miss** — caller says "cancel policy", real ask is "waive this charge"; single-label heads miss it.
- **Over-clarifying** — asking when a confident human would just act; kills CSAT and AHT.
- **Calibration drift** — conformal α calibrated on old data degrades as new products/intents appear (concept drift, festive/EMI-cycle spikes).
- **Long-tail novel intents** — utterances outside the taxonomy silently coerced into the nearest wrong bucket.
- **Regional-language code-switch (Tamil/Telugu/Marathi + English)** — far thinner training data than Hindi-English; accuracy drops.
- **Multi-party / crosstalk** (family member speaking) — diarization failure corrupts intent ([sourced: Sarvam diarization note]).
- **Ambiguity that's genuinely unresolvable by text** — needs a human's world knowledge ("the thing I called about last week").

---

## 6. Gap to full adaptation (what the agent still can't match — and how to close it)

**The residual human edge:**
1. **Meta-cognitive confidence on novel/garbled asks** — humans *know when they don't know* even off-distribution; conformal coverage guarantees break under distribution shift.
2. **Inferring unstated intent from sparse cues** — a human bridges "wo wala kaam" to the right ticket using world + relationship knowledge; ~30pt few-shot gap is exactly this.
3. **Emotion→intent reprioritization** with full social nuance.
4. **Graceful regional code-switch** beyond Hindi-English.

**Concrete engineering path to close it:**
- **Domain-grounded taxonomy + golden set:** build a BPO-specific intent ontology (banking/telecom/insurance verticals) with 3-5k human-labeled real Hinglish/regional call utterances per vertical; this single asset moves accuracy more than any model swap.
- **Continual conformal recalibration:** auto-recalibrate α weekly on fresh labeled traffic (drift detector triggers); class-incremental encoder (Mahalanobis prototype, zero-forgetting) so new intents add cheaply.
- **Context-prior fusion:** make the customer-360 (last txn, EMI cycle, last ticket) a first-class re-ranking signal — this is how you recover "wo wala kaam" → specific ticket.
- **Emotion-as-prior:** train a prosody emotion head and feed its output as an explicit feature into the intent re-ranker, not a parallel afterthought.
- **Regional-language data flywheel:** active-learning loop that mines low-confidence Tamil/Telugu/Marathi-English turns for human labeling first.
- **Self-critique pass on heavy tier:** a second LLM check ("is there a hidden/secondary intent here?") to catch the cancel-policy→waive-charge class.
- **Human-feedback capture:** every escalation logs *why* the agent was uncertain → supervised signal for the next fine-tune.

With these, the step reaches near-human on **in-taxonomy** asks; the genuinely-novel long tail stays HITL by design.

---

## 7. HITL trigger (when a human MUST take over for THIS step)

Hand off when:
- Conformal **prediction set empty or > th (7)** → genuine ambiguity / OOS.
- **ASR confidence below floor** repeatedly (codemix garble) after one clarify attempt.
- **Clarification budget exhausted** — 2 disambiguating questions and intent still unresolved (don't trap the caller).
- **High distress emotion** detected → empathy + human (also reduces mis-selling / regulatory risk).
- **Resolved intent is a high-stakes regulated action** (loan closure, policy cancellation, large money movement) AND confidence is sub-threshold → confirm-with-human.
- **Vulnerable-customer signals** (confusion, elderly, repeated misunderstanding) → IRDAI mis-selling exposure → human.

Not "none — fully automatable": disambiguation is *mostly* automatable but the long-tail + distress + regulated-action confirmation must stay HITL.

---

## 8. Automation readiness: **7 / 10**

In-taxonomy intent recognition + clarification in Hindi/Hinglish for banking/telecom is production-ready with the hybrid+conformal stack (high confidence). The −3 is: regional-language code-switch depth, novel long-tail asks, emotion→intent nuance, and regulated-action confirmation that all still need HITL. Not a 9 because the ~30pt few-shot human gap and calibration-under-drift are real and unsolved at the long tail.

---

## 9. Build spec

**Implement:**
1. Streaming Indic codemix ASR (Saaras v3 / IndicConformer) with partial-transcript feed + per-token confidence.
2. Hinglish normalization/transliteration pass (IndicXlit).
3. Two-tier intent engine: fine-tuned MuRIL/IndicBERT first pass → uncertainty router → Sarvam-30B heavy tier on uncertain turns.
4. **CICC conformal wrapper** over the classifier (α calibrated on held-out set; th=7) → commit/clarify/escalate gate.
5. Customer-360 RAG re-ranker (last txn, product, EMI cycle, last ticket).
6. Prosody emotion head feeding the re-ranker.
7. Multi-label + hidden-intent self-critique pass on heavy tier.
8. Reflective confirmation module (caller's language) before any Tier-2/3 action.
9. Per-turn observability trace (intent, conformal set, asr_conf, action, latency) + weekly drift recalibration job.

**Data needed:**
- 3-5k human-labeled real Hinglish/regional utterances **per vertical**, with intent + secondary-intent + emotion labels.
- Conformal **calibration set** (held-out, refreshed weekly).
- Customer-360 schema/tool access.
- Negative/OOS set for rejection calibration.

**Eval metric that gates ship (per vertical):**
- **Primary gate:** Intent top-1 accuracy ≥ **92%** on in-taxonomy Hinglish golden set AND **conformal coverage ≥ 95%** (true intent in set 95% of the time) AND **single-intent commit rate ≥ 70%** (so we're not over-clarifying) — modeled on CICC Banking77 (73% single, 98% coverage).
- **OOS gate:** F1-OOS ≥ **0.80**.
- **Safety gate:** **0** false-commits on regulated high-stakes intents (loan closure / policy cancel / money movement) in the eval set — any false-commit here blocks ship.
- **Latency gate:** intent decision within **300ms** of final partial (fits voice TTFT budget).
- **Multi-intent recall ≥ 0.85** on the dual-ask subset.

---

## 10. India specifics

- **Hinglish + regional code-switch is the default, not the exception** — mid-sentence Hindi/English/Tamil/Telugu/Marathi mixing; ASR must use codemix mode and NLU must be trained on real mixed utterances ([sourced: arXiv 2510.07037 code-switch survey; awaaz.ai code-switching guide; Sarvam codemix mode]).
- **Sovereign-model preference:** Sarvam-30B/105B + Saaras (India-hosted) ease **DPDP data-residency** vs sending voice data to foreign endpoints ([sourced: Sarvam Feb-2026 from-scratch models; Rest of World 2026]).
- **EMI/salary-cycle priors:** 1st-7th of month skews intents toward EMI/payment — bake calendar into context priors.
- **DPDP purpose-limitation at the intent layer:** once you classify intent (e.g., "pay loan"), you may collect/process **only** the data strictly necessary for that purpose; cross-sell/marketing needs **fresh explicit consent** ([sourced: caller.digital regulatory map; DPDP guides 2026]). Penalties up to **₹250 crore**.
- **Reflective-confirmation = compliance, not just UX:** confirming the intent in the caller's words doubles as DPDP purpose-confirmation and IRDAI mis-selling defense.
- **IRDAI:** mis-selling liability stays with the company even if the error was in the AI's script → conservative clarify/escalate on insurance intents (cancellation, switching, claims).
- **RBI FPC:** AI calls in BFSI must offer a **human-escalation path** — the HITL trigger is a regulatory requirement, not just a quality choice.
- **TRAI DLT:** the call itself must be on a registered Principal Entity / DLT template; consent for *calling* ≠ DPDP consent for *processing voice* — keep them separate.
- **Distress + vulnerable-customer escalation** is both CSAT and regulatory hygiene (mis-selling/elderly protection).

---

### Sources
- Hengst & Wolter, *Conformal Intent Classification and Clarification (CICC)*, NAACL Findings 2024 — https://arxiv.org/abs/2403.18973
- *Intent Detection in the Age of LLMs* (Amazon Science), arXiv 2410.01627 — https://arxiv.org/html/2410.01627v1
- *Intent Recognition and OOS Detection using LLMs in Multi-party Conversations*, arXiv 2507.22289 — https://arxiv.org/abs/2507.22289
- *Orchestration-Free / Flowchart-Guided Customer Service*, arXiv 2602.15377 — https://arxiv.org/pdf/2602.15377
- *Survey of Code-Switched NLP in the Era of LLMs*, arXiv 2510.07037 — https://arxiv.org/pdf/2510.07037
- Sarvam models (Saaras v3, Sarvam-30B/105B, Intent Score) — https://www.sarvam.ai/models ; Indic ASR eval — https://www.sarvam.ai/blogs/evaluating-indian-language-asr
- Open-source Voice AI India 2026 — https://www.caller.digital/blog/open-source-voice-ai-india-sarvam-ai4bharat-bhasini-2026
- Voice AI India Regulatory Map 2026 (DPDP/TRAI/RBI/IRDAI) — https://www.caller.digital/blog/voice-ai-india-regulatory-map-2026
- AI Calling Compliance India 2026 (DPDP/TRAI DLT/RBI) — https://www.autointerviewai.com/blog/ai-calling-india-dpdp-trai-dlt-compliance-complete-guide-2026
- Domain-Specific NLU for Financial Conversations 2026 — https://www.awaaz.ai/blog/domain-specific-nlu-for-financial-conversations-guide
- Code-Switching Voice AI Guide 2026 — https://www.awaaz.ai/blog/code-switching-voice-ai-guide
- Real-Time vs Turn-Based Voice Agents 2026 (latency) — https://softcery.com/lab/ai-voice-agents-real-time-vs-turn-based-tts-stt-architecture
- Retell — How Real-Time Voice AI Works — https://www.retellai.com/blog/how-real-time-voice-ai-works-stt-llm-tts
- AssemblyAI — Voice Agent Architecture / STT latency — https://www.assemblyai.com/blog/voice-agent-architecture

---
Draft research note for review. Cited where possible; [UNSOURCED]/[estimate] elsewhere. Not investment advice.
