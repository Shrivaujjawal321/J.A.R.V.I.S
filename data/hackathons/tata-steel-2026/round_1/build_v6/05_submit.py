"""
05_submit.py — Build submission_v6.zip in HackerEarth 3-file format:
  - solution.csv       (CoilID + Y predictions, blend version)
  - solution.ipynb     (minimal notebook documenting the approach)
  - approach.md        (method summary)
"""

import json, zipfile, textwrap
from pathlib import Path
import pandas as pd
import numpy as np

V6_DIR = Path("data/hackathons/tata-steel-2026/round_1/build_v6")

# Load chosen submission (blend is headline)
with open(V6_DIR / "chosen_threshold_v6_blend.json") as f:
    blend_meta = json.load(f)

with open(V6_DIR / "chosen_threshold_v6.json") as f:
    standalone_meta = json.load(f)

blend_sub  = pd.read_csv(V6_DIR / "expected_submission_v6_blend.csv")
standalone_sub = pd.read_csv(V6_DIR / "expected_submission_v6.csv")

print(f"Blend submission: {len(blend_sub)} rows, {blend_sub.Y.sum()} positives")
print(f"Standalone submission: {len(standalone_sub)} rows, {standalone_sub.Y.sum()} positives")

# ─── approach.md ──────────────────────────────────────────────────────────────
approach_md = f"""# V6 Approach — FT-Transformer + Tree-Stack Blend

## Method Summary

**V6** extends the V5 tree-based stacking (LGB + XGB + CatBoost + LR meta) with a
**Feature Tokenization Transformer (FT-Transformer)** — the SOTA tabular DL architecture
for datasets with high-order feature interactions that gradient-boosted trees miss.

## Architecture

- **Feature Tokenizer:** each of 59 features → d_token=96 embedding via per-feature linear + bias
- **Transformer Blocks:** 3 × Pre-LN Multi-Head Attention (4 heads) + GELU FFN (d_ffn=192)
- **CLS Token:** aggregates sequence, passed to binary classification head
- **Anti-overfit:** BatchNorm on input, attention_dropout=0.2, ffn_dropout=0.2, AdamW wd=1e-4

## Training

- 5-fold StratifiedKFold (seed=42, matches V5)
- Loss: BCEWithLogitsLoss with pos_weight=19.5 (class imbalance 4.88%)
- Optimizer: AdamW, lr=1e-4, CosineAnnealingLR schedule
- Early stopping on val AUC (patience=15)

## Feature Engineering (inherited from V5)

59 features total:
- Raw X1-X49 (selected subset)
- Physics-motivated ratios: X13/X14, X16/X14, FT/CT (X18/X14), Ar3 deviation²
- Campaign position features: X34, X36, any_campaign_zero flags
- Temporal lag: prev5_defect_rate, X13/X36/X10 lag1 + rollmean5
- Polynomial interactions of top features

## Scoring

Competition metric: (Recall + Precision) / 2 × 100

| Model                | OOF Score | OOF AUC |
|----------------------|-----------|---------|
| V5 (tree stack)      | 53.70     | 0.8886  |
| V6 (FT-Transformer)  | {standalone_meta.get("oof_score_v6", "N/A"):.2f}     | {standalone_meta.get("global_oof_auc", "N/A")}  |
| **V6+V5 Blend**      | **{blend_meta.get("oof_score_v6_blend", "N/A"):.2f}**     | **{blend_meta.get("blend_oof_auc", "N/A"):.4f}**  |

## Submission Strategy

Primary submission: **V6 + V5 blend** (50/50 probability average, threshold swept on OOF).
Trees and Transformers disagree on hard edge cases → ensemble diversifies error.

Threshold: {blend_meta.get("chosen_threshold_v6_blend", "N/A"):.6f}
Expected score: {blend_meta.get("oof_score_v6_blend", "N/A"):.2f} OOF → estimated LB ~{blend_meta.get("oof_score_v6_blend", 0) + 2.67:.2f} (V4 calibration: +2.67 observed bias)
"""

(V6_DIR / "approach.md").write_text(approach_md)
print("approach.md written")

# ─── Minimal notebook (valid ipynb) ──────────────────────────────────────────
nb = {
    "nbformat": 4,
    "nbformat_minor": 4,
    "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3.10.0"}
    },
    "cells": [
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": ["# Tata Steel AI Hackathon 2026 — V6 FT-Transformer + Blend\n",
                       "See `approach.md` for full methodology."]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "# V6: FT-Transformer on 59 physics-engineered features\n",
                "# 5-fold StratifiedKFold, blended 50/50 with V5 tree-stack\n",
                f"# OOF blend score: {blend_meta.get('oof_score_v6_blend', 0):.4f}\n",
                f"# Threshold: {blend_meta.get('chosen_threshold_v6_blend', 0):.6f}\n",
                f"# Test positives: {blend_meta.get('n_pos_test', 0)} / 339\n",
            ]
        }
    ]
}

import json as _json
(V6_DIR / "solution.ipynb").write_text(_json.dumps(nb, indent=2))
print("solution.ipynb written")

# ─── Build zip ────────────────────────────────────────────────────────────────
zip_path = V6_DIR / "submission_v6.zip"
with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
    zf.write(V6_DIR / "expected_submission_v6_blend.csv", "solution.csv")
    zf.write(V6_DIR / "solution.ipynb",                   "solution.ipynb")
    zf.write(V6_DIR / "approach.md",                      "approach.md")

print(f"submission_v6.zip written ({zip_path.stat().st_size/1024:.1f} KB)")
print("  Contains: solution.csv (blend), solution.ipynb, approach.md")
print("05_submit.py DONE")
