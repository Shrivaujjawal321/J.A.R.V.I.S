"""VULCAN feedback loop — engineer-in-the-loop, prioritization-adjusting (FR6).

When an engineer confirms, corrects, or closes out a VULCAN diagnosis, that
verdict is stored AND folded into a per-(asset, scenario) **priority weight** that
nudges future risk scoring. The mechanism is deliberately simple, transparent,
and auditable (no opaque online-learning): an exponential-recency update on a
bounded multiplier.

How the weight moves
--------------------
Each (asset_id, scenario_id) carries a weight `w` (default 1.0, clamped to
[`W_MIN`, `W_MAX`]). On feedback:

    confirm  (diagnosis was right)            -> nudge UP   (trust this path more)
    correct  (diagnosis was wrong)            -> nudge DOWN (de-prioritise this path)
    outcome=failure / false_negative          -> strong UP  (we under-called it)
    outcome=no_fault / false_positive         -> DOWN       (we over-called it)

Update rule (EMA toward a target, recency-weighted by `alpha`):
    w <- clamp( w + alpha * (target - w) )

The :class:`PrioritizerAgent` reads `priority_weight(asset, scenario)` and adds a
small, fully-traced `+/-` term to its risk score — so the system demonstrably
*learns from the engineer* across runs while staying explainable.

Storage: pure stdlib `sqlite3` at `<package_root>/data/vulcan_feedback.db`.
Fail-soft: any DB error degrades to an in-process dict; a turn never crashes.
"""

from __future__ import annotations

import json
import logging
import sqlite3
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

log = logging.getLogger("vulcan.feedback")

# weight bounds + update aggressiveness
W_DEFAULT = 1.0
W_MIN = 0.5
W_MAX = 1.6
ALPHA = 0.35                       # recency: higher = newer feedback dominates

# per-verdict EMA targets (where the weight is pulled toward)
_TARGETS: dict[str, float] = {
    "confirm": 1.30,               # confirmed-correct -> trust path more
    "correct": 0.70,               # corrected -> de-prioritise this mapping
    "false_negative": 1.55,        # we missed it -> push hard toward higher priority
    "false_positive": 0.60,        # we over-called -> pull down
    "neutral": 1.0,
}
# verdicts that double as an "outcome" signal
_OUTCOME_TARGET: dict[str, float] = {
    "failure": 1.50,               # asset did fail -> we should prioritise it more
    "true_positive": 1.30,
    "no_fault": 0.65,              # no fault found -> over-called
    "false_alarm": 0.60,
    "resolved": 1.0,
}

_SCHEMA = """
CREATE TABLE IF NOT EXISTS feedback (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at  REAL NOT NULL,
    asset_id    TEXT NOT NULL,
    scenario_id TEXT,
    verdict     TEXT NOT NULL,         -- confirm | correct | false_negative | false_positive | neutral
    outcome     TEXT,                  -- failure | no_fault | resolved | ...
    corrected_scenario_id TEXT,        -- if engineer says the real scenario was X
    engineer    TEXT,
    note        TEXT,
    risk_band_at_time TEXT,            -- the band VULCAN had shown (for audit)
    weight_before REAL,
    weight_after  REAL
);
CREATE INDEX IF NOT EXISTS ix_fb_asset ON feedback(asset_id, scenario_id);

CREATE TABLE IF NOT EXISTS priority_weights (
    asset_id    TEXT NOT NULL,
    scenario_id TEXT NOT NULL,        -- '' = asset-level (scenario-agnostic) weight
    weight      REAL NOT NULL,
    n_updates   INTEGER NOT NULL DEFAULT 0,
    updated_at  REAL,
    PRIMARY KEY (asset_id, scenario_id)
);
"""


def _clamp(w: float) -> float:
    return max(W_MIN, min(W_MAX, w))


@dataclass
class FeedbackResult:
    """The effect of one feedback submission — shows the weight actually moved."""

    asset_id: str
    scenario_id: str
    verdict: str
    outcome: Optional[str]
    weight_before: float
    weight_after: float
    n_updates: int

    @property
    def delta(self) -> float:
        return round(self.weight_after - self.weight_before, 4)

    def to_dict(self) -> dict[str, Any]:
        return {
            "asset_id": self.asset_id,
            "scenario_id": self.scenario_id,
            "verdict": self.verdict,
            "outcome": self.outcome,
            "weight_before": round(self.weight_before, 4),
            "weight_after": round(self.weight_after, 4),
            "delta": self.delta,
            "n_updates": self.n_updates,
            "direction": ("UP" if self.delta > 0 else "DOWN" if self.delta < 0 else "FLAT"),
        }


class FeedbackStore:
    """SQLite-backed feedback + priority-weight store (FR6). Thread-safe, fail-soft."""

    def __init__(self, db_path: Path | str | None = None) -> None:
        self._lock = threading.Lock()
        self._conn: Optional[sqlite3.Connection] = None
        self._mem_weights: dict[tuple[str, str], tuple[float, int]] = {}
        self._mem_fb: list[dict[str, Any]] = []
        try:
            if db_path is None:
                from .config import get_settings
                db_path = get_settings().package_root / "data" / "vulcan_feedback.db"
            p = Path(db_path)
            p.parent.mkdir(parents=True, exist_ok=True)
            self._conn = sqlite3.connect(str(p), check_same_thread=False)
            self._conn.executescript(_SCHEMA)
            self._conn.commit()
            self.path = str(p)
        except Exception as exc:  # noqa: BLE001
            log.warning("FeedbackStore falling back to in-memory: %s", exc)
            self._conn = None
            self.path = ":memory-fallback:"

    # --- weight reads -----------------------------------------------------
    def get_weight(self, asset_id: str, scenario_id: str | None = None
                   ) -> tuple[float, int]:
        """Return (weight, n_updates) for an (asset, scenario). Scenario '' / None
        is the asset-level fallback. A missing row -> (W_DEFAULT, 0)."""
        sid = scenario_id or ""
        if self._conn is None:
            return self._mem_weights.get((asset_id, sid), (W_DEFAULT, 0))
        try:
            with self._lock:
                row = self._conn.execute(
                    "SELECT weight, n_updates FROM priority_weights "
                    "WHERE asset_id=? AND scenario_id=?", (asset_id, sid)).fetchone()
            return (float(row[0]), int(row[1])) if row else (W_DEFAULT, 0)
        except Exception as exc:  # noqa: BLE001
            log.warning("get_weight failed (%s)", exc)
            return self._mem_weights.get((asset_id, sid), (W_DEFAULT, 0))

    def priority_weight(self, asset_id: str, scenario_id: str | None = None) -> float:
        """The effective priority multiplier for risk scoring.

        Prefers the scenario-specific weight; if that scenario has never had
        feedback, falls back to the asset-level weight; else 1.0 (neutral)."""
        if scenario_id:
            w, n = self.get_weight(asset_id, scenario_id)
            if n > 0:
                return w
        w_asset, n_asset = self.get_weight(asset_id, "")
        return w_asset if n_asset > 0 else W_DEFAULT

    def _set_weight(self, asset_id: str, sid: str, w: float, n: int) -> None:
        if self._conn is None:
            self._mem_weights[(asset_id, sid)] = (w, n)
            return
        try:
            with self._lock:
                self._conn.execute(
                    "INSERT INTO priority_weights (asset_id, scenario_id, weight, "
                    "n_updates, updated_at) VALUES (?,?,?,?,?) "
                    "ON CONFLICT(asset_id, scenario_id) DO UPDATE SET "
                    "weight=excluded.weight, n_updates=excluded.n_updates, "
                    "updated_at=excluded.updated_at",
                    (asset_id, sid, w, n, time.time()))
                self._conn.commit()
        except Exception as exc:  # noqa: BLE001
            log.warning("_set_weight failed (%s)", exc)
            self._mem_weights[(asset_id, sid)] = (w, n)

    # --- the update -------------------------------------------------------
    def submit(
        self,
        *,
        asset_id: str,
        scenario_id: str | None = None,
        verdict: str = "confirm",
        outcome: str | None = None,
        corrected_scenario_id: str | None = None,
        engineer: str | None = None,
        note: str | None = None,
        risk_band_at_time: str | None = None,
    ) -> FeedbackResult:
        """Record one feedback item and update the priority weight (EMA).

        Returns a :class:`FeedbackResult` proving the weight moved. The scenario-
        specific AND the asset-level weights are both nudged (asset-level half as
        hard) so even a never-before-seen scenario inherits a sensible prior.
        """
        verdict = (verdict or "neutral").strip().lower()
        outcome_norm = (outcome or "").strip().lower() or None
        sid = scenario_id or ""

        # target: verdict drives it; an explicit outcome can override/strengthen
        target = _TARGETS.get(verdict, W_DEFAULT)
        if outcome_norm and outcome_norm in _OUTCOME_TARGET:
            # combine: take the more extreme pull (further from 1.0)
            ot = _OUTCOME_TARGET[outcome_norm]
            target = ot if abs(ot - 1.0) > abs(target - 1.0) else target

        # scenario-level EMA
        w_before, n_before = self.get_weight(asset_id, sid)
        w_after = _clamp(w_before + ALPHA * (target - w_before))
        self._set_weight(asset_id, sid, w_after, n_before + 1)

        # asset-level EMA (softer — half alpha) so the prior generalises
        if sid:
            aw_before, an_before = self.get_weight(asset_id, "")
            aw_after = _clamp(aw_before + (ALPHA * 0.5) * (target - aw_before))
            self._set_weight(asset_id, "", aw_after, an_before + 1)

        # record the raw feedback row (audit trail)
        rec = {
            "created_at": time.time(), "asset_id": asset_id, "scenario_id": scenario_id,
            "verdict": verdict, "outcome": outcome_norm,
            "corrected_scenario_id": corrected_scenario_id, "engineer": engineer,
            "note": note, "risk_band_at_time": risk_band_at_time,
            "weight_before": w_before, "weight_after": w_after,
        }
        if self._conn is None:
            self._mem_fb.append(rec)
        else:
            try:
                with self._lock:
                    self._conn.execute(
                        "INSERT INTO feedback (created_at, asset_id, scenario_id, "
                        "verdict, outcome, corrected_scenario_id, engineer, note, "
                        "risk_band_at_time, weight_before, weight_after) "
                        "VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                        (rec["created_at"], asset_id, scenario_id, verdict, outcome_norm,
                         corrected_scenario_id, engineer, note, risk_band_at_time,
                         w_before, w_after))
                    self._conn.commit()
            except Exception as exc:  # noqa: BLE001
                log.warning("feedback insert failed (%s)", exc)
                self._mem_fb.append(rec)

        return FeedbackResult(
            asset_id=asset_id, scenario_id=sid, verdict=verdict, outcome=outcome_norm,
            weight_before=w_before, weight_after=w_after, n_updates=n_before + 1,
        )

    # --- reads ------------------------------------------------------------
    def history(self, asset_id: str | None = None, limit: int = 50
                ) -> list[dict[str, Any]]:
        if self._conn is None:
            rows = [r for r in self._mem_fb
                    if asset_id is None or r["asset_id"] == asset_id]
            return rows[-limit:][::-1]
        try:
            with self._lock:
                if asset_id:
                    cur = self._conn.execute(
                        "SELECT * FROM feedback WHERE asset_id=? ORDER BY id DESC LIMIT ?",
                        (asset_id, limit))
                else:
                    cur = self._conn.execute(
                        "SELECT * FROM feedback ORDER BY id DESC LIMIT ?", (limit,))
                cols = [c[0] for c in cur.description]
                return [dict(zip(cols, row)) for row in cur.fetchall()]
        except Exception as exc:  # noqa: BLE001
            log.warning("feedback history failed (%s)", exc)
            return self._mem_fb[-limit:][::-1]

    def all_weights(self) -> list[dict[str, Any]]:
        if self._conn is None:
            return [{"asset_id": a, "scenario_id": s, "weight": w, "n_updates": n}
                    for (a, s), (w, n) in self._mem_weights.items()]
        try:
            with self._lock:
                cur = self._conn.execute(
                    "SELECT asset_id, scenario_id, weight, n_updates, updated_at "
                    "FROM priority_weights ORDER BY asset_id, scenario_id")
                cols = [c[0] for c in cur.description]
                return [dict(zip(cols, row)) for row in cur.fetchall()]
        except Exception as exc:  # noqa: BLE001
            log.warning("all_weights failed (%s)", exc)
            return []

    def clear(self) -> None:
        self._mem_weights.clear()
        self._mem_fb.clear()
        if self._conn is None:
            return
        try:
            with self._lock:
                self._conn.execute("DELETE FROM feedback")
                self._conn.execute("DELETE FROM priority_weights")
                self._conn.commit()
        except Exception as exc:  # noqa: BLE001
            log.warning("feedback clear failed (%s)", exc)


_STORE: Optional[FeedbackStore] = None


def get_feedback_store() -> FeedbackStore:
    global _STORE
    if _STORE is None:
        _STORE = FeedbackStore()
    return _STORE


# ---------------------------------------------------------------------------
def submit_feedback(**kw: Any) -> FeedbackResult:
    """Convenience: submit feedback to the singleton store."""
    return get_feedback_store().submit(**kw)


def priority_weight(asset_id: str, scenario_id: str | None = None) -> float:
    """Convenience: effective priority multiplier for (asset, scenario)."""
    return get_feedback_store().priority_weight(asset_id, scenario_id)
