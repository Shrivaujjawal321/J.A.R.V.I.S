# Jarvis WhatsApp Gateway

A **name-triggered, sandboxed public help bot** on Boss's **personal** WhatsApp number.

Jarvis watches all incoming DMs like an eye — but stays **completely silent** unless
a message addresses it by name (`jarvis` / `hey jarvis` / `hello jarvis`). When named,
it routes the message to an **isolated public worker** and replies — signed as Jarvis,
from Boss's number — so it's always clear whether *Boss* messaged or *Jarvis* did.

## What it is NOT
This is **not** your private Jarvis. The public worker (`public_worker.py`) runs with:
- `allowed_tools = []` — no Read/Write/Bash/WebFetch/MCP. Text only.
- `cwd = whatsapp/sandbox/` (empty) — can't reach the Jarvis repo.
- `setting_sources = []`, `mcp_servers = {}` — no `.claude/`, no CLAUDE.md, no Gmail/Calendar/Notion/Drive/browser.
- A hardened system prompt with **zero Boss data** that refuses owner info, secrets, actions, impersonation.
- No private memory / ChromaDB recall.

So even a jailbroken prompt has nothing to reach.

## Safety layers (in order)
1. **name-gate** — `/jarvis/i` must match, else silent (no LLM call)
2. **rate-limit** — per-sender (4/min, 30/hr, 60/day) + global (30/min) + cooldown after 50 replies
3. **blocklist** — `state/blocklist.json` (sha256 of sender)
4. **input prefilter** — owner-info / secret / injection probe → instant refusal, no model call
5. **sandboxed worker** — empty tools, isolated cwd, hardened prompt
6. **output canary** — strips Boss's email/phone (from `owner_pii.json`) if it ever appears; CRITICAL-logs
7. **signature** — every reply prefixed `🤖 Jarvis — Ujjawal ka AI assistant`

## Setup

```bash
# 1. deps already installed (whatsapp/node_modules). If not:
cd whatsapp && npm install && cd ..

# 2. (optional) add Boss's phone to the PII canary so it can never leak:
#    edit whatsapp/owner_pii.json → "phones": ["+9198XXXXXXXX"]

# 3. First run — scan the QR with your phone (WhatsApp → Linked Devices → Link a Device):
node whatsapp/gateway.mjs
#    Session saves to whatsapp/auth_state/. Ctrl-C after you see "✅ … connected".

# 4. Run as a background service (survives reboots):
cp whatsapp/jarvis-whatsapp.service ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now jarvis-whatsapp
systemctl --user status jarvis-whatsapp
```

> The QR scan (step 3) is **interactive and one-time** — only Boss can do it (needs his phone).
> After that, the session persists and the service starts headless.

## Tuning
- **Trigger word / signature / delays / rate limits** → `config.json`
- **Owner PII canary** → `owner_pii.json` (gitignored)
- **The public persona / refusal rules** → `SYSTEM_PROMPT` in `public_worker.py`
- **Block a sender** → add `"<sha256-16>": {"reason": "..."}` to `state/blocklist.json`

## Logs
- Security events (hash-only, no message bodies): `state/security.jsonl`
- Service stdout/stderr: `data/logs/jarvis-whatsapp.log`

## Stop / reset
```bash
systemctl --user disable --now jarvis-whatsapp     # stop
rm -rf whatsapp/auth_state                          # full logout — re-scan QR to relink
```

## ⚠️ Notes
- **Unofficial** (Baileys reverse-engineers WhatsApp Web). Reply-only + named-trigger is the
  lowest-risk automation category (empirically <2% ban over 12 months), but ban risk is non-zero.
- Pinned to Baileys **6.7.21** (stable). v7 is still RC as of 2026-06.
- Runs alongside the Python Telegram bridge as a separate service — no conflict.
