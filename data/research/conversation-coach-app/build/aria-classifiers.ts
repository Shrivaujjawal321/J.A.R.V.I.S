/**
 * ARIA CLASSIFIERS
 * Contains:
 *   1. Genuine Moment Classifier — is this user turn actually real?
 *   2. Five Skill Scorers (Curiosity / Presence / Self-disclosure / Recovery / Specificity)
 *   3. Behavior Instruction Selector — what should Aria DO this turn?
 *   4. Dynamic State Composer — builds the dynamic_state XML block for the system prompt
 *   5. Memory Update Extractor — parses LLM memory_updates and merges into WorkingMemory
 *   6. Mem0 Context Injector — formats Mem0 facts into system prompt injection
 *
 * Design decisions:
 * - Genuine moment classifier is a SEPARATE lightweight Haiku call (not the main LLM).
 *   This gives us an independent signal. Both the main LLM and the classifier must agree.
 * - Skill scorers are HYBRID: rule-based checks first (fast, cheap), LLM only if ambiguous.
 * - Behavior selector is PURE LOGIC — no LLM needed, just state machine on WorkingMemory.
 * - Dynamic state composer is PURE FUNCTION — deterministic, no async.
 */

import Anthropic from "@anthropic-ai/sdk";
import {
  WorkingMemory,
  ConversationState,
  ConversationTurn,
  GenuineMomentClassifierResult,
  GenuineMomentSignal,
  SkillScoreResult,
  BehaviorInstruction,
  BehaviorType,
  EmotionalMoment,
  InsideJoke,
  Story,
  PersonEntity,
  PlaceEntity,
  PreferenceEntity,
  AriaMood,
} from "./aria-types";
import { v4 as uuidv4 } from "uuid";

// ---------------------------------------------------------------------------
// ANTHROPIC CLIENT (shared with orchestrator via module-level singleton)
// ---------------------------------------------------------------------------

const anthropic = new Anthropic({
  apiKey: process.env.ANTHROPIC_API_KEY!,
});

// ---------------------------------------------------------------------------
// 1. GENUINE MOMENT CLASSIFIER
// ---------------------------------------------------------------------------

/**
 * Runs a lightweight Haiku call to determine if the user's turn qualifies
 * as a "genuine moment" for the mechanic counter.
 *
 * Anti-sycophancy design: We use a SEPARATE classifier (not the same Haiku call
 * that generates the response). The main LLM knows it will score genuine moments,
 * which could bias it to generate warmth. The classifier sees the same turn
 * independently and produces a second opinion. Both must agree.
 *
 * False positive defense: The classifier explicitly checks for disqualifying
 * patterns — generic platitudes, sycophancy, repeat content — before scoring.
 *
 * Confidence threshold: 0.70 — calibrated to avoid both false positives
 * (rewarding performance) and false negatives (missing real moments).
 */
export async function runGenuineMomentClassifier(
  userTranscript: string,
  previousTurns: ConversationTurn[],
  workingMemory: WorkingMemory
): Promise<GenuineMomentClassifierResult> {
  const recentContext = previousTurns
    .slice(-4)
    .map((t) => `${t.role}: ${t.text}`)
    .join("\n");

  const classifierPrompt = `You are a classifier for a conversation coaching app. Your job is to determine if a user's conversational turn qualifies as a "genuine moment."

A GENUINE MOMENT is one where the user does something specifically real and unrehearsed — not a performance.

QUALIFYING SIGNALS (mark is_genuine: true if ANY of these are clearly present):
- "admits_not_knowing": User explicitly says they don't know something, can't figure something out, or is confused — without embarrassment or deflection
- "disagrees_with_aria": User specifically pushes back on something Aria said, with their own perspective
- "shares_personal_unprompted": User shares a specific personal fact, memory, or feeling that wasn't directly asked for
- "asks_surprising_question": User asks Aria something unexpected that shows they were genuinely thinking about her, not just the surface topic
- "stays_after_awkward": User stays engaged and responds authentically after a moment of friction, silence, or awkward honesty
- "sits_in_silence": User uses ellipsis or indicates pause/thought rather than filling with filler

DISQUALIFYING PATTERNS (mark is_genuine: false if ANY of these are present):
- Generic compliment to Aria ("you're so understanding", "I love talking to you")
- Sycophancy ("that's such a great point", "exactly!")
- Explicit flirting or romantic content
- Verbatim or near-verbatim repeat of something said earlier this session
- Vague abstraction ("I've just been feeling off", "things are okay I guess")
- Single-word or near-empty response ("yeah", "okay", "sure")
- Filling silence with irrelevant content

RECENT CONVERSATION CONTEXT:
${recentContext}

USER'S CURRENT TURN:
"${userTranscript}"

Return ONLY valid JSON:
{
  "is_genuine": boolean,
  "signal": one of ["admits_not_knowing","disagrees_with_aria","shares_personal_unprompted","asks_surprising_question","stays_after_awkward","sits_in_silence"] or null,
  "confidence": float between 0.0 and 1.0,
  "disqualifying_reason": string or null
}`;

  try {
    const response = await anthropic.messages.create({
      model: "claude-haiku-4-5",
      max_tokens: 256,
      messages: [{ role: "user", content: classifierPrompt }],
    });

    const rawText = response.content[0].type === "text" ? response.content[0].text : "{}";
    const cleaned = rawText.replace(/^```json\n?/, "").replace(/\n?```$/, "").trim();
    const parsed = JSON.parse(cleaned) as GenuineMomentClassifierResult;

    // Validate signal is one of the valid types
    const validSignals: GenuineMomentSignal[] = [
      "admits_not_knowing",
      "disagrees_with_aria",
      "shares_personal_unprompted",
      "asks_surprising_question",
      "sits_in_silence",
      "stays_after_awkward",
    ];

    if (parsed.signal && !validSignals.includes(parsed.signal)) {
      parsed.signal = null;
    }

    // If disqualifying reason is present, force is_genuine to false
    if (parsed.disqualifying_reason) {
      parsed.is_genuine = false;
    }

    return parsed;
  } catch (err) {
    console.error("[genuine-moment-classifier] Failed:", err);
    // Safe default: not genuine
    return {
      is_genuine: false,
      signal: null,
      confidence: 0,
      disqualifying_reason: "classifier_error",
    };
  }
}

// ---------------------------------------------------------------------------
// 2. FIVE SKILL SCORERS
// Hybrid: rule-based fast checks first; LLM confirmation for ambiguous cases.
// Each scorer returns 0 or 1 for this turn.
// ---------------------------------------------------------------------------

export async function runSkillScorers(
  userTranscript: string,
  previousTurns: ConversationTurn[],
  workingMemory: WorkingMemory
): Promise<SkillScoreResult> {
  const transcript = userTranscript.toLowerCase();
  const lastAriaTurn = [...previousTurns].reverse().find((t) => t.role === "aria");
  const lastAriaText = lastAriaTurn?.text?.toLowerCase() ?? "";

  // Run rule-based checks in parallel
  const [curiosity, presence, selfDisclosure, recovery, specificity] =
    await Promise.all([
      scoresCuriosity(transcript, lastAriaText, previousTurns),
      scoresPresence(transcript),
      scoresSelfDisclosure(transcript, previousTurns),
      scoresRecovery(transcript, previousTurns, workingMemory),
      scoresSpecificity(transcript),
    ]);

  return {
    curiosity,
    presence,
    self_disclosure: selfDisclosure,
    recovery,
    specificity,
  };
}

/**
 * CURIOSITY: +1 if user asks a specific follow-up on something Aria mentioned.
 * Rule: User turn contains a question + references a noun/concept from Aria's last turn.
 */
async function scoresCuriosity(
  transcript: string,
  lastAriaText: string,
  previousTurns: ConversationTurn[]
): Promise<0 | 1> {
  // Must contain a question indicator
  const hasQuestion =
    transcript.includes("?") ||
    /\b(why|what|how|when|where|who|tell me about|curious about)\b/.test(transcript);

  if (!hasQuestion) return 0;

  // Fast path: extract nouns from Aria's last turn and check if user referenced one
  const ariaNouns = extractSignificantNouns(lastAriaText);
  const referencesAria = ariaNouns.some((noun) => transcript.includes(noun));

  if (referencesAria) return 1;

  // Generic follow-ups ("tell me more", "interesting, go on") don't qualify
  const isGenericFollowup = /\b(tell me more|go on|interesting|what else|and then)\b/.test(
    transcript
  );

  if (isGenericFollowup) return 0;

  // Ambiguous — fast LLM check
  return (await llmBinaryCheck(
    transcript,
    `Did this user turn ask a specific follow-up question about something Aria said? (Not a generic "tell me more" — a specific question about a named thing or idea Aria mentioned.) Previous Aria context: "${lastAriaText.slice(0, 200)}"`
  ))
    ? 1
    : 0;
}

/**
 * PRESENCE: +1 if user answer contains 2+ concrete sensory or specific details.
 * Rule: proper nouns, colors, numbers, named places, physical sensations.
 */
async function scoresPresence(transcript: string): Promise<0 | 1> {
  let concreteCount = 0;

  // Numbers
  if (/\b\d+\b/.test(transcript)) concreteCount++;
  // Proper nouns (capitalized words that aren't "I" at the start)
  const properNouns = transcript.match(/\b[A-Z][a-z]+\b/g) ?? [];
  if (properNouns.length >= 1) concreteCount++;
  // Color references
  if (/\b(red|blue|green|white|black|yellow|orange|purple|brown|grey|gray)\b/.test(transcript))
    concreteCount++;
  // Physical sensation words
  if (
    /\b(smell|taste|sound|felt|heard|saw|touch|warm|cold|loud|quiet|bright|dark)\b/.test(
      transcript
    )
  )
    concreteCount++;
  // Named places or specific locations
  if (/\b(street|road|lane|avenue|city|town|village|school|office|park|café|restaurant)\b/.test(
    transcript
  ))
    concreteCount++;

  return concreteCount >= 2 ? 1 : 0;
}

/**
 * SELF-DISCLOSURE: +1 if user shares something true about themselves, unprompted.
 * Rule: first-person + personal verb + NOT a direct response to a direct personal question.
 */
async function scoresSelfDisclosure(
  transcript: string,
  previousTurns: ConversationTurn[]
): Promise<0 | 1> {
  // Must be first-person
  const hasFirstPerson = /\b(i |i'm |i've |i was |i feel |my |mine )\b/.test(transcript);
  if (!hasFirstPerson) return 0;

  // Check if this is just answering a direct Aria question (not unprompted)
  const lastAriaTurn = [...previousTurns].reverse().find((t) => t.role === "aria");
  const ariaAskedDirect =
    lastAriaTurn?.text?.includes("?") &&
    /\b(you|your)\b/.test(lastAriaTurn.text.toLowerCase());

  if (ariaAskedDirect) {
    // If Aria directly asked, it's only disclosure if the user volunteers MORE than asked
    // Fast LLM check for ambiguous cases
    return (await llmBinaryCheck(
      transcript,
      `Aria asked a direct question. Did the user share MORE personal information than what was directly asked? Look for self-disclosure that goes beyond the question scope.`
    ))
      ? 1
      : 0;
  }

  // Unprompted personal share — check it's substantive (>8 words)
  const wordCount = transcript.split(/\s+/).length;
  if (wordCount < 8) return 0;

  // Check for personal content words
  const hasPersonalContent =
    /\b(feel|felt|think|believe|remember|experience|when i|growing up|my [a-z]|afraid|scared|hope|wish|dream|hate|love|dislike|regret)\b/.test(
      transcript
    );

  return hasPersonalContent ? 1 : 0;
}

/**
 * RECOVERY: +1 if user stays engaged AFTER an awkward moment / pushback from Aria.
 * Rule: The previous Aria turn must have been pushback/friction AND user continues engaging.
 */
async function scoresRecovery(
  transcript: string,
  previousTurns: ConversationTurn[],
  workingMemory: WorkingMemory
): Promise<0 | 1> {
  const lastAriaTurn = [...previousTurns].reverse().find((t) => t.role === "aria");
  if (!lastAriaTurn) return 0;

  // Did Aria push back or create friction in her last turn?
  const ariaPushedBack =
    /\b(okay so|i don't think|i actually think|i disagree|that's not quite|wait —|hold on)\b/.test(
      lastAriaTurn.text.toLowerCase()
    );

  const ariaWentFlat =
    lastAriaTurn.mood === "reserved" ||
    workingMemory.last_turn_emotional_weight > 0.5;

  const wasAwkward = ariaPushedBack || ariaWentFlat;

  if (!wasAwkward) return 0;

  // User stayed in — did they respond substantively? (>10 words, not a deflection)
  const wordCount = transcript.split(/\s+/).length;
  const isDeflection = /\b(whatever|sure|okay|yeah yeah|fine)\b/.test(transcript.toLowerCase());

  return wordCount >= 10 && !isDeflection ? 1 : 0;
}

/**
 * SPECIFICITY: +1 if user's answer contains proper nouns, specific numbers, or named things.
 * This is the easiest score to earn — encourages concrete language.
 */
async function scoresSpecificity(transcript: string): Promise<0 | 1> {
  // Proper nouns (capitalized mid-sentence — not just "I")
  const properNounPattern = /(?<![.?!]\s)\b[A-Z][a-z]{2,}\b/g;
  const properNouns = transcript.match(properNounPattern) ?? [];

  // Numbers (any kind)
  const hasNumbers = /\b\d+[\d,.]*/g.test(transcript);

  // Named specific things: days, months, brands, titles
  const hasNamedThings =
    /\b(monday|tuesday|wednesday|thursday|friday|saturday|sunday|january|february|march|april|may|june|july|august|september|october|november|december)\b/.test(
      transcript.toLowerCase()
    );

  return (properNouns.length >= 1 || hasNumbers || hasNamedThings) ? 1 : 0;
}

// ---------------------------------------------------------------------------
// 3. BEHAVIOR INSTRUCTION SELECTOR
// Pure state machine — no LLM. Looks at WorkingMemory and determines
// what TYPE of response Aria should produce this turn.
// Returns behaviors sorted by priority (top 2 are injected into the prompt).
// ---------------------------------------------------------------------------

export async function selectBehaviors(
  state: ConversationState
): Promise<BehaviorInstruction[]> {
  const memory = state.working_memory;
  const turnCount = memory.turn_count;
  const behaviors: BehaviorInstruction[] = [];

  // HOLD_SPACE: If last turn had high emotional weight, do NOT pivot
  if (memory.last_turn_emotional_weight > 0.6) {
    behaviors.push({
      type: "HOLD_SPACE",
      description: "Previous turn had emotional weight — hold it, don't pivot to new topic",
      priority: 1, // highest priority
    });
  }

  // EMOTIONAL_FOLLOWUP: Flagged emotional moment that hasn't been followed up
  for (const moment of memory.emotional_moments) {
    if (
      !moment.followed_up &&
      turnCount - moment.turn >= 4 &&
      turnCount - moment.turn <= 7
    ) {
      behaviors.push({
        type: "EMOTIONAL_FOLLOWUP",
        description: `Gently check in on: "${moment.description}" from turn ${moment.turn}`,
        priority: 2,
      });
    }
  }

  // CALLBACK: Unresolved thread in the return window
  for (const thread of memory.unresolved_threads) {
    if (
      turnCount - thread.first_mentioned_turn >= 3 &&
      turnCount - thread.first_mentioned_turn <= 6 &&
      thread.attempts < 2 // don't try more than twice
    ) {
      behaviors.push({
        type: "CALLBACK",
        description: `Return to "${thread.topic}" from turn ${thread.first_mentioned_turn} — user moved on without resolving it`,
        priority: 3,
      });
    }
  }

  // PUSHBACK: User made a questionable claim last turn
  if (memory.last_turn_has_questionable_claim) {
    behaviors.push({
      type: "PUSHBACK",
      description: "User's last claim deserves a direct, warm disagreement with one specific reason",
      priority: 3,
    });
  }

  // CALLBACK_HUMOR: Inside joke opportunity (8-15 turns after setup)
  for (const joke of memory.inside_jokes) {
    if (
      !joke.used_back &&
      turnCount - joke.turn >= 8 &&
      turnCount - joke.turn <= 15
    ) {
      behaviors.push({
        type: "CALLBACK_HUMOR",
        description: `Playfully reference "${joke.source_quote}" from turn ${joke.turn}`,
        priority: 4,
      });
    }
  }

  // INITIATE: Proactive topic (if no strong user-led thread and queue has something)
  const hasActiveUserThread = memory.unresolved_threads.some(
    (t) => turnCount - t.first_mentioned_turn < 3
  );

  if (!hasActiveUserThread && memory.proactive_queue.length > 0 && turnCount % 4 === 0) {
    behaviors.push({
      type: "INITIATE",
      description: `Proactively bring up: ${memory.proactive_queue[0]}`,
      priority: 5,
    });
  }

  // Sort by priority (lower number = higher priority) and take top 2
  const top2 = behaviors
    .sort((a, b) => a.priority - b.priority)
    .slice(0, 2);

  // Default if nothing
  if (top2.length === 0) {
    return [
      {
        type: "DEFAULT",
        description: "Natural response — no special behavior instruction this turn",
        priority: 99,
      },
    ];
  }

  return top2;
}

// ---------------------------------------------------------------------------
// 4. DYNAMIC STATE COMPOSER
// Builds the <dynamic_state> XML block that gets injected fresh every turn.
// Pure function — deterministic, no side effects.
// ---------------------------------------------------------------------------

export function composeDynamicState(
  state: ConversationState,
  behaviors: BehaviorInstruction[]
): string {
  const mem = state.working_memory;

  // Format people entities
  const peopleList =
    Object.values(mem.entities.people)
      .map((p) => `${p.name} (${p.relationship ?? "unspecified"}, context: ${p.context ?? "general"})`)
      .join("; ") || "none yet";

  // Format stories
  const storiesList =
    mem.stories
      .map((s) => `"${s.summary}" (weight: ${s.emotional_weight.toFixed(1)}, resolved: ${s.resolved})`)
      .join("; ") || "none yet";

  // Format unresolved threads
  const threadsList =
    mem.unresolved_threads
      .filter((t) => t.attempts < 2)
      .map((t) => `"${t.topic}" (first mentioned turn ${t.first_mentioned_turn})`)
      .join("; ") || "none";

  // Format inside jokes
  const jokesList =
    mem.inside_jokes
      .filter((j) => !j.used_back)
      .map((j) => `"${j.source_quote}" from turn ${j.turn}`)
      .join("; ") || "none";

  // Format pending emotional moments
  const pendingEmotional =
    mem.emotional_moments
      .filter((e) => !e.followed_up)
      .map((e) => `turn ${e.turn}: "${e.description}" (weight: ${e.weight.toFixed(1)})`)
      .join("; ") || "none";

  // Format behavior instructions
  const behaviorText = behaviors
    .map((b) => `${b.type}: ${b.description}`)
    .join("\n");

  return `<dynamic_state>
Current mood: ${state.current_mood}
Energy: ${state.current_energy.toFixed(2)}
Session number: ${state.session_number}
Relationship depth: ${state.relationship_depth}/100
Conversation phase: ${state.current_phase}
Genuine moments so far this session: ${state.session_genuine_moment_count}
Total genuine moments (all time): ${state.genuine_moment_count}/50 to graduation

Working memory (this session):
People mentioned: ${peopleList}
Stories told: ${storiesList}
Unresolved threads: ${threadsList}
Inside jokes / quotable phrases: ${jokesList}
Emotional moments pending follow-up: ${pendingEmotional}

Behavior instructions for this turn:
${behaviorText}
</dynamic_state>

<output_format>
CRITICAL: Return a JSON object with these exact fields. No prose outside the JSON.
{
  "speech": "<Aria's spoken response with inline ElevenLabs v3 audio tags>",
  "mood": "<one of: neutral | curious | warm | amused | reserved>",
  "energy": <float 0.0-1.0>,
  "is_genuine_moment": <true | false>,
  "skill_signals": {
    "curiosity": <0 or 1>,
    "presence": <0 or 1>,
    "self_disclosure": <0 or 1>,
    "recovery": <0 or 1>,
    "specificity": <0 or 1>
  },
  "memory_updates": {
    "new_entities": [],
    "new_stories": [],
    "new_emotional_moment": null,
    "quotable_phrase": null,
    "thread_resolved": null,
    "thread_dodged": null
  },
  "crisis_signal": <true | false>
}
</output_format>`;
}

// ---------------------------------------------------------------------------
// 5. MEMORY UPDATE EXTRACTOR
// Merges the LLM's memory_updates field into the current WorkingMemory.
// ---------------------------------------------------------------------------

export async function extractMemoryUpdates(
  userTranscript: string,
  memoryUpdates: import("./aria-types").AriaLLMOutput["memory_updates"],
  currentMemory: WorkingMemory,
  turnCount: number
): Promise<WorkingMemory> {
  const updated: WorkingMemory = JSON.parse(JSON.stringify(currentMemory)); // deep clone

  // Apply new entities
  for (const entityUpdate of memoryUpdates.new_entities) {
    if (entityUpdate.type === "person") {
      const person = entityUpdate.data as PersonEntity;
      updated.entities.people[person.name] = person;
    } else if (entityUpdate.type === "place") {
      const place = entityUpdate.data as PlaceEntity;
      updated.entities.places[place.name] = place;
    } else if (entityUpdate.type === "preference") {
      const pref = entityUpdate.data as PreferenceEntity;
      updated.entities.preferences[pref.topic] = pref;
    }
  }

  // Apply new stories
  for (const story of memoryUpdates.new_stories) {
    // Deduplicate by summary
    const exists = updated.stories.some((s) => s.summary === story.summary);
    if (!exists) {
      updated.stories.push({ ...story, id: uuidv4() });
    }
  }

  // Apply new emotional moment
  if (memoryUpdates.new_emotional_moment) {
    updated.emotional_moments.push({
      ...memoryUpdates.new_emotional_moment,
      id: uuidv4(),
      turn: turnCount,
      followed_up: false,
    });
  }

  // Apply quotable phrase → inside joke
  if (memoryUpdates.quotable_phrase) {
    const alreadyTracked = updated.inside_jokes.some(
      (j) => j.source_quote === memoryUpdates.quotable_phrase
    );
    if (!alreadyTracked) {
      updated.inside_jokes.push({
        id: uuidv4(),
        source_quote: memoryUpdates.quotable_phrase,
        turn: turnCount,
        used_back: false,
      });
    }
  }

  // Resolve a thread
  if (memoryUpdates.thread_resolved) {
    const thread = updated.unresolved_threads.find(
      (t) => t.id === memoryUpdates.thread_resolved
    );
    if (thread) {
      updated.unresolved_threads = updated.unresolved_threads.filter(
        (t) => t.id !== memoryUpdates.thread_resolved
      );
    }
  }

  // Mark a thread as dodged
  if (memoryUpdates.thread_dodged) {
    const thread = updated.unresolved_threads.find(
      (t) => t.id === memoryUpdates.thread_dodged
    );
    if (thread) {
      thread.dodge_turns.push(turnCount);
      thread.attempts += 1;
    }
  }

  // Language register detection — simple heuristic
  // If user writes >15% Hindi/Hinglish markers, switch register
  const hinglishMarkers = /\b(haan|yaar|matlab|achha|theek|bas|bilkul|na|aur)\b/gi;
  const hinglishMatches = (userTranscript.match(hinglishMarkers) ?? []).length;
  const wordCount = userTranscript.split(/\s+/).length;

  if (hinglishMatches / wordCount > 0.1) {
    updated.language_register = "hinglish";
  }

  return updated;
}

// ---------------------------------------------------------------------------
// 6. MEM0 CONTEXT INJECTOR
// Formats stored Mem0 facts into a block that gets prepended to the
// first message of a new session.
// ---------------------------------------------------------------------------

export function injectMem0Context(
  mem0Context: import("./aria-types").Mem0Context
): string {
  if (!mem0Context.facts || mem0Context.facts.length === 0) {
    return "";
  }

  const factLines = mem0Context.facts
    .filter((f) => f.confidence >= 0.6) // only inject high-confidence facts
    .slice(0, 15) // cap at 15 facts to keep injection tight
    .map((f) => `- [${f.category}] ${f.content}`)
    .join("\n");

  const sessionInfo = mem0Context.last_session_summary
    ? `\nLast session summary: ${mem0Context.last_session_summary}`
    : "";

  return `<memory_from_previous_sessions>
This is session #${mem0Context.total_sessions} with this user.
Total genuine moments earned: ${mem0Context.total_genuine_moments}/50.
${sessionInfo}

What Aria remembers about this person:
${factLines}
</memory_from_previous_sessions>`;
}

// ---------------------------------------------------------------------------
// UTIL: LIGHTWEIGHT LLM BINARY CHECK
// Used by skill scorers for ambiguous cases. Haiku call, tight prompt.
// Returns true/false only.
// ---------------------------------------------------------------------------

async function llmBinaryCheck(
  transcript: string,
  question: string
): Promise<boolean> {
  try {
    const response = await anthropic.messages.create({
      model: "claude-haiku-4-5",
      max_tokens: 16,
      messages: [
        {
          role: "user",
          content: `User said: "${transcript.slice(0, 200)}"\n\n${question}\n\nAnswer with only "yes" or "no".`,
        },
      ],
    });

    const text =
      response.content[0].type === "text"
        ? response.content[0].text.toLowerCase().trim()
        : "no";

    return text.startsWith("yes");
  } catch {
    return false; // safe default
  }
}

// ---------------------------------------------------------------------------
// UTIL: EXTRACT SIGNIFICANT NOUNS from text
// Used by curiosity scorer to check if user referenced an Aria topic.
// Simple heuristic: capitalized words + known content words.
// ---------------------------------------------------------------------------

function extractSignificantNouns(text: string): string[] {
  // Proper nouns
  const properNouns = text.match(/\b[A-Z][a-z]{2,}\b/g) ?? [];
  // Long content words (>5 chars, probably not stopwords)
  const contentWords = text
    .split(/\s+/)
    .filter((w) => w.length > 5 && !/^(there|about|which|their|would|could|should|really|still|might|being|having|doing)$/i.test(w))
    .map((w) => w.toLowerCase());

  return [...new Set([...properNouns.map((n) => n.toLowerCase()), ...contentWords])];
}
