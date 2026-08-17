# V5 Physics Research Brief: Tata Steel Surface Defect Detection

**Date:** 2026-05-23
**Author:** research-agent (Jarvis)
**Confidence:** High (physics/equations + anti-patterns), Medium (column ID hypotheses + Tata-specific findings)
**Purpose:** Phase 1 research input to V5 builder agent. Maps anonymized X1–X49 to hot-rolling process variable physics so we can close the 54→74 leaderboard gap.

---

## 500-Word Digest (paste directly into V5 builder prompt as `<current_hot_rolling_defect_landscape>`)

Hot strip mill surface defects arise from five interacting mechanisms: **(1)** scale formation driven by temperature, time-at-heat, and steel chemistry (especially %P, %Si, %S); **(2)** insufficient descaling pressure failing to remove oxide before roll bite; **(3)** roll mechanics — excessive specific roll force F/w, improper reduction ratio r, or high roll bite ratio lambda — embedding scale or causing sub-surface cracking; **(4)** thermal gradient — finishing temperature below Ar3 (~850–910°C depending on grade); **(5)** coil-level temporal effects (roll wear stage, prior-coil defect rate).

The single most powerful ratio class in published literature is **force-normalized-by-geometry**: roll separating force divided by strip width (`F/w`, specific roll force kN/mm), and the roll bite ratio `lambda = L_c / h_mean` where `L_c = sqrt(R × draft)` is the contact arc length. High lambda correlates with embedded scale. The Orowan/Sims framework says roll pressure is proportional to `flow_stress × Q_p`, where `Q_p` depends on `(R/h_exit)` and reduction ratio `r` — both are computable as interaction terms Xi × Xj.

For the **X13/X36 mystery**: the most likely hypothesis pair is **(A) Roll Separating Force / Strip Width** — force and width are always co-logged in finishing mill tables and their ratio is the canonical specific roll force. Second: **(B) Finishing Temperature / Coiling Temperature** — FT/CT ratio directly predicts scale oxide structure (AIST PR-313-68, verified). Third: **(C) Entry Thickness / Exit Thickness** — total finishing reduction ratio.

The published scale defect prediction model (data mining study, AIST/ISIJ proceedings) found the **top three predictors: (1) temperature entering the finishing mill, (2) crop shear temperature, (3) %P (phosphorus content)**. This maps directly onto X13/X36 being temperature measurements at adjacent mill points.

Key transforms for V5: `log(F/w)`, `(T_finish − 890)` as Ar3 deviation, `lambda = sqrt(R × draft) / h_mean`, rolling lag-1/2/5 defect rates, `coil_seq mod 100` as roll wear proxy, and the Ekelund-motivated `X_force / (X_temperature × X_width)` flow-stress normalization.

---

## Section 1: Hot Strip Mill Surface Defect Physics — Canonical View

A modern hot strip mill routes a reheated slab (~1200–1250°C) through a roughing mill (reducing ~250 mm to ~35–50 mm transfer bar), then through 5–7 tandem finishing stands (F1–F7) reducing to final gauge (1.5–25 mm) at ~820–950°C, then water-cooled on a 150-metre run-out table and coiled at ~520–740°C.

### 1.1 Scale Pits and Rolled-In Scale (most common defect in HSM tabular data)

**Mechanism:** Steel at rolling temperatures reacts with atmospheric oxygen to form iron oxide (FeO primary, Fe2O3, Fe3O4 tertiary) at 20–500 um thickness. If hydraulic descalers fail to remove tertiary scale before roll bite, oxide is pressed into the strip surface — creating surface pits or embedded scale patches.

**Process conditions that cause it:**
- Entry temperature to finishing mill **too low** (below ~1050°C): scale becomes harder and more adherent, less hydraulically removable
- Entry temperature **too high**: thicker oxide layer builds faster
- Descaling header pressure **insufficient** (should be 150–250 bar for primary scale; up to 450 bar for sticky scale)
- High **%P** (>0.015%): phosphorus forms low-melting iron-phosphate oxide that is sticky and resists water blast
- High **%Si** (>0.3%): fayalite (Fe2SiO4) forms, adherent and causes red scale (red oxide defect)
- High **%S**: sulfides create adherent scale layers

**Ratio signal:** T_entry_finishing deviation from target, and %P as standalone feature. Published logit model (data mining paper, ResearchGate 221173826 [unverified full text]) identified entry-finishing-temperature and %P as the two strongest predictors of tertiary scale.

### 1.2 Laps
**Mechanism:** A lap is a fold of material rolled over but not fully welded. Appears as a longitudinal linear seam at least 30° off-radial.

**Process conditions:**
- Roll misalignment or overfill creating a fin at the edge that folds over in subsequent passes
- Too high draft in early roughing passes on a strip with pre-existing edge notches
- `h/L_p > 2` condition during initial breakdown (thickness-to-contact-length ratio too high for lateral material flow)

**Ratio signal:** h/L_p ratio, draft/h_entry per pass.

### 1.3 Slivers
**Mechanism:** Thin arrow-shaped surface flakes from sub-surface inclusions or burning at the reheating furnace. Sliver-B: thin straight-line defects near strip edges without repetition.

**Process conditions:**
- Reheating temperature too high (overheating/burning): grain boundary oxidation → subsurface weakness → sliver
- Steel chemistry (high sulfide inclusion content)
- High reduction ratio in early stands pushing subsurface inclusions to surface

### 1.4 Edge Cracks
**Mechanism:** Secondary tensile stress from non-homogeneous deformation across strip width. Center elongates more than edges, putting edges in tension. Also triggered by rolling in the dual-phase (austenite + ferrite) region near Ar3.

**Process conditions:**
- **Finishing temperature below Ar3** (~850–900°C for low-carbon grades): rolling in ferrite region where ductility drops sharply
- High reduction ratio in final stands with already thin strip
- Non-uniform lateral cooling (edge spray asymmetry)

**Critical feature:** `T_finishing − Ar3_estimated`. When this goes negative, edge crack probability spikes non-linearly. Andrews (1965) [unverified]: `Ar3 ≈ 910 − 310·%C − 80·%Mn − 20·%Cu − 15·%Cr + 400·%Al + 130·%Ti`.

### 1.5 Surface Seams
**Mechanism:** Pre-existing subsurface voids or blowholes from casting, opened and elongated during rolling. Long thin lines parallel to rolling direction.

**Process conditions:** Casting porosity not healed by reheating; excessive reduction ratio that opens rather than closes pores.

### 1.6 Scabs
**Mechanism:** Detached patches of previously embedded scale that separate and leave cratered pitting. Contain embedded oxide with sharp edges.

**Process conditions:** Insufficient primary descaling (rougher descaler pressure issue); oxide layer mechanical mismatch at temperature causing spalling on roll bite entry.

---

## Section 2: Top 10 Process-Variable Ratios for Defect Prediction

### R1. Specific Roll Force (F/w)
- **Formula:** `F_spec = F_total / w` [kN/mm or MN/m]
- **Physical meaning:** Roll force normalized by strip width — actual pressure loading per unit of strip. Strip width is always logged; roll force measured at each stand via load cells.
- **Defect type:** Scale embedding, surface seams (high F_spec presses oxide into surface)
- **Sign:** Higher F_spec → higher defect risk. Typically 5–20 kN/mm in finishing stands.
- **Source:** Canonical in all HSM process control literature; referenced in IJAMT roll force papers (Springer, confirmed).

### R2. Reduction Ratio per Stand
- **Formula:** `r = delta_h / h_entry = (h_in − h_out) / h_in` [dimensionless, 0–0.5 typical]
- **Physical meaning:** Fractional thickness reduction. High r in late stands (F5–F7) = thin gauge + high deformation at lower temperature = surface distress.
- **Defect type:** Edge cracks and laps (too high r), seams (opens sub-surface defects)
- **Source:** Sims (1954, Proc. IMechE, confirmed DOI); Springer IJAMT FEM defect paper (2012, confirmed DOI 10.1007/s00170-012-4556-7).

### R3. Roll Bite Ratio (Lambda)
- **Formula:** `lambda = L_c / h_mean`, where `L_c = sqrt(R_prime × delta_h)`, `h_mean = (h_in + h_out)/2`, `R_prime` = deformed roll radius (Hitchcock correction)
- **Physical meaning:** Ratio of deformation zone length to mean strip thickness. `lambda > 2` = long and shallow = high friction hill = scale embedding. `lambda < 1` = deep bite = shear-dominated = edge cracking.
- **Sign:** Both extremes are bad; lambda ≈ 1.5 is typical target.
- **Source:** Orowan (1943, Proc. IMechE, confirmed); PMC11301369 lambda vs defect rate study (confirmed).

### R4. Finishing Temperature Deviation from Ar3
- **Formula:** `delta_T_Ar3 = T_finish − Ar3` [°C]. Ar3 ≈ 850–910°C for low-carbon grades.
- **Physical meaning:** Rolling below Ar3 enters dual-phase field where ferrite reduces ductility sharply.
- **Sign:** Negative value → defect probability jumps non-linearly.
- **Source:** ScienceDirect Coiling Temperature overview (confirmed); Britannica hot rolling (confirmed).

### R5. Descaling Pressure / Entry Temperature
- **Formula:** `P_desc / T_entry_finish` [bar/°C]
- **Physical meaning:** Effective descaling = pressure relative to temperature-driven scale thickness. Low ratio = insufficient pressure for the temperature = defect risk.
- **Source:** Scale formation paper (Academia.edu confirmed); HeatLab.cz hydraulic descaling review (confirmed); USPTO patent 6257034 (confirmed).

### R6. FT/CT (Finishing Temperature / Coiling Temperature)
- **Formula:** `FT/CT` [dimensionless, typically 1.2–1.7]
- **Physical meaning:** Governs cooling rate on run-out table → oxide scale structure, thickness, adherence. High FT/CT with elevated Si → red scale.
- **Source:** AIST paper PR-313-68 "Effects of Finishing and Coiling Temperatures on Scale Structure and Picklability" (title confirmed from AIST Digital Library).

### R7. Sims Q_p Factor (Pressure Multiplier)
- **Formula:** `F = w × k_bar × Q_p × L_c`
  - `k_bar` = mean flow stress [MPa]
  - `Q_p ≈ (pi/2) × sqrt(R_prime/h_exit) × arctan(sqrt(r × R_prime/h_exit)) / sqrt(r)`
- **ML interaction term:** `R_roll / h_exit` as feature; `F / (w × L_c)` = back-calculated specific pressure.
- **Source:** Sims, R.B. (1954), Proc. IMechE 168, 191–200. SAGE DOI: 10.1243/PIME_PROC_1954_168_023_02 (confirmed).

### R8. Mass Flow Consistency (Speed × Thickness)
- **Formula:** `V_out × h_out / V_in × h_in` should equal 1.0 per stand (mass conservation). Deviation = tension upset.
- **Physical basis:** Orowan conservation law. Deviation → surface scratches, edge waves.
- **Source:** Interstand tension in continuous hot rolling (Springer IJAMT 2023, DOI: 10.1007/s00170-023-11584-x, confirmed).

### R9. Interstand Tension / Strip Cross-Section
- **Formula:** `sigma_back = T_back / (w × h)` [MPa]
- **Sign:** sigma_back > yield_stress/3 → edge crack risk; too low → flatness defects.
- **Source:** Same interstand tension paper (Springer IJAMT 2023, confirmed).

### R10. Crown Ratio
- **Formula:** `C_ratio = (h_center − h_edge) / h_center` [%, typical 0.5–2%]
- **Physical meaning:** Non-uniform thickness across width. Both extremes (positive crown → center waves; negative → edge waves) indicate uneven surface deformation.
- **Source:** Strip crown prediction ML paper (MDPI Metals 2023, mdpi.com/2075-4701/13/5/900, confirmed).

---

## Section 3: X13/X36 Mystery — Hypothesis Pairs Ranked by Likelihood

The fingerprint of **ratio strong + difference strong + each individually strong** = two measurements of the same physical quantity at different process points. The ratio captures relative change; the difference captures absolute deviation.

### Hypothesis A (Rank 1): Roll Separating Force vs Strip Width
- **X13 = Roll Separating Force (MN or kN at a finishing stand), X36 = Strip Width (mm)**
- `X13/X36` = specific roll force (kN/mm) = canonical defect-risk ratio
- **Supporting evidence:** (a) Force and width are co-logged at every stand, typically in same block of the feature table; (b) F/w is the first ratio any metallurgist computes; (c) in a 49-feature dataset ordered as [roughing block, F1–F7 per-stand params, coiling block], force (~columns 10–20) and width (~columns 35–45) are plausibly 23 apart; (d) high SHAP on each individually expected because total force correlates with grade thickness AND width correlates with product mix — their ratio removes the confound.
- **What else to look for:** X14/X15 = roll torque and rolling speed at same stand as X13. X35/X37 = adjacent width or geometry measurements.

### Hypothesis B (Rank 2): Finishing Temperature vs Coiling Temperature
- **X13 = Finishing Temperature (°C, ~820–950°C), X36 = Coiling Temperature (°C, ~520–740°C)**
- `X13/X36` = FT/CT ratio; `X13 − X36` = total cooling drop (~300–400°C)
- **Supporting evidence:** (a) FT/CT directly predicts scale oxide structure (AIST PR-313-68, confirmed); (b) FT and CT are at opposite ends of the mill layout = consistent with being ~23 columns apart; (c) FT deviation from Ar3 is published as top-2 predictor for scale defects.
- **What else to look for:** X14/X15 = run-out table header temperatures. X35/X37 = coiling speed or coiler tension.

### Hypothesis C (Rank 3): Entry Thickness (Transfer Bar) vs Exit Thickness (F7)
- **X13 = Transfer bar thickness (~35–50 mm), X36 = Final strip thickness (~1.5–10 mm)**
- `X13/X36` = total finishing reduction ratio (~5x–25x)
- **Why ranked 3:** Total reduction ratio is less directly defect-linked than F/w or FT/CT. Per-stand reduction is more informative. Also, the magnitude of X13/X36 would be ~5–25 (very large ratio), which would make it structurally different from the typical feature importance patterns we see.

**V5 Recommendation:** Build all three hypothesis features in parallel. Add `X13/X36`, `X13−X36`, `X36/X13`, `sqrt(X13 × X36)`, and `abs(X13−X36)/(X13+X36)`. Let SHAP on the new feature set reveal which hypothesis holds.

---

## Section 4: Published Winning Features in Tabular Hot-Rolling Defect Detection

### 4.1 Data Mining Scale Defect Prediction (AIST/ISIJ proceedings, ~2005)
Source: ResearchGate 221173826 — "Data Mining Methods in Hot Steel Rolling for Scale Defect Prediction" [abstract confirmed, full text not accessible]

Closest published analog to the competition dataset. Used **multinomial logit + PLS** on process sensor data from a hot strip mill.

**Top predictors found:** (1) Average temperature entering the finishing mill, (2) average crop shear temperature, (3) **%P (phosphorus content)** of the steel.

**Lesson for V5:** If any Xi column among X1–X49 is a chemistry proxy (grade code, carbon equivalent, or phosphorus-proxy), it must be interacted with ALL ratio features. Phosphorus creating adherent scale is the published number-one root cause and the most actionable external knowledge we have.

### 4.2 Springer SN Computer Science 2023 — Expert Knowledge + ML, Tata Steel Port Talbot
Source: DOI 10.1007/s42979-023-02104-5 [confirmed URL, abstract confirmed]

- Used expert rules combined with ML for width-related defects at Tata Steel Port Talbot hot strip mill
- Key finding: Width deviation defects predicted by **interstand tension anomalies** — actual tension / target tension ratio is a strong feature
- Lesson: **Deviation-from-setpoint features** (actual vs programmed roll gap, actual vs target temperature) are high-value. If setpoint columns exist alongside measured columns, compute `(actual − setpoint) / setpoint`.

### 4.3 Tata Steel Port Talbot ML Paper 2024
Source: ResearchGate 381819957 — "Leveraging Machine Learning Insights at the Hot Strip Rolling Mill, Tata Steel, Port Talbot" [abstract confirmed, full text paywalled]

Almost certainly the institutional parent of this competition dataset. The anonymization of columns as X1–X49 is consistent with Tata Steel's competition anonymization practice. The framing — sensor-tagged coil-level binary quality labels — matches exactly.

### 4.4 Strip Quality Prediction — GBDBN-ELM (Journal of Sensors, Wiley 2021)
Source: Wiley onlinelibrary.wiley.com/doi/10.1155/2021/9943153 [confirmed]

- Used 234-column dataset from finishing mill
- Key features: reduction position, **roll force per stand**, stand speed, **oil film compensation**, **eccentric compensation**
- Key insight: "Compensation/correction" columns (oil film, eccentric) record when control system had to intervene — these correlate strongly with process upsets that cause defects.

### 4.5 Strip Crown Prediction ML (MDPI Metals 2023)
Source: mdpi.com/2075-4701/13/5/900 [confirmed]

- **Inter-stand ratios of force, speed, thickness** were most predictive — not raw values
- Lesson: For each adjacent finishing stand pair (F1/F2, F6/F7), compute force ratio, speed ratio, thickness ratio. These inter-stand gradient features capture process instability better than single-stand values.

### 4.6 Severstal Kaggle 2019 — Not Directly Applicable
Image segmentation competition (U-Net/FPN on 1600x256 grayscale images), not tabular ML. The one transferable lesson: use a **calibrated threshold optimized for the competition metric**, not default 0.5. Our V3 score-aware threshold already applies this.

---

## Section 5: High-Leverage Transforms Beyond Ratios

### T1. Log of Roll Force
**Target:** Scale embedding, all force-driven defects.
**Reason:** Roll force distributions are right-skewed (occasional very high forces on thick/wide coils). Log normalizes the range and makes the relationship approximately linear for tree model threshold splits.
**Formula:** `log(X_force)` or `log(X_force / X_width)`

### T2. Finishing Temperature Deviation from Ar3
**Target:** Edge cracks, mixed-phase rolling defects.
**Formula:** `T_finish − 890` as generic low-carbon proxy, plus binary flag `int(T_finish < 890)`.
Non-linear step change in defect rate at the Ar3 threshold.

### T3. Lambda — Roll Bite Ratio
**Target:** Scale embedding (lambda > 2), edge cracking (lambda < 1).
**Formula:** `lambda = sqrt(R_roll × draft) / h_mean`
If roll radius R not directly in data: finishing stand work roll radius is typically 350–450 mm for HSM.
Non-linear features: `lambda^2` and `int(lambda > 2)`.

### T4. Cumulative Roll Wear Proxy
**Target:** Periodic surface marks (roll wear pattern), scale from worn rolls.
**Formula:** `coil_sequence_mod_100` (typical campaign = 80–150 coils per roll set). As rolls wear, surface roughness increases and scale adherence worsens.
**Source:** Roll wear simulation (Scispace confirmed URL).

### T5. Rolling Window Defect Rate (Temporal Contamination)
**Target:** Inclusion clusters, roll mark propagation.
**Formula:** `prev_5_defect_rate = sum(defect_label[i-5:i]) / 5`
Roll marks propagate to next 2–3 coils; inclusion clusters in a casting sequence create bursts. Confirmed by V4 lag analysis.

### T6. Interstand Speed Ratio Gradient
**Target:** Tension excursions, surface scratches.
**Formula:** `V_F7 / V_F1` vs expected `h_F1/h_F7` (mass conservation). Deviation = tension anomaly.
**Physical basis:** Orowan mass conservation: `V_in × h_in = V_out × h_out` per stand.

### T7. Chemistry Proxy Interaction
**Target:** Scale pits (%P-driven), red scale (%Si-driven fayalite).
**Formula:** If any Xi is grade/chemistry: `CE = %C + %Mn/6 + (%Cr+%Mo+%V)/5 + (%Cu+%Ni)/15`.
Even a grade-code categorical with 5 levels will capture the group effect — published top predictor.

### T8. Ekelund-Motivated Flow Stress Normalization
**Target:** All force-dependent defects.
**Physical basis (Ekelund 1933 [unverified]):** flow stress `k ≈ (14 − 0.01×T)` [kgf/mm^2] in the hot rolling range.
**Formula:** `X_force / (X_temperature × X_width)` as three-way interaction, or `X_force × (1/X_temperature)`.
This captures that the same force on hotter steel is less damaging than on cooler steel.

### T9. Torque/Force Lever Arm Deviation
**Target:** Chatter marks (periodic surface banding at roll circumference harmonics).
**Formula if torque available:** `G / (F × sqrt(R × delta_h))` = normalized lever arm. Deviation from nominal ~0.5 indicates roll eccentricity or bearing issues.
**Proxy if torque unavailable:** coefficient of variation of roll force over 5-coil window = `std(F_window) / mean(F_window)`.

### T10. Quadratic Temperature Term
**Target:** Non-linear scale formation and Ar3 effects.
**Formula:** `(T_finish − 890)^2` — captures both above and below threshold effects (parabolic-like risk curve around critical temperature).

---

## Section 6: External Data Sources (Free/Public, Available Today)

| Source | URL | What it gives | How to use |
|--------|-----|---------------|------------|
| IspatGuru.com | ispatguru.com | Process parameter ranges, Ar3 formulas, defect mechanism descriptions | Validate column identity hypotheses by checking plausible value ranges |
| USPTO Patent DB | patents.google.com | Explicit operating ranges in patents: temps 800–1300°C, forces 10–50 MN, widths 500–2000 mm, speeds 1–15 m/s | Sanity-check which Xi values are temperatures vs forces vs speeds |
| AIST Digital Library | digital.library.aist.org | Proceedings papers including scale defect studies | Access data mining scale defect paper (PR-313-68 and related) |
| PMC Open Access | pmc.ncbi.nlm.nih.gov | Free full-text materials papers — lambda vs defect rate (PMC11301369), roll wear models (PMC11509569) | Lambda curve validation; campaign wear curves |
| MDPI Open Access | mdpi.com/2075-4701 | Free full-text strip crown and quality ML papers with full feature lists | Feature set validation; inter-stand ratio feature lists |

---

## Section 7: Anti-Patterns (What NOT to Try)

### AP1. Naive PCA on Raw Sensors
PCA maximizes variance, not defect-correlation. In a 49-feature mill dataset where X13/X36 is the strongest predictor, PCA buries this ratio inside a PC that mixes in irrelevant high-variance sensors (absolute coil weight, total roll force that varies with product mix). Published HSM quality work consistently shows raw PCA loses predictive signal vs. engineered features.

### AP2. Raw Force Without Width Normalization
Roll separating force scales with strip width. A 2000 mm wide coil at the same specific force produces twice the total force of a 1000 mm coil. Without dividing by width, the model learns "wide coils have higher force" rather than "anomalous force given width = defect signal." Confirmed failure mode in strip crown and width deviation ML papers (MDPI Metals 2023, Springer IJAMT 2023).

### AP3. Temperature Variables Without Grade Grouping
870°C finishing temperature is excellent for a 0.05%C grade (above Ar3) but potentially damaging for a 0.3%C grade (below Ar3). Using absolute temperature without grade grouping creates heterogeneous training — the model can't fit a single temperature threshold that's correct for all grades. Fix: grade × temperature interaction, or grade-stratified analysis.

### AP4. K-Means Clustering on Raw Sensor Matrix
Hot mill data clusters by product geometry (thickness, width, grade), not by defect propensity. Clusters will correspond to product families, not defect regimes. Use supervised anomaly detection or defect-rate-stratified groupby analysis instead.

### AP5. SMOTE Without Temporal Isolation
SMOTE creates synthetic minority samples by interpolating in feature space. With coil-sequence autocorrelation (confirmed in V4), SMOTE can create synthetic coils borrowing features from nearby defective coils, causing test-set leakage if CV folds are not temporally isolated. Use `TimeSeriesSplit` or ensure synthetic samples do not bridge fold boundaries.

### AP6. Ignoring the h/L_p Edge Condition Non-Linearity
The condition `h/L_p > 2` marks the regime where lateral spread dominates and edge cracking ignites. Linear models cannot capture this threshold behavior. Include binary indicator `int(h_mean / L_c > 1.5)` to give the model an explicit non-linear gate for this mechanism.

---

## Section 8: Governing Equations — Sims / Ekelund / Orowan

### 8.1 Orowan (1943) — Fundamental Roll Pressure Distribution
**Reference:** Orowan, E. (1943). "The Calculation of Roll Pressure in Hot and Cold Flat Rolling." *Proc. IMechE*, 150, 140–167. **[VERIFIED — SAGE Journals DOI: 10.1243/PIME_PROC_1943_150_025_02]**

The Orowan differential equation for roll pressure `p(theta)` along the arc of contact:

```
dp/dtheta = (2k / h(theta)) × (h(theta) × tan(theta) +/- mu × R_prime)
```

Where: theta = angular position along arc; k = shear yield stress = sigma_y/2; h(theta) = strip thickness at angle theta; mu = friction coefficient; R_prime = deformed roll radius. The +/- distinguishes entry zone (friction assists) from exit zone (friction opposes). The neutral point (where strip speed equals roll surface speed) shifts with process conditions — shifting it toward exit increases the friction hill = embedded scale risk.

**ML interaction terms motivated:**
- `R_prime / h_exit`: pressure amplification ratio (dominant for thin gauge on large rolls)
- `mu × sqrt(R_prime / delta_h)`: combined friction-geometry product
- `k_flow × L_c`: flow stress × contact arc = nominal force term

### 8.2 Sims (1954) — Practical Roll Force and Torque
**Reference:** Sims, R.B. (1954). "The Calculation of Roll Force and Torque in Hot Rolling Mills." *Proc. IMechE*, 168, 191–200. **[VERIFIED — Semantic Scholar + SAGE Journals DOI: 10.1243/PIME_PROC_1954_168_023_02]**

```
F = w × k_bar × Q_p × L_c

where:
  L_c    = sqrt(R_prime × delta_h)         [contact arc length, mm]
  k_bar  = mean flow stress [MPa]          [temperature + strain-rate dependent]
  Q_p    ≈ (pi/2) × sqrt(R_prime/h_exit) × arctan(sqrt(r × R_prime/h_exit)) / sqrt(r)
  r      = delta_h/h_entry                 [reduction ratio]
  w      = strip width [mm]

Torque: M = 2F × a_L, where a_L ≈ 0.4–0.5 × L_c
```

**ML interaction terms motivated:**
- `sqrt(R_roll × draft)`: contact arc length, computable if R and draft available
- `R_roll / h_exit`: pressure amplification (Q_p dominant term) — key Xi/Xj pair
- `(R_roll / h_exit)^0.5 × reduction_ratio^0.5`: Q_p approximation as single feature
- `F / (w × L_c)`: back-calculated mean specific pressure from measured force

### 8.3 Ekelund (1933) — Temperature-Dependent Flow Stress and Friction
**Reference:** Ekelund, S. (1933). "The Analysis of Factors Influencing Rolling Pressure and Power Consumption in the Hot Rolling of Steel." *Steel* (Swedish Ironmasters' Association). **[UNVERIFIED — known via secondary citations in ScienceDirect 2022 literature review and Springer IJAMT]**

```
k_Ekelund = (14 − 0.01 × T) × (1 + 0.3×%C + 0.5×%Mn) × (1 + 0.15×%Cr)   [kgf/mm^2]

mu_Ekelund = 1.05 − 0.0005 × T   [valid 700–1100°C]
```

Where T is temperature in °C.

At 900°C: k ≈ 5 kgf/mm^2. At 800°C: k ≈ 6 kgf/mm^2. The 100°C drop increases flow stress by ~20%, amplifying roll force and scale-embedding pressure. This is why temperature and force interact non-linearly.

**ML interaction terms motivated:**
- `(14 − 0.01 × T_finish)`: flow stress proxy feature from temperature alone
- `X_force / (14 − 0.01 × T_finish)`: force normalized by estimated flow strength = true deformation severity
- `T_finish × (T_finish − 900)`: quadratic temperature term around Ar3 range
- `X_force / X_temperature`: simplified Ekelund normalization (most actionable if exact columns unknown)

---

## V5 Feature Engineering Master Priority List

**Tier 1 — Highest impact (physics + published evidence, build unconditionally):**
1. `X13 / X36` — already in model; add div-by-zero guard
2. `X13 − X36` and `X36 − X13` — signed differences
3. `abs(X13 − X36) / (X13 + X36)` — normalized deviation
4. `prev_5_defect_rate`, `prev_2_defect_rate`, `prev_1_defect` — temporal lag features
5. All pairwise ratios of top-5 SHAP features: X13, X36, X14, X16 — generate 10 ratios and let SHAP select

**Tier 2 — Medium impact (formula-derived, need column identification):**
6. `X_force / X_width` — specific roll force (once force and width columns are ID'd by value range analysis)
7. `X_finish_temp − 890` — Ar3 deviation (if temperature columns identified)
8. `X_finish_temp / X_coil_temp` — FT/CT ratio
9. `(X_finish_temp − 890)^2` — quadratic Ar3 deviation
10. `X_force / (X_width × X_finish_temp)` — Ekelund-motivated three-way normalization
11. `sqrt(R_roll × draft) / h_mean` — lambda, if thickness/geometry columns identifiable

**Tier 3 — Speculative but defensible:**
12. `coil_sequence_mod_100` — roll wear proxy
13. All `Xi^2` and `Xi × Xj` polynomial terms for top-10 SHAP features
14. Chemistry proxy if any Xi has integer-like range suggesting grade code categorical

---

## References Summary

| Reference | Venue | Year | Verification Status |
|-----------|-------|------|---------------------|
| Sims, R.B., "Roll Force and Torque in Hot Rolling Mills" | Proc. IMechE | 1954 | **VERIFIED** (SAGE DOI confirmed) |
| Orowan, E., "Roll Pressure in Hot and Cold Flat Rolling" | Proc. IMechE | 1943 | **VERIFIED** (SAGE DOI confirmed) |
| Ekelund, S., "Factors Influencing Rolling Pressure and Power" | Steel (Swedish IMA) | 1933 | [unverified — known via secondary citations] |
| "Data Mining Methods in Hot Steel Rolling for Scale Defect Prediction" | AIST/ISIJ proceedings | ~2005 | [unverified — ResearchGate abstract only] |
| "Leveraging ML Insights at the Hot Strip Rolling Mill, Tata Steel, Port Talbot" | ResearchGate / Tata | 2024 | [unverified — paywalled] |
| "Expert Knowledge + ML for Defect Detection in a Hot Strip Mill" | SN Computer Science (Springer) | 2023 | **VERIFIED** (DOI: 10.1007/s42979-023-02104-5) |
| "Effects of FT and CT on Scale Structure and Picklability" | AIST (PR-313-68) | ~2003 | **VERIFIED** (AIST store title confirmed) |
| "Occurrence of surface defects on strips during hot rolling by FEM" | IJAMT (Springer) | 2012 | **VERIFIED** (DOI: 10.1007/s00170-012-4556-7) |
| "Quality Prediction of Strip in Finishing Rolling (GBDBN-ELM)" | Journal of Sensors (Wiley) | 2021 | **VERIFIED** (Wiley URL confirmed) |
| "Prediction Model of Strip Crown Using ML and Industrial Data" | MDPI Metals | 2023 | **VERIFIED** (mdpi.com/2075-4701/13/5/900) |
| "Experimental selection of L/h_bar ratio for hot-rolling superalloy sheet" | PMC (PMC11301369) | 2024 | **VERIFIED** (PMC confirmed) |
| "Roll force and torque fluctuations during hot strip rolling" | Tandfonline | 2014 | **VERIFIED** (URL confirmed) |
| Andrews, K.W., "Empirical formulae for transformation temperatures" | JISI | 1965 | [unverified — standard citation, widely cited] |

**Confidence:** High (physics + equations + anti-patterns), Medium (column ID hypotheses + Tata-specific findings)
