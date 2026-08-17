# AI/ML Resume Mastery — Boss (Ujjawal)

**Started:** 2026-06-07 · **Target:** complete by 2026-06-30 (~23 days) · **Mode:** Jarvis teacher, Hinglish, comprehension-not-writing, brief + deep + example, one step at a time.

> **GOAL:** Boss should DEEPLY understand every technical topic on his AI/ML resume — so he can confidently explain any line in an interview AND genuinely be a good AI/ML engineer. Not ratta — real understanding.
>
> **TEACHING RULE (carried from Python journey):** SHOW the concept → explain with analogy + real example (use HIS OWN projects from the resume) → ask COMPREHENSION questions (predict-output / explain-in-words / spot-the-mistake / "interviewer asks X, how do you answer"). NEVER fill-the-blank / "now you write it". Lead with the answer, then concept. Boss learns concepts fast — reinforce with repetition, keep moving.
>
> **INTERVIEW LENS:** Every lesson ends with "Agar interviewer ye poochhe..." — the actual question + a crisp 2-3 line answer in Boss's own framing. This is the payoff.

---

## How topics map to the resume

Each lesson is tied to a real line on Boss's resume so the payoff is obvious — he's learning to defend his OWN work, not abstract theory.

---

## MODULE A — Classical ML (the **Steel Surface-Defect** project)
*The densest, most interview-heavy module. This is where "ML Engineer" gets tested hardest.*

- [x] A1. The ML big picture ✅ (2026-06-08) — rules-vs-examples, features (X) vs label (y), train vs test (no peeking). Check (house-price X/y) correct. Interview Q (traditional vs ML) covered, tied to Steel project.
- [ ] A2. Data cleaning & preprocessing — missing values, scaling, encoding
- [ ] A3. Feature engineering — what it is, why it beats fancy models
- [ ] A4. Train/test split + data leakage — why you hold data back
- [ ] A5. Cross-validation — k-fold, stratified, and OOF (out-of-fold)
- [ ] A6. Decision trees — the building block (how a tree "decides")
- [ ] A7. Gradient boosting — the core idea (LightGBM & CatBoost, how boosting works)
- [ ] A8. Ensembles — why combining models wins
- [ ] A9. Evaluation metrics — accuracy, precision, recall, F1, the precision-recall tradeoff
- [ ] A10. Calibration — what it means + why his V27 post-hoc threshold broke the LB (his real story)
- [ ] A11. Error analysis & overfitting — CV-vs-LB gap, the systematic-iteration mindset

## MODULE B — GenAI / NLP / RAG (the **Jarvis** + **McpIndex** projects)
*The "GenAI Engineer" half. Hottest hiring area in 2026.*

- [ ] B1. What an LLM actually is — tokens, next-token prediction, context window
- [ ] B2. Embeddings — turning meaning into numbers (vectors)
- [ ] B3. sentence-transformers & all-MiniLM-L6-v2 — the model his Jarvis uses
- [ ] B4. Cosine similarity — how "closeness of meaning" is measured
- [ ] B5. Text chunking — why split docs, why ~500 tokens
- [ ] B6. Vector databases — ChromaDB & pgvector (what/why)
- [ ] B7. RAG pipeline — the full retrieve→augment→generate flow (his Jarvis end-to-end)
- [ ] B8. BM25 & hybrid search — keyword + semantic (his McpIndex)
- [ ] B9. Prompt engineering — what actually moves quality
- [ ] B10. Structured tool-use / function calling — how LLMs "do things" (his EngiNerd pipeline)
- [ ] B11. Evals & self-correction — rubrics, LLM-as-judge (his 4-rubric critic loop)
- [ ] B12. Multi-agent orchestration & Claude Agent SDK — manager→workers, parallel dispatch (his Jarvis core)

## MODULE D — Deep Learning (**PyTorch**)
*The biggest genuine gap from the resume's ML skills. Classical ML (Module A) vs deep learning — when each wins.*

- [ ] D1. What is deep learning + PyTorch — neural nets intuition, tensors, classical-ML vs DL (when to use which)
- [ ] D2. The training loop — forward → loss → backward (autograd) → step; what "training" actually does

## MODULE C — Backend / Infra / Tools (the **FastAPI / systemd** side)
*Makes him a full-stack-ish ML engineer, not just a notebook person.*

- [ ] C1. REST APIs & FastAPI — endpoints, request/response (builds on Python Lesson 13)
- [ ] C2. Pydantic v2 — schemas & validation (why his code is "type-safe")
- [ ] C3. asyncio in production — applied (builds on Python Lesson 14, his concurrent workers)
- [ ] C4. PostgreSQL + pgvector — relational DB basics + vector column
- [ ] C5. Docker — containers, "works on my machine" solved
- [ ] C6. Linux & systemd — long-running services (his daemon as a service)
- [ ] C7. pytest & observability — testing + JSONL logging (his quality gates)
- [ ] C8. Git — version control essentials
- [ ] C9. SSE streaming — server-sent events, "live progress dashboard" (his EngiNerd)
- [ ] C10. Rate-limiting & idempotency — tiered limits, HMAC-verified idempotent payment (his EngiNerd production reliability)
- [ ] C11. Authentication — OTP + OAuth, how login/security works (his EngiNerd auth)
- [ ] C12. Bash & Vercel — shell essentials + deployment platform (quick infra round-out)

---

## Suggested pace (to finish by Jun 30)
- Boss goes fast (multiple lessons/session). 37 lessons / 23 days = very doable.
- Module A first (hardest + most interview-critical), then B (hottest area), then C (rounds it out).
- No fixed daily quota — go by energy. "continue" = next lesson.

## Progress log
- 2026-06-07: Roadmap created. Initially 30 lessons (A:11, B:11, C:8). Boss asked if EVERY resume skill was covered → did honest coverage audit → Boss picked "AI/ML-focused" expansion (option 1): ADDED PyTorch (Module D ×2 — biggest genuine gap), Agent SDK/multi-agent (B12), backend-reliability trio + SSE + Bash/Vercel (C9-C12). DELIBERATELY SKIPPED pure frontend (Next.js/React/TS/Vite/Framer/Capacitor/Drizzle) — not core to AI/ML role, interview-talk level only. **Total now 37 lessons** (A:11, B:12, C:12, D:2). Each tied to a real resume line + interview-question payoff. Boss just completed entire Python roadmap (loops→async in 10 days) — same comprehension-mode teaching. Starting Lesson A1.
