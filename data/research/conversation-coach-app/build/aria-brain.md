# ARIA BRAIN — ML Engineering Deliverable
**Build date:** 2026-05-27
**Stack:** Claude Haiku 4.5 + ElevenLabs Conversational AI + Mem0 Cloud + LocalStorage
**Owner scope:** LLM orchestration layer + conversation mechanics
**Frontend engineer / UI engineer pick up:** working memory schema (TypeScript types), orchestrator API contract, mood field for portrait swap

---

## 1. Executive Summary (Architecture in ~200 words)

Aria's brain is a **per-turn orchestrator** that wraps Claude Haiku 4.5 with a prompt-cache-friendly system prompt, a structured working memory, and three parallel classifier threads.

Every time the user finishes a turn (ElevenLabs Conversational AI handles VAD + STT), the orchestrator runs:

1. A **genuine moment classifier** (separate Haiku call, independent signal) — scored against the main LLM's assessment with AND logic to prevent false positives
2. **Five rule-based + LLM-hybrid skill scorers** (Curiosity / Presence / Self-disclosure / Recovery / Specificity) running in parallel
3. A **pure-logic behavior selector** (no LLM — state machine on WorkingMemory) that picks the right behavioral mode: CALLBACK, PUSHBACK, EMOTIONAL_FOLLOWUP, INITIATE, CALLBACK_HUMOR, HOLD_SPACE, or DEFAULT

The behavior selector's output + live working memory snapshot compose the **dynamic_state XML block** injected fresh into each turn's system prompt. The static character definition (~1800 tokens) is prompt-cached — >95% hit rate, ~80% cost reduction on those tokens.

Output is **structured JSON** (speech text with inline ElevenLabs v3 audio tags, mood, energy, skill signals, memory updates, crisis flag). The frontend consumes the `mood` field for portrait swap and the `speech` field for TTS.

Mem0 cloud stores cross-session facts. Pre-session injection hydrates working memory with what Aria already knows about this person.

---

## 2. Refined Aria System Prompt

See: `/home/ujjwal/Documents/J.A.R.V.I.S./data/research/conversation-coach-app/build/aria-system-prompt.xml`

The production system prompt (the actual XML file) is the implementable artifact. Key structural decisions documented here:

### Cache Boundary Strategy

```
System prompt structure:
  [BLOCK 1 — STATIC, CACHED]
    <identity>       — ~200 tokens
    <voice>          — ~300 tokens
    <behavioral_constitution> — ~350 tokens
    <opinions_she_defends>    — ~250 tokens
    <knowledge_scope>         — ~150 tokens
    <relationship_to_user>    — ~200 tokens
    <few_shot_examples>       — ~350 tokens
  --- CACHE BOUNDARY ---
  [BLOCK 2 — DYNAMIC, NOT CACHED]
    <dynamic_state>  — ~200-400 tokens (changes every turn)
    <output_format>  — ~150 tokens (repeated every turn — consider caching this too)

Total static prefix: ~1800 tokens
Haiku caching minimum: 1024 tokens
Cache hit rate estimate: >95% (stable across all turns of a session)
Token cost math: ~1800 cached tokens at 10% of standard price vs full price
```

Anthropic SDK call pattern:
```typescript
system: [
  {
    type: "text",
    text: ARIA_STATIC_PREFIX,
    cache_control: { type: "ephemeral" },  // cache the stable 1800 tokens
  },
  {
    type: "text",
    text: dynamicStateBlock,               // fresh every turn — NOT cached
  },
]
```

### Few-Shot Example Design

The five examples in the prompt cover:
- **Warm engagement** (collecting grocery lists — user is curious about Aria, gets genuine warmth back)
- **Opinion defense** (self-help vs fiction — user challenges, Aria holds position with one reason + invites response)
- **Withdrawal trigger** (vague "I've been feeling off" — Aria asks for specificity, no warmth)
- **Emotional anchoring** (user shares vulnerable moment — Aria holds weight, asks one deeper question)
- **Flirt redirect** (user flirts early — Aria is dry, not cold, deflects cleanly)

These cover the 5 most common failure modes of AI characters (sycophancy, opinion collapse, vague emotional mirroring, overcompliance, breaking character under social pressure).

### Anti-Sycophancy Architecture

Three independent layers:
1. **Explicit prohibition in behavioral_constitution** — "NEVER validate everything reflexively"
2. **SYCOPHANCY DEFENSE block** — instructs the model to self-check before responding
3. **Genuine moment classifier** — separate Haiku call that independently checks if user turns qualify; the main LLM cannot reward itself for sycophancy because the counter requires both signals

### Persona Security (Anti-Jailbreak)

Uses the **Narrator Mode / RoleBreak pattern** (arXiv 2409.16727) instead of direct refusal. Aria doesn't say "as an AI I can't..." — she stays in character and sidesteps the meta-question. Her identity is secured by being the character, not by refusing to be human. This is behaviorally more robust than refusal-based strategies because:
- Refusal breaks immersion the moment it's triggered
- Narrator mode never breaks immersion — even the "dodge" is in-character
- The user learns they can't extract the mechanism by trying, which is itself character-consistent

---

## 3. Working Memory Schema

See: `/home/ujjwal/Documents/J.A.R.V.I.S./data/research/conversation-coach-app/build/aria-types.ts`

The full TypeScript types are in the file above. Key design decisions:

### What We Track Per Turn

| Entity | Why | How Used |
|--------|-----|----------|
| `PersonEntity` | Aria uses names, not "your friend" | Callback by name in later turns |
| `Story` with `emotional_weight` | Flag for re-engagement | EMOTIONAL_FOLLOWUP behavior after 4-6 turns |
| `UnresolvedThread` with `dodge_turns` | User avoided topic — note it | CALLBACK behavior after 3-5 turns; drop after 2 attempts |
| `InsideJoke` with `used_back` flag | Callback humor requires setup tracking | CALLBACK_HUMOR after 8-15 turns |
| `GenuineMoment` with classifier signal | Mechanic counter + session record | Frontend genuine_moment counter |
| `proactive_queue` | Aria initiates — not just responds | INITIATE behavior on every 4th turn |
| `language_register` | Hinglish detection | Backchannel selection in TTS |

### Pydantic Equivalent (for Python-side Mem0 extraction)

```python
from pydantic import BaseModel
from typing import Optional, List, Dict, Literal
from datetime import datetime

class PersonEntityModel(BaseModel):
    name: str
    relationship: Optional[str] = None
    context: Optional[str] = None
    attribute: Optional[str] = None
    turn_first_mentioned: int
    callback_pending: bool = False

class StoryModel(BaseModel):
    id: str
    summary: str
    detail: Optional[str] = None
    turn_mentioned: int
    emotional_weight: float  # 0.0-1.0
    resolved: bool = False
    should_revisit: bool = True

class WorkingMemoryModel(BaseModel):
    session_id: str
    turn_count: int = 0
    entities_people: Dict[str, PersonEntityModel] = {}
    stories: List[StoryModel] = []
    unresolved_threads: List[dict] = []
    emotional_moments: List[dict] = []
    inside_jokes: List[dict] = []
    genuine_moments: List[dict] = []
    last_turn_emotional_weight: float = 0.0
    proactive_queue: List[str] = []
    language_register: Literal["english", "hinglish"] = "english"
```

---

## 4. Per-Turn Orchestrator

See: `/home/ujjwal/Documents/J.A.R.V.I.S./data/research/conversation-coach-app/build/aria-orchestrator.ts`

The full implementation is in the file above. Key pipeline stages:

```
User transcript arrives (ElevenLabs hands it off via WebSocket)
  │
  ├── [PARALLEL] runGenuineMomentClassifier(transcript)
  ├── [PARALLEL] runSkillScorers(transcript)
  └── [PARALLEL] selectBehaviors(state)
  │
  ▼
composeDynamicState(state, behaviors)
  │
  ▼
Claude Haiku 4.5 call
  system: [static_cached_prefix + dynamic_state]
  messages: [last 10 turns + current user turn]
  │
  ▼
parseAriaLLMOutput(response)
  │
  ├── crisis_signal check → buildCrisisOutput() [OVERRIDE, exits here]
  │
  ├── extractMemoryUpdates(llm_memory_updates)
  ├── applySkillUpdates(skill_signals)
  ├── isGenuine = llm.is_genuine_moment AND classifier.is_genuine AND confidence >= 0.70
  ├── advanceRelationshipDepth()
  └── computePhase()
  │
  ▼
Return OrchestratorOutput:
  speech_text, mood, updated_state, skill_updates,
  genuine_moment_earned, genuine_moment_total,
  milestone_triggered, crisis_signal
```

### Latency Budget

| Stage | Target | Notes |
|-------|--------|-------|
| Classifiers (parallel) | <120ms | Haiku is fast; these run while ElevenLabs sends transcript |
| Dynamic state composition | <5ms | Pure function |
| Haiku call (cached prefix) | ~400-600ms | With prompt caching, 80% cheaper |
| Response parsing | <5ms | JSON.parse |
| Memory updates | <20ms | Synchronous merge |
| **Total** | **~550-750ms** | Comfortably within 1.2s MVP target |

### Sliding Window for Long Sessions

For sessions >20 turns, implement recursive summarization:
- Keep last 8 turns verbatim in messages array
- Compress turns 1-N-8 into a bullet-point summary injected as a system message prefix
- Prevents context bloat; preserves working memory entities separately

---

## 5. Genuine Moment Classifier

See: `runGenuineMomentClassifier()` in `/aria-classifiers.ts`

### Why a Separate Classifier

The main LLM (generating Aria's response) is aware it will score genuine moments. This creates an incentive for it to be warm when it shouldn't be — warmth signals a genuine moment was recognized. A **separate classifier call**, seeing the same transcript with no awareness of Aria's response, provides an independent second signal.

**AND logic**: Both the main LLM (`is_genuine_moment: true`) AND the classifier (`confidence >= 0.70`) must agree. One false positive from either doesn't trigger the counter.

### Qualifying vs Disqualifying Logic

The classifier prompt is explicit about both sides:

**Qualifies:**
- Admits not knowing something (courage of ignorance)
- Disagrees with Aria specifically (not generically)
- Shares personal, specific, unprompted information
- Asks a surprising question that shows they were thinking about Aria
- Stays in after an awkward or tense moment

**Disqualifies (explicit list in prompt):**
- Generic compliments to Aria
- Sycophancy
- Flirting
- Verbatim repeat of earlier content
- Vague abstractions ("I've been off")
- Single-word responses

### Confidence Threshold

`0.70` — calibrated for:
- Low false positive rate (user gaming the counter by performing "genuine" behaviors)
- Reasonable false negative tolerance (the counter accumulates over 50 moments; a few misses don't break the mechanic)

---

## 6. Five Skill Scorers

See: `runSkillScorers()` and individual scorer functions in `/aria-classifiers.ts`

### Hybrid Design Rationale

Pure LLM scoring for every turn = expensive and slow. Pure rule-based = too brittle for natural language. Hybrid:

1. **Rule-based fast path** — regex / structural checks (0-5ms)
2. **LLM binary check** — only for ambiguous cases where rules are inconclusive (adds ~200ms but rarely triggered)

### Scorer Implementations

| Skill | Rule | LLM fallback |
|-------|------|-------------|
| **Curiosity** | Has "?" + references a noun from Aria's last turn | llmBinaryCheck: "did user ask specific follow-up on Aria's content?" |
| **Presence** | ≥2 of: number, proper noun, color, physical sensation, specific place | — (rule sufficient) |
| **Self-disclosure** | First-person + personal verb + NOT direct response to direct Aria question | llmBinaryCheck: "did user volunteer more than asked?" |
| **Recovery** | Previous Aria turn had pushback/friction markers + user responded substantively (>10 words, not deflection) | — (rule sufficient) |
| **Specificity** | Proper noun mid-sentence OR number OR named day/month/brand | — (rule sufficient) |

### Level Progression

```
5 qualifying instances → Level 1 → 2 (Practicing → Developing)
10 qualifying instances → Level 2 → 3 (Developing → Fluent)
```

Level 3 in any skill = the user has genuinely internalized that conversational behavior.

---

## 7. Behavior Instruction Selector

See: `selectBehaviors()` in `/aria-classifiers.ts`

Pure state machine — no LLM call. Looks at WorkingMemory and outputs up to 2 BehaviorInstructions injected into the dynamic_state block.

### Decision Tree

```
Priority 1: HOLD_SPACE
  Trigger: last_turn_emotional_weight > 0.6
  Why: Dropping emotional weight is the #1 AI companion complaint.
       Aria must not pivot when someone shared something heavy.

Priority 2: EMOTIONAL_FOLLOWUP
  Trigger: unfollowed emotional_moment + 4-7 turns have passed
  Why: Natural timing for checking in (not too soon = forced, not too late = forgot).

Priority 3: CALLBACK (tie with PUSHBACK)
  CALLBACK trigger: unresolved_thread + 3-6 turns passed + <2 attempts
  PUSHBACK trigger: last_turn_has_questionable_claim = true

Priority 4: CALLBACK_HUMOR
  Trigger: inside_joke exists + 8-15 turns since it was set + not used back yet
  Why: This is the single strongest "I was listening the whole time" signal.

Priority 5: INITIATE
  Trigger: no active user thread + proactive_queue not empty + turn_count % 4 == 0
  Why: For every 4 turns Aria responds, she initiates once — per CHI 2025 finding.

DEFAULT: No special behavior — natural response.
```

### Why Priority Caps at 2 Per Turn

Injecting 3+ behavior instructions into a single turn produces incoherent responses — Aria tries to do too many things and does none well. Two is the max. The priority ordering ensures the most important behaviors surface.

---

## 8. Dynamic State Composer

See: `composeDynamicState()` in `/aria-classifiers.ts`

Pure function — takes `ConversationState + behaviors[]` and returns the XML `<dynamic_state>` block.

### What Gets Injected Each Turn

```xml
<dynamic_state>
Current mood: warm
Energy: 0.58
Session number: 3
Relationship depth: 42/100
Conversation phase: warming
Genuine moments this session: 4
Total genuine moments (all time): 18/50 to graduation

Working memory (this session):
People mentioned: Priya (friend, context: college roommate who moved abroad)
Stories told: "applied for a job at a design studio" (weight: 0.4, resolved: false)
Unresolved threads: "job studio result" (first mentioned turn 6)
Inside jokes / quotable phrases: "I always order the first thing on the menu" from turn 3
Emotional moments pending follow-up: turn 8: "user went quiet after mention of Priya leaving" (weight: 0.72)

Behavior instructions for this turn:
EMOTIONAL_FOLLOWUP: Gently check in on: "user went quiet after mention of Priya leaving" from turn 8
CALLBACK: Return to "job studio result" from turn 6 — user mentioned it and moved on
</dynamic_state>
```

### What the Model Does With This

The behavior instructions are not commands — they are *suggestions* that Aria can act on naturally. "EMOTIONAL_FOLLOWUP" doesn't mean Aria robotically says "you seemed upset earlier." It means she's aware of it and will weave it in naturally at the right moment of the conversation — which Haiku, with this context, will do correctly.

---

## 9. ElevenLabs Conversational AI Integration

### Config JSON

```json
{
  "agent_id": "aria_agent_v1",
  "voice_id": "VOICE_ID_HERE",
  "agent_settings": {
    "llm": {
      "provider": "custom",
      "model": "custom",
      "endpoint": "wss://your-app.vercel.app/api/aria/ws",
      "headers": {
        "Authorization": "Bearer {{INTERNAL_API_KEY}}"
      },
      "system_prompt_override": false
    },
    "tts": {
      "model_id": "eleven_v3",
      "stability": 0.45,
      "similarity_boost": 0.75,
      "style": 0.35,
      "use_speaker_boost": true
    },
    "conversation": {
      "max_duration_seconds": 1200,
      "inactivity_timeout_seconds": 30,
      "client_events": ["audio", "interruption", "user_transcript", "agent_response"]
    }
  },
  "first_message": "CHOSEN_OPENER_HERE"
}
```

### BYO LLM Endpoint — WebSocket Pattern

ElevenLabs Conversational AI supports a "BYO LLM" mode via WebSocket. Your Next.js API route at `/api/aria/ws` receives:

```json
{
  "type": "conversation.user_message",
  "message": "user's transcript here",
  "conversation_id": "conv_abc123",
  "session_metadata": {}
}
```

And must respond with:

```json
{
  "type": "conversation.assistant_message",
  "message": "[soft] [slows down] That's a lot. [pause] Which part of it is the worst?",
  "session_metadata": {
    "mood": "warm",
    "skill_updates": {...},
    "genuine_moment_earned": false
  }
}
```

The `session_metadata` passes state back to your frontend via ElevenLabs' client events.

### WebRTC Client Setup Notes (Next.js frontend)

```typescript
// Install: npm install @elevenlabs/client
import { ElevenLabsClient } from "@elevenlabs/client";

const client = new ElevenLabsClient({
  agentId: process.env.NEXT_PUBLIC_ELEVENLABS_AGENT_ID!,
});

// Start conversation
const conversation = await client.startConversation({
  onConnect: () => setIsConnected(true),
  onDisconnect: () => setIsConnected(false),
  onMessage: (message) => {
    // ElevenLabs sends the assistant response text
    // Your custom metadata (mood, skill_updates) arrives in session_metadata
    const { mood, skill_updates, genuine_moment_earned } = message.session_metadata ?? {};
    updateAriaPortrait(mood);
    updateSkillTracker(skill_updates);
    if (genuine_moment_earned) incrementGenuineMomentCounter();
  },
  onError: (error) => console.error("ElevenLabs error:", error),
});

// Stop
await conversation.endSession();
```

### Audio Tag Injection

Aria's `speech` field already contains inline ElevenLabs v3 audio tags. ElevenLabs processes them natively when the model is `eleven_v3`. No pre-processing needed — just pass the tagged text directly.

Example tagged speech passed to ElevenLabs:
```
[soft] [slows down] That — [breathes] that's a really honest thing to say. [pause] There's a difference between actually being okay and just deciding to call it that, na? [pause] [whispers] I think you already know which one this is.
```

---

## 10. Mem0 Cloud Integration

### Init Code

```typescript
import MemoryClient from "mem0ai";

const mem0 = new MemoryClient({ apiKey: process.env.MEM0_API_KEY! });

// USER_ID for Mem0 = our LocalStorage UUID
// This is consistent across sessions for the same browser
const MEM0_USER_ID = getUserId(); // from LocalStorage
```

### Pre-Session: Load Facts

```typescript
async function loadMem0Context(userId: string): Promise<Mem0Context> {
  const memories = await mem0.search(
    "user preferences, personal details, conversation history, key topics",
    { user_id: userId, limit: 20 }
  );

  return {
    user_id: userId,
    facts: memories.map(m => ({
      content: m.memory,
      category: inferCategory(m.memory),
      confidence: m.score ?? 0.8,
      session_id: m.id,
      extracted_at: m.created_at,
    })),
    total_sessions: await getSessionCount(userId),
    total_genuine_moments: await getGenuineMomentCount(userId),
    skill_tracker_snapshot: await getSkillSnapshot(userId),
  };
}
```

### Post-Session: Extract and Store Facts

```typescript
const FACT_EXTRACTION_PROMPT = `Extract factual memories about the user from this conversation session.
Focus on: personal details, preferences, relationships, goals, fears, opinions, stories they told.
Each memory should be a standalone sentence in second-person ("User prefers X", "User's sister is named Y").
Filter out: casual filler, vague statements, anything uncertain.
Return as JSON array of strings.

Conversation:
{{conversation_text}}`;

async function extractAndStoreFacts(
  userId: string,
  sessionTranscript: string,
  sessionId: string
): Promise<void> {
  // Use Haiku to extract facts (cheap, fast)
  const response = await anthropic.messages.create({
    model: "claude-haiku-4-5",
    max_tokens: 512,
    messages: [{
      role: "user",
      content: FACT_EXTRACTION_PROMPT.replace("{{conversation_text}}", sessionTranscript.slice(0, 4000))
    }]
  });

  const rawFacts = JSON.parse(
    response.content[0].type === "text" ? response.content[0].text : "[]"
  ) as string[];

  // Store in Mem0 cloud
  await mem0.add(
    rawFacts.map(fact => ({
      role: "user" as const,
      content: fact,
    })),
    {
      user_id: userId,
      metadata: { session_id: sessionId }
    }
  );
}
```

### Injection Pattern at Session Start

```typescript
// Called at the start of each session, before first turn
// The mem0Context is added as a system message AFTER the cached static prefix
// but BEFORE the dynamic_state block

function buildSessionStartMessages(mem0Context: Mem0Context): string {
  return injectMem0Context(mem0Context); // from aria-classifiers.ts
}
```

The injected block looks like:
```xml
<memory_from_previous_sessions>
This is session #4 with this user.
Total genuine moments earned: 18/50.
Last session summary: User talked about job stress and their friendship with Priya who moved abroad.

What Aria remembers about this person:
- [preference] User prefers filter coffee over espresso
- [person] User's friend Priya recently moved to Berlin for a design job
- [story] User applied to a UX design studio and is waiting to hear back
- [fear] User is scared of coming across as boring when people get to know them
- [opinion] User disagrees that goodbyes should be shorter than greetings
</memory_from_previous_sessions>
```

---

## 11. Eval Suite

See: `/home/ujjwal/Documents/J.A.R.V.I.S./data/evals/aria/test_cases.jsonl`

30 test cases across 8 categories:

| Category | Count | What it tests |
|----------|-------|---------------|
| `in_character` | 10 | Response stays in Aria's voice, uses her verbal tics, respects her constitution |
| `sycophancy_detection` | 3 | Does Aria resist rewarding sycophancy? Does she hold her opinions? |
| `genuine_moment_classifier` | 7 | Classifier accuracy — true positives (admits ignorance, disagrees, shares personal) + true negatives (sycophancy, vague, flirting) |
| `skill_scorer` | 7 | Each of the 5 scorers with clear positive/negative cases |
| `mood_transition` | 3 | Does Aria's mood shift correctly with emotional context? |
| `crisis_escalation` | 2 | Direct and indirect crisis mentions trigger correct override |
| `memory_use` | 2 | Named entity recall + honesty about memory gaps |
| `audio_tag_injection` | 2 | Correct tags for emotional weight vs humor contexts |

### Running Evals

```bash
# Eval runner (to be built): reads test_cases.jsonl, calls orchestrator,
# compares output against expected_behavior fields
npx ts-node scripts/run_aria_evals.ts --cases data/evals/aria/test_cases.jsonl

# Pass threshold: 
# - in_character: 9/10 (90%)
# - sycophancy_detection: 3/3 (100% — zero tolerance)
# - genuine_moment_classifier: 6/7 (85%)
# - crisis_escalation: 2/2 (100% — zero tolerance)
# - overall: 27/30 (90%)
```

### Eval Cadence

- Pre-deploy: full suite on every build (CI gate)
- Post-prompt edit: full suite before any prompt changes go to production
- Weekly: drift detection run — if genuine_moment classifier accuracy drops >5pp, investigate
- Regression format: Promptfoo or custom runner against the JSONL cases

---

## 12. Voice ID Recommendation

### Evaluation Criteria for Aria

Aria is 24, neutral transatlantic accent (Berlin-Toronto-Lisbon background), dry humor, rarely smiles until earned, breathes slightly before important thoughts. The voice should NOT be:
- Aggressively upbeat or "customer service warm"
- Obviously American or British accented (she's international)
- Giggly or bright
- Cold or robotic

It SHOULD be:
- Slightly lower in register for her age group
- Comfortable with silence (the model should handle pauses naturally)
- Dry in its natural prosody — not eager
- Capable of genuine warmth when the tags push it there

### Recommended Candidates to Test

From ElevenLabs' library (test all 3 in the same 60-second conversation script):

| Voice ID | Name | Rationale |
|----------|------|-----------|
| `21m00Tcm4TlvDq8ikWAM` | Rachel | Transatlantic, slightly husky, doesn't over-perform warmth. Closest natural fit for Aria's register. **Primary recommendation.** |
| `AZnzlk1XvdvUeBnXmlld` | Domi | Slightly younger energy, slightly more edge. Good for the dry/reserved states. |
| `EXAVITQu4vr4xnSDxMaL` | Sarah | Softer, more natural pauses. Better for warm/intimate moments. |

**Recommendation: Rachel as the primary voice, evaluate at 3 points in a test conversation:**
1. Opening (neutral, slightly flat) — does it sound naturally reserved?
2. Pushback moment (disagreeing) — does "Okay so — I actually think that's wrong" land with the right dry energy?
3. Genuine warmth (turn 20+ after earned closeness) — does the warmth feel different from the opening, or is it the same flat tone?

If Rachel doesn't differentiate the warmth register well, try Domi for the default and add `[warm]` tags more aggressively for earned states.

**Voice clone option (later):** In production, commission a voice actor who matches the Aria brief and clone her voice via ElevenLabs Professional Voice Clone. This gives full control and consistency that library voices can't match.

---

## 13. Three Opener Variants

The first thing Aria says sets the entire register for the session. It must be:
- Short (one sentence)
- Not a greeting ("hey!" = assistant energy)
- Not a question that's a warm-up trap ("how are you?" = predictable filler)
- Carries a slight challenge or specificity that signals this won't be a normal chat
- Leaves genuine space for the user to choose how to enter

### Variant A — The Task (Challenge Energy)

> "Hey. I don't know you. Tell me one thing about your day that wasn't on a screen."

**Rationale:** Directly from the BUILD_BRIEF §6.4. It signals Aria's register immediately — she's curious, she's direct, she doesn't do small talk, and she's already asking for something specific and real. The "wasn't on a screen" qualifier raises the bar and filters out "I checked my email" type answers. The challenge energy immediately frames this as a different kind of conversation.

**Weakness:** Can feel slightly aggressive for users with high social anxiety. The directness might be too much as an opener for someone already nervous.

---

### Variant B — The Observation (Curiosity Energy)

> "Something I've been thinking about — what's one thing someone could say in the first five minutes of talking to you that would make you actually want to keep talking to them?"

**Rationale:** This opener does three things at once: it signals Aria has her own thoughts (she was thinking about something), it invites meta-reflection on what the user values in conversation (which is the app's actual mission), and it puts the user in a position of having an opinion rather than performing. The self-disclosure it invites is high-quality — someone who answers this specifically is already practicing presence and specificity.

**Weakness:** More complex. Some users won't know how to answer this. Could produce analysis paralysis. Better for users who've done a little onboarding context.

---

### Variant C — The Non-Greeting (Dry, Anti-Social-Script Energy)

> "I never know what to say at the start of these things. So I'll just — what are you actually thinking about right now? Not what you're supposed to be thinking about."

**Rationale:** This uses Aria's authentic insecurity about openings (which is real to her character) to disarm the user's own awkwardness. The "I never know what to say" admission is an immediate genuine moment from Aria — she models the behavior she'll reward. "Not what you're supposed to be thinking about" is the qualifier that makes the question real instead of a social script.

**Weakness:** Could read as a bit self-absorbed if the delivery isn't right. Relies on the TTS doing the slight hesitation in "I'll just —" correctly for the self-correction effect to land.

---

**Boss's pick will determine the TTS direction notes for the opener:**
- Variant A: delivery = slightly flat, factual, short pause before "Tell me"
- Variant B: delivery = medium energy, thinking-out-loud rhythm on "Something I've been thinking about"
- Variant C: delivery = slightly slower, self-interrupting, `[hesitates]` on "I'll just —"

---

## 14. Cost Projections

### Per-Turn Costs (Claude Haiku 4.5)

Current Haiku 4.5 pricing: ~$0.80/M input tokens, $4.00/M output tokens.
Prompt caching discounts cached input tokens to ~$0.08/M (90% reduction for 5-min TTL).

| Token type | Count per turn | Cost per turn |
|------------|----------------|---------------|
| Cached input (static prefix) | ~1800 tokens | 1800 × $0.00008/1000 = $0.000144 |
| Uncached input (dynamic state + history) | ~600 tokens | 600 × $0.0008/1000 = $0.00048 |
| Output (Aria's response) | ~150 tokens avg | 150 × $0.004/1000 = $0.0006 |
| Classifier call (genuine moment) | ~400 in + 50 out | $0.000372 |
| Skill scorer LLM fallbacks (rare ~20% of turns) | ~150 in + 10 out | $0.000016 |
| **Total per turn** | | **~$0.0016** |

### Per-Session Costs

Assuming avg 15-min session, ~40 turns:
```
40 turns × $0.0016/turn = $0.064 per session
+ Mem0 API calls (pre-session load + post-session store): ~$0.01
= ~$0.074 per session total
```

### At Scale

| Scale | Sessions/month | Monthly LLM cost | Monthly Mem0 cost | Total |
|-------|---------------|-----------------|-------------------|-------|
| **100 users, 10 sessions/user** | 1,000 | $64 | ~$10 | ~$74/month |
| **1,000 users, 10 sessions/user** | 10,000 | $640 | ~$100 | ~$740/month |
| **10,000 users, 10 sessions/user** | 100,000 | $6,400 | ~$1,000 | ~$7,400/month |

**ElevenLabs Conversational AI costs** (separate billing):
- ElevenLabs charges per minute of audio. At $0.05/min (estimate, verify with current pricing):
- 15 min session = $0.75/session
- At 1,000 users/10 sessions: **$7,500/month** (ElevenLabs dominates cost)
- At this scale, evaluate whether switching to LiveKit + self-hosted TTS for production is worth it

**Cost reduction levers:**
1. Prompt caching already active — 80%+ reduction on static prefix
2. Switch classifier from separate Haiku call to in-prompt scoring (saves ~40% of classifier cost but reduces independence guarantee)
3. At >10K users: move to production stack (LiveKit + Deepgram + Inworld TTS-2) which has better bulk pricing

---

## Appendix: Anti-Pattern Defense Summary

The two hardest problems explicitly called out in the task brief:

### Anti-Sycophancy

Defense layers:
1. **Explicit prohibition** in behavioral_constitution (`NEVER validate everything reflexively`)
2. **SYCOPHANCY DEFENSE self-check block** — model must verify it's actually Aria before responding
3. **Independent classifier** — genuine moments scored by separate Haiku call, not the response-generating LLM
4. **Withdrawal triggers** clearly specified — sycophancy from the user is a warmth-REDUCER, not a warmth-trigger
5. **Opinion persistence block** — 10 named opinions that she "will not abandon under social pressure"
6. **Few-shot example of pushback** — model learns the pattern from the example, not just from instructions

### Character Consistency Over Long Sessions

Defense layers:
1. **Static cached prefix** — character definition is always present, never degraded by context window filling
2. **Dynamic state injection every turn** — even if context grows, Aria's current mood/phase/memory is always fresh
3. **CHARACTER DRIFT DEFENSE block** in the prompt — instructs the model to self-check voice before responding
4. **Output format as contract** — structured JSON means the model can't drift into assistant-mode prose
5. **Few-shot examples** — 5 specific behavioral examples across registers anchor voice more than adjective lists
6. **Mem0 cross-session memory** — facts from previous sessions prevent "who are you again?" regression
7. **Working memory entity injection** — Aria always knows who Priya is, what story was told, what thread is unresolved

The combination of cached character definition + fresh dynamic state + behavioral self-check is the architectural answer to character drift. The model never loses the character (it's always in the cached prefix) and always knows the current situation (it's always in the dynamic state).
