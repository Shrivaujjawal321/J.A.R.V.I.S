# SOP-10 — Ladle Crane Wire Rope Replacement and Brake Service
## TATA_JSR Maintenance Standard Operating Procedure

**Document ID:** SOP-10  
**Revision:** 1.0  
**Effective Date:** 2026-06-09  
**Equipment Class:** ladle_crane  
**Primary Asset Reference:** MS.LDC.CRN01  
**Trigger Failure Modes:** wire_rope_fatigue_broken_wire | hoist_gearbox_gear_wear | brake_wear_slip  
**Spine Scenario Reference:** SCN-047 (MS.LDC.CRN01 — wire_rope_fatigue_broken_wire; MFL 320 mV, rope at discard criterion)  
**Standard:** ISO 4309:2017 (wire rope selection, care, maintenance, and discard criteria) | FEM 1.001 | BS EN 13135 | OSHA 1910.179 (overhead cranes)  
**Safety Class:** P1 — LADLE CRANE HANDLING MOLTEN STEEL IS A LIFE-SAFETY ASSET. ROPE OR BRAKE FAILURE = POTENTIAL LADLE DROP = MASS FATALITY RISK  
**Disclaimer:** SYNTHETIC procedure grounded in research/machinery/11, /18, /19. Values tagged [unverified] are industry estimates. MS.LDC.CRN01 is a Konecranes 320 T ladle crane. Refer to Konecranes OEM documentation for reeving diagram, rope specification, drum groove geometry, and brake torque values. Competent Person inspection certification is a legal requirement in India (Factories Act / BOCW Act).

---

## 1. SCOPE

**Wire rope replacement:** Any time wire rope meets or exceeds ISO 4309:2017 discard criteria (see Section 3), the crane must be taken out of service immediately and the rope replaced before any further lifting operation. This is a legal and safety requirement, not a maintenance preference.

**Brake service:** Brake pad replacement and brake functional testing on the MS.LDC.CRN01 hoist mechanism. A slipping brake on a crane carrying a 320 T ladle of molten steel is a catastrophic failure.

**Hoist gearbox (GMF alarm):** Basic inspection and oil service — triggered by JSR.MS.CRN01.GBX.VIB.GMF > 1.0 g alarm. Full gearbox overhaul per SOP-02 procedures adapted for crane service.

> **Molten-metal ladle crane regime (stricter than general EOT crane):** WLL alarm at 95 % SWL (not 100 %); power cut at 110 % SWL. Any load limiter bypass or mechanical interlock defeat is absolutely prohibited.

---

## 2. SAFETY / LOTO

> **Before any work on this crane: a licensed Competent Person (CP) must be present. The CP is legally responsible for certifying the crane for return to molten-metal service. No return to service without CP sign-off.**

| Step | Action |
|------|--------|
| S-1 | Park crane in maintenance bay. Lower hook block to ground on blocking — do NOT leave hook block suspended during maintenance |
| S-2 | If load is currently suspended: lower load to ground under control before taking crane out of service. Never leave molten ladle hanging while investigating rope/brake issues |
| S-3 | Isolate crane at main isolator (crane cabin isolator + main feeder at sub-station). Lock — personal lock + danger tag |
| S-4 | Apply mechanical travel stop to crane runway to prevent runway travel during maintenance |
| S-5 | Apply wheel chocks to crane bridge girder if work involves climbing on crane structure |
| S-6 | Isolate brake thruster (electro-hydraulic) supply |
| S-7 | Post "CRANE IN MAINTENANCE — NOT TO BE USED FOR LIFTING — COMPETENT PERSON INSPECTION" on all crane panels and the hook block |
| S-8 | Notify melt shop supervisor and safety officer: crane out of service, estimated duration |

**PPE Minimum:** Safety helmet, steel-toe boots, full-body harness with fall-arrest lanyard (work at height on crane structure), cut-resistant gloves, safety glasses. For any work above 1.8 m: mandatory fall protection.

---

## 3. DISCARD CRITERIA — WHEN THIS SOP IS TRIGGERED (ISO 4309:2017)

This SOP is triggered immediately when **any one** of the following criteria is met:

| Criterion | Discard Threshold | Measurement | Spine Reference |
|-----------|------------------|-------------|-----------------|
| Broken wires per lay length | ≥ 12 random broken wires in any one rope lay length, OR ≥ 4 in any one strand | Visual inspection + wire count | SCN-047 |
| Loss of metallic area (LMA) | > 15–20 % in any rope section (MFL alarm 300 mV ≈ > 15–20 % LMA) | MFL instrument (MRT) | SCN-047: 320 mV |
| Rope diameter reduction | ≥ 7 % reduction from nominal diameter | Vernier caliper, multiple positions | Warning at -3 % |
| Core protrusion ("birdcaging") | Any occurrence | Visual | Immediate discard |
| Kink, crush, or sharply bent section | Any occurrence | Visual | Immediate discard |
| Corrosion — severe pitting | Visible pitting reducing outer wire cross-section by > 25 % [unverified] | Visual | Immediate discard |

> **ISO 4309:2017 Note:** MFL signal (MV) and LMA percentage are NOT the same metric and must not be conflated. Warning at 150 mV ≈ 8–12 % LMA (advisory); alarm at 300 mV ≈ > 15–20 % LMA. Rope-diameter reduction (-7 %) is an independent discard criterion.

---

## 4. TOOLS AND EQUIPMENT

| Item | Specification |
|------|--------------|
| MRT instrument (Magnetic Rope Tester) | Waygate Technologies MRT or equivalent — for LMA detection |
| Vernier caliper | For rope diameter measurement |
| Magnifying glass (×10) | Wire counting in lay length |
| Rope-pull reel / capstan | For controlled rope installation from reel |
| Wedge socket press | For dead-end rope termination |
| Fleet-angle measurement tool | Confirm < 4° from drum centreline |
| Crane reeving diagram | From Konecranes documentation — mandatory reference during reeving |
| Dynamometer / load cell | For brake static load test at rated SWL |
| Timer | Brake hold-time measurement |
| Feeler gauge | Brake air-gap measurement |
| Torque wrench (calibrated) | Brake spring pre-load verification |
| Brake pad thickness gauge | Direct measurement of pad material remaining |

---

## 5. SPARES REQUIRED

| Part ID | Description | Stock Qty | Lead Time |
|---------|-------------|-----------|-----------|
| ROPE-CRN-01 | Wire rope (custom length/spec per Konecranes drawing) | 1 on shelf | 6 weeks if OOS |
| SOCK-WEDGE-01 | Wedge socket (rope termination) | 4 on shelf | In stock |
| BRAKE-PAD-01 | Crane brake pads (shoe/disc) | 4 on shelf | 4 weeks if OOS |
| BRAKE-THR-01 | Brake thruster (electro-hydraulic) | 1 on shelf | 8 weeks if OOS |

> **ROPE-CRN-01 is a custom-length, custom-specification wire rope. Lead time 6 weeks if OOS. Keep at least one full rope set in stock at all times — rope failure without a spare is a 6-week crane outage.**

---

## 6. NUMBERED PROCEDURE STEPS

### PART A — Wire Rope Inspection and Replacement

**Pre-work Inspection (Competent Person)**
1. Competent Person (CP) conducts full rope inspection per ISO 4309:2017:
   - Run rope through the full travel range (hook block to maximum height and back) while watching for any corrosion, bulging, core protrusion, or kinking.
   - Count broken wires in the most-visible lay lengths. Use magnifying glass.
   - Measure rope OD at 3 points along rope length (head pulley, mid-rope, end near hook). Compare to nominal diameter and calculate % reduction.
   - Review latest MFL report (JSR.MS.CRN01.ROPE.MFL trending).
2. If any discard criterion is met: take crane out of service immediately per S-1 to S-8. Do not lift any load.
3. If no criterion met: document inspection findings in crane maintenance register. Set next inspection date (quarterly minimum for melt-shop ladle crane service). [unverified]

**Rope Replacement**
4. Apply LOTO per Section 2. Lower hook block to ground on blocking.
5. Remove dead-end rope anchor from the drum or equaliser. If wedge socket: drive out wedge to release.
6. Unspool old rope from drum onto a rope reel using rope capstan. Control the unspooling — do not allow rope to pile on the floor (entanglement hazard).
7. Inspect drum grooves:
    - Measure groove depth with a profile gauge. If groove depth has worn > 3 mm below original profile: drum must be replaced or grooves re-machined. [unverified — confirm with Konecranes]
    - Inspect for corrosion pitting on drum surface.
8. Inspect all sheave grooves: measure groove diameter (D-shape wear indicates rope wear). If groove diameter has increased by > 0.5 mm oversize from nominal: replace sheave. [unverified]
9. Position new rope reel at the access end of the crane bridge.
10. Reeve new rope through all sheaves per Konecranes reeving diagram for MS.LDC.CRN01. **Reeving diagram is mandatory — incorrect reeving causes cross-loading and accelerated rope wear.** Mark rope at the dead end for correct fleet angle reference.
11. Make dead-end termination using wedge socket (SOCK-WEDGE-01):
    - Thread rope through socket body.
    - Form rope eye; install wedge.
    - Pull rope end to seat wedge (do not hammer wedge — tension seats it correctly).
    - Check that rope does not have twist before final tensioning.
    - **Never use rope clips as a permanent dead-end on a ladle crane** — wedge socket is the only acceptable dead-end per FEM 1.001. [unverified]
12. Tension rope: run hook block up and down 3–5 complete cycles with light test load to seat rope in drum and sheave grooves.
13. Measure fleet angle at the drum (angle between rope entering drum groove and centreline of drum perpendicular). **Must be < 4° on each side.** > 4° = accelerated rope wear and drum edge damage. [unverified — confirm with Konecranes drum design]

**Post-Rope-Change CP Certification**
14. Competent Person re-inspects complete reeving, all sheave grooves, dead-end termination, and fleet angles.
15. CP issues maintenance certificate authorising rope replacement as complete. File certificate in crane maintenance register.

---

### PART B — Brake Service (Pad Replacement and Functional Test)

16. Apply LOTO per Section 2. Isolate brake thruster (BRAKE-THR-01) supply.
17. Access brake housing (refer to Konecranes service manual for brake access procedure on this model).
18. Measure brake pad thickness (BRAKE-PAD-01). **Replace if remaining pad thickness < 10 mm** (new pad typically 20 mm; 50% wear threshold). [unverified]
19. Remove old brake pads. Inspect brake drum/disc:
    - Measure drum/disc for out-of-roundness. If > 0.1 mm: resurface or replace drum/disc. [unverified]
    - Inspect for heat cracks. Any radial crack = replace drum.
20. Fit new brake pads of correct friction material and rated torque capacity (pads must meet or exceed OEM brake torque specification for 320 T ladle crane).
21. Set brake air gap to OEM specification. **Typical 0.5–1.0 mm for electromagnetic thrusters.** Measure with feeler gauge. [unverified — confirm with Konecranes specification]
22. Verify brake spring pre-load per OEM specification (spring pre-load determines brake holding torque — under-pre-loaded spring = insufficient braking = load drift under gravity).
23. Reconnect brake thruster supply.

**Brake Functional Test (mandatory before return to service)**
24. Remove LOTO from crane drive (not thruster — thruster already reconnected). Position CP at the test location.
25. **Static brake test:** Lift a test load equal to rated SWL (320 T for MS.LDC.CRN01) using auxiliary rigging. Stop hoist. Apply brake. Hold for 5 minutes. Load must not drift or descend. [unverified — confirm with Konecranes test procedure]
26. **Dynamic test:** Lift rated SWL to 0.5 m height. Stop hoist drive. Brake must stop descent within OEM-specified stopping distance. No uncontrolled drift.
27. Record test results in crane maintenance register. CP signs the test record.
28. If brake fails static or dynamic test: do NOT return crane to service. Re-adjust brake spring pre-load or replace BRAKE-THR-01. Repeat test.

---

### PART C — Hoist Gearbox (GMF Alarm Response)

29. On JSR.MS.CRN01.GBX.VIB.GMF alarm (> 1.0 g warning, > 2.5 g alarm): take crane out of service.
30. Apply full LOTO per Section 2.
31. Take oil sample from hoist gearbox sump. Send for ferrographic analysis.
32. Inspect magnetic drain plug.
33. If ferrography shows tooth-fragment spall: full gearbox overhaul required (see SOP-02 adapted for crane hoist gearbox). Konecranes OEM involvement recommended for major gearbox work on ladle crane.
34. If ferrography shows only fine wear particles: oil service (flush + filter + new oil) per SOP-02 Option A.
35. Hoist gearbox GMF vibration must return to < 0.5 g (normal range: 0–0.5 g) post-service before crane returns to molten-metal duty.

---

## 7. ACCEPTANCE CHECKS

| Parameter | Acceptance Criterion | Instrument |
|-----------|---------------------|------------|
| Rope broken wires (per lay length) | < 12 random broken wires (< 4 in any one strand) | Visual count + magnifier |
| MFL signal (rope LMA) | < 150 mV (normal range: 0–100 mV) | MRT instrument |
| Rope OD reduction | < 3 % from nominal | Vernier caliper |
| Fleet angle (drum) | < 4° | Fleet angle gauge |
| Dead-end termination | Wedge socket — rope seated, no twist | Visual + CP inspection |
| Brake static hold (rated SWL, 5 min) | Zero drift | Load cell + stopwatch |
| Brake pad thickness | > 10 mm remaining | Direct measurement |
| JSR.MS.CRN01.GBX.VIB.GMF | < 0.5 g (normal range) | Vibration analyser |
| JSR.MS.CRN01.BRAKE.TEMP | < 90 °C (normal range: 25–90 °C) | IR thermometer |
| JSR.MS.CRN01.LOAD.SWL | Alarm at 95 % SWL — confirmed functional | Load test |
| Competent Person certificate | Signed and filed before return to molten-metal service | Paper record |

---

## 8. TIME ESTIMATE

| Scenario | Planned TTR | Unplanned TTR |
|----------|-------------|---------------|
| Rope inspection only (no replacement) | 2 h | Same |
| Wire rope replacement (SCN-047 basis) | — | 24 h |
| Brake service (pad reline + test) | 2–6 h | 4 h |
| Rope + brake service (combined) | — | 24 h |
| Hoist gearbox oil service | 4–6 h | Same |
| Hoist gearbox gear replacement | 3–7 days | Same |

*(SCN-047 spine: unplanned downtime 24 h; cost potential USD 1 000 000–20 000 000 for ladle-drop event — Qinghe 2007 benchmark)*

---

## 9. RECURRENCE PREVENTION

- **MRT programme:** Quarterly magnetic rope inspection (MRT) for all cranes in melt-shop and caster service. High-temperature, corrosive environment (melt-shop atmosphere) accelerates rope degradation significantly compared to standard warehouse crane service.
- **Rope lubrication:** Apply wire-rope lubricant on 3-month cycle minimum (melt-shop/hostile environment). Dry rope has 30–50 % shorter fatigue life than properly lubricated rope. [unverified]
- **Brake inspection:** Monthly visual check of brake pad thickness on all duty ladle cranes. Add to operator pre-shift checklist.
- **Reeving design review:** Confirm drum-to-rope-diameter ratio (D/d) is ≥ 25 for ladle crane service (molten-metal fatigue life requirement). Small D/d ratios (< 12) dramatically accelerate rope fatigue. [unverified — confirm with Konecranes]
- **Operator training:** Crane operators must report any unusual sounds (clicking, grinding from drum/sheaves), any visible rope deformation, or any brake drift immediately. In a melt-shop context, operator reporting is the earliest detection system — sensors only provide intermittent MRT data.
- **Never bypass load limiter or safety interlocks** under any operational pressure. Bypasses on ladle cranes are Category 4 (permanently refused per site safety policy).
