# Hydraulic & Pneumatic Systems — Integrated Steel Plant (Tata Steel Scale)
## Deep PdM Reference

**Scope:** AGC servo-hydraulics, caster hydraulics, shear/looper hydraulics, pneumatic actuators  
**Last updated:** 2026-06-08  
**Verification status:** [unverified] unless a cite URL is given

---

## 1. SYSTEM TYPES & LOCATIONS

### 1.1 AGC Servo-Hydraulic System (Hot Strip Mill / Cold Rolling Mill)
- **Purpose:** Micron-precision roll-gap control on each mill stand. Hydraulic cylinders exert force on screw-down or direct-acting mechanisms. Closed-loop: X-ray/gamma gauge → thickness error signal → servo valve command → cylinder position correction in milliseconds.
- **Location:** Each rolling stand (rougher R1-R2, finisher F1-F7 in HSM; tandem stands S1-S5 in CRM). Dedicated hydraulic power unit (HPU) per stand group or shared across 2-3 stands.
- **Operating pressure:** 200–315 bar (servo-hydraulic grade) [Source: oxmaint.com/rolling-mill-hydraulic-system-maintenance-agc-looper]
- **AGC cylinder bore:** 400–900 mm diameter; stroke 10–50 mm; positioning accuracy ±0.01 mm; rated life ≥ 12,000 operating hours [Source: shellpponhydraulic.com AGC cylinder datasheet]
- **Control valve type:** Two-stage electrohydraulic servo valve (Moog, Bosch Rexroth, Parker), bandwidth 100 Hz+; spool clearance 3–5 µm

### 1.2 Hydraulic Power Packs (HPU)
- **Purpose:** Centralized or stand-local pressure supply. Feed servo valves, proportional valves, and directional valves throughout the mill.
- **Location:** Basement or mezzanine adjacent to mill stands, caster bay, shear house
- **Components:** Axial-piston variable-displacement pumps (Parker, Rexroth A4VSO series; Sauer-Danfoss 90-series), pressure-compensated, 1,500–3,000 RPM; motor drives 75–1,000 kW
- **Pressure:** Main AGC circuit 200–315 bar; auxiliary (loopers, coilers) 80–250 bar; furnace/coke-oven tilting 150–200 bar [Source: oxmaint.com/steel-plant-hydraulic-system-maintenance-mills-casters-furnaces]
- **Oil volume:** 2,000–20,000 litres per HPU for a large HSM; two or three pump sets in duty/standby/assist configuration
- **Filtration:** 3 µm absolute beta (β₃ ≥ 200) on pressure line; 10 µm return line; offline kidney-loop (6 µm β ≥ 200) running 24/7

### 1.3 Accumulators
- **Purpose:** Absorb pressure spikes (water-hammer on fast AGC demand); emergency energy store for safe descent; low-pass the pump's ripple from the servo circuit
- **Types:** Bladder (most common), piston, diaphragm
- **Sizes:** 20–200 litre per accumulator, banked sets of 4–8 on large AGC circuits
- **Nitrogen pre-charge:** 60–70% of working pressure [Source: oxmaint.com AGC looper guide]; dropping below 50% of target causes spikes to transmit directly to servo spool → accelerated wear

### 1.4 Continuous Caster Hydraulic Systems
- **Mold oscillation drive:** Servo-hydraulic cylinders oscillate mold at 0–500 cpm, stroke ±2–5 mm, typically 80–150 cpm at 1–2 Hz. Primetals DynaFlex systems use electro-hydraulic servo with <0.01 mm stroke repeatability [Source: primetals.com DynaFlex]
- **Strand guide segment clamping:** Proportional valves control roll-gap force; 100–200 bar; position-controlled via LVDT
- **Tundish stopper/slide gate:** Fast-response servo valve; sub-second open/close
- **Emergency torch cutting hydraulics:** Lower-pressure (80–120 bar) directional valve circuits
- **Dummy bar withdrawal:** 150–200 bar; cylinder-driven

### 1.5 Shear Hydraulics (Crop Shear, Flying Shear, Cobble Shear)
- **Crop shear (HSM entry):** Removes head/tail of transfer bar; accumulator-boosted to give fast blade strike; 200–280 bar peak; blade-drop cycle < 200 ms
- **Flying shear (billet/bar mill):** Synchronised with bar speed; servo or proportional valve drive; 150–250 bar [unverified for exact value — manufacturer datasheets vary]
- **Cobble shear / dividing shear:** Emergency use; 180–250 bar; manual or semi-auto

### 1.6 Looper Hydraulics (HSM)
- **Purpose:** Maintains inter-stand strip tension/looper angle during rolling
- **Valve type:** Proportional valve (10–30 Hz bandwidth, hysteresis ≤ 2%)
- **Pressure:** 100–200 bar
- **Note:** Most dynamically loaded circuit in the mill — rapid pressure cycles every few seconds

### 1.7 Pneumatic Systems
- **Uses:** Roll change automation (push/pull), scale flushing valves, pneumatic conveying (pellets, lime), blast-furnace tuyere inerting, cooling-water control valves, galvanising line tension bridles, cold-mill threading guides
- **Supply pressure:** 5–10 bar plant air (instrument air dryer to dewpoint –40 °C); some high-pressure nitrogen blanket lines at 20–40 bar for caster tundish shroud sealing
- **Actuators:** Spring-return pneumatic cylinders, rack-and-pinion rotary actuators, diaphragm actuators on control valves (Fisher, Rotork, Metso Neles)

---

## 2. PARTS BREAKDOWN

| Component | Detail |
|-----------|--------|
| **Servo valve** | Two-stage flapper/nozzle or jet-pipe pilot → main spool; torque motor; Moog D792/D765, Rexroth 4WREE; spool clearance 3–5 µm; flow rating 4–100 L/min at 70-bar drop |
| **Proportional valve** | Single-stage solenoid + LVDT spool feedback; Parker D3FP, Rexroth 4WRAE; hysteresis ≤ 2%; deadband ±10% signal; bandwidth 10–30 Hz |
| **AGC cylinder** | Integrally forged alloy-steel barrel; hard-chrome or HVOF-coated rod; piston seals: PTFE-backed lip seals + O-ring; rated 315–400 bar; integrated LVDT or magnetostrictive position transducer |
| **Hydraulic pump** | Variable-displacement axial-piston; volumetric efficiency ≥ 95% new; Rexroth A4VSO, Parker PV series; drain case pressure < 3 bar; max case temp < 65 °C |
| **Accumulator bladder** | Nitrile or HNBR rubber; rated to 1.5× working pressure; gas valve (Schrader) on top; oil port (anti-extrusion poppet) at bottom |
| **Pressure filter element** | Borosilicate glass-fibre; β₃(c) ≥ 200 (3 µm absolute); collapse pressure ≥ 20 bar; change on dP indicator pop or quarterly whichever first |
| **Return filter** | 10 µm β ≥ 75; fitted dP switch; bypass valve opens at 3.5–6 bar dP |
| **Hydraulic hose** | SAE 100R13/R15 (4-spiral, ≥ 420 bar working); EN 856 4SH; fitting crimped, not reusable after separation; fire-resistant (MSHA 31-13138 compliant) recommended near hot areas |
| **Manifold block** | D03/D05/D07 machined ductile iron or aluminium; cartridge valve sockets; integrated pressure test points (Minimess); eliminates leak-prone tube joints |
| **Oil** | Mineral HLP/HLPD ISO VG 46 (ambient < 35 °C, cool HPU) or ISO VG 68 (ambient > 35 °C, HPU oil temp > 50 °C); fire-resistant HF-D (phosphate ester, Fyrquel) sometimes mandated near reheating furnaces |
| **Pneumatic cylinder** | Aluminium bore; NBR/PU seals; ISO 6431 standard; rod end: clevis or flange; lubricated or non-lube depending on position |
| **Pneumatic valve** | 5/2 or 5/3 solenoid directional; NAMUR interface for rotary actuators; spring-return fail-safe (typically fail-close on roll-change clamps) |

---

## 3. SENSORS — TYPES AND PLACEMENT

| Sensor | Measurement | Location | Technology |
|--------|-------------|----------|------------|
| **System pressure transducer** | Absolute pressure (bar) | HPU outlet, servo valve supply/return ports, accumulator gas port | Piezo-resistive or ceramic; 0–400 bar; 4–20 mA or IO-Link |
| **Differential pressure (dP) across filter** | Filter clogging; pressure drop (bar) | Return filter, pressure filter | Mechanical pop-indicator or electronic dP transducer; 0–10 bar range |
| **LVDT / magnetostrictive position** | Cylinder rod position (mm) | AGC cylinder piston rod; servo-valve spool | LVDT ±0.05 mm resolution; magnetostrictive ±0.01 mm; signal 0–10 V or 4–20 mA |
| **Oil temperature** | Bulk oil temperature (°C) | HPU reservoir, return line | PT100 or thermocouple; 0–120 °C; alarm at 60 °C, trip at 70 °C |
| **Oil cleanliness / particle counter** | ISO 4406 particle counts at >4 µm, >6 µm, >14 µm | Offline sample port or inline continuous | Laser particle counter (Hydac CS series, MP Filtri LPA series); sample every 500 rolling hours or real-time |
| **Oil water content** | Dissolved/free water ppm | Reservoir return line | Capacitive water-in-oil sensor (Hydac HYDAClab, ifm LDH); 0–2,000 ppm range; alarm at 200 ppm |
| **Flow meter** | System flow (L/min) | Pump outlet, individual servo valve supply | Gear-type or ultrasonic; Moog/Kracht type |
| **Accumulator pre-charge gauge** | Nitrogen gas pressure (bar) | Accumulator gas valve | Bourdon gauge or pressure transducer; checked weekly on shutdown |
| **Servo valve LVDT (internal)** | Spool displacement | Inside servo valve | 2-element differential LVDT embedded in valve body; output used by valve amplifier closed loop |
| **Motor current / power** | Pump motor load | MCC panel | 3-phase current transformer; used for pump volumetric efficiency trending |
| **Oil debris / ferrography** | Ferrous particle concentration | Periodic oil sample | Ferrographic analysis or inline inline magnetic plug; scheduled quarterly |
| **Vibration (accelerometer)** | Pump/motor bearing vibration | Pump motor bearing housings | 100 Hz–10 kHz; ISO 10816-3 RMS velocity; trended vs baseline |
| **Pneumatic pressure** | Line pressure (bar) | Instrument air header, actuator supply | Bourdon or electronic 0–16 bar; low-pressure alarm at < 5.5 bar |

---

## 4. NORMAL SENSOR READINGS

| Sensor | Normal Operating Range | Notes |
|--------|----------------------|-------|
| AGC servo system supply pressure | 200–315 bar ± 5% | Pressure compensator holds steady; ripple < 2% |
| Looper / coiler circuit pressure | 100–250 bar | Varies with rolling force |
| Auxiliary circuits (roll change, etc.) | 80–160 bar | |
| Filter dP (pressure filter, clean) | 0.2–0.8 bar | New element starts ~0.3 bar; change at 4–6 bar visual pop or electronic trip |
| Filter dP (return filter, clean) | 0.3–1.2 bar | Bypass opens at 3.5–6 bar; cold oil startup spike normal |
| Oil temperature (reservoir) | 40–55 °C | Thermostatic cooler/heater maintains; optimal 45–50 °C |
| Oil temperature (servo circuit return) | 45–60 °C | Continuous > 60 °C degrades additives and seals |
| Oil cleanliness (AGC servo circuit) | ISO 16/14/11 (target) | Alert at ISO 18/16/13; one code-step difference = 2× particle concentration |
| Oil cleanliness (proportional valve circuit) | ISO 17/15/12 | |
| Oil cleanliness (cylinder/auxiliary) | ISO 18/16/13 to 19/17/14 | |
| Water content | < 100 ppm (servo); < 200 ppm (general) | [Source: oxmaint.com caster hydraulics] |
| AGC cylinder position (in-spec) | Setpoint ± 0.02 mm | LVDT reading vs commanded; drift > 0.05 mm flagged |
| Accumulator pre-charge pressure | 60–70% of working pressure | e.g. 200–220 bar on 315 bar system |
| Pump motor current | ± 5% of baseline at equivalent load | Trending; absolute value depends on pump size |
| Vibration at pump bearing | < 4.5 mm/s RMS (ISO 10816 Class II) | Alert at 7.1, trip at 11.2 mm/s |
| Instrument air pressure | 6.5–8 bar | Low alarm at 5.5 bar; instrument air dryer dewpoint −40 °C |
| Viscosity at 40 °C (VG 46) | 41.4–50.6 cSt | Change if viscosity shifts ±10% from spec due to contamination or shear degradation |

---

## 5. DEFECT READINGS — FAILURE-MODE SIGNATURES

### 5.1 Servo Valve Silting / Stiction (Contamination-Induced)
- **Mechanism:** Micro-particles (4–6 µm) migrate into 3–5 µm spool clearance → form abrasive silt pack → spool sticks intermittently
- **Primary cause:** Oil cleanliness degrading past ISO 18/16/13 (servo); particle ingress during maintenance
- **Sensor signatures:**
  - LVDT position feedback: command-to-position lag grows from baseline < 5 ms → 15–50 ms over weeks
  - AGC gauge deviation: strip thickness error creeps beyond ±5 µm (customer tolerance often ±10–20 µm); increases at low-frequency (< 1 Hz) inputs
  - Servo linearisation test: flow-gain drops > 10% from commissioning baseline → replacement threshold [Source: oxmaint.com rolling-mill-hydraulic-system-maintenance-agc-looper]
  - System pressure: no change initially — silent failure until quality event
- **Detection lead time:** 4–8 weeks before quality event if command-to-position lag is trended weekly [Source: oxmaint.com rolling-mill-hydraulic-system-maintenance-agc-looper]
- **Threshold for action:** ≥ 5% response time deviation from baseline; flow-gain loss ≥ 10%

### 5.2 Clogged Hydraulic Filter
- **Mechanism:** Progressive particle accumulation in filter media; bypass valve opens at set dP releasing contamination bolus into downstream circuit
- **Sensor signatures:**
  - Filter dP transducer: rises from 0.3–0.8 bar (clean) toward 4–6 bar (clog alarm) — 0.5 bar is ISO 2943 standard normal-operation upper reference [Source: internormenfilters.com]
  - dP rise rate matters: slow (weeks) = normal loading; fast (days) = contamination event upstream
  - Oil particle count downstream spikes immediately after bypass event
- **Threshold for action:** Visual/electronic pop indicator activation at 4–6 bar; do not reset without element change

### 5.3 Cylinder Internal Seal Extrusion / Wear
- **Mechanism:** Piston or rod seal lip wears, extrudes under cycling → allows cross-port bypass of oil → cylinder drifts under load
- **Sensor signatures:**
  - LVDT position drift under load: > 1 mm rod drift with no command (rod seal bypass test) [Source: oxmaint.com rolling-mill-hydraulic-system-maintenance-agc-looper]
  - AGC position drift: cylinder cannot hold position against rolling force → gauge deviation
  - System pressure: low-side pressure rises (cross-port leakage equalises), high-side pressure drops
  - Oil temperature: slightly elevated from internal fluid churning across bypass path
- **Threshold for action:** Position drift > 1 mm at full load; AGC cylinder scheduled re-seal at 12–18 months or 15,000–25,000 force cycles

### 5.4 Accumulator Bladder Rupture / Pre-Charge Loss
- **Mechanism:** Bladder punctured by oil-port poppet (over-discharge); nitrogen permeates rubber over time; sudden rupture from over-pressurisation or cold-inflation (nitrogen chill = brittle failure)
- **Sensor signatures:**
  - Accumulator gas pressure (weekly manual check): drops below 50% of working pressure [Source: fluidpowerjournal.com accumulator pre-charge maintenance]
  - System pressure oscillation amplitude increases (pump ripple no longer damped)
  - On full bladder rupture: oil exits through gas valve, nitrogen mixes into oil → cavitation noise at pump, milky oil
  - Pressure spikes transmit directly to servo valve spool on bladder failure → accelerated wear
- **Threshold for action:** Pre-charge < 50% of target → immediate top-up or replacement; milky oil → emergency shutdown for oil system purge

### 5.5 Hydraulic Pump Wear (Volumetric Efficiency Loss)
- **Mechanism:** Piston-bore and valve-plate wear; slipper pad erosion; case drain flow increases (internal leakage)
- **Sensor signatures:**
  - Pump case drain temperature: rises > 65 °C (normal < 55 °C) [unverified exact threshold varies by pump model]
  - Pump case drain flow: > 10% of rated output flow indicates excessive wear [Source: powermotiontech.com piston pump failure]
  - Motor current: same output pressure → higher current → volumetric efficiency declining
  - System pressure under load: sags ≥ 10% at rated demand → pump losing output
  - Vibration (pump bearing): rising RMS velocity; spectral peak at vane/piston pass frequency
  - Oil metal content (wear debris): elevated iron, chromium, nickel in oil sample (ferrography)
- **Threshold for action:** Volumetric efficiency < 85% of rated; case drain > 10% of rated flow; schedule replacement at next planned window

### 5.6 Hydraulic Hose Failure / Burst
- **Mechanism:** Fatigue from pressure impulse cycling (most common — not static overpressure); abrasion on external cover; fitting corrosion/stress cracking; aging rubber (ozone, heat)
- **Sensor signatures (early):**
  - No direct sensor usually fitted on individual hoses — rely on inspection
  - Pressure transducer downstream shows micro-drops (pinhole weeping before burst)
  - Oil level in HPU reservoir drops unexpectedly
  - Infrared thermal camera: hot spot on hose route during operation
- **Catastrophic burst:**
  - Pressure transducer drops to near-zero downstream instantly
  - HPU low-level alarm triggers
  - Fire risk: mineral oil auto-ignition ~300 °C; hot strip mill strip temperatures 900–1,100 °C — hose in proximity is a severe fire hazard; phosphate-ester fluid or fire-resistant sleeve mandatory near rolling stands [Source: assessor.com.au hydraulic hose safety]
- **Replacement interval:** Every 2–4 years or every 6 months in hot/high-impulse zones; mandatory visual inspection every 12 months [Source: strongflex.com hydraulic hose safety]

### 5.7 Oil Degradation — Water Ingress
- **Mechanism:** Steam, coolant leaks, condensation through breather → water dissolves in oil → additive depletion, hydrolysis, microbial growth, corrosion of servo valve body and spool
- **Sensor signatures:**
  - Water-in-oil sensor: alarm at 200 ppm; critical removal at 500 ppm [Source: oxmaint.com rolling-mill-hydraulic-system-maintenance-agc-looper]
  - Viscosity: instability > 10% if moisture absorption significant [Source: hai-lu-oil.com]
  - Oil appearance: milky/hazy at > 500 ppm free water
  - Reservoir bottom inspection: free water layer (denser than oil) settles
  - Acid number (TAN): rises as hydrolysis products form
- **Threshold for action:** > 200 ppm → identify ingress source + dehydration (vacuum dehydrator or centrifuge); > 500 ppm → drain, flush, oil change

### 5.8 Oil Contamination (Particle Count Rise)
- **Mechanism:** Ingress during filter change, breather bypass, dirty maintenance practices; internal wear particles self-generating
- **Progression:** ISO cleanliness degrades one code step per week if unmanaged; each step = 2× particle concentration
- **Threshold for action:** AGC circuit at ISO 18/16/13 → immediate kidney-loop flush campaign, check filter integrity, review breather desiccant; do not wait for servo valve symptoms

### 5.9 Pneumatic Actuator Failures
- **Seal wear / air leak:** Cylinder extends slowly, incomplete stroke, audible hiss; supply pressure gauge reads normal but cylinder pressure decays under load
- **Frozen actuator (moisture in air):** Instrument air dewpoint not maintained at −40 °C → ice blockage in pilot valve → random loss of control
- **Positioner feedback fault:** Rotary actuator overtravel or oscillation; positioner LVDT zero-drift; manifests as control valve hunting (cycling up/down around setpoint)
- **Corrosion of rod/bore:** Common in scale flushing areas with water spray; internal rust → sticktion → hysteresis

---

## 6. FAILURE MODES — COMPLETE CATALOGUE

| Failure Mode | Affected Component | Primary Cause | Earliest Detectable Sign |
|---|---|---|---|
| Servo valve silting / stiction | AGC servo valve | Oil cleanliness > ISO 18/16/13 | Command-to-position lag increase ≥ 5% |
| Servo valve erosion | Servo valve spool/sleeve | High-velocity particles (> 10 µm) + water | Flow-gain loss > 10%; increased hysteresis |
| Cylinder seal extrusion | AGC/caster cylinder | Over-pressure cycling, thermal swings, aged seals | Position drift > 1 mm under load |
| Cylinder rod corrosion/scoring | Rod chrome surface | Water ingress, scale contamination | Increased seal wear rate; visible scratching on inspection |
| Accumulator bladder rupture | Bladder accumulator | Over-discharge to poppet; cold inflation; fatigue | Pre-charge pressure loss; pressure oscillation increase |
| Pump cavitation | Axial-piston pump | Restricted inlet, low oil level, high viscosity at cold start | Noise (crackling/grinding); case temperature spike; wear debris |
| Pump plate/piston wear | Axial-piston pump | Contamination, cavitation history, end-of-life | Case drain flow > 10% rated; volumetric efficiency < 85% |
| Clogged filter → contamination spike | Return/pressure filter | End of service life; contamination event | dP across filter > 4 bar; oil cleanliness spike after bypass |
| Hose burst | HP hose assemblies | Impulse fatigue; abrasion; aging; fitting corrosion | Pressure micro-drops; oil level fall; IR hot-spot |
| Oil water ingress | Hydraulic oil system | Cooler leak; steam ingress; poor breather; condensation | Water-in-oil sensor > 200 ppm; oil appearance milky |
| Oil oxidation / additive depletion | Hydraulic oil system | Prolonged high-temp operation (> 60 °C); air ingestion | TAN rise; viscosity shift ± 10%; oil color darkening |
| LVDT zero drift | AGC cylinder position | Thermal cycles; mechanical shock; cable connector issue | AGC thickness error with no process change; bias in position feedback |
| Proportional valve coil burnout | Looper/coiler valve | Overvoltage; moisture ingress into amplifier | Valve stuck at last position; no response to command signal |
| Pneumatic actuator seal failure | Cylinder seals | Age, temperature cycling, contaminated air | Incomplete stroke; audible air leak; slow actuation |
| Mold oscillator cylinder seal | Caster oscillation cylinder | High-frequency fatigue (80–150 cpm) | Oscillation amplitude drop; asymmetry in stroke waveform |

---

## 7. REPAIR / RESOLUTION PROCESS

### 7.1 Servo Valve — Flush or Replace
- **Process:**
  1. Isolate stand; switch to backup valve if twin-valve architecture exists
  2. Flush circuit with solvent-flush or high-velocity oil flush (turbulent Re > 4,000) for 20–60 minutes
  3. Bench-test removed valve on servo valve test stand (dynamic flow-gain, step response, hysteresis)
  4. Ultrasonic cleaning of valve body; re-test
  5. If flow-gain degraded > 10% or hysteresis > 3%: replace with new/refurbished valve
  6. Reinstall; bleed; perform AGC calibration (linearisation test, step-response, static gain)
- **Time-to-repair (unplanned):** 4–8 hours per stand; planned window 2–4 hours with pre-staged spare
- **Spare pool:** Minimum 2 per valve type per plant [Source: oxmaint.com rolling-mill-hydraulic-system-maintenance-agc-looper]
- **Cost indication:** Moog/Rexroth servo valve overhaul $2,000–$8,000; new replacement $5,000–$20,000 [unverified; vendor list price range]

### 7.2 Cylinder Seal Kit Replacement
- **Process:**
  1. Depressurize; drain oil; remove cylinder to workshop (AGC cylinder weight 5–20 tonnes — crane required)
  2. Disassemble; inspect bore surface (any scoring > 0.2 mm deep → barrel replacement)
  3. Replace all seals (piston lip seal, rod seal, wiper, O-rings) with OEM or equivalent kit
  4. Hone bore if minor scoring; re-chrome rod if pitting
  5. Reassemble; pressure test to 1.5× working pressure; leak test at working pressure for 15 min
  6. Reinstall and recalibrate LVDT
- **Time-to-repair:** 16–48 hours for AGC cylinder (planned); 8–16 hours caster oscillation cylinder
- **Planned vs unplanned:** Planned seal change costs ~30% of unplanned (no production loss)
- **Interval:** 15,000–25,000 cycles or 12–18 months [Source: oxmaint.com rolling-mill-hydraulic-system-maintenance-agc-looper]

### 7.3 Oil Flush — Contamination Event
- **Process:**
  1. Drain contaminated oil; flush reservoir with clean solvent or flushing oil
  2. Replace all filter elements
  3. Fill with new, pre-filtered oil (ISO 15/13/10 as delivered from supplier via bladder-pump transfer rig)
  4. Circulate through all circuits via flushing bypass rig, sample every 2 hours until target cleanliness achieved
  5. Re-install servo valves last; verify linearisation test passes
- **Duration:** 8–24 hours for full AGC circuit flush
- **Oil cost (Tata scale plant):** ISO VG 46 mineral oil ~₹80–120/litre; 10,000-litre oil change = ₹8–12 lakh + ₹2–4 lakh disposal/re-refining [unverified; market price estimate 2025]

### 7.4 Filter Element Change
- **Trigger:** dP pop indicator at 4–6 bar, or scheduled (quarterly minimum, monthly for servo circuit)
- **Process:** Isolate inlet; depressurize; remove bowl; replace element; re-torque; reset indicator
- **Time:** 30–60 minutes per housing; zero downtime if kidney-loop offline filter
- **Cost:** High-efficiency 3 µm element ₹3,000–₹15,000 per element [unverified; vendor price range]

### 7.5 Accumulator Bladder Replacement
- **Process:** Depressurize gas (bleed Schrader valve); drain oil port; remove top end-cap; extract old bladder; fit new bladder; charge nitrogen slowly to target pre-charge (must inflate slowly to avoid cold-brittleness fracture [Source: baileyintl.com accumulator precharge guide])
- **Time:** 4–8 hours per accumulator; planned window preferred (dangerous energy stored)
- **Inspection interval:** Every 2–3 years full internal inspection

### 7.6 Hydraulic Hose Assembly Replacement
- **Process:** Depressurize; cap open ports; remove assembly; fit new pre-made assembly (crimp-end, not reusable bare hose)
- **Time:** 30–90 minutes per hose; fire-side hose may require hot-work permit
- **Interval:** Replacement every 2–4 years; 6-monthly in impulse/hot zones

### 7.7 Pump Rebuild / Replacement
- **Process:** Standby pump switch → remove failed pump → send to hydraulic workshop for valve-plate/piston/slipper kit replacement → pressure/flow test → reinstall
- **Time:** Standby switch: 15 minutes; rebuild: 8–24 hours; full replacement: 4–8 hours
- **Cost:** Axial-piston pump rebuild ₹1–5 lakh; new pump ₹5–25 lakh depending on size [unverified]

---

## 8. COST / LOSS IMPACT

### 8.1 AGC Failure — Thickness Deviation
- **Direct quality loss:** Strip out of tolerance (customer spec typically ± 10–40 µm on cold-rolled; ± 50–100 µm hot-rolled). Off-tolerance coils downgraded (prime → secondary) or rejected.
- **Rejection cost (Tata scale):** Hot-rolled coil ~₹45,000–₹65,000/tonne; if 200-tonne coil downgraded by ₹5,000/tonne → ₹10 lakh per coil. 1 downtime event may affect 5–20 coils.
- **Cobble event (catastrophic AGC failure):** Strip breaks in finishing train → cobble jam → clean-up 4–12 hours; lost production at HSM ~5,000 tonne/day → ₹22–30 crore/day production value lost; equipment damage ₹1–5 crore. Average cobble total cost $191,000 USD [Source: oxmaint.com rolling-mill-maintenance-checklist]
- **Unplanned hydraulic shutdown:** $100,000–$500,000 per event [Source: oxmaint.com rolling-mill-predictive-maintenance-iot-ai]

### 8.2 Servo Valve Contamination Campaign
- **Prevention vs cure:** Filtration/PM cost ≈ 10% of contamination repair expense [Source: oxmaint.com steel-plant-hydraulic-system-maintenance-mills-casters-furnaces]
- **Servo valve replacement rate improvement:** Circuits at ISO 17/15/12 have 4–6× lower replacement rates than those at ISO 18/16/13 [Source: oxmaint.com rolling-mill-hydraulic-system-maintenance-agc-looper]
- **Kidney-loop ROI:** Payback within 6–12 months in active rolling mill [Source: oxmaint.com rolling-mill-hydraulic-system-maintenance-agc-looper]

### 8.3 Hydraulic Hose Burst — Safety
- **Fire risk:** Atomised mineral oil spray ignites on contact with hot rolling stock or reheating furnace surfaces > 300 °C → uncontrolled fire → plant evacuation, equipment loss, fatality risk
- **Regulatory:** OSHA 29 CFR 1910.303 / IS-875 fire safety; insurance premium impact on any reportable fire
- **Estimated loss per fire event:** ₹5–50 crore for structural/equipment damage depending on area [unverified]

### 8.4 Predictive Maintenance ROI (Literature)
- Predictive maintenance programs on rolling mills reported to reduce unplanned downtime 32% → $2.4M annual savings per production line [Source: oxmaint.com rolling-mill-maintenance-ai-iot-steel-production] [unverified for Tata specific]
- Tata Steel reported 15% reduction in unplanned downtime via ML-driven PdM [unverified for hydraulics specifically; corporate communications]

---

## 9. ADDITIONAL TECHNICAL NOTES

### 9.1 Sensor Fusion for Hydraulic PdM
- **Multi-parameter correlation is essential:** Single-sensor alarms generate many false positives on hydraulic systems (pressure can spike from process demand, not just failure). Effective PdM models correlate:
  - Oil cleanliness trend + servo position lag + filter dP slope + oil temperature drift + pump case drain temperature → multivariate anomaly detection (Isolation Forest, Autoencoder, or LSTM-VAE on 10-second rolling windows)
- **Key feature engineering:**
  - Linearisation test score (weekly batch feature, not real-time)
  - Command-to-position step response lag (ms) — sampled at every roll change transition
  - Filter dP rate-of-change (bar/day)
  - Oil particle count 4-hour EWMA
  - Accumulator pre-charge ratio (actual/target)

### 9.2 AGC Linearisation Test — Basis for RUL Estimation
- **Protocol:** Step-response test during roll gap traversal at ±10% rated flow; measure rise time, overshoot, steady-state error, hysteresis
- **Baseline at commissioning:** Stored as reference vector
- **Degradation curve:** Exponential; hysteresis grows from < 1% (new) → 3% (replace threshold) over 6–18 months depending on oil cleanliness maintained
- **RUL model:** Weibull hazard or linear extrapolation of flow-gain slope; alert at 75% of remaining life to schedule planned replacement

### 9.3 Mold Oscillation — Critical PdM Window
- Mold oscillation cylinder failures in continuous casters cause strand breakout risk (liquid steel escapes solidifying shell → catastrophic safety event)
- Key monitoring: oscillation stroke symmetry (LVDT), frequency stability, servo-valve response at casting frequency
- Any asymmetry > 0.5 mm in stroke between positive/negative half-cycles warrants immediate inspection [unverified exact threshold — Primetals DynaFlex documentation]

### 9.4 Oil Condition Monitoring Programme (Best Practice)
- **Continuous (real-time):** Water-in-oil sensor; particle counter (inline, AGC circuit); temperature
- **Weekly:** Accumulator pre-charge; filter dP visual check; oil level; pump case drain temperature
- **Monthly:** Oil sample to lab (ISO 4406 count, viscosity at 40 °C, TAN, water ppm, spectral metals analysis for Fe/Cu/Cr/Al/Si)
- **Quarterly/annually:** Servo valve linearisation; ultrasonic testing of hose assemblies; oil change decision based on TAN and viscosity vs specification

### 9.5 Fire-Resistant Fluid Zones
- Phosphate-ester hydraulic fluid (HF-D, Fyrquel EHC) mandatory in areas with persistent ignition sources: reheating furnace door mechanisms, hot-strip entry guide actuators, galvanising bath area
- **Incompatibility warning:** Phosphate-ester and mineral oil cannot share circuits or components (different seals, incompatible paints/coatings); contamination of one with the other causes seal swelling and catastrophic failure within hours
- **Servo valve compatibility:** Must use stainless-steel-bodied valves with Viton O-rings; standard nitrile swells in phosphate-ester

---

## References / Sources

- [Rolling Mill AGC Hydraulic System Maintenance (OxMaint)](https://oxmaint.com/industries/steel-plant/rolling-mill-hydraulic-system-maintenance-agc-looper)
- [Steel Plant Hydraulic System Maintenance Guide (OxMaint)](https://oxmaint.com/industries/steel-plant/steel-plant-hydraulic-system-maintenance-mills-casters-furnaces)
- [Hydraulic System Maintenance for Steel Plant Equipment (OxMaint)](https://oxmaint.com/industries/steel-plant/hydraulic-system-maintenance-steel-plant-equipment)
- [AGC Hydraulic Cylinder Specifications (ShellPpon Hydraulic)](https://www.shellpponhydraulic.com/products/detail/AGC-Hydraulic-Cylinder-Automatic-Gauge-Control-Hydraulic-Cylinder)
- [AGC Cylinder Precision for Rolling Mills (GY Hydraulic)](https://www.gyhydraulic.com/news/agc-mill-working-roll-metallurgical-servo-bending-cylinder-precision-control-for-modern-rolling-mills-347386.html)
- [Primetals DynaFlex Hydraulic Mold Oscillator](https://www.primetals.com/en/portfolio/solutions/continuous-casting/dynaflex-hydraulic-mold-oscillator/)
- [ISO 4406 Cleanliness Guide (Hypro Filtration)](https://www.hyprofiltration.com/blog/iso-4406-cleanliness-codes)
- [Hydraulic Oil Contamination Standards ISO vs NAS (Winner Hydraulics)](https://www.winnerhydraulics.com/tech-resources/Hydraulic-Fluid-Cleanliness.html)
- [Accumulator Pre-Charge Maintenance (Fluid Power Journal)](https://fluidpowerjournal.com/hydraulic-accumulators-pre-charge-maintenance/)
- [Accumulator Pre-Charge Guide (Bailey International)](https://www.baileyintl.com/post/the-complete-hydraulic-accumulator-precharge-guide)
- [LVDT in Servo Valve Positioning (Trans-Tek)](https://transtekinc.com/servo-valve-positioning/)
- [LVDT Readings on Hydraulic Continuous Casting Machines (Tozato)](https://www.tozato.com.br/2022/10/lvdt-readings-hydraulic-continuous-casting/)
- [Hydraulic Pump Failure Warning Signs (Durafilterna)](https://www.durafilterna.com/blog/hydraulic-pump-failure-12-warning-signs-that-demand-immediate-action/)
- [Hydraulic Filter Replacement Guide — dP Indicator (Internormen)](https://www.internormenfilters.com/news/hydraulic-filter-replacement-guide-how-to-use-differential-pressure-indicator-readings-for-effective-clogging-detection.html)
- [Hydraulic Hose Safety (Assessor.com.au)](https://www.assessor.com.au/resources/guides/hydraulic-hose-safety)
- [Hydraulic Hose Burst Prevention (StrongFlex)](https://www.strongflex.com/how-to-prevent-hydraulic-hose-burst/)
- [Servo vs Proportional Valves for Industrial Hydraulics (AHS Hydraulics)](https://feeds.ahshydraulics.com/blog/servo-vs-proportional-valves-industrial-hydraulics)
- [Rolling Mill Predictive Maintenance: AI & IoT (OxMaint)](https://oxmaint.com/industries/steel-plant/rolling-mill-predictive-maintenance-iot-ai)
- [Hydraulic Cylinder Uses in Iron & Steel Industry (Yagang Hydraulic)](https://yaganghydraulic.com/guide/hydraulic-cylinder-uses-in-iron-steel-industry/)
- [Pneumatic Actuator Failure Modes (uReason FMEA)](https://www.ureason.com/resources/fmea-or-fmeca-for-your-assets-part-4/)
