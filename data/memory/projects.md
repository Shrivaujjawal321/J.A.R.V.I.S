---
type: fact
zone: warm
last_reviewed: 2026-05-15
---

# Active Projects

> What I'm currently working on. Updated as projects evolve.
> **Memory type**: `fact` — current-state snapshot, decays fast as projects evolve.
> **Zone**: `warm` — high-churn; expect frequent edits; auto-prune dormant entries.

## 🟢 Active

### ⭐ McpIndex — Hackathon Flagship (NEW, LIVE)
- **Goal:** Curated, scored, searchable MCP server discovery — "the npmjs.com for Model Context Protocol"
- **Status:** LIVE in production, 8 Day milestones done in 2 calendar days
- **Live URL:** https://mcpindex-nu.vercel.app
- **Project dir:** `/home/ujjwal/Documents/mcp-hub/` (separate from Jarvis, own git repo)
- **Hackathon:** DevNetwork AI+ML 2026 — deadline 2026-05-28 10:00 AM PT
- **Started:** 2026-05-11
- **Stack:** Next.js 16 + Tailwind 4 + shadcn + Neon Postgres + pgvector + Gemini Flash/embedding + Vercel
- **Stats:** 1,532 MCP servers indexed, 6-dim quality scoring, hybrid semantic+keyword search
- **Chosen problem (Concept criterion):** "20K MCP servers exist, 90% broken, 140K devs/month with zero quality signal." See `/home/ujjwal/Documents/mcp-hub/HACKATHON-PROBLEM.md` for full breakdown.
- **Sponsor strategy:** Primary = Overall Grand Prize ($12.5K). Skip Perfect Corp (wrong vertical). TrueFoundry $1.5K = optional 2-3 day adapter.
- **Remaining work:** `pnpm db:embed --resume` (483 servers tomorrow when quota resets) → record 90s demo → paste DEVPOST.md → submit
- **Files of interest:**
  - mcp-hub/SPEC.md
  - mcp-hub/HACKATHON-PROBLEM.md ⭐ (problem analysis, judging mapping, sponsor fit, judge Q&A prep)
  - mcp-hub/DEVPOST.md (submission writeup)
  - mcp-hub/DEMO-SCRIPT.md (90s narrator script)
  - mcp-hub/ARCHITECTURE.md
  - mcp-hub/DEPLOY.md
- **Cross-references in Jarvis:**
  - `data/notes/hackathon-developerweek-research-2026-05-11.md` (DevNetwork format)
  - `data/notes/hackathon-winning-patterns-2026-05-11.md` (2026 winners)
  - `data/notes/hackathon-ideas-research-2026-05-11.md` (idea menu)
  - `data/notes/devnetwork-sponsor-challenges-2026-05-12.md` (live sponsor enumeration + fit matrix)

### 1. Jarvis — Personal AI Agent
- **Goal:** Build a personal AI assistant on Claude Code + subagents + MCP that handles email, calendar, research, learning, code, tasks
- **Status:** Foundation setup in progress (memory files being filled)
- **Started:** 2026-05-10
- **Stack:** Claude Code + subagents + MCP + (planned) Telegram bridge
- **Next step:** Finish memory files → fix `.mcp.json` Linux paths → test subagent loop → add Gmail/Calendar MCP

### 2. Portfolio Site
- **URL:** https://ujjawal-shrivastav.vercel.app/
- **Goal:** Personal portfolio for job hunt + freelancing credibility
- **Status:** Live, deployed on Vercel
- **Next step:** Audit against current AI/ML hiring expectations — does it showcase what recruiters look for in 2026?

### 3. Enginerd — Education Platform
- **URL:** https://enginerd.vercel.app/
- **Goal:** Online education platform
- **Status:** Live but feels "ordinary, not 2026" per Boss's own assessment — needs modern AI-era UX redesign
- **Blocker:** Design/UX feels dated; not market-ready
- **Next step:** Define what "2026 education platform" means concretely — pick 2-3 reference products (Cursor, Perplexity, ChatGPT Edu, etc.) to study UX patterns from

### 4. Job Hunt — AI/ML Roles
- **Status:** Actively applying on LinkedIn + Naukri.com
- **Critical blocker:** **Resume isn't getting shortlisted** — recruiters aren't even reaching out
- **Diagnosis (hypothesis):** Resume probably failing ATS keyword filters and/or not signaling AI/ML readiness clearly enough for a fresh grad
- **Next step:** P1 — overhaul resume. ATS-friendly format + project-first narrative + concrete AI/ML keywords + measurable outcomes per project. Consider: should be a separate session focus.

### 5. Freelancing (aspirational, blocked)
- **Goal:** Earn money via freelance work
- **Status:** Not started — no Upwork/Fiverr/Contra profile yet
- **Blocker (self-reported):** "Mere project perfect nahi hai" — perfectionism block
- **Reality check:** First freelance clients come from good-enough portfolio + outreach, not perfect portfolio. Worth challenging this block when Boss is ready.
- **Next step:** Decide minimum-viable freelance profile — pick 2-3 strongest existing projects (Enginerd + portfolio site + Jarvis once it's working), write tight case studies, list on one platform first

## 🟡 On Hold

(Nothing currently)

## ✅ Completed (last 90 days)

- B.Tech CS-AIML graduation (2025)

## 💭 Ideas / Someday

- (Add as they come up)

---

**Last updated:** 2026-05-10

**How Jarvis uses this:** Surfaces relevant project context, tracks progress, suggests next steps, identifies blockers, celebrates wins.

**Boss's biggest current pain point:** Resume not getting shortlisted. Treat this as the highest-leverage problem to solve — every other project benefits if income/job is unblocked.
