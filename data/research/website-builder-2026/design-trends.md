# SOTA Web Design — Mid-2026 Trend Taxonomy
**Researched:** 2026-06-11 · For: premium AI website-builder agent pipeline
**Sources:** Awwwards SOTD/SOTM (live fetch Jun 2026), Codrops case studies 2026, Lusion/Active Theory/REJOUICE portfolios, Web Almanac 2025, browser-support trackers. Anything uncorroborated tagged [unverified].

---

## 0. Who is hot right now (mid-2026 power list)

| Studio | Evidence (2025-26) |
|---|---|
| **Immersive Garden** | 3+ SOTMs in 18 months: own site (Jan 2025), Montfort (Jun 2025), Cartier W&W 2025 (Aug 2025), GQ & AP Extraordinary Lab (Mar 2026), Cartier W&W 2026 SOTD (May 25 2026) |
| **Lusion** | Oryzo AI SOTM (Apr 2026), Codrops feature (Apr 2026); "every project gets its own system" philosophy; Lusion Labs R&D |
| **OFF+BRAND** | Lando Norris = **Site of the Year 2025** (Webflow + GSAP); Steven.com SOTD (Jun 4 2026) |
| **REJOUICE** | Terminal Industries SOTM (Sep 2025) |
| **Unseen Studio** | Hubtown SOTD (Jun 10 2026), "2025 Wrapped" SOTD, CSSDA WOTM |
| **OddCommon** | Cleo AI SOTD (May 23 2026) |
| **Locomotive** | Truck'N Roll SOTD (Jun 3 2026); maintains Locomotive Scroll lib |
| **WILD** | Serve Robotics SOTD (Jun 11 2026) |
| **makemepulse** | Apechain SOTD (Jun 6 2026) |
| **Active Theory** | Spotify Wrapped Party (2025, live multiplayer); proprietary **Hydra** 3D engine w/ visual GUI; WebGPU/XR Experiments app |
| **Resn** | Navigate (Apr 2025), Tracing Art (Jul 2025) SOTMs |
| **Noomo Agency** | The Power of Storytelling SOTD (Jun 8 2026) |
| Also active | Vide Infra (AIR), Merci Michel (Cdiscount Jumping Max), Zypsy (ZettaJoule), 51North (Sowieso Wero), Daybreak Studio (Dropbox Brand SOTM Feb 2025), Bürocratik (Floema SOTM May 2026), basement.studio |
| Solo stars | Bruno Simon, Andrew Woan, Louis Paquet (50+ SOTDs), Patrick Heng (Ponpon Mania SOTM Oct 2025), Niccolò Miranda, Julian Garnier |

Note: Awwwards SOTM month labels showed ±1-month offset between index page and search snippets (award month vs publish month); dates above use the live awwwards.com index fetch.

---

## 1. Visual languages (color systems)

- **OKLCH is the new default color space.** Supported in all evergreen browsers (Chrome/Edge 111+, Safari 15.4+, Firefox 113+), ~95-98% global users by 2026. **Tailwind CSS 4.0 ships OKLCH-native palettes**; Figma has an OKLCH picker mode; design-token teams migrating because one OKLCH token yields perceptually-even lightness ramps across hues (HSL never did). CSS Color Module Level 4 features (`color-mix()`, wide-gamut P3) now baseline.
- **Liquid Glass — glassmorphism's 2025-26 evolution.** Apple's WWDC 2025 system language (iOS 26 / macOS Tahoe): physically-modeled **lensing + refraction**, variable opacity, morphing blur, contextual tint that adapts to content behind it. On the web it appears as a *supporting* material (nav bars, overlays), not the whole aesthetic. Static fixed-blur 2020 glass cards now read as dated.
- **Near-monochrome + one engineered accent.** Hubtown (Unseen Studio) built around a single hex (#020A19). Dark, cinematic, restrained palettes dominate the high-craft tier; color does narrative work, not decoration.
- **Neo-brutalism / anti-design is alive** as the counter-position to AI-generated sameness: raw structure, hard borders, unapologetic type, visible grid. Coexists with **maximalism** (Spotify, Liquid Death style layered texture). The macro theme: **"imperfect by design"** — signals human craft vs algorithmic neutrality.
- **Editorial/print-derived systems**: high-contrast serifs, hairline rules, index numbers, captions, magazine pacing (The Renaissance Edition — Shopify Design, SOTM Feb 2026).
- Gradient meshes/auroras persist but only as crafted, animated, shader-driven surfaces — flat "purple SaaS gradient + stock" is an anti-pattern now.

## 2. Typography

- **Variable fonts are table stakes** ("adopt now or rebuild later") — weight/width/optical axes animated on scroll and hover.
- **Kinetic type is the headline move of 2026**: scroll-driven dual-wave text (Codrops, Jan 2026), headlines that "breathe" on scroll, letters that expand on hover, per-glyph stagger via GSAP SplitText (free since GSAP went 100% free under Webflow).
- **High-contrast "funky" serif comeback** against sans-serif "blanding"; 2026 trend clusters named by forecasters: Mutant Heritage, Funky Curvy Serifs, ITC Revival, Typographic Maximalism, Perfectly Imperfect.
- **Display + mono pairing** is the signature high-craft combo: expressive display face for hero moments + monospace for labels/data/nav (reads as technical precision — the Terminal Industries / dev-tool aesthetic). Example pairing faces cited in 2026 roundups: Maxi Fluid, Exposure 2.0 [unverified versions].
- **Custom brand grotesques** as differentiator (basement.studio's Basement Grotesque, open-sourced with its own case-study site).
- Type IS the layout on many winners — oversized clipped headlines, text-as-image heroes.

## 3. Layout systems

- **Bento grids: mainstream, not over.** ~67% of top-100 ProductHunt SaaS homepages use bento-style sections [unverified %]. 2026 evolution = **"Active Grid"**: tiles expand on hover, play video, reveal data layers — static flat boxes now feel like spreadsheets. Use for feature/spec sections, NOT as whole-site identity.
- **Scrollytelling is the dominant narrative mechanism** — from journalism niche to conversion tool (claims: +85% engagement, +8.4% e-comm conversion, up to +40% product-page conversion [unverified vendor stats]). Pinned sticky scenes, scroll-scrubbed video/WebGL, chaptered narratives (The Power of Storytelling — Noomo, SOTD Jun 2026).
- **Horizontal scroll sections** inside vertical flow (GSAP ScrollTrigger pinning); **seamless infinite scroll** as portfolio pattern (Codrops May 2026, GSAP + Lenis with scroll-snapping).
- **Editorial asymmetry / broken grids** — overlapping images, rotated fragments, whitespace as drama; reaction against centered-symmetric SaaS template.
- **Page-as-world**: site is a navigable space — character walks a looping path through papercraft world (Aimee's Papercraft World), drivable car (Bruno Simon), 3D office you roam (Active Theory). The "spatial portfolio" is a recognized genre now.

## 4. Motion languages

- **The canonical stack: GSAP 3.13+ (+ ScrollTrigger, SplitText, Flip — all free post-Webflow-acquisition) + Lenis smooth scroll, synced via `gsap.ticker`.** Appears in virtually every 2026 Codrops case study (Maxima Therapy, Sticky Grid Scroll, Horeca, Flim). Lenis goal = stabilize scroll, not transform it; retrofitting Lenis late breaks everything — decide day one.
- **View Transitions API is production-real**: >85% support; cross-document transitions Chrome 126+, Safari yes, Firefox 144+ (Oct 2025). Astro 5 has it native; pattern = MPA with app-smooth route morphs, free fallback to instant nav. **Barba.js still used** when transitions must coordinate with WebGL canvases (Codrops Feb 2026: GSAP + Three.js + Astro + Barba gallery).
- **FLIP transitions** for grid→detail morphs (Joffrey Spitzer portfolio, Codrops Feb 2026).
- **Magnetic cursors/buttons formalized**: Motion (motion.dev) shipped **Motion+ Cursor** with built-in magnetic + zoning features; GSAP-vault magnetic patterns everywhere on agency CTAs. Custom cursor = brand personality carrier.
- **Custom preloaders as brand theater** — countdown preloader + custom cursor (Naya Studio, Awwwards inspiration); load sequence treated as title sequence, but must mask <2s, not hide slowness.
- **Scroll-driven masking**: SVG mask transitions (Codrops Mar 2026), clip-path wipes + shader uniforms driven by GSAP (Codrops May 2026 portfolio case study).
- **Physics-feel easing**: inertia/weight on 3D objects (Oryzo coaster), Matter.js for playful collisions (Maxima Therapy), Lottie for vector micro-anim.
- CSS-native **scroll-driven animations** (`animation-timeline: scroll()`) usable for lightweight effects; GSAP still owns orchestration [unverified split].

## 5. 3D / shader usage patterns

- **WebGPU hit baseline 2025-26**: Safari 26 shipped it (Sep 2025) → all major browsers. Web Almanac 2025: **~65% of new 3D-shipping web apps use WebGPU** (vs 8% two years prior) [unverified %].
- **Three.js WebGPURenderer production-ready** since ~r171 (zero-config, auto-fallback to WebGL2); r184 (Mar 2026) killed per-frame allocations. **TSL (Three.js Shading Language)** = write shaders once in JS, compiles to WGSL + GLSL — this is how Bruno Simon's SOTM portfolio auto-upgrades to WebGPU.
- **R3F v9 + React 19** for React shops; Threlte for Svelte; raw Three.js for the Lusion/Active Theory tier (custom engines: Active Theory's **Hydra** with designer-facing visual GUI).
- **Patterns that win**: scroll-orbited camera paths with real Z-depth (not layered parallax fake) — Oryzo; product-as-hero cinematic configurators (claimed 40% conversion lift case [unverified]); handcrafted/stylized 3D (papercraft, low-poly, storybook — Lusion's My Little Storybook) **over** photoreal CG; compute-shader particles; live multiplayer shared scenes (Spotify Wrapped Party, Bruno's portfolio online mode).
- **Performance discipline is part of the aesthetic**: 60fps + reduced-motion fallbacks expected by judges; Webflow/no-code tier proves heavy motion ≠ heavy page (Horeca case study).

---

## 6. ≥15 named reference sites (live URLs + what makes each distinctive)

1. **Lando Norris** — landonorris.com [unverified domain; awwwards.com/sites/lando-norris] — **Awwwards Site of the Year 2025** (OFF+BRAND). Proof that Webflow + GSAP (no WebGL) can take SOTY: kinetic type, racing-grade motion pacing, personality-first.
2. **Bruno's Portfolio** — bruno-simon.com — SOTM Jan 2026. Three.js + **TSL → auto-WebGPU**, drivable 3D world, online multiplayer, fully open-source incl. Blender files.
3. **Oryzo AI** — oryzo.ai — SOTM Apr 2026 (Lusion). Satire-as-craft: cork coaster sold like an AI unicorn launch; inertia-weighted 3D, real Z-axis camera travel, full fake campaign (Product Hunt, founder video).
4. **Aimee's Papercraft World** — aimees-papercraft-world.com — SOTD May 24 2026 (Andrew Woan). R3F + Blender + Krita; scroll moves a character along a looping path through a seasonal papercraft diorama; open-source tutorial project.
5. **Hubtown** — hubtown.co.in — SOTD Jun 10 2026 (Unseen Studio). Real-estate corporate site at Awwwards tier: single-color system (#020A19), WebGL + GSAP storytelling — proof "boring industry ≠ boring site."
6. **Terminal Industries** — terminal.industries [unverified domain; rejouice.com/work/terminal-industries] — SOTM Sep 2025 (REJOUICE). Logistics-AI brand: cinematic b2b, mono-data typography, yard-OS made sexy.
7. **Cleo AI** — web.meetcleo.com [unverified exact host] — SOTD May 23 2026 (OddCommon). "Cleo isn't a bank" — silky product-led motion, fintech with attitude.
8. **Cartier Watches & Wonders 2026** — SOTD May 25 2026 (Immersive Garden; URL behind campaign [unverified]). Luxury WebGL jewelry rendering two years running (2025 edition = SOTM Aug 2025).
9. **The Power of Storytelling** — SOTD Jun 8 2026 (Noomo). Conference/editorial scrollytelling flagship.
10. **Apechain** — apechain.com — SOTD Jun 6 2026 (makemepulse). Web3 brand with high-energy WebGL interaction.
11. **Serve Robotics** — serverobotics.com — SOTD Jun 11 2026 (WILD). Robotics product cinematics.
12. **Active Theory** — activetheory.net — agency site as immersive 3D office (neon, AI-chat navigation), runs on proprietary Hydra engine; Spotify Wrapped Party 2025 = live multiplayer at scale.
13. **Lusion** — lusion.co — prior SOTM winner; labs/R&D culture, per-project custom systems.
14. **basement.studio** — basement.studio — brutalist-leaning, custom typeface (Basement Grotesque), Next.js + GSAP stack, "we make cool shit that performs."
15. **Locomotive** — locomotive.ca — agency behind Truck'N Roll SOTD (Jun 3 2026) + Locomotive Scroll library; Montréal editorial-motion school.
16. **Anime.js v4 site** — animejs.com — SOTM May 2025 (Julian Garnier). Library docs site as award-winner: interactive playground = the docs.
17. **MindMarket** — SOTM Dec 2025 (Louis Paquet × KOKI-KIKO) [site URL unverified]. Research-agency brand with human-craft warmth.
18. **Dropbox Brand Guidelines** — brand.dropbox.com [unverified exact host] — SOTM Feb 2025 (Daybreak Studio). Brand-guidelines-as-product page; bento + motion done corporately right.
19. **Ponpon Mania** — SOTM Oct 2025 (Patrick Heng) [URL unverified]. Playful character-driven WebGL comic world.
20. **The Renaissance Edition** — SOTM Feb 2026 (Shopify Design). Editorial maximalism from an in-house team.
21. **Razorpay Sprint 26** — SOTD May 26 2026 (Razorpay Design). Indian fintech in-house team hitting Awwwards — relevant local benchmark for Boss.

---

## 7. Anti-patterns that scream "2020 template" (forbid in builder output)

1. Stock photos: business-casual people laughing at laptops / handshakes.
2. Vague hero: generic headline + says-nothing subtext + two default buttons, no hierarchy, no reason to scroll.
3. **AI-slop sameness**: prompt-generated sites with identical layout + purple gradient + stock illustration; smooth uncanny AI imagery (already reads stale in 2026).
4. Static flat bento boxes with no hover life ("spreadsheet feel").
5. 2020 glassmorphism: fixed-blur frosted cards everywhere, no light/context response.
6. Corporate-Memphis-style generic blob illustrations.
7. Centered symmetric section stack: hero → 3-col features → testimonial carousel → pricing → footer, all fade-up-on-scroll at same easing.
8. Scroll-hijacking without narrative payoff; preloaders that hide slow sites (>2s).
9. Lottie/parallax sprinkled as decoration, disconnected from brand story.
10. Default system blue links, default cursors, default focus rings on a "premium" site — zero craft signals.
11. Retrofitting smooth-scroll/motion late (Horeca lesson: design mobile + motion constraints day one).
12. Free-theme tells: identical WordPress/Bootstrap spacing rhythm, hamburger-everywhere, Font Awesome icons.

## 8. Builder-pipeline implications (synthesis)

- **Default stack for award-tier output**: Next 15 / Astro 5 + GSAP 3.13 (free) + Lenis + View Transitions API (Barba.js only when WebGL must persist across routes) + Three.js r184+ with TSL/WebGPU auto-fallback (R3F v9 if React) + Tailwind 4 (OKLCH tokens) + variable fonts with display+mono pairing.
- **Uniqueness levers the agent must vary per-site**: color system seed (OKLCH ramp), type pairing personality, one signature interaction (magnetic cursor / kinetic hero / 3D object / scrollytale), layout school (editorial-asymmetric vs bento-active vs spatial-world), preloader identity.
- **Quality gates**: 60fps, reduced-motion variant, <2s perceived load, mobile-first motion design, no anti-pattern list violations.
