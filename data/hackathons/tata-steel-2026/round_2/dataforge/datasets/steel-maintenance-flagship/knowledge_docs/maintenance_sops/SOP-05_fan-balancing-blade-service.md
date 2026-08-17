# SOP-05 — Fan Balancing and Blade Service
## TATA_JSR Maintenance Standard Operating Procedure

**Document ID:** SOP-05  
**Revision:** 1.0  
**Effective Date:** 2026-06-09  
**Equipment Class:** bf_sinter_fan_blower  
**Primary Asset References:** BF.BLW.FAN01 | SP.SINT.FAN01  
**Trigger Failure Modes:** blade_erosion_deposit | mass_imbalance_deposit_shedding | bearing_overheating | shaft_bow_misalignment  
**Spine Scenario References:** SCN-051 (SP.SINT.FAN01 — mass_imbalance_deposit_shedding; VIB.1X 7.1 mm/s — primary scenario, covered by Option A clean + field balance with BAL-WT-01) | SCN-041 (BF.BLW.FAN01 — compressor_surge — surge response section, for context)  
**Standard:** ISO 10816-3:2009 Group 3 | ISO 20816-3:2022 | API 670:2014 (BF.BLW.FAN01) | ISO 21940-11 (balancing)  
**Safety Class:** P1 (BF.BLW.FAN01) | P1 (SP.SINT.FAN01 — fire risk, dust-laden gas)  
**Disclaimer:** SYNTHETIC procedure grounded in research/machinery/05, /15, /18, /19. Values tagged [unverified] are industry estimates. BF.BLW.FAN01 (Siemens/MAN axial blast machine) requires OEM specialist involvement for any rotor or bearing work — this SOP covers routine maintenance and field balancing. SP.SINT.FAN01 (TLT-Turbo radial process fan) is suitable for in-house blade and bearing service.

---

## 1. SCOPE

This SOP covers:
1. **Routine Blade Cleaning and Field Balancing** — triggered by rising 1X vibration (imbalance from dust buildup on blade surfaces, dominant failure mode for SP.SINT.FAN01 in sintering service).
2. **Blade Inspection and Hard-Facing / Replacement** — triggered by step-change in vibration (blade damage, erosion, weld failure) or borescope inspection finding.
3. **Bearing Temperature Response** — initial response to TEMP.BRG alarm while awaiting planned bearing change (refer to SOP-01 for full bearing replacement).

**BF.BLW.FAN01 special note:** This is a 28 000 kW Criticality-1 turbomachine. Any bearing work, rotor inspection, or seal work requires OEM (Siemens/MAN) service engineer involvement. This SOP covers the control-room and shutdown response to surge and bearing alarms, and routine blade deposit cleaning where access is possible.

---

## 2. SAFETY / LOTO

| Step | Action |
|------|--------|
| S-1 | Trip or stop fan at control panel. Initiate controlled run-down (do NOT emergency trip unless imminently unsafe — sudden stop of large fan can cause seal rub and shaft bow) |
| S-2 | For BF.BLW.FAN01: notify blast furnace operator — blower trip interrupts cold blast to furnace. Activate alternative blast source per BF contingency procedure before stopping blower |
| S-3 | Allow fan to reach complete rest. **Large fans (SP.SINT.FAN01 at 4 500 kW, BF.BLW.FAN01 at 28 000 kW) may take 5–15 min to stop after power removal** — verify zero speed on encoder or tachometer before any access |
| S-4 | Isolate motor drive at MCC or switchgear. For BF.BLW.FAN01 (MV drive): HV-LOTO with AEP |
| S-5 | Close and lock inlet isolation damper / inlet guide vanes |
| S-6 | Close and lock discharge isolation valve / damper |
| S-7 | Open casing drains to vent any residual gas pressure (mandatory for BF.BLW.FAN01 — residual blast-furnace gas hazard) |
| S-8 | For SP.SINT.FAN01: gas test inside fan casing before entry — sinter exhaust gas contains CO. Confined-space entry permit required if man-access needed |
| S-9 | Apply all personal locks + danger tags. Post "FAN IN MAINTENANCE — DO NOT START" |

**PPE Minimum:** Safety helmet, steel-toe boots, cut-resistant gloves, safety glasses. For SP.SINT.FAN01 (dust-laden gas service): add respiratory protection (P3 filter), dust coverall. For confined-space casing entry: full confined-space PPE, gas detector, buddy system.

---

## 3. TRIGGER CONDITIONS

| Sensor Tag | Threshold | Action |
|-----------|-----------|--------|
| JSR.SP.FAN01.VIB.1X | > 4.5 mm/s (warning) | Inspect for dust buildup; plan balance check |
| JSR.SP.FAN01.VIB.1X | > 7.1 mm/s (alarm — Zone D) | Stop fan; blade inspection + field balance required |
| JSR.BF.BLW.FAN01.VIB.1X | > 4.5 mm/s (warning) | Notify OEM; increase monitoring frequency to 15 min intervals |
| JSR.BF.BLW.FAN01.VIB.1X | > 7.1 mm/s (alarm) | Trip; OEM callout |
| JSR.BF.BLW.FAN01.SHAFT.DISP | > 80 µm pk-pk (warning) | Notify OEM; prepare for bearing inspection |
| JSR.BF.BLW.FAN01.SHAFT.DISP | > 127 µm pk-pk (API 670 alarm) | Trip immediately (API 670:2014 Table 1 trip criterion) |
| JSR.SP.FAN01.TEMP.BRG | > 80 °C (warning) | Schedule bearing inspection; refer SOP-01 |
| JSR.SP.FAN01.TEMP.BRG | > 95 °C (alarm) | Stop; bearing replacement per SOP-01 |
| JSR.BF.BLW.FAN01.TEMP.BRG | > 80 °C (warning) | OEM notification; API 670 monitoring |
| JSR.BF.BLW.FAN01.TEMP.BRG | > 95 °C (alarm) | Trip |
| JSR.BF.BLW.FAN01.THRUST.TEMP | > 90 °C (warning) | OEM notification |
| JSR.BF.BLW.FAN01.THRUST.TEMP | > 105 °C (alarm) | Trip immediately |
| JSR.SP.FAN01.VIB.AXIAL | > 0.4 (warning, axial/radial ratio) | Indicates misalignment or coupling fault |
| JSR.SP.FAN01.DP.DUCT | > 18 kPa | Investigate blade buildup or downstream restriction |
| Gradual 1X rise over days | Any fan | Dust buildup — plan cleaning at next available stop |
| Sudden 1X step | Any fan | Blade damage or deposit shedding event — inspect before restart |

---

## 4. TOOLS AND EQUIPMENT

| Item | Specification |
|------|--------------|
| Two-plane field balancer | IRB-type or Prüftechnik Vibxpert — for in-situ field balancing |
| Balancing weights set (BAL-WT-01) | 5 sets in stock; mass range to match fan disc size |
| In-situ hard-facing weld kit | Tungsten carbide overlay; SMAW or FCAW process |
| Angle gauge (blade pitch) | For axial fan blade pitch setting |
| High-pressure washer | Blade surface cleaning (wet wash) |
| Borescope (Olympus IPLEX) | Blade condition inspection from access ports |
| Vibration analyser | Two-channel for field balancing |
| Wire brush + scraper | Dry cleaning of baked-on deposits |
| Torque wrench (calibrated) | Blade-root bolts; pedestal bearing bolts |
| IR thermometer | Bearing housing monitoring during run-up |
| Anti-seize compound | Blade-root bolt thread treatment |

---

## 5. SPARES REQUIRED

| Part ID | Description | Stock Qty | Lead Time |
|---------|-------------|-----------|-----------|
| FAN-BLADE-SET | Fan blade set (axial/radial) | 0 on shelf | 12 weeks |
| BAL-WT-01 | Balancing weights set | 5 on shelf | In stock |
| BRG-LRG-300 | Large-bore bearing (fan pedestal) | 1 on shelf | 8 weeks if OOS |
| BRG-JRNL-PAD | Journal bearing pads OEM (BF.BLW.FAN01) | 1 on shelf | 12 weeks if OOS |
| BRG-THRUST-PAD | Thrust bearing pads Babbitt (BF.BLW.FAN01) | 1 on shelf | 12 weeks if OOS |
| ASV-VLV-01 | Anti-surge valve (BF.BLW.FAN01) | 0 on shelf | 12 weeks |

> **FAN-BLADE-SET and ASV-VLV-01 are zero-stock, 12-week lead — raise procurement as soon as blade erosion is detected to avoid a blind wait window.**

---

## 6. NUMBERED PROCEDURE STEPS

### OPTION A — Blade Cleaning and Field Balancing (SP.SINT.FAN01; 4–8 h)

**Pre-work**
1. Pull 1X vibration trend for the last 30 days from SCADA (JSR.SP.FAN01.VIB.1X). Gradual rise confirms dust buildup as root cause. Sudden step or any directional change points to blade damage — inspect before considering a balance-only response.
2. Apply LOTO per Section 2. Confirm zero speed before entering fan housing.
3. Gas test inside casing with portable CO detector (confined-space entry; SP.SINT.FAN01 handles sinter exhaust gas).

**Blade Inspection and Cleaning**
4. Enter fan casing or inspect blades through access ports. Inspect all blades systematically (number blades 1–N with chalk before starting). Use straight-edge to measure buildup depth at tip, mid-span, and root on each blade.
5. Record buildup depth and distribution — asymmetric buildup across blades or asymmetric distribution on a single blade = imbalance source.
6. Wet-wash blades with high-pressure water (preferred). Apply equal effort to each blade. Direct nozzle at leading edge and concave face.
7. For baked-on deposits (common with sinter dust at temperature): scrape with non-sparking scraper + wire brush. **Apply equal treatment to all blades — unequal cleaning creates imbalance.**
8. After cleaning: inspect blade surfaces. Document and photograph:
   - Pitting depth at leading edge
   - Erosion of leading-edge thinning (compare to manufacturer minimum thickness)
   - Any cracks (dye-penetrant test if crack is suspected — mandatory for cracks)
   - Erosion grooves at mid-span

**Field Balancing**
9. Set up two-plane field balancer (Prüftechnik Vibxpert or equivalent). Mount accelerometers at DE and NDE pedestals — axial and radial per balancer instructions.
10. Restart fan (remove LOTO partially — only re-energise drive for balance run; maintain mechanical guards and area clearance).
11. Run to full speed. Record reference run (vibration amplitude and phase at each plane). Plot on polar chart.
12. Add trial weight (BAL-WT-01) at calculated position. Record result. Apply balancing software influence coefficient method.
13. Iterate (maximum 3 correction runs typical for good outcomes). **Target: vibration < 2.3 mm/s at each plane (ISO 10816-3 Zone A).** [unverified — should target G2.5 per ISO 21940-11]
14. After accepting balance state: lock balancing weights securely (tack-weld or lockwire if removable type to prevent throwing at speed).
15. Restore full LOTO. Close all access points securely.

---

### OPTION B — Blade Hard-Facing (Erosion Repair; 8–16 h)

15. Apply LOTO. Confirm zero speed.
16. For SP.SINT.FAN01 radial blades: measure leading-edge blade thickness with callipers at 25%, 50%, 75%, and 100% of blade span. Compare to minimum thickness per TLT-Turbo drawing. [unverified — obtain drawing from OEM]
17. If within minimum thickness: proceed with hard-facing overlay.
18. Apply tungsten carbide (WC) weld overlay to leading edge using SMAW or FCAW process (specialist welder required). Overlay thickness: 2–3 mm. [unverified]
19. Dress weld overlay to original blade profile using angle grinder. Verify with template (make template from new blade cross-section drawing or OEM template if supplied).
20. Apply hard-facing to all blades — never patch one blade only (this creates asymmetric mass and immediate imbalance).
21. After hard-facing and dressing: perform field balance per Steps 9–14.

---

### OPTION C — Blade Replacement (after cracks, below-minimum-thickness erosion, or weld failure)

22. Apply LOTO. Mark each blade with blade number and current pitch angle (use angle gauge) before removal — **pitch angle is critical for performance and vibration.** Photograph all blades and angles.
23. Pre-soak blade-root bolts with penetrating oil 24 h before planned start (corroded bolts are common in sinter/BF environments). [unverified]
24. Remove blade-root bolts. Withdraw blades.
25. Fit new blades (FAN-BLADE-SET) at original pitch angle verified by angle gauge. **All blades must be at the same pitch angle within ±0.1°.** [unverified]
26. Torque blade-root bolts to OEM specification. Apply anti-seize compound on threads for future removal.
27. Check static balance on mandrel. Adjust by adding/removing material from blade tip if required. [unverified]
28. Perform field dynamic balance per Steps 9–14 after first run.

---

### BF.BLW.FAN01 — Surge Response and Return to Service (SCN-041 reference)

29. On SURGE alarm (JSR.BF.BLW.FAN01.PRES.OSC > 8%): verify anti-surge valve (ASV-VLV-01) has auto-opened.
30. If surge persists > 2–3 cycles (shaft displacement > 80 µm or audible "banging"): **trip compressor immediately.** Do NOT attempt to hold on-line.
31. Do NOT restart until root cause is identified (filter condition, downstream valve state, operating point vs surge line).
32. After trip: complete LOTO. Call OEM (Siemens/MAN service desk) for post-surge inspection.
33. Pull event-recorder data from Bently Nevada 3500 system — surge signature and timestamp.
34. Borescope IGVs and impeller stages for damage.
35. Pull lube oil sample — ferrographic analysis for metallic debris from bearing wipe.
36. OEM to advise on restart clearance before re-energising.

---

## 7. ACCEPTANCE CHECKS

| Parameter | Acceptance Criterion | Instrument |
|-----------|---------------------|------------|
| JSR.SP.FAN01.VIB.1X post-balance | < 2.3 mm/s (Zone A, ISO 10816-3) | Vibration analyser |
| JSR.BF.BLW.FAN01.VIB.1X | < 2.3 mm/s (Zone A) | Bently Nevada 3500 |
| JSR.BF.BLW.FAN01.SHAFT.DISP | < 50 µm pk-pk (normal range: 10–50 µm) | Bently Nevada proximity |
| JSR.SP.FAN01.TEMP.BRG | < 65 °C (normal range: 45–65 °C) | Thermocouple |
| JSR.BF.BLW.FAN01.THRUST.TEMP | < 75 °C (normal range: 50–75 °C) | Thermocouple |
| Blade pitch angles (axial fan) | Equal within ±0.1° | Angle gauge |
| No resonance during run-up | Smooth acceleration through all speeds | Vibration analyser trend |
| Balancing weight secure | No movement when tapped | Physical check |
| JSR.BF.BLW.FAN01.PRES.OSC | < 2 % (normal range) | Discharge pressure transmitter |

---

## 8. TIME ESTIMATE

| Scenario | TTR |
|----------|-----|
| Blade cleaning + field balance | 4–8 h |
| Hard-facing + balance | 8–16 h |
| Blade set replacement + balance | 8–24 h (depending on access and bolt corrosion) |
| BF.BLW.FAN01 — surge inspection only (no damage) | 4–8 h + OEM clearance |
| BF.BLW.FAN01 — journal bearing replacement | 3–7 days (OEM-led) |

---

## 9. RECURRENCE PREVENTION

- Install abrasion-resistant wear liners (Hardox 400 or equivalent TBC coating) on SP.SINT.FAN01 blade leading edges and inlet box — significantly extends blade life in dust-laden sinter gas service. [unverified]
- Establish cleaning interval based on buildup rate: for SP.SINT.FAN01 (heavy dust loading), inspect blades every 500 operating hours; clean if 1X exceeds 3 mm/s before the interval. [unverified]
- For BF.BLW.FAN01 anti-surge control: verify surge-line coordinates in control system against OEM commissioning data at least every 2 years. Inlet filter fouling reduces surge margin — replace on schedule, not just condition.
- Blade crack detection: inspect all SP.SINT.FAN01 blades with dye-penetrant test at every major planned outage (annual minimum).
- Balancing weights: store BAL-WT-01 in a clean, dry location. Corroded or damaged weights must not be fitted — mass uncertainty causes balance error.
