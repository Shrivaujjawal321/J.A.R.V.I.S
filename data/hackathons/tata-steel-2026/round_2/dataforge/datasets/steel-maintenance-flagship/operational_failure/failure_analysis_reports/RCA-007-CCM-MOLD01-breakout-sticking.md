# FAILURE ANALYSIS REPORT

**Report Number:** RCA-007
**Date of Report:** 2026-01-15
**Classification:** SYNTHETIC — physics-grounded, no proprietary Tata Steel data
**Prepared by:** Reliability Engineering, TATA_JSR Continuous Casting — INCIDENT REVIEW BOARD
**Safety Class:** P1 — SAFETY CRITICAL / POTENTIAL FATAL HAZARD

---

## 1. Asset Identification

| Field | Value |
|---|---|
| Asset ID | CCM.MOLD.01 |
| Equipment Class | continuous_caster_mould |
| Description | Continuous caster copper mould (Caster 1, slab) with thermocouple array + oscillator |
| Location | CASTER_1 / MOLD / MOLD_ASSY |
| Manufacturer | SMS Concast |
| Model | Slab mould Cu-Cr-Zr plate |
| Criticality | 1 (highest) |
| Installation Date | 2021-02-14 |
| Last Overhaul | 2024-10-20 |

---

## 2. Failure Summary

| Field | Value |
|---|---|
| Scenario ID | SCN-043 |
| Failure Mode | breakout_sticking |
| Fault Codes | BPS-BREAKOUT-P1, TC-VPATTERN, OSC-FRICTION-SPIKE |
| Date of Incident | 2026-01-15 |
| Time from BPS alarm to emergency stop | 72 seconds |
| No injuries | Yes — floor cleared per BPS alarm protocol |
| Unplanned Downtime | 36 hours |
| Total Cost Impact | INR 71,810,000 (~USD 860,000) |

---

## 3. Symptom Timeline

### Normal Operation (preceding 40 minutes)
Caster 1 running at 1.1 m/min, 250 mm × 1,500 mm slab format, peritectic steel 0.12% C. Mould flux: standard high-viscosity powder for medium carbon.
- `JSR.CC1.MOLD.TC.DELTA`: 12 °C (normal 0–20 °C)
- `JSR.CC1.MOLD.OSC.FRICTION`: 5 kN (normal 2–8 kN)
- `JSR.CC1.MOLD.LEVEL.DEV`: 1.0 mm (normal −2 to +2 mm)
- `JSR.CC1.MOLD.HEATFLUX`: 1.6 MW/m² (normal 1.2–2.0 MW/m²)

### T−8 min: Mould Level Disturbance
A SEN (submerged entry nozzle) partial clogging event (scale from tundish transition) causes intermittent flow asymmetry. `JSR.CC1.MOLD.LEVEL.DEV` swings between −4 and +4 mm (crossing warning threshold 5 mm). Mould level controller compensates, but the level oscillation disturbs the mould-flux feeding pattern.

### T−5 min: Flux Channelling — Early Sticking Precursor
Uneven flux feeding results in a flux-depleted zone on the broad face near the shell solidification front. At 0.12% C (peritectic composition), the solidification shrinkage during the delta-to-gamma transformation creates a thin, fragile shell. Without adequate flux lubrication, the shell surface begins sticking to the copper mould wall locally.

### T−3 min: Stage 1 — TC Delta First Warning
- `JSR.CC1.MOLD.TC.DELTA` begins showing asymmetric profile: thermocouples on rows 2–3 in one quadrant of the broad face show a localised cold spot (relative dip of 8 °C), while adjacent TCs remain at baseline.
- `JSR.CC1.MOLD.OSC.FRICTION` rises from 5 to 11 kN (crossing warning threshold 10 kN). The oscillation system is experiencing increased drag as the stuck shell resists withdrawal.
- These two signals constitute a Stage 1 BPS warning; BPS (Breakout Prevention System) enters advisory mode.

### T−1.5 min: Stage 2 — BPS Three-Sensor Alarm
- **BPS condition met (3-sensor agreement required to minimise false alarms):**
  - `JSR.CC1.MOLD.TC.DELTA` develops a propagating V-pattern: the localised cold spot grows across 4 adjacent TC positions with delta of 55 °C (alarm threshold 50 °C). The V-pattern is the classical signature of a sticking breakout: the initially-stuck zone widens as the shell tears upward under withdrawal force, creating a 'V' of cold (thin) shell points progressing up the mould face.
  - `JSR.CC1.MOLD.OSC.FRICTION` peaks at 19 kN (alarm threshold 18 kN). The oscillation drive is fighting the full-width shell attachment.
  - `JSR.CC1.MOLD.LEVEL.DEV` reaches 13 mm deviation (alarm 12 mm) as the partial shell blockage disrupts meniscus control.
- `JSR.CC1.MOLD.HEATFLUX` drops to 0.82 MW/m² (alarm 0.8 MW/m²); the stuck and thinned shell acts as a thermal insulator, reducing heat extraction.
- **BPS-BREAKOUT-P1 alarm generated. All three sensor conditions met simultaneously.**
- Fault codes: BPS-BREAKOUT-P1, TC-VPATTERN, OSC-FRICTION-SPIKE.

### T=0: Emergency Response — 72 Seconds
Following the P1 BPS alarm, the operator executes the emergency procedure:
1. **T+0 s:** Automatic speed reduction begins — casting speed reduces from 1.1 m/min to 0.5 m/min (minimum) in 15 seconds.
2. **T+15 s:** Floor PA alarm activated; caster platform staff evacuate to safe positions ≥ 10 m from the caster floor.
3. **T+30 s:** Casting speed still at 0.5 m/min; OSC friction still elevated (16 kN). Operator calls emergency stop.
4. **T+45 s:** Full emergency stop — withdrawal drive stopped; tundish gate closed.
5. **T+72 s:** Liquid steel remaining in the mould cavity is isolated; no breakout occurred. Shell was partially adhered but the emergency stop was executed within the 60–90 second window that prevents a full-shell rupture.

---

## 4. Sensor Evidence Summary

| Tag | Normal Value | Defect Value | Threshold Crossed |
|---|---|---|---|
| JSR.CC1.MOLD.TC.DELTA | 12 °C | 55 °C | Alarm (50 °C) |
| JSR.CC1.MOLD.OSC.FRICTION | 5 kN | 19 kN | Alarm (18 kN) |
| JSR.CC1.MOLD.LEVEL.DEV | 1.0 mm | 13 mm | Alarm (12 mm) |
| JSR.CC1.MOLD.HEATFLUX | 1.6 MW/m² | 0.82 MW/m² | Alarm (0.8 MW/m²) |

---

## 5. Root Cause Analysis

### Immediate Cause
**Shell sticking to mould wall from inadequate flux lubrication at the peritectic composition.** The 0.12% carbon grade is in the peritectic valley of the iron-carbon diagram where the δ→γ solidification transformation produces a volumetric shrinkage of approximately 0.3–0.4%, creating a locally thin and fragile shell. This grade demands the most careful flux management of any carbon range. The localised flux depletion from the SEN-clogging-induced level disturbance created a zone of direct metal-to-mould contact.

### Root Enabling Condition
**SEN partial clogging causing level oscillation.** The tundish was in the transition from heat 1 to heat 2 when alumina inclusions from the ladle shroud accumulated on the SEN bore. This is a known risk for Al-killed steel grades that generate Al₂O₃ agglomerates. The SEN had been in service for 4 hours at this point (specification maximum 5 hours per heat for this grade); it was approaching end-of-life but had not yet been flagged for imminent replacement.

### Systemic Contributing Factor
**BPS false-alarm rate.** Post-incident review of the preceding 4 weeks showed 8 BPS advisory warnings (single-sensor) and 2 three-sensor warnings, all of which were false alarms (confirmed retrospectively — no breakout occurred). High false-alarm experience has historically led operators to delay emergency response. Operator reported: "I hesitated for 5–8 seconds before initiating speed reduction because I expected it to clear." This hesitation, while understandable, reduced the margin. The 72-second response was still within the safe window, but process redesign should not rely on operator experience to compensate for false alarms.

### Physical Findings (post-cooldown inspection)
- Mould broad-face copper plate: abrasion and pickup marks over a 40 × 180 mm zone at approximately 200 mm below the meniscus. Copper plate condemned due to exceeding 15% maximum acceptable wear depth.
- Segments 1–3: minor skull deposits; removed with oxygen lance; rolls confirmed undamaged.
- SEN bore: post-mortem inspection showed 60% flow area restriction from Al₂O₃ clogging.

---

## 6. Corrective Actions Taken

1. **Emergency stop maintained** — Strand left in place until fully solidified (5.5 hours for 250 mm slab at this position).
2. **Floor clearance** — All personnel cleared from caster floor during solidification; area entry by authorised personnel only.
3. **Skull removal** — Oxygen lancing of skull from mould and top segments after solidification confirmed by infrared probe (surface < 200 °C before entry).
4. **Mould copper plate replacement** — Broad-face plate showing pickup zone condemned; replaced with `MOLD-CU-STD` (stock qty 1, lead time 14 weeks — order for replacement stock placed immediately).
5. **Segment inspection and cleaning** — Segments 1–3 inspected; spray nozzles cleared; rolls confirmed free-rotating.
6. **SEN replacement** — New `SEN-NOZ-01` installed for restart.
7. **Tundish inspection** — Ladle shroud + tundish slide gate inspected; slag-eye confirmed sealed; tundish relining ordered for next campaign.
8. **5-Whys RCA completed within 48 hours** — per SMS Concast breakout response protocol (CCM Playbook).
9. **Caster restart** — Dummy-bar restart after 36-hour total downtime; all checks completed before resuming normal casting.

---

## 7. Parts Consumed

| Part ID | Description | Qty | Unit Cost (USD) | Total (USD) |
|---|---|---|---|---|
| MOLD-CU-STD | Mould copper plates (standard slab format) | 1 | 55,000 | 55,000 |
| ROLL-SEG-STD | Strand guide roll (precautionary check; returned serviceable) | 0 | — | — |
| SEN-NOZ-01 | Submerged entry nozzle (consumable) | 2 | 800 | 1,600 |

**Parts total: USD 56,600**
Remainder of USD 860,000 event cost: 36-hour caster downtime (approximately 300 t/hr throughput × 36 h = 10,800 t lost production), quality downgrade costs on the partially-cast heat, post-breakout inspection and cleaning labour.

---

## 8. Downtime

| Type | Hours |
|---|---|
| Unplanned | 36 |
| Planned | 0 |
| **Total** | **36** |

---

## 9. Recurrence Prevention

1. **SEN replacement at 4-hour maximum for 0.12% C grade.** Change SEN replacement schedule: peritectic grades (0.08–0.15% C) = maximum 4 hours (not 5), regardless of visual appearance.
2. **BPS false-alarm root cause analysis.** 8 false alarms in 4 weeks is unacceptably high. Initiate BPS sensor calibration audit; review TC array for ageing thermocouples (TCs > 1,500 operating hours = replace); recalibrate OSC friction baseline quarterly.
3. **Operator-BPS training refresh.** Simulate breakout alarm scenarios in the training simulator quarterly. The 5–8 second hesitation observed is a training failure. Response time target: < 3 seconds from alarm to speed reduction initiation.
4. **Automatic speed reduction.** Upgrade BPS to auto-initiate speed reduction to 0.5 m/min within 2 seconds of BPS-BREAKOUT-P1 alarm, without waiting for operator action. Manual override required to resume speed. This change eliminates the operator hesitation risk.
5. **Mould-plate copper wear tracking.** Track cumulative heats per copper plate; 0.12% C grade causes higher wear. Maximum 800 heats per plate for this grade (vs. 1,000 for general grades).

---

*Standards cited: EP2465622B1 (TC-array BPS pattern detection), EN 746-2:2010, SMS Concast smart mould protocols [synthetic]. Cost benchmark: OxMaint USD 860k/event average; FeroLabs USD 200k–3M range (research/machinery/20).*
