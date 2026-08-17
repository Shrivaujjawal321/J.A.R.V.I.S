# THE EDITH — Frontend

Industrial maintenance control-room cockpit for EDITH, the steel plant maintenance copilot.

## Stack

- Next.js 16 (App Router) + React 19 + TypeScript
- Tailwind CSS 4 with OKLCH design tokens (EDITH design system)
- uPlot 1.6 — live sensor graphs, rAF-buffered, threshold bands
- react-resizable-panels v4 — 3-column draggable cockpit layout
- Zustand — live sensor state, alerts, chat
- TanStack Query v5 — REST polling (assets, reports)
- Native EventSource — SSE stream direct to backend (no Next proxy)
- Framer Motion 12 — panel mounts, alert animations, expandable cards
- Sonner — toast notifications for sensor breaches

## Prerequisites

1. Python FastAPI backend running at `http://127.0.0.1:8077`
2. Node 20

## Run (development)

```bash
cd edith/frontend
npm install
npm run dev
```

App opens at `http://localhost:3000`.

The backend must already be running. Do not start it from here.

## Build (production)

```bash
npm run build
npm run start
```

## Routes

| Route | Description |
|-------|-------------|
| `/` | Main cockpit — 3-panel layout: asset strip / sensor charts / alerts + copilot |
| `/report/[id]` | Printable report view. Add `?print=1` to strip nav for PDF capture. |

## Default focused asset

`HSM.F3.WR.BRG01` — a bearing that degrades into an alarm during the default seek window.

## Backend endpoints used

All requests go directly to `http://127.0.0.1:8077` (CORS open, no Next proxy).

| Method | Path | Used for |
|--------|------|----------|
| GET | `/api/assets` | Asset health strip (polled every 5s) |
| GET | `/api/asset/{id}` | Asset detail (sensors, scenarios) |
| GET | `/api/stream/{id}?speed=8&window=900&seek_event=true` | SSE live feed |
| POST | `/api/ask` | EDITH copilot queries |
| POST | `/api/report` | Generate a report |
| GET | `/api/report/{id}` | Load a saved report |

## Endpoints assumed but not yet in backend

| Method | Path | Purpose | Fallback behavior |
|--------|------|---------|----------|
| GET | `/api/report/{id}/pdf` | PDF download | Falls back to `window.print()` |
| GET | `/api/alerts` | Alert history on load | Empty state (SSE delivers live alerts) |

## Architecture notes

- SSE stream events (`meta`/`tick`/`alert`/`diagnosis`/`end`) drive all live state via native `EventSource` + Zustand.
- `tick` events are rAF-buffered — no `setState` per tick. uPlot's `setData()` is called once per animation frame.
- Sensor charts are uPlot canvas instances with threshold band plugins and dashed threshold lines drawn in `draw` hooks.
- Alert cards use `role="alert"` with `aria-live="assertive"` for ALARM severity.
- Reconnect: up to 10 automatic reconnects with 3s backoff, then a toast prompts manual reload.
- Stale detection: if no `tick` arrives within 8s the stream indicator turns "Stale".
