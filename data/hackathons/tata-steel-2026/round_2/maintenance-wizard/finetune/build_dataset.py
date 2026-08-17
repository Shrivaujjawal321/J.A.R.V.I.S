"""
build_dataset.py
================
Generates a maintenance-domain instruction-tuning dataset (1,200-2,000 examples)
from the existing synthetic corpus:
  - data/synthetic/docs/*.json         -> 200 structured maintenance documents
  - data/kg/steel_plant_fmea.json      -> FMEA graph (FailureMode, RootCause,
                                          Action, SparePart, SOPReference, Effect…)
  - data/kg/steel_plant_ontology.json  -> asset families, sensor specs, spare parts

Output: finetune/maintenance_sft.jsonl
        finetune/maintenance_eval_50.jsonl  (held-out eval set for notebook)

Format: {"instruction": "...", "input": "...", "output": "..."}
  — Unsloth alpaca format, maps 1:1 to SFTTrainer prompt template.

Run: python finetune/build_dataset.py
CPU-only. No GPU, no network, no paid APIs.
"""

import json
import random
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parent.parent
SYNTHETIC_DOCS_DIR = REPO_ROOT / "data" / "synthetic" / "docs"
FMEA_PATH = REPO_ROOT / "data" / "kg" / "steel_plant_fmea.json"
ONTOLOGY_PATH = REPO_ROOT / "data" / "kg" / "steel_plant_ontology.json"
OUTPUT_PATH = Path(__file__).resolve().parent / "maintenance_sft.jsonl"

random.seed(42)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def bulleted(items: list) -> str:
    return "\n".join(f"- {i}" for i in items)


def numbered(items: list) -> str:
    return "\n".join(f"{n+1}. {i}" for n, i in enumerate(items))


def sev_word(sev: str) -> str:
    return {"critical": "CRITICAL", "high": "HIGH", "medium": "MEDIUM", "low": "LOW"}.get(sev, sev.upper())


# ---------------------------------------------------------------------------
# Data loaders
# ---------------------------------------------------------------------------

def load_synthetic_docs(doc_dir: Path) -> list[dict]:
    docs = []
    for p in sorted(doc_dir.glob("*.json")):
        try:
            with open(p) as f:
                docs.append(json.load(f))
        except Exception:
            continue
    return docs


def load_fmea(path: Path) -> dict:
    with open(path) as f:
        raw = json.load(f)
    by_type: dict = {}
    for node in raw.get("nodes", []):
        t = node.get("node_type", "Unknown")
        by_type.setdefault(t, []).append(node)
    return by_type


def load_ontology(path: Path) -> dict:
    with open(path) as f:
        return json.load(f)


# ============================================================================
# GENERATOR 1 — Fault Diagnosis (from failure_analysis docs)
# Produces ~4-5 variants per doc  →  ~128-160 examples
# ============================================================================

def gen_fault_diagnosis(docs: list[dict]) -> list[dict]:
    examples = []
    fa_docs = [d for d in docs if d.get("doc_type") == "failure_analysis"]

    for doc in fa_docs:
        content = doc.get("content_markdown", "")
        asset_id = doc.get("asset_id", "unknown")
        fam = doc.get("asset_family", "").replace("_", " ")
        fault_codes = doc.get("fault_codes_referenced", [])
        failure_modes = doc.get("failure_modes_referenced", [])
        if not fault_codes or not failure_modes or len(content) < 200:
            continue

        fc = fault_codes[0]
        fm = failure_modes[0]
        snippet = content[:2200]

        # V1 — identify fault + evidence + action
        examples.append({
            "instruction": (
                "You are a maintenance engineer AI for an integrated steel plant. "
                "Given this failure analysis report, identify: (1) fault code triggered, "
                "(2) diagnosed failure mode, (3) primary sensor evidence, (4) immediate corrective action."
            ),
            "input": f"Equipment: {asset_id} ({fam})\n\n{snippet}",
            "output": (
                f"**Fault Code:** {fc}\n"
                f"**Failure Mode:** {fm}\n"
                f"**Primary Evidence:** Sensor anomalies consistent with {fm.lower()} were detected. "
                f"The fault code {fc} was triggered when sensor readings crossed the critical threshold.\n"
                f"**Immediate Action:** Equipment was shut down under controlled conditions, LOTO applied, "
                f"and the maintenance team dispatched for inspection and repair."
            ),
        })

        # V2 — severity + production impact
        examples.append({
            "instruction": (
                "Assess the severity and production impact of the following equipment failure. "
                "State the fault code, severity level, downtime estimate, and cost impact."
            ),
            "input": f"Equipment: {asset_id} ({fam})\n\n{snippet}",
            "output": (
                f"**Fault Code:** {fc} | **Failure Mode:** {fm}\n"
                f"**Severity:** {'CRITICAL' if 'critical' in content.lower()[:500] else 'MEDIUM'}\n"
                f"**Downtime Impact:** Unplanned shutdown was triggered. "
                f"Based on the report, the failure caused extended downtime and production loss as documented.\n"
                f"**Cost Impact:** Emergency repair costs (parts + labour) plus production loss during outage. "
                f"See cost summary section of the report for exact figures.\n"
                f"**Key Lesson:** Earlier detection via predictive monitoring would have prevented the unplanned event."
            ),
        })

        # V3 — five-whys extraction (if present)
        if "Five-Why" in content or "five-why" in content.lower() or "Why did" in content:
            examples.append({
                "instruction": (
                    "Extract the Five-Whys root cause chain from this failure analysis report. "
                    "Summarise the root cause statement in one concise sentence."
                ),
                "input": f"Equipment: {asset_id} ({fam})\n\n{snippet}",
                "output": (
                    f"**Five-Whys Chain — {asset_id} / {fc}:**\n"
                    f"1. Equipment failed unexpectedly during operation.\n"
                    f"2. A critical component reached end of service life prematurely.\n"
                    f"3. Operating conditions exceeded the design envelope.\n"
                    f"4. Maintenance intervals were not adjusted for actual severity.\n"
                    f"5. The CMMS planning system does not support condition-based interval adjustment.\n\n"
                    f"**Root Cause Statement:** {fm} resulted from unadjusted maintenance intervals "
                    f"in a system lacking condition-based planning controls."
                ),
            })

        # V4 — corrective actions only
        examples.append({
            "instruction": (
                "Based on this failure analysis report, list the corrective actions required "
                "to restore the equipment and prevent recurrence."
            ),
            "input": f"Equipment: {asset_id} ({fam}) | Fault: {fc} ({fm})\n\n{snippet}",
            "output": (
                f"**Corrective Actions — {asset_id} ({fc}):**\n\n"
                f"**Immediate restoration:**\n"
                f"1. Complete inspection per applicable SOP\n"
                f"2. Replace or repair the failed component identified as root cause\n"
                f"3. Perform post-repair acceptance test before return to service\n\n"
                f"**Recurrence prevention:**\n"
                f"4. Update PM interval for {fm} based on observed MTBF\n"
                f"5. Implement or enhance condition-based monitoring for early detection\n"
                f"6. Train maintenance team on failure mode identification for {fm.lower()}\n"
                f"7. Add fault code {fc} to predictive monitoring dashboard"
            ),
        })

        # V5 — Q&A style: "What is the root cause of this failure?"
        examples.append({
            "instruction": "What is the root cause of this equipment failure? Cite the evidence from the report.",
            "input": f"Report on {asset_id} ({fam}), fault code {fc}:\n\n{snippet}",
            "output": (
                f"**Root Cause:** The failure of {asset_id} was caused by **{fm}**.\n\n"
                f"**Evidence:**\n"
                f"- Physical inspection confirmed the {fm.lower()} condition\n"
                f"- Sensor readings (vibration, temperature, or pressure as applicable) showed values beyond normal operating limits\n"
                f"- Fault code {fc} was triggered, which maps directly to this failure mode\n"
                f"- Oil/material sample analysis supported the diagnosis (NAS class exceedance or contamination evidence)\n\n"
                f"**Contributing Factors:** Thermal cycling, inadequate maintenance interval adjustment, "
                f"and operating conditions exceeding design envelope all accelerated the failure."
            ),
        })

    return examples


# ============================================================================
# GENERATOR 2 — RCA Explanation (from ontology failure modes)
# ~4 variants per failure mode x 16 modes = ~64 examples
# ============================================================================

def gen_rca_explanation(ontology: dict) -> list[dict]:
    examples = []
    families = ontology.get("asset_families", {})

    for fam_name, fam in families.items():
        fam_label = fam_name.replace("_", " ").title()
        sensor_ranges = fam.get("sensor_ranges", {})

        for ss in fam.get("subsystems", []):
            ss_label = ss.get("name", "").replace("_", " ").title()
            for fm in ss.get("failure_modes", []):
                fm_name = fm.get("name", "Unknown")
                fm_id = fm.get("fault_code", fm.get("id", "?"))
                severity = fm.get("severity", "medium")
                mtbf = fm.get("mtbf_days", 365)
                symptoms = fm.get("symptoms", [])
                root_causes = fm.get("root_causes", [])
                corrective = fm.get("corrective_actions", [])
                sensor_sig = fm.get("sensor_signature", {})
                parts = fm.get("requires_parts", [])

                # V1 — full RCA chain
                sensor_str = ""
                if sensor_sig:
                    sensor_str = "Sensor signature: " + ", ".join(f"{k}={v}" for k, v in sensor_sig.items())
                examples.append({
                    "instruction": (
                        f"You are a reliability expert for {fam_label} equipment in a steel plant. "
                        f"Explain the root causes of failure mode '{fm_name}' ({fm_id}), "
                        f"including contributing factors and observable symptoms."
                    ),
                    "input": (
                        f"Equipment: {fam_label} | Subsystem: {ss_label}\n"
                        f"Fault code: {fm_id} | Severity: {sev_word(severity)}\n"
                        f"{sensor_str}"
                    ).strip(),
                    "output": (
                        f"**Failure Mode:** {fm_name} ({fm_id}) — {sev_word(severity)}\n"
                        f"**MTBF:** ~{mtbf} days\n\n"
                        f"**Root Causes:**\n{bulleted(root_causes) if root_causes else '- Requires detailed site investigation'}\n\n"
                        f"**Observable Symptoms:**\n{bulleted(symptoms) if symptoms else '- Vibration increase, temperature rise, performance degradation'}\n\n"
                        f"**Corrective Actions:**\n{bulleted(corrective) if corrective else '- Inspect, diagnose, replace affected components'}\n\n"
                        f"**Parts Required:** {', '.join(parts) if parts else 'See spare parts catalogue'}"
                    ),
                })

                # V2 — sensor reading diagnosis
                if sensor_sig and sensor_ranges:
                    reading_lines = []
                    for sensor, trend in sensor_sig.items():
                        r = sensor_ranges.get(sensor, {})
                        nm = r.get("normal_max", "N/A")
                        reading_lines.append(f"- {sensor}: {trend} (normal max: {nm})")
                    examples.append({
                        "instruction": (
                            f"Diagnose the likely failure mode on this {fam_label} based on the sensor pattern. "
                            f"Explain the physical mechanism linking sensors to the fault."
                        ),
                        "input": f"Equipment: {fam_label}\nSensor pattern:\n" + "\n".join(reading_lines),
                        "output": (
                            f"**Diagnosis:** This pattern is consistent with **{fm_name}** ({fm_id}).\n\n"
                            f"**Physical Mechanism:**\n"
                            + "\n".join(
                                f"- {s} trending {t}: indicates {fm_name.lower()} is progressing in the {ss_label}"
                                for s, t in sensor_sig.items()
                            )
                            + f"\n\n**Immediate Recommendation:** {corrective[0] if corrective else 'Inspect and isolate if critical'}. "
                            f"If severity reaches {sev_word(severity)}, escalate to maintenance manager."
                        ),
                    })

                # V3 — consequence of ignoring
                examples.append({
                    "instruction": (
                        f"What happens if early warning signs of '{fm_name}' on a {fam_label} are ignored? "
                        f"Describe the escalation path and production impact."
                    ),
                    "input": f"Fault: {fm_id} | Severity: {sev_word(severity)} | MTBF: {mtbf} days",
                    "output": (
                        f"**Escalation Path if {fm_name} is Ignored:**\n\n"
                        f"**Stage 1 — Early warning (ignored):**\n{bulleted(symptoms[:2]) if symptoms else '- Subtle sensor deviation'}\n\n"
                        f"**Stage 2 — Progressive degradation:** Condition worsens beyond warning threshold; "
                        f"secondary components begin to be affected.\n\n"
                        f"**Stage 3 — Catastrophic failure:** Unplanned shutdown triggered. "
                        f"{'Emergency isolation required.' if severity == 'critical' else 'Forced outage.'}\n\n"
                        f"**Stage 4 — Extended downtime:** Emergency repair, parts procurement on lead time, "
                        f"production loss until restoration.\n\n"
                        f"**MTBF without intervention:** ~{mtbf} days from onset. "
                        f"Severity: {sev_word(severity)} — {'catastrophic plant impact likely' if severity == 'critical' else 'significant downtime expected'}."
                    ),
                })

                # V4 — which parts and SOP?
                examples.append({
                    "instruction": (
                        f"A technician has confirmed fault {fm_id} ({fm_name}) on a {fam_label}. "
                        f"What replacement parts are needed and which SOP governs the repair?"
                    ),
                    "input": f"Equipment: {fam_label} | Fault: {fm_id} | Severity: {sev_word(severity)}",
                    "output": (
                        f"**Required Parts for {fm_name} repair:**\n"
                        f"{bulleted(parts) if parts else '- Check spare parts catalogue for this asset family'}\n\n"
                        f"**Verify stock availability** in the CMMS before starting work. "
                        f"If any part is out of stock, raise emergency purchase order immediately.\n\n"
                        f"**Applicable SOP:** Locate the SOP for {fm_name.lower()} on {fam_label} equipment "
                        f"(search by fault code {fm_id} or asset family in the SOP library). "
                        f"Verify you have the current revision.\n\n"
                        f"**Pre-work checklist:** LOTO applied → parts staged → SOP in hand → PTW issued → team briefed."
                    ),
                })

    return examples


# ============================================================================
# GENERATOR 3 — RUL Interpretation
# ~3 RUL scenarios x 16 FMs x 5 families = ~240 examples (capped)
# ============================================================================

def gen_rul_interpretation(ontology: dict) -> list[dict]:
    examples = []
    families = ontology.get("asset_families", {})

    rul_scenarios = [
        (0.2, "20%", "early stage", "LOW — monitor at standard interval"),
        (0.4, "40%", "mid-life onset", "MODERATE — plan PM within 60 days"),
        (0.6, "60%", "mid-life", "MODERATE — schedule within 30 days"),
        (0.75, "75%", "advanced", "HIGH — schedule within 7–14 days"),
        (0.88, "88%", "near end-of-life", "HIGH — schedule within 72 hours"),
        (0.95, "95%", "imminent failure", "CRITICAL — isolate at next maintenance window, pre-stage all parts"),
    ]

    for fam_name, fam in families.items():
        fam_label = fam_name.replace("_", " ").title()
        for ss in fam.get("subsystems", []):
            for fm in ss.get("failure_modes", []):
                fm_name = fm.get("name", "Unknown")
                fm_id = fm.get("fault_code", "?")
                severity = fm.get("severity", "medium")
                mtbf = fm.get("mtbf_days", 365)
                corrective = fm.get("corrective_actions", [])

                if not isinstance(mtbf, (int, float)):
                    mtbf = 365

                for consumed, pct, stage, urgency in random.sample(rul_scenarios, k=3):
                    days_op = int(mtbf * consumed)
                    rul = int(mtbf * (1 - consumed))

                    examples.append({
                        "instruction": (
                            f"You are a reliability engineer AI. Interpret this RUL estimate for a {fam_label}, "
                            f"classify the degradation stage, and recommend next actions."
                        ),
                        "input": (
                            f"Equipment: {fam_label} | Failure mode: {fm_name} ({fm_id})\n"
                            f"Severity: {sev_word(severity)} | MTBF: {mtbf} days\n"
                            f"Days operated since last maintenance: {days_op}\n"
                            f"Life consumed: {pct} | Estimated RUL: {rul} days"
                        ),
                        "output": (
                            f"**RUL Interpretation — {fam_label} / {fm_name} ({fm_id})**\n\n"
                            f"**Stage:** {stage.title()}\n"
                            f"**Life consumed:** {pct} of MTBF ({days_op}/{mtbf} days)\n"
                            f"**Remaining life:** ~{rul} days\n"
                            f"**Urgency:** {urgency}\n\n"
                            f"**Recommended Actions:**\n"
                            f"1. {'Increase monitoring to daily readings' if consumed >= 0.75 else 'Continue standard monitoring schedule'}\n"
                            f"2. {'Pre-order all replacement parts NOW' if consumed >= 0.60 else 'Verify spare parts availability'}\n"
                            f"3. {'Book outage window — notify operations' if consumed >= 0.75 else 'Update PM schedule with RUL estimate'}\n"
                            f"4. {corrective[0] if corrective else 'Prepare inspection checklist'} at next scheduled maintenance\n\n"
                            f"**Production risk at end of RUL:** {sev_word(severity)} — "
                            f"{'catastrophic unplanned failure if action deferred' if severity in ('critical','high') else 'planned outage can prevent unplanned event'}."
                        ),
                    })

                    # Second variant: just ask for go/no-go on continuing operation
                    examples.append({
                        "instruction": (
                            f"Can the {fam_label} continue operating safely given this RUL estimate? "
                            f"Provide a go/no-go decision with justification."
                        ),
                        "input": (
                            f"Failure mode: {fm_name} ({fm_id})\n"
                            f"Life consumed: {pct} of MTBF {mtbf} days\n"
                            f"Estimated RUL: {rul} days | Severity: {sev_word(severity)}"
                        ),
                        "output": (
                            f"**Decision: {'GO WITH MONITORING' if consumed < 0.85 else 'NO-GO — schedule immediate maintenance'}**\n\n"
                            f"**Justification:**\n"
                            + (
                                f"With {pct} of life consumed and {rul} days of RUL remaining, the equipment can continue "
                                f"operating provided monitoring frequency is increased. However, maintenance planning should begin now.\n\n"
                                f"**Conditions for continued operation:**\n"
                                f"- Daily vibration + temperature readings\n"
                                f"- Replacement parts pre-staged\n"
                                f"- Outage window booked within {max(7, rul//3)} days"
                                if consumed < 0.85
                                else
                                f"With {pct} of life consumed and only {rul} days of RUL remaining, "
                                f"continuing operation risks a {sev_word(severity)} unplanned failure. "
                                f"The cost and safety risk of that event far outweighs the cost of a planned shutdown.\n\n"
                                f"**Required actions:**\n"
                                f"1. Plan shutdown for the earliest available maintenance window\n"
                                f"2. Confirm all replacement parts are on-site before shutdown\n"
                                f"3. Prepare LOTO and work order\n"
                                f"4. Brief the operations team on production impact"
                            )
                        ),
                    })

    return examples


# ============================================================================
# GENERATOR 4 — SOP-grounded Recommendations
# ~3 variants per SOP doc x 40 SOPs = ~120 examples
# ============================================================================

def gen_sop_recommendations(docs: list[dict], fmea_nodes: dict) -> list[dict]:
    examples = []
    sop_docs = [d for d in docs if d.get("doc_type") == "sop"]
    sop_nodes = fmea_nodes.get("SOPReference", [])

    for doc in sop_docs:
        content = doc.get("content_markdown", "")
        asset_id = doc.get("asset_id", "unknown")
        fam = doc.get("asset_family", "").replace("_", " ")
        failure_modes = doc.get("failure_modes_referenced", [])
        fault_codes = doc.get("fault_codes_referenced", [])
        if not content or len(content) < 200:
            continue

        fm = failure_modes[0] if failure_modes else "equipment fault"
        fc = fault_codes[0] if fault_codes else "N/A"
        snippet = content[:2500]

        # V1 — step-by-step response
        examples.append({
            "instruction": (
                "A technician has been alerted to an equipment fault. Based on the SOP excerpt below, "
                "provide a clear step-by-step response procedure including all safety requirements."
            ),
            "input": f"Equipment: {asset_id} ({fam}) | Fault: {fm} ({fc})\n\nSOP Reference:\n{snippet}",
            "output": (
                f"**Response Procedure — {fm} on {asset_id}:**\n\n"
                f"**Step 1 — Safety / LOTO:**\n"
                f"Isolate {asset_id} per plant isolation standard. Apply Lock-Out Tag-Out (LOTO). "
                f"Verify zero-energy state (electrical, pressure, mechanical).\n\n"
                f"**Step 2 — Initial Assessment:**\n"
                f"Confirm fault code {fc} via control room display. Record all sensor readings at alarm time.\n\n"
                f"**Step 3 — Inspection:**\n"
                f"Execute the inspection steps per the SOP — visual check, measurements, and condition assessment of affected subsystem.\n\n"
                f"**Step 4 — Corrective Action:**\n"
                f"Based on findings, replace or repair components per SOP specification. "
                f"Use approved spare parts from the maintenance catalogue only.\n\n"
                f"**Step 5 — Return to Service:**\n"
                f"Perform functional test per SOP commissioning section. Remove LOTO. Clear alarm. "
                f"Notify control room and update maintenance log."
            ),
        })

        # V2 — pre-work safety checklist
        examples.append({
            "instruction": (
                "List all safety checks and prerequisites a technician must complete "
                "before starting this maintenance task."
            ),
            "input": f"Equipment: {asset_id} ({fam}) | Fault: {fm} ({fc})",
            "output": (
                f"**Pre-Work Safety Checklist — {asset_id}:**\n\n"
                f"1. LOTO applied by authorised person — zero-energy state verified\n"
                f"2. Permit-to-Work (PTW) issued and active\n"
                f"3. PPE confirmed: hard hat, safety glasses, gloves, safety boots, hearing protection\n"
                f"4. No hot surfaces / pressurised lines / rotating parts accessible\n"
                f"5. Correct tools and calibrated instruments at worksite\n"
                f"6. Required spare parts staged and confirmed serviceable\n"
                f"7. Current SOP revision confirmed and in hand\n"
                f"8. Control room notified; team briefed on task scope and hazards\n"
                f"9. Emergency stop locations identified; first aid kit accessible\n\n"
                f"**Proceed only when ALL items confirmed checked.**"
            ),
        })

        # V3 — which SOP applies?
        matching = [s for s in sop_nodes if fam.replace(" ", "_") in s.get("equipment_class", "")]
        sop_ref = random.choice(matching) if matching else None
        if sop_ref:
            examples.append({
                "instruction": "Which SOP should be followed for this fault, and what does the procedure cover?",
                "input": f"Equipment class: {fam} | Fault code: {fc} | Failure mode: {fm}",
                "output": (
                    f"**Applicable SOP:** {sop_ref.get('sop_number', 'See SOP library')}\n"
                    f"**Title:** {sop_ref.get('title', fm + ' procedure')}\n"
                    f"**Equipment class:** {sop_ref.get('equipment_class', fam)}\n\n"
                    f"This SOP covers: isolation and LOTO, inspection procedure, "
                    f"acceptance criteria, repair/replacement steps, and return-to-service commissioning "
                    f"for {fm.lower()} events on {fam} equipment.\n\n"
                    f"**Important:** Always confirm you have the current revision before starting. "
                    f"If the revision date is more than 12 months old, flag for SOP review."
                ),
            })

    return examples


# ============================================================================
# GENERATOR 5 — Spare Parts Procurement Reasoning
# ~3 Q&A per part x (14 ontology + 15 FMEA) = ~87 examples
# ============================================================================

def gen_spare_parts(ontology: dict, fmea_nodes: dict) -> list[dict]:
    examples = []
    sp_cat = ontology.get("spare_parts_catalog", [])
    sp_nodes = fmea_nodes.get("SparePart", [])

    all_parts = list(sp_cat) + [
        {
            "part_number": n.get("id", "?").replace("PART:", ""),
            "part_name": n.get("part_name", n.get("label", "Unknown")),
            "stock_qty": n.get("stock_qty", 0),
            "min_stock_qty": n.get("min_stock_qty", 2),
            "lead_time_days": n.get("lead_time_days", 7),
            "criticality_override": n.get("criticality_override", "standard"),
            "note": n.get("procurement_note", ""),
            "compatible_families": [],
            "unit_cost_inr": "N/A",
        }
        for n in sp_nodes
    ]

    for part in all_parts:
        pname = part.get("part_name", "Unknown Part")
        pno = part.get("part_number", "?")
        stock = part.get("stock_qty", 0)
        min_stock = part.get("min_stock_qty", 2)
        lead = part.get("lead_time_days", 7)
        crit = part.get("criticality_override", "standard")
        note = part.get("note", "")
        compat = part.get("compatible_families", [])
        cost = part.get("unit_cost_inr", "N/A")

        if stock == 0:
            status = "OUT OF STOCK"
        elif stock < min_stock:
            status = "BELOW MINIMUM"
        else:
            status = "ADEQUATE"

        # V1 — can we repair now?
        examples.append({
            "instruction": (
                "Check the spare parts status and advise whether an emergency repair can proceed "
                "immediately or if procurement action is required first."
            ),
            "input": (
                f"Part required: {pname} (No.: {pno})\n"
                f"Current stock: {stock} | Min stock: {min_stock}\n"
                f"Lead time: {lead} days | Criticality: {crit.upper()}\n"
                f"Compatible equipment: {', '.join(compat) if compat else 'See catalogue'}\n"
                + (f"Note: {note}" if note else "")
            ).strip(),
            "output": (
                f"**Stock Status:** {status}\n\n"
                + (
                    f"**Cannot proceed immediately.** Part {pname} is out of stock.\n"
                    f"Actions:\n"
                    f"1. Raise emergency PO now — {lead}-day lead time\n"
                    f"2. Check for compatible substitute in plant stores\n"
                    f"3. Contact supplier for expedited delivery\n"
                    f"4. {'Escalate to maintenance manager and plant manager — critical path item.' if crit == 'critical' else 'Notify maintenance planner.'}\n"
                    f"5. Implement safe temporary workaround if operationally feasible\n"
                    f"Unit cost: INR {cost}"
                    if stock == 0
                    else
                    (
                        f"**Repair can proceed** — {stock} unit(s) in stock.\n"
                        f"**However, stock is below minimum ({min_stock}).** "
                        f"Raise replenishment PO immediately after consuming this part.\n"
                        f"Lead time for restock: {lead} days. Unit cost: INR {cost}."
                        if stock < min_stock
                        else
                        f"**Repair can proceed immediately.** Adequate stock: {stock} unit(s) (min: {min_stock}).\n"
                        f"Issue part from stores. Update inventory after consumption. Unit cost: INR {cost}."
                    )
                )
            ),
        })

        # V2 — procurement quantity calculation
        safety_stock = min_stock + max(1, int(lead / 14))
        order_qty = max(0, safety_stock - stock)
        examples.append({
            "instruction": (
                "Calculate the recommended procurement quantity and urgency for this spare part."
            ),
            "input": (
                f"Part: {pname} ({pno})\n"
                f"Current stock: {stock} | Min stock: {min_stock}\n"
                f"Lead time: {lead} days | Criticality: {crit.upper()}"
            ),
            "output": (
                f"**Procurement Analysis — {pname}:**\n\n"
                f"Current: {stock} units | Minimum required: {min_stock} | Safety stock target: {safety_stock}\n"
                f"**Recommended order quantity:** {max(order_qty, min_stock)} units\n"
                f"**Urgency:** {'IMMEDIATE — place order today' if stock <= min_stock else 'Include in next routine PO cycle'}\n\n"
                f"**Rationale:** With a {lead}-day lead time on a {crit.upper()} part, "
                f"stock must stay above {safety_stock} units to cover any failure during the procurement window. "
                f"{'Current zero stock creates direct production risk.' if stock == 0 else ''}"
            ),
        })

        # V3 — which equipment does this part protect?
        if compat:
            examples.append({
                "instruction": (
                    "Which equipment types are protected by maintaining adequate stock of this spare part, "
                    "and what failure modes does it mitigate?"
                ),
                "input": f"Part: {pname} ({pno}) | Compatible families: {', '.join(compat)}",
                "output": (
                    f"**{pname} ({pno}) — Coverage:**\n\n"
                    f"**Protects:** {bulleted([f.replace('_',' ').title() for f in compat])}\n\n"
                    f"**Failure modes mitigated:** Bearing overheating, mechanical seal leakage, "
                    f"and related rotating equipment failures — depending on application.\n\n"
                    f"**Stock recommendation:** Minimum {min_stock} units on-hand to cover simultaneous "
                    f"failures across the asset fleet. Never let stock drop to zero for a {crit.upper()} part."
                ),
            })

    return examples


# ============================================================================
# GENERATOR 6 — FMEA Multi-step Diagnostic Q&A
# ~3 variants per FailureMode x 52 nodes = ~156 examples
# ============================================================================

def gen_fmea_multistep(fmea_nodes: dict) -> list[dict]:
    examples = []
    fms = fmea_nodes.get("FailureMode", [])
    rcs = [n.get("label", "") for n in fmea_nodes.get("RootCause", [])]
    effects = fmea_nodes.get("Effect", [])
    actions = fmea_nodes.get("Action", [])
    sop_refs = fmea_nodes.get("SOPReference", [])

    for fm in fms:
        fm_name = fm.get("label", "Unknown")
        fm_id = fm.get("fault_code", "?")
        severity = fm.get("severity", "medium")
        mtbf = fm.get("mtbf_days", 365)
        safety_critical = fm.get("safety_critical", fm.get("is_safety_critical", False))

        rcs_s = random.sample(rcs, k=min(3, len(rcs)))
        eff_s = random.sample(effects, k=min(2, len(effects)))
        act_s = random.sample(actions, k=min(3, len(actions)))
        sop_s = random.sample(sop_refs, k=min(2, len(sop_refs)))

        # V1 — full diagnostic chain
        examples.append({
            "instruction": (
                "Provide a complete FMEA diagnostic chain for this fault code: "
                "failure mode → root causes → effects → corrective actions → SOPs."
            ),
            "input": (
                f"Fault code: {fm_id} | Failure mode: {fm_name}\n"
                f"Severity: {sev_word(severity)} | MTBF: {mtbf} days"
                + ("\nSAFETY CRITICAL: YES" if safety_critical else "")
            ).strip(),
            "output": (
                f"**FMEA Chain — {fm_name} ({fm_id})**\n\n"
                f"**1. Failure Mode:** {fm_name} — {sev_word(severity)}, MTBF {mtbf} days\n\n"
                f"**2. Root Causes:**\n{bulleted(rcs_s)}\n\n"
                f"**3. Failure Effects:**\n"
                + bulleted([f"{e.get('label','')} — impact: {e.get('impact','')}" for e in eff_s])
                + f"\n\n**4. Corrective Actions:**\n"
                + bulleted([f"{a.get('label','')} ({a.get('maintenance_type','corrective')}, ~{a.get('estimated_hours','?')} hrs)" for a in act_s])
                + f"\n\n**5. Reference SOPs:**\n"
                + bulleted([f"{s.get('sop_number','')} — {s.get('title','')}" for s in sop_s])
                + f"\n\n**Safety:** {'EMERGENCY isolation required before inspection — safety-critical event.' if safety_critical else 'Apply standard LOTO per plant procedure.'}"
            ),
        })

        # V2 — priority comparison vs another FM
        others = [f for f in fms if f.get("fault_code") != fm_id]
        if others:
            other = random.choice(others)
            o_name = other.get("label", "Unknown")
            o_id = other.get("fault_code", "?")
            o_sev = other.get("severity", "medium")
            o_mtbf = other.get("mtbf_days", 365)
            sev_rank = {"critical": 4, "high": 3, "medium": 2, "low": 1}
            if sev_rank.get(severity, 2) >= sev_rank.get(o_sev, 2):
                first_name, first_id, second_name, second_id = fm_name, fm_id, o_name, o_id
                first_sev, second_sev = severity, o_sev
            else:
                first_name, first_id, second_name, second_id = o_name, o_id, fm_name, fm_id
                first_sev, second_sev = o_sev, severity
            examples.append({
                "instruction": (
                    "Two faults are active simultaneously. Which should be addressed first? "
                    "Provide a prioritisation decision with reasoning."
                ),
                "input": (
                    f"Fault A: {fm_name} ({fm_id}) — Severity: {sev_word(severity)} — MTBF: {mtbf} days\n"
                    f"Fault B: {o_name} ({o_id}) — Severity: {sev_word(o_sev)} — MTBF: {o_mtbf} days"
                ),
                "output": (
                    f"**Prioritise FIRST: {first_name} ({first_id})**\n"
                    f"Reason: Higher severity ({sev_word(first_sev)}) + lower MTBF = greater failure risk per unit time.\n\n"
                    f"**Then address: {second_name} ({second_id})**\n"
                    f"Reason: {sev_word(second_sev)} severity — manageable with increased monitoring while Fault A is resolved.\n\n"
                    f"**Resource plan:**\n"
                    f"1. Assign full repair team to {first_name} immediately\n"
                    f"2. Increase monitoring on {second_name} to hourly readings\n"
                    f"3. If {second_name} escalates to CRITICAL during repair, split the team\n"
                    f"4. Raise work orders for both; update CMMS with priority flags"
                ),
            })

        # V3 — action duration estimate
        repair_hrs = sum(
            a.get("estimated_hours", 4) for a in random.sample(act_s, k=min(2, len(act_s)))
        ) if act_s else 8
        examples.append({
            "instruction": "Estimate the total repair duration and resource requirements for this fault.",
            "input": f"Fault: {fm_name} ({fm_id}) | Severity: {sev_word(severity)}",
            "output": (
                f"**Repair Estimate — {fm_name} ({fm_id})**\n\n"
                f"**Estimated total duration:** {repair_hrs}–{repair_hrs + 4} hours "
                f"(includes LOTO, inspection, repair, testing, return-to-service)\n\n"
                f"**Crew required:** 2–3 technicians (at least one experienced on {fm_name.lower()})\n\n"
                f"**Equipment/tools:**\n"
                f"- Calibrated vibration analyser (pre and post repair)\n"
                f"- Torque wrench (OEM-specified torques)\n"
                f"- Laser alignment tool (if shaft or coupling involved)\n"
                f"- Thermometer for bearing temperature baseline post-repair\n\n"
                f"**Production impact:** {'CRITICAL — full production shutdown during repair' if severity == 'critical' else 'Partial production impact — assess bypass options'}\n\n"
                f"**Cost estimate:** Labour {repair_hrs}–{repair_hrs+4} man-hours + parts cost from catalogue + production downtime loss."
            ),
        })

    return examples


# ============================================================================
# GENERATOR 7 — Maintenance Records
# ~2 Q&A per record x 60 records (cap 50) = ~100 examples
# ============================================================================

def gen_maintenance_records(docs: list[dict]) -> list[dict]:
    examples = []
    mr_docs = [d for d in docs if d.get("doc_type") == "maintenance_record"]

    for doc in mr_docs[:50]:
        content = doc.get("content_markdown", "")
        asset_id = doc.get("asset_id", "unknown")
        fam = doc.get("asset_family", "").replace("_", " ")
        fault_codes = doc.get("fault_codes_referenced", [])
        failure_modes = doc.get("failure_modes_referenced", [])
        if not content or len(content) < 150:
            continue

        fm = failure_modes[0] if failure_modes else "reported fault"
        fc = fault_codes[0] if fault_codes else "N/A"

        # V1 — summarise + follow-up
        examples.append({
            "instruction": (
                "Summarise this maintenance log entry: what work was done, what was found, "
                "and what follow-up actions are required."
            ),
            "input": f"Equipment: {asset_id} ({fam}) | Fault: {fm} ({fc})\n\n{content[:2000]}",
            "output": (
                f"**Maintenance Summary — {asset_id}:**\n\n"
                f"**Equipment:** {asset_id} ({fam}) | **Fault:** {fm} ({fc})\n\n"
                f"**Work Performed:** Equipment isolated per LOTO. {fm} confirmed on inspection. "
                f"Corrective maintenance carried out per applicable SOP. Safety checks completed before restart.\n\n"
                f"**Findings:** Fault code {fc} confirmed active. Physical evidence of {fm.lower()} noted. "
                f"All measurements taken and recorded.\n\n"
                f"**Follow-up actions:**\n"
                f"1. Update PM schedule based on this failure occurrence date\n"
                f"2. Replenish consumed spare parts — raise stores requisition\n"
                f"3. Close work order in CMMS; record actual labour hours\n"
                f"4. Review MTBF — consider PM interval adjustment if this failure was early"
            ),
        })

        # V2 — should we adjust PM interval?
        examples.append({
            "instruction": (
                "Based on this maintenance log, should the PM interval for this failure mode be adjusted? "
                "Provide data-driven reasoning."
            ),
            "input": f"Equipment: {asset_id} | Failure mode: {fm} | Maintenance log:\n{content[:1500]}",
            "output": (
                f"**PM Interval Review — {asset_id} / {fm}:**\n\n"
                f"**Recommendation:** If this failure occurred before the scheduled PM date, "
                f"shorten the interval by 15–20%. If at or after the scheduled date, "
                f"current interval is appropriate — do not change without 3+ data points.\n\n"
                f"**Data needed to decide:**\n"
                f"1. Date of last PM for {fm} on {asset_id}\n"
                f"2. The interval at time of failure\n"
                f"3. Fleet MTBF for this failure mode across similar assets\n"
                f"4. Operating duty cycle and load factor\n\n"
                f"**Action:** Record this event in CMMS. Trigger MTBF recalculation for {fam} fleet "
                f"on next monthly reliability review."
            ),
        })

    return examples


# ============================================================================
# GENERATOR 8 — General Knowledge (expanded hardcoded Q&A)
# 24 high-quality pairs
# ============================================================================

def gen_general_knowledge() -> list[dict]:
    pairs = [
        (
            "Explain the difference between corrective, preventive, and predictive maintenance with steel plant examples.",
            "",
            "**Maintenance Strategy Comparison:**\n\n"
            "**Corrective Maintenance (CM):** React to failure. Example: replacing a seized BF fan bearing after alarm.\n"
            "- Pro: No upfront cost | Con: Unplanned downtime, safety risk\n\n"
            "**Preventive Maintenance (PM):** Fixed-interval servicing. Example: pump oil change every 90 days.\n"
            "- Pro: Predictable | Con: May over-maintain; doesn't adapt to actual condition\n\n"
            "**Predictive Maintenance (PdM):** Condition-triggered. Example: schedule bearing replacement when vibration >7.1 mm/s RMS.\n"
            "- Pro: Maximises component life | Con: Requires sensor infrastructure + analytics\n\n"
            "**Best practice (RCM):** PdM for critical rotating assets, PM for wear-driven components, CM for low-cost non-critical items."
        ),
        (
            "What is ISO 14224 and why is it important for a steel plant CMMS?",
            "",
            "**ISO 14224 — Reliability Data Standard:**\n\n"
            "ISO 14224 defines standardised taxonomy for collecting and exchanging reliability and maintenance data "
            "(originally for oil/gas, now widely adopted in steel, mining, and heavy industry).\n\n"
            "**Why it matters:**\n"
            "1. Consistent failure mode classification → accurate MTBF calculation\n"
            "2. Enables fleet-wide benchmarking (compare BF fans across plants)\n"
            "3. CMMS integration — structured fault codes feed directly into work order management\n"
            "4. Foundation for RCM analysis and regulatory compliance reporting\n"
            "5. Data can be matched against OREDA and EFNMS industry databases\n\n"
            "**In practice:** Record every failure with ISO 14224 failure mode code, equipment class, and operating context."
        ),
        (
            "A blast furnace fan shows vibration of 8.5 mm/s RMS. What does this mean and what should be done?",
            "Normal: 0.5–4.5 mm/s. Warning: 7.1 mm/s. Critical: 11.2 mm/s.",
            "**Vibration Assessment — BF Fan:**\n\n"
            "**Status:** WARNING — 8.5 mm/s is above warning (7.1) but below critical (11.2).\n\n"
            "**Likely causes:** Shaft misalignment (1× and 2× RPM peaks), impeller erosion (blade-pass frequency), "
            "bearing wear (BPFI/BPFO/BSF), or foundation looseness.\n\n"
            "**Immediate actions:**\n"
            "1. Take vibration spectrum — identify dominant frequency\n"
            "2. Increase monitoring to every 4 hours\n"
            "3. Check bearing temperature (warning: 110°C, critical: 140°C)\n"
            "4. Notify maintenance planner — schedule inspection within 48 hours\n"
            "5. Pre-stage replacement parts\n\n"
            "**Escalation trigger:** If vibration reaches 11.2 mm/s → emergency shutdown per SOP-BF-AF-07 immediately."
        ),
        (
            "Explain FMEA Risk Priority Number (RPN) — formula, scales, and interpretation.",
            "",
            "**RPN = Severity (S) × Occurrence (O) × Detection (D)**\n\n"
            "Each factor rated 1–10:\n"
            "- **S (Severity):** Impact on safety, environment, production. 1 = negligible, 10 = catastrophic.\n"
            "- **O (Occurrence):** Likelihood of failure. 1 = rare, 10 = near-certain.\n"
            "- **D (Detection):** Ability to detect before harm. 1 = always detected, 10 = undetectable.\n\n"
            "**RPN thresholds (typical):**\n"
            "- 1–50: Low — standard PM controls adequate\n"
            "- 51–150: Medium — improve detection controls\n"
            "- 151–1000: High — engineering controls, redundancy, or design change required\n\n"
            "**Important:** Any item with S=9 or S=10 requires design-level controls regardless of RPN. "
            "RPN is a ranking tool, not an absolute risk measure."
        ),
        (
            "How do you set preventive maintenance intervals using MTBF?",
            "",
            "**PM Interval from MTBF:**\n\n"
            "**Rule:** Set PM interval at 50–70% of MTBF to intercept failures before they occur.\n\n"
            "**Example:** Centrifugal pump bearing MTBF = 480 days\n"
            "- Conservative: 480 × 0.5 = 240 days\n"
            "- Standard: 480 × 0.6 = 288 days\n"
            "- Aggressive: 480 × 0.7 = 336 days\n\n"
            "**Adjustment factors:**\n"
            "- High operating severity → shorten interval\n"
            "- High criticality → use conservative multiplier\n"
            "- PdM monitoring active → interval can be extended cautiously\n"
            "- 3+ real failure data points → update MTBF and recalculate quarterly\n\n"
            "**Caution:** OEM nameplate MTBF assumes ideal conditions. Always validate against plant-specific failure history."
        ),
        (
            "Walk me through the complete LOTO procedure for a centrifugal pump with electrical, hydraulic, and pressurised fluid energy.",
            "Equipment: centrifugal pump with three energy sources.",
            "**LOTO Procedure — Centrifugal Pump:**\n\n"
            "1. **Notify** control room and affected personnel\n"
            "2. **Identify all energy sources:** electrical (motor), hydraulic (seal flush), pressurised fluid (process)\n"
            "3. **Shut down** using normal stop procedure\n"
            "4. **Isolate each source:**\n"
            "   - Electrical: open and lock isolator switch, remove fuses\n"
            "   - Hydraulic: close and lock supply valve\n"
            "   - Pressure: close isolation valves, open vent/drain, verify zero gauge\n"
            "5. **Apply locks + tags:** each worker applies personal lock + tag with name, date, reason\n"
            "6. **Verify zero energy:** attempt start (should not start); measure zero voltage at terminals\n"
            "7. **Proceed with work**\n"
            "8. **Remove LOTO:** each worker removes only their own lock after confirming area is clear\n\n"
            "**Why mandatory:** Unexpected start-up during maintenance is a leading cause of fatalities in steel plants."
        ),
        (
            "Perform a Five-Whys RCA for a hydraulic power unit pressure relief valve stuck open (HPU-PRV-002).",
            "Fault: HPU-PRV-002 — PRV stuck open. Severity: CRITICAL.",
            "**Five-Whys RCA — HPU-PRV-002:**\n\n"
            "**Why 1:** PRV stuck open?\n→ Contamination debris lodged in valve seat, holding poppet open.\n\n"
            "**Why 2:** Contamination in valve seat?\n→ Hydraulic oil particle count exceeded ISO 4406 Class 18/16/13.\n\n"
            "**Why 3:** Oil particle count exceeded spec?\n→ Hydraulic filter not replaced at scheduled 270-day interval — overdue by 45 days.\n\n"
            "**Why 4:** Filter overdue?\n→ PM work order was deferred during high-production period without re-scheduling.\n\n"
            "**Why 5:** Deferral allowed without re-scheduling?\n→ CMMS does not auto-escalate deferred PMs — the overdue task fell off the backlog.\n\n"
            "**Root Cause Statement:** Absence of PM deferral escalation controls allowed a critical filter change to be missed, "
            "leading to oil contamination and PRV failure.\n\n"
            "**Corrective Actions:**\n"
            "1. Replace contaminated oil + filter immediately\n"
            "2. Replace PRV poppet assembly\n"
            "3. Implement CMMS rule: PM deferrals >7 days require maintenance manager approval\n"
            "4. Add oil particle monitoring to weekly maintenance rounds"
        ),
        (
            "Explain inner race spalling failure mechanism and the repair strategy for a hot strip mill conveyor bearing.",
            "Fault: RC-SPA-001. Vibration shows BPFI harmonic content.",
            "**Inner Race Spalling — RC-SPA-001:**\n\n"
            "**Failure Mechanism (4 stages):**\n"
            "1. **Crack initiation:** Sub-surface fatigue at rolling element contact — from Hertzian stress exceeding material fatigue limit\n"
            "2. **Crack propagation:** Grows with load cycles; accelerated by lubrication breakdown, false brinelling, or high load\n"
            "3. **Spall formation:** Crack reaches surface → material ejection → pit/spall on inner race\n"
            "4. **Rapid progression:** Spall debris enters lubricant, three-body abrasion accelerates; catastrophic failure imminent\n\n"
            "**Vibration signature:** BPFI = (n/2) × RPM × (1 + D_b/D_p × cosα) — this frequency identifies inner race damage.\n\n"
            "**Repair Strategy:**\n"
            "1. Reduce load/speed if possible; increase monitoring to 2-hour intervals\n"
            "2. Replace bearing at next planned outage (within 72 hours at this stage)\n"
            "3. Use correct puller; never hammer-drive a bearing\n"
            "4. Root cause: check alignment, lubrication type/quantity/interval, vibration sources causing false brinelling\n"
            "5. Post-repair: record baseline BPFI amplitude; set alert threshold"
        ),
        (
            "What spare parts should a centrifugal pump fleet of 8 units maintain on-hand, and how to calculate minimum quantities?",
            "Fleet: 8 pumps. Failure modes: mechanical seal leakage (MTBF 480d), bearing fatigue (MTBF 900d), cavitation damage.",
            "**Spare Parts Strategy — 8-unit Centrifugal Pump Fleet:**\n\n"
            "| Part | Min Stock | Basis |\n"
            "|---|---|---|\n"
            "| Mechanical seal | 4 | MTBF 480d → ~6 failures/year across 8 units |\n"
            "| Drive-end bearing | 8 | MTBF 900d, pairs consumed per event |\n"
            "| Non-drive-end bearing | 8 | Same |\n"
            "| Impeller wear ring | 4 | Cavitation damage, frequent |\n"
            "| Coupling element | 4 | Short MTBF, critical |\n"
            "| O-ring/gasket sets | 6 | Low cost, consumed at every seal job |\n\n"
            "**Minimum stock formula:**\n"
            "Min = ⌈ Fleet / MTBF × Lead_time × Safety_factor ⌉\n"
            "Example (seal, MTBF=480, lead=21d, factor=2.0): ⌈8/480×21×2⌉ = ⌈1.4⌉ = 2\n\n"
            "**Rule:** For critical single-point-of-failure parts, minimum = max(formula, 2).\n"
            "Review quarterly using actual CMMS failure rate data."
        ),
        (
            "How does cavitation manifest in a centrifugal pump and what are the corrective + preventive measures?",
            "Fault: CP-CAV-002. Symptoms: low discharge pressure, crackling noise, vibration increase.",
            "**Cavitation — CP-CAV-002:**\n\n"
            "**Mechanism:** Fluid pressure at pump inlet drops below vapour pressure → vapour bubbles form → bubbles implode violently on high-pressure impeller side → micro-jets erode impeller metal.\n\n"
            "**Observable symptoms:**\n"
            "- Crackling 'gravel in pump' noise (bubble implosion)\n"
            "- Discharge pressure fluctuation and reduction\n"
            "- Random-frequency vibration (not synchronous with RPM)\n"
            "- Erosion pitting on impeller leading edges (visible on inspection)\n\n"
            "**Root causes to check:**\n"
            "1. NPSH available < NPSH required\n"
            "2. Blocked suction strainer or excessive suction lift\n"
            "3. Pump running far right of BEP curve (high flow)\n"
            "4. High fluid temperature\n\n"
            "**Corrective:** Clean suction strainer; verify suction valve fully open; adjust operating point toward BEP; inspect/replace eroded impeller.\n\n"
            "**Preventive:** Install low-suction-pressure alarm at 0.5 bar above NPSHR; quarterly strainer inspection; verify pump selection within 70–120% BEP flow."
        ),
        (
            "What is MTBF vs MTTR and how do they combine to give equipment availability?",
            "",
            "**MTBF:** Mean Time Between Failures = Total uptime / Number of failures\n"
            "Example: 5,000 hours / 4 failures = 1,250 hours\n\n"
            "**MTTR:** Mean Time To Repair = Total downtime / Number of failures\n"
            "Example: 24 hours downtime / 4 failures = 6 hours\n\n"
            "**Availability = MTBF / (MTBF + MTTR)**\n"
            "Example: 1250 / (1250 + 6) = 99.5%\n\n"
            "**How to improve:**\n"
            "- MTBF: better PM, condition monitoring, root cause elimination\n"
            "- MTTR: spare parts on-hand, trained technicians, clear SOPs, efficient LOTO\n\n"
            "**Targets (steel plant):**\n"
            "- Critical rotating equipment (BF fans, main pumps): ≥98.5%\n"
            "- Balance-of-plant: ≥95%\n"
            "- Instrumentation: ≥99%"
        ),
        (
            "Describe a complete bearing inspection procedure after a BF fan high-temperature alarm at 118°C.",
            "Alarm: bearing temp 118°C. Warning threshold: 110°C. Critical: 140°C. Vibration: 5.2 mm/s (within warning band).",
            "**BF Fan Bearing Inspection — 118°C Alarm:**\n\n"
            "**Status:** WARNING — 118°C > 110°C threshold but below 140°C critical. Do not emergency-stop yet.\n\n"
            "**Step 1 — Immediate monitoring (no shutdown):**\n"
            "- Read temperature trend over last 2 hours: rising / stable / falling?\n"
            "- Take vibration spectrum for bearing defect frequencies (BPFI/BPFO/BSF)\n"
            "- Check motor current for any anomalous increase\n"
            "- Increase monitoring to every 30 minutes\n\n"
            "**Step 2 — External inspection (while running, safe distance):**\n"
            "- Check for grease/oil leakage at bearing housing seals\n"
            "- Listen for crackling or grinding noise\n"
            "- Verify oil sight glass shows correct level\n\n"
            "**Decision gate:**\n"
            "- Rising toward 130°C → prepare controlled shutdown\n"
            "- Stable at 118°C → schedule inspection within 8 hours\n"
            "- Falling → check if cooling water restored\n\n"
            "**Step 3 — Inspection (after controlled shutdown):**\n"
            "1. Shut down per SOP-BF-AF-07; apply LOTO; cool to <50°C\n"
            "2. Drain oil; take sample (NAS class + water content)\n"
            "3. Remove housing cover; inspect races for discolouration, pitting, cage damage\n"
            "4. Measure clearance vs OEM spec\n"
            "5. Replace bearing (SKF-6310-2RS1) if defects found\n\n"
            "**Document:** All readings + oil sample + findings in maintenance log (fault code BF-BRG-002)."
        ),
        (
            "What is Reliability Centred Maintenance (RCM) and how would you apply it to a steel plant?",
            "",
            "**RCM — Reliability Centred Maintenance:**\n\n"
            "RCM is a structured methodology for determining the most cost-effective maintenance strategy "
            "for each asset, based on its failure modes and consequences.\n\n"
            "**RCM 7-question process:**\n"
            "1. What does the asset do? (Function)\n"
            "2. In what ways can it fail? (Functional failures)\n"
            "3. What causes each failure? (Failure modes — FMEA)\n"
            "4. What happens when it fails? (Failure effects)\n"
            "5. How does each failure matter? (Consequences — safety/operational/economic)\n"
            "6. What can be done to predict or prevent each failure? (Proactive tasks)\n"
            "7. What if no proactive task can be found? (Default actions)\n\n"
            "**Application to steel plant:**\n"
            "- Critical blast furnace fans → PdM (vibration + temperature monitoring) + short PM interval\n"
            "- Non-critical conveyor rollers → run-to-failure with fast replacement strategy\n"
            "- Safety-critical PRVs → inspection-based (functional test) at fixed interval\n\n"
            "**Output:** Asset-specific maintenance plan optimised for cost vs risk."
        ),
        (
            "How do you calculate and interpret the Overall Equipment Effectiveness (OEE) for a steel plant conveyor?",
            "Data: Availability 92%, Performance 88%, Quality 97%.",
            "**OEE = Availability × Performance × Quality**\n\n"
            "OEE = 0.92 × 0.88 × 0.97 = **0.786 → 78.6%**\n\n"
            "**World-class OEE benchmark:** ≥85% for discrete manufacturing.\n\n"
            "**Interpretation of this result (78.6%):**\n"
            "Below world-class. Largest opportunity is Performance (88%) — the equipment is available "
            "but not running at full speed/capacity when running.\n\n"
            "**Component breakdown:**\n"
            "- **Availability 92%:** 8% lost to downtime (planned + unplanned). "
            "Investigate top 3 downtime events — likely bearing failures or conveyor jams.\n"
            "- **Performance 88%:** Running slower than design speed or with minor stops. "
            "Check for drive coupling issues or spray nozzle blockage slowing throughput.\n"
            "- **Quality 97%:** 3% product defects or rejects — good. Keep monitoring.\n\n"
            "**Priority actions:** Improve Performance first (highest gap), then Availability."
        ),
        (
            "What is condition monitoring and which techniques are most effective for rotating equipment in a steel plant?",
            "",
            "**Condition Monitoring for Rotating Equipment:**\n\n"
            "Condition monitoring (CM) uses regular measurement of equipment parameters to detect degradation "
            "before failure — the foundation of predictive maintenance.\n\n"
            "**Top techniques for steel plant rotating equipment:**\n\n"
            "**1. Vibration analysis (most powerful):**\n"
            "- Detects: bearing defects, imbalance, misalignment, looseness, gear faults\n"
            "- Tools: handheld vibration analyser, online CMS with 4–20 mA transmitters\n"
            "- Frequency: weekly (critical), monthly (standard)\n\n"
            "**2. Thermography (infrared):**\n"
            "- Detects: electrical hotspots, bearing overheating, refractory loss, fluid leaks\n"
            "- Tools: FLIR camera during operation\n"
            "- Frequency: quarterly\n\n"
            "**3. Oil analysis:**\n"
            "- Detects: contamination (water, particles), additive depletion, wear metal debris\n"
            "- Tools: ISO 4406 particle counter, spectroscopic oil analysis\n"
            "- Frequency: per oil change interval + after any suspected contamination event\n\n"
            "**4. Ultrasound:**\n"
            "- Detects: early-stage bearing lubrication loss, steam trap faults, compressed air leaks\n"
            "- Most sensitive for catching bearing faults before vibration changes appear\n\n"
            "**5. Motor current signature analysis (MCSA):**\n"
            "- Detects: rotor bar faults, misalignment, load variation — from the MCC panel, no sensor required"
        ),
        (
            "A centrifugal pump's discharge pressure has dropped 15% over 2 weeks. Walk through a systematic diagnosis.",
            "Pump: PUMP-CW-02. Baseline pressure: 4.2 bar. Current: 3.57 bar. No alarms triggered.",
            "**Systematic Diagnosis — Pump Pressure Decline:**\n\n"
            "**Step 1 — Rule out instrumentation fault:**\n"
            "Calibrate or replace pressure gauge/transmitter. Compare against portable reference gauge.\n\n"
            "**Step 2 — Check operating point vs pump curve:**\n"
            "Review whether flow demand has increased (system resistance changed). "
            "A higher flow point on the curve gives lower pressure — this is normal pump behaviour, not a fault.\n\n"
            "**Step 3 — Inspect for cavitation:**\n"
            "Listen for crackling noise. Check NPSH conditions (suction head, fluid temperature, strainer blockage). "
            "Cavitation causes gradual pressure loss + impeller erosion.\n\n"
            "**Step 4 — Check impeller condition:**\n"
            "If system resistance and NPSH are normal, impeller erosion (from cavitation or abrasion) "
            "reduces pump efficiency → lower pressure at same speed.\n\n"
            "**Step 5 — Check for internal recirculation / wear ring clearance:**\n"
            "Excessive wear ring clearance allows internal recirculation, reducing net head. "
            "Inspect wear rings — replace if clearance exceeds OEM spec.\n\n"
            "**Likely root cause at 15% decline:** Impeller erosion or excessive wear ring clearance. "
            "Schedule internal inspection at next maintenance window."
        ),
        (
            "What information should a maintenance engineer capture in a CMMS work order to ensure useful reliability data?",
            "",
            "**CMMS Work Order — Required Data Fields for Reliability:**\n\n"
            "1. **Equipment ID** — exact asset (not just 'pump area')\n"
            "2. **ISO 14224 failure mode code** — standardised taxonomy\n"
            "3. **Fault code** — plant-specific (e.g. BF-BRG-002)\n"
            "4. **Failure date and time** — exact timestamp from alarm log\n"
            "5. **Detection method** — how was the failure found? (alarm/inspection/CM/operator report)\n"
            "6. **Failure mechanism** — what physically caused it? (erosion, fatigue, contamination…)\n"
            "7. **Repair start and end times** — enables MTTR calculation\n"
            "8. **Repair actions taken** — specific steps, not just 'bearing replaced'\n"
            "9. **Parts consumed** — part numbers + quantities\n"
            "10. **Labour hours by trade** — for cost accounting\n"
            "11. **Root cause** — 5-why or fishbone result\n"
            "12. **Recommendations** — PM interval change? New monitoring? SOP update?\n\n"
            "**Why it matters:** Poor data = poor MTBF estimates = wrong PM intervals = more unplanned failures. "
            "Every field is an input to the reliability model."
        ),
        (
            "Explain the difference between run-to-failure, time-based replacement, and condition-based replacement strategies for spare parts.",
            "Context: steel plant maintenance planning.",
            "**Replacement Strategy Comparison:**\n\n"
            "**Run-to-Failure (RTF):**\n"
            "Replace only when the component fails. No monitoring, no planned replacement.\n"
            "- Best for: low-cost, non-critical, easily replaced items (fuses, V-belts, filters)\n"
            "- Risk: unplanned downtime if used on critical equipment\n\n"
            "**Time-Based Replacement (TBR):**\n"
            "Replace at fixed interval regardless of condition (e.g. 'replace seal every 480 days').\n"
            "- Best for: wear-driven components with consistent MTBF and clear failure pattern\n"
            "- Risk: may replace perfectly good components (over-maintenance) or miss early failures on variable-duty assets\n\n"
            "**Condition-Based Replacement (CBR):**\n"
            "Replace when condition monitoring indicates degradation approaching failure threshold.\n"
            "- Best for: high-value critical components (bearings, mechanical seals, impellers)\n"
            "- Requires: sensor data, alarm thresholds, trained analysts\n"
            "- Benefit: maximises component life, minimises unnecessary replacement, prevents unplanned failure\n\n"
            "**Steel plant application:** CBR for critical rotating equipment, TBR for consumables with known wear life, RTF for non-critical low-cost items."
        ),
        (
            "How do you create and use an equipment criticality matrix in a steel plant?",
            "",
            "**Equipment Criticality Matrix:**\n\n"
            "A criticality matrix ranks all assets by the consequence of their failure, "
            "driving decisions on maintenance strategy, spare parts holding, and monitoring investment.\n\n"
            "**Two axes:**\n"
            "- **Consequence (Y-axis):** Safety impact × Production impact × Environmental impact × Repair cost\n"
            "- **Likelihood (X-axis):** Failure probability = 1/MTBF × operating hours\n\n"
            "**Rating scale (1–5 each):**\n"
            "| Score | Consequence | Likelihood |\n"
            "|---|---|---|\n"
            "| 5 | Fatality / total plant shutdown | >4 failures/year |\n"
            "| 3 | Significant downtime / injury risk | 1–4 failures/year |\n"
            "| 1 | No downtime / cosmetic | <1 failure/year |\n\n"
            "**Criticality = Consequence × Likelihood**\n\n"
            "**Steel plant examples:**\n"
            "- BF fan (C=5, L=3) = 15 → CRITICAL → PdM + short PM + critical spare parts on-hand\n"
            "- Cooling water pump (C=3, L=2) = 6 → HIGH → PdM + standard PM\n"
            "- Air compressor dryer (C=1, L=2) = 2 → LOW → PM only, no spare parts holding\n\n"
            "**Review:** Update criticality matrix annually or after any CRITICAL failure event."
        ),
        (
            "What is the difference between MTBF and B10 life, and when should each be used?",
            "",
            "**MTBF vs B10 Life:**\n\n"
            "**MTBF (Mean Time Between Failures):**\n"
            "- Average time between failures for a REPAIRABLE system\n"
            "- Assumes constant failure rate (exponential distribution)\n"
            "- Best for: complex repairable systems, electronic components, system-level reliability\n"
            "- Limitation: masks infant mortality and wear-out phases\n\n"
            "**B10 Life (L10):**\n"
            "- Time at which 10% of a bearing/component population has failed\n"
            "- Based on Weibull distribution — captures wear-out behaviour accurately\n"
            "- Best for: rolling element bearings, mechanical seals, fatigue-limited components\n"
            "- Used directly in: ISO 281 bearing life calculation\n\n"
            "**When to use each:**\n"
            "- Setting PM intervals for systems (assets as a whole) → use MTBF\n"
            "- Selecting bearings or specifying component replacement intervals → use B10 / L10\n"
            "- RCM analysis of wear-out failure modes → use Weibull (B10/B50/B90)\n\n"
            "**Practical rule:** For steel plant rotating equipment, use B10 for bearing replacement schedule and MTBF for overall equipment availability targets."
        ),
        (
            "A hydraulic power unit shows oil temperature of 78°C (normal max 65°C). What is the diagnosis and response?",
            "HPU normal operating temp: 45–65°C. Warning: 70°C. Critical: 85°C.",
            "**HPU Oil Temperature Assessment — 78°C:**\n\n"
            "**Status:** WARNING — above normal max (65°C) and above warning threshold (70°C), below critical (85°C).\n\n"
            "**Likely causes:**\n"
            "1. Oil cooler fouling — reduced heat transfer efficiency\n"
            "2. Oil cooler coolant flow reduced (blocked line, failed pump)\n"
            "3. Oil viscosity too low for operating temperature → excessive internal leakage generating heat\n"
            "4. Relief valve partially open — circulating oil at high pressure without doing work\n"
            "5. Operating load higher than design (system pressure elevated)\n\n"
            "**Immediate actions:**\n"
            "1. Check oil cooler coolant inlet/outlet temperatures and flow rate\n"
            "2. Inspect cooler for fouling; flush if blocked\n"
            "3. Check system pressure vs relief valve setting\n"
            "4. Monitor temperature trend — take reading every 15 minutes\n"
            "5. If rising toward 80°C, reduce system load; above 85°C = emergency shutdown\n\n"
            "**Root cause fix:** Clean oil cooler; verify coolant system; check oil viscosity grade matches operating temperature; service relief valve."
        ),
        (
            "Explain spray nozzle blockage on a hot strip mill conveyor: failure mechanism, detection, and resolution.",
            "Fault code: CONV-SPR-003. MTBF: 90 days. Severity: medium.",
            "**Spray Nozzle Blockage — CONV-SPR-003:**\n\n"
            "**Failure Mechanism:**\n"
            "Hot strip mill conveyors use cooling water spray to control strip temperature and prevent thermal damage. "
            "Nozzles block when:\n"
            "1. Scale and oxide particles from strip surface deposit inside nozzles\n"
            "2. Hard water calcium carbonate precipitates over time\n"
            "3. Foreign debris enters the spray header\n"
            "4. Corrosion products from piping accumulate at nozzle tip\n\n"
            "**Detection (MTBF 90 days — high frequency):**\n"
            "- Visual inspection during operation (blocked nozzle = no spray or reduced cone)\n"
            "- Strip temperature profile deviation (hot spot downstream of blocked zone)\n"
            "- Flow meter reading below baseline on that spray header\n\n"
            "**Resolution:**\n"
            "1. **Immediate:** Isolate blocked header, remove nozzles, clean with descaling solution or wire brush\n"
            "2. **Check:** Verify spray cone pattern on bench before reinstalling\n"
            "3. **System:** Flush header to remove accumulated debris before reinstating\n\n"
            "**Prevention (90-day MTBF — requires proactive programme):**\n"
            "- Biweekly nozzle inspection (visual during scheduled stops)\n"
            "- Inline strainer on spray header — clean monthly\n"
            "- Water treatment programme to reduce hardness and scale formation\n"
            "- Replace nozzles on fixed 60-day cycle rather than waiting for blockage"
        ),
        (
            "How do you build a business case for investing in online condition monitoring for a critical blast furnace fan?",
            "Current state: manual monthly vibration checks. BF fan: criticality=high, MTBF=720 days, 1 unplanned failure/18 months.",
            "**Business Case — Online CMS for BF Fan:**\n\n"
            "**Current state costs (per year):**\n"
            "- Unplanned failure rate: ~0.67 events/year (1 per 18 months)\n"
            "- Average downtime per event: 24–48 hours\n"
            "- Production loss per hour (BF area): assume INR 5L/hour (estimate; use actual)\n"
            "- Cost per unplanned event: 24h × 5L = INR 1.2 crore + emergency labour + parts\n"
            "- Annual unplanned cost: ~INR 80L–1.2Cr/year\n\n"
            "**Online CMS investment:**\n"
            "- 4-channel vibration + temperature transmitter: ~INR 8–12L\n"
            "- Annual software + support: ~INR 2L\n"
            "- Implementation (installation + training): ~INR 3L\n"
            "- Total Year 1: ~INR 13–17L\n\n"
            "**Expected benefit:**\n"
            "- Catch 90% of failures in early warning phase → convert to planned outage (8h vs 48h)\n"
            "- Downtime reduction: 40h/event saved × 0.67 events × 5L/hour = ~INR 1.34Cr/year\n"
            "- Net benefit Year 1: INR 1.34Cr – 17L = INR 1.17Cr\n"
            "- **Payback period: <2 months**\n\n"
            "**Recommendation:** Approve immediately. Online CMS on critical BF fans is among the highest-ROI maintenance investments available."
        ),
        (
            "What questions should a maintenance manager ask before approving a request to extend a PM interval by 30%?",
            "",
            "**PM Interval Extension — Approval Checklist:**\n\n"
            "Before approving a 30% interval extension, the maintenance manager must confirm:\n\n"
            "1. **Data basis:** Is the extension based on ≥3 actual failure data points or just one event? "
            "A single 'no failure found' PM is insufficient justification.\n\n"
            "2. **MTBF validation:** Has the new MTBF been calculated from plant-specific data, not just OEM spec?\n\n"
            "3. **Operating conditions:** Have duty cycle, load factor, or environmental conditions changed? "
            "If operating severity increased, interval should be shortened, not extended.\n\n"
            "4. **Condition monitoring coverage:** Is there active PdM (vibration/temperature monitoring) "
            "to catch any failure that occurs in the extended window? Without PdM, extension is higher risk.\n\n"
            "5. **Criticality:** What is the consequence of failure during the extended interval? "
            "Never extend intervals on safety-critical items without a signed risk assessment.\n\n"
            "6. **Trial plan:** Is the first extension a trial (1 cycle) with mandatory inspection at end, "
            "before becoming permanent policy?\n\n"
            "7. **Rollback trigger:** What sensor threshold or finding during inspection triggers immediate "
            "reversal to the original interval?\n\n"
            "**Approve only if:** ≥3 data points + PdM coverage + trial plan + rollback trigger defined."
        ),
    ]
    return [{"instruction": p[0], "input": p[1], "output": p[2]} for p in pairs]


# ============================================================================
# GENERATOR 9 — Incident Summaries
# ~2 Q&A per incident doc x 16 = ~32 examples
# ============================================================================

def gen_incident_summaries(docs: list[dict]) -> list[dict]:
    examples = []
    for doc in docs:
        if doc.get("doc_type") != "incident_summary":
            continue
        content = doc.get("content_markdown", "")
        asset_id = doc.get("asset_id", "unknown")
        fam = doc.get("asset_family", "").replace("_", " ")
        fault_codes = doc.get("fault_codes_referenced", [])
        failure_modes = doc.get("failure_modes_referenced", [])
        if not content or len(content) < 150:
            continue
        fm = failure_modes[0] if failure_modes else "incident"
        fc = fault_codes[0] if fault_codes else "N/A"

        examples.append({
            "instruction": (
                "Read this incident summary. Extract: (1) what failed, (2) immediate cause, "
                "(3) production impact, (4) top preventive action."
            ),
            "input": f"Equipment: {asset_id} ({fam}) | Fault: {fc}\n\n{content[:2000]}",
            "output": (
                f"**1. What Failed:** {fm} on {asset_id} ({fam})\n\n"
                f"**2. Immediate Cause:** Fault code {fc} triggered when equipment reached failure threshold for {fm.lower()}.\n\n"
                f"**3. Production Impact:** Unplanned downtime — shutdown of {asset_id}. "
                f"Full impact (hours + production loss) in the incident report.\n\n"
                f"**4. Top Preventive Action:** Implement or reinforce condition-based monitoring for {fm.lower()} — "
                f"set sensor alert at warning level to intercept fault before critical state forces unplanned shutdown."
            ),
        })

        examples.append({
            "instruction": "What lessons learned should be captured from this incident to prevent recurrence?",
            "input": f"Incident: {fm} ({fc}) on {asset_id} ({fam})\n\n{content[:1800]}",
            "output": (
                f"**Lessons Learned — {asset_id} / {fc}:**\n\n"
                f"**1. Detection gap:** The failure was not detected early enough to prevent unplanned shutdown. "
                f"Add or lower alert threshold for {fm.lower()} monitoring.\n\n"
                f"**2. PM effectiveness:** Review whether the scheduled PM for {fm.lower()} on {asset_id} was current. "
                f"If PM was overdue, this is a scheduling/backlog management issue.\n\n"
                f"**3. Spare parts readiness:** Confirm critical parts for {fm.lower()} repair are stocked above minimum at all times.\n\n"
                f"**4. Knowledge transfer:** Share failure details with all {fam} equipment maintainers — "
                f"add to site failure case library.\n\n"
                f"**5. SOP review:** Verify the applicable SOP covers this failure mode fully and update if gaps are found."
            ),
        })

    return examples


# ============================================================================
# GENERATOR 10 — Sensor Threshold Q&A (from ontology)
# ~3 Q&A per family x 5 families = ~15 examples
# ============================================================================

def gen_sensor_thresholds(ontology: dict) -> list[dict]:
    examples = []
    for fam_name, fam in ontology.get("asset_families", {}).items():
        fam_label = fam_name.replace("_", " ").title()
        sr = fam.get("sensor_ranges", {})
        if not sr:
            continue

        # V1 — full threshold reference
        examples.append({
            "instruction": f"What are the normal operating ranges and alarm thresholds for a {fam_label}?",
            "input": f"Equipment class: {fam_label}",
            "output": f"**Sensor Thresholds — {fam_label}:**\n\n" + "\n".join(
                f"**{r.get('description', sensor)} ({sensor})**\n"
                f"  Normal: {r.get('normal_min','?')}–{r.get('normal_max','?')}\n"
                f"  Warning: {r.get('warning_min','?')}–{r.get('warning_max','?')}\n"
                f"  Critical: {r.get('critical_min','?')}–{r.get('critical_max','?')}"
                for sensor, r in sr.items()
            ),
        })

        # V2 — multi-sensor reading assessment (all at 10% above normal_max)
        reading_lines, status_lines = [], []
        for sensor, r in sr.items():
            desc = r.get("description", sensor)
            nm = r.get("normal_max", 100)
            wm = r.get("warning_max", nm * 1.2)
            val = round(nm * 1.08, 1)
            status = "WARNING" if val > nm and val <= wm else ("CRITICAL" if val > wm else "NORMAL")
            reading_lines.append(f"- {desc}: {val}")
            status_lines.append(f"- {desc}: {val} → **{status}**")
        examples.append({
            "instruction": (
                f"Assess these sensor readings for a {fam_label}. "
                f"Classify each as NORMAL, WARNING, or CRITICAL and recommend a response level."
            ),
            "input": f"Equipment: {fam_label}\n\n" + "\n".join(reading_lines),
            "output": (
                f"**Sensor Assessment — {fam_label}:**\n\n"
                + "\n".join(status_lines)
                + f"\n\n**Overall:** Readings are borderline WARNING — just above normal range.\n\n"
                f"**Response:** Increase monitoring frequency; trend readings over next 4 hours; "
                f"notify shift supervisor; pre-stage replacement parts; schedule inspection within 24 hours. "
                f"Do NOT shut down unless any parameter crosses critical threshold."
            ),
        })

        # V3 — what to do when a critical reading is received
        for sensor, r in list(sr.items())[:1]:  # just first sensor
            crit_max = r.get("critical_max", 140)
            desc = r.get("description", sensor)
            examples.append({
                "instruction": (
                    f"A {fam_label} has just reported a {desc} reading of {crit_max} (critical threshold). "
                    f"What is the immediate response protocol?"
                ),
                "input": f"Equipment: {fam_label} | Sensor: {desc} | Reading: {crit_max} | Threshold: CRITICAL",
                "output": (
                    f"**CRITICAL ALARM RESPONSE — {fam_label}:**\n\n"
                    f"**Immediate actions (execute within 2 minutes):**\n"
                    f"1. Acknowledge alarm in control room — do NOT silence without action\n"
                    f"2. Notify shift supervisor and maintenance on-call\n"
                    f"3. Initiate controlled shutdown of {fam_label} per applicable emergency SOP\n"
                    f"4. Apply LOTO as soon as equipment is at rest\n"
                    f"5. Do NOT restart without maintenance inspection and sign-off\n\n"
                    f"**Parallel actions:**\n"
                    f"- Record exact {desc} reading and timestamp in the logbook\n"
                    f"- Pull failure mode reference for this alarm from CMMS\n"
                    f"- Confirm spare parts availability for likely root cause\n"
                    f"- Notify operations manager of production impact\n\n"
                    f"**Investigation:** After LOTO and cool-down, inspect the {fam_label} for the failure mode "
                    f"that produces high {desc} — typically bearing overheating, lubrication failure, or process upset."
                ),
            })

    return examples


# ============================================================================
# GENERATOR 11 — Manuals: extract & apply
# ~2 Q&A per manual doc x 40 = ~80 examples
# ============================================================================

def gen_manual_qa(docs: list[dict]) -> list[dict]:
    examples = []
    manual_docs = [d for d in docs if d.get("doc_type") == "manual"]

    for doc in manual_docs[:40]:
        content = doc.get("content_markdown", "")
        asset_id = doc.get("asset_id", "unknown")
        fam = doc.get("asset_family", "").replace("_", " ")
        failure_modes = doc.get("failure_modes_referenced", [])
        fault_codes = doc.get("fault_codes_referenced", [])
        if not content or len(content) < 200:
            continue

        fm = failure_modes[0] if failure_modes else "equipment fault"
        fc = fault_codes[0] if fault_codes else "N/A"
        snippet = content[:2200]

        # V1 — extract key specs
        examples.append({
            "instruction": (
                "Extract the key technical specifications and maintenance-relevant parameters "
                "from this equipment manual section."
            ),
            "input": f"Equipment: {asset_id} ({fam})\n\nManual excerpt:\n{snippet}",
            "output": (
                f"**Key Specifications — {asset_id} ({fam}):**\n\n"
                f"**Design parameters:** Refer to the design parameters table in the manual "
                f"(rated RPM, power, flow, pressure as applicable to this asset class).\n\n"
                f"**Failure mode coverage:** {fm} ({fc})\n\n"
                f"**Maintenance-relevant items:**\n"
                f"- Lubrication type, grade, and change interval\n"
                f"- Bearing model and replacement specification\n"
                f"- Alignment tolerance (±mm)\n"
                f"- Torque specifications for critical fasteners\n"
                f"- Sensor setpoints: normal / warning / critical thresholds\n\n"
                f"**Cross-reference:** Use fault code {fc} to locate the matching failure analysis report "
                f"and SOP for this asset."
            ),
        })

        # V2 — troubleshoot from manual
        examples.append({
            "instruction": (
                "A technician is troubleshooting fault code {fc} on {asset_id}. "
                "Using this manual excerpt, what are the recommended diagnostic steps?"
            ).format(fc=fc, asset_id=asset_id),
            "input": f"Equipment: {asset_id} ({fam}) | Fault: {fm} ({fc})\n\nManual:\n{snippet}",
            "output": (
                f"**Diagnostic Steps — {asset_id} / {fm} ({fc}):**\n\n"
                f"**Step 1:** Confirm fault code {fc} is active in the control system. Record all current sensor readings.\n\n"
                f"**Step 2:** Compare readings against normal operating ranges from the manual. "
                f"Identify which parameters are out of specification.\n\n"
                f"**Step 3:** Cross-reference the fault code with the failure mode description. "
                f"This will point to the affected subsystem and probable root cause.\n\n"
                f"**Step 4:** Follow the manual's troubleshooting decision tree for {fm.lower()}. "
                f"Check the primary cause first; if not found, systematically check contributing factors.\n\n"
                f"**Step 5:** Once confirmed, execute corrective action per the SOP referenced in the manual.\n\n"
                f"**Document:** Record all readings and findings in the CMMS work order before and after repair."
            ),
        })

    return examples


# ============================================================================
# GENERATOR 12 — Multi-turn scenario Q&A (simulated conversation style)
# Additional diverse examples targeting edge cases
# ============================================================================

def gen_multi_scenario() -> list[dict]:
    scenarios = [
        {
            "instruction": "A new maintenance technician asks: 'What is a fault code and how do I use it?' Explain simply.",
            "input": "Context: steel plant rotating equipment maintenance.",
            "output": (
                "**What is a Fault Code?**\n\n"
                "A fault code is a short alphanumeric identifier that tells you exactly what is wrong with a piece of equipment. "
                "Think of it like a barcode for failures.\n\n"
                "**Example:** BF-BRG-002 tells you:\n"
                "- BF = Blast Furnace area\n"
                "- BRG = Bearing fault type\n"
                "- 002 = Specific failure mode number (bearing overheating)\n\n"
                "**How to use it:**\n"
                "1. When an alarm triggers, read the fault code from the control panel display\n"
                "2. Look it up in the CMMS or fault code reference card\n"
                "3. The system tells you: what failed, what to check, which SOP to follow, which parts to get\n"
                "4. Record the fault code on your maintenance work order — this builds the reliability database\n\n"
                "**Rule:** Never clear a fault code without identifying and fixing the root cause. Clearing without fixing = the fault will return."
            ),
        },
        {
            "instruction": "What is the best way to communicate a critical equipment failure to the production team?",
            "input": "Scenario: BF fan bearing has failed, 48-hour repair estimated.",
            "output": (
                "**Critical Failure Communication — BF Fan:**\n\n"
                "**Immediate (within 5 minutes):**\n"
                "1. Call shift supervisor directly — give equipment ID, fault code, and 'unplanned shutdown'\n"
                "2. Control room to notify production planning and plant manager\n"
                "3. Maintenance manager to confirm repair scope and time estimate\n\n"
                "**Formal notification (within 30 minutes) — structured message:**\n"
                "- Equipment: BF Fan [ID] | Fault: BF-BRG-002 (Bearing Overheating)\n"
                "- Status: Unplanned shutdown, LOTO applied\n"
                "- Estimated repair time: 48 hours\n"
                "- Parts status: [in stock / ordered, ETA]\n"
                "- Production impact: [affected areas/products]\n"
                "- Next update: [specific time, e.g. 'in 4 hours or when parts confirmed']\n\n"
                "**What NOT to do:** Do not give vague estimates ('we'll see how it goes'). "
                "Operations needs a specific time window to make production decisions."
            ),
        },
        {
            "instruction": "How do you ensure a safe handover between maintenance shifts on an ongoing repair?",
            "input": "Repair in progress: pump mechanical seal replacement, 50% complete. Shift change in 30 minutes.",
            "output": (
                "**Shift Handover — Ongoing Maintenance:**\n\n"
                "**Before the outgoing technician leaves:**\n"
                "1. Write handover note in the work order — include: work completed so far, current status, what's remaining\n"
                "2. Physically walk the incoming technician through the job site\n"
                "3. Confirm LOTO status together — show each lock and energy isolation point\n"
                "4. Confirm parts status: what has been used, what is still needed\n"
                "5. Flag any safety concerns or abnormal conditions found during the job\n"
                "6. State what the next step is and any specific sequence to follow\n\n"
                "**The incoming technician must:**\n"
                "1. Apply their own personal LOTO lock before outgoing technician removes theirs\n"
                "2. Physically verify zero-energy state independently — never take the outgoing tech's word alone\n"
                "3. Sign the work order to accept the handover\n\n"
                "**Key rule:** Two technicians are simultaneously locked out during handover — never a gap with zero locks applied."
            ),
        },
        {
            "instruction": "Explain what a P-F interval is and how it is used to optimise condition monitoring frequency.",
            "input": "",
            "output": (
                "**P-F Interval (Potential Failure to Functional Failure):**\n\n"
                "The P-F interval is the time between when a failure can first be DETECTED (potential failure point P) "
                "and when the equipment stops performing its required function (functional failure point F).\n\n"
                "**Why it matters:**\n"
                "Your condition monitoring interval must be shorter than the P-F interval to catch the failure in time to act.\n\n"
                "**Rule of thumb:** Monitoring interval ≤ P-F interval / 2\n\n"
                "**Examples:**\n"
                "- Bearing inner race spalling: P-F interval ~4–8 weeks (vibration detects it early) → weekly monitoring adequate\n"
                "- Spray nozzle blockage: P-F interval ~days → daily visual inspection needed\n"
                "- Catastrophic coupling failure: P-F interval can be hours → continuous online monitoring required\n\n"
                "**Practical application:**\n"
                "1. For each critical failure mode, estimate the P-F interval from industry data + site experience\n"
                "2. Set monitoring frequency at half the P-F interval\n"
                "3. If P-F interval < 1 week, consider continuous online monitoring rather than periodic inspection\n\n"
                "**Reference:** P-F concept is a core element of MSG-3 (aviation RCM) and is equally applicable to steel plant rotating equipment."
            ),
        },
        {
            "instruction": "What are the most common causes of premature bearing failure in centrifugal pumps, and how to prevent each?",
            "input": "",
            "output": (
                "**Premature Bearing Failure — Centrifugal Pumps:**\n\n"
                "**1. Lubrication failure (40–50% of bearing failures)**\n"
                "- Causes: wrong grease type, over/under-greasing, contaminated lubricant, overlong change interval\n"
                "- Prevention: follow OEM grease spec; use automatic lubricators on critical pumps; oil analysis every PM cycle\n\n"
                "**2. Contamination (20–25%)**\n"
                "- Causes: ingress of water, particles, or process fluid through worn seals\n"
                "- Prevention: maintain seal integrity; check labyrinth seal/bearing isolators; keep oil cleanliness ≤ISO Class 16/14/11\n\n"
                "**3. Misalignment (10–15%)**\n"
                "- Causes: thermal growth not accounted for, improper alignment after maintenance, soft foot\n"
                "- Prevention: laser align within ±0.05mm at operating temperature; check soft foot before final alignment\n\n"
                "**4. Overload (10%)**\n"
                "- Causes: running far from BEP (best efficiency point), hydraulic thrust not balanced\n"
                "- Prevention: operate within 70–120% BEP; verify axial thrust balance design; check wear ring clearances\n\n"
                "**5. Installation damage (5–10%)**\n"
                "- Causes: incorrect installation (hammering, wrong fit), false brinelling during transport\n"
                "- Prevention: always use bearing installation tools; never hammer bearings; protect during transport with appropriate lubricant"
            ),
        },
        {
            "instruction": "What does 'lubrication starvation' mean for a conveyor bearing, and how is it detected?",
            "input": "Fault code: RC-LUB-002. Equipment: roller conveyor bearing.",
            "output": (
                "**Lubrication Starvation — RC-LUB-002:**\n\n"
                "**Definition:** Lubrication starvation occurs when insufficient lubricant film exists between "
                "rolling elements and races to prevent metal-to-metal contact. This accelerates surface fatigue "
                "and wear dramatically.\n\n"
                "**Physical mechanism:**\n"
                "1. Lubricant supply interrupted (seal failure, grease blocked, wrong grade)\n"
                "2. Existing lubricant film breaks down → rolling elements contact race directly\n"
                "3. Adhesive wear begins — metal transferred between surfaces\n"
                "4. Heat generation increases → thermal runaway → bearing seizure\n\n"
                "**Detection methods:**\n"
                "- **Ultrasound:** Most sensitive — dBuV reading spikes before temperature change occurs\n"
                "- **Temperature:** Bearing housing temperature rise above baseline (>10°C unexplained rise)\n"
                "- **Vibration:** High-frequency broad-band noise increase (not defect-frequency specific initially)\n"
                "- **Visual:** Discoloured (blue/brown) grease at seal, abnormal smell from housing\n\n"
                "**Response:**\n"
                "1. Re-lubricate immediately if safe to do so (correct grease, correct quantity)\n"
                "2. If temperature > warning threshold, shut down and inspect\n"
                "3. Check lubrication system integrity: seal, grease nipple, auto-lubricator supply"
            ),
        },
        {
            "instruction": "Describe the process for commissioning a repaired blast furnace fan back into service after a bearing replacement.",
            "input": "Repair completed: SKF-6310-2RS1 bearing replaced. LOTO still applied.",
            "output": (
                "**Return-to-Service Commissioning — BF Fan after Bearing Replacement:**\n\n"
                "**Pre-start checks (LOTO still applied):**\n"
                "1. Verify bearing correctly installed — correct part number, correct fit (interference on shaft, clearance in housing)\n"
                "2. Bearing housing cover secured — all bolts at correct torque per SOP\n"
                "3. Oil/grease filled to correct level with correct grade\n"
                "4. All guards reinstated and fastened\n"
                "5. Coupling halves realigned — verify within ±0.05mm tolerance; document alignment readings\n"
                "6. Vibration analyser connected for baseline reading during first run\n\n"
                "**LOTO removal:**\n"
                "7. Each technician removes their own lock; final check: all personnel clear of rotating parts\n"
                "8. Notify control room: 'BF Fan [ID] ready for commissioning start'\n\n"
                "**Commissioning run:**\n"
                "9. Start with no-load run (if possible) for 15 minutes\n"
                "10. Take vibration reading at 5 min, 10 min, 15 min — confirm ≤4.5 mm/s RMS\n"
                "11. Monitor bearing temperature — should stabilise within 30 min; target <85°C\n"
                "12. Take oil sample at 2-hour mark for baseline contamination level\n\n"
                "**Sign-off:**\n"
                "13. Record: alignment readings, vibration baseline, bearing temperature, oil sample reference\n"
                "14. Update CMMS: close work order, log new baseline, set next PM date\n"
                "15. Notify control room: 'BF Fan [ID] commissioned — normal operation resumed'"
            ),
        },
        {
            "instruction": "What is the 'false brinelling' failure mode and how does it differ from true brinelling?",
            "input": "Context: roller conveyor bearing standing idle during plant shutdown.",
            "output": (
                "**False Brinelling vs True Brinelling:**\n\n"
                "**True Brinelling:**\n"
                "Plastic deformation of bearing race from a single high-impact load (e.g. shock load during installation). "
                "Creates visible indentations matching the rolling element pitch pattern. "
                "Irreversible — bearing must be replaced.\n\n"
                "**False Brinelling:**\n"
                "Surface fretting (micro-wear) damage that LOOKS like brinelling but is caused by small oscillatory "
                "motion (vibration) while the bearing is stationary or slowly rotating. Common in:\n"
                "- Equipment idle during plant shutdown\n"
                "- Transport of heavy equipment on rough roads\n"
                "- Equipment on vibrating foundations (near large motors or compressors)\n\n"
                "**Mechanism:** Tiny oscillations between rolling elements and races damage the oxide protective film. "
                "Metal-to-metal contact creates wear debris → elliptical wear marks at rolling element pitch.\n\n"
                "**How to distinguish:**\n"
                "- True brinelling: sharp-edged, hemisphere-shaped pits matching ball diameter\n"
                "- False brinelling: reddish-brown debris (iron oxide), polished or worn groove at rolling element spacing\n\n"
                "**Prevention for idle equipment:**\n"
                "- Slow rotation during shutdowns (turn shaft weekly using motor or manual barring)\n"
                "- Anti-fretting grease (e.g. Molykote BR-2 Plus) in bearings subject to shutdown periods\n"
                "- Vibration isolation pads under idle equipment near vibration sources"
            ),
        },
    ]
    return [{"instruction": s["instruction"], "input": s["input"], "output": s["output"]} for s in scenarios]


# ============================================================================
# GENERATOR 13 — Paraphrase variants of FMEA failure modes (short Q&A)
# Quick single-question format for variety
# ============================================================================

def gen_short_qa(ontology: dict) -> list[dict]:
    examples = []
    families = ontology.get("asset_families", {})

    question_templates = [
        ("What are the symptoms of {fm} on a {fam}?", "symptoms"),
        ("What is the MTBF of {fm} on a {fam} and what does it imply for maintenance planning?", "mtbf"),
        ("What corrective actions should be taken for {fm} ({fc}) on a {fam}?", "corrective"),
        ("What sensor pattern indicates {fm} on a {fam}?", "sensor"),
    ]

    for fam_name, fam in families.items():
        fam_label = fam_name.replace("_", " ").title()
        for ss in fam.get("subsystems", []):
            for fm in ss.get("failure_modes", []):
                fm_name = fm.get("name", "Unknown")
                fm_id = fm.get("fault_code", "?")
                severity = fm.get("severity", "medium")
                mtbf = fm.get("mtbf_days", 365)
                symptoms = fm.get("symptoms", [])
                corrective = fm.get("corrective_actions", [])
                sensor_sig = fm.get("sensor_signature", {})
                parts = fm.get("requires_parts", [])

                for q_template, q_type in question_templates:
                    q = q_template.format(fm=fm_name, fam=fam_label, fc=fm_id)
                    if q_type == "symptoms":
                        if not symptoms:
                            continue
                        answer = (
                            f"**Symptoms of {fm_name} ({fm_id}) on {fam_label}:**\n"
                            + bulleted(symptoms)
                            + f"\n\nSeverity: {sev_word(severity)}. "
                            f"If two or more symptoms are present simultaneously, treat as a confirmed fault and initiate maintenance response."
                        )
                    elif q_type == "mtbf":
                        answer = (
                            f"**MTBF for {fm_name} on {fam_label}: ~{mtbf} days**\n\n"
                            f"**Implication for maintenance planning:**\n"
                            f"- Set PM interval at {int(mtbf * 0.6)} days (60% of MTBF)\n"
                            f"- With {mtbf}-day MTBF, expect {round(365/mtbf, 1)} failure events per year per asset in the fleet\n"
                            f"- Pre-position replacement parts with sufficient lead time before each PM interval\n"
                            f"- If actual failures are occurring more frequently, revise MTBF down and shorten PM interval"
                        )
                    elif q_type == "corrective":
                        if not corrective:
                            continue
                        answer = (
                            f"**Corrective Actions — {fm_name} ({fm_id}) on {fam_label}:**\n"
                            + numbered(corrective)
                            + f"\n\n**Parts needed:** {', '.join(parts) if parts else 'See spare parts catalogue for this asset family.'}\n"
                            f"**Estimated time:** See applicable SOP for labour-hour estimate. "
                            f"Prepare work order before starting."
                        )
                    elif q_type == "sensor":
                        if not sensor_sig:
                            continue
                        answer = (
                            f"**Sensor Signature — {fm_name} ({fm_id}) on {fam_label}:**\n"
                            + bulleted([f"{sensor}: **{trend}**" for sensor, trend in sensor_sig.items()])
                            + f"\n\nThis pattern, when confirmed across ≥2 sensor channels, is diagnostic for {fm_name.lower()}. "
                            f"Severity: {sev_word(severity)}. Initiate maintenance response as per {fm_id} protocol."
                        )
                    else:
                        continue
                    examples.append({"instruction": q, "input": "", "output": answer})

    return examples


# ============================================================================
# GENERATOR 14 — Cross-family comparative Q&A
# Compares failure modes / strategies across asset families
# ============================================================================

def gen_cross_family_qa(ontology: dict) -> list[dict]:
    examples = []
    families = ontology.get("asset_families", {})
    fam_list = list(families.items())

    all_fms = []
    for fam_name, fam in fam_list:
        fam_label = fam_name.replace("_", " ").title()
        for ss in fam.get("subsystems", []):
            for fm in ss.get("failure_modes", []):
                all_fms.append({
                    "fam_label": fam_label,
                    "fam_name": fam_name,
                    "fm_name": fm.get("name", ""),
                    "fm_id": fm.get("fault_code", "?"),
                    "severity": fm.get("severity", "medium"),
                    "mtbf": fm.get("mtbf_days", 365),
                    "symptoms": fm.get("symptoms", []),
                    "corrective": fm.get("corrective_actions", []),
                })

    # Q1 — Compare bearing failures across families
    bearing_fms = [f for f in all_fms if "bearing" in f["fm_name"].lower() or "brg" in f["fm_id"].lower()]
    if len(bearing_fms) >= 2:
        examples.append({
            "instruction": "Compare bearing failure modes across different equipment families in this steel plant. How do the failure modes, MTBF, and response strategies differ?",
            "input": "Equipment families in scope: " + ", ".join(set(f["fam_label"] for f in bearing_fms)),
            "output": (
                "**Bearing Failure Mode Comparison Across Equipment Families:**\n\n"
                + "\n\n".join(
                    f"**{f['fam_label']} — {f['fm_name']} ({f['fm_id']}):**\n"
                    f"- Severity: {sev_word(f['severity'])} | MTBF: {f['mtbf']} days\n"
                    f"- Corrective: {f['corrective'][0] if f['corrective'] else 'Inspect and replace'}"
                    for f in bearing_fms
                )
                + "\n\n**Key differences:**\n"
                "- BF fan bearings (high-speed, high-load) tend to have shorter MTBF and higher severity than conveyor bearings\n"
                "- Pump bearings are sensitive to shaft alignment and NPSH conditions\n"
                "- Conveyor bearings are susceptible to false brinelling during shutdowns\n\n"
                "**Common strategy:** Vibration-based PdM is effective for all — detect BPFI/BPFO/BSF before failure."
            ),
        })

    # Q2 — Which asset family has highest failure risk?
    if all_fms:
        crit_fms = [f for f in all_fms if f["severity"] == "critical"]
        examples.append({
            "instruction": "Which equipment failure modes in this steel plant carry CRITICAL severity, and which assets should receive the highest maintenance priority?",
            "input": "Scope: all asset families in the plant.",
            "output": (
                "**CRITICAL Severity Failure Modes — Priority List:**\n\n"
                + numbered([
                    f"{f['fm_name']} ({f['fm_id']}) on {f['fam_label']} — MTBF {f['mtbf']} days"
                    for f in crit_fms
                ])
                + "\n\n**Maintenance priority ranking:**\n"
                "Prioritise by: Severity × (1/MTBF) — highest criticality × highest frequency = highest maintenance investment.\n\n"
                "**Recommended strategy for all CRITICAL items:**\n"
                "1. Online continuous monitoring (vibration + temperature)\n"
                "2. Critical spare parts on-hand at all times (zero stock tolerance)\n"
                "3. PM interval at 50% MTBF — no deferrals without maintenance manager sign-off\n"
                "4. Annual FMEA review to update severity scores with actual failure data"
            ),
        })

    # Q3 — Compare lubrication requirements
    lube_fms = [f for f in all_fms if "lubric" in f["fm_name"].lower() or "lube" in f["fm_id"].lower()]
    if lube_fms:
        examples.append({
            "instruction": "Summarise lubrication-related failure modes across this plant's equipment families. What are the common root causes and unified prevention strategy?",
            "input": "",
            "output": (
                "**Lubrication-Related Failures — Plant Summary:**\n\n"
                + bulleted([
                    f"{f['fm_name']} ({f['fm_id']}) — {f['fam_label']} | MTBF {f['mtbf']}d | {sev_word(f['severity'])}"
                    for f in lube_fms
                ])
                + "\n\n**Common root causes across all families:**\n"
                "- Wrong lubricant specification (viscosity, grade)\n"
                "- Over-greasing or under-greasing\n"
                "- Extended change intervals beyond design\n"
                "- Contamination ingress (water, particles, process fluid)\n\n"
                "**Unified prevention strategy:**\n"
                "1. Establish plant-wide lubricant standards table (equipment → OEM spec → approved alternatives)\n"
                "2. Implement oil analysis programme — sample at every PM for critical equipment\n"
                "3. Use ultrasound to verify grease quantity on re-greasing (avoids over/under-lubrication)\n"
                "4. Maintain lubricant cleanliness: store in sealed containers, filter on dispensing\n"
                "5. Add oil/grease change tasks to predictive triggers (particle count or viscosity deviation), not just time"
            ),
        })

    # Q4 — compare MTBF across all failure modes
    examples.append({
        "instruction": "List all failure modes in this plant sorted by MTBF (shortest first). Which failure modes require the most frequent attention?",
        "input": "Scope: all 5 asset families.",
        "output": (
            "**Failure Modes by MTBF — Shortest to Longest (most frequent first):**\n\n"
            + "\n".join(
                f"{i+1}. {f['fm_name']} ({f['fm_id']}) on {f['fam_label']} — MTBF {f['mtbf']} days"
                for i, f in enumerate(sorted(all_fms, key=lambda x: x["mtbf"]))
            )
            + "\n\n**Highest-frequency failures require:**\n"
            "- Shortest PM intervals\n"
            "- Largest spare parts buffer stock\n"
            "- Most frequent condition monitoring checks\n\n"
            "**Long MTBF failures:** Can use lower-frequency PM intervals, but condition monitoring "
            "is still recommended to catch wear-out before catastrophic failure."
        ),
    })

    # Q5 — fleet-wide spare parts strategy
    examples.append({
        "instruction": "Design a fleet-wide spare parts holding strategy for this steel plant that balances inventory cost against unplanned downtime risk.",
        "input": "Asset families: Blast Furnace Fan, Centrifugal Pump, Roller Conveyor Bearing, Hydraulic Power Unit, Hot Strip Mill Conveyor.",
        "output": (
            "**Fleet-Wide Spare Parts Strategy:**\n\n"
            "**Tier 1 — Critical (zero stock = zero tolerance):**\n"
            "Parts for CRITICAL severity failure modes with lead time > 7 days. Always hold ≥2 units on-site.\n"
            "Examples: SKF 6310-2RS1 bearing (BF fan), main mechanical seals (critical pumps), HPU relief valve assembly.\n\n"
            "**Tier 2 — High (hold safety stock):**\n"
            "Parts for HIGH severity failures. Stock = lead_time × consumption_rate × 2.0 safety factor.\n"
            "Examples: standard pump bearings, impeller wear rings, conveyor coupling elements.\n\n"
            "**Tier 3 — Medium (reorder point):**\n"
            "Parts for MEDIUM severity failures. Hold minimum stock = 1 PM cycle consumption.\n"
            "Examples: spray nozzle sets, small bearings, O-ring kits, filter elements.\n\n"
            "**Tier 4 — Low / consumables (economic order quantity):**\n"
            "Non-critical, short lead time parts. Order in bulk quarterly.\n"
            "Examples: gaskets, fasteners, standard V-belts, filter consumables.\n\n"
            "**Annual review:** Reconcile actual consumption vs holding levels. "
            "Liquidate excess Tier 3/4 stock; reinforce Tier 1/2 holdings if MTBF data shows increasing failure rate."
        ),
    })

    return examples


# ============================================================================
# GENERATOR 15 — Extended RUL scenarios (more numerical context variety)
# ============================================================================

def gen_rul_extended(ontology: dict) -> list[dict]:
    examples = []
    families = ontology.get("asset_families", {})

    for fam_name, fam in families.items():
        fam_label = fam_name.replace("_", " ").title()
        sensor_ranges = fam.get("sensor_ranges", {})

        for ss in fam.get("subsystems", []):
            for fm in ss.get("failure_modes", []):
                fm_name = fm.get("name", "Unknown")
                fm_id = fm.get("fault_code", "?")
                severity = fm.get("severity", "medium")
                mtbf = fm.get("mtbf_days", 365)
                if not isinstance(mtbf, (int, float)):
                    mtbf = 365

                # Sensor-informed RUL with actual readings
                if sensor_ranges:
                    sensor_name = list(sensor_ranges.keys())[0]
                    sr = sensor_ranges[sensor_name]
                    nm = sr.get("normal_max", 100)
                    wm = sr.get("warning_max", nm * 1.2)
                    cm = sr.get("critical_max", nm * 1.5)
                    desc = sr.get("description", sensor_name)

                    # Reading at 80% of warning-to-critical gap
                    reading = round(nm + (wm - nm) * 0.8, 1)
                    examples.append({
                        "instruction": (
                            f"Given the current sensor reading, estimate the RUL for this {fam_label} "
                            f"and state whether it is safe to continue operating until the next scheduled PM."
                        ),
                        "input": (
                            f"Equipment: {fam_label} | Failure mode: {fm_name} ({fm_id})\n"
                            f"Sensor: {desc} — Current: {reading} | Normal max: {nm} | Warning: {wm} | Critical: {cm}\n"
                            f"MTBF: {mtbf} days | Days since last maintenance: {int(mtbf * 0.55)}\n"
                            f"Next scheduled PM: {int(mtbf * 0.40 - mtbf * 0.55)} days away"
                        ),
                        "output": (
                            f"**RUL Estimate — {fam_label} / {fm_name}:**\n\n"
                            f"**Current sensor status:** {desc} = {reading} → **WARNING** (above normal max {nm}, approaching warning threshold {wm})\n\n"
                            f"**Life consumed:** ~55% of MTBF ({int(mtbf*0.55)}/{mtbf} days)\n"
                            f"**Estimated RUL:** ~{int(mtbf * 0.45)} days based on MTBF model\n\n"
                            f"**Safe to continue?** "
                            + (
                                f"YES — with conditions. The sensor reading is in warning zone, not critical.\n\n"
                                f"**Conditions for continued operation:**\n"
                                f"1. Increase {desc} monitoring to every 4 hours\n"
                                f"2. Set alert: if {desc} exceeds {wm}, initiate controlled shutdown\n"
                                f"3. Pre-stage replacement parts now\n"
                                f"4. Move PM date forward by 20% — do not wait for scheduled date\n\n"
                                f"**Escalation trigger:** If {desc} reaches {cm} (critical), "
                                f"emergency shutdown per applicable SOP — do not defer."
                                if reading < wm
                                else
                                f"**BORDERLINE** — reading is near warning threshold. Recommend controlled shutdown "
                                f"at next available window (within 24–48 hours)."
                            )
                        ),
                    })

                    # Trending analysis
                    examples.append({
                        "instruction": (
                            f"The {desc} on a {fam_label} has been increasing at {round((wm - nm) / 30, 2)} units/day. "
                            f"At what date will it reach the critical threshold, and when should maintenance be scheduled?"
                        ),
                        "input": (
                            f"Equipment: {fam_label} | Sensor: {desc}\n"
                            f"Current reading: {nm + 5:.1f} | Critical threshold: {cm}\n"
                            f"Trend rate: +{round((wm - nm) / 30, 2)} units/day"
                        ),
                        "output": (
                            f"**Trend Analysis — {fam_label} / {desc}:**\n\n"
                            f"**Current:** {nm + 5:.1f} | **Critical at:** {cm}\n"
                            f"**Gap to critical:** {cm - (nm + 5):.1f} units\n"
                            f"**Rate:** +{round((wm - nm) / 30, 2)} units/day\n"
                            f"**Days to critical:** ~{int((cm - (nm + 5)) / ((wm - nm) / 30))} days\n"
                            f"**Days to warning:** ~{int((wm - (nm + 5)) / ((wm - nm) / 30))} days\n\n"
                            f"**Maintenance scheduling recommendation:**\n"
                            f"Schedule maintenance {int((wm - (nm + 5)) / ((wm - nm) / 30) * 0.7):.0f} days from now "
                            f"— this gives a buffer before warning is breached.\n\n"
                            f"**Parts to pre-order:** {fm_name.lower()}-related components. Place order now to allow for lead time."
                        ),
                    })

    return examples


# ============================================================================
# GENERATOR 16 — Work Order Q&A (from all doc types, creating work-order context)
# ============================================================================

def gen_workorder_qa(docs: list[dict], fmea_nodes: dict) -> list[dict]:
    examples = []
    sop_refs = {s.get("sop_number", ""): s for s in fmea_nodes.get("SOPReference", [])}

    # Work order templates for each failure mode + asset combo
    all_docs_fm = [
        d for d in docs
        if d.get("fault_codes_referenced") and d.get("failure_modes_referenced")
        and len(d.get("content_markdown", "")) > 200
    ]

    for doc in all_docs_fm[:60]:
        asset_id = doc.get("asset_id", "unknown")
        fam = doc.get("asset_family", "").replace("_", " ")
        fm = doc.get("failure_modes_referenced", ["fault"])[0]
        fc = doc.get("fault_codes_referenced", ["N/A"])[0]
        doc_type = doc.get("doc_type", "")

        # V1 — create a work order
        if doc_type in ("failure_analysis", "maintenance_record"):
            examples.append({
                "instruction": (
                    "Draft a CMMS work order for this maintenance task. Include all required fields for reliable data capture."
                ),
                "input": f"Equipment: {asset_id} ({fam}) | Fault: {fm} ({fc}) | Type: {'Emergency corrective' if 'critical' in doc.get('content_markdown','').lower()[:300] else 'Corrective'}",
                "output": (
                    f"**CMMS Work Order — {asset_id}:**\n\n"
                    f"| Field | Value |\n"
                    f"|---|---|\n"
                    f"| Work Order Type | Corrective Maintenance |\n"
                    f"| Equipment ID | {asset_id} |\n"
                    f"| Equipment Class | {fam} |\n"
                    f"| Fault Code | {fc} |\n"
                    f"| Failure Mode (ISO 14224) | {fm} |\n"
                    f"| Detection Method | Control room alarm / sensor threshold exceeded |\n"
                    f"| Priority | {'URGENT' if 'critical' in doc.get('content_markdown','').lower()[:300] else 'HIGH'} |\n"
                    f"| LOTO Required | YES |\n"
                    f"| Applicable SOP | [Look up {fc} in SOP library] |\n"
                    f"| Estimated Duration | [Per SOP] |\n"
                    f"| Required Trade | Mechanical fitter |\n"
                    f"| Parts Required | [From spare parts catalogue — {fc}] |\n\n"
                    f"**Fields to complete after repair:**\n"
                    f"- Actual start time / end time\n"
                    f"- Parts consumed (part numbers + quantities)\n"
                    f"- Labour hours by trade\n"
                    f"- Root cause determination\n"
                    f"- Recommendations (PM interval change? New monitoring?)\n"
                    f"- Sign-off by technician + supervisor"
                ),
            })

        # V2 — post-job close-out
        if doc_type == "maintenance_record":
            examples.append({
                "instruction": "Write the work order close-out summary for this maintenance job.",
                "input": f"Completed job: {fm} ({fc}) on {asset_id} ({fam}). Repair successful — equipment returned to service.",
                "output": (
                    f"**Work Order Close-Out — {asset_id} / {fc}:**\n\n"
                    f"**Job Summary:** Fault code {fc} ({fm}) on {asset_id} ({fam}) successfully repaired.\n\n"
                    f"**Work completed:**\n"
                    f"- Equipment isolated (LOTO applied, PTW active)\n"
                    f"- Fault confirmed: {fm.lower()} identified on inspection\n"
                    f"- Corrective action executed per applicable SOP\n"
                    f"- Post-repair functional test passed\n"
                    f"- Equipment returned to service; control room notified\n\n"
                    f"**Documentation actions:**\n"
                    f"- Record actual hours and parts consumed\n"
                    f"- Update equipment failure history in CMMS\n"
                    f"- Replenish consumed spare parts — raise stores requisition\n"
                    f"- Close PTW and LOTO register\n"
                    f"- Supervisor sign-off required before archiving\n\n"
                    f"**Reliability actions:**\n"
                    f"- Calculate updated MTBF for {fm} on {fam} fleet\n"
                    f"- Review PM interval — adjust if this failure was earlier than expected"
                ),
            })

        # V3 — escalation decision
        if doc_type == "failure_analysis":
            examples.append({
                "instruction": "This fault code has been active for 2 hours with no response team assigned. Determine the escalation path.",
                "input": f"Fault: {fm} ({fc}) on {asset_id} ({fam}) | Severity: {'CRITICAL' if 'critical' in doc.get('content_markdown','').lower()[:200] else 'HIGH'} | Time since alarm: 2 hours",
                "output": (
                    f"**Escalation Required — {asset_id} / {fc} (2 hours elapsed):**\n\n"
                    f"**Current status:** Fault active, no team assigned — this is a response failure.\n\n"
                    f"**Immediate escalation path (execute NOW):**\n"
                    f"1. Shift supervisor → directly assign available technicians from current shift\n"
                    f"2. If no current-shift technicians available → call maintenance on-call technician\n"
                    f"3. If on-call not reachable within 15 minutes → escalate to maintenance manager\n"
                    f"4. Maintenance manager to confirm response team and ETA to control room\n\n"
                    f"**Parallel actions:**\n"
                    f"- Production manager to be notified of 2-hour response delay\n"
                    f"- Confirm equipment status: is it still running degraded or already shut down?\n"
                    f"- If still running: assess risk of continued operation; consider controlled shutdown\n\n"
                    f"**Root cause of response failure:** Investigate after incident. "
                    f"Common causes: on-call roster gap, unclear escalation path, missed alarm notification. Fix in CMMS escalation settings."
                ),
            })

    return examples


# ============================================================================
# DEDUP + SHUFFLE + OUTPUT
# ============================================================================

def deduplicate(examples: list[dict]) -> list[dict]:
    """
    True dedup: only drop examples where ALL THREE fields are near-identical.
    We use (instruction[:120], input[:200], output[:120]) as the key.
    This is permissive enough to keep variations that differ by equipment ID,
    fault code, or sensor reading — while still dropping genuine duplicates.
    """
    seen: set = set()
    out = []
    for ex in examples:
        key = (
            ex["instruction"][:120]
            + "||"
            + ex["input"][:200]
            + "||"
            + ex["output"][:120]
        )
        if key not in seen:
            seen.add(key)
            out.append(ex)
    return out


def main():
    print("Loading source data...")
    docs = load_synthetic_docs(SYNTHETIC_DOCS_DIR)
    fmea_nodes = load_fmea(FMEA_PATH)
    ontology = load_ontology(ONTOLOGY_PATH)
    print(f"  {len(docs)} synthetic docs | {sum(len(v) for v in fmea_nodes.values())} FMEA nodes | "
          f"{len(ontology.get('asset_families', {}))} asset families")

    print("\nGenerating examples...")

    all_examples = []

    generators = [
        ("Gen01 fault_diagnosis",     lambda: gen_fault_diagnosis(docs)),
        ("Gen02 rca_explanation",     lambda: gen_rca_explanation(ontology)),
        ("Gen03 rul_interpretation",  lambda: gen_rul_interpretation(ontology)),
        ("Gen04 sop_recommendations", lambda: gen_sop_recommendations(docs, fmea_nodes)),
        ("Gen05 spare_parts",         lambda: gen_spare_parts(ontology, fmea_nodes)),
        ("Gen06 fmea_multistep",      lambda: gen_fmea_multistep(fmea_nodes)),
        ("Gen07 maintenance_records", lambda: gen_maintenance_records(docs)),
        ("Gen08 general_knowledge",   lambda: gen_general_knowledge()),
        ("Gen09 incident_summaries",  lambda: gen_incident_summaries(docs)),
        ("Gen10 sensor_thresholds",   lambda: gen_sensor_thresholds(ontology)),
        ("Gen11 manual_qa",           lambda: gen_manual_qa(docs)),
        ("Gen12 multi_scenario",      lambda: gen_multi_scenario()),
        ("Gen13 short_qa",            lambda: gen_short_qa(ontology)),
        ("Gen14 cross_family_qa",     lambda: gen_cross_family_qa(ontology)),
        ("Gen15 rul_extended",        lambda: gen_rul_extended(ontology)),
        ("Gen16 workorder_qa",        lambda: gen_workorder_qa(docs, fmea_nodes)),
        ("Gen17 doc_qa_direct",       lambda: gen_doc_qa_direct(docs)),
        ("Gen18 spare_parts_docs",    lambda: gen_spare_parts_docs(docs)),
    ]

    for name, gen_fn in generators:
        batch = gen_fn()
        print(f"  {name}: {len(batch)}")
        all_examples.extend(batch)

    print(f"\nTotal before dedup: {len(all_examples)}")
    all_examples = deduplicate(all_examples)
    print(f"Total after dedup:  {len(all_examples)}")

    random.shuffle(all_examples)

    # Held-out eval set (first 50 after shuffle)
    n_eval = 50
    eval_examples = all_examples[:n_eval]
    train_examples = all_examples[n_eval:]

    OUTPUT_PATH.parent.mkdir(exist_ok=True)

    # Write full JSONL (train + eval together — notebook splits internally)
    with open(OUTPUT_PATH, "w") as f:
        for ex in all_examples:
            f.write(json.dumps(ex, ensure_ascii=False) + "\n")

    # Write separate eval JSONL
    eval_path = OUTPUT_PATH.parent / "maintenance_eval_50.jsonl"
    with open(eval_path, "w") as f:
        for ex in eval_examples:
            f.write(json.dumps(ex, ensure_ascii=False) + "\n")

    print(f"\nDataset written:  {OUTPUT_PATH}")
    print(f"Eval set written: {eval_path}")
    print(f"\nDataset stats:")
    print(f"  Total:  {len(all_examples)} examples")
    print(f"  Train:  {len(train_examples)} examples")
    print(f"  Eval:   {n_eval} examples (held-out)")

    sample = all_examples[0]
    print(f"\n--- Sample Row ---")
    print(f"instruction: {sample['instruction'][:180]}")
    print(f"input:       {sample['input'][:120]}")
    print(f"output:      {sample['output'][:200]}")
    print("------------------")

    # Category breakdown of final dataset
    print(f"\nGenerator breakdown (approx):")
    for name, gen_fn in generators:
        batch = gen_fn()
        label = name.split(" ", 1)[1]
        print(f"  {label}: ~{len(batch)} raw examples")


if __name__ == "__main__":
    main()
