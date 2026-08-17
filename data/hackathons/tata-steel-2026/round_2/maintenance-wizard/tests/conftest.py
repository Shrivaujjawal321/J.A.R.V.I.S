"""
tests/conftest.py
=================
Shared pytest fixtures for the Maintenance Wizard test suite.

Provides:
    - tmp_db_path: a temporary SQLite file path (deleted after test)
    - session: a SQLModel session backed by a fresh in-memory DB per test
    - sample_asset: an AssetProfile for EAF-04 (the scripted demo asset)
"""

from __future__ import annotations

import os
import tempfile
from typing import Generator

import pytest
from sqlmodel import Session


@pytest.fixture(scope="function")
def tmp_db_path() -> Generator[str, None, None]:
    """Yield a temporary .db file path; delete after the test."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        path = f.name
    try:
        yield path
    finally:
        try:
            os.unlink(path)
        except FileNotFoundError:
            pass


@pytest.fixture(scope="function")
def db_session(tmp_db_path: str) -> Generator[Session, None, None]:
    """
    Yield a SQLModel session backed by a fresh temp SQLite DB.
    All tables are created before the test; DB is discarded after.
    """
    from wizard.core.db import get_engine, init_db

    # Reset module-level engine singleton so each test gets a fresh one
    import wizard.core.db as _db_module
    _db_module._engine = None

    init_db(tmp_db_path)
    with next(
        __import__("wizard.core.db", fromlist=["get_session"]).get_session(tmp_db_path)
    ) as session:
        yield session

    # Reset singleton again so other tests don't inherit this engine
    _db_module._engine = None


@pytest.fixture
def sample_asset():
    """Return a minimal AssetProfile for EAF-04 (not yet persisted)."""
    from datetime import datetime
    from wizard.core.schemas import AssetProfile
    return AssetProfile(
        asset_id="EAF-04",
        plant_area="EAF-Bay-1",
        equipment_name="EAF-04 Electrode Drive",
        equipment_class="hydraulic_unit",
        manufacturer="ABB",
        installation_date=datetime(2018, 6, 1),
        criticality_tier="critical",
        subsystem="electrode-column",
        iso14224_taxonomy="electrical.arc_furnace.electrode_drive",
    )


@pytest.fixture
def sample_sensor(sample_asset):
    """Return a SensorSummary for EAF-04 in degraded state."""
    from datetime import datetime, timedelta
    from wizard.core.schemas import SensorSummary
    return SensorSummary(
        asset_id=sample_asset.asset_id,
        plant_area=sample_asset.plant_area,
        window_start=datetime.utcnow() - timedelta(minutes=15),
        window_end=datetime.utcnow(),
        sensor_readings={
            "temperature_c": 89.4,
            "pressure_bar": 12.1,
            "vibration_mm_s": 7.8,
            "rpm": 1450.0,
            "torque_nm": 312.0,
            "current_a": 48.2,
        },
        anomaly_score=0.71,
        rul_days_p50=11.4,
    )
