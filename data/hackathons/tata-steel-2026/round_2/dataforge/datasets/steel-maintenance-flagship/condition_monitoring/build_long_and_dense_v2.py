#!/usr/bin/env python3
"""Reshape v2 — wide historian -> long + dense + rul, carrying the new v2 columns
(run_id, split, opc_quality) so downstream consumers can do leakage-safe
group-by-asset / leave-one-episode-out CV (fixes CM-04). Adds per-row opc_quality
to the long file (fixes CM-06). No data fabricated; pure reshape.
"""
import json
from pathlib import Path
import pandas as pd

BASE = Path("/home/ujjwal/Documents/J.A.R.V.I.S./data/hackathons/tata-steel-2026/round_2/dataforge/datasets/steel-maintenance-flagship")
RAW = BASE / "condition_monitoring" / "raw_sensor_timeseries.csv"
SPINE = BASE / "SPEC" / "ground_truth_spine.json"
OUT_DIR = BASE / "condition_monitoring"
BY_EQ = OUT_DIR / "by_equipment"
BY_EQ.mkdir(parents=True, exist_ok=True)

META_COLS = ["timestamp", "asset_id", "equipment_class", "fault_label",
             "scenario_id", "run_id", "RUL_hours", "split", "opc_quality"]

spine = json.loads(SPINE.read_text())
tag_unit, class_sensors = {}, {}
for asset in spine["asset_registry"]:
    cls = asset["equipment_class"]
    class_sensors.setdefault(cls, [])
    for s in asset["sensors"]:
        tag_unit[s["tag"]] = s.get("unit", "")
        if s["tag"] not in class_sensors[cls]:
            class_sensors[cls].append(s["tag"])

df = pd.read_csv(RAW)
sensor_cols = [c for c in df.columns if c not in META_COLS]
print(f"raw: {df.shape[0]:,} x {df.shape[1]}  (sensor cols={len(sensor_cols)})")
sev_map = {0: "normal", 1: "warning", 2: "alarm"}
df["severity"] = df["fault_label"].map(sev_map)

# ---- LONG (tidy) -----------------------------------------------------------
long = df.melt(
    id_vars=["timestamp", "asset_id", "equipment_class", "fault_label", "RUL_hours",
             "run_id", "split", "opc_quality", "severity"],
    value_vars=sensor_cols, var_name="sensor", value_name="value")
long = long.dropna(subset=["value"]).copy()
long["unit"] = long["sensor"].map(tag_unit)
long = long.rename(columns={"RUL_hours": "rul_cycles"})
long = long[["timestamp", "asset_id", "equipment_class", "sensor", "value", "unit",
             "fault_label", "rul_cycles", "severity", "run_id", "split", "opc_quality"]]
long = long.sort_values(["asset_id", "timestamp", "sensor"]).reset_index(drop=True)
long.to_csv(OUT_DIR / "sensor_timeseries_long.csv", index=False)
print(f"LONG: {len(long):,} rows  null%={long.isna().mean().mean()*100:.3f}")

# ---- DENSE per equipment_class (classification; rul excluded, split kept) ---
manifest_rows = []
def _emit(name, frame, tags):
    out = frame[["timestamp", "asset_id", "equipment_class"] + tags +
                ["fault_label", "run_id", "split"]].copy()
    out = out.sort_values(["asset_id", "timestamp"]).reset_index(drop=True)
    null_pct = out[tags].isna().mean().mean() * 100
    out.to_csv(BY_EQ / (name + ".csv"), index=False)
    pos = int((out["fault_label"] > 0).sum())
    manifest_rows.append((name + ".csv", len(out), len(tags), round(null_pct, 3),
                          pos, round(pos / len(out) * 100, 2)))
    print(f"  {name+'.csv':46s} {len(out):>6,} rows  {len(tags)} sensors  null%={null_pct:6.3f}  pos={pos}")

for cls, df_cls in df.groupby("equipment_class"):
    assets = sorted(df_cls["asset_id"].unique())
    if len(assets) == 1:
        tags = [t for t in class_sensors.get(cls, []) if t in df_cls.columns and df_cls[t].notna().any()]
        _emit(cls, df_cls, tags)
    else:
        for a in assets:
            sub = df_cls[df_cls["asset_id"] == a]
            tags = [t for t in class_sensors.get(cls, []) if t in sub.columns and sub[t].notna().any()]
            _emit(f"{cls}__{a.replace('.', '_')}", sub, tags)
manifest_rows.sort(key=lambda r: -r[1])

# ---- RUL trajectories (regression; run_id + split kept for LORO-CV) ---------
rul = long[long["rul_cycles"].notna()][
    ["timestamp", "asset_id", "equipment_class", "sensor", "value", "unit",
     "fault_label", "rul_cycles", "severity", "run_id", "split"]].copy()
rul.to_csv(OUT_DIR / "rul_trajectories_long.csv", index=False)
print(f"RUL: {len(rul):,} rows  runs={rul['run_id'].nunique()}")

summary = {
    "long_file": "sensor_timeseries_long.csv", "long_rows": int(len(long)),
    "rul_trajectories_file": "rul_trajectories_long.csv", "rul_rows": int(len(rul)),
    "rul_distinct_runs": int(rul["run_id"].nunique()),
    "by_equipment": [{"file": f, "rows": r, "sensors": s, "sensor_null_pct": n,
                      "positive_rows": p, "positive_pct": pp}
                     for (f, r, s, n, p, pp) in manifest_rows],
}
(OUT_DIR / "_reshape_summary.json").write_text(json.dumps(summary, indent=2))
print("wrote _reshape_summary.json")
