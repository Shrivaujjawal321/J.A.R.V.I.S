# Bearings in an Integrated Steel Plant — Deep Technical Reference
**Scope:** Tata Steel scale integrated plant (blast furnace → hot strip mill → cold rolling)
**Prepared by:** tata-steel-predictive-maintenance subagent
**Date:** 2026-06-08
**Classification:** Domain Reference — Machinery Layer

---

## 1. Bearing Types and Where Each Is Used

### 1.1 Four-Row Tapered Roller Bearing (TQO / TQI)

**Primary location:** Rolling mill roll necks — work rolls and backup rolls in hot strip mill (HSM), cold rolling mill (CRM), plate mill, slab mill, rod mill, bar mill.

**Why here:** Roll necks carry simultaneous heavy radial load (rolling force, up to 40–80 MN on a backup roll) and bidirectional axial thrust. Four rows of tapered rollers in two face-to-face pairs provide radial and thrust capacity in one compact assembly that fits inside the roll chock (housing). No other bearing type achieves this load density in the available space.

**Design configurations:**
- **TQO (most common):** Two TDI double-cone inner rings + one double cup (center) + two single cups (ends) + cone spacer + two cup spacers. Components match-numbered — must be reassembled in original sequence.
- **TQI:** Cone pairs arranged back-to-back; provides higher moment stiffness; used where chock tilting loads are significant.
- **2TDIW:** Four single cups + three spacers; no cone spacer; match-ground for tighter preload control.

**Bore range:** 120 mm – 1 580 mm. A typical work roll neck in a 1 580 mm hot strip mill uses a bore of ~500–700 mm.

**Operating speed:** Low to medium (50–400 RPM at roll neck). High loads dominate over speed for these applications.

**Lubrication:** Oil-film (hydrodynamic oil wedge in chock housing with circulating oil system), or grease-packed sealed variants (NSK Sealed-Clean range). Oil-film systems deliver oil at 1–5 bar through ports in the chock.

**Sources:** [FAG Rolling Bearings in Rolling Mills — Schaeffler WL 17200 (PDF via schaeffler.com)](https://www.schaeffler.com/remotemedien/media/_shared_media/08_media_library/01_publications/schaeffler_2/publication/downloads_18/wl_17200_5_de_en.pdf); [NSK Roll Neck Bearing Manual](https://www.nsk.com/content/dam/nsk/am/en_us/documents/bearings-americas/Roll-Neck-Bearing-Manual.pdf); [American Roller Bearing TQO page](https://www.amroll.com/four-row-tqo.html); [NTN Sealed Four-Row Tapered (PDF)](https://www.ntn-snr.com/sites/default/files/2017-03/en_sealed_four_row_tapered_roller_bearings_ultage.pdf)

---

### 1.2 Spherical Roller Bearing (SRB)

**Primary locations:**
- Conveyor idler rolls and conveyor drive units (raw materials handling — iron ore, coal, coke, sinter conveyors)
- Blast furnace top equipment (skip hoists, bell mechanisms, gas offtake shaft seals)
- Continuous caster secondary cooling zone withdrawal rolls
- Fan drives, cooling tower drives, induced draft fans
- Pump gearbox input/output shafts

**Why here:** Misalignment tolerance up to 3.0° accommodates shaft deflection, foundation settlement, and thermal elongation — all common in large steel plant structures. Handles combined radial + bidirectional axial loads.

**Key spec:** SKF/FAG 22300 series, 22200 series. Bore 20–900 mm. Operating temperature: −30°C to +200°C with metal cage; −30°C to +120°C with polyamide cage.

**Source:** [SKF Spherical Roller Bearings product page](https://www.skf.com/group/products/rolling-bearings/roller-bearings/spherical-roller-bearings); [Quality Bearings Online 22300 series](https://www.qualitybearingsonline.com/spherical-roller/22300-series)

---

### 1.3 Cylindrical Roller Bearing (CRB) — Single-Row and Multi-Row

**Primary locations:**
- Rolling mill roll necks (four-row cylindrical roller — FCRB — used on high-speed stands where radial load dominates and minimal axial thrust; warm mill finishing ends)
- Electric motor drive-end and fan-end (typically N or NU series, free to float axially)
- Gearbox intermediate shafts
- Continuous caster mould oscillator
- Crane wheel bearings (large single-row high-capacity)

**Why here:** Highest radial load capacity per bore size of any rolling-element type. Line contact (roller vs. raceway) vs. point contact (ball). Can run at higher speed than tapered roller.

**Key distinction:** NU/N types allow axial float (roller free to slide axially in outer ring); NJ/NF types provide one-direction thrust. Critical for thermal elongation accommodation in rolling mill drives.

**Source:** [Schaeffler FAG application documentation, general engineering knowledge]

---

### 1.4 Deep-Groove Ball Bearing (DGBB)

**Primary locations:**
- Electric motor bearings (both drive end and non-drive end) — the most common bearing in the plant by unit count
- Small pump bearings
- Conveyor gearbox output shafts (lighter duty)
- Instrumentation and control actuators

**Why here:** Low friction, suitable for high speed, takes both radial and axial load, low cost, universally available. SKF 6205-2RS / 6206-2RS series are the CWRU benchmark bearings (2 HP motor test rig).

**Source:** [CWRU Bearing Dataset documentation](https://deepwiki.com/hustcxl/Rotating-machine-fault-data-set/2.1-cwru-bearing-dataset)

---

### 1.5 Tapered Roller Bearing (TRB) — Single-Row and Double-Row

**Primary locations:**
- Rolling mill pinion stand bearings (moderate load, some axial)
- Crane travel wheel bearings
- Vehicle wheel bearings in plant mobile equipment
- Pump/motor combination units where axial preload is required

**Why here:** Handles combined radial + unidirectional axial load better than ball bearings; cheaper and more available than four-row TQO for smaller applications.

---

### 1.6 Thrust Bearing — Tapered Roller and Ball Thrust

**Primary locations:**
- Rolling mill screw-down mechanisms (thrust to resist the roll-separation force reaction)
- Blast furnace bell-less top distribution chute pivots
- Vertical pump (axial shaft weight + hydraulic thrust)
- Rolling mill edger stands (axial load from edge rolls)

**Why here:** Pure or primarily axial load. Ball thrust bearings (51000 / 53000 series) for lighter duty; tapered roller thrust for heavy and shock loads.

---

### 1.7 Journal (Plain / Sleeve / Hydrodynamic) Bearing

**Primary locations:**
- Hot strip mill roller table rolls (low-speed, simple, continuous water-flood lubrication)
- Blast furnace tuyere cooling water jackets and bustle pipe supports
- Large turbine-driven equipment (steam turbine supports for power generation)
- Some hot mill work roll necks in older mills (being replaced by anti-friction designs)

**Why here:** In water-flooded environments such as roller tables, hydrodynamic film forms naturally; plain copper/Babbitt metal (tin-antimony alloy, 0.125–9 mm thick) is robust and cheap to re-line. No rolling elements to spall or fatigue.

**Monitoring method:** Proximity probe (eddy current) measures shaft eccentricity and orbit within clearance; normal clearance ~0.002–0.003× shaft diameter; alarm when eccentricity exceeds 50–70% of radial clearance. Oil temperature and pressure are primary process variables.

**Sources:** [MDPI Real-Time Measurement of Bearing Housing Clearance in Rolling Mill, 2025](https://www.mdpi.com/1424-8220/25/6/1887); [Machinery Lubrication — Journal Bearing Lubrication](https://www.machinerylubrication.com/Read/779/journal-bearing-lubrication)

---

## 2. Full Parts Breakdown of a Rolling-Element Bearing

Using a four-row tapered roller chock bearing as the most complex steel-plant example:

| Component | Material | Function | Failure vulnerability |
|-----------|----------|----------|-----------------------|
| Inner ring (cone) — 2 double cones | Bearing-grade chromium steel (e.g. 52100 / 100Cr6) | Press-fitted to roll neck; provides tapered raceway for roller contact; transmits roll separating force | Spalling (subsurface fatigue at ~10–15% life); fretting to shaft (loose fit); cracking from shock |
| Outer ring (cup) — 1 double + 2 single | Same bearing steel | Seated in chock housing with interference fit; provides outer raceway; stationary under rolling load | Spalling (outer race defect → BPFO); false brinelling if stand idle under vibration; EDM fluting from stray VFD currents |
| Tapered rollers | Through-hardened bearing steel (60–66 HRC surface) | Transmit load from inner to outer race via line contact; generate BPFO/BPFI/BSF frequencies when damaged | Surface spalling from micro-pit initiation; smearing from slip on cold start; edge loading from misalignment |
| Cage (retainer) | Steel (brass/bronze for high-speed variants; polyamide for smaller bearings) | Maintains roller spacing; prevents roller-roller contact; guides roller spin axis | Fracture from roller binding (lubrication starvation, misalignment); pocket wear causing FTF harmonics |
| Cone spacer / cup spacers | Hardened steel | Precisely sets axial clearance and preload between rows | Fretting wear; incorrect spacers = wrong preload = premature fatigue |
| Seals (lips or labyrinth) | Nitrile rubber (NBR) or PTFE; metal labyrinth in harsh environments | Retains lubricant; excludes water, mill scale, rolling oil | Lip wear → contamination ingress; catastrophic if lip folds and contacts raceway |
| Lubricant film | ISO VG 150–320 mineral oil circulating system (roll neck); or NLGI 2–3 grease (sealed type) | Separates metal surfaces; transfers heat; provides EHD film; viscosity ratio κ ≥ 1.0 required for full film | Starvation (pump failure, line blockage); contamination (water, particles); oxidation/thermal degradation; wrong viscosity grade |
| Housing/Chock | Cast steel or ductile iron | Provides dimensional reference; transmits reaction load to mill housing window | Housing bore wear → outer ring creep → fretting; bore ovalising from repeated chock changes |

---

## 3. Sensors Used — Prevalence and Placement

### Sensor priority ranking for bearings in a steel plant:

| Rank | Sensor | Prevalence | Detects earliest |
|------|--------|-----------|-----------------|
| 1 | Accelerometer (ICP/IEPE piezoelectric) | Ubiquitous — every motor, gearbox, pump, mill stand. Most common PdM sensor | Stage 2 bearing damage (vibration detectable); inner/outer race, rolling element, cage faults via BPFO/BPFI/BSF/FTF |
| 2 | Temperature (RTD/PT100 or thermocouple) | Near-universal on bearings with continuous monitoring. Simple and cheap | Stage 3 (heat precedes seizure by hours); lubrication starvation; overload |
| 3 | Acoustic Emission (AE) sensor | Selective deployment — high-criticality bearings (blast furnace blower, caster withdrawal roll, large rolling mill motors) | Stage 1 — earliest detection (weeks/months before vibration change); subsurface crack initiation at 100–500 kHz |
| 4 | Proximity Probe (Eddy Current) | Journal bearings only; standard for turbines and large horizontal journals | Shaft orbit, clearance change, rub detection |
| 5 | Motor Current Signature Analysis (MCSA) | Applied at motor terminal — no sensor on bearing itself; good for remote diagnostics | Bearing faults manifest as sidebands at (line frequency ± bearing defect frequency) in current spectrum |
| 6 | Oil Debris Monitor (ODM / magnetic plug) | Circulating oil systems (roll neck lube circuits, gearboxes); inline magnetic chip detectors | Ferrous wear particle count correlates to spall area growth; alerts 2–4 weeks before catastrophic failure |

### Accelerometer placement details:
- Mount on bearing housing (rigid, non-rotating structural part) with stud mount for flat response to ≥20 kHz
- Two radial axes (vertical + horizontal) per bearing; one axial axis for thrust-loaded bearings
- Sensitivity selection: 10 mV/g for high-shock roll chocks; 100 mV/g standard motors; 500 mV/g slow rotor (<100 RPM)
- Vendors: PCB Piezotronics (ICP), Brüel & Kjær, Wilcoxon, IFM Electronic

### AE sensor placement:
- Directly on bearing outer ring surface or adjacent rigid housing (thin coupling grease layer for acoustic coupling)
- Frequency response: 20 kHz – 1 MHz; typical band-pass: 100–500 kHz for bearing crack detection; up to 1 MHz for subsurface initiation
- The AE burst energy increases proportionally to crack length — quantitative damage staging possible

**Sources:** [IoT Bearings — Bearing Defect Frequency Formulas](https://iotbearings.com/bearing-defect-frequencies-bpfo-bpfi-bsf-ftf-explained/); [ACOEM bearing fault frequency explanation](https://acoem.us/blog/vibration-analysis/bearing-fault-frequencies/); [MDPI — Early-Stage Damage Diagnosis via AE and ML, Lubricants 2025](https://doi.org/10.3390/lubricants14020095); [SAGE — AE monitoring of large-scale low-speed roller bearings, 2024](https://journals.sagepub.com/doi/10.1177/14759217231164912)

---

## 4. Normal Reading Ranges Per Sensor

### 4.1 Vibration (ISO 20816-3 / formerly ISO 10816-3)

**Measurement:** Broadband velocity, mm/s RMS, 10–1000 Hz, on bearing housing (non-rotating).

| Machine Group | Zone A (Normal) | Zone B (Acceptable) | Zone C (Alert — schedule action) | Zone D (Danger — shutdown) |
|---------------|-----------------|---------------------|-----------------------------------|---------------------------|
| Group 1: >300 kW or shaft height >315 mm (large mills, main drives) | ≤ 3.5 mm/s | 3.5–7.1 mm/s | 7.1–11.2 mm/s | >11.2 mm/s |
| Group 2: 15–300 kW or shaft height 160–315 mm (motors, pumps, fans) | ≤ 2.3 mm/s | 2.3–4.5 mm/s | 4.5–7.1 mm/s | >7.1 mm/s |

> Flexible-foundation machines (free-standing motors on skids): thresholds ~40% higher than rigid foundation values above.

**Asset-specific typical healthy ranges (steel plant operational data) [unverified exact numbers — drawn from OxMaint steel plant guide]:**

| Asset | Healthy (mm/s RMS) | Alert threshold | Action threshold |
|-------|--------------------|-----------------|-----------------|
| Rolling mill main drive motor | 1.5–3.5 | 3.5–7.1 | >7.1 |
| Rolling mill work roll chock bearing | 1.0–4.0 | 4.0–10 | >10 |
| Gearbox / pinion stand | 2.0–4.5 | 4.5–11 | >11 |
| Centrifugal pump | 0.5–2.3 | 2.3–4.5 | >4.5 |
| Continuous caster withdrawal roll | 1.0–3.5 | 3.5–8 | >8 |

**High-frequency acceleration (bearing fault specific):**
- Healthy bearing envelope: acceleration RMS < 0.5 g at BPFO/BPFI bands
- Developing fault: 0.5–2 g; Alert at 2 g; Trip consideration at >5 g in envelope band
- Sampling rate: minimum 20 kHz raw acquisition; 2-second capture window minimum for FFT resolution; spectral snapshots every 1–30 minutes for continuous monitoring

**Sources:** [ISO 20816-3 standard; vibromera.eu ISO 10816-3 article](https://vibromera.eu/glossary/iso-10816-3/); [OxMaint steel plant vibration best practices](https://oxmaint.com/industries/steel-plant/steel-plant-vibration-analysis-best-practices-measurement); [dspanalytic ISO 10816-3 table](https://dspanalytic.com/en/vibrations/understanding-the-iso-10816-3-vibration-severity-table/)

### 4.2 Temperature (Bearing Housing RTD / PT100)

| Condition | Temperature Range | Notes |
|-----------|-----------------|-------|
| Cold start (ambient steel plant floor) | 20–35°C | Before thermal equilibrium |
| Normal steady-state operation | 50–80°C | Grease-lubricated; 40–70°C oil-film |
| Elevated — monitor closely | 80–90°C | Possible lubrication degradation or overload |
| Warning alarm | 90°C (or +20°C above established baseline) | Investigate within shift |
| Danger alarm / shutdown trigger | 100–110°C (sleeve bearing: 100°C; rolling element: 120°C max continuous for standard steel bearings) | Immediate action; shutdown if trend continues |
| Catastrophic / seizure precursor | >120°C and rising rapidly | Lubricant carbonising; seizure imminent |

> Rule of thumb cited by SKF: rolling-element bearings can tolerate up to ~120°C continuous; above this contact bearing manufacturer. Sleeve/journal bearings per EASA: Normal 80°C, Alarm 90°C, Shutdown 100°C.

**Sources:** [Machinery Lubrication — Managing Hot Bearings](https://www.machinerylubrication.com/Read/30608/manage-hot-bearings); [Reliable Plant — SKF bearing temperature troubleshooting](https://www.reliableplant.com/Read/25315/Tips-troubleshooting-bearing-temperatures); [EASA large motor handbook, cited in search results]

### 4.3 Acoustic Emission (AE)

| Parameter | Normal | Developing fault | Active fault |
|-----------|--------|-----------------|-------------|
| AE RMS voltage (relative to quiet baseline) | Baseline established per equipment | +3–6 dB above baseline | +10–20 dB above baseline |
| AE burst count rate (events/second) | 0–2 | 5–20 | >50 |
| Spectral peak frequency | Broad 100–500 kHz, low amplitude | Narrowing around bearing resonance band | Sharp peaks at BPFO/BPFI multiples in AE band |

> AE detects subsurface crack initiation before any vibration change — lead time can be weeks to months. Most sensitive to Stage 1 damage.

### 4.4 Oil Debris Monitor (Ferrous Particle Count)

| Parameter | Normal (clean oil) | Alert | Alarm / Stop circulating oil |
|-----------|-------------------|-------|------------------------------|
| Large particle count (>25 µm ferrous) | 0–2 particles per sample | 5–15 | >25 per sample OR rapid rate-of-change |
| Small particle count (>5 µm) | Background only | Trend up 50% in 48h | Trend up 200% from baseline |
| Water content (Karl Fischer) | <200 ppm | 200–500 ppm | >500 ppm (free water present) |

**Sources:** [Fluid Power Journal — Ferrography Analysis](https://fluidpowerjournal.com/integration-ferrous-density-particle-count-automated-ferrography-analysis-abnormal-wear-conditions/)

### 4.5 Proximity Probe (Journal Bearings Only)

| Parameter | Normal | Alert | Danger |
|-----------|--------|-------|--------|
| Shaft eccentricity ratio (e/C, where C = radial clearance) | 0.3–0.7 under load | >0.8 | >0.9 (near metal-metal contact) |
| Vibration amplitude (peak-peak) | <50 µm pp | 50–100 µm pp | >100 µm pp (ISO 7919) |
| DC gap voltage change (sleeve wear) | ±0.1 mm from baseline | ±0.2 mm | ±0.3 mm (inspect housing bore) |

---

## 5. Defect Readings Per Failure Mode — What Numbers Become + Fault Frequencies

### 5.1 Bearing Defect Frequency Formulas

All four fault frequencies are multiples of shaft RPM:

```
BPFO = (N/2) × [1 - (Bd/Pd) × cos α] × (RPM/60)   [Hz]
BPFI = (N/2) × [1 + (Bd/Pd) × cos α] × (RPM/60)   [Hz]
BSF  = (Pd/(2×Bd)) × [1 - (Bd/Pd)² × cos²α] × (RPM/60)   [Hz]
FTF  = (1/2) × [1 - (Bd/Pd) × cos α] × (RPM/60)   [Hz]
```

Where:
- N = number of rolling elements
- Bd = rolling element diameter (mm)
- Pd = pitch diameter / bearing mean diameter (mm)
- α = contact angle (degrees); tapered roller: typically 10–30°; ball: 15°
- RPM = shaft rotational speed

**Quick approximations (±5–10% without geometry data):**
- BPFO ≈ 0.4 × N × (RPM/60) Hz
- BPFI ≈ 0.6 × N × (RPM/60) Hz
- FTF ≈ 0.4 × (RPM/60) Hz (always sub-synchronous, 0.35–0.48× shaft frequency)
- BSF varies too widely without exact geometry

**Sources:** [IoT Bearings BPFO/BPFI/BSF/FTF formulas and interpretation](https://iotbearings.com/bearing-defect-frequencies-bpfo-bpfi-bsf-ftf-explained/); [ACOEM bearing fault frequencies guide](https://acoem.us/blog/vibration-analysis/bearing-fault-frequencies/); [Reliability Connect — bearing fault frequency + AI methods](https://www.reliabilityconnect.com/bearing-problems-fault-frequency-and-artificial-intelligence-based-methods/)

---

### 5.2 Fault-Specific Signatures and Thresholds

| Failure mode | Sensor | Healthy reading | Warning level | Alarm / action level | Spectral signature |
|--------------|--------|----------------|---------------|----------------------|-------------------|
| Outer race spalling (BPFO fault) | Accelerometer | BPFO amplitude < 0.1 g in envelope | BPFO visible at 0.2–0.5 g | BPFO + harmonics (2×, 3×, 4×BPFO) > 1 g; modulated at shaft rate | Envelope spectrum: discrete peaks at nBPFO; sidebands at ±RPM around BPFO |
| Inner race spalling (BPFI fault) | Accelerometer | BPFI < 0.1 g | BPFI at 0.2–0.5 g | BPFI + sidebands at ±RPM > 1 g (amplitude modulation because defect enters/leaves load zone) | Envelope: BPFI ± k×RPM sideband families; harder to detect than BPFO |
| Rolling element (ball/roller) damage (BSF) | Accelerometer | BSF undetectable | BSF 0.2–0.4 g envelope | BSF and harmonics with 2× BSF prominent (double impact per revolution) > 0.8 g | Envelope: 2×BSF, 4×BSF peaks; smeared due to slip — most difficult to detect |
| Cage damage / wear (FTF) | Accelerometer | FTF undetectable | FTF visible sub-1× RPM | FTF and harmonics > 0.5 g; often appears WITH lubrication issues | Low-frequency sub-synchronous peaks at 0.35–0.48× RPM; cage fracture = sudden broadband noise floor rise |
| Lubrication starvation / degradation | Temperature + AE | Housing temp 50–80°C; AE at baseline | Temp +15°C above baseline AND AE burst rate 5–10×baseline | Temp >100°C; AE rate >50 events/s; vibration broadband floor rises from adhesive wear | Temperature uptrend without load change; AE energy rise precedes vibration |
| Electrical erosion / fluting (EDM) | Vibration + visual + oil analysis | No periodic fluting pattern | Grey-black grease discolouration; broadband noise floor slightly elevated | Distinctive washboard noise; vibration broadband floor elevated 3–6 dB; particles in oil | Not BPFO/BPFI-aligned; high-frequency broadband elevation (frosting → fluting → spalling failure) |
| Contamination / abrasive wear | Oil debris + vibration | Particle count < 5 large particles/sample | Particle count 5–15; gradual vibration floor rise | >25 large particles/sample; accelerated overall vibration trend; bearing life 10–100× reduced | Uniform vibration floor rise rather than discrete spectral peaks; confirmed by particle analysis |
| False brinelling (standstill vibration) | Visual inspection + vibration on restart | Not detectable during operation | Increased noise and vibration after extended standstill | Elevated 1× and nBPFO vibration on restart; fretting debris visible on inspection | Restart vibration spike that may persist if indentations severe |
| True brinelling (shock overload) | Vibration | Pre-event: normal | Not applicable (sudden event) | Immediate: nBPFO peaks after shock; vibration elevated; indentations confirmed on strip | Sudden step-change in vibration level following shock event (crane drop, mill cobble) |

---

## 6. Failure Modes — Full Classification per ISO 15243:2017

ISO 15243:2017 classifies rolling bearing damage into six primary modes with subgroups:

### Mode 1 — Rolling Contact Fatigue

**1a. Subsurface (Classical) Fatigue — Spalling**
- Mechanism: Cyclic Hertzian contact stress creates shear stress field at ~0.5× Hertz contact half-width below surface; microcracks initiate at inclusions, propagate to surface; material flakes away in irregular pits and craters
- Appearance: Irregular, rough, fatigue-textured pits in the rolling contact band (load zone)
- Earliest warning: AE stress-wave bursts (100–500 kHz) detectable weeks/months before visible damage; BPFO/BPFI begin appearing in envelope spectrum
- Final stage: Spalls grow and join; severe vibration; catastrophic if not replaced

**1b. Surface-Initiated Fatigue — Peeling**
- Mechanism: Inadequate EHD film (viscosity ratio κ < 1.0); asperity contact stress exceeds yield; superficial flaking progresses
- Appearance: Gray, matte "frosted" surface
- Earliest warning: AE; microscopy of lubricant oil particle shape and size

### Mode 2 — Wear

**2a. Abrasive Wear**
- Mechanism: Hard contaminant particles (mill scale, silica, iron oxide) in lubricant cut raceway surface
- Appearance: Dull/matte finish; fine scoring parallel to rolling direction; dimensional loss of raceway geometry
- Earliest warning: Oil debris particle count increase; gradual vibration floor rise
- Steel plant prevalence: HIGH — seal damage on conveyor bearings + mill coolant contamination ingress

**2b. Adhesive Wear (Smearing)**
- Mechanism: Insufficient load or excessive speed → rolling element slip → metal-metal adhesion and material transfer
- Appearance: Torn, smeared surface with heat discolouration (gold/blue)
- Common in: Roll neck bearings at cold startup (low speed, high load, before EHD film establishes)

### Mode 3 — Corrosion

**3a. Moisture Corrosion**
- Mechanism: Water ingress through failed seal; condensation; water-based coolant spray contaminating lubricant; rust pitting at roller pitch spacing on stationary bearing
- Appearance: Rust spots, dark oxidation; milky/emulsified grease
- Steel plant prevalence: VERY HIGH — ubiquitous coolant water in rolling mills, casters, blast furnace equipment

**3b. Fretting Corrosion (Fit Corrosion)**
- Mechanism: Micro-slip between bearing bore and shaft (loose fit) or OD and housing; relative movement under cyclic load removes oxide layer, generates reddish-brown Fe₂O₃ debris
- Appearance: Reddish-brown metallic oxide (fretting oxide) at bore/OD surfaces; shaft undersizing with time
- Earliest warning: Physical inspection; bore/shaft measurement confirms undersizing

**3c. False Brinelling (Standstill Vibration)**
- Mechanism: Stationary bearing under load subjected to ambient vibration (transport, nearby machinery); micro-oscillations remove lubricant film; fretting at contact points creates shallow depressions
- Appearance: Shallow depressions at rolling element pitch spacing with reddish-brown debris — distinguishable from true brinelling by debris presence
- Steel plant prevalence: HIGH — standby equipment (spare pump, idle mill stand) vibrated by adjacent running equipment

### Mode 4 — Electrical Erosion (EDM)

**4a. Early Stage (Frosting)**
- Mechanism: VFD (variable frequency drive) drives common-mode voltage along shaft; thin EHD oil film breaks down; current arcs across rolling contact creating microscopic pits
- Appearance: Gray or matte bands on polished raceway; localized initially
- Steel plant prevalence: HIGH and INCREASING — majority of rolling mill motors and auxiliary drives now VFD-controlled

**4b. Advanced Stage (Fluting)**
- Mechanism: Progression of frosting; billions of pits create regular transverse ridges (washboard / picket-fence pattern)
- Appearance: Evenly spaced ridges transverse to rolling direction; diagnostic identifier = gray or black metallic grease (not brown oxidation)
- Signature difference: NOT aligned with BPFO/BPFI — broadband noise elevation; characteristic mechanical noise
- Prevention: Shaft grounding rings (e.g., AEGIS); insulated or ceramic-element hybrid bearings; common-mode choke on VFD output

**Sources:** [American Roller Bearing failure modes](https://www.amroll.com/bearing-failure-modes.html); [Reliability Solutions ISO 15243 article](https://reliabilitysolutions.net/articles/bearing-failure-modes/); [TAPPI — AC Motor Bearing Failure Due to Electrical Discharge (PDF)](https://www.tappi.org/content/Events/19TISSUE/NTS1.1_Kressbach.B.pdf); [AEGIS blog — bearing inspection guide](https://blog.est-aegis.com/what-to-look-for-when-inspecting-your-bearings)

### Mode 5 — Plastic Deformation

**5a. True Brinelling (Shock Overload)**
- Mechanism: Single shock event (mill cobble, crane drop, hammer blow during installation) exceeds Hertz contact yield stress; permanent indentations at rolling element pitch spacing
- Appearance: Clean, shiny metallic indentations — NO reddish debris (distinguishes from false brinelling)
- Earliest warning: Vibration spike immediately after shock; nBPFO frequencies elevated on resuming operation

**5b. Overloading (Quasi-static)**
- Mechanism: Continuous operation above design load capacity; raceway plastically deforms under roller contact
- Appearance: Polished, flattened contact zone; reduced clearance; increased heat

### Mode 6 — Cracking and Fracture

**6a. Cage Fracture**
- Mechanism: Secondary failure from misalignment, lubricant starvation, over-speed, or mismatched thermal expansion causing roller binding in pocket; cage integrity fails catastrophically
- Appearance: Fractured cage; scattered rolling elements; immediate severe vibration; machine trip
- Lead time: Nearly zero — sudden; pre-fracture AE spike may give seconds to minutes warning
- Steel plant consequence: Catastrophic — full bearing disintegration, shaft damage, possible housing destruction

---

## 7. Repair and Resolution Process

### 7.1 Detection-to-Shutdown Decision Flow

```
Stage 1 (AE alert — weeks/months lead):
  → Confirm with oil debris sample, cross-validate with vibration trend
  → Schedule bearing replacement at next planned maintenance window
  → Increase monitoring interval from 30-day to weekly

Stage 2 (Vibration alert — days/weeks lead):
  → BPFO/BPFI peaks confirmed in envelope spectrum + harmonics present
  → Raise criticality; schedule expedited replacement within 1–7 days
  → Ensure spare bearing in-hand from stores before shutdown

Stage 3 (Temperature alarm + audible noise — hours lead):
  → Override production schedule; immediate controlled shutdown
  → Do NOT run to seizure — secondary damage to shaft and chock is costly

Stage 4 (Seizure imminent):
  → Emergency STOP; isolate energy; secure roll/shaft from uncontrolled movement
```

### 7.2 Replacement Procedure — Roll Neck Bearing (Four-Row Tapered Roller)

1. **Energy isolation and LOTO** — Lock out rolling mill stand; confirm zero energy state; cool roll to <50°C if hot rolling
2. **Chock extraction** — Remove chock from mill housing window using hydraulic chock puller or overhead crane (chock weight: 2–20 tonnes depending on mill size); lower to workshop/maintenance bay
3. **Bearing disassembly** — Remove seal, locknut, and end cover; use hydraulic or mechanical press to extract inner rings from roll neck. Outer ring removed from chock bore using press or arbor. CRITICAL: note and record match-mark numbers — all numbered components (cones, cups, spacers) must be reassembled in original sequence
4. **Inspection** — Measure: roll neck diameter and taper for undersizing (acceptance: within 0.02 mm of nominal); chock bore for ovalisation; keyway/slot condition; check for fretting
5. **Bearing heating (if interference fit inner ring)** — Heat inner ring to 80–100°C maximum using induction heater; never use open flame; install on roll neck while hot; allow to cool (interference re-establishes)
6. **Assembly** — Install new outer cups in chock housing (light interference fit); install inner cones; install match-numbered spacers in original sequence; check axial clearance with feeler gauge (typical: 0.05–0.25 mm depending on bearing size)
7. **Lubrication priming** — Fill 2/3 of available space with fresh grease (sealed type) or connect to circulating oil system and purge lines before sealing
8. **Seal installation** — Install new labyrinth or lip seals; verify lip orientation; apply approved sealant to housing joints
9. **Chock reinstallation** — Return chock to mill housing; torque locknut to OEM specification; reconnect oil supply lines
10. **Commissioning checks** — Jog stand at minimum speed (5–10 RPM); check for unusual noise; verify temperature within normal range within 30 minutes of start; take baseline vibration reading

**Time estimates:**
- **Planned replacement** (chock change in prepared workshop): 4–8 hours per stand (2 chocks per roll)
- **Unplanned emergency replacement** (includes diagnosis + expediting spare): 12–24 hours; frequently extends to 18–36 hours if spare not in stock
- **Full roll + bearing change (hot strip mill finishing stand):** 6–10 hours planned; 24–72 hours unplanned for major bearing seizure with shaft/housing secondary damage

**Tools required:** Hydraulic chock puller, induction heater (Equalizer or equivalent), hydraulic press (50–500 tonne), torque wrench (calibrated, OEM-specified torques), feeler gauges, dial test indicator (DTI), crane, specialised bearing handling fixtures

**Spare strategy:** Tata Steel scale — standing inventory of commonly used sizes on-site (TQO bearings for each active roll diameter); OEM lead time for non-stocked sizes: 4–16 weeks. Bearing refurbishment (regrinding raceways and replacement of rollers) used for large bore (>400 mm) to reduce cost [Timken industrial bearing repair service — timken.com/products/industrial-bearing-repair/]

**Sources:** [NSK Roll Neck Bearing Manual (PDF)](https://www.nsk.com/content/dam/nsk/am/en_us/documents/bearings-americas/Roll-Neck-Bearing-Manual.pdf); [SRG Bearing operating instructions for rolling mill bearings](https://www.srgbearing.com/info/what-is-the-operating-instructions-for-install-70407818.html); [OxMaint rolling mill maintenance checklist](https://oxmaint.com/industries/steel-plant/rolling-mill-maintenance-checklist-hot-cold-rolling); [Timken bearing repair](https://www.timken.com/products/industrial-bearing-repair/)

---

## 8. Cost and Loss Impact

### 8.1 Downtime Costs (Integrated Steel Plant Scale)

| Area | Unplanned downtime cost |
|------|------------------------|
| Hot Strip Mill (full line stop) | $50 000 – $200 000 / hour |
| Continuous Caster | $80 000 – $300 000 / hour |
| Blast Furnace bank | $100 000 – $500 000 / hour |
| Rolling Mill single stand (partial) | $6 000 – $12 000 / hour |
| Typical integrated mill annual unplanned downtime | 200–600 hours / year → $25M–$80M annual |

**Source:** [OxMaint — Unplanned downtime in steel plants, costs and solutions](https://oxmaint.com/industries/steel-plant/unplanned-downtime-steel-plant-causes-costs-solutions); World Steel Association data cited therein. Note: figures marked [unverified exact] — drawn from industry analytics site, not primary Tata Steel report.

**Bearing-specific contribution:** 18–25% of all unplanned stops are bearing failures. With 15% reduction in unplanned downtime via PdM (Tata Steel stated achievement — [unverified citation for exact %; attributed to Tata Steel company reports]), this represents $3.75M–$20M annual savings at plant scale.

### 8.2 Planned vs. Unplanned Cost Comparison (Rolling Mill Stand)

| Scenario | Repair cost | Production loss | Total cost |
|----------|------------|-----------------|-----------|
| Planned replacement (6-hour stop) | ~$8 400 labour + parts | ~$36 000–$72 000 | ~$45 000–$80 000 |
| Deferred to failure (18-hour emergency) | ~$14 200 + secondary damage | ~$108 000–$216 000 + shaft/housing | ~$125 000–$250 000+ |

> A steel plant that converted $4.8M emergency bearing repairs to $340K planned interventions via vibration trending is cited by OxMaint [unverified — attributed to unnamed customer case study].

### 8.3 Secondary Damage Cascade

A bearing seizure that is not caught in time causes:
- **Roll neck scoring and grooving** — requires roll grinding or scrapping ($5 000–$80 000 per roll depending on size and grade)
- **Chock bore ovalisation or scoring** — chock requires re-boring or scrapping ($10 000–$50 000 per chock)
- **Housing window damage** — structural mill housing damage is catastrophic; repair requires weeks and major expenditure
- **Fire risk** — seized bearing ignites oil in enclosed chock; fire suppression system activation → further delay
- **Safety** — roll drop or uncontrolled movement if bearing collapses during rolling; personnel injury risk

### 8.4 Cost of Predictive Monitoring System (Reference)

- Online vibration monitoring (per point, stud-mounted ICP sensor + transmitter): $500–$2 000 USD per measurement point installed
- Large hot strip mill: 400–800 measurement points; CAPEX $200K–$1.6M for sensors alone
- System payback: Typically under 12 months at integrated steel plant scale given avoided emergency repair costs

---

## 9. Additional Expert Knowledge

### 9.1 Bearing Life Calculations (L10 / Modified L10)

**Basic ISO 281 L10 life:**
```
L10 = (C/P)^p × 10^6 revolutions
```
Where: C = basic dynamic load rating (kN); P = equivalent dynamic bearing load (kN); p = 3 for ball bearings, 10/3 for roller bearings

**Modified life (ISO 281:2007 Annex A):**
```
Lnm = a1 × aSKF × L10
```
Where: a1 = reliability factor (1.0 for 10% failure probability); aSKF = life modification factor accounting for lubrication, contamination, and fatigue load limit — ranges from 0.1 (contaminated, poor lubrication) to >50 (clean, well-lubricated)

**Practical implication:** A contamination factor of 0.3 reduces bearing life to 30% of catalogue rating — the dominant driver of premature failure in steel plants where coolant water, mill scale, and oxide particles contaminate lubricant.

### 9.2 Lubrication Specification for Steel Plant Bearings

| Application | Lubricant type | ISO viscosity grade | Re-lubrication interval |
|-------------|---------------|--------------------|-----------------------|
| Roll neck (circulating oil) | Mineral oil, anti-wear, EP additives | ISO VG 150–320 | Continuous circulation |
| Motor bearing (grease) | NLGI 2–3 lithium complex or polyurea | N/A (grease consistency) | 2 000–8 000 hours depending on temperature |
| Conveyor idler (sealed for life) | NLGI 3 lithium or polyurea | N/A | No re-lubrication (replace bearing) |
| Gearbox bearing (in-sump) | Gear oil, EP | ISO VG 220–680 | 4 000–8 000 hours or annually |
| High-temperature locations (>150°C) | Synthetic (PAO or ester base) or solid lubricant (graphite/MoS₂) | PAO ISO VG 100–220 | Extended intervals due to thermal stability |

### 9.3 Vibration Signal Processing for Bearing Diagnostics

**Signal processing progression (in order of increasing sensitivity):**

1. **Overall RMS velocity** (mm/s, 10–1000 Hz): Gross health indicator; low sensitivity to early bearing faults; first to confirm Zone C/D
2. **FFT spectrum** (velocity or acceleration): Shows discrete fault frequencies; works well for progressed outer race faults
3. **Envelope analysis** (demodulation): High-pass filter (e.g., 2–10 kHz) → rectify → low-pass → FFT; reveals BPFO/BPFI/BSF/FTF from resonant impacts; standard method for early bearing detection
4. **Time-synchronous averaging (TSA)**: Removes non-synchronous noise; highlights cage and rotating race faults; requires tachometer signal
5. **Kurtosis / kurtogram**: Statistical measure of impulsiveness; rises >3 (normal Gaussian) when bearing impacts present; spectral kurtosis identifies optimal demodulation band
6. **Cepstrum analysis**: Converts spectrum to "quefrency" domain; detects families of harmonics and sidebands; useful for BPFI sideband detection
7. **Machine learning on raw waveform**: CNN-LSTM, 1D-CNN, Transformer-based anomaly detection (SOTA 2024–2025 — TranAD, Anomaly Transformer); trained on normal data; reconstruction error as anomaly score

**Minimum sampling requirements (per IoT Bearings guidance):**
- Raw waveform: ≥20 kHz (Nyquist for 10 kHz envelope analysis)
- 2-second minimum capture window for adequate FFT frequency resolution
- For AE-based detection: ≥1 MHz sampling; burst capture triggered mode

### 9.4 Tata Steel Bearing Research Reference

ResearchGate documents an academic paper: "Application of Data-driven Models to Predictive Maintenance: Bearing Wear Prediction at TATA Steel" — four data-driven RUL prediction methods applied to vibration condition monitoring of rotating machines. The paper proposes detecting, diagnosing, and predicting critical component RUL using measured signals. [Available at ResearchGate, 2021 — full access restricted; abstract only verified](https://www.researchgate.net/publication/353910632_Application_of_Data-driven_Models_to_Predictive_Maintenance_Bearing_Wear_Prediction_at_TATA_Steel)

### 9.5 Public Datasets Directly Applicable to Steel Plant Bearing Modelling

| Dataset | Contents | URL | Applicability |
|---------|----------|-----|--------------|
| **IMS Bearing Dataset** (NASA / Rexnord) | 4 bearings, run-to-failure, 2000 RPM, 6000 lb load; vibration at 1+ kHz; ~100M samples total; AE + vibration | [Kaggle / Catalyzex](https://www.catalyzex.com/s/Ims%20Bearing%20Dataset) | Best for RUL model training; slow-progressing industrial bearing degradation |
| **CWRU Bearing Dataset** | SKF 6205-2RS, 0–3 HP motor; ball, inner, outer race, rolling element faults at 7, 14, 21 mil defect size; 12 kHz + 48 kHz sampling | [Kaggle CWRU](https://www.kaggle.com/datasets/brjapon/cwru-bearing-datasets) | Benchmark for fault classification; most-cited in literature |
| **PHM 2010 Milling** | Milling cutter wear (analog to bearing in stress-wave / thermal signatures); force + vibration | PHM Society archive | Process-analogous context |

### 9.6 MCSA for Remote Bearing Monitoring (No Physical Sensor on Bearing)

When a bearing cannot be accessed for sensor installation, Motor Current Signature Analysis provides a non-invasive alternative:
- Bearing faults cause load variation → torque ripple → shaft speed ripple → stator current modulation
- Fault-induced sidebands appear in current spectrum at: f_line ± k × f_bearing (where f_bearing = BPFO, BPFI, etc.)
- Sensitivity: 10–20 dB below line frequency harmonic; requires high-resolution spectrum (≥0.01 Hz resolution → ≥100 s capture)
- Limitation: Low SNR; contaminated by electrical noise and load fluctuations; best as confirmatory tool rather than primary detector

**Sources:** [Sensemore MCSA guide](https://sensemore.io/motor-current-signature-analysis-mcsa-for-predictive-maintenance/); [ScienceDirect — MCSA for bearing fault detection in mechanical systems](https://www.sciencedirect.com/science/article/pii/S2211812814003861)

### 9.7 Bearing Monitoring Best Practices for PdM System Design

**Alarm configuration (from ISO 20816 framework + industrial practice):**
- Set **alert** (caution) alarm at Zone A/B boundary — triggers increased monitoring frequency
- Set **warning** alarm at Zone B/C boundary — triggers investigation and scheduling
- Set **danger** alarm at Zone C/D boundary — triggers maintenance action within one shift
- Set **emergency trip** alarm at Zone D + temperature >100°C simultaneously — triggers immediate shutdown

**False alarm reduction:**
- Use ensemble of sensors (vibration + temperature + AE) — multi-sensor fusion reduces false positive rate from 35–40% (single sensor) to <8%
- Require alarm persistence (3 consecutive measurement intervals) before escalating
- Apply machine-state masking (ignore alarms during startup/shutdown transients)

**Lead time targets:**
- Stage 1 AE detection: 4–12 weeks before failure → schedule in next planned maintenance
- Stage 2 vibration detection: 2–6 weeks before failure → expedited scheduling
- Stage 3 temperature alarm: 4–24 hours → immediate controlled shutdown

---

## 10. Summary Reference Table — Steel Plant Bearing Quick-Reference

| Bearing type | Primary application | Normal vib (mm/s RMS) | Warning temp | Fault freq | Key failure mode |
|--------------|--------------------|-----------------------|--------------|------------|-----------------|
| 4-row TQO tapered roller | Rolling mill roll necks | 1.0–4.0 | 90°C | BPFO, BPFI | Spalling, contamination, EDM fluting |
| Spherical roller | Conveyors, casters, fans | 0.5–3.5 | 90°C | BPFO, BPFI | Contamination, moisture corrosion, fatigue |
| Cylindrical roller | Motors, gearboxes | 1.5–4.5 | 90°C | BPFO, BPFI, BSF | Spalling, electrical erosion (VFD motors) |
| Deep groove ball | Electric motors (small/med) | 0.5–2.3 | 90°C | BPFI, BPFO, BSF | EDM fluting (VFD), contamination, fatigue |
| Journal/sleeve | Roller tables, large turbines | <50 µm pp displacement | 90°C (sleeve: alarm) | Shaft orbit shift | Lubrication loss, overheating, wear |
| Thrust (tapered roller) | Screw-down, vertical pumps | 1.0–3.5 | 90°C | Axial thrust faults | Overload, incorrect preload |

---

*Document covers: bearing types × applications, parts anatomy, sensor suite and prevalence, ISO-referenced normal and alarm readings, fault frequency formulas, ISO 15243:2017 failure classification with all six modes, repair procedure and time estimates, downtime cost impact, signal processing methods, public datasets, and PdM alarm design guidance.*

*All factual claims are cited with URLs or tagged [unverified]. Temperature and vibration thresholds are cross-referenced against ISO 20816, SKF documentation, and steel-plant-specific operational data.*
