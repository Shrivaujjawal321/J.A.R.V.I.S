# Component 14: Unified Data Schema Across All Input Types
**Tata Steel AI Hackathon 2026 — Round 2 Research Brief**
*Research date: 2026-06-06 | Constraint: CPU-only, solo build, ~9 days, pip-install-first*

---

## 1. Recommended Approach — The Single Winner

**Pydantic v2 discriminated-union entity model with SQLite (via SQLModel 0.0.21) as the persistence layer and a shared `DocumentRecord` bridge for RAG ingestion.**

The architecture is:

```
All input types  ─►  Typed Pydantic v2 model (validated at ingest)
                           │
                    SQLite via SQLModel
                    (single file: wizard.db)
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
        RAG layer      ML pipeline   Agent tools
   (DocumentRecord    (SensorSummary  (SparePart,
    → ChromaDB)        → LightGBM)    AssetProfile)
```

The root discriminated union is `WizardEntity`, a `Literal`-tagged union of eight typed sub-models. Every entity that enters the system is parsed through `WizardEntity` first. If validation fails, the entity is quarantined to `data/quarantine/` with error details — it never silently enters the database. Every entity shares four common fields (`entity_id`, `entity_type`, `asset_id`, `ingested_at`) that form the join key across all downstream consumers.

This is the winning approach because it gives the system one canonical in-memory representation, one storage layer, and one schema-checked ingest path — without the overhead of a proper data platform (no Kafka, no Iceberg, no dbt, all of which are operationally incompatible with a judge's machine / pip-install constraint).

---

## 2. WHY — Evidence-Based Reasoning

### 2a. Pydantic v2 discriminated unions: the right abstraction for heterogeneous industrial data

Pydantic v2 (2.7.x) discriminated unions dispatch validation based on a `Literal`-typed `entity_type` field. This eliminates the need for separate ingestion code per entity type: one `model_validate(raw_dict)` call routes the payload to the correct sub-model and validates all fields. Performance is significant: Pydantic v2's Rust-backed core is up to 4x faster than v1, and discriminated union validation is O(1) lookup (no sequential try-each-submodel fallback).

For the Maintenance Wizard, this matters because eight radically different input types arrive in a single pipeline: sensor summaries, fault logs, maintenance records, manuals, SOPs, spare parts, anomaly alerts, and incident reports. Without a discriminated union, the ingestion layer needs eight separate code paths with manual type checks — a 2022-tier design that creates schema drift as soon as any single path diverges.

The `pydantic-ai` framework (0.0.x, GitHub pydantic/pydantic-ai) itself models agent tool outputs and memory objects as Pydantic BaseModels. The Maintenance Wizard agents already produce `AgentResult` (see BUILD_PROCESS_PLAYBOOK Step 0.3) as a Pydantic model. Extending the same pattern to all eight entity types means zero cognitive overhead: one validation idiom for the entire codebase.

### 2b. SQLModel 0.0.21 + SQLite: zero-infra persistence that runs on a judge's machine

SQLModel (by FastAPI's creator, Tiangolo) unifies SQLAlchemy table definitions and Pydantic models into a single class. One model definition serves as: the database table schema, the API request/response model, the in-memory Python object, and the JSON serialization target. This eliminates the 2022-tier pattern of maintaining parallel `ORMModel` and `APISchema` classes that drift from each other.

SQLite as the persistence backend is non-negotiable for the constraint set:
- Single file (`wizard.db`), no server process, zero extra dependencies
- Handles the expected volume easily: ~10K sensor rows, ~500 document records, ~1K maintenance events — well within SQLite's proven capacity of millions of rows
- `render_as_batch=True` in Alembic handles SQLite's limited ALTER TABLE support for schema migrations
- The BUILD_PROCESS_PLAYBOOK already uses `data/sessions.db` for conversation state — unifying under one SQLite file prevents multiple DB file management

### 2c. ISA-95 + ISO 14224 alignment for the entity hierarchy

The entity model is grounded in two industrial standards:

**ISA-95** (Enterprise-Control System Integration) defines the equipment hierarchy: Enterprise → Site → Area → Work Center → Work Unit → Equipment. The `AssetProfile` entity maps to this hierarchy with fields `plant_area`, `work_center`, `equipment_id`, enabling any entity to be traced up the hierarchy to a business unit for prioritization scoring.

**ISO 14224** (Reliability and Maintenance Data for Equipment) defines the taxonomy for failure modes, maintenance records, and reliability data collection. The `MaintenanceRecord` and `FaultLog` entities use ISO 14224's nine-level classification structure (industry → business category → installation → plant section → section → equipment unit → sub-unit → maintainable item → part). This grounds the synthetic data generation (Component 12) and ensures agents can correctly interpret failure modes.

These standards are established in industrial AI platforms (Hitachi Vantara Lumada, Databricks Industrial AI Reference Architecture). Aligning the schema to them signals domain depth to a Tata Steel judge who understands these standards internally.

### 2d. `DocumentRecord` bridge: the schema that stitches RAG and ML

The key architectural challenge is that RAG needs unstructured text chunks with metadata, while ML needs structured numerical arrays. A naive design creates two separate schemas with no shared identity — the RAG retriever cannot cross-reference a retrieved SOP chunk with the equipment's current sensor readings.

The `DocumentRecord` entity solves this: every entity that contains narrative text (manual sections, SOPs, maintenance reports, incident summaries, failure analysis reports) is ALSO serialized as a `DocumentRecord` with `source_entity_id` linking back to the typed entity. The `DocumentRecord` is what gets chunked and embedded into ChromaDB. The `source_entity_id` is stored as ChromaDB metadata, enabling the RAG retriever to fetch the full typed entity from SQLite when attribution is needed.

This is the pattern used by LlamaIndex's node architecture (2025): "A Node is the atomic unit of data in LlamaIndex and represents a chunk of a source Document, along with metadata that relates them to the document they are in." The `DocumentRecord` is the Maintenance Wizard's equivalent — an embedding-ready unit that preserves its lineage to the original typed entity.

---

## 3. Exact Stack

| Library/Tool | Version | Role |
|---|---|---|
| `pydantic` | 2.7.x | Core entity schema definition; field validation; discriminated unions; JSON schema emission |
| `sqlmodel` | 0.0.21 | Dual SQLAlchemy/Pydantic model — one class = DB table + API model + in-memory object |
| `sqlalchemy` | 2.0.x | Backend ORM; async support; used via SQLModel |
| `alembic` | 1.13.x | Schema migrations; `render_as_batch=True` for SQLite; version-controlled schema evolution |
| `sqlite3` | stdlib | Zero-install persistence; handles the full entity corpus without a server |
| `chromadb` | 0.5.x | In-process vector store for `DocumentRecord` chunks; metadata carries `source_entity_id` |
| `instructor` | 1.8.1 | LLM → typed entity extraction; enforces Pydantic schemas on LLM output at ingest |
| `python-ulid` | 3.0.x | ULID as `entity_id` (lexicographically sortable, URL-safe, collision-free — better than UUID4 for time-series entities) |
| `pydantic-settings` | 2.x | Config validation via env vars; integrates with `wizard/core/config.py` |
| Python | 3.12 | Runtime; all above install via `pip install` |

No Docker. No cloud warehouse. No message broker. Full install: `pip install pydantic sqlmodel alembic chromadb instructor python-ulid pydantic-settings`.

---

## 4. Complete Entity Model

### 4a. Shared base + discriminated root

```python
from __future__ import annotations
from datetime import datetime
from typing import Literal, Annotated, Union
from pydantic import BaseModel, Field
from sqlmodel import SQLModel, Column, JSON
import ulid

class EntityBase(SQLModel):
    entity_id: str = Field(default_factory=lambda: str(ulid.new()))
    asset_id: str                          # FK → AssetProfile
    plant_area: str                        # ISA-95 Area level
    ingested_at: datetime = Field(default_factory=datetime.utcnow)
    source_system: str = "manual"          # "scada", "erp", "manual", "generated"
    schema_version: str = "1.0"
```

### 4b. Eight entity sub-models

**AssetProfile** — the master entity every other entity references:
```python
class AssetProfile(EntityBase, table=True):
    entity_type: Literal["asset"] = "asset"
    equipment_name: str
    equipment_class: str           # ISO 14224: pump | fan | conveyor | bearing | hydraulic_unit
    manufacturer: str
    installation_date: datetime
    design_rpm: float | None
    design_pressure_bar: float | None
    criticality_tier: Literal["critical", "high", "medium", "low"]
    subsystem: str                 # ISO 14224 sub-unit level
    iso14224_taxonomy: str         # e.g. "rotating.centrifugal_pump.impeller"
```

**SensorSummary** — aggregated sensor window (15-min or 1-hour):
```python
class SensorSummary(EntityBase, table=True):
    entity_type: Literal["sensor_summary"] = "sensor_summary"
    window_start: datetime
    window_end: datetime
    sensor_readings: dict = Field(sa_column=Column(JSON))
    # keys: temperature_c, pressure_bar, vibration_mm_s, rpm, torque_nm, current_a
    anomaly_score: float | None    # from Component 9; null until computed
    rul_days_p50: float | None     # from Component 8; null until computed
    operating_condition: str | None  # FD001-style: "normal" | "degraded" | "severe"
```

**FaultLog** — single fault/error event:
```python
class FaultLog(EntityBase, table=True):
    entity_type: Literal["fault_log"] = "fault_log"
    fault_code: str                # e.g. "BRG-WEAR-001"
    fault_description: str
    severity: Literal["low", "medium", "high", "critical"]
    detected_at: datetime
    source: Literal["sensor", "operator", "scada", "erp"]
    confirmed: bool = False
    related_sensor_summary_id: str | None  # FK → SensorSummary
```

**MaintenanceRecord** — completed or planned maintenance event:
```python
class MaintenanceRecord(EntityBase, table=True):
    entity_type: Literal["maintenance_record"] = "maintenance_record"
    work_order_id: str
    maintenance_type: Literal["corrective", "preventive", "predictive", "emergency"]
    description: str
    performed_at: datetime | None
    planned_at: datetime | None
    technician_id: str
    duration_hours: float | None
    parts_used: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    outcome: Literal["resolved", "partial", "escalated", "pending"] = "pending"
    rca_summary: str | None        # root cause, free text — also indexed to DocumentRecord
```

**KnowledgeDocument** — manual section, SOP, or failure analysis report:
```python
class KnowledgeDocument(EntityBase, table=True):
    entity_type: Literal["knowledge_doc"] = "knowledge_doc"
    doc_type: Literal["manual", "sop", "failure_analysis", "incident_summary"]
    title: str
    section: str                   # e.g. "4.2 — Descaler Valve Replacement"
    content_markdown: str          # full text; chunked into DocumentRecord at ingest
    revision: str                  # e.g. "2024-Q3"
    applicable_equipment_classes: list[str] = Field(sa_column=Column(JSON))
```

**SparePart** — spare parts catalog entry with procurement data:
```python
class SparePart(EntityBase, table=True):
    entity_type: Literal["spare_part"] = "spare_part"
    part_number: str               # e.g. "SKF-6310-2RS1"
    part_name: str
    compatible_equipment: list[str] = Field(sa_column=Column(JSON))
    stock_qty: int
    min_stock_qty: int             # reorder point
    unit_cost_inr: float
    lead_time_days: int            # procurement lead time — critical for prioritization
    supplier: str
    criticality_override: Literal["critical", "standard"] = "standard"
    last_updated: datetime = Field(default_factory=datetime.utcnow)
```

**AnomalyAlert** — proactive alert generated by Component 9/10:
```python
class AnomalyAlert(EntityBase, table=True):
    entity_type: Literal["anomaly_alert"] = "anomaly_alert"
    triggered_at: datetime = Field(default_factory=datetime.utcnow)
    alert_type: Literal["sensor_anomaly", "rul_critical", "pattern_match", "threshold_breach"]
    risk_level: Literal["low", "medium", "high", "critical"]
    description: str
    triggering_sensor_summary_id: str | None
    estimated_rul_days: float | None
    recommended_action: str | None
    acknowledged: bool = False
    acknowledged_by: str | None
```

**DocumentRecord** — the RAG bridge entity (not a table, lives in ChromaDB metadata):
```python
class DocumentRecord(BaseModel):
    """Not persisted to SQLite — metadata for ChromaDB chunks."""
    chunk_id: str = Field(default_factory=lambda: str(ulid.new()))
    source_entity_id: str          # FK → any EntityBase
    source_entity_type: str        # for reverse lookup
    asset_id: str
    text: str                      # the chunk text
    doc_type: str                  # "manual" | "sop" | "maintenance_record" | ...
    section: str
    page_or_step: str | None
    embedding_model: str = "BAAI/bge-base-en-v1.5"
```

### 4c. Discriminated root union

```python
WizardEntity = Annotated[
    Union[
        AssetProfile,
        SensorSummary,
        FaultLog,
        MaintenanceRecord,
        KnowledgeDocument,
        SparePart,
        AnomalyAlert,
    ],
    Field(discriminator="entity_type")
]

def ingest_entity(raw: dict) -> WizardEntity:
    """Single entry point. Raises ValidationError → quarantine."""
    return TypeAdapter(WizardEntity).validate_python(raw)
```

---

## 5. Alternatives Considered

### Alternative A: Flat JSON files per entity type (JSONL)
**Tradeoff that eliminates it:** Fast to start, zero setup. But no cross-entity queries: the prioritization agent needs to join SparePart.lead_time_days × FaultLog.severity × AssetProfile.criticality_tier in one SQL query. With JSONL files, this requires loading all three files into Pandas every time — O(n) load latency on every agent call, no indexes, no foreign key integrity. At 10K+ entity rows, this becomes a latency budget violation. SQLite with indexes answers the same join in <5 ms.

### Alternative B: PostgreSQL + SQLAlchemy
**Tradeoff that eliminates it:** Better for production multi-user scale. But it requires a running server process, `psql` installation, and `pg_hba.conf` configuration — none of which can be assumed on a judge's machine. The entire solo/judge-machine constraint collapses to: if the demo requires a Postgres server, it risks a cold-start failure. SQLite is embedded in Python's stdlib and has zero install friction.

### Alternative C: LlamaIndex Document/Node objects as the canonical entity model
**Tradeoff that eliminates it:** LlamaIndex nodes are excellent for RAG pipelines but are RAG-first: they model text chunks with metadata, not typed business entities. Storing SparePart.lead_time_days or SensorSummary.rul_days_p50 as LlamaIndex node metadata fields forces the ML pipeline to parse untyped metadata dicts. The discriminated union approach keeps typed entities first-class and uses LlamaIndex (or ChromaDB directly) only for the text-chunk layer, via the `DocumentRecord` bridge.

### Alternative D: Apache Iceberg + Parquet (lakehouse style)
**Tradeoff that eliminates it:** The 2026-tier data engineering standard for production at scale. But it requires `pyiceberg` + a catalog (REST or Glue), HDFS or S3 for object storage, and Spark or DuckDB as the query engine. For a solo 9-day build on a judge's machine, this is a dependency chain that will not survive a cold `pip install`. Iceberg's value is schema evolution at petabyte scale — overkill for a 10K-row demo dataset.

---

## 6. Anti-Patterns — What Screams "Amateur / 2022-Tier"

- **Storing all entity types in a single `data` column as raw JSON strings.** No schema validation, no column indexes, no cross-entity joins. The prioritization query becomes a full table scan with Python-side JSON parsing. This is a document-store anti-pattern masquerading as a database.

- **Different schemas for the same entity across components.** If the ML pipeline expects `sensor_readings["temperature_c"]` but the RAG pipeline stores it as `readings["temp"]`, the system has an implicit contract violation that only surfaces at runtime — exactly what a discriminated union at the ingest layer prevents.

- **No `asset_id` on every entity.** Every entity must be traceable to a physical asset. Without it, a judge's query "what is the maintenance history for BF-2 Fan?" requires scanning all maintenance records for keyword matches instead of a single indexed lookup on `asset_id = "BF-2-FAN"`.

- **Using Pandas DataFrames as the in-memory entity model.** DataFrames are excellent for batch ML feature computation but terrible as a system-wide entity model: no type safety, no schema validation, no foreign key semantics, and `df.to_dict()` loses all Pydantic validators. An agent that mutates a DataFrame row to update `FaultLog.confirmed = True` has no validation checkpoint — the data can silently corrupt.

- **Separate schema files for SQL tables and Pydantic models.** The 2022 pattern: `models.py` (Pydantic for APIs) + `orm_models.py` (SQLAlchemy for DB) that must be kept in sync manually. SQLModel eliminates this entirely. Any team that maintains both is incurring unnecessary maintenance burden.

- **No quarantine path for invalid entities.** Industrial data is dirty. Real sensor feeds produce nulls, out-of-range values, and malformed JSON. A system that silently ignores or crashes on invalid input will fail in the judge's demo. Every invalid entity must be caught at `ingest_entity()`, written to `data/quarantine/invalid_entities.jsonl` with the validation error, and surface as a count in the dashboard.

- **Ignoring `lead_time_days` in the spare parts schema.** This field is explicitly called out in the problem statement as a prioritization input. A schema that records only stock quantity but not procurement lead time misses the entire point of the spare-parts sub-system: a part with 0 stock and 45-day lead time should trigger emergency procurement immediately; a part with 0 stock and 2-day lead time is less urgent. Omitting this field signals the builder did not read the requirements.

---

## 7. Integration Notes

### Inputs Consumed
- Raw JSONL/CSV from the sensor dataset pipeline (AI4I 2020: uid, product_type, air_temp, process_temp, rpm, torque, tool_wear → `SensorSummary`)
- Synthetic generation output from Component 12 (JSON per document type → `KnowledgeDocument`, `MaintenanceRecord`, `SparePart`, `FaultLog`, `AnomalyAlert`)
- Engineer queries (free text, no schema — bypasses entity model, goes directly to RAG/agent)
- Feedback corrections from the UI (entity_id + correction field + new value → SQLModel `.update()` on the entity row)

### Outputs Produced
- **SQLite `wizard.db`** — single file, all seven entity tables, indexed on `asset_id`, `entity_type`, `ingested_at`
- **`DocumentRecord` objects** — streamed to ChromaDB at ingest time for any entity with `content_markdown` or `rca_summary` or `fault_description` fields
- **Feature arrays** — `SensorSummary` rows SELECT-ed and numpy-stacked by the ML pipeline for LightGBM/WeibullAFT inference (Component 8)
- **Prioritization join result** — SQL query joining `FaultLog`, `SparePart`, `AssetProfile` on `asset_id` → scored priority queue for the agent planner

### Components This Talks To

| Component | How it reads from the schema |
|---|---|
| Component 4 (RAG) | Reads `DocumentRecord` from ChromaDB; fetches full `KnowledgeDocument` / `MaintenanceRecord` from SQLite by `source_entity_id` for citation |
| Component 5 (GraphRAG) | Reads `AssetProfile` for node definitions; `FaultLog` for edge weights (fault frequency per asset pair) |
| Component 8 (RUL) | Reads `SensorSummary` rows for a given `asset_id`, stacks into numpy array for WeibullAFT inference; writes `rul_days_p50` back to `SensorSummary` |
| Component 9 (Anomaly) | Reads `SensorSummary.sensor_readings` JSON column; writes `anomaly_score` back |
| Component 10 (Failure Prediction) | Reads `SensorSummary` + `MaintenanceRecord` join on `asset_id` |
| Component 11 (RCA) | Reads `FaultLog` + `MaintenanceRecord` + `KnowledgeDocument` |
| Component 1 (Orchestrator) | All agent tools take `asset_id: str` as input and query SQLite; all tool outputs are `AgentResult` wrapping the typed entity |
| Alerting Engine | Reads `AnomalyAlert` table, filters `acknowledged=False` and `risk_level in ("high","critical")`; writes `acknowledged=True` on engineer confirmation |
| Spare Parts Prioritization | SQL: SELECT s.part_number, s.lead_time_days, s.stock_qty, a.criticality_tier FROM spare_part s JOIN asset_profile a ON s.asset_id = a.asset_id JOIN fault_log f ON f.asset_id = a.asset_id WHERE f.confirmed=True ORDER BY a.criticality_tier, s.lead_time_days DESC |
| Feedback Loop | Engineer correction payload: `{"entity_id": "...", "field": "rul_days_p50", "corrected_value": 14.0}` → validated against entity schema before write |

### Schema Evolution Strategy

Alembic with `render_as_batch=True` handles SQLite migrations. Every schema change gets a numbered migration file (`alembic/versions/`). `schema_version` field on every entity enables detecting old-format records at query time. For the 9-day build window, schema v1.0 is the only version — but the migration scaffold must be present so the judge can see engineering discipline.

---

## 8. Open Risks / Unknowns

- **SQLite concurrent write contention [LOW RISK]:** SQLite uses file-level locks. For a single-user demo, this is irrelevant. If the alerting engine and the API server write simultaneously (asyncio concurrent tasks), WAL (Write-Ahead Logging) mode (`PRAGMA journal_mode=WAL`) eliminates this — add to `wizard/core/db.py` engine init. [verified pattern for FastAPI + SQLite]

- **JSON column indexing [KNOWN LIMITATION]:** `SensorSummary.sensor_readings` is a JSON column and cannot be indexed in SQLite. The ML pipeline must SELECT all rows for an asset and filter in Python. At ~10K rows per asset, this is ~50 ms — within budget. If volume grows, extract key sensor fields to dedicated columns. [verified SQLite JSON limitation]

- **ChromaDB vs SQLite entity ID sync [MEDIUM RISK]:** If ChromaDB is reset (e.g., `make reset`), `DocumentRecord` chunks lose their embeddings but SQLite entities remain. The RAG layer will return no results until re-ingest. Mitigation: `make reset` script must call both `wizard.db` cleanup AND `chromadb.reset()`. The `DocumentRecord.source_entity_id` foreign key is the recovery anchor — re-ingest by querying all entities with content fields from SQLite. [unverified: needs smoke test in Phase 0]

- **Pydantic discriminated union with SQLModel table inheritance [MEDIUM RISK]:** SQLModel's table-level single-table inheritance and Pydantic discriminated unions are not the same concept. The seven entity types should be seven SEPARATE SQLModel table classes (not a single polymorphic table), with the discriminated union only at the Python validation layer. Using SQLModel's `discriminator` with a single table would require `sa_column=Column(String)` on `entity_type` and a single `wizard_entity` table — simpler but harder to query efficiently. Seven separate tables is the correct design. [verified in SQLModel docs; discriminated union validation layer is pure Pydantic, not SQLModel concern]

- **AI4I 2020 dataset column mapping [LOW RISK]:** The dataset uses `Air temperature [K]` (Kelvin), not Celsius. The ingest script must convert to `temperature_c = (kelvin - 273.15)` before storing in `SensorSummary.sensor_readings`. Failure to do this will cause the anomaly detector and RUL model to see values like 298.1 K instead of 24.95°C — plausible-looking but wrong units that break threshold comparisons. [verified from UCI dataset schema]

- **ULID vs UUID for entity_id [MINOR]:** `python-ulid` 3.0.x generates Crockford Base32 ULIDs. ChromaDB expects string IDs and accepts ULIDs fine. SQLite stores them as TEXT. The benefit over UUID4 is lexicographic sortability by creation time — useful for querying "last N entities" without an ORDER BY on `ingested_at`. [verified: ChromaDB docs state IDs must be strings; ULID is valid]
