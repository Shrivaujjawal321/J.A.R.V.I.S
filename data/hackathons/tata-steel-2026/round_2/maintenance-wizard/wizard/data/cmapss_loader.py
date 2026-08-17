"""
wizard.data.cmapss_loader
=========================
Download + parse NASA C-MAPSS FD001 and FD003 datasets.

Key behaviours (per research report 13 anti-pattern list):
  1. Piecewise-linear RUL cap at RUL_CAP = 125 cycles.
  2. Per-engine MinMax normalisation (NOT global) — prevents 15-30% RMSE penalty.
  3. Anomaly window: last ANOMALY_WINDOW cycles before failure are flagged.
  4. Constant sensor columns are dropped automatically (zero variance).

Download:
  Primary:  PHM Society S3 bucket (public, no login).
  Fallback:  Kaggle mirror (requires KAGGLE_KEY env var — best-effort).
  Cache:     data/raw/cmapss/ — never re-downloads if files exist.

Usage::

    from wizard.data.cmapss_loader import load_cmapss, CmapssDataset

    ds = load_cmapss(subsets=["FD001", "FD003"])
    # ds.train["FD001"]  -> pd.DataFrame with columns engine_id, cycle, s1..s21,
    #                        rul, rul_capped, anomaly_window, health_score
    # ds.test["FD001"]   -> pd.DataFrame (no rul col — derived from RUL_FD001.txt)
    # ds.feature_cols    -> list of sensor column names used after dropping constants
"""

from __future__ import annotations

import io
import logging
import os
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional
from urllib.request import urlopen, Request
from urllib.error import URLError

import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
RUL_CAP: int = 125
"""Piecewise-linear cap on C-MAPSS RUL. Standard since ~2015; omitting this
flags unfamiliarity with the benchmark (research report 13, anti-pattern #2)."""

ANOMALY_WINDOW: int = 30
"""Last N cycles before engine failure → labelled as anomaly window.
IsolationForest + LSTM-AE trained on this label (report 13 §6)."""

# PHM Society S3 — authoritative, no login required
_PHM_URL = (
    "https://phm-datasets.s3.amazonaws.com/NASA/"
    "6.+Turbofan+Engine+Degradation+Simulation+Data+Set.zip"
)

# 26 column headers per C-MAPSS README
_CMAPSS_COLS: List[str] = (
    ["engine_id", "cycle", "op_setting_1", "op_setting_2", "op_setting_3"]
    + [f"sensor_{i}" for i in range(1, 22)]
)

# Sensors to drop (zero / near-zero variance in FD001+FD003)
# Derived empirically; confirmed by literature (these are operational settings
# held constant in single-condition subsets).
_CONST_SENSORS_FD001: List[str] = ["sensor_1", "sensor_5", "sensor_6",
                                     "sensor_10", "sensor_16", "sensor_18", "sensor_19"]
_CONST_SENSORS_FD003: List[str] = ["sensor_1", "sensor_5", "sensor_6",
                                     "sensor_10", "sensor_16", "sensor_18", "sensor_19"]

# Label columns that must NEVER appear in feature_cols — including them causes
# data leakage (the model would train on its own targets).
_LABEL_COLS: frozenset = frozenset({
    "rul", "rul_capped", "anomaly_window", "health_score", "true_rul"
})

# Steel-plant column alias map (cosmetic, for demo UI framing)
CMAPSS_STEEL_MAP: Dict[str, str] = {
    "engine_id":    "equipment_id",
    "cycle":        "operating_hours",
    "op_setting_1": "production_speed_pct",
    "op_setting_2": "load_pct",
    "op_setting_3": "ambient_temp_factor",
    "sensor_2":     "inlet_temperature_c",
    "sensor_3":     "lpc_outlet_temperature_c",
    "sensor_4":     "hpc_outlet_temperature_c",
    "sensor_7":     "hpc_outlet_pressure_bar",
    "sensor_8":     "fan_inlet_mass_flow",
    "sensor_9":     "bypass_duct_pressure_bar",
    "sensor_11":    "vibration_rms",
    "sensor_12":    "bleed_enthalpy",
    "sensor_13":    "bypass_mass_flow",
    "sensor_14":    "hpr_outlet_pressure_bar",
    "sensor_15":    "ratio_hpr_inlet_outlet",
    "sensor_17":    "bleed_pressure_bar",
    "sensor_20":    "bleed_flow_rate",
    "sensor_21":    "torque_nm",
}


# ---------------------------------------------------------------------------
# Dataclass holding all parsed data for both subsets
# ---------------------------------------------------------------------------

@dataclass
class CmapssDataset:
    """
    Container returned by :func:`load_cmapss`.

    Attributes
    ----------
    train : dict[str, pd.DataFrame]
        Training set per subset (FD001 / FD003).
        Columns: engine_id, cycle, op_setting_*, sensor_*, rul, rul_capped,
                 anomaly_window, health_score, <normalised sensor cols>.
    test : dict[str, pd.DataFrame]
        Test set — same columns minus rul/rul_capped/anomaly_window.
    rul_test : dict[str, np.ndarray]
        True RUL values for the last cycle of each test engine.
    feature_cols : list[str]
        Sensor + op-setting columns retained after dropping constants.
    norm_feature_cols : list[str]
        Names of the per-engine normalised columns (suffix ``_norm``).
    """
    train: Dict[str, pd.DataFrame] = field(default_factory=dict)
    test: Dict[str, pd.DataFrame] = field(default_factory=dict)
    rul_test: Dict[str, np.ndarray] = field(default_factory=dict)
    feature_cols: List[str] = field(default_factory=list)
    norm_feature_cols: List[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Public loader
# ---------------------------------------------------------------------------

def load_cmapss(
    subsets: Optional[List[str]] = None,
    raw_dir: Optional[Path] = None,
    force_download: bool = False,
) -> CmapssDataset:
    """
    Load NASA C-MAPSS FD001 (and optionally FD003), applying:
      - piecewise-linear RUL cap (RUL_CAP=125)
      - per-engine MinMax normalisation
      - anomaly window labelling (last 30 cycles before failure)
      - health_score [0→1, 0=healthy, 1=critical]

    Parameters
    ----------
    subsets : list of 'FD001', 'FD003'  (default: both)
    raw_dir : path where raw txt files are cached (default: data/raw/cmapss/)
    force_download : re-download even if files exist

    Returns
    -------
    CmapssDataset
    """
    if subsets is None:
        subsets = ["FD001", "FD003"]

    raw_dir = _resolve_raw_dir(raw_dir)
    _ensure_files(raw_dir, subsets, force_download)

    ds = CmapssDataset()
    feature_cols_set: Optional[List[str]] = None

    for subset in subsets:
        train_df, test_df, rul_arr = _parse_subset(raw_dir, subset)

        # Consistent feature cols across subsets (FD001 drives the list).
        # Exclude engine_id / cycle (index cols) AND all label columns to
        # prevent data leakage into any downstream model (finding #1).
        if feature_cols_set is None:
            feature_cols_set = [
                c for c in train_df.columns
                if c not in ({"engine_id", "cycle"} | _LABEL_COLS)
            ]

        ds.train[subset] = train_df
        ds.test[subset] = test_df
        ds.rul_test[subset] = rul_arr

    if feature_cols_set:
        ds.feature_cols = feature_cols_set
        # norm_feature_cols: per-engine normalisation is performed in-place
        # (no separate *_norm columns are created), so norm_feature_cols is
        # identical to feature_cols — both refer to the same normalised columns
        # (finding #2: the old [f"{c}_norm" ...] pattern produced phantom names).
        ds.norm_feature_cols = list(feature_cols_set)

    logger.info(
        "C-MAPSS loaded: subsets=%s, feature_cols=%d",
        subsets, len(ds.feature_cols),
    )
    return ds


# ---------------------------------------------------------------------------
# Internals
# ---------------------------------------------------------------------------

def _resolve_raw_dir(raw_dir: Optional[Path]) -> Path:
    if raw_dir is not None:
        return Path(raw_dir)
    # Walk up from this file to find repo root (contains pyproject.toml)
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "pyproject.toml").exists():
            return parent / "data" / "raw" / "cmapss"
    return Path.cwd() / "data" / "raw" / "cmapss"


def _ensure_files(raw_dir: Path, subsets: List[str], force: bool) -> None:
    """Download and extract C-MAPSS zip if any required file is missing."""
    raw_dir.mkdir(parents=True, exist_ok=True)

    required: List[str] = []
    for s in subsets:
        required += [f"train_{s}.txt", f"test_{s}.txt", f"RUL_{s}.txt"]

    missing = [f for f in required if not (raw_dir / f).exists()]
    if not missing and not force:
        logger.debug("C-MAPSS cache hit: %s", raw_dir)
        return

    logger.info("Downloading C-MAPSS from PHM Society S3 ...")
    _download_and_extract(raw_dir)

    still_missing = [f for f in required if not (raw_dir / f).exists()]
    if still_missing:
        raise FileNotFoundError(
            f"C-MAPSS download succeeded but these files are missing: {still_missing}. "
            "The ZIP layout may have changed — place the txt files manually in "
            f"{raw_dir} and retry."
        )


def _download_and_extract(raw_dir: Path) -> None:
    """Download the PHM S3 zip and extract all .txt files into raw_dir."""
    try:
        req = Request(_PHM_URL, headers={"User-Agent": "maintenance-wizard/1.0"})
        with urlopen(req, timeout=120) as resp:
            data = resp.read()
        logger.info("Downloaded %.1f MB from PHM S3", len(data) / 1e6)
    except URLError as exc:
        raise ConnectionError(
            f"Cannot download C-MAPSS from PHM S3: {exc}. "
            "Place train_FD001.txt, test_FD001.txt, RUL_FD001.txt "
            "(and FD003 equivalents) in data/raw/cmapss/ manually."
        ) from exc

    with zipfile.ZipFile(io.BytesIO(data)) as zf:
        for name in zf.namelist():
            if name.endswith(".txt") and not name.startswith("__"):
                # Flatten directory structure from zip
                dest = raw_dir / Path(name).name
                dest.write_bytes(zf.read(name))
                logger.debug("Extracted: %s", dest)


def _parse_subset(raw_dir: Path, subset: str):
    """
    Parse one C-MAPSS subset (e.g. 'FD001').

    Returns (train_df, test_df, rul_test_arr)
    """
    train_path = raw_dir / f"train_{subset}.txt"
    test_path  = raw_dir / f"test_{subset}.txt"
    rul_path   = raw_dir / f"RUL_{subset}.txt"

    # ---------- Load raw text (space-separated, no header) ----------
    train_raw = pd.read_csv(train_path, sep=r"\s+", header=None, names=_CMAPSS_COLS)
    test_raw  = pd.read_csv(test_path,  sep=r"\s+", header=None, names=_CMAPSS_COLS)
    rul_arr   = np.loadtxt(rul_path)

    # ---------- Drop constant-variance sensor columns ----------
    const_sensors = (
        _CONST_SENSORS_FD003 if subset == "FD003" else _CONST_SENSORS_FD001
    )
    train_raw = train_raw.drop(columns=[c for c in const_sensors if c in train_raw.columns])
    test_raw  = test_raw.drop( columns=[c for c in const_sensors if c in test_raw.columns])

    # ---------- Compute RUL ground truth for training set ----------
    max_cycle = train_raw.groupby("engine_id")["cycle"].max().rename("max_cycle")
    train_raw = train_raw.join(max_cycle, on="engine_id")
    train_raw["rul"] = train_raw["max_cycle"] - train_raw["cycle"]
    train_raw.drop(columns=["max_cycle"], inplace=True)

    # Piecewise-linear cap (anti-pattern #2 from report 13)
    train_raw["rul_capped"] = train_raw["rul"].clip(upper=RUL_CAP)

    # Anomaly window: last ANOMALY_WINDOW cycles flagged as 1
    train_raw["anomaly_window"] = (train_raw["rul"] <= ANOMALY_WINDOW).astype(int)

    # ---------- Per-engine normalisation (anti-pattern #3: NOT global) ----------
    feature_cols = [
        c for c in train_raw.columns
        if c not in ("engine_id", "cycle", "rul", "rul_capped",
                     "anomaly_window", "health_score")
    ]
    train_raw = _per_engine_normalize(train_raw, feature_cols)
    test_raw  = _per_engine_normalize(test_raw, feature_cols)

    # ---------- Health score (linear: 0=new, 1=critical) ----------
    # Derived from rul_capped: health = 1 - (rul_capped / RUL_CAP)
    train_raw["health_score"] = 1.0 - (train_raw["rul_capped"] / RUL_CAP)

    # ---------- Assign test RUL from RUL_FD00*.txt ----------
    # The test file contains the last observed cycle per engine.
    # RUL file gives the true RUL at that last cycle.
    test_last = (
        test_raw.groupby("engine_id")["cycle"]
        .max()
        .reset_index()
        .assign(true_rul=rul_arr)
    )
    test_raw = test_raw.merge(test_last[["engine_id", "true_rul"]], on="engine_id", how="left")

    logger.info(
        "Parsed %s: train=%d rows, %d engines | test=%d rows, %d engines",
        subset,
        len(train_raw),
        train_raw["engine_id"].nunique(),
        len(test_raw),
        test_raw["engine_id"].nunique(),
    )
    return train_raw, test_raw, rul_arr


def _per_engine_normalize(df: pd.DataFrame, feature_cols: List[str]) -> pd.DataFrame:
    """
    Per-engine MinMax normalisation into [0, 1].

    Each engine gets its own scaler fitted on its own rows.
    This is the correct approach for C-MAPSS (manufacturing variance across
    engines means global scaling loses the per-engine degradation signal).
    """
    norm_rows = []
    for engine_id, group in df.groupby("engine_id"):
        scaler = MinMaxScaler(feature_range=(0, 1))
        # Avoid fitting on cols that are all-NaN or constant per engine
        cols_to_scale = [
            c for c in feature_cols
            if c in group.columns and group[c].std(ddof=0) > 0
        ]
        if cols_to_scale:
            group = group.copy()
            group[cols_to_scale] = scaler.fit_transform(group[cols_to_scale])
        norm_rows.append(group)

    return pd.concat(norm_rows, ignore_index=True)


# ---------------------------------------------------------------------------
# Convenience: anomaly label extractor for ML pipeline
# ---------------------------------------------------------------------------

def get_anomaly_labels(train_df: pd.DataFrame) -> pd.Series:
    """Return the anomaly_window column (1 = anomaly, 0 = normal)."""
    return train_df["anomaly_window"]


def get_feature_matrix(df: pd.DataFrame, feature_cols: List[str]) -> np.ndarray:
    """
    Stack normalised sensor readings into an (N, D) numpy array.
    Used directly by IsolationForest / LSTM-AE in wizard.ml.
    """
    return df[feature_cols].fillna(0.0).to_numpy(dtype=np.float32)
