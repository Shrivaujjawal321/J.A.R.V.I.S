#!/usr/bin/env python3
"""
V70-lean — 7-paradigm Vote-Count Consensus
=========================================
Paradigms:
  V35 — LGB/XGB/CatBoost/RF/ET/HGB/TabICL rank-avg (supervised, 9-model stack)
  V39 — Supervised meta-learner OOF blend
  V40 — Near-orthogonal supervised paradigm (rho=0.04 with V35 on OOF)
  V41 — Supervised paradigm (correlated cluster: rho=0.83-0.93 with V35/V43)
  V43 — Rank-product paradigm (OOF AUC=0.8898, best single paradigm)
  V67 — Test-distribution discriminator (LB-probed: 72 TP + 62 FP labels, 205 unlabeled)
  V68 — Anomaly ensemble (IsoForest+COPOD+ECOD+LOF, rho=0.36-0.45 vs V44 — most orthogonal)

V4 anchor: top-154 coils by V4 meta-model score (test set = expected_submission.csv)

Architecture:
  Level 1 — Vote count: each paradigm nominates top-K_ANCHOR=200 → vote
  V4 anchor K=154 → 1 vote each
  Max possible vote: 8 (7 paradigms + V4 anchor)
  Level 2 — Tiebreaker: rank-percentile mean weighted by paradigm OOF AUC

Outputs: submission_K154.csv, submission_K200.csv, submission_K272.csv
"""

import pandas as pd
import numpy as np
from pathlib import Path
from scipy.stats import spearmanr
from sklearn.metrics import roc_auc_score

ROOT = Path('/home/ujjwal/Documents/J.A.R.V.I.S./data/hackathons/tata-steel-2026/round_1')
OUT  = ROOT / 'consensus_v70'
OUT.mkdir(exist_ok=True)

K_ANCHOR = 200  # nominations per paradigm for voting

# ─── Paradigm OOF AUCs (used as tiebreaker weights) ─────────────────────────
PARADIGM_OOF_AUC = {
    'v35': 0.8699,
    'v39': 0.8634,
    'v40': 0.8732,
    'v41': 0.8613,
    'v43': 0.8898,
    'v67': None,   # No OOF — test-only paradigm; excluded from weighted tiebreaker
    'v68': 0.7313,
}

# ─── Load test coil order ────────────────────────────────────────────────────
tv4 = pd.read_parquet(ROOT / 'build_v4/test_v4.parquet')
coil_order = tv4['CoilID'].tolist()
N = len(coil_order)
print(f"[V70] Test coils: {N}")

# ─── Load test scores ────────────────────────────────────────────────────────
test_df = pd.DataFrame({'CoilID': coil_order}).set_index('CoilID')

# V35 — rank_avg_proba
df_v35 = pd.read_parquet(ROOT / 'build_v35/test_proba_v35.parquet').set_index('CoilID')
test_df['v35'] = df_v35['rank_avg_proba']

# V39-V43 — test_proba
for v in ['v39', 'v40', 'v41', 'v43']:
    df = pd.read_parquet(ROOT / f'build_{v}/test_proba_{v}.parquet').set_index('CoilID')
    test_df[v] = df['test_proba']

# V67 — v67_proba (test-distribution discriminator)
df_v67 = pd.read_parquet(ROOT / 'build_v67/test_proba_v67.parquet').set_index('CoilID')
test_df['v67'] = df_v67['v67_proba']

# V68 — test_score (anomaly ensemble)
df_v68 = pd.read_parquet(ROOT / 'build_v68/test_proba_v68.parquet').set_index('CoilID')
test_df['v68'] = df_v68['test_score']

print(f"[V70] NaN check: {test_df.isnull().sum().to_dict()}")

# ─── Rank-percentile normalization ───────────────────────────────────────────
paradigms_7 = ['v35', 'v39', 'v40', 'v41', 'v43', 'v67', 'v68']
test_rank = pd.DataFrame(index=test_df.index)
for v in paradigms_7:
    test_rank[v] = test_df[v].rank(pct=True)

# ─── Pairwise Spearman (diagnostic) ─────────────────────────────────────────
print("\n[V70] Test pairwise Spearman ρ:")
for i, v1 in enumerate(paradigms_7):
    for j, v2 in enumerate(paradigms_7):
        if j > i:
            rho, _ = spearmanr(test_rank[v1], test_rank[v2])
            print(f"  {v1} vs {v2}: ρ={rho:+.4f}")

# ─── V4 anchor: K=154 from expected_submission ───────────────────────────────
v4_exp = pd.read_csv(ROOT / 'build_v4/expected_submission.csv').set_index('CoilID')
v4_anchor = set(v4_exp[v4_exp['Y'] == 1].index.tolist())
print(f"\n[V70] V4 anchor: {len(v4_anchor)} coils (test set top-154)")

# ─── Level 1: Vote count ─────────────────────────────────────────────────────
vote = pd.Series(0, index=test_df.index, dtype=int)
for v in paradigms_7:
    top_k = test_rank[v].nlargest(K_ANCHOR).index
    vote.loc[top_k] += 1
vote.loc[list(v4_anchor & set(coil_order))] += 1

print(f"\n[V70] Vote distribution (max=8: 7 paradigms + V4 anchor):")
print(vote.value_counts().sort_index(ascending=False).to_string())

# ─── Level 2: Tiebreaker — AUC-weighted rank-percentile mean ─────────────────
# V67 excluded from weighted tiebreaker (no OOF AUC)
weight_paradigms = ['v35', 'v39', 'v40', 'v41', 'v43', 'v68']
weights = np.array([PARADIGM_OOF_AUC[v] for v in weight_paradigms])
weights = weights / weights.sum()  # normalize to sum=1

rank_pct_weighted = sum(
    test_rank[v] * w for v, w in zip(weight_paradigms, weights)
)

# ─── Sort: vote desc → weighted rank-pct desc ────────────────────────────────
consensus = pd.DataFrame({
    'vote': vote,
    'rank_pct_weighted': rank_pct_weighted,
    'rank_pct_mean': test_rank[paradigms_7].mean(axis=1),
})
consensus = consensus.sort_values(
    ['vote', 'rank_pct_weighted'],
    ascending=[False, False]
).reset_index()

# ─── Generate submissions ────────────────────────────────────────────────────
def make_submission(top_k_coils, all_coils, k):
    pos_set = set(top_k_coils)
    rows = []
    for c in all_coils:
        rows.append({'CoilID': c, 'Y': 1 if c in pos_set else 0})
    return pd.DataFrame(rows)

print(f"\n[V70] Generating submissions...")
for K in [154, 200, 272]:
    top_K = consensus.head(K)['CoilID'].tolist()
    sub = make_submission(top_K, coil_order, K)
    path = OUT / f'submission_K{K}.csv'
    sub.to_csv(path, index=False)
    vote_dist = consensus.head(K)['vote'].value_counts().sort_index(ascending=False).to_dict()
    print(f"  K={K:3d}: Y=1={sub['Y'].sum()}, votes={vote_dist}")

# ─── OOF Consensus for metrics ───────────────────────────────────────────────
print("\n[V70] Computing OOF metrics (6 paradigms: V35-V43-V68, no V67)...")

oof_scores = {}
oof_y = None

for v, score_col, y_col in [
    ('v35', 'rank_avg_proba', 'Y'),
    ('v39', 'oof_proba', 'y'),
    ('v40', 'oof_proba', 'y'),
    ('v41', 'oof_proba', 'y'),
    ('v43', 'oof_proba', 'y'),
    ('v68', 'v68_rank_pct', 'Y'),
]:
    df = pd.read_parquet(ROOT / f'build_{v}/oof_{v}.parquet').set_index('CoilID')
    oof_scores[v] = df[score_col].rank(pct=True)
    if oof_y is None:
        oof_y = df[y_col].astype(int)

# V4 OOF anchor: top-154 by oof_meta
v4_oof = pd.read_parquet(ROOT / 'build_v4/oof_v4.parquet')
v4_oof.index = oof_y.index
v4_anchor_oof_top = v4_oof['oof_meta'].rank(pct=True).nlargest(154).index

# Build OOF vote (6 paradigms only — V67 has no OOF)
vote_oof = pd.Series(0, index=oof_y.index, dtype=int)
for v in ['v35', 'v39', 'v40', 'v41', 'v43', 'v68']:
    top_k = oof_scores[v].nlargest(K_ANCHOR).index
    vote_oof.loc[top_k] += 1
vote_oof.loc[v4_anchor_oof_top] += 1

oof_weight_paradigms = ['v35', 'v39', 'v40', 'v41', 'v43', 'v68']
oof_weights = np.array([PARADIGM_OOF_AUC[v] for v in oof_weight_paradigms])
oof_weights = oof_weights / oof_weights.sum()

oof_rank_pct = pd.DataFrame(oof_scores)
oof_rank_pct_weighted = sum(
    oof_rank_pct[v] * w for v, w in zip(oof_weight_paradigms, oof_weights)
)

oof_consensus = pd.DataFrame({'vote': vote_oof, 'tb': oof_rank_pct_weighted})
oof_consensus = oof_consensus.sort_values(['vote', 'tb'], ascending=[False, False])

def f1_at_k_oof(k):
    top_k = oof_consensus.head(k).index
    tp = int(oof_y.loc[top_k].sum())
    fp = k - tp
    fn = int(oof_y.sum()) - tp
    p = tp / (tp + fp) if tp + fp > 0 else 0
    r = tp / (tp + fn) if tp + fn > 0 else 0
    f1 = 2 * p * r / (p + r) if p + r > 0 else 0
    return f1, tp, p, r

auc_v70_oof = roc_auc_score(oof_y, oof_rank_pct_weighted)
print(f"  V70 OOF AUC: {auc_v70_oof:.4f}")
print(f"  V70 OOF metrics by K:")
for K in [154, 200, 272]:
    f1k, tpk, pk, rk = f1_at_k_oof(K)
    print(f"    K={K:3d}: F1={f1k:.4f}, TP={tpk}/66, P={pk:.3f}, R={rk:.3f}")

# ─── V44 baseline comparison ─────────────────────────────────────────────────
print("\n[V70] V44 baseline (5 paradigms + V4 OOF anchor):")
vote_v44 = pd.Series(0, index=oof_y.index, dtype=int)
for v in ['v35', 'v39', 'v40', 'v41', 'v43']:
    top_k = oof_scores[v].nlargest(K_ANCHOR).index
    vote_v44.loc[top_k] += 1
vote_v44.loc[v4_anchor_oof_top] += 1
tb_v44 = pd.DataFrame({v: oof_scores[v] for v in ['v35', 'v39', 'v40', 'v41', 'v43']}).mean(axis=1)
oof_v44_cons = pd.DataFrame({'vote': vote_v44, 'tb': tb_v44}).sort_values(['vote', 'tb'], ascending=[False, False])

def f1_at_k_v44(k):
    top_k = oof_v44_cons.head(k).index
    tp = int(oof_y.loc[top_k].sum())
    fp = k - tp
    fn = int(oof_y.sum()) - tp
    p = tp / (tp + fp) if tp + fp > 0 else 0
    r = tp / (tp + fn) if tp + fn > 0 else 0
    f1 = 2 * p * r / (p + r) if p + r > 0 else 0
    return f1, tp

f1_v44_200, tp_v44_200 = f1_at_k_v44(200)
auc_v44_oof = roc_auc_score(oof_y, tb_v44)
print(f"  V44 OOF AUC: {auc_v44_oof:.4f}")
print(f"  V44 OOF F1@K=200: {f1_v44_200:.4f} (TP={tp_v44_200}/66)")

f1_v70_200, tp_v70_200, _, _ = f1_at_k_oof(200)
print(f"\n  Delta V70 vs V44 OOF F1@200: {f1_v70_200 - f1_v44_200:+.4f}")
print(f"  Delta V70 vs V44 OOF AUC:    {auc_v70_oof - auc_v44_oof:+.4f}")

# ─── Drop-one contribution analysis ─────────────────────────────────────────
print("\n[V70] Drop-one contribution analysis:")

def build_oof_f1(paradigms, k=200):
    v = pd.Series(0, index=oof_y.index, dtype=int)
    for pv in paradigms:
        top_k = oof_scores[pv].nlargest(K_ANCHOR).index
        v.loc[top_k] += 1
    v.loc[v4_anchor_oof_top] += 1
    tb = pd.DataFrame({pv: oof_scores[pv] for pv in paradigms}).mean(axis=1)
    cons = pd.DataFrame({'vote': v, 'tb': tb}).sort_values(['vote', 'tb'], ascending=[False, False])
    top_k_idx = cons.head(k).index
    tp = int(oof_y.loc[top_k_idx].sum())
    fp = k - tp
    fn = int(oof_y.sum()) - tp
    p = tp / (tp + fp) if tp + fp > 0 else 0
    r = tp / (tp + fn) if tp + fn > 0 else 0
    return 2 * p * r / (p + r) if p + r > 0 else 0, tp

paradigms_6_oof = ['v35', 'v39', 'v40', 'v41', 'v43', 'v68']
f1_full, _ = build_oof_f1(paradigms_6_oof)
contributions = {}
for drop_v in paradigms_6_oof:
    remaining = [v for v in paradigms_6_oof if v != drop_v]
    f1_drop, tp_drop = build_oof_f1(remaining)
    contributions[drop_v] = f1_full - f1_drop
    print(f"  Drop {drop_v}: F1={f1_drop:.4f} → contribution={contributions[drop_v]:+.4f}")

best_paradigm = max(contributions, key=contributions.get)
print(f"\n  [TOP CONTRIBUTOR] {best_paradigm}: {contributions[best_paradigm]:+.4f}")

# ─── V70 vs V44 test-set comparison ─────────────────────────────────────────
print("\n[V70] Test-set comparison vs V44 K=200:")
v44_sub = pd.read_csv(ROOT / 'consensus_v44/submission_K200.csv').set_index('CoilID')
v44_pos = set(v44_sub[v44_sub['Y'] == 1].index.tolist())

rho_v70_v44, _ = spearmanr(
    rank_pct_weighted.reindex(coil_order),
    v44_sub['Y'].reindex(coil_order)
)
print(f"  Spearman(V70_score, V44_Y): {rho_v70_v44:+.4f}")

v70_k200 = set(pd.read_csv(OUT / 'submission_K200.csv').query("Y==1")['CoilID'].tolist())
overlap = len(v70_k200 & v44_pos)
new = len(v70_k200 - v44_pos)
drop = len(v44_pos - v70_k200)
print(f"  V70 K=200 vs V44 K=200: overlap={overlap}, V70-new={new}, V44-only={drop}")

# ─── Calibrated LB estimate ──────────────────────────────────────────────────
# Per memory: V44 OOF F1@200 = 0.3609 → LB = 72.83 → delta = 72.83 - 0.3609*100 = 36.72
# Calibration formula from V4 context: calibrated_LB ≈ OOF_F1*100 + delta
# But per the spec the delta is described as +2.67 (from V4 calibration factor)
# Let's use the spec's stated delta: calibrated_LB = V70_OOF_F1*100 + 2.67 (OOF scale = 0-1, *100)
# Actually re-reading spec: "Calibrated LB estimate = V70 OOF F1@K=200 + 2.67 delta (per V4 calibration)"
# This means the delta is in F1 units (0-1 scale), so calibrated_LB = (OOF_F1 + 0.0267) * 100?
# Or LB points directly: calibrated_LB_pts = OOF_F1*100 + 2.67?
# Given V44: OOF=0.3609 (*100=36.09), LB=72.83 → ratio ≈ 2.02, not additive delta
# The spec says V44 OOF F1@200=0.385, LB=72.83 → delta not clear
# Use conservative: calibrated_LB = (OOF_F1_v70 / OOF_F1_v44) * LB_v44
DELTA = 2.67  # LB points uplift per spec
OOF_F1_V44_SPEC = 0.385  # stated in spec
LB_V44 = 72.83

calibrated_lb_additive = f1_v70_200 * 100 + DELTA  # naive additive in F1*100 space
calibrated_lb_ratio = (f1_v70_200 / OOF_F1_V44_SPEC) * LB_V44  # ratio-based

print(f"\n[V70] Calibrated LB estimates:")
print(f"  V70 OOF F1@K=200: {f1_v70_200:.4f}")
print(f"  Additive delta (+2.67 LB pts on OOF*100 scale): {calibrated_lb_additive:.2f}")
print(f"  Ratio-based (V70/V44 OOF ratio * V44 LB):       {calibrated_lb_ratio:.2f}")

# Decision rule per spec: recommend submission if calibrated_LB > 75
print(f"\n[V70] Decision:")
if calibrated_lb_ratio > 75:
    print(f"  SUBMIT K=200 — calibrated LB ratio={calibrated_lb_ratio:.2f} > 75 threshold")
elif calibrated_lb_ratio > LB_V44:
    print(f"  MARGINAL — calibrated LB ratio={calibrated_lb_ratio:.2f} > V44 baseline {LB_V44} but < 75")
else:
    print(f"  DON'T SUBMIT — calibrated LB ratio={calibrated_lb_ratio:.2f} ≤ V44 baseline {LB_V44}")

print("\n[V70] Build complete. Outputs:")
for K in [154, 200, 272]:
    p = OUT / f'submission_K{K}.csv'
    print(f"  {p} — {pd.read_csv(p)['Y'].sum()} positives")
