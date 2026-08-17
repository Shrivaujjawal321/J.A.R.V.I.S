# Tata Steel AI Hackathon 2026 — Round 2: Agentic AI Challenge
## OFFICIAL Problem Statement (verbatim, scraped 2026-06-06)

**Theme:** Maintenance Wizard for Industrial Equipment
**Microsite:** https://www.hackerearth.com/community/challenges/hackathon/ai-hackathon-round-2-agentic-ai-challenge/
**Full PS PDF:** official_PS/FULL_PROBLEM_STATEMENT.pdf (6 pages)
**Submission dashboard:** https://www.hackerearth.com/challenges/hackathon/ai-hackathon-round-2-agentic-ai-challenge/dashboard/391fcb1/idea/

### Logistics (CONFIRMED)
- **Window:** Jun 5, 2026 06:00 PM IST → **Jun 15, 2026 11:59 PM IST**
- **Mode:** Online, **individual** (team size 1)
- 109 registrations (as of scrape)
- **Submit:** single ZIP, multiple submissions allowed, last = final
- Must be **built entirely during hackathon duration**; copied ideas → DQ
- Open-source libs + free public APIs allowed; IP stays with participant

### Evaluation Criteria (6)
1. Problem understanding and solution approach
2. Effective use of Agentic AI frameworks and concepts
3. Technical implementation and innovation
4. Scalability and real-world applicability
5. Quality of presentation and communication
6. Business impact and feasibility

### Webinar "qualities" (also scored — operational)
Fast · Efficient · Accurate · Easy to use · Doesn't break · No errors · Smooth

---

## 1. Background
Steel plants = complex, capital-intensive, interdependent equipment. Unplanned downtime →
production loss, safety risk, inefficiency, higher cost. Engineers rely on **fragmented sources**
(manuals, SOPs, historical logs, failure reports, sensor alerts) — manual, slow, expert-dependent.
Need: an intelligent, context-aware support system that consolidates sources, assists diagnosis,
improves RCA, recommends prioritized actions, enables predictive maintenance.

## 2. Objective
Design & develop an intelligent **Maintenance Wizard** acting as a decision-support platform that enables:
- Faster, more accurate diagnosis of equipment issues
- Identification of probable root causes of failures
- Prediction of equipment degradation and remaining useful life
- Proactive detection of abnormalities and catastrophic failure risks
- Prioritization of maintenance actions (operational + procurement constraints)
- Generation of structured maintenance insights and reports
Support BOTH reactive troubleshooting AND proactive maintenance planning.

## 3. Problem Description
Build a system that ingests maintenance inputs from multiple sources and provides **explainable,
actionable, structured outputs**. Analyse conditions, identify abnormalities, assess risk, recommend
immediate + long-term actions, assist via natural language. Support learning from historical data +
engineer feedback → continuous improvement.

## 4. Expected Inputs (accept one or more)
**4.1 Operational & Failure:** equipment delay logs · fault/error messages · failure analysis reports · incident records/breakdown summaries
**4.2 Condition Monitoring:** sensor data summaries · abnormality/anomaly alerts · process condition indicators
**4.3 Knowledge & Documentation:** equipment manuals · maintenance SOPs · historical maintenance records · spare parts info (availability + procurement lead time)
**4.4 User Interaction:** NL queries · scenario-based learning/troubleshooting prompts · multi-turn follow-up queries

## 5. Expected Outputs
**5.1 Diagnostic & Predictive:** probable fault diagnosis · RCA · RUL prediction · early warning of catastrophic failures · process-related defect detection
**5.2 Risk & Priority:** risk level classification (low/med/high/critical) · urgency assessment · plant-level bottleneck prioritization · prioritize on {process criticality, delay severity, spares availability, procurement lead time}
**5.3 Maintenance Recommendation:** step-by-step repair recs · immediate action points · optimized maintenance plan · long-term monitoring recs · spare procurement strategy
**5.4 Reporting:** structured maintenance reports · abnormal alert reports · decision summaries · equipment-specific digital log entries (optional)

## 6. Functional Requirements (7)
1. **Contextual Reasoning using LLMs/SLMs** — integrate LLM/SLM. **Extra merit for creating/fine-tuning a domain-specific model.** Public APIs allowed.
2. **Knowledge Integration** — reason over manuals, SOPs, historical records, failure reports + operational logs
3. **Natural Language Interaction** — NL queries + multi-turn context-aware conversation
4. **Explainable Recommendations** — outputs traceable to input data / records / rules / docs
5. **Abnormality Detection & Failure Prediction** — dynamic anomaly detection, early warning, failure prediction for critical equipment
6. **Feedback-Driven Improvement** — feedback loop (corrections/confirmations/outcomes) improves future recs
7. **Real-Time Alerting Capability** — real-time abnormal alert reports + user-specific notifications

## 7. Optional Enhancements
Conversational interface · visualization dashboard (health/trends/anomalies) · simulated IoT / monitoring dashboard integration · dynamic per-equipment knowledge base · automatic digital logbook · user-role-based alerts

## 8. Expected Outcome
Function as an intelligent maintenance decision-support system that helps ops teams: reduce unplanned
downtime · improve response time · increase diagnostic accuracy · shift reactive→proactive · improve
planning + spare management · faster informed troubleshooting. **Must demonstrate practical applicability in a steel plant.**

## 9. Deliverables (single ZIP)
- **Detailed source code** of working prototype (complete, runnable)
- **A clear document** explaining: system architecture · tech stack · data flow + system flow ·
  model design + reasoning pipeline · alerting + prediction logic · assumptions + limitations ·
  install/configure/run docs · sample input & output demonstration
- **A screen recording** showcasing the built features

---

## ⚠️ Open question (from microsite Discussion)
A participant asked: *"is there any dataset (logs etc) provided, or do we generate synthetic data?"*
— **No answer yet / no dataset link on microsite.** Working assumption: **we generate realistic synthetic data** (matches our playbook). Watch the discussion thread for an official reply.
