# Voice Realism Deep Dive: Making Aria Sound ALIVE
## Research Brief for Aria — Friendly Indian Peer Voice AI Character

**Date:** 2026-05-27
**Scope:** Micro-acoustics of human speech → 2026 TTS capabilities → Sesame Maya effect → Emotional arc orchestration → Hinglish/Indian voice → Emotion detection → Architecture

---

## Section 1 — The Micro-Acoustics of Believable Human Speech

### What flat TTS misses: 10 phenomena

---

### 1.1 Breathing

**The science:**
Human speech breathing follows a fundamentally different pattern than rest-breathing. Speakers inhale rapidly (0.2–0.5s) at clause boundaries and exhale slowly across utterances. Audible inhalation is not a bug — it is a cue to listeners that a new thought is incoming. A "breath catch" (brief, arrested inhale) is a reliable acoustic marker of surprise or vulnerability. Sighs (long controlled exhalations with a falling pitch contour) signal emotional release, resignation, or intimacy.

Research on nonverbal vocalisations (Trouvain & Campbell, ICPhS 2014) identifies breath sounds as a distinct phonetic category with communicative function — listeners correctly decode their pragmatic meaning even without accompanying words.

**What TTS misses:** Complete silence between sentences, then immediate word onset. No transition — the robot cuts straight to speech.

**Reference:** Podcast application: In Joe Rogan's interviews, the intake breath before "Look — " signals disagreement incoming. On Conan O'Brien's podcast, audible breath before a story establishes narrative gear-shift.

---

### 1.2 Fillers + Disfluencies

**The science:**
Corley & Stewart (2008) — University of Edinburgh — establish that "um" and "uh" are not errors but **signals**. "Uh" predicts a short delay (0.6s mean); "um" predicts a longer delay (1.0s mean). They are communicative meta-signals: "I'm still holding the floor, a longer thought is coming." Listeners who hear "um" actually wait longer and feel less impatient. [Cambridge Core, Journal of the International Phonetic Association]

Disfluencies are speaker-specific in their frequency and placement (MDPI, Languages, 2023). Some speakers cluster fillers at clause boundaries; others place them mid-noun-phrase during lexical retrieval. This individuality makes a character's disfluency pattern part of their identity.

Hindi/Hinglish fillers: "matlab...", "haan so...", "like yaar", "aur kya tha", "basically" (over-used by Indian urban youth). These are culturally indexed — they signal generation and register.

False starts ("I — I mean, it's not that — ") signal emotional activation or self-correction, which signals authenticity.

**Reference:** Conan O'Brien is a masterclass — he uses "I mean" and false starts when improvising something he finds genuinely funny, as a marker of real spontaneity vs rehearsed material.

---

### 1.3 Backchannels

**The science:**
Backchannels are listener responses ("mm-hmm", "right", "haan") produced WHILE the speaker talks, signalling attention, agreement, or empathy without taking the floor. Research at ACL and in COGSCI establishes that their timing is highly constrained: they appear at completion points (clause-final, or post a major intonation peak), not randomly. Misplaced backchannels (wrong timing) actually signal inattention.

Types: **continuers** ("mm-hmm" = keep going), **assessments** ("wow", "achha"), **acknowledgements** ("right", "I see"), **lexical repetitions** ("Paris? Oh wow").

For a voice AI, producing backchannels during user speech — not after — creates the feeling of presence. NVIDIA's PersonaPlex (2025) achieves this via a fully duplex model that runs a parallel backchannel generation stream.

**Reference:** Rime.ai resource on backchanneling; Retell AI implementation guide (2025).

---

### 1.4 Vocal Fry, Creak, Breathiness

**The science:**
Vocal fry (creaky voice / laryngealization) occurs in the lowest register of the voice, around 7–78 Hz vs modal speech at 85–265 Hz (Wikipedia; ASHA Journal). The vocal folds are less tense, vibrating in a slow, irregular pattern creating a "creaking" sound. It appears most commonly:
- At the END of sentences (especially in American female speech)
- In unstressed syllables
- When expressing intimacy or casualness

Entrainment research (ScienceDirect, 2016) shows interlocutors unconsciously mirror each other's fry patterns — it builds rapport.

Breathiness (elevated H1-H2 ratio, increased aspiration noise) signals **intimacy, vulnerability, tiredness, flirtation**. Research on breathy and whispery voice in dialogue (EURASIP Journal on Audio, Speech) identifies breathy voice as appearing more in intimate dyads.

**What this means for Aria:** Ending phrases in slight vocal fry signals casualness and comfort. Shifting to breathier register when saying something vulnerable ("I've felt that way too...") marks intimacy.

---

### 1.5 Speech Rate Variation

**The science:**
Baseline conversational English: 140–160 WPM. Excited speech: 160–220 WPM. Slow, emphatic speech: 100–130 WPM. Emotional speech slows for grief/vulnerability and accelerates for excitement/nervousness.

Rate varies at the SYLLABLE level (syllables/second), not just at word count. English averages 5.3 syllables/second in casual conversation. Rate spikes happen over 2–3 syllables at peak excitement moments; rate drops are often single-syllable emphasis (stressed monosyllables stretched to 2x their normal duration).

**The key pattern:** Acceleration → peak moment → sudden slow-down for the punchline. This is the "comedic timing" pattern. Rogan interviewers notice: build at rate, then land the punchline slower than the setup.

---

### 1.6 Pause Variety

**The science:**
Research distinguishes at least four functionally distinct pauses (MDPI Languages 2023; ScienceDirect):

| Pause Type | Duration | Acoustic Marker | Function |
|-----------|----------|----------------|----------|
| **Micro-pause** | 0–250ms | Silent | Clause boundary; articulatory |
| **Hesitation pause** | 250–600ms + filled | Often + filler ("uh") | Lexical retrieval |
| **Pre-thought pause** | 400–900ms silent | No filler, slight breath | Cognitive formulation — new idea incoming |
| **Emotional pause** | 800ms–2s+ | May include breath-catch | Processing, vulnerability, emphasis |
| **Comedic pause** | Variable — deliberate | Silence before punchline | Timing device |

Listeners use pause + pitch reset + final lengthening as boundary cues. Pauses that fall at prosodically unexpected locations signal hesitation/vulnerability more powerfully than those at expected boundaries.

---

### 1.7 Pitch Contour

**The science:**
The standard inventory of intonation patterns includes: falling (declarative finality), rising (yes/no question or request for confirmation), fall-rise (hedging, challenge), rising-falling (surprise/impressed), and level (continuation).

Indian English specifically features: narrower overall pitch range than American English, retroflex consonants that change preceding vowel formants, and syllable-timed rhythm (more equal syllable duration vs stress-timed English). Uptalk (rising contour on declaratives) in Indian English often signals engagement and friendliness, not uncertainty.

"Sing-song teasing" = rapid rise-fall-rise pitch oscillation, often faster-than-speech-rate, used for playful mock-accusation ("You literally didn't call me back. Did you?").

Low-pitch warm register: F0 drops below speaker's modal pitch, often with slower rate and reduced amplitude — the "telling you a secret" register.

---

### 1.8 Volume Dynamics

**The science:**
Amplitude variation in natural speech spans ~15–20 dB within a single conversation. Key patterns:
- **Confidential whisper:** -15 to -20 dB below modal, breathy noise floor increases
- **Emphatic stress:** +5 to +8 dB above modal on target syllable, plus lengthening
- **Laughter:** unpredictable amplitude spikes (uncontrolled exhalation)
- **Building excitement narrative:** +2 to +3 dB per sentence in a sequence, peaks at climax

Film and podcast reference: Marc Maron on WTF drops to near-whisper when sharing something painful, then builds back up to normal. The volume arc tracks the emotional arc.

---

### 1.9 Laughter Types

**The science:**
Research (Cognitive Processing/Springer 2023; PMC Laughter Perception Network 2013) identifies:

| Type | Acoustic Signature | Function |
|------|-------------------|----------|
| **Mirthful/genuine** | Voiced, irregular amplitude, high F0, vowel-like bursts (Ha Ha) ~75ms each | Real amusement |
| **Polite laugh** | Shorter, more regular, lower amplitude, faster repetition rate | Social acknowledgement |
| **Embarrassed/nervous** | Breathy, nasal, quiet, often pre-emptive (before the punchline) | Deflection |
| **Snort laugh** | Nasal ingressive burst followed by voiced laughter | Involuntary, surprise-amusement |
| **Breathy laugh** | High-frequency aspiration noise dominant, barely voiced | Intimacy, affectionate |
| **Chuckle** | 1–3 laugh calls only, quiet | Mild amusement |

Female laughter: mean F0 ~502 Hz. Male: ~276 Hz. Genuine laughter has more irregular timing; fake/polite laughter is more metronomic (Columbia LABROSA acoustic analysis).

**Key implementation insight:** Polite laugh ≠ real laugh. Aria using polite laughs when something isn't that funny, and genuine bursts when something actually lands, is a high-realism signal.

---

### 1.10 Smile-in-Voice

**The science:**
Phonetics research (ICPhS 2015, Torre et al. 2013 York) has documented measurable acoustic changes when speakers smile:
- Significant increase in F0 (fundamental frequency) — smiling raises pitch
- Increase in intensity (amplitude)
- Increase in F2 formant for rounded vowels (shorter vocal tract effect noted by Ohala 1980)
- Slightly faster rate (smiling involves muscle tension that speeds articulation)

Perceptual experiments confirm listeners can reliably identify smiled speech from audio alone at above-chance accuracy. The "warm smile voice" has a specific fingerprint: slight F0 elevation, more forward mouth position (higher formants), soft onset (no glottal attack), and gentle amplitude on consonants.

---

## Section 2 — 2026 TTS Systems: Phenomenon-by-Phenomenon

### Master Comparison Table

| Phenomenon | ElevenLabs v3 | Sesame CSM-1B | Inworld TTS-2 | Hume EVI-3/4 | Cartesia Sonic-3 | OpenAI gpt-4o Realtime | Suno Bark | Sarvam Bulbul V3 |
|-----------|--------------|---------------|---------------|-------------|-----------------|----------------------|-----------|-----------------|
| **Breathing** | `[breath]`, `[breathes]` | Emergent from context (not explicit) | `[breathe]` (first-class) | Natural via eLLM | Limited | Natural pacing only | Limited | Not documented |
| **Fillers (um/uh)** | Include in text | Emergent — baked into model | Auto + context | Via emotional LLM | Via text injection | "Speak naturally" style | Direct in text | Limited |
| **Backchannels** | Not native | Not native | Not native | EVI duplex approach | Not native | Advanced Voice Mode partial | No | No |
| **Vocal fry** | `[resigned tone]` approximate | Emergent | Prose direction "tired, flat" | Prosody model | `[tired]` tags | Style instruction | No | No |
| **Breathiness** | `[whispers]` adjacent | Contextual | "soft, breathy" prose | Measures H1-H2 analog | Emotive voices | Emotion styles | No | No |
| **Rate variation** | `[rushed]`, `[slows down]`, `[deliberate]` | Context-driven | Inline prose | eLLM-driven | Speed dials | Instruction-driven | No explicit | No |
| **Pause variety** | `[pause]`, `[hesitates]`, `[stammers]` | Context emergent | `[pause]` + prose | Prosody-driven | SSML breaks | Limited control | Limited | No |
| **Pitch contour** | Limited direct control | Emergent | Prose direction | eLLM prosody | Emotive tag | Style instruction | No | No |
| **Volume dynamics** | `[whispers]`, `[shouts]` | Contextual | Prose + `[whisper]` | eLLM | Volume dial | Style instruction | No | No |
| **Laughter types** | `[laughs]`, `[laughs softly]` | Emergent (trained on real laughter) | `[laugh]` (audio event) | EVI vocalization model | `[laughs]` | Partial | Yes (direct) | No |
| **Smile-in-voice** | `[cheerfully]`, `[happily]` | Contextual | Prose: "warm smile" | eLLM prosody | Emotive voices | Style instruction | No | No |
| **Hinglish support** | Good (multilingual v3) | English only | Limited | Limited | Limited | Partial | Limited | NATIVE (best) |

---

### ElevenLabs v3 — Full Audio Tag Reference

Source: [ElevenLabs Blog — v3 Audio Tags](https://elevenlabs.io/blog/v3-audiotags)

**Emotional tags:** `[excited]`, `[sad]`, `[angry]`, `[happily]`, `[sorrowful]`, `[nervous]`, `[tired]`, `[awe]`, `[cheerfully]`, `[flatly]`, `[deadpan]`, `[playfully]`

**Delivery/volume:** `[whispers]`, `[shouts]`, `[x accent]`

**Nonverbal reactions:** `[sigh]`, `[sighs]`, `[laughs]`, `[laughs softly]`, `[gulps]`, `[gasps]`, `[clears throat]`

**Cognitive beats:** `[pauses]`, `[hesitates]`, `[stammers]`, `[resigned tone]`

**Pacing:** `[pause]`, `[breathes]`, `[continues after a beat]`, `[rushed]`, `[slows down]`, `[deliberate]`, `[rapid-fire]`

**Rhythm/hesitation:** `[drawn out]`, `[repeats]`, `[timidly]`

**Emphasis:** `[emphasized]`, `[stress on next word]`, `[understated]`

**Identity:** `[childlike tone]`, `[deep voice]`, `[robotic tone]`

**Sound FX:** `[clapping]`, `[explosion]`, `[gunshot]`, `[door creaks]`, `[bird chirping]`

Tag library contains ~2,000 tags. Model interprets anything in `[ ]`. Tags persist until overridden.

---

### Inworld TTS-2 — The Director Model

Source: [Inworld Realtime TTS-2 Blog](https://inworld.ai/blog/realtime-tts-2), [Replicate](https://replicate.com/inworld/realtime-tts-2)

This is currently the most "director-like" TTS interface. Key differentiators:

1. **Natural language system prompt steering**: You write "tired but warm, like she just got home from a long day" — not tags.
2. **Audio context conditioning**: Model hears previous conversation audio and adapts tone.
3. **Five first-class non-verbal cues** that render as actual audio events: `[laugh]`, `[sigh]`, `[breathe]`, `[clear_throat]`, `[cough]`
4. **Disfluency awareness**: Automatically incorporates "uh", "um" and self-corrections when steered toward casual/warm.
5. **Latency**: Sub-200ms median time-to-first-audio.

Example system prompt for Aria: `"Warm, curious, slightly breathless — like a college friend who just heard something interesting. Speaks in Hinglish, drops to a whisper for confessions, laughs often but genuinely."`

---

### Sesame CSM-1B — The "Born Conversational" Model

Source: [Sesame Research Blog](https://www.sesame.com/research/crossing_the_uncanny_valley_of_voice), [TechCrunch](https://techcrunch.com/2025/03/13/sesame-the-startup-behind-the-viral-virtual-assistant-maya-releases-its-base-ai-model/), [HuggingFace](https://huggingface.co/sesame/csm-1b)

Why Maya sounds different: The model doesn't just convert text to audio — it **processes the full conversation history as multimodal input** (interleaved text + audio tokens). Each utterance is generated with awareness of the prior utterances' prosody. The "one-to-many problem" (any sentence can be said countless valid ways) is resolved by using context.

Technical: Two-stage Llama backbone + audio decoder operating on RVQ/Mimi codes. 24kHz output. 2B parameters.

**What it gets right:** Micro-pauses, emphasis variation, laughter that emerges from context, self-corrections that feel natural — all emergent from training data, not tag injection.

**Key limitation:** English only (training = DailyTalk dataset). No explicit filler API. Requires GPU for inference. Not production-API-ready as of Q1 2026 — base model only, requires fine-tuning for specific character voice.

**The "presence" concept:** Sesame defines presence as the quality of interaction where users feel "real, understood, and valued." Their current research note is honest: human evaluators still prefer original human recordings when they hear the context. The gap is in "fully duplex" turn-taking — the model cannot currently model who should speak when.

---

### Hume EVI-3 / EVI-4 Mini — The Emotion-First Stack

Source: [Hume Blog EVI-3](https://www.hume.ai/blog/announcing-evi-3-api), [Hume Dev Docs](https://dev.hume.ai/docs/speech-to-speech-evi/overview)

**What's current:** EVI 1+2 sunset August 2025. EVI 3 released May 2025. EVI 4-mini with multilingual (including Hindi) active as of January 2026.

**Unique capability:** The only production API that:
1. Measures 48 emotional dimensions from the USER's vocal prosody (pitch, pace, intensity, timbre)
2. Responds with emotionally-matched prosody — not just content matching
3. Sends `assistant_prosody` messages as a side-channel for inspection

This is the critical insight: Hume closes the loop. It doesn't just output emotion — it READS input emotion and calibrates output accordingly.

**For Aria:** If user voice is trembling (Hume detects nervousness/sadness), Aria's response automatically softens. If user laughs, Aria leans into it. This happens at the model level — not in prompting.

---

### Cartesia Sonic-3

Source: [Cartesia Sonic-3 Docs](https://docs.cartesia.ai/build-with-cartesia/tts-models/latest), [Cartesia.ai](https://cartesia.ai/sonic)

Sub-200ms latency, 27 languages, emotion tags, SSML support. Voices tagged as "Emotive" for expressive use cases. Speed/volume dials available. Native laughter support. Good for voice agent scaffolding — more "plumbing-ready" than character-first.

---

### OpenAI gpt-4o Realtime / Advanced Voice

Source: [OpenAI Realtime Intro](https://openai.com/index/introducing-gpt-realtime/)

232ms average response latency. Handles interruptions natively. Style instructions work ("speak empathetically", "use a warm tone"). Natural pacing and intonation improvements in gpt-realtime release. Can switch languages mid-sentence. Partial Hinglish handling.

**The limitation:** No fine-grained audio tag control. You steer via text instruction, not markers. Realism is good but character consistency requires very careful system prompting.

---

### Suno Bark — Open Source Baseline

Source: [Suno Bark GitHub](https://github.com/suno-ai/bark), [HuggingFace](https://huggingface.co/suno/bark)

Bark is the open-source foundational demonstration. Supports: `[laughs]`, `[sighs]`, `[gasps]`, `[clears throat]`, and direct filler injection in text ("and, uh —"). MIT licensed. Multilingual but quality below commercial. Shows the principle — fillers and non-verbals CAN be baked into a TTS model via training, not post-processing.

---

### Tortoise TTS / XTTS

Tortoise: extremely high quality but slow (not real-time without heavy optimization). XTTS v2: cross-lingual voice cloning, GPT2-based decoder. Both require GPU. Good for pre-recorded character voice but not live conversation. Orpheus (March 2025, Canopy AI, Llama-3B based) is the new open-source challenger with better realtime performance.

---

### Best-in-Class by Phenomenon (2026)

| Use Case | Winner | Rationale |
|---------|--------|-----------|
| **Laughter** | ElevenLabs v3 | Most laughter tag variants, most tested |
| **Breathing** | Inworld TTS-2 | First-class `[breathe]` as audio event |
| **Hesitation/fillers** | Sesame CSM (fine-tuned) | Emergent, context-aware, most natural |
| **Emotion arc** | Hume EVI-3 | Only model that reads + responds to user emotion |
| **Character consistency** | ElevenLabs v3 | Voice cloning + stable persona across session |
| **Hinglish/Indian** | Sarvam Bulbul V3 | Purpose-built, code-switching native |
| **Director-style control** | Inworld TTS-2 | Natural language steering, not tag library |
| **Latency** | Cartesia Sonic-3 / Inworld TTS-2 | Both sub-200ms |

---

## Section 3 — The Maya Effect: What Sesame Got Right

### Research paper: "Crossing the Uncanny Valley of Voice"

Source: [Sesame Research](https://www.sesame.com/research/crossing_the_uncanny_valley_of_voice)

Sesame's published framing of why Maya went viral:

**1. The One-to-Many Problem:**
Any text can be spoken an infinite number of valid ways. Prior TTS systems collapse this to one "average" rendering. CSM resolves it by conditioning on full conversation history — the system has heard how the human has been speaking and calibrates accordingly.

**2. Dual-Token Architecture:**
CSM operates on both "semantic tokens" (speaker-invariant linguistic content) and "acoustic tokens" (speaker-specific fine-grained characteristics). This dual representation preserves prosodic richness while enabling variation.

**3. Micro-level naturalism:**
The training on DailyTalk conversational data means the model has internalized: micro-pauses, emphasis shifts, laughter, self-corrections. These aren't post-processed in — they emerge from learned conversational dynamics.

**4. The Gap They Acknowledge:**
Sesame's own evaluation: "When evaluators heard context, they consistently favor original recordings." The remaining gap is turn-taking: who speaks when, pacing across a full conversation. They identify "fully duplex models" as the next frontier — models that can simultaneously listen and speak, learning turn-taking dynamics implicitly.

### Why Maya's fillers feel different from ElevenLabs

ElevenLabs fillers are injected via tags — they are rendered correctly but they don't emerge from the AI's "thinking." Maya's "um..." emerges from the model's internal generation process — it's a real output of indeterminacy in the model's token prediction. It correlates to the model's actual uncertainty about what comes next. Users perceive this as authentic hesitation vs performed hesitation.

### "Voice Presence" defined

Sesame's term: the quality that makes interaction feel "real, understood, and valued." Their four components:
1. **Emotional intelligence** — matching the emotional register of the user
2. **Conversational dynamics** — natural timing, pauses, emphasis
3. **Contextual awareness** — prior turns shape current output
4. **Consistent personality** — coherent character across the conversation

### Sesame in 2026 — Product Status

As of Q1 2026: CSM-1B base model is open-source on HuggingFace (March 2025 release). The fine-tuned Maya/Miles personas are NOT publicly available. Sesame is building toward a consumer voice product. No production API available for third-party integration as of May 2026. [unverified — check sesame.com for latest API status]

**What Boss can borrow:** The architecture principle — use conversation history as audio context, not just text context. This is implementable TODAY by passing prior audio segments as context to CSM-1B (or ElevenLabs if they expose audio conditioning in API).

---

## Section 4 — Emotional Arc in a 15-Minute Conversation

### 4.1 The Four-Phase Arc

Research on emotion dynamics in film dialogues (arXiv 2103.01345; PMC) shows that engaging extended interactions follow a recognizable emotional contour. Applying this to a 15-minute AI voice conversation:

```
Phase 1 — Opening (min 0-3): Cool curiosity
├── Register: Brighter pitch, faster rate, warm but surface-level
├── Aria signals: Interest, slight energy, professional warmth
├── Goal: Establish rapport, signal safety for vulnerability later
└── Voice cues: Light uptalk, faster pace, smile-in-voice

Phase 2 — Warming (min 3-8): Growing intimacy
├── Register: Slightly slower, more relaxed, fillers increase
├── Aria signals: Real engagement, mild self-disclosure
├── Goal: Deepen to personal topics, match user's increasing openness
└── Voice cues: More vocal fry at sentence ends, deeper pitch register

Phase 3 — Climax (min 8-12): Peak engagement
├── Register: Vulnerable moments + genuine laughter peaks
├── Aria signals: Real emotion (surprise, delight, or empathy)
├── Goal: The "moment" — shared laugh, mutual vulnerability, or genuine insight
└── Voice cues: Volume drops for confessions, spike for laughter

Phase 4 — Closing (min 12-15): Warm anticipation
├── Register: Slightly slower, lower, resonant warmth
├── Aria signals: Satisfaction, looking forward, genuine connection
├── Goal: Leave user wanting to return
└── Voice cues: Slower rate, more pause, lower pitch, minimal fry
```

### 4.2 Film/Theater Direction Craft

Source: [Fiveable Storytelling Film+TV, Emotional Pacing](https://library.fiveable.me/storytelling-for-film-and-television/unit-8/emotional-pacing/study-guide/2hCM51PFe7wkhnjR); [Voice Acting depth — Topher Keene](https://www.topherkeene.com/articles/beyond-the-cool-voice-how-to-add-real-depth-to-your-voice-acting)

From film direction:
- **Dynamic variation**: Alternate high-intensity and quiet introspective moments. A scene that stays at one energy level loses audience attention after ~90 seconds.
- **Emotional anchoring**: The director's rule — an actor must find one specific "anchor moment" they feel genuinely — this makes all surrounding performance feel real. For AI: the system prompt must give Aria real "emotional memories" to anchor from.
- **Tension + release**: Disagreement or playful challenge followed by resolution creates dopamine cycling. Voice acting direction calls this "resist then yield."
- **The Slow Note**: Disco Elysium direction — "low and slow, not overact" for the Narrator. This applies to Aria's vulnerability moments — less is more.

### 4.3 Naughty Dog's Technique

Source: [Game Informer — Capturing Joel and Ellie](https://gameinformer.com/b/features/archive/2012/02/20/naughty-dog-39-s-art-of-performance-with-last-of-us.aspx)

Naughty Dog's key insight for The Last of Us voice direction:
- "We figure out what Ellie is SUPPOSED TO BE FEELING right now" — emotion state is the primary design variable, not words
- Director gave actors visceral physical anchor images ("you're in the attic, singing to a dead cat") — not emotional labels
- Ashley Johnson improvised 30% of her lines — emotional authenticity > script adherence
- Sound and voice arc follow Ellie's emotional arc, not the plot

**AI application:** Don't give the LLM emotion labels. Give it scenarios: "You just realized this person really needed to hear that from someone." The model's output will carry more authentic weight.

### 4.4 State Tracking Implementation

The emotion conductor layer needs to track these variables per conversation turn:

```python
aria_state = {
    "mood": "curious",          # curious | warm | intimate | playful | empathetic | excited
    "energy_level": 0.6,        # 0.0-1.0
    "relationship_depth": 12,   # 0-100 (starts at 0, increments per turn)
    "conversation_phase": "opening",  # opening | warming | climax | closing
    "user_last_emotion": "neutral",   # from Hume/Deepgram detection
    "recent_laugh": False,      # did laughter happen recently?
    "recent_vulnerability": False,    # was something vulnerable shared?
    "tension_active": False     # is there unresolved playful tension?
}
```

**Transition rules:**
- `relationship_depth` increments +2 per turn baseline, +5 if user shares personal info, +3 if mutual laughter
- `conversation_phase` advances when `relationship_depth` crosses thresholds (0-20=opening, 20-50=warming, 50-80=climax, 80-100=closing)
- `mood` shifts immediately (same-turn) when user emotion detection reads strong signal — this is "emotional anchoring"
- `energy_level` follows user's energy with a slight lag (1-turn delay) and a cap (Aria never exceeds user +0.2)

### 4.5 Tension + Release Pattern

Playful tease in voice:
- Rate increases slightly
- Pitch rises (sing-song)
- Volume stays consistent but emphasizes the "accusatory" word
- Voice: `[playfully]` or `[teasing]` tag

Resolution in voice:
- Rate drops
- Pitch returns to modal
- Softer onset on first word of resolution
- Voice: `[warmly]` + `[softer]` prose direction

---

## Section 5 — Hinglish + Indian Voice

### 5.1 What makes an Indian voice Indian

From phonetics research (AutoProsody paper arXiv 2502.09661; Speechify blog):
- **Retroflex consonants**: T, D, N produced with tongue curled back — this changes adjacent vowel formants
- **Dental /th/**: Indian English maps English /θ/ to dental /t̪/ — distinct from British or American
- **Syllable-timed rhythm**: More equal syllable duration (vs stress-timed English), creating the characteristic "even" pace
- **Narrower pitch range** overall
- **Rising intonation** on declaratives as engagement signal (not uncertainty)
- **Specific lexical items**: "only" as sentence-final emphasis ("I told you only"), "na?" as tag question, "itself" for emphasis

A Pune-raised voice vs Delhi-raised:
- Pune/Mumbai: Marathi-influenced, slightly more nasal, "ee" vowels slightly more front, slower overall pace
- Delhi: Hindi-influenced, harder consonants, faster rate, stronger retroflex
- Both: distinct from "generic Indian English" which blends these features [unverified — specific acoustic studies on city-level Indian English accent variation are limited]

### 5.2 TTS Systems Ranked for Hinglish

**Tier 1 — Purpose-Built for India:**

**Sarvam Bulbul V3** (February 2026)
- Source: [Sarvam Blog](https://www.sarvam.ai/blogs/bulbul-v3), [Yourstory](https://yourstory.com/ai-story/sarvam-ai-bulbul-v3)
- Trained from scratch on Indian speech patterns, not adapted
- Handles Hinglish, Tanglish, Benglish code-switching natively
- Lowest CER on code-mixed domain across all tested models
- Blind test: 77.95% listener preference in telephony-grade audio
- Beat ElevenLabs and Cartesia in India-specific evaluation (Josh Talks blind study, 2000+ votes/language)
- 11 languages: Hindi, Bengali, Tamil, Telugu, Gujarati, Kannada, Malayalam, Marathi, Punjabi, Odia + Indian English
- Streaming latency: 50% reduction in 2026 version

**AI4Bharat IndicF5 / Indic-Parler-TTS**
- Source: [HuggingFace IndicF5](https://huggingface.co/ai4bharat/IndicF5)
- Trained on 1417 hours (Rasa + IndicTTS + LIMMITS + IndicVoices-R)
- 11 Indian languages
- Near-human quality claim for Hindi
- Open-source (research-grade)

**Tier 2 — Adapted Global Platforms:**

**ElevenLabs Multilingual v3**
- Source: [ElevenLabs India page](https://elevenlabs.io/india)
- 12 Indian languages and accents
- Indian accent voices: retroflex, syllable-timing, dental /th/ — reported as authentic
- Code-switching quality: good for Hinglish where English dominates; weaker when Hindi dominates mid-sentence
- 10,000+ voice library includes Indian-accented voices

**OpenAI gpt-4o Realtime**
- Can switch languages within a sentence
- Hinglish partial — handles English-dominant Hinglish better than Hindi-dominant
- No fine-grained accent control

**Tier 3 — Not recommended for Hinglish:**
- Cartesia Sonic-3: 27 languages but India-specific quality [unverified]
- Sesame CSM-1B: English only

### 5.3 Cultural Micro-Tells in Voice

These are the acoustic+lexical markers that make an Indian urban voice culturally real:

| Marker | What it sounds like | When to deploy |
|--------|--------------------|----|
| **"Achha"** | Short rising-falling on first syllable, Punjabi-Hindi tonal marker | Understanding, mild surprise, "I see" |
| **"Haan"** | Open low vowel, can be nasal, mid-pitch | Backchannel agreement |
| **"Yaar"** | Soft palatal approximant, warm falling tone | Affection, solidarity |
| **"Na?"** | Rising intonation tag, seeking confirmation | Checking in, soft challenge |
| **"Matlab"** | Filled pause in mid-thought, slower onset | Hesitation, reformulation |
| **"Only" sentence-final** | Normal word but sentence-final, emphatic | Indian English emphasis particle |
| **Code-switch** | Smooth — no accent change on English words | Natural Hinglish cadence |

**The key rule:** A believable Hinglish voice does NOT sound like an accent — it sounds like a person whose mother tongue is Hindi but who is fully fluent in English, and the two languages coexist. The accent is not a filter over English; it is a native prosodic system that generates both.

---

## Section 6 — User Voice Input: Emotion Detection

### 6.1 What's Actually Possible in 2026

**Hume EVI-3/4 — The Gold Standard for Emotion Detection**
- Source: [Hume Dev Docs — Expression Measurement](https://dev.hume.ai/docs/expression-measurement/overview), [Hume Prosody Model](https://dev.hume.ai/docs/expression-measurement/models/prosody)
- 48 emotional dimensions measured from vocal prosody alone
- Derived from Cowen's semantic space theory (27-emotion taxonomy, extended)
- Measures: tone, rhythm, timbre of speech — NOT just word sentiment
- In EVI-3: `assistant_prosody` side-channel gives you the emotion scores per utterance
- Latency: ~300ms for emotion measurement alongside transcription
- What it detects from voice: admiration, adoration, aesthetic appreciation, amusement, anger, anxiety, awe, awkwardness, boredom, calmness, concentration, confusion, contempt, contentment, craving, desire, disappointment, disgust, distress, embarrassment, empathic pain, enthusiasm, envy, excitement, fear, guilt, horror, interest, joy, love, nostalgia, pain, pride, realization, relief, romance, sadness, satisfaction, shame, surprise (positive), surprise (negative), sympathy, tiredness, and more [unverified — exact 48 list not publicly documented in full]

**Deepgram — Best Latency for Transcription + Basic Sentiment**
- Source: [Deepgram Real-Time Sentiment](https://deepgram.com/learn/real-time-sentiment-analysis-streaming-audio)
- Sub-100ms STT latency, end-to-end under 300ms
- Sentiment: positive/negative/neutral on utterances
- Prosody markers: pause detection, utterance boundary via prosodic shifts
- Limited to valence (positive/negative) — not the nuanced 48-dimension Hume model
- Best choice if Hume latency is too high and you need basic emotion signal

**AssemblyAI — Intelligence Layer Approach**
- Source: [AssemblyAI Voice Stack 2026](https://www.assemblyai.com/blog/the-voice-ai-stack-for-building-agents)
- STT with "LeMur" intelligence layer — post-transcript LLM processing
- Sentiment analysis, intent recognition, topic detection
- Not real-time in the same sense — processes completed utterances, not streaming prosody
- Universal-2 model at ~14.5% WER

### 6.2 What Aria Can Do With Emotion Detection

```
If user voice shows:          Aria responds with:
------------------------      --------------------------
Nervousness (shaky pitch,    Slower pace, softer volume
fast rate, rising F0)        "hey, no pressure at all..."
                             [breathy] [gentle]

Laughter (irregular          Lean in with own laughter
amplitude, high F0 bursts)   Speed up slightly, energy up
                             [amused] [warm]

Flat/dismissive (narrow      Light playful challenge
pitch range, low energy,     "wait, I need to push back on
slow pace)                   that actually..."
                             [playfully]

Sadness (slow rate,          Immediate soften
falling pitch, long pauses)  Volume drops, rate drops
                             "hey... [pause] that's real."
                             [soft] [intimate]

Excitement (fast rate,        Match energy, escalate
high F0, amplitude spikes)    "YES — okay I love this"
                              [excited] [laughs]
```

### 6.3 Latency Reality

For a production voice AI conversation with emotion detection:
- Hume EVI pipeline: ~300ms total (emotion detection embedded)
- Deepgram STT + separate emotion model: ~250ms STT + ~150ms emotion = ~400ms before LLM
- Target for natural conversation: under 500ms end-to-end (user stops → Aria starts)
- Practical architecture: Hume EVI-4 for the speech-to-speech layer (handles STT + emotion + TTS in one pipeline) is the lowest-friction path

---

## Section 7 — The Voice Orchestration Architecture

### 7.1 Full System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                          USER VOICE INPUT                           │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    STT + EMOTION DETECTION LAYER                     │
│                                                                     │
│  Primary: Hume EVI-4 (handles STT + 48-dim emotion simultaneously) │
│  Fallback: Deepgram STT (sub-100ms) + basic sentiment               │
│                                                                     │
│  Outputs:                                                           │
│    - transcript: "I've been feeling kind of off lately"             │
│    - emotion_scores: {sadness: 0.72, tiredness: 0.61, ...}         │
│    - prosody_features: {pace: "slow", pitch: "falling", ...}       │
│    - dominant_emotion: "sadness"                                    │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     EMOTION CONDUCTOR (State Manager)               │
│                                                                     │
│  aria_state = {                                                     │
│    "mood": "warm",           # current output mode                 │
│    "energy": 0.45,           # 0.0-1.0                             │
│    "relationship_depth": 34, # 0-100                               │
│    "phase": "warming",       # opening/warming/climax/closing       │
│    "user_emotion": "sadness",# detected this turn                  │
│    "user_energy": 0.3,       # detected user energy                │
│    "recent_laugh": False,                                           │
│    "recent_vulnerability": True,                                    │
│    "tension_active": False                                          │
│  }                                                                  │
│                                                                     │
│  State transitions (per turn):                                      │
│    1. Update user_emotion from detection                            │
│    2. Update user_energy from prosody                               │
│    3. Apply mood shift rules (immediate if strong signal)           │
│    4. Increment relationship_depth                                  │
│    5. Advance phase if depth threshold crossed                      │
│    6. Compute aria target_energy = min(user_energy + 0.2, 1.0)    │
│    7. Output: voice_direction_descriptor                            │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     LLM (Claude Haiku) — Content + Direction        │
│                                                                     │
│  SYSTEM PROMPT includes:                                            │
│    - Aria's character definition                                    │
│    - Current aria_state (JSON)                                      │
│    - voice_direction_descriptor                                     │
│    - Conversation history (last N turns)                            │
│                                                                     │
│  OUTPUT FORMAT:                                                     │
│  {                                                                  │
│    "speech": "[soft] [slows down] You know what, [breathe]         │
│               that makes a lot of sense. [pause] More than          │
│               I think you realize.",                                │
│    "tts_system_direction": "warm, slightly breathy, careful         │
│                             pacing, like someone who understands",  │
│    "mood_update": "intimate",                                       │
│    "energy_update": 0.3                                             │
│  }                                                                  │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     TTS LAYER                                        │
│                                                                     │
│  Primary: ElevenLabs v3 (if ElevenLabs + Sarvam hybrid for Hindi) │
│       OR: Inworld TTS-2 (if natural language direction preferred)  │
│       OR: Sarvam Bulbul V3 (if Hinglish-dominant utterances)      │
│                                                                     │
│  Input: speech text with audio tags + tts_system_direction         │
│  Output: audio stream (streaming, first chunk < 200ms)             │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     AUDIO → USER                                     │
│                                                                     │
│  + Backchannel injection if user is mid-speech (duplex mode)        │
│  + Aria's state updated for next turn                               │
└─────────────────────────────────────────────────────────────────────┘
```

---

### 7.2 LLM Prompt: The Emotion Conductor System Prompt

```
You are Aria, a friendly Indian peer voice AI. You are in a voice conversation.

CURRENT ARIA STATE:
{aria_state_json}

VOICE DIRECTION PRINCIPLES:
- Your response is spoken, not text. Write for the ear.
- Use audio tags from ElevenLabs v3 format to direct delivery.
- Available tags: [breath], [breathes], [pause], [hesitates], [sighs], [laughs], 
  [laughs softly], [whispers], [soft], [warm], [excited], [drawn out], [slows down],
  [rushed], [playfully], [deadpan], [stammers]
- For Inworld TTS-2, prepend system direction in prose: 
  e.g. "warm and slightly breathless, leaning in"

PHASE-SPECIFIC VOICE NOTES:
- opening: bright, faster pace, light uptalk, smile-in-voice
- warming: more relaxed, slight vocal fry at sentence ends, occasional filler
- climax: full emotional range — real laughter, real softness for vulnerability
- closing: slower, lower pitch, resonant warmth, more pauses

EMOTION ANCHORING RULE:
If user_emotion is sadness/anxiety/vulnerability — shift to soft+slow IMMEDIATELY this turn.
If user_emotion is excitement/laughter — match their energy this turn.
If user_emotion is dismissive/flat — light playful challenge, do not match flat.

HINGLISH PATTERNS:
Use "haan", "achha", "yaar", "na?", "matlab...", "aur" where natural.
Do NOT force Hinglish every sentence — use it where it flows.

OUTPUT FORMAT:
Return JSON:
{
  "speech": "<text with inline audio tags>",
  "tts_direction": "<prose direction for TTS system prompt>",
  "mood_update": "<new mood word>",
  "energy_update": <float 0.0-1.0>
}
```

---

### 7.3 Mood State Machine

```python
MOOD_TRANSITIONS = {
    # (current_mood, user_emotion) -> new_mood
    ("curious", "excitement"): "excited",
    ("curious", "sadness"): "empathetic",
    ("warm", "sadness"): "intimate",
    ("warm", "excitement"): "playful",
    ("playful", "sadness"): "empathetic",  # immediate — override playful
    ("playful", "laughter"): "playful",    # maintain
    ("intimate", "excitement"): "warm",
    ("empathetic", "excitement"): "warm",
    ("excited", "sadness"): "empathetic",
}

PHASE_THRESHOLDS = {
    "opening":  (0,  25),
    "warming":  (25, 55),
    "climax":   (55, 80),
    "closing":  (80, 100),
}

RELATIONSHIP_DEPTH_INCREMENTS = {
    "baseline_per_turn": 2,
    "user_shares_personal": 5,
    "mutual_laughter": 3,
    "user_vulnerability": 4,
    "disagreement_resolved": 3,
}

VOICE_DIRECTION_BY_PHASE = {
    "opening": {
        "tts_direction": "bright and curious, warm smile in voice, slightly faster pace",
        "energy_baseline": 0.65,
        "filler_rate": "low",
        "fry_rate": "minimal",
    },
    "warming": {
        "tts_direction": "relaxed and engaged, occasional um/uh, slight fry at sentence ends",
        "energy_baseline": 0.55,
        "filler_rate": "medium",
        "fry_rate": "light",
    },
    "climax": {
        "tts_direction": "full emotional range — genuine laughs, real softness for vulnerability",
        "energy_baseline": 0.5,  # variable — follows emotion
        "filler_rate": "high (natural)",
        "fry_rate": "present in intimate moments",
    },
    "closing": {
        "tts_direction": "slower, lower, resonant warmth, longer pauses, no rush",
        "energy_baseline": 0.45,
        "filler_rate": "low",
        "fry_rate": "light",
    },
}
```

---

### 7.4 Sample Implementation Pseudocode

```python
class AriaVoiceOrchestrator:
    def __init__(self):
        self.state = AriaState()
        self.hume_client = HumeEVIClient()
        self.llm = ClaudeHaikuClient()
        self.tts = ElevenLabsV3Client()  # + SarvamBulbulV3 for Hindi utterances
        self.history = ConversationHistory()

    async def process_turn(self, user_audio: bytes) -> bytes:
        # Step 1: STT + Emotion Detection (parallel)
        transcript, emotion_scores = await self.hume_client.analyze(user_audio)
        dominant_emotion = max(emotion_scores, key=emotion_scores.get)
        user_energy = compute_energy_from_prosody(emotion_scores)

        # Step 2: Update state
        self.state.update(
            user_emotion=dominant_emotion,
            user_energy=user_energy,
            turn_content=transcript
        )

        # Step 3: LLM content + voice direction
        llm_response = await self.llm.chat(
            system=build_system_prompt(self.state),
            messages=self.history.get_context(),
            user_message=transcript
        )
        parsed = json.loads(llm_response)

        # Step 4: Language detection for TTS routing
        if is_hindi_dominant(parsed["speech"]):
            tts_provider = self.sarvam_client
        else:
            tts_provider = self.tts  # ElevenLabs for English/Hinglish

        # Step 5: TTS with direction
        audio = await tts_provider.synthesize(
            text=parsed["speech"],
            system_direction=parsed["tts_direction"]
        )

        # Step 6: Update state post-turn
        self.state.apply_update(
            mood=parsed["mood_update"],
            energy=parsed["energy_update"]
        )
        self.history.add_turn(transcript, parsed["speech"])

        return audio

    def build_system_prompt(self, state: AriaState) -> str:
        phase = state.conversation_phase
        direction = VOICE_DIRECTION_BY_PHASE[phase]
        return ARIA_SYSTEM_PROMPT_TEMPLATE.format(
            state=state.to_json(),
            phase_direction=direction["tts_direction"],
            energy=direction["energy_baseline"],
            filler_rate=direction["filler_rate"]
        )
```

---

### 7.5 Sample LLM Output with Voice Direction Tags (30-Second Slice)

**Context:** Conversation phase = climax (relationship_depth = 63). User just said, voice slightly trembling: "I don't know, I've been telling myself it's fine for a while but I think I'm just... tired."

Hume detects: sadness 0.78, tiredness 0.71, hope 0.31.

**LLM output:**
```json
{
  "speech": "[soft] [slows down] Haan. [pause] That — [breathes] that's a really honest thing to say. [pause] Matlab... [drawn out] there's a difference between actually being okay and just deciding to call it that, na? [pause] [whispers] I think you already know which one this is. [pause] [warm] And I think you telling me that right now? That took something.",
  "tts_direction": "warm and careful, like someone who just heard something real. Low pitch, slow pace, breathy quality. Not sad — steady and present.",
  "mood_update": "intimate",
  "energy_update": 0.28
}
```

**Annotation of what each tag does acoustically:**
- `[soft]` → amplitude down 8-10 dB, softer onset on consonants
- `[slows down]` → rate drops from ~140 WPM to ~100 WPM for this phrase
- `"Haan."` → Hinglish backchannel. Said slowly, signals deep acknowledgement
- `[pause]` → 600-900ms of silence — pre-thought pause
- `"That — "` → false start, self-interruption, signals the speaker is choosing words carefully
- `[breathes]` → audible breath event — signals emotional weight
- `"that's a really honest thing to say."` → low, steady, direct
- `[pause]` → another beat — not filler, but weight
- `"Matlab..."` → Hinglish filler + hesitation particle
- `[drawn out]` → stretched vowels on next phrase, slowed articulation
- `", na?"` → Indian English tag question, rising intonation, seeking connection
- `[whispers]` → drop to near-whisper for the "secret truth" moment
- `[pause]` → let the whisper land
- `[warm]` → back to modal warmth for the closing
- `"And I think you telling me that right now?"` → mild uptalk, emotional
- `"That took something."` → final word stressed, falling contour

**Total: ~30 seconds at this pace. Pause time: ~4 seconds total. Rate: ~95 WPM average in this passage.**

---

## The 10 Voice Realism Techniques — Ranked by Impact

### Priority Stack

| Rank | Technique | Why It Matters | Implementation |
|------|-----------|----------------|----------------|
| **1** | **Immediate emotion anchoring** — when user is vulnerable, Aria softens THAT turn, not next | Listeners report "the robot didn't notice" as the #1 uncanny-valley signal | Hume EVI emotion detection → state update → `[soft][slows down]` + `tts_direction` same turn |
| **2** | **Audible breathing** — inhalations between heavy thoughts, breath catches, sighs | Silence-to-speech transitions are the biggest TTS tell | `[breathes]` (Inworld) or `[breath]` (ElevenLabs) at clause boundaries + `[sighs]` for emotional release |
| **3** | **False starts + self-corrections** — "I — I mean, it's not that—" | Signals the character is actually thinking, not reciting | Inject into LLM output when state.recent_vulnerability = True; rare but powerful |
| **4** | **Speech rate variation** | Monotone pace = robotic regardless of voice quality | `[slows down]` for heavy moments, `[rushed]` for excited, `[deliberate]` for emphasis |
| **5** | **Genuine vs polite laughter** — different tags for different amusement levels | Polite laughs every time are uncanny; genuine bursts are rare and therefore precious | Map `[laughs softly]` to mild amusement; `[laughs]` to real reaction; never both in same conversation window |
| **6** | **Contextual fillers** — Hinglish appropriate: "matlab...", "haan so...", "like" | Makes Aria sound like she's thinking, not outputting | Inject in LLM output based on filler_rate in current phase; never over-use |
| **7** | **Pause variety** — different duration/type for different functions | A 200ms pause ≠ a 900ms pause; they mean different things | Map pause types to durations via SSML `<break time="800ms"/>` or explicit count |
| **8** | **Vocal register shifts** — whisper for confessions, build for laughter | Volume arc is emotional arc | `[whispers]` for intimacy moments; volume/energy tracked in state |
| **9** | **Emotional arc orchestration** — the 4-phase arc over 15 minutes | A conversation that stays at one tone feels like a demo, not a person | Phase tracker + relationship_depth counter driving voice direction shift |
| **10** | **Hinglish micro-tells** — "achha", "yaar", "na?", "haan" as real lexical items | Cultural authenticity → trust → realism | LLM instruced with specific placement rules; never forced, always flow-natural |

---

## Confidence Assessment

- **Section 1 (Micro-acoustics):** HIGH — grounded in peer-reviewed phonetics research (Cambridge, ASHA, ICPhS, ScienceDirect)
- **Section 2 (TTS systems):** HIGH for ElevenLabs v3, Inworld TTS-2, Hume EVI, Sarvam — all from official documentation and recent reviews. MEDIUM for Sesame CSM (limited API availability). LOW for Cartesia Hindi quality.
- **Section 3 (Maya effect):** HIGH — based on Sesame's own published research
- **Section 4 (Emotional arc):** MEDIUM-HIGH — theory from film/theater well-documented; AI-specific orchestration patterns are emerging/proposed, not peer-reviewed
- **Section 5 (Hinglish):** HIGH for Sarvam Bulbul V3; MEDIUM for regional accent differentiation (city-level accent studies limited)
- **Section 6 (Emotion detection):** HIGH for Hume EVI capabilities; MEDIUM for real-world latency at scale
- **Section 7 (Architecture):** MEDIUM — architecture is synthesized from best practices; requires implementation testing to validate latency targets

---

## Sources

### Phonetics Research
- [To 'errrr' is Human — Cambridge Core / JIPA](https://www.cambridge.org/core/journals/journal-of-the-international-phonetic-association/article/abs/to-errrr-is-human-ecology-and-acoustics-of-speech-disfluencies/CFCD75C219E62C811D91E13F9A529183)
- [Hesitation Disfluencies — Corley & Stewart, Edinburgh 2008](https://www.pure.ed.ac.uk/ws/files/15012157/Corley_Stewart_2008.pdf)
- [Disfluencies Revisited — MDPI Languages 2023](https://www.mdpi.com/2226-471X/8/3/155)
- [Acoustic Features of Laughter — Cognitive Processing/Springer 2023](https://link.springer.com/article/10.1007/s10339-023-01168-8)
- [Different Types of Laughter — PMC Laughter Perception Network](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3648477/)
- [Acoustic Analysis of Laughter — Columbia LABROSA](http://labrosa.ee.columbia.edu/~dpwe/papers/BickH92-laugh.pdf)
- [Vocal Fry Register — ASHA Journal](https://pubs.asha.org/doi/10.1044/jshr.1103.600)
- [Vocal Fry Entrainment — ScienceDirect 2016](https://www.sciencedirect.com/science/article/abs/pii/S0892199716303800)
- [Breathy and Whispery Voice in Dialogue — EURASIP Journal](https://asmp-eurasipjournals.springeropen.com/articles/10.1155/2010/528193)
- [Acoustic Properties of Smiling — ICPhS 2015](https://www.internationalphoneticassociation.org/icphs-proceedings/ICPhS2015/Papers/ICPHS0337.pdf)
- [Laughing, Breathing, Clicking — Trouvain & Campbell, ICPhS 2014](https://www.isca-archive.org/speechprosody_2014/trouvain14_speechprosody.pdf)
- [Pause Types and Duration — MDPI Languages 2023](https://www.mdpi.com/2226-471X/8/1/23)
- [Speech Rate Average WPM — VirtualSpeech](https://virtualspeech.com/blog/average-speaking-rate-words-per-minute)

### TTS Systems
- [ElevenLabs v3 Audio Tags — Official Blog](https://elevenlabs.io/blog/v3-audiotags)
- [ElevenLabs v3 Audio Tags: Emotional Context](https://elevenlabs.io/blog/eleven-v3-audio-tags-expressing-emotional-context-in-speech)
- [ElevenLabs v3 Audio Tags: Precision Delivery](https://elevenlabs.io/blog/eleven-v3-audio-tags-precision-delivery-control-for-ai-speech)
- [Inworld Realtime TTS-2 Blog](https://inworld.ai/blog/realtime-tts-2)
- [Inworld TTS-2 on Replicate](https://replicate.com/inworld/realtime-tts-2)
- [Inworld TTS-2 Launch — MarkTechPost](https://www.marktechpost.com/2026/05/05/inworld-ai-launches-realtime-tts-2-a-closed-loop-voice-model-that-adapts-to-how-you-actually-talk/)
- [Cartesia Sonic-3 Docs](https://docs.cartesia.ai/build-with-cartesia/tts-models/latest)
- [Cartesia Sonic-3 Overview](https://cartesia.ai/sonic)
- [Cartesia Sonic-3 Review — eesel AI 2025](https://www.eesel.ai/blog/cartesia-sonic-3-api)
- [Suno Bark GitHub](https://github.com/suno-ai/bark)
- [Suno Bark HuggingFace](https://huggingface.co/suno/bark)

### Sesame CSM
- [Sesame Research — Crossing the Uncanny Valley](https://www.sesame.com/research/crossing_the_uncanny_valley_of_voice)
- [Sesame CSM-1B HuggingFace](https://huggingface.co/sesame/csm-1b)
- [Sesame CSM Release — TechCrunch](https://techcrunch.com/2025/03/13/sesame-the-startup-behind-the-viral-virtual-assistant-maya-releases-its-base-ai-model/)
- [CSM Overview — DigitalOcean](https://www.digitalocean.com/community/tutorials/sesame-csm)
- [Sesame Uncanny Valley Analysis — FlowHunt](https://www.flowhunt.io/blog/breaking-the-uncanny-valley-sesames-conversational-ai-voice-models/)

### Hume AI
- [Hume EVI-3 Announcement](https://www.hume.ai/blog/announcing-evi-3-api)
- [Hume Dev Docs Overview](https://dev.hume.ai/intro)
- [Hume Expression Measurement](https://dev.hume.ai/docs/expression-measurement/overview)
- [Hume Speech Prosody Model](https://dev.hume.ai/docs/expression-measurement/models/prosody)
- [Hume EVI Version Docs](https://dev.hume.ai/docs/speech-to-speech-evi/configuration/evi-version)
- [Hume AI — VentureBeat EVI-2](https://venturebeat.com/ai/who-needs-gpt-4o-voice-mode-humes-evi-2-is-here-with-emotionally-inflected-voice-ai-and-api/)
- [Hume AI — Techraisal EVI 3+4](https://www.techraisal.com/blog/hume-ai-empathic-voice-real-time-emotion-and-evi-3-for-conversational-ai_1756380371/)

### Indian Voice + Hinglish
- [Sarvam AI Bulbul V3 Blog](https://www.sarvam.ai/blogs/bulbul-v3)
- [Sarvam Bulbul V3 — Yourstory](https://yourstory.com/ai-story/sarvam-ai-bulbul-v3)
- [Sarvam Bulbul V3 — Blind Test Results](https://evolutionaihub.com/sarvam-ai-bulbul-v3-beats-top-voice/)
- [Sarvam AI TTS API](https://www.sarvam.ai/apis/text-to-speech)
- [Sarvam AI — GrowwStacks Review 2026](https://growwstacks.com/blog/sarvam-ai-tts-stt-voice-agent-test)
- [ElevenLabs India Voice Page](https://elevenlabs.io/india)
- [AI4Bharat IndicF5 — HuggingFace](https://huggingface.co/ai4bharat/IndicF5)
- [IndicVoices-R Paper — arXiv](https://arxiv.org/html/2409.05356v2)
- [Indian Accent Voice Cloning — Speechify](https://speechify.com/blog/indian-accent-voice-cloning/)
- [AutoProsody Indian Languages — arXiv 2025](https://arxiv.org/pdf/2502.09661)

### Emotion Detection / STT
- [Deepgram Real-Time Sentiment Analysis](https://deepgram.com/learn/real-time-sentiment-analysis-streaming-audio)
- [Deepgram vs AssemblyAI — 2026 Comparison](https://deepgram.com/learn/deepgram-vs-assemblyai-vs-whisper)
- [AssemblyAI Voice Stack 2026](https://www.assemblyai.com/blog/the-voice-ai-stack-for-building-agents)
- [Hume Alternatives 2026 — Dasha AI](https://dasha.ai/tips/hume-ai-alternatives)

### Voice Acting + Emotional Arc
- [Sesame — Crossing the Uncanny Valley](https://www.sesame.com/research/crossing_the_uncanny_valley_of_voice)
- [Fiveable — Emotional Pacing in Film/TV](https://library.fiveable.me/storytelling-for-film-and-television/unit-8/emotional-pacing/study-guide/2hCM51PFe7wkhnjR)
- [Topher Keene — Depth in Voice Acting](https://www.topherkeene.com/articles/beyond-the-cool-voice-how-to-add-real-depth-to-your-voice-acting)
- [Game Informer — Naughty Dog Last of Us Performance](https://gameinformer.com/b/features/archive/2012/02/20/naughty-dog-39-s-art-of-performance-with-last-of-us.aspx)
- [Disco Elysium Narrator Direction — PC Gamer](https://www.pcgamer.com/we-talk-to-disco-elysiums-incredible-narrator-who-recorded-350000-words-of-dialogue-and-has-never-acted-before/)
- [Emotion Dynamics in Movie Dialogues — arXiv](https://arxiv.org/pdf/2103.01345)

### Architecture + State Management
- [EmoVoice — LLM-based Emotional TTS arXiv 2025](https://arxiv.org/abs/2504.12867)
- [NVIDIA PersonaPlex — Backchannel + Duplex](https://research.nvidia.com/labs/adlr/personaplex/)
- [Retell AI Backchanneling Guide](https://www.retellai.com/blog/how-backchanneling-improves-user-experience-in-ai-powered-voice-agents)
- [Building Production Voice Agents 2026 — Shekhar Gulati](https://shekhargulati.com/2026/01/03/building-production-ready-voice-agents/)
- [Voice AI Stack 2026 — AssemblyAI](https://www.assemblyai.com/blog/the-voice-ai-stack-for-building-agents)
- [OpenAI gpt-realtime Introduction](https://openai.com/index/introducing-gpt-realtime/)
