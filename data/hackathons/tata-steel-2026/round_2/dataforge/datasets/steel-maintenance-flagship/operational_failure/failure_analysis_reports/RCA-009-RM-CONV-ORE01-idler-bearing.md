# FAILURE ANALYSIS REPORT

**Report Number:** RCA-009
**Date of Report:** 2026-04-11
**Classification:** SYNTHETIC — physics-grounded, no proprietary Tata Steel data
**Prepared by:** Reliability Engineering, TATA_JSR Raw Material Handling
**Safety Class:** P1 — FIRE RISK

---

## 1. Asset Identification

| Field | Value |
|---|---|
| Asset ID | RM.CONV.ORE01 |
| Equipment Class | raw_material_conveyor |
| Description | Raw material yard ore conveyor (long-overland, drive + idlers) |
| Location | RAW_MATERIAL / ORE_YARD / CONV_ORE_1 |
| Manufacturer | TRF / Fenner Dunlop |
| Model | 1,600 mm belt EP630 |
| Rated Power | 800 kW drive |
| Criticality | 2 |
| Installation Date | 2018-12-05 |
| Last Overhaul | 2024-03-30 |

---

## 2. Failure Summary

| Field | Value |
|---|---|
| Scenario ID | SCN-045 |
| Failure Mode | idler_bearing_failure |
| Fault Codes | IDLER-US-ALARM, IDLER-TEMP-FIRE |
| Date of Incident | 2026-04-11 |
| Warning-to-Stop Interval | 12 minutes (between ultrasound alarm and belt stop) |
| No fire | Yes — stopped before ignition |
| Unplanned Downtime | 2 hours |
| Planned Downtime | 0.5 hours (idler swap) |
| Total Cost Impact | INR 625,000 (~USD 7,500) |

---

## 3. Symptom Timeline

### Normal Operation — Patrol Inspection History
The conveyor runs continuously at 2.5 m/s, carrying iron ore at approximately 2,200 t/hr. Idlers are inspected by ultrasound patrols twice per shift.

Previous week patrol readings at idler position C-47 (return strand, 240 m from drive end):
- `JSR.RM.CONV1.IDLER.US` at C-47: −12 dBµV (normal −20 to −8 dBµV) — within normal, but on the high end of the normal band, suggesting early-stage bearing wear.
- `JSR.RM.CONV1.IDLER.TEMP` at C-47: 48 °C (normal 25–60 °C, IR scan).
- Motor current `JSR.RM.CONV1.MTR.CURR`: 78% FLA (normal 60–95%).
- Belt tracking `JSR.RM.CONV1.BELT.EDGE`: +5 mm (well within normal −15 to +15 mm).

### T−1 Week: Previous Patrol — Elevated US, No Action
Ultrasound reading at C-47 was −5 dBµV (above the −8 dBµV upper-normal threshold; below warning 8 dBµV). Under the previous patrol protocol, this was logged as a "watch" item but no replacement was scheduled. In retrospect, this was the earliest detectable defect stage.

### Day of Incident, T−12 min: US Alarm
Patrol technician conducting morning round reached idler C-47:
- `JSR.RM.CONV1.IDLER.US`: 16 dBµV (alarm threshold 15 dBµV). The bearing is generating significant high-frequency stress waves indicative of race-to-roller surface contact damage and lubricant failure.
- `JSR.RM.CONV1.IDLER.TEMP` (IR gun reading at C-47): 95 °C (approaching alarm threshold 100 °C; fire-risk threshold).
- Technician escalates to control room immediately; control room initiates belt emergency stop procedure.
- Fault codes IDLER-US-ALARM and IDLER-TEMP-FIRE generated (IDLER-TEMP-FIRE is a local fire-risk alert per the thermal threshold calibration).

### T=0: Belt Stop — Fire Prevented
Belt stopped within 2 minutes of technician radio call. Idler C-47 temperature at belt stop: 98 °C. Belt surface temperature at contact point: 42 °C (no scorch marks — belt material ignition threshold approximately 150 °C for EP630 rubber). **No fire occurred.**

Visual inspection post-stop: idler C-47 showing blue heat discolouration of the end-cap, consistent with sustained bearing friction heating. Belt surface showed a 180 × 40 mm surface scratch from contact with the seized idler after it stopped rotating.

---

## 4. Sensor Evidence Summary

| Tag | Normal Value | Defect Value | Threshold Crossed |
|---|---|---|---|
| JSR.RM.CONV1.IDLER.US | −14 dBµV | 16 dBµV | Alarm (15 dBµV) |
| JSR.RM.CONV1.IDLER.TEMP | 42 °C | 98 °C | Alarm (100 °C) |
| JSR.RM.CONV1.MTR.CURR | 78% FLA | 85% FLA | Within normal |
| JSR.RM.CONV1.BELT.EDGE | +5 mm | +5 mm | Normal |
| JSR.RM.CONV1.RIP.LOOP | 72 mA | 72 mA | Normal |

---

## 5. Root Cause Analysis

### Primary Root Cause
**Dry/failed idler bearing — lubrication starvation.** The idler at position C-47 is a standard TRF-manufactured sealed-for-life idler (CEMA Class D, 6308 bearing, grease-packed sealed). These idlers are designed for 30,000 hours of maintenance-free service. However, C-47 is located at the 240 m position on the return strand — a position exposed to ore spillage and high belt-wrap forces. Post-teardown inspection found:
- Outer race: circumferential fatigue spall covering 40% of the race surface
- Grease: fully carbonised (black, non-pumpable), zero lubrication remaining
- Seals: one lip seal was cut, likely by a sharp ore fragment, allowing grease escape and ore fines ingress

Ore fines ingress (iron ore with typical particle hardness 6–7 Mohs) accelerated three-body abrasive wear on the bearing race surfaces after seal failure, turning the bearing into a grinding element.

### Why Seizure Didn't Happen Earlier
The idler continued to rotate freely for some weeks after seal failure because residual grease in the bearing retained some lubricating function. The transition from running dry to full seizure is typically rapid (hours to days) once the residual grease is consumed, which explains the week-over-week ultrasound jump from −5 dBµV to 16 dBµV.

### Why This Idler Was Not Changed at −5 dBµV Warning
The previous patrol protocol had a replacement trigger at warning level (8 dBµV), but the reading of −5 dBµV (above normal but below warning) was classified as a "watch" item without a defined re-inspection interval. This is a process gap: any reading above the normal upper band should have a defined follow-up inspection within 24 hours.

---

## 6. Corrective Actions Taken

1. **Belt stop** — Emergency stop within 2 minutes of patrol alarm.
2. **LOTO** — Electrical lockout of 800 kW drive motor; mechanical lockout of belt tension system.
3. **Idler replacement:**
   - Belt lifted at C-47 using a belt lifter tool.
   - Seized idler removed; replacement `IDLER-STD-1600` (standard carrying idler, 1,600 mm belt, stock qty 40) installed.
   - Free-rotation confirmed by hand before belt lowered.
4. **Belt surface inspection** — 3 m around C-47 inspected for scorch damage; minor scratch logged; no structural damage to EP630 carcass. `JSR.RM.CONV1.RIP.LOOP` (rip detector) confirmed no open circuit = belt carcass intact.
5. **Adjacent idler inspection** — Idlers C-45 to C-50 ultrasonically tested; C-46 reading +4 dBµV (above normal threshold); scheduled for replacement within 4 hours as a follow-up.
6. **Restart** — Belt restarted after 2-hour total downtime; motor current confirmed 78% FLA; `IDLER.TEMP` on new C-47 confirmed 32 °C after 30 minutes of operation.

---

## 7. Parts Consumed

| Part ID | Description | Qty | Unit Cost (USD) | Total (USD) |
|---|---|---|---|---|
| IDLER-STD-1600 | Standard carrying idler 1,600 mm | 2 (C-47 + C-46 scheduled) | 90 | 180 |

**Parts total: USD 180**
Remainder of USD 7,500 event cost: 2-hour downtime (approximately 2,200 t/hr ore lost = 4,400 t equivalent; downstream BF burden preparation delay), labour + patrol + IR camera time.

---

## 8. Downtime

| Type | Hours |
|---|---|
| Unplanned (bearing alarm to restart) | 2 |
| Planned (scheduled adjacent idler change) | 0.5 |
| **Total** | **2.5** |

---

## 9. Recurrence Prevention

1. **Ultrasound watch-item protocol.** Any idler US reading above the normal upper band (> −8 dBµV) = 8-hour re-inspection mandatory, not "watch at next patrol." This single change would have triggered replacement 1 week earlier at the −5 dBµV reading and prevented the fire-risk escalation.
2. **Zone-based idler replacement programme.** Position C-47 at 240 m on the return strand is a known high-spillage zone (confirmed by the ore fines in the bearing). All idlers in the C-40 to C-60 range to be replaced on a 24-month proactive schedule (vs. run-to-ultrasound-alarm for clean zones).
3. **Sealed-idler life management.** Standard TRF idlers in high-contamination zones have actual life of approximately 24–30 months, not the 30,000 h nameplate rating. Document zone-specific life limits in CMMS.
4. **Continuous idler monitoring.** For the highest-fire-risk return-strand zones, evaluate permanent acoustic emission clip sensors on every 10th idler, feeding into the SCADA rather than relying solely on patrol UE frequency. This would provide continuous monitoring between patrol visits.
5. **Patrol frequency at high-risk zones.** Increase patrol frequency at high-spillage positions (C-40 to C-60) from twice-per-shift to three-times-per-shift until continuous sensors are deployed.

---

*Standards cited: UE Systems ultrasound inspection guide [unverified], CEMA Section 6 [unverified], Fenner Dunlop belt design manual [unverified]. Fire risk threshold per idler temperature > 100 °C (belt contact ignition safety standard).*
