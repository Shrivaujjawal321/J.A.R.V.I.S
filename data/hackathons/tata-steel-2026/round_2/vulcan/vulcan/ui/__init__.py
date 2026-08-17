"""VULCAN UI (WAVE 5) — Streamlit front end.

A dark, clean, branded (VULCAN / EDITH) operator console wired to the WAVE 1-4
agentic core. Four pages:

  app.py            — Chat (EDITH): NL + multi-turn, inline citations, the
                      "show your work" reasoning trace, RUL + risk badges,
                      one-click demo chips.
  pages/2_Health…   — Fleet health dashboard: 15 assets, per-asset RUL / anomaly /
                      fault status, risk-coloured tiles + drill-down.
  pages/3_Alerts…   — Real-time alerting feed (FR7): replay an episode, watch the
                      WARNING→ALARM→CRITICAL escalation + autonomous diagnosis.
  pages/4_Reports…  — View / generate the structured maintenance reports.

Run:  streamlit run vulcan/ui/app.py
"""
