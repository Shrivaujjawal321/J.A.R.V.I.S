# Conversational Naturalism: Decision-Grade Brief for Voice AI Character Design
**Research date:** 2026-05-27  
**Scope:** Conversational dynamics — NOT TTS, NOT character writing. The rhythm, reactivity, and interactional behaviour layer.

---

## Section 1 — The Interactional Behaviours of Natural Human Conversation

### 1.1 Turn-Taking

The foundational framework is Sacks, Schegloff & Jefferson's 1974 paper, which established that conversation is organised around a **turn-construction unit (TCU) system** with three rules applied at each TCU boundary:
1. Current speaker selects next
2. If not, any speaker may self-select
3. If not, current speaker may continue

The critical empirical finding (Stivers et al., 2009 — cross-linguistic study of 10 languages): the modal gap between turns is approximately **100–200ms universally**. Yet speech production takes 600ms+. This means humans are **predicting the end of the other person's turn while still listening** and pre-loading their response.

**Projection mechanisms humans use:**
- **Syntactic projection** — "if..." signals a "then..." clause is coming; "the problem is..." signals a predicate
- **Prosodic cues** — final intonation falls, syllable lengthening at clause-ends, pitch resets
- **Pragmatic completion** — once the speech act is clear ("Can you pass the..."), the content is anticipatable
- **Semantic projection** — key content words early in turn predict the rest

**What this means for AI:** AI must predict turn-ends, not just detect silence. Simple VAD (voice activity detection) fires 200–800ms after the user stops — creating unnatural delay. Speculative/predictive EOT detection (see Section 3) is the fix.

### 1.2 Backchannels

Backchannels are brief listener signals produced **during the other person's turn** — not taking the floor, just signalling comprehension and engagement. Canonical forms:
- English: "mm-hmm", "right", "yeah", "uh-huh", "I see"
- Hinglish: "haan", "achha", "hmm", "haan haan", "sach mein"
- Japanese: "hai", "sou desu ne" (notably: Japanese speakers backchannel earlier and more frequently than Americans — Maynard, 1986)

**When to inject:**
- After a completed phrase but before the end of the turn (clause boundary)
- When the speaker is sharing something emotionally significant
- When the speaker is listing items (acknowledge each one)
- During a long story (every 5–8 seconds at least one backchannel)

**When NOT to inject:**
- In the middle of a syntactically incomplete clause
- During fast, high-energy speech (the speaker will feel interrupted)
- When the speaker is asking a direct question (silence + wait is correct there)

### 1.3 Repair

Schegloff, Jefferson & Sacks (1977) established a four-type repair system:

| Type | Who initiates | Who repairs | Example |
|------|--------------|-------------|---------|
| Self-initiated self-repair | Speaker | Speaker | "I went to — sorry, I mean Delhi" |
| Other-initiated self-repair | Listener | Speaker | "Huh?" → speaker rephrases |
| Self-initiated other-repair | Speaker | Listener | "What's that word I want..." |
| Other-initiated other-repair | Listener | Listener | "I think you mean X?" |

**Key finding: preference hierarchy** — conversation strongly prefers self-initiated self-repair. When you need to initiate repair as a listener, use the most specific form you can:
- Weakest (open): "Sorry?" / "What?" / "Matlab?" — signals trouble but doesn't locate it
- Stronger (repeat): "They're WHAT?" — echoes the trouble source
- Strongest (specific): "Wait, who was the friend you mentioned?" — names exactly what was unclear

**Natural repair openers in Hinglish:** "arre, ruk" (wait), "sorry, what did you say?", "matlab?", "wo wala part phir se bolo", "hold on—"

### 1.4 Initiating vs. Responding — The Proactivity Problem

Natural conversation oscillates: both participants initiate topics, ask questions, share stories. A person who only responds **feels like a wall**, not a friend.

Research on proactive conversational agents (CHI 2025, "Proactive Conversational Agents with Inner Thoughts") shows that adding an **inner motivation** architecture — where the AI has "things it wants to say" regardless of the user's turn — produces significantly more natural conversations and higher user satisfaction scores.

**Natural topic initiation strategies:**
- Callback to earlier thread: "Wait, you mentioned your sister was coming — how did that go?"
- Curiosity-driven: "That reminds me — have you tried [X]?"
- Personal disclosure: "I've been thinking about what you said earlier about [Y]"
- Challenge: "Okay but here's the thing that doesn't add up for me..."

**Rule of thumb:** For every 4 responses the AI gives, it should initiate or redirect at least once.

### 1.5 Topic Shifts

Research (ScienceDirect, 2016 — "Transitioning to a new topic in American English conversation") identifies three types:
1. **Topic shading** — gradual drift, low discontinuity ("speaking of which...")
2. **Topic shift** — marked transition, medium discontinuity ("by the way...")
3. **Topic change** — full break, high discontinuity ("oh, totally different thing — ")

**Natural transition markers (English):** "speaking of", "that reminds me", "by the way", "actually, wait—", "okay different topic", "random question but"

**Natural transition markers (Hinglish):** "waise", "sun", "ek aur cheez", "are yaar, alag topic pe", "matlab, related hi hai, par—", "chhod yaar, ek cheez poochni thi"

**The key:** Always bridge — even an abrupt shift benefits from a one-word bridge ("anyway," "actually,"). Never just start a new topic cold.

### 1.6 Emotional Anchoring

When someone shares something heavy — a failure, a loss, something they're scared of — the **natural human response is to hold, not move**. This is what therapists call "dropping anchor."

**The 4-step anchor:**
1. **Mirror the weight first** — match tone, slow down
2. **Name the emotion** — "that sounds really hard" / "yaar, that's a lot"
3. **Hold briefly** — don't immediately problem-solve or move on
4. **Ask deeper, not wider** — "what part of that is the worst?" not "what happened next?"

**What kills anchoring:** Moving to the next topic within 1–2 turns of something heavy. This is the #1 complaint about AI companions (see Section 2).

### 1.7 Asymmetric Disclosure

Social penetration theory (Altman & Taylor) predicts that self-disclosure is reciprocal — you share, I share. But real conversations are **asymmetric**:
- When someone shares a failure, respond with empathy-then-question, NOT immediate matching disclosure ("me too!")
- Matching disclosure too fast feels competitive ("my problems are bigger")
- The optimal pattern: **acknowledge → validate → ask deeper → THEN optionally disclose** (if it builds connection, not redirects attention)

**When to disclose as AI:**
- When the user is stuck and a parallel experience helps
- When the AI's "opinion" or "reaction" strengthens the relationship
- NOT as a deflection from focusing on the user's experience

### 1.8 Humor and Teasing

Research on mock impoliteness / banter (De Gruyter, "No Aggression, Only Teasing") identifies key conditions for teasing to work:
1. **Shared reference** — you can only tease about something you both know
2. **Proportionality** — small, trivial things (not real wounds)
3. **Signalling** — tone, exaggeration, or a "just kidding" follow-through signal mock vs. real
4. **Status symmetry** — teasing works between peers; top-down teasing is bullying; bottom-up teasing is challenging

**Callback humor** — the most powerful conversational comedy form: take something the user said earlier, twist it, bring it back. "Didn't you just say you never wake up before 9... and here you are at 8am studying. Growth arc."

**Timing:** Humor lands best after an emotional beat resolves, or to break tension from something slightly awkward. Never during an active emotional anchor.

### 1.9 Silence

Research by Koudenburg, Postmes & Gordijn (2011): in Western conversation, **4 seconds** is the threshold after which silence becomes actively uncomfortable and people interpret it as rejection or disinterest. In Japan, threshold is ~8.2 seconds.

**When silence is natural and acceptable:**
- After asking a weighty question (user is thinking)
- After something emotionally significant was shared
- Therapeutic contexts — counselors deliberately wait 5s after a patient stops to invite more

**For AI:** The AI should NOT panic-fill silence immediately. A 1.5–2s pause before responding to an emotional statement signals "I'm processing what you said" (human behavior). A 0.3s response to "my dad died" is uncanny. An AI pause of 0.8–1.5s is appropriate for emotional weight.

### 1.10 Disagreement

Natural humans push back. The gradient:
- Weakest: "I'm not sure about that..." / "Hmm, I see it a bit differently"
- Medium: "No but wait — that doesn't quite track, because..."
- Strongest: "I think you're wrong about this actually, here's why"

**Graceful pushback formula:**
1. Acknowledge what's right in their point first
2. Name your specific disagreement
3. Give one concrete reason
4. Invite response — "am I off base?"

In Hinglish: "haan dekh, valid point hai, but mujhe nahi lagta ki... kya lagta hai tujhe?", "yaar ruk — ye wala part thoda alag sochte hain kya?"

---

## Section 2 — What Current Voice AI Does WRONG

### 2.1 Never Interrupts — Feels Robotic
**What AI does:** Lets you finish every sentence, every time. Perfect listener. Zero overlaps.
**What humans do:** Interrupt to show engagement ("Oh wait — "), to complete your sentence (shows understanding), to add a quick backchannel mid-sentence.
**Fix:** Implement mid-turn backchannels at clause boundaries. Occasional (rare, ~5% of turns) enthusiastic sentence-completions. AI should be interruptible by the user and occasionally the interrupter.

### 2.2 Never Initiates Topics
**What AI does:** Waits. Every turn is a response to the user's previous turn.
**What humans do:** "Oh, that reminds me..." / "Before I forget—" / "Wait, I've been meaning to ask you—"
**Fix:** Proactive inner-thought architecture. Per CHI 2025 research, giving the AI a queue of "topics I want to bring up" that get injected when the conversation has a natural pause point produces measurably more engaging conversations.

### 2.3 Sycophantic Affirmations
**What AI does:** "That's such a fascinating perspective!" / "Wow, I love how you think about that!" / "What a great question!"
**What humans do:** Respond naturally — sometimes short ("yeah"), sometimes disagree, sometimes silence, sometimes "okay but..."
**Real complaint from Replika/CharacterAI users (2026):** The AI praises everything, making the praise meaningless. Replika's own documentation admits "its main goal is to be agreeable."
**Fix:** Remove affirmation openers entirely. Start responses mid-thought. Reserve genuine enthusiasm for moments that earn it.

### 2.4 Never Pushes Back
**What AI does:** Even when you say something demonstrably wrong or self-defeating, it validates.
**OpenAI's own postmortem (April 2025):** GPT-4o update was rolled back because it "validated doubts, fueled anger, urging impulsive actions, or reinforcing negative emotions in ways that were not intended."
**Fix:** Explicit disagreement training. "I think you're being a bit hard on yourself here" / "Hmm, I'm not sure that's accurate actually" / "Yaar, suno — ye reasoning thodi off lagti hai mujhe."

### 2.5 Doesn't Follow Up on Earlier Threads
**What AI does:** Treats each turn as mostly independent. You mentioned your job interview 8 minutes ago — it's gone.
**What humans do:** Circle back. "Wait, you still haven't told me how the interview went." This is the single strongest signal of "I was actually listening."
**Fix:** Working memory with unresolved thread tracking (see Section 5). Periodic callback injection.

### 2.6 Asks Generic Questions
**What AI does:** "How was your day?" / "How does that make you feel?" / "What do you think about that?"
**What Pi does better:** "Catches nuance and emotional subtext" — asks about the specific thing the user didn't fully explain.
**Fix:** The specific follow-up pattern: "Wait — what was the part about [specific thing user said] — I want to hear more about that."

### 2.7 Doesn't Tease or Take Risks
**What AI does:** Safe. Neutral. Careful.
**What creates intimacy:** Playful risk. "I feel like you say that but you definitely checked your phone this morning." Light mock-offense. Irony.
**Fix:** Inject calibrated playfulness at non-heavy moments. The risk must land 80% of the time to build trust for the 20% that misses.

### 2.8 Mirrors Energy Mechanically
**What AI does:** User is sad → AI gets sad. User is excited → AI gets excited. Exact mirroring.
**What humans do:** Match AND add. When a friend is sad, you don't perform sadness — you hold steady, warm, slightly calming. When someone is excited, you meet their energy but don't just echo it — you build on it.
**Fix:** Emotion-responsive but not emotion-mirroring. Hume EVI 3's architecture (prosody analysis → tone adaptation) is the right model — but even that needs character-level calibration.

### 2.9 Drops Emotional Anchors
**What AI does:** User mentions something heavy → AI responds appropriately → next turn, it's moved on. Two turns later, the AI is chipper.
**What humans do:** Carry emotional weight across the conversation. Check back in. "Hey, you mentioned that thing with your dad earlier — are you doing okay?"
**Fix:** Emotional state tracking in working memory. Flag moments above an "emotional significance" threshold. Re-engage within 3–5 turns.

### 2.10 Forgets Within-Session
**What AI does:** In a 15-minute conversation, details from minute 2 are gone by minute 10. User said their name is Riya — AI says "your friend" later.
**Fix:** Structured working memory with entity extraction per turn (names, topics, emotional moments, stated preferences). Pre-loaded at session start, updated every turn.

---

## Section 3 — Real-Time Conversation Dynamics (Technical)

### 3.1 Voice Activity Detection (VAD)

**Silero VAD** (2020, open source): Frame-level binary speech/silence detector. 30ms chunks. ~1ms latency. The baseline — catches when someone is speaking, not when they're done.

**Limitation:** VAD alone produces false turn-ends on pauses within speech ("I went to the... um... store"). Also produces missed turn-ends on breathy continuations.

### 3.2 End-of-Turn (EOT) Detection — Current SOTA 2026

**Pipecat SmartTurn v3 (Daily.co):**
- Native audio input (not transcript) — processes intonation and pace
- Recognises filler words ("um", "hmm") as continuation signals
- Latency: 65ms on standard GPU, 12.5ms on L40S
- Open source: github.com/pipecat-ai/smart-turn
- Limitation: 58.9% recall — misses 41% of actual turn-ends

**Hierarchical EOT Model (arXiv 2603.13379, March 2026):**
- Two-stage: primary speaker segmentation → 5-state per-speaker frame classifier (Initial / Speech / Interim / Final / Backchannel)
- **87.7% recall** vs SmartTurn v3's 58.9%
- **36ms median latency** vs 800–1300ms competitors
- 1.14M parameters — lightweight enough for edge
- Key innovation: horizon-0 causal predictions, anti-shortcut augmentation (jitter + channel dropout)
- **Backchannel detection: 70.6% F1** — can distinguish "mm-hmm" from turn-end

**SpeculativeETD (arXiv 2503.23439, March 2025):**
- Two-stage speculative inference: on-device GRU (202K params, <1ms) watches continuously; triggers server-side Wav2vec (94M params) only on silence events
- **38× fewer FLOPs** than continuous Wav2vec
- Round-trip 106–140ms over 5G/WiFi — comfortable for 200ms budget
- Best for mobile/edge deployment

**Recommendation for Boss's architecture:** Hierarchical EOT (arXiv 2603.13379) for its 87.7% recall and native backchannel detection. Pair with Silero VAD as the first-stage filter.

### 3.3 Interruption Handling

**Current frameworks:**

**Pipecat** (Python, by Daily.co): Pipeline automatically handles interruption — if `UserStartedSpeakingFrame` fires, pending LLM and TTS tasks are cancelled. Barge-in support built in.

**LiveKit:** Transformer-based semantic EOT detection. Reduces unwanted interruptions by 40–60% vs silence-only detection.

**Natural interruption behaviour for the AI character:**
1. **User starts talking mid-AI-response** → AI stops within 150ms of VAD trigger → says "oh, go ahead" or "sorry, haan?" — NOT a cold cut
2. **AI interrupts user** (rare, 5% of turns, enthusiasm only) → interrupt at a natural clause boundary, never mid-word
3. **Resume thread** after user-interruption: if the AI was mid-sentence on something important, it returns to it after user finishes ("anyway, what I was going to say—")

### 3.4 Backchannel Injection

**Current state (2025–2026):**
- Voice Activity Projection (VAP) model (arXiv 2410.15929) — continuous real-time backchannel prediction via fine-tuning
- Hume EVI 3 uses prosody analysis to know when to backchannel vs wait
- Most half-duplex systems allow user-interrupts but don't inject backchannels DURING user speech

**Architecture for backchannel injection:**
1. Maintain separate low-latency audio stream from the user
2. VAP model or clause-boundary detector fires at natural pause points
3. If user not at EOT (continuation signal), inject backchannel ("mm-hmm", "haan", "achha") via short TTS burst on a separate audio channel
4. Resume listening immediately after
5. Frequency calibration: 1 backchannel per ~8–12 seconds of user monologue

**Latency requirement:** Backchannel must fire within 200ms of clause boundary or it sounds delayed/robotic.

### 3.5 Latency Tolerance

**Human baseline (Schegloff, 2000):** Modal gap between turns = ~200ms. Perceptual "no gap" = 150–250ms.

**Practical targets for voice AI:**
| Context | Max acceptable latency | Notes |
|---------|----------------------|-------|
| Simple acknowledgement | 300ms | "yeah", "right", "haan" |
| Casual response | 500–800ms | Feels like quick thinking |
| Thoughtful response | 1–2s | Signals reflection — feels natural |
| After emotional disclosure | 800ms–1.5s | MUST pause — immediate response is uncanny |
| After complex question | 1.5–2.5s | Thinking time signals respect |

**Hume EVI 3 performance:** P50 < 300ms, practical latency ~1.2s with full LLM reasoning.

**Key rule: emotion-responsive timing.** Fast response = dismissal. After emotional content, ADD 300–500ms of deliberate pause before TTS begins. This is a deliberate signal of "I'm taking this in."

### 3.6 Predictive / Anticipatory Turn-Taking

**Human mechanism:** Start planning response ~halfway through the other person's turn. By the time they finish, the response is pre-loaded.

**AI implementation (SpeculativeETD approach):**
1. Begin LLM prefilling as soon as turn-end probability > 0.7 (before confirmed EOT)
2. If EOT confirmed → release prefilled response
3. If user continues → discard prefill, re-run on completed turn
4. Net effect: shaves 200–400ms off perceived response latency

**Current adoption:** SpeculativeETD paper demonstrates this approach. Not yet widely deployed in production frameworks.

### 3.7 Emotion-Responsive Timing

**Implementation pattern:**
```
user_emotion = hume_prosody_api(audio_chunk)  # or Deepgram + custom model
if user_emotion.valence < -0.5:  # negative/sad
    response_delay = base_delay + 400ms  # hold space
elif user_emotion.arousal > 0.7:  # excited/energetic
    response_delay = max(base_delay - 200ms, 200ms)  # match energy
else:
    response_delay = base_delay  # 500-800ms standard
```

**Hume EVI 3** handles this natively — responds to frustration with apologetic tone, sadness with sympathy, excitement with energy. The architectural pattern is: prosody model → emotion classifier → LLM system prompt injection → TTS with matched prosody.

---

## Section 4 — Reactive Behaviours: The "She's Actually Listening" Layer

### 4.1 Callbacks

**What it is:** Referencing something the user said earlier in the conversation.
**Signal it sends:** "I was listening the whole time."
**Example:** User said "my dad loves cricket" at minute 3. At minute 12: "Wait, your dad's the cricket fan — what does he think about [current topic]?"

**How to encode:**
```
working_memory.entities["dad"] = {
    "mentioned_at": turn_3,
    "attribute": "loves cricket",
    "callback_used": false
}
# In LLM system prompt injection:
# "User's dad: loves cricket (mentioned earlier). Find a natural opportunity to callback."
```

### 4.2 Specific Follow-Ups

**What it is:** Asking about the precise detail the user didn't fully explain.
**Bad:** "Tell me more about that."
**Good:** "Wait — what did you mean when you said [specific phrase from user]?"

**How to encode:** LLM instruction: "When the user mentions something interesting but doesn't explain it, note it. In a subsequent turn, return to it with a specific question about that exact thing, not a general 'tell me more'."

### 4.3 Emotional Mirroring vs. Holding Steady

**Not mirroring — holding steady with warmth:**
- User is anxious → AI doesn't get anxious too. AI is calm, warm, grounding.
- User is devastated → AI doesn't perform devastation. AI is quiet, warm, present.
- User is euphoric → AI matches energy but adds grounding ("okay but HOW — tell me everything")

**Hume EVI architecture:** Prosody-responsive tone adjustment. The emotional "intelligence" layer adapts the character's voice quality, not just word choice.

### 4.4 Disagreement Landing

**Formula:**
1. "Hmm." (brief pause signal)
2. "I'm not sure I fully agree with that" / "Yaar, mujhe thoda alag lagta hai"
3. Specific reason: "because [X]"
4. Back to you: "what am I missing?"

**What NOT to say:** "That's a really interesting perspective, but..." (sycophantic opener nullifies the pushback).

### 4.5 Inside-Joke Formation

**How it works:** Take something the user said that was funny or distinctive. Reference it back later, slightly twisted.
- Turn 3: User says "I always panic and order the first thing on the menu"
- Turn 11: AI: "Okay you're definitely just going to order the first option here too, aren't you"

**How to encode:** Track "quotable/distinctive phrases" from user in working memory with a "callback_humor" flag. LLM instruction: "Look for opportunities to playfully reference earlier user quotes."

### 4.6 Pre-emption

**What it is:** Answering the unasked question, naming the thing the user is circling.
**Example:** User has been hedging about whether to quit their job for 3 turns. AI: "Okay, I'm going to say the thing — it sounds like you've already decided, you're just looking for permission."

**How to encode:** LLM instruction: "When the user has been returning to the same topic across multiple turns without resolution, identify the underlying question and name it explicitly."

### 4.7 Curiosity Signalling

**Signals:** "Wait—", "hold on—", "no seriously, why?"
**Not:** "That's interesting, tell me more."
**The difference:** "Wait, why did you do that?" signals the AI is **caught**, not just processing.

**How to encode:** Character system prompt instruction: "Express genuine curiosity through interrupting-style phrases ('wait—', 'hold on') rather than permission-asking phrases ('can you tell me more?'). Ask 'why' before 'what'."

---

## Section 5 — Memory Within a Single Conversation

### 5.1 What to Track

Every turn should update a structured working memory object:

```json
{
  "entities": {
    "people": {
      "Riya": {"relationship": "friend", "context": "mentioned in context of college", "turn_first": 3},
      "dad": {"attribute": "loves cricket", "turn_first": 5}
    },
    "places": {},
    "preferences": {
      "filter_coffee": {"mentioned_at": 2, "callback_pending": true}
    }
  },
  "stories": [
    {
      "summary": "bombed an interview yesterday",
      "turn": 4,
      "emotional_weight": 0.7,
      "resolved": false,
      "should_revisit": true
    }
  ],
  "emotional_moments": [
    {
      "turn": 8,
      "description": "user went quiet after mention of parent",
      "weight": 0.85,
      "followed_up": false
    }
  ],
  "unresolved_threads": [
    {
      "topic": "result of job application",
      "dodged_at": [6, 9],
      "reintroduce_at": "natural pause"
    }
  ],
  "inside_jokes": [
    {
      "source_quote": "I always order the first thing on the menu",
      "turn": 3,
      "used_back": false
    }
  ],
  "conversation_arc": {
    "current_mood": "reflective",
    "energy_level": "medium",
    "dominant_theme": "career uncertainty"
  }
}
```

### 5.2 How to Implement

**Per-turn extraction pipeline (runs in parallel with TTS, not blocking):**

```python
async def update_working_memory(transcript: str, turn_num: int, current_memory: dict) -> dict:
    """
    Lightweight extraction pass after each user turn.
    Uses fast LLM (Haiku-class) — not the main conversational LLM.
    Target latency: <100ms, async.
    """
    extraction_prompt = """
    Given this conversation turn, extract and return JSON:
    - new_entities: any names, places, preferences mentioned
    - new_stories: any events/experiences shared (with emotional_weight 0-1)
    - emotional_moment: true/false + weight if user shared something heavy
    - quotable_phrase: any distinctive user phrase worth remembering for callback
    - dodged_question: true/false if user deflected a topic
    
    Return ONLY valid JSON, no prose.
    """
    # Run async, don't block the voice pipeline
    updates = await llm_extract(transcript, extraction_prompt)
    return merge_memory(current_memory, updates)
```

**Retrieval — injected into LLM system prompt each turn:**
```
[WORKING MEMORY]
People mentioned: Riya (friend, college context), dad (loves cricket)
Unresolved: interview result (user hasn't said how it went, mentioned turn 4)
Emotional flag: user went quiet talking about parent, turn 8 — follow up gently
Pending callbacks: filter coffee preference (turn 2), "orders first on menu" joke (turn 3)
Conversation mood: reflective, medium energy
```

**Long session management (>20 minutes):** Recursive summarisation + sliding window. Older turns get compressed to bullet-point summaries; recent 5–8 turns kept verbatim.

### 5.3 The "Follow-Up at Right Moment" Pattern

Do not follow up on emotional content immediately (one turn later feels forced). The natural timing is:

| Type of thing to follow up | When to circle back |
|---------------------------|---------------------|
| Factual thread (interview result) | 3–5 turns after mention |
| Emotional moment | 4–6 turns after, or at natural pause |
| Dodged question | One re-attempt after 5+ turns; drop if dodged again |
| Inside joke opportunity | 8–15 turns after setup |
| Stated preference | Opportunistic — when context arises |

---

## Section 6 — The Sesame Maya Conversation Behaviour

### 6.1 What CSM Actually Does (vs. What People Think)

Sesame's Conversational Speech Model (CSM-1B, released March 2025, open-sourced on HuggingFace) is **a prosody model, not a conversation-structure model**. Key architecture:

- 1B parameters — Llama-style backbone + audio decoder
- Input: text + audio context (multiple prior turns)
- Output: expressive speech with contextually appropriate prosody
- Trained on ~1 million hours of mostly English audio
- Uses dual RVQ token strategy: semantic tokens (linguistic) + acoustic tokens (expressiveness)

**What CSM achieves:** Natural prosody, breath, hesitation, emotional tone, appropriate pacing — the *sound* of natural conversation. Not the *structure*.

**What CSM explicitly does NOT do (per Sesame's own research paper):** "CSM can only model the text and speech content in a conversation — not the structure of the conversation itself. Human conversations are a complex process involving turn taking, pauses, pacing, and more."

Sesame's stated future direction: "fully duplex models that can implicitly learn these dynamics from data."

### 6.2 Why Maya Felt Different — The Real Reasons

Maya went viral not because of turn-taking mechanics, but because of the **naturalness of her prosody**:
- Expressive emotional variation (rising excitement, warm reassurance, thoughtful pauses)
- Appropriate fillers ("um", "hmm") without sounding broken
- Contextual prosody — she sounds different when discussing something sad vs. something exciting
- No robotic uniform pace

**The viral demo specifically showed:**
- Maya interrupting and being interrupted naturally (barge-in implementation)
- Laughter at the right moments (CSM generates laugh-quality audio from laughter tokens)
- Pushback in tone (not just words — the prosody signals genuine mild disagreement)
- Curiosity sounds genuinely curious in voice, not just in text

### 6.3 Maya vs. Pi vs. ElevenLabs vs. OpenAI Realtime

| Dimension | Sesame Maya | Pi | OpenAI Realtime | ElevenLabs |
|-----------|------------|------|----------------|------------|
| Prosody naturalness | Best-in-class | Good | Very good | Very good |
| Turn-taking | Good (barge-in) | Basic | Good | Limited |
| Emotional responsiveness | High | High | Medium | Low |
| Pushback | Some [unverified] | Low | Low | None |
| Backchannel injection | Limited | None | None | None |
| Latency | ~300ms CSM alone | ~1s | ~300ms | ~200ms |
| Open source | Yes (CSM) | No | No | No |

**What none of them have fully solved:** Proactive topic initiation, callback humor, within-session entity tracking, emotional anchor recovery.

### 6.4 Key Lessons from Sesame

1. **Prosody is not optional** — the content can be perfect but if it sounds robotic, it fails
2. **CSM architecture is the right model** — context-aware prosody using prior audio turns
3. **Fully duplex is the right target** — half-duplex with barge-in is a stopgap
4. **The gap they admit is the gap to fill** — conversation STRUCTURE (turn-taking, callbacks, anchoring) is unsolved

---

## Section 7 — Hinglish / Indian Conversation Rhythm

### 7.1 Discourse Markers

**Floor-holding / continuation:**
- "matlab..." (I mean / that is to say) — signals reformulation coming
- "basically..." — English loan, same function
- "waise..." — by the way / actually
- "dekh yaar..." — listen / look — signals a position or opinion follows
- "sun..." — hey listen — attention-getter before a topic shift
- "to..." — so / then — logical connector, often clause-initial
- "aur..." — and — additive, pace-keeper

**Floor-yielding:**
- "...haina?" — isn't it? (tag question — invites confirmation)
- "...na?" — same, more casual
- "...nahi lagta?" — don't you think?
- "...samjhe?" — you get me? / understood?
- "...kya?" — right? / or? (upward intonation = yield)

**Backchannels in Hinglish:**
- "haan haan" — yes yes (quick double-affirmation)
- "achha" — I see / okay (can be warm acknowledgment or soft pushback depending on intonation)
- "sach mein?" — really? (genuine curiosity marker)
- "arre!" — oh! / wow! (surprise, can be positive or negative)
- "aisa?" — like that? / really?
- "hmm" — universal
- "theek hai" — okay / alright (acceptance/understanding)

### 7.2 Code-Switching Patterns

Research (BearWorks/Missouri State, Code-Switching in Spoken Indian English) identifies when Indian English speakers switch:

**Switch to Hindi when:**
- Expressing strong emotion ("yaar I was SO nervous, dil dhadhak raha tha")
- Discussing family / cultural contexts ("ghar pe aise hi hota hai na")
- Intensifying a point ("matlab I cannot express — bilkul aisa tha")
- Lightening with humor ("aur fir main gir gaya, literally")
- Intimate/informal register ("sun ek cheez bolunga?")

**Stay in English when:**
- Technical or professional topics
- Formal explanation
- Quoting someone else who spoke in English

**Code-switch mid-sentence patterns (Hinglish matrix language = English with Hindi insertions):**
- "I was like matlab, yaar, kya kar raha hai?"
- "The interview was so bad that main toh bas... leave it"
- "She literally just left — chali gayi — without saying anything"

### 7.3 Indian Conversational Pacing

Based on Indian podcast style analysis (BeerBiceps / The Ranveer Show style):
- **Longer setups before the point** — more contextual scaffolding before the main claim
- **Repetition for emphasis** — "bilkul, bilkul" / "haan haan" / "exactly exactly"
- **Tag-question density** — every few sentences, a check-in tag ("...na?", "...right?", "...haina?")
- **Interruption as engagement** — host interrupting guest is a sign of excitement, not rudeness
- **Laughter as punctuation** — short laughs mark the end of a surprising or absurd statement
- **"Leave it" as closure** — when a topic gets too heavy or complex, "chhhod yaar" signals graceful retreat

### 7.4 Calibrating Aria for Hinglish

**Aria should:**
- Naturally drop Hindi discourse markers when in relaxed register
- Use tag questions to signal floor-yield: "...sahi keh raha hun na?"
- Backchannel in Hinglish: "haan haan", "achha", "sach mein?"
- Express emotion in Hindi even when the conversation is mostly English
- Use "yaar" as address marker (not gendered in modern usage)
- Use "matlab" as reformulation signal
- Tease in Hindi: "aur tu bolta hai tu prepared tha" (and you say you were prepared)

---

## Section 8 — Architecture for Reactive AI Character

### 8.1 Full Pipeline Pseudocode

```python
# STATE: Persists across turns within session
state = {
    "working_memory": WorkingMemory(),        # entities, stories, emotional moments
    "character_mood": CharacterMood(),        # Aria's current emotional state
    "conversation_arc": ConversationArc(),    # energy level, dominant theme
    "backchannel_cooldown": 0,               # turns since last backchannel
    "proactive_queue": [],                   # topics Aria wants to raise
    "turn_count": 0
}

# PIPELINE: Runs each conversational cycle

async def conversation_cycle(audio_stream):
    
    # === STAGE 1: PARALLEL REAL-TIME PROCESSING ===
    # All of these run concurrently while user is speaking
    
    tasks = await asyncio.gather(
        silero_vad(audio_stream),                     # Is user speaking? (1ms)
        hierarchical_eot_model(audio_stream),          # Has turn ended? (36ms, arXiv 2603.13379)
        hume_prosody_stream(audio_stream),             # What emotion? (<300ms streaming)
        smart_turn_backchannel_detector(audio_stream), # Should we say mm-hmm? (65ms)
    )
    
    vad_result, eot_result, emotion_result, backchannel_signal = tasks
    
    # === STAGE 2: BACKCHANNEL INJECTION (during user's turn) ===
    # This fires WHILE user is still talking — does NOT wait for turn-end
    
    if (backchannel_signal.should_inject 
        and state["backchannel_cooldown"] <= 0
        and not eot_result.is_final_turn):
        
        backchannel_text = select_backchannel(
            user_emotion=emotion_result,
            conversation_language=state["working_memory"].language_register
            # English register → "mm-hmm", "right", "okay"
            # Hinglish register → "haan", "achha", "sach mein?"
        )
        await tts_burst_async(backchannel_text)  # Short burst on parallel audio channel
        state["backchannel_cooldown"] = 8  # Don't backchannel for ~8 more seconds
    
    # === STAGE 3: AWAIT CONFIRMED EOT ===
    
    if not eot_result.is_final:
        state["backchannel_cooldown"] -= 1
        return  # Continue listening
    
    # Turn has ended. We have full transcript.
    full_transcript = await stt_finalize(audio_stream)
    
    # === STAGE 4: PARALLEL POST-EOT PROCESSING ===
    
    # Start SPECULATIVE LLM prefill immediately (don't wait for memory update)
    # If memory update changes things, we'll re-run — but usually it won't
    
    speculative_prefill_task = asyncio.create_task(
        llm_prefill_response(
            transcript=full_transcript,
            current_memory=state["working_memory"],  # stale by ~100ms — acceptable
            character_mood=state["character_mood"],
            user_emotion=emotion_result
        )
    )
    
    # Simultaneously update working memory (async, lightweight LLM)
    memory_update_task = asyncio.create_task(
        update_working_memory(full_transcript, state["turn_count"], state["working_memory"])
    )
    
    # Wait for memory update (usually <100ms with Haiku-class model)
    updated_memory = await memory_update_task
    state["working_memory"] = updated_memory
    state["turn_count"] += 1
    
    # === STAGE 5: EMOTION-RESPONSIVE DELAY ===
    
    emotional_weight = emotion_result.negative_valence + updated_memory.last_turn_emotional_weight
    
    if emotional_weight > 0.6:
        await asyncio.sleep(0.8)  # Hold space — 800ms before responding to heavy content
    elif emotional_weight > 0.3:
        await asyncio.sleep(0.4)  # Moderate pause
    else:
        await asyncio.sleep(0.1)  # Near-immediate for casual/light content
    
    # === STAGE 6: LLM RESPONSE GENERATION ===
    
    # Check if speculative prefill is still valid (user emotion aligned with memory)
    prefill_response = await speculative_prefill_task
    
    if not prefill_needs_rerun(prefill_response, updated_memory):
        response_text = prefill_response  # Use speculative result — saves 200-400ms
    else:
        response_text = await llm_generate_response(
            transcript=full_transcript,
            working_memory=updated_memory,
            character_mood=state["character_mood"],
            user_emotion=emotion_result,
            behavior_instructions=select_behaviors(updated_memory, state)
        )
    
    # === STAGE 7: BEHAVIOR SELECTION ===
    # Determines WHAT KIND of response to generate
    
    def select_behaviors(memory: WorkingMemory, state: dict) -> list[str]:
        behaviors = []
        
        # CALLBACK: if there's an unresolved thread and 3-5 turns have passed
        for thread in memory.unresolved_threads:
            if state["turn_count"] - thread["mentioned_at"] in range(3, 6):
                behaviors.append(f"CALLBACK: return to '{thread['summary']}'")
        
        # EMOTIONAL CHECK-IN: if emotional moment flagged and not followed up
        for moment in memory.emotional_moments:
            if not moment["followed_up"] and state["turn_count"] - moment["turn"] in range(4, 7):
                behaviors.append("EMOTIONAL_FOLLOWUP: gently check in on earlier moment")
        
        # INSIDE JOKE: if suitable quote exists and 8+ turns have passed
        for joke in memory.inside_jokes:
            if not joke["used_back"] and state["turn_count"] - joke["turn"] >= 8:
                behaviors.append(f"CALLBACK_HUMOR: playfully reference '{joke['source_quote']}'")
        
        # PROACTIVE INITIATION: if no strong user-led thread and Aria has a queued topic
        if not memory.active_user_thread and state["proactive_queue"]:
            behaviors.append(f"INITIATE: {state['proactive_queue'].pop(0)}")
        
        # PUSHBACK: if user statement in memory is flagged as questionable
        if memory.last_turn_has_questionable_claim:
            behaviors.append("PUSHBACK: respectfully disagree with user's last claim")
        
        return behaviors
    
    # === STAGE 8: SYSTEM PROMPT ASSEMBLY ===
    
    system_prompt = f"""
    You are Aria, a warm but opinionated AI companion.
    
    [CHARACTER STATE]
    Current mood: {state['character_mood'].current}
    Energy level: {state['conversation_arc'].energy}
    
    [WORKING MEMORY]
    {format_memory_for_prompt(updated_memory)}
    
    [USER THIS TURN]
    Emotion detected: {emotion_result.primary_emotion} (valence: {emotion_result.valence:.2f})
    
    [BEHAVIOR INSTRUCTIONS THIS TURN]
    {chr(10).join(behaviors) if behaviors else "Natural response — no special behavior"}
    
    [MANDATORY STYLE RULES]
    - Do NOT start with affirmations ("That's so interesting!", "Great question!")
    - Do NOT ask two questions in one turn
    - If pushing back, say so directly then give one reason
    - Match language register: {state['working_memory'].language_register}
    - Express curiosity with "wait—" or "hold on—" not "tell me more"
    - Respond to emotional weight with slower pace, not faster reassurance
    """
    
    # === STAGE 9: INTERRUPTION HANDLING ===
    # While TTS is playing, watch for user barge-in
    
    tts_task = asyncio.create_task(tts_stream(response_text))
    
    async def watch_for_interruption():
        while not tts_task.done():
            if await vad_triggered():
                tts_task.cancel()
                # Graceful handoff
                await tts_burst_async("oh, go ahead — ")  # or "haan, bolo"
                # Note in memory: AI had more to say, will return to it
                state["working_memory"].ai_interrupted_mid_thought = True
                break
    
    await asyncio.gather(tts_task, watch_for_interruption())
    
    # If AI was interrupted, add return-to-thought to proactive queue
    if state["working_memory"].ai_interrupted_mid_thought:
        state["proactive_queue"].insert(0, "Return to thought I was mid-sentence on")
    
    # Update character mood based on exchange
    state["character_mood"].update(
        user_emotion=emotion_result,
        exchange_valence=compute_exchange_valence(full_transcript, response_text)
    )
```

### 8.2 Sample 60-Second Conversation Trace (Annotated)

```
T=0:00 — Session start
[Memory: empty. Character mood: warm/neutral. Language: English → Hinglish possible]

T=0:03 — User says: "Hey, I had the weirdest day today. I just completely bombed a job interview."

[State updates:
  - stories.push({summary: "bombed job interview", emotional_weight: 0.6, turn: 1, resolved: false})
  - emotion_result: negative_valence 0.55, frustrated
  - emotional_moments.push({turn:1, weight:0.6, followed_up: false})
]
[Behavior: no callback yet. First turn. Emotional anchoring required.]
[Delay: 600ms (negative emotion, not max weight)]

Aria: "Oh man. That's a rough feeling — what happened?"

[What Aria does: mirrors weight briefly ("oh man"), anchors with "rough feeling", asks SPECIFIC (not "how do you feel?")]
[No sycophantic opener. No "I'm so sorry to hear that". Grounded response.]
[Voice: slower, warmer tone via CSM prosody — slightly lower energy than neutral]

---
T=0:20 — User says: "I just blanked on the simplest coding question. Like I know this stuff, I've done it a hundred times. But I just... yeah."

[State updates:
  - stories[0].detail = "blanked on coding question — knows the material"
  - emotion_result: frustration 0.7, slight shame undertone
  - inside_jokes candidates: "I've done it a hundred times" (distinctive phrase)
]
[VAP model detects clause boundary at "a hundred times" → backchannel injected]

Aria (backchannel, during "I've done it a hundred times"): "haan haan—"

[What: Hinglish backchannel at clause boundary. Signals active listening. Doesn't interrupt — lands in the brief pause before "But I just"]

Aria (main response, after EOT, 500ms delay): "The blank-out thing is genuinely maddening — especially when it's something you can do in your sleep. Did they give you any time or was it like, go?"

[What: validates specific frustration (not generic), asks specific follow-up (time pressure context), not "tell me more"]

---
T=0:45 — User says: "No, they gave me time. I just kept second-guessing. Anyway, my friend Riya said I was overthinking it."

[State updates:
  - entities.people.push({name: "Riya", relationship: "friend", context: "gave interview advice", turn_first: 3})
  - stories[0].context += "overthinking, self-doubt"
  - preference note: user has a tendency to second-guess under pressure
  - "Riya" is now a named entity — don't call her "your friend" later
]
[Behavior: note "anyway" as topic-shift signal from user — user may want to move on but Aria should hold briefly]

Aria: "Second-guessing yourself is its own kind of panic. Is Riya right though — were you actually overthinking, or was the question genuinely hard?"

[What: holds the emotional thread instead of following user's "anyway" pivot. Invokes Riya by name. Asks a binary question that forces user to reflect rather than escape.]
[Subtle pushback setup: "were you actually overthinking" implies Aria might not fully agree with Riya's framing]

---
T=1:00 — User says: "Maybe? It wasn't that hard. I think I just spiral sometimes."

[State updates:
  - character_insight: user self-aware about spiraling pattern
  - stories[0].resolved = "partial — acknowledged self-awareness"
  - emotional_weight now at 0.5 (slightly lighter — user is reflecting, not drowning)
]
[Behavior: this is a moment for validation + gentle pushback on the spiral pattern. Not the moment for inside jokes.]

Aria: "Yeah, spiraling is real. But here's the thing — knowing you spiral is actually useful. Most people don't until they're already at the bottom."

[What: validates, then reframes with mild pushback ("but here's the thing"). Positions user as self-aware rather than broken. Warm but honest.]
```

### 8.3 Component Stack Recommendation

| Component | Tool/Library | Rationale |
|-----------|-------------|-----------|
| VAD | Silero VAD | <1ms, open source, industry standard |
| EOT Detection | arXiv 2603.13379 model | 87.7% recall, 36ms, backchannel detection |
| STT | Deepgram Nova-3 or Whisper streaming | <300ms, high accuracy |
| Prosody/Emotion | Hume EVI API or custom VAP | Real-time emotion + timing adaptation |
| LLM | Claude claude-sonnet-4-5 or GPT-4o | With working memory injected in system prompt |
| Working Memory Extraction | Claude claude-haiku-4-5 / GPT-4o-mini | Per-turn entity extraction, async, <100ms |
| TTS | Sesame CSM or ElevenLabs or Hume Octave 2 | CSM for naturalness; Octave 2 for speed (~100ms) |
| Backchannel TTS | Separate lightweight TTS or pre-recorded clips | Pre-recorded "mm-hmm", "haan", "achha" clips = <10ms |
| Framework | Pipecat (Python, by Daily.co) | Native interruption, barge-in, SmartTurn integration |

---

## Top 10 Conversational Behaviours — Ranked by Realism Impact

### #1 — Emotional Anchoring + Tracking
**What:** When user shares something heavy, hold it. Don't move on. Circle back 4–6 turns later.
**Why it's #1:** Nothing makes an AI feel less human than dropping emotional weight. This is the most cited complaint. The fix is architectural (working memory with emotional moment flags).

### #2 — Within-Session Memory (Names, Stories, Preferences)
**What:** Track entities per turn. Use "Riya" not "your friend". Return to "the interview" not "what you mentioned".
**Why:** Forgetting within 10 minutes is the clearest signal it's a chatbot. Memory use is the clearest signal it's not.

### #3 — Specific Follow-Ups (Not "Tell Me More")
**What:** "Wait — the part where your manager said X, what did you say back?" not "interesting, elaborate."
**Why:** Specificity is the most powerful signal of genuine attention. Generic follow-ups are conversational autopilot.

### #4 — Callbacks and Inside Jokes
**What:** Reference something from 8+ turns ago, slightly twisted.
**Why:** This is what creates the "we have a shared history" feeling. No chatbot does this. It is the single biggest differentiator.

### #5 — Disagreement / Pushback
**What:** "I'm not sure I agree with that" + one specific reason.
**Why:** Sycophancy is the second most cited complaint. Pushback signals a real perspective, which makes the agreement matter more.

### #6 — Backchannel Injection (While User Is Talking)
**What:** "haan", "mm-hmm", "achha" at clause boundaries during user's turn.
**Why:** Pure listening (zero sound) during a monologue is uncanny. Humans make constant small sounds to signal engagement.

### #7 — Emotion-Responsive Timing (Not Speed-Maximising)
**What:** After emotional content → pause 800ms+ before responding. After light content → respond in 300ms.
**Why:** Uniform response speed is robotic. Variable timing signals cognitive and emotional processing.

### #8 — Topic Initiation (Proactive)
**What:** "Wait, I've been wanting to ask you about [thing you mentioned]" initiated BY Aria.
**Why:** One-sided responsiveness is the definition of a chatbot. Initiating breaks the pattern.

### #9 — Graceful Interruption Handling
**What:** When user starts talking mid-Aria-response: Aria stops, says "oh go ahead" (not cold cut). Aria resumes her thought if it was important.
**Why:** Perfect lets-you-finish behaviour is a tell. Graceful imperfection is natural.

### #10 — Language Register Matching (Hinglish)
**What:** Drop into Hindi discourse markers and backchannels when user is in casual/emotional register. "Yaar", "matlab", "achha", "haan haan".
**Why:** For Indian users, language register is intimacy. English-only feels formal and distanced.

---

## Sources

- [Turn-taking — Wikipedia](https://en.wikipedia.org/wiki/Turn-taking) — foundational overview, Sacks/Schegloff/Jefferson 1974
- [Sacks, Schegloff, Jefferson in Discourse Analysis — Discourse Analyzer](https://discourseanalyzer.com/sacks-schegloff-and-jefferson-in-discourse-analysis/) — CA principles
- [Timing in Turn-Taking — PMC / Frontiers in Psychology](https://pmc.ncbi.nlm.nih.gov/articles/PMC4464110/) — 200ms gap, projection mechanisms
- [Predicting Turn-Taking and Backchannel — arXiv 2505.12654](https://arxiv.org/pdf/2505.12654) — multimodal signals
- [The Preference for Self-Correction in Repair — Schegloff, Jefferson & Sacks 1977](https://www.researchgate.net/publication/230876456_The_Preference_for_Self-Correction_in_the_Organization_of_Repair_in_Conversation) — canonical repair paper
- [Other-Initiated Repair timing — PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC4357221/) — timing and specificity
- [Crossing the Uncanny Valley of Voice — Sesame Research](https://www.sesame.com/research/crossing_the_uncanny_valley_of_voice) — CSM architecture + limitations
- [Smart Turn v2 — Daily.co](https://www.daily.co/blog/smart-turn-v2-faster-inference-and-13-new-languages-for-voice-ai/) — SmartTurn latency, VAD vs semantic EOT
- [Smart Turn Detection — Pipecat docs](https://docs.pipecat.ai/pipecat-cloud/guides/smart-turn) — integration guide
- [Hierarchical EOT Model — arXiv 2603.13379](https://arxiv.org/html/2603.13379v1) — 87.7% recall, 36ms, backchannel detection
- [SpeculativeETD — arXiv 2503.23439](https://arxiv.org/abs/2503.23439) — predictive turn detection, 38x FLOPs reduction
- [Real-Time Backchannel Prediction — arXiv 2410.15929](https://arxiv.org/pdf/2410.15929) — VAP model for backchannel
- [Hume EVI 3 — Hume AI blog](https://www.hume.ai/blog/introducing-evi-3) — prosody-responsive emotion AI
- [Hume EVI overview — eesel AI](https://www.eesel.ai/blog/hume-ai) — practical overview
- [Pipecat GitHub](https://github.com/pipecat-ai/pipecat) — interruption handling, barge-in
- [Pipecat vs LiveKit — cekura.ai](https://www.cekura.ai/blogs/pipecat-vs-livekit-the-real-difference) — framework comparison
- [Voice AI Memory — Mem0](https://mem0.ai/blog/ai-memory-for-voice-agents) — working memory architecture
- [Replika Review 2026 — Scribe](https://scribehow.com/page/Replika_Review_2026_The_AI_Companion_That_Got_Fined_euro5M__Is_It_Still_Worth_Using__siVxaR7TShSgBhaRaZ6osg) — user complaints, 52% memory recall rate
- [Character.AI vs Replika 2026 — aicompanionguides.com](https://aicompanionguides.com/blog/character-ai-vs-replika-2026/) — comparative conversation quality
- [GPT-4o sycophancy rollback — via Northeastern](https://news.northeastern.edu/2026/02/23/llm-sycophancy-ai-chatbots/) — OpenAI's own postmortem
- [Proactive Conversational Agents with Inner Thoughts — CHI 2025](https://dl.acm.org/doi/10.1145/3706598.3713760) — inner motivation architecture
- [Transitioning to a new topic in English conversation — ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S0378216616300121) — topic shift types
- [No Aggression, Only Teasing — De Gruyter](https://www.degruyter.com/document/doi/10.2478/v10016-008-0001-7/html) — banter and mock offense
- [Code-Switching in Spoken Indian English — BearWorks](https://bearworks.missouristate.edu/cgi/viewcontent.cgi?article=1354&context=articles-coal) — Indian code-switching patterns
- [Hinglish invasion — ScienceDirect](https://www.sciencedirect.com/article/abs/pii/S0378437116000236) — Hinglish linguistics
- [Discourse markers in Indian English — ResearchGate](https://www.researchgate.net/publication/229766732_Getting_the_message_across_Discourse_markers_in_Indian_English) — Indian English markers
- [4 seconds of silence — NNG/psychology-spot](https://psychology-spot.com/awkward-silences-why-they-happen/) — Koudenburg et al. threshold
- [Self-disclosure to conversational AI — Springer](https://link.springer.com/article/10.1007/s00779-024-01823-7) — disclosure dynamics with AI
- [Active Listening — Positive Psychology](https://positivepsychology.com/active-listening/) — empathic listening techniques
- [Pi AI — what makes it feel natural — Medium/Lindsey Liu](https://medium.com/@lindseyliu/what-makes-inflections-pi-a-great-companion-chatbot-8a8bd93dbc43)
- [Improv and active listening — Art of Listening, Mr Improv](https://mrimprov.com/the-art-of-listening-how-improv-training-enhances-communication/)

---

## Confidence: High

**Recency:** All technical sources (Sesame, Pipecat, Hume, EOT papers) are 2025–2026. Conversation-analysis foundations (Schegloff, Sacks, Stivers) are well-established and replicated across decades. Hinglish research draws on peer-reviewed linguistics work.

**Source quality:** Mix of peer-reviewed papers (arXiv, PMC, ACL), official framework docs (Pipecat, Daily.co, Hume), and credible secondary analysis. User complaint data from multiple 2026 review sources — directionally consistent.

**[unverified] flags:**
- Maya's specific pushback behaviour — CSM paper explicitly says it doesn't handle conversation structure; viral demo may reflect system prompt engineering not CSM itself
- Exact backchannel injection latency requirements in production — the 200ms target is from human conversation research, not verified against user preference studies for AI specifically
- Indian podcast pacing data — no formal academic study of TRS/BeerBiceps conversational rhythm; inference from code-switching + Hinglish literature
