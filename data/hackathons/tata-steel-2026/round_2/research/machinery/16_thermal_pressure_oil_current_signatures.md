# Sensor Signatures Reference — Temperature, Pressure, Flow, Oil Analysis, MCSA
## Process & Electrical Condition-Monitoring for Steel-Plant PdM
*Research compiled: 2026-06-08 | For Tata Steel Round 2 — Maintenance Wizard*

---

## 1. TEMPERATURE SENSORS

### 1.1 Sensor Types, Measurement & Units

| Sensor | Principle | Range | Accuracy | Sampling |
|--------|-----------|-------|----------|----------|
| RTD (PT100/PT1000) | Resistance varies with T | -200°C to +660°C | ±0.1–0.5°C | 1–10 Hz (continuous SCADA) |
| Type K Thermocouple | Seebeck effect | -50°C to +1260°C | ±1–2°C | 1–10 Hz; faster transient response |
| Type J Thermocouple | Seebeck effect | -40°C to +750°C | ±1–2°C | 1–10 Hz |
| Infrared (IR) Thermography | Planck radiation | -20°C to +2000°C | ±1–2°C or ±2% | Periodic scan (quarterly–monthly) |

**Why RTD for PdM bearings:** Fault signatures appear as 3–8°C deviations from baseline. RTD accuracy ±0.1–0.5°C resolves these; thermocouple ±2°C would obscure them. [source: temp-pro.com]

### 1.2 Normal Operating Ranges (Healthy)

#### Rolling-Element Bearings (steel plant motors, pumps, gearboxes)
- **Healthy operating range:** 40–80°C (housing surface)
- **Typical steady-state:** 50–70°C at rated load, ambient 25–40°C
- **Sleeve bearings (EASA large motor standard):** Normal ≤ 80°C
- **Rule of thumb:** Operating temperature should not exceed ambient + 40°C rise without investigation

#### Motor Winding Temperature by Insulation Class (IEC 60034-1)
| Class | Max Rated T | Practical Alarm | Practical Trip |
|-------|-------------|-----------------|----------------|
| B | 130°C | 120°C | 130°C |
| F (most industrial) | 155°C | 130°C | 145°C |
| H (high-duty) | 180°C | 155°C | 175°C |

*Class F note: At rated load in 40°C ambient, allowable rise = 105°C → max operating = 145°C, leaving 10°C hot-spot margin to insulation limit of 155°C. [source: motioncontroltips.com, quantum-controls.co.uk]*

#### Hydraulic Oil Temperature
- Normal: 35–55°C in circuit return line
- Maximum continuous: 60°C (above this viscosity drops, oxidation accelerates)
- Mineral oil ignition risk begins: 150–170°C [source: oxmaint.com steel hydraulics]

### 1.3 Defect Readings — Bearings (RTD)

| Stage | Temperature | Rate of Change | Action |
|-------|-------------|----------------|--------|
| Healthy | 40–80°C | < 1°C/hour steady-state | Monitor |
| Warning / Caution | 80–90°C OR +10°C above established baseline | > 2°C/hour | Inspect lubrication, check alignment |
| Alarm | 90–100°C | > 5°C/hour | Reduce load, plan shutdown |
| Trip | ≥ 100–105°C | Rapid rise | Immediate shutdown |

**Rate-of-change rule (industry-standard PdM practice):** A bearing temperature rise >10°C above the running baseline is a caution; rise >2°C/hour is an alarm trigger regardless of absolute value. [source: reliableplant.com SKF tips, plcdcspro.com API 670 guide]

**API 670 setpoints (rotating machinery per IEC/API standards):**
- Low alarm: 70°C
- High alarm: 85°C
- High-high trip: 105°C
- Alarm delay: 3 seconds (prevents nuisance startup trips) [source: plcdcspro.com]

#### Winding Temperature Fault Progression
- Normal: ≤ alarm threshold for class
- Early fault (single-phase overload, blocked ventilation): +15–25°C above baseline
- Winding insulation degradation begins: sustained >10°C above rated rise
- **Every 10°C above rated temperature halves insulation life** (Arrhenius rule — widely cited in motor industry)

### 1.4 Thermography (IR) — ΔT Severity Classification

**Standard:** ISO 18434-1:2008 (general procedures); NETA MTS (electrical equipment)

| ΔT (relative to similar phase or reference) | Classification | Action |
|---------------------------------------------|----------------|--------|
| 1–3°C | Possible deficiency | Document, investigate at next opportunity |
| 4–15°C | Probable deficiency | Schedule repair within next planned outage |
| > 15°C | Serious deficiency — Caution | Prioritise for near-term repair |
| > 30°C | Critical / Immediate hazard | Take offline at earliest safe opportunity |

[Source: NETA MTS via oxmaint.com thermographic inspection; ISO 18434-1 iso.org]

**Phase-to-phase comparison is preferred** over phase-to-ambient for electrical equipment because it eliminates environmental variability.

**Steel plant applications:**
- Transformer hot-spot winding: ΔT > 20°C above top oil = caution; > 40°C = alarm (IEC 60076 loading guide)
- Busbars / cable joints: ΔT > 10°C = investigate; > 30°C = immediate
- Motor housing hot-zones on stator end-turns visible externally: ΔT > 15°C indicates phase imbalance or shorted turns
- Bearing housing IR scan: ΔT > 10°C between DE and NDE bearing = suspect DE bearing damage

### 1.5 Sensor Fault / False-Alarm Issues (Temperature)

| Issue | Cause | Symptom | Fix |
|-------|-------|---------|-----|
| RTD drift | Thermal cycling oxidises platinum leads | Gradual offset, reads 3–10°C high/low | Annual recalibration for critical loops |
| Thermocouple inhomogeneity | Extension wire mismatch | Step-change error | Verify extension wire type matches TC type |
| Cold-junction error | CJC chip not tracking ambient | Systematic offset = ambient error | Verify CJC board calibration |
| Ground loop | Multiple ground paths on TC | Noisy signal, oscillations | Use isolated transmitter inputs |
| Poor thermal contact | Loose mounting, no thermal paste | Reads ambient not bearing temp | Torque sensor to spec, use paste |
| Ambient compensation | IR camera in high-radiant steel environment | Emissivity mismatch inflates readings | Set correct emissivity (steel ε≈0.7–0.85 oxidised) |

---

## 2. PRESSURE & DIFFERENTIAL-PRESSURE SENSORS

### 2.1 Measurement & Units
- **Absolute pressure:** kPa, bar, psi (1 bar = 100 kPa = 14.5 psi)
- **Gauge pressure:** bar(g) — relative to atmosphere
- **Differential pressure (dP):** bar or mbar — across valve, orifice, or filter element
- **Sampling rate:** 10–100 Hz for dynamic systems (servo); 1 Hz adequate for slow process monitoring

### 2.2 Normal Ranges (Steel Plant Hydraulics)

| Circuit | Normal Range | Notes |
|---------|-------------|-------|
| AGC servo system (rolling mill) | 250–300 bar | Millisecond-response cylinders; sensors rated 0–1000 bar |
| Converter / furnace tilting | 150–200 bar | Lower duty, slower response |
| General hydraulic power pack supply | 150–250 bar | Typical industrial band |
| Lubrication circuit supply | 2–8 bar | Low-pressure oil delivery |
| Filter dP (clean element) | 0.3–0.8 bar | Baseline at operating viscosity and flow |
| Cooling water circuit | 2–6 bar | Plant-specific design |

[Source: oxmaint.com steel hydraulics, blog.gamicos.com AGC pressure sensors]

### 2.3 Defect Readings — Hydraulic Pressure

| Fault | Pressure Signature | Threshold | Action |
|-------|-------------------|-----------|--------|
| Filter clogged | dP rising toward bypass | dP > 1.0–1.5 bar = warning; element bypass opens ~3–5 bar | Replace filter element; continued bypass = contamination crisis |
| Pump wear / cavitation | Supply pressure drops + fluctuates | >10% below setpoint = cavitation risk | Check inlet line, oil level, pump case |
| Internal leakage (seal wear) | Cylinder position drift under load | AGC: position drift > 0.05 mm from setpoint | Servo valve response test; seal replacement |
| Servo valve stiction | Erratic pressure with hunting | Response time >5% deviation from baseline | Flush; replace valve if contamination-induced |
| Accumulator nitrogen loss | Pressure spike then sag on demand | Nitrogen pre-charge < 70% of working pressure | Recharge nitrogen; check bladder |
| Burst / pipe crack | Sudden pressure drop to near-zero | Any drop > 50% in < 1 second | Emergency shutdown |

**Filter dP Rule:** Clean filter dP ~ 0.3–0.8 bar. Replace when dP > 1 bar (clogged indicator). At dP > 3–5 bar, bypass valve opens — unfiltered oil circulates, ISO code degrades rapidly. [Source: internormenfilters.com, mpfiltri-filters.com]

### 2.4 Trending: Healthy → Failure

```
Clean filter:  dP 0.3 bar → gradual rise over weeks → dP 1.0 bar (replace) → ignored → 3 bar bypass → ISO code rises 2+ steps → servo valve stiction → position error → strip gauge deviation
```

### 2.5 False-Alarm Issues (Pressure)

| Issue | Cause | Effect |
|-------|-------|--------|
| Cold-start high dP | Oil viscosity high at low temp | False clog alarm; use temperature-compensated alarm enable |
| Pressure transducer drift | Fatigue on Bourdon tube; process vibration | Zero/span drift ±1–3 bar; annual calibration |
| Water hammer false spike | Valve closing too fast | High instantaneous pressure reading; use damped snubber |
| Impulse line blockage | Sediment in impulse lines | Wrong reading, slow response | Flush lines; use diaphragm seal |

---

## 3. FLOW SENSORS

### 3.1 Measurement & Units
- Volumetric flow: L/min, m³/h
- Mass flow: kg/s (Coriolis)
- Technology: electromagnetic (conductive fluids), ultrasonic (clamp-on), Coriolis, turbine, differential-pressure orifice
- Sampling rate: 1–10 Hz typical; Coriolis can reach 100+ Hz

### 3.2 Normal Operating Ranges (Steel Plant)

| Circuit | Normal Flow | Notes |
|---------|-------------|-------|
| Bearing oil lubrication (large mill roll) | 5–30 L/min per bearing | Design-specific |
| Hydraulic power pack return | 50–500 L/min | Scale with cylinder volume |
| Cooling water (roll gap spray) | 100–1000 m³/h | High-volume, low-pressure |
| Gearbox lubrication | 10–60 L/min | Gravity or forced-circulation |
| Compressed air to pneumatic actuators | 20–200 Nm³/h | Process-dependent |

### 3.3 Defect Readings — Flow

| Fault | Flow Signature | Threshold | Action |
|-------|---------------|-----------|--------|
| Blocked nozzle / strainer | Flow falls below setpoint | >10% drop below nominal = caution; >20% = alarm | Inspect and clean strainer |
| Pump wear | Gradual flow decline + rising inlet vacuum | >15% decline from baseline at same pressure | Pump efficiency test |
| Internal bypass (worn valve seat) | Flow high with low pressure differential | Unexplained high flow at low demand | Pressure-flow curve test |
| Cooling water blockage | Flow fall + rising outlet temperature | Flow drop + ΔT > 5°C above normal = alarm | Flush circuit; check scale deposits |
| Air ingestion in hydraulic | Erratic flow, foaming | Flow fluctuation > ±20% + frothy return | Check breathers, seals |

**Steel plant historian context:** 5,000–15,000 monitoring points (OSIsoft PI, Honeywell PHD). Flow deviations flagged against 30-day rolling baseline ±2σ. [Source: oxmaint.com steel plant AI maintenance]

### 3.4 False-Alarm Issues (Flow)

| Issue | Cause |
|-------|-------|
| Entrained air in EM flow meter | Air bubble = spike reading; install upstream straight run |
| Ultrasonic clamp-on coupling loss | Poor gel, pipe scale — reads low; re-couple periodically |
| Reynolds-number shift | Viscosity change at temperature extremes — recalibrate or correct in DCS |

---

## 4. OIL ANALYSIS

### 4.1 What It Measures & Units
Oil analysis comprises multiple tests run on fluid samples, typically:
- **Elemental wear metals** (ICP-OES per ASTM D5185 or RDE per ASTM D6595): Fe, Cu, Pb, Sn, Al, Cr, Ni, Si, Na (ppm)
- **Particle counting / ISO 4406 code:** particles/mL at ≥4 µm, ≥6 µm, ≥14 µm
- **Ferrography (ASTM D7684):** particle morphology, size, shape — identifies wear mode
- **Viscosity (ASTM D445):** kinematic viscosity at 40°C and/or 100°C (cSt)
- **Total Acid Number / TAN (ASTM D664):** mg KOH/g — oxidation/degradation
- **Total Base Number / TBN (ASTM D2896):** mg KOH/g — remaining alkalinity (engine oils)
- **Water content (ASTM D1744 / Karl Fischer):** ppm or % v/v
- **Sampling interval:** monthly (routine), weekly (alarm state), after oil change + 50h run

### 4.2 Normal Readings (Healthy)

#### ISO 4406 Oil Cleanliness Codes
| System | Target Code | Meaning |
|--------|-------------|---------|
| AGC servo valves (rolling mill) | 15/13/10 | Very clean; servo valve requirement |
| General servo / proportional valves | 16/14/11 | Recommended per Donaldson/Parker |
| Standard hydraulic (piston pumps) | 18/16/14 | Typical industrial working standard |
| General lubrication circuits | 19/17/14 | Gearboxes, plain bearings |
| New oil from drum (unfiltered) | 21/19/16 | Requires pre-filtration before use |

*Each code step = 2× particle count. Going from 16→18 = 4× more particles.* [Source: hyprofiltration.com, oxmaint.com steel hydraulics]

#### Wear Metal Baselines (example populations — context-dependent)
| Metal | Source component | Typical industrial baseline | Caution | Action |
|-------|-----------------|----------------------------|---------|--------|
| Iron (Fe) | Gears, bearings, housings | Gearbox: < 50–100 ppm | 100–200 ppm | > 200 ppm or rapid trend rise |
| Copper (Cu) | Brass/bronze cages, bushings | < 30–55 ppm | 55–100 ppm | > 100 ppm |
| Lead (Pb) | Babbitt bearings, anti-wear EP additive breakdown | < 20 ppm | 20–50 ppm | > 50 ppm |
| Tin (Sn) | Babbitt bearing lining | < 10 ppm (steel mill bearing avg 7 ppm) | 10–25 ppm | > 35 ppm |
| Silicon (Si) | Airborne dirt ingestion | < 15 ppm | 15–30 ppm | > 30 ppm (indicates seal failure) |

*Note: Fixed-limit approach is inadequate. Trend rate matters more than absolute value. Context-specific baselines from equipment population are the gold standard. Iron >500 ppm may be normal in some high-contamination gearboxes; the same value may be alarming in a servo circuit.* [Source: machinerylubrication.com, windpowerengineering.com gearbox thresholds]

#### Viscosity Limits
| Deviation from ISO grade nominal | Condition | Action |
|----------------------------------|-----------|--------|
| Within ±10% | Normal | No action |
| ±10% to ±20% | Marginal | Investigate; drain interval review |
| > ±20% | Critical | Change oil; root-cause contamination or degradation |

[Source: machinerylubrication.com, machinerylubricationindia.com]

#### TAN (hydraulic/gear oil) Limits
- New hydraulic oil TAN: typically 0.1–0.5 mg KOH/g
- Action limit: TAN increase of **2× new oil value** OR absolute > 1.5–2.0 mg KOH/g for hydraulic oil
- Zinc-phosphorus (ZDDP) ratio dropping below 60% of new oil baseline = additive depletion alarm [Source: oxmaint.com oil analysis]

#### Water Content
- Hydraulic oil: < 0.05% (500 ppm) normal; > 0.1% (1000 ppm) = action
- Caster hydraulics (per oxmaint steel guide): < 200 ppm target

### 4.3 Defect Readings — Oil Analysis

| Fault | Oil Signature | Threshold / Rate Rule |
|-------|--------------|----------------------|
| Abrasive gear/bearing wear | Fe and Si rising together | Both trending up = external contamination ingestion; Si > 30 ppm = seal failure likely |
| Adhesive (scuffing) wear | Fe rising sharply; large particles in ferrography | Fe doubling in < 2 sample intervals = alarm |
| Babbitt bearing spalling | Sn + Pb rising together | Sn > 35 ppm = action (steel mill reference) |
| Copper bushing wear | Cu rising | Cu > 100 ppm = action |
| Oil oxidation | TAN rising; viscosity increasing | TAN 2× new value = oil change due |
| Water ingress | Water % up; rust particles in ferrography | > 1000 ppm water; foamy oil = immediate |
| Particle contamination spike | ISO code +2 or more steps | ISO code +2 = 4× particles = action; servo valve risk |

**Trend rule (ISO +2 codes):** Two steps jump in ISO 4406 code (e.g. 15/13/10 → 17/15/12) represents a 4× increase in particles — treat as action-level event requiring immediate filter check and source investigation. [Source: hyprofiltration.com, valin.com]

### 4.4 Trending: Healthy → Failure

```
ISO 15/13/10 (target) → particle ingress → 17/15/12 (+2 codes) → caution: filter inspection
→ 19/17/14 (+4 codes) → servo valve stiction begins → position error / strip gauge deviation
→ Fe trending up 10→50→150 ppm over 3 intervals → gear tooth fatigue confirmed
→ ferrography: large platelets (fatigue morphology) → scheduled replacement
→ ignored → catastrophic gear seizure
```

### 4.5 Standards
- **ISO 4406:2021** — Cleanliness codes
- **ASTM D5185** — ICP elemental analysis
- **ASTM D6595** — RDE rotating disc electrode wear metals
- **ASTM D445** — Kinematic viscosity
- **ASTM D664** — Total Acid Number
- **ASTM D7684** — Analytical ferrography
- **ASTM D6224** — In-service monitoring for power plant auxiliary equipment

### 4.6 False-Alarm Issues (Oil Analysis)

| Issue | Cause | Effect |
|-------|-------|--------|
| Contaminated sample bottle | Residual particles in collection container | Spurious particle count spike |
| Sample timing (cold start) | Wear particles settle; sample taken after drain = depleted | Under-reads wear metals |
| New oil baseline not set | First sample has no reference → trend impossible | Always sample at oil fill + 50h run |
| Mix-up of oil types | Different additive packages skew metals | Label samples with oil type + machine ID |

---

## 5. MOTOR CURRENT SIGNATURE ANALYSIS (MCSA)

### 5.1 What It Measures & Units
MCSA uses a **clamp-on current transformer** (CT) on any one stator phase lead to capture a time-series current waveform, then applies **FFT** (Fast Fourier Transform) to yield a current frequency spectrum. No motor shutdown required.

- **Measured quantity:** Phase current (A), frequency spectrum (Hz), sideband amplitude (dBc = dB below fundamental)
- **Sampling rate:** 10,000–20,000 Hz (10–20 kHz) per channel — sufficient to resolve sidebands at 0.1–10 Hz from 50 Hz fundamental
- **Applicable motors:** 3-phase AC induction motors, typically ≥ 50 HP (37 kW); 85% of industrial installations globally [Source: ifactoryapp.com, oxmaint.com MCSA guide]

### 5.2 Normal Readings (Healthy Motor)

| Parameter | Healthy Range | Notes |
|-----------|--------------|-------|
| Running current | 80–100% FLA (full-load amps) | Motor should operate 80–100% of nameplate FLA; <50% FLA = underloaded |
| Power factor (full load, large motors) | 0.85–0.92 lagging | Drops to 0.2–0.3 at no-load |
| Broken-rotor-bar sidebands (f ± 2sf) | −50 to −60 dBc | 50–60 dB below 50 Hz fundamental = healthy |
| Current THD | < 3–5% | Grid-induced harmonics; higher = suspect drive or grid issue |
| Phase current imbalance | < 2% | Per NEMA MG-1; >5% causes 25°C additional winding rise per 1% imbalance above 5% |

*f = line frequency (50 Hz India), s = slip ratio (0.01–0.05 at load), so sidebands appear at ~49.0–49.9 Hz and ~50.1–51.0 Hz.*

### 5.3 Defect Signatures (MCSA)

#### 5.3.1 Broken Rotor Bar
- **Signature:** Sidebands at **f ± 2sf** (lower and upper sideband around fundamental)
- **Frequency example (50 Hz, 3% slip):** sidebands at 47 Hz and 53 Hz
- **Severity scale:**
  | Condition | Sideband Level | Response |
  |-----------|---------------|----------|
  | Healthy | −50 to −60 dBc | Monitor |
  | 1–2 broken bars | −40 to −45 dBc | Monitor closely; plan inspection next planned outage |
  | Multiple broken bars / end-ring crack | −25 to −35 dBc | Plan shutdown within weeks; risk of rotor failure |
  | Imminent failure | > −25 dBc (< 25 dB below fundamental) | Urgent — remove from service |
- **Lead time before fracture propagates:** 4–8 months detectable by MCSA before catastrophic propagation [Source: maximomastery.com, oxmaint.com MCSA 2026]

#### 5.3.2 Bearing Faults (MCSA)
- **Mechanism:** Bearing defect creates periodic air-gap variation → flux modulation → current sidebands at f ± BPFO / f ± BPFI
- **BPFO (Ball Pass Frequency Outer Race):** geometry-dependent; typically 3–10× shaft frequency
- **BPFI (Ball Pass Frequency Inner Race):** typically 4–12× shaft frequency; shows ±1×, ±2× shaft-speed sidebands
- **Amplitude:** Typically 10–40 dB below noise floor of industrial current sensing — MCSA bearing detection requires clean signal; vibration sensors are preferred for early bearing detection
- **Lead time:** 3–6 months before catastrophic seizure detectable [Source: oxmaint.com MCSA 2026]

#### 5.3.3 Air-Gap Eccentricity
- **Static eccentricity:** mounting / frame misalignment; sidebands at **(1 ± nP/2) × f** where P = pole pairs, n = 1,2,3...
- **Dynamic eccentricity:** bent shaft or bearing wear; similar sidebands but rotating with shaft
- **Action:** Investigation when eccentricity sidebands appear > −40 dBc

#### 5.3.4 Stator Winding Fault (Inter-turn short)
- **Signature:** Negative-sequence current component increases; current imbalance > 2%
- **Phase current imbalance rule:** Each 1% imbalance above 5% adds ~25°C to winding temperature (NEMA rule)
- **Action:** Winding resistance test; megger test to confirm

#### 5.3.5 Overload / Underload
- **Overload:** Current > 105% FLA sustained = warning; > 115% FLA = overload alarm
- **Underload:** Current < 50% FLA at known load = suspect coupling failure or pump cavitation

### 5.4 Trending: Healthy → Failure

```
Healthy: sidebands at −55 dBc → 1 broken bar: −42 dBc (alert) → 2 bars: −38 dBc (plan shutdown)
→ 3 bars: −28 dBc (urgent) → end-ring crack: −20 dBc → rotor collapse
Timeline from first detection to catastrophic: 4–8 months typical
```

### 5.5 Which Faults MCSA Best Detects

| Fault | MCSA Sensitivity | Better Sensor |
|-------|-----------------|---------------|
| Broken rotor bar | EXCELLENT — primary method | — |
| Air-gap eccentricity | GOOD | — |
| Stator inter-turn short | GOOD (current imbalance) | Winding resistance test |
| Bearing fault | MODERATE (buried in noise) | Vibration (accelerometer) preferred |
| Overload / underload | EXCELLENT | — |
| Drive/grid harmonics | EXCELLENT | — |

### 5.6 False-Alarm / Calibration Issues (MCSA)

| Issue | Cause | Effect |
|-------|-------|--------|
| Variable-speed drive (VFD) masking | PWM carrier harmonics dominate spectrum | Broken-bar sidebands buried; MCSA less effective on VFDs |
| Light load = small slip | At < 30% load, 2sf sidebands too close to fundamental to distinguish | Use load >60% FLA for reliable MCSA |
| CT saturation | Oversized CT; poor turns ratio | Clipped waveform; false harmonics |
| EMI pickup | Long cable runs, unshielded | Noise floor rises, sidebands masked |
| Rotor bar count unknown | Wrong pole-pair / bar count for frequency prediction | Verify nameplate + rotor design |

---

## 6. SENSOR SELECTION MATRIX — FAULT vs. BEST SENSOR

| Fault | Best Sensor | Secondary |
|-------|-------------|-----------|
| Bearing inner/outer race wear | Vibration (accelerometer) | RTD bearing temp |
| Bearing lubrication failure | RTD (rapid temp rise) | Oil analysis (Fe trend) |
| Broken rotor bar | MCSA | Vibration |
| Winding insulation degradation | RTD winding temp | Thermography (IR) |
| Gear tooth fatigue/pitting | Oil analysis (Fe, ferrography) | Vibration |
| Hydraulic filter clogging | Differential pressure sensor | ISO 4406 (oil analysis) |
| Servo valve contamination/stiction | Differential pressure + flow | ISO 4406 |
| Hydraulic leak / pressure loss | Absolute pressure sensor | Flow sensor |
| Electrical joint loosening | Thermography (ΔT) | MCSA (current imbalance) |
| Pump cavitation | Pressure (inlet vacuum) + vibration | Flow sensor |
| Oil contamination ingress | ISO 4406 + Si in oil analysis | Filter dP |
| Motor overload | MCSA (% FLA) | RTD winding |

---

## 7. STANDARDS REFERENCE

| Standard | Scope |
|----------|-------|
| ISO 4406:2021 | Hydraulic fluid cleanliness codes |
| ISO 18434-1:2008 | Thermography condition monitoring of machines |
| ISO 13373-1:2002 | Vibration condition monitoring (references thermal as complementary) |
| IEC 60034-1 | Motor insulation class temperature limits |
| ASTM D5185 | ICP wear metal analysis |
| ASTM D6595 | RDE rotating disc electrode wear metals |
| ASTM D445 | Kinematic viscosity |
| ASTM D664 | Total Acid Number |
| ASTM D7684 | Analytical ferrography |
| ASTM D6224 | In-service lubricant monitoring (power plant) |
| NETA MTS (ATS-2019) | Thermography ΔT severity for electrical equipment |
| API 670 | Machinery protection — bearing temp alarm/trip setpoints |
| NEMA MG-1 | Motor current imbalance limits (< 2%) |

---

## 8. CONSOLIDATED THRESHOLD QUICK-REFERENCE

```
TEMPERATURE
  Bearing:   Healthy 40–80°C | Alarm 85–90°C | Trip 100–105°C
             Rate rule: >2°C/hour = alarm; >10°C above baseline = caution
  Winding F: Healthy <130°C | Alarm 130°C | Trip 145°C
  Winding H: Healthy <155°C | Alarm 155°C | Trip 175°C
  Thermo ΔT: 1–3°C possible deficiency | 4–15°C probable | >15°C serious | >30°C critical

PRESSURE (hydraulic)
  AGC:       Normal 250–300 bar | Trip: loss >50% in <1s = emergency shutdown
  General:   150–250 bar supply
  Filter dP: Clean 0.3–0.8 bar | Replace >1.0 bar | Bypass opens ~3–5 bar

FLOW
  Alarm:     >10% drop from baseline = caution | >20% = alarm

OIL ANALYSIS
  ISO 4406:  Target servo 15/13/10 | General hydraulic 18/16/14
             +2 code steps = 4× particles = action
  Fe (gear): <100 ppm normal | >200 ppm action (context-dependent)
  Cu:        <55 ppm normal | >100 ppm action
  Sn:        <10 ppm normal | >35 ppm action
  Viscosity: ±10% normal | ±10–20% marginal | >±20% critical/change oil
  TAN:       Action at 2× new-oil value OR absolute >1.5–2.0 mg KOH/g

MCSA
  Running:   80–100% FLA | <50% FLA = underloaded
  PF:        0.85–0.92 full load
  BRB sideband: −50 to −60 dBc healthy | −40 to −45 dBc = 1–2 broken bars (plan outage)
              −25 to −35 dBc = multiple bars (urgent) | >−25 dBc = remove from service
  Imbalance: <2% normal | >5% = +25°C per 1% above 5% (NEMA rule)
```

---

## 9. DATA SOURCES (all checked 2026-06-08)

- [Bearing temperature monitoring & API 670 setpoints — PLC DCS Pro](https://www.plcdcspro.com/blogs/news/motor-bearing-temperature-monitoring-and-vibration-protection-settings)
- [SKF bearing temperature troubleshooting — Reliable Plant](https://www.reliableplant.com/Read/25315/Tips-troubleshooting-bearing-temperatures)
- [Motor insulation class temperature limits — MotionControlTips](https://www.motioncontroltips.com/what-does-motor-insulation-class-specify-and-why-is-it-important/)
- [Insulation class B/F/H practical limits — Quantum Controls](https://www.quantum-controls.co.uk/insights/faqs/how-do-i-classify-the-temperature-limits-of-an-electric-motor/)
- [ISO 18434-1 thermography standard — ISO.org](https://www.iso.org/standard/41648.html)
- [Thermographic inspection electrical — OxMaint](https://oxmaint.com/article/thermographic-inspection-electrical)
- [MCSA broken rotor bar sidebands — MaximoMastery](https://maximomastery.com/terms/mcsa/)
- [MCSA predictive maintenance 2026 — OxMaint](https://oxmaint.com/blog/post/blog-post-motor-current-signature-analysis-predictive-maintenance)
- [MCSA fault signatures detailed — Motor Current Signature Analysis fjinno.net](https://www.fjinno.net/motor-current-signature-analysis)
- [ISO 4406 cleanliness codes — HyPro Filtration](https://www.hyprofiltration.com/blog/iso-4406-cleanliness-codes)
- [ISO 4406 chart complete — Torontech](https://www.torontech.com/articles/full-iso-4406-chart-cleanliness-guide/)
- [Oil analysis PdM wear interpretation — Machinery Lubrication](https://www.machinerylubrication.com/Read/653/wear-oil-analysis)
- [Oil analysis TAN/viscosity limits — OxMaint](https://oxmaint.com/blog/post/blog-post-oil-analysis-predictive-maintenance-machines)
- [Gearbox wear metal limits — Machinery Lubrication India](https://machinerylubricationindia.com/magazine/2020/nov-dec/condition-monitoring-of-gear-through-oil-analysis/)
- [Viscosity ±10/20% action limits — Machinery Lubrication interpret reports](https://www.machinerylubrication.com/Read/30443/oil-analysis-reports)
- [Filter dP replacement thresholds — Internormen Filters](https://www.internormenfilters.com/news/hydraulic-filter-replacement-guide-how-to-use-differential-pressure-indicator-readings-for-effective-clogging-detection.html)
- [Filter dP threshold guide — MP Filtri](https://www.mpfiltri-filters.com/news/how-to-determine-hydraulic-oil-filter-replacement-intervals-pressure-differential-monitoring-environmental-factors-explained.html)
- [Steel plant hydraulic maintenance — OxMaint steel plant](https://oxmaint.com/industries/steel-plant/steel-plant-hydraulic-system-maintenance-mills-casters-furnaces)
- [Rolling mill AGC hydraulics — OxMaint](https://oxmaint.com/industries/steel-plant/rolling-mill-hydraulic-system-maintenance-agc-looper)
- [High-temp pressure sensors steel mill AGC — Gamicos](https://blog.gamicos.com/high-temp-pressure-sensors-in-steel-mill-hydraulic-agc)
- [NETA ΔT severity classification — Aura Safety](https://aurasafety.com/services/electrical-safety/thermography-to-detect-hot-spots)
- [Bearing fault frequency BPFO/BPFI in MCSA — Vibromera](https://vibromera.eu/glossary/bearing-fault-frequencies/)
- [MCSA detection current signatures — iFactory](https://ifactoryapp.com/blog/current-signature-analysis-motors)
- [RTD vs thermocouple PdM bearing — Fluke](https://www.fluke.com/en-us/learn/blog/calibration/rtd-vs-thermocouple-difference)
- [Steel mill flow sensor and predictive maintenance — OxMaint AI](https://www.oxmaint.com/blog/post/steel-plant-management-ai-continuous-operations)
- [Ferrography wear particle analysis — Reliability Web](https://reliabilityweb.com/articles/entry/wear_particle_analysis_-_a_predictive_maintenance_tool)
- [ASTM D6595 RDE wear metals — Infinita Lab](https://infinitalab.com/services/astm-d6595-used-oil-wear-metals-testing/)

---

*[unverified] disclaimer: Specific threshold numbers cited (ISO 4406 targets, dBc sideband levels, temperature alarm setpoints) represent industry-consensus ranges synthesised from multiple sources. Actual setpoints MUST be validated against equipment OEM specs, local process historian baselines, and plant-specific hazard analysis before use in control logic or shutdown systems.*
