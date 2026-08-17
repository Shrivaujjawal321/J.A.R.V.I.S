#!/usr/bin/env python3
"""
AuditAgent CLI — find security bugs in any local project folder.

Usage:
    .venv/bin/python scripts/audit.py <path-to-project>
    .venv/bin/python scripts/audit.py <path> --scanners semgrep,gitleaks
    .venv/bin/python scripts/audit.py <path> --budget 0.50   # enable LLM verify

What it does (defensive, read-only):
    SCOPE_GATE → RECON → SCAN (semgrep/osv/gitleaks/trufflehog/trivy in parallel)
    → ANALYZE (dedupe) → VERIFY (FP-kill) → REPORT.

Output:
    - Findings table printed to terminal (ranked by CVSS)
    - Full Markdown + JSON report saved to data/outputs/audits/<audit_id>/

This runs standalone — the jarvis-core daemon does NOT need to be running.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path

# Make scanners on ~/.local/bin and the venv visible to subprocess adapters.
_HOME_BIN = os.path.expanduser("~/.local/bin")
_VENV_BIN = str(Path(__file__).resolve().parent.parent / ".venv" / "bin")
os.environ["PATH"] = f"{_HOME_BIN}:{_VENV_BIN}:" + os.environ.get("PATH", "")

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from jarvis_core.audit_agent.models import (  # noqa: E402
    AuditRun,
    ScopePolicy,
    Target,
    TERMINAL_STATES,
)
from jarvis_core.audit_agent.state_machine import advance  # noqa: E402

_SEV_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
_SEV_COLOR = {
    "critical": "\033[1;31m",  # bold red
    "high": "\033[31m",        # red
    "medium": "\033[33m",      # yellow
    "low": "\033[36m",         # cyan
    "info": "\033[2m",         # dim
}
_RESET = "\033[0m"


class StandaloneState:
    """Minimal JarvisState stand-in so the FSM can run without the daemon.

    Provides exactly the surface advance() touches: _lock, _audits,
    add_approval, get_approval, sync_to_disk.
    """

    def __init__(self) -> None:
        self._lock = asyncio.Lock()
        self._audits: dict = {}
        self._approvals: dict = {}

    async def add_approval(self, approval) -> None:
        self._approvals[approval.approval_id] = approval

    async def get_approval(self, approval_id):
        return self._approvals.get(approval_id)

    async def sync_to_disk(self) -> None:
        pass  # CLI keeps state in memory; report is the durable artifact


async def run_audit(args) -> int:
    target_path = os.path.abspath(args.path)
    if not os.path.isdir(target_path):
        print(f"✗ Not a directory: {target_path}", file=sys.stderr)
        return 2

    scanners = (
        [s.strip() for s in args.scanners.split(",") if s.strip()]
        if args.scanners
        else ["semgrep", "trivy", "osv", "gitleaks", "trufflehog"]
    )

    target = Target(kind="local_dir", uri=target_path)
    policy = ScopePolicy(
        target=target,
        allowed_scanners=scanners,
        max_budget_usd=args.budget,
    )
    run = AuditRun(user_id="cli", scope_policy=policy)
    state = StandaloneState()

    print(f"\n🔍 Auditing: {target_path}")
    print(f"   Scanners: {', '.join(scanners)}")
    print(f"   LLM verify budget: ${args.budget:.2f}"
          + ("  (deterministic-only)" if args.budget <= 0 else "") + "\n")

    steps = 0
    while run.audit_state not in TERMINAL_STATES and steps < 15:
        prev = run.audit_state
        run = await advance(run, state)
        if run.audit_state != prev:
            print(f"   • {prev.value} → {run.audit_state.value}")
        steps += 1

    if run.audit_state.value != "done":
        print(f"\n✗ Audit ended in {run.audit_state.value}: {run.error or '(no detail)'}")
        return 1

    # ── Summary ───────────────────────────────────────────────────────────
    def _is_fp(f) -> bool:
        return getattr(f.verification_status, "value", f.verification_status) == "false_positive"

    actionable = [f for f in run.findings if not _is_fp(f)]
    fp_count = len(run.findings) - len(actionable)

    by_sev: dict[str, int] = {}
    for f in actionable:
        by_sev[f.severity.value] = by_sev.get(f.severity.value, 0) + 1

    # Which scanners actually ran vs skipped
    print("\n── Scanners ─────────────────────────────")
    for r in run.raw_results:
        status = r.error or f"exit={r.exit_code}"
        mark = "⚠ " if r.error else "✓ "
        print(f"   {mark}{r.scanner:11} {status}")

    if fp_count:
        print(f"\n🛡  Verify layer (moat) auto-filtered {fp_count} false-positive(s) "
              f"of {len(run.findings)} raw findings.")

    print(f"\n── {len(actionable)} actionable findings ──────────────────────")
    for sev in ("critical", "high", "medium", "low", "info"):
        if by_sev.get(sev):
            c = _SEV_COLOR[sev]
            print(f"   {c}{sev.upper():9}{_RESET} {by_sev[sev]}")

    # ── Top findings (actionable only — FPs already filtered) ─────────────
    ranked = sorted(
        actionable,
        key=lambda f: (_SEV_ORDER.get(f.severity.value, 9), -(f.cvss_score or 0)),
    )
    print("\n── Top findings ─────────────────────────")
    for f in ranked[: args.top]:
        c = _SEV_COLOR.get(f.severity.value, "")
        loc = f"{f.file_path}:{f.line_start}" if f.file_path else (f.endpoint or "-")
        cvss = f"CVSS {f.cvss_score:.1f}" if f.cvss_score else "CVSS  - "
        vstatus = getattr(f.verification_status, "value", f.verification_status)
        tag = "✓conf" if vstatus == "confirmed" else "?man" if vstatus == "needs_manual" else ""
        print(f"   {c}[{f.severity.value.upper():8}]{_RESET} {cvss}  {tag:6} {f.scanner:10} {loc}")
        ev = (f.evidence or "").replace("\n", " ").strip()
        if ev:
            print(f"              {ev[:88]}")
    if not ranked:
        print("   (no actionable findings — all raw hits were false positives)")

    # ── Save report ───────────────────────────────────────────────────────
    out_dir = Path("data/outputs/audits") / run.audit_id
    out_dir.mkdir(parents=True, exist_ok=True)
    if run.report:
        (out_dir / "report.md").write_text(run.report.markdown_body)
    (out_dir / "findings.json").write_text(
        json.dumps([f.model_dump(mode="json") for f in run.findings], indent=2)
    )
    print(f"\n📄 Report:  {out_dir / 'report.md'}")
    print(f"📦 JSON:    {out_dir / 'findings.json'}")
    print(f"   Audit ID: {run.audit_id}\n")

    # ── Submission-ready reports (--reports flag) ─────────────────────────
    if args.reports:
        from jarvis_core.audit_agent.reporting import write_reports  # noqa: E402
        report_paths = await write_reports(
            findings=run.findings,
            run=run,
            out_dir=out_dir,
            enrich=False,
        )
        n_reports = sum(1 for p in report_paths if p.name != "index.md")
        if n_reports:
            print(f"📋 Bug reports ({n_reports} HIGH+CRIT findings):")
            for p in report_paths:
                print(f"   {p}")
        else:
            print("   (No HIGH/CRITICAL non-FP findings — no submission reports generated)")
        print()

    return 0


def main() -> int:
    p = argparse.ArgumentParser(
        description="Find security bugs in a local project folder (defensive SAST/SCA/secrets audit).",
    )
    p.add_argument("path", help="Path to the project folder to audit")
    p.add_argument(
        "--scanners",
        default="",
        help="Comma-separated subset (default: all). e.g. semgrep,gitleaks,osv",
    )
    p.add_argument(
        "--budget",
        type=float,
        default=0.0,
        help="USD budget for LLM verify pass (0 = deterministic only). e.g. 0.50",
    )
    p.add_argument("--top", type=int, default=15, help="How many top findings to print")
    p.add_argument(
        "--reports",
        action="store_true",
        default=False,
        help="After audit, emit one submission-ready Markdown bug report per HIGH/CRITICAL "
             "finding into <out_dir>/reports/. Without this flag, behavior is unchanged.",
    )
    args = p.parse_args()
    try:
        return asyncio.run(run_audit(args))
    except KeyboardInterrupt:
        print("\n✗ Interrupted")
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
