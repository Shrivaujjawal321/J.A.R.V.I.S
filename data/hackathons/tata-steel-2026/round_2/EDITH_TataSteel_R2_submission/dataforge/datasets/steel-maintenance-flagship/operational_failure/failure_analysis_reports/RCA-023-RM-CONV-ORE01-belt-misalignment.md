# FAILURE ANALYSIS REPORT

**Report Number:** RCA-023
**Date of Report:** 2026-01-08
**Classification:** SYNTHETIC — physics-grounded, no proprietary Tata Steel data
**Prepared by:** Reliability Engineering, TATA_JSR Raw Material Handling
**Safety Class:** P2

---

## 1. Asset Identification

| Field | Value |
|---|---|
| Asset ID | RM.CONV.ORE01 |
| Equipment Class | raw_material_conveyor |
| Description | Raw material yard ore conveyor (1,600 mm belt EP630) |
| Location | RAW_MATERIAL / ORE_YARD / CONV_ORE_1 |

---

## 2. Failure Summary

| Field | Value |
|---|---|
| Failure Mode | belt_misalignment |
| Fault Codes | BELT-EDGE-WARN, MTR-CURR-HIGH |
| Date of Incident | 2026-01-08 |
| Duration from warning to belt stop | 8 minutes |
| Downtime (belt realignment + idler adjustment) | 3 hours |
| Total Cost Impact | INR 500,000 (~USD 6,000) |

---

## 3. Symptom Timeline

### Context
After monsoon season maintenance, belt return idlers on the return strand at positions R-80 to R-95 were replaced with standard flat return idlers. The replacement crew used idlers from a different batch that had a marginally different roller coating thickness (0.5 mm difference), creating a slight asymmetry in belt contact friction distribution over a 15 m section.

### T−2 shifts: Gradual Drift
- `JSR.RM.CONV1.BELT.EDGE`: drifts from +5 mm to +18 mm over 16 hours (normal ±15 mm; approaching warning ±25 mm). The drift is slow, suggesting a systematic misalignment source rather than a sudden event.
- Drive motor current `JSR.RM.CONV1.MTR.CURR`: rises from 78% to 88% FLA as the belt runs off-centre and rubs against the idler frames.

### T=0: Warning Alarm
- `JSR.RM.CONV1.BELT.EDGE`: 27 mm (crossing warning threshold ±25 mm). BELT-EDGE-WARN generated.
- `JSR.RM.CONV1.MTR.CURR`: 106% FLA (crossing warning threshold 105% FLA due to increased drag). MTR-CURR-HIGH generated.
- Belt visible to be tracking 25–30 mm to the operator-side of the conveyor. No belt edge damage yet (belt edge-to-frame gap approximately 60 mm with this level of misalignment; belt would contact frame at approximately 50 mm deviation = alarm level).
- Belt stopped immediately.

---

## 4. Sensor Evidence Summary

| Tag | Normal Value | Defect Value | Threshold |
|---|---|---|---|
| JSR.RM.CONV1.BELT.EDGE | +5 mm | +27 mm | Warning (25 mm) |
| JSR.RM.CONV1.MTR.CURR | 78% FLA | 106% FLA | Warning (105% FLA) |
| JSR.RM.CONV1.IDLER.TEMP | 42 °C | 48 °C | Normal |
| JSR.RM.CONV1.IDLER.US | −14 dBµV | −9 dBµV | Normal |
| JSR.RM.CONV1.RIP.LOOP | 72 mA | 72 mA | Normal |

---

## 5. Root Cause Analysis

**Belt tracking deviation from asymmetric idler replacement.** Return idlers in a 15 m zone had marginally different coating friction, causing a persistent lateral force on the belt. For a 1,600 mm wide belt at 2.5 m/s, even a 5 N/m lateral force differential can cause a sustained drift of 10–15 mm per 100 m of conveyor travel. Over 16 hours of operation, the belt drifted cumulatively.

The misalignment was exacerbated by a worn training (self-aligning) idler at position R-88 that had lost its pivoting action and was locked in a 3° tilt — contributing a fixed lateral thrust.

---

## 6. Corrective Actions Taken

1. Belt stopped; LOTO on 800 kW drive.
2. Return-strand idler inspection (R-80 to R-95): idler batch inconsistency confirmed. All 15 idlers replaced with a single-batch matched set.
3. Training idler at R-88 replaced with `IDLER-TRAIN-01` (self-aligning, stock qty 6).
4. Belt tensioner slack adjusted to restore crown-over-centre tracking baseline.
5. Belt restarted: tracking confirmed ±5 mm over 30-minute run-in.

---

## 7. Parts Consumed

| Part ID | Description | Qty | Cost (USD) |
|---|---|---|---|
| IDLER-STD-1600 | Standard carrying idler 1,600 mm | 15 | 1,350 |
| IDLER-TRAIN-01 | Training/self-aligning idler | 1 | 320 |

**Parts total: USD 1,670.** Remainder of USD 6,000: 3-hour downtime.

---

## 8. Recurrence Prevention

1. **Batch consistency protocol for idler replacement.** All idlers replaced in a single section must be from the same production batch; verify coating diameter uniformity before installation.
2. **Training idler inspection.** Training idlers at ≥ every 20 idler positions; check pivoting action quarterly — seized training idlers cannot function as tracking correctors.
3. **Belt-edge trend alert.** Belt edge drift > 5 mm in 4 hours = investigate; don't wait for threshold.

---

*Asset: RM.CONV.ORE01. Failure mode: belt_misalignment. Standards: CEMA Section 6 [unverified], Fenner Dunlop belt tracking guidelines.*
