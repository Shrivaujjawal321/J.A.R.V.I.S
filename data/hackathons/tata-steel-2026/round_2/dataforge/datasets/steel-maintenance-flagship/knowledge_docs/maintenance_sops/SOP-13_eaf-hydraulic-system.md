# SOP-13 — EAF Auxiliary Hydraulic System: Oil Cleanliness and Filter Remediation
## TATA_JSR Maintenance Standard Operating Procedure

**Document ID:** SOP-13  
**Revision:** 1.1  
**Effective Date:** 2026-06-09  
**Equipment Class:** eaf_bof_auxiliary  
**Primary Asset Reference:** EAF.AUX.HYD01 (EAF auxiliary hydraulic power unit)  
**Trigger Failure Modes:** oil_contamination_particulate | oil_water_contamination | filter_clog (per EAF.AUX.HYD01 asset-registry failure_modes)  
**Spine Scenario Reference:** SCN-049 (EAF.AUX.HYD01 — filter_clog; FILT.DP 1.0 → 4.5 bar bypass threshold). NOTE: the spine contains no FAILURE scenario for oil_contamination_particulate or oil_water_contamination on this asset; Parts A and B below are condition-based / preventive procedures keyed to the EAF.AUX.HYD01 asset-registry failure_modes and sensor thresholds, NOT to any spine FAILURE scenario.  
**Standard:** ISO 4406:2021 (hydraulic fluid cleanliness) | ISO 23309:2017 (hydraulic flushing) | EN 982:2009 (hydraulic safety) | ISO 4413:2010 (general hydraulic safety requirements)  
**Safety Class:** P4 (per SCN-049 / asset registry; condition-based monitoring with planned remediation — no in-heat actuator-failure event modelled in the spine)  
**Disclaimer:** SYNTHETIC procedure grounded in research/machinery/07 (hydraulic & pneumatic systems), /16, /18, /19 (Playbook 07). Values tagged [unverified] are industry estimates. EAF.AUX.HYD01 is a Bosch Rexroth 350 bar hydraulic power unit serving the Electric Arc Furnace auxiliary actuators (electrode regulation, roof lift, tilt drive, door mechanisms). Confirm exact valve and actuator pressure ratings from Bosch Rexroth OEM documentation.

---

## 1. SCOPE

**Part A — Particulate Contamination / Filter Remediation (condition-based; covers asset failure_modes `oil_contamination_particulate` and `filter_clog`, spine FAILURE scenario SCN-049):** Restoration of hydraulic oil cleanliness from a warning/alarm ISO4406 code back to ≤ 17/15/12 (normal band) using offline kidney-loop filtration and/or oil change, plus filter element replacement on filter differential-pressure alarm. The filter-clog path (FILT.DP rising toward the 4.5 bar bypass threshold) corresponds to spine scenario SCN-049.

**Part B — Water Contamination Response (condition-based; covers asset failure_mode `oil_water_contamination`):** Investigation and elimination of water ingress into hydraulic oil (WATER.PPM warning 200 ppm / alarm 500 ppm). Identification of ingress source (water-cooled component failure, condensation, or fill-port contamination). Oil reclamation or replacement.

**Systems covered:** EAF.AUX.HYD01 hydraulic power unit and all servo/proportional valve circuits it serves (electrode regulation, roof lift, tilt, door).

**Out of scope:** Hydraulic cylinder seal replacement (covered conceptually in SOP-04), servo valve bench service (see SOP-11 for methodology; apply same principles to any EAF servo/proportional valves).

---

## 2. SAFETY / LOTO

| Step | Action |
|------|--------|
| S-1 | Confirm with EAF shift manager: EAF in safe state — no heat in progress, electrodes parked, all actuators in their safe/neutral positions, and furnace tilted back to rest position |
| S-2 | Isolate and lock hydraulic pump motor (MCC — Lock Out, Tag Out, Try Out). Verify pump has stopped on SCADA and that system pressure at the local HPU gauge falls to tank pressure (≈ 0 bar) within 30 s |
| S-3 | Depressurise system: open manual drain valve at accumulator bank to relieve stored pressure. Verify the local system pressure gauge reads 0 bar before any line or component disconnection. |
| S-4 | For any component removal: tag all hose ends before disconnection. Cap immediately with clean plastic plugs to prevent contamination ingress and oil spillage |
| S-5 | This HPU operates at up to 350 bar. Do not rely on pump stop alone — verify zero pressure at the local gauge before touching any fitting |
| S-6 | Oil spillage: EAF environment has molten metal splash risk. Hydraulic oil spillage near hot furnace components is a serious fire hazard. Use drip trays, oil-absorbent mats; do not allow oil on furnace structure |

**PPE Minimum:** Safety helmet, heat-resistant boots, safety glasses, oil-resistant gloves. High-pressure hydraulic injection risk: treat any suspected pinhole leak with extreme caution — do not test with bare skin; use paper/card to detect leaks.

---

## 3. TRIGGER CONDITIONS

| Sensor Tag | Normal Range | Warning | Alarm | Notes |
|-----------|-------------|---------|-------|-------|
| JSR.MS.EAF1.HYD.ISO4406 | ≤ 17/15/12 | 18/16/13 | 19/17/14 | Particle count (ISO 4406:2021) |
| JSR.MS.EAF1.HYD.OIL.TEMP | 40–50 °C | 60 °C | 70 °C | High temp accelerates oxidation/varnish |
| JSR.MS.EAF1.HYD.FILT.DP | 0.0–1.5 bar | 3.0 bar | 4.5 bar | 4.5 bar = element blinding / bypass risk (SCN-049 filter_clog) |
| JSR.MS.EAF1.HYD.WATER.PPM | 0–100 ppm | 200 ppm | 500 ppm | Free/emulsified water risk above alarm |

---

## 4. TOOLS AND EQUIPMENT

| Item | Specification |
|------|--------------|
| Portable kidney-loop filtration unit | KID-LOOP-01: 3 µm absolute, ≥ 20 L/min flow |
| Oil sampling syringe + ISO-clean bottles | For lab particle count (ISO 4406) sample at mid-tank |
| Karl Fischer titrator (or lab service) | For water content measurement (ppm) |
| Vacuum dehydration unit (if available) | For water removal from oil without full change [unverified] |
| Portable oil heater | Pre-heating replacement oil to ≥ 40 °C before fill (reduces moisture condensation) |
| Clean ISO-level oil transfer cart | Must be rated to the target cleanliness level (≤ 17/15/12) |
| Torque wrench | Filter housing and port refitting |
| Oil pan / drip tray (large) | Full system capacity: confirm tank volume from EAF HPU nameplate |

---

## 5. SPARES REQUIRED

| Part ID | Description | Stock Qty | Lead Time |
|---------|-------------|-----------|-----------|
| FLT-HYD-10 | Main system filter element (10 µm) | 6 on shelf | 2 weeks if OOS |
| FLT-SERVO-3 | Fine servo-circuit filter element (3 µm) | 4 on shelf | 2 weeks if OOS |
| KID-LOOP-01 | Kidney-loop unit (portable 3 µm) | 1 on shelf | Rental if OOS |
| OIL-HYD-ISO46 | ISO VG 46 hydraulic oil, anti-wear | Bulk (confirm tank volume) | 1 week standard |

*(Note: FLT-HYD-10 is the spine-registered element for EAF.AUX.HYD01 (SCN-049 spares). FLT-HYD-10 and FLT-SERVO-3 are common filter part IDs shared with the CRM.AGC hydraulic system across the site.)*

---

## 6. NUMBERED PROCEDURE STEPS

### PART A — Particulate Contamination / Filter Remediation (asset failure_modes oil_contamination_particulate, filter_clog; spine SCN-049)

**Assessment and Triage**
1. On JSR.MS.EAF1.HYD.FILT.DP alarm (4.5 bar — SCN-049 bypass threshold): do NOT rely on the filter bypass. The bypass is a last-resort anti-cavitation protection for the pump — oil that bypasses a blinded filter carries full contamination load to all downstream valves. Treat filter DP alarm as a production-pause trigger and plan filter replacement.
2. Collect oil sample using ISO-clean sampling syringe from the tank drain port or dedicated sample port (not from the fill port — fill port samples are not representative of circulating oil). Send to lab for ISO 4406 particle count and visual assessment. If the lab confirms ≥ 19/17/14 (alarm): proceed with full service.
3. If ISO4406 = 18/16/13 (warning only): start kidney-loop filtration; do not shut system down yet. Monitor DP and temperature. Re-sample after 48 h kidney-loop.

**Shut Down and LOTO (if proceeding to full service)**
4. Apply LOTO per safety steps S-1 through S-6. Confirm 0 bar system pressure.

**Filter Replacement (SCN-049 correct_resolution)**
5. Locate main system filter housing(s). Note: EAF hydraulic systems often have multiple filter stages — a coarse suction strainer (at pump inlet), a pressure-line filter (after pump), and a return-line filter (tank return). All stages should be serviced simultaneously if contamination has reached the alarm band (19/17/14) or FILT.DP has hit 4.5 bar.
6. Place drip tray under filter housing. Unscrew filter housing. Remove used filter element (FLT-HYD-10 or FLT-SERVO-3 as applicable). Place used element in a sealed waste bag for lab analysis if root cause is unclear — filter debris pattern can confirm particle origin.
7. Inspect filter housing bowl for sludge, varnish, or water pooling. If sludge or varnish is heavy: wipe housing clean with lint-free cloth wetted with the same grade of hydraulic oil (not solvent — solvent residue damages seals).
8. Install new filter element (FLT-HYD-10 / FLT-SERVO-3). Verify O-ring is correctly seated. Torque housing cap to manufacturer's specification.
9. Replace servo-circuit fine filter (FLT-SERVO-3) — alarm-band particulate (19/17/14) means fine valves have been exposed to contamination beyond their rating.
9a. Clean the suction strainer and fit a fresh desiccant breather to stop continued EAF dust ingress (SCN-049 root cause: filter blinding from systematic EAF dust ingress via breather).

**Kidney-Loop Offline Filtration**
10. Connect KID-LOOP-01 kidney-loop unit to the tank — use the dedicated kidney-loop connection ports (bottom inlet, top return), never T off the main pressure lines.
11. Start kidney-loop at low flow initially (5–10 L/min) for first 15 min, then increase to rated flow (20 L/min). This avoids dislodging a large slug of settled particulate into the circuit at once.
12. Run kidney-loop for minimum 8 h. For the target transition from the alarm band (19/17/14) back to normal (≤ 17/15/12): expect 24–72 h kidney-loop time depending on tank volume and contamination severity. [unverified]
13. Resample oil every 8 h and submit for ISO 4406 count. Continue kidney-loop until two consecutive samples show ≤ 17/15/12.

**Temperature Investigation (OIL.TEMP warning 60 °C / alarm 70 °C)**
14. Abnormal oil temperature (> 60 °C warning) indicates either: (a) cooler fouling, (b) excess leakage (internal or external — leakage flow converts pressure energy to heat), or (c) pump wear (slip path heat). Check cooling water flow to oil cooler — confirm flow is normal on SCADA or physically check.
15. If cooling water flow is confirmed normal but temperature remains elevated (toward the 70 °C alarm): suspect internal pump or valve bypass (wear-related excessive internal leakage). This requires vibration + delivery flow measurement. Log for investigation at next planned outage.

**Return to Service**
16. Remove LOTO. Start pump. Cycle all actuators (electrode regulation, roof, tilt, door) through full travel 3 × with no load. This circulates filtered oil through all valve bodies and actuator lines.
17. Verify JSR.MS.EAF1.HYD.FILT.DP returns to the 0.0–1.5 bar normal range within 30 min of startup (SCN-049 acceptance: DP < 1.5 bar on restart).
18. Resample oil after 2 h running. Confirm ISO4406 ≤ 17/15/12.
19. Record completed work in CMMS: filter part numbers installed, oil samples + ISO4406 results, kidney-loop duration, and all sensor readings at return to service.

---

### PART B — Water Contamination Response (asset failure_mode oil_water_contamination)

**Water Ingress Investigation**
20. Confirm water presence: if lab Karl Fischer confirms water content > 200 ppm (warning), proceed with investigation; treat ≥ 500 ppm (alarm) as the action threshold. Visual check: sample settled in clear glass — free water appears as a cloudy lower layer or as a milky oil if emulsified.
21. At ≥ 500 ppm water (alarm): oil emulsification is likely — the oil will appear milky/hazy rather than clear amber. Emulsified water dramatically reduces the oil film strength; bearing and valve wear accelerates rapidly.
22. Identify the water ingress source — this is the critical step; without fixing the root cause, any remediation is temporary:
    - **Water-cooled bearing or heat exchanger failure:** pressure test water-side circuits while system is at operating pressure. A drop in water pressure (or oil contamination appearing in cooling water) confirms the source.
    - **Condensation (external humidity ingress):** common in systems that cycle between hot operating temperature and cold ambient. Check tank breather — is the desiccant breather saturated (silica gel turned pink)?
    - **Fill-port contamination:** was the last oil fill performed with contaminated oil or using un-clean fill equipment? Check fill port area for evidence.
    - **Cylinder rod seal failure with external water wash-down contact:** EAF environments have heavy water wash-down. If a rod seal is failing, wash-down water can enter the cylinder and migrate to tank.
23. Fix the water ingress source before performing oil remediation — otherwise the tank will recontaminate.

**Mild Contamination (200–500 ppm, no emulsification): Vacuum Dehydration**
24. If vacuum dehydration unit is available: connect to tank and run per manufacturer's procedure. Vacuum dehydration removes water without discarding the oil. Effective for non-emulsified dissolved/free water. [unverified]
25. Run until Karl Fischer confirms water content < 100 ppm. Resample at 12 h intervals.

**Severe Contamination (≥ 500 ppm, emulsified): Oil Change**
26. Pump out all existing oil from tank using a clean transfer pump and waste drums. Do not allow contaminated oil to drain to ground — collect for proper disposal.
27. Flush tank interior: add a small volume (5–10 % of tank capacity) of clean fresh oil of the same grade. Circulate through all lines using pump (with blanked actuator connections to prevent contamination spread into actuators). Drain flush oil to waste.
28. Inspect tank interior: wipe down with lint-free cloth. Check for sludge deposits. If heavy sludge: clean by hand before filling with new oil.
29. Change all filter elements: FLT-HYD-10 and FLT-SERVO-3.
30. Fill with fresh ISO VG 46 hydraulic oil from pre-verified clean drums (confirm the delivery oil is ≤ 17/15/12 ISO4406 or better before filling — do not assume new oil is clean). Pre-heat oil to 40 °C before filling if ambient temperature is < 15 °C.
31. Start pump. Circulate and cycle all actuators. Resample at 2 h and 8 h. Confirm ISO4406 ≤ 17/15/12 and water content < 100 ppm before declaring RTS.

---

## 7. ACCEPTANCE CHECKS

| Parameter | Acceptance Criterion | Instrument |
|-----------|---------------------|------------|
| JSR.MS.EAF1.HYD.ISO4406 (post-service) | ≤ 17/15/12 (2 consecutive samples) | ISO 4406 lab analysis |
| JSR.MS.EAF1.HYD.WATER.PPM (post-service) | < 100 ppm (normal range) | Karl Fischer titration |
| JSR.MS.EAF1.HYD.FILT.DP (post-service) | 0.0–1.5 bar (normal range) within 30 min of startup | SCADA |
| JSR.MS.EAF1.HYD.OIL.TEMP (post-service) | 40–50 °C (normal range) at steady state | SCADA |
| Actuator functional test | All actuators (electrode regulation, roof, tilt, door) complete full stroke without hesitation, abnormal noise, or pressure excursion | Operator check + SCADA |
| Root cause of water ingress | Identified and fixed (or planned fix confirmed) | Maintenance work order |

---

## 8. TIME ESTIMATE

| Scenario | Planned TTR | Notes |
|----------|-------------|-------|
| Filter replacement + kidney-loop initiation (Part A — filter_clog SCN-049) | 4 h work, 24–72 h kidney-loop running time | Kidney-loop runs continuously; system can return to service while kidney-loop continues |
| Oil change (Part B — water contamination ≥ 500 ppm) | 8–16 h | Depends on tank volume |
| Root-cause investigation (water ingress) | 2–8 h additional | May require pressure testing of water-cooled components |

*(SCN-049 spine: planned TTR 4 h, unplanned 4 h, cost INR 200,000 / USD 2,395, safety class P4. No spine FAILURE scenario exists for the particulate or water failure_modes, so Parts A/B costs are not spine-anchored.)*

---

## 9. RECURRENCE PREVENTION

- **Monthly oil sampling programme:** Implement routine monthly ISO 4406 sampling from EAF.AUX.HYD01 as a CMMS-scheduled PM task. Trending from ≤ 17/15/12 toward 18/16/13 gives several weeks warning before reaching the 19/17/14 alarm level.
- **Desiccant breather maintenance:** Replace tank desiccant breather when silica gel is > 50 % saturated (pink). In EAF environments with temperature cycling, steam, and dust ingress, this may be quarterly or more frequent (SCN-049 root cause is dust ingress via a saturated/failed breather).
- **Kidney-loop as standard PM:** Run KID-LOOP-01 for 8 h per month on EAF.AUX.HYD01 as a PM action. This keeps the cleanliness baseline low and extends filter life significantly.
- **Tighten filter PM cadence after a filter_clog event:** Per SCN-049 correct_resolution, move filter-element PM to a weekly cadence after a blinding event until DP trend stabilises.
- **Water-cooled component monitoring:** Add water-side pressure trend monitoring to all heat exchangers and water-cooled bearings served by EAF.AUX.HYD01. A sudden pressure drop is a leading indicator of tube failure — far earlier than water appearing in the oil.
- **Fill discipline:** Only fill hydraulic oil from sealed clean drums. Use a dedicated clean fill cart with a 10 µm in-line fill filter. Never fill from an open drum. Train all operators on this — fill contamination is one of the most common causes of rapid system contamination.
- **Crosslink with SOP-11:** The kidney-loop filtration methodology and ISO 4406 acceptance criteria here are consistent with SOP-11 (CRM.AGC servo system). KID-LOOP-01 can serve both systems on rotation — keep scheduling coordinated.
