# Research Brief: Kids Math Tug-of-War Web Game
**Date:** 2026-05-17
**Purpose:** Phase 1 research for Jarvis build workflow — output feeds frontend-engineer-agent + ui-ux-designer-agent
**Product:** 2-player educational math tug-of-war web game, ages 6-8, India/Android-first

---

## 1. TECH STACK — Winning 2026 Patterns for Browser Kids' Games

### Phaser 4 (v4.1.0, released 2026-04-30)

- **What it is:** A complete 2D browser game framework. The biggest release in Phaser history — ground-up rebuild of the WebGL renderer. Stable npm package as of April 2026.
- **Bundle size:** ~345 KB minified + gzipped (full build). Can be trimmed via custom builds. Phaser Compact Texture (PCT) atlas format is 90–95% smaller than equivalent JSON atlases.
- **What it does well:** Complete game batteries — built-in physics (Arcade and Matter.js), scene management, input handling, tweens, cameras, audio, spritesheet animation, scale manager with full-screen support. SpriteGPULayer allows 1 million sprites in a single draw call. TilemapGPULayer has fixed rendering cost per pixel. Unified Filter system (replaces separate FX + Mask).
- **What it can't do:** Not React-friendly without wrappers (you mount Phaser into a `<div>`, your React UI lives outside). Not a good choice if you want JSX-driven UI and game in the same render tree.
- **Mobile performance:** Built-in scale manager, touch input handling, cross-platform deployment (desktop, mobile, Steam, Discord, YouTube Playables). Context restoration supported out-of-the-box.
- **Learning curve:** Medium. Rich docs, large community. Migration from Phaser 3 → 4 is "a few hours of work" per official docs.
- **Real examples:** Math Playground (Tug Team Multiplication), ICT Games (Tug of War). Thousands of commercial and educational HTML5 games.
- **For our game:** **Strong YES.** Phaser 4 handles the tug-of-war game canvas (rope animation, character sprites, tweens, physics), scene transitions (menu → game → results), and touch input — all out-of-the-box. The MCQ UI can be plain HTML/CSS absolutely positioned over the canvas, or React UI mounted separately.

### Phaser 3 (v3.90.0 "Tsugumi", May 2026 — still maintained)

- **What it is:** The previous stable, still receiving bugfixes in parallel.
- **Bundle size:** Same ~345 KB gzipped.
- **For our game:** Use Phaser 4 instead. All new features land exclusively on v4. Phaser 3 is legacy-path.

### PixiJS v8 (v8.16.0, released February 2026)

- **What it is:** High-performance 2D WebGL rendering engine. NOT a game framework — a rendering library.
- **Bundle size:** ~450 KB (actually larger than Phaser in some builds [unverified]). Rendering-only.
- **What it does well:** Fastest pure 2D WebGL renderer available. WebGPU support built-in (future-proof). Experimental Canvas renderer (v8.16.0) for environments without WebGL/WebGPU. 100K+ particles at 60fps. SplitText, tagged text.
- **What it can't do:** No game systems at all — no physics, no scene management, no audio, no input system, no collision, no tweens. You'd build all of these from scratch. 
- **Mobile:** High-DPI support, touch events, hardware acceleration. Good baseline.
- **For our game:** **No, unless you want to write your own game engine.** PixiJS is the renderer layer under Phaser anyway. For our game with scenes, animations, and audio — use Phaser 4. Use PixiJS only if you need pixel-perfect custom rendering with maximum control and are willing to build all game logic yourself.

### Three.js / React Three Fiber (R3F) v9

- **What it is:** 3D WebGL engine. R3F is the React wrapper.
- **Bundle size:** Three.js core ~600 KB+. With R3F and typical extras (Drei, postprocessing), 800 KB–1.2 MB.
- **What it does well:** 3D scenes, WebGL shaders, particle systems, cinematic camera work. Used for Awwwards-tier marketing sites and immersive experiences.
- **What it can't do:** Overkill for a 2D tug-of-war with cartoon animals. No built-in 2D game primitives. Physics requires @react-three/rapier or cannon.js add-ons.
- **For our game:** **No.** Our tug-of-war animation is 2D — two cartoon animals, a rope, horizontal movement. Three.js would add massive bundle weight and complexity for zero visual gain. Skip unless Boss explicitly wants a 3D isometric style.

### HTML5 Canvas Raw + Vanilla JS

- **What it is:** Browser native canvas API, no dependencies.
- **Bundle size:** 0 KB framework overhead.
- **What it does well:** Minimal bundle, full control, fast on any device. Ideal for ultra-simple games.
- **What it can't do:** You hand-code every animation, physics, input, and scene. No spritesheet management, no tween system, no audio API wrapping.
- **For our game:** **Fallback only.** Acceptable if bundle size is critical constraint (e.g. targeting 2G users with very slow first load). Too much manual work for a 2026-tier output. Phaser 4 is the right abstraction.

### SVG + Framer Motion 12 (inside React)

- **What it is:** Declarative animation library for React + SVG-based game objects.
- **What it does well:** Spring physics, exit/enter animations, layout animations. Excellent for UI transitions, menu flips, button states. Performant for moderate complexity.
- **What it can't do:** Not designed for game loops. No collision, no scene management. SVG becomes slow at many simultaneous animated elements (DOM manipulation overhead). Not suitable as the core game engine.
- **For our game:** **Yes, but only for UI layer.** Framer Motion 12 is excellent for the MCQ button press states, the menu screen transitions, the results screen reveal, the character selection screen. Do NOT use it for the tug-of-war animation itself — use Phaser 4 for that.

### React 19 + Tailwind 4 + shadcn/ui as UI Shell

- **What it is:** React 19 (RSC, Actions, useOptimistic), Tailwind 4 utility CSS, shadcn/ui unstyled components.
- **For our game:** **Yes, for the non-canvas UI.** The MCQ answer buttons, the score display, the topic/difficulty selector, the character unlock gallery — all can be React + Tailwind 4 mounted over or around the Phaser canvas. This hybrid pattern (Phaser canvas + React UI shell) is well-established.

### Vite + React vs Next.js 15

- **Vite recommendation:** **Use Vite + React for this game.** Reasons:
  - Game is a pure client-side SPA. No SEO needed. No SSR needed.
  - Vite builds static assets (HTML/CSS/JS dist/) deployable to Cloudflare Pages, Netlify, or any CDN for free.
  - Cold start <2s, millisecond HMR — fastest dev experience.
  - State of JS 2024: Vite #1 build tool, 95% developer satisfaction.
  - Next.js App Router adds RSC overhead, server routing complexity, and Vercel lock-in with zero benefit for a game.
- **Hosting:** Cloudflare Pages (free tier, global CDN, fast in India) or Netlify. `vite build` → `dist/` → deploy.

---

### PRIMARY STACK RECOMMENDATION

```
Phaser 4.1.0                 — game canvas, physics, animation, audio
React 19 + Vite 6            — app shell, UI components, routing
Tailwind 4                   — UI styling (buttons, menus, score display)
Framer Motion 12             — menu/results screen transitions, button juice
Rive (@rive-app/react-canvas) — cartoon animal character animation
Howler.js 2.x                — cross-browser sound effects + music
@tsparticles/confetti        — correct-answer particle burst
Matter.js (via Phaser)       — optional rope segment physics if needed
```

**Fallback (simpler, faster to build):**
```
Phaser 4.1.0                 — everything (canvas, UI text objects, audio)
Spritesheet PNG              — instead of Rive, for characters
Phaser.Sound                 — instead of Howler.js
```

---

## 2. SIMILAR GAMES — Does This Exact Concept Exist?

**Closest matches found:**

### 1. Tug of Math — tugofmath.app
- **URL:** https://tugofmath.app/en
- **What it does:** Two teams on opposite sides of a shared whiteboard screen. Both teams see the SAME math question simultaneously. Correct answers pull the rope toward that team. Multi-touch supported so both teams tap simultaneously. No accounts, no download. Works on SMART Board, Promethean ActivPanel, tablets.
- **Operations:** +, -, ×, ÷, mixed. Easy/Medium/Hard.
- **What they do well:** Classroom-first UX (big buttons visible from back of room), simultaneous multi-touch, instant setup (30 seconds to launch).
- **What they miss:** Designed for classroom projectors, not phone hot-seat. No character/animal animation — it's just a rope and a flag. No individual answer buttons mirrored per player. No sound design. No AI opponent mode. No character unlocks. No phone landscape mode. Template-tier visuals.
- **Gap vs our game:** Our game adds cartoon animal animations (tiger vs elephant), individual mirrored MCQ buttons, phone-native design, AI opponent, sound feedback, character unlock system, and India-facing content.

### 2. EZCalculatorOnline Tug of War — ezcalculatoronline.com/tug-of-war/
- **URL:** https://www.ezcalculatoronline.com/tug-of-war/
- **What it does:** Split-screen 1v1, same device. Both players see the same math problem simultaneously. Correct answer moves yellow flag/rope. Wrong answer triggers 2-second penalty (screen grays out). Custom avatar (selfie/photo upload or robot/demon character). Operations: +, -, ×, ÷. Duration: Short/Standard/Marathon.
- **What they do well:** Same-question race mechanic (closest to our concept). Penalty system for wrong answers. Avatar customization. Free, no account.
- **What they miss:** No cartoon animal characters, no tug-of-war character animation (just a flag on a line), no sound design, no AI mode, no difficulty levels, no character unlocks, no India-focused math alignment, no PWA/installability, UI is functional but not premium. Visual quality is 2020-era.
- **Gap:** Our tiger vs elephant animated characters + full audio + difficulty levels + unlockable characters + AI opponent elevates this significantly.

### 3. Math Duel — App Store / Google Play (peaksel.com)
- **URL:** https://apps.apple.com/us/app/math-duel-2-player-kids-games/id1060040925 and https://play.google.com/store/apps/details?id=com.mathduel2playersgame.mathgame
- **What it does:** Split-screen mobile app (landscape). Two players on same device. Each player gets MCQ buttons on their half of screen. Adjustable difficulty per player independently. Power-ups (freeze opponent's screen, head start, skip equation). 4.x star rating.
- **What they do well:** Per-player difficulty adjustment, power-up system, polished native app.
- **What they miss:** Native app (not web). No tug-of-war visual — it's abstract score-based. No cartoon character animation, no progressive visual feedback of rope pulling. Not browser-installable.
- **Gap:** Our web-based (no install required), tug-of-war visual narrative, cartoon animals make it more immersive and immediately shareable.

### 4. MathTug — mathtug.com
- **URL:** https://mathtug.com/en/
- **What it does:** Multiplayer math game (classroom-focused, real-time competition). Browser-based, large display designed.
- **What they do well:** Team-based competitive urgency, responsive design.
- **What they miss:** Again, classroom-first not phone-first. No individual MCQ buttons per player on mobile. No animal characters. No sound.
- **Gap:** Phone-native design, character animations, AI opponent mode.

### 5. Math Playground Tug Team (Multiplication/Addition) — mathplayground.com
- **URL:** https://www.mathplayground.com/ASB_TugTeamMultiplication.html and https://www.mathplayground.com/ASB_TugTeamAddition.html
- **What it does:** Tractor-pull themed tug game, up to 8 players, matching multiplication expressions to correct products. Common Core aligned (Grade 3+).
- **What they do well:** Established educational pedigree, fun tractor theme, multi-player.
- **What they miss:** Not 2-player hot-seat race with SAME question. Multiplication-only (our game covers +/-/×/÷). No animated character narrative.
- **Gap:** Our simultaneous same-question race + character animation + India-facing operations (CBSE) is meaningfully different.

### 6. Toy Theater Addition Pull — toytheater.com/addition-pull/
- **URL:** https://toytheater.com/addition-pull/
- **What it does:** Single-player against AI, tap correct answer, opponent pulls you toward water.
- **What they do well:** Simple, clean, age-appropriate, cute single-player narrative.
- **What they miss:** No 2-player hot-seat mode. No character animation. Simple visual.
- **Gap:** Our 2-player mode and AI opponent cover both.

### 7. ICT Games Tug of War — ictgames.com
- **URL:** https://ictgames.com/mobilePage/tugofwar/index.html
- **What it does:** Multiplication/division focus for ages 5-10. UK primary school staple.
- **What they do well:** Trusted by UK schools, mobile-page version exists.
- **What they miss:** Keyboard-based input (enter answer before opponent), not MCQ tap. No visual character animation. Dated UI.

**Critical Question — Does the EXACT same-question-race-to-answer + tug-of-war + cartoon animal combo exist?**

**No.** EZCalculatorOnline is the closest (same question, both players race, rope moves) but has zero cartoon animal animation, no sound, no AI, and minimal visual quality. Tugofmath.app has the classroom-facing mechanic but no phone-hot-seat design. **The combination of: (a) same question displayed to both simultaneously, (b) mirrored MCQ buttons per player, (c) animated cartoon animal characters that physically pull a rope, (d) phone-native landscape design, (e) AI opponent mode, (f) CBSE-aligned content — does not exist in any current web game.** The gap is real and meaningful.

---

## 3. KIDS WEB GAMES — 2026 SOTA Examples (Named, With URLs)

### 1. Prodigy Math — play.prodigygame.com
- **URL:** https://play.prodigygame.com/
- **What makes it premium:** Full RPG narrative overlay — kids answer math to cast spells in battles. WebGL rendering confirmed (WebGL is now Prodigy's ONLY rendering path as of 2026). Character customization, pet system, world exploration. The math is invisible inside the game narrative.
- **Design language:** Vibrant anime-adjacent character art. Warm fantasy palette. Sound-rich (music, SFX on every interaction). Smooth scene transitions.
- **Tech stack:** WebGL-based (confirmed), React shell [unverified based on browser behavior], proprietary engine.
- **Lesson for our game:** Wrap math in a compelling visual narrative. The tug-of-war IS the narrative — lean into the animal character personalities.

### 2. Khan Academy Kids — khanacademy.org/kids
- **URL:** https://www.khanacademy.org/kids
- **What makes it premium:** Hand-drawn character style (Kodi the bear), consistent warm color palette, age-appropriate audio narration on every element, no reading required for youngest users. Very deliberate motion — nothing moves unless it teaches something.
- **Design language:** Warm oranges/yellows, rounded corners on everything, hand-drawn-adjacent art style. Big tap targets (44px+ minimum). Celebration animations on correct answers.
- **Tech stack:** React Native on mobile, React web version [unverified]. 
- **Lesson:** Every interaction gets audio feedback. Big clear targets. Characters have personality.

### 3. Starfall — starfall.com
- **URL:** https://www.starfall.com/h/
- **What makes it premium:** Long-established (K-5), phonics-to-chapter-books progression. Audio-narrated everything. Consistent visual style across 20+ years.
- **Design language:** Primary colors, large fonts, simple illustrations.
- **Tech stack:** Flash-to-HTML5 converted, uses canvas extensively. [unverified framework]
- **Lesson:** Audio narration on every element is non-negotiable for 6-8 age group.

### 4. ABCya — abcya.com
- **URL:** https://www.abcya.com/
- **What makes it premium:** Hundreds of games, grade-level filtering, used by millions of US elementary classrooms. Fast load times, all browser-based.
- **Design language:** Colorful, bubbly UI. Grade-band color coding. Big rounded buttons.
- **Tech stack:** HTML5 Canvas + JavaScript. Mix of Flash-era games and newer HTML5 builds.
- **Lesson for our game:** Instant play without signup is critical. Our game must work with zero account creation.

### 5. Math Playground — mathplayground.com
- **URL:** https://www.mathplayground.com/
- **What makes it premium:** Consistently high-quality HTML5 games, cross-device, used widely in US schools. Game categories clearly organized by grade level. Fast, no-lag performance.
- **Design language:** Clean, uncluttered. Game-specific art per title (not one template). Sound on by default.
- **Tech stack:** HTML5 Canvas (confirmed via View Source on multiple games). Some games use CreateJS.
- **Lesson:** Game-specific art, not a template. Each game has its own visual identity.

### 6. Coolmath Games — coolmathgames.com
- **URL:** https://www.coolmathgames.com/
- **What makes it premium:** Massive catalog, fast load, works on Chromebooks (school-grade compliance). Strong SEO, kids find it organically.
- **Design language:** Clean UI shell with game-specific art. Search and category navigation. Ad-tolerant layout.
- **Tech stack:** Mix — older Flash-converted and newer HTML5 Canvas builds.

### 7. Funexpected Math — funexpectedapps.com
- **URL:** https://funexpectedapps.com/
- **What makes it premium:** Premium visual quality (hand-illustrated characters, sticker-style), subscription model justifies design investment, aligned to curricula worldwide. Age-adaptive difficulty.
- **Lesson:** Sticker/hand-illustrated visual style reads as "premium" for parents, "fun" for kids.

---

## 4. DESIGN LANGUAGE for Ages 6-8 (2026)

### Color Palettes

- **Winning formula (2026):** Vivid primary + warm secondary. Not pastel (too babyish for 6-8). Not desaturated (reads as "adult"). Target: HSL saturation 70-90%, lightness 50-65% for main colors.
- **Specific palettes that work:**
  - **Warm game palette:** Sunshine yellow (`#FFD93D`), Sky blue (`#4ECDC4`), Coral red (`#FF6B6B`), Leaf green (`#6BCB77`), Deep purple accent (`#7B2FBE`)
  - **India-resonant palette:** Saffron (`#FF9933`), Peacock teal (`#1B9E8A`), Festival pink (`#E91E8C`), Cream white (`#FFF8E7`) — these read culturally warm and festive, appropriate for Indian families
- **Background:** Avoid pure white (harsh) and pure black. Use `#FFFDF4` (warm off-white) or `#1A1A2E` (deep navy) for night-mode option.
- **Button contrast:** WCAG 2.2 AA requires 4.5:1 ratio for text on buttons. With vivid colored buttons, use dark text (`#1A1A1A`) not white for yellows/greens; use white for deep blues/purples.
- **Player-side color coding:** Player 1 = Red/Warm, Player 2 = Blue/Cool. Standard in competitive games, immediately intuitive.

### Typography

- **Primary recommendation (2026):** **Fredoka** (Google Fonts, variable font, Light–Bold range). Thick, bubbly strokes, cheerful personality, high legibility at game-resolution sizes. Works perfectly for scores, question numbers, character names. Available as variable font so one file covers all weights.
- **Body/question text:** **Nunito** (Google Fonts) — rounded terminals, high legibility even for emerging readers. Very friendly.
- **Pairing:** Fredoka (headings, score, title) + Nunito (questions, answer buttons, instructions).
- **Avoid:** Comic Sans (ironic association, low legibility). Poppins is fine for adults but slightly cold for 6-8. Quicksand is acceptable but thinner than Fredoka.
- **Size rules:** Question text minimum 24px on phone. Answer buttons minimum 32px. Score minimum 28px. Never below 18px for any game content.

### Iconography Style (2026)

- **Trending and age-appropriate:** Sticker-style or bold flat 2D illustration (NOT isometric for this age). Think: thick outlines (2-4px stroke), vibrant fills, simple shadow. Similar to emoji but higher quality.
- **Character style:** Rounded body proportions (big head, chubby limbs) — this is universally read as "kid-friendly" across cultures. Tiger with big eyes, elephant with floppy ears.
- **Anti-pattern:** Thin-line icon sets (e.g. Heroicons, Feather Icons) — too cold, adult-feeling. Material icons without customization.

### Motion Language (2026)

- **Squash and stretch** on every interactive element: buttons squash on press, character squash on landing, correct answer stretches up before settling.
- **Anticipation + follow-through** on rope pulls: brief pause at start of pull, overshoot past target, settle back.
- **Spring easing** not linear: CSS `spring(1 100 10 0)` or Framer Motion `type: "spring", stiffness: 300, damping: 20` for all interactive feedback.
- **Particle burst** on correct answer: confetti from answer button, spreading outward 0.4s.
- **Screen shake** on wrong answer: 0.2s horizontal oscillation, 3-4 cycles, low amplitude (±6px).
- **Character idle animation**: subtle breathing bob (scale 1.0 → 1.03 → 1.0, 2s loop) so they feel alive between pulls.
- **Rope:** Segments curve with catenary approximation, snaps taut on pull.

### Sound Design (2026 Standard)

- **Library: Howler.js 2.x** — 7 KB gzipped, handles WebAudio + HTML5 fallback, audio sprites, format fallbacks (OGG + MP3). Best-in-class for game SFX.
- **Sound for correct answer:** Short (0.3s), rising pitch, major-key tone. NOT a bell (overused). Think: cartoon "pow" + sparkle shimmer.
- **Sound for wrong answer:** Short (0.2s), descending "bloop" or "buzz". NOT harsh/grating. Kids should feel mild correction, not punishment.
- **Victory fanfare:** 1.5-2s ascending melody, festive, culturally neutral (avoid western-only).
- **Rope pull SFX:** Stretchy "whoosh" with slight creak.
- **Background music:** Optional loop, 60-80 BPM, mute-able. Keep at -12dB relative to SFX so SFX cut through.
- **Mid-frequency focus:** Avoid very low bass (inaudible on phone speakers) and very high treble (harsh on cheap speakers). Target 400Hz–4kHz primary frequency range.
- **Audio unlock pattern (mobile):** Web Audio API requires user gesture to unlock. Standard pattern: play a silent 0.1s sound on first tap/touch event to unlock the AudioContext, then all subsequent sounds work. Howler.js handles this automatically via its `unlock` mechanism.
- **iOS warning:** On iOS, audio only plays inside a user-initiated event handler. If using autoplay for music, it will silently fail. Use Howler.js's `html5: true` flag as fallback for iOS. Test on Safari explicitly.

---

## 5. ANIMATION + INTERACTION PATTERNS

### Tug-of-War Rope Animation (Browser-Cheap Options)

**Option A: Phaser Rope Object (RECOMMENDED)**
Phaser 4 has a built-in `Rope` game object that renders a rope-like curve with deformable segments along a path. You define control points; Phaser renders the segmented mesh. Animating the control points with Phaser tweens gives a satisfying rope pull without external physics. Effort: medium. No extra physics engine needed.

**Option B: Matter.js Chain Constraint (via Phaser's built-in Matter.js integration)**
Create N rigid bodies (chain links) with pin constraints between them. Apply force to end bodies to simulate a tug. Renders with Phaser's graphics layer. More physically accurate but heavier CPU on low-end Android. Phaser 4 includes Matter.js natively — no extra install.

**Option C: Hand-animated SVG path (via `d` attribute interpolation)**
Define rope as an SVG `<path>` with cubic bezier control points. Animate control points with Framer Motion (when mounted in React SVG). Simple catenary approximation: `M x1,y Q midX,sag x2,y`. Move `sag` value based on pull progress. Zero physics overhead. Predictable. Excellent for low-end devices.
```
Recommended: Option A (Phaser Rope) for Phaser-primary stack. Option C (SVG) if game is built as React-only with no Phaser.
```

**Option D: CSS transform with clip-path**
Extremely lightweight — animate rope length with `scaleX` + `transform-origin`. The rope just stretches. No physics feel. Acceptable fallback for very low-end devices.

### Character Animation for Cartoon Animals

**Rive (`@rive-app/react-canvas` v2.x) — RECOMMENDED for characters**
- File sizes 5-10x smaller than Lottie. 60fps vs Lottie's 17fps in benchmarks. Interactive state machines respond to game events in real time.
- State machine setup: `idle` → `pulling` → `winning` → `losing`. Drive state from Phaser events via Rive's `useRive` hook.
- Yeti Confetti Kids and Duolingo both use Rive for character animation (confirmed).
- Ships with native WebGL renderer (`@rive-app/webgl2` for maximum perf).
- Workflow: Design in Rive's web tool → export `.riv` file → load via `@rive-app/react-canvas`.
- [unverified: exact API surface of current v2.x as of May 2026 — verify against rive.app/docs]

**Spritesheet PNG (fallback, simpler)**
- Pre-render character frames in Aseprite or Adobe Animate → export as PNG spritesheet → load with Phaser `anims.create()`.
- Simpler pipeline, no Rive tooling needed. Animation states limited to what's pre-rendered.
- Acceptable if Rive assets aren't available; lower visual ceiling.
- Free asset sources: craftpix.net, itch.io/game-assets, GraphicRiver.

**Lottie — do NOT use for characters**
- 17fps cap in performance benchmarks. 5-10x larger file sizes. No interactive state machine. Deprecated for character use in favor of Rive across the industry.

### Particle Effects on Correct Answer

**`@tsparticles/confetti` (v3.x) — RECOMMENDED**
- Plug-and-play confetti burst. React-ready. Works standalone on any element.
- Usage: `confetti({ particleCount: 80, spread: 70, origin: { x: 0.5, y: 0.6 } })` on correct answer event.
- Bundle: ~40 KB gzipped for confetti preset.
- Alternative: Phaser's built-in particles emitter (if staying fully in Phaser). Phaser 4 particles are GPU-accelerated.

**react-confetti (v6.x)**
- Full-screen confetti canvas overlay. Good for win screen. Not targeted-burst (always full screen). Simpler API than tsparticles.

### Button Feedback

- **Press state:** CSS `transform: scale(0.92)` with `transition: transform 0.08s ease`. Fast enough to feel instant.
- **Spring rebound:** On release, `transform: scale(1.06)` then settle to `scale(1.0)` with spring easing — Framer Motion `whileTap` + `whileHover` variants.
- **Haptic:** `navigator.vibrate(30)` on correct answer tap on Android (not supported on iOS). Keep ≤50ms. Wrap in try-catch — fails silently on iOS.
- **Ripple effect:** CSS radial-gradient from tap point, 0.3s expand + fade. Pure CSS, zero JS.
- **Wrong answer:** Button briefly flashes red (CSS `background: #FF4444` for 0.2s), screen shake (CSS `@keyframes shake` on parent container).

### Screen Shake

```css
@keyframes shake {
  0%, 100% { transform: translateX(0); }
  20% { transform: translateX(-6px); }
  40% { transform: translateX(6px); }
  60% { transform: translateX(-4px); }
  80% { transform: translateX(4px); }
}
```
Applied to `.game-screen` on wrong answer. Duration: 0.25s. Respect `prefers-reduced-motion` — skip shake if set.

---

## 6. MOBILE/PHONE RESPONSIVE CONCERNS

### Viewport and Touch Setup

```html
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
```

- `user-scalable=no` prevents pinch-zoom during gameplay (prevents accidental zoom on double-tap). Note: some accessibility guidelines advise against this — add an accessibility mode toggle for users who need zoom.
- `touch-action: none` on the game canvas element. `touch-action: manipulation` on buttons (allows tap, prevents double-tap zoom, allows scroll in button lists).

### Orientation Strategy

- **Phone (Android):** Force landscape via `screen.orientation.lock('landscape')` API. This is available on Android Chrome via PWA install context. Falls back gracefully to a "rotate your device" screen on non-PWA browser. Alternatively, use CSS: design for landscape viewport, show a rotate prompt if `window.innerWidth < window.innerHeight`.
- **Tablet/iPad (portrait):** Design for portrait naturally — the horizontal split works vertically (top player = Player 1 area, bottom player = Player 2 area). The tug-of-war rope runs vertically in portrait mode for tablets.
- **Desktop:** Both orientations acceptable. Game fills viewport with max-width constrained to `1280px`.

### Low-End Android Performance

- **Chipsets targeted:** Snapdragon 4 Gen 1/2 (budget), MediaTek Helio G88, Dimensity 700-series. Common in Indian market (₹8,000–₹15,000 phones).
- **FPS target:** 60fps on mid-range, 30fps acceptable on low-end. Do NOT run at uncapped framerate — cap at 60fps with `Phaser.AUTO` renderer and `fps: { target: 60, forceSetTimeOut: false }`.
- **Reduce GC pressure:** Pre-allocate object pools in Phaser for particles and tweens. Avoid creating new objects inside the game loop.
- **Texture budget:** Keep total texture memory under 32 MB. Use texture atlases (Phaser PCT format) to minimize draw calls. Avoid large uncompressed PNGs — compress with Squoosh or use WebP (Chrome Android supports WebP natively).
- **WebGL first, Canvas fallback:** Phaser 4 auto-detects. WebGL on 99% of Android phones; Canvas fallback for truly ancient devices.
- **Benchmark signal:** Target 60fps on a Redmi 9 or Samsung Galaxy A23 — common budget Indian Android devices.

### PWA Installability

- **Minimum requirements:** `manifest.json` with `name`, `short_name`, `icons` (192px + 512px PNG), `display: "fullscreen"`, `orientation: "landscape"`, `background_color`, `theme_color`. Plus a registered Service Worker that handles at least a basic `fetch` event.
- **Install prompt UX:** Listen for `beforeinstallprompt`, defer it, show a custom "Play offline! Tap to install" banner after the user plays one round (not on first load). This is the highest-converting trigger.
- **Offline:** Cache game assets (JS bundle, PNG atlases, audio files) via Service Worker Workbox 7.x. Game should work fully offline after first load — this is critical for Indian families on intermittent connections.
- **`display: "fullscreen"`** hides browser chrome completely — essential for immersive game experience on Android.

### Audio on Mobile Browsers

- **Autoplay policy:** All modern browsers block audio autoplay without user gesture. Standard pattern: on first tap anywhere on the game (start screen tap), call `howlerInstance.play('silent')` to unlock the AudioContext.
- **Howler.js handles this automatically** via its internal audio unlock mechanism. Set `Howl.volume(0)` for the unlock sound.
- **iOS Safari:** Requires audio to be called inside a synchronous event handler. Howler's `html5: true` flag uses `<audio>` elements as fallback, which have slightly better autoplay behavior on iOS.
- **Format support:** Provide both OGG (better quality, smaller) and MP3 (iOS fallback). Howler.js selects the best format automatically via `src: ['sound.ogg', 'sound.mp3']`.

---

## 7. CREATIVITY TROPES SIGNALING "2026-TIER" vs ANTI-PATTERNS

### 2026-Tier Moves (DO THESE)

1. **Rive state machines for character animation** — tiger/elephant breathe, react, and celebrate in real-time. Feels alive, not pre-recorded.
2. **View Transitions API for scene flips** (Chrome 126+, Safari 18.2+) — menu → game → results screen transitions animate as cross-fades or slides rather than hard-cut. One line: `document.startViewTransition(() => setScreen('game'))`. Supported in React 19 via `<ViewTransition>` component.
3. **Intentional load sequence** — while assets load, show an animated character doing something (elephant practicing math problems) with a progress bar disguised as a "warming up" mechanic. Not a spinner.
4. **Micro-feedback on every interaction** — every button press, every rope pull, every question transition gets its own animation beat. 2026 UX treats the interface as a living organism.
5. **Audio-visual lock** — correct answer SFX, particle burst, character pull animation, and rope move all fire simultaneously within the same animation frame. Tight sync makes the game feel premium.
6. **Character personality** — the losing character looks increasingly stressed (Rive state: neutral → worried → panicked). Winner looks increasingly confident. Pure storytelling through animation states.
7. **Custom "game feel" cursor** on desktop — paw print or cartoon hand cursor when hovering buttons.
8. **Offline-first PWA** — "Install to your phone, play offline" prompt after first game. 2026-tier for Indian families on intermittent internet.
9. **Haptic feedback on Android** — `navigator.vibrate([30])` on correct, `navigator.vibrate([50, 30, 50])` (double buzz) on wrong. Tactile confirmation makes answers feel real.
10. **Dark-mode aware palette** — `prefers-color-scheme: dark` switches to a deep-navy background with the same vivid character colors. More accessible at night (kids play in bed).

### Anti-Patterns (FORBIDDEN — these scream "2020/template/amateur")

1. **Bootstrap or Material UI with default styling** — immediately readable as a template. Use Tailwind 4 with custom design tokens instead.
2. **Comic Sans** — associated with clip-art era, low credibility with parents, lower legibility. Use Fredoka.
3. **Flat emoji-only icons** without custom illustration — ❌✅ as feedback icons look lazy. Use custom illustrated feedback animations.
4. **"Submit" button** — never. Buttons are "TAP!" or operation symbols or the character's name.
5. **No sound design** — a kids' math game with no audio in 2026 fails immediately in comparison tests.
6. **No animation feedback** — static correct/wrong answer (just color change) is 2015 behavior.
7. **Score as plain text counter** — animate score changes (number spin-up, brief scale pop).
8. **Linear easing on everything** — springs and bounces only for interactive elements.
9. **Unoptimized images** — uncompressed PNGs will kill performance on 4G/low-end Android. Use WebP + texture atlases.
10. **Landscape-only with no rotation prompt** — if user opens on portrait phone, game should show a polite "rotate to play" screen with an animated arrow, not a broken layout.
11. **No loading state** — game assets loading in silence with a white screen. Always show a branded load sequence.
12. **jQuery** — obsolete in 2026 React ecosystem. Zero reason to use it.
13. **1990s pixel art** (unless intentional retro brand) — our game targets ages 6-8 who expect contemporary cartoon style.

---

## 8. MATH QUESTION GENERATION

### CBSE/NCERT Alignment for Ages 6-8 (Classes 1-3)

Per CBSE syllabus 2025-26:
- **Class 1 (age 6):** Numbers 1-100, addition/subtraction within 20, basic shapes, patterns
- **Class 2 (age 7):** Numbers to 999, addition/subtraction with and without carrying within 99, introduction to multiplication (repeated addition, tables of 2 and 5)
- **Class 3 (age 8):** Numbers to 9999, addition/subtraction multi-digit, multiplication tables 2-10, division as sharing/grouping

### Algorithm Design by Difficulty and Operation

**Addition:**
- Easy: a + b where a,b ∈ [1,9], sum ≤ 18 (single digit, no carrying)
- Medium: a + b where a ∈ [10,50], b ∈ [1,9], no carrying (e.g. 23 + 5)
- Hard: a + b where a,b ∈ [10,50], carrying required (e.g. 27 + 16)

**Subtraction:**
- Easy: a - b where a ∈ [2,20], b < a, result ≥ 0 (e.g. 9 - 4)
- Medium: a - b where a ∈ [20,50], b ∈ [1,9], no borrowing
- Hard: a - b where a ∈ [20,99], borrowing required

**Multiplication:**
- Easy: a × b where a ∈ {2,5,10}, b ∈ [1,5] (tables of 2, 5, 10 to 5)
- Medium: a × b where a ∈ {2,3,4,5,10}, b ∈ [1,10]
- Hard: a × b where a,b ∈ [2,10] (full multiplication table)

**Division:**
- Easy: exact division, quotient ≤ 5, divisors 2 or 5 (e.g. 10 ÷ 2)
- Medium: exact division, quotient ≤ 10, divisors 2-5
- Hard: exact division with divisors 2-10, no remainders (keep it age-appropriate — remainders are Class 4+)

### Distractor Generation (Wrong Answer Choices)

For each correct answer `C`, generate 3 distractors:
- `C ± 1` (off-by-one error)
- `C ± random(2,5)` (plausible range)
- Swap operands result if different (e.g. for 8-3=5, a distractor is 3 as "reversal" error)
- Shuffle all 4 options. Never reveal position pattern.
- Validate: no two distractors are the same, no distractor equals the correct answer, all distractors > 0.

### Duplicate Avoidance

Use a session-level `Set<string>` keyed by `${op}_${a}_${b}` (canonical, with a ≤ b for commutative ops). Remove from pool once asked. Refill pool when pool < 5 questions remaining (reset pool but shuffle order to avoid repeats in adjacent rounds).

### Open Source References

- No specific authoritative open-source math content library found for Indian K-3 curriculum. Closest: Khan Academy's exercise framework (open source, but complex — overkill for this use case).
- Recommend: Build the generator in pure TypeScript, ~100 lines, zero dependencies. Simple is correct here.

```typescript
// Minimal example for addition generator
function generateAddition(difficulty: 'easy' | 'medium' | 'hard') {
  if (difficulty === 'easy') {
    const a = randInt(1, 9), b = randInt(1, Math.min(9, 18 - a));
    return { question: `${a} + ${b}`, answer: a + b };
  }
  // ... medium, hard variants
}
```

---

## 9. NAMED REFERENCE SITES — The Bar the Builder Must Match

These are the 5 live references the frontend-engineer-agent must study before writing code:

1. **EZCalculatorOnline Tug of War** — https://www.ezcalculatoronline.com/tug-of-war/
   Study: split-screen layout, flag/rope movement on correct answer, penalty mechanic, same-question-for-both layout. **Note:** This is the closest functional analog. Our game must be visually 3x superior.

2. **Tug of Math** — https://tugofmath.app/en
   Study: multi-touch simultaneous answer handling, classroom-scale button sizing, instant-launch UX. **Note:** Steal their "no account needed, 30-second setup" UX philosophy.

3. **Prodigy Math** — https://play.prodigygame.com/
   Study: how WebGL is used for game world, how math questions are integrated into narrative without breaking immersion, character animation quality, sound design density, celebration sequences.

4. **Math Playground Tug Team Multiplication** — https://www.mathplayground.com/ASB_TugTeamMultiplication.html
   Study: overall game polish expected for this genre, how tug-of-war visual progress works in a more established game, topic-locking mechanic.

5. **Khan Academy Kids** — https://www.khanacademy.org/kids
   Study: character-driven UX, big tap targets, audio-on-everything, warm color palette, how to feel premium without being complex. Match this level of audio feedback density.

6. **Toy Theater Addition Pull** — https://toytheater.com/addition-pull/
   Study: single-player vs AI opponent mechanic, simple-but-effective visual narrative.

---

## 10. PERFORMANCE + A11Y BENCHMARKS

### Lighthouse Targets for a Game Web App

Games are a special case for Lighthouse — the initial load is what Lighthouse measures, not the running game. Reasonable targets:

| Metric | Target | Notes |
|--------|--------|-------|
| **Performance score** | ≥ 70 (load), n/a (game running) | Game loop FPS is not measured by Lighthouse |
| **LCP** | < 2.5s | Main loading screen image/animation should LCP fast |
| **INP** | < 200ms | Button responses in React UI must be fast; game engine inputs handled by Phaser outside React |
| **CLS** | < 0.1 | Reserve space for game canvas with explicit dimensions to avoid layout shift |
| **FPS (game running)** | 60fps mid-range, ≥ 30fps low-end | Use `requestAnimationFrame` timing, throttle to 60fps |
| **PWA score** | 100 | Manifest + SW + HTTPS + installability |

### Core Web Vitals Notes for Games

- **LCP:** Your splash screen or loading animation is the LCP element. Pre-size it with `width`/`height` attributes. Use `loading="eager"` and `fetchpriority="high"`.
- **INP:** React button handlers (MCQ taps) must be ≤ 200ms total including paint. Don't run expensive math generation synchronously on tap — precompute the next 3 questions on a worker or idle callback.
- **CLS:** Reserve canvas dimensions explicitly in CSS (e.g. `aspect-ratio: 16/9` + `width: 100%`). Don't dynamically inject the canvas — it should always be in the DOM.

### WCAG 2.2 AA Considerations for Kids' Games

- **Color contrast:** All text on buttons must meet 4.5:1 ratio. With Fredoka on colored buttons, verify each combo in the palette. The question text on the game background must meet 4.5:1.
- **Tap target size:** WCAG 2.5.5 (AA) requires 44×44px minimum. For kids 6-8, go bigger: **60×60px minimum** for answer buttons. Kids have less precise tap accuracy.
- **Motion:** Implement `prefers-reduced-motion` check:
  ```css
  @media (prefers-reduced-motion: reduce) {
    * { animation-duration: 0.01ms !important; transition-duration: 0.01ms !important; }
  }
  ```
  In practice, skip the screen shake, confetti, and rope bounce when this is set. Show a simple ✓ or ✗ indicator instead. Game still works.
- **Audio captions/visual equivalents:** Every audio cue (correct, wrong, win) must have a simultaneous visual cue (color flash, icon). Never audio-only feedback for primary game events.
- **No flashing:** Avoid any animation >3 flashes/second (triggers photosensitive epilepsy). Correct answer confetti should be particle-based (not flash/strobe). Wrong answer screen shake should use transform not flashing colors.
- **Pause functionality:** Provide a pause button (even in 2-player mode). WCAG gaming guideline: long-running motion/animation must be pauseable.
- **Font size zoom:** Even with `user-scalable=no` for gameplay, the settings/accessibility screens should honor OS font size preferences. Consider `rem` units for non-game UI.

### Reduced-Motion Implementation Strategy for This Game

```javascript
const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

// Pass as prop to Phaser scene config
scene.start('GameScene', { reducedMotion: prefersReducedMotion });

// In game scene: skip tweens, show instant state change
if (!reducedMotion) {
  this.tweens.add({ targets: rope, x: newX, duration: 400, ease: 'Back.easeOut' });
} else {
  rope.x = newX; // instant
}
```

---

## Summary: Recommended Stack (Final)

```
Game engine:     Phaser 4.1.0
App shell:       React 19 + Vite 6.x
Styling:         Tailwind 4
UI animations:   Framer Motion 12 (menus, results screen)
Characters:      Rive v2.x (@rive-app/react-canvas)
Scene transitions: View Transitions API (Chrome 126+/Safari 18.2+)
Sound:           Howler.js 2.2.x
Particles:       @tsparticles/confetti OR Phaser 4 built-in particles
Math generator:  Custom TypeScript, ~100 lines, zero deps
PWA:             Workbox 7.x + manifest.json
Hosting:         Cloudflare Pages (free, global CDN, fast India latency)
Fonts:           Fredoka (variable) + Nunito — both Google Fonts
Asset format:    WebP textures + Phaser PCT atlas + OGG/MP3 audio
```

**Why this beats template tier:**
- Rive characters feel alive (not spritesheet-stiff)
- Howler.js gives tight audio-visual lock
- View Transitions API makes screen changes feel native
- PWA + offline means installable without Play Store (critical for India low-storage users)
- Tailwind 4 + Fredoka + custom palette vs any Bootstrap/MUI default = instantly recognizable as custom-built

---

## Sources

- [Phaser 3 vs Phaser 4 — Official Comparison](https://phaser.io/news/2026/05/phaser-3-vs-phaser-4)
- [Phaser 4.1.0 Download](https://phaser.io/download/release/v4.1.0)
- [Phaser 4 Renderer Article](https://phaser.io/news/2026/04/phaser-4-renderer-faster-cleaner-and-built-for-modern-games)
- [Phaser GitHub Releases](https://github.com/phaserjs/phaser/releases)
- [PixiJS v8 Launch Post](https://pixijs.com/blog/pixi-v8-launches)
- [PixiJS v8 Intro Guide](https://pixijs.com/8.x/guides/getting-started/intro)
- [Phaser vs PixiJS Comparison — Dev.to](https://dev.to/ritza/phaser-vs-pixijs-for-making-2d-games-2j8c)
- [Tug of Math](https://tugofmath.app/en)
- [EZCalculatorOnline Tug of War](https://www.ezcalculatoronline.com/tug-of-war/)
- [MathTug](https://mathtug.com/en/)
- [Math Playground Tug Team Multiplication](https://www.mathplayground.com/ASB_TugTeamMultiplication.html)
- [Math Duel — Peaksel](https://peaksel.com/math-games/math-duel-2-player-math-game/)
- [Toy Theater Addition Pull](https://toytheater.com/addition-pull/)
- [ICT Games Tug of War](https://ictgames.com/mobilePage/tugofwar/index.html)
- [Rive — Interactive Experience Engine](https://rive.app/)
- [Rive Review 2026](https://digitalbydefault.ai/blog/rive-interactive-animation-review-2026/)
- [Rive vs Lottie 2025](https://dev.to/uianimation/rive-vs-lottie-which-animation-tool-should-you-use-in-2025-p4m)
- [Stop Using Lottie for Characters](https://dev.to/uianimation/stop-using-lottie-for-characters-why-rive-is-the-future-of-app-animation-1hjf)
- [Howler.js](https://howlerjs.com/)
- [Howler.js vs Tone.js vs Wavesurfer 2026 — PkgPulse](https://www.pkgpulse.com/guides/howler-vs-tone-js-vs-wavesurfer-web-audio-javascript-2026)
- [tsParticles / Confetti](https://particles.js.org/)
- [tsParticles Confetti npm](https://www.npmjs.com/package/@tsparticles/confetti)
- [Vite vs Next.js 2026](https://designrevision.com/blog/vite-vs-nextjs)
- [Vite vs Next.js — Strapi](https://strapi.io/blog/vite-vs-nextjs-2025-developer-framework-comparison)
- [Fredoka — Google Fonts](https://fonts.google.com/specimen/Fredoka)
- [Nunito — Google Fonts](https://fonts.google.com/specimen/Nunito)
- [Web Game Performance Optimization — Rune](https://developers.rune.ai/blog/web-game-performance-optimization)
- [Chrome Autoplay Policy](https://developer.chrome.com/blog/autoplay)
- [PWA Audio Autoplay — Prototyp](https://blog.prototyp.digital/what-we-learned-about-pwas-and-audio-playback/)
- [Navigator.vibrate() MDN](https://developer.mozilla.org/en-US/docs/Web/API/Navigator/vibrate)
- [Web Haptics Vibration API](https://blog.openreplay.com/haptic-feedback-for-web-apps-with-the-vibration-api/)
- [Squash and Stretch — Josh W. Comeau](https://www.joshwcomeau.com/animation/squash-and-stretch/)
- [Game Juice — Making Gameplay Satisfying](https://thedesignlab.blog/2025/01/06/making-gameplay-irresistibly-satisfying-using-game-juice/)
- [View Transitions API — Chrome Developers](https://developer.chrome.com/docs/web-platform/view-transitions)
- [React ViewTransition](https://react.dev/reference/react/ViewTransition)
- [WCAG 2.2 Color Contrast](https://www.allaccessible.org/blog/color-contrast-accessibility-wcag-guide-2025)
- [WCAG 2.2 — All Techniques](https://www.w3.org/WAI/WCAG22/Techniques/)
- [prefers-reduced-motion Ethics](https://medium.com/@vyakymenko/color-contrast-with-oklch-prefers-reduced-motion-and-motion-design-ethics-089c0c8897d0)
- [Game Accessibility — Filament Games](https://www.filamentgames.com/blog/accessibility-terms-for-game-developers-a-wcag-2-1-aa-glossary/)
- [CBSE Class 1 Maths Syllabus 2025-26 — Vedantu](https://www.vedantu.com/syllabus/cbse-class-1-maths-syllabus)
- [Core Web Vitals 2026](https://www.corewebvitals.io/core-web-vitals)
- [Prodigy Math](https://play.prodigygame.com/)
- [Khan Academy Kids](https://www.khanacademy.org/kids)
- [PWA Installation Guide — MDN](https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps/Guides/Making_PWAs_installable)
- [Making PWAs Installable — web.dev](https://web.dev/learn/pwa/installation-prompt)
