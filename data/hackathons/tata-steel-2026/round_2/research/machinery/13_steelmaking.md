# Steelmaking Equipment — Deep PdM Reference
## BOF/LD Converter · EAF · Ladle Furnace · RH Degasser + Auxiliaries
*Research date: 2026-06-08 | Tata Steel Round 2 — Maintenance Wizard subagent context*

---

## 1. Equipment Types and Sub-systems

### 1.1 BOF / LD Converter (Basic Oxygen Furnace)

A refractory-lined steel vessel (~100–350 t capacity) into which pure oxygen is blown via a water-cooled lance to oxidise carbon from hot metal. Core sub-systems:

| Sub-system | Function |
|---|---|
| Converter vessel + shell | Holds molten charge; outer steel shell houses refractory lining |
| Trunnion ring + trunnion pins | Load-bearing structural ring; two trunnion pins allow vessel tilt 0–360° |
| Tilt drive (gearbox + motor) | Electric or hydraulic drive; tilts vessel for charging, tapping, slagging |
| Oxygen blowing lance + hoist | 4–6-port copper lance tip; hoisted via cable drive; delivers O₂ at supersonic velocity |
| Lance quick-change system | Semi-automated lance swap mechanism; reduces changeover to <30 min |
| Gas recovery hood / OG system | Captures CO-rich off-gas; wet/dry scrubbers or electrostatic precipitators |
| Slag splash / bottom stirring | N₂ or Ar bottom tuyeres for bath stirring; slag splashing gun for lining protection |
| Tap hole block + slide gate | Refractory block at tap hole; controls steel tapping stream |

### 1.2 Electric Arc Furnace (EAF)

Three-phase AC (or DC) furnace melting scrap / DRI via graphite electrodes. Common at Tata Steel Ijmuiden (electric steelmaking route). Sub-systems:

| Sub-system | Function |
|---|---|
| Furnace shell (upper/lower) | Upper shell: water-cooled panels + roof ring. Lower shell: refractory-lined hearth |
| Roof + electrode portal | Eccentric Bottom Tapping (EBT) design typical; roof swings for charging |
| Graphite electrodes (3×) | 400–700 mm dia, 1.5–3 m length per section; continuous addition via electrode column |
| Electrode arms + masts | Hydraulic/servo-electric arms holding electrodes; move up/down for arc gap control |
| Electrode regulation system | Closed-loop hydraulic or servo regulator; maintains constant arc impedance |
| HV transformer + busbar | Furnace transformer 40–200 MVA, 33 kV primary → 0.5–1.5 kV secondary |
| Water-cooled panels (WCP) | Upper shell sidewall + roof panels; cooled by closed-loop water circuit |
| EBT tap hole + slag door | Bottom eccentric tapping avoids slag carry-over; slag door for de-slagging |
| Fume extraction + baghouse | Captures EAF off-gas + particulates |

### 1.3 Ladle Furnace (LF)

Secondary metallurgy station heating and alloying steel in a ladle. Three-electrode AC system. Sub-systems:

| Sub-system | Function |
|---|---|
| Ladle vessel + refractory | Preheated ladle with MgO-C or alumina-spinel lining |
| Three graphite electrodes | 300–500 mm dia; smaller than EAF electrodes; ~27.5 kWh/t average |
| Electrode column + clamps | Vertical travel; copper contact clamps with water cooling |
| Transformer | Lower MVA than EAF (typically 20–60 MVA); voltage ~200–350 V secondary |
| Argon stirring porous plug | Bottom plug delivers Ar for homogenisation and inclusion flotation |
| Alloy + flux addition system | Gravity chutes or wire injection for ferro-alloys, lime, cored wire |
| Ladle slide gate (2-plate or 3-plate) | Refractory plates controlling steel flow to caster; actuated hydraulically |

### 1.4 RH Vacuum Degasser

Ruhrstahl-Heraeus recirculation degasser for ultra-low-carbon (ULC) steel. Sub-systems:

| Sub-system | Function |
|---|---|
| Vacuum vessel (upper/lower) | Refractory-lined cylindrical vessel; houses molten steel during treatment |
| Up-snorkel + down-snorkel | Two immersion legs dipped into ladle; steel circulates via Ar lift gas |
| Vacuum pumps / steam ejectors | Multi-stage steam ejectors or mechanical pumps pulling vessel to <0.5 mbar |
| Argon lift gas injection | Ar injected into up-snorkel to drive recirculation (~85–135 t/min) |
| Top-blowing oxygen lance | Optional: decarburisation blow for C <20 ppm in <15 min |
| Alloy addition chutes | Pressurised hoppers add ferro-alloys under vacuum |
| Snorkel preheating system | Gas burners maintain snorkel at 900–1,500°C before dip-in |

---

## 2. Parts Breakdown

### 2.1 BOF Refractory System

- **Working lining**: Magnesia-carbon (MgO-C) bricks, 800–1,200 mm new thickness
- **Safety/permanent lining**: 100–200 mm behind working lining; last barrier before shell
- **Slag zone / impact zone**: Highest wear zones; wear 2.0–3.0 mm/heat (charge pad) vs 0.8–1.5 mm/heat (barrel) [oxmaint.com data]
- **Slag splash coating**: 5–30 mm protective N₂-splashed slag layer over hot face
- **Bottom blown tuyeres**: 6–18 permeable elements (refractory-encased steel tubes); replaced each reline

### 2.2 BOF Tilt Drive and Trunnion

- **Tilt gearbox**: Multi-stage planetary gearbox; ~4 gears per side; subject to cog wear from vibration during blowing
- **Trunnion ring bearings**: Spherical roller or slide bearings; diameters 800–1,200 mm; load 500–1,500 t dynamic
- **Trunnion pins**: Forged alloy steel; inspected for crack propagation every reline

### 2.3 Oxygen Lance Assembly

- **Lance tube**: Three concentric pipes (O₂ inner, water down-flow, water up-flow); overall length 15–22 m
- **Lance tip (head)**: Cast or forged deoxidised copper; 4–6 supersonic Laval nozzles; Mach 2.0 exit
- **Cooling water**: Recirculating at ~6 kg/cm² (≈0.6 MPa); outlet temperature must stay ≤60–65°C [IspatGuru]
- **Lance hoist**: Wire rope drive with position encoder; position accuracy ±10 mm

### 2.4 EAF Water-Cooled Panels

- **Panel construction**: Boiler-grade tube (70–90 mm dia, 8–10 mm wall), serpentine or box construction
- **Flow per panel**: 10–15 m³/h per m² of panel area [IspatGuru cooling system data]
- **Velocity**: 1.2–2.5 m/s normal; up to 5 m/s in slag-line zone
- **Heat flux**: 100–600 kW/m² depending on UHP practice

### 2.5 EAF Graphite Electrodes

- **Diameter**: 400–700 mm; joined by graphite nipple threaded joints
- **Consumption rate**: 1.5–2.5 kg/t steel (modern); 5–6 kg/t historical (pre-1990) [bestgraphiteelectrodes.com]
- **Arc tip temperature**: ~3,000°C; primary consumption by arc erosion + side oxidation
- **Column length maintained**: 1.5–3.0 m above furnace roof; new sections screwed on during heat

### 2.6 Ladle Slide Gate

- **Plate geometry**: 2-plate sliding (upper fixed + lower sliding) or 3-plate; refractory material: alumina-zirconia-carbon or magnesia-carbon
- **Bore diameter**: 65–130 mm depending on ladle size and casting speed
- **Actuator**: Hydraulic cylinder, 100–250 bar; spring-loaded fail-safe close
- **Replacement interval**: After 1–5 heats depending on grade (aggressive for clean-steel grades)

### 2.7 RH Snorkel Refractory

- **Material**: Magnesia-chrome or alumina-magnesia bricks; hot face ~300–500 mm thickness new
- **Campaign life**: 60–300 heats per snorkel set [IspatGuru RH article]
- **Intermediate maintenance**: After every 6 heats, ~20–60 min gunning repair
- **Bore enlargement effect**: As inner bore erodes, circulation rate drops → treatment time increases → energy rises

---

## 3. Sensors and Most Common Measurements

### 3.1 BOF Sensors

| Sensor | Location | Measurement |
|---|---|---|
| Shell thermocouples (TC array) | Embedded in vessel shell, 50–100 points | Shell temperature (°C) |
| IR thermography camera | Fixed overhead + portable | Full-shell 2D temperature map |
| 3D laser profiler (LiDAR) | Vessel mouth (scheduled scan) | Refractory lining thickness (mm) |
| Lance position encoder | Lance hoist cable drive | Lance tip height above bath (mm) |
| Lance cooling water flow meter | Return water pipe | Cooling water flow (m³/h) |
| Lance cooling water temperature (in/out) | Inline PT100/PT1000 | Water inlet + outlet T (°C) |
| Oxygen flow meter + pressure | Lance supply line | O₂ flow (Nm³/h), pressure (bar) |
| Off-gas analyser (CO, CO₂, O₂) | Gas recovery hood | Off-gas composition (%) |
| Bath temperature (sub-lance / thermocouple) | Immersion at blow end | Liquid steel temperature (°C) |
| Carbon/oxygen probe (sub-lance) | Immersion | [C], [O] in bath at blow end |
| Vibration accelerometers | Tilt gearbox + trunnion bearing housings | Acceleration (g, mm/s RMS) |
| Tilt drive torque sensor | Gearbox output shaft | Torque (kNm) |
| Bottom tuyere back-pressure | Permeable plug supply manifold | Argon/N₂ back-pressure (bar) |

### 3.2 EAF Sensors

| Sensor | Location | Measurement |
|---|---|---|
| Electrode current (current transformer) | Each phase busbar | Electrode current (kA) |
| Electrode voltage (potential transformer) | Each phase | Arc voltage (V) |
| Electrode position encoder | Each electrode mast | Electrode height (mm) |
| Electrode hydraulic pressure | Each arm cylinder | Hydraulic pressure (bar) |
| Panel cooling water ΔT (in/out per panel) | Each WCP circuit | ΔT (°C); alarm if >28°C |
| Panel cooling water flow meter | Per panel group | Flow (m³/h) |
| Panel cooling water pressure | Per panel supply | Pressure (bar); drop = leak |
| Transformer oil DGA sensor | Transformer conservator | H₂, CH₄, C₂H₂ (ppm dissolved) |
| Transformer oil temperature | Transformer top oil | Oil T (°C) |
| Roof off-gas temperature | Elbow duct | Exhaust gas T (°C) |
| Scrap bucket weight | Charging crane scale | Scrap charge (t) |
| Acoustic / vibration on busbar | HV busbar / reactor | Vibration (g) for loose connections |
| Arc harmonics analyser | Power analyser | 2nd–7th harmonic content (%) |
| Fume extraction flow | Extraction duct | Flow (m³/h) — electrode seal loss indicator |

### 3.3 Ladle Furnace Sensors

| Sensor | Location | Measurement |
|---|---|---|
| Electrode current + voltage | Per phase | Current (kA), voltage (V) |
| Electrode position | Column encoder | Height (mm) |
| Ladle shell thermocouple / IR | Ladle outer shell | Shell T (°C) — lining wear proxy |
| Argon flow meter | Bottom plug supply | Ar flow (Nl/min) |
| Argon back-pressure | Plug supply | Back-pressure (bar) — plug blockage indicator |
| Slide gate hydraulic pressure | Actuator cylinder | Pressure (bar) — sticking/seizure |
| Slide gate position sensor | Linear transducer | Gate opening % / mm |
| Steel temperature (immersion TC / pyrometer) | Bath | Steel temperature (°C) |
| Steel sample composition (OES) | Lab | Chemical composition — offline |

### 3.4 RH Degasser Sensors

| Sensor | Location | Measurement |
|---|---|---|
| Vacuum pressure transducer | Vessel top + pump header | Chamber pressure (mbar) |
| Argon lift gas flow + pressure | Up-snorkel injection | Flow (Nl/min), pressure (bar) |
| Vacuum pump steam pressure | Ejector supply | Steam pressure (bar) |
| Snorkel shell thermocouple | Snorkel outer steel casing | Shell T (°C) — lining wear |
| Off-gas O₂ / CO analyser | Vessel exhaust | O₂, CO composition (%) |
| Steel temperature (immersion TC) | Bath / sub-lance | Steel T (°C) |
| Alloy hopper load cells | Alloy vessels | Weight (kg) — confirming addition |
| Pump-down rate curve | Vacuum pressure vs time | Rate of pressure drop (mbar/min) |

---

## 4. Normal Sensor Readings

### 4.1 BOF Normal Values

| Sensor | Normal Range | Notes |
|---|---|---|
| Shell thermocouple (ambient shell) | 80–200°C | Ambient radiation + conducted heat |
| Lance cooling water outlet T | ≤60–65°C | Upper limit; [IspatGuru] |
| Lance cooling water inlet T | 20–30°C | Demineralised supply |
| Lance cooling water flow | Per design spec (maintained) | Exact value plant-specific |
| Lance cooling water pressure | ~6 kg/cm² (≈0.59 MPa) | [IspatGuru] |
| O₂ blowing flow (250 t BOF) | 58,000–66,000 Nm³/h | [IspatGuru table] |
| Off-gas CO at mid-blow | 70–85% | Healthy decarburisation |
| Bath temperature at blow end | 1,620–1,680°C | Grade-dependent |
| Trunnion bearing vibration | <2.0 mm/s RMS | Normal rotating machinery |
| Tilt drive torque | ~50–80% of rated | Load-dependent |

### 4.2 EAF Normal Values

| Sensor | Normal Range | Notes |
|---|---|---|
| Electrode current | 40–80 kA | Depends on transformer tap |
| Arc voltage | 400–900 V | Tap-dependent |
| WCP cooling water ΔT (out − in) | 8–17°C | [IspatGuru cooling system] |
| WCP flow per m² panel | 10–15 m³/h/m² | [IspatGuru] |
| WCP exit pressure | ≥0.14 MPa | Minimum [IspatGuru] |
| Transformer oil T | 40–75°C top oil | IEC limit: <105°C alarm |
| Transformer DGA H₂ | <100 ppm | IEC 60599 guideline |
| Transformer DGA C₂H₂ | <35 ppm | Arcing indicator [IEC 60599] |
| Arc harmonics deviation | <0.5% | >0.8% deviation triggers alert [ifactoryapp] |
| Electrode consumption | 1.5–2.5 kg/t steel | [bestgraphiteelectrodes.com] |

### 4.3 Ladle Furnace Normal Values

| Sensor | Normal Range | Notes |
|---|---|---|
| Electrode current (LF) | 20–35 kA | Typically 22–25 kA per phase example |
| Arc voltage (LF) | 150–300 V | ~252 V example at Gear 2 [eafccmmachine.com] |
| LF power consumption | 20–35 kWh/t steel | Average 27.5 kWh/t [eafccmmachine.com] |
| Argon stirring flow (porous plug) | 100–500 Nl/min | Process step dependent |
| Argon back-pressure | 0.5–2.5 bar | Normal unblocked plug |
| Slide gate hydraulic pressure | 120–180 bar | During open/close stroke |
| Ladle shell T (sidewall) | 150–300°C | Worn lining → rising trend |

### 4.4 RH Degasser Normal Values

| Sensor | Normal Range | Notes |
|---|---|---|
| Vacuum pressure (steady-state) | <0.5 mbar (50 Pa) | ULC steel target [oxmaint.com] |
| Pump-down time to <1 mbar | 4–8 min | Ejector system healthy |
| Treatment cycle time | 20–30 min total | [IspatGuru RH] |
| C removal time (<20 ppm) | <15 min | [IspatGuru] |
| Argon lift gas flow | 1,500–4,000 Nl/min | Recirculation ~85–135 t/min |
| Snorkel shell T (casing) | 300–600°C during treatment | Wear trend: rising baseline |
| Ejector steam pressure | 8–12 bar | Per ejector stage spec |

---

## 5. Defect Readings and Failure Thresholds

### 5.1 BOF Defect Signatures

| Failure Mode | Sensor | Normal | Alarm | Emergency / Action |
|---|---|---|---|---|
| Refractory hot spot / burnthrough risk | Shell thermocouple | 80–200°C | 350°C | 400°C — abort heat, emergency gunning [oxmaint.com alarm thresholds] |
| Refractory wear acceleration | Laser profiler wear rate | 0.5–2.0 mm/heat zone-average | >2.5 mm/heat (rolling 100 heats) | <150 mm residual thickness → reline |
| Lance cooling failure (burnout risk) | Cooling water outlet T | ≤65°C | >70°C | >80°C — withdraw lance immediately |
| Lance cooling failure | Cooling water flow | Design rate | >15% drop from baseline | Flow loss >30% → emergency withdraw |
| Lance tip burnout / nozzle erosion | O₂ flow at fixed pressure | Stable | Pressure rise for same flow | Shock wave signature in pressure trace → tip change |
| Trunnion bearing degradation | Vibration (bearing housing) | <2.0 mm/s RMS | >4.0 mm/s RMS | >7.0 mm/s — planned bearing change |
| Tilt gearbox wear | Vibration (gearbox casing) | Low harmonics | Gear mesh frequency rise | Sidebands >6 dB above noise floor → gearbox inspection |
| Bottom tuyere blockage | Argon back-pressure (tuyere) | 0.5–2.0 bar | >3.5 bar sustained | Blockage confirmed → element replacement at next reline |
| BOF shell deformation | Tilt torque anomaly | 50–80% rated | >90% rated | Asymmetric torque → vessel geometry check |

### 5.2 EAF Defect Signatures

| Failure Mode | Sensor | Normal | Alarm | Emergency / Action |
|---|---|---|---|---|
| WCP water leak (steam explosion risk) | Cooling ΔT (outlet − inlet) | 8–17°C | >25°C on any circuit | >28°C → power off immediately [IspatGuru; ELD system detects 3 L/min in <10 s] |
| WCP water leak | Flow meter (individual panel) | Stable ±5% | >10% flow loss | >20% loss → isolate panel |
| WCP micro-leak | Humidity in off-gas | Baseline | Rising H₂O in exhaust | Confirmed → power off + inspection |
| WCP acoustic leak detection | Acoustic sensor on panel | Baseline noise | >3 dB above noise floor | Confirmed leak signature [US Patent 11,913,857] |
| Electrode breakage precursor | Arc harmonics | <0.5% deviation | 0.8% harmonic deviation | [ifactoryapp data] — power ramp down, mast check |
| Electrode breakage precursor | Electrode mast hydraulic P | Stable | Pressure spike / hunting | Mechanical binding → mast inspection |
| Electrode oxidation loss | Electrode consumption calc | 1.5–2.5 kg/t | >3.5 kg/t | Cooling / current practice review |
| Electrode arm binding | Position encoder + hydraulic P | Smooth travel | Jerky movement / P spikes | Column misalignment → electrode clamp + mast check |
| Transformer incipient fault | DGA H₂ | <100 ppm | 100–300 ppm rising | >300 ppm or C₂H₂ >35 ppm → planned outage [IEC 60599] |
| Transformer insulation fault | DGA acetylene C₂H₂ | <35 ppm | >35 ppm | >100 ppm — arcing fault, emergency shutdown |
| Refractory hearth wear | Heat balance deviation | Nominal energy input | Excess heat input for same melt | Thermal model divergence → reline planning |

### 5.3 Ladle Furnace Defect Signatures

| Failure Mode | Sensor | Normal | Alarm | Emergency |
|---|---|---|---|---|
| Slide gate sticking (metal build-up) | Hydraulic pressure during stroke | 120–180 bar | >220 bar stroke peak | Gate seizure → cast abort risk |
| Slide gate leakage | Thermocouple below gate / IR | Ambient | Rising T at gate housing | Gate runout → emergency close / ladle change |
| Porous plug blockage | Argon back-pressure | <2.5 bar | >3.5 bar | >5 bar → plug blocked → install spare |
| Electrode short-circuit (slag foam) | Current spike + voltage drop | Stable arc | Sudden current surge | Overcurrent trip → raise electrode |
| Ladle lining wear | Shell thermocouple (outer) | 150–300°C | >400°C at any spot | >500°C — pull ladle from service |
| LF transformer fault | DGA + oil T | H₂ <100 ppm, T <75°C | H₂ 100–300 ppm or T >85°C | C₂H₂ >35 ppm — shutdown |

### 5.4 RH Degasser Defect Signatures

| Failure Mode | Sensor | Normal | Alarm | Emergency |
|---|---|---|---|---|
| Snorkel refractory erosion (bore widening) | Circulation rate / treatment time | 20–30 min total | Treatment time >35 min for same C spec | Extended >45 min → schedule snorkel change |
| Snorkel erosion | Snorkel shell thermocouple trend | Stable 300–600°C | Steady rising baseline over campaign | Approaching 700–800°C → urgent snorkel change |
| Vacuum pump/ejector loss | Vessel vacuum pressure | <0.5 mbar steady-state | >1 mbar sustained after pump-down | >2 mbar — ejector fault, check steam supply |
| Ejector steam supply fault | Steam pressure | 8–12 bar | <7 bar | <5 bar — vacuum unachievable → abort treatment |
| Pump-down rate degradation | Pressure-time curve slope | 4–8 min to <1 mbar | >12 min to reach <1 mbar | >15 min → ejector wear / air leak in vessel |
| Vessel refractory wear | Shell T + heat balance | Baseline | Systematic T rise in specific zone | Zone T >700°C — vessel campaign end |
| Air leak into vessel | Vacuum pressure stability | Stable once pumped | Slow pressure creep >0.2 mbar/min | >0.5 mbar/min — seal failure / snorkel gap |

---

## 6. Failure Modes — Full Detail

### 6.1 BOF Vessel / Refractory Wear and Burnthrough

**Mechanism**: Magnesia-carbon bricks erode primarily in the impact zone (where oxygen jet hits bath) and charge pad (where scrap impacts). Combined chemical dissolution by slag and thermal spalling. Wear accelerates at campaign end as protective slag layer thins.

**Earliest signs**:
1. Shell thermocouple T rising above 250°C in a localised zone — earliest detectable precursor
2. Laser scan showing residual <400 mm in impact zone (warning) or <250 mm (critical)
3. Rolling-average wear rate acceleration: >2.5 mm/heat in any zone over last 100 heats
4. Visible red/orange glow on shell exterior (visual IR patrol) — late stage, very dangerous

**Risk**: Burnthrough releases 100–300 t of molten steel + slag at ~1,650°C; catastrophic safety event, facility damage, multiple-week outage.

### 6.2 BOF Lance Burnout / Cooling Failure

**Mechanism**: Copper lance tip exposed to >2,000°C bath radiation. Cooling water circuit removes heat; if flow drops (valve failure, deposit blockage, hose rupture), tip melts within seconds. Thermal fatigue cracking of nozzle copper is also common — progressive over 100–400 heat campaigns.

**Earliest signs**:
1. Cooling water outlet temperature rising toward 70°C (normal ≤65°C)
2. Delta-T (outlet − inlet) narrowing suddenly — possible flow restriction
3. Oxygen pressure spike at constant flow — nozzle geometry change (erosion/deposition)
4. Off-gas CO₂/CO ratio anomaly — post-combustion change inside nozzle

**Consequences**: Lance burnout mid-blow forces emergency withdrawal, heat abort; replacement takes 20–30 min; lance tips cost ~$3,000–8,000 each [unverified exact figure; vendor range].

### 6.3 BOF Trunnion Bearing / Tilt Drive Failure

**Mechanism**: Trunnion bearings carry the full vessel weight (vessel + lining + charge = 500–1,500 t) plus dynamic loads from blowing vibration. Gear cogs in tilt gearbox wear from repeated shock loads. Lubricant degradation under high temperatures.

**Earliest signs**:
1. Vibration spectrum — emergence of bearing defect frequencies (BPFO, BPFI) above noise floor
2. Tilt torque asymmetry — left vs right drive torque imbalance >10%
3. Tilt time increasing for same angle (gearbox drag)
4. Oil sample metal particle count rising

**Consequence**: Trunnion bearing failure → vessel tilt loss → stranded heat; catastrophic bearing failure could result in uncontrolled vessel tip; multi-week repair.

### 6.4 EAF Water-Cooled Panel Leak (Steam Explosion Risk)

**Mechanism**: Thermomechanical fatigue from cycles of heating/cooling (1,800°C interior vs 20–30°C inlet water) causes tube cracking. Scrap impact during charging cracks exposed tubes. Even a 3 L/min leak entering EAF can cause steam flash explosion when water contacts molten slag/steel.

**Earliest signs**:
1. Individual panel outlet temperature rises — 2°C shift detectable with modern IoT [ifactoryapp ELD data]
2. Individual panel flow loss >10%
3. Humidity spike in off-gas analyser
4. Acoustic signature: broadband noise increase on panel acoustic sensor
5. Visual steam wisps from furnace during meltdown phase

**Consequence**: Steam explosion in 100–300 t EAF is a potentially fatal event; panel replacement 4–8 h; refractory damage adds 1–3 days.

### 6.5 EAF Electrode Breakage

**Mechanism**: Graphite nipple joint failure (thermal differential); scrap cave-in impact; arc instability causing excessive mechanical load on column; misalignment of electrode arm. Breakage drops column into molten bath.

**Earliest signs**:
1. Arc harmonic deviation >0.8% — precursor vibration in graphite column [ifactoryapp]
2. Electrode mast hydraulic pressure hunting — mechanical binding
3. Position encoder jitter — column oscillation
4. Increasing current oscillation on one phase at constant power set-point

**Consequence**: Electrode breakage stops heat for 2–4 h minimum; refractory damage risk if arc wanders; electrode column costs $1,500–4,000/segment [unverified; market price range].

### 6.6 EAF Transformer Fault

**Mechanism**: EAF transformers (40–200 MVA) operate under extreme duty cycles — continuous variable load, harmonics, short-circuit events. Winding insulation degrades; hot-spot overheating; bushing partial discharge.

**Earliest signs (DGA)**:
1. H₂ rising from <100 ppm baseline (partial discharge / thermal)
2. C₂H₂ >35 ppm — high-energy arcing in oil
3. CO rising — cellulose insulation overheating
4. Oil top temperature >85°C sustained

**Consequence**: Transformer failure → months-long outage; replacement transformers cost $5–20 M [unverified]; rentals are rare for EAF-specific units. Case study: 130 MVA EAF transformer at steel plant monitored by Morgan Schaffer Calisto R9 online DGA [MDPI Applied Sciences 2025 case study].

### 6.7 Ladle Slide Gate Sticking / Runout

**Mechanism — sticking**: Metal/skull build-up on refractory plate surfaces; thermal distortion of housing; actuator seal wear. Gate cannot open → cast abort, heat lost.

**Mechanism — runout**: Refractory plate cracking from thermal shock; worn bore through repeated heats; misalignment. Gate cannot close → uncontrolled steel flow, ladle runout, safety event.

**Earliest signs (sticking)**:
1. Hydraulic pressure stroke peak increasing heat-over-heat (120 bar → 180 bar → >200 bar)
2. Gate position feedback not reaching full-open position
3. Argon purge pressure test anomaly during ladle preparation

**Earliest signs (runout)**:
1. IR camera showing hot spot at gate housing between heats
2. Plate surface condition assessment (visual + ultrasonic on plate body — offline)

**Consequence**: Cast abort costs one heat + casting sequence disruption (≥30 min delay). Runout: major safety risk + ladle rebuild.

### 6.8 RH Snorkel Erosion and Campaign End

**Mechanism**: Inner bore of snorkel erodes from steel circulation turbulence + slag chemical attack. As bore enlarges, circulation rate decreases — CFD confirms that increasing Ar flow to compensate accelerates upper snorkel erosion [RHI Magnesita paper].

**Earliest signs**:
1. Treatment time creeping upward for identical C-spec heats (most reliable operational signal)
2. Snorkel shell thermocouple trend rising (bore thinning reduces insulation)
3. Pump-down achieving target vacuum but decarburisation rate slower than model

**Consequence**: Snorkel set replacement: 60–300 heat intervals. Each replacement is a 4–8 h maintenance stop (snorkel change + gunning + preheat). Failure to replace in time → substandard C removal → grade downgrade.

### 6.9 RH Vacuum System Failure

**Mechanism**: Steam ejector nozzle erosion from high-velocity steam; steam supply pressure fluctuation (boiler instability); inter-condenser fouling; air ingress through vessel flanges or snorkel gap.

**Earliest signs**:
1. Pump-down time elongating (4–8 min → >12 min)
2. Steady-state vacuum not achieving <0.5 mbar; stabilises at 1–3 mbar
3. Pressure creep (>0.2 mbar/min) after reaching target — air leak
4. Steam supply pressure dropping below 7 bar

**Consequence**: Inability to degas steel → ULC grades unproducible → significant downgrade; production halt.

---

## 7. Repair and Resolution Processes

### 7.1 BOF Refractory Reline

| Step | Duration | Description |
|---|---|---|
| Vessel cool-down | 12–24 h | Forced air/water mist; must reach <150°C for personnel entry |
| Old lining demolition | 24–36 h | Excavators + pneumatic breakers; remove old MgO-C bricks |
| Permanent lining inspection + patch | 4–8 h | Inspect safety lining; patch cracks with castable |
| New working lining installation | 24–48 h | Manual + mechanical brick laying; zone by zone |
| Dry-out + heat-up | 12–24 h | Gas burner pre-heat sequence to 1,200°C |
| Trial heats (break-in) | 1–2 days | First 200–500 heats at reduced intensity |
| **Total planned reline downtime** | **5–10 days** | [oxmaint.com data] |
| Unplanned (emergency) reline | 5–18 days | Includes repair of shell damage, additional structural work |
| Gunning repair (mid-campaign) | 2–8 h | Hot gunning of worn zones; interval every 300–800 heats |

### 7.2 BOF Lance Change

- Routine lance change: 20–30 min (quick-change hoist system)
- Planned: every 200 heats average (range 100–400 heats) [IspatGuru]
- Emergency burnout change: same time but forces heat abort if mid-blow

### 7.3 Trunnion Bearing Change

- Planned (at reline): 3–5 days concurrent with vessel reline
- Unplanned bearing failure: 7–14 days (requires special lifting gear + precision alignment)

### 7.4 EAF Panel Replacement

- Individual panel: 4–8 h (requires furnace cool-down to safe access, panel cut + weld replacement)
- Full upper shell re-panel: 3–5 days
- Emergency mid-heat leak: heat abort + cool-down + minimum 6 h

### 7.5 EAF Electrode Addition

- Normal column addition (new segment screwed on): 5–10 min per column; done during furnace hold
- Electrode breakage recovery: 2–4 h (remove fragments from bath, assess refractory damage, restart)

### 7.6 Ladle Slide Gate Change

- Planned gate change between heats: 15–45 min (cold gate swap at ladle preparation bay)
- Tap hole block replacement (BOF): 30–90 min [oxmaint.com]

### 7.7 RH Snorkel Change

- Planned snorkel set change: 4–8 h (snorkel lower body removal, new lower body positioning, preheat)
- Includes gunning repair of vessel hot face

### 7.8 RH Full Vessel Reline

- Planned: 7–14 days (upper + lower vessel + new snorkels)
- Triggered when vessel shell thermocouple zones approach 700–800°C campaign-end

---

## 8. Cost and Loss Impact

### 8.1 BOF

| Event | Cost / Impact |
|---|---|
| Planned reline (materials + labour) | $2–5 M per reline [oxmaint.com] |
| Burnthrough event (emergency reline + shell repair) | $5–20 M [oxmaint.com] |
| Production loss per unplanned day | $1.5–4 M/day [oxmaint.com] |
| Each extended campaign (500 heats) | Defers $8–15 M reline + adds $2–6 M production value |
| Lost value per aborted heat | $300–600 [oxmaint.com] |
| Annual unplanned downtime cost (industry-wide 2024) | $4.2 B across steel industry [oxmaint.com] |

At Tata Steel India scale (Jamshedpur: ~9 Mtpa capacity), BOF converter unplanned outage of even 3 days = ~73,000 t steel lost at $600/t crude steel = ~$44 M lost production [unverified extrapolation — cited for order-of-magnitude context only].

### 8.2 EAF

| Event | Cost / Impact |
|---|---|
| Panel leak → steam explosion downtime | 1–3 days + safety investigation; $0.5–3 M |
| Electrode breakage downtime cost | ~$15,000/h EAF downtime [oxmaint.com EAF vs BOF article] |
| Electrode cost per breakage event | $3,000–8,000 electrode segment + $30,000–50,000 refractory repair if arc wanders [unverified typical range] |
| Transformer failure | $5–20 M replacement + months outage [unverified] |
| Electrode consumption saving (1 kg/t reduction on 1 Mt/a plant) | ~$60–150/t × 1 Mt = $60–150 M/a [at $60–150/kg electrode price range] [unverified; indicative] |

### 8.3 Ladle / Secondary Metallurgy

| Event | Cost / Impact |
|---|---|
| Cast abort from slide gate seizure | One heat loss (~300–600 t steel) + sequence delay ≥30 min |
| Ladle lining runout | Safety event + ladle rebuild $50,000–200,000 [unverified] |
| RH treatment failure (grade downgrade ULC → LC) | Price differential $50–200/t; on 300 t heat = $15,000–60,000 per heat [unverified indicative] |
| RH snorkel early failure (unplanned change) | 6–12 h unplanned downtime; secondary metallurgy bottleneck |

---

## 9. Additional Notes for PdM System Design

### 9.1 Multi-sensor Fusion Is Mandatory

No single sensor is sufficient for high-confidence failure prediction in any of these assets:
- BOF refractory: laser scan (periodic) + shell TC (continuous) + wear-rate model (computed) must fuse
- EAF panel leak: ΔT alone has too much noise; flow + humidity + acoustic must be combined; earliest detection requires per-panel individual circuit monitoring (not aggregate header)
- RH snorkel: direct measurement impossible mid-heat; proxy signals (treatment time, shell TC trend, vacuum stability) form the evidence chain

### 9.2 Sampling Frequency Requirements

| Asset | Critical signals | Required Hz |
|---|---|---|
| EAF electrode regulation | Current, voltage, position | 200 Hz (arc stability) |
| EAF panel ΔT (leak detection) | Temperature | 1–10 Hz (thermal lag limits faster) |
| BOF lance position | Encoder | 10 Hz |
| BOF shell TC | Temperature | 0.1 Hz (slow thermal) |
| Trunnion/gearbox vibration | Acceleration | ≥1,000 Hz for bearing defect frequencies |
| RH vacuum pressure | Pressure | 1–10 Hz |

### 9.3 Safety-Critical Constraints for ML Models

- BOF shell TC >400°C: **hard stop** — no model should override this; must be interlocked at SCADA level independent of PdM system
- EAF panel ΔT >28°C: **hard interlock** — power off; PdM model is supplementary early warning only
- Slide gate hydraulic pressure limit: **hard stop** — never extrapolate past mechanical limit
- RH vacuum: process quality constraint, not immediate safety; model can advise but not auto-stop

### 9.4 Digital Twin Opportunities

- BOF: Physics-informed wear model (slag chemistry + blow practice → zone-specific wear rate) calibrated by laser scan; closes scan interval with continuous prediction
- EAF: Thermal model of WCP using inlet flow + ambient + power input predicts expected ΔT; deviation from thermal model is a cleaner leak signal than raw ΔT threshold
- RH: CFD-derived circulation rate as function of snorkel bore diameter → bore erosion estimator feeding remaining life

### 9.5 Key Public References

1. IspatGuru — "Oxygen Blowing Lance and Lance Tips in Converter Steelmaking": https://www.ispatguru.com/oxygen-blowing-lance-and-lance-tips-in-converter-steel-making/
2. IspatGuru — "Electric Arc Furnace Cooling System": https://www.ispatguru.com/electric-arc-furnace-cooling-system/
3. IspatGuru — "RH Vacuum Degassing Technology": https://www.ispatguru.com/rh-vacuum-degassing-technology/
4. RHI Magnesita — "Refractory Condition Monitoring and Lifetime Prognosis for RH Degasser": https://www.rhimagnesita.com/wp-content/uploads/2019/05/210-40911-084.pdf
5. CSEM (Yoda) — "Ladle Slide Gate Health Monitoring for Steel Industry": https://yoda.csem.ch/items/09b79c14-fff2-48c5-9f16-139a03944534/full
6. Springer MMTB — "Vibration and Audio Measurements in the Monitoring of BOF Steelmaking": https://link.springer.com/article/10.1007/s11663-023-02859-5
7. ResearchGate — "Monitoring and Diagnosis of Health State of Converter Tilting Trunnion Bearing Based on Stress Wave Analysis": https://www.researchgate.net/publication/358317878
8. ResearchGate — "Earliest Leak Detection (ELD) — New Concept of Security in Water Leak Detection in EAFs": https://www.researchgate.net/publication/318949593
9. SMS Group — "Replacement of BOF Converter Tilting Drives at Trinecke Zelezarny": https://www.sms-group.com/insights/all-insights/replacement-of-bof-converter-tilting-drives-at-trinecke-zelezarny
10. MDPI Applied Sciences 2025 — "Assessment of Transformer Fault Severity from Online DGA": https://www.mdpi.com/2076-3417/15/11/6357
11. Oxmaint — BOF/EAF maintenance data: https://oxmaint.com/industries/steel-plant/bof-converter-maintenance-vessel-lining-management
12. Envista Forensics — Steam explosion mechanisms: https://www.envistaforensics.com/knowledge-center/insights/articles/preventing-catastrophe-understanding-steam-explosions-in-molten-material-environments/

---

*[unverified] tag applied where no public primary source was found; values are industry-typical estimates from operational literature.*
