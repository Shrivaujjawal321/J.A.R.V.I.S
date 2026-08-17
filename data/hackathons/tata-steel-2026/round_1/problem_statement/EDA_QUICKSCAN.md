# EDA Quick Scan — Tata Steel Hot Rolling Defect Dataset

**Scanned:** 2026-05-22 20:35 IST
**Source:** `/home/ujjwal/Documents/J.A.R.V.I.S./data set of tata steel/dataset/`

## Confirmed Shapes
- train: **(1352, 51)** — 49 features + CoilID + Y
- test: **(339, 50)** — 49 features + CoilID (no Y)
- sample_submission: (10, 2) — only 10 rows shown as sample format

## Class Distribution — IMBALANCED
| Y | Count | Percentage |
|---|-------|-----------|
| 0 (No defect) | 1286 | **95.12%** |
| 1 (Alpha defect) | **66** | **4.88%** |

**Only 66 positive training samples.** 5-fold stratified CV → ~13 positives per fold.

## Missing Values
- Train total missing: **249** (across 12 columns)
- Test total missing: 68

Per-column missing in train:
| Col | Missing | % |
|-----|---------|---|
| X15 | **160** | **11.83%** |
| X42 | 31 | 2.29% |
| X48 | 13 | 0.96% |
| X26 | 7 | 0.52% |
| X10, X16, X23-X25, X27 | 6 each | 0.44% |
| X8, X21 | 1 each | tiny |

X15 is the standout — significant missingness, will need careful imputation or might be a signal.

## Data Types
- 50 columns `float64`
- 1 column `int64` (CoilID)
- **No categorical columns** — no encoding needed for tree models

## Feature Scales (vary dramatically — needs analysis)
| Col | Min | Max | Mean | Std |
|-----|-----|-----|------|-----|
| X1 | 235 | 1125 | 1029 | 108 |
| X2 | 97 | 1148 | 575 | 232 |
| X3 | 124 | 1027 | 538 | 135 |
| X4 | 576 | 756 | 693 | 57 |
| X5 | 559 | 763 | 649 | 35 |

Different physical sensors clearly — temperature/pressure/speed mix. Tree models handle scale natively, no normalization needed.
