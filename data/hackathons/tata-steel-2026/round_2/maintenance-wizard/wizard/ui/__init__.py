"""
wizard.ui
=========
Streamlit 1.58 multipage frontend for Maintenance Wizard.

Entry point: wizard/ui/app.py
Run with: streamlit run wizard/ui/app.py

Pages:
  01_Chat.py      — Multi-turn maintenance co-pilot chat (st.write_stream, citations, feedback)
  02_Dashboard.py — Equipment health gauges + 7-day heatmap (Plotly, st.cache_data ttl=30)
  03_Alerts.py    — Real-time alert feed (st.fragment run_every=3, acknowledge workflow)
  04_Logbook.py   — Historical maintenance records + CSV export (sqlite3 + pandas)
  05_Settings.py  — System health + demo controls + session summary

Internal modules:
  _http.py        — httpx.Client (sync) singleton per session
  _demo_seed.py   — Pre-seeded demo data (ensures content on first load)

CRITICAL: httpx.Client (sync) ONLY throughout this package.
Never use httpx.AsyncClient or asyncio.run() — Streamlit runs its own event loop.
"""
