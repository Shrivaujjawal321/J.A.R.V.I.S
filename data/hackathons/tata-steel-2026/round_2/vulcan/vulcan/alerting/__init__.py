"""VULCAN real-time alerting (WAVE 4 · FR7).

A deterministic, LLM-free condition-monitoring loop that REPLAYS a real asset's
dense sensor stream (`condition_monitoring/by_equipment/*.csv`) row-by-row and
fires a prioritized alert the instant a sensor crosses its spine threshold. The
detector itself never calls a model — it is pure arithmetic against the spine
thresholds, so it is fast and can never stall. On a CRITICAL fire it hands off to
the agentic core (`Supervisor.handle_alert`) for the explainable diagnosis+action.

Public API
----------
    from vulcan.alerting import ThresholdMonitor, AlertEngine, replay_episode
    eng = AlertEngine(asset_id="BF.BLW.FAN01")
    for ev in eng.stream():           # deterministic, no LLM
        print(ev.severity, ev.sensor, ev.value)
    episode = replay_episode("BF.BLW.FAN01")   # scripted WARNING->ALARM->CRITICAL demo
"""

from .detector import (
    AlertEvent,
    Severity,
    ThresholdMonitor,
    SensorState,
)
from .engine import AlertEngine, EpisodeResult, replay_episode, DEMO_EPISODES

__all__ = [
    "AlertEvent",
    "Severity",
    "ThresholdMonitor",
    "SensorState",
    "AlertEngine",
    "EpisodeResult",
    "replay_episode",
    "DEMO_EPISODES",
]
