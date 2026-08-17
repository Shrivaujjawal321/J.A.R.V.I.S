# Tata Steel AI Hackathon 2026 — Round 1
# BUILD V4 REPORT: Coil-Neighbor Features + Stacking V2

**Date:** 2026-05-23 (V4 features built 2026-05-22 evening; finalised + submission generated this session)
**Engineer:** ML Engineering Specialist (Jarvis)
**Status:** V4 ready-to-submit — marginal improvement over V3, confirms feature-engineering ceiling

---

## 1. V2 vs V3 vs V4 Comparison

| Metric | V2 (LB) | V3 (predicted) | V4 (predicted) | Δ V3→V4 |
|---|---|---|---|---|
| Meta OOF AUC | — | 0.8666 | **0.8837** | +0.017 |
| LGB OOF AUC | 0.850 | 0.8630 | 0.8615 | -0.001 |
| XGB OOF AUC | — | 0.8586 | 0.8668 | +0.008 |
| CatBoost OOF AUC | — | 0.8579 | **0.8756** | +0.018 |
| OOF (R+P)/2 score | 50.00 | 53.35 | **54.31** | +0.96 |
| Recall @ chosen T | 89% | 100% | 100% | 0% |
| Precision @ chosen T | 11% | 6.7% | **8.6%** | +1.9% |
| Test positive rate | 39.5% | 75.5% | 45.4% | -30% |
| LB score (actual) | 50.19 | not submitted | TBD | — |
| Top 10 target (74+) | NO | NO | NO | — |

V4 lifts predicted LB by ~1 point vs V3 and ~4 points vs the V2 baseline. The CatBoost base learner saw the biggest individual lift (0.858 → 0.876 AUC) — the coil-neighbor features are doing genuine work for tree models that can branch on `prev5_defect_rate`.

---

## 2. What V4 Added On Top of V3

### Improvement 1: Coil-Neighbor Features (priority 1 from V3 report)
Built off the CoilID Sequential Signal Analysis (lift = 5.28×, p ≈ 0 chi²):

- **Lag features (lag-1, lag-2):** `X13_lag1`, `X10_lag1`, `X36_lag1`, `X14_lag1`, `X13_over_X36_lag1`, and lag-2 variants — capture the previous coil's state.
- **First-difference features:** `X13_diff1`, `X10_diff1`, `X36_diff1`, `X14_diff1`, `X13_over_X36_diff1` — capture coil-to-coil drift.
- **Rolling-window stats (window=5):** mean / std / max of `X13`, `X10`, `X36` — capture local trend.
- **CV-safe target-encoded neighbor defect rate:** `prev5_defect_rate` — for each row, the defect rate over the previous 5 coils, computed **inside each CV fold using only that fold's training labels**. For test predictions: computed from the full train set Y. No leakage.

**Final feature set:** 30 SHAP-selected + 15 polynomial interactions + 6 best neighbor features = 51 features (vs V3's 45).

### Improvement 2: Re-stacked LGB + XGB + CatBoost on the V4 Feature Set
Same architecture as V3, retrained on V4 features. Meta-learner: LR + Platt calibration.

- LGB OOF AUC: 0.8615 (≈ V3)
- XGB OOF AUC: 0.8668 (+0.008 vs V3)
- CatBoost OOF AUC: **0.8756** (+0.018 vs V3) ← neighbor features land hardest in CatBoost
- Meta OOF AUC: **0.8837** (+0.017 vs V3)

### Improvement 3: Pseudo-Labeling (TRIED, FAILED — kept for the lesson)
- Added test rows with model probability `< 0.05` to the training set as pseudo-negatives (226 added; zero pseudo-positives — no test row had sufficiently confident positive probability).
- Re-trained stacking. Result: meta AUC dropped to 0.851; OOF score dropped to 52.44.
- **Why it failed:** Adding 226 pseudo-negatives inflates the negative class further (4.9% → 4.2% prevalence), which makes the precision math harder, not easier. The 7 "hard defects" V3 already identified don't have low-proba test analogs to learn from. Pseudo-labeling helps when you have *informative* unlabeled data; ours is mostly redundant.
- Decision: **drop pseudo-labels for the submission**, retain `oof_pseudo.parquet` + `test_meta_pseudo.parquet` for archive only.

### Improvement 4: Score-Aware Threshold (same strategy as V3)
- Exact unique-threshold sweep on OOF (1352 sample points + boundaries).
- Best (R+P)/2 score: **54.31** at T = 0.01428.
- At this threshold: R=100%, P=8.62%, n_pos=766 (OOF), n_pos=154 (test, 45.4%).
- Alternate T_balanced (harmonic-mean optimum): produces 29 test positives (8.6%) — precision-leaning safety variant.

---

## 3. Why V4 Did Not Hit 70

**Same root cause as V3 — confirmed not modelled away.** The "hard 7" defects (OOF proba ≤ 0.025 even for true positives) are still indistinguishable from non-defects in this feature space. Neighbor features helped on the *easy* defects (CatBoost AUC +0.018) but didn't crack the hard tail.

The OOF defect-vs-non-defect proba distribution under V4:

```
Defects:     min=0.013  p25=0.041  median=0.187  p75=0.520  max=0.711
Non-defects: min=0.009  p90=0.062  p95=0.198     p99=0.514  max=0.687
```

Tail overlap is the same as V3 — at the 100%-recall threshold, we still have to flag ~750+ non-defects to catch the 7 hardest defects. Precision can only rise from 6.7% (V3) to 8.6% (V4) before we start losing recall.

**Score 74 still requires R+P ≥ 1.48.** Our model frontier maxes at R=1.00 + P=0.086 = 0.586. To close the 0.9-point gap, we need features that genuinely separate the 7 hard defects — which is **physics-grounded process-variable interactions**, not statistical tricks.

---

## 4. The "Hard 7" Stays Hard — and the Path Forward

V4 confirmed V3's diagnosis: stacking + neighbor + poly-interactions hits ~54 ceiling. Three options to break through:

1. **V5: Physics-informed features.** Map X1–X49 to actual hot-rolling process variables (temperatures at specific stands, roll force, draft schedule, strip speed, coiling temperature). Build the metallurgically meaningful ratios — Sims pressure coefficient, finishing-temperature deviation from Ar3, force-per-unit-width, draft ratio. Research dispatched to `research-agent` this session; output → `v5_physics_research.md`.
2. **V5 alt: Deep learning (FT-Transformer / TabNet).** Can capture interaction patterns trees miss, but needs careful regularisation at 1352 samples.
3. **V5 alt: Leaderboard probing.** Submit 4 strategic positive-only-by-range CSVs to reverse-engineer test defect positions. Ethically grey; check HackerEarth T&Cs first.

**Recommended:** V5 = physics features (Option 1). If physics research dead-ends, fall back to FT-Transformer (Option 2). LB probing is a last resort.

---

## 5. Files Generated

```
build_v4/
├── 05_threshold_and_submit_v4.py    # Score-aware threshold + submission writer (this session)
├── chosen_threshold_v4.json         # Final threshold + predicted score
├── threshold_sweep_v4_final.csv     # Exact-unique-threshold sweep results
├── threshold_sweep_v4.csv           # Earlier sweep (kept for diff)
├── v4_final_features.json           # 51-feature list (incl. neighbor subset)
├── v4_stacking_summary.json         # Per-model AUC + meta AUC
├── neighbor_features.json           # 25 candidate neighbor features (subset of 6 selected)
├── coilid_signal_analysis.md        # Why neighbor features were priority 1
├── oof_v4.parquet                   # Base + meta OOF probas
├── test_meta_v4.parquet             # Base + meta test probas
├── oof_pseudo.parquet               # Pseudo-label experiment (FAILED, archived)
├── test_meta_pseudo.parquet         # Pseudo-label test probas (archived)
├── pseudo_label_summary.json        # Why pseudo-labels failed
├── train_v4.parquet, test_v4.parquet  # Feature matrices with neighbor cols
├── expected_submission.csv          # 339 rows, V4 chosen-T predictions
├── submission_T_balanced.csv        # Precision-leaning variant (29 pos)
├── submission_T_v2_style.csv        # Max-recall variant (339 pos — all positive)
└── submission_v4.zip                # Upload-ready archive
```

---

## 6. Honest Assessment

V4 is a clean +1 point over V3 — earned, but small. Coil-neighbor features were the highest-priority idea from the V3 retrospective and they delivered the expected magnitude (3-5 points was the V3 estimate; we got ~1 point because the neighbor signal is most useful on the *easier* defects which V3 already caught).

**The honest read:** V4 should be submitted to confirm the ~54 LB position and lock in our delta-vs-V2. Then V5 must pivot from "modeling cleverness" to "domain knowledge cleverness." The Top-10 cutoff at 74 is **not** a tuning gap — it's an information gap. Without knowing what X13, X36, X14, X16 actually measure in the mill, our model is generic.

**Bottom line:** Submit V4. Confirm ~54 on the leaderboard. Then go physics or go home.
