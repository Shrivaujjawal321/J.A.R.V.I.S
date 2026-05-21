# Kids Math Tug-of-War — V1 Build Brief

**Owner:** Boss (Ujjawal)
**Project:** Standalone web app
**Target path:** `/home/ujjwal/Documents/kids-math-tug/` (separate from Jarvis repo)
**Bar:** 2026-tier. Reference: Khan Academy Kids audio density + Toca Boca illustration polish + Math Duel's mechanic + visual originality that no competitor has.
**V1 goal:** Shippable, smoke-tested, end-to-end playable. Deployable to Cloudflare Pages. Phone landscape + tablet + desktop responsive.

---

## 1. Product summary

A 2-player educational math web game for kids aged 6-8. Full screen split horizontally:
- **Top half**: Tug-of-war visual — Tiger 🐯 (Player 1) vs Elephant 🐘 (Player 2), rope between them, finish lines on both ends.
- **Bottom half**: Math question (center, shared) + mirrored 2×2 MCQ button grid for each player.

Both players see the SAME question and race to tap the correct answer on THEIR side first. Correct answer → opponent's character pulled +1 step toward your finish line. Wrong answer → your character moves back -0.5 step. First to pull opponent past their finish line wins.

Modes: **2-player hot-seat** (same device) + **AI opponent** (Easy / Medium / Hard).

---

## 2. Tech stack (LOCKED)

| Layer | Choice | Version | Why |
|-------|--------|---------|-----|
| Build tool | **Vite** | 6.x | Pure client SPA, no SSR/SEO needed, fastest HMR, deploys static to Cloudflare Pages free tier |
| Framework | **React** | 19 | Modern hooks, ViewTransition built-in |
| Language | **TypeScript** | 5.x strict | Type safety on game state machine |
| Styling | **Tailwind CSS** | 4 | OKLCH colors, design tokens, mobile-first |
| Game engine | **Phaser** | 4.1.0 | Built-in scene mgmt, tweens, physics, input, audio, Rope object out of box |
| UI animations | **Framer Motion** | 12 | Spring physics on buttons, results screen, layout animations |
| Sound | **Howler.js** | 2.2.x | 7KB, audio sprites, iOS/Android browser-safe |
| Particles | **@tsparticles/confetti** | latest | Plug-and-play burst on correct answer + win screen |
| Fonts | **Fredoka** (heading) + **Nunito** (body) | Google Fonts, variable | Kid-friendly, rounded, high legibility |
| Lint/format | **ESLint** + **Prettier** | latest | Standard |
| Deploy target | **Cloudflare Pages** | — | Free, global CDN, good India latency. Use `vite build` → `dist/` |

**Deferred to V2 (DO NOT include in V1):**
- Rive characters (use SVG cartoon + Framer Motion tweens for V1)
- PWA install prompt + service worker offline (V1 ships web-only)
- Web Speech API read-aloud (V1 numbers-only, no spoken questions)
- Character unlocks / badge system / post-match stats persistence
- Hindi/English language toggle (V1 numbers-only minimal text)
- Online multiplayer

---

## 3. Project structure

```
kids-math-tug/
├── public/
│   ├── sounds/
│   │   ├── correct.mp3       (bright C-major chime, 0.3s)
│   │   ├── wrong.mp3         (soft descending boop, 0.2s)
│   │   ├── pull.mp3          (rope twang, 0.2s)
│   │   ├── win.mp3           (fanfare 1.5s)
│   │   ├── countdown.mp3     (3-2-1 tones)
│   │   └── tap.mp3           (button click, 0.05s)
│   └── favicon.svg
├── src/
│   ├── main.tsx              (React 19 entry)
│   ├── App.tsx               (Top-level router: Home / Setup / Match / Results)
│   ├── screens/
│   │   ├── HomeScreen.tsx    (Mode select: 2P vs AI)
│   │   ├── SetupScreen.tsx   (Topic + difficulty + AI difficulty if applicable)
│   │   ├── MatchScreen.tsx   (The game itself — hosts Phaser canvas + React MCQ UI)
│   │   └── ResultsScreen.tsx (Winner celebration + play again CTA)
│   ├── game/
│   │   ├── PhaserGame.ts     (Phaser 4 game config — single Scene)
│   │   ├── TugScene.ts       (Tug-of-war scene: 2 characters, rope, finish lines, position state)
│   │   ├── characters/
│   │   │   ├── tiger.svg     (SVG cartoon, exportable from Figma/inline)
│   │   │   ├── elephant.svg
│   │   │   └── rope.svg
│   │   └── animation.ts      (Tween helpers: pull, stumble, win-dance, idle bob)
│   ├── math/
│   │   ├── generator.ts      (generateQuestion(op, difficulty) → { question, answer, choices[4] })
│   │   ├── distractors.ts    (3 plausible wrong answers per correct)
│   │   └── ai.ts             (AI opponent: pick answer + reaction time per difficulty)
│   ├── ui/
│   │   ├── AnswerButton.tsx  (Spring-pressed MCQ button with side='left'|'right' theming)
│   │   ├── ScoreBar.tsx      (Optional small visual position indicator)
│   │   ├── Countdown.tsx     (3-2-1 GO overlay)
│   │   ├── MuteToggle.tsx
│   │   └── ResultsCard.tsx
│   ├── hooks/
│   │   ├── useGameLoop.ts    (State machine: idle → countdown → playing → ended)
│   │   ├── useSound.ts       (Howler wrapper, mute aware)
│   │   ├── useReducedMotion.ts
│   │   └── useOrientation.ts (Detect landscape / portrait, show rotate prompt)
│   ├── store/
│   │   └── gameStore.ts      (Zustand or simple useReducer — current match state, settings)
│   ├── styles/
│   │   └── index.css         (Tailwind imports + font-face + global tokens)
│   └── lib/
│       └── colors.ts         (Palette tokens)
├── index.html                (Viewport, theme-color, fonts preload)
├── package.json
├── tsconfig.json
├── tailwind.config.ts
├── vite.config.ts
├── README.md                 (How to run, build, deploy)
└── .gitignore
```

---

## 4. Game state machine (canonical)

```ts
type GameState =
  | { phase: 'home' }
  | { phase: 'setup'; mode: '2p' | 'ai' }
  | { phase: 'countdown'; config: MatchConfig }
  | { phase: 'playing'; config: MatchConfig; current: Question; positions: { p1: number; p2: number }; questionsAsked: number; correctCount: { p1: number; p2: number } }
  | { phase: 'ended'; winner: 'p1' | 'p2' | 'tie'; stats: MatchStats };

type MatchConfig = {
  mode: '2p' | 'ai';
  aiDifficulty?: 'easy' | 'medium' | 'hard';
  operation: '+' | '-' | '×' | '÷';
  difficulty: 'easy' | 'medium' | 'hard';
};

type Question = {
  text: string;          // "7 + 3"
  answer: number;        // 10
  choices: number[];     // [10, 9, 13, 7] shuffled
};
```

**Position scale:** 0 to 10. Both characters start at 5. Correct answer pulls opponent +1 toward your side (your character stays, opponent's position moves). Wrong answer moves your character -0.5 back. Game ends when one character's position ≤ 0 or ≥ 10.

Actually simpler model: **single shared rope position**, starts at 5 (center). P1 correct → position += 1 (moves toward P2). P2 correct → position -= 1 (moves toward P1). Wrong answer for P1 → position -= 0.5 (pulled toward own line). Win conditions: position ≥ 10 → P1 wins (pulled rope flag to their side); position ≤ 0 → P2 wins.

Pick the simpler shared-position model. Implement it.

---

## 5. Layout per breakpoint

### Phone landscape (default, 640×360px)
```
┌─────────────────────────────────────┐
│  P1 finish  ←─ rope ─→  P2 finish   │  ← top half: tug-of-war canvas (Phaser)
│   🐯═══════════🪢═══════════🐘     │
├─────────────────────────────────────┤
│  ⬆ Q: 7 × 4 = ?  ⬆ (center, shared)│  ← question strip (~40px tall)
├──────────────────┬──────────────────┤
│  [ 28 ] [ 24 ]   │   [ 28 ] [ 24 ]  │  ← P1 buttons left, P2 mirrored right
│  [ 32 ] [ 21 ]   │   [ 32 ] [ 21 ]  │     2×2 grid each side
└──────────────────┴──────────────────┘
```

Each button: ~140×80px. Tap target far exceeds 60×60 WCAG min.

### Portrait phone (≤640px width, taller than wide)
Show rotate-to-landscape overlay for 2P mode. AI mode: allow portrait with stacked layout (game top, single MCQ grid bottom).

### Tablet (768-1024px)
3 zones: P1 buttons (left 35%) | Question + rope visual (center 30%) | P2 buttons (right 35%). Game canvas spans full top area. Bigger characters.

### Desktop (≥1280px)
Same as tablet layout, max-width 1280px, centered. Keyboard support:
- P1: `A` `S` `D` `F` for choices 1-4
- P2: `J` `K` `L` `;` for choices 1-4

Labels on buttons show key in corner on desktop only.

---

## 6. Visual design system

### Colors (Tailwind 4 OKLCH tokens)

```css
@theme {
  /* Brand */
  --color-tiger-50: oklch(0.96 0.05 50);
  --color-tiger-500: #FF6B35;     /* P1 side accent */
  --color-tiger-700: #C9512A;

  --color-elephant-100: #E5E5E5;
  --color-elephant-500: #9E9E9E;  /* P2 side accent */
  --color-elephant-700: #616161;

  /* Game feedback */
  --color-correct: #6BCB77;       /* soft green */
  --color-wrong: #FF8A4C;         /* warm orange — NOT pure red, softer for kids */
  --color-rope: #C9A84C;          /* tan/jute */

  /* UI */
  --color-bg: #FFFDF4;            /* warm off-white */
  --color-bg-dark: #1A1A2E;       /* dark mode */
  --color-text: #1F2937;
  --color-accent: #FFCA3A;        /* sunshine yellow CTA */
}
```

Side cues: P1 (left) = warm tones (tiger orange + yellow accents). P2 (right) = cool tones (elephant grey + teal/blue accents). Universally intuitive in competitive games.

### Typography

```css
font-family: 'Fredoka', system-ui, sans-serif;   /* headings, score, question */
font-family: 'Nunito', system-ui, sans-serif;    /* body, labels */
```

Sizes:
- Question: 56-72px (phone) / 80-96px (tablet+)
- Answer button: 40-52px
- Score / countdown: 80-120px
- Body labels: 18-24px min

### Iconography
Thick-outline sticker style. 2-4px stroke, vibrant fill, simple drop-shadow. Inline SVG (no icon library — kids need bold custom illustration, not Heroicons).

### Motion language
- Spring easing on buttons: `{ type: 'spring', stiffness: 300, damping: 20 }`
- Squash & stretch on button press (scale 0.92 → 1.06 → 1.0)
- Idle character: subtle breathing bob (scale 1.0 ↔ 1.03, 2s loop)
- Pull animation: character leans back 5°, plants feet, springs forward
- Rope: SVG path with cubic bezier control point that sags slightly; mid-point oscillates on each pull
- Wrong: 0.2s horizontal shake (±6px, 3 cycles)
- Correct: 0.3s scale-up + 20-25 confetti particles from button

**Respect `prefers-reduced-motion`:**
```css
@media (prefers-reduced-motion: reduce) {
  * { animation-duration: 0.01ms !important; transition-duration: 0.01ms !important; }
}
```
Skip particles, screen shake, rope bounce in reduced mode. Show static ✓ or ✗ instead.

---

## 7. Sound design

Load all sounds via Howler.js as one audio sprite (single file, named regions) for fast load + iOS Safari compatibility.

SFX map:
| Event | Source / generate | Duration |
|-------|-------------------|----------|
| `tap` | Soft pop, button click | 50ms |
| `correct` | Bright C-major chime, rising | 300ms |
| `wrong` | Soft descending two-note boop | 200ms |
| `pull` | Rope twang | 200ms |
| `countdown` | 3 quick tones (low-mid-high) | 1s |
| `win` | Ascending fanfare | 1.5s |

Source files: free CC0 from [Mixkit children pack](https://mixkit.co/free-sound-effects/children/) or [Pixabay sound effects](https://pixabay.com/sound-effects/). Builder agent: download 2-3 candidates per category, pick the best fit, attribute in README.

**Background music**: Skip for V1. Add in V2 (optional toggle, default OFF).

**Mute toggle**: Default ON. Speaker icon in top-right corner on all screens. Persist preference in `localStorage`.

**Audio unlock pattern**: Browser autoplay policies block sound until user interacts. Howler.js handles automatically for most cases, but explicitly unlock on first user tap on Home screen.

---

## 8. Math question generator

```ts
// src/math/generator.ts
type Op = '+' | '-' | '×' | '÷';
type Difficulty = 'easy' | 'medium' | 'hard';

function generateQuestion(op: Op, diff: Difficulty, sessionHistory: Set<string>): Question {
  let a: number, b: number;
  switch (`${op}-${diff}`) {
    case '+-easy':    a = rand(1, 9);   b = rand(1, 9);   break;          // single digit
    case '+-medium':  a = rand(10, 50); b = rand(1, 9);   break;          // no carry
    case '+-hard':    a = rand(10, 50); b = rand(10, 50); break;          // with carry

    case '--easy':    a = rand(2, 20);  b = rand(1, a);   break;          // result ≥ 0
    case '--medium':  a = rand(20, 99); b = rand(1, a); /* no borrow */; break;
    case '--hard':    a = rand(20, 99); b = rand(1, a);   break;          // with borrow

    case '×-easy':    a = pick([2, 5, 10]); b = rand(1, 5);  break;
    case '×-medium':  a = rand(2, 5);   b = rand(1, 10);     break;
    case '×-hard':    a = rand(2, 10);  b = rand(1, 10);     break;

    case '÷-easy':    b = pick([2, 5]); a = b * rand(1, 5);  break;       // exact division
    case '÷-medium':  b = rand(2, 5);   a = b * rand(1, 10); break;
    case '÷-hard':    b = rand(2, 10);  a = b * rand(1, 10); break;
  }

  const answer = compute(a, op, b);
  const key = `${op}-${Math.min(a,b)}-${Math.max(a,b)}`;
  if (sessionHistory.has(key) && sessionHistory.size < 80) {
    return generateQuestion(op, diff, sessionHistory);  // retry once
  }
  sessionHistory.add(key);

  const distractors = generateDistractors(answer, op, a, b);
  const choices = shuffle([answer, ...distractors]);
  return { text: `${a} ${op} ${b}`, answer, choices };
}
```

Distractors: `answer ± 1`, `answer ± rand(2,5)`, operand-reversal result (e.g. for `7×4=28`, distractor could be `28/2=14` or `4×4=16`). Guarantee all > 0 and unique.

---

## 9. AI opponent logic

```ts
// src/math/ai.ts
type AIDifficulty = 'easy' | 'medium' | 'hard';

interface AIBehavior {
  reactionTimeMs: () => number;    // jittered delay before answering
  accuracy: number;                // probability of picking correct (0-1)
}

const AI: Record<AIDifficulty, AIBehavior> = {
  easy:   { reactionTimeMs: () => rand(2500, 4500), accuracy: 0.65 },
  medium: { reactionTimeMs: () => rand(1500, 2800), accuracy: 0.85 },
  hard:   { reactionTimeMs: () => rand(800, 1600),  accuracy: 0.95 },
};
```

On each new question, schedule the AI's response: pick correct answer with probability `accuracy`, else pick a random distractor. Submit after `reactionTimeMs()` elapses, unless the human player has already answered.

In Easy mode, **always give the human kid a head start** — guaranteed 1s delay minimum before AI's first answer per match.

---

## 10. Hot-seat 2P input on phone — UX critical

Both kids share the same touchscreen. Hand the phone horizontally between two kids facing each other (or sitting side by side). Each kid taps THEIR side's MCQ buttons.

Implementation:
- Each player's button cluster uses `pointer-events: auto` within their bounding zone
- No global touch handler — each `<AnswerButton>` has its own `onClick` / `onPointerDown`
- Multiple simultaneous touches OK — browsers handle multi-touch natively. No conflict between P1 left-side tap and P2 right-side tap
- Add `touch-action: manipulation` on buttons (disable double-tap zoom)
- Add `touch-action: none` on game canvas (disable scroll/zoom while playing)
- Set viewport: `<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">`

---

## 11. UX flow

```
HOME
├── [👫 Play with Friend]  →  SETUP (2P) → COUNTDOWN → MATCH → RESULTS
├── [🤖 Play vs Robot]      →  SETUP (AI) → COUNTDOWN → MATCH → RESULTS
└── [⚙️ Settings]            →  Mute toggle, dark mode

SETUP screen:
  [+] [−] [×] [÷]                ← topic row (big icon buttons)
  [Easy] [Medium] [Hard]         ← difficulty row
  (if AI mode also:) [AI Easy] [AI Medium] [AI Hard]
  [▶ START!]

COUNTDOWN: full-screen "3 → 2 → 1 → GO!" with character entrance animation + cheer sound.

MATCH: game runs. Pause button (top center) optional V1 (skip if scope tight).

RESULTS:
  Winner character does victory dance (jump, arms up, confetti)
  Loser character waves friendly (NOT crying — Carol Dweck growth-mindset framing)
  "🐯 Tiger wins!" or "🐘 Elephant wins!"
  Stats: "You got 8 right / 2 wrong" per player
  [▶ Play Again]   [↻ Change Settings]   [🏠 Home]
```

Onboarding: First-launch only — 5-second animated demo (ghost finger tapping, rope moving). No text. Reset on `localStorage.firstLaunch = false` after first match.

---

## 12. Accessibility (WCAG 2.2 AA)

- Color contrast 4.5:1 minimum on all text
- Tap targets 60×60px min for ages 6-8 (our 140×80px far exceeds)
- `prefers-reduced-motion` respected (skip particles + shakes)
- Colorblind safety: never use color alone — pair with shape/sound/icon. Correct = green + ✓ + chime. Wrong = orange + shake + boop.
- No flashing > 3Hz
- Focus rings for keyboard users (3px solid high-contrast)
- `aria-label` on icon-only buttons (mute, home, settings)
- Skip read-aloud for V1 (V2: Web Speech API on question)

---

## 13. Performance targets

- Lighthouse Performance ≥ 70
- LCP < 2.5s on mid-tier Android (Snapdragon 4 Gen 1, Redmi 9 class)
- INP < 200ms on button taps
- CLS < 0.1 (reserve canvas dimensions with explicit `aspect-ratio`)
- Game FPS: 60fps target, 30fps acceptable floor
- Total JS bundle < 500KB gzipped (Phaser 4 alone ~110KB gz)
- Audio sprite < 200KB

---

## 14. Acceptance criteria (Phase 4 will verify)

V1 ships when ALL of:
- [ ] `npm install && npm run dev` succeeds from clean clone, opens at localhost on default port
- [ ] Home screen renders correctly with 2 mode buttons + settings icon
- [ ] Setup screen lets you pick operation + difficulty + (for AI) AI difficulty, then START
- [ ] Countdown plays 3→2→1→GO with sound + character entrance
- [ ] Match screen: question visible, both players' button grids mirrored, tug-of-war animation responds to correct/wrong answers
- [ ] Correct answer: green flash on button + chime + character pulls + opponent's character moves → rope shifts → +1 step toward winner's line
- [ ] Wrong answer: orange flash + soft boop + your character moves back -0.5 step
- [ ] First player to push rope past opponent's finish line wins
- [ ] Results screen shows winner + per-player stats + Play Again works
- [ ] AI mode: AI answers within difficulty-appropriate window, with calibrated accuracy
- [ ] All 4 operations (+, −, ×, ÷) generate valid CBSE-appropriate questions per difficulty
- [ ] No duplicate questions within a session (until ≥ 80 unique used)
- [ ] Phone landscape (640×360) layout works without overflow
- [ ] Tablet + desktop layouts work
- [ ] Portrait phone shows "rotate to landscape" overlay for 2P mode
- [ ] Mute toggle works, persists across reloads via `localStorage`
- [ ] `prefers-reduced-motion` skips screen shake + particles
- [ ] Lighthouse Performance ≥ 70
- [ ] No console errors in Chrome DevTools during full play loop
- [ ] README.md has run + build + deploy instructions
- [ ] Clean `git init` + first commit "Initial V1: kids-math-tug" (NO PUSH — Boss will set up remote)

---

## 15. Out of scope for V1 (DO NOT BUILD)

- ❌ Rive characters (use simple SVG cartoon tigers/elephants for V1 — fine to be a single static SVG with Framer Motion transforms)
- ❌ PWA installability (manifest + service worker — V2)
- ❌ Web Speech API read-aloud
- ❌ Hindi/English language toggle
- ❌ Character unlocks / unlock progression
- ❌ Persistent badges / achievements / stats history
- ❌ Online multiplayer
- ❌ Settings screen beyond mute toggle
- ❌ Background music
- ❌ Login / accounts / user profiles
- ❌ Analytics / telemetry
- ❌ Cloudflare Pages deploy (Boss will do this himself once V1 verified)

---

## 16. Notes on scope discipline

The research surface is vast — design system alone could fill a sprint. **V1 must be playable end-to-end in one builder pass.** Better to ship a clean MVP than a half-built ambitious thing. Specifically:

- For SVG characters: a single SVG file per animal is fine. Animate via Framer Motion transforms (rotate for lean, translateX for step, scale for breathe). Don't try to do per-limb rigged animation in V1.
- For rope: use a single SVG path with one cubic bezier control point. Move the control point's Y based on pull direction for a "sag toward winner" visual.
- For sound: 6 SFX files, downloaded once during build, served from `/public/sounds/`. Don't get fancy.
- For UI: Tailwind utility classes directly, no shadcn/ui (game UI is custom — kids buttons don't fit shadcn's adult patterns). Component primitives only where genuinely shared.
- Tests: skip unit/integration tests in V1. Boss will do manual smoke test in Phase 4. If time permits, add ONE Playwright test for "full match playthrough" — but don't block on it.

---

## 17. Open questions handed to builder (USE YOUR JUDGMENT)

- Pause button in MATCH screen — include if trivial, skip if it complicates state machine
- Character pose count: minimum 3 states (idle, pulling, won/lost). More is bonus.
- Particle library: use `@tsparticles/confetti` for results screen confetti; for in-button correct-answer burst, your call (could be CSS-only sparkles for V1 simplicity)
- Question display: show in tug-of-war zone (top) OR in a dedicated strip above buttons? Pick what looks better in your layout.
- Default theme: light mode. Dark mode toggle in Settings if cheap, skip otherwise.

---

**Builder agent: read both research files** (`tech-stack-research.md` + `design-mechanics-research.md` in the same directory) **before writing any code.** They have specifics this brief abbreviates.

**Verification anchor:** when you're done, the game must pass the acceptance checklist (§14) end-to-end on a fresh `npm install`. If you can't get one of the checkboxes done, flag it explicitly in your reply — don't claim success.
