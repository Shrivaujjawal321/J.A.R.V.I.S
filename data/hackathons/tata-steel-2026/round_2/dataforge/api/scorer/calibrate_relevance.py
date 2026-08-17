#!/usr/bin/env python3
"""
Relevance gate calibration script.
Runs the gate over steel samples (positives) + irrelevant CSVs (negatives)
and prints precision/recall + recommends a threshold.

Usage (from api/ dir with project venv):
  python scorer/calibrate_relevance.py

Or with explicit files:
  python scorer/calibrate_relevance.py \
      --positives ../samples/steel_demo_episode.csv ../samples/steel_good_runtofailure.csv \
      --negatives /tmp/iris.csv /tmp/titanic.csv

The script also auto-generates minimal in-memory negatives (iris-like, titanic-like)
if no --negatives are provided, so it works offline without extra downloads.
"""
from __future__ import annotations

import argparse
import io
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

# Ensure the api/ directory is on sys.path
_API_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(_API_DIR))

from scorer.relevance.gate import score_dataset, get_threshold
from scorer.relevance.embeddings import load_embeddings_model


# ---------------------------------------------------------------------------
# Built-in negative test datasets (generated in-memory; no download needed)
# ---------------------------------------------------------------------------

def _make_iris_df() -> pd.DataFrame:
    """Fisher's iris dataset — clearly irrelevant."""
    rng = np.random.default_rng(42)
    n = 150
    return pd.DataFrame({
        "sepal_length": rng.uniform(4.3, 7.9, n),
        "sepal_width": rng.uniform(2.0, 4.4, n),
        "petal_length": rng.uniform(1.0, 6.9, n),
        "petal_width": rng.uniform(0.1, 2.5, n),
        "species": rng.choice(["setosa", "versicolor", "virginica"], n),
    })


def _make_titanic_df() -> pd.DataFrame:
    """Titanic-like survival dataset — clearly irrelevant."""
    rng = np.random.default_rng(7)
    n = 891
    return pd.DataFrame({
        "PassengerId": range(1, n + 1),
        "Survived": rng.integers(0, 2, n),
        "Pclass": rng.choice([1, 2, 3], n),
        "Name": [f"Person_{i}" for i in range(n)],
        "Sex": rng.choice(["male", "female"], n),
        "Age": rng.uniform(0, 80, n),
        "SibSp": rng.integers(0, 6, n),
        "Parch": rng.integers(0, 6, n),
        "Fare": rng.uniform(0, 512, n),
        "Embarked": rng.choice(["C", "Q", "S"], n),
    })


def _make_iris_renamed_df() -> pd.DataFrame:
    """
    Iris with columns renamed to steel sensor names — gaming attempt.
    Values are physically impossible for those sensor types.
    """
    iris = _make_iris_df()
    iris.columns = ["vibration_mm_s", "temperature_c", "rpm", "current_a", "fault_label"]
    return iris


def _make_random_sensor_named_df() -> pd.DataFrame:
    """Random normal data with sensor column names — gaming attempt."""
    rng = np.random.default_rng(99)
    n = 500
    return pd.DataFrame({
        "timestamp": pd.date_range("2024-01-01", periods=n, freq="1s"),
        "vibration_mm_s": rng.standard_normal(n),  # wrong range: ~N(0,1) not 0-100
        "temperature_bearing_c": rng.standard_normal(n) + 20,  # implausible range
        "pressure_bar": rng.standard_normal(n),
        "current_a": rng.standard_normal(n),
        "rpm": rng.standard_normal(n),
        "failure": rng.integers(0, 2, n),
    })


def _make_weather_df() -> pd.DataFrame:
    """Weather forecast data — has 'temperature' but no steel context."""
    rng = np.random.default_rng(13)
    n = 365
    return pd.DataFrame({
        "date": pd.date_range("2024-01-01", periods=n, freq="1D"),
        "temperature_c": rng.uniform(-10, 40, n),
        "humidity_pct": rng.uniform(20, 100, n),
        "wind_speed_kmh": rng.uniform(0, 100, n),
        "rainfall_mm": rng.uniform(0, 50, n),
        "city": rng.choice(["Mumbai", "Delhi", "Chennai"], n),
    })


# ---------------------------------------------------------------------------
# Built-in positive test datasets (load from samples/ dir)
# ---------------------------------------------------------------------------

_SAMPLES_DIR = Path(__file__).parent.parent.parent / "samples"

BUILTIN_POSITIVES: List[Tuple[str, Optional[Path]]] = [
    ("steel_demo_episode", _SAMPLES_DIR / "steel_demo_episode.csv"),
    ("steel_good_runtofailure", _SAMPLES_DIR / "steel_good_runtofailure.csv"),
    ("steel_weak_dirty", _SAMPLES_DIR / "steel_weak_dirty.csv"),
    ("good_tabular", _SAMPLES_DIR / "good_tabular.csv"),
]

BUILTIN_NEGATIVES: List[Tuple[str, str]] = [
    ("iris", "generated:iris"),
    ("titanic", "generated:titanic"),
    ("weather", "generated:weather"),
]

BUILTIN_GAMING: List[Tuple[str, str]] = [
    ("iris_renamed_sensors", "generated:iris_renamed"),
    ("random_sensor_named", "generated:random_sensor_named"),
]


# ---------------------------------------------------------------------------
# Calibration runner
# ---------------------------------------------------------------------------

def _run_gate(df: pd.DataFrame, name: str) -> Dict:
    result = score_dataset(df=df, filename=name)
    return {
        "name": name,
        "relevance_score": result["relevance_score"],
        "accepted": result["accepted"],
        "kb_match_score": result["kb_match_score"],
        "embed_sim": result.get("embed_sim"),
        "detected_sensors": result["raw_kb"].get("detected_sensors", []),
        "n_sensor_types": result["raw_kb"].get("n_sensor_types", 0),
        "mean_corroboration": result["raw_kb"].get("mean_corroboration", 0),
        "coherence": result["raw_kb"].get("coherence", 0),
    }


def calibrate(
    positive_paths: Optional[List[str]] = None,
    negative_paths: Optional[List[str]] = None,
    threshold_range: Tuple[float, float, float] = (20, 50, 2),
) -> Dict:
    """
    Run calibration sweep. Returns results dict with per-file scores and metrics.
    """
    load_embeddings_model()

    positive_results: List[Dict] = []
    negative_results: List[Dict] = []
    gaming_results: List[Dict] = []

    # ---- Positives ----
    if positive_paths:
        for p in positive_paths:
            path = Path(p)
            if path.is_file():
                df = pd.read_csv(path)
                positive_results.append(_run_gate(df, path.name))
            else:
                print(f"  [WARN] Positive file not found: {p}", file=sys.stderr)
    # Fall back to built-in samples
    if not positive_results:
        for name, path in BUILTIN_POSITIVES:
            if path and path.is_file():
                df = pd.read_csv(path)
                positive_results.append(_run_gate(df, name))
            else:
                print(f"  [SKIP] Built-in positive not found: {path}", file=sys.stderr)

    # ---- Negatives ----
    if negative_paths:
        for p in negative_paths:
            path = Path(p)
            if path.is_file():
                df = pd.read_csv(path)
                negative_results.append(_run_gate(df, path.name))
            else:
                print(f"  [WARN] Negative file not found: {p}", file=sys.stderr)
    # Always include built-in in-memory negatives
    for name, _ in BUILTIN_NEGATIVES:
        if name == "iris":
            df = _make_iris_df()
        elif name == "titanic":
            df = _make_titanic_df()
        elif name == "weather":
            df = _make_weather_df()
        else:
            continue
        negative_results.append(_run_gate(df, name))

    # ---- Gaming ----
    for name, _ in BUILTIN_GAMING:
        if name == "iris_renamed_sensors":
            df = _make_iris_renamed_df()
        elif name == "random_sensor_named":
            df = _make_random_sensor_named_df()
        else:
            continue
        gaming_results.append(_run_gate(df, name))

    def _fmt_e(v):
        return f"{v:.3f}" if v is not None else "N/A"

    # ---- Print individual scores ----
    print("\n=== CALIBRATION RESULTS ===\n")
    print("POSITIVES (should be ACCEPTED):")
    for r in positive_results:
        status = "PASS" if r["accepted"] else "FAIL"
        print(f"  [{status}] {r['name']:40s} score={r['relevance_score']:5.1f}  "
              f"kb={r['kb_match_score']:.3f}  embed={_fmt_e(r['embed_sim'])}")

    print("\nNEGATIVES (should be REJECTED):")
    for r in negative_results:
        status = "PASS" if not r["accepted"] else "FAIL"
        print(f"  [{status}] {r['name']:40s} score={r['relevance_score']:5.1f}  "
              f"kb={r['kb_match_score']:.3f}  embed={_fmt_e(r['embed_sim'])}")

    print("\nGAMING ATTEMPTS (should be REJECTED):")
    for r in gaming_results:
        status = "PASS" if not r["accepted"] else "FAIL (GAMING BYPASSED!)"
        print(f"  [{status}] {r['name']:40s} score={r['relevance_score']:5.1f}  "
              f"kb={r['kb_match_score']:.3f}  "
              f"corr={r['mean_corroboration']:.3f}  coherence={r['coherence']:.3f}")

    # ---- Threshold sweep ----
    print(f"\n=== THRESHOLD SWEEP ({threshold_range[0]:.0f}–{threshold_range[1]:.0f}, step={threshold_range[2]:.0f}) ===\n")
    print(f"{'Threshold':>12} {'Precision':>10} {'Recall':>10} {'FAR_neg':>10} {'FAR_game':>10}")

    all_neg = negative_results + gaming_results
    best_threshold = threshold_range[0]
    best_recall = 0.0

    t = threshold_range[0]
    while t <= threshold_range[1]:
        tp = sum(1 for r in positive_results if r["relevance_score"] >= t)
        fp = sum(1 for r in all_neg if r["relevance_score"] >= t)
        fn = sum(1 for r in positive_results if r["relevance_score"] < t)
        tn = sum(1 for r in all_neg if r["relevance_score"] < t)
        n_neg = len(negative_results)
        n_game = len(gaming_results)
        far_neg = sum(1 for r in negative_results if r["relevance_score"] >= t) / max(n_neg, 1)
        far_game = sum(1 for r in gaming_results if r["relevance_score"] >= t) / max(n_game, 1)

        precision = tp / (tp + fp) if (tp + fp) > 0 else 1.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0

        marker = ""
        # Best threshold = lowest that achieves FAR_neg=0 AND FAR_game=0 AND recall>=0.80
        if far_neg == 0.0 and far_game == 0.0 and recall >= 0.80:
            if recall >= best_recall:
                best_threshold = t
                best_recall = recall
            marker = " <-- candidate"
        print(f"  {t:>10.1f}   {precision:>9.2f}   {recall:>9.2f}   {far_neg:>9.2f}   {far_game:>9.2f}{marker}")
        t += threshold_range[2]

    print(f"\nRECOMMENDED THRESHOLD: {best_threshold:.1f}")
    print(f"(lowest threshold with FAR_neg=0.0, FAR_game=0.0, recall>=0.80)")
    print(f"\nCurrent configured threshold: {get_threshold():.1f}")

    return {
        "positives": positive_results,
        "negatives": negative_results,
        "gaming": gaming_results,
        "recommended_threshold": best_threshold,
        "current_threshold": get_threshold(),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Calibrate EDITH relevance gate")
    parser.add_argument("--positives", nargs="*", help="Positive CSV file paths")
    parser.add_argument("--negatives", nargs="*", help="Negative CSV file paths")
    parser.add_argument(
        "--threshold-range",
        default="20,50,2",
        help="start,stop,step (default: 20,50,2)",
    )
    args = parser.parse_args()

    t_start, t_stop, t_step = [float(x) for x in args.threshold_range.split(",")]
    calibrate(
        positive_paths=args.positives,
        negative_paths=args.negatives,
        threshold_range=(t_start, t_stop, t_step),
    )
