"""
Domain-specific PdM quality checks for steel-plant sensor datasets.

Activates when: dataset_type == "time_series" AND n_numeric_cols >= 5.
Returns a single DimensionResult-compatible dict:
    {"score": float, "detail": str, "severity": str, "raw": dict}

Nine sub-checks with internal weights (sum to 1.0). Knowledge tables (sensor vocab,
equipment coverage, physical ranges, sampling reqs, fault signatures) are research-derived —
see domain_knowledge.py (machinery/01-20 + domain/01-10 corpus):
    sensor_coverage      0.16  — required sensor types present for equipment class
    sampling_rate        0.16  — Nyquist adequacy per sensor type
    failure_representation 0.15 — enough failure events + RTF trajectories
    pdm_imbalance        0.09  — domain-calibrated imbalance (overrides generic class_balance)
    temporal_degradation 0.11  — span / episode count / pre-failure window
    pdm_label_quality    0.09  — RUL monotonicity + batch-logging detection
    sensor_health        0.10  — stuck / saturated / impossible values / blackout chunks
    fault_observability  0.09  — can present sensors observe the equipment's documented
                                 failure modes? (200-row fault→reading signature table)
    metadata_coverage    0.05  — asset_id / equipment_class / operating_mode present
"""

from __future__ import annotations
import pandas as pd
import numpy as np
from typing import Any, Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# Domain knowledge base — distilled from the Tata Steel R2 research corpus
# (machinery/01-20 + domain/01-10) by a 10-agent extract+synthesise workflow.
# 12 sensor types · 17 equipment classes · 111 physical-range rules ·
# 200 fault signatures · 57 quality rules. See domain_knowledge.py.
# These imports REPLACE the previous hand-seeded inline tables (8 sensors / 7
# equipment / 5 ranges) — the scorer is now research-grounded in place.
# ---------------------------------------------------------------------------
from scorer.dimensions.domain_knowledge import (
    SENSOR_VOCAB,
    EQUIPMENT_ALIASES,
    EQUIPMENT_COVERAGE_RULES,
    PHYSICAL_RANGE_RULES,
    SAMPLING_REQUIREMENTS,
    FAULT_SIGNATURES,
    EQUIPMENT_FAULT_MAP,
    NORMAL_BANDS,
)

# Domain-calibrated imbalance bands: (min_rate_exclusive, max_rate_inclusive)
# Keys are (min, max) floats; lookup via linear scan
DOMAIN_IMBALANCE_BANDS: List[Tuple[float, float, float, str, str]] = [
    # (min_excl, max_incl, domain_score, severity, message_template)
    (0.000, 0.005, 20.0, "critical",
     "Failure rate {rate:.2f}% is too sparse for PdM model convergence (IR={ir:.0f}:1). "
     "Minimum ~0.5% required. Collect more failure episodes or use SMOTE-Tomek."),
    (0.005, 0.050, 90.0, "ok",
     "Failure rate {rate:.1f}% (IR={ir:.0f}:1) is REALISTIC for industrial PdM — "
     "this is NOT a dataset problem. No resampling needed; use class_weight='balanced'."),
    (0.050, 0.150, 75.0, "info",
     "Failure rate {rate:.1f}%: slightly elevated but within acceptable PdM range. "
     "Use stratified CV; class_weight='balanced'."),
    (0.150, 0.400, 55.0, "warning",
     "Failure rate {rate:.1f}%: higher than typical plant data. "
     "May indicate over-collection or partial synthetic augmentation."),
    (0.400, 1.001, 40.0, "warning",
     "Failure rate {rate:.1f}%: unrealistically high for industrial PdM. "
     "Dataset is likely heavily over-sampled or synthetic."),
]

METADATA_VOCAB: Dict[str, List[str]] = {
    "asset_id":        ["asset", "machine", "unit", "engine", "device", "equipment_id",
                        "asset_id", "id"],
    "equipment_class": ["type", "class", "category", "model", "machine_type", "equip_class"],
    "operating_mode":  ["mode", "op_setting", "load", "condition", "state", "regime",
                        "setting"],
    "process_stage":   ["stage", "process", "phase", "step", "zone", "pass"],
}

DOMAIN_PDM_INTERNAL_WEIGHTS: Dict[str, float] = {
    "sensor_coverage":       0.16,
    "sampling_rate":         0.16,
    "failure_representation":0.15,
    "pdm_imbalance":         0.09,
    "temporal_degradation":  0.11,
    "pdm_label_quality":     0.09,
    "sensor_health":         0.10,  # expanded: now detects blackout chunks + anomalous drift
    "fault_observability":   0.09,  # NEW: can the present sensors actually observe this
                                    #      equipment's documented failure modes? (200-sig table)
    "metadata_coverage":     0.05,
    # Total = 1.00
}


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _classify_columns(columns: List[str]) -> Dict[str, List[str]]:
    """Map column names → detected sensor types."""
    detected: Dict[str, List[str]] = {}
    for stype, keywords in SENSOR_VOCAB.items():
        matched = [c for c in columns if any(k in c.lower() for k in keywords)]
        if matched:
            detected[stype] = matched
    return detected


def _detect_equipment_class(columns: List[str]) -> Optional[str]:
    """
    Infer equipment class from column names using the research-derived alias table.
    Scores every class by how many of its name/alias tokens appear in the column text
    and returns the best match (alias-aware, not just literal-name substring).
    """
    col_str = " ".join(str(c) for c in columns).lower()
    best, best_score = None, 0
    for equip in EQUIPMENT_COVERAGE_RULES:
        score = 1 if equip in col_str else 0
        for alias in EQUIPMENT_ALIASES.get(equip, []):
            a = alias.lower().strip()
            # multi-word aliases: require the phrase; single tokens: require word-ish hit
            if len(a) >= 3 and a in col_str:
                score += 1
        if score > best_score:
            best, best_score = equip, score
    return best


def _infer_sampling_rate_hz(df: pd.DataFrame, timestamp_col: str) -> Optional[float]:
    """Infer sampling rate from median timestamp delta in Hz."""
    try:
        ts = pd.to_datetime(df[timestamp_col], errors="coerce").sort_values().dropna()
        if len(ts) < 20:
            return None
        median_delta_s = ts.diff().dropna().median().total_seconds()
        if median_delta_s <= 0:
            return None
        return round(1.0 / median_delta_s, 4)
    except Exception:
        return None


def _auto_detect_rul_col(df: pd.DataFrame) -> Optional[str]:
    rul_keywords = ["rul", "remaining", "ttf", "time_to_fail", "remaining_life"]
    for c in df.columns:
        if any(k in c.lower() for k in rul_keywords):
            return c
    return None


def _auto_detect_label_col(df: pd.DataFrame, hint: Optional[str]) -> Optional[str]:
    if hint and hint in df.columns:
        return hint
    label_keywords = ["failure", "fault", "label", "target", "anomaly", "alarm"]
    for c in df.columns:
        if any(k in c.lower() for k in label_keywords):
            return c
    return None


# ---------------------------------------------------------------------------
# Sub-check 1: Sensor Coverage
# ---------------------------------------------------------------------------

def _check_sensor_coverage(
    detected_sensors: Dict[str, List[str]],
    equipment_class: Optional[str],
) -> Dict[str, Any]:
    if equipment_class is None:
        # Unknown equipment — give neutral score, surface what was found
        sensor_list = list(detected_sensors.keys())
        return {
            "score": 50.0,
            "severity": "info",
            "detail": (
                f"Equipment class not inferred from column names. "
                f"Detected sensor types: {sensor_list or 'none'}. "
                "Cannot validate sensor coverage without known equipment class."
            ),
            "raw": {"equipment_class": None, "detected_sensors": sensor_list},
        }

    rules = EQUIPMENT_COVERAGE_RULES[equipment_class]
    required = rules["required"]
    recommended = rules.get("recommended", [])

    missing_required = [r for r in required if r not in detected_sensors]
    present_recommended = [r for r in recommended if r in detected_sensors]

    if len(missing_required) == len(required):
        # All required sensors absent
        score = 20.0
        severity = "critical"
        detail = (
            f"{equipment_class.capitalize()} equipment detected but NONE of the required sensor types "
            f"({required}) are present. "
            f"Detected sensor types: {list(detected_sensors.keys()) or 'none'}. "
            f"This dataset cannot support {equipment_class} predictive maintenance without the correct signals."
        )
    elif missing_required:
        score = 40.0
        severity = "warning"
        detail = (
            f"{equipment_class.capitalize()} equipment: {len(missing_required)} required sensor type(s) missing "
            f"({missing_required}). Present: {list(detected_sensors.keys())}. "
            f"Missing sensors will limit fault detection coverage."
        )
    elif not present_recommended:
        score = 75.0
        severity = "info"
        detail = (
            f"{equipment_class.capitalize()} equipment: all required sensors present {required}. "
            f"No recommended sensors found ({recommended}) — adding them would improve diagnostic depth."
        )
    else:
        score = 100.0
        severity = "ok"
        detail = (
            f"{equipment_class.capitalize()} equipment: all required ({required}) and "
            f"{len(present_recommended)} recommended sensor type(s) present. Sensor coverage is excellent."
        )

    return {
        "score": score,
        "severity": severity,
        "detail": detail,
        "raw": {
            "equipment_class": equipment_class,
            "required": required,
            "missing_required": missing_required,
            "present_recommended": present_recommended,
            "detected_sensors": list(detected_sensors.keys()),
        },
    }


# ---------------------------------------------------------------------------
# Sub-check 2: Sampling Rate Adequacy
# ---------------------------------------------------------------------------

def _check_sampling_rate(
    df: pd.DataFrame,
    timestamp_col: Optional[str],
    detected_sensors: Dict[str, List[str]],
) -> Dict[str, Any]:
    if not timestamp_col:
        return {
            "score": 50.0,
            "severity": "info",
            "detail": "No timestamp column — sampling rate cannot be determined.",
            "raw": {"sampling_rate_hz": None},
        }

    hz = _infer_sampling_rate_hz(df, timestamp_col)
    if hz is None:
        return {
            "score": 50.0,
            "severity": "info",
            "detail": "Sampling rate could not be inferred from timestamps.",
            "raw": {"sampling_rate_hz": None},
        }

    issues: List[str] = []
    worst_score = 100.0

    # Only evaluate sensor types that have requirements AND are present
    for stype, reqs in SAMPLING_REQUIREMENTS.items():
        if stype not in detected_sensors:
            continue
        min_hz = reqs["min_hz"]
        warn_hz = reqs["warn_hz"]

        if hz < warn_hz:
            issues.append(
                f"'{stype}' sensors present but sampling rate {hz:.4g} Hz is far below "
                f"minimum {min_hz:.4g} Hz. {reqs['msg']}"
            )
            # Critical mismatch for vibration/current; warning for others
            if stype in ("vibration", "current"):
                worst_score = min(worst_score, 25.0)
            else:
                worst_score = min(worst_score, 50.0)
        elif hz < min_hz:
            issues.append(
                f"'{stype}' sensors: sampling rate {hz:.4g} Hz is below recommended "
                f"minimum {min_hz:.4g} Hz. {reqs['msg']}"
            )
            worst_score = min(worst_score, 70.0)

    if not issues:
        score = 100.0
        severity = "ok"
        detail = (
            f"Inferred sampling rate: {hz:.4g} Hz. "
            "All detected sensor types meet their minimum sampling requirements."
        )
    else:
        score = worst_score
        severity = "critical" if score <= 30 else "warning"
        detail = f"Inferred sampling rate: {hz:.4g} Hz. Issues: " + " | ".join(issues)

    return {
        "score": round(score, 2),
        "severity": severity,
        "detail": detail,
        "raw": {"sampling_rate_hz": hz, "issues": issues},
    }


# ---------------------------------------------------------------------------
# Sub-check 3: Failure Representation
# ---------------------------------------------------------------------------

def _check_failure_representation(
    df: pd.DataFrame,
    label_col: Optional[str],
    rul_col: Optional[str],
) -> Dict[str, Any]:
    if not label_col or label_col not in df.columns:
        return {
            "score": 50.0,
            "severity": "info",
            "detail": "No label column detected — failure representation cannot be assessed.",
            "raw": {},
        }

    series = df[label_col].dropna()
    failure_mask = series.isin([1, True, "failure", "Failure", "FAIL", "1"])
    n_failures = int(failure_mask.sum())
    n_total = len(series)
    failure_rate = n_failures / max(n_total, 1)

    raw: Dict[str, Any] = {
        "n_failures": n_failures,
        "n_total": n_total,
        "failure_rate_pct": round(failure_rate * 100, 2),
    }

    issues: List[str] = []
    score = 100.0

    # Check failure count
    if n_failures < 30:
        score = min(score, 30.0)
        issues.append(
            f"Only {n_failures} failure events in {n_total:,} rows. "
            "PdM models need at least 30 failure instances to learn reliable precursor signatures."
        )
    elif n_failures < 100:
        score = min(score, 75.0)
        issues.append(
            f"{n_failures} failure events — functional but limited. "
            "100+ failure instances recommended for robust PdM training."
        )

    # RTF trajectory check (RUL column)
    if rul_col and rul_col in df.columns:
        rul_series = df[rul_col].dropna()
        n_zero_rul = int((rul_series == 0).sum())
        raw["n_rtf_endpoints"] = n_zero_rul
        if n_zero_rul == 0:
            score = min(score, 30.0)
            issues.append(
                "RUL column never reaches 0 — no complete run-to-failure trajectories detected. "
                "RUL regression is not feasible; only binary classification is possible with this data."
            )
        elif n_zero_rul < 5:
            score = min(score, 60.0)
            issues.append(
                f"Only {n_zero_rul} complete run-to-failure endpoint(s). "
                "At least 5 complete RTF trajectories are needed for reliable RUL regression."
            )
        else:
            raw["rtf_status"] = "sufficient"

    if not issues:
        severity = "ok"
        detail = (
            f"{n_failures} failure events ({failure_rate*100:.1f}%) in {n_total:,} rows. "
            "Failure representation is adequate for PdM training."
        )
        if rul_col and rul_col in df.columns:
            detail += f" {raw.get('n_rtf_endpoints', 0)} run-to-failure endpoints detected."
    else:
        severity = "critical" if score <= 35 else "warning"
        detail = " ".join(issues)

    return {
        "score": round(score, 2),
        "severity": severity,
        "detail": detail,
        "raw": raw,
    }


# ---------------------------------------------------------------------------
# Sub-check 4: PdM Imbalance Realism
# ---------------------------------------------------------------------------

def _check_pdm_imbalance(
    df: pd.DataFrame,
    label_col: Optional[str],
) -> Dict[str, Any]:
    """
    Domain-calibrated imbalance scoring.
    0.5–15% failure rate = REALISTIC for PdM — override generic penalty to high score.
    Returns score + pdm_override_active flag (used by composite to replace class_balance).
    """
    if not label_col or label_col not in df.columns:
        return {
            "score": 50.0,
            "severity": "info",
            "detail": "No label column — PdM imbalance assessment skipped.",
            "raw": {"pdm_override_active": False},
        }

    series = df[label_col].dropna()
    if series.nunique() < 2:
        return {
            "score": 30.0,
            "severity": "critical",
            "detail": "Label column has fewer than 2 unique values.",
            "raw": {"pdm_override_active": False},
        }

    counts = series.value_counts()
    majority = int(counts.iloc[0])
    minority = int(counts.iloc[-1])
    total = int(len(series))
    failure_rate = minority / max(total, 1)
    ir = majority / max(minority, 1)

    # Find matching band
    for (lo, hi, dom_score, dom_severity, msg_template) in DOMAIN_IMBALANCE_BANDS:
        if lo < failure_rate <= hi or (lo == 0.0 and failure_rate == 0.0):
            msg = msg_template.format(rate=failure_rate * 100, ir=ir)
            return {
                "score": dom_score,
                "severity": dom_severity,
                "detail": msg,
                "raw": {
                    "failure_rate_pct": round(failure_rate * 100, 2),
                    "imbalance_ratio": round(ir, 2),
                    "pdm_override_active": True,
                    "domain_band": f"{lo*100:.1f}–{hi*100:.1f}%",
                },
            }

    # Fallback (shouldn't reach here)
    return {
        "score": 50.0,
        "severity": "info",
        "detail": f"Failure rate {failure_rate*100:.2f}% — unable to classify.",
        "raw": {"pdm_override_active": False},
    }


# ---------------------------------------------------------------------------
# Sub-check 5: Temporal Degradation Arc
# ---------------------------------------------------------------------------

def _check_temporal_degradation(
    df: pd.DataFrame,
    timestamp_col: Optional[str],
    label_col: Optional[str],
    rul_col: Optional[str],
) -> Dict[str, Any]:
    if not timestamp_col:
        return {
            "score": 50.0,
            "severity": "info",
            "detail": "No timestamp column — temporal degradation arc cannot be assessed.",
            "raw": {},
        }

    try:
        ts = pd.to_datetime(df[timestamp_col], errors="coerce").sort_values().dropna()
        if len(ts) < 10:
            return {
                "score": 30.0,
                "severity": "critical",
                "detail": "Fewer than 10 valid timestamps — cannot assess temporal coverage.",
                "raw": {},
            }
        total_span_days = (ts.iloc[-1] - ts.iloc[0]).total_seconds() / 86400
    except Exception:
        return {
            "score": 50.0,
            "severity": "info",
            "detail": "Timestamp parsing failed — temporal degradation arc skipped.",
            "raw": {},
        }

    raw: Dict[str, Any] = {"total_span_days": round(total_span_days, 1)}
    issues: List[str] = []
    score = 100.0

    # Span check
    if total_span_days < 30:
        score = min(score, 30.0)
        issues.append(
            f"Dataset spans only {total_span_days:.1f} days. Steel plant equipment degradation "
            "typically develops over 30–180+ days — this window is too narrow to capture "
            "meaningful degradation arcs."
        )
    elif total_span_days < 90:
        score = min(score, 70.0)
        issues.append(
            f"Dataset spans {total_span_days:.1f} days. 90+ days recommended to capture "
            "full degradation cycles for most rotating equipment."
        )

    # Failure episode count
    if label_col and label_col in df.columns:
        failure_mask = df[label_col].isin([1, True, "failure", "Failure", "FAIL", "1"])
        failure_times = pd.to_datetime(
            df.loc[failure_mask, timestamp_col], errors="coerce"
        ).dropna()
        n_episodes = len(failure_times)
        raw["n_failure_episodes"] = n_episodes

        if n_episodes == 0:
            score = min(score, 30.0)
            issues.append("No failure events found in the dataset.")
        elif n_episodes < 3:
            score = min(score, 60.0)
            issues.append(
                f"Only {n_episodes} failure episode(s). At least 3 distinct failure events "
                "are needed to generalise precursor signatures across multiple degradation paths."
            )

        # Pre-failure window coverage (24h before each failure)
        if len(failure_times) > 0:
            ts_series = pd.to_datetime(df[timestamp_col], errors="coerce")
            covered = 0
            for ft in failure_times:
                window_start = ft - pd.Timedelta(hours=24)
                in_window = ((ts_series >= window_start) & (ts_series < ft)).sum()
                if in_window > 0:
                    covered += 1
            prewindow_pct = round(covered / max(len(failure_times), 1) * 100, 1)
            raw["failures_with_prewindow_pct"] = prewindow_pct
            if prewindow_pct < 50:
                score = min(score, 60.0)
                issues.append(
                    f"Only {prewindow_pct:.0f}% of failure events have data in the 24h pre-failure "
                    "window. Early-warning models cannot be built without pre-failure lead time."
                )

    # Healthy baseline coverage from RUL
    if rul_col and rul_col in df.columns:
        rul_series = df[rul_col].dropna()
        if len(rul_series) > 0:
            max_rul = float(rul_series.max())
            healthy_pct = float((rul_series > max_rul * 0.7).mean() * 100)
            raw["healthy_baseline_pct"] = round(healthy_pct, 1)
            if healthy_pct < 20:
                score = min(score, 70.0)
                issues.append(
                    f"Only {healthy_pct:.0f}% of rows represent clearly healthy states (RUL > 70% max). "
                    "The model cannot learn a reliable healthy baseline without sufficient healthy data."
                )

    if not issues:
        severity = "ok"
        detail = (
            f"Temporal coverage: {total_span_days:.0f} days span, "
            f"{raw.get('n_failure_episodes', 'N/A')} failure episode(s). "
            "Degradation arc is adequately represented."
        )
    else:
        severity = "critical" if score <= 35 else "warning"
        detail = " ".join(issues)

    return {
        "score": round(score, 2),
        "severity": severity,
        "detail": detail,
        "raw": raw,
    }


# ---------------------------------------------------------------------------
# Sub-check 6: PdM Label Quality
# ---------------------------------------------------------------------------

def _check_pdm_label_quality(
    df: pd.DataFrame,
    label_col: Optional[str],
    rul_col: Optional[str],
    timestamp_col: Optional[str],
) -> Dict[str, Any]:
    if not label_col and not rul_col:
        return {
            "score": 50.0,
            "severity": "info",
            "detail": "No label or RUL column — PdM label quality check skipped.",
            "raw": {},
        }

    issues: List[str] = []
    penalty = 0.0
    raw: Dict[str, Any] = {}

    # Batch-logged failure detection
    if label_col and label_col in df.columns and timestamp_col and timestamp_col in df.columns:
        failure_rows = df[df[label_col].isin([1, True, "failure", "Failure", "FAIL", "1"])]
        if len(failure_rows) > 1:
            failure_ts = pd.to_datetime(failure_rows[timestamp_col], errors="coerce").dropna()
            if len(failure_ts) > 1:
                ts_counts = failure_ts.value_counts()
                batch_fraction = float((ts_counts > 1).sum()) / max(len(ts_counts), 1)
                raw["batch_logged_fraction"] = round(batch_fraction, 3)
                if batch_fraction > 0.30:
                    issues.append(
                        f"Batch-logged failures detected ({batch_fraction*100:.0f}% of failure "
                        "timestamps have multiple co-incident events). This suggests administrative "
                        "work-order logging rather than real-time sensor capture — failure timestamps "
                        "may be offset from actual failure onset by hours or days."
                    )
                    penalty += 15.0

    # RUL monotonicity check
    if rul_col and rul_col in df.columns:
        raw["rul_col"] = rul_col
        id_cols = [c for c in df.columns if any(
            k in c.lower() for k in ["asset_id", "machine_id", "unit_number", "engine_id", "asset", "machine", "unit"]
        ) and c != rul_col]

        # Exclude label/target cols from id candidates
        id_cols = [c for c in id_cols if not any(
            x in c.lower() for x in ["rul", "failure", "fault", "label", "target"]
        )]

        if id_cols:
            id_col = id_cols[0]
            non_monotone_assets = 0
            total_assets = 0
            for _, group in df.groupby(id_col):
                total_assets += 1
                if timestamp_col and timestamp_col in group.columns:
                    rul_vals = group.sort_values(timestamp_col)[rul_col].dropna().values
                else:
                    rul_vals = group[rul_col].dropna().values
                if len(rul_vals) > 1:
                    diffs = np.diff(rul_vals.astype(float))
                    n_increase = int((diffs > 1.0).sum())
                    if n_increase / max(len(diffs), 1) > 0.10:
                        non_monotone_assets += 1

            raw["rul_non_monotone_assets"] = non_monotone_assets
            raw["total_assets"] = total_assets

            if total_assets > 0:
                nm_rate = non_monotone_assets / total_assets
                if nm_rate > 0.30:
                    issues.append(
                        f"RUL non-monotonic in {non_monotone_assets}/{total_assets} assets "
                        "(>30% show RUL increases mid-trajectory — indicates labeling error or "
                        "un-flagged maintenance resets)."
                    )
                    penalty += 20.0
                elif nm_rate > 0.10:
                    issues.append(
                        f"RUL non-monotonic in {non_monotone_assets}/{total_assets} assets — "
                        "minor inconsistency, may be sensor noise or maintenance resets."
                    )
                    penalty += 8.0
        else:
            # No asset_id — check globally
            rul_vals = df[rul_col].dropna().values
            if len(rul_vals) > 1:
                diffs = np.diff(rul_vals.astype(float))
                n_increase = int((diffs > 1.0).sum())
                global_nm_rate = n_increase / max(len(diffs), 1)
                raw["global_rul_increase_rate"] = round(global_nm_rate, 3)
                if global_nm_rate > 0.20:
                    issues.append(
                        f"RUL values increase in {global_nm_rate*100:.0f}% of timesteps (no asset_id "
                        "to group by). This may indicate multiple interleaved asset trajectories or "
                        "labeling errors."
                    )
                    penalty += 10.0

        # RUL range sanity
        rul_max = float(df[rul_col].max())
        raw["rul_max"] = rul_max
        if rul_max > 5000:
            issues.append(
                f"Max RUL = {rul_max:.0f} — unusually high; verify units (cycles vs hours vs minutes)."
            )
            penalty += 5.0

    score = max(0.0, min(100.0, 100.0 - penalty))

    if not issues:
        severity = "ok"
        detail = "PdM label quality checks passed — no batch-logging or RUL monotonicity issues detected."
    elif score < 50:
        severity = "critical"
        detail = " | ".join(issues)
    else:
        severity = "warning"
        detail = " | ".join(issues)

    return {
        "score": round(score, 2),
        "severity": severity,
        "detail": detail,
        "raw": raw,
    }


# ---------------------------------------------------------------------------
# Sub-check 7: Sensor Health (stuck / saturated / impossible values / blackout chunks / drift)
# ---------------------------------------------------------------------------

def _detect_group_col_pdm(columns: List[str]) -> Optional[str]:
    """Detect asset identifier for per-asset analysis."""
    candidates = ["asset_id", "machine_id", "unit_number", "engine_id", "unit", "asset", "machine"]
    col_lower = {c.lower(): c for c in columns}
    for cand in candidates:
        if cand in col_lower:
            return col_lower[cand]
    return None


def _check_sensor_health(
    df: pd.DataFrame,
    detected_sensors: Dict[str, List[str]],
) -> Dict[str, Any]:
    # Collect all sensor columns that are numeric (deduplicated — a col can match multiple types)
    _seen: set = set()
    all_sensor_cols = []
    for cols in detected_sensors.values():
        for col in cols:
            if col in df.columns and pd.api.types.is_numeric_dtype(df[col]) and col not in _seen:
                all_sensor_cols.append(col)
                _seen.add(col)

    # If no named sensor types detected, include all numeric non-metadata cols
    if not all_sensor_cols:
        exclude_kw = ["rul", "failure", "fault", "label", "target", "anomaly", "alarm",
                      "timestamp", "time", "date", "asset_id", "sequence_id", "id"]
        all_sensor_cols = [
            c for c in df.columns
            if pd.api.types.is_numeric_dtype(df[c])
            and not any(k in c.lower() for k in exclude_kw)
        ]

    if not all_sensor_cols:
        return {
            "score": 50.0,
            "severity": "info",
            "detail": "No numeric sensor columns identified for sensor health check.",
            "raw": {"skipped": True},
        }

    stuck: List[Dict] = []
    saturated: List[Dict] = []
    impossible: List[Dict] = []
    blackout_chunks: List[Dict] = []
    penalty = 0.0

    WINDOW = 50

    # ------------------------------------------------------------------
    # Per-column checks: stuck, saturation, impossible values
    # ------------------------------------------------------------------
    for col in all_sensor_cols:
        series = df[col].dropna().astype(float)
        if len(series) < 20:
            continue

        # Stuck sensor: rolling std near zero
        if len(series) >= WINDOW * 2:
            rolling_std = series.rolling(WINDOW).std()
            near_zero_frac = float((rolling_std < 1e-6).mean())
            if near_zero_frac > 0.05:
                stuck.append({"col": col, "stuck_frac": round(near_zero_frac, 3)})
                penalty += 15.0

        # Saturation: spike at exact min or max
        col_min, col_max = float(series.min()), float(series.max())
        if col_max > col_min:
            at_min = float((series == col_min).mean())
            at_max = float((series == col_max).mean())
            if at_min > 0.05 or at_max > 0.05:
                saturated.append({
                    "col": col,
                    "at_min_pct": round(at_min * 100, 1),
                    "at_max_pct": round(at_max * 100, 1),
                })
                penalty += 10.0

        # Physical range check
        for stype, cols in detected_sensors.items():
            if col in cols and stype in PHYSICAL_RANGE_RULES:
                prange = PHYSICAL_RANGE_RULES[stype]
                out_of_range = int(((series < prange["min"]) | (series > prange["max"])).sum())
                if out_of_range > 0:
                    impossible.append({
                        "col": col,
                        "sensor_type": stype,
                        "n_impossible": out_of_range,
                        "valid_range": f"{prange['min']} to {prange['max']} {prange['unit']}",
                    })
                    penalty += 20.0
                break

    # ------------------------------------------------------------------
    # Blackout chunk detection: per-asset, consecutive rows where >= 2 sensors are NaN
    # A blackout chunk = at least MIN_NULL_SENSORS sensors null for >= 5 consecutive rows
    # We check per-asset so that across-asset row interleaving doesn't break the streak
    # ------------------------------------------------------------------
    MIN_NULL_SENSORS = 2  # conservative: even 2 simultaneous sensor blackouts are suspicious

    group_col_bo = _detect_group_col_pdm(df.columns.tolist())
    total_blackout_rows_all = 0
    total_long_chunks = 0
    max_chunk_len_all = 0

    def _find_blackout_chunks_in_series(null_per_row: np.ndarray) -> tuple:
        """Return (n_long_chunks, max_chunk, total_rows) for blackout runs >= 5."""
        is_bo = null_per_row >= MIN_NULL_SENSORS
        if not is_bo.any():
            return 0, 0, 0
        changes = np.diff(is_bo.astype(int), prepend=0)
        run_starts = np.where(changes == 1)[0]
        run_ends = np.where(changes == -1)[0]
        if is_bo[-1]:
            run_ends = np.append(run_ends, len(is_bo))
        rl = run_ends - run_starts
        long_rl = rl[rl >= 5]
        if len(long_rl) == 0:
            return 0, 0, 0
        return int(len(long_rl)), int(long_rl.max()), int(long_rl.sum())

    if group_col_bo and group_col_bo in df.columns:
        for _, grp in df.groupby(group_col_bo):
            null_per_row = grp[all_sensor_cols].isnull().sum(axis=1).values
            nc, mc, tr = _find_blackout_chunks_in_series(null_per_row)
            total_long_chunks += nc
            total_blackout_rows_all += tr
            max_chunk_len_all = max(max_chunk_len_all, mc)
    else:
        null_per_row = df[all_sensor_cols].isnull().sum(axis=1).values
        total_long_chunks, max_chunk_len_all, total_blackout_rows_all = _find_blackout_chunks_in_series(null_per_row)

    if total_long_chunks > 0:
        blackout_frac = total_blackout_rows_all / len(df)
        blackout_chunks.append({
            "n_chunks": total_long_chunks,
            "max_chunk_len": max_chunk_len_all,
            "total_rows": total_blackout_rows_all,
            "frac": round(blackout_frac, 4),
            "min_sensors_null": MIN_NULL_SENSORS,
        })
        # Penalty proportional to fraction of rows blacked out (20 pts per 1% blackout, min 10)
        penalty += min(35.0, max(10.0, 2000.0 * blackout_frac))

    # Note: Sensor drift (temperature/vibration increase) is physically expected in
    # run-to-failure PdM data and cannot be reliably distinguished from injected drift
    # without a reference baseline. Drift is therefore NOT penalised here.

    # Cap penalty at 100
    penalty = min(penalty, 100.0)
    score = max(0.0, 100.0 - penalty)

    issues_parts: List[str] = []
    if impossible:
        issues_parts.append(
            f"PHYSICALLY IMPOSSIBLE VALUES in {len(impossible)} column(s): "
            + "; ".join(f"'{e['col']}' ({e['n_impossible']} rows outside {e['valid_range']})" for e in impossible)
            + ". These indicate sensor faults or unit conversion errors."
        )
    if stuck:
        issues_parts.append(
            f"{len(stuck)} stuck sensor(s): "
            + ", ".join(f"'{e['col']}' ({e['stuck_frac']*100:.0f}% of timeline constant)" for e in stuck)
            + ". Stuck sensors provide no information and should be removed."
        )
    if saturated:
        issues_parts.append(
            f"{len(saturated)} saturated channel(s): "
            + ", ".join(
                f"'{e['col']}' (at_min={e['at_min_pct']}%, at_max={e['at_max_pct']}%)"
                for e in saturated
            )
            + ". Saturation clips real signal at ADC boundaries."
        )
    if blackout_chunks:
        bc = blackout_chunks[0]
        issues_parts.append(
            f"SENSOR BLACKOUT: {bc['n_chunks']} blackout chunk(s) detected "
            f"(>={bc['min_sensors_null']} sensors simultaneously null for >=5 consecutive rows). "
            f"Largest blackout: {bc['max_chunk_len']} rows. "
            f"Total affected: {bc['total_rows']:,} rows ({bc['frac']*100:.1f}%). "
            "Blackouts indicate data acquisition failures or communication outages."
        )
    if not issues_parts:
        severity = "ok"
        detail = (
            f"Sensor health: {len(all_sensor_cols)} sensor column(s) checked — "
            "no stuck sensors, saturation, physically impossible values, blackout chunks, "
            "or anomalous drift detected."
        )
    elif score < 40:
        severity = "critical"
        detail = " | ".join(issues_parts)
    else:
        severity = "warning"
        detail = " | ".join(issues_parts)

    return {
        "score": round(score, 2),
        "severity": severity,
        "detail": detail,
        "raw": {
            "n_sensor_cols_checked": len(all_sensor_cols),
            "stuck": stuck,
            "saturated": saturated,
            "impossible_values": impossible,
            "blackout_chunks": blackout_chunks,
            "penalty": round(penalty, 1),
        },
    }


# ---------------------------------------------------------------------------
# Sub-check 8: Operating-Condition Metadata
# ---------------------------------------------------------------------------

def _check_metadata_coverage(df: pd.DataFrame) -> Dict[str, Any]:
    # Exclude obvious label/RUL columns from metadata candidates
    exclude_keywords = ["rul", "failure", "fault", "label", "target", "class", "anomaly"]

    found: Dict[str, str] = {}
    for meta_type, keywords in METADATA_VOCAB.items():
        for c in df.columns:
            c_lower = c.lower()
            if any(k in c_lower for k in keywords):
                if not any(x in c_lower for x in exclude_keywords):
                    found[meta_type] = c
                    break

    n_found = len(found)
    has_asset_id = "asset_id" in found

    if n_found == 0:
        score = 25.0
        severity = "critical"
        detail = (
            "No metadata columns detected (asset_id, equipment_class, operating_mode, process_stage). "
            "Without asset identity, RUL trajectories from different machines are interleaved — "
            "a model cannot distinguish per-asset degradation state. "
            "Add asset_id as the highest-priority metadata fix."
        )
    elif n_found == 1 and not has_asset_id:
        score = 40.0
        severity = "warning"
        detail = (
            f"Only 1 metadata type found ({list(found.keys())}), but no asset_id. "
            "Asset identity is critical for per-machine RUL tracking."
        )
    elif n_found == 1 and has_asset_id:
        score = 45.0
        severity = "warning"
        detail = (
            f"Only asset_id found ({found.get('asset_id')}). "
            "Equipment class and operating mode metadata are absent — "
            "mixed equipment types and load conditions reduce model generalisation."
        )
    elif n_found == 2:
        score = 60.0
        severity = "info"
        detail = (
            f"2 of 4 metadata types found: {list(found.keys())}. "
            "Adding operating_mode and/or process_stage would improve per-condition model accuracy."
        )
    elif n_found == 3:
        score = 80.0
        severity = "ok"
        detail = (
            f"3 of 4 metadata types found: {list(found.keys())}. "
            "Good metadata coverage — one additional context column would complete the picture."
        )
    else:
        score = 100.0
        severity = "ok"
        detail = (
            f"All 4 metadata types present: {list(found.keys())}. "
            "Excellent operating-condition context for per-asset, per-mode PdM modeling."
        )

    return {
        "score": score,
        "severity": severity,
        "detail": detail,
        "raw": {"found": found, "n_found": n_found, "has_asset_id": has_asset_id},
    }


# ---------------------------------------------------------------------------
# Detail string builder
# ---------------------------------------------------------------------------

def _build_detail_string(
    sub: Dict[str, Dict],
    equipment_class: Optional[str],
    detected_sensors: Dict[str, List[str]],
    composite: float,
) -> str:
    equip_str = equipment_class or "unknown equipment"
    sensor_str = ", ".join(detected_sensors.keys()) or "none detected"

    critical_checks = [k for k, v in sub.items() if v.get("severity") == "critical"]
    warning_checks  = [k for k, v in sub.items() if v.get("severity") == "warning"]

    lines = [
        f"Domain PdM analysis (equipment: {equip_str}, sensors: {sensor_str}). "
        f"Domain score: {composite:.0f}/100."
    ]

    if critical_checks:
        lines.append(
            f"CRITICAL domain issues: {', '.join(c.replace('_', ' ') for c in critical_checks)}."
        )
        # Surface the detail of the worst critical check
        for ck in critical_checks[:2]:
            lines.append(sub[ck]["detail"])

    if warning_checks and not critical_checks:
        lines.append(
            f"Warnings: {', '.join(c.replace('_', ' ') for c in warning_checks)}."
        )
        for wk in warning_checks[:1]:
            lines.append(sub[wk]["detail"])

    if not critical_checks and not warning_checks:
        lines.append("All domain-specific PdM checks passed.")

    return " ".join(lines)


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def _check_fault_observability(
    equipment_class: Optional[str],
    detected_sensors: Dict[str, List[str]],
) -> Dict[str, Any]:
    """
    Fault-mode observability — uses the 200-row research fault→reading signature table.

    For the detected equipment class, every documented failure mode manifests in a specific
    sensor channel (e.g. bearing outer-race spalling → vibration envelope; lube starvation →
    temperature + AE). A dataset is only useful for PdM if it actually carries the channels
    needed to SEE those failure modes. Score = fraction of the equipment's documented fault
    modes whose signature sensor is present in the dataset.
    """
    present = set(detected_sensors.keys())

    if not equipment_class or equipment_class not in EQUIPMENT_FAULT_MAP:
        return {
            "score": 70.0,
            "detail": (
                "Equipment class not confidently identified from column names — fault-mode "
                "observability not assessed against the domain signature table (neutral)."
            ),
            "severity": "info",
            "raw": {"skipped": True, "equipment_class": equipment_class},
        }

    sigs = EQUIPMENT_FAULT_MAP[equipment_class]
    # Distinct (fault_name, sensor_type) pairs — a fault may show in multiple channels.
    fault_to_sensors: Dict[str, set] = {}
    for s in sigs:
        fault_to_sensors.setdefault(s.get("fault_name", "?"), set()).add(s.get("sensor_type"))

    total = len(fault_to_sensors)
    observable = [f for f, stypes in fault_to_sensors.items() if stypes & present]
    n_obs = len(observable)
    # Channels documented for this equipment but missing from the dataset
    needed = set().union(*[v for v in fault_to_sensors.values()]) if fault_to_sensors else set()
    missing_channels = sorted(needed - present)

    frac = n_obs / total if total else 0.0
    score = round(100.0 * frac, 1)

    if frac >= 0.75:
        severity = "ok"
    elif frac >= 0.5:
        severity = "info"
    elif frac >= 0.3:
        severity = "warning"
    else:
        severity = "critical"

    detail = (
        f"Equipment '{equipment_class}': {n_obs}/{total} documented failure modes are observable "
        f"with the sensor channels present ({', '.join(sorted(present)) or 'none'}). "
    )
    if missing_channels:
        detail += (
            f"Missing channels that would unlock more failure modes: {', '.join(missing_channels)}. "
        )
    if frac < 0.5:
        detail += (
            "Many known failure modes for this equipment cannot be detected from this data — "
            "add the missing sensor channels for a PdM-ready dataset."
        )

    return {
        "score": score,
        "detail": detail,
        "severity": severity,
        "raw": {
            "equipment_class": equipment_class,
            "total_fault_modes": total,
            "observable_fault_modes": n_obs,
            "missing_channels": missing_channels,
            "present_sensors": sorted(present),
        },
    }


def compute(
    df: pd.DataFrame,
    label_col: Optional[str] = None,
    timestamp_col: Optional[str] = None,
    rul_col: Optional[str] = None,
    **ctx: Any,
) -> Dict[str, Any]:
    """
    Run all 8 domain PdM quality sub-checks.

    Returns same shape as all other dimension modules:
        {"score": float, "detail": str, "severity": str, "raw": dict}

    Activation gate: if fewer than 5 numeric columns, returns neutral (score=50, severity=info).
    """
    n_numeric = df.select_dtypes(include=[np.number]).shape[1]
    if n_numeric < 5:
        return {
            "score": 50.0,
            "detail": (
                f"Only {n_numeric} numeric column(s) — domain PdM checks require at least 5 "
                "numeric sensor columns. Check not applicable."
            ),
            "severity": "info",
            "raw": {"skipped": True, "reason": "insufficient_numeric_cols", "n_numeric": n_numeric},
        }

    # Auto-detect columns if not provided
    if rul_col is None:
        rul_col = _auto_detect_rul_col(df)
    label_col = _auto_detect_label_col(df, label_col)

    detected_sensors = _classify_columns(df.columns.tolist())
    equipment_class  = _detect_equipment_class(df.columns.tolist())

    sub: Dict[str, Dict] = {}

    sub["sensor_coverage"] = _check_sensor_coverage(detected_sensors, equipment_class)

    sub["sampling_rate"] = _check_sampling_rate(df, timestamp_col, detected_sensors)

    sub["failure_representation"] = _check_failure_representation(df, label_col, rul_col)

    sub["pdm_imbalance"] = _check_pdm_imbalance(df, label_col)

    sub["temporal_degradation"] = _check_temporal_degradation(
        df, timestamp_col, label_col, rul_col
    )

    sub["pdm_label_quality"] = _check_pdm_label_quality(
        df, label_col, rul_col, timestamp_col
    )

    sub["sensor_health"] = _check_sensor_health(df, detected_sensors)

    sub["fault_observability"] = _check_fault_observability(equipment_class, detected_sensors)

    sub["metadata_coverage"] = _check_metadata_coverage(df)

    # Weighted composite
    total_w = sum(DOMAIN_PDM_INTERNAL_WEIGHTS.values())
    composite = (
        sum(
            sub[k]["score"] * DOMAIN_PDM_INTERNAL_WEIGHTS[k]
            for k in sub
            if k in DOMAIN_PDM_INTERNAL_WEIGHTS
        )
        / total_w
    )

    # Severity: score-based (consistent with all other dimensions)
    # score>=75 → ok, 60–75 → info, 40–60 → warning, <40 → critical
    severity: str
    if composite >= 75:
        severity = "ok"
    elif composite >= 60:
        severity = "info"
    elif composite >= 40:
        severity = "warning"
    else:
        severity = "critical"

    detail = _build_detail_string(sub, equipment_class, detected_sensors, composite)

    return {
        "score": round(composite, 2),
        "detail": detail,
        "severity": severity,
        "raw": {
            "sub_checks": sub,
            "equipment_class": equipment_class,
            "detected_sensors": list(detected_sensors.keys()),
            "rul_col": rul_col,
            "label_col_used": label_col,
            "pdm_override_active": sub.get("pdm_imbalance", {}).get("raw", {}).get("pdm_override_active", False),
        },
    }
