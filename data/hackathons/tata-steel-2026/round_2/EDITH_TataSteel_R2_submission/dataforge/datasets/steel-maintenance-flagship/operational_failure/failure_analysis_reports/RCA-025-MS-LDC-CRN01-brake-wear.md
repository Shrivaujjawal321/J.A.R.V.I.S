# FAILURE ANALYSIS REPORT

**Report Number:** RCA-025
**Date of Report:** 2026-04-30
**Classification:** SYNTHETIC — physics-grounded, no proprietary Tata Steel data
**Prepared by:** Reliability Engineering, TATA_JSR Melt Shop — Crane Maintenance
**Safety Class:** P1 — SAFETY CRITICAL

---

## 1. Asset Identification

| Field | Value |
|---|---|
| Asset ID | MS.LDC.CRN01 |
| Equipment Class | ladle_crane |
| Description | Melt shop ladle crane hoist (molten-metal handling, safety-critical) |
| Location | MELT_SHOP / LADLE_BAY / CRANE_1_HOIST |
| Manufacturer | Konecranes |

---

## 2. Failure Summary

| Field | Value |
|---|---|
| Failure Mode | brake_wear_slip |
| Fault Codes | BRAKE-TEMP-WARN, BRAKE-SLIP-DETECT |
| Date of Incident | 2026-04-30 |
| Load suspended at time of detection | Yes — 185 t ladle being lowered |
| No uncontrolled descent | Correct — dual-circuit brake held |
| Planned Downtime | 4 hours (brake pad replacement) |
| Unplanned Downtime | 0 |
| Total Cost Impact | INR 1,200,000 (~USD 14,400) |

---

## 3. Symptom Timeline

### Context
Ladle crane performing a ladle lowering operation (185 t ladle, empty after tapping). Crane hoist motor driving against gravity with the regenerative braking system.

### T−10 min: Elevated Brake Drum Temperature
During a hold operation (holding the ladle stationary at pour height for 8 minutes while the tundish was prepared), the hoist brake was fully applied in static holding mode.
- `JSR.MS.CRN01.BRAKE.TEMP`: rises from 72 °C to 112 °C (crossing warning threshold 110 °C). Elevated temperature during a prolonged static hold indicates the brake pad material is at the limit of its design holding load.
- Crane operator noted a slight "spongy" feeling in the brake pedal response — reported to crane maintenance.

### T=0: BRAKE-TEMP-WARN + BRAKE-SLIP-DETECT
During subsequent lowering operation:
- `JSR.MS.CRN01.BRAKE.TEMP` reaches 118 °C (alarm 120 °C).
- Brake-slip detector (encoder comparison: hoist motor speed vs. load block speed, sensing any mismatch > 0.5%) generates BRAKE-SLIP-DETECT — the worn brake pad surface is providing less than design braking torque.
- Emergency procedure: Crane operator immediately applies the secondary (backup) electromagnetic brake; lowering halted; ladle held at static position.
- Crane taken out of service for brake inspection.

---

## 4. Sensor Evidence Summary

| Tag | Normal Value | Defect Value | Threshold |
|---|---|---|---|
| JSR.MS.CRN01.BRAKE.TEMP | 70–74 °C | 118 °C | Alarm (120 °C) |
| JSR.MS.CRN01.LOAD.SWL | 58% | 58% | Normal |
| JSR.MS.CRN01.GBX.VIB.GMF | 0.3 g | 0.35 g | Normal |
| JSR.MS.CRN01.ROPE.MFL | 60 mV | 62 mV | Normal |

---

## 5. Root Cause Analysis

**Brake pad wear exceeding design thickness.** The Konecranes dual-circuit hoist brake uses electro-hydraulic disc brakes with sintered metal pads on a steel drum. Post-inspection: primary brake pad thickness measured at 4.2 mm (new 14 mm, minimum service limit 6 mm). The pad wear was 71% of the pad's life consumed, exceeding the service limit by 1.8 mm. This represents an oversight in the brake inspection program — pads were last measured at the July 2024 overhaul (9 months prior) and recorded as 8.1 mm (within limit); no intermediate brake measurement was scheduled.

Contributing factor: the production period October 2025–April 2026 had 18% higher ladle cycling rate than the baseline used to set the pad inspection interval (12 months), consuming brake wear faster than anticipated.

---

## 6. Corrective Actions Taken

1. Ladle lowered under secondary electromagnetic brake control; ladle set down safely.
2. Crane out of service; CRN02 assigned to melt shop.
3. `BRAKE-PAD-01` (brake pads, stock qty 4) installed on both primary brake circuits.
4. Brake thruster `BRAKE-THR-01` inspected — function confirmed, no replacement needed.
5. Brake test: static hold at 125% SWL (test block) for 10 minutes; drum temperature 76 °C (normal). Slip detector confirmed zero slip.
6. Crane returned to service with updated pad-wear record.

---

## 7. Parts Consumed

| Part ID | Description | Qty | Cost (USD) |
|---|---|---|---|
| BRAKE-PAD-01 | Crane brake pads (shoe/disc) | 4 | 1,800 |

**Parts total: USD 1,800.** Remainder: 4-hour downtime, CRN02 changeover.

---

## 8. Recurrence Prevention

1. **Brake pad thickness measurement: 6-monthly** (reduce from 12-monthly). Discard at ≤ 6 mm. With the current production rate, actual pad life is approximately 14 months, not the 18 months assumed.
2. **Brake temperature trend.** Brake drum temperature during a 5-minute static hold should remain below 90 °C; any hold temperature > 95 °C = brake inspection within 24 hours.
3. **Brake-slip detector commissioning.** The slip detector performed correctly and was the direct safety save in this event. Confirm quarterly calibration check (encoder drift can cause false alarms or missed detections).

---

*Asset: MS.LDC.CRN01. Failure mode: brake_wear_slip. This event demonstrates the safety-critical nature of ladle-crane brake maintenance. No uncontrolled descent occurred — dual-circuit brake design performed as intended.*
