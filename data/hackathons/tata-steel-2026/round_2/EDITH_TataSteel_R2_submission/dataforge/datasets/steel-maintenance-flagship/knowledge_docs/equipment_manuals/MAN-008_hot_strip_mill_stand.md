# Equipment Manual: Hot Strip Mill Rolling Stand
**Asset ID:** HSM.STD.R1
**Equipment Class:** hot_strip_mill_stand
**Document:** MAN-008 | Rev 1.0 | Site: TATA_JSR (Synthetic Reference)
**Standard References:** ISO 20816-3:2022, ASTM E2374-14, Primetals AGC/roll-force documentation

> **DISCLAIMER — SYNTHETIC DOCUMENT.** All numeric values are representative industry estimates grounded in cited standards. No proprietary Tata Steel data is used.

---

## 1. Equipment Description

HSM.STD.R1 is the 4-high reversing roughing stand (R1) at the entry of the hot strip mill. It reduces incoming slab thickness by multiple reversing passes before the strip enters the finishing stands (F1–F7). The stand incorporates AGC (Automatic Gauge Control) hydraulic screwdown, work-roll and backup-roll chock assemblies, and online load-cell-based force measurement.

**Manufacturer:** Primetals
**Model:** 4-high reversing stand
**Process Stage:** Hot rolling (roughing)
**Criticality:** 1
**Installation Date:** 2017-09-10
**Last Overhaul:** 2024-01-25

**Stand configuration:**
- **2 work rolls (WR):** High-speed steel (HSS) composition; direct contact with hot steel strip; subject to thermal and mechanical fatigue
- **2 backup rolls (BUR):** Larger diameter; support work rolls against bending; forged steel
- **4 roll chocks:** Carry roll neck bearings; hydraulic locking
- **AGC screwdown:** Hydraulic cylinders (position-controlled) adjusting roll gap in real time
- **Load cells:** Measure rolling force (kN or MN) — force ripple is the primary defect indicator

---

## 2. Technical Specifications

| Parameter | Value |
|-----------|-------|
| Stand type | 4-high reversing |
| Work roll diameter (new) | ~700–900 mm |
| Work roll minimum condemn dia | ~650–820 mm (depending on roll body length; OEM-specified) |
| Work roll material | High-speed steel (HSS); hardness HSD 78–85 surface |
| Backup roll diameter | ~1400–1600 mm |
| AGC cylinder pressure | Up to 350 bar |
| Roll change time | 15–45 minutes (quick-change chock system) |
| Roll campaign length | Governed by surface condition; typically 50–200 passes per redress |
| Rolling temperature (slab exit R1) | 1050–1150 °C |
| Rolling force range | 10–50 MN (slab-grade and thickness dependent) |

---

## 3. Sensor Instrumentation

| Tag | Quantity | Unit | Normal Range | Warning | Alarm | Standard |
|-----|----------|------|-------------|---------|-------|----------|
| JSR.HR.R1.FORCE | Rolling force ripple (periodic, at 1× roll) | % | 0 – 2 | 4 | 8 | Tata PdM internal (unverified) |
| JSR.HR.R1.WR.VIB.CHOCK | Chock vibration (chatter) | mm/s | 0 – 1.0 | 4.0 | 10.0 | ABB CMC (unverified) |
| JSR.HR.R1.CROWN.DEV | Strip crown deviation | µm | −10 – +10 | 25 | 40 | Industry (unverified) |
| JSR.HR.R1.WR.AE.RMS | Roll journal AE RMS | dB | −3 – +3 | 8 | 15 | ASTM E2374-14 (unverified) |

**FORCE ripple note:** The signal is the amplitude of the periodic rolling-force component at the rotational frequency of the work roll. In a healthy roll, force is nearly constant (ripple <2%). A spalled roll surface creates a periodic impact once per revolution as the spall flat contacts the strip → ripple rises. Period of the defect on strip = π × D_roll.

**VIB.CHOCK note:** Chock vibration is a chatter indicator. Fifth-octave chatter (a resonant instability) generates high-frequency vibration at the chock that can damage strip surface with regular marks at millimetre spacing.

---

## 4. Operating Limits

| Condition | Limit | Action |
|-----------|-------|--------|
| FORCE ripple | >4% (warning) | Increase strip surface inspection; consider reducing passes per campaign |
| FORCE ripple | >8% (alarm) | Stop rolling; change work rolls; segregate strip produced |
| VIB.CHOCK | >4.0 mm/s (warning) | Chatter developing; check rolling speed and reduction schedule |
| VIB.CHOCK | >10.0 mm/s (alarm) | Stop; chatter damage accumulating; change rolls |
| CROWN.DEV | >25 µm (warning) | Crown control adjustment; check backup roll profile |
| CROWN.DEV | >40 µm (alarm) | Stop; inspect roll profile; crown compensation may be exhausted |
| AE.RMS | >8 dB (warning) | Roll journal bearing or surface defect developing |
| AE.RMS | >15 dB (alarm) | Urgent inspection; roll surface fracture or journal failure risk |

---

## 5. Known Failure Modes

### 5.1 Work Roll Spall / Flat — Primary Mode

**Root Cause:** Subsurface roll fatigue defect (initiated by thermal shock, cobble impact, or inclusion in roll blank) breaks out at the roll surface, creating a flat or spalled area. Each revolution, the flat impacts the strip → periodic force ripple.

**Physics:** Spall initiation at subsurface crack (depth 0.5–5 mm); once crack reaches surface, spall fragment separates. Fragment may mark the strip surface or remain attached as a flat. Danger: fragment detachment can cause injury and process upset.

**Degradation Timeline:**
- Healthy campaign: FORCE ripple 1.2%; VIB.CHOCK 0.6 mm/s
- Warning: FORCE ripple rising toward 4% at 1× roll frequency; AE.RMS slight increase
- Alarm: FORCE ripple ≥8%; VIB.CHOCK 6.0 mm/s; periodic marks visible on strip surface
- Risk: Spall fragment detachment; secondary roll/strip damage

**Sensor Signature:**
- FORCE: 1.2 → 8.5% (alarm)
- VIB.CHOCK: 0.6 → 6.0 mm/s (alarm)

**Fault Codes:** FORCE-RIPPLE-HIGH, SURFACE-DEFECT-PERIODIC
**Planned TTR:** 0.75 hours (roll change) | **Unplanned TTR:** 4 hours
**Cost Impact:** USD 184,000 (planned: $11,200 vs unplanned: $184,000 — 16.4× ratio)
**Safety Class:** P2

### 5.2 Roll Wear / Thermal Camber Loss

**Root Cause:** Accumulated rolling cycles erode HSS roll surface; thermal camber (crown developed by temperature gradient across roll length) changes with number of passes, altering strip crown.

**Signature:** CROWN.DEV drifting outside ±10 µm; no force ripple (wear is not periodic).

**Action:** Roll redress in roll shop (regrind 3–5 mm below defect); measure thermal camber and surface finish; return to campaign after UT clearance.

### 5.3 Roll Chatter (5th Octave)

**Root Cause:** Resonant vibration coupling between roll, chock, and mill stand structure at 5th octave chatter frequency (typically 100–200 Hz for a hot strip mill). Triggered by worn roll bearings, poor roll surface condition, or sub-optimal speed/reduction combination.

**Signature:** VIB.CHOCK elevated at characteristic frequency; strip shows regular surface marks at close spacing (0.5–5 mm period); CROWN.DEV may increase.

**Action:** Reduce rolling speed; change work rolls; check chock bearing clearances; notify process metallurgy for product segregation.

### 5.4 Roll Surface Fatigue Crack

**Root Cause:** Thermal fatigue (fire cracking) from repeated heating and quenching. Networks of surface cracks (herringbone / fire-crack pattern) on roll surface.

**Signature:** AE.RMS elevated (fire-crack network generates AE); force ripple may or may not be elevated; visual inspection confirms.

**Action:** Roll to roll shop; UT test after grinding; condemn if crack depth exceeds min dia specification.

---

## 6. Preventive Maintenance Schedule

| Task | Interval | Method | Notes |
|------|----------|--------|-------|
| Online FORCE ripple monitoring (all passes) | Continuous 100 Hz | Load cells → SCADA | 1× roll frequency FFT |
| Chock vibration monitoring | Continuous, burst | Accelerometer | Chatter detection |
| Strip crown/gauge measurement | Continuous 1 Hz | X-ray gauge or isotope gauge | CROWN.DEV feedback to AGC |
| Work roll surface inspection | At each roll change (visual) | Operator visual + roll shop | Spalls, fire cracks, flat marks |
| Work roll UT inspection | At roll shop (each redress) | Immersion UT | Subsurface crack check per OEM |
| Work roll grind (redress) | Per campaign (50–200 passes or surface condition) | Roll shop CNC grinder | 3–5 mm per redress; measure surface finish Ra |
| Work roll profile measurement | At each redress | Roll profile gauge | Compare to required profile |
| Backup roll inspection | At major maintenance shutdown | UT + visual | Longer campaign than WR; typically 3–6 months |
| Chock seal replacement (CHOCK-SEAL-01) | At roll change or seal failure | Roll shop | Stock 4 units; 6-week lead for replenishment |
| Roll bearing inspection | At roll change | Roll shop disassembly | Check clearances; replace if worn |
| AGC cylinder seal check | 6-monthly | Hydraulic leakage test | High-pressure seals; replace on seep |

---

## 7. Troubleshooting

### T1 — FORCE Ripple > 4% (Warning)

1. Check ripple frequency — if period = π × D_roll, it is 1× roll frequency → spall/flat.
2. Check strip surface on-line inspection system — periodic marks confirm spall printing.
3. If confirmed: plan roll change at end of current bar/slab.
4. Do NOT continue rolling high-value grades (automotive, exposed) until rolls changed.
5. Segregate any strip produced with FORCE ripple > 4% for quality hold and inspection.

### T2 — FORCE Ripple > 8% (Alarm)

1. Stop rolling on current product immediately.
2. Quick-change work rolls — WR-HSS-PREP (stock: 4 pairs in roll shop).
3. Roll change time: 15–45 min (budget: up to 4 hours unplanned if chock issues).
4. Send affected rolls to roll shop: grind 3–5 mm below spall depth.
5. UT test after grind; condemn if below minimum diameter.
6. Segregate and inspect all strip produced since last confirmed good FORCE reading.

### T3 — VIB.CHOCK > 4.0 mm/s (Chatter Warning)

1. Reduce rolling speed by 10–20%.
2. Check reduction schedule — very thin gauges at high speeds are chatter-prone.
3. Adjust AGC response (some chatter is AGC-excited — retune gain).
4. If chatter persists: change work rolls (worn surface increases chatter susceptibility).
5. Inspect strip surface — if regular marks present: quality hold.

### T4 — CROWN.DEV > 25 µm (Warning)

1. Apply bend-force correction via hydraulic bender (if within range).
2. If crown cannot be corrected within the bender range: rolls need redress.
3. Check backup roll crown compensation schedule — backup roll approaching condemn dia?

---

## 8. Corrective Maintenance — Roll Change

**Required Spares:**
| Part ID | Description | Stock | Lead Time |
|---------|-------------|-------|-----------|
| WR-HSS-PREP | Prepared work roll pair (HSS, roll shop) | 4 | 0 (roll shop) |
| CHOCK-SEAL-01 | Roll chock seals | 4 | 6 weeks |

**Note on WR-HSS-PREP:** These are not purchased spares but prepared rolls from the plant roll shop inventory. Roll shop maintains a rolling inventory; minimum 4 pairs in "ready" state is the operational standard.

**Planned TTR:** 0.75 hours | **Unplanned TTR:** 4 hours
**16.4× cost penalty for unplanned vs. planned** (OxMaint benchmark: planned $11.2k vs. unplanned $184k)
**Safety Class:** P2

**Roll Change Procedure:**
1. Stop the stand on a gap condition (roll clear of strip).
2. LOTO: main motor VFD off; AGC hydraulics depressurised; chock locks released.
3. Extract WR chock assembly using quick-change crane fixtures (OEM-supplied).
4. Insert prepared WR pair (WR-HSS-PREP) — confirm correct roll profile and direction.
5. Lock chocks; reconnect lube supply; reconnect AE sensors and position probes.
6. Re-roll test bar; confirm FORCE ripple <2%, VIB.CHOCK <1.0 mm/s.
7. Release for production.

---

## 9. Safety

- **Spall fragment ejection:** A spall fragment detaching at rolling speed (0.5–3 m/s strip) has lethal kinetic energy; operator access to the mill housing during rolling is PROHIBITED; rolling area must be guarded.
- **Hot strip ejection (cobble):** If AGC fails or strip jams, hot strip (1050–1150 °C) cobbles violently; all personnel must be behind cobble guards during rolling.
- **Roll change crush hazard:** Work rolls weigh 5–15 tonnes; use OEM lifting fixtures; never lift via unrated rigging on roll body.
- **AGC hydraulic pressure:** Up to 350 bar; depressurise before breaking any connections; verify AGC position sensor shows zero before accessing cylinders.
- **Noise:** Stand noise during rolling can exceed 105 dB(A); mandatory hearing protection; communication via radio or hand signals only.
- **Hot roll surface:** After rolling, roll surface can be 400–600 °C; wait for IR confirmation <100 °C before roll shop grinding; risk of thermal burns and damage to grinder wheel.
