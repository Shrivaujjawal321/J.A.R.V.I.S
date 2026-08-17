# FAILURE ANALYSIS REPORT

**Report Number:** RCA-002
**Date of Report:** 2026-01-22
**Classification:** SYNTHETIC — physics-grounded, no proprietary Tata Steel data
**Prepared by:** Reliability Engineering, TATA_JSR Hot Rolling Division
**Safety Class:** P2

---

## 1. Asset Identification

| Field | Value |
|---|---|
| Asset ID | HSM.F1.GBX01 |
| Equipment Class | mill_gearbox |
| Description | Hot Strip Mill F1 main-drive reduction gearbox (forced-lube, ISO VG 220) |
| Location | HOT_ROLLING / FINISHING_STAND_1 / MAIN_GEARBOX |
| Manufacturer | Flender |
| Model | H4SH-mill drive |
| Rated Power | 6,000 kW |
| Criticality | 1 (highest) |
| Installation Date | 2018-06-20 |
| Last Overhaul | 2023-11-15 |

---

## 2. Failure Summary

| Field | Value |
|---|---|
| Scenario ID | SCN-038 |
| Failure Mode | gear_tooth_fatigue_crack |
| Fault Codes | GMF-DANGER, CHIP-DETECT-ALARM |
| Date of Incident | 2026-01-22 |
| Degradation Onset (first warning) | ~Week 8 of 10-week degradation window |
| Unplanned Downtime | 168 hours (7 days) |
| Total Cost Impact | INR 50,100,000 (~USD 600,000) |

---

## 3. Symptom Timeline

### Weeks 0–8: Healthy Baseline
Gearbox operating under normal load. Sensors within band:
- `JSR.HR.STD1.GBX01.VIB.GMF.RMS`: 2.8 mm/s (normal 0.5–4.0 mm/s, AGMA 9005-F16)
- `JSR.HR.STD1.GBX01.OIL.TEMP`: 56 °C (normal 45–65 °C)
- `JSR.HR.STD1.GBX01.OIL.PRES`: 3.2 bar (normal 2.5–4.0 bar)
- `JSR.HR.STD1.GBX01.OIL.FE.PPM`: 3 ppm (normal 0–5 ppm)
- `JSR.HR.STD1.GBX01.OIL.VISC`: 218 cSt at 40 °C (normal 198–242 cSt for VG 220 ±10%)

### Weeks 8–9: Stage 1 — Cepstrum Rahmonics / GMF Sideband Rise
A cobble event on F1 stand 7 weeks prior had applied a brief torque spike estimated at 140% rated. This nucleated a tooth-root fatigue crack on the high-speed pinion.
- GMF band vibration begins rising: 2.8 → 6.2 mm/s — crossing the warning threshold of 6.0 mm/s.
- Cepstrum analysis shows first and second rahmonics of the mesh-to-shaft frequency ratio rising by 6 dB, indicative of periodic modulation at shaft rotational frequency — consistent with a single-tooth defect.
- Oil temperature rises moderately: 56 → 71 °C (still below 80 °C warning).

### Week 9–10: Stage 2 — Chip Detector Triggered
- `JSR.HR.STD1.GBX01.OIL.FE.PPM` rises sharply: 3 → 60 ppm, crossing alarm threshold of 40 ppm. This indicates chunky ferrous spall debris consistent with fatigue crack propagation and surface delamination.
- Inline chip detector triggers CHIP-DETECT-ALARM.
- `JSR.HR.STD1.GBX01.VIB.GMF.RMS` reaches 11.0 mm/s (alarm threshold 10.0 mm/s).
- Oil viscosity drops to 192 cSt (below warning threshold of 180 cSt), likely due to elevated debris heating and possible water ingress from cooling-water circuit leakage.
- Fault codes GMF-DANGER and CHIP-DETECT-ALARM generated simultaneously in SCADA.

### Immediate Pre-failure: Decision Point
At 11.0 mm/s GMF RMS and 60 ppm Fe, the tooth has lost structural integrity. Operations team initiates controlled stop; the crack front has propagated through approximately 60% of the tooth-root cross-section based on post-failure metallographic examination.

---

## 4. Sensor Evidence Summary

| Tag | Normal Value | Defect Value | Threshold Crossed |
|---|---|---|---|
| JSR.HR.STD1.GBX01.VIB.GMF.RMS | 2.8 mm/s | 11.0 mm/s | Alarm (10.0 mm/s) |
| JSR.HR.STD1.GBX01.OIL.FE.PPM | 3 ppm | 60 ppm | Alarm (40 ppm) |
| JSR.HR.STD1.GBX01.OIL.TEMP | 56 °C | 72 °C | Near warning (80 °C) |
| JSR.HR.STD1.GBX01.OIL.VISC | 218 cSt | 192 cSt | Near warning (180 cSt) |
| JSR.HR.STD1.GBX01.OIL.PRES | 3.2 bar | 3.0 bar | Within normal |

---

## 5. Root Cause Analysis

### Primary Root Cause
**Tooth-root fatigue crack from prior high-torque cobble event.** A strip cobble on F1 stand 7 weeks before failure subjected the main drive gearbox to a transient torque spike (estimated 140% rated by integration of the drive motor current record). The Flender H4SH design nominal safety factor on tooth root bending stress is approximately 1.4–1.6 per ISO 6336; the cobble spike temporarily exceeded this margin, initiating a sub-critical fatigue crack at the tooth-root fillet radius — the highest stress concentration in the gear tooth geometry.

The crack propagated under cyclic bending at normal rated load over the subsequent 7 weeks, following the Paris law crack-growth regime. The exponential rise in Fe ppm (3 → 60 ppm) in the final 1–2 weeks reflects accelerating surface delamination as the crack front neared the pitch-line surface.

### Contributing Factors
1. **Gear campaign duration.** The gearbox had been in continuous service for 26 months since last overhaul (2023-11-15). While within the 36-month planned interval, the cobble event effectively reset the fatigue clock without being logged as a maintenance trigger event.
2. **Oil degradation.** Viscosity at 192 cSt (below 198 cSt lower warning bound) suggests partial oxidation and possible minor water ingress over the 26-month service period, increasing metal-on-metal asperity contact and accelerating surface fatigue at the tooth flanks.
3. **Chip detector response latency.** The inline chip detector was on a 15-minute sampling cycle; the transition from 5 → 60 ppm Fe took approximately 36 hours, meaning 2 sampling intervals elapsed after the first detectable rise before the alarm triggered. Earlier response (hourly sampling or 24-hour ferrography) would have provided an additional ~24-hour warning margin.

---

## 6. Corrective Actions Taken

1. **Immediate controlled stop** — No deferral after CHIP-DETECT-ALARM. Mill F1 brought to rest; adjacent stands F2–F7 continued on reduced schedule.
2. **Gearbox removal** — Unit extracted via overhead crane to the gearbox repair bay (12-hour operation requiring specialized crane and rigging).
3. **Disassembly and inspection** — Full strip-down; tooth fracture confirmed at high-speed pinion, tooth 7 of 43. Root metallography showed inter-granular fatigue fracture with beach marks, consistent with progressive crack propagation over multiple weeks.
4. **Component replacement:**
   - Primary: `GEAR-WHL-M20` (custom large-module gear wheel) ordered; 36-week lead time from Flender. Interim repair using reconditioned spare sourced from sister plant at 18-day logistics transit.
   - `BRG-GBX-SET` (input/output bearing set) replaced as standard practice during major teardown.
5. **Backlash and contact verification** — Gear tooth backlash set to 0.18 mm (within 0.1–0.3 mm spec). Prussian-blue contact print confirmed > 75% face width coverage (spec ≥ 70%).
6. **Oil system renewal** — Full oil drain; sump cleaned; new `OIL-VG220` charge (ISO VG 220 EP, 200 L drum × 2). Filter element `FLT-GBX-01` replaced.
7. **Run-in sequence** — 4-hour run-in at 25% load, 25% speed; 2-hour at 50% load before return to full production. GMF RMS confirmed 2.6 mm/s, Fe ppm at 4 after 48-hour re-run.

---

## 7. Parts Consumed

| Part ID | Description | Qty | Unit Cost (USD) | Total (USD) |
|---|---|---|---|---|
| GEAR-WHL-M20 | Custom large-module gear wheel | 1 | 120,000 | 120,000 |
| BRG-GBX-SET | Gearbox input/output bearing set | 1 | 4,500 | 4,500 |
| OIL-VG220 | ISO VG 220 EP gear oil (200 L drum) | 2 | 900 | 1,800 |
| FLT-GBX-01 | Gearbox oil filter element | 2 | 180 | 360 |

**Parts total: USD 126,660**
Remainder of USD 600,000 event cost: production loss (~7-day outage), crane + labour, interim spare logistics.

---

## 8. Downtime

| Type | Hours |
|---|---|
| Unplanned (gearbox failure + repair) | 168 (7 days) |
| Planned | 0 |
| **Total** | **168** |

---

## 9. Recurrence Prevention

1. **Cobble event protocol.** Mandate a post-cobble maintenance inspection trigger: any drive-train torque spike exceeding 120% rated (detected from motor current integration) = 48-hour escalated oil sampling (ferrography) + GMF baseline reset. This event was missed because the cobble log was not linked to a proactive condition-monitoring flag.
2. **Reduce chip-detector sampling interval** from 15 minutes to continuous inline monitoring; alarm on 10 ppm/hr rate-of-change rather than absolute threshold only.
3. **Long-lead spare pre-positioning.** GEAR-WHL-M20 has a 36-week lead time and zero stock. A consignment arrangement with Flender for one maintained spare is essential for a criticality-1 gearbox; the 18-day borrow from a sister plant was a significant risk.
4. **Annual oil ferrography.** Move from event-triggered to annual scheduled ferrography sampling to catch sub-threshold metallic-wear trends before they accumulate.
5. **GMF sideband index trending.** Add automated cepstrum rahmonics tracking (shaft orders 1×, 2× around GMF) to PdM dashboard. Threshold: > 3 dB month-over-month increase = P2 investigation.

---

*Standards cited: AGMA 9005-F16 (gearbox vibration), ISO 6336 (gear tooth strength), ASTM D5185 / ISO 4406:2021 (oil analysis), Flender H4SH maintenance manual [synthetic reference].*
