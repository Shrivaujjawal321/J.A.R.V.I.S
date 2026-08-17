# Equipment Manual: Rolling Mill Work Roll Bearing (Oil-Film + Roller Neck)
**Asset ID:** HSM.F3.WR.BRG01
**Equipment Class:** rolling_mill_work_roll_bearing
**Document:** MAN-001 | Rev 1.0 | Site: TATA_JSR (Synthetic Reference)
**Standard References:** ISO 15243:2017, ISO 20816-3:2022, ISO 4406:2021, ASTM E2374-14

> **DISCLAIMER — SYNTHETIC DOCUMENT.** All numeric values are representative industry estimates grounded in the cited standards and research briefs (research/machinery/01, 17-20). Site-specific calibration is mandatory before any production use. No proprietary Tata Steel data is used.

---

## 1. Equipment Description

The HSM.F3.WR.BRG01 is the drive-end (DE) work-roll chock bearing assembly installed in Hot Strip Mill Finishing Stand 3 (F3). The assembly combines:

- **Oil-film (hydrodynamic) bearing** in the chock housing providing the primary radial support via a hydrodynamic oil wedge at operating speed.
- **Four-row cylindrical roller neck bearing** (SKF OFB roll-neck series) carrying the roll during low-speed and reversal transients when the oil film cannot be fully maintained.

**Manufacturer:** SKF
**Model:** Oil-film bearing + 4-row cylindrical roller neck bearing
**Rated Speed:** 600 RPM
**Process Stage:** Hot rolling (finishing pass; ~850–1000 °C strip entry temperature)
**Criticality:** 1 (production-critical; no standby unit)
**Installation Date:** 2020-04-12
**Last Overhaul:** 2024-09-03

---

## 2. Technical Specifications

| Parameter | Value |
|-----------|-------|
| Bearing type | Oil-film hydrodynamic + 4-row cylindrical roller (neck) |
| Bore (nominal roll neck dia) | ~500–700 mm (F3 stand) |
| Housing material | Cast steel chock with hardened journal bore |
| Lube system | Forced circulating mineral oil, ISO VG 220 (roll-neck journal oil circuit) |
| Oil supply pressure | 2.5–5 bar (ring main to chock ports) |
| Oil supply temp (inlet) | 40–55 °C |
| Oil film outlet temp normal | 50–65 °C |
| Oil film outlet temp warning | 75 °C |
| Oil film outlet temp alarm | 85 °C |
| Operating speed range | 10–600 RPM |
| Rated load (radial) | Per stand rolling force; typically 10–40 MN on backup roll chocks, significantly lower on work rolls |
| Seal type | Labyrinth (grease-purged) |

---

## 3. Sensor Instrumentation

All sensor tags, units, and alarm levels are taken verbatim from the ground-truth spine (SPEC/ground_truth_spine.json). Thresholds must not be adjusted without a formal MOC.

| Tag | Quantity | Unit | Normal Range | Warning | Alarm | Standard |
|-----|----------|------|-------------|---------|-------|----------|
| JSR.HR.STD3.WR.BRG01.VIB.DE.H.RMS | Vibration velocity RMS | mm/s | 0.5 – 2.3 | 4.5 | 7.1 | ISO 20816-3:2022 Group 2 zones |
| JSR.HR.STD3.WR.BRG01.VIB.DE.ENV.BPFO | Envelope BPFO amplitude | g | 0.0 – 0.5 | 1.0 | 3.0 | ISO 15243:2017 |
| JSR.HR.STD3.WR.BRG01.TEMP.DE | Bearing outer-ring temperature | degC | 40 – 70 | 85 | 100 | ISO 15243:2017 §7 |
| JSR.HR.STD3.WR.BRG01.OFB.OUT.TEMP | Oil-film bearing outlet temperature | degC | 50 – 65 | 75 | 85 | SKF OFB guide |
| JSR.HR.STD3.WR.BRG01.AE.RMS | Acoustic emission RMS | dBuV | −2 – +2 | 6 | 12 | ASTM E2374-14 |

**Note on alarm priority (ISA-18.2-2016):**
- AE.RMS is the **leading indicator** — it crosses the warning threshold 6–8 weeks before any vibration change is detectable. The progression is: AE → BPFO envelope → broadband vibration → temperature.
- Temperature at alarm level (≥100 °C) is a Zone D/late-stage indicator requiring immediate controlled stop.

---

## 4. Operating Limits

| Condition | Limit | Action |
|-----------|-------|--------|
| VIB.DE.H.RMS Zone B | 2.3–4.5 mm/s | Increase monitoring frequency; check lube oil |
| VIB.DE.H.RMS Zone C | 4.5–7.1 mm/s | Reduce load 30%; notify supervisor; schedule inspection within 4 h |
| VIB.DE.H.RMS Zone D | >7.1 mm/s | Controlled stop; LOTO; inspect bearing |
| TEMP.DE | >100 °C | Immediate controlled stop (not emergency trip) |
| OFB.OUT.TEMP | >85 °C | Trip oil-film bearing; stop roll |
| VIB.DE.ENV.BPFO | >3.0 g | BPFO alarm; roll change at next opportunity |
| AE.RMS | >12 dBuV | AE alarm; combine with VIB/TEMP before forced stop |

---

## 5. Known Failure Modes

### 5.1 Outer-Race Fatigue Spall (BPFO) — Primary Mode

**ISO 15243:2017 Classification:** Surface-origin or subsurface-origin rolling-contact fatigue

**Degradation Timeline:**
- Weeks 0–6: Healthy baseline — all sensors within normal band
- Weeks 6–8: AE.RMS rises first, crossing warning (6 dBuV) while vibration remains below threshold; BPFO envelope at 0.3 g (normal)
- Weeks 8–10: AE reaches ~8 dBuV (warning-exceeded); BPFO envelope rises 1.0 → 3.0 g; TEMP.DE begins drifting
- Hours: All three sensors alarming simultaneously; spall fragment risk

**Root Cause:** Subsurface rolling-contact fatigue initiating outer-race spall, accelerated by lubricant contamination (ISO 4406 cleanliness degradation) or inadequate oil-film thickness at low speed.

**Sensor Signature:**
- AE.RMS: +2 dBuV (normal) → +8 dBuV (stage 2 onset) → +12 dBuV (alarm)
- VIB.DE.ENV.BPFO: 0.3 g (normal) → 3.2 g (alarm)
- TEMP.DE: 58 °C (normal) → 102 °C (alarm)

**Fault Codes Generated:** VIB-BPFO-DANGER, TEMP-TRIP-100C

### 5.2 Inner-Race Fatigue Spall (BPFI)

Similar mechanism; BPFI harmonic series appears in envelope spectrum at f_BPFI and sidebands. BPFI is less common than BPFO in roll-neck service because the outer race rotates with the chock in some configurations.

### 5.3 Lubrication Starvation / Overheat

**Root Cause:** Blockage of oil-film bearing supply ports; fouled lube nozzle (LUBE-NOZ-01); pump low pressure; oil viscosity degraded. AE and temperature rise together; BPFO envelope is low.

**Signature:** TEMP.DE rising monotonically; AE.RMS elevated; VIB.DE.H.RMS at normal or slightly elevated; OFB.OUT.TEMP >75 °C (warning) with low or normal oil film outlet delta-T.

### 5.4 Oil-Film Bearing Breakdown

**Root Cause:** Oil viscosity outside ISO VG 220 ±10% band; oil contaminated with water or rolling-scale emulsion; shaft speed below minimum hydrodynamic speed causing metal-to-metal contact.

**Signature:** OFB.OUT.TEMP spike >85 °C; audible metallic contact sound; shaft position sensor (if fitted) showing deviation.

---

## 6. Preventive Maintenance Schedule

| Task | Interval | Method | Standard |
|------|----------|--------|----------|
| Online vibration monitoring (all 5 sensors) | Continuous 1 Hz | Permanent sensors → SCADA | ISO 20816-3:2022 |
| AE.RMS trend review | Weekly | CMMS report | ASTM E2374-14 |
| Lube oil sample (viscosity, Fe ppm) | Monthly | Lab or inline | ISO 4406:2021 |
| Oil-film bearing outlet temp trend | Continuous | SCADA alarm | SKF OFB guide |
| Labyrinth seal inspection + grease purge | 3-monthly | During planned stop | Playbook 01 |
| Bearing housing end-cap torque check | 6-monthly | Calibrated torque wrench | OEM specification |
| Full chock disassembly and bearing inspection | Annual or per OEM life spec | Roll shop | ISO 15243:2017 |
| Journal diameter measurement | At each chock disassembly | Micrometer; compare to H7/k6 tolerance | OEM drawing |
| Coupling element inspection | 6-monthly | Visual + Shore hardness | Spine spare CPL-EL-01 |

---

## 7. Troubleshooting

### T1 — VIB.DE.H.RMS enters Zone C (4.5–7.1 mm/s)

1. Pull FFT spectrum — confirm BPFO harmonic at n × f_BPFO (where f_BPFO = rated_rpm × Nrollers × (1 − d·cos(α)/D) / 2).
2. Check AE.RMS — if >6 dBuV, bearing damage likely confirmed.
3. Pull oil sample — if Fe ppm >15 (warning), expedite roll change.
4. Increase monitoring to 4-hourly if not yet scheduled for roll change; reduce cobble risk by avoiding high-load passes.
5. Plan roll change + chock inspection at next scheduled opportunity (do not force unplanned stop from Zone C alone).

### T2 — TEMP.DE >85 °C (warning)

1. Simultaneously check OFB.OUT.TEMP — if that is also elevated, suspect oil-film bearing feed problem.
2. Verify lube oil supply pressure to chock (should be 2.5–5 bar at ring main).
3. Check lube filter differential pressure — high DP = blocked filter (replace FLT-GBX-01 or equivalent).
4. If temperature continues rising toward 100 °C, initiate controlled stop.
5. Do NOT emergency-trip — thermal shock from sudden stop can crack outer race.

### T3 — OFB.OUT.TEMP >75 °C with normal vibration

1. Suspect oil-film supply starvation or viscosity issue; check oil specification (ISO VG 220 ±10%).
2. Check inlet oil temperature — if inlet >55 °C, oil cooler may be fouled.
3. Increase lube oil flow rate and monitor for 30 minutes.
4. If no recovery: plan controlled stop; inspect lube nozzle (LUBE-NOZ-01) for blockage.

### T4 — AE.RMS >6 dBuV (warning) with VIB and TEMP normal

1. Most likely early-stage fatigue or lubrication-starved micro-slip.
2. Do not stop immediately — increase monitoring to daily AE trend.
3. Pull oil sample; check Fe ppm.
4. Confirm BPFO envelope — if <1.0 g, continue trending; if rising toward 1.0 g, plan roll change within 1–2 weeks.

---

## 8. Corrective Maintenance Procedure (Bearing Replacement)

**Required Spares:**
| Part ID | Description | Stock | Lead Time |
|---------|-------------|-------|-----------|
| BRG-LRG-300 | Large-bore roller bearing >300mm | 1 | 8 weeks |
| SEAL-LAB-01 | Labyrinth seal set | 2 | 2 weeks |
| CPL-EL-01 | Coupling element | 1 | 2 weeks |
| LUBE-NOZ-01 | Oil-film bearing lube nozzle | 4 | 1 week |

**Planned TTR:** 5 hours | **Unplanned TTR:** 12 hours
**Cost Impact:** INR 7,500,000 / USD 90,000 (unplanned, 80–250k range per event)
**Safety Class:** P2

**Procedure:**
1. LOTO per plant LOTO procedure — confirm zero-energy state (hydraulic, electrical, mechanical).
2. Initiate controlled stop (do NOT emergency-trip when TEMP >100 °C — allow controlled thermal deceleration).
3. Drain and collect lube oil; label for analysis.
4. Remove coupling; record gap + angular offset.
5. Remove bearing housing end-caps; photograph bearing in situ.
6. Use hydraulic bearing puller — NEVER strike bearing directly.
7. Measure journal diameter with micrometer — compare to OEM H7/k6 tolerance; send shaft for regrind if worn beyond tolerance.
8. Inspect housing bore with bore gauge; compare to OEM G7 housing fit.
9. Wash removed bearing in clean solvent; classify failure mode per ISO 15243:2017.
10. Clean all surfaces to Ra <1.6 µm.
11. Induction-heat new bearing to 80–100 °C (never exceed 120 °C); fit — should slide by hand.
12. Torque end-cap bolts to OEM specification (calibrated torque wrench).
13. Replace labyrinth seal set (SEAL-LAB-01) and coupling element (CPL-EL-01).
14. Reconnect lube lines; set oil flow per OEM (typically 0.5–2 L/min per bearing); prime before start.
15. Perform laser alignment — target <0.05 mm TIR.
16. Return to service: verify VIB.DE.H.RMS <2.3 mm/s and TEMP.DE <70 °C at 60 minutes from restart.

---

## 9. Safety

- **High-temperature hazard:** Bearing housings retain heat >30 min post-shutdown; wear thermal gloves; use IR thermometer before contact.
- **Crush hazard:** Roll chocks weigh several tonnes; use certified crane + lifting fixtures; NEVER work beneath suspended load.
- **Oil spill/fire hazard:** Lube oil at operating temperature is a fire risk near hot strip (>850 °C); ensure oil spillage response kit on-site; hot-work permit required if grinding/welding near oil lines.
- **Rotating machinery:** Full LOTO including shaft de-rotation lock before any physical access.
- **Induction heater:** High-frequency EMF — remove all metallic implants/devices; do not exceed 120 °C bearing temperature.
