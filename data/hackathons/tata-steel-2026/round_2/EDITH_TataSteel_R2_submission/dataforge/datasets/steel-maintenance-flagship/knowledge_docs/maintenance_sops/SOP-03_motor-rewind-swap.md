# SOP-03 — Motor Rewind and Insurance Spare Swap
## TATA_JSR Maintenance Standard Operating Procedure

**Document ID:** SOP-03  
**Revision:** 1.0  
**Effective Date:** 2026-06-09  
**Equipment Class:** large_induction_motor_vfd  
**Primary Asset Reference:** HSM.F1.MTR01  
**Trigger Failure Modes:** broken_rotor_bar | stator_winding_turn_short | insulation_degradation_ground_fault | rotor_eccentricity | winding_overheat | motor_bearing_spall_BPFO  
**Spine Scenario Reference:** SCN-039 (HSM.F1.MTR01 — broken_rotor_bar; MCSA -34 dBc, VIB 4.8 mm/s)  
**Standard:** IEEE Std 43-2013 (insulation resistance) | IEEE 1415-2006 (MCSA) | NEMA MG1-2021 | IEC 60034-1 Class F  
**Safety Class:** P3 (broken rotor bar — planned swap) | P2 (insulation ground fault)  
**Disclaimer:** SYNTHETIC procedure grounded in research/machinery/03, /16, /18, /19. Values tagged [unverified] are industry heuristics. HSM.F1.MTR01 is an ABB AMI 630 MV (ACS6000 VFD) — always refer to ABB OEM documentation for MV work.

---

## 1. SCOPE

This SOP governs the maintenance, planned swap to insurance spare, and workshop rewind of HSM.F1.MTR01 (ABB AMI 630, 6 000 kW, 990 rpm, 6 kV MV AC induction motor, Insulation Class F, VFD-fed ACS6000).

**Three execution options:**
- **Option A — In-situ insulation treatment** (minor degradation, PI 1.5–2.0, no physical damage)
- **Option B — Insurance spare motor swap** (broken rotor bar confirmed by MCSA; planned 10 h window per SCN-039)
- **Option C — Workshop rewind** (major winding failure, ground fault, PI <1.0, relay trip)

---

## 2. SAFETY / LOTO

> **MV (6 kV) work requires an Authorised Electrical Person (AEP) throughout. No exceptions.**

| Step | Action |
|------|--------|
| S-1 | Issue Electrical Permit to Work (PTW) — shift supervisor sign-off |
| S-2 | Trip motor via process interlock or manual stop. Verify ACS6000 VFD is stopped and DC bus discharge complete (minimum 5 minutes after VFD stop — DC bus capacitor discharge hazard) |
| S-3 | Open MV isolating switchgear (motor feeder). Lock isolator in OPEN position — personal lock + danger tag |
| S-4 | Earth motor terminals using shorting/earthing device — Authorised Electrical Person only |
| S-5 | Verify zero voltage on motor terminals with approved MV meter |
| S-6 | Lock out VFD panel doors |
| S-7 | Post "MV EQUIPMENT ISOLATED — AUTHORIZED WORK IN PROGRESS" at motor terminal box, MCC, and HMI |
| S-8 | For mechanical LOTO: close cooling air dampers, lock cooling fan, apply shaft block if motor is on vertical shaft |
| S-9 | Rig motor only after all electrical LOTO steps complete — motor weight requires crane (confirm rated capacity) |

**PPE Minimum:** MV arc-flash rated PPE (arc rating per site hazard calculation), rubber gloves (IEC 60903 Class 2 or above for 6 kV), face shield, safety helmet, steel-toe boots, safety glasses.

---

## 3. TRIGGER CONDITIONS

| Sensor Tag | Threshold | Action |
|-----------|-----------|--------|
| JSR.HR.STD1.MTR01.MCSA.RBAR.SB | > -45 dBc (warning) | Confirm MCSA at steady load; schedule motor swap within 2–4 weeks |
| JSR.HR.STD1.MTR01.MCSA.RBAR.SB | > -35 dBc (alarm — SCN-039: -34 dBc) | Plan swap within current week. Bars can spread to catastrophic failure |
| JSR.HR.STD1.MTR01.WIND.TEMP | > 145 °C (warning) | Check cooling; derate load |
| JSR.HR.STD1.MTR01.WIND.TEMP | > 155 °C (alarm, Class F limit) | Emergency trip. Option C rewind required — assess PI |
| JSR.HR.STD1.MTR01.VIB.DE.RMS | > 4.5 mm/s (warning) | Investigate — check bearing and alignment |
| JSR.HR.STD1.MTR01.VIB.DE.RMS | > 7.1 mm/s (alarm) | Stop |
| JSR.HR.STD1.MTR01.CURR.IMBAL | > 2 % (warning) | Check supply voltage balance; investigate winding condition |
| JSR.HR.STD1.MTR01.CURR.IMBAL | > 5 % (alarm) | Stop |
| JSR.HR.STD1.MTR01.INS.PI | < 2.0 (warning) | Offline testing; trend monthly |
| JSR.HR.STD1.MTR01.INS.PI | < 1.5 (alarm) | Remove from service; Option A or C required |
| Differential protection relay trip | Any | Do NOT re-energise. Option C assessment |
| JSR.HR.STD1.MTR01.VIB.2XF1 | > 1.0 mm/s (warning) | Eccentricity indicator — investigate alignment and air-gap |
| JSR.HR.STD1.MTR01.VIB.2XF1 | > 2.5 mm/s (alarm) | Stop |

---

## 4. TOOLS AND EQUIPMENT

| Item | Specification |
|------|--------------|
| Megohmmeter (Megger MIT1025) | 5 kV output for MV motor IR and PI testing |
| MCSA analyser | Baker DX / Motor Monitor Plus — steady-load spectrum at rated slip |
| Hi-pot tester | 2 × rated voltage + 1 kV for 1 min (per IEEE Std 43) |
| Surge tester | Baker D6000 — turn-to-turn short detection |
| Thermal camera | Winding and frame hot-spot survey under load |
| Laser alignment tool | Post-swap coupling alignment |
| Dynamic balancing machine | Rotor balance check (workshop) |
| VPI resin system | Vacuum pressure impregnation for rewind |
| Burnout oven | 350–400 °C, 2–4 h (workshop rewind) |
| Crane (heavy lift) | Confirm capacity against motor weight |
| Phase rotation meter | Verify phase sequence before energising spare motor |
| Insulated tools | Rated for 6 kV throughout MV work |

---

## 5. SPARES REQUIRED

| Part ID | Description | Stock Qty | Lead Time |
|---------|-------------|-----------|-----------|
| MTR-MV-6000 | MV insurance spare motor 6 000 kW | 1 on shelf | 40 weeks if procured new |
| BRG-MTR-SET | Motor DE+NDE bearing set SKF 6326/6226 | 1 on shelf | 1 week |
| RWND-KIT-MV | MV rewind materials (wire/resin/wedge/liner) | 1 on shelf | 3 weeks if OOS |
| SEAL-LAB-01 | Labyrinth seal set | 2 on shelf | 2 weeks |

> **MTR-MV-6000 is a reusable capital spare (USD 450 000 / INR 37.575 M). It is NOT consumed by a swap — failed motor goes to workshop for rotor-bar repair (RWND-KIT-MV ~USD 15 000) and returned to spare stock. Do NOT expense the full motor capital cost against a single repair event.**

---

## 6. NUMBERED PROCEDURE STEPS

### OPTION A — In-Situ Insulation Drying and Treatment

1. Apply full LOTO per Section 2.
2. Open motor terminal box. Disconnect power cables — record wire numbers and terminal positions.
3. Take insulation resistance (IR) reading at 5 kV. Apply temperature correction per IEEE 43-2013 Appendix A (IR doubles for every 10 °C temperature decrease — adjust to 40 °C reference). Record PI (10-min reading / 1-min reading).
4. If PI is 1.5–2.0 and no visible physical damage: proceed with drying.
5. Force dry winding using warm air (heat gun at 50 °C directed through motor cooling vents) for 2–4 h, or pass low current (10% rated current via variable autotransformer) until insulation resistance recovers.
6. Re-test PI — target >2.0 before return to service. [unverified]
7. If accessible and PI still marginal: apply VPI (vacuum-pressure impregnation) varnish treatment in situ using brush application. Allow cure per resin manufacturer's specification.
8. Re-test PI: must be >2.0. If not: escalate to Option C.
9. Reconnect power cables. Remove LOTO. Perform no-load start; verify current balance ≤2% unbalance. Ramp to full load; monitor winding temperature for 2 h.

---

### OPTION B — Insurance Spare Motor Swap (planned 10 h, SCN-039 basis)

**Pre-work (day before scheduled swap)**
10. Confirm MTR-MV-6000 is available and tested. Verify insurance spare was last inspected within 12 months (PI test, bearing condition, grease freshness). If not, test and service the spare before the swap window.
11. Prepare mounting base: check hold-down bolt hole positions match spare motor nameplate; confirm same frame size.
12. Confirm crane availability and lift plan. Record motor weight from nameplate.

**Motor Removal**
13. Apply full LOTO per Section 2. Wait for DC bus discharge.
14. Disconnect all power cables and grounding connection from HSM.F1.MTR01. Cap cable ends with insulating boots.
15. Disconnect instrumentation: PT100 thermocouple leads, MCSA clip-on CTs (if installed), encoder (if coupled to VFD speed reference).
16. Remove coupling half from motor shaft. Mark orientation of coupling halves.
17. Unbolt motor from mounting base (record shimming before removing — shims must be reproduced on spare motor for alignment reference).
18. Rig motor to crane using OEM lift points. Lift and transfer to safe staging area. Tag motor with fault date, work order number, and "FOR ROTOR BAR INSPECTION/REPAIR — SEND TO WORKSHOP."

**Spare Motor Installation**
19. Position spare motor (MTR-MV-6000) on mounting base. Fit shims to match height reference from removed motor.
20. Reconnect power cables. Verify cable termination torque per cable manufacturer specification.
21. Reconnect all instrumentation in exact positions.
22. Reconnect coupling half to spare motor shaft. Refit coupling element (CPL-EL-01 if element shows any wear).
23. Laser-align spare motor coupling to gearbox input shaft. **Acceptance: <0.05 mm parallel, <0.05 mm/100 mm angular.** [unverified — confirm against ABB/Flender alignment spec]
24. Reconnect motor earth bond.
25. Before energising: use phase rotation meter to verify phase sequence at motor terminals matches original motor phase rotation. **Reversed phase rotation will drive the rolling mill in reverse — catastrophic.** This is mandatory.

**Commissioning**
26. Remove all LOTO in reverse order. AEP closes MV isolator last.
27. No-load start: motor starts, verify current balance ≤1% imbalance (normal range). Listen for bearing noise or unusual vibration.
28. Check vibration at DE and NDE at no-load. Must be <2.3 mm/s Zone A.
29. Ramp load progressively per ACS6000 VFD load-ramp parameters. At full load: verify MCSA sideband reading (target: < -50 dBc, i.e., healthy on spare motor).
30. Take winding temperature at 30 min, 1 h, 2 h. Must stabilise below 130 °C (normal range). Record in CMMS as post-repair baseline.
31. File MCSA, vibration, and temperature baselines for MTR-MV-6000 in CMMS.
32. Send failed HSM.F1.MTR01 to motor workshop for rotor bar inspection and repair using RWND-KIT-MV.

---

### OPTION C — Workshop Rewind (major winding failure)

*(Apply after relay trip, PI <1.0, or confirmation of ground fault or phase-to-phase short)*

33. Remove motor per steps 13–18.
34. Transport to motor workshop (on-site or specialist MV winding contractor).
35. Strip stator: burn out old winding in burnout oven (350–400 °C, 2–4 h). Do not exceed temperature that damages lamination silicon-iron stack. [unverified — confirm with ABB]
36. Clean slot insulation remnants. Inspect lamination stack for burning, inter-lamination shorts, or heat damage. If lamination damage: re-core or replace stator — major job extending TTR to weeks.
37. Wind new coils: wire gauge, turns per coil, pitch, and connection (wye/delta) must exactly match ABB AMI 630 original nameplate data. Obtain data from ABB or reverse-engineer from removed coil measurements. **Using heavier wire gauge to save cost reduces turns and causes overfluxing — insist on exact match.**
38. Insert coils; secure with slot wedges.
39. VPI impregnation: immerse in Class H resin (180 °C rated), cure in oven per resin specification (minimum cycle 130 °C for 8 h typical). [unverified]
40. Test rewound stator: hi-pot at (2 × 6 000 + 1 000 = 13 000 V) for 1 minute per IEC 60034-1. Surge test for turn-to-turn shorts. IR at 5 kV (target > 1 000 MΩ at 40 °C). [unverified]
41. Inspect rotor: eddy-current test or rotor bar dye test for broken bars. Measure shaft runout (< 0.025 mm TIR for precision machines). [unverified]
42. Dynamic balance rotor to ISO 21940-11 Grade G2.5 or better. [unverified]
43. Reassemble with new bearings (BRG-MTR-SET), labyrinth seals (SEAL-LAB-01), correct grease grade per ABB specification.
44. No-load run test in workshop: measure current balance, vibration, and winding temperature heat-soak for 2 h. Document and certify before shipping back to site.
45. Reinstall motor per Option B steps 19–31. Promote to insurance spare status; update CMMS.

---

## 7. ACCEPTANCE CHECKS

| Parameter | Acceptance Criterion | Instrument |
|-----------|---------------------|------------|
| MCSA rotor bar sideband | < -50 dBc (healthy; normal range -70 to -50 dBc per spine) | MCSA analyser |
| Insulation PI | > 2.0 (target > 3.0 for new/rewound) | Megger MIT1025 |
| Winding temperature (2 h full load) | Stable, < 130 °C (Class F limit 155 °C) | JSR.HR.STD1.MTR01.WIND.TEMP |
| Phase current imbalance | ≤ 1 % (normal range ≤ 1 %) | NEMA MG1-2021 §12.45 |
| VIB.DE.RMS post-repair | < 2.3 mm/s (Zone A) | Vibration analyser |
| Polarisation Index | > 2.0 | IEEE 43-2013 |
| Shaft alignment (coupling) | < 0.05 mm parallel, < 0.05 mm/100 mm angular | Laser aligner |
| Phase rotation | Confirmed correct (same as original) | Phase rotation meter |

---

## 8. TIME ESTIMATE

| Scenario | TTR |
|----------|-----|
| Option A: in-situ drying | 8–24 h |
| Option B: insurance spare swap (SCN-039 basis) | 10 h planned |
| Option C: workshop rewind (LV motor) | 3–7 days |
| Option C: workshop rewind (MV motor > 1 MW) | 4–12 weeks |
| New MV motor procurement if MTR-MV-6000 consumed | 40 weeks |

*(SCN-039 spine: planned downtime 10 h, cost USD 100 000 — includes production loss during swap)*

---

## 9. RECURRENCE PREVENTION

- Trend PI annually (minimum) or after every thermal event — target catching PI drift before it reaches 2.0.
- VFD shaft currents are the primary cause of both bearing failure and insulation damage in VFD-driven motors. Install insulated bearings and fit AEGIS shaft-grounding ring on HSM.F1.MTR01 if not already present — inspect AEGIS ring condition annually.
- Cooling: check cooling air filters monthly. Blocked filters are the most common cause of thermal winding failures in humid steel-plant environments.
- Motor protection relay: verify that overload, single-phase-loss, phase-imbalance, and thermistor (PT100) trips are all enabled in the ACS6000 protection settings. These are often disabled during commissioning and never re-enabled.
- For broken rotor bar (MCSA onset): bars can spread progressively from 1 to multiple bars within weeks to months under cyclic high-torque start loading. Do not defer swap beyond 2–4 weeks from first confirmed alarm.
