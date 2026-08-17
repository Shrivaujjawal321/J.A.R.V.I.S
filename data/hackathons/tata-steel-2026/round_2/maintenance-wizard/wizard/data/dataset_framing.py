"""
wizard.data.dataset_framing
===========================
Cosmetic column-aliasing for the demo UI — reframes C-MAPSS and AI4I
column names into steel-plant language.

This is PURELY cosmetic: the underlying models train on original C-MAPSS
column names. The framed DataFrame is used only by the Streamlit UI and
the LLM narrative layer so judges see steel-plant terminology.

Column alias map (CMAPSS_STEEL_MAP) is defined in cmapss_loader.py and
re-exported here for convenience.

Steel equipment families used in framing:
  EAF-04            Electric Arc Furnace Fan (scripted demo target)
  BF-FAN-01/02      Blast Furnace Fans
  PUMP-CP-01        Centrifugal Pump (cooling circuit)
  CONV-HSM-01       Hot-Strip-Mill Conveyor
  BEAR-RM-01        Roller/Conveyor Bearing
  HPU-01            Hydraulic Power Unit

Usage::

    from wizard.data.dataset_framing import get_framed_df, frame_ai4i

    framed = get_framed_df(cmapss_train_df, asset_label="EAF-04")
    # framed has columns: equipment_id, operating_hours,
    #   production_speed_pct, load_pct, inlet_temperature_c,
    #   vibration_rms, rul, rul_capped, health_score, ...

    ai4i_framed = frame_ai4i(ai4i_df)
    # adds equipment_id column mapped from product_type (L/M/H)
"""

from __future__ import annotations

import logging
from typing import Dict, List, Optional

import pandas as pd

from wizard.data.cmapss_loader import CMAPSS_STEEL_MAP

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Steel equipment label pool (cycled when multiple engines need labels)
# ---------------------------------------------------------------------------
STEEL_ASSET_LABELS: List[str] = [
    "EAF-04",       # Electric Arc Furnace Fan — the scripted demo asset
    "BF-FAN-01",    # Blast Furnace Fan A
    "BF-FAN-02",    # Blast Furnace Fan B
    "PUMP-CP-01",   # Centrifugal Pump (cooling circuit)
    "CONV-HSM-01",  # Hot-Strip-Mill Conveyor
    "BEAR-RM-01",   # Roller/Conveyor Bearing
    "HPU-01",       # Hydraulic Power Unit
    "BF-FAN-03",
    "PUMP-CP-02",
    "CONV-HSM-02",
]

# AI4I product_type → steel equipment class
AI4I_PRODUCT_MAP: Dict[str, str] = {
    "L": "low_grade_rolling_mill",
    "M": "medium_grade_rolling_mill",
    "H": "high_grade_rolling_mill",
}

# Plant areas mapped from product_type
AI4I_PLANT_AREA: Dict[str, str] = {
    "L": "HSM-Bay-1",
    "M": "HSM-Bay-2",
    "H": "HSM-Bay-3",
}


def get_framed_df(
    df: pd.DataFrame,
    asset_label: Optional[str] = None,
    engine_to_asset: Optional[Dict[int, str]] = None,
) -> pd.DataFrame:
    """
    Rename C-MAPSS columns to steel-plant terminology for the demo UI.

    Parameters
    ----------
    df : C-MAPSS DataFrame (from load_cmapss)
    asset_label : if provided, all engine_ids map to this single label
                  (useful for single-asset demo scenarios, e.g. 'EAF-04')
    engine_to_asset : explicit mapping engine_id -> asset label.
                      If None and asset_label is None, cycles through
                      STEEL_ASSET_LABELS by engine_id mod.

    Returns
    -------
    pd.DataFrame with steel-plant column names added alongside originals
    (original columns are preserved; aliases are added as new columns).
    """
    framed = df.copy()

    # Add steel-framed column aliases (add as new cols, keep originals)
    for src, dst in CMAPSS_STEEL_MAP.items():
        if src in framed.columns and dst not in framed.columns:
            framed[dst] = framed[src]

    # Map engine_id → equipment_id
    if asset_label is not None:
        framed["equipment_id"] = asset_label
    elif engine_to_asset is not None:
        framed["equipment_id"] = framed["engine_id"].map(engine_to_asset)
    else:
        n_labels = len(STEEL_ASSET_LABELS)
        # Map each unique engine_id to a label by index
        unique_engines = sorted(framed["engine_id"].unique())
        eid_map = {
            eid: STEEL_ASSET_LABELS[i % n_labels]
            for i, eid in enumerate(unique_engines)
        }
        framed["equipment_id"] = framed["engine_id"].map(eid_map)

    # operating_hours = cycle (already aliased above if sensor_map has 'cycle')
    if "operating_hours" not in framed.columns and "cycle" in framed.columns:
        framed["operating_hours"] = framed["cycle"]

    logger.debug(
        "Framed DataFrame: %d rows, %d columns", len(framed), len(framed.columns)
    )
    return framed


def frame_ai4i(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add steel-framing columns to AI4I 2020 DataFrame.

    Adds:
      equipment_class   : mapped from product_type (L/M/H)
      plant_area        : HSM-Bay-1/2/3
      equipment_id      : constructed as 'ROLL-{product_type}-{uid:04d}'
      sensor_readings   : dict-of-floats for SensorSummary ingest
    """
    framed = df.copy()

    framed["equipment_class"] = framed["product_type"].map(AI4I_PRODUCT_MAP).fillna(
        "unknown_rolling_mill"
    )
    framed["plant_area"] = framed["product_type"].map(AI4I_PLANT_AREA).fillna("HSM-Bay-1")
    framed["equipment_id"] = (
        "ROLL-" + framed["product_type"].astype(str)
        + "-" + framed["uid"].astype(str).str.zfill(5)
    )

    # Build sensor_readings dict column (for SensorSummary.sensor_readings JSON)
    def _make_readings(row) -> dict:
        readings: dict = {}
        if "air_temp_c" in row.index:
            readings["temperature_c"] = float(row["air_temp_c"])
        if "process_temp_c" in row.index:
            readings["process_temperature_c"] = float(row["process_temp_c"])
        if "rotational_speed_rpm" in row.index:
            readings["rpm"] = float(row["rotational_speed_rpm"])
        if "torque_nm" in row.index:
            readings["torque_nm"] = float(row["torque_nm"])
        if "tool_wear_min" in row.index:
            readings["tool_wear_min"] = float(row["tool_wear_min"])
        if "delta_temp_c" in row.index:
            readings["delta_temp_c"] = float(row["delta_temp_c"])
        return readings

    framed["sensor_readings"] = framed.apply(_make_readings, axis=1)

    return framed


def make_cmapss_sensor_readings(row: "pd.Series") -> dict:
    """
    Convert one C-MAPSS row into a SensorSummary.sensor_readings dict.
    Uses the steel-framing column names where available.
    """
    readings: dict = {}
    sensor_map = {
        "inlet_temperature_c":     "temperature_c",
        "vibration_rms":           "vibration_mm_s",
        "hpc_outlet_pressure_bar": "pressure_bar",
        "torque_nm":               "torque_nm",
        "rotational_speed_rpm":    "rpm",
    }
    for src, dst in sensor_map.items():
        if src in row.index and pd.notna(row[src]):
            readings[dst] = float(row[src])

    # Fallback: use raw sensor cols if framed cols missing
    raw_to_std = {
        "sensor_2":  "temperature_c",
        "sensor_11": "vibration_mm_s",
        "sensor_7":  "pressure_bar",
        "sensor_21": "torque_nm",
    }
    for raw, std in raw_to_std.items():
        if std not in readings and raw in row.index and pd.notna(row[raw]):
            readings[std] = float(row[raw])

    return readings
