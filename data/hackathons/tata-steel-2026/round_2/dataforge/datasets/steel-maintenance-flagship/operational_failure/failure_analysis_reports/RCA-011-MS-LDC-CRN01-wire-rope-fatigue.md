# FAILURE ANALYSIS REPORT

**Report Number:** RCA-011
**Date of Report:** 2026-02-28
**Classification:** SYNTHETIC — physics-grounded, no proprietary Tata Steel data
**Prepared by:** Reliability Engineering, TATA_JSR Melt Shop — SAFETY CRITICAL REVIEW
**Safety Class:** P1 — POTENTIAL FATAL HAZARD (LADLE DROP)

---

## 1. Asset Identification

| Field | Value |
|---|---|
| Asset ID | MS.LDC.CRN01 |
| Equipment Class | ladle_crane |
| Description | Melt shop ladle crane hoist (molten-metal handling, safety-critical) |
| Location | MELT_SHOP / LADLE_BAY / CRANE_1_HOIST |
| Manufacturer | Konecranes |
| Model | Ladle crane 320 t |
| Safe Working Load | 320 t |
| Criticality | 1 (highest) |
| Installation Date | 2016-08-20 |
| Last Overhaul | 2024-07-05 |

---

## 2. Failure Summary

| Field | Value |
|---|---|
| Scenario ID | SCN-047 |
| Failure Mode | wire_rope_fatigue_broken_wire |
| Fault Codes | ROPE-MFL-RETIRE, ROPE-DISCARD-ISO4309 |
| Date of Detection | 2026-02-28 (during periodic MFL inspection) |
| No load was suspended at time of detection | True — crane was idle during scheduled inspection |
| Unplanned Downtime | 24 hours |
| Total Cost Impact | INR 83,000,000 (~USD 1,000,000) |
| Potential Consequence if Missed | Catastrophic — ladle drop of molten steel (up to 320 t); fatal |

---

## 3. Symptom Timeline

### History: Scheduled MFL Inspection Programme
Ladle crane hoist ropes are inspected every 3 months using magnetic flux leakage (MFL) non-destructive testing per ISO 4309:2017. Previous inspection records (November 2025):
- `JSR.MS.CRN01.ROPE.MFL`: 52 mV (normal 0–100 mV; estimated < 5% LMA)
- `JSR.MS.CRN01.LOAD.SWL`: 85% SWL maximum lift observed in 3-month period (normal)
- `JSR.MS.CRN01.BRAKE.TEMP`: 74 °C average (normal 25–90 °C)
- `JSR.MS.CRN01.GBX.VIB.GMF`: 0.3 g (normal 0–0.5 g)
- No broken wires observed by Competent Person (CP) visual inspection, November 2025

### T−12 Weeks: Previous MFL Clear
MFL reading 52 mV; CP visual inspection: 0 visible broken wires. Rope diameter: 56.2 mm (nominal 56 mm; −0.36% diameter reduction, well above −7% discard criterion). Rope returned to service.

### Inspection Day (T=0): MFL Alarm
Routine quarterly MFL inspection performed by the Competent Person (crane manufacturer-certified).
- **`JSR.MS.CRN01.ROPE.MFL` reading: 320 mV** (alarm threshold 300 mV; estimate ≥ 15–20% LMA per calibration curve).
- CP visual inspection during the MFL scan (ISO 4309:2017 requires combined MFL + visual):
  - Total random broken wires in one lay length: 14 (discard criterion: ≥ 12 random broken wires in any 1 lay length, per ISO 4309 Table 4 for ladle crane / molten metal service).
  - Broken wires in one strand within one lay length: 5 (discard criterion: ≥ 4 in one strand).
  - **Both broken-wire discard criteria met.**
- Rope diameter at the highest-LMA zone: 54.8 mm (−2.1% reduction; above −7% discard criterion but the broken-wire count takes precedence).
- Fault codes ROPE-MFL-RETIRE and ROPE-DISCARD-ISO4309 generated in the Konecranes CMMS.

### Assessment
The crane was immediately taken out of service. No load was suspended. The rope failure was detected during its scheduled inspection rather than during operation — the inspection programme performed correctly.

---

## 4. Sensor Evidence Summary

| Tag | Normal Value | Defect Value | Threshold Crossed |
|---|---|---|---|
| JSR.MS.CRN01.ROPE.MFL | 60 mV (typical) | 320 mV | Alarm (300 mV; ≥15% LMA) |
| JSR.MS.CRN01.LOAD.SWL | 50–85 %SWL | 85 %SWL | Within normal |
| JSR.MS.CRN01.BRAKE.TEMP | 70 °C | 74 °C | Within normal |
| JSR.MS.CRN01.GBX.VIB.GMF | 0.3 g | 0.4 g | Within normal |

*Note: MFL signal is the LMA proxy. Warning 150 mV ≈ 8–12% LMA (advisory); Alarm 300 mV ≈ > 15–20% LMA. Broken-wire count (14 random in one lay; 5 in one strand) and LMA are distinct metrics; both are met here. ISO 4309:2017 discard criterion: the more restrictive metric governs.*

---

## 5. Root Cause Analysis

### Primary Root Cause
**Wire-rope fatigue — broken wires exceeding ISO 4309:2017 discard criteria.** The hoist rope on a ladle crane is subject to:
1. **Cyclic bending fatigue** at sheave contacts (fleet angle, D/d ratio, reverse bending)
2. **High tensile loads** with repeated dynamic loading during ladle pick-up (slam loading, oscillation)
3. **Environmental degradation** from the melt-shop environment (thermal radiation from molten steel, steam, metallic fume)

The specific rope in service was 56 mm diameter, construction 6 × 36 IWRC (per Konecranes specification for 320 t ladle crane). With a D/d ratio at the main sheave of 18:1 (sheave diameter 1,008 mm / rope diameter 56 mm) and a maximum of 200 lifts per 24-hour period at average load 78% SWL, the rope accumulates approximately 5,400 bending cycles per month per wire at the highest-stress sheave contact.

Over the 7.5-month period since the last rope replacement (July 2024 overhaul), the wires at the drum-dead-end-termination zone and first sheave contact accumulated approximately 40,500 bending cycles. The 14 broken wires cluster in a 400 mm zone at the first sheave contact — the highest-wear zone per ISO 4309 Section 7. This is consistent with fatigue fracture at the wire surface (no reduction in tensile wire diameter; wire cross-sections confirmed circular, not necked, at fracture surfaces).

### Contributing Factor: Operating Load Profile
Production records show the preceding quarter included 12 lifts at 95–100% SWL (near the advisory threshold for ladle crane) versus the typical 3–4 per quarter. These high-load lifts increase the mean wire stress and reduce the Goodman fatigue life margin proportionally.

### Contributing Factor: Rope Age at High-Stress Service
The Konecranes recommendation for ladle-crane hoist ropes in melt-shop service is 12-month maximum service interval (regardless of inspection results). This rope was 7.5 months old with 3 months remaining in its planned service interval. Given the elevated load profile, the rope effectively consumed its fatigue life faster than the calendar schedule assumed.

---

## 6. Corrective Actions Taken

1. **Immediate out-of-service** — Crane removed from service; all lifts suspended until rope replacement complete.
2. **Production continuity** — Ladle crane 2 (CRN02, the secondary crane) used for all lifts during the 24-hour replacement period. Production rate maintained at 80% of normal (single-crane throughput limit).
3. **Rope replacement:**
   - `ROPE-CRN-01` (custom length/spec wire rope) retrieved from store (stock qty 1; custom length = 42 m for this crane configuration, pre-ordered per Konecranes spec).
   - Dead-end termination: wedge-socket type (`SOCK-WEDGE-01`, stock qty 4) — no rope clips used (prohibited on ladle cranes; clips create bending stress concentration at each clip position).
   - Fleet angle confirmed ≤ 4° at full lift range (ISO 4309 requirement to prevent accelerated wear on sheave groove).
4. **Sheave and drum inspection** — Sheave groove profiles measured; groove diameter ≤ 0.5 mm above rope diameter (within wear limit). Drum groove spiral pitch confirmed correct for 56 mm rope.
5. **Competent Person certification** — New rope inspected and certified by CP before first lift; documentation entered in crane maintenance register per Factories Act requirements.
6. **Load test** — Proof load test at 125% SWL with test block before return to production service; brake hold test at 110% SWL confirmed.

---

## 7. Parts Consumed

| Part ID | Description | Qty | Unit Cost (USD) | Total (USD) |
|---|---|---|---|---|
| ROPE-CRN-01 | Wire rope (custom length/spec) | 1 | 9,000 | 9,000 |
| SOCK-WEDGE-01 | Wedge socket (rope termination) | 2 | 350 | 700 |

**Parts total: USD 9,700**
Remainder of USD 1,000,000 event cost: 24-hour single-crane operation (20% production throughput loss in melt shop), Competent Person inspection fee, load-test contractor, risk premium for the near-miss scenario (had the rope failed during a 295-t ladle lift, direct consequences would be catastrophic; business-impact cost includes insurance and incident-response provisions).

---

## 8. Downtime

| Type | Hours |
|---|---|
| Unplanned (crane taken out of service) | 24 |
| Planned | 0 |
| **Total** | **24** |

---

## 9. Recurrence Prevention

1. **Reduce rope inspection interval for elevated-load periods.** When the production plan calls for > 8 lifts at ≥ 90% SWL in a 30-day period, the MFL inspection interval reduces from 3 months to 6 weeks for that period. Link production planning data to CMMS inspection trigger.
2. **Maximum rope service interval: 10 months.** Reduce from the current 12-month planned replacement interval to 10 months for this crane given the observed load profile. At 10 months, the broken-wire count would have been approximately 8 (below the 12-wire discard criterion), allowing scheduled replacement rather than emergency.
3. **Broken-wire visual check frequency.** Between MFL inspections, add a monthly Competent Person visual pass at the drum → first sheave zone (the highest-breakage location). Takes 15 minutes; provides an intermediate safety net between 6-week MFL intervals.
4. **High-load lift operator alert.** Configure SCADA alert: when `JSR.MS.CRN01.LOAD.SWL` ≥ 90% for 5 consecutive measurements, generate a maintenance log entry. This creates an auditable record of high-stress lift events for rope life assessment.
5. **Maintain rope stock.** ROPE-CRN-01 has 6-week lead time. Stock level = 1 should be maintained at all times; after each use, immediate reorder. This event consumed the only stock; had CRN02 also been unavailable, production would have stopped entirely.

---

*Standards cited: ISO 4309:2017 (wire rope inspection and discard criteria for cranes), FEM 1.001, BS EN 13135 (crane machinery requirements). Discard criteria per ISO 4309 Table 4: ladle-crane / molten-metal category — 12 random broken wires in 1 lay length, 4 in one strand, diameter reduction −7%. Cost benchmark: ladle-drop scenarios (Qinghe 2007) USD 1M–20M.*
