# SOP-01 — Rolling-Element Bearing Replacement
## TATA_JSR Maintenance Standard Operating Procedure

**Document ID:** SOP-01  
**Revision:** 1.0  
**Effective Date:** 2026-06-09  
**Equipment Class:** rolling_mill_work_roll_bearing | large_induction_motor_vfd | mill_gearbox | cooling_descaling_pump | bf_sinter_fan_blower  
**Primary Asset References:** HSM.F3.WR.BRG01, HSM.F1.MTR01, HSM.F1.GBX01, HSM.DSC.PMP01, BF.CW.PMP02, BF.BLW.FAN01, SP.SINT.FAN01  
**Trigger Failure Modes:** outer_race_fatigue_spall_BPFO | inner_race_fatigue_spall_BPFI | lubrication_starvation_overheat | pump_bearing_failure | motor_bearing_spall_BPFO | bearing_overheating | journal_bearing_failure  
**Spine Scenario Reference:** SCN-037 (HSM.F3.WR.BRG01 — outer_race_fatigue_spall_BPFO)  
**Standard:** ISO 15243:2017 (bearing failure classification) | ISO 10816-3:2009 / ISO 20816-3:2022 (vibration zones) | API 670:2014 (machinery protection)  
**Safety Class:** P2 (default) — P1 for BF.BLW.FAN01  
**Disclaimer:** SYNTHETIC procedure grounded in cited standards and research/machinery/01, /15, /19. Numbers tagged [unverified] are industry estimates; validate against OEM documentation before operational use.

---

## 1. SCOPE

This SOP covers the planned or emergency replacement of rolling-element bearings (deep-groove ball, cylindrical roller, tapered roller, 4-row cylindrical roller neck bearings) on all rotating machines at TATA_JSR. It applies whether the defect was identified by condition monitoring (vibration, temperature, acoustic emission) or by reactive failure.

**Applies to:** work-roll chock bearings, motor drive-end (DE) and non-drive-end (NDE) bearings, gearbox shaft bearings, pump bracket bearings, fan pedestal bearings.

**Out of scope:** Hydrodynamic journal bearings and thrust bearings on BF.BLW.FAN01 (route to OEM via SOP-05 Fan Balancing and Blade Service — Siemens/MAN specialist team), oil-film bearings requiring specialist OEM team.

---

## 2. SAFETY / LOTO

> **STOP. No physical contact until zero-energy state is verified.**

| Step | Action |
|------|--------|
| S-1 | Isolate main drive at MCC/switchgear — open isolator, apply personal lock + danger tag |
| S-2 | Isolate lube oil system (stop lube pump, close isolation valve to bearing under repair) |
| S-3 | Vent hydraulic / pneumatic actuators associated with the equipment |
| S-4 | Wait for machine to reach a full stop (zero speed on tachometer / encoder) |
| S-5 | Verify zero volts on motor terminals with approved voltmeter |
| S-6 | Apply mechanical block/lock where residual stored energy (spring-loaded devices, gravity-loaded rolls) exists |
| S-7 | Post "EQUIPMENT UNDER MAINTENANCE — DO NOT START" on all start buttons and HMI |
| S-8 | For HSM.F1.MTR01 (MV 6 kV motor): HV-LOTO requires an Authorised Electrical Person in addition to mechanical LOTO — dual-lock regime |
| S-9 | Allow hot bearing housings to cool below 50 °C before physical contact; confirm with IR thermometer |

**PPE Minimum:** Safety helmet, steel-toe boots, cut-resistant gloves, safety glasses. For HSM.F3.WR.BRG01 oil-film bearing: add face shield (oil spray risk). For BF.BLW.FAN01: also wear hearing protection (residual gas noise in blast-furnace area).

---

## 3. TRIGGER CONDITIONS (When to Activate This SOP)

| Sensor Tag | Alarm Threshold Exceeded | Decision |
|-----------|--------------------------|---------- |
| JSR.HR.STD3.WR.BRG01.VIB.DE.H.RMS | > 7.1 mm/s (ISO 20816-3 Zone D) | Emergency bearing change — do not defer |
| JSR.HR.STD3.WR.BRG01.VIB.DE.ENV.BPFO | > 3.0 g | Confirm bearing defect; plan change within next roll-change window |
| JSR.HR.STD3.WR.BRG01.TEMP.DE | > 100 °C | Emergency controlled stop (SCN-037: temp reached 102 °C at failure) |
| JSR.HR.STD3.WR.BRG01.AE.RMS | > 6 dBuV (warning) → > 12 dBuV (alarm) | AE is leading indicator — warning = plan; alarm = act within 4 h |
| JSR.HR.STD1.MTR01.VIB.DE.RMS | > 7.1 mm/s | Emergency |
| JSR.BF.CW.PMP02.TEMP.BRG | > 100 °C | Emergency |
| JSR.BF.BLW.FAN01.TEMP.BRG | > 95 °C | Emergency — P1 asset, notify shift manager immediately |
| Any bearing temp | Sustained rise >5 °C/hr at steady load | Accelerated monitoring; plan change within 24 h |

---

## 4. TOOLS AND EQUIPMENT

| Item | Specification |
|------|--------------|
| Vibration analyser | CSI 2140 / Fluke 810 or equivalent — confirm BPFO/BPFI/AE trend before work |
| Hydraulic bearing puller | Capacity matching bearing bore (minimum 50 kN for >300 mm bore) |
| Induction bearing heater | 80–120 °C range; temperature display; demagnetisation function |
| Laser shaft-alignment tool | Prüftechnik OPTALIGN SMART or equivalent; target <0.05 mm parallel, <0.05 mm/100 mm angular |
| Calibrated torque wrench | Range matching OEM end-cap bolt specification |
| Bore gauge set | Resolution 0.001 mm, range to match housing bore |
| Micrometer set | OD measurement; resolution 0.001 mm |
| Dial indicator + magnetic stand | Shaft runout measurement |
| IR thermometer | For monitoring during reassembly run |
| Oil sampling kit | Pre-repair and post-repair sample; ASTM D5185 / ISO 4406:2021 |
| Calibrated dial thermometer | Induction heater temperature confirmation |
| Clean lint-free cloths | Housing and journal cleaning |
| Solvent (approved grade) | Shaft journal and housing cleaning |
| Crane / chain hoist | As required by component weight — always rig per weight |

---

## 5. SPARES REQUIRED

| Part ID | Description | Stock Qty | Lead Time |
|---------|-------------|-----------|-----------|
| BRG-LRG-300 | Large-bore roller bearing >300 mm (HSM.F3.WR.BRG01) | 1 on shelf | 8 weeks if OOS |
| BRG-MTR-SET | Motor DE+NDE bearing set SKF 6326/6226 (HSM.F1.MTR01) | 1 on shelf | 1 week if OOS |
| BRG-GBX-SET | Gearbox input/output bearing set (HSM.F1.GBX01) | 1 on shelf | 3 weeks if OOS |
| SEAL-LAB-01 | Labyrinth seal set | 2 on shelf | 2 weeks if OOS |
| CPL-EL-01 | Coupling element (spider/grid) | 1 on shelf | 2 weeks if OOS |
| LUBE-NOZ-01 | Oil-film bearing lube nozzle | 4 on shelf | 1 week if OOS |

> **Pre-work check:** Confirm bearing part number against CMMS equipment data card before requisitioning. Verify bearing is at ambient temperature (new bearing from cold store should be handled with gloves — fingerprint oils on raceways cause pitting initiation).

---

## 6. NUMBERED PROCEDURE STEPS

### Phase A — Pre-Work Verification (30 min before shutdown)

1. Pull vibration and temperature trend from SCADA for the last 72 hours. Record pre-repair baseline values in CMMS work order.
2. Confirm replacement bearing part number against equipment data card in CMMS. Unbox bearing; inspect for transport damage; confirm bore, OD, and width match.
3. Confirm induction heater is functional; pre-set to 90 °C.
4. Stage all tools and spares at the work site. Confirm crane or hoist availability and rated capacity.
5. Brief work crew: roles (disassembly lead, reassembly lead, safety observer), tool assignments, expected TTR.

### Phase B — Controlled Equipment Stop

6. Notify production planning: expected downtime — planned: 5 h (SCN-037 basis); unplanned: up to 12 h.
7. For HSM.F3.WR.BRG01 (Zone D / temp >100 °C): initiate controlled stop — do NOT emergency-trip (thermal shock from sudden stop can worsen bearing damage and damage adjacent components). Reduce rolling load progressively over 3–5 minutes before stopping drives.
8. Wait for full stop and apply LOTO per Section 2.

### Phase C — Disassembly

9. Drain and collect lube oil from the bearing housing. Label sample container with asset ID, date, and work order number. Send to laboratory for ISO 4406:2021 particle count and ferrographic analysis.
10. Remove coupling half from the shaft. Record coupling gap and angular offset with dial indicator for reference during reinstallation. Mark coupling halves and shaft with paint pen (for correct re-orientation).
11. Remove bearing housing end-caps (record bolt positions and torque values from data card before removing).
12. Photograph bearing in situ — all faces visible — before removal. This documentation is mandatory for CMMS failure record.
13. Use hydraulic bearing puller. Apply pulling force evenly to inner ring only. **NEVER** strike the bearing with a hammer or drift directly on raceways. For large-bore bearings (>300 mm, HSM.F3.WR.BRG01): use hydraulic oil injection if shaft has oil-injection groove per OEM drawing.
14. Measure shaft journal diameter with micrometer at three axial positions and two perpendicular orientations. Record all six readings. Compare to OEM tolerance (H7/k6 typical fit: +0/-0.025 mm). [unverified — confirm against OEM drawing]
15. Measure housing bore with bore gauge. Compare to OEM G7 tolerance. [unverified]
16. If journal worn beyond tolerance: tag shaft for machine-shop regrind and chrome spray. This extends TTR by 3–5 days — update CMMS and notify shift manager.

### Phase D — Root-Cause Inspection

17. Wash removed bearing in clean solvent. Air-dry. Examine under magnification (×10 loupe minimum).
18. Classify failure mode per ISO 15243:2017 and record in CMMS:
    - Fatigue spalling (subsurface crack → surface pitting) — typical for BPFO/BPFI sensor alarms
    - Adhesive/abrasive wear
    - Corrosion
    - Electrical erosion (fluting) — if present, mandate AEGIS ring check on motor
    - Plastic deformation (overload)
    - Fracture
19. For SCN-037 (BPFO alarm): confirm outer-race spall present. Photograph fatigue origin. Note lube condition — contamination (hard particles) accelerates fatigue.
20. Inspect labyrinth seal (SEAL-LAB-01 reference): measure clearance. If damaged or worn: replace as part of this repair.
21. Inspect lube lines/nozzles: confirm correct nozzle direction (LUBE-NOZ-01 should direct oil jet at rolling elements, not cage). Replace any blocked nozzle.

### Phase E — Reassembly

22. Clean housing bore and shaft journal with approved solvent. Dry with lint-free cloth. Verify surface finish — Ra <1.6 µm by fingernail test (no perceptible roughness). [unverified]
23. Check shaft runout with dial indicator on shaft journal. Runout >0.05 mm TIR requires shaft investigation before reassembly.
24. Heat new bearing in induction heater to 80–100 °C. Monitor with contact thermometer. **Do NOT exceed 120 °C** (raceway steel tempering threshold). Bearing is ready when it slides onto shaft journal under hand pressure — if force is required, increase temperature by 5 °C increments.
25. Slide bearing onto shaft in one smooth, continuous motion. Push against inner ring only. Hold in position against the shaft shoulder for 30 seconds until bearing cools and secures.
26. Install labyrinth seal set (SEAL-LAB-01). Verify seal clearance per OEM drawing.
27. Refit bearing housing. Torque end-cap bolts to OEM specification using calibrated torque wrench (star pattern — do not torque diagonally). Record torque value in CMMS.
28. For oil-lubricated bearings: reconnect lube lines. Set oil flow per OEM specification (typically 0.5–2 L/min per bearing). Prime lube system and verify flow at sight glass before starting machine.
29. For grease-lubricated bearings: fill cavity to 30–50% of free space with OEM-specified grease grade. **Overfilling causes churning heat.** [unverified]
30. Recouple shaft. Align using laser alignment tool. **Acceptance criterion: <0.05 mm parallel offset, <0.05 mm/100 mm angular offset.** [unverified — confirm against OEM specification]
31. Replace coupling element (CPL-EL-01) — always replace during bearing change even if it appears serviceable (low cost insurance against premature re-failure).

### Phase F — Return to Service

32. Remove all LOTO — follow reverse LOTO procedure; confirm all crew are clear before energising.
33. Start machine at no load. Run for 15 minutes. Observe bearing housing temperature (target: ambient ± 5 °C initially, stabilising below 70 °C within 60 min for oil-lubricated). Take vibration reading — must be <2.3 mm/s (ISO 20816-3 Zone A) for HSM.F3.WR.BRG01.
34. Take bearing temperatures at 15 min, 30 min, 60 min. If temperature is still rising at 60 min with no sign of stabilising: SHUT DOWN — investigate preload or alignment error.
35. Ramp to full load. Take final vibration signature and BPFO envelope reading. Record in CMMS as new post-repair baseline.
36. Take oil sample at 2 hours of operation. Send to lab. Target: ISO 4406 ≤17/15/12. [unverified]

---

## 7. ACCEPTANCE CHECKS

| Parameter | Acceptance Criterion | Instrument |
|-----------|---------------------|------------|
| VIB.DE.H.RMS (post-repair) | <2.3 mm/s (Zone A, ISO 20816-3) | Vibration analyser |
| VIB.DE.ENV.BPFO (post-repair) | <0.5 g (normal range per spine) | Envelope analyser |
| TEMP.DE (60-min stabilised) | <70 °C (oil-lube bearing) | Thermocouple / IR |
| Shaft alignment (laser) | <0.05 mm parallel; <0.05 mm/100 mm angular | Laser aligner |
| Lube oil flow | Per OEM specification (visible at sight glass) | Visual |
| ISO 4406 particle count (2 h sample) | ≤17/15/12 | Lab analysis |
| No audible abnormal noise | Smooth, no grinding or clicking | Operator listening check |

---

## 8. TIME ESTIMATE

| Scenario | Planned TTR | Unplanned TTR |
|----------|-------------|---------------|
| Standard accessible bearing (e.g. pump bracket) | 3–5 h | 4–8 h |
| Work-roll chock bearing (HSM.F3.WR.BRG01, >300 mm bore, crane required) | 5 h | 12 h |
| Journal regrind required | Add 3–5 days | Same |

*(TTR estimates derived from SCN-037 spine values: planned 5 h, unplanned 12 h)*

---

## 9. RECURRENCE PREVENTION

- Log ISO 15243 failure mode code in CMMS every repair. Over 6 months, surfacing systemic causes (contamination, misalignment, electrical erosion) enables engineering-level corrective action.
- If electrical fluting (channelling on raceways) is found: fit hybrid ceramic insulated bearing and verify AEGIS shaft grounding ring on all VFD-fed motors.
- Mandate laser alignment check whenever coupling is disturbed, and at 6-monthly intervals on all Criticality-1 machines.
- For HSM.F3.WR.BRG01: verify oil-film bearing lube nozzle (LUBE-NOZ-01) direction every PM cycle. Lube starvation + abrasive contamination are the primary accelerators for BPFO fatigue.
- Consider installing permanent wireless vibration nodes (Schaeffler FAG WiPro or Emerson AMS) on HSM.F3.WR.BRG01 and HSM.F1.MTR01 to reduce alarm-to-action latency from hours to minutes.
