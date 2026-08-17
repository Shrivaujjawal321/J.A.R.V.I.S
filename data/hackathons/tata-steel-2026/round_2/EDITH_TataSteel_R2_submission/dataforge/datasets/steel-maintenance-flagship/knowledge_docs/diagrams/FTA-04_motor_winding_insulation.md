---
doc_id: FTA-04
title: "Fault-Tree Analysis — Motor Stator Winding Insulation Failure"
asset_ids: ["HSM.F1.MTR01"]
related_docs: ["MAN-003", "ELEC-01", "PID-01", "SOP-03", "LOTO-EX-01"]
doc_type: fault_tree
---

# FTA-04 — MV Motor Stator-Winding Insulation Failure
**Doc:** FTA-04 | Rev 1.0 | Site: TATA_JSR (Synthetic)
**Primary asset:** HSM.F1.MTR01 (ABB AMI 630 MV, Class F, VFD-fed)
**Failure mode (spine):** `stator_winding_turn_short` / `insulation_degradation_ground_fault`
**Related scenario:** SCN-039 family (electrical modes) | **Safety class:** P3
**Standard References:** IEEE 43-2013, IEC 60034-1, IEEE 1415-2006, NEMA MG1-2021

> **DISCLAIMER — SYNTHETIC DOCUMENT.** Grounded in MAN-003 §5.2/§5.3 and spine motor sensors. No proprietary Tata Steel data.

---

## 1. Fault Tree

```mermaid
flowchart TD
    TOP["TOP EVENT:<br/>Stator insulation failure → turn/ground fault → motor trip"]
    TOP --> G1{{"OR"}}
    G1 --> IE1["Insulation thermal ageing"]
    G1 --> IE2["VFD-induced electrical stress"]
    G1 --> IE3["Moisture / contamination ingress"]
    IE1 --> O1{{"OR"}}
    O1 --> B1["Winding overheat (WIND.TEMP >145 C)"]
    O1 --> B2["Repeated thermal cycling (VFD start/stop)"]
    IE2 --> O2{{"OR"}}
    O2 --> B3["High dV/dt transients erode turn insulation"]
    O2 --> B4["Common-mode voltage / partial discharge"]
    IE3 --> O3{{"OR"}}
    O3 --> B5["Humidity / condensation"]
    O3 --> B6["Conductive dust / oil film on windings"]
```

## 2. Indented Tree (text)

- **TOP:** Stator insulation failure → turn-short / ground fault → trip
  - **OR**
    - IE1 Thermal ageing **(OR)** — overheat (`WIND.TEMP` >145 °C); thermal cycling
    - IE2 VFD electrical stress **(OR)** — dV/dt erosion; common-mode / partial discharge
    - IE3 Moisture/contamination **(OR)** — humidity; conductive dust/oil

## 3. Sensor Signature → Tree Mapping

| Stage | Spine / MAN-003 signature | Tree node |
|-------|---------------------------|-----------|
| Healthy | `WIND.TEMP` 118 °C; `CURR.IMBAL` 0.6%; `INS.PI` 2–5 | baseline |
| Warning | `INS.PI` < 2.0 (offline); slot temp asymmetry; `CURR.IMBAL` rising | IE1/IE2 |
| Alarm | `INS.PI` < 1.5 (do-not-energise); `CURR.IMBAL` >5%; `VIB.2XF1` elevated (magnetic asymmetry) | turn-short developing |
| Failure | phase-to-phase / ground fault → relay 50N/49 trip | TOP |

**Protection ties (ELEC-01):** relay 46 (`CURR.IMBAL`), relay 49 (`WIND.TEMP`), offline IR/PI (`INS.PI`).

## 4. Resolution
PI < 1.5 → do NOT re-energise without engineering review (MAN-003). Rewind (RWND-KIT-MV, 3-wk) or swap to insurance spare (MTR-MV-6000) per SOP-03. Isolation per LOTO-EX-01 (MV + VFD DC-link + gravity back-drive).
