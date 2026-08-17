# R12 — KNN-Based Feature Variants Beyond Defect-Proximity
**Date:** 2026-05-24
**Context:** V40 OOF 0.87, LB 72.83. ML ceiling previously estimated at 0.89; new KNN strategies targeting AUC 0.95+.
**Goal:** Identify highest-leverage KNN feature variants, implementation patterns, CV-safety rules, and expected marginal lift.

---

## Executive Summary

The existing V40 defect-proximity feature works (OOF 0.87) because it captures a distance signal in 49-D Euclidean space. However, Euclidean distance over 49 features is **distance-dilution territory** — curse of dimensionality means any two distant defects look "similar" in all-feature space. The highest-leverage improvements come from:

1. **KNN-Target-Encoding in low-dimensional subspaces** (temperature subspace X4-X9, force subspace X29-X33) — removes noise dims, sharpens "who is my nearest defective neighbor?"
2. **Soft K-means cluster distances** (k=8, 16, 32) — provides a continuous "soft membership" signal that tells the model WHICH operational mode a coil is in, which is orthogonal to distance-to-nearest-defect.
3. **SCARF contrastive embeddings + KNN** — learns a 16-32D space where defects are explicitly pulled apart from non-defects, then KNN in THAT space is maximally informative. Highest ceiling, highest implementation cost.
4. **PCA subspace KNN** (10-D, 20-D) — fast to implement, removes correlated noise, gives diversity from raw-space proximity.
5. **UMAP 2D features** — informative if defect cluster is visually separable; cheap to add as 2 extra columns with correct fold-safe implementation.

**Hard constraint:** AUC 0.95+ is needed for honest LB 80+. These features together are credibly worth +0.02-0.05 AUC over V40's 0.87. That bridges ~half the gap. Remaining gap requires either (a) better label quality, (b) LB probing, or (c) contrastive pre-training going further than SCARF default.

---

## 1. KNN-Target-Encoding (KNN-TE)

### Concept
For each row i, find its K nearest training neighbors (excluding i itself for train, full train for test). Compute the **mean Y of those K neighbors**. This is a continuous "local defect rate" feature — a row surrounded by mostly defective neighbors gets a high value.

This is different from V40's proximity feature which measures **distance to nearest defect**. KNN-TE measures **defect density in the local neighborhood**, which is more robust to sparse defect regions.

### CV-Safety (Critical)
Naive KNN-TE leaks: if row i is in fold j and you compute its K neighbors from ALL training data (including fold j), you are using target information from the same fold.

**Safe pattern — identical to sklearn TargetEncoder's cross-fitting:**
```python
from sklearn.model_selection import KFold
from sklearn.neighbors import NearestNeighbors
import numpy as np

def knn_target_encode_oof(X_train, y_train, X_test, k=10, n_folds=5):
    """
    OOF-safe KNN target encoding.
    For each train row: compute mean-Y of K neighbors from OTHER folds only.
    For test rows: compute mean-Y of K neighbors from ALL train.
    """
    kf = KFold(n_splits=n_folds, shuffle=True, random_state=42)
    train_feat = np.zeros(len(X_train))

    for fold_idx, (tr_idx, val_idx) in enumerate(kf.split(X_train)):
        # Fit KNN on the OTHER K-1 folds
        nbrs = NearestNeighbors(n_neighbors=k, metric='euclidean').fit(X_train[tr_idx])
        dists, indices = nbrs.kneighbors(X_train[val_idx])
        # Mean Y of K neighbors (all from tr_idx — no leakage)
        train_feat[val_idx] = y_train[tr_idx][indices].mean(axis=1)

    # Test: use all train rows
    nbrs_full = NearestNeighbors(n_neighbors=k, metric='euclidean').fit(X_train)
    dists_t, indices_t = nbrs_full.kneighbors(X_test)
    test_feat = y_train[indices_t].mean(axis=1)

    return train_feat, test_feat
```

**K sensitivity:** Try k=5, 10, 20. Lower k = noisier but more local. Higher k = smoother but dilutes hot zones. At ~1500 train rows and ~22 defects, k=10 is reasonable (expected ~0.07 mean for random neighbor → 0.5+ for hot-zone neighbors).

### Subspace Variants (Key Diversity Source)
Run KNN-TE independently in:
- **Temperature subspace:** X4-X9 (6 dims) — captures thermal similarity
- **Force subspace:** X29-X33 (5 dims) — captures mechanical similarity
- **Composition subspace:** X42, X46, X47, X48 (4 dims) — captures metallurgical grade similarity
- **Full 49-D space** (baseline, already partially in V40)

Each subspace finds **different neighbors**, generating 4 orthogonal KNN-TE features. The model can learn which subspace's "defective neighbor" signal matters most for each decision.

### Expected Features: 4-8 (4 subspaces × 1-2 k values)
### Expected AUC lift: +0.01 to +0.02 standalone; +0.005-0.01 marginal over V40 proximity

---

## 2. Soft K-Means Cluster Distances

### Concept
K-means with k=8, 16, 32 clusters on training features. For each row, compute **distance to ALL k centroids** (not just assigned cluster). This gives k continuous features representing "which operational mode is this coil closest to?"

This captures **operational regime identity** — a coil in a "hot, high-carbon, fast-rolling" regime might have higher defect rate than one in "cool, low-carbon, slow" regime. The cluster distances tell the GBDT the probability of being in each regime.

Why soft? Hard cluster assignment (one-hot) loses the distance gradient. GBDT can learn thresholds on the soft distances much better than binary assignments.

### Implementation
```python
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import numpy as np

def soft_kmeans_features(X_train, X_test, k_list=[8, 16, 32], random_state=42):
    """
    Returns distance-to-centroid features for each k.
    Fit on train only; transform both train and test.
    """
    scaler = StandardScaler()
    X_tr_scaled = scaler.fit_transform(X_train)
    X_te_scaled = scaler.transform(X_test)

    all_train_feats, all_test_feats = [], []

    for k in k_list:
        km = KMeans(n_clusters=k, n_init=10, random_state=random_state)
        km.fit(X_tr_scaled)

        # Euclidean distance to each centroid: shape (n_rows, k)
        train_dists = np.sqrt(((X_tr_scaled[:, None] - km.cluster_centers_[None]) ** 2).sum(axis=2))
        test_dists  = np.sqrt(((X_te_scaled[:, None] - km.cluster_centers_[None]) ** 2).sum(axis=2))

        all_train_feats.append(train_dists)
        all_test_feats.append(test_dists)

    return np.hstack(all_train_feats), np.hstack(all_test_feats)
    # Output: (n_rows, 8+16+32) = 56 features for k=[8,16,32]
```

**CV-Safety:** Fit K-means inside each OOF fold on the fold's training rows. Apply to val rows. For test: fit on ALL train.

**k selection:** k=8 captures broad regimes (overheating vs. underheating vs. normal); k=16 more granular; k=32 might overfit on ~1500 rows. Recommend k=8 and k=16 only.

### Expected Features: 24 (8+16)
### Expected AUC lift: +0.005 to +0.015 marginal (operational regime signal is partially captured by raw features already, but soft distances add a continuous version)

---

## 3. PCA Subspace KNN Features

### Concept
Reduce 49-D feature space to 10-D and 20-D via PCA (trained on train-only). Then compute KNN-TE and/or distance-to-nearest-defect in the reduced space.

**Why this helps:** PCA rotates the space to maximize variance, discarding noise axes. Two coils that are "similar in the PCA-10 sense" share the dominant 10 variance directions. This is often a better "similarity" definition than raw Euclidean for correlated tabular features (and Tata's sensor features are likely correlated — temperature readings at consecutive stands are strongly correlated).

### Implementation
```python
from sklearn.decomposition import PCA

def pca_knn_features(X_train, y_train, X_test, n_components_list=[10, 20], k=10, n_folds=5):
    """
    For each PCA dimensionality: compute fold-safe KNN-TE in that space.
    """
    scaler = StandardScaler()
    X_tr_sc = scaler.fit_transform(X_train)
    X_te_sc = scaler.transform(X_test)

    all_train, all_test = [], []

    for nc in n_components_list:
        pca = PCA(n_components=nc, random_state=42)
        X_tr_pca = pca.fit_transform(X_tr_sc)
        X_te_pca = pca.transform(X_te_sc)

        # Now apply fold-safe KNN-TE in PCA space
        tr_feat, te_feat = knn_target_encode_oof(
            X_tr_pca, y_train, X_te_pca, k=k, n_folds=n_folds
        )
        all_train.append(tr_feat.reshape(-1, 1))
        all_test.append(te_feat.reshape(-1, 1))

        # Also: distance to nearest DEFECT in PCA space
        defect_mask = y_train == 1
        X_defects_pca = X_tr_pca[defect_mask]
        nbrs = NearestNeighbors(n_neighbors=1).fit(X_defects_pca)

        dist_train, _ = nbrs.kneighbors(X_tr_pca)
        dist_test, _  = nbrs.kneighbors(X_te_pca)
        all_train.append(dist_train)
        all_test.append(dist_test)

    return np.hstack(all_train), np.hstack(all_test)
    # Output: (n_rows, 4) — 2 KNN-TE + 2 distance-to-defect for 2 PCA dims
```

**Important:** PCA fit must be inside OOF fold for strict safety, but in practice fitting PCA on all train (unsupervised) is low-leakage-risk since it uses no Y.

### Expected Features: 4-8 (2 KNN-TE + 2 defect-distance for 10-D and 20-D)
### Expected AUC lift: +0.008 to +0.015 (diversity from V40's raw-space proximity; PCA space often finds closer true-similar neighbors)

---

## 4. Stand-Axis Decomposed KNN (Subspace-Isolated)

### Concept
The Tata dataset has physically meaningful feature groups:
- **X4-X9**: Entry temperatures at 6 stands
- **X10-X16**: Finishing temperatures at 7 stands
- **X17-X23**: Strip speed at 7 stands
- **X24-X28**: Rolling load at 5 stands
- **X29-X33**: Rolling force at 5 stands
- **X34-X38**: Strip thickness at 5 stands

For each stand group, compute KNN-TE independently. This gives one feature per group = 6 features that capture "coils with similar thermal/mechanical/geometric history" as separate signals.

**Physical insight:** A coil might be unique in temperature (near a known defective coil's thermal profile) but normal in force. Decomposed features let the model detect this partial matching.

### Implementation
```python
# Define stand subspaces (0-indexed column positions in your feature array)
SUBSPACES = {
    'entry_temp':   list(range(3, 9)),    # X4-X9
    'finish_temp':  list(range(9, 16)),   # X10-X16
    'strip_speed':  list(range(16, 23)),  # X17-X23
    'roll_load':    list(range(23, 28)),  # X24-X28
    'roll_force':   list(range(28, 33)),  # X29-X33
    'thickness':    list(range(33, 38)),  # X34-X38
}

subspace_features_train = []
subspace_features_test  = []

for name, cols in SUBSPACES.items():
    X_tr_sub = X_train[:, cols]
    X_te_sub = X_test[:, cols]
    tr_f, te_f = knn_target_encode_oof(X_tr_sub, y_train, X_te_sub, k=10)
    subspace_features_train.append(tr_f.reshape(-1, 1))
    subspace_features_test.append(te_f.reshape(-1, 1))

# Stack: 6 new features
X_sub_train = np.hstack(subspace_features_train)
X_sub_test  = np.hstack(subspace_features_test)
```

This is **the single highest-confidence variant** because:
1. Physical meaning → less likely to be random noise
2. Low dimensionality per subspace → KNN distance meaningful
3. Orthogonal signals from each physical process stage

### Expected Features: 6 (one KNN-TE per stand group)
### Expected AUC lift: +0.01 to +0.025 marginal (highest of all KNN-TE variants)

---

## 5. SCARF Contrastive Embeddings + KNN

### Concept
Train a neural encoder on ALL features (unlabeled, self-supervised) to learn a space where similar coils are close. Then in that learned embedding space, compute:
1. KNN-TE (mean Y of K neighbors in embedding space)
2. Distance to nearest defect in embedding space

SCARF works by corrupting random feature subsets to create "negative views" and training an encoder to maximize similarity between uncorrupted and corrupted views of the same row. The resulting 16-32D embedding captures non-linear feature interactions that PCA and raw-space distance miss.

### Architecture Details (pytorch-scarf)
```python
# pip install torch scarf (or clone github.com/clabrugere/pytorch-scarf)
from scarf.model import SCARF
from scarf.loss import NTXent
import torch

model = SCARF(
    input_dim=49,      # all features
    emb_dim=32,        # embedding dimensionality
    corruption_rate=0.6,
    dropout=0.1
)
optimizer = torch.optim.Adam(model.parameters(), lr=1e-3, weight_decay=1e-4)
loss_fn = NTXent()

# Training loop (~300-500 epochs on ~1500 rows; ~2-5 min on CPU)
for epoch in range(500):
    for batch in dataloader:  # batch_size=128
        emb_anchor, emb_positive = model(batch)
        loss = loss_fn(emb_anchor, emb_positive)
        loss.backward()
        optimizer.step()
        optimizer.zero_grad()

# Extract embeddings
model.eval()
with torch.no_grad():
    X_train_emb = model.encoder(X_train_tensor).numpy()  # (1500, 32)
    X_test_emb  = model.encoder(X_test_tensor).numpy()   # (339, 32)

# Now apply KNN-TE in embedding space
tr_feat, te_feat = knn_target_encode_oof(X_train_emb, y_train, X_test_emb, k=10)
```

**CV-Safety nuance:** SCARF uses NO labels during training — it's self-supervised. Therefore SCARF fit on ALL train data is safe (no target leakage). The KNN-TE step on top still needs OOF fold-safety for the target mean computation.

**Dataset size concern:** With ~1500 train rows and ~22 defects (1.4% rate), SCARF may not learn a dramatically different space from PCA since contrastive learning benefits more from larger unlabeled pools. However, it can capture non-linear correlations between stand temperatures and forces that PCA can't.

**Recommendation:** Train one SCARF model, extract 32-D embeddings, add 3 features: KNN-TE (k=10), distance-to-nearest-defect, and mean-distance-to-top-5-defects. Total: 3 features from SCARF.

### Expected Features: 3-5
### Expected AUC lift: +0.005 to +0.02 (uncertain; depends on whether non-linear structure exists in this dataset)
### Risk: With 1500 rows, SCARF may learn trivial embeddings. Validate by checking if embedding KNN-TE OOF AUC > raw-space KNN-TE.

---

## 6. UMAP 2-D Features

### Concept
Fit UMAP on training features (unsupervised, no labels), project all rows to 2D. Add umap_1 and umap_2 as literal numerical features. GBDT can then find non-linear cluster boundaries in the UMAP manifold that correspond to defect-prone zones.

### CV-Safety
UMAP fit = unsupervised (no Y) → fit on full train is safe. Use `.transform()` for test.

```python
import umap

reducer = umap.UMAP(n_components=2, n_neighbors=15, min_dist=0.1, random_state=42)
X_train_2d = reducer.fit_transform(X_train_scaled)  # (1500, 2)
X_test_2d  = reducer.transform(X_test_scaled)        # (339, 2)

# Add as 2 raw features
# Also: distance to nearest defect in 2D
X_defects_2d = X_train_2d[y_train == 1]
nbrs_2d = NearestNeighbors(n_neighbors=1).fit(X_defects_2d)
dist_train_2d, _ = nbrs_2d.kneighbors(X_train_2d)
dist_test_2d, _  = nbrs_2d.kneighbors(X_test_2d)
```

**Caution:** UMAP is stochastic (fix random_state). UMAP 2D coordinates are NOT stable across random seeds — two runs give different coordinate values (mirror/rotation). Only use the distance feature (distance-to-nearest-defect-in-UMAP-space) as it's seed-invariant, not raw coordinates.

### Expected Features: 1 distance feature (robust) + 2 coords (noisy)
### Expected AUC lift: +0.003 to +0.010 (low confidence for 1500 rows)

---

## 7. Spectral Clustering (SCM-KNN) — Lower Priority

Spectral clustering on the feature similarity graph, then use cluster assignment + distance-to-spectral-centroid as features. This is the highest-compute option with uncertain benefit at 1500 rows — spectral methods shine on larger datasets.

**Verdict:** Skip for now. Soft K-means (Section 2) provides similar "cluster membership" signal at much lower cost. Revisit only if K-means cluster features don't add OOF lift.

---

## 8. CV-Safety Summary

| Feature Type | Leakage Risk | Safe Pattern |
|---|---|---|
| KNN-TE (any space) | HIGH — uses Y | OOF fold-isolated: fit KNN on K-1 folds, encode val fold |
| Soft K-means distances | NONE — uses no Y | Fit on all train, transform train+test |
| PCA subspace features | VERY LOW — unsupervised | Fit PCA on all train OK; KNN-TE on top needs OOF |
| SCARF embeddings | NONE — self-supervised | Fit on all train, use encoder for both |
| UMAP raw coords | NONE — unsupervised | Fit on all train; BUT coordinates are seed-unstable |
| UMAP defect-distance | NONE | Use distance (seed-invariant), not raw coords |
| Stand-subspace KNN-TE | HIGH — uses Y | Same OOF pattern as KNN-TE |

**Outer CV must also be respected:** All feature generation pipelines above must be wrapped inside the existing 5-fold outer loop to avoid inflating OOF AUC estimate.

---

## 9. Integration with Existing 17 Stand-Residuals

V40 has 17 stand-residual features (actual - expected temperature/force per stand). These are domain-engineered signals. The KNN features are NOT a replacement — they are complementary because:

- Stand-residuals capture **absolute deviation from the expected process** (engineering knowledge)
- KNN-TE features capture **"is this coil near previously defective coils?"** (empirical memory)
- Cluster distances capture **"which operational regime is this coil in?"** (regime identity)

**Marginal contribution check:** After adding all KNN features, run feature importance. If KNN-TE and residuals have similar importance, they are truly complementary. If KNN-TE steals all importance from residuals, they are capturing the same variance through different encodings (reduce to top-k).

---

## Top 5 Recommended KNN Feature Variants (Priority Order)

| Rank | Variant | Features Added | Est. AUC Lift | CV-Safe? | Impl Cost |
|---|---|---|---|---|---|
| 1 | **Stand-axis decomposed KNN-TE** (X4-X9, X10-X16, etc.) | 6 | +0.01-0.025 | Yes (OOF) | Low |
| 2 | **Soft K-means cluster distances** (k=8, k=16) | 24 | +0.005-0.015 | Yes (no Y) | Low |
| 3 | **PCA subspace KNN-TE** (10-D, 20-D) | 4-8 | +0.008-0.015 | Yes (OOF) | Low |
| 4 | **SCARF embedding KNN-TE** | 3-5 | +0.005-0.020 | Yes (self-sup) | Medium |
| 5 | **UMAP defect-distance** | 1 | +0.003-0.010 | Yes (no Y) | Low |

**Cumulative estimated OOF AUC lift:** +0.02 to +0.055 above V40's 0.87 baseline.
At best: reaches 0.87 + 0.055 = 0.925 — still short of 0.95, but narrowing the gap.

---

## 10. Combined Implementation Plan

```python
# Step 1: Stand-axis subspace KNN-TE (Priority 1)
# ~5 min to code, ~30s to run
sub_tr, sub_te = build_subspace_knn_te(X_train, y_train, X_test)  # 6 features

# Step 2: Soft K-means (Priority 2)
# ~2 min to code, ~10s to run
km_tr, km_te = soft_kmeans_features(X_train, X_test, k_list=[8, 16])  # 24 features

# Step 3: PCA subspace KNN-TE (Priority 3)
# ~10 min to code, ~1 min to run
pca_tr, pca_te = pca_knn_features(X_train, y_train, X_test, [10, 20])  # 4-8 features

# Step 4: Full-space KNN-TE (baseline comparison)
# Already partly in V40 via proximity; recast as KNN-TE explicitly
full_tr, full_te = knn_target_encode_oof(X_train_scaled, y_train, X_test_scaled, k=10)  # 1 feat

# Step 5: SCARF (Priority 4 — run overnight if Steps 1-4 show lift)
# ~60 min to implement + train
scarf_tr, scarf_te = scarf_knn_features(X_train, y_train, X_test)  # 3-5 features

# Concatenate with existing features
X_train_aug = np.hstack([X_train_existing, sub_tr, km_tr, pca_tr, full_tr.reshape(-1,1)])
X_test_aug  = np.hstack([X_test_existing,  sub_te, km_te, pca_te, full_te.reshape(-1,1)])

# Total new features before SCARF: 6 + 24 + 8 + 1 = 39 new features
```

---

## 11. Risk Assessment: Redundancy with V40

| V40 Existing Feature | KNN Variant | Redundancy Risk | Verdict |
|---|---|---|---|
| Distance to nearest defect (49-D Euclidean) | Stand-subspace KNN-TE | LOW — different definition of "similar" | ADD |
| Distance to nearest defect (49-D Euclidean) | PCA-10 KNN-TE | MEDIUM — PCA keeps top variance (includes original distance's signal) | ADD but check importance |
| Stand residuals (17 features) | Subspace KNN-TE on same stands | LOW — residual = deviation from process norm; KNN-TE = proximity to defective coils | ADD |
| Within-grade z-scores (V11, hurt) | Cluster distances | LOW — z-scores are per-grade, clusters are global | ADD |
| Raw feature values X1-X49 | Full-space KNN-TE | MEDIUM — KNN-TE is a nonlinear re-encoding of the same space | ADD 1 feature, watch importance |

**Conclusion:** No variant is fully redundant with V40. Stand-subspace KNN-TE is most likely to add net new signal.

---

## References

- [TabR: Tabular Deep Learning Meets Nearest Neighbors (ICLR 2024)](https://arxiv.org/abs/2307.14338) — established that KNN neighbor retrieval + label features dramatically improves tabular deep learning
- [SCARF: Self-Supervised Contrastive Learning via Random Feature Corruption](https://arxiv.org/abs/2106.15147) — foundation for contrastive embedding approach
- [pytorch-scarf implementation](https://github.com/clabrugere/pytorch-scarf) — emb_dim=16-32, corruption_rate=0.6, Adam lr=1e-3
- [K-Fold Target Encoding — sklearn TargetEncoder cross-fitting](https://scikit-learn.org/stable/auto_examples/preprocessing/plot_target_encoder_cross_val.html) — OOF leakage prevention pattern
- [UMAP Transform on New Data](https://umap-learn.readthedocs.io/en/latest/transform.html) — correct fit-on-train-transform-both pattern
- [Regularized Target Encoding (Springer 2022)](https://link.springer.com/article/10.1007/s00180-022-01207-6) — benchmarks showing target-based encoders win with GBDT
- [Proximity Weighted Evidential KNN for Imbalanced Data (PMC)](https://pmc.ncbi.nlm.nih.gov/articles/PMC7206335/) — KNN weighting strategy for imbalanced classification

---

## Confidence Assessment

**Confidence: Medium-High**

- KNN-TE fold-safe pattern: High confidence (well-established, sklearn implements it)
- Stand-axis subspace signal: High confidence (physical domain justifies subspace isolation)
- Soft K-means: High confidence (standard FE technique, low risk)
- SCARF lift magnitude: Low-Medium confidence (1500 rows is small for contrastive pre-training; literature results on larger datasets)
- Total cumulative lift reaching 0.95: Low confidence — even with all variants, gap to 0.95 requires the stealth defects to have a KNN signature, which Cycle 4 forensics suggest may not exist in current features

**Critical honest note:** The FINAL_VERDICT document shows the 7 stealth defects in the test set are not separated by any feature tried in V4-V12. KNN features will amplify the signal from the ~15 easy defects but may not crack the stealth 7. The ceiling with these features is likely 0.92-0.94 OOF, not 0.97+.
