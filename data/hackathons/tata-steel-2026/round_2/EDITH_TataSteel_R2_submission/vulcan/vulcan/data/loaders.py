"""Typed loaders over the steel-maintenance-flagship dataset.

Lightweight dataclasses + cached accessors. No heavy frameworks: stdlib `json`/`csv`
for the small spine + catalogs; `polars` is used lazily ONLY for the large condition
-monitoring CSVs (and even then loaded on demand, never at import).

Everything here is read-only. Loaders cache parsed results so repeated calls are free.
"""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterator

from ..config import Settings, get_settings


# ===========================================================================
# Spine dataclasses (assets / scenarios / spares)
# ===========================================================================
@dataclass(frozen=True)
class Sensor:
    tag: str
    quantity: str
    unit: str
    normal_range: tuple[float | None, float | None]
    warning_threshold: float | None
    alarm_threshold: float | None
    sampling_rate: str | None
    standard: str | None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Sensor":
        nr = d.get("normal_range") or [None, None]
        return cls(
            tag=d.get("tag", ""),
            quantity=d.get("quantity", ""),
            unit=d.get("unit", ""),
            normal_range=(nr[0] if len(nr) > 0 else None, nr[1] if len(nr) > 1 else None),
            warning_threshold=d.get("warning_threshold"),
            alarm_threshold=d.get("alarm_threshold"),
            sampling_rate=d.get("sampling_rate"),
            standard=d.get("standard"),
            raw=d,
        )


@dataclass(frozen=True)
class Asset:
    asset_id: str
    equipment_class: str
    description: str
    process_stage: str
    location: dict[str, Any]
    manufacturer: str | None
    model: str | None
    rated_speed_rpm: float | None
    criticality: int | None        # 1 = most critical
    installation_date: str | None
    last_overhaul_date: str | None
    sensors: list[Sensor]
    failure_modes: list[str]
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Asset":
        return cls(
            asset_id=d.get("asset_id", ""),
            equipment_class=d.get("equipment_class", ""),
            description=d.get("description", ""),
            process_stage=d.get("process_stage", ""),
            location=d.get("location", {}) or {},
            manufacturer=d.get("manufacturer"),
            model=d.get("model"),
            rated_speed_rpm=d.get("rated_speed_rpm"),
            criticality=d.get("criticality"),
            installation_date=d.get("installation_date"),
            last_overhaul_date=d.get("last_overhaul_date"),
            sensors=[Sensor.from_dict(s) for s in d.get("sensors", []) or []],
            failure_modes=list(d.get("failure_modes", []) or []),
            raw=d,
        )

    def sensor(self, tag: str) -> Sensor | None:
        for s in self.sensors:
            if s.tag == tag:
                return s
        return None


@dataclass(frozen=True)
class SpareRef:
    part_id: str
    name: str


@dataclass(frozen=True)
class Scenario:
    scenario_id: str
    asset_id: str
    label: str                      # NORMAL | WARNING | FAILURE | ...
    failure_mode: str
    degradation_timeline: dict[str, str] | None
    sensor_signature: dict[str, Any]
    fault_codes: list[str]
    root_cause: str
    correct_resolution: list[str]
    spares_required: list[SpareRef]
    downtime_hours: dict[str, float]
    cost_impact: dict[str, Any]
    safety_class: str | None        # P1 (most severe) .. P4
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Scenario":
        return cls(
            scenario_id=d.get("scenario_id", ""),
            asset_id=d.get("asset_id", ""),
            label=d.get("label", ""),
            failure_mode=d.get("failure_mode", ""),
            degradation_timeline=d.get("degradation_timeline"),
            sensor_signature=d.get("sensor_signature", {}) or {},
            fault_codes=list(d.get("fault_codes", []) or []),
            root_cause=d.get("root_cause", ""),
            correct_resolution=list(d.get("correct_resolution", []) or []),
            spares_required=[
                SpareRef(part_id=s.get("part_id", ""), name=s.get("name", ""))
                for s in d.get("spares_required", []) or []
            ],
            downtime_hours=d.get("downtime_hours", {}) or {},
            cost_impact=d.get("cost_impact", {}) or {},
            safety_class=d.get("safety_class"),
            raw=d,
        )

    @property
    def is_failure(self) -> bool:
        return self.label.upper() not in ("NORMAL", "")


@dataclass(frozen=True)
class SparePart:
    """From the spine's spare_parts_master (canonical) — see also the richer
    spare_parts_catalog.csv (procurement view with supplier, in_stock)."""
    part_id: str
    name: str
    fits_equipment_class: list[str]
    stock_qty: int | None
    lead_time_weeks: float | None
    unit_cost: dict[str, Any]
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "SparePart":
        return cls(
            part_id=d.get("part_id", ""),
            name=d.get("name", ""),
            fits_equipment_class=list(d.get("fits_equipment_class", []) or []),
            stock_qty=d.get("stock_qty"),
            lead_time_weeks=d.get("lead_time_weeks"),
            unit_cost=d.get("unit_cost", {}) or {},
            raw=d,
        )


@dataclass
class Spine:
    """The whole ground-truth spine, parsed + indexed."""
    meta: dict[str, Any]
    assets: list[Asset]
    scenarios: list[Scenario]
    spares: list[SparePart]
    standards_backbone: list[str]

    # indexes (built in __post_init__)
    _asset_by_id: dict[str, Asset] = field(default_factory=dict, repr=False)
    _scenario_by_id: dict[str, Scenario] = field(default_factory=dict, repr=False)
    _spare_by_id: dict[str, SparePart] = field(default_factory=dict, repr=False)
    _sensor_to_asset: dict[str, str] = field(default_factory=dict, repr=False)

    def __post_init__(self) -> None:
        self._asset_by_id = {a.asset_id: a for a in self.assets}
        self._scenario_by_id = {s.scenario_id: s for s in self.scenarios}
        self._spare_by_id = {p.part_id: p for p in self.spares}
        for a in self.assets:
            for s in a.sensors:
                self._sensor_to_asset[s.tag] = a.asset_id

    # accessors -----------------------------------------------------------
    def asset(self, asset_id: str) -> Asset | None:
        return self._asset_by_id.get(asset_id)

    def scenario(self, scenario_id: str) -> Scenario | None:
        return self._scenario_by_id.get(scenario_id)

    def spare(self, part_id: str) -> SparePart | None:
        return self._spare_by_id.get(part_id)

    def asset_for_sensor(self, sensor_tag: str) -> Asset | None:
        aid = self._sensor_to_asset.get(sensor_tag)
        return self._asset_by_id.get(aid) if aid else None

    def scenarios_for_asset(self, asset_id: str) -> list[Scenario]:
        return [s for s in self.scenarios if s.asset_id == asset_id]

    def spares_for_equipment_class(self, eq_class: str) -> list[SparePart]:
        return [p for p in self.spares if eq_class in p.fits_equipment_class]


# ===========================================================================
# CSV row dataclasses
# ===========================================================================
@dataclass(frozen=True)
class MaintenanceRecord:
    work_order_id: str
    date: str
    asset_id: str
    type: str
    task_description: str
    sop_ref: str
    parts_used: str
    labor_hours: str
    downtime_hours: str
    cost: str
    technician: str
    outcome: str


@dataclass(frozen=True)
class CatalogSpare:
    """Procurement view from spare_parts_catalog.csv (118 rows)."""
    part_id: str
    name: str
    fits_equipment_class: str
    fits_asset_ids: str
    on_hand_qty: str
    min_qty: str
    lead_time_weeks: str
    unit_cost: str
    supplier: str
    criticality: str
    in_stock: str

    @property
    def on_hand(self) -> int:
        try:
            return int(float(self.on_hand_qty))
        except (ValueError, TypeError):
            return 0

    @property
    def lead_weeks(self) -> float:
        try:
            return float(self.lead_time_weeks)
        except (ValueError, TypeError):
            return 0.0

    @property
    def available(self) -> bool:
        return str(self.in_stock).strip().lower() in ("true", "1", "yes") or self.on_hand > 0


@dataclass(frozen=True)
class Incident:
    incident_id: str
    asset_id: str
    start_ts: str
    end_ts: str
    downtime_hours: str
    failure_mode: str
    severity: str
    root_cause_short: str
    resolution_short: str
    cost_estimate: str
    scenario_id: str
    maintenance_type: str


@dataclass(frozen=True)
class FaultMessage:
    timestamp: str
    asset_id: str
    source_system: str
    fault_code: str
    severity: str
    message: str


@dataclass(frozen=True)
class DelayLog:
    timestamp: str
    asset_id: str
    line: str
    delay_minutes: str
    delay_reason_code: str
    description: str


@dataclass(frozen=True)
class AnomalyAlert:
    timestamp: str
    asset_id: str
    sensor: str
    value: str
    threshold: str
    severity: str
    fault_label: str
    scenario_id: str


# ===========================================================================
# Generic CSV / JSONL helpers
# ===========================================================================
def _read_csv_dicts(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        return []
    with path.open("r", encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    out: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                try:
                    out.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return out


def _filter_cols(row: dict[str, str], fields: tuple[str, ...]) -> dict[str, str]:
    return {f: row.get(f, "") for f in fields}


# ===========================================================================
# Knowledge document
# ===========================================================================
@dataclass(frozen=True)
class KnowledgeDoc:
    doc_id: str          # filename stem, e.g. MAN-001_rolling_mill_work_roll_bearing
    path: Path
    kind: str            # "equipment_manual" | "sop" | "rca_report" | "domain" | "additional"
    title: str
    text: str

    @property
    def source_ref(self) -> str:
        """A citation-friendly source reference (filename)."""
        return self.path.name


def _md_title(text: str, fallback: str) -> str:
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("#"):
            return line.lstrip("#").strip()
        if line:
            return line[:120]
    return fallback


# ===========================================================================
# THE LOADER FACADE — one object, cached, exposes everything.
# ===========================================================================
class DataStore:
    """Cached, typed access to the whole flagship dataset."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    # ---- spine ----
    @lru_cache(maxsize=1)
    def spine(self) -> Spine:  # type: ignore[misc]
        path = self.settings.spine_path
        raw = json.loads(path.read_text(encoding="utf-8"))
        meta = {
            k: raw.get(k)
            for k in (
                "dataset_name", "spine_version", "generated", "site",
                "disclaimer", "currency_note",
            )
        }
        return Spine(
            meta=meta,
            assets=[Asset.from_dict(a) for a in raw.get("asset_registry", [])],
            scenarios=[Scenario.from_dict(s) for s in raw.get("failure_scenario_catalog", [])],
            spares=[SparePart.from_dict(p) for p in raw.get("spare_parts_master", [])],
            standards_backbone=list(raw.get("standards_backbone", [])),
        )

    # ---- knowledge CSVs ----
    @lru_cache(maxsize=1)
    def maintenance_records(self) -> list[MaintenanceRecord]:  # type: ignore[misc]
        rows = _read_csv_dicts(self.settings.knowledge_dir / "historical_maintenance_records.csv")
        return [MaintenanceRecord(**_filter_cols(r, MaintenanceRecord.__dataclass_fields__.keys()))  # type: ignore[arg-type]
                for r in rows]

    @lru_cache(maxsize=1)
    def spare_catalog(self) -> list[CatalogSpare]:  # type: ignore[misc]
        rows = _read_csv_dicts(self.settings.knowledge_dir / "spare_parts_catalog.csv")
        return [CatalogSpare(**_filter_cols(r, CatalogSpare.__dataclass_fields__.keys()))  # type: ignore[arg-type]
                for r in rows]

    def spare_catalog_by_id(self) -> dict[str, CatalogSpare]:
        return {c.part_id: c for c in self.spare_catalog()}

    # ---- operational failure ----
    @lru_cache(maxsize=1)
    def incidents(self) -> list[Incident]:  # type: ignore[misc]
        rows = _read_csv_dicts(self.settings.operational_dir / "incident_records.csv")
        return [Incident(**_filter_cols(r, Incident.__dataclass_fields__.keys()))  # type: ignore[arg-type]
                for r in rows]

    @lru_cache(maxsize=1)
    def fault_messages(self) -> list[FaultMessage]:  # type: ignore[misc]
        rows = _read_csv_dicts(self.settings.operational_dir / "fault_error_messages.csv")
        return [FaultMessage(**_filter_cols(r, FaultMessage.__dataclass_fields__.keys()))  # type: ignore[arg-type]
                for r in rows]

    @lru_cache(maxsize=1)
    def delay_logs(self) -> list[DelayLog]:  # type: ignore[misc]
        rows = _read_csv_dicts(self.settings.operational_dir / "equipment_delay_logs.csv")
        return [DelayLog(**_filter_cols(r, DelayLog.__dataclass_fields__.keys()))  # type: ignore[arg-type]
                for r in rows]

    # ---- condition monitoring (small CSVs eager; big ones via polars lazy) ----
    @lru_cache(maxsize=1)
    def anomaly_alerts(self) -> list[AnomalyAlert]:  # type: ignore[misc]
        rows = _read_csv_dicts(self.settings.condition_dir / "anomaly_alerts.csv")
        return [AnomalyAlert(**_filter_cols(r, AnomalyAlert.__dataclass_fields__.keys()))  # type: ignore[arg-type]
                for r in rows]

    def sensor_summaries_lazy(self):
        """polars.LazyFrame over sensor_data_summaries.csv (wide ML feature table).

        Loaded lazily — call `.collect()` / `.filter(...)` to materialise a slice.
        Returns None if polars is unavailable.
        """
        try:
            import polars as pl
        except ImportError:
            return None
        p = self.settings.condition_dir / "sensor_data_summaries.csv"
        if not p.is_file():
            return None
        return pl.scan_csv(str(p), infer_schema_length=2000)

    def by_equipment_csv(self, name: str):
        """Return path to a dense per-class table in condition_monitoring/by_equipment/."""
        p = self.settings.condition_dir / "by_equipment" / name
        return p if p.is_file() else None

    def list_by_equipment(self) -> list[str]:
        d = self.settings.condition_dir / "by_equipment"
        if not d.is_dir():
            return []
        return sorted(f.name for f in d.glob("*.csv"))

    # ---- knowledge docs (markdown) ----
    def _load_docs(self, directory: Path, kind: str) -> list[KnowledgeDoc]:
        docs: list[KnowledgeDoc] = []
        if not directory.is_dir():
            return docs
        for p in sorted(directory.glob("*.md")):
            text = p.read_text(encoding="utf-8", errors="ignore")
            docs.append(
                KnowledgeDoc(
                    doc_id=p.stem, path=p, kind=kind,
                    title=_md_title(text, p.stem), text=text,
                )
            )
        return docs

    @lru_cache(maxsize=1)
    def equipment_manuals(self) -> list[KnowledgeDoc]:  # type: ignore[misc]
        return self._load_docs(self.settings.equipment_manuals_dir, "equipment_manual")

    @lru_cache(maxsize=1)
    def sops(self) -> list[KnowledgeDoc]:  # type: ignore[misc]
        return self._load_docs(self.settings.sops_dir, "sop")

    @lru_cache(maxsize=1)
    def rca_reports(self) -> list[KnowledgeDoc]:  # type: ignore[misc]
        return self._load_docs(
            self.settings.operational_dir / "failure_analysis_reports", "rca_report"
        )

    def all_knowledge_docs(self) -> list[KnowledgeDoc]:
        """Every markdown doc — the RAG corpus seed (manuals + SOPs + RCA reports)."""
        return [*self.equipment_manuals(), *self.sops(), *self.rca_reports()]

    # ---- user interaction (eval set) ----
    @lru_cache(maxsize=1)
    def nl_queries(self) -> list[dict[str, Any]]:  # type: ignore[misc]
        return _read_jsonl(self.settings.user_interaction_dir / "nl_queries.jsonl")

    @lru_cache(maxsize=1)
    def multiturn_conversations(self) -> list[dict[str, Any]]:  # type: ignore[misc]
        return _read_jsonl(self.settings.user_interaction_dir / "multiturn_conversations.jsonl")

    @lru_cache(maxsize=1)
    def troubleshooting_prompts(self) -> list[dict[str, Any]]:  # type: ignore[misc]
        return _read_jsonl(self.settings.user_interaction_dir / "troubleshooting_prompts.jsonl")

    # ---- summary ----
    def summary(self) -> dict[str, int]:
        sp = self.spine()
        return {
            "assets": len(sp.assets),
            "scenarios": len(sp.scenarios),
            "failure_scenarios": sum(1 for s in sp.scenarios if s.is_failure),
            "spares_master": len(sp.spares),
            "spare_catalog": len(self.spare_catalog()),
            "maintenance_records": len(self.maintenance_records()),
            "incidents": len(self.incidents()),
            "fault_messages": len(self.fault_messages()),
            "delay_logs": len(self.delay_logs()),
            "anomaly_alerts": len(self.anomaly_alerts()),
            "equipment_manuals": len(self.equipment_manuals()),
            "sops": len(self.sops()),
            "rca_reports": len(self.rca_reports()),
            "nl_queries": len(self.nl_queries()),
            "multiturn_conversations": len(self.multiturn_conversations()),
            "troubleshooting_prompts": len(self.troubleshooting_prompts()),
            "by_equipment_tables": len(self.list_by_equipment()),
        }


@lru_cache(maxsize=1)
def get_datastore() -> DataStore:
    return DataStore()


if __name__ == "__main__":
    ds = get_datastore()
    import json as _json
    print(_json.dumps(ds.summary(), indent=2))
    sp = ds.spine()
    a = sp.assets[0]
    print("\nfirst asset:", a.asset_id, "| crit", a.criticality, "| sensors", len(a.sensors))
    scn = next(s for s in sp.scenarios if s.is_failure)
    print("first failure scenario:", scn.scenario_id, scn.failure_mode, "safety", scn.safety_class)
