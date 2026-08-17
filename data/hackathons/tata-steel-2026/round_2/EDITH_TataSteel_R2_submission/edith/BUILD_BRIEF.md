# THE EDITH — Frontend Build Brief (cockpit)

Build a **local Next.js 15 + React 19** dark Stark-HUD control-room cockpit for "THE EDITH",
an industrial maintenance copilot for a steel plant. The Python FastAPI backend is ALREADY
built, running, and verified at `http://127.0.0.1:8077`. You build the frontend in
`edith/frontend/` and wire it to that backend.

## Locked product spec (decided by Boss — do not change)
- **One-screen unified cockpit:** live monitoring (center) + Ask-EDITH copilot + alerts feed.
- **Live monitoring:** a **15-asset health strip** (status tiles) + a **focused asset** detail
  with animated live sensor graphs. When all sensors are healthy the graph pattern is calm;
  when a sensor crosses its threshold the line turns its status colour, an **alert card** appears
  explaining *"sensor X crossed the warning/alarm threshold because its value is Y"*, with
  **resolution steps** and a **predicted impact/loss**.
- **Outputs follow the problem statement** (diagnosis · probable root cause · RUL prediction ·
  risk level · prioritized actions · recommendation). Each output **heading shows a short brief +
  an expand control ("drag/expand") that reveals an enhanced brief**. Simple, plain language.
- **Reports:** shareable (a `/report/{id}` web view) + downloadable (PDF).
- **Theme:** dark cyan/blue glass Stark-HUD, classy-simple (Linear/Vercel restraint + Grafana
  chart discipline). NOT a fake-terminal, NOT gauge-soup, NOT neon overload.

## Design system (USE THESE FILES — already written)
- `/home/ujjwal/Documents/J.A.R.V.I.S./data/design/edith-design-system/edith-theme.css`
  — Tailwind 4 `@theme` tokens + `.hud-panel` glass + status colours + keyframes + reduced-motion.
  Copy into `app/globals.css` (or import). OKLCH surface stack hue 250, accent hue 213.
- `/home/ujjwal/Documents/J.A.R.V.I.S./data/design/edith-design-system/components.tsx`
  — reference TSX for StatusTile, StatusBadge, KpiCard, AlertCard, OutputCard (expandable),
  CopilotPanel, ReportButtons, HudPanel, ChartCanvas. Adapt these; keep the a11y.
- `tokens.json` — the raw token tree.
Key rules: cyan accent on ≤10% of pixels (live data + interactive only); 3px status left-border +
~10% bg tint (never full-red cards); `critical-pulse` glow on box-shadow only; Geist + Geist Mono
(`next/font`), tabular-nums on all live numbers; respect `prefers-reduced-motion`.

## Stack (from 2026 research)
- Next.js 15 (App Router) · React 19 · TypeScript · Tailwind CSS 4 · shadcn/ui (compact)
- **Live charts: uPlot 1.6** (canvas, 60fps) for the sensor graphs — buffer SSE points in a
  `useRef` and flush once per `requestAnimationFrame`; fixed sliding window; NEVER `useState`
  per point. Draw **threshold bands** (warning amber `oklch(78% 0.17 78 / .08)`, alarm orange
  `oklch(72% 0.21 48 / .10)`) as filled regions + dashed threshold lines; on breach, the live
  line stroke switches to the status colour and the chart wrapper gets the status glow.
  (Recharts only for any static report chart.)
- Layout: `react-resizable-panels` v3 (left ~18% / center ~52% / right ~30%, draggable).
- State: **Zustand** for live sensor buffer + alerts feed + selected asset + chat; **TanStack
  Query** v5 for REST (assets, asset detail, predict, report).
- SSE: **native `EventSource`** straight to the backend (CORS is open — do NOT proxy SSE through
  Next rewrites, it buffers). Regular REST may go direct too (CORS `*`).
- Toasts: `sonner`. Expandable: Headless UI `Disclosure` + Framer Motion height spring.
- Alerts: dual-layer — `role="alert"` cards in the right feed (persistent) + sonner toast for info.

## Backend API contract (LIVE at http://127.0.0.1:8077 — verified)
- `GET /api/assets` → `{assets:[{asset_id, equipment_class, description, criticality,
  process_stage, health:"normal"|"warning"|"alarm", n_sensors}]}` (poll every ~5s for the strip).
- `GET /api/asset/{id}` → `{asset_id, equipment_class, description, criticality, process_stage,
  sensors:[{tag, quantity, unit, normal:[lo,hi], warning, alarm, direction:"upper"|"lower"}],
  scenarios:[{scenario_id, failure_mode, label, safety_class}]}`.
- `GET /api/stream/{id}?speed=8&window=900&seek_event=true` → **SSE**. Named events:
  - `meta`  `{type, asset_id, description, sensors:[<sensor meta>], rows}`
  - `tick`  `{type, ts, row, values:{tag:number|null}, status:{tag:"normal"|"warning"|"alarm"},
    worst, fault_label}`  ← drive the graphs + health from this, one per replayed historian row.
  - `alert` `{type, ts, asset_id, sensor, quantity, unit, value, threshold, severity:"WARNING"|"ALARM",
    row, reason}`  ← a fresh threshold crossing; render an alert card with the reason.
  - `diagnosis` `{answer, risk_band, rul, confidence, sources, findings:{<key>:{title, brief,
    detail, sources}}}`  ← fires on the first ALARM; render the PS-format expandable output cards.
  - `end` `{type, rows}`.
  Use `speed` to control replay rate (rows/sec). Default focused asset on load: `HSM.F3.WR.BRG01`
  (a bearing that degrades into an alarm within the seek window — good first impression).
- `POST /api/ask` `{query, session_id}` → `{answer, intent, asset_id, risk_band, rul, confidence,
  faithfulness, sources, findings:{<key>:{title, brief, detail, sources}}, trace}`. Copilot uses
  this; render `findings` as the expandable PS-format cards (diagnosis/rca/predictor/prioritizer/
  recommender keys), plus the prose `answer`, `sources` as citation pills, `risk_band` + `rul`
  as badges, `confidence`. (This call hits Claude — may take 5-30s; show a thinking state.)
- `GET /api/predict/{id}` → `{fault, anomaly, rul}` (each a dict; show in the focused panel).
- `POST /api/report` `{asset_id, scenario_id?, kind:"incident"|"decision"}` → `{report_id, report}`.
- `GET /api/report/{id}` → the saved report JSON.
- `GET /api/alerts` → recent alert history.

## Screens to build
1. **Cockpit `/`** — the 3-panel layout described above. Left = health strip (15 tiles from
   `/api/assets`, click to focus). Center = focused asset header (name/desc/criticality/RUL) +
   one uPlot graph per sensor (or a stacked multi-sensor graph) fed by the SSE `tick` stream with
   threshold bands; a small "replay speed" control; the `diagnosis` event renders the PS-format
   expandable output cards below the graphs. Right = alerts feed (from `alert` events, newest on
   top, severity colour, expandable reason+resolution+impact) on top, Ask-EDITH copilot below.
2. **Report `/report/[id]`** — a clean, branded, printable report page rendering the saved report
   (diagnosis, RCA, RUL, risk, prioritized actions, recommendation, citations, a sensor chart).
   `?print=1` hides nav for PDF capture. A "Download PDF" button (calls a backend PDF route — if
   not present yet, fall back to `window.print()`), and a "Copy share link" button.

## Run + deliver
- Scaffold with `npx create-next-app@latest edith/frontend` (TS, Tailwind, App Router, no src dir
  is fine). Use Node 20 (available), npm (available; no pnpm).
- `npm install` the deps. Make `npm run dev` serve on port 3000 cleanly.
- Provide a `README.md` with run steps (backend on 8077, frontend on 3000).
- Keep it ROBUST: handle SSE disconnect/reconnect, loading + empty + error states on every panel,
  stale-data dim if the stream goes silent, WCAG (icon+colour for status, not colour alone).
- Build for REAL data (the backend streams the real historian) — no mock/demo data in the UI.

When done: report what you built, the exact run commands, and any endpoint you assumed but the
backend doesn't yet expose (I'll add it). Do NOT start the backend — it's already running.
