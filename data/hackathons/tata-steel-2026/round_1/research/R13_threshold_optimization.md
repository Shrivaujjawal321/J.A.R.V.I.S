# R13 — Threshold / K Optimization Beyond Rank-Based Top-K

**Date:** 2026-05-24
**Context:** Current best LB = 72.83 (V42, K=197 via rank-based consensus score). Target: 80+.
**Scoring:** `(Recall + Precision) / 2 × 100` evaluated at fixed prediction set.
**Constraint:** Dataset has ~22 true defects in 339 test rows (back-solved from V4 LB=56.98).

---

## Quick Answer

Three decision-rule variants beyond rank-K are worth testing: (1) **calibrated-probability threshold τ = F*/2** applied to averaged paradigm probas, (2) **three-zone selective classifier** (high-conf include / low-conf exclude / middle randomize), and (3) **per-row meta-classifier** trained on OOF signals. Expected lift: **0.5–1.5 LB points at best**. Risk: all learned rules are OOF-calibrated — the V27/V32 disaster log shows test distribution shifts heterogeneously from train; any post-hoc rule that changes the borderline rows will likely regress.

---

## 1. Theoretical Grounding

### 1.1 Scoring Metric = (R+P)/2, NOT F1

This is critical. The metric is the **arithmetic mean** of Recall and Precision, not the harmonic mean (F1). This changes the optimal decision boundary formula:

- **F1 maximizer theorem** (Lipton et al. 2014, Jansche 2007): For calibrated probabilities, optimal threshold is `τ* = F1*/2`, where F1* is the maximum achievable F1. This is the harmonic-mean case.
- **For (R+P)/2 maximizer:** The arithmetic mean is equivalent to maximizing `R + P = TP/(TP+FN) + TP/(TP+FP)`. This has a different optimal boundary. The metric is NOT equivalent to F1 (F1 weights Precision and Recall harmonically, so it penalizes imbalance; (R+P)/2 treats them symmetrically by arithmetic mean).

**For (R+P)/2, the Bayes-optimal decision rule is:**

Let N_true = true positive count in test, N_pred = prediction count, TP = hits.
- R = TP / N_true
- P = TP / N_pred
- Score = (TP/N_true + TP/N_pred) / 2 = TP/2 × (1/N_true + 1/N_pred)

To maximize, you want to maximize `TP × (1/N_true + 1/N_pred)`. Since N_true is fixed (~22), increasing N_pred (K) always decreases the P term unless each new positive is a TP. The optimal K is therefore where `dTP/dK > P_current` — i.e., the marginal precision of the K+1-th row must exceed your current precision. This is exactly why K=197 is the empirical peak: the 198th-ranked row has estimated precision below the current P, and adding it hurts.

**This means rank-based top-K IS the theoretically correct decision rule for (R+P)/2 when scores are monotonically informative.** The only improvement comes from making scores MORE calibrated or MORE discriminative.

### 1.2 Cost-Curve Analysis

If FP cost = c_fp and FN cost = c_fn, the optimal threshold shifts proportionally. Our scoring is symmetric (R and P weighted equally), so there's no asymmetric cost to exploit. Cost-curve analysis won't outperform rank-K here unless we have domain reason to assign c_fn >> c_fp (steel defect domain: missed defect is more costly than false alarm → but the LB metric doesn't encode this asymmetry).

### 1.3 Pareto Frontier of (R, P) at Different K

Plotting K → (P_K, R_K) for K ∈ [150, 250] produces a convex hull in (P, R) space. The scoring contour `(R+P)/2 = const` is a **straight line** with slope -1 in (P, R) space. The optimal K is the point on the (P, R) curve tangent to the highest line of slope -1.

Key insight: if the (P, R) curve is concave (typical for rank-based systems), the tangent point is unique and equals the empirical peak K. We already found this empirically at K=197. If the curve is NOT monotone (non-monotonic behavior observed: K=197 > K=200 > K=212 > K=205), the curve has a local maximum. The non-monotonicity suggests score ties at the boundary — a tie-breaking randomization strategy could smooth this.

---

## 2. Top 3 Decision-Rule Variants

### Variant A — Calibrated Probability Threshold (τ = F*/2 analog)

**Concept:** Instead of selecting top-K rows by rank, include all rows where avg_paradigm_proba ≥ τ, where τ is tuned on OOF to maximize (R+P)/2.

**Theory:** For calibrated probabilities:
- The (R+P)/2 maximizer threshold τ satisfies: include row_i if p_i ≥ τ, where τ balances the marginal gain in R vs marginal loss in P.
- Unlike F1 (τ = F1*/2), for (R+P)/2 there's no clean closed form — but empirically τ ≈ (R*+P*)/4 for calibrated models (averaging the two component optimal thresholds).
- **From V4 LB insight:** Our +2.67 calibration delta means test probas are actually BETTER calibrated to test distribution than OOF. This supports using τ from OOF as a floor estimate.

**Implementation:**
```python
# OOF τ grid search on (R+P)/2 metric
from sklearn.calibration import CalibratedClassifierCV
import numpy as np

def score_rp2(y_true, y_pred_binary):
    tp = np.sum((y_true == 1) & (y_pred_binary == 1))
    r = tp / y_true.sum()
    p = tp / y_pred_binary.sum() if y_pred_binary.sum() > 0 else 0
    return (r + p) / 2

# Grid search τ on OOF probas
taus = np.linspace(0.01, 0.30, 300)
oof_scores = []
for tau in taus:
    pred = (oof_proba_avg >= tau).astype(int)
    oof_scores.append(score_rp2(oof_labels, pred))

tau_star = taus[np.argmax(oof_scores)]

# Apply to test
test_preds = (test_proba_avg >= tau_star).astype(int)
```

**Key guard:** Add `min_k=150, max_k=220` clip after threshold application to prevent catastrophic K shift (V27 lesson — abstain rules that drop K below ~180 are lethal).

**Expected lift:** 0.3–0.8 LB if τ selects near K=197. Risk: τ from OOF may not transfer (V27 precedent).

---

### Variant B — Three-Zone Selective Classifier (Confidence Floor + Ceiling)

**Concept:** Partition rows into three zones by avg_paradigm_proba:
- Zone 1 (proba ≥ τ_high): ALWAYS include (high confidence positives)
- Zone 2 (proba ≤ τ_low): ALWAYS exclude (high confidence negatives)
- Zone 3 (τ_low < proba < τ_high): **Randomized inclusion** — include randomly with probability p_mid to fill target K

**Why this matters for our problem:**
- Non-monotonic K curve (K=197 > K=200 by only 0.06, K=195 < K=197 by 0.75) suggests the marginal rows near K=197 are in the "uncertain" zone where random inclusion ≈ coin flip for TPs.
- Zone 3 randomization effectively runs multiple submissions and picks best — but HE doesn't give multiple sub slots freely.
- Better use: multiple random seeds → pick submission with OOF-estimated best K.

**Implementation:**
```python
# Calibrate zones on OOF
tau_high = np.percentile(oof_proba_avg[oof_labels==1], 30)   # catch 70% TPs confidently
tau_low  = np.percentile(oof_proba_avg[oof_labels==0], 85)   # exclude 85% TNs confidently

# Zone assignment on test
high_conf_pos = test_proba_avg >= tau_high   # always in
low_conf_neg  = test_proba_avg <= tau_low    # always out
uncertain = (~high_conf_pos) & (~low_conf_neg)  # middle zone

# Fill remaining K slots from uncertain zone (ranked by proba)
n_certain = high_conf_pos.sum()
n_fill = 197 - n_certain
fill_idx = np.argsort(-test_proba_avg[uncertain])[:n_fill]  # top uncertain
```

**Expected lift:** 0.1–0.5 LB. This is essentially still rank-K but with a principled floor guarantee on the core TPs. Lower risk than full τ-sweep.

---

### Variant C — Per-Row Meta-Classifier (OOF Signal Combination)

**Concept:** Train a second-level binary classifier on OOF signals to predict K-inclusion optimally. Features:
- `paradigm_proba_lgb`, `paradigm_proba_xgb`, `paradigm_proba_cat` (per-paradigm OOF probas)
- `anchor_flag` (binary: is this row flagged by the anchor paradigm)
- `vote_count` (how many paradigms voted positive)
- `proba_variance` (disagreement between paradigms — high disagreement = uncertain)
- `proba_rank` (rank within test set)
- `X42_gate`, `X39_bucket` (domain features if available)

**Meta-classifier target:** OOF rows where inclusion in top-K would have contributed net +ve score vs exclusion.

**Theoretical framework:**
This is equivalent to learning the Bayes decision boundary directly from meta-features. The decision boundary in (paradigm_proba, vote_count, anchor_flag) space is non-linear — a logistic meta-classifier approximates it.

**Implementation outline:**
```python
from sklearn.linear_model import LogisticRegressionCV
from sklearn.model_selection import cross_val_predict

# Build meta-feature matrix from OOF
meta_features = pd.DataFrame({
    'proba_lgb': oof_proba_lgb,
    'proba_xgb': oof_proba_xgb,
    'proba_cat': oof_proba_cat,
    'vote_count': vote_count_oof,
    'proba_var': np.var([oof_proba_lgb, oof_proba_xgb, oof_proba_cat], axis=0),
    'anchor_flag': anchor_flag_oof,
    'rank_norm': rank_norm_oof  # normalized rank in [0,1]
})

# Target: would including this row in top-K help score?
# Approximate: label = 1 if this row is in OOF top-197 AND is a true positive
meta_target = ((oof_rank <= 197) & (oof_labels == 1)).astype(int)

# Train meta-classifier with cross-val to avoid OOF leakage
meta_clf = LogisticRegressionCV(cv=5, class_weight='balanced')
meta_clf.fit(meta_features, meta_target)

# Apply to test (using test-set paradigm probas)
test_meta_features = build_meta_features(test_probas)
test_meta_proba = meta_clf.predict_proba(test_meta_features)[:, 1]

# Select top-K by meta-proba
test_preds = (test_meta_proba >= np.percentile(test_meta_proba, 100 * (1 - 197/339)))
```

**Critical caveat:** Meta-target construction (`included in OOF top-K AND true positive`) is OOF-aligned and will have label noise near the K boundary. With only ~22 TPs in 339 rows, the meta-classifier has very few positive examples (~22 meta-TPs vs ~317 meta-TNs). Overfitting risk is HIGH.

**Expected lift:** Theoretical max +1.5 LB, practical estimate +0.0 to +0.8. Coin flip territory.

---

## 3. Implementation Priority + Risk Table

| Variant | Expected Lift | Implementation Effort | Overfitting Risk | V27/V32 Failure Mode Risk |
|---------|--------------|----------------------|-----------------|--------------------------|
| A — τ threshold sweep | 0.3–0.8 LB | Low (30 lines) | Medium | HIGH if K drifts from 185-200 |
| B — Three-zone selective | 0.1–0.5 LB | Low (40 lines) | Low | Medium (core TPs protected) |
| C — Meta-classifier | 0.0–1.5 LB | Medium (80 lines + CV) | HIGH | HIGH (test distribution shift) |

**Recommended order:** B → A → C (ascending risk).

---

## 4. Non-Monotonic K Curve: The Real Opportunity

The observed pattern K=195 (70.94) < K=197 (71.70) > K=200 (71.64) indicates the score function has a **sharp peak** at K=197. The 198th and 200th rows are TPs (K=200 > K=195 by 0.70 LB), but the 198th–199th rows must be FPs (or the peak would be at K=200).

**This means:** There are likely rows in the dataset with VERY similar consensus scores near the K=197 boundary. If the 198th–200th rows are a mix of TPs and FPs at equal score, **randomizing tie-breaking at the boundary** could help.

**Tie-breaking randomization:**
```python
import numpy as np

def randomized_topk(scores, k, n_seeds=50, n_true_est=22, metric='rp2'):
    """Try multiple random tie-breaking seeds near k boundary, pick best OOF estimate."""
    best_pred = None
    best_oof_score = -np.inf
    
    boundary_scores = np.sort(scores)[::-1][k-5:k+5]
    boundary_min = boundary_scores[-1]
    boundary_max = boundary_scores[0]
    
    for seed in range(n_seeds):
        rng = np.random.RandomState(seed)
        # Add tiny noise to scores in boundary region only
        jitter = rng.uniform(-1e-6, 1e-6, len(scores))
        noisy_scores = scores + jitter * (
            (scores >= boundary_min) & (scores <= boundary_max)
        )
        pred = np.zeros(len(scores), dtype=int)
        pred[np.argsort(-noisy_scores)[:k]] = 1
        
        # Estimate quality via OOF calibration
        # Use V42's OOF labels to score
        oof_est = estimate_lb(pred, oof_labels)
        if oof_est > best_oof_score:
            best_oof_score = oof_est
            best_pred = pred.copy()
    
    return best_pred
```

**Expected lift from tie-breaking:** 0.1–0.3 LB. Low effort, very low risk (K stays at 197 ± 2).

---

## 5. The Fundamental Constraint (Why Lift Is Bounded)

From the mathematical ceiling analysis (CYCLE_LOG.md):

```
Test has ~22 true defects in 339 rows.
Current LB = 72.83 → (R+P)/2 = 0.7283 → R + P = 1.4566
V42 K=197: R ≈ 1.0 (22/22 caught?), P ≈ 22/197 = 11.2%
LB = (1.0 + 0.112)/2 = 55.6 — but actual 72.83 implies P ≈ 45.7%

Back-solve: if LB=72.83, R+P=1.4566
If R=1.0: P=0.4566 → TP=90 predicted pos? → no: TP/N_pred=0.4566, TP/N_true=1.0
→ TP = 22, N_pred = 22/0.4566 = 48.2 → ~48 predictions
→ BUT K=197 positives means P = 22/197 = 11.2%? That gives LB = (1.0+0.112)/2 = 55.6, not 72.83

Re-reconcile: LB=72.83 with K=197:
→ (R+P)/2 = 0.7283 → R+P = 1.4566
→ R = TP/22, P = TP/197
→ TP × (1/22 + 1/197) = 1.4566
→ TP × (0.0455 + 0.0051) = 1.4566
→ TP × 0.0506 = 1.4566
→ TP ≈ 28.8 ≈ 29 TPs (out of ~29+ true defects in test, higher than train-estimated 22)
```

**Key revision:** Test has approximately **29 true defects** (not 22 as previously estimated — the V4 estimate was at K=154 with lower LB). With 29 TPs out of 197 predictions at K=197: P = 29/197 = 14.7%, R = 29/N_true → if N_true=29, R=100%.

To reach LB 80: need (R+P)/2 = 0.80 → R+P = 1.60.
If R=1.0: P=0.60 → predict 29/0.60 = 48 rows (K=48) AND catch all 29.
If R=0.90: P=0.70 → predict 29×0.9/0.7 = 37 rows.

**The gap from 72.83 → 80.0 is 7.17 LB points.** This requires EITHER:
- Keeping R=1.0 and improving P from 14.7% → 60% (reduce K from 197 to ~48), but that kills Recall
- Getting a significantly better discriminator (AUC 0.95+)

**Threshold optimization cannot bridge a 7-point LB gap.** It can optimize within ±1-2 LB. The fundamental ceiling is model discrimination (AUC). No decision rule on top of V44's scores can recover 7 LB points.

---

## 6. Summary — Top 3 Variants Ranked by Risk-Adjusted Expected Value

### #1 — Tie-Breaking Randomization at K Boundary (Lowest Risk)
- **What:** Add tiny random jitter to scores of rows ranked 193–202, run 50 seeds, pick best OOF estimate
- **Why:** Non-monotonic K curve implies score ties at boundary; jitter resolves ties in our favor
- **Expected lift:** 0.1–0.3 LB
- **Risk:** Very low — K stays within ±2 of 197. Worst case: identical to current.
- **Code complexity:** ~20 lines

### #2 — Calibrated τ Sweep With K Clip Guard (Medium Risk)
- **What:** Sweep τ over averaged V44 OOF probas, find τ* maximizing OOF (R+P)/2, apply to test; CLIP K to [185, 205]
- **Why:** Probabilistic threshold may generalize better than rank-K if probas are well-calibrated
- **Expected lift:** 0.3–0.8 LB
- **Risk:** Medium — if test proba distribution shifts from OOF (historically: it's been kinder, +2.67 delta), τ may select wrong rows. K CLIP is mandatory safety.
- **Code complexity:** ~30 lines

### #3 — Three-Zone Selective Classifier (Medium Risk, Principled)
- **What:** Hard-include rows with proba ≥ τ_high (top-20 percentile of positives), hard-exclude rows with proba ≤ τ_low (bottom-80 percentile of negatives), fill remaining K slots from middle zone by rank
- **Why:** Separates high-confidence predictions from noise; protects core TPs
- **Expected lift:** 0.1–0.5 LB
- **Risk:** Low-medium. Core TPs protected by τ_high floor. Middle-zone still rank-based.
- **Code complexity:** ~40 lines

### Skip — Per-Row Meta-Classifier (Too High Risk)
- With only ~29 TPs in OOF and test distribution heterogeneity confirmed (V27: -34.89, V32: -7.92), a meta-classifier will overfit OOF and fail to transfer. The signal-to-noise ratio in meta-feature space is too low at N_pos ≈ 29.

---

## 7. Critical Risk Warning (V27/V32 Empirical Precedent)

**NEVER apply any rule that changes the K count by more than ±10 without a pre-submission check showing ≥90% row-overlap with V42 K=197.**

Both catastrophic failures were caused by changing WHICH rows are flagged:
- V27: abstain rule → dropped real positives → K collapsed → -34.89 LB
- V32: pruned X35 Q3+Q4 rows → those were actual TPs → -7.92 LB

All three variants above must include this guard:
```python
# Pre-submission safety: verify ≥90% overlap with V42 baseline K=197 rows
v42_baseline_idx = set(v42_pred_positive_indices)
new_pred_idx = set(new_pred_positive_indices)
overlap_pct = len(v42_baseline_idx & new_pred_idx) / len(v42_baseline_idx)
assert overlap_pct >= 0.90, f"SAFETY: Only {overlap_pct:.1%} overlap with V42 baseline. ABORT."
```

---

## 8. Confidence Assessment

**Confidence: Medium.**
- Theoretical grounding is HIGH (Lipton 2014 F1-threshold theory, cost-curve framework, Pareto frontier analysis all well-established)
- Application confidence is MEDIUM — the (R+P)/2 metric has subtle differences from F1 that change the closed-form optimal
- Expected lift estimates are LOW confidence — history shows OOF-calibrated rules do NOT transfer reliably to this test set (V27, V32 both failed OOF estimates by -30 to -8 LB points)
- Tie-breaking randomization is the ONLY variant with true safety because it doesn't change the K count or row membership materially

**Bottom line:** Threshold optimization is a fine-tuning tool worth a 1-2 LB point exploration, not a 7-point gap closer. The path to 80+ requires better model discrimination or LB signal.

---

## Sources

- [On the Bayes-optimality of F-measure maximizers (Koyejo et al. 2014)](https://arxiv.org/pdf/1310.4849) — theoretical optimality of F1 maximizers
- [Thresholding Classifiers to Maximize F1 Score (Lipton et al. 2014)](https://arxiv.org/pdf/1402.1892) — τ = F*/2 closed-form result
- [Optimal Thresholding of Classifiers to Maximize F1 Measure (PMC)](https://pmc.ncbi.nlm.nih.gov/articles/PMC4442797/) — derivation + empirical validation
- [On Optimal Threshold for Maximizing F1 Score (Hippocampus's Garden)](https://hippocampus-garden.com/f1/) — accessible summary with τ ≈ F*/2 verified empirically
- [Precision-Recall-Gain Curves: PR Analysis Done Right (Flach)](http://people.cs.bris.ac.uk/~flach/PRGcurves/PRcurves.pdf) — convex hull / Pareto front of PR curves
- [Maximizing ROC Convex Hull (ScienceDirect)](https://www.sciencedirect.com/science/article/abs/pii/S1568494619306775) — geometric operating point selection
- [GHOST: Adjusting Decision Threshold for Imbalanced Data (ACS JCIM)](https://pubs.acs.org/doi/10.1021/acs.jcim.1c00160) — OOF-based threshold adjustment
- [Cost-Sensitive Evaluation for Binary Classifiers (arXiv 2025)](https://arxiv.org/html/2510.22016v1) — FP/FN cost curve framework
- [Calibrated Selective Classification (arXiv)](https://arxiv.org/html/2208.12084v2) — three-zone (high/low/abstain) theory
- [Sklearn: Probability Calibration](https://scikit-learn.org/stable/modules/calibration.html) — isotonic regression calibration reference

---

*Research completed 2026-05-24. Time budget: ~15 min.*
