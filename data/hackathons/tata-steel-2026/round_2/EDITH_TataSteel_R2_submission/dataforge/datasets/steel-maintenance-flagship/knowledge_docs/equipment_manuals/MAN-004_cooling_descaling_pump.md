# Equipment Manual: High-Pressure Descaling / Cooling-Water Pump
**Asset IDs:** HSM.DSC.PMP01 (HP Descaling Pump) | BF.CW.PMP02 (BF Cooling-Water Pump)
**Equipment Class:** cooling_descaling_pump
**Document:** MAN-004 | Rev 1.0 | Site: TATA_JSR (Synthetic Reference)
**Standard References:** HI 9.6.1-2017, HI 9.6.7-2021, ISO 10816-7:2009, ISO 15243:2017, ASTM E2374-14

> **DISCLAIMER — SYNTHETIC DOCUMENT.** All numeric values are representative industry estimates grounded in the cited standards. No proprietary Tata Steel data is used.

---

## 1. Equipment Description

This manual covers two centrifugal pump assets sharing the `cooling_descaling_pump` equipment class:

### 1.1 HSM.DSC.PMP01 — HP Descaling Pump
Removes mill scale from hot slab surface upstream of rolling. Operates at extremely high pressure (~200 bar) with scale-laden water — a highly abrasive service.

**Manufacturer:** KSB | **Model:** Multitec HP
**Rated Power:** 1,200 kW | **Rated Speed:** 1,485 RPM
**Process Stage:** Hot rolling (descaling station)
**Criticality:** 2

### 1.2 BF.CW.PMP02 — Blast Furnace Cooling-Water Pump
Large double-suction centrifugal pump circulating cooling water to blast furnace tuyeres, bosh, belly, and stack cooling elements. BF cooling failure is a Tier-1 safety/production event.

**Manufacturer:** KSB | **Model:** Omega double-suction
**Rated Power:** 900 kW | **Rated Speed:** 990 RPM
**Process Stage:** Iron making (blast furnace)
**Criticality:** 1

---

## 2. Technical Specifications

### HSM.DSC.PMP01 — HP Descaling

| Parameter | Value |
|-----------|-------|
| Pump type | Multi-stage high-pressure centrifugal |
| Discharge pressure (design) | ~200 bar |
| Flow rate (design) | ~400 m³/hr |
| Impeller material | Duplex stainless steel (abrasion-resistant) |
| Seal type | Mechanical seal, SiC/SiC faces |
| Bearing type | Rolling element (angular contact) |
| NPSH available | Must exceed NPSHr at all times (HI 9.6.1-2017) |

### BF.CW.PMP02 — Cooling-Water

| Parameter | Value |
|-----------|-------|
| Pump type | Double-suction centrifugal |
| Rated head | ~60–80 m (design) |
| Impeller material | Cast iron / bronze (clean water) |
| Seal type | Mechanical seal or packing |
| Bearing type | Rolling element (spherical roller, grease-lubricated) |

---

## 3. Sensor Instrumentation

### HSM.DSC.PMP01

| Tag | Quantity | Unit | Normal Range | Warning | Alarm | Standard |
|-----|----------|------|-------------|---------|-------|----------|
| JSR.HR.DSC.PMP01.PRES.SUC | Suction pressure | kPa | 120 – 250 | 90 | 70 | HI 9.6.1-2017 (NPSH) |
| JSR.HR.DSC.PMP01.PRES.DIS | Discharge pressure | bar | 190 – 210 | 175 | 165 | HI 9.6.7-2021 |
| JSR.HR.DSC.PMP01.AE.RMS | AE broadband RMS | dB | −2 – +2 | 8 | 15 | ASTM E2374-14 (cavitation 100–500 kHz) |
| JSR.HR.DSC.PMP01.VIB.CAS.RMS | Casing vibration RMS | mm/s | 0.5 – 1.5 | 2.5 | 5.0 | ISO 10816-7:2009 |
| JSR.HR.DSC.PMP01.FLOW.DIS | Discharge flow | m³/hr | 388 – 412 | 372 | 352 | Pump curve ±3% |
| JSR.HR.DSC.PMP01.TEMP.BRG | Bearing temperature | degC | 40 – 70 | 85 | 100 | ISO 15243:2017 |

**Suction pressure note:** Lower suction = worse; drop below 70 kPa → cavitation onset (NPSH margin lost). AE.RMS is the sensitive cavitation indicator in the 100–500 kHz band (ASTM E2374-14).

### BF.CW.PMP02

| Tag | Quantity | Unit | Normal Range | Warning | Alarm | Standard |
|-----|----------|------|-------------|---------|-------|----------|
| JSR.BF.CW.PMP02.VIB.1X | Vibration 1× radial | mm/s | 0.5 – 1.8 | 2.8 | 5.6 | ISO 10816-7:2009 |
| JSR.BF.CW.PMP02.HEAD.DEV | Differential head deviation | % | −3 – +3 | −7 | −12 | HI 9.6.7-2021 |
| JSR.BF.CW.PMP02.TEMP.BRG | Bearing temperature | degC | 40 – 70 | 85 | 100 | ISO 15243:2017 |
| JSR.BF.CW.PMP02.VIB.BB | Broadband vibration RMS | mm/s | 0.5 – 1.5 | 2.5 | 5.0 | ISO 10816-7:2009 (seal) |

**HEAD.DEV note:** Negative deviation = head has dropped vs. design curve → impeller wear or recirculation. This is a lower-bound alarm (−12% alarm).

---

## 4. Operating Limits

### HSM.DSC.PMP01

| Condition | Limit | Action |
|-----------|-------|--------|
| PRES.SUC | <90 kPa (warning) | Check suction strainer; suspect air ingress or valve partially closed |
| PRES.SUC | <70 kPa (alarm) | Stop pump — cavitation occurring; damage accumulating at every second of operation |
| PRES.DIS | <175 bar (warning) | Suspect worn impeller or partially blocked nozzles |
| AE.RMS | >8 dB (warning) | Cavitation developing; increase suction pressure immediately |
| AE.RMS | >15 dB (alarm) | Stop pump immediately; cavitation causing impeller erosion |
| VIB.CAS.RMS | >5.0 mm/s | Stop pump; inspect bearing and mechanical seal |
| TEMP.BRG | >100 °C | Controlled stop; seal failure or lube loss |

### BF.CW.PMP02

| Condition | Limit | Action |
|-----------|-------|--------|
| VIB.1X | >2.8 mm/s (warning) | Check impeller balance; pull vibration spectrum |
| HEAD.DEV | <−7% (warning) | Suspect impeller wear; plan inspection |
| HEAD.DEV | <−12% (alarm) | Inspect impeller (IMP-CW-01); replace wear rings (WRING-CW-01) |
| TEMP.BRG | >85 °C | Inspect bearing lubrication |
| TEMP.BRG | >100 °C | Stop; replace bearing |
| VIB.BB | >5.0 mm/s | Mechanical seal failing (broadband = seal rattle) |

---

## 5. Known Failure Modes

### 5.1 Cavitation (HSM.DSC.PMP01)

**Root Cause:** Suction pressure drop below NPSHr (net positive suction head required); vapour bubbles form and collapse violently at impeller vanes, eroding material.

**Physics:** Bubble collapse generates local pressures of 1,000+ bar in microseconds; removes impeller material at vane leading edge (pitting, then deep erosion craters). Identical mechanism to water hammer.

**Degradation Timeline:**
- Onset: AE.RMS crosses 8 dB (warning); faint crackling/gravel noise; suction pressure borderline
- Developing: AE.RMS → 15 dB alarm; discharge pressure drops; flow below 372 m³/hr
- Advanced: Impeller vanes visibly pitted; flow/head characteristic shifted left on pump curve; vibration and noise severe

**Sensor Signature:**
- PRES.SUC: drops below 90 kPa → 70 kPa
- AE.RMS: crosses 8 dB → 15 dB
- FLOW.DIS: drops below 388 → 372 → 352 m³/hr

### 5.2 Mechanical Seal Failure (HSM.DSC.PMP01) — Primary Mode

**Root Cause:** Mechanical seal face wear from abrasive scale-laden water; secondary O-ring degradation from thermal cycling.

**Degradation Timeline:**
- Weeks 0–4: Healthy; weeping at stuffing box (<1 drop/min acceptable)
- Warning: Broadband VIB.CAS.RMS 1.5 → 2.5 mm/s; visible weeping increases
- Alarm: VIB.CAS.RMS >5 mm/s; spraying leak; bearing temperature rising
- Failure: Seal blowout; uncontrolled release of 200-bar water

**Sensor Signature:**
- VIB.CAS.RMS: 1.0 → 5.4 mm/s (alarm)
- TEMP.BRG: 58 → 90 °C (alarm)

**Fault Code:** VIB-SEAL-DANGER
**Planned TTR:** 3 hours | **Unplanned TTR:** 8 hours | **Cost Impact:** INR 1,200,000 / USD 14,400
**Safety Class:** P3

### 5.3 Impeller Wear / Erosion (Both Pumps)

**Root Cause:** Abrasive particles (scale, silica, iron oxide) in water erode impeller vanes progressively, degrading pump performance (head and flow decrease).

**Signature (HSM.DSC.PMP01):** PRES.DIS drops gradually 200 → 175 bar; FLOW.DIS drops; AE.RMS normal (not cavitation — erosion is quieter).

**Signature (BF.CW.PMP02):** HEAD.DEV drifts negative −3% → −7% → −12%; vibration slightly elevated from impeller mass imbalance as vanes wear asymmetrically.

### 5.4 Pump Bearing Failure (Both Pumps)

Same rolling-element bearing failure mechanism as MAN-001. TEMP.BRG and VIB are the primary indicators. See Playbook 01 in repair playbooks for detailed procedure.

### 5.5 Unbalance (BF.CW.PMP02)

**Root Cause:** Impeller fouling with scale buildup on one side creating mass imbalance.

**Signature:** VIB.1X elevated (1× shaft frequency dominant); responds to trim balance or cleaning.

---

## 6. Preventive Maintenance Schedule

| Task | Interval | Pump | Notes |
|------|----------|------|-------|
| Online vibration + pressure + flow monitoring | Continuous 1 Hz | Both | SCADA |
| AE monitoring (cavitation check) | Continuous 1 Hz | DSC.PMP01 | 100–500 kHz band |
| Mechanical seal inspection + leak check | Weekly | Both | Visual; quantify drops/min |
| Suction strainer cleaning | Monthly or ΔP | DSC.PMP01 | Prevents NPSH margin loss |
| Bearing re-greasing | Per OEM schedule | Both | Over-greasing causes overheating |
| Impeller inspection (head deviation check) | 6-monthly | Both | Compare to pump curve |
| Mechanical seal cartridge replacement (SEAL-MECH-DSC) | On weeping increase or 6-monthly for HP service | DSC.PMP01 | Stock 2 units |
| Shaft sleeve inspection (SLV-SHAFT-01) | At seal change | DSC.PMP01 | Replace if >0.1 mm scoring |
| Impeller replacement (IMP-DSC-01 / IMP-CW-01) | On head-deviation alarm | Both | 8-week / 6-week lead |
| Wear ring replacement (WRING-CW-01) | On head alarm or at impeller change | BF.CW.PMP02 | Stock 2 sets |
| Full pump overhaul | Every 3 years or 25,000 h | Both | OEM scheduled overhaul |

---

## 7. Troubleshooting

### T1 — Cavitation (AE.RMS > 8 dB, PRES.SUC < 90 kPa)

1. Immediately increase suction pressure: open suction valve fully; check suction strainer for blockage.
2. Reduce pump speed if on VFD, reducing flow demand.
3. If AE.RMS reaches 15 dB: stop pump; severe cavitation = rapid impeller destruction.
4. Post-event: inspect impeller for pitting; replace (IMP-DSC-01) if pits >2 mm depth.
5. Root cause: measure actual NPSHa at design flow; compare to pump curve NPSHr + 0.5 m margin.

### T2 — Mechanical Seal Leak (VIB.CAS.RMS > 2.5 mm/s, TEMP.BRG rising)

1. Switch to standby pump; isolate PMP01 with suction and discharge valves.
2. LOTO; relieve pressure; drain casing.
3. Back-pullout seal change (SEAL-MECH-DSC, stock 2 units, 2-week lead for replenishment).
4. Inspect shaft sleeve (SLV-SHAFT-01) — replace if scoring >0.1 mm.
5. Install new SiC/SiC cartridge seal; handle lapped SiC seal faces clean and fingerprint-free without gloves — bare-hand oils can affect face seating and gloves introduce particles; clean faces with lint-free wipe + approved solvent before assembly.
6. Shaft runout check: <0.05 mm TIR before assembly.
7. Return to service; confirm VIB.CAS.RMS <1.5 mm/s and no leak within 30 min.

### T3 — Head Deviation Alarm (BF.CW.PMP02 HEAD.DEV < −7%)

1. Plot current operating point (actual head vs. flow) on pump design curve.
2. Check if deviation is actual performance loss vs. changed system resistance.
3. If performance curve has shifted: impeller wear likely; plan inspection.
4. Inspect wear rings (WRING-CW-01) — clearance >2× design = significant recirculation.
5. Replace impeller (IMP-CW-01) if vane erosion >20% original profile.

---

## 8. Corrective Maintenance — Mechanical Seal Change

**Required Spares (HSM.DSC.PMP01):**
| Part ID | Description | Stock | Lead Time |
|---------|-------------|-------|-----------|
| SEAL-MECH-DSC | Mechanical seal cartridge SiC/SiC | 2 | 2 weeks |
| SLV-SHAFT-01 | Pump shaft sleeve | 1 | 3 weeks |
| IMP-DSC-01 | Descale pump impeller | 1 | 8 weeks |

**Required Spares (BF.CW.PMP02):**
| Part ID | Description | Stock | Lead Time |
|---------|-------------|-------|-----------|
| IMP-CW-01 | Cooling pump impeller (double-suction) | 1 | 6 weeks |
| WRING-CW-01 | Wear ring set | 2 | 4 weeks |
| SEAL-MECH-DSC | Mechanical seal | 2 | 2 weeks |

---

## 9. Safety

- **High-pressure hazard (DSC.PMP01):** 200-bar water release is lethal; verify pressure gauge reads zero AND open drain before loosening any bolts; use pressure rating–compliant PPE (face shield, leather apron).
- **LOTO:** Both suction and discharge isolation valves must be closed, locked, and tagged; pump casing must be fully depressurised and drained before access.
- **Rotating parts:** Pump shaft is driven by 1200/900 kW motor; shaft cannot free-rotate after LOTO only if coupling removed or mechanical brake applied.
- **Hot water:** BF cooling-water may be at 50–60 °C; allow 30 min cooling before opening casing.
- **Seal face handling:** SiC faces are brittle and extremely fragile; handle only with protective packaging; do not use gloves during face-to-face alignment — keep faces clean and fingerprint-free, as bare-hand oils can affect face seating and gloves introduce particles.
- **Confined-space:** Pump pits may require confined-space entry permit (oxygen deficiency check before entry).
