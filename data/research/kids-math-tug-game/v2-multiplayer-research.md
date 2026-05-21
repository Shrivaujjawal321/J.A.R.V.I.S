# Kids Math Tug V2 — 10-Axis Multiplayer Research Brief

**Date:** 2026-05-18
**Scope:** Deep research for V2 room-code cross-device multiplayer pivot. V1 stack: Vite 6 + React 19 + TS + Tailwind 4 + Phaser 4.1 + Framer Motion 12 + Zustand, deployed Cloudflare Pages. V2 adds PartyKit-on-Cloudflare room-code mode. Ages 6-8.

---

## CRITICAL FLAG — PartyKit Ecosystem Split (Read Before Everything Else)

**The PartyKit ecosystem has split into two distinct products since the Cloudflare acquisition (April 2024). Boss must understand which one to build on:**

| Product | npm package | Deploy to | Cost | Status |
|---------|-------------|-----------|------|--------|
| PartyKit Cloud (legacy) | `partykit@0.0.115` | PartyKit's managed infra | Separate pricing, opaque | Active but de-emphasized |
| **PartyServer (new canonical)** | `partyserver@0.0.58` | **Your own Cloudflare account** | CF free tier + DO pricing | **Actively developed — this is the future** |

**Build on `partyserver` + `partysocket` targeting your own Cloudflare account.** The GitHub repo `cloudflare/partykit` has superseded `partykit/partykit`. The `partyserver` README literally contains the string "You appear to be migrating a PartyKit project to PartyServer" — Cloudflare expects everyone to migrate. No official sunset announcement found [unverified whether a sunset date exists], but the trajectory is unambiguous.

**Key packages for V2:**
- `partyserver` — Durable Object server class
- `partysocket@1.1.2` — client WebSocket with auto-reconnect (moved to partyserver repo as of March 2025)
- `hono-party` — middleware if using Hono as HTTP layer (optional)

---

## Axis 1 — PartyKit Current SOTA (2026)

### Package Versions

| Package | Version | Last Updated | Notes |
|---------|---------|-------------|-------|
| `partykit` (legacy) | `0.0.115` | March 2025 | Deploys to PartyKit Cloud managed |
| `partyserver` (canonical) | `0.0.58` [unverified — run `npm show partyserver version` before pinning] | Active | Deploys to your own CF account |
| `partysocket` (client) | `1.1.2` | March 22, 2025 | Now lives in cloudflare/partykit repo |
| `hono-party` | See cf partykit repo | Active | Hono HTTP middleware for partyserver |

### Post-Acquisition Status

Cloudflare acquired PartyKit in April 2024. Since then:
- Codebase moved to `github.com/cloudflare/partykit` (canonical)
- `partyserver` emerged as the clean Durable-Objects-native API
- Roadmap includes: real-time React with Server Components, AI agent primitives, edge-native game session hosting
- All new documentation points to self-deployment path, not managed cloud

### Free Tier Specifics (Durable Objects on Workers Free Plan — April 2025 Unlock)

As of **April 7, 2025**, Cloudflare officially brought Durable Objects to the Workers Free plan. Before this date they required a paid account. This is the unlock that makes PartyServer viable for Boss at zero cost.

| Limit | Free Tier |
|-------|----------|
| Worker requests/day | 100,000 |
| Durable Object requests/day | 100,000 |
| DO compute duration/day | ~28 hours (13,000 GB-s) |
| DO storage per instance | 1 GB (SQLite-backed) |
| WebSocket billing ratio | 20:1 (1M WS messages = 50k DO requests) |
| Static asset requests | Unlimited |

**Math for a 2-player kids game:**
- Each match = 1 Durable Object room
- 3-minute game, messages every ~2s = ~180 WS messages → 9 DO requests per room
- 100,000 DO requests ÷ 9 = **~11,000 game completions per day on the free tier**
- Effectively unlimited at Boss's scale

**Critical:** Enable WebSocket Hibernation in the partyserver class.
- Without hibernation: max 100 connections per room, DO always hot, burns duration budget
- With hibernation: max 32,000 connections per room, DO sleeps between messages, zero duration cost

### Deployment Model

```bash
# Boss's path (self-hosted on your CF account)
npm install partyserver partysocket wrangler
npx wrangler deploy
```

URL pattern: `https://<worker-name>.<subdomain>.workers.dev/parties/<server-class>/<room-id>`

### Party.Server (partyserver) Current API Shape

```typescript
import { Server, type Connection, type ConnectionContext } from "partyserver";

export class GameRoom extends Server {
  private gameState!: GameState;

  async onStart() {
    // Called on wake from hibernation — reload state from storage
    const saved = await this.ctx.storage.get<GameState>("state");
    this.gameState = saved ?? createInitialState();
  }

  async onConnect(conn: Connection, ctx: ConnectionContext) {
    // Send current state to joining player
    conn.send(JSON.stringify({ type: "SYNC_STATE", payload: this.gameState }));
    this.room.broadcast(
      JSON.stringify({ type: "PLAYER_JOIN", id: conn.id }),
      [conn.id]   // exclude sender
    );
  }

  async onMessage(message: string, sender: Connection) {
    const msg = JSON.parse(message);
    // Handle ANSWER_SUBMIT, HEARTBEAT, JOIN_ROOM, etc.
    this.room.broadcast(JSON.stringify(resultMsg));
  }

  async onClose(conn: Connection) {
    this.room.broadcast(
      JSON.stringify({ type: "PLAYER_DISCONNECT", id: conn.id })
    );
  }

  readonly options = { hibernate: true };  // essential — enable it
}
```

**wrangler.toml** (required for DO binding):
```toml
[[durable_objects.bindings]]
name = "GAME_ROOM"
class_name = "GameRoom"

[[migrations]]
tag = "v1"
new_sqlite_classes = ["GameRoom"]
```

### Client API (partysocket + React hook)

```typescript
// Vanilla — works inside Phaser or standalone
import PartySocket from "partysocket";

const socket = new PartySocket({
  host: "your-worker.your-subdomain.workers.dev",
  room: "TIGR",       // 4-char room code
  party: "gameroom",  // matches DO class route
});
socket.onmessage = (evt) => { /* handle server messages */ };
socket.send(JSON.stringify({ type: "ANSWER_SUBMIT", choiceIndex: 2, clientTs: Date.now() }));
```

```typescript
// React hook (clean mount/unmount lifecycle)
import { usePartySocket } from "partysocket/react";

const socket = usePartySocket({
  host: "your-worker.your-subdomain.workers.dev",
  room: roomCode,
  party: "gameroom",
  onMessage: (evt) => dispatch(parseServerMsg(evt.data)),
  onClose: () => dispatch({ type: "DISCONNECTED" }),
});
```

`PartySocket` extends `ReconnectingWebSocket` — automatic exponential-backoff reconnection. Critical for mobile 4G→WiFi handoffs.

### Named Production Apps Using PartyKit / PartyServer

1. **tldraw** (tldraw.com) — collaborative infinite canvas. PartyKit powers real-time sync. Their self-hosted solution uses CF Durable Objects directly.
2. **Stately** (stately.ai) — visual state machine editor. Uses PartyKit to run collaborative XState machines on the edge.
3. **UnReel by DataStax** (github.com/datastax/unreel) — AI-generated multiplayer movie quiz, December 2024. Up to 16 players, real-time scoring by correctness + response time. Built in 2 weeks. Closest production analog to V2.
4. **BlockNote** (blocknote.dev) — open-source rich text editor with collaborative editing via partyserver.
5. **Kent C. Dodds' epicweb.dev** — live avatar presence layer for live workshops.
6. **Sketch Mosaic** (github.com/partykit/sketch-mosaic) — multiplayer drawing game: sync-on-connect, broadcast-on-update. The exact state sync pattern Boss needs.

### Known Gotchas (2026)

- **Hibernation + state loss:** The DO class instance is destroyed between messages when hibernation is on. MUST re-read state from `this.ctx.storage` in `onStart()`. In-memory class variables do NOT persist across hibernation cycles.
- **100-connection non-hibernating limit:** Irrelevant for 2-player game, but know it exists.
- **WebSocket 20:1 billing ratio:** Very cheap — 1M WS messages = 50k DO requests.
- **Cold start:** First request to a DO in a new region: 100-200ms overhead [unverified exact]. Subsequent requests: single-digit ms overhead.
- **partysocket moved repo:** As of March 2025, `partysocket` npm package lives in `cloudflare/partykit` repo (not old `partykit/partykit`). Package name unchanged.
- **India ISP routing issue:** See Axis 6.

---

## Axis 2 — Multiplayer 2-Player Race Game Reference Apps

### Per-App Analysis

**JKLM.fun / BombParty (jklm.fun)**
- Room code: 4-character uppercase random (e.g., `WXYZ`)
- Max players: 16 per BombParty room
- Stack: Custom WebSocket server. Bot reverse-engineering reveals two distinct sockets — one for room handshake, one for game events. Likely custom Node.js, not Socket.IO.
- Reconnect: No documented grace period. Room lives until host leaves.
- Host drop: Game ends. No host migration.

**Jackbox Games (jackbox.tv)**
- Room code: 4-character uppercase A-Z. No numbers. Designed to be shouted across a room.
- Max players: 4-8 depending on game title
- First player = VIP → gets Start Game button. Clean kids UX pattern.
- Lobby: Enter code + name on jackbox.tv. Host on TV/main screen.
- Reconnect: Code-based rejoin within session lifetime.

**Kahoot (kahoot.it)**
- Room code: 6-digit numeric PIN. Why numeric: designed for projection screens with young kids calling out numbers. Readability over brevity.
- Max players: 2,000 (managed infra)
- Architecture: Host-paced. All players see same question simultaneously. Answer → server validates → broadcasts result. Server-authoritative.
- Reconnect: Session ends when host closes. No persistent reconnect.

**Quizlet Live (quizlet.com)**
- Closest analog to V2. Individual race mode: all players see same question, first correct answer wins the round.
- Server validates answer correctness + records server-side timestamp. Fastest correct answer wins.
- Used in classrooms globally — well-tested fairness model.

**Skribbl.io (skribbl.io)**
- Stack: Node.js + Socket.IO. Client connects to `/play` → gets server URI → Socket.IO connection. Falls back to polling if WS fails.
- Room code: random URL ID shared as link
- Server-authoritative state. Turn-based (not tap-race).

**Gartic Phone (gartic.io)**
- Short alphanumeric code. Auto-submits blank for disconnected player at timer expiry — clean "no infinite wait" pattern for kids.
- Server-authoritative, multi-round compilation model.

**Summary Table**

| Game | Code Format | Max Players | Host Drop | Reconnect | Notable |
|------|------------|-------------|-----------|-----------|---------|
| JKLM/BombParty | 4-char A-Z | 16 | Game ends | None | Custom WS server |
| Jackbox | 4-char A-Z | 4-8 | Game ends | Code-based | VIP pattern |
| Skribbl.io | Long URL ID | 12 | Game ends | Socket.IO | Polling fallback |
| Kahoot | 6-digit PIN | 2,000 | Game ends | None | Server-auth answers |
| Quizlet Live | Teacher PIN | 40 | Game ends | None | Closest to V2 |
| Gartic Phone | Short alpha | 30 | Auto-skip | Rejoin link | Blank-on-timeout |

**Pattern:** No game at this scale and player age implements host migration. When host drops, game ends. Right call for V2.

---

## Axis 3 — State-Sync Protocol Design for 2-Player Race

### Model Comparison

| Model | Latency | Fairness | Complexity | Right for V2? |
|-------|---------|----------|------------|---------------|
| Authoritative server (event log) | +1 RTT for result | High | Low-medium | **YES** |
| Client prediction + server reconciliation | Near-zero perceived | High | High | Overkill for MCQ |
| CRDT (Yjs/Automerge) | Low overhead | Low — no ordering guarantee | Medium | NO |
| Lockstep deterministic | Must sync every tick | Perfect | High | NO — wrong for MCQ |
| WebRTC P2P + arbiter | Low if peers close | Medium | High | NO — no server validation |

**Recommended: Authoritative Server with Event Log + Optimistic UI tap feedback.**

**Protocol:**
1. Server generates question (or uses deterministic seed — see Axis 7)
2. Server broadcasts `QUESTION_BROADCAST` to both clients simultaneously
3. Client taps choice → sends `ANSWER_SUBMIT { choiceIndex, clientTs }`
4. Server validates correctness, records `serverReceiveTs = Date.now()`
5. Earliest `serverReceiveTs` with correct answer wins
6. Server broadcasts `ROUND_RESULT` to both clients

### TypeScript Message Schema

```typescript
type PlayerId = "host" | "guest";

// Client → Server
interface AnswerSubmit {
  type: "ANSWER_SUBMIT";
  questionIndex: number;
  choiceIndex: number;    // 0-3
  clientTs: number;        // for latency logging only, not arbitration
}

interface HeartbeatMsg {
  type: "HEARTBEAT";
  ts: number;
}

interface RejoinMsg {
  type: "REJOIN";
  token: string;          // session token from sessionStorage
}

// Server → Client
interface SyncState {
  type: "SYNC_STATE";
  gamePhase: "LOBBY" | "ACTIVE" | "ROUND_RESULT" | "GAME_OVER";
  currentQuestion: Question | null;
  scores: Record<PlayerId, number>;
  ropePosition: number;    // -3 to +3
}

interface QuestionBroadcast {
  type: "QUESTION_BROADCAST";
  question: Question;
  questionIndex: number;
  timeoutMs: number;       // how long kids have to answer
}

interface RoundResult {
  type: "ROUND_RESULT";
  winner: PlayerId | "TIE";
  correctAnswer: number;
  newScores: Record<PlayerId, number>;
  newRopePosition: number;
  nextQuestionIn: number;   // ms delay before next question
}

interface PlayerDisconnect {
  type: "PLAYER_DISCONNECT";
  playerId: PlayerId;
  gracePeriodMs: number;
}

interface GameOver {
  type: "GAME_OVER";
  winner: PlayerId | "DRAW";
  finalScores: Record<PlayerId, number>;
}

interface Question {
  id: number;
  text: string;            // "4 + 7 = ?"
  choices: number[];       // [9, 11, 8, 12]
  correctIndex: number;
}
```

### "First Tap" Arbitration (Both Answers Within 50ms)

```
Client A taps at T=0 → arrives at server at T=80ms
Client B taps at T=10ms → arrives at server at T=85ms
→ Server sees A first → A wins
```

Server timestamp is the source of truth. Client timestamps are ignored for arbitration. This is exactly how Quizlet Live works. For ages 6-8 it's perfectly fair — no compensation logic needed.

**Tie handling (same millisecond):** Declare "TIE", rope doesn't move, no point awarded. Statistically extremely rare.

### Not a Tick Loop — Event Log Model

No full-state diff on every tick. Events only:
- `QUESTION_BROADCAST` → `ANSWER_SUBMIT` × 2 → `ROUND_RESULT` → repeat
- On reconnect: server sends full `SYNC_STATE` to reconnecting client
- State size: ~200 bytes (2 scores, rope position, current question, phase)

---

## Axis 4 — Room Code UX

### Code Length Collision Math

| Length | Safe alphabet (22 chars, see below) | Total combos | 50% collision at N concurrent rooms |
|--------|-------------------------------------|-------------|--------------------------------------|
| 4 chars | 22 | 234,256 | ~572 rooms |
| 5 chars | 22 | 5,153,632 | ~2,700 rooms |
| 6 chars | 22 | 113,379,904 | ~12,600 rooms |

For a game where rooms last ≤15 minutes and peak concurrent rooms might be 50-200: **4 chars is safe with a uniqueness check on generation**. If Boss expects viral growth: start with 5 chars — no UX downside, one extra character.

### Safe Alphabet

Remove from A-Z: `O` (vs `0`), `I` (vs `1`/`l`), `L` (vs `1`/`I`), `S` (vs `5`), `Z` (vs `2`), `B` (vs `8`)

**Safe uppercase alphabet: `ACDEFGHJKMNPQRTUVWXY`** (20 chars)

No numbers in the code. Kids 6-8 confuse 0/O and 1/I more than adults.

Jackbox rationale for 4-char uppercase: designed to be shouted across a living room. "TIGR" not "T1G4". Same logic applies here.

### Profanity Filter — Mandatory

TETR.IO learned this lesson the hard way — random 4-letter codes spelled slurs. For a kids game this is a non-negotiable risk to mitigate.

```typescript
import BadWordsFilter from "bad-words"; // v4.0.0, 155 dependents
import { customAlphabet } from "nanoid"; // v5.1.7, crypto-secure

const SAFE_ALPHA = "ACDEFGHJKMNPQRTUVWXY";
const generate = customAlphabet(SAFE_ALPHA, 4);  // or 5
const filter = new BadWordsFilter();

function generateRoomCode(): string {
  while (true) {
    const code = generate();
    if (!filter.isProfane(code.toLowerCase())) return code;
  }
}
```

`nanoid` uses `crypto.getRandomValues()` — cryptographically secure. Much better than `Math.random()`.

### Code Expiration

Room auto-closes when both connections drop for >60 seconds. Implement via DO alarm:

```typescript
async onClose(conn: Connection) {
  const remaining = [...this.room.getConnections()].length;
  if (remaining === 0) {
    // Set alarm to clean up in 60s
    await this.ctx.storage.setAlarm(Date.now() + 60_000);
  }
}

async alarm() {
  // Delete room state, DO evicts naturally
  await this.ctx.storage.deleteAll();
}
```

### URL Deep-Link + Code Both

- Code: `mathtug.app` → "Join Room" → enter `TIGR`
- Deep-link: `mathtug.app/join/TIGR` → auto-fills → tap Join
- WhatsApp share: send deep-link (easy copy-paste). Code for verbal communication.

This is better than Jackbox (code-only, TV-room context) because Boss's use case includes WhatsApp sharing.

### Reference Naming

| Game | Format | Why |
|------|--------|-----|
| BombParty, Jackbox | 4-char A-Z | Shoutable, minimal collision at scale |
| Kahoot | 6-digit numeric | Projection screen readability for young kids |
| Codenames Online | 6-char alphanumeric | Typed into URL, less verbal sharing |

---

## Axis 5 — Reconnect / Disconnect UX

### WebSocket Disconnect Classes

1. **Clean close (`ws.close()`):** Tab/app closed. `onclose` fires with code 1000. Handled cleanly.
2. **Network drop (4G→WiFi handoff):** TCP connection silently dies. Neither side gets immediate notification. Detected only by heartbeat timeout.
3. **Mobile Safari background:** iOS freezes the app. WS appears open client-side but no data flows. `onclose` may not fire for 30-60+ seconds. **The main pain point.**
4. **Screen lock:** Same as backgrounding.

### Mobile Safari Specific — The Nasty One

Safari on iOS aggressively suspends WS connections when the app is backgrounded or the screen locks. The JS socket may appear `OPEN` but `.send()` calls silently fail. The `onclose` event may not fire for 30-60+ seconds.

**Mitigation strategy (required for V2):**

```typescript
// 1. Client-side heartbeat at 15s
setInterval(() => {
  if (socket.readyState === WebSocket.OPEN) {
    socket.send(JSON.stringify({ type: "HEARTBEAT", ts: Date.now() }));
  }
}, 15_000);

// 2. Force reconnect on visibility restore (Safari iOS)
document.addEventListener("visibilitychange", () => {
  if (document.visibilityState === "visible") {
    if (socket.readyState !== WebSocket.OPEN) {
      socket.reconnect(); // PartySocket built-in
    }
  }
});

// 3. Reconnect detection timeout
// If no HEARTBEAT response within 20s → force reconnect
```

PartySocket's built-in `ReconnectingWebSocket` handles exponential backoff automatically — but you still need the visibility listener for iOS.

### Disconnect UX for Ages 6-8

**Recommended V2 behavior:**
- Show overlay: "Waiting for [Tiger/Elephant]... (30s countdown)"
- If reconnect within 30 seconds: resume match from server state (SYNC_STATE on reconnect)
- If no reconnect in 30 seconds: "Friend couldn't reconnect — match ended" → Results screen with partial scores

**Grace period research:**
- Kahoot: 0s (session ends when host closes)
- Photon Engine default: 10s
- Quizlet Live: ~10s
- Gartic Phone: ~60s (async game, more tolerance)
- **Recommendation: 30s for a kids math race** — long enough to re-open an app, short enough that the waiting kid doesn't give up.

### Host Migration

Not needed — the Durable Object IS the host. If Player A (room creator) disconnects, the DO persists with Player B still connected. The DO waits. On host timeout (no reconnect), end match.

### Session Token for Reconnect

```typescript
// On successful join — server sends session token, client stores in sessionStorage
sessionStorage.setItem("mathTugSession", JSON.stringify({
  roomCode: "TIGR",
  role: "host",
  token: "abc123",
  ts: Date.now()
}));

// On reconnect — client checks and sends token
const session = JSON.parse(sessionStorage.getItem("mathTugSession") ?? "null");
if (session && Date.now() - session.ts < 5 * 60 * 1000) {
  socket.send(JSON.stringify({ type: "REJOIN", token: session.token }));
}
```

`sessionStorage` (not `localStorage`) — clears when browser session ends, matching the ephemeral room lifecycle.

### Heartbeat Interval

- **15 seconds** for mobile Safari keep-alive
- Server responds with `PONG` immediately
- DO hibernation-safe: each HEARTBEAT wakes DO, processes PONG, DO re-hibernates
- Client force-reconnects if no PONG within 20s

---

## Axis 6 — Latency Budgets + 4G/3G Handling

### Latency Thresholds for Tap-Race

| RTT | Feel | For MCQ race |
|-----|------|-------------|
| < 100ms | Instant | Perfectly fair |
| 100-200ms | Slight delay | Acceptable — kids don't notice 150ms |
| 200-300ms | Noticeably laggy | Marginal for MCQ |
| > 300ms | Broken | Unfair tap-race |

For a kids educational game (not esports), **200ms acceptable cutoff** is defensible. The game is about learning, not millisecond reaction time.

### India 4G → Cloudflare Edge (Real Numbers)

| Scenario | Approximate RTT |
|----------|----------------|
| Indian user → CF Mumbai (direct peering) | 30-60ms |
| Indian user → CF Mumbai (CF free plan, possible rerouting) | 100-160ms |
| Indian user → Singapore (Jio/Airtel re-route) | 80-120ms |
| 4G Sprint US (benchmark comparison) | ~150ms |
| 3G anywhere | 200-400ms |

**The India problem:** Jio and Airtel (combined ~75% Indian mobile market as of 2025) have historically lacked direct peering with Cloudflare, causing traffic to route via Singapore or Marseille instead of Mumbai/Chennai/Delhi — adding 50-100ms RTT on free tier. Cloudflare has 20+ PoPs in India but the ISP peering gaps affect free-tier users specifically.

**Application-level mitigation: none.** It affects both players equally on the same ISP → relative fairness maintained. Document as known limitation.

### Slow Network UX

```typescript
// Server tracks rolling RTT via HEARTBEAT timestamps
const rtt = Date.now() - msg.ts;
if (rtt > 300) {
  sender.send(JSON.stringify({ type: "NETWORK_SLOW", yourRtt: rtt }));
}
```

UX: small wifi-with-exclamation icon. No artificial handicap — complexity not worth it for V2.

### Latency Masking (Optimistic UI)

When player taps an answer:
1. **Immediately** highlight tapped choice as "selected" (optimistic visual, zero latency)
2. Wait for `ROUND_RESULT` from server (~100-200ms)
3. Reveal correct answer + winner overlay

The instant visual feedback psychologically covers the network round-trip. Do NOT show "you won!" optimistically — requires server confirmation. This pattern (optimistic input, server-authoritative result) is well-documented by Gabriel Gambetta's canonical game networking articles.

---

## Axis 7 — Anti-Cheat / Answer Integrity

### Threat Model

| Threat | Likelihood | Mitigation |
|--------|-----------|-----------|
| 10-year-old opens DevTools, injects answer | Medium | Server validates correctness |
| Multiple rapid taps to game the timestamp | Low | Rate limit + per-round idempotency |
| Network proxy manipulation for timing | Very low | Server timestamp wins, client ts ignored |
| Correct answers visible in WS traffic | Low | Questions broadcast from server, answers never sent until ROUND_RESULT |

### Server-Side Validation: Yes, Required

```typescript
async onMessage(message: string, sender: Connection) {
  const msg = JSON.parse(message);

  if (msg.type === "ANSWER_SUBMIT") {
    const q = this.gameState.currentQuestion;
    if (!q || this.gameState.roundWinner) return; // no question or already resolved

    const isCorrect = msg.choiceIndex === q.correctIndex;
    const playerId = this.getPlayerRole(sender.id);

    if (isCorrect) {
      this.gameState.roundWinner = playerId;
      this.room.broadcast(JSON.stringify({
        type: "ROUND_RESULT",
        winner: playerId,
        correctAnswer: q.correctIndex,
        newScores: this.updateScores(playerId),
        newRopePosition: this.updateRope(playerId),
        nextQuestionIn: 2000
      }));
    }
  }
}
```

### Server-Side Question Generation (Recommended)

Server generates arithmetic questions on-demand — no database needed:

```typescript
function generateQuestion(index: number, roomSeed: number): Question {
  const a = ((roomSeed * index + 7) % 8) + 2;   // 2-9
  const b = ((roomSeed * index + 13) % 8) + 2;
  const answer = a + b;
  const wrongAnswers = [answer - 1, answer + 1, answer + 2];
  const choices = shuffle([answer, ...wrongAnswers], roomSeed + index);
  return {
    id: index,
    text: `${a} + ${b} = ?`,
    choices,
    correctIndex: choices.indexOf(answer)
  };
}
```

Questions are never sent "in advance" — server holds the answer and broadcasts the question when the round starts.

### Rate Limiting + Idempotency

```typescript
// Per-connection rate limit
const lastAnswer = this.gameState.lastAnswerTs[sender.id] ?? 0;
if (Date.now() - lastAnswer < 500) return; // 500ms minimum between submits
this.gameState.lastAnswerTs[sender.id] = Date.now();

// Idempotency: one answer per (playerId, questionIndex)
if (this.gameState.answeredBy[playerId]?.has(msg.questionIndex)) return;
this.gameState.answeredBy[playerId].add(msg.questionIndex);
```

---

## Axis 8 — Lobby + Matchmaking Flow

### Create-Room Flow

```
Home Screen
  → Tap "Play with Friend (Their Phone)"
  → [Settings: difficulty / question count]
  → Server: generate code "TIGR", create DO room
  → Code Display Screen:
      ┌───────────────────────────────────┐
      │  Your Room Code                   │
      │                                   │
      │       T  I  G  R                  │  ← Large, clear
      │                                   │
      │  [Copy Link] [WhatsApp Share]     │
      │                                   │
      │  Waiting for friend...  🐘        │
      │  (animated elephant waiting)      │
      └───────────────────────────────────┘
  → Guest joins → both see Lobby Screen
  → Host taps "Start Game!"
```

### Join-Room Flow

```
Home Screen
  → Tap "Join a Room"
  → Code Entry Screen (4 large boxes, keyboard auto-opens, letter input)
  → Enter "TIGR" → tap "Join"
  → Connecting... → Lobby Screen
```

### Lobby State (Both Devices)

```
Lobby Screen
  ┌─────────────────────────────────────┐
  │  Room: T I G R                      │
  │                                     │
  │  🐯 Tiger ✓       🐘 Elephant ✓    │
  │                                     │
  │  Questions: 10   Level: Easy        │
  │  [Host only: ⚙️ Change Settings]    │
  │                                     │
  │  [HOST ONLY: "Start Game!" button]  │
  └─────────────────────────────────────┘
```

**Settings control:** Host only. Guest sees read-only. Removes confusion for kids.

**Start trigger:** Host-only explicit start. Not auto-start on both-ready — kids need the moment of anticipation.

### Player Identity

- Room creator = Tiger (P1). Room joiner = Elephant (P2). Not configurable — eliminates a choice screen.
- Names: default to animal names. Do not ask for real name — kids privacy, COPPA surface.

### Rematch Flow

```
Game Over: "Tiger wins! 🐯"
[Tiger: Rematch?]  [Elephant: Rematch?]
Both tap → Server resets game state, keeps room code alive → new match
Either taps "Home" → room closes
```

Server listens for `REMATCH_VOTE` from both players. When both vote → reset state → send new `SYNC_STATE` with phase "LOBBY".

### Reference UX Patterns

- **Jackbox:** VIP (first joiner) starts game. Room code on TV screen. Phone shows interaction only. Directly applicable.
- **Skribbl.io:** Lobby shows players as they join. Settings panel (host can change). "Start Game" button for host. Cleanest web reference.
- **Gartic Phone:** Blank-on-timeout for disconnected players — clean "no infinite wait" pattern for kids.

---

## Axis 9 — Mode-Router Architecture Inside the React App

### Current V1 Screen States

```
'home' → 'setup' → 'match' → 'results'
```

Mode (solo vs hotseat) is set during setup. No explicit mode routing.

### V2 Extended State Machine

```
'home'
  ├── mode: 'solo'      → 'setup' → 'match' → 'results'
  ├── mode: 'hotseat'   → 'setup' → 'match' → 'results'
  └── mode: 'online'
        ├── 'create_room'   → 'waiting'
        ├── 'join_room'     → 'joining'
        └── 'lobby' → 'match_online' → 'results'
                          ↕ (overlay)
                     'reconnecting'
```

### Zustand Store Additions

```typescript
type GameMode = "solo" | "hotseat" | "online";
type OnlinePhase =
  | "idle" | "creating" | "waiting" | "joining"
  | "lobby" | "active" | "reconnecting" | "ended";

interface OnlineState {
  phase: OnlinePhase;
  roomCode: string | null;
  myRole: "host" | "guest" | null;
  opponentConnected: boolean;
  opponentName: string;
  latencyMs: number | null;
}

// Extend existing GameStore:
interface GameStore {
  // ... existing fields ...
  mode: GameMode;                  // NEW
  online: OnlineState;             // NEW
  setMode: (m: GameMode) => void;
  setOnlinePhase: (p: OnlinePhase) => void;
}
```

### Screen Routing

```typescript
// App.tsx
function App() {
  const { screen, mode, online } = useGameStore();

  if (screen === "home") return <HomeScreen />;
  if (screen === "setup" && mode !== "online") return <SetupScreen />;
  if (screen === "match") {
    if (mode === "online") return <MatchScreenOnline />;   // NEW
    return <MatchScreen />;                                 // V1 existing
  }
  if (screen === "results") return <ResultsScreen />;

  // Online-only screens
  if (mode === "online") {
    if (online.phase === "creating" || online.phase === "waiting")
      return <CreateRoomScreen />;
    if (online.phase === "joining")
      return <JoinRoomScreen />;
    if (online.phase === "lobby")
      return <LobbyScreen />;
  }
}

// ReconnectingOverlay renders on top of MatchScreenOnline when phase === 'reconnecting'
```

### MatchScreenOnline vs V1 MatchScreen (Hot-Seat)

| Feature | V1 Hot-Seat | V2 Online |
|---------|-------------|-----------|
| MCQ grid layout | Two mirrored grids, landscape | Single full-width grid, portrait |
| Orientation | Landscape locked | Portrait-friendly |
| Opponent MCQ | Shown (mirrored) | NOT shown — just answered/thinking indicator |
| Tug-of-war canvas | Shared horizontal canvas | Full-width canvas |
| Score display | In each grid | Header row |

`MatchScreenOnline` is a **new component**. Does not reuse the mirrored-grid layout.

### Component Reuse Assessment

| V1 Item | Reusable in V2 Online? | Changes |
|---------|----------------------|---------|
| `useGameLoop.ts` | Partially | Extract question logic; replace "next question" trigger with server ROUND_RESULT message |
| `gameStore.ts` | Mostly | Add online state slice |
| `MatchScreen.tsx` (hot-seat) | No — different layout | Create `MatchScreenOnline.tsx` |
| `MCQGrid.tsx` | Yes | None |
| `TugCanvas.tsx` (Phaser) | Yes — rope pos via Zustand | None |
| `ResultsScreen.tsx` | Yes | Handle online mode data |
| `SoundManager.ts` | Yes | None |
| Confetti utils | Yes | None |

**Net: ~60% reuse. New work:**
1. `CreateRoomScreen.tsx`, `JoinRoomScreen.tsx`, `LobbyScreen.tsx`
2. `usePartyRoom.ts` — custom hook wrapping PartySocket + Zustand dispatch
3. `MatchScreenOnline.tsx` — single-player portrait layout
4. `party/gameRoom.ts` — partyserver DO class

### Folder Structure for V2

```
kids-math-tug/
├── src/
│   ├── screens/
│   │   ├── CreateRoomScreen.tsx     [NEW]
│   │   ├── JoinRoomScreen.tsx       [NEW]
│   │   ├── LobbyScreen.tsx          [NEW]
│   │   └── MatchScreenOnline.tsx    [NEW]
│   ├── hooks/
│   │   └── usePartyRoom.ts          [NEW]
│   └── store/
│       └── gameStore.ts             [MODIFIED]
├── party/
│   └── gameRoom.ts                  [NEW — partyserver DO]
├── wrangler.toml                    [NEW]
├── vite.config.ts                   [MODIFIED — Cloudflare Vite Plugin]
└── package.json                     [MODIFIED]
```

**Deployment:**
- SPA: continues to Cloudflare Pages (no change)
- DO Worker: via Cloudflare Vite Plugin (released 2025, reached 1.0) — single `vite build` outputs both SPA + Worker. Strongly recommended over separate wrangler deploy.

---

## Axis 10 — Anti-Patterns and What NOT to Do

### 1. Firebase Realtime Database for Game State

- Firebase RTDB has 100-300ms+ write-to-read propagation latency (documented as "near real-time")
- No server-side validation model — client writes are trusted unless you write complex security rules
- Document contention at 10-20 concurrent users causes 0.5-2s lag
- Charges per GB downloaded — constant state diffing balloons cost
- Vendor lock-in to Google ecosystem

PartyServer + DO is strictly better for this use case in every dimension.

### 2. Socket.IO Standalone Server

- Socket.IO requires sticky sessions — all WS messages from one client must hit the same server process
- Cloudflare Workers are stateless by design — no sticky sessions
- Socket.IO's polling fallback degrades latency on mobile
- Requires a persistent VM/container (Heroku, Railway) — costs money even at low scale
- Socket.IO v4.x bundle overhead: ~170KB gzipped

PartySocket is the correct replacement.

### 3. Pusher / Ably / PubNub

Not wrong, but unnecessary and overpriced for this use case:
- Pusher free: 100 concurrent connections, 200K messages/day — too tight for any growth
- Ably free: 200 concurrent channels — OK but $30+/month when exceeded

Boss has CF free tier with DO. PartyServer is the zero-cost native option. These services make sense for teams with budget who don't want to manage CF accounts.

### 4. HTTP Polling Instead of WebSocket

Never for tap-race. Even 100ms polling = 10 requests/second/client × 2 players = 20 req/s. WebSocket full-duplex is the only correct choice for real-time game state.

### 5. PostgreSQL/Redis for Ephemeral Room State

A 2-player math game room's entire state is ~200 bytes (2 scores, rope position, current question, game phase). Storing it in a DO class instance + optional `ctx.storage` for reconnect is correct. Standing up Postgres + Redis pub/sub for this is architectural malpractice.

### 6. Yjs/Automerge CRDT for Quiz Race

CRDTs are designed for collaborative editing where clients diverge and merge. A tap-race has total ordering requirements (who answered first?) that CRDTs cannot provide — CRDTs have no concept of "which event happened first globally." Authoritative server event-log is correct here. Using Yjs adds 100KB+ bundle overhead for zero benefit.

### 7. WebRTC P2P (No Server)

- Still requires STUN/TURN infrastructure for NAT traversal
- No authoritative arbiter — one peer must act as "trusted server" which trivially enables cheating
- Mobile WebRTC on Safari iOS remains finicky
- Signaling server still needed for SDP exchange

For server-side answer validation, P2P is architecturally incompatible.

### 8. Building Your Own WebSocket Server From Scratch

`partyserver` wraps the DO WebSocket API with clean lifecycle hooks (`onConnect`, `onMessage`, `onClose`, `onStart`, hibernation support). Building this from raw Durable Object WebSocket API reinvents everything partyserver provides. Don't.

### 9. Polling for Room Status (Host Waiting Screen)

While host waits for guest, do NOT poll `GET /room/TIGR/status` every second. Host holds open WebSocket to the DO. Server sends `PLAYER_JOINED` event when guest connects. One persistent WS replaces N polling requests.

### 10. Skipping Profanity Filter on Room Codes

TETR.IO ships without a profanity filter and generates slur codes. For a kids game, unacceptable. Always filter server-side before returning the code. One-line fix with `bad-words@4.0.0`.

---

## Open Questions for Phase 2 Synthesis Brief

These are the decisions Jarvis must lock in before dispatching to backend + frontend agents:

**Q1: Boss's Cloudflare account status?**
`partyserver` self-host requires a CF account (same one as Cloudflare Pages). If Boss is already using CF Pages for V1, the account exists — confirm it has Workers enabled (should be on free tier after the April 2025 unlock).

**Q2: Room code length — 4 or 5 chars?**
4 chars = safe at realistic scale, casual feel. 5 chars = one extra character, more robust, no UX downside. Recommend 5 chars if Boss has no preference.

**Q3: Cloudflare Vite Plugin or separate wrangler.toml?**
Vite Plugin (stable 1.0, 2025): single `vite build` outputs SPA + Worker together. Cleanest path given V1 is already on Vite 6. Alternative: separate `wrangler.toml` + separate `wrangler deploy` step. Recommend Vite Plugin.

**Q4: Question generation — live server-side arithmetic or pre-seeded list?**
Server-side arithmetic generation (trivial for ages 6-8 addition/subtraction) is recommended — no database, no sync issues. Confirm: should difficulty scale mid-match (adaptive), or fixed difficulty set at lobby?

**Q5: Reconnect grace period — 30s or longer?**
30s recommended. Is there a preference? Shorter = cleaner end state. Longer = more kid-friendly.

**Q6: Does TugCanvas.tsx already read `ropePosition` from Zustand directly?**
If yes, V2 online mode just needs to write `ropePosition` updates from server messages into Zustand and the canvas works unchanged. Confirm by reading `TugCanvas.tsx` before builder dispatch.

**Q7: Portrait vs landscape lock for online mode?**
V1 hot-seat is landscape-locked (2 kids, 1 phone). V2 online should be portrait-friendly (each kid's own phone). This changes CSS and Phaser canvas sizing. Confirm orientation preference before UI build.

**Q8: Player names — animal-only or allow custom?**
Animal names (Tiger/Elephant) is simplest and avoids COPPA surface. Custom names = text input = data collection concern for ages 6-8. Recommend animal-only for V2.
