# SOP-09 — Conveyor Idler Replacement and Belt Maintenance
## TATA_JSR Maintenance Standard Operating Procedure

**Document ID:** SOP-09  
**Revision:** 1.0  
**Effective Date:** 2026-06-09  
**Equipment Class:** raw_material_conveyor  
**Primary Asset Reference:** RM.CONV.ORE01  
**Trigger Failure Modes:** idler_bearing_failure | belt_misalignment | motor_overload_blocked_chute | belt_rip_tear  
**Spine Scenario Reference:** SCN-045 (RM.CONV.ORE01 — idler_bearing_failure; ultrasound 16 dBuV, idler temp 100 °C)  
**Standard:** CEMA Belt Conveyor for Bulk Materials (6th ed.) | NEMA MG1 / IEC 60947-4 (motor protection) | Fenner Dunlop belt specifications  
**Safety Class:** P1 (fire risk from seized idler)  
**Disclaimer:** SYNTHETIC procedure grounded in research/machinery/10, /16, /18, /19. Values tagged [unverified] are industry estimates. RM.CONV.ORE01 is a 1 600 mm belt EP630 conveyor (TRF / Fenner Dunlop). Refer to OEM conveyor design document for exact belt tension, idler spacing, and splice specifications.

---

## 1. SCOPE

This SOP covers:
1. **Idler Replacement** — the most frequent maintenance task on RM.CONV.ORE01. A seized idler under a loaded ore belt is the primary belt fire initiator — treat as P1 safety response.
2. **Belt Misalignment Correction** — triggered by belt edge tracking deviation exceeding limits.
3. **Emergency Belt Repair** — cold-bond repair of cuts and punctures, and vulcanised splice repair.
4. **Belt Rip Response** — triggered by rip-detector loop current alarm.

---

## 2. SAFETY / LOTO

> **CONVEYOR SYSTEMS ARE HIGH STORED-ENERGY.** Belt tension means the belt can move unexpectedly even with the drive stopped. A loaded, tensioned belt can injure a person who enters an unguarded zone without physical tension locks.

| Step | Action |
|------|--------|
| S-1 | Stop conveyor at main drive control panel. Confirm motor current = 0 (JSR.RM.CONV1.MTR.CURR = 0) |
| S-2 | Apply personal lock + danger tag to main drive MCC isolator |
| S-3 | For long conveyor: also lock out take-up drive (gravity take-up or tensioning winch) |
| S-4 | Install **physical belt-tension locks / belt clamps** at the work zone (upstream and downstream) before entering any guarded zone. Belt clamps prevent belt run-on under gravity. This step is mandatory — do NOT skip |
| S-5 | Verify motor shaft is at rest (zero speed) before entering any guarded zone |
| S-6 | Post "CONVEYOR IN MAINTENANCE — DO NOT START" on all start buttons and HMI |
| S-7 | For blocked-chute scenario: confirm material above blockage is stable before any clearing activity — chute blockage clearing can cause sudden material avalanche |
| S-8 | For hot idler event: apply fire watch immediately on hot-idler side before proceeding with stop. Have fire extinguisher (CO₂) at hand |

**PPE Minimum:** Safety helmet, steel-toe boots, cut-resistant gloves, safety glasses, high-visibility vest. For hot-idler response: add face shield. For fire response: fire-resistant clothing, respiratory protection.

---

## 3. TRIGGER CONDITIONS

| Sensor Tag | Threshold | Action |
|-----------|-----------|--------|
| JSR.RM.CONV1.IDLER.US | > 8 dBuV (warning — above baseline) | **Stop belt. Identify hot idler on next idler patrol** |
| JSR.RM.CONV1.IDLER.US | > 15 dBuV (alarm — SCN-045: 16 dBuV) | **Stop belt immediately (fire risk).** Emergency idler change |
| JSR.RM.CONV1.IDLER.TEMP | > 80 °C (warning) | Stop belt; emergency idler replacement |
| JSR.RM.CONV1.IDLER.TEMP | > 100 °C (alarm — SCN-045: 100 °C = fire threshold) | **Emergency stop.** Fire watch activated |
| JSR.RM.CONV1.BELT.EDGE | > 25 mm offset (warning) | Investigate idler alignment; correct within one shift |
| JSR.RM.CONV1.BELT.EDGE | > 50 mm offset (alarm) | **Stop belt** — edge damage or belt-off-structure risk |
| JSR.RM.CONV1.MTR.CURR | > 105 % FLA (warning) | Investigate belt loading and chute blockage |
| JSR.RM.CONV1.MTR.CURR | > 125 % FLA (alarm) | Stop belt; clear blockage before restart |
| JSR.RM.CONV1.RIP.LOOP | < 48 mA (warning) | Investigate belt surface for longitudinal rip |
| JSR.RM.CONV1.RIP.LOOP | = 0 mA (alarm — open circuit = tear) | **Emergency stop.** Belt rip confirmed |
| Operator patrol: idler not rotating | Any | Stop belt; change idler before restart — seized idler = fire risk |
| Operator patrol: idler surface temperature (IR gun) | > 65 °C | Stop belt; change idler |

---

## 4. TOOLS AND EQUIPMENT

| Item | Specification |
|------|--------------|
| IR thermometer | Portable; measure idler shell temperature on patrol |
| Belt lifter / pry bar | To lift belt at idler position (never put hands under loaded belt) |
| Ultrasound detector (SDT 270) | Walk-down patrol on idler bearings |
| Vulcanising press | For hot splice repair (portable — 145 °C, 20–30 min) [unverified] |
| Belt clamps (minimum 2 sets) | Physical tension locks for work zone |
| Splicing tools (knife, ply separator) | Belt preparation for vulcanised splice |
| Cold-bond repair kit (3M / Fenner Dunlop) | Temporary puncture/cut repair |
| Training idler adjustment tools | Spanner and hex keys for training idler pivot adjustment |
| CO₂ fire extinguisher (minimum 2) | Fire watch for hot idler response |
| Torch/inspection light | Belt surface inspection in low-light areas |

---

## 5. SPARES REQUIRED

| Part ID | Description | Stock Qty | Lead Time |
|---------|-------------|-----------|-----------|
| IDLER-STD-1600 | Standard carrying idler, 1600 mm belt | 40 on shelf | In stock |
| IDLER-TRAIN-01 | Training / self-aligning idler | 6 on shelf | 4 weeks if OOS |
| BELT-SEC-1600 | Belt section EP630 1600 mm (made-to-order) | 0 on shelf | 10 weeks |
| VULC-KIT-01 | Belt vulcanising kit | 2 on shelf | In stock |

> **BELT-SEC-1600 is zero-stock with 10-week lead. If a rip requires a new belt section, the conveyor may be down for 10 weeks if no belt on site. Maintain at least one on-site emergency section (10–15 m minimum for standard splice repairs). Raise procurement recommendation.**

---

## 6. NUMBERED PROCEDURE STEPS

### OPTION A — Idler Replacement (most common; 15–30 min per idler)

**Emergency Hot Idler Response**
1. On idler temperature alarm (> 100 °C) or ultrasound alarm (> 15 dBuV): stop belt immediately. Set up fire watch with CO₂ extinguisher at the hot idler location. Do NOT wait — a seized idler under a rubber ore belt is a fire initiator.
2. Scan adjacent idlers with IR thermometer — confirm hot idler is isolated case or whether multiple idlers in a section are hot (indicates systematic lubrication failure).
3. Apply LOTO per Section 2. Install belt clamps at the work zone.

**Idler Change**
4. Approach hot idler location. Verify idler shell temperature is below 200 °C before handling with heat-resistant gloves (allow cooling with water spray if needed, but do NOT spray water directly onto a hot bearing — rapid cooling can crack the bearing housing). [unverified]
5. Use belt lifter or pry bar to lift belt at the idler location. **Never put hands or feet under the loaded belt — belt weight can be several tonnes per metre of length.**
6. Remove old idler from carrying frame (most idlers are snap-in or pin-retained — check frame attachment design before starting).
7. Verify replacement idler (IDLER-STD-1600) is correct specification:
    - Belt width: 1600 mm (confirmed)
    - Trough angle: matches existing idler set (typically 35° or 45° — check existing frame angle)
    - Load rating: meets conveyor design specification
    - **Confirm new idler rotates freely by hand before fitting**
8. Fit new idler into carrying frame. Confirm it is properly seated and retained.
9. Lower belt. Confirm idler is under belt.
10. Remove belt clamps. Remove LOTO. Restart belt.
11. Walk the belt for at least one complete circuit after restart — confirm new idler is rotating and not binding.
12. Record replacement in CMMS: idler location (carry side, return side), position from head/tail, idler type (IDLER-STD-1600 or IDLER-TRAIN-01), failure mode of removed idler (seized bearing, failed shell, damaged housing).

---

### OPTION B — Belt Misalignment Correction

13. Stop belt. Apply LOTO. Install belt clamps.
14. Identify misalignment zone by walking the full belt length with belt running (walk from safe side — never walk alongside the edge of a misaligned belt; it can clip a person).
15. Identify root cause of misalignment:
    - **Incorrect idler alignment** (most common): set of idlers at the mistrack zone are not perpendicular to belt travel direction. Adjust by rotating individual idler station (offset angle adjustment) to steer belt.
    - **Belt splice splice off-square**: a splice not cut square to the belt will cause cyclic tracking error every time the splice passes a given point. Rework splice.
    - **Damaged idler causing belt wander**: replace idler per Option A.
    - **Loading zone off-centre**: material loading on one side creates tracking forces. Check chute alignment.
16. Adjust training idler (IDLER-TRAIN-01) at the mistrack zone: rotate the steering idler in the steering direction (toe-in on the side the belt is wandering away from). Make small adjustments (5–10° per step) and observe effect over one belt circuit before making another adjustment. [unverified]
17. After correction: run belt through 5 complete circuits under normal loading. Verify JSR.RM.CONV1.BELT.EDGE is within ±15 mm (normal range).

---

### OPTION C — Belt Repair (Cut / Puncture — Cold Bond Repair)

18. Stop belt. Apply LOTO. Install clamps.
19. Clean damaged area: cut away fraying rubber to clean, stable edges. Minimum 50 mm around damage in all directions. [unverified]
20. Bevel belt carcass edges around cut (45° bevel for cold bond) — allows adhesive to penetrate to belt ply.
21. Roughen surfaces with 36-grit sanding disk.
22. Apply cold-bond adhesive (VULC-KIT-01 compatible primer + adhesive per manufacturer's procedure).
23. Cut patch from repair material to overlap damage by 50 mm in all directions.
24. Apply adhesive to patch and to belt surface. Allow to tack (per manufacturer — typically 5–10 min). Press patch firmly; roll with hand roller.
25. Allow cure: minimum 8 h at ambient temperature (accelerate to 3 h with portable heat lamp). [unverified]
26. Cold repair is **temporary** — suitable for small cuts (< 50 mm length). Plan vulcanised repair at next maintenance window.

---

### OPTION D — Vulcanised Splice Repair (3–8 h including cure)

27. Stop belt. Apply LOTO. **Use belt clamps AND take-up lock — this repair requires belt tension to be fully released in the work zone.**
28. Mark splice position. Cut out damaged section or prepare for new end-to-end splice.
29. Prepare joint faces per VULC-KIT-01 specification:
    - Cut square across belt (use straight edge and belt knife — a crooked cut causes tracking problems)
    - Bevel carcass to taper over 150–300 mm step length
    - Roughen surfaces with belt grinder
    - Apply skim coat of adhesive to both faces and allow to tack
30. Lay new ply strips (from belt vulcanising kit) to rebuild carcass. Cover with rubber compound.
31. Apply portable vulcanising press. Set temperature to 145 °C (for standard EP630 belt rubber). Time: 20–30 min for standard thickness. [unverified — confirm against VULC-KIT-01 time/temperature curve]
32. Allow joint to cool in press before removing (prevent delamination under thermal stress). Trim excess rubber.
33. Re-tension belt per design specification.
34. Run belt one circuit without load; inspect splice for delamination or opening. Run under full load for 30 min; re-inspect.

---

### Blocked Chute Response (motor overload — JSR.RM.CONV1.MTR.CURR > 125 % FLA)

35. Stop belt. Apply LOTO. **DO NOT enter chute structure until blockage stability is confirmed** — a bridged blockage can suddenly release when disturbed, causing a material avalanche.
36. Inspect chute from safe position (not directly below blockage). Use a long tool (air lance, rod) to probe blockage from the side.
37. Use compressed air lance or controlled mechanical break-out to clear blockage. Station a crew member as safety observer.
38. After clearing: inspect belt surface and chute impact plates for damage. Replace damaged chute liners.
39. Check belt tracking at loading zone before restart.
40. Restart belt; monitor current for first 5 minutes (should return to 60–95 % FLA normal range).

---

## 7. ACCEPTANCE CHECKS

| Parameter | Acceptance Criterion | Instrument |
|-----------|---------------------|------------|
| Idler rotation (after replacement) | Freely rotating, no noise | Physical hand-spin check + operator walk-down first circuit |
| Idler temperature (30 min after restart) | < 60 °C (normal range: 25–60 °C) | JSR.RM.CONV1.IDLER.TEMP / IR thermometer |
| Belt edge position (after misalignment repair) | ± 15 mm (normal range) | JSR.RM.CONV1.BELT.EDGE |
| Drive motor current (at rated load) | 60–95 % FLA (normal range) | JSR.RM.CONV1.MTR.CURR |
| Rip detector | 60–80 mA (normal range) | JSR.RM.CONV1.RIP.LOOP |
| Splice integrity (30 min loaded run) | No delamination or opening at splice | Visual inspection |
| Ultrasound level (after idler change) | -20 to -8 dBuV (normal range) | SDT 270 ultrasound detector |

---

## 8. TIME ESTIMATE

| Scenario | Planned TTR | Unplanned TTR |
|----------|-------------|---------------|
| Single idler replacement | 15–30 min | 2 h (including patrol to locate, hot idler cooling) |
| Belt misalignment correction | 1–2 h | 3 h |
| Cold-bond repair (temporary) | 1–2 h | Same |
| Vulcanised splice repair | 4–8 h (including cure) | Same |
| Belt section replacement (full section + 2 splices) | 1–3 days depending on belt length | Same |

*(SCN-045 spine: planned 0.5 h, unplanned 2 h; cost USD 7 500)*

---

## 9. RECURRENCE PREVENTION

- **Thermal monitoring:** Mount fixed IR cameras or FLIR sensors between manual patrol intervals to auto-detect hot idlers (> 65 °C) — reduce fire risk window from patrol-to-patrol hours to minutes.
- **Idler replacement programme:** Replace idlers at end of calculated service life (typically 50 000–80 000 h for good-quality idlers in moderate ore service). [unverified] Do not run to failure in fire-risk ore/coal service.
- **Loading zone maintenance:** Maintain rubber impact bars and skirt boards at loading zones. Exposed metal at loading points is the primary cause of belt cuts and longitudinal tears. Inspect and replace impact bars every 3 months.
- **Belt tracking:** Quarterly alignment check of all idler sets. Misaligned idlers cause both edge wear and belt wander.
- **Rip detector test:** Test JSR.RM.CONV1.RIP.LOOP (Fenner RipScan) signal continuity monthly — the detector loop is the primary protection against a catastrophic belt rip event. A silent rip detector is no protection.
- **BELT-SEC-1600 stock:** Maintain at minimum 1 × 10 m section on-site — current zero stock is a risk for a prolonged outage on belt rip events.
