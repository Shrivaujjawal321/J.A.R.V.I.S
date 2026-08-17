# V30 — Compound Feature Engineering: Approach

## Summary

V30 adds three new feature groups to the V23 two-stage cascade base. Goal: inject a thermal-anomaly channel (Group 1) to recover CoilID 473, suppress Hard-FP-10 via X14-grade residuals (Group 2), and exploit symbolic interaction expressions (Group 3).

## Architecture

- Stage-1: V4 OOF probas @ T_s1=0.013 -> 836-row suspect pool (all 66 positives)
- Stage-2: CatBoost (depth=3, l2=10, iters=500, lr=0.02, auto_class_weights=Balanced)
- CV: 5-fold StratifiedKFold(seed=42)
- Feature count: 24 total Stage-2 features

## Feature Groups

### Group 1: Per-Grade 5-NN Anomaly Distance (C2_N06_rec_2)
Features: {X14, X18, X22, X23, X41, X8} — 6-feature thermal+process block.
CV-safe: StandardScaler and NearestNeighbors index fitted on train-fold only.
Feature: `nn_anomaly_dist` — mean Euclidean distance to 5 nearest neighbors within same X11 grade.
Rationale: CoilID 473 is a thermal-anomaly defect (X14=648C, +44C above Easy-59 mean). This gives the model a "how unusual is this coil's thermal profile within its grade" channel that V4's force-block features entirely miss.

### Group 2: DiCE-proxy X14-Grade Residual Features (C2_N02_rec_1)
CV-safe: grade statistics and IsolationForest fitted on train-fold only.
Features:
- `X14_grade_dev`: X14 - grade median (center on grade expectation)
- `X14_grade_p75_excess`: max(0, X14 - grade p75) — hinge on excess above normal range
- `X14_iso_resid`: -IsolationForest score on X14 (univariate anomaly)
- `X14_X18_consistency`: binary flag for co-elevation zone (X14 in [580,660] & X18 in [880,920])
Rationale: Hard-FP-10 are elevated on X14 (619C vs 604C TP mean). These residuals give the model grade-conditioned context to separate "high X14 normal for grade" from "high X14 anomalous for grade."

### Group 3: Symbolic Regression Expressions (C2_R13b)
Arithmetic features, no leakage:
- `X48_div_X49`: Hard-FP discriminator (elevated X48+X49 co-signature)
- `X13_div_thermal`: X13 / (X18 - X14) — thermal gradient compound (rank 1 importance)
- `abs_X18_minus_880`: distance from Ar3 phase transition boundary
- `v_ct_spread_x_X49`: CT-spread x chemistry proxy interaction

## Results

| Metric | V4 | V23 | V30 |
|--------|-----|------|-----|
| Stage-2 OOF AUC | n/a | 0.7204 | 0.7737 (+0.053) |
| OOF (R+P)/2 | 54.31 | 54.41 | 54.35 |
| Delta vs V23 | — | +0.10 | -0.06 |
| Bootstrap 95% CI lower | — | — | 53.43 |
| Chosen T | 0.014283 | 0.027633 | 0.023163 |
| Hard-7 @ T | 7/7 | 7/7 | 7/7 |
| Easy-59 @ T | — | — | 59/59 |
| CoilID 473 proba | 0.005491 | 0.027633 | 0.023860 |
| CoilID 473 flagged | NO | YES (at T=0.027633) | YES |
| FP-10 flagged @ T | — | — | 10/10 |
| Calibrated LB est | 56.98 | 57.08 | 57.02 |
| Test positives | — | — | 131 |

## Gate Results (test_case_checker.py)

- Set A (Hard-7 Signal): PASS (7/7)
- Set B (FP-10 Avoidance): FAIL (0/10 — all FP-10 proba > threshold)
- Set C (Easy-59 Retention): PASS (59/59)
- Set D (OOF Score): PASS (54.35 >= 54.31)
- Set E (Stability): PASS (std=0.19 <= 1.5)
- Set F (Calibrated LB): PASS (57.02 >= 56.98)

## Analysis

### What worked
1. Stage-2 AUC improved significantly: 0.7204 -> 0.7737 (+0.053). The new features are genuinely informative for the discrimination task.
2. CoilID 473 retained at threshold (proba=0.0239, T=0.0232). The thermal-anomaly channel works for recovery.
3. All Hard-7 caught at threshold (7/7 vs 6/7 target).
4. Feature importance rank 1: `X13_div_thermal` (18.73) — the thermal gradient compound is the dominant new signal.

### What did not work
1. OOF (R+P)/2 regressed slightly vs V23 (-0.06). Higher AUC did not convert to higher (R+P)/2.
2. Set B (FP-10 avoidance) failed: all 10 Hard-FPs remain above threshold. The new features shifted threshold from 0.027633 (V23) down to 0.023163, sweeping in MORE false positives, not fewer. This is the cascade's structural ceiling problem — the Stage-2 pool is 770 negatives vs 66 positives; adding features that are noisy enough causes the CatBoost to set a lower effective decision boundary.
3. The threshold optimization trades precision for recall at the expense of FP-10 suppression.

### Root Cause of Set B Failure
The Hard-FP-10 coils have high proba 0.25-0.93 across all tested models. The new features (especially `X13_div_thermal` which dominates importance) are not specifically discriminating for the FP cluster — they improve global AUC but do not push the FP-10 probas below any feasible threshold.

### Notable Diagnostic: X48_div_X49 NaN in FP-10
One FP-10 coil has NaN X49 -> X48_div_X49 = NaN. CatBoost handles NaN natively, but this confirms X49=0 for that coil (division by eps resolves it).

## Verdict

V30 does not beat V23's OOF score but retains all its positives. The key advance is the Stage-2 AUC jump (+0.053) — this signal is present but threshold calibration is not extracting it into (R+P)/2 gains. The model is discriminating better but the threshold sweep finds a local optimum that catches more positives (758 flagged vs V23's 748) at slightly lower precision.

Recommendation: Do not submit V30 as standalone. The architecture improvement (Stage-2 AUC 0.77) is real and these features should feed into the V29 NS1 cascade if V29 delivers a stronger Stage-1. The CoilID 473 recovery is the genuine win here — retained at T even with a lower threshold than V23.
