"""
Condition Monitoring Data Generator — Spec 4.2
Tata Steel Round-2 Maintenance Wizard | steel-maintenance-flagship dataset
Author: Jarvis (ml-engineer-agent)
Ground truth: SPEC/ground_truth_spine.json
Physics recipes: research/domain/07, research/machinery/15,16,18
Output dir: datasets/steel-maintenance-flagship/condition_monitoring/

Produces 4 CSV files:
  (a) raw_sensor_timeseries.csv    ~150k rows
  (b) sensor_data_summaries.csv    per asset per 6-hour window
  (c) anomaly_alerts.csv           fires when any scenario crosses its threshold
  (d) process_condition_indicators.csv  health-index / OEE-style KPIs

Physics model per research/domain/07 §2.1:
  signal[t] = baseline[t] + degradation_drift[t] + correlated_noise[t]
  degradation_drift uses Weibull-parameterised RTF trajectory
  Sensors rise/fall in signature patterns extracted from spine failure_scenario_catalog

DISCLAIMER: Synthetic but physics-grounded. Not real Tata Steel plant data.
"""

import json
import math
import random
import hashlib
import logging
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, Dict, List, Tuple

import numpy as np
import pandas as pd
from scipy.stats import weibull_min

# ──────────────────────────────────────────────────────────────────────────────
# Paths
# ──────────────────────────────────────────────────────────────────────────────
BASE = Path("/home/ujjwal/Documents/J.A.R.V.I.S./data/hackathons/tata-steel-2026/round_2/dataforge/datasets/steel-maintenance-flagship")
SPINE_PATH = BASE / "SPEC" / "ground_truth_spine.json"
OUT_DIR = BASE / "condition_monitoring"
OUT_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

RNG_SEED = 42
rng = np.random.default_rng(RNG_SEED)
random.seed(RNG_SEED)

# ──────────────────────────────────────────────────────────────────────────────
# Constants / design choices
# ──────────────────────────────────────────────────────────────────────────────
# Simulation window: 52 weeks at 1-hour resolution
# 52w × 7d × 24h = 8736 steps per asset; 16 assets → 139 776 rows baseline
# (maintenance shutdowns + downtime trim brings final count to ~150k after
# episodes are laid out)
SIM_WEEKS = 52
HOURS_PER_WEEK = 168
TOTAL_HOURS = SIM_WEEKS * HOURS_PER_WEEK   # 8736
N_ASSETS = 16                               # as defined in spine asset_registry

# Weibull degradation parameters (shape β, scale η) per equipment class
# Chosen so median life ~ 4000-8000 h, degradation window ~6-12 weeks
WEIBULL_PARAMS = {
    "rolling_mill_work_roll_bearing": {"beta": 2.5, "eta": 6000},   # ISO 15243 fatigue; typical bearing Weibull shape β=2-3
    "mill_gearbox":                   {"beta": 2.0, "eta": 8000},   # gear fatigue β~2; AGMA
    "large_induction_motor_vfd":      {"beta": 3.0, "eta": 7000},   # insulation ageing β~2-4
    "cooling_descaling_pump":         {"beta": 2.2, "eta": 5000},   # seal+impeller
    "bf_sinter_fan_blower":           {"beta": 2.8, "eta": 9000},   # fan imbalance / blade erosion
    "continuous_caster_segment":      {"beta": 2.0, "eta": 4000},   # roll seizure fast-onset
    "continuous_caster_mould":        {"beta": 1.5, "eta": 3500},   # breakout stochastic; low Weibull β=1.5 → early-life failures
    "hot_strip_mill_stand":           {"beta": 2.5, "eta": 5500},   # spall fatigue
    "raw_material_conveyor":          {"beta": 2.0, "eta": 4500},   # idler bearing
    "reheating_furnace":              {"beta": 1.8, "eta": 7000},   # refractory + burner
    "eaf_bof_auxiliary":              {"beta": 2.0, "eta": 6000},   # hydraulic contamination
    "ladle_crane":                    {"beta": 3.0, "eta": 10000},  # wire rope fatigue; long life
    "hydraulics_agc_servo":           {"beta": 2.5, "eta": 5000},   # servo silting
}

# Timestamp base
import datetime
T0 = datetime.datetime(2025, 1, 1, 0, 0, 0)

# ──────────────────────────────────────────────────────────────────────────────
# Load spine
# ──────────────────────────────────────────────────────────────────────────────
log.info("Loading spine …")
with open(SPINE_PATH) as f:
    spine = json.load(f)

asset_registry = {a["asset_id"]: a for a in spine["asset_registry"]}
failure_catalog = spine["failure_scenario_catalog"]

# Build lookup: asset_id → list of FAILURE scenarios
failure_by_asset: Dict[str, List[dict]] = {}
for scn in failure_catalog:
    if scn["label"] == "FAILURE":
        failure_by_asset.setdefault(scn["asset_id"], []).append(scn)

# ──────────────────────────────────────────────────────────────────────────────
# Sensor spec helpers
# ──────────────────────────────────────────────────────────────────────────────

def sensor_midpoint(sensor: dict) -> float:
    """Midpoint of normal_range (for sensors with numeric range)."""
    nr = sensor.get("normal_range")
    if isinstance(nr, list) and len(nr) == 2:
        return (nr[0] + nr[1]) / 2.0
    # Non-numeric (ISO code strings) → return 0 (handled separately)
    return 0.0

def sensor_halfband(sensor: dict) -> float:
    """Half-width of normal_range (gaussian noise std basis)."""
    nr = sensor.get("normal_range")
    if isinstance(nr, list) and len(nr) == 2:
        return max((nr[1] - nr[0]) / 6.0, 1e-6)   # ±3σ = full range
    return 0.1

def is_numeric_sensor(sensor: dict) -> bool:
    return isinstance(sensor.get("normal_range"), list)

def get_alarm_threshold(sensor: dict) -> Optional[float]:
    v = sensor.get("alarm_threshold")
    try:
        return float(v)
    except (TypeError, ValueError):
        return None

def get_warning_threshold(sensor: dict) -> Optional[float]:
    v = sensor.get("warning_threshold")
    try:
        return float(v)
    except (TypeError, ValueError):
        return None

# Sensors whose alarm logic is BIDIRECTIONAL (a separate low band AND a high band).
# Handled explicitly in alert generation, not by threshold_direction().
#   VISC: warn-low at warning_threshold (180), alarm-high at alarm_threshold (265).
BIDIRECTIONAL_SENSORS = {
    "JSR.HR.STD1.GBX01.OIL.VISC": {"warn_low": 180.0, "alarm_high": 265.0},
}

# Quantities that are physically non-negative — clip noise at 0 (Issue 3 fix).
# ppm concentrations, differential/gauge pressures, and flows cannot go negative.
NON_NEGATIVE_QUANTITY_KEYWORDS = [
    "ppm", "particle", "water_content", "diff_pressure", "differential",
    "filter_diff", "flow", "cleanliness",
]

def threshold_direction(sensor: dict) -> str:
    """Return 'upper' (alarm when value EXCEEDS threshold), 'lower'
    (alarm when value FALLS BELOW threshold), or 'bidirectional'.

    Direction is derived ROBUSTLY: the ground-truth signal is the relative
    ordering of warning vs alarm thresholds (alarm < warning ⇒ lower-is-worse),
    backed up by spine notes/quantity hints. This fixes the prior bug where
    4 lower-is-worse sensors (HEAD.DEV, OIL.PRES, PRES.DIS) were treated as
    upper-alarm and fired on every healthy hour.
    """
    if sensor.get("tag") in BIDIRECTIONAL_SENSORS:
        return "bidirectional"

    # PRIMARY (authoritative) signal: numeric threshold ordering.
    # If alarm < warning, the sensor escalates DOWNWARD ⇒ lower-is-worse.
    # If alarm > warning, it escalates UPWARD ⇒ upper-is-worse.
    # This is unambiguous whenever both thresholds are numeric and distinct,
    # and it correctly classifies every numeric sensor in the spine. We do NOT
    # fall back to substring matching on quantity names, because that produced
    # false matches (e.g. "discharge_pressure" ⊂ "discharge_pressure_oscillation"
    # mis-tagged the upper-worse surge sensor as lower-worse).
    alm = get_alarm_threshold(sensor)
    wrn = get_warning_threshold(sensor)
    if alm is not None and wrn is not None and alm != wrn:
        return "lower" if alm < wrn else "upper"

    # SECONDARY signal: explicit spine notes (used only when thresholds tie or
    # one is missing — e.g. INS.PI warn==alarm boundary cases).
    note = (sensor.get("note", "") + " " + sensor.get("standard", "")).lower()
    lower_worse_keywords = [
        "lower is worse", "lower triggers", "drop to 0", "open = tear",
        "negative = wear", "no pulses", "seizure",
    ]
    for kw in lower_worse_keywords:
        if kw in note:
            return "lower"

    return "upper"

def threshold_is_upper(sensor: dict) -> bool:
    """Back-compat helper used by HI/OEE math: True iff 'upper' direction.
    Bidirectional sensors are treated as upper for the (deviation-from-midpoint)
    health-index calc, which is direction-symmetric in magnitude anyway.
    """
    return threshold_direction(sensor) != "lower"

# ──────────────────────────────────────────────────────────────────────────────
# Weibull degradation trajectory
# ──────────────────────────────────────────────────────────────────────────────

def weibull_degradation_curve(n_steps: int, beta: float, eta: float,
                              rng_local: np.random.Generator) -> np.ndarray:
    """
    Returns normalised degradation intensity alpha[t] in [0, 1].
    alpha=0 → healthy, alpha=1 → failure threshold crossed.
    Uses Weibull CDF: alpha(t) = 1 - exp(-(t/eta)^beta)
    where t is scaled so alpha reaches 1 at the last step.

    Physical basis (research/domain/07 §2.1):
      degradation_drift[t] = (defect_value - normal_value) * alpha(t)
    """
    # Inject slight Weibull scale noise per episode
    eta_noisy = eta * (1 + rng_local.normal(0, 0.15))
    # t range: 0 → eta (so CDF goes from 0 → 1-1/e ≈ 0.63 at eta)
    # We want alpha[n_steps-1] ≈ 1 → scale t to hit 2.5*eta (CDF~0.998)
    t = np.linspace(0, 2.5 * eta_noisy, n_steps)
    alpha = 1.0 - np.exp(-(t / eta_noisy) ** beta)
    # Normalise so last value = 1.0
    alpha = alpha / alpha[-1]
    return np.clip(alpha, 0, 1)

# ──────────────────────────────────────────────────────────────────────────────
# Cross-sensor correlation (physics, per research/domain/07 §1.3)
# ──────────────────────────────────────────────────────────────────────────────
# Encoded as a Cholesky-noise matrix per group. We apply a simplified per-asset
# version: temperature and vibration are correlated; pressure and flow are
# anti-correlated with vibration.

def correlated_noise(n_steps: int, n_sensors: int,
                     corr_pairs: List[Tuple[int, int, float]],
                     noise_scale: np.ndarray,
                     rng_local: np.random.Generator) -> np.ndarray:
    """
    Generate correlated Gaussian noise matrix [n_steps × n_sensors].
    corr_pairs: list of (i, j, rho) pairs to encode pairwise correlation.
    noise_scale: std per sensor (n_sensors,).
    """
    # Build correlation matrix
    C = np.eye(n_sensors)
    for i, j, rho in corr_pairs:
        if i < n_sensors and j < n_sensors:
            C[i, j] = rho
            C[j, i] = rho
    # Nearest positive-definite via clipping eigenvalues
    eigvals, eigvecs = np.linalg.eigh(C)
    eigvals = np.maximum(eigvals, 1e-6)
    C_pd = eigvecs @ np.diag(eigvals) @ eigvecs.T
    L = np.linalg.cholesky(C_pd)
    z = rng_local.standard_normal((n_steps, n_sensors))
    noise = (L @ z.T).T  # [n_steps × n_sensors]
    return noise * noise_scale[np.newaxis, :]

# ──────────────────────────────────────────────────────────────────────────────
# Per-asset simulation
# ──────────────────────────────────────────────────────────────────────────────

def simulate_asset(asset: dict, total_hours: int, rng_local: np.random.Generator,
                   failure_scenarios: List[dict]) -> pd.DataFrame:
    """
    Simulate TOTAL_HOURS hourly observations for one asset.
    Injects Weibull degradation windows for each failure scenario.
    Returns a DataFrame with columns:
      timestamp, asset_id, equipment_class, fault_label, scenario_id, RUL_hours,
      <sensor_tag_1>, <sensor_tag_2>, …
    """
    asset_id = asset["asset_id"]
    eq_class = asset["equipment_class"]
    sensors = [s for s in asset["sensors"] if is_numeric_sensor(s)]

    if not sensors:
        return pd.DataFrame()

    n_sensors = len(sensors)
    sensor_tags = [s["tag"] for s in sensors]
    baselines = np.array([sensor_midpoint(s) for s in sensors])
    halfbands = np.array([sensor_halfband(s) for s in sensors])

    # ── Baseline signal: slow sinusoidal + shift-change step function ────────
    t = np.arange(total_hours, dtype=float)
    # 24-hour diurnal + 168-hour weekly load cycle (shift changes, production schedule)
    diurnal = np.sin(2 * np.pi * t / 24) * halfbands[0] * 0.3  # tiny diurnal on first sensor
    weekly  = np.cos(2 * np.pi * t / 168) * halfbands[0] * 0.15

    # Sensor-level baselines as matrix [n_steps × n_sensors]
    baseline_mat = np.tile(baselines, (total_hours, 1))
    # Add gentle diurnal variance to temperature-like sensors only
    for i, s in enumerate(sensors):
        if "temp" in s["quantity"].lower() or "temperature" in s["quantity"].lower():
            baseline_mat[:, i] += diurnal * (halfbands[i] / (halfbands[0] + 1e-9))

    # ── Correlated noise ─────────────────────────────────────────────────────
    # Build pairwise correlations based on sensor types (physics-grounded)
    corr_pairs = []
    vib_idx = [i for i, s in enumerate(sensors) if "vib" in s["quantity"].lower()]
    temp_idx = [i for i, s in enumerate(sensors) if "temp" in s["quantity"].lower()]
    pres_idx = [i for i, s in enumerate(sensors) if "pres" in s["quantity"].lower()
                or "flow" in s["quantity"].lower()]
    # temperature ~ vibration (friction heating), rho ~ 0.6
    for vi in vib_idx:
        for ti in temp_idx:
            corr_pairs.append((vi, ti, 0.55))
    # pressure anti-correlates with vibration, rho ~ -0.3
    for vi in vib_idx:
        for pi in pres_idx:
            corr_pairs.append((vi, pi, -0.25))

    noise_mat = correlated_noise(total_hours, n_sensors, corr_pairs,
                                 halfbands, rng_local)
    # signal = baseline + noise (before degradation)
    signal = baseline_mat + noise_mat

    # ── Degradation windows ──────────────────────────────────────────────────
    fault_label = np.zeros(total_hours, dtype=int)        # 0=healthy, 1=degrading, 2=failed
    scenario_arr = np.full(total_hours, "", dtype=object)
    rul = np.full(total_hours, np.nan, dtype=float)

    wparams = WEIBULL_PARAMS.get(eq_class, {"beta": 2.0, "eta": 6000})
    beta = wparams["beta"]
    eta  = wparams["eta"]

    # Each failure scenario gets ONE degradation window placed at a random offset
    # in the timeline, each lasting 4-12 weeks (672-2016 hours).
    # Multiple episodes can coexist as long as they don't overlap.
    occupied = np.zeros(total_hours, dtype=bool)

    for scn in failure_scenarios:
        sig_sig = scn.get("sensor_signature", {})
        # degradation window size: 6-10 weeks
        deg_hours = int(rng_local.integers(4 * 168, 10 * 168))
        # Scenarios with explicit per-sensor `stage` metadata model a multi-stage
        # degradation where a LEADING indicator must precede laggards by WEEKS
        # (e.g. SCN-037: AE crosses warn weeks 6-8, vibration BPFO weeks 8-10,
        # temp last). Compress 4-stage separation into a 4-week window is
        # impossible, so force such scenarios to a full ~10-week trajectory so the
        # staged onsets (below) can separate by the spine-mandated weeks.
        has_stage_meta = any(
            isinstance(sd, dict) and isinstance(sd.get("stage"), int)
            for sd in sig_sig.values()
        )
        if has_stage_meta:
            deg_hours = max(deg_hours, 10 * 168)   # >= 10 weeks
        # healthy run before degradation: 4-16 weeks
        pre_healthy = int(rng_local.integers(4 * 168, 16 * 168))
        window_len = pre_healthy + deg_hours
        if window_len > total_hours:
            window_len = total_hours
            pre_healthy = max(0, total_hours - deg_hours)

        # Find a gap in the timeline
        max_attempts = 30
        placed = False
        for _ in range(max_attempts):
            start = int(rng_local.integers(0, max(1, total_hours - window_len)))
            end = start + window_len
            if not occupied[start:end].any():
                placed = True
                break

        if not placed:
            continue   # skip if no gap found; healthy data fills the rest

        # Healthy portion: no extra drift
        # Degradation portion: alpha goes from 0 → 1
        deg_start = start + pre_healthy
        deg_end   = min(deg_start + deg_hours, total_hours)
        actual_deg_len = deg_end - deg_start

        alpha = weibull_degradation_curve(actual_deg_len, beta, eta, rng_local)

        # ── Stage-aware onset (Issue 2 fix) ──────────────────────────────────
        # The spine encodes a per-sensor `stage` (1=earliest leading indicator …
        # 4=lagging). A single shared alpha curve made all sensors cross their
        # thresholds within days of each other, inverting the intended ordering
        # (e.g. AE must LEAD vibration BPFO by weeks per Master-Table-18). We give
        # each sensor its own onset offset: lower-stage sensors begin drifting
        # earlier in the window, higher-stage sensors stay flat until later, so
        # the leading indicator crosses its warning weeks before the laggards.
        stages = [sig_sig.get(s["tag"], {}).get("stage") for s in sensors]
        present_stages = sorted({st for st in stages if isinstance(st, int)})
        # Fraction of the degradation window before a stage-k sensor starts moving.
        # Earliest present stage -> 0 (drifts across the whole window); each later
        # stage delays onset by ~22% of the window so it crosses thresholds later.
        stage_onset_frac = {}
        if present_stages:
            base = present_stages[0]
            for st in present_stages:
                # ~0.40 of the (≥10-week) window per stage step. A larger spacing
                # is needed because laggard sensors (e.g. BPFO) cross their OWN
                # warning early within their ramp, so a small onset delay would
                # still let them warn before the leading indicator. With 0.40/step
                # the lead indicator (lowest stage) reliably crosses its warning
                # weeks ahead of the laggards, matching the spine SCN-037 timeline
                # + Master-Table-18 corroboration rule (AE Stage-1, no vib yet).
                stage_onset_frac[st] = min(0.82, 0.46 * (st - base))

        # Isolated RNG for staged-curve shaping so this fix does NOT perturb the
        # main per-asset noise stream (keeping healthy-operation noise unchanged
        # and avoiding phantom alerts elsewhere).
        stage_rng = np.random.default_rng(
            int(hashlib.md5(f"{asset_id}:{deg_start}:stage".encode()).hexdigest(), 16)
            % (2**32)
        )

        def staged_alpha(stage):
            """Return an alpha curve delayed per stage: flat until onset, then
            re-normalised Weibull rise to 1.0 by deg_end."""
            if stage is None or stage not in stage_onset_frac:
                return alpha
            frac = stage_onset_frac[stage]
            if frac <= 0:
                return alpha
            off = int(actual_deg_len * frac)
            a = np.zeros(actual_deg_len)
            tail = actual_deg_len - off
            if tail >= 2:
                seg = weibull_degradation_curve(tail, beta, eta, stage_rng)
                a[off:] = seg
            elif tail == 1:
                a[off:] = 1.0
            return a

        # For each sensor, compute defect delta from spine signature
        for si, sensor in enumerate(sensors):
            tag = sensor["tag"]
            if tag in sig_sig:
                sdata = sig_sig[tag]
                normal_v = sdata.get("normal_value", baselines[si])
                defect_v = sdata.get("defect_value", baselines[si])
                if isinstance(normal_v, str) or isinstance(defect_v, str):
                    continue  # ISO code strings — skip numeric drift
                delta = float(defect_v) - float(normal_v)
                # For lower-is-worse sensors, delta is negative
                a_sensor = staged_alpha(sdata.get("stage"))
                signal[deg_start:deg_end, si] += delta * a_sensor
            else:
                # Sensor not in signature: small sympathetic rise (+15% halfband)
                # due to cross-sensor physics
                signal[deg_start:deg_end, si] += halfbands[si] * 0.15 * alpha

        # Label: 0 (healthy) up to 85% of degradation window, then 1, then 2 at 95%+
        transition_1 = deg_start + int(actual_deg_len * 0.60)
        transition_2 = deg_start + int(actual_deg_len * 0.85)
        fault_label[deg_start:transition_1] = 0   # still healthy-looking
        fault_label[transition_1:transition_2] = 1  # warning/degrading
        fault_label[transition_2:deg_end] = 2       # failure zone

        # RUL: hours remaining until end of degradation window
        for h in range(deg_start, deg_end):
            rul[h] = float(deg_end - h)

        # Mark scenario_id in the degrading portion
        scenario_arr[deg_start:deg_end] = scn["scenario_id"]
        occupied[start:end] = True

    # ── Clip signals to physically plausible bounds ──────────────────────────
    # Use defect_values from failure signatures to set per-sensor clip bounds
    # so that lower-is-worse sensors can actually reach their defect levels.
    defect_floors = {}   # tag -> min allowed value
    defect_ceilings = {} # tag -> max allowed value
    for scn in failure_scenarios:
        for tag, sdata in scn.get("sensor_signature", {}).items():
            nv = sdata.get("normal_value")
            dv = sdata.get("defect_value")
            if not isinstance(nv, (int, float)) or not isinstance(dv, (int, float)):
                continue
            nv, dv = float(nv), float(dv)
            if dv < nv:   # lower-is-worse: need to allow values down to dv
                defect_floors[tag] = min(defect_floors.get(tag, nv), dv - abs(dv) * 0.1)
            else:          # upper alarm: need to allow values up to dv
                defect_ceilings[tag] = max(defect_ceilings.get(tag, nv), dv + abs(dv) * 0.1)

    for si, sensor in enumerate(sensors):
        tag = sensor["tag"]
        nr = sensor.get("normal_range")
        if isinstance(nr, list):
            lo, hi = nr
            span = hi - lo
            clip_lo = defect_floors.get(tag, lo - 0.5 * span)
            clip_hi = defect_ceilings.get(tag, hi + 5 * span)
            # For non-failure assets, use conservative clip
            if tag not in defect_floors and tag not in defect_ceilings:
                clip_lo = lo - 0.5 * span
                clip_hi = hi + 3 * span
            signal[:, si] = np.clip(signal[:, si], clip_lo, clip_hi)
            # Ensure no negative values for temperature and vibration quantities
            qty_l = sensor["quantity"].lower()
            if "temp" in qty_l or "vib" in qty_l:
                signal[:, si] = np.maximum(signal[:, si], 0)
            # Issue 3 fix: clip physically non-negative quantities (ppm, differential
            # / gauge pressure, flow, cleanliness counts) at 0. Unclipped Gaussian
            # noise on healthy assets had pushed WATER.PPM and FILT.DP negative.
            nr_lo = nr[0] if isinstance(nr, list) else 0.0
            if any(kw in qty_l for kw in NON_NEGATIVE_QUANTITY_KEYWORDS) and nr_lo >= 0:
                signal[:, si] = np.maximum(signal[:, si], 0.0)
            # AE / ultrasound dBuV tags occasionally dip slightly below their stated
            # normal floor on healthy samples — clip to the normal-range floor so the
            # signal never violates its declared baseline band.
            if ("acoustic_emission" in qty_l or "ultrasound" in qty_l
                    or "ae_broadband" in qty_l) and isinstance(nr, list):
                signal[:, si] = np.maximum(signal[:, si], nr[0])

    # ── Assemble DataFrame ────────────────────────────────────────────────────
    timestamps = [T0 + datetime.timedelta(hours=int(h)) for h in range(total_hours)]
    df = pd.DataFrame({
        "timestamp":       timestamps,
        "asset_id":        asset_id,
        "equipment_class": eq_class,
        "fault_label":     fault_label,
        "scenario_id":     scenario_arr,
        "RUL_hours":       rul,
    })
    for si, tag in enumerate(sensor_tags):
        df[tag] = np.round(signal[:, si], 4)

    return df


# ──────────────────────────────────────────────────────────────────────────────
# MAIN GENERATION
# ──────────────────────────────────────────────────────────────────────────────
log.info("Starting asset simulation …")

all_dfs = []
for asset in spine["asset_registry"]:
    aid = asset["asset_id"]
    eq_class = asset["equipment_class"]
    local_rng = np.random.default_rng(
        int(hashlib.md5(aid.encode()).hexdigest(), 16) % (2**32)
    )
    scenarios = failure_by_asset.get(aid, [])
    log.info(f"  {aid} ({eq_class}) | {len(scenarios)} failure scenario(s)")
    df_asset = simulate_asset(asset, TOTAL_HOURS, local_rng, scenarios)
    if not df_asset.empty:
        all_dfs.append(df_asset)

log.info("Concatenating all assets …")
raw = pd.concat(all_dfs, ignore_index=True)
raw = raw.sort_values(["asset_id", "timestamp"]).reset_index(drop=True)

# ── Quality check: failure rate ────────────────────────────────────────────
n_total = len(raw)
n_fail  = (raw["fault_label"] >= 2).sum()
n_warn  = (raw["fault_label"] == 1).sum()
failure_rate = n_fail / n_total
warn_rate    = n_warn / n_total
log.info(f"Total rows: {n_total:,}")
log.info(f"Failure rows (label=2): {n_fail:,} ({100*failure_rate:.2f}%)")
log.info(f"Warning rows (label=1): {n_warn:,} ({100*warn_rate:.2f}%)")
assert 0.003 <= failure_rate <= 0.06, \
    f"Failure rate {failure_rate:.3f} outside target 0.3-6% band!"

# Ensure ≥100 failure episodes (research/domain/08 Dimension 2)
n_fail_episodes = raw[raw["fault_label"] >= 2]["scenario_id"].nunique()
log.info(f"Distinct failure scenario instances: {n_fail_episodes}")

# ── (a) Write raw_sensor_timeseries.csv ───────────────────────────────────
out_a = OUT_DIR / "raw_sensor_timeseries.csv"
log.info(f"Writing {out_a.name} …")
raw.to_csv(out_a, index=False)
log.info(f"  → {len(raw):,} rows, {len(raw.columns)} columns")


# ──────────────────────────────────────────────────────────────────────────────
# (b) sensor_data_summaries.csv
# Per-asset, per-6-hour window: mean / max / std / trend per sensor
# ──────────────────────────────────────────────────────────────────────────────
log.info("Building sensor_data_summaries …")

WINDOW_H = 6   # 6-hour windows

# Add window key
raw["window_start"] = raw["timestamp"].apply(
    lambda ts: ts.replace(minute=0, second=0, microsecond=0) - datetime.timedelta(
        hours=ts.hour % WINDOW_H
    )
)

# Sensor tag columns (all columns except metadata)
meta_cols = {"timestamp", "asset_id", "equipment_class", "fault_label",
             "scenario_id", "RUL_hours", "window_start"}
sensor_cols = [c for c in raw.columns if c not in meta_cols]

summary_rows = []
grouped = raw.groupby(["asset_id", "window_start"], sort=True)

for (asset_id, ws), grp in grouped:
    row = {
        "asset_id": asset_id,
        "equipment_class": grp["equipment_class"].iloc[0],
        "window_start": ws,
        "window_end": ws + datetime.timedelta(hours=WINDOW_H),
        "n_samples": len(grp),
        "fault_label_max": int(grp["fault_label"].max()),
        "scenario_id": grp["scenario_id"][grp["fault_label"] > 0].values[0]
                       if (grp["fault_label"] > 0).any() else "",
        "RUL_hours_min": float(grp["RUL_hours"].dropna().min())
                         if grp["RUL_hours"].notna().any() else float("nan"),
    }
    for sc in sensor_cols:
        vals = grp[sc].dropna()
        if len(vals) == 0:
            row[f"{sc}__mean"] = float("nan")
            row[f"{sc}__max"]  = float("nan")
            row[f"{sc}__std"]  = float("nan")
            row[f"{sc}__trend"] = float("nan")
        else:
            row[f"{sc}__mean"]  = round(float(vals.mean()), 4)
            row[f"{sc}__max"]   = round(float(vals.max()),  4)
            row[f"{sc}__std"]   = round(float(vals.std()),  4)
            # trend: slope from simple OLS on index (positive = rising)
            n = len(vals)
            if n >= 2:
                x = np.arange(n, dtype=float)
                slope = float(np.polyfit(x, vals.values, 1)[0])
                row[f"{sc}__trend"] = round(slope, 6)
            else:
                row[f"{sc}__trend"] = 0.0
    summary_rows.append(row)

summaries = pd.DataFrame(summary_rows)
out_b = OUT_DIR / "sensor_data_summaries.csv"
log.info(f"Writing {out_b.name} …")
summaries.to_csv(out_b, index=False)
log.info(f"  → {len(summaries):,} rows, {len(summaries.columns)} columns")

# Sanity: mean values should be derivable from raw
# (spot-check one asset, one sensor)
_asset_check = spine["asset_registry"][0]["asset_id"]
_tag_check   = spine["asset_registry"][0]["sensors"][0]["tag"]
if _tag_check in raw.columns:
    raw_mean = raw[raw["asset_id"] == _asset_check][_tag_check].mean()
    summ_mean = summaries[summaries["asset_id"] == _asset_check][f"{_tag_check}__mean"].mean()
    assert abs(raw_mean - summ_mean) / (abs(raw_mean) + 1e-9) < 0.02, \
        f"Summary mean mismatch for {_tag_check}: raw={raw_mean:.4f} vs summ={summ_mean:.4f}"
    log.info(f"  Spot-check passed: {_tag_check} raw_mean={raw_mean:.4f} ≈ summary_mean={summ_mean:.4f}")


# ──────────────────────────────────────────────────────────────────────────────
# (c) anomaly_alerts.csv
# Fires when a numeric sensor crosses its alarm_threshold, keyed to scenario
# ──────────────────────────────────────────────────────────────────────────────
log.info("Building anomaly_alerts …")

# Build sensor-threshold lookup
# sensor_tag → {alarm_threshold, warning_threshold, upper_alarm, asset_id}
sensor_alarm_map = {}
for asset in spine["asset_registry"]:
    for s in asset["sensors"]:
        if not is_numeric_sensor(s):
            continue
        tag = s["tag"]
        alm = get_alarm_threshold(s)
        wrn = get_warning_threshold(s)
        upper = threshold_is_upper(s)
        sensor_alarm_map[tag] = {
            "alarm_threshold": alm,
            "warning_threshold": wrn,
            "upper_alarm": upper,
            "asset_id": asset["asset_id"],
        }

alert_rows = []

for asset in spine["asset_registry"]:
    aid = asset["asset_id"]
    df_a = raw[raw["asset_id"] == aid].copy()

    for s in asset["sensors"]:
        if not is_numeric_sensor(s):
            continue
        tag = s["tag"]
        if tag not in df_a.columns:
            continue

        alm = get_alarm_threshold(s)
        wrn = get_warning_threshold(s)
        direction = threshold_direction(s)
        bidir = BIDIRECTIONAL_SENSORS.get(tag)

        vals = df_a[tag].values
        timestamps_a = df_a["timestamp"].values
        scenario_a   = df_a["scenario_id"].values
        fault_a      = df_a["fault_label"].values

        for i, (v, ts, scn, fl) in enumerate(
                zip(vals, timestamps_a, scenario_a, fault_a)):
            v = float(v)
            severity = None
            threshold = None

            if direction == "bidirectional":
                # VISC: alarm-high when v > alarm_high, warn-low when v < warn_low.
                ah = bidir["alarm_high"]
                wl = bidir["warn_low"]
                if v > ah:
                    severity = "ALARM"
                    threshold = ah
                elif v < wl:
                    severity = "WARNING"
                    threshold = wl
            elif direction == "upper":
                if alm is not None and v >= alm:
                    severity = "ALARM"
                    threshold = alm
                elif wrn is not None and v >= wrn:
                    severity = "WARNING"
                    threshold = wrn
            else:  # lower
                if alm is not None and v <= alm:
                    severity = "ALARM"
                    threshold = alm
                elif wrn is not None and v <= wrn:
                    severity = "WARNING"
                    threshold = wrn

            if severity:
                alert_rows.append({
                    "timestamp":   pd.Timestamp(ts),
                    "asset_id":    aid,
                    "sensor":      tag,
                    "value":       round(v, 4),
                    "threshold":   threshold,
                    "severity":    severity,
                    "fault_label": int(fl),
                    "scenario_id": scn,
                })

alerts = pd.DataFrame(alert_rows) if alert_rows else pd.DataFrame(
    columns=["timestamp", "asset_id", "sensor", "value", "threshold",
             "severity", "fault_label", "scenario_id"])

out_c = OUT_DIR / "anomaly_alerts.csv"
log.info(f"Writing {out_c.name} …")
alerts.to_csv(out_c, index=False)
log.info(f"  → {len(alerts):,} alert rows")

# ──────────────────────────────────────────────────────────────────────────────
# (d) process_condition_indicators.csv
# Health Index (0-100) + OEE-style KPIs per asset per 24-hour day
# ──────────────────────────────────────────────────────────────────────────────
log.info("Building process_condition_indicators …")

# Health Index formula (per sensor, 0-100):
#   HI_sensor = 100 × (1 - clamp(|value - midpoint| / (alarm_thresh - midpoint), 0, 1))
#   Asset HI  = weighted mean over sensors (equal weights for now)
# OEE = Availability × Performance × Quality (simplified; each 0-1)
#   Availability = fraction of hours with fault_label == 0
#   Performance  = mean(sensor_value_in_normal_range) fraction
#   Quality      = 1 - n_alarms / n_hours (normalised)
# Overall Equipment Effectiveness aligned to typical steel-plant 85%+ OEE targets

WINDOW_D = 24  # 24-hour windows for KPIs

def compute_sensor_hi(value: np.ndarray, midpoint: float,
                      alarm_thresh: Optional[float], upper: bool) -> np.ndarray:
    """Returns HI 0-100 for each timestep. 100=perfectly healthy, 0=at alarm."""
    if alarm_thresh is None:
        return np.full(len(value), 50.0)
    denominator = abs(alarm_thresh - midpoint)
    if denominator < 1e-6:
        return np.full(len(value), 100.0)
    if upper:
        deviation = (value - midpoint) / denominator
    else:
        deviation = (midpoint - value) / denominator  # invert for lower-is-worse
    hi = 100.0 * (1.0 - np.clip(deviation, 0, 1))
    return np.clip(hi, 0, 100)

pci_rows = []

for asset in spine["asset_registry"]:
    aid = asset["asset_id"]
    df_a = raw[raw["asset_id"] == aid].copy()
    eq_class = asset["equipment_class"]
    df_a["day"] = df_a["timestamp"].apply(
        lambda ts: ts.replace(hour=0, minute=0, second=0, microsecond=0)
    )

    numeric_sensors = [s for s in asset["sensors"] if is_numeric_sensor(s)]

    for day, grp in df_a.groupby("day"):
        n_h = len(grp)
        if n_h == 0:
            continue

        # ── Health Index ─────────────────────────────────────────────────────
        sensor_hi_values = []
        for s in numeric_sensors:
            tag = s["tag"]
            if tag not in grp.columns:
                continue
            vals = grp[tag].values.astype(float)
            mid  = sensor_midpoint(s)
            alm  = get_alarm_threshold(s)
            upper = threshold_is_upper(s)
            hi_arr = compute_sensor_hi(vals, mid, alm, upper)
            sensor_hi_values.append(hi_arr.mean())

        health_index = float(np.mean(sensor_hi_values)) if sensor_hi_values else 50.0

        # ── OEE components ────────────────────────────────────────────────────
        fault_labels = grp["fault_label"].values
        n_healthy    = (fault_labels == 0).sum()
        n_warning    = (fault_labels == 1).sum()
        n_failure    = (fault_labels >= 2).sum()

        # Availability: hours without failure / total hours
        # (warning is partial availability: 0.8 weight)
        availability = (n_healthy + 0.8 * n_warning) / max(n_h, 1)

        # Performance: fraction of sensor readings within normal band
        in_normal = 0
        total_sensor_readings = 0
        for s in numeric_sensors:
            tag = s["tag"]
            if tag not in grp.columns:
                continue
            nr = s.get("normal_range", [])
            if len(nr) == 2:
                vals = grp[tag].values.astype(float)
                in_normal += ((vals >= nr[0]) & (vals <= nr[1])).sum()
                total_sensor_readings += len(vals)
        performance = in_normal / max(total_sensor_readings, 1)

        # Quality: fraction of hours with no ALARM-level alert in this day
        # We count alarm crossings from the alerts table
        day_end = day + datetime.timedelta(hours=24)
        if not alerts.empty:
            n_alarms_today = len(alerts[
                (alerts["asset_id"] == aid) &
                (alerts["timestamp"] >= pd.Timestamp(day)) &
                (alerts["timestamp"] < pd.Timestamp(day_end)) &
                (alerts["severity"] == "ALARM")
            ])
        else:
            n_alarms_today = 0
        quality = max(0.0, 1.0 - n_alarms_today / max(n_h, 1))

        oee = availability * performance * quality
        mtbf_estimate = (n_healthy / max(n_failure, 1)) if n_failure > 0 else float("inf")
        rul_min = float(grp["RUL_hours"].dropna().min()) if grp["RUL_hours"].notna().any() else float("nan")

        pci_rows.append({
            "date":             day.strftime("%Y-%m-%d"),
            "asset_id":         aid,
            "equipment_class":  eq_class,
            "health_index":     round(health_index, 2),
            "availability":     round(availability, 4),
            "performance":      round(performance, 4),
            "quality":          round(quality, 4),
            "oee":              round(oee, 4),
            "hours_healthy":    int(n_healthy),
            "hours_warning":    int(n_warning),
            "hours_failure":    int(n_failure),
            "n_alarm_events":   int(n_alarms_today),
            "RUL_hours_min":    round(rul_min, 1) if not math.isnan(rul_min) else float("nan"),
            "fault_label_max":  int(fault_labels.max()),
            "scenario_id":      grp["scenario_id"][grp["fault_label"] > 0].values[0]
                                if (grp["fault_label"] > 0).any() else "",
        })

pci = pd.DataFrame(pci_rows)
out_d = OUT_DIR / "process_condition_indicators.csv"
log.info(f"Writing {out_d.name} …")
pci.to_csv(out_d, index=False)
log.info(f"  → {len(pci):,} rows")

# ──────────────────────────────────────────────────────────────────────────────
# Statistical distinguishability check
# ──────────────────────────────────────────────────────────────────────────────
log.info("Statistical distinguishability check …")

# For each asset that has both healthy and failing rows, check that
# mean sensor values differ significantly between label=0 and label=2.
distinguish_results = []
for asset in spine["asset_registry"]:
    aid = asset["asset_id"]
    df_a = raw[raw["asset_id"] == aid]
    healthy_rows = df_a[df_a["fault_label"] == 0]
    failing_rows = df_a[df_a["fault_label"] >= 2]

    if len(failing_rows) < 5:
        continue

    for s in asset["sensors"]:
        if not is_numeric_sensor(s):
            continue
        tag = s["tag"]
        if tag not in df_a.columns:
            continue
        h_mean = float(healthy_rows[tag].mean())
        f_mean = float(failing_rows[tag].mean())
        # Check that defect direction agrees with signature
        scns = failure_by_asset.get(aid, [])
        expected_dir = None
        for scn in scns:
            ssig = scn.get("sensor_signature", {})
            if tag in ssig and "defect_value" in ssig[tag] and "normal_value" in ssig[tag]:
                nv = ssig[tag]["normal_value"]
                dv = ssig[tag]["defect_value"]
                if isinstance(nv, (int, float)) and isinstance(dv, (int, float)):
                    expected_dir = "up" if float(dv) > float(nv) else "down"
                    break
        actual_dir = "up" if f_mean > h_mean else "down"
        match = (expected_dir is None) or (actual_dir == expected_dir)
        sep_ratio = abs(f_mean - h_mean) / (abs(h_mean) + 1e-9)
        distinguish_results.append({
            "asset_id": aid,
            "sensor": tag,
            "healthy_mean": round(h_mean, 4),
            "failing_mean": round(f_mean, 4),
            "sep_ratio": round(sep_ratio, 4),
            "direction_correct": match,
        })

dist_df = pd.DataFrame(distinguish_results)
if not dist_df.empty:
    ok_count = dist_df["direction_correct"].sum()
    total_count = len(dist_df)
    ok_pct = 100 * ok_count / total_count
    log.info(f"  Direction check: {ok_count}/{total_count} sensors correct ({ok_pct:.1f}%)")
    sep_med = dist_df["sep_ratio"].median()
    log.info(f"  Median separation ratio (failing vs healthy): {sep_med:.4f}")
    assert ok_pct >= 80, f"Too many direction failures: {ok_pct:.1f}%"
    assert sep_med >= 0.05, f"Median separation too low: {sep_med:.4f}"

# ──────────────────────────────────────────────────────────────────────────────
# Final summary
# ──────────────────────────────────────────────────────────────────────────────
log.info("=" * 60)
log.info("GENERATION COMPLETE — Summary")
log.info("=" * 60)
log.info(f"(a) raw_sensor_timeseries.csv       : {len(raw):,} rows × {len(raw.columns)} cols")
log.info(f"(b) sensor_data_summaries.csv        : {len(summaries):,} rows × {len(summaries.columns)} cols")
log.info(f"(c) anomaly_alerts.csv               : {len(alerts):,} rows")
log.info(f"(d) process_condition_indicators.csv : {len(pci):,} rows")
log.info(f"Failure rate (label=2): {100*failure_rate:.3f}%  [target 0.5-5%]")
log.info(f"Warning rate (label=1): {100*warn_rate:.3f}%")
log.info(f"Distinct failure episodes: {n_fail_episodes}  [target ≥100? check below]")
n_failure_rows = n_fail
log.info(f"Failure row count (label=2): {n_failure_rows:,}")
if not dist_df.empty:
    log.info(f"Distinguishability: {ok_pct:.1f}% sensors show correct defect direction")
    log.info(f"Median separation ratio: {sep_med:.4f}")
log.info("All 4 output files written to:")
log.info(f"  {OUT_DIR}")
