# FAILURE ANALYSIS REPORT

**Report Number:** RCA-001
**Date of Report:** 2026-03-14
**Classification:** SYNTHETIC — physics-grounded, no proprietary Tata Steel data
**Prepared by:** Reliability Engineering, TATA_JSR Hot Rolling Division
**Safety Class:** P2

---

## 1. Asset Identification

| Field | Value |
|---|---|
| Asset ID | HSM.F3.WR.BRG01 |
| Equipment Class | rolling_mill_work_roll_bearing |
| Description | Hot Strip Mill Finishing Stand F3 work-roll chock bearing (oil-film + 4-row cylindrical roller neck bearing) |
| Location | HOT_ROLLING / FINISHING_STAND_3 / WORK_ROLL_DE_CHOCK |
| Manufacturer | SKF |
| Model | Oil-film bearing + 4-row cylindrical roller neck brg |
| Rated Speed | 600 rpm |
| Criticality | 1 (highest) |
| Installation Date | 2020-04-12 |
| Last Overhaul | 2024-09-03 |

---

## 2. Failure Summary

| Field | Value |
|---|---|
| Scenario ID | SCN-037 |
| Failure Mode | outer_race_fatigue_spall_BPFO |
| Fault Codes | VIB-BPFO-DANGER, TEMP-TRIP-100C |
| Date of Incident | 2026-03-14 |
| Time to Failure from First Warning | ~4 weeks |
| Unplanned Downtime | 12 hours |
| Planned (subsequent) | 5 hours |
| Total Cost Impact | INR 7,500,000 (~USD 90,000) |

---

## 3. Symptom Timeline

### Week 0–6: Healthy Baseline
- All sensors within normal bands
- `JSR.HR.STD3.WR.BRG01.VIB.DE.H.RMS`: 1.4–1.6 mm/s (normal 0.5–2.3 mm/s, ISO 20816-3:2022 Zone A)
- `JSR.HR.STD3.WR.BRG01.VIB.DE.ENV.BPFO`: 0.25–0.30 g (normal ≤ 0.5 g)
- `JSR.HR.STD3.WR.BRG01.TEMP.DE`: 58 °C (normal 40–70 °C)
- `JSR.HR.STD3.WR.BRG01.AE.RMS`: 0 dBµV (normal −2 to +2 dBµV)
- `JSR.HR.STD3.WR.BRG01.OFB.OUT.TEMP`: 57 °C (normal 50–65 °C)

### Weeks 6–8: Stage 1 — AE Leading Indicator Activated
- Acoustic emission (`JSR.HR.STD3.WR.BRG01.AE.RMS`) begins rising from 0 to 6 dBµV, crossing the AE warning threshold of 6 dBµV at approximately week 7.
- No change observed on vibration velocity or envelope spectrum — AE is the earliest indicator per ISO 15243 bearing-defect progression physics.
- Maintenance notified; no immediate action taken pending confirmation.

### Weeks 8–10: Stage 2 — BPFO Envelope Alarm, AE Elevated
- `JSR.HR.STD3.WR.BRG01.AE.RMS` reaches 8 dBµV (above warning 6, below alarm 12). This represents a Stage 2 onset — the subsurface fatigue crack has propagated to the surface and is generating repetitive stress-wave transients.
- `JSR.HR.STD3.WR.BRG01.VIB.DE.ENV.BPFO` climbs rapidly: 0.3 → 1.0 g (crossing warning threshold at 1.0 g) → 3.2 g (crossing alarm threshold at 3.0 g per ISO 15243:2017). The envelope frequency corresponds to the outer-race BPFO calculated at 600 rpm with the known roller complement of the 4-row cylindrical neck bearing.
- Broadband vibration velocity `JSR.HR.STD3.WR.BRG01.VIB.DE.H.RMS` begins to rise above baseline: 1.6 → 4.8 mm/s (crossing ISO 20816-3 Zone B→C warning threshold of 4.5 mm/s).
- Outer ring temperature `JSR.HR.STD3.WR.BRG01.TEMP.DE` drifts upward from 58 °C to 85 °C (warning threshold reached), indicating frictional heat generation as the spall disrupts the lubricant film.

### Last 24–48 Hours Before Controlled Stop: Stage 3 / Stage 4 — Multi-Sensor Alarm
- `JSR.HR.STD3.WR.BRG01.TEMP.DE` escalates rapidly to 102 °C, exceeding the TRIP threshold of 100 °C. Thermal runaway indicates the oil-film is breaking down over the spalled race area.
- `JSR.HR.STD3.WR.BRG01.OFB.OUT.TEMP` rises to 79 °C (above warning 75 °C), confirming heat is being conducted into the oil circuit.
- Fault codes VIB-BPFO-DANGER and TEMP-TRIP-100C generated in the plant SCADA.
- Operations team initiates controlled deceleration of F3 stand; production transferred to F4 finishing stand. Rolling stopped after current coil discharge.

---

## 4. Sensor Evidence Summary

| Tag | Normal Value | Defect Value | Threshold Crossed | Stage |
|---|---|---|---|---|
| JSR.HR.STD3.WR.BRG01.AE.RMS | 0 dBµV | 8 dBµV | Warning (6) | 2 |
| JSR.HR.STD3.WR.BRG01.VIB.DE.ENV.BPFO | 0.30 g | 3.2 g | Alarm (3.0 g) | 3 |
| JSR.HR.STD3.WR.BRG01.VIB.DE.H.RMS | 1.6 mm/s | 4.8 mm/s | Warning (4.5 mm/s) | 3 |
| JSR.HR.STD3.WR.BRG01.TEMP.DE | 58 °C | 102 °C | TRIP (100 °C) | 4 |
| JSR.HR.STD3.WR.BRG01.OFB.OUT.TEMP | 57 °C | 79 °C | Warning (75 °C) | 3 |

---

## 5. Root Cause Analysis

### Primary Root Cause
**Subsurface rolling-contact fatigue initiating outer-race spall** (classified per ISO 15243:2017 Section 5.1 — normal fatigue from cyclic Hertzian contact stress). The outer-race spall is identifiable by the BPFO-frequency envelope content and confirmed by the progression pattern: AE leads by 2–3 weeks before any vibration-velocity change, followed by BPFO envelope growth, then thermal escalation — this is the textbook four-stage bearing-defect progression.

### Contributing Factor
**Lubricant contamination accelerating fatigue.** Oil-film bearing outlet temperature trending upward over the preceding 6-week period (57 → 62 °C before the failure window) suggests the oil-film viscosity degraded or minor contamination from scale water ingress occurred. Contamination reduces the oil-film lambda ratio (λ = film thickness / composite surface roughness), causing increased asperity contact and subsurface stress intensification that shortens the L10 fatigue life per ISO 281 modified life theory.

### Why Not Other Failure Modes?
- Inner-race spall (BPFI) was ruled out: envelope spectrum showed BPFO content, not BPFI sidebands.
- Lubrication starvation: OFB outlet temperature was elevated but the oil-pump pressure readings remained nominal; starvation would show abrupt AE spike rather than progressive BPFO growth.

---

## 6. Corrective Actions Taken

Actions per Playbook 01 (LOTO + controlled-stop protocol):

1. **Lockout/Tagout** — Zero-energy state confirmed before any bearing access. Hydraulic WR balance pressure vented; cooling water isolated.
2. **Controlled stop** — Mill brought to rest under Zone D alarm (temp > 100 °C); no emergency trip used to avoid thermal shock to the oil-film surfaces.
3. **Bearing removal** — Hydraulic bearing puller used; no hammer contact on bearing faces.
4. **Journal inspection** — Neck journal measured: 0.08 mm below nominal OEM H7/k6 fit tolerance. Surface-ground to restore roundness and surface finish Ra ≤ 0.4 µm before reinstallation.
5. **New bearing installation** — Replacement `BRG-LRG-300` (large-bore roller bearing > 300 mm, stock qty 1, lead time 8 weeks; stock replenished per Kanban trigger) induction-heated to 80–100 °C; seated without impact. Laser alignment verified < 0.05 mm TIR on drive-side chock.
6. **Ancillary replacement** — Coupling element (`CPL-EL-01`) and labyrinth seal set (`SEAL-LAB-01`) replaced as a standard set during the window.
7. **Oil system flush** — OFB circuit flushed; cleanliness sample taken (target ISO 4406:2021 ≤ 16/14/11 for this bearing class).
8. **Post-repair verification** — Mill run at 50% speed for 30 minutes; `JSR.HR.STD3.WR.BRG01.VIB.DE.H.RMS` confirmed 1.4 mm/s, `TEMP.DE` 62 °C at 60 minutes. Both within normal bands; stand returned to service.

---

## 7. Parts Consumed

| Part ID | Description | Qty | Unit Cost (USD) | Total (USD) |
|---|---|---|---|---|
| BRG-LRG-300 | Large-bore roller bearing > 300 mm | 1 | 12,000 | 12,000 |
| SEAL-LAB-01 | Labyrinth seal set | 1 | 600 | 600 |
| CPL-EL-01 | Coupling element | 1 | 450 | 450 |
| LUBE-NOZ-01 | Oil-film bearing lube nozzle (precautionary) | 1 | 120 | 120 |

**Parts total: USD 13,170**

---

## 8. Downtime

| Type | Hours |
|---|---|
| Unplanned (production loss during progression phase) | 12 |
| Planned (bearing replacement window) | 5 |
| **Total** | **17** |

Production loss estimate at ~500 t/hr HSM throughput × 12 unplanned hours = ~6,000 t strip not produced. At approximate margin of USD 12–15/t, production-loss portion of cost impact dominates the total USD 90,000 figure.

---

## 9. Recurrence Prevention

1. **Reduce AE warning response time.** The 2-week gap between AE warning and bearing change decision is too long for a criticality-1 stand. New procedure: AE warn + BPFO > 1.0 g = mandatory P1-scheduled roll change within 72 hours (next roll change window rather than next planned overhaul).
2. **Oil contamination monitoring.** Install inline particle counter on OFB return circuit; target ISO 4406 ≤ 15/13/10 sustained. Any step-change in cleanliness code triggers lube investigation within 24 hours.
3. **Spare bearing Kanban trigger.** With an 8-week lead time on BRG-LRG-300, reorder point should be set at stock qty = 1; incident reduced stock to 0. Order placed same day as bearing removal.
4. **BPFO baseline trending.** Add automated BPFO trending (weekly rolling average) to PdM dashboard. Alert on > 20% week-over-week increase even if absolute value is below warning threshold.
5. **Scale water ingress inspection.** At next scheduled roll change, inspect chock labyrinth seal condition and scale water deflectors; root cause of contamination must be addressed to prevent repeat fatigue acceleration.

---

*This report is based on synthetic but physics-grounded data. Site-specific calibration mandatory before any production deployment. Standards cited: ISO 15243:2017 (bearing failure modes), ISO 20816-3:2022 (vibration zones), ASTM E2374-14 (acoustic emission), SKF OFB guide.*
