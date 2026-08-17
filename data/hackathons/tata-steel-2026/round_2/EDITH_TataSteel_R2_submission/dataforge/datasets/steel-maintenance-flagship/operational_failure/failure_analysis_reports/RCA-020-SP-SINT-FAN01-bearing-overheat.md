# FAILURE ANALYSIS REPORT

**Report Number:** RCA-020
**Date of Report:** 2026-03-02
**Classification:** SYNTHETIC — physics-grounded, no proprietary Tata Steel data
**Prepared by:** Reliability Engineering, TATA_JSR Sinter Plant
**Safety Class:** P2

---

## 1. Asset Identification

| Field | Value |
|---|---|
| Asset ID | SP.SINT.FAN01 |
| Equipment Class | bf_sinter_fan_blower |
| Description | Sinter plant main exhaust fan (high-criticality, dust-laden gas) |
| Location | SINTER_PLANT / MAIN_FAN / FAN_1 |
| Manufacturer | TLT-Turbo |
| Model | Radial process fan |
| Rated Power | 4,500 kW |
| Rated Speed | 990 rpm |

---

## 2. Failure Summary

| Field | Value |
|---|---|
| Failure Mode | bearing_overheating |
| Fault Codes | TEMP-BRG-WARN, VIB-1X-WARN |
| Date of Incident | 2026-03-02 |
| Duration from warning to planned stop | 36 hours |
| Planned Downtime | 8 hours (bearing replacement) |
| Unplanned Downtime | 0 |
| Total Cost Impact | INR 1,800,000 (~USD 21,600) |

---

## 3. Symptom Timeline

### T−2 Months: Gradual Bearing Temperature Trend
- `JSR.SP.FAN01.TEMP.BRG`: slow rise from 56 °C baseline to 68 °C over 8 weeks. Rise rate: approximately 1.5 °C/week — consistent with progressive grease degradation rather than sudden overload.
- `JSR.SP.FAN01.VIB.1X`: 2.0 mm/s (still within normal 1.0–2.3 mm/s).

### T−2 Weeks: Warning Level
- `JSR.SP.FAN01.TEMP.BRG`: 78 °C (approaching warning 80 °C).
- `JSR.SP.FAN01.VIB.1X`: 3.8 mm/s (approaching warning 4.5 mm/s). Vibration rise indicates bearing rolling-element damage beginning — consistent with lubrication-failure-induced surface fatigue after prolonged elevated temperature.
- Maintenance schedules a bearing replacement at the next planned sinter plant maintenance window (36 hours out).

### T=0: Bearing Change Window
- `JSR.SP.FAN01.TEMP.BRG`: 84 °C at planned stop (crossed warning 80 °C, not alarm 95 °C).
- `JSR.SP.FAN01.VIB.1X`: 4.6 mm/s (marginally above warning 4.5 mm/s; below alarm 7.1 mm/s).
- Controlled planned stop; bearing replaced before alarm-level escalation.

---

## 4. Sensor Evidence Summary

| Tag | Normal Value | Defect Value | Threshold |
|---|---|---|---|
| JSR.SP.FAN01.TEMP.BRG | 56 °C | 84 °C | Warning (80 °C) |
| JSR.SP.FAN01.VIB.1X | 1.9 mm/s | 4.6 mm/s | Warning (4.5 mm/s) |
| JSR.SP.FAN01.VIB.AXIAL | 0.2 | 0.25 | Normal |
| JSR.SP.FAN01.DP.DUCT | 11 kPa | 11.5 kPa | Normal |

---

## 5. Root Cause Analysis

**Bearing overheating from grease oxidation/hardening in a high-temperature, high-dust environment.** The sinter fan runs in a 60–80 °C ambient environment (hot gas recirculation zone). The bearing grease (lithium-complex, rated to 180 °C) had reached the end of its service life at approximately 18 months. At elevated base temperature, grease oxidation accelerates; the base oil bleeds out, leaving a thickened, non-lubricating residue that generates heat from rolling-element friction — the same positive-feedback loop seen in idler bearings (RCA-009), at longer time scales in larger equipment.

Contributing factor: the dusty sinter plant atmosphere accelerates seal wear on the fan bearing housing, allowing small quantities of sinter dust (iron oxide, CaO, silica) to ingress and contaminate the grease. Post-inspection, the grease was grey-brown with visible particle inclusions — confirming both oxidation and contamination.

---

## 6. Corrective Actions Taken

1. Planned fan stop at a scheduled maintenance window; sinter plant continued on bypass filter circuit.
2. Drive-end and non-drive-end bearings replaced (large-bore deep-groove bearings, 4500 kW fan equivalent of `BRG-LRG-300` class).
3. Housing seals (labyrinth + contact lip) replaced.
4. New grease charge: high-temperature lithium-complex grease with EP additive (NLGI 2), packed to 60% housing volume.
5. Post-restart: `TEMP.BRG` 57 °C, `VIB.1X` 2.1 mm/s at 30 minutes. Normal.

---

## 7. Parts Consumed

Large-bore bearing set + seals (equivalent to BRG-LRG-300 class): USD 14,000. Total parts USD 14,000; remainder of USD 21,600: 8-hour window labour and grease charge.

---

## 8. Recurrence Prevention

1. **Grease change interval: 14 months** (actual degradation life was 18 months, but the warning presented at 16 months; target change before warning).
2. **TEMP.BRG alert on rate-of-change > 1 °C/week for 3 consecutive weeks.** This trend alert would have triggered action at T−2 months when the rise rate was already 1.5 °C/week — well before warning threshold.

---

*Asset: SP.SINT.FAN01. Failure mode: bearing_overheating. Standards: ISO 15243:2017 Section 8, ISO 10816-3:2009 Group 3.*
