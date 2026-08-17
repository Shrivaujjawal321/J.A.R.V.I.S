# Step A02 — Greeting, Identity Verification & Authentication (KYC-on-call, Security Questions)

**Domain:** India-market, multilingual (Hindi + regional + Hinglish) voice + chat contact-center agent for mid-market BPOs.
**Compliance envelope:** RBI (Master Direction KYC + Authentication Mandate, eff. 1-Apr-2026), IRDAI, DPDP Act 2023 + DPDP Rules 2025, UIDAI/Aadhaar Act.
**Scope of this doc:** ONLY the first ~30–90 seconds of a serviced call/chat: open, greet, establish who is calling, and authenticate them to the assurance level required before any account action is permitted.
**Last researched:** 2026-06-24.

---

## 0. Why this step is the security gate of the entire system

Every downstream action (balance disclosure, fund transfer, SIM/policy change, address update) inherits its risk from this step. Authentication is not a "nice greeting" — it is the **trust boundary**. Under-authenticate → fraud + RBI/IRDAI penalty + DPDP breach. Over-authenticate → friction, abandonment, NPS collapse, and (in 2026) the agent looks dumber than the human it replaced. The job is to hit the *minimum sufficient assurance level for the requested action* — i.e., **step-up authentication**, not flat KBA.

This is also the step most exposed to the **2026 deepfake threat**: a reported ~1,300% YoY rise in deepfake-fraud attempts on call centers, and KBA is now considered structurally broken because AI callers have perfect recall of static answers. So this step is simultaneously the easiest to *script* and the hardest to *secure*.

---

## 1. Human micro-steps (the atomic decomposition)

What a skilled BPO agent ACTUALLY does in the first 30–90 seconds, broken to the smallest cognitive/emotional/mechanical moves:

1. **Pre-call context absorption** — in the 1–2s before/while answering, glance at the screen-pop: ANI (caller number), IVR path taken, CRM match, last-contact reason, open tickets, language flag, VIP/risk flag.
2. **Greeting + brand compliance line** — deliver the mandated opening ("Namaste, [Brand] mein aapka swagat hai, main [name] baat kar raha hoon") at correct pace, warmth, and in the right language.
3. **Language detection + register match** — within the first utterance, detect Hindi / English / Hinglish / regional (Tamil, Telugu, Bengali, Marathi, etc.) and *mirror* the caller's register and formality.
4. **Caller intent pre-read** — listen to the opening line to infer urgency/emotion (angry, distressed, routine) and *why* they called, which sets how much authentication friction is tolerable.
5. **Claimed-identity capture** — get the name/account/policy/mobile the caller *claims* to be, parse it (spelled-out names, digit strings over noisy lines, "mera number hai...").
6. **Record lookup + disambiguation** — find the right record; resolve duplicates ("do Rahul Sharma hain, DOB batayein"), handle no-match gracefully.
7. **Risk + assurance-level decision** — decide *how hard* to authenticate based on (a) requested action's sensitivity, (b) channel/ANI trust signals, (c) account risk flags, (d) recent fraud patterns. This is the senior judgment call.
8. **Authentication-factor selection** — pick which factors to use: ANI match, OTP-to-registered-mobile, KBA security questions, Aadhaar OTP eKYC, voice biometric, DigiLocker fetch — and in what order, balancing security vs. friction.
9. **Challenge delivery + answer capture** — ask the security question(s) / trigger OTP / prompt for biometric phrase, listen to the answer, normalize it (dates spoken many ways, partial matches, typos in spelling).
10. **Answer adjudication (fuzzy match)** — judge "close enough": "t_4th April" vs "4/4", "MG Road" vs "M.G. Rd", maiden-name spelling variants. Decide pass/fail/partial.
11. **Soft-fail handling + retry logic** — when an answer is wrong, decide: benign error (allow retry, reassure) vs. suspicious (escalate, step up, or lock). Manage caller frustration during retries WITHOUT leaking which answer was wrong.
12. **Fraud-instinct / anomaly sensing** — pick up on tells: hesitation patterns, background coaching voices, "let me check my notes", pushy urgency, mismatched voice vs. profile, robotic/synthetic timbre.
13. **Authentication outcome + state transition** — declare verified at level L, log it, set the session's permission scope, and hand off to the service intent — OR fail-closed and route to fraud/manual desk.
14. **Empathetic friction-cushioning throughout** — apologize for the security step, explain *why* ("aapki suraksha ke liye"), keep the caller calm and not feeling interrogated.

---

## 2. Agent approach (how a 2026 AI agent does each sub-step)

| # | Human sub-step | 2026 agent technique |
|---|----------------|----------------------|
| 1 | Pre-call context | **CTI/ANI screen-pop ingested as structured pre-call context block** into the orchestrator state; CRM (Salesforce/Zoho/Leadsquared) lookup by ANI before first token. Risk signals from telephony (STIR/SHAKEN attestation where available, carrier ANI-spoof score). |
| 2 | Greeting + brand line | **Templated, low-temperature TTS** opener (no LLM free-gen for the compliance line — deterministic) via a streaming neural TTS (ElevenLabs Flash v2.5 / Sarvam Bulbul / Cartesia Sonic). Brand line is a fixed asset, not generated, to stay audit-clean. |
| 3 | Language detect + register | **Streaming multilingual ASR with built-in LID + code-switch handling** (Sarvam STT, AI4Bharat IndicConformer-600M). Language flag flips the TTS voice + prompt locale within ~1 turn. Register mirrored via a style-conditioning instruction in the system prompt. |
| 4 | Intent + emotion pre-read | **Paralinguistic/SER model** (emotion-from-audio) + LLM intent classifier on the first utterance. Emotion score feeds an "empathy/friction budget" variable. |
| 5 | Claimed-identity capture | **Slot-filling via structured ASR + entity extraction**; digit/letter normalization with **NATO/Hindi phonetic spell-back confirmation** ("R for Rajesh"). Confidence-gated re-prompt on low-ASR-confidence tokens. |
| 6 | Record lookup + disambig | **Tool call** to CRM/core-banking API; deterministic disambiguation policy (ask one distinguishing attribute). Fuzzy name match (phonetic — Indic Soundex / IndicNLP transliteration-aware). |
| 7 | Assurance-level decision | **Risk engine = policy graph + ML risk score** (deterministic rules for regulatory floors + an ML model for adaptive step-up). LangGraph/state-machine node that maps {action sensitivity × signal trust} → required LoA. This is NOT left to the LLM alone — it's a guarded policy node. |
| 8 | Factor selection | **Authentication orchestrator** picks factor chain from a config matrix. Prefers possession+inherence over KBA. OTP via Aadhaar AUA/KUA API or SMS; voice biometric (text-dependent passphrase or text-independent passive); Aadhaar OTP eKYC / DigiLocker for high-LoA. |
| 9 | Challenge delivery | Deterministic prompt templates per factor; OTP trigger = tool call; voice-bio = passive enrollment+verify on the running audio stream (no extra friction). |
| 10 | Answer adjudication | **Fuzzy/semantic match layer** (not exact string): date-normalization, address canonicalization, edit-distance + phonetic match thresholds, LLM-judge fallback for ambiguous cases with a strict rubric. |
| 11 | Soft-fail/retry | **Policy-driven retry FSM**: N attempts, no answer-leak prompts, escalating step-up. Frustration detected → empathy template + reassurance, but security floor never lowered by emotion. |
| 12 | Fraud sensing | **Real-time anti-spoof / deepfake detector** (ASVspoof-5-class production models, RTF 0.33–0.40) running in parallel on the audio; **synthetic-speech score** + **ANI-spoof score** + behavioral anomaly (hesitation, background-voice diarization) → fraud risk signal feeding the risk engine. |
| 13 | Outcome + state | **Signed auth-assertion** written to session state (LoA, factors used, timestamps, scores) → unlocks scoped tool permissions. Fail-closed → warm transfer to fraud/manual queue with full context. |
| 14 | Friction cushioning | LLM empathy layer constrained by guardrails; explains *why* security exists; never blames caller. |

**Reference architectural pattern:** the 2026 best practice is **layered/continuous authentication woven INTO the conversation** (voiceprint + ANI + CRM + risk-score evaluated *while* the agent talks), not a separate pre-call gate — per Talkdesk/Parloa/Poly.ai/Bland deployments.

---

## 3. Tooling (concrete 2026 stack)

**Orchestration / agent runtime**
- LangGraph or Pipecat (Pipecat for true streaming voice with ~300ms VAD default) as the conversation state machine; auth as guarded nodes.
- Reasoning LLM: Claude (Sonnet-tier) or GPT-class for intent + adjudication; deterministic policy nodes for the actual auth decision.

**Speech**
- **ASR:** Sarvam STT (19.31% WER on IndicVoices, Hinglish/Tanglish code-mix, diarization, word timestamps) or AI4Bharat IndicConformer-600M (30M-param real-time variant) / IndicWhisper for 22 Indian languages.
- **TTS:** Sarvam Bulbul / ElevenLabs Flash v2.5 / Cartesia Sonic (TTS flush <60ms target).
- **Turn-taking:** dedicated turn-taking model (backchannel vs barge-in vs silence) over raw VAD; target 200–400ms turn gap, <2% false-barge-in.

**Identity / KYC rails (India)**
- **Aadhaar eKYC:** UIDAI-authorised AUA/KUA (must be licensed) — OTP eKYC (₹2–5/txn, 8–15s), biometric eKYC, offline XML. Note SHA-1→SHA-256 migration (UIDAI Circular 3 of 2026).
- **DigiLocker consent-fetch API** for OVD pull (consent-mediated).
- **CKYC registry** lookup; PAN/GST/bank-penny-drop via aggregators (Deepvue, Sandbox, AuthBridge, Perfios, BeFiSc).
- **OTP/SMS** via DLT-registered route.

**Voice biometrics + anti-spoof**
- Voiceprint: Phonexia / Nuance-class engines, or Pindrop-style passive (text-independent EER <0.5–1%).
- Anti-deepfake: ASVspoof-5-trained production detectors (Resemble AI Detect / Aurigin AI, RTF 0.33–0.40) — MUST be retrained on 2026 TTS (ElevenLabs, F5-TTS) attacks; 2019-trained detectors do NOT generalize.

**Telephony / risk**
- CTI screen-pop (Genesys/Amazon Connect/Ozonetel/Exotel for India); ANI-spoof scoring; STIR/SHAKEN where available.

**Compliance / observability**
- Consent-manager hooks (DPDP Consent Manager registration opens Stage 2, 12 months from 13-Nov-2026).
- Immutable audit log of every auth decision (factors, scores, LoA, transcript hash).
- Eval harness: Hamming AI / Future AGI for voice-agent eval; custom auth-accuracy harness.

---

## 4. Benchmarks (real numbers)

- **Voice biometric EER:** industry-leading <0.5% EER, best ~0.3%; <1% in optimal conditions. [sourced — ZipDo/Computer-Talk/Talkdesk 2026]
- **Deepfake threat scale:** ~1,300% YoY increase in deepfake fraud attempts on call centers. [sourced — TruthScan 2026 Caller Auth Guide]
- **Anti-spoof real-time:** production ASVspoof-5 detectors at RTF 0.33–0.40 (real-time); a 53.7% FPR was observed in a poorly-generalized production KYC config — illustrating the generalization gap. [sourced — Resemble AI / CallSphere 2026]
- **Indian ASR:** Sarvam STT 19.31% WER on IndicVoices (10 langs), beats GPT-4o Transcribe / Gemini 3 Pro / Deepgram Nova3 / Scribe v2 on Indian accuracy. IndicConformer 30M params for real-time. [sourced — Sarvam AI / AI4Bharat 2026]
- **Aadhaar OTP eKYC:** ₹2–5/txn, 8–15s end-to-end. [sourced — Deepvue 2026 KYC guide]
- **Latency budget:** turn gap 200–400ms; agent-side response <~700ms for naturalness; end-to-end <1.5s good, 1.5–2.5s typical, >3s "broken". TTS flush <60ms. [sourced — FutureAGI/CallSphere/DeepAgent 2026]
- **Fraud reduction with layered auth:** Dock.io reported 50% fraud-incident decrease in 2026 evals attributed to stronger/streamlined auth controls. [sourced — FTX Identity / Dock.io 2026]
- **KBA pass rate / friction:** legitimate-customer KBA failure commonly cited 10–30% [estimate — varies by question quality; no single 2026 source].

---

## 5. Failure modes

1. **KBA is structurally broken (2026):** static security answers verify *database access*, not identity. Delegated AI callers / data-breach holders pass trivially. KBA-only is now indefensible in audit. [sourced — CX Today / Au10tix]
2. **Deepfake / voice-clone bypass** of voice biometrics if anti-spoof is trained on stale (2019) data → fails to generalize to ElevenLabs/F5-TTS clones.
3. **ASR errors on the hardest tokens:** spelled names, long digit strings, heavy regional accents, noisy lines → false KBA mismatches that lock out *genuine* callers (the worst failure for NPS).
4. **Code-switch / register failure:** mid-sentence Hindi↔English↔Tamil switches; agent picks wrong locale, mis-transcribes, or replies in wrong language → caller frustration, abandons before auth.
5. **Over-rigid fuzzy match:** rejects "4 April" vs "04/04" or "M.G. Road" vs "MG Rd" → genuine fail. Or too-loose → fraud passes.
6. **Answer-leak in retry prompts:** poorly designed re-prompts reveal which field was wrong (a fraudster goldmine).
7. **Emotion-driven security erosion:** an angry/distressed caller pressures the agent; a naive empathy layer lowers the security floor.
8. **No-match / disambiguation dead-ends:** duplicate records, joint accounts, callers calling for someone else (POA, family) — policy gaps cause hard stops.
9. **OTP delivery failure:** mobile not linked to Aadhaar / number changed → flow has no graceful fallback (must route to DigiLocker/V-CIP).
10. **Background coaching / social-engineering** that a human "feels" but the agent misses without diarization + anomaly scoring.
11. **Latency stack-up:** ASR + LLM + biometric + anti-spoof in series blows the <1.5s budget → unnatural, caller talks over the agent.
12. **DPDP consent gap:** capturing/storing voiceprint without valid, purpose-bound, verifiable consent + notice = sensitive-data violation.

---

## 6. Gap to full adaptation (what the agent STILL can't do as well as a human — and the path to close it)

**Gap A — Holistic fraud intuition.** A senior human integrates dozens of weak signals (a tremor, a too-perfect answer, "haan haan jaldi karo", a half-heard prompter) into a gut call. The agent currently scores signals in silos.
→ **Path:** train a **multimodal fraud-risk model** that fuses anti-spoof score + paralinguistic features + ASR-hesitation timing + answer-latency + diarization (extra voices) + ANI/STIR signals into one calibrated risk score; label it from real fraud-confirmed calls; calibrate against confirmed-fraud OOF, not synthetic. Continuous retraining as attacks evolve.

**Gap B — Graceful judgment on edge identities.** Humans flex sensibly for POA holders, joint accounts, illiterate callers who can't recall a "registered email", the elderly who fail DOB phrasing. Agents fail-closed too rigidly or open too wide.
→ **Path:** an **edge-case policy library** co-authored with compliance, plus a curated dataset of these scenarios; route truly novel ones to HITL and *learn* from the human's resolution (active learning loop).

**Gap C — Adaptive friction calibration.** Humans intuitively know when to add/remove a question. Agents need an explicit policy.
→ **Path:** a **step-up RL/bandit policy** optimizing (security floor met) subject to minimizing friction/abandonment, gated by hard regulatory floors that can never be traded away.

**Gap D — Robust code-switch authentication dialogue.** Mixed-language spelled answers (a name spelled half in Hindi letters, half English) still break.
→ **Path:** fine-tune ASR on **in-domain auth utterances** (spelled names, DOBs, addresses in Hinglish/regional) + phonetic spell-back confirmation as standard.

**Gap E — Trust that survives an audit.** A human's judgment is explainable post-hoc. The agent must produce a regulator-grade rationale.
→ **Path:** every auth decision emits a **structured, signed decision record** (factors, scores, thresholds, LoA) — explainability by construction.

---

## 7. HITL trigger (when a human MUST take over)

Not fully automatable as a closed loop for high-risk paths. A human (fraud desk / senior agent) MUST take over when:
- Anti-spoof / fraud-risk score crosses the high-risk threshold (suspected deepfake or social engineering).
- Repeated auth failure on a high-value account (potential account-takeover in progress).
- Edge identity outside policy library (POA, deceased-account, court-order, minor, joint with dispute).
- Requested action is above the LoA the available factors can satisfy AND digital step-up (Aadhaar/DigiLocker/V-CIP) is unavailable.
- Caller explicitly demands a human, or distress/vulnerability indicators present (DPDP + fair-treatment).
- Any regulator-defined "must be human-verified" action (per RBI/IRDAI/internal risk policy).

**Routine, low-to-medium-risk auth (balance, status, low-value servicing) with clean ANI + OTP/voiceprint + clean anti-spoof = fully automatable, no HITL.**

---

## 8. Automation readiness: **7 / 10**

The *mechanics* (greet, language, KBA dialogue, OTP, voiceprint, fuzzy match, logging) are ship-ready today with high confidence — readiness 8–9 for low/medium-risk paths. The *fraud-judgment + edge-identity + adaptive-friction* layer for high-risk paths still needs HITL and a continuous-learning loop, which pulls the blended score to **7**. This step is *more* automatable than most BPO steps precisely because it is rule-bounded — but the deepfake arms race and regulatory exposure cap it below 9 until the multimodal fraud model + audit-grade explainability + DPDP consent plumbing are production-hardened.

---

## 9. Build spec

**Implement:**
1. Conversation FSM (Pipecat/LangGraph) with **auth as guarded policy nodes**, not LLM-discretionary.
2. **Risk engine**: deterministic regulatory-floor rules + ML adaptive step-up; maps {action × signals} → required LoA → factor chain.
3. **Auth orchestrator** with factor matrix: ANI/STIR → OTP (Aadhaar AUA/KUA or DLT-SMS) → voiceprint (passive) → KBA (only as add-on, never sole) → Aadhaar eKYC / DigiLocker / V-CIP for high-LoA.
4. **Anti-spoof + multimodal fraud scorer** running in parallel on the audio stream.
5. **Fuzzy adjudication layer** (date/address/name canonicalization, phonetic + edit-distance thresholds, LLM-judge fallback with strict rubric).
6. **Retry FSM** (no answer-leak, escalating step-up, empathy-bounded).
7. **Signed audit-record emitter** + **DPDP consent capture** (purpose-bound notice + verifiable consent before any voiceprint store).
8. Warm-transfer-to-fraud-desk handoff with full context packet.

**Data needed:**
- Labeled corpus of **genuine vs fraudulent auth calls** (Hinglish + regional), with confirmed-fraud labels.
- In-domain **auth-utterance ASR set** (spelled names, DOBs, addresses, account numbers, code-switched).
- **2026 deepfake attack set** (ElevenLabs, F5-TTS, regional TTS clones) for anti-spoof retraining.
- Edge-identity scenario library (POA, joint, elderly, no-Aadhaar-linked-mobile).

**Eval metrics that gate "good enough to ship":**
- **Security:** False Accept Rate (impostor pass) ≤ regulatory/internal threshold; deepfake-bypass rate on held-out 2026 attack set below target; voiceprint EER <1%.
- **Inclusion:** False Reject Rate (genuine lockout) ≤ 5% on the Hinglish/regional eval set (the human-fairness bar).
- **Latency:** p95 turn gap ≤400ms; p95 end-to-end ≤1.5s.
- **Auth-decision accuracy** vs. human-labeled gold ≥ a fixed bar (e.g. ≥97% agreement on pass/fail) with **zero** silent security-floor violations.
- **Audit completeness:** 100% of decisions emit a complete signed record.
- **DPDP:** 100% of voiceprint captures have logged valid consent.

Ship gate = ALL of: FAR floor met AND FRR ≤5% AND p95 latency met AND zero floor-violations in the eval AND 100% audit/consent coverage.

---

## 10. India specifics

- **Regulatory floors are hard, non-negotiable.** RBI Master Direction KYC + **Authentication Mandate effective 1-Apr-2026** (inherence factors — voice/face — now explicitly recognized). IRDAI for insurance servicing. Aadhaar eKYC **only via licensed AUA/KUA/Sub-KUA** — you cannot DIY UIDAI auth.
- **DPDP Act 2023 + Rules 2025:** voiceprint = biometric → **sensitive personal data**. Needs **purpose-bound notice + verifiable consent** before capture/store; recordings (voiceprint + Aadhaar/account numbers spoken aloud) are personal data. Consent-Manager registration regime opens 12 months from 13-Nov-2026 — design consent plumbing now.
- **Language reality:** must handle Hindi, English, Hinglish + Tamil/Telugu/Bengali/Marathi/Kannada/Gujarati/Punjabi etc., with **mid-sentence code-switching** (>250M Indians code-switch). Use Sarvam / AI4Bharat — generic multilingual models underperform on Indian accents (Bihari/Punjabi-accented Hindi breaks "standard Hindi" models per Vistaar).
- **Spelled-answer hell:** names/addresses spelled in mixed scripts; need Indic-phonetic spell-back ("R for Rajesh / R for Ram") confirmation.
- **OTP fallback reality:** Aadhaar-linked mobile often stale/changed → must offer DigiLocker / offline-XML / V-CIP fallback, not dead-end.
- **Fraud context:** SIM-swap + Aadhaar-data-leak ecosystem makes KBA especially weak in India; lean on OTP + voiceprint + anti-spoof, not security questions.
- **Cost sensitivity (mid-market BPO):** Aadhaar OTP eKYC ₹2–5/txn is non-trivial at scale — reserve high-LoA factors for high-risk actions; use cheap signals (ANI, voiceprint passive) for the routine majority.

---

### Sources
- TruthScan, *2026 Caller Authentication Guide* — https://truthscan.com/blog/caller-authentication/
- Talkdesk, *Voice Biometrics for Contact Centers* — https://www.talkdesk.com/blog/voice-biometrics-for-contact-centers/
- ZipDo, *Best Voice Biometric Authentication Software 2026* — https://zipdo.co/best/voice-biometric-authentication-software/
- Computer-Talk, *Voice Biometrics in the Call Center* — https://www.computer-talk.com/blogs/voice-biometrics-in-the-call-center--the-ultimate-guide
- CX Today, *What is KBA and Why AI Just Broke It* — https://www.cxtoday.com/contact-center/what-is-kba-knowledge-based-authentication-and-why-ai-just-broke-it/
- Au10tix, *What is Knowledge-Based Authentication? A 2026 Guide* — https://www.au10tix.com/blog/what-is-knowledge-based-authentication/
- FTX Identity, *KBA Alternatives in 2026* — https://ftxidentity.com/blog/knowledge-based-authentication-alternatives/
- Bland AI, *Verify Caller Authenticity in Real Time* — https://www.bland.ai/blog/how-can-you-verify-the-authenticity-of-a-caller
- Resemble AI, *Audio Deepfake Detection Benchmark 2026* — https://www.resemble.ai/resources/audio-deepfake-detection-benchmark-results-how-8-systems-performed-in-2026
- CallSphere, *ASVspoof 5 Models in Production 2026* — https://callsphere.ai/blog/vw8e-voice-print-spoofing-detection-asvspoof-2026
- Sarvam AI, *Speech to Text* — https://www.sarvam.ai/speech-to-text
- AI4Bharat IndicConformer — https://huggingface.co/ai4bharat/indic-conformer-600m-multilingual ; Vistaar — https://github.com/AI4Bharat/vistaar
- Deepvue, *KYC in India: 2026 Guide* — https://deepvue.ai/topics/identity-kyc/
- HyperVerge, *RBI KYC Guidelines 2026* — https://hyperverge.co/blog/rbi-kyc-guidelines/
- LexisNexis Risk, *RBI Authentication Mandate* — https://risk.lexisnexis.com/global/en/insights-resources/article/rbi-auth-mandate
- EY India, *DPDP Act 2023 & Rules 2025* — https://www.ey.com/en_in/insights/cybersecurity/decoding-the-digital-personal-data-protection-act-2023
- K&K, *Biometric Data under DPDP Act* — https://ksandk.com/data-protection-and-data-privacy/regulation-of-biometric-data-under-the-dpdp-act/
- Caller Digital, *DPDP Voice AI Compliance Checklist* — https://www.caller.digital/blog/dpdp-act-compliance-checklist-voice-ai-india
- UIDAI Authentication Ecosystem — https://uidai.gov.in/en/ecosystem/authentication-ecosystem.html
- FutureAGI, *Voice AI Barge-In & Turn-Taking 2026* — https://futureagi.com/blog/voice-ai-barge-in-turn-taking-2026/
- CallSphere, *Turn-Taking & Barge-In Tuning 2026* — https://callsphere.ai/blog/vw7d-voice-agent-barge-in-turn-taking-2026
- Hamming AI, *Voice Agent Evaluation Metrics* — https://hamming.ai/resources/voice-agent-evaluation-metrics-guide

*Draft research dossier for review. Cited where possible; [estimate] elsewhere. Not investment/legal advice.*
