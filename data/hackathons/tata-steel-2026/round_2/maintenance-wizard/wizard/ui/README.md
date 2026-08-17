# wizard.ui

# wizard.ui — Streamlit Frontend

Streamlit 1.58 multipage app for Maintenance Wizard.

## Entry point

```bash
streamlit run wizard/ui/app.py
```

## Pages

| File | URL slug | Purpose |
|---|---|---|
| `app.py` | (frame) | Navigation, sidebar cost ticker, alert badge |
| `pages/01_Chat.py` | /Chat | Multi-turn co-pilot: st.write_stream + citations + traceable chain + feedback |
| `pages/02_Dashboard.py` | /Dashboard | go.Indicator RUL gauges + go.Heatmap 7-day health |
| `pages/03_Alerts.py` | /Alerts | st.fragment run_every=3 alert feed + acknowledge |
| `pages/04_Logbook.py` | /Logbook | sqlite3 read + pandas + CSV export |
| `pages/05_Settings.py` | /Settings | Health check + demo controls + session summary |

## Internal modules

- `_http.py` — `httpx.Client` (sync) singleton per session. **Never AsyncClient.**
- `_demo_seed.py` — Pre-seeded demo data so every page shows content on first load.

## Critical constraint

Streamlit runs its own event loop. Using `httpx.AsyncClient` or `asyncio.run()` inside
any Streamlit callback raises `RuntimeError: This event loop is already running`.

**Rule: `httpx.Client` (sync) ONLY throughout `wizard.ui.*`.**

## Wow moments implemented

1. **Live Cost-Avoidance Ticker** — sidebar `st.metric` via `st.fragment(run_every=5)`.
   Accumulates `avoided_hours × ₹75,000/hr` for CRITICAL/HIGH events only.
2. **Traceable Diagnosis Chain** — collapsed `st.expander` per message showing
   sensor → SOP(§+page) → historical incident → agent step.
3. **Streaming LLM output** — `st.write_stream` with typewriter character generator.
4. **Citation pills** — `st.badge` per source citation inline in chat.
5. **Feedback loop** — thumbs up/down + correction text → `POST /v1/feedback`.

## Smoke test

```bash
python wizard/ui/smoke_ui.py
```

Expected: `SMOKE PASS — wizard.ui ready`

