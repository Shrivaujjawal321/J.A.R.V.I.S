"""VULCAN conversation memory — per-session SQLite store (FR3 multi-turn).

Keeps turn-by-turn dialogue + a small rolling "focus" of the entities the
conversation is about (the current asset, scenario, last diagnosis) so follow-up
questions like "and what spare does it need?" resolve against the right machine
without the engineer repeating themselves.

Pure stdlib `sqlite3`. CPU/keyless/offline. One file per deployment at
`<package_root>/data/vulcan_sessions.db`. Fail-soft: any DB error degrades to an
in-process dict so a turn never crashes on storage.
"""

from __future__ import annotations

import json
import logging
import sqlite3
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

log = logging.getLogger("vulcan.memory")

_SCHEMA = """
CREATE TABLE IF NOT EXISTS turns (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id  TEXT NOT NULL,
    ts          REAL NOT NULL,
    role        TEXT NOT NULL,          -- 'user' | 'assistant'
    content     TEXT NOT NULL,
    intent      TEXT,                   -- diagnosis | rca | rul | ... (assistant turns)
    focus_json  TEXT                    -- snapshot of conversation focus after this turn
);
CREATE INDEX IF NOT EXISTS ix_turns_session ON turns(session_id, id);

CREATE TABLE IF NOT EXISTS focus (
    session_id  TEXT PRIMARY KEY,
    asset_id    TEXT,
    scenario_id TEXT,
    last_intent TEXT,
    data_json   TEXT,                   -- arbitrary carried slots
    updated     REAL
);
"""


@dataclass
class Turn:
    role: str
    content: str
    intent: str | None = None
    ts: float = field(default_factory=time.time)


@dataclass
class Focus:
    """The rolling 'what are we talking about' state for a session."""

    asset_id: str | None = None
    scenario_id: str | None = None
    last_intent: str | None = None
    data: dict[str, Any] = field(default_factory=dict)

    def update(self, **kw: Any) -> "Focus":
        for k, v in kw.items():
            if v in (None, "", []):
                continue
            if k in ("asset_id", "scenario_id", "last_intent"):
                setattr(self, k, v)
            else:
                self.data[k] = v
        return self

    def to_dict(self) -> dict[str, Any]:
        return {
            "asset_id": self.asset_id,
            "scenario_id": self.scenario_id,
            "last_intent": self.last_intent,
            "data": self.data,
        }


class ConversationStore:
    """SQLite-backed multi-turn store. Thread-safe (one lock, short txns)."""

    def __init__(self, db_path: Path | str | None = None) -> None:
        self._lock = threading.Lock()
        self._mem_fallback: dict[str, list[Turn]] = {}
        self._focus_fallback: dict[str, Focus] = {}
        self._conn: sqlite3.Connection | None = None
        try:
            if db_path is None:
                from ..config import get_settings
                db_path = get_settings().package_root / "data" / "vulcan_sessions.db"
            p = Path(db_path)
            p.parent.mkdir(parents=True, exist_ok=True)
            self._conn = sqlite3.connect(str(p), check_same_thread=False)
            self._conn.executescript(_SCHEMA)
            self._conn.commit()
            self.path = str(p)
        except Exception as exc:  # noqa: BLE001 — degrade to in-memory
            log.warning("ConversationStore falling back to in-memory: %s", exc)
            self._conn = None
            self.path = ":memory-fallback:"

    # --- writes ----------------------------------------------------------
    def add_turn(
        self,
        session_id: str,
        role: str,
        content: str,
        *,
        intent: str | None = None,
        focus: Focus | None = None,
    ) -> None:
        turn = Turn(role=role, content=content, intent=intent)
        if self._conn is None:
            self._mem_fallback.setdefault(session_id, []).append(turn)
            return
        try:
            with self._lock:
                self._conn.execute(
                    "INSERT INTO turns (session_id, ts, role, content, intent, focus_json) "
                    "VALUES (?,?,?,?,?,?)",
                    (session_id, turn.ts, role, content, intent,
                     json.dumps(focus.to_dict()) if focus else None),
                )
                self._conn.commit()
        except Exception as exc:  # noqa: BLE001
            log.warning("add_turn failed (%s) — using memory fallback", exc)
            self._mem_fallback.setdefault(session_id, []).append(turn)

    def save_focus(self, session_id: str, focus: Focus) -> None:
        if self._conn is None:
            self._focus_fallback[session_id] = focus
            return
        try:
            with self._lock:
                self._conn.execute(
                    "INSERT INTO focus (session_id, asset_id, scenario_id, last_intent, "
                    "data_json, updated) VALUES (?,?,?,?,?,?) "
                    "ON CONFLICT(session_id) DO UPDATE SET asset_id=excluded.asset_id, "
                    "scenario_id=excluded.scenario_id, last_intent=excluded.last_intent, "
                    "data_json=excluded.data_json, updated=excluded.updated",
                    (session_id, focus.asset_id, focus.scenario_id, focus.last_intent,
                     json.dumps(focus.data), time.time()),
                )
                self._conn.commit()
        except Exception as exc:  # noqa: BLE001
            log.warning("save_focus failed (%s)", exc)
            self._focus_fallback[session_id] = focus

    # --- reads -----------------------------------------------------------
    def history(self, session_id: str, limit: int = 12) -> list[Turn]:
        if self._conn is None:
            return self._mem_fallback.get(session_id, [])[-limit:]
        try:
            with self._lock:
                rows = self._conn.execute(
                    "SELECT role, content, intent, ts FROM turns WHERE session_id=? "
                    "ORDER BY id DESC LIMIT ?",
                    (session_id, limit),
                ).fetchall()
            return [Turn(role=r[0], content=r[1], intent=r[2], ts=r[3]) for r in reversed(rows)]
        except Exception as exc:  # noqa: BLE001
            log.warning("history failed (%s)", exc)
            return self._mem_fallback.get(session_id, [])[-limit:]

    def get_focus(self, session_id: str) -> Focus:
        if self._conn is None:
            return self._focus_fallback.get(session_id, Focus())
        try:
            with self._lock:
                row = self._conn.execute(
                    "SELECT asset_id, scenario_id, last_intent, data_json FROM focus "
                    "WHERE session_id=?", (session_id,),
                ).fetchone()
            if not row:
                return Focus()
            return Focus(
                asset_id=row[0], scenario_id=row[1], last_intent=row[2],
                data=json.loads(row[3]) if row[3] else {},
            )
        except Exception as exc:  # noqa: BLE001
            log.warning("get_focus failed (%s)", exc)
            return self._focus_fallback.get(session_id, Focus())

    def render_history(self, session_id: str, limit: int = 8) -> str:
        """Compact transcript for prompt injection (multi-turn grounding)."""
        turns = self.history(session_id, limit=limit)
        if not turns:
            return ""
        lines = []
        for t in turns:
            who = "Engineer" if t.role == "user" else "EDITH"
            lines.append(f"{who}: {t.content.strip()[:500]}")
        return "\n".join(lines)

    def clear(self, session_id: str) -> None:
        self._mem_fallback.pop(session_id, None)
        self._focus_fallback.pop(session_id, None)
        if self._conn is None:
            return
        try:
            with self._lock:
                self._conn.execute("DELETE FROM turns WHERE session_id=?", (session_id,))
                self._conn.execute("DELETE FROM focus WHERE session_id=?", (session_id,))
                self._conn.commit()
        except Exception as exc:  # noqa: BLE001
            log.warning("clear failed (%s)", exc)


# module-level singleton (lazy)
_STORE: ConversationStore | None = None


def get_store() -> ConversationStore:
    global _STORE
    if _STORE is None:
        _STORE = ConversationStore()
    return _STORE
