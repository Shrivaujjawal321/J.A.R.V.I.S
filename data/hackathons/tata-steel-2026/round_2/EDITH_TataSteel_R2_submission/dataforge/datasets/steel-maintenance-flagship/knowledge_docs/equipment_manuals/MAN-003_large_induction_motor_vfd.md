# Equipment Manual: Large MV AC Induction Motor (VFD-Fed)
**Asset ID:** HSM.F1.MTR01
**Equipment Class:** large_induction_motor_vfd
**Document:** MAN-003 | Rev 1.0 | Site: TATA_JSR (Synthetic Reference)
**Standard References:** NEMA MG1-2021, IEC 60034-1, IEEE 43-2013, IEEE 1415-2006, ISO 20816-1:2016

> **DISCLAIMER — SYNTHETIC DOCUMENT.** All numeric values are representative industry estimates grounded in the cited standards. No proprietary Tata Steel data is used.

---

## 1. Equipment Description

HSM.F1.MTR01 is the main-drive AC induction motor for Hot Strip Mill Finishing Stand 1 (F1). It is fed by a medium-voltage Variable Frequency Drive (ABB ACS6000) enabling speed-controlled rolling at 0–990 RPM. The motor is directly coupled to gearbox HSM.F1.GBX01.

**Manufacturer:** ABB
**Model:** AMI 630 MV (with ACS6000 VFD)
**Rated Power:** 6,000 kW
**Rated Speed:** 990 RPM
**Rated Voltage:** Medium voltage (typically 3.3 kV or 6.6 kV)
**Bearing DE:** SKF 6326 (deep-groove ball bearing, drive end)
**Bearing NDE:** SKF 6226 (deep-groove ball bearing, non-drive end)
**Insulation Class:** F (155 °C rated; alarm at 155 °C, warning at 145 °C)
**Criticality:** 1
**Installation Date:** 2018-06-20
**Last Overhaul:** 2024-02-10

---

## 2. Technical Specifications

| Parameter | Value |
|-----------|-------|
| Motor type | Squirrel-cage induction (SCIM) |
| Poles | 6 (990 RPM at 50 Hz) |
| Supply frequency | 50 Hz (VFD variable output) |
| Slip at full load | ~1% (990 RPM sync = 1000 RPM) |
| Insulation class | F (155 °C Class F limit, IEC 60034-1) |
| Enclosure | IC411 / IP55 (TEFC) or water-jacket cooled |
| VFD type | ABB ACS6000 (cycloconverter or active-front-end) |
| AEGIS grounding rings | Required (VFD shaft current mitigation) |
| Bearing lubrication | Grease — OEM specified grade for Class F |
| Re-greasing interval | Per OEM schedule (typically 4000–6000 h) |

---

## 3. Sensor Instrumentation

| Tag | Quantity | Unit | Normal Range | Warning | Alarm | Standard |
|-----|----------|------|-------------|---------|-------|----------|
| JSR.HR.STD1.MTR01.MCSA.RBAR.SB | MCSA rotor-bar sideband | dBc | −70 to −50 | −45 | −35 | IEEE 1415-2006 |
| JSR.HR.STD1.MTR01.WIND.TEMP | Stator winding temperature | degC | 80 – 130 | 145 | 155 | IEC 60034-1 Class F |
| JSR.HR.STD1.MTR01.VIB.DE.RMS | Motor body vibration RMS | mm/s | 0.5 – 2.3 | 4.5 | 7.1 | ISO 20816-1:2016 Group 2 |
| JSR.HR.STD1.MTR01.CURR.IMBAL | Phase current imbalance | % | 0 – 1 | 2 | 5 | NEMA MG1-2021 §12.45 |
| JSR.HR.STD1.MTR01.INS.PI | Polarisation Index | ratio | 2.0 – 5.0 | 2.0 | 1.5 | IEEE 43-2013 |
| JSR.HR.STD1.MTR01.VIB.2XF1 | Vibration at 2× supply frequency | mm/s | 0.0 – 0.5 | 1.0 | 2.5 | IEEE 1415-2006 (eccentricity) |

**Note on PI threshold direction:** Lower PI value is worse. PI <1.5 = alarm (IEEE 43-2013 Class F minimum). PI is an offline (de-energised) test; it cannot be continuously monitored.

**Note on MCSA.RBAR.SB direction:** Less negative (closer to 0 dBc) = worse. A sideband of −35 dBc at (f1 ± 2s·f1) confirms rotor bar damage (IEEE 1415-2006).

---

## 4. Operating Limits

| Condition | Limit | Action |
|-----------|-------|--------|
| WIND.TEMP | >145 °C (warning) | Reduce load; check VFD cooling; increase ventilation |
| WIND.TEMP | >155 °C (alarm) | Immediate controlled stop |
| VIB.DE.RMS | >7.1 mm/s | Controlled stop; inspect motor bearings |
| CURR.IMBAL | >2% (warning) | Investigate supply voltage unbalance; check connections |
| CURR.IMBAL | >5% (alarm) | Stop motor; inspect winding / connections |
| MCSA.RBAR.SB | >−45 dBc (warning) | Schedule MCSA survey at steady load; plan motor swap in 2–4 weeks |
| MCSA.RBAR.SB | >−35 dBc (alarm) | Confirm at steady load; initiate motor swap process |
| PI | <2.0 (warning) | Increase drying/cleaning; re-test within 3 months |
| PI | <1.5 (alarm) | Do NOT re-energise without engineering review |
| VIB.2XF1 | >1.0 mm/s | Suspect dynamic eccentricity; investigate air-gap |
| VIB.2XF1 | >2.5 mm/s | Controlled stop; air-gap measurement |

---

## 5. Known Failure Modes

### 5.1 Broken Rotor Bar — Primary Electrical Mode

**Degradation Timeline:**
- Weeks 0–3: Healthy — MCSA.RBAR.SB = −58 to −60 dBc; VIB.DE.RMS = 1.8 mm/s
- Weeks 3–4: MCSA sideband rises −50 → −45 dBc (warning); no vibration change yet
- Alarm stage: Sideband −35 dBc; VIB.DE.RMS = 4.8 mm/s (Zone C); 2× slip-frequency sidebands visible
- Progressive: 2–4 weeks from warning to cascading bar fractures

**Root Cause:** Rotor bar fracture from repeated high-torque starts and thermal cycling (VFD start-stop cycles). Crack initiates at bar-to-end-ring joint; sidebands at (1 ± 2s) × f1 (where s = slip fraction).

**Sensor Signature:**
- MCSA.RBAR.SB: −58 dBc (normal) → −34 dBc (alarm)
- VIB.DE.RMS: 1.8 mm/s (normal) → 4.8 mm/s (alarm)

**Fault Codes:** MCSA-RBAR-ALARM
**Planned TTR:** 10 hours (swap to standby) | **Cost Impact:** USD 100,000 (100–150k range)
**Safety Class:** P3

### 5.2 Stator Winding Turn-to-Turn Short

**Root Cause:** Insulation deterioration between adjacent coil turns (common with VFD common-mode voltage). Thermal cycling and moisture ingress accelerate degradation.

**Signature:** WIND.TEMP asymmetry (one slot hotter than others); CURR.IMBAL rising; VIB.2XF1 elevated (magnetic asymmetry). PI declining over successive offline tests.

**Progression:** Turn short → phase-to-phase fault → trip. Requires winding overhaul (RWND-KIT-MV).

### 5.3 Insulation Degradation / Ground Fault

**Root Cause:** VFD-induced high dV/dt transients erode insulation over time. Moisture, heat cycling, and contamination accelerate.

**Signature:** PI declining below 2.0 (warning) → 1.5 (alarm). Megger IR reading (not a continuous sensor — offline only). Partial discharge (PD) activity detectable on stator RTD signal noise floor if PD monitor fitted.

**Action:** PI <1.5 → do NOT re-energise without engineering sign-off; schedule rewind (RWND-KIT-MV, 3-week lead) or replacement (MTR-MV-6000, 40-week lead).

### 5.4 Rotor Eccentricity

**Root Cause:** Bearing wear allowing rotor to ride eccentric; shaft bow from prior thermal event; rotor balance loss.

**Signature:** VIB.2XF1 > 1.0 mm/s (warning); spectrum shows 2 × 50 Hz plus rotor eccentricity sidebands at f_r ± f_eccentricity. Air-gap measurement confirms.

### 5.5 Motor Bearing Spall (BPFO)

Same mechanism as rolling_mill_work_roll_bearing failure (ISO 15243:2017). Bearings SKF 6326 (DE) and 6226 (NDE). Detected via VIB.DE.RMS and BPFO envelope if motor-mounted accelerometer has envelope analysis capability.

---

## 6. Preventive Maintenance Schedule

| Task | Interval | Method | Standard |
|------|----------|--------|----------|
| Online stator temperature monitoring | Continuous 1 Hz | RTD → SCADA | IEC 60034-1 Class F |
| MCSA scan at steady load | Quarterly or on warning | MCSA instrument | IEEE 1415-2006 |
| Vibration monitoring (VIB.DE.RMS) | Continuous 1 Hz | Permanent accelerometer | ISO 20816-1:2016 |
| Phase current imbalance monitoring | Continuous 1 Hz | VFD monitoring output | NEMA MG1-2021 |
| Polarisation Index test (offline) | Annually or pre/post overhaul | Megger + PI test | IEEE 43-2013 |
| Bearing re-greasing (DE + NDE) | Per OEM schedule (4000–6000 h) | Grease gun, purge old grease | OEM spec grease |
| AEGIS grounding ring inspection | 6-monthly | Visual; measure shaft voltage | SKF/AEGIS guide |
| VFD common-mode choke / dV/dt filter check | Annually | Visual + electrical | ABB ACS6000 manual |
| Air-gap measurement (if eccentricity suspected) | When VIB.2XF1 > 1.0 mm/s | Feeler gauge at 4 points | OEM tolerance |
| Winding resistance + insulation resistance | At each overhaul | Megger + bridge | IEEE 43-2013 |

---

## 7. Troubleshooting

### T1 — MCSA.RBAR.SB > −45 dBc (warning)

1. Confirm at steady-state load (MCSA is only valid at constant speed >60% rated load).
2. Run motor at 80–100% rated load for 15 min; take MCSA spectrum; look for sidebands at f1 ± 2s·f1.
3. If confirmed: document baseline; re-test in 7 days; initiate motor swap procurement.
4. Plan motor swap within 2–4 weeks to standby (MTR-MV-6000, stock qty 1); send failed motor for rotor bar assessment.
5. Verify phase rotation before energising spare.

### T2 — WIND.TEMP > 145 °C (warning)

1. Check VFD cooling (internal fans, air filters, heat exchangers — ACS6000 has internal cooling).
2. Check ambient temperature; verify motor enclosure ventilation not blocked.
3. Reduce load by 20% for 30 min; observe temperature trend.
4. If temperature trends toward 155 °C: initiate controlled stop.

### T3 — CURR.IMBAL > 2% (warning)

1. Check line voltage balance on incoming supply (MV bus).
2. Measure voltages at all three phases at VFD input and motor terminals.
3. Inspect terminal connections for looseness/oxidation.
4. If voltage is balanced but current is not: suspect internal winding fault; PI test at next stop.

### T4 — PI < 2.0 (warning, offline test)

1. Repeat PI test after thorough cleaning and drying of winding.
2. If PI still <2.0: schedule partial discharge test.
3. Continue monitoring insulation resistance trend.
4. Do NOT run if PI <1.5.

---

## 8. Corrective Maintenance — Motor Swap Procedure

**Required Spares:**
| Part ID | Description | Stock | Lead Time |
|---------|-------------|-------|-----------|
| MTR-MV-6000 | MV insurance spare motor 6,000 kW | 1 | 40 weeks |
| BRG-MTR-SET | Motor DE+NDE bearing set (SKF 6326/6226) | 1 | 1 week |
| SEAL-LAB-01 | Labyrinth seal set | 2 | 2 weeks |
| RWND-KIT-MV | MV rewind materials (for repair of failed motor) | 1 | 3 weeks |

**Planned TTR:** 10 hours | **Cost Impact:** USD 100,000 (labour + production, not motor capital)
**Note:** MTR-MV-6000 ($450k) is a reusable rotating capital asset; the failed motor is repaired and returned to spare stock. Cost impact reflects swap labour + lost production only.
**Safety Class:** P3

**Procedure:**
1. Plan 10-hour window with production (maintenance stop or scheduled roll change).
2. LOTO: VFD de-energised; motor terminals earthed; mechanical shaft lock applied.
3. Disconnect motor cables (label all three phases for correct re-connection).
4. Remove coupling; record offset and gap measurements.
5. Rig motor for lift — verify crane SWL ≥ motor weight + 25%; use spreader bar.
6. Lift out failed motor; install insurance spare (MTR-MV-6000).
7. Align to gearbox: parallel misalignment <0.05 mm; angular <0.05 mm/100 mm; use laser alignment tool.
8. Reconnect cables — verify phase rotation with phase tester before energising.
9. Megger check: IR reading ≥ required for Class F (typically >100 MΩ at 1 kV for new motor).
10. Test-run at no-load first; verify vibration <2.3 mm/s; current balanced <1% imbalance.
11. Increase load incrementally to full; monitor WIND.TEMP and VIB for first 30 min.

---

## 9. Safety

- **Medium-voltage hazard:** MV (3.3–6.6 kV) is lethal; LOTO requires MV authorised person; test-before-touch at all terminals; use rubber matting and insulating gloves rated for MV.
- **VFD bus capacitors:** ACS6000 retains high-voltage charge after de-energising; wait minimum 5 minutes (or verify VFD discharge indicator) before touching power connections.
- **Crane and rigging:** Motor weight 15–30 tonnes; certified crane + slings + spreader bar; ground crew MUST NOT stand under suspended load.
- **Shaft rotation:** Even with VFD off, the motor shaft can be driven backwards by the mechanical load; shaft lock pin must be inserted and tagged.
- **Thermal:** Winding RTDs will read elevated temps for 30 min post-shutdown; do not confuse with active fault.
