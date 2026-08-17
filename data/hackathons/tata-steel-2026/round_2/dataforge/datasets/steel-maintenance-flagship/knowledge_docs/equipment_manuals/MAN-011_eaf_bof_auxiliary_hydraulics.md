# Equipment Manual: EAF / Steelmaking Auxiliary Hydraulic Power Unit
**Asset ID:** EAF.AUX.HYD01
**Equipment Class:** eaf_bof_auxiliary
**Document:** MAN-011 | Rev 1.0 | Site: TATA_JSR (Synthetic Reference)
**Standard References:** ISO 4406:2021, ISO 23409 (water content), Bosch Rexroth HPU documentation

> **DISCLAIMER — SYNTHETIC DOCUMENT.** All numeric values are representative industry estimates grounded in cited standards. No proprietary Tata Steel data is used.

---

## 1. Equipment Description

EAF.AUX.HYD01 is the Hydraulic Power Unit (HPU) supplying high-pressure hydraulic oil to EAF 1 electrode regulation cylinders and furnace tilt actuators. Electrode regulation is continuous (closed-loop arc length control at 5–20 Hz response) and is critical to arc stability, energy efficiency, and electrode consumption.

**Manufacturer:** Bosch Rexroth
**Model:** HPU 350 bar
**Process Stage:** Steelmaking (Electric Arc Furnace)
**Criticality:** 1
**Installation Date:** 2019-04-18
**Last Overhaul:** 2024-06-22

**HPU components:**
- High-pressure gear pumps (main + standby)
- Motor-driven (typically 75–200 kW per pump)
- Oil reservoir (600–2000 L)
- High-pressure filtration (10 µm + 25 µm filters)
- Water-cooled heat exchanger (oil cooler)
- Accumulator banks (for fast-response electrode regulation)
- Inline particle counter and water-content sensor
- Relief valves, pressure-reducing valves, directional valves for each consumer

---

## 2. Technical Specifications

| Parameter | Value |
|-----------|-------|
| System pressure | Up to 350 bar |
| Oil type | HLP 46 or HLP 68 (ISO VG 46 or 68, zinc-containing or zinc-free anti-wear) |
| Oil cleanliness target | ≤17/15/12 (ISO 4406:2021) |
| Oil temperature normal | 40–50 °C |
| Oil temperature alarm | 70 °C |
| Filtration | Primary: 25 µm; secondary: 10 µm return filter |
| Filter DP alarm | 4.5 bar |
| Water content normal | 0–100 ppm |
| Water content alarm | 500 ppm |
| Electrode regulation frequency | 5–20 Hz cylinder stroke |
| Accumulator pre-charge | 80% of system pressure (N₂ charged) |

---

## 3. Sensor Instrumentation

| Tag | Quantity | Unit | Normal Range | Warning | Alarm | Standard |
|-----|----------|------|-------------|---------|-------|----------|
| JSR.MS.EAF1.HYD.ISO4406 | Oil cleanliness (ISO 4406:2021 code) | code | ≤17/15/12 | 18/16/13 | 19/17/14 | ISO 4406:2021 |
| JSR.MS.EAF1.HYD.OIL.TEMP | Hydraulic oil temperature | degC | 40 – 50 | 60 | 70 | Rexroth sec2 (unverified) |
| JSR.MS.EAF1.HYD.FILT.DP | Filter differential pressure | bar | 0.0 – 1.5 | 3.0 | 4.5 | Pall (unverified) |
| JSR.MS.EAF1.HYD.WATER.PPM | Water content in oil | ppm | 0 – 100 | 200 | 500 | ISO 23409 (unverified) |

**ISO 4406 code interpretation:** The three-number code (e.g., 17/15/12) represents particle counts at three size thresholds (>4 µm / >6 µm / >14 µm) per 100 mL. Higher number = dirtier oil. The EAF HPU targets ≤17/15/12 for industrial hydraulics. For comparison, the AGC servo circuit (CRM.AGC.SV01) requires the tighter ≤15/13/10.

---

## 4. Operating Limits

| Condition | Limit | Action |
|-----------|-------|--------|
| ISO4406 | 18/16/13 (warning) | Increase filter change frequency; start kidney-loop polishing |
| ISO4406 | 19/17/14 (alarm) | Stop system; identify contamination source; full kidney-loop until ISO target restored |
| OIL.TEMP | >60 °C (warning) | Check oil cooler cooling water flow; reduce load if possible |
| OIL.TEMP | >70 °C (alarm) | Stop pumps; oil degradation threshold |
| FILT.DP | >3.0 bar (warning) | Schedule filter change within 1 shift |
| FILT.DP | >4.5 bar (alarm) | Change filter immediately; bypass indicator may have activated |
| WATER.PPM | >200 ppm (warning) | Suspect cooler leak; check heat exchanger integrity |
| WATER.PPM | >500 ppm (alarm) | Stop system; drain oil; identify and fix cooler leak; replace oil (full batch) |

---

## 5. Known Failure Modes

### 5.1 Oil Contamination — Particulate

**Root Cause:** External ingestion (cylinder rod seal wear draws contamination on retract stroke); filter bypass during high-flow transient; new oil not pre-filtered on fill; reservoir breather filter blocked (atmospheric contamination).

**Consequences:** Abrasive particles damage cylinder seals, pump surfaces, and valve spools. Particles >10 µm cause immediate valve wear; 4–10 µm particles cause fatigue wear over time.

**Signature:** ISO4406 code rising beyond 17/15/12 → 18/16/13 (warning) → 19/17/14 (alarm); increased valve leakage; electrode regulation hunting.

**Resolution:** Kidney-loop filtration (KID-LOOP-01; 1 in stock; portable unit circulates oil through 3 µm absolute filter) + filter element replacement (FLT-HYD-10); identify contamination ingress point.

### 5.2 Water Contamination (Oil-Water)

**Root Cause:** Oil cooler heat-exchanger tube leak (cooling water at 2–4 bar entering oil side at <0.5 bar → water ingresses). Or: condensation in reservoir if ambient temperature cycles below dew point. EAF environments have high ambient humidity.

**Consequence:** Water above 500 ppm causes: (a) oil emulsification → loss of lubrication film; (b) rust on cylinder/valve bores; (c) micro-pitting of pump rolling elements; (d) bacterial growth (creates sludge).

**Signature:** WATER.PPM rising 100 → 200 → 500 ppm; oil may appear milky/cloudy.

**Resolution:** Stop system; drain reservoir; inspect heat exchanger (pressure test cooling water side); replace cooler core (COOL-CORE-01; 1 in stock; 6-week lead); refill with new clean oil; verify WATER.PPM <100 ppm before restart.
**Safety Class:** P2

### 5.3 Oil Temperature Rise / Cooler Fault

**Root Cause:** Oil cooler fouling (scale on water side); cooling water flow reduced; ambient temperature high; increased internal leakage (worn pump/valve generating heat).

**Signature:** OIL.TEMP rising progressively from 46 °C (normal) → 60 °C (warning) → 70 °C (alarm).

**Consequence:** Oil above 60 °C accelerates oxidation and viscosity breakdown; seals swell/harden; reduced system efficiency.

**Resolution:** Clean oil cooler (descale); restore cooling water flow; check pump efficiency (excessive slip = internal heat generation).

### 5.4 Filter Clog

**Root Cause:** Contaminated oil loading filter faster than normal change interval; incorrect filter rating installed; clogged breather filter allowing dirt to bypass to return filter.

**Signature:** FILT.DP rising progressively from 1.0 → 3.0 (warning) → 4.5 bar (alarm); filter bypass indicator pops at alarm level.

**Consequence if bypassed:** Unfiltered oil enters cylinder/valve circuits → rapid component wear.

**Resolution:** Change filter element (FLT-HYD-10; 6 in stock; zero lead time); investigate contamination source.

---

## 6. Preventive Maintenance Schedule

| Task | Interval | Method | Notes |
|------|----------|--------|-------|
| ISO 4406 cleanliness monitoring | Continuous inline / weekly lab | Inline particle counter + lab | Inline sensor provides real-time trend |
| Water content monitoring | Continuous inline / weekly lab | Inline moisture sensor | Alert on WATER.PPM trend rising |
| Filter DP monitoring | Continuous 1 Hz | SCADA pressure transmitter | Change filter when DP > 3 bar |
| Filter element change (FLT-HYD-10) | On DP warning or 3-monthly | Planned HPU stop | Stock 6 units; always available |
| Oil temperature monitoring | Continuous 1 Hz | SCADA | Check cooler if temp rising trend |
| Oil cooler inspection + descaling | 6-monthly | Planned outage | Cooling water side fouling |
| Oil sampling (full analysis) | Monthly | Lab (viscosity, acid, metals, water) | Trend Fe ppm for pump wear |
| Oil change | Annually or on oil analysis alarm | Planned HPU stop | Full drain + flush; fill with pre-filtered new oil |
| Reservoir breather filter change | 3-monthly | Planned stop | Blocked breather = contamination ingress |
| Accumulator pre-charge pressure check | 6-monthly | N₂ pressure gauge | Must be 80% of system pressure |
| Pump efficiency test (volumetric) | 6-monthly | Flow measurement at rated pressure | Declining efficiency = internal wear → excess heat |
| Cylinder rod seal inspection (representative) | Annually | Disassembly sample check | Look for seal extrusion, scoring |

---

## 7. Troubleshooting

### T1 — ISO 4406 Rising (Warning)

1. First check: was any maintenance recently performed that could have introduced contamination (new cylinder, hose change, top-up fill with unfiltered oil)?
2. Start kidney-loop polishing unit (KID-LOOP-01) — attach to reservoir drain/fill port; run with 3 µm filter.
3. Change all return and pressure filters (FLT-HYD-10).
4. Re-sample oil after 8 hours of kidney-loop — should recover to ≤17/15/12.
5. If not improving: suspect active contamination source (cylinder seal leak in-stroke drawing contamination).

### T2 — WATER.PPM > 200 ppm (Warning)

1. Check oil colour/clarity — milky = serious emulsification.
2. Pressure-test oil cooler: isolate cooling water; pressurize to 1.5× working pressure; check for pressure drop (tube leak).
3. Check reservoir for condensation (drain bottom of reservoir; water settles at bottom).
4. If cooler leak confirmed: shut HPU; drain oil into analysis container; replace cooler core (COOL-CORE-01); flush system; fill with new pre-filtered oil.

### T3 — FILT.DP > 3.0 bar (Warning)

1. Plan filter change in next available window (within 1 shift).
2. Have replacement filter element (FLT-HYD-10) staged at HPU.
3. Confirm standby pump is available.
4. Stop main pump; switch to standby; change filter; switch back; check DP returns below 1.5 bar.

---

## 8. Corrective Maintenance — Oil Contamination Response

**Required Spares:**
| Part ID | Description | Stock | Lead Time |
|---------|-------------|-------|-----------|
| FLT-HYD-10 | Hydraulic filter element 10µm | 6 | Stock |
| KID-LOOP-01 | Kidney-loop filtration unit (portable) | 1 | 3 weeks |
| COOL-CORE-01 | Hydraulic oil cooler core | 1 | 6 weeks |

**Safety Class:** P2

---

## 9. Safety

- **High-pressure hydraulic hazard (350 bar):** Oil injection injury — a 350-bar oil jet can penetrate skin and cause tissue necrosis (medical emergency). NEVER use a hand to find a hydraulic leak; use a piece of cardboard; medical attention required if any skin penetration suspected.
- **LOTO:** Depressurise fully to zero (verify on gauge) before opening any hydraulic connection; accumulators retain pressure after pump stop — MUST bleed accumulators via bleed valve before working on circuit.
- **Hot oil:** Oil at 50 °C+ will cause burns; drain into container; use thermal gloves.
- **Fire hazard:** HLP 46/68 mineral oil has flash point ~200 °C; risk of ignition from EAF arc flash or hot electrode material entering the HPU area. HPU room should be enclosed and have CO2 fixed suppression.
- **Oil spill:** Slipping hazard; environmental regulation (oil in water channels); use containment bunds; have absorbent spill kit available.
- **Nitrogen accumulator:** Accumulators pre-charged with N₂ at high pressure; NEVER cut, weld, or drill into an accumulator; must be discharged by specialist with N₂ handling training.
