# V54 Approach — ICR Kaggle-Winner Recipe

## Problem Profile Match

ICR 2023 (Kaggle): N=617, ~6% positives, anonymous tabular, severe public/private shift.
Tata Steel: N=1352, 4.9% positives, anonymous tabular, public/private shift known.

4 ICR gold medalists validated this recipe on exactly this problem profile.

## Key Changes vs V40/V43/V53

1. **10-fold instead of 5-fold:** Each fold sees 12% more training data.
   With only 66 positives, more training data per fold = more stable predictions.

2. **Multi-seed averaging (5 seeds):** GBDTs are sensitive to random seed at small N.
   Averaging 5 seeds reduces variance without additional feature engineering.

3. **4th learner (TabPFN/TabICL):** Non-GBDT diversity. TabPFN was designed for
   small-N tabular problems (< 1000 samples/fold). Provides orthogonal signal.

4. **NO SMOTE:** ICR winners explicitly dropped SMOTE. Our V4 uses SMOTE — confirmed
   drag. V54 uses scale_pos_weight=18.9 only.

5. **Soft pseudo-labels:** V53's best consensus (65% V39) provides confident test
   predictions. Rows with proba ≥ 0.80 added to train with weight=0.5. This is the
   key ICR Grandmaster trick: "use SOFT labels (probabilities), NOT hard 0/1".
   Implementation here uses hard Y=1 assignment but reduced sample_weight.

## Feature Set

V4's 51 SHAP-selected features + V35's 54 stand-FE features = 105 total.
V35 stand-FE are fold-isolated (setpoint medians fitted on train fold only).
This is the proven feature set from our best single-model runs.

## Submission Strategy

- Fire K=200 to protect banked 72.83 LB
- Also try K=154 (ICR recipe = exact N_POS_TEST)
- OOF F1@K=200 gate: must exceed V53 Caruana 0.391
