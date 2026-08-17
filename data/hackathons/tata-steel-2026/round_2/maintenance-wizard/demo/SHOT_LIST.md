# Maintenance Wizard — OBS Shot List
## Tata Steel AI Hackathon 2026 · Round 2 · Screen Recording Setup
**Resolution: 1920×1080 | Frame rate: 30 fps | Audio: system mic or voiceover track**

---

## OBS SCENE SETUP

### Scene 1 — "Full Browser + Terminal Strip" (primary scene)
Used for all beats except Beat 4 (terminal-only).

```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│   Browser — Streamlit app (http://localhost:8501)                   │
│   Full width, top 85% of screen                                     │
│                                                                     │
│   Captures:                                                         │
│    • Sidebar: equipment selector + cost ticker (st.metric)          │
│    • Main area: chat bubbles, agent-step streaming, citation pills  │
│    • Toast alerts firing top-right corner                           │
│                                                                     │
│                                                                     │
├─────────────────────────────────────────────────────────────────────┤
│  Terminal strip — bottom 15% of screen (approx 160px)              │
│  Captures: curl commands + JSON output as beats execute            │
└─────────────────────────────────────────────────────────────────────┘
```

**OBS source config:**
- Source 1: Window Capture → "Firefox/Chrome — localhost:8501" — position: (0,0), size: 1920×900
- Source 2: Window Capture → "Terminal" — position: (0,900), size: 1920×180
- Audio: Built-in mic (or add voiceover in post via Audacity)

### Scene 2 — "Terminal Focus" (Beat 4 — agent trace)
```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│   Terminal — full screen, large font (16pt Monospace)               │
│                                                                     │
│   Shows:                                                            │
│    curl .../session/demo-gold-session-001/state output              │
│    (JSON formatted, piped through python3 -m json.tool)             │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

**Transition:** Cut (no fade) from Scene 1 to Scene 2 at the `curl` command.

---

## FONT / DISPLAY SETTINGS

Before recording:
- Browser zoom: **90%** (Ctrl+- once) so all sidebar + main area is visible without scroll
- Terminal font size: **14pt** (readable at 1080p)
- Streamlit dark mode: optional — but test it before recording. Light mode is safer for screen legibility.
- Close all notifications: `Do Not Disturb` mode on Ubuntu

**OBS recording settings:**
- Encoder: x264 (software) or NVENC if available
- Rate control: CRF 18 (high quality)
- Keyframe interval: 2s
- Container: MP4 (H.264 + AAC)
- Output path: `demo/recording_raw.mp4`

---

## NARRATION CUES — Beat by Beat

| Beat | Start | What's on screen | Narration trigger |
|------|-------|-------------------|-------------------|
| 0 — Hook | 0:00 | Chat page, sidebar ticker at ₹0 | Begin narration immediately |
| 1 — Problem | 0:22 | Dashboard heatmap, EAF-04 red | After heatmap loads fully |
| 2 — Alert WOW | 0:42 | Chat page + terminal strip visible | Speak "Watch." then execute curl |
| 3 — NL query | 1:30 | Chat input box in focus | Type query, then narrate as it streams |
| 4 — Chain | 2:05 | Expander open + terminal JSON | After expander visible, cut to terminal |
| 5 — Feedback | 2:25 | Thumbs-down button visible | Click then narrate |
| 6 — Ticker | 2:50 | Sidebar ticker, inject 2nd fault | Point at ticker, then curl |
| 7 — Close | 3:10 | Settings → Logbook → Dashboard | Narrate each tab switch |

---

## SHOT COMPOSITION DETAILS

### Beat 0 — Hook (0:00–0:22)
**Composition:** Full browser, sidebar left panel clearly visible.

Key elements to ensure visible:
- Sidebar title: "Maintenance Wizard — Tata Steel AI"
- Equipment selector showing "EAF-04 Electric Arc Furnace"
- Sidebar `st.metric`: "Prevented Downtime Cost ₹0"
- Chat page title: "Maintenance Co-pilot Chat"

**Camera move:** Static. No zoom, no pan. Let the UI speak.

**Narration cue:** Begin speaking the moment the browser is visible + stable.

---

### Beat 1 — Problem (0:22–0:42)
**Composition:** Dashboard page — heatmap takes center stage.

Key elements to ensure visible:
- 6×7 heatmap (equipment × days), RdYlGn colorscale
- EAF-04 column is **all dark red** (health score ~12, RUL 0.47 days)
- 6 RUL gauges in a 2×3 grid — EAF-04 gauge is crimson, needle pointing to 0
- Hover over EAF-04 gauge: tooltip shows "RUL: 0.47 days (11.3 hours)"

**Narration cue:** Begin after hovering on EAF-04.

---

### Beat 2 — WOW Alert (0:42–1:30)
**Composition:** Scene 1 (browser top + terminal bottom). This is THE money shot.

Key elements to ensure visible:
- Terminal shows the `curl -X POST .../inject_fault` command being typed
- 2-second pause AFTER pressing Enter (suspense)
- JSON response fills terminal: `"severity": "critical"`, `"rul_days": 0.4708`
- Browser: `st.toast` fires top-right corner — **bright red banner**
- Browser: sidebar ticker jumps from ₹0 to ₹8,55,000 (delta arrow up)

**Narration cue:** After terminal shows "injected" and toast fires, begin narration.

**Critical timing:** The `st.toast` fires via SSE within 1–2 seconds of the POST.
If the Streamlit UI doesn't show the toast, the **03_Alerts page** will show the alert
within 5 seconds (APScheduler tick). Navigate there as fallback.

**Backup shot:** Navigate to 03_Alerts, reload page, alert appears at top of list.

---

### Beat 3 — NL Query (1:30–2:05)
**Composition:** Chat page. Response streams agent-step by agent-step.

Key elements to ensure visible:
- `st.status("Routing to agents...")` spinner fires immediately on Enter
- Agent steps stream: "diagnosis node completed" → "rca node completed" → ...
- Final response has **citation pills** per source: `SOP-EAF-007 §4.3` `Incident #1847`
- Sources expander label: "Sources: SOP-EAF-007 §4.3, Incident #1847, Sensor T-12"

**Narration cue:** Begin narrating while the response is still streaming (shows it's live, not pre-canned).

**If response is slow (>10s):** The `st.status` spinner proves the system is working — narrate: "The six agents are running in sequence. Watch the step labels." This turns latency into a feature.

---

### Beat 4 — Agent Trace (2:05–2:25)
**Composition:** Switch to Scene 2 (terminal fullscreen) after expanding the Sources expander.

Key elements to ensure visible:
- Expander: collapsed label readable — "Sources: SOP-EAF-007 §4.3, Incident #1847"
- After expanding: traceable chain lines visible (sensor → SOP → incident → agent step)
- Terminal: `curl .../session/{id}/state` JSON output, formatted
- JSON shows `agent_trace` array with 6 entries + latency per step
- JSON shows `cited_sources` array with source IDs

**Narration cue:** After expander opens, say: "Every step is checkpointed." Then cut to terminal.

---

### Beat 5 — Feedback (2:25–2:50)
**Composition:** Chat page. The thumbs-down + correction form.

Key elements to ensure visible:
- Thumbs-down icon below the response (row of 👍 👎 buttons)
- After clicking: text input "Describe the correction..." appears
- After submitting: small confirmation: "Feedback recorded. WRPS weights updated via EMA."
- After re-querying: response header shows `[ENGINEER CORRECTION APPLIED]` badge (orange/amber)

**Terminal alternative:**
```bash
curl -s -X POST http://127.0.0.1:8000/v1/feedback \
  -H "Content-Type: application/json" \
  -d '{"session_id":"demo-gold-session-001","equipment_id":"EAF-04",
       "recommendation_id":"demo-rec-001","thumbs_up":false,
       "correction":"Root cause is misalignment.","corrected_risk_level":"critical"}'
```

**Narration cue:** Begin narrating the moment the correction text box appears.

---

### Beat 6 — Ticker (2:50–3:10)
**Composition:** Chat page sidebar, ticker in center focus.

**OBS tip:** Zoom the scene to 110% on the sidebar widget for 3 seconds — shows the metric cleanly. Then zoom back to 100%.

Key elements to ensure visible:
- `st.metric`: label "Prevented Downtime Cost", value "₹17,10,000", delta "+₹8,55,000"
- Or: value "₹8,55,000" before 2nd inject, then "+₹8,55,000" after
- Tooltip shows: "11.3h × ₹75,000/hr = ₹8,47,500 — source: Tata Steel rolling mill KPI"

**Narration cue:** After ticker increments, pause 2 seconds in silence — let the number land.

---

### Beat 7 — Close (3:10–3:40)
**Composition:** Three rapid tab switches.

Sequence:
1. Settings page (2 seconds) — show WRPS sliders + Demo Controls
2. Logbook page (5 seconds) — show 3–5 pre-seeded entries
3. Dashboard heatmap (10 seconds) — end frame, all 6 assets visible, EAF-04 red, others green/amber
4. Hold final frame 3 seconds — **this is the ending frame for the video thumbnail**

**Narration cue:** Each tab switch gets 1 sentence.

**Ending frame:** Dashboard heatmap with sidebar cost ticker visible. EAF-04 visibly red.
This is the "hero shot" — what judges remember.

---

## POST-PRODUCTION CHECKLIST

- [ ] Trim dead time at start/end (keep tight)
- [ ] Add title card (5 seconds): "Maintenance Wizard — Tata Steel AI Hackathon 2026 · Round 2"
- [ ] Add chapter markers in YouTube description matching beats above
- [ ] Caption / subtitle track (optional, improves accessibility for reviewing judges)
- [ ] Check audio: no background noise, narration clearly audible
- [ ] Export: MP4, H.264, 1920×1080, 30fps, ≤500MB
- [ ] Upload: YouTube unlisted → grab share link for submission form
- [ ] Keep raw OBS file as backup (MP4 backup in submission ZIP)

---

## TERMINAL FONT SETUP (Ubuntu)

```bash
# Set GNOME terminal font for recording:
gsettings set org.gnome.Terminal.Legacy.Profile:/org/gnome/terminal/legacy/profiles:/:default/ \
  font 'Monospace 14'
# Or: Right-click terminal → Preferences → Text → Font → Monospace 14
```

---

## BACKUP RECORDING PLAN

If OBS crashes mid-recording:
1. The `data/demo/demo_cache.json` file is already saved — show it in a file manager.
2. Use `asciinema` to record terminal-only: `asciinema rec demo/terminal_demo.cast`
3. Convert to video: `agg demo/terminal_demo.cast demo/terminal_demo.gif`
4. Include as supplementary material in the submission ZIP.

---

## QUICK-START RECORDING COMMANDS

```bash
# Window 1 — backend (leave running)
cd maintenance-wizard
BACKEND_PORT=8000 .venv/bin/uvicorn wizard.backend.app:app \
  --host 127.0.0.1 --port 8000 --workers 1 2>&1 | tee data/demo/backend.log

# Window 2 — UI (leave running, BACKEND_PORT must match backend)
BACKEND_PORT=8000 .venv/bin/streamlit run wizard/ui/app.py --server.port 8501 --server.headless true

# Window 3 — demo commands (use this during recording)
# Beat 2:
curl -s -X POST http://127.0.0.1:8000/v1/demo/inject_fault | python3 -m json.tool
# Beat 4:
curl -s http://127.0.0.1:8000/v1/session/demo-gold-session-001/state | python3 -m json.tool | head -60
# Beat 5:
curl -s -X POST http://127.0.0.1:8000/v1/feedback \
  -H "Content-Type: application/json" \
  -d '{"session_id":"demo-gold-session-001","equipment_id":"EAF-04","recommendation_id":"demo-rec-001","thumbs_up":false,"correction":"Root cause is misalignment, not thermal overload.","corrected_risk_level":"critical"}' \
  | python3 -m json.tool
# Beat 6 (2nd inject):
curl -s -X POST http://127.0.0.1:8000/v1/demo/inject_fault | python3 -m json.tool
```
