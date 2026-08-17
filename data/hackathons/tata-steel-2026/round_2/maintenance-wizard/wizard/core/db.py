"""
wizard.core.db
==============
SQLModel engine init for SQLite `data/wizard.db`.

Features:
- WAL mode (Write-Ahead Logging) — eliminates concurrent write contention
  between the FastAPI server and the APScheduler alerting evaluator
- create_all() creates all SQLModel table classes on first run
- get_session() is a generator-based context manager for FastAPI Depends()
  and for direct use in scripts

Usage::

    # FastAPI dependency injection
    from wizard.core.db import get_session
    from sqlmodel import Session, select

    @app.get("/assets/{asset_id}")
    def get_asset(asset_id: str, session: Session = Depends(get_session)):
        ...

    # Script usage
    with next(get_session()) as session:
        results = session.exec(select(AssetProfile)).all()

    # One-time init (called at app startup)
    from wizard.core.db import init_db
    init_db()
"""

from __future__ import annotations

import logging
from contextlib import contextmanager
from pathlib import Path
from typing import Generator

from sqlalchemy import event, text
from sqlmodel import Session, SQLModel, create_engine

logger = logging.getLogger(__name__)


def _get_db_url(db_path: Path | str | None = None) -> str:
    """
    Build the SQLite connection URL.
    If db_path is None, reads from wizard.core.config.settings.
    """
    if db_path is None:
        try:
            from wizard.core.config import settings
            db_path = settings.resolved_db_path()
        except Exception:
            db_path = Path("data/wizard.db")

    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return f"sqlite:///{db_path.resolve()}"


def _enable_wal(dbapi_conn: object, _: object) -> None:
    """
    SQLite event listener: enable WAL mode + foreign keys on every new connection.
    WAL allows concurrent readers + one writer — critical for FastAPI + APScheduler.
    """
    # dbapi_conn is a sqlite3.Connection at runtime
    cursor = dbapi_conn.cursor()  # type: ignore[union-attr]
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.execute("PRAGMA synchronous=NORMAL")
    cursor.execute("PRAGMA cache_size=-32000")  # 32 MB page cache
    cursor.close()


_engines: dict[str, object] = {}  # per-resolved-URL engine cache


def get_engine(db_path: Path | str | None = None):
    """
    Return a SQLAlchemy engine for the given db_path (per-path singleton).

    Engines are cached by their resolved SQLite URL so that:
    - The production path (None → settings.resolved_db_path()) always returns
      the same engine.
    - Tests / scripts that pass an explicit tmp db_path each get their OWN
      engine and never hit the wrong database.

    Replaces the old single-global ``_engine`` which silently reused the first
    engine for any subsequent call regardless of ``db_path``.
    """
    url = _get_db_url(db_path)
    if url not in _engines:
        engine = create_engine(
            url,
            connect_args={"check_same_thread": False},
            echo=False,  # set to True for SQL debug logging
        )
        event.listen(engine, "connect", _enable_wal)
        logger.info("SQLite engine created: %s", url)
        _engines[url] = engine
    return _engines[url]


def init_db(db_path: Path | str | None = None) -> None:
    """
    Create all tables defined in SQLModel table models.

    Import order matters: all table models must be imported before calling
    create_all() so their metadata is registered. We import schemas here
    to guarantee that.

    Safe to call multiple times — SQLModel's create_all is idempotent
    (it uses CREATE TABLE IF NOT EXISTS under the hood).
    """
    # Ensure all table models are registered in SQLModel metadata
    from wizard.core import schemas as _schemas  # noqa: F401 (side-effect import)

    engine = get_engine(db_path)
    SQLModel.metadata.create_all(engine)
    logger.info("SQLite tables created / verified (wizard.db)")

    # Create indexes that are not handled by SQLModel Field(index=True)
    with engine.connect() as conn:
        _ensure_indexes(conn)


def _ensure_indexes(conn: object) -> None:
    """
    Create any additional composite or functional indexes not covered by
    SQLModel's auto-index generation. Safe to call repeatedly (IF NOT EXISTS).
    """
    indexes = [
        # AnomalyAlert: unacknowledged + critical alerts — the hottest query
        (
            "idx_anomaly_alert_unack_risk",
            "CREATE INDEX IF NOT EXISTS idx_anomaly_alert_unack_risk "
            "ON anomaly_alert (acknowledged, risk_level, triggered_at DESC)"
        ),
        # SensorSummary: latest window per asset
        (
            "idx_sensor_summary_asset_window",
            "CREATE INDEX IF NOT EXISTS idx_sensor_summary_asset_window "
            "ON sensor_summary (asset_id, window_end DESC)"
        ),
        # FaultLog: confirmed faults per asset (prioritization join query)
        (
            "idx_fault_log_asset_confirmed",
            "CREATE INDEX IF NOT EXISTS idx_fault_log_asset_confirmed "
            "ON fault_log (asset_id, confirmed, detected_at DESC)"
        ),
        # MaintenanceRecord: latest events per asset
        (
            "idx_maint_record_asset_performed",
            "CREATE INDEX IF NOT EXISTS idx_maint_record_asset_performed "
            "ON maintenance_record (asset_id, performed_at DESC)"
        ),
        # SparePart: low-stock parts — for the spares warning
        (
            "idx_spare_part_asset_stock",
            "CREATE INDEX IF NOT EXISTS idx_spare_part_asset_stock "
            "ON spare_part (asset_id, stock_qty)"
        ),
    ]

    for idx_name, ddl in indexes:
        try:
            conn.execute(text(ddl))  # type: ignore[union-attr]
        except Exception as exc:
            logger.warning("Index %s: %s", idx_name, exc)

    conn.commit()  # type: ignore[union-attr]


def get_session(db_path: Path | str | None = None) -> Generator[Session, None, None]:
    """
    FastAPI dependency. Use ONLY as ``Depends(get_session)`` — FastAPI advances
    and closes the generator correctly, so the post-yield commit runs.

        @app.get("/x")
        def handler(session: Session = Depends(get_session)):
            ...

    For scripts / tests / background jobs, use ``session_scope()`` instead — the
    bare ``with next(get_session()) as s:`` pattern does NOT trigger the commit
    (the generator is never advanced past the yield), so writes are silently lost.
    """
    engine = get_engine(db_path)
    with Session(engine, expire_on_commit=False) as session:
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise


@contextmanager
def session_scope(db_path: Path | str | None = None) -> Generator[Session, None, None]:
    """
    Transactional session context manager for scripts, tests, and background
    jobs. Commits on clean exit, rolls back on exception, always closes.

        from wizard.core.db import session_scope
        with session_scope() as session:
            session.add(obj)        # committed automatically on block exit
    """
    engine = get_engine(db_path)
    session = Session(engine, expire_on_commit=False)
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def reset_db(db_path: Path | str | None = None) -> None:
    """
    DROP all tables and re-create. Only for `make reset` / tests.
    NEVER call in production or demo — data loss is permanent.
    """
    from wizard.core import schemas as _schemas  # noqa: F401

    url = _get_db_url(db_path)
    engine = get_engine(db_path)
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    # Evict from per-path cache so next call gets a fresh connection pool
    _engines.pop(url, None)
    logger.warning("Database RESET — all tables dropped and recreated")
