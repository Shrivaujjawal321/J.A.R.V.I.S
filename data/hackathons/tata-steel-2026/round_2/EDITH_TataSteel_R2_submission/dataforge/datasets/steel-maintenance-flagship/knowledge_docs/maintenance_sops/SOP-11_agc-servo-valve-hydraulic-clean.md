# SOP-11 — AGC Servo-Valve Cleaning and Hydraulic Oil Remediation
## TATA_JSR Maintenance Standard Operating Procedure

**Document ID:** SOP-11  
**Revision:** 1.0  
**Effective Date:** 2026-06-09  
**Equipment Class:** hydraulics_agc_servo  
**Primary Asset Reference:** CRM.AGC.SV01  
**Trigger Failure Modes:** servo_valve_silting_spool_wear | servo_valve_hysteresis_increase | hydraulic_oil_contamination  
**Spine Scenario Reference:** SCN-048 (CRM.AGC.SV01 — servo_valve_silting_spool_wear; ISO4406 17/15/12, position error 3.2 %, gauge deviation 22 µm)  
**Standard:** ISO 4406:2021 (hydraulic fluid cleanliness) | Moog D661 servo-valve service manual [unverified] | ISO 4413 (hydraulic safety)  
**Safety Class:** P2 (AGC loss → strip gauge excursion → cobble risk)  
**Disclaimer:** SYNTHETIC procedure grounded in research/machinery/07, /17, /18, /19. Values tagged [unverified] are industry estimates. CRM.AGC.SV01 is a Moog D661 servo valve. All bench cleaning and null-trim work must be performed by a trained hydraulic specialist — servo valves with 1–3 µm clearances are destroyed by contamination, incorrect tools, or incorrect assembly.

---

## 1. SCOPE

This SOP covers:
1. **Servo valve removal and ultrasonic bench cleaning** — triggered when ISO 4406 code degrades to 16/14/11 or position error rises above 1.5 %.
2. **Servo valve replacement** — triggered by alarm condition or bench inspection finding spool scoring.
3. **Hydraulic oil system remediation** — mandatory alongside any servo valve work; kidney-loop filtration to restore oil cleanliness.

**CRM.AGC.SV01 function:** Precision screwdown position control for Cold Rolling Mill Stand 2 Automatic Gauge Control. Loss of AGC causes gauge excursions on the rolled strip — product rejection, potential strip break (cobble). This asset justifies immediate response to any condition indicator.

---

## 2. SAFETY / LOTO

> **Servo hydraulic circuits operate at 200–350 bar. High-pressure hydraulic oil injection injury is a surgical emergency — do not allow any connection/disconnection while pressure is present.**

| Step | Action |
|------|--------|
| S-1 | Switch AGC to backup position lock mode (or manual screwdown) via HMI — notify rolling mill operator |
| S-2 | Stop cold rolling mill. Confirm strip is coiled and mill drives are stopped |
| S-3 | Isolate hydraulic supply to CRM Stand 2 AGC circuit: close hydraulic isolation valve at HPU; lock in CLOSED position |
| S-4 | Open circuit relief valve or bleed nipple to release pressure to zero. **Verify pressure gauge reads 0 bar on the servo circuit before any connection work.** Wait minimum 60 seconds after valve close for pressure to decay via accumulators |
| S-5 | Isolate servo-valve electrical supply: disconnect servo-valve driver amplifier connector |
| S-6 | Apply personal lock + danger tag at hydraulic isolation valve and electrical panel |
| S-7 | Post "AGC SERVO MAINTENANCE — MILL INHIBITED" on mill HMI |
| S-8 | Confirm LVDT (linear variable differential transformer) signal is de-energised |

**PPE Minimum:** Safety helmet, steel-toe boots, cut-resistant gloves, safety glasses, face shield for hydraulic connection work (residual pressure risk). For ultrasonic bench cleaning: chemical splash goggles, nitrile gloves, solvent-resistant apron.

---

## 3. TRIGGER CONDITIONS

| Sensor Tag | Threshold | Action |
|-----------|-----------|--------|
| JSR.CR.S2.AGC.SV.ISO4406 | 16/14/11 (warning) | Increase sampling to daily; prepare for valve service |
| JSR.CR.S2.AGC.SV.ISO4406 | 17/15/12 (alarm — SCN-048 condition) | Schedule servo valve clean within 48 h |
| JSR.CR.S2.AGC.SV.POSERR | > 1.5 % (warning) | Investigate servo valve response; check oil cleanliness |
| JSR.CR.S2.AGC.SV.POSERR | > 3.0 % (alarm — SCN-048: 3.2 %) | Immediate AGC switch to backup; plan servo valve change |
| JSR.CR.S2.AGC.SV.NULLLEAK | > 1.0 L/min (warning) | Spool wear / silt bypass; plan replacement |
| JSR.CR.S2.AGC.SV.NULLLEAK | > 2.0 L/min (alarm) | Replace valve |
| JSR.CR.S2.AGC.GAUGE.DEV | > 10 µm (warning) | Investigate AGC loop stability |
| JSR.CR.S2.AGC.GAUGE.DEV | > 20 µm (alarm — SCN-048: 22 µm) | AGC loss; emergency servo valve replacement if backup not available |
| SCADA: AGC position hunting / oscillation | Visible hunting on small commands | Leading sign of silting; check ISO 4406 |
| Filter DP on servo circuit | > 3.0 bar (warning) | Replace filter elements (FLT-SERVO-3) — do not wait for alarm |

---

## 4. TOOLS AND EQUIPMENT

| Item | Specification |
|------|--------------|
| Hydraulic test bench | Servo-valve test capability: regulated pressure supply, flow measurement, step-response test fixture |
| Ultrasonic cleaner | 40 kHz, suitable for precision components; clean solvent (petroleum spirit or OEM-approved servo cleaning fluid) |
| Clean-room bench | Dust-free, ideally in dedicated hydraulic workshop — not near grinding, cutting, or welding operations |
| Precision milliamp calibrator | For null-trim adjustment (0–25 mA range, resolution 0.1 mA) |
| ISO 4406 particle counter (portable) | HYDAC or MP Filtri — on-site oil cleanliness measurement |
| Kidney-loop filtration unit (KID-LOOP-01) | Portable, 3 µm absolute filter, circulation pump |
| Torque screwdriver | Servo valve manifold bolt torque — low torque range (5–25 Nm typical) [unverified] |
| Wire number tags | Tag all servo-valve electrical connectors before removal — essential for correct reconnection |
| OEM service manual | Moog D661 disassembly/reassembly procedure — mandatory reference |
| Clean plastic bags / zip-locks | For sealing all ports immediately on servo valve removal |

---

## 5. SPARES REQUIRED

| Part ID | Description | Stock Qty | Lead Time |
|---------|-------------|-----------|-----------|
| SERVO-VLV-D661 | Moog D661 servo valve | 1 on shelf | 10 weeks if OOS |
| FLT-SERVO-3 | Servo filter element 3 µm absolute | 4 on shelf | In stock |
| FLT-HYD-10 | Hydraulic filter element 10 µm | 6 on shelf | In stock |

> **SERVO-VLV-D661 has 10-week lead time if OOS. The 1 on-shelf spare is the margin. When the spare is used, immediately raise a replacement procurement order — do not wait until the next occurrence.**

---

## 6. NUMBERED PROCEDURE STEPS

### Phase A — Pre-Work Oil Sampling

1. Before removing servo valve: take a sealed hydraulic oil sample from the servo circuit return line using the sample valve. Label with date, asset ID (CRM.AGC.SV01), and work order.
2. Test sample immediately on portable particle counter. Record ISO 4406:2021 code.
3. Send a separate sample to the external oil analysis laboratory for acid number, viscosity at 40 °C, and water content (Karl Fischer). Contaminated oil (acid > 0.5 mgKOH/g or water > 200 ppm) requires a full oil change, not just kidney-loop filtration.

### Phase B — Servo Valve Removal

4. Confirm AGC is on backup/manual position lock per S-1. Confirm mill is stopped per S-2.
5. Apply LOTO per Section 2. Verify circuit pressure = 0 bar on gauge.
6. Tag all electrical connectors on servo valve driver with wire numbers (photograph connections before disconnecting).
7. Disconnect all electrical connectors from servo valve. Cap connectors with lint-free cloth or clean plugs.
8. Unfasten servo valve manifold bolts using torque screwdriver. Record bolt positions.
9. Carefully lift servo valve from manifold (hold upright to prevent debris entering ports).
10. **Immediately seal all 4 hydraulic ports on the removed servo valve with clean plastic caps.** Also seal the matching ports on the manifold.
11. Seal the manifold ports on the circuit to prevent contamination entry during the valve-off period.
12. Transport servo valve to clean hydraulic workshop in a sealed bag.

### Phase C — Option A: Bench Cleaning (if spool shows no scoring)

13. In clean-room bench, open servo valve per Moog D661 service manual. Fully disassemble spool, sleeve, nozzle-flapper components, and torque motor assembly.
14. Ultrasonically clean all components in filtered petroleum spirit (or OEM-approved servo cleaning solvent). Ultrasonic time: 5–10 min per component. Rinse with clean solvent.
15. Inspect spool OD and sleeve bore under ×20 magnification. Measure clearance between spool and sleeve using a calibrated air gauge or precision micrometers.
    - **Acceptable spool-sleeve clearance: OEM specification (typically 1–3 µm total diametral clearance).** [unverified — confirm from Moog D661 drawing]
    - Any scoring visible under magnification = REPLACE VALVE (proceed to Option B).
16. Inspect nozzle flapper gap and nozzle seat for deposit buildup. Clean with lint-free swab and solvent.
17. Reassemble per Moog D661 service manual in clean-room conditions. Torque all fasteners to OEM specification.
18. Test on hydraulic test bench:
    - Apply rated working pressure
    - Command ± 100 % of full stroke; measure response time and hysteresis — must match Moog D661 datasheet values [unverified]
    - Null test: at zero current, spool must return to null (< 1 % of full stroke drift). [unverified]
    - Measure null leakage: must be < 1.0 L/min (warning threshold of JSR.CR.S2.AGC.SV.NULLLEAK). [unverified]
19. If bench test passes: proceed to Phase D (reinstallation).
20. If bench test fails: replace valve (Option B).

### Phase C — Option B: Servo Valve Replacement

21. Remove SERVO-VLV-D661 (spare) from controlled storage. Verify part number matches removed valve. Check OEM specification sheets match the current application (null offset, rated flow, pressure rating).
22. Flush the manifold with clean hydraulic oil (ISO VG 46 HM) before installing new valve — prevents debris from manifold contaminating the new valve immediately on installation.
23. Remove plastic port caps from new valve and manifold simultaneously (absolute minimum air exposure).
24. Fit new valve to manifold. Torque manifold bolts in cross-pattern to OEM specification.

### Phase D — Oil System Remediation (mandatory with any servo valve work)

25. Replace all servo circuit filter elements: FLT-SERVO-3 (3 µm absolute) and FLT-HYD-10 (10 µm) — replace all elements whether or not DP alarm was active.
26. Connect portable kidney-loop filtration unit (KID-LOOP-01) to the servo circuit reservoir via sampling ports. Set circulation at maximum rated flow for KID-LOOP-01.
27. Circulate for minimum 4 h before returning valve to service. Measure ISO 4406 code at 1 h intervals. Continue kidney-loop until cleanliness reaches target: **ISO 4406 ≤ 15/13/10.**
28. If cleanliness is not recovering toward target after 8 h of kidney-loop: the oil itself may be oxidised or heavily contaminated — drain and replace entire servo circuit oil charge.

### Phase E — Servo Valve Reinstallation and Commissioning

29. Reconnect all electrical connectors per wire-number tags recorded at Step 6. Verify each connector is in correct position by cross-checking with photograph.
30. Remove LOTO from electrical supply: reconnect servo driver amplifier.
31. Remove LOTO from hydraulic supply: slowly open hydraulic isolation valve (crack open 10% first to check for leaks before full open).
32. Verify pressure builds on circuit gauge to 200–350 bar operating range.
33. **Null trim calibration:** command zero current to servo valve; observe cylinder position (via LVDT). If cylinder drifts from set position under zero current: adjust null-trim pot on the servo driver amplifier until drift is < 0.1 % of stroke. [unverified — follow Moog driver amplifier calibration procedure]
34. **Step-response test:** command ±50 % of full stroke at 1 Hz on the test bench or in the mill with the drive offline. Response time and overshoot must match OEM datasheet (Moog D661 typical -3 dB bandwidth ~100 Hz at rated pressure). [unverified]
35. Inform mill operator: AGC servo valve replaced/cleaned; ready for production.
36. Return AGC from backup to active control.
37. Run the first strip under AGC control. Monitor JSR.CR.S2.AGC.GAUGE.DEV for first 5 min (normal: < 5 µm deviation). If gauge oscillation is observed: stop mill; re-check null trim.
38. Take oil sample at 4 h after return to service. Target: ISO 4406 ≤ 15/13/10. File in CMMS.

---

## 7. ACCEPTANCE CHECKS

| Parameter | Acceptance Criterion | Instrument |
|-----------|---------------------|------------|
| ISO 4406 servo circuit oil | ≤ 15/13/10 (normal range) | Portable particle counter |
| POSERR | ≤ 0.5 % (normal range: 0.0–0.5 %) | JSR.CR.S2.AGC.SV.POSERR |
| NULLLEAK | ≤ 0.5 L/min (normal range) | JSR.CR.S2.AGC.SV.NULLLEAK |
| GAUGE.DEV (first strip) | ≤ 5 µm (normal range: -5 to +5 µm) | JSR.CR.S2.AGC.GAUGE.DEV |
| Null drift (zero current command) | < 0.1 % of full stroke | LVDT feedback signal |
| Cylinder drift (brake static) | Zero drift at null command | LVDT trend |
| Step response | Within Moog D661 OEM datasheet [unverified] | Hydraulic test bench oscilloscope |
| Filter elements (all) | Replaced; DP at new baseline | JSR filter DP tags |

---

## 8. TIME ESTIMATE

| Scenario | Planned TTR | Unplanned TTR |
|----------|-------------|---------------|
| Valve removal + bench clean + reinstall | 4–8 h | Same |
| Valve replacement (spare in stock) | 2–4 h | 6 h (SCN-048 basis) |
| Kidney-loop to target cleanliness | 4–8 h (concurrent with above) | Same |
| Valve procurement if spare OOS | — | 10 weeks |

*(SCN-048 spine: planned 2 h, unplanned 6 h; cost USD 137 700 from cobble + gauge scrap)*

---

## 9. RECURRENCE PREVENTION

- **The single most effective measure:** Maintain servo circuit oil continuously at ISO 4406 ≤ 15/13/10 using kidney-loop filtration with 3 µm absolute filter on the servo circuit reservoir. Most silting problems disappear entirely with this one measure. Most steel plants install permanent kidney-loop units on all servo circuits. [unverified]
- **Automated inline particle counters:** Install HYDAC or MP Filtri inline particle counters (JSR.CR.S2.AGC.SV.ISO4406) with SCADA integration to give real-time oil cleanliness — weekly manual sampling is too infrequent to catch the 1–2 week build-up window.
- **System flush after any hydraulic event:** Any hydraulic cylinder seal failure, hose rupture, or system contamination event must trigger a full circuit flush before return to service. Debris from these events contaminates the servo circuit within hours.
- **Accumulator bladder inspection:** Annual inspection of all accumulator bladders in the servo circuit. Failed bladders inject nitrogen into the circuit — gas in servo circuits causes erratic step-response.
- **Oil change on condition:** Change servo circuit oil based on condition (acidity, viscosity, water content) not on fixed calendar interval. Water ingress from cooling circuit leaks (common in steel plant environments) is a primary contamination mechanism.
