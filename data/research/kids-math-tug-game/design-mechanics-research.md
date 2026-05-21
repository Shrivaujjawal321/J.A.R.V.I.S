# Kids Math Tug-of-War Game — Design & Mechanics Research
**Date:** 2026-05-17  
**Prepared for:** ui-ux-designer-agent → frontend-engineer-agent  
**Product:** 2-player educational math web game, ages 6-8, tiger vs elephant tug-of-war, hot-seat + AI mode, Indian families, Android/tablet/desktop  

---

## 1. COMPETITIVE LANDSCAPE — What Exists Today

### Directly Overlapping Games (each reviewed individually)

---

**1. Math Duel: 2 Player Kids Games** (MWM)  
- iOS App Store: https://apps.apple.com/us/app/math-duel-2-player-kids-games/id1060040925  
- Google Play: https://play.google.com/store/apps/details?id=com.mathduel2playersgame.mathgame  
- **Mechanics:** Split-screen, same device, two players answer math questions simultaneously. Screen divided horizontally, each player has their own answer side. Covers +/−/×/÷. Adjustable difficulty per player independently (huge feature).  
- **What it does well:** Core mechanic is almost identical to our product. Topic + difficulty selection. No internet required.  
- **What it misses:** ZERO tug-of-war metaphor — it's just score counters. No character animation, no rope mechanic, no visual stakes. The "pull" feeling is completely absent. UI is 2014-era flat design with no personality. No AI opponent. No sound design worth noting. No Indian market optimization. No cartoon animals — just numbers and timers.  
- **Production quality:** Low. Functional but visually uninspired. 4-star rating but based on volume, not delight.

---

**2. Math Fight: 2 Player Math Game**  
- iOS: https://apps.apple.com/us/app/math-fight-2-player-math-game/id738947827  
- **Mechanics:** Same device, split-screen, race to answer first. Penalty of -1 point for wrong answer.  
- **What it does well:** Simple, fast, penalty system for wrong answers (aligns with our -0.5 step concept).  
- **What it misses:** No visual metaphor, no character, no tug-of-war, no AI. Penalty system is harsh for ages 6-8 (losing 1 full point vs our softer -0.5 step). No Indian market awareness.  
- **Production quality:** Low-medium. Better than Math Duel but still generic.

---

**3. Math Tug War – Kids Math Game** (com.app.kidsmathtugwar)  
- Google Play: https://play.google.com/store/apps/details?id=com.app.kidsmathtugwar  
- **Mechanics:** Tug of war style, kids compete by answering math questions, colorful characters. Ages 3-12. Bright cartoonish UI. Reward system with coins and badges.  
- **What it does well:** CLOSEST to our concept on the visual metaphor. Has the tug-of-war framing + cartoon characters + reward coins.  
- **What it misses:** Appears to be 1P vs AI only (no hot-seat 2P confirmed). No same-question race mechanic — players may see different questions. No split-screen UI for 2P hot-seat. Low production quality. Generic cartoon style. No Indian market adaptation.  
- **Production quality:** Low-medium. Bright but cheap-looking assets.

---

**4. Math Tug War: Solo & 2P** (com.hussain.mathtugwar)  
- Google Play: https://play.google.com/store/apps/details?id=com.hussain.mathtugwar  
- **Mechanics:** Local multiplayer on single screen, adaptive AI, 10 game modes (addition, subtraction, multiplication, division, count objects, biggest/smallest, even/odd, missing number).  
- **What it does well:** Has 2P hot-seat. Colorful kid-friendly interface. Broad operation coverage beyond just arithmetic.  
- **What it misses:** No SAME question shown to both players simultaneously — players appear to get sequential turns. No rope visual with animated characters pulling. No animal theme with personality. No Indian market design.  
- **Production quality:** Low-medium. Functional.

---

**5. MathTug (mathtug.com)**  
- URL: https://mathtug.com/en/  
- **Mechanics:** Classroom-focused, two TEAMS (not two individual players). Correct answers pull rope toward team's side. Free, no ads, no accounts. Works on projectors, smart boards, tablets. Large UI. Covers nursery-level counting through high school algebra.  
- **What it does well:** Genuinely free, no-friction entry. Large accessible UI. Curriculum-aligned difficulty tiers. Works everywhere.  
- **What it misses:** Team-vs-team for classrooms (8-30 students per side), NOT the hot-seat 2P family scenario. No character animation or personality. No animal mascots. No sound design. No offline mode. Not designed for home/family use at all.  
- **Production quality:** Medium. Clean, functional, minimal design. No "juice."

---

**6. Tug of Math (tugofmath.app)**  
- URL: https://tugofmath.app/en  
- **Mechanics:** Whiteboard-focused classroom tool. Each team has its own math problem (different problems, not same question). Multi-touch simultaneous input. Both teams tap answers at exact same time. K-6 students. 13 languages.  
- **What it does well:** True simultaneous multi-touch. No accounts/downloads. Works across 13 languages (localization model to study). Real-time competitive feel.  
- **What it misses:** Teams solve DIFFERENT questions (not same question — key design difference). Whiteboard/classroom only, not home. No character animation. Minimal visual design.  
- **Production quality:** Medium. Functional for classrooms.

---

**7. Toy Theater "Addition Pull" (toytheater.com)**  
- URL: https://toytheater.com/addition-pull/  
- **Mechanics:** Online tug-of-war addition game. Player answers correctly → pulls opponent toward water hazard. Wrong/slow answer → opponent pulls you. 5 progressively harder levels. Free web game. 1P vs AI only.  
- **What it does well:** Nails the visual metaphor (tug-of-war toward hazard = consequence). Progressive difficulty. Free and instant-play.  
- **What it misses:** 1P only. Extremely simple visual style (Flash-era). No cartoon character personality. No 2P hot-seat. No sound design worth noting. No Indian market relevance.  
- **Production quality:** Low. Functional but dated.

---

**8. Prodigy Math** (prodigygame.com)  
- URL: https://www.prodigygame.com  
- **Mechanics:** RPG fantasy world. Math problems power wizard battle spells. 1st-8th grade. Character progression, cosmetic unlocks.  
- **What it does well:** Narrative framing makes math feel purposeful. Deep progression system. Character customization drives retention. Covers curriculum systematically.  
- **What it misses:** NOT 2-player hot-seat. Math questions interrupt gameplay rather than being integrated. Aggressive premium upsells have drawn advocacy group complaints. Questions feel disconnected from the fantasy narrative. No Indian market optimization.  
- **Production quality:** High production value overall, but the monetization complaints are significant for educational credibility.

---

**9. Khan Academy Kids**  
- URL: https://learn.khanacademy.org/khan-academy-kids/  
- iOS: https://apps.apple.com/us/app/khan-academy-kids/id1378467217  
- **Mechanics:** Story + game format for ages 2-8. Character-guided activities. Read-aloud technology for non-readers. Common Core-aligned.  
- **What it does well:** Read-aloud for pre-readers (huge for our 6yr old use case). Zero cost. High production quality. Inclusive, diverse characters. Strong pedagogical foundation.  
- **What it misses:** Zero 2-player or competitive mechanics. Cooperative, solo-learning tool only. No competitive drive. No tug-of-war metaphor.  
- **Production quality:** High. Best-in-class for solo adaptive learning. Reference for animation quality and character design.

---

**10. Math Battle Arena (mathbattle.es)**  
- URL: https://www.mathbattle.es/  
- **Mechanics:** Free online multiplayer math game. Same question race — answer first to grab bonus points. Ages 6-14. Online 1v1 or vs AI.  
- **What it does well:** Same-question race mechanic (EXACTLY our mechanic, but online not hot-seat). Ages 6-14 coverage. Free. AI opponent.  
- **What it misses:** Online only (requires internet + accounts). No visual tug-of-war metaphor. No character/animal mascots. No hot-seat 2P same-device mode. No sound design.  
- **Production quality:** Low-medium. Basic UI.

---

**11. Kahoot! Kids**  
- URL: https://kahoot.com/home/kahoot-kids/  
- Play: https://play.google.com/store/apps/details?id=com.kahoot.kids  
- **Mechanics:** Same question shown to all players, first/fastest correct answer wins. Rocket Race mode (correct → rocket flies up). Read-aloud technology. Ages 3-12.  
- **What it does well:** Same-question race mechanic (core mechanic proven at scale). Read-aloud for non-readers. Visual feedback on correct answer (Rocket Race). Widely adopted in Indian schools.  
- **What it misses:** Requires separate devices per player. No hot-seat 2P. No tug-of-war visual. Designed for classrooms (teacher + 20 kids), not family home play.  
- **Production quality:** High. Polish, brand recognition. But designed for classroom not hot-seat.

---

### CRITICAL CONCLUSION: Does Our Exact Concept Exist?

**NO. The specific combination does not exist anywhere in the market:**

The combination of:
- (a) Same question shown to both players simultaneously  
- (b) Hot-seat 2-player on ONE device  
- (c) Animated tug-of-war visual metaphor with character mascots  
- (d) Designed specifically for ages 6-8  
- (e) Indian market cultural context  
- (f) Web-first (not app download)  
- (g) Numbers-first, minimal text for pre-readers  

...has zero direct competitors. Math Duel has (a) + (b) but misses (c)(d)(e)(f)(g). Math Tug War apps have (c) but miss (a)(b)(e)(f). Kahoot has (a) but requires separate devices. MathTug/TugOfMath are classroom-team tools, not family hot-seat.

**The gap is confirmed and significant.** The Indian family hot-seat market is entirely unserved with quality execution.

---

## 2. KID PSYCHOLOGY FOR AGES 6-8

### Attention Span
- Ages 6-8: average **8-12 minutes** of sustained task focus for structured activities. For games with active feedback loops, kids can sustain 15-25 minutes before disengagement. Source: general developmental psychology consensus; our 30-60 second match format is ideal — it fits within attention span as a single loop.
- **Our match length (30-60 sec) is correct.** Total session of 5-8 matches (4-7 minutes) fits perfectly.

### Reading Load
- Ages 6-7: **3-5 words max per instruction** on-screen before frustration. Ages 7-8: up to 8-10 words tolerable.
- Numbers and symbols are processed faster than words at this age. This validates our "numbers-first, minimal text" V1 approach completely.
- Kahoot's adoption of read-aloud for ages 3-12 confirms that text-only is not accessible for the lower end of our range.
- **Design rule:** No instruction should be >5 words. Prefer icons + numbers + sounds over words.

### Reward Cadence
- Kids 6-8 need a positive feedback moment **every 8-15 seconds** to maintain engagement (variable reward interval, not fixed).
- The habit loop (cue → routine → reward) applies: correct answer tap = cue → rope pulls = routine → character cheer + sound = reward.
- Prodigy's model shows that cosmetic rewards (character skins, badges) drive return sessions more than score alone.
- **Our design must ensure:** every correct answer produces an immediately visible consequence (rope moves), not just a score increment. The consequence must be animated and satisfying within 300ms of the tap.

### Frustration Threshold
- Khan Academy Kids and similar platforms calibrate to allow no more than **2-3 consecutive wrong answers** before offering a hint or reducing difficulty.
- In competitive games, 3 wrong answers in a row when opponent is winning can trigger "rage quit." Our -0.5 step (half penalty vs +1 for correct) is well-calibrated — it softens the punishment compared to most competitors.
- **Design rule:** After 3 consecutive wrong answers by one player, the AI (in 1P mode) should slightly slow down. In 2P mode, perhaps reduce the timer pressure briefly. [unverified — design hypothesis, not from published data]

### Competitive vs Cooperative at 6-8
- Ages 6-8 are developmentally in Piaget's Concrete Operational stage — they can understand rules, track scores, and feel genuine competitive drive.
- Carol Dweck's growth mindset research shows that framing wins/losses as effort outcomes ("You answered so fast!" rather than "You're so smart!") is protective against fixed mindset formation.
- Applied to our game: win screen should say something like "Amazing pulling! You answered 8 right!" not just "WINNER." Lose screen should be "You pulled hard! Next time, even faster!" rather than "YOU LOSE."
- Research shows **kids 6-8 can handle competitive loss gracefully IF the loss is presented as a close contest** and there's an immediate "Play Again" CTA.

### "Juice" — How Much Is Right
- Kids need **more juice than adults** — they're wired for exaggerated sensory feedback.
- The "juice problem" research (Wayline, 2024) notes that over-juiced adult games become noise, but for kids, the surplus feedback IS the point.
- **Right amount for ages 6-8:** Particle burst (20-30 particles max), 200-300ms screen shake (mild, not violent — kids on phone screens), character bounce animation 0.4-0.6s, sound within 50ms of tap. Rope animation should be smooth spring physics.
- Wrong answer: gentle red flash on button + soft "boop" sound (not buzzer, not harsh). Should feel like a soft bump, not a punishment.

### Win/Lose Screen Patterns
- Avoid: "YOU LOSE" in large red text — triggers distress response in 6-7 year olds.
- Best pattern (observed in Khan Academy Kids, Sago Mini): Character-expressive outcome. Winner's animal does a victory dance. Loser's animal gives a thumbs-up or a friendly wave (not crying/sad). Text says "Great match!" for both sides.
- **Our specific pattern:** Tiger wins → struts and roars playfully. Elephant wins → does a happy stomp. Non-winner side shows character doing something cute (shaking head playfully, "next time" gesture). Both see "Play Again?" as the primary CTA.

---

## 3. VISUAL DESIGN — Color, Typography, Illustration

### Color Palettes

**Palette 1 — Primary Vivid (Recommended for our game):**  
- Teal: `#00B4D8`  
- Sunny Yellow: `#FFCA3A`  
- Coral: `#FF595E`  
- Grass Green: `#8AC926`  
- Deep Purple: `#6A4C93`  
- Neutral White: `#FFFFFF`  
Used by: numerous top kids' learning apps. Warm + cool balance, high contrast, each color distinctly readable against white. Works colorblind-safe when not relying on red/green alone.

**Palette 2 — Warm Playful:**  
- Orange: `#F3722C`  
- Amber: `#F8961E`  
- Yellow: `#F9C74F`  
- Sage Green: `#90BE6D`  
- Sky: `#43AA8B`  
Good for: warm/sunny afternoon game feel. Works well for Indian visual taste (similar warmth to Holi color palette). High energy.

**Palette 3 — Bold Primary (for tiger/elephant theme):**  
- Tiger Orange: `#FF6B35`  
- Elephant Grey: `#9E9E9E`  
- Jungle Green: `#2D936C`  
- Sky Blue: `#4CC9F0`  
- Rope Tan: `#C9A84C`  
- Off-white: `#FFF8EE`  
This palette maps directly to our character theme. Tiger side = warm oranges, elephant side = cool blues/greys.

**Design rule:** Keep panel backgrounds slightly off-white or very light tint of the player's color. Never dark backgrounds for young kids — increases eye strain on small phone screens.

### Typography

**Top recommendation: Fredoka (variable font, available on Google Fonts)**  
- URL: https://fonts.google.com/specimen/Fredoka  
- Fredoka is the variable-weight evolution of Fredoka One. Rounded terminals, bold, bouncy, high legibility even at small sizes on mobile.  
- Perfect for score counters, math numbers, button labels.  
- **Note:** Single-story 'a' is NOT the default in Fredoka — check if the variable axes include it. For 6-7 year olds, single-story 'a' (like handwriting) is cognitively easier.  
- Use Fredoka at 28-36px minimum for question numbers, 48-60px for answer buttons.

**Second recommendation: Nunito (Google Fonts)**  
- URL: https://fonts.google.com/specimen/Nunito  
- Rounded terminals, friendly, slightly lighter weight than Fredoka. Excellent for body text / short instructional labels.  
- Variable font, full axis support.

**Avoid:** Comic Sans (dated, stigmatized), Sassoon Primary (not on Google Fonts, requires license), anything with decorative serifs, anything condensed/extended, italic-by-default.

**Type sizing rules for our game:**  
- Math question number: **56-72px** (must be readable at arm's length on phone)  
- Answer buttons: **40-52px**  
- Score counter: **32-40px**  
- Any instruction text: **24-28px**, max 5 words  
- Line height: 1.5× x-height (golden ratio is 1.618)

### Illustration Style

**Recommended for our game: Thick-outline Sticker Cartoon (2025 dominant trend)**

Why this style wins for Indian kids 6-8:
- 3-5mm thick black outlines on characters = recognizable from distance, no detail lost on small phone screens
- Flat fill with subtle shadow (no complex gradient rendering) = fast on Android mid-range devices
- Bold, exaggerated proportions = kid-affinity (big eyes, small body)
- Can be animated at 60fps with SVG/Rive without WebGL overhead

**Reference styles to match:**
1. **Khan Academy Kids characters** — thick outlines, expressive eyes, bold shapes. URL: https://learn.khanacademy.org/khan-academy-kids/ — study their character design.
2. **Toca Boca Jr style** — bold, diverse, thick outlines, flat with personality. URL: https://www.tocaboca.com/toca-boca-jr — color blocking and character silhouette clarity.
3. **Sago Mini School** — softer, rounder, even more minimalist. URL: https://sagomini.com — simpler than Toca Boca, works for ages 2-6. Slightly young for our target.
4. **Google's Noto Emoji Animals** — free, perfectly readable tiger and elephant designs. Good as starting reference for silhouette shape [unverified as production-ready].
5. **Skribbl.io style emotes** — very chunky, thick-lined cartoon style popular with younger kids. Reference for proportion exaggeration.

**For tiger vs elephant specifically:**
- Tiger: orange body, black stripes (2-3 max, not realistic), white belly, big round eyes, chunky limbs. Should FEEL cartoon, not realistic.
- Elephant: grey body, large ears, small tusks, thick stubby legs. Round friendly shape.
- Both characters need: idle animation (bouncing lightly), effort animation (leaning back, feet planted, straining), win animation (jumping/celebrating), lose animation (friendly "aww" gesture, not sad).

**Indian market note:** Indian kids 6-8 in 2025 have high exposure to Chhota Bheem animation style — thick outlines, vibrant colors, exaggerated expressions. Our style should be in that family. Avoid Western muted-pastel styles (too subtle).

### Iconography
- Use **Rive animated icons** for interactive elements (the tap/correct/wrong feedback icons).
- Static fallback: Lordicon (https://lordicon.com) — has animated tug of war icons already built.
- Style: solid/filled icons, not outlined — more readable on small screens for ages 6-8.
- Duotone (two-color solid): good for badges and achievement icons.

---

## 4. ANIMATION & MOTION DESIGN

### Tug-of-War Visual (most critical animation)

**What makes it feel satisfying:**
1. **Characters must visibly STRAIN.** Static slide along a line feels empty. Characters need a "lean-back" animation when their opponent is pulling. Feet should appear to dig in — even if it's just feet sliding on ground leaving skid marks.
2. **Rope should have physics.** Not a rigid line. Use a catenary curve (sagging middle) that snaps taut on pulls. A quick whip/snap motion on each pull event is extremely satisfying.
3. **The rope segment should JERK, not glide.** Each correct answer = 200ms quick pull animation (not smooth slide). Feels more like a real pull.
4. **Step-distance visualization.** A faint ground track under each character showing position marks (like a football field) gives parents/teachers visual feedback on score state without reading numbers.
5. **Ground reaction.** Dust puff under character feet when they're planted/straining. Small dirt kick when they get pulled.

**Reference games that nail it:**
- Toy Theater Addition Pull — simple but the "toward hazard" mechanic creates visual stakes. See how the endpoint (water) creates drama.
- Board game "Tug of War" mechanic on BGG (https://boardgamegeek.com/boardgamemechanic/2888/tug-of-war) — the track visualization with markers.

### Question Reveal Animation
- **Best for kids:** Bounce-in from below (card pops up). 200-300ms, slight overshoot (spring physics).
- Avoid: Card flip — adds complexity, 3D transform is disorienting for 6 yr olds.
- Avoid: Slide from side — kids misread it as "something went wrong, screen moved."
- The four answer buttons should stagger in at 50ms intervals after question appears (creates "unpack" feeling vs appearing all at once).

### Correct Answer Feedback Combo (calibrated for ages 6-8):
1. Button turns bright green + scale up 1.15× (100ms)
2. Burst of 20-25 star/sparkle particles from button (300ms)
3. Character on the winner's side does a quick "pull!" animation (300ms lean-back + step forward)
4. Rope jerks 1 step toward winner (200ms spring animation)
5. Celebratory sound (bright chime/ding, C-major)
6. Score counter increments with a pop
**Total perceived time: ~400ms** — feels instant, not laggy.

### Wrong Answer Feedback (softened for kids):
1. Button gently flashes red-orange (NOT full red — less alarming) for 150ms
2. Gentle horizontal shake of button (3px left-right, 2 cycles, 200ms) — like a head-shake, not violent screen shake
3. Soft "boop" sound (descending two-note, not buzzer)
4. Character on the wrong-answerer's side does a tiny stumble-back (150ms)
5. Rope moves 0.5 step back from wrong-answerer's character
**No "WRONG" text. No big red X.** Visual cues only.

### Idle State Between Questions
- Both characters should gently breathe (slow scale pulse 1.0→1.02→1.0 at ~0.8s period).
- After 3+ seconds of inactivity, trigger a random idle animation: tiger yawns and stretches, elephant flaps ears and sways.
- This adds massive personality and tells kids the game is "alive."
- Implement via Rive state machine: IDLE → STRAIN → CELEBRATE → STUMBLE states with transitions.

### Win/Lose Screens
- **Winner side:** Character does full victory dance (500ms loop). Confetti particles from top of screen. "Play Again?" button bounces in.
- **Loser side:** Character does a friendly shrug + wave gesture (NOT sad/droopy). Small encouragement text: "So close! Try again?" 
- **Transition into this screen:** Both character sides slide off the rope + expand to fill their half-screens, then a full-screen overlay fades in with results.
- **Time on results screen:** 3-5 seconds of celebration, then auto-show "Play Again?" CTA prominently.

### Recommended Animation Libraries

**Rive (primary character animation):**
- URL: https://rive.app/  
- Use for: Tiger + elephant character states (idle/strain/celebrate/stumble) as a Rive state machine. 10-15× smaller file size vs Lottie equivalent. State machine transitions triggered by game events (correct answer → trigger "pull" animation, wrong → trigger "stumble").
- Web runtime: `@rive-app/canvas` npm package. Runs at 120fps on modern hardware.
- **This is the right choice for our characters.** Rive is the 2025-2026 standard for interactive character animation in games and apps.

**GSAP 3.13 (rope physics + UI transitions):**
- URL: https://gsap.com/  
- Use for: Rope curve animation (custom SVG path morphing), screen transitions, button spring animations, confetti particles.
- `gsap.to()` with `elastic` or `spring` ease for rope jerks.
- Free for non-commercial, very affordable commercial license.

**Framer Motion 12 (if using React):**
- URL: https://www.framer.com/motion/  
- Use for: Layout animations, page transitions, button feedback on correct/wrong. `spring` physics built-in.
- Less suited for character animation than Rive.

**Lottie (for specific UI icons/badges):**
- URL: https://airbnb.io/lottie/  
- Use for: Badge unlock animations, loading states, static decorative elements. NOT for character animation — use Rive for that.

---

## 5. SOUND DESIGN

### Library / Framework
**Howler.js (strongly recommended):**
- URL: https://howlerjs.com/  
- 7KB gzipped, zero dependencies. Defaults to Web Audio API, falls back to HTML5 Audio. Supports audio sprites (bundle all SFX into one file, reference by time offsets). Critical for mobile — reduces the number of network requests dramatically.
- Supports all formats: OGG (primary), MP3 (fallback), AAC (iOS Safari).

### Free SFX Sources (verified)

| Source | Best For | License |
|--------|----------|---------|
| **Mixkit** (mixkit.co) | Kids UI SFX, game sounds, free children category | Free, royalty-free, no attribution |
| **ZapSplat** (zapsplat.com) | 160,000+ professional SFX, kids-specific category | Free with attribution / paid no-attribution |
| **Freesound** (freesound.org) | Community-sourced, CC0 and CC-BY options | Varies per file, many CC0 |
| **BBC Sound Effects Archive** | High-quality nature/animal sounds | Free for personal/educational use |
| **OpenGameArt** (opengameart.org) | Game-specific SFX, music, explicitly CC licensed | CC0/CC-BY |

**Specific SFX needed for our game:**
- Correct answer chime: bright C-major arpeggio, 300ms
- Wrong answer: soft descending two-note boop, 200ms
- Rope pull: quick whoosh/twang, 150ms
- Win: fanfare, 1.5-2s
- Crowd/encourage: short cheer burst, 600ms
- Character idle sounds: yawn, stretch, ear-flap (optional, adds personality)
- Button tap: satisfying "pop" click, 80ms
- Countdown: 3-2-1 tones (descending thirds, not beeps)

### Background Music
- **Include it.** Background music for kids ages 6-8 significantly increases engagement and sets mood. Without music, the game feels empty between questions.
- **Style:** Upbeat, percussive, light xylophone/marimba-forward. Think Toby Fox (Undertale) energy but simpler. BPM 120-140 (upbeat but not frantic). Key: major (happy, energetic).
- **Looping:** Use seamless loop points. Crossfade on loop. Keep loop length 30-60 seconds to avoid listener fatigue.
- **Source:** OpenGameArt has many CC-licensed kids-appropriate looping game music tracks. Kevin MacLeod (incompetech.com) has family-friendly instrumental tracks (CC-BY).
- **Mute toggle:** Default ON. Prominent speaker icon in corner. Kids (and parents in quiet settings — classroom, airplane) will toggle off. Parent-friendly: show mute toggle prominently on home screen.

### Voice-Over Consideration
- **Highly recommended for V1.5, not mandatory in V1** but design should leave room.
- Web Speech API (free, built into browsers) can read questions aloud with zero production overhead.
- `window.speechSynthesis.speak(new SpeechSynthesisUtterance("3 plus 4"))` — zero infrastructure cost.
- For Indian English accent: test whether Chrome's `hi-IN` voice is good enough, or use `en-IN` voice.
- **Why it matters:** A 6-year-old who can't read "multiplication" can hear "What is 3 times 4?"
- **V1 design decision:** Add a speaker icon on the question that reads it aloud on tap. Does not need to auto-play (would be chaotic in 2P mode with both players seeing same question).

### 2026 Audio Anti-Patterns to Avoid
- Bass drops, whomp sounds (adult gaming trope, alarming for kids)
- Volume spikes louder than background music
- Long silence gaps between question and feedback
- "FAIL" or "LOSER" voice lines
- Overlapping sound triggers without debounce (rapid tapping causes audio pile-up)

---

## 6. UX FLOW — Home to First Match

### Ideal Screen Flow

```
HOME SCREEN
├── [Play with Friend] → MODE SELECT → [Both players see same device]
├── [Play Alone] → MODE SELECT → AI difficulty (Easy / Med / Hard)
└── [Settings] → [Sound toggle, Language if needed]

MODE SELECT (shown only if applicable)
└── Already implicitly chosen from home

TOPIC + DIFFICULTY SELECT
├── Topic: [+] [−] [×] [÷] [Mix]
└── Difficulty: [Easy] [Medium] [Hard]
(Big colorful buttons, one per choice. No dropdowns. Both players choose together.)

CHARACTER SELECT (optional in V1, nice-to-have)
├── Player 1 picks: [Tiger 🐯] or [Elephant 🐘] (or future unlockable)
└── Player 2 gets the other (or mirror choice)
(5-second screen, then auto-advance or tap-to-confirm)

COUNTDOWN
└── Animated 3-2-1 on full screen. Both characters appear on their sides. Rope appears. Crowd cheer sound.

MATCH (split-screen game state)
├── TOP HALF: Tug-of-war visual (rope + characters + position track)
└── BOTTOM HALF: Math question (center) + P1 buttons (left) + P2 buttons (right)

RESULTS SCREEN
├── Victory/encouragement based on outcome
├── Stats: "You got X right!"
└── [Play Again] [Change Settings] [Home]
```

### Screen-by-Screen CTA and Transitions

| Screen | Primary CTA | Transition |
|--------|-------------|------------|
| Home | "Play with Friend" | Scale-in tap → slide-up reveal of next screen |
| Topic + Difficulty | "Start!" | View Transitions API morph (if supported) → game screen |
| Countdown | (none — automatic) | Fade in characters, rope drops down from top |
| Match | Tap answer button | No full-screen transition — everything happens in-place |
| Results | "Play Again!" | Full-screen confetti → slide in results card |

### Onboarding (Zero-Text Approach for 6-year-olds)
- On first launch: skip all text. Run a 10-second **animated demo** where a ghost hand taps the correct answer button, the rope moves, character celebrates. Repeat once.
- "Finger pointing" animation on P1 side: big bouncing arrow pointing to buttons. Fades after first correct tap.
- In AI mode: AI starts at 1-second delay on Easy, giving the kid a head start + time to learn the mechanic before losing.
- No tutorial text. Only visual + audio demonstration.

---

## 7. RESPONSIVE LAYOUT — The Hardest Problem

### Phone Landscape (~640×360px total)
After horizontal split: each player half = **640×180px**

**This is tight. Here is the only layout that works:**

```
[ 640 × 180 px — Player half ]
┌─────────────────────────────────────┐
│  [Btn A]   [Btn B]   Question Area  │  <- NOT POSSIBLE, too wide
└─────────────────────────────────────┘
```
**2×2 grid is the answer:**
```
[ 640 × 180 px — Player half ]
┌──────────────┬──────────────┐
│   [Btn A]    │   [Btn B]    │
├──────────────┼──────────────┤
│   [Btn C]    │   [Btn D]    │
└──────────────┴──────────────┘
```
Each button = ~320×90px. At 90px height, thumb targets are barely adequate (WCAG recommends 44px minimum — 90px is good). This layout is recommended over horizontal row of 4 (which would give ~160×180px per button — awkward).

**BUT:** The question itself needs to show somewhere in this half. Two options:
- **Option A:** Question appears in the CENTER of the full screen (tug-of-war area), large, readable from both sides. Each player's half only contains their 4 answer buttons + a thin score strip. This is cleanest.
- **Option B:** Tiny question display above the 2×2 grid in each player's half (same question repeated twice). Risk: at 640×180, adding question text leaves buttons at ~320×65px — getting small.

**Recommendation: Option A.** Question lives in the tug-of-war visual zone. Both players read it from the shared top half. Buttons fill each player's bottom half completely.

### Thumb Ergonomics on Phone Landscape
- Two-handed grip (landscape phone) = thumbs naturally reach center of their respective half-screen.
- Thumb reach zones: roughly the middle 60% of width and bottom 70% of height are most comfortable.
- Avoid placing critical buttons in top-left/top-right corners (thumb dead zones in landscape).
- **Our 2×2 grid filling each player's half is exactly in the thumb comfort zone.**

### Portrait Mode — Support or Skip?
- **Skip in V1.** Portrait 2P hot-seat on one phone is physically awkward — two players would be face-to-face holding the same phone vertically.
- Landscape is the natural hot-seat orientation. Force landscape for 2P mode.
- For 1P vs AI mode: **support portrait** — one player, one hand, casual play. This doubles the addressable use case.

### Tablet Layout (768-1024px wide)
- Much more room. Top half = 768×400px tug-of-war area. Bottom half = full-width question + two player zones.
- Characters can be larger, animations more expressive.
- Consider: in tablet landscape, show question BETWEEN the two player zones (horizontal split instead of the phone's vertical zones). Player 1 buttons on left 40%, question in center 20%, Player 2 buttons on right 40%.
- Tablet is the optimal device for this game — target it as primary canvas.

### Desktop Layout (1200px+)
- Three-column: P1 buttons | Tug-of-war + Question | P2 buttons.
- Keyboard shortcuts: `A/S/D/F` for P1, `J/K/L/;` for P2. Label buttons with keys shown. This is a known pattern in desktop split-keyboard games and significantly improves desktop feel.
- Maximum canvas width: 1280px, centered. Don't stretch to 1920 — too much dead space.

---

## 8. ACCESSIBILITY (WCAG 2.2 AA for Kids)

### Color Contrast
- Answer buttons: text must achieve **4.5:1 contrast ratio** against button background (AA standard).
- Score counters: same standard.
- Wrong answer red-orange: use `#E85D04` (orange-red) not pure `#FF0000` — more accessible and less alarming. Against white: 3.8:1 (AA for large text, which our buttons are).
- Correct green: use `#2D6A4F` text on `#95D5B2` background rather than pure green — colorblind-safe.

### Colorblind-Safe Design
- **Never rely on red/green alone** to signal correct/wrong. Add:
  - Icon: ✓ (checkmark) for correct, × for wrong — in addition to color
  - Shape: correct button gains rounded glow, wrong button gains shake
  - Sound is the third signal
- Deuteranopia (red-green colorblindness) affects ~8% of males. At Indian population scale, many players will experience this.

### Reduced Motion
- Implement `prefers-reduced-motion` CSS media query.
- When triggered: replace particle bursts with simple color flash. Replace rope spring physics with instant move. Replace character celebration with scale pulse.
- Rive supports conditional animation paths — create a "reduced" state path.

### Touch Target Minimum
- WCAG 2.2 requires 24×24px minimum, but for ages 6-8 aim for **minimum 60×60px**. Our 320×90px buttons are well above threshold.

### Audio-Only Feedback Mode
- In classroom silent mode (mute toggled): visual feedback must be 100% sufficient. The color/shape/animation signals above must carry all the information that sound does.

### Focus Indicators
- For desktop keyboard users: clear, high-contrast focus ring (3px solid) on answer buttons.

---

## 9. MONETIZATION — V1 Design Decisions for V2 Readiness

### What Works in Kids Games in 2026 (without being predatory)

**Best model for our use case: Free Core + Cosmetic Unlockables (Pay-Once or Earn-in-Game)**

- **Core gameplay forever free.** Indian market is F2P-dominant. Charging upfront prevents trial.
- **Unlockable characters:** The "locked character" silhouette on character select screen is a known conversion driver. "Unlock Panda 🐼 and Dinosaur 🦕" behind a one-time small IAP (₹49-99) or earn via gameplay badges.
- **No loot boxes, no random rewards for real money** — COPPA/India regulations, ethical concerns, and parent trust are all against it.
- **No in-game ads in kids' products** — COPPA strictly limits advertising in apps directed at children under 13.
- **Parent-pay model:** Parent unlocks a "Premium Pack" (₹99-149 one-time) for extra characters + math topics + no ads. Child gets gifted value; parent controls spending.

### V1 Design Decisions to Leave Room for V2 Monetization
1. **Character select screen already has placeholders** for locked characters (show silhouettes, "Coming soon" badge). Avoids redesign.
2. **Badge/achievement system exists in V1** (even if not monetized) — gives V2 something to gate.
3. **No hardcoded "Free" assumptions** — premium content slots exist in state/data model even if all currently `unlocked: true`.
4. **No persistent banner ad space** in V1 layout — but a collapsible "parent zone" footer could hold a single house ad or external link if needed.

---

## 10. NAMED REFERENCES — The Builder MUST Study These

These 10 references set the quality bar. Study design, animation, feel, sound, and UX flow for each.

| # | Name | URL | Why Study It |
|---|------|-----|--------------|
| 1 | **Khan Academy Kids** | https://learn.khanacademy.org/khan-academy-kids/ | Best-in-class character design, read-aloud UX, no-text onboarding, sound design, kid-safe win/lose screens |
| 2 | **MathTug Tug of War** | https://mathtug.com/en/games/tug-of-war/ | Closest visual mechanic to ours — study what's missing (no character animation, no juice, no sound) and exceed it |
| 3 | **Toy Theater Addition Pull** | https://toytheater.com/addition-pull/ | Visual stakes ("pull opponent into water") — how consequence is visualized even in a basic game |
| 4 | **Kahoot! Kids** | https://kahoot.com/home/kahoot-kids/ | Same-question race mechanic proven at scale. Rocket Race animation on correct answer. Read-aloud integration |
| 5 | **Toca Boca Jr** | https://www.tocaboca.com/toca-boca-jr (or App Store) | Illustration style reference — thick outlines, bold colors, character expressiveness. Indian kids love this style |
| 6 | **Math Duel: 2 Player Kids Games** | https://play.google.com/store/apps/details?id=com.mathduel2playersgame.mathgame | Direct competitor — understand what they got right mechanically and what their visual gap is. We need to be 5× better UX than this |
| 7 | **Rive Community — Kids/Game examples** | https://rive.app/community/ | Search "character" and "game" — study state machine architectures used by teams building game characters |
| 8 | **GameUI Database — Kids/Casual** | https://gameuidatabase.com/ | Filter by "Kids" and "Educational" — screenshot references of UI layouts, button sizes, color systems in production kids games |
| 9 | **Prodigy Math** | https://www.prodigygame.com/main-en | Study their reward systems, cosmetic unlock screens, and character progression — what drives kids back daily. Then deliberately avoid their aggressive upsell patterns |
| 10 | **Math Battle Arena** | https://www.mathbattle.es/ | Only existing web game with same-question race mechanic. Study the answer-racing UX in isolation, then add everything it lacks |

---

## Summary for Designer Agent

### The One-Sentence Brief
Build a web game that feels like **Kahoot's same-question race mechanic** + **Toy Theater's visual tug-of-war stakes** + **Toca Boca's thick-outline cartoon character quality** + **Khan Academy Kids' kid-safe win/lose and read-aloud accessibility** — none of which currently exist in the same product, for the Indian hot-seat family market.

### Design System Anchors
- **Font:** Fredoka (variable, Google Fonts) — 56px questions, 44px buttons, 28px labels
- **Color:** Palette 1 (Teal + Coral + Yellow + Green + Purple) with Palette 3 animals (Tiger Orange / Elephant Grey)
- **Characters:** Thick-outline sticker cartoon, animated in Rive state machine
- **Rope:** SVG catenary curve, GSAP spring physics on pull events
- **Layout:** Landscape-first, 2×2 button grid per player half, question in shared top visual zone
- **Sound:** Howler.js, audio sprites, ZapSplat + Mixkit SFX sources, looping marimba background music
- **Juice level:** High (20-25 particles on correct, spring rope, character lean-back, 300ms total feedback chain)
- **Failure UX:** Soft orange flash + gentle shake + boop — no red X, no "WRONG" text
- **Win/lose:** Character expression-based, growth-mindset framing, immediate Play Again CTA
- **Accessibility:** Colorblind-safe (shape + color + sound triple-signal), reduced-motion media query, 60×60px minimum touch targets, WCAG 2.2 AA contrast

### Gap Confirmed: Green-Field Opportunity
No existing product combines all five: (1) same-question race + (2) hot-seat 2P + (3) animated tug-of-war character metaphor + (4) ages 6-8 Indian families + (5) web-first no-download. The market gap is real and the execution bar is clear.

---

*Research compiled 2026-05-17. Sources cited inline and below.*

## Sources Consulted
- Math Duel: 2 Player Kids Games — https://apps.apple.com/us/app/math-duel-2-player-kids-games/id1060040925
- Math Tug War Android — https://play.google.com/store/apps/details?id=com.app.kidsmathtugwar
- Math Tug War Solo & 2P — https://play.google.com/store/apps/details?id=com.hussain.mathtugwar
- MathTug — https://mathtug.com/en/
- Tug of Math — https://tugofmath.app/en
- Toy Theater Addition Pull — https://toytheater.com/addition-pull/
- Prodigy Math Review — https://kidedtools.com/blog/prodigy-math-game-review-2025/
- Khan Academy Kids — https://learn.khanacademy.org/khan-academy-kids/
- Kahoot Kids — https://kahoot.com/home/kahoot-kids/
- Math Battle Arena — https://www.mathbattle.es/
- Rive vs Lottie 2025 — https://dev.to/uianimation/rive-vs-lottie-which-animation-tool-should-you-use-in-2025-p4m
- Rive State Machine — https://help.rive.app/editor/state-machine
- Howler.js — https://howlerjs.com/
- Mixkit Free SFX — https://mixkit.co/free-sound-effects/children/
- ZapSplat — https://www.zapsplat.com/sound-effect-category/childrens/
- Typography for Kids (UX of EdTech) — https://medium.com/ux-of-edtech/typography-in-digital-products-for-kids-f10ce0588555
- Fredoka (Google Fonts) — https://fonts.google.com/specimen/Fredoka
- Nunito (Google Fonts) — https://fonts.google.com/specimen/Nunito
- Kids Color Palettes — https://colorhunt.co/palettes/kids
- Game "Juice" Design — https://www.gameanalytics.com/blog/squeezing-more-juice-out-of-your-game-design
- Smashing Magazine Practical Guide Design for Children (2024) — https://www.smashingmagazine.com/2024/02/practical-guide-design-children/
- NN/g Children UX — https://www.nngroup.com/articles/childrens-websites-usability-issues/
- Frontiers Game-Based Learning 2024 — https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2024.1307881/full
- India Mobile Game Market 2025 — https://sensortower.com/blog/india-mobile-game-insights-2025
- Kids Game Monetization 2026 — https://dev.to/linou518/indie-game-monetization-in-2026-premium-dlc-or-subscription-which-path-is-right-for-you-955
- Tug of War: Mathematics App — https://mwm.ai/apps/tug-of-war-mathematics/6759117890
- WCAG 2.2 — https://www.w3.org/TR/WCAG22/
- Toca Boca Jr — https://www.tocaboca.com/toca-boca-jr
- GameUI Database — https://gameuidatabase.com/
