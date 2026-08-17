#!/usr/bin/env python3
"""Reshape the wide 73-col historian (88% null) into:
  1. sensor_timeseries_long.csv  -- tidy/melted, NO nulls
  2. by_equipment/<class>.csv     -- one DENSE wide table per equipment_class

The wide file is null-heavy only because each asset fills just its own ~5 sensors.
That's a format artifact. Melt -> drop NaN gives a tidy, dense table; pivoting per
equipment_class gives near-zero-null model-ready training tables. No data is fabricated.
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

BASE = Path("/home/ujjwal/Documents/J.A.R.V.I.S./data/hackathons/tata-steel-2026/round_2/dataforge/datasets/steel-maintenance-flagship")
RAW = BASE / "condition_monitoring" / "raw_sensor_timeseries.csv"
SPINE = BASE / "SPEC" / "ground_truth_spine.json"
OUT_DIR = BASE / "condition_monitoring"
BY_EQ = OUT_DIR / "by_equipment"
BY_EQ.mkdir(parents=True, exist_ok=True)

META_COLS = ["timestamp", "asset_id", "equipment_class", "fault_label", "scenario_id", "RUL_hours"]

# ---- 1. Build sensor metadata from spine ----------------------------------
spine = json.loads(SPINE.read_text())
tag_unit = {}            # sensor tag -> unit
class_sensors = {}       # equipment_class -> ordered list of sensor tags
for asset in spine["asset_registry"]:
    cls = asset["equipment_class"]
    class_sensors.setdefault(cls, [])
    for s in asset["sensors"]:
        tag = s["tag"]
        tag_unit[tag] = s.get("unit", "")
        if tag not in class_sensors[cls]:
            class_sensors[cls].append(tag)

# ---- 2. Load raw wide --------------------------------------------------
df = pd.read_csv(RAW)
sensor_cols = [c for c in df.columns if c not in META_COLS]
print(f"raw: {df.shape[0]:,} rows x {df.shape[1]} cols  (sensor cols={len(sensor_cols)})")

# severity derived from fault_label (0 normal, 1 degraded/warning, 2 alarm/failure)
sev_map = {0: "normal", 1: "warning", 2: "alarm"}
df["severity"] = df["fault_label"].map(sev_map)

# ---- 3. LONG / tidy melt -----------------------------------------------
long = df.melt(
    id_vars=["timestamp", "asset_id", "equipment_class", "fault_label", "RUL_hours", "severity"],
    value_vars=sensor_cols,
    var_name="sensor",
    value_name="value",
)
long = long.dropna(subset=["value"]).copy()          # drop the structural nulls
long["unit"] = long["sensor"].map(tag_unit)
long = long.rename(columns={"RUL_hours": "rul_cycles"})
long = long[["timestamp", "asset_id", "equipment_class", "sensor", "value",
             "unit", "fault_label", "rul_cycles", "severity"]]
long = long.sort_values(["asset_id", "timestamp", "sensor"]).reset_index(drop=True)

long_path = OUT_DIR / "sensor_timeseries_long.csv"
long.to_csv(long_path, index=False)
print(f"LONG: {long_path.name}  {len(long):,} rows  null%={long.isna().mean().mean()*100:.3f}")

# ---- 4. DENSE wide per equipment_class ---------------------------------
# A few "classes" host >1 asset whose instrument set differs (different physical
# sensors per asset). One class-wide wide table for those would carry structural
# nulls (each asset only fills its own tags). The honest fix: split those into
# per-ASSET dense tables (each asset is internally 0%-null). Single-asset classes
# stay as one class file.
manifest_rows = []


def _emit(name, frame, tags):
    # Model-ready CLASSIFICATION table: dense sensor block + equipment_class context.
    # rul_cycles is deliberately EXCLUDED here -- it is the RUL-regression target and
    # is legitimately sparse (only on run-to-failure trajectories); carrying it would
    # inject ~82% structural null into an otherwise 0%-null classification table.
    # RUL is preserved in sensor_timeseries_long.csv and rul_trajectories_long.csv.
    out = frame[
        ["timestamp", "asset_id", "equipment_class"] + tags + ["fault_label"]
    ].copy()
    out = out.sort_values(["asset_id", "timestamp"]).reset_index(drop=True)
    null_pct = out[tags].isna().mean().mean() * 100
    fname = name + ".csv"
    out.to_csv(BY_EQ / fname, index=False)
    pos = int((out["fault_label"] > 0).sum())
    manifest_rows.append((fname, len(out), len(tags), round(null_pct, 3),
                          pos, round(pos / len(out) * 100, 2)))
    print(f"  {fname:46s} {len(out):>6,} rows  {len(tags)} sensors  "
          f"sensor-null%={null_pct:6.3f}  pos={pos}")


for cls, df_cls in df.groupby("equipment_class"):
    assets = sorted(df_cls["asset_id"].unique())
    if len(assets) == 1:
        tags = [t for t in class_sensors.get(cls, []) if t in df_cls.columns
                and df_cls[t].notna().any()]
        _emit(cls, df_cls, tags)
    else:
        # multi-asset class -> per-asset dense table (different instrumentation)
        for a in assets:
            sub = df_cls[df_cls["asset_id"] == a]
            tags = [t for t in class_sensors.get(cls, []) if t in sub.columns
                    and sub[t].notna().any()]
            _emit(f"{cls}__{a.replace('.', '_')}", sub, tags)

# sort manifest by row count desc
manifest_rows.sort(key=lambda r: -r[1])
print("\nLargest dense file:", manifest_rows[0][0])

# ---- 4b. RUL trajectories (tidy) for the regression task -----------------
# Only the rows that actually carry a RUL value (the run-to-failure windows).
rul = long[long["rul_cycles"].notna()][
    ["timestamp", "asset_id", "equipment_class", "sensor", "value",
     "unit", "fault_label", "rul_cycles", "severity"]
].copy()
rul_path = OUT_DIR / "rul_trajectories_long.csv"
rul.to_csv(rul_path, index=False)
print(f"RUL: {rul_path.name}  {len(rul):,} rows  (run-to-failure windows only, 0% null)")

# write a small json summary the audit step can read
summary = {
    "long_file": long_path.name,
    "long_rows": int(len(long)),
    "rul_trajectories_file": "rul_trajectories_long.csv",
    "rul_rows": int(len(rul)),
    "by_equipment": [
        {"file": f, "rows": r, "sensors": s, "sensor_null_pct": n,
         "positive_rows": p, "positive_pct": pp}
        for (f, r, s, n, p, pp) in manifest_rows
    ],
}
(OUT_DIR / "_reshape_summary.json").write_text(json.dumps(summary, indent=2))
print("\nwrote _reshape_summary.json")
