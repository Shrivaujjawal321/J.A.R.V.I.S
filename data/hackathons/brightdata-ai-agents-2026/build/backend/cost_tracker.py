"""Per-day spend ledger. $5/day cap by default."""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

LEDGER = Path(__file__).parent.parent / "data" / "cost_tracker.json"
LEDGER.parent.mkdir(parents=True, exist_ok=True)

DAILY_CAP_USD = 5.0

# Sonnet 4.6 (Nov 2025+)
COST_PER_MTOK_INPUT = 3.0
COST_PER_MTOK_OUTPUT = 15.0
COST_PER_MTOK_CACHE_READ = 0.30


def compute_cost(usage: dict) -> float:
    """Anthropic usage block → cost in USD."""
    cache_read = usage.get("cache_read_input_tokens", 0)
    fresh_input = usage.get("input_tokens", 0)
    output = usage.get("output_tokens", 0)
    return (
        (fresh_input / 1_000_000) * COST_PER_MTOK_INPUT
        + (cache_read / 1_000_000) * COST_PER_MTOK_CACHE_READ
        + (output / 1_000_000) * COST_PER_MTOK_OUTPUT
    )


def check_and_record(cost_usd: float) -> bool:
    """Return False if recording would exceed daily cap."""
    today = str(date.today())
    data = json.loads(LEDGER.read_text()) if LEDGER.exists() else {}
    if data.get(today, 0.0) + cost_usd > DAILY_CAP_USD:
        return False
    data[today] = round(data.get(today, 0.0) + cost_usd, 6)
    LEDGER.write_text(json.dumps(data, indent=2))
    return True


def today_spend() -> float:
    today = str(date.today())
    data = json.loads(LEDGER.read_text()) if LEDGER.exists() else {}
    return data.get(today, 0.0)
