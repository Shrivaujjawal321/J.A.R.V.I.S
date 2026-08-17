# SOP-12 — Reheating Furnace Burner Service and Refractory Hot-Spot Response
## TATA_JSR Maintenance Standard Operating Procedure

**Document ID:** SOP-12  
**Revision:** 1.0  
**Effective Date:** 2026-06-09  
**Equipment Class:** reheating_furnace  
**Primary Asset Reference:** RHF.ZONE.SOAK  
**Trigger Failure Modes:** burner_failure_fuelside | refractory_hot_spot_burnout | combustion_imbalance_excess_air  
**Spine Scenario Reference:** SCN-046 (RHF.ZONE.SOAK — burner_failure_fuelside; flame signal 38 %, flue O₂ 5.8 %)  
**Standard:** EN 746-2:2010 (industrial thermoprocessing equipment — safety requirements for combustion) | EIGA Doc 44 (combustion safety) | ISO 14224 (failure taxonomy)  
**Safety Class:** P2 (burner failure) | P2 (refractory hot spot)  
**Disclaimer:** SYNTHETIC procedure grounded in research/machinery/12, /16, /18, /19. Values tagged [unverified] are industry estimates. RHF.ZONE.SOAK is a Tenova walking-beam reheating furnace soak zone. Refer to Tenova OEM burner manual and site-specific gas safety procedure for exact fuel-gas handling requirements.

---

## 1. SCOPE

**Part A — Burner Service:** Cleaning, inspection, and replacement of burner nozzle assembly (BURN-NOZ-01) and flame scanner (FLAME-SCAN-01) triggered by flame signal degradation (SCN-046: flame signal dropped from 96 % to 38 %, flue O₂ rose to 5.8 %).

**Part B — Refractory Hot-Spot Response:** IR-detected hot spot on furnace shell (JSR.RHF.Z3.SHELL.IR > 180 °C warning / > 250 °C alarm). Response ranges from reduced-load operation to emergency cool-down for patching, depending on severity.

**Safety note on furnace gas work:** Any work on fuel-gas systems (burner, gas valves, gas train) requires a trained Gas Safety Competent Person following the site Gas Safety Procedure. **Purging is mandatory before any re-light after a flame-out.** Skipping the purge risks an unburnt-gas explosion.

---

## 2. SAFETY / LOTO

### Part A — Burner Service

| Step | Action |
|------|--------|
| S-1 | Close individual burner fuel-gas valve (manual isolation valve at burner group) — lock in CLOSED position with personal lock + danger tag |
| S-2 | Close combustion air fan damper/valve to the affected burner zone |
| S-3 | Verify automatic fuel cutoff has operated (JSR.RHF.Z3.FLAME.SIG < 40 % should have already triggered automatic fuel cutoff per EN 746-2) |
| S-4 | Allow the burner tile and nozzle to cool to < 80 °C before physical contact (confirm with IR thermometer through burner access door) |
| S-5 | Open burner access door (side of furnace) — stand clear of any residual combustion gas or hot gas release on first opening |
| S-6 | Gas test at burner access door opening: use calibrated combustible gas detector before any entry into the furnace zone |
| S-7 | Apply LOTO to the flame scanner electrical supply |

### Part B — Refractory Hot Spot

| Step | Action |
|------|--------|
| S-1 | Reduce furnace temperature setpoint in the affected zone by 50–100 °C |
| S-2 | If shell temperature exceeds 250 °C: initiate controlled cool-down (maximum cooling rate 50 °C/h to prevent thermal shock to adjacent lining and shell) [unverified] |
| S-3 | Close all furnace access doors in the affected zone |
| S-4 | Notify rolling mill production planning: slab throughput will be reduced or stopped |
| S-5 | For emergency shutdown: follow site furnace cool-down procedure (24–48 h to reach ambient) [unverified] |

**PPE Minimum:** Safety helmet, heat-resistant boots, heat-resistant gloves (furnace exterior can be > 200 °C even in "normal" operation), face shield, safety glasses. For confined-space furnace entry (Part B relining): confined-space PPE + gas detector + buddy system. For gas work: fire-resistant overalls, gas detector.

---

## 3. TRIGGER CONDITIONS

| Sensor Tag | Threshold | Action |
|-----------|-----------|--------|
| JSR.RHF.Z3.FLAME.SIG | < 70 % (warning — SCN-046: 96 → 70 %) | Investigate burner; check fuel supply and scanner |
| JSR.RHF.Z3.FLAME.SIG | < 40 % (alarm — automatic fuel cutoff per EN 746-2) | Fuel cutoff auto-operates. Purge required before re-light |
| JSR.RHF.Z3.FLUE.O2 | > 5.0 % (warning — SCN-046: 5.8 %) | Excess air; check burner or air-fuel ratio |
| JSR.RHF.Z3.FLUE.O2 | > 6.0 % (alarm) | Stop zone; investigate combustion system |
| JSR.RHF.Z3.FLUE.O2 | < 1.0 % (warning — low O₂ = rich) | Reduce fuel or increase air; risk of CO formation |
| JSR.RHF.Z3.ZONE.TEMP | > 1 300 °C (warning) | Check temperature control loop |
| JSR.RHF.Z3.ZONE.TEMP | > 1 330 °C (alarm) | Reduce firing; investigate control valve |
| JSR.RHF.Z3.SHELL.IR | > 180 °C (warning) | Plan zone inspection at next furnace stop |
| JSR.RHF.Z3.SHELL.IR | > 250 °C (alarm) | Reduce zone load; plan emergency patch or stop |
| Flame scanner: erratic signal | Any fluctuation not matching fuel state | Clean/replace flame scanner |
| Gas supply pressure: below minimum | Any | Stop zone firing (safety interlock) |

---

## 4. TOOLS AND EQUIPMENT

| Item | Specification |
|------|--------------|
| Combustible gas detector | Calibrated, catalytic bead type; for gas-free verification |
| IR thermometer / thermal camera | Shell hot-spot monitoring |
| Flame scanner test kit | UV/IR signal generator for scanner functional test |
| Torque wrench | Burner nozzle fastening |
| Refractory gunning machine | Compressed-air type for emergency gunite patch |
| Wire brush / stainless tool | Burner nozzle cleaning (carbon deposit removal) |
| Pressure gauge (gas) | Gas supply pressure verification |
| Manometer | Combustion air differential pressure check |
| Combustion analyser (Testo or equiv.) | Flue gas composition tuning after burner service |

---

## 5. SPARES REQUIRED

| Part ID | Description | Stock Qty | Lead Time |
|---------|-------------|-----------|-----------|
| BURN-NOZ-01 | Burner nozzle assembly | 4 on shelf | 4 weeks if OOS |
| FLAME-SCAN-01 | Flame scanner (UV/IR) | 2 on shelf | 3 weeks if OOS |
| REFRAC-CAST-01 | Refractory castable / gunning mix | 10 bags on shelf | 2 weeks if OOS |

---

## 6. NUMBERED PROCEDURE STEPS

### PART A — Burner Nozzle and Flame Scanner Service (SCN-046 reference)

**Immediate Response to Flame-Out / Low Flame Signal**
1. On automatic fuel cutoff (flame signal < 40 %): verify fuel cutoff valve has closed on SCADA. Record the event in CMMS with timestamp, operating conditions (zone temperature, fuel flow, air flow), and flame scanner reading at time of trip.
2. Do NOT attempt immediate re-light. Per EN 746-2: a mandatory purge of the furnace combustion chamber is required before any re-light attempt. Purge duration per site combustion safety procedure (typically 5× combustion air volume at minimum purge flow). [unverified — confirm with Tenova burner safety specification]
3. Apply LOTO per Part A safety steps.
4. Allow burner nozzle tile to cool below 80 °C before opening access door and attempting physical work.

**Burner Nozzle Inspection and Cleaning/Replacement**
5. Open burner access door. Gas test at opening — confirm combustible gas reading is zero before proceeding.
6. Visually inspect burner nozzle (BURN-NOZ-01) through burner access port:
    - Carbon fouling (black deposits): primary cause of poor atomisation and flame instability
    - Physical damage: cracked or eroded nozzle body
    - Gas port blockage: check each gas-injection port with a light
7. Remove burner nozzle assembly per Tenova burner design (typically unscrew or unclip from burner mounting; nozzle is a complete assembly replacement).
8. If nozzle can be cleaned: clean gas ports with stainless wire brush or compressed air. Do not use carbon-steel tools on nozzle ports — metal debris in ports reblocks them immediately. [unverified]
9. If nozzle is cracked, eroded, or ports are enlarged (gas velocity reduced): replace entire assembly (BURN-NOZ-01).
10. Install clean or new nozzle assembly. Torque mounting fasteners per Tenova specification.

**Flame Scanner Service**
11. Disconnect FLAME-SCAN-01 electrical connector (LOTO on scanner supply per S-7).
12. Remove scanner from sighting tube. Clean sighting tube lens with dry lint-free cloth.
13. Inspect scanner lens for fouling — soot, condensate, or refractory dust. Clean lens per manufacturer's specification (dry clean only for UV scanners; damp cloth for IR types — check OEM guidance).
14. Test scanner with flame scanner test kit (portable UV/IR source simulating the flame signal). Scanner should respond to the source. If no response: replace FLAME-SCAN-01.
15. Reinstall scanner. Verify sighting tube is correctly aimed at burner tile centre.
16. Reconnect electrical supply. Test on SCADA — verify scanner signal is present and reading > 90 % with the test source before proceeding to re-light.

**Re-Light Procedure (after purge complete)**
17. Confirm purge timer has completed.
18. Confirm gas supply pressure is within normal range.
19. Re-light via automated ignition sequence (PLC-controlled, EN 746-2 compliant). If automatic ignition fails: do NOT manually re-light with manual torch until checking gas supply condition and scanner operation.
20. Confirm stable flame within 5 seconds of ignition. If no flame in 5 seconds: automatic lockout re-activates. Investigate further before next attempt.
21. After stable flame confirmed: observe flame signal for 5 min. Should stabilise > 90 % (normal range: 90–100 %).
22. Monitor JSR.RHF.Z3.FLUE.O2 over first 15 min post-relight. Target: 1.5–3.5 % (normal range per spine).

**Combustion Tuning (after burner nozzle replacement)**
23. With combustion analyser connected to flue gas sampling point: adjust fuel-air ratio control to achieve target O₂ = 2.4 % (nominal value per SCN-010 healthy signature) with stable flame and zone temperature approaching setpoint.
24. Trim fuel-air ratio controller set points and record final calibrated values in CMMS.

---

### PART B — Refractory Hot Spot Response

**Classification and Immediate Action**
25. On JSR.RHF.Z3.SHELL.IR > 180 °C (warning): reduce zone temperature setpoint by 50 °C. Schedule IR survey of the full furnace shell at next available low-throughput period.
26. Map hot-spot location precisely using IR camera scan of the furnace exterior. Record temperature profile and position in CMMS.
27. On JSR.RHF.Z3.SHELL.IR > 250 °C (alarm): reduce production throughput in the affected zone immediately (reduce slab advance rate or reduce firing).
28. If shell temperature approaches 350 °C (structural concern for carbon-steel shell): initiate emergency cool-down per Tenova furnace cool-down procedure. Notify rolling mill production planning of extended downtime. [unverified — confirm plant-specific structural limit with furnace engineer]

**Emergency Gunite Patch (minor hot spot, furnace at temperature)**
29. Identify hot-spot zone from IR survey. Confirm size < 200 × 200 mm and accessible through furnace side door or inspection port while furnace is at reduced temperature. [unverified]
30. Don appropriate PPE (heat-resistant suit, face shield, breathing apparatus for dusty gunite application).
31. Prepare gunite mix (REFRAC-CAST-01) per manufacturer's mixing procedure. Gunite must be compatible with the furnace atmosphere and hot-face temperature in this zone.
32. Using compressed-air gunning machine: apply gunite to the identified hot spot. Apply in layers not exceeding 50 mm per pass. Allow partial cure between passes. [unverified]
33. Furnace continues at reduced throughput / reduced zone setpoint during patch cure.
34. Monitor JSR.RHF.Z3.SHELL.IR at the patch location over next 4 h. If temperature stabilises below 150 °C: patch is effective.
35. If hot spot is spreading or temperature is still rising despite reduced firing: stop the zone and proceed to major relining (beyond this SOP scope — refer to site Tenova refractory procedure).

**Major Refractory Repair (planned outage, full zone)**
*(Overview only — detailed refractory relining is a specialist contractor scope)*
36. Initiate controlled cool-down per Tenova curve: maximum 50 °C/hour descent. [unverified]
37. Full ambient cool-down: 24–48 h for this soak zone size. [unverified]
38. Scaffold inside zone. Remove damaged refractory by pneumatic demolition.
39. Clean and inspect steel shell for corrosion or distortion.
40. Install refractory anchors (Y-type Inconel for high-temperature zones). [unverified]
41. Cast or brick new lining per Tenova zone-specific design thickness.
42. Dry-out and cure per manufacturer's dry-out curve: **do NOT rush dry-out.** Typical: 24 °C/h ramp to 200 °C; hold 8 h; then 50 °C/h ramp to operating temperature. [unverified] Rapid dry-out causes steam-explosion cracking.
43. Log thermocouple temperatures at each stage of dry-out in CMMS.

---

## 7. ACCEPTANCE CHECKS

| Parameter | Acceptance Criterion | Instrument |
|-----------|---------------------|------------|
| JSR.RHF.Z3.FLAME.SIG (post-service) | 90–100 % (normal range) | SCADA / flame scanner |
| JSR.RHF.Z3.FLUE.O2 (post-service) | 1.5–3.5 % (normal range: target 2.4 %) | Flue gas analyser |
| JSR.RHF.Z3.ZONE.TEMP (steady-state) | 1 180–1 280 °C (normal range) | Zone thermocouple |
| JSR.RHF.Z3.SHELL.IR (post-patch) | < 120 °C (normal range: 80–120 °C) | IR thermometer / thermal camera |
| Automatic flame cutoff test | Activates within 1 s of flame signal < 40 % | Functional test |
| Purge timer | Completes mandatory purge cycle before re-light | PLC timer |
| Re-light success | Stable flame within 5 s of first ignition attempt | SCADA / operator |
| Zone temperature uniformity (after relining) | Heating curves met per metallurgical spec | Type S thermocouple |

---

## 8. TIME ESTIMATE

| Scenario | Planned TTR | Unplanned TTR |
|----------|-------------|---------------|
| Burner nozzle + flame scanner service (SCN-046) | 2 h | 6 h |
| Emergency gunite patch (minor hot spot) | 2–4 h (furnace running) | Same |
| Major zone relining (full shutdown) | 7–21 days | Same |
| Full reheating furnace relining | 4–8 weeks | Same |

*(SCN-046 spine: planned 2 h, unplanned 6 h; cost USD 12 000)*

---

## 9. RECURRENCE PREVENTION

- **Never skip the purge cycle after a flame-out** — skipping the purge for speed is the cause of most furnace combustion explosions. EN 746-2 compliance on purge is non-negotiable.
- **Flame scanner cleaning:** Add flame scanner lens cleaning to every burner nozzle service (30 min extra; prevents the leading cause of false low-signal readings — dirty lens).
- **Fuel supply monitoring:** Install a gas supply pressure trend SCADA tag with alarm — pressure dips below minimum are a root cause of unstable flame before scanner signal degrades.
- **Quarterly IR survey:** Permanently instrument the furnace shell with thermocouple array and IR scan quarterly. Trend-based alerts catch refractory degradation 4–8 weeks before emergency hot spot develops.
- **Dry-out procedure discipline:** Always follow Tenova's dry-out curve after any refractory work. Post it on the furnace control panel and ensure the operator on duty knows they cannot shorten it.
- **BURN-NOZ-01 stock:** Keep minimum 4 units — burner nozzle failures in the soak zone can recur multiple times in a campaign (scale/gas quality dependent). Running to zero stock forces a long unplanned outage.
