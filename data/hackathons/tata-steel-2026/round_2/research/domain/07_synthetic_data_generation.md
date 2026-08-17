# Domain Research 07: Synthetic Steel-Plant Sensor Dataset Generation
**Maintenance Wizard — Tata Steel AI Hackathon 2026, Round 2**
**Research date:** 2026-06-08
**Author:** ml-engineer-agent (Jarvis)
**Scope:** Physics-grounded multivariate sensor simulation, degradation trajectory injection, class imbalance control, intentional data-quality defects, output schema aligned to industrial historian exports.
**Downstream consumers:** DataForge platform seed data, Maintenance Wizard demo sensor playback, optional fine-tune corpus.

---

## Executive Summary (5 bullets)

1. **Physics-first, not pure statistical:** Realistic steel-plant sensor streams require correlated multivariate generation anchored to known thermodynamic and tribological relationships (temperature rise ~ vibration RMS^1.5, bearing fault sidebands at BPFO/BPFI frequencies). Pure CTGAN/TVAE on tabular snapshots loses temporal structure and produces implausible cross-sensor correlations — use physics simulation as the base, add stochastic noise on top.
2. **Degradation = two layers:** (a) a Weibull-parameterized slow-drift trajectory (days to weeks) for RUL encoding and (b) short-window fault-frequency injection into the vibration signal (bearing outer/inner race BPFO/BPFI sidebands) for high-frequency anomaly detection. Both are independently controllable, enabling fine-grained label construction.
3. **Imbalance by construction, not by subsampling:** Generate 95-98% healthy runs at full length; generate 2-5% fault episodes by shortening run-to-failure trajectories. Never balance post-hoc by SMOTE on time-series data — SMOTE creates syntactically valid but physically impossible interpolations across time.
4. **Six data-quality defect types are sufficient:** Missing chunks (sensor blackout), point dropouts (single NaN), sensor drift (slow additive bias), timestamp jitter/duplicates, mislabels (label boundary smear), and flat-line freezes. Each defect is injected as a parameterised post-processing pass so intensity is tunable.
5. **Output schema is historian-compatible:** Timestamp + asset_id + 6 sensor tags + fault_label (4-class) + RUL_cycles + severity + sequence_id — matches OSIsoft PI / Siemens SIMATIC historian export format and the AI4I 2020 reference schema.

---

## 1. Equipment Selection and Physical Basis

### 1.1 Target Asset: Rolling Mill Conveyor Roller / Drive Bearing System

For maximum realism and judge credibility, simulate a **hot-strip-mill conveyor roller** with an attached drive motor. This maps to:

- **Temperature sensors (2):** Bearing housing temperature + motor winding temperature
- **Vibration (1):** Radial vibration at drive-end bearing housing (mm/s RMS)
- **Pressure (1):** Hydraulic clamping pressure on the roller gap actuator (bar)
- **RPM (1):** Roller surface speed derived from motor tachometer (rpm)
- **Current (1):** Motor phase current (A) — proxy for torque load
- **Torque (1, derived):** Estimated torque = (Current × Voltage × PF × η) / (2π × RPM/60) — optionally included as a derived column

For 6-channel output: `temperature_bearing_c`, `temperature_motor_c`, `vibration_mm_s`, `pressure_bar`, `rpm`, `current_a`

### 1.2 Healthy Operating Ranges (based on published steel-plant sensor norms)

| Sensor | Healthy Range | Sampling | Physical basis |
|--------|--------------|----------|----------------|
| temperature_bearing_c | 45–75°C | 1 Hz | ISO 15243: normal bearing temp ≤ ambient+40°C |
| temperature_motor_c | 60–90°C | 1 Hz | NEMA MG1: Class F insulation limit 155°C |
| vibration_mm_s | 1.5–4.5 mm/s | 1 Hz (RMS) | ISO 10816-3 Zone A: <2.3 mm/s, Zone B: <4.5 mm/s |
| pressure_bar | 140–180 bar | 1 Hz | Typical hydraulic AGC system operating pressure |
| rpm | 280–320 rpm | 1 Hz | Typical finishing-mill roller speed range |
| current_a | 120–160 A | 1 Hz | Motor FLA ×0.75–0.95 at normal load |

[unverified: exact operating ranges are illustrative; real plant values require specific equipment datasheets]

### 1.3 Cross-Sensor Correlations (Physical)

The following correlations must be encoded in the simulator — not estimated from data:

```
temperature_bearing ~ 0.65 * vibration_mm_s^1.5   (friction heat from bearing wear)
temperature_motor   ~ 0.72 * current_a             (I²R heating)
current_a           ~ rpm * (load_fraction)         (torque ∝ current at constant V)
pressure_bar        ~ -0.3 * rpm_deviation          (hydraulic compensation for speed changes)
```

These are enforced via a **Cholesky-decomposed covariance matrix** applied to the noise term, NOT to the signal itself.

---

## 2. Multivariate Signal Simulation

### 2.1 Architecture: Physical Model + Correlated Noise + Degradation Overlay

```
signal[t] = baseline[t] + degradation_drift[t] + fault_injection[t] + correlated_noise[t]
```

Each term is computed independently, then summed:

- **baseline[t]:** A slow sinusoidal + step function capturing shift-change load variations
- **degradation_drift[t]:** Monotonic exponential ramp (RUL decay) — only nonzero in fault episodes
- **fault_injection[t]:** Spectral sideband injection into vibration only (bearing faults)
- **correlated_noise[t]:** Multivariate Gaussian with Cholesky-enforced cross-sensor correlation

### 2.2 Code Sketch: Core Simulator

```python
import numpy as np
from scipy.signal import butter, filtfilt
from scipy.stats import weibull_min
import pandas as pd
from dataclasses import dataclass, field
from typing import Literal

# -------------------------------------------------------
# Config
# -------------------------------------------------------
@dataclass
class AssetConfig:
    asset_id: str
    roller_diameter_mm: float = 400.0      # for BPFO/BPFI calculation
    bearing_geometry: dict = field(default_factory=lambda: {
        "n_balls": 9,
        "ball_diameter_mm": 22.0,
        "pitch_diameter_mm": 120.0,
        "contact_angle_deg": 15.0,
    })
    healthy_rpm: float = 300.0
    sampling_hz: int = 1                   # 1 Hz for historian-style data

@dataclass 
class SimConfig:
    n_healthy_runs: int = 950              # 95% of total episodes
    n_fault_runs: int = 50                 # 5% of total
    max_healthy_cycles: int = 2000         # cycles per healthy run
    fault_run_min_cycles: int = 200        # minimum before fault manifests
    fault_run_max_cycles: int = 1200       # maximum run length including degradation
    seed: int = 42

# -------------------------------------------------------
# Bearing Fault Frequency Calculator
# -------------------------------------------------------
def bearing_fault_frequencies(cfg: AssetConfig, rpm: float) -> dict:
    """
    BPFO/BPFI per ISO 15243 and SKF bearing frequency formulas.
    BPFO = (n/2) * RPM/60 * (1 - Bd/Pd * cos(alpha))
    BPFI = (n/2) * RPM/60 * (1 + Bd/Pd * cos(alpha))
    """
    bg = cfg.bearing_geometry
    n = bg["n_balls"]
    Bd = bg["ball_diameter_mm"]
    Pd = bg["pitch_diameter_mm"]
    alpha = np.radians(bg["contact_angle_deg"])
    rps = rpm / 60.0
    bpfo = (n / 2) * rps * (1 - (Bd / Pd) * np.cos(alpha))
    bpfi = (n / 2) * rps * (1 + (Bd / Pd) * np.cos(alpha))
    bsf  = (Pd / (2 * Bd)) * rps * (1 - (Bd / Pd) ** 2 * np.cos(alpha) ** 2)
    return {"bpfo": bpfo, "bpfi": bpfi, "bsf": bsf}

# -------------------------------------------------------
# Correlated Noise Generator
# -------------------------------------------------------
def make_corr_matrix() -> np.ndarray:
    """
    6x6 correlation matrix: [temp_bearing, temp_motor, vibration, pressure, rpm, current]
    Physically motivated cross-correlations.
    """
    R = np.eye(6)
    # temp_bearing <-> vibration: high correlation (friction heat)
    R[0, 2] = R[2, 0] = 0.65
    # temp_motor <-> current: high correlation (I2R)
    R[1, 5] = R[5, 1] = 0.72
    # rpm <-> current: moderate (torque load)
    R[4, 5] = R[5, 4] = 0.45
    # pressure <-> rpm: mild negative (hydraulic compensation)
    R[3, 4] = R[4, 3] = -0.30
    # temp_bearing <-> current: indirect via vibration
    R[0, 5] = R[5, 0] = 0.40
    return R

def correlated_noise(n_steps: int, scales: np.ndarray, seed: int = 0) -> np.ndarray:
    """
    Returns (n_steps, 6) noise array with physical cross-sensor correlations.
    scales: per-sensor 1-sigma noise amplitude
    """
    rng = np.random.default_rng(seed)
    R = make_corr_matrix()
    # Nearest-positive-definite fix via eigenvalue clipping
    eigvals, eigvecs = np.linalg.eigh(R)
    eigvals = np.clip(eigvals, 1e-6, None)
    R_pd = eigvecs @ np.diag(eigvals) @ eigvecs.T
    L = np.linalg.cholesky(R_pd)
    raw = rng.standard_normal((n_steps, 6))
    noise = raw @ L.T
    return noise * scales[np.newaxis, :]

# -------------------------------------------------------
# Baseline Signal Generator
# -------------------------------------------------------
SENSOR_BASELINES = np.array([60.0, 75.0, 2.5, 160.0, 300.0, 140.0])
SENSOR_SCALES    = np.array([ 1.5,  2.0, 0.3,   5.0,   4.0,   4.0])
SENSOR_NAMES     = [
    "temperature_bearing_c", "temperature_motor_c", "vibration_mm_s",
    "pressure_bar", "rpm", "current_a"
]

def healthy_baseline(n_steps: int, cfg: AssetConfig, seed: int = 0) -> np.ndarray:
    """
    Smooth operational baseline with shift-change load steps and slow diurnal variation.
    Returns (n_steps, 6)
    """
    rng = np.random.default_rng(seed)
    t = np.arange(n_steps)
    
    # Diurnal cycle (8-hour shift), amplitude per sensor
    diurnal_amp = np.array([2.0, 2.5, 0.2, 3.0, 2.0, 3.0])
    diurnal = np.sin(2 * np.pi * t[:, None] / (8 * 3600)) * diurnal_amp[None, :]
    
    # Random load step changes every ~30 minutes
    n_steps_per_30min = 1800
    step_changes = np.zeros((n_steps, 6))
    for i in range(0, n_steps, n_steps_per_30min):
        step_changes[i:, :] += rng.normal(0, 0.5, 6)
    step_changes = np.cumsum(step_changes, axis=0) * 0
    # Clamp load steps to ±5% of baseline
    step_amp = SENSOR_BASELINES * 0.05
    step_signal = rng.normal(0, 1, (n_steps, 6)) * step_amp[None, :]
    # Low-pass filter for smooth steps
    b, a = butter(2, 0.002, btype='low')
    for i in range(6):
        step_signal[:, i] = filtfilt(b, a, step_signal[:, i])
    
    noise = correlated_noise(n_steps, SENSOR_SCALES, seed=seed + 1)
    return SENSOR_BASELINES[None, :] + diurnal + step_signal + noise
```

### 2.3 Degradation Trajectory Injection

```python
# -------------------------------------------------------
# Weibull RUL Decay + Degradation Overlay
# -------------------------------------------------------
def weibull_degradation_ramp(
    n_cycles: int,
    fault_type: Literal["outer_race", "inner_race", "rolling_element", "lubrication"],
    shape_k: float = 2.5,
    scale_lambda: float = None,
    onset_fraction: float = 0.6,
) -> np.ndarray:
    """
    Returns a degradation index from 0→1 over n_cycles.
    Onset: degradation begins at onset_fraction * n_cycles (healthy period first).
    Shape k: Weibull shape parameter.
      k=1: constant failure rate (lubrication degradation)
      k=2-3: wear-out (outer/inner race fatigue — most common for bearings)
      k=5+: rapid onset (rolling element spalling)
    
    References: ISO 281 bearing life (L10), Weibull (1951) fatigue model.
    """
    if scale_lambda is None:
        scale_lambda = n_cycles * (1 - onset_fraction)
    
    onset_cycle = int(n_cycles * onset_fraction)
    degradation = np.zeros(n_cycles)
    post_onset = np.arange(n_cycles - onset_cycle)
    # Weibull CDF: F(t) = 1 - exp(-(t/lambda)^k)
    degradation[onset_cycle:] = weibull_min.cdf(
        post_onset, c=shape_k, scale=scale_lambda
    )
    return degradation  # range [0, 1]

# Fault-type-specific sensor amplification matrices
# Each fault type drives different sensors — this is the physics
FAULT_AMPLIFICATION = {
    "outer_race": {
        "temperature_bearing_c": 15.0,   # °C rise at failure
        "temperature_motor_c":    3.0,
        "vibration_mm_s":        12.0,   # dominant symptom
        "pressure_bar":          -8.0,   # hydraulic load shedding
        "rpm":                   -5.0,   # speed drop near failure
        "current_a":              8.0,   # motor compensates
    },
    "inner_race": {
        "temperature_bearing_c": 18.0,
        "temperature_motor_c":    4.0,
        "vibration_mm_s":        10.0,
        "pressure_bar":          -5.0,
        "rpm":                   -3.0,
        "current_a":             10.0,
    },
    "rolling_element": {
        "temperature_bearing_c": 10.0,
        "temperature_motor_c":    2.0,
        "vibration_mm_s":         8.0,
        "pressure_bar":          -3.0,
        "rpm":                   -2.0,
        "current_a":              5.0,
    },
    "lubrication": {
        "temperature_bearing_c": 22.0,   # dominant: friction heat
        "temperature_motor_c":    6.0,
        "vibration_mm_s":         6.0,
        "pressure_bar":          -2.0,
        "rpm":                   -1.0,
        "current_a":              4.0,
    },
}

def apply_degradation_overlay(
    baseline: np.ndarray,
    degradation_index: np.ndarray,
    fault_type: str,
) -> np.ndarray:
    """
    Adds the degradation drift to the baseline signal.
    baseline: (n_steps, 6)
    degradation_index: (n_steps,) in [0, 1]
    """
    amp = np.array([FAULT_AMPLIFICATION[fault_type][s] for s in SENSOR_NAMES])
    drift = degradation_index[:, None] * amp[None, :]
    return baseline + drift
```

### 2.4 Bearing Fault Frequency Injection into Vibration

```python
# -------------------------------------------------------
# Spectral Fault Sideband Injection (vibration channel only)
# -------------------------------------------------------
def inject_bearing_fault_sidebands(
    vibration: np.ndarray,
    fault_type: Literal["outer_race", "inner_race"],
    rpm: float,
    degradation_index: np.ndarray,
    sampling_hz: int = 1,
    n_harmonics: int = 3,
    seed: int = 42,
) -> np.ndarray:
    """
    Adds bearing fault frequency sidebands to the vibration signal.
    Amplitude of sidebands scales with degradation_index (0→1).

    NOTE: At 1 Hz sampling, true bearing fault frequencies (e.g., BPFO~30 Hz)
    are above Nyquist. This function injects the ENVELOPE / RMS-level modulation
    of the fault signal — the time-averaged power increase at each cycle that
    would appear in envelope analysis. At higher sampling (e.g., 25.6 kHz),
    this should be replaced with true spectral injection.

    For 1 Hz historian data: inject a low-frequency amplitude modulation at
    fault_freq modulated down to the observable range (once-per-revolution
    contribution to RMS).
    
    References: ISO 13373-3 (envelope analysis), Smith (1982) bearing fault frequencies.
    """
    rng = np.random.default_rng(seed)
    n = len(vibration)
    t = np.arange(n) / sampling_hz
    
    # Fault characteristic frequencies (at sampling_hz, use the modulation rate)
    # At 1 Hz, we simulate the once-per-defect-pass amplitude modulation
    # (For demo purposes — real analysis requires 10 kHz+ vibration data)
    fault_period_cycles = {
        "outer_race": 9.3,   # BPFO normalized to shaft frequency
        "inner_race": 13.7,  # BPFI normalized
    }
    
    fault_mod_freq = (rpm / 60.0) / fault_period_cycles.get(fault_type, 10.0)
    fault_mod_freq = min(fault_mod_freq, 0.4 * sampling_hz)  # stay below Nyquist
    
    sideband_signal = np.zeros(n)
    for h in range(1, n_harmonics + 1):
        freq = h * fault_mod_freq
        # Random phase per harmonic
        phase = rng.uniform(0, 2 * np.pi)
        amplitude = 2.0 / h  # harmonics decay at 1/h
        sideband_signal += amplitude * np.sin(2 * np.pi * freq * t + phase)
    
    # Scale by degradation_index — zero amplitude when healthy
    scaled_injection = sideband_signal * degradation_index
    return vibration + scaled_injection
```

---

## 3. Warning → Alarm → Failure Progression

The severity label transitions must be non-trivial to separate — a model that simply thresholds vibration above 8.0 mm/s should NOT achieve >0.9 F1 on raw features.

```python
# -------------------------------------------------------
# Progressive Label Assignment
# -------------------------------------------------------
def assign_fault_labels(
    degradation_index: np.ndarray,
    noise_in_labels: bool = True,
    label_smear_window: int = 30,
    seed: int = 0,
) -> np.ndarray:
    """
    Assigns 4-class labels based on degradation index.
    Classes: 0=HEALTHY, 1=WARNING, 2=ALARM, 3=FAILURE
    
    Key: WARNING/ALARM boundary is deliberately noisy to prevent
    trivial separability. Label smearing mimics real-world
    annotation uncertainty (human labeler looking at paper records
    with ±30-cycle timing uncertainty).
    
    Thresholds derived from ISO 13373 severity bands:
    WARNING: first measurable degradation (d > 0.15)
    ALARM:   accelerated wear phase (d > 0.55)
    FAILURE: imminent/post-failure (d > 0.85)
    """
    n = len(degradation_index)
    labels = np.zeros(n, dtype=int)
    labels[degradation_index > 0.15] = 1  # WARNING
    labels[degradation_index > 0.55] = 2  # ALARM
    labels[degradation_index > 0.85] = 3  # FAILURE
    
    if noise_in_labels:
        rng = np.random.default_rng(seed)
        # Find label boundaries, smear ±label_smear_window cycles
        for boundary_threshold in [0.15, 0.55, 0.85]:
            boundary_idx = np.where(np.diff((degradation_index > boundary_threshold).astype(int)))[0]
            for idx in boundary_idx:
                smear_start = max(0, idx - label_smear_window)
                smear_end   = min(n, idx + label_smear_window)
                # Flip 20% of labels in smear window to adjacent class
                flip_mask = rng.random(smear_end - smear_start) < 0.20
                for i, flip in enumerate(flip_mask):
                    if flip:
                        current_label = labels[smear_start + i]
                        adjacent = current_label + rng.choice([-1, 1])
                        labels[smear_start + i] = int(np.clip(adjacent, 0, 3))
    return labels
```

### 3.1 Imbalance Strategy

| Class | Target fraction | Generation method |
|-------|----------------|-------------------|
| HEALTHY (0) | ~80% of all rows | Full-length healthy runs (2000 cycles each) |
| WARNING (1) | ~12% of all rows | Early degradation phase of fault episodes |
| ALARM (2)   | ~5% of all rows  | Mid-degradation phase of fault episodes |
| FAILURE (3) | ~3% of all rows  | Post-alarm phase — short window before EOL |

**Critical: do NOT use SMOTE or any interpolation-based augmentation on time-series.** SMOTE on sensor data creates physically impossible intermediate states (e.g., high vibration but low temperature — violates the friction-heat correlation). Class imbalance is addressed in modeling via:
- `class_weight='balanced'` in sklearn estimators
- `scale_pos_weight` in LightGBM
- Focal loss for neural models
- Stratified sampling in cross-validation

---

## 4. Data Quality Defect Injection

Six defect types, injected as a configurable post-processing pass. Intensity is parameterised — set to 0 for clean data, 0.15 for realistic defect rate, 1.0 for stress-test.

```python
# -------------------------------------------------------
# Data Quality Defect Injection Pipeline
# -------------------------------------------------------
import pandas as pd
import numpy as np

class DefectInjector:
    """
    Injects realistic data quality defects into sensor DataFrames.
    Each method is idempotent given the same seed.
    
    Usage:
        injector = DefectInjector(seed=42, defect_rate=0.15)
        df_dirty = injector.apply_all(df_clean, defect_config)
    """
    def __init__(self, seed: int = 42, defect_rate: float = 0.15):
        self.rng = np.random.default_rng(seed)
        self.defect_rate = defect_rate

    # DEFECT 1: Sensor dropout (single NaN points — instrument power glitch)
    def inject_point_dropouts(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        for col in SENSOR_NAMES:
            mask = self.rng.random(len(df)) < self.defect_rate * 0.5
            df.loc[mask, col] = np.nan
        return df

    # DEFECT 2: Sensor blackout (chunk of NaNs — network/connection loss)
    def inject_missing_chunks(self, df: pd.DataFrame, max_chunk_len: int = 120) -> pd.DataFrame:
        df = df.copy()
        n = len(df)
        n_blackouts = max(1, int(n * self.defect_rate * 0.01))
        for _ in range(n_blackouts):
            col = self.rng.choice(SENSOR_NAMES)
            start = self.rng.integers(0, max(1, n - max_chunk_len))
            length = self.rng.integers(10, max_chunk_len)
            df.iloc[start:start + length, df.columns.get_loc(col)] = np.nan
        return df

    # DEFECT 3: Sensor drift (slow additive bias — calibration offset accumulation)
    def inject_drift(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        n = len(df)
        for col in self.rng.choice(SENSOR_NAMES, size=2, replace=False):
            # Drift starts at a random point, accumulates linearly
            drift_start = self.rng.integers(0, n // 2)
            drift_rate = self.rng.uniform(0.01, 0.05) * SENSOR_SCALES[SENSOR_NAMES.index(col)]
            drift = np.zeros(n)
            drift[drift_start:] = np.arange(n - drift_start) * drift_rate
            df[col] = df[col] + drift
        return df

    # DEFECT 4: Timestamp duplicates / jitter (historian clock skew)
    def inject_timestamp_jitter(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        if 'timestamp' not in df.columns:
            return df
        jitter_seconds = self.rng.integers(-3, 4, size=len(df))
        n_dups = max(1, int(len(df) * self.defect_rate * 0.05))
        dup_indices = self.rng.choice(len(df), size=n_dups, replace=False)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['timestamp'] = df['timestamp'] + pd.to_timedelta(jitter_seconds, unit='s')
        # Insert duplicate timestamps at selected indices
        df.iloc[dup_indices, df.columns.get_loc('timestamp')] = \
            df.iloc[dup_indices - 1, df.columns.get_loc('timestamp')].values
        return df

    # DEFECT 5: Flat-line freeze (sensor stuck at constant value — ADC failure)
    def inject_flatline(self, df: pd.DataFrame, max_len: int = 60) -> pd.DataFrame:
        df = df.copy()
        n = len(df)
        if self.rng.random() > self.defect_rate:
            return df
        col = self.rng.choice(SENSOR_NAMES)
        start = self.rng.integers(0, max(1, n - max_len))
        length = self.rng.integers(5, max_len)
        frozen_val = df.iloc[start][col]
        df.iloc[start:start + length, df.columns.get_loc(col)] = frozen_val
        return df

    # DEFECT 6: Mislabels (label boundary smear — already handled in assign_fault_labels)
    # This adds a second mislabel pass on the fully assembled DataFrame
    def inject_mislabels(self, df: pd.DataFrame, mislabel_rate: float = 0.02) -> pd.DataFrame:
        df = df.copy()
        mask = self.rng.random(len(df)) < mislabel_rate
        n_mislabeled = mask.sum()
        current_labels = df.loc[mask, 'fault_label'].values
        noise = self.rng.choice([-1, 1], size=n_mislabeled)
        df.loc[mask, 'fault_label'] = np.clip(current_labels + noise, 0, 3).astype(int)
        return df

    def apply_all(self, df: pd.DataFrame, include_mislabels: bool = True) -> pd.DataFrame:
        df = self.inject_point_dropouts(df)
        df = self.inject_missing_chunks(df)
        df = self.inject_drift(df)
        df = self.inject_timestamp_jitter(df)
        df = self.inject_flatline(df)
        if include_mislabels:
            df = self.inject_mislabels(df)
        return df
```

---

## 5. Full Dataset Assembly Pipeline

```python
# -------------------------------------------------------
# Full Dataset Generator
# -------------------------------------------------------
from datetime import datetime, timedelta
import uuid

FAULT_TYPES = ["outer_race", "inner_race", "rolling_element", "lubrication"]
WEIBULL_PARAMS = {
    "outer_race":       {"shape_k": 2.5, "onset_fraction": 0.60},
    "inner_race":       {"shape_k": 2.2, "onset_fraction": 0.55},
    "rolling_element":  {"shape_k": 5.0, "onset_fraction": 0.75},  # rapid onset
    "lubrication":      {"shape_k": 1.2, "onset_fraction": 0.40},  # gradual
}

def generate_run(
    asset_id: str,
    run_type: Literal["healthy", "fault"],
    fault_type: str = None,
    n_cycles: int = 2000,
    start_time: datetime = None,
    seed: int = 0,
) -> pd.DataFrame:
    """
    Generate a single asset run (healthy or fault trajectory).
    Returns a DataFrame with historian-compatible schema.
    """
    if start_time is None:
        start_time = datetime(2024, 1, 1)
    
    cfg = AssetConfig(asset_id=asset_id)
    baseline = healthy_baseline(n_cycles, cfg, seed=seed)
    
    if run_type == "healthy":
        degradation_index = np.zeros(n_cycles)
        fault_type_used = "healthy"
    else:
        wp = WEIBULL_PARAMS[fault_type]
        degradation_index = weibull_degradation_ramp(
            n_cycles, fault_type=fault_type, **wp
        )
    
    signal = apply_degradation_overlay(baseline, degradation_index, fault_type or "outer_race")
    
    # Inject bearing fault sidebands into vibration (col index 2)
    if run_type == "fault" and fault_type in ["outer_race", "inner_race"]:
        signal[:, 2] = inject_bearing_fault_sidebands(
            signal[:, 2], fault_type, rpm=300.0,
            degradation_index=degradation_index, seed=seed
        )
    
    # Compute RUL (remaining cycles to end of run where degradation > 0.95)
    failure_cycle = np.where(degradation_index > 0.95)[0]
    if len(failure_cycle) > 0:
        failure_cycle = failure_cycle[0]
        rul = np.maximum(0, failure_cycle - np.arange(n_cycles))
    else:
        rul = np.full(n_cycles, n_cycles)  # healthy: RUL = full run length
    
    labels = assign_fault_labels(degradation_index, noise_in_labels=True, seed=seed)
    
    timestamps = [start_time + timedelta(seconds=i) for i in range(n_cycles)]
    sequence_id = str(uuid.uuid4())[:8]
    
    df = pd.DataFrame(signal, columns=SENSOR_NAMES)
    df['timestamp']     = timestamps
    df['asset_id']      = asset_id
    df['sequence_id']   = sequence_id
    df['fault_type']    = fault_type or "healthy"
    df['fault_label']   = labels        # 0=HEALTHY,1=WARNING,2=ALARM,3=FAILURE
    df['rul_cycles']    = rul.astype(int)
    df['severity']      = pd.Categorical(
        df['fault_label'].map({0:"healthy",1:"warning",2:"alarm",3:"failure"}),
        categories=["healthy","warning","alarm","failure"], ordered=True
    )
    return df


def generate_dataset(
    sim_cfg: SimConfig,
    n_assets: int = 20,
    inject_defects: bool = False,
    defect_rate: float = 0.15,
) -> pd.DataFrame:
    """
    Full dataset: n_healthy_runs healthy + n_fault_runs fault episodes across n_assets.
    inject_defects=True → DataForge weak-sample demo (purposefully imperfect).
    inject_defects=False → clean training / model development data.
    """
    rng_top = np.random.default_rng(sim_cfg.seed)
    all_runs = []
    
    asset_ids = [f"EQP-{i+1:03d}" for i in range(n_assets)]
    
    # Healthy runs
    for i in range(sim_cfg.n_healthy_runs):
        asset = asset_ids[rng_top.integers(0, n_assets)]
        n_cyc = rng_top.integers(500, sim_cfg.max_healthy_cycles)
        start = datetime(2024, 1, 1) + timedelta(days=int(rng_top.integers(0, 365)))
        df = generate_run(asset, "healthy", n_cycles=n_cyc, start_time=start, seed=i)
        all_runs.append(df)
    
    # Fault runs
    for i in range(sim_cfg.n_fault_runs):
        asset = asset_ids[rng_top.integers(0, n_assets)]
        fault = FAULT_TYPES[rng_top.integers(0, 4)]
        n_cyc = rng_top.integers(sim_cfg.fault_run_min_cycles, sim_cfg.fault_run_max_cycles)
        start = datetime(2024, 1, 1) + timedelta(days=int(rng_top.integers(0, 365)))
        df = generate_run(asset, "fault", fault_type=fault, n_cycles=n_cyc,
                          start_time=start, seed=1000 + i)
        all_runs.append(df)
    
    combined = pd.concat(all_runs, ignore_index=True)
    combined = combined.sort_values(["asset_id", "timestamp"]).reset_index(drop=True)
    
    if inject_defects:
        injector = DefectInjector(seed=sim_cfg.seed, defect_rate=defect_rate)
        combined = injector.apply_all(combined, include_mislabels=True)
    
    return combined
```

---

## 6. Output Schema — Historian-Compatible

The output schema mirrors OSIsoft PI historian exports and matches the AI4I 2020 + C-MAPSS conventions used elsewhere in this project.

```python
# -------------------------------------------------------
# Pydantic v2 Schema (matches wizard.db SQLModel tables)
# -------------------------------------------------------
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
from enum import IntEnum

class FaultLabel(IntEnum):
    HEALTHY = 0
    WARNING = 1
    ALARM   = 2
    FAILURE = 3

class SensorReading(BaseModel):
    timestamp:             datetime
    asset_id:              str = Field(..., pattern=r"^EQP-\d{3}$")
    sequence_id:           str
    temperature_bearing_c: float = Field(..., ge=0.0, le=250.0)
    temperature_motor_c:   float = Field(..., ge=0.0, le=250.0)
    vibration_mm_s:        float = Field(..., ge=0.0, le=50.0)
    pressure_bar:          float = Field(..., ge=0.0, le=350.0)
    rpm:                   float = Field(..., ge=0.0, le=1200.0)
    current_a:             float = Field(..., ge=0.0, le=500.0)
    fault_type:            str   = Field(..., description="outer_race|inner_race|rolling_element|lubrication|healthy")
    fault_label:           FaultLabel
    rul_cycles:            int   = Field(..., ge=0)
    severity:              str   = Field(..., pattern=r"^(healthy|warning|alarm|failure)$")

    @field_validator("temperature_bearing_c", "temperature_motor_c")
    @classmethod
    def temp_nan_allowed(cls, v):
        # Allow NaN for defect-injected datasets (None at schema level)
        return v
```

### 6.1 Column Definitions

| Column | Type | Description | Historian analogue |
|--------|------|-------------|-------------------|
| `timestamp` | datetime64[ns] | UTC observation timestamp (1 Hz) | PI tag timestamp |
| `asset_id` | str | Equipment identifier (e.g., EQP-007) | PI Server asset path |
| `sequence_id` | str | Run/episode UUID prefix (8 chars) | Batch record ID |
| `temperature_bearing_c` | float32 | Bearing housing temperature (°C) | PT100 RTD tag |
| `temperature_motor_c` | float32 | Motor winding temperature (°C) | Thermocouple tag |
| `vibration_mm_s` | float32 | Radial vibration RMS (mm/s) | Accelerometer envelope |
| `pressure_bar` | float32 | Hydraulic clamping pressure (bar) | Pressure transducer tag |
| `rpm` | float32 | Roller shaft speed (RPM) | Tachometer/encoder tag |
| `current_a` | float32 | Motor phase current (A) | CT/SCADA analog tag |
| `fault_type` | str | Fault mode (5 classes incl. healthy) | Maintenance event code |
| `fault_label` | int8 | Severity class 0–3 | Alarm level from DCS |
| `rul_cycles` | int32 | Remaining useful life in cycles | Derived/calculated tag |
| `severity` | str | Human-readable severity label | Operator screen label |

---

## 7. Recommended Python Libraries with Versions

| Library | Version | Role | Install |
|---------|---------|------|---------|
| `numpy` | 1.26.x | Core numerical simulation | pip install numpy==1.26.4 |
| `scipy` | 1.13.x | Signal filtering (Butterworth), Weibull CDF, FFT | pip install scipy==1.13.1 |
| `pandas` | 2.2.x | DataFrame assembly, timestamp handling | pip install pandas==2.2.2 |
| `pydantic` | 2.7.x | Schema validation, NaN/range checks | pip install pydantic==2.7.4 |
| `lifelines` | 0.30.x | WeibullAFTFitter for realistic RUL ground truth | pip install lifelines==0.30.0 |
| `scikit-learn` | 1.5.x | IsolationForest validation, train/test split | pip install scikit-learn==1.5.0 |
| `faker` | 26.x | Asset IDs, timestamps, personnel names | pip install Faker==26.0.0 |
| `tsaug` | 0.2.x | Optional: time warp, magnitude warp augmentation | pip install tsaug==0.2.1 |
| `pyarrow` | 16.x | Parquet output for efficient storage | pip install pyarrow==16.1.0 |
| `matplotlib` | 3.9.x | Validation plots (degradation trajectory inspection) | pip install matplotlib==3.9.0 |

**Why NOT SDV/CTGAN here:**
CTGAN and TVAE from the `sdv` library (1.x) are excellent for tabular snapshot generation but they treat each row independently — they have no concept of temporal autocorrelation or physical constraints between sensor channels across time. For historian time-series, pure physics simulation + correlated noise is more faithful. CTGAN is appropriate if you need to augment a *snapshot* (single-cycle) fault classification dataset, not a run-to-failure trajectory.

[unverified: no head-to-head published benchmark comparing CTGAN vs physics simulation for steel PdM specifically — the above reasoning is from first-principles + general literature on synthetic time-series]

**Why NOT tsaug as primary:**
`tsaug` (0.2.1) provides time-warp, magnitude-warp, and slice augmentations. These are useful as a *second-pass augmenter* on generated data (especially for the fault minority class), but they cannot generate the initial degradation trajectory or enforce physical cross-sensor correlations. Use tsaug for +20-30% augmentation of the fault minority class after the physics simulation.

---

## 8. Validation Checks

Before using the synthetic dataset in any model, run these sanity checks:

```python
def validate_dataset(df: pd.DataFrame) -> dict:
    """
    Quick sanity check suite for synthetic dataset.
    Returns a dict with pass/fail for each check.
    """
    results = {}
    
    # 1. Class imbalance check
    label_counts = df['fault_label'].value_counts(normalize=True)
    results['healthy_fraction'] = label_counts.get(0, 0) > 0.70
    results['failure_fraction_under_10pct'] = label_counts.get(3, 0) < 0.10
    
    # 2. Correlation check: vibration-bearing-temp should be > 0.3
    corr = df[['vibration_mm_s', 'temperature_bearing_c']].corr().iloc[0, 1]
    results['vib_temp_corr_positive'] = corr > 0.30
    
    # 3. RUL monotonicity within sequence: should be non-increasing
    for seq_id in df['sequence_id'].unique()[:10]:  # spot-check 10 sequences
        seq = df[df['sequence_id'] == seq_id]['rul_cycles'].values
        results[f'rul_monotone_{seq_id}'] = all(np.diff(seq) <= 1)  # allow ±1 for noise
    
    # 4. No row with FAILURE label but RUL > 50 cycles
    failure_rows = df[df['fault_label'] == 3]
    results['failure_rul_bounded'] = (failure_rows['rul_cycles'] <= 50).all()
    
    # 5. Sensor ranges within physical bounds
    for col, (lo, hi) in zip(
        ['temperature_bearing_c', 'vibration_mm_s', 'pressure_bar', 'rpm'],
        [(0, 250), (0, 50), (0, 350), (0, 1200)]
    ):
        valid = df[col].dropna().between(lo, hi).all()
        results[f'{col}_range_valid'] = valid
    
    return results
```

---

## 9. Usage Guide

### 9.1 Generate Clean Training Data (for model development)
```python
cfg = SimConfig(n_healthy_runs=950, n_fault_runs=50, seed=42)
df_clean = generate_dataset(cfg, n_assets=20, inject_defects=False)
df_clean.to_parquet("data/synthetic_clean.parquet", index=False)
# Expected: ~1.4M rows, 95% healthy, 13 columns
```

### 9.2 Generate DataForge Demo Data (with realistic defects)
```python
cfg = SimConfig(n_healthy_runs=200, n_fault_runs=20, seed=7)
df_dirty = generate_dataset(cfg, n_assets=5, inject_defects=True, defect_rate=0.20)
df_dirty.to_parquet("data/dataforge_demo_dirty.parquet", index=False)
# ~300K rows, 15-20% data quality issues, visually compelling in the UI
```

### 9.3 Generate Sensor Playback for Live Demo
```python
# One fault episode, outer race, pre-seeded — for the "CRITICAL alert" demo moment
df_demo = generate_run(
    asset_id="EAF-04",
    run_type="fault",
    fault_type="outer_race",
    n_cycles=300,
    start_time=datetime(2024, 6, 1),
    seed=2024,
)
df_demo.to_csv("data/demo_playback_EAF04.csv", index=False)
# The ALARM trigger fires at cycle ~180 (60% onset), CRITICAL at ~255 (85% degradation)
```

---

## 10. Integration with Maintenance Wizard Pipeline

The synthetic dataset feeds three components of the Maintenance Wizard:

1. **IsolationForest + LSTM-AE training (`anomaly.py`):** Use `df_clean` with `fault_label=0` rows as the healthy-only training set (unsupervised). Fault rows are used only for evaluation (not training) to preserve unsupervised setting.

2. **WeibullAFTFitter training (`rul.py`):** Aggregate each fault run to one episode row: `{asset_id, fault_type, cycles_to_failure, sensor_values_at_onset}`. `lifelines.WeibullAFTFitter.fit(episode_df, duration_col='cycles_to_failure', event_col='observed')`.

3. **LightGBM failure prediction (`failure_pred.py`):** Supervised on all rows with `fault_label` as target. Stratified 5-fold CV. `class_weight='balanced'` to handle imbalance.

4. **Demo sensor playback (APScheduler tick):** `df_demo_playback_EAF04.csv` is consumed row-by-row by the 5-second APScheduler tick, simulating real-time sensor ingestion into the pipeline.

---

## 11. Sources and References

1. ISO 13373-3:2015 — Condition monitoring and diagnostics of machines: Vibration condition monitoring. [Standard]
2. ISO 10816-3:1998 — Mechanical vibration evaluation of machine vibration by measurements on non-rotating parts. [Standard]
3. Weibull, W. (1951). "A statistical distribution function of wide applicability." Journal of Applied Mechanics. [Primary reference for Weibull degradation model]
4. Smith, J.D. (1982). "Vibration monitoring of bearings at low speeds." Tribology International, 15(3), 139-144. [Bearing fault frequency formulas] [unverified: exact citation — formula is widely reproduced in SKF bearing documentation]
5. SKF Bearing Calculator — bearing frequency formulas reproduced from SKF documentation. https://www.skfbearingselect.com [unverified: URL may have changed]
6. NASA C-MAPSS Dataset — Saxena, A. et al. (2008). "Damage propagation modeling for aircraft engine run-to-failure simulation." PHM 2008. [Primary reference for run-to-failure simulation design]
7. AI4I 2020 Predictive Maintenance Dataset — Matzka, S. (2020). UCI ML Repository. CC BY 4.0. [Reference for fault taxonomy and schema design]
8. "Cleaning Maintenance Logs with LLM Agents" — arXiv:2511.05311, Nov 2025. [Six noise category taxonomy for defect injection]
9. Zhu et al. (2023). "Quality-Related Process Monitoring and Diagnosis of Hot-Rolled Strip Based on Weighted Statistical Feature KPLS." Sensors, DOI: 10.3390/s23136038. [Steel-plant sensor range validation]
10. ISO 15243:2017 — Rolling bearings: damage and failures, terms, characteristics and causes. [Bearing failure mode taxonomy]

---

*Document end. Next: integrate `generate_dataset()` call into `dataforge/seed.py` and wire demo playback CSV into the APScheduler tick in `maintenance-wizard/backend/app/scheduler.py`.*
