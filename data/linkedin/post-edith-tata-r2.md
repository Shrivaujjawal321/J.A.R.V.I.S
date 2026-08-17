# LinkedIn Post — EDITH (Tata Steel Hackathon R2)

> Status: FINAL — YouTube demo link added. Ready to publish.
> Video: https://youtu.be/2upa03Ye9Zg

---

## Post (ready to publish once https://youtu.be/2upa03Ye9Zg filled)

A steel plant never really sleeps — and when a critical asset fails without warning, every minute of unplanned downtime burns money and risk.

For Round 2 of the **Tata Steel National AI/ML Hackathon**, that was the problem I set out to solve.

**The problem 👇**
In heavy industry, maintenance is still mostly *reactive*. By the time a pump, motor or furnace throws a fault, the damage is done. The knowledge needed to act fast — failure histories, P&IDs, SOPs, past root causes — sits buried across manuals and logs that a floor engineer can't search mid-crisis. The result: slow diagnosis, guesswork on root cause, and no reliable read on *how long an asset has left*.

**What I built — EDITH, an agentic maintenance copilot 👇**
A 5-agent reasoning chain that takes a live alarm and walks it end to end:
**Diagnosis → Root Cause → Remaining-Useful-Life → Prioritization → Recommendations.**

- Grounded on a purpose-built **1.25M-row physics-based dataset** (15 assets, 120 run-to-failure episodes, 80 knowledge docs) — so every number comes from *structured ML inference, not an LLM guess*.
- A **hybrid RAG pipeline** (embeddings + FlashRank reranking + a DeBERTa faithfulness gate) that scores every cited claim against its source — if it can't back a statement, it says so. Zero hallucinated facts.
- **Live SSE-streamed monitoring** of 15 assets that auto-fires the full diagnosis on the first sustained alarm — no engineer needed to start it.
- Delivers all six required outputs — diagnosis, root cause, RUL, risk band, prioritized repair steps, and a downloadable PDF report. Fast path responds in **under 300ms**; deep reasoning in ~11s.

It qualified into Round 2 of the national competition — and honestly, building it taught me more about *trustworthy* industrial AI than anything else I've done.

🎥 90-second demo: https://youtu.be/2upa03Ye9Zg
💻 More of my work: https://github.com/Shrivaujjawal321 · https://ujjawal-shrivastav.vercel.app/

If you're working on industrial AI, predictive maintenance, or agentic systems — I'd love to connect.

#AI #MachineLearning #AgenticAI #PredictiveMaintenance #TataSteel #RAG #IndustrialAI #LLM
