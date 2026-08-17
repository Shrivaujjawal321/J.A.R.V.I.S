# AI/ML Interview Drill — Log
**For:** Ujjawal · **Context:** ASIAN Footwears (Python backend + AI-integration pitch) + broader AI/ML job hunt
**Session 1:** 2026-07-03 → 2026-07-06 · **Overall: ~7.2/10**

## Scorecard (Session 1)
| # | Topic | Score | Notes |
|---|-------|-------|-------|
| 1 | AI vs ML vs DL vs GenAI | 7 | Orbit model ✓. Fix: ML paradigms = supervised/unsupervised/reinforcement (regression paradigm NAHI hai). LLM = DL ka product, ulta nahi. |
| 2 | Supervised vs Unsupervised | 7 | Rule: labels hain→supervised, nahi→unsupervised, reward loop→RL. Anomaly detection = unsupervised (RL nahi). |
| 3 | Classification vs Regression | 10 | 5/5. "Kitna?"=regression, "Kaunsa?"=classification. Multi-class vs binary bhi. |
| 4 | Overfitting + fixes | 6 | Detection ✓ (train high, test low). Fixes ratta: augmentation, simpler model, dropout/regularization, early stopping. |
| 5 | Precision/Recall | 9 | scale_pos_weight bola (Tata XP)! Add: threshold tuning + trade-off zikr. |
| 6 | LLM basics | 5 | Token/context window confuse hue the. token=ginti unit · temperature=creativity knob (0=JSON/code) · context window=ek waqt ki yaaddasht. |
| 7 | Embeddings | 8.5 | Pipeline ✓. Fix: embedding model ≠ LLM (do alag models). |
| 8 | RAG | 8.5 | Full pipeline ✓. Add: top-k, source citation, "RAG = Retrieval-Augmented Generation" full form. |
| 9 | RAG vs FT vs Prompt | 9 | 3/3. Rule: knowledge gap→RAG · behaviour gap→FT · instruction gap→prompt. Order: prompt→RAG→FT. |
| 10 | Agents + Jarvis pitch | 4 | ❌ #1 PRIORITY. 45-sec model pitch drafted (definition→architecture→traced example→safety+daily use) — RATTA + bol ke practice. |

## #1 Finding
Scenario/MCQ checks mein sharp (5/5, 3/3), **open-ended "explain/pitch" par thin 1-line answers** — Python mock ka bhi yehi pattern. Formula har answer ke liye: **definition → example → apna project.**

## Ready-made interview lines (is session se)
- LangChain vs SDK: "Saarthi mein LangGraph se 7-agent orchestration, Jarvis mein direct Claude Agent SDK — framework tabhi jab wo value add kare."
- Overfitting: "Train 98/test 65 → augmentation + dropout + early stopping, fir validation curve."
- Recall-first: "Defect miss mehenga, false alarm sasta — scale_pos_weight + threshold ghatana; precision trade-off accepted."
- Jarvis pitch: full version drill log conversation mein (2026-07-06) — 45 sec, 4-part structure.

## Next session
- Jarvis pitch bol ke rehearse (English speaking slot ke saath jod sakte hain)
- Overfitting fixes + LLM basics re-check
- Python drill resume: Topic 5 (map/filter) se — dekho mock-50-python.md Mock log
