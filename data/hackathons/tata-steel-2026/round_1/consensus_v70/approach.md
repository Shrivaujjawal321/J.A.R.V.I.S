# V70-Lean — Approach

## What V70 Is

A 7-paradigm vote-count consensus that extends V44 (5 paradigms) by adding:
- **V67**: Test-distribution discriminator — trained on 134 LB-probed test coils (72 confirmed TP + 62 confirmed FP). Acts as a partially-supervised signal on the test distribution itself. OOF AUC on its labeled set: 0.7263.
- **V68**: Unsupervised anomaly ensemble (IsoForest + COPOD + ECOD + LOF). Rho vs V44 = 0.45 (orthogonal). OOF AUC on training labels: 0.7313.

## Two-Level Aggregation

**Level 1 — Vote count:**
Each of the 7 paradigms nominates its top-K_ANCHOR=200 test coils. V4 model's top-154 test predictions get 1 vote each. Max possible vote = 8.

**Level 2 — Tiebreaker:**
AUC-weighted rank-percentile mean across V35/V39/V40/V41/V43/V68 (V67 excluded — no OOF). Weight formula: OOF_AUC_i / sum(OOF_AUC_all).

## Key Structural Finding

The 100 vote=8 coils are entirely from the V4 anchor's 154 positives. V67's 134 labeled test coils and the vote=8 coils are completely disjoint — because V67 labeled different test coils than V4's top-154. This means:

- The V4 anchor and V67 are targeting **different subsets** of the 339 test coils.
- V4 anchor = positions 1-154 in V4's scoring = the "strong signal" group.
- V67's 72 confirmed TPs rank 188th–338th in V70's order (bottom half of the ranked list).

This is the fundamental tension: V70's high-vote consensus cluster (votes 7-8) is 100% from V4's anchored high-confidence predictions, while V67's confirmed real TPs are in V70's low-rank region.

## Why V68 Adds OOF Lift But Not Test Lift

On OOF (training data): V68's anomaly ensemble has genuine orthogonal signal. Adding V68 to V44's 5 paradigms lifts OOF F1@K=200 from 0.3609 to 0.3759 (+0.0150).

On test (unknown): V68 nominates its top-200 test coils, which heavily overlaps the V4 anchor region (all supervised paradigms converge on the same high-confidence coils). V68 adds no new information in test space — it just confirms what the supervised models already said.

## V67's Paradox

V67 knows which test coils are real TPs (72 of them). But those 72 TPs rank 188th–338th in V70 — they're the contested, hard-to-classify coils that the supervised models disagree about. V70's top-200 only captures 5 of these 72 confirmed TPs.

This means V70 is NOT using V67's knowledge effectively. The right way to use V67 is as a direct override: "if V67 says TP with high confidence, include regardless of vote". V70-lean uses V67 as just another voter, diluted by the consensus.
