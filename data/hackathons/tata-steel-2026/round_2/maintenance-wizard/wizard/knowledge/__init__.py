"""
wizard.knowledge
================
Steel-plant ISO-14224 knowledge layer.

Exports:
    ontology        — ONTOLOGY dict + save/load helpers
    templates       — Jinja2 document skeleton renderer
    fmea_graph      — NetworkX FMEA DiGraph builder + RCA path query
    generator       — Synthetic KB generator (CLI + importable)

Typical usage::

    from wizard.knowledge.ontology import ONTOLOGY
    from wizard.knowledge.fmea_graph import build_fmea_graph, get_rca_path
    from wizard.knowledge.generator import KnowledgeBaseGenerator

    G = build_fmea_graph()
    rca = get_rca_path(G, "BF-BRG-002")
"""

from wizard.knowledge.ontology import ONTOLOGY, get_ontology, save_ontology
from wizard.knowledge.templates import TemplateType, render_template, get_template_string
from wizard.knowledge.fmea_graph import (
    build_fmea_graph,
    save_fmea_graph,
    load_fmea_graph,
    get_rca_path,
)

__all__ = [
    # Ontology
    "ONTOLOGY",
    "get_ontology",
    "save_ontology",
    # Templates
    "TemplateType",
    "render_template",
    "get_template_string",
    # FMEA graph
    "build_fmea_graph",
    "save_fmea_graph",
    "load_fmea_graph",
    "get_rca_path",
]
