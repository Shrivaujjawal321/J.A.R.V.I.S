export const meta = {
  name: 'flagship-v2-reaudit',
  description: 'Re-audit gate: confirm v2 closed the gaps + hunt new gaps introduced by the rebuild',
  phases: [
    { title: 'Re-audit', detail: '7 finders verify closure + hunt new gaps on v2' },
    { title: 'Verify', detail: 'adversarially re-check each finding against the files' },
  ],
}

const DIR = '/home/ujjwal/Documents/J.A.R.V.I.S./data/hackathons/tata-steel-2026/round_2/dataforge/datasets/steel-maintenance-flagship'

const V2 = [
  'The dataset was REBUILT (v2.1, two fix-cycles). A first audit found root-cause gaps (temporal join, ML un-trainable, no adversarial eval) — all closed. A second audit found 7 highs (templated incidents, single-sensor-separable label, bimodal TTF, equipment_master corruption, oil-grade conflict, dangling eval anchors, no gold bottleneck ranking) — all claimed fixed in this cycle-2. VERIFY each claim with evidence, then hunt for any REMAINING or NEW material gap.',
  '- 120 run-to-failure EPISODES (8-11 per asset, run_id each), CONTINUOUSLY varied TTF 73-1827h via a short+medium+long mix (episodes_manifest.csv kind column).',
  '- fault_label is LATENT-CONDITION (episode-progress band, fuzzy boundary), NOT a clock function; rul/tau NOT in the dense by_equipment tables. De-leaked AND non-trivially separable: single-sensor univariate AUC ~0.93 (min 0.75), multivariate ~0.98. Mechanisms: per-episode sensor-response subset, per-sensor decoupled crossing, benign healthy excursions (~7.5% false alarms). RUL leave-one-run-out MAE ~137h vs ~379h baseline.',
  '- RUL: piecewise cap (<=1000h), observation noise, right-censored (NaN when healthy), run_id for LORO-CV (137 runs) in rul_trajectories_long.csv.',
  '- AR(1) autocorrelation median lag-1 about 0.99 (was white noise 0.05 in v1).',
  '- opc_quality column (192 Good / 64 Uncertain / 0 Bad) + injected dropouts; split column (train/val/test) in raw + dense + rul; condition_monitoring/SPLITS.md documents the protocol.',
  '- TEMPORAL JOIN: every incident_records row has run_id + falls inside its asset degradation window; equipment_delay_logs + fault_error_messages carry incident_id FK; ISO-14224 fields + production_impact_tonnes.',
  '- Cycle-2: incidents now have PER-INCIDENT dispersion (cost 120 unique values, downtime/severity vary within asset, recurrence-escalating cost) + detection latency (detection_lead_hours 24-1443h, no longer pinned to onset). equipment_master.csv regenerated clean (all 38 fields). Oil-film bearing grade reconciled to ISO VG 220 across spare catalog + LUBE-01 + MAN-001. All eval md#anchor grounding_refs resolve to real headings. additional/bottleneck_gold_ranking.csv added (gold prioritization ranking).',
  '- maintenance_feedback.csv: 137 prediction-to-outcome-to-correction triples + days_to_next_failure recurrence.',
  '- additional/process_flow_graph.json: 15-node inter-asset dependency DAG for bottleneck prioritization.',
  '- operational_failure/process_defect_events.csv: 874 product-defect events (424 equipment-linked) = process-defect ground truth.',
  '- condition_monitoring/event_stream.csv: 45789 time-ordered events (real-time feed).',
  '- knowledge_docs/diagrams/: 20 docs (P&ID, ELEC, LUBE, FTA, LOTO) + INDEX.csv.',
  '- user_interaction rebuilt: nl_queries.jsonl 180 (35 adversarial/refusal, 30 Hinglish, rubric + expected_behavior on all, section-level grounding_refs), troubleshooting_prompts.jsonl 70, multiturn_conversations.jsonl 60 (28 corrections). EVAL_CARD.md present.',
  '- datacard.md section 0 v2 changelog reframes the 15-asset registry as a deliberate representative SLICE.',
  'Cross-modality claim: 0 orphans including the temporal/causal join.',
].join('\n')

const DIMS = [
  { key: 'sensor-ml',
    persona: 'staff ML/data scientist shipping RUL and anomaly models on industrial historian data',
    focus: `CONDITION-MONITORING ML (PS 4.2 + output 5.1). Read condition_monitoring/* (raw_sensor_timeseries, sensor_timeseries_long, rul_trajectories_long, by_equipment dense tables, anomaly_alerts, SPLITS.md, episodes_manifest). CONFIRM with numbers: at least 120 failure episodes with run_id and varied TTF; RUL is no longer a perfect 1/step countdown (noise + cap + censoring); fault_label is recoverable from sensors yet AUC < 1 (not trivially separable) and rul/tau are absent from the dense tables; AR(1) autocorrelation present; split column enables leakage-safe CV. Then HUNT NEW gaps: did the band-mapping make sensors unrealistically smooth or piecewise-linear? are the episodes near-duplicates (same shape/TTF per asset)? is the fuzzy label boundary realistic? any NEW leakage (does opc_quality or split correlate with the label; can split be inferred from features)? are short vs long episodes separable by a tell-tale artifact?` },
  { key: 'failure-history',
    persona: 'reliability engineer (CMRP) who reads incident logs daily',
    focus: `OPERATIONAL AND FAILURE HISTORY (PS 4.1). Read operational_failure/* (incident_records, equipment_delay_logs, fault_error_messages, process_defect_events) and maintenance_feedback.csv. CONFIRM: incidents carry run_id and co-occur with the sensor degradation window; delay/fault rows carry incident_id FK; ISO-14224 fields + production_impact_tonnes present; recurrence/feedback exists. Then HUNT NEW gaps: are the FK links physically plausible in timing (precursors before failure)? is production_impact_tonnes realistic in magnitude? are downtime/cost consistent with the scenario? did dropping the old incident set lose realism (MTBF spread, deferred maintenance, near-miss)? is the feedback table too clean (prediction almost always correct)?` },
  { key: 'rag-knowledge',
    persona: 'senior RAG and knowledge-engineering lead',
    focus: `KNOWLEDGE AND RAG (PS 4.3). Read knowledge_docs/* including the new diagrams/* (PID, ELEC, LUBE, FTA, LOTO) + INDEX.csv, and spare_parts_catalog. CONFIRM the new diagram doc types exist and spares carry lead time. Then HUNT NEW gaps: are the new diagram docs consistent with the spine (real tags, thresholds) or do they contradict the manuals? coverage holes still (assets or failure modes with no SOP)? chunking guidance? do the section anchors the eval cites actually exist as headings in the target docs?` },
  { key: 'user-eval',
    persona: 'LLM eval lead who builds gold eval sets',
    focus: `USER INTERACTION AND EVAL (PS 4.4). Read user_interaction/* (nl_queries 180, troubleshooting 70, multiturn 60, EVAL_CARD.md). CONFIRM: gradable rubric (required_facts/forbidden_claims) on all records; adversarial/unanswerable/out-of-scope present; section-level grounding_refs resolve to REAL headings/ids; Hindi/Hinglish present; multi-turn corrections present. Then HUNT NEW gaps: do any grounding_refs dangle (point to a non-existent heading/id)? are the required_facts actually correct per the spine? are rubrics deterministically scorable? is difficulty still skewed to lookups? any rubric that would pass a wrong answer?` },
  { key: 'output-enablement',
    persona: 'product-minded ML architect mapping required OUTPUTS back to the data',
    focus: `OUTPUT-ENABLEMENT (PS 5.x + functional req 6/7). For EACH output verify the v2 data now enables AND lets you evaluate it: 5.1 RUL (rul_trajectories + run_id), early catastrophic warning (anomaly_alerts lead time before label flip), process-defect detection (process_defect_events); 5.2 risk (severity/safety_class), plant-level bottleneck prioritization (process_flow_graph + concurrent incidents + spares lead time jointly); 5.3 procurement (spares lead time/stock/cost); 5.4 reports; req6 feedback loop (maintenance_feedback); req7 real-time alerting (event_stream). HUNT: which outputs STILL lack ground truth or an eval harness? is process_flow_graph actually usable to RANK a real bottleneck, and is there any gold ranking to score prioritization against?` },
  { key: 'realism-defensibility',
    persona: 'ex-Tata-Steel Jamshedpur maintenance manager turned hackathon judge',
    focus: `DOMAIN REALISM AND JUDGE-DEFENSIBILITY. Read the spine, the new diagrams, process_defect_events, process_flow_graph, incident_records, maintenance_feedback, datacard section 0. CONFIRM the 15-asset slice is now framed honestly. Then HUNT what a real steel expert still flags: are the new artifacts (defect types, lube grades, fault trees, process-graph buffer hours, production_impact_tonnes) physically credible? any number that screams synthetic (too-round, impossible rate)? contradiction between the new diagram docs and plant physics? are Indian-context details (vendors, CMMS, INR costs) credible?` },
  { key: 'scale-statistics',
    persona: 'applied statistician assessing power and distributional realism',
    focus: `SCALE, DISTRIBUTION AND STATISTICAL POWER. Read the manifest, raw/long sensor files, anomaly_alerts, episodes_manifest, rul_trajectories. CONFIRM: 137 independent run-to-failure realizations now support train + validate; failure-row rate about 4% is honest; LORO-CV feasible. Then HUNT NEW statistical tells: are the 137 episodes truly independent or near-duplicate shapes per asset? are sensor distributions still too clean (gaussian, identical variance, generator artifacts)? does the split avoid leakage (no asset or episode in both train and test)? is the alert-to-failure ratio realistic now? any internal count contradiction across datacard/manifest? does opc_quality or split accidentally encode the label?` },
]

phase('Re-audit')

const FINDINGS_SCHEMA = {
  type: 'object', required: ['dimension', 'closed', 'remaining_or_new'],
  properties: {
    dimension: { type: 'string' },
    closed: { type: 'array', items: { type: 'object', required: ['gap', 'evidence'],
      properties: { gap: { type: 'string' }, evidence: { type: 'string' } } } },
    remaining_or_new: { type: 'array', items: { type: 'object',
      required: ['id', 'title', 'severity', 'kind', 'what', 'evidence', 'fix', 'fix_effort'],
      properties: {
        id: { type: 'string' }, title: { type: 'string' },
        severity: { type: 'string', enum: ['critical', 'high', 'medium', 'low'] },
        kind: { type: 'string', enum: ['remaining', 'new'] },
        what: { type: 'string' }, evidence: { type: 'string' },
        fix: { type: 'string' }, fix_effort: { type: 'string', enum: ['S', 'M', 'L'] } } } },
  },
}

const VERIFY_SCHEMA = {
  type: 'object', required: ['dimension', 'verdicts'],
  properties: { dimension: { type: 'string' },
    verdicts: { type: 'array', items: { type: 'object',
      required: ['id', 'title', 'verdict', 'reason', 'final_severity'],
      properties: { id: { type: 'string' }, title: { type: 'string' },
        verdict: { type: 'string', enum: ['confirmed', 'partially-covered', 'refuted'] },
        reason: { type: 'string' },
        final_severity: { type: 'string', enum: ['critical', 'high', 'medium', 'low', 'none'] } } } } },
}

const results = await pipeline(
  DIMS,
  (d) => agent(
    `You are a ${d.persona} doing a RE-AUDIT of a rebuilt (v2) Tata Steel R2 maintenance dataset. Be skeptical: confirm closures only with concrete file evidence, and actively hunt for gaps the rebuild left open or newly introduced.\n\nDATASET DIR: ${DIR}  (read the actual files; sample large CSVs with head; you may compute a stat with /home/ujjwal/Documents/J.A.R.V.I.S./.venv/bin/python via Bash).\n\n${V2}\n\nYOUR DIMENSION: ${d.focus}\n\nReturn: (1) "closed" = each prior gap you CONFIRMED fixed, with the concrete evidence (file + number) you verified; (2) "remaining_or_new" = gaps still open or newly introduced, each with severity, kind (remaining|new), concrete evidence, a fix, and effort. Only report material gaps you can prove from the files. Quality over quantity.`,
    { label: `reaudit:${d.key}`, phase: 'Re-audit', schema: FINDINGS_SCHEMA }
  ),
  (finding, d) => agent(
    `Independent skeptical verifier. For each gap a re-auditor claims still-open or newly-introduced in the v2 Tata dataset at ${DIR}, RE-READ the files and decide: confirmed (real and material), partially-covered, or refuted (the data actually handles it). Be willing to refute thin claims in both directions.\n\nCLAIMED REMAINING/NEW GAPS (dimension ${finding.dimension}):\n${JSON.stringify(finding.remaining_or_new, null, 2)}\n\nFor each return verdict + reason grounded in the actual files + final_severity.`,
    { label: `verify:${d.key}`, phase: 'Verify', schema: VERIFY_SCHEMA }
  )
)
const clean = results.filter(Boolean)
return { dimensions: clean.length, raw: clean }
