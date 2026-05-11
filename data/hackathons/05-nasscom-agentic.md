# NASSCOM Agentic AI Hackathon 2026 — Deep Research

**Deadline:** TBC (likely late May / early June 2026 — URGENT, register now) | **Prize:** ₹10L | **Outcome:** AI Confluence (July 2026)

## Registration Status (URGENT)
- Official page (`nasscom.in/ai/AIDeveloperMarathon/agentic-ai-hackathon/`) returns 406 to bots — visit in browser
- Also check `hack2skill.com/event/nasscom-ai` (likely host)
- Program structure: Explore (Mar–Apr) → **Engineer (Apr–Jun)** ← hackathon phase → Excel (July finale)
- **Best estimate:** late May / early June close. Register today even if undecided on PS.

---

## Two Confirmed Problem Statements (High Confidence)

### PS1: AI Powered Intelligent Ticket Routing & Resolution Agent (ITSM)

**What it really asks:** Indian IT service desks (Infosys/Wipro/HCL) handle 10K+ tickets/day. L1 tickets are 40-60% of volume. Cost ₹200-800/ticket. Sponsor wants an agent that:
- Understands intent (not keyword matching)
- Pulls user context (history, assets, SLA tier)
- Decides resolve vs escalate
- *Actually executes* the fix via APIs (not just routes)
- Learns from outcomes
- Maintains audit trail

**Sub-problems:**
1. Intent classification at scale (multi-label, multilingual, malformed text)
2. Context assembly (3+ system tool use)
3. Resolve vs escalate decision logic
4. Auto-resolution execution (sandboxed API calls)
5. KB gap detection (draft KB articles for failed resolutions)
6. Multi-channel ingestion (email, Teams, Slack, WhatsApp, voice)

### PS2: Enterprise Knowledge Assistant (RAG + Agentic Workflow)

**What it really asks:** Multi-hop reasoning over heterogeneous enterprise knowledge with authoritative sourcing and ZERO hallucination. NOT a chatbot with KB behind it.

**Sub-problems:**
1. Query decomposition (complex → sub-queries)
2. Multi-source retrieval orchestration (vector + SQL + API + docs)
3. Semantic vs structured hybrid routing
4. Source citation + confidence scoring
5. Knowledge gap detection + escalation (no hallucination)
6. Access control-aware retrieval (RBAC)

---

## 10 Project Ideas Per PS

### PS1: ITSM Ticket Routing & Resolution

| # | Title | Pitch | Difficulty | Agentic Depth |
|---|-------|-------|-----------|--------------|
| 1 | **AutoResolve-IT** | LangGraph ITSM agent: ServiceNow mock + KB + LangSmith traces | Medium | 5 |
| 2 | **TriageSwarm** | CrewAI: Intent + History + Policy + Executor agents | Medium | 4 |
| 3 | **SelfHeal-Agent** | Proactive: monitors metrics → opens + resolves tickets before user reports | Hard | 5 |
| 4 | **KBGapFinder** | After failed resolutions, drafts KB article for human review | Medium | 3 |
| 5 | **MultiLingualDesk** | Hindi/Hinglish ITSM (IndicTrans2 + Claude multilingual) | Medium | 4 |
| 6 | **AgentSRE** | SRE agent: receives alerts → runs runbook steps → pages humans on exhaust | Hard | 5 |
| 7 | **TicketContextualizer** | Pre-routing: assembles full context brief from 4 sources in <10s | Easy-Med | 3 |
| 8 | **ComplianceTicketAudit** | Post-resolution: SLA compliance audit + violation flagging + reports | Medium | 3 |
| 9 | **ConversationalL1Bot** | Slack/Teams bot: resolves password reset + VPN + access via mock APIs | Medium | 4 |
| 10 | **TicketIntelligenceDashboard** | Pattern analysis → root causes → process improvement recs | Medium | 3 |

### PS2: Enterprise Knowledge Assistant

| # | Title | Pitch | Difficulty | Agentic Depth |
|---|-------|-------|-----------|--------------|
| 1 | **HierarchicalKnowledgeAgent** | Router → 3 retriever sub-agents (semantic + SQL + web) → cited synthesis | Med-Hard | 5 |
| 2 | **OnboardingCopilot** | Role-specific 90-day onboarding + proactive doc surfacing | Medium | 4 |
| 3 | **PolicyGuardian** | "Is this compliant?" agent with traceable reasoning + RBAC | Medium | 4 |
| 4 | **KnowledgeSynthesisAgent** | Detects contradictions across enterprise docs → flags for resolution | Hard | 4 |
| 5 | **SalesIntelligenceAgent** | Pre-sales: capability + project history + compliance synthesis | Medium | 4 |
| 6 | **AuditTrailRAG** | Every answer has structured audit trail (retrieved/rejected/scored) | Medium | 4 |
| 7 | **IncidentRunbookAgent** | Incident query → runbook retrieval + freshness check (Git diff) | Medium | 4 |
| 8 | **CrossProjectInsightEngine** | Surfaces patterns across past projects ("similar banking migrations failed because...") | Hard | 5 |
| 9 | **RegulationTracker** | RBI/SEBI updates → diff against internal policies → gap report | Hard | 4 |
| 10 | **MultiModalEnterpriseRAG** | Text + image + table queries over PDFs/spreadsheets/PPTs | Hard | 4 |

---

## Top 3 Frameworks to Learn

### 1. LangGraph (learn FIRST)
- Production-grade, stateful, graph-based
- 70%+ of production agent systems use this
- v1.0 (late 2025) has durable execution + human-in-loop checkpointing + LangSmith
- Time: 2-3 days to be dangerous
- Tutorial: official quickstart + "Customer Support Agent"

### 2. CrewAI (for multi-agent demos)
- Role-based agents — judges instantly grok "Triage Agent + KB Agent + Resolver Agent"
- Fastest idea → working prototype path
- Time: 1-2 days

### 3. LangSmith / Langfuse (NON-NEGOTIABLE)
- Observability layer for production credibility
- Judges WILL ask: "How do you evaluate? How do you know it's not hallucinating?"
- LangSmith native to LangGraph; Langfuse open-source
- Show: trace per agent step + eval run with hallucination % + cost per query

---

## 3 Demos to Study/Clone

1. **LinkedIn SQL Bot (LangGraph, production)** — stateful query planning, human-in-loop approval for destructive queries
2. **RiskWise** (Microsoft AI Agents Hackathon 2025 Best Overall, 18K+ devs) — supply chain risk; clean enterprise framing
3. **NexusGuardAI** (IBM watsonx Orchestrate winner) — agentic SOC copilot; "investigate → correlate → act → audit" pattern transferable to PS1

---

## Top Picks for Ujjawal
- **PS1 — AutoResolve-IT (#1)** for demo-ability OR **AgentSRE (#6)** for novelty (SRE automation is bleeding edge)
- **PS2 — HierarchicalKnowledgeAgent (#1)** for clean theory + measurable accuracy gain (34.6% multi-hop boost) OR **CrossProjectInsightEngine (#8)** for genuine differentiation in Indian IT services
- **Sleeper pick:** RegulationTracker (#9 PS2) — every BFSI IT firm needs this, almost no one builds it well

## What NASSCOM Judges Reward (from past patterns)
1. **Real tool calls, not mocked strings** (Kong hackathon judges explicitly called this out)
2. **Audit trail visibility** (LangSmith traces in demo)
3. **Business case in crores** ("auto-resolves 40% L1 = ₹2Cr annual savings for 1000 tickets/day op")
4. **Agentic depth 4-5** (don't build a score-3 project and call it agentic)
5. **Human-in-loop design** (signals production-readiness)
6. **Founder-grade pitch** (sell as if to sponsor)

## Common Pitfalls
- Chatbot called "agent" — judges WILL ask "where does it plan? Where does it use tools?"
- No actual resolution (PS1 specifically requires action, not just routing)
- Fake/mocked tool calls
- No error handling
- No observability (no traces = no trust = no win)
- For PS2: vanilla RAG with no agentic layer
- For PS2: ignoring access control (disqualifying for enterprise buyers)
