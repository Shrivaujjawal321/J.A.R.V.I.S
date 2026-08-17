#!/usr/bin/env python3
"""
V42 — Consensus Union mirroring Ratnesh-Jarvis's exact 4-paradigm + V4_154 anchor structure.

Paradigms (matching Ratnesh's v32/iter35/iter36/iter37):
- V35 = 9-model rank-avg base (closest to Ratnesh's v32)
- V39 = iter35-equivalent (CoilID + sin/cos cyclic features)
- V40 = iter36-equivalent (defect-proximity, MAXIMALLY ORTHOGONAL)
- V41 = iter37-equivalent (BBSE-reweighted V4 base)
- V4_154 anchor (banked LB-validated picks)

Vote count per coil, max = 5. K-sweep on consensus ordering.
"""
import pandas as pd
import numpy as np
from pathlib import Path
from scipy.stats import spearmanr

ROOT = Path("/home/ujjwal/Documents/J.A.R.V.I.S./data/hackathons/tata-steel-2026/round_1")

test_v4 = pd.read_parquet(ROOT/"build_v4/test_v4.parquet")
coil_order = test_v4["CoilID"].tolist()
N = len(coil_order)

# Load 4 paradigms (V35 + V39 + V40 + V41)
df = pd.DataFrame({"CoilID": coil_order})
df = df.merge(pd.read_parquet(ROOT/"build_v35/test_proba_v35.parquet")[["CoilID","rank_avg_proba"]].rename(columns={"rank_avg_proba":"v35"}), on="CoilID")
df = df.merge(pd.read_parquet(ROOT/"build_v39/test_proba_v39.parquet")[["CoilID","test_proba"]].rename(columns={"test_proba":"v39"}), on="CoilID")
df = df.merge(pd.read_parquet(ROOT/"build_v40/test_proba_v40.parquet")[["CoilID","test_proba"]].rename(columns={"test_proba":"v40"}), on="CoilID")
df = df.merge(pd.read_parquet(ROOT/"build_v41/test_proba_v41.parquet")[["CoilID","test_proba"]].rename(columns={"test_proba":"v41"}), on="CoilID")

paradigms = ["v35","v39","v40","v41"]
print(f"Loaded {N} test rows, {len(paradigms)} paradigms: {paradigms}\n")

# Pairwise Spearman on TEST (key diversity check)
print("Pairwise Spearman (test):")
for i in range(len(paradigms)):
    for j in range(i+1, len(paradigms)):
        s, _ = spearmanr(df[paradigms[i]], df[paradigms[j]])
        flag = " ⭐ DIVERSE" if abs(s) < 0.5 else ""
        print(f"  {paradigms[i]} <-> {paradigms[j]}: ρ={s:+.4f}{flag}")
print()

# K_anchor = 181 per Ratnesh recipe
K_ANCHOR = 181
paradigm_topK = {p: set(df.sort_values(p, ascending=False)["CoilID"].tolist()[:K_ANCHOR]) for p in paradigms}

# V4_154 anchor
v4_sub = pd.read_csv(ROOT/"build_v4/expected_submission.csv")
v4_154_coils = set(v4_sub[v4_sub["Y"]==1]["CoilID"].tolist())

# Vote count: max = 5 (4 paradigms + V4_154 anchor)
vote = pd.Series(0, index=df["CoilID"])
for p in paradigms:
    vote.loc[list(paradigm_topK[p])] += 1
vote.loc[list(v4_154_coils & set(coil_order))] += 1

# Tiebreak by mean rank-percentile (across 4 paradigms)
rank_pct = pd.DataFrame(index=df["CoilID"])
for p in paradigms:
    rank_pct[p] = df.set_index("CoilID")[p].rank(pct=True)
rank_pct_mean = rank_pct.mean(axis=1)

consensus = pd.DataFrame({
    "CoilID": vote.index,
    "vote": vote.values,
    "rank_pct_mean": rank_pct_mean.loc[vote.index].values,
})
consensus = consensus.sort_values(["vote","rank_pct_mean"], ascending=[False,False]).reset_index(drop=True)

print("Vote distribution (max=5):")
print(consensus["vote"].value_counts().sort_index(ascending=False).to_string())
print()

# Cumulative-K composition (how many at each vote level cumulatively)
vote_sorted = consensus["vote"].values
print("Cumulative K composition:")
running = {5:0,4:0,3:0,2:0,1:0,0:0}
for K in [138, 150, 154, 164, 170, 175, 181, 185, 186, 190, 200, 212, 220, 230]:
    if K <= N:
        slice_votes = vote_sorted[:K]
        counts = {v: int((slice_votes==v).sum()) for v in [5,4,3,2,1,0]}
        print(f"  K={K:3d}: {counts}")
print()

# Generate K-sweep submissions
out_dir = ROOT / "consensus_v42"
out_dir.mkdir(exist_ok=True)

K_OPTIONS = [138, 150, 154, 164, 170, 175, 181, 185, 186, 190, 200, 212, 220, 230]
for K in K_OPTIONS:
    if K <= 0 or K >= N:
        continue
    sub = consensus.head(K)[["CoilID"]].copy()
    sub["Y"] = 1
    neg = [c for c in coil_order if c not in set(sub["CoilID"])]
    full = pd.concat([sub, pd.DataFrame({"CoilID":neg,"Y":[0]*len(neg)})], ignore_index=True)
    full = full.set_index("CoilID").loc[coil_order].reset_index()[["CoilID","Y"]]
    full.to_csv(out_dir/f"submission_K{K}.csv", index=False)

print(f"Saved {len(K_OPTIONS)} K-variants to {out_dir}/")
print()

# Diff vs V36 K=186 (banked best at 67.55)
v36 = pd.read_csv(ROOT/"consensus_v36/submission_K186.csv")
v36_pos = set(v36[v36.Y==1].CoilID)

print("Difference from V36 K=186 banked (67.55):")
for K in [170, 181, 186, 200, 212]:
    v42 = pd.read_csv(out_dir/f"submission_K{K}.csv")
    v42_pos = set(v42[v42.Y==1].CoilID)
    diff = len(v36_pos.symmetric_difference(v42_pos))
    overlap = len(v36_pos & v42_pos)
    new = len(v42_pos - v36_pos)
    dropped = len(v36_pos - v42_pos)
    print(f"  K={K:3d}: overlap={overlap}, V42-new={new}, V42-dropped-from-V36={dropped}, sym-diff={diff}")
