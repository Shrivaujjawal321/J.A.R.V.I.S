"""Temporal coverage: gap fraction + ADF stationarity test (time-series only).

Multi-asset aware: timestamps repeat across assets in historian exports.
We assess gap/regularity PER asset (grouping by asset_id / sequence_id / unit fallbacks),
then aggregate weighted by row count. This prevents a clean multi-asset dataset from
looking gappy because different assets ran at different calendar times.
"""

from __future__ import annotations
import pandas as pd
import numpy as np
from typing import Any, Dict, List, Optional, Tuple


def _detect_group_col(df: pd.DataFrame) -> Optional[str]:
    """
    Detect the column that identifies individual asset/unit timelines.
    Priority: asset_id > sequence_id > machine_id > unit_number > engine_id > unit.
    Falls back to None (treat whole dataset as single series).
    """
    candidates = [
        "asset_id", "sequence_id", "machine_id", "unit_number",
        "engine_id", "unit", "asset", "machine",
    ]
    col_lower = {c.lower(): c for c in df.columns}
    for cand in candidates:
        if cand in col_lower:
            return col_lower[cand]
    return None


def _per_asset_stats(
    df: pd.DataFrame,
    timestamp_col: str,
    group_col: Optional[str],
) -> Tuple[float, int, int]:
    """
    Compute weighted average gap_fraction and total large_gaps across all assets/groups.

    Key insight for multi-asset run-to-failure data:
      - Each asset runs in discrete episodes separated by days/weeks.
      - Between-episode calendar gaps are EXPECTED and must NOT count as missing data.
      - We split each asset's timeline into episodes using a 100× median gap threshold,
        then assess intra-episode coverage only.

    Returns (weighted_gap_fraction, total_large_gaps, n_groups).
    """
    ts_all = pd.to_datetime(df[timestamp_col], errors="coerce")

    if group_col is None:
        # Single-series: still apply episode-splitting so a clean file with a long
        # calendar gap between two runs isn't penalised
        ts_sorted = ts_all.dropna().sort_values().reset_index(drop=True)
        return _assess_episodes(ts_sorted, 1)

    groups = df[group_col].unique()
    total_rows = 0
    weighted_gf = 0.0
    total_large = 0
    n_groups = 0

    for grp_val in groups:
        mask = df[group_col] == grp_val
        ts_grp = ts_all[mask].dropna().sort_values().reset_index(drop=True)
        if len(ts_grp) < 3:
            continue

        gf, lg = _assess_episodes(ts_grp, len(ts_grp))
        n = len(ts_grp)
        weighted_gf += gf * n
        total_large += lg
        total_rows += n
        n_groups += 1

    if total_rows == 0:
        return 0.0, 0, 0

    return weighted_gf / total_rows, total_large, n_groups


def _assess_episodes(ts_sorted: pd.Series, n_rows: int) -> Tuple[float, int]:
    """
    Split a sorted timestamp series into episodes at gaps > 100× median interval,
    then measure intra-episode gap fraction and large gaps.

    Returns (gap_fraction, n_intra_large_gaps).
    """
    if len(ts_sorted) < 3:
        return 0.0, 0

    diffs = ts_sorted.diff().dropna()
    if len(diffs) == 0:
        return 0.0, 0

    med = diffs.median()
    if med.total_seconds() <= 0:
        return 0.5, 0  # zero-median = likely timestamp duplication issue

    # Between-episode threshold: 100× median
    between_ep_threshold = med * 100

    # Intra-episode diffs: gaps that are NOT between-episode calendar gaps
    intra_mask = diffs <= between_ep_threshold
    intra_diffs = diffs[intra_mask]

    if len(intra_diffs) == 0:
        return 0.0, 0

    # Large gaps WITHIN episodes (> 10× but <= 100× median)
    within_large = int(((diffs > med * 10) & intra_mask).sum())

    # Gap fraction from intra-episode perspective:
    # expected = sum of intra-episode intervals / median + 1 (for the first point of each ep)
    n_episodes = int((diffs > between_ep_threshold).sum()) + 1
    intra_expected = int(round(intra_diffs.sum() / med)) + n_episodes
    intra_actual = len(intra_diffs) + n_episodes  # = actual points in all episodes

    gf = max(0.0, 1.0 - intra_actual / max(intra_expected, 1))

    return gf, within_large


# ---------------------------------------------------------------------------
# Main compute function
# ---------------------------------------------------------------------------

def compute(
    df: pd.DataFrame,
    timestamp_col: str = None,
    dataset_type: str = "tabular",
    **ctx,
) -> Dict[str, Any]:
    """
    Multi-asset-aware temporal coverage scoring.

    Scores:
      - Gap fraction: intra-episode missing ticks, assessed PER ASSET, weighted by rows
      - ADF p-value: whether the data is stationary (p<0.05 = stationary, preferred for ML)
      - Combined score: 60% gap coverage + 40% stationarity
    """
    if dataset_type != "time_series" or timestamp_col is None:
        return {
            "score": 50.0,
            "detail": "Not a time-series dataset — temporal coverage check skipped.",
            "severity": "info",
            "raw": {"skipped": True},
        }

    if timestamp_col not in df.columns:
        return {
            "score": 30.0,
            "detail": f"Timestamp column '{timestamp_col}' not found in dataset.",
            "severity": "warning",
            "raw": {},
        }

    try:
        ts_check = pd.to_datetime(df[timestamp_col], errors="coerce")
    except Exception:
        return {
            "score": 30.0,
            "detail": f"Could not parse '{timestamp_col}' as datetime.",
            "severity": "warning",
            "raw": {},
        }

    n_valid = ts_check.notna().sum()
    if n_valid < 10:
        return {
            "score": 20.0,
            "detail": "Fewer than 10 valid timestamps — temporal analysis unreliable.",
            "severity": "warning",
            "raw": {},
        }

    # Detect grouping column
    group_col = _detect_group_col(df)

    # Compute per-asset stats
    gap_fraction, n_large_gaps, n_groups = _per_asset_stats(df, timestamp_col, group_col)

    # Coverage score
    coverage_score = max(0.0, min(100.0, 100.0 * (1.0 - 2.0 * gap_fraction)))

    # ADF stationarity on first numeric column (global — assesses signal properties)
    adf_score = 50.0
    adf_detail = ""
    adf_raw: Dict[str, Any] = {}
    try:
        from statsmodels.tsa.stattools import adfuller  # type: ignore

        num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        target_col = ctx.get("label_col")
        adf_cols = [c for c in num_cols if c != target_col and c != timestamp_col]

        if adf_cols:
            series = df[adf_cols[0]].dropna()
            series_clean = series.replace([np.inf, -np.inf], np.nan).dropna()
            if len(series_clean) >= 20:
                adf_result = adfuller(series_clean.iloc[:10_000], autolag="AIC")
                adf_pvalue = float(adf_result[1])
                adf_stat = float(adf_result[0])
                is_stationary = adf_pvalue < 0.05

                adf_score = 90.0 if is_stationary else 50.0
                adf_detail = (
                    f"ADF test on '{adf_cols[0]}': stat={adf_stat:.3f}, p={adf_pvalue:.4f} "
                    f"→ {'stationary' if is_stationary else 'non-stationary (may need differencing)'}."
                )
                adf_raw = {
                    "column": adf_cols[0],
                    "adf_stat": adf_stat,
                    "adf_pvalue": adf_pvalue,
                    "is_stationary": is_stationary,
                }

    except Exception as e:
        adf_detail = f"ADF test unavailable ({type(e).__name__})."

    # Combined score
    score = 0.60 * coverage_score + 0.40 * adf_score

    # Severity — based on per-asset intra-episode gap fraction
    if gap_fraction >= 0.30 or n_large_gaps > 10:
        severity = "critical"
    elif gap_fraction >= 0.10 or n_large_gaps > 3:
        severity = "warning"
    elif gap_fraction > 0.02 or n_large_gaps > 0:
        severity = "info"
    else:
        severity = "ok"

    ts_all = pd.to_datetime(df[timestamp_col], errors="coerce").dropna()
    ts_min = ts_all.min()
    ts_max = ts_all.max()
    global_span = ts_max - ts_min
    span_str = str(global_span).split(".")[0]

    group_str = f"grouped by '{group_col}' ({n_groups} asset(s))" if group_col else "single series"
    detail = (
        f"Time range: {ts_min} → {ts_max} (span: {span_str}). "
        f"Assessment: {group_str}. "
        f"Avg intra-episode gap fraction: {gap_fraction*100:.1f}% "
        f"({n_large_gaps} intra-episode large gap(s) > 10× median). "
    )
    if adf_detail:
        detail += adf_detail

    return {
        "score": round(score, 2),
        "detail": detail,
        "severity": severity,
        "raw": {
            "gap_fraction": round(gap_fraction, 4),
            "n_large_gaps": n_large_gaps,
            "n_groups": n_groups,
            "group_col": group_col,
            "adf": adf_raw,
        },
    }
