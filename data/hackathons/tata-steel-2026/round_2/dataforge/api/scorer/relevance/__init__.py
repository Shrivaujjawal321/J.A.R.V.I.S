"""Relevance-gating engine for EDITH DataForge v2."""
from .gate import compute_relevance_score, gate_dataset, build_relevance_trace, score_dataset

__all__ = [
    "compute_relevance_score",
    "gate_dataset",
    "build_relevance_trace",
    "score_dataset",
]
