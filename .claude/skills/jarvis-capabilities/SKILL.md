---
name: jarvis-capabilities
description: What Jarvis already has built, wired and scheduled — integrations, agents, memory, automation, daemons, pipelines. Read this before proposing to build something, so you extend what exists instead of duplicating it.
---

# Jarvis — current capabilities

Moved out of the always-loaded `CLAUDE.md` on 2026-07-28. It was ~2,900 est.
tokens resident in every session; here only the one-line description above stays
resident and this body loads when it is actually needed.

Keep appending here as things ship — same as before, just not in context by
default.


- [x] Multi-agent orchestration via subagents (16 original + 10 Tier-1 hand-crafted + 67 Tier-2 wrapped = 93 specialists)
- [x] File-based persistent memory
- [x] Slash commands for workflows (9 workflows)
- [x] Gmail integration (Composio MCP, connected to shriva.ujjawal@gmail.com)
- [x] Google Calendar integration (Composio MCP, same account)
- [x] Google Drive integration (Composio MCP, same account)
- [x] Google Docs / Sheets / Slides / Tasks / Photos (Composio MCPs)
- [x] Gemini (no auth — Composio managed)
- [x] YouTube (Composio MCP)
- [ ] Google Meet (auth_config exists but OAuth skipped — re-link if needed)
- [ ] Google Contacts / Forms / Chat (skipped — Google blocks custom OAuth to composio.dev domain; auth_configs exist if Boss verifies domain later)
- [x] Notion integration (Composio MCP)
- [x] Telegram bridge active (@jarvis_Ujjawal_Bot, systemd: jarvis-bridge.service)
- [x] Status line (model | dir | git branch | P1 task count | IST time)
- [x] Knowledge graph via Memory MCP (Person/Project/Event/Trigger entities + relations)
- [x] Cron-based briefings (systemd user timer, 7am IST daily)
- [x] Trigger watcher (systemd user timer, every 6h — checks job-apply gap, resume gap, hackathon deadlines, alerts via Telegram)
- [x] Hackathon radar (auto-scrape Unstop + HackerEarth, alerts on new AI/ML hackathons)
- [x] News feed (RSS-based daily AI/ML digest at 06:30 IST, fed into /briefing)
- [x] Git-tracked Jarvis project (safety from accidental edits)
- [x] Prompt library: 79 professions, 361 candidates, 79 picked, 79 max-potential (`data/agent-prompts*/`)
- [x] Observability: agent-invocation logger + viewer + weekly Telegram summary
- [x] Eval framework: per-agent test cases + regression runner
- [x] Weekly self-review cron: every Sunday 19:00 IST → Telegram
- [x] Feedback collection: `/feedback` slash command + jsonl logger
- [x] Vector DB for episodic memory: Chroma + sentence-transformers, 155 chunks bootstrap, daily incremental cron
- [x] Browser automation: Playwright + 5 utility scripts + browser-agent + `/audit-site`
- [x] Voice interface: Whisper STT + Piper TTS + voice loop + Telegram voice handler
- [x] **Super-agent orchestrator (Phase 1):** `jarvis-core` FastAPI daemon using Claude Agent SDK on Max-subscription OAuth (no API key). Spawns parallel Claude Code workers via `asyncio.gather`. Persistent conversation + task state with 5-min disk sync. Telegram bridge migrated; voice + cron stay on legacy subprocess path until Phase 2.
- [x] **Browser autopilot skill (`.claude/skills/browser-autopilot/`):** Drives Chrome via Chrome DevTools MCP. Scout-then-fill pattern (ARIA-tree-based, survives DOM changes). Workflows for LinkedIn Easy Apply, Naukri quick-apply, generic form fill, login with TOTP 2FA. Tier-3 confirm on every SUBMIT. Daily caps (25/platform). Ethical pacing + session warmup + CAPTCHA-pause. Replaces need for per-platform API integrations.
- [x] **Tiered auto-mode (`.claude/skills/auto-mode/`):** 4-tier trust model. Default `autopilot` = Tier 1+2 auto, Tier 3 (irreversible) still confirms. Slash command `/auto-mode` switches modes. Audit log at `data/audits/YYYY-MM-DD.jsonl` for every Tier-2/3 action.
- [x] **Autonomous overnight Jarvis (Phase 3):** Boss declares goals via `/goal_add <desc>` → daemon decomposes via planner (single-level, JSON-validated) → background scheduler runs Tier-1/2 sub-tasks in parallel → Tier-3 sub-tasks queue as ApprovalRequest for morning nod → morning digest at 06:30 IST summarizes completed/failed/awaiting. Per-goal budget cap ($5 default) + duration cap (2h default). State persists across daemon restarts. Smoke-tested end-to-end: arithmetic goal queued → planned → executed → output verified (142, 46788) → digest rendered.
- [x] **LinkedIn growth pipeline (`scripts/linkedin/`):** Daily ICP-targeted growth automation. 4 systemd timers: morning batch (08:00 IST = search ICP + draft 20 connections + 30 messages + 1 post → Telegram approval), execute (10:00 IST = browser-autopilot drives Chrome on approved items only), afternoon mini-batch (18:00 IST = 5+10), nightly report (21:00 IST = Telegram summary). Premium Career tier: 5 InMails/month budgeted. ICP = 7 categories (AI/ML mgrs, recruiters, founders, hackathon orgs, sr devs at unicorns, intl researchers, VCs). Tier-3 confirm on every send via `/lp_approve_all`, `/lp_approve <ids>`, `/lp_reject <ids>` Telegram commands. No-repeat enforcement via `data/linkedin/contacted.jsonl`. Vercel deploy hook auto-drafts project-showcase post for next morning batch (never auto-publishes). Throttle-aware (LinkedIn restriction warning → pace 0.3x for 7 days).
- [x] **Self-growth loop MVP — Phase A (recall) + Phase B (critic)** (2026-05-13):
  - `jarvis_core/recall.py` — semantic memory recall runs before EVERY `/chat`. Pulls top-k chunks from ChromaDB via existing `EpisodicMemory.recall()`, injects as `<jarvis_memory_context>` block in the worker prompt. Skip-cases: greetings, slash cmds, msgs <30 chars. Score threshold ≥0.55, k=5, 2000-token cap. Kill-switch `JARVIS_RECALL_ENABLED=0`. Logged to `data/logs/recall.jsonl`.
  - `jarvis_core/critic.py` + `confidence.py` — silent post-response reviewer (Haiku 4.5). Four rubrics: INTENT / MEMORY / CLAIMS / TONE. If verdict=revise → ONE revision pass. Confidence tag (`verified` silent / `unverified` / `low`) attached. Skip on trivial msgs, slash cmds, tool errors. Hard timeout 8s. Kill-switch `JARVIS_CRITIC_ENABLED=0`. Logged to `data/logs/critic.jsonl`.
  - `jarvis_core/intent.py` — pre-recall classifier (Haiku 4.5) added 2026-05-15 after Ratnesh-Jarvis comparison. Classifies every `/chat` into 8 categories (task/question/feedback/strategic/emotional/correction/greeting/unknown) + priority (low/normal/high/urgent) + confidence. Hard 3s timeout. Slash commands → synthetic `task`. Tie-breakers: correction-hint upgrade, urgency-keyword override, type/priority floors. Logged to `data/logs/intent.jsonl`. Kill-switch `JARVIS_INTENT_ENABLED=0`. Spec: `specs/intent-classifier.spec.md`. Tests: `tests/test_intent.py` (24 cases). Memory files now carry `type:`/`zone:` frontmatter (foundation for future lifecycle engine). Architecture roadmap (sentinels/lifecycle/event-bus/dashboard) in `specs/architecture-roadmap.md`.
  - Wired into `jarvis_core/daemon.py` `/chat` (intent + recall in parallel → worker → critic). `ChatResponse` carries new fields: `confidence`, `memory_hits`, `revised`, `intent`, `priority`.
  - Specs-driven: `specs/recall.spec.md` + `specs/critic.spec.md` (jarvis-main-style discipline adopted; `specs/_template.spec.md` is the template for future components).
  - Unit tests: `tests/test_recall.py` (12 cases) + `tests/test_critic.py` (16 cases). Eval cases: `data/evals/recall/test_cases.jsonl` + `data/evals/critic/test_cases.jsonl`.
  - **Roadmap (post-MVP):** Phase C auto-capture (every 30min), Phase D reasoning trigger (every 4h), Phase E weekly self-growth loop (Sun 20:00 IST, Tier 1+2 auto-apply / Tier-3 confirm), Phase F spec migration + eval baseline regression check.
- [x] **Hackathon War Room — full 5-phase multi-agent workflow** (2026-05-13):
  - **Spec:** `specs/hackathon-war-room.spec.md` — Input Contract (11 required fields), 5-phase execution flow, anchored 1-10 scoring rubric across 5 dimensions, YAML handoff schema, verification/[unverified] tagging, conflict surfacing, reject-power critique.
  - **5 new specialised agents** in `.claude/agents/`: `company-tech-stack-researcher`, `company-ai-ml-researcher`, `hackathon-intel-researcher`, `mandatory-tech-deep-dive`, `hackathon-critique`.
  - **Phase 1 (7 parallel research agents)**: 5 company (research-analyst + tech-stack + ai-ml + investigative-journalist + librarian-research) + 2 hackathon (hackathon-intel + mandatory-tech-deep-dive).
  - **Phase 2 (3 agents → 10 scored problems)**: product-manager + strategy-consultant + hackathon.
  - **Phase 3 (4 agents × N shortlisted)**: backend + frontend/mobile + ml + data-engineer (+ devops/security/statistician on demand).
  - **Phase 4**: hackathon-critique with reject-power (composite < 6.5 → loops back).
  - **Phase 5**: product-manager + technical-writer + pitch-deck-consultant + qa-test-engineer → final War Room Document (19 sections per spec §13).
  - **Workflow runner** `scripts/hackathon_warroom.py` — state machine, canonical_state.json, checkpoint pauses, resume across sessions.
  - **Skill** `.claude/skills/hackathon-war-room/SKILL.md` — operating contract loaded when activated.
  - **Template** `data/hackathons/_template/` — per-hackathon folder scaffold.
  - **Telegram cmds** added to bridge: `/wr_start <slug>`, `/wr_status [slug]`, `/wr_run <slug>`, `/wr_checkpoint <slug> <approve|drill|skip>`, `/wr_pick <slug> <ids>`.
  - **Active execution:** Tata Steel — `data/hackathons/tata-steel-2026/` initialised, awaiting Input Contract.
- [x] **Self-growth loop — Phase C/D/E/F shipped** (2026-05-13):
  - **Phase C** `scripts/auto_capture.py` — every 30 min via `jarvis-auto-capture.timer`. Reads new turns from `data/logs/conversations.jsonl` (now written by daemon `/chat`), batches by user (max 8 turns), Haiku-summarises into atomic facts, ingests to ChromaDB. Idempotent via content hash dedup. Spec: `specs/auto-capture.spec.md`.
  - **Phase D** `scripts/reasoning_trigger.py` — every 4h via `jarvis-reasoning-trigger.timer`. LLM-driven state synthesis across feedback / audits / markers / tasks / LinkedIn / hackathons. Sends Telegram nudge only on `signal_level ∈ (medium, high)`. 12-hour per-topic cooldown. Spec: `specs/reasoning-trigger.spec.md`.
  - **Phase F** `scripts/eval_baseline.py` — publishes `data/evals/baseline.md` + `baseline.json` by aggregating latest reports. `--check` flag exits non-zero on >5pp pass-rate drop per agent. Used as quality gate by Phase E. Spec: `specs/eval-runner.spec.md`. Backfilled specs: `jarvis-core-daemon`, `episodic-memory`, `telegram-bridge`.
  - **Phase E** `scripts/self_growth_weekly.py` — Sunday 20:00 IST via `jarvis-self-growth.timer`. LLM (Sonnet) synthesises 3-5 capability-change proposals from weekly signals. Enforces `_SAFE_PATTERNS_TIER1/2` allow-list + `_FORBIDDEN_PATTERNS` (jarvis_core, bridge, .mcp.json, daemon/critic/recall scripts → always Tier-3). **Tier 1+2 auto-apply** within safe paths; **Tier-3 queues as local approval files** at `data/growth/awaiting_approval/`. Eval-baseline regression gate suspends auto-apply for the week. Git snapshot before apply. Telegram digest summarises week + applied + awaiting. `--apply-approved` mode processes Boss-approved Tier-3s. Spec: `specs/self-growth.spec.md`.
  - **Telegram commands** added to bridge: `/growth_list`, `/growth_approve <id> [note]`, `/growth_reject <id> [reason]`.
  - **All tests green** (35/35 pytest). Live dry-runs verified: auto_capture (0 turns clean exit), reasoning_trigger (collected real signals across 7 sources), eval_baseline (published + --check = 0 regressions), self_growth_weekly --collect-only (real feedback + recall digest visible).
  - **Activate** (Boss must run manually — Tier-2 systemd action):
    ```bash
    systemctl --user daemon-reload
    systemctl --user enable --now jarvis-auto-capture.timer jarvis-reasoning-trigger.timer jarvis-self-growth.timer
    systemctl --user restart jarvis-bridge   # pick up /growth_* commands
    systemctl --user restart jarvis-core     # pick up conversation log writer
    ```

