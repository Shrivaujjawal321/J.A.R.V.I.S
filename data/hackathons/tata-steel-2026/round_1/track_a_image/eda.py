"""
Track A Day 1 — EDA Script
Dataset: Zhaosxian/SteelDefectX
Run: python eda.py
Outputs:
  eda_class_distribution.csv
  eda_class_distribution.png
"""

from __future__ import annotations

import json
import random
import sys
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # headless
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PIL import Image

# ── paths ─────────────────────────────────────────────────────────────────────
ROUND1_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROUND1_DIR / "data_cache" / "steeldefectx"
OUT_DIR = Path(__file__).resolve().parent

TRAIN_DIR = DATA_DIR / "train"
VAL_DIR = DATA_DIR / "val"
TRAIN_MASK_DIR = DATA_DIR / "train_mask"
VAL_MASK_DIR = DATA_DIR / "val_mask"
CLASS_DESC_JSON = DATA_DIR / "class_descriptions.json"
TRAIN_TEXT_JSON = DATA_DIR / "train-text.json"

# ── seed ──────────────────────────────────────────────────────────────────────
sys.path.insert(0, str(ROUND1_DIR))
from ml_harness.utils.seed import set_seed
set_seed(42)


# ── helpers ───────────────────────────────────────────────────────────────────

IMG_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"}


def list_images(directory: Path) -> list[Path]:
    """Return sorted list of image paths in directory."""
    return sorted(
        p for p in directory.iterdir()
        if p.suffix.lower() in IMG_EXTS
    )


def class_from_filename(path: Path) -> str:
    """Extract class prefix — everything before the first underscore."""
    stem = path.stem  # filename without extension
    return stem.split("_")[0]


def mask_defect_ratio(mask_path: Path) -> float:
    """Return fraction of non-zero pixels in the mask image."""
    try:
        mask = np.array(Image.open(mask_path).convert("L"))
        return float((mask > 0).sum()) / mask.size
    except Exception:
        return 0.0


def find_mask(img_path: Path, train: bool) -> Path | None:
    """Find the corresponding mask file for an image."""
    mask_dir = TRAIN_MASK_DIR if train else VAL_MASK_DIR
    # Masks may have the same stem with different extension
    for ext in IMG_EXTS:
        candidate = mask_dir / (img_path.stem + ext)
        if candidate.exists():
            return candidate
    # Try png fallback
    candidate = mask_dir / (img_path.stem + ".png")
    if candidate.exists():
        return candidate
    return None


# ── load class descriptions ────────────────────────────────────────────────────

def load_class_descriptions() -> dict[str, str]:
    """Return {prefix: class_name} mapping.

    Primary source: train-text.json (has image_name -> class_name).
    Fallback: class_descriptions.json (full names as keys — used for
    verbose description lookup, not prefix mapping).
    """
    # Best source: train-text.json has the authoritative prefix mapping
    if TRAIN_TEXT_JSON.exists():
        with open(TRAIN_TEXT_JSON) as f:
            records = json.load(f)
        prefix_map: dict[str, str] = {}
        for item in records:
            prefix = item["image_name"].split("_")[0]
            prefix_map[prefix] = item["class_name"]
        return prefix_map

    # Fallback: class_descriptions.json — keys are full class names, not prefixes.
    # Try to guess prefix from first word(s) of class name.
    if CLASS_DESC_JSON.exists():
        with open(CLASS_DESC_JSON) as f:
            raw = json.load(f)
        if isinstance(raw, dict):
            # raw is {class_name: long_description} — not usable for prefix mapping
            # return as-is; caller will fall back to prefix as label
            return {}

    print("[warn] Neither train-text.json nor class_descriptions.json found.")
    print("       Using filename prefix as class label (no description).")
    return {}


# ── main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    print("=" * 70)
    print("Track A Day 1 — EDA: SteelDefectX")
    print("=" * 70)

    # ── existence checks ──────────────────────────────────────────────────────
    if not TRAIN_DIR.exists():
        print(f"[error] train/ not found at {TRAIN_DIR}")
        print("        Run download.py first.")
        sys.exit(1)

    # val + mask dirs are optional — warn but continue
    for d, name in [
        (VAL_DIR, "val/"),
        (TRAIN_MASK_DIR, "train_mask/"),
        (VAL_MASK_DIR, "val_mask/"),
    ]:
        if not d.exists():
            print(f"[warn] {name} not found — stats will be train-only.")

    # ── load class descriptions ───────────────────────────────────────────────
    class_desc = load_class_descriptions()

    # ── list images ───────────────────────────────────────────────────────────
    train_imgs = list_images(TRAIN_DIR)
    val_imgs = list_images(VAL_DIR) if VAL_DIR.exists() else []

    print(f"\n[counts] train images : {len(train_imgs):,}")
    print(f"[counts] val   images : {len(val_imgs):,}")
    print(f"[counts] total        : {len(train_imgs) + len(val_imgs):,}")

    # ── class distribution ────────────────────────────────────────────────────
    train_classes: dict[str, list[Path]] = defaultdict(list)
    val_classes: dict[str, list[Path]] = defaultdict(list)

    for p in train_imgs:
        train_classes[class_from_filename(p)].append(p)
    for p in val_imgs:
        val_classes[class_from_filename(p)].append(p)

    all_classes = sorted(
        set(train_classes.keys()) | set(val_classes.keys()),
        key=lambda c: -(len(train_classes.get(c, [])) + len(val_classes.get(c, []))),
    )

    print(f"\n[classes] {len(all_classes)} unique class prefixes found")
    print(f"\n{'Rank':<5} {'Prefix':<12} {'Train':>8} {'Val':>8} {'Total':>8}  Description")
    print("-" * 70)
    for rank, cls in enumerate(all_classes, 1):
        tc = len(train_classes.get(cls, []))
        vc = len(val_classes.get(cls, []))
        desc = class_desc.get(cls, "—")[:32]
        print(f"{rank:<5} {cls:<12} {tc:>8,} {vc:>8,} {tc+vc:>8,}  {desc}")

    top3 = all_classes[:3]
    bot3 = all_classes[-3:]
    print(f"\n[top-3 by freq] {', '.join(top3)}")
    print(f"[bot-3 by freq] {', '.join(bot3)}")

    # ── image dimension check ─────────────────────────────────────────────────
    print("\n[dims] Sampling 10 images per class for size check...")
    all_widths, all_heights = [], []
    dim_hetero: dict[str, bool] = {}

    for cls in all_classes:
        imgs_for_cls = train_classes.get(cls, []) + val_classes.get(cls, [])
        sample = random.sample(imgs_for_cls, min(10, len(imgs_for_cls)))
        sizes: set[tuple[int, int]] = set()
        for p in sample:
            try:
                w, h = Image.open(p).size
                sizes.add((w, h))
                all_widths.append(w)
                all_heights.append(h)
            except Exception as e:
                print(f"  [warn] Could not open {p.name}: {e}")
        hetero = len(sizes) > 1
        dim_hetero[cls] = hetero
        size_str = ", ".join(f"{w}x{h}" for w, h in sorted(sizes))
        flag = " [HETERO]" if hetero else ""
        print(f"  {cls:<12} sizes={size_str[:60]}{flag}")

    if all_widths:
        print(f"\n[dims] Width  — min:{min(all_widths)} max:{max(all_widths)} "
              f"mean:{np.mean(all_widths):.0f}")
        print(f"[dims] Height — min:{min(all_heights)} max:{max(all_heights)} "
              f"mean:{np.mean(all_heights):.0f}")
        hetero_classes = [c for c, v in dim_hetero.items() if v]
        if hetero_classes:
            print(f"[warn] Heterogeneous dims in: {hetero_classes}")
        else:
            print("[dims] All sampled images are uniform size per class.")

    # ── mask defect area ratio ────────────────────────────────────────────────
    print("\n[masks] Computing defect area ratios (% non-zero pixels)...")
    class_ratios: dict[str, list[float]] = defaultdict(list)
    total_masks = 0
    missing_masks = 0

    # Sample up to 50 per class for speed
    for cls in all_classes:
        sample_train = random.sample(
            train_classes.get(cls, []),
            min(30, len(train_classes.get(cls, [])))
        )
        for img_p in sample_train:
            mask_p = find_mask(img_p, train=True)
            if mask_p:
                ratio = mask_defect_ratio(mask_p)
                class_ratios[cls].append(ratio * 100.0)
                total_masks += 1
            else:
                missing_masks += 1

    all_ratios = [r for rs in class_ratios.values() for r in rs]
    if all_ratios:
        arr = np.array(all_ratios)
        print(f"[masks] Sampled {total_masks:,} masks "
              f"({missing_masks} missing / no mask found)")
        print(f"[masks] Defect area ratio (% of image pixels):")
        print(f"         mean   = {arr.mean():.2f}%")
        print(f"         median = {np.median(arr):.2f}%")
        print(f"         p95    = {np.percentile(arr, 95):.2f}%")
        print(f"         p99    = {np.percentile(arr, 99):.2f}%")
        print(f"         max    = {arr.max():.2f}%")
        print(f"\n  Per-class mean defect area (%):")
        for cls in all_classes:
            rs = class_ratios.get(cls, [])
            if rs:
                print(f"    {cls:<12}  {np.mean(rs):.2f}%  (n={len(rs)})")
            else:
                print(f"    {cls:<12}  — (no masks sampled)")
    else:
        print("[warn] No masks found — check TRAIN_MASK_DIR path.")

    # ── save CSV ──────────────────────────────────────────────────────────────
    rows = []
    for cls in all_classes:
        tc = len(train_classes.get(cls, []))
        vc = len(val_classes.get(cls, []))
        rs = class_ratios.get(cls, [])
        mean_pct = float(np.mean(rs)) if rs else float("nan")
        rows.append({
            "class_prefix": cls,
            "class_description": class_desc.get(cls, "unknown"),
            "train_count": tc,
            "val_count": vc,
            "defect_area_mean_pct": round(mean_pct, 4),
        })

    df = pd.DataFrame(rows)
    csv_path = OUT_DIR / "eda_class_distribution.csv"
    df.to_csv(csv_path, index=False)
    print(f"\n[saved] {csv_path}")

    # ── save bar chart ────────────────────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(max(10, len(all_classes) * 0.7), 6))
    x = range(len(all_classes))
    train_counts = [len(train_classes.get(c, [])) for c in all_classes]
    val_counts = [len(val_classes.get(c, [])) for c in all_classes]

    bars1 = ax.bar(x, train_counts, label="Train", color="#2563EB", alpha=0.85)
    bars2 = ax.bar(x, val_counts, bottom=train_counts, label="Val",
                   color="#F59E0B", alpha=0.85)

    ax.set_xticks(list(x))
    ax.set_xticklabels(all_classes, rotation=45, ha="right", fontsize=9)
    ax.set_ylabel("Image Count")
    ax.set_title("SteelDefectX — Class Distribution (Train + Val)")
    ax.legend()
    ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()

    png_path = OUT_DIR / "eda_class_distribution.png"
    fig.savefig(png_path, dpi=120)
    plt.close(fig)
    print(f"[saved] {png_path}")

    # ── final summary ─────────────────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("EDA complete.")
    print(f"  Classes    : {len(all_classes)}")
    print(f"  Train imgs : {len(train_imgs):,}")
    print(f"  Val imgs   : {len(val_imgs):,}")
    if all_ratios:
        arr = np.array(all_ratios)
        print(f"  Defect area: mean={arr.mean():.2f}%  median={np.median(arr):.2f}%  "
              f"p95={np.percentile(arr, 95):.2f}%")
    print("=" * 70)


if __name__ == "__main__":
    main()
