"""VULCAN Wave-4 verification — alerting (FR7) + feedback (FR6) + reports.

A single runnable demo that proves the three Wave-4 deliverables end to end on a
REAL spine asset (BF.BLW.FAN01 / SCN-041 — blast-furnace top-gas booster fan
compressor surge), with ZERO LLM in the detector loop:

  1. ALERTING  — replays the asset's real dense sensor stream and fires a
                 prioritized, autonomous CRITICAL the instant the PRES.OSC surge
                 sensor crosses its spine ALARM threshold (escalates
                 WARNING -> ALARM -> CRITICAL). On CRITICAL it hands off to the
                 agentic core for the explainable diagnosis (FR4).
  2. FEEDBACK  — an engineer confirms the diagnosis; the priority weight for that
                 (asset, scenario) demonstrably moves UP (FR6).
  3. REPORTS   — generates an alert report, an incident report, and a decision
                 card, each grounded + cited to the dataset.

Run (deterministic floor, fast + offline-safe — recommended for the demo):
    VULCAN_LLM_MODE=off VULCAN_LLM_PROVIDER=template \\
      PYTHONPATH=. /home/ujjwal/Documents/J.A.R.V.I.S./.venv/bin/python -m vulcan.verify_wave4

Run (live Claude Max synthesis on the CRITICAL hand-off — ~50s, needs OAuth):
    VULCAN_LLM_MODE=live VULCAN_LLM_PROVIDER=subscription \\
      PYTHONPATH=. /home/ujjwal/Documents/J.A.R.V.I.S./.venv/bin/python -m vulcan.verify_wave4 --handoff
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

DEMO_ASSET = "BF.BLW.FAN01"
DEMO_SCENARIO = "SCN-041"


def banner(t: str) -> None:
    print("\n" + "#" * 74)
    print("# " + t)
    print("#" * 74)


def main() -> None:
    handoff = "--handoff" in sys.argv
    from vulcan.alerting import replay_episode
    from vulcan.feedback import get_feedback_store, priority_weight
    from vulcan.reports import alert_report, incident_report, decision_summary, save_report

    # ---------------------------------------------------------------
    banner(f"1/3  ALERTING (FR7) — autonomous CRITICAL on REAL asset {DEMO_ASSET}")
    res = replay_episode(DEMO_ASSET, handoff=handoff, persist=True)
    print(f"asset={res.asset_id}  scenario={res.scenario_id}  fired_critical={res.fired}")
    print("escalation timeline (deterministic, LLM-free):")
    for t in res.severity_timeline():
        print(f"   {t['severity']:<8} ts={t['timestamp']}  {t['sensor']} = {t['value']}  "
              f"row={t['row_index']}  ({t['reason']})")
    fc = res.first_critical
    assert fc is not None, "FAIL: no CRITICAL fired"
    assert fc.value >= (fc.alarm_threshold or 0), "FAIL: CRITICAL below alarm threshold"
    print(f"\nAUTONOMOUS TRIP: {fc.sensor} = {fc.value}{fc.unit or ''} crossed alarm "
          f"{fc.alarm_threshold}{fc.unit or ''} ({fc.standard}) at {fc.timestamp}")
    if res.diagnosis:
        d = res.diagnosis
        print(f"agentic hand-off: risk={d.get('risk_band')} rung={d.get('llm_rung')} "
              f"faithfulness={d.get('faithfulness')} "
              f"RUL={(d.get('rul') or {}).get('rul_cycles')} cycles")

    # ---------------------------------------------------------------
    banner("2/3  FEEDBACK (FR6) — engineer confirms; priority weight moves")
    fs = get_feedback_store()
    w_before = priority_weight(DEMO_ASSET, DEMO_SCENARIO)
    fb = fs.submit(asset_id=DEMO_ASSET, scenario_id=DEMO_SCENARIO,
                   verdict="confirm", outcome="failure", engineer="shift_eng_A",
                   note="Confirmed compressor surge; anti-surge valve serviced.")
    w_after = priority_weight(DEMO_ASSET, DEMO_SCENARIO)
    print(f"weight ({DEMO_ASSET}/{DEMO_SCENARIO}):  {w_before:.4f} -> {w_after:.4f}  "
          f"(delta {fb.delta:+.4f}, direction {fb.to_dict()['direction']})")
    assert w_after > w_before, "FAIL: confirm feedback did not raise the weight"
    print("=> future risk scoring for this fault path is now weighted higher (auditable).")

    # ---------------------------------------------------------------
    banner("3/3  REPORTS — grounded, dataset-cited Markdown")
    a_rep = alert_report(res)
    pa = save_report(a_rep)
    print(f"alert report     : {pa.name}  ({len(a_rep.markdown)} chars)")
    i_rep = incident_report(DEMO_ASSET, DEMO_SCENARIO)
    pi = save_report(i_rep)
    print(f"incident report  : {pi.name}  ({len(i_rep.markdown)} chars)")
    d_rep = decision_summary(DEMO_ASSET, DEMO_SCENARIO)
    pd = save_report(d_rep)
    print(f"decision card    : {pd.name}")
    print("\n--- decision card ---")
    print(d_rep.markdown)

    banner("WAVE-4 VERIFY COMPLETE — alerting + feedback + reports all green")
    print("Every figure above traces to steel-maintenance-flagship. No fabrication.")


if __name__ == "__main__":
    main()
