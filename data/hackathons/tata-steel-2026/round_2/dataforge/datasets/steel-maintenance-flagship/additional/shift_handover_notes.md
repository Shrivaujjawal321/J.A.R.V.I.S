# Shift Handover Notes — TATA_JSR (Synthetic)
# Format: 3-shift rotation (A=06:00–14:00, B=14:00–22:00, C=22:00–06:00)
# Covering ~10 days of plant activity referencing active failure/watch scenarios
# SYNTHETIC — physics-grounded; NOT real Tata Steel data
# All asset_ids, sensor tags, and thresholds match ground_truth_spine.json v1.0.0

---

## HANDOVER-001
**Date:** 2026-03-10 | **Shift:** A→B | **Outgoing:** Rakesh Sharma (HOT ROLLING & CASTING)
**Incoming:** Priya Mehta

### Watch Items
1. **HSM.F3.WR.BRG01** — AE sensor `JSR.HR.STD3.WR.BRG01.AE.RMS` hit **6.2 dBuV** at 11:40. This is just above the AE warning threshold (6 dBuV per ISA-18.2 alarm config). Envelope BPFO still at **0.3 g** (normal). Temp DE at **59 °C** (normal). Pattern consistent with *very early-stage outer-race spall initiation* (SCN-037 trajectory, Stage 1). Recommend spectrum burst capture every 2 hours. No action needed yet — but do not miss if AE climbs further.
2. **HSM.F1.GBX01** — Oil sample dispatched at 10:00 to lab. Fe count from last sample (3 days ago): **8 ppm** (above normal 0–5 ppm, below warning 15 ppm). Keep monitoring. Next lab result expected 22:00 tonight.
3. **CCM.MOLD.01** — TC delta `JSR.CC1.MOLD.TC.DELTA` had a transient spike to **23 °C** at 09:15 during grade change (1080 → 0.04C LC steel). Not sustained. Level `JSR.CC1.MOLD.LEVEL.DEV` stable at **0.8 mm**. SEN changed at 08:30 before my shift — this may be residual transition noise. Watch closely on next sequence start.
4. **RM.CONV.ORE01** — IR walkdown at 12:00 found idler at position 47 (belt section C) reading **71 °C** (warning threshold 80 °C). Ultrasound `JSR.RM.CONV1.IDLER.US` probe at that point: **+4 dBuV** above baseline (below alarm 15 dBuV). Log for trending. Do NOT let it approach 80 °C without escalating.

### Completed This Shift
- Roll change on F1 stand: new pair installed, runout verified <0.02 mm. No issues.
- Monthly PM on `JSR.RHF.Z3.FLAME.SIG` flame scanner lens cleaning — signal now at 97% (was 91%).
- BF.BLW.FAN01 shaft displacement `JSR.BF.BLW.FAN01.SHAFT.DISP` trend steady at 33 µm — no change from last 48 h.

---

## HANDOVER-002
**Date:** 2026-03-10 | **Shift:** B→C | **Outgoing:** Priya Mehta | **Incoming:** Suresh Naidu

### Watch Items
1. **HSM.F3.WR.BRG01** — AE rose to **7.4 dBuV** at 19:50 (warning exceeded, not yet at alarm 12 dBuV). Envelope BPFO now **0.45 g** (still below warning 1.0 g). Burst spectrum captured at 18:00 shows nascent BPFO peak. **Book a planned roll-change slot for next weekend window.** Spares check: `BRG-LRG-300` — 1 unit on shelf. Labyrinth seal set `SEAL-LAB-01` — 2 on shelf. Good.
2. **RHF.ZONE.SOAK** — Flame scanner `JSR.RHF.Z3.FLAME.SIG` dipped to **73%** at 17:30 (warning threshold 70%) during a gas pressure fluctuation from BFG header. Recovered to 95% within 3 min. Flue O2 `JSR.RHF.Z3.FLUE.O2` went to **4.8%** momentarily (approaching warning 5%). **No alarm fired.** Monitored and recovered. If it dips again tonight, escalate to furnace supervisor for gas supply check.
3. **HSM.F1.GBX01** — Lab result back: Fe = **12 ppm** (up from 8 ppm, approaching warning 15 ppm). GMF vib `JSR.HR.STD1.GBX01.VIB.GMF.RMS` steady at **3.1 mm/s** (normal range). Oil temp **57 °C** (normal). *Trending up*. Schedule spectrometric analysis repeat in 5 days. No shutdown warranted yet.
4. **CCM.SEG.07** — Roll RPM `JSR.CC1.SEG07.ROLL.RPM` for roller S7-R4 showing **7 rpm** (vs normal 14 rpm). Hydraulic force on that segment `JSR.CC1.SEG07.FORCE.HYD` up to **340 kN** (still within normal 200–400 kN). Early sign of bearing drag. **Recommend segment inspection at next heat break.**

### Completed This Shift
- EAF hydraulic HPU `JSR.MS.EAF1.HYD.FILT.DP` filter differential pressure: **1.4 bar** (below warning 3.0 bar). No change needed.
- Ladle crane `JSR.MS.CRN01.ROPE.MFL` weekly MFL scan completed: **68 mV** (normal range). No wire breaks visible on Competent Person visual check. Brake hold test passed.

---

## HANDOVER-003
**Date:** 2026-03-11 | **Shift:** C→A | **Outgoing:** Suresh Naidu | **Incoming:** Rakesh Sharma

### Watch Items
1. **HSM.F3.WR.BRG01** — **ESCALATED.** AE hit **9.1 dBuV** at 03:20 (stage 2 progression, between warn 6 and alarm 12 dBuV). Envelope BPFO now **0.72 g** (below warning 1.0 g but rising rapidly). I recommend accelerating the planned roll-change to *this* weekend if the slot can be confirmed. Notified shift supervisor. Playbook 01 read; LOTO procedure reviewed. All spares confirmed in store.
2. **CCM.SEG.07** — S7-R4 roll RPM down to **4 rpm** at 02:45; force `JSR.CC1.SEG07.FORCE.HYD` at **390 kN** (approaching upper normal 400 kN). Casting speed reduced 10% as precaution. End of heat is at 06:30 — plan segment withdrawal immediately after. Notify caster maintenance team NOW to have `ROLL-SEG-STD` and `BRG-SEG-01` ready in the segment bay.
3. **HSM.DSC.PMP01** — A small weep noted at gland at 04:00 inspection round. VIB `JSR.HR.DSC.PMP01.VIB.CAS.RMS` = **1.6 mm/s** (above normal 1.5 but below warning 2.5). Bearing temp **63 °C** (normal). Likely early seal face wear (SCN-040 trajectory). No immediate action — standby pump available. **Book seal cartridge change for next planned maintenance window (<2 weeks).** `SEAL-MECH-DSC` — 2 on shelf.

### Completed This Shift
- AGC servo `JSR.CR.S2.AGC.SV.POSERR` trending data pulled: 0.28% position error — fully nominal.
- Sinter fan `JSR.SP.FAN01.VIB.1X` = 2.1 mm/s, `JSR.SP.FAN01.TEMP.BRG` = 57 °C. Both normal.

---

## HANDOVER-004
**Date:** 2026-03-11 | **Shift:** A→B | **Outgoing:** Rakesh Sharma | **Incoming:** Priya Mehta

### Watch Items
1. **CCM.SEG.07 — SEGMENT CHANGE IN PROGRESS.** Heat ended at 06:35. Maintenance crew pulled segment 07 at 07:15. Roll S7-R4 confirmed seized — spalled bearing (ISO 15243 fatigue class, water-scale ingress). `ROLL-SEG-STD` and `BRG-SEG-01` replacement in progress. Estimated RTS: 14:00 today (Playbook repair sequence per SCN-042). Do NOT restart caster before segment pressure-test completion.
2. **HSM.F3.WR.BRG01** — Roll-change slot confirmed: Saturday 14-Mar 06:00 window. Production planned to accept 8 h downtime (planned 5 h + 3 h contingency). `BRG-LRG-300`, `SEAL-LAB-01`, `CPL-EL-01` all pulled from store and staged at stand. Induction heater booked. AE currently **9.8 dBuV** — continue hourly monitoring until Saturday.
3. **BF.BLW.FAN01** — Discharge pressure oscillation `JSR.BF.BLW.FAN01.PRES.OSC` had a 3-second burst at **5.2%** at 08:10 (crossed warning 5%). VIB 1X = **2.2 mm/s** (normal). Shaft displacement = **38 µm** (normal). *Single excursion — not a surge event.* Possible transient from downstream valve operation. Log in CMMS. Anti-surge valve (ASV) status confirmed: open-loop test passed. **If another excursion >5% before end of B-shift, notify BF process engineer immediately.**

### Completed This Shift
- RM.CONV.ORE01 idler 47 replaced (had reached 78 °C by 07:45, just below alarm; replaced proactively). Ultrasound now **-12 dBuV** (baseline).
- RHF furnace temperature `JSR.RHF.Z3.ZONE.TEMP` steady at 1248 °C. Flue O2 2.3%. All normal.

---

## HANDOVER-005
**Date:** 2026-03-11 | **Shift:** B→C | **Outgoing:** Priya Mehta | **Incoming:** Suresh Naidu

### Watch Items
1. **CCM.SEG.07 RTS:** Segment reinstalled at 13:40. Gap set to 225 mm per slab format, hydraulic circuit pressure-tested at 600 kN (no leak). Roll RPMs all verified rotating at 12–16 rpm under no-load. Spray nozzles flow-tested: 195 L/min (within 180–220 L/min spec). Caster restart authorised 14:15. First heat started at 15:00 — all readings nominal. **Monitor for first 2 hours closely.** Bulge `JSR.CC1.SEG07.BULGE` = 0.3 mm (normal).
2. **EAF.AUX.HYD01** — Oil ISO4406 inline reading trending: **17/15/12** (at warning threshold). Water content `JSR.MS.EAF1.HYD.WATER.PPM` = **85 ppm** (below warning 200 ppm). Filter DP `JSR.MS.EAF1.HYD.FILT.DP` = **2.1 bar** (approaching warning 3.0 bar). **Plan filter element change at next heat break.** `FLT-GBX-01` in stock.
3. **HSM.F1.MTR01** — Routine MCSA burst at 16:00. Sideband `JSR.HR.STD1.MTR01.MCSA.RBAR.SB` = **-54 dBc** (normal). Winding temp = **121 °C** (normal, below warning 145 °C). Current imbalance = **0.7%** (normal). Motor healthy — no action.

### Completed This Shift
- CRM AGC servo: ISO4406 oil sample collected and sent to lab. Position error 0.31% — normal.

---

## HANDOVER-006
**Date:** 2026-03-12 | **Shift:** A→B | **Outgoing:** Arjun Patel | **Incoming:** Lakshmi Rao

### Watch Items
1. **EAF.AUX.HYD01 — FILTER CHANGED** at 05:30 during EAF tap break. New element installed. Post-change DP `JSR.MS.EAF1.HYD.FILT.DP` = **0.3 bar** (normal). ISO4406 should improve over next 8 h as kidney-loop cycles. Check inline reading at noon.
2. **BF.CW.PMP02** — Head deviation `JSR.BF.CW.PMP02.HEAD.DEV` crept to **-5%** (between normal ±3% and warning -7%). VIB 1X = **1.7 mm/s** (normal). Bearing temp = **64 °C** (normal). *Likely early impeller wear.* Not alarming but trending. Baseline hydraulic test should be scheduled next planned outage (3–4 weeks).
3. **MS.LDC.CRN01** — Hoist gearbox vibration `JSR.MS.CRN01.GBX.VIB.GMF` = **0.62 g** (above normal 0.5 g, below warning 1.0 g). Brake temp `JSR.MS.CRN01.BRAKE.TEMP` = **84 °C** after ladle pick cycle (normal range up to 90 °C). Load SWL was 88% on the 280 t ladle pick this morning — normal operational profile. No action, trend noted.
4. **RHF.ZONE.SOAK** — Shell IR scan at 07:00 found a **152 °C** hotspot at the south wall (approaching warning 180 °C). Zone temp and flame signal nominal. This is likely a thin section in the refractory lining. **Notify Tenova service team for survey during next planned furnace cool.** Do not ignore — progression to alarm (250 °C) would indicate burn-through risk.

### Completed This Shift
- CRM AGC oil lab result: ISO4406 = **15/13/10** — normal, servo clean.
- F1 GBX01 Fe count update from lab: **14 ppm** (still approaching warning 15 ppm but no further jump in 48 h).

---

## HANDOVER-007
**Date:** 2026-03-12 | **Shift:** B→C | **Outgoing:** Lakshmi Rao | **Incoming:** Vijay Singh

### Watch Items
1. **RHF.ZONE.SOAK hotspot** — Re-scanned at 18:00: still **149 °C**. Stable, not growing. Tenova notified via email; survey tentatively scheduled for 23-Mar planned cool. Interim: increase shell scan frequency to twice per shift.
2. **HSM.F3.WR.BRG01** — AE now **10.4 dBuV** (approaching alarm 12 dBuV). BPFO envelope **0.91 g** (just below warning 1.0 g). Temp `JSR.HR.STD3.WR.BRG01.TEMP.DE` = **68 °C** (still below warning 85 °C). **If AE crosses 12 or BPFO crosses 1.0 g before Saturday, escalate to emergency roll-change and invoke Playbook 01 immediately.** Spares confirmed staged at stand.
3. **BF.BLW.FAN01** — No further surge excursions since the 08:10 event on 11-Mar. Shaft displacement steady at **36 µm**. Process engineer confirmed the 08:10 event was from a downstream BFG header valve test. No mechanical concern. Log closed.
4. **SP.SINT.FAN01** — 1X vibration `JSR.SP.FAN01.VIB.1X` rose from 1.9 to **2.7 mm/s** (above normal 2.3, below warning 4.5). Bearing temp stable at 58 °C. *Incremental rise likely from dust deposit imbalance (typical sinter fan behaviour).* Balancing weights set in store (`BAL-WT-01` — 5 units). Schedule an online balancing run if 1X exceeds 3.5 mm/s.

---

## HANDOVER-008
**Date:** 2026-03-13 | **Shift:** C→A | **Outgoing:** Vijay Singh | **Incoming:** Arjun Patel

### Watch Items
1. **HSM.F3.WR.BRG01 — URGENT.** AE reached **11.8 dBuV** at 04:50 (very close to alarm 12 dBuV). BPFO envelope **1.1 g — warning threshold crossed** (warning = 1.0 g). Temp `JSR.HR.STD3.WR.BRG01.TEMP.DE` = **73 °C** (approaching warning 85 °C). **I authorised moving the roll-change from Saturday to TOMORROW (14-Mar) 06:00 as originally planned — already aligned. The scheduled slot holds. If BPFO hits 3.0 g or temp hits 85 °C before 06:00 Saturday, invoke immediate controlled stop per Playbook 01 Step 2.** All crew and spares confirmed.
2. **BF.CW.PMP02** — Bearing temp `JSR.BF.CW.PMP02.TEMP.BRG` = **76 °C** (below warning 85 °C). VIB 1X = **2.1 mm/s** (below warning 2.8 mm/s). Head deviation = **-6%** (worsening, still below warning -7%). Recommend placing `IMP-CW-01` impeller on order — 6-week lead time (stock = 0... check store).
3. **CCM.MOLD.01** — TC delta showed a **17 °C** reading at 02:30 (normal range ≤20 °C). Friction `JSR.CC1.MOLD.OSC.FRICTION` = **6 kN** (normal). Level deviation = **1.2 mm** (normal). This was during a speed reduction — no concern, but log for BPS trend review.

### Completed This Shift
- EAF HPU ISO4406 inline at 03:00: **16/14/11** (at warning). Kidney-loop running. Should clear by morning.
- SP SINT FAN01 1X at 02:45: **3.0 mm/s** (rising). Supervisor notified. Online balancing job raised in CMMS.

---

## HANDOVER-009
**Date:** 2026-03-14 | **Shift:** A→B | **Outgoing:** Rakesh Sharma | **Incoming:** Priya Mehta

### Watch Items
1. **HSM.F3.WR.BRG01 — ROLL-CHANGE COMPLETED** at 11:45. LOTO applied at 06:00; bearing pulled at 07:30 — confirmed outer-race fatigue spall (SCN-037 mode, approx. 8 mm × 12 mm spall on outer race, ~120° arc, consistent with Stage 3/4 BPFO signature). New `BRG-LRG-300` induction-heated and fitted 09:30. Laser alignment completed at 10:45; residual offset 0.018 mm (within 0.05 mm limit). LOTO released 11:00. Run-check at 11:15: VIB **1.3 mm/s**, AE **0.8 dBuV**, temp **53 °C**. **Returned to service.** Root-cause documented in CMMS: lube contamination (Fe particles in OFB oil = 3 ppm — monitoring `JSR.HR.STD3.WR.BRG01.OFB.OUT.TEMP` for next 48 h).
2. **HSM.F1.GBX01** — Fe count lab result: **18 ppm — WARNING THRESHOLD (15 ppm) EXCEEDED.** GMF vib now **4.8 mm/s** (below warning 6.0 mm/s, normal range top is 4.0 mm/s — borderline). **Raise CMMS work order for gearbox oil drain and refill + filter change (OIL-VG220 + FLT-GBX-01 both in stock) within 72 hours.** Spectrographic analysis also requested — looking for sideband harmonic growth.
3. **BF.BLW.FAN01** — Bearing temp `JSR.BF.BLW.FAN01.TEMP.BRG` = **71 °C** (normal, rising trend from 65 °C last week). Shaft displacement **39 µm** (normal). Flag for next vibration analysis to check 1X phase shift (could indicate early journal bearing change in stiffness).

### Completed This Shift
- SP.SINT.FAN01 online balancing completed 09:00–11:00. Added 2 × 50 g trim weights at 145° and 317°. Post-balance VIB 1X = **1.8 mm/s** (within normal). BRG temp unchanged at 57 °C.

---

## HANDOVER-010
**Date:** 2026-03-14 | **Shift:** B→C | **Outgoing:** Priya Mehta | **Incoming:** Suresh Naidu

### Watch Items
1. **HSM.F1.GBX01 — WORK ORDER RAISED** (WO-2026-0741). Oil drain scheduled for 17-Mar 06:00 (next planned stop window). Fe count trending: 3 → 8 → 12 → 14 → 18 ppm over 15 days — clear upward trend consistent with early gear tooth wear (GMF sideband index up 23% from baseline). Keep VIB GMF watch: warning = 6.0 mm/s, alarm = 10.0 mm/s. Currently **5.2 mm/s** — close to warning.
2. **EAF.AUX.HYD01** — ISO4406 recovered to **16/14/11** by 17:00 (kidney-loop helped). Water content **72 ppm** (normal). Filter DP **0.9 bar** (normal). Oil temp **47 °C** (normal). System stabilised after filter change — green across all sensors.
3. **MS.LDC.CRN01** — Gearbox GMF `JSR.MS.CRN01.GBX.VIB.GMF` = **0.78 g** (rising, still below warning 1.0 g). Brake drum temp after 290 t ladle pick: **96 °C** — approached warning 110 °C. Cool-down cycle ran 15 min; recovered to 62 °C. **If brake drum exceeds 110 °C on next pick, initiate crane inspection. Hoist is safety-critical (P1).**
4. **CCM.MOLD.01** — TC delta stable at **11–14 °C** through all heats today. Level deviation within ±1.5 mm. Mould copper plate campaign at 320 heats (design life ~400 heats). Note for planning: `MOLD-CU-STD` on shelf (1 set), lead time 14 weeks if consumed — keep inventory topped up.

---

## HANDOVER-011
**Date:** 2026-03-15 | **Shift:** A→B | **Outgoing:** Arjun Patel | **Incoming:** Lakshmi Rao

### Watch Items
1. **HSM.F1.GBX01 — APPROACHING WARNING.** GMF VIB at 08:00: **5.8 mm/s** (warning = 6.0). Fe count re-run at 06:00 (fast turnaround): **22 ppm** (alarm = 40 ppm but rate of rise concerning). Viscosity sample requested — waiting on lab. **If GMF hits 6.0 mm/s before the 17-Mar oil change, escalate to immediate shutdown.** Do NOT defer beyond 17-Mar under any circumstances.
2. **BF.CW.PMP02** — Head deviation worsened to **-6.8%** (warning = -7%). VIB 1X = **2.3 mm/s** (approaching warning 2.8). **I have pre-ordered `IMP-CW-01` — 6-week lead. Also pre-staged `WRING-CW-01` wear rings.** Next planned outage is 4 Apr — target hydraulic test + impeller inspection then.
3. **CRM.AGC.SV01** — Gauge deviation `JSR.CR.S2.AGC.GAUGE.DEV` showed a **+8 µm** spike at 07:30 (warning = 10 µm). Recovered immediately. ISO4406 = 15/13/10 (normal). Position error = 0.4% (normal). Possibly a momentary servo hunt during grade change. If it recurs > 3 times per shift, pull the servo circuit for inspection.
4. **RHF.ZONE.SOAK** — Shell hotspot now **164 °C** (was 149 °C — growing slowly). Zone temp 1242 °C, flame signal 95% — normal. **Refractory wall thinning is confirmed progression.** Tenova survey moved to earliest possible: 20-Mar. Recommend reducing soak zone setpoint from 1260 to 1240 °C to reduce thermal gradient on the hot side.

---

## HANDOVER-012
**Date:** 2026-03-16 | **Shift:** B→C | **Outgoing:** Vijay Singh | **Incoming:** Arjun Patel

### Watch Items
1. **HSM.F1.GBX01 — CONTROLLED SHUTDOWN EXECUTED at 18:30.** GMF VIB reached **6.3 mm/s** (crossed warning 6.0 at 18:15). Oil temp rose to **72 °C** (approaching warning 80 °C). Fe count from 14:00 sample: **31 ppm** (approaching alarm 40). Shift supervisor authorised controlled stop. LOTO applied at 18:30. Oil drain commenced — found significant metallic sludge and **one chip-detector magnet fragment** (≈3 mm), consistent with early gear tooth crack progression (SCN-038 onset). Awaiting metallurgical sample from oil analysis. **CMMS WO upgraded to URGENT: gear-tooth fatigue inspection. Borescope required.** Specialist crew from Flender notified.
2. **HSM.F1.MTR01** — Motor on its own standby (GBX01 shut down). MCSA run at 19:00 with motor uncoupled from gearbox: sideband `JSR.HR.STD1.MTR01.MCSA.RBAR.SB` = **-57 dBc** (normal). Motor is healthy — confirmed isolated from gearbox vibration.
3. **CCM.SEG.07** — Post-repair monitoring (Day 5): all rolls nominal. RPM 13–16 rpm. Force 295–320 kN. Spray flow 198 L/min. Bulge 0.2 mm. **Segment cleared from intensive monitoring — revert to normal schedule.**

---

## HANDOVER-013
**Date:** 2026-03-17 | **Shift:** C→A | **Outgoing:** Suresh Naidu | **Incoming:** Rakesh Sharma

### Watch Items
1. **HSM.F1.GBX01 — BORESCOPE COMPLETED at 04:00** by Flender specialist. Findings: 3 teeth on output pinion showing Stage 1 fatigue crack (root initiation, not through-crack). `GEAR-WHL-M20` has 36-week lead time (stock = 0). **Options being evaluated: (a) limited-speed operation at 60% torque pending emergency procurement of gear wheel — specialist view is 2–4 week window at reduced load; (b) immediate full shutdown and crane extraction for workshop repair. Decision required by 08:00 from Plant Manager.** All standby production routes (if any) being assessed by Planning.
2. **RM.CONV.ORE01** — Belt edge `JSR.RM.CONV1.BELT.EDGE` at **18 mm** offset (approaching warning 25 mm). Motor current 82 %FLA (normal). Rip-loop current stable at 68 mA. Likely misalignment from ore flow imbalance after last weekend's stockpile reclaim. Schedule training idler adjustment on next available day-shift access.
3. **RHF.ZONE.SOAK** — Shell hotspot scan at 03:00: **171 °C**. Still growing. **Escalate: if it hits 180 °C before Tenova survey (20-Mar), initiate partial furnace derate (reduce to 80% firing rate).** Zone temp currently 1235 °C — within spec.

---

## HANDOVER-014
**Date:** 2026-03-18 | **Shift:** A→B | **Outgoing:** Rakesh Sharma | **Incoming:** Priya Mehta

### Watch Items
1. **HSM.F1.GBX01 — DECISION: Reduced-load operation at 65% rated torque** authorised by Plant Manager at 08:30. Max rolling speed reduced. Production impact: ~18% throughput reduction on F1 stand. Emergency procurement for `GEAR-WHL-M20` initiated through Flender Europe (36-week standard lead; urgent freight and partial-machining split being explored — target 10-week delivery). **CMMS PM frequency increased to 12-hourly GMF vib checks.**
2. **HSM.F1.MTR01** — Running at reduced load with GBX01. VIB DE `JSR.HR.STD1.MTR01.VIB.DE.RMS` = **1.5 mm/s** (normal). Winding temp **102 °C** (normal for reduced-load). All healthy.
3. **CCM.MOLD.01** — Oscillator friction `JSR.CC1.MOLD.OSC.FRICTION` showed a rising trend: **7.2 kN** at noon (still within normal 2–8 kN but highest reading in 10 days). Mould copper plates at 340 heats. Plan copper plate swap for next scheduled caster stop (estimated 22-Mar). Pre-position `MOLD-CU-STD` from store.

---

## HANDOVER-015
**Date:** 2026-03-19 | **Shift:** B→C | **Outgoing:** Lakshmi Rao | **Incoming:** Vijay Singh

### Watch Items
1. **BF.BLW.FAN01 — THRUST BEARING TEMP CONCERN.** `JSR.BF.BLW.FAN01.THRUST.TEMP` = **82 °C** at 20:45 (warning = 90 °C, normal ≤75 °C). 1X VIB `JSR.BF.BLW.FAN01.VIB.1X` = **2.6 mm/s** (normal). Shaft displacement = **43 µm** (normal). **This is the FIRST reading above normal for thrust bearing.** API 670 Bently Nevada alarm set at 90 °C. Possible early lube film thinning on thrust pad. Increase lube oil supply temp to BLW to warm the oil slightly (reduce viscosity if running cold), and check lube supply pressure. **Do NOT ignore this — BF blower downtime = $500k/hr.** Notify BF process engineer and maintenance superintendent immediately.
2. **MS.LDC.CRN01 — ROPE MFL ELEVATED.** Monthly MFL scan at 17:00: **138 mV** (approaching warning 150 mV). Diameter measurement at mid-drum: nominal. No visible broken wires on 1 m visual. **Competent Person inspection requested for this week.** Crane WLL operation continues but log ISO 4309 discard-criteria tracking. `ROPE-CRN-01` is a 12-week lead item — place order now as insurance.
3. **HSM.F1.GBX01** — 12-hourly check at 20:00: GMF VIB = **5.4 mm/s** (stable since reduced-load operation). Fe count from 16:00 sample: **28 ppm** (slightly reduced — consistent with oil drain and refill done before shutdown). Cautiously positive.

---

## HANDOVER-016
**Date:** 2026-03-20 | **Shift:** C→A | **Outgoing:** Vijay Singh | **Incoming:** Arjun Patel

### Watch Items
1. **BF.BLW.FAN01 — THRUST TEMP STABILISED** at **78 °C** (still above normal ≤75 but below warning 90 °C). Lube supply pressure checked: was at lower end of specification (2.4 bar vs nominal 2.6–3.2 bar). Lube pump check valve had slight bypass — adjusted. Temp trend reversing. **Continue monitoring at 30-min intervals. If it rises above 85 °C at any point, initiate planned speed reduction and notify BF manager for possible blower switch-over (if redundant blower available).**
2. **RHF.ZONE.SOAK** — Tenova survey completed at 02:00–04:00. Findings: 45 mm refractory wall thickness remaining vs 90 mm original at the hotspot (south wall panel). Recommendation: repair with gunite during next planned cool (target 30-Mar). **Setpoint reduced to 1235 °C as interim per last handover recommendation.** Shell IR hotspot: **169 °C** (stable since setpoint reduction). No alarm imminent.
2. **MS.LDC.CRN01** — Competent Person rope inspection completed at 03:30. No broken wires found. 3-strand sections measured — diameters nominal (max deviation −0.5% from nominal). MFL **138 mV** as per scan — inspector attributes to minor corrosion pitting in the strands. **Rope to be re-lubricated this A-shift.** Insurance order for `ROPE-CRN-01` placed with Konecranes (12-week delivery).
3. **CCM.MOLD.01** — Oscillator friction `JSR.CC1.MOLD.OSC.FRICTION` = **8.4 kN** (just crossed normal range 8 kN, approaching warning 10 kN). TC delta = **13 °C** (normal). Level = **0.9 mm** (normal). **Mould copper plates now at 355 heats.** Plate-swap scheduled for 22-Mar stop window confirmed. Pre-check `MOLD-CU-STD` stock and `SEN-NOZ-01` nozzle supply (8 on shelf — sufficient).

---

## HANDOVER-017
**Date:** 2026-03-21 | **Shift:** A→B | **Outgoing:** Rakesh Sharma | **Incoming:** Priya Mehta

### Watch Items
1. **CRM.AGC.SV01 — SERVO HUNT RECURRING.** Position error `JSR.CR.S2.AGC.SV.POSERR` showed **3 excursions >1.5%** (warning threshold) during the 06:00–10:00 window. Gauge deviation `JSR.CR.S2.AGC.GAUGE.DEV` peaked at **+9 µm** on one excursion (just below warning 10 µm). ISO4406 inline at 09:00: **16/14/11** (at warning — one step above normal). This combination (oil at warning cleanliness + recurring servo hunt) is the early signature of silt accumulation on the spool (SCN-048). **AGC already switched to backup position mode.** Plan: switch to standby servo during tonight's maintenance window; send `JSR.CR.S2.AGC.SV` circuit for bench clean. `SERVO-VLV-D661` spare on shelf; `FLT-SERVO-3` filter elements in stock.
2. **BF.BLW.FAN01** — Thrust temp now stable at **74 °C** (back within normal range post lube adjustment). 1X VIB = **2.4 mm/s** (normal). Shaft displacement = **40 µm** (normal). Situation resolved — revert to normal monitoring schedule.
3. **HSM.F1.GBX01** — 12-hourly GMF check at 08:00: **5.1 mm/s** (stable/slightly improving under reduced load). Fe count 06:00 sample: **24 ppm** (downward trend since oil change). **Situation managing well at reduced load.** Emergency gear wheel procurement update: Flender Germany confirmed 10-week air-freight delivery; ETA 26-May.

---

## HANDOVER-018
**Date:** 2026-03-22 | **Shift:** B→C | **Outgoing:** Lakshmi Rao | **Incoming:** Suresh Naidu

### Watch Items
1. **CRM.AGC.SV01 — SERVO VALVE REPLACED at 14:30.** Old valve bench-tested: spool annular gap measured — found hard silt deposits (consistent with SCN-048, ISO4406 16/14/11 contamination). Ultrasonic clean took 40 min; valve re-tested — spool movement improved but null leakage up to **1.1 L/min** (warning 1.0 L/min exceeded). Decision: replace with spare `SERVO-VLV-D661`. New valve installed, matched null offset, step-response tested vs Moog datasheet. Position error now **0.18%** (nominal). **AGC returned to automatic mode at 16:00.** 3-µm filter `FLT-SERVO-3` also replaced. **Kidney-loop running to bring ISO4406 back to ≤15/13/10.** Plan: re-sample oil in 48 h.
2. **CCM.MOLD.01 — MOULD PLATES SWAPPED** at 15:00 during scheduled caster stop. Old plates at 371 heats (design ~400 heats). No breakout events in campaign. New `MOLD-CU-STD` installed, taper set per Primetals spec for 225×1600 mm slab. Oscillator friction after new plates: **4.2 kN** (nominal). TC delta uniform at **11 °C**. Caster restarted at 17:30. **Monitor first 3 heats closely for BPS anomalies (new mould run-in).**
3. **BF.CW.PMP02** — VIB 1X jumped to **2.5 mm/s** (approaching warning 2.8). Head deviation = **-6.5%** (approaching warning -7%). Bearing temp **68 °C** (normal). **Running close to warning on two parameters simultaneously.** Advise: switch to redundant pump for BF cooling circuit (if operationally possible) and put PMP02 on standby for inspection. `IMP-CW-01` on order (delivery 28-Apr).

---

## HANDOVER-019
**Date:** 2026-03-23 | **Shift:** A→B | **Outgoing:** Arjun Patel | **Incoming:** Vijay Singh

### Watch Items
1. **BF.CW.PMP02 — PUMP SWITCHED to standby unit at 05:15.** PMP02 isolated and LOTO applied. Impeller inspection in progress: impeller leading-edge erosion of ~1.5 mm (normal life consumption; consistent with -6.5% head deviation). No cracking or cavitation pitting found. **Decision: return PMP02 to service without impeller replacement; monitor daily.** Head dev should remain stable at -6.5% with current loading. `IMP-CW-01` remains on order — will replace at next planned outage.
2. **RM.CONV.ORE01** — Belt edge corrected to **7 mm** after training-idler adjustment (B-shift yesterday). Rip-loop current `JSR.RM.CONV1.RIP.LOOP` = 70 mA (normal 60–80 mA). Motor current `JSR.RM.CONV1.MTR.CURR` = 79 %FLA. Belt fully nominal.
3. **CCM.MOLD.01** — First 3 heats post-plate-swap monitored. TC delta max 14 °C, friction 4.0–4.8 kN, level ±1.2 mm. **New mould run-in complete — cleared for normal production schedule.**
4. **SP.SINT.FAN01** — 1X VIB = **2.1 mm/s** (remained stable since balancing). Bearing temp = 56 °C. **Sinter fan fully recovered.**

---

## HANDOVER-020
**Date:** 2026-03-24 | **Shift:** C→A | **Outgoing:** Suresh Naidu | **Incoming:** Rakesh Sharma

### Watch Items
1. **MS.LDC.CRN01 — ELEVATED MFL GROWING.** Spot MFL check at 02:00: **162 mV** — crossed warning threshold (150 mV). This is the first formal warning-level reading. **Per ISO 4309:2017: crane must receive Competent Person inspection before next lift of molten ladle.** Shift Supervisor notified; crane temporarily restricted to ≤100 t dry loads (not molten metal) pending inspection. Inspection crew mobilised for 06:00 A-shift. `ROPE-CRN-01` order confirmed (12-week delivery).
2. **HSM.F1.GBX01** — 12-hourly GMF check at 03:00: **5.0 mm/s** (stable). Gear tooth status: Stage 1 crack per borescope (3 weeks ago) — no worsening confirmed on last inspection (18-Mar). **Maintain 65% torque limit.** Next borescope scheduled 31-Mar.
3. **EAF.AUX.HYD01** — Water content `JSR.MS.EAF1.HYD.WATER.PPM` rose to **165 ppm** (approaching warning 200 ppm). Source investigation: EAF water-cooling jacket possible micro-leak into HPU reservoir return line. **Defer heat if water >200 ppm — risk of hydraulic oil emulsification.** Notify EAF maintenance engineer.

---

## HANDOVER-021
**Date:** 2026-03-25 | **Shift:** A→B | **Outgoing:** Rakesh Sharma | **Incoming:** Priya Mehta

### Watch Items
1. **MS.LDC.CRN01 — COMPETENT PERSON INSPECTION COMPLETED at 09:30.** Finding: **4 broken wires in one strand over one lay length** (ISO 4309 warning criterion: ≥4 broken wires in one strand = discard criterion per Table 2). **CRANE TAKEN OUT OF SERVICE IMMEDIATELY at 10:00.** Emergency rope replacement in progress. `ROPE-CRN-01` not yet arrived (12-week delivery). **Emergency procurement via Konecranes India direct-from-stock (different spec, requires engineering approval).** Konecranes India confirm compatible rope (same diameter, different lay — engineering sign-off in progress). Production impact: ladle movements via alternative route (longer cycle, ~15% BOF productivity reduction).
2. **EAF.AUX.HYD01** — Water PPM now **193 ppm** (just below warning 200 ppm). Micro-leak in EAF water jacket confirmed; will repair during today's tap break. Until then, divert return line through temporary coalescer filter. Monitor inline every 30 min.
3. **RHF.ZONE.SOAK** — Shell hotspot stable at **167 °C** (gun-ite repair scheduled 30-Mar). Reduced firing rate maintained. Zone temp 1232 °C.

---

## HANDOVER-022
**Date:** 2026-03-26 | **Shift:** B→C | **Outgoing:** Priya Mehta | **Incoming:** Vijay Singh

### Watch Items
1. **MS.LDC.CRN01 — ROPE REPLACEMENT IN PROGRESS.** Konecranes India compatible rope (engineering approval received at 12:30). New rope reeving started 14:00. Expected completion: 04:00 tomorrow. Wedge-socket dead-end fittings confirmed. Drum and sheave groove inspection ongoing — no abnormal wear found. **Crane OOS until rope change complete + load test.**
2. **EAF.AUX.HYD01** — Water-jacket micro-leak repaired during 13:00 tap break. Water PPM `JSR.MS.EAF1.HYD.WATER.PPM` trending down: 148 ppm at 18:00. Coalescer filter removed; return line restored. ISO4406 = 16/14/11 — recovering.
3. **HSM.DSC.PMP01** — Seal weep has progressed. VIB `JSR.HR.DSC.PMP01.VIB.CAS.RMS` now **2.2 mm/s** (below warning 2.5 but rising). Bearing temp `JSR.HR.DSC.PMP01.TEMP.BRG` = **74 °C** (approaching warning 85 °C). **Switch to standby descale pump tonight and book seal cartridge change for tomorrow morning.** `SEAL-MECH-DSC` in stock (2 units).

---

## HANDOVER-023
**Date:** 2026-03-27 | **Shift:** C→A | **Outgoing:** Suresh Naidu | **Incoming:** Arjun Patel

### Watch Items
1. **MS.LDC.CRN01 — ROPE REPLACEMENT COMPLETE at 03:30.** New rope installed, wedge sockets set, fleet angle checked (2.1° — within <4°). Load test completed: 1.25× SWL (400 t static test) — PASSED. Competent Person certificate issued. **Crane returned to full service for molten ladle lifts at 05:00.** MFL scan on new rope baseline: **12 mV** (as expected for new rope).
2. **HSM.DSC.PMP01 — SEAL CHANGE COMPLETED at 01:30.** Back-pullout cartridge changed; shaft sleeve measured — 0.04 mm scoring (within 0.1 mm limit, not replaced). SiC/SiC faces finger-clean. Runout at coupling: 0.03 mm TIR (within 0.05 mm). Pump recommissioned at 02:30. VIB = **0.9 mm/s**, temp = **52 °C** — fully nominal.
3. **HSM.F1.GBX01** — GMF VIB at 03:30: **4.9 mm/s** (stable, reduced-load operation continuing). Oil temp **58 °C**. Fe count from 01:00: **21 ppm** (stable downward trend). Gear wheel emergency procurement status: Flender Germany confirm delivery 2 June (10 weeks from order date).

---

## HANDOVER-024
**Date:** 2026-03-28 | **Shift:** A→B | **Outgoing:** Rakesh Sharma | **Incoming:** Priya Mehta

### Watch Items
1. **RHF.ZONE.SOAK — SHELL HOTSPOT: 178 °C** (approaching alarm 180 °C; warning is 180 °C). Gunite repair window is 30-Mar. **If hotspot exceeds 180 °C before 30-Mar: reduce firing further to 70% or initiate unplanned cool.** Zone temp now at 1218 °C (setpoint 1235 °C reduced for margin). Slab reheat time increasing — notified production planning for schedule buffer.
2. **BF.BLW.FAN01** — Thrust temp back at **76 °C** (just above normal ≤75 °C) — slight regression since lube adjustment. 1X VIB stable at **2.3 mm/s**. **Book lube-system inspection for next planned BF outage.** Lube pump check valve may need replacement.
3. **RM.CONV.ORE01** — New IR walk-down at 08:00: all idlers <45 °C. Belt tracking: edge at **3 mm** (nominal). Motor current **77 %FLA**. **Conveyor fully healthy.**
4. **SP.SINT.FAN01** — 1X VIB trending up again: **2.9 mm/s** (normal band top 2.3 mm/s). Bearing temp 59 °C (normal). Dust deposits likely rebuilding after last online balance. **Schedule online balance check if >3.5 mm/s.**

---

## HANDOVER-025
**Date:** 2026-03-29 | **Shift:** C→A | **Outgoing:** Vijay Singh | **Incoming:** Suresh Naidu

### Watch Items
1. **RHF.ZONE.SOAK — HOTSPOT 183 °C — ALARM THRESHOLD CROSSED at 04:30.** Firing immediately reduced to 65% (zone temp dropped to 1205 °C). Production planning notified; slab reheat extended 12 min per slab. **Gunite repair crew mobilised for 30-Mar 00:01 start (bringing forward by 18 hours).** Shell temp stable at 183 °C after firing reduction (no further rise). Tenova on-site at 06:00.
2. **HSM.F1.GBX01** — GMF VIB at 03:00: **5.3 mm/s**. Fe count: **19 ppm**. Both trending stable. No change from last 5 days. Equipment managing well at 65% load.
3. **MS.LDC.CRN01** — First ladle lifts since rope replacement. MFL baseline scan post-installation: **14 mV** (nominal). Brake drum temp after 295 t pick: **88 °C** (approaching warning 110 °C — new rope means slightly different drum engagement). Brake pad inspection raised in CMMS for next week.

---

## HANDOVER-026
**Date:** 2026-03-30 | **Shift:** A→B | **Outgoing:** Arjun Patel | **Incoming:** Lakshmi Rao

### Watch Items
1. **RHF.ZONE.SOAK — GUNITE REPAIR IN PROGRESS.** Furnace cooled from 01:00. Tenova crew applied gunite at 06:30. 65 mm new castable applied over south wall panel. Cure time 24 h + gradual firing ramp (EN 746-2 dry-out schedule: 100 °C/h to 600 °C, hold 2 h; 100 °C/h to 1200 °C, hold 1 h; then normal operation). **Furnace back at full fire: 36 hours from now (31-Mar 18:00 target).** Production 2 slabs behind schedule — buffer window used.
2. **CRM.AGC.SV01** — Post-servo-replacement monitoring: ISO4406 oil now at **14/12/9** (better than normal — kidney-loop over-performed). Position error = **0.19%** (nominal). Gauge deviation = ±2 µm (nominal). Servo fully recovered.
3. **HSM.F3.WR.BRG01** — 2-week post-repair check: VIB **1.4 mm/s**, AE **1.1 dBuV**, temp **57 °C**, OFB outlet temp **61 °C**. All nominal. OFB oil Fe count = **2 ppm** (clean). **Bearing fully healthy — revert to standard monthly check intervals.**

---

## HANDOVER-027
**Date:** 2026-04-01 | **Shift:** A→B | **Outgoing:** Rakesh Sharma | **Incoming:** Priya Mehta

### Watch Items
1. **RHF.ZONE.SOAK — BACK TO FULL OPERATION at 18:30 on 31-Mar.** Shell scan this morning (06:00): hotspot area **101 °C** (back within normal 80–120 °C range). Zone temp 1255 °C. Flame signal 96%. Flue O2 2.5%. **Furnace fully recovered.** Next shell scan in 2 weeks; Tenova recommend annual inspection going forward.
2. **EAF.AUX.HYD01** — Water content now **44 ppm** (fully normal after micro-leak repair). ISO4406 = **15/13/10** (normal). Filter DP = **0.7 bar** (normal). HPU fully nominal. **Remove from watch list.**
3. **HSM.F1.GBX01** — Morning 12-hourly GMF check: **5.0 mm/s** (stable). Fe count stable at 18–20 ppm range. **Gear wheel ETA confirmed: 5 June from Flender Germany.** Slot booked for full gearbox swap maintenance 8–10 June. Risk: operation at 65% load for 9 more weeks — acceptable per Flender engineer assessment (tooth root crack classified Stage 1; re-examination on 31-Mar borescope showed no progression). **Weekly borescope now mandatory.**
4. **BF.BLW.FAN01** — Thrust temp: **73 °C** (within normal ≤75 °C). Lube pump check valve replaced on 31-Mar during BF partial stop. System healthy.

---

## HANDOVER-028
**Date:** 2026-04-03 | **Shift:** B→C | **Outgoing:** Lakshmi Rao | **Incoming:** Vijay Singh

### Watch Items
1. **HSM.STD.R1 — FORCE RIPPLE ANOMALY.** Rolling force ripple `JSR.HR.R1.FORCE` spiked to **4.2%** at 15:50 (crossed warning 4%). Periodic pattern at ~2.8 Hz (matches 1× roll rotation for this strip product gauge). VIB chock `JSR.HR.R1.WR.VIB.CHOCK` = **2.8 mm/s** (below warning 4.0). AE `JSR.HR.R1.WR.AE.RMS` = **4 dB** (below warning 8). **Strip crown deviation `JSR.HR.R1.CROWN.DEV` = +18 µm** (approaching warning 25 µm). *This is the classic early work-roll spall signature (SCN-044 Stage 2 onset).* **Work rolls to be changed at next scheduled roll-change window (tonight 22:00).** `WR-HSS-PREP` pairs staged in roll shop (4 on shelf). Segregate strip from 15:30–22:00 for visual inspection.
2. **BF.CW.PMP02 — HEAD DEVIATION at -7.1% — WARNING CROSSED.** `JSR.BF.CW.PMP02.HEAD.DEV` = **-7.1%** (warning = -7%). VIB 1X = **2.6 mm/s** (below warning 2.8). Bearing temp = **72 °C** (normal). **Switch to standby pump for BF cooling circuit and schedule PMP02 for impeller inspection/replacement.** `IMP-CW-01` now due: delivery 28-Apr (pre-ordered 5 weeks ago — only 3 more weeks to wait).

---

## HANDOVER-029
**Date:** 2026-04-04 | **Shift:** C→A | **Outgoing:** Suresh Naidu | **Incoming:** Arjun Patel

### Watch Items
1. **HSM.STD.R1 — WORK ROLL CHANGED at 22:15 on 3-Apr.** New pair from roll shop confirmed surface UT-inspected. Post-change check: Force ripple = **0.9%** (normal). Chock VIB = **0.4 mm/s** (normal). Crown deviation = **+4 µm** (normal). Old rolls returned to roll shop — spall confirmed by grinder operator: 6 mm flat, subsurface crack confirmed by UT. Rolls condemned (below minimum diameter after grind would be required). **Root cause: thermal-shock cobble from 3 days prior (not logged properly — raise corrective action for cobble logging).**
2. **BF.CW.PMP02** — Standby pump operating nominally. PMP02 LOTO applied. Impeller inspection at 02:00: erosion on leading edges confirmed (consistent with pre-ordered impeller change). **Replace impeller with `IMP-CW-01` when it arrives 28-Apr. Until then, operate on standby.** Bearing condition on PMP02 shaft: normal, no regrease needed.
3. **CCM.MOLD.01** — TC delta `JSR.CC1.MOLD.TC.DELTA` = **12 °C** (stable). New copper plates now at 12 heats of new campaign. Level deviation ±0.8 mm. Friction 4.1 kN. **Caster fully healthy.**

---

## HANDOVER-030
**Date:** 2026-04-05 | **Shift:** A→B | **Outgoing:** Arjun Patel | **Incoming:** Lakshmi Rao

### Watch Items
1. **HSM.F1.MTR01 — MCSA ANNUAL CHECKS COMPLETED at 07:30.** Rotor bar sideband = **-55 dBc** (normal, well above alarm -35 dBc). Phase current imbalance = **0.8%** (normal). Polarisation index (offline test on spare stator winding) = **3.4** (normal ≥2.0). Stator winding temp at rated load = **124 °C** (normal). **Motor fully healthy — no action required.** Update CMMS next PI due date: April 2027.
2. **EAF.AUX.HYD01** — Routine inline ISO4406 at 09:00: **16/14/11** (at warning). Filter DP = **2.4 bar** (approaching warning 3.0). **Filter change due.** This is the 3rd filter change in 6 weeks — ISO4406 keeps returning to warning. **Investigate root cause: possible internal wear (pump or cylinder seals) generating particles faster than filtration can remove.** Consider particle morphology analysis on next oil sample.
3. **SP.SINT.FAN01** — 1X VIB = **3.3 mm/s** (above normal 2.3, approaching action level 3.5). Bearing temp = 60 °C (normal). Balancing check requested in CMMS (WO-2026-0892). Schedule during next sinter-plant maintenance window.
4. Summary: All Tier-1 critical assets currently **GREEN** except HSM.F1.GBX01 (AMBER — managed reduced-load operation; gear wheel ETA 5 June) and SP.SINT.FAN01 (AMBER — vib rising, balance job pending).

---

*End of Shift Handover Notes — TATA_JSR (Synthetic). 30 notes covering 2026-03-10 to 2026-04-05.*
*All asset_ids, sensor tags, thresholds, spare part codes, and failure mode nomenclature consistent with ground_truth_spine.json v1.0.0.*
*SYNTHETIC DATA — physics-grounded representative examples for ML training purposes only.*
