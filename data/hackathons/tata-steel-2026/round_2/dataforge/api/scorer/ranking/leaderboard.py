"""
Global leaderboard rank assignment — §2.4 of 03_relevance_and_ranking_engine.md

assign_ranks: in-memory re-rank across all accepted datasets after each upload.
recompute_ranks_jsonl: update audits.jsonl with overall_score + rank for all records.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List


def assign_ranks(datasets: List[Dict]) -> List[Dict]:
    """
    Input:  list of dataset records (dicts) each with at least:
              overall_score, quality_score, domain_pdm_score (optional),
              relevance_score, upload_timestamp (or created_at).
    Output: same list with 'rank' field set.
              Rejected (overall_score==0): rank=0.
              Accepted: 1..N ordered by overall_score DESC + tiebreak.

    RANK() semantics (not DENSE_RANK): ties get same rank, next skips.
    """
    accepted = [d for d in datasets if d.get("overall_score", 0.0) > 0.0]
    rejected = [d for d in datasets if d.get("overall_score", 0.0) == 0.0]

    accepted_sorted = sorted(
        accepted,
        key=lambda d: (
            -(d.get("overall_score", 0.0)),
            -(d.get("quality_score", d.get("composite_score", 0.0))),
            -(d.get("domain_pdm_score", 0.0) or 0.0),
            -(d.get("relevance_score", 0.0)),
            # Earlier upload wins on tie — use upload_timestamp or created_at
            d.get("upload_timestamp", d.get("created_at", "")),
        ),
    )

    current_rank = 1
    prev_score: float = float("nan")
    for i, d in enumerate(accepted_sorted):
        s = d.get("overall_score", 0.0)
        if s != prev_score:
            current_rank = i + 1
        d["rank"] = current_rank
        prev_score = s

    for d in rejected:
        d["rank"] = 0

    return accepted_sorted + rejected


def recompute_ranks_jsonl(audits_path: Path) -> None:
    """
    Reload audits.jsonl, call assign_ranks, write back updated records.
    Idempotent — safe to call after every accepted upload.
    """
    if not audits_path.is_file():
        return

    records: List[Dict] = []
    with open(audits_path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except Exception:
                records.append({})  # preserve line position

    ranked = assign_ranks(records)
    # Rebuild dict by audit_id for merging back
    rank_map = {r.get("audit_id", ""): r.get("rank", 0) for r in ranked}
    score_map = {r.get("audit_id", ""): r.get("overall_score", 0.0) for r in ranked}

    # Re-read originals and patch rank + overall_score in place
    originals: List[Dict] = []
    with open(audits_path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
                aid = rec.get("audit_id", "")
                if aid in rank_map:
                    rec["rank"] = rank_map[aid]
                    rec["overall_score"] = score_map.get(aid, rec.get("overall_score", 0.0))
                originals.append(rec)
            except Exception:
                pass

    with open(audits_path, "w") as f:
        for rec in originals:
            f.write(json.dumps(rec, default=str) + "\n")
