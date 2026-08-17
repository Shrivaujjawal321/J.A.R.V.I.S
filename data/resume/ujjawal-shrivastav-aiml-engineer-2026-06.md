# UJJAWAL SHRIVASTAV

**AI/ML Engineer — ML Pipelines, RAG & Agentic Systems**

Delhi, India  •  +91 9718732066  •  shriva.ujjawal@gmail.com
Portfolio: https://ujjawal-shrivastav.vercel.app/  •  LinkedIn: https://www.linkedin.com/in/ujjawal-shrivastav-79610a291/  •  GitHub: https://github.com/Shrivaujjawal321

---

## SUMMARY

AI/ML Engineer (B.Tech CS, AI/ML — 2025) who ships production ML pipelines, agentic RAG systems, and FastAPI services. Reached Round 2 of the Tata Steel National AI/ML Hackathon (70+ submissions). Strong across tabular ML, embeddings, multi-agent orchestration, and real-time streaming.

---

## TECHNICAL SKILLS

**Languages & Backend:** Python, TypeScript, FastAPI, REST, SSE streaming, asyncio, Pydantic v2, Next.js, Node.js, PostgreSQL, Docker, Git

**ML:** scikit-learn, LightGBM, CatBoost, IsolationForest, Pandas, NumPy, cross-validation, model calibration, RUL estimation

**GenAI / NLP:** LLMs, RAG pipelines, agentic reasoning chains, embeddings (sentence-transformers), FlashRank reranking, NLI faithfulness gating (DeBERTa), ChromaDB, pgvector

---

## PROJECTS

### Jarvis — Multi-Agent AI Assistant with RAG Pipeline
*Python, FastAPI, Claude Agent SDK, ChromaDB, sentence-transformers, asyncio, pytest  •  2026*
github.com/Shrivaujjawal321

- Built a production RAG pipeline — markdown and conversation logs chunked, embedded with all-MiniLM-L6-v2, stored in ChromaDB, and retrieved by cosine similarity with token-budget trimming before context injection.
- Deployed a FastAPI daemon (/chat, /task) with asyncio-parallel agent workers and a four-rubric self-correction loop that forces hedging on unsourced claims; 35+ pytest tests, run as systemd services.

### Tata Steel National AI/ML Hackathon 2026 — Round 1 → Round 2 (EDITH)
*scikit-learn, LightGBM, CatBoost · FastAPI, ChromaDB, FlashRank, Claude Agent SDK, Next.js, React 19  •  2026*
github.com/Shrivaujjawal321/edith-maintenance-wizard  •  Demo: youtu.be/2upa03Ye9Zg

- **Round 1 — Steel Surface-Defect Detection:** built a gradient-boosted ensemble (LightGBM + CatBoost) on industrial tabular data with stratified cross-validation, optimizing a custom precision-recall metric across 70+ leaderboard submissions — finished **rank 22** and advanced to Round 2.
- **Round 2 — EDITH (agentic maintenance copilot):** built a five-agent reasoning chain (Diagnosis → RCA → RUL → Prioritization → Recommendations) over a purpose-built 1.25M-row physics-grounded dataset — structured ML inference with zero hallucination risk on factual claims.
- Engineered EDITH's hybrid RAG (bge-small + FlashRank rerank + ChromaDB) with a DeBERTa NLI faithfulness gate, plus SSE-streamed live monitoring of 15 assets and auto-diagnosis on first sustained alarm.

### EngiNerd — AI Learning Platform for Engineering Students
*TypeScript, Next.js, Anthropic Claude (Sonnet / Haiku), Drizzle ORM, PostgreSQL, Playwright  •  2026*
[enginerd.vercel.app](https://enginerd.vercel.app)

- Built a 5-stage LLM content pipeline (research → mapping → deep-dive → writing → review) with Claude structured tool-use, an offline stub mode for deterministic tests, and SSE streaming to a live dashboard.
- Engineered production reliability: tiered Redis rate-limiting, HMAC-verified idempotent payments, and OTP + OAuth auth — 68 unit and 43 Playwright end-to-end tests gating every change.

### McpIndex — Hybrid Search Platform
*Next.js, Neon Postgres, pgvector, Gemini Flash, Vercel  •  2026*
[mcpindex-nu.vercel.app](https://mcpindex-nu.vercel.app)

- Shipped a production search platform indexing 1,532 MCP servers with hybrid BM25 + pgvector semantic search and a 6-dimensional automated quality-scoring pipeline; built end-to-end in 2 days.

### Math Tug — Real-Time 2-Player Educational Game
*React 19, TypeScript, Phaser 4, Tailwind 4, PartyKit (Cloudflare Workers), Capacitor (Android)  •  2026*
github.com/Shrivaujjawal321/kids-math-tug  •  Live: kids-math-tug.vercel.app

- Built a 2-player real-time math tug-of-war game on a Phaser 4 canvas with authoritative PartyKit / Cloudflare-Workers multiplayer sync and a strict-TypeScript state machine — ships to web and as a Capacitor Android app from one codebase.

---

## EDUCATION

**B.Tech — Computer Science (AI/ML Specialization)**, Krishna Engineering College  •  2022 – 2025

---

## STRENGTHS & INTERESTS

Breaks ambiguous problems into shippable units · learns new tools fast · adaptable across the stack  |  **Interests:** Snooker · agent frameworks · side projects
