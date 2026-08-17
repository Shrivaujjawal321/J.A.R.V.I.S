# Integrated Steel Plant — End-to-End Process Map
## Tata Steel Scale | Equipment, Sensors, Operating Conditions, Maintenance Criticality
**Authored by:** Tata-Steel Process Optimization subagent  
**Date:** 2026-06-08  
**Purpose:** Data-quality platform domain model — zero blind spots on where equipment and sensors live  
**Sources:** World Steel Association process guides; Tata Steel Annual Reports 2022–2024; POSCO AI blast-furnace papers (Park et al. 2020); ISO 14224:2016 (FMEA taxonomy for process industries); ABB / Siemens steel automation whitepapers; Worldsteel CO2 data 2023; SMS Group / Primetals equipment specs [unverified where noted]

---

## STAGE 0 — RAW MATERIAL HANDLING

### Equipment
| Machine | Function | Operating Conditions | Criticality |
|---|---|---|---|
| Ship/truck unloaders | Unload iron ore, coking coal, limestone | Capacity 2,000–8,000 t/h; outdoor, corrosive dust | Medium |
| Stacker-reclaimer | Stack and reclaim ore/coal stockpiles | Boom travel 0–120 m; bucket-wheel 500–3,000 t/h | **HIGH** — single point; breakdown halts BF feed |
| Belt conveyors (main lines) | Transport ore/coal/coke 2–15 km across plant | Speed 1–6 m/s; tension 50–500 kN; 24/7 | **HIGH** — idler failures cause belt fires |
| Belt weighers / samplers | Continuous mass-flow measurement | — | Medium |
| Magnetic separators | Remove tramp iron before crushers | — | Low |
| Crushers (primary/secondary) | Size reduction of ore and coal | 100–1,000 rpm; motor 200–2,000 kW | Medium–High |
| Dust extraction fans | Ventilation + fugitive dust control | 20,000–100,000 m³/h | Medium |

### Critical Sensors
- Belt speed + tension (load cells)
- Bucket-wheel current draw (motor amps → overload / blockage)
- Moisture analyzers on coal (NIR) — feed quality signal for coke ovens
- Stockpile level (LIDAR / drone survey)

### Maintenance-Critical Equipment
**Stacker-reclaimers** and **main belt conveyors** dominate downtime. Conveyor idler bearing failure is the highest-frequency fault in raw material handling [ISO 14224 taxonomy; Tata Steel IJmuiden maintenance KPIs, public 2022 report].

---

## STAGE 1 — COKE OVENS

### Process
Coal is heated at 1,000–1,100 °C for 16–24 hours in sealed silica-brick ovens, driving off volatile matter to produce metallurgical coke for the blast furnace.

### Equipment
| Machine | Function | Operating Conditions | Criticality |
|---|---|---|---|
| Coke oven battery (60–80 ovens/battery) | Carbonisation chambers | Wall temp 1,000–1,350 °C; charge cycle 18–24 h | **HIGHEST** — battery is decades-long asset; single cracked wall = full battery stoppage |
| Coal charging cars | Charge coal from top | — | High — mechanical + seal failure = gas leak |
| Pushing machines | Push hot coke out | Peak force 200–400 kN | High |
| Quench cars / dry quenching (CDQ) | Cool hot coke to < 200 °C | Wet: water spray; Dry: 800 °C → 200 °C via nitrogen cycle | **HIGH** — CDQ heat recovery boiler; steam drum failure |
| Coke wharf + conveyor | Transfer cooled coke to BF | — | Medium |
| Underfiring system (gas burners) | Heat oven walls | BFG / COG mixture; flow control valves | High |
| By-product plant (tar, benzene, ammonia recovery) | Treat coke oven gas (COG) | Condensers, scrubbers, compressors; corrosive service | High |
| Oven door seals | Prevent gas escape | Thermal cycling, warping | Medium–High |

### Critical Sensors
- Oven wall temperature (thermocouple arrays, pyrometers)
- COG pressure and composition (H₂, CO, CH₄)
- Stack CO / NOₓ / SO₂ (regulatory)
- Hydraulic pressure on pushing machine
- CDQ steam flow and temperature

### Maintenance-Critical Equipment
**Oven wall refractory** is the single highest-consequence failure (multi-year rebuild). **CDQ boilers** and **underfiring valves** have highest unplanned downtime frequency. Seal leaks are high-frequency but lower consequence [SMS Group coke plant maintenance guide, [unverified exact figures]].

---

## STAGE 2 — SINTER PLANT

### Process
Fine iron ore, recycled dust, and limestone are blended and fired on a moving grate (strand) at 1,200–1,300 °C to produce porous sinter lumps — the primary BF feed.

### Equipment
| Machine | Function | Operating Conditions | Criticality |
|---|---|---|---|
| Mixing drums | Blend ore fines, coke breeze, limestone, return fines | Rotary, 5–15 rpm | Medium |
| Sinter strand (pallet cars on moving grate) | Combustion bed; sinter formation | Bed temp 1,200–1,350 °C; strand speed 1.5–4 m/min | **HIGHEST** — strand downtime = BF feed stoppage |
| Ignition furnace | Surface ignite coke breeze layer | Burner temp 1,200 °C; COG/BFG | High |
| Wind boxes + exhaust fans (main draft) | Draw combustion air through bed | Fan motor 5–20 MW; 24/7 continuous | **HIGH** — fan trip = strand stop |
| Sinter breaker / cooler | Break and cool sinter to < 150 °C | Rotary or linear coolers | High |
| ESP (electrostatic precipitators) | Dust capture from exhaust gas | HV power supply, collecting plates | Medium (regulatory compliance) |
| Return fines screens | Separate undersized sinter for recycle | — | Medium |

### Critical Sensors
- Burn-through point detection (thermocouples in windboxes — peak temperature travel along strand)
- Strand speed
- Exhaust gas temperature and CO
- Fan current / vibration
- Bed height

### Maintenance-Critical Equipment
**Main draft fans** (high-speed, high-power; bearing and impeller erosion) and **sinter strand pallet cars** (thermal fatigue, grate bar breakage) carry highest downtime cost. Fan bearing failure triggers complete strand stop.

---

## STAGE 3 — PELLET PLANT (where present)

### Process
Ultra-fine iron ore concentrate is balled into 8–16 mm green pellets, then hardened in a grate-kiln or shaft furnace at 1,200–1,350 °C. Used as BF or DRI feed. Not all Tata Steel sites have pellet plants [Tata Steel Kalinganagar has pellet plant capacity; IJmuiden does not — uses sinter + lump ore].

### Equipment
| Machine | Function | Operating Conditions | Criticality |
|---|---|---|---|
| Balling discs / drums | Form green pellets | Disc angle 45–50°; moisture control critical | High |
| Travelling grate | Dry and pre-heat pellets | 400–1,000 °C zones | High |
| Rotary kiln | Harden pellets | 1,200–1,350 °C; refractory lining | **HIGH** — kiln shell deformation, refractory wear |
| Annular cooler | Cool pellets | 1,300 → 120 °C | Medium |
| Indurating fans | Provide combustion air | High-power fans | High |

### Maintenance-Critical Equipment
**Rotary kiln refractory** and **balling disc drive systems** [unverified exact MTBF figures].

---

## STAGE 4 — BLAST FURNACE (BF)

### Process
The blast furnace is a counter-current reactor, 25–35 m tall, 12–14 m hearth diameter at Tata Steel scale (IJmuiden BF7: ~10,000 tHM/day). Coke, sinter/pellets, and limestone descend; hot blast (1,100–1,250 °C) + oxygen + pulverised coal injection (PCI) combust, reducing iron oxides to liquid hot metal (HM) at ~1,480–1,520 °C.

### Equipment Detail

#### 4A — Hot Stoves (Cowper Stoves)
| Machine | Function | Operating Conditions | Criticality |
|---|---|---|---|
| Cowper stoves (3–4 per BF) | Preheat blast air to 1,100–1,250 °C by cycling heat absorption / blast heating | Dome temp 1,350–1,450 °C; BFG combustion; 20–30 min cycle | **HIGHEST** — stove shell crack or checker brick collapse = BF shutdown |
| Combustion air blowers | Force air through stoves | 300,000–600,000 Nm³/h; 50,000–100,000 kW motors | **HIGH** — single largest electrical consumer on plant |
| Stove valves (on-gas / off-gas / blast valves) | Cycle stoves between on-gas and on-blast | High temp, high pressure; thermal cycling | High — valve seat erosion |

**Sensors:** dome temperature (Type-R thermocouple), cold/hot blast pressure, stove gas composition, wall temperature profile.

#### 4B — Charging System
| Machine | Function | Operating Conditions | Criticality |
|---|---|---|---|
| Skip hoists or conveyor charging | Transport burden (coke + ore) to top | Skip: 25–35 m lift; 200–400 t/h | High |
| Bell-less top (Paul Wurth type) / rotating chute | Distribute burden in controlled rings | Top pressure 2–4 bar; dusty, abrasive | **HIGH** — burden distribution drives gas flow; maldistribution = scaffold/hanging |
| Top gas pressure control valve | Maintain top pressure | 2–4 bar; erosive BFG with dust | High |

**Sensors:** radar + nuclear level gauges in hoppers, chute position encoder, top gas temperature and pressure.

#### 4C — Tuyere Zone / Raceway
| Machine | Function | Operating Conditions | Criticality |
|---|---|---|---|
| Tuyeres (20–40 per BF) | Inject hot blast + PCI coal into raceway | Tuyere tip temp 2,000–2,200 °C; water-cooled copper | **HIGH** — tuyere burnout stops BF immediately; ~10% annual failure rate [unverified exact %, typical industry figure] |
| Blowpipes + bustle pipe | Distribute blast to tuyeres | 1,100 °C gas; 3–4 bar | High |
| PCI lances | Inject pulverised coal (150–200 kg/tHM) | 150 µm coal + carrier gas | Medium–High |
| Tuyere coolers | Water cooling of tuyere bodies | Δ cool 40–70 °C; flow monitored | High — water leak = explosion risk |

**Sensors:** tuyere gas infrared cameras (raceway monitoring), individual tuyere cooling water flow + temperature, blast temperature post-stove, oxygen injection flow.

#### 4D — Hearth / Taphole
| Machine | Function | Operating Conditions | Criticality |
|---|---|---|---|
| Taphole (2–4 per BF, alternating) | Drain hot metal and slag | HM at 1,480–1,520 °C; slag at 1,430–1,480 °C | **HIGHEST** — taphole erosion or breakout = fatality risk + multi-day shutdown |
| Mud gun | Plug taphole with refractory clay | Hydraulic, 100–300 bar | High |
| Drill | Open taphole | Rotary + percussive | High |
| Torpedo ladles / hot metal ladles | Transport HM to steelmaking | 1,300 t capacity; temp loss ~ 3°C/min | High |

**Sensors:** taphole thermocouple, torpedo ladle temperature, slag composition (X-ray fluorescence at cast house), acoustic emission on hearth walls.

#### 4E — Gas Cleaning Plant (GCP)
| Machine | Function | Operating Conditions | Criticality |
|---|---|---|---|
| Dust catcher (gravity) | Remove coarse dust from BFG | — | Medium |
| Venturi scrubber / bag filter | Clean BFG to < 5 mg/Nm³ dust | High-flow; corrosive gas | High |
| Top-gas pressure recovery turbine (TRT) | Recover energy from BFG pressure | 2–4 bar → ~20 MW per BF | High (energy recovery) |

**BF Summary — Maintenance-Critical Equipment (ranked):**
1. Taphole assembly (highest safety + downtime cost)
2. Tuyeres (highest failure frequency)
3. Hot stove shells + checker bricks (highest consequence per event)
4. Main blast blower (highest power; bearing failure = BF stop)
5. Bell-less top chute drive (maldistribution causes costly scaffold events)

---

## STAGE 5 — DRI / EAF ROUTE (alternative to BF, or hybrid)

### Direct Reduction (DRI) — MIDREX / HYL
| Machine | Function | Operating Conditions | Criticality |
|---|---|---|---|
| Reformer furnace | Reform natural gas to H₂ + CO reductant | 900–1,000 °C; Ni catalyst tubes | **HIGH** — tube failure |
| Shaft furnace | Reduce pellets with syngas | 800–950 °C; 4–8 bar | High |
| Cooling gas compressors | Circulate cooling gas | Large centrifugal compressors | High |

### Electric Arc Furnace (EAF)
| Machine | Function | Operating Conditions | Criticality |
|---|---|---|---|
| EAF shell + roof | Contain melt | 1,550–1,650 °C; arc plasma | **HIGH** — shell cooling leak = catastrophic |
| Graphite electrodes (3 per heat) | Conduct 100–150 kA at 600–900 V | Consumption 1.5–2.5 kg/t steel; breakage risk | **HIGH** — electrode breakage = heat loss, production stop |
| Transformer | Step down HV to furnace voltage | 100–200 MVA; oil-cooled | **HIGH** — transformer failure = multi-day outage |
| Water-cooled panels (sidewalls + roof) | Protect EAF shell | Delta temp 20–40 °C; continuous flow | High — leak → steam explosion risk |
| Tapping spout | Drain steel to ladle | — | Medium |
| Fume extraction system | Capture off-gas + dust | ~600,000 Nm³/h per EAF | Medium (regulatory) |

**Sensors:** electrode position + current + voltage (arc stability), water-cooling flow + temperature differentials per panel, off-gas O₂ / CO / CO₂ (dynamic control), tap temperature (IR pyrometer).

---

## STAGE 6 — BOF / LD CONVERTER (primary steelmaking)

### Process
~300 t of hot metal + ~100 t scrap charged to vessel. Oxygen blown at supersonic speed (Mach 2) via lance for 15–18 minutes. Carbon oxidised from 4.5% → 0.03–0.05%. Slag forms on molten bath. Temperature target 1,620–1,680 °C; carbon target ±0.01%.

### Equipment
| Machine | Function | Operating Conditions | Criticality |
|---|---|---|---|
| BOF vessel (converter) | Primary oxidation vessel | 1,600–1,750 °C; trunnion tilts ±360° | **HIGHEST** — vessel lining wear: 3,000–6,000 heats before relining (2–3 day outage) [World Steel Assoc. 2022] |
| Oxygen lance | Supersonic O₂ injection | Mach 2; lance tip 2,000 °C+; water-cooled | **HIGH** — lance burnout mid-blow; 1–2% heat impact |
| Off-gas hood + OG system | Capture CO-rich converter gas; suppress explosion | CO 60–80%; gas recovery or combustion | High |
| Scrap cranes + charging | Load scrap and hot metal | 300 t ladles; overhead crane | High |
| Sublance / sensors | In-blow C + T measurement | Dip probe at 1,700 °C | High (process quality) |
| Torpedo ladle desulphurisation station | Pre-treat HM: S < 0.002% | Magnesium/lime injection | Medium |
| Slag pot + handling | Receive and transport slag | 1,400–1,500 °C | Medium |

**Sensors:** lance position (encoder), off-gas flow + composition, sublance C/T readout, vessel lining thickness (laser profiling), converter tilt angle.

**Maintenance-Critical:**
1. Vessel refractory lining — highest total downtime cost (planned but costly)
2. Oxygen lance — high failure frequency during blow
3. Off-gas system valves and waste-gas fans

---

## STAGE 7 — SECONDARY METALLURGY / LADLE FURNACE (LF) / VACUUM DEGASSING

### Process
After BOF/EAF tap, liquid steel is refined in ladle to hit exact chemistry and temperature targets before casting. Key operations: temperature homogenisation, alloy addition, desulphurisation, degassing.

### Equipment
| Machine | Function | Operating Conditions | Criticality |
|---|---|---|---|
| Ladle furnace (LF) | Arc reheat + stir; precise alloy trim | 1,560–1,650 °C; graphite electrodes 10–30 MVA | **HIGH** — electrode breakage; ladle shell leak |
| RH vacuum degasser | Remove H₂, N₂, C under < 1 mbar | 150–200 t/heat; snorkel immersed in steel | **HIGH** — snorkel erosion; vacuum pump failure |
| VOD / AOD (stainless) | Argon-oxygen decarburisation | Extreme oxidation + thermal cycle | High |
| Ladle (steel vessel) | Transport and hold liquid steel | 1,550–1,650 °C; 300–350 t | **HIGH** — ladle breakout = catastrophic |
| Ladle slide gate | Control steel flow to caster | Hydraulic; refractory plates | High — sticking/wear mid-cast |
| Argon stirring system (plugs) | Homogenise steel temperature and chemistry | Bottom-blown argon; plug erosion | Medium–High |
| Alloy addition system | Weigh and add ferro-alloys | Precision ±0.5 kg | Medium |

**Sensors:** ladle temperature (thermocouple + pyrometer), electrode current/voltage, vacuum gauge (RH), argon flow rate, alloy weight cells, ladle weight (load cells on transfer car).

---

## STAGE 8 — CONTINUOUS CASTING (CONCAST)

### Process
Liquid steel (1,550–1,600 °C) is poured from ladle → tundish → water-cooled copper mould → solidifying strand pulled at 0.8–2.5 m/min through 100+ guided rolls and spray-cooled zones. Products: slabs (hot strip mill feed), blooms, billets.

### Equipment Detail

#### 8A — Tundish
| Machine | Function | Operating Conditions | Criticality |
|---|---|---|---|
| Tundish (2–6 t refractory vessel) | Buffer reservoir; controls flow to multiple strands | 1,520–1,580 °C; turbostop, weirs | **HIGH** — tundish skull buildup → nozzle clog → casting stop |
| Submerged entry nozzle (SEN) | Inject steel below mould slag layer | 1,520 °C; Al₂O₃ buildup (clogging) | **HIGHEST** — SEN clog is #1 unplanned caster stop [Primetals case studies] |
| Stopper rod / slide gate | Control tundish → mould flow | Refractory; thermal shock cycling | High |
| Tundish car | Position tundish above mould | Driven alignment ±0.5 mm | Medium |

#### 8B — Mould
| Machine | Function | Operating Conditions | Criticality |
|---|---|---|---|
| Copper mould (slab: 900–2,100 mm wide) | Initial shell formation | 1,520 °C steel; water-cooled; 300–1,500 l/min | **HIGHEST** — mould level instability → breakout = ladle of steel on floor |
| Mould oscillator | Oscillate mould to prevent sticking | Frequency 50–300 cpm; stroke 3–10 mm; hydraulic or electromechanical | **HIGH** — oscillator failure mid-cast |
| Mould electromagnetic stirrer (M-EMS) | Stir molten core for equiaxed grain | 50 Hz; 300–600 A coils | Medium |
| Mould powder feeder | Lubricate mould-strand interface | Continuous feed; powder consumption 0.3–0.6 kg/t | Medium |

**Sensors:** mould level (electromagnetic induction or radar ± 1 mm), mould temperature array (thermocouples in copper, 40–80 points), cooling water flow + temperature per mould face, oscillation stroke (LVDT), SEN temperature.

**Breakout Prediction** is the highest-value ML application here: mould thermocouple array anomalies (asymmetric temperature patterns) predict shell freeze or sticking 30–60 seconds before breakout [SMS Group MOLD EXPERT, [unverified response time figure — vendor claim]).

#### 8C — Strand Guide (Segments)
| Machine | Function | Operating Conditions | Criticality |
|---|---|---|---|
| Foot rolls (segment 0) | Support strand immediately below mould | 1,400–1,500 °C surface; water spray | High |
| Drive/containment segments (1–20+) | Guide strand through arc; apply soft reduction | Roll load 50–200 kN/roll; thermal cycling; water spray | **HIGH** — roll bearing failure causes strand deviation → slab shape defects |
| Segment rolls (100–400 total) | Contain bulging, drive strand | 800–1,200 °C contact; misalignment → internal cracks | High |
| Secondary cooling spray headers | Zone-by-zone water cooling | Zone flows 200–2,000 l/min each; nozzle plugging | **HIGH** — blocked spray nozzles → uneven cooling → cracks |
| Pinch rolls + straightener | Straighten curved strand to horizontal | Motor load monitors | High |

**Sensors:** roll gap (hydraulic position sensors), segment coolant flow per zone, strand surface temperature (IR pyrometers at multiple points), roller speed (encoders), strand shell thickness (gamma-ray gauges [unverified deployment at all sites]).

#### 8D — Cutting and Downstream
| Machine | Function | Operating Conditions | Criticality |
|---|---|---|---|
| Torch cutters / shear | Cut strand to slab length | Gas torch or hydraulic shear | Medium |
| Slab transfer table + roller table | Move slabs to scarfing / reheating | — | Medium |
| Scarfing machine | Remove surface defects from slabs | Oxygen-gas torch | Medium |

**Caster Summary — Maintenance-Critical Equipment (ranked):**
1. SEN (highest frequency unplanned stop)
2. Mould copper plates (wear, crack → emergency replacement)
3. Segment rolls / bearings (high replacement frequency, affects quality)
4. Spray cooling nozzles (plugging; quality impact)
5. Mould oscillator (mechanical failure → breakout risk)

---

## STAGE 9 — REHEATING FURNACE (Hot Strip Mill / Plate Mill Entry)

### Process
Slabs (20–250 mm thick, up to 15 m long, 900–1,400 °C target discharge) are pushed or walked through gas-fired furnaces to achieve uniform temperature for rolling.

### Equipment
| Machine | Function | Operating Conditions | Criticality |
|---|---|---|---|
| Walking beam furnace | Convey slabs through heating zones | Burner temp 1,300–1,350 °C; slab surface target 1,150–1,250 °C | **HIGH** — beam mechanism failure = furnace stop |
| Radiant tube / direct-fired burners | Provide heat per zone (preheat, heating, soaking) | BFG/NG/COG mix; 100–300 burners | High |
| Combustion air fans | Supply air to burners | 20,000–80,000 Nm³/h | High |
| Descaler (high-pressure water) | Remove scale before rolling | 150–250 bar; 1,200–1,280 °C slab | Medium |
| Slab pusher / extractor | Move slabs in and out | Hydraulic; position control | Medium |

**Sensors:** zone temperatures (thermocouples, 20–50 per furnace), slab surface temperature (radiation pyrometers at discharge), fuel flow per zone, O₂ / CO in flue gas (combustion efficiency), walking beam position.

**Maintenance-Critical:** Walking beam lifting/traversing mechanism and **regenerative burner systems** (high fouling frequency [unverified]).

---

## STAGE 10 — HOT STRIP MILL (HSM)

### Process
Slabs (220–250 mm thick) are reduced to coils (1.2–25 mm) through roughing mill (5–6 passes, 4-hi reversing) then 6–7 finishing stands in tandem. Exit speeds up to 20 m/s. Strip temperature at finishing mill entry ~1,050 °C; target finishing delivery temp (FDT) 850–920 °C.

### Equipment

#### 10A — Roughing Mill
| Machine | Function | Operating Conditions | Criticality |
|---|---|---|---|
| Roughing mill stand (4-hi reversing) | Reduce slab 220 mm → 30–40 mm in 5–6 passes | Roll force 30–60 MN; motor 10–25 MW | **HIGH** — work roll spalling = production stop |
| Edger (vertical roll) | Control width | Motor 2–5 MW | Medium |
| Crop shear | Crop head/tail | High-speed shear | Medium |

#### 10B — Finishing Mill
| Machine | Function | Operating Conditions | Criticality |
|---|---|---|---|
| F1–F7 finishing stands (4-hi) | Tandem reduction to final gauge | Roll force 15–40 MN/stand; strip speed F7 exit: 15–20 m/s; strip temp 850–950 °C | **HIGHEST** — work roll failure mid-strip catastrophic |
| Work rolls (changed every 4–8 h) | Direct strip contact | 600–700 mm dia; Hi-Cr or ICDP material; thermal + mechanical fatigue | **HIGH** — thermal fatigue cracking; spalling |
| Back-up rolls (changed monthly) | Support work rolls | 1,400–1,600 mm dia; large bearing assembly | High |
| Hydraulic gap control (HGC) | Real-time roll gap adjustment | ±0.01 mm precision; 100+ Hz response | **HIGH** — servo valve sticking |
| Work roll bending (WRB) | Crown / flatness control | 500–2,000 kN per side | High |
| Interstand cooling headers | Cool strip between stands | 500–2,000 l/min | Medium |
| Loopers | Maintain strip tension between stands | Hydraulic; fast response | Medium |

**Sensors:** load cells (roll force), HGC position (LVDT), strip thickness (X-ray gauge after each stand), strip width (laser), strip speed (encoder), strip temperature (pyrometer before/after each stand), flatness meter (shapemeter rolls).

#### 10C — Runout Table (ROT) + Coiler
| Machine | Function | Operating Conditions | Criticality |
|---|---|---|---|
| ROT cooling headers (laminar flow) | Control coiling temperature (CT) 500–700 °C | 200–800 l/min per header; 50–100 headers | **HIGH** — header control valve failure disrupts CT → mechanical property miss |
| Downcoilers (2–3) | Coil strip at 10–20 m/s | Pinch rolls, wrapper rolls; strip head-end tracking | High |
| Coil transfer cars + pallet cars | Transfer coils to dispatch | — | Medium |

**HSM Maintenance-Critical Equipment (ranked):**
1. Work rolls (F1–F7) — highest change frequency; spalling causes strip defects + mill damage
2. HGC servo valves — high failure frequency; direct quality impact
3. Backup roll bearings — large assemblies; failure causes unplanned stop
4. ROT cooling headers + control valves — product quality impact
5. Roughing mill coupling spindles — high torque; fatigue cracking

---

## STAGE 11 — PLATE MILL (alternative to HSM for heavy plate)

| Machine | Function | Operating Conditions | Criticality |
|---|---|---|---|
| 4-hi reversing mill | Reduce slab to plate (6–150 mm) | Roll force 60–80 MN; bidirectional | **HIGH** — work roll failure |
| Quench + accelerated cooling | TMCP (thermomechanical) processing | Controlled water quench post-roll | High |
| Leveller | Flatten plate | Hydraulic; multiple rolls | Medium |
| Ultrasonic testing line | Internal defect scan | — | Medium |

---

## STAGE 12 — COLD ROLLING MILL (CRM)

### Process
Hot-rolled pickled strip (2–6 mm) reduced to 0.18–3.0 mm in tandem cold mill (4–6 stands) or reversing mill at room temperature. Reduction ratios 50–80%. Strip exits with high hardness/tensile strength.

### Equipment

#### 12A — Pickling Line
| Machine | Function | Operating Conditions | Criticality |
|---|---|---|---|
| HCl pickling tanks (4–5) | Dissolve scale; strip speed 100–250 m/min | HCl 15–18%; 70–85 °C; corrosive | **HIGH** — tank leak, fume extraction failure |
| Rinse + dryer | Remove acid residue | — | Medium |
| Entry/exit loopers | Buffer speed differences | High-tension strip; hydraulic | High |
| Side trimmer | Trim strip edges | Carbide blades; quick-change | Medium |

#### 12B — Tandem Cold Mill (TCM)
| Machine | Function | Operating Conditions | Criticality |
|---|---|---|---|
| TCM stands (4–6, 4-hi or 6-hi) | Reduction each pass 15–40% | Roll force 10–30 MN; strip tension 20–60 MPa; speed 20–30 m/s | **HIGHEST** — work roll breakage at speed = emergency |
| Work rolls (4-hi / 6-hi) | Direct strip contact | Changed every 2–6 h; tungsten carbide or HSS | **HIGH** — spalling at cold rolling = strip surface defect |
| Automatic gauge control (AGC) | Maintain thickness ±1 µm | Servo valve + X-ray gauge feedback | **HIGH** |
| Emulsion spray system | Lubrication + cooling | Emulsion 3–5% concentration; 50–60 °C | High |
| Tension reels (coilers/uncoilers) | Strip tension control | 500–3,000 kN | High |

**Sensors:** X-ray thickness gauge (±0.5 µm), strip flatness (shapemeter), roll force (load cell), strip speed (encoder), tension (load cell on reels), roll temperature (IR).

---

## STAGE 13 — ANNEALING (BATCH / CONTINUOUS)

### Batch Annealing (BAF)
| Machine | Function | Operating Conditions | Criticality |
|---|---|---|---|
| Bell-type annealing furnace | Soften cold-rolled coils | Cycles: heat 650–720 °C, soak, cool; HNX atmosphere (H₂/N₂ 5/95) | **HIGH** — atmosphere seal failure → oxidation → coil scrapped |
| Inner cover + base | Contain protective atmosphere | Seal integrity critical | High |
| Circulation fan | Homogenise temperature | Bearing in hot HNX atmosphere | High |

### Continuous Annealing Line (CAL)
| Machine | Function | Operating Conditions | Criticality |
|---|---|---|---|
| CAL furnace (preheat, rapid heating, soaking, slow/fast cool zones) | Continuous strip processing | Strip speed 100–300 m/min; 700–900 °C; radiant tubes or direct-fired | **HIGH** — hearth roll build-up (pickup) → strip surface scratch → entire order scrapped |
| Hearth rolls | Support strip in furnace | 700–900 °C; pickup (alumina buildup on rolls) | **HIGHEST** — pickup = line stop, roll change |
| Tension bridles | Maintain strip tension at furnace entry/exit | — | High |
| Temper mill (skin pass) | Final mechanical property + surface finish | Light reduction 0.5–2% | Medium |

---

## STAGE 14 — GALVANIZING / COATING LINES

### Hot-Dip Galvanizing Line (HDG / CGL)
| Machine | Function | Operating Conditions | Criticality |
|---|---|---|---|
| Cleaning + pretreatment (alkaline degreaser) | Remove oil, prepare surface | 70–80 °C NaOH; electrolytic possible | Medium |
| Annealing furnace (in-line) | Same as CAL; often combined | 700–850 °C; reducing atmosphere | High |
| Zinc pot | Immerse strip in molten zinc | 450–460 °C; bath chemistry Al 0.18–0.25% | **HIGHEST** — zinc pot heating element failure = solidification event (days recovery) |
| Air knives | Control zinc coating weight | Air pressure 0.3–1.5 bar; knife gap ±0.1 mm | High |
| Tension leveller / skin pass | Improve flatness | — | Medium |
| Passivation / chromate / organic coater | Surface treatment | Roll coater; chemistry control | Medium |

**Sensors:** zinc pot temperature (immersion thermocouple), coating weight (X-ray fluorescence gauge online), air knife pressure, strip speed, strip temperature entering pot, bath chemistry (Al, Fe sensors).

### Electrogalvanizing / ETP Lines
Similar sensor profile; electroplating baths instead of zinc pot; rectifier banks are the critical equipment [unverified individual MTBF].

---

## STAGE 15 — UTILITIES

### 15A — Power Generation and Distribution
| Machine | Function | Operating Conditions | Criticality |
|---|---|---|---|
| BF top-gas turbine (TRT) | Recover ~20 MW from BF top pressure | 2–4 bar to atmosphere; continuous | **HIGH** — trip = ~20 MW lost; BF upset |
| BOF gas recovery turbine / boiler | Steam from converter gas combustion | 900 °C off-gas | High |
| Coke dry quenching (CDQ) steam boiler | Steam from hot coke sensible heat | 800 °C → 200 °C; steam 4–6 MPa | High |
| Sinter waste-heat boiler | Recover exhaust heat | 300–400 °C exhaust | Medium |
| Main power transformers (33/11/6.6 kV) | Step down grid supply | 100–300 MVA; oil-cooled | **HIGHEST** — failure = extended site outage |
| UPS / backup power (ARC furnace, caster controls) | Prevent safety-critical loss of control | — | **HIGH** |

**Sensors:** MW meters per HV feeder, transformer temperature (oil + winding), TRT vibration, steam pressure/flow.

### 15B — Compressed Air
| Machine | Function | Operating Conditions | Criticality |
|---|---|---|---|
| Centrifugal + screw compressors | Instrument air + process air | 7–10 bar; 100–5,000 Nm³/h | **HIGH** — instrument air loss = BF/caster control failure |
| Air dryers + filters | Dew-point control < −40 °C | — | High |
| Air receivers | Buffer supply | — | Low |

### 15C — Gas Networks
| Machine | Function | Operating Conditions | Criticality |
|---|---|---|---|
| BFG main (Blast Furnace Gas) | Fuel distribution (CO: 22–28%; H₂: 2–5%; CV: 3.5–4 MJ/Nm³) | 0.05–0.15 bar; large-diameter headers | **HIGH** — pressure loss or CO leak = safety shutdown |
| COG main (Coke Oven Gas) | Fuel distribution (H₂: 55%; CV: 18 MJ/Nm³) | — | High |
| LDG main (LD Converter Gas) | Fuel distribution (CO: 60–70%; CV: 8 MJ/Nm³) | Recovered from BOF; cleaning required | High |
| Gas holders (BFG / COG) | Buffer storage | Large cylindrical/membrane tanks | Medium |
| Gas compressor stations | Move gas across network | — | High |

**Sensors:** gas flow (orifice or ultrasonic), gas composition (CO, H₂ by online analyser), pressure per header, gas holder level, CO alarms throughout plant.

### 15D — Water Systems
| Machine | Function | Operating Conditions | Criticality |
|---|---|---|---|
| Blast furnace closed-circuit cooling | Cool staves, tuyeres | ΔT 5–15 °C; high flow; softened water | **HIGHEST** — cooling water failure = stave burnout |
| Caster secondary cooling pumps | Supply caster spray water | 2,000–15,000 l/min total; multiple zones | **HIGH** |
| HSM ROT supply pumps | Laminar cooling water | 10,000–30,000 l/min | High |
| Cooling towers | Reject heat from all circuits | 20–30 °C ΔT across tower | High |
| Descaler high-pressure pumps | 150–250 bar for scale removal | 500–1,500 l/min | Medium |
| Effluent treatment plant | Water recycle; suspended solids removal | — | Medium (regulatory) |

**Sensors:** flow (electromagnetic or ultrasonic), pressure, temperature, conductivity (scaling), pH, turbidity.

### 15E — Overhead Cranes
| Machine | Function | Operating Conditions | Criticality |
|---|---|---|---|
| BOF shop cranes (300–450 t) | Lift torpedo ladles and scrap buckets | 1,500 t capacity class; 24/7 | **HIGHEST** — crane failure with liquid steel = fatality |
| Caster ladle cranes (250–350 t) | Carry liquid steel ladles | — | **HIGHEST** |
| Coil yard cranes (magnet cranes) | Move steel coils | 20–60 t; automated in modern plants | High |
| Slab yard cranes | Move slabs from caster to reheating | 40–100 t | High |

**Sensors:** load cells (hoist weight), rope tension, hook position (encoder), motor current, braking system pressure, runway wheel flange wear (ultrasonic [unverified deployment]).

**Maintenance-Critical:** BOF and caster crane hoisting machinery (wire rope, drum, brake) — failure here is safety-critical Tier 1 (ISO 4301 classification).

### 15F — Conveyors (Internal)
Belt conveyors throughout plant for: ore fines, coke, limestone, sinter, pellets, slag, roll scale, scrap. Same criticality profile as Stage 0 conveyors. **Return idler bearing failure** causes belt fires; monitored by thermal imaging in modern plants [Tata Steel IJmuiden heat-camera belt monitoring system, [unverified deployment date]].

---

## CROSS-STAGE MAINTENANCE PRIORITY SUMMARY

| Rank | Equipment | Stage | Failure Mode | Consequence |
|---|---|---|---|---|
| 1 | Taphole assembly | BF (4D) | Erosion / breakout | Fatality + multi-day BF stop |
| 2 | Caster breakout (mould level) | Concast (8B) | SEN clog / mould sticking | 50–300 t steel loss + 12–24 h outage |
| 3 | BOF/EAF shop crane | Steelmaking (15E) | Rope/brake failure | Fatality + production stop |
| 4 | Coke oven battery walls | Coke ovens (1) | Refractory crack | Multi-week battery outage; gas emission |
| 5 | Hot stove shells | BF (4A) | Shell crack | BF shutdown; 10–20 day repair |
| 6 | Blast blower motor/bearings | BF (4A) | Bearing failure | Immediate BF stop |
| 7 | EAF electrode system | EAF (5) | Breakage / transformer trip | Heat loss; 2–4 h recovery |
| 8 | Zinc pot heating elements | Galvanizing (14) | Element failure | Solidification; 2–3 day melt-out |
| 9 | HSM work rolls (F-stands) | HSM (10B) | Thermal spalling | Strip defect + emergency roll change |
| 10 | Main power transformers | Utilities (15A) | Insulation failure | Site-wide outage |
| 11 | Instrument air compressors | Utilities (15B) | Compressor trip | BF/caster controls fail safe |
| 12 | Sinter strand draft fans | Sinter (2) | Bearing failure | Strand stop; BF feed interruption |
| 13 | Cold mill work rolls | CRM (12B) | Spalling at speed | Emergency strip break |
| 14 | CAL hearth rolls | Annealing (13) | Pickup buildup | Strip surface defect; product scrap |
| 15 | BF cooling water system | BF + Utilities | Pump/pipe failure | Stave burnout; tuyere explosion |

---

## SENSOR TAXONOMY (Cross-Stage Reference)

| Sensor Type | Stages Present | Parameter |
|---|---|---|
| Thermocouple (K, R, S, N types) | All thermal stages (1,2,4,6,9,10,13,14) | Temperature |
| IR / radiation pyrometer | BF cast house, HSM, caster, reheating | Surface temperature |
| Load cell | HSM (roll force), ladles, conveyors | Force / weight |
| LVDT / position encoder | HGC, mould oscillator, charging, cranes | Position / displacement |
| Electromagnetic induction | Mould level (concast) | Liquid steel level |
| X-ray gauge | TCM, HSM (thickness), galvanizing (coating wt.) | Thickness / coating weight |
| XRF online analyser | Sinter chemistry, slag, zinc pot | Chemistry |
| Gas chromatograph / online analyser | BFG, COG, LDG, stoves | Gas composition |
| Vibration (accelerometer) | Fans, blowers, compressors, motors, rolls | Vibration signature |
| Acoustic emission | BF taphole, coke oven walls | Structural integrity |
| Current / power meter | All motor-driven equipment | Load, efficiency |
| Flow meter (EM/ultrasonic) | Water, gas, cooling circuits | Flow rate |
| Pressure transmitter | Gas networks, hydraulics, cooling | Pressure |
| Laser profilometer | BOF lining, roll profiles, slab dimensions | Geometry |
| Thermal camera | Belt conveyors, coke oven doors | Heat anomaly / fire risk |

---

## DATA QUALITY PLATFORM — KEY IMPLICATIONS

1. **Sensor density is not uniform.** BF (4A–4E) and continuous caster (8A–8D) have the densest sensor arrays (100–500 points per unit). Raw material handling has sparse coverage. Any missing-data imputation strategy must reflect this.

2. **Time alignment is non-trivial.** BOF heat time = 18 min. Caster heat time = 45–90 min. Reheating furnace = 90–180 min. A single slab carries data across 3–4 stages with different time granularities (1 Hz at caster → 0.1 Hz at reheating → per-coil at HSM).

3. **Multi-modal data.** Numerical time series (dominant), image data (thermal cameras, lining lasers), chemical assay tables (lab, 1–2/shift), maintenance records (free text), shift logs (free text). All must be ingested.

4. **Safety-critical channels require no-loss guarantee.** Tuyere cooling flow, mould level, crane load cells, instrument air pressure — these channels must never be imputed silently. Data gaps must raise explicit data-quality alerts.

5. **High-consequence low-frequency events.** BF taphole breakout: once per 2–5 years. Mould breakout: once per 100–500 heats. These are class-imbalance extremes; any ML pipeline on this data needs explicit handling.

---

*End of process map. All operating condition figures are industry-typical unless a specific Tata Steel source is cited. Items marked [unverified] require confirmation against actual Tata Steel site documentation before use in production ML pipelines.*
