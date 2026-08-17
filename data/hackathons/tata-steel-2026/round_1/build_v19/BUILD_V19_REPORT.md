# Tata Steel AI Hackathon 2026 - Round 1
# BUILD V19 REPORT: TabNet + Test-Time Augmentation

**Date:** 2026-05-23
**Engineer:** ML Engineering Specialist (Jarvis)
**Status:** COMPLETE - TabNet underperforms V5 meta ensemble; V5-only chosen

---

## 1. Executive Summary

TabNet was tried as a fundamentally different inductive bias (sparse sequential attention masks,
per-step feature selection) versus the GBDT ensemble in V5. The hypothesis: TabNets explicit
feature selection might surface different signals in this 1352-row steel-process dataset.

**Result: TabNet OOF AUC = 0.8562 vs V5 meta = 0.8886. TabNet lost by -0.032 AUC.**
No blend cleared the V5 baseline. Submission chosen = V5-only reference.
Calibrated LB estimate: **56.32** (vs banked V4 = 56.98, gap = -0.66).

---

## 2. Version Comparison

| Metric                  | V4 (banked LB) | V5 (meta OOF) | V19 TabNet OOF | V19 best blend  | V19 chosen |
|-------------------------|----------------|---------------|----------------|-----------------|------------|
| OOF AUC                 | ~0.8837        | 0.8886        | 0.8562         | 0.8870 (80/20)  | 0.8886     |
| HE OOF score            | ~0.5431        | 0.5360        | 0.5229         | 0.5354          | 0.5365     |
| Calibrated LB est       | 56.98 (actual) | ~56.32        | ~55.62         | ~56.21          | 56.32      |
| Test positives          | 154            | -             | -              | -               | 148        |

---

## 3. Phase B - TabNet 5-Fold OOF Results

### Config
- n_d=16, n_a=16, n_steps=3, gamma=1.5
- n_independent=2, n_shared=2, lambda_sparse=1e-4
- mask_type=entmax
- optimizer: Adam lr=1e-2, StepLR decay step=10 gamma=0.95
- max_epochs=200, patience=30, batch_size=256, virtual_batch_size=64
- Sample weights: pos_weight ~19.5x (4.9% class imbalance)
- Input: 59 V5 features, StandardScaler + nan_to_num

### Per-Fold AUC
| Fold | AUC    | Epochs | Best epoch |
|------|--------|--------|------------|
| 1    | 0.8143 | 40     | 10         |
| 2    | 0.8652 | 43     | 13         |
| 3    | 0.8156 | 35     | 5          |
| 4    | 0.9249 | 49     | 19         |
| 5    | 0.8916 | 48     | 18         |
| Mean | 0.8623 | -      | -          |

**Full OOF AUC (sklearn roc_auc_score): 0.8562**

### Why TabNet Failed on This Dataset
- 1352 rows is well below TabNets effective range (10k-100k+)
- Early stopping triggers at epoch 5-19: severe overfitting on small folds
- High fold variance (0.8143 to 0.9249, range=0.1106) = structural instability
- Virtual batch norm (64 samples) is noisy with ~1080 training samples per fold
- GBDTs win here: native regularization (depth/leaves/l2) fits small N better

---

## 4. Phase C - TTA + Blend Analysis

### TTA Effect
- 20 rounds, N(0, 0.01) noise at inference
- Test prediction |delta|: mean=0.00062, std=0.00097
- TTA effect = negligible. OOF AUC unchanged (0.8562 with or without TTA).
- Root cause: 1% noise is too small relative to StandardScaler-normalized features;
  TabNet already averages 5 folds so variance is low.

### Blend Results
| Config                  | OOF AUC | HE OOF | Threshold |
|-------------------------|---------|--------|-----------|
| TabNet-only (TTA)       | 0.8562  | 0.5229 | 0.0434    |
| TabNet-only (no-TTA)    | 0.8562  | 0.5229 | 0.0434    |
| V5+TabNet 80/20 (TTA)   | 0.8870  | 0.5354 | 0.0218    |
| V5+TabNet 70/30 (TTA)   | 0.8837  | 0.5352 | 0.0198    |
| V5+TabNet 50/50 (TTA)   | 0.8778  | 0.5344 | 0.0159    |
| V5-only (reference)     | 0.8886  | 0.5360 | 0.0218    |

Best blend (80/20) = 0.8870 vs V5-only 0.8886 = -0.0016 delta.
Below 0.002 safety threshold (V10 blend disaster rule). V5-only chosen.

---

## 5. Phase D - Final Submission

| Item                    | Value |
|-------------------------|-------|
| Chosen config           | V5-only (reference) |
| Hard gate zeroed        | 138/339 (X42>0.025067 OR X39>=169) |
| HE OOF score (gated)    | 0.5365 |
| Threshold               | 0.0218 |
| Test positives          | 148/339 |
| Bootstrap CI (95%)      | [0.5171, 0.5707] |
| Calibrated LB estimate  | 56.32 |
| Delta vs banked V4      | -0.66 pts |

Files: build_v19/expected_submission.csv, build_v19/submission_v19.zip

**Recommendation: Do NOT submit V19 -- it will not improve banked V4 (56.98).**

---

## 6. V19 Verdict

| Question                       | Answer |
|--------------------------------|--------|
| TabNet beats V5?               | NO. -0.032 AUC |
| Any blend beats V5?            | NO. Best blend -0.0016 AUC |
| TTA useful?                    | NO. Delta ~0.00062 |
| Submit?                        | Not recommended -- below banked LB |
| TabNet viable for this data?   | NO. Eliminated. |

---

## 7. Lessons

1. **TabNet needs large data.** Under 5k rows, GBDTs consistently dominate.
2. **TTA requires stronger base models.** On a weak model, noise averaging helps nothing.
3. **V10 blend disaster rule holds.** Even a -0.0016 blend gets caught by the safety guard.
4. **V5 meta (0.8886) is the real ceiling** on current features.
5. **The path to 60+ LB requires new features**, not model architecture changes.
