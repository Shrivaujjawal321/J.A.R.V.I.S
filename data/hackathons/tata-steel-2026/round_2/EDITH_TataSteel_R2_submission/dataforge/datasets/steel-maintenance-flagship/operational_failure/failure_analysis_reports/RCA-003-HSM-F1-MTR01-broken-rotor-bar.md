# FAILURE ANALYSIS REPORT

**Report Number:** RCA-003
**Date of Report:** 2026-02-08
**Classification:** SYNTHETIC — physics-grounded, no proprietary Tata Steel data
**Prepared by:** Reliability Engineering, TATA_JSR Hot Rolling Division / Electrical Maintenance
**Safety Class:** P3

---

## 1. Asset Identification

| Field | Value |
|---|---|
| Asset ID | HSM.F1.MTR01 |
| Equipment Class | large_induction_motor_vfd |
| Description | Hot Strip Mill F1 main drive AC induction motor, VFD-fed (MV) |
| Location | HOT_ROLLING / FINISHING_STAND_1 / MAIN_MOTOR |
| Manufacturer | ABB |
| Model | AMI 630 MV (VFD: ACS6000) |
| Rated Power | 6,000 kW |
| Rated Speed | 990 rpm |
| Bearing DE | SKF 6326 |
| Bearing NDE | SKF 6226 |
| Insulation Class | F |
| Criticality | 1 (highest) |
| Installation Date | 2018-06-20 |
| Last Overhaul | 2024-02-10 |

---

## 2. Failure Summary

| Field | Value |
|---|---|
| Scenario ID | SCN-039 |
| Failure Mode | broken_rotor_bar |
| Fault Codes | MCSA-RBAR-ALARM |
| Date of Detection | 2026-02-05 |
| Date of Planned Swap | 2026-02-08 |
| Warning-to-Swap Interval | ~2–4 weeks |
| Planned Downtime | 10 hours (motor swap) |
| Unplanned Downtime | 0 hours (detected early, planned swap) |
| Total Cost Impact | INR 8,350,000 (~USD 100,000) |

---

## 3. Symptom Timeline

### Weeks 0–3: Healthy Baseline
Motor operating normally under routine rolling loads. No VFD faults. Sensor readings:
- `JSR.HR.STD1.MTR01.MCSA.RBAR.SB`: −58 dBc (normal −70 to −50 dBc per IEEE 1415-2006)
- `JSR.HR.STD1.MTR01.WIND.TEMP`: 118 °C (normal 80–130 °C, IEC 60034-1 Class F)
- `JSR.HR.STD1.MTR01.VIB.DE.RMS`: 1.8 mm/s (normal 0.5–2.3 mm/s)
- `JSR.HR.STD1.MTR01.CURR.IMBAL`: 0.6% (normal 0–1%)
- `JSR.HR.STD1.MTR01.VIB.2XF1`: 0.3 mm/s (normal 0–0.5 mm/s)

### Weeks 3–4: Stage 1 — MCSA Sideband Warning
- Motor Current Signature Analysis (MCSA) rotor-bar sideband feature (`JSR.HR.STD1.MTR01.MCSA.RBAR.SB`) rises from −58 dBc to −46 dBc, approaching the warning threshold of −45 dBc.
- The sideband appears at frequencies (1 ± 2ks)f₁ where k = 1 and s = slip, consistent with rotor asymmetry from one or more fractured rotor bars. At this stage the bar fracture is partial — the bar still carries some current but the magnetic flux asymmetry is measurable.
- No vibration change yet; mechanical symptoms lag electromagnetic by 1–3 weeks.
- Maintenance Engineering notified; MCSA measurement scheduled at next shift change for confirmation under steady load (MCSA accuracy requires load > 60% rated to distinguish rotor-bar sidebands from load oscillation).

### Weeks 4–6: Stage 2 — Alarm Level, Vibration Rises
- `JSR.HR.STD1.MTR01.MCSA.RBAR.SB` reaches −34 dBc, exceeding the alarm threshold of −35 dBc.
- `JSR.HR.STD1.MTR01.VIB.DE.RMS` rises from 1.8 mm/s to 4.8 mm/s, crossing the ISO 20816-1 Group 2 warning threshold of 4.5 mm/s. The vibration increase is due to the asymmetric rotor magnetic pull at 2× slip frequency creating a small once-per-rev radial force component.
- Stator winding temperature `JSR.HR.STD1.MTR01.WIND.TEMP` shows minor increase: 118 → 129 °C (still within Class F normal band). The negative-sequence current component from the broken bar circulates in healthy bars, causing marginal additional copper losses.
- Fault code MCSA-RBAR-ALARM generated; motor swap decision made.

### Decision and Planned Outage
Motor swap window scheduled for next planned roll change. Insurance spare `MTR-MV-6000` retrieved from spare motor store. Planned 10-hour swap executed 2026-02-08 (RCA date).

---

## 4. Sensor Evidence Summary

| Tag | Normal Value | Defect Value | Threshold Crossed |
|---|---|---|---|
| JSR.HR.STD1.MTR01.MCSA.RBAR.SB | −58 dBc | −34 dBc | Alarm (−35 dBc) |
| JSR.HR.STD1.MTR01.VIB.DE.RMS | 1.8 mm/s | 4.8 mm/s | Warning (4.5 mm/s) |
| JSR.HR.STD1.MTR01.WIND.TEMP | 118 °C | 129 °C | Within normal (alarm 155 °C) |
| JSR.HR.STD1.MTR01.CURR.IMBAL | 0.6% | 1.3% | Within normal (alarm 5%) |
| JSR.HR.STD1.MTR01.VIB.2XF1 | 0.3 mm/s | 0.8 mm/s | Warning (1.0 mm/s) |

---

## 5. Root Cause Analysis

### Primary Root Cause
**Rotor bar fracture from repeated high-torque starts and thermal cycling.** The ABB AMI 630 rotor cage uses cast aluminium bars. Over the 24-month period since last overhaul (2024-02-10), the motor experienced an estimated 3,400 start cycles (3-per-shift × 3 shifts × 365 days). Each start cycle induces thermal expansion of the bar material at the end-ring joint (the highest-stress location), followed by contraction at rest. Thermal fatigue propagates micro-cracks at the bar-to-end-ring brazed joint over time.

A contributing factor was 6 high-inertia starts documented in the preceding 4-month period during strip-cobble recovery sequences, where the VFD had to re-accelerate the fully-loaded roll stand from near-zero speed. Each event generated a transient bar current approximately 150% of rated locked-rotor current, amplifying the thermal fatigue damage per start.

The fracture is identified as affecting one bar by the MCSA sideband pattern: the sideband at (1 − 2s)f₁ (lower sideband) was 3 dB higher than the upper sideband (1 + 2s)f₁, consistent with a single broken bar rather than inter-bar resistance increase (which produces a more symmetric sideband pattern, per IEEE 1415-2006 Section 5).

### Why Not Stator or Insulation Failure?
- Polarisation index (offline measurement at last overhaul): PI = 3.2, well above the 2.0 warning threshold (IEEE 43-2013). Insulation is not degraded.
- Phase current imbalance remained at 1.3%, well below the 5% alarm threshold (NEMA MG1-2021 12.45), ruling out stator winding turn-short.

---

## 6. Corrective Actions Taken

1. **MCSA confirmation** — At steady load (85% rated) over a 60-second window per IEEE 1415-2006; sideband confirmed at −34 dBc. Rotor bar fracture diagnosis confirmed before committing to motor swap.
2. **Production planning** — Motor swap scheduled to align with next planned roll change to minimise additional unplanned downtime. Operations confirmed current production campaign could continue for 4 additional days without risk of catastrophic failure (management of risk based on sideband level and vibration trend).
3. **Motor swap execution:**
   - Insurance spare `MTR-MV-6000` (ABB AMI 630, 6,000 kW) retrieved from store.
   - Phase rotation confirmed with phasing meter before coupling.
   - LOTO on MV switchgear (6.6 kV isolation).
   - Motor change-out via gantry crane, 10-hour window.
   - Flexible coupling half-shim alignment: residual offset < 0.05 mm per laser alignment.
   - VFD `ACS6000` auto-commission: motor nameplate parameters loaded, encoder offset calibrated.
4. **Failed motor dispatch** — Failed motor sent to ABB service centre for rotor bar inspection and repair (consumable `RWND-KIT-MV` reserved). Expected return to spare stock: 8 weeks.
5. **AEGIS ring inspection** — VFD-drive shaft grounding ring (AEGIS) inspected; carbon fibre brushes found 40% worn. Replaced as a precautionary measure (VFD-induced shaft voltage bearing current is a secondary failure risk per IEEE 1415-2006).

---

## 7. Parts Consumed

| Part ID | Description | Qty | Unit Cost (USD) | Notes |
|---|---|---|---|---|
| MTR-MV-6000 | MV insurance spare motor 6,000 kW | 1 | — | Reusable rotating capital asset; not expensed per event |
| RWND-KIT-MV | MV rewind materials (reserved for failed motor repair) | 1 | 15,000 | Expensed against repair work order |

**Parts expensed this event: USD 15,000**
Remainder of USD 100,000 event cost: labour (crane + alignment + commissioning), MV switching operations, production delay during swap.

---

## 8. Downtime

| Type | Hours |
|---|---|
| Unplanned | 0 |
| Planned (motor swap) | 10 |
| **Total** | **10** |

This is a best-case outcome attributable to early MCSA detection. Without MCSA monitoring, a broken-rotor-bar failure typically progresses to catastrophic winding failure within 2–8 weeks of the alarm-level sideband, requiring 4–8 weeks for rewind versus 10 hours for a planned motor swap.

---

## 9. Recurrence Prevention

1. **MCSA warning-to-action procedure.** Formalise: MCSA sideband ≥ −45 dBc (warning) = schedule motor swap within 15 working days; ≥ −35 dBc (alarm) = swap at next production window ≤ 5 days. This event succeeded because the procedure was followed; it should be codified in CMMS work instructions.
2. **High-inertia start logging.** Link VFD torque records to the PdM system; flag any start current > 130% rated for MCSA follow-up within 5 days. The 6 cobble-recovery starts were identified retrospectively; real-time flagging would have triggered earlier inspection.
3. **Maintain insurance spare readiness.** MTR-MV-6000 must be returned to store within 8 weeks of removal. Add CMMS PM order for annual stator insulation PI check on the spare motor.
4. **AEGIS ring PM interval.** Based on brush wear found (40% at 24 months), set AEGIS ring inspection interval to 18 months for this motor class.
5. **Thermal start cycle count.** Implement start-count OEM limit tracking in CMMS (ABB AMI series: 3,000 full-voltage-equivalent thermal starts between inspections). Alert at 80% of limit.

---

*Standards cited: IEEE 1415-2006 (MCSA for rotor fault detection), IEEE 43-2013 (motor insulation — PI), NEMA MG1-2021 (phase current imbalance), IEC 60034-1 (insulation class). Equipment: ABB AMI 630 MV, VFD ACS6000.*
