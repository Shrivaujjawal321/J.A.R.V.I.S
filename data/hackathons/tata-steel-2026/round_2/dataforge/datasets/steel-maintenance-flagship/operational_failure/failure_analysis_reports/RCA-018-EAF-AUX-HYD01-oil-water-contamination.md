# FAILURE ANALYSIS REPORT

**Report Number:** RCA-018
**Date of Report:** 2026-05-10
**Classification:** SYNTHETIC — physics-grounded, no proprietary Tata Steel data
**Prepared by:** Reliability Engineering, TATA_JSR Melt Shop / Hydraulics
**Safety Class:** P2

---

## 1. Asset Identification

| Field | Value |
|---|---|
| Asset ID | EAF.AUX.HYD01 |
| Equipment Class | eaf_bof_auxiliary |
| Description | EAF/steelmaking auxiliary hydraulic power unit (electrode regulation / tilt) |
| Location | MELT_SHOP / EAF_1 / HYD_POWER_UNIT |
| Manufacturer | Bosch Rexroth |
| Model | HPU 350 bar |

---

## 2. Failure Summary

| Field | Value |
|---|---|
| Failure Mode | oil_water_contamination |
| Fault Codes | HYD-WATER-HIGH, ISO4406-DIRTY |
| Date of Detection | 2026-05-10 |
| Planned Downtime (oil change + decontamination) | 12 hours |
| Unplanned Downtime | 0 (detected proactively) |
| Total Cost Impact | INR 1,500,000 (~USD 18,000) |

---

## 3. Symptom Timeline

### Normal Background
HPU serving EAF electrode regulation (fast response hydraulics at 350 bar). Inline ISO 4406 sensor and inline water-content sensor on HPU reservoir.

### T−2 weeks: Water PPM Rising
- `JSR.MS.EAF1.HYD.WATER.PPM`: 80 ppm → 140 ppm over 2-week period (normal 0–100 ppm; approaching warning 200 ppm). SCADA records the trend but no action is triggered because the threshold was not yet crossed.
- Source: post-investigation, a pinhole crack in the water-cooled electrode cooling coil (located in the EAF vessel immediately above the HPU) was found. Steam condensate was dripping into the HPU reservoir via the return-line port.

### T−1 week: ISO 4406 Degradation
- `JSR.MS.EAF1.HYD.ISO4406`: deteriorates from 17/15/12 (normal) to 18/16/13 (warning). Water promotes oil emulsification and accelerates bacterial growth, which degrades oil lubricity and generates fine particles.
- `JSR.MS.EAF1.HYD.FILT.DP`: rises from 1.0 to 2.2 bar (approaching warning 3.0 bar) as the filter captures the water-promoted particulate contamination.
- `JSR.MS.EAF1.HYD.OIL.TEMP`: 48 °C (within normal; slightly elevated because water reduces the oil's heat-transfer coefficient).

### T=0 (Detection): HYD-WATER-HIGH Alarm
- `JSR.MS.EAF1.HYD.WATER.PPM`: 210 ppm — crossing the warning threshold of 200 ppm. HYD-WATER-HIGH alarm generated.
- `JSR.MS.EAF1.HYD.ISO4406`: at 18/16/13 (warning; one step below alarm 19/17/14).
- EAF electrode regulation still functional; no hydraulic cylinder failures detected. The early alarm is the correct response.

---

## 4. Sensor Evidence Summary

| Tag | Normal Value | Defect Value | Threshold |
|---|---|---|---|
| JSR.MS.EAF1.HYD.WATER.PPM | 80 ppm | 210 ppm | Warning (200 ppm) |
| JSR.MS.EAF1.HYD.ISO4406 | ≤17/15/12 | 18/16/13 | Warning (18/16/13) |
| JSR.MS.EAF1.HYD.FILT.DP | 1.0 bar | 2.2 bar | Near warning (3.0 bar) |
| JSR.MS.EAF1.HYD.OIL.TEMP | 46 °C | 48 °C | Normal |

---

## 5. Root Cause Analysis

**Oil-water contamination from pinhole crack in electrode cooling-circuit coil.** The EAF electrode cooling system uses high-pressure water. A pinhole fatigue crack in a coil section (caused by thermal cycling and vibration from the 60 Hz AC arcing) allowed water droplets to enter the HPU reservoir via the proximity of the coil to the return-line port. Hydraulic oil with > 200 ppm water loses its hydrodynamic film strength significantly (ISO/TR 10949 estimate: film strength falls 15–25% at 0.1% water content), risking servo valve and cylinder wear.

---

## 6. Corrective Actions Taken

1. EAF electrode regulation switched to manual-speed control while HPU serviced.
2. HPU oil change: full drain, reservoir cleaned; new hydraulic oil charge.
3. `FLT-HYD-10` elements (2×) replaced.
4. `KID-LOOP-01` portable kidney-loop filtration: 8-hour cycle after oil change.
5. Cooling coil pinhole identified and section replaced by EAF mechanical team.
6. Post-change water ppm confirmed < 50 ppm; ISO 4406 confirmed ≤ 16/14/11.

---

## 7. Parts Consumed

| Part ID | Description | Qty | Cost (USD) |
|---|---|---|---|
| FLT-HYD-10 | Hydraulic filter element 10 µm | 3 | 360 |
| KID-LOOP-01 | Kidney-loop unit (day rental) | 1 | 450 |

**Parts total: USD 810.** Remainder of USD 18,000: oil charge, labour, planned downtime.

---

## 8. Recurrence Prevention

1. **Water-PPM rate-of-change alert at 10 ppm/day.** The 2-week climb from 80 to 140 ppm was an actionable trend. A rate-of-change alert would have flagged this 10 days earlier.
2. **Annual cooling-coil inspection** with pressure test at 1.5× operating pressure on electrode cooling circuits; pinhole cracks are detectable with eddy-current or hydraulic leak test before they become contamination sources.

---

*Asset: EAF.AUX.HYD01. Failure mode: oil_water_contamination. Standards: ISO 4406:2021, ISO/TR 10949 [unverified], Bosch Rexroth HPU maintenance guide [synthetic].*
