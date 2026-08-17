# FAILURE ANALYSIS REPORT

**Report Number:** RCA-008
**Date of Report:** 2025-12-04
**Classification:** SYNTHETIC — physics-grounded, no proprietary Tata Steel data
**Prepared by:** Reliability Engineering, TATA_JSR Hot Rolling / Roll Shop
**Safety Class:** P2

---

## 1. Asset Identification

| Field | Value |
|---|---|
| Asset ID | HSM.STD.R1 |
| Equipment Class | hot_strip_mill_stand |
| Description | Hot Strip Mill roughing stand R1 (work rolls, AGC screwdown, roll-force load cells) |
| Location | HOT_ROLLING / ROUGHING_STAND_1 / MILL_STAND |
| Manufacturer | Primetals |
| Model | 4-high reversing stand |
| Criticality | 1 (highest) |
| Installation Date | 2017-09-10 |
| Last Overhaul | 2024-01-25 |

---

## 2. Failure Summary

| Field | Value |
|---|---|
| Scenario ID | SCN-044 |
| Failure Mode | work_roll_spall_flat |
| Fault Codes | FORCE-RIPPLE-HIGH, SURFACE-DEFECT-PERIODIC |
| Date of Incident | 2025-12-04 |
| Detection Lead Time | ~4 hours (force ripple warning to spall confirmation) |
| Planned Roll Change Time | 45 minutes |
| Unplanned Downtime | 4 hours (strip segregation + roll extraction) |
| Total Cost Impact | INR 15,400,000 (~USD 184,000) |

---

## 3. Symptom Timeline

### Normal Campaign Operation
R1 working under normal campaign load, rolling 200 mm thick slab to 25–35 mm transfer bar. Work roll grade: HSS (high-speed steel), 800 mm nominal diameter. Roll campaign: day 8 of scheduled 10-day campaign before planned roll change.

Baseline readings:
- `JSR.HR.R1.FORCE`: 1.2% ripple (normal 0–2%)
- `JSR.HR.R1.WR.VIB.CHOCK`: 0.6 mm/s (normal 0–1.0 mm/s)
- `JSR.HR.R1.CROWN.DEV`: 6 µm (normal −10 to +10 µm)
- `JSR.HR.R1.WR.AE.RMS`: 0 dB (normal −3 to +3 dB)

### T−8h: Pre-spall — Cobble Thermal Shock
At T−8h, a minor slab cobble on R1 (third cobble in this campaign) caused a momentary reverse-roll thermal shock: the work roll surface, normally at 450–550 °C in the roll bite zone, contacted the back face of the cobbled slab creating a thermal quench. This is the primary known initiator of HSS work-roll subsurface fatigue spalling in roughing stands.

The cobble itself was minor (< 2-minute recovery) and no abnormal vibration was detected at that time. However, the thermal shock accelerated an existing subsurface defect at the layer interface between the HSS shell layer and the nodular iron core.

### T−4h: Stage 1 — Rolling Force Ripple Warning
- `JSR.HR.R1.FORCE` (rolling force ripple at load cells) rises to 4.2% (approaching warning threshold 4%).
- The force ripple is periodic, occurring at a frequency matching the top work roll's rotational period (1× roll frequency at 600 rpm = 10 Hz). This is the classic signature of a spall or flat on the roll surface: as the spalled zone passes through the roll bite, the load cell sees a brief force dip (spall = reduced contact area = lower force), creating a periodic sinusoidal pattern.
- `JSR.HR.R1.WR.AE.RMS` rises to 5 dB (approaching warning 8 dB), indicating contact-zone acoustic emission from the edge-of-spall stress concentration.

### T−2h: Stage 2 — Alarm Level
- `JSR.HR.R1.FORCE` reaches 8.5% ripple (alarm threshold 8%; fault code FORCE-RIPPLE-HIGH generated).
- `JSR.HR.R1.WR.VIB.CHOCK` rises from 0.6 to 6.0 mm/s (alarm threshold 10.0 mm/s, approaching rapidly). The increasing chock vibration reflects dynamic impacts as the spall fragment edge repeatedly strikes the incoming slab surface.
- Online surface inspection camera (`SURFACE-DEFECT-PERIODIC` fault code): periodic strip surface marks at a pitch of π × D_roll = π × 0.800 m = 2.51 m — confirming the spall is printing on the strip. Strip affected over the last 14 slabs.
- Rolling stopped on the affected product; last 14 coils flagged for quality hold and downgrade assessment.

---

## 4. Sensor Evidence Summary

| Tag | Normal Value | Defect Value | Threshold Crossed |
|---|---|---|---|
| JSR.HR.R1.FORCE | 1.2% | 8.5% | Alarm (8%) |
| JSR.HR.R1.WR.VIB.CHOCK | 0.6 mm/s | 6.0 mm/s | Warning (4.0 mm/s) |
| JSR.HR.R1.WR.AE.RMS | 0 dB | 5 dB | Near warning (8 dB) |
| JSR.HR.R1.CROWN.DEV | 6 µm | 32 µm | Warning (25 µm) |

---

## 5. Root Cause Analysis

### Primary Root Cause
**Subsurface roll defect activated by cobble-induced thermal shock.** HSS work rolls have a metallurgical interface between the HSS outer shell (typically 35–65 mm depth in a new 800 mm diameter roll) and the ductile iron or cast steel core. This interface is a preferential site for subsurface fatigue crack initiation under cyclic Hertzian contact stress. Normal campaigns expose the interface to millions of roll bite cycles; a cobble thermal shock (rapid surface quench followed by internal reheating as the roll re-enters service) creates a steep thermal gradient that generates compressive surface stresses and tensile subsurface stresses near the interface — the exact conditions for spall initiation.

The third cobble was the final increment of damage on an already-stressed roll in day 8 of a 10-day campaign. Fractographic analysis of the spalled fragment post-examination showed:
- Main crack: horizontal plane at 15–20 mm below the roll surface (consistent with maximum shear stress depth at this contact width)
- Secondary crack: vertical, connecting the horizontal crack to the surface (pop-out mechanism)
- Shell appearance: classical "oyster-shell" texture — conchoidal fracture with radial ridges pointing to the initiation site near the interface

### Contributing Factors
1. **Campaign duration.** Day 8 of a 10-day campaign accumulates approximately 4–5 million roll-bite contact cycles, approaching the design fatigue limit for the shell thickness remaining at this point in the campaign.
2. **Cumulative cobble history.** Three cobbles in one campaign is above the target of ≤ 1 per campaign for R1 (roughing stand cobbles create the most severe thermal shock due to higher slab temperature ≥ 1,150 °C and longer contact time). Internal target: replace work rolls after 2nd cobble in a campaign regardless of campaign day.
3. **Existing subsurface initiation site.** Post-mortem UT of the condemned roll found a second spall-initiating crack at an adjacent circumferential position — this roll had a manufacturing inclusion at that location, making it predisposed to early spall.

---

## 6. Corrective Actions Taken

1. **Rolling stopped** — After last slab in the pass schedule; no emergency stop required as the spall was detected at warning stage with force ripple trending, allowing orderly completion of the current pass and withdrawal.
2. **Strip quality hold** — Last 14 coils from affected campaign placed on quality hold; 3 coils downgraded to cold-forming grade (minor surface marks accepted); 11 passed normal inspection (strip marks below threshold for cold-rolled downstream use).
3. **Work roll quick-change (45 minutes):**
   - `WR-HSS-PREP` (prepared work roll pair from roll shop, stock qty 4) installed.
   - Chock seals `CHOCK-SEAL-01` replaced as standard during roll change.
   - New rolls laser-verified for taper: within 15 µm/m specification.
4. **Failed roll dispatch to roll shop:**
   - Spall volume measured: 12 × 18 × 3 mm. Roll diameter remaining (800 − 3 mm × 2) = 794 mm (above condemn diameter 750 mm).
   - Grinding: 4 mm below spall zone removed; surface finish Ra = 0.6 µm confirmed by profilometer.
   - UT inspection after grind: no additional subsurface cracks detected at new surface level. Roll returned to service.
5. **Manufacturing inclusion record.** Roll serial number flagged with UT-detected inclusion location; this roll assigned to a lower-criticality service position for the next campaign.

---

## 7. Parts Consumed

| Part ID | Description | Qty | Unit Cost (USD) | Total (USD) |
|---|---|---|---|---|
| WR-HSS-PREP | Prepared work roll pair (HSS, roll shop) | 1 pair | 80,000 | 80,000 |
| CHOCK-SEAL-01 | Roll chock seals | 1 set | 350 | 350 |

**Parts total: USD 80,350**
Remainder of USD 184,000 event cost: strip quality downgrade losses (3 coils × approximately 20 t × USD 50/t downgrade premium), unplanned 4-hour downtime, labour.

---

## 8. Downtime

| Type | Hours |
|---|---|
| Unplanned | 4 |
| Planned (roll change) | 0.75 |
| **Total** | **4.75** |

---

## 9. Recurrence Prevention

1. **Two-cobble roll change rule.** Formalise in CMMS: any work roll experiencing ≥ 2 cobbles in a single campaign = mandatory roll change at the next opportunity, regardless of campaign day. This event was the 3rd cobble; the rule should have triggered after the 2nd.
2. **Rolling force ripple trending.** Add automated Fourier-decomposition of the load cell signal at 1× roll frequency to the PdM dashboard. Trend the 1× amplitude; alert on > 10% week-over-week increase. This would have identified the post-cobble subsurface damage development 24 hours earlier.
3. **Pre-campaign UT inspection.** Add a brief UT check (phased-array, 5-minute per roll) as part of the roll-shop preparation process (`WR-HSS-PREP`) before each campaign. Reject rolls with any subsurface indication > 3 mm diameter at depths < 25 mm.
4. **Roll tracking database.** Log each roll's cobble history, UT status, and grinding history in CMMS by serial number. Link to PdM thresholds — rolls with known inclusions receive a 10% lower force-ripple alarm threshold.
5. **Surface inspection camera calibration.** The `SURFACE-DEFECT-PERIODIC` signal fired correctly here; ensure the period-matching algorithm is calibrated quarterly against the actual current roll diameter (which changes with each grinding cycle).

---

*Standards cited: OxMaint roll change cost data (planned USD 11.2k vs unplanned USD 184k, 16.4× ratio), research/machinery/20 Section 2D. Roll fatigue physics per HSS work-roll literature (Siebel/Kobasa).*
