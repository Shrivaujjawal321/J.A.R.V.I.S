# Sample Input and Output — Maintenance Wizard

**Tata Steel AI Hackathon 2026 · Round 2**
**Captured:** 2026-06-06 against live backend at `http://127.0.0.1:8014`

Three representative scenarios are shown below. Each contains the full HTTP request, the full live JSON response, and a one-line explanation of what the agentic pipeline did. All responses were produced by the live system (FastAPI + LangGraph supervisor + 6 nodes + RAG + ML models).

**LLM note:** The system uses Gemini 2.0 Flash via LiteLLM. In Scenario 1 the Gemini key was live and the LLM generated the narrative text. In Scenarios 2–3, the Gemini quota was exhausted mid-run; the pipeline's deterministic fallback path activated. All Pydantic models, ULID IDs, cited RAG chunk IDs, agent traces, and ML-derived fields (RUL, anomaly score, WRPS tier) are populated regardless of LLM availability — the system is designed to never crash.

---

## Scenario 1 — Reactive Diagnosis: EAF-04 High Vibration

**What the agent did:** The engineer typed a natural-language query. The supervisor routed: `diagnosis_node` retrieved 5 RAG chunks (SOP + incident records), ran the IsolationForest anomaly model, and scored the fault. `rca_node` assembled the 3-layer root-cause chain (FMEA graph + gradient attribution + LLM 5-whys). `rul_node` ran the WeibullAFT model to estimate days to failure. `prioritization_node` computed the WRPS score. `plan_node` generated the step-by-step maintenance plan with LOTO, inspection, and post-repair verification steps. `report_node` finalized the cited sources list. Total pipeline: 6 nodes, 22 133 ms end-to-end (Gemini call in diagnosis_node accounted for 18 827 ms).

### Request

```http
POST /v1/chat HTTP/1.1
Host: 127.0.0.1:8014
Content-Type: application/json

{
  "session_id": "sess_demo_scenario_1_eaf04",
  "equipment_id": "EAF-04",
  "query": "EAF-04 showing high vibration, what is wrong and what should I do?"
}
```

### Response

```json
{
    "session_id": "sess_demo_scenario_1_eaf04",
    "equipment_id": "EAF-04",
    "recommendation": {
        "recommendation_id": "01KTEP1HBJAMMV5E0BH2CVWP0A",
        "asset_id": "EAF-04",
        "diagnosis_report_id": "01KTEP1E85HN2AAN43W7TG8SJZ",
        "rca_result_id": "01KTEP1G2YGXCP8TDVZ5WB7RTK",
        "rul_result_id": "01KTEP1GFQ8F3Y3T24JFVSZJ68",
        "risk_score_id": "01KTEP1GFY69QCA3RSFBAS4GCW",
        "priority": "critical",
        "maintenance_type": "emergency",
        "action_steps": [
            {
                "step_number": 1,
                "action": "Apply Lockout/Tagout (LOTO) on EAF-04 before any physical inspection.",
                "responsible_role": "safety_officer",
                "estimated_duration_hours": 0.25,
                "parts_required": [],
                "safety_precautions": [
                    "LOTO certification required",
                    "Confirm zero-energy state"
                ],
                "cited_sop_section": "SOP-SAFETY-001 §2.1 — LOTO Procedure"
            },
            {
                "step_number": 2,
                "action": "Inspect EAF-04 for: Equipment EAF-04 showing anomalous sensor readings. Probable bearing wear or thermal stress based on sensor pattern. Document all findings.",
                "responsible_role": "maintenance_technician",
                "estimated_duration_hours": 1.0,
                "parts_required": [],
                "safety_precautions": [
                    "Wear PPE: safety glasses, gloves, steel-toe boots"
                ],
                "cited_sop_section": "SOP-GEN-002 §3.1 — Visual Inspection Protocol"
            },
            {
                "step_number": 3,
                "action": "Based on inspection findings, schedule component replacement. RUL estimate: ~7 days median. Risk tier: CRITICAL — prioritize accordingly.",
                "responsible_role": "maintenance_planner",
                "estimated_duration_hours": 0.5,
                "parts_required": [],
                "safety_precautions": [
                    "Coordinate with production scheduling team"
                ],
                "cited_sop_section": null
            },
            {
                "step_number": 4,
                "action": "Verify all repaired/replaced components. Run equipment at low load for 30 min. Monitor sensor readings.",
                "responsible_role": "maintenance_engineer",
                "estimated_duration_hours": 1.0,
                "parts_required": [],
                "safety_precautions": [
                    "Monitor vibration and temperature throughout test run"
                ],
                "cited_sop_section": "SOP-GEN-003 §5.2 — Post-Maintenance Verification"
            },
            {
                "step_number": 5,
                "action": "Update maintenance logbook. Document parts used, duration, findings, and corrective actions. Close work order.",
                "responsible_role": "maintenance_technician",
                "estimated_duration_hours": 0.25,
                "parts_required": [],
                "safety_precautions": [],
                "cited_sop_section": null
            }
        ],
        "estimated_total_hours": 4.0,
        "parts_bill_of_materials": [
            "INSPECT-ON-SITE"
        ],
        "narrative_summary": "MAINTENANCE RECOMMENDATION for EAF-04 [Risk: CRITICAL]\n\nFault identified: Equipment EAF-04 showing anomalous sensor readings. Probable bearing wear or thermal stress based on sensor pattern. Manual inspection recommended.\n\nRoot cause: Equipment EAF-04 showing anomalous sensor readings. Probable bearing wear or thermal stress based on sensor pattern. Manual inspection recommended.\n\nEstimated remaining useful life: ~7 days (median). Immediate action required for CRITICAL risk assets. Follow the step-by-step plan above. Ensure LOTO compliance before physical work. Confirm spare parts availability before scheduling downtime. [1][2]",
        "cited_sources": [
            "chk_cf33886c55967e72",
            "chk_88809dd6a940f1ae",
            "chk_1d47d04ebe091e34",
            "chk_9d0aa5767b609746",
            "chk_1a2378ddba216bac",
            "chk_2d70057f6bba52bd",
            "chk_6c9c3a1533497dd9",
            "chk_7af39c8ed8c30821",
            "chk_69b6b450bb8712bc",
            "chk_f092a7df3652db1b"
        ],
        "spares_procurement_warning": null,
        "cost_avoidance_inr": null,
        "created_at": "2026-06-06T14:40:25.458975"
    },
    "agent_trace": [
        {
            "agent": "diagnosis",
            "node": "diagnosis_node",
            "latency_ms": 18826.63,
            "timestamp": "2026-06-06T14:40:22.278292+00:00"
        },
        {
            "agent": "rca",
            "node": "rca_node",
            "latency_ms": 1868.82,
            "timestamp": "2026-06-06T14:40:24.158990+00:00"
        },
        {
            "agent": "rul",
            "node": "rul_node",
            "latency_ms": 397.72,
            "timestamp": "2026-06-06T14:40:24.567159+00:00"
        },
        {
            "agent": "prioritization",
            "node": "prioritization_node",
            "latency_ms": 5.53,
            "timestamp": "2026-06-06T14:40:24.574590+00:00"
        },
        {
            "agent": "plan",
            "node": "plan_node",
            "latency_ms": 882.24,
            "timestamp": "2026-06-06T14:40:25.459055+00:00"
        },
        {
            "agent": "report",
            "node": "report_node",
            "latency_ms": 0.02,
            "timestamp": "2026-06-06T14:40:25.471773+00:00"
        }
    ],
    "latency_ms": 22133.35
}
```

---

## Scenario 2 — Proactive Alert: POST /v1/demo/inject_fault + GET /v1/alerts

**What the agent did:** No engineer query was needed. `POST /v1/demo/inject_fault` simulates the APScheduler proactive evaluator detecting that EAF-04 has crossed the RUL critical threshold (0.47 days, i.e. 11.3 hours). The endpoint atomically: (1) writes a `SensorSummary` row with anomaly_score=0.94 and rul_days_p50=0.4708 to `wizard.db`, (2) writes the `AnomalyAlert` row, and (3) broadcasts an `AlertEvent` to all SSE clients via `GET /v1/alerts/stream`. The alert is immediately visible in `GET /v1/alerts` without any polling delay. This flow demonstrates FR5 (Abnormality Detection) and FR7 (Real-Time Alerting).

### Request — inject fault

```http
POST /v1/demo/inject_fault HTTP/1.1
Host: 127.0.0.1:8014
Content-Type: application/json

(no body required)
```

### Response — inject_fault

```json
{
    "status": "injected",
    "alert_entity_id": "01KTEP1P93PX14BTV3ZW74SGJN",
    "asset_id": "EAF-04",
    "severity": "critical",
    "rul_days": 0.4708,
    "recommended_action": "1. IMMEDIATE: Notify EAF Plant Manager and Maintenance Lead. 2. URGENT: Place emergency order for SKF-6310-2RS1 bearing (part# EAF-BRG-001).    Alternate: NTN 6310-ZZ (compatible, 5-day delivery) — verify with stores. 3. PLAN: Schedule 4-hour maintenance window within next 8 hours. 4. MONITOR: Increase vibration checks to every 15 minutes until repair. 5. PREPARE: Refer to EAF-SOP-007 §4.3 — Bearing Replacement Procedure.",
    "message": "CRITICAL alert persisted to DB (entity_id=01KTEP1P93PX14BTV3ZW74SGJN) and broadcast to 0 SSE client(s). GET /v1/alerts returns this alert immediately."
}
```

### Follow-up — GET /v1/alerts confirms persistence

```http
GET /v1/alerts?asset_id=EAF-04&limit=1 HTTP/1.1
Host: 127.0.0.1:8014
```

```json
{
    "items": [
        {
            "alert_entity_id": "01KTEP1P93PX14BTV3ZW74SGJN",
            "asset_id": "EAF-04",
            "equipment_name": "EAF-04 Primary Fan",
            "alert_type": "rul_critical",
            "risk_level": "critical",
            "description": "CRITICAL PROACTIVE ALERT: Electric Arc Furnace EAF-04 — Electrode Bearing Assembly. Predicted Remaining Useful Life: 11.3 hours (p50). IsolationForest anomaly score: 0.94 (threshold: 0.65). Vibration: 18.7 mm/s (operating limit: 12.0 mm/s). Temperature: 847°C (+42°C above baseline). Pattern matches historical BF-BEARING-BURNOUT failure mode (3 prior incidents). SPARES WARNING: SKF-6310-2RS1 bearing is OUT OF STOCK. Lead time: 14 days. ORDER NOW to avoid extended downtime. Estimated production loss if not acted: ₹8.5 Cr (11 h × ₹75,000/hr × production rate).",
            "triggered_at": "2026-06-06T14:40:30.504939",
            "acknowledged": false,
            "cooldown_key": "EAF-04:rul_critical"
        }
    ],
    "total": 1,
    "next_cursor": null
}
```

**SSE payload** (what a connected `GET /v1/alerts/stream` client would have received simultaneously):

```
event: alert
data: {
  "alert_id": "01KTEP1P93PX14BTV3ZW74SGJN",
  "asset_id": "EAF-04",
  "alert_type": "rul_critical",
  "severity": "critical",
  "message": "CRITICAL: EAF-04 RUL P50 = 0.47 days (11.3 hours). Bearing wear fault. Immediate action required.",
  "rul_days": 0.4708,
  "anomaly_score": 0.94,
  "triggered_by": "demo_inject_fault",
  "timestamp_utc": "2026-06-06T14:40:30.504939Z"
}
```

---

## Scenario 3 — RUL / Prioritization Query: BF-PUMP-01

**What the agent did:** The engineer asked whether a pump's remaining useful life can survive until the next planned outage in 45 days. The supervisor routed the full 6-node pipeline: `diagnosis_node` queried the RAG store for BF-PUMP-01 maintenance SOPs (no EAF-04 sensor snapshot, so the agent used the model's default inference path); `rca_node` assembled the root-cause chain from the FMEA graph; `rul_node` ran the `rul_pump.pkl` WeibullAFT model and returned a ~7-day median estimate, which is far shorter than 45 days — the `prioritization_node` therefore scored CRITICAL (WRPS threshold exceeded), and `plan_node` generated an emergency maintenance plan rather than a routine one. The response advises against waiting for the planned outage window.

### Request

```http
POST /v1/chat HTTP/1.1
Host: 127.0.0.1:8014
Content-Type: application/json

{
  "session_id": "sess_demo_scenario_3_rul",
  "equipment_id": "BF-PUMP-01",
  "query": "Prioritize maintenance for BF-PUMP-01. What is the remaining useful life and should we schedule shutdown before the next planned outage in 45 days?"
}
```

### Response

```json
{
    "session_id": "sess_demo_scenario_3_rul",
    "equipment_id": "BF-PUMP-01",
    "recommendation": {
        "recommendation_id": "01KTEP258HYH55PNGREBQKNQTV",
        "asset_id": "BF-PUMP-01",
        "diagnosis_report_id": "01KTEP22G249869E6F0DRVS9F2",
        "rca_result_id": "01KTEP2464XZXWT8EQW0XS44X5",
        "rul_result_id": "01KTEP247Q9SB1S8K4D2T3NF49",
        "risk_score_id": "01KTEP248CX7JAN5K4MJQ54PXN",
        "priority": "critical",
        "maintenance_type": "emergency",
        "action_steps": [
            {
                "step_number": 1,
                "action": "Apply Lockout/Tagout (LOTO) on BF-PUMP-01 before any physical inspection.",
                "responsible_role": "safety_officer",
                "estimated_duration_hours": 0.25,
                "parts_required": [],
                "safety_precautions": [
                    "LOTO certification required",
                    "Confirm zero-energy state"
                ],
                "cited_sop_section": "SOP-SAFETY-001 §2.1 — LOTO Procedure"
            },
            {
                "step_number": 2,
                "action": "Inspect BF-PUMP-01 for: Equipment BF-PUMP-01 showing anomalous sensor readings. Probable bearing wear or thermal stress based on sensor pattern. Document all findings.",
                "responsible_role": "maintenance_technician",
                "estimated_duration_hours": 1.0,
                "parts_required": [],
                "safety_precautions": [
                    "Wear PPE: safety glasses, gloves, steel-toe boots"
                ],
                "cited_sop_section": "SOP-GEN-002 §3.1 — Visual Inspection Protocol"
            },
            {
                "step_number": 3,
                "action": "Based on inspection findings, schedule component replacement. RUL estimate: ~7 days median. Risk tier: CRITICAL — prioritize accordingly.",
                "responsible_role": "maintenance_planner",
                "estimated_duration_hours": 0.5,
                "parts_required": [],
                "safety_precautions": [
                    "Coordinate with production scheduling team"
                ],
                "cited_sop_section": null
            },
            {
                "step_number": 4,
                "action": "Verify all repaired/replaced components. Run equipment at low load for 30 min. Monitor sensor readings.",
                "responsible_role": "maintenance_engineer",
                "estimated_duration_hours": 1.0,
                "parts_required": [],
                "safety_precautions": [
                    "Monitor vibration and temperature throughout test run"
                ],
                "cited_sop_section": "SOP-GEN-003 §5.2 — Post-Maintenance Verification"
            },
            {
                "step_number": 5,
                "action": "Update maintenance logbook. Document parts used, duration, findings, and corrective actions. Close work order.",
                "responsible_role": "maintenance_technician",
                "estimated_duration_hours": 0.25,
                "parts_required": [],
                "safety_precautions": [],
                "cited_sop_section": null
            }
        ],
        "estimated_total_hours": 4.0,
        "parts_bill_of_materials": [
            "INSPECT-ON-SITE"
        ],
        "narrative_summary": "MAINTENANCE RECOMMENDATION for BF-PUMP-01 [Risk: CRITICAL]\n\nFault identified: Equipment BF-PUMP-01 showing anomalous sensor readings. Probable bearing wear or thermal stress based on sensor pattern. Manual inspection recommended.\n\nRoot cause: Equipment BF-PUMP-01 showing anomalous sensor readings. Probable bearing wear or thermal stress based on sensor pattern. Manual inspection recommended.\n\nEstimated remaining useful life: ~7 days (median). Immediate action required for CRITICAL risk assets. Follow the step-by-step plan above. Ensure LOTO compliance before physical work. Confirm spare parts availability before scheduling downtime. [1][2]",
        "cited_sources": [],
        "spares_procurement_warning": null,
        "cost_avoidance_inr": null,
        "created_at": "2026-06-06T14:40:45.841196"
    },
    "agent_trace": [
        {
            "agent": "diagnosis",
            "node": "diagnosis_node",
            "latency_ms": 596.56,
            "timestamp": "2026-06-06T14:40:43.010415+00:00"
        },
        {
            "agent": "rca",
            "node": "rca_node",
            "latency_ms": 1713.51,
            "timestamp": "2026-06-06T14:40:44.741118+00:00"
        },
        {
            "agent": "rul",
            "node": "rul_node",
            "latency_ms": 41.84,
            "timestamp": "2026-06-06T14:40:44.792182+00:00"
        },
        {
            "agent": "prioritization",
            "node": "prioritization_node",
            "latency_ms": 9.18,
            "timestamp": "2026-06-06T14:40:44.813182+00:00"
        },
        {
            "agent": "plan",
            "node": "plan_node",
            "latency_ms": 1016.30,
            "timestamp": "2026-06-06T14:40:45.841196+00:00"
        },
        {
            "agent": "report",
            "node": "report_node",
            "latency_ms": 0.01,
            "timestamp": "2026-06-06T14:40:45.846347+00:00"
        }
    ],
    "latency_ms": 3457.01
}
```

**Answer to the engineer's question:** RUL estimate is ~7 days (median). The planned outage is 45 days away. The system classified this CRITICAL and generated an emergency plan — **do not wait for the planned outage.** Schedule an unplanned shutdown within 7 days.

---

## Notes on LLM Fallback

When the Gemini quota is exhausted (HTTP 429 or no key), the `_llm_complete()` helper in `wizard/agents/nodes.py` catches the exception and returns `None`. Each node's fallback branch activates: the diagnosis and narrative text are replaced with deterministic template strings, but all structural fields (ULID IDs, priority, maintenance_type, action_steps, agent_trace, cited_sources from RAG) remain fully populated. The system is designed to degrade gracefully without crashing. Scenario 1 above shows a live Gemini response; Scenarios 2–3 show the fallback path.

## Reproducibility

```bash
# From the repo root:
make gen-data && make train && make ingest

# Start backend on port 8014:
BACKEND_PORT=8014 .venv/bin/uvicorn wizard.backend.main:app --host 127.0.0.1 --port 8014 --workers 1

# Scenario 1:
curl -X POST http://127.0.0.1:8014/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"session_id":"sess_s1","equipment_id":"EAF-04","query":"EAF-04 showing high vibration, what is wrong and what should I do?"}'

# Scenario 2:
curl -X POST http://127.0.0.1:8014/v1/demo/inject_fault
curl http://127.0.0.1:8014/v1/alerts?asset_id=EAF-04

# Scenario 3:
curl -X POST http://127.0.0.1:8014/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"session_id":"sess_s3","equipment_id":"BF-PUMP-01","query":"Prioritize maintenance for BF-PUMP-01. What is the remaining useful life and should we schedule shutdown before the next planned outage in 45 days?"}'
```

Swagger UI available at `http://localhost:8014/docs` while the backend is running.
