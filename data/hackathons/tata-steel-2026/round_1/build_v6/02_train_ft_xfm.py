"""
02_train_ft_xfm.py — 5-fold FT-Transformer training
Architecture: hand-rolled FT-Transformer (Feature Tokenization + Transformer blocks)
Loss: BCEWithLogitsLoss with pos_weight for class imbalance (4.88% positive rate)
Training: AdamW, lr=1e-4, wd=1e-4, up to 200 epochs, early stopping patience=15 on val AUC
"""

import json, time
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import roc_auc_score

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset

V6_DIR = Path("data/hackathons/tata-steel-2026/round_1/build_v6")

# ─── Load prepared data ───────────────────────────────────────────────────────
X_train = np.load(V6_DIR / "X_train_scaled.npy")  # (1352, 59)
X_test  = np.load(V6_DIR / "X_test_scaled.npy")   # (339, 59)
y_train = np.load(V6_DIR / "y_train.npy")          # (1352,)
coil_ids_train = np.load(V6_DIR / "coil_ids_train.npy", allow_pickle=True)
coil_ids_test  = np.load(V6_DIR / "coil_ids_test.npy",  allow_pickle=True)

with open(V6_DIR / "data_prep_meta.json") as f:
    meta = json.load(f)

N_FEATURES  = meta["n_features"]    # 59
POS_WEIGHT  = meta["pos_weight"]    # ~19.5
print(f"Features: {N_FEATURES}, pos_weight: {POS_WEIGHT:.2f}")

# ─── FT-Transformer Architecture ─────────────────────────────────────────────
# Feature Tokenization: each feature -> d_token embedding via linear + bias
# Transformer blocks: Pre-LN MultiHeadAttention + FFN
# CLS token aggregates sequence -> linear head

class FeatureTokenizer(nn.Module):
    """Linear projection of each scalar feature to d_token embedding."""
    def __init__(self, n_features: int, d_token: int):
        super().__init__()
        # Weight: one linear per feature, shape (n_features, d_token)
        self.weight = nn.Parameter(torch.empty(n_features, d_token))
        self.bias   = nn.Parameter(torch.zeros(n_features, d_token))
        nn.init.kaiming_uniform_(self.weight, nonlinearity="linear")

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: (B, F) -> (B, F, d_token)
        return x.unsqueeze(-1) * self.weight.unsqueeze(0) + self.bias.unsqueeze(0)


class TransformerBlock(nn.Module):
    """Pre-LN Transformer block: LN -> MHA -> residual -> LN -> FFN -> residual."""
    def __init__(self, d_token: int, n_heads: int, d_ffn: int,
                 attn_drop: float, ffn_drop: float):
        super().__init__()
        self.norm1 = nn.LayerNorm(d_token)
        self.attn  = nn.MultiheadAttention(d_token, n_heads,
                                           dropout=attn_drop, batch_first=True)
        self.norm2 = nn.LayerNorm(d_token)
        self.ffn   = nn.Sequential(
            nn.Linear(d_token, d_ffn),
            nn.GELU(),
            nn.Dropout(ffn_drop),
            nn.Linear(d_ffn, d_token),
            nn.Dropout(ffn_drop),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: (B, S, d_token)  S = n_features + 1 (CLS token)
        x2 = self.norm1(x)
        a, _ = self.attn(x2, x2, x2)
        x = x + a
        x = x + self.ffn(self.norm2(x))
        return x


class FTTransformer(nn.Module):
    """
    FT-Transformer for binary tabular classification.
    All-numerical variant (no categorical embeddings needed here
    since V5 already label-encoded categoricals).
    """
    def __init__(self, n_features: int, d_token: int = 96,
                 n_blocks: int = 3, n_heads: int = 4,
                 d_ffn: int = 192, attn_drop: float = 0.2,
                 ffn_drop: float = 0.2):
        super().__init__()
        self.tokenizer = FeatureTokenizer(n_features, d_token)
        self.bn_input  = nn.BatchNorm1d(n_features)  # anti-overfit on input

        # CLS token (learnable)
        self.cls_token = nn.Parameter(torch.zeros(1, 1, d_token))
        nn.init.trunc_normal_(self.cls_token, std=0.02)

        self.blocks = nn.ModuleList([
            TransformerBlock(d_token, n_heads, d_ffn, attn_drop, ffn_drop)
            for _ in range(n_blocks)
        ])
        self.norm_out = nn.LayerNorm(d_token)
        self.head     = nn.Linear(d_token, 1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: (B, F)
        x = self.bn_input(x)                          # BN on raw features
        tokens = self.tokenizer(x)                     # (B, F, d_token)
        cls = self.cls_token.expand(x.size(0), -1, -1) # (B, 1, d_token)
        tokens = torch.cat([cls, tokens], dim=1)        # (B, F+1, d_token)
        for block in self.blocks:
            tokens = block(tokens)
        cls_out = self.norm_out(tokens[:, 0, :])        # CLS output
        return self.head(cls_out).squeeze(-1)           # (B,) logits


# ─── Training Helpers ─────────────────────────────────────────────────────────
def compute_score(y_true, y_prob, threshold):
    """(Recall + Precision) / 2 * 100 — competition metric."""
    preds = (y_prob >= threshold).astype(int)
    tp = int(((preds == 1) & (y_true == 1)).sum())
    fp = int(((preds == 1) & (y_true == 0)).sum())
    fn = int(((preds == 0) & (y_true == 1)).sum())
    recall    = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    return (recall + precision) / 2 * 100


def train_one_epoch(model, loader, optimizer, loss_fn, device):
    model.train()
    total_loss = 0.0
    for Xb, yb in loader:
        Xb, yb = Xb.to(device), yb.to(device)
        optimizer.zero_grad()
        logits = model(Xb)
        loss = loss_fn(logits, yb)
        loss.backward()
        nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        total_loss += loss.item() * len(Xb)
    return total_loss / len(loader.dataset)


@torch.no_grad()
def predict_proba(model, X_np, device, batch_size=256):
    model.eval()
    ds = TensorDataset(torch.tensor(X_np, dtype=torch.float32))
    dl = DataLoader(ds, batch_size=batch_size, shuffle=False)
    probs = []
    for (Xb,) in dl:
        logits = model(Xb.to(device))
        probs.append(torch.sigmoid(logits).cpu().numpy())
    return np.concatenate(probs)


# ─── Hyper-parameters ─────────────────────────────────────────────────────────
SEED        = 42
N_FOLDS     = 5
D_TOKEN     = 96
N_BLOCKS    = 3
N_HEADS     = 4
D_FFN       = 192
ATTN_DROP   = 0.2
FFN_DROP    = 0.2
LR          = 1e-4
WEIGHT_DECAY= 1e-4
MAX_EPOCHS  = 200
PATIENCE    = 15
BATCH_SIZE  = 64

torch.manual_seed(SEED)
np.random.seed(SEED)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Device: {device}")

skf = StratifiedKFold(n_splits=N_FOLDS, shuffle=True, random_state=SEED)

oof_probas  = np.zeros(len(y_train), dtype=np.float32)
test_probas = np.zeros((N_FOLDS, len(X_test)), dtype=np.float32)
fold_aucs   = []
fold_scores = []

t0 = time.time()

for fold, (tr_idx, val_idx) in enumerate(skf.split(X_train, y_train)):
    print(f"\n--- Fold {fold+1}/{N_FOLDS} ---")
    X_tr, X_val = X_train[tr_idx], X_train[val_idx]
    y_tr, y_val = y_train[tr_idx], y_train[val_idx]

    tr_ds = TensorDataset(
        torch.tensor(X_tr, dtype=torch.float32),
        torch.tensor(y_tr, dtype=torch.float32)
    )
    tr_dl = DataLoader(tr_ds, batch_size=BATCH_SIZE, shuffle=True, drop_last=False)

    model = FTTransformer(
        n_features=N_FEATURES, d_token=D_TOKEN,
        n_blocks=N_BLOCKS, n_heads=N_HEADS,
        d_ffn=D_FFN, attn_drop=ATTN_DROP, ffn_drop=FFN_DROP
    ).to(device)

    # BCEWithLogitsLoss with pos_weight for class imbalance
    pw = torch.tensor([POS_WEIGHT], dtype=torch.float32).to(device)
    loss_fn = nn.BCEWithLogitsLoss(pos_weight=pw)

    optimizer = optim.AdamW(model.parameters(), lr=LR, weight_decay=WEIGHT_DECAY)
    # Cosine annealing LR schedule
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=MAX_EPOCHS, eta_min=1e-6)

    best_val_auc   = -1.0
    best_val_loss  = float("inf")
    patience_count = 0
    best_state     = None

    for epoch in range(1, MAX_EPOCHS + 1):
        tr_loss = train_one_epoch(model, tr_dl, optimizer, loss_fn, device)
        scheduler.step()

        val_prob = predict_proba(model, X_val, device)
        val_auc  = roc_auc_score(y_val, val_prob)

        if val_auc > best_val_auc + 1e-5:
            best_val_auc   = val_auc
            best_state     = {k: v.cpu().clone() for k, v in model.state_dict().items()}
            patience_count = 0
        else:
            patience_count += 1

        if epoch % 10 == 0:
            print(f"  Ep {epoch:3d}: loss={tr_loss:.4f}  val_AUC={val_auc:.4f}  best={best_val_auc:.4f}  patience={patience_count}")

        if patience_count >= PATIENCE:
            print(f"  Early stop at epoch {epoch}")
            break

    # Restore best weights
    model.load_state_dict(best_state)

    # OOF predictions
    oof_val = predict_proba(model, X_val, device)
    oof_probas[val_idx] = oof_val

    val_auc_final = roc_auc_score(y_val, oof_val)
    # Score at threshold 0.5 and at 0.1
    score_05 = compute_score(y_val, oof_val, 0.5)
    score_01 = compute_score(y_val, oof_val, 0.1)
    fold_aucs.append(val_auc_final)

    # Test predictions
    test_probas[fold] = predict_proba(model, X_test, device)

    print(f"  Fold {fold+1} DONE: AUC={val_auc_final:.4f}  Score@0.5={score_05:.2f}  Score@0.1={score_01:.2f}")
    print(f"  Elapsed: {(time.time()-t0)/60:.1f} min")

# ─── Aggregate ────────────────────────────────────────────────────────────────
test_meta_v6 = test_probas.mean(axis=0)
oof_auc_global = roc_auc_score(y_train, oof_probas)

print(f"\n=== V6 FT-Transformer Results ===")
print(f"Per-fold AUC: {[f'{a:.4f}' for a in fold_aucs]}")
print(f"Mean fold AUC: {np.mean(fold_aucs):.4f} ± {np.std(fold_aucs):.4f}")
print(f"Global OOF AUC: {oof_auc_global:.4f}")
print(f"Total time: {(time.time()-t0)/60:.1f} min")

# ─── Save OOF + test meta ─────────────────────────────────────────────────────
oof_df = pd.DataFrame({
    "CoilID": coil_ids_train,
    "Y":      y_train,
    "oof_v6": oof_probas,
})
oof_df.to_parquet(V6_DIR / "oof_v6.parquet", index=False)

test_df = pd.DataFrame({
    "CoilID":    coil_ids_test,
    "test_meta_v6": test_meta_v6,
})
test_df.to_parquet(V6_DIR / "test_meta_v6.parquet", index=False)

training_summary = {
    "fold_aucs":       fold_aucs,
    "mean_fold_auc":   float(np.mean(fold_aucs)),
    "std_fold_auc":    float(np.std(fold_aucs)),
    "global_oof_auc":  float(oof_auc_global),
    "n_folds":         N_FOLDS,
    "d_token":         D_TOKEN,
    "n_blocks":        N_BLOCKS,
    "n_heads":         N_HEADS,
    "d_ffn":           D_FFN,
    "attn_drop":       ATTN_DROP,
    "ffn_drop":        FFN_DROP,
    "lr":              LR,
    "weight_decay":    WEIGHT_DECAY,
    "max_epochs":      MAX_EPOCHS,
    "patience":        PATIENCE,
    "pos_weight":      POS_WEIGHT,
    "total_train_min": round((time.time()-t0)/60, 2),
}
with open(V6_DIR / "v6_training_summary.json", "w") as f:
    json.dump(training_summary, f, indent=2)

print("02_train_ft_xfm.py DONE")
print(f"  oof_v6.parquet: {len(oof_df)} rows")
print(f"  test_meta_v6.parquet: {len(test_df)} rows")
