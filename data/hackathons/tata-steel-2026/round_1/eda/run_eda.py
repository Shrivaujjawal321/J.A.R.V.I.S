"""
Tata Steel AI Hackathon 2026 — Round 1
Full EDA Script
Outputs to: /home/ujjwal/Documents/J.A.R.V.I.S./data/hackathons/tata-steel-2026/round_1/eda/
"""

import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
from scipy import stats
from scipy.stats import pointbiserialr, ks_2samp, chi2_contingency
from sklearn.metrics import roc_auc_score, precision_recall_curve
from sklearn.preprocessing import StandardScaler
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns
from scipy.cluster.hierarchy import linkage, dendrogram, fcluster
import json
import os

# ──────────────────────────────────────────────
# PATHS
# ──────────────────────────────────────────────
DATA_DIR = "/home/ujjwal/Documents/J.A.R.V.I.S./data set of tata steel/dataset"
OUT_DIR  = "/home/ujjwal/Documents/J.A.R.V.I.S./data/hackathons/tata-steel-2026/round_1/eda"
FIG_DIR  = os.path.join(OUT_DIR, "figures")
os.makedirs(FIG_DIR, exist_ok=True)

# ──────────────────────────────────────────────
# LOAD DATA
# ──────────────────────────────────────────────
train = pd.read_csv(os.path.join(DATA_DIR, "train.csv"))
test  = pd.read_csv(os.path.join(DATA_DIR, "test.csv"))
sample_sub = pd.read_csv(os.path.join(DATA_DIR, "sample_submission.csv"))

FEATS = [c for c in train.columns if c.startswith("X")]  # X1..X49
Y = train["Y"]
X_train = train[FEATS]
X_test  = test[FEATS]

print(f"Train shape: {train.shape}")
print(f"Test  shape: {test.shape}")
print(f"Sample sub rows: {len(sample_sub)}")
print(f"Num features: {len(FEATS)}")
print(f"Y=1 count: {Y.sum()}, Y=0 count: {(Y==0).sum()}")

# ──────────────────────────────────────────────
# Q1: SAMPLE SUBMISSION INVESTIGATION
# ──────────────────────────────────────────────
q1_rows = len(sample_sub)
q1_test_rows = len(test)
q1_cols = list(sample_sub.columns)
q1_y_vals = sample_sub["Y"].value_counts().to_dict()
print(f"\n[Q1] sample_submission rows={q1_rows}, test rows={q1_test_rows}, cols={q1_cols}, Y vals={q1_y_vals}")

# ──────────────────────────────────────────────
# Q2: FEATURE SIGNAL STRENGTH
# ──────────────────────────────────────────────
print("\n[Q2] Computing feature signal metrics...")

y0 = train[Y==0]
y1 = train[Y==1]
records = []
for feat in FEATS:
    col = train[feat].copy()
    col_train = col.dropna()
    idx_valid = col.notna()

    y_valid = Y[idx_valid].values
    x_valid = col[idx_valid].values

    # Point-biserial correlation
    if len(np.unique(y_valid)) < 2:
        pb_r = 0.0
        pb_p = 1.0
    else:
        pb_r, pb_p = pointbiserialr(y_valid, x_valid)

    # ROC-AUC (handle all same class edge case)
    if len(np.unique(y_valid)) < 2 or len(y_valid) < 10:
        auc = 0.5
    else:
        auc = roc_auc_score(y_valid, x_valid)
        auc = max(auc, 1 - auc)  # symmetric — always >= 0.5

    # Cohen's d
    x0 = col[Y==0].dropna().values
    x1_arr = col[Y==1].dropna().values
    if len(x0) > 1 and len(x1_arr) > 1:
        pooled_std = np.sqrt((np.var(x0, ddof=1) * (len(x0)-1) + np.var(x1_arr, ddof=1) * (len(x1_arr)-1)) / (len(x0) + len(x1_arr) - 2))
        cohens_d = (np.mean(x1_arr) - np.mean(x0)) / (pooled_std + 1e-9)
    else:
        cohens_d = 0.0

    # KS test
    if len(x0) > 1 and len(x1_arr) > 1:
        ks_stat, ks_p = ks_2samp(x0, x1_arr)
    else:
        ks_stat, ks_p = 0.0, 1.0

    missing_pct = col.isna().mean() * 100
    mean_y0 = np.mean(x0) if len(x0) > 0 else np.nan
    mean_y1 = np.mean(x1_arr) if len(x1_arr) > 0 else np.nan
    std_y0  = np.std(x0, ddof=1) if len(x0) > 1 else np.nan
    std_y1  = np.std(x1_arr, ddof=1) if len(x1_arr) > 1 else np.nan

    records.append({
        "feature_name": feat,
        "point_biserial_r": round(pb_r, 4),
        "roc_auc": round(auc, 4),
        "cohens_d": round(cohens_d, 4),
        "ks_pvalue": round(ks_p, 6),
        "missing_pct": round(missing_pct, 3),
        "mean_y0": round(mean_y0, 4) if not np.isnan(mean_y0) else None,
        "mean_y1": round(mean_y1, 4) if not np.isnan(mean_y1) else None,
        "std_y0": round(std_y0, 4) if not np.isnan(std_y0) else None,
        "std_y1": round(std_y1, 4) if not np.isnan(std_y1) else None,
    })

feat_df = pd.DataFrame(records).sort_values("roc_auc", ascending=False)
feat_df.to_csv(os.path.join(OUT_DIR, "feature_importance_table.csv"), index=False)
print(f"[Q2] Feature importance table saved. Top 5 by AUC:")
print(feat_df[["feature_name","roc_auc","cohens_d","ks_pvalue"]].head(5).to_string(index=False))

top10 = feat_df.head(10)["feature_name"].tolist()
bottom10 = feat_df.tail(10)["feature_name"].tolist()
print(f"\nTop 10: {top10}")
print(f"Bottom 10: {bottom10}")

# ──────────────────────────────────────────────
# Q3: MISSINGNESS ANALYSIS
# ──────────────────────────────────────────────
print("\n[Q3] Missingness signal analysis...")

miss_cols = [c for c in FEATS if train[c].isna().any()]
miss_results = {}
for col_name in miss_cols:
    is_missing = train[col_name].isna().astype(int)
    n_miss = is_missing.sum()
    n_present = (~train[col_name].isna()).sum()

    p_y1_missing  = Y[is_missing==1].mean() if n_miss > 0 else 0.0
    p_y1_present  = Y[is_missing==0].mean() if n_present > 0 else 0.0

    # Chi-square test
    ct = pd.crosstab(is_missing, Y)
    if ct.shape == (2,2):
        chi2, p_chi, dof, expected = chi2_contingency(ct)
    else:
        chi2, p_chi = 0.0, 1.0

    miss_results[col_name] = {
        "n_missing": int(n_miss),
        "p_y1_when_missing": round(float(p_y1_missing), 4),
        "p_y1_when_present": round(float(p_y1_present), 4),
        "lift": round(float(p_y1_missing) / (float(p_y1_present) + 1e-9), 3),
        "chi2": round(chi2, 4),
        "chi2_pvalue": round(p_chi, 6),
        "significant": p_chi < 0.05
    }

print("[Q3] Missingness results:")
for col_name, v in miss_results.items():
    sig = "** SIGNAL **" if v["significant"] else ""
    print(f"  {col_name}: P(Y=1|missing)={v['p_y1_when_missing']:.3f}, P(Y=1|present)={v['p_y1_when_present']:.3f}, lift={v['lift']:.2f}, chi2_p={v['chi2_pvalue']:.4f} {sig}")

missingness_signal_columns = [k for k,v in miss_results.items() if v["significant"]]
print(f"\nMissingness signal columns: {missingness_signal_columns}")

# ──────────────────────────────────────────────
# Q4: FEATURE CLUSTERING (hierarchical)
# ──────────────────────────────────────────────
print("\n[Q4] Feature clustering...")

# Use available rows (impute with median for correlation)
X_imp = X_train.copy()
for c in FEATS:
    X_imp[c].fillna(X_imp[c].median(), inplace=True)

corr_matrix = X_imp.corr()
# hierarchical clustering on features
dist_arr = (1 - corr_matrix.abs()).values.copy()
np.fill_diagonal(dist_arr, 0)
dist_arr = np.clip(dist_arr, 0, None)
dist_matrix = pd.DataFrame(dist_arr, index=corr_matrix.index, columns=corr_matrix.columns)

Z = linkage(dist_matrix, method="ward")
# Cut into 3 clusters (matching the 3 stages)
labels_3 = fcluster(Z, t=3, criterion="maxclust")
cluster_map = {}
for feat, label in zip(FEATS, labels_3):
    cluster_map.setdefault(int(label), []).append(feat)

print("[Q4] 3-cluster assignment (stage hypothesis):")
for cid, feats_list in sorted(cluster_map.items()):
    print(f"  Cluster {cid}: {feats_list}")

# Also try 4 clusters
labels_4 = fcluster(Z, t=4, criterion="maxclust")
cluster_map_4 = {}
for feat, label in zip(FEATS, labels_4):
    cluster_map_4.setdefault(int(label), []).append(feat)

# ──────────────────────────────────────────────
# Q5: OUTLIER ANALYSIS
# ──────────────────────────────────────────────
print("\n[Q5] Outlier analysis (5-sigma)...")

outlier_results = {}
for feat in FEATS:
    col = train[feat].dropna()
    mean_v = col.mean()
    std_v  = col.std()
    if std_v == 0:
        continue
    z_scores = (train[feat] - mean_v) / std_v
    outlier_mask = z_scores.abs() > 5
    n_out = outlier_mask.sum()
    if n_out > 0:
        y_among_outliers = Y[outlier_mask].mean()
        outlier_results[feat] = {
            "n_outliers": int(n_out),
            "defect_rate_in_outliers": round(float(y_among_outliers), 4),
            "overall_defect_rate": round(float(Y.mean()), 4),
            "lift": round(float(y_among_outliers) / (float(Y.mean()) + 1e-9), 3)
        }

print("[Q5] Features with 5-sigma outliers correlated with defects (lift>1.5):")
outlier_signals = {k: v for k, v in outlier_results.items() if v["lift"] > 1.5}
for feat, v in sorted(outlier_signals.items(), key=lambda x: -x[1]["lift"]):
    print(f"  {feat}: n={v['n_outliers']}, defect_rate={v['defect_rate_in_outliers']:.3f}, lift={v['lift']:.2f}")

if not outlier_signals:
    print("  (No features with 5-sigma outliers have lift > 1.5)")

# ──────────────────────────────────────────────
# Q6: TRAIN vs TEST DISTRIBUTION SHIFT
# ──────────────────────────────────────────────
print("\n[Q6] Train vs test distribution shift (KS)...")

shift_results = []
for feat in FEATS:
    x_tr = train[feat].dropna().values
    x_te = test[feat].dropna().values
    if len(x_tr) > 1 and len(x_te) > 1:
        ks_s, ks_p = ks_2samp(x_tr, x_te)
        shift_results.append({"feature": feat, "ks_stat": round(ks_s, 4), "ks_pvalue": round(ks_p, 6)})

shift_df = pd.DataFrame(shift_results).sort_values("ks_stat", ascending=False)
print("[Q6] Top 10 features with biggest train-test distribution shift:")
print(shift_df.head(10).to_string(index=False))

significant_shift = shift_df[shift_df["ks_pvalue"] < 0.01]
shift_risk_features = significant_shift.head(5)["feature"].tolist()
print(f"\nFeatures with significant shift (p<0.01): {significant_shift['feature'].tolist()}")

# ──────────────────────────────────────────────
# Q7: MULTICOLLINEARITY
# ──────────────────────────────────────────────
print("\n[Q7] High-correlation pairs (|r| > 0.9)...")

high_corr_pairs = []
corr_vals = corr_matrix.values
feats_arr = np.array(FEATS)
for i in range(len(FEATS)):
    for j in range(i+1, len(FEATS)):
        r = corr_vals[i, j]
        if abs(r) > 0.9:
            high_corr_pairs.append((FEATS[i], FEATS[j], round(r, 4)))

high_corr_pairs.sort(key=lambda x: -abs(x[2]))
print(f"[Q7] Found {len(high_corr_pairs)} pairs with |r| > 0.9:")
for a, b, r in high_corr_pairs[:20]:
    print(f"  {a} <-> {b}: r={r}")

# ──────────────────────────────────────────────
# Q8: BEST SINGLE-FEATURE DECISION RULE
# ──────────────────────────────────────────────
print("\n[Q8] Best single-feature decision rule...")

best_feat = feat_df.iloc[0]["feature_name"]
col_bf = X_train[best_feat].fillna(X_train[best_feat].median())

# Try all thresholds
precision_arr, recall_arr, threshold_arr = precision_recall_curve(Y, col_bf)

# Find best recall at precision >= 0.90
recall_at_p90 = 0.0
best_thresh_p90 = None
for i in range(len(precision_arr)-1):
    if precision_arr[i] >= 0.90:
        if recall_arr[i] > recall_at_p90:
            recall_at_p90 = recall_arr[i]
            best_thresh_p90 = threshold_arr[i] if i < len(threshold_arr) else None

# Best recall at any precision
best_recall_single = recall_arr[1:-1].max() if len(recall_arr) > 2 else 0.0

print(f"[Q8] Best single feature: {best_feat} (AUC={feat_df.iloc[0]['roc_auc']})")
print(f"     Best recall at Precision>=0.90: {recall_at_p90:.3f}")
print(f"     Best recall (unconstrained): {best_recall_single:.3f}")

# ──────────────────────────────────────────────
# Q9: RECALL CEILING — LightGBM 5-fold CV
# ──────────────────────────────────────────────
print("\n[Q9] LightGBM 5-fold stratified CV to estimate recall ceiling...")

try:
    import lightgbm as lgb
    from sklearn.model_selection import StratifiedKFold
    from sklearn.metrics import recall_score, precision_score

    X_imp_all = X_train.copy()
    for c in FEATS:
        X_imp_all[c].fillna(X_imp_all[c].median(), inplace=True)

    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    cv_results = []
    for fold, (tr_idx, val_idx) in enumerate(skf.split(X_imp_all, Y)):
        X_tr_f, X_val_f = X_imp_all.iloc[tr_idx], X_imp_all.iloc[val_idx]
        y_tr_f, y_val_f = Y.iloc[tr_idx], Y.iloc[val_idx]

        # class_weight via scale_pos_weight
        neg = (y_tr_f == 0).sum()
        pos = (y_tr_f == 1).sum()
        spw = neg / (pos + 1e-9)

        clf = lgb.LGBMClassifier(
            n_estimators=500,
            learning_rate=0.05,
            num_leaves=31,
            scale_pos_weight=spw,
            random_state=42,
            verbose=-1,
            n_jobs=4
        )
        clf.fit(X_tr_f, y_tr_f)

        probs = clf.predict_proba(X_val_f)[:, 1]

        # Sweep thresholds for best recall at precision >= 0.90
        prec_arr, rec_arr, thresh_arr = precision_recall_curve(y_val_f, probs)

        best_rec_p90 = 0.0
        best_thresh_fold = 0.5
        for i in range(len(prec_arr)-1):
            if prec_arr[i] >= 0.90 and rec_arr[i] > best_rec_p90:
                best_rec_p90 = rec_arr[i]
                best_thresh_fold = thresh_arr[i] if i < len(thresh_arr) else 0.5

        # Also record max AUC
        auc_fold = roc_auc_score(y_val_f, probs)

        # Record what recall=1.0 costs in precision
        # threshold at which all positives are caught
        rec1_precision = 0.0
        for i in range(len(rec_arr)):
            if rec_arr[i] >= 1.0:
                rec1_precision = prec_arr[i]
                break

        cv_results.append({
            "fold": fold+1,
            "recall_at_precision_90": round(best_rec_p90, 3),
            "auc_roc": round(auc_fold, 4),
            "precision_at_recall_100": round(rec1_precision, 4),
            "best_threshold": round(float(best_thresh_fold), 4)
        })
        print(f"  Fold {fold+1}: recall@prec>=0.90={best_rec_p90:.3f}, ROC-AUC={auc_fold:.4f}, prec@recall=1.0={rec1_precision:.4f}")

    cv_df = pd.DataFrame(cv_results)
    mean_recall_ceil = cv_df["recall_at_precision_90"].mean()
    mean_prec_at_recall100 = cv_df["precision_at_recall_100"].mean()
    max_recall_ceil = cv_df["recall_at_precision_90"].max()

    print(f"\n[Q9] Mean recall @ precision>=0.90 (5-fold): {mean_recall_ceil:.3f}")
    print(f"     Max recall @ precision>=0.90 (5-fold): {max_recall_ceil:.3f}")
    print(f"     Mean precision when recall=1.0: {mean_prec_at_recall100:.3f}")

    lgbm_available = True

except Exception as e:
    print(f"[Q9] LightGBM failed: {e}")
    mean_recall_ceil = None
    max_recall_ceil = None
    mean_prec_at_recall100 = None
    lgbm_available = False
    cv_results = []

# ──────────────────────────────────────────────
# FIGURE 1: CLASS BALANCE
# ──────────────────────────────────────────────
print("\n[VIZ] Generating figures...")

fig, axes = plt.subplots(1, 2, figsize=(10, 5))
counts = Y.value_counts()
axes[0].bar(["No Defect (Y=0)", "Defect (Y=1)"], [counts[0], counts[1]],
            color=["#2196F3", "#F44336"], edgecolor="black")
axes[0].set_title("Class Balance\n(Train Set)", fontsize=13, fontweight="bold")
axes[0].set_ylabel("Count")
for i, v in enumerate([counts[0], counts[1]]):
    axes[0].text(i, v + 5, f"{v}\n({v/len(Y)*100:.1f}%)", ha="center", fontsize=11)
axes[0].set_ylim(0, counts[0] * 1.15)

axes[1].pie([counts[0], counts[1]], labels=["No Defect (95.12%)", "Defect (4.88%)"],
            colors=["#2196F3", "#F44336"], autopct="%1.1f%%", startangle=90,
            textprops={"fontsize": 11})
axes[1].set_title("Class Proportion", fontsize=13, fontweight="bold")

plt.suptitle("Tata Steel: Extreme Class Imbalance — 66 Defects in 1352 Coils",
             fontsize=12, y=1.02, style="italic")
plt.tight_layout()
plt.savefig(os.path.join(FIG_DIR, "01_class_balance.png"), dpi=150, bbox_inches="tight")
plt.close()
print("  01_class_balance.png done")

# ──────────────────────────────────────────────
# FIGURE 2: FEATURE AUC RANKING
# ──────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(14, 8))
colors = ["#F44336" if x >= 0.6 else "#FF9800" if x >= 0.55 else "#9E9E9E"
          for x in feat_df["roc_auc"]]
bars = ax.barh(feat_df["feature_name"], feat_df["roc_auc"], color=colors)
ax.axvline(0.5, color="black", linestyle="--", linewidth=1, label="Random (0.5)")
ax.axvline(0.6, color="orange", linestyle="--", linewidth=1, alpha=0.7, label="Moderate signal (0.6)")
ax.axvline(0.7, color="red", linestyle="--", linewidth=1, alpha=0.7, label="Strong signal (0.7)")
ax.set_xlabel("ROC-AUC (single feature)", fontsize=11)
ax.set_title("All 49 Features Ranked by Single-Feature ROC-AUC\n(Red = strong, Orange = moderate, Grey = weak)",
             fontsize=12, fontweight="bold")
ax.legend(fontsize=9)
ax.invert_yaxis()
plt.tight_layout()
plt.savefig(os.path.join(FIG_DIR, "02_feature_auc_ranking.png"), dpi=150, bbox_inches="tight")
plt.close()
print("  02_feature_auc_ranking.png done")

# ──────────────────────────────────────────────
# FIGURE 3: TOP-10 FEATURE KDE
# ──────────────────────────────────────────────
fig, axes = plt.subplots(2, 5, figsize=(18, 8))
axes_flat = axes.flatten()
for i, feat in enumerate(top10):
    ax = axes_flat[i]
    d0 = train[feat][Y==0].dropna()
    d1 = train[feat][Y==1].dropna()
    ax.hist(d0, bins=30, alpha=0.5, color="#2196F3", density=True, label="Y=0", linewidth=0)
    ax.hist(d1, bins=20, alpha=0.7, color="#F44336", density=True, label="Y=1", linewidth=0)
    ax.set_title(f"{feat}\nAUC={feat_df[feat_df.feature_name==feat].roc_auc.values[0]:.3f}",
                 fontsize=9, fontweight="bold")
    ax.legend(fontsize=7)
    ax.set_xlabel("Value", fontsize=7)
    ax.set_ylabel("Density", fontsize=7)
    ax.tick_params(labelsize=7)

plt.suptitle("Top-10 Features: Distribution by Class (Blue=No Defect, Red=Defect)",
             fontsize=13, fontweight="bold", y=1.01)
plt.tight_layout()
plt.savefig(os.path.join(FIG_DIR, "03_top10_feature_distributions.png"), dpi=150, bbox_inches="tight")
plt.close()
print("  03_top10_feature_distributions.png done")

# ──────────────────────────────────────────────
# FIGURE 4: CORRELATION HEATMAP (hierarchically ordered)
# ──────────────────────────────────────────────
# Reorder features by hierarchical clustering
from scipy.cluster.hierarchy import leaves_list
ordered_idx = leaves_list(Z)
ordered_feats = [FEATS[i] for i in ordered_idx]
corr_ordered = corr_matrix.loc[ordered_feats, ordered_feats]

fig, ax = plt.subplots(figsize=(16, 14))
mask = np.zeros_like(corr_ordered.values, dtype=bool)
sns.heatmap(corr_ordered, ax=ax, cmap="RdBu_r", center=0, vmin=-1, vmax=1,
            square=True, linewidths=0.3,
            cbar_kws={"shrink": 0.7, "label": "Pearson r"},
            xticklabels=True, yticklabels=True)
ax.set_title("Feature–Feature Correlation Matrix (Hierarchically Ordered)\nDark Red=+1, Dark Blue=-1",
             fontsize=13, fontweight="bold")
ax.tick_params(labelsize=6)
plt.tight_layout()
plt.savefig(os.path.join(FIG_DIR, "04_correlation_heatmap.png"), dpi=150, bbox_inches="tight")
plt.close()
print("  04_correlation_heatmap.png done")

# ──────────────────────────────────────────────
# FIGURE 5: X15 MISSINGNESS VS Y
# ──────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# Bar chart: P(Y=1) by missingness status for each column
miss_cols_sorted = sorted(miss_results.keys(), key=lambda x: -miss_results[x]["lift"])
p_y1_miss = [miss_results[c]["p_y1_when_missing"] for c in miss_cols_sorted]
p_y1_pres = [miss_results[c]["p_y1_when_present"] for c in miss_cols_sorted]

x_pos = np.arange(len(miss_cols_sorted))
width = 0.35
bars1 = axes[0].bar(x_pos - width/2, p_y1_miss, width, label="X Missing", color="#F44336", alpha=0.8)
bars2 = axes[0].bar(x_pos + width/2, p_y1_pres, width, label="X Present", color="#2196F3", alpha=0.8)
axes[0].axhline(Y.mean(), color="black", linestyle="--", linewidth=1.5, label=f"Overall avg ({Y.mean():.3f})")
axes[0].set_xticks(x_pos)
axes[0].set_xticklabels(miss_cols_sorted, rotation=45, ha="right", fontsize=9)
axes[0].set_ylabel("P(Defect | Status)")
axes[0].set_title("P(Y=1) When Feature is Missing vs Present", fontweight="bold")
axes[0].legend(fontsize=9)
axes[0].set_ylim(0, max(p_y1_miss + p_y1_pres) * 1.3 if p_y1_miss else 0.2)

# Heatmap of missingness pattern
miss_pattern = train[[c for c in miss_cols_sorted]].isna().astype(int)
miss_pattern["Y"] = Y.values
miss_by_y = miss_pattern.groupby("Y").mean()
sns.heatmap(miss_by_y, ax=axes[1], cmap="Reds", annot=True, fmt=".2f",
            cbar_kws={"shrink": 0.7, "label": "Miss rate"})
axes[1].set_title("Missing Rate per Feature by Class", fontweight="bold")
axes[1].set_xlabel("Features with Missing Values")
axes[1].set_yticklabels(["No Defect (Y=0)", "Defect (Y=1)"], rotation=0)

plt.suptitle("X15 & Other Features: Is Missingness a Defect Signal?",
             fontsize=12, fontweight="bold", y=1.01)
plt.tight_layout()
plt.savefig(os.path.join(FIG_DIR, "05_x15_missingness_vs_y.png"), dpi=150, bbox_inches="tight")
plt.close()
print("  05_x15_missingness_vs_y.png done")

# ──────────────────────────────────────────────
# FIGURE 6: TRAIN vs TEST DISTRIBUTION SHIFTS
# ──────────────────────────────────────────────
top_shift_feats = shift_df.head(6)["feature"].tolist()
fig, axes = plt.subplots(2, 3, figsize=(15, 8))
axes_flat = axes.flatten()
for i, feat in enumerate(top_shift_feats):
    ax = axes_flat[i]
    tr_vals = train[feat].dropna().values
    te_vals = test[feat].dropna().values
    ax.hist(tr_vals, bins=30, alpha=0.6, color="#2196F3", density=True, label="Train")
    ax.hist(te_vals, bins=30, alpha=0.6, color="#FF9800", density=True, label="Test")
    ks_s = shift_df[shift_df.feature == feat]["ks_stat"].values[0]
    ks_p = shift_df[shift_df.feature == feat]["ks_pvalue"].values[0]
    ax.set_title(f"{feat} | KS={ks_s:.3f}, p={ks_p:.4f}", fontsize=10, fontweight="bold")
    ax.legend(fontsize=8)
    ax.set_xlabel("Value", fontsize=8)
    ax.set_ylabel("Density", fontsize=8)
    ax.tick_params(labelsize=8)

plt.suptitle("Top-6 Train vs Test Distribution Shifts (Blue=Train, Orange=Test)",
             fontsize=12, fontweight="bold", y=1.01)
plt.tight_layout()
plt.savefig(os.path.join(FIG_DIR, "06_train_vs_test_distribution_shifts.png"), dpi=150, bbox_inches="tight")
plt.close()
print("  06_train_vs_test_distribution_shifts.png done")

# ──────────────────────────────────────────────
# FINDINGS SUMMARY JSON
# ──────────────────────────────────────────────
findings = {
    "top_10_features": top10,
    "weakest_features": bottom10,
    "missingness_signal_columns": missingness_signal_columns,
    "feature_clusters": cluster_map,
    "feature_clusters_4way": cluster_map_4,
    "recall_ceiling_at_precision_90": float(mean_recall_ceil) if mean_recall_ceil is not None else None,
    "max_recall_ceiling_any_fold": float(max_recall_ceil) if max_recall_ceil is not None else None,
    "mean_precision_when_recall_100": float(mean_prec_at_recall100) if mean_prec_at_recall100 is not None else None,
    "distribution_shift_risk_features": shift_risk_features,
    "high_corr_pairs": [(a, b, r) for a, b, r in high_corr_pairs[:10]],
    "high_priority_engineering_moves": [
        f"Add is_missing flag for columns: {missingness_signal_columns} (chi-sq signal detected)",
        f"Interaction terms: {top10[0]} x {top10[1]} — top-2 AUC features multiplied",
        "Stage-wise aggregate features: mean/std of each cluster group per coil",
        f"Outlier flag: add boolean 'is_outlier_Xk' for features with 5-sigma lift>1.5: {list(outlier_signals.keys())[:5]}",
        "Ratio features between correlated pairs may encode process deviation",
        "log-transform right-skewed features before modeling to help tree splits",
    ],
    "cv_fold_results": cv_results,
    "best_single_feature": feat_df.iloc[0]["feature_name"],
    "best_single_feature_auc": float(feat_df.iloc[0]["roc_auc"]),
    "single_feature_recall_at_precision_90": float(recall_at_p90),
    "high_corr_pair_count_0_9": len(high_corr_pairs),
    "sample_submission": {
        "rows": q1_rows,
        "columns": q1_cols,
        "is_truncated": q1_rows == 10,
        "test_set_rows": q1_test_rows
    }
}

with open(os.path.join(OUT_DIR, "findings_summary.json"), "w") as f:
    json.dump(findings, f, indent=2)
print("\n[JSON] findings_summary.json saved")

# ──────────────────────────────────────────────
# Print all key findings for the report
# ──────────────────────────────────────────────
print("\n" + "="*70)
print("SUMMARY OF KEY NUMBERS FOR REPORT GENERATION")
print("="*70)
print(f"\nQ1: sample_submission has {q1_rows} rows (ONLY {q1_rows} — truncated example)")
print(f"    Actual submission needs {q1_test_rows} rows")
print(f"\nQ2: Top-10 features by AUC: {top10}")
print(f"    Bottom-10: {bottom10}")
print(f"\nQ3: Missingness-signal columns: {missingness_signal_columns}")
for k, v in miss_results.items():
    print(f"    {k}: missing_rate={v['n_missing']}, p_y1_miss={v['p_y1_when_missing']:.4f}, lift={v['lift']:.2f}, chi2_p={v['chi2_pvalue']:.4f}")
print(f"\nQ4: Feature clusters (3-way):")
for cid, fl in sorted(cluster_map.items()):
    print(f"    Cluster {cid}: {fl}")
print(f"\nQ5: Outlier signals (lift>1.5): {list(outlier_signals.keys())}")
for feat, v in outlier_signals.items():
    print(f"    {feat}: n={v['n_outliers']}, defect_rate={v['defect_rate_in_outliers']:.3f}, lift={v['lift']:.2f}")
print(f"\nQ6: Significant shift features (p<0.01): {significant_shift['feature'].tolist()[:10]}")
print(f"\nQ7: High-corr pairs (|r|>0.9): {len(high_corr_pairs)}")
for a, b, r in high_corr_pairs[:5]:
    print(f"    {a} <-> {b}: r={r}")
print(f"\nQ8: Best single feature={feat_df.iloc[0]['feature_name']}, AUC={feat_df.iloc[0]['roc_auc']}")
print(f"    Recall@Precision>=0.90 (single feature): {recall_at_p90:.3f}")
print(f"\nQ9: LightGBM 5-fold CV:")
if cv_results:
    for r in cv_results:
        print(f"    {r}")
    print(f"    MEAN recall@prec>=0.90 = {mean_recall_ceil:.3f}")
    print(f"    MEAN prec@recall=1.0   = {mean_prec_at_recall100:.3f}")
else:
    print("    (LightGBM not available)")

print("\n[DONE] All EDA artifacts written to:", OUT_DIR)
