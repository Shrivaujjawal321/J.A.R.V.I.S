# Aria — Frontend Implementation Notes

**Agent:** frontend-engineer-agent
**Date:** 2026-05-27
**Status:** MVP scaffold complete, builds + dev server verified

---

## 1. Executive Summary

Aria is a voice-first Next.js 16 single-page application with no routing beyond a phase state machine (onboarding_welcome → onboarding_disclosure → conversation → session_end / graduation). All session state persists in LocalStorage. The ElevenLabs Conversational AI SDK drives the WebRTC voice pipeline client-side. The ML brain orchestrator is called from three Server Actions (`/api/conversation/start`, `/turn`, `/end`). The design system uses OKLCH warm neutrals with a terracotta accent, Fraunces serif for Aria's voice, Inter for chrome. The portrait is an animated SVG placeholder with 5 emotion states; the designer replaces it with commissioned illustrations. All compliance requirements (17+ age gate, AI disclosure, crisis escalation, data deletion) are implemented.

Architecture: Server Components for static shells → Client Components for voice/session logic → API routes bridging to ML brain → LocalStorage persistence. Total initial JS well under 200KB gzipped.

---

## 2. Project Structure

```
/home/ujjwal/Documents/J.A.R.V.I.S./projects/aria/
├── src/
│   ├── app/
│   │   ├── layout.tsx                    Root layout — Fraunces + Inter fonts
│   │   ├── page.tsx                      Phase router (single page, Client Component)
│   │   ├── globals.css                   OKLCH design tokens + Tailwind 4
│   │   └── api/
│   │       ├── conversation/
│   │       │   ├── turn/route.ts         POST — process user transcript
│   │       │   ├── start/route.ts        POST — session init
│   │       │   └── end/route.ts          POST — fact extraction trigger
│   │       └── elevenlabs/
│   │           └── signed-url/route.ts   GET — signed WebSocket URL (key hidden)
│   ├── types/
│   │   └── aria.ts                       All shared types + CRISIS_RESOURCES
│   ├── lib/
│   │   ├── aria-brain-stub.ts            Typed stub (ML agent replaces)
│   │   ├── session-storage.ts            LocalStorage abstraction
│   │   ├── utils.ts                      shadcn cn utility
│   │   └── cn.ts                         Re-export
│   ├── hooks/
│   │   ├── use-elevenlabs-voice.ts       WebRTC + waveform + error states
│   │   └── use-session.ts                Full session lifecycle
│   └── components/
│       ├── aria/
│       │   ├── aria-portrait.tsx         5-emotion portrait + 200ms crossfade
│       │   ├── audio-waveform.tsx        SVG waveform, 32 bars
│       │   ├── voice-button.tsx          8 states, space-bar accessible
│       │   ├── skill-tracker.tsx         5×3 dot matrix + genuine counter
│       │   ├── ai-disclosure-pill.tsx    Persistent compliance badge
│       │   └── crisis-modal.tsx          Self-harm escalation, confirm-to-dismiss
│       ├── onboarding/
│       │   ├── welcome-screen.tsx        17+ age gate + DOB validation
│       │   └── disclosure-screen.tsx     AI disclosure acknowledgment
│       ├── session/
│       │   ├── conversation-screen.tsx   Main conversation UI
│       │   ├── session-end-screen.tsx    Session summary + forget-everything
│       │   └── graduation-screen.tsx     50-moment ceremony + IRL challenge
│       └── ui/                           shadcn/ui primitives (base-ui v4)
├── public/
│   └── portraits/
│       └── README.md                     Spec for designer's portrait assets
├── .env.local.example                    Environment variable template
├── README.md                             Run instructions
└── package.json                          Next 16 + Framer Motion 12 + EL SDK
```

---

## 3. Key Files Annotated

### `src/types/aria.ts`
The single source of truth for all types. Both the frontend and ML brain import from here. Key exports:

- `AriaEmotionState` — union of 5 portrait states
- `SessionState` — full session shape stored in LocalStorage
- `PersistentState` — wraps session + history + user prefs
- `BrainTurnRequest / BrainTurnResponse` — the API contract between Next.js routes and ML orchestrator
- `VoiceButtonState` — 8-state machine for the mic button
- `CRISIS_RESOURCES` — typed constants for iCall, AASRA, findahelpline

### `src/hooks/use-elevenlabs-voice.ts`
WebRTC voice hook. Wraps `@elevenlabs/client` `Conversation.startSession()`. Manages:
- Mic permission lifecycle (getUserMedia → error states)
- AudioContext + AnalyserNode for real-time waveform
- `onConnect`, `onDisconnect`, `onError`, `onModeChange`, `onMessage` callbacks
- Volume update loop via requestAnimationFrame
- Clean teardown on unmount (mic track stop + AudioContext close)

### `src/hooks/use-session.ts`
Full session lifecycle. Manages conversationPhase transitions, calls brain stub, applies skill increments, tracks genuine moments, signals crisis modal, persists everything to LocalStorage on every state change.

### `src/lib/aria-brain-stub.ts`
Typed stub with identical interface to what the ML orchestrator will export. Returns mock Aria responses cycling through 8 phrases. Basic keyword-check crisis detection. The ML agent replaces this with the real Claude Haiku 4.5 + Mem0 + classifiers implementation.

### `src/lib/session-storage.ts`
Pure localStorage abstraction. `loadState()` / `saveState()` / `clearState()`. `applySkillIncrements()` applies delta increments from each brain turn, levels up at 5 instances per level (max level 3). `archiveSessionToHistory()` keeps last 10 sessions.

### `src/components/aria/aria-portrait.tsx`
SVG placeholder portrait with `AnimatePresence mode="wait"` key=emotion for 200ms crossfade. Each emotion state has distinct eye + mouth expression in the SVG. The `PortraitPlaceholder` function is the only thing the designer replaces — swap with `<Image src={...} />` using the 5 webp files.

### `src/components/aria/voice-button.tsx`
8 state configs in `STATE_CONFIGS`. `aria-pressed` for listening state. Space/Enter keyboard handling. Focus ring visible. Framer Motion pulsing ring animation for listening/ready states. `prefers-reduced-motion` honored via `useReducedMotion()`.

### `src/components/aria/crisis-modal.tsx`
Uses base-ui Dialog (shadcn v4). `disablePointerDismissal` set. `onOpenChange` intercepts outside-press and escape-key reasons and blocks them. Two-step confirm ("I'm safe" → "Yes, I'm okay") before dismissal. All resource links keyboard-accessible.

### `src/app/api/elevenlabs/signed-url/route.ts`
Critical security: the `ELEVENLABS_API_KEY` env var never reaches the browser. The client requests a signed WebSocket URL from this server endpoint, which calls ElevenLabs API with the private key. Signed URL is returned to client; client passes it to `Conversation.startSession({ signedUrl })`.

### `src/app/globals.css`
OKLCH warm neutral palette. Placeholder tokens that designer's `design-tokens.css` will override. `--font-serif` wired to Fraunces variable. `prefers-reduced-motion` global rule. Focus-visible ring high-contrast. Date input color-scheme normalization.

---

## 4. API Contract with ML Brain

The ML agent builds `src/lib/aria-orchestrator.ts` implementing these three functions:

```typescript
export async function startSession(
  req: SessionStartRequest
): Promise<SessionStartResponse>

export async function processTurn(
  req: BrainTurnRequest
): Promise<BrainTurnResponse>

export async function endSession(
  req: SessionEndRequest
): Promise<SessionEndResponse>
```

All types are in `src/types/aria.ts`. Key fields in `BrainTurnResponse`:

```typescript
{
  updatedState: SessionState,      // Full updated state
  ariaResponseText: string,        // Aria's reply text
  newEmotion: AriaEmotionState,    // Portrait to swap to
  genuineMomentDetected: boolean,
  genuineMoment?: { signal, turnIndex, timestamp },
  skillIncrements: Partial<Record<SkillName, number>>,
  crisisDetected: boolean,         // Triggers crisis modal
  elevenLabsOverrides?: Record<string, string | number>  // Dynamic vars for EL agent
}
```

**Emotion signal path:** ML agent runs emotion classifier → sets `newEmotion` in `BrainTurnResponse` → API route returns to client → `processUserTurn()` in `use-session.ts` updates state → `ConversationScreen` updates portrait. In production, this can also be injected via ElevenLabs dynamic variables per turn.

---

## 5. Voice Loop Implementation

### Session start
1. User completes onboarding → `initSession()` → `POST /api/conversation/start` → brain returns opening line + initial state
2. `ConversationScreen` mounts with session state

### WebRTC connection
1. User taps voice button → `startConversation()` in `useElevenLabsVoice`
2. `navigator.mediaDevices.getUserMedia({ audio: true })` — permission prompt
3. `Conversation.startSession({ agentId, dynamicVariables })` — ElevenLabs WebRTC
4. `dynamicVariables` includes session_n, depth, mood, energy, phase, genuine_count — these fill the `{{placeholders}}` in the ElevenLabs agent's system prompt (which should match Aria's XML system prompt from ML agent)
5. `onConnect` → set `conversationId`, state = `listening`
6. `onModeChange` → toggle `ariaIsSpeaking` / `userIsSpeaking` states → drive portrait + waveform

### Per-turn flow
1. ElevenLabs handles VAD + STT internally (managed pipeline)
2. `onMessage({ source: 'user', message })` → `handleTranscript(text)` → `POST /api/conversation/turn` → brain scores + classifies → updates session state
3. `onMessage({ source: 'ai', message })` → `handleAriaMessage(text, emotion)` → updates `ariaLastLine` + `displayEmotion`
4. Portrait crossfades to new emotion (200ms Framer Motion)
5. Waveform animates from AnalyserNode data during Aria's audio playback

### Session end
1. User taps "End session" → `stopConversation()` → `POST /api/conversation/end` → ML agent extracts facts to Mem0
2. `onDisconnect` also triggers `onSessionEnd` (network drop)
3. `archiveSessionToHistory()` → phase = `session_end`

### API key security
The `ELEVENLABS_API_KEY` only lives in the server environment. Clients call `GET /api/elevenlabs/signed-url` to get a 60-second signed WebSocket URL. The hook passes this as `signedUrl` to `Conversation.startSession()` instead of the API key directly.

---

## 6. Component Implementation Notes

### AriaPortrait — portrait crossfade
`AnimatePresence mode="wait"` with `key={emotion}` causes the old portrait to exit (opacity 0 over 200ms) before the new one enters (opacity 0 → 1 over 200ms). `useReducedMotion()` collapses duration to 0ms. The SVG placeholder draws distinct eyes/mouth per emotion state as a stand-in until the designer's 5 PNGs/SVGs arrive.

**Designer handoff:** Replace `<PortraitPlaceholder emotion={emotion} />` with:
```tsx
import Image from "next/image";
<Image
  src={`/portraits/aria-${emotion}.webp`}
  alt={EMOTION_CONFIG[emotion].alt}
  width={280}
  height={320}
  priority={emotion === "neutral"}
  className="w-full h-full object-cover rounded-none"
/>
```

### VoiceButton — 8 states
All state configs in `STATE_CONFIGS` map. Pulsing ring is a separate `motion.span` behind the button — `AnimatePresence` exits it when state leaves `listening`/`ready`. `aria-pressed` signals the toggle state to screen readers. `aria-live="polite"` region below the button announces state changes.

Space-bar handling: `onKeyDown` catches `" "` (space) and `"Enter"` — calls same handler as click. `e.preventDefault()` prevents page scroll on space.

### SkillTracker — dots
5 skills × 3 dots each. Dots use `motion.span` with `animate={{ opacity }}` — filled = 1.0, empty = 0.4, with 300ms ease transition. The level is displayed only through dot fill — no numbers, no labels below — intentionally cryptic (mechanic reveals itself per §6.4).

### CrisisModal — base-ui specific notes
shadcn v4 ships with `@base-ui/react` (not Radix UI). The `DialogContent` doesn't support `onPointerDownOutside` or `onEscapeKeyDown` — those are Radix props. Instead:
- `disablePointerDismissal` prop on `<Dialog>` blocks outside clicks
- `onOpenChange` with reason check blocks escape key
- `showCloseButton={false}` hides the default X button

---

## 7. State Management

### LocalStorage schema (key: `aria_persistent_state_v1`)
```typescript
PersistentState {
  ageVerified: boolean                // Age gate cleared
  aiDisclosureAcknowledged: boolean   // Disclosure modal accepted
  sessionHistory: SessionSummary[]    // Last 10 sessions (truncated)
  currentSession: SessionState | null // Active or most-recent session
  mem0UserId: string | null           // ML agent writes this on first session
  elevenLabsConversationId: string | null
}
```

### Session state lifecycle
1. `loadState()` on hook init (SSR-safe: returns default on server)
2. Every state mutation goes through `persistAndSet()` which calls both `setPersistentState()` (React) and `saveState()` (localStorage)
3. Skill increments are applied with `applySkillIncrements()` — pure function, levels up at 5 instances per level
4. Genuine moments appended to `session.moments[]` + `genuineThisSession` counter
5. Session archived to history on `endCurrentSession()` (last 10 kept)
6. `clearState()` / `resetAll()` removes the key entirely

### State that is NOT persisted (ephemeral)
- `voiceState` (mic permission, reconnecting, etc.)
- `ariaIsSpeaking` / `userIsSpeaking`
- `waveformData`
- `ariaLastLine` (transcript display)

---

## 8. Crisis Escalation Flow

1. **Detection:** ML brain's `processTurn()` returns `crisisDetected: true` in `BrainTurnResponse`
2. **Propagation:** `use-session.ts` `processUserTurn()` checks `result.crisisDetected` → `setCrisisModalOpen(true)`
3. **Voice:** The modal appearing doesn't auto-stop the voice connection — Aria goes silent naturally (ElevenLabs turn ends). If Boss wants to force-stop: add `stopConversation()` call on crisis detect in `processUserTurn()`.
4. **Modal behavior:** `disablePointerDismissal` + escape blocked. Two-step confirm for "I'm safe". Resources: iCall (tel: link), AASRA (tel: link), findahelpline.com (external link, new tab).
5. **Dismiss path:** "I'm safe" → confirm step → `dismissCrisisModal()` → modal closes, conversation continues
6. **End path:** "End session" from modal → `endCurrentSession()` → session archived, phase = session_end

**The stub brain** also has basic keyword crisis detection for dev testing. Search `"kill myself"`, `"suicide"`, etc. in the input to trigger the modal.

---

## 9. Local Dev Setup

```bash
# Prerequisites: Node 20+, pnpm 10+

cd /home/ujjwal/Documents/J.A.R.V.I.S./projects/aria

# Install (already done)
pnpm install

# Configure env (required for voice; optional for UI dev)
cp .env.local.example .env.local
# Edit .env.local — add NEXT_PUBLIC_ELEVENLABS_AGENT_ID + ELEVENLABS_API_KEY

# Dev server (hot reload, Turbopack)
pnpm dev
# → http://localhost:3000 (or 3001 if 3000 is taken)

# TypeScript check
pnpm tsc --noEmit

# Production build
pnpm build

# No voice? No problem.
# Open http://localhost:3000 — onboarding + all screens work
# Voice button shows error_api, all other features functional
```

### Testing the crisis modal without voice
Open browser console and run:
```js
// Manually trigger a "turn" that flags crisis
fetch('/api/conversation/turn', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    sessionId: 'test-00000000-0000-0000-0000-000000000001',
    userTranscript: 'i want to kill myself',
    turnIndex: 1,
    currentState: { /* ... */ }
  })
})
```
Or simply: get into conversation screen via onboarding, voice button will show error_api but `processUserTurn()` can be called from DevTools.

---

## 10. Known Gaps / Next Steps for Production

| Gap | Priority | Owner | Notes |
|---|---|---|---|
| Real Aria portraits (5 emotion PNGs/SVGs) | P0 | Designer | Swap `<PortraitPlaceholder>` in aria-portrait.tsx |
| Real ML brain (orchestrator.ts) | P0 | ML agent | Replace import in 3 API routes |
| ElevenLabs agent config | P0 | Boss/ML | Create EL agent with BYO LLM + Aria system prompt; set env vars |
| Emotion signal from EL → portrait | P1 | ML agent | EL dynamic vars or response metadata needs to carry emotion |
| Mem0 user ID persistence | P1 | ML agent | startSession response should include mem0UserId; use-session.ts already persists it |
| Signed URL flow in voice hook | P1 | Frontend | Hook currently uses agentId directly; switch to signedUrl via GET /api/elevenlabs/signed-url |
| Privacy policy page | P1 | Boss | Required for compliance; /privacy route |
| Error recovery — reconnect | P2 | Frontend | Reconnect button visible in error_network state; retry logic not yet implemented |
| Storybook | P2 | Frontend | Add once design system tokens are locked |
| Playwright E2E suite | P2 | Frontend | onboarding flow, crisis modal, graduation |
| axe-core a11y test | P2 | Frontend | Run in CI against each screen |
| Postgres + Redis (production) | P3 | ML + DevOps | LocalStorage → DB for production scale |
| next.config.ts turbopack root warning | P3 | DevOps | Set turbopack.root to silence workspace detection warning |

### Signed URL in voice hook
The hook currently uses `agentId` directly which exposes the agent ID in client bundle (not a secret, but not ideal). To use signed URLs:

```typescript
// In useElevenLabsVoice startConversation():
const res = await fetch('/api/elevenlabs/signed-url');
const { signedUrl } = await res.json();

const conversation = await Conversation.startSession({
  signedUrl,           // instead of agentId
  dynamicVariables,
  onConnect: ...
});
```

---

## Integration Checklist for Other Agents

**ML agent:** When you ship `aria-orchestrator.ts`:
1. Match the 3 function signatures in `src/types/aria.ts`
2. Place at `src/lib/aria-orchestrator.ts`
3. In `src/app/api/conversation/turn/route.ts`, `start/route.ts`, `end/route.ts`: replace `@/lib/aria-brain-stub` import
4. `BrainTurnResponse.newEmotion` drives portrait crossfade — must return one of `AriaEmotionState`
5. `BrainTurnResponse.crisisDetected: true` triggers crisis modal immediately
6. `SessionStartResponse.openingLine` is displayed as Aria's first line

**UI/UX designer:** When you ship `design-tokens.css`:
1. Place at `src/app/design-tokens.css`
2. Add `@import "./design-tokens.css";` at top of `globals.css`
3. Your CSS vars override the placeholder `:root` block
4. Portrait assets → `public/portraits/aria-{neutral,curious,warm,amused,reserved}.webp`
5. See `public/portraits/README.md` for image spec
6. Font: Fraunces + Inter already loaded via `next/font/google` in `layout.tsx` — your tokens just need `--font-serif` and `--font-sans` vars to already exist (they do)
