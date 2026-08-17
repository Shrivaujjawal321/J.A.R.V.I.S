# B03 — Indic TTS & Prosody (Natural, Emotional, Fast, Multi-Language, Interruptible)

> **Series:** India Agentic AI Opportunity Map — BPO Agent Deep Research  
> **Step code:** B03 (Infrastructure layer — voice output)  
> **Researcher:** ml-engineer-agent (Jarvis)  
> **Date:** 2026-06-24  
> **Status:** Complete — build-ready

---

## 1. What This Step Is

This step covers the **voice output layer** of a contact-center AI agent: taking an LLM-generated text response and converting it to speech that a real Indian customer hears on a phone call. This sounds deceptively simple. In practice it is the most perceptually demanding component of the voice pipeline because:

- Humans notice unnatural prosody in under 200ms.
- A wrong emotional tone on a collections call can trigger an escalation.
- Code-mixed Hinglish output that sounds stilted destroys caller trust instantly.
- A 50ms difference in TTFB (time-to-first-byte of audio) is the difference between a natural conversation and a "robot on the line" perception.
- Barge-in (the customer cutting the agent off) must stop audio within 60ms or the caller feels ignored.

The step runs on every agent turn — typically 8–25 times per call. It is on the critical latency path.

---

## 2. Human Agent Micro-Steps — What a Skilled Human Actually Does

A trained BPO agent producing a voice response is doing ALL of the following simultaneously, unconsciously, in real-time. These are the atomic cognitive + mechanical moves:

### 2.1 Linguistic Planning
1. **Chooses the response register** — formal Hindi, Hinglish, regional-flavored Hindi, or code-switched English depending on customer cues heard in the prior turn.
2. **Selects vocabulary level** — avoids banking jargon with Tier-3 callers; uses correct terminology with educated urban callers.
3. **Picks grammatical gender agreement** — Hindi inflects verbs and adjectives by gender (e.g. "aap gaye / gayi"). Agent infers caller gender from voice + name and maintains agreement throughout.
4. **Decides sentence length** — angry customers get shorter, slower sentences; cooperative callers get full explanations.

### 2.2 Prosody Planning (pre-utterance, ~50–100ms)
5. **Assigns stress anchors** — identifies which words carry the critical information (amount, date, policy number) and mentally marks them for louder/slower delivery.
6. **Plans sentence melody** — Hindi is a stress-timed language with a different intonation curve than English; agent produces a natural falling tone on declaratives, rising on genuine questions.
7. **Inserts prosodic boundaries** — decides where to pause (after a large number; after "iska matlab yeh hai ki...") to aid comprehension.
8. **Calibrates speaking rate** — slower for elderly callers, faster for impatient urban callers, deliberately slower when delivering a policy restriction.

### 2.3 Emotional Register Selection
9. **Reads caller emotional state** from prior speech (volume, pitch, speech rate, word choice) — sets own tone accordingly: empathetic-soft for distressed, firm-neutral for aggressive, warm-friendly for cooperative.
10. **Applies micro-pause for empathy** — inserts a genuine-feeling pause ("...haan, samjha...") before pivoting to a solution. This is a learned social signal; premature pivoting sounds callous.
11. **Modulates breath and filler** — light fillers ("dekho", "haan", "toh") at appropriate points signal active listening, not robotic recitation.
12. **Suppresses personal emotions** — even if the caller is abusive, the agent maintains a controlled warm-neutral tone. This is trained self-regulation.

### 2.4 Real-time Delivery Adjustments
13. **Adjusts speed to caller response time** — if caller tries to speak, agent slows or pauses.
14. **Handles barge-in gracefully** — stops mid-sentence cleanly, does NOT restart from the beginning, picks up context for the reply.
15. **Self-corrects mispronunciations in real-time** — catches a wrong English word stress or Hindi case ending mid-word, re-says it correctly.
16. **Varies pitch naturalistically** — avoids monotone; pitch naturally rises on list items, falls on terminal statements.

### 2.5 Disclosure / Compliance Phrasing
17. **Delivers mandatory scripts verbatim** — regulatory disclosures (RBI, IRDAI, DPDP) must be said exactly, but agents learn to say them at near-natural speaking pace to avoid caller hang-ups.
18. **Signals script transition prosodically** — slight change in tone/pace flags "this is the legal bit," setting expectation that it's brief.

---

## 3. Agent Approach — How 2026 AI Does This

### 3.1 Architecture Overview

```
LLM text output
      │
      ▼
[Text Normalizer + SSML tagger] ← emotion classifier output (from B06)
      │
      ▼
[Indic TTS engine (streaming)]
      │
      ▼
[Audio buffer + WebSocket stream] → telephony gateway (8kHz/16kHz PCM)
      │
      ◄────── [VAD / barge-in monitor] ── caller audio in
              If VAD fires: TTS flush <60ms + cancel LLM generation
```

### 3.2 Text Normalization for Indic TTS

**The problem:** Raw LLM output is not TTS-ready. Examples of what breaks:
- Numbers: "₹45,230" → must become "pachaalis hazaar do sau tees rupaye"
- Dates: "23/06/2026" → "teenees June do hazaar chabbees"
- Abbreviations: "EMI", "KYC", "OTP" → spelled out or expanded contextually
- Mixed script: "aapka EMI 3,500 rupees hai" → seamless Devanagari + numeral + English acronym handling
- Honorifics: "Sir/Ma'am" → agent must have resolved caller gender beforehand

**2026 agent approach:**
- Use a **rule-based + LLM hybrid normalizer** trained on Indic telephony text:
  - Rule layer: regex patterns for currency, dates, phone numbers, percentages
  - LLM layer: handles ambiguous abbreviations, proper nouns, code-mixed context
  - Tool: `indicnlp` library + Sarvam's built-in normalization pipeline
- Output: clean text with SSML hints (`<emphasis>`, `<break>`, `<prosody rate="slow">`) or natural-language prosody descriptions (Parler-TTS style prompt: "Speak slowly and empathetically, with a pause before the amount")

### 3.3 TTS Engine Selection (2026 Indic Stack)

Three-tier decision based on deployment context:

**Tier 1 — Managed API (recommended for initial deployment)**

| Engine | Languages | TTFB | Key Strength | India-Specific |
|--------|-----------|------|-------------|----------------|
| **Sarvam Bulbul V3** | 11 Indian langs, 35+ voices | <250ms streaming | Most-preferred in 8kHz telephony blind test (Josh Talks, 500+ annotators, 20k votes); lowest CER on code-mixed text | Hinglish native; telephony-optimized; India infra |
| **Gnani Vachana TTS** | 12 Indic langs | ~300ms | 14M hours telephonic training; call-center native; STT+TTS+orchestration in one platform | Purpose-built for BPO; enterprise contracts |
| **ElevenLabs Multilingual v3** | 11 Indian langs incl. Hindi | 1,232ms (multilingual) / ~280ms (Flash) | Best voice realism globally; `hinglish_mode` flag added | Slower; high cost; US-hosted (latency hit) |
| **AI4Bharat Indic Parler-TTS** | 22 Indian langs | Variable (open-source) | Open-source; natural-language prosody control; 1806h training data | Controllable via text prompts; MOS 4.46 on Hindi |

**Tier 2 — Self-hosted (cost optimization at scale)**

| Engine | Architecture | GPU Req | Key Advantage |
|--------|-------------|---------|---------------|
| **AI4Bharat IndicF5** | F5-TTS architecture | A100/H100 | Zero-shot voice cloning in 22 languages; best for custom voice personas |
| **Coqui XTTS-v2** | VITS-based | A10G | Self-hostable, zero-shot cloning; no per-char cost; ~2s latency unoptimized |
| **Fine-tuned Orpheus (LLaMA 3B)** | LLM-native TTS | 2x A10G | 9 Indian langs; emotion tokens built-in; streaming via vLLM |

**Tier 3 — Future (emerging)**

- **BharatGen A2TTS** (MeitY-funded): Speaker-adaptive diffusion model; ~150M params; zero-shot speaker adaptation from reference audio — useful for matching a brand voice persona

### 3.4 Prosody Control Mechanisms

**Approach 1 — SSML (supported by Sarvam, Google TTS)**
```xml
<speak>
  <prosody rate="slow" pitch="-2st">
    Aapka EMI, 
    <emphasis level="strong">paanch hazaar rupaye</emphasis>, 
    <break time="400ms"/> 
    kal tak jama kar dein.
  </prosody>
</speak>
```
- Works: pause insertion, rate, pitch
- Limitation: cannot directly say "sound empathetic"

**Approach 2 — Natural-language prosody prompts (Parler-TTS / Bulbul V3 style)**
```
"Speak in a warm, empathetic tone, slightly slower than normal, with a 
brief pause before the amount. The speaker is a helpful customer service 
agent addressing a concerned customer."
```
- Works for expressiveness, emotion, style
- Less precise on exact timing

**Approach 3 — Emotion-conditioned generation**
- Input: (text, emotion_label, intensity_level)
- Models: fine-tuned FastSpeech2 / VITS2 with emotion embeddings
- Labels: {neutral, empathetic, firm, apologetic, urgent, cheerful}
- Source: training data from labeled call-center recordings (Gnani has this natively)

**2026 production pattern:** Run a lightweight emotion classifier on the LLM output text (from step B06 pipeline), map to a prosody preset, inject as prompt modifier to the TTS engine.

```python
emotion_map = {
    "empathetic":  {"rate": 0.85, "pitch": -1, "prompt": "warm, slow, caring"},
    "firm":        {"rate": 1.0,  "pitch": 0,  "prompt": "confident, clear, direct"},
    "apologetic":  {"rate": 0.8,  "pitch": -2, "prompt": "sincere, measured, soft"},
    "informational":{"rate": 0.95,"pitch": 0,  "prompt": "clear, professional, steady"},
    "urgent":      {"rate": 1.1,  "pitch": +1, "prompt": "alert, decisive, crisp"},
}
```

### 3.5 Hinglish / Code-Switching Output

The TTS must not just accept mixed-script input — it must produce natural prosody for code-switched output.

**Failure pattern:** TTS trained separately on Hindi and English produces a jarring accent shift when switching languages within a sentence.

**2026 solution:**
- Use models trained on **code-switched corpora** (Bulbul V3 explicitly advertises this; Gnani trained on 14M hours including code-mixed telephonic audio)
- At text preprocessing: normalize script (Devanagari for Hindi words, Latin for English words) — do NOT transliterate everything to one script
- English acronyms (EMI, OTP, KYC, NACH) pronounced as English acronyms, not transliterated
- Example good output: "Aapka *OTP* (pronounced O-T-P) abhi expire ho gaya — ek aur request karein?"

### 3.6 Barge-In / Interruptibility Architecture

This is the hardest sub-problem. Audio must stop within 60ms of VAD trigger.

**Component stack:**
```
Telephony RTP stream
      │
      ▼
[WebRTC VAD / Silero VAD]  ← runs continuously, even during TTS playback
   VAD confidence > 0.75 for 200ms sustained
      │
      ▼ barge_in event
[TTS stream flush] — WebSocket `close` or `stop` signal to TTS provider
   Target: <60ms from VAD trigger to audio silence
      │
      ▼
[AbortController → LLM generation cancel]  ← kills in-flight streaming
      │
      ▼
[New STT stream opens from caller audio]
```

**VAD tuning for India telephony:**
- Indian English callers have different prosodic envelope than US English — false barge-in rates are higher on raw Silero VAD
- Tune: energy gate at -42 dBFS (Indian telecom has more background noise), minimum sustained voice 250ms for IVR replacement, 350ms for banking
- Use **per-region threshold tables** in production (metro vs Tier-2 vs 2G connectivity profiles)

**Key providers supporting mid-stream cancellation:** Cartesia Sonic (WebSocket), ElevenLabs Turbo/Flash, Sarvam Bulbul V3 (streaming API)

### 3.7 Real-Time Streaming Pipeline

```
LLM streamed tokens → sentence boundary detector → TTS request (sentence chunks)
                                                         │
                                                    WebSocket stream
                                                         │
                                               Audio buffer (200ms jitter)
                                                         │
                                             Telephony gateway (RTP/SIP)
```

- **Chunk on sentence boundaries** (period, question mark, exclamation, danda for Hindi "।") — do NOT wait for full LLM response
- Target: first audio chunk plays within 500ms of LLM first-token (for Sarvam V3 + Sonnet combo)
- **Pipeline-level optimization:** Start TTS on sentence 1 while LLM generates sentence 2

---

## 4. Tooling — Concrete 2026 Stack

| Layer | Tool | Version/Notes |
|-------|------|---------------|
| TTS engine (managed) | Sarvam Bulbul V3 | Primary; telephony-native; 11 langs; streaming API |
| TTS engine (fallback) | Gnani Vachana TTS | Full BPO platform option; 12 langs |
| TTS engine (self-hosted) | AI4Bharat IndicF5 | Open-source; HuggingFace `ai4bharat/IndicF5` |
| Voice cloning (personas) | AI4Bharat IndicF5 / Gnani zero-shot | <10s reference audio |
| Text normalizer | indicnlp + custom rules | Currency, dates, abbreviations |
| SSML generation | LLM (Haiku) + template rules | Injects pauses, emphasis markers |
| VAD | Silero VAD v4 | Streaming-friendly; <5ms per frame |
| Barge-in orchestration | LiveKit Agents SDK | WebSocket event bus; TTS flush built-in |
| Telephony integration | Twilio Media Streams / Exotel / Sarvam Telephony | SIP/WebSocket bridge |
| Audio codec | G.711 μ-law / OPUS | 8kHz for legacy PSTN; 16kHz for VoIP |
| Emotion classifier | Fine-tuned BERT/DistilBERT | Classifies LLM output text → emotion label |
| Prosody dataset | AutoProsody (arXiv 2502.09661) | Syllable-level prosodic annotations for Indic training |
| Eval | MOS eval harness (crowdworkers) + CER | Word error + naturalness MOS |
| Observability | Langfuse + custom TTS span (TTFB, flush_ms, VAD_confidence) | Per-turn tracing |

---

## 5. Benchmarks

| Metric | Human Agent | Best-in-Class AI (2026) | Source |
|--------|-------------|------------------------|--------|
| TTFB (time to first audio byte) | ~300ms thinking time | Sarvam V3: <250ms; Cartesia Sonic: 188ms P50 | [sourced — Gradium benchmark, Sarvam blog] |
| Barge-in flush time | ~100ms natural pause | Target <60ms; achievable with WebSocket cancel | [sourced — FutureAGI guide 2026] |
| Hinglish naturalness MOS | ~4.5/5 (human) | Bulbul V3: 4.1–4.3/5 (estimated from Josh Talks blind test) | [estimate — blind test methodology, exact MOS not published] |
| Hindi TTS MOS | 4.5 (human) | Indic Parler-TTS: 4.46 on Hindi test set | [sourced — AI4Bharat HuggingFace card] |
| CER on code-mixed text | ~0% (human) | Bulbul V3: lowest CER in category (exact % not published) | [sourced — Sarvam V3 launch blog] |
| False barge-in rate (India telephony) | N/A | Silero VAD: 5–8% raw; 1.4–2% with tuned thresholds | [sourced — FutureAGI guide; Coval benchmarks] |
| Latency uplift (India infra vs US-hosted) | N/A | India-first: 180–260ms E2E; global: 900–1,200ms | [sourced — caller.digital India vs global platforms] |
| Cost per minute (platform layer) | ₹15–25 (human agent fully loaded) | ₹2.40–₹4.80 (India-first AI voice) | [sourced — caller.digital India market analysis 2026] |
| Emotion detection latency | <200ms (human instinct) | 1.5s audio fragment sufficient for ML emotion classification | [sourced — dialora.ai voice sentiment guide] |
| Languages supported | Typically 1–3 per agent | Sarvam V3: 11; Gnani: 12; AI4Bharat IndicF5: 22 | [sourced — vendor pages] |

---

## 6. Failure Modes

### 6.1 Prosody Failures

| Failure | Root Cause | Severity |
|---------|-----------|----------|
| **Monotone delivery on emotional content** | TTS trained on read speech, not expressive call-center audio | High — caller perceives bot as uncaring |
| **Wrong gender agreement in speech** | LLM generates incorrect Hindi verb form; TTS renders it faithfully | Medium — sounds unprofessional |
| **Unnatural stress on English acronyms** (EMI, OTP said with Hindi syllable stress) | TTS applying Hindi phonotactics to English tokens | Medium — sounds robotic |
| **Script-switch jarring** (accent changes when Hindi→English within sentence) | Model trained on monolingual corpora | High — breaks trust for code-switched content |
| **Flat question intonation** (statements and questions sound identical) | Model lacks contextual sentence-type awareness | Medium |
| **Number mispronunciation** (₹1,00,000 rendered as "one lakh" in wrong language) | Normalizer fails on lakh/crore format vs Western format | High in BFSI context |

### 6.2 Latency Failures

| Failure | Root Cause | Impact |
|---------|-----------|--------|
| **First audio chunk >700ms** | Waiting for full LLM response before TTS | Conversation feels broken |
| **Audio glitches mid-stream** | Network jitter + insufficient buffer | Caller perception: bad quality |
| **TTS flush delay >100ms on barge-in** | Provider does not support WebSocket cancellation; HTTP-based TTS | Caller feels ignored |
| **False barge-in on Indian background noise** | VAD not tuned for Indian telephony noise floor (auto-rickshaws, construction) | Agent cut off mid-sentence repeatedly |

### 6.3 Content Failures

| Failure | Root Cause | Severity |
|---------|-----------|----------|
| **Compliance script garbled** | Normalizer breaks on legal boilerplate; TTS rushes through | Regulatory — IRDAI/RBI non-compliance |
| **Incorrect pronunciation of proper nouns** (branch names, city names, scheme names) | OOV (out-of-vocabulary) handling poor | Medium-High |
| **Code-mixed output in wrong language direction** | LLM generates response in English when customer spoke Hindi | High |
| **Overly formal Hindi** to rural caller | Misclassified register | Medium |

### 6.4 Barge-In Failures

| Failure | Root Cause | Severity |
|---------|-----------|----------|
| **Agent keeps speaking after barge-in** | TTS provider no mid-stream cancel support | High — frustrating UX |
| **Over-sensitive barge-in** (music, TV in background triggers) | VAD threshold too low for ambient noise | Medium |
| **Under-sensitive barge-in** (caller says "haan" but VAD misses it) | False silence detection on breathy Indian voices | Medium |

---

## 7. Gap to Full Human Adaptation

### What AI Still Cannot Do as Well as a Human (2026)

**Gap 1 — Spontaneous prosodic creativity**
A human agent can invent novel prosodic contours for non-standard situations ("Sir, aapke saath jo hua hai woh bilkul bhi hona nahi chahiye tha..."). Current TTS systems interpolate between trained prosody patterns; genuine improvisation is absent.
- **Path to close:** Large-scale expressive training data from real call-center recordings with annotated emotion + prosody labels. Gnani has this at 14M hours — the model architecture needs to learn from it end-to-end.

**Gap 2 — Contextual rate adaptation within utterance**
A human slows down precisely at the 10-digit account number, then speeds up on "please note this down." Current SSML/prompt-based prosody cannot reliably do this at token-level granularity.
- **Path to close:** Token-level prosody prediction models (FastSpeech2 extended with context attention) or LLM-to-SSML pipelines that annotate at word level.

**Gap 3 — Zero-shot dialect adaptation**
A human agent who speaks Bhojpuri-accented Hindi automatically shifts register when they hear the caller's accent. Current models have fixed voice personas.
- **Path to close:** Real-time voice style transfer conditioned on ASR-identified caller dialect (15 major Hindi dialect clusters). Requires per-dialect training data (sparse for Tier-3 dialects like Bundeli, Baghelkhandi).

**Gap 4 — Natural filler + breath timing**
Human agents use "haan...", "theek hai...", "toh..." as social lubricant timed to conversation rhythm. Current TTS either overuses fillers (sounds scripted) or underuses (sounds robotic).
- **Path to close:** Dialogue-level prosody model that predicts filler placement from conversation state, not just text content.

**Gap 5 — Emotional authenticity under escalation**
Human agents genuinely slow their speech, lower pitch, increase pauses when a caller is crying or extremely distressed. AI currently maps emotion → preset; it lacks the continuous gradient modulation humans perform.
- **Path to close:** Real-time emotion tracking of BOTH caller speech (from ASR features) and LLM response semantic content → continuous prosody modulation rather than discrete labels.

**Gap 6 — Robustness to phone channel degradation**
Human agents self-regulate when they sense call quality is poor (speak louder, slower, repeat). Current AI does not model channel quality in TTS decisions.
- **Path to close:** Channel quality estimation (SNR from RTP stream) → TTS rate/volume adaptation.

---

## 8. HITL Trigger

For the TTS layer specifically, human takeover is needed when:

1. **Regulatory disclosure failures are detected** — if the TTS mispronounces or truncates a mandatory RBI/IRDAI disclosure script, a human must deliver it on callback.
2. **Caller explicitly complains about voice quality** — "koi insaan se baat karni hai" (want to speak to a human) → immediate escalation, do not retry TTS.
3. **Repeated barge-in loops** — if the agent has been interrupted >3 times in one response, escalate (indicates severe communication breakdown, not just a latency issue).
4. **Emotion = extreme distress or grief** — caller is crying, reporting a death, extreme anger — TTS cannot authentically handle these; route to human within 1 turn.
5. **Dialect not in training distribution** — if ASR confidence on caller language is <70% AND TTS is generating in mismatched language, flag and escalate.

**Otherwise: none — the TTS step itself is fully automatable for standard call flows.**

---

## 9. Automation Readiness: 7/10

**Why 7 and not higher:**
- Latency is solved (Bulbul V3 sub-250ms, Cartesia sub-200ms)
- Languages are largely covered (11–22 Indian languages)
- Hinglish code-switching works in production (Bulbul V3, Gnani)
- Barge-in is architecturally solved (Silero VAD + WebSocket cancel)

**What keeps it from 9–10:**
- Emotional expressiveness in Indic languages is not fully production-grade — MOS gap vs humans ~0.3–0.5 on expressive speech
- Dialect adaptation (Tier-3 geographies) is unsolved
- Continuous prosody modulation (not discrete emotion labels) is research-stage
- Proper noun pronunciation (bank names, scheme names, city names) still fails frequently
- Integration complexity with Indian telephony (Exotel, TATA Tele, Airtel IQ) is non-trivial

---

## 10. Build Spec

### What to Implement

**Phase 1 — Baseline (Week 1–2)**

```
Input: LLM text output (string, potentially Hinglish/mixed script)
Output: PCM audio stream (8kHz G.711 for PSTN, 16kHz OPUS for VoIP)

Components:
1. Text normalizer (currency, date, number, abbreviation → spoken form)
2. Emotion classifier (text → {neutral, empathetic, firm, apologetic, urgent})
3. SSML/prompt injector (adds pauses, emphasis, rate modifiers)
4. Sarvam Bulbul V3 API client (streaming WebSocket)
5. Barge-in controller (Silero VAD + TTS flush signal)
6. Telephony bridge (Twilio Media Streams or Exotel WebSocket)
```

**Phase 2 — Optimization (Week 3–4)**

```
7. Sentence-boundary streaming (chunk LLM output → fire TTS per sentence)
8. Jitter buffer tuning per call quality (detect 2G/3G from RTP packet loss)
9. Per-region VAD threshold tables
10. Proper noun pronunciation dictionary (top 500 Indian bank/city/scheme names)
11. Emotion intensity → continuous prosody parameter (not just discrete preset)
```

**Phase 3 — Scale**

```
12. Self-hosted IndicF5 on Modal Labs (A100) for high-volume cost reduction
13. Voice persona library (3–5 branded voices per BPO client)
14. Dialect-aware register switching (metro / Tier-2 / Tier-3 profiles)
```

### Data Needed

| Data Asset | Volume | Purpose |
|-----------|--------|---------|
| Labeled call-center audio (emotion + prosody) | 10,000+ hours minimum | TTS fine-tune for expressive speech |
| Hinglish TTS training pairs (text + audio) | 500+ hours | Code-switching naturalness |
| Proper noun pronunciation dictionary | 5,000+ entries | Bank names, city names, schemes, product names |
| Adverse noise samples (Indian telecom) | 1,000+ hours | VAD tuning |
| Per-dialect Hindi samples (10+ dialects) | 100+ hours/dialect | Dialect-aware register |

**Available open-source:** AI4Bharat IndicVoices-R (22 languages, 9–175h/lang), INDICVOICES-R (NeurIPS 2024 benchmark)

### Eval Metric Gates — "Good Enough to Ship"

| Metric | Gate Threshold | Measurement Method |
|--------|---------------|-------------------|
| MOS naturalness (Hindi) | ≥ 4.0 / 5.0 | Crowdworker blind listening test, 50+ evaluators, 200+ samples |
| MOS naturalness (Hinglish code-mixed) | ≥ 3.8 / 5.0 | Same; code-mixed test set |
| TTFB (first audio chunk) | ≤ 250ms P90 | Automated latency harness, 1000 runs |
| Barge-in flush time | ≤ 80ms P95 | Synthetic barge-in test (inject voice while TTS playing) |
| False barge-in rate | ≤ 3% | VAD stress test with Indian ambient noise samples |
| CER on numerics / abbreviations | ≤ 5% | ASR-based character error rate on TTS output of financial text |
| Emotion match rate | ≥ 80% | Human rater: does voice tone match expected emotion label? |
| Proper noun accuracy | ≥ 90% | Curated list of 100 critical proper nouns, human listening |
| Compliance script intelligibility | 100% | Every mandatory disclosure intelligible and complete — zero tolerance |

---

## 11. India Specifics

### Language Coverage Priority
1. **Hindi** — 44% of India population; highest BPO volume; Hinglish dominant in urban/semi-urban
2. **Tamil** — major south India BPO hub; Chennai call centers
3. **Telugu** — Hyderabad BPO cluster
4. **Kannada** — Bengaluru IT/BPO adjacent
5. **Marathi** — Mumbai financial services
6. **Bengali** — Kolkata BPOs + rural banking
7. **Gujarati** — MSME/banking segment
8. **Malayalam** — NRI remittance segment
9. **Punjabi** — NBFCs, rural credit
10. **Odia, Assamese** — government/fintech expansion in eastern India

### Hinglish Nuances for TTS

- **Transliteration trap:** Never convert English words to Devanagari for pronunciation — "payment" should sound English, not "पेमेंट" (paymENT with Hindi stress)
- **Lakh/crore** must always be pronounced in Indian English convention, not million/billion — "ek lakh pachees hazaar" never "one hundred and twenty-five thousand"
- **Register-mixing markers:** "toh", "matlab", "matlab yeh hai ki", "dekho" are Hindi social pragmatics — TTS must deliver these with appropriate prosodic weight (not stressed too heavily)
- **Respect forms:** "aap" forms of verbs must be pronounced with correct Hindi vowel lengths — short cuts ("ap" vs "aap") signal disrespect

### Regulatory / Compliance TTS Requirements

| Regulator | Requirement | TTS Implementation |
|-----------|------------|-------------------|
| DPDP Act 2023 | Disclosure at call start: "Yeh call record ki ja sakti hai..." | Pre-recorded or TTS-rendered mandatory opening; logged with timestamp |
| TRAI DLT | AI-generated calls must identify as such; "Yeh ek AI voice assistant hai..." | Mandatory preamble in natural TTS; no deceptive human voice mimicry |
| RBI FPC (Fair Practices Code) | Human escalation option must be offered at least once per call | TTS must pronounce "Kisi insaan se baat karne ke liye 0 daba'ein" clearly and slowly |
| IRDAI (Insurance) | Sales call must be recorded; consent notification mandatory | Consent TTS delivered at call start; recording flag in metadata |
| IRDAI (mis-selling) | Premium amounts, exclusions must be stated clearly | TTS rates these segments 20% slower; emphasis on critical terms |

**DPDPA Rules 2025 (notified Nov 2025, enforcement May 2027):** Full data residency required. TTS processing must happen on India-hosted infrastructure — eliminates ElevenLabs (US-hosted) as sole vendor without a data-processing agreement and India region.

### Telephony-Specific India Notes

- **8kHz G.711:** Most Indian PSTN calls are still 8kHz — TTS must be tested at this codec, not just 48kHz studio quality. Sarvam Bulbul V3 explicitly benchmarked and wins at 8kHz telephony.
- **Telecom noise floor:** Auto-rickshaw sounds, construction noise, roadside calls — VAD must be tuned for this, not US office environments.
- **2G/3G connectivity (Tier-3):** Significant packet loss — jitter buffer must be 300–400ms for rural calls vs 100ms for metro VoIP.
- **TATA Tele / Exotel / Airtel IQ:** Primary Indian telephony providers for BPOs — ensure TTS bridge tested against these SIP stacks, not just Twilio.
- **Call recording retention:** IRDAI mandates 6 months; store TTS output (text + audio) for audit trail.

### Cost Reality Check (India BPO Context)

| Option | Cost/minute (TTS layer only) | Notes |
|--------|-----------------------------|----|
| Sarvam Bulbul V3 (API) | ~₹0.30–0.50/min estimated | No public pricing; contact for enterprise |
| ElevenLabs | ~₹0.80–1.20/min | Character-based pricing; higher at Indian call volumes |
| Gnani (platform) | ₹2.40–4.80/min all-in (TTS+STT+orchestration) | Enterprise contract |
| Self-hosted IndicF5 (Modal) | ~₹0.08–0.15/min at scale | GPU amortized; requires ML ops |

At 100K minutes/month, the difference between managed API and self-hosted is ₹15–35 lakh/year — material for mid-market BPO economics.

---

## 12. References

- [Sarvam Bulbul V3 Launch Blog](https://www.sarvam.ai/blogs/bulbul-v3)
- [AI4Bharat Indic Parler-TTS — HuggingFace](https://huggingface.co/ai4bharat/indic-parler-tts)
- [Gradium TTS Latency Benchmark 2026](https://gradium.ai/content/tts-latency-benchmark-2026)
- [AutoProsody arXiv 2502.09661](https://arxiv.org/abs/2502.09661)
- [FutureAGI Voice AI Barge-In Guide 2026](https://futureagi.com/blog/voice-ai-barge-in-turn-taking-2026/)
- [Caller Digital — Voice AI India vs Global](https://www.caller.digital/blog/voice-ai-india-vs-global-platforms)
- [DPDP / RBI / IRDAI / TRAI Compliance Guide](https://www.autointerviewai.com/blog/ai-calling-india-dpdp-trai-dlt-compliance-complete-guide-2026)
- [Gnani.ai — Vachana TTS](https://www.gnani.ai/resources/blogs/indian-ai-voice-generator-with-breakthrough-secure-voice-technology)
- [Vernacular/Code-switching voice agents 2026](https://www.autointerviewai.com/blog/vernacular-ai-voice-agents-india-hinglish-code-switching-2026)
- [AI4Bharat IndicVoices-R NeurIPS 2024](https://proceedings.neurips.cc/paper_files/paper/2024/file/7dfcaf4512bbf2a807a783b90afb6c09-Paper-Datasets_and_Benchmarks_Track.pdf)
- [IndicF5 HuggingFace](https://huggingface.co/ai4bharat/IndicF5)
- [ElevenLabs vs Cartesia TTS 2026](https://futureagi.com/blog/elevenlabs-vs-cartesia-tts-2026/)
- [Coval — Best TTS Providers 2026](https://www.coval.ai/blog/best-text-to-speech-providers-in-2026-how-to-choose-(and-why-vendor-benchmarks-lie)/)
- [AssemblyAI — Top TTS APIs 2026](https://www.assemblyai.com/blog/top-text-to-speech-apis)
- [Voice AI India Regulatory Map 2026](https://www.caller.digital/blog/voice-ai-india-regulatory-map-2026)

---

*Document complete. Engineer can build from this. No further research needed for initial deployment.*
