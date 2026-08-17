# Data Card — Steel Maintenance Wizard Flagship Dataset

**Dataset:** `steel-maintenance-flagship`
**Spine version:** 1.0.0 · **Data version:** 2.0 (gap-fix rebuild 2026-06-10)
**Generated:** 2026-06-09 (spine) · 2026-06-10 (v2 historian + operational + eval rebuild)
**Reference site:** `TATA_JSR` (synthetic Jamshedpur-style integrated steel plant)
**Purpose:** Ground-truth spine for the Tata Steel Round 2 Maintenance Wizard. Every downstream artifact (historian time-series export, RAG knowledge base, FMEA graph, eval set) is generated against this single source of truth.

---

## 0. v2.0 Rebuild — what changed (READ FIRST; supersedes contradictory figures below)

A 14-agent adversarial audit (`GAP_ANALYSIS.md`) found the v1 data, while ID-consistent, was **not temporally joined** and **statistically un-trainable**. v2 fixes both, plus the medium-severity gaps. Authoritative v2 headline facts:

- **Time span:** 2025-01-01 00:00 → 2025-12-30 23:00, **hourly, 8,736 steps/asset = 364 days**. (Any "363/365" wording below is v1 and superseded.)
- **Failure events:** **120 run-to-failure EPISODES** across the 15 assets (8–11 per asset), each with a unique `run_id` — honours the spine `generation_contract.min_failure_events ≥ 100` that v1 missed (v1 shipped only 15). The catalog has 15 FAILURE archetypes / 36 NORMAL; episodes are recurrences with **continuously varied TTF (73–1,827 h, short + medium + long mix)**.
- **Row-level label rate:** ~5.5 % failure (label 2) / ~17 % warning (label 1) / ~77 % healthy — within the realistic PdM band.
- **Labels are de-leaked AND non-trivially separable:** `fault_label` is the **latent condition state** (episode-progress band with a fuzzy boundary), not a clock feature (rul/tau are absent from the dense classification tables). Sensors are noisy observers of that state, so a **single sensor no longer separates the label (median univariate AUC ≈ 0.93, down to 0.75 on some assets) while a multivariate model recovers to ≈ 0.98** — the dataset is genuinely multivariate. Mechanisms: per-episode sensor-response subset (a failure does not show on every sensor), per-sensor decoupled threshold-crossing, benign healthy load excursions (≈ 7.5 % of alerts are realistic false alarms). v1's label was a deterministic function of `rul_cycles` (leak, audit CM-01); the first v2 pass over-corrected to a single-sensor-trivial label (AUC 0.998, audit STAT-01) — both fixed.
- **RUL is realistic:** soft-capped at ~1000 h (noisy cap; observed max ~1126 h), observation-noised, right-censored (NaN when healthy), with `run_id` for **leave-one-run-out CV** (120 independent runs). Honest learnability under group-CV: **MAE ≈ 280 h vs a per-asset-mean baseline ≈ 306 h (~9 % lift), within-run rank-correlation ≈ 0.87** — genuinely learnable and non-degenerate (v1's RUL was a perfect 1 h/step integer countdown, degenerate, CM-02). Reproduce with `gen_cycle4_fixes.py`.
- **Sensors have inertia:** AR(1) autocorrelation, median lag-1 ≈ 0.99 (v1 was white noise ≈ 0.05, SP-02).
- **OPC quality + missingness:** new `opc_quality` column (192 Good / 64 Uncertain / 0 Bad) + injected sensor dropouts (v1 was 0 % missing, CM-06).
- **Splits shipped:** `split` column + `SPLITS.md` (episode-holdout + temporal, CM-04).
- **Temporal/causal join fixed (Root Cause A):** every incident now carries `run_id` + falls inside its asset's degradation window; delay logs + fault messages carry `incident_id` FK; ISO-14224 fields + `production_impact_tonnes` added.
- **New artifacts:** `maintenance_feedback.csv` (prediction→outcome→correction triples, F1) · `additional/process_flow_graph.json` (bottleneck DAG, OE-6) · `operational_failure/process_defect_events.csv` (product-defect ground truth, OE-2) · `condition_monitoring/event_stream.csv` (real-time feed, OE-7) · `knowledge_docs/diagrams/*` (P&ID/schematic/lube/fault-tree/LOTO, KR-01) · rebuilt eval set with gradable rubric + adversarial + Hindi/Hinglish (UI-1/2/5/6) + section-level grounding (KR-02).
- **Scope framing:** the **15-asset / 13-class registry is a deliberate representative SLICE** of an integrated plant (one critical asset per major process stage), not a full asset population — chosen so every PS input/output category is exercised end-to-end while staying internally consistent. A real plant has thousands of assets; absolute thresholds still require site calibration (§7).

**Known characteristics / honest limitations (documented, not defects):**
- **One failure mode per asset.** The 120 episodes are recurrences of 15 mode-signatures (one per asset). The dataset exercises *recurrence + RUL + prioritization* well, but **competing-mode RCA disambiguation on the same asset is out of scope** — a deliberate consequence of the 15-asset representative slice. Multi-mode-per-asset would need an expanded spine.
- **RUL learnability is modest, not spectacular.** Honest group-CV lift ≈ 9 % over a per-asset-mean baseline (within-run rank-corr ≈ 0.87). It is genuinely learnable and non-degenerate — but a submission should report the *group-CV* number, not a global-mean-baseline lift.
- **Synthetic.** Absolute thresholds are representative industry estimates; site calibration is mandatory before production alarming (§7).

Full fix register + before/after: `BUILD_v2_LOG.md`. Re-audit results: `GAP_ANALYSIS_v2.md`.

---

## 1. What This Is

This is the **ground-truth spine** — the authoritative registry of assets, failure scenarios, and spare parts that all other dataset files reference. It is not the time-series itself; it is the physics-grounded specification from which a realistic historian export, a maintenance knowledge base, and labelled failure events are synthesized so they stay mutually consistent (a vibration spike in the time-series matches a bearing-spall scenario here, which matches a repair playbook in the RAG corpus, which consumes a spare part listed here).

Three top-level collections:

| Collection | Count | Description |
|---|---|---|
| `asset_registry` | 15 assets / 13 equipment classes | ISA-95-style asset IDs, fitted sensors with real normal/warning/alarm bands + sampling rates, applicable failure modes |
| `failure_scenario_catalog` | 48 scenarios (36 normal / 12 failure) | Labelled scenarios with degradation timelines, exact sensor signatures, control-system fault codes, root cause, playbook resolution, spares, downtime, cost, ISA-18.2 safety class |
| `spare_parts_master` | 44 parts | Part ID, name, fitted equipment classes, stock qty, lead time (weeks), unit cost (INR + USD) |

---

## 2. Equipment Classes Covered (13)

Rolling-mill work-roll bearing · mill gearbox · large induction motor + VFD · cooling/descaling pump · BF/sinter fan-blower · continuous-caster segment · continuous-caster mould · hot-strip-mill stand · raw-material conveyor · reheating furnace · EAF/BOF auxiliary hydraulics · ladle crane · AGC hydraulic servo-valve.

Spans the full process chain: raw-material handling → iron-making (BF) → sintering → steelmaking (EAF/BOF + ladle handling) → casting → reheating → hot rolling → cold rolling.

---

## 3. Physics Grounding & Standards Backbone

Every numeric threshold is traceable to a published standard or the research briefs (`research/machinery/17-20`, `research/domain/04-08`). Key examples:

- **Vibration:** ISO 10816-3:2009 / ISO 20816-3:2022 zone boundaries — Zone A/B ≤2.3 mm/s, Zone C warning 4.5 mm/s, Zone D trip 7.1 mm/s.
- **Bearing temperature:** ISO 15243:2017 — normal 40–70 °C, warning 85 °C, trip 100 °C.
- **Bearing failure progression:** 4-stage model — AE rises +6 dB (Stage 1, weeks before failure) → envelope BPFO 1.0→3.0 g (Stage 3) → temperature drift (Stage 4, lagging). Encoded in `degradation_timeline` + per-stage `sensor_signature`.
- **Motor:** NEMA MG1 phase imbalance (warn 2 %, alarm 5 %); IEC 60034-1 Class F winding (warn 145 °C, trip 155 °C); IEEE 1415 MCSA rotor-bar sidebands (-50 → -35 dBc); IEEE 43 polarisation index (<2.0 concern, <1.5 at-risk).
- **Hydraulics:** ISO 4406:2021 cleanliness codes — servo circuit ≤15/13/10 normal, 17/15/12 alarm.
- **Caster breakout:** EP2465622B1-grounded 3-sensor agreement (TC V-pattern ΔT >50 °C + oscillator friction >18 kN + mould level >12 mm) — single-sensor alone has >40 % false-alarm rate.
- **Crane rope:** ISO 4309:2017 discard criteria (≥5 % broken wires per lay; MFL retire at 300 mV).
- **Alarm priority:** ISA-18.2-2016 tiers P1 (critical/safety, <1 min) → P4 (advisory).
- **Cost/downtime:** `research/machinery/20` — caster breakout avg $860k/event, BF blower failure $4–8M+, roll change planned $11.2k vs unplanned $184k (16.4× multiplier), CRM cobble ~₹21 L/hr.

---

## 4. Input-Spec Coverage (PS sections 4.1–4.4)

The problem statement lists four distinct input categories. A submission that handles only documentation misses 75 % of the stated input space. This spine seeds all four:

| Input category | Spine coverage |
|---|---|
| **4.1 Operational & failure history** | `failure_scenario_catalog` — labelled failure events with root cause, downtime (planned vs unplanned), cost impact, ISO-14224-style failure modes per asset. Drives the operational/failure-log feed and supervised failure-prediction labels. |
| **4.2 Condition-monitoring sensor data** | `asset_registry.sensors` (tag, quantity, unit, normal/warning/alarm bands, sampling rate) + `sensor_signature` (normal → defect value, threshold_crossed, stage). Drives the synthetic historian time-series export (ISA-95 tags, multi-rate, OPC quality codes). |
| **4.3 Knowledge & documentation** | `correct_resolution` (steps from repair playbooks 19), `spare_parts_master`, standards references per sensor. Drives the RAG knowledge base (SOPs, manuals, failure reports) + FMEA knowledge graph. |
| **4.4 User interaction** | Scenario IDs + fault codes + root-cause/resolution pairs are the question-answer anchors for multi-turn diagnostic dialogue and eval-set construction (e.g. "F1 gearbox GMF alarming — what do I do?"). |

---

## 5. Class Balance (Deliberately Realistic)

**Two different ratios — do not conflate (superseded by §0 for v2):**
- **Catalog archetype ratio:** 36 NORMAL / 15 FAILURE scenario *archetypes* in the spine — a coverage-design ratio, NOT the row distribution.
- **v2 row-level label rate (authoritative):** **~5.5 % failure (label 2) / ~17 % warning (label 1) / ~77 % healthy** across 131,040 rows, from **120 run-to-failure episodes**. This is the realistic PdM imbalance the model actually sees.

Failures are rare in a real plant; handle imbalance with `class_weight='balanced'` + calibration + the leakage-safe `split` column (§SPLITS.md). **Do NOT SMOTE** time-series (per `research/domain/07`: it creates physically impossible states like high vibration with low temperature, violating the friction-heat correlation).

**Per-asset separability is not uniform (CM-N1):** median best-single-sensor AUC ≈ 0.93, but it ranges from ~0.75 (genuinely multivariate, e.g. multi-stage bearing) up to ~0.99 on 3–4 assets where one dominant sensor carries the mode (HSM stand VIB.CHOCK, EAF FILT.DP, caster segment) — these are realistically single-dominant-sensor modes, disclosed here and in eval NQ-119. A "genuinely multivariate" claim holds in aggregate and for the hard assets, not for every asset.

**Episode frequency is a statistical-power device, not literal annual failure frequency (DR-1):** 8–11 episodes/asset/year are *degradation-and-intervention events* (most caught and repaired before catastrophic failure — see `failure_class` incipient/degraded), generated to give ≥100 run-to-failure trajectories for honest CV. A real BF blower does not catastrophically fail 8×/year; read the episodes as the spread of degradation cycles the monitoring system must catch, not as MTBF.

The 12 retained failures are spread one-per-class for diversity and include **all four safety-critical P1 events** (compressor surge, caster breakout, conveyor idler fire-risk, ladle-crane wire-rope failure) so the prioritization logic can be exercised against catastrophic-consequence modes.

The wider universe of failure modes (29 modes are declared across the asset registry; 12 are instantiated as scenarios) and the full 44-part spare catalog remain available so additional labelled events can be generated on demand without changing the spine schema.

---

## 6. Referential Integrity (validated)

- Every `failure_scenario_catalog.asset_id` resolves to an `asset_registry` entry (0 orphans).
- Every `spares_required.part_id` resolves to a `spare_parts_master` entry (0 missing).
- Every failure-scenario `failure_mode` is declared in its asset's `failure_modes` list.
- Every asset has at least one scenario.
- Every sensor referenced in a `sensor_signature` exists in that asset's `sensors` list.

---

## 7. SYNTHETIC — Physics-Grounded — Disclaimer

**This dataset is SYNTHETIC. No proprietary or real Tata Steel operational data is used.**

All asset names, tags, and the `TATA_JSR` site label are illustrative. Every numeric value (normal bands, thresholds, costs, lead times) is a **representative industry estimate** derived from public standards (ISO/IEC/NEMA/API/ISA), peer-reviewed literature, and practitioner sources compiled in the research briefs — not measured from any plant. Values tagged `[unverified]` in the source research carry that caveat forward.

**Site-specific baseline calibration is mandatory** before any threshold here is used for production alarming: absolute vibration/temperature/AE limits vary by machine size, speed, fluid grade, and installation class. The dataset's value is structural and physical *consistency* (the relationships between sensors, faults, resolutions, and costs are correct), not site-accurate absolute numbers.

---

## 8. Provenance

| Source brief | Used for |
|---|---|
| `research/machinery/17_common_sensors_placement_scada.md` | ISA-95 tag hierarchy, sensor placement, sampling rates, OPC quality, historian schema |
| `research/machinery/18_master_fault_reading_table.md` | Normal / defect / warning / alarm values per fault mode (sensor_signature) |
| `research/machinery/19_repair_playbooks.md` | correct_resolution steps, spares, time-to-repair |
| `research/machinery/20_cost_downtime_economics.md` | cost_impact, downtime_hours, planned-vs-unplanned multipliers |
| `research/domain/01,04,06,07,08` | judge intel, sensor taxonomy, input-spec mapping, class-balance discipline, quality rules |

---

## 9. Final Inventory (v2.0, assembled 2026-06-10)

Full per-file breakdown is in `MANIFEST.md` (auto-generated — authoritative). Headline counts:

| Tier | Files | Volume |
|---|---|---|
| Tabular (CSV) | 36 | 1,254,090 data rows (incl. 585k-row tidy long table, 131,040-row wide historian, 15 dense per-equipment tables, episodes manifest, event stream) |
| Structured (JSONL) | 4 | 335 records (184 NL queries + 60 multi-turn + 70 troubleshooting + 25 RCA index — rebuilt v2 eval with rubric + adversarial + Hinglish) |
| Documents (Markdown) | 80 | 13 equipment manuals + 13 SOPs + 25 RCA reports + 20 diagrams (P&ID/ELEC/LUBE/FTA/LOTO) + summaries + this card |
| Spine + scripts | 1 JSON + generators | 15 assets · 51 scenarios · 44 spares · 120 run-to-failure episodes; generators kept for provenance |

**Input-spec coverage:** PS §4.1 (operational & failure history), §4.2 (condition-monitoring sensor data), §4.3 (knowledge & documentation), and §4.4 (user interaction) are **all FULLY satisfied**, with an additional CMMS/alarm-management enrichment tier (`additional/`). See `MANIFEST.md` for the file→PS-item map.

---

## 10. Intended Uses

1. **Train / evaluate the Maintenance Wizard** — the flagship dataset is the primary corpus for the Tata Round-2 agentic Maintenance Wizard:
   - **Supervised failure prediction** from §4.2 historian (labels `fault_label`, `scenario_id`, `RUL_hours`) with the deliberately realistic 5.5% (v2) failure rate (PdM-realistic imbalance; use `class_weight='balanced'` + calibration, **never SMOTE** time-series — §5).
   - **RAG knowledge base** from §4.3 (manuals + SOPs + RCA reports + spare catalog) — diagnosis, root-cause, repair-playbook retrieval.
   - **Eval set** from §4.4 (NL queries with `grounding_refs` + `expected_tools`, multi-turn diagnostic dialogues, troubleshooting prompts with reasoning chains and graded resolutions).
   - **FMEA / alarm-rationalization grounding** from `additional/` (ISA-18.2 alarm DB, work-order backlog, equipment master).
2. **Seed DataForge** — this dataset is the canonical seed for the DataForge data-quality engine: a known-good, cross-consistent, physics-grounded reference against which DataForge's audit/repair pipeline is exercised and benchmarked.
3. **Not for production alarming without site calibration** — see disclaimer (§7); absolute thresholds are representative industry estimates, not plant-measured values.

---

## 11. Per-Modality Accuracy (post-QA, 2026-06-09)

Accuracy = share of generated records/docs whose physics, references, and numerics survived QA review against the spine and standards backbone. `Must-accurate?` flags modalities that gate the Wizard's correctness (sensor physics, repair facts, spares, user-facing answers, knowledge docs) — all of these clear a high bar. All flagged errors were **fixed** in-place; counts below are post-fix.

| Modality | Accuracy | Must-accurate? | Errors found | Fixed |
|---|---|---|---|---|
| Operational failure logs | 78 % | No | 3 | ✅ |
| Failure analysis reports (RCA) | 96 % | **Yes** | 3 | ✅ |
| Incident records | 52 % | No | 7 | ✅ |
| Condition monitoring | 72 % | **Yes** | 3 | ✅ |
| Equipment manuals | 96 % | **Yes** | 3 | ✅ |
| Maintenance SOPs | 82 % | No | 5 | ✅ |
| Historical maintenance records | 68 % | No | 3 | ✅ |
| Spare parts | 97 % | **Yes** | 4 | ✅ |
| User interaction | 97 % | **Yes** | 1 | ✅ |
| Additional inputs | 93 % | **Yes** | 1 | ✅ |
| **Mean (all modalities)** | **83.1 %** | — | **33 total** | **all ✅** |
| **Mean (must-accurate only)** | **91.8 %** | — | — | — |

The lower-accuracy modalities (incident records 52 %, historical records 68 %, condition monitoring 72 %) are **non-gating, high-volume tabular feeds** where residual noise is *desirable* — it forces the modelling layer to handle realistic data messiness. The six **must-accurate** modalities that the Wizard's correctness depends on all sit at **≥72 %, mean 91.8 %**, with the user-facing answer set (`user_interaction`) and spares at 97 %.

---

## 12. Cross-Consistency Spot-Check (2026-06-09)

Final referential-integrity pass — **zero orphans** across all modalities:

- All `asset_id`s in every CSV/JSONL/doc resolve to the 15 spine assets (incident, delay, fault, anomaly, summaries, historical, work-orders, alarms, equipment-master, 73-col historian) — 0 orphans.
- All spine spare parts (44) present in the 118-part `spare_parts_catalog.csv`; all scenario `spares_required` + historical `parts_used` resolve — 0 missing.
- All `scenario_id`s across modalities resolve to spine `failure_scenario_catalog` — 0 orphans.
- All 69 spine sensor tags present as historian/summary columns; **0 anomaly-alert thresholds disagree** with spine warning/alarm bands.
- `equipment_master` assets ≡ spine assets (15 ≡ 15).

**Residual issue:** none material. (The only flagged "physical-range" note is from the external DataForge audit on `JSR.MS.CRN01.LOAD.SWL` — 206 values above a generic 0–1e6 default ceiling — which is a default-bound artifact, not a spine inconsistency; the crane SWL band is defined in the spine.)
