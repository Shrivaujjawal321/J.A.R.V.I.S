#!/usr/bin/env python3
"""
EDITH end-to-end eval — runs the dataset's gold eval set against the LIVE /api/ask
and scores with the dataset's own deterministic eval harness (no LLM judge).
Produces the measured-accuracy evidence judges never see from other teams.

Usage:  .venv/bin/python eval_run.py [--limit N] [--base http://127.0.0.1:8077]
Writes: edith/data/eval_results.json + edith/EVAL_RESULTS.md
"""
import argparse, json, re, sys, time
from pathlib import Path

import requests

HERE = Path(__file__).resolve().parent
R2 = HERE.parent
DATASET = R2 / "dataforge" / "datasets" / "steel-maintenance-flagship"
sys.path.insert(0, str(DATASET / "user_interaction"))
import eval_harness as eh  # noqa: E402


def _basename(ref: str) -> str:
    """normalize a grounding ref to a comparable basename (strip anchors/paths)."""
    r = str(ref)
    r = r.split("#")[0]
    r = r.split("/")[-1]
    return r.lower()


def answer_text_of(resp: dict) -> str:
    parts = [resp.get("answer") or ""]
    for s in resp.get("sections") or []:
        parts += [s.get("title", ""), s.get("brief", ""), s.get("detail", "")]
    return "\n".join(p for p in parts if p)


def behavior_of(resp: dict, answer: str) -> str:
    # primary signal: the API's own intent (robust); fallback: phrase sniffing
    intent = (resp.get("intent") or "").lower()
    if intent in ("clarification",):
        return "clarify"
    if intent in ("refusal", "out_of_scope", "unknown_asset"):
        return "refuse_or_flag"
    a = answer.lower()
    if any(k in a for k in ["could not identify which machine", "please name the asset",
                            "please name the exact machine", "please type a question"]):
        return "clarify"
    if any(k in a for k in ["cannot answer", "out of scope", "i can't help",
                            "not something i can", "no such asset", "does not exist",
                            "insufficient data", "i don't have data", "have no data",
                            "won't guess", "i won't guess"]):
        return "refuse_or_flag"
    return "answer"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--base", default="http://127.0.0.1:8077")
    args = ap.parse_args()

    gold = eh.load_gold()  # nl_queries + troubleshooting prompts, rubric'd
    items = list(gold.items())
    if args.limit:
        items = items[: args.limit]

    results = []
    lat = []
    t0 = time.time()
    for i, (qid, item) in enumerate(items, 1):
        query = item.get("query") or item.get("prompt") or ""
        if not query:
            continue
        t = time.time()
        try:
            r = requests.post(f"{args.base}/api/ask",
                              json={"query": query, "session_id": f"eval-{qid}"},
                              timeout=60)
            resp = r.json()
        except Exception as e:
            results.append({"query_id": qid, "error": str(e)[:120]})
            continue
        ms = int((time.time() - t) * 1000)
        lat.append(ms)
        answer = answer_text_of(resp)
        cited = [_basename(s) for s in (resp.get("sources") or [])]
        # score against the gold rubric; align refs by basename for fairness
        gold_refs = [_basename(g) for g in (item.get("grounding_refs") or [])]
        item_for_score = dict(item)
        item_for_score["grounding_refs"] = gold_refs
        sc = eh.score_answer(item_for_score, answer, cited_refs=cited)
        beh = behavior_of(resp, answer)
        exp_beh = item.get("expected_behavior", "answer")
        beh_ok = (beh == "answer") if exp_beh == "answer" else (beh != "answer")
        results.append({
            "query_id": qid, "category": item.get("category", ""),
            "lang": item.get("lang", "en"), "expected_behavior": exp_beh,
            "behavior": beh, "behavior_ok": beh_ok,
            "fact_recall": sc["fact_recall"], "hard_fail": sc["hard_fail"],
            "grounding_ref_match": sc["grounding_ref_match"],
            "score": sc["score"], "latency_ms": ms,
        })
        if i % 25 == 0:
            print(f"  {i}/{len(items)} done…")

    ok = [r for r in results if "error" not in r]
    answerable = [r for r in ok if r["expected_behavior"] == "answer"]
    guard = [r for r in ok if r["expected_behavior"] != "answer"]
    import statistics as st
    summary = {
        "items_run": len(ok), "errors": len(results) - len(ok),
        "wall_seconds": round(time.time() - t0, 1),
        "answerable": {
            "n": len(answerable),
            "mean_fact_recall": round(st.mean(r["fact_recall"] for r in answerable), 3) if answerable else None,
            "forbidden_claim_violations": sum(r["hard_fail"] for r in answerable),
            "mean_grounding_match": round(st.mean(r["grounding_ref_match"] for r in answerable), 3) if answerable else None,
        },
        "guardrail": {
            "n": len(guard),
            "correct_behavior_rate": round(st.mean(1.0 if r["behavior_ok"] else 0.0 for r in guard), 3) if guard else None,
            "confident_wrong_answers": sum(1 for r in guard if not r["behavior_ok"] and r["hard_fail"]),
        },
        "latency_ms": {
            "p50": int(st.median(lat)) if lat else None,
            "p90": int(sorted(lat)[int(len(lat) * 0.9)]) if lat else None,
            "max": max(lat) if lat else None,
        },
        "by_lang": {},
    }
    for lang in sorted({r["lang"] for r in ok}):
        sub = [r for r in ok if r["lang"] == lang and r["expected_behavior"] == "answer"]
        if sub:
            summary["by_lang"][lang] = {
                "n": len(sub),
                "mean_fact_recall": round(st.mean(r["fact_recall"] for r in sub), 3),
            }

    out = {"summary": summary, "results": results}
    (HERE / "data" / "eval_results.json").write_text(json.dumps(out, indent=2))

    s = summary
    md = f"""# EDITH — Measured Accuracy (end-to-end eval)

EDITH was evaluated **end-to-end** (live `/api/ask` → multi-agent pipeline → scored answer)
against the dataset's **{s['items_run']}-item gold eval set** using its deterministic eval
harness (strict fact matching + forbidden-claim gate — no LLM judge, fully reproducible).

| Metric | Value |
|---|---|
| Gold items run | {s['items_run']} (errors: {s['errors']}) |
| **Fact recall (answerable, n={s['answerable']['n']})** | **{s['answerable']['mean_fact_recall']}** |
| **Forbidden-claim violations** (confident wrong statements) | **{s['answerable']['forbidden_claim_violations']}** |
| Grounding-citation match | {s['answerable']['mean_grounding_match']} |
| **Guardrail behavior** (adversarial/unanswerable, n={s['guardrail']['n']}) | **{s['guardrail']['correct_behavior_rate']}** correct (refuse/clarify instead of guessing) |
| Latency p50 / p90 | {s['latency_ms']['p50']} ms / {s['latency_ms']['p90']} ms |

Per-language fact recall: {json.dumps(s['by_lang'])}

Reproduce: `python eval_run.py` (backend running). Raw per-item results: `data/eval_results.json`.
"""
    (HERE / "EVAL_RESULTS.md").write_text(md)
    print(json.dumps(summary, indent=2))
    print(f"\nwrote EVAL_RESULTS.md + data/eval_results.json")


if __name__ == "__main__":
    main()
