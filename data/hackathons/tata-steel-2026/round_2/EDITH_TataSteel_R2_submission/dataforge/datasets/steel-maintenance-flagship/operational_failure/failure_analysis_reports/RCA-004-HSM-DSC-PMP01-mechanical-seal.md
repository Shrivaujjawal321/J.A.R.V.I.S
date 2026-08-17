# FAILURE ANALYSIS REPORT

**Report Number:** RCA-004
**Date of Report:** 2026-04-03
**Classification:** SYNTHETIC — physics-grounded, no proprietary Tata Steel data
**Prepared by:** Reliability Engineering, TATA_JSR Hot Rolling Division / Mechanical Maintenance
**Safety Class:** P3

---

## 1. Asset Identification

| Field | Value |
|---|---|
| Asset ID | HSM.DSC.PMP01 |
| Equipment Class | cooling_descaling_pump |
| Description | Hot Strip Mill high-pressure descaling pump (centrifugal, ~200 bar service) |
| Location | HOT_ROLLING / DESCALER / HP_DESCALE_PUMP_1 |
| Manufacturer | KSB |
| Model | Multitec HP |
| Rated Power | 1,200 kW |
| Rated Speed | 1,485 rpm |
| Criticality | 2 |
| Installation Date | 2019-08-30 |
| Last Overhaul | 2024-05-18 |

---

## 2. Failure Summary

| Field | Value |
|---|---|
| Scenario ID | SCN-040 |
| Failure Mode | mechanical_seal_failure |
| Fault Codes | VIB-SEAL-DANGER |
| Date of Incident | 2026-04-03 |
| Total Duration (warning to seal change) | ~4–8 weeks |
| Unplanned Downtime | 8 hours (leak escalation to standby switch) |
| Planned Downtime | 3 hours (back-pullout seal change) |
| Total Cost Impact | INR 1,200,000 (~USD 14,400) |

---

## 3. Symptom Timeline

### Weeks 0–4: Healthy Operation
High-pressure descaling service, 200 bar, scale-laden water (1,485 rpm). Sensor readings:
- `JSR.HR.DSC.PMP01.VIB.CAS.RMS`: 1.0 mm/s (normal 0.5–1.5 mm/s, ISO 10816-7:2009)
- `JSR.HR.DSC.PMP01.PRES.DIS`: 200 bar (normal 190–210 bar)
- `JSR.HR.DSC.PMP01.PRES.SUC`: 185 kPa (normal 120–250 kPa; NPSH adequate)
- `JSR.HR.DSC.PMP01.AE.RMS`: 0 dB (normal −2 to +2 dB, ASTM E2374-14)
- `JSR.HR.DSC.PMP01.FLOW.DIS`: 400 m³/hr (normal 388–412 m³/hr)
- `JSR.HR.DSC.PMP01.TEMP.BRG`: 58 °C (normal 40–70 °C)

### Weeks 4–6: Stage 1 — Seal Weeping, Vibration Rise
- A fine water mist observed at pump gland during operator rounds (not captured by automated sensor — relies on patrol observation).
- `JSR.HR.DSC.PMP01.VIB.CAS.RMS` begins rising: 1.0 → 2.5 mm/s. The casing vibration increase indicates the mechanical seal faces are no longer providing a concentric rotary seal; the uneven axial-face load from face wear creates a small radial imbalance transmitted to the casing.
- `JSR.HR.DSC.PMP01.AE.RMS` rises to 6 dB (still below 8 dB warning), indicating acoustic emission from liquid-phase impingement in the seal cavity — consistent with a weeping seal at 200 bar.
- Operator log: "minor seal drip, monitoring."

### Weeks 6–8: Stage 2 — Vibration Alarm, Bearing Temperature Rise
- `JSR.HR.DSC.PMP01.VIB.CAS.RMS` escalates to 5.4 mm/s, exceeding the alarm threshold of 5.0 mm/s (ISO 10816-7:2009). The seal face wear has now progressed to full-face film breakdown; contact between SiC faces is generating heat and dynamic loading.
- `JSR.HR.DSC.PMP01.TEMP.BRG`: bearing temperature rises from 58 °C to 90 °C, exceeding the warning threshold of 85 °C and approaching the alarm of 100 °C. The heat source is mechanical friction at the degraded seal faces; heat transfers axially along the shaft to the drive-end bearing.
- `JSR.HR.DSC.PMP01.AE.RMS` reaches 12 dB (above warning 8 dB), confirming seal cavity turbulence from high-pressure spray ingress.
- Standby pump `HP_DESCALE_PUMP_2` brought online; `PMP01` isolated for repair.
- Fault code VIB-SEAL-DANGER generated in SCADA.

---

## 4. Sensor Evidence Summary

| Tag | Normal Value | Defect Value | Threshold Crossed |
|---|---|---|---|
| JSR.HR.DSC.PMP01.VIB.CAS.RMS | 1.0 mm/s | 5.4 mm/s | Alarm (5.0 mm/s) |
| JSR.HR.DSC.PMP01.TEMP.BRG | 58 °C | 90 °C | Warning (85 °C) |
| JSR.HR.DSC.PMP01.AE.RMS | 0 dB | 12 dB | Warning (8 dB) |
| JSR.HR.DSC.PMP01.PRES.DIS | 200 bar | 195 bar | Within normal |
| JSR.HR.DSC.PMP01.FLOW.DIS | 400 m³/hr | 388 m³/hr | Warning lower bound |

---

## 5. Root Cause Analysis

### Primary Root Cause
**Mechanical seal face wear from abrasive scale-laden water at 200 bar service pressure.** The KSB Multitec HP operates on high-pressure descaling water that carries mill scale (iron oxide particles, typically 50–500 µm). Despite a strainer on the suction side, fine particles below strainer rating (typically 200 µm) continuously pass through the seal flush circuit. Over the 22-month service life since last overhaul (2024-05-18), these particles abrade the SiC seal faces in a three-body abrasion mechanism, progressively increasing the face-surface roughness from a designed Ra ≤ 0.1 µm (optically flat) to Ra ≈ 0.8–1.2 µm as measured at disassembly.

### Secondary Root Cause
**O-ring degradation.** The secondary seal O-ring (nitrile, NBR) showed surface cracking consistent with thermal ageing at the 85–90 °C bearing temperature seen in the final stage. The O-ring had been installed at the 2024-05-18 overhaul; 22 months at elevated temperature in the presence of water additives (biocides/inhibitors in the descaling water circuit) caused hardening and micro-cracking. The O-ring no longer provided a reliable secondary barrier once the primary SiC faces degraded.

### Why Not Cavitation?
Cavitation was considered but ruled out: suction pressure `JSR.HR.DSC.PMP01.PRES.SUC` remained above 120 kPa (NPSH adequate per HI 9.6.1-2017); acoustic emission was at frequencies associated with seal-face contact (10–100 kHz regime), not the 100–500 kHz cavitation bubble collapse signature. Discharge pressure and flow remained within normal bands until near failure.

---

## 6. Corrective Actions Taken

1. **Standby pump switchover** — PMP02 (backup descaling pump) brought online; PMP01 isolated without production interruption.
2. **LOTO** — Electrical isolation of 1,200 kW motor; mechanical lock on suction/discharge isolation valves; pressure bled to zero from casing drain.
3. **Back-pullout seal replacement:**
   - KSB Multitec HP cartridge-type seal design allows seal removal without disturbing pump casing alignment (back-pullout construction).
   - Shaft sleeve inspected: scoring depth measured 0.12 mm (specification ≤ 0.1 mm TIR), marginally over limit. Sleeve replaced (`SLV-SHAFT-01`).
   - New `SEAL-MECH-DSC` (SiC/SiC mechanical seal cartridge) installed; face surfaces wiped with lint-free cloth (fingerprint contamination causes rapid face failure at 200 bar).
   - Seal flush circuit cleaned; strainer element replaced.
4. **Shaft runout verification** — Dial gauge at seal bore: 0.03 mm TIR (within ≤ 0.05 mm specification).
5. **Post-repair test run** — 30-minute run at 200 bar; `VIB.CAS.RMS` confirmed 0.9 mm/s, `TEMP.BRG` 60 °C; no visible leak. Pump returned to service.

---

## 7. Parts Consumed

| Part ID | Description | Qty | Unit Cost (USD) | Total (USD) |
|---|---|---|---|---|
| SEAL-MECH-DSC | Mechanical seal cartridge SiC/SiC | 1 | 1,500 | 1,500 |
| SLV-SHAFT-01 | Shaft sleeve | 1 | 700 | 700 |

**Parts total: USD 2,200**
Remainder of USD 14,400 event cost: labour, strainer replacement, production risk during 8-hour unplanned period.

---

## 8. Downtime

| Type | Hours |
|---|---|
| Unplanned (leak escalation before standby switch) | 8 |
| Planned (back-pullout seal change) | 3 |
| **Total** | **11** |

---

## 9. Recurrence Prevention

1. **Planned seal replacement interval.** Based on 22-month service life to wear, reduce planned seal replacement interval to 18 months for this service (200 bar, scale-laden water). Schedule with next annual pump overhaul window.
2. **Continuous AE monitoring review.** AE at the seal cavity should trigger investigation at 6 dB (not wait for 8 dB warning). Combine AE > 4 dB + operator patrol confirmation of drip = immediate standby switchover within 4 hours.
3. **Suction strainer finer mesh.** Evaluate 100 µm strainer element (from current 200 µm) on suction side to reduce abrasive loading on seal flush circuit. Must verify NPSH margin is maintained at reduced suction flow restriction.
4. **EPDM O-ring upgrade.** Replace NBR O-ring with EPDM (ethylene propylene diene monomer) which has superior temperature and chemical resistance to water-treatment additives; expected service life extension from 22 months to > 36 months based on material selection data.
5. **Vibration trend alert on rate-of-change.** Set SCADA alert on `VIB.CAS.RMS` rate of change > 0.5 mm/s per week as an early-warning trigger, irrespective of absolute threshold.

---

*Standards cited: ISO 10816-7:2009 (pump vibration), HI 9.6.1-2017 (NPSH), ASTM E2374-14 (acoustic emission). Equipment: KSB Multitec HP [synthetic reference].*
