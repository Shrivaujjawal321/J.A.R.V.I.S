"""Submission writer and validator — writes CSV and checks row/column match against sample_submission."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


def write_submission(
    df: pd.DataFrame,
    path: str | Path,
    sample_path: str | Path | None = None,
) -> None:
    """Write df to a CSV submission file; optionally validate shape and columns against sample_submission.

    Args:
        df:          DataFrame to write. Must have an index or explicit ID column — write as-is.
        path:        Output CSV path. Parent directory is created if it does not exist.
        sample_path: Path to sample_submission.csv. If given, validates row count and column names.

    Raises:
        ValueError: If row count or column names do not match the sample submission.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    if sample_path is not None:
        sample = pd.read_csv(sample_path)

        # --- row count check ---
        if len(df) != len(sample):
            raise ValueError(
                f"Row count mismatch: submission has {len(df)} rows, "
                f"sample_submission has {len(sample)} rows."
            )

        # --- column name check ---
        sub_cols = list(df.columns)
        smp_cols = list(sample.columns)
        if sub_cols != smp_cols:
            raise ValueError(
                f"Column mismatch:\n  submission  : {sub_cols}\n  sample_sub  : {smp_cols}"
            )

    df.to_csv(path, index=False)

    print(f"Submission written: {path}  ({len(df):,} rows x {len(df.columns)} cols)")
    print("\n--- 5-row preview ---")
    print(df.head(5).to_string(index=False))
    print("---------------------")
