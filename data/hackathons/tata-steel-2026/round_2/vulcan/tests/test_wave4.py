"""WAVE 4 tests — alerting (FR7), feedback loop (FR6), structured reports.

All tests here are deterministic and LLM-free (the agentic hand-off is exercised
manually via verify_wave4, not in CI — it needs the subscription + 50s). These
lock in the verified behaviour:

  * the deterministic detector fires WARNING -> ALARM -> CRITICAL on the REAL
    spine asset BF.BLW.FAN01 / SCN-041 (compressor surge on PRES.OSC),
  * an engineer's feedback demonstrably moves the priority weight,
  * the three report builders render grounded Markdown without an LLM.

Run:  /home/ujjwal/Documents/J.A.R.V.I.S./.venv/bin/python -m pytest tests/test_wave4.py -v
"""

from __future__ import annotations

import pytest

from vulcan.alerting import replay_episode, AlertEngine, Severity
from vulcan.feedback import FeedbackStore
from vulcan.reports import incident_report, alert_report, decision_summary, Report


# ===========================================================================
# FR7 — deterministic real-time alerting on a REAL spine asset (no LLM)
# ===========================================================================
def test_alert_replay_fires_critical_on_real_asset():
    """BF.BLW.FAN01 / SCN-041 surge must escalate WARNING->ALARM->CRITICAL."""
    res = replay_episode("BF.BLW.FAN01", handoff=False, persist=False)
    assert res.asset_id == "BF.BLW.FAN01"          # REAL spine asset, not a phantom
    assert res.scenario_id == "SCN-041"
    assert res.fired is True                        # autonomous CRITICAL trip
    assert res.first_warning is not None
    assert res.first_alarm is not None
    assert res.first_critical is not None
    # the escalation is monotonic in severity AND in row order (time)
    fw, fa, fc = res.first_warning, res.first_alarm, res.first_critical
    assert fw.severity == Severity.WARNING
    assert fa.severity >= Severity.ALARM
    assert fc.severity == Severity.CRITICAL
    assert fw.row_index <= fa.row_index <= fc.row_index


def test_critical_fires_at_correct_threshold_and_sensor():
    """The CRITICAL must be the surge sensor crossing its spine ALARM threshold."""
    res = replay_episode("BF.BLW.FAN01", handoff=False, persist=False)
    fc = res.first_critical
    assert fc.sensor == "JSR.BF.BLW.FAN01.PRES.OSC"   # discharge-pressure oscillation
    assert fc.alarm_threshold == 8                    # spine API-670 surge alarm
    assert fc.value >= fc.alarm_threshold             # actually crossed it
    assert fc.scenario_id == "SCN-041"                # hands off the right scenario
    assert "by_equipment" in fc.source               # cites the real replay source


def test_detector_is_llm_free_and_fast():
    """The stream path must be pure arithmetic — no model load, sub-second."""
    import time
    eng = AlertEngine("BF.BLW.FAN01", persist=False)
    t = time.time()
    n = 0
    fired_critical = False
    for ev in eng.stream(row_start=1300, row_end=2000):
        n += 1
        if ev.severity == Severity.CRITICAL:
            fired_critical = True
            break
    assert n > 0
    assert fired_critical
    assert time.time() - t < 5.0                      # deterministic + fast


# ===========================================================================
# FR6 — feedback loop moves the prioritization weight
# ===========================================================================
def test_feedback_confirm_moves_weight_up():
    fs = FeedbackStore(db_path=":memory:")  # isolated in-memory db for the test
    asset, scn = "BF.BLW.FAN01", "SCN-041"
    w0 = fs.priority_weight(asset, scn)
    assert w0 == pytest.approx(1.0)                   # neutral prior
    r = fs.submit(asset_id=asset, scenario_id=scn, verdict="confirm", outcome="failure")
    assert r.weight_after > r.weight_before           # nudged UP
    assert r.delta > 0
    assert fs.priority_weight(asset, scn) > 1.0


def test_feedback_false_positive_moves_weight_down():
    fs = FeedbackStore(db_path=":memory:")
    asset, scn = "HSM.F3.WR.BRG01", "SCN-037"
    r = fs.submit(asset_id=asset, scenario_id=scn, verdict="false_positive")
    assert r.weight_after < r.weight_before           # de-prioritised
    assert r.delta < 0
    assert fs.priority_weight(asset, scn) < 1.0


def test_feedback_weight_is_clamped_and_persisted():
    fs = FeedbackStore(db_path=":memory:")
    asset, scn = "BF.BLW.FAN01", "SCN-041"
    # hammer confirms — must never exceed the W_MAX clamp
    for _ in range(20):
        fs.submit(asset_id=asset, scenario_id=scn, verdict="false_negative")
    w = fs.priority_weight(asset, scn)
    assert w <= 1.6 + 1e-9                             # W_MAX clamp holds
    # the asset-level weight also generalised from the scenario feedback
    assert fs.priority_weight(asset) > 1.0
    assert len(fs.history(asset)) >= 20               # audit trail recorded


# ===========================================================================
# Reports — grounded Markdown, no LLM (template floor)
# ===========================================================================
def test_incident_report_is_grounded_markdown():
    rep = incident_report("BF.BLW.FAN01", "SCN-041")
    assert isinstance(rep, Report)
    assert rep.kind == "incident"
    md = rep.markdown
    assert "VULCAN Maintenance Report" in md
    assert "Root Cause Analysis" in md
    assert "Spare-Procurement Strategy" in md
    assert "ground_truth_spine.json" in md            # cites the dataset (FR4)
    assert rep.data["asset_id"] == "BF.BLW.FAN01"


def test_alert_report_from_episode():
    res = replay_episode("BF.BLW.FAN01", handoff=False, persist=False)
    rep = alert_report(res)
    assert rep.kind == "alert"
    md = rep.markdown
    assert "Real-Time Alert Report" in md
    assert "CRITICAL" in md
    assert "JSR.BF.BLW.FAN01.PRES.OSC" in md          # the real surge sensor
    assert "Escalation timeline" in md


def test_decision_summary_card():
    rep = decision_summary("BF.BLW.FAN01", "SCN-041")
    assert rep.kind == "decision"
    md = rep.markdown
    assert "Decision Card" in md
    assert "RISK" in md
    assert rep.data["asset_id"] == "BF.BLW.FAN01"
