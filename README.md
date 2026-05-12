# Jarvis — Personal AI Agent System

Multi-agent AI assistant I've built over ~6 weeks. Runs on Claude Max subscription (no developer API key) via Claude Agent SDK + Claude Code subagents + MCP servers. Live on my laptop as a 24/7 daemon + Telegram bot.

## Latest Builds (May 2026)

- 🎯 **Autonomous overnight goal pursuit (Phase 3)** — declare a plain-English goal via Telegram; daemon decomposes via JSON-schema-validated planner, spawns parallel Claude Code workers, gates Tier-3 actions for morning approval, sends 06:30 IST digest. Per-goal budget caps + duration limits + decomposer depth limits enforce safety. End-to-end smoke-tested. [`jarvis_core/`](jarvis_core/)
- ⚡ **Super-agent orchestrator daemon (Phase 1)** — long-running FastAPI service on `127.0.0.1:8765` using Claude Agent SDK on Max-subscription OAuth (`CLAUDE_CODE_OAUTH_TOKEN` — no API key). Spawns parallel workers via `asyncio.gather`. Persistent conversation + task state with 5-min disk sync + atomic writes. Multi-turn session resumption verified. [`jarvis_core/daemon.py`](jarvis_core/daemon.py)
- 🌐 **Browser autopilot skill (Phase 2)** — drives Chrome via Chrome DevTools MCP. Scout-then-fill pattern uses ARIA accessibility tree (survives DOM cosmetic changes). Workflows for LinkedIn Easy Apply, Naukri quick-apply, generic form fill, login with TOTP 2FA via `pyotp` + OS keychain. Tier-3 confirm on every submit. Daily caps + session warmup + CAPTCHA pause + cool-down enforcement. [`.claude/skills/browser-autopilot/`](.claude/skills/browser-autopilot/)
- 🔐 **Tiered trust framework** — 4-tier model (auto / auto+log / confirm / refused) with mode switcher (manual / autopilot / fullauto) and append-only JSONL audit log per action. Irreversible operations gate even in fullauto. [`.claude/skills/auto-mode/`](.claude/skills/auto-mode/)
- 🧠 **93 specialist subagents** — 10 hand-crafted (ml-engineer, security-engineer, product-manager, devops-sre, technical-writer, ...) + 67 wrapped from a 79-profession prompt library (curated from GitHub, evaluated, picked, enhanced to max-potential by a 6-parallel-instance enhancer agent). + 16 Jarvis-native (resume, hackathon, voice, browser, ...). [`.claude/agents/`](.claude/agents/)
- 🎙️ **Voice loop** — Whisper STT + Piper TTS, full duplex over Telegram voice messages. [`bridge/voice_handler.py`](bridge/voice_handler.py)
- 📚 **Episodic memory** — Chroma vector DB + sentence-transformers, 155-chunk bootstrap, daily incremental ingest. `/recall` slash command for semantic memory search. [`scripts/episodic_memory.py`](scripts/episodic_memory.py)
- 📱 **Telegram bridge (live, systemd)** — `@jarvis_Ujjawal_Bot` — text + voice + slash commands. Falls back to direct subprocess if daemon is down. [`bridge/telegram_bridge.py`](bridge/telegram_bridge.py)

## How it works at runtime

```
You ──Telegram──> bridge ──HTTP──> jarvis-core daemon ──Claude Agent SDK──> N parallel Claude Code workers
                                          │                                          │
                                          ▼                                          ▼
                                  Persistent state                       Subagents + MCP servers
                                  (5-min disk sync)                      (Gmail, Calendar, Notion,
                                                                          Chrome DevTools, ...)
```

Stack: **Python 3.12 · FastAPI · Pydantic v2 · asyncio · Claude Agent SDK · Chroma · sentence-transformers · Whisper · Piper · Playwright · Telegram Bot API · systemd**

## Original setup guide (build your own)

The original starter-pack section that follows shows how someone else can clone + customize this for their own use.

## Architecture

```
You ──> Claude Code (Manager) ──> Specialist Subagents ──> MCP Servers ──> Real Integrations
              │                              │
              ▼                              ▼
      CLAUDE.md (context)        data/memory/ (persistent state)
```

## Quick Start (30 minutes)

### 1. Copy this folder to your projects directory

```bash
cp -r jarvis-starter ~/projects/jarvis
cd ~/projects/jarvis
```

### 2. Initialize git

```bash
git init
git add .
git commit -m "Initial Jarvis setup from starter pack"
```

### 3. Customize `data/memory/` files

Edit these files with YOUR information:
- `data/memory/facts.md` — Your name, location, work, family
- `data/memory/preferences.md` — How you like to communicate
- `data/memory/projects.md` — What you're working on
- `data/memory/people.md` — Important people in your life
- `data/memory/habits.md` — Your daily routines

These are loaded into Jarvis's context every session.

### 4. Test in Claude Code

```bash
claude
```

Try:
```
> Read CLAUDE.md and data/memory/facts.md. Introduce yourself based on what you know about me.
> /plan-day
> Use research-agent to find latest AI agent frameworks 2026
```

### 5. Set up MCP servers (when ready)

See `.mcp.json` — uncomment the servers you want to use. Most need:
- Gmail — OAuth credentials
- Google Calendar — same OAuth
- Notion — integration token
- Memory — works out of the box

### 6. Set up Telegram bridge (Week 2)

```bash
cd bridge
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your TELEGRAM_BOT_TOKEN
python telegram_bridge.py
```

Now message your bot — yeh tumhare Jarvis se Telegram pe baat karayega.

### 7. Set up cron jobs (Week 2-3)

```bash
crontab -e
# Paste contents from scripts/crontab.example
```

## Folder Structure

```
jarvis/
├── CLAUDE.md                    # Project context (auto-loaded)
├── .claude/
│   ├── agents/                  # Specialist subagents
│   │   ├── email-agent.md
│   │   ├── calendar-agent.md
│   │   ├── research-agent.md
│   │   ├── task-agent.md
│   │   ├── code-agent.md
│   │   ├── learning-agent.md
│   │   └── memory-agent.md
│   ├── commands/                # Slash commands (workflows)
│   │   ├── briefing.md          # /briefing — morning summary
│   │   ├── triage.md            # /triage — inbox cleanup
│   │   ├── weekly-review.md     # /weekly-review
│   │   └── plan-day.md          # /plan-day — daily planning
│   └── settings.json            # Hooks and configuration
├── .mcp.json                    # MCP server config
├── data/
│   ├── memory/                  # Persistent facts about you
│   ├── conversations/           # Chat logs
│   ├── briefings/               # Daily briefings archive
│   ├── notes/                   # Your notes
│   └── tasks.md                 # Task list
├── bridge/                      # External interface (Telegram, etc.)
└── scripts/                     # Cron jobs, setup scripts
```

## How It Works

**Manager (Claude Code main session):**
- Reads CLAUDE.md and memory files at session start
- Decides which subagent handles each request
- Synthesizes results from multiple subagents

**Specialist subagents:**
- Each has focused expertise (email, calendar, etc.)
- Independent context windows (no pollution)
- Limited tool access (safety)
- Can be invoked automatically or explicitly

**Slash commands:**
- Multi-step workflows
- `/briefing`, `/triage`, etc.
- Coordinate multiple subagents

**MCP servers:**
- Real integrations (Gmail, Calendar, Notion, Memory)
- Same tools available to all subagents (configurable per agent)

**Bridge service (optional):**
- Listens for external events (Telegram messages, emails)
- Spawns Claude Code in headless mode
- 24/7 operation

## Daily Workflow

**Morning (automatic via cron):**
- 7am: `/briefing` → digest sent to Telegram

**Throughout day (interactive):**
- Open terminal: `claude`
- Talk to Jarvis: "draft reply to Rohit", "what's free tomorrow afternoon"
- Or message your Telegram bot from phone

**Evening:**
- Review tasks: `Show me today's pending tasks`
- Plan tomorrow: `/plan-day`

**Weekly (Sunday evening cron):**
- 7pm Sun: `/weekly-review` → summary of week, upcoming priorities

## Customization

Every file in this starter is meant to be customized. Make Jarvis YOUR Jarvis:

- Tone and personality → `CLAUDE.md`
- What it knows about you → `data/memory/`
- What specialists you have → add files to `.claude/agents/`
- What workflows → add files to `.claude/commands/`
- What integrations → edit `.mcp.json`

## Adding Capabilities Later

| Want | How |
|------|-----|
| New skill | Add subagent file to `.claude/agents/` |
| New workflow | Add slash command to `.claude/commands/` |
| New integration | Add MCP server to `.mcp.json` |
| New automation | Add cron job to `scripts/crontab.example` |

## Troubleshooting

**Subagents not detected:**
```bash
# Inside claude session
/agents
```
Should list all 7 agents. If not, restart Claude Code.

**MCP server failing:**
```bash
# Check MCP status inside claude
/mcp
```

**Memory not loading:**
Make sure CLAUDE.md references `data/memory/` files explicitly.

## Next Steps

After setup works:
1. Use it daily for a week — note what's missing
2. Add custom subagents for your specific needs
3. Add Gmail/Calendar MCP servers
4. Set up Telegram bridge
5. Schedule cron jobs

**Build incrementally. Each capability you add compounds.**

---

Built with Claude Code subagents. Subscription only. ₹0 ongoing cost.
