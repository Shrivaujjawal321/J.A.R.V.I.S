# 11 — Cranes & Lifting Equipment (Integrated Steel Plant — Tata Steel Scale)
> Deep PdM Reference | Compiled 2026-06-08 | Sources cited throughout

---

## 1. TYPES OF CRANES — What They Are and Where They Operate

### 1.1 Ladle / Hot-Metal Cranes (highest safety criticality)
- **Location:** BOF/EAF melt shop, continuous caster bay, secondary metallurgy (LF/VD)
- **Capacity:** 300–500 t main hoist; 80–105 t auxiliary hoist [Tata Steel-JASO contract, 2019 & 2025]
- **Configuration:** Four-girder box-beam design, open-winch hoisting mechanism, two motors feeding a central planetary gearbox; twin hooks (main + auxiliary)
- **Duty class:** ISO M8 / FEM 4m (extra-heavy, continuous)
- **Special feature:** Anti-sway PLC to prevent molten metal turbulence; regenerative VFDs; redundant dual/triple braking; CCTV + WiFi telemetry (EWon)
- **Tata Steel specific (Port Talbot, 2025):** 500 t ladle cranes ordered from JASO for new EAF-based green steelmaking line [Business Standard, 2025-05-27]

### 1.2 Charging Cranes (EAF/BOF)
- **Location:** EAF/BOF bay, above converter/furnace vessel
- **Capacity:** Typically 100–200 t
- **Role:** Charge scrap baskets into EAF; charge hot metal ladles into BOF converter
- **Hazard:** Open furnace vessel below; electromagnetic interference from EAF accelerates electrical degradation
- **Consequence of failure:** Furnace idles at ~$15,000/hr in wasted energy [Mazzella/oxmaint]

### 1.3 Torpedo-Car / Hot-Metal Transfer Cranes
- **Location:** Hot metal transfer station (blast furnace → BOF)
- **Load temperature:** 1,400–1,500°C
- **Capacity:** Varies; typically 250–350 t

### 1.4 Caster Ladle Cranes (Tundish + Ladle Turret Service)
- **Location:** Continuous casting bay
- **Role:** Lower ladle onto turret, handle tundish
- **Failure consequence:** Breakout/explosion if ladle drops; steel skull loss

### 1.5 Scrap-Handling Magnet Cranes
- **Location:** Scrap yard, EAF bay
- **Capacity:** 40–80 t; lifting magnets up to 5 t lift per magnet
- **Hazard:** Magnet de-energise = uncontrolled drop of scrap; crushing risk
- **Monitoring priority:** Magnet power supply continuity, cable wear

### 1.6 Slab / Bloom Handling Cranes (Tong Cranes)
- **Location:** Rolling mill bay, slab yard
- **Capacity:** 50–200 t; C-hooks or tong grabs
- **Duty class:** A6–A7

### 1.7 Maintenance EOT Cranes (Workshop)
- **Location:** Machine shop, maintenance bay
- **Capacity:** 5–50 t
- **Duty class:** A3–A5; standard design; lower monitoring priority

### 1.8 Gantry Cranes (Rail-Mounted Outdoor)
- **Location:** Raw material yards, ore stockpiles, coal handling
- **Capacity:** 10–100 t
- **Failure modes:** Rail settlement (outdoor), wind loading, long-travel wheel wear

---

## 2. PARTS BREAKDOWN

### 2.1 Wire Ropes
- **Material:** High-strength steel; multi-strand construction (6×36 IWRC typical for hoists)
- **Ladle crane special requirement:** Extra-high fatigue-class ropes (ISO 2408 / EN 12385-4); heat-resistant coatings; shorter replacement intervals than standard
- **Reeving:** Multiple-part reeving (4–8 falls) to distribute load; bottom block + hook assembly

### 2.2 Hooks
- **Type:** Forged alloy steel, Clevis or shank mount; Grade 80/100
- **Design factor:** 5:1 (breaking load to WLL) minimum; ladle cranes often 6:1
- **Features:** Safety latch; swivel capability (controlled); trunnion-style saddle hooks for ladle lugs

### 2.3 Drums
- **Type:** Flanged drum; grooved for rope guidance in multi-layer spooling
- **Material:** Cast or fabricated steel
- **Wear point:** Grooves flatten or deform → rope cross-overs → accelerated rope wear

### 2.4 Sheaves (Pulleys)
- **Material:** Cast steel or ductile iron; nylon/polymer-lined for wire rope protection
- **Groove diameter:** Must match rope diameter per ISO 4308; groove too small → rope deformation
- **Bearing type:** Self-aligning roller; lubrication-critical

### 2.5 Hoist Gearbox
- **Type:** Planetary (central stage) + helical/bevel input stages typical for large ladle cranes
- **Oil volume:** 50–200 L depending on size; viscosity ISO VG 220/320
- **Bearing arrangement:** Tapered roller bearings on output shaft; deep-groove ball on high-speed stages
- **Thermal environment:** Ladle crane gearboxes see ambient 60–80°C + radiant spikes >200°C; requires oil cooling or synthetic lubricants

### 2.6 Hoist Motors
- **Type:** AC slip-ring induction (legacy) or AC squirrel-cage + VFD (modern)
- **Insulation class:** F or H; tropical/heavy-duty rating
- **Rating:** Duty cycle S3/S4 (intermittent), crane duty
- **Encoder:** Absolute encoder on motor shaft for position/speed feedback

### 2.7 Brakes
- **Type:** Electro-hydraulic disc brake (EHDB) or electromagnetic disc brake; spring-apply, power-release ("fail-safe")
- **Number:** Dual or triple independent brakes on hoist — each must independently hold 150% rated load (FEM/ASME requirement for ladle cranes)
- **Lining material:** Sintered metal or organic compound; ladle cranes use higher-temperature grades
- **Torque rating:** Typically 150–200% of motor rated torque

### 2.8 Bridge Girders (Structural)
- **Type:** Box-girder (double or four-girder); span 15–35 m for melt-shop bays
- **Material:** S355/S460 structural steel; critical welds post-weld heat treated
- **Camber:** Pre-built upward camber (L/1000 typical) to compensate dead load deflection

### 2.9 Bridge & Trolley Wheels
- **Material:** Forged alloy steel; hardened tread + flange
- **Diameter:** 400–800 mm on large ladle cranes
- **Tread profile:** Tapered or cylindrical; matched to rail profile
- **Replacement criterion:** Flange thickness reduced to 50% of new value [crane industry standard]

### 2.10 Runway Rails
- **Profile:** Square head (KP) or flanged (crane rail section A45–A120); hardened alloy steel
- **Fastening:** Rail clips + baseplates; expansion joints at intervals
- **Wear mode:** Head wear (vertical), gauge variation, rail end gap

### 2.11 Long-Travel Drive (Bridge Drive)
- **Type:** AC motor + gearbox on each end truck; shaft encoder for synchronisation
- **Skew control:** Differential encoder feedback; PLC corrects independently per side
- **Buffer stops:** End-of-travel hydraulic buffers

### 2.12 Power Supply
- **Festoon system (light cranes):** Festoon cable + trolley on catenary
- **Conductor bars (large cranes):** Four-wire or six-wire copper/aluminum conductor rail; copper-carbon collector shoes
- **EMC concern:** EAF bay → high electromagnetic noise; shielded cabling + ferrite filters mandatory

---

## 3. SENSORS — Most Common in PdM Programs

| # | Sensor | Location | Signal Type | Monitoring Target |
|---|--------|----------|-------------|-------------------|
| 1 | Load cells / strain gauges | Drum bearing seats; end trucks | Analog 4–20 mA / digital | Load weight, overload event, asymmetric lift |
| 2 | Magnetic rope testing (MRT) head | Fixed on rope at fleet angle point | Electromagnetic flux | LMA (loss of metallic area), broken internal wires |
| 3 | Brake wear / air-gap sensor | Each brake caliper | Inductive proximity / LVDT | Lining thickness, air gap, response time |
| 4 | Triaxial vibration accelerometer | Gearbox housing; motor NDE + DE bearings | IEPE 100 mV/g, 10 Hz–10 kHz | Gear tooth defect, bearing spalling, imbalance |
| 5 | Oil particle counter (in-line) | Gearbox lube circuit | ISO 4406 class output | Metallic wear debris → early gear/bearing failure |
| 6 | Motor current (MCSA) | VFD / MCC panel | CT 0–5 A | Slip-ring condition, winding fault, load spikes |
| 7 | Absolute rotary encoder | Motor shaft; drum shaft | SSI / EnDat digital | Rope position, hook height, speed, deceleration profile |
| 8 | Thermocouple / PT100 | Gearbox oil sump; motor windings; heat shields | 4–20 mA / Pt100 bridge | Thermal overload, cooling failure |
| 9 | Acoustic emission (AE) sensors | Girder welds; hook shank | Piezoelectric, 100–300 kHz | Crack initiation, propagation in structural welds |
| 10 | Laser / ultrasonic distance sensor | Bridge ends (skew detection) | 4–20 mA / digital | Bridge crabbing, rail alignment deviation |
| 11 | Overspeed switch | Motor/drum shaft | NC contact | Runaway hoist detection, emergency brake trigger |
| 12 | Limit switches (rotary / weight-hammer) | Drum; travel end | NC/NO contact | Upper/lower hook limit, bridge/trolley travel limits |
| 13 | Thermal imager (IR camera) | Conductor bars; VFD panels (periodic) | Thermal image | Hot-spots, collector bar arcing, electrical faults |
| 14 | Structural strain gauge (FBG or foil) | Girder web; end-plate welds | Wheatstone bridge / optical | Fatigue cycle counting, peak stress monitoring |

---

## 4. NORMAL READINGS PER SENSOR

| Sensor | Normal Range | Notes |
|--------|-------------|-------|
| Load cell (% WLL) | 20–95% WLL during lift; 0% when parked | >100% = overload alarm; ladle cranes alarm at 95%, cut power at 110% |
| Brake opening current (% baseline) | 85–100% of commissioning baseline | <50% = warn; <5% = brake will not release → critical fault [Konecranes TRUCONNECT] |
| Brake response time | ≤200 ms engage; ≤500 ms release | >200 ms engage extension → Severity 1 |
| Vibration (gearbox, velocity RMS) | ≤4.5 mm/s RMS (ISO 10816 Zone A/B for Class I machinery) | Gearbox thresholds elevated; "satisfactory" limit cited as ~10 mm/s RMS [cbmconnect] |
| Vibration (bearing envelope, g RMS) | Baseline ± 20%; BPFO/BPFI absent | Fault frequencies: FTF ~0.5 Hz, BSF ~4–5 Hz, BPFO ~12 Hz, BPFI ~16 Hz (application-specific) [prosig] |
| Oil particle count (gearbox) | ISO 4406 ≤ 17/15/12 (new oil) | >20/18/15 = advisory; rising trend = imminent failure |
| Gearbox oil temp | 50–75°C (mineral oil); ≤85°C synthetic | >90°C = alarm; >100°C = shutdown |
| Motor winding temp (Class F) | ≤115°C rise above 40°C ambient = 155°C | >155°C = alarm; sustained >165°C = imminent insulation failure |
| Motor current (% FLA) | 70–100% FLA during rated lift | Sudden spike >120% FLA = overload/jam; gradual rise = winding/bearing degradation |
| Rope LMA (MRT) | 0–5% LMA = new/good | >10% LMA = advisory; >15–20% LMA = discard territory per ISO 4309 |
| Hook throat opening | Manufacturer nominal ± 0% | >15% throat opening increase = immediate removal (ASME B30.10) |
| Hook twist | <5° from vertical | >10° twist = immediate removal |
| Rail gauge deviation | ±2 mm of design gauge | >5 mm = corrective action; causes wheel flange binding and structural skew loads |
| Bridge skew (laser differential) | <2 mm end-to-end | >5 mm = slow to crawl; >15 mm = stop |

---

## 5. DEFECT READINGS — Value Changes and Thresholds by Failure Mode

### 5.1 Wire Rope Wear / Broken Strands
| Indicator | Normal | Warning | Discard |
|-----------|--------|---------|---------|
| Visible broken wires (per ISO 4309) | 0 | ≥6 random in 1 lay length | ≥12 random / ≥4 in one strand / any complete strand break |
| Diameter reduction | 0% | >3% | >7% (or per manufacturer) |
| MRT — LMA | 0–5% | 8–12% | >15–20% |
| MRT — Localised flaw index | 0 | Signal spike >2× baseline | Any single break cluster at cross-over zones |
| Rope temperature discolouration | Silver/grey | Straw/blue tint (>200°C exposure) | Dark blue/black = heat treatment limit exceeded; discard immediately |
- Heat-exposed (ladle crane) ropes require 30–50% shorter replacement intervals than ISO 4309 standard calculation due to thermal embrittlement [unverified — industry practice]

### 5.2 Brake Failure
| Indicator | Normal | Warning | Critical |
|-----------|--------|---------|----------|
| Opening current (% baseline) | 90–100% | 50–85% | <5% (brake will not open) |
| Brake engage response | ≤200 ms | 200–500 ms | >500 ms (brake slippage risk) |
| Lining thickness | 100% new | 40–60% remaining | ≤30% → schedule replacement |
| Drift under load test | 0 mm | 1–3 mm/min | >3 mm/min = hoist brake drift = Severity 1 deficiency [oxmaint] |
- Thermal fade from radiant heat (ladle cranes): brake torque can drop 20–40% near furnace tap [unverified — based on friction material thermal curves]

### 5.3 Gearbox / Bearing Failure
| Indicator | Normal | Warning | Critical |
|-----------|--------|---------|----------|
| Vibration RMS (gearbox housing) | Baseline ± 10% | Baseline +50% | Baseline +200% or absolute >18–25 mm/s RMS |
| Gear mesh frequency harmonics | 1× GMF only | 2–3× GMF sidebands appearing | High-order GMF sidebands + noise floor rise = spalling |
| Oil particle count ISO class | ≤17/15/12 | 19/17/14 | ≥21/19/16 or step-change in 1 week |
| Chip detector magnet | Clean | Light fuzz | Metallic fragments >2 mm → stop and inspect |
| Oil sump temperature | 60–75°C | 80–90°C | >100°C |
- Prediction window with MFD + oil analysis: 3–8 weeks advance notice [oxmaint IoT guide]
- Emergency gearbox replacement: 72–120 hours downtime [$80K–$200K + production loss] [oxmaint]

### 5.4 Hook Fatigue / Overload
| Indicator | Normal | Warning | Critical |
|-----------|--------|---------|----------|
| Throat opening | Design nominal | +5–10% | >+15% = discard immediately (ASME B30.10) |
| Twist | <5° | 5–10° | >10° = discard |
| MPI / UT (periodic NDT) | No indications | Linear indication <3 mm | Any through-crack indication = remove from service |
| Overload event log (load cell) | 0 × >100% WLL | 1–2 events/year | >5 events or any single event >125% WLL = hook NDT required |

### 5.5 Bridge / Trolley Wheel and Rail Wear
| Indicator | Normal | Warning | Critical |
|-----------|--------|---------|----------|
| Wheel flange thickness | 100% new | 60–70% | <50% = replace [crane industry standard] |
| Rail head wear (vertical) | 0% | 10–15% | >20% or cracking visible |
| Rail gauge | Design ± 1 mm | ±3–5 mm | >±5 mm → abnormal wheel loads |
| Vibration at travel speed (bridge drive) | Smooth baseline | Rhythmic impulse at wheel circumference | High-amplitude impulse = flat spot → immediate wheel inspection |
| Skew sensor differential | <2 mm | 2–10 mm | >15 mm → structural overload risk |

### 5.6 Structural Girder Fatigue Cracking
| Indicator | Normal | Warning | Critical |
|-----------|--------|---------|----------|
| Strain gauge peak (% design stress) | 60–80% of design | 90–100% | >100% or sudden step change = crack propagation |
| AE event rate (weld zone) | <2 events/hr | 2–10 events/hr | >20 events/hr sustained = crack growth active |
| Visual / PT / UT at welds | No indications | Surface irregularity | Any confirmed crack → engineering hold, NDE full scan |
| Girder deflection (mid-span, % span) | L/1000 | L/800 | L/700 = excessive; indicates permanent deformation or crack |
- Fatigue cracking at welded connections is the #1 structural failure mode in crane girders [oxmaint maintenance guide]

---

## 6. FAILURE MODES — Detail and Earliest Signs

### FM-01: Wire Rope Wear and Broken Strands
- **Root cause:** Cyclic bending fatigue at sheaves and drum; corrosion from steam/humidity; thermal embrittlement (ladle cranes)
- **Earliest signs (hours to weeks before failure):**
  - MRT LMA reading creeping from 5% → 8%
  - First external broken wires visible at sheave-contact points
  - Rope diameter reduction begins (measure monthly)
  - Rope stiffness change detected via encoder deceleration curve drift
- **Critical escalation:** Internal strand breaks (invisible to visual) detected only by MRT — can lead to sudden catastrophic failure without warning if MRT not deployed

### FM-02: Brake Failure (Most Critical Single-Point Failure)
- **Root cause:** Lining wear, spring fatigue, solenoid/hydraulic actuator failure, thermal fade
- **Earliest signs:**
  - Opening current drops below 85% of baseline
  - Brake engagement time extends beyond 200 ms
  - Drift test shows 1–2 mm/min drift under load
  - Audible squeal during engagement (uneven contact)
- **Catastrophic path:** Brake failure under loaded ladle = uncontrolled descent of 300–500 t of liquid steel at 1,600°C

### FM-03: Hook Fatigue and Deformation
- **Root cause:** Cumulative fatigue from near-capacity lifts; dynamic shock loads; accidental overloads
- **Earliest signs:**
  - Load cell log reveals repeated events >90% WLL
  - Hook shank PT/MPI reveals linear surface indication (fatigue initiation)
  - Throat opening measurement creeps beyond +5%
- **Detection interval:** ASME B30.10 — monthly visual for Class A cranes; MPI at least annually or after any overload event

### FM-04: Gearbox Bearing Failure
- **Root cause:** Lubrication breakdown (high-temp oil degradation), contamination, fatigue spalling, misalignment
- **Earliest signs (3–8 weeks before failure):**
  - BPFO/BPFI harmonic family emerging in FFT spectrum
  - Oil particle count ISO class stepping up by 2–3 classes
  - Sump temp rising 5–10°C above seasonal baseline
  - Acoustic emission from bearing zone during coast-down
- **Consequence:** Full seizure = 72–120 hour repair; $80K–$200K parts + production loss [oxmaint]

### FM-05: Wheel Flat Spot / Rail Damage
- **Root cause:** Emergency braking during travel → wheel slide; rail misalignment → repeated impact; thermal distortion of runway beams
- **Earliest signs:**
  - Rhythmic shock impulse in bridge-drive vibration signal (frequency = travel speed / wheel circumference)
  - Increased motor current during travel on affected section
  - Visual flat spot or spalling on wheel tread
- **Cascade risk:** Flat spot → rail head indentation → rail cracking → structural load concentration

### FM-06: Structural Girder Fatigue Cracking
- **Root cause:** High-cycle fatigue at welded connections (web-to-flange, end-plate, rail-mount pad); cumulative overload
- **Earliest signs:**
  - Strain gauge reading peak stress >90% design
  - AE sensor detects micro-cracking events at weld toes
  - Visual: rust staining, paint cracking at weld zones
  - Mid-span deflection increasing beyond L/800
- **Standard:** EN 13001-3-1 for fatigue life; FEM/ANSYS simulation for crack propagation assessment

### FM-07: Electrical / Collector Bar Failure
- **Root cause:** Arcing, overheating, EAF electromagnetic interference
- **Earliest signs:**
  - IR camera hot-spot on collector shoe/bar >50°C above ambient
  - Increased motor current noise/spikes (MCSA)
  - Insulation resistance trending downward on motor winding (Megger test)

---

## 7. REPAIR AND RESOLUTION

### 7.1 Wire Rope Replacement
- **Decision criteria:** ISO 4309:2017 + heat-exposure accelerated criteria for ladle cranes
- **Process:**
  1. Park crane in maintenance bay; lock out / tag out (LOTO)
  2. Unreeve old rope; measure drum groove wear
  3. Pre-stretch new rope before installation
  4. Reeve new rope; set end anchor; proof-load to 100% WLL
  5. Inspect sheave grooves and lubrication
- **Time-to-repair:** 4–12 hours depending on crane size and number of rope falls [crane industry data]
- **Planned vs unplanned:** Planned rope change (MRT-triggered) = 4 hr window; Emergency field break = 24–48 hr + rope procurement lead time

### 7.2 Brake Service
- **Lining replacement:** Drain hydraulic circuit → remove caliper → swap lining pads → bleed + reset air gap → calibration test under load
- **Spring check:** Replace spring pack if set-length shortened >5% (spring fatigue)
- **Time:** 2–4 hours per brake assembly; ladle crane has 2–3 brakes per hoist
- **Post-repair mandatory:** Dynamic brake test (drift test under 100% load)

### 7.3 Hook Inspection and NDT (ASME B30.10 / EN 13001)
- **Schedule:** Monthly visual; annual MPI/UT for Class A cranes; after every overload event
- **Process:**
  1. Degrease hook
  2. Magnetic particle inspection (MPI per EN 10228-1 or ASTM E709) on shank, neck, bowl
  3. Dimensional check: throat opening, twist, diameter at throat
  4. Load test after reinstallation
- **Discard triggers:** Throat opening >15%; twist >10°; any confirmed crack indication
- **Time:** 2–4 hours per hook including reinstallation

### 7.4 Gearbox Overhaul
- **Trigger:** Oil analysis + vibration trending; do not wait for noise/heat stage
- **Planned replacement (bearing swap):** 8–16 hours; bearing units ~30 kg each [ifactoryapp]
- **Full gearbox R&R:** 72–120 hours; requires pre-positioned spare gearbox or remanufactured unit
- **Recommended strategy:** Keep one spare gearbox assembly per crane class at site

### 7.5 Structural Crack Repair
- **NDT-confirmed crack:** Engineering hold imposed immediately; no loads permitted
- **Repair:** Weld repair per qualified welding procedure (WPS); PWHT if required by standard; UT/MPI post-weld
- **Return to service:** Load test at 100% WLL; AE monitoring for 2 weeks post-repair
- **Time:** 24–120 hours depending on crack size and access

### 7.6 Wheel and Rail Maintenance
- **Wheel replacement:** Flange at <50% original → in-situ turning if possible; otherwise end-truck change-out
- **Rail realignment:** Survey with laser alignment tool; re-torque clips; weld repair rail head spalls
- **Quarterly survey:** Gauge, level, rail wear measurement for Class A cranes [oxmaint / OSHA]

---

## 8. COST AND LOSS IMPACT

### 8.1 Production Downtime
| Failure Scenario | Cost / Hour (USD) | Cost / Hour (INR approx.) | Notes |
|------------------|--------------------|---------------------------|-------|
| Ladle crane stops → melt shop stops | $50K–$200K | ₹40–170 lakh | Tata-scale integrated plant; rolling mill + caster downstream idle |
| Charging crane fails → furnace idles | $15,000 | ₹1.25 crore | Furnace energy waste alone [oxmaint / Mazzella] |
| Steel mill rolling mill stoppage (India) | — | ₹21 lakh/hr | Case study cited [arXiv 2510.26684] |
| Wire rope emergency replacement | $22K–$55K per event | ₹18–46 lakh | Includes downtime + procurement [oxmaint IoT guide] |
| Gearbox failure + repair | $80K–$200K + production loss | ₹67–170 lakh + production | 72–120 hr downtime [oxmaint] |

### 8.2 Safety Catastrophe
- A ladle drop releasing 300–500 t of steel at 1,600°C is a **multi-fatality, plant-destruction event**
- Can penetrate concrete flooring, breach adjacent bays, damage continuous casters (months to rebuild)
- Insurance: Such events trigger forensic investigations, regulatory shutdown of entire melt shop
- Historical analogies: Ladle crane failures rank among the most lethal industrial accidents globally

### 8.3 Maintenance Cost Reduction (IoT PdM ROI)
- Fleet-level: Unplanned crane stoppages dropped **58%** post-IoT deployment [oxmaint IoT guide]
- Annual savings: **$420K** per fleet in one documented case [oxmaint]
- Cost per heat: $2,800 → $1,200 per heat (−57%) within 11 months [oxmaint]
- Emergency vs. planned repair cost ratio: **3–5×** more expensive reactive vs. structured maintenance [oxmaint]
- Wire rope lifespan extended **+30%** with MRT-guided replacement [ifactoryapp]

---

## 9. ADDITIONAL TECHNICAL DETAILS

### 9.1 Anti-Sway Systems
- Ladle cranes use model-based or input-shaping anti-sway PLC algorithms
- Purpose: Prevent oscillation of liquid metal → turbulence → slag inclusion + temperature loss
- Sensor input: Hook rope angle (pendulum encoder or camera-based tracking); trolley acceleration

### 9.2 Load-Cycle Counting (Fatigue Life Management)
- Every crane has a designed number of load cycles (C-class per FEM/ISO 4301)
- Class A cranes log every lift via load cell + encoder
- When cumulative cycle count approaches design life (e.g., 1.6×10⁶ cycles for M8 class), engineering assessment of residual life required per EN 13001-3-1
- Consequence of ignoring: Brittle fracture of girder at weld toe without visible warning

### 9.3 Konecranes TRUCONNECT (Industry Reference)
- Commercial PdM platform widely used in steel mills
- Collects: Brake opening current, motor hours, lift cycle count, drive fault codes
- Brake opening current <5% → "very probable risk that the brake will not open" [Konecranes TRUCONNECT documentation]

### 9.4 JASO 500 t Crane for Tata Steel
- Open-winch hoisting, two motors + central planetary gearbox
- Auxiliary: 105 t
- Features: CCTV, EWon WiFi, vibration gauge, dual A/C systems, regenerative VFDs, anti-collision system [Business Standard / KHL Group, 2025]

### 9.5 Heat Shields
- Ladle/EAF cranes: Steel + ceramic-fibre insulated shields over trolley, hoist motors, electrical boxes
- Inspection: Replace if >30% deformed or if thermocouple shows >200°C behind shield [oxmaint]

---

## 10. RELEVANT SAFETY STANDARDS

| Standard | Scope |
|----------|-------|
| **ISO 4309:2017** | Wire rope care, inspection, discard criteria for cranes |
| **ISO 4308** | Sheave and drum diameter ratios |
| **ISO 4301 / FEM 1.001** | Crane classification (duty class M1–M8) |
| **EN 13001-3-1** | Structural fatigue design and assessment |
| **ASME B30.2** | Overhead and gantry cranes; load test 125% annually |
| **ASME B30.10** | Hooks; NDT requirements; discard criteria |
| **OSHA 1910.179** | US standard; frequent (daily–monthly) + periodic inspection mandates |
| **EN 10228-1 / ASTM E709** | MPI procedure for ferromagnetic crane components |
| **IS 3177:1999** | Indian Standard — EOT cranes; relevant for Tata Steel India plants |
| **IS 15560:2005** | Indian Standard — Safety requirements for cranes |

---

## Sources

- [Steel Plant Crane Analytics: EOT, Ladle & Charging Cranes — ifactoryapp](https://ifactoryapp.com/industries/steel-plant/steel-plant-crane-analytics-eot-ladle)
- [Crane & Material Handling Maintenance in Steel Plants IoT Guide — oxmaint](https://oxmaint.com/blog/post/crane-material-handling-maintenance-steel-plants-iot)
- [Overhead Crane Maintenance in Steel Plants: EOT, Ladle & Special Purpose Cranes — oxmaint](https://oxmaint.com/industries/steel-plant/overhead-crane-maintenance-steel-plants-eot-ladle)
- [Steel Plant Crane Maintenance & Safety CMMS — oxmaint](https://oxmaint.com/industries/steel-plant/steel-plant-crane-maintenance-overhead-crane-safety)
- [What Makes a Ladle Crane Different — bettercrane.com](https://www.bettercrane.com/resouces/news/ladle-crane-vs-general-use-overhead-crane.html)
- [Zero-Failure Ladle Cranes for High-Temperature Melt-Shops — bettercrane.com](https://www.bettercrane.com/resouces/news/melt-shops-ladle-cranes.html)
- [Safety Devices of Ladle Overhead Cranes — bettercrane.com](https://www.bettercrane.com/resouces/news/safety-devices-of-ladle-overhead-crane.html)
- [TRUCONNECT Remote Monitoring Service — Konecranes](https://www.konecranes.com/en-us/service/predictive-maintenance-and-remote-monitoring/truconnect-remote-service-for-overhead-cranes)
- [Tata Steel Advances Low CO2 Plans Through Major Crane Project — Business Standard, 2025-05-27](https://www.business-standard.com/companies/news/tata-steel-advances-green-steelmaking-plans-through-major-crane-project-125052701183_1.html)
- [Tata Steel JASO Crane Contract — KHL Group](https://www.khl.com/news/jaso-to-build-its-biggest-industrial-crane/1140432.article)
- [ISO 4309:2017 — ISO.org](https://www.iso.org/standard/66759.html)
- [Overhead Crane Wire Rope Inspection Guide 2026 — HOJ Innovations](https://hoj.net/blogs/resources/overhead-crane-wire-rope-inspection-replacement-criteria-broken-wire-limits-and-compliance-requirements)
- [Condition Monitoring Technologies for Steel Wire Ropes — IJPHM / PHM Society](https://papers.phmsociety.org/index.php/ijphm/article/download/2527/1487)
- [Non-Destructive Testing for Crane Components — HNL Cranes](https://www.hnhlcranes.com/understanding-ndt-crane-components-safety-testing/)
- [Crane Hook NDT — ASME B30.10 Requirements](https://qualifiedcranetraining.com/non-destructive-testing-requirements-for-crane-hooks-under-asme-b30-10/)
- [Gearbox Vibration Analysis — CBM CONNECT](https://www.cbmconnect.com/technology-based-crane-monitoring-and-diagnostics/)
- [Gearbox Vibration Demodulation Analysis — ProSig](https://blog.prosig.com/2024/02/23/bearings-gearbox-analysis-using-demodulation-techniques/)
- [The True Cost of Overhead Crane Breakdowns — Mazzella](https://www.mazzellacompanies.com/learning-center/the-true-cost-of-overhead-crane-breakdowns/)
- [Crane Rail Misalignment, Wheel Wear & Fixes — BW Crane](https://jsbwcrane.com/rail-systems-for-overhead-and-gantty-cranes-misalignment-issues-and-fixes/)
- [Residual Life of Steel Structures — Mechanics & Industry Journal, 2019](https://www.mechanics-industry.org/articles/meca/full_html/2019/08/mi190171/mi190171.html)
