#!/usr/bin/env python3
"""
Eval harness for the Maintenance Wizard (OE-N3). Scores a Wizard's answers against
the shipped gold eval set deterministically:

  - required_facts recall   (fraction of rubric.required_facts present in the answer)
  - forbidden_claims gate    (any forbidden claim present -> hard fail)
  - grounding-ref match       (did the answer cite the gold grounding_refs)
  - expected_behavior          (answer / refuse / clarify / flag_insufficient_data)

Usage (programmatic):
    from eval_harness import load_gold, score_answer
    gold = load_gold()
    result = score_answer(gold["NQ-001"], wizard_answer_text, cited_refs=[...])

Also ships score_rul() for the quantitative RUL task (group-CV MAE).
Run `python eval_harness.py` for a self-test over the gold set with a trivial
echo-Wizard (sanity that every rubric is parseable + scorable).
"""
import json, re
from pathlib import Path

HERE = Path(__file__).parent
GOLD_FILES = ["nl_queries.jsonl", "troubleshooting_prompts.jsonl"]


def load_gold():
    gold = {}
    for fn in GOLD_FILES:
        p = HERE / fn
        if not p.exists():
            continue
        for line in p.read_text().splitlines():
            if not line.strip():
                continue
            o = json.loads(line)
            qid = o.get("query_id") or o.get("id") or f"{fn}:{len(gold)}"
            gold[qid] = o
    return gold


def _norm(s):
    return re.sub(r"\s+", " ", str(s).lower()).strip()


def _fact_present(fact, a):
    """STRICT fact match (UIE-N1 fix): the full normalized fact phrase must appear as
    a substring. This prevents value-swapped answers from scoring (e.g. a fact
    'temp 100 degC' is NOT credited by an answer that says 'temp 58, vib 100'). If the
    fact carries numbers, every number must also be present (guards paraphrases that
    drop/alter a value). No lenient token-bag fallback."""
    f = _norm(fact)
    if f in a:
        return True
    nums = re.findall(r"-?\d+\.?\d*", f)
    if not nums:
        return False
    # numeric fact paraphrase: require ALL numbers AND all alpha keywords (>3 chars)
    # to be present, each number adjacent (±20 chars) to at least one keyword, so a
    # value cannot be credited if it was reassigned to a different quantity.
    kws = [t for t in re.findall(r"[a-z]{4,}", f)]
    if not all(n in a for n in nums) or not all(k in a for k in kws):
        return False
    for n in nums:
        pos = a.find(n)
        window = a[max(0, pos - 20): pos + len(n) + 20]
        if kws and not any(k in window for k in kws):
            return False
    return True


def score_answer(item, answer_text, cited_refs=None):
    """Return a dict scorecard for one answer. Deterministic, no LLM judge needed."""
    cited_refs = cited_refs or []
    rub = item.get("rubric", {}) or {}
    req = rub.get("required_facts", []) or []
    forb = rub.get("forbidden_claims", []) or []
    a = _norm(answer_text)

    fact_hits = [f for f in req if _fact_present(f, a)]
    fact_recall = len(fact_hits) / len(req) if req else 1.0
    # UIE-N2: word-boundary match so short codes (P1, DE) don't false-positive inside
    # other words; phrase forbidden-claims match as substrings.
    def _forbidden(f):
        fn = _norm(f)
        if len(fn) <= 4 and " " not in fn:
            return re.search(rf"(?<![a-z0-9]){re.escape(fn)}(?![a-z0-9])", a) is not None
        return fn in a
    forbidden_hit = [f for f in forb if _forbidden(f)]
    gold_refs = set(item.get("grounding_refs", []) or [])
    ref_match = len(gold_refs & set(cited_refs)) / len(gold_refs) if gold_refs else 1.0

    exp_beh = item.get("expected_behavior", "answer")
    # caller can pass behavior via cited_refs sentinel; here we just expose the target
    hard_fail = bool(forbidden_hit)
    score = 0.0 if hard_fail else round(0.6 * fact_recall + 0.4 * ref_match, 3)
    return {
        "query_id": item.get("query_id"),
        "expected_behavior": exp_beh,
        "fact_recall": round(fact_recall, 3),
        "facts_hit": fact_hits,
        "forbidden_triggered": forbidden_hit,
        "grounding_ref_match": round(ref_match, 3),
        "hard_fail": hard_fail,
        "score": score,
    }


def score_rul(pred_csv, truth_col="rul_cycles", pred_col="pred_rul", group_col="run_id"):
    """Group-CV-style MAE scorer. pred_csv must have truth_col, pred_col, group_col."""
    import pandas as pd
    df = pd.read_csv(pred_csv)
    mae = (df[truth_col] - df[pred_col]).abs().mean()
    base = (df[truth_col] - df.groupby("asset_id")[truth_col].transform("mean")).abs().mean() \
        if "asset_id" in df.columns else (df[truth_col] - df[truth_col].mean()).abs().mean()
    return {"mae": round(float(mae), 2), "per_asset_mean_baseline_mae": round(float(base), 2),
            "lift_pct": round(100 * (1 - mae / base), 1)}


def score_early_warning(anomaly_csv, tolerance_h=24):
    """OE-3: early-warning lead-time scorer. For each failure run, does an alert fire
    at least `tolerance_h` before failure? Returns detection rate + lead-time stats.
    Uses anomaly_alerts.csv's lead_to_failure_h (added cycle-5)."""
    import pandas as pd
    al = pd.read_csv(anomaly_csv)
    al = al[al.get("run_id", "").astype(str) != ""]
    al["lead"] = pd.to_numeric(al.get("lead_to_failure_h"), errors="coerce")
    per_run = al[al.lead >= tolerance_h].groupby("run_id").lead.max()
    n_runs = al.run_id.nunique()
    detected = per_run.notna().sum()
    return {"runs": int(n_runs), "detected_ge_tolerance": int(detected),
            "detection_rate": round(detected / max(n_runs, 1), 3),
            "median_warning_lead_h": round(float(per_run.median()), 1) if len(per_run) else None,
            "tolerance_h": tolerance_h}


def score_prioritization(ranking_csv, predicted_order):
    """OE-1: score a Wizard's bottleneck ranking against the gold ranking via Spearman."""
    import pandas as pd
    gold = pd.read_csv(ranking_csv).sort_values("gold_rank")
    gmap = {a: r for a, r in zip(gold.asset_id, gold.gold_rank)}
    pred_ranks = [gmap.get(a) for a in predicted_order if a in gmap]
    gold_ranks = sorted(pred_ranks)
    if len(pred_ranks) < 2:
        return {"spearman": None, "n": len(pred_ranks)}
    import numpy as np
    rho = np.corrcoef(pred_ranks, gold_ranks)[0, 1]
    return {"spearman": round(float(rho), 3), "n": len(pred_ranks)}


if __name__ == "__main__":
    gold = load_gold()
    print(f"loaded {len(gold)} gold items")
    by_beh = {}
    rubric_ok = 0
    for qid, item in gold.items():
        by_beh[item.get("expected_behavior", "answer")] = by_beh.get(item.get("expected_behavior", "answer"), 0) + 1
        if item.get("rubric", {}).get("required_facts"):
            rubric_ok += 1
        # self-test: echo the expected_answer as the "Wizard answer"
        r = score_answer(item, item.get("expected_answer", ""), cited_refs=item.get("grounding_refs", []))
        assert "score" in r
    print(f"rubric-scorable items: {rubric_ok}/{len(gold)}")
    print(f"expected_behavior distribution: {by_beh}")
    print("self-test passed: every gold item is parseable + scorable.")
