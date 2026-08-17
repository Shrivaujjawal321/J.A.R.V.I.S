# V55 Approach — Stealth-Defect Focal-Loss Specialist

## Problem Statement

V44 K=200 consensus (72.83 LB) catches ~129 of the ~154 test true positives (based on F1 back-calculation). A peer at 77.67 catches ~144. The gap = ~15 TPs we consistently miss. These are the "stealth defects" — coils that look normal to our ensemble's ranking.

## R22 Hypothesis

The missed positives share a characteristic: they score in the middle of V44's ranking distribution (not at the bottom — those are random noise, not defects). Their physical signature is detectable but weak relative to the majority of clear defects. A specialist model trained to focus specifically on these borderline rows, with extreme positive weighting, can find feature interactions the full-dataset model ignores.

## Architecture Decisions

### 1. Training Cluster Construction

- **V44 OOF borderline:** Rows where V44 consensus rank falls between 100 and 400 (out of 1352). This is the "uncertain zone" — rows V44 is least confident about.
- **All Y=1 included:** Never filter out positives, even the ones V44 already catches confidently. The specialist needs to see the full positive distribution to understand what "defect" means.
- **Result:** ~340-row training cluster with 66 positives — imbalance ~4.2:1 (vs 19:1 in full dataset)

### 2. Focal Loss (γ=2.0, α=0.85)

Standard cross-entropy with `scale_pos_weight` still treats negatives equally — in our ~274-row negative cluster, many negatives are "hard negatives" that naturally live near the decision boundary. Focal loss with γ=2.0 down-weights easy negatives (ones the model already assigns low probability), forcing gradient updates to concentrate on the genuinely ambiguous rows.

α=0.85 provides additional positive class weighting on top of γ (asymmetric focal loss).

**CRITICAL implementation detail:** `init_score` must be set to the log-odds of the cluster's positive prior (not 0 or the full-dataset prior). Without this, the initial model predictions are wildly wrong and early boosting rounds waste capacity correcting the initialization error.

### 3. scale_pos_weight = cluster_imbalance × 3

For the borderline cluster (~4.2:1 imbalance), `scale_pos_weight = 4.2 × 3 ≈ 12.6`. This is the "triple weight" per R22 spec. Note: the spec said "19 × 3 = 57" but 19 was the FULL DATASET imbalance. In the borderline cluster, negatives are pre-filtered to the hard ones, so 4.2:1 is the actual imbalance — using 57 would massively over-correct.

### 4. Same 105-Feature Set as V35

No feature engineering changes. The specialist's value comes from WHERE it trains (cluster) and HOW it trains (focal loss), not from new features. Adding new features at this stage risks introducing confounds.

### 5. Fold Structure Matches V44

StratifiedKFold(5, shuffle=True, seed=42) — identical to all V44 paradigms. This ensures OOF probabilities are directly comparable for consensus blending.

## Validation Gates

Three gates guard against noise:

1. **OOF AUC >= 0.80:** Lower bar than V44 (which is ~0.93 OOF rank_pct correlation) because this is a specialist on 340 rows. Gate confirms V55 has positive predictive power at all.

2. **Hard-positive mean OOF proba >= 0.45:** The critical gate. Hard positives = the 18 Y=1 rows V44 ranks below position 200. V44 assigns them mean raw proba ~0.047 (via V35). V55 must lift them above 0.45 to justify blend credit. If V55 can't lift these rows, it found nothing new.

3. **Spearman vs V44 in [0.40, 0.70]:** V55 must be genuinely different from V44 (not just a noisy echo). Too high (>0.70) = echoing. Too low (<0.40) = predicting something orthogonal to true positives (likely cluster noise).

## Blend Strategy

If all gates pass:

```python
v44_pct = v44_score.rank(pct=True)
v55_pct = oof_v55_proba.rank(pct=True)
blend = 0.70 * v44_pct + 0.30 * v55_pct
```

70/30 preserves V44's core ranking (the 72.83 LB signal) while injecting V55's specialist lift. The 0.30 weight is conservative — if V55 gates pass strongly (hard-pos delta > +0.30), consider 60/40.

## What This Does NOT Fix

- Bayes irreducible error: some of the 15 missed TPs may be genuinely undetectable in X1-X49
- Test distribution shift: V55 trains on OOF positives that happen to be hard — test hard positives may have different characteristics
- Calibration: focal loss outputs are uncalibrated — rank_pct transformation is mandatory before blending

## Anti-patterns Explicitly Avoided

- NO SMOTE on cluster (distribution mismatch between synthetic + real negatives in a 340-row cluster)
- NO post-hoc abstain rules (V27 lesson: threshold manipulation collapses LB)
- NO blend without Spearman sanity check (V31 lesson: orthogonal signals × blend = collapse)
- NO direct submission of V55 alone (it's a specialist, not a full-coverage model)
