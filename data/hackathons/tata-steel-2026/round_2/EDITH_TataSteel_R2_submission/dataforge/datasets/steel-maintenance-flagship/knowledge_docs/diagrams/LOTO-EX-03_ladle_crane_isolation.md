---
doc_id: LOTO-EX-03
title: "LOTO Worked Example — Ladle-Crane Wire-Rope / Brake Isolation"
asset_ids: ["MS.LDC.CRN01"]
related_docs: ["LOTO-TEMPLATE", "SOP-10", "ELEC-03", "FTA-05", "PID-06"]
doc_type: loto_permit
---

# LOTO-EX-03 — Ladle Crane Wire-Rope Replacement / Brake Service (Worked Permit)
**Doc:** LOTO-EX-03 | Rev 1.0 | Site: TATA_JSR (Synthetic)
**Standard References:** OSHA 29 CFR 1910.147 + 1910.179; ISO 4309:2017; instantiates LOTO-TEMPLATE

> **DISCLAIMER — SYNTHETIC worked example. P1 LIFE-SAFETY ASSET.** Competent-Person sign-off is mandatory and legally required. No proprietary Tata Steel data.

---

## Permit Header

| Field | Entry |
|-------|-------|
| Permit No. | LOTO-EX-03 |
| Asset ID | MS.LDC.CRN01 |
| Equipment / location | MELT_SHOP / LADLE_BAY / CRANE_1_HOIST (Konecranes 320 t) |
| Work to be done | Wire-rope replacement (ROPE-CRN-01) + brake service (BRAKE-PAD-01) |
| Triggering SOP | **SOP-10** (crane wire-rope & brake) |
| Triggering scenario | SCN-047 (wire_rope_fatigue_broken_wire) — `ROPE-MFL-RETIRE` / `ROPE-DISCARD-ISO4309` (`ROPE.MFL` 300 mV) |
| Safety class | **P1 — rope/brake failure = ladle drop = mass-fatality risk** |

## 1. Energy Sources (checked)

| Energy type | Present | Isolation device | Stored-energy hazard |
|-------------|---------|------------------|----------------------|
| Electrical | ✔ | Cabin isolator + main feeder at sub-station — lock open | live runway feeder |
| **Gravity (suspended load)** | ✔ | **Lower hook block to ground on blocking — NEVER leave ladle/hook suspended** | falling load |
| Hydraulic (brake thruster) | ✔ | Isolate electro-hydraulic thruster supply | brake-thruster pressure |
| Mechanical (rope/drum tension) | ✔ | De-tension before dead-end removal | stored rope tension, spring brake |
| Travel (runway / bridge) | ✔ | Apply runway travel stop + wheel chocks | crane motion |

## 2. Isolation Steps

1. If a load is suspended, lower it to ground under control **before** any isolation. Park crane in maintenance bay; lower hook block onto blocking.
2. Isolate at cabin isolator and main feeder; lock + danger tag.
3. Isolate brake-thruster hydraulic supply.
4. Apply runway travel stop; chock bridge wheels if climbing structure.
5. Post "CRANE IN MAINTENANCE — NOT TO BE USED FOR LIFTING — COMPETENT PERSON INSPECTION" on all panels and the hook block.
6. De-tension rope before removing dead-end anchor.

## 3. Verification Record (worked)

| Check | Method | Reading |
|-------|--------|---------|
| Electrical dead | test-before-touch at hoist drive | 0 V |
| Hook block grounded | visual — on blocking | ✔ |
| Brake-thruster isolated | hydraulic gauge | 0 bar |
| Travel prevented | travel stop + chocks | ✔ |
| Rope de-tensioned | drum/dead-end slack confirmed | ✔ |

## 4. Sign-Off

| Role | Lock ID | Status |
|------|---------|--------|
| Authorised isolator | LK-EL-2 | applied |
| Performing crew (rope + brake) | LK-RG-1, LK-MC-5 | applied (full-body harness — work at height) |
| **Competent Person (CP)** | CP-CRN-01 | **must certify before return to molten-metal service** |
| Melt-shop supervisor | — | notified, duration logged |

> **Return to service (P1):** No re-energisation until the CP re-inspects reeving, terminations, fleet angles, and brake; static brake test at 320 t rated SWL holds 5 min zero-drift; CP signs the maintenance certificate (SOP-10 §7). Load-limiter / interlock bypass is permanently prohibited.
