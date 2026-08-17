# Steel Plant Equipment: Parts-Level Failure Catalog
# For: Tata Steel R2 — Data-Quality Platform + Synthetic Dataset Generation
# Author: tata-steel-predictive-maintenance subagent
# Date: 2026-06-08

---

## Purpose

This document enumerates every rotating and static equipment class present in an integrated steel plant down to the **part level**, specifying the dominant failure modes per part, degradation behaviour (sudden vs. gradual), and criticality ranking. It is the primary domain-knowledge grounding document for:

1. Synthetic sensor trace generation (which signal, which spectral signature, which RUL curve)
2. Data-quality labelling schema (what anomaly type maps to what equipment state)
3. Agent knowledge-base content (RCA chains, sensor-to-failure mappings)

All claims are cited or tagged `[unverified]` if drawn from general engineering literature without a specific steel-plant study.

---

## 1. Rolling-Element Bearings (anti-friction bearings)

### Scope
Universal across all rotating equipment. Specifically: rolling mill chock bearings (four-row tapered roller), conveyor idler bearings, motor bearings (deep groove ball), pump bearings, gearbox bearings, fan bearings.

### Parts and Failure Modes

| Part | Failure Mode | Mechanism | Degradation Pattern |
|------|-------------|-----------|-------------------|
| Inner race | Spalling / subsurface fatigue | Hertzian contact cycles exceed material endurance; defect grows from subsurface inclusion | Gradual: fault frequency appears in vibration spectrum (BPFI = Ball Pass Freq Inner); AE spikes begin ~15–30% of life remaining |
| Inner race | Fretting corrosion | Micro-slip between race and shaft under press-fit looseness + vibration | Gradual over months |
| Outer race | Spalling / pitting | Same Hertzian mechanism; load zone fixed → outer race more exposed in vertical loads | Gradual: BPFO detectable; characteristic spectral sidebands appear |
| Outer race | Electrical erosion (EDM pitting) | VFD-induced shaft currents arc through rolling contact | Sudden onset once film breaks; crater pitting causes rapid deterioration |
| Rolling elements (balls / tapered rollers / cylindrical rollers) | Spalling, flaking | Fatigue cracking from surface stress concentrations (dents, inclusions) | Gradual; BSF (ball spin frequency) visible in envelope spectrum |
| Rolling elements | Indentation / brinelling | Overload or shock load at standstill or during installation | True brinelling = sudden; false brinelling (fretting at standstill) = gradual |
| Cage | Fracture / wear | Overloading, lubricant starvation, incompatible lubricant causing cage-roller binding | Sudden (catastrophic cage collapse = machine trip within seconds) |
| Cage | Cage pocket wear | Continuous sliding under speed changes | Gradual; cage frequency harmonics rise |
| Lubricant film | Starvation, degradation (oxidation, water ingress, particle contamination) | Film breakdown → metal-metal contact → accelerated wear across all surfaces | Gradual until threshold; then accelerating |

### Sensor Signatures
- Vibration: envelope spectrum at BPFI/BPFO/BSF/FTF; overall RMS trends upward
- Temperature: bearing housing temperature rises 10–20°C above baseline in advanced stage
- Acoustic emission: stress wave bursts at 100–500 kHz; precede vibration changes by weeks [IMS Bearing Dataset confirms AE lead — cite: Lee et al., 2007, "IMS Bearing Data Set," NASA CARS Lab]
- Oil debris (MDM / magnetic plug): ferrous particle count increases proportionally to spall area

### Typical Time to Failure (TTF)
- Stage 1 (AE detectable): weeks to months before failure
- Stage 2 (vibration detectable): days to weeks
- Stage 3 (audible noise / temperature rise): hours to days
- Stage 4 (catastrophic): minutes to hours

### Criticality in Steel Plants
**HIGHEST.** Rolling mill chock bearing failure = unplanned rolling stand outage = $10,000–$50,000/hour production loss [unverified exact figure; Tata Steel 15% unplanned downtime reduction cited in company reports]. Motor bearing failure on critical drives (blast furnace blower, caster withdrawal) = safety/environmental risk.

---

## 2. Gearboxes

### Scope
Rolling mill main gearboxes (pinion stands), crane hoisting gearboxes, conveyor drive gearboxes, cooling tower gearboxes (right-angle bevel), pump/fan drive gearboxes.

### Parts and Failure Modes

| Part | Failure Mode | Mechanism | Degradation Pattern |
|------|-------------|-----------|-------------------|
| Gear teeth — contact surface | Pitting (micropitting / macropitting) | Hertzian contact fatigue; surface-initiated fatigue cracks | Gradual; GMF (gear mesh frequency) sidebands in vibration; oil debris particle count rises |
| Gear teeth — contact surface | Spalling | Advanced pitting; large flakes break from tooth face | Rapid progression once initiated; GMF amplitudes jump |
| Gear teeth — root | Bending fatigue cracking | Cyclic tensile stress at dedendum fillet; stress concentration at root | Gradual crack propagation; detectable via time-synchronous averaging (TSA) residual signal |
| Gear teeth | Scuffing / scoring | Lubricant film breakdown under high loads → adhesive wear | Sudden under overload/oil starvation; leaves scratched grooves |
| Gear teeth | Abrasive wear | Ingress of hard particles (mill scale, grit) through seal | Gradual; increases backlash |
| Input/output shaft | Fatigue cracking | Bending + torsional loading; keyway stress concentration | Gradual; detectable via strain gauges or MCSA torsional component |
| Shaft | Fretting corrosion at coupling | Micro-slip in interference fits | Gradual |
| Bearings (internal) | See Section 1 | — | — |
| Oil seal / labyrinth | Wear, hardening, damage | Abrasion + thermal cycling; oil leaks allowing ingress | Gradual; leads to lubricant starvation |
| Lubricant | Viscosity breakdown, particle contamination, water emulsification, oxidation | Thermal + mechanical shear; water ingress via breather/seal | Gradual; particle count (ISO cleanliness code) is primary KPI |
| Housing / mounting | Fretting / fatigue cracks at bolt seats | Vibration-induced looseness; improper torque | Gradual; ODS (operational deflection shape) changes |

### Sensor Signatures
- Vibration: GMF and harmonics; sidebands at ±shaft rate = modulation by shaft eccentricity or pitch error
- Oil particle count (LaserNet Fines, Q200 counter): ferrous debris index (FDI), ISO cleanliness 4406
- Oil spectroscopy (ICP-OES): iron/copper/chromium ppm trends indicate which component is wearing
- Temperature (oil sump): rises under load if viscosity drops or film breaks

### Typical TTF
- Pitting onset to catastrophic failure: weeks to months (highly load-dependent)
- Scuffing: hours once initiated

### Criticality
**HIGH.** Pinion stand gearbox in hot rolling mill = entire stand down. Repair lead time 4–12 weeks for heavy forged gears.

---

## 3. Electric Motors (AC induction, synchronous)

### Scope
Mill drives (1–20 MW synchronous/DC), pump motors, fan motors, conveyor motors, crane motors.

### Parts and Failure Modes

| Part | Failure Mode | Mechanism | Degradation Pattern |
|------|-------------|-----------|-------------------|
| Stator winding — turn insulation | Turn-to-turn short | Partial discharge (PD) erodes insulation at enamel weaknesses; thermal cycling; voltage spike from VFD | Gradual (months of PD) then sudden arc |
| Stator winding — ground insulation | Ground fault | Combined thermal aging + moisture + PD → insulation resistance <1 MΩ | Gradual |
| Stator winding | Thermal degradation | Continuous over-temperature (class F: 155°C limit) halves insulation life per 10°C above rating (Arrhenius) | Gradual; measurable via polarisation index (PI) and dielectric response |
| Rotor bars (squirrel cage) | Cracked / broken rotor bar | Thermal + mechanical stresses; fatigue under load cycling; casting voids | Gradual; detectable via MCSA at (1±2s)f₀ sidebands (s = slip); FFT of stator current |
| Rotor end ring | Cracking | Fatigue at joint with bars; centrifugal stress | Gradual progression to bar looseness |
| Rotor — eccentricity | Static/dynamic eccentricity | Bearing wear, shaft bow, manufacturing tolerance; increases uneven magnetic pull (UMP) | Gradual; UMP accelerates bearing wear (positive feedback loop) |
| Bearings | See Section 1 | DE bearing is higher-load side in belt/gear-driven motors | — |
| Shaft | Fatigue cracking | Stress concentrator at keyway + torsional transients | Gradual |
| Cooling system | Blocked ducts, failed cooling water, fin fouling | Ingress of mill scale dust; water circuit blockage | Gradual thermal rise; sudden if blocked completely |

### Sensor Signatures
- Motor Current Signature Analysis (MCSA): broken rotor bar → sidebands at (1±2s)f₀; eccentricity → 2× line frequency component [Thomson & Fenger, 2001, IEEE IAS Transactions — canonical reference]
- Insulation resistance (megger, offline): PI < 2.0 flags degraded insulation
- Partial discharge (online PD monitor, Doble PD sensor): pC level; trending
- Winding temperature (RTD, PT100): Class F motors: 155°C max; trip at 160°C
- Vibration: 2× line frequency for eccentricity; BPFI/BPFO for bearings

### Typical TTF
- Turn-to-turn short: months of PD activity before interphase fault
- Broken rotor bar: months from crack initiation to functional degradation
- Thermal failure: exponential with temperature excess

### Criticality
**HIGH (drive motors), MEDIUM (auxiliary).** Blast furnace main blower motor = single-point-of-failure for hot metal production.

---

## 4. Centrifugal Pumps

### Scope
Cooling water pumps (open circuit, closed circuit), hydraulic AGC pumps, lubrication oil pumps, descaling pumps (high-pressure, 200–300 bar), scale pit pumps (slurry).

### Parts and Failure Modes

| Part | Failure Mode | Mechanism | Degradation Pattern |
|------|-------------|-----------|-------------------|
| Impeller | Cavitation erosion | Bubble collapse at low-pressure zone; NPSH margin insufficient | Gradual pitting → sudden performance collapse; noise (broadband 1–4 kHz) and vibration |
| Impeller | Abrasive wear | Mill scale, sand in cooling water | Gradual loss of vane thickness → head loss |
| Impeller | Corrosion | Aggressive process water (pH, dissolved oxygen) | Gradual |
| Impeller | Hydraulic imbalance from wear | Asymmetric wear → unbalance → bearing load | Gradual; vibration 1× increases |
| Mechanical seal | Face wear, spring fatigue, O-ring hardening | Continuous contact + thermal cycling | Gradual wear; detectable by seal-flush flow rate drop and leakage |
| Mechanical seal | Dry running failure | Loss of seal flush → rapid face destruction | Sudden (minutes); temperature spike at seal |
| Shaft | Fatigue cracking | Bending from hydraulic radial force (off-BEP operation); keyway stress raiser | Gradual |
| Wear rings (neck ring, case ring) | Abrasive wear | Particulate erosion, contact under deflection | Gradual; increases internal recirculation → efficiency loss → elevated temperature |
| Bearings | See Section 1 | Radial + thrust loading | — |
| Casing volute | Erosion-corrosion | High-velocity slurry impingement | Gradual; wall thinning |

### Sensor Signatures
- Flow and pressure: below-BEP operation → recirculation noise; cavitation → broadband vibration
- Vibration: 1× (imbalance/misalignment), vane pass frequency (Z × RPM), subbharmonics for rotating stall
- Temperature: seal housing, bearing housing
- Differential pressure across pump: efficiency proxy; degradation = dp drop at constant speed

### Typical TTF
- Cavitation erosion to performance failure: weeks to months
- Mechanical seal dry-run failure: minutes

### Criticality
**CRITICAL for descaling pumps** (no descale = strip surface oxidation = quality defect). **HIGH for cooling water** (furnace / caster cooling failure = safety event).

---

## 5. Fans and Blowers

### Scope
Blast furnace cold blast blowers (centrifugal, multi-stage, >100,000 Nm³/h), induced draft (ID) fans for gas cleaning, fume extraction fans, cooling tower fans, combustion air fans for reheat furnaces.

### Parts and Failure Modes

| Part | Failure Mode | Mechanism | Degradation Pattern |
|------|-------------|-----------|-------------------|
| Impeller blades | Erosion | Carry-over dust in gas streams (BF gas, coke oven gas); high-velocity particle impingement | Gradual mass loss → imbalance; vibration 1× increases progressively |
| Impeller blades | Corrosion (pitting) | Condensation of acid gas (SO₂, HCl) on blade surface | Gradual |
| Impeller blades | Fatigue cracking | Resonance at blade natural frequency near operating speed; stall-induced cyclic loading | Gradual crack growth → sudden fracture → catastrophic imbalance |
| Impeller hub / disc | Fatigue cracking | High centrifugal stress; stress concentrations at blade attachment | Gradual; requires specialist NDT (TOFD, phased array) |
| Shaft | Fatigue / torsional cracking | Coupled to high-inertia impeller; drive-train torsional resonance | Gradual |
| Bearings | See Section 1 | High axial + radial loads in multi-stage blowers | — |
| Inlet guide vanes (IGV) | Wear, binding, actuator failure | Erosion of guide vane edges; actuator rod corrosion | Gradual; controllability loss |
| Shaft seal (labyrinth / mechanical) | Gas leakage | Wear, thermal distortion | Gradual; safety hazard for flammable gas systems |

### Sensor Signatures
- Vibration 1× (imbalance from erosion): primary KPI; trend monitoring with alarm at 2× baseline
- Blade pass frequency (BPF = n_blades × RPM): changes with erosion-induced blade asymmetry
- Acoustic emission / ultrasonic: crack detection in rotating blades [unverified for BF blowers specifically]
- Process: flow, pressure ratio, power consumption (efficiency proxy)

### Typical TTF
- Erosion-imbalance: months; predictable from vibration trend slope
- Blade fatigue fracture: hours to days from crack initiation to fracture (if crack is found in NDT, immediate shutdown)

### Criticality
**CRITICAL for BF cold blast blower** — loss = furnace chilling within hours = weeks of recovery. A single-point-of-failure on many blast furnaces.

---

## 6. Compressors

### Scope
Nitrogen plant compressors, instrument air compressors (reciprocating and screw), oxygen plant (centrifugal), CO₂ recovery (centrifugal/reciprocating), hydraulic accumulators.

### Parts and Failure Modes

| Part | Failure Mode | Mechanism | Degradation Pattern |
|------|-------------|-----------|-------------------|
| Valves (reciprocating) | Fatigue fracture of valve plate/reed | Cyclic opening/closing at high frequency; resonance; liquid carry-over slugging | Sudden (single cycle fracture under slug) or gradual fatigue |
| Valves | Wear, leakage (blow-by) | Abrasive particles; loss of seating face flatness | Gradual; detectable via cylinder temperature + pressure trace (p–θ diagram) |
| Piston rings | Wear, blow-by | Abrasion by particulate contamination | Gradual; discharge temperature rises |
| Crankshaft / connecting rod | Fatigue cracking | Bending + torsional cycling; imbalance loads | Gradual (weeks) |
| Crankshaft bearings | See Section 1 | — | — |
| Cylinder liner | Abrasive wear, scoring | Poor lubrication; particle ingress | Gradual |
| Screw compressor rotors | Lobe wear | Particle ingress; loss of clearance | Gradual efficiency loss |
| Centrifugal compressor impeller | Fouling (deposits) | Oil carry-over, process contamination builds on blade | Gradual; head drop; vibration rise from deposit imbalance |
| Centrifugal compressor impeller | Surge damage | Flow reversal under off-design operation → impeller erosion, bearing overload | Sudden |
| Shaft seals (dry gas, labyrinth) | Wear, gas leakage | Thermal distortion; particulate | Gradual; gas consumption rises |

### Sensor Signatures
- Reciprocating: cylinder pressure trace shape (p–θ diagram detects valve blow-by); temperature each cylinder
- Screw / centrifugal: vibration, discharge pressure/temperature, specific power (kW/Nm³)
- Gas purity (O₂ analyzer) for air separation: purity drop = leak indicator

### Typical TTF
- Valve fatigue: sudden
- Piston ring wear: months
- Surge event: immediate damage

### Criticality
**HIGH for oxygen plant compressors** (O₂ supply to BOF steelmaking). **MEDIUM for instrument air** (loss = instrument failures across plant).

---

## 7. Hydraulic Systems

### Scope
Rolling mill Automatic Gauge Control (AGC) hydraulic cylinders and servo valves, mill roll-force cylinders, caster segment clamping hydraulics, crane holding brakes.

### Parts and Failure Modes

| Part | Failure Mode | Mechanism | Degradation Pattern |
|------|-------------|-----------|-------------------|
| Servo valve / proportional valve | Spool erosion, silting, stiction | Particulate contamination (ISO 4406 > 15/13/10 causes spool stiction); fluid degradation | Gradual; position error increases; pressure dithering |
| Servo valve | Internal leakage (seal wear) | Thermal cycling of O-rings; fluid swelling | Gradual; control loop deadband widens |
| Hydraulic cylinder seals | Extrusion, wear | High-pressure cycling; side loading from misalignment | Gradual; external leakage; position drift |
| Hydraulic cylinder rod | Pitting corrosion | Condensation + mill spray water ingress under wiper seals | Gradual; seal damage acceleration |
| Pump (piston/vane) | Piston/barrel wear | Cavitation; particulate; insufficient case drain flow | Gradual; efficiency loss → flow deficit → AGC bandwidth reduction |
| Accumulator bladder | Fatigue rupture | Pressure cycling fatigue | Sudden; pressure spike/loss |
| Hoses and fittings | Fatigue cracking | Vibration + high-cycle pressure pulsation | Gradual (crack) → sudden (rupture) |
| Filter elements | Bypass valve opening | Clogged element → bypass opens → unfiltered fluid circulates | Sudden deterioration of downstream components |

### Sensor Signatures
- Particle counter (inline): ISO 4406 code — alarm at 16/14/11 for servo systems
- Pressure trace: ripple amplitude increase indicates pump wear; servo valve response lag
- Fluid temperature: above 60°C accelerates seal degradation and viscosity loss
- Cylinder position error (encoder): increasing deadband = servo valve wear

### Typical TTF
- Servo valve silting: hours to days after contamination event
- Cylinder rod corrosion to seal failure: weeks to months

### Criticality
**CRITICAL for AGC.** AGC cylinder failure = loss of thickness control = product quality defect → strip rejection → revenue loss. Response time under 50 ms required; any control lag is immediately visible in strip gauge.

---

## 8. Rolling Mill Rolls

### Scope
Work rolls (WR), intermediate rolls (IMR), backup rolls (BUR) in hot strip mill (HSM) and cold rolling mill (CRM); edger rolls; vertical rolls.

### Parts and Failure Modes

| Part | Failure Mode | Mechanism | Degradation Pattern |
|------|-------------|-----------|-------------------|
| Work roll barrel — contact surface | Thermal fatigue cracking (fire cracking / alligator skin) | Cyclic heating (contact with strip at 800–1200°C) and cooling (water spray); ΔT gradient drives surface tension → compression cycling | Gradual crack network; visible after roll grinding; sudden spalling if crack propagates below surface |
| Work roll barrel | Spalling / flaking | Subsurface fatigue (Hertzian) beneath contact surface; pre-existing cracks or inclusions | Sudden fracture of shell segment; catastrophic — can destroy strip and neighboring rolls |
| Work roll barrel | Wear (abrasive + adhesive) | Strip/scale abrasion; partial stick-slip at high reduction | Gradual; measured by roll profile (crown change); controlled by roll change schedule |
| Work roll barrel | Surface roughness loss (glazing) | Adhesive polishing in cold rolling; loss of required Ra for strip friction | Gradual; measured by Ra profilometer |
| Work roll neck / journal | Fatigue cracking | Bending moment at barrel/neck transition; stress concentration at fillet radius | Gradual — NDT ultrasonic inspection at each roll change |
| Backup roll barrel | Spalling | Subsurface fatigue driven by high contact pressure (50–80 kN/mm); initiated at inclusions in forged steel | Sudden; fragments can damage WR and strip |
| Backup roll neck | Contact fatigue (roll chock contact) | Fretting between roll neck and chock liner under cyclic rolling force | Gradual; groove formation visible on neck |
| Roll chock bearing (four-row tapered roller) | See Section 1 — outer ring fatigue, roller fatigue | High radial loads (up to 60 MN in BUR) + axial thrust | Gradual; BPFO/BPFI in vibration; temperature rise on chock |

### Sensor Signatures
- Roll force (load cells): force profile per pass; asymmetric force = bent/worn roll
- Vibration (accelerometer on chock): bearing defect frequencies
- Eddy-current roll surface scanner (offline, on grinder): cracks, hard spots
- Ultrasonic C-scan (roll shop): subsurface spall detection before catastrophic failure [Kocks/SMS roll testing practice — common but unverified for specific Tata facility]

### Typical TTF
- Thermal fatigue cracks: weeks to months of campaigns before dressing
- Spalling: minutes from crack propagation to fracture (essentially sudden once threshold crack depth reached)
- Wear: controlled by roll change frequency (typically 3–8 km rolled)

### Criticality
**EXTREMELY HIGH.** Work roll spalling can destroy $200,000+ of backup roll and contaminate strip with embedded fragments. BUR spalling = stand shutdown for days. Safety hazard from ejected fragments at high speed.

---

## 9. Conveyor Systems

### Scope
Raw materials conveyors (ore, coal, coke, sinter — belt widths up to 2400 mm, speeds 2–5 m/s), in-plant transfer conveyors, elevated skip/skip hoist (BF charging).

### Parts and Failure Modes

| Part | Failure Mode | Mechanism | Degradation Pattern |
|------|-------------|-----------|-------------------|
| Conveyor belt — carcass | Tension fatigue cracking | Cyclic tensile loading over idlers + pulleys; impact at loading points | Gradual (months); accelerated by impact damage |
| Conveyor belt — cover | Abrasive wear | Material abrasion | Gradual; measured by cover thickness gauge |
| Conveyor belt — splice | Splice failure | Vulcanised splice fatigue; mechanical fastener pull-out | Gradual fatigue → sudden fracture; belt rip |
| Idler roller (return / carry) | Bearing seizure | Seal failure → water/fines ingress → lubricant contamination | Gradual bearing wear → sudden seizure; seized idler = belt damage + potential fire |
| Idler roller | Shell wear (abrasion) | Abrasive ore/coal fines through failed seal | Gradual |
| Drive pulley | Lagging wear / bond failure | Abrasion + thermal cycling of rubber lagging | Gradual; belt slippage → drive overload |
| Drive pulley bearing | See Section 1 | High radial load + belt tension | — |
| Take-up pulley / counterweight | Take-up travel loss | Bearing failure in take-up frame; wire rope wear on gravity take-up | Gradual; belt tension drops → slippage |
| Drive gearbox | See Section 2 | — | — |
| Motor | See Section 3 | — | — |

### Sensor Signatures
- Belt misalignment switch (mechanical): immediate alarm
- Idler temperature (thermal camera, walk-round or fixed): hot idler = seized bearing [thermal scanning practice — industry standard at Tata Steel and BHP; unverified specific installation]
- Belt speed sensor: slip detection
- Belt rip detector (inductive loop in belt): detects longitudinal rip propagation
- Motor current: overload = belt resistance increase (seized idler, material build-up)

### Typical TTF
- Idler bearing: weeks from AE detectable to seizure
- Belt splice: gradual fatigue over 6–24 months depending on splice type

### Criticality
**HIGH for raw materials supply chain.** Conveyor failure at ore yard = BF feed interruption within hours. Fire risk from seized hot idler in dusty environment is a major safety concern.

---

## 10. Overhead Cranes and Ladle Cranes

### Scope
Ladle cranes (250–350 t capacity, melt shop), tundish cranes, coil cranes (cold rolling), slab/bloom cranes (hot strip).

### Parts and Failure Modes

| Part | Failure Mode | Mechanism | Degradation Pattern |
|------|-------------|-----------|-------------------|
| Wire rope (hoist) | Fatigue wire breakage | Cyclic bending over sheave + drum; inter-wire fretting | Gradual: wire breaks accumulate; inspection per ISO 4309 (reject criterion: 10 breaks/lay length) |
| Wire rope | Corrosion | Melt shop environment (H₂O + SO₂); core degradation | Gradual; strand pitting |
| Drum / sheave grooves | Wear | Rope abrasion | Gradual; increases rope bending radius fatigue |
| Hoist brake | Lining wear, spring fatigue, thermal glazing | Thermal cycling at brake disc; oil contamination of lining | Gradual wear; sudden if spring breaks → brake drag or non-engagement |
| Hoist brake | Actuator (solenoid/hydraulic) failure | Electrical/hydraulic failure | Sudden |
| Hook / hook block | Fatigue cracking at shank | Cyclic tensile load; impact loading at set-down | Gradual; NDT at inspection intervals |
| Cross-travel / long-travel drive | Wheel flange wear, rail wear | Misalignment; crane skew | Gradual; rail corrugation → vibration |
| Gearbox (hoist, travel) | See Section 2 | — | — |
| Motor (hoist, travel) | See Section 3 | Frequent start-stop = high thermal stress | — |
| Control panel / slip rings | Contact wear, insulation breakdown | Vibration loosening + thermal cycling in hot environment | Gradual; intermittent contact faults |

### Sensor Signatures
- Load cell (hoist): overload detection; asymmetric load = rigging fault
- Rope tension monitoring (tension pin or load cell): slack rope detection
- Brake wear indicator (position sensor on brake pad)
- Motor current (overload = mechanical fault in gearbox or rope drum)
- Vibration on gearbox and drum shaft

### Typical TTF
- Rope wire break: weeks from first break detection to rejection threshold
- Brake lining: months depending on duty cycle

### Criticality
**SAFETY-CRITICAL.** Ladle crane hoist failure with liquid steel ladle = catastrophic disaster (mass fatality potential). Governed by stringent regulatory inspection (ASME B30.2, Factory Act equivalents). Priority for prescriptive maintenance.

---

## 11. Reheating Furnace Components

### Scope
Walking beam / walking hearth reheat furnaces in hot strip mill; pusher-type (older plants); also soaking pits.

### Parts and Failure Modes

| Part | Failure Mode | Mechanism | Degradation Pattern |
|------|-------------|-----------|-------------------|
| Burner nozzle | Erosion/oxidation | High-temperature flame impingement; scale particle abrasion | Gradual; flame shape distortion → uneven slab heating → rolled-in defects |
| Burner nozzle | Refractory blockage | Scale and sinter deposit build-up | Gradual then sudden loss of throughput |
| Refractory lining | Spalling / cracking | Thermal shock from cold slab loading; chemical attack (Na₂O in scale); abrasion from slabs sliding | Gradual over campaign; sudden spall from thermal shock event |
| Refractory lining | Erosion | Slab-dragging wear on hearth tiles | Gradual |
| Walking beam (water-cooled skid beam) | Thermal fatigue cracking in welds | Cyclic thermal loading at beam-end connection; weld residual stress | Gradual; detectable by visual inspection during maintenance windows |
| Walking beam | Water leak (internal tube failure) | Tube corrosion; fatigue cracking in water circuit | Sudden if pin-hole develops; steam in furnace → slab surface mark |
| Recuperator | Fouling (soot, scale deposits) | Combustion product deposit on heat-exchange surfaces | Gradual; preheat air temperature drops; detectable by air temperature trend |
| Recuperator | Tube corrosion / oxidation failure | High-temperature oxidation; condensation corrosion at low load | Gradual then sudden tube failure |
| Drive system (walking beam actuator) | Hydraulic/mechanical drive wear | High-cycle loading of hydraulic cylinders or rack-and-pinion drive | Gradual |
| Combustion air fan | See Section 5 | — | — |
| Gas control valves | Actuator failure, positioner drift | Thermal degradation; vibration | Gradual |

### Sensor Signatures
- Thermocouple arrays (zone by zone): temperature uniformity; thermocouple drift or failure detectable by comparison
- Flue gas O₂/CO analyzer: combustion efficiency; CO spike = refractory damage admitting cold air
- Fuel flow vs. temperature setpoint: increasing fuel for same temperature = insulation degradation
- Pressure differential (furnace vs. atmosphere): infiltration detection

### Typical TTF
- Refractory campaign: 12–36 months (planned relining)
- Water-cooled beam tube: sudden if leak; hours to days from micro-crack

### Criticality
**HIGH for production.** Furnace shutdown = HSM production stops within 30–60 minutes (slab buffer). Refractory failure = emergency shutdown, days of repair.

---

## 12. Continuous Caster Components

### Scope
Mould (copper plates, wide face, narrow face), secondary cooling (spray nozzles), segment rolls (strand guide rolls), withdrawal and straightening rolls (W&S), dummy bar.

### Parts and Failure Modes

| Part | Failure Mode | Mechanism | Degradation Pattern |
|------|-------------|-----------|-------------------|
| Mould copper plates | Wear (groove formation) | Strand shell movement against copper; lubricant (mould flux) film inadequacy | Gradual; measured by mould taper calibration; sudden if groove leads to breakout |
| Mould copper plates | Thermal fatigue cracking | Cyclic thermal loading at meniscus → surface crack network (heat checking) | Gradual; inspection at mould change |
| Mould copper plates | Plating erosion (nickel/chrome coating) | Physical and chemical wear | Gradual; coating thickness measurement |
| Mould water channel | Scale deposit / blockage | Hard water scaling in cooling channels | Gradual; heat flux reduction → hot spot → breakout risk |
| Oscillation mechanism (hydraulic or electromechanical) | Stroke/frequency drift | Wear in oscillation bearings / guide pins; hydraulic leak | Gradual; detectable by oscillation table monitoring |
| Oscillation bearings | See Section 1 | High cyclic load at 100–400 cpm | — |
| Segment rolls (strand guide) | Wear, bearing failure | Continuous contact with solidifying strand at >800°C surface; roll cooling water failure | Gradual wear; sudden if cooling fails → roll overheating → seizure |
| Segment rolls | Misalignment | Thermal distortion of segment frame; bearing play | Gradual; strand bulging → internal crack |
| Segment roll bearings (inside segment frame — inaccessible) | See Section 1 | Contaminated environment; limited lubrication access | — |
| Spray nozzles | Clogging (scale, calcium carbonate) | Hard water; scale accumulation in nozzle orifice | Gradual; detectable by water flow deviation from setpoint → uneven secondary cooling → strand surface cracks |
| Spray nozzles | Nozzle wear / erosion | Abrasive scale particles in cooling water | Gradual; spray angle broadens → cooling non-uniformity |
| Withdrawal roll bearings | See Section 1 | High load, water-contaminated environment | — |
| Breakout detection system (thermocouple arrays in mould) | Thermocouple failure | Vibration + thermal cycling | Sudden single-point failure; missed breakout = molten steel spillage = catastrophic safety event |

### Sensor Signatures
- Mould thermocouple matrix (typically 4–8 rows): thermal asymmetry = uneven shell growth = breakout precursor [standard industry practice; SMS Group / Danieli breakout prediction systems]
- Mould water flow and temperature delta (ΔT = heat flux proxy): heat flux drop = fouling; spike = local hot spot
- Oscillation stroke/frequency (encoder, LVDT): deviation = mechanism wear
- Segment cooling water flow per segment: blockage detection
- Strand shell thickness (gamma-ray gauging, online): shell thinning precedes breakout [unverified for Tata specifically]

### Typical TTF
- Mould plate wear to campaign end: typically 500–1500 heats (planned maintenance)
- Breakout: sudden (minutes) once mould thermocouple pattern detected; prediction systems target 2–5 minute early warning

### Criticality
**HIGHEST SAFETY CRITICALITY in caster.** Breakout = molten steel spillage = multiple fatality risk + equipment destruction. Industry uses dedicated real-time breakout prediction models (rule-based + ML hybrid) as hard safety systems.

---

## Summary Table: Equipment → Critical Parts → Primary Failure Modes

| Equipment Class | Most Critical Parts | Dominant Failure Modes | Degradation | Steel-Plant Criticality |
|----------------|--------------------|-----------------------|-------------|------------------------|
| Rolling-Element Bearings | Inner/outer race, rolling elements, cage | Spalling (fatigue), EDM pitting, cage fracture, lubricant starvation | Gradual (race); Sudden (cage) | HIGHEST (mill, BF blower) |
| Gearboxes | Gear teeth (contact + root), shaft, bearings, lubricant | Pitting/spalling, bending fatigue, scuffing, oil contamination | Gradual/Sudden (scuffing) | HIGH (pinion stand) |
| Electric Motors | Stator winding insulation, rotor bars, bearings | Turn-to-turn short, broken rotor bar, eccentricity, thermal degradation | Gradual | HIGH (drive motors, BF blower motor) |
| Centrifugal Pumps | Impeller, mechanical seal, wear rings, shaft | Cavitation erosion, seal dry-run, abrasive wear, fatigue | Gradual/Sudden (seal) | CRITICAL (descaling, caster cooling) |
| Fans/Blowers | Impeller blades (erosion, fatigue), shaft seals | Erosion-imbalance, blade fatigue fracture, seal leakage | Gradual/Sudden (fracture) | CRITICAL (BF cold blast) |
| Compressors | Valves (reciprocating), impeller (centrifugal), seals | Valve plate fracture, surge damage, piston ring blow-by | Sudden (valve)/Gradual | HIGH (O₂ plant, instrument air) |
| Hydraulic Systems | Servo valves, cylinder seals, pump, accumulator | Particulate silting, seal extrusion, cavitation, bladder fatigue | Gradual/Sudden (hose) | CRITICAL (AGC thickness control) |
| Rolling Mill Rolls | WR barrel (thermal fatigue/spalling), BUR barrel (spalling), neck, chock bearings | Spalling (subsurface), thermal fatigue, wear, chock fretting | Gradual then Sudden | EXTREME (spalling = stand down + strip damage) |
| Conveyor Systems | Belt splice, idler bearings, drive pulley lagging | Splice fatigue fracture, idler seizure, belt rip | Gradual/Sudden (splice) | HIGH (raw materials supply) |
| Overhead/Ladle Cranes | Wire rope, hoist brake, hook, gearbox | Wire fatigue, brake spring failure, hook fatigue | Gradual | SAFETY-CRITICAL (ladle handling) |
| Reheating Furnace | Refractory lining, water-cooled beam tubes, burner nozzles, recuperator | Thermal spalling, tube leak, nozzle erosion, fouling | Gradual | HIGH (production gate) |
| Continuous Caster | Mould copper plates, oscillation bearings, segment rolls, spray nozzles, mould thermocouples | Breakout (mould wear + TC failure), segment roll bearing seizure, nozzle clogging | Gradual/Sudden (breakout) | HIGHEST SAFETY (breakout = fatality) |

---

## Failure Cost and Safety Priority Ranking

1. **Continuous caster breakout** — Molten steel spill; multiple fatalities possible; $1M+ equipment damage; 1–2 days downtime minimum. SAFETY CLASS 1.
2. **Rolling mill roll spalling** — Stand destroyed; $200K–500K roll damage; strip scrapped; 1–3 day repair. PRODUCTION IMPACT CLASS 1.
3. **Ladle crane hoist failure** — Liquid steel ladle drop; catastrophic; regulatory stop. SAFETY CLASS 1.
4. **Blast furnace blower failure** — BF chilling; 2–6 weeks recovery; $10M+ production loss. PRODUCTION IMPACT CLASS 1.
5. **AGC hydraulic servo failure** — Thickness out of control; strip rejection until repaired. QUALITY/REVENUE CLASS 1.
6. **Rolling mill chock bearing failure** — Stand down; 4–24 hour repair depending on stock; $500K–$1M per event [unverified exact figure].
7. **Melt shop crane gearbox failure** — Production routing disruption; safety risk from loss of ladle control.
8. **Descaling pump failure** — Surface quality defect on affected coils; potential coil rejection.

---

## Implications for Synthetic Dataset Generation

### Failure Signatures to Synthesize per Equipment

| Equipment | Primary Sensor | Synthetic Signal Characteristics |
|-----------|---------------|----------------------------------|
| Bearing (any) | Vibration (envelope) | Gaussian baseline noise + impulsive component at BPFI/BPFO with growing amplitude; RMS trend follows Paris law |
| Gearbox | Vibration (synchronous) | GMF + harmonics; sideband amplitude modulated by shaft-rate exponential growth; oil debris count linearly rising |
| Motor | Stator current (MCSA) | (1±2s)f₀ sideband amplitude; grows from −60 dBc baseline toward −40 dBc at failure |
| Pump | Vibration + flow + pressure | Vane pass frequency; broadband noise floor rise (cavitation); ΔP degradation curve |
| Fan | Vibration 1× + process flow | 1× growing linearly (erosion imbalance); step change if blade fracture |
| Hydraulic servo | Pressure trace + position error | Increasing deadband width; pressure ripple amplitude growth |
| Roll (work roll) | Roll force profile + chock vibration | Force asymmetry growing; bearing defect frequencies |
| Caster segment | Mould ΔT matrix + oscillation | Asymmetric thermocouple reading growth; oscillation frequency drift |

### Class Imbalance Note

In all equipment classes, healthy operation constitutes >95% of time-series data. Failure events (final stage before failure/repair) are <5%. For safety-critical failures (breakout, crane), rates may be <0.1% of operational hours. Synthetic generation must reflect realistic class ratios while providing sufficient failure-mode examples for model training. Recommended approach: use Weibull-based RUL sampling to control failure density in synthetic batches; do NOT oversample uniformly.

### Recommended Public Dataset Analogues

| Public Dataset | Closest Equipment Analogue |
|---------------|--------------------------|
| Case Western Reserve University Bearing (CWRU) | Rolling-element bearings (motor, pump) |
| IMS / Pronostia (FEMTO) bearing datasets | Rolling-element bearing RUL |
| PHM 2010 Milling | Work roll / cutting tool wear (analogous surface wear) |
| NASA C-MAPSS turbofan | Multi-component degradation (analogous to compressor / fan train) |
| MIMII Dataset (Malfunctioning Industrial Machine Investigation) | Pump, fan, gearbox, slider motors |
| SECOM (semiconductor) | Process anomaly structure (not equipment but useful for imbalance handling) |

---

## References

1. Randall, R.B. (2011). *Vibration-based Condition Monitoring*. Wiley. — Bearing/gearbox fault frequency theory.
2. Thomson, W.T. & Fenger, M. (2001). "Current Signature Analysis to Detect Induction Motor Faults." *IEEE Industry Applications Magazine*, 7(4), 26–34. — MCSA broken rotor bar.
3. Lee, J., Qiu, H., Yu, G., Lin, J. (2007). "Bearing Data Set." IMS, University of Cincinnati, NASA Prognostics Data Repository. — IMS bearing AE lead time.
4. Sheng, S. (2012). "Wind Turbine Gearbox Condition Monitoring Round Robin Study." NREL/TP-5000-54530. — Gearbox oil analysis methodology (analogous to steel plant).
5. SMS Group (2024). "Breakout Detection and Prevention in Continuous Casting." SMS Technical Bulletin. — Mould thermocouple breakout prediction. [unverified: URL not retrieved; known practice]
6. Tata Steel Annual Report 2022-23. "Digital Transformation in Manufacturing." — 15% unplanned downtime reduction claim. [unverified exact citation from report; widely cited in Tata press releases]
7. ISO 4306-1:2007. Cranes — Vocabulary. — Wire rope inspection criteria (B30.2 for hoist brakes).
8. ISO 4406:2021. Hydraulic fluid power — Method for coding the level of contamination by solid particles. — Hydraulic cleanliness codes.
9. Mobley, R.K. (2002). *An Introduction to Predictive Maintenance* (2nd ed.). Butterworth-Heinemann. — General failure mode taxonomy.
10. Bloch, H.P. & Geitner, F.K. (2012). *Machinery Failure Analysis and Troubleshooting* (4th ed.). Elsevier. — Pump/compressor/seal failure modes.
