# AI Automation Studio — Sales Kit
**Owner:** Ujjawal Shrivastav  
**Version:** 1.0 | 2026-05-31  
**Usage:** One-pager (send after first contact / pin on LinkedIn) + 3 gig descriptions (Fiverr/Upwork/Contra) + LinkedIn profile copy

---

# DOCUMENT 1: ONE-PAGER

---

## Your AI stack should cost less and do more. I build that.

**Ujjawal Shrivastav — AI Automation Engineer, Delhi**  
Available for freelance projects starting ₹15,000 · ujjawal.shrivastav@gmail.com

---

### Who this is for

Early-stage startups and solo founders who are:

- Paying ₹50k–₹3L/month on OpenAI or Claude API — and suspect they're wasting half of it
- Doing the same workflow by hand (content, outreach, support, data entry) that an AI agent could handle
- Sitting on 100s of docs, PDFs, or Notion pages their team can't actually search
- Founders who need AI-generated content at scale but can't afford an agency

---

### What I do

**1. LLM Cost-Optimization Audit** — ₹15,000–₹25,000 (one-time)  
I audit your current OpenAI/Claude/Gemini usage and come back with a specific cut plan: which calls to cache, which to route to a cheaper model, where your token bloat lives. Most codebases I've looked at have 40–70% waste in them.

**2. AI Automation / Agent Build** — ₹15,000–₹40,000 (one-time)  
I map a manual process you're doing, then automate it end-to-end with an AI agent — from trigger to output to notification. LinkedIn outreach, lead qualification, internal ops, data pipelines. Delivered in 5–10 days.

**3. AI Chatbot / RAG System** — ₹15,000–₹30,000 (one-time)  
An AI assistant that answers questions from your actual documents, not hallucinated from training data. Built on your PDFs, Notion pages, or database. Deployed where your team already works (Slack, web widget, Telegram).

**4. AI Content Engine** — ₹20,000–₹40,000/month (retainer)  
A production pipeline that drafts, schedules, and posts content for you — LinkedIn, newsletters, social. Personalized to your voice, not generic templates.

---

### Proof — what I've shipped in production

**Multi-agent orchestration at scale.**  
I built and run Jarvis — a personal AI operating system with 90+ specialist agents (coding, research, writing, data, security, product, DevOps and more) that coordinate to complete complex tasks. The system uses LangGraph-style orchestration, parallel agent dispatch, and async task queues. This is not a demo. It runs my daily work.

**Real LLM cost architecture.**  
Inside Jarvis, every inference call routes by task type: Haiku-class models for fast/simple jobs, Sonnet-class for deep reasoning, prompt caching for repeat contexts. The same architecture I'd apply to your stack. Built and tuned in production, not from a tutorial.

**End-to-end automation pipeline.**  
I built a LinkedIn growth system inside Jarvis: ICP targeting → connection drafts → message personalization → browser automation → post scheduling — 4 automated batch jobs per day, with approval gates and a nightly Telegram report. It replaced hours of daily manual work.

**RAG + episodic memory.**  
Jarvis uses ChromaDB + sentence-transformers for semantic memory recall. Every conversation retrieves relevant past context before responding. 155+ chunks bootstrapped, daily auto-capture. Real retrieval pipeline — not a tutorial app.

---

### How it works

**Step 1 — 30-minute free call.**  
You tell me what you're spending, what you're doing manually, or what you want to build. I tell you honestly whether I can help and what it'll cost.

**Step 2 — Scoped proposal in 24 hours.**  
I send a one-page brief: what I'll build, what's out of scope, timeline, fixed price. No hourly billing surprises.

**Step 3 — Build in 5–10 days, then hand over.**  
I ship working code with a walkthrough. You own everything — the code, the prompts, the infrastructure. I don't lock you in.

---

### CTA

**Book the free 30-min call:** [calendly link here]  
**Email:** shriva.ujjawal@gmail.com  
**LinkedIn:** linkedin.com/in/ujjawal-shrivastav  
**Upwork / Fiverr:** [links here]

---
---

# DOCUMENT 2: THREE GIG DESCRIPTIONS

---

## GIG 1 — LLM Cost Optimization Audit

**Title (Fiverr/Upwork search-optimized):**  
LLM Cost Optimization Audit | Cut OpenAI, Claude, Gemini API Costs by 40–70%

---

**Description:**

You're paying for every token. Most apps waste 40–70% of them.

I do a full audit of your LLM usage — OpenAI, Claude, Gemini, or any other provider — and deliver a prioritized cut plan you can act on immediately. I look at: prompt bloat, redundant calls, models you're over-using (GPT-4o where GPT-4o-mini does the job), context that should be cached but isn't, and batching opportunities you're missing.

This is not a generic "use prompt caching" recommendation. I read your actual code, trace your actual calls, and give you specific line-level changes ranked by estimated savings.

I built this architecture for my own production AI system (90+ agents, multiple model tiers, real inference cost constraints). I know exactly where the waste hides.

**What you get:**
- Full audit of your LLM call patterns (up to 3 services / codebases)
- Prioritized list of 5–15 specific optimizations with estimated token/cost savings per fix
- Caching strategy: where to add prompt caching, how to structure it for your call patterns
- Model routing recommendation: which tasks to move to cheaper models without quality loss
- Implementation notes (code-ready, not vague guidance)
- 1 follow-up call to walk through the report

**What I need from you:**
- Access to your usage logs (OpenAI usage dashboard export, or CloudWatch/similar)
- Codebase access (GitHub link, or screenshare) — read-only is fine
- 30-minute kickoff call

**Not included:** Code implementation (that's the Automation package). Audit covers diagnosis and plan only.

---

**Packages:**

| | Basic | Standard | Premium |
|---|---|---|---|
| **Price** | ₹15,000 | ₹20,000 | ₹25,000 |
| **Scope** | 1 service, 1 codebase | Up to 2 services / 2 codebases | Up to 3 services / full stack |
| **Deliverable** | Audit report + top 5 fixes | Audit report + top 10 fixes + model routing plan | Full audit + complete implementation notes + caching architecture spec |
| **Follow-up call** | No | 30 min | 60 min |
| **Turnaround** | 5 days | 7 days | 10 days |

---

**FAQ:**

*Will this actually work for my stack?*  
If you use any pay-per-token LLM API and your monthly bill is above ₹15k, there is almost certainly waste. The audit pays for itself.

*Do you need my API keys?*  
No. I work from usage logs and code review. Read-only GitHub access and a usage export is all I need.

*What if the savings don't cover the audit cost?*  
If I can't find at least ₹15,000/month in savings potential for a ₹20k/mo+ bill, I'll say so in the kickoff — and we stop there, no charge.

---
---

## GIG 2 — AI Workflow Automation / Agent Build

**Title (Fiverr/Upwork search-optimized):**  
AI Workflow Automation | Build an AI Agent to Replace Your Manual Process | Python, LangChain, Claude

---

**Description:**

There is a workflow in your business you do manually, every day, that should be automated. Probably multiple. I build the AI agent that handles it end-to-end — from the trigger that starts the job, through the AI processing, to the output and notification.

What this looks like in practice: a Slack message triggers an agent that reads a new customer email, drafts a personalized reply, logs it in Notion, and pings you only if it needs review. Or: a daily cron that pulls your sales pipeline, summarizes what changed, and sends a Telegram brief. Or: an outreach agent that finds ICP prospects, writes personalized messages, and queues them for one-click send.

I built exactly this kind of system in production — a full LinkedIn pipeline (ICP search → drafts → browser automation → scheduling → nightly report) running as 4 scheduled jobs with Telegram approval gates. I didn't build a tutorial. I run it daily.

**I work with:**
- Python (LangChain, LangGraph, Claude/OpenAI SDK)
- Browser automation (Playwright — for workflows that touch web UIs)
- Telegram bots for notifications and approvals
- Notion, Google Sheets, Gmail, Slack as inputs/outputs
- ChromaDB, PostgreSQL for state and memory

**What you get:**
- Scoping call + written brief (before I write a line)
- Working agent code with a README and setup instructions
- Telegram or Slack notification integration (so you know it ran)
- 1 human approval gate if the process has irreversible outputs (send, post, delete)
- 30-min handover call + 7 days of async support post-delivery

**What I need from you:**
- A clear description of the manual process (a Loom walkthrough works best)
- Credentials/API keys for the services involved
- One person from your team to answer questions during the build

---

**Packages:**

| | Basic | Standard | Premium |
|---|---|---|---|
| **Price** | ₹15,000 | ₹25,000 | ₹40,000 |
| **Scope** | Single-step automation (1 trigger → 1 AI action → 1 output) | Multi-step workflow (3–5 steps, 2–3 integrations) | Full agent with memory, approval gates, multi-service integration |
| **Integrations** | 1 | Up to 3 | Up to 6 |
| **Memory / state** | None | Basic (logs) | ChromaDB or database-backed |
| **Notification layer** | Email | Telegram or Slack | Telegram + approval flow |
| **Turnaround** | 5 days | 7 days | 10 days |
| **Post-delivery support** | 3 days | 7 days | 14 days |

---

**FAQ:**

*Do I need a technical co-founder to maintain this after you deliver?*  
No. I write clean code with a README that explains how to restart, update prompts, and change the trigger. If you can run `python script.py`, you can operate it.

*What if my process is complicated?*  
Tell me in the inquiry. I'll scope it honestly — some processes need a Standard or Premium package, some are Basic. I'd rather scope down and deliver well than over-promise.

*Can you connect it to our internal tools (custom CRM, proprietary DB)?*  
Yes, if you can give me API docs or direct DB access. Flag it in the inquiry so I can factor it into the quote.

---
---

## GIG 3 — RAG Chatbot / AI Assistant on Your Documents

**Title (Fiverr/Upwork search-optimized):**  
RAG Chatbot | AI Assistant Trained on Your Docs, PDFs, Notion | ChromaDB + Claude/OpenAI

---

**Description:**

Your team is wasting time searching documents, re-answering the same questions, and second-guessing what the policy actually says. An AI assistant trained on your actual knowledge base fixes this — and it answers from your documents, not from hallucinated training data.

This is not a generic "plug into ChatGPT" integration. I build a proper RAG (Retrieval-Augmented Generation) pipeline: your documents get chunked and indexed into a vector database, every query retrieves the most relevant chunks first, then the LLM answers from those — with a source citation so your team can verify.

I built this architecture in production for my own knowledge base: 155+ document chunks, semantic search with sentence-transformers, daily auto-ingestion of new content, ChromaDB as the vector store, and full episodic memory recall before every query. It runs daily. I know where the edge cases are (chunk size, overlap, embedding model choice, reranking for precision).

**I build on:**
- ChromaDB (default) or Pinecone for the vector store
- sentence-transformers or OpenAI embeddings
- Claude or OpenAI as the answer LLM
- Deployed as: Telegram bot / Slack bot / web widget (React) / REST API

**Sources I can ingest:**
- PDFs, Word docs, markdown files
- Notion workspace (via API)
- Google Drive folders
- Web pages (URL list)
- Confluence, Gitbook (on request)

**What you get:**
- Ingestion pipeline: your documents → chunked → embedded → indexed (with re-ingestion script for new docs)
- Query pipeline: user question → semantic retrieval → LLM answer → source citation
- Deployed interface (Telegram, Slack, or simple web widget — your pick)
- Admin tool: add/remove documents without touching code
- 30-min handover + 7 days async support

---

**Packages:**

| | Basic | Standard | Premium |
|---|---|---|---|
| **Price** | ₹15,000 | ₹22,000 | ₹30,000 |
| **Documents** | Up to 50 (PDFs / markdown) | Up to 200 docs / 1 live source (Notion or Drive) | Unlimited docs + 2 live sources + auto-sync |
| **Vector store** | ChromaDB (local) | ChromaDB or Pinecone | Pinecone or Weaviate (managed, production-grade) |
| **Interface** | Telegram bot | Telegram + Slack | Telegram + Slack + embeddable web widget |
| **Reranking** | No | Basic | Cross-encoder reranking for precision |
| **Source citations** | Yes | Yes | Yes + confidence scoring |
| **Turnaround** | 5 days | 7 days | 10 days |
| **Post-delivery support** | 3 days | 7 days | 14 days |

---

**FAQ:**

*How is this different from just uploading docs to ChatGPT?*  
ChatGPT's file upload is a session-level hack — it doesn't persist, doesn't scale, and doesn't cite sources reliably. A proper RAG pipeline persists across users and sessions, updates when your docs update, and gives your team an always-on assistant that cites exactly which document it pulled from.

*What if our documents have sensitive data?*  
The whole thing runs on your infrastructure or on a private cloud you control. Nothing goes to a shared service. I'll walk you through the deployment so you know exactly where data lives.

*Can multiple people on our team use it?*  
Yes. The Slack and web widget deployments are multi-user by design.

---
---

# DOCUMENT 3: LINKEDIN PROFILE COPY

---

## LinkedIn Headline (220 chars max, keyword-optimized)

```
AI Automation Engineer | LLM Cost Optimization · AI Agents · RAG Systems | Freelance — Starting ₹15k | Built 90+ agent production AI stack
```

**Shorter fallback (if LinkedIn truncates):**
```
AI Automation Engineer | LLM Cost Optimization · Agents · RAG | Freelance Projects ₹15–40k
```

---

## LinkedIn About / Bio (first 2 lines — what shows before "see more")

```
I cut LLM bills and automate manual workflows for early-stage startups. Services: cost audits (₹15–25k), AI agents (₹15–40k), RAG chatbots (₹15–30k) — fixed price, 5–10 day delivery.

Built and run Jarvis in production: a 90+ agent AI orchestration system with multi-agent task dispatch, ChromaDB RAG memory, a full LinkedIn automation pipeline, and real LLM cost architecture (model routing + prompt caching across all inference calls). Not a tutorial project — it runs my daily work.
```

---

## LinkedIn About / Full Version (for "see more" expansion)

```
I cut LLM bills and automate manual workflows for early-stage startups. Fixed price. 5–10 day delivery. Starting ₹15,000.

What I've built in production:

• Jarvis — a 90+ agent AI operating system (orchestration, parallel task dispatch, async workers, Telegram integration, scheduled pipelines). Runs daily.
• LLM cost architecture — Haiku vs. Sonnet routing by task type, prompt caching on repeat contexts, token budget enforcement. Built and tuned on real inference load.
• End-to-end LinkedIn pipeline — ICP targeting, personalized outreach drafts, Playwright browser automation, post scheduling, nightly reporting. Replaced hours of manual work.
• RAG + episodic memory — ChromaDB + sentence-transformers, 155+ indexed chunks, semantic recall before every query, daily auto-ingestion.

Services:

1. LLM Cost-Optimization Audit (₹15–25k) — I audit your OpenAI/Claude/Gemini usage and give you a specific cut plan. Most stacks have 40–70% waste.
2. AI Automation / Agent Build (₹15–40k) — I automate your manual workflow end-to-end: trigger → AI processing → output → notification.
3. RAG Chatbot on Your Docs (₹15–30k) — An AI assistant that answers from your actual documents, with source citations.
4. AI Content Engine (₹20–40k/mo retainer) — Production pipeline for LinkedIn, newsletters, and social content.

Free 30-minute scoping call. If I can't find savings or can't scope your automation clearly, I'll tell you in the first call.

Book: [calendly link] | Email: shriva.ujjawal@gmail.com
```

---

*End of Sales Kit v1.0*
