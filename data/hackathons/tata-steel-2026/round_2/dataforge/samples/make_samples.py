"""
Generate 3 sample datasets for DataForge demo:
  1. good_tabular.csv       — clean, balanced, no issues → should score HIGH (85+)
  2. weak_tabular.csv       — missing values, severe imbalance, mislabels, dupes → LOW (35-50)
  3. timeseries_sensor.csv  — steel-plant sensors with timestamp + gaps → MEDIUM (60-75)
"""

from __future__ import annotations
import numpy as np
import pandas as pd
from pathlib import Path

RNG = np.random.RandomState(42)
OUT_DIR = Path(__file__).parent


# ---------------------------------------------------------------------------
# 1. GOOD TABULAR — failure classification, balanced, clean
# ---------------------------------------------------------------------------

def make_good_tabular(n: int = 2000) -> pd.DataFrame:
    """
    Simulated bearing failure classification dataset.
    8 features, ~50/50 class balance, clean labels, no missing.
    Features: vibration, temperature, rpm, load, age_days, maintenance_gap_days,
              oil_viscosity, motor_current
    """
    # Class 0 = normal, Class 1 = failure
    y = RNG.binomial(1, 0.48, size=n)

    vibration  = np.where(y, RNG.normal(8.5, 1.5, n), RNG.normal(2.0, 0.8, n)).clip(0, 30)
    temp_c     = np.where(y, RNG.normal(85.0, 8.0, n), RNG.normal(62.0, 6.0, n)).clip(20, 150)
    rpm        = np.where(y, RNG.normal(2800, 200, n), RNG.normal(3000, 150, n)).clip(0, 5000)
    load_pct   = np.where(y, RNG.normal(88.0, 8.0, n), RNG.normal(70.0, 10.0, n)).clip(0, 100)
    age_days   = RNG.gamma(shape=3, scale=100, size=n).clip(1, 2000)
    maint_gap  = np.where(y, RNG.gamma(3, 90, n), RNG.gamma(3, 40, n)).clip(1, 1000)
    oil_visc   = np.where(y, RNG.normal(28, 5, n), RNG.normal(46, 4, n)).clip(10, 100)
    current_a  = np.where(y, RNG.normal(42, 5, n), RNG.normal(35, 4, n)).clip(10, 80)

    df = pd.DataFrame({
        "vibration_mm_s":       vibration.round(3),
        "temperature_c":        temp_c.round(1),
        "rpm":                  rpm.astype(int),
        "load_pct":             load_pct.round(1),
        "age_days":             age_days.astype(int),
        "maintenance_gap_days": maint_gap.astype(int),
        "oil_viscosity_cst":    oil_visc.round(2),
        "motor_current_a":      current_a.round(2),
        "failure":              y,
    })
    return df


# ---------------------------------------------------------------------------
# 2. WEAK TABULAR — many issues injected
# ---------------------------------------------------------------------------

def make_weak_tabular(n: int = 1500) -> pd.DataFrame:
    """
    Same schema but with severe issues:
    - 55% missing in temperature (critical column)
    - 40% missing in oil_viscosity
    - 18% missing in vibration
    - Extreme imbalance: 3% failure rate (IR=32)
    - 15% duplicate rows
    - 10% mislabelled rows
    - Inf/extreme values in current
    - Constant column injected (dead sensor)
    """
    y = RNG.binomial(1, 0.03, size=n)  # extreme imbalance IR~32

    vibration  = np.where(y, RNG.normal(8.5, 1.5, n), RNG.normal(2.0, 0.8, n)).clip(0, 30).astype(float)
    temp_c     = np.where(y, RNG.normal(85.0, 8.0, n), RNG.normal(62.0, 6.0, n)).clip(20, 150).astype(float)
    rpm        = np.where(y, RNG.normal(2800, 200, n), RNG.normal(3000, 150, n)).clip(0, 5000)
    load_pct   = np.where(y, RNG.normal(88.0, 8.0, n), RNG.normal(70.0, 10.0, n)).clip(0, 100)
    age_days   = RNG.gamma(shape=3, scale=100, size=n).clip(1, 2000)
    maint_gap  = np.where(y, RNG.gamma(3, 90, n), RNG.gamma(3, 40, n)).clip(1, 1000)
    oil_visc   = np.where(y, RNG.normal(28, 5, n), RNG.normal(46, 4, n)).clip(10, 100).astype(float)
    current_a  = np.where(y, RNG.normal(42, 5, n), RNG.normal(35, 4, n)).astype(float)

    # Inject 55% missing in temperature (critical — dead thermocouple)
    miss_temp = RNG.choice(n, size=int(0.55 * n), replace=False)
    temp_c[miss_temp] = np.nan

    # 40% missing in oil_viscosity
    miss_oil = RNG.choice(n, size=int(0.40 * n), replace=False)
    oil_visc[miss_oil] = np.nan

    # 18% missing in vibration
    miss_vib = RNG.choice(n, size=int(0.18 * n), replace=False)
    vibration[miss_vib] = np.nan

    # Extreme values in current_a (bad sensor readings)
    extreme_idx = RNG.choice(n, size=40, replace=False)
    current_a[extreme_idx] = RNG.choice([-9999.0, 99999.0], size=40)

    df = pd.DataFrame({
        "vibration_mm_s":       vibration.round(3),
        "temperature_c":        temp_c.round(1),
        "rpm":                  rpm.astype(float),
        "load_pct":             load_pct.round(1),
        "age_days":             age_days.astype(int),
        "maintenance_gap_days": maint_gap.astype(int),
        "oil_viscosity_cst":    oil_visc.round(2),
        "motor_current_a":      current_a.round(2),
        "dead_sensor":          0,           # constant column — dead sensor
        "failure":              y,
    })

    # Inject mislabels (10%)
    n_mislabels = int(0.10 * n)
    mislabel_idx = RNG.choice(n, size=n_mislabels, replace=False)
    df.loc[mislabel_idx, "failure"] = 1 - df.loc[mislabel_idx, "failure"]

    # Inject duplicates (15%)
    n_dupes = int(0.15 * n)
    dupe_idx = RNG.choice(n, size=n_dupes, replace=False)
    dupes = df.iloc[dupe_idx].copy()
    df = pd.concat([df, dupes], ignore_index=True)

    return df


# ---------------------------------------------------------------------------
# 3. TIME-SERIES SENSOR — steel plant style with gaps
# ---------------------------------------------------------------------------

def make_timeseries_sensor(n: int = 3000) -> pd.DataFrame:
    """
    5-minute interval readings from a steel plant furnace/roller line.
    Features: temperature_c, vibration_mm_s, pressure_bar, rpm, current_a, torque_nm
    Label: failure_event (binary)
    Timestamp: synthetic with ~10% gap (missing intervals)
    """
    # Generate base timestamps at 5-min intervals but drop ~10% to create gaps
    base_start = pd.Timestamp("2025-01-01 00:00:00")
    all_ticks = pd.date_range(start=base_start, periods=int(n * 1.15), freq="5min")
    keep_mask = RNG.random(len(all_ticks)) > 0.10
    timestamps = all_ticks[keep_mask][:n]

    t = np.arange(n)

    # Temperature: slow sinusoidal drift (furnace cycle) + noise
    temp_c     = 820 + 60 * np.sin(2 * np.pi * t / 480) + RNG.normal(0, 12, n)
    vibration  = 3.5 + 0.8 * np.sin(2 * np.pi * t / 96) + RNG.exponential(0.4, n)
    pressure_bar = 2.8 + 0.2 * RNG.normal(0, 1, n)
    rpm        = 1450 + RNG.normal(0, 25, n)
    current_a  = 38 + 4 * np.sin(2 * np.pi * t / 192) + RNG.normal(0, 2, n)
    torque_nm  = 850 + 80 * np.sin(2 * np.pi * t / 192) + RNG.normal(0, 30, n)

    # Failure events: rare (~3%), correlated with high temperature + vibration
    failure_prob = (
        0.01
        + 0.15 * (temp_c > 880).astype(float)
        + 0.10 * (vibration > 5.0).astype(float)
    )
    failure_prob = np.clip(failure_prob, 0, 0.9)
    failure_event = RNG.binomial(1, failure_prob).astype(int)

    # Add a large gap (8-hour silence) in the middle for gap detection
    mid = n // 2
    mid_time = timestamps[mid]
    gap_end = mid_time + pd.Timedelta(hours=8)
    # Shift all timestamps after the midpoint
    timestamps_list = list(timestamps)
    for i in range(mid, len(timestamps_list)):
        timestamps_list[i] = timestamps_list[i] + pd.Timedelta(hours=8)

    # Missing values: ~5% in pressure and torque
    miss_pres = RNG.choice(n, size=int(0.05 * n), replace=False)
    miss_torq = RNG.choice(n, size=int(0.05 * n), replace=False)
    pressure_arr = pressure_bar.copy()
    torque_arr   = torque_nm.copy()
    pressure_arr[miss_pres] = np.nan
    torque_arr[miss_torq]   = np.nan

    df = pd.DataFrame({
        "timestamp":       timestamps_list,
        "temperature_c":   temp_c.round(1),
        "vibration_mm_s":  vibration.round(3),
        "pressure_bar":    pressure_arr.round(3),
        "rpm":             rpm.round(0).astype(float),
        "current_a":       current_a.round(2),
        "torque_nm":       torque_arr.round(1),
        "failure_event":   failure_event,
    })

    return df


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    OUT_DIR.mkdir(exist_ok=True)

    print("Generating sample datasets...")

    df_good = make_good_tabular(2000)
    path_good = OUT_DIR / "good_tabular.csv"
    df_good.to_csv(path_good, index=False)
    print(f"  1. good_tabular.csv: {len(df_good)} rows, {df_good.shape[1]} cols | "
          f"failure rate={df_good['failure'].mean()*100:.1f}%")

    df_weak = make_weak_tabular(1500)
    path_weak = OUT_DIR / "weak_tabular.csv"
    df_weak.to_csv(path_weak, index=False)
    miss_pct = df_weak.isnull().mean().mean() * 100
    print(f"  2. weak_tabular.csv: {len(df_weak)} rows, {df_weak.shape[1]} cols | "
          f"failure rate={df_weak['failure'].mean()*100:.1f}% | missing={miss_pct:.1f}%")

    df_ts = make_timeseries_sensor(3000)
    path_ts = OUT_DIR / "timeseries_sensor.csv"
    df_ts.to_csv(path_ts, index=False)
    print(f"  3. timeseries_sensor.csv: {len(df_ts)} rows, {df_ts.shape[1]} cols | "
          f"failure rate={df_ts['failure_event'].mean()*100:.1f}%")

    print(f"\nAll samples written to: {OUT_DIR}")
