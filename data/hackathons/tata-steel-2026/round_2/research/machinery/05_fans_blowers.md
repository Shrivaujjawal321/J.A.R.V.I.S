# Fans & Blowers in an Integrated Steel Plant — Deep Reference
**Research Date:** 2026-06-08
**Scope:** Tata Steel-scale integrated steelworks (BF→Sinter→Coke→BOF chain)
**Confidence:** High for failure modes, sensors, thresholds; Medium for cost figures (cited but partly vendor-sourced)

---

## 1. FAN TYPES, LOCATIONS & KEY SPECS

### 1.1 Blast Furnace Cold-Blast Turbo-Blower
**The most critical rotating machine in the entire plant.**

| Parameter | Typical Value |
|---|---|
| Configuration | 2–4 stage centrifugal OR axial turbo-compressor |
| Flow capacity | 150,000–800,000 m³/hr (very large BFs up to 1.5 million m³/hr) |
| Discharge pressure | 3–5 bar (centrifugal); up to 25 bar (axial) |
| Discharge temperature | 150–250°C from compression heat alone |
| Motor rating | 10–29 MW |
| Operating speed | 3,000–10,000 RPM (some high-speed designs up to 60,000 RPM) |
| Tip speed | >300 m/s |
| Total sensors per blower train | 24–36 |

Hot blast is heated separately in stoves to 1,000–1,300°C before injection. The blower provides the cold-blast air at pressure.
**Location:** Blower house, adjacent to cast house. Single point of failure for the entire furnace.

**Reference:** [Blast Furnace Blower Predictive Maintenance — Oxmaint](https://oxmaint.com/industries/steel-plant/blast-furnace-blower-turbo-machinery-predictive-maintenance)

---

### 1.2 Sinter Plant Main Draft Fan (Main Exhaust / Exhauster)
**Second-most critical fan; loss = strand starvation.**

| Parameter | Typical Value |
|---|---|
| Type | Large centrifugal, single or double-inlet |
| Duty | Suction through windboxes; moves hot, dust-laden gas |
| Gas temperature | 100–200°C at fan inlet (post-ESP/cyclone) |
| Dust loading | Moderate post-ESP; very high if precipitator bypasses |
| Motor | 3–15 MW |
| Control | Inlet guide vanes (IGV) or variable-speed drive |

**Location:** Downstream of electrostatic precipitator, upstream of chimney.
MTBF target (world-class): 800+ operating hours between planned interventions.
A single exhauster failure halts the entire sintering strand; 50 t/hr shortfall = USD 8,000–15,000/hr lost production when BF throttles.

---

### 1.3 Sinter Cooler Fans
| Parameter | Value |
|---|---|
| Type | Axial or centrifugal |
| Duty | Force ambient air upward through hot sinter bed (700°C+ bed) |
| Number | 4–12 fans per cooler |
| Control | Speed-varied to match sinter output rate |

**Location:** Below the linear/circular sinter cooler deck.

---

### 1.4 Blast Furnace Stove Combustion Air Fans (FD Fans for Stoves)
| Parameter | Value |
|---|---|
| Type | Centrifugal FD (forced-draft) |
| Fuel handled | BF top gas (BFG), COG, or mixed gas |
| Temperature | Ambient inlet; stove dome up to 1,350°C |
| Safety | ATEX/explosion-proof construction; spark-resistant (AMCA Type A/B) mandatory for BFG/COG service |

**Location:** Stove battery, adjacent to BF.

---

### 1.5 Induced Draft (ID) Fans — BOF/EAF/Coke Oven Hoods
- Evacuate fume and offgas from converter/EAF hoods or coke oven ascension pipes
- Handle high-temperature, dust-laden, sometimes CO-bearing gas
- Must be ATEX-rated where gas is flammable
- Large units: 2–8 MW motors
- Control: IGV + variable-speed drive

---

### 1.6 Dust Extraction & Baghouse Fans
| Parameter | Value |
|---|---|
| Type | Radial-blade centrifugal (preferred for abrasive/sticky dust — self-cleaning) |
| Wheel design | Backward-curved for clean service; radial-paddle for heavy dust |
| Duty | Maintain negative pressure on hoods/enclosures; draw through baghouse |
| Motor | 75 kW – 2 MW per fan |

**Design note:** AMCA recommends radial-blade (paddle) wheels for coarse, heavy, or abrasive dust in baghouse service — more erosion-resistant than backward-inclined.

---

### 1.7 BF Top Gas / COG Gas Blowers (circulation/boosting)
- Circulate or boost BF top gas for power generation or distribution
- Require gas-tight shaft seals (dry gas seals or labyrinth + buffer gas)
- Flammable gas service: ATEX Zone 1 or 2, gas-tight casing, CO detectors mandatory

---

## 2. PARTS BREAKDOWN

```
Fan/Blower Assembly
│
├── Impeller / Rotor
│   ├── Blades (backward-curved, radial, or axial aerofoil)
│   ├── Hub / disc
│   ├── Shroud (covered impellers)
│   └── Balance weights (trim balance holes/plugs)
│
├── Shaft
│   ├── Journal sections (running in radial bearings)
│   ├── Thrust collar
│   ├── Keyway / interference fit to impeller
│   └── Keyphasor notch (once-per-rev reference)
│
├── Bearings
│   ├── Radial (journal) bearings — sleeve / tilting-pad for turbomachinery
│   ├── Thrust bearing (double-acting for turbo-blowers)
│   └── Anti-friction (rolling element) bearings — smaller fans
│
├── Casing / Volute
│   ├── Spiral scroll (centrifugal)
│   ├── Inlet bell / suction cone
│   ├── Inspection ports / handhole covers
│   └── Drain / vent connections
│
├── Inlet Guide Vanes (IGV) / Inlet Dampers
│   ├── Actuator (pneumatic or electric)
│   ├── Vane ring / spider
│   └── Position feedback sensor
│
├── Shaft Seals
│   ├── Labyrinth / carbon ring seals (standard)
│   ├── Dry gas seals (BFG / hazardous gas service)
│   └── Stuffing box (older, lower-pressure fans)
│
├── Drive / Coupling
│   ├── Direct drive (motor–coupling–fan shaft)
│   ├── Flexible disc / gear coupling
│   ├── Fluid coupling or VFD (speed control)
│   └── Intermediate gearbox (some high-speed designs)
│
└── Motor
    ├── Squirrel-cage induction (most)
    ├── Synchronous motor (large turbo-blowers for PF correction)
    └── Motor current transformers (MCTs) for load monitoring
```

---

## 3. SENSOR SUITE — TYPES & PLACEMENT

### Blast Furnace Turbo-Blower (Full Turbomachinery Protection per API 670)

| Sensor | Location | Purpose |
|---|---|---|
| Proximity probes (eddy-current) | 2 × per radial bearing, 90° X-Y | Shaft relative displacement (µm) |
| Axial/thrust probes | Thrust bearing collar, 2 probes | Axial shaft position (mm) |
| Keyphasor probe | Single notch on shaft | 1× reference; phase tracking |
| Casing accelerometers | Each bearing housing, 3 axes | High-frequency bearing defects (kHz range) |
| RTD / thermocouple | Loaded bearing zone, metal | Babbitt/bearing metal temperature (°C) |
| Dynamic pressure transducers | Suction/discharge piping | Surge detection (0.6–2.5 Hz pulsations) |
| Process pressure transmitters | Inlet, interstage, outlet | Performance & surge margin |
| Flow measurement (orifice/venturi) | Suction duct | Flow vs. surge curve |
| Oil pressure transmitters | Supply & return headers | Lube oil system health |
| Oil temperature sensors | Sump, supply, return, each bearing drain | Thermal status |
| In-line oil particle counters | Main lube supply | Wear debris (ISO 4406 cleanliness) |
| Seal gas ΔP transmitters | Dry gas seal panels | Seal integrity |
| Motor CT / power analyser | MCC / switchgear | Motor current, kW, PF |

**Total sensor count per blower train:** 24–36 sensors (API 670 minimum compliant)

### Industrial Process Fans (ID/FD/Sinter/Cooler fans — ISO 13373 / ISO 10816)

| Sensor | Purpose |
|---|---|
| Piezo accelerometers on bearing housings (H, V, A axes) | Overall vibration velocity (mm/s RMS) |
| RTD or thermocouple on bearing housing | Bearing temperature |
| Motor CT / power meter | Electrical load |
| Inlet/outlet pressure transmitters | Draft & flow |
| IGV position sensor | Control feedback |
| Shaft proximity probes (larger fans >500 kW) | Shaft displacement |
| Vibrating wire or strain gauge on critical blades | Blade resonance (specialist installations) |

---

## 4. NORMAL OPERATING READINGS

### 4.1 Vibration — Velocity (Overall RMS, casing-mounted accelerometer)

**ISO 10816-3 / ISO 20816-3 Zone Boundaries (mm/s RMS)**

| Machine Group | Description | Zone A (new) | Zone B (OK) | Zone C (restricted) | Zone D (DANGER) |
|---|---|---|---|---|---|
| **Group 1, rigid** | >300 kW, rigid mount (most large process fans) | <2.3 | 2.3–4.5 | 4.5–7.1 | >7.1 |
| **Group 1, flexible** | >300 kW, flexible/spring mount | <3.5 | 3.5–7.1 | 7.1–11.0 | >11.0 |
| **Group 2, rigid** | 15–300 kW, rigid | <2.3 | 2.3–4.5 | 4.5–7.1 | >7.1 |

**ISO 14694 (fan-specific) BV category thresholds (in-situ, velocity mm/s RMS):**

| Category | Application | Normal OK | Alarm | Shutdown |
|---|---|---|---|---|
| BV-3 | Process/power gen, up to 300 kW | <4.5 | >7.1 | >11.2 |
| BV-4 | Petrochem / critical process, flexible mount | <2.8 | >4.5 | >7.1 |

**Balance quality grade (ISO 1940-1):** G6.3 general; G2.5 for process fans; G1.0 for high-speed turbomachinery.

---

### 4.2 Shaft Displacement (Proximity Probes — Turbo-blowers, API 670)

| Parameter | Normal | Alert | Trip |
|---|---|---|---|
| Shaft relative vibration (radial, peak-peak) | <50 µm | 80 µm | 125–160 µm |
| Axial position (thrust) | ±0.1 mm of datum | ±0.3 mm | ±0.5 mm |
| Journal eccentricity ratio | <0.5 | 0.5–0.7 | >0.7 (oil film breakdown imminent) |

**API 670 note:** A shaft vibration reaching the 160 µm trip threshold can cross from alert to trip "in under one second" during instability — digital relay trip essential, not analog.

---

### 4.3 Bearing Temperature (°C)

| Bearing Type | Normal Operating | Alarm (absolute or rate) | Trip |
|---|---|---|---|
| Sleeve/journal bearing (Babbitt) | 60–85°C | Baseline +10°C OR rate >15°C/hr | Baseline +20°C OR 120°C absolute |
| Rolling-element bearing | 50–80°C | >80°C | >100°C |
| General (ISO/CMMS rule of thumb) | <80°C stable | >80°C or rising | >100°C or rise >5°C in 15 min |

---

### 4.4 Process / Performance Readings

| Parameter | Normal |
|---|---|
| Surge margin (BF blower) | >20% above surge line |
| Specific power deviation | Within ±3% of post-overhaul OEM baseline |
| Oil viscosity deviation | ±5% of spec (caution); ±10% (critical) |
| Lube oil iron content | <50 ppm (>50 ppm = journal wear) |
| Lube oil copper content | <20 ppm (>20 ppm = bearing cage wear) |
| Oil water content | <0.1% (caution); >0.5% (critical) |
| Oil particle count | ISO 4406 Class 16/14/11 or cleaner |

---

## 5. DEFECT READINGS — FAILURE MODE SIGNATURES

### 5.1 Mass Imbalance (Blade Erosion → Progressive Imbalance)
**Vibration spectrum signature:** Sharp dominant peak at **exactly 1× RPM** (running speed), stable phase angle.
Phase is crucial: phase stays constant as amplitude grows — distinguishes from looseness (variable phase).

| Stage | Radial vibration velocity | Shaft displacement | Action |
|---|---|---|---|
| Baseline (new) | 1–2 mm/s | ~20–30 µm pp | Normal |
| Early imbalance growth | 2–4.5 mm/s (+60–100%) | 40–60 µm | Increase monitoring frequency |
| Alarm — ISO Zone C | >4.5 mm/s rigid (>7.1 flexible) | >80 µm alert | Schedule rebalance within 2–4 weeks |
| Critical — ISO Zone D / shutdown | >7.1 mm/s rigid | >125 µm trip | Emergency stop |

**ISO ref:** ISO 10816-3 (casing velocity); ISO 14694 (fan-specific); API 670 §4.3 (shaft displacement trips).

Blade erosion is asymmetric — leading-edge material loss on one or more blades shifts centre of mass. Imbalance force = m × e × ω² — doubles with every +41% speed increase (ω² law), so erosion that causes mild vibration at part-load becomes critical at full speed.

---

### 5.2 Blade Fatigue Cracking / Fracture
**Earliest sign:** Elevated **blade pass frequency (BPF)** = n_blades × RPM.
Also: sidebands around BPF at ±1×, ±2× RPM (modulation from cracked blade).

| Indicator | Normal | Crack developing | Imminent failure |
|---|---|---|---|
| BPF amplitude | Low baseline | +3–6 dB | >10 dB above baseline + sidebands |
| Sub-synchronous content | None | Slight noise floor rise | Broadband rise |
| Detection window | — | 2–8 weeks pre-failure | Hours–days |

**Catastrophic risk:** A fractured blade at high speed (tip speeds >300 m/s) becomes a ballistic fragment — casing penetration risk. Mandated borescope interval when BPF sidebands appear.

---

### 5.3 Bearing Failure (Rolling Element or Journal)
**Rolling-element bearing defect frequencies:**
- BPFO (outer race): n_balls × 0.4 × RPM (typical)
- BPFI (inner race): n_balls × 0.6 × RPM
- BSF (ball spin): 0.2 × RPM × (diameter ratio)
- FTF (cage): ~0.4 × RPM

| Stage | BPFO/BPFI amplitude | Temperature | Detection window |
|---|---|---|---|
| Incipient (Stage 1) | Slight rise above noise floor | Baseline | 6–12 months (oil debris, ultrasound) |
| Early (Stage 2) | 3–6 dB above noise floor | +2–5°C | 4–8 weeks (vibration spectrum) |
| Advanced (Stage 3) | Significant spectral lines | +5–15°C | 1–4 weeks |
| Failure imminent | Harmonics + sidebands; overall RMS spikes | +20°C+ | Hours–days |

**Journal bearing (BF turbo-blower):**
Oil whirl: sub-synchronous at 0.4–0.48× RPM → dangerous if locks to 0.5× (oil whip → shaft orbit instability → possible rub and seizure).

---

### 5.4 Misalignment
**Signature:** Dominant **2× RPM** peak in radial AND elevated axial vibration.
Also: 1× + 2× both elevated; axial 2× may exceed radial 1×.

| Indicator | Normal | Alarm |
|---|---|---|
| 2× RPM / 1× RPM ratio | <0.3 | >0.5 (investigate); >1.0 (critical) |
| Axial vibration | Low | Elevated, comparable to radial |
| Bearing temperatures | Symmetric | Asymmetric (hot on misaligned bearing) |

**ISO alignment tolerance (>1800 RPM):** Angular <0.0005″/inch coupling spacing; offset <0.001″ TIR.

---

### 5.5 Resonance / Structural Resonance
**Signature:** Vibration amplitude disproportionately high at one specific speed; does not scale linearly with load.
Detected by: bump test / impact test (ODS analysis) during outage; operating deflection shape (ODS) online.
Risk: blade natural frequency excited by BPF (BPF = n × f_natural). Fan blade resonance at operating speed → high-cycle fatigue cracking.

---

### 5.6 Fouling Buildup on Impeller
**Signature:** Gradual, **symmetric** increase in 1× (mass addition, not loss) + reduction in flow/pressure performance.
Distinguished from erosion imbalance by: performance data (lower flow at same power) + slower vibration growth rate.
Recoverable by: online washing (where process permits) or offline water wash during planned stop.

---

### 5.7 Shaft Seal Gas Leakage (Hazardous Gas Service)
**Earliest signs:**
- Seal gas differential pressure drop below OEM minimum
- CO / BFG detector alarm at blower house (if BFG service)
- Bearing housing temperature anomaly from gas ingress

**Safety risk:** BFG (CO-rich) or COG leakage → asphyxiation + explosion hazard. ATEX-rated fans must maintain seal integrity — trip on seal ΔP loss is mandatory.

---

### 5.8 Compressor Surge (BF Turbo-Blower)
**Signature:** Low-frequency pulsation **0.6–2.5 Hz** on dynamic pressure transducers + axial vibration spike + flow reversal noise.
**Consequence:** Massive cyclic force on impeller (every surge cycle imposes a full pressure reversal). Even 3–5 surge events can fatigue-crack blades. Mandatory post-surge borescope.

---

## 6. FAILURE MODES — SUMMARY TABLE

| Failure Mode | Root Cause | Earliest Detectable Sign | Time to Failure After Detection | ISO/API Ref |
|---|---|---|---|---|
| Blade erosion → imbalance | Abrasive particles (iron ore, coke, lime) | 1× RPM growth, first appearing in spectrum trend | Weeks–months | ISO 14694, ISO 10816 |
| Blade fatigue cracking | HCF from resonance or surge-induced stress | BPF amplitude + sidebands on spectrum | 2–8 weeks | — |
| Blade fracture (catastrophic) | Propagated crack | Sub-synchronous broadband rise, sudden amplitude jump | Hours | — |
| Rolling-element bearing spalling | Overload, lubrication failure, contamination | BPFO/BPFI in spectrum, oil debris | 4–26 weeks | ISO 15243 |
| Journal bearing oil whirl | Lightly loaded bearing, excessive clearance | 0.4–0.48× sub-synchronous in radial spectrum | Minutes to hours once initiated | API 670 |
| Shaft seal leakage | Wear, thermal cycling, contamination | Seal ΔP below minimum | Days–weeks | — |
| Fouling buildup | Sticky process dust (lime, condensate) | Symmetric 1× increase + performance drop | Weeks–months | — |
| Resonance | BPF coincides with blade natural freq | High amplitude at one speed, non-linear load response | Slow crack initiation | IEC/ISO structural |
| Compressor surge | Off-design operating point, duct blockage, IGV fault | 0.6–2.5 Hz pressure pulsation | Immediate | API 672/670 |
| Misalignment | Thermal growth, incorrect assembly | 2× dominant + axial elevation | Weeks–months | ISO 10816 |

---

## 7. REPAIR / RESOLUTION PROCESS

### 7.1 Blade Repair & Rebalancing (Sinter/ID/FD Fans)
1. **Isolate fan:** Lockout/tagout; open dampers for safe access.
2. **Borescope / visual inspection:** Map blade erosion depth and pattern.
3. **Hard-facing / weld repair:** Chrome carbide overlay (CCO) or tungsten carbide spray on leading edges and pressure faces. Typical weld repair: 4–8 hrs per impeller.
4. **In-situ dynamic balancing:** Add trial weights; two-plane balance to ISO 1940-1 G2.5 (or G1.0 for high-speed). Portable balancing analyzer with phase reference.
5. **Restart and trending re-baseline:** New baseline accepted within Zone A (<2.3 mm/s rigid).

**Hard-facing impeller life extension:** Standard MS impellers without hard-facing: 12–24 months. CCO hard-faced: 36–48 months in high-dust duty.
**Replacement cycle:** Severely eroded impellers requiring full replacement: 8–16 hours (crane lift, bolt-up, balancing).

---

### 7.2 Bearing Replacement
| Action | Time |
|---|---|
| Rolling-element bearing change (smaller fans, <500 kW) | 4–8 hrs |
| Journal / tilting-pad bearing change (turbo-blower) | 24–48 hrs (clean-room conditions, precision clearance checks) |
| Full rotor-out for shop rebalancing | Rotor removal 16–24 hrs; shop balance + reassembly 1–3 weeks; OEM facility 6–16 weeks |

**Planned vs. unplanned:**
- Planned (scheduled on 6–12 month trend data): bearing pre-purchased (4–16 weeks lead time); maintenance window aligned with BF relining or planned production dip.
- Unplanned (sudden alarm/trip): 24–72 hrs furnace wind-break recovery; emergency bearing sourcing at 40–80% premium; total event cost $2–8 million.

---

### 7.3 BF Turbo-Blower Major Overhaul
- **Interval:** 8–15 years (with proper monitoring).
- **Scope:** Rotor removal, shop balance, impeller inspection, all seal and bearing replacement, alignment.
- **Rotor lead time (new):** 12–24 months — no stockpile exists; rotor damage = extended outage.
- **Bearing assembly lead time:** 4–16 weeks.

---

### 7.4 Shaft Seal Repair (Dry Gas Seals)
- Seal cartridge replacement: 16–32 hrs (specialist OEM technician required).
- Hazardous gas service: N₂ purge of housing before opening; gas detection active throughout.

---

## 8. COST & PRODUCTION LOSS IMPACT

### 8.1 BF Blower Failure — The Catastrophic Case

| Metric | Value | Source |
|---|---|---|
| Operational cost of downtime | USD 500,000+ per hour | [Oxmaint BF Blower Maintenance](https://oxmaint.com/industries/steel-plant/blast-furnace-blower-maintenance-monitoring) |
| Cost per unplanned emergency shutdown event | USD 4–8 million (production loss + repairs + refractory thermal cycling) | [Ifactory AI Analytics](https://ifactoryapp.com/industries/steel-plant/blast-furnace-blower-turbo-machinery-predictive-analytics) |
| Recovery time after blower trip | 8 days minimum (controlled wind-break → maintenance → restart ramp-up) | [Oxmaint](https://oxmaint.com/industries/steel-plant/blast-furnace-blower-maintenance-monitoring) |
| Refractory life reduction per event | 6–18 months (from thermal cycling) | [Ifactory AI](https://ifactoryapp.com/industries/steel-plant/blast-furnace-blower-turbo-machinery-predictive-analytics) |
| Real-world example — Algoma Steel BF outage | ~150,000 t hot metal lost; EBITDA impact CAD 120–130 million | [Northern Ontario Business](https://www.northernontariobusiness.com/industry-news/manufacturing/blast-furnace-outage-cost-algoma-steel-as-much-as-130m-9114927) |
| Annual expected loss without monitoring (2 events/yr) | ~USD 10 million per blower house | [Ifactory AI](https://ifactoryapp.com/industries/steel-plant/blast-furnace-blower-turbo-machinery-predictive-analytics) |
| Predictive monitoring annual ROI | USD 11.5 million (avoided failures + component life extension + energy) | [Oxmaint](https://oxmaint.com/industries/steel-plant/blast-furnace-blower-turbo-machinery-predictive-maintenance) |
| Monitoring system payback | Under 2 months | [Oxmaint](https://oxmaint.com/industries/steel-plant/blast-furnace-blower-turbo-machinery-predictive-maintenance) |

**Shutdown sequence context:** A blower trip triggers an immediate furnace wind-break requiring 34 sequential controlled operations. The wind cannot simply be restarted — tuyeres, taphole, and burden state all require managed ramp-down, then managed ramp-up.

---

### 8.2 Sinter Main Exhaust Fan Failure

| Metric | Value |
|---|---|
| Production shortfall | 50 t/hr sinter deficit |
| BF throttle cost | USD 8,000–15,000/hr [unverified — vendor estimate] |
| Bearing change (planned) | 8–16 hrs, fan off-line; BF may throttle or use sinter stockpile buffer |
| Impeller replacement | 16–24 hrs outage; full sinter strand stop |
| MTBF world-class target | 800+ operating hours |

---

### 8.3 Safety Considerations — Flammable Gas Service

- **BFG / COG fans:** CO content in BFG typically 22–27% by volume. Explosive limits: COG 4.5–35%; BFG ~35–74%. Shaft seal failure → gas in blower house → explosion + asphyxiation.
- **Mandatory controls:** Gas detection (CO + combustible); ATEX Zone 1 or 2 classification; spark-resistant AMCA Type A construction; dry gas seal with N₂ buffer; automatic trip on seal ΔP loss.
- **AMCA spark-resistance classes:** Type A = all airstream parts non-ferrous; Type B = non-ferrous wheel + rubbing ring; Type C = non-ferrous plate both sides of housing.
- **Stove FD fans:** Handle mixed BFG/COG at burners — same ATEX requirements.
- **BOF/EAF ID fans:** Handle CO-rich converter gas; positive-pressure seals or water seals on shaft.

---

## 9. MONITORING STRATEGY & PREDICTIVE MAINTENANCE OUTCOMES

### 9.1 Monitoring Frequency by Criticality

| Fan Type | Recommended Monitoring |
|---|---|
| BF Turbo-Blower | Continuous online, 24×7, API 670 protection system |
| Sinter Main Exhaust | Continuous online (≥weekly route if no online) |
| BOF/EAF ID fans | Monthly route-based; online for >2 MW |
| Cooler fans, FD fans | Monthly route-based |
| Baghouse fans | Quarterly; monthly in high-dust service |

### 9.2 Predictive Maintenance Results (Reported Outcomes)

| Metric | Result | Source |
|---|---|---|
| Unplanned blower shutdowns reduction | 92% | [Ifactory AI](https://ifactoryapp.com/industries/steel-plant/blast-furnace-blower-turbo-machinery-predictive-analytics) |
| Advance warning — bearing | 14–28 days (online analytics) vs. 6–12 months (early ultrasound/oil debris) | [Oxmaint](https://oxmaint.com/industries/steel-plant/blast-furnace-blower-turbo-machinery-predictive-maintenance) |
| Advance warning — rotor imbalance | 21–45 days | [Oxmaint](https://oxmaint.com/industries/steel-plant/blast-furnace-blower-turbo-machinery-predictive-maintenance) |
| Oil change interval extension | 2× with oil analysis | [Oxmaint](https://oxmaint.com/industries/steel-plant/blast-furnace-blower-maintenance-monitoring) |
| Major overhaul interval achieved | 15+ years (with online CBM) | [Oxmaint](https://oxmaint.com/industries/steel-plant/blast-furnace-blower-maintenance-monitoring) |

---

## 10. KEY STANDARDS REFERENCE

| Standard | Scope | Application |
|---|---|---|
| **ISO 10816-3 / ISO 20816-3** | Vibration severity zones A/B/C/D for rotating machinery >15 kW | All process fans (casing-mounted velocity) |
| **ISO 14694:2003** | Industrial fans — balance quality & vibration levels; BV-1 to BV-5 categories | Fan-specific alarm/shutdown limits |
| **ISO 1940-1** | Balance quality grades G0.4–G6.3 | In-situ and shop balancing of fan impellers |
| **API 670** | Machinery Protection Systems (proximity probes, thermocouple, axial position) | BF turbo-blowers and large turbomachinery |
| **API 672 / 681** | Packaged integrally geared centrifugal air compressors | Some BF blower configurations |
| **ISO 15243** | Rolling-element bearing failure classification | Bearing damage analysis |
| **ISO 13373** | Condition monitoring of machines — vibration | General vibration program |
| **AMCA 99-0401** | Spark-resistant fan construction Types A/B/C | Hazardous gas service fans |

---

## 11. GLOSSARY OF KEY TERMS

| Term | Meaning |
|---|---|
| BPF | Blade Pass Frequency = n_blades × RPM |
| BPFO/BPFI | Bearing Pass Frequency Outer/Inner race |
| BSF | Ball Spin Frequency |
| FTF | Fundamental Train (cage) Frequency |
| 1× / 2× | 1× = once per revolution (imbalance); 2× = twice (misalignment) |
| Sub-synchronous | Below running speed — oil whirl, surge, stall |
| IGV | Inlet Guide Vanes — flow control device |
| CBM | Condition-Based Maintenance |
| HCF | High-Cycle Fatigue |
| CCO | Chrome Carbide Overlay (hard-facing) |
| ATEX | EU explosive atmosphere classification |
| BFG | Blast Furnace Gas (~22% CO, ~55% N₂, ~21% CO₂, ~2% H₂) |
| COG | Coke Oven Gas (~55% H₂, ~25% CH₄ — very flammable) |

---

## Sources

- [Blast Furnace Blower Turbo-Machinery Maintenance: Vibration Analysis & Condition Monitoring — Oxmaint](https://oxmaint.com/industries/steel-plant/blast-furnace-blower-turbo-machinery-maintenance)
- [Blast Furnace Blower Predictive Maintenance — Oxmaint](https://oxmaint.com/industries/steel-plant/blast-furnace-blower-turbo-machinery-predictive-maintenance)
- [Blast Furnace Blower Maintenance: Prevent Costly Turbo-Blower Failures — Oxmaint](https://oxmaint.com/industries/steel-plant/blast-furnace-blower-maintenance-monitoring)
- [Blast Furnace Blower & Turbo-Machinery Predictive Analytics — Ifactory AI](https://ifactoryapp.com/industries/steel-plant/blast-furnace-blower-turbo-machinery-predictive-analytics)
- [Sinter Plant Maintenance Management: Iron Ore Preparation — Oxmaint](https://oxmaint.com/industries/steel-plant/sinter-plant-maintenance-management-iron-ore-preparation)
- [Vibration Monitoring for Centrifugal Blowers: The 2026 Guide — F7i.ai](https://f7i.ai/blog/vibration-monitoring-for-centrifugal-blowers-beyond-basic-balancing)
- [Comprehensive Field Guide: Industrial Fan and Blower Maintenance (Vibration Limits) — Unitec Industrial](https://www.unitecd.com/comprehensive-field-guide-industrial-fan-and-blower-maintenance-balancing-belt-tensioning-bearing-lubrication-and-vibration-limits/)
- [ISO 14694: Fan Vibration & Balance Quality Standard — Vibromera](https://vibromera.eu/glossary/iso-14694/)
- [ISO 10816-3 Vibration Limits: Zones A/B/C/D — Vibromera](https://vibromera.eu/glossary/iso-10816-3/)
- [Understanding the ISO 10816-3 Vibration Severity Chart — Acoem USA](https://acoem.us/blog/other-topics/understanding-the-iso-10816-3-vibration-severity-chart/)
- [Blast Furnace Outage Cost Algoma Steel as Much as $130M — Northern Ontario Business](https://www.northernontariobusiness.com/industry-news/manufacturing/blast-furnace-outage-cost-algoma-steel-as-much-as-130m-9114927)
- [ID Fans and FD Fans — AS Engineers](https://theasengineers.com/id-and-fd-fans/)
- [Centrifugal Blowers and Fans in Steel and Metal Industries — AS Engineers](https://theasengineers.com/top-centrifugal-blowers-and-fans-for-steel-and-metal-industries/)
- [Fan Failures: Five Typical Problems — Plant Magazine](https://www.plant.ca/features/163687/)
- [Understanding Sinter and Sinter Plant Operations — IspatGuru](https://www.ispatguru.com/understanding-sinter-and-sinter-plant-operations/)
- [Vibration Analysis of Centrifugal Fans — Power-MI](https://power-mi.com/content/vibration-analysis-centrifugal-fans)
