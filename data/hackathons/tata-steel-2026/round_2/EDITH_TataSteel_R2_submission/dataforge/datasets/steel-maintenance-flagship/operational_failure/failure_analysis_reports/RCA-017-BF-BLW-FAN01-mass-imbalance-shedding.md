# FAILURE ANALYSIS REPORT

**Report Number:** RCA-017
**Date of Report:** 2025-08-22
**Classification:** SYNTHETIC — physics-grounded, no proprietary Tata Steel data
**Prepared by:** Reliability Engineering, TATA_JSR Blast Furnace / Blower House
**Safety Class:** P2

---

## 1. Asset Identification

| Field | Value |
|---|---|
| Asset ID | BF.BLW.FAN01 |
| Equipment Class | bf_sinter_fan_blower |
| Description | Blast furnace turbo-blower / cold-blast machine |
| Location | BLAST_FURNACE / BLOWER_HOUSE / TURBO_BLOWER_1 |

---

## 2. Failure Summary

| Field | Value |
|---|---|
| Failure Mode | mass_imbalance_deposit_shedding |
| Fault Codes | VIB-1X-WARN, IMBALANCE-STEPCHANGE |
| Date of Incident | 2025-08-22 |
| Unplanned Downtime | 8 hours |
| Total Cost Impact | INR 25,000,000 (~USD 300,000) |

---

## 3. Symptom Timeline

### Background
The cold-blast machine operates on filtered ambient air. Despite inlet filtration, fine particles (silica dust, coal fines from the adjacent ore yard during high-wind conditions) penetrate the inlet filter and deposit on the axial blower impeller blades. Over a 10-month operating period since the October 2023 overhaul, approximately 12 kg of deposits had accumulated unevenly across the rotor.

### T−3 weeks: Gradual Vibration Rise
- `JSR.BF.BLW.FAN01.VIB.1X`: drifts from 1.8 mm/s to 3.2 mm/s over 3 weeks (approaching warning 4.5 mm/s). This gradual 1× rise is the classic signature of mass accumulation (imbalance buildup) — the slope is approximately 0.5 mm/s per week, consistent with the known deposit rate in high-dust conditions.
- `JSR.BF.BLW.FAN01.SHAFT.DISP`: rises from 35 µm to 55 µm (within normal 10–50 µm range; approaching warning).
- No temperature anomaly; surge margin adequate.

### T=0: Step-Change — Deposit Shedding
At 14:32 during a brief process transient (momentary 5% surge margin approach during a demand change), a section of accumulated deposit on blades 3 and 7 detached simultaneously. The rotor went from a gradual buildup imbalance to an asymmetric shedding imbalance in < 1 second.
- `JSR.BF.BLW.FAN01.VIB.1X` jumps from 3.2 to 5.9 mm/s (crossing warning 4.5 mm/s, approaching alarm 7.1 mm/s). The step-change character distinguishes shedding imbalance from crack propagation.
- `JSR.BF.BLW.FAN01.SHAFT.DISP` rises to 82 µm (crossing warning 80 µm, per API 670:2014).
- Fault codes VIB-1X-WARN and IMBALANCE-STEPCHANGE generated.
- Operators reduce blast volume by 8% to reduce aerodynamic loading on the impeller; vibration stabilises at 5.3 mm/s.
- Controlled shutdown initiated.

---

## 4. Sensor Evidence Summary

| Tag | Normal Value | Defect Value | Threshold |
|---|---|---|---|
| JSR.BF.BLW.FAN01.VIB.1X | 1.8 mm/s | 5.9 mm/s | Warning (4.5 mm/s) |
| JSR.BF.BLW.FAN01.SHAFT.DISP | 35 µm | 82 µm | Warning (80 µm) |
| JSR.BF.BLW.FAN01.TEMP.BRG | 60 °C | 68 °C | Normal |
| JSR.BF.BLW.FAN01.PRES.OSC | 1.0% | 2.1% | Normal |
| JSR.BF.BLW.FAN01.THRUST.TEMP | 68 °C | 72 °C | Normal |

---

## 5. Root Cause Analysis

**Mass imbalance from blade deposit accumulation and asymmetric shedding.** The inlet filter change interval (6-monthly) had extended to 9 months due to a filter procurement delay, allowing higher dust penetration into the blower. The asymmetric shedding triggered by the process transient is dangerous precisely because the rotor mass distribution changes instantaneously, potentially exceeding the API 670 trip threshold before the control system can respond.

No blade erosion damage was found on post-inspection borescope — the deposit was on blade leading-edge surfaces, not eroding the substrate. However, the sustained 3-week gradual vibration rise was an actionable signal that was not acted upon.

---

## 6. Corrective Actions Taken

1. Controlled shutdown; borescope inspection through IGV access ports.
2. Deposits found on blades 1, 3, 5, 7, 11, 14 (out of 16 blades). Weight distribution map created.
3. In-situ balancing: `BAL-WT-01` balance weights fitted at calculated angular positions on the rotor balance planes (front and rear). Residual imbalance confirmed < G 1.0 (ISO 1940) at operating speed via coast-down analysis.
4. Inlet filter changed: new elements (store) installed. `JSR.BF.BLW.FAN01.VIB.1X` confirmed 1.7 mm/s post-restart.

---

## 7. Parts Consumed

| Part ID | Description | Qty | Cost (USD) |
|---|---|---|---|
| BAL-WT-01 | Balancing weights set | 1 set | 50 |

Remainder of USD 300,000: 8-hour BF reduced-blast event cost.

---

## 8. Recurrence Prevention

1. **Vibration 1× rate-of-change alert.** If `VIB.1X` rate of increase > 0.3 mm/s per week for 2 consecutive weeks → schedule inlet inspection and cleaning within 72 hours (do not wait for warning threshold).
2. **Inlet filter change interval: 6 months maximum** with no deferral. Procurement lead time for filter elements is ≤ 2 weeks; no excuse for a 3-month overrun.
3. **Quarterly in-situ rotor deposit inspection** via borescope when operating in high-dust conditions (coal unloading campaigns in adjacent yard).

---

*Asset: BF.BLW.FAN01. Failure mode: mass_imbalance_deposit_shedding. Standards: ISO 1940 (balancing quality), API 670:2014 (shaft displacement protection).*
