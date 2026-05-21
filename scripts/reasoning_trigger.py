#!/usr/bin/env python3
"""
reasoning_trigger.py — Phase D of the self-growth loop.

Runs every 4 hours via systemd timer. Reads Boss's recent state across multiple
sources, asks Claude (Haiku) to synthesise up to 3 prioritised proposals, and
sends a Telegram nudge only when the overall signal is `medium` or higher.

See `specs/reasoning-trigger.spec.md` for the full contract.

Usage:
    .venv/bin/python scripts/reasoning_trigger.py
    .venv/bin/python scripts/reasoning_trigger.py --dry-run
"""
from __future__ import annotations

import argparse
import asyncio
import json
import logging
import os
import re
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# ── Paths + defaults ──────────────────────────────────────────────────────────

TASKS_FILE = PROJECT_ROOT / "data" / "tasks.md"
MARKERS_DIR = PROJECT_ROOT / "data" / "markers"
FEEDBACK_LOG = PROJECT_ROOT / "data" / "logs" / "feedback.jsonl"
AUDIT_DIR = PROJECT_ROOT / "data" / "audits"
LINKEDIN_DIR = PROJECT_ROOT / "data" / "linkedin"
HABITS_FILE = PROJECT_ROOT / "data" / "memory" / "habits.md"
HACKATHONS_DIR = PROJECT_ROOT / "data" / "hackathons"

STATE_FILE = MARKERS_DIR / "reasoning_state.json"
RUN_LOG = PROJECT_ROOT / "data" / "logs" / "reasoning_trigger.jsonl"

LLM_MODEL = os.getenv("JARVIS_REASONING_MODEL", "claude-haiku-4-5-20251001")
HARD_TIMEOUT_S = 90
COOLDOWN_HOURS = 12

ROOT_ENV = PROJECT_ROOT / ".env"
BRIDGE_ENV = PROJECT_ROOT / "bridge" / ".env"

logging.basicConfig(
    level=os.getenv("JARVIS_REASONING_LOG_LEVEL", "INFO"),
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)
log = logging.getLogger("reasoning_trigger")


# ── Env loading ───────────────────────────────────────────────────────────────


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


# ── State (cooldown) ──────────────────────────────────────────────────────────


def _load_state() -> dict:
    if not STATE_FILE.exists():
        return {"alerts_by_topic": {}, "last_run_ts": None}
    try:
        return json.loads(STATE_FILE.read_text())
    except Exception as exc:
        log.warning("state corrupt (%s) — resetting", exc)
        return {"alerts_by_topic": {}, "last_run_ts": None}


def _save_state(state: dict) -> None:
    MARKERS_DIR.mkdir(parents=True, exist_ok=True)
    tmp = STATE_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps(state, indent=2))
    tmp.replace(STATE_FILE)


def _topic_on_cooldown(state: dict, topic: str) -> bool:
    last = state.get("alerts_by_topic", {}).get(topic)
    if not last:
        return False
    try:
        when = datetime.fromisoformat(last)
    except ValueError:
        return False
    return datetime.now(timezone.utc) - when < timedelta(hours=COOLDOWN_HOURS)


def _record_alert(state: dict, topic: str) -> None:
    state.setdefault("alerts_by_topic", {})[topic] = datetime.now(timezone.utc).isoformat()


# ── Signal collection ────────────────────────────────────────────────────────


def _read_text_safe(path: Path, max_chars: int = 4000) -> str:
    if not path.exists():
        return ""
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""
    if len(text) > max_chars:
        return text[-max_chars:]  # keep most-recent end
    return text


def _read_recent_jsonl(path: Path, days: int = 7, max_lines: int = 100) -> list[dict]:
    if not path.exists():
        return []
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    out: list[dict] = []
    try:
        for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
            if not raw.strip():
                continue
            try:
                obj = json.loads(raw)
            except json.JSONDecodeError:
                continue
            ts_str = obj.get("ts") or obj.get("timestamp")
            if ts_str:
                try:
                    when = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
                except ValueError:
                    when = None
                if when and when < cutoff:
                    continue
            out.append(obj)
    except Exception as exc:
        log.warning("could not read %s: %s", path, exc)
    return out[-max_lines:]


def _summarise_markers() -> dict[str, str]:
    """For each marker file, report 'N days ago' age."""
    out: dict[str, str] = {}
    if not MARKERS_DIR.exists():
        return out
    now = datetime.now(timezone.utc)
    for f in sorted(MARKERS_DIR.glob("*")):
        if not f.is_file() or f.name in ("reasoning_state.json", "trigger_state.json"):
            continue
        try:
            mtime = datetime.fromtimestamp(f.stat().st_mtime, tz=timezone.utc)
        except Exception:
            continue
        age_days = (now - mtime).total_seconds() / 86_400
        out[f.name] = f"{age_days:.1f} days ago"
    return out


def _collect_signals() -> dict:
    """Build the structured signals payload for the LLM."""
    audit_files = sorted(AUDIT_DIR.glob("*.jsonl"), reverse=True)[:7] if AUDIT_DIR.exists() else []
    audit_lines: list[dict] = []
    for f in audit_files:
        audit_lines.extend(_read_recent_jsonl(f, days=7, max_lines=30))

    linkedin_files = sorted(LINKEDIN_DIR.glob("*.jsonl"), reverse=True)[:5] if LINKEDIN_DIR.exists() else []
    linkedin_lines: list[dict] = []
    for f in linkedin_files:
        linkedin_lines.extend(_read_recent_jsonl(f, days=7, max_lines=20))

    hackathon_files = sorted(HACKATHONS_DIR.glob("*"))[-5:] if HACKATHONS_DIR.exists() else []
    hackathon_text = "\n\n".join(
        f"## {f.name}\n{_read_text_safe(f, 1000)}" for f in hackathon_files if f.is_file()
    )

    return {
        "now": datetime.now(timezone.utc).isoformat(),
        "tasks_md": _read_text_safe(TASKS_FILE, 3000),
        "habits_md": _read_text_safe(HABITS_FILE, 1500),
        "markers": _summarise_markers(),
        "feedback_last_14d": _read_recent_jsonl(FEEDBACK_LOG, days=14, max_lines=40),
        "audit_last_7d": audit_lines[-50:],
        "linkedin_last_7d": linkedin_lines[-30:],
        "hackathons_excerpt": hackathon_text[:2500],
    }


# ── Synthesis prompt ─────────────────────────────────────────────────────────


_SYNTH_TEMPLATE = """You are Jarvis's reasoning-trigger module. Boss (Ujjawal) is busy; you only nudge him when multiple signals add up to something worth surfacing. Stay grounded — every proposal MUST cite specific evidence from the signals below.

Boss's current priorities (descending):
1. Resume + AI/ML job hunt (P0)
2. Hackathon submissions (P0 if deadline in 7 days)
3. LinkedIn growth pipeline approvals (P1)
4. Anisha (P1 — never escalate solo; surface only obvious gaps)
5. Habits / sleep (P2)

Read the signals and decide:
- Overall `signal_level`: "low" | "medium" | "high"
- Up to 3 `proposals`, each with topic / why / action / urgency
  - `topic`: 1-3 word tag — used for cooldown
  - `why`: one sentence citing specific evidence ("marker says last resume edit 4.2 days ago + 12 unapproved LinkedIn drafts")
  - `action`: a single concrete next step (≤ 15 words)
  - `urgency`: "now" | "today" | "this_week"

`signal_level` logic:
- "low" — nothing urgent. Boss gets no Telegram. Default.
- "medium" — one clear gap OR multiple weak signals compounding. Telegram digest.
- "high" — actual deadline within 48h or compliance/safety issue. Telegram now.

Output ONLY a single JSON object, no prose around it:

{"signal_level": "...", "proposals": [{"topic": "...", "why": "...", "action": "...", "urgency": "..."}]}

If you have nothing meaningful, return: {"signal_level": "low", "proposals": []}.

---

SIGNALS:

__SIGNALS_BLOCK__

Now output the JSON object."""


def _build_signals_block(signals: dict) -> str:
    parts: list[str] = []
    parts.append(f"CURRENT TIME (UTC): {signals['now']}")
    parts.append("")
    parts.append("== MARKERS (age since last update) ==")
    for k, v in signals.get("markers", {}).items():
        parts.append(f"  {k}: {v}")
    parts.append("")
    parts.append("== OPEN TASKS (data/tasks.md) ==")
    parts.append(signals.get("tasks_md") or "(empty)")
    parts.append("")
    parts.append("== HABITS (data/memory/habits.md) ==")
    parts.append(signals.get("habits_md") or "(empty)")
    parts.append("")
    parts.append("== FEEDBACK (last 14 days) ==")
    fb = signals.get("feedback_last_14d") or []
    if fb:
        for entry in fb[-15:]:
            parts.append(f"  - {entry.get('ts','?')} {entry.get('rating','?')} on {entry.get('target','?')}: {entry.get('note','')[:120]}")
    else:
        parts.append("  (none)")
    parts.append("")
    parts.append("== AUDIT (last 7 days) ==")
    audit = signals.get("audit_last_7d") or []
    if audit:
        for entry in audit[-25:]:
            parts.append(f"  - {entry.get('ts','?')} tier{entry.get('tier','?')} action={entry.get('action','?')[:80]}")
    else:
        parts.append("  (none)")
    parts.append("")
    parts.append("== LINKEDIN PIPELINE (last 7 days) ==")
    li = signals.get("linkedin_last_7d") or []
    if li:
        for entry in li[-15:]:
            parts.append(f"  - {entry.get('ts','?')} {str(entry)[:160]}")
    else:
        parts.append("  (none)")
    parts.append("")
    parts.append("== HACKATHONS UPCOMING (excerpt) ==")
    parts.append(signals.get("hackathons_excerpt") or "(none)")
    return "\n".join(parts)


def _build_synth_prompt(signals: dict) -> str:
    return _SYNTH_TEMPLATE.replace("__SIGNALS_BLOCK__", _build_signals_block(signals))


# ── LLM dispatch + parsing ───────────────────────────────────────────────────


_JSON_BLOCK_RE = re.compile(r"\{.*\}", re.DOTALL)


def _parse_synth(raw: str) -> dict | None:
    if not raw:
        return None
    text = raw.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    candidates = [text]
    m = _JSON_BLOCK_RE.search(text)
    if m:
        candidates.append(m.group(0))
    for c in candidates:
        try:
            data = json.loads(c)
        except (json.JSONDecodeError, ValueError):
            continue
        if isinstance(data, dict) and "signal_level" in data:
            return data
    return None


async def _synthesise(signals: dict) -> dict | None:
    from jarvis_core.orchestrator import run_worker

    prompt = _build_synth_prompt(signals)
    try:
        outcome = await asyncio.wait_for(
            run_worker(
                prompt,
                project_root=PROJECT_ROOT,
                max_turns=1,
                allowed_tools=[],
                timeout_seconds=60,
                model=LLM_MODEL,
            ),
            timeout=70,
        )
    except asyncio.TimeoutError:
        log.warning("synthesis timeout")
        return None
    except Exception as exc:
        log.warning("synthesis error: %s", exc)
        return None
    if outcome.error and not outcome.text:
        return None
    return _parse_synth(outcome.text)


# ── Telegram dispatch ────────────────────────────────────────────────────────


def _format_telegram(synth: dict) -> str:
    level = synth.get("signal_level", "low")
    proposals = synth.get("proposals") or []
    if not proposals:
        return ""
    emoji = {"high": "🚨", "medium": "💡", "low": ""}.get(level, "💡")
    lines = [f"{emoji} *Reasoning trigger* — signal: *{level}*", ""]
    for i, p in enumerate(proposals, 1):
        topic = p.get("topic", "?")
        why = p.get("why", "")
        action = p.get("action", "")
        urgency = p.get("urgency", "")
        lines.append(f"*{i}. {topic}* _({urgency})_")
        lines.append(f"  • Why: {why}")
        lines.append(f"  • Action: {action}")
        lines.append("")
    lines.append("_Set JARVIS_REASONING_ENABLED=0 to silence._")
    return "\n".join(lines)


def _send_telegram(text: str) -> bool:
    token = ENV.get("TELEGRAM_BOT_TOKEN")
    chat_id = ENV.get("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        log.info("Telegram creds missing — skipping send")
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


# ── Main ─────────────────────────────────────────────────────────────────────


def _append_run_log(entry: dict) -> None:
    try:
        RUN_LOG.parent.mkdir(parents=True, exist_ok=True)
        with RUN_LOG.open("a") as fh:
            fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception:
        pass


async def main(dry_run: bool = False) -> int:
    if os.getenv("JARVIS_REASONING_ENABLED", "1") in ("0", "false", "False"):
        log.info("disabled via env — exit clean")
        return 0

    started = time.perf_counter()
    state = _load_state()
    signals = _collect_signals()

    if dry_run:
        log.info("DRY RUN — signals collected:")
        for k, v in signals.items():
            if isinstance(v, str):
                log.info("  %s: %d chars", k, len(v))
            elif isinstance(v, list):
                log.info("  %s: %d items", k, len(v))
            elif isinstance(v, dict):
                log.info("  %s: %d keys", k, len(v))
        _append_run_log({
            "ts": datetime.now(timezone.utc).isoformat(),
            "status": "dry_run",
        })
        return 0

    try:
        synth = await asyncio.wait_for(_synthesise(signals), timeout=HARD_TIMEOUT_S)
    except asyncio.TimeoutError:
        log.warning("hard timeout (%ds) exceeded in synthesis", HARD_TIMEOUT_S)
        synth = None

    if not synth:
        _append_run_log({
            "ts": datetime.now(timezone.utc).isoformat(),
            "status": "synth_failed",
        })
        return 0

    signal_level = synth.get("signal_level", "low")
    proposals = synth.get("proposals") or []

    # Filter cooldown
    filtered: list[dict] = []
    for p in proposals:
        topic = str(p.get("topic", "")).strip().lower()
        if not topic:
            continue
        if _topic_on_cooldown(state, topic):
            log.info("topic %r on cooldown — skipping", topic)
            continue
        filtered.append(p)

    sent = False
    if signal_level in ("medium", "high") and filtered:
        text = _format_telegram({"signal_level": signal_level, "proposals": filtered})
        if text:
            sent = _send_telegram(text)
            if sent:
                for p in filtered:
                    _record_alert(state, str(p.get("topic", "")).strip().lower())

    state["last_run_ts"] = datetime.now(timezone.utc).isoformat()
    _save_state(state)

    duration_ms = int((time.perf_counter() - started) * 1000)
    log.info("done signal=%s proposals=%d sent=%s %dms",
             signal_level, len(proposals), sent, duration_ms)
    _append_run_log({
        "ts": datetime.now(timezone.utc).isoformat(),
        "status": "ok",
        "signal_level": signal_level,
        "proposals_count": len(proposals),
        "proposals_after_cooldown": len(filtered),
        "telegram_sent": sent,
        "duration_ms": duration_ms,
    })
    return 0


def _cli() -> int:
    parser = argparse.ArgumentParser(description="Reasoning trigger — synthesise Boss's state")
    parser.add_argument("--dry-run", action="store_true",
                        help="Collect signals + print, but no LLM, no Telegram")
    args = parser.parse_args()
    return asyncio.run(main(dry_run=args.dry_run))


if __name__ == "__main__":
    raise SystemExit(_cli())
