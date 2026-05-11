# Jarvis — Personal AI Agent (Claude Code Subagents Edition)

Subscription-only setup. No API keys needed. Built on Claude Code + subagents + MCP.

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
