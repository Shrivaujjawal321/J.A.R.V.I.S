# Flagship Dataset — Adversarial Gap Analysis (what we missed)

**Method:** 14-agent workflow — 7 deep finders (one per dimension) + 7 adversarial verifiers that re-read the actual files to confirm/refute each gap. 960k tokens. Run 2026-06-10.

**Verdict tally:** 5 critical · 12 high · 21 medium · 1 refuted.

The dataset's standards-grounding, spare-parts side, and RAG corpus richness are genuinely strong. The gaps cluster into **three root causes** below. The team's own "0 orphans / 83% accuracy" self-audit is true *at the ID-string level* — but it never checked **temporal/causal join** or **ML statistical validity**, which is where the real holes are.

---

## ROOT CAUSE A — The four modalities live in disjoint time universes (the biggest miss)
*Covers: OFH-01, OFH-02, SP-03, DR-01 — all CRITICAL/HIGH, all confirmed.*

The "0 orphans" referential integrity is on `scenario_id`/`asset_id` strings only. **On the timeline, the modalities don't line up:**

- `incident_records.csv`: 2024-01-02 → 2025-05-30 (**109 of 150 incidents are in 2024**)
- `sensor_timeseries_long.csv` / `rul_trajectories_long.csv`: **2025 only**
- RCA reports: dated 2025-07 → **2026-05** (months-to-2yr *after* the incidents)

**Consequence:** 109/150 incidents (73%) have **zero co-occurring sensor data**. Tested the join directly — only **3 of 34** 2025 unplanned incidents fall inside their own asset's degradation window. The reactive-troubleshooting workflow the PS demands ("show me the sensor trend that led to INC-XXXX") **has no answer for most incidents.**

Also: `equipment_delay_logs.csv` and `fault_error_messages.csv` carry **no `incident_id` FK** — they're independent random streams. Failure-named delay codes exist (`GEAR_TOOTH_CRACK`, `BEARING_SPALL_BPFO`) but their timestamps don't align with the matching incidents. So the **incident → delay → spare → RCA causal chain is broken.**

> **Self-own:** the repo already contains `fix_incident_records.py` whose docstring says it re-bases incidents into the 2025 window "so each incident co-occurs with its precursor fault/delay rows" — **it was written but never applied.** The shipped CSV is the pre-fix timeline.

---

## ROOT CAUSE B — The ML targets are statistically un-trainable AND leaky
*Covers: SP-01, CM-02, CM-03, OE-1 (failure/RUL power) + CM-01, CM-04 (leakage) + SP-02 (noise). CRITICAL/HIGH, confirmed.*

PS §5.1 wants RUL + failure prediction. The data **cannot demonstrate it with any rigor:**

- **N = 15 failure events total — exactly 1 per asset, 1 mode each.** 51 scenarios in the spine but only 15 are FAILURE, each on a distinct asset. So **per-class hold-out = 0 positives.** No leave-one-run-out CV is possible; any RUL MAE is an N=1 anecdote.
- **RUL is a perfect linear countdown (1 cycle/hour).** `BF.BLW.FAN01` = 1389,1388,…,2,1 with the *only* consecutive diff being exactly 1.0 — zero noise, zero knee, zero censoring. **Counting rows backward beats any model.** Sensor features add nothing.
- **`fault_label` is a deterministic 3-bucket of `rul_cycles`** (e.g. BRG01: label0 if rul≥673, label1 673–253, label2 ≤253). The supervised label is a *clock band, not a sensor state* — a model just memorises a countdown.
- **No train/val/test split or leakage guard anywhere.** A naive random row-split puts adjacent hours of the same ramp in train AND test → inflated metrics. (The DataForge "leakage 100" score is misleading — it scores 100 only because `rul_cycles` was excluded from the dense tables, so the auditor never sees the label *is* the clock.)
- **Partial:** the *temperature/pressure/RMS scalar* channels are white noise (lag-1 ≈ 0.05). BUT — verifier correction — the **degradation feature channels are realistic** (BPFO envelope lag-1 = 0.994, oil-Fe 0.993, monotonic 15× rise to failure). So RUL *slope* IS cleanly estimable on the right channels; it's the flat scalar channels that dent the "physics-grounded" claim.

---

## ROOT CAUSE C — Eval set can't catch the dangerous failure (safety blind spot)
*Covers: UI-2 (CRITICAL), UI-1, KR-02, UI-4 (HIGH), UI-5, UI-6 (MED).*

- **UI-2 (critical):** **0/150 queries are adversarial / unanswerable / out-of-scope.** No query about a nonexistent asset, no "insufficient data — clarify", no off-topic ask. For a safety assistant where a confident-wrong *"safe to run"* is a safety event — and the webinar literally scores **"doesn't break"** — this is the single most dangerous eval blind spot.
- **UI-1 (high):** no gradable rubric / judge harness. `expected_answer` is free text with no `required_facts` / `forbidden_claims` / scoring fields → **you cannot reproducibly score the Wizard.** (Mitigant: `troubleshooting_prompts.jsonl` IS rich — reasoning chains, parts, lead-time, cost — so it's a build-on, not from-scratch.)
- **KR-02 (high):** all 631 `grounding_refs` are **file-level, never section/step-level** (0 contain `#`/`§`/`step`). The docs DO have anchors (`MAN-001 ## 1..5`, `SOP-01 S-1..S-9`) — the eval just doesn't use them. **Caps PS functional-req 4 (explainable/traceable) — a judged criterion.**
- **UI-4 (high):** eval is starved of evidence on RUL, prioritization, procurement, and report/logbook outputs — it mostly tests single-hop threshold lookups.
- **UI-5/UI-6 (med):** no Hindi/Hinglish/code-switched operator language (this is an *Indian* plant); multi-turn has no user-correction/context-trap turns.

---

## Feedback-loop data is entirely absent
*OFH-04 + OE-4 (HIGH/MED, confirmed).* PS functional-req 6 **mandates** a feedback-driven improvement loop. There are **zero prediction→outcome→correction triples.** `historical_maintenance_records.csv.outcome` is free-text condition notes ("Fe 3 ppm normal… no action"), not a recommendation-effectiveness signal. Only 7 of 625 records are actual breakdowns. The recurrence chains exist *in prose* (breakdown_summaries narrates a bearing failing "seventh time") but never as a structured field → the loop is **architecturally unprovable on this data.**

---

## Medium quick-hits (21 — the high-signal ones)
- **KR-01** — zero diagram doc types: no P&ID, electrical schematic, lubrication chart, fault-tree, or LOTO permit template.
- **OE-6** — no inter-asset process-flow / dependency graph → plant-level **bottleneck prioritization (PS 5.2) can't be computed or evaluated.**
- **OE-2 / DR-04** — process/product-defect detection (PS 5.1) has **no structured ground truth**; the only `quality` field is OEE-quality pinned at 1.0 even during failures.
- **CM-06** — datacard claims "OPC quality codes + multi-rate sampling" that are **absent** from every file; 0% missingness → no sensor-fault-vs-equipment-fault realism.
- **OE-7** — condition-monitoring is batch tables only; no event-ordered streaming feed (PS req 7 real-time alerting) and `anomaly_alerts` isn't globally time-sorted.
- **OFH-03** — `incident_records` lacks ISO-14224 / CMMS fields, esp. **downstream production impact in tonnes**.
- **DR-03 / SP-07** — whole plant areas absent (coke ovens, sinter detail, BOF lance, RH degasser, pickling, galvanizing, utilities) and not framed as a deliberate slice; 1-yr hourly can't show multi-year slow degradation.
- **SP-06** — datacard imbalance figures contradict each other (25% vs 12-failure vs 2.1%) and 363/364/365-day spans are unreconciled.
- **KR-05** — table-heavy docs with no chunking guidance → naive chunking fragments threshold/spare/step tables.

---

## Refuted (honest correction)
- **OE-5 (refuted):** "early catastrophic warning has no lead-time label." Actually `anomaly_alerts.csv` gives a genuine clock-independent early signal — for BRG01 the first WARNING fires 2025-06-04, label doesn't flip until 2025-06-18 (**~14-day value-driven lead, 246 alerts before transition**). Warning timeliness IS scoreable.

## Verified strengths (so the picture is balanced)
- Threshold physics correctly traceable to ISO/IEC/NEMA/ISA standards.
- The **spares side of the 5.2 join is present and usable** (`lead_time_weeks`, `on_hand_qty`, work-order `scenario_ref`).
- **Degradation feature channels are realistically autocorrelated** — RUL slope IS estimable on BPFO/oil-Fe/MFL/servo channels.
- `troubleshooting_prompts.jsonl` is genuinely rich (decomposable gold facts already there).
- Dense `by_equipment/*.csv` **already exclude `rul_cycles`** → a leakage-safe features-only export exists.

---

## Prioritized fix plan (5 days to deadline)
| # | Fix | Kills | Effort | Leverage |
|---|---|---|---|---|
| 1 | **Run `fix_incident_records.py`** + add `incident_id` FK to delay/fault logs + 5–10 recurrences/asset | Root Cause A | **S** (code already written) | Highest — restores the whole causal chain |
| 2 | Generate **5–10 varied run-to-failure runs per class** (varied TTF, add a RUL cap + obs noise + non-linear knee) + ship `SPLITS.md` (group-by-asset temporal split) + inject autocorrelation into flat scalar channels | Root Cause B | **M** | Makes 5.1 demonstrable |
| 3 | Add a **feedback table** (prediction→outcome→correction triples) + recurrence/re-fail fields | OFH-04/OE-4 | **S–M** | Unlocks PS req 6 |
| 4 | Add ~40 **adversarial/unanswerable/out-of-scope + Hindi/Hinglish** queries + a **gradable rubric** (`required_facts`/`forbidden_claims`) + **section-level** grounding_refs | Root Cause C | **M** | Safety + judged explainability |
| 5 | Add **process-flow/dependency graph JSON** + a P&ID/schematic stub + correct datacard contradictions (OPC, multi-rate, 363/364, 25%/2.1%) | OE-6/KR-01/CM-06/SP-06 | **S** | Cheap credibility |

> Strategic note: some gaps (N=1 failure per class) are inherent to a single-plant synthetic snapshot — those should be **framed honestly in the datacard/pitch** ("representative slice, not statistical population") rather than fixed. The temporal-join break (RC-A) and the leaky/degenerate RUL (RC-B) are the ones a sharp judge or a real ML run *will* expose — fix those first.
