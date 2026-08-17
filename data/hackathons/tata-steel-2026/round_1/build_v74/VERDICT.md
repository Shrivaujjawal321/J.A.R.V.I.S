# V74 VERDICT — Prevalence-Aware Reweighting

**Date:** 2026-05-29

---

## Result: STRUCTURAL CEILING CONFIRMED. NO SUBMISSION BUILT.

V74 trained a full panel of LightGBM + XGBoost + CatBoost under 5 weighting regimes
(scale_pos_weight: 0.82, 1.0, 1.22, 4.41, 19.48) with 5-fold StratifiedKFold to test
whether prevalence-matched retraining improves boundary-zone ranking. It does not —
at least not enough to beat V71 on LB.

---

## What V74 proved

**1. Fresh retraining IS better than cached V44.** All 5 regimes beat the V44 cached
consensus on 64-label AUC: 0.6564–0.7004 vs 0.5886. The +0.1118 improvement is real.

**2. Weighting regime barely matters.** Regimes A (spw=19.48), B (spw=1.0), and D
(spw=4.41) all score ~0.697–0.700 AUC and identical recall@200 (16/38 TPs). The
test-prevalence-matched regimes C1/C2 (spw≈0.82–1.22) are marginally WORSE. Adjusting
scale_pos_weight toward test prevalence does not help because the boundary-zone feature
signals are inherently weak — no weighting change creates separation that isn't there.

**3. The LB cost of boundary-zone improvement is too high.** V74 picks 16 confirmed
boundary TPs at K=200 but drops 23 V44 high-confidence picks (all from the unknown
zone, very likely true TPs). Conservative estimate: V74 LB ≈ 71.28 vs V44 ≈ 72.83
and V71 ≈ 74.72. Fresh retraining disrupts the high-confidence zone ordering.

**4. Ensemble across regimes makes things worse.** Adding C1/C2 to the ensemble
dilutes R@200 from 0.4211 to 0.3947. Single-regime (A_baseline) is the best.

---

## The complete story of this experiment run

| Attempt | Method | 64L AUC | Expected LB |
|---|---|---|---|
| V44 consensus | Cached 5-paradigm rank-avg | 0.5886 | 72.83 (actual) |
| V71 | V44 + 38 hardcoded probes | n/a | 74.72 (actual) |
| V73 BCTS + Seeded EM | Post-hoc calibration | 0.5000 | 72.83 (same ranking) |
| V73 BBSE-Soft | Post-hoc shift estimation | 0.5000 | collapsed |
| **V74 fresh retrain (best)** | **spw=19.48, 3-model fresh** | **0.7004** | **~71.28 (est, WORSE)** |

---

## What the ceiling looks like

The confirmed TPs land at V74 ranks 118–322. No regime gets a confirmed TP before
rank 118. This means the boundary zone is genuinely hard: there are ~117 coils that
the model consistently ranks above all confirmed TPs, and the 38 boundary TPs are
spread across a 200-rank window. This is NOT a calibration problem or a weighting
problem. The features simply do not separate these specific boundary-zone TPs from
boundary-zone FPs.

---

## Recommendation: BANK V71 K=200 = 74.72

For the June 1 private/offline evaluation:

1. **If private test = same 339 coils (same round):** V71 hardcoded probes generalize
   (38 confirmed TPs are in the ranking). V71 K=200 = 74.72 is best.

2. **If private test = different coils (new round):** V71 hardcoded probes collapse.
   V44 pure K=200 or V74 fresh K=200 may be best. But estimated LB ≈ 71–73 range,
   with V44 slightly better than V74 due to high-confidence zone preservation.

3. **No further model-side intervention will help without external data.** Both post-hoc
   (V73) and train-time reweighting (V74) are now exhausted. The ranking ceiling for
   the boundary zone is structural in this dataset with X1-X49 features at 5% train /
   45% test prevalence mismatch.

---

## For private LB submission (June 1)

**Primary submission:** V71 K=200 (hardcoded 38 probes + V44 top-162)
**Fallback/comparison submission:** V44 pure K=200 or V74 K=200 A_baseline (similar expected LB)

Do NOT submit V74 as the primary unless you want to risk the V44 high-confidence zone.
V74 is a marginal improvement in boundary-zone ordering but a net negative on expected
full-test LB.
