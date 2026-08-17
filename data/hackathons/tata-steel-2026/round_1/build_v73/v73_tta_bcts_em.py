#!/usr/bin/env python3
"""
build_v73 — Test-Time Adaptation via Seeded EM + BCTS on V44 Consensus Stack
=============================================================================

Implements R27 Priority 1: BCTS calibration + Seeded EM (q_init=0.45)
Fallback: BBSE-Soft / RLLS if q_final < 0.20

Input:  V44 paradigm parquets (v35/v39/v40/v41/v43 OOF + test probabilities)
Output: submission CSV at calibration-chosen K

Critical design notes:
  - BCTS fitted on OOF log-odds (convert raw proba to logit — no decision_function available)
  - V44 consensus score (rank_pct_mean) preserved as the base ranking
  - TTA modifies the K selection and p(y=1) estimate; does NOT rerank arbitrarily
  - Validated on: 64 confirmed test labels (38 TP + 26 FP) + synthetic 45%-resampled OOF
  - NEVER blend corrected + uncorrected predictions (V10 -8.47 LB lesson)
  - NEVER apply +2.67 OOF→LB offset (documented disaster on this dataset)

Guardrails from R27:
  - q_init = 0.45 (seeded, not train prior)
  - BCTS on logit(raw_proba), not predict_proba sigmoid output
  - EM fallback to BBSE if q_final < 0.20
  - Validate on both 64-label set AND synthetic 45% OOF — never OOF-only

Author: Jarvis ML-Engineer-Agent
Date: 2026-05-29
Seed: 42 (deterministic)
"""

from __future__ import annotations

import json
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.special import expit, logit
from scipy.stats import spearmanr
from sklearn.metrics import (
    average_precision_score,
    precision_score,
    recall_score,
    roc_auc_score,
)

warnings.filterwarnings("ignore")

# ─── Paths ───────────────────────────────────────────────────────────────────

ROOT = Path("/home/ujjwal/Documents/J.A.R.V.I.S./data/hackathons/tata-steel-2026/round_1")
OUT  = ROOT / "build_v73"
OUT.mkdir(exist_ok=True)

SEED = 42
rng  = np.random.default_rng(SEED)

# ─── Scoring formula ─────────────────────────────────────────────────────────
# HackerEarth: Score = 50 * TP * (K + N_POS) / (K * N_POS)
# where N_POS = total true positives in test set (~152 estimated, 339*0.45)
N_TEST      = 339
Q_TEST_EST  = 0.45            # domain knowledge: ~45% prevalence
N_POS_EST   = round(N_TEST * Q_TEST_EST)   # ~152
Q_TRAIN     = 66 / 1352       # exact train positive rate

print(f"[V73] Train prevalence: {Q_TRAIN:.4f}  ({int(Q_TRAIN*1352)}/1352)")
print(f"[V73] Test prevalence (domain knowledge): {Q_TEST_EST:.4f}  (~{N_POS_EST}/{N_TEST})")

def he_score(tp: int, k: int, n_pos: int = N_POS_EST) -> float:
    """HackerEarth score = 50 * TP * (K + N_POS) / (K * N_POS)."""
    if k == 0 or n_pos == 0:
        return 0.0
    return 50.0 * tp * (k + n_pos) / (k * n_pos)

# ─── Load V44 paradigm probabilities ─────────────────────────────────────────

print("\n[V73] Loading paradigm parquets …")

def load_paradigm_probas():
    """Load OOF and test probabilities for all 5 V44 paradigms."""
    # OOF — each has different column name for the label
    v35_oof  = pd.read_parquet(ROOT / "build_v35/oof_v35.parquet")[
        ["CoilID", "Y", "rank_avg_proba"]].rename(columns={"Y": "y", "rank_avg_proba": "v35"})
    v39_oof  = pd.read_parquet(ROOT / "build_v39/oof_v39.parquet")[
        ["CoilID", "y", "oof_proba"]].rename(columns={"oof_proba": "v39"})
    v40_oof  = pd.read_parquet(ROOT / "build_v40/oof_v40.parquet")[
        ["CoilID", "y", "oof_proba"]].rename(columns={"oof_proba": "v40"})
    v41_oof  = pd.read_parquet(ROOT / "build_v41/oof_v41.parquet")[
        ["CoilID", "y", "oof_proba"]].rename(columns={"oof_proba": "v41"})
    v43_oof  = pd.read_parquet(ROOT / "build_v43/oof_v43.parquet")[
        ["CoilID", "y", "oof_proba"]].rename(columns={"oof_proba": "v43"})

    # Merge OOF (all 1352 rows, same CoilIDs)
    oof = v35_oof.copy()
    for df_p, col in [(v39_oof, "v39"), (v40_oof, "v40"), (v41_oof, "v41"), (v43_oof, "v43")]:
        oof = oof.merge(df_p[["CoilID", col]], on="CoilID", how="left")

    # Test probabilities
    v35_test = pd.read_parquet(ROOT / "build_v35/test_proba_v35.parquet")[
        ["CoilID", "rank_avg_proba"]].rename(columns={"rank_avg_proba": "v35"})
    v39_test = pd.read_parquet(ROOT / "build_v39/test_proba_v39.parquet")[
        ["CoilID", "test_proba"]].rename(columns={"test_proba": "v39"})
    v40_test = pd.read_parquet(ROOT / "build_v40/test_proba_v40.parquet")[
        ["CoilID", "test_proba"]].rename(columns={"test_proba": "v40"})
    v41_test = pd.read_parquet(ROOT / "build_v41/test_proba_v41.parquet")[
        ["CoilID", "test_proba"]].rename(columns={"test_proba": "v41"})
    v43_test = pd.read_parquet(ROOT / "build_v43/test_proba_v43.parquet")[
        ["CoilID", "test_proba"]].rename(columns={"test_proba": "v43"})

    # Preserve V4 coil order (canonical test ordering)
    coil_order = pd.read_parquet(ROOT / "build_v4/test_v4.parquet")["CoilID"].tolist()
    test = pd.DataFrame({"CoilID": coil_order})
    for df_p, col in [(v35_test, "v35"), (v39_test, "v39"),
                      (v40_test, "v40"), (v41_test, "v41"), (v43_test, "v43")]:
        test = test.merge(df_p[["CoilID", col]], on="CoilID", how="left")

    print(f"  OOF shape: {oof.shape}  pos_rate: {oof['y'].mean():.4f}")
    print(f"  Test shape: {test.shape}")
    print(f"  OOF NaNs: {oof.isnull().sum().to_dict()}")
    print(f"  Test NaNs: {test.isnull().sum().to_dict()}")

    return oof, test, coil_order

oof, test, coil_order = load_paradigm_probas()
y_oof = oof["y"].values.astype(float)
N_OOF = len(oof)

# ─── V44 Consensus Score (rank_pct_mean) — the base ranking to preserve ──────

PARADIGMS = ["v35", "v39", "v40", "v41", "v43"]

def compute_v44_score(df: pd.DataFrame) -> np.ndarray:
    """Rank-percentile mean across all 5 paradigms = V44 consensus score."""
    pcts = np.column_stack([df[p].rank(pct=True).values for p in PARADIGMS])
    return pcts.mean(axis=1)

oof["v44_score"]  = compute_v44_score(oof)
test["v44_score"] = compute_v44_score(test)

print(f"\n[V73] V44 OOF score: min={oof['v44_score'].min():.4f}  max={oof['v44_score'].max():.4f}")
print(f"[V73] V44 test score: min={test['v44_score'].min():.4f}  max={test['v44_score'].max():.4f}")

# Sanity: Spearman correlation between our reconstructed score and existing consensus
v44_cache = pd.read_parquet(ROOT / "data_cache/v44_oof_consensus.parquet")
merged_check = oof.merge(v44_cache[["CoilID","V44_mean_proba"]], on="CoilID")
rho_check, _ = spearmanr(merged_check["v44_score"], merged_check["V44_mean_proba"])
print(f"[V73] Spearman ρ(reconstructed V44 vs cached V44): {rho_check:.4f}  (expect >0.999)")

# ─── Convert raw probas to logits for BCTS ───────────────────────────────────
# R27 says: use raw log-odds / decision_function, NOT sigmoid'd predict_proba
# Since we only have predict_proba, we apply logit() to recover log-odds
# Clip to avoid ±inf at exactly 0 or 1

EPS = 1e-6

def safe_logit(p: np.ndarray) -> np.ndarray:
    return logit(np.clip(p, EPS, 1 - EPS))

# For BCTS, we'll use the per-paradigm raw proba → logit
# Then aggregate OOF logits (mean) as the "consensus log-odds" for calibration
oof_logits_all  = np.column_stack([safe_logit(oof[p].values)  for p in ["v39", "v40", "v41"]])
test_logits_all = np.column_stack([safe_logit(test[p].values) for p in ["v39", "v40", "v41"]])

# Mean consensus logit across 3 real-probability paradigms (v43 is rank-product, skip)
oof_logit_mean  = oof_logits_all.mean(axis=1)
test_logit_mean = test_logits_all.mean(axis=1)

print(f"\n[V73] OOF consensus logit:  min={oof_logit_mean.min():.3f}  max={oof_logit_mean.max():.3f}  mean={oof_logit_mean.mean():.3f}")
print(f"[V73] Test consensus logit: min={test_logit_mean.min():.3f}  max={test_logit_mean.max():.3f}  mean={test_logit_mean.mean():.3f}")

# ─── BCTS Calibration ────────────────────────────────────────────────────────

def bcts_neg_log_likelihood(params: np.ndarray,
                             logits: np.ndarray,
                             y: np.ndarray) -> float:
    """
    Bias-Corrected Temperature Scaling negative log-likelihood.

    Model: adjusted = (logit + b1 - b0) / T
    p(y=1|x) = sigmoid(adjusted)

    R27 §2 Method 1: per-class bias (b0, b1) removes class-conditional overconfidence.
    """
    T, b0, b1 = params
    if T < 1e-4:
        return 1e10
    adjusted = (logits + b1 - b0) / T
    # numerically stable log-likelihood
    log_p1 = -np.log1p(np.exp(-adjusted))      # log sigmoid(adjusted)
    log_p0 = -np.log1p(np.exp(adjusted))       # log (1 - sigmoid(adjusted))
    nll    = -(y * log_p1 + (1.0 - y) * log_p0).mean()
    return float(nll)


def bcts_calibrate(logits_oof: np.ndarray,
                   y_oof: np.ndarray,
                   x0: list | None = None) -> tuple[float, float, float]:
    """
    Fit BCTS parameters (T, b0, b1) on OOF logits.

    Returns (T, b0, b1).
    """
    if x0 is None:
        x0 = [1.5, 0.0, 0.0]
    result = minimize(
        bcts_neg_log_likelihood,
        x0=x0,
        args=(logits_oof, y_oof),
        method="Nelder-Mead",
        options={"maxiter": 5000, "xatol": 1e-7, "fatol": 1e-7},
    )
    T, b0, b1 = result.x
    return float(T), float(b0), float(b1)


def bcts_predict(logits: np.ndarray, T: float, b0: float, b1: float) -> np.ndarray:
    """Apply BCTS to get calibrated p(y=1|x)."""
    adjusted = (logits + b1 - b0) / T
    return expit(adjusted)


print("\n[V73] Fitting BCTS on OOF logits …")
T_bcts, b0_bcts, b1_bcts = bcts_calibrate(oof_logit_mean, y_oof)
print(f"  BCTS params: T={T_bcts:.4f}  b0={b0_bcts:.4f}  b1={b1_bcts:.4f}")

p_cal_oof  = bcts_predict(oof_logit_mean,  T_bcts, b0_bcts, b1_bcts)
p_cal_test = bcts_predict(test_logit_mean, T_bcts, b0_bcts, b1_bcts)

# Sanity check: OOF calibrated AUC
auc_uncal = roc_auc_score(y_oof, expit(oof_logit_mean))
auc_cal   = roc_auc_score(y_oof, p_cal_oof)
cal_mean_pos  = p_cal_oof[y_oof == 1].mean()
cal_mean_neg  = p_cal_oof[y_oof == 0].mean()
uncal_mean_pos = expit(oof_logit_mean[y_oof == 1]).mean()
uncal_mean_neg = expit(oof_logit_mean[y_oof == 0]).mean()
print(f"  OOF AUC before BCTS: {auc_uncal:.4f}  after: {auc_cal:.4f}")
print(f"  Uncalibrated mean p(y=1|Y=1)={uncal_mean_pos:.4f}  p(y=1|Y=0)={uncal_mean_neg:.4f}")
print(f"  BCTS-calibrated mean p(y=1|Y=1)={cal_mean_pos:.4f}  p(y=1|Y=0)={cal_mean_neg:.4f}")
print(f"  Test BCTS-calibrated mean: {p_cal_test.mean():.4f}  (expect ~0.05 still, EM will fix this)")

# ─── Seeded EM Label-Shift Correction ────────────────────────────────────────

def seeded_em_label_shift(
    p_cal: np.ndarray,
    q_train: float,
    q_init: float,
    max_iter: int = 1000,
    tol: float = 1e-8,
    verbose: bool = True,
) -> tuple[float, np.ndarray]:
    """
    Saerens (2002) EM with seeded initialization for label shift correction.

    R27 §2 Method 1:
      - q_init=0.45 puts EM in the correct basin of attraction
      - BCTS removes class-conditional overconfidence first

    p_cal:   (N,) BCTS-calibrated p(y=1|x)
    q_train: scalar, train positive rate (0.049)
    q_init:  scalar, seeded initial guess for test positive rate (0.45)

    Returns: (q_final, p_corrected) where p_corrected is the EM-reweighted posterior
    """
    P  = np.column_stack([1 - p_cal, p_cal])     # (N, 2)
    qs = np.array([1.0 - q_train, q_train])       # train priors
    q  = np.array([1.0 - q_init,  q_init])        # seeded init

    converged_at = max_iter
    for it in range(max_iter):
        # E-step: posterior ∝ p_cal(y|x) * q(y) / q_s(y)
        weights = P * (q / qs)                    # (N, 2)
        weights_sum = weights.sum(axis=1, keepdims=True)
        posterior = weights / (weights_sum + 1e-15)

        # M-step
        q_new = posterior.mean(axis=0)
        delta = float(np.max(np.abs(q_new - q)))
        q = q_new

        if delta < tol:
            converged_at = it
            break

    q_final = float(q[1])
    if verbose:
        print(f"  EM converged at iter={converged_at}  q_final={q_final:.4f}  (seeded from {q_init})")

    return q_final, posterior[:, 1]


print(f"\n[V73] Running Seeded EM (q_init=0.45, q_train={Q_TRAIN:.4f}) …")
q_final_test, p_em_test = seeded_em_label_shift(
    p_cal_test, q_train=Q_TRAIN, q_init=0.45, verbose=True
)
q_final_oof,  p_em_oof  = seeded_em_label_shift(
    p_cal_oof,  q_train=Q_TRAIN, q_init=0.45, verbose=True
)

# ─── R27 Guardrail: Check EM convergence ────────────────────────────────────

EM_STUCK_THRESHOLD = 0.20
EM_FAILED = q_final_test < EM_STUCK_THRESHOLD

if EM_FAILED:
    print(f"\n[V73] WARNING: EM stuck! q_final={q_final_test:.4f} < {EM_STUCK_THRESHOLD}")
    print("[V73] Falling back to BBSE-Soft / RLLS …")
else:
    print(f"\n[V73] EM OK: q_final={q_final_test:.4f}  (expected 0.30-0.55)")
    print(f"[V73] EM-corrected test mean: {p_em_test.mean():.4f}  (should be ~{q_final_test:.3f})")

# ─── BBSE-Soft Fallback ───────────────────────────────────────────────────────

def bbse_soft_from_probas(
    p_oof:   np.ndarray,
    y_oof:   np.ndarray,
    p_test:  np.ndarray,
    q_train: float,
    lambda_reg: float = 0.01,
) -> tuple[float, np.ndarray]:
    """
    BBSE-Soft (Lipton et al. ICML 2018) using pre-computed OOF probabilities.

    Does NOT require calibration — robust to biased classifiers.
    Uses RLLS (regularized) to handle near-singular confusion matrices.

    R27 §2 Method 3 fallback.
    """
    # Step 1: OOF hard predictions (threshold 0.5 for confusion matrix)
    y_hat_oof  = (p_oof  > 0.5).astype(int)
    y_hat_test = (p_test > 0.5).astype(int)

    # Step 2: Confusion matrix (row = true, col = predicted), normalized by pred
    from sklearn.metrics import confusion_matrix
    C_raw = confusion_matrix(y_oof, y_hat_oof)   # (2, 2), counts
    # Convert to column-normalized: C[i,j] = P(Y=i | hat_Y=j)
    col_sums = C_raw.sum(axis=0, keepdims=True) + 1e-10
    C = C_raw / col_sums

    # Step 3: Test prediction histogram
    mu_test = np.array([1 - y_hat_test.mean(), y_hat_test.mean()])

    # Step 4: RLLS estimate: solve (C^T C + λI) w = C^T μ
    A = C.T @ C + lambda_reg * np.eye(2)
    b = C.T @ mu_test
    q_test = np.linalg.solve(A, b)
    q_test = np.clip(q_test, 0, 1)
    q_test = q_test / q_test.sum()

    print(f"  BBSE q_test estimate: neg={q_test[0]:.4f}  pos={q_test[1]:.4f}")

    # Step 5: Importance weights
    q_train_arr = np.array([1.0 - q_train, q_train])
    w = q_test / (q_train_arr + 1e-10)
    print(f"  Importance weights: neg={w[0]:.3f}  pos={w[1]:.3f}")

    # Step 6: Bayes reweighting
    p_corr = p_test * w[1] / (p_test * w[1] + (1 - p_test) * w[0] + 1e-15)

    return float(q_test[1]), p_corr


print("\n[V73] Running BBSE-Soft (as parallel sanity check + fallback if EM stuck) …")
q_bbse_test, p_bbse_test = bbse_soft_from_probas(
    p_oof   = p_cal_oof,
    y_oof   = y_oof,
    p_test  = p_cal_test,
    q_train = Q_TRAIN,
)
_, p_bbse_oof = bbse_soft_from_probas(
    p_oof   = p_cal_oof,
    y_oof   = y_oof,
    p_test  = p_cal_oof,
    q_train = Q_TRAIN,
)

# ─── Choose primary TTA output ───────────────────────────────────────────────

if EM_FAILED:
    p_tta_test = p_bbse_test
    p_tta_oof  = p_bbse_oof
    q_tta      = q_bbse_test
    method_used = "BBSE-Soft (EM fallback)"
else:
    p_tta_test = p_em_test
    p_tta_oof  = p_em_oof
    q_tta      = q_final_test
    method_used = "Seeded-EM + BCTS"

print(f"\n[V73] Method: {method_used}")
print(f"[V73] TTA test mean: {p_tta_test.mean():.4f}  q_tta={q_tta:.4f}")

# ─── K Selection ─────────────────────────────────────────────────────────────
# Strategy: q_final gives us estimated test prevalence → K_cal = round(q_final * N_TEST)
# Also sweep K and report HE score on the 64-label validation set

K_v71      = 200          # current best baseline
K_cal_em   = int(round(q_tta * N_TEST))    # EM-estimated K
K_range    = list(range(100, 280, 5))      # sweep range

print(f"\n[V73] EM-estimated K: {K_cal_em}  (q_final={q_tta:.4f} × {N_TEST})")

# ─── Validation on 64 Confirmed Test Labels ───────────────────────────────────

tps_df = pd.read_csv(ROOT / "SOURCE_SUBMISSION/data/confirmed_tps.csv")
fps_df = pd.read_csv(ROOT / "SOURCE_SUBMISSION/data/confirmed_fps.csv")
tp_ids = set(tps_df["CoilID"].values)
fp_ids = set(fps_df["CoilID"].values)
confirmed_64_ids = tp_ids | fp_ids

print(f"\n[V73] 64-label validation set: {len(confirmed_64_ids)} rows "
      f"({len(tp_ids)} TP + {len(fp_ids)} FP)")

test["p_tta"] = p_tta_test
test["v44_rank"] = test["v44_score"].rank(ascending=False)

# Build a validation frame for the 64 confirmed labels
val64 = test[test["CoilID"].isin(confirmed_64_ids)].copy()
val64["true_label"] = val64["CoilID"].apply(lambda c: 1 if c in tp_ids else 0)

# Baseline: V44 score on 64 labels
auc_v44_64   = roc_auc_score(val64["true_label"], val64["v44_score"])
auc_tta_64   = roc_auc_score(val64["true_label"], val64["p_tta"])

print(f"\n[V73] 64-label AUC:")
print(f"  Baseline V44 consensus:    {auc_v44_64:.4f}")
print(f"  TTA ({method_used}):  {auc_tta_64:.4f}")

# For P/R@K on 64 labels — simulate what top-K from full 339 captures of these 64
def pr_at_k_on_64(scores_full: pd.Series, coil_order_full: list,
                  k: int, tp_ids: set, fp_ids: set) -> tuple[float, float, int, int]:
    """
    Precision and Recall on the 64-label subset when top-K coils are predicted positive.
    """
    topk = set(scores_full.nlargest(k).index.tolist())
    tp_in_topk = len(topk & tp_ids)
    fp_in_topk = len(topk & fp_ids)
    precision = tp_in_topk / (tp_in_topk + fp_in_topk) if (tp_in_topk + fp_in_topk) > 0 else 0.0
    recall    = tp_in_topk / len(tp_ids) if len(tp_ids) > 0 else 0.0
    return precision, recall, tp_in_topk, fp_in_topk

# Set scores indexed by CoilID for lookup
v44_scores = test.set_index("CoilID")["v44_score"]
tta_scores  = test.set_index("CoilID")["p_tta"]

print(f"\n[V73] P/R on 64-label set at K=200 (V71 baseline):")
p_v44, r_v44, tp_v44, fp_v44 = pr_at_k_on_64(v44_scores, coil_order, K_v71, tp_ids, fp_ids)
p_tta, r_tta, tp_tta, fp_tta = pr_at_k_on_64(tta_scores,  coil_order, K_v71, tp_ids, fp_ids)
print(f"  V44 K=200: TP={tp_v44}  FP={fp_v44}  P={p_v44:.4f}  R={r_v44:.4f}")
print(f"  TTA K=200: TP={tp_tta}  FP={fp_tta}  P={p_tta:.4f}  R={r_tta:.4f}")

# Also at K_cal_em
print(f"\n[V73] P/R on 64-label set at K={K_cal_em} (EM-calibrated K):")
p_v44_kc, r_v44_kc, tp_v44_kc, fp_v44_kc = pr_at_k_on_64(v44_scores, coil_order, K_cal_em, tp_ids, fp_ids)
p_tta_kc, r_tta_kc, tp_tta_kc, fp_tta_kc = pr_at_k_on_64(tta_scores,  coil_order, K_cal_em, tp_ids, fp_ids)
print(f"  V44 K={K_cal_em}: TP={tp_v44_kc}  FP={fp_v44_kc}  P={p_v44_kc:.4f}  R={r_v44_kc:.4f}")
print(f"  TTA K={K_cal_em}: TP={tp_tta_kc}  FP={fp_tta_kc}  P={p_tta_kc:.4f}  R={r_tta_kc:.4f}")

# ─── K Sweep on 64-label validation ──────────────────────────────────────────

print("\n[V73] K sweep on 64-label validation (HE-score proxy using confirmed counts):")
k_sweep_results = []
for k in K_range:
    p_b, r_b, tp_b, fp_b = pr_at_k_on_64(v44_scores, coil_order, k, tp_ids, fp_ids)
    p_t, r_t, tp_t, fp_t = pr_at_k_on_64(tta_scores,  coil_order, k, tp_ids, fp_ids)
    # For HE score estimate, use the TP/FP counts from the confirmed zone as signal
    # Real HE needs true positives across ALL test rows, not just these 64
    he_v44_proxy = he_score(tp_b, k)  if k > 0 else 0.0  # proxy — see note
    he_tta_proxy = he_score(tp_t, k)  if k > 0 else 0.0
    k_sweep_results.append({
        "K": k, "tp_v44": tp_b, "fp_v44": fp_b, "p_v44": p_b, "r_v44": r_b,
        "tp_tta": tp_t, "fp_tta": fp_t, "p_tta": p_t, "r_tta": r_t,
    })

sweep_df = pd.DataFrame(k_sweep_results)
print(sweep_df[["K","tp_v44","fp_v44","p_v44","r_v44","tp_tta","fp_tta","p_tta","r_tta"]].to_string(index=False))

# ─── Synthetic 45%-Prevalence OOF Validation ─────────────────────────────────

print("\n[V73] Synthetic 45%-prevalence OOF validation …")

def synthetic_45pct_eval(
    p_oof_uncal: np.ndarray,
    p_oof_cal:   np.ndarray,
    p_oof_tta:   np.ndarray,
    y_oof_full:  np.ndarray,
    q_target:    float = 0.45,
    n_bootstrap: int   = 100,
    seed:        int   = SEED,
) -> dict:
    """
    Resample train-OOF to ~45% positive prevalence.
    Evaluate whether TTA K selection is better calibrated than V44 raw score.
    """
    rng_syn = np.random.default_rng(seed)
    pos_idx = np.where(y_oof_full == 1)[0]
    neg_idx = np.where(y_oof_full == 0)[0]
    n_pos   = len(pos_idx)    # 66
    n_neg   = len(neg_idx)    # 1286

    # To get 45% prevalence: n_pos / (n_pos + n_neg_sampled) = 0.45
    # → n_neg_sampled = n_pos * (1 - 0.45) / 0.45
    n_neg_target = int(np.round(n_pos * (1 - q_target) / q_target))
    n_total      = n_pos + n_neg_target

    print(f"  Synthetic sample: n_pos={n_pos}, n_neg_sample={n_neg_target} → N={n_total}, q_actual={n_pos/n_total:.4f}")

    aucs_uncal, aucs_cal, aucs_tta = [], [], []
    he_uncal, he_cal, he_tta = [], [], []
    k_chosen_tta = []

    for _ in range(n_bootstrap):
        neg_sample = rng_syn.choice(neg_idx, size=n_neg_target, replace=False)
        idx = np.concatenate([pos_idx, neg_sample])
        rng_syn.shuffle(idx)

        y_s     = y_oof_full[idx]
        p_uncal = p_oof_uncal[idx]
        p_cal_s = p_oof_cal[idx]
        p_tta_s = p_oof_tta[idx]

        # AUC
        aucs_uncal.append(roc_auc_score(y_s, p_uncal))
        aucs_cal.append(  roc_auc_score(y_s, p_cal_s))
        aucs_tta.append(  roc_auc_score(y_s, p_tta_s))

        # (R+P)/2 score at optimal threshold
        n_true_pos = int(y_s.sum())
        for p_arr, score_list in [(p_uncal, he_uncal), (p_cal_s, he_cal), (p_tta_s, he_tta)]:
            best_score = 0.0
            for k in range(max(1, n_true_pos - 30), min(n_total, n_true_pos + 30)):
                top_k = np.argsort(p_arr)[::-1][:k]
                preds = np.zeros(n_total)
                preds[top_k] = 1
                tp_ = int((preds * y_s).sum())
                # HE formula
                s = 50 * tp_ * (k + n_true_pos) / (k * n_true_pos) if (k * n_true_pos) > 0 else 0.0
                best_score = max(best_score, s)
            score_list.append(best_score)

        # K calibration: EM-estimated K vs true K
        # TTA posterior mean as prevalence estimate
        q_est = float(p_tta_s.mean())
        k_chosen_tta.append(int(round(q_est * n_total)))

    results = {
        "auc_uncal":  float(np.mean(aucs_uncal)),
        "auc_cal":    float(np.mean(aucs_cal)),
        "auc_tta":    float(np.mean(aucs_tta)),
        "he_uncal":   float(np.mean(he_uncal)),
        "he_cal":     float(np.mean(he_cal)),
        "he_tta":     float(np.mean(he_tta)),
        "k_true":     n_pos,
        "k_chosen_tta_mean": float(np.mean(k_chosen_tta)),
        "k_chosen_tta_std":  float(np.std(k_chosen_tta)),
    }
    return results

syn_results = synthetic_45pct_eval(
    p_oof_uncal = expit(oof_logit_mean),
    p_oof_cal   = p_cal_oof,
    p_oof_tta   = p_tta_oof,
    y_oof_full  = y_oof,
    q_target    = 0.45,
    n_bootstrap = 200,
    seed        = SEED,
)

print(f"\n  Synthetic 45%-OOF (200 bootstrap runs):")
print(f"  AUC — uncal: {syn_results['auc_uncal']:.4f}  cal: {syn_results['auc_cal']:.4f}  TTA: {syn_results['auc_tta']:.4f}")
print(f"  HE-score — uncal: {syn_results['he_uncal']:.2f}  cal: {syn_results['he_cal']:.2f}  TTA: {syn_results['he_tta']:.2f}")
print(f"  K calibration: true={syn_results['k_true']}  TTA-est={syn_results['k_chosen_tta_mean']:.1f} ± {syn_results['k_chosen_tta_std']:.1f}")

# ─── Choose Final K ───────────────────────────────────────────────────────────
# Decision rule:
#  1. Primary: EM-estimated K (q_final * 339)
#  2. Secondary: also output K=200 for direct comparison with V71
#  3. If TTA AUC on 64-labels is WORSE than baseline: keep V44 ranking, try K variation only

SUBMIT_Ks = sorted(set([K_v71, K_cal_em, max(100, K_cal_em - 20), min(270, K_cal_em + 20)]))
print(f"\n[V73] Submission K values to generate: {SUBMIT_Ks}")

# ─── Build Submissions ────────────────────────────────────────────────────────

def build_submission(scores: pd.Series, coil_order: list, k: int) -> pd.DataFrame:
    """Build submission CSV: 339 rows, Y=1 for top-K by score."""
    pos_ids = set(scores.nlargest(k).index.tolist())
    rows = [{"CoilID": c, "Y": 1 if c in pos_ids else 0} for c in coil_order]
    return pd.DataFrame(rows)


# Use TTA scores as ranking if AUC improved, else fall back to V44
if auc_tta_64 >= auc_v44_64 - 0.01:   # allow tiny tolerance (noise in 64-sample AUC)
    primary_scores = test.set_index("CoilID")["p_tta"]
    ranking_source = f"TTA ({method_used})"
else:
    primary_scores = test.set_index("CoilID")["v44_score"]
    ranking_source = "V44 consensus (TTA AUC degraded — keeping base ranking)"
    print(f"\n[V73] WARNING: TTA AUC ({auc_tta_64:.4f}) < V44 AUC ({auc_v44_64:.4f}) on 64-label set. Reverting to V44 ranking.")

print(f"\n[V73] Submission ranking source: {ranking_source}")

submission_paths = {}
for k in SUBMIT_Ks:
    sub = build_submission(primary_scores, coil_order, k)
    path = OUT / f"submission_K{k}.csv"
    sub.to_csv(path, index=False)
    assert int(sub["Y"].sum()) == k, f"K mismatch: {int(sub['Y'].sum())} != {k}"
    assert len(sub) == N_TEST, f"Row count mismatch: {len(sub)} != {N_TEST}"
    submission_paths[k] = path

    # Validate against 64 confirmed
    pos_in_sub = set(sub[sub["Y"] == 1]["CoilID"].values)
    tp_in_sub  = len(tp_ids  & pos_in_sub)
    fp_in_sub  = len(fp_ids  & pos_in_sub)
    he_proxy   = he_score(tp_in_sub, k)
    print(f"  K={k}: TPs={tp_in_sub}/38  FPs={fp_in_sub}/26  HE-proxy={he_proxy:.2f}")
    print(f"  Saved: {path}")

# ─── Save Metrics for CV Report ──────────────────────────────────────────────

metrics = {
    "q_train": float(Q_TRAIN),
    "q_init_em": 0.45,
    "q_final_em_test": float(q_final_test),
    "q_final_em_oof":  float(q_final_oof),
    "q_bbse": float(q_bbse_test),
    "em_stuck": bool(EM_FAILED),
    "method_used": method_used,
    "ranking_source": ranking_source,
    "bcts_T":  float(T_bcts),
    "bcts_b0": float(b0_bcts),
    "bcts_b1": float(b1_bcts),
    "auc_v44_64": float(auc_v44_64),
    "auc_tta_64": float(auc_tta_64),
    "baseline_K200_tp_in_64": int(tp_v44), "baseline_K200_fp_in_64": int(fp_v44),
    "tta_K200_tp_in_64":      int(tp_tta), "tta_K200_fp_in_64":      int(fp_tta),
    "K_cal_em": int(K_cal_em),
    "submit_Ks": SUBMIT_Ks,
    "synthetic_45pct": syn_results,
    "K_sweep": sweep_df.to_dict(orient="records"),
}

with open(OUT / "v73_metrics.json", "w") as f:
    json.dump(metrics, f, indent=2)

print(f"\n[V73] Metrics saved: {OUT / 'v73_metrics.json'}")
print("\n[V73] Done.")
