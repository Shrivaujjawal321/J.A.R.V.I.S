# The Corner Pocket v2 — Awwwards-Tier Snooker Club Website

A cinematic, scroll-driven 3D website for The Corner Pocket, Mumbai's premium snooker club.
Built on Next.js 15 · React 19 · Tailwind CSS 4 · Three.js (R3F) · GSAP ScrollTrigger · Framer Motion · Lenis.

---

## Quick Start

```bash
npm install
npm run dev
# Opens on http://localhost:3000
```

Build for production:
```bash
npm run build
npm start
```

Type-check:
```bash
npm run typecheck
```

---

## What Each Section Does

| Section | What It Does |
|---|---|
| **Loader** | 1.5s cinematic intro — cue ball rolls in, title assembles letter-by-letter, curtain wipes up |
| **Nav** | Fixed header, transparent → frosted on scroll, mobile hamburger with stagger-reveal |
| **Hero** | Full-viewport procedural 3D snooker table (Three.js, no GLB), mouse-parallax orbit, bloom postprocessing |
| **About** | 3-panel scroll-jacked story, background shifts from near-black → felt-green |
| **Tables & Facilities** | GSAP-pinned horizontal scroll section — 7 facility cards translate on scroll progress |
| **Membership** | 3D-tilt mouse-track cards, flip on click to reveal full perk list |
| **Coaching** | Split reveal — image clip-path animation + SVG cue-stick draws itself on scroll |
| **Events** | Infinite marquee strip + 3 event cards with stagger reveal |
| **Gallery** | 8-image asymmetric grid, parallax at different speeds per image, lightbox on click |
| **Booking** | Float-label form, magnetic submit button, success state |
| **Contact** | Address, hours, map placeholder |
| **Footer** | Minimal, 3-column, giant TCP watermark, social links |

---

## Find-and-Replace Before Launch

Replace every item in this checklist before deploying to production:

### Content
- `42, Linking Road, Bandra West` — real club address
- `+91-22-4567-8900` — real phone number
- `hello@cornerpocket.in` — real email
- `https://cornerpocket.in` — real domain (in `layout.tsx` and JSON-LD)
- `Est. 2018` — real founding year (in `Loader.tsx`, `Nav.tsx`, `Footer.tsx`)
- Tournament names in `Events.tsx` → real upcoming events
- Event dates and details in `Events.tsx` → real data
- Coaching prices in `Coaching.tsx` → real pricing
- Opening hours in `Contact.tsx` and `Footer.tsx` → real hours

### Photography
All Unsplash URLs are placeholders. Replace with actual club photography:
- `app/layout.tsx` → `/og-image.jpg` (1200×630 OG image)
- `public/fallback/hero.jpg` — static reduced-motion hero (1920×1080)
- `components/Coaching.tsx` — coaching photo URL (~600×800, coach in action)
- `components/Gallery.tsx` — 8 gallery image URLs (see `GALLERY_IMAGES` array)

### Form Submission
In `components/Booking.tsx`, uncomment and configure Formspree:
```ts
const res = await fetch('https://formspree.io/f/YOUR_FORM_ID', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
  body: JSON.stringify(values),
});
```
Sign up at formspree.io, create a form, paste your form ID.

### Maps
In `components/Contact.tsx`, replace the map placeholder div with a real Google Maps iframe:
```html
<iframe
  src="https://www.google.com/maps/embed?pb=!1m18...YOUR_EMBED_KEY"
  width="100%" height="100%"
  style="border:0"
  allowfullscreen
  loading="lazy"
  referrerpolicy="no-referrer-when-downgrade"
  title="The Corner Pocket location map"
/>
```

### Social Links
In `components/Footer.tsx` → update Instagram, Twitter, WhatsApp hrefs.

---

## Deploy to Vercel (One-Click)

1. Push code to GitHub
2. Go to vercel.com → New Project → Import your repo
3. Framework: Next.js (auto-detected)
4. No env variables needed for the base site
5. Click Deploy

That's it. Vercel handles ISR, edge caching, AVIF/WebP image optimization automatically.

---

## Accessibility Notes (for Reviewers)

- **Reduced-motion:** The entire loader, 3D scene, and scroll animations are disabled when `prefers-reduced-motion: reduce` is set. A static hero image (`/fallback/hero.jpg`) is shown instead of the 3D scene.
- **3D scene ARIA:** The Canvas has `role="img"` and an `aria-label` describing the scene. Screen readers skip the 3D canvas.
- **Custom cursor:** Disabled entirely on touch devices (`pointer: coarse`).
- **Focus rings:** Gold `outline: 2px solid #d4af37` on all `:focus-visible` states. Never suppressed without a visible replacement.
- **Form:** All inputs are properly labelled with `<label>` elements and `htmlFor`/`id` pairing. `aria-required` on required fields.
- **Color contrast:** All body text at ≥4.5:1 against dark backgrounds. Gold accents checked against `#0a0d0a`.
- **Keyboard navigation:** All interactive elements reachable via Tab. Membership cards respond to Enter/Space for flip.
- **Lightbox:** `role="dialog"`, `aria-modal="true"`, close button with `aria-label`.

---

## Performance Notes

- **R3F/Three.js** is dynamically imported (`ssr: false`) — never in the initial bundle
- `AdaptiveDpr` drops canvas DPR to 1x when FPS < 60
- `performance.regress()` threshold is managed by R3F's AdaptiveDpr automatically
- Images: `next/image` with AVIF/WebP, lazy-loaded except hero fallback (`priority`)
- Fonts: `next/font/google` with `display: swap` — no layout shift
- JS initial bundle target: <200KB gzipped (excluding R3F which is lazy)
- Lighthouse target: Performance ≥85, A11y ≥95, Best Practices ≥90, SEO ≥95
