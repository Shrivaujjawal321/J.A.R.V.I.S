"""
wizard.backend
==============
FastAPI backend service for the Maintenance Wizard.

Public surface — what other modules import from this package:

    from wizard.backend.wrps import (
        score_maintenance_priority,          # sync: (asset_id: str) -> RiskScore
        score_maintenance_priority_async,    # async: (asset_id: str) -> RiskScore
        score_maintenance_priority_for_session,  # (asset_id, session) -> (RiskScore, dict)
        apply_feedback_to_weights,           # (corrected, current) -> bool
        get_current_weights,                 # () -> dict[str, float]
        update_weights_from_ui,              # (new_weights) -> None
    )

    from wizard.backend.alerting import (
        AlertBroadcaster,
        broadcaster,                         # module-level singleton
        evaluate_alerts,                     # async, called by APScheduler
        trigger_demo_eaf04_alert,            # async, one-shot 90s wow moment
        setup_scheduler,                     # (scheduler: AsyncIOScheduler) -> None
    )

    from wizard.backend.graph_placeholder import (
        run_graph,       # async: (ChatRequest) -> tuple[MaintenanceRecommendation, list[dict]]
        stream_graph,    # async generator: (ChatRequest) -> AsyncGenerator[dict, None]
    )

    from wizard.backend.app import app   # FastAPI application instance
"""

def __getattr__(name: str):  # type: ignore[override]
    """Lazy imports to avoid circular imports and heavy dep loading at package scan."""
    if name in (
        "score_maintenance_priority", "score_maintenance_priority_async",
        "score_maintenance_priority_for_session", "apply_feedback_to_weights",
        "get_current_weights", "update_weights_from_ui",
    ):
        from wizard.backend import wrps as _wrps
        return getattr(_wrps, name)
    if name in (
        "AlertBroadcaster", "broadcaster", "evaluate_alerts",
        "setup_scheduler", "trigger_demo_eaf04_alert",
    ):
        from wizard.backend import alerting as _alerting
        return getattr(_alerting, name)
    if name in ("run_graph", "stream_graph"):
        from wizard.backend import graph_placeholder as _gph
        return getattr(_gph, name)
    if name in ("llm_circuit_breaker", "get_request_id"):
        from wizard.backend import middleware as _mw
        return getattr(_mw, name)
    if name == "app":
        from wizard.backend.app import app
        return app
    raise AttributeError(f"module 'wizard.backend' has no attribute {name!r}")

__all__ = [
    "score_maintenance_priority",
    "score_maintenance_priority_async",
    "score_maintenance_priority_for_session",
    "apply_feedback_to_weights",
    "get_current_weights",
    "update_weights_from_ui",
    "AlertBroadcaster",
    "broadcaster",
    "evaluate_alerts",
    "setup_scheduler",
    "trigger_demo_eaf04_alert",
    "run_graph",
    "stream_graph",
    "llm_circuit_breaker",
    "get_request_id",
]
