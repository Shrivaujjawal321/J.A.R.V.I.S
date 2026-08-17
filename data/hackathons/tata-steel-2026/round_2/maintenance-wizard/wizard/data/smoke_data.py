"""
wizard.data.smoke_data
======================
Self-contained smoke test for the wizard.data module.

Tests (no pytest dependency — plain Python assertions):
  1. C-MAPSS loader: parse from cached files (skip download if files missing)
  2. AI4I loader: parse from cached files (skip download if files missing)
  3. Dataset framing: column aliasing
  4. DB ingest: write SensorSummary rows into a temp wizard.db, verify count
  5. Asset seeder: idempotent profile creation

Run::

    python wizard/data/smoke_data.py

Expected output (pass):
    [PASS] cmapss_loader ...
    [PASS] ai4i_loader ...
    [PASS] dataset_framing ...
    [PASS] db_ingest ...
    [PASS] asset_seeder ...
    All data smoke tests passed.
"""

from __future__ import annotations

import sys
import tempfile
import logging
from pathlib import Path

logging.basicConfig(level=logging.WARNING)  # suppress info noise during smoke test
logger = logging.getLogger(__name__)


def _check(label: str, condition: bool, msg: str = "") -> None:
    if condition:
        print(f"  [ok] {label}")
    else:
        print(f"  [FAIL] {label}: {msg}")
        sys.exit(1)


def test_cmapss_loader() -> None:
    """Test C-MAPSS loader: either loads from cache or skips gracefully."""
    print("\n[TEST] cmapss_loader")
    from wizard.data.cmapss_loader import load_cmapss, CmapssDataset, RUL_CAP, CMAPSS_STEEL_MAP

    _check("RUL_CAP is 125", RUL_CAP == 125)
    _check("CMAPSS_STEEL_MAP has 'engine_id'", "engine_id" in CMAPSS_STEEL_MAP)
    _check("CMAPSS_STEEL_MAP maps to 'equipment_id'",
           CMAPSS_STEEL_MAP["engine_id"] == "equipment_id")

    # Try to load; skip download check if PHM unreachable
    raw_dir = Path("data/raw/cmapss")
    fd001_train = raw_dir / "train_FD001.txt"

    if fd001_train.exists():
        ds = load_cmapss(subsets=["FD001"])
        _check("CmapssDataset returned", isinstance(ds, CmapssDataset))
        _check("FD001 in train", "FD001" in ds.train)
        train_df = ds.train["FD001"]
        _check("train_FD001 has >1000 rows", len(train_df) > 1000)
        _check("'rul' column present", "rul" in train_df.columns)
        _check("'rul_capped' <= RUL_CAP", train_df["rul_capped"].max() <= RUL_CAP)
        _check("'anomaly_window' is binary", set(train_df["anomaly_window"].unique()).issubset({0, 1}))
        _check("'health_score' in [0,1]",
               train_df["health_score"].between(0.0, 1.0).all())
        _check("feature_cols non-empty", len(ds.feature_cols) > 0)
    else:
        print("  [SKIP] train_FD001.txt not in cache — download skipped in smoke test")

    print("[PASS] cmapss_loader")


def test_ai4i_loader() -> None:
    """Test AI4I loader: either loads from cache or skips gracefully."""
    print("\n[TEST] ai4i_loader")
    from wizard.data.ai4i_loader import (
        load_ai4i, AI4I_FAULT_MAP, AI4I_STEEL_FAULT_CODES,
        FEATURE_COLS, get_feature_matrix, get_fault_labels,
    )
    import numpy as np

    _check("AI4I_FAULT_MAP has 5 entries", len(AI4I_FAULT_MAP) == 5)
    _check("HDF maps to HCF", AI4I_FAULT_MAP["HDF"]["steel_code"] == "HCF")
    _check("PWF maps to DMO", AI4I_FAULT_MAP["PWF"]["steel_code"] == "DMO")
    _check("OSF maps to RFE", AI4I_FAULT_MAP["OSF"]["steel_code"] == "RFE")
    _check("TWF maps to WRD", AI4I_FAULT_MAP["TWF"]["steel_code"] == "WRD")
    _check("AI4I_STEEL_FAULT_CODES dict", len(AI4I_STEEL_FAULT_CODES) == 5)

    raw_dir = Path("data/raw/ai4i")
    csv_path = raw_dir / "ai4i2020.csv"

    if csv_path.exists():
        df = load_ai4i()
        _check("10000 rows", len(df) == 10000)
        _check("air_temp_c in Celsius (not Kelvin)",
               df["air_temp_c"].max() < 100.0,
               f"max={df['air_temp_c'].max():.1f} (should be <100 C, not Kelvin)")
        _check("process_temp_c in Celsius",
               df["process_temp_c"].max() < 100.0)
        _check("delta_temp_c column present", "delta_temp_c" in df.columns)
        _check("active_fault_mode column present", "active_fault_mode" in df.columns)
        _check("steel_fault_code column present", "steel_fault_code" in df.columns)
        _check("imbalance_ratio < 0.10",
               df.attrs.get("imbalance_ratio", 1.0) < 0.10,
               f"imbalance={df.attrs.get('imbalance_ratio', 'N/A')}")
        X = get_feature_matrix(df)
        _check("feature_matrix shape (10000, 6)", X.shape == (10000, 6),
               f"got {X.shape}")
        y = get_fault_labels(df)
        _check("fault_labels length 10000", len(y) == 10000)
    else:
        print("  [SKIP] ai4i2020.csv not in cache — download skipped in smoke test")

    print("[PASS] ai4i_loader")


def test_dataset_framing() -> None:
    """Test dataset framing with synthetic mini-DataFrame."""
    print("\n[TEST] dataset_framing")
    import pandas as pd
    import numpy as np
    from wizard.data.dataset_framing import (
        get_framed_df, frame_ai4i, STEEL_ASSET_LABELS, make_cmapss_sensor_readings,
    )

    # Minimal synthetic C-MAPSS-like DataFrame
    n = 20
    df = pd.DataFrame({
        "engine_id":    [1] * 10 + [2] * 10,
        "cycle":        list(range(1, 11)) * 2,
        "op_setting_1": np.random.rand(n),
        "op_setting_2": np.random.rand(n),
        "sensor_2":     np.random.uniform(640, 650, n),
        "sensor_7":     np.random.uniform(550, 560, n),
        "sensor_11":    np.random.uniform(47, 49, n),
        "sensor_21":    np.random.uniform(388, 393, n),
        "rul":          list(range(100, 90, -1)) * 2,
        "rul_capped":   [min(r, 125) for r in list(range(100, 90, -1)) * 2],
        "anomaly_window": [0] * n,
        "health_score": [0.2] * n,
    })

    framed = get_framed_df(df)
    _check("equipment_id column created", "equipment_id" in framed.columns)
    _check("operating_hours column created", "operating_hours" in framed.columns)
    _check("inlet_temperature_c added", "inlet_temperature_c" in framed.columns)
    _check("vibration_rms added", "vibration_rms" in framed.columns)

    framed_single = get_framed_df(df, asset_label="EAF-04")
    _check("single asset label applied",
           (framed_single["equipment_id"] == "EAF-04").all())

    # Test make_cmapss_sensor_readings
    row = df.iloc[0]
    readings = make_cmapss_sensor_readings(row)
    _check("readings is dict", isinstance(readings, dict))
    _check("readings has temperature_c or vibration_mm_s",
           "temperature_c" in readings or "vibration_mm_s" in readings)

    # Test frame_ai4i with synthetic data
    ai4i_mini = pd.DataFrame({
        "uid":             [1, 2, 3],
        "product_id":      ["L-1", "M-2", "H-3"],
        "product_type":    ["L", "M", "H"],
        "air_temp_c":      [25.0, 26.0, 27.0],
        "process_temp_c":  [30.0, 31.0, 32.0],
        "rotational_speed_rpm": [1500, 1400, 1600],
        "torque_nm":       [40.0, 45.0, 35.0],
        "tool_wear_min":   [10, 20, 5],
        "machine_failure": [0, 1, 0],
        "active_fault_mode": ["none", "HDF", "none"],
        "delta_temp_c":    [5.0, 5.0, 5.0],
    })
    framed_ai4i = frame_ai4i(ai4i_mini)
    _check("equipment_id added to AI4I", "equipment_id" in framed_ai4i.columns)
    _check("plant_area added to AI4I", "plant_area" in framed_ai4i.columns)
    _check("sensor_readings added to AI4I", "sensor_readings" in framed_ai4i.columns)
    _check("sensor_readings is dict", isinstance(framed_ai4i["sensor_readings"].iloc[0], dict))

    print("[PASS] dataset_framing")


def test_db_ingest() -> None:
    """Test DB ingest into a temporary SQLite database."""
    print("\n[TEST] db_ingest")
    import pandas as pd
    import numpy as np
    from wizard.data.db_ingest import ingest_sensor_rows, seed_demo_assets, ingest_ai4i_rows
    from wizard.core.db import init_db, session_scope
    from wizard.core.schemas import SensorSummary, AssetProfile
    from sqlmodel import select

    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test_wizard.db"
        init_db(db_path)

        # --- Seed assets ---
        seed_demo_assets(db_path)
        with session_scope(db_path) as session:
            assets = session.exec(select(AssetProfile)).all()
        _check("seed_demo_assets created 6 assets", len(assets) == 6,
               f"got {len(assets)}")

        # --- Ingest C-MAPSS-like rows ---
        n = 50
        mini_df = pd.DataFrame({
            "engine_id":     [1] * n,
            "cycle":         list(range(1, n + 1)),
            "op_setting_1":  np.random.rand(n),
            "sensor_2":      np.random.uniform(640, 650, n),
            "sensor_7":      np.random.uniform(550, 560, n),
            "sensor_11":     np.random.uniform(47, 49, n),
            "sensor_21":     np.random.uniform(388, 393, n),
            "rul":           list(range(n, 0, -1)),
            "rul_capped":    [min(r, 125) for r in range(n, 0, -1)],
            "anomaly_window":[0 if r > 30 else 1 for r in range(n, 0, -1)],
            "health_score":  [1 - min(r, 125) / 125 for r in range(n, 0, -1)],
        })

        # Use session_scope() so the INSERT is committed (finding #4 fix).
        with session_scope(db_path) as session:
            n_written = ingest_sensor_rows(
                mini_df, asset_id="EAF-04", session=session
            )
        _check(f"ingest_sensor_rows wrote {n} rows", n_written == n,
               f"got {n_written}")

        with session_scope(db_path) as session:
            all_summaries = session.exec(
                select(SensorSummary).where(SensorSummary.asset_id == "EAF-04")
            ).all()
        _check("SensorSummary rows in DB", len(all_summaries) == n,
               f"got {len(all_summaries)}")

        # Check operating_condition derived correctly
        last_row = sorted(all_summaries, key=lambda s: s.operating_hours or 0)[-1]
        _check("last row has operating_hours", last_row.operating_hours is not None)
        _check("sensor_readings is dict", isinstance(last_row.sensor_readings, dict))

        # --- AI4I ingest ---
        ai4i_mini = pd.DataFrame({
            "uid":             list(range(5)),
            "product_id":      ["L-1", "L-2", "M-1", "H-1", "H-2"],
            "product_type":    ["L", "L", "M", "H", "H"],
            "air_temp_c":      [25.0, 25.5, 26.0, 27.0, 27.5],
            "process_temp_c":  [30.0, 30.5, 31.0, 32.0, 32.5],
            "rotational_speed_rpm": [1500, 1510, 1400, 1600, 1590],
            "torque_nm":       [40.0, 41.0, 45.0, 35.0, 36.0],
            "tool_wear_min":   [10, 12, 20, 5, 7],
            "machine_failure": [0, 0, 1, 0, 0],
            "active_fault_mode": ["none", "none", "HDF", "none", "none"],
            "steel_fault_code":  ["OK", "OK", "HCF", "OK", "OK"],
            "steel_fault_description": ["No fault"] * 5,
            "delta_temp_c":    [5.0] * 5,
        })
        with session_scope(db_path) as session:
            n_ai4i = ingest_ai4i_rows(ai4i_mini, session=session)
        _check("ingest_ai4i_rows wrote 5 rows", n_ai4i == 5, f"got {n_ai4i}")

        # Idempotency: seed_demo_assets again should not double-create
        seed_demo_assets(db_path)
        with session_scope(db_path) as session:
            assets2 = session.exec(select(AssetProfile)).all()
        _check("seed_demo_assets is idempotent", len(assets2) == 6,
               f"got {len(assets2)} (expected 6, not doubled)")

    print("[PASS] db_ingest")


def test_asset_seeder() -> None:
    """Verify all 6 demo assets are seeded with correct fields."""
    print("\n[TEST] asset_seeder")
    import tempfile
    from wizard.data.db_ingest import seed_demo_assets
    from wizard.core.db import session_scope
    from wizard.core.schemas import AssetProfile
    from sqlmodel import select

    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test2.db"
        seed_demo_assets(db_path)
        with session_scope(db_path) as session:
            assets = session.exec(select(AssetProfile)).all()

        asset_map = {a.asset_id: a for a in assets}
        _check("EAF-04 exists", "EAF-04" in asset_map)
        _check("EAF-04 is critical", asset_map["EAF-04"].criticality_tier == "critical")
        _check("PUMP-CP-01 is high", asset_map["PUMP-CP-01"].criticality_tier == "high")
        _check("HPU-01 is medium", asset_map["HPU-01"].criticality_tier == "medium")
        _check("BF-FAN-01 has design_rpm", asset_map["BF-FAN-01"].design_rpm == 1500.0)
        _check("all 6 assets present", len(asset_map) == 6, f"got {len(asset_map)}")

    print("[PASS] asset_seeder")


def main() -> None:
    print("=" * 60)
    print("wizard.data smoke test")
    print("=" * 60)

    test_cmapss_loader()
    test_ai4i_loader()
    test_dataset_framing()
    test_db_ingest()
    test_asset_seeder()

    print("\n" + "=" * 60)
    print("All data smoke tests passed.")
    print("=" * 60)


if __name__ == "__main__":
    main()
