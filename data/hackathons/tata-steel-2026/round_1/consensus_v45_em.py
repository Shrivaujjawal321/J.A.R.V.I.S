#!/usr/bin/env python3
"""
V45 — EM label-shift recalibration on V44 paradigm-averaged probabilities.

Per Saerens / Alexandari ICML 2020. Post-hoc, no retraining.
1. Average paradigm OOF probas → "consensus probability"
2. Isotonic-calibrate OOF on train labels
3. Apply same calibrator to test
4. EM iteration to estimate test prevalence q_est from test probas
5. Rescale test probabilities with prior-ratio formula
6. Sort by rescaled, take top-K
"""
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.isotonic import IsotonicRegression

ROOT = Path('/home/ujjwal/Documents/J.A.R.V.I.S./data/hackathons/tata-steel-2026/round_1')

# ===========================================================================
# Load OOF + test probas from all paradigms
# ===========================================================================
oof_v4 = pd.read_parquet(ROOT/'build_v4/oof_v4.parquet')
y_train = oof_v4['Y'].values
p_train = y_train.mean()
print(f"Train prevalence p = {p_train:.4f}")

# OOF probas
oof_sources = {
    'v4': (ROOT/'build_v4/oof_v4.parquet', 'oof_meta'),
    'v33': (ROOT/'build_v33/oof_v33.parquet', 'oof_proba'),
    'v34': (ROOT/'build_v34/oof_v34.parquet', 'oof_meta'),
    'v35': (ROOT/'build_v35/oof_v35.parquet', 'rank_avg_proba'),
    'v39': (ROOT/'build_v39/oof_v39.parquet', 'oof_proba'),
    'v40': (ROOT/'build_v40/oof_v40.parquet', 'oof_proba'),
    'v41': (ROOT/'build_v41/oof_v41.parquet', 'oof_proba'),
}

# Need to align all OOFs by CoilID. V4 oof doesn't have CoilID — use train_v4 row order.
train_v4 = pd.read_parquet(ROOT/'build_v4/train_v4.parquet')
train_coil_order = train_v4['CoilID'].tolist()
n_train = len(train_coil_order)
assert n_train == len(y_train)

oof_df = pd.DataFrame({'CoilID': train_coil_order, 'y': y_train, 'v4': oof_v4['oof_meta'].values})
for name, (path, col) in oof_sources.items():
    if name == 'v4': continue
    d = pd.read_parquet(path)
    if 'CoilID' in d.columns:
        oof_df = oof_df.merge(d[['CoilID', col]].rename(columns={col: name}), on='CoilID', how='left')
    else:
        # row-aligned
        if len(d) == n_train:
            oof_df[name] = d[col].values

# V35 rank_avg_proba is 0-339-scale, not 0-1. Normalize:
if oof_df['v35'].max() > 1.5:
    oof_df['v35'] = oof_df['v35'] / oof_df['v35'].max()

# Drop NaN
before = len(oof_df)
oof_df = oof_df.dropna()
print(f"OOF aligned: {len(oof_df)} of {before} rows")

paradigms = ['v4','v33','v34','v35','v39','v40','v41']

# Rank-normalize each paradigm OOF to [0,1] then average (handles scale differences)
oof_ranks = pd.DataFrame()
for p in paradigms:
    oof_ranks[p] = oof_df[p].rank(pct=True)
oof_mean_rank = oof_ranks.mean(axis=1).values

# ===========================================================================
# Test probas — same paradigms
# ===========================================================================
test_v4_df = pd.read_parquet(ROOT/'build_v4/test_v4.parquet')
coil_order = test_v4_df['CoilID'].tolist()
N = len(coil_order)

v4_test_meta = pd.read_parquet(ROOT/'build_v4/test_meta_v4.parquet')
test_df = pd.DataFrame({'CoilID': coil_order, 'v4': v4_test_meta['test_meta'].values})

for name, src in [('v33','build_v33/test_proba_v33.parquet'),
                  ('v34','build_v34/test_proba_v34.parquet'),
                  ('v35','build_v35/test_proba_v35.parquet'),
                  ('v39','build_v39/test_proba_v39.parquet'),
                  ('v40','build_v40/test_proba_v40.parquet'),
                  ('v41','build_v41/test_proba_v41.parquet')]:
    d = pd.read_parquet(ROOT/src)
    col = 'rank_avg_proba' if 'rank_avg_proba' in d.columns else 'test_proba'
    test_df = test_df.merge(d[['CoilID', col]].rename(columns={col: name}), on='CoilID')

# Normalize v35 in test
if test_df['v35'].max() > 1.5:
    test_df['v35'] = test_df['v35'] / test_df['v35'].max()

# Rank-normalize each paradigm test proba to [0,1] then average
test_ranks = pd.DataFrame()
for p in paradigms:
    test_ranks[p] = test_df[p].rank(pct=True)
test_mean_rank = test_ranks.mean(axis=1).values

# ===========================================================================
# Calibrate OOF mean-rank to probabilities via Isotonic on (oof_mean_rank, y)
# ===========================================================================
y_train_aligned = oof_df['y'].values  # length = len(oof_df)
iso = IsotonicRegression(out_of_bounds='clip', y_min=1e-6, y_max=1-1e-6)
iso.fit(oof_mean_rank, y_train_aligned)
calibrated_oof = iso.predict(oof_mean_rank)
calibrated_test = iso.predict(test_mean_rank)

print(f"Calibrated OOF: range [{calibrated_oof.min():.4f}, {calibrated_oof.max():.4f}], mean {calibrated_oof.mean():.4f}")
print(f"Calibrated test: range [{calibrated_test.min():.4f}, {calibrated_test.max():.4f}], mean {calibrated_test.mean():.4f}")

# ===========================================================================
# EM iteration to estimate test prevalence q_est
# ===========================================================================
def em_label_shift(test_preds, p_train, max_iter=1000, tol=1e-8):
    q_est = float(np.mean(test_preds))
    history = [q_est]
    for it in range(max_iter):
        q_old = q_est
        ratio = (q_est / p_train) / ((1 - q_est) / (1 - p_train))
        corrected = ratio * test_preds / (ratio * test_preds + (1 - test_preds) + 1e-12)
        q_est = float(np.mean(corrected))
        history.append(q_est)
        if abs(q_est - q_old) < tol:
            break
    return corrected, q_est, history

corrected_test, q_est, history = em_label_shift(calibrated_test, p_train)
print(f"\nEM converged: q_est = {q_est:.4f} (estimated test prevalence)")
print(f"Iteration history (first 10): {history[:10]}")
print(f"Corrected test probas: range [{corrected_test.min():.4g}, {corrected_test.max():.4g}], mean {corrected_test.mean():.4f}")

# ===========================================================================
# Compare ranking with vs without EM
# ===========================================================================
test_df['calibrated'] = calibrated_test
test_df['em_corrected'] = corrected_test

# Top-K from EM-corrected
ranking_em = np.argsort(-corrected_test)  # descending
ranking_uncal = np.argsort(-calibrated_test)

# Compare top-200 overlap
top200_em = set([coil_order[i] for i in ranking_em[:200]])
top200_uncal = set([coil_order[i] for i in ranking_uncal[:200]])
print(f"\nTop-200 EM vs uncalibrated overlap: {len(top200_em & top200_uncal)} of 200")

# V44 K=200 banked submission for comparison
v44 = pd.read_csv(ROOT/'consensus_v44/submission_K200.csv')
v44_pos = set(v44[v44.Y==1].CoilID.tolist())
print(f"V45 EM top-200 vs V44 K=200 (72.83 banked) overlap: {len(top200_em & v44_pos)} of 200")

# ===========================================================================
# Generate V45 K-sweep submissions
# ===========================================================================
out_dir = ROOT / 'consensus_v45'
out_dir.mkdir(exist_ok=True)

K_OPTIONS = [138, 154, 170, 181, 190, 195, 197, 200, 205, 212, 220]
for K in K_OPTIONS:
    if K <= 0 or K >= N: continue
    selected_coils = [coil_order[i] for i in ranking_em[:K]]
    sub = pd.DataFrame({'CoilID': coil_order})
    sub['Y'] = sub['CoilID'].isin(selected_coils).astype(int)
    sub.to_csv(out_dir/f'submission_K{K}.csv', index=False)
    diff_v44 = len(set(selected_coils).symmetric_difference(v44_pos)) if K == 200 else 'N/A'
    print(f"  K={K:3d}: saved, V44_K200_diff={diff_v44}")

print(f"\nSaved {len(K_OPTIONS)} V45 submissions to {out_dir}/")
print(f"Best fire candidate: K=200 (matches V44 K=200 baseline)")
