#!/usr/bin/env python3
"""
consensus_v44.py — V44 Consensus Union (rank-product, 5 paradigms + V4 anchor).

Reads pre-computed test probability parquets from each paradigm training run,
computes a consensus rank-product score, and outputs the top-K=200 submission.

This produces submission_K200_v44.csv (72.83 LB baseline), which is the
starting point for the LB-probing phase that yields the final 87.17 LB score.

Input dependencies (must be run AFTER the corresponding train_*.py scripts):
    build_v35/test_proba_v35.parquet  (column: rank_avg_proba)
    build_v39/test_proba_v39.parquet  (column: test_proba)
    build_v40/test_proba_v40.parquet  (column: test_proba)
    build_v41/test_proba_v41.parquet  (column: test_proba)
    build_v43/test_proba_v43.parquet  (column: test_proba)
    build_v4/test_v4.parquet          (CoilID ordering anchor)
    build_v4/expected_submission.csv  (V4 K=154 positives for vote bonus)

Output:
    consensus_v44/submission_K200.csv — 339 rows, 200 positives
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

# ---- Configuration -----------------------------------------------------------

ROOT = Path(__file__).resolve().parents[2]   # round_1/ directory
# Override with an absolute path if running from a different location:
# ROOT = Path("/path/to/round_1")

K_SUBMIT = 200     # K for the base submission (72.83 LB)
K_ANCHOR = 181     # vote-counting threshold for each paradigm

# ---- Load test CoilID ordering -----------------------------------------------

test_v4 = pd.read_parquet(ROOT / "build_v4" / "test_v4.parquet")
coil_order = test_v4["CoilID"].tolist()
N = len(coil_order)
print(f"Test set: {N} coils")

# ---- Load paradigm probability parquets --------------------------------------

df = pd.DataFrame({"CoilID": coil_order})

# V35: rank-average of 9-model GBDT ensemble (105 features)
v35 = pd.read_parquet(ROOT / "build_v35" / "test_proba_v35.parquet")[
    ["CoilID", "rank_avg_proba"]
].rename(columns={"rank_avg_proba": "v35"})
df = df.merge(v35, on="CoilID")

# V39: CoilID-derived features + LightGBM (58 features, Ratnesh iter35 recipe)
v39 = pd.read_parquet(ROOT / "build_v39" / "test_proba_v39.parquet")[
    ["CoilID", "test_proba"]
].rename(columns={"test_proba": "v39"})
df = df.merge(v39, on="CoilID")

# V40: defect-proximity features + LightGBM (62 features, Ratnesh iter36 recipe)
v40 = pd.read_parquet(ROOT / "build_v40" / "test_proba_v40.parquet")[
    ["CoilID", "test_proba"]
].rename(columns={"test_proba": "v40"})
df = df.merge(v40, on="CoilID")

# V41: stand-order-aware temporal features (additional paradigm)
v41 = pd.read_parquet(ROOT / "build_v41" / "test_proba_v41.parquet")[
    ["CoilID", "test_proba"]
].rename(columns={"test_proba": "v41"})
df = df.merge(v41, on="CoilID")

# V43: rank-product of V4_meta x V40 (highest single-paradigm OOF AUC = 0.890)
v43 = pd.read_parquet(ROOT / "build_v43" / "test_proba_v43.parquet")
v43_col = None
for c in ["test_proba", "rank_product", "oof_proba", "proba"]:
    if c in v43.columns:
        v43_col = c
        break
if v43_col is None:
    v43_col = [c for c in v43.columns if c != "CoilID"][0]
print(f"V43 probability column: {v43_col}")
df = df.merge(
    v43[["CoilID", v43_col]].rename(columns={v43_col: "v43"}), on="CoilID"
)

paradigms = ["v35", "v39", "v40", "v41", "v43"]
print(f"Loaded {len(paradigms)} paradigms for {N} test coils\n")

# ---- Pairwise diversity check ------------------------------------------------

print("Pairwise Spearman correlations (diversity check):")
for i in range(len(paradigms)):
    for j in range(i + 1, len(paradigms)):
        rho, _ = spearmanr(df[paradigms[i]], df[paradigms[j]])
        print(f"  {paradigms[i]} <-> {paradigms[j]}: rho={rho:+.4f}")
print()

# ---- Vote count (top-K_ANCHOR per paradigm) + V4 anchor bonus ----------------

paradigm_topK = {
    p: set(df.sort_values(p, ascending=False)["CoilID"].tolist()[:K_ANCHOR])
    for p in paradigms
}

v4_sub = pd.read_csv(ROOT / "build_v4" / "expected_submission.csv")
v4_154_coils = set(v4_sub[v4_sub["Y"] == 1]["CoilID"].tolist())

vote = pd.Series(0, index=df["CoilID"])
for p in paradigms:
    vote.loc[list(paradigm_topK[p])] += 1
# V4 K=154 positives add one vote each (anchor for strong positives)
vote.loc[list(v4_154_coils & set(coil_order))] += 1

# ---- Rank-percentile mean (tiebreaker) ---------------------------------------

rank_pct = pd.DataFrame(index=df["CoilID"])
for p in paradigms:
    rank_pct[p] = df.set_index("CoilID")[p].rank(pct=True)
rank_pct_mean = rank_pct.mean(axis=1)

# ---- Consensus DataFrame (sort: vote desc, then rank_pct_mean desc) ----------

consensus = pd.DataFrame(
    {
        "CoilID": vote.index,
        "vote": vote.values,
        "rank_pct_mean": rank_pct_mean.loc[vote.index].values,
    }
).sort_values(["vote", "rank_pct_mean"], ascending=[False, False]).reset_index(drop=True)

print("Vote distribution (max=6 = 5 paradigms + V4_154 anchor):")
print(consensus["vote"].value_counts().sort_index(ascending=False).to_string())
print()

# ---- Build K=200 submission --------------------------------------------------

out_dir = ROOT / "consensus_v44"
out_dir.mkdir(exist_ok=True)


def build_submission(consensus_df: pd.DataFrame, k: int) -> pd.DataFrame:
    pos_ids = set(consensus_df.head(k)["CoilID"].tolist())
    rows = [
        {"CoilID": c, "Y": 1 if c in pos_ids else 0}
        for c in coil_order
    ]
    return pd.DataFrame(rows)


sub_k200 = build_submission(consensus, K_SUBMIT)
out_path = out_dir / f"submission_K{K_SUBMIT}.csv"
sub_k200.to_csv(out_path, index=False)

pos_count = int(sub_k200["Y"].sum())
assert pos_count == K_SUBMIT, f"Expected {K_SUBMIT} positives, got {pos_count}"
assert len(sub_k200) == N, f"Expected {N} rows, got {len(sub_k200)}"

print(f"Saved: {out_path}")
print(f"  Rows: {len(sub_k200)} | Positives: {pos_count}")
print(f"  Top vote distribution in K={K_SUBMIT}: "
      f"{consensus.head(K_SUBMIT)['vote'].value_counts().sort_index(ascending=False).to_dict()}")
print()
print("V44 consensus complete. Submit consensus_v44/submission_K200.csv to HackerEarth.")
print("Expected LB: 72.83 (V44 K=200 baseline confirmed on public leaderboard).")
