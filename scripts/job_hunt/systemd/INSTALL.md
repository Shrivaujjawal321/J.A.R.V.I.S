# Jarvis Job-Outreach Engine — install

Daily at 09:00 IST: send follow-ups due today → source fresh AI/ML India targets
(headless Claude) → verify deliverability → send personalized cold emails
(bounce-safe only, ~25/day) → log → Telegram report.

## Prereqs (already done 2026-06-20)
- `.env` has `GMAIL_ADDRESS`, `GMAIL_APP_PASSWORD`, `GMAIL_SENDER_NAME`
- `data/job-hunt/contacted.jsonl` seeded (dedupe + follow-up state)

## Install
```bash
mkdir -p ~/.config/systemd/user ~/Documents/J.A.R.V.I.S./data/logs
cp ~/Documents/J.A.R.V.I.S./scripts/job_hunt/systemd/jarvis-jobhunt.* ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now jarvis-jobhunt.timer
systemctl --user list-timers | grep jobhunt   # verify scheduled
```

## Manual run / test
```bash
cd ~/Documents/J.A.R.V.I.S.
.venv/bin/python -m scripts.job_hunt.daily_engine --dry-run     # no send
.venv/bin/python -m scripts.job_hunt.daily_engine               # live run now
.venv/bin/python -m scripts.job_hunt.daily_engine --limit 25    # cap new sends
```

## Tuning (env vars)
- `JH_DAILY_CAP` (default 25) — max new cold emails/day
- `JH_PACING_SEC` (default 20) — seconds between sends

## Disable
```bash
systemctl --user disable --now jarvis-jobhunt.timer
```
