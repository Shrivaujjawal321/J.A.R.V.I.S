# Motion System for Dense Operational Software (2026) — Research Brief

Research question: What is the actual, measurable motion system used by best-in-class dense operational software — and what should a TMS dispatch console's be?

## Quick Answer

Best-in-class operational tools (Linear, GitHub/Primer, Atlassian, IBM Carbon) converge on a **narrow duration band of ~100–300ms**, almost always **ease-out for anything entering/appearing and ease-in for anything leaving**, restrict animation to **compositor-only properties** (`transform`, `opacity`), and — critically — **remove animation entirely from any action a user repeats hundreds of times a day** (keyboard shortcuts, row selection, status toggles). The instinct to add "polish" animation to every state change is the single most common regretted decision in this category; the industry pattern is not "faster animation" but "no animation" for high-frequency interactions, and animation reserved only for low-frequency, spatially-informative transitions (drawer open, modal, wizard step). For a dispatch console specifically, this means: near-zero animation on data mutation (status chips, table rows, HOS bars, detention timers should update as literal state, not decorative motion), and motion budget spent only on the 4-step wizard, drawer, and notification centre.

## Recommended Token Table

| Token | Value | Easing | Governs |
|---|---|---|---|
| `motion.none` | 0ms | — | Status chip color change, table cell value update, HOS bar fill update, detention timer tick, row selection highlight, any state change a dispatcher triggers via keyboard/hotkey, optimistic UI confirmation (action appears to complete instantly; server sync happens invisibly in background) |
| `motion.instant` | 80–100ms | `ease-out` (`cubic-bezier(0,0,0.2,1)`, Material "standard-decelerate") | Hover state, focus ring appearance, button press feedback, tooltip appear |
| `motion.fast` | 120–180ms | enter: `ease-out`; exit: `ease-in` (`cubic-bezier(0.4,0,1,1)`) | Dropdown/select menu open, popover, checkbox/toggle fill, small chip enter (e.g. new notification badge) |
| `motion.base` | 200–250ms | enter: `ease-out`; exit: 30–50ms *faster* than enter (asymmetric — see Linear/NN·g finding) | Drawer slide-in, side-panel open, filter panel expand, wizard step transition |
| `motion.slow` (ceiling — do not exceed) | 300–350ms | `ease-in-out` or spring (see below) | Modal open/close, full-page-region transition. Nothing in this product should animate past ~350ms; NN/g's own data says ≥500ms reads as "a real drag." |
| `motion.toast-in` | 150–200ms | `ease-out` | Notification centre item enter |
| `motion.toast-out` | 200–250ms, then 4–6s dwell before auto-dismiss | `ease-in` (fade + slight upward/lateral slide) | Toast dismiss. Never auto-dismiss error/action-required toasts. |
| `motion.skeleton-to-content` | 120–150ms crossfade | `ease-out` | Swap from skeleton to real data, *only triggered if load exceeds ~400ms* (see loading-state ladder below) |
| Spring (for anything the user can re-trigger mid-animation: drawer, popover, drag) | stiffness ≈ 300–400, damping ≈ 30–35, mass 1 [inferred — see confidence note] | n/a (spring, not cubic-bezier) | Drawer/panel that can be toggled rapidly; anything driven by drag/gesture |

**Loading-indicator ladder** (Nielsen response-time thresholds mapped to indicator choice — see NN/g section below):
- < 100ms wait: no indicator at all
- 100–400ms: small inline spinner
- 400ms–3s: skeleton screen
- \> 3s: skeleton + progress/ETA text

**Reduced motion:** `prefers-reduced-motion: reduce` → collapse all `motion.base`/`motion.slow` spatial transitions (slide, scale, parallax) to **opacity-only crossfades at ~100ms**; keep functional feedback (focus rings, color state changes) since those convey information, not decoration; never fully remove motion that is the *only* signal of a state change (e.g. don't silently kill a "saved" confirmation — crossfade it instead of sliding it).

---

## Evidence Section (per source)

### Linear
**Found (secondary technical breakdown, not Linear's own blog — see confidence note):**
- Restricts animation to compositor-only properties (`transform`, `opacity`, plus paint-only `background-color`); explicit stance: never animate layout-triggering properties (width/height/margin/padding).
- Reported concrete durations: highlight fade-in 0s (instant), highlight fade-out 0.15s, "quick" 0.1s, "regular" 0.25s, "slow" 0.35s.
- **Asymmetric timing pattern**: elements appear instantly, disappear more slowly — mirrors macOS convention.
- Core philosophy statement (paraphrased from the source): all the engineering effort to shave milliseconds off perceived latency "can be undone by bad animations" — a single unnecessary 500ms transition erases the felt benefit of an otherwise fast app.
- Optimistic UI: local-first sync engine (MobX/IndexedDB) applies mutations to UI immediately; network confirmation, retry, and rollback all happen invisibly. No spinners for user-initiated mutations.
[Source: performance.dev "How's Linear so fast? A technical breakdown" — third-party reverse-engineering, treat as **medium confidence**, not an official Linear statement]

### Material Design 3 (Google)
**Found:** Duration tokens organized as a numeric scale: `short1` 50ms, `short2` 100ms, `short3` 150ms, `short4` 200ms, `medium1` 250ms, `medium2` 300ms, `medium3` 350ms, `medium4` 400ms, `long1` 450ms ... up to `extraLong4` 1000ms (used for large/expressive transitions, container transforms, page transitions — not appropriate for a dense operator tool). Two easing families: **Emphasized** `cubic-bezier(0.2, 0, 0, 1.0)` (recommended for most transitions, content entering the viewport) and **Standard**, prioritizing practicality/speed over naturalness.
**Confidence note:** M3's own page (m3.material.io) renders its token table client-side; my direct fetch could not extract the raw table, so these numbers come from cross-referenced secondary sources. The scale shape (50ms increments up to 1000ms) is internally consistent with what I know of the spec, but treat exact boundary values as **medium confidence**, verify against `m3.material.io/styles/motion/easing-and-duration/tokens-specs` before hard-coding.

### IBM Carbon Design System
**Found:** Two motion "moods" — **productive** (fast, for frequent/functional interactions) and **expressive** (slower, reserved for rare/important moments to "offer a rhythmic break to the productive experience" — explicitly *not* the default). Token names exist (`fast-01`, `fast-02`, `moderate-01`, `moderate-02`, `slow-01`, `slow-02`) and Carbon states "most animations in the component library last between 100 and 300 milliseconds."
**Not found:** I could not extract the exact ms value behind each individual token (`fast-01` vs `fast-02` etc.) despite four separate fetch/search attempts — the docs site renders these client-side and didn't surface in text search. **Do not treat any specific Carbon token=ms mapping as verified; only the 100–300ms aggregate range and the productive/expressive split are confirmed.**

### Atlassian Design System
**Found:** Explicit two-tier duration split by interaction class — **Interactions: 50–150ms** (hover, press, list-item state change) and **Transitions: 150–400ms** (elements entering/exiting/repositioning: modal, panel, flag, popup). Named easing curves with cubic-bezier values: ease-out-bold `cubic-bezier(0, 0.4, 0, 1)` ("arrive quickly, decelerate to a stop"), ease-in-out-bold `cubic-bezier(0.4, 0, 0, 1)`, ease-in-practical `cubic-bezier(0.6, 0, 0.8, 0.6)`, ease-out-practical `cubic-bezier(0.4, 1, 0.6, 1)`. Note: their newer semantic-token system (`motion.popup.enter` etc.) was, as of the page I fetched, still behind a feature flag (`platform-dst-motion-uplift`) — treat as **emerging, not yet fully shipped**.
[Source: atlassian.design/foundations/motion — **high confidence**, directly fetched primary doc]

### GitHub Primer
**Found:** Semantic duration scale — `motion.duration.micro` ≈100ms (hover/focus), `motion.duration.short` ≈200ms (state changes), `motion.duration.medium` ≤300ms (general ceiling for UI interactions), `motion.duration.long` 500ms (hard max, explicitly "never exceed for UI"). Easing is keyword-referenced (`enter`/`exit`/`move`/`hover`/`linear`) with actual cubic-bezier curve values deferred to a separate `DESIGN_TOKENS_SPEC.md` I could not locate/fetch.
**Confidence:** duration scale is **medium-high** (consistent primary-source structure across two fetch attempts); exact cubic-bezier numbers for Primer's curves are **not found**.

### Fluent 2 (Microsoft)
**Found:** Qualitative guidance only — animation duration should scale with element size/distance traveled ("give larger elements more time"), four named easing types (linear, ease-in, ease-out, ease-in-out) described conceptually.
**Not found:** No specific ms values or cubic-bezier coordinates surfaced in the public motion overview page. Fluent 2's toast component does specify a **7-second dwell** for toasts with no action.

### Material Design / general industry — spinner vs skeleton (perceived performance)
**Found:** Apps that replaced spinners with skeleton screens report 30–50% perceived-performance improvement with zero backend change; skeleton screens reduce bounce 9–20% in some studies. One study found the opposite for very short waits — spinners were rated more positively when the actual wait was brief, because a skeleton for a near-instant load can itself feel like a false promise of more content than needed. Synthesized ladder (Nielsen threshold + skeleton research): no indicator <100ms, spinner 100–400ms, skeleton 400ms–3s, skeleton+progress >3s.
[Sources: multiple UX-blog secondary sources — **medium confidence**, directionally consistent across sources but no single peer-reviewed study pinned all four thresholds precisely]

### Nielsen Norman Group — response-time limits
**Found, high confidence (NN/g primary source, directly fetched):**
- **0.1s (100ms)**: limit for an action to feel instantaneous — direct manipulation, no feedback needed beyond the result itself.
- **1.0s**: limit for the user's flow of thought to stay uninterrupted; delay is noticed but tolerated without special feedback.
- **10s**: limit for keeping attention on the task at all; beyond this, users context-switch and need progress feedback with an estimate.
- Separately (NN/g "Executing UX Animations: Duration and Motion Characteristics"): simple feedback (checkbox/toggle) ≈100ms total; modal entering ≈200–300ms; general safe range 100–400ms, "far more common for animations to be too long than too short"; at ~500ms animations "start to feel like a real drag." Ease-out recommended for entering (lets the eye track the element to rest); ease-in for exiting (acceleration away feels natural). Entry/exit asymmetry explicitly recommended: e.g. popup takes 300ms to appear but only 200–250ms to disappear.
- Cites one peer-reviewed study: Pratt et al. (2010), *Psychological Science*, "It's Alive! Animate motion captures visual attention" — animated motion reliably captures attention, which is exactly why it should be reserved for things that deserve attention-capture, and withheld from routine high-frequency state changes.
[Sources: [Response Time Limits (NN/g)](https://www.nngroup.com/articles/response-times-3-important-limits/), [Executing UX Animations (NN/g)](https://www.nngroup.com/articles/animation-duration/)]

### Emil Kowalski (animations.dev)
**Found, high confidence (directly fetched primary essay "You Don't Need Animations"):**
- General ceiling: "UI animations should generally stay under 300ms." Concrete comparison offered: a 180ms dropdown feels more responsive than a 400ms one.
- **Core repetition argument** (directly on-point for this brief): frequent interactions are the strongest candidate for *removing* animation entirely, not speeding it up. Verbatim-paraphrased argument: something opened hundreds of times a day that animates every time becomes "very annoying"; no animation at all is "the optimal experience" for that case.
- Keyboard-triggered actions specifically called out: because they may be repeated hundreds of times a day, animating them makes the interaction "feel slow, delayed, and disconnected from the user's actions" — explicit recommendation to **never** animate them.
[Source: [emilkowal.ski/ui/you-dont-need-animations](https://emilkowal.ski/ui/you-dont-need-animations)]

### Superhuman
**Found (third-party technical breakdown — blakecrosley.com — treat as medium-low confidence, not Superhuman's own published spec):**
- Reported response-time targets: internal target 50–60ms, public claim of 100ms as the "feels instant" threshold, ~50ms for archive/send/move actions, ~100ms for first search results.
- Reported animation durations: ~150ms ease-out for email archive/slide transitions, ~200ms `cubic-bezier(0.34, 1.56, 0.64, 1)` (an overshoot/spring-like curve) for command palette entry.
- Optimistic UI + 5-second undo-toast pattern instead of loading spinners for destructive/committing actions — directly transferable to a dispatch console's status-change actions (e.g. "reassign driver" completes optimistically with an undo window rather than a blocking spinner).
**Caveat:** I could not corroborate these specific ms figures against an official Superhuman engineering source; they should be treated as a plausible, well-reasoned reconstruction, not verified fact.

### Vercel / Geist, Stripe Dashboard, Notion, Datadog, Retool, Figma, Height — what I could NOT find
- **Vercel Geist**: design system exists and documents motion as a category, but no public page surfaced exact duration/easing tokens in this research pass.
- **Stripe**: no published numeric motion tokens found. Found one specific, sourced UX decision: Stripe's iPhone dashboard adds a deliberate **100ms delay before opening a card** (not an animation duration — a debounce/UX delay) for two stated reasons: data isn't ready yet, and it gives the user time to register where they tapped. General principle attributed to Stripe: prefer custom cubic-bezier curves over built-in `ease`/`linear`, animate `transform`/`opacity` only, keep animated DOM subtrees small to limit repaint scope. [Source: Quora response citing Stripe's front-end team + stripe.com/blog/connect-front-end-experience — **low-medium confidence**, not a primary numeric spec]
- **Notion**: no public design-system motion documentation found.
- **Datadog**: found only a loading-indicator rule ("display a loader if wait > 1 second," "loaders no larger than 24px") and dense-table guidance (progressive disclosure via hover tooltips, ellipsis truncation) — no motion/animation duration guidance in their public UI-extension design guidelines. [Source: [DataDog/apps UI extensions design guidelines](https://github.com/DataDog/apps/blob/master/docs/en/ui-extensions-design-guidelines.md)]
- **Retool**: no published motion/design-token documentation found; only community forum discussion of hover-reveal row actions as a UX pattern (functional, not a timing spec).
- **Figma (the product's own UI)**: no public motion-token spec found. Figma's 2026 Config announcement added a native **Motion** feature for *designing* animations (timeline, keyframes, spring controls, Dev Mode export to CSS/React) — this is about their tool for creating motion, not necessarily documentation of their own app's internal motion values.
- **Height**: shut down September 2025 (acquired-audience absorbed largely by Linear, no formal acquisition confirmed); not usable as an active reference.

### Spring physics parameters (industry defaults)
**Found:** Framer Motion / Motion library defaults: `stiffness: 100, damping: 10, mass: 1`. General physics relationship: higher stiffness = faster/snappier; lower damping = more oscillation/bounce; higher mass = slower, more "lumbering." Motion (formerly Framer Motion) explicitly markets spring-based animation as **interruptible** — because it animates against live transform state rather than fixed CSS keyframes, a spring smoothly reverses direction if interrupted mid-flight, whereas CSS keyframe animations "snap back" to the first keyframe when interrupted, producing a visibly broken transition.
[Source: [motion.dev spring docs](https://motion.dev/docs/spring), [motion.dev easing functions](https://motion.dev/docs/easing-functions)]
**Recommendation derived from this** [inferred]: for the dispatch console's drawer/panel and any element a dispatcher might toggle rapidly (open→close→open in quick succession while triaging), use spring, not CSS transition — the interruption-smoothness matters more here than exact timing precision. For everything else (chip fades, hover states), a fixed-duration cubic-bezier is fine and cheaper to reason about.

---

## Anti-Patterns for Operator Tools (with why)

1. **Animating on every data mutation / websocket push.** A dispatch console re-renders constantly (GPS pings, status changes, new loads). If table rows or status chips animate on every update, the screen never stops moving during a busy shift — this is the single most cited "regretted" pattern in dense internal tools (per multiple UX sources: "flashy features that look great in a demo become torture by the fifteenth time"). Fix: `motion.none` for data-driven updates; reserve any transition for *user-initiated* changes only.
2. **Animating high-frequency/keyboard-triggered actions.** Directly per Kowalski: never animate actions a dispatcher does hundreds of times a day (row select, status toggle, hotkey-driven assignment). Animation here reads as latency, not polish.
3. **Symmetric enter/exit timing.** Multiple sources (Linear, NN/g) independently converge on asymmetric timing — fast/instant appearance, slightly slower, easier disappearance. Symmetric timing (both directions identical) is a template-tier tell.
4. **Spinners for anything under 400ms and skeletons for anything over 3s without a progress estimate.** Both directions cost perceived performance — a spinner on a 150ms load flickers uselessly; a skeleton alone (no ETA) past 3s reads as stuck. Map the loading-indicator ladder above.
5. **Blocking keyboard input during a transition.** A modal-open or panel-slide animation that swallows keystrokes for its duration breaks a dispatcher's hotkey muscle memory — animations must never gate input; the target state should be programmatically "arrived" (focusable, hotkey-live) at the start of the transition, with the visual catching up.
6. **Easing/animating literal counters** (detention timers, HOS countdown bars). These represent real elapsed time. Any easing curve or transition delay on the *value itself* makes the display lie by a few hundred ms about actual elapsed/remaining time — update these via direct state/interval, never via animated tweening. (Motion on their *container* — e.g. a color-state change from green→amber→red as a threshold crosses — is fine and should use `motion.instant`/`motion.fast`, but the number and bar-fill must be exact.)
7. **CSS-keyframe animation on anything re-triggerable.** If a drawer/dropdown can be opened, closed, and reopened faster than its own animation completes (very common under dispatcher time pressure), CSS keyframes will visibly snap/stutter. Use interruptible (spring or JS-driven, transform-based) animation for anything in this category.
8. **Decorative motion competing with alert motion.** If routine chip/hover motion uses the same visual register (movement, scale, glow) as a genuine alert (e.g. a truck going non-compliant on HOS), the alert loses salience through habituation. Reserve any expressive/attention-grabbing motion (Carbon's "expressive" mood, a pulse, a stronger easing overshoot) exclusively for rare, important events — never for routine chrome.
9. **Long entrance/reveal sequences, scroll-jacking, parallax.** Explicitly out of scope per the brief's own framing, and confirmed by every source above as belonging to marketing-site motion language, not operational software — none of the reviewed products (Linear, Atlassian, Carbon, Primer) use anything beyond simple enter/exit/move transitions.

---

## Open Questions I Could Not Resolve

- **Exact Carbon `fast-01`/`fast-02`/`moderate-01`/`moderate-02`/`slow-01`/`slow-02` ms values** — confirmed only the aggregate "100–300ms for most animations" claim and the productive/expressive naming; the per-token breakdown needs a direct look at the `@carbon/motion` npm package source rather than the docs site (which renders client-side and evaded both fetch and search).
- **Exact Material 3 token table** — same client-side rendering problem; the short1→extraLong4 scale I report is consistent with known M3 structure but should be re-verified against `m3.material.io/styles/motion/easing-and-duration/tokens-specs` or the M3 GitHub token JSON before being hard-coded into a design system.
- **Any genuinely primary-sourced motion spec for Stripe Dashboard, Vercel/Geist, Notion, or Figma's own app UI.** None of these four publish a numeric motion-token doc publicly (unlike Atlassian, Carbon, Primer, Fluent2, Polaris, Material). What I have for Stripe is a single anecdote (100ms delay before card-open) and general principles, not a token scale.
- **Superhuman's numbers are unverified against a primary source.** They're a plausible, internally consistent reconstruction from a third-party breakdown, not from Superhuman's own engineering blog. Useful as a directional reference (optimistic UI + undo pattern is the real transferable insight), not as numbers to copy verbatim.
- **No hard, controlled A/B data found** specifically quantifying "animation fatigue" in dense B2B tools (e.g., a measured task-time delta for animated vs. non-animated row-select at week 4 of daily use). What exists is strong, repeated expert consensus (Kowalski, multiple UX Collective/production blog pieces, Linear's stated design philosophy) rather than a peer-reviewed study — the Pratt et al. (2010) NN/g citation establishes that motion captures attention, but doesn't directly measure fatigue from repetition. Treat the repetition-cost argument as strong expert consensus, not as a cited controlled study result.
- **Spring parameter values for a specific "dispatch console feel"** (stiffness 300–400/damping 30–35 in the token table above) are my own [inferred] extrapolation from Framer Motion's documented defaults (100/10/1, which read as noticeably softer/bouncier than what a snappy operator tool wants) — not a value found in any named product's public spec. Worth prototyping and tuning against actual usage rather than treating as settled.

## Confidence Summary

- **High confidence, directly verified from primary sources:** NN/g response-time limits and animation-duration article; Atlassian's duration bands and easing curves; Emil Kowalski's repetition/duration argument; Primer's duration scale structure; WCAG 2.3.3 requirement text; Framer Motion/Motion spring defaults.
- **Medium confidence, consistent across secondary sources but not independently verified against a primary numeric table:** Material 3 exact token values, Carbon's aggregate 100–300ms range (not per-token breakdown), skeleton-vs-spinner perceived-performance percentages, Linear's specific ms figures (from a third-party technical breakdown, not Linear's own words).
- **Low-medium confidence, single-source or unverifiable:** Superhuman's specific ms figures; Stripe's general animation principles (beyond the one sourced 100ms anecdote).
- **Not found at all (flagged explicitly rather than guessed):** Vercel/Geist, Notion, Figma-app, Retool, Datadog motion-token specifics; the exact cubic-bezier values behind Carbon's and Primer's named easing curves.
