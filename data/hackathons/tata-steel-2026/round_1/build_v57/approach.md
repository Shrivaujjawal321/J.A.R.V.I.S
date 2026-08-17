# V57 Approach — Adversarial Validation + Density-Ratio Reweighting

## Motivation

V4 baseline assumes i.i.d. train-test, but:
- Train prevalence = 4.9%, test prevalence ≈ 45% (label shift)
- Adversarial AUC = 0.5509 (covariate shift confirmed)

Sugiyama et al. 2007 (IWCV) proves: if you weight train samples by p(test|x)/p(train|x),
importance-weighted empirical risk converges to the test risk. This is the theoretically
correct correction for covariate shift.

## Implementation

1. Adversarial classifier: concat train+test → 5-fold LGB → OOF P(sample=test|x)
2. Density-ratio: w = p̂/(1-p̂), clip [0.1, 10], normalize mean=1.0
3. V4 exact base (LGB+XGB+CAT, 5-fold, 51 features) with sample_weight=DR_weights
4. LR meta on [lgb_oof, xgb_oof, cat_oof]
5. BBSE Bayes posterior adjustment for estimated test prevalence q_test=0.0156

## Key Results

- Adversarial AUC: 0.5509
- OOF F1@K=200: 0.345865 (FAIL vs 0.391 benchmark)
- Spearman vs V44: 0.9053 (orthogonality check)
- BBSE in use: False

## Risks

1. DR weights amplify a handful of high-p̂ train rows → potential instability
2. BBSE prevalence estimate depends on model calibration; if wrong, corrects in wrong direction
3. With only 66 positives, DR-upweighted positives dominate gradient — monitor OOF AUC vs V4 baseline

## Submission

- K=154 (ICR recipe) and K=200 (V44 banked protection)
- Fire K=200 to protect banked 72.83 LB
