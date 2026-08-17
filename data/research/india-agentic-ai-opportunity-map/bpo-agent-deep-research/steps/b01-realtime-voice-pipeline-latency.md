# B01 — Real-Time Voice Pipeline & Latency Engineering

> Micro-step deep-dive: **Sub-700ms end-to-end turn, barge-in detection, VAD, and turn-taking**
> Context: India-market, multilingual (Hindi + regional + Hinglish), RBI/IRDAI/DPDP-compliant, action-taking BPO contact-center agent
> Research date: 2026-06-24
> Scope: THIS STEP ONLY — from caller audio-in to agent audio-out, one turn.

---

## 1. What a Skilled Human Agent Actually Does (Atomic Micro-Steps)

A trained BPO agent performing a single conversational turn executes far more than "listen and respond." Breaking it to the smallest atoms:

### 1.1 Pre-Speech Signal Detection
- **Passive auditory monitoring** — maintains open-ear attention even while speaking or on hold; detects when background noise pattern shifts to foreground voice
- **Channel quality assessment** — instantaneously registers call quality (mobile vs landline, VOIP artifacts, echo) and mentally adjusts comprehension confidence
- **Caller-state reading** — from first phoneme, begins reading emotional valence (angry, confused, distracted), language variant (Hindi, Hinglish, regional accent), and speech rate

### 1.2 Turn-Yielding Signal Processing
- **Prosodic cue recognition** — detects falling intonation (declarative end), rising intonation (question), trailing-off or "um/haan" (continuation marker)
- **Syntactic completeness sensing** — unconsciously parses whether the sentence has a verb, subject, and conclusion; does not wait for silence if semantic content is clearly complete
- **Pause duration calibration** — distinguishes: (a) within-clause breath pause ~150ms, (b) hesitation/filler ~400ms, (c) genuine turn end ~600ms+; this calibration is language-specific (Hindi has different pause norms than English)
- **Back-channel monitoring** — decides whether caller's "haan haan" or "theek hai" signals agreement-and-continue or genuine end-of-turn
- **Silence triangulation** — confirms silence is not phone muting, network dropout, or hold music

### 1.3 Barge-In and Interruption Handling
- **Simultaneous listen-while-speak** — during own speech, agent maintains auditory attention stream; can catch caller's attempted interruption from first syllable
- **Interrupt intent classification** — instantly judges: (a) genuine redirect (must yield), (b) agreement backfill ("haan," "okay" mid-speech = ignore/continue), (c) emotional outburst (yield + de-escalate), (d) confusion signal (yield + rephrase)
- **Clean yield execution** — when yielding, cuts own speech at a semantic boundary (not mid-word), creates smooth handoff
- **Echo suppression** — mentally filters out own voice bouncing back through the phone line and discounts it from speech detection

### 1.4 Speech Decoding (ASR equivalent)
- **Code-switch decoding** — simultaneously decodes Hindi + English words appearing in the same utterance without cognitive switching cost ("mera account blocked hai, please unblock karo")
- **Telephony audio compensation** — compensates for 8kHz narrow-band audio, compression artifacts, packet loss gaps
- **Domain vocabulary bias** — automatically applies a "prior" toward domain vocabulary (account numbers, product names, policy terms) when decoding ambiguous phonemes
- **Number normalization** — converts spoken "two-two-seven" to 227, "double-seven" to 77 etc., instantly
- **Name and entity recognition** — flags named entities (customer name, city, product) for action

### 1.5 Processing / Response Generation (LLM equivalent)
- **Working memory maintenance** — holds call context (past 5-10 turns), CRM data just retrieved, current problem state
- **Intent resolution** — from decoded text, determines caller's request type (query/complaint/escalation request/payment)
- **Response planning** — selects response strategy from trained script + situation; adds empathy markers appropriate to language register
- **Language register matching** — mirrors caller's formality level (formal Hindi vs casual Hinglish vs regional mix)

### 1.6 Speech Production (TTS equivalent)
- **Prosody selection** — chooses pace, pitch, and emphasis appropriate to content and caller state
- **Fluency management** — avoids unnatural pauses; uses filler ("ek second hold kariye") when fetching system info
- **Breath + pause control** — places natural pauses at clause boundaries; never a dead silence >300ms without filler
- **Volume calibration** — adjusts to caller's volume and background noise level

### 1.7 Concurrency / Parallelism
- **Simultaneous actions** — while speaking, agent is already navigating CRM, reading next script point, typing case notes; this is "full duplex cognition"
- **Interrupt readiness** — maintains split-attention throughout; can drop current output stream and switch to input mode within ~100ms

---

## 2. Agent Approach: How a 2026 AI System Does Each Sub-Step

### 2.1 Pre-Speech Signal Detection

**Technique:** Continuous streaming VAD on 20ms audio frames.

- **Model:** Silero VAD v5 (open-source, 1.8MB, PyTorch, 6ms/frame on CPU) or Picovoice Cobra VAD (C SDK, 1.8ms/frame, 0.05% CPU) for resource-constrained edge deployments.
- **Input:** Raw PCM at 8000Hz (telephony) or 16000Hz (WebRTC); pre-processed with WebRTC AEC (Acoustic Echo Cancellation) to remove agent's own output from the input stream before VAD sees it.
- **Output:** Binary speech/non-speech classification per frame + confidence score 0-1.
- **Channel quality:** Measured via SNR estimator (RNNoise or DTLN). If SNR drops below threshold, ASR confidence is flagged as unreliable → escalation signal raised.

**Framework:** Pipecat v1.0 (Daily.co, Apr 2026) or LiveKit Agents SDK v1.5.6. Both natively integrate Silero VAD and run it on every audio frame before STT.

### 2.2 Turn-Yielding Signal Processing

This is the hardest sub-step to automate and the biggest latency driver.

**Three-tier architecture (2026 production standard):**

**Tier 1 — Acoustic VAD (fast, noisy):**
- Silero/Cobra detects speech vs silence in real time.
- 500ms silence triggers a "candidate end-of-turn" signal.
- Problem: adds 500ms latency as a structural minimum; can't detect semantically complete short utterances without silence.

**Tier 2 — STT Endpointing (medium, more accurate):**
- Deepgram Nova-3 or AssemblyAI Universal-2 runs streaming ASR on the audio.
- Their own endpointing model watches partial transcript tokens and predicts utterance boundary from STT-internal signals.
- Fires 100-200ms faster than silence-based endpointing.
- Deepgram median first-transcript latency: 180ms [sourced: picovoice.ai benchmarks].

**Tier 3 — Semantic End-of-Turn (slowest, most accurate):**
- LiveKit's open-source EOU (End of Utterance) model — 135M parameter SmolLM v2-based transformer fine-tuned on conversational data.
- Reads partial transcript in real-time; predicts whether user is semantically done based on syntactic completeness.
- Can fire BEFORE trailing silence, saving 200-400ms vs silence-only approach.
- False positive risk on mid-sentence pauses; requires tuning.

**Production pattern:** All three tiers run in parallel; first confident signal wins. LiveKit calls this "adaptive endpointing" and reports 86% precision / 100% recall on interruption events [sourced: LiveKit Agents v1.5.6 release notes].

**Prosodic/back-channel handling (gap in 2026 SOTA):** No production system reliably handles back-channel ("haan haan") as non-turn-end. Most systems falsely treat it as a turn yield. Partial workaround: duration gates (< 300ms utterance → back-channel candidate → suppress end-of-turn signal).

### 2.3 Barge-In and Interruption Handling

**Architecture:** Requires true full-duplex audio with echo cancellation as a prerequisite.

**Step-by-step flow:**
1. **Echo cancellation first:** WebRTC AEC subtracts the known playback audio (TTS output) from the microphone input. Without this, VAD triggers on the agent's own voice → phantom barge-in loop.
2. **Parallel VAD during TTS playback:** VAD continues running on the AEC-filtered input even while TTS audio is streaming out.
3. **Barge-in trigger:** VAD confidence > threshold for > minimum duration (typically 100ms) → "barge-in candidate."
4. **Interrupt classifier:** A lightweight classifier (binary: genuine interrupt vs. agreement backfill) runs on partial transcript. Models: small distilled BERT or even regex on "haan/okay/theek" to suppress.
5. **TTS cancel:** If genuine interrupt confirmed, TTS output is stopped at the next audio chunk boundary (< 20ms). LLM generation may also be cancelled (token-budget save).
6. **Fresh STT stream:** A new STT session is initiated from the barge-in audio.

**Barge-in detection latency target:** Under 150ms from caller voice start to TTS cancellation [sourced: smallest.ai production checklist].

**Framework support:** Pipecat v1.0 has native barge-in handler in its pipeline processor abstraction. LiveKit Agents SDK has TTS cancellation hooks. Both require AEC-capable telephony layer (Twilio Media Streams, Agora, or LiveKit WebRTC).

### 2.4 Speech Decoding (ASR)

**Model options for India/Hinglish:**

| Model | WER Hindi | WER Hinglish | Latency | Notes |
|---|---|---|---|---|
| Deepgram Nova-3 | ~11% | ~18% | 180ms median | Best global latency; Hinglish needs fine-tune |
| Sarvam AI STT | ~10% | ~16% | 200-300ms | Native Indic, 11 languages, strong code-switch |
| Whisper Large v3 | 14% | 22% | 400-600ms | Too slow for real-time without speculative decoding |
| Gnani Inya VoiceOS | ~10% | ~15% | < 300ms | India-specific, handles code-switch natively |
| AssemblyAI Universal-2 | 13% | 20% | 200ms | Good endpointing, weaker on Indic |

**Production recommendation for India BPO:** Sarvam AI STT as primary (Indic native), Deepgram Nova-3 as fallback (lower latency, weaker Indic). Route by caller language detection in first 2 seconds.

**Streaming:** Both emit partial transcripts every 50-80ms. LLM processing can begin on partial transcript once confidence threshold met.

**Domain vocabulary bias:** Both Deepgram and Sarvam allow custom vocabulary injection (hotwords / boost phrases). Load domain vocab (product names, policy IDs, customer-facing terms) at session start.

### 2.5 Processing / Response Generation

**Model selection for voice latency:**

Time-to-first-token (TTFT) dominates. Full response quality matters less; first audio byte must fire quickly.

| Model | TTFT | Voice Suitability | India Edge |
|---|---|---|---|
| GPT-4o-mini | ~400ms | High | Needs prompt for Hinglish |
| Gemini 2.5 Flash | ~400ms | High | Native multilingual |
| Claude 3.5 Haiku | ~360ms | High | Good instruction follow |
| GPT-4o / Realtime API | 300-500ms | Highest (native audio) | 70+ lang, no India TTS voices yet |
| Llama 3.3 70B (local) | Variable | Medium | Data sovereignty option |

**OpenAI Realtime API (GPT-Realtime-2):** Speech-to-speech model, eliminates STT→LLM→TTS serialization. TTFB 400-600ms in US regions; 600-900ms from India due to geography [estimate]. Pricing: $32/1M audio input + $64/1M audio output tokens (~$0.30/minute call).

**Streaming token pattern:** LLM streams tokens → TTS begins synthesis on first complete sentence (~15-20 tokens) → concurrent playback. This hides 60-70% of LLM inference latency from perceived caller experience.

**Response pre-computation:** For high-frequency turn patterns (greeting, hold filler, re-ask), pre-synthesize responses and cache audio. Eliminates latency for ~30% of turns in scripted BPO flows.

### 2.6 Speech Synthesis (TTS)

**India-specific TTS options:**

| Model | Languages | Latency (TTFB) | Quality | Notes |
|---|---|---|---|---|
| Smallest.ai Turbo | Hindi, En-IN | < 100ms | High | Best latency; voice cloning |
| Sarvam AI TTS | 11 Indic + En-IN | 250ms (streaming) | High | Natural prosody, 25+ voices |
| ElevenLabs v3 | Hindi (limited) | 100-200ms | Highest | Western voices primarily |
| Google Chirp 3 | Hindi, 3 regional | 150-300ms | High | GCP native, low egress cost in India |
| Azure Neural TTS | Hindi, Tamil, Telugu | 200-350ms | High | SSML support, custom voice |

**Streaming TTS:** Critical. TTS must emit first audio chunk after first sentence (not after full LLM response). Smallest.ai and Sarvam both support sentence-streaming mode.

**Filler injection:** While fetching CRM data or tool results, inject pre-synthesized filler: "Ek second, main check kar raha hu" → covers tool latency without silence.

### 2.7 Full Pipeline Orchestration

**Recommended 2026 production stack for India BPO:**

```
Telephony layer: Twilio Programmable Voice (SIP trunk) or Plivo (India-native)
  ↓ PCM audio at 8kHz, μ-law
WebRTC / PSTN bridge: LiveKit WebRTC (open-source, self-hosted India region)
  ↓ AEC + noise suppression (WebRTC stack)
VAD: Silero VAD (Pipecat-native) in parallel with STT endpointing
  ↓ Trigger signal
STT: Sarvam AI STT (primary) / Deepgram Nova-3 (fallback)
  ↓ Partial + final transcript streaming
Semantic EOU: LiveKit turn-detector (SmolLM EOU model)
  ↓ Confirmed end-of-turn signal
LLM: Claude 3.5 Haiku / Gemini 2.5 Flash (streaming, TTFT ~360-400ms)
  ↓ Streaming tokens → sentence detection
TTS: Smallest.ai Turbo / Sarvam TTS (sentence-level streaming)
  ↓ Audio chunks → playback
Barge-in loop: VAD on AEC output → interrupt signal → TTS cancel → fresh STT stream
```

**Framework:** Pipecat v1.0 (Python) or LiveKit Agents Python SDK. Both provide this entire pipeline as configurable processors; swap each stage independently.

---

## 3. Tooling (Concrete 2026 Stack)

### Frameworks
- **Pipecat v1.0** (Daily.co, open-source, Apr 2026) — frame-based pipeline, 68+ integrations, native VAD+barge-in
- **LiveKit Agents Python SDK v1.5.6** — adaptive interruption, preemptive generation, open-source WebRTC infra
- **Agora TEN Framework** — TEN VAD + TEN Turn Detection; strong Asia-Pacific infra

### STT
- **Deepgram Nova-3** — streaming, 36 languages, 180ms median latency, custom vocab
- **Sarvam AI STT API** — 11 Indic languages + Hinglish, code-switching native
- **Gnani Inya VoiceOS** — direct audio-to-audio for India market, sub-300ms
- **AssemblyAI Universal-2** — good endpointing, fallback option

### VAD
- **Silero VAD v5** — open-source, 6ms/frame, Python-native, 87.7% TPR at 5% FPR
- **Picovoice Cobra VAD** — commercial, 1.8ms/frame, 98.9% TPR, low CPU footprint
- **LiveKit turn-detector** — semantic EOU model (SmolLM-based, 135M params)

### LLM
- **Claude 3.5 Haiku** — 360ms TTFT, best instruction follow, Anthropic SDK streaming
- **Gemini 2.5 Flash** — 400ms TTFT, natively multilingual, low cost
- **OpenAI GPT-Realtime-2** — speech-to-speech, eliminates cascade latency (higher cost)

### TTS
- **Smallest.ai Turbo** — < 100ms TTFB, voice cloning, Hindi-native
- **Sarvam AI TTS** — 11 Indic languages, 250ms streaming, natural prosody
- **Google Chirp 3 HD** — Hindi + regional, GCP region in Mumbai (low latency)

### Telephony
- **Twilio Programmable Voice** — SIP trunking, DTMF, recording, global
- **Plivo** — India-native, ₹-denominated, TRAI compliant DLT integration
- **Exotel** — India BPO leader, DLT headers built-in, compliant

### Observability
- **Langfuse** (open-source) — trace every LLM call: prompt, output, latency, cost
- **Datadog** — infrastructure metrics (telephony jitter, packet loss, audio quality)
- **Custom JSONL latency logger** — timestamp every stage: `userSpeechEnd → vadTrigger → sttFinal → llmFirstToken → ttsFirstChunk → playbackStart`

### Echo Cancellation
- **WebRTC AEC** — built into browsers and LiveKit; handles most telephony echo
- **Speex DSP** — open-source, good for SIP deployments
- **Agora AI AEC** — DNN-based, handles residual echo after WebRTC AEC

---

## 4. Benchmarks

### End-to-End Latency
| Metric | Number | Source |
|---|---|---|
| Human conversational gap | 200-300ms | [estimate, linguistics research] |
| "Feels human" threshold | < 700ms | [sourced: retellai.com] |
| "Acceptable" threshold | < 1200ms | [sourced: hamming.ai] |
| "Conversation breakdown" | > 1500ms | [sourced: hamming.ai] |
| Retell AI P50 latency | 580-620ms | [sourced: retellai.com benchmark, 1200+ calls] |
| Vapi optimized latency | 500-600ms | [sourced: retellai.com benchmark] |
| Cascaded pipeline (unoptimized) | 1200-1800ms | [sourced: trillet.ai] |
| OpenAI Realtime API (US) | 400-600ms | [sourced: openai.com] |
| OpenAI Realtime API (India est.) | 600-900ms | [estimate, +150-250ms for Asia roundtrip] |

### Stage-Level Latency Budget (600ms target)
| Stage | Optimized | Typical | Source |
|---|---|---|---|
| Network + telephony | 30-80ms | 50-150ms | [sourced: retellai.com] |
| VAD + turn detection | 150-300ms | 250-500ms | [sourced: hamming.ai] |
| STT final transcript | 50-100ms | 100-200ms | [sourced: hamming.ai] |
| LLM TTFT | 150-400ms | 300-600ms | [sourced: hamming.ai] |
| TTS first audio byte | 40-100ms | 100-250ms | [sourced: smallest.ai, sarvam.ai] |
| **Total optimized** | **~620ms** | **~1200ms** | |

### VAD Accuracy
| Model | TPR @ 5% FPR | CPU (RTF) | Source |
|---|---|---|---|
| WebRTC VAD | 50% | < 0.001 | [sourced: picovoice.ai] |
| Silero VAD v5 | 87.7% | 0.00429 | [sourced: picovoice.ai] |
| Cobra VAD | 98.9% | 0.000399 | [sourced: picovoice.ai] |

### ASR WER — Hindi / Hinglish
| Model | Hindi WER | Hinglish WER | Source |
|---|---|---|---|
| Sarvam AI STT | ~10% | ~16% | [estimate based on Sarvam claims] |
| Deepgram Nova-3 | ~11% | ~18% | [sourced: callsphere.ai, forasoft.com] |
| Gnani Inya | ~10% | ~15% | [sourced: gnani.ai] |
| Whisper Large v3 | ~14% | ~22% | [estimate, gnani.ai comparison] |
| Global models (telephony) | 14-16% | 25-35% | [sourced: gnani.ai] |

### Barge-In
| Metric | Target | Achievable | Source |
|---|---|---|---|
| Time to detect barge-in | < 150ms | 100-200ms | [sourced: smallest.ai] |
| Time to cancel TTS | < 20ms | < 20ms (chunk boundary) | [estimate] |
| Barge-in precision (LiveKit) | 86% | 86% | [sourced: LiveKit v1.5.6 notes] |
| Barge-in recall (LiveKit) | 100% | 100% | [sourced: LiveKit v1.5.6 notes] |

---

## 5. Failure Modes

### 5.1 Premature Interruption (False Positive Barge-In)
**What happens:** Agent cuts off caller mid-thought on a breath pause or filler ("um... mera"). Caller re-states; agent interrupts again. Conversation breaks down.
**Why it happens:** VAD-only turn detection fires on any voice gap > silence threshold. Silence thresholds set too aggressively to reduce latency.
**Frequency:** Common when silence threshold < 400ms; endemic in rule-based VAD systems.

### 5.2 Zombie Agent (False Negative Barge-In)
**What happens:** Agent keeps speaking while caller is actively talking. Caller experiences being talked over by a bot. High frustration, drop-off.
**Why it happens:** Echo cancellation failure — agent's own TTS audio bleeds into microphone, VAD classifies it as speech, suppresses barge-in detection.
**When it occurs:** VoIP calls with high echo; mobile calls on speakerphone; network jitter causing AEC reference signal to desync.

### 5.3 Turn-Yield False Positive (Back-Channel as Turn-End)
**What happens:** Caller says "haan, haan" (agreement-while-listening). Agent interprets as turn yield and launches response. Caller: "kya? Main bol raha tha..." (I was speaking!).
**Why it happens:** "haan" is a complete utterance acoustically. Classifier sees silence after it and fires end-of-turn. Common in Hindi conversational patterns.
**Missing:** Back-channel model fine-tuned on Hindi conversational data.

### 5.4 Hinglish ASR Collapse
**What happens:** Caller switches mid-sentence: "Mera password reset karna hai, login nahi ho raha ek hafte se." ASR either (a) transcribes English words with wrong spelling ("nahin" → "nine"), (b) drops intra-word code-switches, or (c) hallucinates wrong words entirely.
**Why it happens:** Global models not trained on code-mixed corpora. Telephony 8kHz audio further degrades Indic phonemes (retroflexes, aspirated stops poorly represented).
**WER impact:** Jumps from ~11% to ~25-35% on heavy Hinglish.

### 5.5 Latency Spike on Tool Call
**What happens:** Caller asks something requiring CRM lookup. LLM generates tool call; tool executes (50-500ms); LLM resumes. Meanwhile, silence. Caller thinks call dropped, starts talking.
**Why it happens:** No filler injection during tool execution latency. Pipeline hangs waiting for tool result before TTS can start.
**Fix:** Inject pre-synthesized filler at tool-call start; resume from filler end with result.

### 5.6 Geo-Latency to US/EU LLM APIs
**What happens:** India-based caller → India telephony → India server → US LLM API → adds 150-250ms round-trip.
**Why it happens:** Most LLM providers (OpenAI, Anthropic) have primary endpoints in US/EU; no India region as of 2026.
**Partial fix:** Azure OpenAI has Mumbai region for some models. Google Gemini GCP has Mumbai. Anthropic: no India region.

### 5.7 Number and Account ID Misrecognition
**What happens:** Caller says their 10-digit policy number. ASR transcribes 8 of 10 digits correctly. System validates the wrong ID, wastes 30s, caller frustrated.
**Why it happens:** Number strings lack context; ASR confidence is low on digit sequences especially over telephony. "Teen" vs "teen" (3 vs teen) can flip.
**Fix:** Digit-mode ASR grammar (Deepgram keyterm boost), DTMF fallback, explicit confirmation loop.

### 5.8 Regional Language Spill-Over
**What happens:** BSNL caller from rural UP switches to Awadhi or Bhojpuri sub-dialect. ASR trained on standard Hindi fails. WER spikes to > 40%.
**Why it happens:** Training data is metro-biased. Regional dialects and accents massively underrepresented in ASR training corpora.
**Scale of problem:** India has 122 major languages and 1,599 dialects. Standard Hindi + Hinglish covers maybe 40% of BPO call volume comfortably.

---

## 6. Gap to Full Adaptation (vs Human)

### What the Agent CANNOT Yet Do As Well As a Human

**Gap 1: Back-Channel / Listener Acknowledgment (the "haan haan" problem)**
- Human automatically distinguishes agreement-backchannels from turn-yields using prosody + duration + context.
- 2026 agents treat "haan" as turn-end most of the time.
- **Path to close:** Fine-tune a 50M param classifier on 10K+ labeled Hindi conversational back-channel samples. Dataset needed: real call recordings labeled by native Hindi speakers. Timeline: 3-6 months of data collection + 1-2 months fine-tune.

**Gap 2: Dialect and Accent Coverage**
- Human agents (often from similar regional backgrounds) understand caller accents naturally.
- 2026 ASR degrades sharply beyond standard Hindi/Hinglish: Bhojpuri, Rajasthani, Marathi-inflected Hindi, etc.
- **Path to close:** Collect 200-500 hours of dialectal BPO call audio per major region. Fine-tune Sarvam or Whisper v3 with LoRA on this data. Partner with BPO for data labeling. Timeline: 6-12 months.

**Gap 3: Full Duplex Cognition**
- Human simultaneously speaks AND scans CRM AND hears caller AND monitors tone. True parallelism.
- 2026 cascade pipeline is still sequential: VAD→STT→LLM→TTS. Even with streaming, it's a daisy-chain.
- **Path to close:** Speech-to-speech models (OpenAI GPT-Realtime-2, Kyutai Moshi) eliminate the cascade. But: lack Hindi TTS voices, reduced controllability, no intermediate text for logging/compliance. Adoption in India: 12-18 months away for production-grade Indic S2S.

**Gap 4: Prosodic Empathy Matching**
- Human modulates voice tone, pace, warmth in real time to match caller's emotional state.
- 2026 TTS generates natural-sounding speech but with fixed emotional baseline; no real-time emotional prosody adaptation.
- **Path to close:** Emotion-conditioned TTS models (ElevenLabs expressive v3, Sarvam expressive mode). Feed caller emotion signal (sad/angry/confused from STT sentiment) as TTS conditioning. Partially available in 2026; Hindi coverage limited.

**Gap 5: Contextual Silence Comfort**
- Skilled agent knows when to let silence breathe (customer is thinking, not done).
- Agent system treats all silence > threshold as end-of-turn trigger.
- **Path to close:** Variable silence threshold based on context: (a) post-complex-question: longer threshold, (b) post-simple-question: shorter. Requires conversation state tracker that feeds threshold adjuster.

**Gap 6: Low-Latency India Inference**
- Human agent has zero LLM API latency — their "brain" is co-located.
- India→US LLM roundtrip adds 150-250ms structurally.
- **Path to close:** (a) Azure OpenAI Mumbai region (some models), (b) Self-hosted Llama 3.3 70B on Modal/RunPod India data center, (c) Gemini GCP Mumbai. Target: < 50ms LLM roundtrip. Achievable in 12 months as cloud providers expand India.

---

## 7. HITL Trigger — When Human Must Take Over

For THIS specific step (voice pipeline/latency), HITL triggers are:

1. **Barge-in loop failure** — agent and caller talk over each other for 3+ consecutive turns → auto-transfer to human queue with call transcript
2. **ASR confidence persistently low** — 3 consecutive turns with ASR confidence < 0.6 and no semantic intent extracted → escalate
3. **Caller explicitly requests human** — "aap se baat nahi karni, mujhe insaan chahiye" (any variant) → immediate transfer, no retry
4. **Silence timeout** — caller goes silent > 15 seconds after repeated prompts → warm-transfer to human
5. **Emotional escalation** — VAD detects crying, shouting persisting > 2 turns despite de-escalation attempt → human
6. **DTMF non-response** — caller fails voice VAD consistently and also fails DTMF fallback → operator

**None-fully-automatable for this step:** Fully automatable for structured, predictable call flows. HITL needed only in above failure recovery scenarios.

---

## 8. Automation Readiness: 6 / 10

**Rationale:**
- Core pipeline (VAD→STT→LLM→TTS with barge-in) works in production for English; achieves < 700ms in optimized deployments.
- **India-specific deductions:**
  - Hinglish/code-switch ASR WER still 15-20% (vs 6-8% for English); not production-grade for complex conversations.
  - No dominant India-region LLM endpoint; geo-latency structural.
  - Back-channel handling unsolved → frequent premature interruptions → bad CX.
  - Dial compliance (TRAI DLT, DPDP consent) adds complexity not present in Western deployments.
- **Score justification:** A 6 means "works for simple scripted flows, fails on complex unscripted ones." Structured flows (bill payment, FAQ, IVR replacement) are ready today. Complex conversations (complaint resolution, insurance mis-selling complaints) are not.

---

## 9. Build Spec

### What to Implement

**Phase 1: Baseline pipeline (4-6 weeks)**
- Twilio / Plivo → LiveKit → Pipecat frame pipeline
- Silero VAD → Sarvam STT (streaming) → Claude 3.5 Haiku (streaming) → Sarvam TTS (sentence-streaming)
- Basic barge-in: VAD on AEC output → TTS cancel
- Pre-synthesized filler pool (10-15 clips in Hindi/Hinglish)
- Latency instrument: timestamp every stage to JSONL

**Phase 2: Semantic turn detection (3-4 weeks)**
- Integrate LiveKit EOU model (or fine-tune SmolLM on Hindi conversational data)
- A/B test: silence-only vs EOU model on latency and premature-interruption rate
- Back-channel classifier: distilled binary model on "haan/okay/theek hai" patterns

**Phase 3: India ASR optimization (6-8 weeks)**
- Collect 50-100 hours of labeled BPO call audio (Hinglish, major regional accents)
- Fine-tune Sarvam STT with LoRA on domain vocabulary
- Implement domain vocab boost (product names, policy IDs, city names)
- DTMF fallback for account number entry

**Phase 4: India geo-latency reduction (2-3 weeks)**
- Deploy LLM on Azure OpenAI Mumbai region (GPT-4o-mini) or GCP Mumbai (Gemini Flash)
- Measure before/after TTFT improvement
- Response caching for top-50 scripted responses (instant TTS play)

### Data Needed
- 100+ hours of Hindi/Hinglish telephony audio (8kHz, real BPO calls)
- 10K labeled back-channel samples (Hindi: haan/theek/sahi - labeled as backfill vs turn-end)
- Domain vocabulary list (product names, policy terms, city names, common account queries)
- Golden eval set: 300 turns labeled with correct end-of-turn decision + barge-in timing

### Eval Metric Gate ("ship when...")
- End-to-end P50 latency: < 700ms (measured from `userSpeechEnd` to `firstAudioByte`)
- End-to-end P90 latency: < 1200ms
- Barge-in detection rate: > 90% of true interruptions caught within 150ms
- Premature interruption rate: < 5% of turns (false positive barge-in)
- Back-channel suppression accuracy: > 85% (haan/okay correctly not treated as turn-end)
- ASR WER on domain Hinglish eval set: < 18%
- Tool-call silence coverage: 100% of tool calls get filler injection

---

## 10. India Specifics

### Hinglish / Code-Switching
- **Intra-word code-switching:** "adjust-karo", "account-wala", "reset-nahi-ho-raha" — ASR must not break these at language boundaries. Standard ASR trained on monolingual corpora fails.
- **Phonological interference:** Hindi speakers pronounce "v" as "w", retroflexes alter English phoneme perception. ASR needs accent-robust training data.
- **Number verbalization patterns:** "Double seven" (77), "double-zero" (00), "teen tin" (3, 3), "paanch sau" (500) — all need normalization rules.
- **Regional variants:** Tamil-English (South India), Bengali-English (East), Marathi-English (West) — each has distinct code-switch patterns. BPO must detect caller origin and route to appropriate ASR variant.

### Regulatory Compliance (Voice Layer Specific)
- **TRAI DLT:** Every outbound call requires registered sender header and pre-approved script template. AI-generated responses must stay within registered template bounds for outbound flows.
- **DPDP Act (2023):** Voice recordings are personal data. Must: (a) state recording is happening before call starts, (b) get explicit consent for promotional calls, (c) honor deletion requests (right to erasure) after purpose fulfilled, (d) limit retention to regulatory minimum.
- **IRDAI (insurance):** Disclosure within opening 10 seconds: agent name + insurer name + capacity. All coverage claims must match policy documents. Recorded consent mandatory for policy-impacting actions.
- **RBI (BFSI):** Calling hours strictly 8 AM - 7 PM IST. Identity disclosure within 30 seconds. No abusive language (ML classifier must monitor for tone). Recording minimum 90 days, up to 3 years for high-value loans.
- **DND scrubbing:** Pre-call lookup against TRAI National DND Registry is mandatory. Must be automated and logged before dialing.

### Consent Capture in Voice Pipeline
- **Mandatory opening script:** "Yeh call record ki ja rahi hai. Kya aap continue karna chahenge?" (This call is being recorded. Do you wish to continue?)
- **Consent signal detection:** VAD must correctly interpret caller's "haan" post-consent prompt as consent signal (not just acknowledgment). Must be time-stamped and stored.
- **Language of consent:** DPDP suggests plain language in customer's preferred language. System must offer consent prompt in detected caller language.

### Telephony Infrastructure India
- **PSTN quality:** Indian mobile networks (Jio, Airtel, Vi) deliver 8kHz AMR-NB audio. Quality variance is high. ASR must be robust to AMR compression artifacts.
- **Network jitter:** India mobile networks show higher jitter than US/EU. LiveKit's jitter buffer and Plivo's India-region CDN help.
- **Preferred telcos for BPO:** Exotel (DLT-native), Tata Communications (enterprise SIP), Plivo (developer-friendly, India routes), Twilio (with India SIP trunk).
- **VoIP vs PSTN:** Enterprise BPOs use SIP trunks. Consumer-facing voice agents increasingly use WebRTC (app-embedded calls) — better audio quality, no carrier compression.

### Calling Hours + Time Gates
- Code the voice pipeline to check IST time before initiating outbound calls.
- BFSI/collections: hard block outside 8 AM-7 PM IST.
- General BPO: TRAI recommends 9 AM - 9 PM but sector-specific rules apply.
- Weekend and public holiday gates must be configurable.

---

## Sources

- [Retell AI: How Real-Time Voice AI Works (STT→LLM→TTS)](https://www.retellai.com/blog/how-real-time-voice-ai-works-stt-llm-tts)
- [Retell AI: Voice AI Latency Benchmarks](https://www.retellai.com/resources/ai-voice-agent-latency-face-off-2025)
- [Hamming AI: Voice AI Latency — What's Fast, What's Slow](https://hamming.ai/resources/voice-ai-latency-whats-fast-whats-slow-how-to-fix-it)
- [Picovoice: Complete Guide to VAD 2026](https://picovoice.ai/blog/complete-guide-voice-activity-detection-vad/)
- [Picovoice: Cobra vs Silero vs WebRTC VAD Benchmarks](https://picovoice.ai/blog/best-voice-activity-detection-vad/)
- [LiveKit: Turn Detection — VAD, Endpointing, Model-Based](https://livekit.com/blog/turn-detection-voice-agents-vad-endpointing-model-based-detection)
- [LiveKit: Sequential Pipeline Architecture](https://livekit.com/blog/sequential-pipeline-architecture-voice-agents)
- [LiveKit: Using Transformer for End-of-Turn Detection](https://livekit.com/blog/using-a-transformer-to-improve-end-of-turn-detection)
- [Gradium: Turn-Taking in Voice Agents — Why Rule-Based VAD Is Broken](https://gradium.ai/content/turn-taking-voice-agents-vad)
- [Agora: TEN VAD and Turn Detection](https://www.agora.io/en/blog/making-voice-ai-agents-more-human-with-ten-vad-and-turn-detection/)
- [Smallest.ai: Real-Time S2S for Customer Support](https://smallest.ai/blog/real-time-speech-to-speech-ai-for-customer-support-how-to-build-low-latency-voice-conversations)
- [Smallest.ai vs Sarvam AI comparison](https://smallest.ai/blog/smallest-ai-vs-sarvam-ai)
- [Deepgram: Hinglish Voice AI — Why ASR Fails](https://deepgram.com/learn/hinglish-voice-ai-speech-recognition)
- [Gnani.ai: Code-Switching Speech Recognition Hinglish](https://www.gnani.ai/resources/blogs/blog-code-switching-speech-recognition-hinglish-asr)
- [Caller Digital: Voice AI India Regulatory Map 2026](https://www.caller.digital/blog/voice-ai-india-regulatory-map-2026)
- [AutoInterviewAI: AI Calling India DPDP/TRAI Compliance](https://www.autointerviewai.com/blog/ai-calling-india-dpdp-trai-dlt-compliance-complete-guide-2026)
- [OpenAI: Delivering Low-Latency Voice AI at Scale](https://openai.com/index/delivering-low-latency-voice-ai-at-scale/)
- [OpenAI: Introducing GPT-Realtime](https://openai.com/index/introducing-gpt-realtime/)
- [Trillet AI: Voice AI Latency Benchmarks 2026](https://trillet.ai/blogs/voice-ai-latency-benchmarks)
- [Plivo: How to Build a Voice AI Agent — LiveKit, Pipecat, TEN](https://www.plivo.com/blog/how-to-build-a-voice-ai-agent-livekit-pipecat-ten-or-native/)
- [Softcery: Real-Time vs Turn-Based Voice Agents Architecture](https://softcery.com/lab/ai-voice-agents-real-time-vs-turn-based-tts-stt-architecture)
- [arxiv: Building Enterprise Realtime Voice Agents (2603.05413)](https://arxiv.org/html/2603.05413v1)
- [Sarvam AI: Text to Speech API for Indian Languages](https://www.sarvam.ai/apis/text-to-speech)
- [Parloa: Speech Latency in Voice AI for CX](https://www.parloa.com/knowledge-hub/speech-latency-voice-ai/)
- [Reverie: Multilingual Speech Recognition Trends India](https://reverieinc.com/blog/multilingual-speech-recognition-trends/)
- [SIMBA Voice: Echo Cancellation in Real-Time Voice AI](https://simbavoice.ai/resources/echo-cancellation-in-real-time-voice-ai)
