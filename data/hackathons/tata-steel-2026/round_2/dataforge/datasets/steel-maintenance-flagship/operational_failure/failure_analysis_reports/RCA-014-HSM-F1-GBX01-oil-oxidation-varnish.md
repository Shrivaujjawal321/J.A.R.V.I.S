# FAILURE ANALYSIS REPORT

**Report Number:** RCA-014
**Date of Report:** 2025-10-02
**Classification:** SYNTHETIC — physics-grounded, no proprietary Tata Steel data
**Prepared by:** Reliability Engineering, TATA_JSR Hot Rolling Division
**Safety Class:** P3

---

## 1. Asset Identification

| Field | Value |
|---|---|
| Asset ID | HSM.F1.GBX01 |
| Equipment Class | mill_gearbox |
| Description | Hot Strip Mill F1 main-drive reduction gearbox (forced-lube, ISO VG 220) |
| Location | HOT_ROLLING / FINISHING_STAND_1 / MAIN_GEARBOX |
| Manufacturer | Flender |

---

## 2. Failure Summary

| Field | Value |
|---|---|
| Failure Mode | oil_oxidation_varnish |
| Fault Codes | OIL-VISC-HIGH, OIL-TEMP-WARN |
| Date of Detection | 2025-10-02 (scheduled oil sample analysis) |
| Planned Downtime (oil change) | 8 hours |
| Unplanned Downtime | 0 |
| Total Cost Impact | INR 420,000 (~USD 5,000) |

---

## 3. Symptom Timeline

### T−6 Months: Previous Oil Sample
`JSR.HR.STD1.GBX01.OIL.VISC`: 220 cSt at 40 °C (exactly VG 220 nominal — oil at this time was relatively new, changed 4 months prior).
`JSR.HR.STD1.GBX01.OIL.TEMP`: 58 °C (normal 45–65 °C).
`JSR.HR.STD1.GBX01.OIL.FE.PPM`: 3 ppm (normal). No varnish concern.

### T−3 Months: Mid-Interval Sample
`JSR.HR.STD1.GBX01.OIL.VISC`: 235 cSt — rising toward upper normal bound (242 cSt). Laboratory reporting: "oil beginning to polymerise; varnish potential index (VPI) = 38 (target ≤ 30)."
`JSR.HR.STD1.GBX01.OIL.TEMP`: 63 °C (near upper normal, indicating reduced heat-transfer efficiency of varnish-coated heat-exchanger surfaces).

### T=0 (Detection): Scheduled Annual Oil Analysis
- `JSR.HR.STD1.GBX01.OIL.VISC`: 268 cSt — exceeding the upper alarm threshold of 265 cSt (ISO 3448 VG 220 +15% = 253 cSt warning, +20% = 264 cSt is effectively an alarm band based on the spine's 265 cSt threshold). The viscosity increase reflects oxidative polymerisation — long-chain oil molecules cross-linking into sticky varnish precursors.
- `JSR.HR.STD1.GBX01.OIL.TEMP`: 68 °C (rising; varnish coating on the sump walls and heat-exchanger baffles reduces thermal conductivity).
- `JSR.HR.STD1.GBX01.OIL.FE.PPM`: 6 ppm (slightly above normal 5 ppm upper bound; varnish on gear faces acts as a mild abrasive, generating fine metallic particles).
- Visual inspection of sump drain plug shows yellow-brown lacquer deposits — classic varnish appearance.
- `JSR.HR.STD1.GBX01.VIB.GMF.RMS`: 3.2 mm/s (within normal; no gear damage yet — the varnish finding is a pre-failure condition).

---

## 4. Sensor Evidence Summary

| Tag | Normal Value | Defect Value | Threshold |
|---|---|---|---|
| JSR.HR.STD1.GBX01.OIL.VISC | 218 cSt | 268 cSt | Alarm (265 cSt) |
| JSR.HR.STD1.GBX01.OIL.TEMP | 56 °C | 68 °C | Near warning (80°C) |
| JSR.HR.STD1.GBX01.OIL.FE.PPM | 3 ppm | 6 ppm | Warning (15 ppm) |
| JSR.HR.STD1.GBX01.VIB.GMF.RMS | 2.8 mm/s | 3.2 mm/s | Normal |

---

## 5. Root Cause Analysis

**Oil oxidation and varnish formation from extended service at elevated sump temperature.** The ISO VG 220 EP oil was 10 months old (change interval is 12 months). The combination of operating at the upper end of the normal temperature range (58–68 °C over the period) and normal air contact in the partially-enclosed sump caused cumulative oxidative degradation. ISO VG 220 mineral oil oxidation rate roughly doubles per 10 °C temperature rise (Arrhenius rule of thumb); operating at 65–68 °C rather than the nominal 55 °C sump design point accelerated the degradation.

The varnish precursors (insoluble degradation products) coat internal sump surfaces, the pump screen, and eventually the gear tooth flanks. Left unaddressed, varnish progressively reduces lubrication film thickness, increases sump operating temperature further (positive feedback), and ultimately contributes to gear surface micropitting — which was the failure mode being proactively prevented here.

This event was a **pre-failure condition caught by scheduled oil analysis** — not a full failure event. The cost is the planned oil change plus sump cleaning, versus the USD 600,000 gear-tooth fatigue event (RCA-002) that could result if oil condition is ignored.

---

## 6. Corrective Actions Taken

1. Scheduled oil change at next planned maintenance window (8-hour outage).
2. Full drain of sump; solvent-flush of sump walls and baffle surfaces to remove varnish deposits.
3. New charge `OIL-VG220` (2 × 200 L drums); new `FLT-GBX-01` filter elements (2×).
4. Oil cooler tubes inspected: 30% varnish film removed by flush; cooling performance restored.
5. Post-change sample at 2 weeks: OIL.VISC 219 cSt, OIL.TEMP 57 °C — nominal.

---

## 7. Parts Consumed

| Part ID | Description | Qty | Cost (USD) |
|---|---|---|---|
| OIL-VG220 | ISO VG 220 EP gear oil (200 L) | 2 | 1,800 |
| FLT-GBX-01 | Gearbox oil filter element | 2 | 360 |

**Parts total: USD 2,160.** Event cost reflects planned labour only.

---

## 8. Recurrence Prevention

1. **Reduce oil change interval to 9 months** for this gearbox given its documented tendency to operate at the upper normal temperature band.
2. **VPI monitoring.** Add varnish potential index (VPI, ASTM D7843 or equivalent) to the routine oil analysis panel. VPI > 30 = schedule oil change within 60 days; VPI > 50 = schedule change within 30 days.
3. **Sump temperature reduction.** Investigate oil cooler bypass control: maintain sump temperature at 55–58 °C (lower end of normal) rather than allowing drift to 65 °C.

---

*Asset: HSM.F1.GBX01 (same as RCA-002; different failure mode — oxidation/varnish). This report demonstrates a PREVENTIVE detection scenario.*
