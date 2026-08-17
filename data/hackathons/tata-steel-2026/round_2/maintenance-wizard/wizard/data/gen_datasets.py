"""
wizard/data/gen_datasets.py
============================
Entrypoint: download/cache NASA C-MAPSS (FD001 + FD003) and AI4I 2020 datasets,
apply domain framing, and ingest SensorSummary rows for the demo assets into wizard.db.

Handles download failure gracefully — prints a clear message and exits 0 so the
rest of the pipeline (KG build, ML training on synthetic data) can proceed offline.

Usage::
    python wizard/data/gen_datasets.py [--skip-cmapss] [--skip-ai4i]
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("gen_datasets")


def _ingest_cmapss(raw_dir: Path) -> int:
    """
    Download + parse C-MAPSS FD001 + FD003, then ingest SensorSummary rows.
    Returns number of rows written; 0 on offline/error.
    """
    try:
        from wizard.data.cmapss_loader import load_cmapss
        from wizard.data.db_ingest import seed_demo_assets, ingest_sensor_rows

        log.info("Loading NASA C-MAPSS (FD001 + FD003) …")
        ds = load_cmapss(subsets=["FD001", "FD003"], raw_dir=raw_dir)

        # Seed asset profiles first (idempotent)
        seed_demo_assets()

        # Ingest FD001 train set → EAF-04 (the demo "blast furnace fan" asset)
        written = 0
        train_fd001 = ds.train.get("FD001")
        if train_fd001 is not None and len(train_fd001) > 0:
            # Use a sample to keep DB size manageable (first 2000 rows)
            sample = train_fd001.head(2000)
            n = ingest_sensor_rows(sample, asset_id="EAF-04", source_system="cmapss")
            log.info("C-MAPSS FD001 → EAF-04: %d SensorSummary rows written", n)
            written += n

        # Ingest FD003 → BF-FAN-01
        train_fd003 = ds.train.get("FD003")
        if train_fd003 is not None and len(train_fd003) > 0:
            sample = train_fd003.head(1000)
            n = ingest_sensor_rows(sample, asset_id="BF-FAN-01", source_system="cmapss")
            log.info("C-MAPSS FD003 → BF-FAN-01: %d SensorSummary rows written", n)
            written += n

        return written

    except (ConnectionError, FileNotFoundError, OSError) as exc:
        log.warning(
            "C-MAPSS download/parse failed (offline or missing file): %s\n"
            "  → Place train_FD001.txt, test_FD001.txt, RUL_FD001.txt (and FD003 equivalents)\n"
            "    in data/raw/cmapss/ to use real data. Continuing with synthetic fallback.",
            exc,
        )
        return 0
    except Exception as exc:
        log.warning("C-MAPSS ingest unexpected error: %s — skipping.", exc)
        return 0


def _ingest_ai4i(raw_dir: Path) -> int:
    """
    Download + parse AI4I 2020, then ingest SensorSummary rows.
    Returns number of rows written; 0 on offline/error.
    """
    try:
        from wizard.data.ai4i_loader import load_ai4i
        from wizard.data.db_ingest import seed_demo_assets, ingest_ai4i_rows
        from wizard.data.dataset_framing import frame_ai4i

        log.info("Loading AI4I 2020 Predictive Maintenance Dataset …")
        df = load_ai4i(raw_dir=raw_dir)
        log.info(
            "AI4I loaded: %d rows, %.1f%% failures",
            len(df),
            df["machine_failure"].mean() * 100,
        )

        # Seed asset profiles first (idempotent)
        seed_demo_assets()

        # Frame + ingest (sample 2000 rows for demo)
        sample = df.head(2000)
        try:
            framed = frame_ai4i(sample)
        except Exception as exc:
            log.warning("frame_ai4i failed (%s) — ingesting raw rows directly.", exc)
            framed = sample

        n = ingest_ai4i_rows(framed)
        log.info("AI4I 2020 → wizard.db: %d SensorSummary rows written", n)
        return n

    except (ConnectionError, FileNotFoundError, OSError) as exc:
        log.warning(
            "AI4I 2020 download/parse failed (offline or missing file): %s\n"
            "  → Download ai4i2020.csv from https://archive.ics.uci.edu/dataset/601\n"
            "    and place it in data/raw/ai4i/. Continuing with synthetic fallback.",
            exc,
        )
        return 0
    except Exception as exc:
        log.warning("AI4I ingest unexpected error: %s — skipping.", exc)
        return 0


def _seed_synthetic_sensor_rows() -> int:
    """
    Fallback: seed wizard.db with synthetic SensorSummary rows so the demo
    has something to work with even if all downloads fail.
    Returns number of rows written.
    """
    try:
        import numpy as np
        import pandas as pd
        from wizard.data.db_ingest import seed_demo_assets, ingest_sensor_rows
        from wizard.ml.feature_utils import SENSOR_KEYS

        log.info("Seeding wizard.db with synthetic SensorSummary rows (offline fallback) …")
        seed_demo_assets()

        rng = np.random.default_rng(42)
        total_written = 0

        asset_classes = {
            "EAF-04":      "fan",
            "BF-FAN-01":   "fan",
            "PUMP-CP-01":  "pump",
            "CONV-HSM-01": "conveyor",
            "BEAR-RM-01":  "bearing",
        }

        for asset_id in asset_classes:
            n = 200
            rows = []
            for cycle in range(1, n + 1):
                # Simulate gradual degradation over cycles
                deg = cycle / n
                readings = {k: float(rng.uniform(0.1 + deg * 0.3, 0.5 + deg * 0.4))
                            for k in SENSOR_KEYS}
                rul = max(0, n - cycle)
                rows.append({
                    "cycle": cycle,
                    "rul": rul,
                    "rul_capped": min(rul, 125),
                    "anomaly_window": int(rul <= 30),
                    "health_score": 1.0 - min(rul, 125) / 125.0,
                    **readings,
                })

            df = pd.DataFrame(rows)
            written = ingest_sensor_rows(df, asset_id=asset_id, source_system="synthetic")
            log.info("Synthetic fallback → %s: %d rows", asset_id, written)
            total_written += written

        return total_written

    except Exception as exc:
        log.warning("Synthetic sensor seed failed: %s", exc)
        return 0


def main(skip_cmapss: bool = False, skip_ai4i: bool = False) -> None:
    from wizard.core.db import init_db

    log.info("Initialising wizard.db …")
    init_db()

    raw_cmapss = _REPO_ROOT / "data" / "raw" / "cmapss"
    raw_ai4i   = _REPO_ROOT / "data" / "raw" / "ai4i"

    cmapss_written = 0
    ai4i_written   = 0

    if not skip_cmapss:
        cmapss_written = _ingest_cmapss(raw_dir=raw_cmapss)
    else:
        log.info("Skipping C-MAPSS (--skip-cmapss flag set).")

    if not skip_ai4i:
        ai4i_written = _ingest_ai4i(raw_dir=raw_ai4i)
    else:
        log.info("Skipping AI4I (--skip-ai4i flag set).")

    # If both downloads failed, seed synthetic rows so demo assets have data
    if cmapss_written == 0 and ai4i_written == 0:
        log.info(
            "Both real datasets unavailable — seeding synthetic SensorSummary rows …"
        )
        _seed_synthetic_sensor_rows()

    # Seed fault log with realistic delay_hours + SCADA/control_system sources (§4.1)
    from wizard.data.db_ingest import (
        seed_fault_log, seed_demo_sensor_summaries, seed_demo_spare_parts,
    )
    fault_rows = seed_fault_log()
    log.info("gen_datasets: fault_log seeded — %d new rows with delay_hours + scada sources", fault_rows)

    # Seed spare parts per asset (§4.3/§5.3) so spare-procurement recommendations fire
    spare_rows = seed_demo_spare_parts()
    log.info("gen_datasets: spare_part seeded — %d new rows (in-stock + out-of-stock mix)", spare_rows)

    # Seed per-asset "latest" SensorSummary rows so _extract_sensor_snapshot reads
    # real data.  Mix: 2 critical (BEAR-RM-01, PUMP-CP-01), EAF-04 baseline,
    # 3 normal (BF-FAN-01, CONV-HSM-01, HPU-01).  inject_fault still pushes EAF-04
    # to critical for the scripted demo moment.
    sensor_seed_rows = seed_demo_sensor_summaries()
    log.info("gen_datasets: per-asset sensor summaries seeded — %d new rows", sensor_seed_rows)

    log.info(
        "gen_datasets complete: C-MAPSS rows=%d, AI4I rows=%d, fault_log rows=%d, sensor_seed rows=%d",
        cmapss_written,
        ai4i_written,
        fault_rows,
        sensor_seed_rows,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Download/cache C-MAPSS + AI4I and ingest into wizard.db"
    )
    parser.add_argument("--skip-cmapss", action="store_true",
                        help="Skip NASA C-MAPSS download (use synthetic fallback)")
    parser.add_argument("--skip-ai4i", action="store_true",
                        help="Skip AI4I 2020 download (use synthetic fallback)")
    args = parser.parse_args()

    main(skip_cmapss=args.skip_cmapss, skip_ai4i=args.skip_ai4i)
    sys.exit(0)
