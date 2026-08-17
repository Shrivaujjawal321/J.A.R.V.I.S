# FAILURE ANALYSIS REPORT

**Report Number:** RCA-005
**Date of Report:** 2026-02-19
**Classification:** SYNTHETIC — physics-grounded, no proprietary Tata Steel data
**Prepared by:** Reliability Engineering, TATA_JSR Blast Furnace / Ironmaking
**Safety Class:** P1 — SAFETY CRITICAL

---

## 1. Asset Identification

| Field | Value |
|---|---|
| Asset ID | BF.BLW.FAN01 |
| Equipment Class | bf_sinter_fan_blower |
| Description | Blast furnace turbo-blower / cold-blast machine (Tier-1 critical) |
| Location | BLAST_FURNACE / BLOWER_HOUSE / TURBO_BLOWER_1 |
| Manufacturer | Siemens / MAN |
| Model | Axial blast machine |
| Rated Power | 28,000 kW |
| Rated Speed | 3,600 rpm |
| Criticality | 1 (highest) |
| Installation Date | 2016-03-01 |
| Last Overhaul | 2023-10-12 |

---

## 2. Failure Summary

| Field | Value |
|---|---|
| Scenario ID | SCN-041 |
| Failure Mode | compressor_surge |
| Fault Codes | SURGE-ALARM, ASV-CYCLING |
| Date of Incident | 2026-02-19 |
| Surge Duration | ~8 cycles over 6 minutes before trip |
| Unplanned Downtime | 96 hours (blast furnace reduced-blast recovery) |
| Total Cost Impact | INR 500,000,000 (~USD 6,000,000) |

---

## 3. Symptom Timeline

### Prior to Incident: Operating Point Drift
The BF turbo-blower operates continuously. Over the 7 days preceding the surge event, the blast furnace burden had been modified to a higher-coke-rate campaign (BF operators adjusting for incoming iron ore fines with lower reducibility). The combined effect was a moderate reduction in blast volume demand (estimated 12% below normal operating flow) while blast pressure was held approximately constant — moving the operating point left on the compressor characteristic curve toward the surge envelope.

The anti-surge controller (ASV: anti-surge valve) had been cycling increasingly frequently over 3 days, indicating the operating margin to the surge line was reducing.

### Day 0, Hour 0: Normal Baseline
- `JSR.BF.BLW.FAN01.VIB.1X`: 1.8 mm/s (normal 1.0–2.3 mm/s, ISO 10816-3:2009 Group 3 Zone A)
- `JSR.BF.BLW.FAN01.SHAFT.DISP`: 35 µm pk-pk (normal 10–50 µm, API 670:2014 Table 1)
- `JSR.BF.BLW.FAN01.TEMP.BRG`: 60 °C (normal 45–65 °C)
- `JSR.BF.BLW.FAN01.THRUST.TEMP`: 68 °C (normal 50–75 °C)
- `JSR.BF.BLW.FAN01.PRES.OSC`: 1.0% (normal 0–2%)

### Hour 0, T+0: Triggering Event — Downstream Valve Slam
A manual hot-blast valve on blast main #2 was inadvertently slammed shut during a routine blast equalisation operation. This caused an instantaneous step increase in downstream pressure, sharply reducing the flow through the blower to near zero. The operating point crossed the surge line in < 1 second.

### Hours 0 to +0.1: Surge Onset
- `JSR.BF.BLW.FAN01.PRES.OSC` spikes to 9% (alarm 8%) — the pressure oscillation signal captures the characteristic surge oscillation: discharge pressure collapses as backflow occurs, then rebuilds as the compressor re-establishes forward flow, cycling at 2–5 Hz.
- `JSR.BF.BLW.FAN01.SHAFT.DISP` rises to 95 µm pk-pk (warning 80 µm; API 670:2014 trip set at 127 µm). The axial displacement spike reflects the alternating axial thrust reversal during each surge cycle — the compressor's rotor slams axially forward and back as flow periodically reverses.
- Anti-surge valve `ASV-VLV-01` auto-opens (ASV-CYCLING alarm triggered).

### Hours 0.1 to +0.1 (6 minutes): 8 Surge Cycles
- Surge cycling continues at approximately 1.3 cycles/minute (reflecting the large volume of the BF bustle pipe and hot stoves between the compressor and the blast orifices — surge frequency inversely proportional to plenum volume).
- `JSR.BF.BLW.FAN01.VIB.1X` rises to 5.8 mm/s during surge peaks (alarm 7.1 mm/s; approaching trip).
- `JSR.BF.BLW.FAN01.THRUST.TEMP` rises to 108 °C (alarm 105 °C) — repeated thrust reversals are overloading the Babbitt thrust bearing pads.
- `JSR.BF.BLW.FAN01.TEMP.BRG` rises to 82 °C (warning 80 °C), indicating journal bearing heating from the high-amplitude shaft motion.
- After the 8th surge cycle, SURGE-ALARM trips the blower. Blast furnace goes to no-blast condition.

---

## 4. Sensor Evidence Summary

| Tag | Normal Value | Defect Value | Threshold Crossed |
|---|---|---|---|
| JSR.BF.BLW.FAN01.PRES.OSC | 1.0% | 9.0% | Alarm (8%) |
| JSR.BF.BLW.FAN01.SHAFT.DISP | 35 µm | 95 µm | Warning (80 µm) |
| JSR.BF.BLW.FAN01.VIB.1X | 1.8 mm/s | 5.8 mm/s | Warning (4.5 mm/s) |
| JSR.BF.BLW.FAN01.THRUST.TEMP | 68 °C | 108 °C | Alarm (105 °C) |
| JSR.BF.BLW.FAN01.TEMP.BRG | 60 °C | 82 °C | Warning (80 °C) |

---

## 5. Root Cause Analysis

### Immediate Cause
**Downstream valve slam.** Manual operation of hot-blast valve #2 during routine blast equalisation caused an instantaneous flow reduction that crossed the surge line. The human action was procedurally incorrect — equalisation valve operation requires a controlled throttle-over-60-seconds procedure that was not followed.

### Contributory Cause 1: Reduced Surge Margin
The shift in BF burden composition over the preceding 7 days had moved the operating point leftward on the characteristic curve, reducing the surge-margin from the designed ≥ 15% to an estimated ≤ 6% at the time of the valve slam. This narrowed margin meant that even a partial disturbance would have been sufficient to trigger surge; the valve slam simply was the specific event that triggered it.

### Contributory Cause 2: Inlet Filter Fouling
Post-incident inspection found the inlet filter differential pressure had risen to 1.2 kPa above the nominal 0.4 kPa (measured during blower decontamination), equivalent to an effective reduction in inlet flow area. This further restricted achievable flow and shifted the characteristic curve rightward (reducing surge margin). The inlet filter had last been changed at the October 2023 overhaul — 16 months prior.

### Physical Damage Assessment
- Thrust bearing pads (`BRG-JRNL-PAD`) — 3 of 6 Babbitt pads showed cracking and partial extrusion from the repeated axial loading during surge cycling. Pads condemned and replaced.
- Journal bearing: visual inspection showed minor fretting on the lower-half pad surface (≤ 0.2 mm Babbitt loss); within acceptable limits per OEM specification; cleaned and returned to service.
- IGVs and impellers: borescope inspection found no blade damage. Clearance at tip ≤ 0.5 mm within spec.

---

## 6. Corrective Actions Taken

1. **Immediate trip maintained** — Blower not restarted until surge cause fully identified (per standard protocol: do not restart until cause is resolved).
2. **Blast furnace management** — BF placed on no-blast / natural gas support (stove-isolated hold). Production rate reduced by ~65% for 96-hour recovery period.
3. **Blower inspection** — Forced borescope of all IGV stages and impeller passages; shaft inspected for axial scratch marks in journal; oil ferrography of journal bearing circuit.
4. **Thrust bearing pad replacement** — `BRG-JRNL-PAD` set (3 damaged pads) replaced with OEM Babbitt tilting-pad set.
5. **Inlet filter renewal** — Inlet filter elements replaced; differential pressure post-replacement: 0.4 kPa (nominal).
6. **Anti-surge line recalibration** — Process engineers recalculated surge line per OEM compressor map at the current burden-modified operating point. Anti-surge controller setpoint advanced by 8% flow margin to account for the observed rightward shift of the compressor characteristic.
7. **Operator retraining** — Blast equalisation procedure formalized; hot-blast valve operation during blower-online conditions classified as a 2-person-authorised task with a mandatory 60-second ramp.
8. **Post-restart protocol** — Blower started unloaded, stepped to 50% load over 2 hours, surge margin verified at each step against recalibrated ASC line.

---

## 7. Parts Consumed

| Part ID | Description | Qty | Unit Cost (USD) | Total (USD) |
|---|---|---|---|---|
| BRG-JRNL-PAD | Journal bearing pads (OEM tilting-pad) | 1 set | 25,000 | 25,000 |
| ASV-VLV-01 | Anti-surge valve (post-inspection: no replacement needed; ASV functional) | 0 | — | — |

**Parts total: USD 25,000**
Remainder of USD 6,000,000 event cost: 96-hour BF production loss at approximately USD 500,000/hr reduced rate (iron production loss, downstream steelmaking schedule disruption), plus labour and contractor inspection costs.

---

## 8. Downtime

| Type | Hours |
|---|---|
| Unplanned (blower trip + BF reduced-blast recovery) | 96 |
| Planned | 0 |
| **Total** | **96** |

---

## 9. Recurrence Prevention

1. **Surge margin monitoring — real-time operating point plot.** Implement real-time operating-point overlay on compressor characteristic map in the blower control room. Alert operator when margin < 10%; mandatory ASC setpoint review when < 8%.
2. **Burden-change protocol.** Any BF burden modification exceeding ±8% coke rate = mandatory blower anti-surge setpoint review before shift start. Link to BF production planning.
3. **Hot-blast valve interlock.** Instrument hot-blast valve #2 and all manual blast valves with a position-rate limiter (maximum 2° per second) enforced by PLC interlock during blower-online conditions. Bypass requires 2-person authorisation.
4. **Inlet filter differential pressure trend.** Set `DP > 0.8 kPa` = planned filter change within 30 days (not deferred to annual overhaul). This single modification would have eliminated the contributory cause.
5. **Surge cycle count tracking.** Each surge cycle accelerates bearing and seal fatigue. Implement cumulative surge-cycle counter in SCADA; ≥ 3 cycles/month = P2 anti-surge system review.

---

*Standards cited: API 670:2014 (machinery protection, shaft displacement), API 617 (centrifugal compressor surge), ISO 10816-3:2009 (fan/blower vibration). Equipment: Siemens/MAN axial blast machine [synthetic reference]. Cost benchmark: BF blower outage USD 4–8M (research/machinery/20 iron-making uptime data).*
