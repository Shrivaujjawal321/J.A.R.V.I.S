# V24 Approach — Robust Focal Loss on LGB + V4 Base Models

## Technique: Robust Focal Loss (RFL)

**Paper:** Yao et al. 2023, "Robust-GBDT: GBDT with Nonconvex Loss for Tabular Classification
in the Presence of Label Noise and Class Imbalance." arXiv:2310.05067 / Knowledge and Information Systems 2025.

**Motivation:** This dataset has confirmed label noise (Elkan-Noto PU estimate c=0.154, ~361 hidden
positives among Y=0 rows) AND 20:1 class imbalance. RFL is specifically designed for this joint scenario.

**RFL Formula (Yao et al. Section 3):**
- For y=1: L = (1-p)^r * (1 - p^q) / q
- For y=0: L = p^r * (1 - (1-p)^q) / q

r controls imbalance focusing (like focal gamma). q controls noise robustness. q=0 reduces to focal loss.

## Architecture

- **Features:** Same 51 features as V4 (30 SHAP-selected + 15 polynomial + 6 coil-neighbor)
- **CV:** 5-fold StratifiedKFold(seed=42), SMOTE(0.3, k=3) inside folds
- **LGB:** Custom RFL objective via LGB 4.x params["objective"] API
- **XGB:** V4-exact params (scale_pos_weight=19.5, standard logloss)
- **CatBoost:** V4-exact params (auto_class_weights="Balanced", standard logloss)
- **Meta:** LR + Platt calibration (CalibratedClassifierCV)
- **Threshold:** Exact unique-threshold sweep maximizing (R+P)/2

## Grid Search Results

Best config: LGB r=0.5, q=0.3 (RFL with mild robustness)
- LGB OOF AUC: 0.8723 (+0.0108 vs V4 0.8615) ← RFL improves LGB
- XGB OOF AUC: 0.8615 (V4: 0.8668) ← V4 params reproduced
- CatBoost OOF AUC: 0.8622 (V4 stored: 0.8756) ← V4 stored not reproducible
- Meta OOF AUC: 0.8681 (V4: 0.8837) ← regressed due to CatBoost reproduction gap
- OOF (R+P)/2: 53.40 (V4: 54.31) ← below gate

## Honest Verdict

**V24 does NOT pass acceptance gates.** OOF = 53.40 < gate 54.31.

**Root cause:** V4's stored CatBoost OOF AUC of 0.8756 cannot be reproduced
from the documented parameters (best we get is 0.8622, confirmed by multiple attempts
with different configurations). This means any full-retrain of V4's stacking base
on these parameters starts from a lower floor than V4.

**RFL partial success:** LGB-only RFL consistently improves LGB AUC by +0.007 to +0.016.
In a hybrid experiment (LGB-RFL + V4's frozen XGB/CatBoost OOFs), best OOF was 54.47 (+0.16),
but this is not a valid independent build per competition rules (blending V4 artifacts into V24).

**Key learning:** RFL as a custom objective works well for LGB on this dataset. For XGB,
the interaction between scale_pos_weight and custom objectives causes numerical instability
at small n (1352 rows, 13 positives/fold). Recommendation: LGB-only RFL in future builds
would benefit from better XGB and CatBoost base models from a fresh strong training run.

## What Worked

- LGB custom objective via LGB 4.6.x params["objective"] API
- Focal loss (q=0.0) and mild RFL (q=0.3) both improve LGB AUC
- Anti-pattern guard (r <= 2.5) prevented precision collapse
