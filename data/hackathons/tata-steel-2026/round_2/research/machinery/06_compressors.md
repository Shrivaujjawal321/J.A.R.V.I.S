# PdM Reference: Compressors in Integrated Steel Plants (Tata Steel Scale)

**Compiled:** 2026-06-08  
**Scope:** All major compressor types found in a ~5–10 MTPA integrated steelworks — instrumented for predictive maintenance.  
**Note:** Values marked [unverified] are drawn from third-party technical references, not OEM manuals. Actual setpoints are equipment-specific and set during commissioning.

---

## 1. Compressor Types & Locations in Integrated Steel

### 1.1 Centrifugal Air Compressors (Plant Air & Instrument Air)

**Where:** Central compressor houses, often 4–6 machines sharing a distribution header.  
**What they do:**  
- **Plant air:** 6–7 bar(g), feeds pneumatic tools, conveying systems, bag filters, blast cleaning.  
- **Instrument air:** 5–7 bar(g), dry/oil-free, powers control valve actuators, positioners, transmitters across the whole plant (BF, BOF, CCM, rolling mills). This is the most safety-critical compressed-air circuit.  

**Typical specs:**  
- Capacity: 2,000–25,000 Nm³/hr per unit  
- Discharge pressure: 6–8 bar(g) [unverified — varies by plant design]  
- Speed (integrally geared stage): 10,000–30,000 rpm on high-speed impeller shafts; bull gear ~3,000–3,600 rpm  
- Motor: 250 kW – 3 MW  
- Standard: API 617 (axial and centrifugal compressors)  

**Sub-types:**  
- Integrally geared centrifugal (most common for instrument/plant air, oil-free)  
- Axial-centrifugal for very large flows (blast furnace blowers overlap here)

### 1.2 Rotary Screw Compressors

**Where:** Distributed utility rooms near coke plant, raw materials, maintenance workshops; also backup instrument air.  
**What they do:** 7–13 bar(g) compressed air for local tools and processes.  
**Typical specs:**  
- Capacity: 500–5,000 Nm³/hr  
- Discharge pressure: 7–12 bar(g)  
- Oil-injected (general utility) or oil-free (instrument air backup)  
- Speed: 1,500–3,600 rpm direct drive or geared  

### 1.3 Reciprocating (Piston) Compressors

**Where:** High-pressure applications — CO₂ injection, hydraulic accumulator charging, coke oven gas (COG) boosting at lower volumes, laboratory/test rigs.  
**What they do:** Very high pressure ratios (up to 200–350 bar for special applications), or precise pressure delivery.  
**Typical specs:**  
- Single/multi-stage  
- Discharge pressure: 20–200+ bar depending on service  
- Speed: 300–1,500 rpm  

### 1.4 Blast Furnace Blowers (High-Volume Centrifugal / Axial)

**Where:** Blast furnace cast house / blower house, one per blast furnace.  
**What they do:** Deliver hot blast air at 3–6 bar(g) to tuyeres — critical for continuous BF operation. Flow: 100,000–300,000 Nm³/hr on large BFs.  
**Note:** Often called "blowers" not compressors, but functionally identical machinery; governed by same PdM principles.  

### 1.5 Air Separation Unit (ASU) Compressors

**Where:** Oxygen/nitrogen plant (on-site ASU), typically adjacent to BF and BOF shops.  
**What they do:** Feed atmospheric air (compressed to 5–10 bar(g)) into the cryogenic separation columns to produce:  
- **Oxygen (O₂):** 95–99.5% purity, ~200–1,500 t/day per train → piped to BOF lance, BF tuyere enrichment, electric arc furnace  
- **Nitrogen (N₂):** Purging, stirring, inerting, continuous caster shrouding  
- **Argon:** Secondary metallurgy (AOD, ladle purging)  

**Typical specs:**  
- Main air compressor (MAC): centrifugal, multi-stage, 10–50 MW, 5–8 bar(g) discharge  
- Booster compressors for high-pressure oxygen: reciprocating, up to 40–80 bar(g)  
- Cycle: 1–2 MAC failures per year is historically reported on large ASUs [unverified — per industry reference]  

### 1.6 Coke Oven Gas (COG) / Blast Furnace Gas (BFG) Compressors

**Where:** Byproduct gas recovery systems.  
**What they do:**  
- **COG compressors:** Boost reformed/cleaned COG pressure for injection to BF, steel-plant boilers, or power plants. Centrifugal or rotary lobe types. Hazardous gas (H₂ ~55%, CO ~5–8%).  
- **BFG boosters:** Raise BFG pressure for use in stoves and power plants.  
- **Tata Steel, Kalinganagar:** Water-injected compressor units documented for process gas service [source: GreenSteelWorld].  

### 1.7 Process Gas Compressors (BOF / Converter Gas Recovery)

**Where:** LD gas (CO-rich, ~65%) cleaning and recovery plants.  
**What they do:** Compress converter off-gas for re-use as fuel.  

---

## 2. Parts Breakdown

### 2.1 Centrifugal Compressor (integrally geared, oil-free)

| Sub-assembly | Key components |
|---|---|
| Compression elements | Impellers (3D milled titanium/stainless, backward-swept), diffusers, volutes/return channels |
| Rotating assembly | High-speed pinion shafts (one per impeller stage), bull gear, main shaft |
| Bearings | Tilting-pad journal bearings (radial) + Kingsbury-type thrust bearings on each shaft; white-metal (babbitt) lined |
| Shaft seals | Labyrinth seals (oil-free stages), dry gas seals (DGS) on process gas variants |
| Intercoolers | Shell-and-tube heat exchangers between stages; water-cooled; remove heat of compression |
| Aftercooler | Post-last-stage cooler + moisture separator |
| Lube/seal oil system | Oil reservoir, main oil pump (shaft-driven) + standby electric pump, oil cooler, oil filter, oil heater (pre-start), drain system |
| Inlet guide vanes (IGV) | Variable-angle inlet vanes for capacity and surge control |
| Anti-surge system | Blow-off/recycle valve, flow transmitter, surge controller |
| Motor/driver | Induction motor or steam turbine (older plants); VFD increasingly common |
| Instrumentation | Per API 670 / API 617 — see Section 3 |

### 2.2 Rotary Screw Compressor

- Male/female rotors (meshing helical lobes), rotor housing  
- Roller/ball bearings (airend), main drive bearings  
- Oil separator (oil-injected type), oil cooler, oil filter, thermostatic bypass valve  
- Inlet filter / unloader valve  
- Pressure relief valve  
- Minimum pressure valve  
- Motor + coupling  

### 2.3 Reciprocating Compressor

- Cylinders, pistons, piston rings, rider bands  
- Suction and discharge valves (spring-loaded plate/ring type — most failure-prone part)  
- Piston rod + packing rings (dynamic seal)  
- Crosshead + crosshead pin/bushing  
- Connecting rod + crankshaft  
- Main/crank bearings + crosshead shoes  
- Intercoolers + aftercooler  
- Cylinder lubrication system (loss-lubrication injectors)  
- Frame lubrication system (crankcase oil)  

---

## 3. Sensors and Instrumentation (per API 670 / API 617)

| Sensor | Location | Technology | Primary use |
|---|---|---|---|
| Shaft vibration (radial) | Each bearing, X+Y planes | Eddy-current proximity probes (non-contact) | Unbalance, misalignment, rub, oil whirl, surge |
| Shaft vibration (axial) | Thrust end, one or two probes | Eddy-current proximity probe | Axial position / thrust bearing load |
| Casing vibration | Bearing housing | Seismic accelerometer or velocity pickup | Overall mechanical condition |
| Bearing temperature | Each journal and thrust pad | RTD (PT100) or thermocouple embedded in pad | Bearing health, lubrication adequacy |
| Oil pressure | Lube oil supply header | Pressure transmitter | Lubrication integrity |
| Oil temperature | Oil supply & return | RTD / thermocouple | Oil viscosity, cooler performance |
| Oil level | Oil reservoir | Level gauge / level switch | Lube system integrity |
| Discharge pressure | Each stage outlet | Pressure transmitter | Stage performance, system demand |
| Suction pressure | Compressor inlet | Pressure transmitter | Flow, anti-surge control |
| Differential pressure (across filter) | Inlet air filter, oil filter | DP transmitter | Filter loading, maintenance trigger |
| Discharge temperature | Each stage outlet | RTD / thermocouple | Valve condition (recip), intercooler performance, overload |
| Inter-stage temperature | Between stages | RTD / thermocouple | Intercooler fouling detection |
| Flow | Suction / discharge | Orifice plate / venturi / ultrasonic | Anti-surge, capacity monitoring |
| Motor current | Motor MCC | CT-based MCSA | Motor / mechanical load anomalies |
| Surge counter | Anti-surge control loop | Software-derived from P, T, flow | Surge event frequency alarm |
| Oil analysis (offline) | Oil sample port | Spectroscopy, ferrography, viscosity | Bearing wear metals, contamination, oil degradation |
| Vibration spectrum (periodic) | Bearing housings | Portable or online analyser | Fault frequency identification |

**API 670 minimum requirement** for centrifugal compressor: ≥2 radial X+Y probe pairs per bearing + ≥1 axial probe pair; monitoring frequencies ≥2 kHz; separate alarm (alert) and danger (trip) setpoints; surge detection using discharge pressure + flow + temperature.  
**Surge trip logic (common):** 3 surge cycles in 10 seconds → trip [source: Bently Nevada / Baker Hughes].

---

## 4. Normal Operating Readings by Sensor

Values below are industry-typical ranges for large centrifugal plant-air / instrument-air compressors at an integrated steel plant. Actual setpoints are commissioned per OEM specifications.

| Sensor | Normal Operating Range | Notes |
|---|---|---|
| Discharge pressure (plant air) | 6.0–7.5 bar(g) | System design dependent |
| Discharge temperature (oil-free centrifugal, final stage) | 40–60 °C after aftercooler | Before aftercooler may be 150–200 °C |
| Inter-stage temperature (after intercooler) | 35–45 °C | "Approach temperature" to cooling water typically ≤15 °C |
| Suction temperature | Ambient ±5 °C | Varies with seasonal conditions |
| Bearing temperature (tilting-pad journal, centrifugal) | 60–85 °C [unverified] | API 617 8th ed. previously allowed ≤100 °C; practical limit per OEM ~90–95 °C |
| Lube oil supply temperature | 38–55 °C | Pre-bearing entry; OEM typically 40–55 °C; start permissive >30 °C [source: instrumentationtools.com] |
| Lube oil pressure | 1.5–3.5 bar(g) [unverified] | Supply to bearings; exact value OEM-specific |
| Shaft vibration (proximity probe, 1× synchronous) | <12–18 µm peak-to-peak [unverified] | API 617 formula: √(12,000/N) mils max; at 10,000 rpm ≈ 34 µm (1.1 mil); at 18,000 rpm ≈ 22 µm (0.87 mil) |
| Casing vibration (RMS velocity) | <2.3 mm/s RMS (Zone A) | ISO 10816-3 Zone A = newly commissioned; Zone B ≤ 4.5 mm/s = acceptable |
| Motor current | Within nameplate ±5% | Deviations indicate capacity changes or mechanical binding |

**Screw compressor specifics (oil-injected):**  
- Discharge temperature (normal): 75–95 °C [source: multiple manufacturers, confirmed via web search]  
- Discharge pressure: 7–10 bar(g) typical  
- Bearing temperature: 55–80 °C [unverified]  

**Reciprocating compressor specifics:**  
- Cylinder discharge temperature: set per stage design; typically 120–160 °C for air service [unverified]  
- Piston rod packing temperature: <90 °C [unverified]  

---

## 5. Defect / Failure Readings — What Changes and When

### 5.1 Centrifugal Compressor — Surge

**What it is:** Flow reversal when compressor operates left of the surge line (too low flow, too high pressure ratio). Gas column oscillates backward through impeller.  
**Sensor signatures:**  
- Sudden large oscillation in suction/discharge pressure (±10–30% of normal within 0.1–0.5 s)  
- High-amplitude shaft vibration spike — can exceed 2–3× normal in one cycle  
- Axial position shifts  
- Audible bang / rhythmic thumping  
- Motor current surges  
**Typical threshold:** Anti-surge valve opens at surge control line (~10% margin from surge curve); alarm at ≥1 surge event; trip at ≥3 surges / 10 s [source: Baker Hughes / Bently Nevada literature]  
**Cause:** Reduced demand with no recycle, fouled inlet filter, IGV malfunction, cooler blockage  

### 5.2 Bearing Failure (all types)

**Earliest sign — weeks before failure:**  
- Bearing temperature rising trend (>2 °C/day sustained) [unverified trending threshold]  
- Oil analysis: elevated Fe, Cu, Pb wear metals (ferrography detects before any vibration change)  
- Subtle sub-synchronous vibration at bearing defect frequencies (BPFI, BPFO, BSF, FTF) — detectable with spectrum analysis  

**Mid-stage (days before):**  
- Bearing temperature: >95–105 °C → alarm; >110–120 °C → trip [unverified, based on API 617 guidance and OEM norms]  
- Vibration amplitude increasing: shaft vibration >2× baseline; casing vibration crossing Zone C (>7.1 mm/s RMS per ISO 10816-3)  
- Lube oil return temperature elevated  

**Acute failure:**  
- Vibration spikes to 3–10× normal  
- Bearing temperature runaway >120 °C  
- Possible oil pressure drop (damaged surfaces create bypass paths)  
- Machine trip on vibration danger setpoint  

**Typical danger setpoints (centrifugal) [unverified]:**  
- Shaft vibration trip: 50–75 µm peak-to-peak (varies by speed and clearance)  
- Bearing temperature trip: 110–121 °C (235–250 °F per Turbomachinery Magazine)  
- Lube oil low-pressure trip: 0.8–1.0 bar(g) [unverified]  

### 5.3 Seal Failure (Labyrinth / Dry Gas Seal)

**Signs:**  
- Oil carryover in discharge air (for oil-seal types) — increased lube oil consumption >10% from baseline  
- Process gas leakage → rising bearing environment temperature  
- Vibration increase (seal rub): sub-synchronous components, 1× amplitude increase  
- Seal gas flow change (DGS monitoring): abnormal primary vent flow >15% of setpoint [unverified]  
- Audible hiss or oil mist visible at seal housings  

### 5.4 Reciprocating Compressor — Valve Failure

**Most common failure mode** in reciprocating compressors.  
**Signs:**  
- Suction valve failure: elevated discharge temperature of that stage, reduced flow; suction pressure may rise  
- Discharge valve failure: elevated inter-stage temperature, reduced capacity; knock/rattle from valve cage  
- Discharge temperature rise: flag at >10 °F (5.5 °C) per week [source: Relia magazine]  
- PV analysis (pressure-volume trace) distortion from normal card shape  
- Monitoring frequency: daily discharge temperature check; cylinder temperature trending is primary PdM tool  

### 5.5 Intercooler Fouling

**Signs:**  
- Inter-stage temperature rise: approach temperature to cooling water increases from design ~10 °C toward >20–25 °C [unverified]  
- Increased specific power (kWh/100 Nm³) without demand change  
- Reduced surge margin (impellers see higher pressure ratio → shift toward surge line)  
- Higher next-stage discharge temperature  
- Detection: track inter-stage temperature against ambient and cooling water temperature continuously  

### 5.6 Lube Oil System Failure

**Signs:**  
- Low oil pressure alarm → standby oil pump auto-starts  
- Oil pressure continuing to fall after pump start → trip  
- High oil temperature: oil cooler failure or high ambient  
- Oil discoloration, milky appearance → water ingress; dark/varnish smell → oxidation  
- Oil analysis: viscosity out of spec, elevated acid number, water content >0.1%, metallic particles  

### 5.7 Screw Compressor — Rotor Wear / Oil Separator Degradation

**Signs:**  
- High oil carryover in discharge air (excess oil downstream, failed coalescing element)  
- High differential pressure across oil separator: >1.0 bar over new baseline → replacement needed  
- Elevated discharge temperature (>105 °C → alarm; >110–115 °C → trip) due to reduced oil injection cooling  
- Airend bearing failure: vibration (if monitored) rises; abnormal noise (grinding, squealing); eventual rotor contact  

### 5.8 Summary of Key Threshold Table

| Measurement | Normal | Alarm (Alert) | Trip (Danger) | Failure Mode |
|---|---|---|---|---|
| Bearing temp (centrifugal, tilting-pad) | 60–85 °C | 95–100 °C | 110–121 °C | Bearing failure, lube issue |
| Shaft vibration (centrifugal, proximity) | <18–25 µm pk-pk | ~2× baseline | Per API 617 formula + OEM factor | Unbalance, rub, surge |
| Casing vibration (ISO 10816-3) | <2.3 mm/s (Zone A) | 4.5–7.1 mm/s (Zone C entry) | >7.1 mm/s (Zone D) | General mechanical fault |
| Lube oil pressure | 1.5–3.5 bar | Low alarm (~1.5 bar) | Trip ~0.8–1.0 bar | Oil pump failure, blockage |
| Lube oil supply temperature | 38–55 °C | >65 °C | >75 °C | Cooler failure |
| Discharge temp (screw, oil-injected) | 75–95 °C | >105 °C | >110–115 °C | Cooler failure, oil starvation |
| Cylinder discharge temp (recip) | Design value | +5.5 °C/week trend | >150–175 °C | Valve failure, ring wear |
| Inter-stage approach temperature | ≤10–15 °C | >20 °C vs. design | >25 °C | Intercooler fouling |
| Oil separator ΔP (screw) | Baseline | +0.5 bar over new | +1.0 bar over new | Coalescing element blocked |
| Surge events | 0 | ≥1 event (alarm) | ≥3 events / 10 s | Flow reversal, system fault |

*All threshold values marked [unverified] — confirm against specific OEM documentation.*

---

## 6. Failure Modes — Mechanisms, Earliest Signs, Timeline

### 6.1 Surge (Centrifugal)

- **Mechanism:** Flow falls below minimum stable flow at operating pressure ratio. Gas velocity in impeller drops to zero and reverses. Can occur in milliseconds.  
- **Root causes:** Sudden demand drop (plant trip), blocked inlet filter, fouled cooler raising pressure ratio, IGV stuck open, control system failure  
- **Earliest signs:** Approach toward surge line on performance map (flow dropping, pressure rising); anti-surge controller opening recycle valve  
- **Timeline:** Single surge → structural fatigue damage; repeated surges (10–100 events) → impeller cracking, bearing damage, seal damage  
- **PdM indicator:** Trend of anti-surge valve opening frequency; flow margin to surge line  

### 6.2 Bearing Failure (all compressor types)

- **Mechanism:** Oil film breakdown → metal-to-metal contact → abrasive wear → overheating → seizure  
- **Root causes:** Lube oil contamination (water, particles), oil degradation (varnish), incorrect viscosity, starvation during startup/shutdown, overloading from misalignment or unbalance  
- **Earliest signs (weeks out):** Wear metal increase in oil analysis; bearing defect frequencies in vibration spectrum  
- **Mid-stage (days out):** Temperature rise trend, broadband vibration increase  
- **Acute:** Alarm → trip within minutes  
- **Timeline to failure from first oil-analysis signal:** 2–8 weeks typically [unverified]  

### 6.3 Mechanical Seal / Labyrinth Seal Failure

- **Mechanism:** Clearance growth (labyrinth) → cross-leakage; DGS face contamination or face wear → leakage past primary seal  
- **Earliest sign:** Increased seal gas consumption, oil in discharge, mist at housing  
- **Secondary sign:** Vibration from rub if clearance collapses  

### 6.4 Reciprocating Valve Failure

- **Mechanism:** Valve plate fatigue fracture, carbon buildup jamming plate open, corrosion  
- **Earliest sign:** Cylinder temperature deviation (trending 5–10 °C above baseline)  
- **Confirmed:** PV card distortion, reduced capacity  
- **Timeline from first temperature rise:** Days to weeks  
- **Consequence:** Reduced compression efficiency, lost capacity, eventually rod-load reversal → bearing and rod damage  

### 6.5 Intercooler Fouling / Blockage

- **Mechanism:** Scale, biofilm, oil deposits on tube surfaces reduce heat transfer  
- **Earliest sign:** Approach temperature creeping up; specific power increase  
- **Timeline:** Weeks to months (gradual)  
- **Consequence:** Thermal overload, reduced flow capacity, surge margin reduction  

### 6.6 Lube/Oil System Failure

- **Mechanism:** Oil pump failure, blocked filter, oil leak, oil degradation  
- **Earliest sign:** Low-pressure alarm triggering standby pump; oil analysis showing degradation  
- **Acute:** Low-pressure trip → immediate shutdown (no delay allowed per API 670)  
- **Consequence without intervention:** Bearing seizure within minutes  

---

## 7. Repair and Resolution Process

### 7.1 Bearing Replacement (Centrifugal, Tilting-Pad Journal)

- **Process:** Isolate and depressurize → open casing/bearing covers → remove old pads (check babbitt erosion, scoring) → fit new pads with correct clearances → align shaft → close → flush lube system → run-in  
- **Time:** 1–3 days for planned; 3–5 days for emergency (parts lead time risk)  
- **Interval (planned):** 20,000–40,000 operating hours, or condition-triggered  

### 7.2 Seal Replacement

- **Labyrinth seals:** Relatively quick — 4–8 hours for access and replacement  
- **Dry gas seals (DGS):** More involved — 1–3 days; requires specialized kits and clean room conditions for assembly  

### 7.3 Impeller / Rotor Overhaul

- **Scope:** Remove rotor bundle, check impeller blade erosion/cracks (dye penetrant test), balance rotor, inspect diffusers  
- **Time:** 5–10 days planned outage  
- **Interval:** 3–5 years (major overhaul); annual minor inspection  

### 7.4 Reciprocating Compressor Valve Replacement

- **Most common planned maintenance task** on recips  
- **Process:** Isolate cylinder → remove valve cover → extract valve cage → fit new plates/springs/seat → reassemble  
- **Time:** 2–8 hours per cylinder valve (simple), longer for multi-cylinder machines  
- **Interval (calendar):** 8,000–16,000 operating hours; condition-based preferred  

### 7.5 Screw Compressor Airend Overhaul

- **Process:** Remove airend → strip bearings, rotors, shaft seals → measure rotor tip clearances → replace bearings and seals → reassemble and test  
- **Time:** 2–5 days  
- **Interval:** 20,000–30,000 hours [source: Minnuo / industry literature]  

### 7.6 Intercooler Cleaning / Replacement

- **Tube-side cleaning:** Chemical descaling (offline, 4–8 hours) or hydroblasting  
- **Tube bundle replacement:** 1–3 days depending on size  
- **Interval:** Typically at major overhaul or condition-triggered  

### 7.7 Major Overhaul (Centrifugal, Full)

- **Frequency:** Every 3–5 years (condition-based approach preferred over fixed schedule)  
- **Duration:** 5–14 days planned outage  
- **Scope:** Full disassembly, impeller inspection, rotor balance, all bearings/seals replaced, intercoolers cleaned/replaced, lube system flushed, gearbox inspection  
- **Planned vs. Unplanned MTTR:** Planned overhaul = 5–14 days; unplanned emergency bearing failure = 3–7 days (if parts on shelf) up to 4–6 weeks (if rotor damage requires OEM repair)  

---

## 8. Cost and Production Loss Impact

### 8.1 Instrument Air Failure — Cascading Plant-Wide Consequence

Instrument air compressors serve **every pneumatic control valve in the plant**. Loss of instrument air pressure:  
- Control valves lock in their fail-safe position (air-to-close → open; air-to-open → close)  
- BOF oxygen lance control fails → charge in vessel is uncontrolled  
- CCM mold level control fails → break-out risk  
- BF blast stove valve sequencing fails → hot blast disruption  
- **Effect:** Within 15–45 minutes, multiple production units must be manually held or emergency-stopped  
- **Recovery:** Even after air is restored, particulate flushed into positioner tubing can block instrument valve positioners → secondary damage [source: Instrument Air System / Power Plant Manual]  

### 8.2 ASU Compressor Failure — Oxygen Supply Interruption

- BOF requires ~55–60 Nm³ O₂ per tonne of steel for blowing; no oxygen → no BOF heats  
- BF tuyere enrichment lost → furnace productivity down ~10–20%  
- **Oxygen storage buffers** (high-pressure receivers, liquid O₂ backup) typically provide 30–120 minutes of operation; beyond that → controlled blast furnace wind-down or BOF suspension  
- ASU restart after compressor trip: cold-box warm-up and re-cool takes **6–24 hours** depending on type and how long it was down  
- **Single-train ASU failure at 1 MTPA BOF shop:** Direct production loss of 2,000–3,500 t/day of liquid steel  

### 8.3 BF Blower Failure

- Loss of blast → BF must be "banked" (damped down) within minutes  
- Un-banking and restoring full blast after repair: 12–48 hours  
- A single unplanned BF stop costs the equivalent of 4,000–12,000 tonnes of hot metal production at $200–400/t HM [unverified — depends on current HM price and plant size]  

### 8.4 Downtime Cost Benchmarks (Integrated Steel)

- **Industry benchmark, integrated steel plant, unplanned stop:** $500,000–$1,200,000 per hour [source: oxmaint.com steel plant analysis, ifactory analysis 2026]  
- **Cascade effect documented:** A single $340 seal failure → $1.2 M total production + quality + schedule loss [source: ifactory case study]  
- **Compressor bearing failure during peak demand:** System pressure drops below critical threshold → BOF hold within 45 minutes → entire production sequence disrupted [source: oxmaint.com]  
- **Energy cost:** A 5% specific power increase on a 2 MW compressor running 8,000 h/year → ~₹80–100 lakh/year additional energy cost [unverified rough calc at ₹6/kWh]  
- **Leak losses:** 840 CFM of leaks found in one mid-size plant survey = significant energy waste; ultrasonic detection can recover 20–30% energy [source: f7i.ai PdM playbook]  

### 8.5 Safety Consequences

- **Instrument air loss:** Control valves going to unsafe position can cause runaway process conditions (thermal runaway in furnaces, pressure buildup)  
- **COG / BFG compressor failure:** Hazardous gas release risk (CO poisoning, explosion risk H₂-rich COG); fire and explosion hazard  
- **High-pressure oxygen compressor failure:** O₂-enriched atmosphere near failure point — fire/explosion severity multiplied  
- **Lubrication oil fire:** Lube oil under pressure meeting hot surfaces (shaft, bearing) → oil mist ignition risk  

---

## 9. Predictive Maintenance Strategy Summary

### Priority Monitoring by Machine Criticality

| Machine | Criticality | Primary PdM Methods | Monitoring Frequency |
|---|---|---|---|
| Instrument air centrifugal | P0 — single-point-of-failure | Vibration (online, continuous), bearing temp (online), discharge pressure, oil analysis | Continuous + quarterly oil sample |
| ASU main air compressor | P0 | Same as above; inter-stage temperature; seal gas monitoring | Continuous |
| BF blower | P0 | Shaft vibration (continuous), bearing temp, surge monitoring | Continuous |
| Screw compressors (utility) | P1 | Discharge temperature, oil separator ΔP, bearing vibration | Online + monthly route |
| Reciprocating (high-pressure) | P1 | Cylinder temperature trending (daily), PV analysis quarterly, lube oil daily | Daily manual + quarterly PV |
| COG / BFG compressors | P1 | Vibration, discharge pressure, seal leak detection | Continuous vibration; weekly manual |

### Key PdM Algorithms for Steel Plant Compressors

1. **Surge count / rate trending** — anomaly if surge frequency increasing over 7-day rolling window  
2. **Bearing temperature rate-of-change** — alert if ΔT > 2 °C/day sustained for ≥3 days  
3. **Specific power tracking** — baseline kWh/100 Nm³; alert at >5% sustained deviation (fouling or seal wear)  
4. **Inter-stage approach temperature** — baseline vs. cooling water temperature; alert at +10 °C above design  
5. **Oil wear metal trending** — Fe, Cu, Pb concentration rate-of-increase vs. expected wear rate  
6. **Vibration spectrum waterfall** — track sub-synchronous amplitude at 0.4×–0.49× N (oil whirl precursor) and bearing defect frequencies  
7. **Anti-surge valve position duration** — sustained open position signals compressor operating near or in surge zone  

---

## 10. Additional Context: Tata Steel-Specific

- **Tata Steel, Kalinganagar (5 MTPA):** Water-injected compressor units documented in process gas compression service [source: GreenSteelWorld, SMS Group COG injection project].  
- **ASU integration:** Tata Steel's integrated plants have on-site ASUs with large centrifugal MACs; oxygen produced is directly piped to BOF, BF enrichment, and secondary metallurgy. Disruption to MAC = direct BOF production impact within 30–120 min.  
- **COG compression for BF injection:** Tata Steel contracted SMS Group for COG injection technology (2025); compressor selection (temperature range, centrifugal vs. recip) was cited as a critical success factor [source: GreenSteelWorld].  
- **Instrument air specificity:** At Tata Steel scale, instrument air header pressure is typically maintained at 5.5–7.0 bar(g) with multiple redundant compressors and a receiver bank (storage volume) for ride-through. Loss of one machine should not cause a process trip if system is correctly designed; loss of two machines or a distribution rupture causes plant-wide impact.  

---

## Sources

- [Compressed Air & Gas System Maintenance for Steel Plants — oxmaint.com](https://oxmaint.com/industries/steel-plant/compressed-air-gas-system-maintenance-steel-plants) — Industry maintenance guide, steel plant specific
- [Compressor Predictive Maintenance — f7i.ai 2025 Playbook](https://f7i.ai/blog/compressor-predictive-maintenance-the-ultimate-2025-implementation-playbook) — PdM methods, failure modes, cost impact
- [Vibration Monitoring of Integrally Geared Centrifugal Air Compressor — Metrix/Modern Pumping Today](https://modernpumpingtoday.com/vibration-monitoring-of-an-integrally-geared-centrifugal-air-compressor/) — API 670 sensor placement
- [Centrifugal Compressor Vibration Testing and Analysis — inspection-for-industry.com](https://www.inspection-for-industry.com/centrifugal-compressor-vibration.html) — API 617 vibration limits
- [API 670 Machinery Protection Systems — Meggitt](https://meggittsensing.com/energy/expert-articles/general-api-670-requirements-for-machinery-protection-systems/) — Standard requirements
- [Reciprocating Compressor Maintenance — Relia Magazine](https://reliamag.com/articles/reciprocating-compressor-maintenance/) — Failure modes, overhaul intervals
- [Screw Compressor Discharge Temperature — UNITEC Industrial](https://www.unitecd.com/troubleshooting-screw-compressor-high-discharge-temperature-a-comprehensive-guide/) — Alarm/trip temperature values
- [Centrifugal Compressor Start Permissive and Interlocks — InstrumentationTools](https://instrumentationtools.com/centrifugal-compressor-start-permissive-and-interlocks/) — Lube oil temperature ranges
- [Unplanned Downtime Steel Plants — oxmaint.com](https://oxmaint.com/industries/steel-plant/unplanned-downtime-steel-plant-causes-costs-solutions) — Cost benchmarks
- [Critical Asset Management Steel Plants — ifactory](https://ifactoryapp.com/industries/steel-plant/critical-asset-management-steel-plants-blast-furnaces-bof-eaf) — Downtime cost data
- [Compressor Surge Detection — Baker Hughes / Bently Nevada](https://www.bakerhughes.com/bently-nevada/orbit-home/orbit-article/reciprocating-compressor-condition-monitoring-q2) — Surge logic, 3 surges/10 s trip
- [ISO 10816-3 Vibration Zones — DSP Analytic](https://dspanalytic.com/en/vibrations/understanding-the-iso-10816-3-vibration-severity-table/) — Zone boundary values
- [Tata Steel COG Injection — GreenSteelWorld](https://greensteelworld.com/tata-steel-selects-sms-group-for-coke-oven-gas-injection-technology) — Compressor selection context
- [Instrument Air System Failure — Power Plant Manual](https://powerplantmanual.com/instrument-air-system-in-power-plant/) — Instrument air criticality
- [Compressor Intercooler Maintenance — FS-Elliott](https://www.fs-elliott.com/blog/understanding-air-compressor-intercooler-maintenance) — Fouling symptoms
- [Compressor Downtime True Cost — Industrial Air Service](https://www.industrialairservice.com/news-nashville-townhall/the-true-cost-of-compressor-downtime-and-how-to-avoid-it) — Downtime cost quantification
- [Centrifugal Compressor Seal Failure — Turbo Air Tech](https://www.turboairtech.com/blog/compressor-seal-guide-types-failure-maintenance) — Seal failure signatures
- [Compressor Overhaul Guide — Swamina International](https://swaminainternational.com/blog/industrial-compressor-major-overhauling-benefits/) — Overhaul scope and timing

---

*Document status: Research compilation for Tata Steel Round 2 — Maintenance Wizard system. Numeric thresholds marked [unverified] must be validated against OEM manuals and actual plant DCS setpoint records before use in ML model target engineering.*
