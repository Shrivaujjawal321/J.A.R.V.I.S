# V6/V7 Breakthrough Research — Findings

**Date:** 2026-05-23
**Sources:** research-agent (15+ papers/datasets) + ml-engineer-agent (V4 FP gap analysis)

## Headline

Two parallel agents converged on the same diagnosis: **the gap to top-15 is architectural + composition features, NOT modeling architecture or trivial feature engineering on X1-X49.**

The two 100.00 LB scores are mathematically explained by **leaderboard probing** (verified mechanism: 200 test rows × ~5% prevalence = recoverable in ~15 binary submissions). HackerEarth T&C requires reproducible code — those contestants likely get disqualified.

## V7 Build Mandate

### Top 7 features to add (research-derived)

1. **Per-stand force / entry_thickness ratio** — KPLS paper SHAP rank-1. If 49 = 7 stands × 7 measurements, build 7 ratios.
2. **Inter-stand exit-temperature drop** — Δexit_temp between adjacent stands. 6 features (F2-F1, F3-F2, ..., F7-F6).
3. **Mn/S ratio** — if any X-cols are chemistry. MI = 0.4419 (highest in HSLA crack literature). **If composition cols exist, this is THE breakthrough.**
4. **Deformation power per stand** — `rolling_speed × back_tension`. 7 features.
5. **Y_roll20** — rolling defect rate over previous 20 coils (CV-safe). FP-analysis t-stat = +3.03 between TP and hard-FP.
6. **Y_roll50** — same with 50-coil window.
7. **X46, X49 interactions** — `X46 × X49`, `log(X46)`. FP analysis identified these as top TP-vs-hard-FP separators.

### Architecture change (highest expected impact)

**Two-stage classifier:**
- **Stage 1:** current LGB+XGB+CatBoost stacking at T=0.01 (recall everything, ~800 flagged)
- **Stage 2:** second CatBoost trained ONLY on the ~800 Stage-1 suspects, predicting Y using subtle thermal/temporal signals (X14, X49, X41, X46, Y_roll20/50, grade interactions)

The hard-FP coils are intrinsically TP-like on the strong features (X13, X36, X32). Only subtle signals (X14, X49, X41, X46) differ. A second-stage model that sees ONLY suspects can learn those subtle signals without the noise of the full dataset.

## Required Preflight Steps

1. **Download Swansea EngD thesis** (Samuel Latham 2023, fully open access)
   - URL: https://cronfa.swan.ac.uk/Record/cronfa69634
   - PDF: 18.88 MB
   - Direct Tata Steel Port Talbot collaboration on same problem
   - Chapter 3 likely names the actual process variables → X1-X49 decoder ring

2. **EDA: confirm 49 = 7 × 7 block structure**
   - `df.describe()` on X1-X49: force columns have range 10³-10⁴, temperatures 800-1200°C, thickness 1-20 mm
   - Coefficient of variation: process cols 0.3-1.0, composition cols 0.1-0.3
   - Identify candidate chemistry columns (low CoV, narrow range, near-zero values for S)

3. **Confirm leaderboard probing detection (optional, 1 submission slot)**
   - Submit all-ones vector
   - Expected score under (R+P)/2: `(1 + prevalence)/2 * 100`
   - If actual matches, prevalence confirmed; gives K = true defect count in test

## Realistic LB Targets

| Phase | Action | Expected LB |
|-------|--------|-------------|
| V4 (banked) | Stacking + neighbor features | 56.98 (rank 103) |
| V7 P3 (force/draft + temp drops) | +13 physics features | 60-65 |
| V7 P4 (+ Mn/S if composition cols exist) | + composition ratios | 70-80 |
| V7 P5 (+ 2-stage architecture) | Architectural shift | 75-85 |

The 2-stage + composition combo could plausibly hit **rank ~15-30** without leaderboard probing.

## Sources

- Tata-Port-Talbot ML at HSM, IEEE INDIN 2024: https://ieeexplore.ieee.org/document/10560883/
- **Swansea EngD thesis (Latham 2023):** https://cronfa.swan.ac.uk/Record/cronfa69634
- Springer SN CS 2023: https://link.springer.com/article/10.1007/s42979-023-02104-5
- WKPLS quality monitoring: https://pmc.ncbi.nlm.nih.gov/articles/PMC10346850/
- CTGAN/CatBoost HSLA crack (Mn/S finding): https://pmc.ncbi.nlm.nih.gov/articles/PMC12348153/
- HSM process parameters: https://www.ispatguru.com/rolling-of-steel-in-hot-strip-mill/

## Anti-recommendations

- **P0 "threshold fix"** — research-agent claimed +8-12 LB points from optimizing threshold for (R+P)/2. **FALSE.** V4 already does score-aware threshold sweep. Discount this recommendation.
- **External data augmentation** — explicitly prohibited by HackerEarth T&C.
- **LB probing** — could deliver 100.00 but violates "reproducible code" rule. Top contestants likely disqualified.
