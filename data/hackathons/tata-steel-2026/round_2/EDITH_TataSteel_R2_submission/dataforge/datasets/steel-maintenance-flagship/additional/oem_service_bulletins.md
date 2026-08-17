# OEM Service Bulletins — TATA_JSR (Synthetic)
# Covers equipment classes present in ground_truth_spine.json v1.0.0
# SYNTHETIC — technically accurate; NOT real OEM documents
# Format mirrors industry-standard field service bulletins (FSB) / service information letters (SIL)

---

## FSB-SKF-2024-001
**OEM:** SKF
**Applies To:** `HSM.F3.WR.BRG01` — Oil-film bearing + 4-row cylindrical roller neck bearing (rolling_mill_work_roll_bearing)
**Subject:** Revised outer-race fatigue life expectancy under contaminated lube conditions; BPFO envelope alarm threshold guidance
**Severity:** Advisory
**Date:** 2024-09-15
**Ref Standard:** ISO 15243:2017 (rolling bearing failure modes)

### Background
Field data from hot-strip mill applications globally shows that oil-film bearing outlet temperatures (sensor: `JSR.HR.STD3.WR.BRG01.OFB.OUT.TEMP`) above 72 °C sustained for >4 hours correlate with a 3× acceleration of outer-race fatigue initiation in the associated roller neck bearing. The current alarm threshold of 85 °C (OFB outlet) captures severe events but misses this intermediate accelerated-wear regime.

### Action Required
1. **Update CMMS PM trigger:** Add conditional task: if `OFB.OUT.TEMP` exceeds 72 °C for ≥4 h, schedule envelope spectrum burst capture within 2 shifts.
2. **Verify lube cleanliness:** Target ISO 4406:2021 cleanliness ≤16/14/11 in OFB supply circuit. If Fe PPM in lube exceeds 3 ppm (per `JSR.HR.STD3.WR.BRG01.OFB.OUT.TEMP` correlation), initiate kidney-loop polishing.
3. **Stage spares proactively:** Ensure `BRG-LRG-300` is on-shelf (minimum 1 unit) at all times for mills using this bearing family. Lead time 8 weeks — re-order point = 0 units remaining.
4. **AE as leading indicator:** The `JSR.HR.STD3.WR.BRG01.AE.RMS` sensor is the earliest detectable precursor — typically crosses 6 dBuV warning 3–5 weeks before envelope BPFO alarm. Do not wait for VIB alarm before planning maintenance.

### NOT Required
No immediate shutdown warranted unless AE >12 dBuV AND BPFO >3.0 g simultaneously. Single-sensor warning is not a discard criterion.

---

## FSB-SKF-2024-002
**OEM:** SKF
**Applies To:** `HSM.F3.WR.BRG01` and general rolling-element bearing population (rolling_mill_work_roll_bearing)
**Subject:** Induction heating temperature protocol for large-bore bearing installation
**Severity:** Mandatory Practice
**Date:** 2024-11-20
**Ref Standard:** SKF installation guide [internal]; ISO 15243:2017 sec 5.1

### Background
Bearing inner-race overheating during installation (>120 °C) causes tempering of the raceway steel and reduces subsequent fatigue life by up to 30%. Field reports indicate inconsistent temperature monitoring during induction-heater mounting.

### Action Required
1. **Maximum installation temperature:** 110 °C for large-bore bearings >300 mm (part `BRG-LRG-300`). Do NOT exceed 120 °C at any point. Use calibrated contact or IR thermometer at inner race.
2. **Heating rate:** ≤30 °C/min to avoid thermal gradient-induced distortion.
3. **Journal surface:** Inspect journal for scoring >0.05 mm before fitting; regrind if necessary. Fit interference should be per OEM H7/k6 specification.
4. **Temperature verification:** Record installation temperature in CMMS. If >110 °C confirmed, flag bearing for enhanced early-life monitoring (reduce burst-capture interval to weekly for first 3 months).
5. **Labyrinth seal `SEAL-LAB-01`:** Replace at every bearing change — do not re-use worn seals.

---

## FSB-FLENDER-2023-007
**OEM:** Flender (Siemens)
**Applies To:** `HSM.F1.GBX01` — H4SH-mill drive gearbox (mill_gearbox)
**Subject:** Gear tooth fatigue crack detection via cepstrum rahmonics and chip detector co-validation
**Severity:** Alert
**Date:** 2023-08-10
**Ref Standard:** AGMA 9005-F16 [unverified]; ISO 10816

### Background
Laboratory testing and field failures in H4SH-class mill-drive gearboxes confirm that tooth-root fatigue cracks in the output pinion are not reliably detected by GMF band vibration alone until the crack is >2 mm depth (Stage 2). The combination of (a) rising cepstrum rahmonics and (b) chip-detector debris preceded tooth fracture by 4–8 weeks in 7 of 9 documented cases.

### Action Required
1. **Chip detector:** Install inline magnetic chip detector if not already fitted to `JSR.HR.STD1.GBX01.OIL` return line. Fragment threshold: ≥3 mm particle = immediate stop, borescope.
2. **Oil sampling frequency:** During periods when Fe count is >10 ppm (approaching warning 15 ppm), increase oil sampling to every 5 days (from monthly). If Fe >20 ppm, sample every 48 hours.
3. **Viscosity check:** High-torque cobble events can cause oil oxidation and viscosity drop. If `JSR.HR.STD1.GBX01.OIL.VISC` falls below 198 cSt (warning threshold per ISO 3448 VG220 −10%), drain and refill with fresh `OIL-VG220` immediately regardless of appearance.
4. **Borescope interval:** If any of the following: Fe >25 ppm, GMF >5.5 mm/s, chip-detector trip — schedule borescope within 72 hours.
5. **Spare gear wheel `GEAR-WHL-M20`:** Lead time 36 weeks; recommend carrying at minimum a partially-machined blank (18-week lead) as a standing order if mill is operating >8 years since last gear replacement.

### NOT Required
No immediate action if all parameters within normal range. Advisory only.

---

## FSB-FLENDER-2025-002
**OEM:** Flender (Siemens)
**Applies To:** `HSM.F1.GBX01`
**Subject:** Reduced-load operation protocol for Stage-1 gear-tooth crack
**Severity:** Engineering Guidance
**Date:** 2025-02-14

### Background
Following field cases where Stage-1 crack gearboxes were operated at full load to failure (resulting in >120 h downtime), Flender Engineering has developed a structured reduced-load protocol to extend safe operation pending emergency gear-wheel procurement.

### Protocol
1. **Confirm via borescope** that crack is Stage 1 (root initiation, no through-crack, no fragment generation).
2. **Maximum operating torque:** 65% rated. For `HSM.F1.GBX01` (6000 kW at 990 rpm): rolling speed to be reduced proportionally; advise production planning.
3. **12-hourly GMF VIB checks:** `JSR.HR.STD1.GBX01.VIB.GMF.RMS`. If GMF exceeds 6.5 mm/s at reduced load, immediate controlled stop — do not wait for alarm 10.0 mm/s.
4. **48-hourly oil sampling:** Fe count target ≤30 ppm at 65% load. If >40 ppm (alarm): immediate stop, borescope.
5. **Weekly borescope:** Any visible crack progression (Stage 1→2 transition) = immediate shutdown and crane extraction.
6. **Maximum window:** 12 weeks at 65% load is the absolute Flender-approved limit. If emergency spare not arrived within 12 weeks, shut down for workshop repair regardless.

---

## FSB-ABB-2024-003
**OEM:** ABB
**Applies To:** `HSM.F1.MTR01` — AMI 630 MV motor, ACS6000 VFD (large_induction_motor_vfd)
**Subject:** VFD-induced bearing currents: AEGIS ring inspection and shaft grounding protocol
**Severity:** Advisory
**Date:** 2024-05-22
**Ref Standard:** IEEE 43-2013; NEMA MG1-2021 12.45; IEC 60034-1 Class F

### Background
MV motors fed by ACS6000-class VFDs are susceptible to high-frequency (HF) bearing currents that cause EDM pitting on the raceway (ISO 15243:2017 electrical erosion mode). This is distinct from mechanical fatigue spalling and may not be detected by BPFO envelope analysis.

### Action Required
1. **AEGIS ring inspection:** Inspect shaft grounding ring (AEGIS or equivalent) every 12 months during planned downtime. Replace if carbon brush fibers are worn >50% or ring shows continuous conductive path breaks. Log in CMMS (next due date with `HSM.F1.MTR01` last overhaul: February 2024 → February 2025).
2. **DE bearing inspection:** At every motor overhaul, inspect `SKF 6326` DE bearing bore for EDM frosting (matt grey surface with regular micro-craters <0.5 mm). If found, replace bearing and inspect VFD grounding bonding.
3. **Phase current imbalance monitoring:** `JSR.HR.STD1.MTR01.CURR.IMBAL` — sustained imbalance >2% (warning) can indicate VFD output asymmetry, which increases HF current magnitude. Notify VFD maintenance team if warning sustained >1 h.
4. **Polarisation Index (PI) trending:** `JSR.HR.STD1.MTR01.INS.PI` (offline event). Annual PI ≥2.0 is minimum; trend must not drop >0.5 units per year. If PI falls below 2.0 (warning = alarm), arrange motor swap for rewind within 4 weeks — do not continue operation below PI 1.5.
5. **2×supply frequency vibration `JSR.HR.STD1.MTR01.VIB.2XF1`:** Values >1.0 mm/s indicate rotor eccentricity developing. Schedule motor-gap survey (air-gap measurement) within 2 weeks.

---

## FSB-KSB-2023-011
**OEM:** KSB
**Applies To:** `HSM.DSC.PMP01` (Multitec HP) and `BF.CW.PMP02` (Omega double-suction) — both cooling_descaling_pump class
**Subject:** Mechanical seal and impeller wear management for scale-laden and abrasive-water service
**Severity:** Mandatory Inspection Interval Update
**Date:** 2023-12-01
**Ref Standard:** HI 9.6.1-2017 (NPSH); HI 9.6.7-2021; ISO 15243:2017

### Background
KSB field analysis across steel plant installations shows that SiC/SiC mechanical seal face wear rate in scale-laden HP service (>150 bar discharge, solids >50 mg/L) is 2× higher than in clean-water applications. Standard 12-month planned replacement intervals are insufficient.

### Action Required — HSM.DSC.PMP01
1. **Seal life:** Reduce planned seal replacement interval from 12 months to **8 months** or at first indication of weeping (whichever earlier). Part `SEAL-MECH-DSC` (SiC/SiC cartridge) — ensure 2 units on shelf at all times.
2. **Suction pressure watch:** `JSR.HR.DSC.PMP01.PRES.SUC` — any sustained drop below 90 kPa (warning) indicates NPSH margin <10%. Impeller cavitation at `JSR.HR.DSC.PMP01.AE.RMS` will be the secondary indicator. Minimum suction: 70 kPa alarm = immediate action.
3. **Back-pullout interval:** Full back-pullout inspection (impeller + wear rings + shaft sleeve) at every **third** seal change or at 24 months, whichever earlier. KSB recommends replacement of `SLV-SHAFT-01` shaft sleeve if scoring >0.1 mm.
4. **Discharge pressure trend:** `JSR.HR.DSC.PMP01.PRES.DIS` falling below 185 bar (warning 175) while flow is nominal indicates impeller erosion. Order `IMP-DSC-01` at first warning crossing.

### Action Required — BF.CW.PMP02
1. **Head deviation surveillance:** `JSR.BF.CW.PMP02.HEAD.DEV` — each −1% of head at constant speed = approximately 2.5% impeller diameter reduction from wear. Warning −7% indicates significant wear; plan impeller swap within the next planned outage (maximum 4 weeks from warning).
2. **Impeller stock:** `IMP-CW-01` (double-suction impeller) has 6-week lead time. Re-order point: place order when head deviation exceeds −4% (proactive buffer).
3. **Wear ring `WRING-CW-01`:** Replace at every impeller change. Do not re-use wear rings.

---

## FSB-SIEMENS-MAN-2024-015
**OEM:** Siemens / MAN Turbomachinery
**Applies To:** `BF.BLW.FAN01` — axial turbo-blower / cold-blast machine (bf_sinter_fan_blower)
**Subject:** Thrust bearing temperature limits and anti-surge valve operability verification
**Severity:** Safety Alert
**Date:** 2024-07-08
**Ref Standard:** API 670:2014 Table 1; API 617; ISO 10816-3:2009 Group 3

### Background
Three incidents globally in 2023–2024 involved BF turbo-blowers where thrust bearing temperatures exceeded 95 °C (API 670 alarm) within 30 minutes of ASV (anti-surge valve) functional degradation. The combination of reduced surge margin and thrust-unloading failure creates a compounded failure mode.

### Action Required
1. **Monthly ASV operability test:** Conduct open-loop travel test on anti-surge valve (`ASV-VLV-01`) monthly. Record full-stroke time (target <2 s). If stroke time >3 s or valve fails to return to set position within 0.5 s of command, remove valve and inspect/service. Lead time 12 weeks — maintain 1 spare valve in stock.
2. **Thrust bearing temperature trending:** `JSR.BF.BLW.FAN01.THRUST.TEMP` — API 670 operating limit is 105 °C (alarm). Warning at 90 °C. If temperature exceeds 80 °C and is trending up at >0.5 °C/h, initiate lube system investigation immediately (pressure, temperature, pump check valves, filter DP).
3. **Shaft displacement response to surge:** `JSR.BF.BLW.FAN01.SHAFT.DISP` — during any surge event (discharge oscillation `JSR.BF.BLW.FAN01.PRES.OSC` >5%), shaft displacement must be monitored at 10 Hz. If displacement exceeds 100 µm during a surge event, trip machine — internal rub is probable.
4. **Bently Nevada calibration:** Verify proximity probe calibration (`JSR.BF.BLW.FAN01.SHAFT.DISP`) every 6 months. Calibration drift >±5 µm at alarm setpoint 127 µm = re-calibrate before next BF campaign.
5. **Journal bearing pads `BRG-JRNL-PAD`:** Inspect at every major planned outage (≥24-month interval). Babbitt thickness <2 mm = replace. Lead time 12 weeks — one set must be in store at all times.

---

## FSB-SMSCONCAST-2024-009
**OEM:** SMS Concast
**Applies To:** `CCM.SEG.07` (continuous_caster_segment) and `CCM.MOLD.01` (continuous_caster_mould)
**Subject:** Breakout prevention system (BPS) false-alarm rate and 3-sensor confirmation protocol
**Severity:** Operating Procedure Mandatory Update
**Date:** 2024-03-18
**Ref Standard:** EP2465622B1 [unverified]; SMS Concast BPS user guide

### Background
Single-sensor BPS false-alarm rate for TC delta alone is approximately 40%. The EP2465622B1 algorithm requires all three confirmatory signals (TC delta V-pattern, friction spike, level wave) before initiating deceleration response. Installations that have configured single-sensor BPS trips have experienced unnecessary production losses without reduction in actual breakout rate.

### Action Required — CCM.MOLD.01
1. **BPS configuration:** Confirm that the plant BPS system requires ALL three conditions simultaneously:
   - `JSR.CC1.MOLD.TC.DELTA` ≥25 °C (warning) with V-pattern propagation
   - `JSR.CC1.MOLD.OSC.FRICTION` ≥10 kN (warning)
   - `JSR.CC1.MOLD.LEVEL.DEV` ≥5 mm (warning)
   Single-sensor trips should be configured as advisory alerts only, not automatic speed reductions.
2. **TC array maintenance:** Inspect all TC penetrations for scale build-up at every copper-plate change. Scale on TC tips causes lag in temperature response; if lag >0.5 s on any TC, replace that TC before restart.
3. **Mould copper plate campaign tracking:** Copper Cr-Zr alloy plates (part `MOLD-CU-STD`) should be retired at 400 heat-equivalents or at first confirmed bulge event. Do not extend campaigns without Competent Person taper-gauge measurement confirming wear <0.3 mm.
4. **SEN `SEN-NOZ-01` change frequency:** Minimum every 4 heats in high-carbon-equivalent steels, or at any casting speed reduction >25% (possible SEN erosion). Stock target: ≥8 units. Lead time: 0 weeks (consumable).

### Action Required — CCM.SEG.07
1. **Roll RPM encoder check:** `JSR.CC1.SEG07.ROLL.RPM` — encoder cable corrosion in the spray-water environment is common. Verify encoder signal continuity at every segment overhaul (pull from strand and inspect). A reading of exactly 0 rpm must be treated as seizure AND possible encoder failure until verified.
2. **Spray nozzle `NOZ-SPRAY-01` replacement:** Full nozzle set replacement at every segment pull for maintenance (minimum 12-week pull cycle). Partial blockage not detectable on `JSR.CC1.SEG07.SPRAY.FLOW` zonal flow sensor until 3+ nozzles are blocked.
3. **Segment gap setting:** After any roll replacement, verify gap with calibration kit to ±0.5 mm per slab format. Incorrect gap is the leading cause of strand bulge (sensor `JSR.CC1.SEG07.BULGE`).

---

## FSB-TENOVA-2024-003
**OEM:** Tenova
**Applies To:** `RHF.ZONE.SOAK` — walking-beam reheating furnace soak zone (reheating_furnace)
**Subject:** Refractory shell hotspot monitoring protocol and emergency derate procedure
**Severity:** Safety Guidance
**Date:** 2024-06-30
**Ref Standard:** EN 746-2:2010 sec 5.4; EIGA

### Background
Shell IR scanning is the primary indicator of refractory thinning. Field data across 12 Tenova walking-beam installations shows that shell temperatures above 180 °C (alarm per `JSR.RHF.Z3.SHELL.IR`) indicate remaining refractory thickness <50% of original — a condition requiring mandatory repair at next planned cool.

### Action Required
1. **IR scan frequency:** Minimum 2× per week during normal operation. Increase to 2× per shift if any hotspot identified >140 °C (pre-warning level).
2. **Intermediate derate trigger:** If any shell hotspot reaches 160 °C: reduce zone firing to 85% rated. If it reaches 170 °C: reduce to 75%. If 180 °C alarm fires: reduce to 65% immediately and schedule emergency repair within 10 days (do not defer beyond 14 days).
3. **Gunite repair materials:** `REFRAC-CAST-01` (castable/gunning mix) — maintain minimum 10 bags in store. Application per Tenova gunite spec (65 mm minimum reinstated thickness). Cure schedule: 100 °C/h ramp to 600 °C, 2 h hold, then 100 °C/h to operating temperature. Do not accelerate dry-out — steam spalling risk.
4. **Burner interaction:** Hotspot on wall adjacent to burner port `JSR.RHF.Z3.FLAME.SIG` — verify burner impingement angle. Burner flame length exceeding 1.5 × furnace width at rated firing can cause direct impingement and localised refractory erosion.
5. **Flue O2 monitoring:** `JSR.RHF.Z3.FLUE.O2` — sustained O2 <1.0% (warning_threshold_low) indicates oxygen-deficient combustion and risk of CO accumulation. This is a safety hazard (EN 746-2 requires automatic fuel cutoff at >CO alarm or O2 <0.5%). Ensure safety interlocks are tested annually.

---

## FSB-BOSCH-REXROTH-2024-022
**OEM:** Bosch Rexroth
**Applies To:** `EAF.AUX.HYD01` — HPU 350 bar (eaf_bof_auxiliary)
**Subject:** Water contamination limits and mandatory coalescer filtration for EAF/melt-shop HPUs
**Severity:** Mandatory Practice
**Date:** 2024-09-05
**Ref Standard:** ISO 23409 [unverified]; ISO 4406:2021

### Background
EAF/BOF environments expose hydraulic reservoirs to steam and water ingress from electrode and tilting water-cooling systems. Water above 200 ppm (warning: `JSR.MS.EAF1.HYD.WATER.PPM`) initiates micro-pitting on servo-control piston rods and pump barrel surfaces, leading to progressive ISO 4406 code deterioration.

### Action Required
1. **Inline water sensor calibration:** Verify calibration of water-content sensor (`JSR.MS.EAF1.HYD.WATER.PPM`) quarterly. Sensor drift >±15 ppm at 200 ppm range = replace. Use Karl Fischer reference sample.
2. **200 ppm hard limit:** At or above 200 ppm: do NOT start new EAF heat. Isolate reservoir, connect portable coalescer/absorber filter unit, and circulate until water ≤100 ppm (normal range upper bound).
3. **Root-cause protocol:** Water PPM events must trigger leak investigation within 8 hours. Common sources in EAF service: electrode water-cooling jacket micro-crack, tilt-drive cylinder internal bypass. Log in CMMS.
4. **Filter DP management:** `JSR.MS.EAF1.HYD.FILT.DP` >3.0 bar (warning) = plan filter change within 4 hours. >4.5 bar (alarm) = immediate filter change regardless of operating state. Part `FLT-HYD-10` (10 µm) — stock ≥6 elements. Reorder point = 2 remaining.
5. **ISO 4406 target for EAF service:** 17/15/12 is warning; target normal ≤17/15/12 for this HPU class. Servo-valve circuits (if any) require ≤15/13/10 — use dedicated servo filter circuit if electrode-regulation servo valves present.

---

## FSB-KONECRANES-2024-006
**OEM:** Konecranes
**Applies To:** `MS.LDC.CRN01` — Ladle crane 320 t (ladle_crane)
**Subject:** Wire rope discard criteria, MFL interpretation, and mandatory Competent Person inspection intervals for molten-metal service
**Severity:** Safety Mandatory
**Date:** 2024-04-12
**Ref Standard:** ISO 4309:2017; FEM 1.001; BS EN 13135

### Background
Ladle cranes handling molten steel operate under the most demanding rope duty class. ISO 4309:2017 specifies discard criteria; however, field incidents show that MFL (magnetic flux leakage) proxy thresholds and visible broken-wire counts are sometimes not actioned promptly due to production pressure.

### Action Required
1. **MFL interpretation:** Sensor `JSR.MS.CRN01.ROPE.MFL` (mV signal):
   - 0–100 mV: Normal. Rope healthy, continue standard monthly monitoring.
   - 100–150 mV: Pre-warning zone. Increase inspection to bi-weekly. Begin Competent Person inspection scheduling.
   - 150–300 mV: Warning. Equivalent to ~8–12% LMA (Loss of Metallic Area). **Competent Person inspection required BEFORE next molten-metal lift.** Do not use rope for ladle service above 150 mV without CP sign-off.
   - >300 mV: Alarm. Equivalent to >15–20% LMA OR ≥12 random broken wires in one lay (or ≥4 in one strand) per ISO 4309. **Take crane out of service immediately.** Do not lower load under rope with alarm MFL if load is already suspended; call specialist.
2. **Competent Person (CP) inspection:** Required per ISO 4309 at intervals not exceeding:
   - Standard service: 3 months
   - Molten-metal class (this crane): **Monthly** minimum, or after any shock load >110% SWL.
3. **Load cell `JSR.MS.CRN01.LOAD.SWL`:** Molten-metal ladle crane alarm set at 95% WLL (warning 95%); power cut at 110%. Do not defeat overload protection. Tare weight of empty ladle must be re-zeroed after each ladle refurbishment.
4. **Rope replacement:** `ROPE-CRN-01` (wire rope, custom length/spec) — lead time 12 weeks standard. Because no standby rope in stock guarantees minimum downtime, **place standing insurance order for one rope set every 2 years** even if rope is not at discard. Replacement at maximum 3 years of service life regardless of MFL reading (molten-metal service factor).
5. **Brake drum temperature:** `JSR.MS.CRN01.BRAKE.TEMP` — alarm at 120 °C. After any full-load pick, allow cool-down cycle before next lift if drum temperature >90 °C. Sustained operation above 110 °C accelerates brake-lining wear; inspect pads monthly. `BRAKE-PAD-01` stock: minimum 4 sets.
6. **Hoist gearbox GMF `JSR.MS.CRN01.GBX.VIB.GMF`:** In molten-metal service, apply 20% more conservative action threshold. Practical action at 0.8 g (vs alarm 2.5 g) — plan gearbox inspection during next crane OOS window.

---

## FSB-MOOG-2023-014
**OEM:** Moog
**Applies To:** `CRM.AGC.SV01` — D661 servo valve, hydraulic AGC screwdown (hydraulics_agc_servo)
**Subject:** Silting and spool-wear detection via null-leakage and position-error diagnostics
**Severity:** Advisory
**Date:** 2023-10-25
**Ref Standard:** ISO 4406:2021 servo; Moog sec3 [unverified]

### Background
The D661 servo valve has a spool-to-sleeve radial clearance of 1–3 µm. Particles in the 1–5 µm range (which pass through conventional 10 µm filters undetected) accumulate in the annular gap and cause silting. The ISO 4406 code of the servo circuit (`JSR.CR.S2.AGC.SV.ISO4406`) must be maintained at ≤15/13/10 to prevent this failure mode.

### Action Required
1. **Servo circuit filtration:** Dedicated 3 µm absolute filter (`FLT-SERVO-3`) is mandatory for this valve. Replace at every 500 operating hours, or at ISO 4406 code ≥16/14/11 — whichever occurs first. Do NOT use 10 µm system filters as the sole servo circuit filter.
2. **Null-leakage diagnostic:** `JSR.CR.S2.AGC.SV.NULLLEAK` — factory null leakage for a new D661 is <0.3 L/min. Warning 1.0 L/min indicates 30–40% spool wear; alarm 2.0 L/min = replace valve. Perform null-leakage test during every planned maintenance window (minimum quarterly).
3. **Position error trending:** `JSR.CR.S2.AGC.SV.POSERR` — values >1.5% (warning) occurring >3 times in a 4-hour window is the diagnostic trigger for silt accumulation on the spool. Do not wait for alarm 3.0% — by that point, valve replacement (not cleaning) is typically required.
4. **Ultrasonic bench cleaning:** If spool shows silting but no scoring, ultrasonic bath (35 kHz, mild solvent) for 45 min, then re-test null leakage. If null leakage still >1.0 L/min after cleaning: replace with spare `SERVO-VLV-D661` (stock: 1 unit; lead time 10 weeks — re-order after every use).
5. **Kidney-loop requirement:** After any ISO 4406 excursion ≥17/15/12, connect portable kidney-loop unit `KID-LOOP-01` to servo circuit reservoir and circulate until ISO 4406 returns to ≤14/12/9 (one code better than normal). Target time: 8–16 h.
6. **Grade deviation `JSR.CR.S2.AGC.GAUGE.DEV`:** If gauge deviation exceeds ±10 µm (warning) for >30 min continuously, calculate strip rejection cost (CRM ~INR 2.1 M/cobble-hour). Position-error and gauge-deviation triggers should generate automatic CMMS work orders for servo inspection within 24 h.

---

## FSB-TLT-TURBO-2024-008
**OEM:** TLT-Turbo
**Applies To:** `SP.SINT.FAN01` — radial sinter exhaust fan (bf_sinter_fan_blower)
**Subject:** Dust deposit imbalance management and online balancing protocol for sinter exhaust service
**Severity:** Advisory
**Date:** 2024-02-14
**Ref Standard:** ISO 10816-3:2009 Group 3; ISO 21940-11:2016 (field balancing)

### Background
Sinter exhaust fans are subject to cyclical dust deposition and shedding. Asymmetric deposit buildup causes 1× mass-imbalance vibration increase (sensor `JSR.SP.FAN01.VIB.1X`) that can exceed ISO 10816-3 Zone C (warning 4.5 mm/s) in as little as 3–5 weeks following a clean fan balance. This is distinct from structural damage and can be corrected by online balancing.

### Action Required
1. **Deposit monitoring:** `JSR.SP.FAN01.DP.DUCT` — inlet-outlet differential pressure above 18 kPa (warning) is a secondary indicator of restricted flow from downstream deposit. Cross-check with 1X vibration trending.
2. **Online balancing trigger:** If `JSR.SP.FAN01.VIB.1X` exceeds 3.5 mm/s and is trending upward, schedule online balancing within 5 days. `BAL-WT-01` balance weight set (5 units in stock) is sufficient for trim balancing. Target residual unbalance: ISO 21940-11 Grade G6.3 (VIB <2.3 mm/s at operating speed 990 rpm).
3. **Axial vibration ratio `JSR.SP.FAN01.VIB.AXIAL`:** Axial/radial ratio >0.4 (warning) indicates blade distortion or shaft misalignment, not deposit imbalance. This requires planned outage inspection, not just online balancing. If axial ratio exceeds 0.7 (alarm), arrange offline fan pull within 2 weeks.
4. **Bearing temperature `JSR.SP.FAN01.TEMP.BRG`:** Sinter exhaust fans run in high-dust, elevated ambient temperature environments. Bearing outer ring temperature approaching 80 °C (warning 80 °C, alarm 95 °C) with no corresponding vibration increase may indicate lubrication degradation from dust ingress into bearing housing seals. Degrease and regrease with high-temp EP grease at 80 °C trigger.
5. **Blade erosion inspection:** Annual borescope of fan blades through inspection port. Leading-edge erosion >3 mm depth from original profile = replace blade set `FAN-BLADE-SET`. Unequal blade erosion will present as persistent 1× unbalance not correctable by counterweighting alone.

---

## FSB-TRF-FENNERDUNLOP-2024-005
**OEM:** TRF / Fenner Dunlop
**Applies To:** `RM.CONV.ORE01` — 1600 mm EP630 belt conveyor (raw_material_conveyor)
**Subject:** Belt rip detection system testing, idler thermal management, and belt-edge tracking limits
**Severity:** Mandatory Maintenance Protocol
**Date:** 2024-08-22
**Ref Standard:** CEMA sec6 [unverified]; Fenner RipScan [unverified]; ISO 7623:2015

### Background
Overland ore conveyors carrying coarse iron ore (+50 mm lumps) have a significantly higher rip initiation rate than coal or pellet conveyors. Fenner Dunlop field data shows mean time between rip events of 8–14 months for EP630 belts at steel plants; each belt-rip repair averages 4–12 hours downtime. The RipScan loop current sensor `JSR.RM.CONV1.RIP.LOOP` is the only continuous rip monitor.

### Action Required
1. **RipScan loop test:** Test loop continuity (baseline 60–80 mA per `JSR.RM.CONV1.RIP.LOOP`) monthly. If any reading <48 mA (warning) without confirmed physical damage explanation: schedule belt walk-down within 1 shift. If reading = 0 mA (alarm): stop belt immediately — a longitudinal rip may be propagating.
2. **Idler thermal protocol:** IR thermography walk-down of all idlers minimum 1× per week (`JSR.RM.CONV1.IDLER.TEMP`). Idlers >65 °C: log and schedule replacement within 2 weeks. Idlers >80 °C (warning): replace on next available shift. Idlers >100 °C (alarm): stop belt, replace immediately — fire risk. `IDLER-STD-1600` stock: minimum 40 units (current stock level per spine — maintain this level, re-order when ≤20 remaining).
3. **Ultrasound patrol `JSR.RM.CONV1.IDLER.US`:** Complement IR with ultrasound patrol for early bearing fault detection (ultrasound crosses warning +8 dBuV ~3–5 days before thermal rise). Priority: inspect idlers >0 dBuV on ultrasound (above baseline range −20 to −8 dBuV).
4. **Belt-edge tracking `JSR.RM.CONV1.BELT.EDGE`:** Warning at ±25 mm, alarm at ±50 mm. Edge tracking >25 mm sustained for >10 min = stop belt and adjust training idlers. Do not allow belt to run against fixed structure — belt-edge damage leads to carcass delamination, which accelerates rip propagation.
5. **Vulcanising kits `VULC-KIT-01`:** Minimum 2 kits on site at all times (current stock = 2). Each kit sufficient for one full-belt emergency splice. For planned belt replacement, `BELT-SEC-1600` (10-week lead) must be pre-ordered when a rip event occurs regardless of whether repair is effected.

---

*End of OEM Service Bulletins — TATA_JSR (Synthetic)*
*14 bulletins covering all 15 asset_ids and all 11 equipment_classes in ground_truth_spine.json v1.0.0*
*SYNTHETIC DATA — technically grounded but not real OEM documents. Do not use for actual maintenance decisions.*
