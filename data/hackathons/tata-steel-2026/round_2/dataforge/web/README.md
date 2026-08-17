# DataForge — Dataset Quality Scoring by EDITH

Frontend for the DataForge platform: a 2026-tier dataset quality-scoring UI for industrial/steel data, branded as a product of **EDITH** (an AI dataset intelligence agent).

## Stack

- **Next.js 15** (App Router, Turbopack dev)
- **React 19** (Client Components where needed, Server default)
- **TypeScript 5** strict mode
- **Tailwind CSS v4** (OKLCH design tokens, dark-first)
- **Framer Motion 12** (spring physics, reduced-motion aware)
- **Recharts 3** (radar chart, no default color palette)
- **TanStack Query v5** (datasets page)
- **react-dropzone 15** (upload zone)
- **Geist Sans + Geist Mono** (next/font)

## Run locally

```bash
# Install dependencies
pnpm install

# Development server (port 3000)
pnpm dev
```

Open [http://localhost:3000](http://localhost:3000).

## Mock mode (no backend needed)

The app ships with a fully-working mock mode. When `NEXT_PUBLIC_USE_MOCK=1` (set in `.env.local`), all API calls return pre-built sample data — no backend required for demo purposes.

To switch to the real API:
1. Start the backend (`python -m dataforge.api` or similar, default port 8011)
2. Edit `.env.local`: set `NEXT_PUBLIC_USE_MOCK=0`
3. Restart dev server

## Environment variables

| Variable | Default | Description |
|---|---|---|
| `NEXT_PUBLIC_API_URL` | `http://127.0.0.1:8011` | Backend base URL |
| `NEXT_PUBLIC_USE_MOCK` | `1` | `1` = mock data, `0` = real API |

## Pages

| Route | Description |
|---|---|
| `/` | Landing + upload hero. Drag-drop zone, collapsible options, "Analyze with EDITH" CTA, how-it-works, trending preview. |
| `/result` | Audit result view. Animated score ring, readiness gauge, radar chart, dimension breakdown, EDITH review, improvement coaching cards, data preview. |
| `/datasets` | Dataset library. Bento cards, leaderboard table, top-ranked row. |

## Improve loop

When a user uploads a second dataset (via "Improve & re-upload"), the result page automatically detects the previous result and renders a before→after comparison: previous ring (ghost), new ring animating from old score, per-dimension delta arrows, and a floating score delta badge.

The previous result is persisted in `localStorage` under the key `dataforge_last_audit`.

## Build

```bash
pnpm build
pnpm start
```
