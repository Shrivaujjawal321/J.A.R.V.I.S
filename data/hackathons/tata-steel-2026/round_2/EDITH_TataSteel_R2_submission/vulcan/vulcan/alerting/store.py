"""VULCAN alert store — SQLite persistence for fired alerts (FR7 + reporting).

A tiny, fail-soft sqlite table that records every fired :class:`AlertEvent`.
The report layer reads it back to build an alert report; the feedback loop links
an engineer's outcome to a specific alert. Pure stdlib `sqlite3`, one file at
`<package_root>/data/vulcan_alerts.db`. Degrades to an in-memory list on any DB
error so the alerting loop never crashes.
"""

from __future__ import annotations

import logging
import sqlite3
import threading
import time
from pathlib import Path
from typing import Any, Optional

log = logging.getLogger("vulcan.alerting.store")

_SCHEMA = """
CREATE TABLE IF NOT EXISTS alerts (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    fired_at    REAL NOT NULL,             -- wall-clock when recorded
    ts          TEXT,                      -- source-data timestamp
    asset_id    TEXT NOT NULL,
    sensor      TEXT,
    value       REAL,
    severity    TEXT NOT NULL,             -- WARNING | ALARM | CRITICAL
    severity_rank INTEGER,
    warning_threshold REAL,
    alarm_threshold   REAL,
    unit        TEXT,
    standard    TEXT,
    row_index   INTEGER,
    scenario_id TEXT,
    fault_label INTEGER,
    reason      TEXT,
    source      TEXT
);
CREATE INDEX IF NOT EXISTS ix_alerts_asset ON alerts(asset_id, id);
CREATE INDEX IF NOT EXISTS ix_alerts_sev   ON alerts(severity_rank);
"""


class AlertStore:
    def __init__(self, db_path: Path | str | None = None) -> None:
        self._lock = threading.Lock()
        self._mem: list[dict[str, Any]] = []
        self._conn: Optional[sqlite3.Connection] = None
        try:
            if db_path is None:
                from ..config import get_settings
                db_path = get_settings().package_root / "data" / "vulcan_alerts.db"
            p = Path(db_path)
            p.parent.mkdir(parents=True, exist_ok=True)
            self._conn = sqlite3.connect(str(p), check_same_thread=False)
            self._conn.executescript(_SCHEMA)
            self._conn.commit()
            self.path = str(p)
        except Exception as exc:  # noqa: BLE001
            log.warning("AlertStore falling back to in-memory: %s", exc)
            self._conn = None
            self.path = ":memory-fallback:"

    # ------------------------------------------------------------------
    def record(self, ev: Any) -> int:
        """Persist one AlertEvent. Returns the row id (or -1 on memory fallback)."""
        d = ev.to_dict() if hasattr(ev, "to_dict") else dict(ev)
        d["fired_at"] = time.time()
        if self._conn is None:
            self._mem.append(d)
            return -1
        try:
            with self._lock:
                cur = self._conn.execute(
                    "INSERT INTO alerts (fired_at, ts, asset_id, sensor, value, "
                    "severity, severity_rank, warning_threshold, alarm_threshold, "
                    "unit, standard, row_index, scenario_id, fault_label, reason, source) "
                    "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (d["fired_at"], d.get("timestamp"), d["asset_id"], d.get("sensor"),
                     d.get("value"), d["severity"], d.get("severity_rank"),
                     d.get("warning_threshold"), d.get("alarm_threshold"),
                     d.get("unit"), d.get("standard"), d.get("row_index"),
                     d.get("scenario_id"), d.get("fault_label"), d.get("reason"),
                     d.get("source")),
                )
                self._conn.commit()
                return int(cur.lastrowid or -1)
        except Exception as exc:  # noqa: BLE001
            log.warning("alert record failed (%s) — memory fallback", exc)
            self._mem.append(d)
            return -1

    # ------------------------------------------------------------------
    def recent(self, asset_id: Optional[str] = None, limit: int = 50
               ) -> list[dict[str, Any]]:
        """Most-recent fired alerts (optionally filtered to one asset)."""
        if self._conn is None:
            rows = [r for r in self._mem
                    if asset_id is None or r["asset_id"] == asset_id]
            return rows[-limit:][::-1]
        try:
            with self._lock:
                if asset_id:
                    cur = self._conn.execute(
                        "SELECT * FROM alerts WHERE asset_id=? ORDER BY id DESC LIMIT ?",
                        (asset_id, limit))
                else:
                    cur = self._conn.execute(
                        "SELECT * FROM alerts ORDER BY id DESC LIMIT ?", (limit,))
                cols = [c[0] for c in cur.description]
                return [dict(zip(cols, row)) for row in cur.fetchall()]
        except Exception as exc:  # noqa: BLE001
            log.warning("alert recent failed (%s)", exc)
            return self._mem[-limit:][::-1]

    def counts(self, asset_id: Optional[str] = None) -> dict[str, int]:
        """Severity counts (for the alert report header)."""
        rows = self.recent(asset_id=asset_id, limit=100000)
        out: dict[str, int] = {}
        for r in rows:
            out[r["severity"]] = out.get(r["severity"], 0) + 1
        return out

    def clear(self, asset_id: Optional[str] = None) -> None:
        if asset_id is None:
            self._mem.clear()
        else:
            self._mem = [r for r in self._mem if r["asset_id"] != asset_id]
        if self._conn is None:
            return
        try:
            with self._lock:
                if asset_id:
                    self._conn.execute("DELETE FROM alerts WHERE asset_id=?", (asset_id,))
                else:
                    self._conn.execute("DELETE FROM alerts")
                self._conn.commit()
        except Exception as exc:  # noqa: BLE001
            log.warning("alert clear failed (%s)", exc)


_STORE: Optional[AlertStore] = None


def get_alert_store() -> AlertStore:
    global _STORE
    if _STORE is None:
        _STORE = AlertStore()
    return _STORE
