# SOP-04 — Pump Mechanical Seal Replacement
## TATA_JSR Maintenance Standard Operating Procedure

**Document ID:** SOP-04  
**Revision:** 1.0  
**Effective Date:** 2026-06-09  
**Equipment Class:** cooling_descaling_pump  
**Primary Asset References:** HSM.DSC.PMP01 | BF.CW.PMP02  
**Trigger Failure Modes:** mechanical_seal_failure | pump_bearing_failure | impeller_wear_erosion  
**Spine Scenario Reference:** SCN-040 (HSM.DSC.PMP01 — mechanical_seal_failure; VIB 5.4 mm/s, bearing temp 90 °C) | SCN-050 (BF.CW.PMP02 — pump_bearing_failure; bearing temp 100 °C, VIB.1X 5.6 mm/s — bearing-set + SEAL-MECH-DSC replacement covered under Phase B/C bearing + seal work)  
**Standard:** HI 9.6.1-2017 (NPSH) | HI 9.6.7-2021 (pump operation) | ASME B73.1 | ISO 15243:2017 (bearing)  
**Safety Class:** P3  
**Disclaimer:** SYNTHETIC procedure grounded in research/machinery/04, /16, /18, /19. Values tagged [unverified] are industry estimates. HSM.DSC.PMP01 is a KSB Multitec HP (~200 bar service); BF.CW.PMP02 is a KSB Omega double-suction. Refer to KSB OEM documentation for specific torque values, seal dimensions, and impeller fit tolerances.

---

## 1. SCOPE

This SOP covers the replacement of mechanical seals (back-pullout cartridge type) and associated shaft-sleeve inspection on HSM.DSC.PMP01 (high-pressure descaling pump, ~200 bar) and BF.CW.PMP02 (cooling-water pump, 900 kW). Impeller inspection and wear-ring replacement is included as an integrated task when the pump is already open for seal work.

**HSM.DSC.PMP01 specific note:** This pump operates at ~200 bar discharge pressure — seal failure in this service causes high-energy water jets (safety hazard). Always switch to standby pump and fully depressurize before work begins.

---

## 2. SAFETY / LOTO

| Step | Action |
|------|--------|
| S-1 | Switch production to standby pump. Confirm standby is running at target pressure (JSR.HR.DSC.PMP01.PRES.DIS: 190–210 bar for descaler) |
| S-2 | Stop motor via MCC. Confirm motor reaches zero speed |
| S-3 | Close suction isolation valve. Close discharge isolation valve. Lock both valves in CLOSED position |
| S-4 | Apply personal lock + danger tag to motor isolator at MCC |
| S-5 | Open vent/drain valve on pump casing to release trapped pressure. **For HSM.DSC.PMP01: do NOT open casing vent until pressure gauge reads zero.** Wait minimum 2 minutes after valve close before opening vent — accumulators can maintain pressure |
| S-6 | Drain pump casing. Collect fluid in drip tray or drain pan (descale water contains scale inhibitors — follow plant waste disposal procedure) |
| S-7 | Verify zero pressure on casing drain gauge before removing any bolted connection |
| S-8 | Isolate and vent seal flush and quench lines (where applicable) |

**PPE Minimum:** Safety helmet, steel-toe boots, cut-resistant gloves, safety glasses, chemical-splash apron, face shield for pump drain opening (residual high-pressure fluid risk).

---

## 3. TRIGGER CONDITIONS

| Sensor Tag | Threshold | Action |
|-----------|-----------|--------|
| JSR.HR.DSC.PMP01.VIB.CAS.RMS | > 2.5 mm/s (warning) | Inspect seal chamber; check for leakage |
| JSR.HR.DSC.PMP01.VIB.CAS.RMS | > 5.0 mm/s (alarm — SCN-040: 5.4 mm/s) | Stop pump; plan seal change |
| JSR.HR.DSC.PMP01.TEMP.BRG | > 85 °C (warning) | Derate; schedule change |
| JSR.HR.DSC.PMP01.TEMP.BRG | > 100 °C (alarm — SCN-040: 90 °C at failure-stage) | Stop pump |
| JSR.HR.DSC.PMP01.PRES.DIS | < 175 bar (warning) | Investigate impeller wear or blocked suction |
| JSR.HR.DSC.PMP01.FLOW.DIS | < 372 m³/hr (warning) | Investigate impeller wear |
| JSR.HR.DSC.PMP01.PRES.SUC | < 90 kPa (warning — cavitation risk) | Urgent: stop pump; check suction conditions |
| Visual: seal leakage | > 10 mL/min | Plan change within 1 shift |
| Visual: seal spraying water | Any | Switch to standby immediately; emergency seal change |
| JSR.BF.CW.PMP02.TEMP.BRG | > 85 °C | Stop; check bearing condition |
| JSR.BF.CW.PMP02.VIB.BB | > 2.5 mm/s (seal zone) | Inspect seal |

---

## 4. TOOLS AND EQUIPMENT

| Item | Specification |
|------|--------------|
| Seal assembly press / sleeve driver | Sized for pump shaft OD |
| Dial indicator + magnetic stand | Shaft runout measurement (TIR) |
| Bore and OD micrometers | Sleeve scoring measurement; impeller OD |
| Torque wrench | Gland-plate bolts and casing bolts — per OEM data card |
| Face-cleanliness inspection mirror | Verifying seal face before installation |
| Shaft alignment tool (laser) | Post-reinstallation motor-pump alignment |
| Balancing machine | If new impeller is fitted |
| Vacuum/pressure test kit | Post-installation casing pressure test |
| Drip-tray and waste containers | Fluid disposal |
| Clean lint-free cloths and IPA wipes | For seal face and shaft sleeve cleaning |

---

## 5. SPARES REQUIRED

| Part ID | Description | Stock Qty | Lead Time |
|---------|-------------|-----------|-----------|
| SEAL-MECH-DSC | Mechanical seal cartridge SiC/SiC (HSM.DSC.PMP01) | 2 on shelf | 2 weeks if OOS |
| SLV-SHAFT-01 | Pump shaft sleeve | 1 on shelf | 3 weeks if OOS |
| IMP-DSC-01 | Descale pump impeller (if wear found) | 1 on shelf | 8 weeks if OOS |
| IMP-CW-01 | Cooling pump impeller double-suction (BF.CW.PMP02) | 1 on shelf | 6 weeks if OOS |
| WRING-CW-01 | Wear ring set | 2 on shelf | 4 weeks if OOS |

---

## 6. NUMBERED PROCEDURE STEPS

### Phase A — Isolation and Preparation

1. Switch to standby pump. Confirm standby at rated pressure and flow. Record JSR.HR.DSC.PMP01.PRES.DIS = 0 bar after isolation confirms pump is isolated (not standby serving the line).
2. Apply LOTO per Section 2. Verify zero pressure on drain gauge.
3. Drain casing into drip tray. Open seal chamber vent last.
4. Disconnect motor coupling half. Mark coupling halves and shaft with paint pen (reassembly reference).
5. For back-pullout design (KSB Multitec HP): disconnect piping from back end only — leave suction and discharge pipe connected. Withdraw back-pullout unit (motor + bearing housing + impeller assembly) axially rearward.
6. For non-back-pullout design: remove pump casing bolts and withdraw casing exposing impeller and seal.

### Phase B — Seal Removal

7. Remove gland plate bolts. Note spring orientation in gland before disassembly — photograph in situ.
8. Remove rotating assembly (spring-loaded rotating face + shaft sleeve). Keep assembly upright to prevent spring distortion.
9. Remove stationary seat from gland plate seal chamber. Note seal arrangement (pusher or non-pusher, single or tandem, flushed or quenched).
10. Measure existing seal type: note face material (SiC/SiC for abrasive HP service; carbon/SiC for clean-water cooling service), seal OD, ID, and spring dimensions against SEAL-MECH-DSC data card. Confirm match to installed seal.
11. Inspect seal faces under magnification — photograph for failure analysis. Note: thermal cracking of SiC faces = thermal cycling; heavy scoring = abrasive particles; blistering = incorrect fluid compatibility.

### Phase C — Shaft Sleeve Inspection

12. Inspect shaft sleeve (SLV-SHAFT-01) with outside micrometer. Measure sleeve OD at three axial positions.
13. Run fingernail across sleeve face: any detectable groove or step = scoring. If scoring depth > 0.1 mm at any point: replace sleeve. A scored sleeve will cause immediate new-seal leakage even with a new cartridge. [unverified]
14. If sleeve is acceptable (< 0.1 mm): clean sleeve with IPA wipe. Dress minor surface imperfections with 400-grit emery paper wrapped around shaft in rotation direction — do NOT dress with flat strokes.
15. Clean seal chamber bore. Remove all scale and deposits.

### Phase D — Impeller and Wear Ring Inspection (while pump is open)

16. Remove impeller. Measure OD at multiple positions. Compare to design drawing — record wear loss.
17. Measure wear ring clearance between impeller OD and casing wear ring ID. **Normal: 0.3–0.5 mm. Replace wear ring if clearance > 1.0 mm or pump hydraulic efficiency has dropped > 5%.** [unverified]
18. Inspect impeller vanes and inlet eye for erosion damage (scale-laden process water causes erosion at vane leading edges). If erosion reduces vane thickness to < 50% of new: recommend impeller replacement (IMP-DSC-01) at next planned outage.
19. If impeller replaced: balance to ISO 21940-11 Grade G6.3 minimum on shop balancing machine. [unverified]

### Phase E — New Seal Installation

20. **Cleanliness is paramount.** Any contamination on seal faces will cause immediate leakage.
    - Use clean IPA-soaked lint-free cloth for all faces and chambers.
    - Wear clean, powderless nitrile gloves while handling seal faces — one fingerprint causes pitting initiation.
    - Work at a clean bench away from grinding or cutting operations.
21. Lightly lubricate all O-rings with the compatible fluid for this service:
    - HSM.DSC.PMP01 (process water): use clean water only — never grease on water seals.
    - BF.CW.PMP02 (cooling water): use clean water.
    - Never use petroleum grease on water seal O-rings.
22. Install new stationary seat into gland bore. Apply moderate, even hand pressure — no tools. Confirm seat is square and fully seated.
23. Verify shaft sleeve is fitted correctly. Slide rotating assembly (spring + faces + sleeve) onto shaft per manufacturer assembly drawing. Note assembly direction — most seals are specific about spring orientation relative to flow direction. 
24. Push rotating assembly to the set-point position per manufacturer's assembly drawing — cartridge seals have set-screws that lock the face loading; tighten set-screws while faces are under correct compression, then release and re-confirm.
25. Fit gland plate. Torque gland bolts evenly in cross pattern to OEM specification.
26. Verify shaft runout with dial indicator before closing casing: **< 0.05 mm TIR.** [unverified] Runout > 0.05 mm indicates bearing issue or shaft bending — investigate before proceeding.

### Phase F — Reassembly

27. Refit impeller (torque impeller nut to OEM specification — note: most single-stage pumps have left-hand thread on impeller nut — verify against KSB drawing). [unverified]
28. Reassemble pump casing / reinsert back-pullout unit. Torque casing bolts in cross pattern.
29. Reconnect flush and quench connections to seal per piping diagram.
30. Reconnect coupling half. Laser-align motor to pump. **Acceptance: < 0.05 mm parallel, < 0.05 mm/100 mm angular.** [unverified]

### Phase G — Return to Service

31. Slowly open suction valve. Allow casing to fill (confirm through vent or drain plug — no air trapped).
32. Remove LOTO. Start motor.
33. Open discharge valve gradually while monitoring JSR.HR.DSC.PMP01.PRES.DIS and JSR.HR.DSC.PMP01.FLOW.DIS. Ramp to operating point.
34. Inspect seal chamber immediately after start for any visible leakage. Cartridge seals should be zero-leakage. If any spray or drip: STOP pump immediately — seal faces may have been contaminated during installation.
35. After 15 minutes of operation: take vibration reading at pump casing (JSR.HR.DSC.PMP01.VIB.CAS.RMS). Target: < 1.5 mm/s (normal range: 0.5–1.5 mm/s).
36. After 60 minutes: check bearing temperature (JSR.HR.DSC.PMP01.TEMP.BRG). Target: < 70 °C.
37. Record all sensor readings as post-repair baseline in CMMS work order.

---

## 7. ACCEPTANCE CHECKS

| Parameter | Acceptance Criterion | Instrument |
|-----------|---------------------|------------|
| Seal leakage | Zero visible leakage (cartridge seal) | Visual inspection |
| VIB.CAS.RMS | < 1.5 mm/s (normal range: 0.5–1.5 mm/s) | JSR.HR.DSC.PMP01.VIB.CAS.RMS |
| TEMP.BRG (60 min) | < 70 °C | JSR.HR.DSC.PMP01.TEMP.BRG |
| PRES.DIS | 190–210 bar (normal range) | JSR.HR.DSC.PMP01.PRES.DIS |
| FLOW.DIS | 388–412 m³/hr (normal range) | JSR.HR.DSC.PMP01.FLOW.DIS |
| Shaft runout (TIR) | < 0.05 mm | Dial indicator |
| Pump alignment | < 0.05 mm parallel | Laser aligner |
| PRES.SUC | 120–250 kPa (above cavitation threshold) | JSR.HR.DSC.PMP01.PRES.SUC |

---

## 8. TIME ESTIMATE

| Scenario | Planned TTR | Unplanned TTR |
|----------|-------------|---------------|
| Back-pullout seal change (HSM.DSC.PMP01) | 3 h | 8 h |
| In-line pump (pipe removal needed) | 6 h | 12 h |
| Seal + impeller/wear ring replacement | 5 h | 10 h |
| Shaft sleeve replacement | +2 h on any of above | Same |

*(SCN-040 spine: planned 3 h, unplanned 8 h; cost USD 14 400)*

---

## 9. RECURRENCE PREVENTION

- **Cavitation prevention:** Verify NPSH margin at all operating flow rates. Check JSR.HR.DSC.PMP01.PRES.SUC is stable above 120 kPa at maximum flow — a suction pressure fluctuation is the indicator of NPSH approach. Check suction strainer for blockage monthly.
- **Abrasive service upgrade:** For HSM.DSC.PMP01 (scale-laden HP water): SiC/SiC seal faces are mandatory. Do NOT substitute with carbon face even as an emergency measure — carbon will fail within hours in this service.
- **Sleeve material upgrade:** Consider Colmonoy-overlay shaft sleeve for HSM.DSC.PMP01 — higher hardness extends interval between replacements in abrasive service. [unverified]
- **Seal flush quality:** Verify flush-water quality quarterly — most seal failures in steel-plant service trace to dirty or inadequate flush water.
- **Alignment:** Misaligned motor imposes radial load on shaft, accelerating seal wear. Laser-align every time pump is disturbed.
- **Condition trending:** Monitor JSR.HR.DSC.PMP01.FLOW.DIS vs PRES.DIS weekly and plot on pump curve. Impeller wear can be detected 4–8 weeks before seal failure accelerates, allowing planned intervention.
