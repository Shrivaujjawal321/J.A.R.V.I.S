"""Duplicates dimension: exact row duplicates, near-dup estimate, and timestamp duplicates."""

from __future__ import annotations
import pandas as pd
import numpy as np
from typing import Any, Dict, List, Optional


def _detect_group_col(df: pd.DataFrame) -> Optional[str]:
    """Detect asset / unit identifier column."""
    candidates = ["asset_id", "machine_id", "unit_number", "engine_id", "unit", "asset", "machine"]
    col_lower = {c.lower(): c for c in df.columns}
    for cand in candidates:
        if cand in col_lower:
            return col_lower[cand]
    return None


def _detect_timestamp_col_local(df: pd.DataFrame, ctx: Dict) -> Optional[str]:
    """Prefer ctx hint, else sniff from column names."""
    hint = ctx.get("timestamp_col")
    if hint and hint in df.columns:
        return hint
    for col in df.columns:
        if any(k in col.lower() for k in ["time", "date", "ts", "timestamp", "datetime"]):
            try:
                pd.to_datetime(df[col].dropna().iloc[:20], errors="raise")
                return col
            except Exception:
                pass
    return None


def compute(df: pd.DataFrame, **ctx) -> Dict[str, Any]:
    n_rows = len(df)
    if n_rows == 0:
        return {"score": 0.0, "detail": "Empty dataset.", "severity": "critical", "raw": {}}

    # ------------------------------------------------------------------
    # 1. Exact row duplicates (all columns)
    # ------------------------------------------------------------------
    dupe_mask = df.duplicated()
    exact_count = int(dupe_mask.sum())
    exact_frac = exact_count / n_rows

    # ------------------------------------------------------------------
    # 2. Near-duplicate estimate (rounded numeric hash)
    # ------------------------------------------------------------------
    sample_size = min(n_rows, 50_000)
    df_sample = df.sample(n=sample_size, random_state=42) if n_rows > sample_size else df

    num_cols = df_sample.select_dtypes(include=[np.number]).columns.tolist()
    near_dup_count = 0
    near_dup_frac = 0.0

    if num_cols:
        try:
            rounded = df_sample[num_cols].apply(
                lambda col: col.round(1) if col.dtype in [np.float64, np.float32] else col
            )
            near_dup_mask = rounded.duplicated()
            near_dup_count_sample = int(near_dup_mask.sum())
            near_dup_count = int(near_dup_count_sample * (n_rows / sample_size))
            near_dup_frac = near_dup_count / n_rows
        except Exception:
            pass

    # ------------------------------------------------------------------
    # 3. Timestamp duplicate detection (within asset/group)
    #    A clean historian export has unique (timestamp, asset_id) pairs.
    #    Duplicate (timestamp, asset_id) = injected duplication artefact.
    # ------------------------------------------------------------------
    ts_col = _detect_timestamp_col_local(df, ctx)
    group_col = _detect_group_col(df)

    ts_dup_count = 0
    ts_dup_frac = 0.0
    ts_dup_detail = ""

    if ts_col and ts_col in df.columns:
        if group_col and group_col in df.columns:
            # Per-asset duplicate timestamps
            ts_dup_mask = df.duplicated(subset=[ts_col, group_col], keep=False)
            # Count non-first duplicates (same as how exact_count is measured)
            ts_dup_first = df.duplicated(subset=[ts_col, group_col], keep="first")
            ts_dup_count = int(ts_dup_first.sum())
            ts_dup_frac = ts_dup_count / n_rows
            if ts_dup_count > 0:
                ts_dup_detail = (
                    f" {ts_dup_count:,} duplicate timestamps within the same asset "
                    f"({ts_dup_frac*100:.1f}% of rows) — each (timestamp, {group_col}) pair "
                    "should be unique in a clean historian export."
                )
        else:
            # No group col: check globally
            ts_dup_first = df.duplicated(subset=[ts_col], keep="first")
            ts_dup_count = int(ts_dup_first.sum())
            ts_dup_frac = ts_dup_count / n_rows
            if ts_dup_count > 0:
                ts_dup_detail = (
                    f" {ts_dup_count:,} duplicate global timestamps "
                    f"({ts_dup_frac*100:.1f}% of rows)."
                )

    # ------------------------------------------------------------------
    # 4. Combined penalty and score
    # ------------------------------------------------------------------
    # Exact row dupes weighted heavily, timestamp dupes weighted similarly,
    # near-dupes lightly
    total_penalty = (
        exact_frac
        + ts_dup_frac          # timestamp dupes penalise equally to exact row dupes
        + 0.3 * max(0, near_dup_frac - exact_frac)
    )
    score = max(0.0, min(100.0, 100.0 * (1.0 - 4.0 * total_penalty)))

    # Severity
    combined_frac = max(exact_frac, ts_dup_frac)
    if combined_frac >= 0.1:
        severity = "critical"
    elif combined_frac >= 0.02 or near_dup_frac >= 0.1:
        severity = "warning"
    elif combined_frac > 0 or near_dup_frac > 0.02:
        severity = "info"
    else:
        severity = "ok"

    # First few duplicate rows for actionable feedback
    first_dupes: List[int] = []
    if exact_count > 0:
        dupe_indices = df[dupe_mask].index.tolist()[:5]
        first_dupes = [int(i) for i in dupe_indices]

    detail = f"{exact_count:,} exact duplicate rows ({exact_frac*100:.1f}% of dataset)."
    if near_dup_count > exact_count:
        detail += f" ~{near_dup_count:,} near-duplicate rows estimated (rounded numeric similarity)."
    if ts_dup_detail:
        detail += ts_dup_detail
    if first_dupes:
        detail += f" First exact duplicate indices: {first_dupes}."
    if exact_count == 0 and near_dup_count == 0 and ts_dup_count == 0:
        detail = "No exact, near-duplicate, or duplicate-timestamp rows detected."

    return {
        "score": round(score, 2),
        "detail": detail,
        "severity": severity,
        "raw": {
            "exact_count": exact_count,
            "exact_frac": round(exact_frac, 4),
            "near_dup_count": near_dup_count,
            "near_dup_frac": round(near_dup_frac, 4),
            "ts_dup_count": ts_dup_count,
            "ts_dup_frac": round(ts_dup_frac, 4),
            "first_dupe_indices": first_dupes,
        },
    }
