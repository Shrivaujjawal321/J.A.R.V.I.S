# FAILURE ANALYSIS REPORT

**Report Number:** RCA-006
**Date of Report:** 2026-03-28
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
| Manufacturer | SMS Concast |
| Model | Smart segment |
| Criticality | 1 (highest) |
| Installation Date | 2019-11-22 |
| Last Overhaul | 2024-08-01 |

---

## 2. Failure Summary

| Field | Value |
|---|---|
| Scenario ID | SCN-042 |
| Failure Mode | roll_seizure |
| Fault Codes | ROLL-SEIZE, SEG-FORCE-HIGH |
| Date of Incident | 2026-03-28 |
| Time from Warning to Seizure | ~2 hours (rapid progression) |
| Unplanned Downtime | 8 hours |
| Total Cost Impact | INR 8,000,000 (~USD 96,000) |

---

## 3. Symptom Timeline

### Normal Operation (hours before event)
Caster 1 operating at 1.0 m/min casting speed, 220 mm slab format, steel grade Q345B.
- `JSR.CC1.SEG07.ROLL.RPM`: 14 rpm (normal 3–25 rpm, encoder-confirmed rotation)
- `JSR.CC1.SEG07.FORCE.HYD`: 300 kN (normal 200–400 kN clamping force)
- `JSR.CC1.SEG07.BULGE`: 0.6 mm (normal 0–1.0 mm)
- `JSR.CC1.SEG07.SPRAY.FLOW`: 200 L/min (normal 180–220 L/min)
- `JSR.CC1.SEG07.VIB.ROLL`: 1.2 mm/s (normal 0.5–2.0 mm/s)

### T−2h: Onset — Spray Nozzle Partial Blockage
Secondary cooling zone 7 spray flow (`JSR.CC1.SEG07.SPRAY.FLOW`) drops from 200 to 162 L/min over a 30-minute period (approaching warning threshold 150 L/min). Post-incident inspection revealed 2 of 8 nozzles on roll 7A partially blocked with accumulated scale and calcium carbonate deposits from process water.

The reduced spray cooling increases the roll surface temperature. The rolls on Segment 7 are hollow-shaft construction with internal water cooling; if the external spray cooling is insufficient, the roll surface heats above design temperature and differential thermal expansion reduces the bearing clearance.

### T−1.5h: Thermal Expansion — Bearing Clearance Reduction
Roll bearing temperature (inferred from external bearing housing temperature by adjacent PT100 sensors — not the dedicated `VIB.ROLL` tag) estimated at 95 °C (above rated 70 °C maximum). Internal bearing clearance reduces due to differential thermal expansion between the steel shaft and the bearing inner ring, transitioning from the designed 0.06 mm running clearance to near-zero.

`JSR.CC1.SEG07.VIB.ROLL` rises from 1.2 mm/s to 3.8 mm/s (crossing warning threshold 3.5 mm/s), indicating increased rolling contact friction as the bearing approaches a tight-clearance condition.

### T−0.5h: Seizure Initiation
- `JSR.CC1.SEG07.ROLL.RPM` drops from 14 rpm to 2 rpm (encoder pulse count falling). Partial seizure: the roll is still turning but frictional drag is increasing rapidly.
- `JSR.CC1.SEG07.FORCE.HYD` rises from 300 kN to 520 kN as the hydraulic position control attempts to maintain the segment gap against a partially-seized roll that is creating an obstruction to smooth slab withdrawal.

### T=0: Full Seizure
- `JSR.CC1.SEG07.ROLL.RPM` drops to 0 (alarm threshold: 0 rpm = seizure confirmed). The roll stops rotating; the strand is now dragged past a stationary roll.
- `JSR.CC1.SEG07.FORCE.HYD` peaks at 540 kN (alarm threshold 550 kN — approaching alarm level).
- `JSR.CC1.SEG07.BULGE` increases to 2.8 mm (exceeding warning threshold 2.0 mm), indicating strand bulging in the zone of the seized roll where cooling and guidance are inadequate.
- ROLL-SEIZE and SEG-FORCE-HIGH fault codes generated in SCADA.
- Caster operator reduces casting speed to 0.3 m/min immediately; heat ended by closing tundish gate.

---

## 4. Sensor Evidence Summary

| Tag | Normal Value | Defect Value | Threshold Crossed |
|---|---|---|---|
| JSR.CC1.SEG07.ROLL.RPM | 14 rpm | 0 rpm | Alarm (0 = seizure) |
| JSR.CC1.SEG07.FORCE.HYD | 300 kN | 540 kN | Alarm (550 kN) |
| JSR.CC1.SEG07.BULGE | 0.6 mm | 2.8 mm | Warning (2.0 mm) |
| JSR.CC1.SEG07.SPRAY.FLOW | 200 L/min | 162 L/min | Near warning (150 L/min) |
| JSR.CC1.SEG07.VIB.ROLL | 1.2 mm/s | 3.8 mm/s | Warning (3.5 mm/s) |

---

## 5. Root Cause Analysis

### Primary Root Cause
**Roll bearing seizure from thermal overload caused by spray nozzle blockage.** The causal chain is:
1. Scale and calcium carbonate deposits partially blocked 2 of 8 spray nozzles on Segment 7 (T−2h).
2. Reduced secondary cooling increased roll surface temperature above the design operating limit.
3. Differential thermal expansion closed the bearing running clearance (designed for normal temperature conditions).
4. Loss of internal running clearance in the rolling-element bearing eliminated lubricant film between the rolling elements and raceways, causing metal-to-metal galling contact, then seizure.
5. The seized roll dragged against the moving strand, generating force spikes detected by the hydraulic clamping system.

### Contributing Factor: Water Quality
Process water analysis from the cooling-water sample taken at T+4h showed elevated total dissolved solids (TDS): 820 mg/L (typical target ≤ 500 mg/L) and water hardness 340 mg/L CaCO₃ (target ≤ 200 mg/L). The elevated hardness accelerates calcium carbonate precipitation in the spray nozzles over time. The water softening unit on the secondary cooling circuit had been bypassed for 3 weeks due to a resin replacement outage — this was the root enabling condition for the nozzle blockage.

### Contributing Factor: Missed Roll Inspection
The last segment workshop inspection (2024-08-01) had noted roll 7A bearing clearance at 0.058 mm (specification 0.04–0.08 mm; near the upper limit). A clearance near the upper limit reduces the thermal margin before seizure occurs. This was documented but not flagged as requiring earlier re-inspection.

---

## 6. Corrective Actions Taken

1. **Casting speed reduction** — Speed reduced to 0.3 m/min, then heat ended; strand solidification completed over 2–4 hours before segment withdrawal.
2. **Strand cooling** — Segment 7 area allowed to cool 3 hours before caster bay entry.
3. **Segment withdrawal** — Segment 07 withdrawn via caster-bay overhead crane using segment handling fixture.
4. **Roll and bearing replacement:**
   - Seized roll 7A condemned; measured for scoring — shaft surface roughness Ra > 3 µm (specification Ra ≤ 0.8 µm for bearing seats). Roll replaced with `ROLL-SEG-STD` (strand guide roll, stock qty 2).
   - Both bearings on roll 7A replaced (`BRG-SEG-01`, stock qty 4).
5. **Spray nozzle cleaning and replacement:**
   - All 8 nozzles on Segment 7 removed, ultrasonically cleaned; 2 blocked nozzles replaced with `NOZ-SPRAY-01` (consumable; stock qty 50).
   - Nozzle pattern check: flow test at 0.5 bar confirms ± 5% of rated flow per nozzle (specification ± 8%).
6. **Segment gap reset** — Segment gap set to 222 mm for 220 mm slab format per Primetals setup tables; hydraulic pressure test at 600 kN confirmed no leakage.
7. **Water treatment bypass correction** — Water softening unit resin refilled; bypass valve closed; TDS and hardness returned to specification within 24 hours.
8. **Segment reinstallation and restart** — Segment reinstalled; caster restarted with dummy bar for sequence start. Spray flow confirmed 198–204 L/min on all zones. Roll RPM confirmed 14 rpm encoder at 1.0 m/min casting speed.

---

## 7. Parts Consumed

| Part ID | Description | Qty | Unit Cost (USD) | Total (USD) |
|---|---|---|---|---|
| ROLL-SEG-STD | Strand guide roll (standard diameter) | 1 | 9,000 | 9,000 |
| BRG-SEG-01 | Segment roll bearing | 2 | 1,200 | 2,400 |
| NOZ-SPRAY-01 | Spray nozzle (consumable) | 2 | 35 | 70 |

**Parts total: USD 11,470**
Remainder of USD 96,000 event cost: 8-hour production loss (caster downtime), hot metal cooling loss, slab quality downgrades in the affected heat.

---

## 8. Downtime

| Type | Hours |
|---|---|
| Unplanned (seizure + cooling + repair) | 8 |
| Planned | 0 |
| **Total** | **8** |

---

## 9. Recurrence Prevention

1. **Spray flow rate-of-change alert.** Add SCADA alert: spray flow drop > 10 L/min in 20 minutes = immediate maintenance investigation. Early detection at T−1.5h would have allowed nozzle clearing without roll damage.
2. **Water treatment bypass prohibition.** Water softening unit maintenance must use a backup rental resin softener or portable water treatment unit during resin regeneration; bypassing the circuit entirely is not permitted for > 4 hours.
3. **Nozzle inspection frequency.** Add quarterly nozzle flow check (removed + flow-tested) to the segment offline inspection cycle, replacing the current annual check.
4. **Roll bearing clearance action limit.** Update segment workshop procedure: roll bearing radial clearance ≥ 0.07 mm (currently 0.058 mm threshold was near upper spec) = mandatory replacement at the next segment shop visit, not deferred.
5. **Thermal margin modelling.** Implement a simple thermal margin calculator in the SCADA: if spray flow drops below 80% of design AND roll surface temperature estimate (from strand solidification model) exceeds a calculated threshold, generate a predictive alert before seizure occurs.

---

*Standards cited: SMS Concast Smart Segment design guidelines [synthetic reference], ISO 10816-3 (vibration), Primetals soft-reduction guidelines [unverified]. Cost estimate: USD 80,000–200,000 per event (research/machinery/20).*
