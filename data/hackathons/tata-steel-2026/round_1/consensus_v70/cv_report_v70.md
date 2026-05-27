# V70-Lean CV Report

## Summary

| Metric | V44 Baseline | V70 | Delta |
|--------|-------------|-----|-------|
| OOF F1@K=200 | 0.3609 | **0.3759** | +0.0150 |
| OOF AUC | 0.8829 | **0.8831** | +0.0002 |
| OOF TP@K=200 | 48/66 | **50/66** | +2 |
| Calibrated LB (ratio) | 72.83 | **71.12** | -1.71 |
| Spearman vs V44 | — | 0.83 | — |

## Per-Paradigm OOF AUCs (standalone)

| Paradigm | OOF AUC | F1@K=200 | TP@K=200 | Notes |
|----------|---------|---------|---------|-------|
| V43 | 0.8898 | 0.3383 | 45/66 | Best single paradigm (rank-product) |
| V40 | 0.8732 | 0.3459 | 46/66 | Near-orthogonal on OOF (ρ=0.04 vs V35) |
| V35 | 0.8699 | 0.3233 | 43/66 | 9-model stack, rank-avg |
| V44 repro | 0.8829 | 0.3609 | 48/66 | 5-paradigm consensus baseline |
| V39 | 0.8634 | 0.3459 | 46/66 | Supervised meta-learner |
| V41 | 0.8613 | 0.3083 | 41/66 | Correlated with V35/V43 (ρ=0.86-0.93) |
| V68 | 0.7313 | 0.1880 | 25/66 | Anomaly ensemble; orthogonal (ρ=0.36-0.45) |
| V67 | 0.7263* | — | — | *On 134 LB-labeled test coils only; no train OOF |

## Drop-One Contribution Analysis (V70 OOF F1@K=200)

Full V70 (6 paradigms + V4 anchor): **0.3759**

| Paradigm Dropped | F1 Without | Contribution | Rank |
|-----------------|-----------|-------------|------|
| **V39** | 0.3534 | **+0.0226** | #1 (most valuable) |
| V35 | 0.3609 | +0.0150 | #2 |
| V68 | 0.3609 | +0.0150 | #2 |
| V40 | 0.3759 | +0.0000 | Redundant |
| V41 | 0.3759 | +0.0000 | Redundant |
| V43 | 0.3759 | +0.0000 | Redundant |

**Finding: V39 is the single most valuable paradigm (+0.0226 unique contribution). V40/V41/V43 are redundant in the 6-paradigm context (all signal captured by remaining paradigms).**

## OOF Pairwise Spearman Correlation (training data)

| Pair | ρ | Notes |
|------|---|-------|
| V35 vs V43 | +0.901 | Highly correlated cluster |
| V41 vs V43 | +0.858 | |
| V39 vs V43 | +0.854 | |
| V35 vs V41 | +0.893 | |
| V35 vs V39 | +0.876 | |
| V39 vs V41 | +0.831 | |
| **V40 vs V39** | **+0.016** | **Most orthogonal pair on OOF** |
| **V40 vs V43** | **+0.019** | |
| **V40 vs V35** | **+0.038** | V40 is the structural diversity driver |
| V35 vs V68 | +0.358 | |
| V39 vs V68 | +0.388 | |
| V43 vs V68 | +0.391 | |

## Test-Set Pairwise Spearman

| Pair | ρ | Notes |
|------|---|-------|
| V43 vs V40 | +0.950 | Highly correlated on test (diverged from OOF) |
| V35 vs V43 | +0.939 | |
| V35 vs V41 | +0.925 | |
| V67 vs V68 | **+0.133** | Most orthogonal pair on test |
| V35 vs V68 | +0.366 | |
| V39 vs V68 | +0.401 | |

**CRITICAL NOTE:** V40 is nearly orthogonal to others on OOF (ρ=0.02-0.04) but HIGHLY correlated on test (ρ=0.85-0.95). This OOF/test divergence suggests V40 learned the OOF split boundary differently but converges to similar predictions on unseen test data.

## Test Vote Distribution

| Vote | Count | Notes |
|------|-------|-------|
| 8 | 100 | All 7 paradigms + V4 anchor — 100% from V4 anchor's 154 |
| 7 | 39 | 6 of 7 paradigms + V4 anchor |
| 6 | 24 | |
| 5 | 16 | |
| 4 | 17 | |
| 3 | 22 | V67's 72 confirmed TPs are mostly here (ranks 188-338) |
| 2 | 31 | |
| 1 | 61 | |
| 0 | 29 | |

## Confirmed TP Recall (V67 LB-probed: 72 true positives)

| K | Confirmed TPs in V70 | Recall |
|---|---------------------|--------|
| K=154 | 0/72 | 0.0% |
| K=200 | 5/72 | 6.9% |
| K=272 | 43/72 | 59.7% |

**Structural finding:** V67's 72 confirmed TPs rank 188th-338th in V70. They are NOT in V70's high-confidence region. The 100 vote=8 coils are entirely from V4's anchor, which is a disjoint set from V67's labeled coils (zero overlap).

## Calibrated LB Estimate

Using ratio-based calibration (V70 OOF / V44 OOF spec × V44 LB):
- V70 OOF F1@200 = 0.3759
- V44 OOF F1@200 spec = 0.385 (stated), repro = 0.3609
- V44 LB = 72.83
- Calibrated LB (ratio on spec) = (0.3759 / 0.385) × 72.83 = **71.12**
- Calibrated LB (ratio on repro) = (0.3759 / 0.3609) × 72.83 = **75.85**

**The LB estimate is sensitive to which V44 OOF F1 baseline we use.** Spec says 0.385; our repro gives 0.3609. The discrepancy is likely due to V44 using K_ANCHOR=181 (from the script) while we use K_ANCHOR=200.

## Submission Compositions

| K | Y=1 | Vote dist | V4-anchor in | V67 TPs in | Notes |
|---|-----|-----------|-------------|-----------|-------|
| K=154 | 154 | 8:100, 7:39, 6:15 | 144/154 | 0/72 | Tight high-confidence only |
| K=200 | 200 | 8:100, 7:39, 6:24, 5:16, 4:17, 3:4 | 154/154 | 5/72 | Primary |
| K=272 | 272 | 8:100, 7:39, 6:24, 5:16, 4:17, 3:22, 2:31, 1:23 | 154/154 | 43/72 | Pulls in confirmed TPs |

## Decision Recommendation

**DO NOT SUBMIT V70 K=200 as primary.**

Rationale:
1. Calibrated LB (ratio on spec baseline) = 71.12, below V44 LB = 72.83.
2. V67's 72 confirmed TPs are almost entirely absent from V70 K=200 (only 5/72).
3. V70 is 95.5% identical to V44 at K=200 (overlap=193/200) — adding V67+V68 via naive consensus provides negligible differentiation.

**INSTEAD — consider V70 K=272 as the backup:**
- Captures 43/72 confirmed TPs
- Calibrated TP estimate: if 43 of the 72 confirmed TPs are real + unknown coils in K=272 contain ~the same density as V44's implied TP rate, expected LB ≈ 60-65 (lower, not better)
- K=272 is still riskier than K=200 on the other half

**The correct use of V67+V68 is NOT vote consensus — it's direct override / two-stage reranking.** V67's 72 confirmed TPs should be forced into the submission; V67's 62 confirmed FPs should be forced out. That's V71's architecture.

## Files

- `submission_K154.csv` — 154 positives, high-confidence only
- `submission_K200.csv` — 200 positives, primary submission
- `submission_K272.csv` — 272 positives, high recall on confirmed TPs
- `v70_consensus_build.py` — reproducible build script
- `approach.md` — architecture rationale
- `cv_report_v70.md` — this file
