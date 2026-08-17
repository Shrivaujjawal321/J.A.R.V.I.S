# V32 Approach — V4-pure-prune (X35 Q3+Q4 subtraction)

## Strategy

Pure subtraction from V4's banked 154-flag submission. Drop the 23 V4-flagged test rows that sit in X35 quintiles Q3+Q4 (lowest train defect-rate buckets).

## Method

1. Compute X35 quintile cutoffs from train: [0.0, 216836, 12925764, 14410283, 15063880, 17740669]
2. Assign each test row to a quintile.
3. Take V4's flagged 154-row set (banked LB 56.98).
4. Drop the subset whose X35 falls in Q3 (16 rows) or Q4 (7 rows) = 23 rows total.
5. Submit the remaining 131 rows as positive.

## Justification

V4 OOF per-quintile precision against train labels:
- Q0: 0.119 (32 TP / 268 flagged)
- Q1: 0.127 (26 TP / 204 flagged)
- Q2: 0.025 (3 TP / 121 flagged)
- Q3: 0.022 (2 TP / 91 flagged)
- Q4: 0.037 (3 TP / 82 flagged)

V4 overflags Q3+Q4 by ~5× compared to its overall precision floor. Subset is statistically FP-enriched per train.

## Predicted LB

Under (R+P)/2 algebra with n_pos≈154 (test prevalence ~45%), V4 banked 56.98 implies R=P=0.57 on test (88 TPs in 154 flagged). If all 23 pruned are FPs: kept 131 = 88 TP + 43 FP. P=0.672, R=0.571, score=62.2. If 2 of 23 are TPs: score=60.7. Predicted range: 60-62 LB.

## Risk

If train-Q3+Q4-low-defect-rate pattern does not transfer to test, some real test positives in V4's Q3+Q4 picks will be dropped, hurting recall. Mitigation: pure subset of V4_binary — Spearman with V4_binary on kept rows is 1.0 by construction.

## Files

- solution.csv: 339 rows, 131 positive
- expected_submission.csv: identical
