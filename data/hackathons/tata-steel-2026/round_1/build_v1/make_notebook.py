"""
Combines all 5 step scripts into a single solution.ipynb notebook.
"""
import nbformat as nbf
from pathlib import Path

OUT_DIR = Path("/home/ujjwal/Documents/J.A.R.V.I.S./data/hackathons/tata-steel-2026/round_1/build_v1")

nb = nbf.v4.new_notebook()
cells = []

# Title cell
cells.append(nbf.v4.new_markdown_cell("""# Tata Steel AI Hackathon 2026 — Defect Detection in Hot Rolling
## Solution Notebook — Submission v1

**Author:** Ujjawal Shrivastav | **Date:** 2026-05-22

### Approach Summary
Binary classification: predict steel coil defects (4.88% positive rate, 66 defects in 1352 train rows).

Key engineering choices:
- **KNN imputation** for X15 (160 missing values, 7th strongest feature)
- **Ratio features** (X13/X36, X10/X34) encode the physical defect mechanism: rolling force rises, cooling capacity drops
- **Lag features** enabled (CoilID lag-1 autocorrelation = 0.69, sequential production order confirmed)
- **Stage aggregations** across 3 physical process clusters
- **LightGBM** with scale_pos_weight=19.5, 5-fold StratifiedKFold
- **Threshold tuning** on OOF predictions — target: maximize recall subject to precision≥0.90

**V1 honest result:** OOF AUC=0.827, OOF recall=0.924 @ threshold=0.02 (precision=0.078).
The precision target (>90%) is not met at this baseline — v2 will address with SMOTE + anomaly detection ensemble.
"""))

# Step scripts
scripts = [
    ("01_load_and_verify.py", "## Step 1: Load & Verify Data"),
    ("02_feature_engineering.py", "## Step 2: Feature Engineering (49 → 95 features)"),
    ("03_baseline_lgbm.py", "## Step 3: LightGBM Baseline — 5-Fold CV"),
    ("04_threshold_tuning.py", "## Step 4: Threshold Tuning on OOF Predictions"),
    ("05_predict_and_submit.py", "## Step 5: Final Predictions & Submission"),
]

for fname, header in scripts:
    fpath = OUT_DIR / fname
    if fpath.exists():
        code = fpath.read_text()
        cells.append(nbf.v4.new_markdown_cell(header))
        cells.append(nbf.v4.new_code_cell(code))
    else:
        cells.append(nbf.v4.new_markdown_cell(f"{header}\n\n*File not found: {fname}*"))

# Results summary cell
cells.append(nbf.v4.new_markdown_cell("""## Results Summary

| Metric | V1 Value |
|--------|----------|
| Train positives | 66 / 1352 (4.88%) |
| Features engineered | 95 (from 49 original) |
| OOF AUC | 0.827 |
| OOF Recall @ thr=0.02 | 0.924 |
| OOF Precision @ thr=0.02 | 0.078 |
| Test predicted defects | 157 / 339 |
| Full criteria met? | No — v2 needed |

### Top 3 fixes for v2
1. **SMOTE oversampling** — synthetic minority examples to sharpen boundary
2. **Anomaly detection ensemble** — Isolation Forest as meta-feature
3. **LightGBM stability** — fix dormant fold issue with `is_unbalance=True` and `min_data_in_leaf=5`
"""))

nb.cells = cells

nb_path = OUT_DIR / "solution.ipynb"
with open(nb_path, "w") as f:
    nbf.write(nb, f)

print(f"Notebook saved: {nb_path}")
