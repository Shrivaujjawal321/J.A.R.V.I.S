"""
fix_incident_records.py
=======================
Applies the three audit corrections to incident_records.csv so it stays
consistent with SPEC/ground_truth_spine.json and the sibling modality files
(fault_error_messages.csv, equipment_delay_logs.csv, failure_analysis_reports/).

Corrections
-----------
1+2 (FK integrity). `scenario_id` is treated as a STRICT foreign key to the
    exact (asset_id, failure_mode) pair in the failure_scenario_catalog.
    The catalog holds exactly ONE FAILURE scenario per asset (SCN-037..048,
    the asset's PRIMARY failure mode). For any incident row whose
    (asset_id, failure_mode) does NOT match a cataloged FAILURE scenario, the
    scenario_id is BLANKED -- mirroring failure_analysis_reports/index.jsonl,
    which correctly leaves scenario_id absent for secondary / non-cataloged
    modes (RCA-013..025). Never point scenario_id at a scenario whose asset_id
    or failure_mode differs from the row's own.

3 (Timeline alignment). The original incidents spanned 2024-01-08..2025-05-28
    (506 days), while fault_error_messages.csv and equipment_delay_logs.csv
    both span the 2025 calendar year (2025-01-01..2025-12-31) and the RCA
    reports are dated 2025-07-19..2026-05-10. The incidents are re-based into
    the 2025 window (2025-01-02..2025-12-30) preserving chronological order
    and relative spacing, so each incident co-occurs with its precursor
    fault/delay rows and precedes / aligns with the RCA report dates.
    Durations (downtime_hours) are preserved exactly; end_ts is recomputed
    from the new start_ts + the row's own downtime_hours.

Re-runnable: reads the existing CSV, rewrites it in place. Idempotent on the
FK fix; the timeline rebase is anchored to the WINDOW (not to prior output) so
re-running maps the same fractional positions to the same dates.
"""

import csv
import json
import os
from datetime import datetime, timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
SPINE = os.path.join(HERE, "..", "SPEC", "ground_truth_spine.json")
CSV_PATH = os.path.join(HERE, "incident_records.csv")

# Shared timeline window (matches fault_error_messages.csv / equipment_delay_logs.csv)
WIN_START = datetime(2025, 1, 2, 0, 0, 0)
WIN_END = datetime(2025, 12, 30, 23, 59, 59)

FIELDNAMES = [
    "incident_id", "asset_id", "start_ts", "end_ts", "downtime_hours",
    "failure_mode", "severity", "root_cause_short", "resolution_short",
    "cost_estimate", "scenario_id",
]


def load_valid_fk():
    """(asset_id, failure_mode) -> scenario_id for FAILURE scenarios only."""
    spine = json.load(open(SPINE))
    return {
        (s["asset_id"], s["failure_mode"]): s["scenario_id"]
        for s in spine["failure_scenario_catalog"]
        if s.get("label") != "NORMAL"
    }


def main():
    valid_fk = load_valid_fk()
    rows = list(csv.DictReader(open(CSV_PATH)))

    # --- Correction 3: rebase timeline into the shared 2025 window ---
    # Preserve chronological order + relative spacing of original start_ts.
    starts = [datetime.strptime(r["start_ts"], "%Y-%m-%d %H:%M:%S") for r in rows]
    o_min, o_max = min(starts), max(starts)
    o_span = (o_max - o_min).total_seconds()
    w_span = (WIN_END - WIN_START).total_seconds()

    fk_fixed = 0
    fk_blanked = 0
    fk_kept = 0

    for r, st in zip(rows, starts):
        frac = (st - o_min).total_seconds() / o_span if o_span else 0.0
        new_start = WIN_START + timedelta(seconds=frac * w_span)
        # Recompute end from the row's own downtime (durations preserved exactly).
        dt_hours = float(r["downtime_hours"])
        new_end = new_start + timedelta(hours=dt_hours)
        r["start_ts"] = new_start.strftime("%Y-%m-%d %H:%M:%S")
        r["end_ts"] = new_end.strftime("%Y-%m-%d %H:%M:%S")

        # --- Corrections 1+2: strict FK on exact (asset_id, failure_mode) ---
        want = valid_fk.get((r["asset_id"], r["failure_mode"]), "")
        old = r["scenario_id"].strip()
        if want:
            if old != want:
                fk_fixed += 1
            else:
                fk_kept += 1
            r["scenario_id"] = want
        else:
            if old:
                fk_blanked += 1
            r["scenario_id"] = ""

    with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDNAMES)
        w.writeheader()
        w.writerows(rows)

    # Verification
    new_starts = sorted(r["start_ts"] for r in rows)
    print(f"rows               : {len(rows)}")
    print(f"FK kept (correct)  : {fk_kept}")
    print(f"FK corrected->blank: {fk_blanked}")
    print(f"FK changed-value   : {fk_fixed}")
    print(f"rows with scn_id   : {sum(1 for r in rows if r['scenario_id'])}")
    print(f"rows blank scn_id  : {sum(1 for r in rows if not r['scenario_id'])}")
    print(f"new start_ts range : {new_starts[0]} -> {new_starts[-1]}")

    # Assert no surviving FK violates the (asset,mode) contract
    bad = 0
    for r in rows:
        if r["scenario_id"]:
            if valid_fk.get((r["asset_id"], r["failure_mode"])) != r["scenario_id"]:
                bad += 1
    print(f"residual FK violations: {bad}")
    assert bad == 0, "FK contract still violated"


if __name__ == "__main__":
    main()
