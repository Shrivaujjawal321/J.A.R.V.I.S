# Steel Plant Equipment Failure — Repair / Resolution Process Playbooks
# Maintenance Engineer's Runbook
# Version 1.0 | 2026-06-08
# Coverage: 13 major failure mode families across hot/cold rolling, casting, utilities, and materials-handling

---

## HOW TO USE THIS DOCUMENT

Each playbook follows a fixed eight-section schema:
1. Detection → Diagnosis (readings that confirm the fault)
2. Immediate Action (stop / derate / isolate / safety steps)
3. Repair Procedure (step-by-step)
4. Spares Required + Lead Time
5. Tools / Skills / Crew
6. Time-to-Repair (TTR) — planned vs unplanned
7. Plannability (next shutdown vs emergency stop)
8. Verification / Return-to-Service
9. Recurrence Prevention

Plant-specific numerical estimates are tagged [unverified — for demo only] where they come from synthetic corpus or industry heuristics rather than a verified Tata Steel source document. Published standards and manufacturer guidance are cited by URL where available.

---

---

# PLAYBOOK 01 — ROLLING-ELEMENT BEARING FAILURE
## Equipment: All rotating machines (motors, gearboxes, roll necks, fans, pumps)

### 1. Detection → Diagnosis

| Indicator | Alarm Threshold | Instrument |
|-----------|----------------|------------|
| Vibration velocity (RMS) | >7.1 mm/s ISO 10816-3 Zone C→D | Permanently mounted accelerometer or route-based vibration pen |
| Bearing housing temperature | >80 °C (80-95 °C = warning; >95 °C = danger) [unverified] | Thermocouple / IR gun |
| Acoustic emission (AE) | Elevated dBµV vs baseline | AE sensor or ultrasonic SDT instrument |
| Lube oil particle count | ISO 4406 cleanliness >18/16/13 | In-line particle counter or lab sample |
| Shock-pulse value (SPM) | dBN >35 | SPM instrument |

Diagnostic sequence:
- Step 1: When alarm triggers, take waveform (time-domain + FFT). Confirm bearing defect frequencies: BPFO (ball-pass outer), BPFI (ball-pass inner), BSF (ball-spin), FTF (fundamental train) match the installed bearing catalogue.
- Step 2: Cross-reference with temperature trend over last 7 days. Sudden spike + high BPFO = outer-race spall. Gradual rise + AE peak = lubrication starvation.
- Step 3: Pull an oil sample from the lube reservoir feeding that bearing. Ferrous particle count >200 ppm (patchwork analysis) confirms metallic wear. [unverified]
- Step 4: Compare shaft runout at coupling using a dial gauge (>0.05 mm TIR = misalignment contributing factor). [unverified]
- Step 5: Log exact machine speed, load, and ambient temperature at time of alarm to confirm diagnosis is not speed-transient artefact.

Reference: ISO 10816-3:2009 (vibration severity), ISO 15243:2017 (bearing failure mode classification).
URL: https://www.iso.org/standard/59063.html

### 2. Immediate Action

1. Acknowledge and log alarm in CMMS (SAP PM or Maximo) with timestamp.
2. If vibration is in Zone D (>14 mm/s) OR temperature >95 °C: initiate controlled shutdown of the equipment — do NOT emergency-trip unless fire/smoke is present (sudden trip can cause secondary damage via thermal shock).
3. If Zone C (<14 mm/s, <85 °C): derate load by 30%, increase lube oil flush rate, notify shift supervisor, schedule inspection within next 4 hours.
4. Lock-out / Tag-out (LOTO) per plant LOTO procedure before any physical inspection. Confirm zero-energy state.
5. Post safety barrier around equipment; hot bearing housings retain heat >30 min post-shutdown.

### 3. Repair Procedure

**Stage A — Disassembly**
1. Drain and collect lube oil (label containers for analysis).
2. Remove coupling (record coupling gap and angular offset for reinstallation reference).
3. Remove bearing housing end-caps; photograph bearing in situ.
4. Use bearing puller (hydraulic preferred; mechanical if small bore <80 mm). NEVER strike bearing directly with hammer.
5. Measure journal diameter with micrometer. Record reading; compare to OEM tolerance (+0/-0.025 mm for H7/k6 typical fit). [unverified]
6. Inspect housing bore with bore gauge; compare to OEM (G7 housing fit typical). [unverified]
7. If journal worn beyond tolerance: send shaft to machine shop for chrome-spray and re-grind (this extends TTR significantly — see Section 6).

**Stage B — Root-Cause Inspection**
8. Wash removed bearing in clean solvent, air-dry, photograph all surfaces under magnification.
9. Classify failure mode per ISO 15243: fatigue spall, wear, corrosion, electrical erosion (fluting), plastic deformation, fracture.
10. Inspect seals/shields for damage. Inspect labyrinth seal clearance.
11. Inspect lube lines: check for blockage, kinking, correct nozzle direction (oil jet must aim at rolling elements, not cage).

**Stage C — Reassembly**
12. Clean housing bore and shaft journal thoroughly; verify surface finish Ra <1.6 µm. [unverified]
13. Heat new bearing in induction heater to 80-100 °C (NEVER exceed 120 °C to avoid raceway softening). Fit bearing onto shaft — it should slide by hand; if it requires force, temperature is too low.
14. Fit housing and torque end-cap bolts to OEM specification (always use calibrated torque wrench).
15. Replenish grease (for grease-lubricated bearings): fill 30-50% of free space — overfilling causes churning and overheating. Use the OEM-specified grease grade. [unverified]
16. For oil-lubricated bearings: reconnect lube lines, set correct flow rate per OEM (typical 0.5-2 L/min per bearing), prime system before start.
17. Recouple shaft: align using laser alignment tool (target <0.05 mm parallel, <0.05 mm/100 mm angular). [unverified]
18. Replace coupling element (spider/disk/sleeve) if it shows wear — always replace during bearing change (cheap insurance).

### 4. Spares Required + Lead Time

| Item | Stock Policy | Typical Lead Time if OOS |
|------|-------------|--------------------------|
| Replacement bearing (standard SKF/FAG/NSK) | Keep 1 unit on shelf per critical machine | 1-3 days (distributor stock) |
| Bearing (special large bore >300 mm) | Managed stock or VMI agreement | 4-12 weeks [unverified] |
| Labyrinth seal set | Keep 2 per machine | 1-2 weeks [unverified] |
| Coupling element (spider/grid) | Keep 1 per machine | 1-2 weeks |
| Lube oil (ISO VG 46/68/100 as applicable) | Bulk tank on-site | In stock |
| Induction heater consumables | Workshop stock | In stock |

### 5. Tools / Skills / Crew

- Tools: Vibration analyser (CSI 2140 / Fluke 810 or equivalent), induction bearing heater, hydraulic bearing puller set, laser shaft-alignment tool (Prüftechnik OPTALIGN or equivalent), calibrated torque wrench set, bore gauge, micrometer set, dial indicator, IR thermometer, oil sampling kit.
- Skills: Level 2 vibration analyst (ISO 18436-2) for diagnosis; mechanical fitter (journeyman) for replacement. Machine-shop lathe operator if journal regrind needed.
- Crew: 1 vibration analyst (diagnosis), 2 mechanical fitters (disassembly/reassembly), 1 supervision (permit holder).

### 6. Time-to-Repair

| Scenario | TTR |
|----------|-----|
| Standard bearing swap, accessible location, spares on shelf | 4-8 hours (unplanned) / 3-5 hours (planned) [unverified] |
| Large-bore bearing, crane required | 8-16 hours [unverified] |
| Journal regrind needed | Add 3-5 days [unverified] |
| Full gearbox removal required | See Playbook 02 |

### 7. Plannability

- Zone C: Plan for next scheduled maintenance window (weekly or monthly PM).
- Zone D or temperature >95 °C: Emergency stop — cannot be deferred.
- Trending (rising vibration still in Zone B/C): high-value opportunity to plan during a production gap (e.g. grade change, tap-to-tap break) to avoid emergency outage.

### 8. Verification / Return-to-Service

1. Pre-start check: confirm lube oil flow visible at sight glass; bearing housing temperature ambient ± 5 °C.
2. Start at no-load; run for 15 minutes. Take vibration reading — must be <2.3 mm/s (Zone A) per ISO 10816-3.
3. Take bearing temperature at 15 min, 30 min, 60 min. Should stabilise <70 °C (grease-lubricated) or <65 °C (oil-lubricated). If still rising at 60 min, shut down and investigate preload/alignment.
4. Ramp to full load; take final vibration signature. File in CMMS as baseline for this repair.
5. Take oil sample at 2 hours into operation; send to lab. Target ISO 4406 ≤17/15/12. [unverified]

### 9. Recurrence Prevention

- Root-cause register: log ISO 15243 failure mode code into CMMS every time — over 6 months this surfaces systemic causes (contamination, misalignment, overloading).
- Lubrication management: implement automatic lubrication systems (SKF TLSD / Lincoln) on high-frequency relubrication points to eliminate human-error starvation.
- Alignment program: mandate laser-alignment check every time coupling is disturbed, and at 6-monthly intervals on all Category 1 machines.
- Shaft current mitigation: if fluting (electrical erosion) is found, fit insulated bearing (hybrid ceramic or coated outer ring) and check VFD grounding on motor.
- Online monitoring: install permanent wireless vibration nodes (Emerson AMS Wireless HART or Schaeffler FAG WiPro) on critical machines so alarm-to-action time reduces from hours to minutes.

---

---

# PLAYBOOK 02 — GEARBOX TOOTH / OIL FAILURE
## Equipment: Mill-drive gearboxes, pinion stands, rougher/finishing mill gearboxes, coiler drive gearboxes

### 1. Detection → Diagnosis

| Indicator | Alarm Threshold | Instrument |
|-----------|----------------|------------|
| Vibration: gear mesh frequency (GMF = N x RPM/60) | >10 mm/s at GMF + sidebands | Vibration analyser + spectrum |
| Cepstrum analysis: quefrency peaks | Sidebands spaced at shaft RPM | Cepstrum processing |
| Oil temperature (sump) | >80 °C warning / >90 °C trip [unverified] | Thermocouple in sump |
| Oil pressure | <2 bar (minimum for forced-lube) [unverified] | Pressure switch/transmitter |
| Magnetic plug / chip detector | Metallic debris present | Visual inspection + chip detector |
| Oil particle count / ferrography | >1000 ppm Fe or large gear spall particles | Lab oil analysis |
| Audible noise | Grinding, knocking, or whining | Operator ears / stethoscope |

Diagnostic sequence:
- Step 1: Pull oil sample — perform ferrography (particle morphology). Gear-wear particles are flat platelets; tooth spall = chunky, irregular fragments. This is the most definitive non-invasive diagnostic.
- Step 2: Take vibration spectrum at input and output shaft positions. Look for GMF amplitude and sideband pattern (number of sidebands = severity index). A sideband ratio >3 dB change from baseline = significant tooth damage. [unverified]
- Step 3: If possible, borescope through inspection port while gear is at low speed to visually confirm tooth condition (pitting, spall, scuffing, micro-pitting).
- Step 4: Check oil level and colour. Black/milky oil = contamination or water ingress. Check breather condition.
- Step 5: Correlate with production history — sudden high-torque events (cobble in mill, sticker, emergency brake) often precede tooth damage.

Reference: AGMA 2101-D04 (gear strength), ISO 13306 (maintenance terminology).
URL: https://www.agma.org/standards/

### 2. Immediate Action

1. If chip detector alarms or large spall confirmed on ferrography: immediate controlled stop. Do NOT continue operation — loose debris in oil causes cascading bearing and tooth damage within hours.
2. If only elevated temperature + mild vibration increase: derate load 20%, increase oil cooling flow, increase oil sampling frequency to every 2 hours, notify maintenance manager.
3. LOTO before opening any inspection cover.
4. Retain all oil samples in sealed containers — they are evidence for root-cause.

### 3. Repair Procedure

**Option A — In-situ tooth repair (minor pitting/micro-pitting, tooth intact)**
1. Open inspection covers (LOTO).
2. Inspect all teeth under illumination — document with photography at each tooth position.
3. If pitting is sub-surface and tooth geometry intact: apply gear-tooth sealant compound (Belzona 1212 or equivalent) to arrested pits to prevent debris generation. This is a condition-based defer, not a fix.
4. Flush gearbox twice with flushing oil (ISO VG 32 flush grade). Drain completely.
5. Replace oil filter elements (always).
6. Refill with fresh gear oil (OEM-specified grade — typically ISO VG 220 or 320 extreme-pressure gear oil for mill drives). [unverified]
7. Check breather and replace if blocked.

**Option B — Gear wheel / pinion replacement (spalling, tooth fracture)**
1. Full LOTO + de-energise hydraulic brake systems.
2. Remove gearbox from drive train (disconnect couplings, remove hold-down bolts, rig with crane to OEM lift points).
3. Transport to workshop (gearbox repair bay). Weight can be 5-50 tonnes for mill-drive boxes — crane capacity must be confirmed before lift. [unverified]
4. Strip gearbox on workbench. Record all shaft end-float and backlash measurements before disassembly.
5. Remove damaged gear wheel/pinion from shaft (hydraulic press; heat if shrink-fit).
6. Inspect gear shaft for fretting or wear. Measure gear-seat diameter vs OEM tolerance.
7. Install new gear wheel: heat-fit to OEM interference (typically 0.05-0.15% of bore diameter). [unverified]
8. Reassemble with new bearings (take the opportunity — bearing replacement cost is negligible vs gearbox removal labour).
9. Set backlash per OEM spec (typical 0.1-0.3 mm for industrial gearboxes; tighter for high-speed stages). [unverified]
10. Check gear tooth contact pattern with Prussian blue: contact should be centred and cover >70% of tooth face. [unverified]
11. Refill with correct oil; run-in per OEM break-in procedure (usually 4-8 hours at 50% load with increased monitoring).
12. Reinstall in drive train; laser-align all couplings.

### 4. Spares Required + Lead Time

| Item | Stock Policy | Lead Time if OOS |
|------|-------------|-----------------|
| Oil filter elements | Min 3 per gearbox on shelf | In stock |
| Gear oil (correct grade, 200 L drum) | In stock bulk | In stock |
| Input/output shaft bearings | Keep one set per critical gearbox | 1-4 weeks [unverified] |
| Gear wheel (standard cut) | On-demand from gear manufacturer | 8-20 weeks [unverified] |
| Gear wheel (custom large module, >M20) | Capital-linked long-lead spare | 20-52 weeks [unverified] |
| Gearbox complete (critical mill drive) | Insurance spare or OEM exchange pool | 12-24 weeks [unverified] |

### 5. Tools / Skills / Crew

- Tools: Vibration analyser, borescope (Olympus IPLEX or equiv.), ferrography unit OR oil analysis lab courier, hydraulic press (10-100 T), induction heater, laser alignment, calibrated torque wrenches, precision dial gauges (backlash measurement), Prussian blue compound, flush oil drum.
- Skills: Gearbox specialist fitter, vibration analyst (Level 2), crane operator (overhead crane ticket), machine-shop operator if shaft repair needed.
- Crew: 2-4 fitters + 1 crane operator + 1 maintenance engineer (for OEM interface) + 1 permit-holder supervisor.

### 6. Time-to-Repair

| Scenario | TTR |
|----------|-----|
| Oil flush + filter change only | 4-6 hours [unverified] |
| Gear wheel replacement (gearbox removed, spare gear available) | 3-7 days [unverified] |
| Gear wheel replacement (gear manufactured to order) | 8-24 weeks [unverified] |
| Complete gearbox swap (insurance spare available) | 16-24 hours (crane + alignment time) [unverified] |

### 7. Plannability

- Pitting / micro-pitting with no spall: plan to next campaign break (days to weeks) with increased monitoring.
- Tooth spall / fracture: emergency stop. No deferral possible — risk of catastrophic tooth failure causing shaft fracture.
- Mill-drive gearbox replacement: must be planned to a major shutdown unless insurance spare is available for hot-swap.

### 8. Verification / Return-to-Service

1. Run at 25% load for 30 minutes; take vibration spectrum and oil temperature. Compare to pre-repair baseline.
2. Run at 50% load for 1 hour; check oil cleanliness (particle count must be declining — flushing effect from new surfaces).
3. Full load: take vibration signature at steady state. GMF amplitude must be within 3 dB of baseline.
4. Oil sample at 8 hours running: target ISO 4406 cleanliness recovering toward ≤18/16/13. [unverified]
5. Inspect magnetic drain plug at 24 hours — normal "fines cloud" around plug is acceptable; discrete large particles are not.

### 9. Recurrence Prevention

- Oil analysis programme: monthly (quarterly for low-criticality) ferrographic analysis of all gearbox oil samples. Trend particle counts — catch degradation 2-4 weeks before catastrophic failure.
- Oil quality management: implement oil cleanliness target <16/14/11 ISO 4406 for all mill-drive gearboxes via kidney-loop filtration units. [unverified]
- Load exceedance logging: connect torque measurement to CMMS; auto-raise work order if torque exceeds 110% rated for >5 seconds. [unverified]
- Run-in procedure: enforce low-load run-in after any gear replacement (new surfaces need to bed in).
- Thermal camera survey: quarterly thermal imaging of gearbox sump areas to detect early hot spots.

---

---

# PLAYBOOK 03 — MOTOR WINDING / ROTOR FAILURE
## Equipment: All large AC/DC drive motors (mill drives, fan drives, pump drives, crane hoists)

### 1. Detection → Diagnosis

| Indicator | Failure Mode | Instrument |
|-----------|-------------|------------|
| Motor Current Analysis (MCA) — rotor slot harmonics | Broken rotor bar | Power analyser / MCSA software (Baker DX or Motor Monitor Plus) |
| Winding insulation resistance (Megohm test) | Winding degradation | Megohmmeter (Megger MIT1025) |
| Polarisation Index (PI) — R10min/R1min | <2.0 = concern; <1.0 = critical | Megohmmeter |
| Winding temperature | >Class F limit 155 °C / Class H 180 °C | Embedded thermocouples (PT100) or thermal camera |
| Vibration: 2x line-frequency sidebands around GMF | Broken rotor bar or eccentricity | Vibration analyser |
| Differential protection relay trip | Winding fault to earth or phase-to-phase | Protection relay (SEL-710 or equiv.) |
| Partial Discharge (PD) magnitude | >100 pC continuous [unverified] | PD coupler / TEV probe |

Diagnostic sequence:
- Step 1: Check CMMS — was there a recent overcurrent, phase loss, or voltage dip event logged? These are primary causes.
- Step 2: De-energise motor. Take insulation resistance (IR) test at 1 kV (for LV motors) or 5 kV (for MV motors). PI <2.0 warrants further investigation. Record temperature at time of test — IR is temperature-dependent (apply correction per IEEE 43-2013).
- Step 3: If motor is suspect for broken rotor bar: take Motor Current Signature Analysis (MCSA) at steady-state load. Look for sidebands at f ± 2sf (where s = slip) — amplitude >-50 dBc from fundamental = broken bar. [unverified]
- Step 4: Bump test (short impulse with motor out of service): perform high-voltage surge test to identify turn-to-turn shorts (Baker D6000 or equivalent).
- Step 5: Thermal camera survey of motor body while running at load — hot spots on frame indicate concentrated heat from localised winding damage.

Reference: IEEE Std 43-2013 (Insulation Resistance Testing), NEMA MG1, IEC 60034-1.
URL: https://standards.ieee.org/ieee/43/3606/

### 2. Immediate Action

1. If protection relay has tripped: do NOT reset and restart until IR test confirms winding is serviceable. Forcing a re-start on a faulted winding causes further irreversible damage.
2. If winding temperature alarm only (not trip): reduce motor load, check cooling air flow (fan / heat exchanger).
3. LOTO. Post "MOTOR UNDER INVESTIGATION — DO NOT START" tag.
4. For MV motors (>3.3 kV): notify electrical supervisor; HV LOTO requires authorised person.

### 3. Repair Procedure

**Option A — In-situ repair (minor insulation degradation, no physical damage)**
1. With motor isolated: dry out winding by forced warm air (heat gun at 50 °C) or by passing low current through winding until insulation resistance recovers to >100 MΩ at 40 °C.
2. Apply vacuum pressure impregnation (VPI) varnish treatment if accessible (smaller motors brought to workshop).
3. Re-test insulation after treatment — PI must be >2.0 before return to service. [unverified]

**Option B — Workshop rewind (severe winding failure)**
1. Remove motor from equipment — disconnect all power connections, coupling, and mounting bolts. Rig per weight (large MV motors >10 T need crane).
2. Transport to motor workshop (on-site or specialist winding shop).
3. Strip stator: burn out old winding in burnout oven (350-400 °C for 2-4 hours). Do NOT exceed temperature that damages laminations. [unverified]
4. Clean slots; inspect lamination stack for damage (burning, shorts between laminations). If lamination damage: re-core or replace stator (major job — weeks).
5. Wind new coils to original specification: wire gauge, turns per coil, pitch, connection (wye/delta). Use original nameplate data or reverse-engineer from removed coil measurements.
6. Insert coils; secure with slot wedges.
7. VPI impregnation: immerse in Class H (180 °C) resin, cure in oven per resin manufacturer specification.
8. Test rewound stator: hi-pot test (2 × rated voltage + 1 kV for 1 minute), surge test, IR test (>1000 MΩ at 40 °C target). [unverified]
9. Inspect rotor: check for broken bars (rotor bar dye test or eddy-current test), shaft runout (<0.025 mm TIR for precision motors). [unverified]
10. Balance rotor: dynamic balance to ISO 21940-11 Grade G2.5 or better. [unverified]
11. Reassemble: new bearings (always), correct oil/grease per OEM.
12. No-load run test and heat-soak test before return to site.

**Option C — Motor swap (critical motor, insurance spare available)**
1. Remove failed motor (LOTO, disconnect, rig, remove).
2. Install spare motor on prepared baseplate.
3. Laser-align coupling to driven equipment.
4. Reconnect power; verify phase rotation before energising (phase-rotation meter).
5. Send failed motor to workshop for assessment/rewind.
6. Full load test and commission.

### 4. Spares Required + Lead Time

| Item | Stock Policy | Lead Time if OOS |
|------|-------------|-----------------|
| Bearings (DE and NDE, per motor type) | Keep 1 set per critical motor | 1-3 days |
| Motor spare (complete, critical service) | Insurance spare on shelf | In stock (large capital) |
| Motor spare (general service LV) | Pooled by frame size | 2-8 weeks [unverified] |
| Rewind materials (wire, resin, wedge, slot liner) | Winding shop stock | 2-4 weeks [unverified] |
| MV motor (>1 MW, custom) | Long-lead procurement | 20-52 weeks [unverified] |

### 5. Tools / Skills / Crew

- Tools: Megohmmeter (Megger MIT1025 or 5 kV unit for MV), MCSA analyser, hi-pot tester, surge tester (Baker D6000), thermal camera, lathe (for rotor), dynamic balancing machine, VPI resin system, burnout oven, laser alignment, crane.
- Skills: Licensed electrician (LV), HV-authorised person (MV work), motor winding specialist, mechanical fitter (bearings, coupling), alignment specialist.
- Crew: 2 electricians, 2 mechanical fitters, 1 supervisor/permit holder, motor winding shop team (for rewind).

### 6. Time-to-Repair

| Scenario | TTR |
|----------|-----|
| In-situ drying and varnish (minor) | 8-24 hours [unverified] |
| Motor swap with insurance spare | 6-12 hours (removal + alignment + commissioning) [unverified] |
| Workshop rewind (LV motor, no lamination damage) | 3-7 days [unverified] |
| Workshop rewind (MV motor >1 MW) | 4-12 weeks [unverified] |
| New motor procurement (large MV, custom) | 20-52 weeks [unverified] |

### 7. Plannability

- Rising temperature trend or PI between 1.5-2.0: plan rewind or replacement within next major shutdown.
- PI <1.0 or differential relay trip: emergency stop — cannot restart until tested.
- Broken rotor bar (confirmed by MCSA, running otherwise smoothly): plan motor swap within 2-4 weeks; rotor bars can spread progressively to catastrophic failure. [unverified]

### 8. Verification / Return-to-Service

1. Pre-energise: insulation resistance >100 MΩ (>1000 MΩ preferred), PI >2.0, phase rotation confirmed.
2. No-load start: current balance ≤2% unbalance across phases, winding temperature rising normally.
3. Load test: current at full load within nameplate ±5%, temperature stabilises below class limit within 2 hours.
4. Final vibration check: overall vibration <2.8 mm/s for motors <15 kW, <4.5 mm/s for >15 kW (ISO 10816-3 Zone A). [unverified]

### 9. Recurrence Prevention

- Trend PI annually (or after every thermal event) — target is catching PI drift before it reaches 2.0.
- Variable Frequency Drive earthing: rotor shaft currents from VFDs are the leading cause of bearing AND winding failure in modern motors. Install insulated bearings and shaft grounding brushes (AEGIS rings) on all VFD-driven motors >22 kW. [unverified]
- Motor protection relay: ensure overload, single-phase loss, phase-imbalance, and thermistor trips are all set AND enabled in relay (often disabled during commissioning and never re-enabled).
- Cooling: check cooling air filters monthly; blocked air filters are the most common cause of thermal winding failures in humid steel plant environments.
- Rewind specification control: when rewinding, always specify original wire gauge and turns — a rewinder using a heavier gauge wire to save cost reduces turns per coil, changes motor characteristics, and causes insulation damage from overfluxing.

---

---

# PLAYBOOK 04 — PUMP SEAL / IMPELLER FAILURE
## Equipment: Hydraulic descale pumps, cooling water pumps, scale pit pumps, lubrication oil pumps

### 1. Detection → Diagnosis

| Indicator | Failure Mode | Instrument |
|-----------|----------------|------------|
| Seal leakage flow rate | >10 mL/min (mechanical seal) [unverified] | Visual / collection cup measurement |
| Pump suction / discharge pressure delta | Impeller wear = reduced head, increased flow at lower pressure | Differential pressure gauge / PI controller |
| Motor current | Below design = cavitation or worn impeller; above design = impeller rubbing on casing | Ammeter / SCADA |
| Vibration | >4.5 mm/s at pump casing = cavitation / impeller damage [unverified] | Vibration pen |
| Shaft leakage (gland-packed pump) | >1 drop/second is normal; drip-free = too tight, stream = seal failure [unverified] | Visual |
| Noise | Crackling/rattling = cavitation; screeching = dry seal | Operator |

Diagnostic sequence:
- Step 1: Check seal chamber pressure and leakage rate. Mechanical seal leak >10 mL/min means faces are damaged or secondary O-ring is failing.
- Step 2: Plot pump operating point (flow vs head) against the design curve. If operating point has shifted to the right on the curve (higher flow, lower head): impeller wear. Left shift (lower flow, higher head): blockage or wear ring tight.
- Step 3: NPSH check — if suction pressure fluctuates, cavitation is likely. NPSH available must be ≥ NPSH required + 0.5 m safety margin. [unverified]
- Step 4: Bearing vibration check at pump bracket (not motor) to separate pump faults from motor/coupling faults.

Reference: HI 1.3 (Hydraulic Institute Standards for centrifugal pumps), ASME B73.1.
URL: https://www.pumps.org/standards/

### 2. Immediate Action

1. For active seal failure with water/oil spraying: isolate pump (stop motor, close suction and discharge valves). Switch to standby pump if available.
2. For gradual seal leak (moderate drip): reduce seal chamber pressure if possible (reduce discharge pressure), arrange standby pump readiness, schedule maintenance within one shift.
3. LOTO on pump and associated isolation valves.
4. If pump is in hydraulic descale service: ensure descale accumulator system remains pressurised from alternate source before isolating.

### 3. Repair Procedure

**Mechanical Seal Replacement**
1. Drain pump casing and seal chamber (collect liquid in drip tray — may be contaminated oil or process water with scale inhibitor).
2. Remove pump half-coupling, back-pullout assembly if available (allows seal change without disturbing pipe connections).
3. Remove gland plate and flush seal chamber.
4. Slide out stationary seat and rotating assembly. Note spring orientation and seal dimensions (OD, ID, face material — typically SiC/SiC for abrasive service, carbon/SiC for clean water). [unverified]
5. Clean shaft and shaft sleeve thoroughly. Inspect sleeve for scoring — if grooved >0.1 mm: replace sleeve (or build-up and re-grind). [unverified]
6. Install new seal: follow manufacturer assembly drawing exactly. Critical points: ensure O-rings are lightly lubricated with compatible fluid (water seals: clean water; oil seals: light oil — never use grease on a water seal). Keep seal faces clean — one fingerprint can cause immediate leakage.
7. Set seal flush and quench connections to specification; verify correct tubing orientation.
8. Reinstall pump; verify shaft runout <0.05 mm TIR. [unverified]
9. Prime pump; close discharge valve; start motor; crack-open discharge valve slowly.

**Impeller Replacement / Wear Ring Renewal**
1. Remove pump casing (split-case) or back-pullout assembly.
2. Remove impeller nut (left-hand thread on most single-stage pumps — check). [unverified]
3. Measure impeller OD and compare to original drawing. Wear rings: measure clearance between impeller and casing wear ring (new clearance typical 0.3-0.5 mm; replace at >1.0 mm or when pump efficiency drops >5%). [unverified]
4. Replace impeller and/or wear rings. Balance new impeller to ISO 21940-11 Grade G6.3 minimum. [unverified]
5. Re-assemble pump. Check shaft deflection — excessive deflection indicates bearing failure or impeller rub.

### 4. Spares Required + Lead Time

| Item | Stock Policy | Lead Time if OOS |
|------|-------------|-----------------|
| Mechanical seal (per pump type) | Keep 1 complete spare seal per pump, 2 for critical | 1-4 weeks |
| Shaft sleeve | Keep 1 per pump | 2-4 weeks |
| Impeller (standard material) | 1 per critical pump | 4-12 weeks [unverified] |
| Wear rings | 2 sets per pump | 2-6 weeks [unverified] |
| Casing gasket / O-ring kit | 2 per pump | In stock |
| Complete pump spare (critical descale service) | Insurance spare | In stock |

### 5. Tools / Skills / Crew

- Tools: Seal assembly press, shaft runout dial indicator, bore/OD micrometers, torque wrench, face-cleanliness mirror, shaft alignment tool, balancing machine (for impeller).
- Skills: Pump specialist (pipefitter/millwright), mechanical seal manufacturer training recommended for large or specialised seals.
- Crew: 2 fitters, 1 supervisor.

### 6. Time-to-Repair

| Scenario | TTR |
|----------|-----|
| Mechanical seal swap (back-pullout design) | 2-4 hours (planned) / 4-8 hours (unplanned) [unverified] |
| Mechanical seal swap (in-line pump, pipe removal needed) | 6-12 hours [unverified] |
| Impeller replacement | 4-8 hours (planned) [unverified] |
| Complete pump swap (insurance spare) | 1-3 hours [unverified] |

### 7. Plannability

- Gradual seal weep: plan within 1-2 shifts. Can use standby pump.
- Sudden seal failure / pump deadhead: emergency (switch to standby immediately, repair on isolated pump in parallel with continued production).
- Impeller wear (detected by performance loss): plan to next PM window.

### 8. Verification / Return-to-Service

1. Start pump against closed discharge; confirm amps at no-load within nameplate range.
2. Open discharge gradually; confirm differential pressure and flow rate match design curve.
3. Inspect seal chamber leakage: zero leakage acceptable for cartridge seals; <3 drops/min for some gland-type designs. [unverified]
4. Vibration check at 15 and 60 minutes of operation — target <4.5 mm/s.

### 9. Recurrence Prevention

- Cavitation prevention: verify NPSH margin, check for vortex formation in wet pit, ensure suction strainer is not blocked.
- Abrasive service: upgrade to harder seal face materials (SiC vs SiC) and sleeve material (Colmonoy or Stellite-coated) for scale-pit pumps handling high-solids liquids. [unverified]
- Seal flush plan review: most seal failures in steel plant service trace to dirty flush water or inadequate quench flow. Verify flush connections quarterly.
- Alignment: misaligned pump-motor imposes radial load on shaft, accelerating seal wear. Laser-align every time pump is disturbed.
- Condition-based monitoring: trend motor current and differential pressure weekly — impeller wear is a slow degradation and can be trended months ahead of failure.

---

---

# PLAYBOOK 05 — FAN BLADE / FAN BEARING FAILURE
## Equipment: Baghouse fans, boiler fans (ID/FD/PA), cooling tower fans, furnace combustion air fans, draught fans

### 1. Detection → Diagnosis

| Indicator | Failure Mode | Instrument |
|-----------|----------------|------------|
| Vibration at running speed (1X) | Blade imbalance, buildup, erosion | Permanently mounted accelerometer |
| Vibration at 1X with sidebands | Blade pass frequency = N_blades × RPM/60 — elevated = blade damage | Vibration analyser |
| Airflow / static pressure drop | Blade erosion or buildup | Pitot traverse / orifice plate / DP cell |
| Motor current rise | Blade buildup increasing drag | Motor current monitoring |
| Visual inspection through access port | Blade crack, erosion, corrosion buildup | Borescope |
| Bearing temperature | Bearing failure (see Playbook 01 for full detail) | Thermocouple |

Diagnostic sequence:
- Step 1: Vibration spectral analysis — high 1X amplitude = imbalance (most common cause in steel plant dust-laden service). High BPF (blade pass frequency) = blade damage or variation.
- Step 2: Check vibration trend history. Gradual rise in 1X over weeks = progressive dust buildup. Sudden step change = blade damage event (stone ingestion, thermal distortion, weld failure).
- Step 3: If fan handles process gas/dust: inspect blades at next accessible stop. Baghouse fans in steel plants typically accumulate fines on leading edges and near mid-span — this is the primary imbalance source. [unverified]
- Step 4: Check for resonance: if vibration is high at specific RPM bands during run-up, fan critical speed may coincide with operating speed (rare but catastrophic).

### 2. Immediate Action

1. If vibration exceeds Trip setpoint (typically >18 mm/s or plant-specific limit): automatic or manual trip the fan. Do NOT continue — blade failure can cause secondary rotor destruction and housing penetration (safety-critical).
2. If elevated but below trip: reduce speed if VFD-driven, investigate cause during next available stop.
3. LOTO + ensure fan casing is at rest (full stop) before opening access doors — residual rotation in large fans can take 5-15 minutes. [unverified]

### 3. Repair Procedure

**Imbalance due to Dust Buildup**
1. Open access doors (fan stationary, LOTO confirmed).
2. Inspect blades: measure and record buildup depth and distribution using a straight-edge (asymmetric buildup → imbalance).
3. Clean blades: wet wash (high-pressure water) or dry cleaning (scraper + wire brush for baked-on deposits). Pay equal attention to all blades.
4. Inspect blade surface after cleaning: pitting, erosion grooves, leading-edge thinning.
5. Re-balance in situ using field balancing equipment (IRB-type two-plane balancer). Target: G2.5 or better (ISO 21940-11). [unverified]
6. Run and verify vibration.

**Blade Erosion / Tip Repair**
1. Remove fan from service (LOTO).
2. Measure blade thickness at leading edge and tip. Compare to minimum thickness per OEM drawing. [unverified]
3. If within tolerance: apply hard-facing weld (Tungsten Carbide overlay) to leading edge to extend remaining life. Dress weld to original profile; re-balance.
4. If below minimum thickness or cracked: replace blade. For backward-curved multi-blade (centrifugal): replace as matched set (two opposite blades or all blades to maintain balance class). [unverified]

**Blade Replacement (axial fan, e.g. cooling tower)**
1. Mark all blades with blade number and pitch angle before removal.
2. Remove blade-root bolts (corroded bolts common — pre-soak with penetrating oil 24h before planned work).
3. Fit new blades at original pitch angle (use angle gauge — critical for airflow and vibration).
4. Torque blade-root bolts to OEM specification. Apply anti-seize compound.
5. Check static balance on mandrel; adjust blade pitch if required.
6. Dynamic balance in situ after first run.

### 4. Spares Required + Lead Time

| Item | Lead Time |
|------|----------|
| Blade set (standard axial fan) | 4-12 weeks [unverified] |
| Blade set (large centrifugal, custom) | 12-24 weeks [unverified] |
| Tungsten carbide welding consumables | In stock (welding workshop) |
| Fan bearings (large bore) | 4-12 weeks [unverified] |
| Balancing weights | In stock |

### 5. Tools / Skills / Crew

- Tools: Two-plane field balancer (IRB-type or Pruftechnik Vibxpert), in-situ hard-facing welding kit, angle gauge (blade pitch), high-pressure washer, borescope.
- Skills: Millwright/fitter, welder (hard-facing), balancing technician.
- Crew: 2-3 fitters, 1 welder if hard-facing, 1 supervisor.

### 6. Time-to-Repair

| Scenario | TTR |
|----------|-----|
| Cleaning + field re-balance | 4-8 hours [unverified] |
| Hard-facing + re-balance | 8-16 hours [unverified] |
| Blade set replacement (axial fan) | 8-24 hours depending on access and corrosion [unverified] |

### 7. Plannability

- Gradual buildup / imbalance rise: plan to next maintenance window (shift break, scheduled outage). High urgency if fan has no standby.
- Blade crack / sudden vibration step: emergency stop.

### 8. Verification / Return-to-Service

1. Run at 25%, 50%, 75%, 100% speed; take vibration at each step. Must be below Zone A/B at all speeds.
2. Confirm no resonance during run-up.
3. Check blade pitch angles are equal (critical for axial fans — asymmetry = vibration and reduced efficiency).

### 9. Recurrence Prevention

- Install abrasion-resistant wear liners on fan inlet and blade leading edges (Hardox 400 or TBC coating) for fans handling dusty process gas. [unverified]
- Automatic online balancing systems (LordMicrostrain or Cemb ActiveBalance) for fans where stopping for balance is expensive. [unverified]
- Borescope inspection quarterly without stopping fan (some plants install permanent borescope ports).
- Programmed blade cleaning: establish cleaning interval based on buildup rate (e.g. every 500 operating hours for baghouse fans). [unverified]

---

---

# PLAYBOOK 06 — COMPRESSOR SURGE / BEARING FAILURE
## Equipment: Blast furnace air compressors, nitrogen/oxygen plant compressors, instrument air compressors, boiler feed-water booster compressors

### 1. Detection → Diagnosis

**Surge Detection**
| Indicator | Alarm/Trip Level | Instrument |
|-----------|-----------------|------------|
| Discharge pressure oscillation | >±5% at constant speed [unverified] | Discharge pressure transmitter |
| Axial thrust bearing temperature | >80 °C [unverified] | Thermocouple on thrust pad |
| Anti-surge valve (ASV) position | Repeatedly cycling open = approaching surge line | Position indicator |
| Vibration (axial) | Step increase during surge event | Proximeter probe (Bently Nevada) |
| Audible "bang" or coughing sound | Diagnostic | Operator report |
| Compressor surge map position | Operating point left of surge line | Control system calculation |

**Bearing Failure Detection** (applies to journal and thrust bearings — hydrodynamic oil-film type in large turbo-compressors)
| Indicator | Level | Instrument |
|-----------|-------|------------|
| Journal bearing metal temperature | >90 °C warning / >105 °C trip [unverified] | Embedded thermocouple or RTD |
| Shaft vibration (proximity probe) | >50 µm pp warning / >76 µm pp trip (API 670 Alert/Trip typical) [unverified] | Bently Nevada 3500 system |
| Oil supply pressure | <2 bar = trip [unverified] | Pressure switch |
| Shaft position (DC offset) | Axial displacement >0.5 mm from datum = thrust bearing loss [unverified] | Proximeter probe |

Diagnostic sequence (surge):
- Step 1: Review control system trend: did the anti-surge valve fail to open in time? Was suction throttled too aggressively? Was there a downstream pressure disturbance (furnace tap, pipeline valve slam)?
- Step 2: Check inter-stage temperatures and pressures — elevated inter-stage temperatures after a surge event = internal recirculation.
- Step 3: Inspect inlet guide vanes (IGVs) for damage — surge events generate severe pressure reversals that can bend or crack IGVs.
- Step 4: Pull vibration data from the event recorder in the Bently Nevada system — the surge signature (chaotic vibration burst) is diagnostic and the timestamp helps root-cause the trigger event.

### 2. Immediate Action (Surge)

1. Anti-surge system should automatically open ASV and reduce load — verify this happened.
2. If surge persists (more than 2-3 cycles): trip compressor immediately. Sustained surge can destroy seals, bearings, and impellers within seconds.
3. After trip: do NOT restart until cause is identified. Repeated surge-start-surge is a common operator error that leads to total loss of a machine.
4. Notify process team — likely impact on downstream users (blast furnace, oxygen plant). Activate standby compressor or load management procedure.
5. LOTO and inspection.

### 3. Repair Procedure

**After Surge Event (bearing / seal inspection)**
1. Conduct full machine inspection: visual inspection of all accessible IGVs, diffuser vanes, impellers (via borescope), seals.
2. Pull lube oil sample — surge events generate heat and metallic debris. Ferrography will reveal if bearing damage occurred.
3. Check shaft runout and axial position against baseline.
4. If vibration has increased post-surge: pull rotor for full inspection in workshop.

**Journal Bearing Replacement (after failure)**
1. Strip compressor at bearing ends — highly specialised work (OEM service team typically required for large API-617 class machines).
2. Remove journal bearing pads (tilting-pad or sleeve type). Inspect for scoring, wiping, or spall.
3. Measure bearing clearance vs OEM tolerance (typical diametral clearance 0.001-0.002 × shaft diameter). [unverified]
4. Replace bearing shells/pads.
5. Reassemble; re-commission with phased run-up per OEM procedure.

**Thrust Bearing Replacement**
1. Similar to journal bearing but involves careful measurement of rotor axial position.
2. Install new thrust pads/Babbitt segments.
3. Set axial clearance per OEM specification.
4. Always replace lube oil filter elements after any bearing replacement.

### 4. Spares Required + Lead Time

| Item | Lead Time |
|------|----------|
| Journal bearing shells/pads (OEM) | 4-20 weeks [unverified] |
| Thrust bearing pads | 4-20 weeks [unverified] |
| Anti-surge valve (Koso / Fisher or equiv.) | 8-16 weeks [unverified] |
| Lube oil filters | In stock |
| Mechanical seal cartridge | 8-24 weeks [unverified] |
| Spare rotor (capital insurance) | 26-52 weeks [unverified] |

### 5. Tools / Skills / Crew

- Tools: Bently Nevada monitoring system, borescope, precision dial gauges, OEM calibrated assembly tools, clean-room portable shelter (for bearing work on site), high-cleanliness lube oil supply.
- Skills: OEM-trained compressor engineer (most plants use OEM service contract), specialist rotating equipment engineer.
- Crew: 3-5 OEM service engineers + plant supervision.

### 6. Time-to-Repair

| Scenario | TTR |
|----------|-----|
| Surge event — inspection only, no damage | 4-8 hours [unverified] |
| Journal bearing replacement (single bearing) | 3-7 days [unverified] |
| Thrust bearing replacement | 2-5 days [unverified] |
| Rotor replacement | 3-10 days (if spare rotor available) [unverified] |
| Rotor repair (balance, weld, machine) | 4-12 weeks [unverified] |

### 7. Plannability

- Compressor surge is not planned — it is an emergency.
- Bearing wear (detected via trend): can often be planned to the next major outage if rates are slow. Vibration trending with API 670 alert/trip levels provides typically 2-8 weeks warning. [unverified]
- Emergency: any time vibration exceeds API 670 trip levels or thrust bearing detects axial displacement.

### 8. Verification / Return-to-Service

1. Pre-start: lube oil system primed, shaft turns freely, all proximeter probe gaps set to OEM specification (typically 0.762 mm = -10V for Bently Nevada system), oil pressure within limits.
2. Start: run at minimum speed for 30 minutes on lube oil — no load.
3. Load step-up: 25% → 50% → 75% → 100%. Check vibration and temperature at each step. Surge line must be respected during all speed changes.
4. Anti-surge system test: perform an ASV functional test before declaring compressor in-service.
5. Full-load steady-state: vibration <25 µm pp (journal), axial within ±0.25 mm of datum. [unverified]

### 9. Recurrence Prevention

- Anti-surge control calibration: verify surge-line coordinates in the control system against OEM test data at least every 2 years.
- Inlet filter health: blocked inlet filters reduce surge margin — replace on schedule (not just condition — steel plant air quality can block filters faster than predicted). [unverified]
- Process coordination: train process operators that compressor minimum load limits must be respected — downstream valve-slamming is a primary surge initiator.
- Online performance monitoring: continuously track the compressor's operating position on the Mollier chart and send an early warning alarm when approaching surge line by 10% margin. [unverified]

---

---

# PLAYBOOK 07 — HYDRAULIC SERVO-VALVE SILTING
## Equipment: AGC (Automatic Gauge Control) hydraulic screwdown cylinders, looper cylinders, side-guide cylinders, rolling-force control

### 1. Detection → Diagnosis

| Indicator | Diagnosis | Instrument |
|-----------|-----------|------------|
| Roll gap control hunting / oscillation | Servo valve spool sticking | SCADA — roll-gap actuator position trend |
| AGC step-response sluggish | Spool partially blocked | Hydraulic test rig or in-situ step-test |
| Hydraulic spool position not matching demand | Valve gain reduced | Position LVDT feedback vs demand |
| Oil cleanliness degrading | Silting source | ISO 4406 particle count — must be ≤15/13/10 for servo valves [unverified] |
| Differential pressure across servo valve filter elevated | Accumulation | DP indicator on servo-valve filter |

Diagnostic sequence:
- Step 1: Review AGC position-error trend. Servo-valve silting signature is: correct response at first move, then increasingly sluggish on small-amplitude, high-frequency commands (the silt plugs the spool's annular gap which is typically 1-3 µm clearance). [unverified]
- Step 2: Take servo-valve hydraulic oil sample. If ISO 4406 cleanliness is >16/14/11, silting is the primary suspect. Particle size distribution: silt = particles 1-5 µm, not caught by standard 10 µm filter.
- Step 3: If accessible, perform a null test: servo valve drive current set to zero; if spool does not return to null (cylinder drifts), internal sticking confirmed.

### 2. Immediate Action

1. Switch AGC to backup mode or manual position lock if available — a stuck servo valve in AGC service causes gauge excursion on the strip and product quality failure.
2. Notify process/quality team of potential gauge disturbance.
3. LOTO hydraulic supply to the affected circuit — servo valves operate at 200-350 bar: high-pressure hydraulic LOTO is safety-critical. [unverified]
4. Take a hydraulic oil sample immediately — capture the contamination state.

### 3. Repair Procedure

**Option A — Servo Valve Cleaning (bench clean)**
1. Remove servo valve from manifold block (tag all electrical connectors with wire number before removal).
2. Transport to clean, dust-free hydraulic bench.
3. Disassemble servo valve per manufacturer's procedure (Moog, Parker, Bosch-Rexroth service manuals). Servo valves are precision instruments — 1-3 µm clearances; absolute cleanliness required.
4. Ultrasonically clean spool, sleeve, and nozzle-flapper components in filtered solvent.
5. Inspect spool and sleeve bore under magnification for scoring. Clearance between spool and sleeve must be within OEM tolerance (typically ≤0.001 mm). If scoring present: replace valve.
6. Reassemble in clean-room conditions; test on hydraulic test bench (measure step response and gain — must match OEM datasheet).
7. Reinstall on manifold.

**Option B — Servo Valve Replacement**
1. Remove failed valve (as above).
2. Install new/rebuilt valve of identical model. Confirm null offset (zero-current position) matches the original — mismatched null causes cylinder bias and AGC offset.
3. Adjust null trim electrically per controller procedure.
4. Flush valve manifold with clean oil before reinstall to prevent immediate re-contamination.

**Oil System Remediation (mandatory alongside valve repair)**
5. Replace all high-pressure servo-valve filters (10 µm and 3 µm absolute). [unverified]
6. Add off-line kidney-loop filtration to servo circuit reservoir: target ISO 4406 ≤15/13/10. [unverified]
7. Check all accumulator bladders for hydraulic oil contamination (burst bladder injects gas — gas in servo circuit causes erratic response).

### 4. Spares Required + Lead Time

| Item | Lead Time |
|------|----------|
| Servo valve (Moog D661 / Parker TDC series or equiv.) | 4-16 weeks (OEM or rebuild house) [unverified] |
| Servo valve filter elements (3 µm, 10 µm) | In stock (minimum 2 sets per servo circuit) |
| Kidney-loop filter unit (portable) | 2-4 weeks [unverified] |
| Hydraulic oil (ISO VG 46 HM) | In stock |

### 5. Tools / Skills / Crew

- Tools: Hydraulic test bench (with pressure and flow measurement), ultrasonic cleaner, clean-room bench, servo-valve null-adjustment kit (precision milliamp calibrator), particle counter, ISO 4406 oil test kit.
- Skills: Hydraulic specialist (servo-valve manufacturer training preferred), instrumentation technician for null adjustment and LVDT calibration.
- Crew: 1-2 hydraulic specialists, 1 instrumentation tech, 1 permit holder.

### 6. Time-to-Repair

| Scenario | TTR |
|----------|-----|
| Valve removal and bench clean (valve reusable) | 4-8 hours [unverified] |
| Valve replacement (spare in stock) | 2-4 hours [unverified] |
| Valve replacement (procure new) | 4-16 weeks [unverified] |

### 7. Plannability

- Silting is gradual — track ISO 4406 particle counts weekly on servo circuits. Rising cleanliness number = upcoming silting. Plan valve clean at next grade-change stop.
- Acute valve seizure = emergency (AGC loss in mill cannot be sustained — strip gauge excursion causes product rejection and may cause strip break).

### 8. Verification / Return-to-Service

1. After valve replacement: perform step-response test — command ±50% of full stroke at 1 Hz; response time and overshoot must match OEM specification.
2. Null offset: verify no cylinder drift at zero-current command.
3. AGC functional test: run strip under AGC, verify gauge profile within ±5 µm tolerance band at steady-state. [unverified]
4. Oil sample: target ISO 4406 ≤15/13/10 within 4 hours of return to service. [unverified]

### 9. Recurrence Prevention

- The single most effective measure: maintain oil cleanliness continuously at ISO 4406 ≤15/13/10 using kidney-loop filtration with 3 µm absolute filters on all servo circuits. Most silting problems disappear entirely with this one measure.
- Oil sampling programme: weekly ISO 4406 particle count on all servo-valve circuits. Automated on-line particle counters (HYDAC, MP Filtri) provide real-time data to SCADA.
- System flush protocol: full system flush after any hydraulic cylinder seal failure or hydraulic hose rupture (these events release debris into the circuit).
- Accumulator bladder inspection: annual inspection — failed bladders release nitrogen bubbles into servo circuits.
- Hydraulic oil change: change oil on acidity/viscosity/cleanliness condition (not calendar interval) — water ingress from cooling system leaks is a primary cleanliness failure cause in steel plants.

---

---

# PLAYBOOK 08 — MILL ROLL SPALLING / ROLL CHANGE
## Equipment: Hot strip mill work rolls and back-up rolls, cold mill work rolls, plate mill rolls

### 1. Detection → Diagnosis

| Indicator | Failure Mode | Instrument / Source |
|-----------|-------------|---------------------|
| Surface quality deviation on strip | Spall mark printing on strip | Quality control — surface inspection camera (ISRA Vision or similar) |
| Strip thickness variation (periodic) | Roll-surface defect — period = πD (roll circumference) | Gauge meter — Fourier analysis of gauge deviation |
| Force / torque spike | Spall propagation or roll scab | Roll-force load cells |
| Vibration at roll-pass frequency | Roll surface damage | Vibration sensor at roll chock |
| Roll grinding report | Pre-existing marks observed in roll shop | Roll grinder profile measurement |
| Visual on roll body | Spalling, thermal crack, corrosion pit | Direct visual (magnifying glass or roll-inspection light) |

Diagnostic sequence:
- Step 1: Review online surface inspection system images — identify if defect on strip has a periodic pitch. Calculate period = πD; match to which roll in the stand is the source.
- Step 2: Take roll surface images (offline roll-inspection light) for the suspected roll.
- Step 3: Classify per AISE (Association of Iron and Steel Engineers) roll defect classification: spall (subsurface crack propagation), fire crack (thermal fatigue), banding/grooves (mechanical), porosity (casting defect).
- Step 4: Measure roll profile on roll grinder to quantify spall depth and area.
- Step 5: Check roll usage log: rolling tonnes since last grind, cooling water quality, cobble history (cobbles impose extreme thermal shock). Most roll spalls are initiated by pre-existing sub-surface defects activated by a cobble or thermal event.

Reference: AISE Technical Report No. 11 (Roll Technology).

### 2. Immediate Action

1. Stop rolling when spall-printed product is identified (cannot reclaim affected strip — notify quality team to segregate).
2. Roll change: swap the affected roll for a prepared roll from the roll shop. For work rolls this should take 15-45 minutes (planned stand changeover equipped with quick-change system). [unverified]
3. For catastrophic spall (large fragment breaking away — risk to mill house): emergency stop; personnel clear of mill house; assess structural damage to screwdown, chocks, and roll housing before restart.
4. Send failed roll to roll shop for inspection and disposition (grind to below spall depth if possible, or condemn).

### 3. Repair Procedure

**Work Roll Change Procedure**
1. Stop mill, raise rolls to maximum gap.
2. Lock out main drives (LOTO); verify backup roll cooling is still flowing (prevents thermal gradient stress during stop). [unverified]
3. Fit roll-change device (dedicated hydraulic roll-change car or side-shifting roll-change mechanism depending on mill design).
4. Remove work roll chock clamps. Slide out work rolls (paired) onto roll-change car.
5. Transfer to roll shop via roll storage track.
6. Load replacement work rolls (pre-set in chocks from roll shop, correct crown and hardness for schedule) into stand.
7. Clamp chocks; verify roll gap and parallelism.
8. Re-enable cooling, re-engage drives.
9. Test roll: roll 1-2 test pieces, check gauge and surface before resuming full production.

**Roll Shop Grind and Restore**
1. Place roll on roll grinder (Waldrich Coburg / Herkules or similar CNC roll grinder).
2. Measure roll profile and spall geometry.
3. Grind to remove spall plus minimum safe margin (typically 3-5 mm below spall depth for work rolls). [unverified]
4. If spall extends below minimum diameter: condemn roll.
5. Achieve surface roughness target per schedule (hot mill WR Ra 0.8-2.0 µm typical; cold mill WR Ra 0.3-1.0 µm). [unverified]
6. Apply correct crown profile (CNC grinder to programme).
7. Ultrasonic test roll after grinding to detect sub-surface cracks (Stresstech ultrasonic roll tester or equivalent).
8. Log roll data into roll management system (diameter, grinding stock used, pass/fail).

**Back-up Roll Change (major maintenance event)**
1. Back-up roll change requires removing the complete upper or lower back-up roll assembly (weight 40-120 tonnes for large hot strip mills). [unverified]
2. Requires plant overhead cranes of 120-200 T capacity. [unverified]
3. Full day or multi-day event. Follow OEM roll-change procedure.
4. Inspect back-up roll chocks, roll neck bearings (tapered roller bearing or 4-row cylindrical bearings), and seals — replace if worn.
5. Return to roll shop for regrind — BUR re-grind cycle typically every 3-6 months depending on tonnage. [unverified]

### 4. Spares Required + Lead Time

| Item | Lead Time |
|------|----------|
| Work rolls (prepared, in-house roll shop) | In stock (prepared inventory — typically 2-5 rolls per stand) |
| Work rolls (new from supplier — HSS or high-chrome iron) | 12-26 weeks [unverified] |
| Back-up roll (new) | 26-52 weeks [unverified] |
| Roll chock bearings (large tapered/cylindrical) | 8-20 weeks [unverified] |
| Roll chock seals | 4-8 weeks [unverified] |

### 5. Tools / Skills / Crew

- Tools: Roll-change car, overhead crane (full-weight capacity), CNC roll grinder, ultrasonic roll tester, roll profile gauge (contact or optical), roll surface inspection light, chock press.
- Skills: Roll-shop operator (CNC grinding), millwright (chock assembly/disassembly), crane operator, metallurgist (roll disposition decision), NDT technician (UT testing).
- Crew: 3-5 mill crew (roll change), 2 roll shop operators (grinding), 1 maintenance engineer + 1 metallurgist (disposition).

### 6. Time-to-Repair

| Scenario | TTR |
|----------|-----|
| Work roll change (quick-change mill, hot strip) | 15-45 minutes [unverified] |
| Work roll change (older plate mill without quick change) | 2-4 hours [unverified] |
| Work roll grind (minor) | 2-4 hours [unverified] |
| Back-up roll change | 8-24 hours [unverified] |
| Back-up roll regrind | 8-16 hours on grinder [unverified] |

### 7. Plannability

- Work roll spall detected online: plan roll change to next available gap (cobble stop, grade change, end of coil) — cannot defer if strip quality is being affected.
- Minor fatigue cracking visible in roll shop inspection: plan roll change before it propagates to spall.
- Back-up roll change: plan to major scheduled maintenance outage. Cannot easily emergency-change — 8-24 hour event even with good preparation.

### 8. Verification / Return-to-Service

1. New work rolls: verify crown profile matches schedule spec before insertion into stand (roll shop measurement).
2. After roll change: run 1-2 test coils through gauge measurement to confirm gauge profile is on-target.
3. Check roll cooling water flow and spray pattern (blocked nozzles contribute to thermal crown and thermal fatigue).
4. Surface inspection system: verify alarm-free for first 10 minutes of rolling after roll change.

### 9. Recurrence Prevention

- Roll thermal management: maintain consistent cooling water supply, flow rate, and temperature (contaminated cooling water with high dissolved solids accelerates thermal cracking). [unverified]
- Cobble protocol: after every cobble, inspect roll surfaces before resuming production — fire cracks from cobble thermal shock are the primary spall initiator.
- Roll schedule: implement data-driven roll change frequency (condition monitoring vs fixed-tonnage schedule). Use online surface inspection data to catch spall at earliest stage.
- HSS (High Speed Steel) roll campaign: HSS work rolls have 3-5x the wear resistance of high-chrome iron for hot-strip finishing stands — justify the higher roll cost against reduced change frequency and improved surface quality. [unverified]
- Ultrasonic roll inspection frequency: inspect all work rolls ≥ every 2 campaign-grinds using automated ultrasonic tester. Early sub-surface crack detection is the only way to prevent spall.

---

---

# PLAYBOOK 09 — CONTINUOUS CASTER: SEGMENT / MOULD / BREAKOUT
## Equipment: Continuous casting machine — mould, strand guide segments, withdrawal rolls, liquid steel handling

### 9A — MOULD COPPER WEAR / MOULD LEVEL OSCILLATION FAULT

#### 1. Detection → Diagnosis

| Indicator | Failure Mode | Instrument |
|-----------|-------------|------------|
| Mould level oscillation amplitude increasing | Worn copper, oscillation drive fault, or SEN erosion | Mould level sensor (electromagnetic or radioactive) |
| Mould copper temperature deviation (thermocouple array) | Hot band = channel erosion, crack, or sticking | Embedded thermocouples (Accuflow or equivalent) |
| Mould powder consumption (kg/t) anomaly | SEN breakage, powder clogging | Manual tracking + SCADA |
| Mould taper mismatch | Worn or deformed copper plates | Mould geometry measurement (manual or automated) |
| Visual: surface defects on slab | Oscillation marks depth inconsistency, longitudinal cracks | Slab inspection post-caster |

Diagnostic sequence:
- Step 1: Review mould level trace (standard deviation of level should be <±2 mm steady-state). Gradual increase = SEN (Submerged Entry Nozzle) erosion widening the casting channel. Sudden step = SEN partial blockage (Al₂O₃ clogging). [unverified]
- Step 2: Check mould thermocouple array — if a hot band (row with temperatures 20-40 °C above neighbours) develops at a consistent position, it indicates copper wall erosion forming a groove. [unverified]
- Step 3: Review oscillation drive data: stroke, frequency, and waveform. If waveform deviates from sinusoidal (for electro-mechanical oscillators) or from programmed profile (for hydraulic oscillators), drive system fault is likely.
- Step 4: After heat: remove mould and inspect copper plates under lighting — measure groove depth (>3 mm = change required per most plants' internal SOP). [unverified]

#### 2. Immediate Action

1. Mould level oscillation increasing with no SEN change possible mid-heat: raise casting speed slightly (sometimes stabilises level) OR call end of heat early.
2. If mould level alarm cannot be controlled: initiate controlled end-of-heat. Do not continue casting into an unstable mould level regime — breakout risk increases dramatically. [unverified]
3. Post-heat: take mould out of service; do not transfer to next ladle without inspection if anomaly was observed.

#### 3. Repair Procedure (Mould Maintenance)

1. Remove mould from machine after heat.
2. Disassemble copper plates from water box. Clean copper surfaces.
3. Measure copper plate thickness at grid of measurement points (contact gauge or CMM). Compare to minimum thickness per OEM (new plate is typically 35-50 mm; minimum before replace is ~25-30 mm). [unverified]
4. Inspect for grooves, cracks, inclusions embedded in copper.
5. If within tolerance: re-nickel-plate (electroplating) the copper surface to restore wear resistance; coat groove with hard chrome or Ni overlay if shallow. This is done at the roll shop or by outside specialist. [unverified]
6. If below minimum thickness or cracked: replace copper plates.
7. Reassemble mould; check mould taper per schedule specification using taper-measurement gauge. Adjust taper bolts to correct value.
8. Verify all thermocouple positions and continuity.
9. Leak test mould water circuit (pressure test at 1.5× working pressure for 10 min). [unverified]
10. Measure mould corner distortion — corners are high-wear areas; if distorted >0.5 mm: return for re-machining. [unverified]

### 9B — CASTER SEGMENT FAILURE

#### 1. Detection → Diagnosis

| Indicator | Failure Mode | Instrument |
|-----------|-------------|------------|
| Strand guide force deviation | Roll seized, worn, or bracket failure | Hydraulic segment force sensors |
| Roll rotation monitoring | Roll not rotating | Encoder or proximity switch on segment rolls |
| Slab surface defects (transverse cracks) | Segment misalignment or seized rolls | Slab inspection |
| Cooling water flow alarm in specific zone | Spray nozzle blocked or pipe cracked | Zone-specific flow meter |
| Visible slab bulging | Segment gap opened beyond spec | Strand guide position measurement |

Diagnostic sequence:
- Step 1: Review segment force and roll rotation logs. A seized roll will show no encoder pulses and elevated contact force (or paradoxically low force if roll has broken away). [unverified]
- Step 2: Slab surface inspection — transverse surface cracks at regular pitch = seized roll printing. The pitch equals the roll circumference (π × roll diameter).
- Step 3: Cooling water flows per zone — sudden drop = nozzle blockage or cooling pipe fracture. In steel plant water conditions (high dissolved solids), nozzle blockage by scale is very common.

#### 2. Immediate Action

1. Seized roll in a segment: cannot be cleared in-situ. Reduce casting speed if segment is in the unbent zone (still liquid core) to reduce strand guide forces.
2. Blocked spray cooling in a zone: attempt to clear by cycling the zone valve; if cooling remains absent, reduce casting speed or adjust secondary cooling recipe to compensate with adjacent zones.
3. If segment damage is severe (bracket failure, roll fallen off, strand is unsupported): emergency stop the caster. Risk of breakout is high when strand guide fails.
4. After emergency stop: follow caster dummy-bar insertion procedure to restart or follow cast-off procedure to safely drain the remaining liquid steel.

#### 3. Repair Procedure (Segment Change)

1. Stop casting; allow strand to cool sufficiently (typically 2-4 hours before entering segment bay). [unverified]
2. Withdraw segment using segment-handling crane (segments weigh 10-50 T depending on caster size). [unverified]
3. In segment repair bay:
   - Inspect all rolls for seizure, flatting, or surface damage.
   - Measure roll diameters at multiple positions — measure taper wear. Replace if wear >2 mm OD. [unverified]
   - Replace roll bearings (always — cost of bearing is small vs segment re-pull cost if bearing fails in service).
   - Inspect and clean all cooling nozzles. Replace blocked/eroded nozzles.
   - Check segment frame geometry — check gap between upper and lower frames against schedule using feeler gauges / OEM fixture. Adjust (shim or precision-grind) to restore correct geometry.
   - Inspect tie-rod and hydraulic cylinder for corrosion/seal damage.
4. Reinstall refurbished segment. Torque all tie-rod nuts per OEM. Set gap per schedule casting format (narrow/wide slab).
5. Pressure-test segment cooling circuit.

### 9C — BREAKOUT RESPONSE

#### 1. Detection → Diagnosis

A breakout is the escape of liquid steel through a shell breach below the mould. It is one of the most dangerous and costly events in a steel plant.

| Indicator | Alarm Type | Instrument |
|-----------|-----------|------------|
| Breakout prediction system (BPS) alarm — thermocouple pattern indicating shell thinning | Early warning — typically 60-90 seconds before shell rupture | Dedicated BPS algorithm (EBLD — Expert Breakout Detection by Siemens/Danieli, or similar) |
| Mould level drop below lower limit | Shell hanging or breakout has occurred | Mould level sensor |
| Caster floor temperature sensors | Liquid steel reached machine floor | IR or thermocouple |
| Operator visual | Glow from strand guide / liquid steel visible on floor | Operator on CCTV or floor |

#### 2. Immediate Action — BREAKOUT EMERGENCY RESPONSE

1. BPS alarm: IMMEDIATELY reduce casting speed to minimum (sometimes can "heal" the breakout by reducing ferrostatic pressure). If BPS alarm escalates — stop casting NOW (stop withdrawal, stop tundish flow).
2. Full emergency stop of caster: stop withdrawal roll drive; close tundish sliding gate.
3. Emergency evacuation: all personnel clear caster floor — liquid steel contact is fatal. Activate site emergency alarm. [unverified]
4. Ladle slide-gate close — do NOT continue to fill tundish.
5. DO NOT operate any equipment in the affected bay until liquid steel is confirmed solidified and cooled (minimum 4-6 hours for large breakouts — can be 24+ hours). [unverified]

#### 3. Repair Procedure (Post-Breakout)

1. Safety inspection: after cooldown confirmed by thermal camera and physical observation, entry only with full PPE (full face shield, proximity heat protection).
2. Remove solidified steel skull from strand guide — may require gas cutting, hydraulic equipment, and extended manual breaking.
3. Inspect all segments in the breakout zone for damage (steel infiltration, warped frames, damaged cooling pipes).
4. Replace all damaged segments and rolls in the affected zone.
5. Clean all cooling nozzles (scale buildup from evaporated cooling water during the thermal event).
6. Check structural integrity of caster building — breakouts can cause spalling of concrete and structural damage.
7. Full recommissioning run before next heat.

### 4. Spares Required + Lead Time (combined)

| Item | Lead Time |
|------|----------|
| Mould copper plates (standard format) | 8-20 weeks [unverified] |
| Mould copper plates (non-standard format) | 20-40 weeks [unverified] |
| Strand guide rolls (standard diameters) | 6-16 weeks [unverified] |
| Segment complete (rebuild or new) | 16-52 weeks [unverified] |
| SEN (Submerged Entry Nozzle) | In stock (consumable — keep 5-10 spares) |
| Segment roll bearings | Keep on shelf per segment type |
| Spray nozzles (standard) | In stock (consumable) |

### 5. Tools / Skills / Crew

- Segment crane, segment repair bay (equipped with wash bay + assembly jacks), CMM or segment gap fixture, nozzle pressure tester, mould taper gauge, copper plate measurement tools, electroplating facility (on-site or contracted).
- Skills: Caster maintenance crew (specialised — combines millwright, hydraulics, metrology), metallurgist (breakout RCA), safety officer (breakout recovery).
- Crew: 4-8 caster maintenance fitters (segment change), 2 metallurgists, 1 shift manager for breakout events.

### 6. Time-to-Repair

| Scenario | TTR |
|----------|-----|
| Mould change (planned, between heats) | 10-30 minutes [unverified] |
| Mould copper plate replacement (off-machine) | 4-8 hours [unverified] |
| Segment change (single) | 4-8 hours [unverified] |
| Breakout recovery (minor, localised) | 24-48 hours [unverified] |
| Breakout recovery (major, multi-segment damage) | 3-14 days [unverified] |

### 7. Plannability

- Mould copper wear / SEN change: planned (heat-to-heat gaps are the natural window).
- Segment change: planned to maintenance shutdown (typically weekly or fortnightly caster maintenance window).
- Breakout: by definition, unplanned emergency. BPS systems reduce frequency but cannot eliminate breakouts.

### 8. Verification / Return-to-Service

1. Mould: leak test, thermocouple continuity test, taper verification, BPS calibration check.
2. Segment: gap measurement, cooling water flow test per nozzle, roll rotation test.
3. First heat after maintenance: run at 60-70% casting speed for first 15 minutes with enhanced monitoring. [unverified]
4. BPS system: verify alarm thresholds are active before first heat.

### 9. Recurrence Prevention

- BPS tuning: refine BPS alarm thresholds based on the thermocouple response data from actual breakouts — do not reduce sensitivity to eliminate nuisance trips (a nuisance trip is far cheaper than a breakout).
- Mould powder management: correct mould powder for the steel grade is critical to shell lubrication. Steel grade changes must include powder changes per the metallurgical procedure.
- SEN quality control: inspect SENs at goods receipt. Cracked or undersized SENs cause asymmetric flow and shell thinning on one face.
- Cooling water quality: scale deposits on cooling channels reduce heat transfer, increasing shell temperature and breakout risk. Implement water treatment (corrosion inhibitor + scale inhibitor) and annual descaling of mould water circuits.
- Post-breakout RCA: every breakout must have a formal 5-whys root-cause analysis completed within 48 hours. Common root causes (in approximate order of frequency at most plants): mould level instability → shell re-melt, improper taper → shell sticking, SEN blockage → uneven shell growth, missed BPS alarm, cooling water failure. [unverified]

---

---

# PLAYBOOK 10 — CONVEYOR IDLER / BELT FAILURE
## Equipment: Ore conveyor, coal conveyor, sinter conveyor, pellet conveyor, scrap conveyor

### 1. Detection → Diagnosis

| Indicator | Failure Mode | Instrument |
|-----------|-------------|------------|
| Idler noise (squealing, grinding, thumping) | Seized idler bearing | Operator walk-down, acoustic monitoring (SDT270) |
| Idler temperature >80 °C | Dry/failed bearing | IR thermometer on idler shell |
| Belt tracking deviation | Misaligned idlers, damaged idler, or belt splice damage | Belt tracking monitors / CCTV / operator |
| Belt surface damage (cuts, rips, transverse cracks) | Impact damage at loading zone, or idler seizure causing rub | Rope detection sensor or operator |
| Drive motor current spike | Belt jamming or excessive friction | Motor current SCADA trend |
| Belt sag / low tension | Broken or missing carrying idlers in a section | Visual / tension measurement |

Diagnostic sequence:
- Step 1: Walk the belt with IR thermometer on all idler shells. Seized idlers are the #1 cause of belt fires — a seized idler running hot under a rubber belt is a fire initiator.
- Step 2: Check belt tracking at head and tail pulleys. Mistrack >50 mm at belt edge = investigate idler alignment or belt curvature in that section. [unverified]
- Step 3: Inspect belt surface at loading zone (impact zone) and transfer points — these are primary cut and puncture locations.
- Step 4: Check belt splice condition (mechanical fasteners or vulcanised — check for opening fasteners or delamination at edges).

### 2. Immediate Action

1. Seized/hot idler: stop belt IMMEDIATELY. A smoking or fire-adjacent idler under a loaded belt loaded with coal or organic material is a fire risk. Follow plant fire watch protocol.
2. Belt fire confirmed: activate fire suppression system (CO₂ or foam), stop all adjacent conveyors, call emergency response team.
3. Belt mistracks heavily (>100 mm at edge): stop belt — serious edge damage or belt loss off structure is imminent.
4. LOTO: conveyor drives are high-stored-energy systems — belt tension means the belt can move unexpectedly even with drive stopped. Install physical belt-tension locks or jacks before entry into guarded zones.

### 3. Repair Procedure

**Idler Replacement (most common repair)**
1. Stop belt and LOTO.
2. Lift belt at the idler location using belt lifter or pry bar (never put hands under loaded belt).
3. Remove idler from carrying frame — most idlers are snap-in or pin-retained.
4. Fit replacement idler of correct size (belt width matched, trough angle, load rating).
5. Confirm idler rotates freely before installing.
6. Lower belt; confirm correct position.
7. Restart belt; check idler is rotating (walk the first run).

**Belt Splice Repair (vulcanised)**
1. Stop belt; allow tension to be safely removed (use belt clamps or brakes on the take-up).
2. Prepare joint faces per vulcanising kit specification: cut away damaged splice section, bevel belt carcass to taper, apply skim coat of adhesive.
3. Lay new ply strips; cover with rubber; apply heat and pressure using vulcanising press per time/temperature cycle (typical 145 °C for 20-30 min for standard conveyor rubber). [unverified]
4. Allow to cure; trim excess; inspect bond.
5. Re-tension belt per manufacturer specification.

**Belt Repair (cut/puncture — cold repair)**
1. Clean damaged area; cut away fraying rubber to clean edge.
2. Apply cold-bond repair kit (3M or Fenner Dunlop equivalent) — roughen surface, apply adhesive, press patch.
3. Allow cure time per kit specification (8-24 hours at ambient; faster with localized heat). [unverified]
4. Cold repairs are temporary for large cuts — plan vulcanised repair or belt replacement.

**Belt Replacement**
Major event — requires pre-cut belt roll, multiple splices, and coordinated crew.

### 4. Spares Required + Lead Time

| Item | Lead Time |
|------|----------|
| Standard idlers (carrying, return, impact) | In stock (bulk — minimum 2% of installed count) [unverified] |
| Specialised idlers (garland, discenter, training) | 2-6 weeks [unverified] |
| Belt vulcanising kit (per type) | In stock |
| Cold-repair patch kit | In stock |
| Replacement belt section (per width/rating) | 4-16 weeks (belt is made-to-order for specific width/strength/cover) [unverified] |

### 5. Tools / Skills / Crew

- Tools: IR thermometer, belt lifter, idler replacement trolley (for heavy idlers), vulcanising press, belt clamps, splicing tools, tension gauge.
- Skills: Conveyor technician (idler work is semi-skilled; vulcanising requires specialist training and qualification), fire warden for hot idler response.
- Crew: 1-2 technicians for idler replacement, 2-3 for belt splice, fire team if hot idler.

### 6. Time-to-Repair

| Scenario | TTR |
|----------|-----|
| Single idler replacement | 15-30 minutes [unverified] |
| Vulcanised belt splice | 3-8 hours (including cure time) [unverified] |
| Cold repair (temporary) | 1-2 hours [unverified] |
| Belt section replacement (full length) | 1-3 days depending on belt length [unverified] |

### 7. Plannability

- Idler replacement: routine maintenance — any seized idler should be changed within one shift. Bulk idler change of a whole section can be planned to a shutdown.
- Belt splice: can usually be planned to night shift or weekend outage. Emergency if belt has broken.
- Belt fire: immediate emergency — no plan.

### 8. Verification / Return-to-Service

1. After idler replacement: run belt one complete circuit; walk all new idlers confirming they are rotating.
2. After belt splice: run 30 minutes at load; inspect splice for delamination or opening.
3. Tracking check: confirm belt remains centred through the repaired section under loaded conditions.

### 9. Recurrence Prevention

- Thermal monitoring: mount fixed IR cameras or FLIR sensors at points between inspection intervals to auto-detect hot idlers (>65 °C) before they become fire risks.
- Idler replacement program: replace idlers at end of calculated life (typically 50,000-80,000 hours for quality idlers in moderate conditions) — do not run to failure in fire-risk material service. [unverified]
- Loading zone maintenance: maintain rubber impact bars and skirt boards at loading zones — most belt cuts originate from exposed metal at loading points.
- Belt alignment: quarterly alignment check of all idler sets — misaligned idlers cause edge wear and belt wander.

---

---

# PLAYBOOK 11 — CRANE WIRE ROPE / BRAKE FAILURE
## Equipment: Overhead travelling cranes (melt shop, caster bay, rolling mill), ladle cranes, scrap charging cranes

### 1. Detection → Diagnosis

**Wire Rope**

| Indicator | Criterion | Method |
|-----------|-----------|--------|
| Visible broken wires per lay length | ≥5% of total wires broken in any rope lay = replace (ISO 4309:2017 / EN 12385-4) | Manual visual inspection + magnifying glass |
| Corrosion pitting on outer wires | Severe pitting reducing cross-section | Visual |
| Core protrusion ("birdcaging") | Rope unserviceable immediately | Visual |
| Rope diameter reduction | >3% reduction from nominal (ISO 4309 criterion) | Vernier caliper measurement at multiple points |
| Kinked, crushed, or sharply bent section | Remove from service immediately | Visual |
| Magnetic rope tester (MRT) result | Loss of Metallic Area (LMA) >10% in any section | MRT instrument (Waygate Technologies MRT or equivalent) |

**Brake**

| Indicator | Failure Mode | Instrument |
|-----------|-------------|------------|
| Brake pad thickness | <50% of new thickness = replace (typically new = 20 mm; replace at 10 mm) [unverified] | Manual measurement |
| Brake drum temperature | >120 °C after normal operation = glazed or dragging [unverified] | IR thermometer |
| Brake torque test | Fails to hold rated load at standstill | Load test |
| Brake release time | >OEM specification = solenoid or spring fault | Timer at brake |
| CCTV or visual: load drift with brake applied | Brake slipping | Observation |

#### 2. Immediate Action

1. If wire rope inspection reveals >5% broken wires in any lay: take crane out of service immediately. Do NOT use for any lift.
2. If brake test fails: take crane out of service. A crane with a slipping brake handling molten steel is a fatality risk.
3. Notify lifting/inspection authority (at Tata Steel sites, this falls under regulatory crane inspection regime — crane is out of service until inspection and repair is certified by a Competent Person per relevant national regulation, e.g. OSHA 1910.179 in USA, Factories Act in India). [unverified]
4. If load is suspended when rope/brake fault is discovered: lower load to ground under manual control (using alternative means if primary brake is failed) before taking crane out of service. DO NOT leave load suspended.

#### 3. Repair Procedure

**Wire Rope Replacement**
1. LOTO crane — lock out all motions; apply mechanical travel stop to prevent runway movement.
2. Lower hook block to ground (on blocking); remove dead-end rope anchor.
3. Unspool old rope from drum using rope reel device.
4. Inspect drum grooves for wear; measure drum groove depth (if worn >3 mm: replace drum or re-machine grooves). [unverified]
5. Inspect sheave grooves (D-shape wear indicates rope wear). Replace sheaves if groove diameter has worn >0.5 mm oversize. [unverified]
6. Reeving new rope: feed from new rope reel; reeve through all sheaves per crane reeving diagram (must be correct reeving — wrong reeving causes cross-loading). Mark the rope at the dead end for correct fleet angle.
7. Make dead-end termination: wedge socket (preferred) or swagged thimble. Rope clips only as temporary — never permanent for overhead crane rope end. [unverified]
8. Tension rope: run hook block up and down several times with light load to seat rope in grooves.
9. Measure fleet angle: must be <4° (each side of the sheave centre line). Greater angle causes accelerated rope wear. [unverified]

**Brake Reline / Brake Service**
1. Access brake housing (LOTO; motor de-energised and thruster released — never work on brake with motor energised).
2. Remove old brake pads (shoes or disc pads depending on type).
3. Measure brake drum/disc diameter — if drum is worn out-of-round >0.1 mm, or cracked: replace. [unverified]
4. Fit new brake pads of correct material (rated torque capacity ≥ brake torque specification).
5. Set brake air gap to OEM specification (typical 0.5-1.0 mm for electromagnetic thrusters). [unverified]
6. Verify brake spring pre-load per OEM (spring pre-load determines holding torque — under-torqued spring = under-braking = load drift).
7. Perform static brake test: apply load equal to rated SWL; brake must hold without drift for 5 minutes. [unverified]
8. Log test result in crane maintenance record.

### 4. Spares Required + Lead Time

| Item | Lead Time |
|------|----------|
| Wire rope (per crane type and length) | 2-8 weeks (custom length/spec) [unverified] |
| Rope sockets (wedge type) | In stock |
| Brake pads (per brake type) | 2-6 weeks [unverified] |
| Brake drum | 6-16 weeks [unverified] |
| Sheave set | 4-12 weeks [unverified] |
| Brake thruster (electric/hydraulic) | 4-10 weeks [unverified] |

### 5. Tools / Skills / Crew

- Tools: Rope-pull reel/capstan, wedge socket press, sheave puller, brake adjustment tools, dynamometer (load cell) for brake test, Vernier calipers, MRT instrument (magnetic rope tester) for inspection.
- Skills: Crane inspector (Competent Person — legally required in most jurisdictions for wire rope inspection and crane certification), rigger (for rope reeving), mechanical fitter (brake).
- Crew: 2-3 riggers/fitters, 1 Competent Person (inspector), 1 permit holder / supervisor.

### 6. Time-to-Repair

| Scenario | TTR |
|----------|-----|
| Wire rope replacement (single-fall hoist) | 4-8 hours [unverified] |
| Wire rope replacement (multi-fall reeving, large ladle crane) | 8-24 hours [unverified] |
| Brake reline + test | 2-6 hours [unverified] |
| Sheave replacement (accessible) | 4-8 hours [unverified] |

### 7. Plannability

- Wire rope: planned replacement on condition (MRT) or at fixed service life interval (typically 12-18 months in harsh steel plant conditions). Emergency if criterion exceeded in inspection. [unverified]
- Brake: planned reline on pad-thickness condition or at 12-month service interval. Emergency if load drift observed during operation.
- Never defer emergency rope or brake issues on cranes handling molten steel — consequences are fatal.

### 8. Verification / Return-to-Service

1. Wire rope: visual inspection of all installed rope, correct reeving confirmed per diagram, all terminations checked.
2. Brake: static load test (rated SWL held for 5 min), dynamic test (rated SWL lifted and stopped, no drift).
3. Crane functional test: test all motions (hoist up/down, traverse, travel) at no-load and at rated SWL.
4. Crane re-certification by Competent Person — documentation required before returning to service on molten-metal duty. [unverified]

### 9. Recurrence Prevention

- MRT programme: quarterly MRT inspection of all crane wire ropes in melt-shop and caster service (high-temperature, corrosive environment accelerates wire rope degradation). [unverified]
- Lubrication: apply wire-rope lubricant on a 3-month cycle (in hostile environments) — dry rope has 30-50% shorter life than properly lubricated rope. [unverified]
- Brake inspection: monthly visual check of brake pad thickness on all duty cranes. Add to operator pre-shift checklist.
- Load path design: review reeving diagram — poor fleet angles and small drum-to-rope-diameter ratios (D/d <12) significantly accelerate rope fatigue. [unverified]
- Training: crane operators must report any unusual noises, drifting, or slow brake response immediately — early reporting is the primary defence against catastrophic failure in this equipment class.

---

---

# PLAYBOOK 12 — FURNACE REFRACTORY / COOLING BEAM FAILURE
## Equipment: Reheating furnace (pusher, walking-beam), blast furnace, BOF/EAF linings, ladle linings

### 1. Detection → Diagnosis

**Refractory Wear**

| Indicator | Failure Mode | Instrument / Method |
|-----------|-------------|---------------------|
| Shell thermocouple temperature rising | Refractory thinning in that zone | Thermocouple array on furnace shell |
| Hot spot on furnace shell (IR survey) | Refractory breach, or cooling-beam water circuit failure | Periodic IR camera survey |
| Fuel/gas consumption rising at constant output | Thermal efficiency falling = refractory degradation | Fuel flow meters vs throughput |
| Stack temperature rising | Heat escaping through degraded lining | Stack temperature thermocouple |
| Flue gas composition change (high unburned) | Refractory scaling and product retention | Gas analyser |

**Cooling Beam Failure (walking-beam furnace)**

| Indicator | Failure Mode | Instrument |
|-----------|-------------|------------|
| Steam generation from beam area | Beam water tube cracked — water entering furnace | Visual (water evaporation) + furnace atmosphere alarm |
| Beam cooling water return temperature spike | Partial blockage or reduced flow | Return temperature sensor |
| Beam cooling flow drop | Tube cracked, blocked, or fitting leaked | Flow meter |
| Water-in-furnace atmosphere: dew point change | Significant beam failure | Flue gas moisture analyser |

Diagnostic sequence:
- Step 1: Review shell thermocouple trends — a single thermocouple rising 50-100 °C above neighbours indicates localised refractory loss at that position. Map the thermal profile.
- Step 2: If IR camera survey shows a hot spot: precisely locate it on the furnace geometry map. Compare to last refractory thickness measurement (invasive probe or neutron backscatter measurement).
- Step 3: For cooling beams, check water-flow balance on all beam circuits. A cracked beam will show elevated water consumption (the water is entering the furnace and evaporating). Compare total water-in vs total water-out flow on the cooling circuit.
- Step 4: Review operational history: has this zone handled scale-heavy or wet product? Has there been a furnace trip causing rapid thermal cycle? These are primary refractory failure initiators.

### 2. Immediate Action

**Refractory Hot Spot**
1. Reduce furnace temperature setpoint in the affected zone by 50-100 °C — reduces thermal load on remaining lining.
2. If shell temperature reaches structural-integrity concern level (plant-specific — typically >350 °C for carbon-steel shell in a standard reheating furnace): initiate furnace shutdown procedure for emergency relining. [unverified]
3. Notify metallurgy — reduced zone temperature will affect slab heating profile and may require rolling mill schedule adjustment.

**Cooling Beam Failure**
1. Water-in-furnace is dangerous — steam explosions can occur in furnace if the beam failure is large. Shut down the affected beam circuit.
2. If the beam failure is significant: initiate furnace shutdown — cannot safely continue operation with major cooling beam failure.
3. Reduce throughput immediately; avoid pushing cold/wet stock into a furnace with compromised cooling.

### 3. Repair Procedure

**Emergency Refractory Patch (minor area, furnace at temperature)**
1. For small spalls (<200 × 200 mm) accessible through a furnace door: apply gunite (refractory gunning mix) using a compressed-air gunning machine. Suitable anchor materials and mixes must be compatible with the furnace atmosphere and temperature. [unverified]
2. Furnace continues running at reduced throughput/temperature while patch cures.

**Major Refractory Repair / Relining (shutdown required)**
1. Cool furnace — controlled cooling rate must be followed (typically maximum 50 °C/hour descent to avoid thermal shock to remaining good lining and furnace shell). [unverified]
2. Full cool-down to ambient: 24-48 hours for a large reheating furnace. [unverified]
3. Scaffold inside furnace.
4. Remove damaged refractory by hand-breaking and pneumatic demolition. Hot face materials at this stage: castable refractory or fired brick depending on zone.
5. Clean shell; inspect steel shell for corrosion, cracks, or thermal distortion.
6. Install anchors for new lining (Y-type or V-type Inconel anchors for high-temperature zones). [unverified]
7. Cast or brick new lining to design thickness (hot-face brick: ISO 2000 quality or better for reheating furnace work zone). [unverified]
8. Back-fill with insulating castable behind hot-face.
9. Dry-out and cure: slow heat-up per manufacturer's dry-out curve (critical — too-fast dry-out causes steam-explosion cracking). Typical dry-out: 24 °C/h to 200 °C; hold 8 h; 50 °C/h to operating temperature. [unverified]

**Cooling Beam Repair**
1. Cool furnace (as above for major shutdown).
2. Remove damaged beam from furnace (beams are removable on most modern walking-beam designs via plug welds and flanged connections).
3. Transport to workshop.
4. Pressure-test beam at 1.5 × working pressure to locate leak.
5. Weld repair crack (specialist high-temperature alloy welding) or replace beam tube section.
6. Recoat with refractory protection if applicable.
7. Reinstall beam; reconnect cooling circuit; pressure-test in-situ before furnace start.

### 4. Spares Required + Lead Time

| Item | Lead Time |
|------|----------|
| Gunite / gunning mix (50 kg bags) | In stock (keep 20-50 bags per furnace) [unverified] |
| Refractory bricks (IFB, dense fireclay, AZS, SiC) | 4-12 weeks (standard) / 16-26 weeks (fused-cast) [unverified] |
| Castable refractory (low-cement, self-flow, gunning) | 4-8 weeks [unverified] |
| Cooling beam spare (identical) | 8-20 weeks [unverified] |
| Anchor materials (Inconel Y-type) | 4-8 weeks [unverified] |
| Ceramic fibre module (for top/door repairs) | 2-6 weeks [unverified] |

### 5. Tools / Skills / Crew

- Tools: Refractory gunning machine, pneumatic demolition tools, IR camera (for survey), neutron backscatter refractory measurement probe (specialist tool), casting moulds, vibrator for castable, thermal couples for dry-out monitoring, welding set (Inconel-capable).
- Skills: Refractory mason (specialist), refractory engineer (dry-out management), welder (P91/Inconel for beam repair), scaffold erector.
- Crew: 6-20 refractory masons for major relining, 1-2 engineers, scaffold crew.

### 6. Time-to-Repair

| Scenario | TTR |
|----------|-----|
| Gunite patch (minor, furnace running) | 2-4 hours [unverified] |
| Major zone relining | 7-21 days (cool-down + demolition + reline + dry-out) [unverified] |
| Cooling beam repair | 3-7 days [unverified] |
| Full reheating furnace relining | 4-8 weeks [unverified] |

### 7. Plannability

- Refractory condition monitoring (thermocouple trending + annual IR survey + annual thickness measurement): enables planned relining at a major shutdown, avoiding emergency.
- Hot spot at critical threshold: emergency. No safe deferral when shell integrity is at risk.
- Cooling beam failure: emergency.

### 8. Verification / Return-to-Service

1. Complete dry-out per manufacturer's curve — do not rush. Document temperatures at each thermocouple during heat-up.
2. Furnace integrity check: no steam puffing from joints, no visible cracking.
3. Perform operational trial at 70% load for first 2 hours — monitor shell temperatures vs pre-repair baseline.
4. Slab temperature uniformity: confirm heating curves are met per metallurgical spec.

### 9. Recurrence Prevention

- Online shell-temperature monitoring: permanently install thermocouple array on furnace shell with SCADA alarming. Trend-based alerts catch refractory degradation 4-8 weeks before emergency. [unverified]
- Post-campaign analysis: photograph all hot-face surfaces at every shutdown. Build a photo-documentation database — refractory wear patterns are highly predictable if tracked systematically.
- Dry wet/cold stock: avoid charging very cold or wet billets/slabs — thermal shock is a primary cracking initiator.
- Cooling water quality (beams): implement scale-inhibitor treatment in cooling beam water circuits. Scale buildup reduces cooling efficiency and increases beam tube temperatures — primary cause of beam fatigue cracks.

---

---

# PLAYBOOK 13 — ELECTRODE / LANCE FAILURE (EAF / BOF / LMF)
## Equipment: Electric Arc Furnace (EAF) graphite electrodes, BOF oxygen lance, Ladle Metallurgy Furnace (LMF) electrodes, argon/nitrogen stirring lances

### 13A — EAF GRAPHITE ELECTRODE FAILURE

#### 1. Detection → Diagnosis

| Indicator | Failure Mode | Instrument |
|-----------|-------------|------------|
| Electrode stub visible after fracture | Electrode break due to thermal shock, mechanical impact, or over-current | CCTV in furnace bay + operator visual |
| Arc instability (voltage/current oscillation) | Electrode length change or partial fracture | Electrode regulation system trend |
| Electrode consumption rate rising | Grade degradation or over-oxidation from poor gas protection | Tonnes/electrode tracking in furnace PLC |
| Nipple connection joint visible (over-consumption to nipple zone) | Electrode column consumed to joint | Visual at electrode guard ring |
| EAF mechanical vibration event log | Electrode dropped/impacted during scrap charging | Event log |

Diagnostic sequence:
- Step 1: Any sudden change in arc regulation system output (rapid electrode position change) during melting indicates a broken electrode or scrap cave-in event. Stop melting, visually check electrode stub positions through slag door.
- Step 2: Review electrode current balance across three phases — a broken stub will cause arc asymmetry and significant single-phase overcurrent.
- Step 3: Post-heat: raise electrodes above bath, inspect electrode columns through furnace camera — measure remaining stub length.

#### 2. Immediate Action

1. Broken electrode in heat: power-off to the affected phase immediately. Do not continue to arc on the broken stub — the stub can fall into the bath causing arc shorts, equipment damage, or spatter injury.
2. Remove remaining stub from column (if safe to access). Fit replacement electrode and add to column.
3. If only one phase is broken: it may be possible to melt on two-phase (reduced efficiency) to complete the heat rather than tapping incomplete. This is a plant-specific decision by the EAF manager. [unverified]
4. If electrode falls into bath: do not charge further scrap on top of it — the graphite will dissolve. Continue melt; graphite addition to the bath can actually benefit carburisation depending on the grade target. [unverified]

#### 3. Repair Procedure

**Electrode Column Extension / Replacement**
1. Power off and raise electrode arm to maximum height.
2. Access electrode clamp area (LOTO electrical and mechanical — electrode arm movements are dangerous).
3. Unscrewing stub (use electrode unscrewing machine — power-driven unscrewing prevents nipple damage).
4. Thread new electrode onto stub column using water-cooled nipple — apply correct torque (typically 600-1000 N·m for large electrodes; follow electrode supplier torque spec exactly — over-torque causes nipple fracture). [unverified]
5. Release electrode clamp; lower column to correct arc length.
6. Verify electrode centrality in electrode hole (misaligned electrode hits roof causing secondary breakage).

### 13B — BOF OXYGEN LANCE FAILURE / BURNBACK

#### 1. Detection → Diagnosis

| Indicator | Failure Mode | Instrument |
|-----------|-------------|------------|
| Cooling water return temperature spike >40 °C rise | Lanceburn-through — water exposed to hot steel | Inlet/outlet temperature differential monitor |
| Cooling water flow imbalance | Lance tube blocked or cracked | Inlet vs outlet flow meters |
| Flame at lance tip visible (abnormal colour) | Lance nozzle erosion / asymmetric wear | CCTV at hood |
| Oxygen flow drop at constant pressure | Lance nozzle worn (Mach disc changed) | Oxygen flow transmitter |
| Lance retraction speed decrease | Lance binding on guide or slag accumulation | Position encoder trend |

Diagnostic sequence:
- Step 1: Water temperature differential is the primary safety signal. A ΔT > +35 °C over baseline on return water = lance burnthrough imminent or active. Trip threshold is typically ΔT = 40-50 °C. [unverified]
- Step 2: Review blowing records: heat number, oxygen flow, lance height, bath carbon estimate. Premature burn-back is common after: low lance height, high oxygen rate, low bath carbon, or poor slag chemistry (thin, acidic slag provides less thermal protection to lance tip).
- Step 3: After heat: withdraw lance and inspect nozzle visually — measure nozzle throat diameter vs new (new typically 45-52 mm depending on converter size; nozzle condemned when throat eroded >10% over nominal). [unverified]

#### 2. Immediate Action

1. If water ΔT alarm: IMMEDIATELY withdraw lance from converter — do NOT keep blowing.
2. If water ΔT reaches trip setpoint: emergency retract and trip oxygen supply. Alert process team — heat must be completed on a replacement lance or, if conversion is too early, the heat may be aborted.
3. A broken lance with water tube ruptured into a hot steel bath creates a steam explosion risk: keep all personnel clear of converter area.
4. Replace lance before next heat.

#### 3. Repair Procedure

**Lance Nozzle Replacement**
1. Withdraw and park lance in maintenance position.
2. LOTO oxygen and cooling water connections.
3. Cut off worn nozzle (plasma or oxy-gas cutting).
4. Prepare lance tip face to receive new nozzle (square, clean face).
5. Weld new nozzle onto copper lance tip using qualified procedure (typically silver-braze or autogenous TIG on copper — must be leak-tight to 20 bar cooling water pressure). [unverified]
6. Pressure-test complete lance cooling circuit (1.5 × working pressure, 10 minutes). [unverified]
7. Leak test all nozzle ports with compressed air under water.
8. Return to service.

**Lance Replacement (new complete lance)**
1. For burn-through (lance body damaged beyond nozzle repair): replace complete lance.
2. Fit and align new lance in lance car — confirm correct length and centrality in converter mouth.
3. Reconnect oxygen quick-connect and cooling water swivel joints.
4. Test cooling water flow and temperature balance.
5. Functional test: blow dry oxygen at minimum flow for 30 seconds before first heat to confirm nozzle is clear.

### 13C — STIRRING / PURGING LANCE (ARGON / NITROGEN)

| Indicator | Failure Mode | Action |
|-----------|-------------|--------|
| No gas flow at set pressure | Porous plug blocked | Replace porous plug (planned ladle maintenance) |
| Elevated gas pressure required for same flow | Partial blockage | Increase purge pressure within limits; schedule plug replacement |
| Visible leak at lance joint | Coupling failure | Replace coupling; LOTO |

### 4. Spares Required + Lead Time (combined)

| Item | Lead Time |
|------|----------|
| Graphite electrodes (RP/HP/UHP grade) | 4-12 weeks (typically managed on VMI agreement with Graftech / Tokai Carbon / SGL) [unverified] |
| Electrode nipples | Same lead time as electrodes |
| BOF oxygen lance (complete) | 2-6 weeks [unverified] |
| BOF lance nozzle (copper) | 2-4 weeks [unverified] |
| Lance cooling water quick-connect couplings | In stock |
| Porous plug (ladle / RH degasser) | 2-4 weeks (manageable inventory consumable) [unverified] |

### 5. Tools / Skills / Crew

**EAF Electrodes**
- Tools: Electrode unscrewing machine (powered), electrode clamp, calibrated torque wrench for nipple connections, electrode length measurement tool (laser rangefinder from floor or crown-level measurement).
- Skills: EAF operator + electrode specialist (supplier representative often assists with campaign optimisation).
- Crew: 2-3 furnace crew, 1 electrician (electrode clamp and power connection).

**BOF Lance**
- Tools: Plasma cutter, TIG welding set (copper-capable), pressure test rig, lance alignment fixture, oxygen blow-down kit.
- Skills: Welder (copper welding certification), BOF operator, pressure-system competent person.
- Crew: 2 welders, 2 BOF maintenance fitters, 1 permit holder.

### 6. Time-to-Repair

| Scenario | TTR |
|----------|-----|
| EAF electrode addition between heats | 5-15 minutes [unverified] |
| BOF lance change (spare available) | 15-30 minutes between heats [unverified] |
| BOF lance nozzle re-tip (workshop) | 2-4 hours [unverified] |
| BOF lance repair (burned-through body) | Replace with new — 15-30 min if spare available [unverified] |

### 7. Plannability

- EAF electrode: planned additions between heats are routine operations. Emergency is a mid-heat break.
- BOF lance: replace on schedule (typically 50-150 heats per lance nozzle). Emergency is a burn-through.

### 8. Verification / Return-to-Service

**EAF Electrode**
1. Verify electrode alignment in column (all three columns equal stub length ± 50 mm). [unverified]
2. First-arc test: apply low power; confirm stable arc regulation before stepping to full power.

**BOF Lance**
1. Cooling water flow and ΔT test at normal operating pressure — no anomaly.
2. Oxygen flow test at minimum rate — confirm correct Mach-number jets visible at nozzle (white flame structure, correct number of gas jets).
3. First heat: monitor water ΔT every 30 seconds during blowing.

### 9. Recurrence Prevention

- EAF electrode:
  - Grade selection: use UHP (Ultra High Power) electrodes for UHP-class furnaces — using HP grade in a UHP furnace is the most common cause of premature breakage. [unverified]
  - Scrap quality: oversized scrap causes mechanical breakage during cave-ins. Implement scrap size limits for the first bucket.
  - Electrode cooling: maintain water-cooled electrode gantry seals in good condition — air cooling of electrode above bath reduces oxidation losses by 30-50%. [unverified]
  - Electrical control: properly tuned electrode regulation avoids excessive current spikes that cause thermal shock to graphite.

- BOF lance:
  - Lance height control: enforce minimum lance height protocol for each blowing stage. Low lance height is the primary cause of early burnthrough.
  - Slag management: maintain correct basicity and FeO content in slag — corrosive or thin slag does not protect lance tip from radiant heat.
  - Water quality: maintain cooling water chemistry within specification — scale build-up in lance cooling channels is a primary cause of burn-through.
  - Heat records: track heats-per-lance and nozzle throat diameter — set mandatory change-out at condition limit, not operator discretion.

---

---

# CROSS-REFERENCE MATRIX

| Failure Mode | Playbook | Primary Detection Method | Typical Unplanned TTR | Emergency Stop? |
|--------------|----------|--------------------------|----------------------|----------------|
| Bearing failure | PB-01 | Vibration (ISO 10816 Zone D) | 4-16 h | Zone D / >95°C |
| Gearbox tooth/oil | PB-02 | Ferrography + chip detector | 3-7 days | Spall/fracture |
| Motor winding/rotor | PB-03 | IR test / MCSA | 8h–12 weeks | PI <1.0 / relay trip |
| Pump seal/impeller | PB-04 | Seal flow + performance curve | 2-8 h | Sudden seal failure |
| Fan blade/bearing | PB-05 | Vibration 1X + BPF | 4-24 h | Zone D / blade crack |
| Compressor surge | PB-06 | Surge-line position + ASV | 4h–10 days | Sustained surge |
| Servo-valve silting | PB-07 | ISO 4406 + step-response | 2-4 h (spare avail.) | AGC loss |
| Mill roll spalling | PB-08 | Surface inspection + gauge | 15 min–24 h | Strip quality failure |
| Caster segment/mould | PB-09 | Thermocouple array + force | 4–48 h | Breakout / BPS trip |
| Conveyor idler/belt | PB-10 | IR thermometer + tracking | 15 min–8 h | Hot idler / fire |
| Crane rope/brake | PB-11 | Visual + MRT / brake test | 4-24 h | Always emergency |
| Furnace refractory | PB-12 | Shell thermocouple + IR survey | 7–21 days | Shell temp limit |
| Electrode/lance | PB-13 | Water ΔT / arc stability | 15 min–4 h | Water ΔT alarm |

---

# REFERENCES AND STANDARDS (NON-EXHAUSTIVE)

| Standard | Title | URL |
|----------|-------|-----|
| ISO 10816-3:2009 | Mechanical vibration — rotating machine severity | https://www.iso.org/standard/59063.html |
| ISO 15243:2017 | Rolling bearings — failure modes and classification | https://www.iso.org/standard/59858.html |
| ISO 4309:2017 | Cranes — wire rope selection, care, maintenance | https://www.iso.org/standard/66276.html |
| ISO 18436-2:2014 | Condition monitoring — training of personnel (vibration) | https://www.iso.org/standard/61145.html |
| ISO 21940-11 | Mechanical vibration — rotor balancing | https://www.iso.org/standard/56326.html |
| API Std 670 | Machinery protection systems (compressors) | https://www.api.org/products-and-services/standards/important-standards-program/api-670 |
| API Std 617 | Axial and centrifugal compressors | https://www.api.org/ |
| AGMA 2101-D04 | Fundamental rating factors for gear tooth strength | https://www.agma.org/standards/ |
| HI 1.3 | Hydraulic Institute — centrifugal pump standards | https://www.pumps.org/standards/ |
| IEEE Std 43-2013 | IEEE recommended practice for motor insulation resistance testing | https://standards.ieee.org/ieee/43/3606/ |
| NEMA MG1 | Motors and generators | https://www.nema.org/standards/view/Motors-and-Generators |
| IEC 60034-1 | Rotating electrical machines — rating and performance | https://www.iec.ch/dyn/www/f?p=103:22:0::::FSP_ORG_ID:1282 |
| OSHA 1910.179 | Overhead and gantry cranes | https://www.osha.gov/laws-regs/regulations/standardnumber/1910/1910.179 |
| EN 12385-4 | Steel wire ropes — safety for stranded ropes for general lifting applications | https://www.en-standard.eu/ |
| ISO 4406:2021 | Hydraulic fluid power — method for coding cleanliness level | https://www.iso.org/standard/79671.html |
| AISE Technical Report No. 11 | Roll Technology | https://www.steel.org/ |

---

*Document end. All estimates tagged [unverified — for demo only] are drawn from industry heuristics and the synthetic corpus; they are not certified Tata Steel plant data and must be validated against actual OEM documentation, plant SOPs, and CMMS historical records before operational use.*
