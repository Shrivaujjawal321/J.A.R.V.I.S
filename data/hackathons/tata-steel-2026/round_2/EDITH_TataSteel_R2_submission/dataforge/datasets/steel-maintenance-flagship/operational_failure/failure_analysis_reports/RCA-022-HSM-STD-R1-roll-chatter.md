# FAILURE ANALYSIS REPORT

**Report Number:** RCA-022
**Date of Report:** 2025-10-20
**Classification:** SYNTHETIC — physics-grounded, no proprietary Tata Steel data
**Prepared by:** Reliability Engineering, TATA_JSR Hot Rolling Division
**Safety Class:** P3

---

## 1. Asset Identification

| Field | Value |
|---|---|
| Asset ID | HSM.STD.R1 |
| Equipment Class | hot_strip_mill_stand |
| Description | Hot Strip Mill roughing stand R1 (4-high reversing stand) |
| Location | HOT_ROLLING / ROUGHING_STAND_1 / MILL_STAND |

---

## 2. Failure Summary

| Field | Value |
|---|---|
| Failure Mode | roll_chatter_5th_octave |
| Fault Codes | CHATTER-VIB-WARN, CROWN-DEV-WARN |
| Date of Incident | 2025-10-20 |
| Duration of chatter episode | 4 minutes (self-damped by speed change) |
| Unplanned Downtime | 0 (rolling continued at modified parameters) |
| Planned Downtime | 2 hours (chock clearance adjustment + roll change) |
| Total Cost Impact | INR 600,000 (~USD 7,200) |

---

## 3. Symptom Timeline

### Context
R1 was rolling 35 mm → 20 mm reduction pass at 4.2 m/s strip speed. The slab temperature was slightly below target (1,120 °C vs. target 1,150 °C) due to a brief reheating furnace temperature dip earlier in the shift.

### T=0: Chatter Onset
- `JSR.HR.R1.WR.VIB.CHOCK`: rises abruptly from 0.5 mm/s to 4.8 mm/s (crossing warning 4.0 mm/s). The chatter frequency is approximately 140 Hz, falling in the "5th octave" range (120–170 Hz for roughing stands), where the stand structural resonance and the rolling-process feedback loop can couple.
- `JSR.HR.R1.FORCE`: rolling force ripple rises from 1.2% to 3.8% (approaching warning 4%).
- `JSR.HR.R1.CROWN.DEV`: strip crown deviation rises from 6 µm to 28 µm (crossing warning 25 µm). The oscillating chock creates a periodic rolling gap variation that directly maps to strip crown periodicity.

### T+2 min: Operator Response — Speed Change
Operator increases rolling speed from 4.2 to 5.1 m/s (above the chatter resonance lock-in speed range for this reduction). Chatter self-damps within 30 seconds.
- `JSR.HR.R1.WR.VIB.CHOCK` returns to 0.9 mm/s.
- `JSR.HR.R1.CROWN.DEV` returns to 9 µm.

### T+4 min: Stable Operation
Rolling continued; no roll change required during the pass. However, 3 coils during the chatter episode had strip crown deviation > 25 µm — placed on hold for downstream thickness check.

---

## 4. Sensor Evidence Summary

| Tag | Normal Value | Defect Value | Threshold |
|---|---|---|---|
| JSR.HR.R1.WR.VIB.CHOCK | 0.5 mm/s | 4.8 mm/s | Warning (4.0 mm/s) |
| JSR.HR.R1.FORCE | 1.2% | 3.8% | Near warning (4%) |
| JSR.HR.R1.CROWN.DEV | 6 µm | 28 µm | Warning (25 µm) |
| JSR.HR.R1.WR.AE.RMS | 0 dB | 4 dB | Normal |

---

## 5. Root Cause Analysis

**Roll chatter (5th-octave) from below-optimal slab entry temperature creating elevated deformation resistance.** Chatter in rolling mills occurs when a regenerative self-excited vibration loop develops between the roll-gap dynamics (varying rolling force due to strip thickness variation) and the stand structural dynamics (roll-chock natural frequency in the 100–200 Hz range). Lower slab temperature increases the material flow stress significantly (approximately 8–12% per 30 °C below target for C-Mn steel in the austenite range), raising the rolling force and shifting the roll-gap dynamic stiffness into a range that can excite the stand's natural frequency.

The chatter was self-limiting (damped by speed change) and did not cause roll spall or bearing damage. The chock vibration and crown deviation alarm are reliable early indicators that the process has entered a chatter regime.

---

## 6. Corrective Actions Taken

1. Speed increase terminated chatter episode.
2. Planned roll change at shift end: work rolls changed (already at day 7 of 10-day campaign; brought forward to day 7 given the chatter episode). New rolls have higher crown profile (10 µm more positive crown) to compensate for thermal camber loss late in campaign.
3. Chock clearances checked: work-roll chock liner clearance measured at 0.35 mm (specification ≤ 0.30 mm on worn limit). Liners adjusted (shimmed) to 0.22 mm to reduce the dynamic play that amplifies chatter amplitude once initiated.
4. Strip on hold: 3 coils inspected; crown deviation < 30 µm in all cases; cleared for downstream processing.

---

## 7. Parts Consumed

Roll change: `WR-HSS-PREP` pair (already scheduled). `CHOCK-SEAL-01` seals. Routine campaign change-out.

---

## 8. Recurrence Prevention

1. **Slab entry temperature minimum of 1,130 °C** for R1 reductions > 40%. Alert the rolling supervisor when furnace discharge temperature is below this threshold; reduce the reduction ratio on the first pass until temperature is confirmed.
2. **Chock clearance PM interval: 6-monthly.** Clearance degrades through wear; 6-monthly measurement and correction within 0.25 mm.
3. **Automated chatter detection.** Implement 5th-octave chatter detection (bandpass filter 100–200 Hz on chock accelerometer; alert if amplitude > 1.5 mm/s in this band) as a PdM feature rather than relying solely on the broadband `VIB.CHOCK` reading.

---

*Asset: HSM.STD.R1. Failure mode: roll_chatter_5th_octave. Rolling mill chatter mechanics per ABB CMC reference [unverified].*
