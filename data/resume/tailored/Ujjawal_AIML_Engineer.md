# UJJAWAL SHRIVASTAV

**AI Engineer — RAG, Agentic Systems & NLP/GenAI Automation**

Delhi, India  •  +91 9718732066  •  shriva.ujjawal@gmail.com
Portfolio: https://ujjawal-shrivastav.vercel.app/  •  LinkedIn: https://www.linkedin.com/in/ujjawal-shrivastav-79610a291/  •  GitHub: https://github.com/Shrivaujjawal321

---

## SUMMARY

AI/ML Engineer (B.Tech CS-AIML — 2025) specialising in RAG pipelines, agentic multi-agent systems, and NLP/GenAI automation. Reached Round 2 of the Tata Steel National AI/ML Hackathon (70+ LB submissions, rank 22). Hands-on with LLMs (Claude, Gemini), vector DBs (ChromaDB, pgvector), prompt engineering, and production FastAPI services — ready to ship AI-powered features from day one.

---

## TECHNICAL SKILLS

**Languages & Backend:** Python, TypeScript, FastAPI, REST, SSE streaming, asyncio, Pydantic v2, Next.js, Node.js, PostgreSQL, Docker, Git

**ML & Data:** scikit-learn, LightGBM, CatBoost, IsolationForest, Pandas, NumPy, cross-validation, model calibration, RUL estimation

**GenAI / NLP / Agentic:** LLMs (Claude, Gemini), RAG pipelines, prompt engineering, multi-agent orchestration, AI automation workflows, embeddings (sentence-transformers, bge-small), FlashRank reranking, NLI faithfulness gating (DeBERTa), ChromaDB, pgvector, fine-tuning awareness (LoRA/PEFT)

---

## PROJECTS

### Jarvis — Multi-Agent AI Assistant with RAG & Automation Pipeline
*Python, FastAPI, Claude Agent SDK, ChromaDB, sentence-transformers, asyncio, pytest  •  2026*
github.com/Shrivaujjawal321

- Built a production RAG pipeline — docs and conversation logs chunked, embedded with all-MiniLM-L6-v2, stored in ChromaDB, retrieved by cosine similarity with token-budget trimming; eval suite of 155+ bootstrapped chunks tunes retrieval threshold.
- Prompt-engineered a four-rubric self-correction loop (intent / claims / memory / tone) inside a FastAPI daemon with asyncio-parallel agentic workers; AI automation via Telegram bridge + cron triggers — 35+ pytest tests, live as systemd services.

### Tata Steel National AI/ML Hackathon 2026 — Round 1 → Round 2 (EDITH)
*scikit-learn, LightGBM, CatBoost · FastAPI, ChromaDB, FlashRank, Claude Agent SDK, Next.js, React 19  •  2026*
github.com/Shrivaujjawal321/edith-maintenance-wizard  •  Demo: youtu.be/2upa03Ye9Zg

- **Round 1 — Defect-Pattern Detection:** gradient-boosted ensemble (LightGBM + CatBoost) on industrial tabular sensor data with stratified cross-validation, optimizing a custom precision-recall metric — 70+ LB submissions, finished **rank 22**, advanced to Round 2.
- **Round 2 — EDITH (agentic maintenance copilot):** five-agent reasoning chain (Diagnosis → RCA → RUL → Prioritization → Recommendations) over a 1.25M-row physics-grounded dataset; structured ML inference with zero hallucination risk on factual claims.
- Engineered hybrid RAG (bge-small embeddings + FlashRank reranking + ChromaDB) with a DeBERTa NLI faithfulness gate; SSE-streamed live monitoring of 15 industrial assets with auto-diagnosis on first sustained alarm.

### EngiNerd — AI Learning Platform (5-Stage LLM Pipeline)
*TypeScript, Next.js, Anthropic Claude (Sonnet / Haiku), Drizzle ORM, PostgreSQL, Playwright  •  2026*
enginerd.vercel.app

- Built a 5-stage NLP content pipeline (research → concept mapping → deep-dive → writing → review) with Claude structured tool-use, prompt-engineered per stage, and SSE streaming to a live progress dashboard.
- Engineered production reliability: tiered rate-limiting, HMAC-verified idempotent payments, OTP + OAuth auth — 68 unit + 43 Playwright end-to-end tests gating every deploy.

### McpIndex — Hybrid Search Platform (BM25 + pgvector Semantic Search)
*Next.js, Neon Postgres, pgvector, Gemini Flash, Vercel  •  2026*
mcpindex-nu.vercel.app

- Shipped a search platform indexing 1,532 MCP servers using hybrid BM25 + pgvector semantic search and a 6-dimensional automated quality-scoring pipeline; built end-to-end in 2 days.

---

## EDUCATION

**B.Tech — Computer Science (AI/ML Specialization)**, Krishna Engineering College  •  2022 – 2025

---

## STRENGTHS & INTERESTS

Ships production AI systems fast · strong at prompt engineering and RAG debugging · adaptable across ML and GenAI stacks  |  **Interests:** Agent frameworks · side projects · snooker
