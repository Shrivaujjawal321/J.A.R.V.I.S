# Continuous Caster — PdM Reference (Exhaustive)

**Domain:** Tata Steel Round 2 — Agentic Maintenance Wizard  
**Safety class:** CRITICAL — breakout = molten steel release, Class-1 safety incident  
**Date:** 2026-06-08

---

## 1. Sub-Systems

| # | Sub-System | Function | Safety Criticality |
|---|-----------|----------|--------------------|
| 1 | **Mould** | Initial solidification shell formation; copper plates + water cooling channels | CRITICAL |
| 2 | **Oscillation System** | Prevents shell sticking to copper via sinusoidal/non-sinusoidal oscillation | HIGH |
| 3 | **Strand Guide Segments** (0–N segments after mould exit) | Support, contain, and progressively cool the solidifying strand; rolls apply gentle soft-reduction force | HIGH |
| 4 | **Secondary Cooling Spray Zones** (Zones 1–8+ depending on machine length) | Air-mist or water spray nozzles control strand surface temp profile | HIGH |
| 5 | **Withdrawal & Straightener Unit** | Pulls strand at controlled casting speed; straightens curved strand to horizontal | HIGH |
| 6 | **Tundish** | Intermediate vessel between ladle and mould; controls flow, temperature buffer, inclusion removal | HIGH |
| 7 | **Ladle Turret** | Rotates ladles over tundish; enables sequence casting without interruption | MEDIUM–HIGH |
| 8 | **SEN / Submerged Entry Nozzle** | Delivers steel from tundish into mould below meniscus; controls flow symmetry | HIGH |
| 9 | **Torch Cutter / Runout Table** | Cuts solidified slab to length; conveys product | MEDIUM |

---

## 2. Parts Breakdown

### 2.1 Mould
- **Copper Plates** (broad-face ×2, narrow-face ×2 for slab casters): Ni-Co or CrNi-plated; initial thickness ~40–55 mm; scrap limit ~28–30 mm remaining
- **Mould Water-Cooling Channels**: Slots machined behind copper face; water flow ~2,500–4,000 L/min per face
- **Mould Thermocouples**: Embedded at 2–4 rows, 20–40 per face (older), 80–160 per face (modern matrix arrays); Type-K or Type-T; response time < 1 s [Source: PMC9780797]
- **Mould Taper**: Narrow-face plates tilted inward ~1–1.4%/m to match strand shrinkage; monitored per sequence

### 2.2 Oscillation System
- **Eccentric Drive / Hydraulic Servo Actuator**: Generates sinusoidal or non-sinusoidal stroke
- **Linear Position Transducer (LVDT)**: Measures actual stroke displacement
- **Load Cells / Force Sensors**: Monitor oscillation table bearing load
- **Oscillation Table Frame, Guide Columns, Leaf Springs** (hydraulic systems): Wear items inspected per campaign

### 2.3 Segment Rolls & Bearings (per segment, 2–14 roll pairs)
- **Segment Rolls**: Cast alloy steel; surface hardness 55–65 HRC; diameter ~150–250 mm; subject to thermal fatigue and wear
- **Segment Roll Bearings**: Spherical roller bearings (SRB) in sealed, water-cooled housings; grease or centralized oil lubrication; NSK, SKF, Timken are principal suppliers [Source: nsk.com/eu-en/2022]
- **Segment Frame / Tie Rods**: Structural; hydraulic cylinder actuated for soft-reduction and roll gap control
- **Hydraulic Cylinders**: Position-controlled; sensor = linear encoder on piston rod

### 2.4 Secondary Cooling Spray Nozzles
- **Air-Mist Nozzles**: Two-fluid (water + compressed air); typical water orifice 0.5–5.0 L/min; air pressure 1.5–3.0 bar [Source: Lechler lechlerusa.com]
- **Full-Cone Water Nozzles**: Pure water; pressure 1–7 bar; flow 5–50 L/min
- **Zone Isolation Valves + Flow Meters**: Per-zone control; flow measurement ±2% accuracy

### 2.5 SEN / Submerged Entry Nozzle
- **Alumina-Graphite Refractory Body**: 600–900 mm long; bore diameter ~40–80 mm
- **Preheating Shroud**: Heated to ~1,200°C before insertion to avoid thermal shock
- **Stopper Rod or Slide Gate**: Regulates steel flow from tundish through SEN

### 2.6 Tundish
- **Working Lining**: MgO or alumina-based refractory; thickness 70–120 mm; renewed every 4–10 heats
- **Stopper Rod**: Al₂O₃-graphite; primary flow control; tip erosion is primary wear mode
- **Impact Pad / Turbostop**: Ceramic insert at ladle stream impact point; reduces turbulence
- **Temperature Thermocouple (Immersion)**: Measures tundish steel temperature each heat

### 2.7 Ladle Turret
- **Rotating Arm + Hydraulic Drive**: 180° rotation; bearings and ring gear
- **Load Cells on Each Arm**: Measure ladle weight (used for metal weight calculation and leak detection)
- **Hydraulic Tilt Cylinders**: For ladle opening/closing
- **Emergency Drive (battery-backed)**: Safety system for ladle positioning if power fails

---

## 3. Sensors — Types + Most Common

| Sensor | Location | Principle | Measurement | Most Common? |
|--------|----------|-----------|-------------|-------------|
| **Mould Thermocouples** | Embedded in copper plate, 2–4 row matrix | Thermoelectric (Type-K/T) | Copper plate temperature (°C) | #1 most critical |
| **Mould Level Sensor** | Top of mould | Eddy-current or radioactive (Co-60) or laser | Meniscus level (mm from top) | #2 most critical |
| **Oscillation Displacement (LVDT)** | Oscillation table | Linear variable differential transformer | Stroke position (mm) | Frequent |
| **Segment Roll-Gap Encoder** | Hydraulic cylinder piston | Linear encoder | Roll gap (mm) | Frequent |
| **Hydraulic Pressure Transducer** | Segment hydraulic circuit | Piezoelectric | Pressure (bar) | Frequent |
| **Spray Zone Flow Meter** | Each cooling zone header | Electromagnetic or Coriolis | Water flow rate (L/min) | Frequent |
| **Spray Zone Pressure Sensor** | Zone inlet | Diaphragm pressure | Bar | Frequent |
| **Strand Surface Pyrometer** | Between segments | Infrared | Surface temperature (°C) | Moderate |
| **Segment Bearing Vibration** | Roll bearing housing | Accelerometer | Acceleration (g), velocity (mm/s) | Growing use |
| **Stopper Rod Position** | Tundish rod actuator | Linear encoder | Position (mm) = clogging proxy | Frequent |
| **Tundish Weight Load Cells** | Ladle turret arm | Strain gauge | Steel weight (tonnes) | Standard |
| **Tundish Temperature TC** | Immersion / submerged | Type-S thermocouple | Steel temperature (°C) | Standard |
| **Casting Speed Encoder** | Withdrawal drive motor | Rotary encoder | Speed (m/min) | Standard |
| **Mould Water Temperature** | Inlet + outlet per face | RTD (Pt-100) | Delta-T = heat extraction rate (°C) | Standard |
| **Mould Water Flow** | Supply header | Electromagnetic | L/min | Standard |

---

## 4. Normal Operating Readings

### 4.1 Mould Thermocouples
- **Normal range:** 100–250°C at copper hot face (back-plate reading; actual copper face up to 350°C)
- Typical gradient top → bottom: higher at meniscus (~200–250°C), decreasing to ~100–130°C at mould exit
- **Upper TC reads higher than lower TC** during stable casting — this is the baseline polarity
- Temperature fluctuation acceptable: ±15°C around rolling mean [Source: iFactory / PMC9780797]
- Max hot-face temperature before sticking risk: >350°C [Source: ispatguru.com breakout article]
- Thermocouple failure signatures: stuck at 300°C (upper TC fault) or 0°C reading (lower TC fault) [PMC9780797]

### 4.2 Mould Level
- **Control setpoint:** Typically 80–120 mm below top of mould
- **Allowable fluctuation:** ±3 mm from setpoint during stable casting [Source: iFactoryApp]
- Level sensor accuracy: ±1 mm (eddy-current type) [Source: sert-metal.com]
- Measuring range: 0–300 mm below mould top [Source: sert-metal.com]

### 4.3 Oscillation
- **Stroke:** 2–10 mm (most slab casters 4–8 mm); billet casters can run 3–6 mm
- **Frequency:** 60–200 cpm (cycles per minute); hydraulic servo casters auto-track casting speed; sinusoidal waveform standard; non-sinusoidal used for high-speed AHSS
- **Negative Strip Time (NST):** Target 0.10–0.15 s; deviation ±10 ms is alarm threshold
- **Stroke deviation alarm:** <2% of set stroke [Source: iFactoryApp segment analytics]
- Typical casting speed for slab: 0.8–1.8 m/min (AHSS up to 2.5 m/min)

### 4.4 Roll Gap
- Design gap: Equals slab thickness minus accumulated shrinkage taper (~200–260 mm for typical slab)
- **Max allowable deviation from design gap curve:** 0.5 mm [Source: oxmaint / Sarclad]
- Mould taper max deviation: ±0.3 mm [Source: oxmaint]

### 4.5 Secondary Cooling Spray Flow
- **Total specific water flow:** 1.2–2.5 L/kg of cast steel depending on steel grade [Source: Lechler PDF]
- Zone 1 (foot rolls, immediately below mould): Highest intensity; ~50–150 L/min per nozzle bank
- Water pressure at nozzle: 1–7 bar (water nozzles); air-mist water pressure >1.2 bar at 2–2.5 bar air [Source: ispatguru air-mist]
- **Acceptable flow variance:** ±10% from design [Source: oxmaint]

### 4.6 Tundish Temperature
- **Target superheat:** 15–35°C above liquidus (grade-dependent)
- Alarm low: <10°C superheat (risk of freeze, SEN clog)
- Alarm high: >40°C superheat (shell thinning risk, increased breakout probability; >25°C above target = 60% higher breakout risk) [Source: iFactoryApp breakout analytics]

### 4.7 Casting Speed
- Slab caster normal: 0.8–1.8 m/min
- Max speed triggers breakout risk — shell thinning at high v; automatic speed reduction when BRS > 80 [Source: iFactory BRS model]

---

## 5. Defect Readings — Failure Mode Thresholds

### 5.1 Sticker (Shell-Sticking) Breakout — Thermocouple Pattern
**Mechanism:** Solidified shell partially adheres to copper face → tears at meniscus → thin zone moves downward with casting → if uncorrected, shell ruptures below mould exit.

**Pattern (Temperature-Gradient Algorithm):**
1. Upper TC in affected column: **sharp temperature RISE** (+15°C above baseline in <10 s)
2. Same column lower TC (one row below): temperature initially stable, then also rises as sticker moves down
3. As sticker descends: upper TC temperature **drops sharply** (shell re-solidifies above), lower TC **rises**
4. **Temperature polarity REVERSAL**: upper TC < lower TC in affected column (differential goes negative) = strong alarm [Source: PMC9780797]
5. Gradient rate alarm: >2.20°C/s rise rate = alarm trigger [Source: PMC9780797]
6. Minimum alert gradient: 0.18°C/s (below this = noise floor) [Source: PMC9780797]
7. Sticker velocity (Ss = Dv/tv) must be < casting speed for confirmed alarm vs. false positive

**Response window:** Sticker detection to strand arrest: 2–5 minutes [Source: iFactoryApp]  
**BRS thresholds:** Advisory BRS>65, auto speed-reduce BRS>80, emergency BRS>92 [Source: iFactoryApp]

### 5.2 Mould Level Instability
- Normal: ±3 mm from setpoint
- **Alert threshold:** ±5 mm deviation persisting >3 s
- **Alarm:** ±10 mm (auto casting speed reduction triggered)
- **Emergency:** ±15 mm or level rate of change >3 mm/s → automatic emergency stop
- Cause: SEN clogging (level drops as flow reduces), stopper rod erosion (level rises, flow uncontrolled), slag entrapment, Ar gas flow asymmetry

### 5.3 SEN Clogging — Stopper Rod / Slide Gate Position Signal
- Normal: Stopper position drifts gradually downward over heat as steel flows; smooth monotonic trend
- **Clogging signature:** Stopper rod position INCREASES (opens wider) to maintain flow → equivalent flow reduction at same opening = clogging index rise [Source: Girase et al., Journals Sagepub]
- **Nozzle Clogging Index (NCI):** Derived from stopper rod opening vs. expected flow model; NCI > threshold triggers scheduled SEN change
- DNN/ConvLSTM models now used for clogging detection from time-series stopper position + level data [Source: ScienceDirect 2023 S095741742302465X]
- Clinically: SEN lifetime 1–4 heats for Al-killed steel (worst clogging grades); 6–12 heats for clean grades

### 5.4 Spray Nozzle Clogging
- **Alert threshold:** Flow <15% below design for any zone [Source: iFactoryApp]
- **Blockage rate:** 40% of secondary cooling nozzles develop partial or full blockage within 6 months without structured maintenance program [Source: oxmaint]
- Detection: Zone-level flow meter drops + pressure differential rises
- Consequence: Local surface temperature spike → transverse surface cracks in slab → quality reject

### 5.5 Segment Roll Bearing Seizure
- **Vibration precursor:** Bearing defect frequency amplitude rising >6 dB above baseline in velocity spectrum (mm/s)
- Temperature rise: >20°C above adjacent bearing housing = early thermal alarm
- **Seized roll:** Driving torque spike on withdrawal drive motor current (3–5× normal); striation marks on slab surface; roll stop confirmed by rotation sensor dropout
- Detection lag without digital tracking: 18–24 h between onset and visible slab defect [Source: oxmaint segment analytics]

### 5.6 Mould Copper Plate Wear / Heat Checking
- **Normal groove depth at meniscus:** <0.3 mm
- **Plan-for-change threshold:** 0.3–0.5 mm groove depth
- **Immediate change required:** >0.5 mm groove depth [Source: oxmaint copper lifecycle page]
- Heat checking (thermal fatigue cracks): Visible cracks > 2 mm depth = immediate condemnation
- Nickel plating wear-through: Copper surface exposed → sticking risk → campaign end

### 5.7 Oscillation System Drift
- Stroke deviation > 2% of set value = alarm [Source: iFactoryApp]
- Frequency error > 5 cpm at set speed = maintenance flag
- NST deviation > ±20 ms = quality risk (mark depth on slab changes → surface cracks)
- Bearing or guide wear in eccentric drive causes amplitude reduction and phase lag

### 5.8 Tundish Lining Failure / Skull
- Lining thermocouples (shell T/C): T rise >50°C on outer steel shell = hot spot = lining breach warning
- Steel skull formation: tundish weight model detects >2 t unaccounted residual after sequence end
- Stopper rod tip erosion: Flow hysteresis increases — same position gives different flow rates across heats

---

## 6. Failure Modes — Taxonomy + Earliest Signs

### FM-01: BREAKOUT (Catastrophic) — Safety Class 1
**Definition:** Liquid steel escapes through thin/ruptured shell below mould exit; pours onto strand guide, rollers, and basement.  
**Types:** Sticker (75–80%), crack-type (15–20%), scum/inclusion entrapment (~5%) [Source: ispatguru breakout article]  
**Earliest signs:**
- Sticker type: Upper mould TC temperature rise + polarity reversal (2–5 min warning window)
- Crack type: Mould level disturbance + shell friction signal spike + tundish superheat deviation
- Both: BRS score climbing toward 80+

**Severity:** Molten steel flood → fire risk, personnel safety, equipment destruction  
**Frequency:** Industry average 0.3–0.8 breakouts per caster per year (reactive plants); drops to ~0.05 with mature BPS systems [unverified aggregate]

### FM-02: Mould Thermocouple Failure
**Signs:** TC reads constant 300°C (upper fault) or 0°C (lower fault) or implausible step change [PMC9780797]  
**Impact:** BPS blind spot in failed column — breakout risk window unmonitored  
**Action:** Redundant TC matrix cross-validation flags faulty TC; mark as failed; reduce casting speed; plan mould change at next opportunity

### FM-03: SEN Clogging
**Earliest signs:** Stopper rod opening increases to compensate flow drop; NCI index rising; mould level slight fall + asymmetric flow (EMF sensor on mould shows asymmetric meniscus)  
**Progression rate:** Fast for Al-killed steel (can clog within 30 min of heat start)  
**Action:** Argon purging through SEN as immediate measure; SEN change at ladle exchange window

### FM-04: Segment Roll Seizure (Bearing Failure)
**#1 cause of unplanned caster stoppages** [Source: oxmaint]  
**Earliest signs:** Vibration envelope increase at bearing defect frequencies (BPFO/BPFI); bearing housing T rise; withdrawal motor current increase  
**Roll life:** 10,000–50,000 heats depending on segment position (foot-roll area shortest) [Source: oxmaint segment maintenance]  
**Bear life improvement:** NSK reported 2× bearing life extension in CCM application with new bearing design [Source: nsk.com 2022]

### FM-05: Spray Nozzle Clogging
**Earliest signs:** Zone flow meter reading 10–15% below design at same supply pressure  
**Root cause:** Scale / iron oxide particles + biological fouling in recirculated water system  
**MTBF without PM:** 40% partial/full clog within 6 months [Source: oxmaint]  
**Consequence:** Local surface cracking → slab downgrade or crop

### FM-06: Oscillation Drift
**Signs:** LVDT stroke amplitude deviation >2%, frequency lag vs. speed setpoint, mark depth variation on slab surface  
**Root cause:** Eccentric drive bearing wear, spring fatigue (mechanical oscillators), servo valve wear (hydraulic)  
**Consequence:** Irregular oscillation marks → surface cracks; sticking risk from loss of negative strip

### FM-07: Mould Wear / Heat Checking
**Signs:** Post-campaign groove depth measurement >0.3 mm at meniscus; visual crack inspection post-sequence  
**Plating campaign lengths:** Cr: 100–150 heats; Ni: ~300 heats; Ni-Co: 500–800 heats [Source: oxmaint copper lifecycle]; Record: 627 heats (Nucor Crawfordsville)  
**Consequence:** Sticking → sticker breakout; groove → longitudinal slab crack

### FM-08: Tundish Lining Breach / Skull
**Signs:** Outer-shell thermocouple T rise >50°C; residual metal weight after sequence; stopper hysteresis change  
**Consequence:** 25–35% of total caster downtime attributed to turret + tundish failures [Source: oxmaint ladle turret]  
**Single event cost:** $200K–$500K [Source: oxmaint]

---

## 7. Repair / Resolution Process

### Mould Change
- **Trigger:** Campaign end (Ni: ~300 heats; Ni-Co: ~500–800 heats), groove >0.5 mm, heat crack, emergency breakout damage
- **Planned changeover time:** 2–4 hours (mould swap + realign + water leak test + TC check)
- **Emergency (post-breakout):** 12–24 h + cleanup of solidified steel in guide segments
- **Refurbishment cycles:** 5–8 per copper plate set before plate is scrapped [Source: oxmaint copper lifecycle]

### Segment Change
- **Trigger:** Accumulated roll-gap deviation, bearing inspection finding, campaign schedule
- **Campaign interval:** Typically >2 years target; shorter for high-tonnage or foot-roll segments [Source: Primetals roll reconditioning]
- **Planned segment replacement time:** Previously ~20 h; improved designs (Primetals) reduce to ~10 h [Source: oxmaint search result / nsk 2022]
- **Roll reconditioning:** Surface re-grinding + hard-chrome or laser-clad rebuild at dedicated workshop
- **Strategy:** Keep parallel stock of reconditioned segments for rapid swap; minimize cold caster time

### SEN Change
- **Frequency:** 1–4 heats (Al-killed steel) to 6–12 heats (clean grades)
- **Change time:** 3–5 min during ladle exchange window (planned); emergency during sequence = sequence abort
- **Argon purging:** 2–5 NL/min through SEN port as anti-clogging measure (continuous or pulsed)

### Spray Nozzle Maintenance
- **Inspection/replacement interval:** Every 6 months recommended; visual inspection + flow test each campaign [Source: oxmaint water treatment]
- **Cleaning method:** High-pressure water or mechanical de-scaling; nozzle replacement if orifice deformed
- **Time per zone:** ~1–2 h per zone during planned caster cold maintenance window

### Breakout Recovery
1. Emergency strand arrest (auto) + water flood of guide area
2. Solidified steel (skull) removal from segments: 6–12 h mechanical + thermal cutting
3. Segment inspection and roll replacement if damaged
4. Mould change if copper plates damaged
5. Full water leak test + TC check on all segments
6. Total outage from breakout to restart: **12–24 h typical; up to 48–72 h for severe events** [Source: iFactoryApp; oxmaint]
7. Restart requires full dummy bar thread-up

---

## 8. Cost / Loss Impact

| Event | Direct Cost | Downtime | Notes |
|-------|------------|----------|-------|
| **Breakout (severe)** | $4–8 M (total including lost production, equipment damage, cleanup) [Source: oxmaint] | 12–72 h; avg 48–96 h [Source: iFactoryApp] | Safety Class 1; injury/fatality risk; steel pour onto hot equipment = fire |
| **Breakout (moderate)** | $1.8–4.5 M [Source: iFactoryApp] | 48–96 h | Even "minor" breakout = significant event |
| **Steel loss per breakout** | 50–300 t liquid steel lost | — | At ~₹50,000/t billet = ₹2.5 Cr–₹15 Cr steel loss alone [unverified — indicative at current prices] |
| **Caster restart after breakout** | Avg 3–4 h restart quoted; full recovery 12–24 h [Source: PMC8778296 / NCM paper] | — | |
| **Tundish skull / turret failure** | $200K–$500K [Source: oxmaint ladle turret] | 4–8 h | |
| **Unplanned segment bearing failure** | €14,850/event in documented bearing case [Source: nsk.com 2022] — but total with lost production >> this | 4–10 h per segment change | |
| **Annual caster availability — reactive PM** | Equipment availability 84–86% [Source: oxmaint] | 12–15 unplanned stops/yr × 4–8 h each | |
| **Annual caster availability — predictive PM** | Equipment availability 92–94% [Source: oxmaint] | 4–6 residual unplanned stops/yr | 30–40% reduction in unplanned stoppages [Source: oxmaint] |
| **Spray nozzle PM program** | Baseline investment ~$88K–$175K for 2-strand caster BPS system [Source: iFactoryApp] | — | Pays back vs. one breakout avoided |

**BPS (Breakout Prevention System) value:** Single breakout avoidance = $1.8–$4.5 M; annual 2-strand value ~$2.1 M from combined breakout + quality improvement [Source: iFactoryApp]. Reduction in breakout rate: up to 94% documented [Source: iFactoryApp].

---

## 9. Additional Notes

### 9.1 Measurement Architecture for ML/AI PdM
- **Thermocouple sampling rate:** 1-second intervals (standard); modern systems 100–500 ms [Source: iFactoryApp]
- **BPS system update frequency:** Every 10 seconds for BRS score [Source: iFactoryApp]
- **Sensor count per strand:** 200–500 signals (TCs + level + flow + gap + speed + pressure) — rich multivariate time-series
- **Detection method evolution:** Rule-based (threshold logic, 1990s) → pattern recognition algorithms → ANN (PMC8778296) → GA-BP hybrid → ConvLSTM for SEN clog (ScienceDirect 2023) → integrated BRS with multi-model ensemble

### 9.2 Data Availability for ML Models
- **Public datasets:** Sparse; most plant data proprietary; academic papers use anonymized sets from 1–5 plants
- **Typical dataset size for breakout model:** 500–2,000 heats; sticker events 5–50 per dataset (imbalanced — false negative cost >> false positive cost)
- **Key challenge:** Class imbalance (breakout is rare), sensor dropout, grade-change confounds, varying casting speed

### 9.3 Operating Parameter Interdependencies (Reward Shaping Caution)
- Casting speed ↑ → productivity ↑ but breakout risk ↑ + segregation ↑
- Spray cooling intensity ↑ → surface crack risk ↑ (thermal stress) but centerline segregation ↓
- Tundish superheat ↑ → SEN clog ↓ but shell thinning risk ↑
- These create non-monotonic reward surfaces — naive RL reward shaping dangerous; safety constraints must be hard, not soft

### 9.4 Competitive Technology References
- **Primetals LevMon:** Eddy-current mould level sensor system — ±1 mm, 0–300 mm range [primetals.com]
- **SMS Group:** Strand condition monitors + roll gap measurement sleds [sms-group.com]
- **Sarclad:** Strand Condition Monitor — roll gap, roll rotation, alignment per segment [docplayer sarclad]
- **Lechler / Spraying Systems:** Secondary cooling nozzle design + clogging study tools [lechlerusa.com]
- **ConvLSTM for SEN clog:** First fully data-driven approach, 2023 [ScienceDirect S095741742302465X]
- **XGBoost BPS at 0.65 threshold:** 99.5% accuracy, 100% sticker detection [PMC9780797]

### 9.5 Tata Steel Context [unverified unless sourced]
- Tata Steel IJmuiden (Netherlands) operates slab casters producing ~7 Mtpa; Port Talbot historically ran 4-strand slab casters (now in transition to EAF route 2026)
- Tata Steel India (Jamshedpur, Kalinganagar) — slab + bloom + billet casters; Kalinganagar is largest greenfield integrated plant built post-2015 in India
- Any "Tata Steel uses X breakout system" claims require plant-specific public source — not verified here

---

## Sources

- [An Intelligent Logic-Based Mold Breakout Prediction System (PMC)](https://pmc.ncbi.nlm.nih.gov/articles/PMC9780797/)
- [Productivity Enhancement via ANN Breakout Prediction (PMC)](https://pmc.ncbi.nlm.nih.gov/articles/PMC8778296/)
- [iFactoryApp — Continuous Casting Machine Analytics & Breakout Prevention](https://ifactoryapp.com/industries/steel-plant/continuous-casting-machine-analytics-breakout-prevention)
- [iFactoryApp — Continuous Caster Analytics: Mold, Segments & Strand Guide](https://ifactoryapp.com/industries/steel-plant/continuous-caster-analytics-mold-segments)
- [Oxmaint — Caster Mold Maintenance Tracking](https://oxmaint.com/industries/steel-plant/caster-mold-maintenance-tracking)
- [Oxmaint — Slab Caster Mold Copper Plate Lifecycle Management](https://oxmaint.com/industries/steel-plant/slab-caster-mold-copper-plate-lifecycle-management)
- [Oxmaint — Continuous Caster Maintenance: Mold, Segments & Strand Guide](https://oxmaint.com/industries/steel-plant/continuous-caster-maintenance-mold-segments)
- [Oxmaint — Ladle Turret and Tundish Maintenance Optimization](https://oxmaint.com/industries/steel-plant/ladle-turret-tundish-maintenance-optimization-casting-oee)
- [Oxmaint — Continuous Casting Water Treatment & Secondary Cooling](https://oxmaint.com/industries/steel-plant/continuous-casting-water-treatment-secondary-cooling)
- [IspatGuru — Breakouts During Continuous Casting of Liquid Steel](https://www.ispatguru.com/breakouts-during-continuous-casting-of-liquid-steel/)
- [IspatGuru — Air Mist Cooling in Continuous Casting](https://www.ispatguru.com/air-mist-cooling-in-continuous-casting/)
- [Primetals LevMon — Mold Level Sensor System](https://www.primetals.com/en/portfolio/solutions/continuous-casting/levmon-mold-level-sensor-system/)
- [Primetals — Extra Long-Life Bearing Unit for Continuous Casters](https://www.primetals.com/en/portfolio/solutions/continuous-casting/extra-long-life-bearing-unit/)
- [Primetals — Continuous Caster Roll Manufacturing and Reconditioning](https://www.primetals.com/en/portfolio/solutions/continuous-casting/continuous-caster-roll-manufacturing-and-reconditioning/)
- [NSK — Doubles Bearing Life in Continuous Casting Application (2022)](https://www.nsk.com/eu-en/company/news/2022/nsk-doubles-bearing-life-in-continuous-casting-machine-applicati/)
- [Lechler — Precision Spray Nozzles for Secondary Cooling](https://www.lechlerusa.com/fileadmin/media-usa/Literature/Brochures/metal/Continuous_Casting_-_Secondary_Cooling.pdf)
- [Lechler — Spray Nozzles for Secondary Cooling in Continuous Casters](https://www.lechlerusa.com/en/applications/secondary-cooling-continuous-casting)
- [ScienceDirect — Deep Neural Networks for SEN Clogging Detection (ConvLSTM, 2023)](https://www.sciencedirect.com/science/article/abs/pii/S095741742302465X)
- [ResearchGate — Development of Nozzle Clogging Index for Continuous Slab Casting](https://www.researchgate.net/publication/277006010_Development_and_Application_of_Nozzle_Clogging_Index_to_Improve_the_Castability_in_Continuous_Slab_Casting)
- [Metals 2025 — Impacts of Cooling Reduction Due to Spray Nozzle Clogging on Shell Formation](https://doi.org/10.3390/met15101107)
- [Sert-Metal — Electromagnetic Mould Level Sensor](http://www.sert-metal.com/continuous-casting/electromagnetic-mould-level-sensor.html)
- [SMS Group — Rugged Roll Gap Sleds](https://www.sms-group.com/en-us/insights/all-insights/rugged-roll-gap-sleds)
- [InTechOpen — Optimization of Oscillation Parameters in Continuous Casting (PDF)](https://cdn.intechopen.com/pdfs/10931/InTech-Optimization_of_oscillation_parameters_in_continuous_casting_process_of_steel_manufacturing_genetic_algorithms_versus_differential_evolution.pdf)
