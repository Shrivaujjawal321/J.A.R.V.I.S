# FAILURE ANALYSIS REPORT

**Report Number:** RCA-016
**Date of Report:** 2025-09-15
**Classification:** SYNTHETIC — physics-grounded, no proprietary Tata Steel data
**Prepared by:** Reliability Engineering, TATA_JSR Hot Rolling Division
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

---

## 2. Failure Summary

| Field | Value |
|---|---|
| Failure Mode | cavitation |
| Fault Codes | PUMP-NPSH-WARN, AE-CAVITATION |
| Date of Incident | 2025-09-15 |
| Duration of cavitation event | 22 minutes |
| Planned Downtime (impeller inspection) | 4 hours |
| Unplanned Downtime | 0 (pump remained operational; impeller inspected at next window) |
| Total Cost Impact | INR 800,000 (~USD 9,600) |

---

## 3. Symptom Timeline

### Context
August–September: Monsoon season. Raw water supply temperature to the descaling circuit drops from 32 °C to 24 °C; dissolved oxygen in the water increases. Separately, a partial blockage in the suction strainer (confirmed post-incident) reduced the suction-side flow area.

### T−30 min: Suction Pressure Drop
- `JSR.HR.DSC.PMP01.PRES.SUC`: falls from 185 kPa to 82 kPa (below the warning threshold of 90 kPa). The suction pressure is now below the minimum required for adequate NPSH (net positive suction head) — per HI 9.6.1-2017, the pump requires a minimum suction pressure to prevent vapour bubble formation at the impeller eye.
- `JSR.HR.DSC.PMP01.PRES.DIS`: drops slightly from 200 to 192 bar (lower end of normal), reflecting reduced pump efficiency as NPSH margin is consumed.

### T−10 min: Cavitation Onset
- `JSR.HR.DSC.PMP01.AE.RMS`: rises to 10 dB (warning threshold 8 dB). The acoustic emission signature at 100–500 kHz (ASTM E2374-14 cavitation band) is the definitive early indicator of vapour bubble collapse on the impeller vane pressure face.
- `JSR.HR.DSC.PMP01.VIB.CAS.RMS`: rises from 1.0 to 2.8 mm/s (crossing warning 2.5 mm/s) due to the broadband shock loading from bubble implosion events.
- `JSR.HR.DSC.PMP01.FLOW.DIS`: drops to 374 m³/hr (warning threshold 372 m³/hr) — flow loss from vapour void formation at impeller eye.

### T=0: Decision to Switch to Standby
- `JSR.HR.DSC.PMP01.PRES.SUC`: reaches 68 kPa (below alarm threshold 70 kPa) — severe NPSH deficit.
- `JSR.HR.DSC.PMP01.AE.RMS`: 14 dB (approaching alarm 15 dB).
- After 22 minutes total cavitation exposure, standby pump switched in; PMP01 isolated.

---

## 4. Sensor Evidence Summary

| Tag | Normal Value | Defect Value | Threshold |
|---|---|---|---|
| JSR.HR.DSC.PMP01.PRES.SUC | 185 kPa | 68 kPa | Alarm (70 kPa) |
| JSR.HR.DSC.PMP01.AE.RMS | 0 dB | 14 dB | Warning (8 dB) |
| JSR.HR.DSC.PMP01.VIB.CAS.RMS | 1.0 mm/s | 2.8 mm/s | Warning (2.5 mm/s) |
| JSR.HR.DSC.PMP01.FLOW.DIS | 400 m³/hr | 374 m³/hr | Warning (372 m³/hr) |
| JSR.HR.DSC.PMP01.PRES.DIS | 200 bar | 192 bar | Normal |

---

## 5. Root Cause Analysis

**Cavitation from NPSH deficit caused by suction strainer partial blockage.** The suction strainer had accumulated a 40% area restriction from scale and biofilm (seasonal increase in organic growth at lower water temperatures). This raised the suction-line pressure drop, reducing the pressure available at the impeller eye below the vapour pressure of the water at pumping conditions.

The 22-minute cavitation exposure caused visible pitting on the impeller vane concave face (pressure face), measured at up to 0.4 mm pit depth on post-inspection. At 200 bar service, even minor surface roughness on the impeller vanes reduces hydraulic efficiency and can initiate fatigue cracks from the pit stress concentrators.

---

## 6. Corrective Actions Taken

1. Standby pump PMP02 online; PMP01 isolated.
2. Suction strainer cleaned; scale and biofilm removed (4-hour inspection window).
3. Impeller inspected: 6 pitting sites on vanes, 0.2–0.4 mm depth. Within serviceable limits (reject at > 1.0 mm depth per KSB guideline). Noted for enhanced monitoring.
4. Suction pressure confirmed 185 kPa after strainer cleaning; AE RMS confirmed 0 dB on restart.
5. Biocide dosing increased in the descaling water supply for the monsoon season.

---

## 7. Parts Consumed

None consumed this event. Cost represents 4-hour planned window plus impeller wear acceleration risk.

---

## 8. Recurrence Prevention

1. **Strainer cleaning frequency: monthly during monsoon season** (July–September). Currently quarterly.
2. **Suction pressure low-low alarm at 90 kPa** should also trigger an automatic alert to check the strainer differential pressure. Link NPSH alert to a strainer DP sensor (not currently installed; add DP gauge across strainer).
3. **AE cavitation monitoring.** The AE sensor at the pump casing correctly identified cavitation onset at 10 dB before the suction pressure dropped to alarm level. Confirm the AE cavitation band (100–500 kHz) is configured in the SCADA AE processing. Establish an AE > 6 dB = "investigate suction side" protocol.

---

*Asset: HSM.DSC.PMP01. Failure mode: cavitation. Standards: HI 9.6.1-2017 (NPSH), ASTM E2374-14 (AE cavitation).*
