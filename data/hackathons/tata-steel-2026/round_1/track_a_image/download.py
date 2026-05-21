"""
Track A Day 1 — Dataset Download
Dataset: Zhaosxian/SteelDefectX (HuggingFace Hub, CC-BY-4.0)
Run: python download.py
Idempotent: skips if train/ already populated.
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

# ── paths ─────────────────────────────────────────────────────────────────────
ROUND1_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROUND1_DIR / "data_cache" / "steeldefectx"
TRAIN_DIR = DATA_DIR / "train"


def _disk_usage_gb(path: Path) -> float:
    total = sum(f.stat().st_size for f in path.rglob("*") if f.is_file())
    return total / 1024**3


def main() -> None:
    # ── idempotency check ──────────────────────────────────────────────────────
    if TRAIN_DIR.exists() and any(TRAIN_DIR.iterdir()):
        train_count = sum(1 for _ in TRAIN_DIR.rglob("*.jpg")) + \
                      sum(1 for _ in TRAIN_DIR.rglob("*.png")) + \
                      sum(1 for _ in TRAIN_DIR.rglob("*.bmp"))
        if train_count > 100:
            print(f"[skip] train/ already has {train_count:,} images.")
            print(f"[disk] {_disk_usage_gb(DATA_DIR):.2f} GB used in {DATA_DIR}")
            return

    print("[download] Starting SteelDefectX download...")
    print(f"[target]  {DATA_DIR}")
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    try:
        from huggingface_hub import snapshot_download
    except ImportError:
        print("[error] huggingface_hub not installed.")
        print("        Run: pip install huggingface_hub")
        sys.exit(1)

    snapshot_download(
        repo_id="Zhaosxian/SteelDefectX",
        repo_type="dataset",
        local_dir=str(DATA_DIR),
        local_dir_use_symlinks=False,
        ignore_patterns=["*.git*", "*.gitattributes"],
    )

    # ── verify ─────────────────────────────────────────────────────────────────
    train_count = (
        sum(1 for _ in TRAIN_DIR.rglob("*.jpg"))
        + sum(1 for _ in TRAIN_DIR.rglob("*.png"))
        + sum(1 for _ in TRAIN_DIR.rglob("*.bmp"))
    )
    disk_gb = _disk_usage_gb(DATA_DIR)
    print(f"\n[done] {train_count:,} train images found.")
    print(f"[disk] {disk_gb:.2f} GB used in {DATA_DIR}")

    # show top-level directory listing
    print("\n[layout]")
    for item in sorted(DATA_DIR.iterdir()):
        if item.is_dir():
            n = sum(1 for _ in item.rglob("*") if _.is_file())
            print(f"  {item.name}/  ({n:,} files)")
        else:
            print(f"  {item.name}")


if __name__ == "__main__":
    main()
