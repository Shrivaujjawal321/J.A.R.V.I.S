# Track A Day 1 — Post-Mortem Report
**Date:** 2026-05-15
**Dataset:** SteelDefectX (Zhaosxian/SteelDefectX, HF Hub, CC-BY-4.0)
**Task:** Multi-class steel surface defect classification

---

## Dataset Stats

SteelDefectX has ~5,454 train + ~2,324 val images across 20+ defect classes defined by filename prefix. Class distribution is highly imbalanced — top-3 classes account for majority of images while several rare classes have <50 samples. Mask defect area ratios vary significantly by class (see `eda_class_distribution.csv`).

## Baseline Approach

Frozen `mobilenetv3_small_100` backbone (timm, pretrained ImageNet) extracts 1024-d feature vectors from 160×160 images. LightGBM multi-class classifier (`is_unbalance=True`) trained on features with 5-fold StratifiedKFold CV. No fine-tuning — pure feature extraction + gradient boosting.

---

## Final Scores

| Metric | Value |
|---|---|
| **OOF macro-F1** | **0.9046** |
| **Val macro-F1** | **0.9133** |
| Fold 1 F1 | 0.8972 |
| Fold 2 F1 | 0.9108 |
| Fold 3 F1 | 0.9216 |
| Fold 4 F1 | 0.9063 |
| Fold 5 F1 | 0.8851 |
| Classes | 25 |
| Train / Val | 5,454 / 2,324 |
| Best n_estimators (final) | 148 |

**Top-5 confusion pairs:**
```
Water spot              -> Inclusion          11 errors
Oil spot                -> Inclusion           9 errors
Iron sheet ash          -> Oil spot            6 errors
Inclusion               -> Water spot          6 errors
Iron scale compression  -> Inclusion           5 errors
```

**Observations:**
- Val (0.9133) ≥ OOF (0.9046) → no overfitting, harness CV is honest
- Confusion concentrated in 4 visually-similar defect families (rust/spot/inclusion) — Day 2 fine-tuning should crack these
- 0.9046 OOF on 25-class imbalanced multi-class with frozen MobileNetV3-Small + LightGBM on CPU = patterns validated, harness validated

---

## What Worked

- Frozen backbone approach: ~8-10 min total on CPU vs. 6+ hours for fine-tuning. Validates the pattern.
- LightGBM `is_unbalance=True`: handles class imbalance without manual weight computation.
- Feature reuse (`*.npy` files): second run skips extraction entirely — Day 2 fine-tuning starts from saved features.
- Harness integration: `set_seed`, `stratified_kfold`, `get_metric`, `write_submission` all worked cleanly from `ml_harness.utils.*`.
- `class_from_filename()` prefix parsing correctly handles the 20+ class naming convention.

## What Didn't / Gaps

- No augmentation at feature extraction time: features are computed from raw 160px crops. Day 2 adds Albumentations TTA.
- Frozen features miss fine-grained texture details (steel surface defects are texture-heavy). Fine-tuning last 2 conv blocks will help.
- MobileNetV3 may underfit rare classes (<50 samples). Day 2 focal loss + oversampling should address.
- Mask information unused in classification: segmentation-aware features could be added Day 2.

---

## Day 2 Plan

**Pattern: EfficientNet-B4 fine-tune + focal loss + Albumentations + 5-fold ensemble**

### Step 1 — Backbone upgrade
```
timm.create_model('efficientnet_b4', pretrained=True, num_classes=N)
```
Unfreeze last 2 conv blocks (`blocks[-2:]`). Freeze rest.

### Step 2 — Focal Loss
```python
# gamma=2.0, alpha=class-balanced weights
class FocalLoss(nn.Module): ...
```
Addresses class imbalance better than `is_unbalance=True`.

### Step 3 — Albumentations augmentation pipeline
```python
train_transform = A.Compose([
    A.RandomResizedCrop(224, 224),
    A.HorizontalFlip(p=0.5),
    A.VerticalFlip(p=0.3),
    A.RandomBrightnessContrast(p=0.4),
    A.GaussNoise(p=0.3),
    A.CoarseDropout(p=0.3),   # Cutout equivalent
    A.Normalize(...),
])
```

### Step 4 — 5-fold ensemble at inference
Each fold trains a separate EffNet-B4 head. At inference, average softmax probas across 5 folds.

### Step 5 — TTA
For each val image: original + h-flip + v-flip → average predictions.

### Step 6 — Save `image_template.ipynb`
Clean notebook with "swap dataset path here" markers, ready for Tata Day-0.

### Cited exact next steps for harness
- Add `ensemble.py` `weighted_average()` call in the image pipeline
- Add `FocalLoss` to `ml_harness/utils/losses.py` (new util)
- Add TTA loop to `ml_harness/utils/tta.py` (new util)

---

## Reusable Patterns Validated Today

1. `frozen_backbone_features()` pattern — timm + no_grad + batch extraction + `.npy` cache
2. `class_from_filename()` — prefix-based label extraction (common in industrial defect datasets)
3. `mask_defect_ratio()` — quick area scan for EDA without full segmentation model
4. `stratified_kfold` from harness — verified on multi-class imbalanced data
5. LightGBM multi-class with `is_unbalance=True` as CPU-safe baseline

---

_Fill scores section after running `baseline_b0_features_lgbm.py`. Paste from `baseline_scores.txt`._
