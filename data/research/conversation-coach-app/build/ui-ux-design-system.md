# ARIA — UI/UX Design System
**Version:** 1.0 — MVP (Web)
**Stack target:** Next.js 15 + Tailwind 4 + shadcn/ui v4 + React 19
**Date:** 2026-05-27
**Owner:** UI/UX Design Specialist → Frontend Engineer handoff

---

## 1. Executive Summary

ARIA's design language is built on a single premise: **Aria would design her own home to feel like this.** She lives in Lisbon. Her apartment has good afternoon light, linen curtains, a half-finished novel on the table. The UI should carry that same quality — warm without being cozy, considered without being cold, restrained in a way that signals taste rather than austerity. The palette anchors in warm off-white (the limestone and sun-faded plaster of Lisbon's Alfama) with a single chosen accent. Typography pairs Fraunces (a variable optical-axis serif with a slight "wonk" that reads as literary personality) with Inter Variable (clean, legible, invisible when it should be). Motion is nearly absent — portrait crossfades at 200ms, the waveform breathes, nothing celebrates. The success state is not a confetti moment; it is a graduation. The design must know this from its first pixel.

---

## 2. Design Tokens

### 2.1 Color — OKLCH Palette

OKLCH is used throughout. Hex fallbacks are provided for tools that don't support OKLCH yet. All contrast ratios are calculated against the base background unless noted.

#### Semantic Roles

```
Role                        OKLCH                           Hex fallback    Contrast on bg-base
────────────────────────────────────────────────────────────────────────────────────────────────
bg-base                     oklch(0.97 0.008 78)            #F8F4EE         —
bg-surface                  oklch(0.99 0.004 78)            #FDFCFA         —
bg-muted                    oklch(0.93 0.014 78)            #EDE8E0         —
bg-elevated                 oklch(1.00 0.000 0)             #FFFFFF         —
border-default              oklch(0.88 0.012 78)            #DDD8CE         —
border-muted                oklch(0.92 0.010 78)            #E8E3DB         —
text-primary                oklch(0.22 0.022 60)            #2A2318         13.4:1
text-secondary              oklch(0.42 0.020 68)            #575040         5.2:1
text-muted                  oklch(0.56 0.016 72)            #7A7264         3.9:1 (large text / UI chrome only)
text-on-accent              oklch(0.99 0.004 78)            #FDFCFA         see accent variants
────────────────────────────────────────────────────────────────────────────────────────────────
```

#### Three Accent Options (Boss picks one)

**Option 1 — Terracotta ("Aria's father's warmth, Lisbon rooftops")**

Reasoning: Aria's Brazilian father is described as "warm but unreliable." Lisbon's rooftops are terracotta tile. This color carries the warmth that Aria rarely shows — it appears in the product's signal moments (genuine moment counter, level-up, voice button active state) in a way that feels earned, not default. Indie skincare brand palette — exactly the world Aria works in as a copywriter.

```
accent-base                 oklch(0.62 0.13 43)             #B06030
accent-light                oklch(0.76 0.09 43)             #CB9070
accent-subtle               oklch(0.91 0.05 43)             #F0DDD3
accent-on-light-bg          oklch(0.54 0.14 43)             #923D1A    4.9:1 on bg-base (AA for normal text)
```

**Option 2 — Sage ("Aria's mother's restraint, the Bear app's quiet")**

Reasoning: Aria's German mother is "cold but principled." Sage is the restraint option — Mediterranean, literary magazine (Monocle-era green), Bear app-adjacent. This accent feels cerebral and considered. It signals the intellectual register Aria defaults to when not yet warm. Most aligned with the "reserved" end of her character.

```
accent-base                 oklch(0.62 0.09 148)            #567A5C
accent-light                oklch(0.78 0.07 148)            #91B896
accent-subtle               oklch(0.93 0.04 148)            #DFE9E0
accent-on-light-bg          oklch(0.44 0.10 148)            #2E5C35    5.8:1 on bg-base (AA)
```

**Option 3 — Dusty Mauve ("faded Lisbon walls, literary winter afternoons")**

Reasoning: The faded painted facades of Lisbon's Mouraria neighbourhood — a dusty rose-violet. Aria collects strangers' handwriting. This color has the quality of old ink, pressed flowers, writing that's been carried in a pocket. The most "literary journal" option. Unusual in the app space — genuinely distinctive.

```
accent-base                 oklch(0.68 0.08 354)            #A87585
accent-light                oklch(0.82 0.05 354)            #C9A4AE
accent-subtle               oklch(0.93 0.03 354)            #EDE2E5
accent-on-light-bg          oklch(0.48 0.10 354)            #7A3D50    5.4:1 on bg-base (AA)
```

**Designer recommendation:** Terracotta (Option 1). It maps directly to Aria's Lisbon setting and her Brazilian father's warmth — the warmth that appears only when earned. The accent being a warm fire-earth tone on a cool parchment background creates the exact tension the product is about: warmth is not the default; it is the destination.

#### State Colors (shared across all accent choices)

```
state-error                 oklch(0.52 0.18 27)             #B03020
state-error-bg              oklch(0.95 0.03 27)             #F7E8E5
state-success               oklch(0.54 0.14 148)            #2D5E3C
state-success-bg            oklch(0.95 0.03 148)            #E3EFE6
state-warning               oklch(0.68 0.14 70)             #9A7020
focus-ring                  var(--color-accent-base)
```

#### Dark Mode (prefers-color-scheme: dark)

```
bg-base dark                oklch(0.13 0.016 60)            #1C1710
bg-surface dark             oklch(0.17 0.016 60)            #231E14
bg-muted dark               oklch(0.21 0.018 62)            #2B2519
border-default dark         oklch(0.30 0.016 62)            #3E3830
text-primary dark           oklch(0.93 0.010 78)            #EDE9E3
text-secondary dark         oklch(0.72 0.012 72)            #B5AFA7
text-muted dark             oklch(0.54 0.012 72)            #7E7870
```

---

### 2.2 Typography

#### Scale

```
Step    Size/Line   Use
─────────────────────────────────────────────────────────────────
xs      11/16       AI disclosure pill, skill labels (uppercase), footer links
sm      13/18       Secondary labels, genuine moments counter
base    15/22       Body / UI chrome (Inter)
md      17/26       Aria's transcript text (Fraunces)
lg      22/30       Section headers (Fraunces), onboarding headline
xl      28/36       Onboarding primary headline (Fraunces, light weight)
2xl     36/44       Graduation ceremony type-out (Fraunces, italic)
```

#### Font Families

```
sans:    "Inter Variable", "Inter", -apple-system, BlinkMacSystemFont, system-ui, sans-serif
serif:   "Fraunces", Georgia, "Times New Roman", serif
mono:    "JetBrains Mono Variable", "JetBrains Mono", "Fira Code", monospace
```

#### Loading strategy (Next.js)

```typescript
import { Fraunces, Inter } from "next/font/google";

export const inter = Inter({
  subsets: ["latin"],
  variable: "--font-sans",
  display: "swap",
});

export const fraunces = Fraunces({
  subsets: ["latin"],
  variable: "--font-serif",
  axes: ["SOFT", "WONK"],   // WONK axis gives Fraunces its literary personality
  display: "swap",
  style: ["normal", "italic"],
});
```

#### Typographic treatments per surface

| Surface | Font | Weight | Size | Notes |
|---|---|---|---|---|
| Aria's spoken text (transcript) | Fraunces | 300 italic | 17/28 | The "she said" register — literary, personal |
| User's spoken text (if shown) | Inter | 400 | 15/22 | Clean, functional |
| Onboarding headline | Fraunces | 300 | 28–36/40 | Large, breathing, inviting |
| UI labels | Inter | 400–500 | 11–13/16 | Functional, muted |
| Skill names | Inter | 500 | 11/16 | Uppercase, 0.08em letter-spacing |
| AI disclosure | Inter | 400 | 11/16 | Persistent but unobtrusive |
| Graduation type-out | Fraunces | 300 italic | 22/32 | Slow reveal, full-screen |

---

### 2.3 Spacing Scale

Base unit: 4px. All values in rem (assuming 16px root).

```
0     0px     0rem
1     4px     0.25rem
2     8px     0.5rem
3     12px    0.75rem
4     16px    1rem
5     20px    1.25rem
6     24px    1.5rem
8     32px    2rem
10    40px    2.5rem
12    48px    3rem
16    64px    4rem
20    80px    5rem
24    96px    6rem
32    128px   8rem
```

#### Layout constants

```
max-width-conversation:   420px   (centered column, all viewports)
portrait-size:            280px   (portrait illustration)
portrait-size-sm:         240px   (< 375px screens)
mic-button-size:          72px    (48px min for a11y, 72px for comfort)
skill-strip-height:       48px    (bottom strip)
disclosure-height:        32px    (top pill bar)
```

---

### 2.4 Border Radii

```
none    0px
sm      4px     (pills inner segments, inputs)
md      8px     (small cards, tooltips)
lg      12px    (buttons, primary surfaces)
xl      20px    (modals, onboarding cards, portrait frame)
2xl     28px    (mic button when large)
full    9999px  (AI disclosure pill, genuine moments badge, dot indicators)
```

---

### 2.5 Shadow System

Shadows are warm-tinted (low chroma, hue 60) to prevent the cold-grey shadow look.

```
shadow-sm:  0 1px 3px oklch(0.15 0.02 60 / 0.06)
shadow-md:  0 2px 8px oklch(0.15 0.02 60 / 0.08), 0 1px 3px oklch(0.15 0.02 60 / 0.04)
shadow-lg:  0 8px 32px oklch(0.15 0.02 60 / 0.12), 0 2px 8px oklch(0.15 0.02 60 / 0.05)
shadow-xl:  0 16px 56px oklch(0.15 0.02 60 / 0.16), 0 4px 16px oklch(0.15 0.02 60 / 0.08)
shadow-portrait: 0 4px 24px oklch(0.15 0.02 60 / 0.10)   (Aria's portrait frame)
shadow-none: none
```

---

### 2.6 Motion Language

**Principle:** Every animation must aid cognition or signal state. Remove decorative motion. The feeling is "intimate, quiet, considered." Nothing bounces. Nothing celebrates except the graduation.

```json
{
  "duration": {
    "instant":    "0ms",
    "fast":       "120ms",
    "base":       "200ms",
    "slow":       "350ms",
    "portrait":   "200ms",
    "waveform":   "80ms",
    "graduation": "600ms"
  },
  "easing": {
    "linear":     "linear",
    "out":        "cubic-bezier(0.0, 0.0, 0.2, 1.0)",
    "in-out":     "cubic-bezier(0.4, 0.0, 0.2, 1.0)",
    "subtle":     "cubic-bezier(0.2, 0.0, 0.4, 1.0)",
    "waveform":   "cubic-bezier(0.4, 0.0, 0.2, 1.0)",
    "spring-soft":"cubic-bezier(0.34, 1.1, 0.64, 1.0)"
  }
}
```

**Reduced motion contract:**
- All crossfades: instant (0ms) or simple opacity 1 → 1 (no position shift)
- Audio waveform: static flat line at 4px height, no animation
- Skill level-up: instant fill, no pulse
- Graduation type-out: show full text at once, no character-by-character reveal
- CSS: `@media (prefers-reduced-motion: reduce)` block in design-tokens.css enforces all of the above

---

## 3. Component Specs

### 3.1 Voice Button

The most critical interaction element. The user's primary input.

#### Anatomy

```
┌─────────────────────────────┐
│                             │
│         [outer ring]        │  ← animated ring, 80px circle, accent at 20% opacity
│      ┌──────────────┐       │
│      │  [mic icon]  │       │  ← 28px SVG icon, white, centered
│      │  72px circle │       │  ← filled circle, accent gradient
│      └──────────────┘       │
│                             │
│     "Tap to talk"           │  ← label, 13px Inter, text-muted, centered below
│                             │
└─────────────────────────────┘
```

#### State Matrix

| State | Visual | Label | Animation | Notes |
|---|---|---|---|---|
| **default** | Accent-filled circle, subtle warm shadow, mic icon white | "Tap to talk" | None | Initial state, waiting |
| **hover** | Circle lightens (accent-light), outer ring appears at 30% | "Tap to talk" | Ring fades in 120ms | Desktop only |
| **focus** (keyboard) | 3px focus ring, offset 3px, accent color, shape follows circle | "Tap to talk" | Ring on focus | WCAG 2.2 — :focus-visible only |
| **listening** | Circle pulses — outer ring: scale 1.0→1.15→1.0, opacity 100%→0%, 1.4s loop, ease-out | "Listening..." | Continuous ring pulse | VAD active, mic open |
| **processing** | Circle dims to 70% opacity, outer ring spins (rotation 0→360, 1.2s loop, linear) | "Thinking..." | Rotation on ring | Post-STT, awaiting LLM |
| **aria-speaking** | Circle fills with bg-muted instead of accent, mic icon replaced with speaker icon (20px) | "Aria is talking" | None | Button disabled while Aria speaks |
| **disabled** | Opacity 40%, no pointer events | — | None | Session init / error / ended |
| **error-mic** | Circle in state-error-bg, red border, ⚠ icon | "Mic unavailable" | Shake 2px × 2 (200ms, once) | getUserMedia denied |
| **error-connection** | Circle in state-error-bg, ⚠ icon | "Connection lost" | None | Network error |
| **loading** | Soft pulse on circle (opacity 0.4→0.8, 1s loop) | — | Opacity pulse | Session initializing |

#### Keyboard Interaction

| Key | Action |
|---|---|
| Space / Enter | Toggle listen (start/stop recording) |
| Escape | Cancel listening, return to default |

#### ARIA Annotation

```html
<button
  type="button"
  role="button"
  aria-label="Tap to talk to Aria"          <!-- dynamic: "Listening", "Aria is talking", etc. -->
  aria-pressed="false"                       <!-- true when listening -->
  aria-disabled="false"
  aria-live="polite"                         <!-- state changes announced -->
  aria-describedby="mic-status"
>
  <svg aria-hidden="true" ...><!-- mic icon --></svg>
</button>
<span id="mic-status" class="sr-only" aria-live="assertive">
  <!-- Dynamically updated: "Listening", "Aria is responding", "Connection lost" -->
</span>
```

#### Motion spec

- Listening ring: `@keyframes ring-pulse { 0% { transform: scale(1); opacity: 1; } 100% { transform: scale(1.2); opacity: 0; } }` — duration 1.4s, ease-out, infinite
- Processing ring: `@keyframes ring-spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }` — duration 1.2s, linear, infinite
- State transition (default → listening): icon cross-fade 120ms, ring appears 120ms
- Error shake: `@keyframes shake { 0%, 100% { transform: translateX(0); } 25% { transform: translateX(2px); } 75% { transform: translateX(-2px); } }` — 200ms, ease-in-out, 2 iterations

**Reduced motion:** All ring animations → instant static visual. No pulsing, no spinning. Use only color + icon changes to signal state.

---

### 3.2 Audio Waveform Visualization

#### Anatomy

```
         [Aria speaking state — organic bars]
   │  │         │   │
  ││  ││        ││  │   ││
  ││  ││  │    │││  ││  ││
──────────────────────────── ← baseline

  Width: 100% of portrait width (max 280px)
  Height: 4px (silence) → 40px (loud)
  Bars: 7 bars, equal spacing, rounded caps
```

#### States

| State | Visual | Notes |
|---|---|---|
| **idle** (Aria not speaking) | Hidden (height: 0, opacity: 0) | Fades out 200ms after speech ends |
| **aria-speaking** | Animated bars responding to TTS audio amplitude | 7 bars, organic height variation |
| **user-listening** | Not shown (waveform is Aria's voice visualizer only) | Mic button shows user state |
| **reduced-motion** | Static flat line: 7 bars all at 6px height, no animation | No animation via `prefers-reduced-motion` |

#### Visual spec

- 7 vertical bars
- Bar width: 3px
- Bar gap: 6px
- Bar radius: 2px (full round caps)
- Bar height range: 4px–40px, driven by audio amplitude (0–1 normalized)
- Color: `var(--color-accent-base)` at 65% opacity
- Animation: each bar has independent height transition at 80ms duration, `cubic-bezier(0.4, 0, 0.2, 1)`
- Container: `width: 100%; height: 48px; display: flex; align-items: center; justify-content: center;`
- Fade in/out: opacity transition 200ms when Aria starts/stops speaking

#### ARIA annotation

```html
<div
  role="img"
  aria-label="Audio waveform — Aria is speaking"
  aria-hidden="true"           <!-- visual decoration only; speech is the primary channel -->
>
  <!-- 7 bar divs animated via JS -->
</div>
```

**Note to frontend engineer:** Do not use aria-live here. The waveform is a visual echo of audio that is already directly accessible via the TTS voice. Do not double-announce.

---

### 3.3 Skill Tracker

#### Anatomy

```
Bottom strip, 48px height

┌────────────────────────────────────────────────┐
│                                                │
│  Cur  ●●○   Pre  ●○○   Dis  ○○○   Rec  ○○○   Spe  ○○○   · 7  │
│                                                │
└────────────────────────────────────────────────┘

Legend:
  ● filled dot (8px circle, accent color)
  ○ empty dot (8px circle, border only, border-default color)
  Cur/Pre/Dis/Rec/Spe = Curiosity/Presence/Disclosure/Recovery/Specificity
  · 7 = genuine moments count
```

#### Label visibility (discovery mechanic)

- **Default:** Labels hidden. Only dots visible. Skill identity unknown to user.
- **On hover (desktop):** Label appears with `opacity: 0 → 1`, `transform: translateY(4px) → translateY(0)`, 150ms ease-out. Positioned above the dot group.
- **On long-press (mobile, ≥600ms):** Same label appearance as hover.
- **On level-up:** Label appears briefly (2s) then fades — confirms the user just did something, but does not explain the system.
- **Screen reader:** Full label + level always exposed via sr-only. The discovery mechanic is visual only.

#### State Matrix (per skill)

| State | Visual |
|---|---|
| Level 0 | All 3 dots empty (○○○) |
| Level 1 | First dot filled (●○○) |
| Level 2 | Two dots filled (●●○) |
| Level 3 | All three filled (●●●) |
| Level-up transition | New dot: scale 0.6 → 1.4 → 1.0, opacity 0 → 1, 400ms spring-soft easing |

#### Genuine Moments Counter

- Text: `· {count}` — Inter 500, 13px, `text-secondary`
- On increment: number changes with a simple `opacity: 0 → 1` crossfade of the new number, 200ms
- No fanfare. No confetti. The number just changes.

#### ARIA annotation

```html
<nav aria-label="Conversation skills" role="region">
  <ul role="list">
    <li>
      <span class="sr-only">Curiosity: level 2 of 3</span>
      <div aria-hidden="true"><!-- 3 dots visual --></div>
      <span aria-hidden="true" class="skill-label">Cur</span>
    </li>
    <!-- ... repeat for 5 skills ... -->
  </ul>
  <div aria-label="Genuine moments this session: 7" role="status" aria-live="polite">
    <span aria-hidden="true">· 7</span>
    <span class="sr-only">7 genuine moments this session</span>
  </div>
</nav>
```

---

### 3.4 AI Disclosure Pill

Persistent throughout the session. Non-dismissable.

#### Anatomy

```
┌─────────────────────────────────────────────┐
│ ● You're talking with an AI character.   [?] │
└─────────────────────────────────────────────┘

● = 6px dot, accent color
[?] = 14px help icon, links to compliance/info page
Shape: pill (border-radius: full)
Background: bg-muted
Border: 1px border-muted
```

#### States

| State | Visual |
|---|---|
| Default | Visible, static |
| Hover on `[?]` | Tooltip: "Aria is an AI character, not a real person. Learn more." — fades in 150ms |
| Focus on `[?]` | 3px focus ring on the icon, offset 2px |

#### ARIA annotation

```html
<div role="status" aria-live="off" aria-atomic="true">
  <span aria-hidden="true" class="dot"></span>
  <span>You're talking with an AI character.</span>
  <a
    href="/about-aria"
    aria-label="Learn more about Aria being an AI character"
    rel="noopener"
  >
    <!-- ? icon -->
  </a>
</div>
```

**Note:** This element must never be hidden, `display: none`, or removed via JS. It is a compliance requirement (EU AI Act Article 5, Replika precedent).

---

### 3.5 End Session Modal

Triggered via "End session" link (bottom-right). Soft, not alarming. Aria doesn't "miss you" when you leave — that's a feature.

#### Anatomy

```
┌──────────────────────────────────────┐
│                                      │
│   End this conversation?             │  ← Fraunces, 18px, text-primary
│                                      │
│   Aria won't remember this session   │  ← Inter 400, 14px, text-muted
│   unless you save it.                │
│                                      │
│   [  End session  ]   [ Keep talking ]│  ← primary (destructive-adjacent) / ghost
│                                      │
└──────────────────────────────────────┘
```

#### States

| State | Notes |
|---|---|
| Default | Modal with shadow-xl, backdrop blur: 4px at 0.4 opacity |
| Loading (ending) | "End session" button shows spinner, disabled, "Ending..." label |
| Post-confirmation | Modal fades out 200ms, session state cleared, blank/thank-you screen |

#### Keyboard Interaction

| Key | Action |
|---|---|
| Escape | Close modal ("Keep talking") |
| Enter (when "End session" focused) | Confirm end |
| Tab | Cycles between two buttons |

Initial focus: "Keep talking" button (safe default — escape from accidental trigger)

#### ARIA annotation

```html
<dialog
  role="alertdialog"
  aria-modal="true"
  aria-labelledby="end-session-title"
  aria-describedby="end-session-desc"
>
  <h2 id="end-session-title">End this conversation?</h2>
  <p id="end-session-desc">Aria won't remember this session unless you save it.</p>
  <button type="button" autofocus>Keep talking</button>
  <button type="button">End session</button>
</dialog>
```

---

## 4. Aria Portrait — Three Mood Board Proposals

### 4.1 Option A: Painterly Editorial Illustration

**The Aria you'd find illustrating a profile in a literary magazine.**

Visual language: Oil pastel or gouache-adjacent digital painting. Muted, warm, rendered. The face is specific — she looks like an actual 24-year-old you could place in Alfama. Olive-toned skin (the Brazilian father's warmth), features with European softness, a specific gaze that reads as "considering, not open."

**Named visual references:**

- Karolis Strautniekas — portrait illustrations (moody, dark-ground editorial, muted palette). https://www.strautniekas.com/
- Anna Higgie — portrait work for The New Yorker, New York Times Magazine. Painterly, literary, specific faces. https://annahiggie.com/
- Victo Ngai editorial portraits — complex, layered, with emotional depth. https://victo-ngai.com/
- Claudia Carieri — painterly editorial portraits for European magazines.
- Reference aesthetic: any Granta or Paris Review cover portrait, 2018–2023.

**Palette for illustration:** warm neutrals from the token system. Aria's shirt/top: natural linen or muted sage. Background: the same bg-base warm off-white, so the illustration bleeds into the UI seamlessly.

**Strengths:**
- Highest "character feels real" factor — specific face = specific person
- Most "literary magazine" aligned — reinforces the vibe directly
- Arrestingly beautiful when executed well

**Weaknesses:**
- 5 expression variants require commissioned illustration work (not CSS-swappable at low cost)
- Hard to animate later (Live2D path would require rework)
- If execution quality drops, the specificity works against you

---

### 4.2 Option B: Stylized Contemporary Digital (Designer Recommendation)

**The Aria you'd find on a beautifully designed indie app.**

Visual language: Semi-stylized digital portrait. Not anime-otaku coded, not Western cartoon. The contemporary "desi-international" digital art aesthetic growing on ArtStation and Instagram — clean line confidence, selective depth, luminous skin rendering with 2–3 light sources, enough stylization that expression variants are clear and emotionally readable.

**Named visual references:**

- Ilya Kuvshinov — specifically his muted, mature work (not the oversaturated pieces). Masterful at expression through subtle feature shifts. https://www.kuvshinov-ilya.com/
- Loish (Lois van Baarle) — painterly semi-stylized portraits with warmth and depth. https://www.loish.net/
- Nate Lacoste — portrait studies that sit between realistic and stylized. https://www.artstation.com/natelacoste
- Wlop (Wang Ling) — the "digital painting + graphic novel" synthesis. https://wlop.artstation.com/
- Reference commissions: ArtStation tag "character portrait semi-realistic 2024" — abundant artists in $300–800 range

**Expression variant approach:** With this style, the 5 emotion states are delivered as 5 separate PNG/WebP files (or SVG if vector approach). The stylized nature means brow height, mouth position, and eye shape carry clear emotional signal even at portrait crop. Crossfade in CSS handles the transition.

**Strengths:**
- Clear expression readability — emotion states unambiguous even at portrait crop
- Directly compat with Live2D rigging for production path (stylized art = best for rigging)
- Artist availability: abundant in this style on commission platforms
- Strong brand identity — specific enough to be memorable, stylized enough to be ownable
- Scales to mobile without quality loss (no photorealism expectations)

**Weaknesses:**
- Less "literary magazine" and more "well-made app" (some product identity depends on this tradeoff)
- 5 commissions needed (or one artist delivering all 5 variants as a set — standard practice)

---

### 4.3 Option C: Minimal Line + Spot Color

**The Aria you'd encounter on a Taschen book cover.**

Visual language: Decisive single-weight line drawing, one or two flat spot colors, the face suggested rather than rendered. The New Yorker meets Matisse's late cut-outs. Aria's face is conveyed through a confident line — the tilt of a jaw, the specific angle of an eye — not through shading or volume. Color is used as editorial accent, not descriptive.

**Named visual references:**

- Christoph Niemann — line portraits, single-color editorial. His work for The New York Times Sunday Magazine. https://www.christophniemann.com/
- Jean Jullien — graphic, flat, wit-inflected illustration. https://www.jeanjullien.com/
- Malika Favre — precise single-color figurative work, Art Deco inflected. https://www.malikafavre.com/
- Riccardo Guasco — Matisse-influenced line + flat color portraits. https://www.riccardoguasco.com/
- Reference aesthetic: Penguin Modern Classics covers, The New Yorker 1950s–1970s cover portraits

**Expression variant approach:** The 5 states are genuinely minimal changes — one brow line shifted, mouth slightly open vs. closed, head tilt angle. This is the most elegant solution from a mechanical standpoint and the most intellectually aligned with Aria's character (she communicates through subtle register shifts, not theatrical faces).

**Strengths:**
- Most unique in the AI companion space — no competitor looks like this
- Aligned with the literary character bible — the restraint IS the characterization
- Cheapest to commission (line drawing = faster artist time)
- The "absence" of photorealism creates the Scott McCloud masking effect — users project onto a less-defined face

**Weaknesses:**
- Least immediately "warm" or inviting — may create higher drop-off on first interaction
- Expression states require careful execution to read clearly at small sizes
- No Live2D path — this style does not rig

---

### 4.4 Recommendation

**Option B for MVP production.** Option C as an A/B test variant after launch.

Option B gives you: clear emotion states (critical for a 5-state portrait system), Live2D compatibility (critical for production v1 path), strong brand ownable-ness, and a sufficiently contemporary-literary aesthetic when paired with the warm neutral palette. The tokens do the heavy lifting of "literary restraint" — Option B portrait doesn't need to carry that weight alone.

Option C is worth testing: if the product validates qualitatively, commission a minimal-line variant and A/B it on the onboarding screen. The masking effect could produce higher genuine connection scores per the Scott McCloud research.

---

## 5. Five Emotion State Illustration Specs

For each state: visual description for an illustrator briefing or AI image generation prompt.

### 5.1 Neutral (default state)

**Description:** Aria faces the viewer directly. Her expression is open and attentive — not smiling, not tense. There is light in her eyes (catch-lights at 10 o'clock and 2 o'clock positions). Her brows are at rest. Her mouth is relaxed, lips lightly closed or barely parted. The feeling: "I'm here. I'm listening. I haven't decided how I feel about you yet." Her posture is straight. If visible, her shoulders are level.

**Emotional register:** Present, neutral, observant.

**Key differentiator from other states:** She is not performing warmth. The gaze is direct, not soft. If this face were on a person walking down the street, you would think: "That person is thinking about something."

**AI-gen prompt base:** "Portrait of a 24-year-old woman, olive skin, warm neutral expression, direct gaze, catch-light in eyes, relaxed brows, mouth lightly closed, contemporary digital illustration, muted palette [warm off-white background], [chosen illustration style]"

---

### 5.2 Curious

**Description:** Her head tilts 4–6 degrees to her left (viewer's right). One brow — her left — rises fractionally. Her eyes are wider than neutral, slightly more open. There may be a subtle forward lean in the shoulders. Her mouth is neutral to very slightly parted — she is about to speak, or just stopped herself from speaking. The feeling: "Wait. Say more about that."

**Key feature:** The head tilt is the primary differentiator from neutral. It should be decisive enough to read at portrait crop (280px wide).

**AI-gen prompt delta:** "...head tilted slightly left, one eyebrow raised, eyes wide and engaged, slight forward lean in posture..."

---

### 5.3 Warm

**Description:** A genuine Duchenne smile — meaning: her cheeks lift, her eyes narrow slightly at the outer corners (crow's feet just forming), and the smile reaches the eyes. Her mouth is closed — no teeth. This is a real smile, not a performed one. It is the smile of someone who is genuinely pleased and a little surprised to be pleased. Her head is level or very slightly down-tilted (a softening). The feeling: "I like you. That's a real thing for me to say."

**Key constraint:** No open-mouth smile. No enthusiasm. The warmth is in the eye muscles, not the mouth width. This is a hard note for illustrators — specify explicitly: "Duchenne smile, eyes crinkling at corners, no teeth visible."

**AI-gen prompt delta:** "...genuine warm smile not showing teeth, eyes slightly crinkled at corners (Duchenne smile), cheeks raised, head level, warm light quality..."

---

### 5.4 Amused

**Description:** This is the nose-laugh moment. Her eyes are angled slightly downward — looking away from the viewer, toward the lower left, as if she just heard something and is taking a moment before responding. Her mouth shows the beginning of a real smile — asymmetric, slightly more pulled up on one side. There is no exaggerated expression. The feeling: "Okay that's actually funny. I wasn't going to laugh."

**Key differentiator from Warm:** The gaze breaks — she looks away. In the Warm state, she looks at you. In Amused, she looks away (the contained, private laugh). This distinction is subtle but characterful.

**AI-gen prompt delta:** "...eyes glancing slightly down and to the side (not making direct eye contact), asymmetric small smile, one corner of mouth raised more than the other, contained private amusement..."

---

### 5.5 Reserved

**Description:** Her mouth is completely neutral — neither smile nor frown. Her gaze is direct, steady, slightly more intense than neutral. Both brows are level but there is a very slight furrow — not a frown, just the presence of thought. This is the "I am deciding something about you" face. Eyes are fully open, pupils slightly smaller than curious state. The feeling: "I'm not going anywhere. I'm thinking."

**Critical constraint:** This must NOT read as cold, angry, or disappointed. The eyes must retain warmth (catch-lights present, not flat). The difference from neutral: more focused. More present in a specific, evaluative way. The distinction is in the slight brow furrow and the intensity of the gaze.

**AI-gen prompt delta:** "...neutral mouth, direct steady gaze, slight evaluative furrow in brows (not frown), eyes fully open and focused, not cold but thinking, retained catch-lights in eyes..."

---

### 5.6 Expression Transition Spec

CSS-only implementation for Path A (static illustrations):

```css
.aria-portrait-state {
  position: absolute;
  top: 0; left: 0;
  width: 100%; height: 100%;
  opacity: 0;
  transition: opacity 200ms cubic-bezier(0.0, 0.0, 0.2, 1.0);
}

.aria-portrait-state.active {
  opacity: 1;
}

@media (prefers-reduced-motion: reduce) {
  .aria-portrait-state {
    transition: none;
  }
}
```

Each state is a separate `<img>` or `<picture>` element. Only the active state has `opacity: 1`. Crossfade is handled by the transition on opacity. The portrait container has `position: relative` and `overflow: hidden`. All images are pre-loaded.

---

## 6. Onboarding Flow Wireframes

Three screens. No tutorial. No skip. 0 friction to reach the conversation.

### Screen 1: Introduction

```
╔═══════════════════════════════════════════╗
║                                           ║
║                                           ║
║          [Aria portrait — neutral]        ║
║            (240px, centered)              ║
║                                           ║
║                                           ║
║          You're about to talk             ║
║               to Aria.                   ║
║                                           ║
║      She practices conversation with      ║
║      you. No scripts. No lessons.         ║
║      Just talking.                        ║
║                                           ║
║                                           ║
║   ┌─────────────────────────────────┐     ║
║   │  I'm 17 or older — let's start  │     ║
║   └─────────────────────────────────┘     ║
║                                           ║
║     Already talked to Aria? Continue.     ║
║                                           ║
╚═══════════════════════════════════════════╝
```

**Copy rationale:** "No scripts. No lessons. Just talking." — this is the anti-Duolingo statement. Positions the product honestly. "Already talked to Aria? Continue." — handles returning sessions in the onboarding frame.

**Age gate:** The CTA button IS the age confirmation. Clicking "I'm 17 or older — let's start" is the age acknowledgment. No checkbox, no date-of-birth entry (reduces friction; legal weight is equivalent for MVP). Store: `localStorage.setItem('aria_age_confirmed', 'true')`.

**Compliance:** 17+ age gate from BUILD_BRIEF §8. Stored in localStorage. Re-shown after localStorage clear only.

**Typography:** Headline "You're about to talk to Aria." in Fraunces 300, 28px. Body text Inter 400, 15px, text-secondary. CTA button: Inter 500, 15px, text-on-accent.

---

### Screen 2: AI Disclosure

```
╔═══════════════════════════════════════════╗
║                                           ║
║                                           ║
║           Before you begin.               ║
║                                           ║
║                                           ║
║   Aria is an AI character, not a real     ║
║   person. She's designed to help you      ║
║   practice real-world conversation.       ║
║                                           ║
║   ─────────────────────────────────────   ║
║                                           ║
║   If you're going through something       ║
║   difficult:                              ║
║                                           ║
║   iCall (India)  9152987821               ║
║   AASRA           9820466726             ║
║   International  findahelpline.com        ║
║                                           ║
║   ─────────────────────────────────────   ║
║                                           ║
║   ┌─────────────────────────────────┐     ║
║   │          I understand           │     ║
║   └─────────────────────────────────┘     ║
║                                           ║
╚═══════════════════════════════════════════╝
```

**Copy rationale:** "Not a real person" is the exact wording required (EU AI Act Article 5). Crisis resources must be shown before first interaction — BUILD_BRIEF §8. The horizontal rules create section breaks that make the resource numbers scannable.

**Storage:** `localStorage.setItem('aria_ai_disclosure_accepted', 'true')`. Only shown once per device. Always accessible via "What is this?" link.

**Typography:** Headline "Before you begin." in Fraunces 300 italic, 22px. Body Inter 400, 15px. Resources: Inter 500, 14px, monospace for numbers (for readability). Crisis number links: `tel:` protocol.

---

### Screen 3: First Conversation (No explicit UI transition)

```
╔═══════════════════════════════════════════╗
║                                           ║
║  ● You're talking with an AI character.  ║  ← disclosure pill, appears
║                                           ║
║                                           ║
║          [Aria portrait — neutral]        ║
║                                           ║
║                                           ║
║   "Hey. I don't know you yet.             ║
║    Tell me one thing about your day       ║
║    that wasn't on a screen."              ║
║                                           ║
║        ～～～～～～～～～～～～～           ║  ← waveform appears as she speaks
║                                           ║
║           [ mic button ]                  ║
║           "Tap to talk"                   ║
║                                           ║
║   ○○○  ○○○  ○○○  ○○○  ○○○    · 0         ║  ← skill tracker appears, all empty
║                                           ║
║                      End session   What is this? ║
╚═══════════════════════════════════════════╝
```

**Transition from Screen 2:** "I understand" button fades the disclosure screen out (200ms). Main conversation screen fades in (200ms). The first session begins — ElevenLabs starts the audio, Aria's portrait renders, the waveform appears when audio plays.

**No tutorial.** The skill tracker appears with all dots empty. No labels. No explanation. The user discovers it.

---

## 7. Main Conversation Screen — Full Spec

### 7.1 Wireframe

```
╔═══════════════════════════════════════════════════════╗
║                                                       ║
║  ┌──────────────────────────────────────────────────┐ ║
║  │ ● You're talking with an AI character.      [?]  │ ║  top bar, fixed, 32px
║  └──────────────────────────────────────────────────┘ ║
║                                                       ║
║                                                       ║  24px gap
║               ┌─────────────────┐                    ║
║               │                 │                    ║
║               │  Aria portrait  │                    ║  280px × 280px
║               │  (emotion state │                    ║  centered
║               │   swaps here)   │                    ║
║               │                 │                    ║
║               └─────────────────┘                    ║
║                                                       ║  16px gap
║         ～～～～～～～～～～～～～～～～              ║  waveform, 48px height
║                                                       ║  8px gap
║   "Tell me one thing about your day                   ║
║    that wasn't on a screen."                         ║  Aria's last line
║                                                       ║  Fraunces italic, 17px, text-secondary
║                                                       ║  max 2 lines, truncates
║                                                       ║  24px gap
║               ┌─────────────────┐                    ║
║               │  [ mic icon ]   │                    ║  72px circle, accent
║               └─────────────────┘                    ║
║               "Tap to talk"                           ║  label, 13px, text-muted
║                                                       ║  24px gap
║  ────────────────────────────────────────────────     ║  1px border-muted
║                                                       ║
║  ●●○    ●○○    ○○○    ○○○    ○○○              · 7    ║  skill strip, 48px
║  Cur    Pre    Dis    Rec    Spe                      ║  (labels hidden by default)
║                                                       ║
╚═══════════════════════════════════════════════════════╝
║  End session                    What is this?         ║  footer links, outside card
```

### 7.2 Layout Rules

- **Max width:** 420px centered (desktop shows it as a centered column, not full-width)
- **Mobile:** 100vw, 16px horizontal padding, safe area insets respected
- **Portrait aspect ratio:** 1:1, rendered as rounded square (radius: 16px) with shadow-portrait
- **Aria transcript:** 2-line max, truncated with ellipsis, italic Fraunces, text-secondary — communicates "she just said this" without being a full chat log (voice-first: no persistent transcript in MVP)
- **Vertical flow:** All elements stack center-aligned. No sidebars. No columns.
- **Background:** bg-base (warm off-white). No texture. No pattern. Just the warmth of the color.

### 7.3 Responsive Behavior

| Breakpoint | Changes |
|---|---|
| < 375px | Portrait shrinks to 240px. Mic button stays 72px. |
| 375–420px | Full-size portrait (280px). Standard layout. |
| > 420px | Content max-width 420px centered. Background shows bg-base edge-to-edge, or a subtle centered shadow on the content column. |
| Landscape mobile | Portrait reduces to 160px. Skill tracker moves to right sidebar. Mic button stays centered. |

---

## 8. Graduation Ceremony UI Spec

Triggered at 50 genuine moments. Not in MVP but designed for production awareness.

### 8.1 Sequence

**Beat 1 — Portal in (0–600ms)**
Full-screen overlay fades in over the main conversation screen. Background: bg-base at 96% opacity. Backdrop filter: none (preserve performance). The overlay does not blur the content behind — it simply covers it, a page being turned.

**Beat 2 — Aria portrait transition (600–1200ms)**
Aria's portrait, already in the "warm" state (the UI has been tracking her emotion state), crossfades to a slightly larger version: 320px, soft warm glow behind (a subtle radial gradient in accent-subtle, 200px radius, 0.4 opacity).

**Beat 3 — Type-out begins (1200–6000ms)**
Aria's graduation line appears character by character. Speed: 28 characters per second (fast enough to feel intentional, slow enough to be read as spoken). Font: Fraunces 300 italic, 22px/32px, text-primary.

```
Exact text (from BUILD_BRIEF):

"Look — I think you're ready for this in real life.
Try it. Go talk to someone today.
Come back if you want, but you don't need me for this anymore."
```

Display: left-aligned within centered 340px column. The typing cursor (a 2px warm-accent vertical bar) appears after the last character during the reveal, then disappears.

**Beat 4 — IRL challenge card rises (6200ms)**
A card slides up from below (transform: translateY(60px) → translateY(0), opacity 0 → 1, 400ms spring-soft easing):

```
┌───────────────────────────────────────────┐
│                                           │
│   Your challenge for this week:           │
│   Fraunces 500, 14px, accent-on-light-bg  │
│                                           │
│   Have a genuine 5-minute conversation    │
│   with a stranger. Come back and tell     │
│   Aria how it went.                       │
│                                           │
│   [ I'll do it ]     [ Not yet ]          │
│                                           │
└───────────────────────────────────────────┘
```

**Beat 5 — After CTA**
- "I'll do it": Aria's portrait transitions to the amused state (the closest to "I believe you"). Screen fades. Session ends. Success state.
- "Not yet": Card dismisses (slides back down, 250ms). Returns to main conversation screen. Aria continues.

### 8.2 Accessibility

- `aria-live="assertive"` on the type-out container — each completed sentence announced to screen reader
- `prefers-reduced-motion`: show full text immediately, no type-out, no slides
- Focus management: when graduation overlay appears, focus moves to the overlay
- ESC: no dismiss (graduation is not an alert — it is a moment)

---

## 9. Tailwind 4 + shadcn/ui v4 Implementation Snippets

### 9.1 Tailwind 4 CSS-First Theme Extension

In `app/globals.css` (or `styles/globals.css`):

```css
@import "tailwindcss";

@theme {
  /* === COLORS === */
  --color-bg-base: oklch(0.97 0.008 78);
  --color-bg-surface: oklch(0.99 0.004 78);
  --color-bg-muted: oklch(0.93 0.014 78);
  --color-bg-elevated: oklch(1.00 0.000 0);

  --color-border-default: oklch(0.88 0.012 78);
  --color-border-muted: oklch(0.92 0.010 78);

  --color-text-primary: oklch(0.22 0.022 60);
  --color-text-secondary: oklch(0.42 0.020 68);
  --color-text-muted: oklch(0.56 0.016 72);
  --color-text-on-accent: oklch(0.99 0.004 78);

  /* Accent — terracotta (default; swap var for other options) */
  --color-accent: oklch(0.62 0.13 43);
  --color-accent-light: oklch(0.76 0.09 43);
  --color-accent-subtle: oklch(0.91 0.05 43);
  --color-accent-text: oklch(0.54 0.14 43); /* for text ON light bg, AA compliant */

  --color-error: oklch(0.52 0.18 27);
  --color-error-bg: oklch(0.95 0.03 27);
  --color-success: oklch(0.54 0.14 148);
  --color-success-bg: oklch(0.95 0.03 148);

  /* === TYPOGRAPHY === */
  --font-sans: "Inter Variable", "Inter", -apple-system, BlinkMacSystemFont, system-ui, sans-serif;
  --font-serif: "Fraunces", Georgia, "Times New Roman", serif;
  --font-mono: "JetBrains Mono Variable", "JetBrains Mono", monospace;

  --text-xs: 0.6875rem;     /* 11px */
  --text-sm: 0.8125rem;     /* 13px */
  --text-base: 0.9375rem;   /* 15px */
  --text-md: 1.0625rem;     /* 17px */
  --text-lg: 1.375rem;      /* 22px */
  --text-xl: 1.75rem;       /* 28px */
  --text-2xl: 2.25rem;      /* 36px */

  --leading-tight: 1.3;
  --leading-snug: 1.4;
  --leading-normal: 1.5;
  --leading-relaxed: 1.65;

  /* === SPACING === */
  --spacing-0: 0px;
  --spacing-1: 4px;
  --spacing-2: 8px;
  --spacing-3: 12px;
  --spacing-4: 16px;
  --spacing-5: 20px;
  --spacing-6: 24px;
  --spacing-8: 32px;
  --spacing-10: 40px;
  --spacing-12: 48px;
  --spacing-16: 64px;
  --spacing-20: 80px;
  --spacing-24: 96px;

  /* === RADII === */
  --radius-none: 0px;
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 12px;
  --radius-xl: 20px;
  --radius-2xl: 28px;
  --radius-full: 9999px;

  /* === SHADOWS === */
  --shadow-sm: 0 1px 3px oklch(0.15 0.02 60 / 0.06);
  --shadow-md: 0 2px 8px oklch(0.15 0.02 60 / 0.08), 0 1px 3px oklch(0.15 0.02 60 / 0.04);
  --shadow-lg: 0 8px 32px oklch(0.15 0.02 60 / 0.12), 0 2px 8px oklch(0.15 0.02 60 / 0.05);
  --shadow-xl: 0 16px 56px oklch(0.15 0.02 60 / 0.16), 0 4px 16px oklch(0.15 0.02 60 / 0.08);
  --shadow-portrait: 0 4px 24px oklch(0.15 0.02 60 / 0.10);

  /* === MOTION === */
  --duration-fast: 120ms;
  --duration-base: 200ms;
  --duration-slow: 350ms;
  --duration-portrait: 200ms;

  --ease-out: cubic-bezier(0.0, 0.0, 0.2, 1.0);
  --ease-in-out: cubic-bezier(0.4, 0.0, 0.2, 1.0);
  --ease-spring-soft: cubic-bezier(0.34, 1.1, 0.64, 1.0);

  /* === LAYOUT === */
  --max-w-conversation: 420px;
  --portrait-size: 280px;
  --portrait-size-sm: 240px;
  --mic-size: 72px;
  --skill-strip-h: 48px;
  --disclosure-h: 32px;
}

/* === DARK MODE === */
@media (prefers-color-scheme: dark) {
  @theme {
    --color-bg-base: oklch(0.13 0.016 60);
    --color-bg-surface: oklch(0.17 0.016 60);
    --color-bg-muted: oklch(0.21 0.018 62);
    --color-bg-elevated: oklch(0.22 0.015 60);
    --color-border-default: oklch(0.30 0.016 62);
    --color-border-muted: oklch(0.26 0.014 62);
    --color-text-primary: oklch(0.93 0.010 78);
    --color-text-secondary: oklch(0.72 0.012 72);
    --color-text-muted: oklch(0.54 0.012 72);
    --color-accent-subtle: oklch(0.24 0.07 43);
  }
}

/* === REDUCED MOTION === */
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}

/* === BASE LAYER === */
@layer base {
  html {
    font-family: var(--font-sans);
    background-color: var(--color-bg-base);
    color: var(--color-text-primary);
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
  }

  :focus-visible {
    outline: 3px solid var(--color-accent);
    outline-offset: 3px;
  }

  ::selection {
    background-color: var(--color-accent-subtle);
    color: var(--color-text-primary);
  }
}
```

---

### 9.2 Voice Button Component (TSX)

```tsx
// components/aria/voice-button.tsx
"use client";

import { cn } from "@/lib/utils";
import { Mic, Volume2, AlertTriangle, Loader2 } from "lucide-react";

type VoiceButtonState =
  | "default"
  | "listening"
  | "processing"
  | "aria-speaking"
  | "error-mic"
  | "error-connection"
  | "disabled"
  | "loading";

interface VoiceButtonProps {
  state: VoiceButtonState;
  onToggle: () => void;
  className?: string;
}

const stateConfig: Record<
  VoiceButtonState,
  { label: string; ariaLabel: string; ariaPressed: boolean }
> = {
  default: {
    label: "Tap to talk",
    ariaLabel: "Tap to talk to Aria",
    ariaPressed: false,
  },
  listening: {
    label: "Listening...",
    ariaLabel: "Listening. Tap to stop.",
    ariaPressed: true,
  },
  processing: {
    label: "Thinking...",
    ariaLabel: "Aria is thinking",
    ariaPressed: false,
  },
  "aria-speaking": {
    label: "Aria is talking",
    ariaLabel: "Aria is speaking. Wait for her to finish.",
    ariaPressed: false,
  },
  "error-mic": {
    label: "Mic unavailable",
    ariaLabel: "Microphone is unavailable. Check your browser permissions.",
    ariaPressed: false,
  },
  "error-connection": {
    label: "Connection lost",
    ariaLabel: "Connection lost. Check your internet connection.",
    ariaPressed: false,
  },
  disabled: {
    label: "",
    ariaLabel: "Voice input unavailable",
    ariaPressed: false,
  },
  loading: {
    label: "",
    ariaLabel: "Loading conversation",
    ariaPressed: false,
  },
};

export function VoiceButton({ state, onToggle, className }: VoiceButtonProps) {
  const config = stateConfig[state];
  const isInteractive = state === "default" || state === "listening";
  const isError = state === "error-mic" || state === "error-connection";

  return (
    <div className={cn("flex flex-col items-center gap-2", className)}>
      {/* Outer ring container */}
      <div className="relative flex items-center justify-center w-24 h-24">
        {/* Animated ring — only shown on listening/processing */}
        {state === "listening" && (
          <span
            className="absolute inset-0 rounded-full animate-ring-pulse"
            aria-hidden="true"
            style={{
              background: "var(--color-accent)",
              opacity: 0.2,
            }}
          />
        )}
        {state === "processing" && (
          <span
            className="absolute inset-0 rounded-full border-2 border-t-transparent animate-ring-spin"
            aria-hidden="true"
            style={{ borderColor: "var(--color-accent)" }}
          />
        )}

        {/* Core button */}
        <button
          type="button"
          onClick={onToggle}
          disabled={!isInteractive}
          aria-label={config.ariaLabel}
          aria-pressed={config.ariaPressed}
          aria-disabled={!isInteractive}
          className={cn(
            // Base
            "relative z-10 flex items-center justify-center",
            "w-[72px] h-[72px] rounded-full",
            "transition-all duration-[var(--duration-base)] ease-[var(--ease-out)]",
            // Default / listening
            isInteractive && [
              "bg-[var(--color-accent)]",
              "hover:bg-[var(--color-accent-light)]",
              "active:scale-95",
              "shadow-[var(--shadow-md)]",
            ],
            // Processing / aria-speaking
            state === "processing" && "bg-[var(--color-accent)] opacity-70 cursor-wait",
            state === "aria-speaking" && "bg-[var(--color-bg-muted)] cursor-not-allowed",
            // Error
            isError && [
              "bg-[var(--color-error-bg)]",
              "border-2 border-[var(--color-error)]",
              "animate-shake",
            ],
            // Disabled / loading
            (state === "disabled" || state === "loading") &&
              "bg-[var(--color-bg-muted)] opacity-40 cursor-not-allowed",
          )}
        >
          {/* Icon */}
          {(state === "default" || state === "listening") && (
            <Mic
              size={28}
              className="text-[var(--color-text-on-accent)]"
              aria-hidden="true"
            />
          )}
          {state === "processing" && (
            <Loader2
              size={24}
              className="text-[var(--color-text-on-accent)] animate-spin"
              aria-hidden="true"
            />
          )}
          {state === "aria-speaking" && (
            <Volume2
              size={24}
              className="text-[var(--color-text-secondary)]"
              aria-hidden="true"
            />
          )}
          {isError && (
            <AlertTriangle
              size={24}
              className="text-[var(--color-error)]"
              aria-hidden="true"
            />
          )}
        </button>
      </div>

      {/* Label */}
      {config.label && (
        <span
          className="text-[var(--text-sm)] font-sans text-[var(--color-text-muted)]"
          aria-hidden="true"
        >
          {config.label}
        </span>
      )}

      {/* Screen-reader live region */}
      <span
        role="status"
        aria-live="assertive"
        className="sr-only"
      >
        {config.ariaLabel}
      </span>
    </div>
  );
}
```

---

### 9.3 Aria Portrait Component (TSX)

```tsx
// components/aria/aria-portrait.tsx
"use client";

import Image from "next/image";
import { cn } from "@/lib/utils";

export type EmotionState = "neutral" | "curious" | "warm" | "amused" | "reserved";

interface AriaPortraitProps {
  emotionState: EmotionState;
  size?: number;
  className?: string;
}

// Map emotion states to illustration files
const portraitSrc: Record<EmotionState, string> = {
  neutral: "/aria/aria-neutral.webp",
  curious: "/aria/aria-curious.webp",
  warm: "/aria/aria-warm.webp",
  amused: "/aria/aria-amused.webp",
  reserved: "/aria/aria-reserved.webp",
};

const emotionAltText: Record<EmotionState, string> = {
  neutral: "Aria — present and attentive",
  curious: "Aria — interested, leaning in",
  warm: "Aria — warm, a genuine smile",
  amused: "Aria — amused, looking away with a quiet laugh",
  reserved: "Aria — thinking, steady gaze",
};

export function AriaPortrait({
  emotionState,
  size = 280,
  className,
}: AriaPortraitProps) {
  return (
    <div
      className={cn(
        "relative overflow-hidden rounded-[16px]",
        "shadow-[var(--shadow-portrait)]",
        className,
      )}
      style={{ width: size, height: size }}
      role="img"
      aria-label={emotionAltText[emotionState]}
    >
      {(Object.keys(portraitSrc) as EmotionState[]).map((state) => (
        <Image
          key={state}
          src={portraitSrc[state]}
          alt=""                      // decorative — parent div has aria-label
          aria-hidden="true"
          fill
          priority={state === "neutral"}
          className={cn(
            "object-cover absolute inset-0",
            "transition-opacity duration-[200ms] ease-[var(--ease-out)]",
            emotionState === state ? "opacity-100" : "opacity-0",
          )}
          sizes={`${size}px`}
        />
      ))}
    </div>
  );
}
```

---

### 9.4 Skill Tracker Component (TSX)

```tsx
// components/aria/skill-tracker.tsx
"use client";

import { useState } from "react";
import { cn } from "@/lib/utils";

interface SkillLevel {
  id: "curiosity" | "presence" | "disclosure" | "recovery" | "specificity";
  shortLabel: string;
  fullLabel: string;
  level: 0 | 1 | 2 | 3;
}

interface SkillTrackerProps {
  skills: SkillLevel[];
  genuineMoments: number;
  className?: string;
}

function SkillDots({ level, skillId }: { level: number; skillId: string }) {
  return (
    <div className="flex gap-1" aria-hidden="true">
      {[1, 2, 3].map((dot) => (
        <span
          key={dot}
          className={cn(
            "w-2 h-2 rounded-full transition-all duration-[400ms] ease-[var(--ease-spring-soft)]",
            dot <= level
              ? "bg-[var(--color-accent)]"
              : "border border-[var(--color-border-default)] bg-transparent",
          )}
          data-skill={skillId}
          data-filled={dot <= level}
        />
      ))}
    </div>
  );
}

export function SkillTracker({
  skills,
  genuineMoments,
  className,
}: SkillTrackerProps) {
  const [hoveredSkill, setHoveredSkill] = useState<string | null>(null);

  return (
    <nav
      aria-label="Conversation skills"
      className={cn(
        "flex items-center justify-between px-4",
        "h-[var(--skill-strip-h)] border-t border-[var(--color-border-muted)]",
        className,
      )}
    >
      <ul role="list" className="flex items-center gap-4">
        {skills.map((skill) => (
          <li
            key={skill.id}
            className="flex flex-col items-center gap-0.5 relative"
            onMouseEnter={() => setHoveredSkill(skill.id)}
            onMouseLeave={() => setHoveredSkill(null)}
          >
            {/* Screen-reader text — always present */}
            <span className="sr-only">
              {skill.fullLabel}: level {skill.level} of 3
            </span>

            {/* Tooltip — visual only, hidden by default */}
            <span
              className={cn(
                "absolute -top-7 left-1/2 -translate-x-1/2",
                "text-[var(--text-xs)] font-sans text-[var(--color-text-muted)]",
                "whitespace-nowrap px-2 py-1 rounded-[var(--radius-sm)]",
                "bg-[var(--color-bg-muted)] border border-[var(--color-border-muted)]",
                "transition-opacity duration-150 ease-[var(--ease-out)]",
                hoveredSkill === skill.id ? "opacity-100" : "opacity-0",
                "pointer-events-none",
              )}
              aria-hidden="true"
            >
              {skill.fullLabel}
            </span>

            <SkillDots level={skill.level} skillId={skill.id} />

            {/* Short label — hidden until hover */}
            <span
              className={cn(
                "text-[var(--text-xs)] font-sans uppercase tracking-[0.08em]",
                "text-[var(--color-text-muted)]",
                "transition-opacity duration-150",
                hoveredSkill === skill.id ? "opacity-100" : "opacity-0",
              )}
              aria-hidden="true"
            >
              {skill.shortLabel}
            </span>
          </li>
        ))}
      </ul>

      {/* Genuine moments counter */}
      <div
        className="flex items-center gap-1"
        aria-label={`${genuineMoments} genuine moments this session`}
      >
        <span
          className="text-[var(--text-sm)] font-sans text-[var(--color-text-muted)]"
          aria-hidden="true"
        >
          · {genuineMoments}
        </span>
        <span className="sr-only">
          {genuineMoments} genuine moments this session
        </span>
      </div>
    </nav>
  );
}
```

---

### 9.5 shadcn/ui Theme Override (components.json + globals)

In `components.json`:
```json
{
  "$schema": "https://ui.shadcn.com/schema.json",
  "style": "new-york",
  "rsc": true,
  "tsx": true,
  "tailwind": {
    "config": "",
    "css": "app/globals.css",
    "baseColor": "neutral",
    "cssVariables": true
  },
  "aliases": {
    "components": "@/components",
    "utils": "@/lib/utils",
    "ui": "@/components/ui",
    "lib": "@/lib",
    "hooks": "@/hooks"
  }
}
```

shadcn maps its `--primary` to our accent. In `globals.css` after `@theme`:

```css
/* shadcn/ui variable mapping */
:root {
  --background: var(--color-bg-base);
  --foreground: var(--color-text-primary);
  --card: var(--color-bg-surface);
  --card-foreground: var(--color-text-primary);
  --popover: var(--color-bg-elevated);
  --popover-foreground: var(--color-text-primary);
  --primary: var(--color-accent);
  --primary-foreground: var(--color-text-on-accent);
  --secondary: var(--color-bg-muted);
  --secondary-foreground: var(--color-text-secondary);
  --muted: var(--color-bg-muted);
  --muted-foreground: var(--color-text-muted);
  --accent: var(--color-accent-subtle);
  --accent-foreground: var(--color-accent-text);
  --destructive: var(--color-error);
  --destructive-foreground: var(--color-text-on-accent);
  --border: var(--color-border-default);
  --input: var(--color-border-default);
  --ring: var(--color-accent);
  --radius: var(--radius-lg);
}
```

---

### 9.6 Keyframe Animations (globals.css addition)

```css
@keyframes ring-pulse {
  0% { transform: scale(1); opacity: 0.8; }
  100% { transform: scale(1.25); opacity: 0; }
}

@keyframes ring-spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  20%       { transform: translateX(-2px); }
  40%       { transform: translateX(2px); }
  60%       { transform: translateX(-2px); }
  80%       { transform: translateX(2px); }
}

@keyframes dot-pop {
  0%   { transform: scale(0.6); opacity: 0; }
  60%  { transform: scale(1.4); }
  100% { transform: scale(1.0); opacity: 1; }
}

@keyframes loading-pulse {
  0%, 100% { opacity: 0.4; }
  50%       { opacity: 0.8; }
}

/* Apply animations via Tailwind utilities */
@layer utilities {
  .animate-ring-pulse {
    animation: ring-pulse 1.4s ease-out infinite;
  }
  .animate-ring-spin {
    animation: ring-spin 1.2s linear infinite;
  }
  .animate-shake {
    animation: shake 200ms ease-in-out 2;
  }
  .animate-dot-pop {
    animation: dot-pop 400ms cubic-bezier(0.34, 1.1, 0.64, 1.0) forwards;
  }
  .animate-loading-pulse {
    animation: loading-pulse 1.2s ease-in-out infinite;
  }
}
```

---

## 10. Accessibility Checklist (WCAG 2.2 AA)

### 10.1 Color Contrast

| Element | Color (on bg-base) | Contrast | AA |
|---|---|---|---|
| text-primary on bg-base | oklch(0.22 / 0.97) | ~13.4:1 | Pass AAA |
| text-secondary on bg-base | oklch(0.42 / 0.97) | ~5.2:1 | Pass AA |
| text-muted on bg-base | oklch(0.56 / 0.97) | ~3.9:1 | Pass for large text / UI chrome only. Do NOT use for body text. |
| accent-text on bg-base (terracotta) | oklch(0.54 / 0.97) | ~4.9:1 | Pass AA |
| text-on-accent on accent-base | oklch(0.99 / 0.62) | ~7.2:1 | Pass AA |
| text-muted on bg-muted | ~4.1:1 | Pass for non-text |
| AI disclosure text on bg-muted | text-secondary | ~4.8:1 | Pass AA |

**Action for frontend engineer:** Run `postcss-oklch` for hex fallback + `wcag-contrast` package in CI to catch regressions.

### 10.2 Interactive Target Size (WCAG 2.5.5 / 2.5.8)

| Element | Size | Notes |
|---|---|---|
| Mic button | 72×72px | Exceeds 44px minimum |
| End session link | min 44×44px touch target (CSS padding) | Link text is small — use padding to achieve target |
| What is this? link | min 44×44px touch target | Same |
| Skill tracker dots (hover area) | Per-skill li: min 40px wide × 48px tall | The li is the hover target, not the 8px dot |
| AI disclosure [?] icon | 44×44px touch target via padding | 14px icon, padded |
| Modal buttons | 48px tall minimum | Sufficient width by content |

### 10.3 Keyboard Navigation Order

Tab order for the main conversation screen:
1. AI disclosure `[?]` link
2. Mic button
3. End session link
4. What is this? link

Skill tracker is navigable via arrow keys (left/right) once focused, but is also fully exposed via `aria-label` without requiring navigation.

Onboarding:
1. CTA button (Screen 1)
2. Crisis resource links (Screen 2)
3. "I understand" button (Screen 2)

### 10.4 Screen Reader Narrative (linear reading order)

Verify the page makes sense as a linear text stream:

```
[persistent status]: You're talking with an AI character. [link: Learn more]
[image]: Aria — present and attentive
[status, live]: [state label changes: "Aria is speaking" / "Listening" / etc.]
[button]: Tap to talk to Aria
[nav, "Conversation skills"]:
  Curiosity: level 2 of 3
  Presence: level 1 of 3
  Disclosure: level 0 of 3
  Recovery: level 0 of 3
  Specificity: level 0 of 3
  [status, live]: 7 genuine moments this session
[link]: End session
[link]: What is this?
```

This narrative must make complete sense without seeing the visual.

### 10.5 ARIA Live Regions

| Region | Element | `aria-live` level | Notes |
|---|---|---|---|
| Voice button state | `#mic-status` span | `assertive` | State changes (listening/processing) need immediate announcement |
| Genuine moments counter | div in skill tracker | `polite` | Non-urgent increment |
| Aria's transcript | transcript div | `polite` | New line from Aria |
| End session modal | `<dialog>` | Implicit from role | Focus moves to dialog on open |
| Graduation type-out | container div | `assertive` | Major state change |
| AI disclosure | status div | `off` | Persistent, not dynamic |

### 10.6 Reduced Motion Contract (complete)

| Animation | Normal | Reduced motion |
|---|---|---|
| Portrait crossfade | 200ms opacity | 0ms (instant swap) |
| Mic listening ring | 1.4s pulse loop | Static ring, no animation |
| Mic processing ring | 1.2s spin | Static ring, no spin |
| Skill dot level-up | 400ms pop | Instant fill |
| Genuine moments counter | 200ms number fade | Instant number change |
| Waveform bars | 80ms height transition | Static flat line (4px) |
| Onboarding screen transitions | 200ms fade | Instant |
| Graduation type-out | Character-by-character | Full text at once |
| IRL challenge card | 400ms slide up | Instant appearance |
| End session modal | 200ms fade in | Instant |

**Implementation:** All handled by `@media (prefers-reduced-motion: reduce)` global rule in design-tokens.css + component-level conditional animation class application.

### 10.7 Semantic HTML Checklist

- [ ] Page has a `<main>` landmark
- [ ] AI disclosure uses `role="status"` not a decorative `div`
- [ ] Mic button is a `<button>`, not a `<div>` with onClick
- [ ] Aria portrait is a `<div role="img" aria-label="...">` with all state images `aria-hidden`
- [ ] Skill tracker is a `<nav>` with `aria-label`
- [ ] Modal uses the `<dialog>` element with `role="alertdialog"`
- [ ] Crisis resource phone numbers are `<a href="tel:...">` links
- [ ] Fraunces italic transcript text is not conveying information via font style alone
- [ ] Color is not the sole differentiator for skill levels (dot fill vs. border is shape + color combined)
- [ ] Error states communicate error in text (not icon-only) via `aria-label`

### 10.8 Form Labels

Onboarding has no form fields beyond the single-button age gate. If a date-of-birth field is added in future:
- Visible `<label>` required (or `aria-label` if design-constrained)
- Error messages via `aria-describedby` pointing to an `aria-live="assertive"` error container
- Invalid state: `aria-invalid="true"` on the input

---

## 11. Open Questions for Engineering

1. **Waveform audio data:** The waveform bars need real-time amplitude data from the ElevenLabs audio stream. How does the frontend access raw PCM amplitude data from the ElevenLabs browser SDK during playback? Can the SDK expose an `AnalyserNode` from the Web Audio API, or does amplitude need to come via a callback from the ElevenLabs event system? Design assumes 60fps amplitude updates via `requestAnimationFrame`.

2. **Portrait preloading:** All 5 portrait states should be preloaded before the conversation starts. Confirm approach: `<link rel="preload" as="image" ...>` in `<head>` for all 5 WebP files, or `priority` prop on all 5 Next.js `<Image>` components (which adds preload headers). The second causes 5 parallel fetches on first load — confirm with perf budget.

3. **Skill tracker data binding:** The `SkillTracker` component takes a `skills` array prop. Who updates this array, and at what frequency? If the ML brain updates skill levels per turn, the frontend receives an event (WebSocket or polling), and should update with React state. The dot-pop animation should trigger ONLY when a level increments (not on initial render). Suggest: track previous level in a ref and compare, then conditionally apply `animate-dot-pop` class.

4. **Genuine moments — increment event:** What event does the frontend receive when a genuine moment is scored? Is it a WebSocket event, a response field, or a polling endpoint? The genuine moments counter (`· 7`) needs to update in near-real-time (within the same turn response). Confirm the data flow.

5. **Aria transcript display:** The current spec shows Aria's last line as 1–2 lines of Fraunces italic text (voice-first: no full chat log). Confirm: in MVP, only the most recent Aria response is shown, and it is truncated to 2 lines? Or should there be a scrollable history accessible via some affordance? The current design hides the history — but if stakeholders want it visible, the layout needs a scrollable transcript area, which changes the proportion of the main screen.

6. **Session persistence (localStorage):** The age confirmation and AI disclosure acceptance are stored in localStorage. The skill tracker state and genuine moments counter — where do they persist? LocalStorage per BUILD_BRIEF for MVP. What's the key schema? Confirm so design can specify the empty/zero state on first load correctly.

7. **Portrait art commissioning:** The design calls for Option B (stylized semi-flat). Art must be commissioned before MVP ships. The 5 expression variants should be delivered as a single artist set (same style, same lighting, same character design) at 560×560px minimum (2x for retina), exported as WebP. Commission timeline: 2–4 weeks from brief delivery. Should this be parallelized with code build?

8. **Crisis escalation overlay:** BUILD_BRIEF §8 requires crisis escalation if the user mentions self-harm. The design spec does not include this overlay in detail (it was out of scope for MVP component list). Engineering needs a design for the crisis resource takeover — it should interrupt Aria's voice, replace the portrait with a simple neutral state, and present the crisis resources in high-contrast, accessible text. Recommend: issue filed as design task post-MVP-spec-sign-off.

---

**End of ARIA UI/UX Design System v1.0**
*Handoff to: `frontend-engineer-agent`*
*Parallel: Illustration commission brief to go to illustrator based on §4 + §5*
