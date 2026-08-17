# V20 Build Report

## Overview
Two genuinely untried approaches vs V5 stacking baseline (OOF AUC 0.8886, LB 56.98).

---

## Track 1 — TabPFN Cloud

**Status: FAILED — requires interactive account login**

tabpfn-client 0.3.0 installed successfully but blocks on first call with an interactive
registration/login prompt (PriorLabs account). No anonymous access available.
The process hung waiting for user input and had to be killed.

- OOF AUC: N/A
- LB estimate: N/A
- Action: Would need manual `tabpfn-client login` from a terminal session, then re-run.

---

## Track 2 — NCA-learned metric + distance-weighted KNN

**Status: COMPLETED — underperforms V5**

5-fold StratifiedKFold results:

| Fold | AUC    |
|------|--------|
| 1    | 0.7522 |
| 2    | 0.8148 |
| 3    | 0.6636 |
| 4    | 0.9136 |
| 5    | 0.7719 |
| **Mean OOF** | **0.7849** |

- V5 baseline OOF AUC: 0.8886
- Delta vs V5: **-0.1037** (significantly worse)
- Best OOF score (Recall+Prec)/2*100: 42.64 @ threshold=0.0524
- Recall=0.712, Precision=0.141, N_test_predictions=76
- Est LB range (raw): 42.64 -- 45.34 (even with +2.7 calibration bonus)

**Root cause:** NCA-KNN is fundamentally a lazy learner. With only 66 positives in 1352 rows
(4.88% prevalence), the NCA linear projection cannot learn a clean separation for this
extreme imbalance. Tree-based ensembles handle this far better via splitting + class weighting.
Fold 3 (AUC=0.6636) is near-random — NCA diverged in that split's minority distribution.

---

## V5 OOF Blend Attempt (sanity check)

Not attempted — submission log shows blends are catastrophic for this scoring metric
(V10 blend: 47.00 vs V4 single: 56.98). Blending probabilities kills precision without
recovering enough recall on this (Recall+Prec)/2 metric.

---

## Verdict

| Track | Works? | OOF AUC | Est LB | Vs V4 banked |
|-------|--------|---------|--------|--------------|
| TabPFN cloud | NO (auth required) | — | — | — |
| NCA-KNN | YES (runs) | 0.7849 | ~42-45 | WORSE by ~15 pts |
| V4 banked | — | 0.884 | 56.98 | BASELINE |

**DO NOT SUBMIT V20.** NCA-KNN is substantially worse than V4 (OOF -0.1037 AUC,
estimated LB 42-45 vs 56.98 banked). Submitting would not improve standing.

---

## Path Forward

V4 (56.98) remains the best submission. Gap to top-10 (80.6) is ~23.6 points.
Approaches exhausted: LGBM/XGB/CatBoost stacking, coil-neighbor features, V5 physics
features, blends (catastrophic), NCA-KNN (underperforms), TabPFN (auth blocked).

Options left worth trying:
1. **TabPFN with manual login** — if auth is resolved, TabPFN's Bayesian prior on small tabular
   data could be competitive. Register at app.priorlabs.ai then `tabpfn-client login` in terminal.
2. **FT-Transformer (tabular deep learning)** — can capture feature interactions trees miss.
   Implementation: `pip install pytorch-frame` or rtdl. Expensive but possible locally.
3. **UMAP + HDBSCAN anomaly detection** — treat defects as anomalies in unsupervised space,
   since 90%+ scorers may be using the structural separation property.
4. **Accept current standing** — 56.98 is solid given honest ML ceiling appears ~57 without
   data leakage / LB probing. Two contestants at 100.00 are likely probing.
