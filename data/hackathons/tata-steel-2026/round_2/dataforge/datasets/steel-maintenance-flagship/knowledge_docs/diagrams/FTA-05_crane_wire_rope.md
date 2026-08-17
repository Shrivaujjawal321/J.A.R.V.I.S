---
doc_id: FTA-05
title: "Fault-Tree Analysis — Ladle-Crane Wire-Rope Failure"
asset_ids: ["MS.LDC.CRN01"]
related_docs: ["MAN-012", "ELEC-03", "PID-06", "SOP-10", "LOTO-EX-03"]
doc_type: fault_tree
---

# FTA-05 — Ladle-Crane Wire-Rope Fatigue / Broken-Wire Failure
**Doc:** FTA-05 | Rev 1.0 | Site: TATA_JSR (Synthetic)
**Primary asset:** MS.LDC.CRN01 (Konecranes 320 t ladle crane)
**Failure mode (spine):** `wire_rope_fatigue_broken_wire` | **Scenario:** SCN-047
**Fault codes (spine):** `ROPE-MFL-RETIRE`, `ROPE-DISCARD-ISO4309` | **Safety class:** P1
**Standard References:** ISO 4309:2017, FEM 1.001, BS EN 13135, OSHA 1910.179

> **DISCLAIMER — SYNTHETIC DOCUMENT.** Life-safety asset. Grounded in spine SCN-047 + SOP-10 discard criteria. No proprietary Tata Steel data.

---

## 1. Fault Tree

```mermaid
flowchart TD
    TOP["TOP EVENT:<br/>Wire-rope failure → ladle drop → molten-steel spill / fatality"]
    TOP --> G1{{"OR"}}
    G1 --> IE1["Rope fatigue / broken wires exceed discard"]
    G1 --> IE2["Corrosion / metallic-area loss"]
    G1 --> IE3["Mechanical damage"]
    G1 --> IE4["Undetected degradation (inspection gap)"]
    IE1 --> A1{{"AND"}}
    A1 --> B1["Bending cycles over sheaves/drum (low D/d ratio)"]
    A1 --> B2["High-temp melt-shop duty accelerating fatigue"]
    IE2 --> O2{{"OR"}}
    O2 --> B3["Severe pitting / >15-20% LMA"]
    O2 --> B4["Inadequate rope lubrication (>3 mo)"]
    IE3 --> O3{{"OR"}}
    O3 --> B5["Kink / crush / birdcage"]
    O3 --> B6["Wrong reeving / fleet angle >4 deg"]
    IE4 --> O4{{"OR"}}
    O4 --> B7["Missed MRT/MFL inspection"]
    O4 --> B8["Competent-Person inspection lapsed"]
```

## 2. Indented Tree (text)

- **TOP:** Wire-rope failure → ladle drop (mass-fatality risk)
  - **OR**
    - IE1 Fatigue/broken wires **(AND)** — bending cycles (low D/d) + hostile melt-shop duty
    - IE2 Corrosion / LMA loss **(OR)** — pitting / >15–20% LMA; poor rope lube
    - IE3 Mechanical damage **(OR)** — kink/crush/birdcage; wrong reeving / fleet >4°
    - IE4 Undetected degradation **(OR)** — missed MRT; lapsed CP inspection

## 3. Sensor / Inspection Signature → Tree Mapping (SCN-047)

| Stage | Signature (spine / ISO 4309) | Tree node |
|-------|------------------------------|-----------|
| Healthy (months) | `ROPE.MFL` 0–100 mV; <6 broken wires | baseline |
| Warning | `ROPE.MFL` 150 mV (~8–12% LMA); dia −3%; ≥6 random broken wires/lay | IE1/IE2 early |
| Alarm (discard) | `ROPE.MFL` 300 mV (>15–20% LMA); ≥12 random (or ≥4 in one strand); dia −7% | ISO 4309 discard |
| Failure | rope parts → ladle drop | TOP |

**Fault codes:** `ROPE-MFL-RETIRE` (MFL threshold), `ROPE-DISCARD-ISO4309` (broken-wire/LMA/diameter criteria).

> **Defence-in-depth (cuts IE4):** quarterly MRT, monthly visual, pre-shift operator check, mandatory Competent-Person certification before molten-metal return-to-service.

## 4. Resolution
Immediate removal from service on any discard criterion; rope replacement per SOP-10 Part A; brake check Part B. Isolation per LOTO-EX-03 (electrical + brake-hydraulic + gravity — never leave ladle suspended).
