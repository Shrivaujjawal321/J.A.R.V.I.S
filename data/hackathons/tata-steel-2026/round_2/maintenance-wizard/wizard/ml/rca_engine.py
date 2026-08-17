"""
wizard.ml.rca_engine
=====================
3-Layer Root Cause Analysis engine.

Architecture (per research report 11):
  Layer 1 — NetworkX FMEA causal graph traversal (deterministic, <10ms)
             BFS from symptom node up CAUSED_BY / TRIGGERS edges (depth 4).
  Layer 2 — DoWhy GCM anomaly attribution (~200-800ms)
             Per-sensor attribution scores from pre-fitted GraphicalCausalModel.
             Merged with Layer 1: graph edges with high GCM score → HIGH_CONFIDENCE.
  Layer 3 — LLM 5-Whys chain (semantic, 1-3s)
             EvidenceAssembler → FiveWhysReasoner (LiteLLM) → CauseChainValidator
             CauseChainValidator: every claim MUST cite a graph node or RAG chunk.
             Ungrounded claims → [unverified] flag (suppressed from user-facing output).

Graceful degradation:
  Layer 2 absent (no DoWhy / no sensor data) → Layer 1 + Layer 3 only.
  Layer 3 absent (LLM offline) → Layer 1 + 2 only, 5-whys = [].
  Layer 1 graph absent → stub chain from fault_code only.

Public API
----------
  rca_analyze(asset_id, fault_code, fault_description, sensor_df,
               context_chunks, anomaly_scores) -> RCAResult
"""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np

from wizard.core.schemas import CauseChainStep, RCAResult
from wizard.ml.registry import ModelRegistry

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# FMEA graph — embedded seed (loaded from data/kg/steel_plant_fmea.json or fallback)
# ---------------------------------------------------------------------------

_SEED_FMEA_GRAPH: Dict[str, Any] = {
    "nodes": [
        # Blast-furnace family
        {"id": "BF_TUYERE_WEAR",   "label": "BF Tuyere Wear",           "family": "blast_furnace", "severity": "high"},
        {"id": "BF_COOLING_FAIL",  "label": "BF Cooling Failure",       "family": "blast_furnace", "severity": "critical"},
        {"id": "BF_BURNOUT",       "label": "BF Tuyere Burnout",        "family": "blast_furnace", "severity": "critical"},
        # Fan / conveyor
        {"id": "BRG_WEAR",         "label": "Bearing Wear",             "family": "rotating",      "severity": "medium"},
        {"id": "LUB_FAILURE",      "label": "Lubrication Failure",      "family": "rotating",      "severity": "medium"},
        {"id": "VIBRATION_HIGH",   "label": "Abnormal Vibration",       "family": "rotating",      "severity": "high"},
        # Hydraulic
        {"id": "HYD_SEAL_DEG",     "label": "Hydraulic Seal Degradation","family": "hydraulic",    "severity": "medium"},
        {"id": "HYD_PRESS_DROP",   "label": "Hydraulic Pressure Drop",  "family": "hydraulic",     "severity": "high"},
        {"id": "HYD_PUMP_FAIL",    "label": "Hydraulic Pump Failure",   "family": "hydraulic",     "severity": "critical"},
        # AI4I fault modes (steel aliased)
        {"id": "WRD",              "label": "Work Roll Degradation",    "family": "rolling_mill",  "severity": "medium"},
        {"id": "HCF",              "label": "Heat Dissipation Failure", "family": "thermal",       "severity": "high"},
        {"id": "DMO",              "label": "Drive Motor Overload",     "family": "electrical",    "severity": "critical"},
        {"id": "RFE",              "label": "Roll Force Exceedance",    "family": "rolling_mill",  "severity": "high"},
        {"id": "UNA",              "label": "Unclassified Anomaly",     "family": "unknown",       "severity": "medium"},
        # Root causes
        {"id": "MISSED_PM",        "label": "Missed Preventive Maintenance","family": "process",   "severity": "medium"},
        {"id": "PROD_DEFERRAL",    "label": "Production-Priority PM Deferral","family": "process", "severity": "medium"},
        {"id": "OVERLOAD",         "label": "Equipment Overload",       "family": "operational",   "severity": "high"},
        {"id": "ABRASIVE_WEAR",    "label": "Abrasive Wear (Process)",  "family": "operational",   "severity": "medium"},
    ],
    "edges": [
        # blast furnace chain
        {"source": "BF_BURNOUT",       "target": "BF_COOLING_FAIL",  "relation": "caused_by", "sop": "BF-SOP-001 §3.4"},
        {"source": "BF_COOLING_FAIL",  "target": "BF_TUYERE_WEAR",   "relation": "caused_by", "sop": "BF-SOP-001 §2.1"},
        {"source": "BF_TUYERE_WEAR",   "target": "ABRASIVE_WEAR",    "relation": "caused_by", "sop": "BF-SOP-001 §1.5"},
        # rotating machinery
        {"source": "VIBRATION_HIGH",   "target": "BRG_WEAR",         "relation": "caused_by", "sop": "ROT-SOP-003 §4.2"},
        {"source": "BRG_WEAR",         "target": "LUB_FAILURE",      "relation": "caused_by", "sop": "ROT-SOP-003 §2.3"},
        {"source": "LUB_FAILURE",      "target": "MISSED_PM",        "relation": "caused_by", "sop": "ROT-SOP-003 §1.1"},
        {"source": "MISSED_PM",        "target": "PROD_DEFERRAL",    "relation": "caused_by", "sop": "PROC-SOP-007 §1.0"},
        # hydraulic chain
        {"source": "HYD_PUMP_FAIL",    "target": "HYD_PRESS_DROP",  "relation": "caused_by", "sop": "HYD-SOP-002 §4.2"},
        {"source": "HYD_PRESS_DROP",   "target": "HYD_SEAL_DEG",    "relation": "caused_by", "sop": "HYD-SOP-002 §3.1"},
        {"source": "HYD_SEAL_DEG",     "target": "MISSED_PM",       "relation": "caused_by", "sop": "HYD-SOP-002 §1.2"},
        # rolling mill / AI4I
        {"source": "WRD",              "target": "ABRASIVE_WEAR",    "relation": "caused_by", "sop": "MILL-SOP-005 §2.1"},
        {"source": "HCF",              "target": "OVERLOAD",         "relation": "caused_by", "sop": "THERM-SOP-004 §3.3"},
        {"source": "DMO",              "target": "OVERLOAD",         "relation": "caused_by", "sop": "ELEC-SOP-006 §2.2"},
        {"source": "RFE",              "target": "OVERLOAD",         "relation": "caused_by", "sop": "MILL-SOP-005 §3.0"},
    ],
}

# Fault-code → FMEA node mapping
_FAULT_CODE_MAP: Dict[str, str] = {
    "WRD": "WRD", "TWF": "WRD",
    "HCF": "HCF", "HDF": "HCF",
    "DMO": "DMO", "PWF": "DMO",
    "RFE": "RFE", "OSF": "RFE",
    "UNA": "UNA", "RNF": "UNA",
    "BRG-WEAR-001": "BRG_WEAR",
    "VIBRATION-HIGH": "VIBRATION_HIGH",
    "HYD-PRESS-DROP": "HYD_PRESS_DROP",
    "BF-TUYERE-WEAR": "BF_TUYERE_WEAR",
}


# ---------------------------------------------------------------------------
# Layer 1: NetworkX FMEA graph traversal
# ---------------------------------------------------------------------------

def _load_fmea_graph() -> "networkx.DiGraph":  # type: ignore[name-defined]
    """
    Load the FMEA causal graph from data/kg/steel_plant_fmea.json.
    Falls back to the embedded seed graph if the file is missing.
    """
    try:
        import networkx as nx  # type: ignore[import]

        # Try loading from disk
        here = Path(__file__).resolve()
        for parent in here.parents:
            if (parent / "pyproject.toml").exists():
                kg_path = parent / "data" / "kg" / "steel_plant_fmea.json"
                break
        else:
            kg_path = Path.cwd() / "data" / "kg" / "steel_plant_fmea.json"

        if kg_path.exists():
            data = json.loads(kg_path.read_text())
            logger.debug("Loaded FMEA graph from %s", kg_path)
        else:
            data = _SEED_FMEA_GRAPH
            logger.debug("Using embedded seed FMEA graph.")

        G = nx.DiGraph()
        for node in data.get("nodes", []):
            G.add_node(node["id"], **{k: v for k, v in node.items() if k != "id"})
        for edge in data.get("edges", []):
            G.add_edge(
                edge["source"], edge["target"],
                relation=edge.get("relation", "caused_by"),
                sop=edge.get("sop", ""),
            )
        return G
    except ImportError:
        logger.warning("networkx not installed — Layer 1 traversal disabled.")
        return None  # type: ignore[return-value]


def _layer1_traverse(
    G: Optional[Any],  # networkx.DiGraph
    fault_code: str,
    depth: int = 4,
) -> List[CauseChainStep]:
    """
    BFS backward traversal from the symptom node.

    Returns ordered list of CauseChainStep (proximate → root).
    """
    if G is None:
        return []

    # Map fault code to graph node
    start_node = _FAULT_CODE_MAP.get(fault_code, fault_code)
    if start_node not in G.nodes:
        # Try partial match
        for nid in G.nodes:
            if fault_code.upper() in nid:
                start_node = nid
                break
        else:
            logger.debug("Layer1: fault_code '%s' not found in FMEA graph.", fault_code)
            return []

    steps: List[CauseChainStep] = []
    visited = {start_node}
    frontier = [start_node]
    current_depth = 0

    while frontier and current_depth < depth:
        next_frontier = []
        for node in frontier:
            # Edges are directed symptom→cause (e.g. BF_BURNOUT→BF_COOLING_FAIL→BF_TUYERE_WEAR).
            # Use successors to traverse the caused_by chain from symptom to root cause.
            try:
                successors = list(G.successors(node))
            except Exception:
                successors = []

            for succ in successors:
                if succ in visited:
                    continue
                visited.add(succ)
                edge_data = G.get_edge_data(node, succ, {})
                node_data = G.nodes.get(succ, {})
                steps.append(CauseChainStep(
                    node_id=succ,
                    node_label=node_data.get("label", succ),
                    edge_relation=edge_data.get("relation", "caused_by"),
                    cited_source=edge_data.get("sop") or None,
                    layer="graph",
                ))
                next_frontier.append(succ)

        frontier = next_frontier
        current_depth += 1

    return steps


# ---------------------------------------------------------------------------
# Layer 2: DoWhy GCM anomaly attribution
# ---------------------------------------------------------------------------

def _layer2_gcm_attribution(
    sensor_df: Optional["pandas.DataFrame"],  # type: ignore[name-defined]
    anomaly_scores: Optional[Dict[str, float]],
    gcm_artifact: Optional[Any],
) -> Dict[str, float]:
    """
    Run DoWhy GCM attribute_anomalies on sensor data.

    Returns dict {node_id: attribution_score} for nodes above 0.3 threshold.
    Falls back to anomaly_scores dict re-labelled if DoWhy unavailable.
    """
    # Fast fallback: return anomaly scores re-named as node IDs
    if anomaly_scores:
        # Map sensor names to FMEA nodes where possible
        sensor_to_node = {
            "vibration_mm_s": "VIBRATION_HIGH",
            "temperature_c":  "HCF",
            "pressure_bar":   "HYD_PRESS_DROP",
            "torque_nm":      "DMO",
        }
        result = {}
        for sensor, score in anomaly_scores.items():
            node = sensor_to_node.get(sensor, sensor)
            if float(score) >= 0.3:
                result[node] = round(float(score), 4)
        if result:
            logger.debug("Layer2: using anomaly_scores fallback (no GCM).")
            return result

    if sensor_df is None or sensor_df.empty:
        return {}

    try:
        import dowhy.gcm as gcm  # type: ignore[import]

        if gcm_artifact is None:
            logger.debug("Layer2: no GCM artifact — skipping DoWhy attribution.")
            return {}

        causal_model = gcm_artifact.get("causal_model")
        target_node  = gcm_artifact.get("target_node", "machine_failure")
        if causal_model is None:
            return {}

        # attribute_anomalies expects an anomaly sample (last row) vs. normal distribution
        normal_data = gcm_artifact.get("normal_data", sensor_df.tail(30))
        anomaly_sample = sensor_df.tail(1)

        attributions = gcm.attribute_anomalies(
            causal_model,
            target_node,
            anomaly_samples=anomaly_sample,
        )
        result = {}
        for node_id, score in attributions.items():
            s = float(np.mean(np.abs(score)))
            if s >= 0.3:
                result[str(node_id)] = round(s, 4)

        logger.debug("Layer2: GCM attributions computed for %d nodes.", len(result))
        return result

    except ImportError:
        logger.debug("DoWhy not installed — Layer2 attribution skipped.")
        return {}
    except Exception as exc:
        logger.warning("DoWhy GCM attribution error: %s", exc)
        return {}


# ---------------------------------------------------------------------------
# Layer 3: LLM 5-Whys + CauseChainValidator
# ---------------------------------------------------------------------------

_FIVE_WHYS_SCHEMA = {
    "why_1": "string",
    "why_2": "string",
    "why_3": "string",
    "why_4": "string",
    "why_5": "string",
    "root_cause": "string",
    "evidence_refs": "list of node_ids or SOP section strings",
}

_FIVE_WHYS_SYSTEM = """You are a steel-plant maintenance expert. Your task is root-cause analysis.
Given the evidence below, produce a structured 5-Whys chain in JSON format.

Rules:
1. Every 'why' statement MUST cite at least one evidence_ref from the provided evidence.
2. evidence_refs must be exact node IDs from the FMEA graph or SOP section strings provided.
3. Do NOT introduce entities not present in the evidence block.
4. Output ONLY valid JSON matching the schema. No prose outside the JSON object.

Schema:
{
  "why_1": "<immediate observable symptom>",
  "why_2": "<cause of why_1, evidence_ref: [...]>",
  "why_3": "<cause of why_2, evidence_ref: [...]>",
  "why_4": "<cause of why_3, evidence_ref: [...]>",
  "why_5": "<root cause, evidence_ref: [...]>",
  "root_cause": "<one-sentence root cause summary>",
  "evidence_refs": ["node_id_1", "SOP-XXX §Y.Z", ...]
}"""


def _build_evidence_block(
    fault_code: str,
    fault_description: str,
    cause_chain: List[CauseChainStep],
    gcm_attributions: Dict[str, float],
    context_chunks: Optional[List[str]],
) -> str:
    lines = [
        f"FAULT: {fault_code} — {fault_description}",
        "",
        "FMEA GRAPH CAUSE CHAIN:",
    ]
    for i, step in enumerate(cause_chain, 1):
        src = f" [cite: {step.cited_source}]" if step.cited_source else ""
        lines.append(f"  Step {i}: {step.node_label} ({step.node_id}){src}")

    if gcm_attributions:
        lines.append("")
        lines.append("GCM ATTRIBUTION SCORES (threshold > 0.3):")
        for node, score in sorted(gcm_attributions.items(), key=lambda x: -x[1]):
            lines.append(f"  {node}: {score:.3f}")

    if context_chunks:
        lines.append("")
        lines.append("RETRIEVED SOP / MAINTENANCE CONTEXT:")
        for j, chunk in enumerate(context_chunks[:5], 1):
            lines.append(f"  [Chunk {j}] {chunk[:200]}")

    return "\n".join(lines)


def _parse_five_whys_json(raw: str) -> Optional[Dict[str, Any]]:
    """Extract JSON from LLM output (may be wrapped in markdown code block)."""
    # Strip code fences
    raw = raw.strip()
    if raw.startswith("```"):
        raw = re.sub(r"```[a-z]*\n?", "", raw).strip().rstrip("`").strip()
    try:
        return json.loads(raw)
    except Exception:
        # Try to find JSON block
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except Exception:
                pass
    return None


def _validate_claims(
    five_whys: Dict[str, Any],
    valid_refs: List[str],
) -> tuple[List[str], List[str]]:
    """
    CauseChainValidator: verify each why statement cites a valid ref.

    Returns (validated_whys, unverified_claims).
    """
    validated: List[str] = []
    unverified: List[str] = []
    evidence_refs = five_whys.get("evidence_refs", [])

    for key in ["why_1", "why_2", "why_3", "why_4", "why_5"]:
        why_text = str(five_whys.get(key, ""))
        if not why_text:
            continue
        # Check if any valid_ref appears in the evidence_refs list
        has_grounding = any(
            str(ref) in str(evidence_refs) or str(ref) in why_text
            for ref in valid_refs
        )
        if has_grounding:
            validated.append(why_text)
        else:
            unverified.append(why_text + " [unverified]")

    return validated, unverified


def _layer3_llm_five_whys(
    fault_code: str,
    fault_description: str,
    cause_chain: List[CauseChainStep],
    gcm_attributions: Dict[str, float],
    context_chunks: Optional[List[str]],
) -> tuple[List[str], List[str]]:
    """
    LLM-powered 5-Whys with CauseChainValidator.

    Returns (validated_whys, unverified_claims).
    Falls back to [] if LLM unavailable.
    """
    evidence_block = _build_evidence_block(
        fault_code, fault_description, cause_chain, gcm_attributions, context_chunks
    )

    # Valid refs = all graph node IDs + SOP citations in cause chain
    valid_refs: List[str] = [step.node_id for step in cause_chain]
    valid_refs += [step.cited_source for step in cause_chain if step.cited_source]
    valid_refs += list(gcm_attributions.keys())

    try:
        import litellm  # type: ignore[import]
        from wizard.core.config import settings

        messages = [
            {"role": "system", "content": _FIVE_WHYS_SYSTEM},
            {"role": "user",   "content": f"EVIDENCE:\n{evidence_block}\n\nGenerate the 5-Whys JSON now."},
        ]

        response = litellm.completion(
            model=settings.llm_model_light,
            messages=messages,
            temperature=0.1,
            max_tokens=1024,
            timeout=settings.llm_timeout_seconds,
        )
        raw_output = response.choices[0].message.content or ""
        parsed = _parse_five_whys_json(raw_output)

        if parsed is None:
            logger.warning("Layer3: LLM returned non-JSON output — skipping 5-whys.")
            return [], []

        validated, unverified = _validate_claims(parsed, valid_refs)
        logger.debug(
            "Layer3: %d validated whys, %d unverified claims.",
            len(validated), len(unverified)
        )
        return validated, unverified

    except ImportError:
        logger.debug("litellm not installed — Layer3 5-whys skipped.")
        return [], []
    except Exception as exc:
        logger.warning("Layer3 LLM 5-whys failed: %s", exc)
        return [], []


# ---------------------------------------------------------------------------
# Public: rca_analyze
# ---------------------------------------------------------------------------

def rca_analyze(
    asset_id: str,
    fault_log_id: str,
    fault_code: str,
    fault_description: str = "",
    sensor_df: Optional[Any] = None,          # pd.DataFrame or None
    context_chunks: Optional[List[str]] = None,
    anomaly_scores: Optional[Dict[str, float]] = None,
) -> RCAResult:
    """
    Run 3-layer Root Cause Analysis.

    Parameters
    ----------
    asset_id : str
        Equipment identifier.
    fault_log_id : str
        FK → FaultLog.entity_id.
    fault_code : str
        Primary fault code (e.g. 'WRD', 'HDF', 'BRG-WEAR-001').
    fault_description : str
        Human-readable fault description.
    sensor_df : pd.DataFrame, optional
        Sensor time-series window (24h before fault) for GCM attribution.
    context_chunks : list[str], optional
        Top-k RAG chunks retrieved for this equipment / fault.
    anomaly_scores : dict[str, float], optional
        Per-sensor anomaly scores from anomaly detector.

    Returns
    -------
    RCAResult (wizard.core.schemas)
    """
    logger.info("RCA analysis: asset=%s, fault=%s", asset_id, fault_code)

    # --- Layer 1: Graph traversal ---
    G = _load_fmea_graph()
    cause_chain = _layer1_traverse(G, fault_code, depth=4)
    logger.debug("Layer1: %d cause chain steps.", len(cause_chain))

    # --- Layer 2: DoWhy GCM ---
    gcm_artifact = ModelRegistry.load("rca_gcm_default", fallback=None)
    gcm_attributions = _layer2_gcm_attribution(sensor_df, anomaly_scores, gcm_artifact)
    logger.debug("Layer2: %d GCM attributions.", len(gcm_attributions))

    # Promote cause_chain steps with high GCM scores to HIGH_CONFIDENCE layer tag
    gcm_node_ids = set(gcm_attributions.keys())
    promoted_chain: List[CauseChainStep] = []
    for step in cause_chain:
        if step.node_id in gcm_node_ids:
            promoted = CauseChainStep(
                node_id=step.node_id,
                node_label=step.node_label,
                edge_relation=step.edge_relation,
                cited_source=step.cited_source,
                layer="gcm",  # elevated confidence
            )
            promoted_chain.append(promoted)
        else:
            promoted_chain.append(step)

    # --- Layer 3: LLM 5-Whys ---
    five_whys, unverified = _layer3_llm_five_whys(
        fault_code, fault_description,
        promoted_chain, gcm_attributions, context_chunks,
    )

    # --- Root cause summary ---
    if promoted_chain:
        deepest_step = promoted_chain[-1]
        root_cause_summary = f"{deepest_step.node_label} ({deepest_step.node_id})"
        if deepest_step.cited_source:
            root_cause_summary += f" — ref: {deepest_step.cited_source}"
    elif fault_description:
        root_cause_summary = fault_description
    else:
        root_cause_summary = f"Fault code {fault_code} — manual investigation required."

    # Collect cited sources
    cited: List[str] = []
    for step in promoted_chain:
        if step.cited_source:
            cited.append(step.cited_source)
    if context_chunks:
        cited.extend([f"rag_chunk_{i}" for i in range(min(3, len(context_chunks)))])

    return RCAResult(
        asset_id=asset_id,
        fault_log_id=fault_log_id,
        cause_chain=promoted_chain,
        root_cause_summary=root_cause_summary,
        five_whys=five_whys,
        gcm_attributions=gcm_attributions,
        cited_sources=cited,
    )


# ---------------------------------------------------------------------------
# Offline training: fit DoWhy GCM on sensor data
# ---------------------------------------------------------------------------

def train_rca_gcm(
    sensor_df: "pandas.DataFrame",  # type: ignore[name-defined]
    target_col: str = "machine_failure",
    models_dir: Optional[Path] = None,
) -> None:
    """
    Fit a DoWhy GraphicalCausalModel on historical sensor data.
    Saves the fitted model as 'rca_gcm_default.pkl'.

    DAG structure is hand-specified from the FMEA seed graph (Layer 1).
    PC-algorithm discovery is NOT used (anti-pattern per report 11 §4 Alt B).
    """
    try:
        import dowhy.gcm as gcm  # type: ignore[import]
        import networkx as nx    # type: ignore[import]
        import joblib            # type: ignore[import]
    except ImportError as exc:
        raise ImportError("pip install dowhy networkx joblib") from exc

    if models_dir is None:
        here = Path(__file__).resolve()
        for parent in here.parents:
            if (parent / "pyproject.toml").exists():
                models_dir = parent / "data" / "models"
                break
        else:
            models_dir = Path.cwd() / "data" / "models"
    models_dir.mkdir(parents=True, exist_ok=True)

    # Build a simple causal DAG from available sensor columns
    sensor_cols = [c for c in sensor_df.columns if c != target_col]

    G_causal = nx.DiGraph()
    G_causal.add_nodes_from(sensor_cols + [target_col])
    # Hand-specify directional edges (sensors → failure)
    for col in sensor_cols:
        G_causal.add_edge(col, target_col)

    # Also add natural physical dependencies where known
    if "temperature_c" in sensor_cols and "pressure_bar" in sensor_cols:
        G_causal.add_edge("temperature_c", "pressure_bar")
    if "vibration_mm_s" in sensor_cols and "temperature_c" in sensor_cols:
        G_causal.add_edge("vibration_mm_s", "temperature_c")

    causal_model = gcm.StructuralCausalModel(G_causal)

    # Auto-assign mechanisms
    gcm.auto.assign_causal_mechanisms(causal_model, sensor_df)

    # Fit
    logger.info("Fitting DoWhy GCM on %d samples ...", len(sensor_df))
    gcm.fit(causal_model, sensor_df)
    logger.info("DoWhy GCM fitted.")

    artifact = {
        "causal_model": causal_model,
        "target_node": target_col,
        "normal_data": sensor_df[sensor_df[target_col] == 0].tail(100),
    }
    out_path = models_dir / "rca_gcm_default.pkl"
    joblib.dump(artifact, out_path)
    logger.info("Saved DoWhy GCM artifact → %s", out_path)
