# Step 1 Notes — Load & Verify

## Data shapes
- train : (1352, 51)
- test  : (339, 50)
- sample: (10, 2)
- Submission must be: 339 rows × 2 cols

## Class balance
- Y=0: 1286 (95.12%)
- Y=1: 66 (4.88%)
- Imbalance: 19.5:1

## Missing values (train)
- X8: 1 (0.07%)
- X10: 6 (0.44%)
- X15: 160 (11.83%)
- X16: 6 (0.44%)
- X21: 1 (0.07%)
- X23: 6 (0.44%)
- X24: 6 (0.44%)
- X25: 6 (0.44%)
- X26: 7 (0.52%)
- X27: 6 (0.44%)
- X42: 31 (2.29%)
- X48: 13 (0.96%)

## Missing values (test)
- X15: 52 (15.34%)
- X42: 11 (3.24%)
- X48: 5 (1.47%)

## CoilID sequentiality
- Range: 1 → 1691
- Diffs mean: 1.25
- X13 lag-1 autocorrelation: 0.6924
- X13 lag-2 autocorrelation: 0.5953
- Spearman(CoilID, X13): r=-0.4907, p=0.0000
- Defect clustering (gaps ≤ 10): 36 pairs

## Verdict: Lag features valid?
YES — build lag features in Step 2

## Key observations
- Top features confirmed: X13, X10, X36, X34 (AUC 0.77–0.83)
- X15 has 160 missing train values (11.83%) — use KNN imputation
- Class imbalance is severe — scale_pos_weight = 19.5
