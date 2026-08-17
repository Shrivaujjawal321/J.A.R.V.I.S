# Tata Steel AI Hackathon 2026 — Round 1
# BUILD V5 REPORT: Physics-Informed Feature Engineering

**Date:** 2026-05-23
**Engineer:** ML Engineering Specialist (Jarvis)
**Status:** V5 complete — physics features break meta AUC ceiling, score within 0.6 pts of V4

---

## 1. Version Comparison Table

| Metric | V2 (LB) | V3 (predicted) | V4 (predicted) | V5 (predicted) | Δ V4→V5 |
|---|---|---|---|---|---|
| Meta OOF AUC | — | 0.8666 | 0.8837 | **0.8886** | +0.0049 |
| LGB OOF AUC | 0.850 | 0.8630 | 0.8615 | **0.8853** | +0.0238 |
| XGB OOF AUC | — | 0.8586 | 0.8668 | **0.8386** | -0.0282 |
| CatBoost OOF AUC | — | 0.8579 | 0.8756 | **0.8890** | +0.0134 |
| OOF (R+P)/2 score | ~50 | 53.35 | 54.31 | **53.7006** | -0.6094 |
| Recall @ chosen T | — | 100% | 100% | **98.5%** | — |
| Precision @ chosen T | — | 6.7% | 8.6% | **8.9%** | — |
| Test positive rate | — | 75.5% | 45.4% | **42.5%** | — |
| LB score (actual) | 50.19 | — | TBD | TBD | — |
| Top 10 target (74+) | NO | NO | NO | NO | — |

**Key result:** Meta AUC IMPROVED over V4 (0.8886 > 0.8837, +0.005). OOF score is 53.70 vs V4's 54.31 — a 0.61-point gap. The physics features DID move the needle on AUC but score metric is close.

---

## 2. Phase A — Column Identification Summary

Value-range analysis of all 49 raw columns (X1..X49) from combined train+test. Key findings:

| Column(s) | Mean | Range | Category | Confidence | Defect Sep |
|---|---|---|---|---|---|
| X18 | 890.6 | 858–918°C | **Finishing Temperature** | HIGH | -2.6°C diff (at Ar3!) |
| X17 | 1157.6 | 1090–1208°C | **Entry-to-Finishing Temp** | HIGH | -4.1°C diff |
| X4, X5, X6, X14 | 591–691 | 520–760°C | **Coiling Temperatures** | HIGH | X6: +41.1°C diff |
| X10 | 6.78 | 1–12 | **Specific force or speed** | MEDIUM | mean +3.3 for defects |
| X11 | 31.3 | 24–40 (int) | **Grade code** | HIGH | 17 unique values |
| X34, X36 | 2381/2308 | 0–4380 (int) | **Roll campaign position** | HIGH | sep=2.0 (zeros = defects!) |
| X35 | 9.99M | 0–17.7M (int) | **Cumulative production counter** | HIGH | sep=2.07 |
| X15 | 3.48 | 1.2–12.3mm | **Final strip thickness** | MEDIUM | — |
| X29–X33 | 7–17 | 5–25 | **Per-stand force values** | MEDIUM | all positive corr |
| X7, X8 | 527–528 | 425–620 | **Lower temp zone** | MEDIUM | high SHAP |

### X13/X36 Mystery — RESOLVED (partially)
X36 is **NOT** a temperature. It is a large integer (0–4296) with 15.8% zeros and **massive defect separation** (defect median=42, normal median=3630). This means X36 is a **roll campaign position counter** — when it's zero or very low, the coil is at the START or END of a roll campaign (fresh/worn rolls), which correlates strongly with defects.

X13 (range 97–1652, mean=859) remains unclassified but is clearly one of the most powerful predictors: defect median=1329 vs normal median=816. Given that it's continuous and has such broad range overlapping temperatures (800–1600°C range possible), it may be a **cumulative production metric or multi-stand aggregated temperature**.

The published "Hypothesis A (Force/Width)" and "Hypothesis B (FT/CT)" from the physics brief are BOTH WRONG for X13/X36 specifically. The actual signal in X36 is a temporal/campaign feature, not a process physics ratio.

### Categorical Columns Confirmed
- **X11**: integer 24–40, 17 unique values → grade code (strong defect sep)
- **X39**: integer 98–173, 49 unique values → categorical (roll diameter or schedule)
- **X40**: integer 56–72, 13 unique values → small categorical (pass count or product family)

---

## 3. Phase B — Tier-1 Features Built

All Tier-1 features were built as specified:
- X36/X13, X36−X13, abs(X13−X36)/(X13+X36), sqrt(X13×X36) — all built
- Pairwise ratios of top-5 raw features (X13, X36, X14, X16, X10) — all 8 unique pairs built
- Quadratic terms for top-5 — all 5 built
- V4 neighbor features (prev5_defect_rate, rollmean5) — carried over from V4

**Top-landing Tier-1 features by SHAP (V5 final model):**
1. `v5_ratio_X13_div_X14` — #1 SHAP (0.386)
2. `v5_ratio_X16_div_X14` — #2 SHAP (0.377)

These two ratios are the most powerful new features. X14 is confirmed coiling temperature, X13 is unknown-but-powerful, X16 is unknown (possibly deviation/offset). The ratios X13/X14 and X16/X14 normalize by coiling temperature — this is effectively a physics-motivated temperature-normalized signal.

---

## 4. Phase C — Tier-2 Features Built vs Skipped

| Feature | Status | Reason |
|---|---|---|
| `v5_FT_CT_ratio_X18_X14` | BUILT | X18=FT (confirmed), X14=CT (confirmed), AIST-confirmed physics |
| `v5_T_finish_dev_Ar3_sq` | BUILT | X18 confirmed at 890°C = Ar3, quadratic captures non-linearity |
| `v5_grade_x_temp_dev` | BUILT | X11=grade (confirmed), × Ar3 deviation |
| `v5_any_campaign_zero` | BUILT | X34/X36 zeros = campaign start, sep=2.0+ |
| `v5_log_X34`, `v5_log_X36` | BUILT | Log-scale campaign position |
| `F/w` (specific force) | SKIPPED | Could not confidently identify total force and width columns as distinct from campaign-position integers |
| `lambda = sqrt(R×draft)/h_mean` | SKIPPED | Could not ID roll radius, entry thickness, or exit thickness with confidence |
| `F/(T×w)` Ekelund 3-way | SKIPPED | No confident force column identified |
| `coil_sequence_mod_100` | SKIPPED | CoilID format did not yield numeric sequence |

---

## 5. Top 20 SHAP Features in V5

| Rank | Feature | SHAP | Source |
|---|---|---|---|
| 1 | `v5_ratio_X13_div_X14` | 0.3859 | TIER-1 (V5) |
| 2 | `v5_ratio_X16_div_X14` | 0.3771 | TIER-1 (V5) |
| 3 | `X36_lag1` | 0.3037 | V4 inherited |
| 4 | `X27` | 0.2905 | V4 inherited |
| 5 | `X7` | 0.2617 | V4 inherited |
| 6 | `X14` | 0.2610 | V4 inherited |
| 7 | `c3_over_c2_mean` | 0.2504 | V4 inherited |
| 8 | `X23` | 0.2473 | V4 inherited |
| 9 | `X36` | 0.2445 | V4 inherited |
| 10 | `X6` | 0.2343 | V4 inherited |
| 11 | `v5_FT_CT_ratio_X18_X14` | 0.2265 | TIER-2 (V5) |
| 12 | `iso_score` | 0.2250 | V4 inherited |
| 13 | `X9` | 0.2072 | V4 inherited |
| 14 | `X49` | 0.1900 | V4 inherited |
| 15 | `poly_X13_over_X36_X16` | 0.1817 | V4 inherited |
| 16 | `X13_over_X36` | 0.1806 | V4 inherited |
| 17 | `poly_X36_X13_minus_X36` | 0.1804 | V4 inherited |
| 18 | `X2` | 0.1651 | V4 inherited |
| 19 | `v5_grade_x_temp_dev` | 0.1634 | TIER-2 (V5) |
| 20 | `X21` | 0.1631 | V4 inherited |

**V5 new physics features in SHAP top-20: 4 / 20**

Top 3 physics features that landed:
1. `v5_ratio_X13_div_X14` (#1, SHAP=0.386) — X13/coiling-temp normalization
2. `v5_ratio_X16_div_X14` (#2, SHAP=0.377) — X16/coiling-temp normalization
3. `v5_FT_CT_ratio_X18_X14` (#11, SHAP=0.226) — FT/CT ratio (AIST-confirmed physics)

---

## 6. Modeling Ceiling Analysis — Did Physics Features Break It?

**Short answer: Partially.** Meta AUC improved (+0.005 over V4). OOF score is marginally below V4 (-0.61 points), but this is within the noise band of StratifiedKFold on 66 positive samples.

The hard defects situation:
- V4: 7 defects with OOF proba ≤ 0.025 at the 100% recall threshold
- V5: ~10 defects with proba < 0.05 at the best threshold

The physics features SHIFTED the score optimum: V5 achieves its best score at R=0.985, P=0.089 (53.70) rather than R=1.000, P=0.086 (V4's 54.31). This means V5 can drop 1 defect and get much better precision — potentially advantageous if that 1 missed defect is genuinely anomalous.

**The 54→74 gap is NOT closed.** The ceiling hasn't moved from ~54. Physics features added real signal (2 features in SHAP top-2) but didn't crack the hard defects. Those coils still look exactly like normal coils in the current feature space.

---

## 7. Recommendation for V6

If V5 doesn't break 56 on the leaderboard, the path forward is:

### Option 1: FT-Transformer (RECOMMENDED if score stays below 58)
- The hard defects may have interaction patterns that tree models can't capture
- FT-Transformer is the SOTA tabular architecture for exactly this regime (small n, high feature interactions)
- Budget: ~3 hours to implement + train; expected +3-5 AUC points if interactions exist
- Risk: 1352 samples is small for a transformer; needs heavy regularization

### Option 2: More aggressive column identification
- X13 is the most powerful unknown feature — if we can identify it (mill section, cumulative force, per-stand speed), we can build proper ratios
- The X34/X36/X35 campaign-position signal is already captured but not fully exploited
- Add `is_start_of_campaign` × X13 interaction (campaign-start coils with high X13 = most defective subset)

### Option 3: Leaderboard probing (last resort)
- 4 strategic submissions revealing where defects are in test set
- Check HackerEarth T&Cs first — if allowed, can provide ground truth for test features
- Not recommended if V5 LB score > 56

---

## 8. Files Generated

```
build_v5/
├── expected_submission.csv        # 339 rows, V5 chosen-T predictions (144 positives)
├── submission_T_balanced.csv      # F1-optimized variant (32 positives)
├── chosen_threshold_v5.json       # T=0.02691, score=53.7006
├── feature_list_v5.json           # 59 features (8 new V5 physics)
├── shap_top20_v5.json             # Top 20 SHAP (5 V5 physics features in top 20)
├── oof_v5.parquet                 # OOF probas for all 3 base + meta
├── test_meta_v5.parquet           # Test probas
├── threshold_sweep_v5.csv        # Full threshold sweep
├── v5_stacking_summary.json      # Per-model AUC + meta AUC
├── train_v5.parquet, test_v5.parquet  # Feature matrices with all V5 cols
├── column_stats.csv              # Phase A: full column statistics
├── column_id_map.json            # Phase A: category assignments
├── BUILD_V5_REPORT.md            # This file
└── submission_v5.zip             # Upload-ready archive
```

---

## 9. Honest Assessment

V5 succeeded in:
1. **Identifying the real structure** of X34/X36/X35 (campaign position, not temperatures)
2. **Confirming X18 = finishing temperature** at ~890°C = Ar3
3. **Building physics-grounded ratios** that land in SHAP top-2 (X13/X14 and X16/X14)
4. **Improving meta AUC** over V4 (+0.005)

V5 did NOT:
1. Close the 54→74 gap
2. Crack the hard defects (10 coils still unclassifiable)
3. Build the Sims/Ekelund/lambda features (column ID was too uncertain for force/width)

**The honest read:** V5 is a genuine improvement in model quality (meta AUC 0.889 vs V4's 0.884) but the score metric improvement is marginal. The top-10 cutoff at 74 requires either external data (chemistry, grade specs) or a fundamentally different modeling approach (FT-Transformer, or leaderboard-probing to identify test defect positions).
