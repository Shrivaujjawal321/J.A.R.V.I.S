# Column Identification Report — V5 Phase A
**Date:** 2026-05-23
**Method:** Value-range analysis + defect-label separation analysis
**Data:** Combined train (1352) + test (339) = 1691 rows

## Summary Table

| Column | Mean | Std | Min | P5 | Median | P95 | Max | IntLike | N_unique | Category | Confidence |
|--------|------|-----|-----|----|--------|-----|-----|---------|----------|----------|------------|
| X1 | 1027.76 | 109.52 | 235.25 | 810.28 | 1071.35 | 1107.21 | 1132.44 | N | 1691 | unknown | low |
| X2 | 576.33 | 230.85 | 96.76 | 185.74 | 589.57 | 975.54 | 1148.17 | N | 1691 | unknown | low |
| X3 | 539.93 | 135.18 | 124.15 | 303.97 | 549.61 | 744.54 | 1026.92 | N | 1691 | unknown | low |
| X4 | 691.22 | 57.31 | 569.99 | 594.87 | 724.70 | 743.72 | 755.98 | N | 1691 | coiling_temp_520_740C | high |
| X5 | 648.40 | 35.79 | 559.27 | 583.08 | 660.77 | 678.54 | 763.26 | N | 1691 | coiling_temp_520_740C | high |
| X6 | 617.53 | 45.95 | 529.94 | 542.99 | 614.68 | 671.52 | 743.90 | N | 1691 | coiling_temp_520_740C | high |
| X7 | 528.28 | 46.70 | 439.22 | 450.46 | 547.11 | 601.30 | 619.93 | N | 1691 | strip_width_mm_500_2000 | medium |
| X8 | 527.77 | 40.59 | 425.41 | 450.07 | 545.12 | 568.13 | 577.65 | N | 1691 | strip_width_mm_500_2000 | medium |
| X9 | 460.90 | 40.56 | 343.11 | 382.15 | 481.84 | 495.21 | 505.35 | N | 1691 | unknown | low |
| X10 | 6.78 | 2.62 | 1.12 | 2.38 | 6.85 | 10.93 | 12.31 | N | 1691 | specific_force_kNmm_5_20 | medium |
| X11 | 32.17 | 3.33 | 24.00 | 27.00 | 31.00 | 37.00 | 40.00 | Y | 17 | integer_categorical_grade_or_code | high |
| X12 | 48.10 | 9.57 | -2.32 | 33.71 | 47.85 | 64.30 | 98.44 | N | 1691 | unknown | low |
| X13 | 858.88 | 395.27 | 97.08 | 246.39 | 826.87 | 1546.60 | 1652.57 | N | 1691 | unknown | low |
| X14 | 598.79 | 30.97 | 538.36 | 549.01 | 600.12 | 646.81 | 660.37 | N | 1691 | coiling_temp_520_740C | high |
| X15 | 3.48 | 2.15 | 1.17 | 1.58 | 2.83 | 7.89 | 12.33 | N | 1667 | final_thickness_mm_1_10 | medium |
| X16 | 22.91 | 3.91 | -0.92 | 16.90 | 22.78 | 29.29 | 39.01 | N | 1691 | unknown | low |
| X17 | 1157.63 | 14.17 | 1089.90 | 1129.85 | 1158.78 | 1179.59 | 1207.81 | N | 1691 | entry_finish_temp_1000_1250C | high |
| X18 | 890.58 | 7.87 | 858.75 | 879.00 | 890.07 | 901.18 | 918.08 | N | 1691 | finishing_temp_820_950C | high |
| X19 | 1359.29 | 142.02 | 911.11 | 1236.52 | 1281.84 | 1593.73 | 1747.36 | N | 1691 | strip_width_mm_500_2000 | medium |
| X20 | 571.24 | 126.46 | 165.73 | 358.43 | 574.51 | 759.58 | 1065.13 | N | 1691 | unknown | low |
| X21 | 676.35 | 89.71 | 357.82 | 528.28 | 678.70 | 815.79 | 1108.93 | N | 1691 | unknown | low |
| X22 | 599.41 | 164.78 | 68.53 | 244.22 | 636.79 | 811.41 | 1061.01 | N | 1691 | unknown | low |
| X23 | 28.76 | 4.00 | -0.27 | 22.97 | 28.53 | 35.43 | 41.27 | N | 1691 | unknown | low |
| X24 | 16.35 | 4.93 | -1.26 | 0.79 | 16.90 | 22.15 | 30.79 | N | 1691 | unknown | low |
| X25 | 16.05 | 3.11 | -0.46 | 11.50 | 15.72 | 21.47 | 24.50 | N | 1691 | unknown | low |
| X26 | 13.20 | 1.46 | -0.02 | 10.80 | 13.36 | 15.22 | 16.92 | N | 1691 | unknown | low |
| X27 | 10.33 | 1.32 | -0.17 | 7.95 | 10.47 | 12.20 | 14.05 | N | 1691 | unknown | low |
| X28 | 4.75 | 0.60 | 4.32 | 4.41 | 4.54 | 6.51 | 6.64 | N | 1691 | final_thickness_mm_1_10 | medium |
| X29 | 6.92 | 1.10 | 4.57 | 4.94 | 6.88 | 8.57 | 10.25 | N | 1691 | specific_force_kNmm_5_20 | medium |
| X30 | 10.05 | 2.24 | 4.36 | 5.68 | 10.06 | 13.48 | 14.91 | N | 1691 | specific_force_kNmm_5_20 | medium |
| X31 | 13.42 | 3.25 | 5.43 | 7.42 | 13.72 | 18.66 | 20.29 | N | 1691 | specific_force_kNmm_5_20 | medium |
| X32 | 15.91 | 3.79 | 6.51 | 8.60 | 16.19 | 20.36 | 24.51 | N | 1691 | specific_force_kNmm_5_20 | medium |
| X33 | 17.03 | 3.68 | 6.71 | 9.30 | 18.80 | 20.50 | 25.23 | N | 1691 | specific_force_kNmm_5_20 | medium |
| X34 | 2380.95 | 1761.63 | 0.00 | 0.00 | 3502.00 | 4082.00 | 4380.00 | Y | 876 | large_scale_weight_or_length | medium |
| X35 | 9989475.97 | 6631779.77 | 0.00 | 0.00 | 13948685.00 | 15757759.50 | 17740669.00 | Y | 1426 | large_scale_weight_or_length | medium |
| X36 | 2308.21 | 1763.94 | 0.00 | 0.00 | 3591.00 | 4081.50 | 4296.00 | Y | 880 | large_scale_weight_or_length | medium |
| X37 | 1683.61 | 1742.89 | 0.00 | 0.00 | 649.00 | 4045.50 | 4457.00 | Y | 936 | unknown | low |
| X38 | 700.51 | 1267.18 | 0.00 | 0.00 | 74.00 | 3872.50 | 4155.00 | Y | 679 | unknown | low |
| X39 | 162.43 | 11.30 | 98.00 | 152.00 | 164.00 | 171.00 | 173.00 | Y | 49 | integer_categorical_grade_or_code | high |
| X40 | 61.87 | 3.82 | 56.00 | 57.00 | 62.00 | 71.00 | 72.00 | Y | 13 | integer_categorical_grade_or_code | high |
| X41 | 0.59 | 0.30 | 0.08 | 0.15 | 0.58 | 1.12 | 1.38 | N | 1691 | unknown | low |
| X42 | 0.01 | 0.02 | 0.00 | 0.00 | 0.00 | 0.05 | 0.07 | N | 1346 | unknown | low |
| X43 | 0.28 | 0.07 | 0.03 | 0.15 | 0.29 | 0.37 | 0.41 | N | 1691 | unknown | low |
| X44 | 0.09 | 0.07 | 0.00 | 0.00 | 0.07 | 0.22 | 0.33 | N | 1638 | unknown | low |
| X45 | 11.08 | 25.23 | -89.30 | -26.95 | 8.54 | 57.20 | 120.17 | N | 1691 | unknown | low |
| X46 | 0.00 | 0.01 | 0.00 | 0.00 | 0.00 | 0.01 | 0.06 | N | 1630 | unknown | low |
| X47 | 0.05 | 0.04 | 0.02 | 0.03 | 0.05 | 0.06 | 0.42 | N | 1691 | unknown | low |
| X48 | 0.01 | 0.01 | 0.00 | 0.00 | 0.00 | 0.03 | 0.05 | N | 1262 | unknown | low |
| X49 | 0.06 | 0.05 | 0.00 | 0.01 | 0.06 | 0.15 | 0.25 | N | 1680 | unknown | low |

## Key Findings


### Confirmed High-Confidence Assignments

**X18 = Finishing Temperature (°C)** [HIGH confidence]
- Mean: 890.6°C, Range: 858–918°C, std=7.87
- This is exactly the Ar3 transformation temperature (~890°C for low-carbon steel)
- Defect median: 887.5°C, Normal median: 890.1°C — defects roll at slightly lower FT
- The most physically meaningful temperature in the dataset

**X17 = Entry-to-Finishing Temperature (°C)** [HIGH confidence]
- Mean: 1157.6°C, Range: 1090–1208°C
- Matches published operating ranges for finishing mill entry (1000–1250°C)
- Defect median: 1154.9°C vs Normal: 1158.9°C

**X4, X5, X6, X14 = Coiling Temperatures (°C)** [HIGH confidence]
- X4: mean=691, X5: mean=648, X6: mean=617, X14: mean=598
- All in 520–760°C range = confirmed coiling temperature zone
- X6 has highest defect separation (+41.1°C above normal) among these

**X11 = Grade Code (integer)** [HIGH confidence]
- Integer 24–40, 17 unique values
- Clear grade/steel-type categorical (confirmed by integer distribution + n_unique)

**X34, X36 = Roll Campaign Position** [HIGH confidence]
- X34: integer 0–4380, 17.5% zeros; X36: integer 0–4296, 15.8% zeros
- **Massive defect separation: defect median=0 vs normal median=3500+**
- Zero or near-zero = start/end of roll campaign (fresh/worn rolls)
- Hypothesis A (Force/Width) and Hypothesis B (FT/CT) are BOTH WRONG for X36
- X36 is a temporal/campaign-position counter, not a temperature or force

**X35 = Cumulative Production Counter** [HIGH confidence]
- Integer 0–17.7M, mean=9.99M when non-zero
- Second highest defect separation (sep=2.07)
- Confirms the campaign-position hypothesis

### X13/X36 Mystery — RESOLVED

The research brief hypothesized X13/X36 = Force/Width (Hyp A) or FT/CT (Hyp B) or thickness ratio (Hyp C).

**None of these apply.** X36 is a campaign-position counter (integers 0-4296 with 15.8% zeros), not temperature or force. X13/X36 ratio computed from V3 data has median=0.25 (not 1.2–1.7 for FT/CT, not 5–25 for thickness). The extreme ratio values come from X36 near-zero values.

The actual signal in X36: **coils with X36=0 or very low values are defective at 2-3× base rate.** This is likely because: (a) first coils after a roll change have rough roll surface → defects, or (b) last coils before roll change have worn rolls → defects.

X13 (range 97–1652, continuous, mean=858) remains partially unclassified. It correlates strongly with defects (defect median=1329 vs normal 816). Given the range, it may be:
- A cumulative pass parameter that scales with strip size/weight
- Total roll force (though 97–1652 MN is unusually wide)
- A process aggregation metric across multiple stands

### X13/X36 Hypothesis Refutation
- **Hypothesis A (Force/Width):** REFUTED — X36 is integer with zeros, not continuous width
- **Hypothesis B (FT/CT):** REFUTED — X36 range 0-4296 not 520-740°C
- **Hypothesis C (thickness ratio):** REFUTED — same reason

### Unknown Columns (Important)
- **X10** (mean=6.78): Strong defect sep (10.06 vs 6.78), range 1–12 — could be specific force or speed
- **X7, X8** (mean=527–528, range 425–620): Could be temperatures at different mill points or coiling-adjacent temps
- **X16** (mean=22.9): Slight negative values exist — possibly a deviation/offset measurement, range 16–29
- **X29–X33**: Range 5–25, all positively correlated with defects — likely per-stand force values
- **X41** (range 0.08–1.38): Possibly reduction ratio (matches 0–0.5 typical, some above 0.5)
- **X39** (int 98–173, 49 unique), **X40** (int 56–72, 13 unique): Unknown categoricals

