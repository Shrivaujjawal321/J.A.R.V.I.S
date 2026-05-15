"""
Tiny helper to read Jarvis's active auto-mode from data/config/auto-mode.json.

The LinkedIn pipeline uses this to decide whether per-batch Telegram approval
(`/lp_approve_all`) is required (autopilot/manual) or whether the batch is
auto-approved end-to-end (fullauto). Same source of truth as the auto-mode
slash command and the .claude/skills/auto-mode/SKILL.md tier model.
"""
from __future__ import annotations

import json
from pathlib import Path

CONFIG_PATH = Path(__file__).resolve().parents[2] / "data" / "config" / "auto-mode.json"

VALID_MODES = ("manual", "autopilot", "fullauto")


def current_mode() -> str:
    """Returns one of VALID_MODES. Defaults to 'autopilot' on missing/corrupt config."""
    if not CONFIG_PATH.exists():
        return "autopilot"
    try:
        data = json.loads(CONFIG_PATH.read_text())
    except json.JSONDecodeError:
        return "autopilot"
    mode = data.get("mode", "autopilot")
    return mode if mode in VALID_MODES else "autopilot"


def is_fullauto() -> bool:
    return current_mode() == "fullauto"
