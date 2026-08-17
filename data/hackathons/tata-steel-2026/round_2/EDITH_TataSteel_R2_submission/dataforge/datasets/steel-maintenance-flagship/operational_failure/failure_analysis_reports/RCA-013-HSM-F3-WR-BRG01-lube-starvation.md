# FAILURE ANALYSIS REPORT

**Report Number:** RCA-013
**Date of Report:** 2025-11-18
**Classification:** SYNTHETIC — physics-grounded, no proprietary Tata Steel data
**Prepared by:** Reliability Engineering, TATA_JSR Hot Rolling Division
**Safety Class:** P2

---

## 1. Asset Identification

| Field | Value |
|---|---|
| Asset ID | HSM.F3.WR.BRG01 |
| Equipment Class | rolling_mill_work_roll_bearing |
| Description | Hot Strip Mill Finishing Stand F3 work-roll chock bearing (oil-film + 4-row cylindrical roller neck bearing) |
| Location | HOT_ROLLING / FINISHING_STAND_3 / WORK_ROLL_DE_CHOCK |
| Manufacturer | SKF |
| Model | Oil-film bearing + 4-row cylindrical roller neck brg |

---

## 2. Failure Summary

| Field | Value |
|---|---|
| Failure Mode | lubrication_starvation_overheat |
| Fault Codes | TEMP-TRIP-100C, OFB-TEMP-HIGH |
| Date of Incident | 2025-11-18 |
| Unplanned Downtime | 6 hours |
| Total Cost Impact | INR 3,500,000 (~USD 41,900) |

---

## 3. Symptom Timeline

### T−90 min: OFB Outlet Temperature Warning
During normal rolling, a lube nozzle (`LUBE-NOZ-01`) on the oil-film bearing (OFB) circuit partially blocked with scale debris from the cooling water header — a different failure mode from the fatigue-spall event (RCA-001). The reduced oil-film flow rate caused the OFB outlet temperature to climb.

- `JSR.HR.STD3.WR.BRG01.OFB.OUT.TEMP`: rises from 57 °C to 78 °C (crossing warning threshold 75 °C). This is the earliest indicator — the OFB outlet temperature responds faster than the outer-ring temperature sensor because it directly measures the departing oil film heat.
- `JSR.HR.STD3.WR.BRG01.TEMP.DE`: 62 °C (still normal, 40–70 °C range).
- `JSR.HR.STD3.WR.BRG01.VIB.DE.H.RMS`: 1.8 mm/s (normal — no vibration change yet; lubrication starvation presents as thermal before mechanical).

### T−30 min: Thermal Escalation — Bearing Outer Ring
- `JSR.HR.STD3.WR.BRG01.OFB.OUT.TEMP`: reaches 82 °C (above warning 75 °C; approaching alarm 85 °C).
- `JSR.HR.STD3.WR.BRG01.TEMP.DE`: rises from 62 °C to 88 °C (crossing warning 85 °C). Heat is now conducting into the bearing outer ring as the oil-film viscosity drops below the minimum hydrodynamic film requirement at the reduced flow rate.
- `JSR.HR.STD3.WR.BRG01.AE.RMS`: 7 dBµV (above warning 6 dBµV) — acoustic emission from increased metal-to-metal asperity contact under the thinning oil film.

### T=0: TRIP
- `JSR.HR.STD3.WR.BRG01.TEMP.DE`: 103 °C (exceeding trip threshold 100 °C). TEMP-TRIP-100C generated.
- `JSR.HR.STD3.WR.BRG01.OFB.OUT.TEMP`: 87 °C (above alarm 85 °C). OFB-TEMP-HIGH generated.
- Stand F3 tripped; rolling transferred to F4.

---

## 4. Sensor Evidence Summary

| Tag | Normal Value | Defect Value | Threshold |
|---|---|---|---|
| JSR.HR.STD3.WR.BRG01.OFB.OUT.TEMP | 57 °C | 87 °C | Alarm (85 °C) |
| JSR.HR.STD3.WR.BRG01.TEMP.DE | 58 °C | 103 °C | TRIP (100 °C) |
| JSR.HR.STD3.WR.BRG01.AE.RMS | 0 dBµV | 7 dBµV | Warning (6 dBµV) |
| JSR.HR.STD3.WR.BRG01.VIB.DE.H.RMS | 1.6 mm/s | 2.1 mm/s | Normal (< 2.3 mm/s) |

---

## 5. Root Cause Analysis

**Lubrication starvation from blocked lube nozzle.** Scale debris from the stand cooling-water header cross-contaminated the OFB lube oil supply through a deteriorated heat-exchanger tube (minor water-in-oil ingress). The debris partially blocked the `LUBE-NOZ-01` nozzle orifice (0.8 mm bore, reduced to effective 0.4 mm), cutting oil-film flow rate by approximately 50%. The oil-film bearing (hydrodynamic design) requires minimum flow for viscous film formation; below this, metal-to-metal contact begins at the peak-pressure zone of the journal, generating heat that escalates once the positive-feedback loop (higher temp → lower viscosity → thinner film → more heat) initiates.

Key distinction from fatigue-spall (RCA-001): no BPFO envelope content was seen; the AE was broadband rather than tonally at BPFO, confirming mixed-friction origin rather than discrete spall contact.

---

## 6. Corrective Actions Taken

1. Stand F3 LOTO; OFB system isolated.
2. Lube nozzle `LUBE-NOZ-01` removed, cleaned; replaced (stock qty 4).
3. OFB circuit flushed; heat exchanger inspected — tube bundle leak confirmed. Tube plugged (precautionary); full heat exchanger replacement scheduled for next planned outage.
4. Bearing inspected post-cooldown: no raceway damage detected on visual and dye-penetrant examination; outer-ring surface Ra confirmed 0.4 µm (within specification). Bearing returned to service.
5. System restarted with oil flow verified: OFB outlet temperature confirmed 58 °C at 15-minute mark.

---

## 7. Parts Consumed

| Part ID | Description | Qty | Cost (USD) |
|---|---|---|---|
| LUBE-NOZ-01 | Oil-film bearing lube nozzle | 2 | 240 |

**Parts total: USD 240.** Remainder of ~USD 41,900: 6-hour unplanned downtime, heat exchanger inspection.

---

## 8. Recurrence Prevention

1. **OFB outlet temp response protocol.** OFB outlet > 75 °C (warning) = verify lube nozzle flow within 10 minutes; if oil flow confirmed reduced, stand down within 30 minutes. This event had a 90-minute warning window — sufficient to prevent the trip.
2. **Annual heat-exchanger tube inspection.** Water-in-oil contamination is a known initiator of both nozzle blockage and oil degradation. Add 12-monthly eddy-current inspection of OFB heat-exchanger tube bundles.

---

*Asset: HSM.F3.WR.BRG01 (same asset as RCA-001; different failure mode — lubrication starvation). Standards: ISO 15243:2017 Section 7 (overheat), SKF OFB guide [unverified].*
