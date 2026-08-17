"""
synth_schema.py — JSON Schema cleaning + tool definition builder.

WHY THIS FILE EXISTS:
  Pydantic v2 model_json_schema() emits valid JSON Schema but Claude's strict
  tool-use mode rejects several constraints it generates:
    - maxLength / minLength on strings  (Signal.summary, raw_evidence)
    - minimum / maximum on floats       (Signal.confidence ge/le constraints)
    - maxItems / minItems > 1 on arrays
  This module provides _clean_schema_for_claude() to strip those, enforce
  additionalProperties:false on every object node, and handle the dict|None
  (price_target_range) free-form case.

CACHE NOTE:
  build_investment_brief_tool() adds cache_control on the tool definition.
  The tool cache is INDEPENDENT from the message/system cache — changes to
  tool_choice do not invalidate it. Only changes to input_schema, description,
  or name invalidate the tool cache. Lock those in constants; never regenerate
  dynamically per request.

Reference: research/17_claude_toolUse_synthesizer.md §2.
"""

from __future__ import annotations

import copy
from typing import Any

from .schemas import InvestmentBrief

# ────────────────────────── Schema Cleaner ──────────────────────────────────

# Constraint keywords that Claude strict mode rejects.
# minItems is allowed at 0 or 1 only; we strip minItems > 1 cases by always
# stripping it (our arrays don't use minItems semantically in the schema).
_STRIP_KEYS: frozenset[str] = frozenset({
    "maxLength",
    "minLength",
    "minimum",
    "maximum",
    "exclusiveMinimum",
    "exclusiveMaximum",
    "multipleOf",
    "maxItems",
    "minItems",  # strip entirely — strict mode is brittle with >1 min
})


def _clean_node(node: Any) -> None:
    """
    Recursively clean a schema node IN PLACE.

    Transformations:
    1. Strip _STRIP_KEYS constraint keywords.
    2. Set additionalProperties:false on every "type":"object" node.
       Exception: anyOf variant with no known properties gets
       additionalProperties:true to signal intentional free-form dict
       (price_target_range use-case).
    3. Ensure all object nodes have "required" listing all property keys
       (Claude strict requires required to be exhaustive).
    """
    if not isinstance(node, dict):
        return

    # 1. Strip unsupported constraint keywords
    for key in list(node.keys()):
        if key in _STRIP_KEYS:
            del node[key]

    # 2. additionalProperties + required on object nodes
    if node.get("type") == "object":
        if "properties" in node:
            # Known-property object: lock it down
            node["additionalProperties"] = False
            if "required" not in node:
                node["required"] = list(node["properties"].keys())
        else:
            # Property-less object (free-form dict like price_target_range)
            # additionalProperties:true signals this is intentional
            node.setdefault("additionalProperties", True)

    # 3. Handle anyOf variants — apply additionalProperties to inline objects
    if "anyOf" in node:
        for variant in node["anyOf"]:
            if isinstance(variant, dict) and variant.get("type") == "object":
                if "properties" in variant:
                    variant["additionalProperties"] = False
                    if "required" not in variant:
                        variant["required"] = list(variant["properties"].keys())
                else:
                    variant.setdefault("additionalProperties", True)

    # Recurse into nested dicts and lists
    for value in node.values():
        if isinstance(value, dict):
            _clean_node(value)
        elif isinstance(value, list):
            for item in value:
                _clean_node(item)


def _clean_schema_for_claude(schema: dict[str, Any]) -> dict[str, Any]:
    """
    Transform Pydantic v2 model_json_schema() output into a Claude strict-mode
    compatible JSON Schema. Returns a NEW dict (does not mutate input).

    Transformations applied (see _clean_node for details):
    - Remove: maxLength, minLength, minimum, maximum, exclusiveMin/Max,
              multipleOf, maxItems, minItems
    - Add: additionalProperties:false on all object-type nodes
    - Add: required:[all properties] on object nodes where missing
    - Remove: top-level "title" and "$schema" keys (noise)

    Does NOT:
    - Flatten $defs/$ref — Claude strict supports internal references.
    - Touch enum values — supported as-is.
    - Touch format:"date-time" — supported by Claude.
    """
    schema = copy.deepcopy(schema)
    _clean_node(schema)
    schema.pop("title", None)
    schema.pop("$schema", None)
    return schema


# ────────────────────────── Tool Definition Builder ─────────────────────────

# Module-level constant so the schema is cleaned once at import time.
# This ensures the tool definition is identical across all requests —
# critical for Claude's 24h schema cache (first call compiles grammar;
# subsequent calls are cache hits saving 200-500ms each).

_RAW_SCHEMA: dict[str, Any] = InvestmentBrief.model_json_schema()
_CLEAN_SCHEMA: dict[str, Any] = _clean_schema_for_claude(_RAW_SCHEMA)

_TOOL_DESCRIPTION = (
    "Synthesize data from multiple financial sources into a structured investment brief. "
    "Called exactly once per synthesis request. Populate every required field. "
    "For cross_source_contradictions, surface any case where two sources give conflicting "
    "signals — e.g. LinkedIn shows aggressive hiring while SEC guidance warns of revenue "
    "softness, or Reddit sentiment is strongly bearish while analyst consensus is bullish. "
    "List each contradiction as a plain English sentence. "
    "Use 'minimal' for data_quality_flag when fewer than 3 sources returned usable data, "
    "'partial' for 3-5, 'full' for 6+."
)


def build_investment_brief_tool() -> dict[str, Any]:
    """
    Build the tools=[...] payload item for client.messages.create().

    The cache_control is placed ON this tool definition (the last tool in the
    array), which caches all tools up to and including this entry. Together
    with the system prompt (Block 1 + Block 2 = ~1,100 tokens), the tool schema
    (~600 tokens) puts total cached tokens well above the 1,024-token threshold
    required for Sonnet 4.6.

    Cache lifecycle: stable for 24h after first use (schema compilation).
    Invalidated by ANY change to name, description, or input_schema.
    Do NOT call this function per-request — call it once at module load or
    startup and reuse the same dict reference.
    """
    return {
        "name": "emit_investment_brief",
        "description": _TOOL_DESCRIPTION,
        "strict": True,
        "input_schema": _CLEAN_SCHEMA,
        # Cache breakpoint 2 of 2: tool definition (stable across all tickers)
        "cache_control": {"type": "ephemeral"},
    }


# Module-level singleton — import this in synthesizer.py to avoid
# rebuilding the schema dict on every call.
INVESTMENT_BRIEF_TOOL: dict[str, Any] = build_investment_brief_tool()
