#!/usr/bin/env python3
"""
test_case_checker.py — Cycle gate evaluation for Tata Steel V23+ builds.

CLI:
    python ml_harness/utils/test_case_checker.py \\
      --oof build_v23/oof_v23.parquet \\
      --threshold build_v23/chosen_threshold_v23.json \\
      --fixtures cycles_v2/_fixtures/ \\
      --out cycles_v2/cycle_1/test_report_v23.md

Return code: 0 if all 6 gates pass; otherwise returns count of failed gates.

OOF parquet must contain at least two columns:
  - A CoilID column (name discovered automatically — checks 'CoilID', 'coil_id', 'id')
  - A probability column (name discovered automatically — checks 'oof_proba', 'oof_meta',
    'oof_lgb', 'proba', 'y_pred', 'prediction'; if multiple found, uses the first match
    or the one named in the parquet metadata if present)

The chosen_threshold JSON must contain key 'chosen_threshold'.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Tuple

import numpy as np
import pandas as pd
import yaml


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

def _round1_dir() -> Path:
    """Return the round_1/ directory (parent of ml_harness/)."""
    # __file__ = .../round_1/ml_harness/utils/test_case_checker.py
    # parents[0] = utils/, parents[1] = ml_harness/, parents[2] = round_1/
    return Path(__file__).resolve().parents[2]


TRAIN_PATH_CANDIDATES = [
    # Primary: dataset shipped with the hackathon, at J.A.R.V.I.S. repo root
    _round1_dir().parents[3] / "data set of tata steel" / "dataset" / "train.csv",
    # Fallback: direct absolute path (hardcoded as last resort)
    Path("/home/ujjwal/Documents/J.A.R.V.I.S./data set of tata steel/dataset/train.csv"),
]

# train_v4.parquet is the canonical row-order reference for builds that don't embed CoilID.
# It is sorted by CoilID and all V4+ OOF parquets are row-aligned to it.
TRAIN_V4_PARQUET_CANDIDATES = [
    _round1_dir() / "build_v4" / "train_v4.parquet",
]

COILID_CANDIDATES = ["CoilID", "coil_id", "id"]
PROBA_CANDIDATES = ["oof_proba", "oof_meta", "oof_lgb", "proba", "y_pred", "prediction"]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _find_train_csv() -> Path:
    """Locate train.csv across known candidate paths."""
    for p in TRAIN_PATH_CANDIDATES:
        if p.exists():
            return p
    raise FileNotFoundError(
        f"train.csv not found in candidate paths:\n"
        + "\n".join(str(p) for p in TRAIN_PATH_CANDIDATES)
    )


def _discover_column(df: pd.DataFrame, candidates: list[str], label: str) -> str:
    """Return first candidate column found in df.columns, else raise."""
    for c in candidates:
        if c in df.columns:
            return c
    raise KeyError(
        f"Could not find {label} column in OOF parquet. "
        f"Tried: {candidates}. Available: {df.columns.tolist()}"
    )


def _find_train_v4_parquet() -> Path | None:
    """Locate train_v4.parquet, which provides the canonical CoilID row-order."""
    for p in TRAIN_V4_PARQUET_CANDIDATES:
        if p.exists():
            return p
    return None


def _load_oof(oof_path: Path) -> Tuple[pd.DataFrame, str, str]:
    """Load OOF parquet. Returns (df, coilid_col, proba_col).

    If the OOF parquet lacks a CoilID column, we inject CoilIDs from
    train_v4.parquet (row-aligned by construction for V4+ builds).
    """
    df = pd.read_parquet(oof_path)

    # Discover proba column first (always required)
    proba_col = _discover_column(df, PROBA_CANDIDATES, "oof_proba")

    # Try to find CoilID column
    coilid_col = None
    for c in COILID_CANDIDATES:
        if c in df.columns:
            coilid_col = c
            break

    if coilid_col is None:
        # OOF is row-aligned to train_v4.parquet; inject CoilID from there
        tv4_path = _find_train_v4_parquet()
        if tv4_path is None:
            raise FileNotFoundError(
                "OOF parquet has no CoilID column and train_v4.parquet not found at "
                + str(TRAIN_V4_PARQUET_CANDIDATES[0])
                + ". Cannot align rows to CoilIDs."
            )
        tv4 = pd.read_parquet(tv4_path)[["CoilID"]]
        if len(tv4) != len(df):
            raise ValueError(
                f"OOF has {len(df)} rows but train_v4 has {len(tv4)} rows; "
                "cannot inject CoilID by row alignment."
            )
        df = df.reset_index(drop=True)
        df.insert(0, "CoilID", tv4["CoilID"].values)
        coilid_col = "CoilID"

    return df, coilid_col, proba_col


def _score_at_threshold(
    y_true: np.ndarray, y_proba: np.ndarray, threshold: float
) -> Tuple[float, float, float]:
    """Return (recall, precision, (R+P)/2*100) at given threshold."""
    y_pred = (y_proba >= threshold).astype(int)
    tp = int(((y_pred == 1) & (y_true == 1)).sum())
    fp = int(((y_pred == 1) & (y_true == 0)).sum())
    fn = int(((y_pred == 0) & (y_true == 1)).sum())
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    score = (recall + precision) / 2.0 * 100.0
    return recall, precision, score


def _bootstrap_oof_score(
    y_true: np.ndarray,
    y_proba: np.ndarray,
    threshold: float,
    n: int,
    seed: int,
) -> Tuple[float, float]:
    """Bootstrap (R+P)/2*100 score. Returns (lower_95ci, upper_95ci)."""
    rng = np.random.default_rng(seed)
    scores = []
    n_samples = len(y_true)
    for _ in range(n):
        idx = rng.integers(0, n_samples, size=n_samples)
        _, _, s = _score_at_threshold(y_true[idx], y_proba[idx], threshold)
        scores.append(s)
    scores_arr = np.array(scores)
    lower = float(np.percentile(scores_arr, 2.5))
    upper = float(np.percentile(scores_arr, 97.5))
    return lower, upper


def _bootstrap_subsample_scores(
    y_true: np.ndarray,
    y_proba: np.ndarray,
    threshold: float,
    n_bootstraps: int,
    subsample_frac: float,
    seed: int,
) -> list[float]:
    """Return list of (R+P)/2*100 scores on n_bootstraps subsample draws."""
    rng = np.random.default_rng(seed)
    n_samples = len(y_true)
    k = int(n_samples * subsample_frac)
    scores = []
    for _ in range(n_bootstraps):
        idx = rng.choice(n_samples, size=k, replace=False)
        _, _, s = _score_at_threshold(y_true[idx], y_proba[idx], threshold)
        scores.append(s)
    return scores


# ---------------------------------------------------------------------------
# Gate evaluation
# ---------------------------------------------------------------------------

def run_checks(
    oof_path: Path,
    threshold_path: Path,
    fixtures_dir: Path,
    out_path: Path,
) -> int:
    """Run all 6 gate sets. Returns number of failed gates (0 = all pass)."""

    # ── Load inputs ──────────────────────────────────────────────────────────
    oof_df, coilid_col, proba_col = _load_oof(oof_path)
    oof_df = oof_df.rename(columns={coilid_col: "CoilID", proba_col: "oof_proba"})

    with open(threshold_path) as f:
        threshold_data = json.load(f)
    new_threshold = float(threshold_data["chosen_threshold"])

    hard7 = pd.read_csv(fixtures_dir / "hard7.csv")
    hard_fp10 = pd.read_csv(fixtures_dir / "hard_fp10.csv")
    easy59 = pd.read_csv(fixtures_dir / "easy59.csv")

    with open(fixtures_dir / "test_cases.yaml") as f:
        tc = yaml.safe_load(f)

    v4_threshold = float(tc["v4_chosen_threshold"])
    v4_oof_score = float(tc["v4_oof_score"])

    # Locate train.csv and merge Y labels
    train_path = _find_train_csv()
    train_df = pd.read_csv(train_path)[["CoilID", "Y"]]

    # Build the reference DataFrame aligning OOF probas to train CoilIDs.
    # _load_oof guarantees CoilID is present (injected from train_v4 if missing).
    # Merge on CoilID to get Y labels.
    merged = oof_df[["CoilID", "oof_proba"]].merge(
        train_df.rename(columns={"Y": "Y_true"}), on="CoilID", how="inner"
    )

    y_true = merged["Y_true"].values.astype(int)
    y_proba = merged["oof_proba"].values
    coil_to_proba = dict(zip(merged["CoilID"].values, y_proba))

    # ── Set A: Hard-7 ─────────────────────────────────────────────────────────
    half_v4 = 0.5 * v4_threshold
    set_a_rows = []
    for _, row in hard7.iterrows():
        cid = int(row["CoilID"])
        new_proba = coil_to_proba.get(cid, float("nan"))
        per_row_pass = bool(new_proba > half_v4)
        caught_at_build_threshold = bool(new_proba > new_threshold)
        set_a_rows.append({
            "CoilID": cid,
            "v4_proba": row["v4_oof_proba"],
            "new_proba": new_proba,
            "per_row_pass (>0.5*v4_thresh)": per_row_pass,
            "caught_at_new_thresh": caught_at_build_threshold,
        })
    set_a_per_row_passes = sum(r["per_row_pass (>0.5*v4_thresh)"] for r in set_a_rows)
    set_a_gate = set_a_per_row_passes >= 1  # at_least 1 of 7

    # ── Set B: Hard-FP-10 ────────────────────────────────────────────────────
    set_b_rows = []
    for _, row in hard_fp10.iterrows():
        cid = int(row["CoilID"])
        new_proba = coil_to_proba.get(cid, float("nan"))
        per_row_pass = bool(new_proba < new_threshold)
        set_b_rows.append({
            "CoilID": cid,
            "v4_proba": row["v4_oof_proba"],
            "new_proba": new_proba,
            "per_row_pass (<new_thresh)": per_row_pass,
        })
    set_b_passes = sum(r["per_row_pass (<new_thresh)"] for r in set_b_rows)
    set_b_gate = set_b_passes >= 5  # at_least 5 of 10

    # ── Set C: Easy-59 ───────────────────────────────────────────────────────
    set_c_rows = []
    for _, row in easy59.iterrows():
        cid = int(row["CoilID"])
        new_proba = coil_to_proba.get(cid, float("nan"))
        per_row_pass = bool(new_proba > new_threshold)
        set_c_rows.append({
            "CoilID": cid,
            "v4_proba": row["v4_oof_proba"],
            "new_proba": new_proba,
            "per_row_pass (>new_thresh)": per_row_pass,
        })
    set_c_passes = sum(r["per_row_pass (>new_thresh)"] for r in set_c_rows)
    set_c_gate = set_c_passes >= 58  # at_least 58 of 59

    # ── Set D: OOF score gate + bootstrap CI ─────────────────────────────────
    _, _, new_oof_score = _score_at_threshold(y_true, y_proba, new_threshold)
    bs_n = int(tc["set_D"]["bootstrap_n"])
    bs_seed = int(tc["set_D"]["bootstrap_seed"])
    bs_lower, bs_upper = _bootstrap_oof_score(y_true, y_proba, new_threshold, bs_n, bs_seed)
    oof_score_min = float(tc["set_D"]["oof_score_min"])
    bs_lower_ci_min = float(tc["set_D"]["bootstrap_lower_ci_min"])
    set_d_gate = (new_oof_score >= oof_score_min) and (bs_lower >= bs_lower_ci_min)

    # ── Set E: Stability across bootstrap subsamples ──────────────────────────
    n_bs_e = int(tc["set_E"]["n_bootstraps"])
    sub_frac = float(tc["set_E"]["subsample_frac"])
    max_std = float(tc["set_E"]["max_std"])
    # Use same seed as Set D for reproducibility
    sub_scores = _bootstrap_subsample_scores(
        y_true, y_proba, new_threshold, n_bs_e, sub_frac, seed=bs_seed
    )
    sub_std = float(np.std(sub_scores))
    set_e_gate = sub_std <= max_std

    # ── Set F: Calibrated LB estimate ────────────────────────────────────────
    calibration_offset = float(tc["set_F"]["formula"].split("+")[1])  # parses "oof_score + 2.67"
    min_calibrated = float(tc["set_F"]["min_calibrated"])
    calibrated_lb = new_oof_score + calibration_offset
    set_f_gate = calibrated_lb >= min_calibrated

    # ── Aggregate ────────────────────────────────────────────────────────────
    gates = {
        "A": set_a_gate,
        "B": set_b_gate,
        "C": set_c_gate,
        "D": set_d_gate,
        "E": set_e_gate,
        "F": set_f_gate,
    }
    gates_passed = sum(gates.values())
    gates_failed = 6 - gates_passed

    # ── Emit markdown report ─────────────────────────────────────────────────
    out_path.parent.mkdir(parents=True, exist_ok=True)
    build_name = oof_path.parent.name

    lines = [
        f"# Test Gate Report — {build_name}",
        "",
        f"**OOF parquet:** `{oof_path}`",
        f"**Threshold:** {new_threshold:.8f}",
        f"**V4 threshold (reference):** {v4_threshold:.8f}",
        "",
        "---",
        "",
        "## Set A — Hard-7 (most precarious true defects)",
        "",
        f"> Gate: at least 1 of 7 rows must have `new_oof_proba > 0.5 * v4_threshold` ({half_v4:.8f})",
        "",
        f"| CoilID | v4_proba | new_proba | >0.5×v4_thresh | caught@new_thresh |",
        f"|--------|----------|-----------|----------------|-------------------|",
    ]
    for r in set_a_rows:
        check = "YES" if r["per_row_pass (>0.5*v4_thresh)"] else "NO"
        caught = "YES" if r["caught_at_new_thresh"] else "NO"
        lines.append(
            f"| {r['CoilID']} | {r['v4_proba']:.6f} | {r['new_proba']:.6f} | {check} | {caught} |"
        )
    tick = "[x]" if set_a_gate else "[ ]"
    lines += [
        "",
        f"**Per-row passes:** {set_a_per_row_passes} / 7",
        f"- {tick} **Set A GATE: {'PASS' if set_a_gate else 'FAIL'}** ({set_a_per_row_passes}/7 >= 1)",
        "",
    ]

    lines += [
        "## Set B — Hard-FP-10 (hardest false positives)",
        "",
        f"> Gate: at least 5 of 10 rows must have `new_oof_proba < new_threshold` ({new_threshold:.8f})",
        "",
        f"| CoilID | v4_proba | new_proba | <new_thresh |",
        f"|--------|----------|-----------|-------------|",
    ]
    for r in set_b_rows:
        check = "YES" if r["per_row_pass (<new_thresh)"] else "NO"
        lines.append(f"| {r['CoilID']} | {r['v4_proba']:.6f} | {r['new_proba']:.6f} | {check} |")
    tick = "[x]" if set_b_gate else "[ ]"
    lines += [
        "",
        f"**Per-row passes:** {set_b_passes} / 10",
        f"- {tick} **Set B GATE: {'PASS' if set_b_gate else 'FAIL'}** ({set_b_passes}/10 >= 5)",
        "",
    ]

    lines += [
        "## Set C — Easy-59 (regression guard)",
        "",
        f"> Gate: at least 58 of 59 rows must have `new_oof_proba > new_threshold` ({new_threshold:.8f})",
        "",
        f"| CoilID | v4_proba | new_proba | >new_thresh |",
        f"|--------|----------|-----------|-------------|",
    ]
    # Only print failures + first 10 passes to keep report readable
    c_printed = 0
    c_failures = [r for r in set_c_rows if not r["per_row_pass (>new_thresh)"]]
    c_passes_sample = [r for r in set_c_rows if r["per_row_pass (>new_thresh)"]][:10]
    for r in c_failures:
        lines.append(f"| {r['CoilID']} | {r['v4_proba']:.6f} | {r['new_proba']:.6f} | NO |")
    for r in c_passes_sample:
        lines.append(f"| {r['CoilID']} | {r['v4_proba']:.6f} | {r['new_proba']:.6f} | YES |")
    if len(c_passes_sample) < set_c_passes:
        lines.append(f"| ... | ... | ... | YES ({set_c_passes - len(c_passes_sample)} more) |")
    tick = "[x]" if set_c_gate else "[ ]"
    lines += [
        "",
        f"**Per-row passes:** {set_c_passes} / 59",
        f"- {tick} **Set C GATE: {'PASS' if set_c_gate else 'FAIL'}** ({set_c_passes}/59 >= 58)",
        "",
    ]

    recall_d, prec_d, _ = _score_at_threshold(y_true, y_proba, new_threshold)
    lines += [
        "## Set D — OOF Score Gate",
        "",
        f"| Metric | Value | Threshold | Pass? |",
        f"|--------|-------|-----------|-------|",
        f"| OOF (R+P)/2 score | {new_oof_score:.4f} | >= {oof_score_min} | {'YES' if new_oof_score >= oof_score_min else 'NO'} |",
        f"| Bootstrap 95% CI lower (n={bs_n}, seed={bs_seed}) | {bs_lower:.4f} | >= {bs_lower_ci_min} | {'YES' if bs_lower >= bs_lower_ci_min else 'NO'} |",
        f"| Bootstrap 95% CI upper | {bs_upper:.4f} | — | — |",
        f"| Recall @ new_threshold | {recall_d:.4f} | — | — |",
        f"| Precision @ new_threshold | {prec_d:.4f} | — | — |",
    ]
    tick = "[x]" if set_d_gate else "[ ]"
    lines += [
        "",
        f"- {tick} **Set D GATE: {'PASS' if set_d_gate else 'FAIL'}** (OOF={new_oof_score:.2f}>={oof_score_min} AND CI_lower={bs_lower:.2f}>={bs_lower_ci_min})",
        "",
    ]

    lines += [
        "## Set E — Stability (bootstrap subsamples)",
        "",
        f"> Gate: std of (R+P)/2 across {n_bs_e} × {sub_frac*100:.0f}% subsamples <= {max_std}",
        "",
        f"| Subsample | Score |",
        f"|-----------|-------|",
    ]
    for i, s in enumerate(sub_scores, 1):
        lines.append(f"| {i} | {s:.4f} |")
    tick = "[x]" if set_e_gate else "[ ]"
    lines += [
        "",
        f"**Std:** {sub_std:.4f}",
        f"- {tick} **Set E GATE: {'PASS' if set_e_gate else 'FAIL'}** (std={sub_std:.3f} <= {max_std})",
        "",
    ]

    blend_penalty = float(tc["set_F"]["blend_penalty"])
    lines += [
        "## Set F — Calibrated LB Estimate",
        "",
        f"| Formula | Value |",
        f"|---------|-------|",
        f"| OOF score | {new_oof_score:.4f} |",
        f"| Calibration offset (+2.67 V4-validated) | +{calibration_offset} |",
        f"| Single-model calibrated LB est | {calibrated_lb:.4f} |",
        f"| Blend penalty (if blended) | {blend_penalty} |",
        f"| Minimum required calibrated LB | {min_calibrated} |",
    ]
    tick = "[x]" if set_f_gate else "[ ]"
    lines += [
        "",
        f"- {tick} **Set F GATE: {'PASS' if set_f_gate else 'FAIL'}** (calibrated_LB={calibrated_lb:.2f} >= {min_calibrated})",
        "",
        "---",
        "",
        "## Summary",
        "",
    ]
    for name, passed in gates.items():
        tick = "[x]" if passed else "[ ]"
        lines.append(f"- {tick} Set {name}: {'PASS' if passed else 'FAIL'}")
    lines += [
        "",
        f"## GATES PASSED: {gates_passed} / 6",
        "",
        f"**Build name:** {build_name}",
        f"**New threshold:** {new_threshold:.8f}",
        f"**V4 reference threshold:** {v4_threshold:.8f}",
        f"**New OOF score:** {new_oof_score:.4f}",
        f"**V4 OOF score (reference):** {v4_oof_score}",
        f"**Calibrated LB estimate:** {calibrated_lb:.4f}",
        f"**Bootstrap 95% CI:** [{bs_lower:.4f}, {bs_upper:.4f}]",
        "",
        "_Generated by test_case_checker.py_",
    ]

    out_path.write_text("\n".join(lines))
    print(f"Report written to: {out_path}")
    print(f"GATES PASSED: {gates_passed} / 6")
    if gates_failed > 0:
        failed_names = [k for k, v in gates.items() if not v]
        print(f"FAILED GATES: {', '.join(failed_names)}")

    return gates_failed


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Evaluate a new build against the Tata Steel cycle test cases."
    )
    p.add_argument(
        "--oof", required=True,
        help="Path to OOF parquet (must contain CoilID + oof_proba columns, or row-aligned to train_v4)."
    )
    p.add_argument(
        "--threshold", required=True,
        help="Path to chosen_threshold JSON (must contain key 'chosen_threshold')."
    )
    p.add_argument(
        "--fixtures", required=True,
        help="Path to _fixtures/ directory containing hard7.csv, hard_fp10.csv, easy59.csv, test_cases.yaml."
    )
    p.add_argument(
        "--out", required=True,
        help="Output path for the markdown gate report."
    )
    return p.parse_args()


def main() -> None:
    args = _parse_args()
    failed = run_checks(
        oof_path=Path(args.oof),
        threshold_path=Path(args.threshold),
        fixtures_dir=Path(args.fixtures),
        out_path=Path(args.out),
    )
    sys.exit(failed)


if __name__ == "__main__":
    main()
