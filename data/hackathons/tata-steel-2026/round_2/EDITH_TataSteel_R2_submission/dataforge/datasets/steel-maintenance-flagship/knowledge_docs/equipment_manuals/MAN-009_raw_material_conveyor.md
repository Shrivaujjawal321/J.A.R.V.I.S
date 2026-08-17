# Equipment Manual: Raw Material Overland Conveyor
**Asset ID:** RM.CONV.ORE01
**Equipment Class:** raw_material_conveyor
**Document:** MAN-009 | Rev 1.0 | Site: TATA_JSR (Synthetic Reference)
**Standard References:** CEMA Handbook 6th Ed., ISO 5048, UE Systems ultrasound guides, Fenner Dunlop RipScan

> **DISCLAIMER — SYNTHETIC DOCUMENT.** All numeric values are representative industry estimates grounded in cited standards. No proprietary Tata Steel data is used.

---

## 1. Equipment Description

RM.CONV.ORE01 is the main ore-yard-to-stockhouse overland conveyor transporting iron ore from raw material yard to blast furnace stockpile. As a high-volume bulk-materials conveyor carrying abrasive ore, it is subject to continuous idler bearing fatigue, belt wear, and occasional overload from chute blockages.

**Manufacturer:** TRF / Fenner Dunlop
**Model:** 1600 mm belt, EP630 (Polyester-Polyamide fabric, 630 N/mm breaking strength)
**Rated Power:** 800 kW (drive motor)
**Process Stage:** Raw material handling
**Criticality:** 2
**Installation Date:** 2018-12-05
**Last Overhaul:** 2024-03-30

**Conveyor components:**
- **Belt:** EP630, 1600 mm wide; multiple-ply fabric carcass; rubber top and bottom covers
- **Drive arrangement:** Head pulley drive, 800 kW motor + gearbox; possibly with take-up gravity counterweight
- **Idlers:** Carrying (3-roll trough), return (2-roll flat), impact (at loading point); typically every 1–1.5 m carrying, every 3 m return
- **Pulleys:** Head (drive), tail (take-up), snub, bend
- **Belt rip detection:** Embedded conductor loop (Fenner RipScan); open circuit = tear

---

## 2. Technical Specifications

| Parameter | Value |
|-----------|-------|
| Belt width | 1600 mm |
| Belt type | EP630 (polyester warp, polyamide weft) |
| Belt breaking strength | 630 N/mm per ply |
| Belt speed | 3–5 m/s (typical ore duty) |
| Trough angle | 35° (3-roll carrying set) |
| Carrying idler spacing | ~1.0–1.5 m |
| Return idler spacing | ~3 m |
| Idler roller diameter | 152 or 194 mm (standard) |
| Idler bearing type | Spherical roller bearing or deep-groove ball (sealed, grease-packed) |
| Drive motor rating | 800 kW; squirrel-cage induction |
| Drive motor protection | Overload relay + soft-starter or VFD |
| Take-up type | Gravity counterweight (constant tension) |

---

## 3. Sensor Instrumentation

| Tag | Quantity | Unit | Normal Range | Warning | Alarm | Standard |
|-----|----------|------|-------------|---------|-------|----------|
| JSR.RM.CONV1.MTR.CURR | Drive motor current | %FLA | 60 – 95 | 105 | 125 | NEMA MG1 / IEC 60947-4 |
| JSR.RM.CONV1.IDLER.US | Idler ultrasound level | dBuV | −20 – −8 | 8 | 15 | UE Systems (unverified; above baseline) |
| JSR.RM.CONV1.IDLER.TEMP | Idler surface temperature | degC | 25 – 60 | 80 | 100 | Fire-risk threshold |
| JSR.RM.CONV1.BELT.EDGE | Belt edge position | mm | −15 – +15 | 25 | 50 | CEMA §6 (unverified) |
| JSR.RM.CONV1.RIP.LOOP | Rip detector loop current | mA | 60 – 80 | 48 | 0 | Fenner RipScan (unverified) |

**IDLER.US note:** Ultrasound is measured by a patrol-based or fixed sensor. Values are above-baseline in dBuV. Warning at 8 dBuV above baseline = bearing generating high-frequency friction signals (early stage). Alarm at 15 dBuV = bearing in advanced distress; seizure and fire risk imminent.

**RIP.LOOP note:** A continuous loop embedded in the belt generates a measurable current when intact. Any break in the loop (belt longitudinal rip) → loop open → current drops to 0 (alarm). Warning at 48 mA may indicate partial conductor damage. This is a hardwired safety system — 0 mA must stop the belt immediately.

**BELT.EDGE note:** Positive values = belt tracking toward operator side; negative = opposite. ±25 mm warning; ±50 mm alarm (belt rubbing on structure; risk of edge damage).

---

## 4. Operating Limits

| Condition | Limit | Action |
|-----------|-------|--------|
| MTR.CURR | >105% FLA (warning) | Suspect overloaded chute or plugged chute; check loading zone |
| MTR.CURR | >125% FLA (alarm) | Stop belt; inspect for stall/jam/material surge |
| IDLER.US | >8 dBuV above baseline (warning) | Tag idler for replacement in next patrol stop |
| IDLER.US | >15 dBuV above baseline (alarm) | Stop belt immediately; fire risk |
| IDLER.TEMP | >80 °C (warning) | Confirm hot idler via IR camera; tag for urgent replacement |
| IDLER.TEMP | >100 °C (alarm) | Stop belt immediately; fire/smoke risk |
| BELT.EDGE | >25 mm (warning) | Adjust training idlers; check loading alignment |
| BELT.EDGE | >50 mm (alarm) | Stop belt; belt damage / structure collision risk |
| RIP.LOOP | 48 mA (warning) | Inspect belt surface for damage; slow down belt |
| RIP.LOOP | 0 mA (alarm) | Stop belt immediately; belt rip confirmed |

---

## 5. Known Failure Modes

### 5.1 Idler Bearing Failure — Primary and Most Common Mode

**Root Cause:** Sealed idler bearings have finite grease life; contamination from water and ore dust degrades seals; bearings run dry → seizure. A seized idler under a loaded belt generates frictional heat → ignites rubber belt (belt fire).

**Why this matters:** Seized idler is the #1 initiator of conveyor belt fires in steel plants. Belt rubber ignites at ~300 °C; a seized idler running under a loaded belt can reach this temperature in minutes.

**Degradation Timeline:**
- Healthy: IDLER.US = −14 dBuV; IDLER.TEMP = 42 °C
- Warning: IDLER.US rises to 8 dBuV above baseline (friction noise detectable)
- Alarm: IDLER.US = 16 dBuV above baseline; IDLER.TEMP = 100 °C (fire-risk threshold)
- Failure: Belt fire; full belt replacement; production halt

**Sensor Signature:**
- IDLER.US: −14 → 16 dBuV (alarm)
- IDLER.TEMP: 42 → 100 °C (alarm)

**Fault Codes:** IDLER-US-ALARM, IDLER-TEMP-FIRE
**Planned TTR:** 0.5 hours | **Unplanned TTR:** 2 hours | **Cost Impact:** INR 625,000 / USD 7,500 (idler change before fire)
**Note:** Full conveyor belt fire event ~INR 10,000,000 / USD 120,000 if not caught early.
**Safety Class:** P1 (fire risk)

### 5.2 Belt Misalignment (Tracking)

**Root Cause:** Uneven loading (off-centre chute), worn or misaligned training idlers, pulley misalignment, or belt splice angle deviation. Belt edge runs against conveyor structure → edge damage → belt weakening.

**Signature:** BELT.EDGE > ±25 mm (warning); visible inspection shows belt rubbing on frame or covers.

**Consequences:** Edge damage reduces belt breaking strength; if edge torn through, structural failure possible; belt replacement needed.

**Action:** Adjust training (self-aligning) idlers; check loading alignment; check take-up tension symmetry.

### 5.3 Motor Overload / Blocked Chute

**Root Cause:** Material surge from ore stockpile slumping; blocked transfer chute (wet/sticky ore); belt start-up with frozen material (winter).

**Signature:** MTR.CURR spikes to >105% FLA (warning) → >125% FLA (alarm); belt decelerates; motor thermal relay trips.

**Consequence:** Motor thermal damage if sustained; gearbox overload if belt stalls suddenly (shock torque).

**Action:** Stop belt; clear chute blockage manually (LOTO first); check if belt is still moving (not stalled against a jam).

### 5.4 Belt Rip / Tear

**Root Cause:** Sharp tramp metal or rock from ore stockpile penetrates belt at loading zone; longitudinal rip can propagate the full conveyor length in seconds if not immediately stopped.

**Signature:** RIP.LOOP drops to 0 mA (alarm); audible tearing sound; material spillage along conveyor.

**Consequence:** Belt section (BELT-SEC-1600) replacement; up to 10-week lead for made-to-order belt; vulcanising splice required (VULC-KIT-01).

---

## 6. Preventive Maintenance Schedule

| Task | Interval | Method | Notes |
|------|----------|--------|-------|
| Idler patrol inspection (visual + ultrasound) | Weekly (or every 40 operating hours) | Walking patrol with UE Systems SDT | Listen for dry bearings; flag by colour code |
| IR idler temperature survey | Monthly | Thermal camera during operation | Identify hot idlers before seizure |
| Belt tracking check | Daily (pre-shift) | Visual observation + BELT.EDGE sensor | Adjust training idlers proactively |
| Belt surface inspection (top and bottom covers) | Monthly | Walking inspection; stop belt for full visual | Mark worn zones; measure cover thickness |
| Rip detector (RIP.LOOP) function test | Monthly | Interrupt loop with test device; verify alarm | Zero tolerance for defeated rip detector |
| Drive motor current trend | Continuous | SCADA | Seasonal change (wet/frozen ore) |
| Idler replacement (IDLER-STD-1600) | On ultrasound warning or temperature flag | Patrol stop | Stock 40 units; zero lead time |
| Self-aligning idler inspection (IDLER-TRAIN-01) | 3-monthly | Visual; check pivot freedom | Replace stiff units |
| Belt splice inspection | Monthly | Visual (top and bottom) | Mechanical fastener splice: check belt-to-belt condition; replace if separating |
| Head and tail pulley lagging inspection | 6-monthly | Visual | Worn lagging → belt slip under load → overload alarm |
| Gearbox oil level + condition | Monthly | Dipstick + oil sample | Drive gearbox (separate from conveyor frame) |

---

## 7. Troubleshooting

### T1 — IDLER.TEMP > 80 °C or IDLER.US > 8 dBuV (Warning)

1. Flag the idler (spray-paint the frame) for replacement in the next opportunity stop.
2. Confirm via IR camera — if temperature confirmed >80 °C: prioritise replacement within 1–2 shifts.
3. **Do not leave a >80 °C idler running unattended** — temperature can escalate to fire threshold quickly on a loaded belt.
4. At stop: LOTO belt; lift belt with pry bar or jacking bar; swap idler (IDLER-STD-1600; stock 40).
5. Check adjacent idlers — clustered failures indicate section of belt with poor cover/water ingress.

### T2 — IDLER.TEMP > 100 °C / IDLER.US > 15 dBuV (Alarm — FIRE RISK)

1. **Stop belt immediately.**
2. Sound fire alarm; prepare CO2/dry powder extinguisher; check for smoke.
3. LOTO; wait for IR confirmation that belt is not smouldering before manual inspection.
4. Replace seized idler (IDLER-STD-1600).
5. Inspect belt for heat damage (rubber cracking/melting above the idler).
6. If belt is heat-damaged: assess splice-in repair vs. full replacement.

### T3 — RIP.LOOP = 0 mA (Alarm)

1. Belt stops automatically (rip detector hardwired to emergency stop relay).
2. Walk the entire belt length; locate rip (may be longitudinal, 1–50+ m long).
3. LOTO before entering belt tunnel or returning belt side.
4. Assess rip extent; if minor (transverse, <50 mm): vulcanise (VULC-KIT-01).
5. If major longitudinal rip: belt section replacement (BELT-SEC-1600; 0 in stock, 10-week lead). Arrange temporary conveyor or truck haulage.

### T4 — BELT.EDGE > 25 mm (Warning)

1. Check loading chute centreline — material off-centre loading is the most common cause.
2. Adjust self-aligning training idlers downstream of loading zone.
3. Check tail pulley alignment (laser or string line).
4. If belt continues to migrate after adjustment: consider belt inspection for splice angle error.

---

## 8. Corrective Maintenance — Idler Replacement

**Required Spares:**
| Part ID | Description | Stock | Lead Time |
|---------|-------------|-------|-----------|
| IDLER-STD-1600 | Standard carrying idler 1600mm belt | 40 | Stock |
| IDLER-TRAIN-01 | Training/self-aligning idler | 6 | 4 weeks |
| BELT-SEC-1600 | Belt section EP630 1600mm | 0 | 10 weeks |
| VULC-KIT-01 | Belt vulcanising kit | 2 | Stock |

**Planned TTR (idler change):** 0.5 hours
**Unplanned TTR (idler seizure + fire check):** 2 hours
**Safety Class:** P1

---

## 9. Safety

- **Fire risk:** Seized idler is classified as P1 because the belt fire that follows can destroy the entire conveyor (>INR 10M) and injure personnel. Always respond to idler temperature alarm as a fire precursor — not a routine maintenance flag.
- **LOTO — belt energy:** The belt stores significant elastic energy under tension; even after motor LOTO, the take-up counterweight can drive the belt if not mechanically blocked. Apply belt travel locks at head pulley.
- **Confined-space / belt tunnel:** Many conveyors run in enclosed tunnels; oxygen depletion from CO2 extinguishant and dust accumulation are hazards; gas test before entry; confined-space permit required.
- **Entanglement hazard:** Never approach moving belt without full LOTO; return belt and carry belt move at 3–5 m/s; entanglement is instantly fatal.
- **Dust explosion hazard:** Ore dust (especially if coal conveyor nearby) can form explosive atmosphere; no hot-work without gas check and area clearance.
- **Tramp metal:** Tramp metal in ore causes rip events; magnetic separator maintenance is a prevention measure but not part of this conveyor directly — liaise with yard team.
