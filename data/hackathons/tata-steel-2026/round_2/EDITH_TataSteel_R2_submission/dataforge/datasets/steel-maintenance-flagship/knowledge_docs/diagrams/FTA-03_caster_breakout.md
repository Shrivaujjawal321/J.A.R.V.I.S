---
doc_id: FTA-03
title: "Fault-Tree Analysis — Continuous-Caster Breakout (Sticking)"
asset_ids: ["CCM.MOLD.01"]
related_docs: ["MAN-007", "PID-02", "SOP-07", "LUBE-01"]
doc_type: fault_tree
---

# FTA-03 — Continuous-Caster Breakout / Shell Sticking
**Doc:** FTA-03 | Rev 1.0 | Site: TATA_JSR (Synthetic)
**Primary asset:** CCM.MOLD.01 (slab Cu-Cr-Zr mould)
**Failure mode (spine):** `breakout_sticking` | **Scenario:** SCN-043
**Fault codes (spine):** `BPS-BREAKOUT-P1`, `TC-VPATTERN`, `OSC-FRICTION-SPIKE` | **Safety class:** P1
**Standard References:** mould BPS practice; SMS Concast oscillator/mould references

> **DISCLAIMER — SYNTHETIC DOCUMENT.** Grounded in spine SCN-043 (3-of-3 BPS rule). No proprietary Tata Steel data.

---

## 1. Fault Tree

```mermaid
flowchart TD
    TOP["TOP EVENT:<br/>Breakout — solidified shell ruptures below mould → molten-steel spill"]
    TOP --> A0{{"AND (BPS 3-of-3)"}}
    A0 --> IE1["Local shell sticking to mould wall"]
    A0 --> IE2["Oscillator friction spike"]
    A0 --> IE3["Mould-level instability"]
    IE1 --> O1{{"OR"}}
    O1 --> B1["Poor mould lubrication (powder/oil)"]
    O1 --> B2["Improper mould taper / Cu-plate wear"]
    O1 --> B3["SEN blockage / erosion → flow maldistribution"]
    IE2 --> O2{{"OR"}}
    O2 --> B4["Lube film breakdown at meniscus"]
    O2 --> B5["Oscillator mechanism fault"]
    IE3 --> O3{{"OR"}}
    O3 --> B6["Level-control hunting"]
    O3 --> B7["Tundish/SEN flow disturbance"]
```

> **Critical AND-gate:** A true breakout requires concurrent evidence on all three branches (TC V-pattern, friction spike, level wave). Single-sensor excursions are advisory — this AND-gate is the BPS logic that prevents false trips.

## 2. Indented Tree (text)

- **TOP:** Breakout — shell rupture below mould → spill
  - **AND (BPS 3-of-3)**
    - IE1 Shell sticking **(OR)** — poor lubrication; bad taper / Cu-plate wear; SEN blockage
    - IE2 Friction spike **(OR)** — meniscus lube-film breakdown; oscillator fault
    - IE3 Level instability **(OR)** — level-control hunting; SEN flow disturbance

## 3. Sensor Signature → Tree Mapping (SCN-043)

| Stage | Spine signature | Tree node |
|-------|-----------------|-----------|
| Healthy | TC delta 12 °C; level 1 mm; heat flux 1.6 MW/m² | baseline |
| Warning | `TC.DELTA` 20→25 °C **+** `OSC.FRICTION` spike **+** level wave (need all 3) | AND partially met |
| Alarm | `TC.DELTA` >50 °C V-pattern propagating **+** `OSC.FRICTION` >18 kN | BPS trip |
| Failure | shell rupture 60–90 s after BPS alarm | TOP |

**Fault codes:** `BPS-BREAKOUT-P1`, `TC-VPATTERN` (`MOLD.TC.DELTA`), `OSC-FRICTION-SPIKE` (`MOLD.OSC.FRICTION`).

## 4. Resolution
On BPS alarm: automatic casting-speed reduction / strand stop (PID-02 I-CC-01). Post-event: inspect Cu plate for sticking marks, check mould powder feed and SEN, verify oscillator. Mould copper change per SOP-07 if plate wear (B2) is the root cause.
