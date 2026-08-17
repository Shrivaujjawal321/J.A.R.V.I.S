"""
wizard.data.ai4i_loader
=======================
Download + parse AI4I 2020 Predictive Maintenance Dataset (UCI, CC BY 4.0).

Key behaviours:
  1. Kelvin → Celsius conversion for air_temp and process_temp columns.
     Failure to do this leaves values like 298.1 K in SensorSummary — plausible
     but wrong units that break threshold comparisons (report 14, open risk §5).
  2. AI4I fault modes (TWF, HDF, PWF, OSF, RNF) mapped to steel-plant
     fault codes and descriptions.
  3. Class imbalance handled: base failure rate is ~3.4%. Callers may use
     class_weight='balanced' or SMOTE — the loader returns imbalance_ratio.
  4. Download from UCI ML Repository (CC BY 4.0). Cached in data/raw/ai4i/.

AI4I → Steel fault mapping (research report 13, §2b):
  HDF  (heat dissipation failure)  → furnace-cooling-fault  (HCF)
  PWF  (power failure)             → drive-motor-overload   (DMO)
  OSF  (overstrain failure)        → roll-force-exceedance  (RFE)
  TWF  (tool wear failure)         → work-roll-degradation  (WRD)
  RNF  (random failure)            → unclassified-anomaly   (UNA)

Usage::

    from wizard.data.ai4i_loader import load_ai4i, AI4I_FAULT_MAP

    df = load_ai4i()
    # df columns: uid, product_type, air_temp_c, process_temp_c,
    #             rotational_speed_rpm, torque_nm, tool_wear_min,
    #             machine_failure, TWF, HDF, PWF, OSF, RNF,
    #             active_fault_mode, steel_fault_code, steel_fault_description
"""

from __future__ import annotations

import io
import logging
import zipfile
from pathlib import Path
from typing import Dict, List, Optional
from urllib.request import urlopen, Request
from urllib.error import URLError

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Download URL — UCI ML Repository (CC BY 4.0)
# ---------------------------------------------------------------------------
_UCI_URL = (
    "https://archive.ics.uci.edu/static/public/601/"
    "ai4i+2020+predictive+maintenance+dataset.zip"
)
_EXPECTED_FILENAME = "ai4i2020.csv"

# ---------------------------------------------------------------------------
# Fault taxonomy mapping
# ---------------------------------------------------------------------------
AI4I_FAULT_MAP: Dict[str, Dict[str, str]] = {
    "TWF": {
        "steel_code":        "WRD",
        "steel_name":        "work_roll_degradation",
        "steel_description": "Work roll degradation — tool wear exceeds allowable threshold",
        "iso14224_class":    "mechanical.wear.abrasive",
        "severity_default":  "medium",
    },
    "HDF": {
        "steel_code":        "HCF",
        "steel_name":        "furnace_cooling_fault",
        "steel_description": "Heat dissipation failure — cooling system insufficient for process load",
        "iso14224_class":    "thermal.cooling.inadequate",
        "severity_default":  "high",
    },
    "PWF": {
        "steel_code":        "DMO",
        "steel_name":        "drive_motor_overload",
        "steel_description": "Power failure — drive motor electrical overload detected",
        "iso14224_class":    "electrical.overload.motor",
        "severity_default":  "critical",
    },
    "OSF": {
        "steel_code":        "RFE",
        "steel_name":        "roll_force_exceedance",
        "steel_description": "Overstrain failure — rolling force exceeds equipment design limit",
        "iso14224_class":    "mechanical.overload.structural",
        "severity_default":  "high",
    },
    "RNF": {
        "steel_code":        "UNA",
        "steel_name":        "unclassified_anomaly",
        "steel_description": "Unclassified random failure — requires further investigation",
        "iso14224_class":    "unknown.random",
        "severity_default":  "medium",
    },
}

# Convenience dict: ai4i column name → steel fault code
AI4I_STEEL_FAULT_CODES: Dict[str, str] = {
    mode: info["steel_code"] for mode, info in AI4I_FAULT_MAP.items()
}

# Raw column name remapping (after Kelvin conversion)
_COL_RENAME = {
    "UDI":                    "uid",
    "Product ID":             "product_id",
    "Type":                   "product_type",
    "Air temperature [K]":    "air_temp_k",    # converted below
    "Process temperature [K]":"process_temp_k", # converted below
    "Rotational speed [rpm]": "rotational_speed_rpm",
    "Torque [Nm]":            "torque_nm",
    "Tool wear [min]":        "tool_wear_min",
    "Machine failure":        "machine_failure",
    "TWF":                    "TWF",
    "HDF":                    "HDF",
    "PWF":                    "PWF",
    "OSF":                    "OSF",
    "RNF":                    "RNF",
}


# ---------------------------------------------------------------------------
# Public loader
# ---------------------------------------------------------------------------

def load_ai4i(
    raw_dir: Optional[Path] = None,
    force_download: bool = False,
) -> pd.DataFrame:
    """
    Load AI4I 2020 dataset from cache or UCI repository.

    Applies:
      - Kelvin → Celsius: air_temp_c = air_temp_k - 273.15
      - Fault mode enrichment: active_fault_mode, steel_fault_code,
        steel_fault_description columns added
      - imbalance_ratio stored in df.attrs

    Returns
    -------
    pd.DataFrame with columns:
        uid, product_id, product_type,
        air_temp_c, process_temp_c,
        rotational_speed_rpm, torque_nm, tool_wear_min,
        machine_failure, TWF, HDF, PWF, OSF, RNF,
        active_fault_mode, steel_fault_code, steel_fault_description,
        delta_temp_c  (process - air, a useful derived feature)
    """
    raw_dir = _resolve_raw_dir(raw_dir)
    csv_path = raw_dir / _EXPECTED_FILENAME
    _ensure_file(csv_path, force_download)

    df = pd.read_csv(csv_path)

    # Rename columns
    df = df.rename(columns=_COL_RENAME)

    # Kelvin → Celsius (critical: report 14 open risk §5)
    if "air_temp_k" in df.columns:
        df["air_temp_c"] = df["air_temp_k"] - 273.15
        df.drop(columns=["air_temp_k"], inplace=True)
    if "process_temp_k" in df.columns:
        df["process_temp_c"] = df["process_temp_k"] - 273.15
        df.drop(columns=["process_temp_k"], inplace=True)

    # Derived feature: temperature delta (process - ambient)
    if "air_temp_c" in df.columns and "process_temp_c" in df.columns:
        df["delta_temp_c"] = df["process_temp_c"] - df["air_temp_c"]

    # Fault mode enrichment
    df = _enrich_fault_modes(df)

    # Log class balance (report 13 anti-pattern #4: naive classifier reaches 96.6% accuracy)
    n_total = len(df)
    n_failure = int(df["machine_failure"].sum())
    imbalance_ratio = n_failure / n_total if n_total > 0 else 0.0
    df.attrs["imbalance_ratio"] = imbalance_ratio
    df.attrs["n_total"] = n_total
    df.attrs["n_failure"] = n_failure

    logger.info(
        "AI4I loaded: %d rows, %d failures (%.1f%%) — use class_weight='balanced' or SMOTE",
        n_total, n_failure, imbalance_ratio * 100,
    )
    return df


def _resolve_raw_dir(raw_dir: Optional[Path]) -> Path:
    if raw_dir is not None:
        return Path(raw_dir)
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "pyproject.toml").exists():
            return parent / "data" / "raw" / "ai4i"
    return Path.cwd() / "data" / "raw" / "ai4i"


def _ensure_file(csv_path: Path, force: bool) -> None:
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    if csv_path.exists() and not force:
        logger.debug("AI4I cache hit: %s", csv_path)
        return

    logger.info("Downloading AI4I 2020 from UCI ML Repository ...")
    try:
        req = Request(_UCI_URL, headers={"User-Agent": "maintenance-wizard/1.0"})
        with urlopen(req, timeout=60) as resp:
            data = resp.read()
    except URLError as exc:
        raise ConnectionError(
            f"Cannot download AI4I 2020 from UCI: {exc}. "
            "Download ai4i2020.csv manually from "
            "https://archive.ics.uci.edu/dataset/601 and place it in "
            f"{csv_path.parent}/"
        ) from exc

    # UCI returns a zip
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as zf:
            for name in zf.namelist():
                if name.lower().endswith(".csv"):
                    csv_path.write_bytes(zf.read(name))
                    logger.info("Extracted AI4I CSV: %s", csv_path)
                    return
        raise FileNotFoundError("No CSV found inside UCI zip archive.")
    except zipfile.BadZipFile:
        # Sometimes UCI returns the CSV directly (not zipped)
        csv_path.write_bytes(data)
        logger.info("Saved AI4I CSV (direct): %s", csv_path)


def _enrich_fault_modes(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add columns:
      active_fault_mode       -> first active fault mode column name (or 'none')
      steel_fault_code        -> mapped steel fault code (or 'OK')
      steel_fault_description -> human-readable steel fault description
    """
    fault_cols = [c for c in ("TWF", "HDF", "PWF", "OSF", "RNF") if c in df.columns]

    def _first_fault(row):
        for c in fault_cols:
            if row.get(c, 0) == 1:
                return c
        return "none"

    df["active_fault_mode"] = df.apply(_first_fault, axis=1)
    df["steel_fault_code"] = df["active_fault_mode"].map(
        lambda m: AI4I_FAULT_MAP[m]["steel_code"] if m in AI4I_FAULT_MAP else "OK"
    )
    df["steel_fault_description"] = df["active_fault_mode"].map(
        lambda m: AI4I_FAULT_MAP[m]["steel_description"] if m in AI4I_FAULT_MAP else "No fault"
    )
    return df


# ---------------------------------------------------------------------------
# Feature engineering helpers (called by ML pipeline)
# ---------------------------------------------------------------------------

FEATURE_COLS: List[str] = [
    "air_temp_c",
    "process_temp_c",
    "delta_temp_c",
    "rotational_speed_rpm",
    "torque_nm",
    "tool_wear_min",
]

def get_feature_matrix(df: pd.DataFrame) -> np.ndarray:
    """Return (N, 6) float32 feature array for LightGBM training."""
    cols = [c for c in FEATURE_COLS if c in df.columns]
    return df[cols].fillna(0.0).to_numpy(dtype=np.float32)


def get_fault_labels(df: pd.DataFrame) -> np.ndarray:
    """Return binary machine_failure label array (int8)."""
    return df["machine_failure"].to_numpy(dtype=np.int8)


def get_multiclass_labels(df: pd.DataFrame) -> np.ndarray:
    """
    Return 6-class fault-type ordinal label for LightGBM
    (0 = none + 5 AI4I fault modes).

    NOTE: This is the AI4I *fault-type* classification — distinct from the
    failure_predictor's RUL-horizon 4-class label. Do not conflate the two.

      0 = no_failure  (none)
      1 = tool_wear   (TWF — work-roll degradation)
      2 = thermal     (HDF — furnace cooling fault)
      3 = power_overload (PWF — drive motor overload)
      4 = overstrain  (OSF — roll force exceedance)
      5 = unclassified (RNF — random / unclassified anomaly)
    """
    label_map = {"none": 0, "TWF": 1, "HDF": 2, "PWF": 3, "OSF": 4, "RNF": 5}
    return df["active_fault_mode"].map(label_map).fillna(0).to_numpy(dtype=np.int8)
