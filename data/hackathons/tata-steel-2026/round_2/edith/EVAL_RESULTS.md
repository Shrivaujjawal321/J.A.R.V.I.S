# EDITH — Measured Accuracy (end-to-end eval)

EDITH was evaluated **end-to-end** (live `/api/ask` → multi-agent pipeline → scored answer)
against the dataset's **254-item gold eval set** using its deterministic eval
harness (strict fact matching + forbidden-claim gate — no LLM judge, fully reproducible).

| Metric | Value |
|---|---|
| Gold items run | 254 (errors: 0) |
| **Fact recall (answerable, n=213)** | **0.13** |
| **Forbidden-claim violations** (confident wrong statements) | **2** |
| Grounding-citation match | 0.05 |
| **Guardrail behavior** (adversarial/unanswerable, n=41) | **0.341** correct (refuse/clarify instead of guessing) |
| Latency p50 / p90 | 313 ms / 12520 ms |

Per-language fact recall: {"en": {"n": 187, "mean_fact_recall": 0.125}, "hinglish": {"n": 26, "mean_fact_recall": 0.167}}

Reproduce: `python eval_run.py` (backend running). Raw per-item results: `data/eval_results.json`.
