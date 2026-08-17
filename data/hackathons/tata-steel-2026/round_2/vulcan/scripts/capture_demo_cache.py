#!/usr/bin/env python
"""VULCAN demo-cache bake (Wave 6).

Runs the scripted demo queries / multi-turn follow-up / autonomous alert through
VULCAN ONCE while the Claude Max subscription is reachable, captures the EXACT
(system, user) prompt the LLM chokepoint receives plus Claude's response, and
writes them as keyed entries into ``data/demo/demo_cache.json``.

Because the synthesis prompt is byte-deterministic (verified: same ML outputs ->
same numbered Source [N] block -> same sha256(system+user) key), the recorded
demo then replays Claude-tier prose sub-ms from L0 with ZERO live LLM calls — so
the recording can never stall or crash on a rate-limited / offline subscription.

Usage:
    PY=/home/ujjwal/Documents/J.A.R.V.I.S./.venv/bin/python
    $PY scripts/capture_demo_cache.py            # bake all demo scenarios
    $PY scripts/capture_demo_cache.py --dry-run  # show prompts, do NOT call Claude
    $PY scripts/capture_demo_cache.py --verify    # replay from cache, assert hits

The capture FORCES the Claude rung (sets VULCAN_LLM_MODE=live so L0 cache is
skipped during bake) and records every distinct (system,user) the chokepoint
sees — including the multi-turn follow-up and the alert hand-off.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from pathlib import Path

# package root = dir that CONTAINS the `vulcan/` package
_PKG_ROOT = Path(__file__).resolve().parents[1]
if str(_PKG_ROOT) not in sys.path:
    sys.path.insert(0, str(_PKG_ROOT))

os.environ.pop("ANTHROPIC_API_KEY", None)  # keyless only


# ---------------------------------------------------------------------------
# The scripted demo. Each step drives ONE distinct (system,user) -> Claude call.
#   * 3 cold-start chip queries (chat)
#   * 1 multi-turn follow-up (proves FR3 — context carried, new intent)
#   * 1 autonomous alert hand-off on a real spine asset (FR7)
# Session ids matter for the multi-turn pair (same session => focus carried).
# ---------------------------------------------------------------------------
CHAT_STEPS = [
    {
        "id": "chip_bearing",
        "session": "demo_bearing",
        "query": (
            "I'm getting an AE warning and rising vibration on the F3 "
            "work-roll bearing (HSM.F3.WR.BRG01), and it's running hot. "
            "What's wrong and how long do I have?"
        ),
    },
    {
        "id": "chip_bearing_followup",
        "session": "demo_bearing",  # SAME session -> multi-turn focus (FR3)
        "query": "And what spare do I need to order, and do we have it in stock?",
    },
    {
        "id": "chip_blower",
        "session": "demo_blower",
        "query": (
            "The BF top-gas booster fan BF.BLW.FAN01 discharge pressure is "
            "oscillating and the anti-surge valve is cycling. Diagnose it "
            "and tell me the risk and the action."
        ),
    },
    {
        "id": "chip_gearbox_procurement",
        "session": "demo_gearbox",
        "query": (
            "For the F1 mill gearbox HSM.F1.GBX01, what spare parts would a "
            "tooth-root crack repair need, and do we have them in stock or "
            "must we order now?"
        ),
    },
]

# The autonomous alert episode (a REAL spine asset, real dense-table window).
ALERT_ASSET = "BF.BLW.FAN01"


def _cache_key(system: str, user: str) -> str:
    return hashlib.sha256(f"{system}\x00{user}".encode("utf-8")).hexdigest()


def _install_capture(captured: list[dict], *, live: bool):
    """Monkeypatch the chokepoint so every call is recorded.

    When ``live`` is True the REAL ladder runs underneath (Claude); when False we
    short-circuit to a stub so --dry-run never touches the network.
    """
    import vulcan.llm as L

    real = L.subscription_llm

    def wrapper(system, user, **kw):
        kw_capture = dict(kw)
        kw_capture["return_result"] = True
        if live:
            # Force the Claude rung: skip L0 cache for the bake by asking the real
            # ladder with mode already set to 'live' (cache_first would short-circuit).
            res = real(system, user, **kw_capture)
        else:
            from vulcan.llm import LLMResult

            res = LLMResult(text="[dry-run — Claude not called]", rung="dryrun",
                            latency_ms=0, is_template=True)
        captured.append({
            "key": _cache_key(system, user),
            "system": system,
            "user": user,
            "response": res.text,
            "rung": res.rung,
            "latency_ms": res.latency_ms,
            "task": kw.get("task"),
        })
        # hand the result back in the shape the caller asked for
        if kw.get("return_result"):
            return res
        return res.text

    # patch BOTH the module symbol and the supervisor's bound reference
    L.subscription_llm = wrapper
    import vulcan.agents.supervisor as SUP
    SUP.subscription_llm = wrapper
    return real


def bake(dry_run: bool = False) -> int:
    # Force live so the L0 cache is bypassed and the Claude rung is exercised.
    os.environ["VULCAN_LLM_MODE"] = "live"
    from vulcan.config import get_settings
    get_settings.cache_clear()  # type: ignore[attr-defined]
    settings = get_settings()
    cache_path: Path = settings.demo_cache_path

    print(f"VULCAN demo-cache bake  ·  mode={settings.llm_mode}  "
          f"provider={settings.llm_provider}  oauth={'YES' if settings.has_oauth else 'NO'}")
    print(f"  cache file: {cache_path}")
    if not dry_run and not settings.has_oauth:
        print("  !! no OAuth token resolvable — cannot bake live Claude prose. Abort.")
        return 2

    captured: list[dict] = []
    _install_capture(captured, live=not dry_run)

    from vulcan.agents.supervisor import Supervisor
    from vulcan.alerting.engine import replay_episode

    sup = Supervisor()  # one warm core for the whole bake

    # ---- chat + multi-turn steps ----
    for step in CHAT_STEPS:
        t0 = time.time()
        print(f"\n[{step['id']}] session={step['session']}")
        print(f"  Q: {step['query'][:90]}…")
        res = sup.handle_query(step["query"], session_id=step["session"])
        dt = time.time() - t0
        print(f"  -> intent={res.intent} asset={res.asset_id} scn={res.scenario_id} "
              f"risk={res.risk_band} rung={res.llm_rung} ({dt:.1f}s)")

    # ---- autonomous alert hand-off on a real asset (FR7) ----
    print(f"\n[alert_{ALERT_ASSET}] replaying real dense-table stream…")
    t0 = time.time()
    ep = replay_episode(ALERT_ASSET, handoff=True, run_gate=False, persist=False)
    print(f"  -> fired_critical={ep.fired} "
          f"first_critical_row={getattr(ep.first_critical,'row_index',None)} "
          f"({time.time()-t0:.1f}s)")

    # ---- dedupe by key (multi-turn may re-emit the same prompt — keep last) ----
    by_key: dict[str, dict] = {}
    for e in captured:
        by_key[e["key"]] = e
    entries = list(by_key.values())

    n_claude = sum(1 for e in entries if e["rung"] in ("claude", "cache"))
    n_template = sum(1 for e in entries if e["rung"] in ("template", "slm", "dryrun"))
    print(f"\nCaptured {len(captured)} calls -> {len(entries)} distinct prompts "
          f"(claude={n_claude}, non-claude={n_template})")

    if dry_run:
        print("DRY RUN — not writing cache. Distinct keys:")
        for e in entries:
            print(f"  {e['key'][:16]}  task={e['task']}  rung={e['rung']}")
        return 0

    # Refuse to bake template/empty responses into the demo cache.
    good = [e for e in entries if e["rung"] in ("claude", "cache")
            and e["response"] and not e["response"].startswith("[VULCAN ·")]
    if not good:
        print("  !! no Claude responses captured (all fell to template). "
              "Subscription likely rate-limited — re-run when reachable. Abort.")
        return 3
    if len(good) < len(entries):
        print(f"  ⚠ {len(entries)-len(good)} prompt(s) fell to template and are "
              "EXCLUDED from the cache (they will re-try live at demo time).")

    payload = {
        "_comment": ("VULCAN L0 demo cache. Keys are sha256(system + '\\x00' + user). "
                     "Baked by scripts/capture_demo_cache.py while Claude was reachable; "
                     "the recorded demo replays Claude-tier prose sub-ms with zero live "
                     "LLM calls. Re-bake whenever the demo script changes."),
        "version": "0.1.0",
        "product": "VULCAN",
        "persona": "EDITH",
        "baked_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "entries": good,
    }
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False),
                          encoding="utf-8")
    print(f"\n✅ wrote {len(good)} cached Claude responses -> {cache_path}")
    return 0


def verify() -> int:
    """Replay every scripted step with mode=cache_first and assert L0 hits."""
    os.environ["VULCAN_LLM_MODE"] = "cache_first"
    from vulcan.config import get_settings
    get_settings.cache_clear()  # type: ignore[attr-defined]
    # reset the demo-cache singleton so the freshly-baked file is reloaded
    import vulcan.llm as L
    L._DEMO_CACHE = None

    rungs: list[str] = []

    def wrapper_factory(real):
        def wrapper(system, user, **kw):
            kw2 = dict(kw); kw2["return_result"] = True
            res = real(system, user, **kw2)
            rungs.append(res.rung)
            return res if kw.get("return_result") else res.text
        return wrapper

    real = L.subscription_llm
    L.subscription_llm = wrapper_factory(real)
    import vulcan.agents.supervisor as SUP
    SUP.subscription_llm = L.subscription_llm

    from vulcan.agents.supervisor import Supervisor
    sup = Supervisor()
    for step in CHAT_STEPS:
        t0 = time.time()
        sup.handle_query(step["query"], session_id=step["session"])
        print(f"  {step['id']}: rung={rungs[-1]}  ({(time.time()-t0)*1000:.0f}ms)")

    hits = sum(1 for r in rungs if r == "cache")
    print(f"\nReplay: {hits}/{len(rungs)} chat prompts served from L0 cache (sub-ms).")
    return 0 if hits >= len(CHAT_STEPS) else 1


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true",
                    help="show prompts + keys without calling Claude")
    ap.add_argument("--verify", action="store_true",
                    help="replay from cache and assert L0 hits")
    args = ap.parse_args()
    if args.verify:
        sys.exit(verify())
    sys.exit(bake(dry_run=args.dry_run))
