# The Corner Pocket — Marketing Site

A premium, dark-mode, single-page marketing site for The Corner Pocket snooker club. Built with **Astro 4 + Tailwind CSS 3**. Zero React, zero JS framework — just Astro components and a sprinkle of vanilla JS for the nav + scroll reveals.

The aesthetic: **felt green + brass + gold + walnut**, classic snooker-hall typography, generous spacing. Designed to feel like SoHo House meets a Victorian billiards room — never gamer, never neon.

---

## 1. Quickstart

```bash
# install deps
npm install

# dev server (http://localhost:4321)
npm run dev

# production build → ./dist
npm run build

# preview production build locally
npm run preview
```

Recommended Node version: **18.17+** or **20+**.

---

## 2. Project structure

```
corner-pocket-site/
├── astro.config.mjs          ← Astro config (site URL, integrations)
├── tailwind.config.mjs       ← design tokens: colors, fonts, animations
├── tsconfig.json
├── package.json
├── public/                   ← static assets served as-is
│   ├── favicon.svg
│   └── robots.txt
└── src/
    ├── layouts/
    │   └── Layout.astro      ← <head>, fonts, JSON-LD, OG tags
    ├── styles/
    │   └── global.css        ← Tailwind layers + custom components + reveal animations
    ├── components/
    │   ├── Nav.astro             ← sticky nav, mobile menu
    │   ├── Hero.astro            ← full-bleed felt + dual CTA + stats
    │   ├── SectionHeader.astro   ← reusable eyebrow + headline pattern
    │   ├── About.astro           ← club story + founder quote
    │   ├── Tables.astro          ← 4-card facilities grid
    │   ├── Membership.astro      ← 3 pricing tiers
    │   ├── Coaching.astro        ← coach intro + 4 session types
    │   ├── Events.astro          ← upcoming events grid
    │   ├── Gallery.astro         ← CSS-columns masonry, 6 images
    │   ├── Booking.astro         ← reservation form
    │   ├── Contact.astro         ← address, phone, social, map embed
    │   └── Footer.astro
    └── pages/
        └── index.astro       ← composes all sections
```

---

## 3. Find-and-replace before launch (do this first)

All placeholders are gathered here. Open each file and update:

### `src/layouts/Layout.astro`
- `telephone: '+91-98000-00000'` → real club phone
- `streetAddress: '12 Linking Road, Bandra West'` → real address
- `postalCode: '400050'`, `addressLocality`, `addressRegion` → real values
- `geo.latitude / longitude` → real coordinates (use [latlong.net](https://www.latlong.net))
- `openingHoursSpecification` → real hours

### `src/components/Hero.astro`
- Tagline currently set to **"Where the city racks up after dark."** Two alternatives are listed in the component's frontmatter comment block. Edit if preferred.
- Hero image is an Unsplash hotlink — replace with a brand photograph of your felt close-up.
- "Est. 2019 — Bandra West, Mumbai" eyebrow line.
- Stats row: 6 tables / 4 pool / 1 bar / 24/7 — adjust if numbers differ.

### `src/components/About.astro`
- Founder quote and name (`Aman Sethi` → real founder).
- "340+ members" stat plaque.
- Image (Unsplash) → real club interior shot.

### `src/components/Membership.astro`
- Three tier prices (₹2k / ₹8k / ₹25k per month) — confirm with Boss / club.
- Joining fee line (₹15,000) at section bottom.

### `src/components/Coaching.astro`
- Coach name `Ravi Mehta` and credentials.
- Four session prices.
- Image → real photo of coach / coaching session.

### `src/components/Events.astro`
- Three event cards (dates, times, names). Refresh monthly.

### `src/components/Gallery.astro`
- Six Unsplash images → real club photography.

### `src/components/Booking.astro`
- Form `action`. Currently `mailto:bookings@thecornerpocket.club` (works on first launch, no backend).
  - **To swap for [Formspree](https://formspree.io):** create a form, copy the endpoint URL (looks like `https://formspree.io/f/xqknqkqk`), replace the `FORM_ACTION` value at the top of `Booking.astro`, and remove the `enctype="text/plain"` attribute.
  - **To use [Web3Forms](https://web3forms.com) (free, no signup):** set `FORM_ACTION` to `https://api.web3forms.com/submit` and add a hidden field `<input type="hidden" name="access_key" value="YOUR-KEY" />` near the top of the form.
- Phone number `+91 98000 00000`.
- All `bookings@`, `hello@`, `membership@` email addresses.

### `src/components/Contact.astro`
- Address (must match `Layout.astro` JSON-LD).
- Phone.
- Social links (Instagram / Facebook / WhatsApp) — currently pointing to `thecornerpocket` handles.
- Google Maps embed currently uses the address-search fallback. To get an exact pin, replace `mapEmbed` with the embed URL from `maps.google.com → Share → Embed a map`.

### `src/components/Footer.astro`
- Hours, copyright.

### Branding
- **OG image:** add a `public/og-cover.jpg` (1200×630px) — the Layout already references `/og-cover.jpg`. Without this, social sharing will fall back to favicon.
- **Favicon:** `public/favicon.svg` ships with a cue-ball + gold-dot mark. Replace with brand mark if you have one.
- **Domain:** update `site:` in `astro.config.mjs` and `Sitemap:` line in `public/robots.txt`.

---

## 4. Image strategy

All current images are **Unsplash hotlinks** (live URLs with `?auto=format&fit=crop&w=...&q=...` params). They work in dev and production without download, but:

- **Before launch**, replace each one with real club photography. Hotlinking Unsplash forever is fragile (URLs can change) and unprofessional for a premium brand.
- Recommended workflow: download replacements to `public/images/`, then reference as `/images/your-photo.jpg`.
- Use AVIF or WebP where possible. For hero images, keep under 250KB.
- Astro's `<Image />` component can be added later if you want automatic optimisation — it requires `@astrojs/image` or the built-in image service.

Image locations to swap:
- `Hero.astro` × 1 (full-bleed felt close-up)
- `About.astro` × 1 (interior, brass-framed)
- `Coaching.astro` × 1 (coach demonstrating)
- `Gallery.astro` × 6 (masonry grid)

---

## 5. Deployment

This is a fully static site — `npm run build` outputs to `./dist`. Deploy anywhere that serves static files.

### Vercel (recommended — zero-config)
```bash
npm i -g vercel
vercel
```
Or push to GitHub → import on [vercel.com/new](https://vercel.com/new). Vercel auto-detects Astro.

### Netlify
1. `npm run build`
2. Drag `dist/` onto [app.netlify.com/drop](https://app.netlify.com/drop) **— or —**
3. Connect a GitHub repo; Netlify auto-detects Astro (build cmd `npm run build`, publish dir `dist`).

### Cloudflare Pages
1. Push to GitHub.
2. Cloudflare Dashboard → Workers & Pages → Create → Pages → Connect to Git.
3. Build command: `npm run build` · Output directory: `dist` · Framework: Astro.

### GitHub Pages / S3 / nginx
After `npm run build`, upload contents of `dist/` to any static host. Ensure the host serves `index.html` for the root path and respects the asset hashes.

---

## 6. Design system reference

| Token | Value | Use |
|-------|-------|-----|
| `ink` | `#0b0f0c` | Page background |
| `ink-soft` | `#111713` | Alternating section background |
| `felt` | `#0e4a2e` | Brand felt green |
| `felt-light` | `#1a6b46` | Lifted felt |
| `brass` | `#b08d57` | Borders, hairlines, micro-accents |
| `gold` | `#d4af37` | Primary CTAs, accent text (never body) |
| `cream` | `#f5e6c8` | Body text on dark — meets WCAG AA |
| `cream-muted` | `#cbb898` | Secondary text |
| `cream-dim` | `#9a8b6e` | Tertiary / metadata |
| `walnut` | `#3d2817` | Cards, dividers |

**Typography:**
- Display headings: `Playfair Display` (Google Fonts)
- Body / editorial copy: `Cormorant Garamond` (Google Fonts)
- UI / sans: `Inter` (Google Fonts)
- All three loaded in `Layout.astro` via Google Fonts CSS.

**Motion:**
- Reveal-on-scroll via vanilla IntersectionObserver in `Layout.astro`
- One ambient shimmer on hero scroll cue
- Respects `prefers-reduced-motion` globally

---

## 7. Accessibility checklist (already done)

- [x] Semantic HTML (`<main>`, `<nav>`, `<section>`, `<article>`, `<footer>`)
- [x] Skip-to-main-content link
- [x] All images have meaningful alt text (decorative use empty `alt=""`)
- [x] Form fields have labels + autocomplete + required hints
- [x] Brass focus rings on all interactive elements
- [x] Color contrast: cream `#f5e6c8` on ink `#0b0f0c` = 14.5:1 (AAA)
- [x] Gold reserved for accents only (gold on ink = 11.0:1, but small visual targets)
- [x] `prefers-reduced-motion` honoured (animations degrade to none)
- [x] Keyboard-navigable nav + form

Final check before launch: run [WAVE](https://wave.webaim.org) and [Lighthouse](https://developer.chrome.com/docs/lighthouse) against the deployed URL.

---

## 8. Performance budget

Targets: **Lighthouse Performance ≥95, Accessibility ≥95, SEO ≥95**.

To stay there:
- Keep hero image under 250KB (use AVIF/WebP)
- Don't add React/Vue/Svelte unless absolutely needed
- Lazy-load below-the-fold images (already done)
- If you add video, lazy-load + autoplay-muted only

---

## 9. SEO (already wired)

- Title + description on each page (via Layout `Props`)
- Canonical URL auto-computed
- Open Graph + Twitter Card tags
- JSON-LD `LocalBusiness` + `SportsActivityLocation` schema in `Layout.astro` — Google rich-result eligible
- `sitemap-index.xml` generated automatically by `@astrojs/sitemap`
- `robots.txt` in `public/`

---

## 10. v2 enhancements (when ready)

- **Real booking system:** Stripe Checkout or Razorpay for deposit-protected reservations
- **Membership portal:** Astro + Supabase auth; member-only event RSVPs
- **Photography:** commission a half-day shoot — felt textures, brass details, low-light interiors. This single change moves the site from "great template" to "Awwwards-eligible"
- **Custom shader hero:** subtle WebGL ripple on the felt (R3F + GLSL, ~30 LOC) for a real "wow" moment without bloat
- **Tournament leaderboards:** monthly bracket page driven by a Google Sheet via Astro's static fetch

---

## 11. Credits

- Astro https://astro.build
- Tailwind CSS https://tailwindcss.com
- Fonts: Playfair Display, Cormorant Garamond, Inter (Google Fonts, Open Font License)
- Placeholder photography: Unsplash — replace before launch
