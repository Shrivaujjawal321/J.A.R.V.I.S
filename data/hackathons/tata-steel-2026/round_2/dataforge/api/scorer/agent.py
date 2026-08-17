"""
DataForge Scoring Agent — Decision Graph

The agent DECIDES which checks to run, in what order, based on data characteristics.
It builds an explicit reasoning trace visible to judges.

Decision graph:
  1. Profile dataset → detect type (tabular vs time-series), label col, timestamp col
  2. Gate on minimum quality → run cheap checks first (completeness, schema, duplicates, distribution)
  3. If time-series detected → unlock temporal_coverage
  4. If label present → unlock class_balance, label_quality, leakage
  5. If composite looks viable → run readiness (LightGBM training)
  6. Compose improvements + review
  7. If LLM key present → rewrite review with LLM; else use deterministic template
"""

from __future__ import annotations
import os
import asyncio
import hashlib
import time
import pandas as pd
import numpy as np
from typing import Any, Dict, List, Optional, Tuple

from scorer.dimensions import (
    completeness,
    class_balance,
    label_quality,
    duplicates,
    outliers,
    schema_validity,
    leakage,
    temporal_coverage,
    feature_redundancy,
    distribution_sanity,
)
from scorer.dimensions import domain_pdm as domain_pdm_module
from scorer.composite import compute_composite, get_weights
from scorer.readiness import compute_readiness
from scorer.models import (
    AuditResult,
    DimensionResult,
    SubScores,
    ReadinessResult,
    ReadinessPenalties,
    Improvement,
    Preview,
    ColumnPreview,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _detect_timestamp_col(df: pd.DataFrame) -> Optional[str]:
    """Auto-detect a datetime column."""
    for col in df.columns:
        if any(hint in col.lower() for hint in ["time", "date", "ts", "timestamp", "datetime", "created", "updated"]):
            try:
                pd.to_datetime(df[col].dropna().iloc[:50], errors="raise")
                return col
            except Exception:
                pass
    # Try parsing each object column
    for col in df.select_dtypes(include=["object"]).columns:
        sample = df[col].dropna().iloc[:20]
        try:
            parsed = pd.to_datetime(sample, errors="coerce")
            if parsed.notna().mean() > 0.8:
                return col
        except Exception:
            pass
    return None


# Common target/label column names across ML datasets (lowercased, exact-match tier).
_LABEL_NAME_EXACT = {
    "target", "label", "labels", "class", "classes", "y", "output", "outcome",
    "response", "result", "status", "failure", "fault", "defect", "anomaly",
    "churn", "fraud", "is_fraud", "rul", "category", "target_class", "machine_failure",
}
# Substring hints — a column whose name *contains* one of these is a likely target.
_LABEL_NAME_HINTS = (
    "target", "label", "class", "failure", "fault", "defect", "anomaly",
    "churn", "fraud", "outcome", "status", "rul",
)


def _detect_label_col(df: pd.DataFrame, timestamp_col: Optional[str] = None) -> Tuple[Optional[str], str]:
    """
    Auto-detect the supervised target column when the caller did not specify one.

    Conservative 3-tier heuristic (returns the column + a confidence string for the trace):
      1. Exact name match against common target names (high confidence).
      2. Substring-hint match, preferring the lowest-cardinality candidate, excluding id-like cols.
      3. Fallback: the last column IFF it is low-cardinality (looks categorical/binary),
         which is the dominant CSV convention for ML datasets (medium confidence).
    Returns (None, "none") when nothing looks like a label — honest abstention beats a wrong guess.
    """
    cols = [c for c in df.columns if c != timestamp_col]
    if not cols:
        return None, "none"
    lower = {c: str(c).strip().lower() for c in cols}
    n = max(len(df), 1)

    def _is_id_like(c: str) -> bool:
        lc = lower[c]
        return lc == "id" or lc.endswith("_id") or lc.endswith("id") and df[c].nunique(dropna=True) > 0.9 * n

    # Tier 1 — exact match on a known target name (skip id-like)
    for c in cols:
        if lower[c] in _LABEL_NAME_EXACT and not _is_id_like(c):
            if df[c].nunique(dropna=True) >= 2:
                return c, "high (exact name match)"

    # Tier 2 — substring hint, prefer lowest-cardinality non-id candidate
    hinted = [
        c for c in cols
        if any(h in lower[c] for h in _LABEL_NAME_HINTS) and not _is_id_like(c)
        and df[c].nunique(dropna=True) >= 2
    ]
    if hinted:
        best = min(hinted, key=lambda c: df[c].nunique(dropna=True))
        return best, "medium (name hint)"

    # Tier 3 — last column if it looks like a categorical/low-cardinality target
    last = cols[-1]
    if not _is_id_like(last):
        nun = df[last].nunique(dropna=True)
        if 2 <= nun and (nun <= 20 or nun / n <= 0.05):
            return last, "medium (last column, low cardinality)"

    return None, "none"


def _detect_dataset_type(df: pd.DataFrame, timestamp_col: Optional[str]) -> str:
    if timestamp_col:
        return "time_series"
    return "tabular"


def _stable_dataset_id(df: pd.DataFrame) -> str:
    """SHA-256 of first 1000 rows serialised as CSV bytes."""
    sample = df.head(1000)
    raw = sample.to_csv(index=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:32]


def _build_preview(df: pd.DataFrame) -> Preview:
    columns = []
    for col in df.columns:
        null_pct = round(float(df[col].isnull().mean() * 100), 2)
        dtype = str(df[col].dtype)
        columns.append(ColumnPreview(name=col, dtype=dtype, null_pct=null_pct))

    # Sample 5 rows, serialise to JSON-safe dict
    sample = df.head(5).replace({np.nan: None, np.inf: None, -np.inf: None})
    sample_rows = sample.astype(object).where(sample.notna(), None).to_dict(orient="records")
    # Ensure all values are JSON-serialisable
    safe_rows = []
    for row in sample_rows:
        safe_row = {}
        for k, v in row.items():
            if isinstance(v, (np.integer,)):
                v = int(v)
            elif isinstance(v, (np.floating,)):
                v = float(v) if np.isfinite(v) else None
            elif isinstance(v, (np.bool_,)):
                v = bool(v)
            safe_row[str(k)] = v
        safe_rows.append(safe_row)
    return Preview(columns=columns, sample_rows=safe_rows)


def _generate_improvements(
    sub_scores: Dict[str, Dict],
    dataset_type: str,
    weights: Dict[str, float],
    cap_reasons: List[str],
) -> List[Improvement]:
    improvements = []

    dim_order = {
        "completeness":        ("Fill Missing Values", "P0", "medium"),
        "class_balance":       ("Address Class Imbalance", "P1", "medium"),
        "label_quality":       ("Review and Correct Mislabelled Rows", "P0", "high"),
        "duplicates":          ("Deduplicate Dataset", "P0", "low"),
        "outliers":            ("Investigate and Clip Outliers", "P1", "medium"),
        "schema_validity":     ("Fix Schema / Type Issues", "P1", "low"),
        "leakage":             ("Remove Leaky Features", "P0", "low"),
        "temporal_coverage":   ("Fill Temporal Gaps", "P1", "high"),
        "feature_redundancy":  ("Remove Redundant Features", "P2", "low"),
        "distribution_sanity": ("Fix Distribution Anomalies", "P1", "low"),
        "domain_pdm":          ("Address Domain PdM Quality Issues", "P0", "high"),
    }

    for dim, result in sub_scores.items():
        score = result["score"]
        if score >= 85:
            continue  # Good enough, no improvement needed

        cfg = dim_order.get(dim, (dim.replace("_", " ").title(), "P2", "medium"))
        base_title, base_priority, effort = cfg

        # Severity-based priority escalation
        sev = result.get("severity", "ok")
        if sev == "critical":
            priority = "P0"
        elif sev == "warning":
            priority = "P1"
        else:
            priority = base_priority if base_priority == "P2" else "P2"

        # Estimated score delta (how much composite could improve if this dim hit 90)
        weight = weights.get(dim, 0.08)
        delta = round((90.0 - score) * weight, 1)

        desc = result.get("detail", "See dimension detail.")
        improvements.append(
            Improvement(
                dimension=dim,
                priority=priority,
                title=base_title,
                description=desc,
                estimated_score_delta=delta,
                effort=effort,
            )
        )

    # Sort: P0 first, then by delta desc
    priority_order = {"P0": 0, "P1": 1, "P2": 2}
    improvements.sort(key=lambda x: (priority_order[x.priority], -x.estimated_score_delta))

    return improvements[:10]


def _deterministic_review(
    filename: str,
    dataset_type: str,
    n_rows: int,
    n_cols: int,
    composite_score: float,
    grade: str,
    sub_scores: Dict[str, Dict],
    readiness_data: Optional[Dict],
    improvements: List[Improvement],
    cap_reasons: List[str],
) -> str:
    """
    High-quality template-based review a non-technical engineer can understand.
    This is the primary path when no LLM API key is present.
    """
    lines = []

    # Opening summary
    grade_emoji_map = {
        "Excellent": "excellent condition",
        "Good": "good condition",
        "Fair": "fair condition with some issues",
        "Needs Work": "multiple quality problems",
        "Poor": "critical quality problems",
    }
    lines.append(
        f"Your dataset '{filename}' ({n_rows:,} rows, {n_cols} columns) has been assessed as "
        f"'{grade}' with an overall quality score of {composite_score:.0f}/100. "
        f"The dataset is in {grade_emoji_map.get(grade, 'an assessed condition')}."
    )

    # Score breakdown highlight
    critical_dims = [(k, v) for k, v in sub_scores.items() if v["severity"] == "critical"]
    warning_dims  = [(k, v) for k, v in sub_scores.items() if v["severity"] == "warning"]

    if critical_dims:
        dim_names = [k.replace("_", " ") for k, _ in critical_dims]
        lines.append(
            f"Critical issues were found in: {', '.join(dim_names)}. "
            f"These must be addressed before the data can be used for reliable machine learning."
        )

    if warning_dims:
        dim_names = [k.replace("_", " ") for k, _ in warning_dims]
        lines.append(
            f"Warnings were raised for: {', '.join(dim_names)}. These will reduce model accuracy if left unaddressed."
        )

    # Cap explanations
    if cap_reasons:
        lines.append("Scoring notes: " + " ".join(cap_reasons))

    # Readiness summary
    if readiness_data and not readiness_data.get("skipped"):
        rp = readiness_data.get("readiness_pct", 0)
        bauc = readiness_data.get("baseline_auc", 0)
        tauc = readiness_data.get("target_auc", 0.80)
        lines.append(
            f"ML Readiness: a quick 3-fold cross-validation achieved a baseline AUC of {bauc:.3f}. "
            f"After adjusting for data quality penalties, there is a {rp:.0f}% probability this dataset "
            f"will reach the target AUC of {tauc:.2f} in production training."
        )
    elif readiness_data and readiness_data.get("skipped"):
        lines.append(f"ML Readiness training was skipped: {readiness_data.get('reason', '')}")

    # Domain PdM findings (plant engineer language)
    domain_result = sub_scores.get("domain_pdm")
    if domain_result and not domain_result.get("raw", {}).get("skipped"):
        domain_score = domain_result.get("score", 50.0)
        domain_sev = domain_result.get("severity", "info")
        domain_raw = domain_result.get("raw", {})
        equip_class = domain_raw.get("equipment_class")
        detected_sensors = domain_raw.get("detected_sensors", [])
        sub_checks = domain_raw.get("sub_checks", {})

        equip_str = equip_class.capitalize() if equip_class else "Steel-plant"
        sensor_str = ", ".join(detected_sensors) or "none detected"

        lines.append(
            f"Domain PdM Analysis ({equip_str} equipment | sensors: {sensor_str}): "
            f"domain quality score is {domain_score:.0f}/100."
        )

        # Surface the most important sub-check findings
        for sub_name, sub_val in sub_checks.items():
            if sub_val.get("severity") in ("critical", "warning"):
                readable = sub_name.replace("_", " ").title()
                lines.append(f"  - {readable}: {sub_val['detail']}")

        # PdM imbalance override — explicitly reassure plant engineer
        pdm_imb = sub_checks.get("pdm_imbalance", {})
        if pdm_imb.get("raw", {}).get("pdm_override_active") and pdm_imb.get("severity") == "ok":
            lines.append(
                f"  - Imbalance note: {pdm_imb['detail']}"
            )

        if domain_sev == "critical":
            lines.append(
                "Domain issues are CRITICAL — the dataset cannot support industrial PdM modeling "
                "in its current state. Address domain findings before any model training."
            )

    # Top improvement
    if improvements:
        top = improvements[0]
        lines.append(
            f"Top priority action: [{top.priority}] {top.title} — {top.description} "
            f"Fixing this could improve the composite score by approximately {top.estimated_score_delta:.0f} points."
        )

    return " ".join(lines)


# ---------------------------------------------------------------------------
# Subscription-backed review (NO API key — uses Boss's Claude Max subscription
# via CLAUDE_CODE_OAUTH_TOKEN + the Claude Agent SDK, same auth as jarvis-core).
# ---------------------------------------------------------------------------

def _load_oauth_token() -> Optional[str]:
    """Return CLAUDE_CODE_OAUTH_TOKEN from env, else read it from the Jarvis repo .env.

    The EDITH uvicorn process is launched from api/ and may not inherit the repo-root
    .env, so we fall back to parsing it directly (once) and caching into os.environ.
    """
    tok = os.getenv("CLAUDE_CODE_OAUTH_TOKEN")
    if tok:
        return tok
    # Walk up to find the Jarvis repo root .env (contains the token)
    here = os.path.abspath(__file__)
    for _ in range(8):
        here = os.path.dirname(here)
        env_path = os.path.join(here, ".env")
        if os.path.isfile(env_path):
            try:
                with open(env_path, "r") as fh:
                    for line in fh:
                        line = line.strip()
                        if line.startswith("CLAUDE_CODE_OAUTH_TOKEN="):
                            tok = line.split("=", 1)[1].strip().strip('"').strip("'")
                            if tok:
                                os.environ["CLAUDE_CODE_OAUTH_TOKEN"] = tok
                                return tok
            except Exception:
                pass
        if os.path.basename(here) == "J.A.R.V.I.S.":
            break
    return None


async def _subscription_review(prompt: str, timeout_s: int = 30) -> Optional[str]:
    """Rewrite the review via the Claude Max subscription (Agent SDK, no API key).

    Returns the model text, or None on any failure (offline, token missing, timeout,
    SDK absent) so the caller falls back to the deterministic template.
    """
    if os.getenv("EDITH_LLM_REVIEW", "subscription").lower() in ("0", "off", "none"):
        return None
    token = _load_oauth_token()
    if not token:
        return None
    try:
        from claude_agent_sdk import ClaudeAgentOptions, query  # type: ignore
    except Exception:
        return None

    system_prompt = (
        "You are DataForge / EDITH, an industrial dataset-quality analyst. You write short, "
        "plain-language audit reviews for steel-plant engineers who are NOT data scientists. "
        "No jargon, no markdown headers, no 'I'. Be specific and actionable."
    )
    options_kwargs: dict = {
        "max_turns": 1,
        "allowed_tools": [],          # pure text generation — no tools
        "system_prompt": system_prompt,
    }
    try:
        options = ClaudeAgentOptions(**options_kwargs)
    except TypeError:
        # Older/newer SDK build may not accept one of the kwargs — retry minimal
        options = ClaudeAgentOptions(max_turns=1)

    text_parts: List[str] = []
    final_result: Optional[str] = None

    async def _collect() -> None:
        nonlocal final_result
        async for message in query(prompt=prompt, options=options):
            content = getattr(message, "content", None)
            if isinstance(content, list):
                for block in content:
                    t = getattr(block, "text", None)
                    if t:
                        text_parts.append(t)
            result = getattr(message, "result", None)
            if isinstance(result, str) and result:
                final_result = result

    try:
        await asyncio.wait_for(_collect(), timeout=timeout_s)
    except Exception:
        return None

    text = (final_result or "\n".join(text_parts)).strip()
    return text or None


async def _llm_review(
    deterministic_review: str,
    sub_scores: Dict[str, Dict],
    composite_score: float,
    grade: str,
    improvements: List[Improvement],
    dataset_type: str,
) -> str:
    """
    Optionally rewrite the review using Anthropic Claude or Gemini.
    Returns deterministic_review if no API key or call fails.
    """
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    gemini_key = os.getenv("GEMINI_API_KEY")

    improvements_str = "\n".join(
        [f"- [{imp.priority}] {imp.title}: {imp.description}" for imp in improvements[:5]]
    )

    # Build domain PdM context for the LLM if available
    domain_context = ""
    domain_result = sub_scores.get("domain_pdm")
    if domain_result and not domain_result.get("raw", {}).get("skipped"):
        domain_raw = domain_result.get("raw", {})
        equip_class = domain_raw.get("equipment_class", "unknown")
        sensors = domain_raw.get("detected_sensors", [])
        sub_checks = domain_raw.get("sub_checks", {})
        critical_subs = {k: v["detail"] for k, v in sub_checks.items() if v.get("severity") == "critical"}
        warning_subs  = {k: v["detail"] for k, v in sub_checks.items() if v.get("severity") == "warning"}
        domain_context = (
            f"\nDOMAIN PdM FINDINGS (equipment: {equip_class}, sensors: {sensors}):\n"
            + (f"  CRITICAL: {critical_subs}\n" if critical_subs else "")
            + (f"  WARNING: {warning_subs}\n" if warning_subs else "")
            + (f"  Domain score: {domain_result.get('score', '?')}/100\n")
        )
        # Add imbalance override context if active
        pdm_imb = sub_checks.get("pdm_imbalance", {})
        if pdm_imb.get("raw", {}).get("pdm_override_active"):
            domain_context += (
                f"  PdM IMBALANCE NOTE: {pdm_imb.get('detail', '')}\n"
                "  (Generic imbalance penalty was overridden because this failure rate is "
                "realistic for industrial predictive maintenance — tell the plant engineer "
                "that the imbalance is NOT a problem.)\n"
            )

    prompt = f"""You are DataForge, an AI data quality analyst for industrial manufacturing datasets.

Write a concise, professional 2-3 paragraph review of a dataset audit for a plant engineer who is NOT a data scientist.
Avoid technical jargon. Use plain English. Be specific about problems and solutions.
If domain PdM findings are provided, lead with those — they are the most actionable for a plant engineer.
If the imbalance override is active, explicitly tell the engineer the failure rate is normal and expected.

AUDIT SUMMARY:
- Overall Grade: {grade} ({composite_score:.0f}/100)
- Dataset Type: {dataset_type}
- Dimension Scores: {', '.join([f"{k}: {v['score']:.0f}" for k, v in sub_scores.items()])}
{domain_context}
TOP IMPROVEMENTS NEEDED:
{improvements_str}

DRAFT REVIEW (improve this):
{deterministic_review}

Rewrite as 2-3 clear paragraphs. Be specific. Do not add fake data. Do not say "I"."""

    # PRIMARY path for Boss's setup: Claude Max subscription via OAuth token (NO API key).
    sub_text = await _subscription_review(prompt)
    if sub_text:
        return sub_text

    if anthropic_key:
        try:
            import anthropic  # type: ignore
            client = anthropic.Anthropic(api_key=anthropic_key)
            msg = client.messages.create(
                model="claude-haiku-4-5",
                max_tokens=600,
                messages=[{"role": "user", "content": prompt}],
            )
            return msg.content[0].text.strip()
        except Exception:
            pass

    if gemini_key:
        try:
            import google.generativeai as genai  # type: ignore
            genai.configure(api_key=gemini_key)
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(prompt)
            return response.text.strip()
        except Exception:
            pass

    return deterministic_review


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

async def run_audit(
    df: pd.DataFrame,
    filename: str,
    label_col: Optional[str],
    timestamp_col: Optional[str],
    target_auc: float = 0.80,
) -> AuditResult:
    """
    Full agentic audit pipeline with explicit reasoning trace.
    """
    trace: List[str] = []
    t_start = time.time()

    # ----------------------------------------------------------------
    # Step 1: Profiling + type detection
    # ----------------------------------------------------------------
    trace.append("STEP 1: Profiling dataset characteristics.")

    if timestamp_col is None:
        timestamp_col = _detect_timestamp_col(df)
        if timestamp_col:
            trace.append(f"  → Auto-detected timestamp column: '{timestamp_col}'")

    # Auto-detect the supervised target when the caller didn't pass one. Without this,
    # class_balance / label_quality / leakage / readiness all default to neutral 50 on
    # every external upload, collapsing the score's ability to discriminate good vs bad data.
    label_auto_detected = False
    if label_col is None:
        label_col, label_conf = _detect_label_col(df, timestamp_col)
        if label_col:
            label_auto_detected = True
            trace.append(f"  → Auto-detected label column: '{label_col}' — confidence {label_conf}")
        else:
            trace.append("  → No label column detected (no name match, no low-cardinality target).")

    dataset_type = _detect_dataset_type(df, timestamp_col)
    trace.append(f"  → Dataset type: {dataset_type} | rows={len(df):,} cols={len(df.columns)}")
    trace.append(
        f"  → Label column: {label_col or '[none]'}"
        f"{' (auto)' if label_auto_detected else ''} | Timestamp: {timestamp_col or '[none]'}"
    )

    dataset_id = _stable_dataset_id(df)
    weights = get_weights(dataset_type)

    # ----------------------------------------------------------------
    # Step 2: Cheap checks (always run)
    # ----------------------------------------------------------------
    trace.append("STEP 2: Running structural checks (completeness, schema, duplicates, distribution).")

    ctx = {
        "label_col": label_col,
        "timestamp_col": timestamp_col,
        "dataset_type": dataset_type,
    }

    completeness_r   = completeness.compute(df, **ctx)
    schema_r         = schema_validity.compute(df, **ctx)
    duplicates_r     = duplicates.compute(df, **ctx)
    distribution_r   = distribution_sanity.compute(df, **ctx)
    outliers_r       = outliers.compute(df, **ctx)
    redundancy_r     = feature_redundancy.compute(df, **ctx)

    trace.append(
        f"  → Completeness={completeness_r['score']:.0f} | Schema={schema_r['score']:.0f} | "
        f"Duplicates={duplicates_r['score']:.0f} | Distribution={distribution_r['score']:.0f}"
    )

    # ----------------------------------------------------------------
    # Step 3: Label-dependent checks
    # ----------------------------------------------------------------
    if label_col and label_col in df.columns:
        trace.append(f"STEP 3: Label column '{label_col}' present — running label-aware checks.")
        class_balance_r = class_balance.compute(df, **ctx)
        label_quality_r = label_quality.compute(df, **ctx)
        leakage_r       = leakage.compute(df, **ctx)
        trace.append(
            f"  → ClassBalance={class_balance_r['score']:.0f} | LabelQuality={label_quality_r['score']:.0f} | "
            f"Leakage={leakage_r['score']:.0f}"
        )
    else:
        trace.append("STEP 3: No label column — class_balance, label_quality, leakage set to neutral (50).")
        neutral = {"score": 50.0, "detail": "No label column provided.", "severity": "info", "raw": {}}
        class_balance_r = neutral.copy()
        label_quality_r = neutral.copy()
        leakage_r       = neutral.copy()

    # ----------------------------------------------------------------
    # Step 4: Temporal checks (time-series only)
    # ----------------------------------------------------------------
    if dataset_type == "time_series":
        trace.append(f"STEP 4: Time-series dataset — running temporal coverage check.")
        temporal_r = temporal_coverage.compute(df, **ctx)
        trace.append(f"  → TemporalCoverage={temporal_r['score']:.0f}")
    else:
        trace.append("STEP 4: Tabular dataset — temporal coverage check skipped (weight=0).")
        temporal_r = {
            "score": 50.0,
            "detail": "Not applicable for tabular datasets.",
            "severity": "info",
            "raw": {"skipped": True},
        }

    # ----------------------------------------------------------------
    # Step 4b: Domain PdM checks (time-series + 5+ numeric cols only)
    # ----------------------------------------------------------------
    n_numeric_cols = df.select_dtypes(include=[np.number]).shape[1]
    domain_pdm_r: Optional[Dict] = None

    if dataset_type == "time_series" and n_numeric_cols >= 5:
        trace.append(
            f"STEP 4b: Time-series with {n_numeric_cols} numeric cols — "
            "running domain PdM checks (8 sub-dimensions: sensor coverage, sampling rate, "
            "failure representation, PdM imbalance realism, temporal degradation arc, "
            "PdM label quality, sensor health, operating metadata)."
        )
        domain_pdm_r = domain_pdm_module.compute(df, **ctx)
        trace.append(
            f"  → DomainPdM={domain_pdm_r['score']:.0f} | severity={domain_pdm_r['severity']}"
        )

        # Surface equipment class and key findings in trace
        domain_raw = domain_pdm_r.get("raw", {})
        equip_class = domain_raw.get("equipment_class")
        if equip_class:
            trace.append(f"  → Equipment class inferred: {equip_class}")
        detected_sensors = domain_raw.get("detected_sensors", [])
        trace.append(f"  → Detected sensor types: {detected_sensors}")

        # Surface critical/warning sub-checks
        sub_checks = domain_raw.get("sub_checks", {})
        for sub_name, sub_val in sub_checks.items():
            if sub_val.get("severity") in ("critical", "warning"):
                trace.append(
                    f"  → [{sub_val['severity'].upper()}] {sub_name}: {sub_val['detail'][:120]}"
                )

        # PdM imbalance override: if domain layer detected a PdM dataset with realistic
        # imbalance (0.5–15%), REPLACE class_balance score with the domain-calibrated one.
        # This prevents the generic log-decay penalty from unfairly downgrading a healthy
        # PdM dataset with 2% failure rate (IR=50:1 is NORMAL for steel plants).
        pdm_override = domain_raw.get("pdm_override_active", False)
        pdm_imb_sub = sub_checks.get("pdm_imbalance", {})
        pdm_imb_severity = pdm_imb_sub.get("severity", "info")
        if pdm_override and pdm_imb_sub:
            original_cb_score = class_balance_r.get("score", 50.0)
            new_cb_score = pdm_imb_sub["score"]
            if label_col and label_col in df.columns:
                class_balance_r = {
                    "score": new_cb_score,
                    "detail": (
                        f"[PdM DOMAIN OVERRIDE] {pdm_imb_sub['detail']} "
                        f"(Generic imbalance penalty overridden from {original_cb_score:.0f} → "
                        f"{new_cb_score:.0f} because this failure rate is realistic for industrial PdM.)"
                    ),
                    "severity": pdm_imb_severity,
                    "raw": {**class_balance_r.get("raw", {}), "pdm_override": True},
                }
                trace.append(
                    f"  → PdM IMBALANCE OVERRIDE: class_balance {original_cb_score:.0f} → "
                    f"{new_cb_score:.0f} ({pdm_imb_sub['detail'][:80]})"
                )
    else:
        if dataset_type != "time_series":
            trace.append("STEP 4b: Tabular dataset — domain PdM checks skipped (not applicable).")
        else:
            trace.append(
                f"STEP 4b: Only {n_numeric_cols} numeric cols (need 5+) — "
                "domain PdM checks skipped."
            )

    # ----------------------------------------------------------------
    # Step 5: Composite + caps
    # ----------------------------------------------------------------
    trace.append("STEP 5: Computing composite score with penalty caps.")

    raw_sub_scores = {
        "completeness":        completeness_r,
        "class_balance":       class_balance_r,
        "label_quality":       label_quality_r,
        "duplicates":          duplicates_r,
        "outliers":            outliers_r,
        "schema_validity":     schema_r,
        "leakage":             leakage_r,
        "temporal_coverage":   temporal_r,
        "feature_redundancy":  redundancy_r,
        "distribution_sanity": distribution_r,
    }
    # Include domain_pdm in composite computation if it ran
    if domain_pdm_r is not None:
        raw_sub_scores["domain_pdm"] = domain_pdm_r

    composite_score, grade, cap_reasons = compute_composite(raw_sub_scores, dataset_type)
    trace.append(f"  → Composite={composite_score:.1f} | Grade={grade}")
    if cap_reasons:
        for reason in cap_reasons:
            trace.append(f"  → CAP ACTIVE: {reason}")

    # ----------------------------------------------------------------
    # Step 6: Readiness (conditional)
    # ----------------------------------------------------------------
    readiness_data = None
    if label_col and label_col in df.columns:
        trace.append("STEP 6: Running ML readiness check (LightGBM 3-fold CV).")
        readiness_data = compute_readiness(
            df,
            label_col=label_col,
            composite_score=composite_score,
            sub_scores=raw_sub_scores,
            target_auc=target_auc,
            dataset_type=dataset_type,
        )
        if readiness_data:
            if readiness_data.get("skipped"):
                trace.append(f"  → Readiness SKIPPED: {readiness_data.get('reason')}")
            else:
                trace.append(
                    f"  → Readiness={readiness_data['readiness_pct']:.0f}% | "
                    f"BaselineAUC={readiness_data['baseline_auc']:.3f}"
                )
    else:
        trace.append("STEP 6: No label — readiness check skipped.")

    # ----------------------------------------------------------------
    # Step 7: Improvements + Review
    # ----------------------------------------------------------------
    trace.append("STEP 7: Generating ranked improvements and narrative review.")

    improvements = _generate_improvements(raw_sub_scores, dataset_type, weights, cap_reasons)

    det_review = _deterministic_review(
        filename=filename,
        dataset_type=dataset_type,
        n_rows=len(df),
        n_cols=len(df.columns),
        composite_score=composite_score,
        grade=grade,
        sub_scores=raw_sub_scores,
        readiness_data=readiness_data,
        improvements=improvements,
        cap_reasons=cap_reasons,
    )

    review = await _llm_review(
        deterministic_review=det_review,
        sub_scores=raw_sub_scores,
        composite_score=composite_score,
        grade=grade,
        improvements=improvements,
        dataset_type=dataset_type,
    )

    llm_used = review != det_review
    trace.append(f"  → Review source: {'LLM (rewritten)' if llm_used else 'deterministic template'}")

    elapsed = round(time.time() - t_start, 2)
    trace.append(f"DONE: Audit completed in {elapsed}s.")

    # ----------------------------------------------------------------
    # Assemble final result
    # ----------------------------------------------------------------

    def _dim_result(r: Dict, dim_name: str) -> DimensionResult:
        # For domain_pdm we pass the raw dict so the frontend / LLM review can access sub_checks.
        # For all other dimensions raw is omitted (keep response size down).
        raw_payload = r.get("raw") if dim_name == "domain_pdm" else None
        return DimensionResult(
            score=float(r["score"]),
            weight=weights.get(dim_name, 0.0),
            detail=r.get("detail", ""),
            severity=r.get("severity", "info"),
            raw=raw_payload,
        )

    sub_scores_obj = SubScores(
        completeness        = _dim_result(completeness_r,   "completeness"),
        class_balance       = _dim_result(class_balance_r,  "class_balance"),
        label_quality       = _dim_result(label_quality_r,  "label_quality"),
        duplicates          = _dim_result(duplicates_r,      "duplicates"),
        outliers            = _dim_result(outliers_r,        "outliers"),
        schema_validity     = _dim_result(schema_r,          "schema_validity"),
        leakage             = _dim_result(leakage_r,         "leakage"),
        temporal_coverage   = _dim_result(temporal_r,        "temporal_coverage"),
        feature_redundancy  = _dim_result(redundancy_r,      "feature_redundancy"),
        distribution_sanity = _dim_result(distribution_r,    "distribution_sanity"),
        domain_pdm          = _dim_result(domain_pdm_r, "domain_pdm") if domain_pdm_r is not None else None,
    )

    # Build readiness
    readiness_obj = None
    if readiness_data and not readiness_data.get("skipped"):
        readiness_obj = ReadinessResult(
            readiness_pct=readiness_data["readiness_pct"],
            baseline_auc=readiness_data["baseline_auc"],
            target_auc=target_auc,
            penalties=ReadinessPenalties(
                label_noise=readiness_data["penalties"]["label_noise"],
                imbalance=readiness_data["penalties"]["imbalance"],
                temporal_gaps=readiness_data["penalties"]["temporal_gaps"],
            ),
        )

    preview = _build_preview(df)

    return AuditResult(
        dataset_id=dataset_id,
        filename=filename,
        dataset_type=dataset_type,
        n_rows=len(df),
        n_cols=len(df.columns),
        composite_score=composite_score,
        grade=grade,
        sub_scores=sub_scores_obj,
        readiness=readiness_obj,
        review=review,
        improvements=improvements,
        preview=preview,
        reasoning_trace=trace,
    )
