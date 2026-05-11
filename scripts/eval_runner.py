#!/usr/bin/env python3
"""
Jarvis Phase 5 — Agent Eval Runner
====================================
Runs regression tests against Jarvis agent prompts.

Usage:
  .venv/bin/python scripts/eval_runner.py <agent-slug>     # one agent
  .venv/bin/python scripts/eval_runner.py --all            # all agents (use sparingly)
  .venv/bin/python scripts/eval_runner.py --regression     # compare vs last run

MODE NOTES
----------
This runner operates in one of two modes depending on environment:

1. DESIGN-MODE (default):
   Generates evaluator-ready prompt packages that Boss pastes into a Claude Code
   session manually. No API calls made. Safe, always works.

2. HEADLESS-MODE (experimental):
   Attempts to call `claude -p` (Claude Code headless) with the agent system prompt
   + test input. Requires Claude Code to be authenticated. May not work in all
   environments — see eval_runner README for details.

Set EVAL_MODE=headless in environment to attempt headless mode.
"""

import argparse
import json
import os
import sys
import textwrap
from datetime import date, datetime
from pathlib import Path
from typing import Optional

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML not installed. Run: .venv/bin/pip install pyyaml")
    sys.exit(1)

# ── Paths ──────────────────────────────────────────────────────────────────────
JARVIS_ROOT = Path(__file__).parent.parent
EVALS_DIR = JARVIS_ROOT / "data" / "evals"
AGENTS_DIR = JARVIS_ROOT / "data" / "agent-prompts-final"
BRIDGE_ENV = JARVIS_ROOT / "bridge" / ".env"

TODAY = date.today().isoformat()
NOW = datetime.now().strftime("%Y-%m-%d %H:%M")

# ── Telegram notify ────────────────────────────────────────────────────────────

def load_bridge_env() -> dict:
    """Load bridge .env for Telegram credentials."""
    env = {}
    if BRIDGE_ENV.exists():
        for line in BRIDGE_ENV.read_text().splitlines():
            line = line.strip()
            if line and "=" in line and not line.startswith("#"):
                k, _, v = line.partition("=")
                env[k.strip()] = v.strip()
    return env


def send_telegram(message: str) -> bool:
    """Send a Telegram notification via the bridge bot. Returns True if sent."""
    try:
        import requests
    except ImportError:
        print("  [telegram] requests not installed — skipping notification")
        return False

    env = load_bridge_env()
    token = env.get("TELEGRAM_BOT_TOKEN")
    user_ids = env.get("ALLOWED_USER_IDS", "")
    if not token or not user_ids:
        print("  [telegram] credentials not found in bridge/.env — skipping")
        return False

    chat_id = user_ids.split(",")[0].strip()
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        resp = requests.post(url, json={"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}, timeout=10)
        if resp.ok:
            print(f"  [telegram] notification sent to {chat_id}")
            return True
        else:
            print(f"  [telegram] send failed: {resp.status_code} {resp.text[:100]}")
    except Exception as e:
        print(f"  [telegram] error: {e}")
    return False


# ── Test case loader ────────────────────────────────────────────────────────────

def load_test_cases(agent_slug: str) -> Optional[dict]:
    """Load test-cases.yaml for an agent. Returns None if not found."""
    tc_path = EVALS_DIR / agent_slug / "test-cases.yaml"
    if not tc_path.exists():
        print(f"  [skip] No test-cases.yaml found at {tc_path}")
        return None
    with open(tc_path) as f:
        return yaml.safe_load(f)


def list_agents_with_tests() -> list[str]:
    """Return all agent slugs that have a test-cases.yaml."""
    agents = []
    for p in sorted(EVALS_DIR.iterdir()):
        if p.is_dir() and (p / "test-cases.yaml").exists():
            agents.append(p.name)
    return agents


# ── Agent prompt loader ─────────────────────────────────────────────────────────

def load_agent_prompt(agent_slug: str, agent_file: Optional[str] = None) -> Optional[str]:
    """
    Extract the deployable prompt from an agent .md file.
    Looks for the block between ```  ``` markers under 'THE PROMPT' section.
    Falls back to returning the full file content if no code block found.
    """
    if agent_file:
        path = JARVIS_ROOT / agent_file
    else:
        path = AGENTS_DIR / f"{agent_slug}.md"

    if not path.exists():
        print(f"  [warn] Agent file not found: {path}")
        return None

    content = path.read_text()

    # Try to extract the verbatim prompt between the first ``` block after "THE PROMPT"
    in_prompt_section = False
    in_code_block = False
    prompt_lines = []

    for line in content.splitlines():
        if "THE PROMPT" in line or "## THE PROMPT" in line:
            in_prompt_section = True
            continue
        if in_prompt_section:
            if line.strip().startswith("```") and not in_code_block:
                in_code_block = True
                continue
            elif in_code_block and line.strip() == "```":
                break  # end of prompt block
            elif in_code_block:
                prompt_lines.append(line)

    if prompt_lines:
        return "\n".join(prompt_lines)

    # Fallback: return full file
    return content


# ── Design-mode: generate evaluator prompt package ────────────────────────────

def generate_evaluator_package(agent_slug: str, tc: dict, system_prompt: Optional[str]) -> str:
    """
    Generate a self-contained evaluator package that Boss can paste into Claude
    to manually score a test case.
    """
    dims = tc.get("rubric_dimensions", [])
    dim_table = "\n".join(
        f"  - {d['name']} (min: {d.get('min_score', 4)}/5): {d.get('description', '')}"
        for d in dims
    )
    expected = "\n".join(f"  - {q}" for q in tc.get("expected_qualities", []))

    agent_prompt_block = ""
    if system_prompt:
        truncated = system_prompt[:3000] + "\n[...truncated for brevity]" if len(system_prompt) > 3000 else system_prompt
        agent_prompt_block = f"""
## Agent System Prompt (paste as system prompt when testing)

```
{truncated}
```
"""

    return f"""# Eval Package — {agent_slug} / {tc['id']}

**Test:** {tc.get('name', tc['id'])}
**Date:** {NOW}
**Mode:** DESIGN-MODE (manual eval — paste into Claude Code session)

## Step 1: Set Up the Session

Open a new Claude Code session and paste the Agent System Prompt below as the
system prompt (or use `--system-prompt` flag with `claude -p`).
{agent_prompt_block}

## Step 2: Send This Input

```
{tc.get('input', '').strip()}
```

## Step 3: Score the Response

For each dimension, score 1-5 using this scale:
  5 = Excellent (matches description fully)
  4 = Acceptable (minor gaps)
  3 = Borderline (partial)
  1-2 = Reject (dimension failed)

**Rubric Dimensions:**
{dim_table}

**Expected Qualities (checklist — check each that is present in the response):**
{expected}

**Minimum score per dimension:** {tc.get('min_score_per_dim', 4)}/5

## Step 4: Record Scores

Paste your scores into the report section in:
  data/evals/{agent_slug}/reports/{TODAY}.md

---
*Generated by eval_runner.py (design-mode) — {NOW}*
"""


# ── Headless mode: attempt claude -p ─────────────────────────────────────────

def run_headless(agent_slug: str, tc: dict, system_prompt: Optional[str]) -> dict:
    """
    Attempt to run the agent via `claude -p` in headless mode.
    Returns a result dict with 'output' and 'error' keys.

    LIMITATIONS (documented):
    - Requires Claude Code to be authenticated (subscription, not API key)
    - claude -p spawns a new Claude Code session — may be blocked in certain
      automated environments (auto-mode classifier blocks nested claude invocations
      with --dangerously-skip-permissions)
    - No way to programmatically extract structured rubric scores from the output
      without a second LLM-as-judge pass (which itself needs API access)
    - Recommended: use design-mode and score manually, or get an Anthropic API key
      for true automated LLM-as-judge scoring.
    """
    import subprocess

    if not system_prompt:
        return {"output": None, "error": "No system prompt available — cannot run headless"}

    input_text = tc.get("input", "").strip()
    cmd = [
        "claude",
        "-p",
        "--no-session-persistence",
        "--system-prompt", system_prompt,
        input_text,
    ]

    print(f"  [headless] Running: claude -p --no-session-persistence ...")
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
            cwd=str(JARVIS_ROOT),
        )
        if result.returncode != 0:
            return {
                "output": result.stdout,
                "error": f"claude exited {result.returncode}: {result.stderr[:300]}",
            }
        return {"output": result.stdout, "error": None}
    except subprocess.TimeoutExpired:
        return {"output": None, "error": "Timed out after 120s"}
    except FileNotFoundError:
        return {"output": None, "error": "claude binary not found in PATH"}
    except Exception as e:
        return {"output": None, "error": str(e)}


# ── Report writer ──────────────────────────────────────────────────────────────

def write_report(agent_slug: str, results: list[dict], mode: str) -> Path:
    """Write an eval report to data/evals/{agent}/reports/{TODAY}.md"""
    report_dir = EVALS_DIR / agent_slug / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / f"{TODAY}.md"

    lines = [
        f"# Eval Report — {agent_slug}",
        f"**Date:** {NOW}  ",
        f"**Mode:** {mode}  ",
        f"**Runner:** eval_runner.py  ",
        "",
        "---",
        "",
        "## Results",
        "",
    ]

    passed = 0
    failed = 0
    needs_manual = 0

    for r in results:
        tc_id = r.get("tc_id", "unknown")
        tc_name = r.get("tc_name", "")
        status = r.get("status", "PENDING_MANUAL")

        icon = {"PASS": "PASS", "FAIL": "FAIL", "PENDING_MANUAL": "PENDING", "ERROR": "ERROR"}.get(status, status)
        lines.append(f"### {tc_id}: {tc_name}")
        lines.append(f"**Status:** {icon}  ")

        if status == "PASS":
            passed += 1
        elif status == "FAIL":
            failed += 1
        else:
            needs_manual += 1

        if r.get("error"):
            lines.append(f"**Error:** {r['error']}  ")
        if r.get("output"):
            truncated = r["output"][:2000] + "\n[...truncated]" if len(r["output"]) > 2000 else r["output"]
            lines.append("")
            lines.append("**Agent Output (first 2000 chars):**")
            lines.append("```")
            lines.append(truncated)
            lines.append("```")
        if r.get("eval_package_path"):
            lines.append(f"**Evaluator Package:** `{r['eval_package_path']}`  ")
        if r.get("scores"):
            lines.append("")
            lines.append("**Scores:**")
            for dim, score in r["scores"].items():
                min_s = r.get("min_scores", {}).get(dim, 4)
                flag = "" if score >= min_s else " BELOW MIN"
                lines.append(f"  - {dim}: {score}/5{flag}")
        lines.append("")

    lines += [
        "---",
        "",
        "## Summary",
        "",
        f"- Total test cases: {len(results)}",
        f"- Passed: {passed}",
        f"- Failed: {failed}",
        f"- Pending manual review: {needs_manual}",
        "",
    ]

    if mode == "design-mode":
        lines += [
            "## Next Steps (Design Mode)",
            "",
            "1. Open each evaluator package listed above",
            "2. Paste the system prompt into a new Claude Code session",
            "3. Send the test input",
            "4. Score response against rubric dimensions",
            "5. Edit this file to replace PENDING_MANUAL with PASS/FAIL + actual scores",
            "",
        ]

    report_path.write_text("\n".join(lines))
    return report_path


def write_summary_report(all_results: dict[str, list[dict]], mode: str) -> Path:
    """Write cross-agent summary to data/evals/reports/summary-{TODAY}.md"""
    summary_path = EVALS_DIR / "reports" / f"summary-{TODAY}.md"
    lines = [
        f"# Jarvis Eval Summary — {TODAY}",
        f"**Run at:** {NOW}  ",
        f"**Mode:** {mode}  ",
        "",
        "| Agent | Total | Pass | Fail | Pending |",
        "|-------|-------|------|------|---------|",
    ]

    total_pass = total_fail = total_pending = 0
    for agent, results in sorted(all_results.items()):
        p = sum(1 for r in results if r.get("status") == "PASS")
        f = sum(1 for r in results if r.get("status") == "FAIL")
        n = sum(1 for r in results if r.get("status") not in ("PASS", "FAIL"))
        lines.append(f"| {agent} | {len(results)} | {p} | {f} | {n} |")
        total_pass += p
        total_fail += f
        total_pending += n

    total = sum(len(r) for r in all_results.values())
    lines.append(f"| **TOTAL** | {total} | {total_pass} | {total_fail} | {total_pending} |")
    lines += ["", "---", "", "## Individual Reports", ""]
    for agent in sorted(all_results.keys()):
        lines.append(f"- `data/evals/{agent}/reports/{TODAY}.md`")

    summary_path.write_text("\n".join(lines))
    return summary_path


# ── Regression check ───────────────────────────────────────────────────────────

def find_last_report(agent_slug: str) -> Optional[Path]:
    """Find the most recent report for an agent (excluding today)."""
    report_dir = EVALS_DIR / agent_slug / "reports"
    if not report_dir.exists():
        return None
    reports = sorted(report_dir.glob("*.md"), reverse=True)
    for r in reports:
        if r.stem != TODAY:
            return r
    return None


def check_regression(agent_slug: str, current_results: list[dict]) -> Optional[str]:
    """
    Compare current results against last run.
    Returns a regression alert message if there's a regression, else None.
    """
    last = find_last_report(agent_slug)
    if not last:
        return None  # No baseline to compare

    current_pass = sum(1 for r in current_results if r.get("status") == "PASS")
    current_fail = sum(1 for r in current_results if r.get("status") == "FAIL")

    # Simple heuristic: read last report for pass/fail counts
    last_content = last.read_text()
    last_pass = 0
    last_fail = 0
    for line in last_content.splitlines():
        if line.startswith("- Passed:"):
            try:
                last_pass = int(line.split(":")[1].strip())
            except ValueError:
                pass
        if line.startswith("- Failed:"):
            try:
                last_fail = int(line.split(":")[1].strip())
            except ValueError:
                pass

    if current_fail > last_fail:
        return (
            f"REGRESSION: {agent_slug}\n"
            f"Last run ({last.stem}): {last_pass} pass / {last_fail} fail\n"
            f"Today ({TODAY}): {current_pass} pass / {current_fail} fail\n"
            f"New failures: {current_fail - last_fail}"
        )
    return None


# ── Core runner ────────────────────────────────────────────────────────────────

def run_agent(agent_slug: str, mode: str, packages_dir: Path) -> tuple[list[dict], Optional[str]]:
    """
    Run all test cases for an agent. Returns (results_list, regression_alert).
    """
    print(f"\n=== Running eval: {agent_slug} ===")

    data = load_test_cases(agent_slug)
    if not data:
        return [], None

    agent_file = data.get("agent_file")
    system_prompt = load_agent_prompt(agent_slug, agent_file)
    if system_prompt:
        print(f"  [ok] Loaded agent prompt ({len(system_prompt)} chars)")
    else:
        print(f"  [warn] Could not load agent prompt")

    test_cases = data.get("test_cases", [])
    print(f"  [ok] {len(test_cases)} test case(s) found")

    results = []

    for tc in test_cases:
        tc_id = tc.get("id", "unknown")
        tc_name = tc.get("name", tc_id)
        print(f"  → {tc_id}: {tc_name}")

        result = {
            "tc_id": tc_id,
            "tc_name": tc_name,
            "status": "PENDING_MANUAL",
            "output": None,
            "error": None,
            "scores": {},
            "min_scores": {},
        }

        if mode == "headless":
            headless_result = run_headless(agent_slug, tc, system_prompt)
            result["output"] = headless_result.get("output")
            result["error"] = headless_result.get("error")
            if result["error"]:
                result["status"] = "ERROR"
                print(f"    [error] {result['error']}")
            else:
                # Without API-based LLM judge, we can't auto-score — mark as pending
                result["status"] = "PENDING_MANUAL"
                print(f"    [headless] Output captured ({len(result['output'] or '')} chars) — manual scoring needed")
        else:
            # Design mode: generate evaluator package
            package = generate_evaluator_package(agent_slug, tc, system_prompt)
            pkg_path = packages_dir / f"{agent_slug}_{tc_id}_eval.md"
            pkg_path.write_text(package)
            result["eval_package_path"] = str(pkg_path.relative_to(JARVIS_ROOT))
            result["status"] = "PENDING_MANUAL"
            print(f"    [design-mode] Evaluator package written: {pkg_path.name}")

        # Populate min_scores from rubric
        for dim in tc.get("rubric_dimensions", []):
            dim_name = dim.get("name", "")
            result["min_scores"][dim_name] = dim.get("min_score", tc.get("min_score_per_dim", 4))

        results.append(result)

    # Write per-agent report
    report_path = write_report(agent_slug, results, mode)
    print(f"  [ok] Report: {report_path.relative_to(JARVIS_ROOT)}")

    # Regression check
    regression_alert = check_regression(agent_slug, results)
    if regression_alert:
        print(f"  [REGRESSION] {regression_alert}")

    return results, regression_alert


# ── CLI entrypoint ─────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Jarvis Phase 5 — Eval Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""
            Examples:
              .venv/bin/python scripts/eval_runner.py code-reviewer
              .venv/bin/python scripts/eval_runner.py research-analyst
              .venv/bin/python scripts/eval_runner.py --all
              .venv/bin/python scripts/eval_runner.py --regression
              EVAL_MODE=headless .venv/bin/python scripts/eval_runner.py code-reviewer
        """),
    )
    parser.add_argument("agent", nargs="?", help="Agent slug to evaluate (e.g. code-reviewer)")
    parser.add_argument("--all", action="store_true", help="Run all agents with test cases")
    parser.add_argument("--regression", action="store_true", help="Compare today vs last run for all agents")
    parser.add_argument("--notify", action="store_true", help="Send Telegram notification on regressions")
    args = parser.parse_args()

    mode = os.environ.get("EVAL_MODE", "design").lower()
    if mode not in ("design", "design-mode", "headless", "headless-mode"):
        print(f"Unknown EVAL_MODE={mode!r}. Use 'design' or 'headless'.")
        sys.exit(1)
    mode = "headless" if "headless" in mode else "design-mode"

    print(f"Jarvis Eval Runner — {NOW}")
    print(f"Mode: {mode}")
    print(f"Evals dir: {EVALS_DIR}")

    # Packages dir for design-mode outputs
    packages_dir = EVALS_DIR / "_packages" / TODAY
    packages_dir.mkdir(parents=True, exist_ok=True)

    if args.regression:
        agents = list_agents_with_tests()
        print(f"\nRegression check across {len(agents)} agent(s)...")
        all_alerts = []
        for slug in agents:
            data = load_test_cases(slug)
            if not data:
                continue
            last = find_last_report(slug)
            if not last:
                print(f"  {slug}: no baseline report — skipping")
                continue
            print(f"  {slug}: baseline is {last.stem}")
            # Can't re-run in regression mode without re-running — just check existing
            alert = f"Regression check for {slug}: baseline at {last.stem}. Run eval to get today's results."
            all_alerts.append(alert)
            print(f"    {alert}")
        if not all_alerts:
            print("No baselines found. Run evals first to establish a baseline.")
        return

    if args.all:
        agents = list_agents_with_tests()
        print(f"\nRunning {len(agents)} agent(s): {', '.join(agents)}")
    elif args.agent:
        agents = [args.agent]
    else:
        parser.print_help()
        sys.exit(1)

    all_results: dict[str, list[dict]] = {}
    all_regression_alerts: list[str] = []

    for slug in agents:
        results, regression_alert = run_agent(slug, mode, packages_dir)
        all_results[slug] = results
        if regression_alert:
            all_regression_alerts.append(regression_alert)

    # Write summary if multiple agents
    if len(agents) > 1:
        summary_path = write_summary_report(all_results, mode)
        print(f"\n[ok] Summary report: {summary_path.relative_to(JARVIS_ROOT)}")

    # Telegram notifications
    if all_regression_alerts and (args.notify or os.environ.get("EVAL_NOTIFY")):
        alert_text = f"*Jarvis Eval Regression Alert* ({TODAY})\n\n" + "\n\n".join(all_regression_alerts)
        send_telegram(alert_text)
    elif all_regression_alerts:
        print(f"\n[regressions] {len(all_regression_alerts)} regression(s) detected. Run with --notify to send Telegram alert.")

    # Final summary
    total = sum(len(r) for r in all_results.values())
    pending = sum(1 for rl in all_results.values() for r in rl if r.get("status") == "PENDING_MANUAL")
    errors = sum(1 for rl in all_results.values() for r in rl if r.get("status") == "ERROR")

    print(f"\n=== Done ===")
    print(f"  Total test cases: {total}")
    print(f"  Pending manual review: {pending}")
    print(f"  Errors: {errors}")
    if mode == "design-mode":
        print(f"  Evaluator packages: {packages_dir.relative_to(JARVIS_ROOT)}/")
        print(f"\n  Next: open each *_eval.md package, follow the instructions to score manually.")


if __name__ == "__main__":
    main()
