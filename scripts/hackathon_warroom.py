#!/usr/bin/env python3
"""
hackathon_warroom.py — Jarvis Hackathon War Room workflow runner.

Implements the 5-phase state machine defined in `specs/hackathon-war-room.spec.md`.
Each phase runs agents (via jarvis_core.orchestrator) in parallel where possible,
merges outputs into a consolidated report, then PAUSES at a checkpoint waiting for
Boss's decision (via Telegram `/wr_checkpoint` or CLI `checkpoint` subcommand).

State is persisted to `data/hackathons/{slug}/canonical_state.json` after every
phase / agent output → resumable across daemon restarts.

CLI:
    python scripts/hackathon_warroom.py start    <slug> --input contract.json
    python scripts/hackathon_warroom.py status   <slug>
    python scripts/hackathon_warroom.py run      <slug>           # run current phase
    python scripts/hackathon_warroom.py checkpoint <slug> <approve|drill|skip>
    python scripts/hackathon_warroom.py pick     <slug> <id1,id2,...>
    python scripts/hackathon_warroom.py resume   <slug>           # alias for `run`
"""
from __future__ import annotations

import argparse
import asyncio
import json
import logging
import os
import re
import shutil
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

HACKATHONS_DIR = PROJECT_ROOT / "data" / "hackathons"
TEMPLATE_DIR = HACKATHONS_DIR / "_template"
RUN_LOG = PROJECT_ROOT / "data" / "logs" / "warroom.jsonl"

ROOT_ENV = PROJECT_ROOT / ".env"
BRIDGE_ENV = PROJECT_ROOT / "bridge" / ".env"

DEFAULT_MODEL = os.getenv("JARVIS_WARROOM_MODEL", "claude-sonnet-4-6")

logging.basicConfig(
    level=os.getenv("JARVIS_WARROOM_LOG_LEVEL", "INFO"),
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)
log = logging.getLogger("warroom")


# ── Required fields per spec §1 ──────────────────────────────────────────────

REQUIRED_FIELDS = [
    ("COMPANY", "name"),
    ("COMPANY", "url"),
    ("HACKATHON", "url"),
    ("HACKATHON", "problem_statements"),
    ("HACKATHON", "deadline"),
    ("HACKATHON", "team_size"),
    ("HACKATHON", "required_tech"),
    ("TEAM", "roles"),
    ("TEAM", "skill_levels"),
    ("TEAM", "time_budget_hours"),
    ("CONSTRAINTS", "budget"),
]

# ── Phase 1 agent roster ─────────────────────────────────────────────────────

PHASE_1_COMPANY_AGENTS = [
    "research-analyst-agent",
    "company-tech-stack-researcher-agent",
    "company-ai-ml-researcher-agent",
    "investigative-journalist-agent",
    "librarian-research-assistant-agent",
]
PHASE_1_HACKATHON_AGENTS = [
    "hackathon-intel-researcher-agent",
    "mandatory-tech-deep-dive-agent",
]


# ── Env loading (for Telegram digests) ───────────────────────────────────────


def _load_env_files() -> dict[str, str]:
    env: dict[str, str] = {}
    for path in (ROOT_ENV, BRIDGE_ENV):
        if not path.exists():
            continue
        for line in path.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            env[key.strip()] = value.strip().strip('"').strip("'")
    env.update(os.environ)
    return env


ENV = _load_env_files()


# ── State helpers ────────────────────────────────────────────────────────────


def _slug_dir(slug: str) -> Path:
    return HACKATHONS_DIR / slug


def _state_path(slug: str) -> Path:
    return _slug_dir(slug) / "canonical_state.json"


def _load_state(slug: str) -> dict:
    p = _state_path(slug)
    if not p.exists():
        raise FileNotFoundError(f"No state for {slug!r} — run `start` first")
    return json.loads(p.read_text())


def _save_state(slug: str, state: dict) -> None:
    state["updated_at"] = datetime.now(timezone.utc).isoformat()
    tmp = _state_path(slug).with_suffix(".tmp")
    tmp.write_text(json.dumps(state, indent=2, ensure_ascii=False))
    tmp.replace(_state_path(slug))


def _append_checkpoint_log(slug: str, entry: str) -> None:
    log_path = _slug_dir(slug) / "checkpoint_log.md"
    if not log_path.exists():
        log_path.write_text(f"# Checkpoint log — {slug}\n\n")
    with log_path.open("a") as fh:
        fh.write(f"\n## {datetime.now(timezone.utc).isoformat()}\n\n{entry}\n")


def _append_run_log(entry: dict) -> None:
    try:
        RUN_LOG.parent.mkdir(parents=True, exist_ok=True)
        with RUN_LOG.open("a") as fh:
            fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception:
        pass


# ── Input contract validation ────────────────────────────────────────────────


def _missing_fields(state: dict) -> list[str]:
    contract = state.get("input_contract", {})
    missing: list[str] = []
    for section, field in REQUIRED_FIELDS:
        v = (contract.get(section) or {}).get(field)
        if v in (None, "", []):
            missing.append(f"{section}.{field}")
    return missing


def _consolidated_question(missing: list[str]) -> str:
    return (
        "🚧 *Hackathon War Room — Input Contract incomplete*\n\n"
        "Please supply the following fields (one consolidated answer):\n\n"
        + "\n".join(f"  • `{m}`" for m in missing)
        + "\n\nReply by editing `canonical_state.json` directly, or by sending a JSON snippet via Telegram `/wr_input <slug>` (planned)."
    )


# ── Telegram send ────────────────────────────────────────────────────────────


def _send_telegram(text: str, chat_id: str | None = None) -> bool:
    token = ENV.get("TELEGRAM_BOT_TOKEN")
    chat_id = chat_id or ENV.get("TELEGRAM_CHAT_ID") or (
        ENV.get("ALLOWED_USER_IDS", "").split(",")[0].strip()
    )
    if not token or not chat_id:
        log.info("Telegram creds missing — printing to stdout instead")
        print(text)
        return False
    try:
        import requests
    except ImportError:
        log.warning("requests not installed")
        return False
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        r = requests.post(
            url,
            json={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"},
            timeout=15,
        )
        if r.status_code != 200:
            log.warning("Telegram send failed: %d %s", r.status_code, r.text[:200])
            return False
    except Exception as exc:
        log.warning("Telegram send error: %s", exc)
        return False
    return True


# ── Start / init ─────────────────────────────────────────────────────────────


def cmd_start(slug: str, input_path: str | None) -> int:
    """Initialize a new War Room folder from template, optionally load input contract."""
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", slug):
        log.error("invalid slug %r — use lowercase alphanumeric + hyphen", slug)
        return 1
    dest = _slug_dir(slug)
    if dest.exists():
        log.error("folder already exists: %s", dest)
        return 1
    if not TEMPLATE_DIR.exists():
        log.error("template missing: %s — run setup first", TEMPLATE_DIR)
        return 1

    shutil.copytree(TEMPLATE_DIR, dest)
    state = json.loads((dest / "canonical_state.json").read_text())
    state["slug"] = slug
    state["started_at"] = datetime.now(timezone.utc).isoformat()
    state["current_phase"] = 0

    # Optional: load input contract from a JSON file
    if input_path:
        contract_path = Path(input_path)
        if not contract_path.exists():
            log.warning("input file %s missing — proceeding with empty contract", input_path)
        else:
            try:
                user_contract = json.loads(contract_path.read_text())
                # Shallow-merge into the template's input_contract
                for section in ("COMPANY", "HACKATHON", "TEAM", "CONSTRAINTS"):
                    if section in user_contract:
                        state["input_contract"][section].update(user_contract[section])
                log.info("loaded input contract from %s", input_path)
            except json.JSONDecodeError as e:
                log.error("input file is not valid JSON: %s", e)
                return 1

    _save_state(slug, state)
    missing = _missing_fields(state)

    print(f"✓ War Room initialised at {dest.relative_to(PROJECT_ROOT)}")
    print(f"  current_phase: 0")
    if missing:
        print(f"  ⚠ {len(missing)} Input Contract field(s) missing — required before Phase 1:")
        for m in missing:
            print(f"    - {m}")
        print(f"\n  Fill them in canonical_state.json then run: `run {slug}`")
    else:
        print(f"  ✓ Input Contract complete — ready to run Phase 1 with: `run {slug}`")
    _append_checkpoint_log(slug, f"Initialised. Missing fields: {missing or '(none)'}")
    _append_run_log({
        "ts": datetime.now(timezone.utc).isoformat(),
        "slug": slug, "action": "start", "missing_fields": missing,
    })
    return 0


# ── Status ───────────────────────────────────────────────────────────────────


def cmd_status(slug: str) -> int:
    state = _load_state(slug)
    missing = _missing_fields(state)
    print(f"slug:               {state['slug']}")
    print(f"started_at:         {state.get('started_at')}")
    print(f"updated_at:         {state.get('updated_at')}")
    print(f"current_phase:      {state.get('current_phase')}")
    print(f"current_checkpoint: {state.get('current_checkpoint')}")
    print(f"input_contract:     {'COMPLETE' if not missing else f'MISSING {len(missing)} fields'}")
    if missing:
        for m in missing:
            print(f"  - {m}")
    completed_phases = list(state.get("phase_outputs", {}).keys())
    print(f"completed_phases:   {completed_phases}")
    shortlisted = state.get("shortlisted_problem_ids", [])
    print(f"shortlisted:        {shortlisted}")
    print(f"selected:           {state.get('selected_problem_id')}")
    war_room_path = state.get("war_room_document_path")
    if war_room_path:
        print(f"WAR ROOM DOCUMENT:  {war_room_path}")
    return 0


# ── Phase runners ────────────────────────────────────────────────────────────


async def _build_phase_1_prompt(role: str, state: dict) -> str:
    contract = state["input_contract"]
    company = contract.get("COMPANY", {})
    hackathon = contract.get("HACKATHON", {})

    if role.startswith("company-") or role in (
        "research-analyst-agent", "investigative-journalist-agent",
        "librarian-research-assistant-agent",
    ):
        focus = (
            f"\nFocus area within company: {company.get('focus')}"
            if company.get('focus') else ""
        )
        return (
            f"You are operating in Jarvis Hackathon War Room — Phase 1.\n\n"
            f"COMPANY:\n"
            f"  name: {company.get('name')}\n"
            f"  url: {company.get('url')}{focus}\n\n"
            f"Produce your YAML output per the schema defined in your agent spec. "
            f"Verify every specific claim with a source URL or tag `[unverified]`. "
            f"Confidence < 0.6 → `[low-confidence]` tag. "
            f"Stay strictly within YOUR research surface — do not duplicate peers' work.\n\n"
            f"Output ONLY the YAML document. No markdown fences. No prose outside the schema."
        )
    # Hackathon agents
    return (
        f"You are operating in Jarvis Hackathon War Room — Phase 1.\n\n"
        f"HACKATHON:\n"
        f"  url: {hackathon.get('url')}\n"
        f"  problem_statements: {hackathon.get('problem_statements')}\n"
        f"  deadline: {hackathon.get('deadline')}\n"
        f"  team_size: {hackathon.get('team_size')}\n"
        f"  required_tech: {hackathon.get('required_tech')}\n"
        f"  judging_rubric: {hackathon.get('judging_rubric') or '(not published — infer)'}\n\n"
        f"Produce your YAML output per the schema defined in your agent spec. "
        f"Verify every specific claim with a source URL or tag `[unverified]`. "
        f"Confidence < 0.6 → `[low-confidence]` tag.\n\n"
        f"Output ONLY the YAML document. No markdown fences. No prose outside the schema."
    )


async def _run_agent_via_subagent(agent_name: str, prompt: str,
                                  timeout: int = 300) -> dict:
    """Dispatch an agent by name via run_worker — the spawned Claude Code worker
    will route to the named subagent (via Agent tool) when phrased appropriately.
    """
    from jarvis_core.orchestrator import run_worker

    # We tell the worker explicitly to delegate to the named agent
    delegation_prompt = (
        f"Use the Agent tool with subagent_type='{agent_name.replace('-agent', '')}' "
        f"to handle this task. Do NOT do the work yourself — delegate.\n\n"
        f"Task for the {agent_name}:\n\n{prompt}\n\n"
        f"Return ONLY the agent's YAML output verbatim."
    )
    try:
        outcome = await asyncio.wait_for(
            run_worker(
                delegation_prompt,
                project_root=PROJECT_ROOT,
                max_turns=8,
                timeout_seconds=timeout,
                model=DEFAULT_MODEL,
            ),
            timeout=timeout + 30,
        )
    except asyncio.TimeoutError:
        return {"agent_id": agent_name, "error": "timeout", "raw": ""}
    except Exception as exc:
        return {"agent_id": agent_name, "error": str(exc), "raw": ""}

    return {"agent_id": agent_name, "error": outcome.error,
            "raw": outcome.text or "", "duration_ms": outcome.duration_ms,
            "cost_usd": outcome.cost_usd}


async def cmd_run_phase_1(slug: str) -> int:
    state = _load_state(slug)
    missing = _missing_fields(state)
    if missing:
        msg = _consolidated_question(missing)
        _send_telegram(msg, state.get("telegram_chat_id"))
        log.error("Input Contract incomplete — halting per spec")
        return 2

    state["current_phase"] = 1
    state["current_checkpoint"] = None
    _save_state(slug, state)

    all_agents = PHASE_1_COMPANY_AGENTS + PHASE_1_HACKATHON_AGENTS
    log.info("Phase 1 — dispatching %d parallel research agents", len(all_agents))
    _send_telegram(
        f"🔬 *War Room {slug}* — Phase 1 starting "
        f"({len(all_agents)} agents in parallel). ETA 8-15 min.",
        state.get("telegram_chat_id"),
    )

    # Build prompts + dispatch all in parallel
    tasks = []
    for agent in all_agents:
        prompt = await _build_phase_1_prompt(agent, state)
        tasks.append(_run_agent_via_subagent(agent, prompt, timeout=600))

    started = time.perf_counter()
    results = await asyncio.gather(*tasks, return_exceptions=True)
    duration_s = int(time.perf_counter() - started)

    # Save raw outputs
    out_dir = _slug_dir(slug) / "agent_outputs"
    out_dir.mkdir(parents=True, exist_ok=True)

    ok_count = 0
    fail_count = 0
    for agent, result in zip(all_agents, results):
        if isinstance(result, Exception):
            log.warning("agent %s raised: %s", agent, result)
            (out_dir / f"1-{agent}.error.txt").write_text(repr(result))
            fail_count += 1
            continue
        if result.get("error"):
            log.warning("agent %s errored: %s", agent, result["error"])
            (out_dir / f"1-{agent}.error.txt").write_text(result["error"])
            fail_count += 1
            continue
        (out_dir / f"1-{agent}.yml").write_text(result["raw"])
        ok_count += 1

    # Build consolidated reports (markdown wrappers)
    company_report = out_dir.parent / "phase_1_research"
    company_report.mkdir(parents=True, exist_ok=True)
    company_md = company_report / "company_intelligence_report.md"
    hack_md = company_report / "hackathon_intelligence_report.md"

    company_md.write_text(_compose_company_report(slug, out_dir, state))
    hack_md.write_text(_compose_hackathon_report(slug, out_dir, state))

    # Update state
    state["phase_outputs"]["1"] = {
        "agents_dispatched": len(all_agents),
        "agents_ok": ok_count,
        "agents_failed": fail_count,
        "duration_s": duration_s,
        "company_report": str(company_md.relative_to(PROJECT_ROOT)),
        "hackathon_report": str(hack_md.relative_to(PROJECT_ROOT)),
        "completed_at": datetime.now(timezone.utc).isoformat(),
    }
    state["current_checkpoint"] = "1"
    _save_state(slug, state)

    _append_checkpoint_log(
        slug,
        f"**Phase 1 complete** — {ok_count}/{len(all_agents)} agents OK in {duration_s}s.\n"
        f"Reports: `{company_md.name}`, `{hack_md.name}`.\n"
        f"**CHECKPOINT 1** — awaiting Boss decision via "
        f"`/wr_checkpoint {slug} approve|drill|skip`.",
    )
    _send_telegram(
        f"🔬 *War Room {slug}* — Phase 1 done.\n"
        f"  • Agents OK: {ok_count}/{len(all_agents)}\n"
        f"  • Duration: {duration_s}s\n"
        f"  • Reports: `{company_md.relative_to(PROJECT_ROOT)}`, `{hack_md.relative_to(PROJECT_ROOT)}`\n\n"
        f"⚠️ CHECKPOINT 1\n"
        f"Reply: `/wr_checkpoint {slug} approve` to proceed to Phase 2,\n"
        f"or `/wr_checkpoint {slug} drill` to deepen Phase 1,\n"
        f"or `/wr_checkpoint {slug} skip` to skip directly to Phase 3 (advanced).",
        state.get("telegram_chat_id"),
    )
    _append_run_log({
        "ts": datetime.now(timezone.utc).isoformat(),
        "slug": slug, "phase": 1, "ok": ok_count, "fail": fail_count,
        "duration_s": duration_s,
    })
    return 0


def _compose_company_report(slug: str, out_dir: Path, state: dict) -> str:
    """Wrap the 5 company-agent YAML outputs into a single markdown document."""
    lines = [
        f"# Company Intelligence Report — {slug}",
        "",
        f"Compiled {datetime.now(timezone.utc).isoformat()}",
        "",
        "Each section below is one agent's raw YAML output, preserved verbatim. "
        "The Daemon does not paraphrase — Boss reads source of truth.",
        "",
    ]
    for agent in PHASE_1_COMPANY_AGENTS:
        section_title = agent.replace("-agent", "").replace("-", " ").title()
        yml_path = out_dir / f"1-{agent}.yml"
        err_path = out_dir / f"1-{agent}.error.txt"
        lines.append(f"## {section_title}")
        lines.append("")
        if yml_path.exists():
            lines.append("```yaml")
            lines.append(yml_path.read_text().strip())
            lines.append("```")
        elif err_path.exists():
            lines.append(f"_ERROR:_ `{err_path.read_text()[:200]}`")
        else:
            lines.append("_(no output)_")
        lines.append("")
    return "\n".join(lines)


def _compose_hackathon_report(slug: str, out_dir: Path, state: dict) -> str:
    lines = [
        f"# Hackathon Intelligence Report — {slug}",
        "",
        f"Compiled {datetime.now(timezone.utc).isoformat()}",
        "",
    ]
    for agent in PHASE_1_HACKATHON_AGENTS:
        section_title = agent.replace("-agent", "").replace("-", " ").title()
        yml_path = out_dir / f"1-{agent}.yml"
        err_path = out_dir / f"1-{agent}.error.txt"
        lines.append(f"## {section_title}")
        lines.append("")
        if yml_path.exists():
            lines.append("```yaml")
            lines.append(yml_path.read_text().strip())
            lines.append("```")
        elif err_path.exists():
            lines.append(f"_ERROR:_ `{err_path.read_text()[:200]}`")
        else:
            lines.append("_(no output)_")
        lines.append("")
    return "\n".join(lines)


# ── Phase 2 / 3 / 4 / 5 — stub implementations with same pattern ─────────────


async def cmd_run_phase_2(slug: str) -> int:
    state = _load_state(slug)
    # Phase 2 prerequisite: Phase 1 must be completed (its output exists)
    if "1" not in state.get("phase_outputs", {}):
        log.error("Phase 1 not yet completed — run Phase 1 first")
        return 2
    if state.get("current_checkpoint") not in (None, "approve_1"):
        log.error("Stuck at checkpoint %s — resolve first",
                  state.get("current_checkpoint"))
        return 2

    state["current_phase"] = 2
    state["current_checkpoint"] = None
    _save_state(slug, state)

    _send_telegram(
        f"🧩 *War Room {slug}* — Phase 2 starting "
        f"(problem discovery, 3 agents). ETA 5-10 min.",
        state.get("telegram_chat_id"),
    )

    company_md = (PROJECT_ROOT / state["phase_outputs"]["1"]["company_report"]).read_text()
    hack_md = (PROJECT_ROOT / state["phase_outputs"]["1"]["hackathon_report"]).read_text()

    prompt = (
        f"You are operating in Jarvis Hackathon War Room — Phase 2 (Problem Discovery).\n\n"
        f"INPUT — Phase 1 reports below.\n\n"
        f"---\n\n{company_md}\n\n---\n\n{hack_md}\n\n---\n\n"
        f"Use the Agent tool to delegate to these 3 subagents sequentially: "
        f"`product-manager`, `strategy-consultant`, `hackathon`. Collect their outputs.\n\n"
        f"Then synthesise: produce AT LEAST 10 candidate problems. For each, emit a "
        f"YAML block with these fields:\n"
        f"  - problem_id: kebab-case slug\n"
        f"  - problem_statement\n"
        f"  - target_user\n"
        f"  - pain_severity: 1-10 (anchored)\n"
        f"  - business_impact\n"
        f"  - ai_opportunity\n"
        f"  - data_availability: explicit (real / synthetic / hybrid / blocked)\n"
        f"  - competitive_differentiation\n"
        f"  - alignment_with_hackathon_theme: 0.0-1.0\n"
        f"  - alignment_with_company_pain_points: 0.0-1.0\n"
        f"  - scores: {{innovation, judge_appeal, feasibility, technical_depth, business_potential, composite}}\n"
        f"  - required_roles: [{{role, skill_level, est_hours}}]\n"
        f"  - top_risks: [...]\n\n"
        f"Rank by composite (default weights: 0.20/0.25/0.25/0.15/0.15). Output ONE markdown "
        f"document with the 10 ranked problems and a one-line rationale per problem."
    )

    from jarvis_core.orchestrator import run_worker
    started = time.perf_counter()
    try:
        outcome = await asyncio.wait_for(
            run_worker(prompt, project_root=PROJECT_ROOT, max_turns=15,
                       timeout_seconds=900, model=DEFAULT_MODEL),
            timeout=950,
        )
    except asyncio.TimeoutError:
        log.error("Phase 2 timeout")
        return 2
    duration_s = int(time.perf_counter() - started)

    out_path = _slug_dir(slug) / "phase_2_problems.md"
    out_path.write_text(outcome.text or "(no output)")
    state["phase_outputs"]["2"] = {
        "report": str(out_path.relative_to(PROJECT_ROOT)),
        "duration_s": duration_s,
        "completed_at": datetime.now(timezone.utc).isoformat(),
    }
    state["current_checkpoint"] = "2"
    _save_state(slug, state)

    _append_checkpoint_log(
        slug,
        f"**Phase 2 complete** — 10 problems scored in {duration_s}s.\n"
        f"Report: `{out_path.name}`.\n"
        f"**CHECKPOINT 2** — Boss picks 2-3 via `/wr_pick {slug} <id1,id2,id3>`.",
    )
    _send_telegram(
        f"🧩 *War Room {slug}* — Phase 2 done in {duration_s}s.\n"
        f"  • Report: `{out_path.relative_to(PROJECT_ROOT)}`\n\n"
        f"⚠️ CHECKPOINT 2 — Pick 2-3 problem ids:\n"
        f"`/wr_pick {slug} id1,id2[,id3]`",
        state.get("telegram_chat_id"),
    )
    return 0


async def cmd_run_phase_3(slug: str) -> int:
    state = _load_state(slug)
    shortlisted = state.get("shortlisted_problem_ids") or []
    if not shortlisted:
        log.error("No problems shortlisted — run `pick` first")
        return 2

    state["current_phase"] = 3
    state["current_checkpoint"] = None
    _save_state(slug, state)

    _send_telegram(
        f"⚙️ *War Room {slug}* — Phase 3 starting "
        f"(solution research × {len(shortlisted)} problems × 4 agents each).",
        state.get("telegram_chat_id"),
    )

    # For each shortlisted problem, run 4 agents in parallel
    phase_2_md = (_slug_dir(slug) / "phase_2_problems.md").read_text()
    out_dir = _slug_dir(slug) / "phase_3_solutions"
    out_dir.mkdir(parents=True, exist_ok=True)

    from jarvis_core.orchestrator import run_worker
    all_problem_results = {}
    for pid in shortlisted:
        log.info("Phase 3 — solution research for %s", pid)
        prompt = (
            f"You are in Jarvis Hackathon War Room — Phase 3 (Solution Research).\n\n"
            f"PROBLEM TO SOLVE: `{pid}` (full details below).\n\n"
            f"---\n{phase_2_md}\n---\n\n"
            f"Run these 4 subagents in PARALLEL via the Agent tool: "
            f"`backend-engineer`, `frontend-engineer`, `ml-engineer`, `data-engineer`. "
            f"For each, request architecture / stack-selection / data-strategy / AI-ML-strategy "
            f"per spec §9.\n\n"
            f"Synthesise into ONE markdown document with sections: "
            f"Architecture (mermaid diagram), Stack Selection (every choice with 2+ alternatives + why), "
            f"Data Strategy, AI/ML Strategy. Include composite re-score."
        )
        started = time.perf_counter()
        try:
            outcome = await asyncio.wait_for(
                run_worker(prompt, project_root=PROJECT_ROOT, max_turns=20,
                           timeout_seconds=900, model=DEFAULT_MODEL),
                timeout=950,
            )
            problem_md = _slug_dir(slug) / "phase_3_solutions" / f"problem_{pid}.md"
            problem_md.write_text(outcome.text or "(no output)")
            all_problem_results[pid] = {
                "report": str(problem_md.relative_to(PROJECT_ROOT)),
                "duration_s": int(time.perf_counter() - started),
            }
        except asyncio.TimeoutError:
            log.error("Phase 3 timeout for %s", pid)
            all_problem_results[pid] = {"error": "timeout"}

    state["phase_outputs"]["3"] = {
        "per_problem": all_problem_results,
        "completed_at": datetime.now(timezone.utc).isoformat(),
    }
    state["current_checkpoint"] = "3"
    _save_state(slug, state)

    _append_checkpoint_log(
        slug,
        f"**Phase 3 complete** — solutions researched for {len(all_problem_results)} problems.\n"
        f"**CHECKPOINT 3** — Boss picks 1 final problem to commit to via `/wr_pick {slug} <id>`.",
    )
    _send_telegram(
        f"⚙️ *War Room {slug}* — Phase 3 done.\n"
        f"  • Solutions: {len(all_problem_results)} problem(s) researched\n"
        f"  • Reports in `data/hackathons/{slug}/phase_3_solutions/`\n\n"
        f"⚠️ CHECKPOINT 3 — Commit to 1 problem:\n"
        f"`/wr_pick {slug} <id>`",
        state.get("telegram_chat_id"),
    )
    return 0


async def cmd_run_phase_4(slug: str) -> int:
    state = _load_state(slug)
    selected = state.get("selected_problem_id")
    if not selected:
        log.error("No problem selected — run `pick` at checkpoint 3 first")
        return 2

    state["current_phase"] = 4
    state["current_checkpoint"] = None
    _save_state(slug, state)

    _send_telegram(
        f"🔥 *War Room {slug}* — Phase 4 starting (critique).",
        state.get("telegram_chat_id"),
    )

    solution_md = (_slug_dir(slug) / "phase_3_solutions" / f"problem_{selected}.md").read_text()
    phase_2_md = (_slug_dir(slug) / "phase_2_problems.md").read_text()

    prompt = (
        f"You are in Jarvis Hackathon War Room — Phase 4 (Validation).\n\n"
        f"Use the Agent tool to delegate to `hackathon-critique` subagent. Pass it ALL of:\n"
        f"  - The selected problem (`{selected}`) full Phase 2 entry\n"
        f"  - The Phase 3 solution research below\n\n"
        f"---\n{solution_md}\n---\n\n{phase_2_md}\n---\n\n"
        f"Return the critique YAML verbatim. If verdict is `reject`, halt — Boss must "
        f"loop back to Phase 3 with revised prompts."
    )
    from jarvis_core.orchestrator import run_worker
    started = time.perf_counter()
    try:
        outcome = await asyncio.wait_for(
            run_worker(prompt, project_root=PROJECT_ROOT, max_turns=10,
                       timeout_seconds=600, model=DEFAULT_MODEL),
            timeout=650,
        )
    except asyncio.TimeoutError:
        log.error("Phase 4 timeout")
        return 2
    duration_s = int(time.perf_counter() - started)
    out_path = _slug_dir(slug) / "phase_4_risk_register.md"
    out_path.write_text(outcome.text or "(no output)")

    # Naive verdict detection
    verdict = "approve"
    text = (outcome.text or "").lower()
    if "verdict: reject" in text or 'verdict:"reject"' in text:
        verdict = "reject"
    elif "verdict: approve_with_changes" in text:
        verdict = "approve_with_changes"

    state["phase_outputs"]["4"] = {
        "report": str(out_path.relative_to(PROJECT_ROOT)),
        "duration_s": duration_s,
        "verdict": verdict,
        "completed_at": datetime.now(timezone.utc).isoformat(),
    }
    _save_state(slug, state)

    if verdict == "reject":
        _send_telegram(
            f"🔥 *War Room {slug}* — Phase 4 verdict: *REJECT*.\n"
            f"Critic recommends loop back to Phase 3. Review:\n"
            f"`data/hackathons/{slug}/phase_4_risk_register.md`",
            state.get("telegram_chat_id"),
        )
        return 0

    state["current_checkpoint"] = None  # Phase 4 → 5 is automatic gate
    _save_state(slug, state)

    _send_telegram(
        f"🔥 *War Room {slug}* — Phase 4 done. Verdict: *{verdict}*.\n"
        f"Auto-advancing to Phase 5 (build plan). Run: `run {slug}`.",
        state.get("telegram_chat_id"),
    )
    return 0


async def cmd_run_phase_5(slug: str) -> int:
    state = _load_state(slug)
    state["current_phase"] = 5
    state["current_checkpoint"] = None
    _save_state(slug, state)

    _send_telegram(
        f"🏗️ *War Room {slug}* — Phase 5 starting (final War Room Document).",
        state.get("telegram_chat_id"),
    )

    # Concatenate all phase outputs
    sections: list[tuple[str, Path]] = [
        ("Company Intelligence", _slug_dir(slug) / "phase_1_research" / "company_intelligence_report.md"),
        ("Hackathon Intelligence", _slug_dir(slug) / "phase_1_research" / "hackathon_intelligence_report.md"),
        ("Phase 2 — 10 Problems", _slug_dir(slug) / "phase_2_problems.md"),
        ("Phase 4 — Risk Register", _slug_dir(slug) / "phase_4_risk_register.md"),
    ]
    selected = state.get("selected_problem_id")
    if selected:
        sections.append((
            f"Phase 3 — Selected solution ({selected})",
            _slug_dir(slug) / "phase_3_solutions" / f"problem_{selected}.md",
        ))

    bundle = []
    for title, p in sections:
        if p.exists():
            bundle.append(f"## {title}\n\n{p.read_text()}\n")

    prompt = (
        f"You are in Jarvis Hackathon War Room — Phase 5 (Final Build Plan).\n\n"
        f"Use the Agent tool to delegate to `product-manager`, `technical-writer`, "
        f"`pitch-deck-consultant`, `qa-test-engineer` in sequence. Synthesise ALL "
        f"prior phase outputs (below) into the final War Room Document per spec §13. "
        f"19 sections, in this order:\n"
        f"1 Executive Summary · 2 Company Intelligence Report · 3 Hackathon Intelligence Report · "
        f"4 Top 10 Problems · 5 Selected Problem + rationale · 6 Deep Solution Research · "
        f"7 Final Architecture · 8 Tech Stack Decision Log · 9 Team Structure · "
        f"10 Execution Roadmap · 11 Risk Register · 12 Judge-Winning Strategy · "
        f"13 Demo Strategy · 14 Presentation Strategy · 15 GitHub Structure · "
        f"16 MVP Scope · 17 Scaling Roadmap · 18 Agent Workflow Diagram · "
        f"19 Appendix: Sources + Confidence.\n\n"
        f"---\n\n" + "\n---\n\n".join(bundle) + "\n\n---\n\n"
        f"Return the full War Room Document as one markdown file."
    )
    from jarvis_core.orchestrator import run_worker
    started = time.perf_counter()
    try:
        outcome = await asyncio.wait_for(
            run_worker(prompt, project_root=PROJECT_ROOT, max_turns=15,
                       timeout_seconds=900, model=DEFAULT_MODEL),
            timeout=950,
        )
    except asyncio.TimeoutError:
        log.error("Phase 5 timeout")
        return 2
    duration_s = int(time.perf_counter() - started)

    out_path = _slug_dir(slug) / "war_room.md"
    out_path.write_text(outcome.text or "(no output)")

    state["phase_outputs"]["5"] = {
        "report": str(out_path.relative_to(PROJECT_ROOT)),
        "duration_s": duration_s,
        "completed_at": datetime.now(timezone.utc).isoformat(),
    }
    state["current_phase"] = "done"
    state["war_room_document_path"] = str(out_path.relative_to(PROJECT_ROOT))
    _save_state(slug, state)

    _send_telegram(
        f"🏆 *War Room {slug}* — DONE!\n"
        f"Final War Room Document: `{out_path.relative_to(PROJECT_ROOT)}`\n"
        f"Duration Phase 5: {duration_s}s.",
        state.get("telegram_chat_id"),
    )
    return 0


# ── Run dispatcher ───────────────────────────────────────────────────────────


async def cmd_run(slug: str) -> int:
    state = _load_state(slug)
    phase = state.get("current_phase")
    checkpoint = state.get("current_checkpoint")

    # Decide what to run based on (phase, checkpoint) tuple
    if phase == 0 and checkpoint is None:
        return await cmd_run_phase_1(slug)
    if phase == 1 and checkpoint == "1":
        log.error("At Checkpoint 1 — Boss must `/wr_checkpoint %s approve` first", slug)
        return 2
    if phase == 2 and checkpoint is None:
        return await cmd_run_phase_2(slug)
    if phase == 2 and checkpoint == "2":
        log.error("At Checkpoint 2 — Boss must `/wr_pick %s <ids>` first", slug)
        return 2
    if phase == 3 and checkpoint is None:
        return await cmd_run_phase_3(slug)
    if phase == 3 and checkpoint == "3":
        log.error("At Checkpoint 3 — Boss must `/wr_pick %s <id>` first", slug)
        return 2
    if phase == 4 and checkpoint is None:
        return await cmd_run_phase_4(slug)
    if phase == 5 and checkpoint is None:
        return await cmd_run_phase_5(slug)
    log.warning("Nothing to do — phase=%s checkpoint=%s", phase, checkpoint)
    return 0


# ── Checkpoint advance ───────────────────────────────────────────────────────


def cmd_checkpoint(slug: str, decision: str) -> int:
    state = _load_state(slug)
    cp = state.get("current_checkpoint")
    if cp is None:
        log.error("Not at a checkpoint — current_checkpoint=None")
        return 2

    decision = decision.lower()
    if decision not in ("approve", "drill", "skip"):
        log.error("Decision must be approve|drill|skip")
        return 2

    if decision == "approve":
        # advance phase
        cp_to_phase = {"1": 2, "2": 3, "3": 4}
        if cp not in cp_to_phase:
            log.error("Unknown checkpoint %r", cp)
            return 2
        state["current_phase"] = cp_to_phase[cp] - 1  # set to prev so run advances
        state["current_checkpoint"] = cp  # keep marker until run starts
        # The run dispatcher uses (phase, checkpoint) tuple; clear checkpoint to None
        # so the next run kicks off the next phase
        state["current_checkpoint"] = None
        state["decisions"].append({
            "ts": datetime.now(timezone.utc).isoformat(),
            "checkpoint": cp, "decision": "approve",
        })
        # Actually advance current_phase to next phase number directly:
        state["current_phase"] = cp_to_phase[cp]
    elif decision == "drill":
        state["decisions"].append({
            "ts": datetime.now(timezone.utc).isoformat(),
            "checkpoint": cp, "decision": "drill",
            "note": "Boss requested deeper drilling on this phase.",
        })
        log.info("Drill noted — re-run the phase manually with specific agent prompts.")
    elif decision == "skip":
        # Skip from checkpoint 1 → Phase 3, etc.
        skip_map = {"1": 3, "2": 4}
        if cp not in skip_map:
            log.error("Cannot skip from checkpoint %r", cp)
            return 2
        state["current_phase"] = skip_map[cp]
        state["current_checkpoint"] = None
        state["decisions"].append({
            "ts": datetime.now(timezone.utc).isoformat(),
            "checkpoint": cp, "decision": "skip",
        })
    _save_state(slug, state)
    _append_checkpoint_log(slug, f"Boss decision at checkpoint {cp}: **{decision}**.")
    print(f"OK — checkpoint {cp} decision={decision}. current_phase={state['current_phase']}")
    return 0


def cmd_pick(slug: str, ids_csv: str) -> int:
    state = _load_state(slug)
    cp = state.get("current_checkpoint")
    ids = [s.strip() for s in ids_csv.split(",") if s.strip()]
    if cp == "2":
        if not (2 <= len(ids) <= 3):
            log.error("Phase 2 pick: choose 2-3 ids")
            return 2
        state["shortlisted_problem_ids"] = ids
        state["current_checkpoint"] = None
        state["current_phase"] = 3
        state["decisions"].append({
            "ts": datetime.now(timezone.utc).isoformat(),
            "checkpoint": "2", "decision": "pick", "ids": ids,
        })
        _save_state(slug, state)
        print(f"OK — shortlisted {ids}. Next: `run {slug}` (Phase 3).")
        return 0
    if cp == "3":
        if len(ids) != 1:
            log.error("Phase 3 pick: choose exactly 1 id")
            return 2
        state["selected_problem_id"] = ids[0]
        state["current_checkpoint"] = None
        state["current_phase"] = 4
        state["decisions"].append({
            "ts": datetime.now(timezone.utc).isoformat(),
            "checkpoint": "3", "decision": "pick", "ids": ids,
        })
        _save_state(slug, state)
        print(f"OK — selected {ids[0]}. Next: `run {slug}` (Phase 4).")
        return 0
    log.error("Not at a pick-checkpoint — current=%r", cp)
    return 2


# ── CLI ──────────────────────────────────────────────────────────────────────


def _cli() -> int:
    parser = argparse.ArgumentParser(description="Hackathon War Room workflow runner")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_start = sub.add_parser("start", help="Initialise a new war-room folder")
    p_start.add_argument("slug")
    p_start.add_argument("--input", help="Path to JSON file with input contract")

    p_status = sub.add_parser("status", help="Show state of a war room")
    p_status.add_argument("slug")

    p_run = sub.add_parser("run", help="Run the next phase (resumes from saved state)")
    p_run.add_argument("slug")

    p_resume = sub.add_parser("resume", help="Alias for run")
    p_resume.add_argument("slug")

    p_cp = sub.add_parser("checkpoint", help="Advance from current checkpoint")
    p_cp.add_argument("slug")
    p_cp.add_argument("decision", choices=["approve", "drill", "skip"])

    p_pick = sub.add_parser("pick", help="Pick problem id(s) at a checkpoint")
    p_pick.add_argument("slug")
    p_pick.add_argument("ids", help="Comma-separated problem ids")

    args = parser.parse_args()

    if args.cmd == "start":
        return cmd_start(args.slug, args.input)
    if args.cmd == "status":
        return cmd_status(args.slug)
    if args.cmd in ("run", "resume"):
        return asyncio.run(cmd_run(args.slug))
    if args.cmd == "checkpoint":
        return cmd_checkpoint(args.slug, args.decision)
    if args.cmd == "pick":
        return cmd_pick(args.slug, args.ids)
    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(_cli())
