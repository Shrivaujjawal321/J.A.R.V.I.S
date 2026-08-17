#!/usr/bin/env python3
"""
Bake REAL Claude answers for EDITH's proactive-chip queries into the L0 demo cache,
so the cockpit demo shows genuine Claude-tier reasoning INSTANTLY (rung=cache) with
zero live-call risk — and FR1 (LLM reasoning) is exercised in the judged path.

Run ONCE while the Claude Max subscription is reachable:
    .venv/bin/python bake_demo_cache.py            # bake (calls Claude live)
    .venv/bin/python bake_demo_cache.py --verify   # assert all entries cache-hit
"""
import argparse, hashlib, json, os, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
R2 = HERE.parent
sys.path.insert(0, str(R2 / "vulcan"))
os.environ.pop("ANTHROPIC_API_KEY", None)
os.environ.setdefault("VULCAN_DATASET_ROOT",
                      str(R2 / "dataforge" / "datasets" / "steel-maintenance-flagship"))
os.environ["VULCAN_LLM_PROVIDER"] = "subscription"


def _cache_key(system: str, user: str) -> str:
    return hashlib.sha256(f"{system}\x00{user}".encode("utf-8")).hexdigest()


def seeded(asset_id: str, eq_class: str, chip: str) -> str:
    """Replicate edith/backend/main.py ask() seeding for generic chip queries."""
    return f"For asset {asset_id} ({eq_class}): {chip}"


# Exactly what the cockpit sends when a judge clicks each proactive chip.
QUERIES = [
    # GBX01 (watch state chips)
    ("s-gbx-1", seeded("HSM.F1.GBX01", "mill_gearbox", "What's most likely causing this trend?")),
    ("s-gbx-2", seeded("HSM.F1.GBX01", "mill_gearbox", "Should I move up the next inspection?")),
    ("s-gbx-3", seeded("HSM.F1.GBX01", "mill_gearbox", "What happens if this continues for 2 weeks?")),
    # BRG01 (healthy state chips)
    ("s-brg-1", seeded("HSM.F3.WR.BRG01", "rolling_mill_work_roll_bearing", "When is the next check due?")),
    ("s-brg-2", seeded("HSM.F3.WR.BRG01", "rolling_mill_work_roll_bearing", "Show recent sensor trends for this machine.")),
    ("s-brg-3", seeded("HSM.F3.WR.BRG01", "rolling_mill_work_roll_bearing", "Any spares I should keep ready for this machine?")),
    # typed demo fallback (contains 'gearbox' -> NOT seeded)
    ("s-typed", "Diagnose this gearbox and give next steps"),
]
ALERTS = [  # the SSE auto-diagnosis hand-off per demo asset (sensor = first to alarm)
    ("HSM.F1.GBX01", ""), ("HSM.F3.WR.BRG01", ""),
]


def install_capture(captured, live=True):
    import vulcan.llm as L
    real = L.subscription_llm

    def wrapper(system, user, **kw):
        kw2 = dict(kw); kw2["return_result"] = True
        if live:
            res = real(system, user, **kw2)
        else:
            from vulcan.llm import LLMResult
            res = LLMResult(text="[dry]", rung="dryrun", latency_ms=0, is_template=True)
        captured.append({"key": _cache_key(system, user), "system": system, "user": user,
                         "response": res.text, "rung": res.rung, "task": kw.get("task")})
        return res if kw.get("return_result") else res.text

    L.subscription_llm = wrapper
    import vulcan.agents.supervisor as S
    S.subscription_llm = wrapper
    return real


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--verify", action="store_true")
    args = ap.parse_args()

    if args.verify:
        os.environ["VULCAN_LLM_MODE"] = "cache_first"
    else:
        os.environ["VULCAN_LLM_MODE"] = "live"   # bypass L0 during bake

    from vulcan.config import get_settings
    try: get_settings.cache_clear()
    except Exception: pass
    st = get_settings()
    print(f"mode={st.llm_mode} provider={st.llm_provider} oauth={st.has_oauth} "
          f"cache={st.demo_cache_path} (existing entries: pre-load below)")

    captured = []
    if not args.verify:
        install_capture(captured, live=True)

    from vulcan.agents.supervisor import Supervisor
    sup = Supervisor()

    hits = misses = 0
    for sid, q in QUERIES:
        t = time.time()
        tr = sup.handle_query(q, session_id=f"bake-{sid}")
        ms = int((time.time() - t) * 1000)
        rung = getattr(tr, "llm_rung", "?")
        print(f"  [{rung:9s} {ms:6d}ms] {q[:70]}")
        if args.verify:
            hits += rung == "cache"; misses += rung != "cache"
    for aid, sensor in ALERTS:
        t = time.time()
        tr = sup.handle_alert(asset_id=aid, sensor=sensor, severity="ALARM",
                              session_id="alerts")
        ms = int((time.time() - t) * 1000)
        rung = getattr(tr, "llm_rung", "?")
        print(f"  [{rung:9s} {ms:6d}ms] ALERT hand-off {aid}")
        if args.verify:
            hits += rung == "cache"; misses += rung != "cache"

    if args.verify:
        print(f"\nverify: {hits} cache-hits, {misses} misses")
        sys.exit(0 if misses == 0 else 1)

    # merge captured into demo_cache.json (entries shape)
    path = Path(st.demo_cache_path)
    existing = {"entries": []}
    if path.is_file():
        existing = json.loads(path.read_text())
        if "entries" not in existing:
            existing = {"entries": [{"key": k, "response": v} for k, v in existing.items()]}
    seen = {e.get("key") for e in existing["entries"]}
    added = 0
    for c in captured:
        if c["key"] in seen or c["rung"] in ("template", "dryrun"):
            continue
        existing["entries"].append(c); seen.add(c["key"]); added += 1
    path.write_text(json.dumps(existing, indent=1))
    print(f"\nbaked {added} new entries (total {len(existing['entries'])}) -> {path}")


if __name__ == "__main__":
    main()
