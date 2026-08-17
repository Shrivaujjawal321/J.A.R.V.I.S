# V6 Approach — FT-Transformer + Tree-Stack 90/10 Blend

## Method Summary
V6 adds a Feature Tokenization Transformer (FT-Transformer) to the V5 tree stack.
Blended 90% V5 (LGB+XGB+CatBoost+LR meta) + 10% V6 (FT-Transformer) on probability level.

## Architecture (FT-Transformer)
- Feature Tokenizer: per-feature linear projection → d_token=96 embedding
- 3 Pre-LN Transformer blocks, 4 attention heads, d_ffn=192
- BCEWithLogitsLoss, pos_weight=19.48, AdamW lr=1e-4, CosineAnnealingLR
- 5-fold StratifiedKFold (seed=42), early stopping on val AUC (patience=15)

## Scoring
| Model | OOF Score | OOF AUC |
|---|---|---|
| V5 tree stack | 53.70 | 0.8886 |
| V6 FT-Transformer | 52.53 | 0.8425 |
| V6+V5 90/10 blend | 54.11 | 0.8860 |

## Submission
Blend: 90% V5 meta + 10% V6 FT-Transformer, threshold=0.025920
OOF (R+P)/2: 54.11, Bootstrap 95% CI: [53.95, 54.30]
Estimated LB (OOF + 2.67 calibration): 56.78
Test positives: 161 / 339
