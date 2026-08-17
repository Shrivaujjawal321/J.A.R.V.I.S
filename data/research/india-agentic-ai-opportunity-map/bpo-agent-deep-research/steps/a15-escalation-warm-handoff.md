# Step A15 — Escalation Decision & Warm Handoff
### (Knowing WHEN to transfer + delivering a clean summary so the human can continue without the customer repeating)

**Context:** India-market, multilingual (Hindi + regional + Hinglish), RBI/IRDAI/DPDP-compliant, action-taking voice+chat contact-center agent for mid-market BPOs.
**Scope of this dossier:** ONLY the escalation-decision + warm-handoff micro-step. Not authentication, not resolution, not after-call work — except where they trigger or feed this step.
**Date:** 2026-06-24

---

## 0. Why this step is the highest-leverage, highest-risk step in the whole agent

Two things make A15 special:

1. **It is the agent's "I don't know" reflex.** Every other step assumes the agent can act. This step is the *meta-decision* — when to STOP acting. A miscalibrated agent that doesn't escalate is the single largest source of regulatory, reputational, and CSAT damage. RBI's FREE-AI framework explicitly makes "People First" + a working human escalation path a non-negotiable (Source: RBI FREE-AI report, Aug 2025, https://rbidocs.rbi.org.in/rdocs/PublicationReport/Pdfs/FREEAIR130820250A24FF2D4578453F824C72ED9F5D5851.PDF).

2. **The handoff is where CSAT is won or lost.** 73% of consumers say repeating information after a transfer is one of the most frustrating parts of support (Source: PwC, cited by BlueTweak, 2026, https://bluetweak.com/blog/ai-to-human-handoff/). Warm transfers with structured context lift CSAT 10-15% vs. cold transfers (Source: Bland AI / MightyCall, 2026, https://www.bland.ai/blog/what-is-a-warm-transfer-in-a-call-center).

So A15 = (a) a *calibrated abstention/routing classifier* fused with (b) a *grounded summarization + telephony handoff*. These are two distinct ML problems glued by an orchestration policy. Treat them separately in the build.

---

## 1. Human micro-steps — what a skilled BPO agent ACTUALLY does

Decomposed into the smallest atomic cognitive + emotional + mechanical moves:

### 1A. Continuous "am-I-still-the-right-person?" monitoring (background loop)
- **m1. Scope check** — "Is this request inside what I'm authorized/able to do?" (e.g. fraud reversal, loan restructure, death-claim — outside L1 scope). Runs every turn, mostly subconscious.
- **m2. Progress check** — "Am I actually moving toward resolution, or going in circles?" (counts failed attempts, repeated clarifications).
- **m3. Emotional-temperature read** — detects rising frustration, distress, threat-to-escalate, crying, abuse — across tone + words + code-switch (Indian callers slip into Hindi/regional when angry).
- **m4. Risk/compliance sniff** — "Did the caller just say something that legally I cannot handle alone?" (dispute, harassment complaint, vulnerable customer, suicide/self-harm, regulator/ombudsman mention, media/legal threat).
- **m5. Explicit-request catch** — caller literally says "let me talk to a human / supervisor se baat karao / manager."

### 1B. The escalation DECISION (the judgment moment)
- **m6. Threshold weighing** — fuses m1–m5 into a single "escalate vs. keep trying" call, weighted by *consequence* (a billing query tolerates more retries than a fraud claim).
- **m7. De-escalation-first instinct** — a *good* agent first tries to calm/solve before transferring (transfer is costly + may not even help). Knows the difference between "frustrated but solvable" and "must transfer now."
- **m8. Route selection** — picks the RIGHT destination: supervisor vs. specialist queue (collections, retention, claims) vs. grievance officer vs. fraud desk. Not just "a human" — the *correct* human.
- **m9. Availability/expectation reality-check** — "Is that queue staffed right now? Should I offer callback instead of a 20-min hold?" Manages caller expectations.

### 1C. The WARM HANDOFF execution
- **m10. Set the customer's expectation** — "I'm connecting you to a specialist who can do X; you won't have to repeat everything." Reduces transfer anxiety + repeat.
- **m11. Mentally compress the case** — builds a 3-5 line summary: identity, verified-status, the ONE problem, what's been tried, what's pending, emotional state, and the *action the next agent should take*.
- **m12. The whisper / briefing** — on hold, tells the receiving agent the summary privately before bridging the caller (the defining feature of a *warm* vs cold transfer).
- **m13. Permission & consent carry-over** — communicates what the caller already authorized (e.g., "consented to OTP, not yet to payment") so the next agent doesn't re-collect or over-reach.
- **m14. Clean bridge + graceful exit** — connects, confirms the receiving agent has it, exits without dead air or dropping the caller.

A skilled agent does m1-m5 *constantly and in parallel*, fires m6-m9 in ~1-2 seconds, and executes m10-m14 in 20-40 seconds. The whole thing is mostly tacit.

---

## 2. Agent approach — how a 2026 AI agent performs each sub-step

The architecture is a **dual-loop**: a fast *escalation sentinel* running every turn, plus a *handoff generator* invoked once the sentinel fires.

### 2A. Monitoring loop (m1-m5) → **Escalation Sentinel** (runs every turn, parallel to main dialog LLM)

| Human move | Agent technique (2026) |
|---|---|
| m1 Scope check | **Tool/intent allow-list gate.** Main agent is a tool-using LangGraph/Pipecat node; any intent that maps to a "human-only" action node (fraud-reversal, death-claim, restructure) flips an escalate flag deterministically. Rules > ML here — you WANT this hard-coded for audit. |
| m2 Progress check | **Loop/repair-state counter** in graph state: `failed_attempts`, `clarification_loops`, `no_progress_turns`. Threshold (e.g. ≥3) is a deterministic trigger. Detects "circular conversation" (BlueTweak contextual trigger). |
| m3 Emotional read | **Streaming multimodal sentiment** — paralinguistic (prosody/pitch/energy via wav2vec2/Whisper-encoder emotion head) + lexical (the LLM's own frustration classification) fused. India-tuned so deference/code-switch isn't misread as satisfaction (Source: Caller Digital / Shunya Labs, 2026). Gnani-style real-time sentiment claims ~25% escalation reduction when used for de-escalation (Source: Gnani.ai, 2026). |
| m4 Risk/compliance sniff | **Guardrail classifier ensemble** (NeMo Guardrails / Llama Guard 3-style + a domain-tuned BFSI/insurance risk classifier). Keyword + semantic detection of: dispute, harassment, ombudsman/RBI/IRDAI, self-harm, legal/media threat, vulnerable-customer markers. Self-harm = hard interrupt. |
| m5 Explicit request | **Intent classifier + regex/keyword** in 11+ languages incl. Hinglish ("human se baat", "supervisor", "manager", "insaan"). Highest-precision, zero-tolerance trigger. |

The Sentinel emits a structured signal each turn: `{escalate: bool, reason_code, severity, suggested_route, confidence}`.

### 2B. The DECISION (m6-m9) → **Calibrated routing policy**

- **m6 Threshold weighing:** This is where 2026 SOTA matters. Use **calibrated confidence** on the main agent's trajectory, not raw token probability. RLHF degrades calibration (Source: Zylos Research, Apr 2026, https://zylos.ai/research/2026-04-18-llm-calibration-uncertainty-production-agents), so layer **Holistic Trajectory Calibration (HTC)** (Source: arXiv 2601.15778, 2026) or activation-based abstention (Source: arXiv 2510.13750) over the dialog model to get a *trustworthy* "should I keep going" score. Fuse Sentinel signals + calibrated confidence in a small policy head / decision-tree with *consequence-weighted* thresholds (low threshold for fraud, higher for billing).
- **m7 De-escalation-first:** Policy includes a "try-de-escalate-once" branch for *solvable-but-frustrated* states (empathy reflection + offer concrete fix) before transferring — gated so it NEVER applies to compliance/self-harm/explicit-request reasons.
- **m8 Route selection:** Map `reason_code → skill queue` via a routing table (fraud→fraud desk, collections-dispute→grievance officer, claim→claims specialist, retention-cancel→retention). LLM proposes, table validates.
- **m9 Availability check:** Query ACD/queue API for real-time agent availability + EWT (expected wait time); if no agent or EWT > threshold, offer **scheduled callback / async ticket** instead of dead hold.

### 2C. The WARM HANDOFF (m10-m14) → **Grounded summarizer + telephony bridge**

| Human move | Agent technique (2026) |
|---|---|
| m10 Set expectation | Scripted, localized TTS line ("Main aapko specialist se connect kar raha hoon, aapko dobara sab batana nahi padega"). |
| m11 Compress case | **Grounded, schema-constrained summarization.** LLM (Gemini-2.0-Flash class for low hallucination — 0.7% summary hallucination, Source: Vectara via Suprmind, 2026) summarizes ONLY from the verified transcript + tool-call log into a fixed JSON schema (identity, verified-status, one-line problem, attempts, pending action, sentiment, consent state). Constrained decoding + post-hoc faithfulness check (NLI/SummaC entailment vs. transcript) to block hallucinated facts. |
| m12 Whisper/briefing | The JSON renders into (a) a **screen-pop card** in the agent desktop (Cresta/Parloa-style agent-assist) AND (b) optionally a TTS whisper played only to the receiving agent before bridging (Source: BlueTweak / SigmaMind, 2026). |
| m13 Consent carry-over | `consent_state` is a first-class field (DPDP-critical): what was consented, what was NOT. Prevents re-collection and over-reach. |
| m14 Clean bridge | **SIP REFER / warm-transfer via LiveKit or Pipecat native SIP** — agent stays on, briefs, then bridges caller. Barge-in/turn-taking handled so no dead air (turn-gap P95 200-450ms; Source: FutureAGI, 2026). |

---

## 3. Tooling — concrete 2026 stack

- **Voice orchestration / telephony bridge:** LiveKit Agents (native SIP, SmolLM-v2 ~135M turn-detector) or Pipecat (Frame-based, SmartTurnAnalyzer). Both support SIP REFER warm transfer to human queues. (Source: LiveKit, Forasoft, 2026.)
- **STT/TTS (Indic):** Sarvam (11 Indian languages, <500ms latency, code-switch as primary objective) and/or Gnani for BFSI + voice biometrics. (Source: Sarvam PIB release; Caller Digital, 2026.)
- **Dialog LLM:** GPT-4o/Claude-class for reasoning; **Gemini-2.0-Flash** specifically for the *summary node* (lowest summarization hallucination at 0.7%).
- **Escalation sentinel:** small fine-tuned classifier (DistilBERT/IndicBERT multilingual) for intent+risk; prosodic emotion head (wav2vec2 / Whisper-encoder). Run as a parallel Pipecat processor.
- **Guardrails:** NVIDIA NeMo Guardrails + Llama Guard 3-class + a custom BFSI/IRDAI risk classifier.
- **Calibration layer:** HTC / activation-based abstention head over the dialog model; temperature-scaling + isotonic calibration on the routing logits; verbalized-confidence as a secondary signal only.
- **Summary faithfulness check:** SummaC / MiniCheck / NLI-entailment gate; TofuEval-style eval harness for dialogue-summary hallucination.
- **Routing/ACD integration:** REST/webhook into the BPO's ACD (Genesys/Avaya/Ozonetel/Exotel/Knowlarity) for skill-queue + EWT.
- **Agent-assist desktop:** Cresta / Parloa / Decagon-style screen-pop with the handoff card.
- **Observability/audit:** structured event log of every escalation decision (reason_code, confidence, route, timestamp) for RBI/IRDAI auditability.

---

## 4. Benchmarks — real numbers

| Metric | Number | Source/tag |
|---|---|---|
| Healthy containment (resolved w/o escalation) | 40-70% mature; 20-40% early | [sourced] IrisAgent/Famulor, 2026 |
| Planned escalation rate (target) | 30-40% | [sourced] IrisAgent, 2026 |
| Forced escalation rate (target) | <10% | [sourced] IrisAgent, 2026 |
| Handoff context completeness (the key metric) | >90% target; "single most common failure point" | [sourced] IrisAgent, 2026 |
| Repeat-info frustration | 73% of consumers cite it as top frustration | [sourced] PwC via BlueTweak, 2026 |
| Warm-transfer CSAT lift | +10-15% vs cold | [sourced] Bland AI/MightyCall, 2026 |
| Summarization hallucination (grounded) | <2% typical; Gemini-2.0-Flash 0.7% | [sourced] Vectara/Suprmind, 2026 |
| Dialogue-summary inconsistency (worst case, ungrounded) | avg 26.8%; best model still 16% | [sourced] arXiv 2311.07194 |
| RAG/grounding hallucination reduction | 30-70% | [sourced] modelslab, 2026 |
| Barge-in success / false-barge | >96% / <2%; turn-gap P95 200-450ms | [sourced] FutureAGI, 2026 |
| Real-time sentiment → escalation reduction | ~25%; FCR +30% | [sourced] Gnani.ai, 2026 |
| Calibration: RLHF degrades it | qualitative — confident-wrong is systematic | [sourced] Zylos, Apr 2026 |
| Agentic UQ benchmark suite | does NOT yet exist in mature form (early 2026) | [sourced] arXiv 2602.05073 (ICML'25 position) |

The standout: **handoff context completeness is the named #1 failure point**, and there is **no mature agentic-uncertainty benchmark** — so you must build your own eval for the decision half.

---

## 5. Failure modes — where the agent breaks

1. **Under-escalation (the dangerous one):** Miscalibrated confidence (RLHF-degraded) → agent confidently proceeds on a fraud/dispute/self-harm case it should have handed off. Highest regulatory + safety risk.
2. **Over-escalation:** Sentinel too trigger-happy → containment collapses, queues flood, ROI evaporates, customers annoyed by needless transfers.
3. **Emotion misread (India-specific):** English-tuned sentiment reads a deferential Hindi/regional caller as "satisfied" → misses distress (Source: Caller Digital, 2026). Or sarcasm/code-switch flips polarity.
4. **Summary hallucination:** Ungrounded summarizer invents a fact (wrong amount, false "verified", fabricated prior attempt) → human acts on bad info; up to 16-27% inconsistency if not grounded+checked.
5. **Wrong-route handoff:** Sends fraud to billing; human re-transfers → exactly the repeat-info frustration you were trying to avoid.
6. **Consent/PII leakage in handoff:** Summary over-shares or carries stale consent → DPDP violation.
7. **Telephony failure on bridge:** Dropped call, dead air, lost context on SIP REFER → customer drops, CSAT tanks.
8. **Latency stall at the decision moment:** Adding a heavy calibration/summarizer call mid-call introduces dead air right when the caller is already frustrated.
9. **Availability mismatch:** Escalates to an unstaffed queue → 20-min hold → worse than not escalating.

---

## 6. Gap to full adaptation — what the agent STILL can't do as well as a human, and how to close it

**The residual human edge is in m6 (consequence-weighted judgment) and m7 (de-escalate-vs-transfer instinct).** A great human agent *feels* when a calm customer is actually a flight risk, or when a "frustrated" customer is one good sentence away from being delighted — and chooses NOT to transfer. The agent's decision is still brittle on these soft, high-context judgment calls.

Concrete gaps + the engineering/data path to close each:

| Gap | Why agent is worse | Path to close |
|---|---|---|
| **Calibrated "keep-going vs transfer" judgment** | No mature agentic-UQ benchmark exists; RLHF confidence is untrustworthy | Build a labeled trajectory dataset from your own call logs (escalate / should-have-escalated / over-escalated), train an HTC/activation-abstention head, set consequence-weighted thresholds per intent. This is the #1 build investment. |
| **Distinguishing solvable-frustration from must-transfer** | Lacks the tacit "one more try will fix this" instinct | Counterfactual labeling: mine cases where a human de-escalated successfully vs. transferred; train a de-escalation-success predictor that gates the "try-once" branch. |
| **India emotion/code-switch nuance** | English-tuned affect models misread deference/sarcasm | Fine-tune prosodic + lexical emotion on *your* Hindi/regional/Hinglish call audio with native-speaker labels; calibrate per-region. |
| **Choosing callback vs hold gracefully** | No real "feel" for caller patience | Feed real-time EWT + caller-history (prior abandons) into the availability policy; A/B the offer. |
| **Summary that captures the *unstated* important thing** | Human notices "she mentioned her husband just passed" as load-bearing context; LLM may drop it | Two-pass summary: extractive (verbatim quotes) + abstractive, with a "salient emotional/vulnerability flag" field forced into the schema; faithfulness-checked. |

The closing strategy is data + calibration, not a bigger base model. **The decision half is a supervised-learning + calibration problem on your own labeled call data; the handoff half is a grounding + schema-discipline problem.** Most of full adaptation is achievable; the last ~10% (pure soft judgment) is where HITL stays.

---

## 7. HITL trigger — when a human MUST take over this step

This step IS the handoff, so "HITL" here means: **which escalation decisions must a human (supervisor) review/own, vs. the agent firing the transfer autonomously.**

Agent fires the handoff autonomously (no supervisor approval needed) for routine planned escalations (out-of-scope, repeated-failure, explicit request).

A human MUST be in the loop when:
- **Self-harm / suicide / acute distress** → immediate hard interrupt to a trained human; never agent-managed.
- **Vulnerable customer** flagged (elderly, distressed bereavement, financial-hardship under RBI fair-practices) → human-led.
- **Regulator / ombudsman / legal / media threat mentioned** → human + compliance.
- **Calibrated confidence is in the "abstain" band but the consequence is high** (fraud, large financial reversal) → human reviews before/at handoff.
- **DPDP-sensitive action would be implied by the handoff** (e.g., transferring data to a third-party desk beyond consent) → human authorizes.

So: **not fully automatable end-to-end.** The *common* escalations are automatable; the *high-consequence/safety/compliance* escalations are exactly the ones that must route to a human (which is the point of the step).

---

## 8. Automation readiness — **8 / 10**

- The **handoff-execution half** (m10-m14: summarize, warm-bridge, screen-pop) is genuinely ship-ready at ~9/10 — grounded summarization is <2% hallucination, SIP warm transfer is mature, agent-assist screen-pops are productized (Cresta/Parloa/Decagon).
- The **decision half** (m6-m9: calibrated judgment) is the drag — ~7/10 — because mature agentic-UQ benchmarks don't exist and RLHF calibration is untrustworthy, so you must build + label your own. Once you have consequence-weighted thresholds tuned on your data, it's high-confidence.
- Net **8/10**: deployable today with the explicit/scope/repeat/sentiment triggers fully automated, calibrated-judgment + high-consequence cases kept under supervisor HITL. The bottleneck to 10 is your own labeled trajectory data + India-tuned affect, not base-model capability.

---

## 9. Build spec

**What to implement:**
1. **Escalation Sentinel** — parallel Pipecat/LiveKit processor emitting `{escalate, reason_code, severity, suggested_route, confidence}` every turn. Deterministic triggers (scope allow-list, loop-counter, explicit-request keyword in 11+ langs) + ML triggers (risk guardrail ensemble, India-tuned streaming sentiment).
2. **Calibrated routing policy** — HTC/activation-abstention head over the dialog model + temperature/isotonic calibration; consequence-weighted thresholds per intent; de-escalation-first branch (gated off for compliance/safety).
3. **Routing table + ACD integration** — `reason_code → skill_queue`, real-time EWT, callback fallback.
4. **Grounded handoff summarizer** — Gemini-2.0-Flash class, schema-constrained JSON `{identity, verified_status, one_line_problem, attempts[], pending_action, sentiment, consent_state, vulnerability_flag}`, with a SummaC/NLI faithfulness gate vs. transcript.
5. **Warm-transfer bridge** — SIP REFER via LiveKit/Pipecat, whisper + screen-pop card, clean bridge.
6. **Audit log** — every decision persisted for RBI/IRDAI.

**Data needed:**
- 5-10k labeled call trajectories: `escalate / should-have-escalated (missed) / over-escalated`, with correct route + consequence tier.
- Hindi/regional/Hinglish call audio with native-speaker emotion + frustration labels (for affect fine-tune + calibration).
- Gold handoff summaries (human-written) per call for the summarization eval.
- Consent-state traces for the DPDP carry-over field.

**Eval metrics that gate "good enough to ship":**
- **Decision half:** Missed-escalation rate (false-negative on must-escalate) **< 1%** on the held-out set (this is the safety gate — weight FN >> FP); over-escalation/false-positive **< 15%**; ECE on routing confidence **< 0.05**.
- **Handoff half:** Summary **faithfulness ≥ 98%** (no hallucinated facts vs transcript, TofuEval/SummaC-checked); **context-completeness ≥ 90%** (all schema fields correctly populated, human-rated); **post-handoff repeat-rate < 10%** (customer didn't have to re-state the problem).
- **End-to-end:** Warm-transfer CSAT delta ≥ +10% vs cold baseline; bridge success ≥ 99%; added decision+summary latency < 1.2s (no audible dead air).

Ship gate = ALL of the above met on held-out India call data, with self-harm/vulnerable/compliance cases at 100% routed-to-human in red-team eval.

---

## 10. India specifics

- **Mandatory human escalation is law, not UX.** AI cannot be the sole interaction option for financial products; the customer must be able to reach a human at any point, and every BFSI call must surface the grievance-redressal path aligned to the **RBI Integrated Ombudsman Scheme**; insurance to the **IRDAI ombudsman** (Source: AutoInterviewAI / Caller Digital regulatory map, 2026).
- **RBI FREE-AI "People First"** + working escalation path is a framework requirement (Source: RBI FREE-AI, Aug 2025).
- **Collections (RBI Fair Practices):** 8am-7pm window, ≤3 calls/day/borrower, mandatory entity ID + grievance info + **supervisor escalation path**; human collection agents need IIBF-DRA cert — "AI doesn't pass IIBF, so the platform's compliance architecture must be the auditable substitute" (Source: Caller Digital, 2026). → escalation logging is a compliance artifact, not optional.
- **IRDAI policy-impacting changes** (premium change, rider, beneficiary, surrender) need **recorded consent with comprehension confirmation** — these are hard escalate-or-confirm triggers; carry consent_state in the handoff.
- **DPDP:** documented opt-out + grievance officer; the handoff summary must NOT over-share PII or carry stale consent across desks.
- **Language/affect:** code-switching is the norm (caller flips to Hindi/regional when angry); English-tuned sentiment under-reads deferential distress → MUST use India-tuned affect (Sarvam/Gnani-class) and treat "human se baat karao / supervisor / insaan" + regional equivalents as the highest-precision explicit trigger across all 11+ languages.
- **Whisper/handoff to human in the caller's language** — receiving-agent screen-pop in English/working language, but customer-facing expectation-setting line in the caller's language.

---

### Sources
- IrisAgent — Voice AI 2026 benchmarks: https://irisagent.com/blog/voice-ai-customer-service-2026-benchmarks/
- Famulor — AI Voice Agent KPIs 2026: https://www.famulor.io/blog/ai-voice-agent-kpis-12-metrics-that-matter-in-2026
- BlueTweak — AI-to-Human Handoff 2026: https://bluetweak.com/blog/ai-to-human-handoff/
- Bland AI — Warm Transfer & CSAT: https://www.bland.ai/blog/what-is-a-warm-transfer-in-a-call-center
- Decagon — Warm vs Cold Transfer: https://decagon.ai/glossary/what-is-warm-transfer-vs-cold-transfer
- SigmaMind — Warm Transfer for Voice AI: https://www.sigmamind.ai/blog/warm-transfer
- Cresta — Best AI Agents for Contact Centers 2026: https://cresta.com/guides/best-ai-agents
- Zylos Research — LLM Calibration & UQ in production agents (Apr 2026): https://zylos.ai/research/2026-04-18-llm-calibration-uncertainty-production-agents
- arXiv 2601.15778 — Agentic Confidence Calibration (HTC)
- arXiv 2510.13750 — Confidence-Based Response Abstinence
- arXiv 2602.05073 — UQ in LLM Agents (ICML'25 position)
- arXiv 2311.07194 — Factual Consistency in Dialogue Comprehension
- arXiv 2402.13249 — TofuEval (dialogue-summary hallucination)
- Suprmind — AI Hallucination Rates June 2026: https://suprmind.ai/hub/ai-hallucination-rates-and-benchmarks/
- FutureAGI — Voice AI Barge-In & Turn-Taking 2026: https://futureagi.com/blog/voice-ai-barge-in-turn-taking-2026/
- LiveKit — Turn Detection for Voice Agents: https://livekit.com/blog/turn-detection-voice-agents-vad-endpointing-model-based-detection
- Caller Digital — Voice AI India Regulatory Map 2026: https://www.caller.digital/blog/voice-ai-india-regulatory-map-2026
- Caller Digital — Multilingual Voice AI India 2026: https://caller.digital/blog/multilingual-voice-ai-hindi-tamil-telugu-bengali-india-2026
- AutoInterviewAI — AI Calling India DPDP/TRAI/RBI Compliance 2026: https://www.autointerviewai.com/blog/ai-calling-india-dpdp-trai-dlt-compliance-complete-guide-2026
- RBI FREE-AI Framework (Aug 2025): https://rbidocs.rbi.org.in/rdocs/PublicationReport/Pdfs/FREEAIR130820250A24FF2D4578453F824C72ED9F5D5851.PDF
- Gnani.ai — Real-Time Sentiment Detection: https://www.gnani.ai/resources/blogs/how-real-time-sentiment-detection-works-in-voice-ai
- Sarvam AI (PIB): https://www.pib.gov.in/PressReleasePage.aspx?PRID=2231169

*Draft research dossier for review. Cited where possible; [estimate] elsewhere. Not investment advice.*
