# 02 — Gearboxes & Gear Drives in an Integrated Steel Plant
## PdM Deep-Reference | Tata Steel Round 2 | 2026-06-08

---

## 1. Gearbox Types & Where They Live

| Gearbox Class | Location in Plant | Drive Power Typical | Gear Form | Notes |
|---|---|---|---|---|
| **Main reduction gearbox** | Hot strip mill (HSM), each finishing stand | 3,000–12,000 hp (≈2.2–9 MW) per stand | Double-helical / herringbone | Converts motor speed to roll speed; absorbs 4× rated torque impact shock on bar entry |
| **Pinion stand** | Attached downstream of main reduction, all rolling mills | Receives output from main gearbox | Single or double helical | Splits torque between upper and lower work rolls; pinion pitch dia. 2–4 ft, weighing 10,000–20,000 lb |
| **Reduction gearbox (multi-stage)** | Roughing mill, bar & rod mills, plate mills | 1,000–5,000 kW | Helical, multi-stage | Achieves gear ratios 5:1–100:1; typical efficiency 96–99 % |
| **Planetary gearbox** | Coiler mandrel drives, cold rolling tandem mill coiler, continuous caster withdrawal roll drives | 200–2,000 kW | Epicyclic sun/planet/ring | High torque-density in compact envelope; used where radial space is constrained |
| **Bevel-helical gearbox** | 90° directional drives — conveyor head drives, blast furnace skip hoist, stave cooler fans | 100–1,500 kW | Spiral bevel + helical stages | Direction change + speed reduction in one housing |
| **Worm gearbox** | Auxiliary drives: roll-gap screw-down positioners, ladle turret slow-drive, AGC cylinders | 5–250 kW | Worm & wheel | Very high reduction ratios 10:1–100:1 per stage; self-locking; low efficiency 50–90 % |
| **Turbo-gearbox / speed increaser** | Blast furnace gas turbines, plant compressors | Up to 20 MW | Parallel-shaft helical | Less common in rolling section; critical in utility area |

**Material notes (all classes):** Pinion shafts use carburized modified AISI 4320 to HRC 58 case hardness; gear rims use AISI 4340/4350 at 363–401 Bhn. [Source: Machine Design article — see §References]

---

## 2. Parts Breakdown

### 2.1 Gear Elements
- **Gear teeth — flank (face):** Load-bearing contact surface. Hertzian contact stress site; micropitting, macropitting, and scuffing initiate here.
- **Gear teeth — root (fillet):** Highest bending stress location. Root fatigue crack initiates here, progressing into tooth body and eventually to tooth-breakage or shaft fracture.
- **Driving gear / pinion:** Smaller element of the mesh pair; higher rotational speed, more tooth-pass cycles per unit time — therefore the first to fatigue. Pinion face widths 4–10 ft in HSM.
- **Driven gear / bull gear:** Large gear; mass 80,000–190,000 lb in HSM main gearbox; slower speed but higher torque.
- **Herringbone / double-helical geometry:** Opposite-hand helix angles cancel axial thrust internally; allows helix angle 20°–45° for smooth torque without thrust bearing load — preferred in high-power mill drives.

### 2.2 Rotating & Static Structure
- **Input/output shafts:** Alloy steel, precision-ground; fatigue crack nucleates at keyway or fillet radii under cyclic bending + torsion.
- **Rolling element bearings (main):** Usually spherical roller or cylindrical roller — CARB toroidal in later designs. Support radial and axial loads from gear forces; the most frequent failure sub-component.
- **Plain (hydrodynamic) bearings:** Used on very large slow shafts (pinion shaft journals in heavy-duty mills); fail by oil-film breakdown → scuffing.
- **Couplings:** Gear-type couplings between motor-shaft and gearbox input; spindle couplings between pinion stand output and work roll; fail by fretting, tooth wear, angular misalignment.
- **Seals:** Lip or labyrinth seals at shaft exits; degradation → lube leakage + external contamination ingress.
- **Casing / housing:** Cast or fabricated steel; structural resonances can amplify gear noise; machining of bearing bores critical to alignment.
- **Lubrication system:** Forced-feed with oil cooler + filter. Reservoir 200–4,000 litres for large HSM gearbox. Oil grade ISO VG 220–320 (helical/herringbone); ISO VG 460–680 for worm gear. Oil pump, filter (10–25 µm absolute), heat exchanger.
- **Oil filter / debris monitor:** Magnetic plug + online ferrous particle sensor (e.g., GasTOPS MetalSCAN, Hitachi CM-A series) captures wear debris.

---

## 3. Sensors — Full Set & Relative Deployment Prevalence

| Sensor | Physical Quantity | Typical Location | Prevalence in Steel PdM | Notes |
|---|---|---|---|---|
| **Piezoelectric accelerometer** | Acceleration (vibration) | Bearing housing, gearbox casing, pinion-stand housing | **Very high — #1 deployed** | Range 10 Hz–20 kHz; high-freq envelope (HFRT) for bearings, GMF analysis for gears |
| **Proximity probe (eddy current)** | Shaft radial displacement | Input/output shaft journals (large slow gearboxes) | High | API 670 standard for shaft-riding protection; displacement in µm |
| **RTD / thermocouple (oil temperature)** | Oil sump/supply/return temperature | Gearbox oil sump, lube system header | **Very high — co-equal #1** | Simplest, cheapest, always present; first indication of lube breakdown |
| **RTD on bearing housing** | Bearing surface temperature | Outer-race housing bore or housing pocket | High | Detects lubrication failure, overload, cage damage |
| **Online ferrous debris / particle count** | Fe particle concentration (ppm), ISO 4406 cleanliness code | Oil return line, sump | Medium-high | Most specific to actual tooth/bearing wear; direct material loss indicator |
| **Acoustic emission (AE) sensor** | Stress wave energy (100 kHz–1 MHz) | Bearing housing, gear casing | Medium | Earliest detection of crack nucleation; leads vibration by 4–8 months; installed on critical assets |
| **Oil viscosity / water-in-oil sensor** | Kinematic viscosity, water ppm | Online in lube loop | Medium | Quantomix OilCheck or Parker kittiwake style; catch lube degradation early |
| **Motor current signature analysis (MCSA)** | Phase current spectrum | MCC or VFD output | Medium | Non-invasive; detects gear eccentricity, bearing defects via current modulation |
| **Strain gauge / torque meter** | Torsional load | Input shaft (selected critical gearboxes) | Low-medium | Physics-informed RUL; useful for fatigue-life consumed per cycle |
| **Speed encoder (tachometer)** | Shaft RPM | Input/output shaft | High | Required for computing GMF and bearing defect frequencies; usually already present for process control |

---

## 4. Normal Operating Readings

### 4.1 Vibration (ISO 10816-3 / ISO 20816-3 framework)

For large industrial machines (>300 kW, rigid mounting, rolling element bearings), the ISO 10816-3 velocity RMS zones are:

| Zone | Condition | Velocity RMS (mm/s) |
|---|---|---|
| A | New / excellent | < 2.3 |
| B | Acceptable for long-term | 2.3 – 4.5 |
| C | Alert — investigate | 4.5 – 7.1 |
| D | Danger — stop | > 7.1 |

[Note: exact numbers vary by machine class within the standard; figures above are for Class III, 15 kW–300 kW; Class IV (>300 kW) zones shift to roughly 3.5 / 7.1 / 11.2 / >11.2 mm/s — [unverified for class IV exact boundary]]

**Practical mill gearbox baseline vibration:** 1–3 mm/s velocity RMS broadband during steady rolling. Acceleration baseline at bearing housing 0.5–2.0 g RMS (broadband 10 Hz–1 kHz).

**Gear mesh frequency spectrum (healthy):**
- GMF = (number of teeth on gear) × (shaft RPM / 60) [Hz]
  - Example: 45-tooth gear at 300 RPM → GMF = 45 × 300/60 = 225 Hz
- Harmonics: 2×GMF, 3×GMF visible but amplitude decaying
- Sidebands: symmetric, amplitude < −30 dB relative to GMF peak; spacing = shaft rotational frequency (1×RPM/60 Hz)
- Time waveform: near-sinusoidal, low kurtosis (< 3)

### 4.2 Bearing temperatures

| Parameter | Normal | Caution | Alarm | Trip |
|---|---|---|---|---|
| Bearing housing temperature | 40–70°C above ambient (~60–90°C absolute) | 85°C | 95°C | 105°C |
| Oil supply temperature | 40–55°C | 60°C | 65°C | 70°C |
| Oil return temperature | < 15°C above supply | +15 | +20 | +25 |

[API 670 alarm = 85°C trip = 105°C for sleeve bearings; rolling element bearings typically 10°C lower; [unverified exact plant setpoints]]

### 4.3 Oil analysis (ISO 4406 cleanliness code — particle counts at 4 µm / 6 µm / 14 µm)

| Parameter | Target (new oil / clean system) | Alert | Action |
|---|---|---|---|
| ISO 4406 cleanliness code | 16/14/11 | 18/16/13 | 20/18/15 (flush + filter change) |
| Iron content (ICP) | < 20 ppm | 50 ppm | > 80 ppm |
| Copper content | < 15 ppm | 30 ppm | > 60 ppm |
| Water content | < 0.05 % | 0.1 % | > 0.2 % (dehydrate or change) |
| Viscosity @ 40°C | Within ±5 % of ISO VG grade spec | ±8 % | > ±10 % (change oil) |
| Ferrous debris index (online) | Baseline established; < 2× baseline | 3× baseline | 5× baseline |

Chevron OEM ISO cleanliness specs: critical gearboxes target 16/14/11 — [Source: Chevron ISOCLEAN OEM guide]

---

## 5. Defect Signatures — What the Numbers Become

### 5.1 Gear tooth pitting / spalling / wear

**Progression:** Micropitting (pits < 10 µm) → macropitting / spalling (pits 0.1–10 mm) → tooth material loss → noise + accelerated wear.

| Stage | Vibration change | Oil change | AE change |
|---|---|---|---|
| Micro-pitting onset | GMF sidebands appear; spacing = 1× pinion shaft freq; SER (Sideband Energy Ratio) increases from baseline | Fe ppm rises from <20 to 30–50; ISO code shift to 18/16 | AE hit-rate increases 2–3× baseline |
| Macro-pitting | 2×, 3×GMF harmonics grow; sideband amplitude ratio > −20 dB; kurtosis > 4 | Fe > 80 ppm; Cu > 40 ppm if bearing impact; oil darkens | AE RMS energy 5–10× baseline |
| Spalling (accelerating) | Overall vibration doubles; time waveform shows high-amplitude impacts; kurtosis > 6; HFRT envelope shows GMF sidebands at bearing-housing HF bands | Fe > 150 ppm; large particles (>100 µm) visible on magnetic drain plug | AE continuous bursts |
| Catastrophic tooth loss | GMF amplitude 3–5× baseline or collapses if tooth gone; shaft 1× unbalance rises | Fe spike > 500 ppm; large chips on magnetic plug | N/A — failure imminent |

**Warning alarm trigger:** SER > −20 dB across ≥2 harmonics of GMF AND iron > 80 ppm → alert maintenance.
**Danger alarm trigger:** Overall velocity > 7.1 mm/s OR kurtosis > 6 OR Fe > 150 ppm → production stoppage required.

**Sideband Amplitude Ratio (SAR) / Sideband Energy Ratio (SER):**
SER = 10 × log₁₀[(sum of upper + lower sideband amplitudes²) / GMF amplitude²] dB
- Healthy: SER < −30 dB (sidebands negligible)
- Alert: SER in range −20 dB to −15 dB
- Alarm: SER > −15 dB
- Harmonics below −40 dB relative to GMF should be excluded from SER calculation (GE patent US8171797B2)

### 5.2 Root bending fatigue crack

- AE: primary sensor — detects crack propagation at defect size 500 µm (vibration doesn't respond until >1,000 µm) [PMC8538209]
- Vibration: 1× shaft frequency phase and amplitude change; modulation sidebands around all harmonics; time-waveform shows sharp impulse at tooth-pass rate
- Oil: no significant change until crack propagates to tooth loss (then chips)

### 5.3 Gear scuffing (adhesive wear)

- Occurs at high sliding velocities, boundary lubrication, oil film breakdown
- **Earliest sign:** Rising bulk gear temperature (IR thermography), oil temperature rise > 10°C in 30 minutes, oil viscosity drop to < ISO VG spec − 8%
- Vibration: high-frequency noise; GMF broadband floor rises
- Oil: Fe and Cr increase rapidly; ferrous index spike

### 5.4 Bearing fatigue (inner race, outer race, rolling element)

- Defect frequencies: BPFO = 0.4 × Nb × fr; BPFI = 0.6 × Nb × fr; BSF = (Pd/Bd)/2 × fr × [1−(Bd/Pd×cosα)²]; FTF = fr/2 × [1 − (Bd/Pd)×cosα]
  where Nb = number of rolling elements, fr = shaft rotational freq, Pd = pitch dia, Bd = ball dia, α = contact angle
- Stage 1 (sub-surface crack): detectable only by AE / HF envelope; overall vibration unchanged
- Stage 2 (surface fatigue): BPFO or BPFI visible in envelope spectrum; kurtosis 4–6
- Stage 3 (multiple pits): bearing defect frequency + harmonics; sideband growth around defect freqs; kurtosis > 6; temperature +5–10°C
- Stage 4 (spalling): overall velocity > 7.1 mm/s; kurtosis >10; rapid temperature rise

### 5.5 Lubrication breakdown / contamination

| Parameter | Normal → Degraded |
|---|---|
| Oil temperature | 50°C → 70°C (warning); > 80°C sustained = thermal breakdown accelerating |
| Viscosity @40°C | VG 320 = 320 cSt → drops 10–15% on thermal crack; rises if oxidation sludge |
| Water content | < 0.05% → > 0.2% = emulsification; bearing corrosion within 2 weeks |
| ISO cleanliness | 16/14/11 → 20/18/15 = 1,000× more particles; abrasive wear rate multiplies 5–10× |
| Acid number (TAN) | < 1.0 mg KOH/g → > 2.0 = oil oxidation; > 3.0 = change mandatory |

---

## 6. Failure Modes — Root Causes & Earliest Signs

| Failure Mode | Root Cause | Earliest Detectable Sign | Typical Lead Time Before Failure |
|---|---|---|---|
| **Tooth surface micropitting** | EHD film inadequate; low viscosity; high sliding speed; water contamination | Fe ppm rise + AE hit-rate increase | 3–6 months |
| **Tooth macropitting / spalling** | Progressive from micropitting; overload; material defect | GMF sidebands (SER > −20 dB) + Fe >80 ppm | 1–3 months |
| **Tooth root bending fatigue crack** | Cyclic bending stress exceeding endurance limit; shock loads (bar entry = 4× rated torque) | AE burst signature; phase change on 1× shaft | 2–5 months |
| **Gear scuffing (scoring)** | Oil film breakdown; viscosity too low at operating temp; inadequate EP additive | Oil temp spike; vibration high-freq floor rise | Hours to days — rapid |
| **Shaft fatigue fracture** | Cyclic bending + torsion; stress concentration at keyways; corrosion pitting | AE; 1× vibration amplitude growth; phase shift | 1–4 months |
| **Bearing fatigue** | Overload; misalignment; lubrication failure | AE; HFRT envelope; Stage 1 undetected by broadband | 3–12 months |
| **Bearing brinelling** | Impact loads (bar threading, mill jams, startup) | High-freq envelope peaks at BPFO immediately post-event | Weeks to months |
| **Lube system contamination** | Seal failure; mill scale/water ingress; filter bypass | ISO 4406 code shift; water-in-oil sensor alarm | Days to weeks |
| **Gear misalignment** | Thermal expansion mismatch; foundation settlement; improper assembly | Contact pattern shift; edge loading visible; 2×GMF harmonic growth | Months |
| **Coupling fatigue / fretting** | Angular/parallel misalignment; cyclic torque reversal | 2× shaft frequency vibration; thermal imaging hot-spots | Weeks to months |

---

## 7. Repair / Resolution Process

### 7.1 Inspection sequence (planned)
1. Visual inspection with casing open — tooth contact pattern check (bluing), crack detection (PT or MT)
2. Dimensional inspection — pitch circle runout, tooth spacing error, shaft deflection measurement
3. Bearing clearance check — compare against OEM spec; replace if clearance >150% of new value
4. Alignment check — laser alignment of gear shaft to motor; accept tolerance typically < 0.05 mm/m angular
5. Oil system: flush, filter change, lab analysis of drained oil; inspect magnetic plug for chips
6. NDT on shafts: UT flaw detection for sub-surface cracks at keyways and fillet radii
7. Gear mesh contact check after reassembly; run-in at 50% load for 4 hours with oil analysis at 2 h

### 7.2 Tooth repair options
- **Stage 1–2 (micropitting/light pitting):** Polish + surface treatment, increase oil viscosity one grade, change to higher-performance EP oil, more frequent oil analysis (monthly → bi-weekly)
- **Stage 3 (macropitting/spalling on one tooth):** Weld repair (if geometry permits) or planned pinion replacement at next scheduled outage; 5–15 day lead time for spare pinion if in stock
- **Stage 4 (catastrophic):** Emergency gearbox changeout; replacement gearbox OEM lead time 6–18 months — underscores criticality of spares strategy

### 7.3 Bearing replacement
- Standard replacement time (bearing only, casing not cracked): 8–24 hours in HSM, 4–8 hours in auxiliary gearbox
- Full gearbox disassembly + rebuild (multi-stage): 3–7 days planned; 7–21 days unplanned (awaiting parts)

### 7.4 Oil system actions
- Oil change + flush: 4–8 hours; filter change 30 minutes (most systems allow online filter change)
- Contamination event (water ingress): drain, flush with flushing oil, refill, sample at 4h and 8h

### 7.5 Planned vs unplanned comparison
| Intervention | Planned (PdM-triggered) | Unplanned (run-to-failure) |
|---|---|---|
| Pinion replacement | $85K + 2-day scheduled outage | $420K + 5–21 days emergency (lost production + cascade damage) |
| Bearing replacement | $8K–$25K + 8–24h scheduled | $50K–$150K + 2–7 days (secondary damage to gear teeth, shaft) |
| Full gearbox rebuild | $250K + 7-day outage | $500K–$3M + 10–21 days |

---

## 8. Cost / Loss Impact

### 8.1 Production loss rate
- HSM (7 m wide, ~3 Mt/yr capacity): **$38,000–$60,000 per unplanned downtime hour** [unverified for Tata Steel specifically; cited range from Gary, Indiana flat-steel producer case: $38K/hr — Oxmaint]
- Cold rolling mill: ~$15,000–$30,000/hr [unverified; estimate from industry benchmarks]
- Bar/rod/structural mill: $5,000–$15,000/hr [unverified]

### 8.2 Failure event total cost
| Event | Direct Repair | Lost Production (5–21 days × rate) | Cascade Damage | Total |
|---|---|---|---|---|
| Catastrophic HSM finishing stand gearbox | $300K–$800K | $1.9M–$18M | $200K–$1M (downstream rolls, spindle) | $2.4M–$20M |
| Pinion stand bearing failure (unplanned) | $50K–$150K | $300K–$2M | $50K–$300K | $400K–$2.5M |

### 8.3 PdM program ROI
- Minimum viable PdM sensor + analytics investment for HSM gearbox fleet: $80K–$150K upfront
- Annual value from avoided failures, extended component life, optimised outages: $5.6M+ (HSM scale) [Oxmaint]
- Typical payback period: < 3 months at HSM scale

### 8.4 Cascade / secondary effects
- **Tooth breakage in pinion stand** → fragment can destroy mating gear, spindle coupling, and work roll bearings in one event — multiplying repair cost 3–5×
- **Gearbox seizure** → may damage motor armature (de-celeration torque spike)
- **HSM gearbox failure** → entire finishing train idle → reheated slab rejected → energy waste + scrap loss → downstream coiler/processing idle

### 8.5 Replacement parts lead time risk
- Spare HSM main reduction gearbox: 6–18 months from OEM
- Spare pinion: 5–30 days depending on size (> 10,000 lb = always long lead)
- Recommendation: maintain one critical-path spare pinion set per stand for top-2 highest-risk stands

---

## 9. Additional PdM Engineering Notes

### 9.1 Signal processing stack for gearbox vibration
1. **Broadband velocity RMS** (10 Hz–1 kHz): overall machine health trending per ISO 10816-3
2. **Spectrum (FFT)**: detect GMF, harmonics, sidebands — window 1–10 s, resolution ≤ 0.5 Hz at gear speeds
3. **High-frequency resonance technique (HFRT) / envelope analysis**: band-pass 5–20 kHz → rectify → low-pass → FFT of envelope; detects bearing defects and early gear pitting before broadband rises
4. **Time synchronous averaging (TSA)**: removes noise; requires tachometer; isolates per-shaft gear signature
5. **Cepstrum analysis**: quefrency peaks at sideband spacing; detects distributed gear damage
6. **Kurtosis / kurtogram**: statistical impulsiveness; K > 3 = impact events present; K > 6 = significant fault

### 9.2 Gear mesh frequency example — HSM finishing stand (typical)
- Motor: 6,000 kW, 500 RPM output
- Reduction gearbox: 45-tooth input gear, 135-tooth output gear → ratio 3:1 → output 167 RPM
- GMF = 45 × (500/60) = 375 Hz (at input shaft)
- GMF at output = 135 × (167/60) = 375 Hz (same — as expected; mesh event rate same for both gears)
- First sideband pair: 375 ± 8.3 Hz (input shaft 500/60 = 8.33 Hz)
- Pinion stand additional GMF: depends on pinion tooth count and roll speed (~30–120 Hz typical)

### 9.3 MCSA for gearbox health
- Gear eccentricity modulates air gap → motor current spectral peaks at fr ± f_slip
- Bearing outer-race defect appears in current spectrum at f_line ± BPFO
- Advantage: purely non-invasive; no mechanical sensor installation
- Limitation: sensitivity lower than vibration; useful as corroborating channel

### 9.4 Foundation models for gearbox PdM (2024–2026 SOTA)
- **Anomaly Transformer** (Wu et al., 2022) [arxiv 2110.02642]: association discrepancy mechanism; strong on multi-variate gearbox sensor streams
- **TimesNet** (Wu et al., 2023) [openreview ICLR 2023]: 2D temporal variation modelling; outperforms LSTM-AE on CWRU bearing + gearbox datasets
- **Chronos** (Ansari et al., 2024, Amazon): foundation model for zero-shot time-series forecasting; applicable to RUL under data-sparse new-gearbox scenarios
- **Physics-informed neural networks (PINNs)**: encode Hertz contact theory + fracture mechanics as soft constraints in RUL model; prevents physically impossible predictions; recommended for root-crack RUL

### 9.5 Public datasets for model training/transfer
- **Case Western Reserve University Bearing Dataset** (CWRU): 12 kHz / 48 kHz accelerometer, inner/outer/ball faults, 0–3 hp load — standard benchmark
- **IMS Bearing Dataset** (NASA): run-to-failure, 4 bearings, 1 MHz, 20.4 kHz sample — RUL study standard
- **PHM 2009 Gear Challenge**: seeded gear fault, multiple severity levels, 66.7 kHz — gear-specific
- **PRONOSTIA / FEMTO Bearing**: run-to-failure bearings — degradation trajectory modelling

---

## References

- [Powerful gears in rolling mills — Machine Design](https://www.machinedesign.com/motors-drives/article/21827030/powerful-gears-in-rolling-mills) — gear dimensions, material specs, torque conditions
- [Predictive Maintenance for Rolling Mill Gearboxes & Drives — Oxmaint](https://oxmaint.com/industries/steel-plant/predictive-maintenance-rolling-mill-gearboxes-drives) — detection lead times, repair cost stages, PdM ROI
- [Comprehensive Guide to Gearboxes for Steel Rolling Machines — Hani Tech](https://hanrm.com/comprehensive-guide-to-gearboxes-for-steel-rolling-machines/) — gearbox types, operating spec ranges
- [GMF Calculation and Gearbox Problems Detection — CBM Connect](https://www.cbmconnect.com/gmf-calculation-and-gearbox-problems-detection/) — GMF formula, sideband diagnostics, spectrum analysis depth
- [Helical Gearbox Defect Detection with ML using GMF Sidebands — PMC/NCBI](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11174595/) — 2024 peer-reviewed; regular mesh + sideband features for ML classifier
- [Sideband Energy Ratio for Gear Mesh Fault Detection — US Patent US8171797B2](https://patents.google.com/patent/US8171797B2/en) — SER definition, −40 dB exclusion threshold
- [Fault Feature Analysis of Gear Tooth Spalling — PMC/NCBI](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8538209/) — dynamic simulation + experiment; vibration vs AE defect detection size threshold
- [An Improved Sideband Energy Ratio for Planetary Gearboxes — ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S0022460X20305423)
- [Gearbox Tooth Cut Fault Diagnostics using AE and Vibration — MDPI Sensors](https://www.mdpi.com/1424-8220/14/1/1372) — comparative study: AE detects smaller defects earlier
- [Chevron ISOCLEAN OEM ISO Cleanliness — Industrial Gear](https://www.chevronlubricants.com/content/dam/external/isoclean/en_us/resources/ISOCLEAN-OEM_ISOCleanliness_Industrial_Gear_S.pdf) — target cleanliness codes per OEM
- [ISO 10816-3 Vibration Severity Guidelines — CBM Connect](https://www.cbmconnect.com/simplified-vibration-monitoring-iso-10816-3-guidelines/) — zone boundaries
- [Macropitting Gear Failures — ONYX Insight](https://onyxinsight.com/resources-support/failure-atlas/macropitting-gear-failure/) — failure progression description
- [An Ear for Gears — Crystal Instruments](https://www.crystalinstruments.com/an-ear-for-gears-understanding-gearbox-signatures) — gearbox vibration signature interpretation
- [Lubrication Requirements for Industrial Gearboxes — TANHON](https://tanhon.com/lubrication-requirements-for-industrial-gearboxes/) — oil viscosity selection, temperature effects
- [Rolling Mill Gearbox Manufacturer — The Steefo Group](https://www.thesteefogroup.com/products/rolling-mill-gearbox/) — product specs
- [Hot Strip Mill Main Drives — Galbiati Group](https://galbiati.it/en/gear-reducers/hot-strip-mill-main-drives/) — HSM drive specifications

---

*[unverified] tags: Tata Steel-specific ₹/hr downtime figures; Class IV ISO 10816-3 exact zone boundaries; specific plant bearing temperature setpoints — these are industry-range estimates. All should be cross-checked against Tata Steel's own O&M documentation or instrumentation calibration records.*
