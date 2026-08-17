# B02 — Indic ASR Engineering

**Chunk:** Indic ASR engineering (code-mixed Hindi+regional, telephony 8kHz audio, noise, accents)

**Scope:** India-market, multilingual (Hindi + regional + Hinglish), RBI/IRDAI/DPDP-compliant, action-taking voice+chat contact-center agent for mid-market BPOs.

**Last updated:** 2026-06-24

---

## 1. What a skilled human contact-center agent actually does in this step

A human agent on a telephony call does not "do ASR" as a single act. They perform a cascade of micro-skills, most of them running in parallel and sub-consciously. Broken into atomic sub-steps:

### Acoustic preprocessing (sub-conscious, instantaneous)

1. **SNR estimation** — the agent's auditory cortex judges within ~200ms whether the call quality is clean, has road noise, echo, or is on a congested 2G line. This triggers gain compensation in how attentively they listen.
2. **Echo / sidetone filtering** — on PSTN/GSM the agent hears their own voice back with ~50ms delay; they learn to ignore it and attend to the caller's signal only.
3. **Packet-loss concealment** — when the line breaks up for 50–300ms, the agent uses context to fill the phonetic gap ("he said 'account numb—' and then I heard '—seven-eight-nine' so the middle was probably digits").
4. **8kHz bandwidth awareness** — the agent sub-consciously knows fricatives (s, sh, f) blur on narrowband; they rely more on vowels, prosody, and context.

### Speaker + dialect calibration (first 3–5 seconds)

5. **L1 identification** — agent detects whether the caller's primary language is Hindi, Tamil, Telugu, Marathi, Bengali, Gujarati, Kannada, Punjabi, or one of ~20 others within the first sentence.
6. **Accent mapping** — within the same language, regional sub-dialect matters: UP Hindi vs. Bihari (Bhojpuri/Maithili inflections) vs. Rajasthani vs. Pahadi vs. Standard Delhi. The agent recalibrates phoneme mappings.
7. **Code-switch ratio estimation** — is this caller Hinglish (50/50), English-dominant, or Hindi-dominant? Some callers switch mid-word ("account-wa mein problem hai").
8. **Speech rate calibration** — fast urban callers vs. slow deliberate rural callers. Affects how the agent segments breath groups.

### Online transcription / comprehension

9. **Phoneme stream parsing** — continuous stream; agent does NOT wait for sentence-end to start understanding. Partial parses are updated as more signal arrives.
10. **Lexical ambiguity resolution** — "Rohit" vs. "Rohith" vs. "Roheit"; "PAN" vs. "pan"; "ATM pin" vs. "aatma" — resolved by context (is this an account query?).
11. **Named-entity focus** — agent knows to laser-focus on high-value tokens: mobile numbers, account numbers, policy IDs, amounts, dates. They tolerate misparse of filler words but not entities.
12. **Language-tag assignment per token** — even if not explicit, the agent mentally knows "this word is English," "this is transliterated Hindi written in Roman," "this is a proper noun in Marathi."
13. **Disfluency filtering** — "main, main... woh account, haan woh account ka..." — the agent strips repetitions and false starts automatically.
14. **Barge-in detection** — when the caller interrupts themselves or interrupts the agent's response, the agent switches attention almost instantly (<300ms).

### Post-transcription normalization

15. **Number verbalization** — "teen-sau-tees" → 330; "double four" → 44; "ek lakh pachaas hazaar" → 150,000. Context matters: "ek-do-teen" in account context means digits 1,2,3 not the number 123.
16. **Indic script normalization** — the agent mentally maps spoken Devanagari to the bank's Latin-script database ("Suresh Kumar" vs. "Suresh Kumaar").
17. **Intent extraction** — transcription and intent run in parallel; agent is already forming hypotheses ("this is a balance inquiry") before the sentence is complete.
18. **Confidence flagging** — agent mentally marks uncertain words: "I think he said 'Axis' bank but it could be 'access' — I should ask."

---

## 2. Agent approach — how a 2026 AI system performs each sub-step

| Human micro-step | AI technique in 2026 |
|---|---|
| SNR estimation | Real-time DNSMOS scorer (Microsoft DNSMOS P.835, runs in <5ms on CPU) feeds a dynamic confidence floor to the ASR decoder |
| Echo/sidetone filtering | WebRTC AEC3 (Acoustic Echo Cancellation 3rd gen) applied to raw PCM stream before ASR ingestion; or Speex AEC for lightweight PSTN paths |
| Packet-loss concealment | RNN-based PLC (e.g., Google's RNNoise PLC or Opus PLC in WebRTC stack) applied at codec layer |
| 8kHz bandwidth awareness | Band-limited acoustic model — model trained natively on 8kHz audio (NOT just downsampled 16kHz); or bandwidth extension via DNN super-resolution (e.g., BSHALL / Samplerate upsampler) to 16kHz pre-ASR |
| L1 identification | Frame-level Language ID (LID) head on conformer encoder — multi-class softmax over 22 Indic languages + English, updated every 500ms. Gnani Prisma v2.5 and Sarvam Saaras v3 both do this natively |
| Accent mapping | Accent-conditioned acoustic model — adapter layers (LoRA) per accent cluster (North-belt, South-accent-Hindi, East-belt, Dravidian-accent). LAHAJA benchmark used for eval |
| Code-switch ratio estimation | Token-level LID running in parallel with ASR decoder; Weighted Finite-State Transducer (WFST) or neural LM that scores cross-lingual transitions naturally |
| Speech rate calibration | Dynamic CTC/RNNT beam width + timing model; streaming chunk size adjusted per detected speech rate |
| Online / streaming transcription | CTC + RNNT hybrid streaming decoder (e.g., IndicConformer-600M streaming mode, or Saaras v3 Realtime WebSocket). Partial hypotheses emitted every 200–500ms |
| Lexical ambiguity resolution | Contextual LM rescoring — domain-specific n-gram or neural LM rescores top-N hypotheses; bank/insurance vocabulary boosted via shallow fusion hotword list |
| Named-entity focus | Entity-aware decoding — hotword boosting (bias phrases) fed at inference time; post-ASR NER via IndicBERT/XLM-R fine-tuned on financial entities |
| Disfluency filtering | Sequence-to-sequence disfluency removal model (fine-tuned T5 or small Llama); or rule-based repetition filter on ASR lattice |
| Barge-in detection | Silero VAD or Pyannote VAD running in parallel on each channel; interrupt signal triggers ASR flush and response cancellation within <300ms |
| Number verbalization | Finite-state number normalizer — Indic-specific: handles "lakh", "crore", "hazaar", digit strings, mixed spellings. Tools: Pynini FST, or IndicNLP normalizer |
| Named entity normalization | Named entity normalization pipeline: transliteration (AI4Bharat IndicTrans2 letter-to-letter) + soundex / phonetic matching against CRM database |
| Intent extraction | Parallel intent classifier on partial transcript — lightweight distilled model (MiniLM or IndicBERT) updates intent label every 500ms as transcript builds |
| Confidence flagging | ASR lattice confidence scores (log-prob of top hypothesis vs. 2nd-best) → uncertainty flag triggers agent escalation or clarification prompt |

---

## 3. Concrete 2026 tooling stack

### Tier-1 (production-grade, India-specific, recommended)

**Primary ASR engine (pick one):**
- **Gnani Prisma v2.5** (June 2026) — ranked #1 in 8 of 9 Indian languages on Gramvaani + real-world noisy benchmarks; 14M-hour proprietary corpus; native GSM/VoIP codec handling; word-level code-switching without language tagging; API + on-premise. Best for Dravidian language BPOs.
- **Sarvam Saaras v3** — 1M+ hour training; 22 official Indian languages; streaming WebSocket API; <150ms TTFT in Fast mode; Balanced + Accurate modes; reinforcement-learning post-training; best on IndicVoices (19.31% WER across 10 languages). Best for breadth and Hindi+regional mix.
- **AI4Bharat IndicConformer-600M-Multilingual** — open-weight (MIT license), Conformer-Large, 22 languages, hybrid CTC+RNNT; self-hosted on GPU. Best for cost-sensitive BPOs or privacy-first on-prem deployments.

**Fallback / ensemble:**
- **OpenAI Whisper Large-v3** — strong Hindi-only; degrades on Hinglish; useful as second decoder for confidence arbitration.
- **Azure Cognitive Services Speech (South India endpoint)** — enterprise SLA; lower WER than US-routed but still loses to Indian-trained models on code-mixed.

**Pre-processing pipeline:**
- **WebRTC AEC3** (C++ via libspeexdsp Python binding) — echo cancellation
- **RNNoise** — background noise suppression (pub/sub noise)
- **Silero VAD v4** (PyTorch, <20ms latency) — endpoint detection, barge-in, silence trimming
- **Pynini + IndicNLP** — Indic text normalization (numbers, dates, currency)

**Streaming infrastructure:**
- **WebSocket server** (FastAPI + uvicorn) receiving G.711 µ-law/A-law from Asterisk/FreeSWITCH/Twilio
- **FFMPEG** or **sox** for on-the-fly PCM conversion (8kHz → 16kHz via sinc upsampling for models that require it)
- **Pyannote Audio 3.3** — speaker diarization for multi-speaker calls (agent vs. customer channel separation)

**Post-ASR layer:**
- **IndicBERT / XLM-R** fine-tuned NER — entity extraction (PAN, Aadhaar, account numbers, amounts)
- **AI4Bharat IndicTrans2** — transliteration (Roman Hinglish → Devanagari) for CRM lookup
- **Langfuse** — tracing ASR hypotheses, confidence scores, latency per call turn

**Eval:**
- **LAHAJA** benchmark — multi-accent Hindi WER eval
- **Voice of India** benchmark (arxiv:2604.19151) — 15 languages, 139 regional clusters, telephony audio
- **Gramvaani** benchmark — rural + semi-urban Hindi, Gnani's hardest benchmark
- **IndicVoices** — Sarvam's primary benchmark, 10 languages

---

## 4. Benchmarks

All numbers below are sourced or tagged as estimates based on published comparator data.

### WER by model tier (telephony + accent + code-switch, 8kHz audio)

| Tier | Hindi | Hinglish (code-mixed) | Tamil | Telugu | Bengali |
|---|---|---|---|---|---|
| Global US-trained (Azure, AWS, Google) | 38–52% | 55–70% | 45–58% | 47–60% | 42–55% |
| Indian-trained, no telephony specialization | 10–16% | 15–22% | 14–22% | 15–23% | 14–22% |
| Indian-trained + telephony specialized (frontier) | 7–12% | 10–16% | 11–17% | 12–18% | 11–17% |

[sourced — caller.digital/blog/voice-ai-wer-benchmarks 2026]

### Specific model data points

| Model | Benchmark | WER | Source |
|---|---|---|---|
| Sarvam Saaras v3 | IndicVoices (10 langs) | 19.31% overall | [sourced — sarvam.ai/blogs/asr] |
| Gnani Prisma v2.5 vs Sarvam Saaras v3 | Noisy Dravidian langs | 18% lower WER than Sarvam | [sourced — BusinessToday, Jun 2026] |
| Gnani Prisma v2.5 | Rural Hindi dialects | 15% lower WER vs. competitors | [sourced — cxotoday.com, Jun 2026] |
| IndicWhisper | Vistaar benchmark (39/59 subsets) | Avg 4.1 WER reduction vs. base Whisper | [sourced — arxiv Vistaar paper] |
| AI4Bharat IndicASR / Wav2Vec | Clean Hindi | 12–18% WER | [estimate — open-source community reports] |
| AI4Bharat IndicASR / Wav2Vec | 8kHz telephony | 22–30% WER | [estimate] |
| Voice of India district variation | Nainital (easiest) | ~4% WER | [sourced — arxiv 2604.19151] |
| Voice of India district variation | Mannarakkat (hardest) | ~44% WER | [sourced — arxiv 2604.19151] |
| Voice of India | Bhojpuri/Maithili | 4–5x WER vs. Hindi baseline | [sourced — arxiv 2604.19151] |

### Latency

| Metric | Number | Source |
|---|---|---|
| Sarvam Saaras v3 TTFT (Fast mode) | <150ms | [sourced — docs.sarvam.ai] |
| India-first platforms end-to-end | 180–260ms p95 | [sourced — caller.digital] |
| Global platforms (US/EU region) end-to-end | 900–1,200ms p95 | [sourced — caller.digital] |
| Network routing overhead India-first | 10–20ms | [sourced — caller.digital] |
| Network routing overhead global | 180–220ms | [sourced — caller.digital] |

### VAD benchmarks

| Model | TPR at 5% FPR |
|---|---|
| WebRTC VAD (Google) | 50% |
| Silero VAD | 87.7% |
| Picovoice Cobra VAD | 98.9% |

[sourced — picovoice.ai/blog/best-voice-activity-detection-vad 2026]

---

## 5. Failure modes

1. **Aggressive intra-sentential code-switching** — when a caller switches language mid-word or mid-syllable ("my account-wa mein paisa credit nahi—"), global models drop the Hindi suffix and hallucinate English words. Even Indian models lose 5–8pp WER here. Root cause: training data has sentence-level switches, not morpheme-level.

2. **Low-resource dialects — Bhojpuri, Maithili, Awadhi, Chhattisgarhi** — Voice of India data shows 55–65% WER for out-of-region migrants (Chhattisgarhi speakers in Tamil Nadu). Training data for these dialects is 10–100x less than standard Hindi.

3. **Telephony codec degradation** — G.729 (8kbps) and AMR-NB are lossy. 8kHz narrowband removes fricatives above 3.4kHz. This causes f/s/sh confusion. Adding 2–6% packet loss further degrades to +3–8pp WER versus clean audio.

4. **Background noise + cross-talk** — open-plan BPO floors have simultaneous agent conversations at 70+ dB. Beam-forming and channel separation help but the model still gets partial leakage of adjacent agent speech as "customer" words.

5. **Strongly accented English in Indian context** — Tamil Nadu English, Bengali English, and Gujarati English have systematic phoneme substitutions (v/w, p/b, retroflex plosives) that confuse models trained on pan-Indian data without region-specific fine-tuning.

6. **Number entity failures** — Indian number verbalization is non-trivial: "teen-do-panch" could be a PIN (325) or a count (three, two, five said individually). Model often gets the digits right but formats wrong ("325" vs. "3-2-5"). EER (Entity Error Rate) on account numbers can be 8–15% even when WER is 10%.

7. **Female voice bias** — Voice of India benchmark confirms 19–21% male-speaker penalty vs. female speakers across ALL models tested. Cause: most telephony training data over-represents male callers in India.

8. **Streaming partial hypothesis instability** — in CTC streaming decoders, partial hypotheses flip between characters. For financial data (PAN, account numbers), a flip from "AB" to "ABC" mid-stream causes downstream NER to fire on wrong entity. Needs stable-prefix guarantee or deferred entity commitment.

9. **IVR pre-audio corruption** — DTMF tones, hold music, on-hold beeps, IVR transitions all inject non-speech signals that confuse VAD and sometimes get transcribed as garbage tokens. Models need IVR-aware pre-filter.

10. **Same-channel diarization failure** — when caller and agent are on the same audio channel (no separate recording tracks), speaker diarization at turn boundaries fails if one speaker starts before the other finishes (overlapping speech). The wrong words get attributed to the wrong speaker, breaking downstream compliance tagging.

---

## 6. Gap to full human adaptation

### What the agent still can't do as well as a human:

**Gap 1 — Deep dialect generalization (highest-priority)**
Humans with native-language background instantly recognize and adapt to Bhojpuri, Awadhi, Marwari. Current models have no dialect-specific acoustic model for these; they fail on out-of-distribution phoneme inventories (e.g., Bhojpuri retroflex nasals absent from training).

Closing path: Collect 500+ hours per dialect from real calls (with DPDP consent, anonymized); fine-tune dialect-conditioned adapters (LoRA layers on IndicConformer-600M); eval on LAHAJA-style regional benchmarks.

**Gap 2 — Morpheme-level code-switching**
Humans handle "main gaya-tha" (past tense suffix on English base) and "account-wa" (Bhojpuri diminutive suffix on English noun) perfectly. ASR models trained on sentence-level CS data miss intra-word mixing.

Closing path: Data augmentation with morpheme-level code-mixed sentences; train LM on COMI-LINGUA dataset (arxiv 2503.21670); use byte-level tokenizer (BPE on mixed script) so morpheme boundaries are visible to decoder.

**Gap 3 — Financial entity accuracy under noise**
Human agents confirm ambiguous entities ("aapne kaha PAN number AB Charlie...?"). Models transcribe and pass forward; downstream NER can produce wrong entity silently.

Closing path: Confidence-threshold trigger for entity re-prompting; dual-path decode (character-level fallback for numeric strings); CRM regex-validate in real-time and trigger re-ask if format invalid.

**Gap 4 — Real-time adaptation within a call**
A human recalibrates continuously — if they mishear something and the customer corrects them, they update their internal phoneme model for that caller. Current ASR systems are stateless per utterance.

Closing path: Stateful decoder with speaker adaptation — accumulate N-best hypotheses across the call, use speaker embedding (d-vector / x-vector) for live adaptation. Research exists (MAML-based fast adaptation) but not production-ready for Indic languages.

**Gap 5 — Intent-aware phoneme selection**
Humans use top-down semantic context to disambiguate ("did they say 'teen' (3) or 'ten' (10)?"). Current decoders do bottom-up phoneme-to-word only. LM rescoring helps but is not as tight as human semantic grounding.

Closing path: Joint ASR+intent decoder (e.g., end-to-end spoken language understanding) — encode audio → CTC tokens + intent label simultaneously. Sarvam's reinforcement-learning post-training step moves in this direction but isn't publicly benchmarked on this specific task.

---

## 7. HITL trigger

Human must take over when:
- ASR confidence score < 0.60 on a named entity (PAN, account number, policy ID, amount) AND the system cannot get a valid confirmed value after 2 re-prompt attempts
- Detected language is not in the model's supported language set (e.g., Konkani, Dogri, Santali in a BPO not specifically set up for them) — route to human agent who speaks that L1
- Packet loss > 15% (estimated from ASR gap patterns) — call quality is irrecoverable; escalate
- Caller is using a dialect-specific term the model has no vocabulary entry for AND the utterance is a critical entity (account numbers, complaint ID)
- Regulatory trigger: IRDAI / RBI sensitive interaction (insurance mis-selling detection, loan restructuring) where transcript confidence is below threshold and the interaction will be used in a regulatory audit

For routine interactions (balance inquiry, statement request, simple complaint logging) where ASR confidence > 0.80 and entity validation passes: no HITL needed.

---

## 8. Automation readiness: 6 / 10

**Rationale:**
- Hindi + standard Hinglish in clean telephony: 8–9/10 (production-ready right now with Gnani/Sarvam)
- Hindi + heavy dialect variation (Bhojpuri, Maithili, Chhattisgarhi): 3–4/10 (significant WER, real incident risk)
- Dravidian regional languages (Tamil, Telugu, Kannada, Malayalam): 5–6/10 with Indian-trained models
- Low-resource Indian languages (Santali, Dogri, Bodo, Manipuri): 1–2/10 (no production-grade model)
- Noisy telephony (GSM, 2G, high packet loss): 5–6/10 even with best Indian models

Composite = 6/10. The step is deployable for the 70–75% of calls that are Hindi/Hinglish over acceptable-quality lines. A residual 25–30% still need human or hybrid handling.

---

## 9. Build spec

### What to implement

**Component 1: Audio ingestion pipeline**
- Accept G.711 µ-law/A-law PCM from Asterisk/FreeSWITCH/Twilio via WebSocket or SIP Media stream
- Apply WebRTC AEC3 (echo cancellation) + RNNoise (noise suppression)
- Run Silero VAD v4 (PyTorch, 20ms chunks) for endpoint detection and barge-in signal
- Resample 8kHz → 16kHz via sinc filter (not linear interpolation) for models requiring 16kHz input

**Component 2: Primary streaming ASR**
- Integrate Sarvam Saaras v3 Realtime WebSocket API (or Gnani Prisma v2.5 if Dravidian languages are primary)
- Stream 200ms audio chunks; receive partial hypotheses every 300ms
- Buffer partial hypotheses; commit final hypothesis on VAD end-of-speech signal
- Fallback: IndicConformer-600M self-hosted on A100/H100 GPU (Modal Labs or RunPod) for on-prem/cost-sensitive path

**Component 3: Post-ASR normalization**
- Pynini FST-based number normalizer (lakh, crore, hazaar, ordinals, dates)
- IndicNLP text normalizer (Unicode normalization, punctuation)
- AI4Bharat IndicTrans2 transliteration (Roman → Devanagari for CRM lookup)

**Component 4: NER + entity validation**
- IndicBERT or XLM-R fine-tuned on financial entity dataset (PAN, Aadhaar, account numbers, IFSC, amounts, dates)
- Regex-based format validation post-NER (PAN: `[A-Z]{5}[0-9]{4}[A-Z]`, mobile: `[6-9]\d{9}`)
- Confidence threshold gate: if entity confidence < 0.75, emit re-prompt signal

**Component 5: Observability**
- Langfuse trace per call turn: audio chunk ID, ASR hypothesis, confidence, latency, final entity set
- Per-call WER measurement against agent-corrected ground truth (for continuous eval)
- ASR cost tracking: Sarvam API charges per minute; log input duration + API cost per call

### Data needed

| Data asset | Volume | Purpose |
|---|---|---|
| Real BPO call recordings (with consent) | 1,000+ hours Hindi/Hinglish | Fine-tune + eval |
| Regional dialect recordings (Bhojpuri, Awadhi, Rajasthani, Marwari) | 200+ hours each | Dialect adapter training |
| Financial entity annotated transcripts | 10,000+ sentences | NER fine-tune |
| LAHAJA benchmark | 12.5 hours, 132 speakers, 83 districts | Accent WER eval |
| Voice of India benchmark | 536 hours, 15 languages | Multilingual eval |
| Gramvaani benchmark | Rural/semi-urban Hindi | Hard Hindi eval |

### Eval metrics and gates

| Metric | Definition | Shipping gate |
|---|---|---|
| WER (overall) | Word-level edit distance on test set | < 15% on BPO telephony test set |
| WER (Hinglish code-mixed) | WER on utterances with >20% language switch tokens | < 20% |
| Entity Error Rate (EER) | % of named entities (PAN, account, amounts) wrong | < 3% |
| Code-Switch Recovery Rate (CSR) | % of language switches handled without WER spike | > 90% |
| TTFT (time to first token) | Latency from speech end to first hypothesis word | < 300ms p95 |
| End-to-end transcript latency | From audio chunk to committed final transcript | < 600ms p95 |
| Barge-in detection accuracy | % of actual interrupts detected within 300ms | > 92% |
| DNSMOS quality gate | Average DNSMOS P.835 score on input audio | > 2.5 (flag calls < 2.0 for escalation) |

---

## 10. India specifics

### Linguistic specifics

**Hinglish code-switching patterns:**
- Hindi morphology on English roots: "login karna hai", "payment pending hai", "update karo"
- Honorifics embedded mid-sentence: "aapka account-ji mein..."
- Digit verbalization is highly contextual: "do-char-six" in account context = digits 2,4,6; in arithmetic = the number 246
- Negation patterns: "nahi chahiye" (don't want), "mat karo" (don't do) — phonetically close to each other but semantically opposite; ASR must get these right
- Script ambiguity: callers from UP often say "nahin" as "nahi"; Punjabi callers say "nahion"; these are the same semantic token

**Regional accent mapping for BPOs:**
- North India Hindi belt (UP, Bihar, MP, Rajasthan, Haryana, Delhi) — ~50% of Indian BPO call volume; within this, Bihar accent (retroflex plosive shift) and Rajasthani accent (dental stop fronting) are hardest
- South India accent on Hindi — Tamil/Telugu callers speaking Hindi substitute dental stops with retroflex; d/l confusion; retroflex r is absent in South India
- Bengali accent on Hindi — breathy voice quality, aspirated stop shifts; ASR needs Bengali-L1-Hindi data
- Gujarati/Marathi callers — vowel length distinctions blur; schwa deletion patterns differ from standard Hindi
- Code-switching differs by city: Mumbai = Bambaiya Hindi (heavy Marathi/Urdu substrate); Delhi = standard Hinglish; Hyderabad = Telugu-Hindi mix; Chennai = Tamil-English with minimal Hindi

**Indian number system specifics:**
- Lakh (1,00,000) and Crore (1,00,00,000) — not in any global model vocabulary
- "Paanch hazaar teen sau" = 5,300; agent must parse this correctly for transaction amounts
- Mobile numbers are 10 digits read as 2+4+4 or 5+5 or individual digits — all valid verbal patterns
- Aadhaar is 12 digits read in 4-4-4 groups
- PAN is 5 alpha + 4 numeric + 1 alpha — read as "A-B-C-D-E one-two-three-four F"

### Regulatory specifics

**DPDP Act 2023 (effective May 2027 but implement now):**
- Explicit consent required before recording: IVR disclosure + caller affirmative action (press 1) is the standard consent flow
- Purpose limitation: recording for "quality assurance" cannot be reused for "behavioral analysis" or "model training" without separate consent — this means BPOs cannot freely use call recordings to fine-tune ASR without separate data use consent
- Data residency: audio and transcripts must be stored in India (ap-south-1 or equivalent Indian cloud region)
- Retention: 6 months (IRDAI insurance sales calls), 2 years (RBI regulated complaint calls), then mandatory secure deletion
- Penalties: up to Rs 250 crore (~$30M) per violation

**TRAI regulations:**
- Automated voice calls must use '140xx' series for promotional, '160xx' for transactional/service
- DLT registration required for every outbound voice campaign; template pre-approval mandatory
- NCPR (National Customer Preference Register) scrub mandatory before any outbound automated call

**RBI specifics:**
- Call recordings for customer complaints: minimum 2-year retention
- No customer PII (account numbers, amounts) in ASR logs transmitted outside India
- Fair Practices Code (FPC): collections calls must be between 8am–7pm IST; ASR must timestamp calls and enforce this

**IRDAI specifics:**
- Insurance sales calls: 6-month recording retention minimum
- Mis-selling detection: ASR transcript used in claim disputes — accuracy on benefit terms ("sum assured", "maturity amount", "exclusion") is legally material
- Key terms that MUST be transcribed accurately: "free-look period", "premium amount", "sum insured", "nomination", "claim settlement ratio"

### Infrastructure specifics for India

- Most Indian BPOs still run on on-premise Asterisk/FreeSWITCH PBX, not cloud-native SIP
- Telephony path: PSTN/GSM → SIP trunk → Asterisk → G.711 PCM stream → ASR
- Latency budget: total end-to-end voice latency (caller speaks → agent/bot responds) should be <800ms. With 150ms ASR TTFT (Sarvam Fast mode) + ~200ms LLM inference + ~150ms TTS + ~150ms network = ~650ms. Achievable.
- Rural India 2G/EDGE calls: AMR-NB (12.2kbps) codec, 15–25 dB SNR, 2–6% packet loss. These require dedicated telephony-noise trained models (Category C per caller.digital benchmark).
- Language-first routing: IVR must detect caller's preferred language in first 3 seconds (LID on greeting utterance) and route to appropriate ASR model + LLM language variant.

---

## Sources

- [Voice of India Benchmark — arXiv 2604.19151](https://arxiv.org/abs/2604.19151)
- [Sarvam Saaras V3 Technical Post](https://www.sarvam.ai/blogs/asr)
- [Sarvam Streaming ASR API Docs](https://docs.sarvam.ai/api-reference-docs/speech-to-text/apis/streaming)
- [Gnani AI Prisma v2.5 Launch — BusinessToday, Jun 2026](https://www.businesstoday.in/technology/artificial-intelligence/story/gnani-ai-launches-prisma-v2-5-claims-better-accuracy-than-sarvam-elevenlabs-on-indian-speech-538008-2026-06-19)
- [Gnani AI Prisma v2.5 — Inc42](https://inc42.com/buzz/gnani-ai-doubles-down-on-sovereign-voice-ai-models-with-prisma-v2-5-launch/)
- [Gnani Prisma v2.5 — CXO Today](https://cxotoday.com/media-coverage/gnani-ai-launches-prisma-v2-5-ranked-1-in-8-of-9-indian-languages-on-real-world-and-noisy-asr-benchmarks/)
- [State of ASR Models in India 2026 — Gnani.ai](https://www.gnani.ai/resources/state-of-asr-models-2026)
- [Why Speech Recognition Fails on Hinglish — Gnani.ai Blog](https://www.gnani.ai/resources/blogs/blog-code-switching-speech-recognition-hinglish-asr)
- [Voice AI WER Benchmarks Indian Languages 2026 — Caller Digital](https://caller.digital/blog/voice-ai-wer-benchmarks-indian-languages-hindi-tamil-telugu-bengali-marathi-2026)
- [Voice AI India vs Global Platforms 2026 — Caller Digital](https://www.caller.digital/blog/voice-ai-india-vs-global-platforms)
- [Open-Source Voice AI India 2026 — Caller Digital](https://www.caller.digital/blog/open-source-voice-ai-india-sarvam-ai4bharat-bhasini-2026)
- [LAHAJA: Multi-accent Hindi ASR Benchmark — arXiv 2408.11440](https://arxiv.org/pdf/2408.11440)
- [AI4Bharat IndicConformer-600M on Hugging Face](https://huggingface.co/ai4bharat/indic-conformer-600m-multilingual)
- [Vistaar: Diverse Benchmarks for Indian ASR](https://arxiv.org/pdf/2305.15386)
- [Best Voice Activity Detection 2026 — Picovoice](https://picovoice.ai/blog/best-voice-activity-detection-vad/)
- [DPDP Act Compliance for Contact Centers — Gistly](https://www.gistly.ai/blog/dpdp-act-compliance-contact-centers)
- [Voice AI Compliance in India — ConversAI Labs](https://www.conversailabs.com/blog/voice-ai-compliance-in-india)
- [Voice AI India Regulatory Map 2026 — Caller Digital](https://www.caller.digital/blog/voice-ai-india-regulatory-map-2026)
- [Call Center Audio Recording Compliance India — ClearTouch](https://www.cleartouch.in/blog/call-center-audio-recording-legal-requirements-in-india/)
- [COMI-LINGUA Code-Mixed Hindi-English Dataset — arXiv 2503.21670](https://arxiv.org/pdf/2503.21670)
- [Sarvam AI ASR Evaluation Beyond WER](https://www.sarvam.ai/blogs/evaluating-indian-language-asr)
- [Benchmarking ASR for Indian Languages in Agricultural Contexts](https://arxiv.org/html/2602.03868v1)
