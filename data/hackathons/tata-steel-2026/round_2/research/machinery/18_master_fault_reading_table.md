# Master Fault → Reading Reference Table
## Steel-Plant Predictive Maintenance — Normal vs Defect vs Alarm Values
**Generated:** 2026-06-08  
**Scope:** Rolling bearings, gearboxes, induction motors, pumps, fans, compressors, hydraulics, mill rolls, continuous casters, conveyors, cranes, furnaces  
**Standards backbone:** ISO 10816-3:2009, ISO 20816-1:2016, ISO 20816-3:2022, ISO 4406:2021 (oil cleanliness), ISO 15243:2017 (bearing failure), NEMA MG1-2021 (motor), API 670 (machinery protection), IEC 60034-1 (motor), ASTM E2374 (AE), EN 13306:2017 (maintenance terminology)

---

## HOW TO READ THIS TABLE

- **Normal value** = healthy machine in steady-state operation at rated load/speed  
- **Defect/degrading value** = reading when fault is developing (pre-failure, 2–8 weeks before failure)  
- **Warning threshold** = operator alert, increase inspection frequency  
- **Alarm/trip threshold** = production hold or automatic trip  
- **Earliest indicator** = the single sensor that fires first in the fault progression  
- `[unverified]` = value is representative/derived from analogous plant data; verify against site baseline  

---

## 1. ROLLING ELEMENT BEARINGS (General)

**Multi-sensor corroboration pattern:** Bearing failure progresses in 4 stages. Stage 1: AE spike (ultrasound 40–60 kHz) appears 4–8 weeks before failure — no vibration change yet. Stage 2: bearing defect frequencies (BPFO, BPFI, BSF, FTF) appear as sidebands in vibration FFT (1–10 kHz range), broadband noise floor rises. Stage 3: Overall vibration RMS rises >2× baseline, temperature begins +5–10°C drift. Stage 4: All three sensors alarming simultaneously — imminent failure within hours. **Rule:** AE alone is insufficient to schedule shutdown; require AE + vibration frequency confirmation before trip. Temperature is a lagging indicator — do not wait for it to alarm.

| Equipment | Fault Mode | Sensor/Parameter | Normal Value | Defect/Degrading Value | Warning Threshold | Alarm/Trip Threshold | Standard/Ref | Earliest Indicator |
|-----------|-----------|-----------------|--------------|----------------------|-------------------|---------------------|--------------|-------------------|
| Rolling mill stand bearing | Outer race fatigue spall (BPFO) | Vibration — envelope spectrum BPFO amplitude | < 0.5 g RMS | 1.5–5 g; BPFO harmonic train visible | 1.0 g envelope RMS | 3.0 g envelope RMS | ISO 15243:2017 §6.1; SKF Bearing Maintenance Handbook | Acoustic emission ↑ 6 dB above baseline (Stage 1) |
| Rolling mill stand bearing | Inner race fatigue spall (BPFI) | Vibration — envelope spectrum BPFI + sidebands at ±frot | < 0.5 g RMS at BPFI | 2–6 g; sidebands ±1× frot around BPFI | 1.2 g | 3.5 g | ISO 15243:2017 §6.1 | AE burst count rate > 200 events/sec |
| Rolling mill stand bearing | Rolling element defect (BSF) | Vibration — envelope spectrum BSF | < 0.3 g | 1–4 g; modulation at cage freq | 0.8 g | 2.5 g | ISO 15243:2017 §6.2 | AE |
| Rolling mill stand bearing | Cage fracture (FTF) | Vibration — low freq cage frequency (0.4–0.5 × frot) | < 0.1 g | Irregular/intermittent 0.5–1.5 g bursts | 0.4 g | 1.0 g | ISO 15243:2017 §6.3 | Irregular AE burst pattern |
| All bearings — hot mill | Overheating / lubrication starvation | RTD/thermocouple at bearing outer ring | 40–70 °C (ambient +30°C) | 80–100 °C rising trend; oil viscosity drop | 85 °C | 100 °C (trip) | ISO 15243:2017 §7; SKF bearing temp limits | RTD ↑ sustained >5°C/h drift |
| All bearings — hot mill | Grease/oil contamination (abrasive) | Vibration — broadband noise floor (1–10 kHz) | Noise floor < −60 dBg | Noise floor rises 6–10 dB; no discrete peaks | +6 dB noise floor | +12 dB noise floor | ISO 4406:2021; NAS 1638 | Broadband noise rise in HF vibration |
| Backup roll bearing (BRG) | Fretting / false brinelling | Vibration RMS (ISO 20816-3 Zone A/B) | Zone A: < 2.3 mm/s RMS | 4–8 mm/s RMS; broadband rise | Zone B: 2.3–4.5 mm/s | Zone C: > 4.5 mm/s (warning); Zone D: >7.1 mm/s (trip) | ISO 20816-3:2022 Table 1 (Group 2 machines) | Vibration broadband power |
| Conveyor idler bearing | Spall — outer race | Ultrasound dB level (structure-borne, 40 kHz) | Baseline −20 to −10 dBuV | +8–15 dBuV above baseline | +8 dBuV | +15 dBuV | UE Systems App Note; [unverified plant-specific] | Ultrasound level |
| Crane hoist bearing | Wear / pitting | Vibration velocity RMS | < 1.8 mm/s RMS | 3.5–7 mm/s; discrete harmonics | 2.3 mm/s | 4.5 mm/s | ISO 10816-3:2009 Zone B/C | Vibration velocity |

---

## 2. GEARBOXES

**Multi-sensor corroboration:** Gear fault: gear mesh frequency (GMF = Z × frot) sidebands appear in FFT. Wear: GMF amplitude rises; tooth surface temperature ↑ (thermal camera or oil-out temp). Scuffing/micropitting: AE events at GMF rate. Confirm with oil debris particle count — ferrous ppm rising confirms mechanical wear vs. electrical noise artifact.

| Equipment | Fault Mode | Sensor/Parameter | Normal Value | Defect/Degrading Value | Warning Threshold | Alarm/Trip Threshold | Standard/Ref | Earliest Indicator |
|-----------|-----------|-----------------|--------------|----------------------|-------------------|---------------------|--------------|-------------------|
| Rolling mill main gearbox | Gear tooth wear (GMF sideband) | Vibration — GMF sideband amplitude at GMF ± frot | Sideband level < −30 dBg relative to GMF | Sidebands rise to −15 to −20 dBg; sideband index SI > 0.1 | SI > 0.15 (6 dB rise) | SI > 0.25; visible harmonic train | AGMA 9005-F16; [unverified] | GMF sideband growth |
| Rolling mill main gearbox | Gear tooth fatigue crack | Vibration — cepstrum rahmonics at tooth-pass period | Rahmonic amplitude < 0.01 g | Rahmonic amplitude 0.03–0.08 g; modulation visible | 0.03 g rahmonic | 0.08 g rahmonic | [unverified; technique from Randall 2021 "Vibration-based Condition Monitoring"] | Cepstrum rahmonics |
| Rolling mill main gearbox | Gear scuffing / micropitting | Oil particle count — ferrous wear debris (ppm) | < 5 ppm ferrous | 10–30 ppm; rapid 2× rise in 1 week | 15 ppm | 40 ppm | ISO 4406:2021; ASTM D7690 | Oil debris ferrous ppm rise |
| Mill pinion gearbox | High-speed shaft bearing spall | Vibration — HSS bearing BPFO | < 0.5 g envelope | 2–5 g; harmonic train | 1.0 g | 3.0 g | ISO 15243:2017 | AE |
| Continuous caster drive gearbox | Gear pitting (GFI) | Oil viscosity cSt @ 40°C | ISO VG 220 → 198–242 cSt | < 180 cSt or > 260 cSt (oxidation) | ±15% of grade | ±20% of grade | ISO 3448; DIN 51519 | Oil viscosity drift |
| Hot strip mill coiler gearbox | Axial misalignment | Vibration — 1× axial / radial ratio | Axial/radial ratio < 0.5 | Ratio 0.8–1.5; 1× axial dominant | Ratio > 0.7 | Ratio > 1.2 | ISO 10816-3; [unverified] | Phase measurement (cross-channel) |
| Coke oven pusher gearbox | Tooth breakage | Vibration — impulsive peak factor (kurtosis) | Kurtosis < 4 (raw time-domain) | Kurtosis 6–12; isolated impulses at tooth-mesh period | Kurtosis > 5 | Kurtosis > 8 | [unverified; Randall §5] | Time-domain kurtosis |

---

## 3. INDUCTION MOTORS

**Multi-sensor corroboration:** Broken rotor bar: MCSA sidebands at (1 ± 2s)f₁ (s = slip). Confirm with stator current spectrum + vibration at 2× slip freq. Winding insulation failure: PI (polarisation index) drops; partial discharge AE events at 100 Hz rate. Eccentricity: MCSA sideband at f₁ ± fr; vibration 1× and 2× dominate. All three indicators must agree before condemning winding.

| Equipment | Fault Mode | Sensor/Parameter | Normal Value | Defect/Degrading Value | Warning Threshold | Alarm/Trip Threshold | Standard/Ref | Earliest Indicator |
|-----------|-----------|-----------------|--------------|----------------------|-------------------|---------------------|--------------|-------------------|
| Rolling mill main drive motor | Broken rotor bar | MCSA — sideband at (1−2s)f₁ relative to fundamental | < −50 dBc (decibels below carrier) | −40 to −30 dBc; harmonic train at (1±2ks)f₁ | −45 dBc | −35 dBc | IEC 60034-1; EPRI TR-1000979 [unverified URL] | MCSA (1−2s)f₁ sideband |
| Rolling mill main drive motor | Stator winding turn-to-turn short | Phase current imbalance (%) | < 1% imbalance | 3–5% imbalance; negative sequence component ↑ | 2% | 5% (NEMA MG1) | NEMA MG1-2021 §12.45 | Negative sequence current component |
| Rolling mill main drive motor | Insulation degradation (ground fault developing) | Polarisation Index (PI = IR₁₀min / IR₁min) | PI > 2.0 (acceptable); PI > 4 (good) | PI 1.5–2.0 (marginal) | PI < 2.0 | PI < 1.5 (at risk) | IEEE Std 43-2013 | Insulation resistance trend |
| Rolling mill main drive motor | Bearing failure (motor side) | Vibration — motor bearing envelope at BPFO | < 0.5 g | 1.5–4 g | 1.0 g | 3.0 g | ISO 20816-3:2022 | AE at motor bearing |
| Rolling mill main drive motor | Rotor eccentricity | MCSA — eccentricity sideband at f₁ ± fr | < −60 dBc | −45 to −50 dBc | −50 dBc | −40 dBc | IEEE 1415-2006 (MCSA) | MCSA eccentricity sidebands |
| Mill drive motor | Overheating — winding | PT100 / NTC embedded winding temperature | Class F: < 130°C (steady state) | 145–155 °C; upward trend >2°C/h | 145 °C | 155 °C (trip Class F) | IEC 60034-1 §9 (Class F insulation) | Winding temperature rate-of-change |
| Blast furnace blower motor | Motor vibration overall | Vibration velocity RMS (motor body) | < 2.3 mm/s (ISO 20816 Group 2) | 4.5–7.1 mm/s | 4.5 mm/s (Zone C) | 7.1 mm/s (Zone D, shutdown) | ISO 20816-1:2016 Table 1 | Overall vibration RMS |
| Conveyor drive motor | Rotor imbalance | Vibration — 1× frot amplitude (radial) | < 1.0 mm/s at 1× | 2.5–4.5 mm/s at 1× dominant | 2.3 mm/s | 4.5 mm/s | ISO 10816-3 | 1× vibration rise |
| Motor (any) | Air gap eccentricity — static | Vibration 2× supply freq (100 Hz or 120 Hz) | < 0.5 mm/s at 2×f₁ | 1.5–3 mm/s at 2×f₁ | 1.0 mm/s | 2.5 mm/s | IEEE 1415-2006 | 2×f₁ vibration |

---

## 4. CENTRIFUGAL PUMPS

**Multi-sensor corroboration:** Cavitation: pressure fluctuation + AE (broadband 100–500 kHz) + suction pressure drop — all three needed. Impeller wear: flow rate drop + vibration 1× rise + discharge pressure down. Seal leak: vibration broadband rise + process fluid temperature upset + bearing housing vibration. Use flow-vs-head curve deviation as ground truth.

| Equipment | Fault Mode | Sensor/Parameter | Normal Value | Defect/Degrading Value | Warning Threshold | Alarm/Trip Threshold | Standard/Ref | Earliest Indicator |
|-----------|-----------|-----------------|--------------|----------------------|-------------------|---------------------|--------------|-------------------|
| Hot strip mill descaler pump | Cavitation | Suction pressure (kPa) | > NPSHr + 0.5 m margin | Drops to NPSHr; pressure pulsations ±10% | < NPSHr + 0.3 m | At/below NPSHr | HI 9.6.1-2017 (Hydraulic Institute) | AE broadband 100–500 kHz spike |
| Hot strip mill descaler pump | Cavitation | AE broadband RMS (100–500 kHz) | Baseline (plant-specific) | +10–15 dB above baseline | +8 dB | +15 dB | ASTM E2374-14 | AE spike |
| Cooling water pump | Impeller wear / erosion | Differential head (m) at rated flow | Design point ±3% | −8 to −15% of design head | −7% | −12% | HI 9.6.7-2021 | Head deviation from pump curve |
| Cooling water pump | Mechanical seal failure (developing) | Vibration — broadband 1–10 kHz RMS | < 1.5 mm/s | 3–6 mm/s; white noise rise | 2.5 mm/s | 5 mm/s | ISO 10816-7:2009 (pumps) | Broadband vibration rise |
| Cooling water pump | Bearing failure | Vibration velocity RMS | < 2.8 mm/s (ISO 10816-7 Zone A) | 4.5–7.1 mm/s | 4.5 mm/s (Zone B/C) | 7.1 mm/s (Zone D) | ISO 10816-7:2009 | Bearing envelope |
| Hydraulic pump (mill AGC) | Internal leakage / worn slipper | Case drain flow (L/min) | < 2% of rated displacement × speed | 4–8% of nominal; case temperature ↑ | 3% rated flow | 6% rated flow (condemn) | Parker Hannifin Pump Service Manual [unverified] | Case drain flow increase |
| Hydraulic pump (mill AGC) | Cavitation (aeration) | Return line filter differential pressure (bar) | < 0.5 bar ΔP across return filter | 0.8–1.2 bar; frothy oil, viscosity upset | 0.8 bar | 1.2 bar | Bosch Rexroth Hydraulics Handbook [unverified] | Differential pressure + AE |
| Blast furnace cooling water pump | Vibration — unbalance | 1× vibration (radial) | < 1.8 mm/s | 3.5–5.5 mm/s; 1× dominant, phase stable | 2.8 mm/s | 5.6 mm/s | ISO 10816-7:2009 | 1× vibration |

---

## 5. INDUSTRIAL FANS / BLOWERS

**Multi-sensor corroboration:** Imbalance: dominant 1× with consistent phase. Resonance: high vibration at speed coinciding with structural natural frequency — confirm by coast-down spectrum. Blade erosion/fouling: 1× rises over weeks + blade-pass frequency (BPF = N×frot) amplitude increases. Bearing failure: envelope at BPFO/BPFI on top of fan vibration floor.

| Equipment | Fault Mode | Sensor/Parameter | Normal Value | Defect/Degrading Value | Warning Threshold | Alarm/Trip Threshold | Standard/Ref | Earliest Indicator |
|-----------|-----------|-----------------|--------------|----------------------|-------------------|---------------------|--------------|-------------------|
| Blast furnace ID fan | Blade erosion / deposit buildup | Vibration 1× frot (mm/s) | < 2.3 mm/s | 5–8 mm/s; gradual 1× rise over days | 4.5 mm/s | 7.1 mm/s | ISO 10816-3:2009 Group 3 | 1× vibration slow trend |
| Blast furnace ID fan | Mass imbalance after deposit shedding | Vibration 1× step-change | Baseline 1–2 mm/s | Sudden jump to 8–15 mm/s at 1× | Any step > 3 mm/s | 10 mm/s | ISO 10816-3 | Instantaneous 1× step |
| Coke oven exhaust fan | Blade fatigue crack | AE burst count (100 kHz) | < 50 events/min | 200–500 events/min; rising trend | 150 events/min | 400 events/min | ASTM E2374; [unverified] | AE count rate |
| Sinter plant main fan | Bearing overheating | Bearing outer ring temperature (°C) | 45–65 °C | 80–95 °C; ΔT > 20°C above ambient+30 | 80 °C | 95 °C | ISO 15243:2017 §8 | Temperature rate-of-change |
| Sinter plant main fan | Shaft bow / misalignment | Vibration — 1× axial + 2× radial | 2× < 30% of 1× | 2× rises to 50–80% of 1×; axial ↑ | 2× > 40% of 1× | 2× > 70% of 1× | [unverified; Mobius Institute] | Axial vibration 1× |
| Reheat furnace combustion fan | Bearing vibration (high speed) | Vibration velocity RMS | < 2.3 mm/s | 4.5–7.1 mm/s | 4.5 mm/s | 7.1 mm/s | ISO 20816-3:2022 | Overall RMS |

---

## 6. COMPRESSORS (Reciprocating & Centrifugal)

**Multi-sensor corroboration (reciprocating):** Valve failure — cylinder pressure waveform P-V diagram distortion is definitive; also high vibration at valve frequency, discharge temp ↑. Piston ring blow-by — crankcase AE + crankcase pressure rise + intercooler temp imbalance. Rod drop — laser displacement or proximity probe on piston rod deviation. Need P-V + temp + vibration to confirm.

| Equipment | Fault Mode | Sensor/Parameter | Normal Value | Defect/Degrading Value | Warning Threshold | Alarm/Trip Threshold | Standard/Ref | Earliest Indicator |
|-----------|-----------|-----------------|--------------|----------------------|-------------------|---------------------|--------------|-------------------|
| Air separation compressor | Surge (centrifugal) | Inlet flow vs surge line (% of surge margin) | > 10% surge margin | 5–8% margin; flow fluctuation ±5% | 8% margin | 5% margin (anti-surge valve triggers) | API 670:2014 §5.8; [unverified plant] | Differential pressure + flow oscillation |
| Air separation compressor | Centrifugal bearing — tilting pad | Radial shaft vibration (proximity probe, μm pk-pk) | < 50 μm pk-pk (API 670 threshold depends on speed) | 80–120 μm; rising trend | 80 μm (alert per API 670) | 127 μm (typical trip, API 670) | API 670:2014 Table 1 | Shaft displacement pk-pk |
| Reciprocating instrument air compressor | Discharge valve failure | Cylinder discharge temperature (°C) | Rated ±10°C of design | +20–35°C above design; P-V loop area shrinks | +20°C | +35°C (trip or unload) | API 618:2007 §6.3; [unverified for exact value] | P-V diagram distortion |
| Reciprocating instrument air compressor | Piston ring blow-by | Crankcase pressure (mbar g) | Near atmospheric (< 10 mbar g) | 20–50 mbar g; methane/air smell [unverified] | 20 mbar g | 50 mbar g | [unverified; Ariel compressor manual] | Crankcase pressure rise |
| Reciprocating instrument air compressor | Suction valve wear | Vibration — valve cover (peak, g) | < 5 g peak at valve cover | 12–20 g peak; asymmetric cylinder-to-cylinder | 10 g | 18 g | [unverified; equivalent from Ludeca app note] | Valve cover high-g vibration |

---

## 7. HYDRAULIC SYSTEMS (Mill Screwdown / AGC)

**Multi-sensor corroboration:** Contamination causes multiple parallel failures: servo valve lap wear (position hunt), pump wear (case drain ↑), actuator seal leak (position drift). Cross-check oil ISO code + case drain + servo valve position error in steady state — all should degrade together. Confirm contamination source by particle shape analysis (smooth = fatigue, sharp = abrasion).

| Equipment | Fault Mode | Sensor/Parameter | Normal Value | Defect/Degrading Value | Warning Threshold | Alarm/Trip Threshold | Standard/Ref | Earliest Indicator |
|-----------|-----------|-----------------|--------------|----------------------|-------------------|---------------------|--------------|-------------------|
| Mill AGC hydraulic cylinder | Oil contamination (particulate) | ISO 4406 cleanliness code (4 μm / 6 μm / 14 μm) | ≤ 17/15/12 (servo circuit) | 19/17/14 — rising; particles visible under microscope | 18/16/13 | 19/17/14 (flush/filter required) | ISO 4406:2021; Rexroth Hyd. Handbook §4 | ISO cleanliness code step-up |
| Mill AGC hydraulic cylinder | Oil water contamination | Karl Fischer water content (ppm) | < 100 ppm (mineral oil) | 200–500 ppm; emulsification visible | 200 ppm | 500 ppm (drain/dry cycle) | ISO 23409:2011 [unverified URL] | Water ppm rise |
| Mill AGC servo valve | Spool wear / lap erosion | Servo valve null leakage (L/min at null command) | < 0.5 L/min null leak | 1.5–3 L/min; position hunt in steady state | 1.0 L/min | 2.0 L/min | Moog Servo Valve Manual §3 [unverified] | Position error in steady state |
| Mill AGC servo valve | Hysteresis increase | Valve hysteresis (% of rated command) | < 0.5% | 1.5–3%; position control instability | 1.5% | 3% | Moog Servo Valve Manual §3 | Hysteresis in ramp test |
| Mill hydraulic power unit | Oil temperature rise | Hydraulic oil temperature (°C) | 40–50 °C operating | 60–70 °C; viscosity drop; accelerated wear | 60 °C | 70 °C (cooler fault) | Bosch Rexroth Hydraulics §2 [unverified] | Oil temperature trend |
| Mill hydraulic power unit | Filter differential pressure (clog) | Filter ΔP (bar) | < 1.5 bar ΔP across pressure filter | 3–5 bar; bypass indicator may pop | 3.0 bar | 4.5 bar (change filter) | Pall Corp filter specifications [unverified] | Filter ΔP |

---

## 8. MILL ROLLS (Work Rolls / Backup Rolls)

**Multi-sensor corroboration:** Roll spall / flat: rolling force fluctuation at once-per-revolution + strip thickness variation at same frequency + vibration at 1× roll frot. Roll chatter (fifth octave): vibration dominant at chatter freq (usually 100–200 Hz for cold mill) + strip gauge variation spectral peak at same frequency. Confirm roll damage with ultrasonic roll inspection at next scheduled change.

| Equipment | Fault Mode | Sensor/Parameter | Normal Value | Defect/Degrading Value | Warning Threshold | Alarm/Trip Threshold | Standard/Ref | Earliest Indicator |
|-----------|-----------|-----------------|--------------|----------------------|-------------------|---------------------|--------------|-------------------|
| Hot mill work roll | Roll spall / flat spot | Rolling force variation (% of mean) | < ±2% force ripple | ±5–10% at 1× roll speed; periodic | ±4% | ±8% (roll change required) | [unverified; Tata Steel PdM internal ref] | Rolling force periodic fluctuation |
| Hot mill work roll | Roll wear — thermal camber loss | Strip crown deviation from target (μm) | ±10 μm crown | ±30–50 μm; crown worsening over campaign | ±25 μm | ±40 μm | [unverified] | Strip gauge profile deviation |
| Cold mill work roll | 5th-octave chatter (roll-strip dynamic) | Vibration at chatter frequency (100–200 Hz), mm/s RMS | < 1 mm/s in 100–200 Hz band | 5–15 mm/s; strip surface marks | 4 mm/s | 10 mm/s (speed reduction required) | [unverified; ABB CMC literature] | Vibration chatter freq + strip visual |
| Cold mill work roll | Roll surface crack (fatigue) | AE rms at 100 kHz near roll journal | Baseline ± 3 dB | +10–15 dB above baseline; bursts at 1/rev | +8 dB | +15 dB | ASTM E2374-14 [unverified application] | AE burst rate |
| Backup roll (BUR) | Bearing inner race fatigue | Vibration envelope BPFI (low speed, 15–60 RPM) | < 0.3 g envelope | 1.0–2.5 g; discrete harmonic train | 0.7 g | 2.0 g | ISO 15243:2017; [unverified BUR-specific] | Envelope spectrum BPFI |
| Backup roll (BUR) | Roll barrel spall | Ultrasonic immersion scan (reflector amplitude dB) | No indication (baseline) | 3–6 dB reflector; growing in successive scans | 3 dB new indication | 6 dB (remove from service) | [unverified; plant NDT protocol] | UT indication growth |

---

## 9. CONTINUOUS CASTER

**Multi-sensor corroboration:** Mould breakout prediction — the "gold standard" multi-sensor pattern: mould thermocouple array shows V-shaped cold spot (heat flux drop at one location) propagating downward with strand withdrawal speed, WHILE sticking friction spikes on the oscillator force trace, WHILE mould level fluctuates ±5 mm. All three must agree: thermocouple pattern + oscillator force + level — single sensor alone causes >40% false alarm rate. [Reference: Tata Steel Europe mould level control patent EP2465622B1; [unverified] for exact thresholds].

| Equipment | Fault Mode | Sensor/Parameter | Normal Value | Defect/Degrading Value | Warning Threshold | Alarm/Trip Threshold | Standard/Ref | Earliest Indicator |
|-----------|-----------|-----------------|--------------|----------------------|-------------------|---------------------|--------------|-------------------|
| Continuous caster mould | Breakout — sticking type | Mould thermocouple ΔT (adjacent TCs, same column, °C) | < 20 °C ΔT between adjacent TCs | 30–60 °C localized cold spot; V-pattern propagating | 25 °C ΔT sustained > 5 s | 50 °C ΔT → reduce speed to 0.5 m/min | Tata Steel EP2465622B1; [unverified exact threshold] | Thermocouple V-pattern formation |
| Continuous caster mould | Breakout — sticking | Mould oscillator friction force (kN) | 2–8 kN baseline | 12–20 kN spike at negative strip period | 10 kN | 18 kN | [unverified; SMS Concast oscillation control] | Friction force spike during negative strip |
| Continuous caster mould | Mould level instability | Mould level deviation (mm from setpoint) | ±2 mm | ±8–15 mm; oscillatory; SEN wear | ±5 mm | ±12 mm (auto speed reduce) | [unverified; Siemens Level Control system] | Mould level oscillation frequency |
| Caster secondary cooling | Roll segment misalignment | Strand bulging (soft reduction thickness vs. target, mm) | < 1 mm deviation | 2–5 mm; internal crack risk; crater end position shift | 2 mm | 4 mm (reduce casting speed) | [unverified; Primetals soft-reduction system] | Strand thickness deviaton |
| Caster withdrawal roll | Roll bearing failure | Vibration — roll bearing at withdrawal speed | < 2 mm/s RMS | 4–7 mm/s; 1× + BPFO combo | 3.5 mm/s | 6.0 mm/s | ISO 10816-3 [unverified application] | Envelope BPFO |
| Caster withdrawal roll | Roll surface groove/wear | Strand surface mark — oscillation mark depth (μm) | < 50 μm oscillation mark depth | > 80 μm marks; periodic roll-pitch marks superimposed | 70 μm | 100 μm (inspect rolls) | [unverified] | Surface mark period correlating to roll circumference |
| Caster tundish | SEN (submerged entry nozzle) erosion | Tundish-to-mould flow asymmetry (%) | < 5% left-right flow asymmetry | 10–25% asymmetry; biased flow; level waves | 8% | 15% (change SEN) | [unverified; ABB mould EMS] | Mould level asymmetry pattern |
| Caster mould | Copper plate wear / heat flux degradation | Mean mould heat flux (MW/m²) | 1.2–2.0 MW/m² (billet caster) | < 0.8 MW/m²; localized hot spot or cold zone | < 1.0 MW/m² | < 0.8 MW/m² | [unverified; industry rule-of-thumb] | Heat flux calculated from TC array |

---

## 10. CONVEYOR SYSTEMS

**Multi-sensor corroboration:** Belt misalignment: belt alignment sensor (edge sensor) + motor current ↑ (load redistribution) + idler bearing vibration ↑ on pull-off side. Confirm with thermal camera scan — misaligned belt shows edge heat. Blocked chute: belt tension load cells ↑ + motor current ↑ + belt speed ↓ under load. Belt tear: acoustic emission or rip detector loop (current loss) — definitive.

| Equipment | Fault Mode | Sensor/Parameter | Normal Value | Defect/Degrading Value | Warning Threshold | Alarm/Trip Threshold | Standard/Ref | Earliest Indicator |
|-----------|-----------|-----------------|--------------|----------------------|-------------------|---------------------|--------------|-------------------|
| Raw materials conveyor | Idler bearing failure | Ultrasound dBuV @ 40 kHz | Plant baseline (e.g. −15 dBuV) | +8 to +15 dBuV above baseline | +8 dBuV | +15 dBuV | UE Systems Guide; [unverified plant] | Ultrasound level |
| Raw materials conveyor | Belt misalignment | Belt edge position sensor (mm from center) | < ±15 mm from centerline | ±30–60 mm; lateral drift; edge fraying | ±25 mm | ±50 mm (auto-stop) | CEMA Belt Conveyor Standard §6 [unverified] | Belt edge position |
| Raw materials conveyor | Motor overload (blocked chute) | Drive motor current (A or % FLA) | < 95% FLA | 110–130% FLA sustained > 5 s | 105% FLA | 125% FLA (trip) | NEMA MG1-2021; IEC 60947-4 | Motor current |
| Raw materials conveyor | Belt rip / longitudinal tear | Belt rip detector loop current (mA) | Nominal loop current (60–80 mA typically) | Loop opens or drops to 0 | Any 20% drop from nominal | Open circuit = immediate stop | [unverified; Fenner Dunlop RipScan spec] | Rip detector loop open |
| Ore yard reclaimer conveyor | Slippage (belt-pulley) | Belt slip sensor (% speed deviation drive vs. tail) | < 1% slip | 3–8% slip; belt speed < drive speed | 2% | 5% (auto slip-clutch engage or stop) | [unverified] | Speed sensor differential |
| Coke conveyor | Roller seizure / fire risk | Thermal camera — idler temperature (°C) | < 60 °C idler surface | 80–120 °C; visible IR hotspot | 80 °C | 100 °C (replace idler, fire risk on coke belt) | [unverified; fire risk specific to coke/coal belts] | IR thermal scan hotspot |

---

## 11. CRANES (EOT / Ladle Cranes)

**Multi-sensor corroboration:** Hoist gearbox wear: vibration GMF sidebands ↑ + gearbox oil temperature ↑ + oil debris ferrous ppm ↑. Rope fatigue: magnetic flux leakage (MFL) defect signal + rope diameter reduction by caliper. Wheel/rail wear: vibration at wheel-pass frequency + rail inspection visual. Overload: load cell ↑ + structural strain gauge ↑ simultaneously.

| Equipment | Fault Mode | Sensor/Parameter | Normal Value | Defect/Degrading Value | Warning Threshold | Alarm/Trip Threshold | Standard/Ref | Earliest Indicator |
|-----------|-----------|-----------------|--------------|----------------------|-------------------|---------------------|--------------|-------------------|
| Ladle crane hoist | Wire rope fatigue — broken wire | MFL signal (wire rope tester, mV) | Baseline MFL (< 100 mV) | 200–500 mV at defect; periodic as rope feeds | 150 mV | 300 mV (retire rope) | ISO 4309:2017 (rope discard criteria) | MFL rope tester signal |
| Ladle crane hoist | Wire rope diameter reduction (wear) | Rope diameter caliper (mm) | Nominal Ø ± 1% | Ø reduced 3–5%; visible wire breaks | −2% from nominal Ø | −3% nominal Ø (ISO 4309 discard) | ISO 4309:2017 §5.3 | Diameter gauge + MFL |
| Ladle crane hoist gearbox | Gear tooth wear | Vibration GMF amplitude (g) | < 0.5 g at GMF | 1.5–3 g; sideband family visible | 1.0 g | 2.5 g | [unverified; ISO 10816 extrapolation] | GMF amplitude growth |
| Ladle crane wheel / rail | Wheel flat (impact) | Vibration — impact at wheel-pass frequency (g peak) | < 2 g peak | 6–15 g; repeating impulse at wheel rotation period | 4 g | 10 g | [unverified; Mobius Institute crane module] | Peak vibration impulse |
| EOT crane end carriage | Structural overload | Load cell (% SWL — Safe Working Load) | Operating < 100% SWL | 110–125% SWL; creep/deformation visible | 105% SWL | 110% SWL (auto-cut) | FEM 1.001 (European crane standard); BS EN 13135 | Load cell reading |
| Ladle crane travel rail | Rail joint wear | Vibration impact at rail joint (g) | < 3 g at joint | 8–20 g; increasing over months; carbody sway | 6 g | 15 g | [unverified; rail maintenance protocol] | Vibration at known joint spacing |

---

## 12. FURNACES (Reheat Furnace / Annealing / BF Stoves)

**Multi-sensor corroboration:** Refractory hotspot: IR camera external scan + embedded TC deviation from zone average + flue gas O₂ rise (poor combustion from air infiltration through crack). Burner failure: flame scanner signal dropout + NOₓ/CO rise in flue gas analyser + furnace pressure fluctuation. BF stove checker crack: differential pressure ΔP rise + dome temperature asymmetry + CO₂ percentage in waste gas. All three needed to distinguish checker crack from soot blockage.

| Equipment | Fault Mode | Sensor/Parameter | Normal Value | Defect/Degrading Value | Warning Threshold | Alarm/Trip Threshold | Standard/Ref | Earliest Indicator |
|-----------|-----------|-----------------|--------------|----------------------|-------------------|---------------------|--------------|-------------------|
| Reheat furnace | Refractory hot spot / burnout | IR camera external shell temperature (°C) | 80–120 °C shell surface | 200–350 °C localised spot; growing | 180 °C | 250 °C (reduce zone firing; inspect) | [unverified; general refractory practice] | IR thermal camera hotspot |
| Reheat furnace | Burner failure — fuel-side | Flame scanner signal (%) | 90–100% signal (healthy flame) | < 50% signal; flickering; intermittent | < 70% signal | < 40% (automatic fuel cutoff) | EN 746-2:2010 §5.4 (industrial thermoprocess); [unverified exact %) | Flame scanner % signal |
| Reheat furnace | Combustion imbalance (excess air) | Flue gas O₂ (%) at economiser exit | 1.5–3.5% O₂ (natural gas; design stoichiometry) | < 0.5% (rich, CO risk) or > 6% (lean, fuel waste) | < 1% or > 5% | < 0.5% (CO alarm) | EIGA IGC Doc 105 [unverified URL]; EN 746-2 | Flue gas O₂ probe |
| Reheat furnace | Slab surface oxidation (scale loss) | Scale loss weight (% of slab weight) | 0.8–1.2% (normal hot rolling scale) | > 1.5% scale; furnace atmosphere oxidising | 1.4% | 1.8% (reduce furnace O₂) | [unverified; iron oxide scale chemistry] | Excess scale on descaler entry |
| Blast furnace stove (Cowper) | Checker brick deterioration | Stove ΔP during blast period (mbar) | 50–80 mbar ΔP (new checker) | 120–200 mbar; increasing trend over campaign | 120 mbar | 180 mbar (schedule de-dusting/repair) | [unverified; BF stove operational data] | Stove differential pressure trend |
| Blast furnace stove | Gas leakage — combustion to blast | Waste gas CO₂ (%) during on-blast | < 0.5% CO₂ in cold blast | 1–3% CO₂; combustion gas crossover | 1% CO₂ | 2% CO₂ (isolate stove) | [unverified] | Waste gas CO₂ analyser |
| Continuous annealing furnace | Radiant tube burnout | Tube skin temperature (°C) — embedded TC | 900–1000 °C typical Si-SiC tube rating | > 1100 °C; tube deformation, oxidation | 1050 °C | 1100 °C (cut tube gas, inspect) | [unverified; Kanthal radiant tube specs] | Tube skin TC spike |
| Continuous annealing furnace | Atmosphere dew point drift (H₂/N₂) | Dew point (°C) in HNX atmosphere | −30 to −50 °C dew point | > −20 °C dew point; water infiltration; oxidation | −25 °C | −15 °C (purge required) | [unverified; Linde HNX atmosphere guide] | Dew point sensor |

---

## 13. OIL / LUBRICATION SYSTEMS (Cross-equipment)

**Multi-sensor corroboration:** Oil degradation: viscosity drift + AN (acid number) rise + water ppm ↑ + particle count ↑ — all degrade together if oxidation is the root cause. If only particle count spikes without viscosity change, contamination from external source (not oxidation). Cross-check ISO code + ferrous ppm to separate wear debris from external contamination.

| Equipment | Fault Mode | Sensor/Parameter | Normal Value | Defect/Degrading Value | Warning Threshold | Alarm/Trip Threshold | Standard/Ref | Earliest Indicator |
|-----------|-----------|-----------------|--------------|----------------------|-------------------|---------------------|--------------|-------------------|
| Mill gearbox oil circuit | Oil oxidation / varnish | Acid Number AN (mg KOH/g) | < 0.3 mg KOH/g (new oil) | 1.0–2.5 mg KOH/g; varnish deposits | 1.0 mg KOH/g | 2.0 mg KOH/g (oil change) | ASTM D664; ISO 6618 | AN titration trend |
| Mill gearbox oil circuit | Viscosity breakdown (shear) | Kinematic viscosity cSt @ 40°C | ISO VG 220 → 198–242 cSt | < 180 cSt (shear breakdown) or > 265 cSt (oxidation thickening) | ±15% of grade centre | ±20% (condemn) | ISO 3448; ASTM D445 | Viscosity measurement |
| Mill gearbox oil circuit | Metallic wear debris | Ferrous particle count (ppm via ICP or PQ Index) | PQ Index < 10 [unverified scale] | PQ 25–60; ICP Fe > 30 ppm | PQ > 20; Fe > 20 ppm | PQ > 50; Fe > 50 ppm | ASTM D5185 (ICP); Spectro/Fluitec PQ method | PQ Index or ICP Fe trend |
| Rolling mill centralized lubrication | Lubricant starvation (blocked line) | Lubrication pressure at point-of-use (bar) | Design pressure ± 10% | Drops > 20% or to zero in one branch | −15% from design | −25% from design (blocked line alarm) | [unverified; Lincoln Lubrication system spec] | Point-of-use pressure sensor |
| Mill oil film bearing (OFB) | Oil film breakdown | Oil film bearing outlet temperature (°C) | 50–65 °C | 75–85 °C; rising trend; may precede bearing seizure | 75 °C | 85 °C (trip OFB) | [unverified; SKF OFB application guide] | OFB oil outlet temperature |

---

## 14. ACOUSTIC EMISSION — CROSS-EQUIPMENT REFERENCE LEVELS

| Equipment | Fault Mode | Sensor/Parameter | Normal Value | Defect/Degrading Value | Warning Threshold | Alarm/Trip Threshold | Standard/Ref | Earliest Indicator |
|-----------|-----------|-----------------|--------------|----------------------|-------------------|---------------------|--------------|-------------------|
| Any rotating bearing | Early fatigue initiation | AE RMS voltage (40–60 kHz, structure-borne) | Baseline ± 2 dBuV (plant-specific) | +6–8 dBuV above baseline; impulse rate ↑ | +6 dBuV sustained > 30 min | +12 dBuV | ASTM E2374-14; [unverified absolute levels] | AE RMS rise (Stage 1 — no vibration change yet) |
| Crane wire rope | Stress corrosion cracking | AE event count (burst events/min, 50–200 kHz) | < 10 events/min at operating load | 50–200 events/min; correlated with load cycles | 50 events/min | 150 events/min | ASTM E1316; [unverified for rope] | AE event count |
| Mill roll journal | Surface crack propagation | AE burst energy (aJ per event, 100 kHz) | < 100 aJ/event background | 500–2000 aJ; events clustered at 1/rev | 300 aJ | 1000 aJ (remove from service) | [unverified; application-specific AE calibration required] | AE burst energy |

---

## SUMMARY CORROBORATION RULES (Key Sensor Combinations)

| Equipment Class | Primary Early Indicator | Confirmatory Sensor 2 | Confirmatory Sensor 3 | False-Alarm Suppressor |
|----------------|------------------------|----------------------|----------------------|----------------------|
| Rolling bearing | AE RMS (40–60 kHz) ↑ | Envelope BPFO/BPFI amplitude ↑ | Bearing temp rate-of-change ↑ | Require 2 of 3 for trip |
| Gearbox | GMF sideband amplitude ↑ | Oil ferrous ppm ↑ | Oil temperature ↑ | Oil debris confirms mechanical vs. electrical noise |
| Induction motor | MCSA (1−2s)f₁ sideband ↑ | Winding temperature ↑ | Vibration 1× imbalance ↑ | PI (insulation) for winding vs. rotor fault discrimination |
| Centrifugal pump | AE broadband (cavitation) | Suction pressure ↓ | Differential head ↓ from design curve | Flow meter confirms operating point |
| Caster mould breakout | TC V-pattern cold spot | Oscillator friction force spike | Mould level oscillation | All 3 required — single-sensor > 40% FAR |
| Hydraulic system | ISO 4406 code step-up | Case drain flow ↑ | Servo valve position error | Particle shape analysis (abrasive vs. fatigue) |
| Conveyor belt | Motor current ↑ | Belt tension ↑ | Idler ultrasound ↑ | Thermal scan confirms misalignment vs. overload |
| Crane wire rope | MFL defect signal ↑ | Rope diameter reduction | AE burst count ↑ | MFL + diameter together → retire per ISO 4309 |
| Reheat furnace | IR hot spot camera | TC zone deviation ↑ | Flue O₂ rise | TC confirms refractory breach vs. IR camera noise |

---

## KEY STANDARDS AND SOURCES

| Standard / Source | Scope | URL / Ref |
|-------------------|-------|-----------|
| ISO 10816-3:2009 | Vibration — industrial machines >15 kW, 120–15000 RPM | https://www.iso.org/standard/38677.html |
| ISO 20816-1:2016 | Vibration measurement and evaluation | https://www.iso.org/standard/63180.html |
| ISO 20816-3:2022 | Industrial machines with power > 15 kW | https://www.iso.org/standard/73600.html |
| ISO 15243:2017 | Rolling bearings — failure modes | https://www.iso.org/standard/59429.html |
| ISO 4406:2021 | Hydraulic fluid cleanliness coding | https://www.iso.org/standard/76897.html |
| ISO 4309:2017 | Crane wire rope — discard criteria | https://www.iso.org/standard/64864.html |
| API 670:2014 | Machinery protection systems (proximity probes) | https://www.api.org/products-and-services/standards/important-standards-announcements/standard-api-670 |
| API 618:2007 | Reciprocating compressors | https://www.api.org/products-and-services/standards/important-standards-announcements/standard-api-618 |
| NEMA MG1-2021 | Motors and generators | https://www.nema.org/Standards/Pages/Motors-and-Generators.aspx |
| IEC 60034-1 | Rotating electrical machines — rating | https://webstore.iec.ch/publication/136 |
| IEEE Std 43-2013 | Insulation resistance testing | https://standards.ieee.org/ieee/43/3918/ |
| IEEE 1415-2006 | MCSA for induction motors | https://standards.ieee.org/ieee/1415/3169/ |
| ASTM E2374-14 | Acoustic emission system performance verification | https://www.astm.org/e2374-14.html |
| ASTM D664 | Oil acid number | https://www.astm.org/d0664-11ae02.html |
| ASTM D5185 | ICP — oil wear metals | https://www.astm.org/d5185-18.html |
| EN 746-2:2010 | Industrial thermoprocessing equipment safety | https://www.en-standard.eu/bs-en-746-2-2010/ |
| AGMA 9005-F16 | Industrial gear lubrication | https://www.agma.org/standards/agma-9005-f16/ |
| HI 9.6.1-2017 | Pump NPSH | https://www.pumps.org/product/9-6-1-2017/ |
| CEMA Belt Conveyor | Belt conveyor standard | https://www.cemanet.org/product/belt-conveyors-for-bulk-materials/ |
| FEM 1.001 | Crane design classification | https://www.fem-europe.com/fem-documents/ |
| Tata Steel EP2465622B1 | Mould breakout prediction patent | https://patents.google.com/patent/EP2465622B1 |

---

*All `[unverified]` tagged values are representative industry-wide estimates. Site-specific baseline calibration is mandatory before deploying alarm thresholds in production. Absolute thresholds vary by machine size, speed, fluid grade, and installation class.*
