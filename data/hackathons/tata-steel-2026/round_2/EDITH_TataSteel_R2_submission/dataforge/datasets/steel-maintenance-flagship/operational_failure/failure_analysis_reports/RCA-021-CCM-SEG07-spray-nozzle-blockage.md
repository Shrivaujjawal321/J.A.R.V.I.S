# FAILURE ANALYSIS REPORT

**Report Number:** RCA-021
**Date of Report:** 2026-02-14
**Classification:** SYNTHETIC — physics-grounded, no proprietary Tata Steel data
**Prepared by:** Reliability Engineering, TATA_JSR Continuous Casting
**Safety Class:** P2

---

## 1. Asset Identification

| Field | Value |
|---|---|
| Asset ID | CCM.SEG.07 |
| Equipment Class | continuous_caster_segment |
| Description | Continuous caster strand-guide segment 7 (withdrawal/bending zone) |
| Location | CASTER_1 / STRAND_GUIDE / SEGMENT_07 |

---

## 2. Failure Summary

| Field | Value |
|---|---|
| Failure Mode | spray_nozzle_blockage |
| Fault Codes | SPRAY-FLOW-LOW, BULGE-WARN |
| Date of Incident | 2026-02-14 |
| Duration from warning to action | 18 minutes |
| Planned Downtime | 2 hours (nozzle cleaning at heat end) |
| Unplanned Downtime | 0 |
| Cost Impact | INR 350,000 (~USD 4,200) |

---

## 3. Symptom Timeline

### Normal Operation (Previous Heat)
Secondary cooling zone 7 running at design parameters. `JSR.CC1.SEG07.SPRAY.FLOW`: 200 L/min; `JSR.CC1.SEG07.BULGE`: 0.5 mm.

### T−18 min: Spray Flow Drop
- `JSR.CC1.SEG07.SPRAY.FLOW`: drops from 200 to 148 L/min over 15 minutes (crossing warning threshold 150 L/min). The flow drop is gradual — consistent with progressive nozzle blockage (scale deposit accumulation in the nozzle orifice) rather than sudden valve failure (which would be a step change).
- `JSR.CC1.SEG07.BULGE`: rises from 0.5 to 1.8 mm (approaching warning 2.0 mm). The reduced cooling allows the strand surface shell to soften slightly, increasing the metallostatic pressure-driven bulging between roll pairs.

### T=0: Warning Alarm
- `JSR.CC1.SEG07.SPRAY.FLOW`: 144 L/min (below warning 150 L/min). SPRAY-FLOW-LOW.
- `JSR.CC1.SEG07.BULGE`: 2.1 mm (above warning 2.0 mm). BULGE-WARN.
- Casting speed reduced by 15% to restore effective cooling per tonne (same heat removal at lower throughput).
- Heat ended at natural sequence completion; no emergency stop required.

---

## 4. Sensor Evidence Summary

| Tag | Normal Value | Defect Value | Threshold |
|---|---|---|---|
| JSR.CC1.SEG07.SPRAY.FLOW | 200 L/min | 144 L/min | Warning (150 L/min) |
| JSR.CC1.SEG07.BULGE | 0.5 mm | 2.1 mm | Warning (2.0 mm) |
| JSR.CC1.SEG07.ROLL.RPM | 14 rpm | 14 rpm | Normal |
| JSR.CC1.SEG07.FORCE.HYD | 300 kN | 315 kN | Normal |

---

## 5. Root Cause Analysis

**Spray nozzle blockage from scale and calcium carbonate deposits** — same water quality issue as identified in RCA-006 (roll seizure), but caught at an earlier, lower-consequence stage. Three of 8 nozzles in Segment 7 had partial blockage reducing total zone flow rate by approximately 28%. Calcium carbonate deposits were the primary blockage material (water hardness had recovered to 280 mg/L CaCO₃ — still above the 200 mg/L target — following the water softener commissioning after the RCA-006 event).

---

## 6. Corrective Actions Taken

1. Casting speed reduced at T=0; heat completed normally.
2. Segment 7 nozzle inspection at heat end (strand retracted): all 8 nozzles removed; 3 blocked nozzles ultrasonically cleaned; 1 replaced (`NOZ-SPRAY-01`, stock qty 50).
3. Water softener output verified: 190 mg/L CaCO₃ (within target ≤ 200 mg/L).
4. Spray flow confirmed 200 L/min at full zone pressure before next heat.

---

## 7. Parts Consumed

| Part ID | Description | Qty | Cost (USD) |
|---|---|---|---|
| NOZ-SPRAY-01 | Spray nozzle (consumable) | 1 | 35 |

**Parts total: USD 35.** Remainder of USD 4,200: minor throughput loss from speed reduction during affected heat.

---

## 8. Recurrence Prevention

1. **Nozzle flow test on every segment withdrawal.** Add a 10-minute nozzle flow test (all nozzles at design pressure; reject any < 90% rated flow) as standard practice during each segment withdrawal for refurbishment.
2. **Water hardness continuous monitoring.** Add inline conductivity sensor on secondary cooling supply; alert at hardness proxy > conductivity 450 µS/cm (approximate threshold for target water quality).

---

*Asset: CCM.SEG.07. Failure mode: spray_nozzle_blockage. A less severe recurrence of the same water-quality root cause as RCA-006.*
