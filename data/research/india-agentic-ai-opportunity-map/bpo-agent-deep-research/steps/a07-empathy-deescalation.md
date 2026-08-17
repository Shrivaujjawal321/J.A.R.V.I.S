# Step A07 — Empathy, Rapport & De-escalation (Calming an Angry/Upset Customer)

> Deep-research dossier for an India-market, multilingual (Hindi + regional + Hinglish), RBI/IRDAI/DPDP-compliant, action-taking voice+chat contact-center agent for mid-market BPOs.
> Scope: ONLY the empathy / rapport / de-escalation micro-step. Standalone — an engineer can build from this.
> Date: 2026-06-24. Tags: [sourced] = web-verified; [estimate] = first-principles inference.

---

## 0. Why this step is special

This is the one micro-step where the *delivery* matters as much as the *content*. A factually perfect refund offer delivered with flat affect at the wrong moment makes an angry customer angrier. De-escalation is a **closed-loop affective control problem**: read the customer's emotional state, choose a regulation tactic, render it with the right prosody and timing, observe the state change, and adjust — turn by turn, often before resolution exists. It sits *upstream* of and *interleaved with* problem-solving, not after it.

Two structural facts shape everything below:
1. **Anger is usually a mask for "I feel unheard."** ([sourced — callcenterstudio, getinsite]) The job is acknowledgement first, fix second.
2. **In 2026, the bottleneck is no longer "can the model sound empathetic" — frontier models already match/beat the *average* human on perceived empathy ([sourced — HEART, arXiv 2601.19922]). The bottleneck is adaptive reframing, tension-naming, boundary-holding under abuse, and avoiding "templatic" empathy.** That is precisely the gap to full adaptation.

---

## 1. Human micro-steps (the smallest atomic moves)

A skilled BPO agent runs this loop, mostly subconsciously:

**A. Detect & diagnose (perception)**
1. **Emotion read from voice** — pick up arousal (loud/fast = high) and valence (negative) from pitch, pace, volume, tremor — *before* parsing words. Tag: angry / frustrated / anxious / crying / sarcastic / resigned.
2. **Emotion read from words** — lexical cues ("ridiculous", "third time", "cheat", swearing, "main complaint karunga"), threats (legal, social-media, "RBI me shikayat").
3. **Intensity & trajectory** — is it escalating, plateaued, or already cooling? Rate-of-change matters more than the absolute level.
4. **Root-cause hypothesis of the anger** — money lost / time wasted / felt disrespected / fear (fraud, EMI default) / repeat-contact fatigue. The *driver* dictates the tactic.
5. **"Is this directed at me or the situation?"** — separates personal abuse (needs boundary) from situational venting (needs validation).

**B. Decide (policy)**
6. **Tactic selection** — acknowledge → validate → apologize → reassure → set expectation → solve. Pick the next move conditioned on state. (LAST: Listen, Apologize, Solve, Thank; or HEARD framework.)
7. **Let-them-vent vs. interject** — judge whether to stay silent (let the customer finish a rant) or to step in. Interrupting an angry venter escalates; over-silence reads as not caring.
8. **Pacing decision** — slow down own speech, lower volume, insert a beat of silence to model calm (mirroring-then-leading).
9. **Register/honorific selection (India)** — "sir/ma'am/ji", switch to the customer's language, drop jargon.

**C. Render (production)**
10. **Speak the empathy line with congruent prosody** — soft, slower, downward intonation; NOT chirpy. Tone-content congruence is the whole game.
11. **Backchannel while they vent** — "hmm", "ji", "samajh raha hoon", "haan" — low-volume, non-interrupting, to signal presence.
12. **Name the emotion + validate** — "I can hear how frustrating this is, and you're right to be upset that it happened three times."
13. **Take ownership / micro-apology** — "I'm sorry this happened" (situational apology) without admitting unlawful liability.
14. **Bridge to action** — "Here's exactly what I'll do right now…" — convert calm into a concrete next step (this is what actually closes anger).

**D. Verify & loop (feedback)**
15. **Re-read state after the move** — did volume drop? did they exhale? did they say "okay"? If yes → proceed; if no → re-validate or change tactic, don't push to solution.
16. **Hold boundary if abused** — calm, firm "I want to help you, and I'll need us to keep this respectful so I can" — repeat-warn-then-escalate.
17. **Know when it's beyond you** — sense self-harm, extreme threat, or unrecoverable rage → escalate to human/supervisor.

This 17-move loop runs continuously and **in parallel with** the resolution workflow.

---

## 2. Agent approach — how a 2026 AI agent does each move

The architecture is a **paralinguistic perception layer → affective state tracker → de-escalation policy → emotion-conditioned speech-to-speech rendering → post-turn state re-estimation loop.**

| Human move | 2026 agent technique |
|---|---|
| 1. Emotion from voice | Streaming **Speech Emotion Recognition** on 1–3 s windows. Use **Hume Expression Measurement API / EVI-3** (prosody model trained on millions of perceptual ratings) or a fine-tuned **wav2vec2/WavLM/Whisper-encoder SER head**; dimensional output: arousal + valence + discrete (anger/frustration/anxiety/sad). EmoNet-Voice-class fine-grained taxonomy (40 emotions, intensities). [sourced — Hume, EmoNet-Voice arXiv 2506.09827] |
| 2. Emotion from words | LLM/affect classifier on the live transcript (BERT-BiLSTM sentiment + LLM intent for threats/legal/abuse keywords). Fuse late with audio score. [sourced — Nature s41598-025-15501-y] |
| 3. Intensity & trajectory | Maintain a running **emotion time-series** in dialogue state; compute slope (escalating/cooling). Simulator-tracked per-turn user-state à la **EIBench** state vector. [sourced — EIBench arXiv 2606.15532] |
| 4. Root-cause of anger | LLM reasoning over transcript + CRM context (repeat contacts, amount, fraud flag) → labels driver (money/time/disrespect/fear/fatigue). |
| 5. At-me-or-situation | Abuse/toxicity classifier (e.g., Perspective-style or LLM) separates directed abuse from venting → routes to boundary policy vs. validation policy. |
| 6. Tactic selection | **De-escalation policy** = LLM prompted with an explicit playbook (acknowledge→validate→apologize→reassure→expectation→solve) **conditioned on the live emotion state**, ideally an **RL-tuned policy** (CTC-GRPO / turn-credit GRPO from EIBench) so the model optimizes the *trajectory of the user's emotion*, not just one nice-sounding reply. [sourced — EIBench] |
| 7. Vent vs. interject | **Turn-taking / barge-in model** (LiveKit adaptive interruption, smart-turn / semantic VAD) tuned to *not* barge in on an angry venter; backchannel instead; detect the "I'm done venting" cue (falling pitch, pause). [sourced — LiveKit, Hamming runbook] |
| 8. Pacing | Emotion-conditioned TTS: slow rate, lower pitch, insert short silences. Hume **Octave** exposes pacing/intensity as steerable params; EVI-3 adjusts pitch/pacing mid-utterance. [sourced — Hume Octave/EVI-3] |
| 9. Register/honorifics (India) | Language-ID + code-switch handler; system prompt enforces "ji/sir/ma'am", mirrors customer language; Hinglish-native LLM (**Sarvam-M / Bulbul-V3 TTS**, Krutrim, or fine-tuned). [sourced — Sarvam Bulbul V3] |
| 10. Congruent prosody render | **Speech-to-speech** model (EVI-3, OpenAI Realtime-2) that preserves emotion in generation, OR text-LLM + emotion-tagged TTS. Speech-to-speech avoids the "right words, wrong tone" failure. [sourced — Hume EVI-3, OpenAI Realtime-2] |
| 11. Backchannel | Low-latency injected "hmm/ji/haan" tokens during user speech via the turn-taking layer. |
| 12. Name+validate | LLM generates affect-labeling + validation; constrained by anti-template instructions (vary phrasing, reference the customer's *specific* grievance, not generic "I understand"). |
| 13. Micro-apology | Compliance-bounded apology templates (situational regret, no liability admission) — guardrail layer. |
| 14. Bridge to action | Tool-calling layer: as soon as state cools, the planner emits the concrete action ("processing refund now") — empathy and action are co-rendered. |
| 15. Re-read state | Next-turn SER + transcript → update emotion vector → close the loop. This is the dense reward signal for an RL policy. |
| 16. Boundary hold | Guardrail policy: detect abuse → calm firm warning → re-warn → escalate. (EIBench "Defense/boundary maintenance" axis — where models are weakest.) [sourced — EIBench] |
| 17. Escalate | HITL trigger classifier (self-harm, extreme threat, regulatory complaint, sustained rage post-2-attempts) → warm transfer to human. |

---

## 3. Tooling — concrete 2026 stack

**Perception (affect in)**
- **Hume Expression Measurement API** (48 vocal expression dims) or **EVI-3** speech-to-speech (reads + responds to emotion). [sourced]
- Open alt: **wav2vec2-XLSR / WavLM-Large** fine-tuned on **EmoNet-Voice / HumDial-EIBench** + IEMOCAP/MELD; add **Indic SER** fine-tune. [sourced]
- Transcript affect: **BERT-BiLSTM** or LLM (Sarvam-M / GPT-class) for lexical sentiment + threat/abuse detection. [sourced]

**Orchestration / turn-taking**
- **LiveKit Agents** (adaptive interruption handling, backchannel, barge-in) or **Pipecat** for the real-time pipeline. [sourced]
- **Smart-turn / semantic VAD** for end-of-vent detection. [sourced]

**Policy / dialogue brain**
- LLM with explicit de-escalation playbook in system prompt; for max quality, an **RL-tuned emotion-management policy** via **CTC-GRPO** trained against an **EIBench-style simulator**. [sourced — EIBench]
- Eval harness: **EIBench, HEART, AttuneBench, EQBench3, EmoBench-M, HumDial-EIBench**. [sourced]

**Rendering (affect out)**
- **Hume Octave TTS / EVI-3** (steerable emotion + pacing), **OpenAI Realtime-2** (speech-to-speech, contextual emotional register), or **ElevenLabs Flash v2.5 / Cartesia** for sub-100 ms TTFB when text-LLM + TTS split. [sourced]
- India voice: **Sarvam Bulbul-V3** (emotion-rich Hinglish, sub-250 ms streaming, 11 Indian langs). [sourced]

**Compliance / guardrails**
- Policy layer enforcing RBI call-window, recording disclosure, debt-validation, no-harassment caps, apology-without-liability. (See §10.)

**Observability**
- Per-turn emotion time-series logging, CSAT/escalation telemetry, **Coval/Hamming**-style voice-agent eval + adversarial angry-caller simulation. [sourced]

---

## 4. Benchmarks (real numbers)

- **Anger SER accuracy ~95%** (high-arousal emotions); confusable pairs (sadness vs distress) ~63% — anger is the *easy* emotion to detect, which favors this use case. [sourced — EmoNet-Voice / amity]
- Modern SER: **>90% on clean benchmarks, up to ~98%** for core emotions (anger/happiness); **drops to ~64%** when scaling data points / real noisy conditions. [sourced — Springer s10462-024-11065-x]
- **EVI-3 latency**: model response **<300 ms**, practical end-to-end **~1.2 s**; beats GPT-4o / Gemini Live on latency. [sourced — Hume/sureprompts]
- **TTS TTFB sub-100 ms**: Cartesia, Deepgram, Rime, ElevenLabs Flash v2.5. **Bulbul-V3 sub-250 ms** streaming. [sourced]
- **Human-conversation target latency ~500 ms**; production voice agents aim **≤800 ms**; barge-in cancel must add **<60 ms**. [sourced — Retell/futureagi]
- **HEART (2026)**: frontier LLMs **approach/surpass average human** on perceived empathy & consistency; humans still win **adaptive reframing, tension-naming, tone shifts in adversarial turns**. LLM-judge vs human agreement **~80%**. [sourced — HEART arXiv 2601.19922]
- **EIBench**: CTC-GRPO lifts Qwen3-8B from **−22.4 → +22.4**; generalizes (SAGE +12.4, EQBench3 +20.9%). Models strong on support/rapport, **weak on boundary maintenance under pressure**. [sourced — EIBench arXiv 2606.15532]
- **Hinglish code-switch ASR WER ~42%** on standard monolingual models — the upstream risk that corrupts everything downstream. [sourced — autointerviewai/caller.digital]
- **Emotion-aware Hindi voicebot reduced escalations ~80%** (vendor-reported, BFSI). [sourced — Tabbly — treat as vendor claim, not independent].
- **"Templatic empathy"**: LLMs deploy a narrow, well-liked empathy template reliably across model families — liked by raters but not adaptive. [sourced — arXiv 2604.08479].

---

## 5. Failure modes

1. **Tone-content incongruence** — right empathy words, flat/chirpy voice. The #1 trust-killer. Mitigated only by speech-to-speech or tightly emotion-conditioned TTS.
2. **Templatic empathy** — "I understand how frustrating this is" on loop; the customer notices the script and escalates *because* it feels robotic. [sourced]
3. **SER errors under Indian conditions** — noise, accents, code-switch, sarcasm; misreads frustration as neutral or detects anger when it's just a loud speaker. Real-world SER drops to ~64%. [sourced]
4. **Barge-in mishandling** — interrupting a venting angry customer (escalates) OR failing to stop talking when they cut in (reads as not listening). [sourced]
5. **Boundary collapse under abuse** — models over-apologize / capitulate to abusive or manipulative pressure rather than holding a calm boundary. EIBench's weakest axis. [sourced]
6. **Validating an illegitimate demand** — empathizing so hard it implies the customer is owed something they aren't (refund, liability admission) → compliance + business risk.
7. **Empathy-then-no-action gap** — soothing words with no concrete fix re-ignites anger ("don't just say sorry, DO something").
8. **Latency-induced dead air** during an emotional moment reads as cold; >800 ms feels like the bot froze. [sourced]
9. **Emotion whiplash** — TTS snapping from sad-soft back to cheerful too fast after partial resolution.
10. **Hinglish/regional misread** — "Haan ji" as agreement vs sarcastic frustration; honorific or language mismatch insults the customer. [sourced]
11. **Missing the trajectory** — reacting to absolute anger level, not its slope; keeps de-escalating a customer who already calmed (patronizing) or under-responds to a fast escalation.
12. **Sarcasm / suppressed anger** — calm voice, hostile words ("wah, badhiya service") — audio says neutral, intent is furious. Multimodal fusion gap.

---

## 6. Gap to full adaptation (what the agent STILL can't match a human on)

Per HEART (2026) the residual human advantages — and the concrete path to close each:

- **Adaptive reframing** (turning a complaint into a manageable next step in a genuinely novel way). → Close via **RL on emotion-trajectory reward** (CTC-GRPO/EIBench simulator) so the policy optimizes *did the customer actually calm*, not "did this sound nice." Build an India-BPO-specific simulator from real (anonymized) escalation transcripts.
- **Tension-naming** (explicitly, gracefully calling out the elephant: "I can tell you've lost trust in us"). → Fine-tune on **gold de-escalation transcripts where senior agents name tension**; add a "tension-naming" skill to the playbook with anti-template constraints.
- **Boundary maintenance under abuse/manipulation** (the EIBench weak axis). → Targeted RL on **Defense/Repair scenarios**; explicit guardrail policy with calm-firm-warn-escalate ladder; reward self-protection + alignment jointly (current systems do alignment only). [sourced — EIBench, de-escalation survey]
- **Nuanced tone shifts in adversarial turns** — smooth, sub-second prosody control that tracks micro-changes. → Speech-to-speech models with **continuous, mid-utterance prosody steering** (EVI-3 direction) + closed-loop on live SER, not turn-batched.
- **Multimodal sarcasm / suppressed-anger detection.** → Train fusion head on **code-mixed sarcasm corpora** (e.g., commonsense-augmented code-mixed emotion data) + Indic prosody. [sourced — arXiv 2310.13080]
- **Genuine accountability + discretionary goodwill** (a human can *mean* "I'll personally fix this" and bend a rule). → Give the agent **bounded discretion tools** (pre-approved goodwill credits, callback commitments) so empathy converts to real authority, not theater.

**Net:** the perception + rendering gap is mostly *closed* (anger detection ~95%, emotive TTS strong). The remaining gap is **policy under adversarial/abusive/novel turns** — solvable with simulator-based RL on an India-specific emotion-management environment, NOT with bigger base models.

---

## 7. HITL trigger (when a human MUST take over)

Hand off to a human/supervisor when ANY of:
- **Self-harm / suicidal ideation / threat of violence** signaled → immediate warm transfer + safety protocol.
- **Sustained rage after ≥2 de-escalation attempts** with no cooling (trajectory flat/up) → escalate before brand damage.
- **Explicit demand for a human / "I want to speak to a manager"** — honor immediately (forcing the bot escalates).
- **Regulatory/legal threat** ("RBI/IRDAI complaint", "lawyer", "consumer court") → human + compliance loop.
- **Abuse beyond boundary ladder** (post-warnings) → policy-defined transfer or controlled disconnect.
- **SER/intent confidence below threshold** in a high-emotion turn → don't gamble; route to human.
- **Vulnerable customer** (elderly, distressed-fraud-victim, financial-hardship disclosure) → human empathy is safer + compliance-favored.

Not "none — fully automatable": de-escalation has a non-trivial tail of high-stakes emotional/regulatory cases where a confident human handoff is the correct product behavior.

---

## 8. Automation readiness: **6 / 10**

Justification: Perception (anger detection ~95%) and emotive rendering (EVI-3/Octave/Bulbul-V3) are **production-ready**. Empathy *delivery* already matches the average human ([HEART]). What caps it at 6: (a) the **policy gap under adversarial/abusive/novel turns + boundary-holding** (EIBench-weak), (b) **Indian-condition SER robustness** (noise/code-switch/sarcasm, WER 42% upstream risk), (c) **templatic-empathy** ceiling, and (d) the **regulatory tail** demanding HITL. For *routine* frustrated-customer de-escalation in a single language: ~8/10. For the *full* angry-spectrum incl. abuse/threats/Hinglish-sarcasm in compliant BFSI: ~6/10. Ship as **agent-led with human-on-the-loop escalation**, not human-out-of-the-loop.

---

## 9. Build spec

**Implement**
1. **Affect-in pipeline**: streaming SER (Hume EVI-3 or fine-tuned WavLM) fused (late fusion) with transcript sentiment/threat/abuse classifier → unified per-turn emotion vector (arousal, valence, discrete label, intensity, confidence).
2. **Emotion state tracker**: rolling time-series + slope (escalating/cooling) + root-cause label + at-me/at-situation flag.
3. **De-escalation policy**: LLM with explicit playbook (acknowledge→validate→apologize→reassure→set-expectation→solve) conditioned on the emotion vector; **boundary ladder** sub-policy; **anti-template** constraint (must reference the customer's specific grievance, vary phrasing). Phase 2: replace prompt-policy with **CTC-GRPO RL** against an India-BPO emotion simulator.
4. **Turn-taking layer** (LiveKit): backchannel during vent, no barge-in on anger, end-of-vent detection.
5. **Affect-out rendering**: emotion-conditioned speech-to-speech (EVI-3) or emotion-tagged TTS (Bulbul-V3 for Hindi/Hinglish) with pacing/pitch/silence control + smooth (no-whiplash) transitions.
6. **Action bridge**: tool-calls fire the concrete fix the moment state cools; bounded goodwill tools.
7. **Compliance guardrail** wrapping all output (§10).
8. **HITL router** (§7) with confidence + safety + regulatory triggers.

**Data needed**
- Real (anonymized, consented) angry-call recordings + transcripts from the BPO, labeled for: emotion-per-turn, trajectory, tactic used, outcome (calmed Y/N), CSAT.
- Hinglish/regional + sarcasm-in-code-mix emotion corpus for SER/intent fine-tune. [sourced — arXiv 2310.13080]
- Gold de-escalation transcripts from **top human agents** (for SFT of reframing/tension-naming).
- An **EIBench-style simulator** seeded with India scenarios (Support/Defense/Repair/Charm) for RL + eval.

**Eval metric that gates ship**
Primary gate: **De-escalation Success Rate (DSR)** = fraction of angry-onset calls where the emotion-trajectory slope turns negative (customer measurably calms) within N turns AND the call ends with CSAT ≥ threshold AND no unresolved abuse-boundary breach. Target gate: **DSR ≥ senior-human baseline on a held-out angry-call set** + **escalation-appropriateness ≥ 95%** (HITL fired when it should, not when it shouldn't) + **zero compliance violations** (apology-without-liability, call-window, disclosure). Secondary: HEART-dimension scores ≥ average-human, EIBench Defense-axis above a floor, perceived-empathy human rating, false-barge-in rate, p95 latency ≤ 800 ms. Adversarial suite: abusive/manipulative/sarcastic/Hinglish callers (Coval/Hamming-style sim).

---

## 10. India specifics

**Language / culture**
- **Code-switching is the default** — Hindi+English+regional in one sentence; monolingual ASR ~42% WER → use Hinglish-native stack (Sarvam Bulbul-V3 / Sarvam-M, Krutrim). Empathy lines must be *natively* Hinglish, not translated ("Main samajh sakta hoon aapko kitni pareshani hui hai"). [sourced]
- **Honorifics are non-negotiable** — "ji / sir / ma'am"; respectful register; tone calibration differs by region (Tamil/Telugu/Bengali/Marathi politeness norms).
- **"Haan ji" ambiguity** — agreement vs sarcastic frustration; needs prosody fusion, not lexical-only. [sourced]
- **Regional emotional display rules** differ — same de-escalation tactic lands differently across states; per-language SER + tactic tuning.

**Regulatory (de-escalation-relevant)**
- **RBI Fair Practices Code (DBR.LEG master circular, Jul 2024)**: no calls before 8 AM / after 7 PM; **≤3 calls/day** to same borrower; no abusive language / public shaming; no contacting family/employer. A de-escalation flow must never breach these even when the *customer* is hostile. [sourced]
- **DPDP Act 2023**: consent/lawful basis, data minimization, recording disclosure, retention logs — emotion data is personal data; storing affect time-series needs lawful basis + minimization. [sourced]
- **IRDAI**: recording disclosure in opening utterance, licensed POSP handoff on binding questions, insurer name disclosed, no rebate language. [sourced]
- **Call recording**: RBI mandates recording for complaints, **≥2-yr retention**, secure storage + access logs. [sourced]
- **Apology discipline**: situational regret ("I'm sorry this happened") is fine; **liability admission is not** — guardrail must enforce.
- **HITL is partly a compliance feature**: regulatory-threat or vulnerable-customer triggers map to legal-safe human handoff.

---

## Sources
- EmoNet-Voice (fine-grained SER benchmark): https://arxiv.org/abs/2506.09827
- Real-time SER + accuracy ranges: https://link.springer.com/article/10.1007/s10462-024-11065-x
- Hume EVI-3 / Octave (emotion + prosody, latency): https://www.hume.ai/empathic-voice-interface ; https://www.techraisal.com/blog/hume-ai-empathic-voice-real-time-emotion-and-evi-3-for-conversational-ai_1756380371/
- Voice model comparison 2026 (latency/TTFB): https://sureprompts.com/blog/voice-generation-models-compared-2026 ; https://www.marktechpost.com/2026/05/30/best-text-to-speech-tts-models-in-2026-a-benchmark-based-comparison/
- EIBench (turn-credit RL, emotion management, boundary weakness): https://arxiv.org/abs/2606.15532
- HEART (humans vs LLMs emotional support; residual human edge): https://arxiv.org/abs/2601.19922 ; https://techxplore.com/news/2026-02-heart-benchmark-ability-llms-humans.html
- Templatic empathy: https://arxiv.org/pdf/2604.08479
- BERT-BiLSTM + GenAI proactive care: https://www.nature.com/articles/s41598-025-15501-y
- De-escalation techniques / empathy statements: https://callcenterstudio.com/genel/7-empathy-statements-that-de-escalate-angry-callers-instantly/ ; https://blog.getinsite.io/effective-customer-service-de-escalation-skills-for-call-center-agents ; https://convin.ai/blog/de-escalation-techniques
- Barge-in / turn-taking 2026: https://hamming.ai/resources/voice-agent-interruption-handling-runbook ; https://futureagi.com/blog/voice-ai-barge-in-turn-taking-2026/ ; https://docs.livekit.io/agents/logic/turns/adaptive-interruption-handling/ ; https://www.retellai.com/resources/ai-voice-agent-latency-face-off-2025
- India multilingual / Hinglish voice AI + Sarvam Bulbul-V3: https://www.autointerviewai.com/blog/vernacular-ai-voice-agents-india-hinglish-code-switching-2026 ; https://www.sarvam.ai/apis/text-to-speech/hindi ; https://caller.digital/blog/multilingual-voice-ai-hindi-tamil-telugu-bengali-india-2026
- Code-mixed emotion/sarcasm: https://arxiv.org/pdf/2310.13080
- India regulatory (RBI/DPDP/IRDAI): https://www.carmaone.ai/blog/rbi-compliant-ai-collections-guide-india-2026 ; https://www.caller.digital/blog/dpdp-act-compliance-checklist-voice-ai-india ; https://www.conversailabs.com/blog/voice-ai-compliance-in-india
- Vendor escalation-reduction claim (treat cautiously): https://www.tabbly.io/blogs/hindi-ai-voice-agents-multilingual-india
