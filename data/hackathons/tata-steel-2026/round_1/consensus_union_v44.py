#!/usr/bin/env python3
"""
V44 — Consensus Union with V43 rank-product paradigm added (6 paradigms total).
"""
import pandas as pd
import numpy as np
from pathlib import Path
from scipy.stats import spearmanr

ROOT = Path('/home/ujjwal/Documents/J.A.R.V.I.S./data/hackathons/tata-steel-2026/round_1')

test_v4 = pd.read_parquet(ROOT/'build_v4/test_v4.parquet')
coil_order = test_v4['CoilID'].tolist(); N = len(coil_order)

df = pd.DataFrame({'CoilID': coil_order})
df = df.merge(pd.read_parquet(ROOT/'build_v35/test_proba_v35.parquet')[['CoilID','rank_avg_proba']].rename(columns={'rank_avg_proba':'v35'}), on='CoilID')
df = df.merge(pd.read_parquet(ROOT/'build_v39/test_proba_v39.parquet')[['CoilID','test_proba']].rename(columns={'test_proba':'v39'}), on='CoilID')
df = df.merge(pd.read_parquet(ROOT/'build_v40/test_proba_v40.parquet')[['CoilID','test_proba']].rename(columns={'test_proba':'v40'}), on='CoilID')
df = df.merge(pd.read_parquet(ROOT/'build_v41/test_proba_v41.parquet')[['CoilID','test_proba']].rename(columns={'test_proba':'v41'}), on='CoilID')

# Add V43
v43_df = pd.read_parquet(ROOT/'build_v43/test_proba_v43.parquet')
print(f'V43 test schema: {list(v43_df.columns)}, shape: {v43_df.shape}')
# Find the right proba column
v43_proba_col = None
for c in ['test_proba', 'rank_product', 'oof_proba', 'proba']:
    if c in v43_df.columns:
        v43_proba_col = c; break
if v43_proba_col is None:
    v43_proba_col = [c for c in v43_df.columns if c != 'CoilID'][0]
print(f'V43 using column: {v43_proba_col}')
df = df.merge(v43_df[['CoilID', v43_proba_col]].rename(columns={v43_proba_col:'v43'}), on='CoilID')

paradigms = ['v35','v39','v40','v41','v43']
print(f'Loaded {N} test rows, {len(paradigms)} paradigms: {paradigms}\n')

print('Pairwise Spearman (test):')
for i in range(len(paradigms)):
    for j in range(i+1, len(paradigms)):
        s, _ = spearmanr(df[paradigms[i]], df[paradigms[j]])
        print(f'  {paradigms[i]} <-> {paradigms[j]}: ρ={s:+.4f}')
print()

K_ANCHOR = 181
paradigm_topK = {p: set(df.sort_values(p, ascending=False)['CoilID'].tolist()[:K_ANCHOR]) for p in paradigms}
v4_sub = pd.read_csv(ROOT/'build_v4/expected_submission.csv')
v4_154_coils = set(v4_sub[v4_sub['Y']==1]['CoilID'].tolist())

vote = pd.Series(0, index=df['CoilID'])
for p in paradigms: vote.loc[list(paradigm_topK[p])] += 1
vote.loc[list(v4_154_coils & set(coil_order))] += 1

rank_pct = pd.DataFrame(index=df['CoilID'])
for p in paradigms: rank_pct[p] = df.set_index('CoilID')[p].rank(pct=True)
rank_pct_mean = rank_pct.mean(axis=1)

consensus = pd.DataFrame({
    'CoilID': vote.index,
    'vote': vote.values,
    'rank_pct_mean': rank_pct_mean.loc[vote.index].values,
})
consensus = consensus.sort_values(['vote','rank_pct_mean'], ascending=[False,False]).reset_index(drop=True)

print('Vote distribution (max=6 = 5 paradigms + V4_154):')
print(consensus['vote'].value_counts().sort_index(ascending=False).to_string())
print()

out_dir = ROOT / 'consensus_v44'
out_dir.mkdir(exist_ok=True)

K_OPTIONS = [138, 150, 154, 164, 170, 181, 186, 190, 193, 195, 197, 200, 205, 212, 220]
print('K-sweep:')
for K in K_OPTIONS:
    if K <= 0 or K >= N: continue
    sub = consensus.head(K)[['CoilID']].copy(); sub['Y']=1
    neg = [c for c in coil_order if c not in set(sub['CoilID'])]
    full = pd.concat([sub, pd.DataFrame({'CoilID':neg,'Y':[0]*len(neg)})], ignore_index=True).set_index('CoilID').loc[coil_order].reset_index()[['CoilID','Y']]
    full.to_csv(out_dir/f'submission_K{K}.csv', index=False)
    vote_dist = consensus.head(K)['vote'].value_counts().sort_index(ascending=False).to_dict()
    print(f'  K={K:3d}: votes={vote_dist}')

# Diff vs V42 K=197 (banked best 71.70)
v42 = pd.read_csv(ROOT/'consensus_v42/submission_K197.csv')
v42_pos = set(v42[v42.Y==1].CoilID)
print()
print('V44 vs V42 K=197 (71.70 baseline):')
for K in [186, 190, 197, 200]:
    v44 = pd.read_csv(out_dir/f'submission_K{K}.csv')
    v44_pos = set(v44[v44.Y==1].CoilID)
    diff = len(v42_pos.symmetric_difference(v44_pos))
    overlap = len(v42_pos & v44_pos)
    new = len(v44_pos - v42_pos)
    drop = len(v42_pos - v44_pos)
    print(f'  K={K}: overlap={overlap}, V44-new={new}, V42-only={drop}, sym-diff={diff}')

# V43 standalone top-K (just rank by V43 proba)
print()
print('V43-standalone top-K (rank by V43 alone, no consensus):')
v43_only = pd.DataFrame({'CoilID': df['CoilID'], 'v43_score': df['v43']})
v43_only = v43_only.sort_values('v43_score', ascending=False).reset_index(drop=True)
for K in [154, 170, 186, 197]:
    sub = v43_only.head(K)[['CoilID']].copy(); sub['Y']=1
    neg = [c for c in coil_order if c not in set(sub['CoilID'])]
    full = pd.concat([sub, pd.DataFrame({'CoilID':neg,'Y':[0]*len(neg)})], ignore_index=True).set_index('CoilID').loc[coil_order].reset_index()[['CoilID','Y']]
    full.to_csv(out_dir/f'submission_K{K}_v43solo.csv', index=False)
    v43_only_pos = set(full[full.Y==1].CoilID)
    overlap_v42 = len(v43_only_pos & v42_pos)
    print(f'  K={K}: V43-standalone, overlap with V42-K197={overlap_v42}/{K}')
