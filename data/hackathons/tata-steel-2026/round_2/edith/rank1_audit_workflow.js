export const meta = {
  name: 'edith-rank1-audit',
  description: 'Find everything missing in THE EDITH vs the Tata Steel R2 PS + judge bar — rank-1 gap hunt',
  phases: [
    { title: 'Audit', detail: '5 parallel auditors: PS-compliance, judge-sim, deliverables, robustness, differentiation' },
    { title: 'Verify', detail: 'adversarial verification of every claimed gap' },
  ],
}

const R2 = '/home/ujjwal/Documents/J.A.R.V.I.S./data/hackathons/tata-steel-2026/round_2'

const CTX = [
  'PROJECT: "THE EDITH" — agentic maintenance copilot for the Tata Steel AI Hackathon 2026 Round 2 ("Maintenance Wizard for Industrial Equipment"). Deadline Jun 15 2026 11:59 PM IST. Goal: RANK 1.',
  'PATHS:',
  `- Official problem statement: ${R2}/official_PS/OFFICIAL_PS.md (verbatim summary; full PDF same dir).`,
  `- EDITH app: ${R2}/edith/ -> backend/main.py (FastAPI on 127.0.0.1:8077, RUNNING) + frontend/ (Next.js 16 on 127.0.0.1:3000, RUNNING) + README.md + BUILD_BRIEF.md.`,
  `- Engine (reused as library): ${R2}/vulcan/vulcan/ -> agents/ (Supervisor + 5 domain agents), rag/ (bge+FlashRank+Chroma), ml/ (LightGBM fault/RUL + IsolationForest), alerting/, reports/, llm.py (Claude Max subscription OAuth via claude-agent-sdk; fast grounded-deterministic default; NO API key).`,
  `- Dataset (self-built, v2, audited): ${R2}/dataforge/datasets/steel-maintenance-flagship/ (1.25M rows, 120 run-to-failure episodes, RAG corpus 80 docs, eval set with rubric, SPEC/datacard.md, GAP_ANALYSIS_v2.md).`,
  '- UX spec implemented: /home/ujjwal/Documents/J.A.R.V.I.S./data/outputs/prds/edith-ux-content-system-2026-06-10.md',
  'WHAT THE APP DOES TODAY (verified): 15-asset health strip with plain headlines; focused asset VERDICT card (healthy/watch/act_within/act_now) with whats-happening/how-urgent/steps/parts/if-unaddressed/technical-expand; live SSE historian replay with uPlot graphs (full sensor names + NORMAL/RISING/OVER-LIMIT + threshold bands); alert cards with plain reasons; auto diagnosis hand-off on first ALARM; Ask-EDITH copilot (asset-aware, PS-format expandable section cards with citations); proactive state-aware suggestion chips with WHY; feedback widget (POST /api/feedback); START HERE bottleneck banner (>=2 attention assets); reports: POST /api/report -> /report/{id} shareable web view + GET /api/report/{id}/pdf branded PDF; /api/predict (fault/anomaly/RUL); /api/focus guided bundle; /api/bottleneck.',
  'JUDGING (6): 1 problem understanding & approach · 2 effective use of Agentic AI frameworks/concepts · 3 technical implementation & innovation · 4 scalability & real-world applicability · 5 quality of presentation & communication · 6 business impact & feasibility. Webinar qualities also scored: fast, efficient, accurate, easy to use, does not break, no errors, smooth.',
  'PS DELIVERABLES (§9, single ZIP): (a) detailed source code of working prototype; (b) a clear DOCUMENT: system architecture, tech stack, data flow + system flow, model design + reasoning pipeline, alerting + prediction logic, assumptions + limitations, install/configure/run docs, sample input & output demonstration; (c) a SCREEN RECORDING showcasing the features.',
  'FUNCTIONAL REQS (§6): LLM/SLM contextual reasoning (EXTRA MERIT for creating/fine-tuning a domain-specific model) · knowledge integration · NL multi-turn · explainable/traceable recommendations · abnormality detection + failure prediction · feedback-driven improvement · real-time alerting.',
].join('\n')

const DIMS = [
  { key: 'ps-compliance',
    persona: 'meticulous requirements auditor who maps every PS line to implementation evidence',
    focus: `PS LINE-BY-LINE COMPLIANCE. Read ${R2}/official_PS/OFFICIAL_PS.md fully. For EVERY item in §4 (inputs 4.1-4.4), §5 (outputs 5.1-5.4 — including process-defect detection, plant-level bottleneck prioritization, urgency assessment, spare procurement strategy, abnormal alert reports, decision summaries, digital logbook), §6 (all 7 functional reqs), §7 (optional enhancements: conversational interface, visualization dashboard, simulated IoT integration, dynamic per-equipment knowledge base, automatic digital logbook, user-role-based alerts) and §8: verify whether EDITH actually implements it by reading backend/main.py, the vulcan agents, and probing the RUNNING app (Bash curl to http://127.0.0.1:8077). Classify each: IMPLEMENTED (evidence) / PARTIAL (what is missing) / MISSING. Be precise — judges will check these like a checklist.` },
  { key: 'judge-sim',
    persona: 'Tata Steel hackathon judge (steel-plant digital head + AI architect) scoring for rank-1 vs ~100 competing teams',
    focus: `JUDGE SIMULATION. Score EDITH 1-10 on each of the 6 criteria + the webinar qualities, with evidence from the code + running app (curl the API; read frontend components). For criterion 2 specifically (Agentic AI frameworks/concepts): is the multi-agent orchestration (Supervisor -> Diagnosis/RCA/Predictor/Prioritizer/Recommender agents) VISIBLE to a judge in the UI/demo, or buried in code? Round-2 judges score agentic interpretability — check if the reasoning trace/agent-chain is surfaced anywhere a judge can SEE. For each criterion list: what earns points today, what LOSES points vs a rank-1 entry, and the single highest-leverage fix. Also flag anything that looks generic/template-tier vs isse-behtar-kuch-nahi tier.` },
  { key: 'deliverables',
    persona: 'submission-readiness manager who has shipped winning hackathon ZIPs',
    focus: `SUBMISSION DELIVERABLES (§9). Check what EXISTS vs required: (a) source code — is ${R2}/edith/ + vulcan + dataset packaged/packageable as a clean ZIP with no junk (node_modules, .next, __pycache__, vectordb size?), with a one-command install+run that works on a fresh machine (check README.md run steps — do they actually work? is requirements.txt complete? playwright+markdown deps? npm build?); (b) the REQUIRED DOCUMENT — does any architecture/tech-stack/data-flow/model-design/reasoning-pipeline/alerting-logic/assumptions/install/sample-IO document exist for EDITH? (search ${R2}/edith and round_2 root); (c) SCREEN RECORDING — does any exist? Also: submission portal needs (HackerEarth single ZIP, multiple submissions allowed, last = final). List every missing deliverable artifact with the concrete fix + effort. This category is pass/fail for judging — be exhaustive.` },
  { key: 'robustness',
    persona: 'QA engineer enforcing the webinar bar: fast, accurate, easy, does not break, no errors, smooth',
    focus: `ROBUSTNESS + DEMO-SAFETY of the RUNNING app. Using Bash: curl every backend endpoint (health, assets, asset/{id}, focus/{id} for a healthy AND a warning asset, bottleneck, predict/{id}, ask (POST, time it), report POST + GET + pdf, alerts, stream/{id} first events). Check: error handling on bad asset ids; cold-start latency vs warm; the frontend is currently npm-run-dev (it ALREADY crashed once for the user — check if a production build exists / builds cleanly: cd ${R2}/edith/frontend && npx next build 2>&1 | tail; do NOT leave a build running); single-command startup script for BOTH servers? auto-restart? port conflicts? What breaks if the demo machine reboots? Judge will run from the ZIP — what fails on first run? List concrete break-risks ranked by demo-impact.` },
  { key: 'differentiation',
    persona: 'hackathon strategist who knows what separates rank-1 from rank-5 (everyone will have RAG + a dashboard)',
    focus: `DIFFERENTIATION + QUICK WINS. Most competing teams will ship: a Streamlit RAG chatbot + a dashboard + an off-the-shelf LLM. What does EDITH have that they will not (self-built audited 1.25M-row dataset, 120-episode trainable ML, multi-agent grounded pipeline, faithfulness gate, eval harness with 250 gold items + adversarial/Hinglish queries, guided engineer-first UX, no-API-key subscription brain)? Read the eval harness (dataforge/datasets/steel-maintenance-flagship/user_interaction/eval_harness.py) and judge intel (${R2}/research/domain/01_tata_r2_judge_intel.md if present; also research/23_judging-optimization.md). Then list the 5-8 highest-leverage additions doable in <=2 days that move rank: e.g. visible agent reasoning-trace panel; "EDITH-deep" Claude mode toggle shown in demo; eval-results page (accuracy proof — judges love measured accuracy); domain-fine-tuned/SLM angle for the EXTRA MERIT line; digital logbook quick-win; simulated-IoT framing; cost/ROI slide numbers from the dataset. For each: why it moves a SPECIFIC judging criterion + effort S/M/L.` },
]

phase('Audit')

const FINDINGS_SCHEMA = {
  type: 'object', required: ['dimension', 'strengths', 'gaps'],
  properties: {
    dimension: { type: 'string' },
    strengths: { type: 'array', items: { type: 'string' } },
    gaps: { type: 'array', items: { type: 'object',
      required: ['id', 'title', 'severity', 'what', 'evidence', 'fix', 'fix_effort', 'judging_criterion'],
      properties: {
        id: { type: 'string' }, title: { type: 'string' },
        severity: { type: 'string', enum: ['blocker', 'high', 'medium', 'low'] },
        what: { type: 'string' }, evidence: { type: 'string' },
        fix: { type: 'string' }, fix_effort: { type: 'string', enum: ['S', 'M', 'L'] },
        judging_criterion: { type: 'string' } } } },
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
        final_severity: { type: 'string', enum: ['blocker', 'high', 'medium', 'low', 'none'] } } } } },
}

const results = await pipeline(
  DIMS,
  (d) => agent(
    `You are a ${d.persona}, auditing THE EDITH before the Tata Steel R2 submission. Be exhaustive and skeptical — the team wants RANK 1 and a missed requirement = lost points. Ground every gap in concrete evidence (file you read, endpoint you curled, output you saw). Both servers are RUNNING (backend 8077, frontend 3000) — test live where relevant. Python: /home/ujjwal/Documents/J.A.R.V.I.S./.venv/bin/python.\n\n${CTX}\n\nYOUR DIMENSION: ${d.focus}\n\nReturn strengths (verified, for the submission doc) + gaps (each with severity — blocker = submission/demo fails or a required PS item is absent; high = clearly loses judge points; medium/low = polish). Quality over noise, but MISS NOTHING that a judge would notice.`,
    { label: `audit:${d.key}`, phase: 'Audit', schema: FINDINGS_SCHEMA }
  ),
  (finding, d) => agent(
    `Independent skeptical verifier for the Tata R2 EDITH submission audit. For each claimed gap below, RE-CHECK against the actual files/running app (backend 8077, frontend 3000; paths in context) and decide: confirmed / partially-covered (something exists the auditor missed) / refuted. Adjust severity honestly — blocker only if submission/demo genuinely fails or a required PS deliverable is absent.\n\n${CTX}\n\nCLAIMED GAPS (dimension ${finding.dimension}):\n${JSON.stringify(finding.gaps, null, 2)}\n\nReturn a verdict per gap with concrete reason.`,
    { label: `verify:${d.key}`, phase: 'Verify', schema: VERIFY_SCHEMA }
  )
)

const clean = results.filter(Boolean)
return { dimensions: clean.length, raw: clean }
