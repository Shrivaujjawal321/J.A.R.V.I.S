# UJJAWAL SHRIVASTAV

**AI Engineer | GenAI & Agentic Systems**

Delhi, India  •  +91 9718732066  •  shriva.ujjawal@gmail.com
[Portfolio](https://ujjawal-shrivastav.vercel.app/)  •  [LinkedIn](https://www.linkedin.com/in/ujjawal-shrivastav-79610a291/)  •  [GitHub](https://github.com/Shrivaujjawal321)

---

## SUMMARY

AI Engineer specializing in production GenAI applications — multi-agent orchestration, RAG pipelines, and LLM-driven user-facing systems. Hands-on experience shipping agentic platforms from architecture to deployment. Strong problem-solver mindset with a bias toward shipping working systems over prototypes. B.Tech in Computer Science (AI/ML), 2025.

---

## TECHNICAL SKILLS

**LLM & GenAI:** Claude API, OpenAI API, Gemini, Claude Agent SDK, LangChain, Prompt Engineering, Fine-tuning workflows, Model Context Protocol (MCP), Function Calling

**Agentic Systems:** Multi-agent orchestration, Autonomous task decomposition, Tiered safety frameworks, Episodic memory (vector recall), Agent evaluation pipelines

**Retrieval & Search:** RAG architectures, ChromaDB, pgvector, Sentence Transformers, Hybrid semantic + keyword search, Reranking

**Backend & Deployment:** Python, FastAPI, asyncio, REST APIs, Next.js 15, Node.js, PostgreSQL, Neon Postgres, Vercel, Docker, Systemd services

**ML Foundations:** PyTorch, Scikit-learn, LightGBM, XGBoost, Pandas, NumPy, Optuna, SHAP

**Tools:** Git, Linux, Bash, JSON/JSONL pipelines, Streamlit

---

## EXPERIENCE

### AI Engineer Intern — AgentNation
*Jan 2026 – Present  •  4 months*

AgentNation is a digital-twin platform that creates personalized AI agents mirroring each user's persona, voice, and decision patterns through a guided onboarding flow.

- Designed the agent memory architecture — defined memory taxonomy (facts, preferences, episodic interactions, behavioral patterns) and mapped which data type belongs in which memory layer to enable consistent twin behavior across sessions.
- Structured the platform UI for the onboarding and twin-interaction flows, organizing component hierarchy and information layout to balance depth of intake with completion rate.
- Triaged and resolved production errors and integration issues across the codebase using Claude Code as an AI-assisted engineering workflow, shipping fixes faster than traditional manual debugging cycles.
- Collaborated with the team on iteration cycles — translating product requirements into memory-schema decisions and UI structure changes that improved twin response consistency.

---

## PROJECTS

### Jarvis — Production Multi-Agent AI Orchestration Platform
*Python, FastAPI, Claude Agent SDK, MCP, ChromaDB, Asyncio*  •  *2026*
[github.com/Shrivaujjawal321](https://github.com/Shrivaujjawal321)

- Architected and deployed a 93-specialist multi-agent system with a FastAPI daemon (`jarvis-core`) that dispatches parallel Claude Code workers via `asyncio.gather` for concurrent multi-domain execution.
- Built an autonomous goal lifecycle engine: natural-language goal intake → LLM decomposition into typed sub-tasks → parallel execution → human-approval queue for irreversible actions → morning digest, with per-goal budget and duration caps.
- Engineered a 4-tier safety framework (auto / audited / confirm / refuse) with immutable JSONL audit logging, mirroring human-in-loop guardrails for production AI systems.
- Shipped an episodic memory layer using ChromaDB + sentence-transformers with daily incremental ingestion and semantic recall injected into every agent invocation.
- Deployed a weekly self-improvement loop: LLM synthesizes feedback signals → auto-applies safe capability changes → queues higher-risk changes for review, gated by eval-regression checks.

### McpIndex — MCP Server Discovery Platform
*Next.js 15, Neon Postgres, pgvector, Gemini Flash, Vercel*  •  *2026*
[mcpindex-nu.vercel.app](https://mcpindex-nu.vercel.app)

- Built and deployed a production search platform indexing 1,532 MCP servers, with hybrid semantic + keyword search powered by pgvector embeddings — shipped from zero to live in 2 days.
- Designed a 6-dimensional automated quality scoring pipeline (reliability, documentation, adoption, recency, security, compatibility) to surface high-signal results over raw popularity.
- Integrated Gemini Flash for query understanding and semantic ranking; built ingestion crawler and scoring jobs for continuous index refresh.

---

## EDUCATION

**B.Tech — Computer Science (AI/ML Specialization)**
Krishna Engineering College  •  2022 – 2025

---

## STRENGTHS

- **Problem-Solver Mindset** — breaks ambiguous problems into shippable units, optimizes for working systems over polish
- **AI-Native Builder** — designs and ships end-to-end with modern LLM tooling and agentic patterns
- **Production Discipline** — audit logging, safety tiers, evaluation pipelines, and deployment as first-class concerns
