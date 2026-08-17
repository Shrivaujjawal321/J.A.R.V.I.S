/**
 * ARIA PER-TURN ORCHESTRATOR
 * Next.js API route: POST /api/aria/turn
 *
 * Pipeline per turn:
 *   1. Run genuine-moment classifier + skill scorer IN PARALLEL with behavior selector
 *   2. Compose dynamic_state block
 *   3. Call Claude Haiku 4.5 with static cached prefix + dynamic state + conversation history
 *   4. Parse structured JSON output
 *   5. Update working memory + skill tracker
 *   6. Return speech text + state updates to frontend
 *
 * Architecture decisions:
 * - Claude Haiku 4.5 with prompt caching (static prefix is ~1800 tokens, well above 1024 threshold)
 * - Structured output via the output_format block in the system prompt — more reliable than JSON Mode for complex schemas
 * - All classifier calls are Haiku too (not a separate model) — saves latency, same quality bar
 * - No Hume in MVP (emotion detection is Phase 2) — classifier-inferred mood only
 * - ElevenLabs Conversational AI handles VAD/STT/turn detection on the frontend
 */

import Anthropic from "@anthropic-ai/sdk";
import {
  ConversationState,
  ConversationTurn,
  OrchestratorInput,
  OrchestratorOutput,
  AriaLLMOutput,
  BehaviorInstruction,
  WorkingMemory,
  SkillTracker,
  AriaMood,
  GenuineMoment,
  SKILL_LEVEL_THRESHOLD,
} from "./aria-types";
import {
  runGenuineMomentClassifier,
  runSkillScorers,
} from "./aria-classifiers";
import { selectBehaviors } from "./aria-classifiers";
import { composeDynamicState } from "./aria-classifiers";
import { extractMemoryUpdates } from "./aria-classifiers";
import { injectMem0Context } from "./aria-classifiers";

// ---------------------------------------------------------------------------
// ANTHROPIC CLIENT — singleton to share connection
// ---------------------------------------------------------------------------

const anthropic = new Anthropic({
  apiKey: process.env.ANTHROPIC_API_KEY!,
});

// ---------------------------------------------------------------------------
// LOAD STATIC SYSTEM PROMPT (cached prefix)
// Loaded once at module level so it doesn't re-read file per request.
// In production, this would be bundled at build time.
// ---------------------------------------------------------------------------

import { readFileSync } from "fs";
import { join } from "path";

const ARIA_STATIC_PROMPT = readFileSync(
  join(process.cwd(), "data/research/conversation-coach-app/build/aria-system-prompt.xml"),
  "utf-8"
);

// Strip the dynamic_state placeholder block from the static portion.
// The orchestrator injects a fresh dynamic_state each turn.
const ARIA_STATIC_PREFIX = ARIA_STATIC_PROMPT
  .split("<!-- ============================================================")
  .find((part) => part.includes("STATIC CACHED PREFIX"))
  ?.split("<!-- ============================================================")[0] ?? ARIA_STATIC_PROMPT;

// ---------------------------------------------------------------------------
// MAIN ORCHESTRATOR FUNCTION
// ---------------------------------------------------------------------------

/**
 * processAriaTurn — the single exported function the API route calls.
 *
 * @param input - User transcript + full conversation state
 * @returns Orchestrator output: speech text, updated state, skill/moment updates
 */
export async function processAriaTurn(
  input: OrchestratorInput
): Promise<OrchestratorOutput> {
  const { user_transcript, conversation_state, previous_turns, is_first_turn } = input;

  // -------------------------------------------------------------------------
  // STAGE 1: PARALLEL PRE-PROCESSING
  // Run classifiers and behavior selection concurrently.
  // These don't depend on each other, so run them together.
  // -------------------------------------------------------------------------

  const [classifierResult, skillResult, behaviors] = await Promise.all([
    // Genuine moment classifier — is this turn "real"?
    runGenuineMomentClassifier(
      user_transcript,
      previous_turns,
      conversation_state.working_memory
    ),
    // Five skill scorers
    runSkillScorers(
      user_transcript,
      previous_turns,
      conversation_state.working_memory
    ),
    // Behavior instruction selector — what should Aria DO this turn?
    selectBehaviors(conversation_state),
  ]);

  // -------------------------------------------------------------------------
  // STAGE 2: COMPOSE DYNAMIC STATE BLOCK
  // This is the non-cached portion of the system prompt — changes every turn.
  // -------------------------------------------------------------------------

  const dynamicStateBlock = composeDynamicState(
    conversation_state,
    behaviors
  );

  // Full system prompt = static cached prefix + fresh dynamic state
  const fullSystemPrompt = `${ARIA_STATIC_PREFIX}\n\n${dynamicStateBlock}`;

  // -------------------------------------------------------------------------
  // STAGE 3: CALL CLAUDE HAIKU 4.5
  // Static prefix is marked for caching — saves ~80% on those tokens.
  // Dynamic state is never cached (changes every turn by definition).
  // -------------------------------------------------------------------------

  // Format conversation history for the messages array.
  // ElevenLabs Conv AI provides the transcript — we pass it as the user message.
  // Previous turns are in the messages array for context.
  const messages = buildMessageHistory(previous_turns, user_transcript);

  let llmOutput: AriaLLMOutput;

  try {
    const response = await anthropic.messages.create({
      model: "claude-haiku-4-5",
      max_tokens: 1024,
      // Prompt caching on the static system prompt prefix.
      // The cache_control block goes on the last chunk of the system prompt
      // that is stable — everything before dynamic_state.
      system: [
        {
          type: "text",
          text: ARIA_STATIC_PREFIX,
          // Cache the stable character definition + persona + examples
          cache_control: { type: "ephemeral" },
        },
        {
          type: "text",
          // Dynamic state injected fresh — NOT cached
          text: dynamicStateBlock,
        },
      ],
      messages,
    });

    // Parse the structured JSON output
    const rawContent = response.content[0];
    if (rawContent.type !== "text") {
      throw new Error("Unexpected non-text response from Haiku");
    }

    llmOutput = parseAriaLLMOutput(rawContent.text);
  } catch (err) {
    console.error("[aria-orchestrator] LLM call failed:", err);
    // Graceful degradation — return a safe fallback response
    llmOutput = buildFallbackOutput(conversation_state);
  }

  // -------------------------------------------------------------------------
  // STAGE 4: HANDLE CRISIS SIGNAL
  // If crisis detected, override speech and return crisis flag immediately.
  // This bypasses all game mechanics — safety over character consistency.
  // -------------------------------------------------------------------------

  if (llmOutput.crisis_signal) {
    return buildCrisisOutput(conversation_state);
  }

  // -------------------------------------------------------------------------
  // STAGE 5: APPLY MEMORY UPDATES
  // Extract entities, stories, emotional moments from this turn and merge
  // into working memory.
  // -------------------------------------------------------------------------

  const updatedMemory = await extractMemoryUpdates(
    user_transcript,
    llmOutput.memory_updates,
    conversation_state.working_memory,
    conversation_state.working_memory.turn_count
  );

  // Update proactive queue: if AI was interrupted, put "return to thought" first
  if (updatedMemory.ai_interrupted_mid_thought) {
    updatedMemory.proactive_queue.unshift("Return to thought I was mid-sentence on");
  }

  // -------------------------------------------------------------------------
  // STAGE 6: UPDATE SKILL TRACKER
  // -------------------------------------------------------------------------

  const updatedSkillTracker = applySkillUpdates(
    conversation_state.skill_tracker,
    llmOutput.skill_signals
  );

  // -------------------------------------------------------------------------
  // STAGE 7: UPDATE GENUINE MOMENT COUNTER
  // Both the LLM's assessment and our classifier must agree (AND logic)
  // to prevent false positives. Classifier confidence threshold: 0.70.
  // -------------------------------------------------------------------------

  const isGenuine =
    llmOutput.is_genuine_moment &&
    classifierResult.is_genuine &&
    classifierResult.confidence >= 0.70;

  let newGenuineMomentTotal = conversation_state.genuine_moment_count;
  let sessionGenuineCount = conversation_state.session_genuine_moment_count;

  if (isGenuine) {
    newGenuineMomentTotal += 1;
    sessionGenuineCount += 1;

    // Store the genuine moment in working memory for session record
    const genuineMoment: GenuineMoment = {
      id: `gm_${Date.now()}`,
      session_id: conversation_state.session_id,
      turn: updatedMemory.turn_count,
      signal: classifierResult.signal!,
      classifier_confidence: classifierResult.confidence,
      user_transcript_snippet: user_transcript.slice(0, 100),
    };
    updatedMemory.genuine_moments.push(genuineMoment);
  }

  // -------------------------------------------------------------------------
  // STAGE 8: UPDATE CONVERSATION STATE
  // Advance mood, energy, phase, relationship depth.
  // -------------------------------------------------------------------------

  const updatedRelationshipDepth = advanceRelationshipDepth(
    conversation_state.relationship_depth,
    skillResult,
    isGenuine,
    llmOutput
  );

  const updatedPhase = computePhase(updatedRelationshipDepth);

  const updatedState: ConversationState = {
    ...conversation_state,
    current_mood: llmOutput.mood,
    current_energy: llmOutput.energy,
    current_phase: updatedPhase,
    relationship_depth: updatedRelationshipDepth,
    genuine_moment_count: newGenuineMomentTotal,
    session_genuine_moment_count: sessionGenuineCount,
    skill_tracker: updatedSkillTracker,
    working_memory: {
      ...updatedMemory,
      turn_count: updatedMemory.turn_count + 1,
      last_turn_emotional_weight: llmOutput.memory_updates.new_emotional_moment?.weight ?? 0,
      last_turn_has_questionable_claim: false, // reset after each turn
    },
    last_turn_at: new Date().toISOString(),
    // Graduation milestone flags
    milestone_10_triggered:
      conversation_state.milestone_10_triggered ||
      (newGenuineMomentTotal >= 10 && !conversation_state.milestone_10_triggered),
    milestone_25_triggered:
      conversation_state.milestone_25_triggered ||
      (newGenuineMomentTotal >= 25 && !conversation_state.milestone_25_triggered),
    milestone_50_triggered:
      conversation_state.milestone_50_triggered ||
      (newGenuineMomentTotal >= 50 && !conversation_state.milestone_50_triggered),
  };

  // -------------------------------------------------------------------------
  // STAGE 9: DETERMINE MILESTONE TRIGGER
  // -------------------------------------------------------------------------

  let milestoneTriggered: null | 10 | 25 | 50 = null;

  if (updatedState.milestone_10_triggered && !conversation_state.milestone_10_triggered) {
    milestoneTriggered = 10;
  } else if (updatedState.milestone_25_triggered && !conversation_state.milestone_25_triggered) {
    milestoneTriggered = 25;
  } else if (updatedState.milestone_50_triggered && !conversation_state.milestone_50_triggered) {
    milestoneTriggered = 50;
  }

  // -------------------------------------------------------------------------
  // STAGE 10: BUILD AND RETURN OUTPUT
  // -------------------------------------------------------------------------

  return {
    speech_text: llmOutput.speech,
    mood: llmOutput.mood,
    updated_state: updatedState,
    skill_updates: llmOutput.skill_signals,
    genuine_moment_earned: isGenuine,
    genuine_moment_total: newGenuineMomentTotal,
    milestone_triggered: milestoneTriggered,
    crisis_signal: false,
  };
}

// ---------------------------------------------------------------------------
// HELPER: BUILD MESSAGE HISTORY
// Formats previous turns as Anthropic messages array.
// Keeps last 10 turns to manage context window.
// ---------------------------------------------------------------------------

function buildMessageHistory(
  previousTurns: ConversationTurn[],
  currentUserTranscript: string
): Anthropic.MessageParam[] {
  // Use last 10 turns for context — prevents context bloat
  // In production, implement sliding window summary for >20 turns
  const recentTurns = previousTurns.slice(-10);

  const messages: Anthropic.MessageParam[] = recentTurns.map((turn) => ({
    role: turn.role === "user" ? "user" : "assistant",
    content: turn.text,
  }));

  // Add the current user turn
  messages.push({
    role: "user",
    content: currentUserTranscript,
  });

  return messages;
}

// ---------------------------------------------------------------------------
// HELPER: PARSE LLM OUTPUT
// The system prompt instructs Haiku to return JSON.
// We parse it here with a fallback for malformed output.
// ---------------------------------------------------------------------------

function parseAriaLLMOutput(rawText: string): AriaLLMOutput {
  // Strip any markdown code fences if Haiku wrapped the JSON
  const cleaned = rawText
    .replace(/^```json\n?/, "")
    .replace(/\n?```$/, "")
    .trim();

  const parsed = JSON.parse(cleaned) as AriaLLMOutput;

  // Validate mood is one of the 5 valid states
  const validMoods: AriaMood[] = ["neutral", "curious", "warm", "amused", "reserved"];
  if (!validMoods.includes(parsed.mood)) {
    parsed.mood = "neutral";
  }

  // Clamp energy to [0, 1]
  parsed.energy = Math.min(1.0, Math.max(0.0, parsed.energy ?? 0.5));

  return parsed;
}

// ---------------------------------------------------------------------------
// HELPER: ADVANCE RELATIONSHIP DEPTH
// Based on depth increment rules from voice-realism-deep-dive.md §4.4
// ---------------------------------------------------------------------------

function advanceRelationshipDepth(
  currentDepth: number,
  skillResult: ReturnType<typeof runSkillScorers> extends Promise<infer T> ? T : never,
  isGenuine: boolean,
  llmOutput: AriaLLMOutput
): number {
  let increment = 2; // baseline per turn

  // Skill signal increments
  if (llmOutput.skill_signals.self_disclosure) increment += 3;
  if (llmOutput.is_genuine_moment && isGenuine) increment += 3;
  if (llmOutput.memory_updates.new_emotional_moment?.weight &&
      llmOutput.memory_updates.new_emotional_moment.weight > 0.5) increment += 2;

  // Inside joke formation
  if (llmOutput.memory_updates.quotable_phrase) increment += 1;

  return Math.min(100, currentDepth + increment);
}

// ---------------------------------------------------------------------------
// HELPER: COMPUTE CONVERSATION PHASE
// Thresholds from voice-realism-deep-dive.md §4.4
// ---------------------------------------------------------------------------

function computePhase(depth: number): import("./aria-types").ConversationPhase {
  if (depth < 25) return "opening";
  if (depth < 55) return "warming";
  if (depth < 80) return "climax";
  return "closing";
}

// ---------------------------------------------------------------------------
// HELPER: APPLY SKILL UPDATES
// Each skill increments on qualifying instance; 5 instances = level up.
// ---------------------------------------------------------------------------

function applySkillUpdates(
  tracker: SkillTracker,
  signals: AriaLLMOutput["skill_signals"]
): SkillTracker {
  const updated = JSON.parse(JSON.stringify(tracker)) as SkillTracker; // deep clone

  const skills = ["curiosity", "presence", "self_disclosure", "recovery", "specificity"] as const;

  for (const skill of skills) {
    if (signals[skill]) {
      updated[skill].instances += 1;
      // Level up check
      const newLevel = Math.min(
        3,
        Math.floor(updated[skill].instances / SKILL_LEVEL_THRESHOLD) + 1
      ) as 1 | 2 | 3;
      updated[skill].level = newLevel;
    }
  }

  return updated;
}

// ---------------------------------------------------------------------------
// HELPER: FALLBACK OUTPUT (when LLM fails)
// Returns a safe, in-character response that won't break the session.
// ---------------------------------------------------------------------------

function buildFallbackOutput(state: ConversationState): AriaLLMOutput {
  return {
    speech: "[soft] [pause] Sorry — I lost my train of thought for a second. What were you saying?",
    mood: "neutral",
    energy: 0.5,
    is_genuine_moment: false,
    skill_signals: {
      curiosity: 0,
      presence: 0,
      self_disclosure: 0,
      recovery: 0,
      specificity: 0,
    },
    memory_updates: {
      new_entities: [],
      new_stories: [],
      new_emotional_moment: null,
      quotable_phrase: null,
      thread_resolved: null,
      thread_dodged: null,
    },
    crisis_signal: false,
  };
}

// ---------------------------------------------------------------------------
// HELPER: CRISIS OUTPUT
// Aria exits character, speaks plainly, provides crisis resources.
// This is the highest-priority override in the entire system.
// ---------------------------------------------------------------------------

function buildCrisisOutput(state: ConversationState): OrchestratorOutput {
  const crisisSpeech = `[soft] [slows down] [pause] Hey — I want to step outside our conversation for a moment. [breathes] What you're describing sounds serious, and I want to make sure you have support. [pause] Please reach out to someone who can actually help: iCall India at 9152987821, AASRA at 9820466626, or findahelpline.com if you're elsewhere. [pause] [warm] I mean this. You don't have to be okay right now. But please don't be alone with it.`;

  return {
    speech_text: crisisSpeech,
    mood: "warm",
    updated_state: state, // Don't update state during crisis
    skill_updates: {
      curiosity: 0,
      presence: 0,
      self_disclosure: 0,
      recovery: 0,
      specificity: 0,
    },
    genuine_moment_earned: false,
    genuine_moment_total: state.genuine_moment_count,
    milestone_triggered: null,
    crisis_signal: true,
  };
}

// ---------------------------------------------------------------------------
// INITIAL STATE FACTORY
// Called when a new session starts. Optionally hydrated with Mem0 context.
// ---------------------------------------------------------------------------

export function createInitialConversationState(
  userId: string,
  sessionNumber: number,
  mem0Context?: import("./aria-types").Mem0Context
): ConversationState {
  const sessionId = `session_${userId}_${Date.now()}`;

  const emptyWorkingMemory: WorkingMemory = {
    session_id: sessionId,
    turn_count: 0,
    entities: { people: {}, places: {}, preferences: {} },
    stories: [],
    unresolved_threads: [],
    emotional_moments: [],
    inside_jokes: [],
    genuine_moments: [],
    last_turn_emotional_weight: 0,
    last_turn_has_questionable_claim: false,
    ai_interrupted_mid_thought: false,
    proactive_queue: [],
    language_register: "english",
  };

  const defaultSkillTracker: SkillTracker = {
    curiosity: { level: 1, instances: 0 },
    presence: { level: 1, instances: 0 },
    self_disclosure: { level: 1, instances: 0 },
    recovery: { level: 1, instances: 0 },
    specificity: { level: 1, instances: 0 },
  };

  return {
    session_id: sessionId,
    user_id: userId,
    session_number: sessionNumber,
    current_mood: "neutral",
    current_energy: 0.6,
    current_phase: "opening",
    relationship_depth: 0,
    genuine_moment_count: mem0Context?.total_genuine_moments ?? 0,
    session_genuine_moment_count: 0,
    skill_tracker: mem0Context?.skill_tracker_snapshot ?? defaultSkillTracker,
    milestone_10_triggered: (mem0Context?.total_genuine_moments ?? 0) >= 10,
    milestone_25_triggered: (mem0Context?.total_genuine_moments ?? 0) >= 25,
    milestone_50_triggered: (mem0Context?.total_genuine_moments ?? 0) >= 50,
    working_memory: emptyWorkingMemory,
    session_started_at: new Date().toISOString(),
    last_turn_at: new Date().toISOString(),
  };
}

// ---------------------------------------------------------------------------
// NEXT.JS API ROUTE HANDLER
// Usage: POST /api/aria/turn
// Body: { user_transcript: string, conversation_state: ConversationState, previous_turns: ConversationTurn[] }
// ---------------------------------------------------------------------------

export async function POST(request: Request): Promise<Response> {
  try {
    const body = await request.json();

    const orchestratorInput: OrchestratorInput = {
      user_transcript: body.user_transcript,
      conversation_state: body.conversation_state,
      previous_turns: body.previous_turns ?? [],
      is_first_turn: body.is_first_turn ?? false,
    };

    // Input validation
    if (!orchestratorInput.user_transcript?.trim()) {
      return Response.json({ error: "user_transcript is required" }, { status: 400 });
    }

    const output = await processAriaTurn(orchestratorInput);

    return Response.json(output);
  } catch (err) {
    console.error("[aria/turn] Error:", err);
    return Response.json(
      { error: "Internal server error", detail: String(err) },
      { status: 500 }
    );
  }
}
