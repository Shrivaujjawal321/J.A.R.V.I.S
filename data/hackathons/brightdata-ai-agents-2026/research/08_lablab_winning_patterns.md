# lablab.ai Past Hackathon Winners — Pattern Extraction (2024-2026)

## Quick Answer

Winning lablab.ai projects share three non-negotiables: **sponsor tech used for the hardest/most valuable step (not bolt-on)**, **"agentic" framing throughout**, and **quantified pain in first 10 seconds**. UI polish + README hygiene are tie-breakers; problem framing is the decider.

---

## Winner Table (Selected, 2024-2026)

| Project | Hackathon | Prize | Why It Won |
|---------|-----------|-------|------------|
| **Memoiz** | Redis GenAI | 1st | Deep Redis integration (vector search + feature store), emotional use case |
| **RedAGPT** | Redis GenAI | 2nd | Clear B2B value, Redis as feature store |
| **VHeal AI** | RAISE 2025 Vultr track | Winner | Agentic hospital discharge — RAISE judged on multi-agent |
| **AURA** | RAISE 2025 Vultr | Winner | Deployed on sponsor cloud with enterprise framing |
| **Emergency Triage Automation** | AI Genesis 2025 | 1st ($3K) | **Solo winner** — polish beats team size; life-or-death = max attention |
| **NexusGuardAI** | IBM watsonx Orchestrate | Winner | Deep watsonx Orchestrate (5-system integration) |
| **DORA Gatekeeper** | IBM watsonx | Winner | 5-system integration via watsonx (Box + Granite + ERP + Outlook + Vector DB) |
| **Tachiwin** | Llama Impact LATAM | 1st ($3K) | Social impact + underserved market (indigenous Mexican languages) |
| **Bridge-PA** | AI Agent Olympics, Milan AI Week 2026 | Winner | Days→minutes (quantified), Vultr deployment |
| **MenuTaste** | AI Agent Olympics | Winner | Featherless + Vultr stack, niche B2B, exportable output |
| **SOC-CERT** | DEV × n8n × BrightData 2025 | 1st ($1K) | n8n + BrightData scheduled loop, 99.8% uptime |
| **BrandGuard AI** | DEV × n8n × BrightData | 2nd ($1K) | Multi-agent + BrightData social scrape (sponsor sweet spot) |
| **Release Sentinel** | DEV × n8n × BrightData | 4th ($1K) | 18+ vendor scrapes every 6h — exact hardest problem |
| **Pixie** | DEV × n8n × BrightData | 5th ($1K) | Voice → scrape → PRD → prototype on Lovable |
| **LaunchPilot AI** | lablab (BrightData-adjacent) | Showcased | BrightData SERP + Claude → GTM strategy |

---

## Key Findings

### 1. "Agentic" framing mandatory in 2025-2026
RAISE 2025 explicitly judged on "how effectively it embraced advanced multi-agent systems." Every post-mid-2025 winner has "agent," "agentic," or "autonomous" in name or first pitch sentence. **Not optional.**

### 2. Sponsor tech for hardest step, not easiest
- IBM watsonx: losers called one API; winners orchestrated 5 systems
- BrightData: losers did one ad-hoc scrape; winners built **scheduled autonomous refresh loop** every 6h or daily

### 3. Problem domain determines score ceiling
Healthcare + security + enterprise compliance consistently win — judges calculate ROI immediately. B2C/consumer can win (Memoiz, Tachiwin) with emotional/social-impact angle overriding TAM question.

### 4. Solo builders can win
AI Genesis 2025 1st = 1 person. All 5 BrightData/n8n challenge winners were solo. Platform doesn't favor large teams.

### 5. Demo shows agent working, not slides about it
lablab official: "Show happy path, jump to Magic Moment." Wow moment on screen before minute 1 in every winning description.

### 6. UI polish differentiates top 20% from middle
Raw Streamlit = bottom 40%. Winners add **real-time agent-thinking log panel** showing autonomous step execution. This is the 2025-2026 "I'm not a wrapper" signal.

---

## Sponsor-Tech Depth Matrix

| Event | Surface (losers) | Deep (winners) |
|-------|------------------|----------------|
| IBM watsonx | One text-gen API | 5-system orchestration via Orchestrate |
| Redis GenAI | Redis as cache | Vector DB + feature store + pub/sub |
| Llama Impact | Llama as default LLM swap | Domain-specific RAG / Llama-unique problem |
| BrightData + n8n | One manual scrape | Scheduled autonomous loop + anti-bot + structured → agent decision |
| Vultr | Deployed on Vultr | Agent runtime + latency benchmarks + architecture diagram |

---

## Demo Video Analysis

**Hard constraint:** 5-min cap, under 300MB.

| Duration | Signal |
|----------|--------|
| < 2 min | Underbuilt |
| 2:30-3:30 | Solo / 2-person sweet spot |
| 3:30-4:30 | 3-4 person team sweet spot |
| 4:30-5:00 | Only if every second live demo |

**Inferred winning structure:**
- 0:00-0:30: Cold open with quantified pain, no intro
- 0:30-0:45: Product name + one-line pitch
- 0:45-3:30: Live demo, agent executing multi-step autonomously
- 3:30-4:15: Architecture slide (30s max)
- 4:15-4:45: Impact + roadmap (bullets)
- 4:45-5:00: GitHub URL + deployed URL + names

**Style:** Human voiceover always. AI voiceover = red flag per lablab guide.

---

## README / GitHub Patterns

**Must-haves:**
1. Logo + 1-line description above fold
2. Demo video thumbnail (YouTube embed / GIF)
3. 3-command setup: `git clone` → `pip install` → `python app.py`
4. `.env.example` with all keys named
5. Architecture diagram (Mermaid or PNG)
6. Tech stack badges (shields.io)
7. MIT license

**BrightData-specific:** README leads with "what live data is fetched + why freshness matters." `.env.example` shows BrightData config. Architecture diagram labels BrightData as **trust/freshness layer** not generic HTTP client.

**Anti-patterns in losing repos:** No README beyond auto-template, secrets in main branch, deployed URL 404 at judging, 500-line `main.py` with no structure.

---

## Winning Playbook for BrightData × lablab 2026

**Framing:**
- Title contains "Agent" or "Agentic" explicitly
- Problem exists where stale data = wrong decision (monitoring, intel, compliance, arbitrage)
- B2B with stated dollar cost
- BrightData for hardest step (anti-bot, freshness, scale) not convenience

**Technical:**
- Multi-agent graph (LangGraph preferred, CrewAI acceptable)
- ≥2 BrightData tools (SERP + Unlocker, or MCP + Browser)
- Autonomous scheduled refresh loop, not user-triggered
- Live URL at submission (Render / Railway / Vercel / Docker)

**Demo (3:30-4:00):**
- Quantified pain within 10s
- Agent doing hard thing visible by 45s
- Human voiceover
- Real-time agent-thinking log visible
- Architecture slide 20s, not main content

**GitHub:**
- 3-command setup
- `.env.example` with BrightData API_KEY, MCP_TOKEN
- Architecture diagram showing BrightData as live data layer
- Demo GIF or YouTube embed above fold
- MIT license

**Anti-patterns:**
- AI voiceover
- Mockup features that don't work
- BrightData as generic afterthought
- B2C without strong hook
- Raw Streamlit with no agent activity viz
- Opening with slide deck

---

## BrightData-Specific Pattern (DEV Challenge Aug 2025)

5 winners all built **monitoring or intelligence pipelines** where BrightData was the autonomous data-fetch backbone — not user-initiated lookup.

**Winning archetype:** "Agent wakes up every N hours, fetches via BrightData, makes autonomous decision, delivers structured output."

All 5 had real-time dashboard or notification output (Slack, Gmail, web UI) — not just terminal log.

---

## Sources

- [Recent Winners — lablab.ai](https://lablab.ai/apps/recent-winners)
- [AI Agent Olympics Recap](https://lablab.ai/ai-hackathons/milan-ai-week-hackathon)
- [RAISE 2025 Summary](https://lablab.ai/blog/raise-your-hack-summary-2025)
- [IBM watsonx Hackathon Recap](https://lablab.ai/ai-hackathons/agentic-ai-hackathon-ibm-watsonx-orchestrate)
- [Hackathon Guidelines Tutorial](https://lablab.ai/blog/hackathon-guidelines)
- [lablab Rule Book](https://lablab.ai/hackathon-rules)
- [DEV × n8n × BrightData Winners](https://dev.to/devteam/congrats-to-the-winners-of-the-real-time-ai-agents-challenge-powered-by-n8n-and-bright-data-104c)
- [3 Hackathon Winners — Redis Blog](https://redis.io/blog/lablab-ai-hackathon-review/)
- [AI to Code: Winning Hackathons Guide](https://lablab.ai/blog/ai-to-code-winning-hackathons-guide)

**Confidence:** High — submission rules + winner descriptions across multiple sponsor events. Medium for inferred video timestamp structure.
