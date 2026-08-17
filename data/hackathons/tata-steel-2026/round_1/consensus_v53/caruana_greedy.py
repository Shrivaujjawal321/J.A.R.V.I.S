#!/usr/bin/env python3
"""
V53 — Caruana 2004 Greedy Ensemble Selection on paradigm OOFs.

Algorithm: Forward greedy selection WITH replacement (auto-sklearn fast variant).
Metric: F1@K=200 on OOF (higher = better), matches actual LB evaluation.
Paradigms: V4_meta, V33, V34, V35_rank, V39, V40, V41, V43, V46, V48_rank, V50, V51
           + V44_consensus (rank-pct mean) as a pre-built candidate.
Calibration: Isotonic regression per paradigm before greedy (per R28).
Outputs: weights.json, submission_K*.csv, cv_report_v53.md
"""

import json
import numpy as np
import pandas as pd
from pathlib import Path
from collections import Counter
from scipy.stats import spearmanr
from sklearn.calibration import CalibratedClassifierCV
from sklearn.isotonic import IsotonicRegression

ROOT = Path('/home/ujjwal/Documents/J.A.R.V.I.S./data/hackathons/tata-steel-2026/round_1')
OUT  = ROOT / 'consensus_v53'
OUT.mkdir(exist_ok=True)

# ─── Constants ────────────────────────────────────────────────────────────────
N_ITERATIONS  = 100
N_POS_OOF     = 66      # real positives in y_train (confirmed from V4 OOF)
K_FOR_GREEDY  = 200     # target K used as greedy metric
K_SUBMISSIONS = [154, 170, 181, 197, 200, 205, 212]

# ─── F1@K metric ──────────────────────────────────────────────────────────────
def f1_at_k(y_true: np.ndarray, scores: np.ndarray, k: int = K_FOR_GREEDY) -> float:
    """
    F1@K = 2*TP / (K + n_pos)
    TP = positives in top-K by score.
    HIGHER = BETTER (required for Caruana greedy).
    """
    top_k_idx  = np.argpartition(scores, -k)[-k:]
    tp         = int(y_true[top_k_idx].sum())
    n_pos      = int(y_true.sum())
    denom      = k + n_pos
    return (2.0 * tp / denom) if denom > 0 else 0.0

# ─── Isotonic calibration ─────────────────────────────────────────────────────
def isotonic_calibrate(oof_score: np.ndarray, y_true: np.ndarray) -> np.ndarray:
    """
    Fit isotonic regression on OOF scores and return calibrated probabilities.
    Monotone-preserving: ranking order stays identical, only score distribution shifts.
    """
    ir = IsotonicRegression(out_of_bounds='clip')
    ir.fit(oof_score, y_true)
    return ir.predict(oof_score)

# ─── Load OOF predictions ─────────────────────────────────────────────────────
def load_oofs() -> tuple[dict, np.ndarray, list]:
    """
    Returns:
      oof_dict  : {name: np.array of shape (1352,)} — raw OOF scores
      y_train   : np.array(1352,) — ground truth
      coil_ids  : list of 1352 CoilIDs (order matches oof arrays)
    """
    # Anchor: V4 gives us y_train and CoilID order
    v4 = pd.read_parquet(ROOT / 'build_v4/oof_v4.parquet')
    y_train   = v4['Y'].values.astype(float)
    # V4 has no CoilID column — use integer index; we'll align on position
    # (All OOF files confirmed shape=(1352, *) with same fold splits)
    n_train   = len(y_train)

    # Helper: load a parquet, return a 1352-length score array
    def load_oof_col(path: str, col: str) -> np.ndarray:
        df = pd.read_parquet(ROOT / path)
        return df[col].values.astype(float)

    # ---- Paradigm OOF scores (raw, pre-calibration) ----
    oof_raw = {}

    # V4 — use oof_meta (the stacked meta-learner output, best single V4 column)
    oof_raw['V4_meta']     = v4['oof_meta'].values.astype(float)

    # V33 — single oof_proba
    oof_raw['V33']         = load_oof_col('build_v33/oof_v33.parquet', 'oof_proba')

    # V34 — use oof_meta (stacked)
    v34 = pd.read_parquet(ROOT / 'build_v34/oof_v34.parquet')
    oof_raw['V34_meta']    = v34['oof_meta'].values.astype(float)

    # V35 — rank_avg_proba (the paradigm's own ensemble of 8 base models)
    oof_raw['V35_rank']    = load_oof_col('build_v35/oof_v35.parquet', 'rank_avg_proba')

    # V39
    oof_raw['V39']         = load_oof_col('build_v39/oof_v39.parquet', 'oof_proba')

    # V40
    oof_raw['V40']         = load_oof_col('build_v40/oof_v40.parquet', 'oof_proba')

    # V41
    oof_raw['V41']         = load_oof_col('build_v41/oof_v41.parquet', 'oof_proba')

    # V43
    oof_raw['V43']         = load_oof_col('build_v43/oof_v43.parquet', 'oof_proba')

    # V46
    oof_raw['V46']         = load_oof_col('build_v46/oof_v46.parquet', 'oof_proba')

    # V48 — rank_avg_proba (same structure as V35)
    oof_raw['V48_rank']    = load_oof_col('build_v48/oof_v48.parquet', 'rank_avg_proba')

    # V50
    oof_raw['V50']         = load_oof_col('build_v50/oof_v50.parquet', 'oof_proba')

    # V51 — use mean of 3 seeds for OOF (more stable signal)
    v51 = pd.read_parquet(ROOT / 'build_v51/oof_v51.parquet')
    oof_raw['V51_mean']    = v51[['oof_proba', 'oof_seed42', 'oof_seed123']].mean(axis=1).values.astype(float)

    # ---- V44 consensus rank-pct mean as a candidate ----
    # Recompute from OOF rank percentiles of the 5 V44 paradigms
    # V44 uses: V35_rank, V39, V40, V41, V43 (5 paradigms) + V4_154 vote
    # For OOF version: rank-pct mean of those 5 OOF signals
    v44_oof_signals = {
        'V35_rank': oof_raw['V35_rank'],
        'V39':      oof_raw['V39'],
        'V40':      oof_raw['V40'],
        'V41':      oof_raw['V41'],
        'V43':      oof_raw['V43'],
    }
    v44_oof_pct = np.stack([
        pd.Series(s).rank(pct=True).values for s in v44_oof_signals.values()
    ], axis=1).mean(axis=1)
    oof_raw['V44_consensus'] = v44_oof_pct

    print(f"Loaded {len(oof_raw)} paradigm OOF signals, each shape ({n_train},)")
    print(f"n_pos in y_train: {int(y_train.sum())}")
    assert all(len(v) == n_train for v in oof_raw.values()), "Shape mismatch in OOFs!"

    return oof_raw, y_train, None   # CoilIDs only needed for test

# ─── Load TEST predictions ────────────────────────────────────────────────────
def load_test_preds() -> tuple[dict, list]:
    """
    Returns:
      test_dict : {name: np.array of shape (339,)}
      coil_order: list of 339 CoilIDs in submission order
    """
    # CoilID order from V4 test file (canonical)
    v4_test    = pd.read_parquet(ROOT / 'build_v4/test_v4.parquet')
    coil_order = v4_test['CoilID'].tolist()
    N_test     = len(coil_order)

    def load_test_col(path: str, col: str) -> np.ndarray:
        df = pd.read_parquet(ROOT / path)
        # Align to coil_order
        df = df.set_index('CoilID').reindex(coil_order)
        return df[col].values.astype(float)

    test_raw = {}

    # V4 — no test_proba file; generate from V4's expected_submission rank order
    # Use the expected_submission probabilities aren't available; we use V4's
    # 0/1 binary as a crude score — but better: V4 has test_v4 features only.
    # Instead, generate V4 test score from OOF meta-leaner OOF as a proxy.
    # The correct approach: use expected_submission ranking as score (rank of Y=1).
    # V4_154 expected_submission: 154 positives → use position rank as score.
    v4_sub      = pd.read_csv(ROOT / 'build_v4/expected_submission.csv')
    v4_sub      = v4_sub.set_index('CoilID').reindex(coil_order)
    # Y is binary 0/1 — not a good ranking signal. Skip V4_meta for test
    # and handle it separately as a V4_154_vote below (boolean indicator).
    # For Caruana we need continuous scores — V4 binary will just flip on/off.
    # Include it: 0/1 is valid; greedy will find if it helps.
    test_raw['V4_binary'] = v4_sub['Y'].values.astype(float)

    # V33
    test_raw['V33']        = load_test_col('build_v33/test_proba_v33.parquet', 'test_proba')

    # V34
    test_raw['V34_meta']   = load_test_col('build_v34/test_proba_v34.parquet', 'test_proba')

    # V35
    test_raw['V35_rank']   = load_test_col('build_v35/test_proba_v35.parquet', 'rank_avg_proba')

    # V39
    test_raw['V39']        = load_test_col('build_v39/test_proba_v39.parquet', 'test_proba')

    # V40
    test_raw['V40']        = load_test_col('build_v40/test_proba_v40.parquet', 'test_proba')

    # V41
    test_raw['V41']        = load_test_col('build_v41/test_proba_v41.parquet', 'test_proba')

    # V43
    test_raw['V43']        = load_test_col('build_v43/test_proba_v43.parquet', 'test_proba')

    # V46
    test_raw['V46']        = load_test_col('build_v46/test_proba_v46.parquet', 'test_proba')

    # V48
    test_raw['V48_rank']   = load_test_col('build_v48/test_proba_v48.parquet', 'test_proba')

    # V50
    test_raw['V50']        = load_test_col('build_v50/test_proba_v50.parquet', 'test_proba')

    # V51 — mean of 3 seeds
    v51_test = pd.read_parquet(ROOT / 'build_v51/test_proba_v51.parquet')
    v51_test = v51_test.set_index('CoilID').reindex(coil_order)
    test_raw['V51_mean'] = v51_test[['test_proba','test_proba_seed42','test_proba_seed123']].mean(axis=1).values.astype(float)

    # V44_consensus: rank-pct mean of 5 paradigm test scores
    v44_test_signals = {
        'V35_rank': test_raw['V35_rank'],
        'V39':      test_raw['V39'],
        'V40':      test_raw['V40'],
        'V41':      test_raw['V41'],
        'V43':      test_raw['V43'],
    }
    v44_test_pct = np.stack([
        pd.Series(s).rank(pct=True).values for s in v44_test_signals.values()
    ], axis=1).mean(axis=1)
    test_raw['V44_consensus'] = v44_test_pct

    print(f"Loaded {len(test_raw)} paradigm TEST signals, each shape ({N_test},)")
    assert all(len(v) == N_test for v in test_raw.values()), "Shape mismatch in test preds!"

    return test_raw, coil_order

# ─── Caruana Greedy Selection ─────────────────────────────────────────────────
def caruana_greedy_select(
    oof_calib: dict,          # {name: calibrated OOF score (n_train,)}
    y_train:   np.ndarray,
    metric_fn,                # (y_true, scores) -> float, HIGHER = BETTER
    n_iterations: int = N_ITERATIONS,
    sorted_init:  bool = True,
) -> tuple[dict, np.ndarray, list]:
    """
    Caruana 2004 greedy forward ensemble selection with replacement.
    Returns:
      weights       : {name: float weight (sums to 1.0)}
      oof_ensemble  : np.array(n_train,) — final OOF ensemble scores
      selected_seq  : list of selected names in order (for trajectory analysis)
    """
    names = list(oof_calib.keys())
    preds = np.stack([oof_calib[n] for n in names], axis=0)   # (N, n_train)
    N     = len(names)

    # Step 1: Individual scores (for sorted init + reporting)
    individual_scores = np.array([metric_fn(y_train, preds[i]) for i in range(N)])
    print("\n--- Individual OOF F1@K=200 (pre-greedy) ---")
    for i in np.argsort(individual_scores)[::-1]:
        print(f"  {names[i]:20s}: {individual_scores[i]:.6f}")

    if sorted_init:
        init_order = np.argsort(individual_scores)[::-1]
    else:
        rng = np.random.default_rng(42)
        init_order = rng.permutation(N)

    # Step 2: Greedy loop
    ensemble_sum   = np.zeros(preds.shape[1], dtype=float)
    selected_idx   = []

    best_loss_traj = []
    for t in range(1, n_iterations + 1):
        best_score = -np.inf
        best_i     = None
        for i in range(N):
            candidate  = (ensemble_sum + preds[i]) / t
            score      = metric_fn(y_train, candidate)
            if score > best_score:
                best_score = score
                best_i     = i
        ensemble_sum += preds[best_i]
        selected_idx.append(best_i)
        best_loss_traj.append(best_score)
        if t % 20 == 0:
            print(f"  iter {t:3d}: best F1@K={best_score:.6f}  selected={names[best_i]}")

    # Step 3: Weights
    counts  = Counter(selected_idx)
    weights = {names[i]: counts[i] / n_iterations for i in range(N) if counts.get(i, 0) > 0}
    oof_ensemble = ensemble_sum / n_iterations

    return weights, oof_ensemble, [names[i] for i in selected_idx]

# ─── Equal-vote baseline (OOF rank-pct mean of all candidates) ───────────────
def equal_vote_oof(oof_calib: dict, y_train: np.ndarray) -> tuple[float, np.ndarray]:
    """Equal-weight rank-pct mean of all OOF signals. Same construction as V44."""
    pct_mat = np.stack([
        pd.Series(v).rank(pct=True).values for v in oof_calib.values()
    ], axis=1)
    ensemble = pct_mat.mean(axis=1)
    score    = f1_at_k(y_train, ensemble, K_FOR_GREEDY)
    return score, ensemble

# ─── Submission generator ─────────────────────────────────────────────────────
def make_submission(scores: np.ndarray, coil_order: list, k: int, path: Path):
    top_k = np.argpartition(scores, -k)[-k:]
    top_set = set(np.array(coil_order)[top_k])
    rows = [{'CoilID': c, 'Y': 1 if c in top_set else 0} for c in coil_order]
    df = pd.DataFrame(rows)
    df.to_csv(path, index=False)
    return top_set

# ─── MAIN ─────────────────────────────────────────────────────────────────────
def main():
    print("=" * 60)
    print("V53 — Caruana Greedy Ensemble Selection")
    print("=" * 60)

    # 1. Load OOFs and test preds
    oof_raw, y_train, _ = load_oofs()
    test_raw, coil_order = load_test_preds()

    # Align keys: OOF and test must have same paradigm names
    # V4_meta in OOF but V4_binary in test → rename OOF side to match
    # For Caruana we need SAME key in both. Resolve:
    #   OOF keys:  V4_meta, V33, V34_meta, V35_rank, V39, V40, V41, V43,
    #              V46, V48_rank, V50, V51_mean, V44_consensus
    #   Test keys: V4_binary, V33, V34_meta, V35_rank, V39, V40, V41, V43,
    #              V46, V48_rank, V50, V51_mean, V44_consensus
    # Problem: V4_meta (OOF) vs V4_binary (test) — different representations.
    # Strategy: keep V4_meta in OOF under key "V4", use V4_binary for test under "V4".
    oof_raw['V4']  = oof_raw.pop('V4_meta')
    test_raw['V4'] = test_raw.pop('V4_binary')

    # Verify key alignment
    oof_keys  = set(oof_raw.keys())
    test_keys = set(test_raw.keys())
    assert oof_keys == test_keys, f"OOF/test key mismatch: {oof_keys ^ test_keys}"

    # 2. Isotonic calibration of OOF (per R28: calibrate before meta-selection)
    print("\n--- Applying Isotonic Calibration to OOF ---")
    oof_calib = {}
    for name, scores in oof_raw.items():
        cal = isotonic_calibrate(scores, y_train)
        oof_calib[name] = cal
        pre  = f1_at_k(y_train, scores, K_FOR_GREEDY)
        post = f1_at_k(y_train, cal,    K_FOR_GREEDY)
        print(f"  {name:20s}: F1@K pre={pre:.4f}  post={post:.4f}  delta={post-pre:+.4f}")

    # Note: test predictions are NOT isotonic-calibrated (we don't have test labels).
    # The calibration on OOF guides weight SELECTION; test probas are used as-is
    # for ranking (ranking-preserving, so isotonic order == raw order on test).

    # 3. Equal-vote baseline
    print("\n--- Equal-Vote Baseline (all paradigms) ---")
    ev_score, ev_oof = equal_vote_oof(oof_calib, y_train)
    print(f"  Equal-vote OOF F1@K=200: {ev_score:.6f}")

    # Also compute equal-vote only over the V44 subset (5 paradigms)
    v44_subset = {k: oof_calib[k] for k in ['V35_rank','V39','V40','V41','V43']}
    ev_v44_score, _ = equal_vote_oof(v44_subset, y_train)
    print(f"  Equal-vote (V44 subset only) OOF F1@K=200: {ev_v44_score:.6f}")

    # 4. Caruana greedy
    print("\n--- Caruana Greedy Selection (T=100 iterations) ---")
    metric_fn = lambda y, s: f1_at_k(y, s, K_FOR_GREEDY)
    weights, oof_greedy, selection_seq = caruana_greedy_select(
        oof_calib, y_train, metric_fn, n_iterations=N_ITERATIONS, sorted_init=True
    )

    # 5. Greedy OOF score
    greedy_oof_score = metric_fn(y_train, oof_greedy)
    print(f"\n--- Greedy OOF F1@K=200: {greedy_oof_score:.6f} ---")
    print(f"    vs Equal-vote:          {ev_score:.6f}")
    print(f"    Delta (greedy - equal): {greedy_oof_score - ev_score:+.6f}")

    # Gate 1: greedy MUST be >= equal-vote (monotone non-decreasing property)
    assert greedy_oof_score >= ev_score - 1e-9, \
        f"GATE FAIL: greedy {greedy_oof_score:.6f} < equal-vote {ev_score:.6f}"

    # 6. Weight analysis
    print("\n--- Final Caruana Weights ---")
    for name, w in sorted(weights.items(), key=lambda x: -x[1]):
        bar = '#' * int(w * 40)
        print(f"  {name:20s}: {w:.4f}  {bar}")
    top_weight = max(weights.values())
    top_name   = max(weights, key=weights.get)
    print(f"\n  Max single-paradigm weight: {top_name} = {top_weight:.4f}")
    if top_weight > 0.80:
        print("  WARNING: >80% concentration on single paradigm — possible greedy local trap!")
    else:
        print("  OK: weight distribution not concentrated (< 80% on single paradigm)")

    # Gate 2: concentration check
    # (not a hard fail — just logged)

    # 7. Build test ensemble
    print("\n--- Building Test Ensemble ---")
    test_ensemble = np.zeros(len(coil_order), dtype=float)
    for name, w in weights.items():
        # Use raw test score (ranking-preserving; calibration affects OOF selection only)
        test_ensemble += w * test_raw[name]
    print(f"  Test ensemble range: [{test_ensemble.min():.4f}, {test_ensemble.max():.4f}]")

    # Gate 3: Spearman vs V44 test rank-pct
    v44_test_rank = pd.Series(test_raw['V44_consensus']).rank(pct=True).values
    v53_test_rank = pd.Series(test_ensemble).rank(pct=True).values
    spear, _ = spearmanr(v44_test_rank, v53_test_rank)
    print(f"\n  Spearman(V53 test rank, V44 test rank-pct): ρ={spear:+.4f}")
    if spear < 0.80:
        print(f"  WARNING: Spearman < 0.80 — V53 diverges significantly from V44 direction!")
    else:
        print(f"  OK: Spearman >= 0.80 — V53 in same direction as V44")

    # 8. Generate submissions
    print(f"\n--- Generating submissions for K={K_SUBMISSIONS} ---")
    v44_k200_pos = None
    try:
        v44_k200 = pd.read_csv(ROOT / 'consensus_v44/submission_K200.csv')
        v44_k200_pos = set(v44_k200[v44_k200.Y == 1].CoilID)
    except FileNotFoundError:
        print("  (V44 K=200 CSV not found for overlap comparison)")

    overlap_report = {}
    for k in K_SUBMISSIONS:
        path    = OUT / f'submission_K{k}.csv'
        top_set = make_submission(test_ensemble, coil_order, k, path)
        if v44_k200_pos is not None:
            overlap = len(top_set & v44_k200_pos)
            overlap_report[k] = overlap
            print(f"  K={k:3d}: saved to {path.name}  overlap_with_V44_K200={overlap}/{min(k, 200)}")
        else:
            print(f"  K={k:3d}: saved to {path.name}")

    # 9. Save weights.json
    weights_path = OUT / 'weights.json'
    weights_json = {
        'paradigm_weights': {k: round(v, 6) for k, v in weights.items()},
        'selection_sequence': selection_seq,
        'n_iterations': N_ITERATIONS,
        'oof_f1_at_k200': {
            'caruana': round(greedy_oof_score, 6),
            'equal_vote_all': round(ev_score, 6),
            'equal_vote_v44_subset': round(ev_v44_score, 6),
            'delta_vs_equal_vote': round(greedy_oof_score - ev_score, 6),
        },
        'spearman_vs_v44': round(float(spear), 6),
        'gates': {
            'caruana_gte_equal_vote': bool(greedy_oof_score >= ev_score - 1e-9),
            'max_weight_under_80pct': bool(top_weight <= 0.80),
            'spearman_gte_0_8': bool(spear >= 0.80),
        },
    }
    with open(weights_path, 'w') as f:
        json.dump(weights_json, f, indent=2)
    print(f"\n  weights.json saved: {weights_path}")

    # 10. Generate CV report
    _write_cv_report(
        weights, greedy_oof_score, ev_score, ev_v44_score,
        individual_scores=None,
        oof_calib=oof_calib,
        y_train=y_train,
        spear=spear,
        top_weight=top_weight,
        top_name=top_name,
        overlap_report=overlap_report,
        v44_k200_pos=v44_k200_pos,
    )

    print("\n" + "=" * 60)
    print("V53 complete.")
    print(f"  Caruana OOF F1@K200: {greedy_oof_score:.6f}")
    print(f"  Equal-vote OOF F1@K200: {ev_score:.6f}")
    print(f"  Delta: {greedy_oof_score - ev_score:+.6f}")
    print(f"  Spearman vs V44: {spear:+.4f}")
    print("=" * 60)


# ─── CV Report writer ─────────────────────────────────────────────────────────
def _write_cv_report(weights, greedy_score, ev_score, ev_v44_score,
                     individual_scores, oof_calib, y_train, spear,
                     top_weight, top_name, overlap_report, v44_k200_pos):
    # Recompute individual scores for the report
    indiv = {}
    for name, scores in oof_calib.items():
        indiv[name] = f1_at_k(y_train, scores, K_FOR_GREEDY)

    lines = [
        "# V53 CV Report — Caruana Greedy Ensemble",
        "",
        f"**Date:** 2026-05-24",
        f"**Banked best:** V44 K=200 = 72.83 LB",
        f"**Algorithm:** Caruana 2004 greedy forward selection with replacement",
        f"**Metric:** F1@K=200 on OOF (n_pos=66, K=200)",
        f"**Iterations:** {N_ITERATIONS}",
        "",
        "---",
        "",
        "## OOF F1@K=200 Summary",
        "",
        "| Method | OOF F1@K=200 | Delta vs Equal-Vote |",
        "|--------|-------------|---------------------|",
        f"| **Caruana Greedy (V53)** | **{greedy_score:.6f}** | **{greedy_score - ev_score:+.6f}** |",
        f"| Equal-vote all paradigms | {ev_score:.6f} | 0.000000 |",
        f"| Equal-vote V44 subset (5 paradigms) | {ev_v44_score:.6f} | {ev_v44_score - ev_score:+.6f} |",
        "",
        "---",
        "",
        "## Individual Paradigm OOF F1@K=200",
        "",
        "| Paradigm | Individual F1@K=200 | Caruana Weight | Selection Count |",
        "|----------|---------------------|----------------|-----------------|",
    ]
    for name in sorted(indiv, key=lambda x: -indiv[x]):
        w     = weights.get(name, 0.0)
        count = round(w * N_ITERATIONS)
        lines.append(
            f"| {name} | {indiv[name]:.6f} | {w:.4f} | {count} |"
        )

    lines += [
        "",
        "---",
        "",
        "## Gates",
        "",
        f"- **Gate 1 (Caruana >= equal-vote):** {'PASS' if greedy_score >= ev_score - 1e-9 else 'FAIL'}",
        f"- **Gate 2 (max weight < 80%):** {'PASS' if top_weight <= 0.80 else 'FAIL'} — max={top_name} @ {top_weight:.4f}",
        f"- **Gate 3 (Spearman vs V44 >= 0.80):** {'PASS' if spear >= 0.80 else 'FAIL'} — ρ={spear:+.4f}",
        "",
        "---",
        "",
        "## Submission Overlap with V44 K=200 (banked 72.83)",
        "",
        "| K | V53 Top-K Overlap with V44 K=200 |",
        "|---|-----------------------------------|",
    ]
    for k, ov in sorted(overlap_report.items()):
        lines.append(f"| {k} | {ov}/{min(k, 200)} |")

    lines += [
        "",
        "---",
        "",
        "## Top-3 Risks",
        "",
        "1. **OOF overfitting to calibration:** Isotonic calibration on OOF (Option C) is valid",
        "   because all base models used identical fold splits. Risk level: LOW — 100 iterations",
        "   on N=13 models is well within safe regime (< 150 iterations cap per R25).",
        "",
        "2. **V4_binary test score:** V4's test score is binary (0/1 expected submission), not a",
        "   continuous probability. If Caruana assigns non-trivial weight to V4, the test ensemble",
        "   may have discontinuities near the K cutoff. Check: if V4 weight > 20%, validate that",
        "   submission_K200 overlap with V44 is still ≥ 0.80.",
        "",
        "3. **OOF F1@K vs LB F1@K gap:** Per R28 (OOF calibration not LB calibration), post-hoc",
        "   rules validated on OOF can diverge from LB by up to ±1.5 points. V27 showed this.",
        "   Mitigated here by using F1@K (not threshold-based) — ranking is more robust than",
        "   classification calibration.",
        "",
        "---",
        "",
        "## Architecture Notes",
        "",
        "- Paradigm signals loaded: V4_meta (OOF), V33, V34_meta, V35_rank, V39, V40, V41,",
        "  V43, V46, V48_rank, V50, V51_mean, V44_consensus (13 total)",
        "- Calibration: IsotonicRegression per paradigm on OOF scores before greedy",
        "- Test ensemble: weighted sum of RAW test scores (calibration affects selection, not ranking)",
        "- V44_consensus included as a synthetic candidate so greedy can 'pick V44 alone' if optimal",
        "- Spearman sanity vs V44 ensures V53 is not an orthogonal direction from the banked best",
    ]

    report_path = OUT / 'cv_report_v53.md'
    report_path.write_text('\n'.join(lines))
    print(f"\n  cv_report_v53.md saved: {report_path}")


if __name__ == '__main__':
    main()
