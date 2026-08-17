#!/usr/bin/env python3
"""
V36 — Consensus Union (4 paradigms: V4 + V33 + V34 + V35) + V4_154 anchor

Method:
1. Each paradigm contributes its top-K_anchor (K_anchor=181) CoilIDs
2. V4_154 contributes 154 anchor CoilIDs
3. Vote per CoilID = how many of these 5 sources include it (max 5)
4. Tiebreak: mean rank-percentile across 4 paradigms
5. Sort by (vote desc, rank_pct_mean desc), take top-K for final submission

OOF-CONSENSUS VALIDATION (internal K-proxy, no LB burn needed):
1. Same 4 paradigms have OOF probas on train (5-fold)
2. Compute SAME consensus union on OOF data → pick K that maximizes OOF (R+P)/2
3. Apply that K to test consensus → final submission
"""
import pandas as pd
import numpy as np
from pathlib import Path
from scipy.stats import spearmanr

ROOT = Path("/home/ujjwal/Documents/J.A.R.V.I.S./data/hackathons/tata-steel-2026/round_1")

# ===========================================================================
# STEP 1 — Load test probas (4 paradigms)
# ===========================================================================
test_v4 = pd.read_parquet(ROOT / "build_v4/test_v4.parquet")
coil_order = test_v4["CoilID"].tolist()
N = len(coil_order)

v4_meta = pd.read_parquet(ROOT / "build_v4/test_meta_v4.parquet")
v4_proba = pd.DataFrame({"CoilID": coil_order, "v4": v4_meta["test_meta"].values})

v33_df = pd.read_parquet(ROOT / "build_v33/test_proba_v33.parquet")
v33_proba = v33_df[["CoilID", "test_proba"]].rename(columns={"test_proba": "v33"})

v34_df = pd.read_parquet(ROOT / "build_v34/test_proba_v34.parquet")
v34_proba = v34_df[["CoilID", "test_proba"]].rename(columns={"test_proba": "v34"})

v35_df = pd.read_parquet(ROOT / "build_v35/test_proba_v35.parquet")
# Use rank_avg_proba as V35's single signal
v35_proba = v35_df[["CoilID", "rank_avg_proba"]].rename(columns={"rank_avg_proba": "v35"})

df = v4_proba.merge(v33_proba, on="CoilID").merge(v34_proba, on="CoilID").merge(v35_proba, on="CoilID")
assert len(df) == N

paradigms = ["v4", "v33", "v34", "v35"]
print(f"Loaded {N} test rows, {len(paradigms)} paradigms: {paradigms}\n")

# ===========================================================================
# STEP 2 — Diagnostics
# ===========================================================================
print("Per-paradigm proba range:")
for p in paradigms:
    print(f"  {p}: min={df[p].min():.4g}  median={df[p].median():.4g}  max={df[p].max():.4g}")
print()
print("Pairwise Spearman:")
for i in range(len(paradigms)):
    for j in range(i+1, len(paradigms)):
        s, _ = spearmanr(df[paradigms[i]], df[paradigms[j]])
        print(f"  {paradigms[i]} <-> {paradigms[j]}: ρ={s:+.4f}")
print()

# ===========================================================================
# STEP 3 — V4_154 anchor + per-paradigm top-181 + vote count
# ===========================================================================
K_ANCHOR = 181

v4_sub = pd.read_csv(ROOT / "build_v4/expected_submission.csv")
v4_154_coils = set(v4_sub[v4_sub["Y"] == 1]["CoilID"].tolist())

paradigm_topK = {}
for p in paradigms:
    sorted_coils = df.sort_values(p, ascending=False)["CoilID"].tolist()
    paradigm_topK[p] = set(sorted_coils[:K_ANCHOR])

vote = pd.Series(0, index=df["CoilID"])
for p in paradigms:
    vote.loc[list(paradigm_topK[p])] += 1
vote.loc[list(v4_154_coils & set(coil_order))] += 1

rank_pct = pd.DataFrame(index=df["CoilID"])
for p in paradigms:
    rank_pct[p] = df.set_index("CoilID")[p].rank(pct=True)
rank_pct_mean = rank_pct.mean(axis=1)

consensus = pd.DataFrame({
    "CoilID": vote.index,
    "vote": vote.values,
    "rank_pct_mean": rank_pct_mean.loc[vote.index].values,
})
consensus = consensus.sort_values(["vote", "rank_pct_mean"], ascending=[False, False]).reset_index(drop=True)

print("Vote distribution (max=5 = all 4 paradigms top-181 + V4_154):")
print(consensus["vote"].value_counts().sort_index(ascending=False).to_string())
print()

# ===========================================================================
# STEP 4 — OOF-CONSENSUS K-VALIDATION (internal K proxy, no LB burn!)
# ===========================================================================
print("=" * 70)
print("OOF-CONSENSUS K-VALIDATION (internal K-selection signal)")
print("=" * 70)

# Load OOF probas for each paradigm
# V4 has oof_v4.parquet with oof_meta column
# V33/V34/V35 should have oof_v33/v34/v35.parquet

train_v4 = pd.read_parquet(ROOT / "build_v4/train_v4.parquet")
train_coils = train_v4["CoilID"].tolist()
y_train = train_v4["Y"].values
n_train = len(train_coils)
n_pos_train = int(y_train.sum())
print(f"Train: n={n_train}, n_pos={n_pos_train}, prevalence={n_pos_train/n_train:.4f}\n")

oof_v4 = pd.read_parquet(ROOT / "build_v4/oof_v4.parquet")
# v4 oof needs CoilID alignment — assume same row order as train_v4
oof_v4_meta = oof_v4["oof_meta"].values

oof_v33 = pd.read_parquet(ROOT / "build_v33/oof_v33.parquet")
oof_v34 = pd.read_parquet(ROOT / "build_v34/oof_v34.parquet")
oof_v35 = pd.read_parquet(ROOT / "build_v35/oof_v35.parquet")

print(f"OOF v4 shape: {oof_v4.shape}, cols: {list(oof_v4.columns)}")
print(f"OOF v33 shape: {oof_v33.shape}, cols: {list(oof_v33.columns)}")
print(f"OOF v34 shape: {oof_v34.shape}, cols: {list(oof_v34.columns)}")
print(f"OOF v35 shape: {oof_v35.shape}, cols: {list(oof_v35.columns)}")
print()

# Align all OOF on CoilID
oof_df = pd.DataFrame({"CoilID": train_coils, "Y": y_train, "v4": oof_v4_meta})

for name, oof_pq in [("v33", oof_v33), ("v34", oof_v34), ("v35", oof_v35)]:
    if "CoilID" in oof_pq.columns:
        # Find the proba column
        proba_col = None
        for c in ["oof_proba", "rank_avg_proba", "oof_meta", "test_proba"]:
            if c in oof_pq.columns:
                proba_col = c
                break
        if proba_col is None:
            # First non-CoilID non-Y column
            cands = [c for c in oof_pq.columns if c not in ("CoilID","Y","y")]
            proba_col = cands[0]
        print(f"  {name}: using column '{proba_col}'")
        oof_df = oof_df.merge(oof_pq[["CoilID", proba_col]].rename(columns={proba_col: name}), on="CoilID", how="left")
    else:
        # No CoilID — assume row alignment with train
        if len(oof_pq) == n_train:
            cands = [c for c in oof_pq.columns if c not in ("Y","y")]
            print(f"  {name}: no CoilID, using column '{cands[0]}' (positional align)")
            oof_df[name] = oof_pq[cands[0]].values
        else:
            print(f"  WARNING {name}: shape mismatch ({len(oof_pq)} vs {n_train}), skipping")

# Drop rows with NaN in any paradigm
before = len(oof_df)
oof_df = oof_df.dropna()
print(f"\nOOF aligned: {len(oof_df)} of {before} rows after dropna")
print(f"Paradigms available in OOF: {[c for c in oof_df.columns if c not in ('CoilID','Y')]}")
print()

# OOF consensus union
oof_paradigms = [c for c in oof_df.columns if c not in ("CoilID","Y")]
oof_topK = {}
for p in oof_paradigms:
    sorted_idx = oof_df.sort_values(p, ascending=False)["CoilID"].tolist()
    # K_anchor scaled to train size: train has ~1352 rows vs 339 test, so anchor K_train = K_anchor * (n_train/n_test)
    K_anchor_train = int(K_ANCHOR * n_train / N)  # ≈ 722
    oof_topK[p] = set(sorted_idx[:K_anchor_train])

oof_vote = pd.Series(0, index=oof_df["CoilID"])
for p in oof_paradigms:
    oof_vote.loc[list(oof_topK[p])] += 1
# V4 binary on train: any train rows V4 flagged positively?
# Use oof_v4 with threshold = V4's chosen threshold (T=0.01428)
v4_oof_positive = set(oof_df[oof_df["v4"] > 0.01428]["CoilID"].tolist())
oof_vote.loc[list(v4_oof_positive & set(oof_df["CoilID"]))] += 1

oof_rank_pct = pd.DataFrame(index=oof_df["CoilID"])
for p in oof_paradigms:
    oof_rank_pct[p] = oof_df.set_index("CoilID")[p].rank(pct=True)
oof_rank_pct_mean = oof_rank_pct.mean(axis=1)

oof_consensus = pd.DataFrame({
    "CoilID": oof_vote.index,
    "vote": oof_vote.values,
    "rank_pct_mean": oof_rank_pct_mean.loc[oof_vote.index].values,
})
oof_consensus = oof_consensus.merge(oof_df[["CoilID","Y"]], on="CoilID")
oof_consensus = oof_consensus.sort_values(["vote", "rank_pct_mean"], ascending=[False, False]).reset_index(drop=True)

print(f"OOF vote distribution (max=5):")
print(oof_consensus["vote"].value_counts().sort_index(ascending=False).to_string())
print()

# K-sweep on OOF: scale K from test-K via (n_train/n_test) ratio
# Effective: K_train_test_equiv = K_test * (n_pos_train / n_pos_test_estimated)
# Simpler: sweep K_train, compute (R+P)/2 vs train labels
n_pos_oof = int(oof_consensus["Y"].sum())
print(f"OOF K-sweep ({n_pos_oof} positives in OOF):")
oof_K_results = []
for K_train in range(50, min(800, n_train), 10):
    selected = oof_consensus.head(K_train)
    tp = int(selected["Y"].sum())
    r = tp / n_pos_oof if n_pos_oof > 0 else 0
    p = tp / K_train if K_train > 0 else 0
    score = (r + p) / 2 * 100
    oof_K_results.append((K_train, tp, r, p, score))

oof_K_df = pd.DataFrame(oof_K_results, columns=["K_train","TP","R","P","score"])
best_idx = oof_K_df["score"].idxmax()
best_K_train = oof_K_df.loc[best_idx, "K_train"]
best_score = oof_K_df.loc[best_idx, "score"]
print(f"\nOOF-optimal K_train = {best_K_train}, OOF score = {best_score:.2f}")
print(f"K_train / n_train ratio = {best_K_train/n_train:.4f}")

# Scale to test K
# n_pos ratio implied: K_train * (n_pos_test / n_pos_train) = K_test
# But we don't know n_pos_test. Best guess: assume same selection-rate.
# Selection-rate-based: K_test_recommended = best_K_train * (N / n_train)
K_test_selection_rate = int(round(best_K_train * N / n_train))
print(f"K_test (selection-rate scaling) = {K_test_selection_rate}")

# Show neighborhood of best K
print(f"\nNeighbourhood of best K_train (in OOF):")
print(oof_K_df.iloc[max(0,best_idx-5):best_idx+6].to_string(index=False))
print()

# ===========================================================================
# STEP 5 — Final test submissions for K-sweep
# ===========================================================================
print("=" * 70)
print("FINAL TEST K-SWEEP SUBMISSIONS")
print("=" * 70)

K_OPTIONS = sorted(set([138, 154, 164, 170, 181, 200, 212, K_test_selection_rate]))

out_dir = ROOT / "consensus_v36"
out_dir.mkdir(exist_ok=True)

for K in K_OPTIONS:
    if K <= 0 or K >= N:
        continue
    sub = consensus.head(K)[["CoilID"]].copy()
    sub["Y"] = 1
    neg = [c for c in coil_order if c not in set(sub["CoilID"])]
    sub_full = pd.concat([sub, pd.DataFrame({"CoilID": neg, "Y": [0]*len(neg)})], ignore_index=True)
    sub_full = sub_full.set_index("CoilID").loc[coil_order].reset_index()[["CoilID","Y"]]
    sub_full.to_csv(out_dir / f"submission_K{K}.csv", index=False)

    sel_coils = set(sub_full[sub_full["Y"]==1]["CoilID"])
    vote_dist = consensus.head(K)["vote"].value_counts().sort_index(ascending=False).to_dict()
    cov = {p: len(sel_coils & paradigm_topK[p]) for p in paradigms}
    cov["v4_154"] = len(sel_coils & v4_154_coils)
    print(f"  K={K:3d}: vote={vote_dist}, cov={cov}")

print()
print(f"Saved {len([k for k in K_OPTIONS if 0<k<N])} K-variants to {out_dir}/")
print()
print(f"RECOMMENDED K (from OOF-consensus selection-rate scaling): K_test = {K_test_selection_rate}")
print(f"OOF expected score at recommended K: {best_score:.2f}")
print(f"V4 OOF→LB calibration delta: +2.67 (single-model, may not apply to consensus)")
print(f"Conservative est LB at recommended K: {best_score + 2.67:.2f}")
