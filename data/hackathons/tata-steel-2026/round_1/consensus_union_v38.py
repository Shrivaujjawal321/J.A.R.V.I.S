#!/usr/bin/env python3
"""
V38 — Consensus Union with 5 paradigms including V37 (AutoGluon, Spearman ~0.02 vs GBDTs).

This injects genuine model-family diversity into the consensus.
"""
import pandas as pd
import numpy as np
from pathlib import Path
from scipy.stats import spearmanr

ROOT = Path("/home/ujjwal/Documents/J.A.R.V.I.S./data/hackathons/tata-steel-2026/round_1")

# Load test data
test_v4 = pd.read_parquet(ROOT/"build_v4/test_v4.parquet")
coil_order = test_v4["CoilID"].tolist()
N = len(coil_order)

# All 5 paradigms
v4_meta = pd.read_parquet(ROOT/"build_v4/test_meta_v4.parquet")
df = pd.DataFrame({"CoilID": coil_order, "v4": v4_meta["test_meta"].values})
df = df.merge(pd.read_parquet(ROOT/"build_v33/test_proba_v33.parquet")[["CoilID","test_proba"]].rename(columns={"test_proba":"v33"}), on="CoilID")
df = df.merge(pd.read_parquet(ROOT/"build_v34/test_proba_v34.parquet")[["CoilID","test_proba"]].rename(columns={"test_proba":"v34"}), on="CoilID")
df = df.merge(pd.read_parquet(ROOT/"build_v35/test_proba_v35.parquet")[["CoilID","rank_avg_proba"]].rename(columns={"rank_avg_proba":"v35"}), on="CoilID")
df = df.merge(pd.read_parquet(ROOT/"build_v37/test_proba_v37.parquet")[["CoilID","test_proba"]].rename(columns={"test_proba":"v37"}), on="CoilID")

paradigms = ["v4","v33","v34","v35","v37"]
print(f"Loaded {N} test rows, {len(paradigms)} paradigms: {paradigms}\n")

# Pairwise Spearman
print("Pairwise Spearman correlations:")
for i in range(len(paradigms)):
    for j in range(i+1, len(paradigms)):
        s, _ = spearmanr(df[paradigms[i]], df[paradigms[j]])
        flag = " ⭐" if abs(s) < 0.3 else ""
        print(f"  {paradigms[i]} <-> {paradigms[j]}: ρ={s:+.4f}{flag}")
print()

# Per-paradigm top-K_anchor
K_ANCHOR = 181
paradigm_topK = {p: set(df.sort_values(p,ascending=False)["CoilID"].tolist()[:K_ANCHOR]) for p in paradigms}

# V4_154 anchor
v4_sub = pd.read_csv(ROOT/"build_v4/expected_submission.csv")
v4_154_coils = set(v4_sub[v4_sub["Y"]==1]["CoilID"].tolist())

# Vote count: max = 6 (5 paradigms + V4_154 anchor)
vote = pd.Series(0, index=df["CoilID"])
for p in paradigms:
    vote.loc[list(paradigm_topK[p])] += 1
vote.loc[list(v4_154_coils & set(coil_order))] += 1

# Tiebreak: mean rank-percentile
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

print(f"Vote distribution (max=6 = 5 paradigms top-181 + V4_154):")
print(consensus["vote"].value_counts().sort_index(ascending=False).to_string())
print()

# Generate K-sweep submissions
out_dir = ROOT / "consensus_v38"
out_dir.mkdir(exist_ok=True)

# Key K values to try
K_OPTIONS = [138, 154, 164, 170, 181, 185, 186, 187, 190, 195, 200, 212, 220]

print("K-sweep submissions:")
for K in K_OPTIONS:
    if K <= 0 or K >= N:
        continue
    sub = consensus.head(K)[["CoilID"]].copy()
    sub["Y"] = 1
    neg = [c for c in coil_order if c not in set(sub["CoilID"])]
    full = pd.concat([sub, pd.DataFrame({"CoilID":neg,"Y":[0]*len(neg)})], ignore_index=True)
    full = full.set_index("CoilID").loc[coil_order].reset_index()[["CoilID","Y"]]
    full.to_csv(out_dir/f"submission_K{K}.csv", index=False)
    vote_dist = consensus.head(K)["vote"].value_counts().sort_index(ascending=False).to_dict()
    print(f"  K={K:3d}: vote_dist={vote_dist}")

print()
print(f"Saved {len([k for k in K_OPTIONS if 0<k<N])} K-variants to {out_dir}/")

# Diff vs base K=186 (4-paradigm consensus, scored 67.55)
base = pd.read_csv(ROOT/"consensus_v36/submission_K186.csv")
base_pos = set(base[base.Y==1].CoilID)
v38_k186 = pd.read_csv(out_dir/"submission_K186.csv")
v38_pos = set(v38_k186[v38_k186.Y==1].CoilID)
diff = len(base_pos.symmetric_difference(v38_pos))
print(f"\nV38 K=186 vs V36 K=186: {diff} rows different")
print(f"V37-induced changes from adding orthogonal AutoGluon signal: {diff} rows swapped at K=186")
