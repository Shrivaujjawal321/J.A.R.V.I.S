# Domain-Specific Quality Rules for Steel-Plant / PdM Sensor Datasets
**DataForge — Scorer Domain-Awareness Upgrade**
*Authored: 2026-06-08 | Target: scorer/dimensions/domain_pdm.py + composite.py integration*

---

## Purpose

The existing DataForge scorer evaluates generic tabular/time-series quality (completeness, balance, leakage, etc.). These dimensions are necessary but not sufficient for a steel-plant predictive-maintenance dataset. A dataset with 100% completeness and zero leakage can still be completely useless for PdM if it lacks vibration sensors, samples them at 100 Hz, has zero run-to-failure trajectories, or marks failures 48 hours after the actual event.

This document defines the **domain-specific quality rubric** — eight dimensions that go beyond what generic stats can see. Each dimension specifies: what it checks, how to detect it programmatically, what threshold triggers each severity, how it maps to the existing scorer, and the exact plain-language message surface to users.

---

## How This Plugs Into the Existing Scorer

**Integration strategy (three layers):**

1. **New dimension module:** `scorer/dimensions/domain_pdm.py` — a single module that runs all eight checks when the agent detects a time-series dataset with equipment/sensor characteristics. Returns a `Dict[str, Any]` in the same shape as all other dimension modules (`score`, `detail`, `severity`, `raw`).

2. **New `SubScores` field:** Add `domain_pdm: Optional[DimensionResult]` to `models.py`. Scored only when `dataset_type == "time_series"` and at least 5+ numeric sensor columns are detected (heuristic: `n_numeric_cols >= 5`). Neutral (score=50, severity="info") for tabular/non-sensor datasets.

3. **Weight injection:** Add `"domain_pdm": 0.15` to `TIME_SERIES_WEIGHTS` in `composite.py`, redistributing from `distribution_sanity` (0.08 → 0.05) and `feature_redundancy` (0.07 → 0.05) since those are already partially captured here. Tabular weights: `domain_pdm: 0.00` (no impact). New TIME_SERIES total still sums to 1.0.

4. **Activation gate in agent.py:** After Step 4 (temporal checks), add a Step 4b: if `dataset_type == "time_series" and n_numeric >= 5`, run `domain_pdm.compute(df, **ctx)` and append to trace.

5. **LLM review prompt enrichment:** Pass `domain_pdm` detail into the `_llm_review` prompt so the narrative surfaces domain-specific findings, not just generic scores.

---

## Dimension 1 — Sensor Coverage Adequacy

**What it checks:** Whether the sensor types required for the stated equipment class are actually present, inferred from column names.

### The Core Problem

A bearing health dataset without vibration sensors is like a cardiac dataset without ECG — structurally complete but clinically useless. Different equipment failure modes require fundamentally different physical signal types:

| Equipment / Failure Mode | Required Sensor Type(s) | Why |
|---|---|---|
| Rolling-element bearing (BPFO/BPFI/BSF faults) | Vibration (acceleration, g or mm/s²) | Fault frequencies appear as spectral sidebands at kHz range; temperature lags behind |
| Electric motor health | Current (A or mA), Vibration | Motor Current Signature Analysis (MCSA) detects rotor bar faults, eccentricity |
| Hydraulic pump | Pressure (bar/psi), Flow rate, Temperature | Pressure ripple frequency reveals pump wear; cavitation visible in pressure spikes |
| Gearbox | Vibration (triaxial), Oil temp | Gear mesh frequency = shaft RPM × number of teeth; harmonics reveal tooth wear |
| Furnace / heat treatment | Temperature (multiple zones), Gas flow, Power | Thermal gradients indicate refractory degradation or burner imbalance |
| Compressor | Pressure, Vibration, Temperature | Surge detection needs both pressure and vibration; temperature alone is insufficient |
| Rolling mill (steel-specific) | Roll force (kN), Roll gap, Temperature, Motor current | Pass schedule validation; roll wear → increasing roll force at constant gap |

Sources: [Tractian — Top 5 PdM Sensors (2026)](https://tractian.com/en/blog/top-predictive-maintenance-sensors), [f7i.ai — Sensor PdM Strategy 2026](https://f7i.ai/blog/sensor-predictive-maintenance-building-a-full-stack-reliability-strategy), [IoT Bearings — Bearing Defect Frequencies](https://iotbearings.com/bearing-defect-frequencies-bpfo-bpfi-bsf-ftf-explained/)

### Detection Logic

```python
# Keyword vocabulary for each sensor type
SENSOR_VOCAB = {
    "vibration":   ["vib", "accel", "rms", "kurtosis", "bearing", "g_rms", "vel", "displacement", "envelope"],
    "temperature": ["temp", "tmp", "therm", "celsius", "fahrenheit", "kelvin", "thr"],
    "pressure":    ["press", "psi", "bar", "kpa", "mpa"],
    "current":     ["curr", "amps", "ampere", "ia", "ib", "ic", "phase_a"],
    "speed":       ["rpm", "speed", "velocity", "shaft", "freq"],
    "flow":        ["flow", "flux", "volume_rate"],
    "force_torque":["force", "torque", "load", "kn", "nm", "roll_force", "roll_gap"],
    "power":       ["power", "kw", "watt", "energy"],
}

# Equipment class keyword → required sensor types
EQUIPMENT_COVERAGE_RULES = {
    "bearing":   {"required": ["vibration"], "recommended": ["temperature", "speed"]},
    "motor":     {"required": ["current"],   "recommended": ["vibration", "temperature"]},
    "pump":      {"required": ["pressure", "vibration"], "recommended": ["temperature", "flow"]},
    "gearbox":   {"required": ["vibration"], "recommended": ["temperature", "speed"]},
    "furnace":   {"required": ["temperature"], "recommended": ["power", "flow"]},
    "mill":      {"required": ["force_torque", "speed"], "recommended": ["temperature", "current"]},
    "compressor":{"required": ["pressure", "vibration"], "recommended": ["temperature", "speed"]},
}

def _classify_columns(df_columns):
    """Map column names to detected sensor types."""
    detected = {}
    for stype, keywords in SENSOR_VOCAB.items():
        matched = [c for c in df_columns if any(k in c.lower() for k in keywords)]
        if matched:
            detected[stype] = matched
    return detected

def _detect_equipment_class(df_columns, metadata_col=None):
    """Infer equipment class from column names or metadata."""
    col_str = " ".join(df_columns).lower()
    for equip in EQUIPMENT_COVERAGE_RULES:
        if equip in col_str:
            return equip
    return None  # Unknown; skip coverage check
```

**Score mapping:**
- All required sensors present + ≥1 recommended: 100
- All required sensors present, no recommended: 75
- 1 of N required missing: 40 (warning)
- All required missing (or equipment class undetectable): 20 (critical for known class, 50 neutral for unknown)

**Severity:** `critical` if known equipment class has 0 required sensors detected. `warning` if 1 of N required missing. `info` if all required present but no recommended. `ok` if fully covered.

**User message example:**
> "Bearing dataset detected (column names: 'bearing_temp', 'shaft_rpm') but NO vibration sensor columns found. Bearing fault frequencies (BPFO/BPFI/BSF) are only visible in vibration signals — temperature alone cannot detect early bearing failure. Add vibration/acceleration columns or this dataset cannot support bearing PdM."

---

## Dimension 2 — Sampling-Rate Adequacy

**What it checks:** Whether the inferred sampling rate is fast enough to capture the fault physics of the sensor type present.

### The Core Problem

Nyquist theorem is not optional. For bearing fault detection via envelope analysis, defect frequencies typically appear at 1–10 kHz. The Nyquist minimum is 2×f_max — so bearing vibration needs at minimum 20 kHz sampling to detect high-frequency impulse energy. A dataset sampled at 1 Hz captures none of this. For temperature sensors, 1-minute intervals are fine. The same rule does not apply — but the scorer must know which is which.

| Sensor Type | Minimum Sampling Rate | Recommended Rate | What's Missed Below Minimum |
|---|---|---|---|
| Vibration (bearing/gear) | 10 kHz (20 kHz Nyquist for 10 kHz faults) | 25.6 kHz | All bearing defect frequencies; envelope analysis impossible |
| Vibration (imbalance/misalignment) | 500 Hz | 1–5 kHz | 1× and 2× shaft harmonics resolvable; higher-order harmonics missed |
| Motor current (MCSA) | 1–5 kHz | 10 kHz | Rotor slot harmonics at 500–2000 Hz missed |
| Pressure (pump, hydraulic) | 100 Hz | 1 kHz | Pump vane pass frequency, cavitation missed |
| Temperature | 0.01 Hz (1/min) | 0.1 Hz (every 10s) | No fault-relevant dynamic — thermal lag is 100s+ |
| Speed/RPM | 10 Hz | 100 Hz | Transient speed events missed |

Sources: [IoT Bearings — Sampling Rate in Bearing Monitoring](https://iotbearings.com/why-sampling-rate-matters-bearing-vibration-monitoring/), [Vibromera — Bearing Fault Frequencies](https://vibromera.eu/glossary/bearing-fault-frequencies/), [TEEPTRAK — PdM ML Deployment 2026](https://teeptrak.com/en/predictive-maintenance-ml-deployment-2026/)

### Detection Logic

```python
def _infer_sampling_rate_hz(df, timestamp_col):
    """Infer sampling rate from median timestamp delta."""
    ts = pd.to_datetime(df[timestamp_col], errors="coerce").sort_values().dropna()
    if len(ts) < 20:
        return None
    median_delta_s = ts.diff().dropna().median().total_seconds()
    if median_delta_s <= 0:
        return None
    return round(1.0 / median_delta_s, 2)  # Hz

SAMPLING_REQUIREMENTS = {
    "vibration":    {"min_hz": 10_000, "warn_hz": 2_000,  "msg": "Bearing fault frequencies require ≥10 kHz sampling (Nyquist for 5 kHz defect harmonics)."},
    "current":      {"min_hz": 1_000,  "warn_hz": 100,    "msg": "MCSA rotor fault detection requires ≥1 kHz sampling."},
    "pressure":     {"min_hz": 100,    "warn_hz": 10,     "msg": "Pump vane pass / cavitation detection requires ≥100 Hz."},
    "temperature":  {"min_hz": 0.003,  "warn_hz": 0.0003, "msg": "Temperature sampling below 0.003 Hz (one per 5 min) may miss fast thermal transients."},
    "speed":        {"min_hz": 10,     "warn_hz": 1,      "msg": "Speed sensors below 10 Hz miss transient speed events."},
}
```

**Score mapping:**
- All detected sensor types meet recommended rate: 100
- All meet minimum but none meet recommended: 70
- At least one critical sensor type (vibration/current) below minimum: 25 (critical)
- Sampling rate cannot be determined (no timestamp): 50 neutral

**Severity:** `critical` if vibration or current columns present but inferred rate < 1 kHz (effectively unusable for fault detection). `warning` if between minimum and recommended. `ok` if meets recommended.

**User message example:**
> "Vibration columns detected ('vib_x', 'vib_y') but inferred sampling rate is 10 Hz — far below the 10 kHz minimum required to capture bearing defect frequencies. At 10 Hz sampling, all bearing fault signatures (BPFO, BPFI, BSF) are aliased out. This vibration data is structurally present but physically unusable for bearing diagnostics."

---

## Dimension 3 — Failure Representation

**What it checks:** Are there enough failure events, enough distinct failure modes covered, and are run-to-failure (RTF) trajectories complete end-to-end?

### The Core Problem

PdM models are only as good as the failure diversity they were trained on. A dataset with 1000 rows but only 2 failure events (0.2%) cannot learn the precursor signature. Equally, a dataset with 30% failure rate is not representative of real plant conditions. The sweet spot for learning is: enough failures to train on, but realistic enough to avoid class-collapse. For RTF datasets specifically, the key structure is the full trajectory from healthy → degraded → failure — any truncation destroys the shape of the degradation curve.

| Check | Threshold | Impact |
|---|---|---|
| Total failure events | < 30: critical / 30–100: warning / > 100: ok | Below 30, model cannot learn reliable precursor signatures |
| Distinct failure modes in label | < 2 modes in multi-mode dataset: warning | Model will only learn dominant mode |
| RTF trajectories present | 0 complete RTF: critical / some RTF: warning / majority complete: ok | Without RTF, RUL regression is impossible; can only do binary classification |
| Failure rate realism | < 0.5%: critical (too sparse) / 0.5–15%: ok / > 40%: warning (over-sampled/synthetic) | Below 0.5%, model never converges on minority; above 40%, distribution is synthetic |

Sources: [Predictive Maintenance RUL (Academia.edu)](https://www.academia.edu/164859368/Predictive_Maintenance_of_Manufacturing_Industry_Machines_Using_Remaining_Useful_Life_RUL_Prediction), [Semi-Supervised Monotonic Constraints for RUL (PMC)](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8880416/)

### Detection Logic

```python
def _check_failure_representation(df, label_col, rul_col=None):
    """
    label_col: binary failure label (0=healthy, 1=failure/fault)
    rul_col: if present, check for RTF structure
    """
    results = {}
    
    if label_col and label_col in df.columns:
        series = df[label_col].dropna()
        failure_mask = series.isin([1, True, "failure", "Failure", "FAIL"])
        n_failures = int(failure_mask.sum())
        n_total = len(series)
        failure_rate = n_failures / max(n_total, 1)
        results["n_failures"] = n_failures
        results["failure_rate_pct"] = round(failure_rate * 100, 2)
    
    if rul_col and rul_col in df.columns:
        # RTF detection: does RUL reach 0 for any asset?
        rul_series = df[rul_col].dropna()
        n_zero_rul = int((rul_series == 0).sum())
        # Monotonicity per asset_id group if available
        results["n_rtf_endpoints"] = n_zero_rul
        
        # Check monotonicity violations
        if "asset_id" in df.columns or "machine_id" in df.columns:
            id_col = "asset_id" if "asset_id" in df.columns else "machine_id"
            violations = 0
            for _, group in df.groupby(id_col):
                rul_vals = group[rul_col].dropna().values
                if len(rul_vals) > 1:
                    diffs = np.diff(rul_vals)
                    # In a proper RTF trajectory, RUL should generally decrease
                    # Allow up to 5% non-monotonic steps (sensor noise, cycle resets)
                    n_increases = int((diffs > 1).sum())  # increases > 1 unit are violations
                    if n_increases / max(len(diffs), 1) > 0.10:
                        violations += 1
            results["monotonicity_violations"] = violations
    
    return results
```

**Score mapping (composite sub-score for this check alone):**
- n_failures >= 100, RTF present, failure_rate 0.5–15%, 0 monotonicity violations: 100
- n_failures 30–100, some RTF, failure_rate ok: 75
- n_failures < 30 or 0 RTF trajectories: 30 (critical)
- failure_rate < 0.5%: 25 (critical — statistically unlearnable without synthetic augmentation)
- failure_rate > 40% AND RUL present (suggests synthetic/upsampled): 40 (warning)

**User message example:**
> "Only 8 failure events found in 4,200 rows (0.19% failure rate). PdM models cannot learn reliable precursor signatures from fewer than 30 failure instances — the minority class is statistically unrepresented. Additionally, no run-to-failure trajectories detected (RUL column never reaches 0), meaning RUL regression is not feasible with this data. Recommended: augment with SMOTE-Tomek or source additional failure episodes."

---

## Dimension 4 — Class Imbalance Realism (PdM Context)

**What it checks:** Whether the imbalance ratio is realistic for PdM (and thus accepted) versus artificially sparse (dataset problem) or artificially balanced (synthetic noise).

### The Core Problem

Generic `class_balance.py` penalises IR=50:1 heavily (score ~6). But in PdM, IR=50:1 (2% failure rate) is NORMAL and expected — it reflects the real world. Penalising this is wrong. The question is NOT "is the dataset balanced?" but rather:
- Is it balanced enough to train a model at all? (minimum event count)
- Is the imbalance *representative* (real plant failure rate, ~1–5%) or *artificial* (poorly collected, <0.1%)?
- Has the dataset been synthetically balanced to the point of introducing unrealistic failure representation (>40%)?

The existing `class_balance.py` score penalises realistic PdM imbalance. The domain layer must OVERRIDE this for PdM contexts with a re-calibrated scoring curve.

| Failure Rate | Generic Score Penalty | Domain Interpretation | Domain Adjustment |
|---|---|---|---|
| 0–0.5% | Heavy penalty | Too sparse — model cannot converge | Keep penalty (critical) |
| 0.5–5% | Heavy penalty (IR=20–200:1) | REALISTIC plant failure rate | Override to 80+ (ok — no correction needed) |
| 5–15% | Moderate penalty | Slightly high but typical of collected datasets | Override to 70+ (info) |
| 15–40% | Mild penalty | Over-collected or partially synthetic | Keep mild penalty (warning) |
| >40% | Low penalty in generic | Unrealistic — fully synthetic upsampling | Penalise (warning) |

### Detection Logic

```python
DOMAIN_IMBALANCE_OVERRIDE = {
    # (min_rate, max_rate): (domain_score, domain_severity, message)
    (0.0,    0.005): (20.0, "critical", "Failure rate <0.5%: too sparse for model convergence. Use SMOTE or collect more failure episodes."),
    (0.005,  0.05):  (90.0, "ok",       "Failure rate {rate:.1f}%: realistic for industrial PdM (IR={ir:.0f}:1). No resampling needed — use class_weight='balanced'."),
    (0.05,   0.15):  (75.0, "info",     "Failure rate {rate:.1f}%: slightly elevated but within acceptable PdM range. Consider stratified CV."),
    (0.15,   0.40):  (55.0, "warning",  "Failure rate {rate:.1f}%: higher than typical plant data. May indicate over-collection or partial synthetic augmentation."),
    (0.40,   1.0):   (40.0, "warning",  "Failure rate {rate:.1f}%: unrealistically high for industrial PdM. Dataset likely heavily over-sampled or synthetic."),
}
```

**Integration:** The domain module computes a `pdm_imbalance_override` sub-score that REPLACES `class_balance` score in the composite when dataset is time-series + sensor + PdM context. This prevents the generic imbalance penalty from unfairly downgrading a good PdM dataset with realistic 2% failure rate.

**User message example:**
> "Failure rate is 1.8% (IR=55:1) — this is REALISTIC for industrial predictive maintenance and does NOT indicate a dataset problem. Generic imbalance warnings are overridden for PdM datasets. Use class_weight='balanced' in your model; no resampling required."

---

## Dimension 5 — Temporal Coverage for Degradation

**What it checks:** Is there enough chronological history to capture the full degradation arc from healthy to failure? Are multiple operational modes and seasonal periods represented?

### The Core Problem

The existing `temporal_coverage.py` checks gap fraction and ADF stationarity. What it does NOT check:
- Is the time span long enough to capture equipment degradation (typically 30–180+ days for steel plant machinery)?
- Are there multiple distinct failure episodes (not just one), enabling the model to generalize?
- Is the pre-failure window (the "prognostic horizon") preserved — i.e., are there N hours/days of data leading up to each failure event?
- [unverified: ISO 13381-1 recommends sufficient data to span at least 3 complete failure cycles for reliability of RUL models]

| Check | Threshold | Score Impact |
|---|---|---|
| Total time span | < 30 days: critical / 30–90 days: warning / > 90 days: ok | Short span can't capture slow degradation |
| Number of distinct failure episodes | < 3: critical / 3–10: warning / > 10: ok | Too few episodes = overfitting single failure path |
| Pre-failure window coverage | < 24h before each failure event: warning | No lead time = cannot build an early-warning model |
| Post-maintenance / healthy-baseline coverage | < 20% of data is clearly healthy (RUL near max): warning | Model can't learn healthy baseline |

### Detection Logic

```python
def _check_temporal_degradation_coverage(df, timestamp_col, label_col=None, rul_col=None):
    ts = pd.to_datetime(df[timestamp_col], errors="coerce").sort_values().dropna()
    total_span_days = (ts.iloc[-1] - ts.iloc[0]).total_seconds() / 86400
    
    results = {"total_span_days": round(total_span_days, 1)}
    
    if label_col and label_col in df.columns:
        failure_times = df.loc[df[label_col].isin([1, True, "failure"]), timestamp_col]
        failure_times = pd.to_datetime(failure_times, errors="coerce").dropna()
        n_episodes = len(failure_times)
        results["n_failure_episodes"] = n_episodes
        
        # Check pre-failure window: median gap between last failure and its predecessor
        if len(failure_times) > 0 and len(ts) > 0:
            # For each failure, find the earliest timestamp in that session
            # Simplified: check if there are rows in the 24h window before each failure
            prewindow_coverage = []
            for ft in failure_times:
                window_start = ft - pd.Timedelta(hours=24)
                rows_in_window = df[
                    (pd.to_datetime(df[timestamp_col], errors="coerce") >= window_start) &
                    (pd.to_datetime(df[timestamp_col], errors="coerce") < ft)
                ]
                prewindow_coverage.append(len(rows_in_window) > 0)
            results["failures_with_prewindow_pct"] = round(sum(prewindow_coverage) / max(len(prewindow_coverage), 1) * 100, 1)
    
    if rul_col and rul_col in df.columns:
        rul_series = df[rul_col].dropna()
        max_rul = float(rul_series.max())
        healthy_pct = float((rul_series > max_rul * 0.7).mean() * 100)
        results["healthy_baseline_pct"] = round(healthy_pct, 1)
    
    return results
```

**Score mapping:**
- span ≥ 90 days, ≥ 10 episodes, pre-failure window present, healthy baseline ≥ 20%: 95
- span 30–90 days, 3–10 episodes: 70
- span < 30 days OR < 3 episodes OR 0 pre-failure windows: 30 (critical)

**User message example:**
> "Dataset spans only 12 days and contains 1 failure episode. Industrial degradation processes in steel plant equipment (rolling mill bearings, drive motors) typically develop over 30–180 days. A 12-day window is insufficient to capture precursor signatures — the model will see only the final failure event, not the degradation arc. Extend historical collection or augment with synthetic degradation trajectories."

---

## Dimension 6 — Label Quality for PdM (Time-Alignment + RUL Monotonicity)

**What it checks:** Are failure labels temporally aligned with actual events (not logged 48h late)? Are anomaly windows correctly bounded (not 2 weeks wide)? Is the RUL column monotonically decreasing within each asset's trajectory?

### The Core Problem

The existing `label_quality.py` detects statistical mislabels via cross-validation disagreement. It cannot detect *temporal misalignment* — a common and catastrophic problem in industrial datasets where failure is logged when the work order was closed (24–72 hours after actual failure onset). A model trained on 72h-late labels learns the WRONG precursor window and fails in production.

| Label Quality Issue | Detection Method | Threshold | Score Penalty |
|---|---|---|---|
| Failure label clustering (event-at-timestamp vs. batch-logged) | Check time-delta distribution between consecutive failure rows | If >30% of failures are on the same timestamp or within 1 minute: warning (batch logging) | −15 pts |
| RUL non-monotonicity | Per-asset group: count timesteps where RUL increases by >1 unit | > 10% non-monotonic steps per asset: warning; > 30%: critical | −20 pts |
| Anomaly window width (if anomaly_start/anomaly_end columns present) | Median window width vs. known fault onset-to-failure times | Median window > 7 days: warning (too wide — model can't learn precise onset) | −10 pts |
| RUL range sanity | Max RUL > 1000 cycles/hours for short run-to-failure datasets | If max_rul > 5× median failure duration: warning [unverified: threshold depends heavily on equipment type] | −10 pts |
| Label completeness at failure horizon | Are labels present for all rows near failure events (±5 timesteps)? | > 10% missing labels in ±5 window around failures: critical | −20 pts |

### Detection Logic

```python
def _check_pdm_label_quality(df, label_col, rul_col=None, timestamp_col=None):
    issues = []
    penalty = 0.0
    
    if timestamp_col and label_col and label_col in df.columns:
        # Check for batch-logged failures (multiple failures at same timestamp)
        failure_rows = df[df[label_col].isin([1, True, "failure"])]
        if len(failure_rows) > 0 and timestamp_col in failure_rows.columns:
            failure_ts = pd.to_datetime(failure_rows[timestamp_col], errors="coerce")
            ts_counts = failure_ts.value_counts()
            batch_fraction = float((ts_counts > 1).sum()) / max(len(ts_counts), 1)
            if batch_fraction > 0.30:
                issues.append(f"Batch-logged failures detected ({batch_fraction*100:.0f}% of failure timestamps have multiple co-incident events — suggests administrative logging, not real-time sensor capture)")
                penalty += 15.0
    
    if rul_col and rul_col in df.columns:
        # Monotonicity check per asset
        id_col = next((c for c in ["asset_id", "machine_id", "unit_number", "engine_id"] if c in df.columns), None)
        if id_col:
            non_monotone_assets = 0
            total_assets = 0
            for _, group in df.groupby(id_col):
                total_assets += 1
                rul_vals = group.sort_values(timestamp_col)[rul_col].dropna().values if timestamp_col in group else group[rul_col].dropna().values
                if len(rul_vals) > 1:
                    diffs = np.diff(rul_vals.astype(float))
                    n_increase = int((diffs > 1.0).sum())
                    if n_increase / max(len(diffs), 1) > 0.10:
                        non_monotone_assets += 1
            
            if total_assets > 0:
                nm_rate = non_monotone_assets / total_assets
                if nm_rate > 0.30:
                    issues.append(f"RUL non-monotonic in {non_monotone_assets}/{total_assets} assets (>30% of assets show RUL increasing mid-trajectory — indicates labeling error or cycle-reset artifact)")
                    penalty += 20.0
                elif nm_rate > 0.10:
                    issues.append(f"RUL non-monotonic in {non_monotone_assets}/{total_assets} assets — minor inconsistency, may be sensor noise or maintenance resets")
                    penalty += 8.0
        
        # RUL range sanity
        rul_max = float(df[rul_col].max())
        if rul_max > 5000:
            issues.append(f"Max RUL = {rul_max:.0f} — unusually high; verify units (cycles vs hours vs minutes)")
            penalty += 5.0
    
    score = max(0.0, min(100.0, 100.0 - penalty))
    return {"score": score, "issues": issues, "penalty": round(penalty, 1)}
```

**Severity:** `critical` if RUL non-monotonicity > 30% of assets or batch-logged failures > 30%. `warning` if any single issue present at lower threshold. `ok` if all checks pass.

**User message example:**
> "RUL column shows non-monotonic values in 4 of 5 assets: RUL increases multiple times mid-trajectory, which is physically impossible during uninterrupted degradation. This indicates either a labeling error (RUL was recalculated at a wrong reference point) or un-flagged maintenance resets that changed the degradation baseline. Models trained on this data will predict inconsistent RUL values. Fix by re-aligning RUL per maintenance window."

---

## Dimension 7 — Sensor Health (Stuck Sensors, Drift, Saturation)

**What it checks:** Are any sensor channels stuck (constant or near-constant), drifting (systematic linear trend without physical cause), saturated (clipped at hardware limit), or producing physically impossible values?

### The Core Problem

`distribution_sanity.py` already catches constant columns and infinite values. The domain layer adds physics-aware checks that `distribution_sanity` cannot perform without domain knowledge.

| Sensor Fault | Detection Method | Physical Cause | Score Penalty |
|---|---|---|---|
| Stuck sensor | Rolling std over 50-sample window ≈ 0 for > 5% of timeline | Connector loose, firmware freeze, ADC failure | −15 pts per stuck channel |
| Hard saturation | Value distribution has spike at min or max (> 5% of readings at exact boundary) | ADC clipping at 0V or VREF | −10 pts per saturated channel |
| Soft saturation | Values cluster above 95th percentile for >10% of readings | Physical or electronic range exceedance | −5 pts per soft-saturated channel |
| Linear drift > 3σ/week | OLS slope over time > 3× baseline σ per week | Sensor contamination, mounting shift, thermal expansion | −10 pts per drifting channel |
| Physically impossible values | Value outside known physical range for that sensor type | See table below | −20 pts (critical) |

**Physically impossible value ranges (steel plant context):**

| Sensor Type | Impossible Range | Correct Range (typical) | Source |
|---|---|---|---|
| Temperature (°C, ambient/equipment) | < −50°C or > 1700°C | −10 to 1600°C (smelting = ~1600°C, ambient = 10–50°C) | Steel process engineering reference [unverified: verify for specific process] |
| Vibration RMS (g) | < 0 g or > 500 g for rotating machinery | 0.1–100 g typical; > 100 g = impending catastrophic failure | ISO 10816-3 [unverified: exact limits vary by machine class] |
| Rotational speed (RPM) | < 0 or > 50,000 RPM for most steel plant drives | 0–5,000 RPM for large drives; up to 30,000 for small motors | |
| Pressure (bar) | < −1 bar (below full vacuum) or > 1000 bar for standard lines | 0–350 bar typical hydraulic; 0–10 bar pneumatic | |
| Motor current (A) | < 0 A | 0–10,000 A for large drives | |

Sources: [APERIO — Sensor Drift Detection](https://aperio.ai/sensor-drift/), [MDPI — Drift Detection in Process Plants](https://www.mdpi.com/2073-4441/14/6/926), [IEEE — Sensor Drift Detection in SNG Plants](https://ieeexplore.ieee.org/document/8088327/)

### Detection Logic

```python
PHYSICAL_RANGE_RULES = {
    "temperature": {"min": -50, "max": 1700, "unit": "°C"},
    "vibration":   {"min": 0,   "max": 500,  "unit": "g (RMS)"},
    "pressure":    {"min": -1,  "max": 1000, "unit": "bar"},
    "speed":       {"min": 0,   "max": 50000, "unit": "RPM"},
    "current":     {"min": 0,   "max": 10000, "unit": "A"},
}

def _detect_stuck_channels(df, sensor_cols, window=50, stuck_threshold=0.95):
    """Rolling window: fraction of time where std ≈ 0."""
    stuck = []
    for col in sensor_cols:
        if col not in df.columns:
            continue
        series = df[col].dropna().astype(float)
        if len(series) < window * 2:
            continue
        rolling_std = series.rolling(window).std()
        near_zero_frac = float((rolling_std < 1e-6).mean())
        if near_zero_frac > 0.05:  # stuck more than 5% of the time
            stuck.append({"col": col, "stuck_frac": round(near_zero_frac, 3)})
    return stuck

def _detect_saturation(df, sensor_cols):
    saturated = []
    for col in sensor_cols:
        if col not in df.columns:
            continue
        series = df[col].dropna().astype(float)
        if len(series) < 20:
            continue
        col_min, col_max = series.min(), series.max()
        at_min = float((series == col_min).mean())
        at_max = float((series == col_max).mean())
        if at_min > 0.05 or at_max > 0.05:
            saturated.append({
                "col": col,
                "at_min_pct": round(at_min*100, 1),
                "at_max_pct": round(at_max*100, 1),
            })
    return saturated
```

**Score mapping (per-channel penalties, compound):**
- 0 stuck channels, 0 saturated, 0 impossible values: 100
- 1–2 issues across all channels: 75 (info/warning)
- Any impossible value range detected: 40 (critical) — signals fundamental data quality problem
- > 20% of channels stuck or saturated: 30 (critical)

**User message example:**
> "Sensor 'bearing_temp_2' is stuck (constant value 23.4°C for 94% of the timeline). Stuck sensors produce no information — any model relying on this column will learn a spurious constant feature. Additionally, 'vib_rms_motor1' shows 6.1% of readings at exact maximum value (500g), indicating ADC saturation — real values above 500g are clipped. Both channels should be removed or replaced before model training."

---

## Dimension 8 — Operating-Condition Metadata

**What it checks:** Are asset_id / equipment_class / process-stage metadata columns present? Without these, a model trained on mixed equipment types learns a conflated signal and generalizes to nothing.

### The Core Problem

Steel plants run dozens of equipment classes under different operating conditions (loaded/unloaded, high-speed rolling pass vs. idle, summer vs. winter ambient). A dataset without asset identity or operating condition context forces the model to treat a heavily loaded bearing the same as a just-maintained idle one — this is the single largest source of false positives in deployed PdM systems. ISA-95 and ISO 14224 both mandate this hierarchy for reliability data.

Sources: [Component 14 Research Brief — ISA-95 + ISO 14224 alignment](../14_unified-data-schema.md)

| Metadata Column | Why Required | Detection Heuristic |
|---|---|---|
| `asset_id` / `machine_id` / `unit_number` | Without it, temporal sequences from different machines are interleaved — RUL regression is meaningless | Look for low-cardinality string/int column (2–500 unique values) that isn't a label |
| `equipment_class` / `machine_type` | Needed to apply equipment-specific physical range rules; needed for per-class model routing | String column with < 20 unique values |
| `operating_mode` / `load_level` / `op_setting` | Sensor readings vary 3–5× between high-load and low-load — without mode flag, model sees phantom anomalies at mode transitions | Numeric or categorical column with < 10 distinct values |
| `process_stage` | Steel-specific: hot rolling vs. cold rolling vs. annealing have totally different thermal/vibration profiles | String column matching known process vocabulary |

### Detection Logic

```python
METADATA_VOCAB = {
    "asset_id":        ["asset", "machine", "unit", "engine", "device", "equipment_id", "asset_id", "id"],
    "equipment_class": ["type", "class", "category", "model", "machine_type", "equip_class"],
    "operating_mode":  ["mode", "op_setting", "load", "condition", "state", "regime", "setting"],
    "process_stage":   ["stage", "process", "phase", "step", "zone", "pass"],
}

def _check_metadata_presence(df):
    found = {}
    for meta_type, keywords in METADATA_VOCAB.items():
        matched = [c for c in df.columns if any(k in c.lower() for k in keywords)]
        # Filter out label/RUL columns
        matched = [c for c in matched if not any(x in c.lower() for x in ["rul", "failure", "fault", "label", "target"])]
        if matched:
            found[meta_type] = matched[0]  # take first match
    return found

# Scoring:
# 4 metadata types found: 100
# 3 found (must include asset_id): 80
# 2 found: 60
# Only asset_id found: 50 (warning — minimal context)
# None found: 25 (critical)
```

**Score mapping:**
- All 4 metadata types present: 100
- 3 present (including asset_id): 80 (ok)
- 2 present: 60 (info)
- Only 1 (asset_id alone): 45 (warning)
- 0 metadata: 25 (critical)

**Hard cap:** If `asset_id` is absent and dataset has multiple sequential runs (detected by RUL resetting to max mid-timeline), composite score is capped at 60 — the data is structurally ambiguous for per-asset modeling.

**User message example:**
> "No asset_id column detected. This dataset appears to contain sensor readings from multiple pieces of equipment interleaved without identity tags. Without asset_id, RUL trajectories from different machines are blended — a model cannot distinguish 'machine A at day 45 of degradation' from 'machine B at day 2.' Add asset_id or equipment identifiers as the single highest-priority metadata fix."

---

## Composite Integration Plan

### New TIME_SERIES_WEIGHTS (updated)

```python
TIME_SERIES_WEIGHTS = {
    "completeness":        0.12,   # unchanged
    "class_balance":       0.05,   # reduced — domain_pdm overrides for PdM
    "label_quality":       0.08,   # reduced — domain_pdm adds PdM-specific checks
    "duplicates":          0.06,   # unchanged
    "outliers":            0.05,   # reduced — sensor health check in domain_pdm
    "schema_validity":     0.07,   # unchanged
    "leakage":             0.10,   # unchanged
    "temporal_coverage":   0.18,   # reduced slightly (domain adds degradation arc check)
    "feature_redundancy":  0.05,   # reduced
    "distribution_sanity": 0.05,   # reduced — domain covers physical range sanity
    "domain_pdm":          0.19,   # NEW — highest single weight for sensor time-series
}
# Total = 1.00
```

### Sub-Score Composition for domain_pdm

The `domain_pdm` dimension returns a single composite score from the 8 checks with internal weights:

```python
DOMAIN_PDM_INTERNAL_WEIGHTS = {
    "sensor_coverage":      0.20,  # Most impactful: wrong sensor type = useless data
    "sampling_rate":        0.20,  # Equally impactful: wrong rate = aliased data
    "failure_representation": 0.18, # Core PdM requirement
    "pdm_imbalance":        0.10,  # Calibrated for PdM reality
    "temporal_degradation": 0.12,  # Degradation arc quality
    "pdm_label_quality":    0.10,  # Time-alignment + monotonicity
    "sensor_health":        0.05,  # Stuck/drift/saturation
    "metadata_coverage":    0.05,  # Asset ID + operating context
}
```

### Hard Caps (domain-specific additions to composite.py)

```python
# Add to compute_composite() in composite.py:

# Domain PdM cap: if domain_pdm present and critical → composite capped at 55
domain_r = sub_scores.get("domain_pdm", {})
if domain_r.get("score", 100) < 30:
    raw_composite = min(raw_composite, 50.0)
    cap_reasons.append(
        "Score capped at 50 due to critical domain quality failure "
        "(missing required sensors, sub-Nyquist sampling, or zero failure events). "
        "This dataset cannot support predictive maintenance modeling in its current state."
    )
```

---

## Summary Table — All 8 Domain Dimensions

| # | Dimension | Maps To Existing | Weight in domain_pdm | Detection Method | P0 Threshold | User Message Theme |
|---|---|---|---|---|---|---|
| 1 | Sensor Coverage | distribution_sanity (partial) | 20% | Column name vocabulary matching vs. equipment class | 0 required sensors for known equipment class | "Bearing dataset with no vibration columns" |
| 2 | Sampling Rate | temporal_coverage (partial) | 20% | Median timestamp delta → Hz; compare to Nyquist for sensor type | Vibration < 1 kHz | "Vibration sampled at 10 Hz — bearing faults invisible" |
| 3 | Failure Representation | class_balance + label_quality | 18% | Count failure events, RUL=0 endpoints, per-mode counts | n_failures < 30 OR 0 RTF trajectories | "8 failure events — statistically unlearnable" |
| 4 | PdM Imbalance Realism | class_balance (overrides) | 10% | Failure rate → domain-calibrated curve | failure_rate < 0.5% | "1.8% failure rate is realistic — not a problem" |
| 5 | Temporal Degradation Arc | temporal_coverage | 12% | Span days, episode count, pre-failure window, healthy baseline | span < 30d OR < 3 episodes | "12-day span can't capture slow bearing degradation" |
| 6 | PdM Label Quality | label_quality | 10% | RUL monotonicity per asset; batch-log detection; window width | > 30% assets non-monotonic | "RUL increases mid-trajectory in 4/5 assets" |
| 7 | Sensor Health | distribution_sanity | 5% | Rolling-std stuck check; saturation; physical range rules | Any impossible value; > 20% channels stuck | "bearing_temp_2 stuck at 23.4°C for 94% of timeline" |
| 8 | Operating Metadata | schema_validity (partial) | 5% | Vocabulary matching for asset_id, class, mode, stage | No asset_id in multi-run dataset | "No asset_id: multi-machine data is ambiguous" |

---

## File to Create: `scorer/dimensions/domain_pdm.py`

The implementation stub to be filled from this spec:

```python
"""
Domain-specific PdM quality checks for steel-plant sensor datasets.
Activates when: dataset_type == "time_series" and n_numeric_cols >= 5.
Returns a single DimensionResult-compatible dict with sub-scores in raw{}.
"""

from __future__ import annotations
import pandas as pd
import numpy as np
from typing import Any, Dict, Optional

# --- Vocabulary tables (from this spec) ---
SENSOR_VOCAB = { ... }
EQUIPMENT_COVERAGE_RULES = { ... }
SAMPLING_REQUIREMENTS = { ... }
PHYSICAL_RANGE_RULES = { ... }
METADATA_VOCAB = { ... }
DOMAIN_PDM_INTERNAL_WEIGHTS = { ... }

def compute(
    df: pd.DataFrame,
    label_col: Optional[str] = None,
    timestamp_col: Optional[str] = None,
    rul_col: Optional[str] = None,  # auto-detected if None
    **ctx,
) -> Dict[str, Any]:
    """
    Returns same shape as all other dimension modules:
    {"score": float, "detail": str, "severity": str, "raw": dict}
    """
    n_numeric = df.select_dtypes(include=[np.number]).shape[1]
    if n_numeric < 5:
        return {
            "score": 50.0,
            "detail": "Fewer than 5 numeric columns — domain PdM checks not applicable.",
            "severity": "info",
            "raw": {"skipped": True, "reason": "insufficient_numeric_cols"},
        }
    
    # Auto-detect RUL column if not provided
    if rul_col is None:
        rul_candidates = [c for c in df.columns if any(k in c.lower() for k in ["rul", "remaining", "ttf", "time_to_fail"])]
        rul_col = rul_candidates[0] if rul_candidates else None
    
    detected_sensors = _classify_columns(df.columns.tolist())
    equipment_class  = _detect_equipment_class(df.columns.tolist())
    
    sub = {}
    
    # Run all 8 checks ...
    # [full implementation follows this spec]
    
    # Weighted composite
    total_w = sum(DOMAIN_PDM_INTERNAL_WEIGHTS.values())
    composite = sum(sub[k]["score"] * DOMAIN_PDM_INTERNAL_WEIGHTS[k] for k in sub if k in DOMAIN_PDM_INTERNAL_WEIGHTS) / total_w
    
    # Severity escalation
    critical_dims = [k for k, v in sub.items() if v["severity"] == "critical"]
    severity = "critical" if critical_dims else ("warning" if any(v["severity"] == "warning" for v in sub.values()) else "ok")
    
    detail = _build_detail_string(sub, equipment_class, detected_sensors, composite)
    
    return {
        "score": round(composite, 2),
        "detail": detail,
        "severity": severity,
        "raw": {"sub_checks": sub, "equipment_class": equipment_class, "detected_sensors": list(detected_sensors.keys())},
    }
```

---

## References

- [Sensor Predictive Maintenance: Full-Stack Strategy 2026 — f7i.ai](https://f7i.ai/blog/sensor-predictive-maintenance-building-a-full-stack-reliability-strategy)
- [PdM ML Deployment 2026: ISO 17359, ISO 13374 — TEEPTRAK](https://teeptrak.com/en/predictive-maintenance-ml-deployment-2026/)
- [Bearing Defect Frequencies BPFO/BPFI/BSF/FTF — IoT Bearings](https://iotbearings.com/bearing-defect-frequencies-bpfo-bpfi-bsf-ftf-explained/)
- [Why Sampling Rate Matters in Bearing Vibration Monitoring — IoT Bearings](https://iotbearings.com/why-sampling-rate-matters-bearing-vibration-monitoring/)
- [Bearing Fault Frequencies: Formulas — Vibromera](https://vibromera.eu/glossary/bearing-fault-frequencies/)
- [Top 5 PdM Sensors 2026 — Tractian](https://tractian.com/en/blog/top-predictive-maintenance-sensors)
- [Semi-Supervised Monotonic Constraints for RUL (PMC8880416)](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8880416/)
- [Sensor Drift Detection — APERIO AI](https://aperio.ai/sensor-drift/)
- [Data-Driven Drift Detection in Real Process Tanks — MDPI Water](https://www.mdpi.com/2073-4441/14/6/926)
- [Sensor Drift Detection in SNG Plant — IEEE Xplore](https://ieeexplore.ieee.org/document/8088327/)
- [Component 13: Public PdM Dataset Selection (C-MAPSS + AI4I)](../13_public-pdm-datasets.md)
- [Component 14: Unified Data Schema (ISA-95 + ISO 14224)](../14_unified-data-schema.md)

---

*Items tagged [unverified] indicate claims that are directionally correct per domain reasoning but whose exact numeric thresholds lack direct citation and should be validated against ISO 13373, ISO 10816, or Tata Steel internal maintenance standards before hardcoding into the scorer.*

*Document status: research complete, implementation-ready. Next step: `scorer/dimensions/domain_pdm.py` implementation sprint.*
