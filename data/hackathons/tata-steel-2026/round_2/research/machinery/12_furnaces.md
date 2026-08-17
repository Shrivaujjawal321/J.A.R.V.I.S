# Furnaces — Predictive Maintenance Reference
## Integrated Steel Plant Scale (Tata Steel context)
*Research compiled 2026-06-08 for Tata Steel Round 2 Agentic AI Challenge*

---

## 1. FURNACE TYPES AND SUB-SYSTEMS

### 1.1 Reheating Furnaces (Hot Strip Mill — HSM)

Three main types in modern integrated plants:

| Type | How it works | Typical capacity | HSM use |
|------|-------------|-----------------|---------|
| **Walking beam** | Water-cooled beams lift + step slabs forward | 300–500 t/hr | Primary modern choice |
| **Pusher** | Hydraulic pusher ram advances slabs on fixed skids | 150–300 t/hr | Older installations; simpler |
| **Rotary hearth** | Circular rotating floor; billets/blooms in ring | 50–200 t/hr | Special sections, pipe mills |

**Sub-systems (walking beam / pusher):**
- **Heating zones** (3–4 zones): preheat → heating → soaking; each independently fired
- **Burners**: top-firing, bottom-firing, or cross-firing; regenerative or recuperative
- **Recuperator**: shell-and-tube or rotary ceramic; recovers heat from flue gas to pre-heat combustion air
- **Water-cooled skid system**: longitudinal and cross-directional pipes + insulating skid buttons (walking beam only — moving + fixed beams)
- **Walking beam hydraulics**: 2× hydraulic cylinders (lift + traverse); eccentric shafts; servo-valves
- **Refractory lining**: multi-layer ceramic fibre + dense castable + brick; typical thickness 350–600 mm
- **Flue gas / waste-heat duct**: dampers, draft fans, stack
- **Discharge roller table**: rolls slab to roughing mill

### 1.2 Blast Furnace Mechanicals

Sub-systems relevant to PdM (not the process chemistry — see separate doc):

| Sub-system | Description |
|-----------|-------------|
| **Hot blast stoves (Cowper stoves)** | 3–4 stoves per BF; alternate on-gas (combustion, dome 1,300–1,550°C) and on-blast (preheated air ~1,100–1,250°C to tuyeres) |
| **Checker chamber / checker brick** | Silica or high-alumina brick stack that stores + releases heat; 30–50 m tall stove |
| **Stove valves** | Gas intake, air intake, blast main valves; ~10 s cycle time |
| **Bell-less top (Paul Wurth type)** | Rotating distribution chute + upper/lower seal valves; distributes burden (ore/coke/sinter) |
| **Tuyeres + tuyere coolers** | 20–42 copper water-cooled nozzles around hearth circumference; blast at ~1,100°C + PCI coal injection |
| **Cooling staves** | Copper or cast-iron plates bolted to shell in bosh/belly/stack; coolant flowing through internal pipes |
| **Hearth + taphole** | Refractory skull; carbon blocks; 2–4 tapholes; ceramic taphole clay gun |
| **Shell & cooling plates** | Outer steel shell; 500+ monitoring thermocouples + flowmeters |

### 1.3 Annealing / Galvanizing Furnaces (CAL / CGL)

| Furnace | Process | Temperature range |
|---------|---------|-----------------|
| **Continuous Annealing Line (CAL)** | Strip recrystallization in N₂/H₂ atmosphere; radiant tube heating | 700–900°C |
| **Continuous Galvanizing Line (CGL) annealing section** | Pre-galvanizing anneal + atmosphere furnace | 650–850°C |
| **CGL zinc pot** | Liquid zinc bath; strip dips through; coating applied | 445–460°C (zinc bath) |
| **CGL galvannealing furnace (GA)** | Induction or radiant-tube heating post-pot for Fe-Zn alloying | 480–550°C |

**Key sub-systems (CAL/CGL):**
- **Hearth rolls**: alloy rolls (~700–1,000 mm dia) supporting strip; driven by individual gearboxes
- **Radiant tubes**: gas-fired U-shape or W-shape Inconel/silicon carbide tubes; heat without direct flame contact
- **Strip tension control**: bridle rolls + load cells
- **Zinc pot heating**: induction coil (modern) or gas-fired immersion tubes; zinc at 445–460°C
- **Air knife / wiping nozzles**: N₂ gas knives control coating weight
- **Dross removal system**: top-dross + bottom-dross skimming; dross pumps
- **Pot roll assembly**: submerged sink roll + stabilizer rolls; subject to zinc erosion

---

## 2. PARTS BREAKDOWN (PdM-relevant components)

### Reheating Furnace

| Component | Material / Spec | PdM priority |
|-----------|----------------|-------------|
| Burner tip / nozzle | Alloy steel or ceramic | High |
| Burner gas/air control valve | Pneumatically actuated | Medium |
| Recuperator tubes | Stainless or ceramic | High |
| Walking beam eccentric shaft | Forged steel, oil-bath bearing | High |
| Walking beam hydraulic cylinder seals | Polyurethane seals, 200 bar | Medium |
| Water-cooled skid pipe | 100–150 mm dia carbon steel; internal scale | High — steam explosion risk |
| Skid insulating buttons / refractory pads | High-alumina castable | Medium |
| Furnace refractory lining | Silica / alumina brick + fibre backup | High |
| Flue gas damper actuator | Electro-pneumatic | Low |
| Discharge roller | Cast iron + water cooling | Medium |

### Blast Furnace Mechanicals

| Component | Material / Spec | PdM priority |
|-----------|----------------|-------------|
| Tuyere (nozzle body) | Wrought copper; water-cooled double wall | Critical |
| Tuyere cooler (blowpipe/tuyere assembly) | Copper with drilled cooling channels | Critical |
| Cooling stave (bosh/belly) | Cast iron or copper; 4× internal pipes | Critical |
| Cooling stave (stack) | Cast iron; 2-pipe | High |
| Hot stove dome refractory | Silica brick (must stay >600°C) | High |
| Checker brick | High-alumina or silica | Medium |
| Stove gas/blast valve | DN500–900 high-temp metal seat | High |
| Bell-less top distribution chute | Wear-resistant cast iron | Medium |
| Top seal valve seats | Alloy steel; cooled | Medium |
| Taphole drill / clay gun | Hydraulic; drill bit wear | Medium |

### CAL / CGL Furnace

| Component | Material / Spec | PdM priority |
|-----------|----------------|-------------|
| Hearth roll barrel | Ceramic sprayed alloy (Fe-Cr base) | High |
| Hearth roll bearing (furnace end) | Graphite-lubricated high-temp | High |
| Hearth roll drive motor | AC inverter | Medium |
| Radiant tube | Si₃N₄ SiC or Inconel 601 | Medium |
| Zinc pot induction coil | Water-cooled copper | High |
| Sink roll / stabilizer roll (zinc pot) | Fe-Al intermetallic resistant alloy | High |
| Air knife nozzle | Stainless; zinc clogging | Medium |
| Strip tension load cell | Strain gauge | Medium |

---

## 3. SENSORS AND MOST COMMON READINGS

### 3.1 Reheating Furnace Sensors

| Sensor | Location | Signal type | Normal value |
|--------|----------|------------|-------------|
| Zone thermocouple (Type S / Type B) | Furnace roof + hearth, each zone | mV → 0–10V | 1,050–1,260°C (zone-dependent; see §4) |
| Discharge pyrometer (IR / radiation) | Furnace exit, aimed at slab top surface | 4–20 mA | 1,150–1,250°C |
| Flue gas O₂ analyzer | Waste-gas duct, per zone | % O₂ | 1–3% excess O₂ (reducing-neutral atmosphere) |
| Combustion air flow (orifice plate / vortex) | Burner air supply header | 4–20 mA | Varies by zone load; ratio-controlled |
| Fuel gas flow (coriolis / orifice) | Burner fuel supply | 4–20 mA | Varies; track GJ/tonne KPI |
| Furnace pressure (draft) | Near roof, flue end | Pa gauge | 0–20 Pa positive draft |
| Cooling-water flow (electromagnetic) | Skid pipe circuits, each beam | 4–20 mA + HART | 100% nominal (alert: <85%) |
| Cooling-water inlet/outlet temp (RTD Pt100) | Per skid pipe circuit | 4–20 mA | ΔT = 5–15°C; outlet <40°C |
| Shell temperature (IR camera / contact TC) | Furnace outer shell | °C | Baseline; hotspot >50°C above baseline = alert |
| Hydraulic pressure (walking beam) | Lift + traverse cylinders | bar | Lift: 80–120 bar nominal |
| Drive bearing vibration (accelerometer) | Eccentric shaft bearings | mm/s RMS | <2.8 mm/s (ISO 10816 zone A) |
| Recuperator differential pressure | In/out of recuperator | kPa | Stable baseline; rising ΔP = fouling |
| Fuel/tonne KPI | SCADA calculated | GJ/t | 1.0–1.5 GJ/t; alert on +3% over 4 weeks |

### 3.2 Blast Furnace Mechanical Sensors

| Sensor | Location | Normal value |
|--------|----------|------------|
| Tuyere cooling-water outlet temp (RTD) | Per tuyere, 20–42 channels | <55°C; alert >55°C for >10 min |
| Tuyere cooling-water flow (EM flowmeter) | Per tuyere circuit | Baseline; ΔP alarm >0.15 bar |
| Stave cooling-water ΔT (RTD pair) | Per stave circuit (500+ total) | 10–30°C depending on zone |
| Stave cooling-water flow (EM, DN32–80) | Per stave circuit (530+ sensors) | >90% of baseline; <2.0 m/s = alarm |
| Shell thermocouple | Outer shell behind staves | <80°C hotspot threshold |
| Hearth refractory thermocouple (Type K) | 200+ embedded, 4–5 levels | 200–600°C (monitoring erosion front) |
| Top gas temp (4-point cross, TC) | Stockline/throat area | 150–400°C; asymmetry >12°C = alarm |
| Top gas composition analyzer (CO, CO₂) | Throat off-take | CO₂/(CO+CO₂) = 0.45–0.55 (ηCO) |
| Blast pressure | Hot blast main | 3–5 bar (plant-specific) |
| Blast volume flow | Hot blast main | 3,000–10,000 Nm³/min (furnace size) |
| Hot stove dome temperature (TC Type S) | Stove dome | On-gas: 1,300–1,550°C; limit = brick max rating |
| Stove waste-gas outlet temp | Stove flue | <400–450°C; rising = checker fouling |
| Stove valve position + cycle time | Each stove valve | ~10 s per cycle; increasing = wear alarm |
| Bell-less top chute position (encoder) | Distribution chute | ±0.1° accuracy; drift = maldistribution |
| Skip / conveyor load cell | Charging conveyor | Batch weight ±0.5% |
| Ultrasonic stave thickness | Bosh staves (portable or online) | Trending; >2 mm/week thinning rate = alert |

### 3.3 CAL / CGL Furnace Sensors

| Sensor | Location | Normal value |
|--------|----------|------------|
| Zone temperature (TC Type K/S) | Each heating zone, furnace roof | CAL: 700–900°C; CGL preheat: 650–850°C |
| Strip surface pyrometer (IR) | At each heating/cooling zone exit | ±5°C of setpoint |
| Hearth-roll drive motor current (CT) | Each roll drive panel | Baseline per roll; rising current = pickup buildup |
| Hearth-roll bearing temperature (RTD) | External bearing housings | <120°C; >150°C = alert |
| Strip tension load cell | Bridle rolls | Setpoint ±5%; snap-risk if zero |
| Furnace atmosphere analyzer (H₂, dew-point) | N₂/H₂ atmosphere sampling | H₂ 2–20% (grade dependent); dew-point < −30°C |
| Zinc pot temperature (immersion TC) | Zinc bath, 2–3 points | 445–460°C; <440°C = solidification risk; >480°C = coating defects |
| Zinc pot induction coil current | Induction power supply | Nominal per heat load; drop = coil fault |
| Coating weight (X-ray fluorescence, both faces) | Post-air-knife | Grade setpoint ±3 g/m² |
| Air knife pressure / flow | N₂ header | 0.1–0.8 bar (grade-dependent) |
| Radiant tube skin temperature (TC) | External tube surface | <1,050°C rated max |
| GA inductor temperature | GA inductor block | <85°C coil temp; rising = insulation degradation |

---

## 4. NORMAL READINGS PER SENSOR — SUMMARY TABLE

### Reheating Furnace Zone Temperature Targets (walking beam, slab ~250 mm)

| Zone | Top firing setpoint | Bottom firing setpoint | Purpose |
|------|-------------------|----------------------|---------|
| Preheat (Zone 1) | 900–1,050°C | 850–1,000°C | Gradual thermal soak |
| Heating (Zone 2) | 1,180–1,240°C | 1,150–1,210°C | Bulk heat input |
| Soaking (Zone 3) | 1,200–1,260°C | 1,180–1,240°C | Temperature equalisation |
| **Discharge pyrometer target** | — | — | **1,150–1,250°C** |

*Source: [IspatGuru — Heating of Steel in Reheating Furnace](https://www.ispatguru.com/heating-of-steel-in-reheating-furnace/)*; temperature setpoints also in [Griffin Open Systems white paper](https://www.griffinopensystems.com/wp-content/uploads/2020/11/GOS-Reheat-Furnaces-White-Paper-.pdf)

### Blast Furnace Cooling Water Normal Parameters

| Parameter | Normal | Source |
|-----------|--------|--------|
| Stave circuit water velocity | 2.4–2.5 m/s | [oxmaint.com BF cooling](https://oxmaint.com/industries/steel-plant/blast-furnace-cooling-monitoring-real-time) |
| Stave cooling ΔT | 10–30°C zone-dependent | ibid. |
| Stave water inlet temp | 25–40°C | ibid. |
| Water conductivity | 1,400–1,600 µS/cm | ibid. |
| Supply–return flow balance | <1% differential | ibid. |
| Tuyere outlet temp | <55°C | [oxmaint.com tuyere](https://oxmaint.com/industries/steel-plant/blast-furnace-tuyere-maintenance-inspection-replacement) |

### Hot Stove Normal Parameters

| Parameter | Normal | Source |
|-----------|--------|--------|
| Dome temperature (on-gas) | 1,300–1,550°C | [oxmaint.com stove](https://oxmaint.com/industries/steel-plant/hot-blast-stove-maintenance-refractory-valve-inspection) |
| Blast delivery temperature | 1,100–1,250°C | ibid. |
| Waste gas outlet temp | <400–450°C | ibid. |
| Blast delivery duration per cycle | ≥45 min | ibid. |

---

## 5. DEFECT READINGS PER FAILURE MODE — THRESHOLDS

### 5.1 Reheating Furnace

| Failure mode | Sensor(s) | Normal | Defect signal | Threshold / action |
|-------------|----------|--------|--------------|-------------------|
| Burner tip erosion | Fuel flow per zone, zone TC, fuel/tonne KPI | Baseline | Fuel/tonne KPI rising | +3% over 4–6 weeks → burner inspection [oxmaint] |
| Skid pipe blockage (scale) | Cooling water flow per circuit | 100% nominal | Flow drop | <85% nominal → clean / inspect [oxmaint] |
| Skid pipe overtemperature (approaching rupture) | Skid pipe skin TC | <40°C outlet | Rising outlet T with low/normal flow | Outlet >60°C + flow <85% → emergency shutdown (steam explosion risk) |
| Refractory lining thinning | Shell TC, IR camera | Baseline surface T | Localised hotspot | Shell hotspot >50°C above baseline → patch plan; >100°C → urgent [oxmaint] |
| Recuperator fouling | Recuperator ΔP, air preheat temp | Stable ΔP | Rising ΔP + falling air preheat T | Preheat temp drop >30°C from baseline over 2 months → cleaning outage |
| Walking-beam bearing fatigue | Bearing vibration (accel.) | <2.8 mm/s | Rising trend | 2–4 week advance warning before spalling [oxmaint] |
| Hydraulic seal leak (walking beam) | Hydraulic pressure loss, oil level | Stable | Pressure hunting or drop | Pressure drop >10 bar from setpoint → seal replacement |
| "Skid marks" (thermal shadow in slab) | Discharge pyrometer profile | Uniform T | Cold stripe at slab bottom | ΔT 50–100°C at slab surface stripe → adjust skid button refractory |

### 5.2 Blast Furnace Mechanicals

| Failure mode | Sensor(s) | Normal | Defect signal | Threshold / action |
|-------------|----------|--------|--------------|-------------------|
| **Tuyere burn-through** (melting loss ~85% of failures) | Tuyere outlet water T | <55°C | Sustained rising trend over 3–5 days | >55°C for >10 min → reduce blast, plan replacement; 7–14 day detection window [oxmaint] |
| Tuyere burn-through (sudden) | Cooling circuit ΔP | Stable | Sudden pressure drop | Immediate: >0.15 bar sudden drop → emergency stop blast to affected sector |
| Tuyere nose erosion | Bore diameter (weekly manual measure) | Baseline | Bore enlargement | Growing bore rate → service window in 4–8 weeks |
| Cooling stave wear (abrasive) | Stave cooling ΔT, ultrasonic thickness | Baseline ΔT | Slowly rising ΔT | 0.3°C rise over 2 weeks in bosh = 2 mm/week thinning → intensify monitoring [ifactoryapp] |
| Cooling stave "banana effect" bending | Flow variability, ΔT edge anomaly | Uniform circuit ΔT | Edge circuits show T anomaly | Asymmetric ΔT > 5°C within stave → stave inspection |
| Cooling stave leak (water ingress to BF) | Flow imbalance (supply vs return) | <1% differential | Differential rise | >3% differential → immediate investigation; water + molten iron = explosive [oxmaint] |
| Shell hotspot (refractory loss) | Shell TC | <80°C | Spot above 80°C | >80°C → schedule replacement; rapid rise = emergency [oxmaint tuyere] |
| Hearth refractory erosion | Hearth embedded TC | 200–600°C gradient | Rising temperature at deeper levels | Level advancement of 500°C isotherm toward shell → campaign life assessment |
| Hot stove dome crack / refractory damage | Dome skin TC, dome shell TC | Baseline | Rising shell T | Localised dome hotspot → isolate stove; repair required [oxmaint stove] |
| Checker brick channelling / fouling | Stove waste-gas outlet T, blast duration | <450°C waste; ≥45 min blast | Rising waste T or shorter blast duration | Waste gas >450°C for 3+ cycles OR blast duration drop >20% → checker cleaning/reline [oxmaint stove] |
| Bell-less top chute wear / drift | Encoder position, distribution patterns | ±0.1° | Position drift; asymmetric top gas T | Top gas T asymmetry >12°C over 3 days; chute angle drift >0.4° → recalibrate/replace |
| Taphole clay gun failure | Hydraulic pressure, taphole open-close time | Normal cycle | Extended or failed opening | > 2× normal opening time → drill bit or clay gun hydraulics |

### 5.3 CAL / CGL Furnace

| Failure mode | Sensor(s) | Normal | Defect signal | Threshold / action |
|-------------|----------|--------|--------------|-------------------|
| **Hearth roll alumina/iron-oxide buildup (pickup)** | Drive motor current per roll, strip surface quality camera | Baseline current | Rising current (higher torque) | Current drift +5–10% above baseline + surface quality alert → roll removal / grinding [patent US8864869] |
| Hearth roll bearing failure | Bearing temp RTD | <120°C | Rising trend | >150°C → schedule replacement at next planned stop |
| Radiant tube crack / burnout | Zone temperature (TC) | Setpoint ±5°C | Falling zone T despite full gas flow; atmosphere O₂ spike | O₂ in furnace atmosphere (should be reducing); failing zone T → isolate tube, cap-off or replace |
| Zinc pot temperature drop (induction coil fault) | Zinc bath TC, induction coil current | 445–460°C; nominal coil current | T dropping toward solidification point | <440°C → alarm; <420°C → imminent solidification; coil current drop from nominal → fault [galvinfo] |
| Zinc pot solidification (worst case) | Zinc bath TC | 445–460°C | T below 419.5°C (Zn melting point) | FULL SOLIDIFICATION: line stop; melt-out recovery 48–72 h [industry-standard [unverified]] |
| Zinc pot dross build-up on sink roll | Zinc pot immersion camera / coating defect signal | Normal dross rate | Coating defect rate rising; dross accumulation visual | >3× normal dross → roll pull and clean; line stop 4–8 h |
| Strip break (caused by hearth roll pickup or tension excursion) | Strip tension load cell | Setpoint | Sudden tension spike to zero | Tension = 0 → immediate line stop; thread-up required: 2–6 h |
| GA inductor insulation degradation | GA inductor coil temp, power factor | <85°C; nominal power factor | Rising coil temp or power factor drift | >100°C coil temp or power factor >10% shift → service at next stop |

---

## 6. FAILURE MODES — DETAILED + EARLIEST SIGNS

### 6.1 Reheating Furnace

**Refractory wear / spalling**
- Mechanism: thermal cycling + slab abrasion → brick loosening → hot-face erosion → cold-face exposure
- Earliest sign: furnace shell thermocouple at that zone begins drifting upward (weeks–months before structural failure)
- If missed: shell glowing visible, potential hot-gas breakthrough; major relining

**Water-cooled skid pipe failure / leak**
- Mechanism: scale deposit (hard water) insulates pipe → localised overtemperature → pipe wall oxidation → pinhole crack
- Earliest sign: cooling water flow in that circuit drops below 85% nominal; outlet temperature rises
- SAFETY: water at 200+ bar steam pressure contacting 1,200°C hot slab → steam explosion, deflagration risk
- Detection window: weeks if flow-monitored; sudden if unmonitored
- Reference: [ScienceDirect — Characteristics of skid pipe failure](https://www.sciencedirect.com/science/article/abs/pii/S1350630719308684)

**Burner malfunction (tip erosion / valve sticking)**
- Mechanism: combustion erosion of orifice → irregular flame → cold spots in slab; lazy burner = fuel wasted
- Earliest sign: GJ/tonne KPI creeping up 2–5%; zone temperature becoming harder to hold at setpoint
- Detection window: 4–6 week KPI trend

**Recuperator fouling**
- Mechanism: particulate deposition from flue gas on tube bundle → higher pressure drop → less pre-heated air
- Earliest sign: rising differential pressure across recuperator; combustion air preheat temperature falling
- Impact: energy efficiency loss, higher fuel consumption

**Walking beam drive failure**
- Mechanism: eccentric shaft bearing fatigue under cyclic load
- Earliest sign: vibration signature change (2–4 week advance warning via accelerometer trending)
- Impact: entire HSM stops; emergency repair 12–24 hours [oxmaint]

### 6.2 Blast Furnace Mechanicals

**Tuyere burn-through**
- Mechanism (80–92% of cases = melting loss): slag droplets / iron splash contact tuyere nose → localised copper melt
- Earliest sign: tuyere cooling water outlet temperature begins sustained upward trend over 3–5 consecutive days
- Detection window: 7–14 days before failure when per-tuyere T trending is active
- If missed: molten iron breakthrough to tuyere cooler body → potentially explosive; forced 8–16 hour emergency stop
- Reference: [oxmaint.com tuyere maintenance](https://oxmaint.com/industries/steel-plant/blast-furnace-tuyere-maintenance-inspection-replacement); [lmmgroupcn tuyere burn-through](https://www.lmmgroupcn.com/original-ariticles-how-to-prevent-the-blast-furnace-tuyere-burning-through/)

**Cooling stave failure**
- Mechanism: abrasive wear by burden material → gradual copper thinning → water channel exposure → leakage
- Earliest sign: stave cooling ΔT rising 0.3°C over 2 weeks in bosh zone; ultrasonic thickness trending >2 mm/week loss
- Critical risk: water ingress to BF interior → steam explosion at 2,000°C iron (water at ~38 l/h into molten iron is sufficient for damaging explosion [unverified — industry reference])
- Reference: [oxmaint.com BF cooling monitoring](https://oxmaint.com/industries/steel-plant/blast-furnace-cooling-monitoring-real-time)

**Hot stove dome crack**
- Mechanism: silica brick phase transition stress during thermal cycling; differential expansion cracks
- Earliest sign: dome or combustion chamber shell temperature rising (IR survey); waste gas outlet rising over 3+ cycles
- Constraint: silica brick must never cool below 600°C during operation (phase transition causes expansion cracks) [oxmaint stove]

**Checker brick channelling**
- Mechanism: preferential gas paths form in checker → reduced thermal storage → shorter blast delivery → higher coke rate
- Earliest sign: blast delivery duration falling below 45 min; waste gas outlet temperature creeping above 400°C
- Detection window: weeks of gradual drift

**Bell-less top chute wear**
- Mechanism: impact + abrasion from ore/coke/sinter (hard, sharp-edged particles) → wear surface loss
- Earliest sign: burden distribution asymmetry (top gas temperature asymmetry >12°C East–West or North–South) + chute angle encoder drift
- Reference: burden distribution monitoring [ifactoryapp BF monitoring](https://ifactoryapp.com/industries/steel-plant/blast-furnace-ai-monitoring-sensors)

**Hearth refractory erosion**
- Mechanism: liquid iron dissolves carbon bricks over campaign; "elephant foot" erosion pattern
- Earliest sign: embedded thermocouple array shows 500°C isotherm advancing toward shell (2 mm/week threshold)
- Detection: 200+ TC array allows 3D erosion mapping; campaign end decisions based on isotherm position

### 6.3 CAL / CGL Furnace

**Hearth roll pickup (alumina / iron-oxide buildup)**
- Mechanism: Mn-oxide / Fe-oxide / Al₂O₃ from strip surface deposits on roll body → nodule grows → imprints on strip (waffle mark / dent defect)
- Earliest sign: gradual rise in roll drive motor current (torque increase) + first appearance of periodic marks on strip at coil inspection
- Detection window: days (current trending) before quality defect becomes production-scrap level
- References: [US Patent 8864869 — hearth roll](https://patents.google.com/patent/US8864869B2/en); [Patent 4470802](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/4470802)

**Zinc pot solidification**
- Mechanism: induction heater failure OR power cut → zinc bath cools below 419.5°C melting point → solid zinc locks pot hardware
- Earliest sign: pot temperature trending downward; coil current dropping from nominal
- Threshold: <440°C = alarm; <420°C = critical; <419.5°C = solidification begins
- Full solidification = 48–72 hour recovery (re-melt with portable burners + gradual heat-up to avoid thermal shock to ceramic lining) [unverified — industry known]
- Temperature management: [GalvInfo Note 2.4.1](https://www.galvinfo.com/wp-content/uploads/sites/8/2017/05/GalvInfoNote_2_4_1.pdf)

**Radiant tube crack / burnout**
- Mechanism: thermal fatigue cycling + internal oxidation → wall crack → combustion gas enters reducing furnace atmosphere → strip oxidation / adhesion
- Earliest sign: unexpected O₂ spike in furnace atmosphere analyzer (should be near zero in N₂/H₂); falling zone temperature under full gas flow
- Detection window: hours (atmosphere O₂ spike is fast indicator)

---

## 7. REPAIR / RESOLUTION PROCESSES

### Reheating Furnace Repairs

| Repair type | Trigger | Process | Duration | Planned vs unplanned |
|------------|---------|---------|----------|---------------------|
| **Full refractory relining** | Campaign end / major damage | Cool to ambient (48–72 h); demolish old lining; install ceramic fibre + castable + brick; cure dry-out (30–50 h) | 7–21 days total | Planned every 3–5 years [oxmaint] |
| **Emergency patch (hot repair)** | Localised hotspot detected | Insert refractory castable through access door; may require 4–8 h cool | 4–24 h | Unplanned |
| **Burner tip replacement** | Tip erosion / GJ/tonne KPI trigger | Shut zone; replace nozzle assemblies per zone | 4–8 h per zone | Planned at 6–12 month intervals |
| **Recuperator cleaning** | Rising ΔP | Chemical descaling or mechanical cleaning of tube bundle | 8–24 h | Planned |
| **Skid pipe repair / replacement** | Flow <85% or pipe leak | Drain circuit; cut out damaged section; weld in new; pressure test; refill | 12–48 h | Unplanned; safety critical |
| **Walking-beam bearing replacement** | Vibration trend or spalling | Cool furnace; access eccentric shaft; press out bearing; install new | 12–24 h | Planned preferred (2–4 week window) |

### Blast Furnace Mechanical Repairs

| Repair type | Trigger | Process | Duration |
|------------|---------|---------|----------|
| **Tuyere replacement (planned)** | Outlet T trend > 7–14 day window | Reduce blast; isolate tuyere zone; extract tuyere assembly; fit new; pressure-test; resume | 3–5 h per unit (planned) |
| **Tuyere replacement (emergency)** | Sudden burn-through | BF slowdown or winddown; 8–16 h repair; higher collateral risk | 8–16 h |
| **Cooling stave replacement** | Stave ΔT / ultrasonic threshold | Requires BF slowdown / partial shutdown; shell cut; stave extraction; new stave installation | 24–72 h per zone panel |
| **Hot stove dome repair** | Shell hotspot / dome TC alarm | Isolate stove (3-stove rotation absorbs); external scaffold; refractory injection or ceramic welding | 1–7 days per stove (stove offline) |
| **Checker brick reline** | Blast duration <35 min; waste-gas T high | Major shutdown; full checker dump; rebuild | 14–30 days (annual planned outage) |
| **Bell-less top chute replacement** | Wear / encoder drift | Top of BF access; crane removal of chute assembly; install new | 8–24 h (during planned top maintenance) |
| **BF major reline (campaign end)** | Hearth TC isotherm reaching shell | Full shutdown; skull removal; demolition; complete reline | 90–180 days; [oxmaint BF campaign](https://oxmaint.com/industries/steel-plant/blast-furnace-maintenance-management-cmms-guide) |

### CAL / CGL Furnace Repairs

| Repair type | Trigger | Process | Duration |
|------------|---------|---------|----------|
| **Hearth roll change** | Current trending + quality mark | Line stop; cool zone; extract roll from furnace (crane); install ground/new roll | 4–12 h per roll |
| **Radiant tube replacement** | Atmosphere O₂ spike | Line stop; cool; tube cap-off (temporary) or replace; atmosphere purge; restart | 4–8 h per tube |
| **Zinc pot induction coil repair** | Coil current drop / T drop | Line stop; pot cool; coil replacement (complex, requires zinc temperature hold throughout); if pot cools below solidification: 48–72 h recovery | 8–24 h (minor); 48–72 h (solidification) |
| **Sink roll / pot roll change** | Dross accumulation, defect rate | Zinc pot drain (partial); roll pull + new installation; zinc top-up | 8–24 h |
| **Strip break thread-up** | Tension = 0 event | Manual thread through all furnace sections; zinc pot re-threading | 2–6 h |

---

## 8. COST / LOSS IMPACT

### 8.1 Reheating Furnace

| Event | Production impact | Cost estimate | Notes |
|-------|-----------------|--------------|-------|
| Burner degradation (undetected) | 15–25% excess fuel per tonne; temperature inconsistency → mill speed reduction or reject | GJ/tonne rise × production rate | [oxmaint] |
| Walking-beam drive emergency stop | 12–24 h HSM stoppage | 12–24 h × HSM production value; high-value coil product | Entire downstream campaign halts [oxmaint] |
| Skid pipe rupture + steam explosion | Immediate furnace shutdown; potential personnel injury | Multi-day furnace shutdown + equipment damage; major refractory damage | Safety-critical; uninsurable shortfall [ScienceDirect skid pipe] |
| Emergency refractory patch | 4–24 h | Moderate (patch material + labour) | vs 7–21 days if lining collapses |
| Major refractory relining | 7–21 days planned outage | Planned — refractory + labour; downtime cost amortised | Major overhaul every 3–5 years [oxmaint] |

### 8.2 Blast Furnace

| Event | Production impact | Cost estimate | Notes |
|-------|-----------------|--------------|-------|
| 6-hour unplanned tuyere emergency | BF slowdown/winddown | $800K–$1.2M lost production (5,000 t/day BF) | [oxmaint tuyere] |
| Undetected thermal drift → off-spec HM | Off-spec pig iron reprocessing | $2.3M reprocessing cost per documented case | [ifactoryapp] |
| Planned refractory repair vs emergency | Planned ~$50K vs Emergency ~$2M | Factor 40× cost differential | [ifactoryapp] |
| Unplanned BF blowdown | 1 day+ | $500K–$2M per day | [ifactoryapp] |
| Cooling stave water leak explosion | Potential catastrophic | Campaign loss + structural damage; human casualties | Explosive steam at 2,000°C iron [oxmaint cooling] |
| BF major reline (campaign end) | 90–180 day outage | Multi-hundred-million ₹ (reline + lost production) [unverified specific ₹ figure] | Campaign: 15–20 years target [ifactoryapp] |
| 62% tuyere replacements are unplanned | Opportunity cost vs planned 3–5 h | Emergency = 8–16 h each | [oxmaint tuyere] — strong case for PdM |

### 8.3 CAL / CGL Furnace

| Event | Production impact | Cost estimate | Notes |
|-------|-----------------|--------------|-------|
| Zinc pot solidification (full) | 48–72 h line stop + zinc recovery loss | 48–72 h × CGl line production rate (~100 kt/year line → ~15–22 t/hr → 720–1,600 t lost production) + zinc material cost | [unverified specific cost; industry-standard recovery time range] |
| Hearth roll pickup → strip defect | Quality downgrade or scrap of coils; line stop 4–12 h for roll change | Per-coil downgrade premium + line stop | Quality-critical; customer returns risk |
| Strip break | 2–6 h unplanned downtime | 2–6 h × line value | Frequent in CAL at high speed |
| Radiant tube replacement | 4–8 h planned; unplanned = line stop + atmosphere recovery | Tube cost ~₹50K–₹200K + downtime | [unverified ₹ range — tube cost varies by material] |

---

## 9. ADDITIONAL TECHNICAL NOTES

### 9.1 Tuyere Statistics (Global)

- 62% of tuyere replacements are unplanned emergency changes [oxmaint tuyere — cited from industry CMMS data]
- Service life: 3–12 months per unit; highly process-dependent
- Lead time for custom copper tuyeres: 8–12 weeks → keep 15–20% installed-count as spares [oxmaint tuyere]
- Tuyere failure root cause breakdown: melting loss 80–92%, abrasion 3–15%, rupture <5% [lmmgroupcn]

### 9.2 Cooling System Scale (Blast Furnace)

- Modern large BF runs 530+ electromagnetic flowmeters on cooling circuits alone
- Sensitivity: leak detection down to "drips per minute" with electromagnetic flow balance
- 85% of cooling circuit failures show detectable signals 30–60 days before failure [oxmaint BF cooling]
- Closed-loop cooling enables 15–20 year operation without major cooling-system overhaul [oxmaint BF cooling]

### 9.3 Hot Stove Constraint — Silica Brick

- Silica brick MUST stay above 600°C during operation; cooling through phase-transition causes permanent cracking
- This means stove partial repairs require very careful thermal management — cannot simply shut off and cool a stove quickly
- Design campaign life of hot stoves: 30+ years with systematic maintenance [oxmaint stove]

### 9.4 Hearth Roll Buildup — Material Science Note

Buildup deposits are primarily: Fe₂O₃ (iron oxide), MnO (manganese oxide), Al₂O₃ (alumina from Al-killed steels). Alumina buildup is the hardest and most damaging for high-strength steel grades. Modern rolls use Cr₂O₃ + Al₂O₃ thermal spray top-coat to resist adhesion [US Patent 8864869; US Patent 10337082].

### 9.5 PdM Opportunity Summary (for AI Challenge framing)

| Furnace system | Best PdM signal | Algorithm fit | Potential gain |
|---------------|---------------|--------------|---------------|
| Reheating furnace burners | GJ/tonne KPI + zone TC trend | Anomaly detection (LSTM / isolation forest) | 5–8% fuel savings [oxmaint] |
| Reheating furnace skid pipe | Cooling flow + outlet T per circuit | Threshold + multivariate regression | Steam explosion prevention (safety-critical) |
| BF tuyere | Per-tuyere outlet T trend (3–5 day rising) | Time-series trend + CUSUM | 62% planned vs unplanned flip; $800K–$1.2M per event |
| BF stave cooling | ΔT + ultrasonic thickness trend | Regression + erosion rate model | Campaign life extension; prevent water explosion |
| BF burden distribution | Top gas T asymmetry + chute encoder | Pattern recognition + Bayesian | 15–25% energy improvement potential [ifactoryapp] |
| CAL hearth roll | Drive motor current per roll | Anomaly detection (LSTM baseline) | Quality defect prevention; 4–12 h planned vs unplanned stop |
| CGL zinc pot | Bath TC + induction coil current | Threshold + rate-of-change alert | 48–72 h solidification recovery prevention |

---

## SOURCES

- [oxmaint — Reheating Furnace Maintenance: Walking Beam, Burners & Refractory](https://oxmaint.com/industries/steel-plant/reheating-furnace-maintenance-walking-beam-burners-refractory)
- [oxmaint — Reheat Furnace Maintenance: Burner, Refractory & Walking Beam System Guide](https://oxmaint.com/industries/steel-plant/reheat-furnace-maintenance-burner-refractory-walking-beam)
- [ifactoryapp — Reheating Furnace analytics: Walking Beam, Burner & Refractory](https://ifactoryapp.com/industries/steel-plant/reheating-furnace-analytics-walking-beam)
- [IspatGuru — Reheating Furnaces and their Types](https://www.ispatguru.com/reheating-furnaces-in-steel-plants/)
- [IspatGuru — Heating of Steel in Reheating Furnace](https://www.ispatguru.com/heating-of-steel-in-reheating-furnace/)
- [ScienceDirect — Characteristics of skid pipe failure in walking beam reheating furnace](https://www.sciencedirect.com/science/article/abs/pii/S1350630719308684)
- [ResearchGate — Failure Analysis of Skid Beam in Walking Beam Reheating Furnace](https://www.researchgate.net/publication/383672332_Failure_Analysis_of_Skid_Beam_in_Walking_Beam_Reheating_Furnace_of_Hot_Strip_Mill)
- [Griffin Open Systems — Temperature Setpoint Optimization in Steel Reheat Furnaces](https://www.griffinopensystems.com/wp-content/uploads/2020/11/GOS-Reheat-Furnaces-White-Paper-.pdf)
- [oxmaint — Blast Furnace Cooling System Monitoring: Real-Time Stave Protection](https://oxmaint.com/industries/steel-plant/blast-furnace-cooling-monitoring-real-time)
- [oxmaint — Blast Furnace Tuyere Maintenance: Inspection, Replacement & Failure Prevention](https://oxmaint.com/industries/steel-plant/blast-furnace-tuyere-maintenance-inspection-replacement)
- [oxmaint — Blast Furnace Maintenance Management: Maximize Campaign Life & Efficiency](https://oxmaint.com/industries/steel-plant/blast-furnace-maintenance-management-system)
- [oxmaint — Hot Blast Stove Maintenance: Refractory, Valve & Dome Inspection](https://oxmaint.com/industries/steel-plant/hot-blast-stove-maintenance-refractory-valve-inspection)
- [oxmaint — Blast Furnace Maintenance Management: Complete CMMS Guide](https://oxmaint.com/industries/steel-plant/blast-furnace-maintenance-management-cmms-guide)
- [ifactoryapp — Smart Blast Furnace Monitoring with AI and Advanced Sensors](https://ifactoryapp.com/industries/steel-plant/blast-furnace-ai-monitoring-sensors)
- [ifactoryapp — Blast Furnace Daily Monitoring Checklist](https://ifactoryapp.com/industries/steel-plant/blast-furnace-daily-monitoring-checklist)
- [lmmgroupcn — How to prevent the blast furnace tuyere burning through](https://www.lmmgroupcn.com/original-ariticles-how-to-prevent-the-blast-furnace-tuyere-burning-through/)
- [jucosrefractory — Forms and causes of blast furnace tuyere damage](https://www.jucosrefractory.com/info/forms-and-causes-of-blast-furnace-tuyere-damag-90640580.html)
- [manglamelectricals — Condition Based Monitoring of Tuyeres in Blast Furnace](https://www.manglamelectricals.com/condition-monitoring-of-tuyeres-using-thermal-imaging-cameras-to-prevent-gas-leakage)
- [IspatGuru — Hot Blast Stoves](https://www.ispatguru.com/hot-blast-stoves/)
- [aluminabricks — Quality Checker Bricks for Blast Furnace](https://www.aluminabricks.com/blog/maximizing-blast-furnace-performance-with-quality-checker-bricks/)
- [US Patent 8864869 — Hearth roll in continuous annealing furnace](https://patents.google.com/patent/US8864869B2/en)
- [US Patent 4470802 — Buildup-resistant hearth roll for continuous annealing furnace](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/4470802)
- [US Patent 10337082 — Hearth roll and continuous annealing facility](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/10337082)
- [GalvInfo Note 2.4.1 — Zinc Bath Management on Continuous Hot-Dip Galvanizing](https://www.galvinfo.com/wp-content/uploads/sites/8/2017/05/GalvInfoNote_2_4_1.pdf)
- [Academia.edu — Heat Balance Analysis of Annealing Furnaces and Zinc Pot in CGL](https://www.academia.edu/16895799/Heat_Balance_Analysis_of_Annealing_Furnaces_and_Zinc_Pot_in_Continuous_Hot_Dip_Galvanizing_Lines)
- [SMM — Application of Induction Heating Technology in Galvanizing](https://news.metal.com/newscontent/101292949/application-of-induction-heating-technology-in-batch-galvanizing)
- [Envistaforensics — Steam Explosions in Molten Material Environments](https://www.envistaforensics.com/knowledge-center/insights/articles/preventing-catastrophe-understanding-steam-explosions-in-molten-material-environments/)

*[unverified] tags used where specific numbers (recovery times, ₹ costs) are industry-standard practice but no public primary source citation was located in this research session.*
