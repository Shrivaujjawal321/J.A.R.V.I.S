"""
feature_engineering.py — V34 Per-Stand Residual Feature Engineering
Copied directly from build_v33/feature_engineering.py.
Tata Steel Hot Rolling Defect Detection

CRITICAL: All setpoint statistics computed on TRAIN FOLD ONLY (Section 2 + Section 10 of RESEARCH_BRIEF_v33.md).
NO pd.concat([train, test]) allowed anywhere.

Stand ordering validation (AP-6):
  Temperature X4-X9: monotonically DECREASING (confirmed, F1=692°C → F6=461°C)
  Force X29-X33: monotonically INCREASING (confirmed, F1=6.9 → F5=17.1 MN, later stands apply more)

X35 analysis (actual data):
  - 946/1352 (70%) in HIGH mode (>1e6), median=13.9M
  - 406/1352 (30%) in LOW mode (≤1e6)
"""

from __future__ import annotations

import numpy as np
import pandas as pd

TEMP_COLS = ["X4", "X5", "X6", "X7", "X8", "X9"]   # F1-F6 finishing temperatures, monotonically decreasing
FORCE_COLS = ["X29", "X30", "X31", "X32", "X33"]    # F1-F5 stand forces, monotonically increasing
STAND_COLS = TEMP_COLS + FORCE_COLS
TARGET_COL = "Y"
ID_COL = "CoilID"


class StandSetpoints:
    """Holds train-fold-computed setpoints (medians, stds) — frozen for val/test transforms."""

    def __init__(self):
        self.temp_medians: pd.Series | None = None
        self.force_medians: pd.Series | None = None
        self.temp_stds: pd.Series | None = None
        self.force_stds: pd.Series | None = None
        self.x35_high_median: float | None = None
        self.x35_high_std: float | None = None
        self.is_fitted = False

    def fit(self, X_train_fold: pd.DataFrame) -> "StandSetpoints":
        """Fit all setpoint statistics on training fold rows ONLY."""
        self.temp_medians = X_train_fold[TEMP_COLS].median()
        self.force_medians = X_train_fold[FORCE_COLS].median()
        self.temp_stds = X_train_fold[TEMP_COLS].std().replace(0, 1e-9)
        self.force_stds = X_train_fold[FORCE_COLS].std().replace(0, 1e-9)

        # X35 within-high-mode stats (train fold only)
        if "X35" in X_train_fold.columns:
            high_mask = X_train_fold["X35"] > 1e6
            if high_mask.sum() > 5:
                self.x35_high_median = float(X_train_fold.loc[high_mask, "X35"].median())
                self.x35_high_std = float(X_train_fold.loc[high_mask, "X35"].std())
                if self.x35_high_std < 1e-9:
                    self.x35_high_std = 1e-9
            else:
                # Fallback: global X35 stats
                self.x35_high_median = float(X_train_fold["X35"].median())
                self.x35_high_std = float(X_train_fold["X35"].std()) or 1e-9

        self.is_fitted = True
        return self

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply frozen setpoints to any dataframe (val fold or test). Returns new df with engineered features."""
        assert self.is_fitted, "Must call fit() before transform()"
        df = df.copy()

        # ── Feature 1: Signed Temperature Residuals (6 features) ──────────────
        for i, col in enumerate(TEMP_COLS):
            median = self.temp_medians[col]
            df[f"res_temp_{i+1}"] = df[col] - median
            df[f"abs_res_temp_{i+1}"] = (df[col] - median).abs()

        # ── Feature 2: Signed Force Residuals (5 features) ────────────────────
        for i, col in enumerate(FORCE_COLS):
            median = self.force_medians[col]
            df[f"res_force_{i+1}"] = df[col] - median
            df[f"abs_res_force_{i+1}"] = (df[col] - median).abs()

        # ── Feature 3: Cumulative Process Deviation Score (z-weighted) ────────
        temp_z_resids = (df[TEMP_COLS] - self.temp_medians) / self.temp_stds
        force_z_resids = (df[FORCE_COLS] - self.force_medians) / self.force_stds
        all_z = pd.concat([temp_z_resids, force_z_resids], axis=1)
        df["cum_process_dev"] = all_z.abs().sum(axis=1)
        df["max_abs_z_dev"] = all_z.abs().max(axis=1)

        # ── Feature 3b: Simple cumulative force deviation (raw) ───────────────
        df["cum_force_dev_raw"] = (df[FORCE_COLS] - self.force_medians).sum(axis=1)
        df["max_abs_force_dev"] = (df[FORCE_COLS] - self.force_medians).abs().max(axis=1)
        df["max_abs_temp_dev"] = (df[TEMP_COLS] - self.temp_medians).abs().max(axis=1)

        # ── Feature 4: Max-Deviant Stand Index and Value ───────────────────────
        temp_res_cols = [f"res_temp_{s}" for s in range(1, 7)]
        df["worst_temp_stand"] = df[temp_res_cols].abs().values.argmax(axis=1).astype(float)
        df["worst_temp_mag"] = df[temp_res_cols].abs().max(axis=1)

        force_res_cols = [f"res_force_{s}" for s in range(1, 6)]
        df["worst_force_stand"] = df[force_res_cols].abs().values.argmax(axis=1).astype(float)
        df["worst_force_mag"] = df[force_res_cols].abs().max(axis=1)

        # ── Feature 5: Inter-stand temperature gradients ──────────────────────
        temp_cols_list = TEMP_COLS
        for i in range(len(temp_cols_list) - 1):
            df[f"temp_drop_{i+1}_{i+2}"] = df[temp_cols_list[i]] - df[temp_cols_list[i + 1]]

        # ── Feature 6: X35 Bimodal Decomposition (3 features) ────────────────
        if "X35" in df.columns:
            df["X35_is_high"] = (df["X35"] > 1e6).astype(float)
            df["X35_log1p"] = np.log1p(df["X35"])
            high_mask_df = df["X35"] > 1e6
            df["X35_high_mode_zscore"] = np.where(
                high_mask_df,
                (df["X35"] - self.x35_high_median) / self.x35_high_std,
                0.0,
            )
            # Interaction: edger-on × cumulative force
            df["X35_flag_x_cum_force"] = df["X35_is_high"] * df["cum_force_dev_raw"]

        # ── Feature 7: Temperature × Force cross-products at paired stands ────
        # X4-X8 × X29-X33 (5 paired stands; X9 is temp-only)
        for k in range(5):
            t_col = TEMP_COLS[k]   # X4, X5, X6, X7, X8
            f_col = FORCE_COLS[k]  # X29, X30, X31, X32, X33
            t_med = self.temp_medians[t_col]
            f_med = self.force_medians[f_col]
            # Residual cross-product (double-deviation signal)
            df[f"res_cross_{k+1}"] = (df[t_col] - t_med) * (df[f_col] - f_med)

        # ── Feature 8: Temperature span (total cooling range) ─────────────────
        df["temp_span"] = df[TEMP_COLS[0]] - df[TEMP_COLS[-1]]  # X4 - X9
        df["temp_entry"] = df[TEMP_COLS[0]]   # X4 entry temperature
        df["temp_exit"] = df[TEMP_COLS[-1]]   # X9 exit temperature

        # ── Feature 9: Force escalation (last/first force ratio) ──────────────
        f_first = df[FORCE_COLS[0]].replace(0, np.nan)
        f_last = df[FORCE_COLS[-1]]
        df["force_escalation_ratio"] = f_last / (f_first + 1e-6)

        # ── Feature 10: Log force columns (AP-5: handle heavy tails) ──────────
        for col in FORCE_COLS:
            df[f"log_{col}"] = np.log1p(df[col].clip(lower=0))

        return df


def validate_stand_ordering(train: pd.DataFrame) -> dict:
    """AP-6: Validate stand column ordering before feature engineering."""
    result = {}

    temp_means = train[TEMP_COLS].mean()
    temp_vals = temp_means.values
    is_temp_mono_dec = all(temp_vals[i] >= temp_vals[i + 1] for i in range(len(temp_vals) - 1))
    result["temp_mono_decreasing"] = bool(is_temp_mono_dec)
    result["temp_means"] = {col: float(v) for col, v in zip(TEMP_COLS, temp_vals)}

    force_means = train[FORCE_COLS].mean()
    force_vals = force_means.values
    is_force_mono_inc = all(force_vals[i] <= force_vals[i + 1] for i in range(len(force_vals) - 1))
    result["force_mono_increasing"] = bool(is_force_mono_inc)
    result["force_means"] = {col: float(v) for col, v in zip(FORCE_COLS, force_vals)}

    # Determine ordering status
    if is_temp_mono_dec:
        result["temp_order_status"] = "CONFIRMED_F1_TO_F6"
        result["temp_order_action"] = "Use as-is (X4=entry, X9=exit)"
    else:
        result["temp_order_status"] = "WARNING_NOT_MONOTONE"
        result["temp_order_action"] = "Investigate before sequential feature engineering"

    if is_force_mono_inc:
        result["force_order_status"] = "CONFIRMED_INCREASING_F1_TO_F5"
        result["force_order_action"] = "Physically correct — later stands apply more force on thinner strip"
    else:
        result["force_order_status"] = "WARNING_NOT_MONOTONE"
        result["force_order_action"] = "Investigate before sequential feature engineering"

    return result


def get_engineered_feature_names(base_cols: list[str]) -> list[str]:
    """Return the list of all engineered feature names that will be added."""
    engineered = []
    # Residuals
    for i in range(6):
        engineered += [f"res_temp_{i+1}", f"abs_res_temp_{i+1}"]
    for i in range(5):
        engineered += [f"res_force_{i+1}", f"abs_res_force_{i+1}"]
    # Aggregates
    engineered += ["cum_process_dev", "max_abs_z_dev", "cum_force_dev_raw",
                   "max_abs_force_dev", "max_abs_temp_dev"]
    # Max-deviant
    engineered += ["worst_temp_stand", "worst_temp_mag", "worst_force_stand", "worst_force_mag"]
    # Gradients
    for i in range(5):
        engineered.append(f"temp_drop_{i+1}_{i+2}")
    # X35
    engineered += ["X35_is_high", "X35_log1p", "X35_high_mode_zscore", "X35_flag_x_cum_force"]
    # Cross-products
    for k in range(5):
        engineered.append(f"res_cross_{k+1}")
    # Temp span
    engineered += ["temp_span", "temp_entry", "temp_exit"]
    # Force ratio
    engineered.append("force_escalation_ratio")
    # Log force
    for col in FORCE_COLS:
        engineered.append(f"log_{col}")
    return engineered
