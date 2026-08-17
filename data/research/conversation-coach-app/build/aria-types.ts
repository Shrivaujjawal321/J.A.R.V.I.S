/**
 * ARIA TYPES — Working Memory + State
 * Used by orchestrator, classifiers, and Next.js API routes.
 *
 * Design notes:
 * - All types are serializable to JSON (no class instances) for LocalStorage persistence.
 * - Pydantic equivalents are in aria-orchestrator.ts for the Python side (Mem0 integration).
 * - These types map 1:1 to the dynamic_state block in the system prompt.
 */

// ---------------------------------------------------------------------------
// EMOTION + MOOD
// ---------------------------------------------------------------------------

/** The 5 visual/emotional states Aria can be in. Maps 1:1 to CSS portrait swap. */
export type AriaMood = "neutral" | "curious" | "warm" | "amused" | "reserved";

/** 0 = dormant / barely present. 1 = fully energized. Drives TTS pacing. */
export type EnergyLevel = number; // 0.0 – 1.0

// ---------------------------------------------------------------------------
// CONVERSATION ARC
// ---------------------------------------------------------------------------

export type ConversationPhase = "opening" | "warming" | "climax" | "closing";

/** Relationship depth score. Drives phase advancement and warmth thresholds. */
export type RelationshipDepth = number; // 0 – 100

// ---------------------------------------------------------------------------
// SKILL TRACKER
// ---------------------------------------------------------------------------

export type SkillLevel = 1 | 2 | 3;

export interface SkillTracker {
  /** Asking specific follow-up questions on Aria's content */
  curiosity: {
    level: SkillLevel;
    instances: number; // cumulative qualifying instances
  };
  /** Concrete sensory detail in user answers */
  presence: {
    level: SkillLevel;
    instances: number;
  };
  /** Sharing something true about themselves, unprompted */
  self_disclosure: {
    level: SkillLevel;
    instances: number;
  };
  /** Staying engaged after an awkward moment or pushback */
  recovery: {
    level: SkillLevel;
    instances: number;
  };
  /** Proper nouns, numbers, specific named things in answers */
  specificity: {
    level: SkillLevel;
    instances: number;
  };
}

/** Increment per skill — 5 qualifying instances = level up */
export const SKILL_LEVEL_THRESHOLD = 5;

// ---------------------------------------------------------------------------
// WORKING MEMORY ENTITIES
// ---------------------------------------------------------------------------

export interface PersonEntity {
  name: string;
  relationship?: string; // "friend", "sister", "colleague" etc.
  context?: string; // "mentioned in context of job interview"
  attribute?: string; // "loves cricket", "is getting married"
  turn_first_mentioned: number;
  callback_pending: boolean;
}

export interface PlaceEntity {
  name: string;
  context?: string;
  turn_first_mentioned: number;
}

export interface PreferenceEntity {
  topic: string; // "filter coffee", "first thing on the menu"
  sentiment: "positive" | "negative" | "neutral";
  turn_first_mentioned: number;
  callback_pending: boolean;
}

export interface WorkingMemoryEntities {
  people: Record<string, PersonEntity>;   // keyed by name
  places: Record<string, PlaceEntity>;
  preferences: Record<string, PreferenceEntity>;
}

// ---------------------------------------------------------------------------
// STORIES + THREADS
// ---------------------------------------------------------------------------

export interface Story {
  id: string;
  summary: string;
  detail?: string;
  turn_mentioned: number;
  emotional_weight: number; // 0.0 – 1.0
  resolved: boolean;
  should_revisit: boolean;
}

export interface UnresolvedThread {
  id: string;
  topic: string;
  first_mentioned_turn: number;
  dodge_turns: number[]; // turns where user avoided this
  reintroduce_at: "natural_pause" | number; // turn number or trigger
  attempts: number; // how many times we've tried to re-open
}

// ---------------------------------------------------------------------------
// EMOTIONAL MOMENTS
// ---------------------------------------------------------------------------

export interface EmotionalMoment {
  id: string;
  turn: number;
  description: string; // "user went quiet after mention of parent"
  weight: number; // 0.0 – 1.0
  followed_up: boolean;
  follow_up_turn?: number;
}

// ---------------------------------------------------------------------------
// INSIDE JOKES
// ---------------------------------------------------------------------------

export interface InsideJoke {
  id: string;
  source_quote: string; // verbatim or close to verbatim from user
  turn: number;
  used_back: boolean;
  used_back_turn?: number;
}

// ---------------------------------------------------------------------------
// GENUINE MOMENTS
// ---------------------------------------------------------------------------

export type GenuineMomentSignal =
  | "admits_not_knowing"
  | "disagrees_with_aria"
  | "shares_personal_unprompted"
  | "asks_surprising_question"
  | "sits_in_silence"
  | "stays_after_awkward";

export interface GenuineMoment {
  id: string;
  session_id: string;
  turn: number;
  signal: GenuineMomentSignal;
  classifier_confidence: number; // 0.0 – 1.0
  user_transcript_snippet?: string;
}

// ---------------------------------------------------------------------------
// PER-TURN CLASSIFIER OUTPUTS
// ---------------------------------------------------------------------------

export interface GenuineMomentClassifierResult {
  is_genuine: boolean;
  signal: GenuineMomentSignal | null;
  confidence: number; // 0.0 – 1.0; threshold for genuine = 0.70
  disqualifying_reason?: string;
}

export interface SkillScoreResult {
  curiosity: 0 | 1;
  presence: 0 | 1;
  self_disclosure: 0 | 1;
  recovery: 0 | 1;
  specificity: 0 | 1;
}

// ---------------------------------------------------------------------------
// BEHAVIOR INSTRUCTIONS
// ---------------------------------------------------------------------------

export type BehaviorType =
  | "CALLBACK"
  | "PUSHBACK"
  | "EMOTIONAL_FOLLOWUP"
  | "INITIATE"
  | "CALLBACK_HUMOR"
  | "HOLD_SPACE"
  | "DEFAULT";

export interface BehaviorInstruction {
  type: BehaviorType;
  description: string; // e.g. "Return to 'job interview result' from turn 4"
  priority: number; // lower = higher priority; only top 2 injected per turn
}

// ---------------------------------------------------------------------------
// WORKING MEMORY (full session state)
// ---------------------------------------------------------------------------

export interface WorkingMemory {
  session_id: string;
  turn_count: number;
  entities: WorkingMemoryEntities;
  stories: Story[];
  unresolved_threads: UnresolvedThread[];
  emotional_moments: EmotionalMoment[];
  inside_jokes: InsideJoke[];
  genuine_moments: GenuineMoment[];

  /** True if the last user turn had an actively running emotional moment */
  last_turn_emotional_weight: number;
  /** True if user said something that Aria should push back on */
  last_turn_has_questionable_claim: boolean;
  /** True if AI was interrupted mid-thought and needs to return */
  ai_interrupted_mid_thought: boolean;
  /** Topics Aria wants to proactively bring up */
  proactive_queue: string[];
  /** Language register of the conversation */
  language_register: "english" | "hinglish";
}

// ---------------------------------------------------------------------------
// CONVERSATION STATE (persisted to LocalStorage)
// ---------------------------------------------------------------------------

export interface ConversationState {
  session_id: string;
  user_id: string; // LocalStorage UUID for MVP
  session_number: number; // how many total sessions

  // Aria's current state this turn
  current_mood: AriaMood;
  current_energy: EnergyLevel;
  current_phase: ConversationPhase;
  relationship_depth: RelationshipDepth;

  // Mechanic counters (cumulative across sessions)
  genuine_moment_count: number; // total all time
  session_genuine_moment_count: number; // this session only
  skill_tracker: SkillTracker;

  // Graduation flags
  milestone_10_triggered: boolean;
  milestone_25_triggered: boolean;
  milestone_50_triggered: boolean;

  // In-session working memory
  working_memory: WorkingMemory;

  // Timestamps
  session_started_at: string; // ISO 8601
  last_turn_at: string;
}

// ---------------------------------------------------------------------------
// PER-TURN INPUT/OUTPUT
// ---------------------------------------------------------------------------

/** What the orchestrator receives each turn */
export interface OrchestratorInput {
  user_transcript: string;
  conversation_state: ConversationState;
  previous_turns: ConversationTurn[]; // last 8 turns for context
  is_first_turn: boolean;
}

/** Raw LLM output — structured JSON as defined in system prompt output_format */
export interface AriaLLMOutput {
  speech: string; // Aria's spoken response with ElevenLabs audio tags inline
  mood: AriaMood;
  energy: EnergyLevel;
  is_genuine_moment: boolean;
  skill_signals: SkillScoreResult;
  memory_updates: {
    new_entities: Array<{
      type: "person" | "place" | "preference";
      data: PersonEntity | PlaceEntity | PreferenceEntity;
    }>;
    new_stories: Story[];
    new_emotional_moment: EmotionalMoment | null;
    quotable_phrase: string | null;
    thread_resolved: string | null; // thread id
    thread_dodged: string | null;   // thread id
  };
  crisis_signal: boolean;
}

/** What the orchestrator returns to the frontend */
export interface OrchestratorOutput {
  // What to send to ElevenLabs TTS
  speech_text: string;
  // What mood state to render in the UI (portrait swap)
  mood: AriaMood;
  // Updated state to persist to LocalStorage
  updated_state: ConversationState;
  // Mechanic updates for the UI skill tracker strip
  skill_updates: SkillScoreResult;
  // New genuine moment (if any) for the counter
  genuine_moment_earned: boolean;
  genuine_moment_total: number;
  // Graduation triggers
  milestone_triggered: null | 10 | 25 | 50;
  // Crisis flag — frontend shows crisis resources if true
  crisis_signal: boolean;
}

/** Single turn record for conversation history */
export interface ConversationTurn {
  turn_number: number;
  role: "user" | "aria";
  text: string; // clean text, no audio tags
  text_with_tags?: string; // Aria's side: original tagged text
  timestamp: string;
  mood?: AriaMood; // Aria's mood at this turn
  skill_signals?: SkillScoreResult; // user turn skill scoring
}

// ---------------------------------------------------------------------------
// MEM0 INTEGRATION TYPES
// ---------------------------------------------------------------------------

/** Facts extracted from a session and stored in Mem0 cloud */
export interface Mem0Fact {
  content: string;
  category:
    | "person"
    | "preference"
    | "story"
    | "opinion"
    | "goal"
    | "fear"
    | "relationship";
  confidence: number;
  session_id: string;
  extracted_at: string;
}

/** What Mem0 returns at session start — injected into system prompt */
export interface Mem0Context {
  user_id: string;
  facts: Mem0Fact[];
  last_session_summary?: string;
  total_sessions: number;
  total_genuine_moments: number;
  skill_tracker_snapshot: SkillTracker;
}

// ---------------------------------------------------------------------------
// ELEVENLABS CONV AI CONFIG TYPES
// ---------------------------------------------------------------------------

export interface ElevenLabsConvAIConfig {
  agent_id: string;
  voice_id: string;
  // BYO LLM endpoint — your Next.js API route
  llm_websocket_url: string;
  // Conversation initiation config
  first_message?: string;
  // Conversation metadata passed through to your LLM
  conversation_config_override?: {
    agent: {
      prompt: {
        prompt: string; // Aria's static system prompt text
      };
      first_message?: string;
    };
  };
}

// ---------------------------------------------------------------------------
// GRADUATION MECHANIC
// ---------------------------------------------------------------------------

export interface GraduationState {
  is_graduated: boolean;
  graduated_at?: string;
  irl_challenge_accepted: boolean;
  irl_challenge_completed: boolean;
  return_story?: string; // what user told Aria after IRL challenge
}
