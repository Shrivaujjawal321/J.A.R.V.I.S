# THE EDITH — Agentic Maintenance Intelligence

A local, dark Stark-HUD industrial-maintenance copilot for a steel plant, running on the
**v2 flagship dataset**. EDITH powers and orchestrates everything: live condition monitoring,
threshold alerting with plain-language reasons, grounded diagnosis / RCA / RUL / risk /
prioritized actions in the problem-statement format, and shareable + downloadable reports.

- **Brain:** Claude Max subscription via `claude-agent-sdk` (OAuth token, **no API key**), with an
  instant grounded-deterministic fast path (RAG + ML + equipment spine) as the default for snappy UX.
  Set `EDITH_LLM_PROVIDER=subscription` for Claude-deep reasoning (slower).
- **Engine reuse:** the proven VULCAN cores (hybrid RAG `bge-small + FlashRank + Chroma`,
  LightGBM RUL, IsolationForest anomaly, threshold alerting, report builder, faithfulness gate).
- **Stack:** FastAPI backend · Next.js 16 + React 19 + Tailwind 4 + uPlot frontend.

## Run (one command)

```bash
# one-time: pip install -r edith/backend/requirements.txt   (+ `playwright install chromium` for PDF)
bash edith/start.sh          # backend :8077 + frontend :3000
bash edith/start.sh stop     # stop both
```

Or manually (two terminals): `cd edith/backend && bash run.sh` · `cd edith/frontend && npm install && npm run build && npm run start`.

**Submission artifacts:** `SUBMISSION_DOCUMENT.md` (the PS §9 document) · `EVAL_RESULTS.md`
(measured end-to-end accuracy on the 250-item gold eval) · `demo/` (screen recording) ·
`make_submission_zip.sh` (builds the HackerEarth ZIP).

Open **http://localhost:3000**. The cockpit auto-focuses `HSM.F3.WR.BRG01` and starts streaming
the real historian; click any asset in the left strip to focus it.

## What you get (maps to the Tata PS)
- **Live monitoring** — 15-asset health strip + focused asset with animated uPlot sensor graphs,
  warning/alarm threshold bands; the line turns its status colour and the panel glows on breach.
- **Real-time alerts** — when a sensor crosses a threshold an alert card appears stating *"<sensor>
  = <value> crossed the <warning/alarm> threshold (<limit>)"*, with resolution steps + predicted
  impact (on the first ALARM EDITH hands off a full grounded diagnosis).
- **Ask EDITH** — PS-format grounded answer: diagnosis · probable root cause · RUL · risk · prioritized
  actions · recommendation. Each heading shows a short brief + an **expand** for the enhanced brief,
  with inline citations. Asset-aware (uses the focused asset).
- **Reports** — `/report/{id}` shareable web view + **downloadable branded PDF** (`/api/report/{id}/pdf`).

## API (backend, 8077)
`GET /api/health` · `GET /api/assets` · `GET /api/asset/{id}` · `GET /api/stream/{id}` (SSE) ·
`POST /api/ask` · `GET /api/predict/{id}` · `POST /api/report` · `GET /api/report/{id}` ·
`GET /api/report/{id}/pdf` · `GET /api/alerts`

## Notes
- Synthetic dataset — site calibration required before production alarming.
- Rebuild artifacts if the dataset changes: `python -m vulcan.rag.store` (RAG corpus) and
  `python -m vulcan.ml.models` (ML), both with `VULCAN_DATASET_ROOT` set to the flagship dataset.
