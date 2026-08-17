# SOP-08 — Hot Strip Mill Work Roll Change (Spall / Scheduled)
## TATA_JSR Maintenance Standard Operating Procedure

**Document ID:** SOP-08  
**Revision:** 1.0  
**Effective Date:** 2026-06-09  
**Equipment Class:** hot_strip_mill_stand  
**Primary Asset Reference:** HSM.STD.R1  
**Trigger Failure Modes:** work_roll_spall_flat | roll_wear_thermal_camber_loss | roll_chatter_5th_octave | roll_surface_fatigue_crack  
**Spine Scenario Reference:** SCN-044 (HSM.STD.R1 — work_roll_spall_flat; force ripple 8.5 %, chock vib 6.0 mm/s)  
**Standard:** AISE Technical Report No. 11 (Roll Technology) | ISO 21940-11 (rotor/roll balancing) | ISO 15243:2017 (bearing)  
**Safety Class:** P2  
**Disclaimer:** SYNTHETIC procedure grounded in research/machinery/08, /15, /18, /19. Values tagged [unverified] are industry estimates. HSM.STD.R1 is a Primetals 4-high reversing roughing stand. Refer to Primetals/OEM roll-change procedure for specific sequence on this stand design.

---

## 1. SCOPE

This SOP covers:
- **Unscheduled (emergency) work roll change** triggered by spall detection (force ripple alarm + strip surface marking, SCN-044).
- **Scheduled (campaign) work roll change** triggered by tonnage/pass count or surface condition criterion.
- Roll shop inspection, grinding, and disposition of removed rolls.

**Back-up roll change** is a major plant shutdown event outside this SOP scope — refer to OEM back-up roll change procedure (Primetals). TTR for BUR change: 8–24 h minimum with 120–200 T crane.

---

## 2. SAFETY / LOTO

| Step | Action |
|------|--------|
| S-1 | Stop rolling. Retract rolls to maximum gap (full open on AGC screwdown) |
| S-2 | Trip main drive (HSM.F1.MTR01) and confirm drives are at zero speed |
| S-3 | LOTO main drive at MCC (HV LOTO with AEP for MV motor) |
| S-4 | **Verify backup roll cooling water is still FLOWING** — do not close cooling water during a roll change (preventing thermal gradient stress in hot BURs during stop). Cooling is only stopped after BURs have cooled to ambient for scheduled BUR changes |
| S-5 | Isolate roll balance hydraulic system. Apply safety lock on screwdown to prevent inadvertent roll gap closure during roll change |
| S-6 | LOTO roll-change car hydraulic power unit (separate isolation from mill main hydraulics) |
| S-7 | Post "ROLL CHANGE IN PROGRESS — DO NOT START MILL" on all mill HMI stations |
| S-8 | Confirm roll-change car/side-shift mechanism is at safe-stow position before allowing personnel into the roll gap |

**PPE Minimum:** Safety helmet, steel-toe boots, heat-resistant gloves (rolls may be at operating temperature during emergency change), safety glasses, hearing protection. For emergency spall events: add face shield (spall fragments possible on inspection).

---

## 3. TRIGGER CONDITIONS

| Sensor Tag | Threshold | Action |
|-----------|-----------|--------|
| JSR.HR.R1.FORCE (force ripple %) | > 4 % (warning) | Fourier analysis of force signal; check strip surface for periodic marking |
| JSR.HR.R1.FORCE (force ripple %) | > 8 % (alarm — SCN-044: 8.5 %) | **Stop rolling.** Emergency roll change |
| JSR.HR.R1.WR.VIB.CHOCK | > 4.0 mm/s (warning) | Increase monitoring; check for surface marks on strip |
| JSR.HR.R1.WR.VIB.CHOCK | > 10.0 mm/s (alarm — SCN-044: 6.0 mm/s at failure stage) | Stop rolling |
| JSR.HR.R1.CROWN.DEV | > 25 µm (warning) | Roll wear or thermal crown developing |
| JSR.HR.R1.CROWN.DEV | > 40 µm (alarm) | Plan roll change |
| JSR.HR.R1.WR.AE.RMS | > 8 dB (warning) | Investigate sub-surface roll condition |
| Strip surface inspection system | Periodic defect at pitch = π × D (roll circumference) | Confirms spall on work roll of identified roll diameter |
| Roll shop inspection | Sub-surface cracks found by ultrasonic tester | Do not return roll to service until crack removed by grinding |
| Campaign tonnage counter | Per scheduled tonnage trigger (e.g. every 500 t/stand) [unverified] | Scheduled roll change |

---

## 4. TOOLS AND EQUIPMENT

| Item | Specification |
|------|--------------|
| Roll-change car (hydraulic) | Plant-installed; rated for work roll weight (roughing stand WR: 15–40 T) [unverified] |
| Overhead crane (roll shop and mill bay) | Full roll weight capacity |
| CNC roll grinder (roll shop) | Waldrich Coburg / Herkules or equivalent — profile capability |
| Roll profile gauge | Contact or optical; resolution 0.001 mm [unverified] |
| Ultrasonic roll tester | Stresstech or equivalent — automated UT scan |
| Roll inspection light | Directional light at 10–15° incidence for surface crack detection |
| Chock press | For removing and fitting bearings to roll chock |
| Torque wrench | Chock clamp bolts |
| Magnifying glass (×10) | Surface inspection of removed roll |
| Dial indicator | Roll runout check post-change |

---

## 5. SPARES REQUIRED

| Part ID | Description | Stock Qty | Lead Time |
|---------|-------------|-----------|-----------|
| WR-HSS-PREP | Prepared work roll pair HSS (from roll shop) | 4 pairs on shelf | In stock (roll shop prepares continuously) |
| CHOCK-SEAL-01 | Roll chock seals | 4 on shelf | 6 weeks if OOS |

> **WR-HSS-PREP:** HSS (High Speed Steel) rolls have 3–5× wear resistance vs high-chrome iron for hot-strip finishing stands. Prepared rolls in roll shop inventory are the key to keeping emergency roll change TTR at 15–45 min. Never run roll-shop inventory to zero — minimum 2 prepared pairs at all times.

> **New work roll procurement from supplier (if roll shop stock exhausted):** 12–26 weeks — this is a campaign-planning risk.

---

## 6. NUMBERED PROCEDURE STEPS

### Phase A — Detection and Decision to Change Roll

1. On force-ripple alarm or strip surface inspection alarm: confirm defect period = π × roll diameter. Calculate which specific roll (WR, BUR, or DR roll) is the source. Record calculation in CMMS event log.
2. If product currently in mill: **stop rolling immediately** — affected strip must be segregated. Notify quality team with defect location (coil number, approximate position).
3. Segregate affected strip from production grade — tag as suspect quality.
4. Apply LOTO per Section 2.
5. Visually inspect work roll surface from accessible position (side of stand, through roll gap) with inspection light at 10–15° incidence angle. Confirm spall location visually.

### Phase B — Work Roll Removal

6. Retract rolls to maximum gap (screwdown fully open). Lock screwdown with safety lock.
7. Remove chock clamps — record clamp positions for reinstallation reference.
8. Deploy roll-change car to the work roll side.
9. Slide work rolls (upper and lower WR as paired set) out of the stand onto the roll-change car.
10. Transport rolls on roll-change car to roll storage track.
11. Transfer to roll shop via overhead crane or roll track.
12. Tag removed rolls with: heat/coil number at time of change, failure description (spall, scheduled, surface mark), CMMS work order number.

### Phase C — New Work Roll Installation

13. Confirm prepared roll pair (WR-HSS-PREP) is available. Verify roll pair was inspected in roll shop before this change (profile measurement + UT scan on record).
14. Verify crown profile of prepared rolls matches the rolling schedule specification for the next coils to be rolled. Different profiles are required for different strip widths and grades — this is the metallurgist's/rolling engineer's sign-off.
15. Inspect new roll chock seals (CHOCK-SEAL-01) — replace any seal showing cuts, cracking, or hardening. A leaked seal means water ingress into the chock bearing.
16. Load prepared work rolls into stand using roll-change car.
17. Engage chock clamps. Torque to OEM specification.
18. Confirm roll gap and parallelism using screwdown reference position display. For AGC-equipped stands: zero-position calibration of roll gap after roll change is mandatory (new roll diameter differs from removed roll diameter after grinding).
19. Re-enable cooling water flow to work rolls. Confirm nozzle spray pattern is correct (visual from side of stand).
20. Re-engage main drives and coupling systems.

### Phase D — Return to Production

21. Remove all LOTO in reverse sequence. For HV motor LOTO: AEP re-energises last.
22. Roll 1–2 test pieces (pre-production verification coils — not prime product). Monitor:
    - Strip gauge profile (JSR.HR.R1.CROWN.DEV must be within ±10 µm)
    - Force ripple (JSR.HR.R1.FORCE must be < 2 % steady-state)
    - Strip surface inspection system: zero defect pattern for first 10 minutes
23. If test pieces pass: resume normal production with enhanced monitoring for first 15 minutes.
24. Record all sensor baselines (force, vibration, AE) post roll change in CMMS as new roll-campaign baseline.

### Phase E — Roll Shop Disposition (removed roll)

25. Place removed roll on CNC roll grinder.
26. Measure roll profile and spall geometry with roll profile gauge. Record spall depth, area, and position.
27. Grind to remove spall plus minimum safe margin (**typically 3–5 mm below spall depth for work rolls**). [unverified]
28. If after grinding, remaining roll diameter is still above minimum diameter (per roll schedule): proceed to ultrasonic inspection.
29. **Ultrasonic test:** automated UT scan on roll surface and sub-surface. Any crack indication remaining = grind deeper or condemn. Do not return a roll to service with known sub-surface cracks.
30. If above minimum diameter and UT clear: achieve surface roughness target for next use (hot mill WR: Ra 0.8–2.0 µm; achieve correct crown profile per programme). Log roll data in roll management system (diameter, stock used, pass/fail). Store as prepared spare.
31. If below minimum diameter: condemn roll. Tag "CONDEMNED — DO NOT USE." Dispose per plant scrap procedure.

---

## 7. ACCEPTANCE CHECKS

| Parameter | Acceptance Criterion | Instrument |
|-----------|---------------------|------------|
| Force ripple (post-change) | < 2 % (normal range: 0–2 %) | JSR.HR.R1.FORCE |
| Chock vibration | < 1.0 mm/s (normal range: 0–1.0 mm/s) | JSR.HR.R1.WR.VIB.CHOCK |
| Crown deviation | ± 10 µm (normal range: -10 to +10 µm) | JSR.HR.R1.CROWN.DEV |
| AE.RMS | < 3 dB (normal range: -3 to +3 dB) | JSR.HR.R1.WR.AE.RMS |
| Strip surface inspection (first 10 min) | No periodic defect detected | Surface inspection system |
| Roll gauge profile (test coils) | Within schedule specification | Gauge meter |
| Roll cooling nozzle spray | Correct fan-spray pattern, no blocked nozzles | Visual check |

---

## 8. TIME ESTIMATE

| Scenario | Planned TTR | Unplanned TTR |
|----------|-------------|---------------|
| Work roll change (quick-change HSM roughing stand) | 15–45 min | 4 h |
| Roll shop grind (minor surface) | 2–4 h | Same |
| Roll shop grind + UT inspection | 4–6 h | Same |
| Back-up roll change (not this SOP) | — | 8–24 h |

*(SCN-044 spine: planned 0.75 h, unplanned 4 h; cost USD 184 000 unplanned vs USD 11 200 planned)*

---

## 9. RECURRENCE PREVENTION

- **After every cobble event:** Inspect work roll surfaces before resuming production. Cobble-induced thermal shock is the primary spall initiator — a roll that looks fine visually may have activated sub-surface cracks.
- **Roll thermal management:** Maintain consistent cooling water quality and flow. High dissolved-solids water causes scale deposits on roll surfaces, reducing cooling effectiveness and accelerating thermal fatigue cracking.
- **HSS roll adoption:** Justify HSS work rolls (WR-HSS-PREP) for HSM finishing stands — 3–5× wear resistance means longer campaigns, fewer changes, and improved strip surface quality.
- **Ultrasonic roll inspection frequency:** Inspect all work rolls with automated UT tester at minimum every 2 grinding passes. Sub-surface cracks are invisible to the naked eye; only UT catches them before they propagate to a spall event.
- **Roll schedule optimisation:** Use online surface inspection data to trigger rolls changes condition-based, not purely fixed-tonnage. Early change catches surface issues before they print on strip — planned change cost (USD 11 200) is 16× cheaper than unplanned (USD 184 000).
