#!/usr/bin/env python3
"""
eval_audit_verify.py — AuditAgent verify-layer evaluation harness.

Loads labeled cases from data/evals/audit/verify_cases.jsonl, runs them
through the context classifier and (optionally) the LLM verify pipeline,
then prints:
  - Per-case results with verdicts + verdicts-vs-expected
  - Confusion matrix: FP-kill rate, true-confirm rate, misses
  - An overall PASS/FAIL signal (FP-kill ≥ 80%, recall-preserved ≥ 90%)

Modes:
  --deterministic-only  (default)  — classify_context + deterministic_triage only.
                                     No LLM calls. Fast, free, fully testable in CI.
  --llm                            — Run the full verify_findings pipeline with LLM.
                                     Requires the Jarvis daemon + run_worker to be
                                     importable and responsive. Not run in CI by default.

Usage:
  .venv/bin/python scripts/eval_audit_verify.py               # deterministic only
  .venv/bin/python scripts/eval_audit_verify.py --llm         # full LLM run
  .venv/bin/python scripts/eval_audit_verify.py --quiet       # minimal output
"""
from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path

# Ensure project root on path
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from jarvis_core.audit_agent.context import (
    classify_context,
    CATEGORY_BUILD,
    CATEGORY_DOCUMENTATION,
    CATEGORY_EXAMPLE,
    CATEGORY_TEST,
)
from jarvis_core.audit_agent.models import Finding, Severity, VerificationStatus
from jarvis_core.audit_agent.pipeline import _deterministic_triage, verify_findings

_CASES_PATH = _ROOT / "data" / "evals" / "audit" / "verify_cases.jsonl"

_DETERMINISTIC_FP_THRESHOLD = 0.85  # mirrors pipeline.py Pass 0

# Severity string → enum
_SEV_MAP = {
    "critical": Severity.CRITICAL,
    "high": Severity.HIGH,
    "medium": Severity.MEDIUM,
    "low": Severity.LOW,
    "info": Severity.INFO,
}


def _load_cases() -> list[dict]:
    cases = []
    with _CASES_PATH.open() as fh:
        for line in fh:
            line = line.strip()
            if line:
                cases.append(json.loads(line))
    return cases


def _make_finding_from_case(case: dict) -> Finding:
    sev_str = case.get("severity", "medium").lower()
    severity = _SEV_MAP.get(sev_str, Severity.MEDIUM)
    return Finding(
        scanner=case.get("scanner", "semgrep"),
        rule_id=case.get("rule_id", "unknown-rule"),
        severity=severity,
        file_path=case.get("file_path"),
        line_start=case.get("line_start"),
        evidence=case.get("evidence", ""),
        cwe=case.get("cwe"),
    )


def _deterministic_run(cases: list[dict]) -> list[dict]:
    """Run classify_context + deterministic pre-triage on each case.

    This mirrors exactly what verify_findings Pass 0 does.
    Returns a list of result dicts per case.
    """
    results = []
    for case in cases:
        finding = _make_finding_from_case(case)
        ctx = classify_context(finding.file_path)

        # Apply Pass 0 logic — mirrors pipeline.py exactly
        if (
            ctx.category in (CATEGORY_TEST, CATEGORY_DOCUMENTATION, CATEGORY_EXAMPLE, CATEGORY_BUILD)
            and ctx.fp_prior >= _DETERMINISTIC_FP_THRESHOLD
        ):
            verdict = "false_positive"
            reason = f"[det] {ctx.rationale} (fp_prior={ctx.fp_prior:.0%})"
        else:
            # Deterministic triage fallback (no LLM)
            _deterministic_triage([finding])
            verdict = finding.verification_status.value
            reason = finding.verification_reason or f"[det-fallback] category={ctx.category}"

        results.append({
            "case_id": case["case_id"],
            "label": case.get("label", ""),
            "file_path": case.get("file_path"),
            "expected_verdict": case["expected_verdict"],
            "expected_category": case.get("expected_category"),
            "got_category": ctx.category,
            "got_verdict": verdict,
            "reason": reason,
            "correct": _verdicts_match(verdict, case["expected_verdict"]),
            "note": case.get("note", ""),
        })
    return results


async def _llm_run(cases: list[dict]) -> list[dict]:
    """Run the full verify_findings pipeline (with LLM) on each case."""
    findings = [_make_finding_from_case(c) for c in cases]

    # verify_findings updates findings in-place and returns them
    updated, _ = await verify_findings(findings, max_budget_usd=2.0)

    results = []
    for case, finding in zip(cases, updated):
        verdict = finding.verification_status.value
        ctx = classify_context(finding.file_path)
        results.append({
            "case_id": case["case_id"],
            "label": case.get("label", ""),
            "file_path": case.get("file_path"),
            "expected_verdict": case["expected_verdict"],
            "expected_category": case.get("expected_category"),
            "got_category": ctx.category,
            "got_verdict": verdict,
            "reason": finding.verification_reason or "(no reason stored)",
            "correct": _verdicts_match(verdict, case["expected_verdict"]),
            "note": case.get("note", ""),
        })
    return results


def _verdicts_match(got: str, expected: str) -> bool:
    """Flexible match: needs_manual is acceptable for confirmed cases.

    We are STRICT on FP-kills: if expected=false_positive, only false_positive counts.
    For confirmed: confirmed = win, needs_manual = acceptable (kept in queue), confirmed-as-FP = miss.
    """
    if expected == "false_positive":
        return got == "false_positive"
    if expected == "confirmed":
        return got in ("confirmed", "needs_manual")  # needs_manual keeps it in play
    if expected == "needs_manual":
        return got in ("needs_manual", "confirmed")  # conservative confirm is OK
    return got == expected


def _compute_metrics(results: list[dict]) -> dict:
    """Compute FP-kill rate and true-confirm rate (recall-preserved)."""
    # FP-kill: of cases expected to be false_positive, how many were killed?
    known_fps = [r for r in results if r["expected_verdict"] == "false_positive"]
    correctly_killed = [r for r in known_fps if r["got_verdict"] == "false_positive"]
    fp_kill_rate = len(correctly_killed) / len(known_fps) if known_fps else 0.0

    # FP leaked through (false negatives of the killer = real FPs we let through)
    leaked_fps = [r for r in known_fps if r["got_verdict"] != "false_positive"]

    # True-confirm recall: of cases expected confirmed/needs_manual, how many did we NOT kill?
    known_real = [r for r in results if r["expected_verdict"] in ("confirmed", "needs_manual")]
    not_killed = [r for r in known_real if r["got_verdict"] != "false_positive"]
    recall_preserved = len(not_killed) / len(known_real) if known_real else 0.0

    # True positives accidentally killed (worst failure mode)
    false_negatives = [r for r in known_real if r["got_verdict"] == "false_positive"]

    # Overall accuracy
    total = len(results)
    correct = sum(1 for r in results if r["correct"])
    accuracy = correct / total if total else 0.0

    return {
        "total": total,
        "correct": correct,
        "accuracy": accuracy,
        "fp_kill_rate": fp_kill_rate,
        "recall_preserved": recall_preserved,
        "known_fps": len(known_fps),
        "correctly_killed": len(correctly_killed),
        "leaked_fps": leaked_fps,
        "known_real": len(known_real),
        "not_killed": len(not_killed),
        "false_negatives": false_negatives,
    }


def _print_results(results: list[dict], quiet: bool) -> None:
    if not quiet:
        print("\n=== Per-case results ===")
        for r in results:
            status = "PASS" if r["correct"] else "FAIL"
            print(
                f"  [{status}] {r['case_id']:25s} "
                f"expected={r['expected_verdict']:14s} "
                f"got={r['got_verdict']:14s} "
                f"cat={r['got_category']}"
            )
            if not r["correct"]:
                print(f"         file: {r['file_path']}")
                print(f"         note: {r['note']}")
                print(f"         reason: {r['reason'][:120]}")


def _print_metrics(metrics: dict, mode: str) -> None:
    print(f"\n=== AuditAgent Verify-Layer Eval ({mode} mode) ===")
    print(f"  Total cases       : {metrics['total']}")
    print(f"  Correct           : {metrics['correct']} / {metrics['total']}  ({metrics['accuracy']:.0%})")
    print()
    print(f"  FP-kill rate      : {metrics['fp_kill_rate']:.1%}  "
          f"({metrics['correctly_killed']}/{metrics['known_fps']} known-FPs killed)")
    print(f"  Recall preserved  : {metrics['recall_preserved']:.1%}  "
          f"({metrics['not_killed']}/{metrics['known_real']} real findings kept)")
    print()

    if metrics["leaked_fps"]:
        print(f"  LEAKED FPs (known-FP, not killed) [{len(metrics['leaked_fps'])}]:")
        for r in metrics["leaked_fps"]:
            print(f"    - {r['case_id']:25s} got={r['got_verdict']}  file={r['file_path']}")
            print(f"      reason: {r['reason'][:100]}")
    else:
        print("  Leaked FPs: none")

    if metrics["false_negatives"]:
        print(f"\n  FALSE NEGATIVES (real finding killed as FP) [{len(metrics['false_negatives'])}]:")
        for r in metrics["false_negatives"]:
            print(f"    *** {r['case_id']:25s} got=false_positive  file={r['file_path']}")
            print(f"      note: {r['note']}")
    else:
        print("  False negatives (real→FP): none")

    # Pass/fail gates
    fp_kill_ok = metrics["fp_kill_rate"] >= 0.80
    recall_ok  = metrics["recall_preserved"] >= 0.90

    print()
    print(f"  Gate FP-kill ≥ 80%       : {'PASS' if fp_kill_ok else 'FAIL'}  ({metrics['fp_kill_rate']:.1%})")
    print(f"  Gate recall-preserved ≥ 90%: {'PASS' if recall_ok else 'FAIL'}  ({metrics['recall_preserved']:.1%})")

    if fp_kill_ok and recall_ok:
        print("\n  OVERALL: PASS — moat is working")
    else:
        print("\n  OVERALL: FAIL — see gates above")


async def _main(args: argparse.Namespace) -> int:
    cases = _load_cases()
    if not cases:
        print(f"ERROR: No cases found at {_CASES_PATH}", file=sys.stderr)
        return 1

    print(f"Loaded {len(cases)} eval cases from {_CASES_PATH.relative_to(_ROOT)}")

    if args.llm:
        print("Mode: LLM (full verify_findings pipeline) — this will make LLM calls")
        try:
            results = await _llm_run(cases)
            mode = "llm"
        except Exception as exc:
            print(f"LLM run failed: {exc}", file=sys.stderr)
            print("Falling back to deterministic mode...")
            results = _deterministic_run(cases)
            mode = "deterministic (llm-fallback)"
    else:
        print("Mode: deterministic only (classify_context + _deterministic_triage)")
        results = _deterministic_run(cases)
        mode = "deterministic"

    _print_results(results, args.quiet)
    metrics = _compute_metrics(results)
    _print_metrics(metrics, mode)

    # Exit code: 0 = pass, 1 = fail (for CI gate)
    fp_kill_ok = metrics["fp_kill_rate"] >= 0.80
    recall_ok  = metrics["recall_preserved"] >= 0.90
    return 0 if (fp_kill_ok and recall_ok) else 1


def main() -> None:
    parser = argparse.ArgumentParser(description="AuditAgent verify-layer eval harness")
    parser.add_argument(
        "--llm", action="store_true",
        help="Run full LLM verify pipeline (requires daemon). Default: deterministic only.",
    )
    parser.add_argument(
        "--quiet", "-q", action="store_true",
        help="Suppress per-case output, show only metrics",
    )
    args = parser.parse_args()
    sys.exit(asyncio.run(_main(args)))


if __name__ == "__main__":
    main()
