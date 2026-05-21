# Installing the LinkedIn pipeline systemd timers

Run once from `~/Documents/J.A.R.V.I.S.` as your normal user (not root):

```bash
mkdir -p ~/.config/systemd/user
mkdir -p ~/Documents/J.A.R.V.I.S./data/logs

cp scripts/linkedin/systemd/jarvis-linkedin-*.{service,timer} ~/.config/systemd/user/

systemctl --user daemon-reload

systemctl --user enable --now jarvis-linkedin-morning.timer
systemctl --user enable --now jarvis-linkedin-execute.timer
systemctl --user enable --now jarvis-linkedin-afternoon.timer
systemctl --user enable --now jarvis-linkedin-report.timer

# Verify
systemctl --user list-timers | grep linkedin
```

## Schedule (UTC → IST conversion)

| Timer | UTC | IST | What it does |
|---|---|---|---|
| morning  | 02:30 | 08:00 | Search ICP, draft batch, Telegram preview to Boss |
| execute  | 04:30 | 10:00 | Run executor on Boss-approved items |
| afternoon | 12:30 | 18:00 | Smaller mini-batch (5 conns + 10 msgs) |
| report   | 15:30 | 21:00 | Nightly Telegram summary |

`RandomizedDelaySec` adds 5–10 min jitter to look more human.

## Restart bridge so /lp_* commands work

After installing, restart the Telegram bridge so it picks up the new handlers:

```bash
systemctl --user restart jarvis-bridge
```

## Pre-flight checklist (BEFORE first morning run)

- [ ] Chrome is open with `--remote-debugging-port=9222 --user-data-dir=~/.cache/jarvis-chrome`
- [ ] Boss is logged into LinkedIn in that Chrome window
- [ ] `data/linkedin/icp.json` has been reviewed by Boss (geo + companies look right)
- [ ] `.env` has TELEGRAM_BOT_TOKEN and ALLOWED_USER_IDS
- [ ] Test the helpers manually:
  ```bash
  cd ~/Documents/J.A.R.V.I.S.
  .venv/bin/python -c "from scripts.linkedin import _telegram_notify; print(_telegram_notify.send('LP test ✅'))"
  ```

## Disable / pause

```bash
# pause for a few days
systemctl --user stop jarvis-linkedin-morning.timer
systemctl --user stop jarvis-linkedin-execute.timer

# permanently disable
systemctl --user disable --now jarvis-linkedin-morning.timer
systemctl --user disable --now jarvis-linkedin-execute.timer
systemctl --user disable --now jarvis-linkedin-afternoon.timer
systemctl --user disable --now jarvis-linkedin-report.timer
```

## Monitoring

```bash
# Live logs
journalctl --user -u jarvis-linkedin-morning -f

# Last morning run
journalctl --user -u jarvis-linkedin-morning -n 200

# All LinkedIn audits today
cat ~/Documents/J.A.R.V.I.S./data/audits/$(date +%F).jsonl | grep linkedin_executor
```
