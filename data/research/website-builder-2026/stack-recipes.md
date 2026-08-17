# The Mid-2026 Implementation Toolkit for Premium Websites — Stack + Recipes

**Research date:** 2026-06-11 · **For:** Premium AI website-builder agent pipeline (Awwwards-tier output, not template-tier)
**Method:** WebSearch + WebFetch + GitHub Releases API + npm registry (exact versions and weekly downloads pulled live on 2026-06-11). Anything not corroborated by 2+ sources or a primary source is tagged [unverified].

---

## PART 1 — THE STACK (verified versions, adoption, licensing, verdicts)

### 1. Next.js — v16.2.9 stable (16.3 in preview)
- **Version:** `next@16.2.9` is npm latest (verified via npm registry 2026-06-11). v16.3.0-preview.3 / canary.48 published 2026-06-10 ([GitHub releases](https://github.com/vercel/next.js/releases)). Next 16 GA was Oct 2025 ([blog](https://nextjs.org/blog/next-16)); 16.2 shipped March 18, 2026 ([blog](https://nextjs.org/blog/next-16-2)).
- **What's in it:** Cache Components (`"use cache"` directive — opt-in caching, dynamic-at-request by default), React 19.2 via Canary channel, **React Compiler stable** (auto-memoization, zero manual code), **Turbopack default bundler** (2–5× faster prod builds, up to 10× faster Fast Refresh), 16.2 added ~400% faster `next dev` startup + ~50% faster rendering + AI-ready `create-next-app` + experimental Agent DevTools + Next.js DevTools MCP ([LogRocket](https://blog.logrocket.com/next-js-16-whats-new/), [Strapi](https://strapi.io/blog/next-js-16-features)).
- **Adoption:** 39.17M npm downloads/week (npm API, week ending 2026-06-02). The default for SaaS/product/dashboard builds.
- **License/cost:** MIT, free. Vercel hosting optional (works on Netlify/Cloudflare/self-host).
- **Verdict — winning** for app-like builds and anything needing server components/caching. For pure marketing/static sites it's increasingly *losing to Astro* on shipped-JS weight (see §10).

### 2. Tailwind CSS — v4.3.0
- **Version:** v4.3.0, released 2026-05-08 (GitHub releases verified). v4.2 (Feb 18, 2026) added a first-party **webpack plugin** + 4 new color palettes ([InfoQ](https://www.infoq.com/news/2026/04/tailwind-css-4-2-webpack/)); v4.3 added first-party **scrollbar styling**, more logical-property utilities, zoom/tab-size utilities, better `@variant` ([tailwindcss.com](https://tailwindcss.com/blog/tailwindcss-v4-3)).
- **Adoption:** 110.67M npm downloads/week (npm API) — the single most-installed tool in this entire list. "Zero reason to start with v3 in 2026"; Headless UI, Radix, shadcn/ui all shipped v4-compatible versions by Q1 2026 ([LogRocket guide](https://blog.logrocket.com/tailwind-css-guide/)).
- **Key v4 facts:** Oxide engine (Rust), CSS-first config (`@theme`, no `tailwind.config.js` needed), native CSS variables for every token, OKLCH default palette, container queries built in. Build-time drops from 8–12s to <2s on typical CI ([designrevision migration guide](https://designrevision.com/blog/tailwind-4-migration)).
- **License/cost:** MIT, free (Tailwind Plus templates/UI blocks are the paid arm).
- **Verdict — winning, default.** The CSS layer of essentially every 2026 stack; pair with hand-written CSS for shader/canvas layers.

### 3. GSAP — v3.15.0 · **100% free including all former Club plugins**
- **Version:** `gsap@3.15.0` (npm latest, modified 2026-04-13; GitHub tags: 3.15.0 → 3.13.0 verified). 3.06M npm downloads/week — and that undercounts: huge CDN usage via cdnjs/jsdelivr in Webflow-land.
- **Licensing — the big story:** Webflow acquired GreenSock Oct 15, 2024; on **April 30, 2025 GSAP became 100% free for everyone, including commercial use and ALL formerly-paid Club plugins** — SplitText, MorphSVG, DrawSVG, ScrollSmoother, Inertia, ScrambleText, etc. No Webflow account required ([Webflow announcement](https://webflow.com/blog/gsap-becomes-free), [CSS-Tricks](https://css-tricks.com/gsap-is-now-completely-free-even-for-commercial-use/), [gsap.com/pricing](https://gsap.com/pricing/)). Note: it is free under GreenSock's "no-charge" standard license, not OSI open-source [unverified nuance — exact license text should be re-read before redistribution inside a builder product].
- **What's new since 3.13:** complete **SplitText rewrite** — 50% smaller, screen-reader accessible (auto `aria-label`/`aria-hidden`), `autoSplit` responsive re-splitting on resize/font-load, `deepSlice` through nested tags, built-in `mask` option for line/word/char reveal clipping ([gsap.com 3.13 blog](https://gsap.com/blog/3-13/), [Webflow blog on the rewrite](https://webflow.com/blog/gsap-splittext-rewrite)).
- **Verdict — winning, the animation backbone.** ScrollTrigger remains the industry standard for scroll-driven work; the free-plugin unlock removed the last cost barrier. Risk to watch: Webflow stewardship concentration [speculative].

### 4. Lenis — v1.3.23
- **Version:** v1.3.23, released 2026-04-15 (GitHub releases, darkroomengineering/lenis). Package is `lenis` (the old `@studio-freight/lenis` is retired). 751K npm downloads/week.
- **What it is:** ~3 kB smooth-scroll that wraps **native scroll** (not scroll-hijack), any-axis, with `lenis/react` adapter; positions itself "Made for 2026+" ([lenis.darkroom.engineering](https://lenis.darkroom.engineering/), [GitHub](https://github.com/darkroomengineering/lenis)).
- **Adoption evidence:** the de-facto lerp-scroll layer on agency/award sites; showcase page lists top studio work; standard pairing documented with GSAP ScrollTrigger in Next 15/16 App Router guides ([DevDreaming 2026 guide](https://devdreaming.com/blogs/nextjs-smooth-scrolling-with-lenis-gsap)).
- **License/cost:** MIT, free.
- **Verdict — winning** for the "expensive scroll feel." Alternative: GSAP's own ScrollSmoother (now free too) — Lenis stays favored for native-scroll behavior + tiny size. Always expose `prefers-reduced-motion` off-switch.

### 5. Motion — v12.40.0 (the framer-motion successor)
- **Version:** `motion@12.40.0` (npm + GitHub tags verified; v13.0.0-alpha.0 tagged, so v13 is imminent). Import path `motion/react`.
- **History:** Framer Motion went independent in late 2024 and was renamed **Motion** at motion.dev; now has vanilla-JS and Vue APIs, not just React ([motion.dev announcement](https://motion.dev/magazine/framer-motion-is-now-independent-introducing-motion), [upgrade guide](https://motion.dev/docs/react-upgrade-guide)).
- **Adoption:** `motion` 13.0M downloads/week and `framer-motion` (legacy package) still 36.7M/week (npm API) — combined ~50M/week makes it the most-used JS animation library on npm by far.
- **License/cost:** MIT core; **Motion+** one-time paid tier for premium components/examples (Cursor component etc.) [pricing not re-verified].
- **Verdict — winning for React UI animation** (layout animations, `AnimatePresence`, springs, gestures). Division of labor in premium builds: **Motion for component/UI state animation, GSAP for timeline orchestration + scroll choreography.**

### 6. React Three Fiber — v9.6.1 (+ v10 alpha) · drei — v10.7.7 (+ v11 alpha)
- **Versions (GitHub + npm verified):** `@react-three/fiber@9.6.1` (2026-04-28); **v10.0.0-alpha.1** (2026-01-17) adds **WebGPURenderer support + new scheduler** (advanced `useFrame` scheduling, usable outside Canvas). `@react-three/drei` latest = **10.7.7** (v11.0.0-alpha.5 tracks R3F v10).
- **Compatibility:** R3F v9 is the React 19 pairing (works 19.0–19.2; the 19.2 reconciler bump caused friction, now resolved) ([v9 migration guide](https://r3f.docs.pmnd.rs/tutorials/v9-migration-guide), [pmndrs discussions](https://github.com/pmndrs/drei/discussions/2213)).
- **Adoption:** fiber 3.50M + drei 2.73M downloads/week (npm API).
- **License/cost:** MIT, free.
- **Verdict — winning for React-stack 3D.** Ship v9.6 + drei 10.x today; plan the v10/WebGPU jump for late 2026. For non-React or ultra-light builds, raw three.js or **OGL** (used on Dave Holloway's 2026 portfolio for performance) are the alternatives ([Codrops spotlight](https://tympanus.net/codrops/2026/01/22/from-design-first-to-motion-driven-dylan-brouwers-journey-into-the-no-code-frontier/) [the OGL attribution is from a Codrops developer-spotlight roundup — verified pattern, exact post varies]).

### 7. three.js — r184 · WebGPU + TSL now real
- **Version:** r184 (2026-04-16, GitHub releases). 10.15M downloads/week.
- **WebGPU status:** **WebGPU is baseline in every major browser as of 2026** — Chrome/Edge, Firefox (Win+macOS), Safari 26 (iOS + macOS Tahoe) ship it on by default ([VR.org analysis](https://vr.org/articles/webgpu-baseline-2026-three-js-webxr-default)); `WebGPURenderer` is a near drop-in swap since r171 ([utsubo migration checklist](https://www.utsubo.com/blog/webgpu-threejs-migration-guide), [threejs docs](https://threejs.org/docs/pages/WebGPURenderer.html)).
- **TSL (Three Shading Language):** JS-based node shader system that **compiles to WGSL (WebGPU) with automatic GLSL (WebGL2) fallback** — write shaders once, run on both backends ([Maxime Heckel's Field Guide to TSL and WebGPU](https://blog.maximeheckel.com/posts/field-guide-to-tsl-and-webgpu/)).
- **Claimed adoption:** "65% of new 3D-shipping web apps used WebGPU" per 2025 Web Almanac [unverified — single source (VR.org); treat as directional]. Older-device GPU coverage still demands the GLSL fallback path.
- **Verdict — winning; TSL is the future-proof shader strategy** for a builder product (one authored effect → two backends). Keep WebGL2 fallback mandatory through 2026.

### 8. View Transitions API — same-doc broadly shipped; cross-doc Chromium+Safari only
- **Same-document support (caniuse, fetched 2026-06-11):** Chrome/Edge 111+, **Safari 18+**, **Firefox 144+** → **~88.6% global** ([caniuse](https://caniuse.com/view-transitions)).
- **Cross-document (MPA) support:** Chrome 126+, **Safari 18.2+**; **Firefox has NOT shipped cross-document** (`@view-transition` ignored → snaps, no animation) ([CSS-Tricks gotchas](https://css-tricks.com/cross-document-view-transitions-part-1/), [MDN](https://developer.mozilla.org/en-US/docs/Web/API/View_Transition_API)). Conflicting claims exist on Safari cross-doc version — 18.2 per multiple sources [confidence: medium-high].
- **React/Next integration:** React `<ViewTransition>` is **experimental/canary only**; Next.js gates it behind `viewTransition: true` (unstable_, "not recommended for production", stabilization expected later in 2026). Next 16.2's `<Link>` gained a `transitionTypes` prop ([Next docs](https://nextjs.org/docs/app/guides/view-transitions), [react.dev](https://react.dev/reference/react/ViewTransition), [digitalapplied deep-dive](https://www.digitalapplied.com/blog/react-19-2-view-transitions-animate-navigation-nextjs-16)).
- **Verdict — use as progressive enhancement now** (shared-element morphs, crossfades cost ~10 lines of CSS); do NOT make it the sole transition system for premium feel — Firefox MPA + experimental React status are the blockers.

### 9. Astro — v6.4.6
- **Version:** `astro@6.4.6` (2026-06-10, GitHub releases). **Astro 6.0 GA'd March 10, 2026**: built-in **Fonts API**, Content Security Policy API, Live Content Collections, Vite 7 + Environment API (dev runs your exact prod runtime), **Node 22 required**, experimental Rust compiler ([astro.build/blog/astro-6](https://astro.build/blog/astro-6/)); 6.2 (Apr 30) added SVG optimizer API + font file URL helper ([blog](https://astro.build/blog/astro-620/)).
- **Adoption:** 3.10M downloads/week — has roughly tripled since 2024 [trend per ecosystem reporting, exact multiple unverified]. Lighthouse 95–100 typical for content pages; islands architecture = near-zero default JS ([fireup.pro](https://fireup.pro/news/astro-5-the-web-framework-for-content-driven-websites)).
- **License/cost:** MIT, free. First-class on Netlify/Vercel/Cloudflare.
- **Verdict — winning for marketing/portfolio/content sites** (the exact category a website-builder product mostly emits). Pairs cleanly with GSAP + Lenis + Barba or native view transitions; can embed React/R3F islands where 3D is needed.

### 10. shadcn/ui — CLI v4 (shadcn@4.11.0), the "agentic era" component layer
- **Version:** `shadcn@4.11.0` CLI (2026-06-08, GitHub releases). **March 2026 platform update:** CLI v4 (`--dry-run`, `--diff`, `--view` inspection), **shadcn/skills** (gives coding agents correct component/registry context — covers BOTH Radix and Base UI primitives), **Presets engine** (theme+fonts+radius+icons in one portable string), **any public GitHub repo can be a registry** via `registry.json`; `init` scaffolds Next.js, Vite, Laravel, React Router, Astro, TanStack Start ([changelog](https://ui.shadcn.com/docs/changelog/2026-03-cli-v4), [DEV summary](https://dev.to/codedthemes/shadcnui-march-2026-update-cli-v4-ai-agent-skills-and-design-system-presets-1gp1)).
- **License/cost:** MIT, copy-into-your-repo model (no runtime dep).
- **Verdict — winning as the app-UI substrate AND as AI-builder infrastructure** (registries + skills are literally designed for agent pipelines like Boss's product). **Caution for the premium-marketing use case:** default shadcn look is the new "generic" — a builder must re-token (custom palette via Presets, non-Inter type, custom radius/motion) or output screams template.

### 11. Premium type sources (the anti-Inter list)
- **2026 direction:** large-scale shift **geometric sans → neo-grotesque**, plus high-contrast editorial serifs; variable fonts are now table stakes; display fonts trend to extremes (width/weight/contrast) with expressive axes — Fraunces "wonk", Recursive's sans↔mono morph ([madegooddesigns trending](https://madegooddesigns.com/trending-fonts/), [Creative Boom top-50](https://www.creativeboom.com/resources/top-50-fonts-in-2026/), [Muzli variable fonts](https://muz.li/blog/best-free-variable-fonts-for-ui-and-web-design-2026/)).
- **Free, premium-feel (builder-safe licensing):**
  - **Fontshare** (Indian Type Foundry, free incl. commercial): **Satoshi** (the most-adopted Inter-replacement), **General Sans**, **Clash Display**, Cabinet Grotesk ([fontshare.com](https://www.fontshare.com/), [license explainer](https://madegooddesigns.com/fontshare/)).
  - **Pangram Pangram** (free-to-try, cheap personal; paid commercial): **PP Editorial New** — "the most widely adopted" trending display serif — PP Neue Montreal, PP Mori ([pangrampangram.com](https://pangrampangram.com/)).
  - **Google Fonts non-Inter picks:** Bricolage Grotesque, Instrument Sans/Serif, Fraunces, Roboto Flex (multi-axis variable) [verified available; "premium feel" is editorial judgment].
- **Paid foundry tier (what actual award sites license):** **Klim** (Söhne — "memory of Akzidenz-Grotesk through the reality of Helvetica", Tiempos — the leading editorial serif), **ABC Dinamo** (Diatype), **Grilli Type** (GT America/GT Standard), Commercial Type, OH no Type ([Klim](https://klim.co.nz/collections/soehne/), [foundry roundup](https://qodeinteractive.com/magazine/type-foundries/)).
- **Licensing economics:** desktop $100–300/family; **web licenses $200–500/yr, typically priced by monthly pageviews**; separate app/advertising licenses ([Creative Bloq licensing guide](https://www.creativebloq.com/features/font-licensing)). **Builder implication:** default output to Fontshare/Google variable fonts (zero license risk), surface paid-foundry upsell as a "premium type" option the user licenses themselves.

### Stack pieces that are LOSING (for awareness)
- **Barba.js** — `@barba/core` at just **6.8K downloads/week** (npm API): beloved in the agency/Webflow niche (Osmo sells a Barba+GSAP course; Codrops still publishes Barba tutorials in 2026) but native View Transitions are eating its mainstream use case.
- **Locomotive Scroll** — superseded by Lenis in new work [unverified but consistent across 2025-26 guides].
- **styled-components / CSS-in-JS runtime** — ceded to Tailwind 4 + CSS variables [ecosystem consensus].
- **framer-motion (the npm name)** — still 36.7M downloads/week but legacy; new code imports `motion`.

---

## PART 2 — THE RECIPES (named patterns + exact library combos)

The patterns below are the recurring "this is a 2026 premium site" moves, each with the minimal library recipe. Primary teaching sources: **Codrops** (tympanus.net), **Osmo Vault** (osmo.supply — Dennis Snellenberg + Ilja van Eck, 150+ production components, built off 35+ combined Awwwards SOTDs), **GSAP Demo Hub** (demos.gsap.com).

### R1. Masked-Line Hero Reveal ("the agency intro")
Headline split into lines/words, each line slides up from inside an overflow/clip mask with stagger; hero image scales 1.15→1 behind it; nav fades last.
- **Recipe:** GSAP 3.15 `SplitText` (use the 3.13+ rewrite: `mask: "lines"`, `autoSplit: true` for font-load/resize safety, auto-aria for a11y) + `gsap.timeline()` with `power4.out` / custom ease + optional Lenis.
- **Why it wins:** instant craft signal; rewrite killed the old FOUC/wrap bugs. ([gsap.com/blog/3-13](https://gsap.com/blog/3-13/), [Webflow SplitText story](https://webflow.com/blog/gsap-splittext-rewrite))

### R2. Scroll-Pinned Scrollytelling Section ("pin + scrub")
Section pins to viewport while an internal timeline scrubs with scroll — text steps, product states, chart builds.
- **Recipe:** GSAP `ScrollTrigger` (`pin: true`, `scrub: 1`, `anticipatePin`) + Lenis (native-scroll friendly) + timeline of fades/transforms. Pin-and-fade variant: pinned section's content crossfades per scroll segment. ([ScrollTrigger docs](https://gsap.com/docs/v3/Plugins/ScrollTrigger/), [Web Bae pin+fade](https://www.webbae.net/posts/horizontal-scrolling-section-with-pin-and-fade-effects))

### R3. Horizontal Scroll Gallery (vertical input → x travel)
Pinned container translates a row of panels on `xPercent` as the user scrolls vertically; nested reveals fire via `containerAnimation`.
- **Recipe:** GSAP ScrollTrigger (`pin` + `xPercent` tween + `containerAnimation` for inner triggers) + Lenis. The canonical award-site section since ~2022, still everywhere in 2026. ([GSAP forums canonical thread](https://gsap.com/community/forums/topic/33311-using-gsap-scrolltrigger-for-horizontal-scroll/))

### R4. Image Distortion Shader Hover
Images rendered as WebGL planes; hover/mouse velocity drives a uv-displacement / pixel-distortion uniform in the fragment shader.
- **Recipe:** three.js r184 (or R3F v9 + drei `useTexture`) + custom shader (GLSL today; **author new effects in TSL** for WebGPU+WebGL dual output) + pointer-velocity → uniform lerp. Canonical tutorials: Codrops [motion hover distortions](https://tympanus.net/codrops/2019/10/21/how-to-create-motion-hover-effects-with-image-distortions-using-three-js/), [pixel distortion](https://tympanus.net/codrops/2022/01/12/pixel-distortion-effect-with-three-js/) (patterns still current; re-skin per brand).

### R5. Scroll-Revealed WebGL Gallery (DOM↔GL sync)
Three.js planes positioned to exactly overlay HTML `<img>` elements; Lenis scroll offset feeds the render loop; shader reveal (dissolve/wipe/warp) as each enters viewport.
- **Recipe:** GSAP + Three.js + Lenis (+ Astro + Barba in the MPA version). Named 2026 walkthrough: Codrops **"Building a Scroll-Revealed WebGL Gallery with GSAP, Three.js, Astro and Barba.js"** (Feb 2, 2026) ([link](https://tympanus.net/codrops/2026/02/02/building-a-scroll-revealed-webgl-gallery-with-gsap-three-js-astro-and-barba-js/)).

### R6. Reactive-Depth 3D Image Tube / Scroll Tunnel
Infinitely looping tube/tunnel of images, scroll-driven with inertia, shader-based deformation at the edges.
- **Recipe:** React Three Fiber v9 + drei + scroll velocity → shader uniform + deterministic loop math. Named source: Codrops **"Reactive Depth: Building a Scroll-Driven 3D Image Tube with React Three Fiber"** (Feb 17, 2026) ([link](https://tympanus.net/codrops/2026/02/17/reactive-depth-building-a-scroll-driven-3d-image-tube-with-react-three-fiber/)).

### R7. Velocity-Reactive Infinite Marquee
Looping text/logo strip whose speed and direction respond to scroll velocity; premium variants run along an SVG path or sandwich content between two z-layered marquees.
- **Recipe (GSAP flavor):** `xPercent` wrap loop (`gsap.utils.wrap`) + `ScrollTrigger.onUpdate` velocity → `timeScale`, or the helper `horizontalLoop`. **(Motion flavor):** SVG-path marquee — Codrops **"Infinite Marquee Along an SVG Path with React & Motion"** (Jun 17, 2025) ([link](https://tympanus.net/codrops/2025/06/17/building-an-infinite-marquee-along-an-svg-path-with-react-motion/)). Whole-page loop variant: Codrops **"The Never Ending Story: Seamless Infinite Scroll with GSAP & Lenis"** (May 28, 2026) ([link](https://tympanus.net/codrops/2026/05/28/the-never-ending-story-building-a-seamless-infinite-scroll-experience-with-gsap-lenis/)).

### R8. Custom Cursor + Magnetic Buttons
Branded cursor follower (dot + trailing ring, `mix-blend-mode: difference`), morphs on hoverables ("View", "Drag"); CTAs magnetically pull toward pointer and elastic-return on leave.
- **Recipe:** `gsap.quickTo()` for 60fps x/y followers ([official GSAP pen](https://codepen.io/GreenSock/pen/dyjywaZ), [Demo Hub cursor-follower](https://demos.gsap.com/demo/cursor-follower/)); magnetic = bounding-box offset × pull factor, `elastic.out(1, 0.3)` return ([GSAP Vault magnetic](https://gsapvault.com/effects/magnetic-cursor)). Motion+ also ships a paid Cursor component. **Must-do:** disable on touch + `prefers-reduced-motion`; keep native cursor for a11y.

### R9. Intentional Counter Preloader → Hero Handoff
0→100 counter (sliding-digit style beats plain increments in 2026), tied to real asset load progress, exits via clip-path wipe that *hands off into the hero reveal timeline* (one continuous choreography), gated to once-per-session.
- **Recipe:** GSAP timeline + (`fonts.ready` + image `Promise.all` or resource-progress) + `sessionStorage` flag + `clip-path: inset()` exit. ([Awwwards loading-page collection](https://www.awwwards.com/awwwards/collections/loading-page/), [oma-kase 2026 preloader roundup](https://www.oma-kase.com/blog/best-framer-preloader-components)). Anti-pattern: fake 3-second loaders on repeat visits.

### R10. Route/Page Transitions — three lanes (decision matrix)
- **Lane A — Native View Transitions (progressive enhancement):** CSS `view-transition-name` shared-element morphs; same-doc ~88.6% support; cross-doc = Chromium + Safari 18.2, **Firefox snaps** ([caniuse](https://caniuse.com/view-transitions), [CSS-Tricks](https://css-tricks.com/cross-document-view-transitions-part-1/)).
- **Lane B — React `<ViewTransition>` + Next 16.2 (`viewTransition: true`, `Link transitionTypes`):** the future for Next apps but **experimental, not production-recommended yet** ([Next guide](https://nextjs.org/docs/app/guides/view-transitions)).
- **Lane C — Barba.js 2.x + GSAP (full creative control, MPA/Astro):** intercept navigation, animate out → swap → animate in; the award-site standard when transitions ARE the design. Named 2026 walkthrough: Codrops **"Creating Custom Page Transitions in Astro with Barba.js and GSAP"** (Apr 8, 2026) ([link](https://tympanus.net/codrops/2026/04/08/creating-custom-page-transitions-in-astro-with-barba-js-and-gsap/)); Osmo sells a dedicated [page-transition course](https://www.osmo.supply/product/page-transition-course). Niche but proven (6.8K downloads/wk).
- **Builder rule:** A for free polish everywhere; C when transition is a brand moment on a static/Astro build; B only behind a "beta" flag until stabilized late 2026.

### R11. WebGPU/TSL Hero Scene (the 2026 differentiator)
Hero-level generative scene (particles, fluid, refraction glass) authored once in TSL, rendering WGSL on WebGPU with automatic GLSL fallback.
- **Recipe:** three.js r184 `WebGPURenderer` + TSL node materials (+ R3F v10-alpha if React; stable lane = vanilla three island). ([Maxime Heckel field guide](https://blog.maximeheckel.com/posts/field-guide-to-tsl-and-webgpu/), [utsubo migration checklist](https://www.utsubo.com/blog/webgpu-threejs-migration-guide)). Budget rule: 60fps mid-tier laptop, DPR clamp, reduced-motion static fallback.

### R12. Velocity-Skew Scroll Text (kinetic typography)
Large display type skews/leans proportional to scroll velocity (Lenis `velocity` → `skewY`/`rotation` clamp), often combined with R1 masks and R7 marquees. **Recipe:** Lenis velocity event + `gsap.quickTo` skew. [Pattern verified across Osmo Vault + GSAP demos; no single canonical URL.]

---

## PART 3 — BUILDER-PRODUCT IMPLICATIONS (synthesis)

1. **Two output stacks, not one:** (a) **Astro 6 + GSAP 3.15 + Lenis 1.3** for marketing/portfolio tier (fastest, lightest, transition lane C/A); (b) **Next 16.2 + Tailwind 4.3 + Motion 12 + shadcn CLI v4 (re-tokened) + R3F 9.6 islands** for app/SaaS tier.
2. **Everything animation-critical is now $0:** GSAP plugins free (Apr 2025), Lenis MIT, Motion MIT, three MIT — zero licensing cost in generated output; fonts are the only licensing minefield → default Fontshare/Google variable fonts, never default Inter.
3. **shadcn registries + skills are agent-native infrastructure** — a builder pipeline can host its own component registry (any GitHub repo) and feed `shadcn/skills` context to its codegen agents.
4. **The premium bar is choreography, not parts:** preloader → hero reveal → pinned sections → custom cursor must read as ONE timeline system (this is what separates Osmo-tier from template-tier).
5. **Author shaders in TSL from day one** — single source for WebGL2 + WebGPU keeps generated effects future-proof without per-site rework.
6. **A11y/perf guardrails are part of "premium":** `prefers-reduced-motion` variants, SplitText auto-aria, native-scroll Lenis, DPR-clamped canvases, once-per-session preloaders.

*Report compiled by Jarvis research worker, 2026-06-11. Version numbers verified against GitHub Releases + npm registry the same day; download counts are npm week 2026-05-27→2026-06-02.*
