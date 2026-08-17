#!/usr/bin/env python3
"""
scripts/run_and_capture.py
==========================
All-in-one: init DB, start backend on :8000, wait for health,
run demo capture, kill backend, save data/demo/demo_cache.json.

Usage:
    /path/to/.venv/bin/python scripts/run_and_capture.py
"""
from __future__ import annotations

import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PYTHON = REPO / ".venv" / "bin" / "python"
UVICORN = REPO / ".venv" / "bin" / "uvicorn"
PORT = 8000
BASE_URL = f"http://127.0.0.1:{PORT}"
DEMO_DIR = REPO / "data" / "demo"
LOG_PATH = DEMO_DIR / "backend_capture.log"

os.chdir(REPO)
sys.path.insert(0, str(REPO))


def init_db() -> None:
    print("[1/4] Initializing database...")
    from wizard.core.db import init_db as _init
    _init()
    print("  DB initialized at data/wizard.db")


def start_backend() -> subprocess.Popen:
    print(f"[2/4] Starting backend on :{PORT}...")
    DEMO_DIR.mkdir(parents=True, exist_ok=True)
    env = {**os.environ, "BACKEND_PORT": str(PORT)}
    log_f = open(LOG_PATH, "w")
    proc = subprocess.Popen(
        [str(UVICORN), "wizard.backend.app:app",
         "--host", "127.0.0.1",
         "--port", str(PORT),
         "--workers", "1"],
        env=env,
        stdout=log_f,
        stderr=subprocess.STDOUT,
        cwd=str(REPO),
    )
    print(f"  Backend PID: {proc.pid}")
    return proc


def wait_for_health(max_seconds: int = 90) -> bool:
    import httpx
    print(f"[3/4] Waiting for backend health (max {max_seconds}s)...")
    client = httpx.Client(base_url=BASE_URL, timeout=5.0)
    start = time.monotonic()
    while time.monotonic() - start < max_seconds:
        try:
            r = client.get("/v1/health")
            if r.status_code == 200:
                data = r.json()
                print(f"  Backend healthy: status={data.get('status')} db={data.get('db_ok')}")
                client.close()
                return True
        except Exception:
            pass
        time.sleep(2)
        elapsed = int(time.monotonic() - start)
        print(f"  Waited {elapsed}s...")
    client.close()
    return False


def run_capture() -> None:
    print("[4/4] Running demo cache capture...")
    capture_script = REPO / "scripts" / "capture_demo_cache.py"
    result = subprocess.run(
        [str(PYTHON), str(capture_script)],
        cwd=str(REPO),
        capture_output=False,
    )
    if result.returncode != 0:
        print(f"  WARN: capture script exited with code {result.returncode}")


def main() -> None:
    proc = None
    try:
        init_db()
        proc = start_backend()
        if not wait_for_health():
            print("ERROR: Backend did not come up in time. Check data/demo/backend_capture.log")
            if LOG_PATH.exists():
                lines = LOG_PATH.read_text().splitlines()
                print("\nLast 30 log lines:")
                for line in lines[-30:]:
                    print(f"  {line}")
            sys.exit(1)

        run_capture()

    finally:
        if proc:
            print("\nShutting down backend...")
            try:
                proc.send_signal(signal.SIGTERM)
                proc.wait(timeout=10)
            except Exception:
                proc.kill()
            print(f"  Backend stopped.")

    cache_path = DEMO_DIR / "demo_cache.json"
    if cache_path.exists():
        with open(cache_path) as f:
            cache = json.load(f)
        beats = cache.get("beats", {})
        ok = sum(1 for v in beats.values() if isinstance(v, dict) and v.get("status_code", 0) < 400)
        print(f"\nDemo cache: {cache_path}")
        print(f"Beats captured: {len(beats)} total, {ok} OK (2xx)")
    else:
        print("\nWARN: demo_cache.json not found — check logs.")


if __name__ == "__main__":
    main()
