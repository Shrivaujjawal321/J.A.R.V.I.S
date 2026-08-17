"""VULCAN structured reports (WAVE 4 · reporting FR).

Three grounded, dataset-cited report builders, each rendered as Markdown (and
returnable as a dict for the UI / JSON export):

  * incident_report(...)  — a full per-incident maintenance report: diagnosis,
                            root cause, RUL, risk, prioritized actions, spare
                            procurement strategy, cost — every figure citing its
                            dataset source (spine / SOP / catalog).
  * alert_report(...)     — a real-time alert report from a fired alerting
                            episode: the WARNING->ALARM->CRITICAL escalation
                            timeline + the autonomous diagnosis hand-off.
  * decision_summary(...) — a one-screen action card a shift engineer reads in
                            10 seconds: risk band, the single next action, the
                            ORDER-NOW part, and the lead-time clock.

All builders are deterministic string assembly over the agentic findings + spine
data — NO LLM (the narrative prose, if any, is the supervisor's already-generated
answer). They never raise; missing data renders as an explicit 'not available'.
"""

from .builder import (
    incident_report,
    alert_report,
    decision_summary,
    save_report,
    Report,
)

__all__ = [
    "incident_report",
    "alert_report",
    "decision_summary",
    "save_report",
    "Report",
]
