# Train / Val / Test Split Protocol

A `split` column is present in `raw_sensor_timeseries.csv`, every `by_equipment/*.csv`
dense table, and `rul_trajectories_long.csv`. **Do not random-split rows** — adjacent
hours of one degradation ramp would leak across folds.

## Protocol (leakage-safe)
- **Failure episodes** are the unit of holdout. Each episode has a unique `run_id`
  (e.g. `HSM.F3.WR.BRG01::E03`). Per asset, episodes are ordered by failure time:
  the **last 2 episodes → test**, the **prior 1 → val**, the **rest → train**.
- **Healthy steady-state rows** (no `run_id`) are split **temporally**: first 70% of
  the year → train, 70–85% → val, ≥85% → test.
- For RUL regression use **leave-one-run-out CV** over `run_id` (120 independent runs).
- For failure classification use the `split` column or **group-K-fold on `asset_id`**.

## Row counts
| split | rows |
|---|---|
| train | 85,014 |
| val | 18,739 |
| test | 27,287 |

## Why
The v1 dataset shipped no split and a clock-derived label, so a naive split reported
inflated metrics (audit CM-04). Episode-holdout + temporal healthy split + `run_id`
LORO-CV make reported RUL/failure metrics honest.
