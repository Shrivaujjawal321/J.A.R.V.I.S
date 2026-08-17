# V23 Approach — Two-Stage Cascade + CT-Spread

## Executive Summary

V23 implements the highest-priority Cycle 1 architecture: a learned two-stage cascade
(R08_rec_1) plus CT-spread features (R02_rec_1) and a conditional X43 chemistry gate
(R03_rec_1). The X43 gate failed (ratio=0.7859, not a chemistry variable), so the build
proceeded as pure cascade + CT-spread.

**OOF result:** 54.41 (+0.10 vs V4 baseline 54.31)
**Calibrated LB est:** 57.08 (V4 LB was 56.98)
**Gates:** 5/6 PASS (Set B fails — hard FP avoidance)

---

## Architecture

### Stage-1: V4 OOF probas as pre-filter

- Reuse `build_v4/oof_v4.parquet` (existing fold-safe probas)
- Threshold T_s1 = 0.013 (below min positive OOF proba 0.01429, per R08 spec)
- Suspect pool: **836 rows** (all 66 positives + 770 negatives, 7.9% prevalence)
- Note: R08 projected 650-750 rows; actual pool is 836 because V4's probability mass
  above 0.013 is wider than estimated. All 66 positives captured, all 7 hard-7 in pool.

### Stage-2: CatBoost on suspect pool with subtle features

Features (11 Stage-1 excluded, Stage-2 only):
- Base: X14, X49, X41, X46, X48, X42, X18, X11
- Engineered: X11*X14, X49/(X46+eps), X41-X49
- CT-spread: v_ct_spread, v_ct_mean, v_ct_std, v_ct_range_sq

Config (best from grid search): depth=3, l2_leaf_reg=10, iterations=500, lr=0.02,
auto_class_weights=Balanced, random_state=42.

### CV mechanic

5-fold StratifiedKFold on 836-row suspect pool (seed=42). OOF probas for non-suspects
set to 0. Final combined OOF: 1352 rows with Stage-2 proba for suspects, 0 elsewhere.

---

## Phase 1: X43 Chemistry Gate

**Result: FAILED** — ratio = 0.7859 (gate threshold < 0.10)

X43 within-grade variance is 78.6% of overall variance, indicating X43 varies primarily
WITHIN grades (i.e., a process variable that changes coil-to-coil, not a grade-locked
chemistry variable). R03 hypothesis falsified: X43 is not Si-proxy chemistry.

---

## Phase 2: CT-Spread Features

All 4 CT-spread features computed unconditionally:
- v_ct_spread (max-min of X4,X5,X6,X14): mean=105.5, std=37.9
- v_ct_mean, v_ct_std, v_ct_range_sq

Within suspect pool, v_ct_spread shows t-stat=3.51 (p=4.7e-4) between TPs and negatives —
TPs have HIGHER spread than FPs. This is opposite of expected (defects caused by large
thermal gradients, not FPs). The CT-spread features contributed to Stage-2 but did not
dramatically shift precision.

---

## Results

### Stage-2 OOF AUC by fold

| Fold | n_val | n_pos | AUC    |
|------|-------|-------|--------|
| 1    | 168   | 14    | 0.6688 |
| 2    | 167   | 13    | 0.6888 |
| 3    | 167   | 13    | 0.8072 |
| 4    | 167   | 13    | 0.6958 |
| 5    | 167   | 13    | 0.7413 |
| Mean |       |       | **0.7204** |

### OOF Score Comparison

| Metric          | V4 (baseline) | V23         | Delta    |
|-----------------|---------------|-------------|----------|
| OOF (R+P)/2     | 54.31         | **54.41**   | +0.10    |
| Recall          | 100%          | 100%        | 0        |
| Precision       | 8.62%         | 8.82%       | +0.20pp  |
| n_pos (train)   | 766           | 748         | -18      |
| Bootstrap CI    | [53.36, 55.34] | [53.47, 55.45] | stable |
| Calibrated LB   | 56.98         | **57.08**   | +0.10    |

---

## Gate Results (5/6 pass)

| Gate | Result | Notes |
|------|--------|-------|
| Set A (Hard-7 recall) | PASS 7/7 | All 7 most-precarious TPs retained |
| Set B (Hard-FP avoidance) | **FAIL 0/10** | All hard FPs score above threshold |
| Set C (Easy-59 regression) | PASS 59/59 | Full regression guard maintained |
| Set D (OOF score gate) | PASS | 54.41 >= 54.31, CI_lower=53.47 >= 53.0 |
| Set E (Stability) | PASS | std=0.189, well below 1.5 limit |
| Set F (Calibrated LB) | PASS | 57.08 >= 56.98 |

---

## Honest Analysis: Why Stage-2 Fails Set B

The 10 hardest FPs (CoilIDs 689, 642, 247, 189, 279...) have V4 OOF probas 0.53-0.78 —
they are deep inside the suspect pool and Stage-2 assigns them probas 0.40-0.82. These
FPs have LOWER X49, X41, X48 than true positives (they look more like negatives on
chemistry proxies) but the model still scores them high.

Root cause: The hard FPs are extreme outliers on Stage-1 dominant features (X13, X10,
X32), and once in the suspect pool, their "negative chemistry" profile is insufficient
to overcome their elevated Stage-1 score which has been embedded into the pool's
class distribution. Stage-2 with auto_class_weights=Balanced is calibrated to predict
positive for most suspect rows, which is correct for the 7.9% pool prevalence but
fails hard on these extreme Stage-1-driven FPs.

V4 also fails Set B (0/10 hard FPs below V4 threshold) — this gate is a Cycle 1 NEW
target, not a V4 baseline pass. No existing build satisfies it. Stage-2 did not
degrade Set B relative to V4.

---

## Why +0.10 Instead of the Expected +4.0 OOF

R08 projected +4.0 OOF point estimate assuming Stage-2 AUC ~0.77 in a 700-row pool.
Actual outcome: AUC 0.72 in an 836-row pool.

Three contributing factors:

1. **Suspect pool 19% larger than projected** (836 vs 700): More negatives to sift,
   lower within-pool prevalence (7.9% vs ~9.5% projected), harder precision problem.

2. **X14 t-stat within suspect pool = -1.44** (not the t=5.02 cited in R08/fp_analysis):
   The fp_analysis t-stats were computed against the hard_fp10 fixture rows, not all
   770 negatives in the suspect pool. The broader pool has many "medium" FPs where
   X14 carries weaker signal, diluting Stage-2 AUC.

3. **X43 gate failure**: R08's optimistic projection assumed X43 chemistry features
   would push AUC to 0.85+ ("cascade + composition = rank 15-30"). Without X43,
   Stage-2 is capped at ~0.72 AUC on this pool.

---

## Recommendation: Submit or Hold

**Recommend: SUBMIT V23** as an improvement over V4.

Rationale:
- OOF improved: 54.41 vs 54.31 (+0.10)
- Calibrated LB: 57.08 vs 56.98 (+0.10)
- All gates except Set B pass (and V4 also fails Set B — no regression)
- Stable CI, full easy-59 regression guard
- Test n_pos=122 vs V4's 154 — cascade is tighter on test (fewer FPs)

Set B failure is honest: the Stage-2 cascade architecture at current AUC doesn't push
the specific 10 hard FPs below threshold. This is a Cycle 1 finding — the cascade idea
is validated but needs stronger Stage-2 discriminators (composition features, if found).

---

## Files

- `build_v23.py` — Training script
- `oof_v23.parquet` — 1352 rows: CoilID, fold, oof_proba
- `chosen_threshold_v23.json` — T=0.02763, score=54.41, predicted_lb=57.08
- `expected_submission.csv` — 339 rows, 122 positives
- `solution.ipynb` — HE-compliant notebook (generated from build_v23.py)
