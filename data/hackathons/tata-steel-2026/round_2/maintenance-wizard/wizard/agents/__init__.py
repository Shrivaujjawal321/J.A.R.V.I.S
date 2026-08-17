"""
wizard.agents
=============
Agentic core for the Maintenance Wizard.

Registers wizard.core.schemas Pydantic models with LangGraph's JsonPlusSerializer
so checkpoint round-trips work without "Deserializing unregistered type" warnings.

The LANGGRAPH_CHECKPOINT_ALLOWED_MODULES env-var is a no-op at runtime — the only
effective fix is to pass a configured serde= instance directly to AsyncSqliteSaver.
That is done in graph._ensure_compiled_graph() using WIZARD_SERDE defined below.
"""
from __future__ import annotations

# Build a module-level serde instance with all wizard schemas allow-listed.
# graph.py imports WIZARD_SERDE and passes it to AsyncSqliteSaver(serde=...).
try:
    from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer as _JPS

    WIZARD_SERDE = _JPS(
        allowed_msgpack_modules=[
            ("wizard.core.schemas", "DiagnosisReport"),
            ("wizard.core.schemas", "RCAResult"),
            ("wizard.core.schemas", "RULResult"),
            ("wizard.core.schemas", "RiskScore"),
            ("wizard.core.schemas", "AlertSeverity"),
            ("wizard.core.schemas", "MaintenanceRecommendation"),
            ("wizard.core.schemas", "ActionStep"),
            ("wizard.core.schemas", "CauseChainStep"),
        ]
    )
except Exception:
    WIZARD_SERDE = None  # type: ignore[assignment]
