# THE EDITH — Quick Start (for evaluators)

**What this is:** an agentic Maintenance Wizard for a steel plant (Tata Steel AI Hackathon
2026, Round 2). Live condition monitoring → plain-language verdicts → diagnosis / root cause /
RUL / risk / prioritized actions with citations → reports (web + PDF).

**Watch first (2 min):** the demo video — see the Demo Link on the submission (full narrated walkthrough).
**Read:** `edith/SUBMISSION_DOCUMENT.md` — architecture, models, data flow, sample I/O.

---

## Run it (Linux/macOS · ~10 minutes first time)

Prerequisites: **Python 3.10+** (with venv: `sudo apt install python3-venv` on Debian/Ubuntu),
**Node 18+** (with npm), internet for the first install.

```bash
# 1) from this folder (the ZIP root):
python3 -m venv .venv
source .venv/bin/activate
pip install -r edith/backend/requirements.txt        # ~5-8 min first time

# 2) start everything (backend :8077 + frontend :3000)
bash edith/start.sh

# 3) open the cockpit
#    http://localhost:3000
```

Stop with `bash edith/start.sh stop`.

**What you should see within ~30s:** the dark control-room cockpit; 15 machines in the left
strip; live sensor graphs streaming for the focused machine; alerts appearing as the
historian replays a degradation episode; "EDITH suggests" questions in the right panel.

Try: click `HSM.F1.GBX01` in the left strip (a machine with early gear-tooth wear) → read
the plain-language verdict → click a suggested question → expand "How EDITH decided" →
click the report button (top-right of the center panel).

---

## Notes for evaluators

- **No API key is required or used.** `GET /api/health` shows `"has_oauth": false` on your
  machine — expected. EDITH then uses its fast grounded-deterministic reasoning path (every
  answer still cited + traceable). With a Claude Max subscription token
  (`CLAUDE_CODE_OAUTH_TOKEN`) it transparently upgrades to EDITH-deep; the demo cache in
  `vulcan/data/demo/` already contains real Claude answers for the suggested questions.
- **First question may take ~30-60s** while the local embedding model loads (downloads
  ~130 MB from Hugging Face once); afterwards answers are sub-second to a few seconds.
- The RAG index (`vulcan/data/vectordb`) ships **prebuilt and included**. The ML models
  (fault / RUL / anomaly) **train automatically on first launch** from the bundled dataset
  (~2-3 min, one-time, no internet needed) — `edith/start.sh` handles this. This keeps the
  package under the 50 MB upload cap; everything else runs out of the box.
- The dataset (`dataforge/datasets/steel-maintenance-flagship/`) is self-built and synthetic
  (physics-grounded to ISO/IEC/NEMA standards) — datacard at `SPEC/datacard.md`.
- Windows: use WSL2 (the launch scripts are bash).

## Troubleshooting

| Symptom | Fix |
|---|---|
| `pip install` fails on torch | `pip install torch --index-url https://download.pytorch.org/whl/cpu` then retry |
| Port 3000/8077 busy | `bash edith/start.sh stop`, then start again |
| Frontend shows but no data | confirm backend: `curl http://127.0.0.1:8077/api/health` |
| PDF button errors | optional dep: `playwright install chromium` |
