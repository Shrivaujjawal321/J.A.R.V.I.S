# V22 — V4 structure + AutoGluon's CatBoost_r167

Single surgical change: CatBoost hyperparams swapped to AG-discovered config (depth=6, lr=0.069, l2=2.15, max_ctr_complexity=4).
LGB + XGB unchanged.
LR meta + Platt + gate + score-aware T (V4 baseline preserved).

Meta OOF AUC: 0.8829 (V5: 0.8886, delta -0.0057)
OOF (R+P)/2: 53.55
Calibrated LB est: 56.22
