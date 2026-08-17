# Equipment Manual: Continuous Caster Copper Mould
**Asset ID:** CCM.MOLD.01
**Equipment Class:** continuous_caster_mould
**Document:** MAN-007 | Rev 1.0 | Site: TATA_JSR (Synthetic Reference)
**Standard References:** EP2465622B1 (breakout prediction), SMS Concast mould technology guides, EN 746 (safety)

> **DISCLAIMER — SYNTHETIC DOCUMENT.** All numeric values are representative industry estimates grounded in cited standards. No proprietary Tata Steel data is used.

---

## 1. Equipment Description

CCM.MOLD.01 is the copper slab mould assembly for Caster 1, including the copper plate assembly, oscillator drive, mould level control system, and the thermocouple (TC) array used by the Breakout Prediction System (BPS).

The mould is where liquid steel first solidifies into a thin shell (~10–25 mm at mould exit). It is the most instrumented and automation-critical component in the caster — a breakout (shell rupture below the mould) is one of the most dangerous and costly events in steelmaking.

**Manufacturer:** SMS Concast
**Model:** Slab mould, Cu-Cr-Zr plate
**Process Stage:** Casting (primary solidification)
**Criticality:** 1
**Installation Date:** 2021-02-14
**Last Overhaul:** 2024-10-20

**Mould assembly:**
- **Copper plates (broad face + narrow face):** Cu-Cr-Zr alloy; nickel-plated working surface; tapered to match shell shrinkage
- **Oscillator:** Servo-hydraulic or eccentric drive providing sinusoidal oscillation (prevents sticking)
- **Mould level sensor:** Eddy-current or gamma-ray based
- **TC array:** Rows of thermocouples 100–200 mm below top of mould; typically 20–40 TCs per broad face
- **BPS (Breakout Prediction System):** Real-time algorithm monitoring TC array for characteristic V-pattern of sticking

---

## 2. Technical Specifications

| Parameter | Value |
|-----------|-------|
| Mould format (slab) | 900–1850 mm width × 200–250 mm thickness (design range) |
| Copper plate material | Cu-Cr-Zr, Ni-coated working face |
| Copper plate service life | ~250,000–400,000 tonnes (plate-specific; monitor taper wear) |
| Oscillation frequency | 80–160 cycles/min (speed-dependent) |
| Oscillation stroke | ±3–6 mm |
| Casting speed | 0.8–2.2 m/min (slab, width/grade dependent) |
| Mould cooling water flow | ~3,000–5,000 L/min total (broad + narrow face) |
| Mould cooling ΔT normal | 8–15 °C (water inlet to outlet) |
| Mould flux (powder) | Applied continuously; melts to form liquid slag film between copper and shell |
| Normal heat flux | 1.2–2.0 MW/m² (mean over broad face) |
| SEN submersion depth | 100–150 mm below mould level |

---

## 3. Sensor Instrumentation

| Tag | Quantity | Unit | Normal Range | Warning | Alarm | Standard |
|-----|----------|------|-------------|---------|-------|----------|
| JSR.CC1.MOLD.TC.DELTA | Adjacent thermocouple delta temperature | degC | 0 – 20 | 25 | 50 | EP2465622B1 (unverified) |
| JSR.CC1.MOLD.OSC.FRICTION | Oscillator friction force | kN | 2 – 8 | 10 | 18 | SMS Concast (unverified) |
| JSR.CC1.MOLD.LEVEL.DEV | Mould level deviation | mm | −2 – +2 | 5 | 12 | Siemens level control (unverified) |
| JSR.CC1.MOLD.HEATFLUX | Mean mould heat flux | MW/m² | 1.2 – 2.0 | 1.0 | 0.8 | Industry rule (unverified) |

**TC.DELTA critical note:** The adjacent-TC temperature delta is a computed signal — any adjacent pair showing delta >25 °C (warning) is suspicious; delta >50 °C with V-pattern propagation across adjacent TCs is the BPS alarm signature for sticking breakout. A V-pattern forms because the stuck shell tears progressively across the mould width, dragging cold copper surface with it.

**Note on BPS false alarm rate:** Single-sensor TC.DELTA crossing threshold has ~40% FAR. The three-sensor combination (TC.DELTA + OSC.FRICTION spike + LEVEL.DEV oscillation) reduces FAR to <5% per industry benchmark.

**HEATFLUX note:** Lower is worse (note in spine). Declining heat flux = sticking or mould lubrication breakdown. The signal is computed from TC array and cooling water ΔT.

---

## 4. Operating Limits

| Condition | Limit | Action |
|-----------|-------|--------|
| TC.DELTA | >25 °C (warning) | BPS advisory; verify pattern; increase oscillation frequency |
| TC.DELTA | >50 °C (alarm, V-pattern) | BPS ALARM; reduce casting speed to 0.5 m/min immediately |
| OSC.FRICTION | >10 kN (warning) | Suspect sticking; review flux addition; lubrication |
| OSC.FRICTION | >18 kN (alarm) | BPS confirmation; reduce speed; possible stop |
| LEVEL.DEV | >5 mm (warning) | Level control disturbance; investigate SEN / tundish flow |
| LEVEL.DEV | >12 mm (alarm) | Level instability; reduce speed; risk of slag entrainment |
| HEATFLUX | <1.0 MW/m² (warning) | Declining heat transfer; check flux consumption rate |
| HEATFLUX | <0.8 MW/m² (alarm) | Sticking risk; check mould oscillation + flux |

**BPS Alarm Action (all three sensors triggered simultaneously):**
1. Reduce casting speed to ≤0.5 m/min immediately
2. If pattern escalating: full emergency stop (stop withdrawal + close tundish gate)
3. Evacuate caster floor level

---

## 5. Known Failure Modes

### 5.1 Breakout Sticking — Highest Priority Mode

**Physics:** Liquid steel shell sticks to mould copper wall. As withdrawal continues, the thin shell (10–25 mm) tears. The torn zone is dragged upward (cold compared to adjacent shell → V-pattern on TC array). Below the mould, the shell is too thin to contain the liquid steel → rupture → liquid steel onto caster floor.

**Causes:**
- Poor mould flux lubrication (wrong viscosity/basicity for grade/speed)
- Mould taper mismatch (excessive friction)
- SEN erosion causing asymmetric flow and meniscus disturbance
- Mould level fluctuation (turbulence → slag entrainment → poor lubrication)
- Low casting speed (reduces oscillation negative strip time → sticking tendency)

**Degradation Timeline:**
- Healthy: TC.DELTA 12 °C; OSC.FRICTION 5 kN; LEVEL.DEV 1 mm; HEATFLUX 1.6 MW/m²
- Warning: TC.DELTA 20→25 °C; friction spike; level wave (all 3 needed for reliable diagnosis)
- Alarm: TC.DELTA >50 °C V-pattern propagating; friction >18 kN
- Failure: Shell rupture 60–90 seconds after BPS alarm if not acted upon

**Sensor Signature:**
- TC.DELTA: 12 → 55 °C (alarm)
- OSC.FRICTION: 5 → 19 kN (alarm)
- LEVEL.DEV: 1.0 → 13 mm (alarm)

**Fault Codes:** BPS-BREAKOUT-P1, TC-VPATTERN, OSC-FRICTION-SPIKE
**Cost Impact:** INR 71,810,000 / USD 860,000 (range $200k–$3M+, 36 h unplanned)
**Safety Class:** P1

### 5.2 Mould Level Instability

**Root Cause:** SEN partial blockage → asymmetric jet → level oscillation. Or: tundish slide gate hunting → flow variation. Or: caster speed change without level control feed-forward.

**Signature:** LEVEL.DEV cycling above ±5 mm (warning); slag entrainment visible on surface; oscillation marks deeper/irregular on slab.

**Consequences:** Slag entrainment → subsurface inclusions in product; SEN erosion accelerated; can trigger sticking.

**Action:** Replace SEN (SEN-NOZ-01; 8 in stock) during sequence change. Tune level control loop.

### 5.3 Copper Plate Wear

**Root Cause:** Prolonged high-heat-flux casting erodes Ni coating and then Cu surface. Taper changes as plate wears non-uniformly. High-strength/micro-alloyed grades are more aggressive.

**Signature:** Heat flux declining at end of plate campaign (wear reduces thermal conductivity); taper gauge showing deviation from nominal; narrow-face plates may show "barrelling."

**Consequence:** Reduced heat extraction → thinner shell → increased breakout risk at end of plate campaign.

**Action:** Replace copper plates (MOLD-CU-STD; 1 set in stock, 14-week lead) at campaign end per tonnage schedule.

### 5.4 SEN Erosion

**Root Cause:** Alumina inclusions and steel flow erode SEN bore and port geometry, changing jet direction and turbulence intensity.

**Signature:** Asymmetric TC pattern (one side of broad face hotter); LEVEL.DEV increasing; periodic replacement per sequence count.

**Action:** Replace SEN at defined sequence intervals (SEN-NOZ-01; 8 in stock; typical life 5–8 sequences depending on grade).

---

## 6. Preventive Maintenance Schedule

| Task | Interval | Method | Notes |
|------|----------|--------|-------|
| BPS monitoring (TC array + friction + level) | Continuous 10–100 Hz | BPS computer | Real-time V-pattern detection |
| Mould flux addition check | Per heat | Operator inspection | Correct flux type for grade/speed |
| Mould level control calibration | Weekly | Calibration against reference | ±1 mm target accuracy |
| SEN replacement | Per sequence schedule (5–8 sequences) | Sequence change stop | SEN-NOZ-01; 8 in stock |
| Oscillator stroke and frequency check | Weekly | Oscillator controller readout | Compare to schedule |
| TC array verification | Per campaign (weekly) | Replace failed/drifted TCs | Minimum 80% TC coverage for BPS |
| Mould copper plate taper measurement | Per campaign | Gauge measurement | Compare to wear allowance |
| Copper plate replacement (MOLD-CU-STD) | Per tonnage schedule (~300k t) | Planned campaign stop | 14-week lead — order 3 months ahead |
| Oscillator bearing + drive inspection | 3-monthly | Visual + OSC.FRICTION trend | High friction = sticking seal/bearing |
| Mould cooling water quality check | Monthly | Lab sample (hardness, pH) | Scale deposits reduce cooling |

---

## 7. Troubleshooting

### T1 — BPS ALARM (TC.DELTA > 50 °C V-pattern + OSC.FRICTION > 18 kN)

**This is a P1 emergency. Time to shell rupture: 60–90 seconds from full alarm.**

1. **Immediately** reduce casting speed to ≤0.5 m/min (BPS auto-command in most systems; verify execution).
2. Increase oscillation frequency to maximum allowable for current speed.
3. Watch TC pattern — if V-pattern stops propagating and temperatures recover: crisis averted; continue at reduced speed; increase mould flux addition.
4. If TC.DELTA continues rising or shell shows signs of breakthrough: **full emergency stop** — stop withdrawal motor; close tundish gate.
5. **Evacuate caster floor level** — liquid steel release is fatal.
6. After stop: do NOT re-enter floor until all steel has solidified (minimum 4–6 hours + temperature confirmation).
7. Post-breakout: remove skull; replace all damaged segments and mould components (MOLD-CU-STD + ROLL-SEG-STD as needed); 5-whys RCA within 48 hours.

### T2 — LEVEL.DEV > 5 mm (Warning, Oscillating)

1. Check tundish weight (is a new ladle connecting — transient normal).
2. If persistent: suspect SEN partial blockage → schedule SEN change at next sequence break.
3. Check level control loop PID tuning — if hunting: detune proportional gain.
4. Verify tundish slide gate not sticking.

### T3 — HEATFLUX < 1.0 MW/m² (Warning)

1. Check mould flux type and addition rate — incorrect flux viscosity for the grade/speed combination.
2. Increase flux addition rate by 10–20% and observe heat flux recovery.
3. Check oscillation — low frequency or stroke = poor lubrication.
4. If heat flux does not recover and TC.DELTA rising: suspect sticking onset; reduce speed; treat as early T1.

### T4 — OSC.FRICTION > 10 kN (Isolated, No TC.DELTA Pattern)

1. First suspect: mechanical issue with oscillator (worn bearing, stiff guide, broken spring).
2. Check oscillator encoder waveform — should be smooth sinusoidal; spikes = mechanical fault.
3. Inspect oscillator drive mechanism at next sequence break.
4. If friction >18 kN without TC pattern: stop casting; mechanical failure of oscillator is likely (cannot maintain shell lubrication).

---

## 8. Corrective Maintenance — Post-Breakout Recovery

**Required Spares:**
| Part ID | Description | Stock | Lead Time |
|---------|-------------|-------|-----------|
| MOLD-CU-STD | Mould copper plates (standard slab format) | 1 | 14 weeks |
| ROLL-SEG-STD | Strand guide roll | 2 | 12 weeks |
| SEN-NOZ-01 | Submerged entry nozzle (consumable) | 8 | Stock |

**CRITICAL:** MOLD-CU-STD has only 1 set in stock with a 14-week lead. Do not deplete this stock without immediately ordering replacement. After a breakout event, copper plates are typically replaced.

**Unplanned TTR (breakout event):** 36 hours
**Cost Impact:** USD 860,000 (range $200k–$3M+)
**Safety Class:** P1

---

## 9. Safety

- **P1 Safety Class — highest plant risk:** Any actual or potential breakout must trigger floor evacuation alarm; liquid steel at 1,550 °C has instantaneous fatal contact potential at any body exposure.
- **Tundish shrouding:** Hot steel from tundish can splash during SEN changes; mandatory face shield, aluminised jacket, metatarsal boots for all within 5 m.
- **BPS dependency:** Never operate caster with BPS disabled or with <80% TC array functional — written authorisation from plant manager required.
- **Oscillator inspection:** Oscillator moves continuously at 80–160 cycles/min; never insert hands/tools in oscillator zone without full stop + mechanical lock.
- **Carbon monoxide:** CO can accumulate at mould level from mould flux combustion; CO detector is mandatory; ventilation must be verified before close inspection of mould area.
- **Electrical:** TC array at 24 VDC (safe) but BPS computer and level sensor electronics are plant power; follow electrical isolation procedures.
