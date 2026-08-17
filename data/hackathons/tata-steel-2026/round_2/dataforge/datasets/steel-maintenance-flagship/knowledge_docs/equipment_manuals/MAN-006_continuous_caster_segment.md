# Equipment Manual: Continuous Caster Strand-Guide Segment
**Asset ID:** CCM.SEG.07
**Equipment Class:** continuous_caster_segment
**Document:** MAN-006 | Rev 1.0 | Site: TATA_JSR (Synthetic Reference)
**Standard References:** ISO 10816-3 (unverified), Primetals SMS Concast segment design guides

> **DISCLAIMER — SYNTHETIC DOCUMENT.** All numeric values are representative industry estimates. No proprietary Tata Steel data is used.

---

## 1. Equipment Description

CCM.SEG.07 is Segment 7 of the strand-guide assembly in Continuous Caster 1 (Caster 1, slab format). Located in the withdrawal/bending zone (~2–5 m below the mould exit), this segment guides the partially solidified slab as it curves from vertical to horizontal, applying controlled soft-reduction forces to improve slab centre-segregation.

**Manufacturer:** SMS Concast
**Model:** Smart segment (independent hydraulic gap control)
**Process Stage:** Casting (withdrawal and bending zone)
**Criticality:** 1
**Installation Date:** 2019-11-22
**Last Overhaul:** 2024-08-01

**Segment Function:**
- Support and guide the partially solidified strand (liquid core still present at Seg 7)
- Apply hydraulic clamping force for dynamic soft reduction
- Provide secondary cooling via spray nozzles between rolls
- Rolls must rotate freely — a seized roll drags the strand, causing transverse cracks and potential breakout

---

## 2. Technical Specifications

| Parameter | Value |
|-----------|-------|
| Number of rolls per segment | 6–10 (design-specific) |
| Roll diameter | Typically 200–300 mm |
| Roll material | High-chrome cast iron or hard-chromium-plated steel |
| Roll bearing type | Spherical roller bearings (water + scale-resistant) |
| Hydraulic system pressure | Max 350 bar (segment clamp) |
| Normal clamping force | 200–400 kN |
| Spray nozzle type | Full-cone or flat-fan water spray |
| Secondary cooling water pressure | Typically 10–15 bar to spray nozzles |
| Soft-reduction gap control | ±0.1 mm position accuracy (SMS Smart Segment) |
| Operating temperature environment | 900–1100 °C strand surface; segment rolls < 200 °C surface |

---

## 3. Sensor Instrumentation

| Tag | Quantity | Unit | Normal Range | Warning | Alarm | Standard |
|-----|----------|------|-------------|---------|-------|----------|
| JSR.CC1.SEG07.FORCE.HYD | Segment hydraulic clamping force | kN | 200 – 400 | 480 | 550 | Primetals soft-reduction (unverified) |
| JSR.CC1.SEG07.ROLL.RPM | Roll rotation speed | RPM | 3 – 25 | 1.0 | 0.0 | Encoder; 0 = seizure |
| JSR.CC1.SEG07.BULGE | Strand bulge deviation | mm | 0.0 – 1.0 | 2.0 | 4.0 | Primetals (unverified) |
| JSR.CC1.SEG07.SPRAY.FLOW | Zone spray flow rate | L/min | 180 – 220 | 150 | 120 | Secondary cooling zone |
| JSR.CC1.SEG07.VIB.ROLL | Roll bearing vibration | mm/s | 0.5 – 2.0 | 3.5 | 6.0 | ISO 10816-3 (unverified) |

**ROLL.RPM critical note:** A reading of 0.0 RPM (alarm) indicates a seized roll with absolute certainty. At Segment 7 (liquid core zone), a seized roll dragging the strand causes immediate risk of transverse cracking, internal tears, and breakout potential. This alarm requires immediate action — reduce casting speed or end heat.

**FORCE.HYD note:** Force rising above 480 kN (warning) while ROLL.RPM drops indicates roll seizure developing. Both together = roll_seizure scenario.

---

## 4. Operating Limits

| Condition | Limit | Action |
|-----------|-------|--------|
| ROLL.RPM = 0 (alarm) | Any one roll | Reduce casting speed to min (<0.5 m/min); end heat if liquid core zone |
| FORCE.HYD | >480 kN (warning) | Investigate roll resistance; check spray cooling |
| FORCE.HYD | >550 kN (alarm) | End heat; withdraw segment via crane |
| BULGE | >2.0 mm (warning) | Suspect misalignment or reduced cooling; investigate spray flow |
| BULGE | >4.0 mm (alarm) | Stop casting; breakout risk; emergency procedure |
| SPRAY.FLOW | <150 L/min (warning) | Spray nozzle(s) partially blocked; increase flow or clean nozzles |
| SPRAY.FLOW | <120 L/min (alarm) | Immediate: insufficient cooling → surface cracking and shell thinning |
| VIB.ROLL | >3.5 mm/s (warning) | Roll bearing degrading; plan inspection at next segment change |
| VIB.ROLL | >6.0 mm/s (alarm) | Roll bearing failing; plan withdrawal as soon as safely possible |

---

## 5. Known Failure Modes

### 5.1 Roll Seizure — Primary and Most Dangerous Mode

**Root Cause:** Roll bearing seizure from thermal/water-scale ingress; scale packs into bearing gap, frictional heat exceeds lubricant capacity → metal-to-metal welding of rolling elements.

**Why this matters:** When a roll seizes, the strand drags over a stationary roll surface. The friction marks a defect band at periodic intervals across the slab width. In the liquid core zone (Seg 7), this can tear the thin solidified shell → breakout.

**Degradation Timeline:**
- Normal: ROLL.RPM = 14 RPM, FORCE.HYD = 300 kN
- Warning: FORCE.HYD rising (300 → 480 kN); ROLL.RPM slowing (14 → 1 RPM warning)
- Alarm: ROLL.RPM = 0 RPM; FORCE.HYD = 540 kN; transverse crack risk

**Sensor Signature:**
- ROLL.RPM: 14 → 0 (alarm)
- FORCE.HYD: 300 → 540 kN (alarm)

**Fault Codes:** ROLL-SEIZE, SEG-FORCE-HIGH
**Cost Impact:** INR 8,000,000 / USD 96,000 (range $80k–$200k, 8 h unplanned)
**Safety Class:** P2

### 5.2 Roll Bearing Failure

**Root Cause:** Bearing fatigue/contamination failure (separate from seizure — bearing fails internally but roll may still rotate slowly). Scale contamination via failed bearing seal is the primary aggravator. Spherical roller bearing (SRB) used in segment rolls tolerates misalignment and thermal expansion.

**Signature:** VIB.ROLL rising 2.0 → 3.5 → 6.0 mm/s; FORCE.HYD slightly elevated; ROLL.RPM normal until late-stage.

**Action:** Plan segment withdrawal and roll bearing replacement (BRG-SEG-01). Unlike seizure, bearing failure is detectible weeks ahead.

### 5.3 Spray Nozzle Blockage

**Root Cause:** Scale accumulation inside nozzle orifices; deposits from high-hardness cooling water; nozzle cracking from thermal cycling.

**Signature:** SPRAY.FLOW drops below 180 → 150 → 120 L/min; local temperature sensors (if fitted) would show strand surface hot spot. Strand defects (surface cracks) follow if cooling inadequate.

**Action:** Clean or replace spray nozzles (NOZ-SPRAY-01; 50 in stock, lead time = 0). Nozzle cleaning can be attempted during scheduled stop with high-pressure water jet.

### 5.4 Segment Misalignment / Strand Bulging

**Root Cause:** Hydraulic cylinder drift causing unequal gap between fixed and loose frames; thermal distortion after segment damage; incorrect reassembly after overhaul.

**Signature:** BULGE deviation rising > 1.0 mm; FORCE.HYD asymmetric between left and right hydraulics; slab centre segregation quality indicator rises.

**Action:** Hydraulic gap recalibration; segment alignment check via laser/template; compare actual gap to soft-reduction schedule.

---

## 6. Preventive Maintenance Schedule

| Task | Interval | Method | Notes |
|------|----------|--------|-------|
| Online monitoring: FORCE, ROLL.RPM, SPRAY.FLOW, BULGE | Continuous 1–10 Hz | SCADA/PLC | All signals to caster automation |
| Spray nozzle inspection + flow test | Per campaign (typically weekly) | Flow test bench | Replace clogged nozzles (NOZ-SPRAY-01) |
| Roll rotation check (encoder verify) | Per campaign | Encoder health check | Drift or constant reading = failed encoder; replace before seizure is missed |
| Roll surface inspection (visual) | Every segment change | Visual during disassembly | Flats, scoring, circumferential cracks |
| Bearing clearance measurement | At roll replacement | Dial indicator | Compare to OEM clearance spec |
| Hydraulic system pressure test | After each segment change | Hydraulic test rig | Test to 1.25× rated pressure; hold 5 min |
| Segment geometry check (gap + taper) | At overhaul | Laser + template | ±0.1 mm per soft-reduction schedule |
| Full segment overhaul (rolls, bearings, frames) | Every 200,000–400,000 tonnes throughput (OEM guideline) | Dedicated segment repair bay | Complete disassembly; measure all critical dimensions |

---

## 7. Troubleshooting

### T1 — ROLL.RPM = 0 (Seizure Alarm)

1. **Immediately reduce casting speed** to minimum (≤0.5 m/min) to reduce friction force on seized roll.
2. If strand is in liquid core zone: call for **end of heat** — tundish gate to minimum; do not add new steel.
3. Allow heat to end naturally; do not force emergency stop unless breakout indicators also present.
4. After heat ends: allow slab to cool 2–4 hours minimum before segment area entry.
5. Withdraw segment via overhead handling crane using certified lifting fixtures.
6. Replace seized roll (ROLL-SEG-STD) + bearing (BRG-SEG-01); clean spray nozzles.
7. Inspect rolls adjacent to seized roll for drag damage.
8. Set segment gap per slab format and soft-reduction schedule; pressure-test hydraulics before return.

### T2 — SPRAY.FLOW < 150 L/min (Warning)

1. Identify which nozzle zone is low — zone-level flow meters identify blocked circuit.
2. At next scheduled stop (ideally within 1 heat): clean or replace blocked nozzles (NOZ-SPRAY-01).
3. Do NOT continue multiple heats with severely reduced cooling — surface crack rate increases.
4. If SPRAY.FLOW < 120 L/min (alarm): abort heat; cooling is insufficient to maintain shell integrity.

### T3 — FORCE.HYD > 480 kN (Warning) with Normal RPM

1. Suspect scale build-up between rolls and strand surface increasing friction.
2. Verify BULGE — if elevated, may be abnormal soft-reduction requirement; check schedule.
3. Monitor trend: if force rises AND RPM slows together = seizure developing; action as T1.
4. If force rises alone: investigate hydraulic control (sticking cylinder position sensor or valve).

---

## 8. Corrective Maintenance — Segment Change and Roll Replacement

**Required Spares:**
| Part ID | Description | Stock | Lead Time |
|---------|-------------|-------|-----------|
| ROLL-SEG-STD | Strand guide roll (standard diameter) | 2 | 12 weeks |
| BRG-SEG-01 | Segment roll bearing | 4 | 8 weeks |
| NOZ-SPRAY-01 | Spray nozzle (consumable) | 50 | Stock |

**ROLL-SEG-STD note:** 12-week lead with only 2 in stock. Monitor bearing vibration ahead of forced changes; pre-order to maintain ≥4 in stock for critical segment zones.

**Unplanned TTR:** 8 hours
**Cost Impact:** USD 96,000 (range $80k–$200k)
**Safety Class:** P2

---

## 9. Safety

- **Liquid-metal exclusion zone:** During casting operations, ALL segment areas within 10 m of liquid core are designated red zones; minimum PPE = full-length aluminised coat, face shield, metatarsal boots.
- **Strand breakout risk:** If ROLL.RPM alarm coincides with BULGE alarm AND MOULD.TC.DELTA alarm: treat as breakout condition; evacuate caster floor level immediately.
- **High-temperature surfaces:** After heat end, segment rolls and frames are 400–900 °C; wait for IR confirmation <200 °C before touching with gloves; minimum 2–4 hours cooling.
- **Hydraulic energy:** Segment clamp cylinders at up to 350 bar; depressurise to zero and tag before loosening any hydraulic connection; stored energy in accumulator = fatal if released uncontrolled.
- **Crane operations:** Segment mass typically 15–30 tonnes; certified crane + OEM handling frame; never improvise lifting points.
- **Hot water / steam:** Secondary cooling water at 10–15 bar and elevated temperature; depressurise and drain before segment is cold enough to disassemble.
