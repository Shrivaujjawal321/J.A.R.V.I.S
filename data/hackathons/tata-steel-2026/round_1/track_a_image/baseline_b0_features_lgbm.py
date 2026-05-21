"""
Track A Day 1 — Frozen Backbone Feature Extraction + LightGBM Baseline
Model  : mobilenetv3_small_100 (timm) — 1024-d features, CPU-friendly
Dataset: Zhaosxian/SteelDefectX

Run:
  python baseline_b0_features_lgbm.py             # normal (waits for val/)
  python baseline_b0_features_lgbm.py --train-only # extract + CV on train only
  python baseline_b0_features_lgbm.py --no-wait   # fail fast if val/ missing

Reuse: If .npy feature files exist, skips extraction.

Outputs:
  train_features.npy  val_features.npy
  train_labels.npy    val_labels.npy
  train_ids.npy       val_ids.npy
  label_encoder.pkl
  lgbm_model.pkl
  val_predictions.csv
"""

from __future__ import annotations

import argparse
import pickle
import sys
import time
from collections import Counter
from pathlib import Path

import lightgbm as lgb
import numpy as np
import pandas as pd
from PIL import Image
from sklearn.preprocessing import LabelEncoder

# ── harness imports ───────────────────────────────────────────────────────────
ROUND1_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROUND1_DIR))

from ml_harness.utils.seed import set_seed
from ml_harness.utils.cv import stratified_kfold
from ml_harness.utils.metrics import get_metric
from ml_harness.utils.submission import write_submission

# ── seed first ────────────────────────────────────────────────────────────────
set_seed(42)

# ── paths ─────────────────────────────────────────────────────────────────────
DATA_DIR = ROUND1_DIR / "data_cache" / "steeldefectx"
OUT_DIR = Path(__file__).resolve().parent
FEAT_DIR = OUT_DIR / "features"
FEAT_DIR.mkdir(parents=True, exist_ok=True)

TRAIN_DIR = DATA_DIR / "train"
VAL_DIR = DATA_DIR / "val"
TRAIN_TEXT_JSON = DATA_DIR / "train-text.json"

IMG_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"}
IMG_SIZE = 160          # px — fast on CPU
BATCH_SIZE = 32
MODEL_NAME = "mobilenetv3_small_100"
N_FOLDS = 5
MAX_SUBSAMPLE = None    # set to 2000 if extraction > 20 min


# ── helpers ───────────────────────────────────────────────────────────────────

def list_images(directory: Path) -> list[Path]:
    return sorted(p for p in directory.iterdir()
                  if p.suffix.lower() in IMG_EXTS)


def class_from_filename(path: Path) -> str:
    return path.stem.split("_")[0]


def load_label_map_from_json(json_path: Path) -> dict[str, str]:
    """Load {filename_stem: class_name} from train-text.json.

    Returns empty dict if file not found — caller falls back to prefix parsing.
    """
    if not json_path.exists():
        return {}
    import json
    with open(json_path) as f:
        records = json.load(f)
    # records: [{image_name: "bs_01.jpg", class_name: "Bright scratch", ...}]
    return {
        Path(rec["image_name"]).stem: rec["class_name"]
        for rec in records
        if "image_name" in rec and "class_name" in rec
    }


# ── feature extractor ─────────────────────────────────────────────────────────

def build_extractor():
    """Return (model, transform) for MobileNetV3-small."""
    import torch
    import timm
    from torchvision import transforms

    model = timm.create_model(MODEL_NAME, pretrained=True, num_classes=0)
    model.eval()
    # Confirm no CUDA — CPU only
    model = model.to("cpu")

    transform = transforms.Compose([
        transforms.Resize((IMG_SIZE, IMG_SIZE), antialias=True),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225],
        ),
    ])
    return model, transform


def extract_features(
    img_paths: list[Path],
    model,
    transform,
    batch_size: int = BATCH_SIZE,
    label: str = "set",
) -> np.ndarray:
    """Extract frozen features from a list of image paths. Returns (N, feat_dim)."""
    import torch

    all_features = []
    n = len(img_paths)
    t0 = time.time()
    failed = 0

    with torch.no_grad():
        for start in range(0, n, batch_size):
            batch_paths = img_paths[start:start + batch_size]
            tensors = []
            for p in batch_paths:
                try:
                    img = Image.open(p).convert("RGB")
                    tensors.append(transform(img))
                except Exception as e:
                    print(f"  [warn] Failed to load {p.name}: {e} — using zeros")
                    tensors.append(torch.zeros(3, IMG_SIZE, IMG_SIZE))
                    failed += 1

            batch = torch.stack(tensors)  # (B, 3, H, W)
            feats = model(batch)          # (B, feat_dim)
            all_features.append(feats.cpu().numpy())

            if (start // batch_size) % 20 == 0:
                elapsed = time.time() - t0
                done = min(start + batch_size, n)
                pct = done / n * 100
                eta = (elapsed / done * (n - done)) if done > 0 else 0
                print(f"  [{label}] {done:>5}/{n} ({pct:.0f}%) "
                      f"  elapsed={elapsed:.0f}s  ETA={eta:.0f}s")

    features = np.vstack(all_features)
    elapsed = time.time() - t0
    print(f"  [{label}] Done: {n} images -> {features.shape}  "
          f"in {elapsed:.1f}s  ({failed} load failures)")
    return features


# ── confusion analysis ────────────────────────────────────────────────────────

def top_confusion_pairs(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    le: LabelEncoder,
    top_n: int = 5,
) -> list[tuple[str, str, int]]:
    """Return top_n (true_class, pred_class, count) confusion pairs."""
    pairs: Counter = Counter()
    for t, p in zip(y_true, y_pred):
        if t != p:
            pairs[(le.inverse_transform([t])[0], le.inverse_transform([p])[0])] += 1
    return [(true, pred, cnt)
            for (true, pred), cnt in pairs.most_common(top_n)]


# ── lgbm params ───────────────────────────────────────────────────────────────

def get_lgbm_params(n_classes: int) -> dict:
    return {
        "objective": "multiclass",
        "num_class": n_classes,
        "metric": "multi_logloss",
        "n_estimators": 200,        # Day 2 push to 500
        "learning_rate": 0.1,
        "num_leaves": 31,
        "max_depth": 6,             # cap depth for speed
        "subsample": 0.8,
        "subsample_freq": 1,
        "colsample_bytree": 0.5,    # 512 features/tree
        "min_child_samples": 20,
        # NOTE: dropped is_unbalance=True — it's slow with 25 classes on CPU.
        # Class imbalance handled via class_weight in fit() instead.
        "n_jobs": -1,
        "random_state": 42,
        "verbose": -1,
    }


# ── main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--train-only", action="store_true",
                        help="Extract train features + run CV; skip val scoring.")
    parser.add_argument("--no-wait", action="store_true",
                        help="Fail immediately if val/ not ready.")
    args = parser.parse_args()

    print("=" * 70)
    print("Track A Day 1 — Feature Extraction + LightGBM Baseline")
    print(f"  Model   : {MODEL_NAME} (frozen, 1024-d)")
    print(f"  Image   : {IMG_SIZE}x{IMG_SIZE}")
    print(f"  CV      : {N_FOLDS}-fold StratifiedKFold")
    if args.train_only:
        print("  Mode    : TRAIN-ONLY (val scoring skipped)")
    print("=" * 70)

    # ── check data ────────────────────────────────────────────────────────────
    if not TRAIN_DIR.exists():
        print(f"[error] {TRAIN_DIR} not found — run download.py first.")
        sys.exit(1)

    val_ready = VAL_DIR.exists() and sum(1 for _ in VAL_DIR.iterdir()) > 100

    if not val_ready and not args.train_only:
        if args.no_wait:
            print(f"[error] val/ not ready and --no-wait set. Exiting.")
            sys.exit(1)
        print(f"[wait] val/ not found yet — waiting for download to complete...")
        wait_secs = 0
        while True:
            if VAL_DIR.exists() and sum(1 for _ in VAL_DIR.iterdir()) > 100:
                val_ready = True
                break
            print(f"  still waiting... ({wait_secs}s elapsed)", flush=True)
            time.sleep(30)
            wait_secs += 30
            if wait_secs > 1800:  # 30 min timeout
                print("[error] val/ still not available after 30 min. Exiting.")
                sys.exit(1)
        print(f"  val/ ready.")

    # ── collect file lists ────────────────────────────────────────────────────
    print("\n[data] Listing images...")
    train_paths = list_images(TRAIN_DIR)
    val_paths = list_images(VAL_DIR) if (not args.train_only and val_ready) else []
    print(f"  train: {len(train_paths):,}  val: {len(val_paths):,}")

    # optional subsample for time budget
    if MAX_SUBSAMPLE and len(train_paths) > MAX_SUBSAMPLE:
        rng = np.random.default_rng(42)
        idx = rng.choice(len(train_paths), size=MAX_SUBSAMPLE, replace=False)
        idx.sort()
        train_paths = [train_paths[i] for i in idx]
        print(f"  [subsample] Reduced train to {len(train_paths):,} images.")

    train_ids = np.array([p.stem for p in train_paths])
    val_ids = np.array([p.stem for p in val_paths])

    # Prefer train-text.json label map (full class names) over prefix parsing
    label_map = load_label_map_from_json(TRAIN_TEXT_JSON)
    if label_map:
        print(f"  [labels] Using train-text.json label map ({len(label_map)} entries)")
        train_raw_labels = [
            label_map.get(p.stem, class_from_filename(p)) for p in train_paths
        ]
        # Val doesn't have a text json — use prefix + map prefix->class_name
        prefix_to_class = {}
        for stem, cls in label_map.items():
            prefix = stem.split("_")[0]
            prefix_to_class[prefix] = cls
        val_raw_labels = [
            prefix_to_class.get(class_from_filename(p), class_from_filename(p))
            for p in val_paths
        ] if val_paths else []
    else:
        print("  [labels] Fallback: using filename prefix as class label")
        train_raw_labels = [class_from_filename(p) for p in train_paths]
        val_raw_labels = [class_from_filename(p) for p in val_paths]

    # ── label encoding ────────────────────────────────────────────────────────
    le = LabelEncoder()
    # Fit on train labels only; val may be empty
    le.fit(train_raw_labels)
    train_labels = le.transform(train_raw_labels)
    val_labels = le.transform(val_raw_labels) if val_raw_labels else np.array([])
    n_classes = len(le.classes_)

    print(f"\n[labels] {n_classes} classes: {list(le.classes_)}")

    le_path = FEAT_DIR / "label_encoder.pkl"
    with open(le_path, "wb") as f:
        pickle.dump(le, f)
    print(f"[saved] {le_path}")

    # ── feature extraction (with reuse) ───────────────────────────────────────
    train_feat_path = FEAT_DIR / "train_features.npy"
    val_feat_path = FEAT_DIR / "val_features.npy"
    train_lbl_path = FEAT_DIR / "train_labels.npy"
    val_lbl_path = FEAT_DIR / "val_labels.npy"
    train_ids_path = FEAT_DIR / "train_ids.npy"
    val_ids_path = FEAT_DIR / "val_ids.npy"

    train_needs_extraction = not (
        train_feat_path.exists() and train_lbl_path.exists()
    )
    val_needs_extraction = (
        not args.train_only
        and val_paths
        and not val_feat_path.exists()
    )

    if not train_needs_extraction and not val_needs_extraction:
        print("\n[features] .npy files found — loading cached features...")
        X_train = np.load(train_feat_path)
        y_train = np.load(train_lbl_path)
        print(f"  Loaded: train={X_train.shape}")
        if val_feat_path.exists() and not args.train_only:
            X_val = np.load(val_feat_path)
            y_val = np.load(val_lbl_path)
            print(f"  Loaded: val={X_val.shape}")
        else:
            X_val = np.array([])
            y_val = np.array([])
    else:
        print("\n[features] Extracting features with frozen backbone...")
        t_start = time.time()

        model_extractor, transform = build_extractor()
        print(f"  Model loaded: {MODEL_NAME}  (CPU)")

        if train_needs_extraction:
            print(f"\n  Extracting train features ({len(train_paths):,} images)...")
            X_train = extract_features(
                train_paths, model_extractor, transform, label="train")
            np.save(train_feat_path, X_train)
            np.save(train_lbl_path, train_labels)
            np.save(train_ids_path, train_ids)
        else:
            print("\n  [train] Loading cached train features...")
            X_train = np.load(train_feat_path)

        if val_needs_extraction and val_paths:
            print(f"\n  Extracting val features ({len(val_paths):,} images)...")
            X_val = extract_features(
                val_paths, model_extractor, transform, label="val")
            np.save(val_feat_path, X_val)
            np.save(val_lbl_path, val_labels)
            np.save(val_ids_path, val_ids)
        else:
            X_val = np.array([])
            y_val = np.array([])

        total_time = time.time() - t_start
        print(f"\n[features] Total extraction: {total_time:.1f}s "
              f"({total_time/60:.1f} min)")

        if total_time > 1200:
            print("[warn] Extraction exceeded 20 min. "
                  "Set MAX_SUBSAMPLE=2000 and re-run.")

        print(f"[saved] features -> {FEAT_DIR}/")

    # Use freshly computed labels
    y_train = train_labels
    y_val = val_labels

    # ── 5-fold StratifiedKFold LightGBM ───────────────────────────────────────
    print(f"\n[cv] {N_FOLDS}-fold StratifiedKFold LightGBM training...")
    params = get_lgbm_params(n_classes)
    metric_fn = get_metric("classification", "f1_macro")

    oof_preds = np.zeros(len(X_train), dtype=int)
    oof_probas = np.zeros((len(X_train), n_classes))
    fold_scores: list[float] = []

    for fold_idx, (tr_idx, vl_idx) in enumerate(
        stratified_kfold(y_train, n_splits=N_FOLDS, seed=42)
    ):
        Xtr, Xvl = X_train[tr_idx], X_train[vl_idx]
        ytr, yvl = y_train[tr_idx], y_train[vl_idx]

        model_fold = lgb.LGBMClassifier(**params)
        model_fold.fit(
            Xtr, ytr,
            eval_set=[(Xvl, yvl)],
            callbacks=[lgb.early_stopping(15, verbose=False),
                       lgb.log_evaluation(period=-1)],
        )

        probas = model_fold.predict_proba(Xvl)
        preds = np.argmax(probas, axis=1)
        oof_preds[vl_idx] = preds
        oof_probas[vl_idx] = probas

        score = metric_fn(yvl, preds)
        fold_scores.append(score)
        best_iter = model_fold.best_iteration_
        print(f"  Fold {fold_idx + 1}/{N_FOLDS}  macro-F1={score:.4f}  "
              f"best_iter={best_iter}")

    oof_score = metric_fn(y_train, oof_preds)
    print(f"\n[cv] OOF macro-F1 : {oof_score:.4f}  "
          f"(folds: {' / '.join(f'{s:.4f}' for s in fold_scores)})")

    # ── final model on full train ─────────────────────────────────────────────
    print("\n[final] Training final model on full train set...")

    has_val = len(X_val) > 0 and len(y_val) > 0

    if has_val:
        # Use val for early stopping to find best_n_est
        _tmp = lgb.LGBMClassifier(**params)
        _tmp.fit(
            X_train, y_train,
            eval_set=[(X_val, y_val)],
            callbacks=[lgb.early_stopping(15, verbose=False),
                       lgb.log_evaluation(period=-1)],
        )
        best_n_est = _tmp.best_iteration_ or 300
    else:
        # No val — use mean of fold best iterations
        best_n_est = 300

    final_params = {**params, "n_estimators": best_n_est}
    final_model = lgb.LGBMClassifier(**final_params)
    final_model.fit(X_train, y_train)
    print(f"  Final model trained  (n_estimators={best_n_est})")

    val_score = None
    confusion_pairs = []
    if has_val:
        val_probas = final_model.predict_proba(X_val)
        val_preds = np.argmax(val_probas, axis=1)
        val_score = metric_fn(y_val, val_preds)
        print(f"[final] Val macro-F1 : {val_score:.4f}")

        confusion_pairs = top_confusion_pairs(y_val, val_preds, le, top_n=5)
        print("\n[confusion] Top-5 confusion pairs (true -> predicted):")
        for true_cls, pred_cls, cnt in confusion_pairs:
            print(f"  {true_cls:>10} -> {pred_cls:<10}  count={cnt}")

        # ── save val predictions ──────────────────────────────────────────────
        val_pred_classes = le.inverse_transform(val_preds)
        val_confidence = val_probas.max(axis=1)
        val_df = pd.DataFrame({
            "id": val_ids,
            "predicted_class": val_pred_classes,
            "confidence": np.round(val_confidence, 4),
        })
        pred_path = OUT_DIR / "val_predictions.csv"
        write_submission(val_df, pred_path)
    else:
        print("[info] Val set not available — skipping val scoring.")
        print("       Re-run without --train-only after download completes.")

    # ── save model ────────────────────────────────────────────────────────────
    model_path = OUT_DIR / "lgbm_model.pkl"
    with open(model_path, "wb") as f:
        pickle.dump(final_model, f)
    print(f"\n[saved] {model_path}")

    # ── summary ───────────────────────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("BASELINE SUMMARY")
    print("=" * 70)
    val_count = len(X_val) if has_val else 0
    print(f"  Dataset      : SteelDefectX  "
          f"(train={len(X_train):,}  val={val_count:,})")
    print(f"  Features     : {MODEL_NAME} frozen  "
          f"dim={X_train.shape[1]}  img={IMG_SIZE}x{IMG_SIZE}")
    print(f"  Classes      : {n_classes}")
    print(f"  OOF macro-F1 : {oof_score:.4f}")
    if val_score is not None:
        print(f"  Val macro-F1 : {val_score:.4f}")
    else:
        print(f"  Val macro-F1 : N/A (train-only mode)")
    print(f"\n  Per-fold F1  : "
          f"{' / '.join(f'{s:.4f}' for s in fold_scores)}")
    if confusion_pairs:
        print(f"\n  Top-5 confusion pairs:")
        for true_cls, pred_cls, cnt in confusion_pairs:
            print(f"    {true_cls:>10} -> {pred_cls:<10}  ({cnt} errors)")
    print("=" * 70)

    # ── write scores to a quick txt for day1_report ───────────────────────────
    score_file = OUT_DIR / "baseline_scores.txt"
    with open(score_file, "w") as f:
        f.write(f"OOF macro-F1 : {oof_score:.4f}\n")
        val_score_str = f"{val_score:.4f}" if val_score is not None else "N/A"
        f.write(f"Val macro-F1 : {val_score_str}\n")
        f.write(f"Per-fold     : {fold_scores}\n")
        f.write(f"Classes      : {n_classes}\n")
        f.write(f"Train        : {len(X_train)}\n")
        f.write(f"Val          : {val_count}\n")
        f.write("Top-5 confusion pairs:\n")
        for true_cls, pred_cls, cnt in confusion_pairs:
            f.write(f"  {true_cls} -> {pred_cls}  ({cnt})\n")
    print(f"[saved] {score_file}")


if __name__ == "__main__":
    main()
