# V53 CV Report — Caruana Greedy Ensemble

**Date:** 2026-05-24
**Banked best:** V44 K=200 = 72.83 LB
**Algorithm:** Caruana 2004 greedy forward selection with replacement
**Metric:** F1@K=200 on OOF (n_pos=66, K=200)
**Iterations:** 100

---

## OOF F1@K=200 Summary

| Method | OOF F1@K=200 | Delta vs Equal-Vote |
|--------|-------------|---------------------|
| **Caruana Greedy (V53)** | **0.390977** | **+0.022556** |
| Equal-vote all paradigms | 0.368421 | 0.000000 |
| Equal-vote V44 subset (5 paradigms) | 0.360902 | -0.007519 |

---

## Individual Paradigm OOF F1@K=200

| Paradigm | Individual F1@K=200 | Caruana Weight | Selection Count |
|----------|---------------------|----------------|-----------------|
| V51_mean | 0.360902 | 0.0100 | 1 |
| V39 | 0.353383 | 0.6500 | 65 |
| V34_meta | 0.345865 | 0.0000 | 0 |
| V43 | 0.345865 | 0.0100 | 1 |
| V50 | 0.345865 | 0.0000 | 0 |
| V44_consensus | 0.345865 | 0.0000 | 0 |
| V4 | 0.345865 | 0.0000 | 0 |
| V35_rank | 0.330827 | 0.0000 | 0 |
| V41 | 0.330827 | 0.0000 | 0 |
| V46 | 0.330827 | 0.0000 | 0 |
| V33 | 0.323308 | 0.0300 | 3 |
| V48_rank | 0.323308 | 0.0000 | 0 |
| V40 | 0.105263 | 0.3000 | 30 |

---

## Gates

- **Gate 1 (Caruana >= equal-vote):** PASS
- **Gate 2 (max weight < 80%):** PASS — max=V39 @ 0.6500
- **Gate 3 (Spearman vs V44 >= 0.80):** PASS — ρ=+0.9796

---

## Submission Overlap with V44 K=200 (banked 72.83)

| K | V53 Top-K Overlap with V44 K=200 |
|---|-----------------------------------|
| 154 | 154/154 |
| 170 | 169/170 |
| 181 | 176/181 |
| 197 | 188/197 |
| 200 | 189/200 |
| 205 | 190/200 |
| 212 | 191/200 |

---

## Top-3 Risks

1. **OOF overfitting to calibration:** Isotonic calibration on OOF (Option C) is valid
   because all base models used identical fold splits. Risk level: LOW — 100 iterations
   on N=13 models is well within safe regime (< 150 iterations cap per R25).

2. **V4_binary test score:** V4's test score is binary (0/1 expected submission), not a
   continuous probability. If Caruana assigns non-trivial weight to V4, the test ensemble
   may have discontinuities near the K cutoff. Check: if V4 weight > 20%, validate that
   submission_K200 overlap with V44 is still ≥ 0.80.

3. **OOF F1@K vs LB F1@K gap:** Per R28 (OOF calibration not LB calibration), post-hoc
   rules validated on OOF can diverge from LB by up to ±1.5 points. V27 showed this.
   Mitigated here by using F1@K (not threshold-based) — ranking is more robust than
   classification calibration.

---

## Architecture Notes

- Paradigm signals loaded: V4_meta (OOF), V33, V34_meta, V35_rank, V39, V40, V41,
  V43, V46, V48_rank, V50, V51_mean, V44_consensus (13 total)
- Calibration: IsotonicRegression per paradigm on OOF scores before greedy
- Test ensemble: weighted sum of RAW test scores (calibration affects selection, not ranking)
- V44_consensus included as a synthetic candidate so greedy can 'pick V44 alone' if optimal
- Spearman sanity vs V44 ensures V53 is not an orthogonal direction from the banked best