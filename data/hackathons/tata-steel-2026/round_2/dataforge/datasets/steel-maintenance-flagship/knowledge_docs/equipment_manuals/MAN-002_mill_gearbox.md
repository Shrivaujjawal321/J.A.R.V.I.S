# Equipment Manual: Mill Drive Reduction Gearbox
**Asset ID:** HSM.F1.GBX01
**Equipment Class:** mill_gearbox
**Document:** MAN-002 | Rev 1.0 | Site: TATA_JSR (Synthetic Reference)
**Standard References:** AGMA 9005-F16, ISO 4406:2021, ISO 3448 VG220, ASTM D5185

> **DISCLAIMER — SYNTHETIC DOCUMENT.** All numeric values are representative industry estimates grounded in the cited standards and research briefs. No proprietary Tata Steel data is used.

---

## 1. Equipment Description

HSM.F1.GBX01 is the main-drive reduction gearbox coupling the 6,000 kW VFD-fed AC induction motor (HSM.F1.MTR01) to Finishing Stand 1 work rolls. It provides speed reduction and torque multiplication for hot strip rolling.

**Manufacturer:** Flender
**Model:** H4SH-mill drive
**Rated Power:** 6,000 kW
**Rated Speed (input):** ~990 RPM (motor) → ~150–250 RPM (output, depending on ratio)
**Lubrication:** Forced-lube circulating system, ISO VG 220 EP gear oil
**Process Stage:** Hot rolling
**Criticality:** 1
**Installation Date:** 2018-06-20
**Last Overhaul:** 2023-11-15

---

## 2. Technical Specifications

| Parameter | Value |
|-----------|-------|
| Gear type | Parallel-shaft helical or double-helical |
| Module | >M20 (custom large-module) |
| Oil grade | ISO VG 220 EP (AGMA 9005-F16 Severity 5+) |
| Oil volume | ~500–1000 L sump |
| Forced-lube pump pressure | 2.5–4.0 bar (normal); alarm <2.0 bar |
| Gear tooth backlash (new) | 0.1–0.3 mm |
| Contact pattern (acceptance) | >70% face width (Prussian-blue test) |
| Design service factor | AGMA SF ≥ 1.4 (mill service) |
| Rated gear-mesh frequency (GMF) | f_GMF = (input RPM / 60) × number of teeth (teeth-count plant-specific) |

---

## 3. Sensor Instrumentation

| Tag | Quantity | Unit | Normal Range | Warning | Alarm | Standard |
|-----|----------|------|-------------|---------|-------|----------|
| JSR.HR.STD1.GBX01.VIB.GMF.RMS | GMF band vibration RMS | mm/s | 0.5 – 4.0 | 6.0 | 10.0 | AGMA 9005-F16 |
| JSR.HR.STD1.GBX01.OIL.TEMP | Oil sump temperature | degC | 45 – 65 | 80 | 90 | Playbook 02 |
| JSR.HR.STD1.GBX01.OIL.PRES | Lube oil pressure | bar | 2.5 – 4.0 | 2.2 | 2.0 | Forced-lube minimum |
| JSR.HR.STD1.GBX01.OIL.FE.PPM | Ferrous particle count | ppm | 0 – 5 | 15 | 40 | ASTM D5185 / ISO 4406:2021 |
| JSR.HR.STD1.GBX01.OIL.VISC | Kinematic viscosity at 40 °C | cSt | 198 – 242 | 180 | 265 | ISO 3448 VG220 ±10% |

**Alarm logic note:** Oil pressure is a **lower-bound alarm** (drop to ≤2.0 bar = alarm). Oil viscosity has both low (180 cSt, thinned = degraded/contaminated) and high (265 cSt, thickened = cold/oxidised) alarm limits.

---

## 4. Operating Limits

| Condition | Limit | Action |
|-----------|-------|--------|
| GMF.RMS Zone B | 4.0–6.0 mm/s | Increase oil sampling to weekly; trend GMF sidebands |
| GMF.RMS Zone C | 6.0–10.0 mm/s | Reduce load; pull emergency oil sample; notify engineering |
| GMF.RMS Zone D | >10.0 mm/s | Immediate controlled stop; inspect internals |
| OIL.TEMP | >90 °C | Stop and isolate; check oil cooler / lube pump |
| OIL.PRES | ≤2.0 bar | Immediate shutdown alarm (lube starvation) |
| OIL.FE.PPM | >40 ppm | Stop; drain, investigate gear/bearing damage source |
| OIL.VISC | <180 or >265 cSt | Oil change; do NOT operate until viscosity restored |

---

## 5. Known Failure Modes

### 5.1 Gear Tooth Wear — GMF Sideband Growth

**Root Cause:** Gradual abrasive wear of gear flanks from contaminated lubricant or inadequate EHL film; GMF sidebands grow symmetrically at f_GMF ± n × f_shaft.

**Signature:** OIL.FE.PPM gradually rising (3 → 15 ppm warning); GMF.RMS rising 2.8 → 6 mm/s; viscosity possibly drifting below 198 cSt.

**Detectability:** Early via oil analysis (ferrography shows platelets vs. chunks). Vibration lags oil cleanliness by weeks.

### 5.2 Gear Tooth Fatigue Crack — Primary Failure Mode

**Degradation Timeline:**
- Weeks 0–8: Healthy baseline — GMF.RMS 2.8 mm/s; OIL.FE.PPM 3 ppm
- Weeks 8–10: Cepstrum rahmonics rise; GMF sidebands grow; OIL.FE.PPM → 15 ppm (warning)
- Alarm: Chip detector triggers; spall debris; OIL.FE.PPM → 60 ppm
- Failure: Tooth fracture → shaft risk; catastrophic

**Root Cause:** Tooth-root fatigue crack from prior high-torque cobble event; cyclic bending stress exceeds endurance limit at root fillet.

**Sensor Signature:**
- VIB.GMF.RMS: 2.8 → 11.0 mm/s (alarm)
- OIL.FE.PPM: 3 → 60 ppm (alarm)

**Fault Codes:** GMF-DANGER, CHIP-DETECT-ALARM

**Cost Impact:** INR 50,100,000 / USD 600,000 (range $500k–$3M, 168 h unplanned)
**Safety Class:** P2

### 5.3 Gear Scuffing / Micropitting

**Root Cause:** Breakdown of EHL film during overload or incorrect oil viscosity; instantaneous metal-to-metal welding followed by tearing (scuffing) or superficial contact-fatigue pits (micropitting). Micropitting dulls tooth flanks; scuffing can remove metal in large patches.

**Signature:** Oil temperature spike; GMF vibration unstable; oil discoloration; Fe ppm rise; visual tooth examination shows dull matte finish (micropitting) or torn surface with directional scoring (scuffing).

### 5.4 Oil Oxidation / Varnish

**Root Cause:** High-temperature operation (>65 °C sustained) degrades ISO VG 220 EP oil; oxidation products form insoluble varnish deposits on internal surfaces, blocking lube nozzles and filter.

**Signature:** OIL.VISC rising above 242 cSt; oil darkens / smell changes; OIL.PRES drop as nozzles clog; OIL.TEMP rise (reduced cooling).

---

## 6. Preventive Maintenance Schedule

| Task | Interval | Method | Notes |
|------|----------|--------|-------|
| Online vibration (GMF band) monitoring | Continuous 1 Hz | Permanent accelerometer | Trend GMF + sidebands |
| Oil temperature and pressure monitoring | Continuous 1 Hz | SCADA | Alarm on any deviation |
| Oil sample — ferrography + ASTM D5185 | Monthly | Lab or inline | Fe ppm, viscosity, acidity |
| Oil filter element replacement (FLT-GBX-01) | 3-monthly or ΔP alarm | Planned stop | Always stock 3 elements |
| Oil change (OIL-VG220, 200 L drum) | Annually or on viscosity alarm | Planned shutdown | Flush sump before refill |
| Chip detector inspection/clean | Monthly | Routine | During oil sampling |
| Gear visual inspection (borescope) | Every 2 years or on GMF alarm | Planned overhaul | Prussian-blue contact check |
| Tooth-flank metrology (CMM / profile gauge) | At overhaul | Metrology lab | Compare to acceptance tolerances |
| Backlash measurement | At overhaul | Dial gauge / feeler gauge | Spec: 0.1–0.3 mm |
| Bearing replacement (BRG-GBX-SET) | Per OEM life or vibration alarm | Planned overhaul | L10 life typically 30,000 h |

---

## 7. Troubleshooting

### T1 — GMF.RMS > 6.0 mm/s (warning)

1. Pull full vibration spectrum — confirm GMF harmonics + sideband index (ratio of sideband to GMF amplitude).
2. Pull emergency oil sample — if OIL.FE.PPM >15, defect is advanced; reduce load and expedite shutdown.
3. If sideband index >0.3 (engineering rule): plan shutdown within 48 h; do not allow cobble events.
4. If GMF.RMS >10 mm/s: immediate controlled stop.

### T2 — OIL.FE.PPM > 15 ppm (warning)

1. Confirm Fe ppm with lab ferrography — distinguish platelets (wear) vs. chunks (fracture).
2. If chunks present: immediate controlled stop; tooth fracture likely.
3. If platelets only: change oil filter (FLT-GBX-01); schedule oil change; increase monitoring.

### T3 — OIL.PRES ≤ 2.2 bar (warning)

1. Check lube pump operation — verify pump running at correct speed/displacement.
2. Check oil filter DP — if high, change filter.
3. Check main supply valve position.
4. If pressure drops to ≤2.0 bar: stop gearbox immediately — lube starvation will destroy gear bearings within minutes.

### T4 — OIL.TEMP > 80 °C (warning)

1. Check oil cooler flow (cooling water flow / temperature).
2. Check oil volume in sump (low level = poor cooling).
3. Reduce load if possible.
4. If temperature hits 90 °C: stop; inspect cooler for fouling; drain and analyse oil.

---

## 8. Corrective Maintenance — Gear Wheel Replacement

**Required Spares:**
| Part ID | Description | Stock | Lead Time |
|---------|-------------|-------|-----------|
| GEAR-WHL-M20 | Custom large-module gear wheel | 0 | 36 weeks |
| BRG-GBX-SET | Gearbox input/output bearing set | 1 | 3 weeks |
| FLT-GBX-01 | Gearbox oil filter element | 3 | Stock |
| OIL-VG220 | ISO VG 220 EP gear oil (200 L drum) | 4 | Stock |
| CPL-EL-01 | Coupling element | 1 | 2 weeks |

**CRITICAL NOTE:** GEAR-WHL-M20 has a 36-week procurement lead time with 0 units currently in stock. A tooth fracture event without a pre-positioned spare results in ~168 hours unplanned downtime minimum.

**Unplanned TTR:** 168 hours (7 days)
**Cost Impact:** INR 50,100,000 / USD 600,000 (up to $3M for extended swap)
**Safety Class:** P2

**Procedure:**
1. Immediate controlled stop; do NOT allow continued running with tooth fracture (secondary shaft damage).
2. LOTO — confirm zero energy; drain all oil.
3. Remove gearbox via overhead crane to dedicated repair bay.
4. Disassemble to access gear wheel; photograph and document all damage.
5. Replace gear wheel (GEAR-WHL-M20) and bearing set (BRG-GBX-SET).
6. Set backlash 0.1–0.3 mm per OEM specification.
7. Prussian-blue contact check — must achieve >70% face width before signing off.
8. Reassemble; fill with fresh ISO VG 220 EP oil (flush sump first).
9. Run-in at low load (20% rated torque for 4 h, then 50% for 4 h) before returning to full production.
10. Take oil sample at 8 h and 24 h after return-to-service; confirm Fe ppm <5 ppm before removing from enhanced monitoring.

---

## 9. Safety

- **Oil pressure release hazard:** Forced-lube systems operate at 2.5–4.0 bar; depressurise before loosening any fittings; lube oil at 65 °C can cause burns.
- **Crush hazard:** Gearbox mass typically 20–80 tonnes for mill service; use rated crane and spreader bar; never work under suspended gearbox.
- **Oil fire hazard:** ISO VG 220 oil flash point ~200 °C; keep hot-work sparks away from oil-wetted surfaces; fire suppression (CO2 or HFC) available at gearbox bays.
- **Rotating machinery:** Do NOT enter drive zone while shaft can rotate (coupling keyed on shaft + LOTO lock required).
- **Noise:** GMF noise levels during high-speed running can exceed 100 dB(A) at 1 m; mandatory hearing protection.
