# SOP-07 — Continuous Caster Mould Copper Plate Change and Breakout Response
## TATA_JSR Maintenance Standard Operating Procedure

**Document ID:** SOP-07  
**Revision:** 1.0  
**Effective Date:** 2026-06-09  
**Equipment Class:** continuous_caster_mould  
**Primary Asset Reference:** CCM.MOLD.01  
**Trigger Failure Modes:** breakout_sticking | mould_level_instability | copper_plate_wear | SEN_erosion  
**Spine Scenario Reference:** SCN-043 (CCM.MOLD.01 — breakout_sticking; TC delta 55 °C, friction 19 kN, level deviation 13 mm)  
**Standard:** ISO 14224 | EN 746-2:2010 (furnace safety, adapted for caster) | SMS Concast mould standard [unverified]  
**Safety Class:** P1 — BREAKOUT IS A FATALITY RISK  
**Disclaimer:** SYNTHETIC procedure grounded in research/machinery/09, /18, /19. Values tagged [unverified] are industry estimates. CCM.MOLD.01 is an SMS Concast slab mould with Cu-Cr-Zr copper plates and thermocouple array. Refer to SMS Concast and Danieli/Siemens BPS documentation for exact BPS thresholds and mould taper settings.

---

## 1. SCOPE

This SOP covers two distinct scenarios:

**Part A — Routine Mould Maintenance (Planned):** Copper plate inspection, thickness measurement, taper setting, thermocouple continuity check, and mould change between heats. Planned frequency: typically every 2 000–4 000 heats per copper-plate campaign. [unverified]

**Part B — Breakout Emergency Response (Unplanned):** Immediate response to Breakout Prediction System (BPS) alarm (SCN-043 three-sensor confirmation: TC delta > 50 °C, friction > 18 kN, level deviation > 12 mm). This is a P1 safety emergency — liquid steel on the caster floor is fatal.

---

## 2. SAFETY / LOTO

### Part A — Planned Mould Maintenance
| Step | Action |
|------|--------|
| S-1 | Confirm heat complete; tundish gate closed; strand solidified in mould and upper segment |
| S-2 | Stop oscillation drive. Confirm oscillation is at rest |
| S-3 | Close and isolate tundish cooling water supply to mould (not the mould itself — mould cooling continues until copper drops to < 100 °C) |
| S-4 | After copper temperature confirmed < 100 °C: close mould cooling water supply valves; lock |
| S-5 | Apply LOTO to oscillation drive motor |
| S-6 | Verify tundish is raised clear of mould (SEN withdrawn) |

### Part B — Breakout Emergency
| Step | Action |
|------|--------|
| E-1 | **BPS ALARM: IMMEDIATE evacuation of all personnel from caster floor** |
| E-2 | Stop withdrawal rolls (emergency stop withdrawal drive) |
| E-3 | Close tundish slide gate |
| E-4 | Activate site emergency alarm |
| E-5 | Do NOT operate any equipment on the caster floor until liquid steel is confirmed solidified — minimum 4–6 h, may be 24+ h for a large breakout |
| E-6 | Contact shift manager, safety officer, and metallurgy team immediately |

**PPE for Planned Maintenance:** Safety helmet, steel-toe boots, heat-resistant gloves, face shield, heat-resistant apron.  
**PPE for Breakout Recovery Entry:** Full proximity-heat suit, face shield, heat-resistant boots — no entry until skin temperature of affected area < 250 °C confirmed by IR camera.

---

## 3. TRIGGER CONDITIONS

| Sensor Tag | Threshold | Action |
|-----------|-----------|--------|
| JSR.CC1.MOLD.TC.DELTA | > 25 °C (warning) | Notify caster operator; check casting speed, mould powder |
| JSR.CC1.MOLD.TC.DELTA | > 50 °C (alarm — SCN-043: 55 °C) | **BPS: Reduce casting speed immediately. If V-pattern propagating: initiate emergency stop** |
| JSR.CC1.MOLD.OSC.FRICTION | > 10 kN (warning) | Investigate mould lubrication (powder) and taper |
| JSR.CC1.MOLD.OSC.FRICTION | > 18 kN (alarm — SCN-043: 19 kN) | **Emergency stop if combined with TC alarm** |
| JSR.CC1.MOLD.LEVEL.DEV | > 5 mm (warning) | Check SEN; reduce casting speed |
| JSR.CC1.MOLD.LEVEL.DEV | > 12 mm (alarm — SCN-043: 13 mm) | **Emergency if combined with other BPS alarms** |
| JSR.CC1.MOLD.HEATFLUX | < 1.0 MW/m² (warning) | Copper wear or SEN blockage; check |
| JSR.CC1.MOLD.HEATFLUX | < 0.8 MW/m² (alarm) | Stop casting; mould inspection required |
| Mould copper thickness (post-heat measurement) | < 25–30 mm nominal minimum [unverified] | Replace copper plates (Part A) |
| BPS — V-pattern TC plus friction plus level (all 3) | Any combination of 3 sensors crossing warning | **Full BPS alarm — execute Part B emergency response** |

**BPS NOTE:** Single-sensor alerts have >40% false alarm rate. The three-sensor combination (TC delta + friction + level) crossing simultaneously is the SCN-043 confirmed breakout signature. Never inhibit BPS alarms to reduce "nuisance trips" — an inhibited BPS is more dangerous than a nuisance trip.

---

## 4. TOOLS AND EQUIPMENT

| Item | Specification |
|------|--------------|
| Copper plate thickness gauge (contact) | Calibrated ± 0.1 mm resolution |
| CMM or segment gap fixture | Mould taper measurement |
| Mould taper gauge set | Per SMS Concast mould geometry specification |
| Thermocouple continuity tester | Check all TC positions in copper array |
| Pressure test rig | 1.5 × working pressure test for water circuit |
| Torque wrench (calibrated) | Copper plate fastener torque (per OEM spec) |
| Electroplating / reconditioning facility | Re-nickel or hard-chrome plating (on-site or contracted) |
| High-pressure water | Copper surface cleaning |
| Mould crane / handling equipment | For copper plate removal/reinstallation |
| IR camera | Post-breakout recovery — area temperature survey |
| Gas cutting set | Post-breakout skull removal [unverified] |

---

## 5. SPARES REQUIRED

| Part ID | Description | Stock Qty | Lead Time |
|---------|-------------|-----------|-----------|
| MOLD-CU-STD | Mould copper plates (standard slab format) | 1 set on shelf | 14 weeks if OOS |
| SEN-NOZ-01 | Submerged entry nozzle (consumable) | 8 on shelf | In stock |
| ROLL-SEG-STD | Strand guide roll (for post-breakout segment repair) | 2 on shelf | 12 weeks |

> **MOLD-CU-STD has 14-week lead time. Monitor copper plate thickness at every heat-end inspection. Order replacement copper when plate thickness drops below 32 mm (4–6 heats before minimum 25–30 mm threshold). [unverified — confirm minimum with SMS Concast]**

---

## 6. NUMBERED PROCEDURE STEPS

### PART A — Planned Mould Maintenance

**Between-Heat Mould Inspection (15–30 min window)**
1. After end of heat: confirm tundish is raised, SEN withdrawn, oscillation stopped.
2. Verify mould cooling water is still flowing — do not close mould cooling until copper temperature drops below 100 °C (monitored by thermocouple array on copper plate back-face).
3. Inspect mould surface visually through top opening:
   - Look for grooves or erosion channels in the copper face (common at SEN impact zones).
   - Inspect mould corners — high-wear zones.
   - Note any residual powder or steel adhesion.
4. Take mould heat-flux reading from SCADA (JSR.CC1.MOLD.HEATFLUX) — trend vs previous heats on this mould set. Declining heat flux indicates copper wear or scale buildup on cooling channels.
5. If all checks pass: proceed to next heat. Record inspection findings in CMMS mould campaign log.

**Mould Copper Plate Change (planned)**
6. Apply LOTO per Part A steps S-1 to S-6. Confirm mould copper temperature < 100 °C.
7. Remove mould from machine: disconnect cooling water hoses; disconnect oscillation coupling; lift mould assembly via mould handling crane.
8. Transfer to mould workshop.
9. Disassemble: separate copper plates from water box (backplate). Clean copper surfaces with high-pressure water.
10. Measure copper plate thickness at a grid of points (minimum 3 × 5 measurement grid per plate face). Record all measurements. Compare to minimum thickness (25–30 mm typically — confirm from SMS Concast specification). [unverified]
11. Inspect copper face for:
    - Grooves deeper than 1 mm (groove → channel erosion → SEN flow asymmetry → level instability)
    - Transverse cracks (brittle fracture from thermal cycling)
    - Corner distortion > 0.5 mm — return for re-machining if distorted. [unverified]
12. **If within thickness tolerance:** Refurbish by electroplating — re-nickel the copper surface (or hard-chrome for highest-wear mould formats). This is done by on-site electroplating facility or specialist contractor. Shallow grooves (< 1 mm deep) can be filled with Ni overlay and re-surfaced. [unverified]
13. **If below minimum thickness or cracked:** Replace copper plates (MOLD-CU-STD). Do not attempt to use below-minimum plates — risk of shell breakthrough and breakout.
14. Reassemble mould: torque copper plate fasteners per OEM specification in cross-pattern.
15. Check mould taper: use taper gauge to measure taper value at top and bottom of copper plate (full-face taper should match grade/casting-speed specification from metallurgy procedure). Adjust taper bolts to correct value.
16. Test all thermocouple positions: connect TC continuity tester to TC array plug. Record any open circuits — damaged TCs must be replaced before mould goes back into service (BPS relies on the full TC array).
17. Pressure-test mould water circuit: apply 1.5 × working pressure for 10 minutes. Zero leakage. [unverified] 
18. Check oscillation drive coupling condition. Replace oscillation bearing if any wear noted.
19. Reinstall mould on machine. Reconnect cooling water. Verify all TC connections to BPS system are live (BPS self-test before first heat — mandatory).

---

### PART B — Breakout Emergency Response

**Immediate Response (0–2 minutes from BPS alarm)**
20. **On BPS alarm (SCN-043: TC delta > 50 °C V-pattern + friction > 18 kN + level deviation > 12 mm):** Reduce casting speed to minimum immediately (target 0.5 m/min per BPS protocol). This can allow the sticking shell to "heal" if the breakout has not yet propagated through the shell.
21. If casting speed reduction does not stop the TC V-pattern propagation within 30 seconds: **FULL EMERGENCY STOP:**
    - Stop withdrawal rolls (emergency-stop withdrawal drive)
    - Close tundish slide gate simultaneously
    - Press emergency-stop on caster HMI
22. Activate site emergency alarm. **Order immediate evacuation of all personnel from the caster floor area.** Liquid steel on caster floor is a fatality risk. No exceptions.
23. Close ladle slide gate (inform ladle transfer car operator via radio).
24. Notify shift manager, safety officer, metallurgist within 60 seconds of alarm.
25. Do NOT attempt to restart caster or enter floor area under any circumstances until cleared by shift manager and safety officer.

**Monitoring Phase (after emergency stop)**
26. Observe SCADA: watch caster floor temperature sensors and IR camera feeds for any indication of liquid steel on floor.
27. Track time since emergency stop. Minimum 4–6 h before any entry into the affected bay area. For a large breakout (multiple segments involved): may be 24+ h. [unverified]
28. After minimum cooling period: IR camera survey of entire affected bay from the control room or safe vantage point — confirm floor temperature is below 250 °C before entry. [unverified]

**Post-Breakout Recovery**
29. Full PPE for all personnel entering the bay (proximity heat suit, face shield). First entry is safety officer + maintenance supervisor only. Assess extent of steel spillage.
30. Remove solidified steel skull: requires gas cutting equipment (oxygen/LPG), hydraulic jackhammers, and manual breaking tools. This can take many hours to days for a large breakout.
31. Inspect all strand guide segments in the affected zone (Segment 7 and adjacent segments) for damage:
    - Check segment frames for steel infiltration into cooling pipes or frame distortion.
    - Check all rolls for seizure, damage.
    - Replace all damaged segments and rolls using SOP-06 Segment Change procedure.
32. Clean all secondary cooling nozzles — scale from evaporated cooling water during the thermal event blocks nozzles.
33. Check structural integrity of the caster building — check for spalling of concrete overhead and any structural steel distortion.
34. Recommission caster per normal first-cast procedure. Run first heat at 60–70% speed with enhanced monitoring.
35. Initiate formal 5-whys Root Cause Analysis within 48 h of breakout event. Document: BPS alarm history, TC delta trend, friction trend, level trend, casting speed history, mould powder grade, SEN condition, taper setting, heat composition. Log findings in CMMS with event code "BREAKOUT."

---

## 7. ACCEPTANCE CHECKS

| Parameter | Acceptance Criterion | Instrument |
|-----------|---------------------|------------|
| Copper plate thickness (all measurement points) | > 25–30 mm minimum [unverified] | Thickness gauge |
| Mould taper | Per grade/speed specification (metallurgy procedure) | Taper gauge |
| TC array continuity | 100% of thermocouples functional | TC continuity tester |
| BPS system | Self-test passed; all alarm thresholds active | BPS HMI / Siemens/Danieli |
| Mould cooling circuit | Zero leakage at 1.5 × WP for 10 min | Pressure gauge |
| Mould level (first heat) | ± 2 mm deviation (normal range: -2 to +2 mm) | JSR.CC1.MOLD.LEVEL.DEV |
| Oscillator friction (first heat) | 2–8 kN (normal range) | JSR.CC1.MOLD.OSC.FRICTION |
| Heat flux (first heat) | > 1.2 MW/m² (normal range: 1.2–2.0 MW/m²) | JSR.CC1.MOLD.HEATFLUX |
| TC delta (first heat) | < 20 °C (normal range: 0–20 °C) | JSR.CC1.MOLD.TC.DELTA |
| Slab surface quality | No longitudinal cracks; oscillation marks uniform | Slab surface inspection |

---

## 8. TIME ESTIMATE

| Scenario | TTR |
|----------|-----|
| Between-heat inspection (no issues) | 10–30 min |
| Planned copper plate change (off-machine) | 4–8 h |
| Breakout recovery (minor, localised, < 2 segments) | 24–48 h |
| Breakout recovery (major, multi-segment damage — SCN-043 worst case) | 3–14 days |

*(SCN-043 spine: unplanned downtime 36 h; cost USD 860 000 average — range USD 200 000–3 000 000+)*

---

## 9. RECURRENCE PREVENTION

- **BPS tuning:** Refine BPS alarm thresholds using post-event thermocouple data. Do not reduce sensitivity to eliminate nuisance trips — a nuisance trip is far cheaper than a breakout.
- **Mould powder management:** Correct mould powder for each steel grade is critical to shell lubrication. Grade changes MUST trigger powder changes per the metallurgical procedure. Incorrect powder (viscosity, melting point) is a primary sticking cause.
- **SEN quality control:** Inspect SENs (SEN-NOZ-01) at goods receipt. Cracked or undersized SENs cause asymmetric steel flow and shell thinning on one mould face. Any crack in SEN = reject before use.
- **Cooling water quality:** Scale in mould cooling channels reduces heat transfer → copper hot spots → shell temperature rise. Implement water treatment (scale inhibitor + corrosion inhibitor) and annual descaling of mould water circuits.
- **Taper management:** Wrong taper (too tight = shell sticking; too loose = bulging) is a leading breakout cause. Validate taper setting after every copper plate change and at every grade transition requiring a taper change.
- **Every breakout requires formal 5-whys RCA within 48 h.** Logging breakout events with full sensor data in CMMS builds the pattern library that prevents recurrence.
