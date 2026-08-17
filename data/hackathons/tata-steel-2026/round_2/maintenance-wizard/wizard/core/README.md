# wizard.core — Shared Contracts

This sub-package is the single source of truth for all typed entities and configuration.
Every other sub-package imports from here. Never import across sub-packages sideways.

## Files

| File | Purpose |
|---|---|
| `schemas.py` | Pydantic v2 + SQLModel entity models, cross-agent output models, discriminated union, `ingest_entity()` |
| `config.py` | Pydantic-settings `WizardSettings` — all env vars in one place |
| `db.py` | SQLite engine init (WAL mode), `init_db()`, `get_session()`, `reset_db()` |
| `smoke_core.py` | Self-test — run with `python wizard/core/smoke_core.py` |

## Integration Contract

All other modules import exactly these names:

```python
# Entity table models (7)
from wizard.core.schemas import (
    EntityBase, AssetProfile, SensorSummary, FaultLog,
    MaintenanceRecord, KnowledgeDocument, SparePart, AnomalyAlert,
)

# Non-table models
from wizard.core.schemas import DocumentRecord, QuarantineRecord

# Union + ingest
from wizard.core.schemas import WizardEntity, ingest_entity

# Cross-agent outputs (9)
from wizard.core.schemas import (
    AlertSeverity, AlertEvent, DiagnosisReport,
    CauseChainStep, RCAResult, RULResult, RiskScore,
    ActionStep, MaintenanceRecommendation,
)

# LangGraph state
from wizard.core.schemas import MaintenanceState

# Config + DB
from wizard.core.config import settings
from wizard.core.db import get_session, init_db
```
