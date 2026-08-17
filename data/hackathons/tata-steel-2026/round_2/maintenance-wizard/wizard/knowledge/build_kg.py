"""
wizard/knowledge/build_kg.py
=============================
Entrypoint: build the FMEA NetworkX knowledge graph and save it to data/kg/.

Produces:
  data/kg/steel_plant_fmea.json      — NetworkX node_link_data serialization
  data/kg/steel_plant_ontology.json  — Raw ontology JSON

The graph is the same one wired into wizard.rag.kg_retriever at runtime.
This script is idempotent — re-running overwrites the JSON with an identical graph.

Usage::
    python wizard/knowledge/build_kg.py
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("build_kg")


def main() -> None:
    from wizard.knowledge.fmea_graph import build_fmea_graph, save_fmea_graph
    from wizard.knowledge.ontology import save_ontology

    kg_dir = _REPO_ROOT / "data" / "kg"
    kg_dir.mkdir(parents=True, exist_ok=True)

    # Build FMEA graph
    log.info("Building FMEA knowledge graph …")
    G = build_fmea_graph()
    log.info(
        "Graph built: %d nodes, %d edges",
        G.number_of_nodes(),
        G.number_of_edges(),
    )

    # Save graph JSON
    fmea_path = kg_dir / "steel_plant_fmea.json"
    save_fmea_graph(G, fmea_path)
    size_kb = fmea_path.stat().st_size / 1024
    log.info("FMEA graph saved → %s (%.1f KB)", fmea_path, size_kb)

    # Save ontology JSON
    ontology_path = kg_dir / "steel_plant_ontology.json"
    save_ontology(ontology_path)
    size_kb2 = ontology_path.stat().st_size / 1024
    log.info("Ontology saved → %s (%.1f KB)", ontology_path, size_kb2)

    # Quick sanity check
    node_types = {}
    for _, data in G.nodes(data=True):
        nt = data.get("node_type", "unknown")
        node_types[nt] = node_types.get(nt, 0) + 1
    log.info("Node type distribution: %s", node_types)

    fm_count = node_types.get("FailureMode", 0)
    action_count = node_types.get("Action", 0)
    log.info(
        "FailureMode nodes: %d | Action nodes: %d",
        fm_count,
        action_count,
    )

    if G.number_of_nodes() < 50:
        log.error(
            "Graph has only %d nodes — expected ≥200. Check fmea_graph.py.",
            G.number_of_nodes(),
        )
        sys.exit(1)

    log.info("KG build complete.")


if __name__ == "__main__":
    main()
    sys.exit(0)
