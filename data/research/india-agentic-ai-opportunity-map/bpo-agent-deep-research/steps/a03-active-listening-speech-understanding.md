# Step A03 — Active Listening & Understanding Messy Real Speech
### (mumbling, background noise, talk-over) — India multilingual BPO voice agent

**Scope:** This dossier covers ONLY the perception layer — turning messy, real-world Indian-customer audio into a clean, correctly-segmented, correctly-attributed, correctly-understood representation of *what the caller actually means*, in real time, before any reasoning/intent/action happens. It explicitly stops at "agent has a reliable understanding of the utterance"; intent classification, dialog policy, and action-taking are downstream steps.

**Why this step is the hardest perception problem in the Indian BPO stack:** Indian telephony audio is typically **8 kHz, heavily compressed, with non-stationary background noise** (TV, family, traffic, street vendors, fans), **dense Hindi↔English code-switching mid-sentence**, **30+ regional accents**, frequent **talk-over / barge-in**, and high disfluency (false starts, "haan haan", "matlab", "woh kya hai na"). Global ASR stacks trained on clean US/EU studio audio collapse here. This is the single biggest quality lever in the whole agent.

---

## 1. Human micro-steps (what a skilled human agent ACTUALLY does)

A good Indian contact-center agent does all of this in ~200–300 ms, sub-consciously and continuously:

1. **Acoustic gain & focus** — mentally "turns up" the caller's voice and suppresses the TV/family/street noise behind them (auditory stream segregation / cocktail-party effect).
2. **Speaker tracking** — locks onto *the customer's* voice even when a family member talks in the background or grabs the phone ("ek minute, mummy se baat karwati hoon").
3. **Phoneme repair under degradation** — fills in muffled/clipped syllables from context ("...rance policy" → "insurance policy") even when the audio literally dropped.
4. **Code-switch parsing** — parses "mera EMI ka due date kya hai, woh bounce ho gaya tha last month" as one coherent thought, not two broken language fragments.
5. **Accent normalization** — maps a Bhojpuri/Tamil/Bengali-accented "vaarjan" → "version", "phipty" → "fifty", "skeem" → "scheme" on the fly.
6. **Disfluency stripping** — discards "haan woh, matlab, kya bolun, actually..." and keeps the propositional content.
7. **Number/entity capture under stress** — locks a 16-digit card number / policy number / OTP / amount spoken fast and noisily, often asking for a repeat of *only* the doubtful digits ("4-3-2... sorry last 3 again?").
8. **Endpoint / turn-end judgment** — decides whether the caller has *finished their thought* or is just pausing to recall a number — and crucially does NOT interrupt a thinking pause.
9. **Barge-in handling** — stops talking instantly when the customer cuts in, and re-routes attention to what the customer now says.
10. **Talk-over disambiguation** — when both speak at once, decides whose content matters and either yields or politely reclaims the floor.
11. **Prosody/emotion read** — hears irritation, panic, confusion, sarcasm in *how* it's said, not just the words — adjusting interpretation ("theek hai" said flatly ≠ agreement).
12. **Confidence + repair decision** — knows *when it didn't catch something* and surgically asks for a targeted repeat instead of a blanket "sorry, come again?".
13. **Context-carry** — remembers what was said 3 turns ago to disambiguate a pronoun or a half-spoken reference now.
14. **Silence/hold tolerance** — interprets a long silence correctly (caller fetching the card vs. call dropped vs. caller annoyed and waiting).

The deep insight: **a human does perception + light reasoning + emotional read as one fused act.** The agent must split these into a pipeline yet recombine fast enough that it *feels* fused.

---

## 2. Agent approach (per sub-step, named techniques — 2026 SOTA)

| Human sub-step | 2026 agent technique |
|---|---|
| 1. Acoustic gain/noise suppression | **Neural speech-enhancement front-end**: DeepFilterNet3 (self-host) or **Krisp** (cloud) as a pre-ASR denoise stage. Adding a neural suppressor drops WER **20–40% relative** on noisy input ([sourced — forasoft 2026]). |
| 2. Speaker tracking | **Telephony dual-channel separation** (caller on its own RTP channel = perfect separation, zero diarization cost) + **target-speaker diarization** with augmented speaker-embedding sampling for single-channel cases. AssemblyAI streaming diarization (public beta, $0.06/hr) for live single-channel. |
| 3. Phoneme repair | **End-to-end Indic-weighted ASR** (Sarvam Saaras v3) that learned Indian phonotactics from scratch — not a bolt-on; plus **LLM generative error correction (GenSEC / H2T mapping)** over N-best hypotheses as a post-pass. |
| 4. Code-switch parsing | **Code-switch-aware E2E ASR** — single-pass model with a code-switch LM that does NOT enforce one-language-per-phrase. E2E intra-sentential handling cuts boundary WER up to **55%** vs. LID-routing pipelines ([sourced — Gladia 2026]). |
| 5. Accent normalization | Indic-first acoustic model + **LoRA fine-tune on accent-stratified call data** + GenEC rare-word correction with phonetic context. |
| 6. Disfluency stripping | ASR with disfluency-aware decoding; **LLM cleanup pass** that normalizes "matlab/woh kya hai na" out while preserving meaning. |
| 7. Number/entity capture | **Contextual biasing / hotword boosting** (retrieval + RL-tuned hotword injection into LLM-ASR) for policy/card formats; **inverse text normalization** for digit grouping; **targeted re-prompt** logic driven by per-token confidence. |
| 8. Turn-end judgment | **Semantic VAD / model-based endpointing**: Pipecat **smart-turn-v3** (waveform-native, multilingual incl. Hindi, Dec 2025) or **LiveKit Turn Detector v1** (audio+LLM, captures *how* it's said). Closes the gap to **~300 ms** vs. naive 800–1500 ms VAD-silence ([sourced — futureagi/LiveKit 2026]). |
| 9. Barge-in | Keep turn-detection layer hot **during** TTS playback; on detected user onset → cancel TTS stream, hand control to STT. Target **<200 ms** suppression latency. LiveKit Agents v1.5+ ships adaptive interruption (86% precision / 100% recall). |
| 10. Talk-over disambiguation | Multi-talker streaming ASR with **speaker-agnostic activity streams**; decoupled separation→recognition; policy decides yield-vs-reclaim. |
| 11. Prosody/emotion read | **Paralinguistic / SER head** on the audio encoder (emotion, arousal, irritation) running parallel to ASR; fed as a side-signal to the dialog policy. |
| 12. Confidence + repair | **Per-token ASR confidence** + entity-slot confidence thresholds → trigger **surgical re-prompt** ("aapne kaha 4-3-2... last 3 digits dobara bata dijiye"). |
| 13. Context-carry | Streaming transcript + rolling dialog state in the LLM context window; pronoun/reference resolution by the orchestrator LLM. |
| 14. Silence/hold tolerance | VAD silence-duration classifier + call-progress signals (RTP keep-alive) → distinguish thinking-pause vs. fetch-pause vs. dropped call. |

**Architecture pattern (2026 default):** real-time streaming pipeline orchestrated by **Pipecat v1.0** or **LiveKit Agents**, stages = `[denoise] → [VAD/semantic-turn] → [streaming ASR + contextual biasing] → [GenSEC LLM correction] → [parallel SER head] → dialog`. This is the "real-time" architecture (vs. turn-based), chosen because BPO calls demand sub-second, interruptible interaction.

---

## 3. Tooling (concrete 2026 stack)

**Orchestration / real-time transport**
- **Pipecat v1.0.0** (Apr 2026) or **LiveKit Agents v1.5+** — pipeline + barge-in + endpointing + preemptive generation built-in.
- **FastRTC** for lightweight transport; SIP/RTP bridge for telephony (Plivo/Exotel/Twilio India / Knowlarity).

**Speech enhancement (front-end)**
- Self-host: **DeepFilterNet3** (real-time, 80–120 ms min frame).
- Cloud: **Krisp** noise + voice-cancellation.

**ASR (the core)**
- **India-first (recommended primary): Sarvam Saaras v3** — Indic-from-scratch, handles 8 kHz + noise + multi-speaker, streaming WebSocket, **median <100–250 ms latency**, **₹1.5/min**, 10+ Indian languages. 19.31% WER on IndicVoices 10-lang; beats GPT-4o-Transcribe / Gemini 3 Pro / Deepgram Nova-3 / Scribe v2 on Indian accuracy ([sourced — Sarvam 2026]).
- **Alt/fallback: Deepgram Nova-3** (+ keyterm biasing) for cloud English-heavy; **Gladia Solaria-1** (94%+ accuracy, 100 langs, ~270 ms, telephony-optimized, code-switch native).
- **Self-host alt:** Whisper Large-v3 Turbo + DeepFilterNet + **LoRA fine-tune** on Indian call data.

**Turn detection / endpointing**
- **pipecat-ai/smart-turn-v3** (HF, open-source, waveform-native, multilingual incl. HI) or **LiveKit Turn Detector v1** (audio+LLM).

**Diarization (single-channel cases)**
- **AssemblyAI streaming diarization** (beta, $0.06/hr) or pyannote-based target-speaker diarization. *Prefer telephony dual-channel to avoid this entirely.*

**Contextual biasing / entity capture**
- LLM-ASR with **hotword retrieval + RL reward** (arXiv 2512.21828) or retraining-free **WCTC-Biasing** for CTC models. Per-domain hotword lists (product names, policy formats, branch names).

**Post-ASR correction**
- **GenSEC** LLM pass (N-best → single corrected hypothesis); **H2T LoRA adapter** for code-switch; FlanEC/T5-style rescoring.

**Emotion / paralinguistics**
- SER head (wav2vec2/whisper-encoder based) for arousal/irritation side-signal.

**Eval / observability**
- **Hamming AI** voice-agent eval, **Pipecat eval harness**; track WER, entity-error-rate, turn-detection F1, barge-in precision/recall, end-to-end latency.

---

## 4. Benchmarks (real numbers)

| Metric | Number | Source/tag |
|---|---|---|
| Hindi WER, India-first model from scratch | **8–10%** | [sourced — caller.digital / nextlevel 2026] |
| Hindi WER, fine-tuned Whisper-v3 on 500–1k hrs Indian data | **14–16%** (from ~22% base) | [sourced — caller.digital 2026] |
| Sarvam Saaras-class WER, IndicVoices 10-lang | **19.31%** | [sourced — Sarvam 2026] |
| Hindi WER achievable in production worst-case | **<12%** | [sourced — caller.digital 2026] |
| WER reduction from neural noise suppressor | **20–40% relative** | [sourced — forasoft 2026] |
| Code-switch boundary WER reduction, E2E vs LID-pipeline | **up to 55%** | [sourced — Gladia 2026] |
| Streaming ASR latency (Sarvam) | **<100–250 ms median** | [sourced — Sarvam 2026] |
| Streaming ASR latency (Gladia Solaria) | **~270 ms** | [sourced — Gladia 2026] |
| Semantic turn-detection latency vs naive VAD | **~300 ms** vs 800–1500 ms | [sourced — futureagi/LiveKit 2026] |
| Barge-in suppression latency target | **<200 ms** | [sourced — futureagi 2026] |
| Barge-in accuracy target / LiveKit adaptive | **95%+ target; 86% precision / 100% recall** | [sourced — LiveKit 2026] |
| Diarization improvement in noise (AssemblyAI) | **+30%** | [sourced — AssemblyAI 2026] |
| Diarization degradation onset | overlap / **>6–8 simultaneous speakers** | [sourced — AssemblyAI 2026] |
| Realistic end-to-end voice latency target | **<1 s** | [sourced — softcery/dev.to 2026] |
| Entity (16-digit card/policy) capture under noise | no clean public India benchmark | **[estimate]** ~92–96% with biasing + targeted re-prompt |

---

## 5. Failure modes (where the agent breaks)

1. **Dense intra-word code-switch + accent** — "isko activate karwana hai par OTP aa nahi raha" with a Telugu accent on 8 kHz: ASR drops "activate"/"OTP", GenEC mis-corrects.
2. **Talk-over / >2 active speakers** — accuracy collapses on overlap and beyond 6–8 speakers; single-channel diarization mis-attributes the family member's voice to the customer.
3. **Fast noisy digit strings** — a 16-digit card or policy number spoken quickly over TV noise: one wrong digit = wrong account = compliance incident. The agent often doesn't *know* it got it wrong.
4. **Thinking-pause = false endpoint** — caller pauses to read a number off a card; naive/over-eager turn detector cuts them off → frustration, re-tries.
5. **Prosody blindness** — flat "haan theek hai" (resigned, not consenting) read as consent → wrong action; sarcasm/irony missed entirely.
6. **Regional code-switch into low-resource language** — sudden switch to Bhojpuri/Maithili/Marwari mid-Hindi degrades to gibberish.
7. **Domain proper nouns** — scheme names, branch names, product SKUs ("Sukanya Samriddhi", "Smart Term Plus") not in vocabulary → mangled without hotword biasing.
8. **Denoiser over-suppression** — aggressive enhancement clips real speech (especially soft/elderly/female voices), *creating* errors.
9. **Cascading error** — denoise error → ASR error → GenEC "confidently corrects" to a plausible-but-wrong utterance → downstream acts on a hallucinated request.
10. **Channel/codec variability** — VoLTE vs landline vs OTT (WhatsApp call) vs IVR transfer change the acoustic profile mid-call.

---

## 6. Gap to full adaptation (what the agent STILL can't do as well as a human — and the path to close it)

| Residual gap vs. human | Why it persists | Concrete engineering/data path to close |
|---|---|---|
| **Knowing it didn't hear correctly** (human's metacognitive "I missed that") | ASR confidence is poorly calibrated on noisy code-switch; the model is most wrong exactly when overconfident | Train a **calibrated confidence/uncertainty head** on noisy Indian call data; gate entity slots on calibrated confidence; route low-confidence to surgical re-prompt. Eval = ECE (expected calibration error) on held-out noisy calls. |
| **Cocktail-party separation as well as a human ear** | Single-channel separation still breaks on heavy overlap/family handoff | **Force telephony dual-channel** wherever possible; for single-channel, fine-tune target-speaker extraction on Indian household-noise data (TV/kids/kitchen). |
| **Prosody → meaning fusion** (resigned vs. willing "haan") | SER is a side-signal, not fused with semantics | **Joint audio-text dialog model** that conditions intent on prosody; collect India-labeled prosody-intent pairs (consent-vs-resignation). |
| **Low-resource regional switch** (Bhojpuri/Maithili/Marwari) | Data scarcity | Targeted data collection + LoRA per regional dialect; synthetic code-switch augmentation with phonetic context. |
| **Disfluency repair that preserves customer intent exactly** | LLM cleanup can drop meaningful hedges | GenEC tuned with a reward that penalizes meaning-loss, not just WER. |
| **Graceful repair UX** (asking for ONLY the doubtful digits, like a human) | Most stacks blanket "sorry, repeat that" | Build a **per-token-confidence-driven targeted re-prompt** policy: re-ask only the low-confidence span. This is a *huge* perceived-quality win and is buildable today. |

**Boss's core question — can the agent fully adapt to the human here?** For clean-to-moderate audio: yes, already near-parity. The remaining 10–15% gap is concentrated in (a) **noisy fast entity capture with self-aware repair**, (b) **prosody-meaning fusion**, and (c) **heavy overlap/regional-switch**. The fastest, highest-ROI closes are **dual-channel telephony + calibrated confidence + surgical re-prompt + domain hotword biasing** — none require frontier research, all are 2026-shippable engineering.

---

## 7. HITL trigger (when a human MUST take over)

- **Repeated low-confidence on a critical entity** (card/policy/OTP/amount) after 2 targeted re-prompts → escalate to human (compliance + UX).
- **Sustained heavy overlap / multiple speakers** the agent cannot disambiguate.
- **Detected high distress/panic** (SER) on a sensitive (BFSI/insurance) call — RBI FPC requires a human-escalation path anyway.
- **Persistent code-switch into an unsupported regional language.**
- Otherwise: **the perception step itself is largely automatable**; HITL is for the *consequences* of perception failure on high-stakes slots, not routine listening.

---

## 8. Automation readiness: **7 / 10**

Justification: Streaming Indic ASR + semantic turn detection + denoise + barge-in are **production-grade today** for Hindi/Hinglish on the common case (caller in moderate noise, dual-channel). Sarvam-class models hit 8–12% Hindi WER and sub-300 ms latency. The −3 reflects the unsolved tail: **fast noisy entity capture with self-aware repair, heavy overlap, prosody-meaning fusion, and low-resource regional switching** — where humans still clearly win and a wrong digit is a compliance event. Not a 9–10 because in BFSI the cost of a silent mis-hear is high; not below 7 because the common case is genuinely solved.

---

## 9. Build spec (what to implement + data + eval gate)

**Implement (MVP perception stack):**
1. Telephony bridge with **dual-channel separation** (caller isolated) — non-negotiable first lever.
2. **DeepFilterNet3** denoise front-end (toggle, with over-suppression guard for soft voices).
3. **Sarvam Saaras v3 streaming** as primary ASR; Deepgram Nova-3 fallback router.
4. **smart-turn-v3** semantic endpointing + **barge-in** (cancel TTS on user onset).
5. **Contextual biasing** with per-tenant hotword lists (product/scheme/branch names, policy/card regex formats) + **ITN** for digit grouping.
6. **GenSEC LLM correction** pass over N-best, tuned to preserve meaning.
7. **Calibrated per-token + per-slot confidence** → **surgical targeted re-prompt** policy.
8. Parallel **SER head** emitting irritation/distress side-signal to dialog policy.

**Data needed:**
- 500–1,000+ hrs **real Indian call-center audio** (8 kHz, consented), accent-stratified (≥10 states), with Hinglish code-switch transcripts.
- Household-noise corpus (TV/kids/kitchen/traffic) for noise-robustness + denoiser tuning.
- Labeled **entity-capture set** (card/policy/OTP/amount under noise) for slot-error-rate.
- **Prosody-intent pairs** (consent vs. resignation vs. distress) for SER fusion.

**Eval metrics that gate ship:**
- **WER ≤ 12%** on held-out noisy Hindi/Hinglish (ship gate); ≤ 10% target.
- **Entity Error Rate ≤ 2%** on critical slots after re-prompt (the real compliance gate).
- **Turn-detection F1 ≥ 0.9** and **median end-to-end latency < 1 s**, ASR latency < 300 ms.
- **Barge-in precision ≥ 95% / recall ≥ 95%.**
- **Confidence calibration: ECE ≤ 0.05** on entity slots (so the agent *knows* when to re-ask).
- **Diarization error rate** acceptable only documented; prefer dual-channel to sidestep.

---

## 10. India specifics (Hinglish / regional / regulatory)

**Linguistic**
- **Hinglish intra-sentential code-switch is the norm, not the exception** — model MUST be code-switch-native (single-pass, no LID routing). Use Indic-from-scratch (Sarvam) over fine-tuned global models (8–10% vs 14–16% Hindi WER).
- **30+ accents**; Tamil/Telugu/Bengali/Marathi each shift phonetics — accent-stratified data + per-dialect LoRA.
- **8 kHz telephony + household noise** is the default acoustic condition; tune the denoiser and ASR for it, not for studio audio.
- **Number reading varies** ("do hazaar paanch sau" vs "twenty-five hundred") — robust ITN for Indian number conventions.

**Regulatory (gates the perception stack's data handling)**
- **DPDP Act 2025/Rules** — substantive obligations effective ~**May 13, 2027**; need **explicit informed consent** to process the voice recording, transcript, sentiment tag, CRM entry. Penalties up to **₹250 crore**. Build consent capture + purpose limitation + erasure into the audio pipeline now.
- **TRAI DLT** — principal-entity/header/template registration + DND scrubbing for outbound.
- **RBI FPC** (fintech/BFSI) — mandatory **human-escalation option** → reinforces the HITL trigger above.
- **IRDAI** norms for insurance AI calling.
- **AI disclosure** — must disclose AI + recording at call start.
- **PII redaction** — transcripts contain card/Aadhaar/policy numbers → **real-time PII redaction** in the transcript store; retention only as long as RBI/IRDAI/IT-Act require, then erase.
- **Data localization / sovereign compute** — prefer India-hosted ASR (Sarvam runs on sovereign compute) to ease localization and DPDP compliance vs. routing audio to US-hosted global ASR.

---

## Sources
- [Gladia — Code Switching in Speech Recognition (2026)](https://www.gladia.io/blog/what-is-code-switching-in-speech-recognition)
- [Caller Digital — Voice AI WER Benchmarks Indian Languages 2026](https://caller.digital/blog/voice-ai-wer-benchmarks-indian-languages-hindi-tamil-telugu-bengali-marathi-2026)
- [Caller Digital — Voice AI for India vs Global Platforms 2026](https://www.caller.digital/blog/voice-ai-india-vs-global-platforms)
- [Caller Digital — DPDP vs TRAI Consent for Voice Recordings 2026](https://www.caller.digital/blog/dpdp-vs-trai-consent-voice-recordings-audit-trail-india-2026)
- [Softcery — Real-Time vs Turn-Based Voice Agents 2026](https://softcery.com/lab/ai-voice-agents-real-time-vs-turn-based-tts-stt-architecture)
- [FutureAGI — Voice AI Barge-In and Turn-Taking 2026](https://futureagi.com/blog/voice-ai-barge-in-turn-taking-2026/)
- [LiveKit — Turn Detection for Voice Agents](https://livekit.com/blog/turn-detection-voice-agents-vad-endpointing-model-based-detection)
- [LiveKit — Solving end-of-turn detection: Turn Detector v1.0](https://livekit.com/blog/solving-end-of-turn-detection)
- [Pipecat smart-turn-v3 (Hugging Face)](https://huggingface.co/pipecat-ai/smart-turn-v3)
- [Daily — Smart Turn v2 open-source semantic VAD](https://www.daily.co/blog/smart-turn-v2-faster-inference-and-13-new-languages-for-voice-ai/)
- [Sarvam — Speech to Text](https://www.sarvam.ai/speech-to-text) · [Sarvam Streaming STT API](https://docs.sarvam.ai/api-reference-docs/api-guides-tutorials/speech-to-text/streaming-api)
- [NextLevel — Best Speech to Text Models 2026](https://nextlevel.ai/best-speech-to-text-models/)
- [Forasoft — Speech Recognition Accuracy in Noisy Environments 2026](https://www.forasoft.com/blog/article/speech-recognition-accuracy-noisy-environments)
- [NoiseReducerAI — DeepFilterNet vs RNNoise](https://noisereducerai.com/blogs/deepfilternet-ai-noise-reduction/)
- [AssemblyAI — Top Speaker Diarization Libraries & APIs 2026](https://www.assemblyai.com/blog/top-speaker-diarization-libraries-and-apis)
- [arXiv 2512.21828 — Contextual Biasing for LLM-Based ASR with Hotword Retrieval + RL](https://arxiv.org/abs/2512.21828)
- [arXiv 2510.03630 — Scaling Multi-Talker ASR with Speaker-Agnostic Activity Streams](https://arxiv.org/pdf/2510.03630)
- [arXiv 2310.13013 — Generative error correction for code-switching ASR using LLMs](https://arxiv.org/abs/2310.13013)
- [arXiv 2508.04721 — Low-Latency End-to-End Voice Agents for Telecom](https://arxiv.org/html/2508.04721v1)
- [Hamming AI — How to Evaluate Voice Agents 2026](https://hamming.ai/resources/how-to-evaluate-voice-agents-2026)
- [Auto Interview AI — AI Calling Compliance India 2026 (DPDP/TRAI/RBI)](https://www.autointerviewai.com/blog/ai-calling-india-dpdp-trai-dlt-compliance-complete-guide-2026)

---
*Draft research dossier for review. Cited where possible; [estimate] elsewhere. Not investment advice.*
