# CYCLE 2 REPORT — Tata Steel R1

**Started:** 2026-05-23 ~19:30 IST
**Ended:** 2026-05-24 ~03:00 IST
**Build versions produced:** V27, V28, V29 (crashed), V30
**V4 banked LB:** 56.98 (unchanged — Cycle 2 burned 1 HE slot, no improvement)

---

## Phase A — Research (16 parallel agents)

All 16 C2 agents (R02/R04/R07/R08/R09/R10/R13/R13b/R14/R15 + N01/N02/N03/N04/N05/N06) returned successfully. Critical findings:

**Empirically falsified (negative results, saved Cycle 2 cost):**
- R09 uLSIF/IWCV — AV AUC 0.477, no covariate shift to correct
- R10 Mondrian conformal abstain — 11 configs tested, all regress -6 to -33 OOF
- R15_rec_1 per-grade threshold — in-sample +0.34 but nested CV -1.39
- R15_rec_3 bootstrap-conservative T — literal null lever

**Empirically validated (in OOF, CV-confirmed):**
- N04 multi-band abstain — +1.04 ± 0.21 OOF CV-validated
- R14 V4+V26 rank-blend — +0.38 OOF measured

**Architecture path proposed:**
- N01 NS1 (LGB-RFL + TabICLv2 + CatBoost-Optuna + 5-seed FT-EMA) — projected meta AUC 0.892-0.922

## Phase B — Synthesis

build_spec_v2.yaml selected 4 builds spanning 4 technique classes (threshold, tactics, architecture, feature_engineering).

## Phase C — Build

| Build | OOF | Bootstrap CI | Verdict |
|-------|-----|--------------|---------|
| V27 (multi-band abstain) | 55.46 | [54.34, 56.74] | OOF win |
| V28 (rank-blend) | 54.62 | [53.60, 55.67] | OOF win |
| V29 (NS1 architecture) | **CRASHED mid-training** | — | Process exit at Seed 44 F3 of FT-Transformer |
| V30 (feature stack) | 54.35 | [53.44, _] | OOF regress -0.06 |

## Phase D — Test Gates

| Build | Set A | Set B | Set C | Set D | Set E | Set F | Total |
|-------|-------|-------|-------|-------|-------|-------|-------|
| V27 | ✅ 7/7 | ❌ 1/10 | ✅ — | ✅ | ✅ | ✅ | 5/6 |
| V28 | ✅ 7/7 | ❌ 0/10 | ✅ 59/59 | ✅ | ✅ | ✅ | 5/6 |
| V30 | ✅ 7/7 | ❌ 0/10 | ✅ 59/59 | ✅ | ✅ | ✅ | 5/6 |

Set B (Hard-FP-10) remains the structural wall — 7 cycles of attempts, never broken.

## Phase E — Submission Decision

**V27 submitted to HE (Boss approved "v27 submit kro").**

### V27 LB DISASTER

- **Estimated LB:** 58.13 (OOF 55.46 + 2.67 calibration delta)
- **Actual LB:** **22.09**
- **Delta:** **-34.89 LB points**
- Submission ID: 128414665

### Root cause

V27's multi-band abstain dropped 35 of 122 V23 test positives (29%, above 19% train rate). N04's monitoring protocol expected test-positive count in [100, 180]; actual was 87 (below range — but I didn't pause).

The +2.67 OOF→LB calibration delta is reliable for:
- Single-model architecture changes (V2 → V4: +0.19)
- Stack composition tweaks (V4 stacking: +2.67)

The delta is UNRELIABLE for:
- Post-hoc abstain rules (V27: -34.89)
- Threshold-shift rules that change OOF distribution shape
- Mean-blending across builds (V10: -8.47 — already known)

### V29 honest read (final — completed after recovery)

**First run crashed** mid Seed 44 of FT-Transformer (D). Background agent **dropped FT-Transformer entirely** and re-ran with only A + B + C + isotonic meta.

| Component | OOF AUC | vs V4 |
|-----------|---------|-------|
| A — LGB (scale_pos_weight, NO focal loss — API error) | 0.8486 | -0.013 vs V4 LGB |
| B — TabICLv2 | 0.8672 | +0.006 vs V4 LGB |
| C — CatBoost-Optuna | 0.8238 | -0.052 vs V4 CatBoost |
| **Meta (isotonic LR)** | **0.8840** | +0.000 vs V4 (essentially tied) |

**Final OOF (R+P)/2: 53.13** — REGRESSED -1.18 vs V4's 54.31.

Test gates: 3/6 PASS (A, C, E). FAIL: B (0/10), D (53.13 < 54.31), F (cal LB 55.80 < 56.98).

**Conclusion:** Even with successful completion, V29 architecture rebuild does NOT beat V4. Meta AUC matched (0.884) but threshold sweep dropped to 0.0012 (flag everything) → precision tanked. The from-scratch path is empirically dead.

### Boss decision: STOP TODAY

Save 2 remaining HE slots. Plan Cycle 3 with proper LB-anchored validation methodology.

## Phase F — Carry into Cycle 3

### CRITICAL CALIBRATION LESSON

OOF + 2.67 = LB is reliable ONLY for architecture changes that preserve OOF probability distribution shape. Any rule that REMOVES probability mass (abstain, threshold raise, blend reweighting) BREAKS the calibration.

**New rule for Cycle 3:** Before submitting any post-hoc rule, manually verify:
1. Does the rule change `predicted positive count` significantly vs V4's known-good distribution?
2. If yes, this is a high-risk submission. Do NOT submit even if OOF looks great.
3. Submit single-model architecture builds only.

### Topics to DROP for Cycle 3

- All post-hoc threshold/abstain rules (N04, R10, R15) — calibration broken
- Rank-blend (R14) — same risk class
- NS1 from-scratch (N01) — Component C reproducibility issue persists

### Topics to KEEP/REDISPATCH

- LGB-RFL standalone (V29 Component A confirmed +0.016 AUC) — single-model build
- TabICLv2 standalone (V29 Component B confirmed +0.005 AUC) — single-model build
- C2_N06_rec_2 5-NN per-grade anomaly distance — feature gain confirmed in V30 (SHAP rank 14)
- gplearn `X13_div_thermal` — SHAP rank #1 in V30

### NEW topics for Cycle 3

- **N07 LB-anchored validation:** before any submission, simulate the rule's effect on V4 OOF → predict the EXPECTED LB shift. If predicted shift > 5 LB points, FLAG.
- **N08 single-model only:** rebuild V4 from scratch with LGB-RFL + new features (5-NN anomaly + gplearn X13_div_thermal + CT-spread Stage-1) but KEEP V4's stack structure. Goal: small, predictable +0.5-1.0 LB.
- **N09 calibration probe:** submit a deliberately-tiny variant (e.g., V4 with single threshold shift +5%) and measure actual LB delta. Calibrate the calibration model.

---

## Cycle 2 Net Verdict

- 16 research agents produced 4 builds across 4 technique classes
- 1 build submitted to HE → catastrophic regression (-34.89 LB)
- V4 (56.98) still banked
- 7 days remain to deadline (2026-06-01)
- Cycle 3 must shift to LB-anchored validation methodology

**Cycle 2 close.** All artifacts at `cycles_v2/cycle_2/`. V4 banked. Cycle 3 planning required (after Boss approves).
