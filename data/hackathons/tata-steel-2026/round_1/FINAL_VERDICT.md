# Tata Steel Hackathon Round 1 — Final Verdict After 4 Cycles

**Date:** 2026-05-23
**Status:** ML-honest ceiling confirmed at LB ~58. 90% target unreachable without leaderboard probing.

## Build Summary (chronological)

| # | Build | OOF | Calibrated LB | Verdict |
|---|---|---|---|---|
| 1 | V2 | ~50 | **50.19 actual** | early baseline |
| 2 | V4 | 54.31 | **56.98 actual** | BANKED on LB |
| 3 | V5 (physics) | 53.70 | 56.37 | marginal |
| 4 | V6 (FT-Transformer) | 54.11 | 56.78 | architecture didn't help |
| 5 | V7 (chemistry) | 53.14 | 55.81 | regressed |
| 6 | V8 (hierarchical gate) | 53.78 | 56.45 | gate works, AUC drops |
| 7 | V9 (full-train+TabPFN) | 53.71 | 56.38 | TabPFN blocked |
| 8 | **V10 (V5+V8+V9 mean)** | **55.47** | **58.14** | **best honest** |
| 9 | V11 (within-grade Z) | 54.97 | 57.64 | doesn't help |
| 10 | V12 (Optuna+bagging) | 55.02 | 57.69 | doesn't help |

## What Was Tried (Exhaustive)

### Architectures (7)
- LGB+XGB+CatBoost stacking (V4, V5)
- FT-Transformer (V6) — too few rows
- Anomaly detection ensemble (Cycle 1C) — exhausted
- PU learning (Cycle 1D) — exhausted
- Hierarchical gating (V8) — works partially
- Full-train + TabPFN attempt (V9) — license blocked
- Multi-seed bagging + Optuna (V12) — hurt

### Feature Engineering (5 sets)
- Coil neighbor temporal (V4)
- Physics: Ar3, Ekelund, lambda (V5)
- Chemistry: X42, X46, Si/Mn, CarbonEq (V7)
- Within-grade z-scores (V11)
- All stealth-defect signature features (cycle 3)

### Calibration / Threshold
- Score-aware (R+P)/2 sweep (all builds)
- Platt calibration via CalibratedClassifierCV (all)
- Bootstrap CI 95% (all)
- V4 actual-vs-OOF gave +2.67 calibration delta (used throughout)

### Class Imbalance
- SMOTE (V2)
- class_weight=balanced (all V5+)
- scale_pos_weight (XGB)
- auto_class_weights Balanced (CatBoost)
- IsolationForest meta-feature (V2-V4)
- ADASYN (recommended but never tested — research-agent recommendation)
- PU learning (Cycle 1D)

### Research
- Swansea EngD thesis 2023 (Latham, Tata collab) read
- KPLS paper (PMC10346850)
- CTGAN/CatBoost HSLA crack paper (PMC12348153)
- 4 other published papers on HSM defect ML

## Mathematical Proof of Ceiling

V4 LB = 56.98 ⇒ test set has **~22 true defects** (back-solved from (R+P)/2 formula).
To reach LB 80: need R=1.0 + P=0.65 → predict top 34 with 22 TPs + 12 FPs.
To reach LB 90: need R=1.0 + P=0.80 → predict top 27 with 22 TPs + 5 FPs.

Best model (V10) Meta OOF AUC = 0.8936.
At AUC 0.89: top-22 prediction catches ~13/22 = 60% of true defects.
**AUC 0.95+ mathematically required for honest LB 80+.**
We achieve 0.89. Gap is structural — features don't separate the 7 stealth defects.

## Why the 100-Scorers Exist

Verified math: at HE's daily submission limit (≥3/day), **LB probing recovers all test labels in 6-15 submissions** via binary search. Two contestants have 100.00 — almost certainly probing.

HE T&C requires "reproducible code" — a hardcoded CSV in `solution.ipynb` technically passes since the same CSV reproduces. Whether HE judges manually flag this is unknown.

## Recommendation

**Submit V10 as final Round 1 deliverable. Move all energy to Round 2.**

- V10 calibrated LB 58.14 → expected rank ~50-70 (top half = Round 2 shortlist threshold met)
- The Tata Steel offer comes from Round 2 (agentic system) — Round 1 only filters
- Time spent on 90%+ cycling has DIMINISHING returns

V10 zip ready at: `data/hackathons/tata-steel-2026/round_1/build_v10/submission_v10.zip`

## Files of Value

- `CYCLE_LOG.md` — full cycle 1-4 narrative
- `cycle1/track_a_eda_findings.md` — Track A breakthrough (X39 + X42 gate)
- `cycle1/track_b_findings.md` — Swansea thesis findings, ML tricks
- `v6_breakthrough_research.md` — composition column identification
- `fp_analysis/` — 7 stealth defect forensic CSVs
- All build_v* dirs preserved
- `references/latham_2023_swansea_thesis.pdf` — downloaded for archive
