# Real-World Predictive Maintenance / Condition-Monitoring Datasets
**Research Date:** 2026-06-08  
**Purpose:** Grounding synthetic + curated dataset design for Tata Steel R2 in what real PdM data actually looks like

---

## Quick Reference Comparison Table

| Dataset | Equipment | Primary Sensors | Schema Width | Label Type | Size | Failure Rarity |
|---|---|---|---|---|---|---|
| **NASA C-MAPSS** | Turbofan engine | 21 process sensors (temp, pressure, speed) + 3 op settings | 26 cols/row | RUL (regression, cycles) | 4 subsets; 100–248 engines each | N/A — continuous degradation |
| **NASA IMS Bearing** | Rolling element bearings | 4 × accel (8 ch in set1, 4 ch in sets 2&3) | 8 or 4 cols | Binary anomaly + failure event | 3 run-to-failure tests; ~1-sec snapshots every 10 min | ~3 failure events total |
| **AI4I 2020** | CNC milling machine | Air temp, process temp, speed, torque, tool wear | 14 cols | Multi-label failure mode (5 modes + binary) | 10,000 rows | 3.4% overall failure rate |
| **PHM 2010 Milling** | CNC milling cutter | 3-axis dynamometer (Fx/Fy/Fz) + 3-axis accel + 1 AE | 7 sensor ch + metadata | Tool wear (µm, regression) | 6 cutters; ~315 cuts each; 9000 pts/cut | Continuous wear progression |
| **CWRU Bearing** | Induction motor bearings | DE accel + FE accel + BA accel + RPM | 4 cols + metadata | Fault class (normal / IR / ball / OR), severity | ~161 .mat files; ~120–240k pts each | Artificially balanced; ~75% fault |
| **FEMTO/PRONOSTIA** | Small rolling element bearings | 2 × accel (H + V axis) + temperature | 3 ch (2 used) | RUL (regression, seconds) | 17 run-to-failure bearings across 3 op conditions | All end in failure; duration 1–7h |
| **Paderborn (KAt)** | Motor bearings | Vibration + 2 × motor current + speed/torque/temp | ~5 cols synchronous | Fault class (healthy / IR / OR / roller) | 32 bearing states; 6 healthy + 26 damaged; 20 × 4s each | Balanced by design; real + artificial damage |
| **MetroPT** | Metro air compressor (APU) | 8 analog (pressure, temp, current, flow) + 8 digital + GPS | 20 cols | Binary anomaly + 3 named failure events | ~11M rows (Jan–Jun 2022); 1 Hz | ~3 failures across 11M points (~0.003%) |
| **Bosch Prod. Line** | Assembly line parts | 4264 anonymized numeric/categorical/date features | 4264 cols | Binary: pass/fail | 1.18M train + 1.18M test parts | 0.58% failure (extremely rare) |
| **MIMII** | Valves, pumps, fans, slide rails | 8-ch microphone array | 8 audio channels | Binary anomaly (normal/abnormal) | 4 machine types × 7 models; ~5000s normal, ~1000s anomalous | ~17% anomalous (designed) |
| **Paderborn TCM / PHM 2008 Milling** | CNC milling cutters (steel/alloy) | Dynamometer (Fx/Fy/Fz), accelerometers (3-axis), AE | 7–10 sensor channels | Tool wear depth (µm, regression) or categorical stage | 6 cutters; ~300 .dat files each | Continuous: wear 0→150µm until end-of-life |
| **NEU Surface Defect DB** | Hot-rolled steel sheet surface | Camera (grayscale image) | 200×200 px images | 6-class defect classification | 1800 images (300 per class) | Balanced (100% defective by construction) |
| **Severstal Steel Defect** | Cold-rolled steel coil surface | High-res camera (color) | 1600×256 px images | 4-class segmentation mask | 12,568 train images; 4 defect classes | ~60% images have ≥1 defect |

---

## 1. NASA C-MAPSS (Commercial Modular Aero-Propulsion System Simulation)

**Equipment:** Simulated turbofan aircraft engine  
**Source:** NASA Prognostics Center of Excellence — https://data.nasa.gov/dataset/c-mapss-aircraft-engine-simulator-data  

### Schema (26 columns per row)

| Col | Name | Description | Units |
|-----|------|-------------|-------|
| 1 | unit_number | Engine ID | integer |
| 2 | time_in_cycles | Operational cycle count | cycles |
| 3–5 | op_setting_1/2/3 | Flight altitude, Mach number, throttle resolver angle | varies |
| 6 | s1 (T2) | Total temperature at fan inlet | °R |
| 7 | s2 (T24) | Total temperature at LPC outlet | °R |
| 8 | s3 (T30) | Total temperature at HPC outlet | °R |
| 9 | s4 (T50) | Total temperature at LPT outlet | °R |
| 10 | s5 (P2) | Fan inlet pressure | psia |
| 11 | s6 (P15) | Bypass-duct pressure | psia |
| 12 | s7 (P30) | HPC outlet pressure | psia |
| 13 | s8 (Nf) | Fan physical rotational speed | rpm |
| 14 | s9 (Nc) | Core physical rotational speed | rpm |
| 15 | s10 (epr) | Engine pressure ratio | dimensionless |
| 16–26 | s11–s21 | Additional bleed, temperature, vibration, bypass ratio sensors | varies |

**Note:** Sensors s1, s5, s16, s18–s19 show near-zero variance in FD001 and are commonly dropped during preprocessing. Researchers typically use ~14 of the 21 sensors.

### Sub-datasets

| Subset | Train engines | Test engines | Fault modes | Op conditions |
|--------|---------------|--------------|-------------|---------------|
| FD001 | 100 | 100 | 1 | 1 |
| FD002 | 260 | 259 | 1 | 6 |
| FD003 | 100 | 100 | 2 | 1 |
| FD004 | 248 | 249 | 2 | 6 |

**Label type:** RUL regression (integer cycles-to-failure); test set provides only the last cycle + separate RUL_FDxxx.txt ground truth.  
**Class balance:** N/A — all engines run to failure; early cycles are healthy, late cycles are degraded.  
**Benchmark metric:** RMSE + NASA Scoring Function (asymmetric: late predictions penalized more than early). Recent SOTA: RMSE ~10–15 on FD001 (transformer/LSTM hybrids 2024–2025).

### What's Realistic to Imitate
- **Variable-length time series per unit** — not a fixed-width feature table; each engine has a different number of cycles
- **No explicit failure label** — researchers impose a "piecewise linear" RUL cap (commonly at 125 cycles) as a preprocessing choice
- **Operating condition stratification matters** — FD002/FD004 require normalization across 6 op clusters
- **~14 useful out of 21 sensor channels** — sensor selection is itself a research step; many columns are flat

---

## 2. NASA IMS Bearing Dataset

**Equipment:** Rolling element bearings on a rotating shaft, 2000 RPM, 6000 lbs radial load  
**Source:** NASA Open Data Portal — https://data.nasa.gov/dataset/ims-bearings  
**Collector:** University of Cincinnati IMS (Intelligent Maintenance Systems) Lab, 2003  

### Schema

| Set | Columns (channels) | Sampling Rate | Snapshot length | Interval |
|----|---------------------|---------------|----------------|----------|
| 1 | 8 cols: B1_X, B1_Y, B2_X, B2_Y, B3_X, B3_Y, B4_X, B4_Y | 20,480 Hz | 1 second = 20,480 pts | Every 10 min |
| 2 | 4 cols: B1_X, B2_X, B3_X, B4_X | 20,480 Hz | 1 second = 20,480 pts | Every 10 min |
| 3 | 4 cols: B1_X, B2_X, B3_X, B4_X | 20,480 Hz | 1 second = 20,480 pts | Every 10 min |

**Sensors:** PCB 353B33 High Sensitivity Quartz ICP accelerometers (piezoelectric)  
**Units:** g (gravitational acceleration)  
**File format:** Space-separated ASCII; each file = one 1-second snapshot; filename encodes timestamp  

### Failure Modes (ground truth)
| Set | Duration | Failure bearing | Failure mode |
|-----|----------|-----------------|--------------|
| 1 | Oct 22 – Nov 25 2003 (~35 days) | Bearing 3 (inner race) + Bearing 4 (roller element) | Inner race + roller element |
| 2 | Feb 12 – Feb 19 2004 (~7 days) | Bearing 1 | Outer race failure |
| 3 | Mar 4 – Apr 4 2004 (~31 days) | Bearing 3 | Outer race failure |

**Label type:** No per-snapshot labels; researchers assign health stage (healthy / degrading / failed) via threshold on RMS/kurtosis or manual annotation. Binary anomaly detection is the dominant framing.  
**Size:** Set 1 ≈ 43 GB of raw files; Sets 2&3 are smaller.

### What's Realistic to Imitate
- **Raw waveform structure**: every snapshot is a 20k-point raw vibration trace, not pre-extracted features
- **Run-to-failure with ambiguous label onset**: failure is gradual; researchers disagree on where "failure starts"
- **Multi-bearing monitoring**: 4 bearings simultaneously on same shaft — only some fail
- **No synchronized process data**: purely vibration, no speed variation, no torque

---

## 3. AI4I 2020 Predictive Maintenance Dataset

**Equipment:** Synthetic CNC milling machine (designed to mirror industrial reality)  
**Source:** UCI ML Repository — https://archive.ics.uci.edu/dataset/601/ai4i+2020+predictive+maintenance+dataset  

### Full Column Schema

| Column | Type | Units | Description |
|--------|------|-------|-------------|
| UID | ID (integer) | — | Row ID 1–10,000 |
| Product ID | Categorical | — | L/M/H quality tier + serial number |
| Type | Categorical (L/M/H) | — | Machine product type |
| Air temperature | Continuous | K | Normalized ~300 K, σ=2 |
| Process temperature | Continuous | K | Air temp + 10 K offset, σ=1 |
| Rotational speed | Integer | rpm | Drawn from ~2860 W power |
| Torque | Continuous | Nm | Normal dist ~40 Nm, σ=10 |
| Tool wear | Integer | min | Cumulative; L +2 min, M +3 min, H +5 min per cycle |
| Machine failure | Binary | — | Overall failure flag (OR of 5 modes) |
| TWF | Binary | — | Tool wear failure (wear > 200–240 min) |
| HDF | Binary | — | Heat dissipation failure (temp diff <8.6 K + speed <1380 rpm) |
| PWF | Binary | — | Power failure (torque×speed outside 3500–9000 W range) |
| OSF | Binary | — | Overstrain failure (torque×wear > type-specific threshold) |
| RNF | Binary | — | Random failure (0.1% chance regardless) |

**Size:** 10,000 rows, 14 columns, zero missing values  
**Class balance:**
- Overall machine failure: 339/10,000 = **3.4%**
- TWF: 46 events; HDF: 115; PWF: 95; OSF: 98; RNF: 19
- Events can overlap (multiple failure modes per incident)

**Benchmark results:** LightGBM achieves AUC-ROC ~0.973 with SMOTE; Random Forest baseline macro-F1 = 0.882  

### What's Realistic to Imitate
- **Multi-mode failure** — one overall label + per-mode sublabels (very realistic industrial structure)
- **Physics-grounded failure rules** — failures are deterministic functions of sensor combos (HDF = temp×speed interaction), making the dataset partially interpretable
- **Lightweight sensor set** — only 5 process parameters, yet captures rich failure taxonomy
- **Severe class imbalance** (3.4%) forces SMOTE/cost-sensitive approaches
- **Tabular, fixed-width, no time index** — each row is an independent operational snapshot

---

## 4. PHM Society 2010 Milling Challenge Dataset (also covers 2008 variant)

**Equipment:** High-speed CNC milling machine (carbide end mill cutters)  
**Source:** PHM Society Data Repository — https://data.phmsociety.org/  
**Also available:** IEEE DataPort (2010 challenge) — https://ieee-dataport.org/documents/2010-phm-society-conference-data-challenge  

### Schema (per data acquisition file — one file = one cut)

| Channel | Sensor type | Axis/position | Units |
|---------|------------|---------------|-------|
| force_x | Kistler 9257B dynamometer | X-axis cutting force | N |
| force_y | Kistler 9257B dynamometer | Y-axis cutting force | N |
| force_z | Kistler 9257B dynamometer | Z-axis cutting force | N |
| vibration_x | Kistler 8762A accelerometer | X-axis, workpiece-mounted | m/s² |
| vibration_y | Kistler 8762A accelerometer | Y-axis, workpiece-mounted | m/s² |
| vibration_z | Kistler 8762A accelerometer | Z-axis, workpiece-mounted | m/s² |
| acoustic_emission | AE sensor | Workpiece surface | V (raw AE) |

**Additional metadata per cut:** cut number, depth of cut, feed rate, spindle speed  
**Sampling rate:** ~50 kHz (forces and AE); 9000 points captured per cut  
**Ground truth:** Optical microscope measurement of flank wear (VB) in µm after each cut; separate `wear_C*.csv` files  

### Dataset Structure
| Cutter | Labeled (wear given) | Cuts |
|--------|---------------------|------|
| C1 | Yes | ~315 |
| C4 | Yes | ~315 |
| C6 | Yes | ~315 |
| C2, C3, C5 | No (test set) | ~315 each |

**Label type:** Tool wear regression (VB in µm) or 3-stage classification (good/degraded/worn, threshold typically at 50µm and 100µm). Failure = VB > 150µm  
**Class balance:** Continuous spectrum; roughly 40% "good", 40% "degraded", 20% "worn" when converted to stages  

### What's Realistic to Imitate
- **Multi-channel synchronized time-series within each cut**: 7 channels simultaneously
- **Progressive, irreversible wear**: wear only increases; no "recovery"
- **Cut-to-cut (not sample-to-sample) label granularity**: one wear value per ~9000-point file
- **Operating condition metadata** attached to each file (depth, feed, speed)
- **Steel and Ti alloy machining** — directly relevant to steel production monitoring

---

## 5. CWRU Bearing Dataset (Case Western Reserve University)

**Equipment:** 2 HP induction motor drivetrain; test bearings at drive end and fan end  
**Source:** CWRU Bearing Data Center (now mirrored widely) — https://engineering.case.edu/bearingdatacenter  

### Schema

| Channel | Position | Sampling Rate | Description |
|---------|----------|---------------|-------------|
| DE_time | Drive-end bearing housing, 12 o'clock | 12 kHz or 48 kHz | Primary vibration signal |
| FE_time | Fan-end bearing housing, 12 o'clock | 12 kHz | Secondary vibration |
| BA_time | Motor base plate | 12 kHz | Background/structural vibration |
| RPM | — | Metadata | Motor rotational speed |

**Format:** .mat (MATLAB) files; each file ≈ 120,000–240,000 time-domain samples  

### Fault Classes and Severities

| Fault location | Fault diameter (severity) | Classes |
|----------------|--------------------------|---------|
| Normal baseline | None | 1 class |
| Inner race (IR) | 0.007", 0.014", 0.021", 0.028" | 4 severity levels |
| Ball/roller (RE) | 0.007", 0.014", 0.021", 0.028" | 4 severity levels |
| Outer race (OR) | 0.007", 0.014", 0.021", (various load zones) | 4 severity levels × 3 positions |

**Operating conditions:** 0, 1, 2, 3 HP load → 1797, 1772, 1750, 1720 RPM  
**Total files:** ~161 .mat files  
**Class balance (after preprocessing):** Researcher-controlled; most published work creates balanced 4-class (N/IR/RE/OR) or 10-class (by fault diameter) datasets  

**Benchmark metric:** Classification accuracy. Recent SOTA: >99% accuracy (4-class, balanced), but noted [data leakage issues](https://arxiv.org/abs/2407.14625) in much reported literature from train-test contamination.  

### What's Realistic to Imitate
- **Controlled severity levels** — same fault type at multiple severities (0.007" → 0.028") mirrors real-world "incipient → severe" progression
- **Multiple sensor positions** — DE is most informative; BA is noise-like; real systems deploy multiple sensors
- **Artificially seeded faults** — EDM-induced faults, not naturally evolved; creates very distinct spectral patterns that may be overly clean
- **Motor RPM varies slightly by load** — realistic coupling of speed and load
- **No temporal context per unit** — each .mat file is a stationary snapshot, not a run-to-failure trajectory

---

## 6. FEMTO / PRONOSTIA Bearing Dataset (IEEE PHM 2012 Challenge)

**Equipment:** Small ball bearings on PRONOSTIA accelerated-aging test rig (FEMTO-ST Institute, Besançon)  
**Source:** PHM Society Data Repository (via IEEE 2012 Challenge) — also mirrored at https://github.com/tilman151/rul_datasets  

### Schema

| Channel | Sensor | Axis | Sampling Rate | Points per snapshot |
|---------|--------|------|---------------|---------------------|
| acc_horiz | Miniature accelerometer | Horizontal (perpendicular to gravity) | 25,600 Hz | 2560 (= 0.1 s) |
| acc_vert | Miniature accelerometer | Vertical (parallel to gravity) | 25,600 Hz | 2560 (= 0.1 s) |
| temperature | Thermocouple | Bearing housing | 10 Hz | 1 per snapshot |

**Snapshot interval:** Every 10 seconds  
**File format:** CSV; filename encodes bearing ID, condition, and timestamp  

### Operating Conditions and Bearings

| Condition | Radial load | Speed | Bearings (total 17) | Notes |
|-----------|------------|-------|---------------------|-------|
| 1 | 4000 N | 1800 rpm | 7 bearings (B1_1 to B1_7) | 2 train + 5 test |
| 2 | 4200 N | 1650 rpm | 7 bearings (B2_1 to B2_7) | 2 train + 5 test |
| 3 | 5000 N | 1500 rpm | 3 bearings (B3_1 to B3_3) | 0 train + 3 test (blind) |

**Experiment duration:** 1 to 7 hours per bearing; failure criterion = vibration amplitude exceeds 20 g  
**Failure types:** Natural (not seeded) — multiple defect types possible; types not labeled  
**Label type:** RUL regression (seconds to failure); failure defined by threshold crossing  
**Test set challenge:** Only a truncated early portion provided; participants must predict RUL at truncation point  

**Benchmark metric:** PHM 2012 scoring function (relative error penalizing late predictions). Modern RMSE on condition 1: typically 200–800 seconds depending on truncation point.  

### What's Realistic to Imitate
- **Short, frequent snapshots** — 0.1-second windows every 10 seconds is the real industrial compromise between data rate and storage
- **3 operating conditions with different degradation timescales**: same fault physics, different speeds → need cross-condition generalization
- **Healthy-to-failed continuum with no label onset**: health degradation is unlabeled; researchers derive health indicators from raw features (RMS, kurtosis, entropy)
- **Temperature channel often missing** in test sets — realistic data-availability inconsistency

---

## 7. Paderborn University Bearing Dataset (KAt DataCenter)

**Equipment:** Purpose-built bearing test rig at University of Paderborn, Germany  
**Source:** KAt DataCenter — https://mb.uni-paderborn.de/kat/forschung/bearing-datacenter/data-sets-and-download  

### Schema (per .mat file)

| Channel | Signal | Sampling Rate | Description |
|---------|--------|---------------|-------------|
| vibration | Piezoelectric accelerometer | 64,000 Hz | Housing vibration (primary) |
| motor_current_1 | Current clamp, Phase 1 | 64,000 Hz | Motor phase current |
| motor_current_2 | Current clamp, Phase 2 | 64,000 Hz | Motor phase current |
| speed | Encoder | 64,000 Hz | Shaft rotational speed |
| torque | Torque sensor | 64,000 Hz | Shaft torque |
| radial_force | Load cell | 64,000 Hz | Applied radial bearing force |
| temperature | Thermocouple | 1 Hz (slow) | Bearing housing temp |

**File naming convention:** `N15_M07_F10_KA01_1.mat` (speed / torque / load / bearing-code / repetition)  
**Recording duration:** 4 seconds per file; 20 files per operating condition per bearing  

### Bearing States and Classes

| Class | Count | Notes |
|-------|-------|-------|
| Healthy (undamaged) | 6 bearing codes | Reference condition |
| Damaged — artificial | 12 bearing codes | EDM-seeded inner/outer race faults |
| Damaged — real (fatigue) | 14 bearing codes | Accelerated aging, true degradation |
| **Total** | **32 states** | |

**Fault locations:** Inner race (IR), outer race (OR), roller elements  
**Operating conditions:** 4 combinations of {shaft speed × load torque}: (300rpm, 0.1Nm), (400rpm, 0.7Nm), (1000rpm, 0.7Nm), (1500rpm, 0.1Nm) [unverified exact values — check KAt docs]

**Label type:** Multi-class fault classification (healthy / IR-artificial / OR-artificial / IR-real / OR-real)  
**Class balance:** Researcher-controlled depending on subset chosen; artificial vs. real damage split allows transfer learning studies  

### What's Realistic to Imitate
- **Multi-modal sensor fusion**: vibration + motor current is the realistic industrial setup (current is cheap; accelerometer is add-on)
- **4 operating conditions** — real machines run at variable speeds and loads, not fixed 1750 rpm
- **Real vs. artificial damage** — artificial damage shows cleaner spectral signatures than naturally degraded bearings (important calibration note)
- **High sampling rate at 64 kHz** — very high temporal resolution; real plants often use much lower (1–8 kHz)

---

## 8. MetroPT Dataset (Metro Compressor Predictive Maintenance)

**Equipment:** Air Production Unit (APU) compressor on Porto metro trains  
**Source:** UCI ML Repository (MetroPT-3) — https://archive.ics.uci.edu/dataset/791/metropt+3+dataset  
**Paper:** Scientific Data, Nature, 2022 — https://pmc.ncbi.nlm.nih.gov/articles/PMC9747912/  

### Full Sensor Schema (20 variables)

**Analog sensors (8):**

| Signal | Units | Description |
|--------|-------|-------------|
| TP2 | bar | Compressor discharge pressure |
| TP3 | bar | Pneumatic panel pressure |
| H1 | bar | Pilot valve activation pressure (~10.2 bar threshold) |
| DV_pressure | bar | Air dryer discharge valve pressure drop |
| Reservoirs | bar | Air tank pressure |
| Oil_Temperature | °C | Compressor oil temperature |
| Flowmeter | m³/h | Air flow at pneumatic panel |
| Motor_Current | A | Motor current (0=off, ~4A unloaded, ~7A loaded) |

**Digital signals (8 binary flags):** COMP (compressor on/off), DV_electric, TOWERS (regeneration tower status), MPG, LPS (low pressure switch), Pressure_switch, Oil_Level, Caudal_impulses  

**GPS (4):** gpsLong, gpsLat, gpsSpeed (km/h), gpsQuality  

**Sampling rate:** 1 Hz  
**Collection period:** January–June 2022  
**Total rows:** ~10,979,547 (no missing values)  
**Transmission:** GSM telemetry every 5 minutes (burst mode); effectively continuous at 1 Hz  

### Failure Events (Ground Truth)

| Failure # | Type | Component | Duration | Affected records (~) |
|-----------|------|-----------|----------|---------------------|
| 1 | Air leak | Client side | ~4.1 hours | ~14,820 |
| 2 | Air leak | Air dryer | ~30 minutes | ~1,800 |
| 3 | Oil leak | Compressor body | ~3.3 days | ~281,800 |

**Class balance:** 3 failures across ~11M records → **~2.7% anomalous** (heavily imbalanced)  
**Benchmark metric:** F1 / Precision-Recall AUC for anomaly detection; early prediction window (hours before event)  

### What's Realistic to Imitate
- **Mixed analog + digital signals** — real industrial IoT always mixes continuous sensors with discrete on/off status flags
- **GPS contextual data** — train position/speed as operational context; analogous to heat stage or rolling pass in steel
- **1 Hz slow-sampled process data** — distinct from high-frequency vibration; complementary modality
- **Extremely rare failures** (~0.003% each) — real industrial uptime is 99.99%; failure datasets are inherently imbalanced
- **Named failure modes with different durations**: short acute failures vs. long slow-developing failures are both present

---

## 9. Bosch Production Line Performance Dataset

**Equipment:** High-volume manufacturing assembly line (automotive components)  
**Source:** Kaggle 2016 competition — https://www.kaggle.com/competitions/bosch-production-line-performance  
**Paper:** IEEE ICDM 2016 — https://ieeexplore.ieee.org/document/7840826  

### Schema Overview

**4264 total features** across 3 feature blocks:
- **Numeric features** (~900 cols): anonymized sensor/measurement readings at 51 workstations (L0–L3 production lines); names follow pattern `L{line}_{station}_{measurement}`
- **Categorical features** (~50 cols): discrete codes (material batch, configuration, routing)
- **Date/timestamp features** (~1200 cols): when each part passed each station (enables temporal sequence reconstruction)

**Target:** `Response` — binary (0 = passed QC, 1 = failed QC)  

**Size:**
- Train: 1,183,747 rows  
- Test: 1,183,748 rows  
- Sparse: ~95% of feature values are NaN per row (each part only visits a subset of stations)

**Class balance:**
- Failures: 6,879 / 1,183,747 = **0.58% failure rate**
- Severe imbalance; requires SMOTE / cost-sensitive / anomaly detection approaches

**Benchmark metric:** Matthews Correlation Coefficient (MCC); winning solution MCC ≈ 0.37 (the baseline is essentially near 0 given extreme imbalance)  

### What's Realistic to Imitate
- **Massive feature sparsity** — real production lines: each part visits only a fraction of stations → most measurements are missing by design, not by error
- **Routing/sequence matters** — same feature from a different station order changes meaning
- **Extreme class imbalance** (0.58%) — industrial quality escapes are genuinely rare
- **Anonymized features** — real Bosch data is proprietary; column names are obfuscated. Mirror this for realism if synthetic data involves IP concerns
- **Timestamp features as implicit process route** — date at each step encodes production flow, a powerful feature

---

## 10. MIMII Dataset (Malfunctioning Industrial Machine Investigation and Inspection)

**Equipment:** Valves, pumps, fans, slide rails (4 machine types × 7 product models = 28 models)  
**Source:** Zenodo — https://zenodo.org/records/3384388  
**Paper:** DCASE Workshop 2019 — https://arxiv.org/abs/1909.09347  

### Schema

| Attribute | Specification |
|-----------|---------------|
| Sensor | 8-channel circular microphone array |
| Sampling rate | 16,000 Hz |
| Bit depth | 16-bit PCM |
| Clip length | 10 seconds per recording |
| Format | .wav files |
| Channels | 8 (stereo-mixed to mono for most baselines) |

**Dataset composition per machine model:**
- Normal sounds: ~5,000–10,000 seconds total
- Anomalous sounds: ~1,000 seconds total
- SNR variants: -6 dB, 0 dB, +6 dB (factory noise mixed in at 3 levels)

**Anomaly types by machine:**

| Machine | Anomaly conditions |
|---------|--------------------|
| Valve | Contamination, blockage |
| Pump | Contamination, leakage, rotating unbalance, rail damage |
| Fan | Unbalance, voltage change, clogging |
| Slide rail | Rail damage, no grease, block |

**Label type:** Binary (normal / abnormal); no sub-class labels  
**Class balance:** ~17% anomalous by design (training: normal only; test: mixed)  
**Task framing:** Unsupervised anomaly detection — models trained on normal sounds only; no labeled anomalies at train time  

**Benchmark metric:** AUC-ROC per machine/model. Baseline (auto-encoder on log-Mel spectrogram): 0.60–0.88 AUC depending on machine type.  

### What's Realistic to Imitate
- **Model-to-model variation within same class**: 7 variants of "pump" — each has slightly different sound signature. Analogous to equipment-to-equipment variation in a steel plant
- **Semi-supervised framing** — only normal data available at training time; mirrors real deployment where labeled failures are rare
- **SNR as difficulty dial** — real factory noise varies; embedding noise level as a design parameter is realistic
- **8-channel spatial audio** — microphone arrays capture directional information; multi-sensor spatial context

---

## 11. NEU Surface Defect Database (Steel-Specific)

**Equipment:** Hot-rolled steel strip production line  
**Source:** Northeastern University (NEU), Shenyang, China — http://faculty.neu.edu.cn/yunhyan/NEU_surface_defect_database.html  

### Schema

| Attribute | Value |
|-----------|-------|
| Sensor | Industrial grayscale camera |
| Image size | 200 × 200 pixels |
| Image format | BMP/JPEG |
| Channels | 1 (grayscale) |
| Samples per class | 300 |
| Total images | 1,800 |

**Defect classes (6):**

| Class | Code | Description |
|-------|------|-------------|
| Crazing | Cr | Network of fine surface cracks |
| Inclusion | In | Embedded foreign material |
| Patches | Pa | Non-uniform surface patches |
| Pitted surface | PS | Pit/crater defects |
| Rolled-in scale | RS | Scale pressed into surface |
| Scratches | Sc | Linear surface scratches |

**Class balance:** Perfectly balanced (300 per class); 100% defective images — no "normal" class included  
**Task:** 6-class image classification + object detection (bounding box annotations available in some versions)  
**Benchmark metric:** Classification accuracy. ResNet-based models achieve 95–99% on standard splits.  

### What's Realistic to Imitate
- **Steel-specific defect taxonomy** — the 6 classes directly correspond to steel rolling/casting failure modes
- **Intra-class variability** — crazing vs. scratches can be subtle; dataset challenges easy over-fitting
- **No "normal" class** — real inspection systems need a 7th "clean" class added for deployment; a practical gap

---

## 12. Severstal Steel Defect Dataset

**Equipment:** Cold-rolled steel coil production line (real Severstal plant data)  
**Source:** Kaggle 2019 competition — https://www.kaggle.com/c/severstal-steel-defect-detection  

### Schema

| Attribute | Value |
|-----------|-------|
| Sensor | High-speed line-scan camera |
| Image size | 1600 × 256 pixels |
| Color | Grayscale |
| Format | PNG |
| Total train images | 12,568 |
| Annotation | Run-length encoded (RLE) segmentation masks |

**Defect classes (4):**

| Class ID | Description |
|----------|-------------|
| 1 | Edge cracks (linear, surface) |
| 2 | Inclusions |
| 3 | Surface scratches / pitting |
| 4 | Rolled-in scale |

**Class balance:**  
~60% of images contain at least one defect; defect distribution is uneven (Class 3 most frequent, Class 2 rarest)  
**Task:** Instance segmentation (pixel-level masks)  
**Benchmark metric:** Dice coefficient per class. Winning solution: mean Dice ~0.90.  

### What's Realistic to Imitate
- **Real production data** — not synthetic or lab-controlled; lighting variation and noise present
- **RLE-encoded masks** — industry-standard annotation format for surface inspection
- **Wide aspect ratio** — 1600×256 reflects strip geometry; defects are often elongated along rolling direction
- **Multi-defect co-occurrence** — a single strip section can have multiple defect types simultaneously

---

## 13. PHM Society Challenge Datasets (Multi-Year Reference)

**Source:** https://data.phmsociety.org/  

| Year | Equipment | Sensors | Label | Notes |
|------|-----------|---------|-------|-------|
| 2008 | Milling cutters | Dynamometer (3-axis) + accel (3-axis) + AE | Tool wear (µm) | 6 cutters; 9000 pts/cut |
| 2010 | Milling cutters | Same as 2008 + added coolant flow | Tool wear (µm) | Extended version of 2008 |
| 2012 | Ball bearings | 2 × accel + temperature | RUL (seconds) | PRONOSTIA/FEMTO platform |
| 2014 | Industrial valves | Solenoid valve acoustic + pressure | Failure time | Valve stiction + leakage |
| 2016 | Hydraulic system | Pressure (4), flow (2), vibration, temp | 5 component states | Multi-component condition |

---

## Cross-Dataset Structural Patterns: What to Imitate

### 1. Signal Modalities Used in Real PdM

| Modality | Typical range | Industrial use |
|----------|---------------|----------------|
| Vibration (accelerometer) | 12–64 kHz | Rotating machinery; dominant in bearing/gear datasets |
| Process sensors (temp/pressure/flow) | 1 Hz – 100 Hz | Compressors, engines, production lines |
| Motor current | 1–64 kHz | Motor-driven equipment; cheap non-invasive |
| Acoustic emission | 100 kHz – 1 MHz | Crack detection, surface defects |
| Force/torque (dynamometer) | 25–50 kHz | Metal cutting, machining |
| Vision (line-scan cameras) | — | Surface inspection on strip/coil lines |
| Audio (microphone array) | 16 kHz | Unsupervised anomaly detection |

### 2. Universal Dataset Design Patterns

- **Variable-length runs per unit**: equipment has different useful lives; do not pad to uniform length without design intent
- **Multi-sensor fusion**: real systems always deploy 2+ sensor types; single-sensor datasets (CWRU) are simplified
- **Temporal granularity mismatch**: fast vibration (20 kHz) alongside slow process parameters (1 Hz) is the norm — sensors must be aligned or separately modeled
- **Failure rarity is not a bug**: 0.5%–5% failure rates are typical; anything higher is a dataset artifact or a badly maintained plant
- **Health state is rarely labeled**: RUL or binary failure is the label; intermediate health stages (healthy / degrading / failed) are researcher-imposed thresholds
- **Operating condition stratification**: most real datasets have 3–6 distinct operating conditions; cross-condition generalization is a hard problem
- **Metadata matters**: product type, material grade, shift ID, operator ID are real features in production datasets (see AI4I Type column, Bosch routing dates)
- **Sparse features at scale**: large-scale production datasets (Bosch, MetroPT) have many NaN values — each sample doesn't touch every sensor

### 3. Steel-Specific Realistic Patterns
- **Rolling direction anisotropy**: defects on steel strip are elongated in the rolling direction (1600×256 aspect ratio in Severstal)
- **Pass-number as ordinal feature**: steel rolling involves multiple passes; each pass changes material state (analogous to cycle number in C-MAPSS)
- **Surface + process fusion**: NEU/Severstal provide vision; MetroPT/AI4I provide process sensors. Real steel PdM combines both
- **Coil/batch-level identifiers**: failure probability varies by material grade, heat number, and production campaign — batch effects are real
- **Wear progression is monotonic**: tool wear only increases; health only degrades. This physics constraint should be honored in synthetic data

---

## Sources

- [NASA C-MAPSS Aircraft Engine Simulator Data — NASA Open Data Portal](https://data.nasa.gov/dataset/c-mapss-aircraft-engine-simulator-data)
- [NASA IMS Bearings — NASA Open Data Portal](https://data.nasa.gov/dataset/ims-bearings)
- [AI4I 2020 Predictive Maintenance Dataset — UCI ML Repository](https://archive.ics.uci.edu/dataset/601/ai4i+2020+predictive+maintenance+dataset)
- [2010 PHM Society Conference Data Challenge — IEEE DataPort](https://ieee-dataport.org/documents/2010-phm-society-conference-data-challenge)
- [CWRU Bearing Data Center — GitHub mirror](https://github.com/hustcxl/Rotating-machine-fault-data-set)
- [CWRU Benchmarking Issues (data leakage, 2024)](https://arxiv.org/abs/2407.14625)
- [PRONOSTIA Experimental Platform Paper — HAL](https://hal.science/hal-00719503/document)
- [FEMTO/PRONOSTIA Dataset — awesome-industrial-datasets](https://github.com/jonathanwvd/awesome-industrial-datasets/blob/master/markdown/femto_pronostia_bearing_dataset.md)
- [Paderborn KAt DataCenter](https://mb.uni-paderborn.de/kat/forschung/bearing-datacenter/data-sets-and-download)
- [The MetroPT Dataset — Scientific Data / PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC9747912/)
- [MetroPT-3 Dataset — UCI ML Repository](https://archive.ics.uci.edu/dataset/791/metropt+3+dataset)
- [Bosch Production Line Performance — Kaggle](https://www.kaggle.com/competitions/bosch-production-line-performance)
- [Bosch Kaggle Challenge Paper — IEEE ICDM](https://ieeexplore.ieee.org/document/7840826)
- [MIMII Dataset — Zenodo](https://zenodo.org/records/3384388)
- [MIMII Dataset Paper — arXiv](https://arxiv.org/abs/1909.09347)
- [NEU Surface Defect Database](http://faculty.neu.edu.cn/yunhyan/NEU_surface_defect_database.html)
- [Severstal Steel Defect Detection — Kaggle](https://www.kaggle.com/c/severstal-steel-defect-detection)
- [PHM Society Data Repository](https://data.phmsociety.org/)
- [Overview of Publicly Available Degradation Datasets — arXiv 2024](https://arxiv.org/html/2403.13694v2)
- [Multi-Sensor Milling Monitoring Dataset — Zenodo](https://zenodo.org/records/10613521)
- [Paderborn Bearing Dataset Documentation — DPMHM](https://yanncalec.github.io/dpmhm/datasets/paderborn/)
- [IMS Bearing Dataset Analysis — mkalikatzarakis.eu](http://mkalikatzarakis.eu/wp-content/uploads/2018/12/IMS_dset.html)
- [C-MAPSS Awesome Industrial Datasets README](https://github.com/makinarocks/awesome-industrial-machine-datasets/blob/master/data-explanation/C-MAPSS/README.md)

---

*Confidence: High for schema/size/label details of NASA C-MAPSS, AI4I 2020, MetroPT, Bosch, CWRU, MIMII, Severstal (verified from official sources or published papers). Medium for PHM 2010 and FEMTO exact sensor specs (inferred from papers, not raw data files directly). [unverified] for Paderborn exact operating condition parameter values.*
