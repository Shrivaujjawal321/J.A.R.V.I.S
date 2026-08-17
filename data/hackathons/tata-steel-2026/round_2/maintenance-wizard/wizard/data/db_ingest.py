"""
wizard.data.db_ingest
=====================
Bridge between the dataset layer and wizard.db (SQLite via SQLModel).

Converts parsed pandas DataFrames into :class:`wizard.core.schemas.SensorSummary`
entities and bulk-inserts them into the database.

Also provides convenience loaders for seeding :class:`AssetProfile` rows
corresponding to the steel-framed equipment families.

Public functions
----------------
ingest_sensor_rows(df, asset_id, source_system, session, batch_size)
    -> int  (rows written)

ingest_asset_profiles(session)
    -> list[AssetProfile]  (seeded master assets)

seed_demo_assets(db_path)
    -> None  (idempotent one-shot demo seeder)

Usage::

    from wizard.data.db_ingest import ingest_sensor_rows, seed_demo_assets
    from wizard.core.db import session_scope

    seed_demo_assets()  # idempotent — call at startup

    # Pass an explicit session (caller manages lifecycle):
    with session_scope() as session:
        n = ingest_sensor_rows(cmapss_train_df, asset_id="EAF-04", session=session)

    # Or let ingest_sensor_rows manage its own session:
    n = ingest_sensor_rows(cmapss_train_df, asset_id="EAF-04")
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List

import pandas as pd
from sqlmodel import Session, select

from wizard.core.schemas import (
    AssetProfile,
    FaultLog,
    SensorSummary,
    SparePart,
    ingest_entity,
)
from wizard.core.db import init_db, get_session, session_scope
from wizard.data.dataset_framing import make_cmapss_sensor_readings, frame_ai4i

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Demo asset seed definitions (5 steel equipment families + EAF-04)
# ---------------------------------------------------------------------------
_SEED_ASSETS = [
    {
        "entity_type":       "asset",
        "asset_id":          "EAF-04",
        "equipment_name":    "EAF-04 Primary Fan",
        "equipment_class":   "fan",
        "plant_area":        "EAF-Bay-4",
        "work_center":       "Electric-Arc-Furnace-4",
        "manufacturer":      "ABB",
        "design_rpm":        1480.0,
        "criticality_tier":  "critical",
        "subsystem":         "primary-exhaust-fan",
        "iso14224_taxonomy": "rotating.centrifugal_fan.impeller",
        "source_system":     "generated",
    },
    {
        "entity_type":       "asset",
        "asset_id":          "BF-FAN-01",
        "equipment_name":    "BF-1 Blast Furnace Fan A",
        "equipment_class":   "fan",
        "plant_area":        "BF-Area-1",
        "work_center":       "Blast-Furnace-1",
        "manufacturer":      "Siemens",
        "design_rpm":        1500.0,
        "criticality_tier":  "critical",
        "subsystem":         "cold-blast-fan",
        "iso14224_taxonomy": "rotating.centrifugal_fan.impeller",
        "source_system":     "generated",
    },
    {
        "entity_type":       "asset",
        "asset_id":          "PUMP-CP-01",
        "equipment_name":    "Cooling Circuit Centrifugal Pump 01",
        "equipment_class":   "pump",
        "plant_area":        "Utility-Block-A",
        "work_center":       "Cooling-System",
        "manufacturer":      "KSB",
        "design_rpm":        1450.0,
        "design_pressure_bar": 8.5,
        "criticality_tier":  "high",
        "subsystem":         "impeller",
        "iso14224_taxonomy": "rotating.centrifugal_pump.impeller",
        "source_system":     "generated",
    },
    {
        "entity_type":       "asset",
        "asset_id":          "CONV-HSM-01",
        "equipment_name":    "Hot-Strip-Mill Conveyor Drive 01",
        "equipment_class":   "conveyor",
        "plant_area":        "HSM-Bay-1",
        "work_center":       "Hot-Strip-Mill-1",
        "manufacturer":      "SMS Group",
        "design_rpm":        75.0,
        "criticality_tier":  "high",
        "subsystem":         "drive-roller",
        "iso14224_taxonomy": "linear.conveyor.drive_roller",
        "source_system":     "generated",
    },
    {
        "entity_type":       "asset",
        "asset_id":          "BEAR-RM-01",
        "equipment_name":    "Rolling Mill Bearing Stand 3",
        "equipment_class":   "bearing",
        "plant_area":        "HSM-Bay-2",
        "work_center":       "Rolling-Mill-1",
        "manufacturer":      "SKF",
        "design_rpm":        800.0,
        "criticality_tier":  "critical",
        "subsystem":         "backup-roll-bearing",
        "iso14224_taxonomy": "rotating.bearing.roller",
        "source_system":     "generated",
    },
    {
        "entity_type":       "asset",
        "asset_id":          "HPU-01",
        "equipment_name":    "Hydraulic Power Unit 01",
        "equipment_class":   "hydraulic_unit",
        "plant_area":        "Utility-Block-B",
        "work_center":       "Hydraulic-Systems",
        "manufacturer":      "Bosch Rexroth",
        "design_pressure_bar": 250.0,
        "criticality_tier":  "medium",
        "subsystem":         "main-pump",
        "iso14224_taxonomy": "fluid_power.hydraulic_unit.main_pump",
        "source_system":     "generated",
    },
]


# ---------------------------------------------------------------------------
# SensorSummary ingest from C-MAPSS DataFrame
# ---------------------------------------------------------------------------

def ingest_sensor_rows(
    df: pd.DataFrame,
    asset_id: str,
    source_system: str = "generated",
    session: Optional[Session] = None,
    batch_size: int = 500,
    base_time: Optional[datetime] = None,
    hours_per_cycle: float = 1.0,
) -> int:
    """
    Convert C-MAPSS (or AI4I) DataFrame rows into :class:`SensorSummary`
    entities and insert them into wizard.db.

    Parameters
    ----------
    df           : DataFrame from load_cmapss or load_ai4i (framed or raw)
    asset_id     : Target asset (e.g. 'EAF-04'). All rows tagged with this id.
    source_system: 'generated' | 'scada' | 'erp'
    session      : Existing SQLModel Session; if None, opens a new one.
    batch_size   : Rows per INSERT batch (SQLite performs best at ~500)
    base_time    : Datetime for cycle 1 (default: now - n_cycles hours)
    hours_per_cycle: How many hours each C-MAPSS cycle represents (default 1h)

    Returns
    -------
    int : Number of rows successfully written
    """
    n_rows = len(df)
    if n_rows == 0:
        # Return early BEFORE opening any session — no leak possible.
        return 0

    if session is not None:
        # Caller owns the session lifecycle; write directly and return.
        return _ingest_sensor_rows_inner(
            df, asset_id, source_system, session, batch_size, base_time, hours_per_cycle
        )

    # No caller-supplied session — open our own via session_scope() which
    # commits on clean exit and always closes (finding #4: the old
    # `with next(get_session())` pattern does NOT commit writes).
    with session_scope() as _session:
        return _ingest_sensor_rows_inner(
            df, asset_id, source_system, _session, batch_size, base_time, hours_per_cycle
        )


def _ingest_sensor_rows_inner(
    df: pd.DataFrame,
    asset_id: str,
    source_system: str,
    session: Session,
    batch_size: int,
    base_time: Optional[datetime],
    hours_per_cycle: float,
) -> int:
    """Inner worker — assumes session lifecycle is managed by caller."""
    n_rows = len(df)
    if base_time is None:
        base_time = datetime.utcnow() - timedelta(hours=n_rows * hours_per_cycle)

    written = 0
    batch: List[SensorSummary] = []

    for _, row in df.iterrows():
        cycle = int(row.get("cycle", row.get("operating_hours", 0)))
        win_start = base_time + timedelta(hours=cycle * hours_per_cycle)
        win_end   = win_start + timedelta(hours=hours_per_cycle)

        # Build sensor_readings dict
        if "sensor_readings" in row.index and isinstance(row["sensor_readings"], dict):
            readings = row["sensor_readings"]
        else:
            readings = make_cmapss_sensor_readings(row)

        # Derive operating_condition from anomaly_window / rul
        op_cond = _derive_operating_condition(row)

        entity = SensorSummary(
            asset_id=asset_id,
            plant_area=str(row.get("plant_area", "unspecified")),
            source_system=source_system,
            window_start=win_start,
            window_end=win_end,
            sensor_readings=readings,
            operating_condition=op_cond,
            operating_hours=float(cycle),
            # rul_days_p50 and anomaly_score written later by ML pipeline
        )
        batch.append(entity)

        if len(batch) >= batch_size:
            session.add_all(batch)
            session.flush()
            written += len(batch)
            batch = []
            logger.debug("Flushed %d SensorSummary rows for %s", written, asset_id)

    if batch:
        session.add_all(batch)
        session.flush()
        written += len(batch)

    logger.info(
        "ingest_sensor_rows: %d rows written for asset_id=%s",
        written, asset_id,
    )
    return written


def _derive_operating_condition(row: "pd.Series") -> str:
    """Derive 'normal'/'degraded'/'severe' from row metadata."""
    if "anomaly_window" in row.index and row["anomaly_window"] == 1:
        # Last 30 cycles before failure
        rul = row.get("rul", 999)
        return "severe" if rul <= 10 else "degraded"
    if "health_score" in row.index:
        hs = float(row["health_score"])
        if hs >= 0.8:
            return "severe"
        if hs >= 0.5:
            return "degraded"
    return "normal"


# ---------------------------------------------------------------------------
# Asset profile seeder
# ---------------------------------------------------------------------------

def ingest_asset_profiles(session: Session) -> List[AssetProfile]:
    """
    Insert seed AssetProfile rows if they don't already exist.
    Idempotent: skips any asset_id that is already in the DB.

    Returns
    -------
    list[AssetProfile] : newly created profiles (empty if all existed)
    """
    created: List[AssetProfile] = []
    for raw in _SEED_ASSETS:
        existing = session.exec(
            select(AssetProfile).where(AssetProfile.asset_id == raw["asset_id"])
        ).first()
        if existing is not None:
            continue

        entity = ingest_entity(raw)
        session.add(entity)
        created.append(entity)

    if created:
        session.flush()
        logger.info("Seeded %d AssetProfile rows", len(created))
    return created


def seed_demo_assets(db_path: Optional[Path] = None) -> None:
    """
    Idempotent one-shot demo asset seeder.
    Safe to call at application startup — skips existing rows.
    """
    init_db(db_path)
    # Use session_scope() so the INSERT is committed on clean exit.
    # (The old `with next(get_session(...)) as session:` was wrong —
    # get_session() returns a generator, not a context manager, so
    # writes were silently lost.)
    with session_scope(db_path) as session:
        profiles = ingest_asset_profiles(session)
    logger.info("seed_demo_assets: %d new assets created", len(profiles))


# ---------------------------------------------------------------------------
# Fault log seeder — PS §4.1: realistic delay_hours + SCADA/control_system sources
# ---------------------------------------------------------------------------

# Realistic fault seed rows keyed to actual asset_ids in wizard.db.
# Each entry includes:
#   - delay_hours: actual production-delay hours caused by the fault (WRPS F2 input)
#   - source: 'scada' or 'control_system' entries ensure §4.1 control-system fault
#             representation alongside existing 'operator' rows
#   - severity: drives WRPS fallback when delay_hours computation is bypassed
_SEED_FAULTS: list[dict] = [
    # EAF-04 — critical fan; bearing fault from SCADA
    {
        "asset_id": "EAF-04",
        "plant_area": "EAF-Bay-4",
        "fault_code": "BRG-TEMP-HIGH-001",
        "fault_description": "SCADA-detected bearing temperature exceedance: 112°C (limit 85°C). Auto-derating initiated.",
        "severity": "critical",
        "delay_hours": 18.5,
        "source": "scada",
        "confirmed": True,
    },
    # BF-FAN-01 — critical fan; vibration step-change from SCADA
    {
        "asset_id": "BF-FAN-01",
        "plant_area": "BF-Area-1",
        "fault_code": "VIB-STEP-HIGH-003",
        "fault_description": "Control system fault: shaft vibration step-change 1.8→5.2 mm/s at rated speed. 1× imbalance component dominant.",
        "severity": "high",
        "delay_hours": 12.0,
        "source": "control_system",
        "confirmed": True,
    },
    # PUMP-CP-01 — high criticality; cavitation detected by pressure sensor
    {
        "asset_id": "PUMP-CP-01",
        "plant_area": "Utility-Block-A",
        "fault_code": "PUMP-CAV-002",
        "fault_description": "Suction pressure anomaly: 0.3 bar below design minimum. Flow drop 8%. Cavitation suspected from acoustic signature.",
        "severity": "medium",
        "delay_hours": 6.0,
        "source": "scada",
        "confirmed": True,
    },
    # CONV-HSM-01 — high criticality; drive overcurrent from PLC
    {
        "asset_id": "CONV-HSM-01",
        "plant_area": "HSM-Bay-1",
        "fault_code": "DRIVE-OC-007",
        "fault_description": "Control system fault: drive overcurrent trip I > 1.4×FLA during coil transfer. Third occurrence in 8 hours.",
        "severity": "high",
        "delay_hours": 9.0,
        "source": "control_system",
        "confirmed": True,
    },
    # BEAR-RM-01 — critical bearing; operator report with measured delay
    {
        "asset_id": "BEAR-RM-01",
        "plant_area": "HSM-Bay-2",
        "fault_code": "BRG-PLAY-EXCESS-001",
        "fault_description": "Backup roll bearing axial play 0.45 mm (limit 0.25 mm). BPFO spectral peaks elevated. Operator measurement during roll change.",
        "severity": "critical",
        "delay_hours": 24.0,
        "source": "operator",
        "confirmed": True,
    },
    # HPU-01 — medium criticality; servo valve fault from PLC/DCS
    {
        "asset_id": "HPU-01",
        "plant_area": "Utility-Block-B",
        "fault_code": "HYD-PRES-LOW-002",
        "fault_description": "DCS fault: hydraulic pressure drop 250→212 bar on main circuit. Servo valve spool position sensor deviation flagged.",
        "severity": "medium",
        "delay_hours": 4.0,
        "source": "control_system",
        "confirmed": True,
    },
    # EAF-04 — second fault entry; electrode position fault from PLC
    {
        "asset_id": "EAF-04",
        "plant_area": "EAF-Bay-4",
        "fault_code": "E-ENC-042",
        "fault_description": "PLC encoder signal loss on electrode positioning axis. Position oscillation ±12 mm (limit ±2 mm). Arc instability — power-on efficiency -6%.",
        "severity": "high",
        "delay_hours": 7.5,
        "source": "scada",
        "confirmed": True,
    },
    # BF-FAN-01 — seal wear; operator + SCADA corroborated
    {
        "asset_id": "BF-FAN-01",
        "plant_area": "BF-Area-1",
        "fault_code": "SEAL-WEAR-BF-01",
        "fault_description": "Oil seal degradation on fan shaft — oil mist visible. SCADA lube pressure slightly low. Confirmed by technician inspection.",
        "severity": "medium",
        "delay_hours": 3.5,
        "source": "operator",
        "confirmed": True,
    },
    # PUMP-CP-01 — coolant temperature deviation from SCADA
    {
        "asset_id": "PUMP-CP-01",
        "plant_area": "Utility-Block-A",
        "fault_code": "COOL-TEMP-RISE-005",
        "fault_description": "SCADA coolant temperature rise +4°C on EAF bay cooling loop. Pump discharge flow 8% below setpoint. EAF bay at risk.",
        "severity": "high",
        "delay_hours": 8.0,
        "source": "scada",
        "confirmed": True,
    },
    # CONV-HSM-01 — gearbox oil contamination; operator
    {
        "asset_id": "CONV-HSM-01",
        "plant_area": "HSM-Bay-1",
        "fault_code": "GEAR-OIL-CONTAM-002",
        "fault_description": "Milky gear oil observed in HSM-01 drive gearbox — water ingress via cooled bearing housing seal. Oil sample dispatched.",
        "severity": "medium",
        "delay_hours": 2.0,
        "source": "operator",
        "confirmed": True,
    },
    # BEAR-RM-01 — lubrication fault from SCADA lube monitoring system
    {
        "asset_id": "BEAR-RM-01",
        "plant_area": "HSM-Bay-2",
        "fault_code": "LUBE-FLOW-LOW-RM3",
        "fault_description": "SCADA lube monitoring: grease flow to backup roll bearing RM-01 below minimum threshold for 45 min. Thermal alarm imminent.",
        "severity": "high",
        "delay_hours": 16.0,
        "source": "scada",
        "confirmed": True,
    },
    # HPU-01 — contamination particle count (auto-sampler = control_system)
    {
        "asset_id": "HPU-01",
        "plant_area": "Utility-Block-B",
        "fault_code": "HYD-OIL-PART-003",
        "fault_description": "Online particle counter (control system): ISO 4406 cleanliness code exceeded 18/16/13 (target 17/15/12). Accelerated filter loading.",
        "severity": "low",
        "delay_hours": 2.5,
        "source": "control_system",
        "confirmed": True,
    },
]


def seed_demo_sensor_summaries(db_path: Optional[Path] = None) -> int:
    """
    Idempotent one-shot demo SensorSummary seeder.

    Seeds a SINGLE "latest" SensorSummary row per demo asset with realistic
    physical-unit sensor_readings.  The mix:

    DEGRADED / CRITICAL assets (chat → high priority, short RUL, high anomaly):
      • BEAR-RM-01  — bearing with vibration_mm_s=9.1 (critical band), temp high
      • PUMP-CP-01  — pump with pressure_bar=32 (critical-low), high vibration

    NORMAL assets (chat → low priority, long RUL, low anomaly):
      • BF-FAN-01   — fan within normal operating bands
      • CONV-HSM-01 — conveyor within normal bands
      • HPU-01      — hydraulic unit within normal bands

    EAF-04 baseline (slightly elevated but NOT critical):
      • vibration=6.0 (warn zone), temp=470 — /v1/demo/inject_fault still pushes
        it to critical for the scripted wow-moment.

    Idempotency: skips assets that already have a SensorSummary row with
    source_system='demo_seed'.  Call `make reset` to wipe and re-seed.

    Returns number of new rows inserted.
    """
    from datetime import datetime, timedelta

    init_db(db_path)

    # Per-asset seed spec.
    # Fields: sensor_readings, equipment_class, operating_condition, anomaly_score, op_hours
    # NOTE: rul_days_p50 is intentionally NOT hard-coded here. It is computed at
    # seed time by calling predict_rul() so that /v1/sensor/state (stored value)
    # and /v1/chat (live re-inference on the same sensor_readings) are identical.
    _SENSOR_SEEDS: list[dict] = [
        # ----------------------------------------------------------------
        # BEAR-RM-01 — CRITICAL: bearing vibration in critical band,
        #   temperature elevated, lube pressure low.
        #   physics_degradation_index → ~0.695 → high priority, short RUL
        # ----------------------------------------------------------------
        {
            "asset_id": "BEAR-RM-01",
            "plant_area": "HSM-Bay-2",
            "equipment_class": "bearing",
            "sensor_readings": {
                "temperature_c": 455.0,   # warn_hi=450 for bearing → above warning
                "vibration_mm_s": 9.1,    # critical band: >5.5 (bearing override)
                "pressure_bar": 88.0,     # lube pressure: warn_lo=90 → approaching critical
                "rpm": 795.0,             # low-end: near warn_lo=700 for bearing
                "current_a": 78.0,        # elevated (warn_hi=85)
                "torque_nm": 720.0,       # high end (warn_hi=800 for bearing)
            },
            "operating_condition": "severe",
            "anomaly_score": 0.88,
            "operating_hours": 14250.0,
        },
        # ----------------------------------------------------------------
        # PUMP-CP-01 — CRITICAL: pressure in critical-low (cavitation),
        #   vibration elevated.  physics_degradation_index → ~0.719
        # ----------------------------------------------------------------
        {
            "asset_id": "PUMP-CP-01",
            "plant_area": "Utility-Block-A",
            "equipment_class": "pump",
            "sensor_readings": {
                "temperature_c": 210.0,   # normal band (200–420 default)
                "vibration_mm_s": 8.9,    # critical band for pump (>6.5)
                "pressure_bar": 28.0,     # critical-low for pump (<30)
                "rpm": 1430.0,            # normal
                "current_a": 42.0,        # normal
                "torque_nm": 380.0,       # normal
            },
            "operating_condition": "severe",
            "anomaly_score": 0.82,
            "operating_hours": 9870.0,
        },
        # ----------------------------------------------------------------
        # EAF-04 — BASELINE: slightly elevated (warn zone) but NOT critical.
        #   inject_fault pushes it to critical for the scripted moment.
        # ----------------------------------------------------------------
        {
            "asset_id": "EAF-04",
            "plant_area": "EAF-Bay-4",
            "equipment_class": "fan",
            "sensor_readings": {
                "temperature_c": 460.0,   # slightly above normal_hi=420 → warn zone
                "vibration_mm_s": 6.0,    # warn zone for fan (4.5–8.5)
                "pressure_bar": 18.5,     # EAF fan duct pressure — normal for fan class
                "rpm": 1450.0,            # normal
                "current_a": 340.0,       # elevated but within fan class normal range
                "torque_nm": 420.0,       # normal
            },
            "operating_condition": "degraded",
            "anomaly_score": 0.52,
            "operating_hours": 8760.0,
        },
        # ----------------------------------------------------------------
        # BF-FAN-01 — NORMAL: all sensors well within bands
        # ----------------------------------------------------------------
        {
            "asset_id": "BF-FAN-01",
            "plant_area": "BF-Area-1",
            "equipment_class": "fan",
            "sensor_readings": {
                "temperature_c": 320.0,
                "vibration_mm_s": 2.1,
                "pressure_bar": 160.0,
                "rpm": 1490.0,
                "current_a": 48.0,
                "torque_nm": 480.0,
            },
            "operating_condition": "normal",
            "anomaly_score": 0.12,
            "operating_hours": 6540.0,
        },
        # ----------------------------------------------------------------
        # CONV-HSM-01 — NORMAL: conveyor in healthy operating zone
        # ----------------------------------------------------------------
        {
            "asset_id": "CONV-HSM-01",
            "plant_area": "HSM-Bay-1",
            "equipment_class": "conveyor",
            "sensor_readings": {
                "temperature_c": 280.0,
                "vibration_mm_s": 1.8,
                "pressure_bar": 140.0,
                "rpm": 72.0,           # slow drive-roller speed — conveyor is geared
                "current_a": 38.0,
                "torque_nm": 520.0,
            },
            "operating_condition": "normal",
            "anomaly_score": 0.09,
            "operating_hours": 11200.0,
        },
        # ----------------------------------------------------------------
        # HPU-01 — NORMAL: hydraulic unit healthy
        # ----------------------------------------------------------------
        {
            "asset_id": "HPU-01",
            "plant_area": "Utility-Block-B",
            "equipment_class": "hydraulic_unit",
            "sensor_readings": {
                "temperature_c": 240.0,   # HPU override: normal 150–380
                "vibration_mm_s": 1.6,
                "pressure_bar": 238.0,    # HPU normal: 120–250
                "rpm": 1420.0,
                "current_a": 35.0,
                "torque_nm": 310.0,
            },
            "operating_condition": "normal",
            "anomaly_score": 0.07,
            "operating_hours": 7830.0,
        },
    ]

    # Import ML RUL estimator once — used to compute rul_days_p50 from the
    # same model that POST /v1/chat uses, so both surfaces are identical.
    try:
        from wizard.ml.rul_estimator import predict_rul as _predict_rul
        _rul_available = True
    except Exception as _exc:
        logger.warning("seed_demo_sensor_summaries: predict_rul unavailable (%s) — rul_days_p50 will be None", _exc)
        _rul_available = False

    now = datetime.utcnow()
    inserted = 0

    with session_scope(db_path) as session:
        for spec in _SENSOR_SEEDS:
            asset_id = spec["asset_id"]

            # Idempotency: skip if a demo_seed row already exists for this asset
            existing = session.exec(
                select(SensorSummary).where(
                    SensorSummary.asset_id == asset_id,
                    SensorSummary.source_system == "demo_seed",
                )
            ).first()
            if existing is not None:
                continue

            # Compute rul_days_p50 from the ML model so the stored value equals
            # what /v1/chat re-infers on the same sensor_readings.
            rul_p50: float | None = None
            if _rul_available:
                try:
                    _rul = _predict_rul(
                        asset_id=asset_id,
                        sensor_readings=spec["sensor_readings"],
                        equipment_class=spec.get("equipment_class", "default"),
                    )
                    rul_p50 = _rul.rul_days_p50
                    logger.debug(
                        "seed_demo_sensor_summaries: %s rul_days_p50=%.2f (di=%.3f, model=%s)",
                        asset_id, rul_p50, _rul.degradation_index, _rul.model_used,
                    )
                except Exception as exc:
                    logger.warning(
                        "seed_demo_sensor_summaries: predict_rul failed for %s (%s) — rul_days_p50=None",
                        asset_id, exc,
                    )

            row = SensorSummary(
                asset_id=asset_id,
                plant_area=spec.get("plant_area", "unspecified"),
                source_system="demo_seed",
                window_start=now - timedelta(minutes=15),
                window_end=now,
                sensor_readings=spec["sensor_readings"],
                operating_condition=spec.get("operating_condition", "normal"),
                rul_days_p50=rul_p50,
                anomaly_score=spec.get("anomaly_score"),
                operating_hours=spec.get("operating_hours"),
            )
            session.add(row)
            inserted += 1

        if inserted:
            session.flush()

    logger.info("seed_demo_sensor_summaries: %d new SensorSummary rows inserted", inserted)
    return inserted


def seed_fault_log(db_path: Optional[Path] = None) -> int:
    """
    Idempotent fault log seeder — PS §4.1 compliance.

    Inserts FaultLog rows with:
      - Realistic delay_hours (2–24h by severity) for WRPS F2 computation
      - source in {'scada', 'control_system', 'operator'} so control-system
        fault messages are genuinely represented alongside operator entries

    Rows are keyed on (asset_id, fault_code) — re-running skips existing rows.

    Returns
    -------
    int : number of new rows inserted (0 if all already exist)
    """
    init_db(db_path)
    inserted = 0

    with session_scope(db_path) as session:
        for raw in _SEED_FAULTS:
            # Idempotency: skip if (asset_id, fault_code) already present
            existing = session.exec(
                select(FaultLog).where(
                    FaultLog.asset_id == raw["asset_id"],
                    FaultLog.fault_code == raw["fault_code"],
                )
            ).first()
            if existing is not None:
                continue

            fault = FaultLog(
                asset_id=raw["asset_id"],
                plant_area=raw.get("plant_area", "unspecified"),
                fault_code=raw["fault_code"],
                fault_description=raw["fault_description"],
                severity=raw["severity"],
                delay_hours=raw.get("delay_hours"),
                source=raw.get("source", "operator"),
                confirmed=raw.get("confirmed", True),
            )
            session.add(fault)
            inserted += 1

        if inserted:
            session.flush()

    logger.info("seed_fault_log: %d new FaultLog rows inserted", inserted)
    return inserted


# Spare parts per demo asset — a realistic mix of in-stock + out-of-stock so
# the WRPS spare-availability factor and the spare-procurement recommendation
# (PS §5.3 / Explainer §4) genuinely fire. Matched to assets by asset_id.
_SEED_SPARES: list[dict] = [
    # BEAR-RM-01 (bearing) — flagship critical stockout
    {"asset_id": "BEAR-RM-01", "part_number": "BRG-SKF-6310-2RS1",
     "part_name": "Spherical Roller Bearing 6310-2RS1", "compatible_equipment": ["BEAR-RM-01"],
     "stock_qty": 0, "min_stock_qty": 2, "unit_cost_inr": 18500.0, "lead_time_days": 14,
     "supplier": "SKF India", "criticality_override": "critical"},
    # EAF-04 (fan) — one low, one ok
    {"asset_id": "EAF-04", "part_number": "FAN-BRG-2208",
     "part_name": "Fan Shaft Bearing 2208", "compatible_equipment": ["EAF-04"],
     "stock_qty": 1, "min_stock_qty": 2, "unit_cost_inr": 9200.0, "lead_time_days": 10,
     "supplier": "Schaeffler India", "criticality_override": "high"},
    {"asset_id": "EAF-04", "part_number": "EAF-ELEC-CLMP-300",
     "part_name": "Electrode Clamp Assembly", "compatible_equipment": ["EAF-04"],
     "stock_qty": 4, "min_stock_qty": 2, "unit_cost_inr": 42000.0, "lead_time_days": 7,
     "supplier": "Tata Growth Shop", "criticality_override": ""},
    # PUMP-CP-01 (pump) — seal stockout
    {"asset_id": "PUMP-CP-01", "part_number": "PMP-SEAL-65",
     "part_name": "Mechanical Seal 65mm", "compatible_equipment": ["PUMP-CP-01"],
     "stock_qty": 0, "min_stock_qty": 2, "unit_cost_inr": 13400.0, "lead_time_days": 12,
     "supplier": "EagleBurgmann India", "criticality_override": "high"},
    {"asset_id": "PUMP-CP-01", "part_number": "PMP-IMP-200",
     "part_name": "Centrifugal Impeller 200mm", "compatible_equipment": ["PUMP-CP-01"],
     "stock_qty": 2, "min_stock_qty": 1, "unit_cost_inr": 56000.0, "lead_time_days": 20,
     "supplier": "Kirloskar Brothers", "criticality_override": ""},
    # BF-FAN-01 (fan) — comfortable
    {"asset_id": "BF-FAN-01", "part_number": "BF-FAN-BRG-2210",
     "part_name": "Blast-Furnace Fan Bearing 2210", "compatible_equipment": ["BF-FAN-01"],
     "stock_qty": 3, "min_stock_qty": 2, "unit_cost_inr": 11200.0, "lead_time_days": 8,
     "supplier": "Schaeffler India", "criticality_override": ""},
    # CONV-HSM-01 (conveyor) — belt at minimum, long lead
    {"asset_id": "CONV-HSM-01", "part_number": "CONV-ROLL-45",
     "part_name": "Idler Roller 45mm", "compatible_equipment": ["CONV-HSM-01"],
     "stock_qty": 6, "min_stock_qty": 3, "unit_cost_inr": 3200.0, "lead_time_days": 5,
     "supplier": "Fenner Conveyor", "criticality_override": ""},
    {"asset_id": "CONV-HSM-01", "part_number": "CONV-BELT-1200",
     "part_name": "Conveyor Belt Section 1200mm", "compatible_equipment": ["CONV-HSM-01"],
     "stock_qty": 1, "min_stock_qty": 1, "unit_cost_inr": 88000.0, "lead_time_days": 21,
     "supplier": "Fenner Conveyor", "criticality_override": "high"},
    # HPU-01 (hydraulic_unit) — pump stockout, filter ok
    {"asset_id": "HPU-01", "part_number": "FILT-HPU-010",
     "part_name": "Hydraulic Return-Line Filter Element", "compatible_equipment": ["HPU-01"],
     "stock_qty": 8, "min_stock_qty": 4, "unit_cost_inr": 2100.0, "lead_time_days": 3,
     "supplier": "Bosch Rexroth India", "criticality_override": ""},
    {"asset_id": "HPU-01", "part_number": "HPU-PMP-90",
     "part_name": "Axial Piston Hydraulic Pump 90cc", "compatible_equipment": ["HPU-01"],
     "stock_qty": 0, "min_stock_qty": 1, "unit_cost_inr": 124000.0, "lead_time_days": 30,
     "supplier": "Bosch Rexroth India", "criticality_override": "critical"},
]


def seed_demo_spare_parts(db_path: Optional[Path] = None) -> int:
    """
    Idempotent spare-parts seeder — PS §4.3 / §5.3 compliance.

    Seeds SparePart rows per demo asset (matched by asset_id) with a realistic
    mix of in-stock and out-of-stock parts, so the WRPS spare-availability
    factor and the spare-procurement recommendation genuinely fire.

    Rows are keyed on (asset_id, part_number) — re-running skips existing rows.
    """
    init_db(db_path)
    inserted = 0
    with session_scope(db_path) as session:
        for raw in _SEED_SPARES:
            existing = session.exec(
                select(SparePart).where(
                    SparePart.asset_id == raw["asset_id"],
                    SparePart.part_number == raw["part_number"],
                )
            ).first()
            if existing is not None:
                continue
            session.add(SparePart(
                asset_id=raw["asset_id"],
                plant_area=raw.get("plant_area", "unspecified"),
                part_number=raw["part_number"],
                part_name=raw["part_name"],
                compatible_equipment=raw.get("compatible_equipment", []),
                stock_qty=raw["stock_qty"],
                min_stock_qty=raw["min_stock_qty"],
                unit_cost_inr=raw.get("unit_cost_inr", 0.0),
                lead_time_days=raw["lead_time_days"],
                supplier=raw.get("supplier", "unknown"),
                criticality_override=raw.get("criticality_override", ""),
            ))
            inserted += 1
        if inserted:
            session.flush()
    logger.info("seed_demo_spare_parts: %d new SparePart rows inserted", inserted)
    return inserted


# ---------------------------------------------------------------------------
# AI4I ingest convenience
# ---------------------------------------------------------------------------

def ingest_ai4i_rows(
    df: pd.DataFrame,
    session: Optional[Session] = None,
    batch_size: int = 500,
) -> int:
    """
    Ingest AI4I 2020 rows as SensorSummary entities.
    Expects df to be output of frame_ai4i() so 'equipment_id' and
    'sensor_readings' columns are present.

    Returns number of rows written.
    """
    if "equipment_id" not in df.columns:
        df = frame_ai4i(df)

    if session is not None:
        return _ingest_ai4i_rows_inner(df, session, batch_size)

    # No caller-supplied session — use session_scope() so writes are committed.
    with session_scope() as _session:
        return _ingest_ai4i_rows_inner(df, _session, batch_size)


def _ingest_ai4i_rows_inner(
    df: pd.DataFrame,
    session: Session,
    batch_size: int,
) -> int:
    """Inner worker — assumes session lifecycle is managed by caller."""
    base_time = datetime.utcnow()
    written = 0
    batch: List[SensorSummary] = []

    for idx, row in df.iterrows():
        win_start = base_time + timedelta(minutes=int(idx))
        win_end   = win_start + timedelta(minutes=1)
        readings  = row.get("sensor_readings", {})
        if not isinstance(readings, dict):
            readings = {}

        entity = SensorSummary(
            asset_id=str(row.get("equipment_id", "ROLL-UNKNOWN")),
            plant_area=str(row.get("plant_area", "HSM-Bay-1")),
            source_system="generated",
            window_start=win_start,
            window_end=win_end,
            sensor_readings=readings,
            operating_condition="normal" if row.get("machine_failure", 0) == 0 else "severe",
        )
        batch.append(entity)

        if len(batch) >= batch_size:
            session.add_all(batch)
            session.flush()
            written += len(batch)
            batch = []

    if batch:
        session.add_all(batch)
        session.flush()
        written += len(batch)

    logger.info("ingest_ai4i_rows: %d rows written", written)
    return written
