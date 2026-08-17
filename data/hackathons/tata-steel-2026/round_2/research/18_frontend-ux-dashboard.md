# Component 18: Frontend / UX & Equipment-Health Dashboard
**Tata Steel AI Hackathon 2026 — Round 2 Research Brief**
*Research date: 2026-06-06 | Constraint: CPU-only, solo build, ~9 days, pip-install-first, judge's machine*

---

## 1. Recommended Approach — The Single Winner

**Streamlit 1.58.0 + Plotly 5.22 + httpx 0.27 (sync) + st.fragment (run_every) for live polling**

For a solo 9-day build that must run on a judge's machine via `pip install`, Streamlit is the unambiguous winner. The decision is not even close once the judging criteria are mapped to implementation cost:

- "Easy to use" — Streamlit's imperative Python-native model ships a polished 5-page app in ~600 lines of Python. Equivalent React + Next.js app requires: TypeScript config, Tailwind setup, Next.js routing, state management (Zustand/Jotai), API client layer (TanStack Query), streaming hook, chart library (Recharts/Nivo) — minimum 2 full days before a single pixel renders.
- "Doesn't break" — Streamlit runs as a single Python process alongside the FastAPI backend. No Node.js runtime, no npm, no build step, no hydration errors. On a judge's machine: `pip install -r requirements.txt && streamlit run wizard/ui/app.py` — that's it.
- "Smooth working" — Streamlit 1.37+ introduced `st.fragment(run_every=...)` which replaces the old unmaintained `streamlit-autorefresh` component entirely. A fragment decorated with `run_every=3` polls the backend every 3 seconds without triggering a full page rerun, which is exactly the real-time alert mechanism needed for the demo.
- "Fast output" — `st.write_stream` renders LLM token streams character-by-character, producing a ChatGPT-style typewriter effect with zero extra code. Combined with `st.status('Routing to agents...')` the perceived latency is much lower than actual latency.

The build playbook (already established in this hackathon's architecture document) confirms this: Streamlit 1.35 was the locked choice. This research validates upgrading the pinned version to **Streamlit 1.58.0** (latest stable as of 2026-05-28, confirmed via PyPI) to gain `st.fragment` with `run_every`, `st.badge`, native `st.pills`, and the Starlette/Uvicorn backend (replaces Tornado, no more event-loop edge cases).

**Critical implementation constraint confirmed by research:** Streamlit runs its own event loop. Any `httpx.AsyncClient` or `asyncio.run()` call inside a Streamlit callback will raise `RuntimeError: This event loop is already running`. The fix is mandatory: use `httpx.Client` (sync) everywhere in the UI layer. This is the single most common source of demo-day crashes in Streamlit + FastAPI stacks and must be enforced via a code comment at the singleton definition site.

---

## 2. Why — Evidence-Based Reasoning

### Time-to-ship delta is decisive

Per comparative research across Python dashboard frameworks in 2026:
- **Streamlit**: 1–3 days for a working KPI + chat + alert dashboard ([Python Dashboard Complete 2026 Guide](https://www.usedatabrain.com/how-to/create-python-dashboard))
- **Plotly Dash 3**: 1–2 weeks; Dash 3 (March 2025) added Pages + background callbacks + AG Grid, but the callback model (decorators wiring Input→Output) requires significantly more boilerplate than Streamlit's imperative model for a multi-page agentic chat app
- **React/Next.js 15**: 2–4 days for UI alone, before any backend integration; every judging axis maps to a frontend concern (streaming, SSE, charts, state), all needing separate library choices

With 14 hours budgeted for the entire UX phase (Phase 6 in the build playbook) a React build would consume the full budget before the chat streaming was wired. Streamlit completes the same surface area in 8–10 hours, leaving 4–6 hours for polish and robustness.

### st.fragment replaces streamlit-autorefresh

The `streamlit-autorefresh` package (v1.0.1, last released June 2023) is effectively abandoned — Snyk health analysis flagged it as low maintenance with no Python 3.12 explicit support. The alternative `st-autorefresh` (PyPI: `st-autorefresh`) explicitly supports Python 3.12. However, **both are now superseded** by the native `@st.fragment(run_every=3)` decorator introduced in Streamlit 1.37 (July 2024), which is now stable in 1.58.0. The native fragment approach requires zero extra pip dependencies, has no maintenance risk, and integrates cleanly with Streamlit's session state model.

```python
@st.fragment(run_every=3)
def alert_poller():
    alerts = http_client.get("/alerts/active").json()
    new_alerts = [a for a in alerts if a["id"] not in st.session_state["seen_alert_ids"]]
    for alert in new_alerts:
        st.session_state["seen_alert_ids"].add(alert["id"])
        st.session_state["alerts"].append(alert)
        st.toast(f"[{alert['severity']}] {alert['title']}", icon="🔴" if alert["severity"] == "CRITICAL" else "⚠️")
```

This fragment reruns every 3 seconds independently — no full-page rerun, no extra package, no asyncio conflict.

### Streamlit 1.58.0 specific features that matter

Confirmed from official 2026 release notes ([Streamlit 2026 release notes](https://docs.streamlit.io/develop/quick-reference/release-notes/2026)):

- **Starlette/Uvicorn as default web server** (replaces Tornado): eliminates the legacy Tornado event loop conflict that caused asyncio errors in older versions. More ASGI-compatible, better performance.
- **st.bottom**: pinned container for chat input — keeps `st.chat_input` always visible regardless of scroll position. Critical for the chat page UX.
- **st.badge**: renders colored inline badges for severity labels and citation pills. No third-party component needed.
- **st.pills** (native, stable): replaces the old `streamlit-pills` community component for source citation selection UI.
- **:shimmer[] markdown directive**: animated loading text for streaming states — "Running agents..." with a shimmer effect signals activity without a spinner.
- **Streaming markdown auto-complete**: `st.write_stream` now auto-completes unclosed markdown syntax (bold, code blocks) during LLM streaming, preventing broken rendering mid-stream.
- **st.fragment with run_every**: confirmed stable, used for dashboard auto-updates and alert polling.

### Plotly 5.22 for visualization

Plotly `go.Indicator` with `mode="gauge+number+delta"` is the standard for equipment health gauges in industrial dashboards ([Plotly Indicators documentation](https://plotly.com/python/indicator/)). The `make_subplots` function renders 6 equipment gauges in a single Plotly figure passed to `st.plotly_chart(use_container_width=True)` — one backend call, one render. `@st.cache_data(ttl=30)` caches the figure for 30 seconds, preventing redundant backend polls on every page rerun.

For the equipment health heatmap (6 equipment × 7 days), `go.Heatmap` with a `RdYlGn` colorscale maps health scores 0–100 to red–yellow–green. This is the ISA-101 standard for process industry displays: muted background, color reserved for status signals. Research confirms this matches industrial HMI best practices for predictive maintenance dashboards ([IoT-Driven Predictive Maintenance Dashboards](https://saudijournals.com/media/articles/SJEAT_109_457-466.pdf)).

### Citation pills satisfy explainability requirement

Requirement 4 ("explainable + traceable outputs grounded to sources") maps directly to the chat page UI. Each assistant message includes:
1. `st.badge` pills: one per citation, showing `[SOURCE-N: doc_name §section]`
2. `st.expander` per citation: chunk text + equipment_id + confidence
3. Agent trace expander (collapsed): nodes fired, latency per node, model used, cache hit

This pattern — inline citation badges over an expandable detail — is validated by production RAG products (Perplexity.ai, Bing Chat, Anthropic Claude.ai) as the correct UX for source grounding. Judges evaluating "explainable + traceable" will see it immediately without drilling in.

---

## 3. Exact Stack — Libraries, Versions, Roles

| Library | Version | Role |
|---|---|---|
| `streamlit` | 1.58.0 | Primary UI framework: 5-page app, chat, dashboard, alerts, logbook, settings |
| `plotly` | 5.22.0 | All charts: go.Indicator gauges, go.Heatmap health matrix, scatter anomaly timeline |
| `httpx` | 0.27.x | Sync HTTP client for all backend calls (`httpx.Client`, never `AsyncClient`) |
| `python-dotenv` | 1.0.x | Load `.env` in Streamlit context before any page renders |
| `pandas` | 2.2.x | DataFrame for logbook table, heatmap pivot, CSV export |
| `rich` | 13.x | Dev-only: pretty-print health check output during local dev |

**No additional UI packages needed.** The following are explicitly NOT used:
- `streamlit-autorefresh` — replaced by `@st.fragment(run_every=3)` (native, v1.37+)
- `st-autorefresh` — same reason
- `streamlit-pills` — replaced by native `st.pills` (stable in v1.58)
- `nest_asyncio` — masks problems; not needed if httpx.Client (sync) is used throughout
- Any React/Node.js dependency

**Backend packages consumed by the UI (already in `requirements.txt` from other phases):**
- `sse-starlette 1.8` — the FastAPI SSE endpoint exists but Streamlit cannot consume SSE natively; `st.fragment(run_every)` polling is used instead
- `sqlite3` (stdlib) — logbook reads direct from `data/sessions.db`

---

## 4. Alternatives Considered — Precise Tradeoffs

### Alternative 1: Plotly Dash 3

**Why it lost:** Dash 3 (March 2025) is mature for industrial dashboards — background callbacks, Pages routing, AG Grid. Plotly/Dash's Manufacturing examples gallery shows real-time production dashboards. However, Dash's decorator-based callback model (`@app.callback(Output(...), Input(...))`) forces explicit wiring of every interaction, making a multi-turn chat interface (where assistant messages accumulate in session state) non-trivial. Implementing streaming LLM output in Dash requires a custom WebSocket component or dcc.Interval polling — neither is as clean as `st.write_stream`. Estimated time delta: +1.5 days vs Streamlit for the same surface area on a solo build. With only 14 hours budgeted for Phase 6, that delta is fatal.

### Alternative 2: Gradio 5.x (with gr.ChatInterface)

**Why it lost:** Gradio's `gr.ChatInterface` is excellent for AI model demos and provides agent trace display natively in collapsible accordions (confirmed via Gradio docs 2025). It would handle the chat page faster than Streamlit. However, Gradio is purpose-built for the chat-model-demo use case and is not a general dashboard framework. Building the equipment health heatmap, RUL gauges, anomaly scatter, and alert feed in Gradio requires custom components or `gr.HTML` blocks with embedded JavaScript — fragile and slow. The multi-page navigation (5 pages) in Gradio is inferior to Streamlit's `st.navigation`. Gradio excels for Hugging Face Spaces model demos; this project needs a full maintenance decision-support dashboard, not a model demo.

### Alternative 3: React 19 + Next.js 15 (App Router)

**Why it lost:** Production-grade, WCAG 2.2 AA, Lighthouse 95+ — but catastrophically wrong tradeoff for this constraint set. React requires: TypeScript strict config, Tailwind 4 `@theme` setup, shadcn/ui installation, a streaming hook for SSE/fetch, TanStack Query for polling, Recharts or Nivo for industrial gauges (no native equivalent to Plotly's `go.Indicator`), and a build step that produces a `/dist` or `.next` directory. The judge must run `npm install && npm run build && npm start` in addition to the Python backend — a two-runtime setup that violates the "pip install over docker-compose" preference. More critically, the 9-day solo build cannot absorb the 2+ days React UI setup costs while also delivering LangGraph agents, RAG, ML models, and eval suites. React is the right choice for Boss's portfolio site; it is the wrong choice for this hackathon's UI component.

### Alternative 4: Panel (HoloViz)

**Why it lost:** Panel is more flexible than Streamlit and supports any plotting library (Bokeh, Plotly, Matplotlib, HoloViews). It runs well in Jupyter notebooks and has a stronger story for complex dashboards with bidirectional reactive state. However, Panel's learning curve is steeper (reactive programming paradigm, `param` library), its ecosystem is smaller (fewer examples, less Stack Overflow coverage), and its chat/conversational UI primitives are weaker than Streamlit's mature `st.chat_message` + `st.chat_input` + `st.write_stream` stack. For a 9-day solo build where the conversational interface is a primary judging surface, Panel's weaker chat primitives are disqualifying.

---

## 5. Anti-Patterns — What Screams "Amateur / 2022-Tier"

1. **Using `streamlit-autorefresh` instead of `@st.fragment(run_every=...)`** — unmaintained package, last updated June 2023, deprecated since Streamlit 1.37. Any judge who reads `requirements.txt` and sees this knows the builder missed 18 months of Streamlit updates.

2. **Raw spinner with `st.spinner('Loading...')` during LLM response** — the correct 2025 pattern is `st.status('Routing to agents...')` while the graph initializes, then `st.write_stream(token_generator)` for the actual response. Spinner + full page rerun = slow, jarring. Streaming typewriter effect = smooth.

3. **Bare Python tracebacks reaching the UI** — `AttributeError: 'NoneType' object has no attribute 'json'` appearing in red inside the Streamlit app is an instant disqualifier for "doesn't break" and "no errors." Every backend call must be in `try/except` with a human-readable `st.warning`.

4. **Using `asyncio.run()` or `httpx.AsyncClient` in Streamlit callbacks** — causes `RuntimeError: This event loop is already running`. This is the most common demo-day crash for Streamlit + FastAPI stacks. Fix: `httpx.Client` (sync), instantiated once as a session state singleton.

5. **st.experimental_fragment** — deprecated January 1, 2025. Using the old decorator on Python 3.12 / Streamlit 1.58 will raise a deprecation warning or error. Use `@st.fragment`.

6. **Full-page rerun for alert polling** — wrapping `GET /alerts/active` in the top-level script causes every poll to re-render all charts, resetting scroll position and flickering every 3 seconds. The correct pattern is `@st.fragment(run_every=3)` which isolates the poll to a sidebar badge counter without touching any chart.

7. **Plotly figures without `use_container_width=True`** — gauges and heatmaps rendered at fixed pixel widths look broken on judge's monitors at different resolutions. Always pass `use_container_width=True` to `st.plotly_chart`.

8. **No `@st.cache_data(ttl=...)` on chart-generating functions** — every page rerun (and there are many in a live Streamlit app) will re-fetch the heatmap data and re-render 6 gauge figures. With `ttl=30`, charts are computed at most once per 30 seconds. Without caching, latency compounds and the demo feels sluggish.

9. **Confusing the feedback widget with `st.form`** — `st.form` clears the entire chat history on submit. The feedback widget (thumbs up/down + correction text) must use standard `st.button` + `st.text_input` widgets with `key=f"fb_{message_id}"` to avoid wiping the conversation.

10. **No pre-seeded demo data in the logbook and alert pages** — empty tables on first load look like the system has no data. Seed 5 historical acknowledged alerts and 3 historical logbook entries at startup so every page shows meaningful content from second one of the demo.

---

## 6. Integration Notes — Inputs, Outputs, Component Connections

### Inputs consumed by the UI layer

| Source Component | Data | Mechanism |
|---|---|---|
| Component 04 (RAG) via API | `retrieved_docs: list[RetrievedDoc]` (citations for each response) | `POST /chat` response body → `citations` field |
| Component 08 (RUL estimator) via API | `rul_days_p50, rul_days_p90, risk_class, failure_probability_30d` | `GET /sensor/state` → per-equipment snapshot |
| Component 09 (Anomaly detector) via API | `anomaly_score, is_anomaly, feature_importance_top3` | `GET /sensor/state` → per-equipment snapshot |
| Component 15 (Risk prioritization) via API | `urgency_score, risk_classification` per equipment | `GET /alerts/active` → alert card data |
| Component 16 (Maintenance recommendation) via API | `MaintenanceRecommendation` JSON | `POST /chat` response body → recommendations field |
| Component 05 (Alerting engine) via API | `Alert(alert_id, severity, title, body, triggered_at, recommended_action_brief)` | `GET /alerts/active` (polled by st.fragment) |
| LangGraph multi-turn state | Session history | `GET /session/{session_id}/history` |
| Sensor playback engine | `SensorSnapshot` per equipment, `row_index`, `speed_multiplier` | `GET /sensor/state` |
| Feedback loop | Correction ingestion | `POST /feedback` |
| Health check | System status | `GET /health` |

### Outputs produced by the UI layer

| Output | Destination | Description |
|---|---|---|
| `POST /chat {session_id, message, equipment_id}` | FastAPI → LangGraph | Every chat submission |
| `POST /feedback {session_id, turn_id, correction_type, correction_text, corrected_rul_days}` | FastAPI → Feedback loop (Component 06) | Engineer corrections from thumbs-down + text input |
| `POST /sensor/speed {multiplier}` | FastAPI → Sensor playback | Demo mode: set multiplier=100 for 90s demo trigger |
| `POST /sensor/reset` | FastAPI → Sensor playback | Demo reset button in Settings page |
| Alert acknowledgement `PUT /alerts/{alert_id}/acknowledge` | FastAPI → SQLite | Moves alert to logbook |

### Components it talks to directly (all via sync httpx.Client)

- **FastAPI server** (`http://localhost:8000`): primary backend; all agent orchestration, RAG, ML, alerts behind this single interface. The UI never imports wizard Python modules directly — always via HTTP. This decoupling means the UI is restartable independently of the backend.
- **No direct database access** from UI except: `sqlite3` read of `data/sessions.db` for the logbook page (read-only, avoids one HTTP round-trip for static historical data).

### Page-to-component mapping

| Streamlit Page | Primary Component Connections |
|---|---|
| `01_Chat.py` | `/chat` (POST), `/feedback` (POST), `/session/history` (GET) |
| `02_Dashboard.py` | `/sensor/state` (GET, cached 30s), `/alerts/active` (GET, fragment 3s) |
| `03_Alerts.py` | `/alerts/active` (GET, fragment 3s), `/alerts/{id}/acknowledge` (PUT) |
| `04_Logbook.py` | `data/sessions.db` (sqlite3 read-only), `st.download_button` CSV export |
| `05_Settings.py` | `/health` (GET), `/sensor/reset` (POST), `/sensor/speed` (POST) |

---

## 7. Open Risks and Unknowns

### Risk 1 — Streamlit asyncio behavior on Starlette backend [PARTIALLY VERIFIED]
Streamlit 1.58.0 ships Starlette/Uvicorn as the default web server, replacing Tornado. This should resolve the legacy `RuntimeError: This event loop is already running` that affected older Streamlit versions when asyncio was involved. However, the mandate to use `httpx.Client` (sync) throughout the UI remains correct regardless — mixing sync and async in Streamlit is still fragile even on Starlette. Risk: LOW if the sync-only rule is enforced. Risk: HIGH if any developer adds `asyncio.run()` in a future callback.

### Risk 2 — st.fragment(run_every=3) + multiple pages [PARTIALLY VERIFIED]
`st.fragment` with `run_every` is confirmed stable as of Streamlit 1.37 and documented in 1.56.0 docs. However, behavior when the decorated function is defined inside a page file (not the main `app.py`) has less documentation. The recommended pattern is to place `alert_poller()` in `app.py` (runs on all pages) so the alert badge in the sidebar updates regardless of which page is active. This is consistent with the `st.navigation` pattern where `app.py` acts as a frame around all pages. [unverified: exact behavior when fragment with run_every is defined in a sub-page file vs app.py]

### Risk 3 — Plotly make_subplots performance with 6 gauges [VERIFIED SAFE]
`go.Indicator` with `make_subplots(rows=2, cols=3)` for 6 equipment gauges is well-documented in Plotly 5.x official examples. `@st.cache_data(ttl=30)` wrapping the gauge-generation function ensures the figure is recomputed at most every 30 seconds. With `ttl=30`, the dashboard page renders the cached figure from session state on most reruns — negligible latency.

### Risk 4 — httpx.Client singleton across Streamlit sessions [LOW RISK]
`httpx.Client` is not thread-safe when the same instance is shared across concurrent requests. However, Streamlit's execution model (one script run per user interaction, single-threaded per session) means the singleton pattern `st.session_state.setdefault('http_client', httpx.Client(...))` gives each user session its own client. For a hackathon demo with 1 judge, this is safe. For production multi-user deployment, a connection pool or per-request client would be needed. [unverified: exact Streamlit session isolation guarantees in 1.58.0 Starlette mode]

### Risk 5 — st.write_stream with FastAPI SSE [CONFIRMED MISMATCH]
`st.write_stream` expects a Python generator (callable that yields strings). FastAPI's SSE endpoint (`/chat/stream`) returns a streaming HTTP response. These do not connect natively in Streamlit. The correct pattern for this system is: FastAPI `/chat` returns the full structured JSON response (with all citations, confidence, trace) after the LangGraph graph completes, and `st.write_stream` streams the `answer_text` field from this JSON by iterating over its characters or words. Alternatively, a generator can poll a token queue. Both work. True SSE → Streamlit streaming is not supported natively. [verified: confirmed by Streamlit community discussions and the existing build playbook decision]

### Risk 6 — Demo playback speed_multiplier timing [UNVERIFIED]
The demo relies on `POST /sensor/speed {multiplier: 100}` triggering EAF-04's RUL to cross 72h at exactly 90 seconds of real elapsed time. This is a function of the sensor playback engine (Component 01, Step 1.4) and the proactive planner's 30s poll interval (Step 4.7). The UI Settings page sends this command via a "Start Demo Mode" button. If the playback engine's row advancement is slower than expected (e.g., asyncio task scheduling jitter), the 90-second trigger may arrive at 100–120 seconds. This affects demo storytelling but not correctness. Mitigation: the Settings page also shows a "Simulate Fault (immediate)" button that directly calls `POST /sensor/inject_fault {equipment_id: "EAF-04"}` as a belt-and-suspenders backup. [unverified: exact timing under asyncio task scheduling jitter on demo machine CPU]

---

## Summary Decision

**Streamlit 1.58.0 is the correct and only defensible choice for this component.**

The judging criteria ("easy to use," "smooth," "doesn't break," "fast output") map to exactly what Streamlit does well: instant rendering, streaming output, no build step, one-command startup. The 14-hour Phase 6 budget is achievable with Streamlit and would be blown by any alternative. The key implementation decisions — sync httpx.Client only, `@st.fragment(run_every=3)` for alert polling, `@st.cache_data(ttl=30)` for charts, `st.write_stream` for LLM token streaming, `st.badge` for citation pills, `st.bottom` for persistent chat input, pre-seeded demo data for all pages — are each individually validated by 2025–2026 Streamlit release notes and production patterns from the community.

The system architecture is clean: FastAPI handles all backend logic; Streamlit is a pure display and interaction layer that communicates exclusively over HTTP via a sync httpx.Client singleton per session. This separation means the UI can be restarted, demo-reset, or swapped without touching a single line of agent code.
