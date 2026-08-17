# Step A06 — Emotion & Sentiment Reading

**(Detecting frustration, distress, sarcasm, urgency in voice)**

Deep-research dossier · India-market multilingual (Hindi + regional + Hinglish) action-taking voice+chat contact-center agent · RBI/IRDAI/DPDP-compliant · mid-market BPOs.

Last updated: 2026-06-24. Tagging convention: **[sourced]** = backed by a cited link, **[estimate]** = my engineering judgment, **[analysis]** = inference.

---

## 0. Why this step is special (the one-paragraph framing)

Emotion reading is the **affective sensing layer** of the agent. It does not take an action by itself — it produces a continuously-updated *affect state* (valence, arousal, specific emotion labels, confidence, trajectory) that every downstream module consumes: tone of the TTS reply, escalation routing, retention-offer triggering, compliance guard ("is this person in distress → do not hard-sell"), and supervisor barge-in. It is therefore a **cross-cutting signal producer**, not a terminal action. The hard truth from 2026 research: machines are *good at coarse arousal* (loud/agitated vs calm), *mediocre at fine-grained emotion in the wild*, and *bad at sarcasm and masked distress*. Real-world spontaneous speech drops accuracy ~24 points vs acted lab data (EMOVOME 45.6% UA vs IEMOCAP 69.6% UA) [sourced]. The whole engineering game on this step is closing that lab→field gap on Indian code-mixed audio while staying inside DPDP/inference-of-emotion regulatory lines.

---

## 1. Human micro-steps — what a skilled BPO agent actually does

A good human agent does emotion reading **continuously and pre-attentively** while also doing everything else. Decomposed into atomic moves:

1. **Acoustic baseline calibration (first 3–8 sec).** Subconsciously fixes the caller's *normal* pitch, pace, loudness, accent — so later deviations register as signal, not trait. (A naturally loud Punjabi speaker ≠ angry.)
2. **Arousal tracking (continuous).** Notices energy/loudness/pitch-range/speech-rate spikes → "this person is getting heated / panicked / rushed."
3. **Valence read (continuous).** Positive vs negative tilt — warmth, sigh, clipped tone, exhale of relief.
4. **Specific-emotion labeling.** Maps the blend to a label set that matters operationally: frustration, anger, anxiety/distress, confusion, resignation/hopelessness, satisfaction, impatience/urgency.
5. **Lexical-affect fusion.** Combines *what* was said ("ye teesri baar bol raha hu") with *how* (flat, exhausted tone) — the repetition + flat affect = escalation risk.
6. **Sarcasm / incongruence detection.** Catches when words say one thing and prosody/context says the opposite ("haan haan bahut achhi service hai aapki" said flat/clipped = complaint, not praise).
7. **Masked-distress detection.** Notices over-controlled calm, long pauses, voice tremor, a swallowed word — "polite but actually about to churn / actually in financial distress."
8. **Urgency vs anger disambiguation.** Fast loud speech can be *time-pressure urgency* ("flight 2 ghante me hai") OR *anger*; the human disambiguates by content + who-the-pressure-is-aimed-at.
9. **Cause attribution.** Decides whether the negative affect is *at me/company* (complaint), *at situation* (sympathy needed), or *trait* (just a brusque person).
10. **Trajectory/derivative read.** Tracks the *slope* — is the customer cooling down after my apology, or still climbing? This dictates next move more than the absolute level.
11. **Threshold-to-action mapping.** Converts the affect read into a decision: soften tone, apologize, slow down, offer escalation, stop pitching, alert nobody / alert supervisor.
12. **Cultural/register adjustment.** Re-weights all of the above for region, gender, age, formality (a respectful "ji" tone masking anger; rural vs metro directness; festival-season stress).

The expert difference vs a novice: **micro-steps 1, 6, 7, 9, 10** (baseline normalization, sarcasm, masked distress, attribution, trajectory). Novices catch raw arousal only.

---

## 2. Agent approach — how a 2026 AI agent does each sub-step

| Human micro-step | 2026 agent technique |
|---|---|
| 1. Baseline calibration | Per-call **speaker-relative normalization**: z-score the prosodic features (pitch F0, energy, rate from a Praat/openSMILE/`opensmile` eGeMAPS extractor) against a rolling 5–8s window of *that caller's* speech, not a global prior. Reduces "loud-speaker = angry" false positives. [analysis] |
| 2. Arousal tracking | Streaming **acoustic SER head** on a self-supervised audio backbone: `emotion2vec_plus` / fine-tuned **wav2vec2/WavLM** emitting valence-arousal-dominance (VAD) regression every 250–500ms window. Arousal is the most reliable axis. [sourced — emotion2vec, wav2vec2 SER] |
| 3. Valence read | Same VAD head; valence is weaker than arousal, fuse with text. [sourced — acoustic better for arousal than valence] |
| 4. Specific-emotion labeling | **Two-track fusion**: (a) acoustic classifier over a *call-center label set* (frustration/anger/anxiety/confusion/satisfaction/urgency), (b) **speech-LLM** (Qwen2-Audio-7B or Audio Flamingo 3, LoRA-tuned) doing instruction-style "classify the emotion + give reasoning." Late-fuse logits. [sourced — VoxEmo] |
| 5. Lexical-affect fusion | **Multimodal late fusion**: ASR transcript → text emotion model (IndicBERT / multilingual-BERT-BiLSTM) fused with acoustic logits via a small gating MLP. BERT+BiLSTM hybrids hit <200ms in production. [sourced — Nature BERT-BiLSTM] |
| 6. Sarcasm / incongruence | **Prosody-text contradiction detector**: explicitly compute disagreement between text-sentiment and acoustic-valence; high disagreement → sarcasm/incongruence flag. This is exactly the VoxParadox failure axis — baseline audio-LLMs collapse to 8–17% when prosody contradicts text, recoverable to ~65–72% with PCLM+DPO contrastive training. [sourced — VoxParadox] |
| 7. Masked distress | Detect **low-arousal-negative-valence + lexical distress markers + long pauses + voice tremor (jitter/shimmer from eGeMAPS)**. Specialized rule+ML overlay; weakest area. [estimate] |
| 8. Urgency vs anger | **Content-conditioned classifier**: feed transcript intent (deadline/time words) + acoustic arousal → separate "urgency" head from "anger" head. Don't let one acoustic spike fire both. [analysis] |
| 9. Cause attribution | LLM reasoning over dialogue context: target-of-sentiment classification (at-agent / at-company / at-situation / trait). Aspect-based sentiment, not just polarity. [analysis] |
| 10. Trajectory read | **Stateful affect tracker**: EMA + slope of valence/arousal over the call; emit `escalating` / `de-escalating` / `stable`. This derivative is the highest-value cheap feature. [estimate] |
| 11. Threshold→action | Policy layer maps {emotion, confidence, slope} → action tokens consumed by dialogue manager (soften, apologize, escalate, stop-pitch). Hysteresis to avoid flapping. [analysis] |
| 12. Cultural/register | Domain-adapt + region-conditioned models; fine-tune on Indian code-mixed emotional corpora; condition on detected language/region. In-group advantage is real and measurable. [sourced — cross-cultural in-group advantage] |

**Recommended architecture (2026 default):** Hybrid **cascade + parallel-acoustic** —
- Streaming STT (Sarvam / Gnani / AssemblyAI Indic) → transcript track.
- Parallel **always-on acoustic SER** (emotion2vec/WavLM head) on the raw stream → VAD + label track every ~300ms (does NOT wait for ASR; preserves prosody the cascade would lose).
- **Late multimodal fusion** + **incongruence/sarcasm detector** + **trajectory tracker** → single affect-state object.
- A periodic **speech-LLM reasoning pass** (turn-level, not per-frame) for sarcasm/attribution/nuance where latency budget allows.

This dual-path matters because pure cascaded (STT→text) systems **lose tone/prosody in the handoff** [sourced]; pure speech-to-speech models carry prosody but are weak at fine labels and expensive. The parallel acoustic side-channel is the standard 2026 fix.

---

## 3. Tooling — concrete 2026 stack

**Acoustic SER backbone / heads**
- `emotion2vec` / `emotion2vec_plus_large` (FunASR/ModelScope) — universal SER embeddings, strong few-shot.
- `wav2vec2`/`WavLM-large` fine-tuned on IEMOCAP+MELD+Indian corpora (SpeechBrain recipe `emotion-recognition-wav2vec2-IEMOCAP`).
- **openSMILE / Praat-parselmouth** for eGeMAPS low-level descriptors (F0, jitter, shimmer, loudness) → cheap interpretable features for baseline normalization + tremor.

**Speech-LLM (turn-level nuance / sarcasm / reasoning)**
- **Qwen2-Audio-7B-Instruct** (best open-weight on VoxEmo after LoRA, +23.7 Macro-F1) or **Audio Flamingo 3**; add **PCLM + DPO** contrastive training to survive prosody-text contradiction (VoxParadox 17→65%). Kimi-Audio / Qwen2.5-Omni as alternates.

**Text-emotion track**
- IndicBERT v2 / MuRIL / multilingual-BERT + BiLSTM head (sub-200ms hybrid). Aspect/target sentiment via a small instruct LLM.

**Streaming Indic STT (feeds text track)**
- **Sarvam** (11 Indian languages, real-time streaming), **Gnani** (14B voice-first Indian model), **AssemblyAI** / Deepgram for English-heavy Hinglish, IndicConformer/IndicWhisper open-source fallback.

**Orchestration / streaming**
- Pipecat / LiveKit Agents / Retell (emotion-adaptive dialogue) for the realtime audio graph; WebSocket multiplex (reuse one socket across turns, ~50ms/turn saved — Gradium pattern).

**Data / training corpora**
- Indian emotional speech: **IITKGP-SEHSC** (Hindi, 12k utts), **EmoTa** (Tamil, 936 utts, κ=0.74), Telugu AIR corpus, EmoInHindi (multi-label dialogues), MUStARD/MUStARD++ (sarcasm, English — for sarcasm head pretraining), EMOVOME (real-life spontaneous, for field realism). **You will still need to collect your own Hinglish call-center corpus** (see Build Spec).

**Eval**
- VoxEmo toolkit + EmoBox (multilingual multi-corpus SER) for offline; custom production eval on held-out real calls.

---

## 4. Benchmarks — real numbers

| Metric | Number | Source |
|---|---|---|
| IEMOCAP SER weighted acc (wav2vec2 + NCDE, 2025) | **73.37% WA / 74.18% UA** | [sourced] PLOS One 2025 |
| IEMOCAP (wav2vec2 + ConLearnNet) | 72.86% WA / 72.85% UA | [sourced] MDPI Electronics |
| **Real-world spontaneous (EMOVOME)** | **45.58% UA** | [sourced] EMOVOME arXiv |
| RAVDESS (acted) for contrast | 75.00% UA | [sourced] EMOVOME paper |
| Speech-LLM zero-shot (Qwen2-Audio) Macro-F1 range across 35 corpora | ~1%–77% (wildly dataset-dependent) | [sourced] VoxEmo |
| Qwen2-Audio after LoRA fine-tune | **+23.7 Macro-F1**, beats traditional baseline on 10/30 datasets | [sourced] VoxEmo |
| **Sarcasm / prosody-contradicts-text (VoxParadox emotion+intonation)** baseline | **GPT-4o-Audio 8.6%, AF3 17.4%, Qwen2.5-Omni 7.95%** | [sourced] VoxParadox |
| Same, after PCLM+DPO mitigation | **65.2%–72.3%** | [sourced] VoxParadox |
| Real-time emotion latency (BERT+BiLSTM hybrid) | **<200ms end-to-end** | [sourced] Nature s41598-025-15501-y / Haptik |
| Speech-to-speech time-to-first-token (Apr 2026) | 0.78s (Grok Voice) – 2.98s (Gemini 3.1 Flash Live); human ~200ms | [sourced] Inworld/AssemblyAI |
| Multimodal vs text-only emotional-intent classification lift | **+23% to +37%** | [sourced] Haloocom/Haptik |
| Inter-annotator agreement on emotion labels (the ceiling) | **~60% avg** | [sourced] ground-truth survey |
| EmoTa Tamil inter-annotator Fleiss κ | 0.74 (substantial) | [sourced] EmoTa |
| Business outcomes claimed (real-time sentiment) | up to +30% FCR, −25% escalations, −40% AHT | [sourced — vendor claims, treat as marketing] Gnani/Haloocom |

**Key takeaway for Boss:** the *honest* operating number on real Indian call audio for fine-grained emotion is **~45–60% UA**, not the 73% you see in IEMOCAP papers. Arousal-only (calm vs agitated) is much higher (~80%+ [estimate]). Sarcasm in voice is near-broken out-of-the-box (<20%).

---

## 5. Failure modes

1. **Acted→field collapse.** Models trained on IEMOCAP/RAVDESS drop ~24 UA points on spontaneous calls. [sourced]
2. **Sarcasm / incongruence.** Audio-LLMs read the transcript, not the prosody — collapse to 8–17% when tone contradicts words. Worst on Hinglish polite-sarcasm ("waah, kya service"). [sourced]
3. **Loud-speaker / accent false-positive.** Regional loud/fast prosody (Punjabi, Bhojpuri, some Tamil registers) flagged as anger without speaker-relative baseline. [analysis]
4. **Masked distress miss.** Over-controlled, quiet, financially-distressed callers (very common in collections) read as "neutral/calm" — the most operationally costly miss. [estimate]
5. **Urgency↔anger confusion.** Same acoustic arousal; without content conditioning the agent apologizes when it should just act fast (or vice versa). [analysis]
6. **Code-switch boundary errors.** Emotion + language ID + ASR all degrade at Hindi↔English switch points; misaligned transcript corrupts text-track fusion. [analysis]
7. **Channel/telephony noise.** 8kHz narrowband, packet loss, background (street, family, TV) — Indian calls are noisy; SER is brittle to it. [estimate]
8. **Label-set mismatch / soft labels.** Operational emotions (frustration, resignation) aren't IEMOCAP's 4 classes; and humans only agree ~60% anyway — a hard label is often wrong by construction. [sourced]
9. **Cross-cultural / in-group gap.** Models trained on Western affect underperform on Indian expression norms. [sourced]
10. **Latency vs depth tradeoff.** The speech-LLM that catches sarcasm is too slow for per-frame; the fast acoustic head misses sarcasm. Architectural tension. [analysis]
11. **Trajectory flapping.** Without hysteresis, the affect state oscillates and triggers contradictory tone changes mid-sentence. [analysis]

---

## 6. Gap to full adaptation — what the agent still can't do, and how to close it

**What the human still beats the agent at:**

- **A. Masked / suppressed emotion** (distress hidden behind politeness). Human catches the swallowed word, the half-second hesitation, the "I'm fine" that isn't. Agent reads calm.
- **B. Sarcasm & irony in Hinglish.** Human uses shared cultural context; agent reads the literal transcript.
- **C. Cause attribution + trait-vs-state.** Human knows "this person is just brusque" vs "this person is now angry at me." Agent over-triggers on trait-brusque speakers.
- **D. Multi-turn affective theory-of-mind.** Human tracks *why* the mood is moving and predicts it ("she'll explode if I quote the fee now"). Agent reads present state, not predicted reaction.
- **E. Ground-truth ceiling.** Even humans only agree ~60%; "full adaptation" to an unreliable target is ill-posed — the goal is *human-parity*, not 100%.

**Concrete path to close each:**

- **Close A (masked distress):** Build a dedicated *suppressed-distress* head trained on (i) jitter/shimmer/micro-tremor eGeMAPS features, (ii) pause-duration distributions, (iii) lexical distress markers, on a **collections/insurance-claim corpus** with *outcome labels* (did the person actually churn / default / file complaint) as distant supervision — not just perceived-emotion labels. Outcome-grounded labels beat perceived-emotion labels for the cases that matter.
- **Close B (sarcasm):** Add **PCLM + DPO contrastive training** (VoxParadox method: 17→65%) on a synthetically-augmented Hinglish sarcasm set (controlled TTS that mismatches transcript and prosody), plus mine real sarcastic call segments. Explicitly feature the **text-sentiment vs acoustic-valence disagreement score** as input.
- **Close C (attribution):** Aspect/target-based sentiment LLM pass + a per-caller baseline so trait-brusqueness is normalized out (micro-step 1). Personalize the threshold to the speaker's own baseline.
- **Close D (predictive ToM):** Sequence model over the affect-state trajectory predicting *next-turn* emotion conditioned on the agent's candidate action — i.e. "if I quote fee now, P(anger spike)=0.7." Train on historical calls where the action and the subsequent reaction are both logged. This is the genuinely hard frontier.
- **Close E (ceiling):** Move from hard labels to **soft-label / distributional targets** (VoxEmo's prompt-ensemble insight) and evaluate against the action that mattered, not against a noisy emotion label.

**The single highest-leverage investment:** a **proprietary, outcome-labeled Hinglish call-center emotional corpus** (real spontaneous calls + business outcome + light human emotion annotation). Every gap above is bottlenecked on *Indian spontaneous data*, not on model architecture. Architecture is commodity; the data moat is the product.

---

## 7. HITL trigger — when a human must take over

Emotion reading itself is a **background signal**; you rarely "hand off the sensing." But it should **trigger** human handoff of the *conversation* when:

1. **Confidence-gated distress.** Affect state = anxiety/distress/hopelessness with confidence > τ AND high-stakes context (collections, insurance claim, medical, suicidal-ideation lexical markers) → **mandatory human/supervisor barge-in**. Distress + vulnerability is a hard HITL line, not a soft one.
2. **Sustained escalation.** Trajectory = escalating for N turns despite de-escalation attempts → route to human.
3. **Sarcasm/incongruence flag on a complaint** where misreading would worsen it → human review.
4. **Low overall affect confidence on a high-value/at-risk customer** → human.
5. **Regulatory vulnerability detection** (DPDP "vulnerable data principal" cues, RBI fair-practice distress signals in recovery calls) → human, because acting on inferred emotion to push a financial product to a distressed person is a compliance landmine.

Otherwise: **fully automatable as a signal producer.** The *sensing* is automated; the *override authority* on detected distress stays human.

---

## 8. Automation readiness: **5 / 10**

Rationale [analysis]:
- **Arousal / agitation detection** alone: ~8/10 — reliable, low-latency, shippable today.
- **Frustration/urgency coarse buckets** with text fusion: ~6/10 — usable with HITL and conservative thresholds.
- **Fine-grained specific emotion on spontaneous Hinglish:** ~4/10 — real-world UA ~45–55%.
- **Sarcasm / masked distress:** ~2–3/10 — near-broken out-of-the-box; the drag on the composite.
- Weighted for *fully replacing a skilled human's emotional read* → **5/10**. Good enough to **augment** every call and **auto-handle** the easy 70%; not good enough to remove the human on the affectively-hard 30% — which is exactly where emotion reading matters most.

---

## 9. Build spec

**What to implement**
1. **Dual-path affect engine**: parallel always-on acoustic SER (emotion2vec/WavLM head, 300ms windows) + cascaded text-emotion (Indic STT → IndicBERT/MuRIL + BiLSTM) → late-fusion gating MLP → single **AffectState** object `{valence, arousal, label, confidence, slope, sarcasm_flag, distress_flag, lang/region}`.
2. **Speaker-relative normalizer** (eGeMAPS z-scoring over rolling window) feeding the acoustic head.
3. **Incongruence/sarcasm detector**: text-sentiment vs acoustic-valence disagreement + PCLM/DPO-trained speech-LLM turn-level pass.
4. **Trajectory tracker** (EMA + slope + hysteresis) emitting escalating/de-escalating/stable.
5. **Policy/threshold layer** → action tokens for the dialogue manager + HITL triggers (Section 7).
6. **Audit/consent layer** (Section 10) — log affect inferences as DPDP-sensitive, purpose-bound.

**Data needed**
- Proprietary **Hinglish + regional spontaneous call corpus**, real telephony (8kHz), with: (a) light perceived-emotion labels (≥3 annotators, report Fleiss κ — target >0.6), (b) **business-outcome labels** (churn/complaint/default/CSAT) as distant supervision, (c) sarcasm and masked-distress sub-sets. Bootstrap with IITKGP-SEHSC, EmoTa, EmoInHindi, MUStARD++, EMOVOME; **collect ≥50–100h real call audio per priority language** [estimate] for field-grade performance.

**Eval metric that gates ship**
- **Primary gate:** On a held-out set of *real* (not acted) Indian call segments, **macro-F1 ≥ 0.55 on the operational label set** AND **arousal/escalation detection recall ≥ 0.85** (catching agitation matters more than precision). [estimate]
- **Distress recall gate (safety-critical):** **recall ≥ 0.90** on the distress/vulnerability class on a curated hard set — false negatives here are the expensive, regulated failures. Precision can be lower (human reviews the flags).
- **Sarcasm gate:** measured separately; ship a *flag-for-human* mode until ≥0.60 on a Hinglish sarcasm set (matching VoxParadox-mitigated levels) before trusting it to drive tone autonomously.
- **Latency gate:** affect-state update **p95 < 300ms** from audio frame; turn-level speech-LLM nuance pass **< 1s**.
- **Calibration gate:** ECE < 0.1 so the confidence used for HITL gating is trustworthy.

---

## 10. India specifics

**Language / Hinglish**
- **Code-switching is the default**, not the exception — mid-sentence Hindi↔English flips break SER+ASR+langID jointly at switch boundaries. Models must be trained *on* code-mixed audio, not on Hindi and English separately. EmoInHindi (multi-label Hindi dialogue) + SemEval Hindi-English code-mixed emotion tasks are the closest public assets.
- **Regional prosody priors differ widely** — baseline loudness/rate for Punjabi/Bhojpuri/Tamil/Bengali speakers varies; speaker-relative normalization (micro-step 1) is *mandatory* in India, more than in Western deployments. **In-group advantage** is documented — Indian-expressed emotion is best recognized by Indian-trained models. [sourced]
- **Politeness register masks affect** — "ji", honorifics, indir'ectness mean Indian callers often *suppress* anger behind formality; the masked-distress head matters more here than in Western corpora. [analysis]
- **Festival/seasonal + telephony reality** — noisy backgrounds (family, street, TV), 8kHz narrowband, shared phones. Train and eval on degraded audio.

**Regulatory (this is a live constraint, not a footnote)**
- **DPDP Act 2023 (India):** inferred emotional state from voice is **personal data**, plausibly drawing on biometric/voice characteristics → requires **purpose limitation, consent/notice, and data-minimization**. Logging affect inferences without a stated purpose and consent is a DPDP exposure. Treat the AffectState log as sensitive, purpose-bound, retention-limited.
- **EU AI Act precedent (relevant if any EU client/data):** from **Feb 2, 2025, emotion inference from biometric data in workplace/education is *prohibited*** (Art. 5(1)(f)); raised-voice/basic expressions are out of scope, but *inferring deeper emotion* is in. [sourced] A BPO serving EU customers, or inferring *agent* emotion for monitoring, can cross this line. **Do not deploy agent-monitoring emotion detection on staff.**
- **RBI fair-practice (collections):** acting on detected distress to *intensify* a recovery push is a fair-practice/harassment risk. The compliant design uses distress detection to **de-escalate and route to human**, never to pressure. Bake this into the policy layer.
- **IRDAI (insurance):** misreading distress/urgency in a claims or mis-selling context has consumer-protection consequences; distress → slow down + human, never up-sell.

**Net India design rule:** detect emotion to **protect and route**, not to **exploit or surveil**. That single principle keeps you on the right side of DPDP, RBI, IRDAI, and EU-AI-Act spillover simultaneously.

---

## Sources

- [VoxEmo: Benchmarking SER with Speech LLMs (arXiv 2603.08936)](https://arxiv.org/html/2603.08936)
- [VoxParadox — adversarial paralinguistic benchmark (ICML 2026)](https://voxparadox.github.io/)
- [Wav2vec2.0 + NCDE SER, IEMOCAP 73.37% WA (PLOS One 2025)](https://journals.plos.org/plosone/article?id=10.1371%2Fjournal.pone.0318297)
- [wav2vec2 + ConLearnNet SER (MDPI Electronics)](https://www.mdpi.com/2079-9292/13/6/1103)
- [EMOVOME real-life spontaneous speech dataset (arXiv 2403.02167)](https://arxiv.org/html/2403.02167v3)
- [Intelligent emotion sensing BERT-BiLSTM <200ms (Nature Sci Reports s41598-025-15501-y)](https://www.nature.com/articles/s41598-025-15501-y)
- [Haptik — real-time sentiment in voice AI](https://www.haptik.ai/blog/voice-ai-real-time-sentiment-analysis)
- [Haloocom — real-time sentiment omnichannel 2026](https://connect.haloocom.com/blog/real-time-sentiment-analysis-in-omnichannel-platforms)
- [Gnani — real-time sentiment detection in voice AI](https://www.gnani.ai/resources/blogs/how-real-time-sentiment-detection-works-in-voice-ai)
- [Sarvam — Indian-language TTS/conversational agents](https://www.sarvam.ai/products/conversational-agents)
- [Caller.digital — Top voice AI agents India 2026](https://caller.digital/blog/top-10-voice-ai-agents-india-2026)
- [EmoTa: Tamil emotional speech dataset (ACL 2025)](https://aclanthology.org/2025.chipsal-1.19.pdf)
- [IITKGP-SEHSC Hindi emotion corpus](https://www.researchgate.net/publication/241181292_IITKGP-SEHSC_Hindi_Speech_Corpus_for_Emotion_Analysis)
- [MUStARD multimodal sarcasm benchmark (arXiv 2310.01430)](https://arxiv.org/abs/2310.01430)
- [Cross-cultural in-group advantage in vocal emotion (PMC3595515)](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3595515/)
- [EU AI Act emotion-recognition workplace prohibition](https://fpf.org/blog/red-lines-under-eu-ai-act-unpacking-the-prohibition-of-emotion-recognition-in-the-workplace-and-education-institutions/)
- [Inworld — best speech-to-speech APIs 2026 latency](https://inworld.ai/resources/best-speech-to-speech-apis)
- [AssemblyAI — voice AI stack for agents 2026](https://www.assemblyai.com/blog/the-voice-ai-stack-for-building-agents)

*Draft research dossier for review. Cited where possible; [estimate]/[analysis] elsewhere. Not investment advice.*
