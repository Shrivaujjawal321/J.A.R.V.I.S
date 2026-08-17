"""VULCAN Wave-2 verification — RAG + ML + tools, end to end, on real data.

Run:  PYTHONPATH=. python -m vulcan.verify_wave2     (from the vulcan/ package root)
   or  /path/to/.venv/bin/python vulcan/verify_wave2.py

Prints a single honest report:
  1. RAG: corpus chunk count + a bearing-query retrieval (top sources + scores).
  2. ML : holdout metrics + live fault/anomaly/RUL predictions on real windows.
  3. TOOLS: real dataset values from 3 deterministic tools.

Everything here is keyless / CPU / offline. No LLM is called.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# allow running as a plain script
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def section(title: str) -> None:
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


def verify_rag() -> None:
    section("1. RAG  — local bge-small + ChromaDB + FlashRank")
    from vulcan.rag import collection_count, retrieve, sources

    n = collection_count()
    print(f"corpus chunks ingested: {n}")
    if n == 0:
        print("!! collection empty — run:  python -m vulcan.rag.store")
        return

    query = "bearing outer race BPFO vibration spall what should I do"
    print(f"\nretrieve({query!r}):")
    chunks = retrieve(query, top_k=5)
    for i, c in enumerate(chunks, 1):
        print(f"  [{i}] rerank={c.rerank_score:7.3f} dense={c.dense_score:5.3f} "
              f"{c.doc_type:14s} {c.citation()}")
    print("\n  distinct sources:", [s["source"] for s in sources(chunks)])

    # equipment-class prefilter demo
    chunks2 = retrieve("how to replace this bearing safely",
                       equipment_class="rolling_mill_work_roll_bearing",
                       doc_types=["sop"], top_k=3)
    print("\n  prefiltered (SOP, rolling_mill_work_roll_bearing):")
    for c in chunks2:
        print(f"    {c.citation()}  ({c.doc_type})")


def verify_ml() -> None:
    section("2. ML  — 15 fault + 15 anomaly + 13 RUL models (steel-native dense tables)")
    import pandas as pd

    from vulcan.ml import anomaly_score, estimate_rul, predict_fault
    from vulcan.ml.features import sensor_columns
    from vulcan.config import get_settings

    # live: healthy latest window
    print("predict_fault(BF.BLW.FAN01) [latest, healthy]:")
    r = predict_fault("BF.BLW.FAN01")
    print(f"  -> {r['predicted_class']}  {r['probabilities']}")

    # fire on a REAL failure window
    s = get_settings()
    p = s.condition_dir / "by_equipment" / "bf_sinter_fan_blower__BF_BLW_FAN01.csv"
    df = pd.read_csv(p)
    scols = sensor_columns(df)
    fail = df.index[df.fault_label == 2].tolist()
    if fail:
        i = fail[len(fail) // 2]
        win = df[scols].iloc[max(0, i - 23):i + 1].to_dict("records")
        rf = predict_fault("BF.BLW.FAN01", window=win)
        ra = anomaly_score("BF.BLW.FAN01", window=win)
        print(f"\npredict_fault(BF.BLW.FAN01) [REAL failure window @row {i}]:")
        print(f"  -> {rf['predicted_class']}  {rf['probabilities']}")
        print(f"anomaly_score(...) -> score={ra['anomaly_score']}  is_anomaly={ra['is_anomaly']}")

    print("\nestimate_rul on 3 assets:")
    for aid in ("HSM.F3.WR.BRG01", "BF.BLW.FAN01", "CCM.MOLD.01"):
        rr = estimate_rul(aid)
        print(f"  {aid:18s} rul_cycles={rr.get('rul_cycles')}  ~days={rr.get('rul_days_estimate')}")


def verify_tools() -> None:
    section("3. TOOLS — deterministic dataset reads (no LLM)")
    from vulcan.tools import (get_asset, get_scenario, get_spares_for_scenario)

    a = get_asset("BF.BLW.FAN01")
    print(f"get_asset(BF.BLW.FAN01): class={a['equipment_class']} "
          f"criticality={a['criticality']} sensors={a['sensor_count']} src={a['source']}")

    scn = get_scenario("SCN-041")
    print(f"get_scenario(SCN-041): {scn['label']}/{scn['failure_mode']} "
          f"safety={scn['safety_class']} cost_inr={scn['cost_impact'].get('inr')}")

    sps = get_spares_for_scenario("SCN-041")
    print(f"get_spares_for_scenario(SCN-041): order_required={sps['procurement_action_required']} "
          f"max_lead={sps['max_lead_time_weeks']}wk total_cost_inr={sps['total_parts_cost_inr']}")
    for part in sps["parts"]:
        print(f"   - {part['part_id']:14s} {part['recommendation']}")


def main() -> None:
    verify_rag()
    verify_ml()
    verify_tools()
    print("\n" + "=" * 70)
    print("VULCAN Wave-2 verification complete — all components keyless / CPU / offline.")
    print("=" * 70)


if __name__ == "__main__":
    main()
