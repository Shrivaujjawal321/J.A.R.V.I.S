# Equipment Manual: Walking-Beam Reheating Furnace (Soak Zone)
**Asset ID:** RHF.ZONE.SOAK
**Equipment Class:** reheating_furnace
**Document:** MAN-010 | Rev 1.0 | Site: TATA_JSR (Synthetic Reference)
**Standard References:** EN 746-2:2010, EIGA (gas safety), ISO 14001 (environmental)

> **DISCLAIMER — SYNTHETIC DOCUMENT.** All numeric values are representative industry estimates grounded in cited standards. No proprietary Tata Steel data is used.

---

## 1. Equipment Description

RHF.ZONE.SOAK is the soak zone (Zone 3) of the walking-beam reheating furnace serving the hot strip mill. Slabs enter cold (~ambient to 200 °C) and exit at ~1150–1250 °C, uniformly heated through the full cross-section, before passing to the roughing stands.

The soak zone is the final zone before discharge; it ensures temperature uniformity and homogenisation of the steel microstructure. The walking-beam mechanism lifts and walks slabs along the furnace at a controlled rate matched to the mill throughput.

**Manufacturer:** Tenova
**Model:** Walking-beam WB
**Process Stage:** Reheating (upstream of hot rolling)
**Criticality:** 2
**Installation Date:** 2017-05-15
**Last Overhaul:** 2023-12-08

**Combustion system:**
- Fuel: Mixed gas (typically blast furnace gas + coke oven gas mixture; or natural gas)
- Burner arrangement: Top/bottom fired (regenerative or recuperative burners typical in soak zone)
- Air-fuel control: Ratio controller with flue gas O2 trim
- Safety system: EN 746-2 compliant — automatic fuel cutoff on flame failure; purge before re-light; gas detection

---

## 2. Technical Specifications

| Parameter | Value |
|-----------|-------|
| Furnace type | Walking beam (bottom- and top-fired) |
| Fuel type | Mixed blast furnace + coke oven gas (or natural gas) |
| Soak zone temperature target | 1180–1280 °C |
| Maximum zone temperature | 1330 °C (alarm) |
| Slab discharge temperature | 1150–1250 °C (grade-dependent) |
| Refractory lining | High-alumina brick (>90% Al₂O₃) + ceramic fibre backup |
| Shell external temperature (normal) | 80–120 °C |
| Shell temperature alarm (burnout indicator) | 250 °C |
| Flue gas O₂ target | 1.5–3.5% (slightly oxidising atmosphere) |
| Combustion air preheat | Regenerative (waste-heat recovery) |
| Walking beam cycle | Typically 30–120 s per step (matched to mill demand) |

---

## 3. Sensor Instrumentation

| Tag | Quantity | Unit | Normal Range | Warning | Alarm | Standard |
|-----|----------|------|-------------|---------|-------|----------|
| JSR.RHF.Z3.SHELL.IR | Shell surface temperature (IR scan) | degC | 80 – 120 | 180 | 250 | Refractory practice (unverified) |
| JSR.RHF.Z3.FLAME.SIG | Flame scanner signal | % | 90 – 100 | 70 | 40 | EN 746-2:2010 §5.4 |
| JSR.RHF.Z3.FLUE.O2 | Flue gas O₂ | % | 1.5 – 3.5 | high: 5.0; low: 1.0 | high: 6.0 | EN 746-2 / EIGA |
| JSR.RHF.Z3.ZONE.TEMP | Zone temperature | degC | 1180 – 1280 | 1300 | 1330 | Type S thermocouple |

**FLAME.SIG note:** Lower signal = worse. Alarm at <40% triggers automatic fuel cutoff (EN 746-2 §5.4 requirement). Warning at <70% indicates unstable flame (burner fouling or gas supply issue).

**FLUE.O2 note:** Both high and low deviations are alarms. Low O₂ (<1.0% warning) = sub-stoichiometric combustion → CO formation (toxic + furnace atmosphere explosion risk). High O₂ (>6.0%) = too lean → energy waste + excessive oxidation of steel surface (scale loss).

**SHELL.IR note:** Shell hot-spot above 250 °C indicates refractory failure/burnout at that location. Left untreated: shell buckle, water ingress to refractory, catastrophic failure.

---

## 4. Operating Limits

| Condition | Limit | Action |
|-----------|-------|--------|
| ZONE.TEMP | >1300 °C (warning) | Reduce burner firing rate; check thermocouple accuracy |
| ZONE.TEMP | >1330 °C (alarm) | Emergency firing reduction; slab burn risk |
| SHELL.IR | >180 °C (warning) | Mark area; schedule refractory inspection at next furnace stop |
| SHELL.IR | >250 °C (alarm) | Stop furnace; refractory burnout at that location |
| FLAME.SIG | <70% (warning) | Inspect burner nozzle and flame scanner; clean |
| FLAME.SIG | <40% (alarm) | EN 746-2: automatic fuel cutoff; purge before re-light |
| FLUE.O2 | <1.0% (warning) | Risk of CO and furnace explosion; increase air supply |
| FLUE.O2 | >5.0% (warning) | Lean: increase fuel or check burner for blockage |
| FLUE.O2 | >6.0% (alarm) | Significant misfire; investigate |

---

## 5. Known Failure Modes

### 5.1 Burner Failure (Fuel-Side) — Primary Mode

**Root Cause:** Burner nozzle fouling from scale, condensate, or combustion deposits; gas supply pressure fluctuation; flame scanner contaminated with soot/dust → false flame-out signal.

**Degradation Timeline:**
- Healthy: FLAME.SIG = 96%; FLUE.O2 = 2.4%; ZONE.TEMP = 1240 °C
- Warning: FLAME.SIG 96 → 70% (flickering); FLUE.O2 rising (incomplete combustion)
- Alarm: FLAME.SIG <40% → automatic fuel cutoff (EN 746-2); FLUE.O2 = 5.8% (unburnt air)
- Failure: Flambe-out + unburnt fuel in furnace chamber

**EN 746-2 Procedure after flame-out:**
1. Automatic fuel cutoff (hardwired safety relay, not software).
2. Mandatory furnace purge (5+ air changes of furnace volume before re-light).
3. Re-light procedure per burner management system (BMS).

**Sensor Signature:**
- FLAME.SIG: 96 → 38% (alarm — lower is worse)
- FLUE.O2: 2.4 → 5.8% (alarm — excess air after fuel cutoff)

**Fault Codes:** FLAME-FAIL-CUTOFF, FLUE-O2-HIGH
**Planned TTR:** 2 hours | **Unplanned TTR:** 6 hours | **Cost Impact:** USD 12,000
**Safety Class:** P2

### 5.2 Refractory Hot-Spot / Burnout

**Root Cause:** Refractory lining erosion by high-temperature gas streams; mechanical impact from cobble through furnace (rare); thermal cycling fatigue at corners/joints.

**Signature:** SHELL.IR identifies local hot spot → rising progressively from 120 → 180 → 250 °C. May be accompanied by discoloration or deformation of steel shell.

**Consequence:** If burnout progresses to water-cooled shell elements, water can enter refractory → steam explosion risk.

**Action:** At >180 °C: plan repair at next scheduled furnace stop; gunning refractory (REFRAC-CAST-01). At >250 °C: stop furnace for emergency refractory repair.

### 5.3 Combustion Imbalance / Excess Air

**Root Cause:** Air-to-fuel ratio drift from control valve wear, fuel gas calorific value variation (BF gas varies with furnace operation), or O₂ analyser calibration drift.

**Signature:** FLUE.O2 rising toward >5% (warning) with ZONE.TEMP dropping (excess air cools furnace); scale on slab surface increased (oxidising atmosphere).

**Action:** Re-trim air-to-fuel ratio via O₂ controller; recalibrate O₂ analyser; check fuel gas calorific value.

---

## 6. Preventive Maintenance Schedule

| Task | Interval | Method | Notes |
|------|----------|--------|-------|
| Flame scanner signal monitoring | Continuous 10 Hz | SCADA | Auto-trip on <40% (EN 746-2) |
| Flue gas O₂ monitoring | Continuous 1 Hz | In-situ O₂ analyser | Calibrate monthly with reference gas |
| Zone temperature monitoring | Continuous 1 Hz | Type S thermocouple | Replace failed TCs promptly (redundancy) |
| Shell IR survey | Monthly | Portable IR camera walk-down | Document all readings; track trends |
| Burner nozzle inspection + clean | Quarterly or on flame-signal warning | Planned shutdown slot | Replace (BURN-NOZ-01; stock 4) |
| Flame scanner clean + calibration | Quarterly | Planned shutdown | Replace (FLAME-SCAN-01; stock 2) |
| Flue gas O₂ analyser calibration | Monthly | Reference gas (N₂ + known O₂ mix) | Zero and span check |
| Refractory inspection (visual + hammer test) | Annually (furnace cold stop) | Visual + tap test | Gun repair hot spots; document thickness |
| Refractory gunning repair (REFRAC-CAST-01) | On hot-spot alarm or annual inspection | Hot or cold gunning depending on severity | Plan during planned maintenance shutdown |
| Gas valve and train inspection (EN 746-2) | Annually | Specialist combustion engineer | SIL-rated safety valves; proof test |
| Walking beam drive inspection | 6-monthly | Visual + vibration | Walking beam is mechanical critical |
| Water-cooling circuit check (if applicable) | Monthly | Flow and temperature monitoring | Cooled skid pipes/beam underside |

---

## 7. Troubleshooting

### T1 — Flame Failure / Automatic Fuel Cutoff (FLAME.SIG < 40%)

**This is an EN 746-2 safety system activation — mandatory procedure:**

1. Confirm fuel cutoff is active (gas isolation valve closed — check SCADA status, not just the alarm).
2. **Do NOT attempt immediate re-light.** Mandatory furnace purge first:
   - Open combustion air dampers fully; run purge air for a minimum of 5 furnace volume changes (BMS timer controls this automatically; manual override is prohibited without gas-safety engineer present).
3. Investigate cause before re-light: inspect burner nozzle (fouled? eroded?); inspect flame scanner (clean of soot?); check gas supply pressure.
4. Clean/replace burner nozzle (BURN-NOZ-01) and/or flame scanner (FLAME-SCAN-01) as required.
5. Re-tune fuel-air ratio after nozzle replacement.
6. Re-light via BMS sequence; confirm FLAME.SIG >90% before full firing rate.

### T2 — FLUE.O2 < 1.0% (Rich Mixture Warning)

1. Immediate risk: CO formation and explosive atmosphere in furnace chamber.
2. Reduce fuel supply; increase air proportionally.
3. Check O₂ analyser reading against secondary measurement (portable analyser in stack).
4. If O₂ cannot be recovered above 1.5%: reduce firing rate significantly; notify gas-safety engineer.
5. Do NOT re-enter furnace chamber with any residual CO-containing atmosphere — verify with gas detector.

### T3 — SHELL.IR > 180 °C (Refractory Warning)

1. Document location (zone + position) and current temperature.
2. At next planned furnace stop: inspect refractory from inside.
3. Prepare gunning mix (REFRAC-CAST-01; stock 10 bags).
4. If location is at a water-cooled element: increase urgency; steam explosion risk if refractory perforation.
5. Repair: clean loose refractory; apply gunning mix; allow to cure; re-inspect before firing.

---

## 8. Corrective Maintenance — Burner Nozzle Replacement

**Required Spares:**
| Part ID | Description | Stock | Lead Time |
|---------|-------------|-------|-----------|
| BURN-NOZ-01 | Burner nozzle assembly | 4 | 4 weeks |
| FLAME-SCAN-01 | Flame scanner (UV/IR) | 2 | 3 weeks |
| REFRAC-CAST-01 | Refractory castable / gunning mix | 10 bags | 2 weeks |

**Planned TTR:** 2 hours (nozzle + scanner change during planned stop)
**Unplanned TTR:** 6 hours (includes purge time + troubleshooting)
**Safety Class:** P2

---

## 9. Safety

- **Gas explosion risk:** This is the primary hazard. NEVER bypass the BMS sequence or attempt manual re-light without full purge. A furnace with unburnt gas mixture can detonate.
- **CO poisoning:** BF gas is typically 20–28% CO; coke oven gas contains H₂S. Always gas-test (CO + H₂S) before entering any furnace, duct, or flue area. CO >25 ppm = STEL; >100 ppm = immediately evacuate.
- **High-temperature burns:** Furnace interior at 1200–1330 °C. Access restricted to furnace cold (below 50 °C confirmed by thermocouple) plus forced ventilation. Hot-entry procedures (above 50 °C) require specialist PPE and permit.
- **Refractory dust (silica):** Damaged refractory creates respirable silica dust (crystalline silica, IARC Group 1 carcinogen). P3 respirator (FFP3) minimum during any refractory repair; wet-gunning preferred to dry-spray.
- **Walking beam mechanical hazard:** Walking beam mechanism moves cyclically; absolutely no personnel on furnace floor during beam operation. Full mechanical LOTO on beam drive before entry.
- **Thermal explosion hazard (water-cooled elements):** If water-cooled skids or beams have coolant flow failure while furnace is hot: risk of sudden steam explosion. Continuously monitor cooling water flow/temperature; interlock with furnace trip.
