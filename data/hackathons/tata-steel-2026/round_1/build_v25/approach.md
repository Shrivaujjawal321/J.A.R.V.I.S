# V25 — Roll-Campaign Ordinals + Force-Block Grade Z-Scores

## Architecture
Base: V4-faithful hyperparams (from build_v26 reference):
- LGB: lr=0.05, num_leaves=31, subsample=0.8, colsample=0.8, scale_pos_weight=19.5, early_stop=50
- XGB: lr=0.05, max_depth=4, subsample=0.8, colsample=0.8, min_child_weight=5, spw=19.5, early_stop=50
- CAT: lr=0.05, depth=5, l2=3, scale_pos_weight=19.5
- Meta: LR + Platt (CalibratedClassifierCV cv=5)
- SMOTE: strategy=0.3, k_neighbors=3 inside each fold

## New Features
### R12_rec_1: Roll-Campaign Ordinal (4 features, no Y — CV-safe)
campaign_id, coils_since_last_zero, coils_to_next_zero, norm_campaign_pos

### R01_rec_1: Force-Block Grade Z-Scores (5 features — gate PASS)
adj_corr(X29-X33)=0.9526 > far_corr=0.7991: block CONFIRMED
z=(x-mu_grade)/(sigma_grade+1e-6), mu/sigma from training fold only. Global fallback n<8.

Total: 60 features

## Results
| Model | Mean OOF AUC |
|-------|-------------|
| LGB | 0.8583 |
| XGB | 0.8569 |
| CAT | 0.8869 |
| Meta | 0.8870 |

| Metric | V4 | V25 | Delta |
|--------|----|-----|-------|
| Meta OOF AUC | 0.8837 | 0.8870 | +0.0033 |
| OOF (R+P)/2 | 54.31 | 53.88 | -0.43 |
| Bootstrap CI lower | 53.36 | 53.04 | - |
| Calibrated LB est | 56.98 | 56.55 | -0.43 |

Threshold: 0.00989843 | R=1.0000 | P=0.0776 | Test n_pos: 202/339

## Verdict
NO IMPROVEMENT over V4 (delta -0.43 OOF points)
