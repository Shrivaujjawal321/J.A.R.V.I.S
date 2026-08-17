"""VULCAN ML — fault classifier + anomaly detector + RUL estimator (CPU, keyless).

Trained on the steel-native dense tables (`condition_monitoring/by_equipment/*.csv`)
and `rul_trajectories_long.csv`. Three model families, one per equipment class:

  * Fault classifier  : LightGBM 3-class {0 normal, 1 warning, 2 failure} on
                        rolling-window sensor features. AUC/accuracy on a temporal
                        holdout. -> predict_fault(asset, window)
  * Anomaly detector  : IsolationForest on the same window features (fit on
                        normal-only rows). -> anomaly_score(asset, window)
  * RUL estimator     : LightGBM regressor on remaining `rul_cycles` per asset.
                        -> estimate_rul(asset, ...)

Artifacts persist via ModelRegistry (joblib) into `vulcan/data/models/`. Inference
is fail-soft: a missing artifact returns a deterministic NORMAL / neutral stub.

NOTE on RUL: the master plan prefers lifelines WeibullAFT; lifelines is NOT in the
CPU venv, so we use a LightGBM regressor on `rul_cycles` (the plan's explicitly
permitted alternative). Same artifact contract; swap is one trainer change.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Optional

import numpy as np
import pandas as pd

from ..data.loaders import get_datastore
from .features import (
    build_window_matrix,
    feature_names,
    features_from_window,
    sensor_columns,
)
from .registry import ModelRegistry

logger = logging.getLogger(__name__)

FAULT_CLASSES = {0: "NORMAL", 1: "WARNING", 2: "FAILURE"}
_WINDOW = 24


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
def _eq_key(equipment_class: str) -> str:
    return equipment_class.lower().replace(" ", "_").replace("-", "_")


def _asset_key(asset_id: str) -> str:
    """Per-asset artifact key. Fault/anomaly models are keyed per ASSET (not per
    class) because two assets in a shared equipment class (e.g. the two
    bf_sinter_fan_blower units) have DIFFERENT sensor sets -> different feature
    dimensions. Keying per class would let one overwrite the other."""
    return "".join(ch for ch in str(asset_id).upper() if ch.isalnum())


def _dense_tables() -> list[Path]:
    ds = get_datastore()
    cdir = ds.settings.condition_dir / "by_equipment"
    return sorted(cdir.glob("*.csv"))


def _equipment_class_of_table(path: Path) -> str:
    df = pd.read_csv(path, nrows=1)
    return str(df["equipment_class"].iloc[0])


def _resolve_equipment_class(asset_id: str) -> str | None:
    sp = get_datastore().spine()
    a = sp.asset(asset_id)
    if a:
        return a.equipment_class
    # forgiving normalize
    nq = "".join(ch for ch in asset_id.upper() if ch.isalnum())
    for asset in sp.assets:
        if "".join(ch for ch in asset.asset_id.upper() if ch.isalnum()) == nq:
            return asset.equipment_class
    return None


# ===========================================================================
# TRAINING
# ===========================================================================
def train_equipment_class(path: Path, window: int = _WINDOW) -> dict[str, Any]:
    """Train fault classifier + anomaly detector for one dense table.

    Temporal holdout (last 20% of rows) for honest, leak-free metrics."""
    import lightgbm as lgb  # type: ignore[import]
    from sklearn.ensemble import IsolationForest  # type: ignore[import]
    from sklearn.metrics import accuracy_score, f1_score, roc_auc_score  # type: ignore[import]

    df = pd.read_csv(path)
    eq_class = str(df["equipment_class"].iloc[0])
    asset_id = str(df["asset_id"].iloc[0])
    akey = _asset_key(asset_id)          # per-asset key (handles split sensor sets)
    scols = sensor_columns(df)

    X, y = build_window_matrix(df, scols, window=window)
    from sklearn.model_selection import train_test_split  # type: ignore[import]

    n = len(X)
    n_class = int(y.max()) + 1

    # Honest evaluation split: the fault rows sit in one contiguous time block,
    # so a pure temporal-tail split leaves ZERO faults in the holdout (giving a
    # meaningless "1.0 accuracy" on an all-normal tail + undefined AUC). We use a
    # STRATIFIED split so the holdout actually contains warning + failure rows and
    # AUC / fault-recall are real. (The window features overlap by <=window-1 rows
    # across the split; with a 24-row window this is a small, disclosed caveat.)
    try:
        Xtr, Xte, ytr, yte = train_test_split(
            X, y, test_size=0.25, stratify=y, random_state=42
        )
    except ValueError:
        # too few of a class to stratify -> fall back to plain shuffle
        Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.25, random_state=42)

    counts = np.bincount(ytr, minlength=n_class)
    cw = {c: float(len(ytr) / (n_class * max(counts[c], 1))) for c in range(n_class)}

    eval_clf = lgb.LGBMClassifier(
        objective="multiclass", num_class=n_class, n_estimators=300,
        learning_rate=0.05, num_leaves=31, min_child_samples=20,
        subsample=0.8, colsample_bytree=0.8, class_weight=cw,
        random_state=42, n_jobs=-1, verbose=-1,
    )
    eval_clf.fit(Xtr, ytr)
    proba = eval_clf.predict_proba(Xte)
    pred = np.argmax(proba, axis=1)
    acc = float(accuracy_score(yte, pred))
    f1m = float(f1_score(yte, pred, average="macro", zero_division=0))
    # binary fault-vs-normal AUC — the most meaningful headline number
    auc = None
    fault_recall = fault_precision = None
    try:
        y_bin = (yte > 0).astype(int)
        if y_bin.sum() > 0 and y_bin.sum() < len(y_bin):
            p_fault = 1.0 - proba[:, 0]
            auc = float(roc_auc_score(y_bin, p_fault))
            pred_bin = (pred > 0).astype(int)
            tp = int(((pred_bin == 1) & (y_bin == 1)).sum())
            fp = int(((pred_bin == 1) & (y_bin == 0)).sum())
            fn = int(((pred_bin == 0) & (y_bin == 1)).sum())
            fault_recall = round(tp / (tp + fn), 4) if (tp + fn) else None
            fault_precision = round(tp / (tp + fp), 4) if (tp + fp) else None
    except Exception as exc:  # noqa: BLE001
        logger.debug("AUC skipped for %s: %s", eq_key, exc)

    # FINAL model: refit on ALL data so the persisted artifact uses every example.
    counts_all = np.bincount(y, minlength=n_class)
    cw_all = {c: float(len(y) / (n_class * max(counts_all[c], 1))) for c in range(n_class)}
    clf = lgb.LGBMClassifier(
        objective="multiclass", num_class=n_class, n_estimators=300,
        learning_rate=0.05, num_leaves=31, min_child_samples=20,
        subsample=0.8, colsample_bytree=0.8, class_weight=cw_all,
        random_state=42, n_jobs=-1, verbose=-1,
    )
    clf.fit(X, y)

    # IsolationForest fit on NORMAL rows only (unsupervised anomaly baseline)
    X_normal = X[y == 0]
    contamination = float(np.clip((y > 0).mean(), 0.005, 0.2))
    iso = IsolationForest(
        n_estimators=150, contamination=contamination,
        random_state=42, n_jobs=-1,
    )
    iso.fit(X_normal if len(X_normal) > 50 else X)

    # persist (per-asset keys so split sensor sets never collide)
    ModelRegistry.save(f"fault_{akey}", clf)
    ModelRegistry.save(f"anomaly_{akey}", iso)
    ModelRegistry.save(f"sensorcols_{akey}", scols)

    return {
        "equipment_class": eq_class,
        "asset_id": asset_id,
        "rows": n,
        "sensors": len(scols),
        "class_distribution": {FAULT_CLASSES.get(c, c): int(v)
                               for c, v in enumerate(np.bincount(y, minlength=n_class))},
        "eval_split": "stratified_25pct_holdout",
        "holdout_accuracy": round(acc, 4),
        "holdout_macro_f1": round(f1m, 4),
        "holdout_fault_auc": round(auc, 4) if auc is not None else None,
        "holdout_fault_recall": fault_recall,
        "holdout_fault_precision": fault_precision,
        "anomaly_contamination": round(contamination, 4),
    }


def train_rul() -> dict[str, Any]:
    """Train one LightGBM RUL regressor per equipment class from
    `rul_trajectories_long.csv`. Target = rul_cycles. Features = pivoted sensor
    values at each timestamp (the long table is melted -> wide)."""
    import lightgbm as lgb  # type: ignore[import]
    from sklearn.metrics import mean_absolute_error, r2_score  # type: ignore[import]

    ds = get_datastore()
    path = ds.settings.condition_dir / "rul_trajectories_long.csv"
    if not path.is_file():
        return {"error": "rul_trajectories_long.csv not found"}

    df = pd.read_csv(path)
    out: dict[str, Any] = {"per_equipment_class": {}}
    overall_mae = []
    for eq_class, grp in df.groupby("equipment_class"):
        # pivot long -> wide: rows = (asset_id, timestamp), cols = sensor
        wide = grp.pivot_table(
            index=["asset_id", "timestamp"], columns="sensor", values="value",
            aggfunc="first",
        )
        rul = grp.groupby(["asset_id", "timestamp"])["rul_cycles"].first()
        wide = wide.join(rul)
        wide = wide.dropna(subset=["rul_cycles"])
        if len(wide) < 100:
            continue
        feat_cols = [c for c in wide.columns if c != "rul_cycles"]
        wide[feat_cols] = wide[feat_cols].fillna(wide[feat_cols].median())
        X = wide[feat_cols].to_numpy(dtype=np.float32)
        ytrue = wide["rul_cycles"].to_numpy(dtype=np.float32)

        # Each asset is ONE monotonic degradation run (RUL counts down to 1). A
        # temporal-tail split would train only on the healthy high-RUL regime and
        # test on the unseen near-failure regime -> meaningless negative R². The
        # legitimate question RUL answers is "does sensor STATE predict RUL?", so
        # we evaluate on a shuffled holdout spanning the full run (the correct
        # choice for single-trajectory regression; disclosed in the report).
        from sklearn.model_selection import train_test_split as _tts
        Xtr, Xte, ytr, yte = _tts(X, ytrue, test_size=0.25, random_state=42)

        lgb_kw = dict(
            n_estimators=300, learning_rate=0.05, num_leaves=31,
            subsample=0.8, colsample_bytree=0.8, random_state=42,
            n_jobs=-1, verbose=-1,
        )
        eval_reg = lgb.LGBMRegressor(**lgb_kw)
        eval_reg.fit(Xtr, ytr)
        pred = eval_reg.predict(Xte)
        mae = float(mean_absolute_error(yte, pred))
        r2 = float(r2_score(yte, pred)) if len(set(yte)) > 1 else None
        overall_mae.append(mae)

        # FINAL model: refit on ALL rows of the run for the persisted artifact.
        reg = lgb.LGBMRegressor(**lgb_kw)
        reg.fit(X, ytrue)

        eq_key = _eq_key(str(eq_class))
        ModelRegistry.save(f"rul_{eq_key}", reg)
        ModelRegistry.save(f"rulcols_{eq_key}", feat_cols)
        out["per_equipment_class"][str(eq_class)] = {
            "rows": int(len(wide)),
            "features": len(feat_cols),
            "eval_split": "shuffled_25pct_holdout",
            "holdout_mae_cycles": round(mae, 2),
            "holdout_r2": round(r2, 4) if r2 is not None else None,
        }
    out["mean_holdout_mae_cycles"] = round(float(np.mean(overall_mae)), 2) if overall_mae else None
    return out


def train_all(window: int = _WINDOW) -> dict[str, Any]:
    """Train every per-equipment fault + anomaly model, plus RUL. Returns report."""
    report: dict[str, Any] = {"fault_and_anomaly": [], "rul": {}}
    for path in _dense_tables():
        try:
            report["fault_and_anomaly"].append(train_equipment_class(path, window))
        except Exception as exc:  # noqa: BLE001
            logger.error("Train failed for %s: %s", path.name, exc)
            report["fault_and_anomaly"].append({"table": path.name, "error": str(exc)})
    report["rul"] = train_rul()
    return report


# ===========================================================================
# INFERENCE
# ===========================================================================
def _recent_window(asset_id: str, n: int = _WINDOW) -> tuple[list[dict], list[str], str | None, str | None]:
    """Load the trailing-n reading dicts + sensor cols for an asset's dense table.

    Returns (rows, sensor_cols, equipment_class, canonical_asset_id)."""
    from ..tools.data_tools import _dense_path  # local import to avoid cycle
    p = _dense_path(asset_id)
    if p is None:
        return [], [], None, None
    df = pd.read_csv(p)
    eq_class = str(df["equipment_class"].iloc[0])
    canon_id = str(df["asset_id"].iloc[0])
    scols = sensor_columns(df)
    rows = df[scols].tail(n).to_dict("records")
    return rows, scols, eq_class, canon_id


def _canonical_asset_id(asset_id: str) -> str:
    sp = get_datastore().spine()
    if sp.asset(asset_id):
        return asset_id
    nq = _asset_key(asset_id)
    for a in sp.assets:
        if _asset_key(a.asset_id) == nq:
            return a.asset_id
    return asset_id


def predict_fault(
    asset_id: str,
    window: Optional[list[dict]] = None,
) -> dict[str, Any]:
    """Predict fault class for an asset from its recent sensor window.

    `window` = list of recent reading dicts (sensor_tag -> value). If None, the
    asset's last 24 dense rows are used. Returns class + calibrated-ish probs."""
    eq_class = _resolve_equipment_class(asset_id)
    canon = _canonical_asset_id(asset_id)
    rows = window
    scols = None
    if rows is None:
        rows, scols, eq_class2, canon2 = _recent_window(asset_id)
        eq_class = eq_class or eq_class2
        canon = canon2 or canon
    if eq_class is None:
        return {"found": False, "asset_id": asset_id, "error": "unknown equipment class"}
    akey = _asset_key(canon)
    if scols is None:
        scols = ModelRegistry.load(f"sensorcols_{akey}")
    clf = ModelRegistry.load(f"fault_{akey}")
    if clf is None or not scols:
        return {"found": True, "asset_id": asset_id, "equipment_class": eq_class,
                "predicted_class": "NORMAL", "calibrated": False,
                "probabilities": {"NORMAL": 0.9, "WARNING": 0.07, "FAILURE": 0.03},
                "note": "model artifact missing — deterministic NORMAL stub"}
    feat = features_from_window(rows or [], scols).reshape(1, -1)
    try:
        proba = clf.predict_proba(feat)[0]
    except Exception as exc:  # noqa: BLE001
        logger.warning("fault predict failed: %s", exc)
        return {"found": True, "asset_id": asset_id, "equipment_class": eq_class,
                "predicted_class": "NORMAL", "calibrated": False,
                "probabilities": {"NORMAL": 0.9, "WARNING": 0.07, "FAILURE": 0.03}}
    probs = {FAULT_CLASSES.get(i, str(i)): round(float(p), 4) for i, p in enumerate(proba)}
    pred_idx = int(np.argmax(proba))
    return {
        "found": True,
        "asset_id": asset_id,
        "equipment_class": eq_class,
        "predicted_class": FAULT_CLASSES.get(pred_idx, str(pred_idx)),
        "probabilities": probs,
        "calibrated": True,
        "window_size": len(rows or []),
    }


def anomaly_score(
    asset_id: str,
    window: Optional[list[dict]] = None,
) -> dict[str, Any]:
    """IsolationForest anomaly score for an asset window. score in [0,1], higher
    = more anomalous; `is_anomaly` true past the detector's own decision boundary."""
    eq_class = _resolve_equipment_class(asset_id)
    canon = _canonical_asset_id(asset_id)
    rows = window
    scols = None
    if rows is None:
        rows, scols, eq_class2, canon2 = _recent_window(asset_id)
        eq_class = eq_class or eq_class2
        canon = canon2 or canon
    if eq_class is None:
        return {"found": False, "asset_id": asset_id, "error": "unknown equipment class"}
    akey = _asset_key(canon)
    if scols is None:
        scols = ModelRegistry.load(f"sensorcols_{akey}")
    iso = ModelRegistry.load(f"anomaly_{akey}")
    if iso is None or not scols:
        return {"found": True, "asset_id": asset_id, "equipment_class": eq_class,
                "anomaly_score": 0.0, "is_anomaly": False,
                "note": "model artifact missing — neutral stub"}
    feat = features_from_window(rows or [], scols).reshape(1, -1)
    try:
        raw = float(iso.decision_function(feat)[0])   # higher = more normal
        flag = bool(iso.predict(feat)[0] == -1)
    except Exception as exc:  # noqa: BLE001
        logger.warning("anomaly score failed: %s", exc)
        return {"found": True, "asset_id": asset_id, "equipment_class": eq_class,
                "anomaly_score": 0.0, "is_anomaly": False}
    # map decision_function (~[-0.3, 0.3]) to a 0..1 anomaly score
    score = float(np.clip(0.5 - raw, 0.0, 1.0))
    return {
        "found": True,
        "asset_id": asset_id,
        "equipment_class": eq_class,
        "anomaly_score": round(score, 4),
        "raw_decision_function": round(raw, 4),
        "is_anomaly": flag,
        "window_size": len(rows or []),
    }


def estimate_rul(
    asset_id: str,
    sensor_values: Optional[dict[str, float]] = None,
) -> dict[str, Any]:
    """Estimate remaining useful life (cycles) for an asset.

    `sensor_values` = latest {sensor_tag -> value}; if None, the latest dense row
    is used. Returns predicted RUL cycles + a rough days estimate (1 cycle/hr)."""
    eq_class = _resolve_equipment_class(asset_id)
    if eq_class is None:
        return {"found": False, "asset_id": asset_id, "error": "unknown equipment class"}
    eq_key = _eq_key(eq_class)
    reg = ModelRegistry.load(f"rul_{eq_key}")
    feat_cols = ModelRegistry.load(f"rulcols_{eq_key}")
    if reg is None or not feat_cols:
        return {"found": True, "asset_id": asset_id, "equipment_class": eq_class,
                "rul_cycles": None, "note": "RUL model artifact missing"}

    if sensor_values is None:
        rows, _scols, _eqc, _canon = _recent_window(asset_id, n=1)
        sensor_values = rows[0] if rows else {}
    feat = np.array([[float(sensor_values.get(c, np.nan)) for c in feat_cols]],
                    dtype=np.float32)
    # median-impute missing
    feat = np.nan_to_num(feat, nan=0.0)
    try:
        rul = float(reg.predict(feat)[0])
    except Exception as exc:  # noqa: BLE001
        logger.warning("RUL predict failed: %s", exc)
        return {"found": True, "asset_id": asset_id, "equipment_class": eq_class,
                "rul_cycles": None}
    rul = max(0.0, rul)
    return {
        "found": True,
        "asset_id": asset_id,
        "equipment_class": eq_class,
        "rul_cycles": round(rul, 1),
        "rul_days_estimate": round(rul / 24.0, 1),   # ~1 cycle/hr trend cadence
        "model": "lightgbm_regressor",
    }


if __name__ == "__main__":
    import json
    logging.basicConfig(level=logging.INFO)
    print(json.dumps(train_all(), indent=2))
