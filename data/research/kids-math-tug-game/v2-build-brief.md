# V2 Build Brief — Kids Math Tug Online Mode

*Phase 2 Synthesis — Research → Builder Dispatch Brief*
*For: frontend-engineer-agent + backend-engineer-agent*
*Date: 2026-05-18*

---

## Open Questions — Answered from V1 Codebase

Before the brief, all 8 research open questions are now resolved by reading the actual V1 code:

**Q1 — CF account:** V1 already deploys to Cloudflare Pages (confirmed by project structure). Same account works for partyserver. Workers free tier unlocked April 2025.

**Q2 — Room code length:** 4 chars. V1 is a kids hobby project. Collision math is safe at realistic concurrent usage. One fewer character = easier to type on a phone keyboard. Go with 4.

**Q3 — Vite Plugin vs separate wrangler:** Vite config is minimal (`@vitejs/plugin-react` + `@tailwindcss/vite`). Adding `@cloudflare/vite-plugin` is one line. Use it — single build command, no separate `wrangler deploy` step.

**Q4 — Question generation:** V1 already has a beautiful `generator.ts` with seeded dedup, `generateDistractors`, all 4 ops × 3 difficulties. The server can call the same logic (or a simplified variant). No separate question DB needed.

**Q5 — Reconnect grace period:** 30 seconds. Fast enough that waiting kid doesn't leave, long enough for app re-open.

**Q6 — Does TugCanvas read ropePosition from Zustand?** YES, confirmed. In `MatchScreen.tsx` line 82: `scene.setRopePosition(ropePosition, !reduced)` — driven by `ropePosition` from Zustand. V2 online mode just writes server-received `ropePosition` into the same Zustand field. Canvas works unchanged.

**Q7 — Portrait vs landscape for online mode:** V1 hot-seat shows "Rotate to play!" overlay in portrait mode (line 179 of MatchScreen.tsx). Online mode must NOT do this — each kid is on their own phone, portrait is the expected orientation. New `MatchScreenOnline.tsx` is portrait-first, no rotation gate.

**Q8 — Player names:** Animal-only (Tiger/Elephant). `HomeScreen.tsx` already uses emoji-first identity. Keep it consistent. No name input field.

---

## What V1 Already Has (Do Not Re-Build)

| Component | File | Reuse in V2 |
|-----------|------|-------------|
| Question generator (all 4 ops, 3 difficulties, dedup, distractors) | `src/math/generator.ts`, `src/math/distractors.ts` | Port server-side directly |
| Rope position → Phaser canvas bridge | `MatchScreen.tsx` → `TugScene` via `setRopePosition()` | Unchanged — Zustand drives it |
| Answer buttons (2×2 MCQ grid) | `src/ui/AnswerButton.tsx` | Reuse as-is |
| Score bar | `src/ui/ScoreBar.tsx` | Reuse |
| Sound system (Web Audio API, no files) | `src/hooks/useSound.ts` | Reuse |
| Countdown overlay | `src/ui/Countdown.tsx` | Reuse |
| Framer Motion screen transitions | `App.tsx` | Extend — add new phases |
| Results screen | `src/screens/ResultsScreen.tsx` | Reuse — pass online results via same Zustand `winner` field |
| Phaser TugScene | `src/game/TugScene.ts` | Unchanged |

**GameMode type** in `types.ts` is currently `'2p' | 'ai'`. V2 adds `'online'` — one line change.

**GamePhase** is currently `'home' | 'setup' | 'countdown' | 'playing' | 'ended'`. Online mode needs additional phases — handled cleanly by a separate `onlinePhase` slice in Zustand, not by polluting `GamePhase`.

---

## V2 Architecture Spec

### New Files to Create

```
kids-math-tug/
│
├── party/
│   └── gameRoom.ts          ← partyserver Durable Object (ALL server logic)
│
├── src/
│   ├── screens/
│   │   ├── CreateRoomScreen.tsx
│   │   ├── JoinRoomScreen.tsx
│   │   ├── LobbyScreen.tsx
│   │   └── MatchScreenOnline.tsx
│   │
│   ├── hooks/
│   │   └── usePartyRoom.ts  ← PartySocket wrapper + Zustand dispatch
│   │
│   └── store/
│       └── onlineSlice.ts   ← New Zustand slice (don't mutate gameStore.ts)
│
├── wrangler.toml            ← DO binding config
└── vite.config.ts           ← add @cloudflare/vite-plugin
```

Files to **modify** (minimal surgery):

```
src/lib/types.ts    ← add 'online' to GameMode
src/App.tsx         ← add online phase routing
src/screens/HomeScreen.tsx  ← add 3rd button "Play Online"
package.json        ← add partyserver, partysocket, nanoid, bad-words
```

---

## Server: `party/gameRoom.ts` Full Spec

The Durable Object is the source of truth for the entire online match.

**State it holds:**
```typescript
interface RoomState {
  phase: 'WAITING' | 'LOBBY' | 'COUNTDOWN' | 'ACTIVE' | 'ROUND_RESULT' | 'GAME_OVER';
  hostConnId: string | null;
  guestConnId: string | null;
  hostSessionToken: string;
  guestSessionToken: string;
  config: { operation: Op; difficulty: Difficulty; };
  ropePosition: number;          // 0–10, starts 5
  scores: { host: number; guest: number; };
  currentQuestion: Question | null;
  questionIndex: number;
  roundWinner: 'host' | 'guest' | 'tie' | null;
  lastAnswerTs: { host: number; guest: number; };
  disconnectedAt: { host: number | null; guest: number | null; };
  rematchVotes: { host: boolean; guest: boolean; };
}
```

**Key server responsibilities:**
1. Generate room code (caller does this via HTTP POST before WS connect)
2. On `JOIN_ROOM`: assign host (first join) or guest (second join), send session token
3. On both players connected → phase `LOBBY`
4. On `START_GAME` from host → run 3-2-1 countdown server-side, broadcast `COUNTDOWN_TICK`, then `QUESTION_BROADCAST`
5. On `ANSWER_SUBMIT`: validate correctness, record `serverTs`, declare winner (earliest correct), compute new `ropePosition`, broadcast `ROUND_RESULT`, wait 2s, broadcast next `QUESTION_BROADCAST`
6. On `DISCONNECT` (onClose): start 30s grace timer via DO alarm; broadcast `PLAYER_DISCONNECT` with grace period
7. On `REJOIN` with valid token within 30s: reconnect player, broadcast `SYNC_STATE`
8. On `REMATCH_VOTE` from both: reset state, re-enter LOBBY
9. On `HEARTBEAT`: respond with `PONG` (keeps mobile WS alive)

**Message types** (reference the full TypeScript schema from the research doc):
- Client→Server: `JOIN_ROOM`, `ANSWER_SUBMIT`, `HEARTBEAT`, `REJOIN`, `START_GAME`, `UPDATE_CONFIG`, `REMATCH_VOTE`, `LEAVE_ROOM`
- Server→Client: `SYNC_STATE`, `PLAYER_JOIN`, `PLAYER_DISCONNECT`, `COUNTDOWN_TICK`, `QUESTION_BROADCAST`, `ROUND_RESULT`, `GAME_OVER`, `PONG`, `ERROR`

**Room code generation** (server-side HTTP handler):
```typescript
import { customAlphabet } from 'nanoid';
import BadWordsFilter from 'bad-words';
const gen = customAlphabet('ACDEFGHJKMNPQRTUVWXY', 4);
const filter = new BadWordsFilter();
function generateRoomCode() {
  while (true) {
    const code = gen();
    if (!filter.isProfane(code.toLowerCase())) return code;
  }
}
```

**Answer arbitration:**
```typescript
// First CORRECT answer by serverReceiveTs wins
if (msg.type === 'ANSWER_SUBMIT') {
  const isCorrect = msg.choiceIndex === state.currentQuestion!.correctIndex;
  if (isCorrect && !state.roundWinner) {
    state.roundWinner = role;         // role = 'host' | 'guest'
    // update ropePosition, broadcast ROUND_RESULT
  }
}
```

**Rope physics** (matches V1 exactly):
- Correct answer: rope moves 1 unit toward opponent's side
- Wrong answer: rope moves 0.5 units against you
- Win threshold: rope reaches 0 or 10
- Start: 5 (centre)

**DO configuration:**
```toml
# wrangler.toml
name = "kids-math-tug-server"
main = "party/gameRoom.ts"
compatibility_date = "2025-01-01"

[[durable_objects.bindings]]
name = "GAME_ROOM"
class_name = "GameRoom"

[[migrations]]
tag = "v1"
new_sqlite_classes = ["GameRoom"]
```

**Enable hibernation:** `readonly options = { hibernate: true };` — mandatory to avoid duration charges.

---

## Client: `src/hooks/usePartyRoom.ts` Spec

Single hook that owns all online-mode networking. Components call this hook; they don't touch PartySocket directly.

```typescript
interface UsePartyRoomReturn {
  // Connection
  connect: (roomCode: string, role: 'host' | 'guest') => void;
  disconnect: () => void;
  // Actions
  sendAnswer: (choiceIndex: number, questionIndex: number) => void;
  sendStartGame: () => void;
  sendRematchVote: () => void;
  sendUpdateConfig: (config: Partial<MatchConfig>) => void;
  // State (mirrors what server sent, synced into Zustand)
  connectionStatus: 'idle' | 'connecting' | 'connected' | 'reconnecting' | 'disconnected';
  latencyMs: number | null;
}
```

Responsibilities:
- Wraps `usePartySocket` from `partysocket/react`
- On every server message → dispatch to `onlineSlice` Zustand actions
- 15s heartbeat interval
- `visibilitychange` → force reconnect if WS not OPEN (Safari iOS fix)
- Session token save/restore via `sessionStorage`
- On `SYNC_STATE` received → write `ropePosition` + `scores` into existing `gameStore` (bridge between online and local state)

---

## Client: `src/store/onlineSlice.ts` Spec

**Do not modify `gameStore.ts` heavily.** Instead, create a separate Zustand store for online state. The two stores communicate only at the `ropePosition` + `scores` level (online slice writes to gameStore when server sends updates).

```typescript
type OnlinePhase =
  | 'idle' | 'creating' | 'waiting_for_guest'
  | 'joining' | 'lobby' | 'countdown'
  | 'active' | 'round_result' | 'reconnecting' | 'game_over';

interface OnlineStore {
  phase: OnlinePhase;
  roomCode: string | null;
  myRole: 'host' | 'guest' | null;
  opponentConnected: boolean;
  currentQuestion: Question | null;
  questionIndex: number;
  roundWinner: 'host' | 'guest' | 'tie' | null;
  myScore: number;
  opponentScore: number;
  ropePosition: number;
  countdownValue: number | null;
  disconnectGraceMs: number | null;
  gameOverWinner: 'host' | 'guest' | 'draw' | null;
  // actions
  setPhase: (p: OnlinePhase) => void;
  applyServerMessage: (msg: ServerMessage) => void;
  reset: () => void;
}
```

---

## Client: New Screens Spec

### `CreateRoomScreen.tsx`
- On mount: POST `/api/room` → server creates DO, returns `{ roomCode }` → store in `onlineSlice`
- Connect PartySocket as host
- Display: large 4-char code, "Copy Link" button (copies `mathtug.pages.dev/join/TIGR`), WhatsApp share button (`whatsapp://send?text=...`)
- State: "Waiting for friend... 🐘" with gentle animation
- On `PLAYER_JOIN` received → transition to LobbyScreen
- Back button → disconnect + goToHome

### `JoinRoomScreen.tsx`
- 4 large letter-input boxes (auto-focus next box on input, backspace goes back)
- Converts input to uppercase automatically
- On "Join" tap → connect PartySocket as guest with entered code
- On connection error (room not found) → shake animation + "Room not found or expired"
- On `SYNC_STATE` with phase LOBBY → transition to LobbyScreen

### `LobbyScreen.tsx`
- Shows both animals: 🐯 Tiger (host) + 🐘 Elephant (guest) with "connected" indicators
- Host sees: difficulty selector (Easy/Medium/Hard), operation selector (+/−/×/÷), "Start Game!" button
- Guest sees: current settings read-only, "Ready!" status
- On `START_GAME` from host → server broadcasts COUNTDOWN_TICK sequence
- On opponent disconnect here → "Friend disconnected. Waiting 30s..." or back to home on timeout

### `MatchScreenOnline.tsx`
- **Portrait-first layout** (no rotation gate unlike hot-seat mode)
- Layout (top to bottom):
  - Header: `🐯 Tiger [score] ←rope→ [score] Elephant 🐘` — rope position shown as visual bar
  - Phaser TugCanvas (same component, full width, reads `ropePosition` from Zustand)
  - Question strip: `3 + 7 = ?` (large Fredoka font, same as V1)
  - QuestionTimer arc (same component)
  - MCQ 2×2 grid (your answers only — `AnswerButton` reused, single player's grid)
  - Opponent indicator strip: `🐘 Elephant... thinking` / `🐘 Elephant answered!`
- On tap: immediate optimistic highlight (AnswerButton `feedback='idle'→'selected'`) → wait for `ROUND_RESULT` → show correct answer highlight
- On `PLAYER_DISCONNECT` → show `ReconnectingOverlay` (countdown 30s) over everything
- On `GAME_OVER` → trigger confetti + transition to ResultsScreen (same component, reuse)

### `ReconnectingOverlay.tsx` (new, small)
- Full-screen semi-transparent overlay on top of MatchScreenOnline
- Animated waiting spinner
- "Waiting for Tiger... (28s)" countdown
- "End Match" button (if kid doesn't want to wait)

---

## `App.tsx` Routing Extension

```typescript
// Extend existing phase-based routing:
import { useOnlineStore } from './store/onlineSlice';

export default function App() {
  const phase = useGameStore((s) => s.phase);
  const mode  = useGameStore((s) => s.mode);
  const onlinePhase = useOnlineStore((s) => s.phase);

  const isHome    = phase === 'home';
  const isSetup   = phase === 'setup' && mode !== 'online';
  const isMatch   = (phase === 'playing' || phase === 'countdown') && mode !== 'online';
  const isEnded   = phase === 'ended' && mode !== 'online';

  // Online flows
  const isCreateRoom = mode === 'online' && onlinePhase === 'creating';
  const isWaiting    = mode === 'online' && onlinePhase === 'waiting_for_guest';
  const isJoinRoom   = mode === 'online' && onlinePhase === 'joining';
  const isLobby      = mode === 'online' && onlinePhase === 'lobby';
  const isOnlineMatch = mode === 'online' &&
    ['countdown','active','round_result','reconnecting'].includes(onlinePhase);
  const isOnlineOver  = mode === 'online' && onlinePhase === 'game_over';

  // AnimatePresence keys pick up the right screen — existing transition system just works
}
```

---

## `HomeScreen.tsx` — One Button Addition

Add a third button between the existing two:

```tsx
{/* NEW: Online mode */}
<motion.button
  onClick={() => { handleMode('online'); }}   // sets mode='online', onlinePhase='creating'
  style={{
    background: 'linear-gradient(135deg, #6BCB77 0%, #3d9e47 100%)',
    // same sizing/border-radius as existing buttons
  }}
>
  📱 Play Online
</motion.button>
```

HomeScreen already has room for 3 buttons in its flex column.

---

## `package.json` — New Dependencies

```json
{
  "dependencies": {
    "partyserver": "^0.0.58",
    "partysocket": "^1.1.2",
    "nanoid": "^5.1.7",
    "bad-words": "^4.0.0"
  },
  "devDependencies": {
    "@cloudflare/vite-plugin": "^1.0.0",
    "wrangler": "^4.0.0"
  }
}
```

---

## `vite.config.ts` — CF Vite Plugin Addition

```typescript
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';
import { cloudflare } from '@cloudflare/vite-plugin';  // ADD

export default defineConfig({
  plugins: [
    cloudflare(),   // ADD — handles Worker build alongside SPA
    react(),
    tailwindcss(),
  ],
  // ... rest unchanged
});
```

---

## Mobile Safari Anti-Death Checklist

These must be in `usePartyRoom.ts` or bad things happen on iPhone:

1. **15s heartbeat** — `setInterval(() => socket.send(HEARTBEAT), 15_000)`
2. **visibilitychange reconnect** — `document.addEventListener('visibilitychange', () => { if (visible && socket not OPEN) socket.reconnect() })`
3. **sessionStorage token** — save `{ roomCode, role, token }` on join, restore on reconnect
4. **PartySocket auto-reconnect** — `ReconnectingWebSocket` built-in, exponential backoff, no manual config needed

---

## Rope Mechanics — Match V1 Exactly

V1 uses `ropePosition` 0–10 starting at 5. Server must use the same scale:
- Correct: `ropePosition += 1` (for host) or `ropePosition -= 1` (for guest)
- Wrong: `ropePosition -= 0.5` (for host) or `ropePosition += 0.5` (for guest)
- Win: ropePosition >= 10 → host wins; ropePosition <= 0 → guest wins
- Clamp: `Math.max(0, Math.min(10, ropePosition))`

`scene.setRopePosition(ropePosition, animated)` — the Phaser scene already handles this. In MatchScreenOnline, this is called identically to MatchScreen via the same Zustand subscription.

---

## India Latency — Known Limitation (Document, Don't Fix)

For V2 scope: acceptable. Both players on Jio/Airtel face the same routing → relative fairness maintained. Note in README. If V3 becomes commercial → explore Cloudflare Argo or paid plan.

---

## What NOT to Build in V2

- No Firebase, no Socket.IO standalone server, no Pusher
- No HTTP polling for room status
- No WebRTC
- No CRDT (Yjs) for game state
- No Postgres/Redis for room state
- No custom profanity word list — use `bad-words` npm
- No host migration — DO is the host, not a peer
- No player name input — Tiger/Elephant only
- No adaptive difficulty — fixed difficulty chosen in lobby

---

## Summary — What V2 Builder Gets

**Backend agent task:** Build `party/gameRoom.ts` (partyserver DO class) + `wrangler.toml`. Server manages: room creation, player join/role assignment, session tokens, question generation (port from `generator.ts`), answer validation + timing arbitration, rope physics, reconnect grace period (30s alarm), rematch flow, heartbeat PONG.

**Frontend agent task:** Build 4 new screens + `usePartyRoom.ts` hook + `onlineSlice.ts` store slice. Modify `App.tsx` routing, `HomeScreen.tsx` (add 3rd button), `types.ts` (add 'online' to GameMode), `vite.config.ts` (add CF plugin). Portrait-first layout for MatchScreenOnline. Reuse: AnswerButton, ScoreBar, TugCanvas, Countdown, QuestionTimer, ResultsScreen, SoundManager — all unchanged.
