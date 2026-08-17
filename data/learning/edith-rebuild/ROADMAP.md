# EDITH Rebuild — Teacher Mode Roadmap

**Started:** 2026-07-08
**Goal:** Boss EDITH Maintenance System ko scratch se samajh kar mentally rebuild kar sake — har design decision ka WHY + why-not-alternatives ke saath. Interview-ready depth.
**Format (locked):** Problem → Options → Why Chosen → Working → Real Example → Analogy → Interview Golden Answer → Comprehension Checks (predict-output / spot-flaw / explain — NEVER "write code yourself").
**Register:** Hinglish, story-based, ASCII diagrams, comparison tables. Ek lesson per session. Checks answer karne ke baad hi next lesson.

## Grounding sources (real build files)
- `data/hackathons/tata-steel-2026/round_2/dataforge/datasets/steel-maintenance-flagship/SPEC/datacard.md`
- `dataforge/gen_condition_monitoring_v2.py` (+ cycle2/4/5 fix scripts)
- `edith/SUBMISSION_DOCUMENT.md`
- `vulcan/` (agents, ml, rag), `maintenance-wizard/`

## Curriculum — Project as 10 Problems

| # | Problem (lesson) | Core question | Status |
|---|---|---|---|
| 0 | Problem Framing | PS §5/§6 → system requirements. Engineer-first thesis. | pending |
| 1 | **DATA SYNTHESIS** | Real data nahi hai — physics-grounded synthetic kaise banaya (spine → generators → de-leaked labels → audit cycles) | **PASSED 2026-07-10 (simple version)** |
| 2 | ML Layer | IsolationForest (anomaly) + LightGBM classifier (fault) + LightGBM regressor (RUL). Why not deep learning. Group-CV by run_id. | **PASSED 2026-07-11** (Boss ne khud supervised-vs-unsupervised reasoning nikali; refinement diya: classifier confident-galat hota hai, "pata nahi" nahi bol sakta) |
| 3 | Knowledge / RAG | 80 docs, bge-small embeddings + ChromaDB + FlashRank rerank. Why RAG not fine-tuning for manuals. | **PASSED 2026-07-11** (Boss: retrain costly/slow → RAG; maine freshness point complete kiya) |
| 4 | Agentic Reasoning | 5-agent chain (Diagnosis→RCA→Predictor→Prioritizer→Recommender) + supervisor. Deterministic-first, LLM 4-rung ladder. Why multi-agent not one prompt. | **PASSED 2026-07-11** (Boss: specific kaam → targeted fix vs blind full retrain) |
| 5 | Trust Layer | DeBERTa NLI faithfulness gate + inline citations. Why pretrained, not trained. | **PASSED 2026-07-11** (Boss: contradiction → line blocked, hallucination pakda) |
| 6 | Serving Backend | FastAPI + SSE live stream + endpoints (/ask, /focus, /bottleneck, /predict, /report). Real-time alerting. | **PASSED 2026-07-11** (Boss: polling = late alert = blast risk → SSE) |
| 7 | Cockpit UI | Next.js 16 + uPlot dark HUD. START-HERE panel, verdict cards. Engineer-first design decisions. | **PASSED 2026-07-11** (Boss: hamara design = 1 sec mein problem dikhti; dost ka = khud dhoondte raho) |
| 8 | Evaluation | 310-item eval set (Hinglish + adversarial refusal), feedback loop §6.6. How to know it works. | **PASSED 2026-07-11** (Boss: Team A "kuch bhi likh dega" = hallucination in own words; refusal = feature) |
| 9 | Packaging | PDF reports, demo recording, submission doc — PS 1:1 mapping. | **PASSED 2026-07-11** |

## Study rules (teacher mode v2)
1. **Ek lesson = ek problem.** Poora dump nahi.
2. **Har lesson ke end mein 3 checks** — Boss answers, fir main gaps correct karta hoon, TAB next lesson.
3. **Revision hooks:** har lesson ka "Ek line mein yaad rakho" + ek analogy. Next session start pe pichle lesson ka 1 rapid-fire check (spaced repetition).
4. **Why-not table mandatory** — har decision ke against 2-3 rejected alternatives with reasons.
5. **Interview Golden Answer** har lesson mein — English, bolne layak.
6. Boss ke wrong answers = data. Root-cause the misconception, don't just correct.

## Progress log
- 2026-07-08 — Lesson 1 (Data Synthesis) delivered (detailed version). Boss bola "samajh nahi aaya".
- 2026-07-10 — **IMPORTANT: Boss ko ULTRA-SIMPLE language chahiye.** Detailed version fail hui. Simple re-teach (master-file analogy, 3 rules, exam-corner-answer leakage analogy) worked. Boss ne dono checks pass kiye (Rule-2 inertia + label leakage). Jargon baad mein introduce karo, pehle intuition. Ek concept per section, chhoti lines.
- 2026-07-10 — Lesson 2 (ML Layer) started — simple version, doctor/hospital analogy, LightGBM reg-vs-clf Boss pehle se jaanta hai (uske notes mein hai), usse connect kiya.
- 2026-07-11 — **COURSE COMPLETE (9/9 PASS)** — Lessons 2-9 sab simple-version mein, har lesson 1 check ke saath. Final synthesis check bhi pass: "kisi pe aankh band bharosa nahi — har baat ka saboot" (Boss: "LLM pe kabhi aankh band bharosa nahi kiya"). Lesson 0 (Problem Framing) separately nahi padhaya — lessons ke andar hi cover hua.
- **NEXT OPTIONS (Boss decide karega):** (a) revision rapid-fire quiz (9 one-liners), (b) EDITH interview mock (English mein, ASIAN-interview style), (c) kisi lesson ka detailed/technical version (ab jargon ke saath — Weibull, AR(1), embeddings, NLI), (d) haath se mini-version banwana (chhota EDITH scratch se).

## Revision one-liners (spaced repetition ke liye)
1. Data: "Pehle master file (spine), fir sara data usi se — model ko answer chupke se mat do (leakage)."
2. ML: "Nurse (IsolationForest) + doctor ke 2 jawab (LightGBM clf=category, reg=number). Table data → LightGBM, DL nahi."
3. RAG: "Ratta nahi, open-book — matlab ke numbers se page dhoondo, 2 chhalni, page-number saboot."
4. Agents: "5 specialist workers — facts data se, LLM sirf bhasha. Galti turant milti hai."
5. Trust: "Copy-checker teacher (DeBERTa) har line ko kitab se milata hai — SUPPORTED/CONTRADICTION/NEUTRAL."
6. Backend: "Waiter+menu (FastAPI counters), doodhwala subscription (SSE) — khatre pe system khud chillaye."
7. UI: "Car dashboard — START HERE red light, rang-patti, 2-layer jawab (verdict + saboot)."
8. Eval: "310 sawal — seedhe + Hinglish + trick (jahan sahi jawab = MANA karna). Har change pe exam dubara."
9. Packaging: "Question number ke saamne jawab, demo ka baked backup, limits khud batao."
10. MASTER: "Kisi pe aankh band bharosa nahi — har baat ka saboot, warna 'pata nahi'."
