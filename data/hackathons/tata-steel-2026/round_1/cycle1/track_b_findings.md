# Track B Findings — Swansea Thesis + SOTA ML Tricks

**Agent:** research-agent
**Date:** 2026-05-23
**Status:** Complete — agent could not write to disk, persisted via Jarvis

## Headline

The Latham 2025 EngD thesis is read through Chapter 5. It is CNN-based for time-series-plot image classification (not tabular ML directly), BUT Section 5.4 reveals a traditional ML approach with 4 statistical features achieving **91.43% accuracy** (Fine KNN winner). **Section 5.1.2-5.1.3 contain the EXACT manual decision rules Tata Steel analysts use**, which 2 perfect-100 scorers may have rediscovered.

## X1-X49 Mapping (Latham thesis cross-ref, HIGH confidence top 7)

| Competition Col | Thesis Variable | Physical Meaning | Confidence |
|---|---|---|---|
| **X13** | `RM_model_error` | RM width model error (aim vs actual at RM exit) | HIGH |
| **X41** | `FM_model_error` | FM width model error (aim vs actual at FM exit) | HIGH |
| X14 | `F11_Exit_Temperature_A` | FM exit temp (top sensor) | HIGH |
| X10 | E2 edger force average | Edger 2 average roller force | HIGH |
| X36 | F11 Temp Upper Limit | FM exit upper tolerance | HIGH |
| X34 | F11 Temp Lower Limit | FM exit lower tolerance | HIGH |
| X35 | COIL_TEMP_TOL_MINUS | Lower coiler temp tolerance | HIGH |
| X30 | ANC In Progress (binary) | Binary alarm flag | MED |
| X2 | width_alarm | Spread/Squeeze profile violation | MED |

## The Possible Killer Rule (per thesis §5.1.2 / 5.1.3)

```python
# Manual rules used by Tata Steel analysts:
defect_pred = ((abs(X13) > 5) | (abs(X41) > 5) | (X2 == 1)).astype(int)
```

**Hypothesis: this exact rule may be what the 100-score contestants found.**

**Caveat:** Our X13 mean is 868, X41 mean 0.586 — the thresholds ">5" might not literally apply, OR the units are encoded differently in our anonymised data. Need empirical test.

## ML Tricks Ranked (for 1352 rows + 4.9% prevalence)

| Rank | Method | Insight | OSS Lib | Expected Lift |
|------|--------|---------|---------|---------------|
| 1 | **TabPFN v2** | Prior-fitted transformer, near-zero tuning, native imbalance | `pip install tabpfn` | +5–12 OOF |
| 2 | **ADASYN** | Better than SMOTE for rare events | `imbalanced-learn` | +3–6 |
| 3 | **Focal Loss for LGB/XGB** | Downweights easy negatives | `imbalance-xgboost` | +2–4 |
| 4 | **Mondrian Conformal Prediction** | Class-conditional coverage guarantees | `crepes` | +1–3 |
| 5 | **Physics-rule hard features** | Binary features from thesis thresholds — exact rule Tata analysts use | numpy | **+3–8 (single addition)** |

## 100-Score Mystery — Three Hypotheses

(a) **LB probing** — submit binary masks, recover labels mathematically. ~6-8 probes suffice
(b) **Physics rule perfect separator** — e.g., `width_alarm=True AND rm_model_error>5`
(c) **Train/test leakage via CoilID ordering** — exotic

If (b), V8 + thesis rule would also hit 100. Test the rule first before any ML.

## V8 Build Priority

1. **Test physics rule alone on OOF** — if >80, that's the contest answer
2. Add binary thresholds as features: `abs(X13) > tau_13`, `abs(X41) > tau_41`, scan for best tau
3. Run TabPFN v2 as ensemble member
4. Replace SMOTE with ADASYN
5. Focal loss in LGB/XGB

## Sources

- Latham, S. (2025). "Detecting Width-Related Defects in the Hot Strip Mill Process using Deep Learning and Expert Knowledge." EngD Thesis, Swansea University — LOCAL: `references/latham_2023_swansea_thesis.pdf`
- TabPFN v2: https://github.com/PriorLabs/TabPFN
- Imbalance-XGBoost: https://arxiv.org/pdf/1908.01672
- ADASYN vs SMOTE: https://doi.org/10.3390/computers15030151
- RC3P (NeurIPS 2024): https://proceedings.neurips.cc/paper_files/paper/2024/file/ee66188f019df7199c4c06320f698fa1-Paper-Conference.pdf
