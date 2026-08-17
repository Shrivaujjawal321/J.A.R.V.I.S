# Flagship Dataset v2 — Gap Analysis & Rebuild Journey

**What this is:** the record of how the `steel-maintenance-flagship` dataset went from v1 (ID-consistent but temporally-disjoint and statistically un-trainable) to v2.1 (fully cross-consistent, ML-trainable, judge-defensible). Driven by repeated 14-agent adversarial audit gates (find → fix → re-audit), each finding independently verified against the actual files.

**Method:** every cycle ran 7 deep finder agents (one per dimension: sensor-ML, failure-history, RAG-knowledge, user-eval, output-enablement, domain-realism, scale-statistics) + 7 adversarial verifiers that re-read the files to confirm/refute. ~2.7M tokens across the gates.

---

## Convergence at a glance

| Gate | Critical | High | What the highs were |
|---|---|---|---|
| **Audit 1 (v1)** | **5** | 12 | temporal-join broken · ML un-trainable (N=1) · degenerate RUL · leaky labels · no adversarial eval |
| **Audit 2 (after cycle-1 rebuild)** | **0** | 7 | templated incidents · single-sensor-separable label · bimodal TTF · equipment_master corruption · oil-grade conflict · dangling eval anchors · no gold ranking |
| **Audit 3 (after cycle-2)** | **0** | 4 | stale "137" counts · RUL-lift overstatement · 1 bad eval ref · ranking-rule inconsistency (all small/doc) |
| **Audit 4 (after cycle-3/4)** | running | — | — |

Criticals: **5 → 0 → 0**. Highs: data-architecture → realism → documentation-only. The two original root causes (temporal join, ML trainability) closed in cycle-1 and **never reappeared**.

---

## The two original root causes (Audit 1) — CLOSED

### Root Cause A — modalities lived in disjoint time universes
v1's "0 orphans" was true only on `scenario_id` strings. On the timeline, 73 % of incidents (2024) had **zero** co-occurring sensor data (2025-only), and RCAs were dated months-to-2yr after. The reactive workflow "show me the sensor trend that led to INC-XXXX" had no answer.

**Fix:** every incident is now generated **from** a sensor episode — it carries `run_id` and falls inside that asset's degradation window (verified 120/120). Delay logs, fault messages, defect events, feedback, and RCA reports all carry `incident_id`/`run_id` FK. **0 orphans across every causal link.**

### Root Cause B — the ML targets were un-trainable and leaky
v1 had 15 failure events (1/asset → no per-class CV), a perfect-linear-countdown RUL (degenerate), and a `fault_label` that was a deterministic function of the clock (leak).

**Fix:** **120 run-to-failure episodes** (8–11/asset, honouring the spine's own `min_failure_events ≥ 100` contract that v1 missed); RUL is soft-capped + noised + right-censored with `run_id` for leave-one-run-out CV; labels are the **latent condition state** (not the clock, not a single sensor). Honest ML: RUL group-CV rank-corr ≈ 0.87 (~9 % MAE lift over per-asset-mean); failure classification multivariate AUC ≈ 0.98 while **single-sensor AUC ≈ 0.93** (down from a trivially-separable 0.998) — genuinely multivariate.

---

## Cycle-by-cycle fixes

**Cycle 1** (closed all 5 criticals): multi-episode sensor regen · AR(1) autocorrelation (lag-1 0.05 → 0.99) · de-leaked latent labels · noisy/capped/censored RUL · OPC quality + dropouts · train/val/test splits · temporal-join operational layer · feedback table · process-flow graph · defect ground truth · event stream · 20 diagram docs (P&ID/ELEC/LUBE/FTA/LOTO) · eval rebuilt (180 queries, 35 adversarial, 30 Hinglish, rubric, section-grounding).

**Cycle 2** (closed all 7 highs): medium-TTF episodes (continuous TTF) · per-episode sensor-response subset + benign healthy excursions (single-sensor AUC 0.998 → 0.926; 7.5 % realistic false alarms) · per-incident cost/downtime dispersion (14 → 120 unique costs) · detection-latency variance · equipment_master regenerated clean (38 fields) · oil grade reconciled to ISO VG 220 · 100 % of eval anchors resolve · gold bottleneck ranking.

**Cycle 3/4** (closed all 4 highs, all small): RUL-lift claim corrected to honest group-CV everywhere · stale "137" → 120 (generators made dynamic) · eval incident refs clamped to valid range · bottleneck ranking recomputed monotonic with component columns · per-incident diagnostic-text variation (root_cause 26 → 108 unique) · failure_class decoupled from severity (now detection-timing) · zero-downtime incidents removed · anomaly_alerts + RCA reports given incident/run FK · OPC decode legend shipped.

---

## Final state

- **36 CSV (~1.25 M rows) · 4 JSONL · 79 Markdown docs · 120 episodes · ~5.5 % failure rows.**
- **0 orphans** across spine ↔ episodes ↔ incidents ↔ delay/fault/defect/feedback/RCA/anomaly (ID **and** temporal/causal).
- Every PS §4 input + §5 output category has ground truth **and** an eval path.
- Honest, documented limitations: one failure-mode per asset (representative slice); RUL learnable but modest; synthetic (site calibration required).

Reproduce: `gen_condition_monitoring_v2.py` → `build_long_and_dense_v2.py` → `gen_operational_v2.py` → `gen_structural_v2.py` → `gen_cycle2_fixes.py` → `fix_eval_anchors.py` → `gen_cycle4_fixes.py` → `gen_manifest_v2.py`. Full register: `BUILD_v2_LOG.md`.
