"""VULCAN agentic core (WAVE 3).

The supervisor/orchestrator + five domain specialists + reasoning trace + per-
session multi-turn memory + NL resolver. Keyless, CPU, fail-soft. The supervisor
owns the single LLM chokepoint call; everything else is deterministic dataset
grounding with an auditable reasoning trace and an NLI faithfulness gate.

Public API
----------
    from vulcan.agents import Supervisor
    sup = Supervisor()
    res = sup.handle_query("F3 work-roll bearing is vibrating, what's wrong?",
                           session_id="bay-3")
    print(res.trace.render())     # the transparent reasoning trace (FR4)
    print(res.answer)             # grounded, cited answer
    follow = sup.handle_query("and how long do I have?", session_id="bay-3")  # FR3
"""

from .supervisor import Supervisor, TurnResult
from .domain_agents import (
    DiagnosisAgent,
    Finding,
    PredictorAgent,
    PrioritizerAgent,
    RCAAgent,
    RecommenderAgent,
)
from .resolver import ResolvedQuery, resolve
from .trace import ReasoningTrace, TraceStep
from .memory import ConversationStore, Focus, get_store

__all__ = [
    "Supervisor", "TurnResult",
    "DiagnosisAgent", "RCAAgent", "PredictorAgent", "PrioritizerAgent",
    "RecommenderAgent", "Finding",
    "ResolvedQuery", "resolve",
    "ReasoningTrace", "TraceStep",
    "ConversationStore", "Focus", "get_store",
]
