# 08 — Mill Rolls & Mill Stands: Deep PdM Reference
**Scope:** Hot Strip Mill (HSM), Plate Mill, Cold Rolling Mill — rolls, stands, and roll-shop lifecycle  
**Last updated:** 2026-06-08  
**Verification legend:** [verified] = backed by cited public source; [unverified] = plausible industry knowledge, not confirmed by a primary source in this document

---

## 1. TYPES — Rolls and Stand Configurations

### 1.1 Roll Categories

| Role | Where Used | Typical Barrel ⌀ | Typical Barrel Length | Material |
|---|---|---|---|---|
| **Work Roll (WR)** | Every stand; in direct contact with strip | HSM: 600–800 mm; CRM: 400–600 mm | 1,200–2,100 mm | HSM F1-F4: High-Cr centrifugal composite, HSD 60–70; HSM F5-F7: ICDP or HSS, HSD 70–80 / 60–66 HRC; CRM: Forged alloy steel, 58–66 HRC surface [verified — hanmillrolls.com] |
| **Backup Roll (BUR)** | 4-high and 6-high mills; supports WR against deflection | HSM: 1,200–1,600 mm; CRM: 1,000–1,400 mm | 1,400–2,500 mm | Forged vacuum-degassed alloy steel; HSM example: 1,550 mm ⌀ × 2,230 mm × 5,830 mm total, ≈46 tonnes [verified — SAIL tenders PDF]; plate mill: 2,200 mm ⌀ × 4,300 mm × 9,860 mm, ≈170 tonnes [verified — SAIL] |
| **Intermediate Roll (IMR)** | 6-high mills (e.g., Sendzimir / HC mills in CRM) | 400–600 mm | Matches WR barrel | High-Cr or forged steel, 58–64 HRC |

### 1.2 Stand Configurations

| Config | Description | Typical Location |
|---|---|---|
| **2-High** | One WR pair; roughing or skin-pass | Roughing stands (slab breakdown), skin-pass mill |
| **4-High** | WR pair + BUR pair; dominant in HSM finishing | HSM F1–F7; plate mill; tandem CRM |
| **6-High (HC/UCM)** | WR + IMR + BUR all pairs; axial shifting for shape control | Final stands of advanced CRM or combined finishing stand |
| **Cluster (Sendzimir / 20-Hi)** | Multiple small WRs backed by cluster of idler rolls | Ultra-thin foil, stainless, silicon steel |

### 1.3 Stand Positions — Hot Strip Mill (Typical 7-Stand Finishing)

| Stand | Grade | Roll Material | Campaign Targets |
|---|---|---|---|
| R1–R2 (Roughing) | 60CrNiMo; semi-steel | HSD 40–65 | 20,000–60,000 t/campaign [unverified — aggregate estimate] |
| F1–F4 (Early Finishing) | High-Cr centrifugal | HSD 60–70 | 60,000–120,000 t/campaign [unverified] |
| F5–F7 (Late Finishing, surface-critical) | ICDP / HSS | HSD 70–80 | 4,000–8,000 t before WR change [verified — oxmaint.com]; 30–90 min rolling time per WR change [verified — oxmaint.com] |

---

## 2. PARTS BREAKDOWN

### 2.1 Work Roll Anatomy

```
[Drive Spindle Coupling]
        |
  [Wobbler/Drive End Neck] — Journal surface: mirror finish 50–100 µm Ra [verified — ispatguru.com]
        |
  [Roll Neck — Drive Side] ←— Four-row tapered roller bearing in chock
        |
  [Roll Barrel] ←— Contact zone with strip; surface hardness per grade above
        |
  [Roll Neck — Operator Side] ←— Mirror four-row tapered bearing in chock
        |
  [Operator Neck]
```

### 2.2 Backup Roll Anatomy

Same neck-barrel-neck topology; BUR necks are larger-diameter and mount oil-film hydrodynamic bearings [verified — ispatguru.com] or large four-row tapered roller bearings. Barrel diameter governs strip width capability. BUR weight 46–170 t depending on mill size.

### 2.3 Chock Assembly (per roll end)

- **Chock body:** Cast or forged steel housing that encloses the bearing and transmits rolling force to the mill housing window.
- **Bearing:** Four-row tapered roller bearing (FTRB) — ID range 120–1,320 mm; four rows split into two back-to-back pairs for combined radial (>30 MN capability for BUR in HSM stands) and bidirectional axial load [verified — NSK, SKF product pages + oxmaint.com]. WR chocks use smaller FTRBs or cylindrical roller bearings.
- **Seals:** Labyrinth + contact seals to exclude mill scale and water.
- **Balance cylinders:** Hydraulic actuators that lift the top roll assembly during strip threading, preventing uncontrolled gap drop.
- **Bending blocks / bending actuators:** Hydraulic cylinders in the chock that apply positive or negative roll bending force (typically ±500–2,000 kN per chock) for crown and flatness control.

### 2.4 Screwdown / HGC (Hydraulic Gap Control)

- **Mechanical screwdown:** Threaded screw + worm gear; coarse positioning, ±0.1 mm class.
- **HGC (Hydraulic Automatic Gap Control):** Servo-hydraulic cylinder; fine positioning response for thickness regulation. Position accuracy in the micron range; PID / MPC closed-loop [verified — Danieli, ResearchGate].
- **Roll gap position sensor:** LVDT or linear encoder on each screwdown column (operator + drive side independently). Asymmetric readings signal roll misalignment or chock wear.

### 2.5 Drive Spindles

- **Universal spindle / articulated spindle:** Transmit motor torque to roll; allow vertical adjustment of roll gap. Critical wear point: spider crosses and yoke bores.
- Spindle coupling wear generates 2× and 3× rotational frequency harmonics in vibration spectrum [verified — oxmaint.com vibration blog].

---

## 3. SENSORS — TYPES AND SIGNAL PATHS

| Sensor | Measurement | Location | Signal / Protocol |
|---|---|---|---|
| **Load cell / roll force transducer** | Rolling force (MN); asymmetric DS vs OS | Under screwdown column cap or integrated in HGC cylinder | 4–20 mA or digital fieldbus; OPC-UA to L2 historian [verified — msnst.com, blhnobel.com] |
| **HGC position sensor (LVDT)** | Roll gap position (mm, µm resolution) | On each hydraulic cylinder | Direct to AGC controller |
| **Chock bearing temperature RTD/thermocouple** | Bearing temperature (°C) | Embedded in chock body, lubricant return line | 4–20 mA; alarm/trip hardwired |
| **Chock accelerometer / vibration** | Vibration (mm/s RMS or g); chatter frequency spectrum | Bolted to chock or mill housing | ICP accelerometer → vibration analyser; FFT bands to historian [verified — oxmaint.com] |
| **Roll surface inspection camera / eddy-current scanner** | Surface cracks, roughness bands, chatter marks | Inline scan head above/below strip exit | Digital image / eddy-current signal → defect map |
| **Motor torque / current transducer** | Drive torque (kNm) or motor current (A) | Mill motor MCC | L1 PLC; historian |
| **Strip thickness gauge (X-ray / isotope)** | Exit thickness (mm) | Entry + exit of each stand | Closes AGC loop |
| **Strip width gauge** | Width (mm); edge waviness | After last finishing stand | CCD laser gauge |
| **Roll shop hardness tester** | Surface hardness (HSD / HRC) | Roll shop, post-campaign | Manual or CNC-integrated |

---

## 4. NORMAL SENSOR READINGS

| Sensor | Normal Operating Range | Notes |
|---|---|---|
| **Rolling force (WR, F-stands)** | 10–30 MN per stand | Depends on strip width, gauge, grade; BUR in large HSM: forces exceeding 30 MN [verified — oxmaint.com] |
| **Screwdown position (HGC)** | Within ±0.05 mm of setpoint during steady-state rolling | Transient excursions at head/tail end |
| **Chock bearing temperature (FTRB, WR)** | 40–70 °C above ambient; absolute typically 50–80 °C | Oil-film BUR bearings: 50–75 °C in lube return |
| **Chock bearing vibration (steady-state)** | < 2.0 mils (50 µm) peak-to-peak; or < 2.0 mm/s RMS [verified — plcdcspro.com, oxmaint.com] | Measured at chock accelerometer |
| **Roll surface roughness (WR exit CRM)** | Ra 0.3–1.5 µm depending on product grade | Roughness degrades toward end of campaign |
| **Motor torque per stand** | Within 5–10% of L2 model setpoint | Significant asymmetry (DS vs OS) flags misalignment |
| **Roll wear rate (HSS WR)** | 0.01–0.03 mm / 1,000 t [verified — hanmillrolls.com] | Cast materials: 0.02–0.06 mm / 1,000 t |
| **WR crown profile deviation** | < 0.02 mm from target crown | Triggers regrind scheduling when exceeded |

---

## 5. DEFECT / FAILURE READINGS AND THRESHOLDS

### 5.1 Chock Bearing Degradation (FTRB)

| Stage | Temperature | Vibration | Action |
|---|---|---|---|
| Healthy | < 80 °C | < 2.0 mils / 2 mm/s | Monitor |
| Early fault (BPFO/BPFI side-band growth) | 80–85 °C | 2.0–4.0 mils; BPFO harmonics visible in FFT | Increase inspection interval; plan roll change |
| Alarm | 85 °C [verified — plcdcspro.com] | 5.0 mils / 5 mm/s [verified — plcdcspro.com] | Roll change at next scheduled break |
| Trip / Emergency pull | 105 °C [verified — plcdcspro.com] | 8.0 mils / 8 mm/s [verified — plcdcspro.com] | Immediate roll change; cobble risk |
| Fatal seizure risk | > 125 °C continuous [verified — various bearing OEMs] | Broadband noise floor rise | Emergency stop |
| Lead time before failure | Detectable vibration elevation 2–4 campaigns before failure; 62% of HSM bearing failures follow this pattern [verified — oxmaint.com] | | |

### 5.2 Chatter / Mill Vibration

| Mode | Frequency | Detection Signature | Threshold / Action |
|---|---|---|---|
| 3rd-octave chatter | 100–250 Hz; most common 110–170 Hz [verified — Wiley/onlinelibrary, innovaltec.com] | Sharp peak in accelerometer FFT at characteristic frequency; periodic chatter marks on strip (pitch = strip speed / chatter freq) | Reduce rolling speed by 5–15%; adjust emulsion; investigate roll eccentricity |
| 5th-octave chatter | 500–1,000 Hz [unverified — aggregate estimate] | High-frequency accelerometer peak; fine-pitch marks on strip | Roll change; check WR roundness |
| Mill bounce (structural resonance) | 10–30 Hz | 1× or 2× at structural natural frequency; large-amplitude housing vibration | Speed detuning; check spindle coupling wear |
| Chatter mark strip rejection | > 0.5 µm periodic thickness variation at chatter pitch on strip surface | | Grade downgrade or scrap |

**Early sensor sign of chatter onset:** subharmonic broadband floor rise 3–5 dB before discrete peaks appear [verified — oxmaint.com vibration blog].

### 5.3 Roll Force Anomalies

| Anomaly | Reading Pattern | Likely Cause |
|---|---|---|
| Gradual force increase over campaign | +5–15% above model setpoint | Roll wear, bearing drag increase, lubrication loss [verified — msnst.com] |
| Asymmetric force (DS ≠ OS by > 5%) | One column higher than other | Roll misalignment; chock clearance excess; bearing fault |
| Sudden force spike > 150% of setpoint | Impulsive | Strip cobble incoming; weld failure; cold mark in strip |
| Force drop to near-zero mid-strip | Loss of bite | Breakout precursor; spindle failure |

### 5.4 Roll Thermal Fatigue (Fire Cracking) — Surface

- Work roll surface cycles from ~600 °C (strip contact zone) to ~100 °C (cooling water zone) every revolution [verified — PMC/MDPI materials paper].
- A 16 °C increase in surface temperature enhances crack growth rate by 2.58× [verified — academia.edu thermal fatigue paper].
- Early sign: band fire-cracks (mosaic pattern) matching strip width; ladder cracks (longitudinal) indicating blocked cooling nozzle.
- Detection: visual inspection at roll change; eddy-current or dye-penetrant at roll shop.
- Critical threshold: if cracks deeper than 5 mm detected by UT, roll must be removed for deeper regrind or condemned.

### 5.5 Subsurface Spalling (Back-up Roll)

- Hardness threshold: surface HSD > 65 + work-hardening increase > HSD 3 → micro-crack initiation [verified — lmmrolls.com BUR spalling analysis].
- Pit size trigger: spalling depth > 3 mm or diameter > 10 mm → immediate roll change [verified — oxmaint.com cobble prevention].
- Visual: "cat's tongue" shaped chunks detaching from barrel; silvery oxide-covered circumferential peel streaks.
- 70 °C surface-to-core temperature gradient → ~1,100 kg/cm² longitudinal tensile stress → thermal breakage risk [verified — ispatguru.com abnormalities].

### 5.6 Roll Neck / Journal Fracture

- Fatigue crack initiates in fillet radius between barrel and neck (stress concentration zone).
- Bending fracture: 45° fracture surface under shock load (cobble, hard spot) [verified — ispatguru.com].
- Torsional failure: cone-shaped fracture at drive end when torque exceeds material strength.
- Core residual tensile stress can reach 12 kg/mm²; longitudinal thermal fracture threshold ~7–10 kg/mm² additional stress [verified — lmmworkrolls.com].
- NDT sign: ultrasonic A-scan indication in neck fillet before through-crack; phased-array can locate initiation zone.

---

## 6. FAILURE MODES — CATALOGUE

| # | Failure Mode | Root Cause | Earliest Detectable Sign | Detection Method | Lead Time |
|---|---|---|---|---|---|
| 1 | **Roll thermal fatigue / fire cracking** | Cyclic thermal gradient 600°C↔100°C per revolution; cooling blockage; prolonged rolling stop with hot strip between rolls | Band or ladder surface cracks | Eddy current or dye-penetrant at roll change | Visual at next roll change; ultrasonic for depth |
| 2 | **Subsurface spalling (WR/BUR)** | Contact fatigue + work hardening exceeding HSD threshold; metallurgical inclusions as crack seeds | Circumferential peel stripes; increasing surface roughness; strip surface marking | Ultrasonic UT on barrel; surface inspection camera on strip | 55% reduction in spalling with UT programs [verified — ndt.net NDT paper]; 2–4 campaigns lead time |
| 3 | **Roll fracture (barrel)** | Casting defects (shrinkage, porosity); abnormal structure (unspheroidized graphite → 10–20× stress concentration) [verified — lmmworkrolls.com]; cobble shock | Sudden torque spike; load cell spike > 2× setpoint; audible crack | Real-time load cell and torque monitoring | Milliseconds — catastrophic; prevention only via pre-campaign NDT |
| 4 | **Roll neck fatigue fracture** | Alternating bending stress in fillet; inadequate fillet radius; excessive residual stress | Phased-array UT echo in fillet zone | Ultrasonic phased-array at roll shop every major campaign | Hours to days if crack detected early |
| 5 | **Chock bearing failure (FTRB)** | Water ingress through worn seals; inadequate lubrication; overload from cobble shock | Temperature rise 80–85 °C; BPFO/BPFI frequency harmonics in vibration spectrum | Bearing vibration analyser; chock temp RTD | 2–4 campaigns (~8–32 hours rolling) detectable lead time [verified — oxmaint.com] |
| 6 | **Roll eccentricity** | Manufacturing eccentricity; uneven regrind; chock clearance excess | 1× rotational frequency peak in vibration; periodic gauge variation at strip matching roll circumference pitch | Vibration FFT; strip thickness gauge correlation | Accumulates over campaign; detectable pre-campaign via roll shop roundness check |
| 7 | **Chatter / regenerative vibration** | Speed-coupled with strip/roll system natural frequency; lubricant film instability; spindle coupling wear | 100–250 Hz FFT peak on chock accelerometer; chatter marks on strip | In-stand accelerometer + real-time FFT analyser | Minutes — can develop rapidly once initiated |
| 8 | **Shell–core interface disbonding** | Oxidation / flux at casting bond layer; thermal cycling stress at interface | UT layer-echo loss; shell separation chunk; strip surface damage | Phased-array UT perpendicular to barrel | Next UT inspection cycle |
| 9 | **Work hardening + spall initiation (BUR shoulder drop)** | Uneven bending force across barrel; roll bending actuator imbalance | Edge spall chunks at DS or OS; asymmetric roll force | Strip edge inspection; load cell DS/OS asymmetry | 1–3 campaigns |
| 10 | **HGC / screwdown position fault** | Seal leakage in hydraulic cylinder; LVDT sensor drift; servo-valve sticking | Thickness gauge deviation > setpoint; DS/OS gap asymmetry | AGC gauge feedback; LVDT self-check | Continuous — detected within one head-end pass |

---

## 7. REPAIR / RESOLUTION PROCESS

### 7.1 Roll Change Cycle

- **Hot strip mill work rolls (F5–F7):** Change every 30–90 min rolling time or 4,000–8,000 t for surface-critical grades [verified — oxmaint.com]; automated roll-change equipment: 8–15 minutes change time [unverified].
- **Hot strip mill work rolls (F1–F4):** Change every 2–4 hours or 15,000–30,000 t [unverified — aggregate estimate].
- **Backup rolls:** Campaign measured in weeks; changed every 4–8 weeks depending on tonnage rolled and diameter reduction; change requires overhead crane (46–170 t lift).

### 7.2 Roll Shop Regrinding

- **CNC roll grinder:** CBN or aluminium-oxide wheel; automated profile measurement + feedback.
- **Work roll regrind material removal:** 0.1–0.5 mm per grind (surface only); deeper grind (20–25 mm) required after fatigue-layer crack detection [verified — lmmrolls.com BUR spalling article].
- **Backup roll regrind:** 1–5 mm per campaign to remove wear and restore crown profile.
- **Inspection post-grind:** Eddy-current scan (surface cracks); ultrasonic scan (subsurface voids, neck fillet); hardness mapping (confirm fatigue layer removal).
- **Regrind time:** WR: 1–4 hours; BUR: 8–24 hours depending on material removal and diameter [unverified].
- **Condemnation diameter:** When barrel diameter drops to scrap limit (typically 60–80 mm below nominal), roll is scrapped. Diameter tracking is per-campaign mandatory data.

### 7.3 NDT Schedule

| Inspection | Method | Interval | What It Finds |
|---|---|---|---|
| Surface crack | Eddy-current + magnetic particle (MPI) | Every regrind | Fire cracks, fatigue peel initiators |
| Subsurface spall/inclusion | Phased-array UT (barrel) | Every 2nd–3rd regrind cycle or post-shock event | Spall initiation voids at 5–30 mm depth |
| Neck fillet integrity | Ultrasonic A-scan or phased-array | Every major campaign | Fatigue crack growth in fillet radius |
| Roll roundness / eccentricity | CMM / laser gauge on grinder | Every regrind | Eccentricity → chatter contribution |
| Hardness map | Shore D / Leeb rebound hardness tester | After each regrind for BURs | Work-hardening layer state — if HSD > 65 + delta HSD > 3, grind deeper [verified — lmmrolls.com] |

Comprehensive NDT programs reduce spalling by approximately 55% in HSMs [verified — ndt.net/wcndt2012 paper].

### 7.4 Chock Rebuild

- Bearing replacement: full FTRB strip-down every 6–18 months or after any thermal/vibration exceedance event.
- Seal replacement: more frequent; every 3–6 months in water-rich HSM environment [unverified].
- Chock bore resurfacing: if fretting corrosion or wear exceeds 0.1 mm diametrical [unverified].
- Bearing pre-set / clearance measurement: critical after reassembly; 0.04 mm bearing clearance deviation produces strip width variation of 1.2 mm [verified — oxmaint.com HSM stands article].

### 7.5 Planned vs. Unplanned

- Mills with active vibration-based PdM achieve 3× better planned-to-reactive ratio on chock changes [verified — oxmaint.com].
- Bearing-related outage reduction: 62% with condition monitoring [verified — oxmaint.com].
- Campaign extension with PdM: 18% average WR campaign length gain [verified — oxmaint.com].

---

## 8. COST / LOSS IMPACT

| Event | Financial Impact | Source |
|---|---|---|
| **Unplanned HSM stand outage** | $180,000 average (including downgrade losses, emergency repair, caster hold) [verified — oxmaint.com] | oxmaint.com HSM stands article |
| **Single cobble event** | $150,000–$500,000 direct damage; $150K–$600K per unplanned hot mill stoppage [verified — arhfoundation.org, oxmaint.com vibration] | Multiple sources |
| **Backup roll replacement (capital)** | > $200,000 per roll [verified — oxmaint.com roll shop article]; total lifecycle cost higher when regrind + logistics included | oxmaint.com |
| **Reactive vs. predictive maintenance annual cost** | Reactive: $4M–$12M/yr; Predictive: $2.5M–$7M/yr per rolling line [verified — oxmaint.com vibration blog] | oxmaint.com |
| **Annual savings from vibration PdM** | $800K–$2.4M per major rolling line [verified — oxmaint.com] | oxmaint.com |
| **Emergency vs. planned repair cost multiplier** | 3–5× higher for emergency repairs [verified — oxmaint.com] | oxmaint.com |
| **Unplanned stopage frequency** | Reactive: 12–24/year; Predictive: 4–8/year [verified — oxmaint.com] | oxmaint.com |
| **Cobble risk multiplier from visible spalling** | Cobble risk increases 12× with visible spalling > 3 mm [verified — oxmaint.com cobble article] | oxmaint.com |
| **Roll-related downtime share** | Bearing failures account for > 35% of unplanned downtime in HSM operations [verified — ifactoryapp.com] | ifactoryapp.com |
| **Quality impact** | 0.04 mm chock clearance deviation → 1.2 mm strip width variation across coil [verified — oxmaint.com] | oxmaint.com |
| **Strip rejection from chatter marks** | Periodic thickness variation > 0.5 µm at chatter pitch → grade downgrade or scrap [unverified — threshold estimate] | — |
| **NDT program ROI** | 55% reduction in spalling failures [verified — ndt.net WCNDT 2012 paper] | ndt.net |

---

## 9. SUPPLEMENTARY — SENSOR-TO-FAILURE MAPPING FOR ML/PdM

This mapping is the direct input for a maintenance AI/wizard agent's feature engineering:

```
Feature                          → Failure Mode(s)
──────────────────────────────────────────────────────
Chock bearing temp (°C)          → FTRB degradation (mode 5)
BPFO/BPFI frequency amplitude    → FTRB inner/outer race fault (mode 5)
1× rotational vibration          → Roll eccentricity (mode 6)
2×/3× rotational vibration       → Spindle coupling wear
100–250 Hz FFT peak amplitude    → 3rd-octave chatter onset (mode 7)
Load cell DS/OS asymmetry (MN)   → Misalignment; chock clearance; BUR shoulder drop (modes 9,10)
Load cell absolute spike          → Cobble/fracture risk (mode 3)
Gradual load cell increase        → Roll wear; bearing drag (modes 1,5)
HGC position deviation (µm)      → Hydraulic seal fault; LVDT drift (mode 10)
Motor torque asymmetry (DS vs OS) → Spindle wear; coupling misalignment
Strip thickness deviation profile → Crown profile drift; eccentricity (mode 6)
Roll wear rate (mm/1000t)        → Material selection fit; lubrication adequacy
BUR surface hardness HSD         → Work-hardening / spall initiation risk (mode 2)
Post-grind UT echo depth (mm)    → Subsurface fatigue crack depth (modes 2,8)
Campaign length vs. history      → Early subsurface damage flag (shortened = anomaly)
```

### 9.1 Suggested PdM Model Targets

| Target | Recommended Approach | Key Features |
|---|---|---|
| FTRB remaining useful life | Gradient boosted regression (XGBoost / LightGBM) on vibration FFT bands + temperature trend slope | BPFO amplitude, temp delta, campaign hours |
| Chatter onset alert | Time-series anomaly detection (isolation forest / LSTM-AE) on chock accelerometer 100–250 Hz band energy | Rolling 60-s windowed band energy ratio |
| Spalling risk score (BUR) | Bayesian survival model (Weibull accelerated failure time); inputs: cumulative tonnage, hardness delta HSD, regrind depth | Time-to-event framing |
| Roll fracture prevention | Hard rule (load cell spike > 150% setpoint for > 50 ms → immediate mill stop); supervised classifier for pre-cobble load cell patterns | Rule + ML hybrid |
| Roll change optimization (campaign extension) | Contextual bandit / Bayesian optimization over WR change interval; reward = (strip surface quality − cobble risk) | Per-stand, per-grade model |

### 9.2 Digital Twin Integration Point

A physics-informed thermal fatigue model (cyclic temperature gradient from pyrometer + cooling water flow → crack growth rate using Paris law calibrated to roll material) can generate synthetic training samples for rare spalling / fracture events — compensating for low event counts in real plant data.

---

## 10. KEY REFERENCES

1. [Analysis of Back-up Roll Spalling Causes — LMM GROUP](https://lmmrolls.com/analysis-of-the-causes-of-spalling-of-hot-continuous-rolling-back-up-rolls/) — verified spalling mechanism + HSD thresholds
2. [Backup Roll Fracture — PMC / MDPI Materials](https://pmc.ncbi.nlm.nih.gov/articles/PMC9147539/) — peer-reviewed work hardening + fracture mechanism
3. [NDT of Mill Rolls — APCNDT 2013 — ndt.net](https://www.ndt.net/article/apcndt2013/papers/066.pdf) — UT + eddy-current methods, 55% spalling reduction claim
4. [Bearings for Rolling Mill Rolls — IspatGuru](https://www.ispatguru.com/bearings-for-rolling-mill-rolls/) — bearing type overview, oil-film bearing specs
5. [Roll Abnormalities and Failures — IspatGuru](https://www.ispatguru.com/abnormalities-and-failures-of-rolling-mill-rolls/) — failure taxonomy, thermal breakage stress values
6. [Hot Strip Mill Maintenance Stands & Rolls — Oxmaint](https://oxmaint.com/industries/steel-plant/hot-strip-mill-maintenance-stands-rolls) — campaign lengths, bearing lead time statistics, cost figures
7. [Rolling Mill Vibration Predictive Monitoring — Oxmaint](https://oxmaint.com/blog/post/rolling-mill-vibration-predictive) — vibration cost + failure statistics
8. [Work Roll Material Selection — HANI Mill Rolls](https://hanmillrolls.com/critical-selection-guide-for-work-roll-materials-in-rolling-operations/) — hardness by stand position, wear rates
9. [Thermal Fatigue in Work Rolls — PMC / MDPI](https://pmc.ncbi.nlm.nih.gov/articles/PMC7665132/) — cyclic temperature + crack growth rate
10. [Mill Chatter Component Extraction — Wiley Shock and Vibration 2024](https://onlinelibrary.wiley.com/doi/10.1155/vib/1109551) — 3rd-octave frequency range verification
11. [Motor Bearing Temp & Vibration Thresholds — PLCDCSPRO](https://www.plcdcspro.com/blogs/news/motor-bearing-temperature-monitoring-and-vibration-protection-settings) — 85°C alarm / 105°C trip / 8 mils trip values
12. [Cobble Detection — Oxmaint](https://oxmaint.com/industries/steel-plant/cobble-detection-prevention-rolling-mills-guide) — 12× cobble risk multiplier from spalling
13. [FAG Rolling Bearings for Rolling Mill Applications — Schaeffler](https://www.schaeffler.com/remotemedien/media/_shared_media/08_media_library/01_publications/schaeffler_2/publication/downloads_18/wl_17200_4_de_en.pdf) — FTRB design details
14. [SAIL Tenders Roll Shop — SAIL](https://sailtenders.co.in/STDocs/SAIL_Shop/Roll%20Shops.pdf) — BUR dimensions and weight specs (46 t and 170 t examples)
15. [Work Roll Breakage Causes — LMM Work Rolls](https://lmmworkrolls.com/en/analysis-on-the-causes-of-breakage-of-work-rolls-in-plate-and-strip-mills/) — residual stress values, preheating parameters
