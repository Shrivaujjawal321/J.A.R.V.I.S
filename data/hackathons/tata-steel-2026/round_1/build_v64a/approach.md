# V64a Approach — V35 9-model Recipe on ENRICHED Train

## Key Change from V35
- Enriched train: 1352 orig + 134 injected (72 TPs + 62 FPs from public test)
- scale_pos_weight: 19.48 → 9.768
- Fold split: 5-fold on orig 1352 only, injected always in training

## Why This Works (vs naive enrichment)
Naive approach (fold V64a-v1): StratifiedKFold on all 1486 rows → injected rows in val
→ OOF metric computed on rows model "already saw" injected patterns from → AUC crashed 0.91→0.77

Correct approach: Keep val folds clean (orig rows only).
Injected rows act as extra training signal in EVERY fold.
Result: higher signal during training, clean OOF evaluation.
