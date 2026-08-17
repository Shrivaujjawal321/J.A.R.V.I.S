# FAILURE ANALYSIS REPORT

**Report Number:** RCA-019
**Date of Report:** 2025-12-18
**Classification:** SYNTHETIC — physics-grounded, no proprietary Tata Steel data
**Prepared by:** Reliability Engineering, TATA_JSR Blast Furnace Cooling Water
**Safety Class:** P2

---

## 1. Asset Identification

| Field | Value |
|---|---|
| Asset ID | BF.CW.PMP02 |
| Equipment Class | cooling_descaling_pump |
| Description | Blast furnace cooling-water circulation pump (large centrifugal) |
| Location | BLAST_FURNACE / COOLING_WATER / PUMP_102 |
| Manufacturer | KSB |
| Model | Omega double-suction |
| Rated Power | 900 kW |
| Rated Speed | 990 rpm |

---

## 2. Failure Summary

| Field | Value |
|---|---|
| Failure Mode | impeller_wear_erosion |
| Fault Codes | HEAD-DEV-WARN, VIB-BB-WARN |
| Date of Detection | 2025-12-18 (trending; planned corrective action) |
| Planned Downtime (impeller + wear-ring replacement) | 16 hours |
| Unplanned Downtime | 0 |
| Total Cost Impact | INR 2,200,000 (~USD 26,300) |

---

## 3. Symptom Timeline

### T−4 months: Head Deviation First Warning
- `JSR.BF.CW.PMP02.HEAD.DEV`: −4% (warning threshold −7%). Differential head is 4% below design — early indication of impeller wear reducing hydraulic efficiency.
- `JSR.BF.CW.PMP02.VIB.1X`: 1.8 mm/s (normal range 0.5–1.8 mm/s; on upper edge).
- No bearing temperature anomaly.

### T−2 months: Continued Degradation
- `JSR.BF.CW.PMP02.HEAD.DEV`: −6% (warning threshold −7%; nearly triggered).
- `JSR.BF.CW.PMP02.VIB.BB`: 1.8 mm/s — this is a mildly-elevated reading, not the baseline (baseline normal value is 1.2 mm/s per the normal range 0.5–1.5 mm/s; 1.8 is above upper normal but below warning 2.5 mm/s). The broadband vibration increase reflects the hydraulic turbulence from impeller vane wear — worn vane tips create asymmetric wakes that excite broadband noise.
- `JSR.BF.CW.PMP02.TEMP.BRG`: 68 °C (near upper normal 70 °C).
- Planned corrective action scheduled for December planned outage.

### T=0 (Planned Outage): Detection and Replacement
- `JSR.BF.CW.PMP02.HEAD.DEV`: −8% (crossing warning threshold −7%; alarm is −12%). Planned maintenance window correctly coincided with the progression — replacement before alarm.
- `JSR.BF.CW.PMP02.VIB.BB`: 2.3 mm/s (approaching warning 2.5 mm/s).
- Fault codes HEAD-DEV-WARN and VIB-BB-WARN confirmed.

---

## 4. Sensor Evidence Summary

| Tag | Normal Value | Defect Value | Threshold |
|---|---|---|---|
| JSR.BF.CW.PMP02.HEAD.DEV | 0% | −8% | Warning (−7%) |
| JSR.BF.CW.PMP02.VIB.BB | 1.2 mm/s | 2.3 mm/s | Near warning (2.5 mm/s) |
| JSR.BF.CW.PMP02.VIB.1X | 1.4 mm/s | 1.9 mm/s | Normal |
| JSR.BF.CW.PMP02.TEMP.BRG | 55 °C | 68 °C | Normal |

---

## 5. Root Cause Analysis

**Impeller vane erosion from suspended solids in the blast furnace cooling water.** BF cooling water circulates through the blast furnace tuyere cooling panels, jacket, staves, and hot blast stove piping — all heat exchanger circuits subject to iron oxide, scale, and occasional infiltration from the blast furnace gas-cooling system. The double-suction Omega design has two impeller halves; wear was asymmetric (left-side eye more worn) likely due to slightly unbalanced inlet flow distribution from the suction manifold geometry.

Post-inspection measurements: impeller vane tip clearance had grown from 0.4 mm (new) to 1.8 mm (worn) on the left side. This additional clearance allows recirculation flow from discharge to suction, reducing hydraulic efficiency by approximately 8–10% (matching the −8% HEAD.DEV reading).

The wear rings `WRING-CW-01` showed a similar clearance increase from 0.2 mm to 0.6 mm, contributing to the recirculation and reduced head.

---

## 6. Corrective Actions Taken

1. Standby cooling pump PMP01 started; PMP02 isolated at planned window.
2. Full pump disassembly; impeller condemned (vane tip clearance 1.8 mm; reject criterion > 1.5 mm).
3. `IMP-CW-01` (double-suction cooling impeller, stock qty 1) installed; new `WRING-CW-01` wear rings (stock qty 2).
4. Pump reassembled; bearing clearances checked; shaft end-float 0.12 mm (within 0.08–0.18 mm spec).
5. Post-restart: `HEAD.DEV` confirmed 0% (design head); `VIB.BB` 1.3 mm/s.

---

## 7. Parts Consumed

| Part ID | Description | Qty | Cost (USD) |
|---|---|---|---|
| IMP-CW-01 | Cooling pump impeller (double-suction) | 1 | 6,500 |
| WRING-CW-01 | Wear ring set | 2 | 800 |

**Parts total: USD 7,300.** Remainder: 16-hour planned window labour.

---

## 8. Recurrence Prevention

1. **Impeller replacement interval: 36 months** (actual wear life was 26 months from installation 2024-04-11 overhaul; reduce interval accordingly).
2. **Water treatment improvement.** Add a 25 µm in-line filter on the BF cooling-water header return to remove scale particles before they recirculate through the pump. Estimated 30% wear-rate reduction.
3. **HEAD.DEV rate-of-change alert.** If head deviation becomes 0.5% more negative per month for 2 consecutive months → flag for planned inspection within 60 days.

---

*Asset: BF.CW.PMP02. Failure mode: impeller_wear_erosion. Standards: HI 9.6.7-2021 (head-flow tolerance), ISO 10816-7:2009 (pump vibration).*
