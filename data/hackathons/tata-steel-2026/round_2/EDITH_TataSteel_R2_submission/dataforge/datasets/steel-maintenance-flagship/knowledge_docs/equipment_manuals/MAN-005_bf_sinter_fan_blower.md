# Equipment Manual: Blast Furnace Turbo-Blower / Sinter Fan
**Asset IDs:** BF.BLW.FAN01 (BF Turbo-Blower) | SP.SINT.FAN01 (Sinter Plant Main Exhaust Fan)
**Equipment Class:** bf_sinter_fan_blower
**Document:** MAN-005 | Rev 1.0 | Site: TATA_JSR (Synthetic Reference)
**Standard References:** API 670:2014, ISO 10816-3:2009, ISO 15243:2017, API 617

> **DISCLAIMER — SYNTHETIC DOCUMENT.** All numeric values are representative industry estimates grounded in the cited standards. No proprietary Tata Steel data is used.

---

## 1. Equipment Description

### 1.1 BF.BLW.FAN01 — Blast Furnace Turbo-Blower

The BF turbo-blower supplies cold blast air to the blast furnace at high pressure and volume. It is the single most critical rotating machine in the ironmaking process; a trip causes an immediate blast furnace production halt at a cost estimated at $500k/hour.

**Manufacturer:** Siemens / MAN
**Model:** Axial blast machine
**Rated Power:** 28,000 kW
**Rated Speed:** 3,600 RPM
**Process Stage:** Iron making (blast furnace)
**Criticality:** 1

### 1.2 SP.SINT.FAN01 — Sinter Plant Main Exhaust Fan

Large radial process fan handling high-temperature, dust-laden exhaust gas from the sinter bed. Subject to severe blade erosion from sintered dust particles.

**Manufacturer:** TLT-Turbo
**Model:** Radial process fan
**Rated Power:** 4,500 kW
**Rated Speed:** 990 RPM
**Process Stage:** Sintering
**Criticality:** 1

---

## 2. Technical Specifications

### BF.BLW.FAN01

| Parameter | Value |
|-----------|-------|
| Machine type | Axial-flow turbo-blower (multi-stage) |
| Bearing type | Tilting-pad journal bearings (hydrodynamic), thrust bearing (Babbitt pads) |
| Lube system | Forced-lube, API 614 grade |
| Shaft monitoring | Bently Nevada proximity probes (API 670:2014) |
| Surge protection | Anti-surge valve (ASV) + control system (surge line + 8% margin) |
| Inlet guide vanes (IGVs) | Variable; used for flow control |
| Normal shaft displacement | 10–50 µm pk-pk |
| API 670 alarm displacement | 127 µm pk-pk (Table 1) |

### SP.SINT.FAN01

| Parameter | Value |
|-----------|-------|
| Machine type | Radial centrifugal fan (backward-curved blades) |
| Blade material | Wear-resistant cast steel or hard-surfaced |
| Bearing type | Rolling element (large spherical roller) |
| Lube system | Circulating oil or grease |
| Balance requirement | ISO G6.3 or better after blade erosion repair |

---

## 3. Sensor Instrumentation

### BF.BLW.FAN01

| Tag | Quantity | Unit | Normal Range | Warning | Alarm | Standard |
|-----|----------|------|-------------|---------|-------|----------|
| JSR.BF.BLW.FAN01.VIB.1X | Vibration 1× RMS | mm/s | 1.0 – 2.3 | 4.5 | 7.1 | ISO 10816-3:2009 Group 3 |
| JSR.BF.BLW.FAN01.SHAFT.DISP | Shaft displacement pk-pk | µm | 10 – 50 | 80 | 127 | API 670:2014 Table 1 |
| JSR.BF.BLW.FAN01.TEMP.BRG | Bearing outer-ring temperature | degC | 45 – 65 | 80 | 95 | ISO 15243:2017 §8 |
| JSR.BF.BLW.FAN01.PRES.OSC | Discharge pressure oscillation | % | 0 – 2 | 5 | 8 | API 670 surge (unverified) |
| JSR.BF.BLW.FAN01.THRUST.TEMP | Thrust bearing temperature | degC | 50 – 75 | 90 | 105 | API 617 class (unverified) |

**SHAFT.DISP alarm significance:** API 670:2014 specifies shutdown at 127 µm pk-pk for a machine of this class. Alarm at 80 µm allows protective action before hardware damage.

**PRES.OSC significance:** Discharge pressure oscillation >8% indicates surge condition — potentially catastrophic within seconds.

### SP.SINT.FAN01

| Tag | Quantity | Unit | Normal Range | Warning | Alarm | Standard |
|-----|----------|------|-------------|---------|-------|----------|
| JSR.SP.FAN01.VIB.1X | Vibration 1× RMS | mm/s | 1.0 – 2.3 | 4.5 | 7.1 | ISO 10816-3:2009 Group 3 |
| JSR.SP.FAN01.TEMP.BRG | Bearing outer-ring temperature | degC | 45 – 65 | 80 | 95 | ISO 15243:2017 §8 |
| JSR.SP.FAN01.VIB.AXIAL | Axial 2× ratio | ratio | 0.0 – 0.3 | 0.4 | 0.7 | Mobius (unverified) |
| JSR.SP.FAN01.DP.DUCT | Inlet-outlet differential pressure | kPa | 8 – 14 | 18 | 22 | Performance degradation |

**VIB.AXIAL note:** Elevated axial vibration at 2× shaft frequency (misalignment signature). Ratio = axial / radial at 2×.

---

## 4. Operating Limits

### BF.BLW.FAN01

| Condition | Limit | Action |
|-----------|-------|--------|
| PRES.OSC | >5% (warning) | Surge margin narrowing; verify ASV position; increase flow |
| PRES.OSC | >8% (alarm) | Surge occurring; verify ASV auto-opened immediately |
| PRES.OSC | >8%, ASV open, still surging | Trip machine immediately; do NOT restart until cause found |
| SHAFT.DISP | >80 µm (warning) | Check balance; inspect bearings; prepare for forced stop |
| SHAFT.DISP | >127 µm (alarm) | API 670 shutdown trip; machine must not run |
| TEMP.BRG | >95 °C (alarm) | Stop; inspect journal bearing pads |
| THRUST.TEMP | >105 °C (alarm) | Stop; thrust bearing failure imminent |

### SP.SINT.FAN01

| Condition | Limit | Action |
|-----------|-------|--------|
| VIB.1X | >4.5 mm/s (warning) | Suspect blade erosion/deposit; plan balance inspection |
| VIB.1X | >7.1 mm/s (alarm) | Stop fan; inspect blades |
| VIB.AXIAL ratio | >0.4 (warning) | Inspect coupling alignment |
| VIB.AXIAL ratio | >0.7 (alarm) | Stop; realign before restart |
| DP.DUCT | >18 kPa (warning) | Fan performance degraded; inspect blades and ductwork |

---

## 5. Known Failure Modes

### 5.1 Compressor Surge (BF.BLW.FAN01) — Highest Priority

**Physics:** Surge occurs when the operating point (pressure vs. flow) crosses to the left of the surge line on the compressor map. Flow reversal occurs in milliseconds; pressure oscillates violently.

**Triggers:**
- Downstream valve slam (sudden throttling)
- Inlet filter fouling (reduced volumetric flow)
- BF hanging (sudden blast volume drop)
- Control system malfunction (IGV over-close)

**Degradation Timeline:**
- Surge onset: ASV cycles; pressure oscillation 5% → 8% (alarm); shaft displacement increases
- Sustained surge: 2–3 cycles → blade/IGV damage; bearing loads exceed design; white-metal wiping
- Catastrophic: Shaft displacement >127 µm; impeller clash; catastrophic failure in seconds

**Sensor Signature:**
- PRES.OSC: 1% (normal) → 9% (alarm)
- SHAFT.DISP: 35 µm (normal) → 95 µm (alarm)

**Fault Codes:** SURGE-ALARM, ASV-CYCLING
**Cost Impact:** INR 500,000,000 / USD 6,000,000 (range $4M–$8M+, 96 h unplanned)
**Safety Class:** P1

### 5.2 Blade Erosion / Deposit Build-up (Both)

**Root Cause (Sinter fan SP.SINT.FAN01):** Sintered dust particles in gas stream erode blade leading edges. After campaign, material loss causes mass imbalance → 1× vibration growth.

**Root Cause (BF.BLW.FAN01):** Scale or particulate ingestion despite inlet filters; blade deposit build-up causing asymmetric mass shift → 1× imbalance.

**Signature:** VIB.1X gradually rising over weeks/months; AE shows no impact signature (erosion is smooth). For SP.SINT.FAN01, DP.DUCT rising as blade profile degrades fan curve.

### 5.3 Mass Imbalance / Deposit Shedding (Both)

**Root Cause:** Sudden shedding of adhered deposit (thermal or mechanical) causing instantaneous step-change in rotor balance. VIB.1X jumps suddenly (not gradual).

**Signature:** Step-change increase in VIB.1X (e.g., 2.3 → 6+ mm/s in one data point).

**Action:** Stop; inspect blades for deposit/erosion; trim balance or full-speed balance. Use BAL-WT-01 balancing weights.

### 5.4 Journal Bearing Failure (BF.BLW.FAN01)

**Root Cause:** Tilting-pad journal bearing white-metal wipe from lube starvation, contamination, or shock load (post-surge).

**Signature:** TEMP.BRG spike; SHAFT.DISP increase; SHAFT.DISP may show orbit change (circular → elliptical) on proximity probes.

### 5.5 Shaft Bow / Misalignment (SP.SINT.FAN01)

**Root Cause:** Thermal bow from uneven cooling; misalignment between fan and drive motor after maintenance.

**Signature:** VIB.AXIAL ratio elevated; 2× shaft frequency dominant; 1× also present.

### 5.6 Bearing Overheating (Both)

**Root Cause (BF.BLW.FAN01):** Lube oil failure to tilting-pad bearing; post-surge shock; contamination.
**Root Cause (SP.SINT.FAN01):** Rolling-element bearing: grease starvation, overcrowding, contamination from dust ingress through seals.

---

## 6. Preventive Maintenance Schedule

| Task | Interval | Equipment | Notes |
|------|----------|-----------|-------|
| Continuous vibration + displacement monitoring | Continuous | Both | Bently Nevada (BF); standard mounts (Sinter) |
| Anti-surge system functional test | Monthly | BF.BLW.FAN01 | Verify ASV stroke + control response |
| Inlet filter differential pressure check | Weekly | BF.BLW.FAN01 | High ΔP = approaching surge |
| Lube oil sampling (viscosity, contamination) | Monthly | BF.BLW.FAN01 | API 614-grade oil |
| Journal bearing pad clearance measurement | At planned shutdown | BF.BLW.FAN01 | Compare to OEM tolerance |
| Thrust bearing pad inspection | At planned shutdown | BF.BLW.FAN01 | Babbitt condition; clearance |
| Blade inspection + clean | 3-monthly or VIB alarm | SP.SINT.FAN01 | Remove build-up; measure erosion |
| Dynamic balance check | After blade clean or deposit shed | Both | ISO G6.3 target post-balance |
| Coupling alignment | After any maintenance | Both | Laser alignment <0.05 mm |
| Bearing re-greasing | Per OEM schedule | SP.SINT.FAN01 | Sinter fan rolling bearings |

---

## 7. Troubleshooting

### T1 — Compressor Surge (PRES.OSC > 5%)

1. **Immediately verify:** ASV (anti-surge valve) auto-position — should open on surge detection.
2. If ASV is open and surge continues beyond 2–3 cycles: **trip machine immediately** — continued surging causes catastrophic damage in <30 seconds.
3. Do NOT restart until root cause is identified and corrected.
4. Investigate: Was the BF hanging? Was a downstream valve slammed? Was the inlet filter overloaded?
5. Borescope IGVs and impeller blades for damage; run ferrography on lube oil to check for white-metal particles from bearings.
6. Calibrate anti-surge control line vs. OEM performance map before restart.
7. Notify ironmaking process team — BF blast pressure management needed.

### T2 — VIB.1X > 4.5 mm/s (Sinter Fan, Warning)

1. Pull spectrum — confirm 1× dominant (imbalance) vs. 2× dominant (misalignment).
2. If 1× dominant: suspect blade erosion/deposit; plan inspection at next scheduled stop.
3. If step-change in vibration (deposit shedding): stop fan; inspect blades; balance before restart.
4. Balancing weights (BAL-WT-01) available in stock for in-situ trim balance.

### T3 — TEMP.BRG > 80 °C (Warning, Either)

1. BF.BLW.FAN01: Check lube oil supply pressure and temperature to journal bearings. Inspect oil cooler.
2. SP.SINT.FAN01: Check bearing condition; inspect grease — over-greasing causes churning heat.
3. If approaching 95 °C: plan shutdown; continuing risks white-metal wipe.

### T4 — SHAFT.DISP > 80 µm (BF Blower Warning)

1. Increase monitoring scan rate (if configurable).
2. Notify shift supervisor and process team.
3. Prepare for planned stop within 4 hours.
4. If displacement continues rising toward 127 µm: trip immediately.
5. Post-shutdown: inspect bearing journals for wipe marks; check balance.

---

## 8. Corrective Maintenance

**Required Spares — BF.BLW.FAN01:**
| Part ID | Description | Stock | Lead Time |
|---------|-------------|-------|-----------|
| ASV-VLV-01 | Anti-surge valve | 0 | 12 weeks |
| BRG-JRNL-PAD | Journal bearing pads (OEM tilting-pad) | 1 | 12 weeks |
| BRG-THRUST-PAD | Thrust bearing pads (Babbitt) | 1 | 12 weeks |
| FAN-BLADE-SET | Fan blade set | 0 | 12 weeks |
| BAL-WT-01 | Balancing weights set | 5 | Stock |

**CRITICAL NOTE:** ASV-VLV-01, BRG-JRNL-PAD, BRG-THRUST-PAD, and FAN-BLADE-SET are all on 12-week lead with 0 (blades) or limited stock. Pre-position spares before campaign.

**Unplanned TTR (surge + damage):** 96 hours minimum
**Cost Impact:** USD 6,000,000 (range $4M–$8M)
**Safety Class:** P1

---

## 9. Safety

- **P1 Safety Class:** Any event on BF.BLW.FAN01 is a plant-level production emergency; escalate to maintenance superintendent immediately.
- **Surge event:** Do NOT enter machine hall during active surge — potential shrapnel from blade failure.
- **High-speed rotating machinery:** 3,600 RPM; stored kinetic energy is enormous; coast-down period >5 minutes; do NOT approach shaft until Bently Nevada confirms <10 RPM and shaft locked.
- **Hot bearing oil:** Tilting-pad lube oil at 65 °C; depressurise lube system before opening any connections.
- **Noise levels:** Both machines exceed 110 dB(A) during operation; mandatory double hearing protection in machine hall.
- **Sinter fan gas exposure:** SP.SINT.FAN01 handles CO-containing sinter offgas; CO detector required before opening ductwork; gas-tight gloves and half-face respirator for internal inspection; confined-space permit.
