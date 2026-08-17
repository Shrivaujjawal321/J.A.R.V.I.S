# SOP-06 — Continuous Caster Segment Change
## TATA_JSR Maintenance Standard Operating Procedure

**Document ID:** SOP-06  
**Revision:** 1.0  
**Effective Date:** 2026-06-09  
**Equipment Class:** continuous_caster_segment  
**Primary Asset Reference:** CCM.SEG.07  
**Trigger Failure Modes:** roll_seizure | roll_bearing_failure | spray_nozzle_blockage | segment_misalignment_bulging  
**Spine Scenario Reference:** SCN-042 (CCM.SEG.07 — roll_seizure; roll RPM = 0, clamping force 540 kN)  
**Standard:** ISO 14224 (failure taxonomy) | SMS Concast segment design standard [unverified]  
**Safety Class:** P2  
**Disclaimer:** SYNTHETIC procedure grounded in research/machinery/09, /18, /19. Values tagged [unverified] are industry estimates. CCM.SEG.07 is an SMS Concast Smart Segment. Refer to SMS Concast documentation for segment-specific gap settings, torque values, and lift points.

---

## 1. SCOPE

This SOP covers the planned segment withdrawal, workshop repair, and re-installation for CCM.SEG.07 (Caster 1, Strand Guide Segment 7, withdrawal/bending zone). The primary trigger is roll seizure (SCN-042), but the same procedure applies to any segment requiring withdrawal for bearing replacement, nozzle cleaning, or geometry correction.

**Safety context:** Segment 7 is in the withdrawal/bending zone of Caster 1. If a heat is in progress and roll seizure is detected, the liquid-core zone may still be active in this region. The sequence is: reduce casting speed → end heat → allow strand to cool → then proceed with segment withdrawal. **Never enter the strand guide bay while a cast is in progress or while liquid steel is present in the strand.**

---

## 2. SAFETY / LOTO

| Step | Action |
|------|--------|
| S-1 | Confirm heat has ended and tundish gate is closed. Verify on SCADA that withdrawal roll speed is zero |
| S-2 | Allow strand to cool (minimum 2–4 h for Segment 7 to reach safe handling temperature after end of cast) [unverified] |
| S-3 | Verify strand temperature at Segment 7 location with IR gun — skin temperature must be < 250 °C before entering the bay [unverified] |
| S-4 | Isolate hydraulic power to Segment 7 clamping circuit — close hydraulic isolation valve; lock in CLOSED position |
| S-5 | Isolate secondary cooling water supply to Segment 7 zone — close supply valve; lock |
| S-6 | Isolate withdrawal roll drive at drive cabinet |
| S-7 | Apply danger tags at all isolation points; post "SEGMENT MAINTENANCE — CASTER 1 INHIBITED" on caster HMI |
| S-8 | Establish exclusion zone around Segment 7 bay — barrier tape; no unauthorised entry |
| S-9 | Confirm segment handling crane is inspected and rated for segment weight (SMS Concast Smart Segment: 10–50 T depending on format — confirm from nameplate) |

**PPE Minimum:** Safety helmet, steel-toe boots, heat-resistant gloves, face shield, proximity-heat protection suit for bay entry during cooling phase. Crane rigger PPE for lift operations.

---

## 3. TRIGGER CONDITIONS

| Sensor Tag | Threshold | Action |
|-----------|-----------|--------|
| JSR.CC1.SEG07.ROLL.RPM | < 1.0 rpm (warning) | Investigate roll rotation; check bearing condition |
| JSR.CC1.SEG07.ROLL.RPM | = 0 (alarm — SCN-042) | **Roll seized.** Reduce casting speed; plan end of heat |
| JSR.CC1.SEG07.FORCE.HYD | > 480 kN (warning) | Check for roll seizure or strand over-constraint |
| JSR.CC1.SEG07.FORCE.HYD | > 550 kN (alarm — SCN-042: 540 kN) | End heat; segment change required |
| JSR.CC1.SEG07.BULGE | > 2.0 mm (warning) | Reduce casting speed; check segment gap |
| JSR.CC1.SEG07.BULGE | > 4.0 mm (alarm) | Emergency stop casting in affected zone |
| JSR.CC1.SEG07.SPRAY.FLOW | < 150 L/min (warning) | Check nozzle blockage; reduce casting speed |
| JSR.CC1.SEG07.SPRAY.FLOW | < 120 L/min (alarm) | Stop casting; uncontrolled cooling = transverse cracks |
| JSR.CC1.SEG07.VIB.ROLL | > 3.5 mm/s (warning) | Plan bearing inspection at next maintenance window |
| JSR.CC1.SEG07.VIB.ROLL | > 6.0 mm/s (alarm) | Plan segment change |
| Slab surface: transverse cracks at regular pitch | period = π × roll diameter | Confirms seized roll printing on strand |

---

## 4. TOOLS AND EQUIPMENT

| Item | Specification |
|------|--------------|
| Segment handling crane | Rated for segment weight (confirm against OEM nameplate) |
| Segment transport car / flatbed | To move segment between caster and repair bay |
| Feeler gauge set | Segment gap measurement (roll-to-roll gap vs schedule format) |
| OEM segment gap fixture | If available — reference gap measurement tool per SMS Concast [unverified] |
| Wash bay equipment | High-pressure water for segment cleaning |
| Assembly jacks / hydraulic jacks | Segment frame realignment in repair bay |
| Roll OD micrometer | Roll diameter measurement at multiple positions |
| Nozzle pressure tester | Confirms spray nozzle flow rate and spray angle |
| Hydraulic torque wrench | Tie-rod nut torque (per OEM specification) |
| Pressure test rig | Segment cooling circuit pressure test |
| Borescope or inspection light | Internal hydraulic cylinder inspection |
| Camera (photos for CMMS record) | Document condition of all rolls and seals |

---

## 5. SPARES REQUIRED

| Part ID | Description | Stock Qty | Lead Time |
|---------|-------------|-----------|-----------|
| ROLL-SEG-STD | Strand guide roll (standard diameter) | 2 on shelf | 12 weeks if OOS |
| BRG-SEG-01 | Segment roll bearing | 4 on shelf | 8 weeks if OOS |
| NOZ-SPRAY-01 | Spray nozzle (consumable) | 50 on shelf | In stock |

> **During segment change: always replace ALL bearings in the segment being serviced — cost of bearing is negligible vs re-pull cost if a second bearing fails in service after reinstallation.**

---

## 6. NUMBERED PROCEDURE STEPS

### Phase A — In-Cast Response (SCN-042 — Roll Seizure While Casting)

1. **On ROLL.RPM = 0 alarm:** immediately notify casting supervisor and metallurgist.
2. If strand is still in liquid-core zone at Segment 7: **reduce casting speed to minimum (0.5–0.8 m/min)** to reduce ferrostatic pressure and strand guide forces. Monitor JSR.CC1.SEG07.FORCE.HYD — if force continues to rise toward 550 kN alarm: initiate end of heat.
3. Issue end-of-heat command: stop steel flow from tundish (close slide gate). Allow casting to continue at minimum speed until the tundish is empty and strand solidifies completely in mould and upper strand guide.
4. Do NOT attempt to increase casting speed to clear a seized roll — this increases strand forces and risks transverse cracking or breakout.
5. Record event: timestamp, heat number, casting speed history, force and RPM trend. This is the root-cause record.

### Phase B — Segment Withdrawal

6. Apply LOTO per Section 2. Allow minimum 2–4 h cooling from end of heat. Verify strand skin temperature with IR gun.
7. Release segment tie-rod hydraulic pressure (ensure hydraulic LOTO is active — segment opens under spring load).
8. Confirm strand has withdrawn from segment (or segment is upstream-end of solidified strand — confirm with caster operator).
9. Attach lifting slings/hooks to OEM-designated lifting points on segment frame. Do NOT use non-OEM lift points — segment frame is not designed for arbitrary lifting.
10. Using segment handling crane, lift segment out of strand guide and transfer to segment transport car.
11. Move to segment repair bay.

### Phase C — Segment Inspection and Repair in Workshop

12. Wash entire segment with high-pressure water in wash bay to remove scale, sinter, and solidified steel deposits. Allow to drain.
13. Photograph all rolls — both drive and non-drive ends. Number rolls from 1 (entry roll) to final roll (exit) using chalk or paint.
14. Inspect each roll by hand rotation:
    - Seized rolls will not turn — identify seized rolls and mark.
    - Rolls with rough or irregular rotation = bearing failure.
    - Rolls with visible flats, grooving, or pitting = surface wear or thermal damage.
15. Measure roll OD at drive end, mid-span, and non-drive end using OD micrometer. **Replace roll if wear > 2 mm reduction from nominal OD.** [unverified — confirm against SMS Concast minimum OD table]
16. **Replace ALL bearings (BRG-SEG-01) in the segment.** Remove bearing housings, extract bearings, inspect bearing seats in housing bore. If housing bore is damaged (scoring, corrosion pitting > 0.5 mm deep): segment frame requires machine-shop repair. [unverified]
17. Fit new bearings per ISO 15243 best practice (induction heater 80–100 °C; never hammer). Refit roll into segment frame.
18. Inspect and clean ALL spray nozzles (NOZ-SPRAY-01 — consumable):
    - Remove nozzles.
    - Flush nozzle bores with clean water.
    - Check nozzle spray angle with pressure tester (each nozzle must produce correct fan-angle pattern per SMS specification).
    - Replace any nozzle that is blocked, eroded, or has incorrect spray pattern.
19. Inspect segment frame geometry:
    - Measure gap between upper and lower frame at reference measurement points using feeler gauges and OEM gap fixture (if available). Compare to required gap for current slab casting format (narrow/wide slab schedule).
    - Acceptable tolerance: ± 0.3 mm from nominal gap for this segment. [unverified]
    - If gap is out of tolerance: re-shim frame or grind contact surfaces (metallurgist/engineer approval required).
20. Inspect tie-rods for straightness and thread condition. Inspect hydraulic cylinders for seal integrity (no oil seep). Replace seals if any cylinder shows weeping.
21. Pressure-test cooling circuit: apply 1.5 × working pressure for 10 min. Zero leakage criterion. [unverified]

### Phase D — Segment Re-Installation

22. Transport serviced segment to caster on transport car.
23. Confirm dummy strand or cast strand has cleared the segment bay location.
24. Lower segment into position using handling crane. Guide into strand guide support structure using guide pins.
25. Torque ALL tie-rod nuts to OEM specification using hydraulic torque wrench (cross-pattern torque sequence). **Record torque values in CMMS work order.** [unverified — confirm torque from SMS Concast manual]
26. Set segment gap to format specification: verify upper-lower gap with feeler gauges at reference measurement points. Shim if required.
27. Reconnect hydraulic supply lines. Reopen hydraulic isolation valve.
28. Apply hydraulic clamping force — ramp to mid-range (300 kN) and verify JSR.CC1.SEG07.FORCE.HYD reading corresponds. Zero offset calibration if required.
29. Reconnect secondary cooling water supply lines. Reopen cooling water valve.
30. Verify roll rotation: energise withdrawal drive briefly (single rotation at minimum speed). Confirm all rolls rotate freely (JSR.CC1.SEG07.ROLL.RPM should register).
31. Verify spray cooling flow: open cooling water to zone, confirm JSR.CC1.SEG07.SPRAY.FLOW is 180–220 L/min (normal range).
32. Remove all LOTO. Notify caster operator that Segment 7 is available.

### Phase E — First Heat After Maintenance

33. Run first heat at 60–70% of normal casting speed for the first 15 minutes with enhanced monitoring. [unverified]
34. Monitor JSR.CC1.SEG07.ROLL.RPM continuously — confirm all rolls rotating at expected speed.
35. Monitor JSR.CC1.SEG07.FORCE.HYD — normal range 200–400 kN. Any sustained value above 400 kN: notify metallurgist.
36. Inspect slab surface after first heat for transverse cracks — confirm no periodic marking.

---

## 7. ACCEPTANCE CHECKS

| Parameter | Acceptance Criterion | Instrument |
|-----------|---------------------|------------|
| Roll rotation (all rolls) | Rotates freely by hand after repair; ROLL.RPM registers > 3 rpm during casting | Physical check + JSR.CC1.SEG07.ROLL.RPM |
| Segment gap | Within ± 0.3 mm of format specification [unverified] | Feeler gauge + OEM fixture |
| Cooling water flow | 180–220 L/min (normal range) | JSR.CC1.SEG07.SPRAY.FLOW |
| Clamping force | 200–400 kN (normal range) during first heat | JSR.CC1.SEG07.FORCE.HYD |
| Cooling circuit pressure test | Zero leakage at 1.5 × WP | Pressure gauge |
| Strand bulge (first heat) | < 1.0 mm (normal range: 0.0–1.0 mm) | JSR.CC1.SEG07.BULGE |
| Roll bearing vibration (first heat) | < 2.0 mm/s (normal range) | JSR.CC1.SEG07.VIB.ROLL |
| Slab surface quality | No transverse cracks at roll pitch | Slab surface inspection |

---

## 8. TIME ESTIMATE

| Scenario | TTR |
|----------|-----|
| Single segment change (planned maintenance window) | 4–8 h after strand clears + 2–4 h cooling |
| Emergency segment change (unplanned, SCN-042 basis) | 8 h unplanned (spine SCN-042 value) |
| Segment repair bay work (bearings + nozzles + geometry) | 6–12 h (can parallel with caster downtime) |

*(SCN-042 spine: unplanned downtime 8 h, cost USD 96 000)*

---

## 9. RECURRENCE PREVENTION

- **Roll bearing lubrication:** Ensure grease/water lubrication purge system for segment roll bearings is operational — bearings in this segment zone are subject to severe water and scale ingress. Purge frequency per SMS Concast specification. [unverified]
- **Cooling water quality:** Scale deposits in spray nozzles are the primary nozzle blockage cause. Implement water treatment (scale inhibitor) and nozzle pressure-test every heat-end inspection.
- **Segment exchange program:** Replace segments on a planned ton-count or heat-count schedule (typically every 2 000–4 000 heats depending on steel grade and casting speed — confirm with metallurgy). This converts unplanned emergency pulls into planned maintenance.
- **Roll seizure root cause:** After every seized roll event, perform 5-whys RCA within 48 h. Common causes: inadequate lubrication purge, thermal overload from casting speed increase during tundish change, scale ingress from inadequate spray nozzle coverage.
- **Condition monitoring:** Install roll-rotation encoders on all critical segments (if not already present) — RPM = 0 at any point during a heat is an immediate casting-speed reduction trigger, not just an alarm to log.
