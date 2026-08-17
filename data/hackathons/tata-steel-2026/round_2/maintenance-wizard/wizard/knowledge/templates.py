"""
wizard.knowledge.templates
===========================
Jinja2 skeleton templates for all 6 synthetic document types.

Templates use typed variable slots filled by Faker/Mimesis for deterministic
fields. Free-text narrative sections are left as `{{ narrative_FIELD }}` for
LLM elaboration (or template-fallback text for offline mode).

Template types:
    EQUIPMENT_MANUAL   - Equipment manual section
    MAINTENANCE_SOP    - Step-by-step SOP procedure
    MAINTENANCE_LOG    - Single maintenance log entry
    FAILURE_ANALYSIS   - Root cause failure analysis report
    INCIDENT_SUMMARY   - Breakdown/incident narrative
    SPARE_PARTS_RECORD - Spare parts catalog entry

Usage::

    from wizard.knowledge.templates import render_template, TemplateType

    text = render_template(TemplateType.MAINTENANCE_LOG, vars_dict)
"""

from __future__ import annotations

import enum
from typing import Any

from jinja2 import Environment, BaseLoader, StrictUndefined


class TemplateType(str, enum.Enum):
    EQUIPMENT_MANUAL = "equipment_manual"
    MAINTENANCE_SOP = "maintenance_sop"
    MAINTENANCE_LOG = "maintenance_log"
    FAILURE_ANALYSIS = "failure_analysis"
    INCIDENT_SUMMARY = "incident_summary"
    SPARE_PARTS_RECORD = "spare_parts_record"


# ---------------------------------------------------------------------------
# RAW JINJA2 TEMPLATE STRINGS — one per document type
# ---------------------------------------------------------------------------

_TEMPLATES: dict[str, str] = {

    "equipment_manual": """\
# Equipment Manual — {{ equipment_name }} ({{ equipment_id }})
**Document No.:** SOM-{{ equipment_class | upper }}-{{ "%04d" | format(doc_seq) }}
**Revision:** {{ revision }}
**Issue Date:** {{ issue_date }}
**Applicable Equipment Class:** {{ equipment_class }} — {{ iso14224_class }}
**Work Center:** {{ work_center }}

---

## 1. Description and Purpose

{{ equipment_name }} is a {{ equipment_class }} installed in the {{ plant_area }} at
{{ plant_name }}. It forms part of the {{ subsystem }} subsystem.

{{ narrative_description }}

**Design Parameters:**
| Parameter | Value | Unit |
|---|---|---|
{% for param, val in design_params.items() %}| {{ param }} | {{ val.value }} | {{ val.unit }} |
{% endfor %}

---

## 2. Operating Limits and Sensor Thresholds

| Sensor | Normal Range | Warning Threshold | Critical Threshold |
|---|---|---|---|
{% for sensor, limits in sensor_ranges.items() %}| {{ sensor }} | {{ limits.normal_min }} – {{ limits.normal_max }} | {{ limits.warning_max }} | {{ limits.critical_max }} |
{% endfor %}

**Note:** Critical threshold breach requires immediate notification to shift supervisor and
activation of SOP-{{ equipment_class | upper }}-EMRG-01.

---

## 3. Subsystems and Components

{{ narrative_subsystems }}

The following subsystems are covered under this manual:
{% for ss in subsystems %}
- **{{ ss.name }}:** {{ ss.description }}
{% endfor %}

---

## 4. Known Failure Modes (ISO 14224 RCM Taxonomy)

{% for fm in failure_modes %}
### FM {{ loop.index }}: {{ fm.name }} (Code: {{ fm.fault_code }})

**Severity:** {{ fm.severity | upper }}
**ISO 14224 Code:** {{ fm.iso14224_code }}
**Mean Time Between Failures:** {{ fm.mtbf_days }} days (design basis)

**Symptoms:**
{% for s in fm.symptoms %}
- {{ s }}
{% endfor %}

**Root Causes:**
{% for rc in fm.root_causes %}
- {{ rc }}
{% endfor %}

**Corrective Actions:**
{% for ca in fm.corrective_actions %}
{{ loop.index }}. {{ ca }}
{% endfor %}

**Required Spare Parts:** {{ fm.requires_parts | join(', ') }}

{% endfor %}

---

## 5. Maintenance Schedule

{{ narrative_maintenance_schedule }}

| Task | Frequency | Responsible Role | Reference SOP |
|---|---|---|---|
{% for task in maintenance_tasks %}| {{ task.task }} | {{ task.frequency }} | {{ task.role }} | {{ task.sop }} |
{% endfor %}

---

*Document prepared by {{ author_name }}, {{ author_role }}, {{ prepared_date }}*
*Approved by: {{ approver_name }}, {{ approver_role }}*
""",

    "maintenance_sop": """\
# Standard Operating Procedure — {{ sop_title }}
**SOP No.:** {{ sop_number }}
**Revision:** {{ revision }}
**Effective Date:** {{ effective_date }}
**Applicable Equipment:** {{ applicable_equipment }}
**Asset Family:** {{ equipment_class }}

---

## 1. Purpose and Scope

{{ narrative_purpose }}

This SOP applies to {{ applicable_equipment }} units in the {{ plant_area }} of {{ plant_name }}.

---

## 2. Prerequisites and Safety Requirements

**Personal Protective Equipment (PPE):**
{% for ppe in ppe_required %}
- {{ ppe }}
{% endfor %}

**Permits Required:**
- Work Permit No: WP-{{ plant_area | upper }}-{{ permit_seq }}
{% if requires_isolation %}- Equipment Isolation Certificate (LOTO per SOP-ELEC-LOTO-01){% endif %}
{% if hot_work %}- Hot Work Permit (if cutting/welding involved){% endif %}

**CRITICAL SAFETY WARNINGS:**
{% for warning in safety_warnings %}
⚠️ {{ warning }}
{% endfor %}

---

## 3. Tools and Materials Required

**Tools:**
{% for tool in tools_required %}
- {{ tool }}
{% endfor %}

**Consumables / Spare Parts:**
{% for part in parts_required %}
- {{ part }}
{% endfor %}

---

## 4. Step-by-Step Procedure

**Estimated Duration:** {{ estimated_duration_hours }} hours
**Minimum Crew:** {{ min_crew }} technicians

{% for step in procedure_steps %}
### Step {{ step.number }}: {{ step.title }}

{{ step.instruction }}

{% if step.caution %} ⚠️ **Caution:** {{ step.caution }}{% endif %}
{% if step.torque_spec %}**Torque Specification:** {{ step.torque_spec }}{% endif %}
{% if step.measurement %}**Measurement Required:** {{ step.measurement }}{% endif %}

{% endfor %}

---

## 5. Acceptance Criteria

After completing the procedure, verify:
{% for criterion in acceptance_criteria %}
- [ ] {{ criterion }}
{% endfor %}

---

## 6. Post-Work Verification

{{ narrative_post_work }}

Record the completed work order in the CMMS with:
- Work Order No.: WO-{{ work_order_prefix }}-{{ work_order_seq }}
- Technician IDs, actual duration, parts consumed, next due date.

---

*Author: {{ author_name }}, {{ author_role }} | Approved: {{ approver_name }} | Date: {{ effective_date }}*
""",

    "maintenance_log": """\
# Maintenance Log Entry
**Log ID:** ML-{{ log_id }}
**Work Order:** {{ work_order_id }}
**Date:** {{ performed_date }}
**Shift:** {{ shift }} | **Crew:** {{ crew_size }} technicians

---

**Equipment ID:** {{ equipment_id }}
**Equipment Name:** {{ equipment_name }}
**Plant Area:** {{ plant_area }}
**Maintenance Type:** {{ maintenance_type }}

---

## Work Description

{{ narrative_work_description }}

## Findings

{{ narrative_findings }}

**Fault Code(s) Identified:** {{ fault_codes | join(', ') }}
**Severity at Inspection:** {{ severity }}

## Actions Taken

{% for action in actions_taken %}
{{ loop.index }}. {{ action }}
{% endfor %}

## Parts Replaced / Consumed

| Part Number | Part Name | Quantity | Batch/Serial |
|---|---|---|---|
{% for part in parts_consumed %}| {{ part.part_number }} | {{ part.part_name }} | {{ part.qty }} | {{ part.batch }} |
{% endfor %}

{% if parts_consumed | length == 0 %}
*No parts replaced — inspection/service only.*
{% endif %}

## Measurements and Readings

| Parameter | Before | After | Acceptable Range |
|---|---|---|---|
{% for m in measurements %}| {{ m.parameter }} | {{ m.before }} | {{ m.after }} | {{ m.range }} |
{% endfor %}

## Outcome and Next Actions

**Outcome:** {{ outcome }}
**Equipment Returned to Service:** {{ returned_to_service }}

{{ narrative_outcome }}

{% if next_due_date %}**Next Scheduled Maintenance:** {{ next_due_date }}{% endif %}

---

*Logged by: {{ technician_name }} (ID: {{ technician_id }}) | Supervisor: {{ supervisor_name }}*
*Sign-off time: {{ signoff_time }}*
""",

    "failure_analysis": """\
# Failure Analysis Report — {{ equipment_name }}
**Report No.:** FAR-{{ report_seq }}
**Incident Date:** {{ incident_date }}
**Report Date:** {{ report_date }}
**Equipment ID:** {{ equipment_id }}
**Fault Code:** {{ fault_code }}
**Severity:** {{ severity | upper }}

---

## Executive Summary

{{ narrative_executive_summary }}

---

## 1. Incident Description

**Date/Time of Failure:** {{ incident_date }} {{ incident_time }}
**Operating Condition at Failure:** {{ operating_condition }}
**Production Impact:** {{ production_impact_hours }} hours downtime, approx. ₹{{ production_loss_inr }} loss.

{{ narrative_incident_description }}

---

## 2. Failure Timeline

| Time | Event | Sensor Reading | Action Taken |
|---|---|---|---|
{% for event in timeline %}| {{ event.time }} | {{ event.event }} | {{ event.sensor_reading }} | {{ event.action }} |
{% endfor %}

---

## 3. Root Cause Analysis

### 3.1 Physical Root Cause

{{ narrative_physical_root_cause }}

**Evidence:**
{% for ev in evidence %}
- {{ ev }}
{% endfor %}

### 3.2 Contributing Factors

{% for cf in contributing_factors %}
{{ loop.index }}. **{{ cf.factor }}**: {{ cf.explanation }}
{% endfor %}

### 3.3 Five-Whys Analysis

1. **Why did the equipment fail?** {{ why1 }}
2. **Why did that happen?** {{ why2 }}
3. **Why did that happen?** {{ why3 }}
4. **Why did that happen?** {{ why4 }}
5. **Why did that happen?** {{ why5 }}

**Root Cause Statement:** {{ root_cause_statement }}

---

## 4. Corrective Actions

| Action | Owner | Due Date | Status |
|---|---|---|---|
{% for ca in corrective_actions %}| {{ ca.action }} | {{ ca.owner }} | {{ ca.due_date }} | {{ ca.status }} |
{% endfor %}

---

## 5. Preventive Actions (to prevent recurrence)

{{ narrative_preventive_actions }}

{% for pa in preventive_actions %}
- {{ pa }}
{% endfor %}

---

## 6. Cost Summary

| Item | Amount (INR) |
|---|---|
| Parts cost | ₹{{ parts_cost_inr }} |
| Labour cost | ₹{{ labour_cost_inr }} |
| Production loss | ₹{{ production_loss_inr }} |
| **Total** | **₹{{ total_cost_inr }}** |

---

*Prepared by: {{ analyst_name }}, {{ analyst_role }}*
*Reviewed by: {{ reviewer_name }}, Maintenance Manager*
*Date: {{ report_date }}*
""",

    "incident_summary": """\
# Incident/Breakdown Summary
**Incident ID:** INC-{{ incident_id }}
**Date:** {{ incident_date }}
**Shift:** {{ shift }}
**Reported By:** {{ reporter_name }} ({{ reporter_role }})

---

**Equipment:** {{ equipment_name }} ({{ equipment_id }})
**Plant Area:** {{ plant_area }}
**Incident Type:** {{ incident_type }}
**Alert Level:** {{ alert_level }}

---

## Incident Description

{{ narrative_incident_description }}

**Initial Sensor Reading at Fault:**
- Temperature: {{ sensor_temp_c }}°C (threshold: {{ sensor_temp_threshold_c }}°C)
- Vibration: {{ sensor_vib_mm_s }} mm/s (threshold: {{ sensor_vib_threshold_mm_s }} mm/s)
- Pressure: {{ sensor_pres_bar }} bar (normal: {{ sensor_pres_normal_bar }} bar)

---

## Immediate Response Actions

{{ narrative_immediate_response }}

{% for action in immediate_actions %}
{{ loop.index }}. {{ action }}
{% endfor %}

---

## Production Impact

**Duration of Stoppage:** {{ stoppage_hours }} hours
**Production Units Affected:** {{ affected_units }}
**Estimated Production Loss:** ₹{{ production_loss_inr }}

---

## Preliminary Cause Assessment

{{ narrative_preliminary_cause }}

**Fault Code Logged:** {{ fault_code }}
**Assigned to Maintenance Team:** {{ assigned_team }}

---

## Status

**Current Status:** {{ current_status }}
**Expected Return to Service:** {{ eta_return }}

---

*Incident logged: {{ logged_at }} | System: CMMS-SAP PM Module*
""",

    "spare_parts_record": """\
# Spare Parts Catalog Entry
**Part Number:** {{ part_number }}
**Catalog ID:** SPC-{{ catalog_seq }}
**Last Updated:** {{ last_updated }}

---

## Part Details

| Field | Value |
|---|---|
| **Part Name** | {{ part_name }} |
| **Manufacturer** | {{ manufacturer }} |
| **Manufacturer Part No.** | {{ mfr_part_number }} |
| **Material** | {{ material }} |
| **Weight (kg)** | {{ weight_kg }} |
| **Compatible Equipment** | {{ compatible_equipment | join(', ') }} |
| **ISO 14224 Function Class** | {{ function_class }} |

---

## Procurement Information

| Field | Value |
|---|---|
| **Preferred Supplier** | {{ supplier }} |
| **Supplier Contact** | {{ supplier_contact }} |
| **Unit Cost (INR)** | ₹{{ unit_cost_inr }} |
| **Lead Time (days)** | {{ lead_time_days }} |
| **Criticality** | {{ criticality_override | upper }} |
| **Currency** | INR |
| **Payment Terms** | {{ payment_terms }} |

---

## Stock Information

| Field | Value |
|---|---|
| **Current Stock (units)** | {{ stock_qty }} |
| **Minimum Stock Level** | {{ min_stock_qty }} |
| **Storage Location** | {{ storage_location }} |
| **Storage Conditions** | {{ storage_conditions }} |
| **Shelf Life** | {{ shelf_life }} |

{% if stock_qty == 0 %}
⚠️ **STOCK ALERT: ZERO STOCK** — Lead time {{ lead_time_days }} days.
{% if lead_time_days >= 14 %}
🔴 **PROCUREMENT URGENT**: Long lead time. Raise Purchase Order immediately if failure imminent.
{% endif %}
{% elif stock_qty < min_stock_qty %}
⚠️ **STOCK ALERT: BELOW MINIMUM** — Current: {{ stock_qty }}, Minimum: {{ min_stock_qty }}.
{% endif %}

---

## Usage History

| Month | Qty Consumed | Work Orders |
|---|---|---|
{% for usage in usage_history %}| {{ usage.month }} | {{ usage.qty }} | {{ usage.work_orders }} |
{% endfor %}

---

## Installation Notes

{{ narrative_installation_notes }}

---

*Catalog maintained by: {{ catalog_manager }} | Approved: {{ approver_name }}*
"""
}

# ---------------------------------------------------------------------------
# Jinja2 Environment
# ---------------------------------------------------------------------------

_env = Environment(
    loader=BaseLoader(),
    undefined=StrictUndefined,
    trim_blocks=True,
    lstrip_blocks=True,
)


def render_template(template_type: TemplateType, variables: dict[str, Any]) -> str:
    """
    Render a Jinja2 skeleton template with the given variables.

    Parameters
    ----------
    template_type : TemplateType
        Which document type to render.
    variables : dict
        Variable dict. Keys must match template slots exactly.
        Missing required keys raise jinja2.UndefinedError.

    Returns
    -------
    str
        Rendered Markdown string.
    """
    raw = _TEMPLATES[template_type.value]
    template = _env.from_string(raw)
    return template.render(**variables)


def get_template_string(template_type: TemplateType) -> str:
    """Return the raw Jinja2 template string for a given type."""
    return _TEMPLATES[template_type.value]


__all__ = [
    "TemplateType",
    "render_template",
    "get_template_string",
]
