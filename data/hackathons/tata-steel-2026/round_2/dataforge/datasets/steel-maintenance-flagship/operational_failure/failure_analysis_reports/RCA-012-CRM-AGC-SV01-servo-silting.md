# FAILURE ANALYSIS REPORT

**Report Number:** RCA-012
**Date of Report:** 2026-04-22
**Classification:** SYNTHETIC — physics-grounded, no proprietary Tata Steel data
**Prepared by:** Reliability Engineering, TATA_JSR Cold Rolling Mill / Hydraulics
**Safety Class:** P2

---

## 1. Asset Identification

| Field | Value |
|---|---|
| Asset ID | CRM.AGC.SV01 |
| Equipment Class | hydraulics_agc_servo |
| Description | Cold rolling mill AGC hydraulic screwdown servo-valve circuit (precision gauge control) |
| Location | COLD_ROLLING / STAND_2 / AGC_SERVO_VALVE |
| Manufacturer | Moog |
| Model | D661 servo valve |
| Criticality | 1 (highest) |
| Installation Date | 2020-01-30 |
| Last Overhaul | 2024-09-14 |

---

## 2. Failure Summary

| Field | Value |
|---|---|
| Scenario ID | SCN-048 |
| Failure Mode | servo_valve_silting_spool_wear |
| Fault Codes | SERVO-HUNT, GAUGE-EXCURSION, ISO4406-SERVO-DIRTY |
| Date of Incident | 2026-04-22 |
| Warning-to-Loss Interval | ~2–3 days |
| Unplanned Downtime | 6 hours |
| Planned Downtime | 2 hours (valve change + kidney loop) |
| Total Cost Impact | INR 11,500,000 (~USD 137,700) |

---

## 3. Symptom Timeline

### Normal Operation Baseline
Cold rolling stand 2 AGC (automatic gauge control) maintaining 2.0 mm strip gauge to ± 5 µm. The Moog D661 servo valve operates at 200–350 bar hydraulic pressure, with oil cleanliness requirement ISO 15/13/10 (ISO 4406:2021) — critical because the D661 spool has a 1–3 µm radial clearance, making it extraordinarily sensitive to particulate contamination.

Baseline readings:
- `JSR.CR.S2.AGC.SV.ISO4406`: ISO 15/13/10 (normal; ≤ 15/13/10 for servo)
- `JSR.CR.S2.AGC.SV.POSERR`: 0.3% (normal 0–0.5%)
- `JSR.CR.S2.AGC.SV.NULLLEAK`: 0.3 L/min (normal 0–0.5 L/min)
- `JSR.CR.S2.AGC.GAUGE.DEV`: ±3 µm (normal ±5 µm)

### T−3 Days: ISO4406 Degradation
An inline particle counter on the servo circuit registers a step-change in ISO 4406 cleanliness code:
- Previous 2-week average: ISO 15/13/10
- T−3 days: ISO 16/14/11 (first-level warning threshold)
- The degradation coincides with a high-pressure hose replacement on an adjacent stand (Stand 3) — the hose replacement introduced debris into the interconnected hydraulic header, which contaminated the Stand 2 servo supply despite the on-line filtration.
- SCADA generates ISO4406-SERVO-DIRTY advisory. Maintenance team schedules kidney-loop filtration but defers for 24 hours due to planned production volume.

### T−2 Days: Spool Silting — Position Hunt
- `JSR.CR.S2.AGC.SV.POSERR` rises to 1.8% (crossing warning threshold 1.5%). The position error represents hunting: the AGC controller sends small-amplitude position commands (< 0.1 mm), but the silt-plugged spool is responding sluggishly at small amplitudes — the classic silting symptom in a single-stage torque-motor servo valve.
- The AGC controller's dead-band compensation increases hunting frequency to keep the average position close to setpoint, but the valve's effective bandwidth drops from the rated 90 Hz (−3 dB) to approximately 30 Hz.
- Strip gauge deviation `JSR.CR.S2.AGC.GAUGE.DEV`: widens to ±10 µm (warning threshold ±10 µm) — strip is at the upper quality limit.

### T−1 Day: ISO4406 Reaches Alarm
- Oil cleanliness deteriorates further to ISO 17/15/12 (alarm threshold). Silt continues to accumulate in the spool annular gap and pilot-stage nozzle passages.
- `JSR.CR.S2.AGC.SV.POSERR` reaches 3.2% (alarm threshold 3.0%; fault code SERVO-HUNT).
- `JSR.CR.S2.AGC.GAUGE.DEV`: reaches ±22 µm (alarm threshold ±20 µm; fault code GAUGE-EXCURSION). Strip out of specification. Last 8 coils at Stand 2 put on gauge hold pending inspection.
- AGC switched to backup lock (fixed screw position). Production continues but without gauge compensation — manual gauge monitoring by operator.

---

## 4. Sensor Evidence Summary

| Tag | Normal Value | Defect Value | Threshold Crossed |
|---|---|---|---|
| JSR.CR.S2.AGC.SV.ISO4406 | ISO 15/13/10 | ISO 17/15/12 | Alarm (17/15/12) |
| JSR.CR.S2.AGC.SV.POSERR | 0.3% | 3.2% | Alarm (3.0%) |
| JSR.CR.S2.AGC.GAUGE.DEV | ±3 µm | ±22 µm | Alarm (±20 µm) |
| JSR.CR.S2.AGC.SV.NULLLEAK | 0.3 L/min | 1.4 L/min | Warning (1.0 L/min) |

---

## 5. Root Cause Analysis

### Primary Root Cause
**Silt (1–5 µm particles) plugging the servo-valve spool annular gap.** The Moog D661 is a single-stage torque-motor servo valve with a 1–3 µm nominal spool-to-bore clearance. ISO 4406 particles in the 1–5 µm range (the "silt fraction," not captured by standard 10 µm-rated filters) can wedge into this clearance and resist spool movement under low-amplitude control signals. As the silt film builds up over 1–2 days after a contamination event, the valve's response to small commands becomes hysteretic and eventually threshold — the valve fails to track reference signals below a certain amplitude.

The silt particle source was the debris introduced during the adjacent hose replacement (T−3 days). Metal filings and rubber particles from the new hose end-fitting were estimated in the 2–8 µm range — exactly the size range that passes through the 10 µm online filters but plugs the servo gap.

### Why the 24-Hour Deferral Was Consequential
The ISO4406-SERVO-DIRTY advisory at T−3 days was the critical intervention point. Had the kidney-loop filtration been deployed within 4 hours (instead of deferred 24 hours), the silt concentration in the servo supply would have been reduced to ISO 15/13/10 before the cumulative deposition in the spool gap reached a threshold level. Instead, 24 hours of full-load operation with dirty oil allowed irreversible spool scoring on the high-pressure land edge (confirmed by valve bench test).

### Spool Wear Confirmation
Bench-tested replaced valve: null-leakage at 210 bar = 1.8 L/min (specification ≤ 0.5 L/min). Disassembly: scratches on land edge surface, 0.8 µm Ra (specification ≤ 0.2 µm). Valve condemned — ultrasonic cleaning would restore cleanliness but not surface finish.

---

## 6. Corrective Actions Taken

1. **AGC backup lock** — AGC transferred to fixed-screw backup mode; production continued manually.
2. **High-pressure LOTO** — 210 bar servo circuit pressure released before valve access; nitrogen blanket maintained on accumulator.
3. **Valve removal and replacement:**
   - `SERVO-VLV-D661` (Moog D661, stock qty 1) removed from store and installed.
   - Null offset calibration performed: signal input sweep ±10 mA; null null set per Moog commissioning procedure.
   - Step-response test: bandwidth confirmed 88 Hz (−3 dB) against OEM specification 90 Hz — within acceptable range post-null set.
4. **Filter replacement:**
   - `FLT-SERVO-3` (servo filter element 3 µm absolute, stock qty 4): both 3 µm elements in the servo circuit replaced.
   - Standard 10 µm elements on the high-pressure supply also replaced.
5. **Kidney-loop deployment:**
   - `KID-LOOP-01` portable kidney-loop unit connected to the servo circuit reservoir; 6-hour filtration cycle.
   - Post-loop cleanliness: ISO 14/12/09 (better than the ISO 15/13/10 target).
6. **AGC recommission:**
   - Gauge closed-loop test: step response to 0.1 mm demand = 95 ms response (specification ≤ 120 ms).
   - `JSR.CR.S2.AGC.GAUGE.DEV` confirmed ±2.8 µm at steady state — within ±5 µm normal band.
7. **Strip quality disposition:**
   - 8 coils on gauge hold: metallurgical inspection; gauge deviation ±22 µm over periods of 3–4 seconds. For hot-rolled blank supply to downstream pickling line, this deviation is within the pickling-line intake tolerance (±35 µm). All 8 coils cleared for further processing; no scrap.

---

## 7. Parts Consumed

| Part ID | Description | Qty | Unit Cost (USD) | Total (USD) |
|---|---|---|---|---|
| SERVO-VLV-D661 | Moog D661 servo valve | 1 | 14,000 | 14,000 |
| FLT-SERVO-3 | Servo filter element 3 µm absolute | 4 | 220 | 880 |

**Parts total: USD 14,880**
Remainder of USD 137,700 event cost: 6-hour AGC-backup production loss (~30% scrap-rate increase without AGC over 1-hr detection window — 8 coils × ~20 t × USD 680 scrap premium = ~USD 109,000), labour, kidney-loop operation.

---

## 8. Downtime

| Type | Hours |
|---|---|
| Unplanned | 6 |
| Planned (valve change + flush) | 2 |
| **Total** | **8** |

---

## 9. Recurrence Prevention

1. **Mandatory immediate kidney-loop on ISO4406 advisory.** ISO4406-SERVO-DIRTY (16/14/11) = deploy kidney-loop within 4 hours, no deferral. This is a P1 maintenance priority for servo circuits. Update the work-instruction priority code accordingly.
2. **Hose replacement contamination control.** Any hydraulic hose replacement within the servo supply header = mandatory oil flush of the new hose section with clean oil before reconnection to the servo circuit. Procedure: cap the servo supply at the new connection point, flush new hose with 10 volumes of clean oil into a drain bucket, then connect. Takes 10 minutes; eliminates the primary contamination mechanism in this event.
3. **Servo oil cleanliness real-time SCADA trending.** Current cleanliness data (inline particle counter) is logged at 0.01 Hz. Add a 1-hour rolling-average trend with a rate-of-change alert: any increase of 1 ISO code unit in 4 hours = immediate investigation. This enables intervention before spool deposition reaches irreversible levels.
4. **Maintain SERVO-VLV-D661 stock.** Stock was reduced to zero after this event (10-week lead time). The valve must be on stock at all times for a criticality-1 circuit. Place order for replacement stock immediately; confirm lead time with Moog and set Kanban trigger at stock = 1.
5. **Annual servo valve bench-test.** Regardless of in-situ performance, annually bench-test the installed servo valve (null leakage + frequency response) to catch developing spool wear before it affects gauge control. Cost: 1 day labour + test equipment.

---

*Standards cited: ISO 4406:2021 (hydraulic fluid cleanliness coding), Moog D661 specification sheet [synthetic reference], ISA-18.2-2016 (alarm management). AGC scrap cost data per research/machinery/20 (CRM cobble/scrap metrics).*
