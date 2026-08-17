# SOP-02 — Gearbox Oil Change and Gear Tooth Service
## TATA_JSR Maintenance Standard Operating Procedure

**Document ID:** SOP-02  
**Revision:** 1.0  
**Effective Date:** 2026-06-09  
**Equipment Class:** mill_gearbox  
**Primary Asset Reference:** HSM.F1.GBX01  
**Trigger Failure Modes:** gear_tooth_wear_GMF_sideband | gear_tooth_fatigue_crack | gear_scuffing_micropitting | oil_oxidation_varnish  
**Spine Scenario Reference:** SCN-038 (HSM.F1.GBX01 — gear_tooth_fatigue_crack)  
**Standard:** AGMA 2101-D04 (gear tooth strength) | ISO 13306 (maintenance terminology) | ISO 4406:2021 (oil cleanliness)  
**Safety Class:** P2  
**Disclaimer:** SYNTHETIC procedure grounded in research/machinery/02, /18, /19, /20. Values tagged [unverified] are industry heuristics; validate against Flender H4SH-mill-drive OEM documentation.

---

## 1. SCOPE

This SOP covers two distinct maintenance activities for HSM.F1.GBX01 (Flender H4SH mill-drive reduction gearbox, 6 000 kW, ISO VG 220):

- **Option A (Minor):** Oil flush, filter replacement, and oil-quality restoration — triggered by elevated oil temperature, oil oxidation (varnish), rising ferrous particle count, or scheduled PM interval.
- **Option B (Major):** Gear wheel / pinion replacement and full gearbox overhaul — triggered by confirmed tooth spall, fatigue crack, or chip-detector alarm.

**Safety note:** HSM.F1.GBX01 is a Criticality-1 asset. Gear tooth fatigue (SCN-038: GMF 11.0 mm/s, Fe 60 ppm) is an immediate-stop event — no deferral permitted once chip detector alarms or spall particles confirmed on ferrography.

---

## 2. SAFETY / LOTO

| Step | Action |
|------|--------|
| S-1 | Isolate HSM F1 main drive motor (HSM.F1.MTR01) at MCC — open isolator, personal lock + tag |
| S-2 | HV-LOTO for MV motor (6 kV) per site HV procedure — Authorised Electrical Person required |
| S-3 | Stop lube oil supply pump; close inlet and outlet isolation valves |
| S-4 | Allow gearbox to reach zero-speed (confirm on encoder). For large flywheel-effect drives: minimum 5-minute wait |
| S-5 | Vent any pneumatic/hydraulic coupling activation circuits |
| S-6 | Wait for sump oil to cool below 50 °C before opening drain valve (hot oil burn hazard) |
| S-7 | Post LOTO tags on ALL gearbox access points, drain valves, and lube system |

**PPE Minimum:** Safety helmet, steel-toe boots, cut-resistant gloves, safety glasses, chemical-splash apron when handling hot oil. For major overhaul: add full face shield and heat-resistant gloves during drain operations.

---

## 3. TRIGGER CONDITIONS

| Sensor Tag | Threshold | Action |
|-----------|-----------|--------|
| JSR.HR.STD1.GBX01.VIB.GMF.RMS | > 6.0 mm/s (warning) | Increase oil sampling to every 2 h; notify maintenance manager |
| JSR.HR.STD1.GBX01.VIB.GMF.RMS | > 10.0 mm/s (alarm — SCN-038: 11.0 mm/s) | **Immediate controlled stop.** Proceed to Option B |
| JSR.HR.STD1.GBX01.OIL.TEMP | > 80 °C (warning) | Derate load 20%; increase cooling flow; check lube pump pressure |
| JSR.HR.STD1.GBX01.OIL.TEMP | > 90 °C (alarm) | Controlled stop; oil analysis before restart |
| JSR.HR.STD1.GBX01.OIL.PRES | < 2.2 bar (warning) | Investigate lube pump; do not run gearbox at reduced lube pressure |
| JSR.HR.STD1.GBX01.OIL.FE.PPM | > 15 ppm (warning) | Take additional sample; interpret ferrography |
| JSR.HR.STD1.GBX01.OIL.FE.PPM | > 40 ppm (alarm — SCN-038: 60 ppm) | **Stop. Chip detector inspection. Ferrography. Proceed to Option B if spall confirmed** |
| JSR.HR.STD1.GBX01.OIL.VISC | < 180 cSt or > 265 cSt at 40 °C | Oil oxidation/contamination — Option A flush required |
| Chip detector | Metallic debris present | **Immediate controlled stop.** Option B |
| Scheduled PM interval | (per CMMS plan) | Option A oil service |

---

## 4. TOOLS AND EQUIPMENT

| Item | Specification |
|------|--------------|
| Ferrography unit / oil lab courier | ASTM D5185 particle count + morphological analysis |
| Borescope | Olympus IPLEX or equivalent — gearbox inspection port access |
| Vibration analyser | Cepstrum capability — GMF sideband analysis |
| Hydraulic press | 10–100 T for gear wheel extraction |
| Induction heater | For heat-fit gear wheel reinstallation |
| Laser alignment tool | Post-reinstallation coupling alignment |
| Precision dial gauges | Backlash measurement (resolution 0.01 mm) |
| Prussian blue compound | Gear tooth contact pattern check |
| Flush-oil drums | ISO VG 32 flush grade — minimum 2 × sump volume |
| Clean oil transfer pump | To fill with fresh VG 220 oil |
| Calibrated torque wrenches | Hold-down bolts, end-cap bolts |
| Overhead crane | Minimum capacity for gearbox weight (confirm before lift) |

---

## 5. SPARES REQUIRED

| Part ID | Description | Stock Qty | Lead Time |
|---------|-------------|-----------|-----------|
| FLT-GBX-01 | Gearbox oil filter element | 3 on shelf | In stock |
| OIL-VG220 | ISO VG 220 EP gear oil, 200 L drum | 4 on shelf | In stock |
| GEAR-WHL-M20 | Custom large-module gear wheel (>M20) | 0 on shelf | **36 weeks** |
| BRG-GBX-SET | Gearbox input/output bearing set | 1 on shelf | 3 weeks |
| CPL-EL-01 | Coupling element | 1 on shelf | 2 weeks |

> **CRITICAL SPARE NOTE:** GEAR-WHL-M20 has zero stock and 36-week lead time. If SCN-038 (tooth fracture) occurs without a gear on order, gearbox repair window is 8–24 weeks. This drives the P1 priority for condition-based early detection. Raise a procurement recommendation immediately when GMF sidebands first begin rising.

---

## 6. NUMBERED PROCEDURE STEPS

### OPTION A — Oil Service (4–6 h)

**Pre-work**
1. Record pre-drain oil condition in CMMS: temperature (JSR.HR.STD1.GBX01.OIL.TEMP), pressure (JSR.HR.STD1.GBX01.OIL.PRES), vibration (JSR.HR.STD1.GBX01.VIB.GMF.RMS), and latest ISO 4406 code.
2. Apply LOTO per Section 2. Allow oil to cool below 50 °C.

**Oil Drain and Sampling**
3. Position drain pan (capacity ≥ full sump volume). Open drain valve. Collect entire oil charge.
4. While oil is draining: take a mid-drain oil sample into a clean, labelled sample bottle. Send to lab: ISO 4406:2021 particle count + ASTM D5185 elemental analysis (Fe, Cu, Cr, Si) + kinematic viscosity at 40 °C + acid number.
5. Allow sump to drain completely. Inspect magnetic drain plug — photograph and record any debris on plug. A "cloud" of fine fines is normal; discrete large fragments or shiny slivers indicate tooth damage and require escalation to Option B.
6. Replace oil filter element (FLT-GBX-01). Do not reuse filter even if it appears clean.
7. Replace breather (if blocked or degraded) — a blocked breather pressurises the sump and forces oil past shaft seals.

**Flushing**
8. Close drain valve. Add ISO VG 32 flush-grade oil (minimum 25% of sump volume). Close all inspection ports.
9. Start lube pump for 5 minutes at minimum RPM (ensure gearbox drives remain in LOTO — flush run is on lube pump only, no rotation of main gearbox).
10. Drain flush oil completely. Inspect magnetic drain plug again.
11. Repeat flush once more (two-flush minimum for contaminated sumps). Drain fully.

**Refill and Return to Service**
12. Close drain valve. Add fresh ISO VG 220 EP gear oil (OIL-VG220) to the correct level mark on sight glass. Confirm correct grade — do not mix additive packages from different suppliers.
13. Replace inspection covers and vent plugs.
14. Remove LOTO from lube system only. Start lube oil pump. Verify oil pressure at JSR.HR.STD1.GBX01.OIL.PRES: must be 2.5–4.0 bar (normal range). Verify oil level stable.
15. Remove full LOTO. Start gearbox drive at 25% load for 30 minutes; take vibration and temperature readings.
16. Ramp to full load. Take post-service vibration baseline — GMF must be within 3 dB of pre-service baseline.
17. Take oil sample at 8 hours runtime. Target ISO 4406 recovering toward ≤18/16/13. [unverified]

---

### OPTION B — Gear Wheel Replacement (168 h unplanned / planned shutdown per SCN-038)

**Immediate Stop**
18. On GMF alarm > 10 mm/s OR chip detector alarm: initiate controlled stop. No deferral. Notify shift manager and maintenance manager immediately.
19. Apply full LOTO per Section 2.
20. Retain all oil samples from the event as evidence. Do not discard.

**Gearbox Removal**
21. Disconnect couplings at input and output shafts. Label all coupling components with wire-number and position paint markings for accurate reinstallation.
22. Remove gearbox hold-down bolts (record torque values from data card). Photograph dowel-pin locations.
23. Rig gearbox with crane to OEM lift points marked on housing. Confirm crane capacity against gearbox nameplate weight. Move to gearbox repair workshop. **Weight of HSM.F1.GBX01: confirm with OEM drawing before lift.**

**Disassembly and Inspection**
24. In workshop: record all shaft end-float measurements and backlash values before disassembly. These are the reference for reinstallation.
25. Open gearbox and inspect all gear teeth under workshop lighting. Document every tooth with photographs (record tooth number from reference mark). Classify damage per AGMA 2101-D04: pitting, spalling, micro-pitting, scuffing, tooth-root fracture.
26. Remove damaged gear wheel/pinion from shaft using hydraulic press. If shrink-fit: apply localised induction heat to gear boss only (never direct flame — risk of annealing the shaft). [unverified — confirm with Flender OEM removal procedure]
27. Inspect gear seat on shaft for fretting, wear, or corrosion. Measure seat diameter vs OEM tolerance. If worn: machine-shop regrind and chrome-spray required.

**Gear Wheel Replacement**
28. Install new gear wheel (GEAR-WHL-M20): verify part number and module against CMMS data card. Heat-fit gear to shaft per OEM interference specification (typically 0.05–0.15% of bore diameter). [unverified]
29. Install new bearings (BRG-GBX-SET) — take this opportunity regardless of bearing condition; bearing replacement cost is negligible versus gearbox removal labour.
30. Set backlash per OEM specification. **Target: 0.1–0.3 mm for industrial mill-drive gearboxes.** Measure with dial gauge at multiple tooth positions (minimum 8 positions around circumference). [unverified — must confirm against Flender H4SH drawing]
31. Check gear tooth contact pattern with Prussian blue compound. Apply thin coat to 3–5 adjacent teeth on the new wheel. Rotate under light torque. Contact pattern must be centred on tooth face and cover **>70% of face width and >60% of tooth height.** [unverified]

**Reassembly and Return to Drive Train**
32. Refill gearbox with ISO VG 220 EP oil (OIL-VG220) after completing assembly. Replace oil filter (FLT-GBX-01).
33. Reinstall gearbox in drive train. Torque hold-down bolts to data-card values. Reinstall dowel pins.
34. Reconnect couplings. Replace coupling element (CPL-EL-01).
35. Laser-align all couplings to <0.05 mm parallel, <0.05 mm/100 mm angular.

**Run-In Procedure (mandatory after gear replacement)**
36. Remove LOTO from lube system. Start lube pump; verify pressure 2.5–4.0 bar.
37. Run-in phase 1: 30 min at **25% rated load.** Take vibration (GMF) and oil temperature. Target GMF <6 mm/s, temperature <65 °C.
38. Run-in phase 2: 1 h at **50% load.** Take oil temperature and vibration. Take oil sample — particle count must be declining (flushing effect from new tooth surfaces).
39. Run-in phase 3: ramp to **full load** over 15 min. Record steady-state GMF, oil temperature, and oil pressure. File as post-repair CMMS baseline.
40. Inspect magnetic drain plug at 24 h after return to full load — a cloud of fine metal fines is normal new-surface bedding; discrete large particles or slivers = investigate further.

---

## 7. ACCEPTANCE CHECKS

| Parameter | Acceptance Criterion | Instrument |
|-----------|---------------------|------------|
| GMF vibration (steady-state full load) | Within 3 dB of pre-repair baseline; <6.0 mm/s (warning threshold) | Vibration analyser |
| Oil temperature | 45–65 °C (normal range) | JSR.HR.STD1.GBX01.OIL.TEMP |
| Lube oil pressure | 2.5–4.0 bar | JSR.HR.STD1.GBX01.OIL.PRES |
| Ferrous particle count (24 h sample) | < 15 ppm (warning onset) | ISO 4406 / ferrography |
| Gear tooth contact (Prussian blue) | >70% face width, centred | Direct inspection |
| Coupling alignment | <0.05 mm parallel, <0.05 mm/100 mm angular | Laser aligner |
| No audible grinding or knocking | Smooth, constant gear-mesh tone | Operator stethoscope |
| Backlash | Per OEM spec (0.1–0.3 mm) [unverified] | Dial gauge |

---

## 8. TIME ESTIMATE

| Scenario | TTR |
|----------|-----|
| Option A: oil service only | 4–6 h |
| Option B: gear wheel replacement (gear on shelf) | 3–7 days |
| Option B: gear on 36-week lead (GEAR-WHL-M20) | 8–24+ weeks — complete gearbox swap or temporary production reduction |

*(SCN-038 spine: unplanned downtime 168 h = 7 days for tooth fracture event; cost impact USD 600 000)*

---

## 9. RECURRENCE PREVENTION

- Monthly ferrographic oil analysis on HSM.F1.GBX01 is non-negotiable. Ferrography detects gear spall particles 2–4 weeks before GMF alarm escalates to emergency stop level.
- Implement kidney-loop filtration with target ISO 4406 < 16/14/11 continuously on this gearbox. [unverified]
- Connect torque measurement to CMMS; auto-raise work order if torque exceeds 110% rated for > 5 seconds (cobble events are primary tooth fatigue initiators).
- Raise long-lead procurement for GEAR-WHL-M20 as soon as ferrous particles first trend above 5 ppm — 36-week lead time means early ordering is the only way to avoid extended downtime on a gear fracture event.
- Enforce run-in procedure after every gear replacement. New tooth surfaces need low-load bedding to prevent adhesive wear during initial contact.
