# BPO CONTACT-CENTER AGENT — HUMAN→AGENT ADAPTATION MAP

**India-Specific | 2026 Engineering-Grade Decomposition**
**Across 36 Researched Steps | Call Lifecycle → Full Stack**

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [The Human Contact-Center Agent's Job — Fully Decomposed](#2-the-human-contact-center-agents-job--fully-decomposed)
3. [Per-Step Human→Agent Adaptation Table](#3-per-step-humanagent-adaptation-table)
4. [Automation Readiness Tiers](#4-automation-readiness-tiers)
5. [The Enabling Capability Stack](#5-the-enabling-capability-stack)
6. [The "Full Adaptation" Roadmap](#6-the-full-adaptation-roadmap)
7. [Derived Optimal Architecture](#7-derived-optimal-architecture)
8. [MVP Build Sequence](#8-mvp-build-sequence)
9. [Risks & Where It Breaks](#9-risks--where-it-breaks)

---

## 1. Executive Summary

### The Governing Insight

A human contact-center agent's job is not one job. It is at least **36 distinct capability clusters** spanning acoustic perception, regulatory compliance, knowledge retrieval, real-time negotiation, and emotional labor. When decomposed at the micro-step level, the automation picture clarifies sharply: **the parts that feel hard (knowledge lookup, decisioning, wrap-up) are actually near-fully automatable today. The parts that feel simple (empathy, fraud sensing, vulnerability detection) are the hardest to close.**

### Where We Are in 2026

| Tier | Definition | Coverage |
|------|-----------|----------|
| Fully automatable now (8-10/10) | Deterministic, structured, parallelizable; agent matches or exceeds human | 10 of 36 steps (~28%) |
| Automatable with guardrails/HITL (5-7/10) | Agent handles the majority; structured handoff on well-defined failure modes | 21 of 36 steps (~58%) |
| Human-led for now (1-4/10) | Fundamental perception/judgment gaps; AI is a copilot only | 5 of 36 steps (~14%) |

### The Three Structural Gaps

The decomposition reveals that all 5 "human-led" steps and the hardest gaps in the HITL tier share three root causes:

**Gap A — Holistic adversarial intuition under novelty.** Fraud, abuse, and social-engineering detection depend on fusing dozens of weak, never-seen-before signals. Current classifiers only catch in-distribution attacks.

**Gap B — Invisible/quiet vulnerability and masked emotional states.** Detecting genuine financial distress, cognitive decline, or suppressed anger from a caller presenting as calm requires theory-of-mind that no 2026 model reliably has on Indian-accented telephony audio.

**Gap C — Deep Indic dialect comprehension at the phoneme level.** Bhojpuri, Awadhi, Marwari, and sub-district accent variations produce ASR WER spikes of 20-35% that compound every downstream step.

### The Sequence to Full Adaptation

```
Phase 1 (0-90d):   Build the deterministic spine — compliance, action-safety,
                    orchestration, wrap-up, CTI/memory. Ship what is already >=8/10.

Phase 2 (90-180d): Close ASR/TTS/latency. Indic fine-tunes. Hybrid RAG with
                    groundedness gate. Intent + eligibility engine.

Phase 3 (180-365d): Close emotion + vulnerability with multimodal SER. Close
                    fraud with cross-session velocity + coercion detectors.
                    Accumulate 6-12 months of labeled call data. Fine-tune.

Phase 4 (12-24mo): Close the final adversarial/prosodic moats via:
                    (a) RLHF/DPO on real call outcomes,
                    (b) dialect-specific acoustic model expansions,
                    (c) multimodal native speech-to-speech for empathy/de-escalation.
                    Structural augmentation (not replacement) for steps that remain
                    human-led for regulatory/liability reasons.
```

The governing rule: **build the deterministic layers first, then layer the probabilistic ones on top. Every HITL trigger must be a machine-checkable predicate, not a vibe.**

---

## 2. The Human Contact-Center Agent's Job — Fully Decomposed

The call lifecycle has six phases. Every micro-step below is drawn from the 36 researched chunks.

---

### Phase 0: Pre-Call (before the phone is answered)

**Step 0.1 — Mandatory Recording Disclosure & DPDP Consent Setup**

Before the dialer even connects the call, the agent's supporting system must have already:

1. Confirmed the number is not DND/DNC-registered via NCPR scrub.
2. Validated that prior, still-valid, purpose-specific consent exists for this call type.
3. Confirmed the call is within TRAI's 9am-9pm promotional window (or 10am-7pm for promo, 8am-7pm for RBI collections).
4. Checked the daily and weekly contact-frequency counter and cooling-off period for this customer.
5. Confirmed the call is being placed via the correct number series — 140 (promotional), 1600 (BFSI regulated), or normal CLI for transactional calls within 30 minutes of a customer action (TRAI Feb 2025 amendment).
6. Matched the call content to a pre-registered DLT template.

**Why this matters:** Every one of these is a regulatory checklist item with real penalty exposure. The agent performs this pre-flight entirely in the background system; the human agent only sees the resulting "cleared to connect" status.

---

### Phase 1: Call Opening (first 5-10 seconds)

**Step 1.1 — Call Routing & Context Load (CTI Screen-Pop)**

The moment SIP-INVITE fires, the human agent:

1. Reads the ANI/DNIS and IVR-path off the softphone before answering — this gives the first intent prior (which queue, which IVR option pressed).
2. Glances at the screen-pop and sanity-checks that the CTI loaded the right record (name + last-4 sanity check).
3. Resolves identity ambiguity: ANI maps to 2+ accounts (joint card, family plan) — the agent picks the likely one, holds both, or routes to a cold script on no-match.
4. Forms a *why-hypothesis* by fusing: the open ticket, the T-2 failed payment, the last call's unresolved promise, and a recent SMS/email.
5. Scans history for only the 3-5 facts that matter: status/balance, last outcome, open promise/complaint, last sentiment. Not the whole 360-degree view.
6. Detects VIP/vulnerable/repeat-caller flags (5th call this week = frustrated; HNI tag = white-glove handling).
7. Decides language register before speaking: past-interaction language tag + region of number + name → opens in Hindi, mirrors Hinglish.
8. Smell-tests for fraud or wrong-person: voice doesn't match expected age/gender, caller fishing for info, unusual agitation → raise auth bar.
9. Pre-loads the likely tool/workflow: opens dispute form or payment screen before the customer even asks.
10. Sets required auth level: read-only = 2FA; financial action/KYC = full step-up per RBI/IRDAI graduated auth.
11. Carries forward cross-channel state: if the customer WhatsApp'd an hour ago and abandoned → continues that thread.
12. Discards noise: suppresses a stale or clearly-wrong screen-pop rather than being misled by it.

**Step 1.2 — Mandatory Recording Disclosure & Consent Delivery (On-Call)**

1. Opens with the recording disclosure verbatim — "this call is being recorded for quality and training" — in the customer's language, before any PII is spoken.
2. Delivers the DPDP notice and purpose at point of collection: plain-language statement of what data is processed and why.
3. (AI-agent only) States clearly: "you are speaking with an automated assistant" — IT Amendment Rules 2026.
4. States company and representative identity.
5. Asks the affirmative-consent question and waits for an unambiguous "haan/yes/theek hai" — silence is not consent.
6. Branches on refusal: switches to a no-record path if supported, or ends the call politely.
7. Gates cross-sell separately: promotional cross-sell needs its own consent and promo-category DND clearance.
8. Gives the withdrawal route inside the prompt.
9. Sequences all of this before any substantive talk — holds the discipline even under "haan haan chhodo, kaam batao" pressure.
10. Logs the consent artifact precisely: consented/refused, timestamp, language, and which notice version.

**Step 1.3 — Greeting, Identity Verification & Authentication**

1. Pre-call context absorption: in 1-2 seconds, glances at screen-pop — ANI, IVR path, CRM match, last contact, open tickets, language/VIP/risk flags.
2. Delivers the mandated brand greeting at correct pace and warmth in the right language.
3. Detects language within the first utterance and mirrors the caller's register and formality.
4. Pre-reads intent and emotion (angry/distressed/routine) from the opening line — sets tolerance for auth friction.
5. Captures the claimed identity (name/account/policy/mobile), parsing spelled names and digit strings over noisy lines.
6. Looks up the record and disambiguates duplicates ("do Rahul Sharma hain, DOB batayein"), handles no-match gracefully.
7. Decides the assurance level (LoA): how hard to authenticate, from action sensitivity × ANI trust × account risk × fraud patterns.
8. Selects the authentication factor chain: ANI, OTP-to-registered-mobile, KBA, Aadhaar OTP eKYC, voiceprint, DigiLocker.
9. Delivers the challenge, triggers OTP, prompts the biometric phrase, and captures the answer.
10. Adjudicates "close enough" — fuzzy-matches dates ("4 April" vs "04/04"), addresses ("MG Rd" vs "M.G. Road").
11. Handles soft-fails: benign error (allow retry, reassure) vs suspicious (step up/lock) without leaking which answer was wrong.
12. Senses fraud instinct: hesitation, background coaching voices, pushy urgency, robotic/synthetic timbre, voice-profile mismatch.
13. Declares verified at level L, logs it, sets scoped session permissions — or fails closed to fraud/manual desk.
14. Empathetically cushions friction throughout: apologizes for security, explains "aapki suraksha ke liye", keeps caller calm.

---

### Phase 2: Understanding (seconds 10-60)

**Step 2.1 — Active Listening & Understanding Messy Real Speech**

1. Acoustic gain and focus: mentally suppresses TV/family/street noise, locks onto the caller's voice.
2. Speaker tracking: locks on THE customer's voice even when a family member talks or grabs the phone.
3. Phoneme repair under degradation: fills in muffled/clipped syllables from context.
4. Code-switch parsing: reads a Hindi+English intra-sentence mix as one coherent thought.
5. Accent normalization: maps Bhojpuri/Tamil/Bengali-accented phonemes on the fly.
6. Disfluency stripping: discards "haan woh, matlab, kya bolun, actually" and keeps propositional content.
7. Number/entity capture under stress: locks a 16-digit card/policy/OTP/amount spoken fast and noisily.
8. Endpoint/turn-end judgment: decides if the caller finished a thought or is pausing to recall a number.
9. Barge-in handling: stops talking instantly when the customer cuts in.
10. Talk-over disambiguation: when both speak at once, decides whose content matters.
11. Prosody/emotion read: hears irritation/panic/sarcasm in HOW it is said.
12. Confidence and repair decision: knows when something wasn't caught and asks a surgical targeted repeat.
13. Context-carry: remembers what was said 3 turns ago to resolve a pronoun or half-spoken reference.
14. Silence/hold tolerance: correctly reads a long silence as fetching card vs dropped call vs annoyance.

**Step 2.2 — Language, Dialect & Code-Mixing Handling**

1. Passive language inventory: within 1-2 seconds forms an implicit profile of base language, English comfort, register, and rough dialect/region.
2. Matrix-language decision: picks the base language to anchor the reply.
3. Borrowing vs switching discrimination: distinguishes a naturalized loanword (account, balance, block) to keep verbatim from a genuine switch to mirror.
4. Mid-sentence switch tracking: follows language flips within one breath.
5. Entity preservation across scripts: locks alphanumerics, names, amounts exactly without translating or rounding.
6. Register mirroring: mirrors formality/warmth; respectful "aap/ji" for elderly/formal callers.
7. Dialect accommodation: adjusts comprehension for Bhojpuri-tinged, Marwari, Mumbai-Hindi.
8. Repair on mismatch: gracefully re-anchors if wrong base language was guessed.
9. Code-mixes the reply: answers in the same mixed style the caller used.
10. Compliance-language gating: delivers mandatory disclosures in a language the customer actually understands.
11. Pronounces the other language's tokens faithfully on readback.
12. Continuous re-profiling: live-tracks and drifts with the caller.

**Step 2.3 — Intent Recognition & Disambiguation**

1. Catches the literal words even when broken/code-mixed/disfluent.
2. Strips noise: drops fillers, repeats, self-corrections.
3. Maps register and emotion because emotion reshapes intent priority.
4. Forms a small hypothesis set of 2-3 candidate intents, not a single guess.
5. Pulls silent context priors: recent transaction, product held, last ticket, IVR path, time-of-month.
6. Meta-cognitively estimates own confidence — "do I actually know what they want?"
7. Decides commit/clarify/probe/escalate based on that confidence.
8. Crafts ONE minimal disambiguating either/or that maximally splits the hypothesis set.
9. Detects multi-intent or hidden intent (stated "cancel policy" = real "waive this charge").
10. Re-anchors the hypothesis live as the caller answers.
11. Confirms understanding in the caller's own words before acting.
12. Logs the resolved intent and reason for wrap-up/next agent.

**Step 2.4 — Emotion & Sentiment Reading**

1. Acoustic baseline calibration in first 3-8 seconds: fixes the caller's normal pitch/pace/loudness/accent.
2. Continuous arousal tracking: notices energy/pitch-range/speech-rate spikes.
3. Continuous valence read: positive vs negative tilt.
4. Specific-emotion labeling: frustration, anger, anxiety/distress, confusion, resignation/hopelessness, satisfaction, impatience/urgency.
5. Lexical-affect fusion: combines WHAT was said with HOW.
6. Sarcasm/incongruence detection: catches when words and prosody/context disagree.
7. Masked-distress detection: over-controlled calm, long pauses, voice tremor, swallowed words.
8. Urgency vs anger disambiguation: fast+loud can be time-pressure OR anger; resolves via content.
9. Cause attribution: is the negative affect AT me/company (complaint), at the situation (sympathy), or trait?
10. Trajectory/derivative read: tracks the SLOPE — cooling after apology or still climbing.
11. Threshold-to-action mapping: converts affect read into decision (soften, apologize, slow down, stop pitching, escalate).
12. Cultural/register adjustment: re-weights everything for region, gender, age, formality.

---

### Phase 3: Serving (the core of the call)

**Step 3.1 — Empathy, Rapport & De-escalation**

1. Detects emotion from voice before words: reads arousal and valence from prosody.
2. Detects emotion from words: lexical cues, legal/social-media/RBI threats, swearing.
3. Estimates intensity and trajectory.
4. Hypothesizes root-cause of the anger: money lost/time wasted/felt disrespected/fear.
5. Judges "at-me or at-situation": separates personal abuse from situational venting.
6. Selects tactic: acknowledge → validate → apologize → reassure → set-expectation → solve (LAST/HEARD), conditioned on live state.
7. Decides vent-vs-interject: stays silent and lets them finish a rant, or steps in.
8. Sets pacing: slows own speech, lowers volume, inserts a beat of silence to model calm.
9. Selects register/honorifics: "ji/sir/ma'am", switches to customer's language.
10. Renders empathy with congruent prosody: soft, slower, downward intonation, never chirpy.
11. Backchannels while they vent: low-volume "hmm/ji/haan/samajh raha hoon".
12. Names the emotion and validates the specific grievance; micro-apologizes without admitting liability.
13. Bridges calm to action: "here's exactly what I'll do right now."
14. Re-reads state after the move; if not cooling, re-validates or changes tactic; holds boundary if abused; escalates if beyond scope.

**Step 3.2 — Knowledge Lookup & Grounding**

1. Parses the answerable question out of a messy turn.
2. Classifies the knowledge type: static policy vs account-specific fact vs procedure vs regulatory/legal.
3. Picks the authoritative source (MITC/sanction letter/product master/circular), not a convenient stale one.
4. Disambiguates the variant: product, segment, scheme code, vintage, fixed vs floating.
5. Resolves effective-date/version — is this today's schedule or grandfathered old terms?
6. Locates the exact literal clause/number, not a paraphrase.
7. Cross-checks for contradiction and applies precedence (regulation overrides product sheet).
8. Calibrates confidence and decides guess vs verify vs abstain.
9. Actively suppresses the plausible-but-wrong answer that merely sounds right.
10. Translates clause-language into customer Hinglish while preserving numbers exactly.
11. States it with an authority hedge ("as per current policy") so the answer is defensible.
12. Separates policy-fact from account-specific-fact.
13. Logs what was answered for QA traceability.

**Step 3.3 — Multi-Turn Context & Working Memory**

1. Anchors the call frame in the first 2-3 turns: locks primary intent + entities in play.
2. Maintains a running entity register: caller, account, "wife" = Sunita, "policy" = the ULIP not the term plan.
3. Tracks co-reference and deixis: resolves "woh/uska/yeh/that-one/pehle-wala" to the correct prior entity.
4. Holds the open-loop stack: what is promised-but-not-done.
5. Tracks dialogue-act/task state: mid-auth, mid-disclosure, waiting for OTP, collecting a reason.
6. Reconciles corrections and retractions: "Rs12,400... sorry Rs14,200" → overwrites old value AND propagates downstream.
7. Carries emotional/relationship state: caller angry at minute 2, calmed by minute 6.
8. Suppresses repetition: never re-asks an already-answered slot.
9. Bridges interruptions, barge-ins, and holds.
10. Segments 2-3 jobs within one call; keeps each job's state separate but linked.
11. Time-orders facts so recency wins.
12. Selective forgetting/salience: drops small-talk and abandoned tangents.
13. Pre-loads remembered context into the next utterance to signal tracking.
14. Hands the thread off cleanly: compresses the whole call into a 2-line state summary for transfer/escalation.

**Step 3.4 — Eligibility Checks & Decisioning**

1. Frames the ask precisely: converts fuzzy request into a typed eligibility question.
2. Selects the governing rule set by product, segment, state, channel, regulator, and effective-date version.
3. Inventories required attributes: tenure, DPD/bucket, CIBIL band, KYC, exposure, age, cooling-off, prior claims.
4. Pulls facts from systems: CRM/LOS/policy-admin/CIBIL/core-banking.
5. Detects missing/conflicting facts and asks the one decisive missing input.
6. Verifies volunteered facts: decides whether customer-stated income/employment can be trusted or needs verification.
7. Runs the rule: applies thresholds/branches — meets-all=eligible, fails-one=ineligible, near-miss=exception candidate.
8. Identifies the binding constraint: the ONE rule that failed.
9. Checks for exception/override paths: waiver authority, supervisor override, alternate product, manual-underwriting queue.
10. Computes conditions and sub-limits: max amount, revised tenure, co-applicant required, premium loading.
11. Decides confidence and whether to commit.
12. Translates verdict into customer-appropriate empathetic Hinglish.
13. Offers next-best alternative/remedy: down-sell, cure path, alternate product.
14. Logs the decision + reason + evidence + rule version.

**Step 3.5 — Compliance & Mandatory Disclosures (Mid-Call)**

1. Identifies the regulatory regime in play: RBI-lending vs IRDAI-insurance vs DPDP-generic vs RBI-recovery.
2. Sequences disclosures correctly: recording + AI-identity before any PII; KFS before contract; free-look before close.
3. Delivers mandatory disclosures verbatim-enough.
4. Detects customer's preferred language and switches the mandatory script.
5. Captures explicit affirmative consent — waits for unambiguous "haan/yes/theek hai".
6. Distinguishes consent scope: record vs process-for-purpose vs marketing are separate, never bundled.
7. Reads mandatory product disclosures at the right trigger point.
8. Plain-language translates jargon without changing legal meaning.
9. Handles consent refusal gracefully.
10. Detects vulnerability/non-comprehension and slows down or flags.
11. Logs the consent event with timestamp, language, and disclosure version.
12. Resists customer attempts to skip disclosures.
13. Answers compliance follow-ups truthfully.
14. Produces the audit-ready record.

**Step 3.6 — Objection Handling & Negotiation**

1. Detects that an objection actually occurred vs a stall, a question, or noise.
2. Classifies objection type: affordability/dispute-validity/willingness/authority-deferral/trust-scam/emotional/procedural.
3. Reads emotional temperature from prosody + words + latency.
4. Decides stance instantly: empathize-first vs inform-first vs concede vs hold-firm vs de-escalate.
5. Acknowledges/validates before responding.
6. Diagnoses the REAL objection under the stated one.
7. Selects the right lever from a mental playbook: PTP split, partial, settlement %, fee waiver, retention offer, value reframe, compliant consequence framing.
8. Frames the lever to THIS person's language register, constraint, and inferred personality.
9. Quantifies the offer within authority limits: anchors above floor, concedes in small steps.
10. Delivers a specific ask and micro-commitment.
11. Handles the counter-objection by looping without repeating an already-rejected lever.
12. Knows when to STOP: hard no, genuine hardship, real dispute, or harassment line.
13. Closes the loop mechanically: captures PTP amount+date, fires payment link, confirms, sets callback.
14. Self-regulates own tone: stays warm and unflappable under abuse.

**Step 3.7 — Cross-Sell / Up-Sell Judgment**

1. Resolution-state check — never pitches until the original problem is fully solved.
2. Emotional-valence read — detects positive/neutral vs frustrated/rushed/angry.
3. Effort-state read — suppresses even a relevant offer if the call was already long/painful.
4. Trust-window detection — waits for a positive micro-moment.
5. Time/permission read — suppresses or heavily compresses if customer signals time pressure.
6. Need-inference from context: maps what just happened to a latent need.
7. Eligibility and holding check — never pitches what they already own or can't get.
8. Suitability judgment — conscience filter: is this GOOD for them?
9. Propensity intuition — "will THIS person actually say yes?"
10. One-best-thing selection — picks the single most relevant offer, never dumps a menu.
11. Permission pre-frame — micro-consent ask before pitching.
12. Relevance-anchoring — ties the offer explicitly to what just happened.
13. Restraint/graceful-no — reads the first hint of disinterest and drops it instantly.
14. Frequency memory — remembers who was already pitched/said no across calls.

**Step 3.8 — Backend Action Execution**

1. Verbally re-confirms the exact resolved action before touching any system.
2. Runs an authority/eligibility self-check.
3. Pulls the correct record in CRM/CBS and disambiguates look-alikes.
4. Reads current state before writing: already refunded? pending duplicate ticket? account frozen?
5. Computes the exact payload: gross vs net-of-GST refund, original channel, plan-change effective date.
6. Captures and verbalizes the authorization artifact: OTP/verbal consent/consent token.
7. Executes the write — often across two screens.
8. Watches the system response: success/fail code, timeout, gateway down.
9. Reconciles partial failure: if refund fired but ticket didn't save, fixes only the dangling half.
10. Generates and reads back the proof: captures reference/ARN/SR number and speaks it.
11. Logs disposition and free-text notes for the next agent.
12. Decides on escalation: if amount too high/eligibility unclear/system erroring, stops and warm-transfers to L2.

---

### Phase 4: Control & Exception Handling

**Step 4.1 — Silence / Dead-Air & Hold-Mute Etiquette**

1. Detects a coming wait and classifies it: short cognitive fill vs long system wait vs off-stage mute.
2. Drops a pre-emptive micro-acknowledgement instantly so there is zero silence.
3. Narrates the screen continuously during a medium wait.
4. Makes an explicit hold request with all three parts: reason + estimated duration + actual permission ask.
5. Waits for and registers consent before going on hold.
6. Engages hold cleanly so customer hears hold tone/music, not the agent's background.
7. Checks back on a 30-45 second cadence before the customer gets anxious.
8. Honours the quoted time or renegotiates.
9. Returns from hold deliberately: thanks for holding, apologizes for wait, immediately delivers value.
10. Mutes to cough/sneeze/consult a team lead.
11. Un-mute safety check: confirms the off-stage exchange ended before speaking.
12. Offers callback proactively if wait gets very long.
13. Reads customer tolerance and adapts: irate/rushed get shorter holds.

**Step 4.2 — Fraud / Abuse / Social-Engineering Caller Handling**

1. Pressure-pattern sensing: reads the SHAPE of the request (artificial urgency, authority citation, secrecy, fear, reward bait).
2. Coercion/live-coaching detection: hears a second background voice, dictation pauses, repeated phrases — the authenticated holder being puppeted.
3. Never-ask tripwire: recognizes the caller steering toward OTP/CVV/PIN/full card/full Aadhaar.
4. Pretext deconstruction: decodes the cover story and tests it against policy.
5. Repeated-failure/probing read: distinguishes a benign fumbling customer from systematic probing (ATO in progress).
6. Step-up-on-suspicion: raises the auth bar independently of nominal action risk.
7. Hard-refuses the risky mutation: says NO to cred reset/mobile-email change/beneficiary add/limit hike/SIM-swap when suspicion is live.
8. Refuses without leaking: declines without confirming account details or revealing which signal tripped.
9. Holds the line under escalating pressure.
10. Abuse classification and warning ladder: separates frustration vs abuse vs fraud-aggression.
11. Defined cutoff execution: after 2-3 warnings terminates cleanly.
12. Fraud-ops flag and case raise: marks account/session as suspected fraud, triggers NCRP/1930 golden-hour hold.
13. Evidence preservation: keeps recording/transcript, the signals that tripped, exact request refused.
14. Warm contextful handoff to the fraud desk.

**Step 4.3 — Escalation Decision & Warm Handoff**

1. Scope check — every turn, "is this request inside what I'm authorized/able to do?"
2. Progress check — "am I moving toward resolution or going in circles?"
3. Emotional-temperature read — detects rising frustration/distress/abuse.
4. Risk/compliance sniff — catches dispute, harassment, ombudsman/RBI/IRDAI mention, self-harm, legal/media threat.
5. Explicit-request catch — caller literally says "human se baat karao/supervisor/manager/insaan."
6. Threshold weighing — fuses all signals into one escalate-vs-keep-trying call, weighted by consequence.
7. De-escalation-first instinct — tries to calm/solve once before transferring.
8. Route selection — picks the CORRECT human: supervisor vs fraud desk vs grievance officer vs claims/retention specialist.
9. Availability/expectation reality-check — is that queue staffed? offer callback vs 20-minute hold?
10. Sets customer expectation: "connecting you to a specialist who can do X; you won't have to repeat everything."
11. Mentally compresses the case: 3-5 line summary.
12. Whisper/briefing: privately tells the receiving agent the summary before bridging the caller.
13. Consent/permission carry-over: communicates what caller already authorized.
14. Clean bridge and graceful exit: connects, confirms receiving agent has it, exits with no dead air.

**Step 4.4 — Supervisor Whisper / Real-Time Coaching & Barge-In**

1. Live-floor scanning: keeps peripheral watch over many simultaneous live conversations.
2. Risk-prioritized attention allocation: decides which session deserves the next 30 seconds.
3. Drop-in silent monitoring: opens one session and listens/reads silently.
4. Rapid context-load: reconstructs who the customer is, the intent, what has been tried.
5. Coach-vs-barge decision: judges whether a whisper hint will save it or the supervisor must take over.
6. Whisper formulation: crafts a short, actionable in-the-moment hint.
7. Whisper delivery timing: injects the hint at a natural gap.
8. Barge-in/graceful seizure: announces appropriately, smoothly assumes control.
9. State/context inheritance on takeover.
10. Mid-call wrong-action catch: stops/redirects the agent before a wrong figure/wrong account/script breach causes harm.
11. Multi-session context-switching: bounces between sessions holding partial state for several at once.
12. Post-intervention handback/disposition: returns control (whisper) or closes out (barge), tags what happened.
13. In-the-moment coaching note: captures WHY the intervention was needed.
14. Composure and judgment under pressure: stays calm, decides fast.

**Step 4.5 — Vulnerable-Customer & Duty-of-Care Handling**

1. Driver-scanning while serving — continuously listens for FCA four vulnerability drivers (Health, Life events, Resilience/financial hardship, Capability/literacy).
2. Acute-risk listening — catches self-harm/suicidal-ideation, domestic-abuse, and medical-emergency signals as a separate higher-urgency channel.
3. Disclosure-handling reflex — validates without prying when a customer volunteers a vulnerability.
4. Care-mode switch — slows pace, drops jargon, shortens sentences, lowers cognitive load.
5. Comprehension-confirmation loop — teach-back: asks the customer to restate what they understood.
6. Sales/up-sell suppression — actively withholds the cross-sell the script would normally trigger.
7. Aggressive-collection suppression — stands down dunning/urgency/penalty-threat scripts on genuine hardship.
8. Hardship/forbearance offering — proactively surfaces EMI pause/restructure, cooling-off, fee waiver.
9. Capacity/coercion check on transactions — senses whether a confused/elderly caller truly understands/wants it.
10. Accessibility accommodation — slower/louder speech, read-out/resend, carer on line, comfort-language switch.
11. Specialist/helpline routing — routes to vulnerable-customer desk/senior human, or for acute self-harm warm-bridges to Tele-MANAS 14416.
12. Sensitive, minimal recording — flags vulnerability for care-continuity, minimal/lawful under DPDP.
13. Holds firm on protection — withholds the vulnerable customer's OWN insistence when safeguard rules apply.
14. Graceful close and safety-net — ends with helpline/next-step info and a comprehension check.

---

### Phase 5: Closing & After-Call Work

**Step 5.1 — Call Wrap-Up & Disposition Coding**

1. Recalls the gist: reconstructs the call's intent from working memory.
2. Identifies the ONE primary reason-for-contact even when 3 issues were raised.
3. Spots secondary intents / cross-sell hints / churn-risk signals / repeat-caller frustration.
4. Determines the outcome: resolved/unresolved/escalated/callback/sale/no-sale.
5. Maps intent+outcome to the CRM disposition dropdown — often a 40-200 code taxonomy with overlapping entries.
6. Resolves taxonomy ambiguity using unwritten team convention.
7. Picks sub-disposition/reason codes.
8. Writes the free-text note for the next agent.
9. Captures action commitments as SLAs.
10. Updates structured CRM fields: account status, follow-up date, consent tick, contact preference, DPDP purpose-tag.
11. Triggers downstream workflow: create ticket, fire callback task, push to retention queue, send e-mandate/SMS.
12. Self-QA sanity check: "did I tag right? will QA flag me?"
13. Compliance tagging: was consent recorded? was a mis-selling disclosure made?
14. Emotional reset: dumps the previous (possibly abusive) call to be fresh for the next.

**Step 5.2 — After-Call Work & Follow-Up**

1. Recalls the call in working memory: reason, what was promised, customer emotional state, any committed date/amount.
2. Decides the disposition code from a 30-200 code taxonomy.
3. Writes the call summary/disposition note: factual, tone-neutral.
4. Extracts structured commitments: PTP amount+date, appointment slot, callback date/time, refund, docs to send.
5. Updates CRM/case fields: status, sub-status, next-action-date, amount, contact-preference.
6. Creates or updates the ticket: open/link case, set priority/queue/owner.
7. Schedules the callback/appointment in a legal+free slot (RBI 08:00-19:00 window).
8. Fires the promised outbound: SMS/WhatsApp/email with correct DLT-approved template in the right language.
9. Reconciles against consent/DND/DPDP state before any action.
10. Sets grievance/escalation trail: routes with context, generates complaint reference + SLA per RBI/IRDAI.
11. Self-checks completeness: re-reads, verifies every promise captured.
12. Mentally closes the loop and context-switches to the next call.

---

### Phase 6: Continuous Quality & Operations

**Step 6.1 — QA / Eval Flywheel**

1. Recalls and loads the correct rubric/scorecard for this specific call type.
2. Identifies call context from metadata before listening.
3. Listens for mandatory opening disclosures: binary pass/fail under RBI FPC and IRDAI norms.
4. Scores compliance gates first (auto-fail check).
5. Scores empathy and tone on Likert 1-5 by listening to vocal quality.
6. Evaluates code-switch quality.
7. Tracks internal consistency: promise made at minute 3 — was it delivered by minute 12?
8. Scores problem resolution: genuinely resolved or deferred without commitment?
9. Evaluates call close: summary, reference number, next-step, survey consent.
10. Exercises borderline judgment: rubric gives integer 1-5 but call is 3.5.
11. Writes actionable coaching notes in agent's language (Hinglish).
12. Flags anomalies for escalation.
13. Participates in calibration sessions: double-blind review of AI-scored calls.
14. Monitors weekly score distributions for drift signals.

**Step 6.2 — Observability & Cost-Per-Resolution**

1. Agent clocks into ACD; system records exact start timestamp.
2. Agent presses ACW at call end, transitioning status and starting after-call-work timer.
3. Agent selects disposition code encoding resolution type.
4. Agent clicks Ready to return to queue; WFM records AHT = talk + hold + ACW.
5. Mentally assesses FCR (first-contact resolution) and notes if unresolved.
6. QA analyst pulls 2-5% random call sample from recording system 24-72h post-call.
7. QA analyst listens full recording and scores rubric.
8. Finance maps agent FTE fully-loaded cost ÷ calls handled = cost per call.
9. Finance computes gross margin per client.
10. Supervisor manually monitors queue depth and skill-match.
11. Finance flags cost overrun > 20% above plan.
12. Compliance ensures call recordings retained per mandate: RBI 5yr BFSI, IRDAI 3yr, CERT-In 180-day minimum.
13. On regulatory audit request, compliance officer manually retrieves specific call recording + disposition log.
14. Compliance officer verifies PII in call notes not retained beyond DPDP purpose limitation.

---

### Cross-Cutting Capabilities (Infrastructure, Not Steps)

**Real-Time Voice Pipeline & Latency Engineering** — VAD, ASR, TTS, barge-in, turn-taking running at sub-700ms end-to-end.

**Indic ASR Engineering** — code-mixed Hindi+regional, telephony 8kHz audio, noise compensation, accent normalization.

**Indic TTS & Prosody** — natural, emotional, fast, multi-language, interruptible synthesis.

**Agent Orchestration, Routing & HITL Interrupts** — LangGraph/Agent-SDK, planner, session state, HITL triggers.

**Memory Architecture** — session + customer long-term + org memory; personalization layers.

**RAG Grounding, Citation & Hallucination Guardrails** — refuse-and-escalate on low retrieval confidence.

**Action Safety** — idempotency keys, dry-run, rollback, value thresholds, immutable audit ledger.

**Compliance-as-Code Engine** — machine-enforced RBI/IRDAI/DPDP rules, consent ledger.

**Security, DPDP, PII Redaction & Data Localization** — in-country VPC/on-prem, encryption.

**Telephony/CPaaS & Omnichannel Integration** — SIP/CTI transfer, WhatsApp BSP, channel unification.

**Concurrent Multi-Session Context Isolation** — blending discipline, PII leak prevention across sessions.

---

## 3. Per-Step Human→Agent Adaptation Table

| Step | Human Micro-Steps (count) | Key Micro-Steps | 2026 Agent Approach | Readiness /10 | HITL Trigger | Key Gap to Close |
|------|--------------------------|-----------------|---------------------|--------------|--------------|------------------|
| **0.1 Pre-call compliance check** | 6 | DND scrub, consent-on-file, time-window gate, frequency counter, number-series, DLT template match | OPA Rego policies per regulator; pre-flight evaluation FastAPI gate; full deterministic enforcement | 9 | New regulatory circular requiring manual policy diff review | Novel regulatory interpretation; stale Rego = compliance gap |
| **1.1 CTI screen-pop & context load** | 12 | ANI/IVR prior; CRM pop; fraud smell-test; cross-channel state; language-register decision | LangGraph pre-turn graph: sip_meta → crm_lookup → identity_resolve → risk_score → intent_predict → context_summarize → auth_policy; typed Pydantic CallContext | 8 | Identity confidence below threshold AND sensitive action requested | Probabilistic sparse-signal fraud intuition; multi-account disambiguation |
| **1.2 Recording disclosure & DPDP consent** | 14 | Verbatim compliance open; AI identity disclosure; affirmative consent capture; consent refusal branch; cross-sell separate consent; audit log | Deterministic compliance FSM (not LLM-discretionary); per-regime obligation manifest; consent ledger with timestamp + version | 8 | Consent refused with no configured no-record path; vulnerability/confusion score above threshold | Graceful barge-in delivery; robotic-read avoidance on elderly/confused callers |
| **1.3 Greeting, identity verification & auth** | 14 | LoA decision; auth factor chain selection; close-enough adjudication; fraud instinct | Layered continuous auth woven into conversation; CTI/ANI + CRM as structured pre-call context; GUARDED policy FSM nodes; ML adaptive step-up | 7 | Anti-spoof/fraud-risk score high; exhausted retries without clear pass/fail; explicit human request | Holistic fraud intuition from weak multi-signal fusion; "coached call" coercion detection |
| **2.1 Active listening & messy speech** | 14 | Acoustic gain/focus; phoneme repair; code-switch parsing; number capture under stress; endpoint judgment | DeepFilterNet3 denoise → Silero VAD v5 → Sarvam Saaras v3 ASR with partial transcripts; per-token confidence; targeted re-prompt on low-confidence entities | 7 | Repeated low-confidence on critical entity after 2 re-prompts; sustained heavy overlap; critical entity never validated | ASR metacognition (overconfident on noisy codemix); new-dialect WER spikes |
| **2.2 Language, dialect & code-mixing** | 12 | Matrix-language decision; borrowing vs switching discrimination; entity preservation across scripts; compliance-language gating | End-to-end code-switch-native ASR (Saaras V3); language-profile tracker state object; per-segment lang tags+confidence; NO utterance-level LID router | 7 | Customer requests different language; compliance disclosure unclear due to dialect gap; WER > threshold on critical entity | Deep dialect comprehension (Bhojpuri/Awadhi/Marwari); compliance-language gating in edge-dialects |
| **2.3 Intent recognition & disambiguation** | 12 | Hypothesis set formation; silent context priors; confidence metacognition; ONE disambiguating probe; hidden intent detection | Streaming code-switch ASR → fine-tuned MuRIL/IndicBERT → conformal prediction → uncertainty routing → Claude Sonnet for ambiguous | 7 | Conformal prediction set empty or > threshold; ASR confidence below floor after one clarify attempt | Meta-cognitive confidence on novel/garbled off-distribution asks; UNSTATED intent from sparse cues |
| **2.4 Emotion & sentiment reading** | 12 | Acoustic baseline calibration; trajectory/derivative read; sarcasm detection; masked-distress detection; cause attribution | Always-on streaming SER (emotion2vec_plus / fine-tuned WavLM) every 300ms; late-fused with IndicBERT text track; AffectState struct | 5 | Distress/anxiety/hopelessness above confidence threshold; Hinglish sarcasm undetected; repeated SER timeout | Masked/suppressed distress; Hinglish sarcasm/irony; cause attribution (trait-vs-state) |
| **3.1 Empathy, rapport & de-escalation** | 14 | Vent-vs-interject decision; pacing modulation; congruent prosody; re-read after each move; boundary under abuse | Streaming SER late-fused with transcript sentiment → empathy-class LLM with de-escalation playbook; EVI-3/Octave prosody; hard guardrails on self-harm/abuse | 6 | Self-harm/suicidal ideation/violence; sustained rage after 2 de-escalation attempts; explicit human request; regulatory vulnerability flag | Adaptive re-generation under sustained adversarial/abusive/novel turns; policy revision mid-storm |
| **3.2 Knowledge lookup & grounding** | 13 | Authoritative-source selection; effective-date/version resolution; confidence calibration; active suppression of plausible-wrong | Hybrid RAG (BM25 + BGE-M3 dense, RRF fusion); BGE Reranker v2-m3; groundedness verifier (NLI/LLM); abstention classifier; Pydantic-validated citation schema | 7 | Groundedness verifier fails AND corrective re-retrieval also fails; conflict between two authoritative sources | Authoritative-source instinct on incomplete/contradictory KBs; calibrated abstention on edge cases |
| **3.3 Multi-turn context & working memory** | 14 | Entity register maintenance; co-reference/deixis resolution; open-loop stack; correction propagation; selective salience | Typed Session State Object + mem0 memory layer; Context Assembler per turn; episodic memory for cross-call recall; entity resolution via pragmatic-inference layer | 7 | Memory conflict with no recency resolution; entity resolution failure on safety-critical field; agent loops on a completed sub-task | Implicit never-stated context; correction propagation across dependent computations |
| **3.4 Eligibility checks & decisioning** | 14 | Governing rule set selection; binding constraint identification; exception/override path detection; next-best alternative | LLM orchestrator + deterministic DMN/OPA-Rego/Cedar policy engine; LLM handles language/framing; engine gives 100% reproducible verdict; versioned policy registry | 8 | Manual-underwriting/discretion path; near-miss or override-candidate flagged as human-authority-only | Getting clean/verified inputs; discretion/exception judgment on novel edge cases |
| **3.5 Compliance & mandatory disclosures** | 14 | Regime identification; disclosure sequencing; affirmative consent capture; vulnerability detection; log consent artifact | Deterministic compliance state-machine wrapped around LLM; per-regime obligation manifest loader; vulnerability/confusion sensor triggers HITL | 7 | Vulnerability/confusion score exceeds threshold; agent skips or truncates a mandatory disclosure; consent refusal | Vulnerability + comprehension sensing (duty of care); graceful handling when customer pushes back |
| **3.6 Objection handling & negotiation** | 14 | Objection type classification; real-objection diagnosis; lever selection from playbook; authority-limit anchoring; stop-condition recognition | 2-level objection-intent classifier on streaming ASR; real-time SER for escalation slope; orchestrator brain LLM with empathize-before-lever template; deterministic engine for numbers/authority | 5 | Genuine hardship/financial-distress disclosure; dispute/"not my debt"/"already paid" unverifiable; sustained abuse | Dynamic mid-objection stance-switching; restraint calibration under ambiguity |
| **3.7 Cross-sell / up-sell judgment** | 14 | Resolution-state check; effort-state read; trust-window detection; suitability judgment; single-best-offer selection; graceful-no | Two-layer split: per-turn boolean moment-gate (deterministic) + eligibility+suitability rules engine + LLM for framing only; frequency-memory service | 5 | High-value/complex regulated products (ULIP, investment-linked); suitability assessment requires financial advice license | RESTRAINT calibration — subtle disinterest signals; ironic or indirect disengagement; faint cues to not pitch |
| **3.8 Backend action execution** | 12 | Pre-action consent re-confirm; authority self-check; current-state read; payload computation; partial failure reconciliation | LLM PROPOSES; Action Gateway (deterministic MCP tools) EXECUTES; Propose→Validate→Confirm→Commit→Verify→Log; idempotency keys; saga compensation | 5 | Action amount/impact exceeds policy cap; system returning unrecognized error code; conflicting system states | Cross-system implicit reconciliation under ambiguity; never-seen two-system failure combo |
| **4.1 Silence / dead-air & hold etiquette** | 13 | Wait type classification; permission ask before hold; check-back cadence; honour quoted time; mute safety check | Deterministic wait-aware FSM (ACTIVE/FILLING/HOLD_REQUEST/HOLD/RETURN); driven by tool-call lifecycle events NOT LLM text; tool latency registry | 8 | Max-hold budget breached; customer verbally signals distress on hold; hold etiquette is the canary for underlying escalation trigger | Truly adaptive read-the-room cadence based on subtle vocal trajectory cues |
| **4.2 Fraud / abuse / social-engineering** | 14 | Pressure-pattern sensing; coercion/live-coaching detection; never-ask tripwire; pretext deconstruction; refuse-without-leaking | Parallel sentinel track (off 400ms response path): SE classifier + abuse/threat classifier + diarization/coercion detector + anti-deepfake + cross-session velocity engine → calibrated fraud_risk score | 5 | Manipulation/coercion/deepfake/velocity score crosses high-risk threshold; attempted SIM-swap/OTP social engineering; any novel pretext | Holistic adversarial intuition under novelty; slow-burn multi-call grooming; live-coached deepfake call |
| **4.3 Escalation decision & warm handoff** | 14 | Scope check; progress check; route selection; availability reality-check; whisper brief; consent carry-over | Dual-loop architecture: Escalation Sentinel (parallel, every turn) + Warm Transfer Orchestrator; deterministic triggers + ML consequence-weighted scoring; typed EscalationDecision struct | 8 | Complex escalation requiring judgment on consequence-weighted routing; supervisor discretion on de-escalate-vs-transfer | De-escalate-vs-transfer instinct for edge cases where a "frustrated" caller is one sentence from delighted |
| **4.4 Supervisor whisper / barge-in** | 14 | Risk-prioritized attention allocation; coach-vs-barge decision; whisper delivery timing; multi-session context-switching | Agent as LiveKit room participant; supervisor read-only subscription; automated risk triage (affect + sentinel flags); whisper TTS injection to agent ear | 5 | Action about to commit is irreversible, incorrect, or compliance-violating; human supervisor judgment needed on novel situation | Attention under genuine ambiguity before metrics cross threshold; graceful face-saving barge-in |
| **4.5 Vulnerable customer & duty of care** | 14 | FCA four-driver scanning; acute-risk listening; care-mode switch; comprehension-confirmation loop; sales suppression; Tele-MANAS routing | Parallel duty-of-care sentinel: four-driver vulnerability classifier + SEPARATE high-recall self-harm/crisis classifier + coercion/capacity sensor | 4 | ANY self-harm/suicidal/domestic-abuse signal; capability/coercion flag above threshold; all acute-risk | Detecting quiet/invisible/fluctuating vulnerability; distinguishing "confused" from "non-native speaker of the interface language" |
| **5.1 Call wrap-up & disposition coding** | 14 | Gist reconstruction; ONE primary intent identification; taxonomy ambiguity resolution; CRM field update; compliance tagging | Single grounded multi-task LLM call over diarized transcript → Pydantic disposition schema → deterministic tool execution; tribal convention learned via DSPy-optimize on 6-12mo labeled pairs | 8 | Disposition confidence below threshold; compliance flag fires; multi-label conflict on financial-consequence code | Tribal/unwritten coding conventions; taxonomy edge-cases the codes don't cover |
| **5.2 After-call work & follow-up** | 12 | Structured commitment extraction; DLT-template-correct outbound firing; DPDP/DND pre-action reconciliation; grievance trail with SLA | Event-triggered durable ACW workflow (Temporal/LangGraph) on call.ended; extraction service → validation → deterministic outbound actions; scheduling in RBI 08:00-19:00 window | 8 | Disposition confidence < 0.85; multi-label conflict on financial-consequence code; outbound fails consent check | Cross-call relationship memory ("3rd broken PTP → escalate to legal"); reading unspoken/implied commitments |
| **6.1 QA / eval flywheel** | 14 | Rubric-load per call type; empathy/tone scoring from vocal quality; code-switch quality eval; borderline judgment; calibration sessions; drift monitoring | Gnani Prisma v2.5 ASR + diarization; per-dimension scoring (LLM + acoustic SER head); automated calibration against human gold labels; drift detector on weekly distributions | 7 | Auto-fail on compliance dimension; AI-human inter-rater kappa < 0.60; novel call type with no training data | Tone and prosody empathy scoring (~40% of empathy signal is acoustic); Hindi sarcasm in QA |
| **6.2 Observability & cost-per-resolution** | 14 | Per-call cost attribution; FCR judgment; 100% scoring vs 2-5% sampling; margin tracking; recording retention per regulator; audit-request retrieval | OTel GenAI spans with 4-layer token split; per-turn cost attribution; automated FCR scoring; real-time anomaly detection; automated audit-trail retrieval | 7 | Spend anomaly 5x above baseline with unidentified root cause; new cost-driver not yet in attribution model | Contract-layer margin governance; commercial SLA penalty clause awareness |
| **Voice pipeline & latency** | 13 | VAD; barge-in yield; echo suppression; full-duplex cognition; filler during data fetch | Silero VAD v5 → Sarvam Saaras v3 streaming → Claude Haiku 4.5 LLM → sentence boundary → Bulbul-V3 TTS → SIP; parallel barge-in monitor | 6 | Barge-in loop failure 3+ consecutive turns; ASR confidence < floor on critical entity | Back-channel discrimination ("haan haan" problem); latency budget under realistic India-PSTN conditions |
| **Indic ASR engineering** | 14 | L1 identification; regional accent mapping; code-switch ratio estimation; named-entity laser focus; disfluency filtering | WebRTC AEC3 → RNNoise → Silero VAD → Sarvam Saarika v2 / Gnani Prisma v2.5 → domain-vocab bias; per-entity confidence; targeted re-prompt | 6 | ASR entity confidence < 0.60 on named entity AND cannot get valid confirmed value | Deep dialect generalization (Bhojpuri/Awadhi/Marwari/Rajasthani phoneme inventories) |
| **Indic TTS & prosody** | 14 | Response register selection; Hindi gender agreement; stress anchors; sentence-level melody; rate calibration per caller; graceful barge-in receipt | Text normalization (indicnlp + Haiku LLM) → Bulbul-V3 / Saarika-Aura / ElevenLabs multilingual; SSML prosody tags; sentence-boundary chunking; interrupt-cancel | 7 | Compliance script mispronounced or truncated; TTS synthesis error mid-disclosure | Spontaneous prosodic creativity for non-standard emotional situations; Hindi gender agreement errors |
| **Agent orchestration & HITL** | 14 | Intent-to-skill mapping; queue state awareness; warm handoff execution; continuous self-monitoring for HITL triggers | LangGraph StateGraph (ContactCenterState); Supervisor Planner (Sonnet 4.6, temp=0) + N Skill-Worker leaves (Haiku 4.5); typed state schema; 8 nodes | 6 | Customer explicitly requests supervisor; value above authority; legal signal; emotional state crossing threshold | Tri-lingual mid-sentence NLU for Tamil+Hindi+English; graceful state-resume after interrupt |
| **Memory architecture** | 14 | Screen-pop recognition; emotional priming from history signals; ticket clustering; contradiction detection; promise registry; organizational memory lookup | 4-layer memory: in-context (200K) + Redis session (4h TTL) + Mem0 customer long-term + org RAG knowledge base; pre-call context assembly via asyncio.gather | 7 | Identity verification mismatch; CRM vs stated fact conflict; privacy-restricted history access | Implicit emotional memory; cross-call emotional continuity; editorial judgment on what to log vs omit |
| **RAG grounding & hallucination guardrails** | 14 | Intent disambiguation; entity extraction; multi-source cross-check; staleness awareness; relevance gating; conflict detection; citation delivery | Hybrid retrieval (Elasticsearch BM25 + BGE-M3/Qdrant, RRF); BGE Reranker v2-m3; composite confidence score; NLI faithfulness verifier; abstention path | 6 | Composite retrieval confidence < 0.50; faithfulness score < 0.75; two authoritative sources conflict | KB coverage awareness (can't distinguish "not found" from "doesn't exist"); Hindi-language KB coverage |
| **Action safety** | 10 | Pre-action intent re-verification; duplicate/prior-execution check; dry-run preview; rollback awareness; regulatory disclosure trigger; audit entry | IdempotencyMiddleware (SHA-256 composite key, Redis hot + PostgreSQL warm + S3 cold); Authorization Gate; dry-run confirmation step; immutable audit ledger | 7 | Refund > ₹2,000; KYC change to high-risk field; bulk action; system returning unrecognized state | Semantic ambiguity under emotional stress ("cancel everything" said in frustration = not literal cancellation) |
| **Compliance-as-code engine** | 14 | Pre-call: 6 regulatory pre-flight checks; mid-call: consent withdrawal detection; banned-phrase monitoring; mandatory disclosure tracking; post-call: interaction audit record; cross-channel opt-out propagation | OPA Rego policies per regulator; pre-call evaluation FastAPI gate; streaming banned-phrase detector; consent ledger; post-call audit assembler | 8 | New regulatory circular; vulnerability/distress detected; agent offers unauthorized discount | Novel regulatory interpretation requiring human compliance officer; stale Rego policy gap |
| **Security, DPDP & PII redaction** | 14 | PII flag and mask on repeat-back; minimum-necessary PII solicitation; interrupt caller volunteering excess PII; social-engineering detection; DPO escalation within 4h | PII Interception Middleware (regex → Presidio+custom-Indian-recognizers → GLiNER-pii-base-v1.0); in-country VPC; compliance config per client; breach detection | 5 | Breach confirmed; suspected identity fraud; Hinglish PII disclosure missed | Hinglish/transliterated PII detection (GLiNER Hindi zero-shot F1 ~47.8%); automatic DPO escalation pipeline |
| **Telephony/CPaaS & omnichannel** | 14 | Channel detection on call arrival; DTMF/IVR navigation; audio quality diagnosis; attended transfer whisper brief; WhatsApp HSM template selection; 24h session window awareness | Exotel/Plivo SIP → LiveKit Agents voice pipeline → LangGraph multi-channel orchestrator; shared CustomerState in Redis; WhatsApp BSP integration | 6 | MOS < 2.5 > 30s AND customer reports audio issues; SIP REFER failure; WhatsApp 24h window expired with unresolved issue | Dynamic IVR navigation at unfamiliar third-party systems; multi-channel time-slicing without dropped threads |
| **Concurrent multi-session isolation** | 12 | Screen/record discipline; wrap-before-next; name/context reset reflex; identity-confidence judgment on cross-channel stitch; selective carry-forward; verbal slip-catch | Immutable session_id + tenant_id keyed context objects; four-plane leak defense (memory/tool/logging/TTS); cross-session PII diffuser; probabilistic identity-resolution layer | 6 | Any detected cross-session PII leak; identity resolution failure on cross-channel stitch; conflicting consent states | Agent failure ceiling is a silent, fluent, machine-speed PII leak — structurally higher severity than human verbal slip |
| **Where humans still beat agents** | 12 | Real-time prosodic empathy read before words; improvised exception judgment; trust-and-fraud sixth sense; multi-party/background-context handling; graceful failure + face-saving handoff | Per-turn Adaptation Router {ASR confidence, emotion+arousal, intent confidence, action-tier, regulatory-class} → {AGENT_HANDLE, AGENT+COPILOT, WARM_TRANSFER}; native S2S for prosodic moat | 6 | Half of the triggers here ARE the HITL; the router's output IS the escalation decision | ~50% closeable via data+engineering; ~50% deliberate regulatory/risk gating that SHOULD remain human-augmented |

---

## 4. Automation Readiness Tiers

### Tier Definitions

**Fully Automatable Now (8-10/10):** The agent matches or exceeds human performance on ALL critical micro-steps. HITL triggers are narrow, well-defined, and rare (<5% of calls). The deterministic spine (compliance-as-code, action-gateway, CRM write) is the backbone.

**Automatable with Guardrails/HITL (5-7/10):** The agent handles the core workflow but requires structured human handoff on defined failure modes. HITL triggers fire 10-30% of calls. The hybrid is safe to deploy but not yet "lights-out."

**Human-Led for Now (1-4/10):** Fundamental perception or judgment gaps mean the AI is a copilot tool, not the primary agent. Deploying as primary agent here creates unacceptable risk (regulatory, reputational, or safety).

---

### Fully Automatable Now (8-10/10)

| Step | Score | Why it's there |
|------|-------|----------------|
| Pre-call compliance check (DND/DLT/time-window) | 9 | Pure deterministic rule engine; OPA Rego has zero ambiguity; machine is faster and more reliable than human memory |
| CTI screen-pop & context load | 8 | Parallelized LangGraph pre-turn graph is structurally faster than human eye-scan; CRM API calls are already machine calls |
| Recording disclosure & DPDP consent delivery | 8 | Deterministic FSM with verbatim delivery; the ONLY residual gap is barge-in graceful recovery (solvable with a 200ms re-insert mechanism) |
| Eligibility checks & decisioning | 8 | The verdict is a DMN/OPA engine; the LLM only handles language framing; machines make fewer rule-version and data-entry errors than humans |
| Escalation decision & warm handoff | 8 | Common escalation triggers are all machine-checkable predicates; the system composes the whisper brief from Session State; only consequence-weighting on novel scenarios remains human |
| Call wrap-up & disposition coding | 8 | Grounded multi-task LLM over diarized transcript; Pydantic schema enforcement; tribal conventions are a data problem solvable with 6-12 months of labeled pairs |
| After-call work & follow-up | 8 | Temporal/LangGraph durable workflow; all steps are structured API calls; DPDP/DND pre-action reconciliation is deterministic |
| Compliance-as-code engine | 8 | OPA Rego per regulator; real-time banned-phrase detector; consent ledger; the only gap is novel circular interpretation requiring a human compliance officer |
| Hold/silence & dead-air etiquette | 8 | Deterministic wait-aware FSM; tool-call lifecycle events are machine-observable; the residual gap (adaptive cadence from subtle vocal cues) is a CSAT refinement, not a safety issue |

**The boundary:** these steps share a common property — the core decision logic is already digital (CRM APIs, rule engines, consent logs, timeout counters). The agent is replacing a human who was themselves reading machine outputs. The switch is clean.

---

### Automatable with Guardrails/HITL (5-7/10)

| Step | Score | Why it is not 8+ yet |
|------|-------|----------------------|
| Greeting, identity verification & auth | 7 | LoA judgment under adversarial signals; holistic fraud intuition not yet in-distribution on Indian call audio |
| Active listening & messy speech | 7 | Near-parity on clean audio; residual gap on noisy code-switch with overconfident ASR |
| Language, dialect & code-mixing | 7 | Standard Hindi+English+Hinglish is solved; deep dialect (Bhojpuri, Awadhi, Marwari) WER is 20-30% above target |
| Intent recognition & disambiguation | 7 | Conformal prediction covers most; OOS intents and garbled codemix break coverage guarantees |
| Knowledge lookup & grounding | 7 | Retrieval+groundedness gate is strong; the gap is KB coverage awareness and conflict adjudication |
| Multi-turn context & working memory | 7 | Session state is solid; implicit never-stated context and correction propagation are the remaining gaps |
| Compliance & mandatory disclosures | 7 | FSM enforces delivery; vulnerability/non-comprehension sensing is the gap |
| Indic TTS & prosody | 7 | Bulbul-V3/Saarika-Aura covers the standard case; spontaneous prosodic creativity for non-standard emotional situations lags |
| QA / eval flywheel | 7 | 100% scoring of structured dimensions is solved; prosodic empathy scoring (~40% of signal) still requires acoustic-LLM fusion |
| Observability & cost-per-resolution | 7 | OTel harness + automated attribution is mature; commercial contract-layer awareness is human |
| Empathy, rapport & de-escalation | 6 | Perception (~95% anger detection) is largely solved; policy under adversarial/novel/abusive turns is where humans still win |
| Real-time voice pipeline & latency | 6 | Sub-700ms P50 is achievable on LiveKit+Haiku; P95 under India-PSTN jitter + backchannel discrimination lag |
| Indic ASR engineering | 6 | Hindi+English+Hinglish on clean audio is near-parity; deep dialect generalization is a data gap |
| Agent orchestration, routing & HITL | 6 | LangGraph StateGraph covers the defined cases; tri-lingual NLU (Tamil+Hindi+English) and graceful interrupt resume are open |
| RAG grounding & hallucination guardrails | 6 | Hybrid retrieval + groundedness gate is solid; KB coverage awareness and Hindi KB coverage are the gaps |
| Action safety | 7 | IdempotencyMiddleware + Action Gateway are deterministic; semantic ambiguity under emotional stress is the residual risk |
| Memory architecture | 7 | 4-layer memory stack covers session + customer + org; implicit emotional memory and editorial judgment are soft gaps |
| Telephony/CPaaS & omnichannel | 6 | SIP/LiveKit/WhatsApp BSP pipeline is buildable; dynamic IVR navigation at novel third-party systems is an open problem |
| Concurrent multi-session isolation | 6 | Defense-in-depth via session_id keying is architecturally sound; the failure ceiling (silent machine-speed PII leak) is higher severity than human slip |
| Where humans still beat agents | 6 | The Adaptation Router is deployable; ~50% of the moat is closeable in 12-24mo; ~50% should remain augmentation |

**The boundary:** these steps have a proven agent path for the majority case. The HITL triggers are well-defined. These are safe to deploy in production TODAY with a staffed escalation pool. The risk is in the tail — novel inputs, distribution shift, and the ~10-30% of calls that hit edge cases.

---

### Human-Led for Now (1-4/10)

| Step | Score | Root Cause |
|------|-------|-----------|
| Vulnerable customer & duty of care | 4 | Quiet/invisible vulnerability (capability, resilience) is not reliably detectable from call audio alone; missing FCA-taxonomy-labeled Indian call data; regulatory duty-of-care liability if wrong |
| Emotion & sentiment reading | 5* | *Technically 5 but the hardest to close for Indian telephony specifically; Hinglish sarcasm, masked distress, and cause attribution remain outside reliable automated detection on 8kHz telephony audio |
| Fraud / abuse / social-engineering | 5* | *Technically 5 but novel pretexts, slow-burn grooming, and live-coached deepfake calls are outside in-distribution detection; failure here is catastrophic (financial crime, regulatory action) |
| Objection handling & negotiation | 5 | Dynamic mid-objection stance-switching; genuine hardship detection; the real-money decision (PTP amount the customer will actually honor) requires theory-of-mind not yet reliable |
| Cross-sell / up-sell judgment | 5 | RESTRAINT calibration under ambiguity; suitability for regulated products requires licensed financial advisor judgment in many IRDAI cases |
| Supervisor whisper / barge-in | 5 | The supervisor role IS the HITL rail; deploying AI as the primary supervisor is a category error at this readiness level |
| Backend action execution | 5 | Cross-system implicit reconciliation under never-seen failure combos; the stakes (refund, KYC, plan change) mean false execution is a regulatory and financial incident |

**The boundary:** these steps share one or more of: (A) catastrophic failure mode (fraud, financial crime, regulatory penalty), (B) missing training data for Indian call context, (C) legal/regulatory liability that explicitly requires a licensed/qualified human, or (D) the failure ceiling of an AI error is structurally higher severity than a human error on the same step.

*Note: Emotion reading and fraud are scored 5/10 in the readiness table but are treated as human-led because the tail risk is asymmetric. A 5/10 fraud detector on a fraud call is not "90% of the job automated" — it is "10% of attacks get through, each potentially a ₹10L+ incident."*

---

## 5. The Enabling Capability Stack

The 36 steps reduce to a platform spine of 11 capability layers. Every step draws from multiple layers; the spine must be built as infrastructure before individual steps can be enabled.

```
┌─────────────────────────────────────────────────────────────┐
│                    PLATFORM SPINE                           │
├──────────────────────┬──────────────────────────────────────┤
│  L1  TELEPHONY BRIDGE│ SIP inbound/outbound (Exotel/Plivo)  │
│                      │ LiveKit WebRTC (AEC + NS)             │
│                      │ G.711 µ-law/A-law ingestion           │
│                      │ WhatsApp BSP (Meta/Gupshup/Kaleyra)   │
│                      │ CTI screen-pop API (Genesys/Avaya)    │
├──────────────────────┼──────────────────────────────────────┤
│  L2  VOICE PERCEPTION│ WebRTC AEC3 echo cancellation         │
│                      │ DeepFilterNet3 denoise front-end       │
│                      │ Silero VAD v5 (20ms frames, 6ms/frame)│
│                      │ Sarvam Saaras v3 streaming ASR         │
│                      │ Gnani Prisma v2.5 (Indic diarization) │
│                      │ emotion2vec_plus / WavLM SER head      │
│                      │ Language-profile tracker state object  │
├──────────────────────┼──────────────────────────────────────┤
│  L3  SYNTHESIS       │ Text normalizer (indicnlp + Haiku LLM)│
│                      │ Bulbul-V3 / Saarika-Aura TTS           │
│                      │ SSML prosody tags per emotion/regime   │
│                      │ Sentence-boundary chunking (first 15 t)│
│                      │ Interrupt-cancel / barge-in receive    │
├──────────────────────┼──────────────────────────────────────┤
│  L4  ORCHESTRATION   │ LangGraph StateGraph (ContactCenter-  │
│                      │   State, 8 nodes, typed Pydantic)     │
│                      │ Claude Sonnet 4.6 (Supervisor Planner) │
│                      │ Claude Haiku 4.5 (Skill Workers)       │
│                      │ Pipecat Flows (VAD + TTS pipeline)     │
│                      │ Escalation Sentinel (parallel, /turn)  │
│                      │ Adaptation Router (HANDLE/COPILOT/     │
│                      │   TRANSFER per-turn policy)            │
├──────────────────────┼──────────────────────────────────────┤
│  L5  MEMORY          │ In-context: Claude 200K window         │
│                      │ Session: Redis (session:{call_id}, 4h) │
│                      │ Customer LT: Mem0 (customer:{id})      │
│                      │ Org knowledge: Qdrant (policy/product) │
│                      │ Context Assembler (asyncio.gather)     │
│                      │ Promise registry + open-loop tracker   │
├──────────────────────┼──────────────────────────────────────┤
│  L6  KNOWLEDGE / RAG │ Curated metadata-rich KB               │
│                      │   (doc_type/product/segment/effective_ │
│                      │   from/effective_to/source_authority)  │
│                      │ Elasticsearch BM25 + BGE-M3 dense      │
│                      │ RRF fusion → BGE Reranker v2-m3        │
│                      │ NLI faithfulness verifier (groundedness│
│                      │ Abstention classifier (KB coverage)    │
│                      │ Pydantic citation schema (chunk_id,    │
│                      │   source, confidence, text_span)       │
├──────────────────────┼──────────────────────────────────────┤
│  L7  DECISION ENGINES│ DMN/OPA-Rego/Cedar policy engine       │
│                      │   (eligibility, auth level, waiver,    │
│                      │   exception/override, product rules)   │
│                      │ Open Policy Agent per regulator        │
│                      │   (rbi_fpc, trai_tcccpr, irdai_norms,  │
│                      │   dpdp_consent)                        │
│                      │ Objection playbook (deterministic levers│
│                      │ Moment-gate (cross-sell suppression)   │
├──────────────────────┼──────────────────────────────────────┤
│  L8  ACTION GATEWAY  │ MCP tool server per integration        │
│                      │   (issue_refund, create_ticket,        │
│                      │   update_kyc, change_plan, schedule_cb)│
│                      │ IdempotencyMiddleware (SHA-256 key,    │
│                      │   Redis hot + PostgreSQL warm + S3)    │
│                      │ Authorization Gate (tier + policy check)│
│                      │ Saga compensation registry             │
│                      │ Immutable audit ledger (append-only PG)│
├──────────────────────┼──────────────────────────────────────┤
│  L9  COMPLIANCE RAIL │ Compliance FSM (per-call, mandatory   │
│                      │   node enforcement, not LLM-optional) │
│                      │ Pre-call OPA gate (DND/DLT/time-window)│
│                      │ Consent ledger (timestamp, language,   │
│                      │   version, purpose, withdrawal)        │
│                      │ Banned-phrase streaming detector        │
│                      │ Vulnerability/duty-of-care sentinel    │
│                      │ Post-call audit assembler              │
├──────────────────────┼──────────────────────────────────────┤
│  L10 SECURITY / PII  │ PII Interception Middleware            │
│                      │   (regex → Presidio+Indian-recognizers │
│                      │   → GLiNER-pii-base-v1.0)              │
│                      │ In-country VPC (AWS ap-south-1 /       │
│                      │   Azure India / GCP Mumbai)            │
│                      │ Session context isolation (session_id  │
│                      │   keying, BAN module-level global state)│
│                      │ Fraud sentinel (SE classifier + velocity│
│                      │   engine + anti-deepfake + coercion)   │
│                      │ Breach detection + DPO escalation pipe │
├──────────────────────┼──────────────────────────────────────┤
│  L11 OBSERVABILITY   │ OTel GenAI spans (4-layer token split: │
│                      │   prompt/tool/memory/response)         │
│                      │ Per-turn: session_id, tenant_id, turn, │
│                      │   intent_class, model_tier, rag_chunks │
│                      │ Cost attribution: $/turn, $/session    │
│                      │ Automated QA (Gnani diarization +      │
│                      │   per-dimension LLM scorer)            │
│                      │ Drift detector (weekly distribution)   │
│                      │ Recording retention (RBI 5yr / IRDAI   │
│                      │   3yr / CERT-In 180d, S3 Glacier)      │
└──────────────────────┴──────────────────────────────────────┘
```

### Layer Interdependencies (Build Order)

The layers are not independent. The correct build sequence respects their dependencies:

```
L1 (Telephony) → L2 (Perception) → L3 (Synthesis) must be
  a functional unit before any dialog layer is meaningful.

L7 (Decision Engines) + L8 (Action Gateway) + L9 (Compliance Rail)
  form the "safe execution core" — must be production-hardened
  before ANY action-taking step is deployed.

L10 (Security/PII) must be enforced BEFORE L2 output reaches L4/L5 —
  PII flows through the ASR transcript and into the LLM context;
  the middleware must intercept between them.

L11 (Observability) must instrument ALL other layers from day 1 —
  retrofitting observability is technically possible but misses the
  early data needed for the QA flywheel and model fine-tuning.
```

---

## 6. The "Full Adaptation" Roadmap

The roadmap is organized by the gap class each move closes, not by time alone. Each entry names the specific data or engineering move, the steps it unblocks, and the eval gate that confirms closure.

---

### Gap Class A — Indic ASR / Dialect Coverage

**Current state:** Sarvam Saaras v3 + Gnani Prisma v2.5 cover standard Hindi+English+Hinglish at near-parity with humans on clean-to-moderate telephony. WER spikes 20-35% on Bhojpuri, Awadhi, Marwari, Rajasthani sub-district accents.

**Move A1 (0-6 months):** Collect 500-1000 hours of labeled telephony audio per dialect from BSNL/Jio rural call archives (consent-cleared) or synthetic augmentation via dialect TTS. Fine-tune Sarvam Saaras v3 with dialect adapters (LoRA on the acoustic encoder). Target WER < 15% on Bhojpuri/Awadhi/Marwari.

**Eval gate:** WER on a held-out 100-hour dialect test set; entity-level F1 on account numbers, amounts, and policy IDs spoken in each dialect.

**Steps unblocked:** Active listening (2.1), Language/dialect handling (2.2), Intent recognition (2.3) — all three are blocked on this for rural India deployments.

**Move A2 (6-12 months):** Deploy per-dialect acoustic model A/B routing based on caller ANI region prefix and language-profile tracker output. Monitor WER drift per dialect in production.

---

### Gap Class B — Prosodic Empathy & Emotional Perception

**Current state:** Streaming SER (emotion2vec_plus / WavLM head) at 300ms windows handles arousal and valence on clean audio. Hinglish sarcasm detection F1 is ~55-60%. Masked distress (over-controlled calm) detection is near-random. Cause attribution (trait-vs-state) over-triggers on brusque-by-nature speakers.

**Move B1 (0-6 months):** Deploy dual-path (acoustic SER + IndicBERT text track, late-fusion MLP). Collect 3-month production audio with human-labeled AffectState ground truth (outsource to specialized call-center QA teams familiar with Indian caller behavior). Target: arousal/valence MAE < 0.15, discrete emotion macro-F1 > 0.72.

**Move B2 (6-12 months):** Fine-tune on labeled Hinglish sarcasm/irony corpus (500+ examples minimum) drawn from production calls. Add trajectory feature (slope of arousal across last 5 turns) as explicit model input. Deploy multimodal empathy model (native speech-to-speech path: GPT-Realtime or Gemini Live) for the de-escalation step specifically — bypass STT→LLM→TTS cascade entirely for the highest-stakes empathy moments.

**Move B3 (12-24 months):** DPO/RLHF on de-escalation outcomes (calls where agent successfully calmed vs escalated to human) to train the policy model on real outcome rewards. Close the adaptive re-generation under adversarial/abusive turns gap.

**Eval gate:** A held-out 200-call set with human-labeled emotional trajectories; CSAT delta on AI-handled vs human-handled de-escalation calls.

**Steps unblocked:** Emotion & sentiment reading (2.4), Empathy/de-escalation (3.1), Objection handling (3.6) — all partially blocked here.

---

### Gap Class C — Fraud & Adversarial Intuition

**Current state:** In-distribution attacks (OTP phishing, SIM-swap pressure, standard pretexts) are detectable at ~85%+ with the parallel sentinel track. Novel pretexts, slow-burn multi-call grooming, and live-coached deepfake calls are near-random-chance.

**Move C1 (0-6 months):** Deploy the parallel sentinel track (SE classifier + abuse/threat classifier + speaker diarization/coercion detector + cross-session velocity engine) as a read-only copilot tool for human fraud desk agents. This generates labeled data: every human fraud-desk decision becomes a training signal.

**Move C2 (6-12 months):** Anti-spoofing/deepfake voice detector (ASVspoof 2024-class model) on every call. Cross-channel velocity engine (same-customer calls within 2-hour window + prior ATO attempt flags). Publish calibrated fraud_risk_score as a structured field on every CallContext.

**Move C3 (12-24 months):** Train a multimodal manipulation-risk model on 12+ months of labeled production calls (human-confirmed fraud cases). The model sees audio features (prosody, hesitation, coaching-pause pattern) + transcript features (pretext structure, urgency anchors) + velocity features (cross-session, cross-channel). Target AUC > 0.90 on confirmed fraud cases.

**Eval gate:** Precision/recall on a held-out fraud case set curated with the NCRP/1930 case resolution outcomes; false-positive rate on legitimate distressed callers.

**Steps unblocked:** Fraud/abuse handling (4.2), Identity verification (1.3) — both partially blocked.

---

### Gap Class D — Vulnerable Customer Detection

**Current state:** Acute signals (self-harm, domestic abuse, medical emergency) can be detected with high-recall classifiers and modest precision. Quiet/invisible vulnerability (cognitive decline, financial capability, fluctuating mental health) on a calm call produces no strong acoustic signal. FCA four-driver multi-label model does not exist for Indian call context.

**Move D1 (0-6 months):** Deploy a high-recall (>0.95) binary self-harm/crisis classifier as the ONLY autonomous gate — everything above the threshold triggers immediate human transfer to Tele-MANAS 14416 or vulnerable-customer desk. No false-negative is acceptable here; false-positives cost one unnecessary warm transfer.

**Move D2 (6-12 months):** Build FCA four-driver multi-label model (Health/Life-event/Resilience/Capability) fine-tuned on Indian-context labeled calls. The label taxonomy must be adapted for Indian BPO context (e.g., "Resilience" = job loss / EMI over-leverage / crop failure; "Capability" = low financial literacy, first-generation bank user). Requires 1000+ labeled examples per driver.

**Move D3 (12-24 months):** Longitudinal vulnerability tracking across calls (Mem0 customer long-term memory). A customer flagged as "low-capability" on call 1 has that flag carried forward, so call 2 agent starts in care-mode even if the call opens with no signal.

**Eval gate:** Recall on a held-out vulnerable-customer set reviewed by trained duty-of-care assessors; false-positive rate on standard callers.

**Steps unblocked:** Vulnerable customer handling (4.5), Compliance/disclosures (3.5).

---

### Gap Class E — Tribal Knowledge & KB Coverage

**Current state:** RAG pipeline covers documented knowledge accurately. Tribal/unwritten coding conventions (which CRM code maps to an undocumented edge case) live in supervisor heads. KB coverage awareness ("I searched but found nothing" vs "this doesn't exist") is unreliable.

**Move E1 (0-3 months):** Mine 6-12 months of (transcript → human disposition code) pairs per client. DSPy-optimize or LoRA fine-tune the disposition classifier on this data. The unwritten conventions are implicitly encoded in the data; this is the fastest route to closing the tribal knowledge gap.

**Move E2 (3-6 months):** Train a binary KB-coverage classifier on (query, retrieval-results, human-abstention-labels). The classifier learns to distinguish "this query has no good answer in the KB" from "this query matched but at low confidence." Separate signal, separate model.

**Move E3 (6-12 months):** Implement conflict-adjudication policy: when two authoritative sources disagree, the system raises a structured conflict record (conflict_id, source_a, source_b, claim_text, effective_dates) and escalates to a human knowledge-base steward — not to the front-line agent. The steward's resolution is added to the KB as a new authoritative entry.

**Eval gate:** Faithfulness on FaithBench-India (custom); disposition accuracy vs human gold-label; abstention recall on queries with no KB answer.

**Steps unblocked:** Knowledge lookup/grounding (3.2), Call wrap-up/disposition (5.1).

---

### Gap Class F — Compliance Regulatory Coverage

**Current state:** Existing Rego policies cover RBI FPC, TRAI TCCCPR, IRDAI norms, DPDP consent as of their last update dates. New circulars require manual Rego update and deploy; during the gap, the engine runs on stale rules.

**Move F1 (ongoing):** Regulatory circular monitoring pipeline: scrape RBI/SEBI/IRDAI/TRAI/MeitY notification pages daily, run a structured extraction LLM to identify rule changes, generate a draft Rego policy diff, route to human compliance officer for review and approval, deploy on merge. Target: new circular → approved Rego update within 5 business days.

**Move F2 (6-12 months):** Compliance hot-patch mechanism: when a new circular is identified but Rego is not yet updated, insert a conservative override (restrict the action requiring the new rule) until the update is reviewed. "When in doubt, be more restrictive" is always the safe default.

**Eval gate:** Time-to-Rego-update on simulated circular injection; compliance violation rate on monthly QA audit.

**Steps unblocked:** Compliance-as-code engine (L9), Pre-call gate (0.1), Mid-call disclosures (3.5).

---

### Gap Class G — Action Reconciliation & Saga Handling

**Current state:** Declared saga compensations (issue_refund failed → compensate_ticket is known) work. Never-seen two-system failure combinations are handled by the human agent's implicit cross-system knowledge.

**Move G1 (0-6 months):** Inventory every action pair that can partially succeed across the system topology. For each pair, declare the compensation action explicitly in the saga registry. Start with the 10 most common action types (refund, ticket, KYC update, plan change, callback schedule, mandate, email/SMS dispatch, payment link, address update, nomination change).

**Move G2 (6-12 months):** Production monitoring: instrument every multi-step action with a saga_id and track partial-completion events in the audit ledger. Any partial completion without a matching compensation fires an alert to a human ops agent within 60 seconds.

**Eval gate:** Zero unresolved partial-completion events over a 30-day production window; saga-compensation latency < 60 seconds from failure detection.

**Steps unblocked:** Backend action execution (3.8), After-call work (5.2).

---

### Synthesis: Readiness Trajectory

| Horizon | Expected Readiness Floor | What Changes |
|---------|--------------------------|-------------|
| Today | 5/36 steps fully automatable | Spine is being built |
| 6 months | 14/36 steps fully automatable | L1-L9 spine live; dialect ASR move A1; fraud sentinel C1 deployed as copilot |
| 12 months | 22/36 steps fully automatable | B1+B2 (emotion/prosody); C2 (velocity/deepfake); D1 (acute vulnerability); E1 (tribal knowledge mined) |
| 24 months | 30/36 steps fully automatable | B3 (DPO empathy); C3 (fraud multimodal); D2 (four-driver vulnerability); A2 (dialect routing) |
| Structural ceiling | ~32/36 steps | Deliberate regulatory/liability gating keeps vulnerable-customer acute handling, high-value financial advice, and novel fraud as human-augmented. These are design choices, not engineering failures. |

---

## 7. Derived Optimal Architecture

The architecture below is derived from the step decomposition — it is not assumed. Every component exists because one or more steps required it.

---

### Top-Level Design

```
                           ┌─────────────────────────────┐
                           │      TELEPHONY PLANE         │
                           │  Exotel/Plivo SIP ←→ LiveKit │
                           │  WebRTC AEC + Noise Suppress  │
                           │  G.711 µlaw audio streams     │
                           └──────────┬──────────────────┘
                                      │ dual-channel audio
                          ┌───────────▼───────────────────┐
                          │       PERCEPTION LAYER        │
                          │                               │
                          │  DeepFilterNet3 denoise       │
                          │  Silero VAD v5 (20ms)         │
                          │  Sarvam Saaras v3 streaming   │
                          │  Gnani Prisma v2.5 diarize    │
                          │  WavLM SER head @300ms        │
                          │  Language-profile tracker     │
                          └──┬───────────────────────┬───┘
                             │ typed transcript        │ AffectState
                             │ + per-token confidence  │
                ┌────────────▼────────────┐  ┌────────▼──────────────┐
                │  PII INTERCEPT LAYER    │  │  FRAUD SENTINEL       │
                │  regex + Presidio +     │  │  (parallel, off-path) │
                │  GLiNER-pii-base-v1.0  │  │  SE classifier        │
                │  → typed PII tokens    │  │  velocity engine      │
                └────────────┬───────────┘  │  anti-deepfake        │
                             │ sanitized     │  coercion detector    │
                             │ transcript    └────────┬──────────────┘
                ┌────────────▼──────────────────────▼──────────────────┐
                │              PRE-TURN CONTEXT ASSEMBLER              │
                │  asyncio.gather:                                      │
                │    crm_lookup() + mem0.recall() + ticket_cluster()    │
                │    + intent_predict() + risk_score() + auth_policy()  │
                │  Emits: typed CallContext (Pydantic v2)               │
                └────────────────────────┬─────────────────────────────┘
                                         │ CallContext
                ┌───────────────────────▼──────────────────────────────┐
                │              COMPLIANCE GATE (pre-dialog)            │
                │  OPA Rego: DND/DLT/time-window/frequency/consent     │
                │  Compliance FSM: mandatory node queue for this regime │
                │  Emits: ClearToConnect + ObligationManifest          │
                └────────────────────────┬─────────────────────────────┘
                                         │
                ┌───────────────────────▼──────────────────────────────┐
                │                 LANGRAPH STATEGRAPH                  │
                │           ContactCenterState (typed Pydantic)        │
                │                                                       │
                │  ┌─────────────────────────────────────────────────┐ │
                │  │  SUPERVISOR PLANNER NODE                         │ │
                │  │  Claude Sonnet 4.6, temp=0                       │ │
                │  │  Reads: CallContext + AffectState + fraud_risk   │ │
                │  │  Emits: intent + route + next_skill + state_delta│ │
                │  └────────────────────────────────────────────────-┘ │
                │          │ route decision                             │
                │   ┌──────┴───────────────────────────────────┐      │
                │   │           SKILL WORKER NODES             │      │
                │   │  (Claude Haiku 4.5, parallel, isolated)  │      │
                │   │                                           │      │
                │   │  AUTH_WORKER     → auth FSM + OTP        │      │
                │   │  KNOWLEDGE_WORKER → RAG + grounding gate │      │
                │   │  ELIGIBILITY_WORKER → OPA/DMN engine     │      │
                │   │  COMPLIANCE_WORKER → disclosure FSM      │      │
                │   │  EMPATHY_WORKER   → de-escalation policy │      │
                │   │  ACTION_WORKER    → Action Gateway        │      │
                │   │  WRAPUP_WORKER    → disposition + ACW    │      │
                │   └──────────────────────────────────────────┘      │
                │                                                       │
                │  ┌─────────────────────────────────────────────────┐ │
                │  │  ESCALATION SENTINEL (parallel, every turn)     │ │
                │  │  Checks: scope + loops + affect + risk + explicit│ │
                │  │  Emits: EscalationDecision + whisper_brief       │ │
                │  └─────────────────────────────────────────────────┘ │
                │                                                       │
                │  ┌─────────────────────────────────────────────────┐ │
                │  │  VULNERABILITY SENTINEL (parallel, off-path)    │ │
                │  │  FCA four-driver classifier + crisis classifier  │ │
                │  │  Emits: VulnerabilityFlag → care-mode trigger    │ │
                │  └─────────────────────────────────────────────────┘ │
                └────────────────────────┬─────────────────────────────┘
                                         │ response text
                ┌───────────────────────▼──────────────────────────────┐
                │              SYNTHESIS LAYER                         │
                │  Text normalizer (indicnlp + Haiku LLM)              │
                │  SSML prosody injector (per AffectState + regime)    │
                │  Bulbul-V3 / Saarika-Aura TTS                        │
                │  Sentence-boundary chunker (first-15-token begin)    │
                │  Wait-aware FSM (ACTIVE/FILLING/HOLD/RETURN)         │
                │  Interrupt-cancel monitor                             │
                └────────────────────────┬─────────────────────────────┘
                                         │ audio
                ┌───────────────────────▼──────────────────────────────┐
                │              TELEPHONY OUTPUT                        │
                │  LiveKit → Exotel/Plivo SIP → caller                 │
                │  Parallel: WhatsApp BSP / email / SMS outbound       │
                └──────────────────────────────────────────────────────┘
```

### HITL Checkpoint Architecture

HITL is not a fallback — it is a first-class architectural component.

```
ESCALATION SENTINEL emits EscalationDecision every turn.
When escalate=true:
  1. PAUSE dialog worker (do not generate next response)
  2. GENERATE whisper_brief from Session State (3-5 lines)
  3. FIND available human in suggested_route queue
     - Available: warm transfer via SIP REFER + LiveKit room invite
     - Unavailable: offer callback, set SLA_callback_required flag
  4. BRIEF human via whisper channel (agent-side audio only)
  5. HUMAN acknowledges → agent releases caller
  6. LOG: escalation_reason, severity, route, time-to-human
  7. POST-CALL: tag call in QA flywheel as escalation-case for review

SUPERVISOR WHISPER architecture:
  - AI agent runs as LiveKit room participant
  - Supervisor has read-only subscription to all active sessions
  - Automated risk-triage surface shows: affect trajectory, fraud_risk,
    escalation_sentinel output per session
  - Supervisor injects whisper via separate WebRTC track
    (agent-side only, caller does not hear)
  - Barge-in: supervisor joins full track, agent yields automatically
```

### Memory Architecture (4-Layer)

```
LAYER 1 — In-Context (LLM window, 200K)
  - Current conversation turns
  - CallContext block (pre-assembled, GROUNDED — not LLM-generated)
  - Compliance ObligationManifest (injected as system-prompt block)
  - Session State object summary

LAYER 2 — Session State (Redis, session:{call_id}, 4h TTL)
  - {caller_id, primary_intent, entities{name,type,value,confidence,
     nbest,valid_at}, open_promises[], task_state, relationship_state,
     topic_threads[], verified_level, consent_events[], affect_history[]}
  - Written per-turn by Context Assembler
  - Read by every Skill Worker

LAYER 3 — Customer Long-Term (Mem0, customer:{id}, permanent)
  - Prior call summaries (last 12 calls)
  - Preferences (language, channel, callback window)
  - Vulnerability flags (DPDP-controlled access)
  - Historical sentiment trajectory
  - Promise history (broken PTPs → escalation risk score)

LAYER 4 — Org Knowledge (Qdrant, RAG KB)
  - Product sheets, policy documents, regulatory circulars
  - Procedure guides, escalation maps
  - Metadata: effective_from, effective_to, source_authority,
    regulator_ref, language, version
  - Indexed for hybrid BM25 + dense retrieval
```

### Action Safety Architecture

```
LLM (Skill Worker) → ActionIntent struct (Pydantic v2)
  - action_type, target_id, amount, channel, effective_date,
    conditionality_flag, confidence, source_utterance

→ Chain-of-Verification (Haiku 4.5 critique):
  - checks scope ambiguity, conditionality, confidence
  - emits: verified_action or ambiguity_flag

→ Authorization Gate:
  - checks tier (agent / TL / manager) against action type + amount
  - checks verified_level ≥ required_auth_level
  - emits: authorized | escalate_to_tier_X

→ TTS dry-run: reads back action to caller for consent
  - captures explicit confirmation (yes/no ASR)
  - on no/ambiguous: ABORT, do not write

→ IdempotencyMiddleware:
  - SHA-256(action_type + target_id + amount + channel + effective_date)
  - Redis hot-tier check (< 1ms)
  - on collision: return prior result, do not re-execute

→ Action Gateway MCP Tool:
  - executes against CRM/CBS/Gateway
  - reads system response (success/fail/timeout/partial)
  - on partial: fires saga compensation immediately
  - on success: generates ARN/ref, logs to immutable audit ledger

→ Post-execution verification:
  - reads CRM status field to confirm state change
  - confirms only after read-back succeeds
  - TTS: reads ref number + ETA to caller
```

---

## 8. MVP Build Sequence

The wedge is the deterministic spine + the highest-readiness steps. Ship what is already 8-10/10 first; they prove the architecture and generate the labeled data the harder steps need.

---

### Phase 1: The Deterministic Spine (Days 1-60)

**Goal:** A working end-to-end call that can handle clean, standard, non-adversarial inbound queries with full compliance, safety, and observability. No fraud, no vulnerable customers, no objections.

**Steps shipped in Phase 1:**
- Pre-call compliance check (OPA Rego, DND scrub, DLT validation)
- CTI screen-pop & context load (LangGraph pre-turn, asyncio.gather)
- Recording disclosure & DPDP consent delivery (deterministic FSM)
- Greeting + Identity verification (standard OTP/KBA path, no fraud edge cases)
- Knowledge lookup & grounding (hybrid RAG + groundedness gate)
- Eligibility checks & decisioning (OPA/DMN engine + LLM framing)
- Backend action execution (Action Gateway + idempotency + audit ledger)
- Call wrap-up & disposition coding (grounded multi-task LLM + Pydantic schema)
- After-call work & follow-up (Temporal durable workflow)
- Hold/silence etiquette (wait-aware FSM)
- Observability harness (OTel GenAI spans, per-turn cost attribution)
- Basic escalation (scope check + explicit human request trigger)

**Eval gates for Phase 1:**
- Compliance disclosure delivery: 100% of mandatory nodes reached on 200 test calls (zero misses, zero wrong order)
- Action safety: zero double-executions across 500 idempotency test cases (synthetic)
- Knowledge accuracy: faithfulness > 0.85 on 100-question golden set (product/policy)
- Disposition accuracy: top-1 disposition code accuracy > 80% on 200-call golden set
- End-to-end latency: P50 < 700ms, P95 < 1500ms on clean Indian telephony audio
- Cost attribution: 100% of calls have fully attributed $/turn within 5% of actual

**What Phase 1 covers on a 60-day demo:**

A human-supervised demo call in which an AI agent takes an inbound call about a personal loan EMI inquiry, verifies the caller's identity via OTP, looks up the correct EMI schedule from the policy KB, explains it accurately in Hinglish, handles a simple eligibility check for a payment pause, executes a callback scheduling action, delivers the required RBI disclosures, wraps up with a correct disposition code, and fires the DLT-approved SMS follow-up — all within 700ms P50 latency, with a full OTel trace showing per-turn cost and a compliance audit record.

**What Phase 1 does NOT cover:** Angry callers, fraud, vulnerable customers, complex negotiations, deep dialect speech, second-tier objections.

---

### Phase 2: Perception + Language + Emotion (Days 60-120)

**Steps added:**
- Active listening & messy speech (full noise pipeline + confidence-gated re-prompt)
- Language, dialect & code-mixing (end-to-end code-switch-native ASR, language-profile tracker)
- Intent recognition & disambiguation (MuRIL/IndicBERT + conformal prediction)
- Emotion & sentiment reading (dual-path SER deployed as copilot signal)
- Indic TTS & prosody (full Bulbul-V3 deployment + SSML prosody + interrupt-cancel)
- Real-time voice pipeline & latency (full VAD + barge-in + back-channel discrimination)
- Multi-turn context & working memory (typed Session State + Mem0 integration)

**Eval gates for Phase 2:**
- Code-switch ASR: entity-level F1 > 0.90 on Hinglish test set; WER < 20% on standard Hinglish
- Intent classification: macro-F1 > 0.82 on 200-intent golden set; clarify-ask rate < 15% of ambiguous calls
- Emotion detection: macro-F1 > 0.70 on arousal/valence labels; false-positive escalation rate < 10%
- TTS naturalness: MOS > 4.0 on Hinglish compliance script and Hinglish conversation samples
- End-to-end latency with full perception stack: P50 < 800ms, P95 < 1800ms

---

### Phase 3: Control, Exception, and Quality (Days 120-180)

**Steps added:**
- Empathy, rapport & de-escalation (full affective control loop, LAST/HEARD playbook)
- Compliance & mandatory disclosures (full vulnerability/confusion sensor)
- Escalation decision & warm handoff (dual-loop Sentinel + Warm Transfer Orchestrator)
- QA / eval flywheel (Gnani diarization + per-dimension LLM scorer + drift detector)
- Memory architecture (4-layer full deployment including customer long-term)
- RAG groundedness & hallucination guardrails (KB-coverage classifier + abstention path)
- Omnichannel integration (WhatsApp BSP + cross-channel CustomerState)
- PII redaction & data localization (GLiNER + in-country VPC)

**Eval gates for Phase 3:**
- De-escalation: CSAT on AI-handled angry-caller calls vs human baseline (target: within 5 CSAT points)
- QA automation: inter-rater kappa > 0.75 against human QA scores on 100 calibration calls
- Warm handoff: context-carry-forward completeness (zero "can you repeat?" on transferred calls on 50-call sample)
- Escalation trigger: precision > 0.90 on explicit-human-request detection; zero false-negative (every explicit request caught)
- PII redaction: Aadhaar/PAN/account-number precision > 0.99 in English; > 0.85 in Hindi (GLiNER baseline, improve over Phase 4)

---

### Phase 4: Adversarial & Sensitive Handling (Days 180-365)

**Steps added (as copilot/augmentation, not autonomous):**
- Fraud / abuse / social-engineering (sentinel track from copilot to gate mode)
- Vulnerable customer & duty of care (full four-driver classifier deployment)
- Objection handling & negotiation (RL/DPO fine-tuned stance policy)
- Cross-sell / up-sell judgment (restraint calibration via DPO on CSAT outcomes)
- Backend action execution on complex multi-system sagas
- Supervisor whisper / barge-in (LiveKit room participant architecture)
- Concurrent multi-session isolation (full defense-in-depth)

**Eval gates for Phase 4:**
- Fraud detection: AUC > 0.90 on confirmed fraud case held-out set; false-positive rate < 5% on legitimate distressed callers
- Vulnerability detection: recall > 0.90 on self-harm/crisis held-out set; four-driver macro-F1 > 0.65
- Cross-sell restraint: CSAT on cross-sell interactions vs human baseline; suppression rate on high-effort calls > 90%
- Session isolation: zero cross-session PII leaks on 10,000-session penetration test

---

## 9. Risks & Where It Breaks

The failure surface of a deployed AI contact-center agent is not uniformly distributed. These are the honest break points, organized by severity and probability.

---

### Critical Failures (low probability, catastrophic consequence)

**R1 — Live-coached deepfake call on a high-value action**

A fraudster uses a cloned voice model of the account holder to pass voice authentication, then a human operator guides the AI agent via social engineering toward a fund transfer or SIM-swap. Current anti-spoofing detectors (ASVspoof 2024-class) have ~8-12% EER on real-time telephony-degraded cloned audio. The agent's fraud sentinel may not catch a well-executed deepfake because the cloned voice passes the acoustic profile check.

**Mitigation:** Hard cap on actions executable without step-up to human (no fund transfer > ₹X without voice + OTP + human TL sign-off); cross-channel velocity check (SIM-swap attempts flag on cross-channel if the same customer "called" from two different numbers within 4 hours); NCRP 1930 golden-hour hold on any suspected fraud.

**R2 — Undetected self-harm disclosure on a "neutral" call**

A caller in genuine distress presents calmly (masked distress), never uses trigger keywords, and the AI agent does not escalate. The call ends. The caller is not routed to Tele-MANAS 14416.

**Mitigation:** High-recall binary crisis classifier (target: > 0.95 recall at the cost of false-positives); any ambiguous signal triggers an empathetic check-in ("aap theek hain?") before close; supervisor dashboard flags all calls containing specific affect-trajectory patterns (arousal dropping + valence sharply negative = potential masked distress).

**R3 — Compliance disclosure gap under barge-in**

The caller interrupts the RBI FPC mandatory disclosure mid-sentence. The agent stops TTS (correct behavior for barge-in), re-routes attention to the caller's interruption, and never re-inserts the interrupted disclosure. The call ends with a compliance gap.

**Mitigation:** Compliance FSM tracks delivered vs pending mandatory nodes independently of LLM dialog state. If a node is interrupted mid-delivery, it is marked incomplete and must be re-delivered at the next appropriate gap. The FSM blocks call close if any mandatory node is incomplete.

---

### High-Probability Failures (common at scale, manageable consequence)

**R4 — WER spike on rural Bhojpuri/Marwari caller destroys the call**

The ASR produces a garbled transcript. Every downstream step (intent, eligibility, action) fails. The caller repeats themselves 3-4 times and escalates to "human chahiye."

**Mitigation:** Per-entity confidence threshold; after 2 failed re-prompts on a critical entity, auto-escalate with a warm handoff summary. The escalation sentinel catches this loop within 3 turns. The real fix is Move A1 (dialect ASR fine-tuning) — this is the highest-ROI engineering investment for rural India coverage.

**R5 — "haan haan" backchannel triggers premature response**

Agent is mid-explanation of EMI schedule. Caller says "haan haan" (agreeing, not yielding). Silero VAD reads it as turn-end. Agent stops and waits. Caller now thinks the agent is broken.

**Mitigation:** Back-channel discrimination model (short-duration + rising pitch + < 200ms = agreement signal; suppress premature turn-end). Pipecat smart-turn-v3 model with Hindi-specific backchannel training. Deploy in A/B against raw VAD; measure premature-interrupt rate.

**R6 — Cross-session PII contamination under high load**

Under high concurrency (500+ simultaneous sessions), a session_id collision or a module-level mutable state variable leaks CustomerA's name into CustomerB's TTS output.

**Mitigation:** Immutable session_id (UUID v4) bound at SIP INVITE; BAN module-level mutable global conversation state via static analysis lint rule; 4-plane leak defense (memory plane + tool plane + logging plane + TTS plane each independently keyed on session_id); circuit-breaker on any detected leak (kill all workers in the affected pool, alert DPO within 4 hours per DPDP).

**R7 — OPA Rego stale on new RBI circular**

A new RBI FPC amendment changes the mandatory cooling-off disclosure requirement. Rego is not updated for 15 days. During those 15 days, the system runs 50,000+ calls without the new mandatory line. Each call is a regulatory violation.

**Mitigation:** Regulatory circular monitoring pipeline (Move F1) reduces detection-to-Rego latency. Conservative hot-patch mechanism restricts the action class requiring the new rule until Rego is updated. Legal team reviews the regulatory monitoring pipeline output daily, not weekly.

**R8 — Faithfulness failure on a regulatory-critical number**

The RAG pipeline retrieves an outdated version of a product sheet (effective_to date was 6 months ago). The agent quotes the old foreclosure charge figure to the caller. The caller relied on this, made a financial decision, and the agent quoted an incorrect number. This is a documented mis-selling event.

**Mitigation:** effective_from / effective_to metadata field enforced on all KB ingestion; queries always filter on effective_from <= today <= effective_to; stale documents are not deleted but are marked inactive and excluded from retrieval. The faithfulness verifier checks that quoted numbers match retrieved source text exactly (not paraphrase).

---

### Structural Risks (persistent, managed by design)

**R9 — Augmentation creep: the "mostly automated" trap**

The system achieves 90% automation and leadership reduces the human escalation pool. The remaining 10% of calls (fraud, vulnerable, complex disputes, novel situations) now have long queue times to reach a human. Customer experience on these high-stakes calls degrades severely — precisely the calls where the AI's failure ceiling is highest.

**Mitigation:** Maintain a minimum human escalation pool sized for 100% of HITL-triggered calls at peak volume, not 10%. The efficiency gain is in reducing the total pool needed, not in eliminating it. HITL trigger SLA: < 3-minute queue time to a human on any escalation.

**R10 — LLM hallucination bypassing the groundedness gate on edge-case queries**

The faithfulness verifier is trained on known query types. A novel query type (new product, new regulation, unusual customer scenario) produces a hallucination that the verifier rates as faithful because it superficially matches retrieved text structure.

**Mitigation:** The groundedness gate is a necessary but not sufficient safety measure. Defense-in-depth: (a) QA flywheel reviews 100% of calls with low retrieval confidence; (b) the abstention classifier is tuned to high recall (prefer abstaining over guessing); (c) weekly adversarial red-team tests on the groundedness gate with novel query types; (d) the "aapke case mein confirm karke batata hoon" abstention path is always available to the LLM as a first-class option.

**R11 — Emotional labor gap in sustained abuse calls**

A human agent can emotionally regulate, set a firm boundary, issue structured warnings, and terminate a call. An AI agent can execute this mechanically via the abuse classification + warning ladder. The risk is not that the AI gets upset — it is that the mechanical execution of a structured warning ladder reads as inhuman to an abusive caller, potentially escalating to a regulatory complaint ("the robot was rude to me"). 

**Mitigation:** The warning ladder language is generated by the LLM (warm, empathetic tone) but triggered deterministically (abuse classifier, not LLM discretion). The boundary is real; the language wrapping it is human. After the second warning, a warm transfer to a human is the correct resolution — the human can make a final judgment call that the AI cannot.

---

### The Honest Ceiling

Thirty-two of 36 steps can reach full automation on a 24-month roadmap. The four that remain human-augmented by deliberate design:

1. **Acute vulnerable-customer handling with self-harm signals** — regulatory duty of care; Tele-MANAS routing must be confirmed by a trained human.
2. **Novel fraud under active social engineering** — a human fraud desk agent reviewing the live call in real time is the only reliable gate against a motivated human adversary using novel pretexts.
3. **Financial advice for regulated investment products** — IRDAI and SEBI require a licensed financial advisor for certain advice categories; this is a legal boundary, not a capability gap.
4. **Consequential exception judgment on novel edge cases** — when no SOP applies and the decision has significant financial/regulatory/reputational stakes, a senior human's judgment call is the appropriate final gate.

These are not failures. They are the correct design. The goal of full adaptation is not zero humans — it is **humans working at their highest and most irreplaceable capacity**, doing the 4 things that actually require human judgment, while the 32 mechanical steps run reliably at machine speed and scale.

---

*Document compiled from 36 researched micro-step chunks. All readiness scores, gap analyses, and build specifications are derived from step-level decomposition, not assumed at the system level. India-specific regulatory references (RBI FPC, IRDAI norms, TRAI TCCCPR, DPDP Act 2023 + Rules 2025, CERT-In) reflect the regulatory environment as of mid-2026.*