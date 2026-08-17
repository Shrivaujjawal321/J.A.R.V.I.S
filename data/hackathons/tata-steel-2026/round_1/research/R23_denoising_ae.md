# R23 — Denoising Autoencoder Pretraining + Modern SSL Alternatives
**Tata Steel Defect Detection | Banked: 72.83 LB | Date: 2026-05-24**

---

## Verdict Up Front

DAE pretraining on N=1691 is **viable but high-risk**. The original Porto trick worked because 595K rows gave the DAE rich distributional coverage. At 1691 rows the DAE will memorize rather than generalize unless architecture is aggressively regularized. The modern alternative **SCARF** is better-suited: contrastive corruption works on small N, has two working PyTorch repos, and the ICLR 2022 paper showed gains even on OpenML datasets with under 1000 rows. Recommendation: **implement SCARF first (lower risk, cleaner code), then DAE as a second attempt**.

---

## 1. Does DAE Work on N=1691? (Literature Evidence)

### What Porto's DAE actually needed

- Architecture: 221-1500-1500-1500-221 (221 input features, three 1500-unit hidden layers).
- Corruption: 15% swap noise (replace feature value with random value from same column in another row).
- Dataset used for DAE: **train + test combined** (595K train + 892K test = 1.49M rows for the autoencoder). The "larger the test set, the better" was an explicit observation from Michael Jahrer.
- Embedding extraction: concatenate all three hidden layer activations → ~4,500 new features fed into downstream NNs.

### At N=1691

Three failure modes become serious:

| Risk | Mechanism | Severity |
|------|-----------|----------|
| Memorization | 1691 rows, 1500-unit hidden layer = model is massively wider than data. It will learn identity mapping, not representations. | HIGH |
| Collapse | With too few samples, swap noise creates trivial negatives — the DAE just learns mean imputation. | MEDIUM |
| Overfitting downstream | 4,500 DAE features from 1691 rows is a ~2.6× feature-to-sample ratio inversion — LightGBM will overfit these immediately. | HIGH |

### Literature verdict

- **Are Large-scale Datasets Necessary for Self-Supervised Pre-Training? (arXiv 2112.10740):** DAEs are *more sample-efficient* than joint-embedding (contrastive) methods and can work on target-task data directly. However "more efficient than ImageNet-scale" ≠ "works at 1691 rows." The paper's smallest dataset is still >>5K.
- **Attention vs Contrastive Learning (arXiv 2401.04266):** Benchmarked 28 datasets including Blood-Transfusion (748 rows), ILPD (583 rows), Diabetes (768 rows). Contrastive methods ranked top-3 in only 3/16 hard-dataset cases. **DNN-AE** (basic autoencoder pretraining) was "20× faster" and competitive on easy datasets. For hard/imbalanced datasets SAINT-class models were better.
- **Kaggle Playground + competition history:** DAE with swap noise appears repeatedly in Tabular Playground Series solutions, but typically N > 50K. At N < 2K there is no published competition evidence of DAE giving a clean AUC lift.
- **Semi-supervised SSL:** TabTransformer MLM/RTD pretraining shows **+2.1% mean AUC** over baselines — but in settings with many unlabeled samples and few labels. Our setting (1352 labeled + 339 "unlabeled" test) is closer to fully-supervised than semi-supervised.

**Bottom line:** DAE *can* work at N=1691 but only if: (a) architecture is drastically shrunk (256-128-256, not 1500s), (b) dropout is aggressive (0.4–0.5), (c) you include test rows in the DAE training pool (adds 20% more rows). Expected OOF AUC lift: **+0.003 to +0.010** if it works; **0 or negative** if it memorizes.

---

## 2. Modern SSL Alternatives — Ranked

### Rank 1: SCARF (Recommended)
**Paper:** SCARF: Self-Supervised Contrastive Learning using Random Feature Corruption (ICLR 2022)
**Repo:** https://github.com/clabrugere/pytorch-scarf

**How it works:**
- For each sample, creates a "corrupted view" by replacing a random subset of features with values drawn from the marginal distribution of that feature (i.e., random row from same column — identical corruption mechanism to Porto's swap noise).
- Encoder encodes both anchor and corrupted view → NT-Xent contrastive loss maximizes agreement between anchor and its view, minimizes agreement with other samples' views.
- Projection head used only during pretraining; encoder's output (not projection) used as embedding for downstream.

**Why better than DAE for small N:**
- Contrastive learning is harder to collapse on small datasets than reconstruction (the negative examples force the encoder to discriminate, not just reconstruct mean).
- No decoder to memorize — encoder is the bottleneck. Much fewer parameters.
- ICLR 2022 benchmark: 69 OpenML-CC18 datasets, SCARF outperformed autoencoder-based learning on **50/69 datasets** (statistically significant on 24). Included datasets with <1000 rows.
- Corruption rate 0.6 used in reference implementations (vs Porto's 0.15). Higher corruption = harder pretext task = better representations at small N.

**Downstream use (two paths):**
1. **Embed-then-GBDT:** Freeze encoder, run all 1691 rows through it, get 64-dim (or 128-dim) embedding, concatenate with original features → feed to LightGBM/XGBoost.
2. **Embed-then-NN (finetune):** Use encoder as backbone, add linear head, finetune with cross-entropy + focal loss on labeled 1352 rows.

---

### Rank 2: DAE (Porto pattern, downsized)
Covered in depth above. Use architecture 256-128-256, dropout 0.4, swap noise 0.15, 50-100 epochs, AdamW + OneCycleLR. Include test 339 rows in DAE training. Extract bottleneck (128-dim) as embedding. Concat with original features.

---

### Rank 3: VIME (NeurIPS 2020)
**What it does:** Two pretext tasks — (a) mask estimation (predict which features were corrupted), (b) value imputation (reconstruct corrupted values). Both tasks together produce richer gradients than reconstruction alone.

**Why ranked 3rd:**
- More complex to implement (two-head loss).
- Designed for settings where categorical feature embeddings are uniform (VIME doesn't handle mixed categorical+continuous well out of the box).
- Small-dataset evidence weaker than SCARF.
- No corruption of categorical features in the original paper — our features include categorical-encoded cols that VIME would mishandle without modification.

---

## 3. Concrete Python Implementation — SCARF (PyTorch, ~50 lines)

```python
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader, TensorDataset
import numpy as np

# ── Architecture ──────────────────────────────────────────────────────────────
class SCARFEncoder(nn.Module):
    def __init__(self, input_dim, emb_dim=128, dropout=0.1):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, 256), nn.BatchNorm1d(256), nn.ReLU(), nn.Dropout(dropout),
            nn.Linear(256, 256), nn.BatchNorm1d(256), nn.ReLU(), nn.Dropout(dropout),
            nn.Linear(256, emb_dim),
        )
        self.proj = nn.Sequential(
            nn.Linear(emb_dim, 128), nn.ReLU(),
            nn.Linear(128, 64),
        )

    def forward(self, x):
        z = self.net(x)
        return z, self.proj(z)   # (embedding, projection)

# ── Corruption (swap noise from marginal) ─────────────────────────────────────
def corrupt(x: torch.Tensor, marginals: torch.Tensor, rate: float = 0.6):
    """Replace `rate` fraction of features with random draws from marginal."""
    mask = torch.rand_like(x) < rate
    idx = torch.randint(0, x.size(0), (x.size(0),), device=x.device)
    corrupted = torch.where(mask, marginals[idx], x)
    return corrupted

# ── NT-Xent Loss ──────────────────────────────────────────────────────────────
def nt_xent(z1, z2, temperature=0.5):
    z1 = F.normalize(z1, dim=1)
    z2 = F.normalize(z2, dim=1)
    N = z1.size(0)
    z = torch.cat([z1, z2], dim=0)                      # (2N, D)
    sim = torch.mm(z, z.T) / temperature                 # (2N, 2N)
    sim.fill_diagonal_(-1e9)                              # exclude self
    labels = torch.cat([torch.arange(N, 2*N), torch.arange(0, N)]).to(z.device)
    return F.cross_entropy(sim, labels)

# ── Training Loop ─────────────────────────────────────────────────────────────
def pretrain_scarf(X_all: np.ndarray, emb_dim=128, epochs=200, lr=1e-3, batch=256):
    """X_all = train + test concatenated (1691 rows after scaling), returns encoder."""
    X_t = torch.tensor(X_all, dtype=torch.float32)
    marginals = X_t                                       # draw corruption from full pool
    loader = DataLoader(TensorDataset(X_t), batch_size=batch, shuffle=True, drop_last=True)
    
    model = SCARFEncoder(X_all.shape[1], emb_dim=emb_dim).cuda()
    opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=epochs)

    model.train()
    for ep in range(epochs):
        total = 0.0
        for (x,) in loader:
            x = x.cuda()
            x_corrupt = corrupt(x, marginals.cuda(), rate=0.6)
            _, z_anchor = model(x)
            _, z_corrupt = model(x_corrupt)
            loss = nt_xent(z_anchor, z_corrupt)
            opt.zero_grad(); loss.backward(); opt.step()
            total += loss.item()
        sched.step()
        if ep % 50 == 0:
            print(f"Ep {ep}: loss={total/len(loader):.4f}")
    return model

# ── Embedding Extraction ──────────────────────────────────────────────────────
@torch.no_grad()
def get_embeddings(model, X: np.ndarray, batch=512):
    model.eval()
    X_t = torch.tensor(X, dtype=torch.float32)
    embs = []
    for i in range(0, len(X_t), batch):
        z, _ = model(X_t[i:i+batch].cuda())  # use encoder output, not projection
        embs.append(z.cpu())
    return torch.cat(embs).numpy()

# ── Usage ─────────────────────────────────────────────────────────────────────
# from sklearn.preprocessing import StandardScaler
# scaler = StandardScaler()
# X_train_scaled = scaler.fit_transform(X_train)
# X_test_scaled  = scaler.transform(X_test)
# X_all_scaled   = np.vstack([X_train_scaled, X_test_scaled])   # 1691 rows for DAE pool
#
# encoder = pretrain_scarf(X_all_scaled, emb_dim=128, epochs=300, lr=5e-4, batch=128)
#
# emb_train = get_embeddings(encoder, X_train_scaled)           # (1352, 128)
# emb_test  = get_embeddings(encoder, X_test_scaled)            # (339, 128)
#
# # Path A: concat and feed to LightGBM
# X_train_aug = np.hstack([X_train_scaled, emb_train])          # (1352, input_dim+128)
# X_test_aug  = np.hstack([X_test_scaled,  emb_test])
# lgbm.fit(X_train_aug, y_train, ...)
#
# # Path B: finetune encoder + linear head
# # head = nn.Linear(128, 1); train with focal loss on X_train_scaled, y_train
```

**Key hyperparameters for N=1691:**
- `emb_dim=128` (not 512 — too wide for 1691 rows)
- `epochs=300` with cosine schedule (Porto used 200 epochs; we run slightly longer to compensate for smaller N)
- `batch=128` (not 256 — full dataset is 1691 rows, batch=128 = ~13 steps/epoch, keeps variety)
- `corruption_rate=0.6` (SCARF default; higher than Porto's 0.15 because contrastive needs harder negatives)
- `dropout=0.1` in encoder (low — BatchNorm already regularizes, don't double-penalize small N)
- **Include test 339 rows in pretraining pool** (no labels needed — this is the Porto transductive trick applied to SCARF)

---

## 4. Test Set Inclusion (Porto Transductive Trick)

Porto included test features (unlabeled) in the DAE training pool. This is legal in Kaggle/competition settings and adds information about the test distribution to the encoder. We have 339 test rows. Steps:

1. Scale `X_train + X_test` together using `StandardScaler.fit(X_train)` then `transform` both.
2. Stack for SCARF pretraining: `X_all = vstack([X_train_scaled, X_test_scaled])` → 1691 rows.
3. SCARF pretrains on these 1691 rows (no labels needed).
4. Extract embeddings separately for train (1352) and test (339).
5. Downstream supervised training uses only the 1352 train embeddings with labels.

This is a +20% data boost for the encoder. With our N=1691, every row counts.

---

## 5. Downstream Paths

### Path A: Embed-then-GBDT
- Concat `[scaled_features, 128-dim SCARF embedding]` for each sample.
- Feed augmented feature matrix to LightGBM with current best hyperparameters (focal loss objective, class_weight).
- Risk: 128 extra features from an encoder trained on 1691 rows. If the embeddings carry noise, LGBM will overfit them. Mitigate with `colsample_bytree=0.5` and `min_child_samples=20`.
- Expected lift: **+0.003 to +0.008 AUC** if representations are clean. Zero if encoder collapsed.
- **Verification gate:** Check that SCARF training loss actually decreases below 1.0 before extracting embeddings. If loss stays flat → encoder collapsed → skip this path.

### Path B: Embed-then-NN (finetune)
- Freeze encoder (or use low LR = 1e-5 for encoder, 1e-3 for head).
- Add `nn.Linear(128, 1)` head + sigmoid.
- Train with `BCEWithLogitsLoss` + class `pos_weight` to handle imbalance.
- Focal loss alternative: `alpha=0.25, gamma=2` (already proven in your stack).
- 5-fold CV OOF on train 1352 rows.
- Expected lift: probably comparable to current MLP baselines if embeddings are good, but a new signal source for stacking.

---

## 6. Expected OOF AUC Lift — Honest Assessment

| Scenario | Expected AUC delta | Confidence |
|----------|-------------------|------------|
| SCARF pretraining works, Path A (concat → LGBM) | +0.003 to +0.010 | Low-Medium |
| SCARF pretraining works, Path B (finetune NN) | +0.002 to +0.008 | Low-Medium |
| DAE pretraining works (Porto architecture scaled down) | +0.002 to +0.007 | Low |
| SCARF encoder collapses (loss doesn't decrease) | 0 or negative | — |
| DAE memorizes (reconstruction loss hits zero immediately) | 0 or negative | — |
| Both work and are stacked (SCARF embed + DAE embed → stacking layer) | +0.008 to +0.015 | Low |

**These are not big lifts.** At 72.83 LB you are in territory where every +0.005 matters. But be aware: the variance at N=1352 labeled rows means +0.005 CV might be noise. LB is the only truth.

---

## 7. Risk Assessment

| Risk | Likelihood | Mitigation |
|------|-----------|------------|
| Encoder collapse (SCARF loss stays at ~ln(N)) | Medium | Increase corruption rate to 0.7; reduce batch to 64 |
| DAE memorization (reconstruction loss → 0 immediately) | High | Reduce layers to 1; add Dropout(0.5) |
| Embeddings add noise to LGBM | Medium | Use `colsample_bytree=0.5`; validate with OOF before test submission |
| Embedding dimension too large for N | Medium | Try emb_dim=64 first; add L2 regularization |
| Preprocessing mismatch (test leakage into scaler) | Low | Fit scaler only on train, transform test separately |
| Implementation bugs in contrastive loss | Low | Use `clabrugere/pytorch-scarf` repo as reference — it is clean and tested |

---

## 8. Recommended Execution Order

1. **Implement SCARF pretraining** using code above. Train on X_all (1691 rows). Verify loss curve goes down and levels off around 4.0–5.5 (not stays at ln(N)).
2. **Path A first:** Concat embeddings with scaled features → retrain LGBM baseline. Check OOF AUC vs 72.83 (CV equivalent).
3. **If Path A lifts:** Submit. If not, try `emb_dim=64`, try `corruption_rate=0.7`.
4. **Path B second:** Finetune SCARF encoder + linear head with focal loss, 5-fold CV. Add to stacking ensemble.
5. **DAE as third attempt:** Only if SCARF gives uplift and time remains. Use 256-128-256 architecture.
6. **Never substitute** representation learning for feature engineering — these are additive.

---

## Sources

- [Porto Seguro Winning Solution — fast.ai forum (Jahrer)](https://forums.fast.ai/t/porto-seguro-winning-solution-representation-learning/8499) — primary source for Porto DAE architecture details
- [SCARF paper — arXiv 2106.15147](https://arxiv.org/abs/2106.15147) — ICLR 2022, 69-dataset OpenML benchmark
- [clabrugere/pytorch-scarf](https://github.com/clabrugere/pytorch-scarf) — clean SCARF implementation, NT-Xent loss, corruption strategy
- [Attention vs Contrastive Learning — arXiv 2401.04266](https://arxiv.org/html/2401.04266v1) — benchmarks SCARF/SAINT/DNN-AE on 28 datasets including sub-1000-row sets
- [PyTorch Tabular DAE Tutorial](https://pytorch-tabular.readthedocs.io/en/latest/tutorials/08-Self-Supervised%20Learning-DAE/) — DAE implementation reference, swap vs zero noise, fine-tuning workflow
- [Are Large-scale Datasets Necessary for SSL — arXiv 2112.10740](https://arxiv.org/pdf/2112.10740) — sample efficiency of DAE vs contrastive methods
- [TabTransformer semi-supervised — arXiv 2012.06678](https://arxiv.org/pdf/2012.06678) — +2.1% AUC in semi-supervised settings with unlabeled data
- [Revisiting Pretraining Objectives — arXiv 2207.03208](https://arxiv.org/pdf/2207.03208) — comparison of pretraining losses for tabular deep learning
