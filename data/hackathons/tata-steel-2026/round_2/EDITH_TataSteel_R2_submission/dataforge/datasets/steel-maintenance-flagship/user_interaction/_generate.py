#!/usr/bin/env python3
"""
Generate USER INTERACTION data (spec 4.4) for the Tata Steel Round-2 Maintenance Wizard.
Everything is grounded in SPEC/ground_truth_spine.json + the equipment manuals (MAN-*),
maintenance SOPs (SOP-*), RCA reports (RCA-*), and the condition-monitoring CSVs.

Outputs:
  nl_queries.jsonl            (~150 single-turn engineer Q&A)
  troubleshooting_prompts.jsonl (~60 scenario-based diagnostic chains)
  multiturn_conversations.jsonl (~50 multi-turn dialogues, 3-6 turns)

NOT real plant data: synthetic but physics-accurate, grounded in the spine.
"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
SPINE = os.path.join(HERE, "..", "SPEC", "ground_truth_spine.json")

with open(SPINE) as f:
    spine = json.load(f)

assets = {a["asset_id"]: a for a in spine["asset_registry"]}
scenarios = {s["scenario_id"]: s for s in spine["failure_scenario_catalog"]}
spares = {p["part_id"]: p for p in spine["spare_parts_master"]}

# Map asset_id -> manual file, sop file (by equipment_class order in dir)
MAN = {
    "HSM.F3.WR.BRG01": "MAN-001_rolling_mill_work_roll_bearing.md",
    "HSM.F1.GBX01": "MAN-002_mill_gearbox.md",
    "HSM.F1.MTR01": "MAN-003_large_induction_motor_vfd.md",
    "HSM.DSC.PMP01": "MAN-004_cooling_descaling_pump.md",
    "BF.BLW.FAN01": "MAN-005_bf_sinter_fan_blower.md",
    "CCM.SEG.07": "MAN-006_continuous_caster_segment.md",
    "CCM.MOLD.01": "MAN-007_continuous_caster_mould.md",
    "HSM.STD.R1": "MAN-008_hot_strip_mill_stand.md",
    "RM.CONV.ORE01": "MAN-009_raw_material_conveyor.md",
    "RHF.ZONE.SOAK": "MAN-010_reheating_furnace.md",
    "EAF.AUX.HYD01": "MAN-011_eaf_bof_auxiliary_hydraulics.md",
    "BF.CW.PMP02": "MAN-004_cooling_descaling_pump.md",
    "SP.SINT.FAN01": "MAN-005_bf_sinter_fan_blower.md",
    "MS.LDC.CRN01": "MAN-012_ladle_crane.md",
    "CRM.AGC.SV01": "MAN-013_hydraulics_agc_servo.md",
}
SOP = {
    "SCN-037": "SOP-01_bearing-replacement.md",
    "SCN-038": "SOP-02_gearbox-oil-gear-service.md",
    "SCN-039": "SOP-03_motor-rewind-swap.md",
    "SCN-040": "SOP-04_pump-mechanical-seal.md",
    "SCN-041": "SOP-05_fan-balancing-blade-service.md",
    "SCN-042": "SOP-06_caster-segment-change.md",
    "SCN-043": "SOP-07_mould-copper-change.md",
    "SCN-044": "SOP-08_hot-strip-mill-roll-change.md",
    "SCN-045": "SOP-09_conveyor-idler-belt.md",
    "SCN-046": "SOP-12_furnace-burner-refractory.md",
    "SCN-047": "SOP-10_crane-wire-rope-brake.md",
    "SCN-048": "SOP-11_agc-servo-valve-hydraulic-clean.md",
}
RCA = {
    "SCN-037": "RCA-001-HSM-F3-WR-BRG01-BPFO-spall.md",
    "SCN-038": "RCA-002-HSM-F1-GBX01-gear-tooth-fatigue.md",
    "SCN-039": "RCA-003-HSM-F1-MTR01-broken-rotor-bar.md",
    "SCN-040": "RCA-004-HSM-DSC-PMP01-mechanical-seal.md",
    "SCN-041": "RCA-005-BF-BLW-FAN01-compressor-surge.md",
    "SCN-042": "RCA-006-CCM-SEG07-roll-seizure.md",
    "SCN-043": "RCA-007-CCM-MOLD01-breakout-sticking.md",
    "SCN-044": "RCA-008-HSM-STD-R1-work-roll-spall.md",
    "SCN-045": "RCA-009-RM-CONV-ORE01-idler-bearing.md",
    "SCN-046": "RCA-010-RHF-ZONE-SOAK-burner-failure.md",
    "SCN-047": "RCA-011-MS-LDC-CRN01-wire-rope-fatigue.md",
    "SCN-048": "RCA-012-CRM-AGC-SV01-servo-silting.md",
}

# Tools the wizard can call (agentic RAG + tool-use surface)
T_SENSOR = "get_sensor_reading"       # live/last value for a tag
T_TREND = "get_sensor_trend"          # timeseries window for a tag
T_ASSET = "get_asset_info"            # registry lookup
T_THRESH = "get_thresholds"           # normal/warn/alarm for a tag
T_KB = "search_knowledge_base"        # RAG over manuals/SOPs/RCAs
T_SOP = "get_sop"                     # fetch a specific SOP
T_MANUAL = "get_equipment_manual"     # fetch a MAN-*
T_RCA = "get_rca_report"              # fetch RCA-*
T_SPARE = "lookup_spare_part"         # stock_qty + lead_time + cost
T_HIST = "query_maintenance_history"  # CMMS work-order history
T_ALERT = "get_active_alerts"         # anomaly_alerts.csv
T_DIAG = "run_diagnostic_model"       # classifier / RUL
T_COST = "estimate_cost_impact"       # downtime/cost
T_WO = "create_work_order"            # CMMS write (planning)

nl = []   # nl_queries.jsonl rows
ts = []   # troubleshooting_prompts.jsonl rows
mt = []   # multiturn_conversations.jsonl rows


def q(query, answer, refs, tools):
    nl.append({
        "query": query,
        "expected_answer": answer,
        "grounding_refs": refs,
        "expected_tools": tools,
    })


# ---------------------------------------------------------------------------
# (A) nl_queries.jsonl  -- single-turn engineer questions
# ---------------------------------------------------------------------------

# ---- Threshold / spec lookups (one per key sensor) -------------------------
q("What is the normal vibration range for the F3 work-roll bearing JSR.HR.STD3.WR.BRG01.VIB.DE.H.RMS?",
  "Normal velocity RMS is 0.5-2.3 mm/s. Warning trips at 4.5 mm/s and alarm at 7.1 mm/s, per ISO 20816-3:2022 Group 2 zones for asset HSM.F3.WR.BRG01.",
  ["spine:HSM.F3.WR.BRG01/JSR.HR.STD3.WR.BRG01.VIB.DE.H.RMS", "MAN-001_rolling_mill_work_roll_bearing.md"],
  [T_THRESH, T_ASSET])

q("What temperature should the F3 work-roll bearing run at, and when does it alarm?",
  "Bearing outer-ring temp (JSR.HR.STD3.WR.BRG01.TEMP.DE) normal band is 40-70 degC. Warning is 85 degC, alarm/trip is 100 degC (ISO 15243:2017 sec7). A controlled stop is triggered when temp exceeds 100 degC.",
  ["spine:HSM.F3.WR.BRG01/JSR.HR.STD3.WR.BRG01.TEMP.DE"], [T_THRESH, T_SENSOR])

q("What is the alarm threshold for envelope BPFO on the F3 work-roll bearing?",
  "Envelope BPFO amplitude (JSR.HR.STD3.WR.BRG01.VIB.DE.ENV.BPFO) is normal 0.0-0.5 g, warning 1.0 g, alarm 3.0 g (ISO 15243:2017). A rise toward 3 g indicates an outer-race spall.",
  ["spine:HSM.F3.WR.BRG01/JSR.HR.STD3.WR.BRG01.VIB.DE.ENV.BPFO"], [T_THRESH])

q("Which sensor is the leading indicator of bearing spall on the HSM F3 work-roll bearing?",
  "Acoustic emission RMS (JSR.HR.STD3.WR.BRG01.AE.RMS) is the leading indicator. It crosses its 6 dBuV warning at roughly weeks 6-8, before any vibration change. Envelope BPFO and temperature follow later in stages 3-4.",
  ["spine:SCN-037/degradation_timeline", "spine:HSM.F3.WR.BRG01/JSR.HR.STD3.WR.BRG01.AE.RMS", "RCA-001-HSM-F3-WR-BRG01-BPFO-spall.md"],
  [T_TREND, T_KB])

q("What is the GMF-band vibration warning and alarm for the F1 gearbox?",
  "GMF-band vibration RMS (JSR.HR.STD1.GBX01.VIB.GMF.RMS) on HSM.F1.GBX01 is normal 0.5-4.0 mm/s, warning 6.0 mm/s, alarm 10.0 mm/s.",
  ["spine:HSM.F1.GBX01/JSR.HR.STD1.GBX01.VIB.GMF.RMS"], [T_THRESH])

q("What ferrous particle ppm is acceptable in the F1 gearbox oil?",
  "Ferrous particle count (JSR.HR.STD1.GBX01.OIL.FE.PPM) is normal 0-5 ppm, warning 15 ppm, alarm 40 ppm (ASTM D5185 / ISO 4406:2021). Above 40 ppm indicates active gear/bearing metal loss.",
  ["spine:HSM.F1.GBX01/JSR.HR.STD1.GBX01.OIL.FE.PPM"], [T_THRESH, T_SENSOR])

q("What is the normal kinematic viscosity for the F1 gearbox oil and what oil is specified?",
  "Oil is ISO VG220 EP gear oil. Kinematic viscosity at 40 degC normal band is 198-242 cSt (ISO 3448 VG220 +/-15%); warning low 180 cSt, alarm high 265 cSt. The matching spare is OIL-VG220 (200L drum).",
  ["spine:HSM.F1.GBX01/JSR.HR.STD1.GBX01.OIL.VISC", "spine:spare/OIL-VG220"], [T_THRESH, T_SPARE])

q("What lube oil pressure must the F1 gearbox maintain?",
  "Forced-lube pressure (JSR.HR.STD1.GBX01.OIL.PRES) normal 2.5-4.0 bar; warning LOW at 2.2 bar, alarm LOW at 2.0 bar. Below 2.0 bar risks boundary lubrication of gears and bearings.",
  ["spine:HSM.F1.GBX01/JSR.HR.STD1.GBX01.OIL.PRES"], [T_THRESH, T_SENSOR])

q("What MCSA rotor-bar sideband level indicates a broken rotor bar on the F1 main motor?",
  "MCSA rotor-bar sideband (JSR.HR.STD1.MTR01.MCSA.RBAR.SB) normal -70 to -50 dBc, warning -45 dBc, alarm -35 dBc (IEEE 1415-2006). Crossing -35 dBc at steady load confirms broken-bar diagnosis.",
  ["spine:HSM.F1.MTR01/JSR.HR.STD1.MTR01.MCSA.RBAR.SB", "spine:SCN-039"], [T_THRESH, T_DIAG])

q("What is the stator winding temperature limit for the F1 main motor?",
  "Stator winding temp (JSR.HR.STD1.MTR01.WIND.TEMP) on the Class-F insulated ABB AMI 630 motor is normal 80-130 degC, warning 145 degC, alarm 155 degC (IEC 60034-1 Class F).",
  ["spine:HSM.F1.MTR01/JSR.HR.STD1.MTR01.WIND.TEMP"], [T_THRESH])

q("What polarisation index value means the F1 motor insulation is degrading?",
  "Polarisation index (JSR.HR.STD1.MTR01.INS.PI) is normal 2.0-5.0; warning at 2.0 and alarm at 1.5 (IEEE 43-2013). Lower is worse - PI dropping toward 1.5 indicates insulation moisture/contamination.",
  ["spine:HSM.F1.MTR01/JSR.HR.STD1.MTR01.INS.PI"], [T_THRESH])

q("What phase current imbalance is allowed on the F1 main motor?",
  "Phase current imbalance (JSR.HR.STD1.MTR01.CURR.IMBAL) normal 0-1%, warning 2%, alarm 5% (NEMA MG1-2021 12.45).",
  ["spine:HSM.F1.MTR01/JSR.HR.STD1.MTR01.CURR.IMBAL"], [T_THRESH])

q("What suction pressure causes cavitation on the HP descaling pump?",
  "Suction pressure (JSR.HR.DSC.PMP01.PRES.SUC) normal 120-250 kPa; warning LOW 90 kPa, alarm LOW 70 kPa (HI 9.6.1-2017 NPSH). Falling below these starves NPSH and triggers cavitation.",
  ["spine:HSM.DSC.PMP01/JSR.HR.DSC.PMP01.PRES.SUC"], [T_THRESH, T_SENSOR])

q("What is the normal discharge pressure and flow of the HP descaling pump?",
  "Discharge pressure (JSR.HR.DSC.PMP01.PRES.DIS) normal 190-210 bar (warn 175, alarm 165). Discharge flow (JSR.HR.DSC.PMP01.FLOW.DIS) normal 388-412 m3/hr (warn 372, alarm 352), per the pump curve +/-3%.",
  ["spine:HSM.DSC.PMP01/JSR.HR.DSC.PMP01.PRES.DIS", "spine:HSM.DSC.PMP01/JSR.HR.DSC.PMP01.FLOW.DIS"], [T_THRESH])

q("When does the BF turbo-blower shaft displacement alarm?",
  "Shaft displacement pk-pk (JSR.BF.BLW.FAN01.SHAFT.DISP) on BF.BLW.FAN01 is normal 10-50 um, warning 80 um, alarm 127 um (API 670:2014 Table 1, proximity probe).",
  ["spine:BF.BLW.FAN01/JSR.BF.BLW.FAN01.SHAFT.DISP"], [T_THRESH])

q("What discharge pressure oscillation indicates surge on the BF blower?",
  "Discharge pressure oscillation (JSR.BF.BLW.FAN01.PRES.OSC) normal 0-2%, warning 5%, alarm 8%. Above 8% with surge-margin loss is incipient compressor surge (API 670 surge basis).",
  ["spine:BF.BLW.FAN01/JSR.BF.BLW.FAN01.PRES.OSC", "spine:SCN-041"], [T_THRESH])

q("What roll rotation speed on caster segment 7 indicates a seized roll?",
  "Roll rotation speed (JSR.CC1.SEG07.ROLL.RPM) normal 3-25 rpm; warning at 1.0 rpm, alarm at 0.0 rpm. A drop to 0 rpm means roll seizure - the roll stops and drags the strand.",
  ["spine:CCM.SEG.07/JSR.CC1.SEG07.ROLL.RPM", "spine:SCN-042"], [T_THRESH, T_SENSOR])

q("What segment clamping force is abnormal on caster segment 7?",
  "Segment clamping force (JSR.CC1.SEG07.FORCE.HYD) normal 200-400 kN, warning 480 kN, alarm 550 kN. Rising force with falling roll rpm is the roll-seizure signature.",
  ["spine:CCM.SEG.07/JSR.CC1.SEG07.FORCE.HYD", "spine:SCN-042"], [T_THRESH])

q("What mould TC delta indicates a breakout precursor on Caster 1 mould?",
  "Adjacent-thermocouple delta (JSR.CC1.MOLD.TC.DELTA) normal 0-20 degC, warning 25 degC, alarm 50 degC. A V-pattern cold spot above 50 degC propagating down the mould is a sticking-breakout precursor flagged by the BPS.",
  ["spine:CCM.MOLD.01/JSR.CC1.MOLD.TC.DELTA", "spine:SCN-043"], [T_THRESH, T_DIAG])

q("What oscillator friction force is abnormal on the caster mould?",
  "Mould oscillator friction force (JSR.CC1.MOLD.OSC.FRICTION) normal 2-8 kN, warning 10 kN, alarm 18 kN. A friction spike combined with TC V-pattern and level wave is the 3-sensor breakout signature.",
  ["spine:CCM.MOLD.01/JSR.CC1.MOLD.OSC.FRICTION", "spine:SCN-043"], [T_THRESH])

q("What roll-force ripple indicates a work-roll spall on roughing stand R1?",
  "Rolling-force ripple (JSR.HR.R1.FORCE) normal 0-2%, warning 4%, alarm 8%. A periodic ripple at 1x roll frequency (period = pi*D) is a work-roll spall printing on the strip.",
  ["spine:HSM.STD.R1/JSR.HR.R1.FORCE", "spine:SCN-044"], [T_THRESH, T_DIAG])

q("What idler surface temperature is a fire risk on the ore conveyor?",
  "Idler surface temp (JSR.RM.CONV1.IDLER.TEMP) normal 25-60 degC, warning 80 degC, alarm 100 degC (fire-risk threshold). A seized idler above 100 degC under a loaded belt is the #1 belt-fire initiator.",
  ["spine:RM.CONV.ORE01/JSR.RM.CONV1.IDLER.TEMP", "spine:SCN-045"], [T_THRESH, T_SENSOR])

q("What idler ultrasound level warns of a failing conveyor idler bearing?",
  "Idler ultrasound level (JSR.RM.CONV1.IDLER.US) normal -20 to -8 dBuV (above baseline). Warning +8 dBuV, alarm +15 dBuV. A rise of +8 dBuV is the earliest idler-bearing warning, before temperature rise.",
  ["spine:RM.CONV.ORE01/JSR.RM.CONV1.IDLER.US", "spine:SCN-045"], [T_THRESH])

q("What conveyor rip-detector loop current means a belt tear?",
  "Rip-detector loop current (JSR.RM.CONV1.RIP.LOOP) normal 60-80 mA, warning 48 mA, alarm 0 mA. An open loop (0 mA) means a rip-detector loop is severed = longitudinal belt tear.",
  ["spine:RM.CONV.ORE01/JSR.RM.CONV1.RIP.LOOP"], [T_THRESH])

q("What flame scanner signal triggers fuel cutoff on the reheat furnace soak zone?",
  "Flame scanner signal (JSR.RHF.Z3.FLAME.SIG) normal 90-100%, warning 70%, alarm 40% (EN 746-2:2010 sec5.4). Lower is worse - automatic fuel cutoff occurs below 40% flame signal.",
  ["spine:RHF.ZONE.SOAK/JSR.RHF.Z3.FLAME.SIG", "spine:SCN-046"], [T_THRESH])

q("What flue-gas O2 range is correct on the reheat furnace soak zone?",
  "Flue-gas O2 (JSR.RHF.Z3.FLUE.O2) normal 1.5-3.5%; low warning 1.0% (rich/CO risk), high warning 5.0%, alarm 6.0% (EN 746-2 / EIGA). High O2 with low flame signal indicates burner failure / excess air.",
  ["spine:RHF.ZONE.SOAK/JSR.RHF.Z3.FLUE.O2", "spine:SCN-046"], [T_THRESH])

q("What is the soak-zone furnace temperature setpoint band?",
  "Zone temperature (JSR.RHF.Z3.ZONE.TEMP) normal 1180-1280 degC, warning 1300 degC, alarm 1330 degC (Type S thermocouple).",
  ["spine:RHF.ZONE.SOAK/JSR.RHF.Z3.ZONE.TEMP"], [T_THRESH])

q("What ISO 4406 cleanliness must the EAF hydraulic power unit oil meet?",
  "EAF HPU oil cleanliness (JSR.MS.EAF1.HYD.ISO4406) target <=17/15/12; warning 18/16/13, alarm 19/17/14 (ISO 4406:2021).",
  ["spine:EAF.AUX.HYD01/JSR.MS.EAF1.HYD.ISO4406"], [T_THRESH])

q("What water content in the EAF hydraulic oil triggers an alarm?",
  "Water content (JSR.MS.EAF1.HYD.WATER.PPM) normal 0-100 ppm, warning 200 ppm, alarm 500 ppm. Free/emulsified water above 500 ppm degrades film strength and accelerates corrosion.",
  ["spine:EAF.AUX.HYD01/JSR.MS.EAF1.HYD.WATER.PPM"], [T_THRESH, T_SENSOR])

q("What filter differential pressure indicates a clogged filter on the EAF HPU?",
  "Filter diff pressure (JSR.MS.EAF1.HYD.FILT.DP) normal 0-1.5 bar, warning 3.0 bar, alarm 4.5 bar. Above 4.5 bar the element is clogged and bypass may open - change FLT-HYD-10.",
  ["spine:EAF.AUX.HYD01/JSR.MS.EAF1.HYD.FILT.DP", "spine:spare/FLT-HYD-10"], [T_THRESH, T_SPARE])

q("What head deviation indicates impeller wear on the BF cooling-water pump?",
  "Differential-head deviation (JSR.BF.CW.PMP02.HEAD.DEV) normal -3 to +3%; warning -7%, alarm -12%. Negative deviation = impeller/wear-ring erosion losing head (HI 9.6.7-2021).",
  ["spine:BF.CW.PMP02/JSR.BF.CW.PMP02.HEAD.DEV"], [T_THRESH])

q("What servo oil cleanliness is required for the cold-mill AGC servo valve?",
  "AGC servo oil cleanliness (JSR.CR.S2.AGC.SV.ISO4406) target <=15/13/10; warning 16/14/11, alarm 17/15/12 (ISO 4406:2021 servo). Servo valves need cleaner oil than general hydraulics due to 1-3 um spool clearance.",
  ["spine:CRM.AGC.SV01/JSR.CR.S2.AGC.SV.ISO4406", "spine:SCN-048"], [T_THRESH])

q("What servo position error indicates AGC valve silting?",
  "Servo position error (JSR.CR.S2.AGC.SV.POSERR) normal 0.0-0.5%, warning 1.5%, alarm 3.0%. Position hunt on small commands with dirty oil (ISO 16/14/11+) is the silting signature.",
  ["spine:CRM.AGC.SV01/JSR.CR.S2.AGC.SV.POSERR", "spine:SCN-048"], [T_THRESH, T_DIAG])

q("When must the ladle-crane wire rope be discarded per ISO 4309?",
  "Discard when MFL signal (JSR.MS.CRN01.ROPE.MFL) reaches 300 mV (~>15-20% LMA), or >=12 random broken wires in one lay length (or >=4 in one strand), or rope-diameter reduction exceeds -7% nominal (ISO 4309:2017). Warning is 150 mV (~8-12% LMA) / -3% diameter.",
  ["spine:MS.LDC.CRN01/JSR.MS.CRN01.ROPE.MFL", "spine:SCN-047", "SOP-10_crane-wire-rope-brake.md"], [T_THRESH, T_KB])

q("At what load does the ladle crane cut power?",
  "Hoist load (JSR.MS.CRN01.LOAD.SWL) alarms at 95% WLL and cuts power at 110% SWL on this 320t molten-metal ladle crane (FEM 1.001 / BS EN 13135). This is stricter than general EOT cranes (105/110).",
  ["spine:MS.LDC.CRN01/JSR.MS.CRN01.LOAD.SWL"], [T_THRESH])

# ---- Asset registry / identity questions -----------------------------------
q("Who is the OEM and model of the F1 main drive motor, and what are its bearings?",
  "HSM.F1.MTR01 is an ABB AMI 630 MV induction motor (6000 kW, 990 rpm), VFD-fed via an ACS6000, Class-F insulation. DE bearing is SKF 6326, NDE bearing is SKF 6226. Matching spare is BRG-MTR-SET.",
  ["spine:HSM.F1.MTR01", "spine:spare/BRG-MTR-SET"], [T_ASSET, T_SPARE])

q("What is the rated power of the BF turbo-blower and its criticality?",
  "BF.BLW.FAN01 is a Siemens/MAN axial blast machine rated 28,000 kW at 3600 rpm, criticality 1 (Tier-1 critical). Installed 2016-03-01, last overhaul 2023-10-12.",
  ["spine:BF.BLW.FAN01"], [T_ASSET])

q("What OEM made the F1 gearbox and what is its rated power?",
  "HSM.F1.GBX01 is a Flender H4SH mill-drive reduction gearbox, forced-lube on ISO VG220, rated 6000 kW, criticality 1.",
  ["spine:HSM.F1.GBX01"], [T_ASSET])

q("Which assets are criticality-1 in the hot rolling area?",
  "In HOT_ROLLING the criticality-1 assets are HSM.F3.WR.BRG01 (F3 work-roll bearing), HSM.F1.GBX01 (F1 gearbox), HSM.F1.MTR01 (F1 main motor), and HSM.STD.R1 (R1 roughing stand). The descale pump HSM.DSC.PMP01 is criticality 2.",
  ["spine:asset_registry"], [T_ASSET])

q("What is the SWL of the melt-shop ladle crane?",
  "MS.LDC.CRN01 is a Konecranes 320t ladle crane hoist (rated_load_t 320), criticality 1, molten-metal handling - safety-critical.",
  ["spine:MS.LDC.CRN01"], [T_ASSET])

q("Which standards back the vibration thresholds in this plant?",
  "Vibration uses ISO 10816-3:2009 / ISO 20816-3:2022 zone tables; rolling-bearing failure modes use ISO 15243:2017; machinery protection (shaft displacement) uses API 670:2014; motors use NEMA MG1-2021 / IEC 60034-1.",
  ["spine:standards_backbone"], [T_KB])

# ---- Spare-part / lead-time questions ---------------------------------------
q("What is the lead time for the custom F1 gearbox gear wheel?",
  "GEAR-WHL-M20 (custom large-module gear wheel >M20) has stock_qty 0 and a 36-week lead time, unit cost USD 120,000 / INR 10,020,000. This long lead is the key reason a gear-tooth fatigue failure on HSM.F1.GBX01 is so costly.",
  ["spine:spare/GEAR-WHL-M20", "spine:SCN-038"], [T_SPARE])

q("Do we stock a spare MV motor for the F1 main drive and what is its lead time?",
  "Yes - MTR-MV-6000 (MV insurance spare motor 6000 kW), stock_qty 1, 40-week lead time, unit cost USD 450,000. It is a reusable rotating-capital asset; the failed motor is rewound (RWND-KIT-MV) and returned to spare stock.",
  ["spine:spare/MTR-MV-6000", "spine:SCN-039"], [T_SPARE])

q("What is the lead time on the Moog D661 AGC servo valve?",
  "SERVO-VLV-D661 (Moog D661 servo valve) has stock_qty 1 and a 10-week lead time, unit cost USD 14,000. With only one on the shelf, plan a kidney-loop clean (KID-LOOP-01) and bench-clean of the removed valve to avoid stocking out.",
  ["spine:spare/SERVO-VLV-D661", "spine:SCN-048"], [T_SPARE])

q("How many large-bore roller bearings (>300mm) do we stock and what fits them?",
  "BRG-LRG-300 has stock_qty 1, 8-week lead time, USD 12,000 each. It fits the rolling_mill_work_roll_bearing and bf_sinter_fan_blower classes.",
  ["spine:spare/BRG-LRG-300"], [T_SPARE])

q("What is the lead time for caster mould copper plates?",
  "MOLD-CU-STD (mould copper plates, standard slab format) has stock_qty 1 and a 14-week lead time, USD 55,000. Critical for breakout recovery on CCM.MOLD.01.",
  ["spine:spare/MOLD-CU-STD", "spine:SCN-043"], [T_SPARE])

q("Which spares are zero-lead-time (on shelf, ready to fit)?",
  "Zero-lead-time spares include FLT-GBX-01, OIL-VG220, WR-HSS-PREP (prepared work rolls), IDLER-STD-1600, NOZ-SPRAY-01, SEN-NOZ-01, VULC-KIT-01, BAL-WT-01, FLT-HYD-10, FLT-SERVO-3, and SOCK-WEDGE-01.",
  ["spine:spare_parts_master"], [T_SPARE])

q("What spare seal do I need for the descale-pump mechanical seal job and its lead time?",
  "SEAL-MECH-DSC (mechanical seal cartridge SiC/SiC), stock_qty 2, 2-week lead time, USD 1,500. Pair it with SLV-SHAFT-01 (shaft sleeve, stock 1, 3-week) if the sleeve scoring exceeds 0.1mm.",
  ["spine:spare/SEAL-MECH-DSC", "spine:spare/SLV-SHAFT-01", "spine:SCN-040"], [T_SPARE])

q("How many spare work-roll pairs do we keep and what do they cost?",
  "WR-HSS-PREP (prepared HSS work-roll pair from roll shop), stock_qty 4, zero lead time, USD 80,000 per pair. They enable a 15-45 min quick roll change after a spall.",
  ["spine:spare/WR-HSS-PREP", "spine:SCN-044"], [T_SPARE])

q("What is the anti-surge valve lead time for the BF blower?",
  "ASV-VLV-01 (anti-surge valve, Koso/Fisher) has stock_qty 0 and a 12-week lead time, USD 45,000. Journal-bearing pads (BRG-JRNL-PAD) and thrust pads (BRG-THRUST-PAD) are also 12-week items.",
  ["spine:spare/ASV-VLV-01", "spine:SCN-041"], [T_SPARE])

# ---- Cost / downtime questions ----------------------------------------------
q("What does a compressor surge failure on the BF blower cost?",
  "Catastrophic: USD 6,000,000 point estimate (range USD 4-8M), INR 500,000,000. BF downtime runs ~USD 500k/hr and a sustained surge can destroy the machine in seconds. Safety class P1, 96h unplanned downtime.",
  ["spine:SCN-041/cost_impact"], [T_COST])

q("What is the cost difference between a planned and unplanned work-roll spall on R1?",
  "OxMaint data: planned change ~USD 11,200 vs unplanned ~USD 184,000 - a 16.4x penalty. Point estimate is USD 184,000 / INR 15,400,000. This is why force-ripple trending to catch spall early matters.",
  ["spine:SCN-044/cost_impact"], [T_COST])

q("What is the estimated cost of a caster breakout event?",
  "Breakout/sticking on CCM.MOLD.01: USD 860,000 point (OxMaint avg), range USD 200k-3M+, INR 71,810,000, 36h unplanned downtime, safety class P1.",
  ["spine:SCN-043/cost_impact"], [T_COST])

q("What is the business impact of an AGC servo-valve silting failure?",
  "USD 137,700 / INR 11,500,000. AGC loss drives ~30% scrap increase plus cobble risk; CRM cobble cost is roughly Rs 21 lakh per cobble-hour. Safety class P2.",
  ["spine:SCN-048/cost_impact"], [T_COST])

q("How much does a ladle-crane wire-rope failure potentially cost?",
  "USD 1,000,000 point estimate, range USD 1M-20M (Qinghe 2007 ladle-drop benchmark), INR 83,000,000, 24h unplanned, safety class P1. The catastrophic potential is loss of life from a molten-ladle drop.",
  ["spine:SCN-047/cost_impact"], [T_COST])

q("What is the cost of an F1 gearbox tooth-fatigue failure?",
  "USD 600,000 point (range USD 500k-3M), INR 50,100,000, 168h (7-day) unplanned downtime - driven by the 36-week lead time on the custom GEAR-WHL-M20 gear wheel. Safety class P2.",
  ["spine:SCN-038/cost_impact", "spine:spare/GEAR-WHL-M20"], [T_COST])

# ---- Failure-mode definitional / RCA questions ------------------------------
q("What causes outer-race spalling on the F3 work-roll bearing?",
  "Subsurface rolling-contact fatigue initiating an outer-race spall (ISO 15243 fatigue mode), accelerated by lube contamination. The signature is rising AE first, then envelope BPFO toward 3 g, then temperature rise toward 100 degC.",
  ["spine:SCN-037/root_cause", "RCA-001-HSM-F3-WR-BRG01-BPFO-spall.md"], [T_RCA, T_KB])

q("Why do gear teeth crack on the F1 gearbox?",
  "Tooth-root fatigue cracking, typically initiated by a prior high-torque cobble event, producing chunky spall debris. Signature: cepstrum rahmonics and GMF sidebands rise, then chip-detector/spall particles, then tooth fracture.",
  ["spine:SCN-038/root_cause", "RCA-002-HSM-F1-GBX01-gear-tooth-fatigue.md"], [T_RCA])

q("What is the root cause of broken rotor bars on the F1 motor?",
  "Rotor-bar fracture from repeated high-torque starts and thermal cycling. MCSA shows sidebands at (1+/-2s)*f1 growing from -50 toward -35 dBc, with 2x-slip vibration appearing as bars crack progressively over 2-4 weeks.",
  ["spine:SCN-039/root_cause", "RCA-003-HSM-F1-MTR01-broken-rotor-bar.md"], [T_RCA, T_DIAG])

q("What causes mechanical-seal failure on the descale pump?",
  "Mechanical seal face wear from abrasive scale-laden water, with secondary O-ring degradation. Broadband casing vibration rises 1.5->5+ mm/s and bearing temp climbs as the seal weeps then sprays.",
  ["spine:SCN-040/root_cause", "RCA-004-HSM-DSC-PMP01-mechanical-seal.md"], [T_RCA])

q("Why does the caster segment roll seize?",
  "Roll-bearing seizure from thermal load and water/scale ingress. The roll stops rotating (rpm->0) and drags the strand, clamping force climbs above 480 kN, risking transverse slab cracks and breakout.",
  ["spine:SCN-042/root_cause", "RCA-006-CCM-SEG07-roll-seizure.md"], [T_RCA])

q("What is the root cause of a caster sticking breakout?",
  "Shell sticking to the mould wall from poor lubrication, improper taper, or SEN blockage. It is confirmed only by 3-sensor agreement (TC V-pattern + oscillator friction spike + level wave); any single sensor alone has >40% false-alarm rate.",
  ["spine:SCN-043/root_cause", "RCA-007-CCM-MOLD01-breakout-sticking.md"], [T_RCA, T_DIAG])

q("What causes the ore-conveyor idler bearing to fail and why is it dangerous?",
  "A dry or failed idler bearing seizes under the loaded belt - the #1 belt-fire initiator. Ultrasound rises +8 then +15 dBuV and idler temp climbs to 100 degC (fire threshold).",
  ["spine:SCN-045/root_cause", "RCA-009-RM-CONV-ORE01-idler-bearing.md"], [T_RCA])

q("What causes a burner failure on the reheat furnace soak zone?",
  "Burner nozzle fouling or gas-supply fluctuation causing an unstable flame (EN 746-2). Flame signal falls 96->below 40% and flue O2 rises as unburnt fuel accumulates; auto fuel cutoff fires below 40%.",
  ["spine:SCN-046/root_cause", "RCA-010-RHF-ZONE-SOAK-burner-failure.md"], [T_RCA])

q("What causes AGC servo-valve silting?",
  "Silt (1-5 um particles) plugs the servo-spool annular gap (1-3 um clearance), giving sluggish small-amplitude response. Oil drifts dirtier than ISO 16/14/11, position error and gauge deviation grow.",
  ["spine:SCN-048/root_cause", "RCA-012-CRM-AGC-SV01-servo-silting.md"], [T_RCA])

# ---- Procedure / SOP questions ----------------------------------------------
q("What is the first step before any bearing replacement on the F3 work-roll bearing?",
  "Apply LOTO and confirm zero-energy state (Playbook 01 / SOP-01). Use a controlled stop - not an emergency trip - then a hydraulic bearing puller (never strike the bearing).",
  ["spine:SCN-037/correct_resolution", "SOP-01_bearing-replacement.md"], [T_SOP])

q("What temperature should a new work-roll bearing be heated to during fitting?",
  "Induction-heat the new bearing to 80-100 degC for interference fitting, then laser-align to <0.05 mm, and replace the coupling element and labyrinth seal (CPL-EL-01, SEAL-LAB-01).",
  ["spine:SCN-037/correct_resolution", "SOP-01_bearing-replacement.md", "spine:spare/SEAL-LAB-01"], [T_SOP, T_SPARE])

q("How do I verify a successful bearing replacement on the F3 work roll?",
  "Run-in and verify vibration < 2.3 mm/s and bearing temp < 70 degC at 60 minutes, returning both to their normal bands before releasing to production.",
  ["spine:SCN-037/correct_resolution"], [T_SOP, T_SENSOR])

q("What is the procedure for an F1 gearbox tooth fracture?",
  "Immediate controlled stop (no deferral), crane the gearbox to the repair bay, replace the gear wheel plus bearings, set backlash 0.1-0.3 mm, verify Prussian-blue contact >70% face, then run-in at low load before full load.",
  ["spine:SCN-038/correct_resolution", "SOP-02_gearbox-oil-gear-service.md"], [T_SOP])

q("How do I confirm a broken rotor bar before swapping the motor?",
  "Confirm via MCSA at steady load (sideband worse than -35 dBc). Plan the motor swap within 2-4 weeks using the insurance spare, send the failed motor for rotor-bar test and repair, and verify phase rotation before energising the spare.",
  ["spine:SCN-039/correct_resolution", "SOP-03_motor-rewind-swap.md"], [T_SOP, T_DIAG])

q("What is the response sequence when the BPS flags a caster breakout?",
  "On BPS alarm reduce casting speed to a minimum 0.5 m/min immediately; if it keeps escalating, full emergency stop (halt withdrawal + close the tundish gate) and evacuate the caster floor (liquid steel is fatal). Do not operate until steel has solidified 4-6h+, then remove the skull, replace damaged segments, and run a 5-whys RCA within 48h.",
  ["spine:SCN-043/correct_resolution", "SOP-07_mould-copper-change.md"], [T_SOP])

q("What do I do first on a compressor surge alarm at the BF blower?",
  "Verify the anti-surge valve (ASV) auto-opened. If surge persists beyond 2-3 cycles, trip immediately and do NOT restart until the cause is identified. Then borescope IGVs/impellers, run ferrography on the oil, and recalibrate the anti-surge line vs OEM data.",
  ["spine:SCN-041/correct_resolution", "MAN-005_bf_sinter_fan_blower.md"], [T_SOP, T_KB])

q("What is the correct response to an idler-bearing fire-risk alarm on the conveyor?",
  "Stop the belt immediately (fire risk), apply LOTO and belt-tension lock before entry, lift the belt and replace the idler with the correct width/trough/rating (IDLER-STD-1600), and confirm free rotation before restart.",
  ["spine:SCN-045/correct_resolution", "SOP-09_conveyor-idler-belt.md", "spine:spare/IDLER-STD-1600"], [T_SOP, T_SPARE])

q("What is the procedure for a flame-failure on the reheat furnace?",
  "Automatic fuel cutoff fires below 40% flame signal. Purge the furnace before re-light (safety-critical), clean or replace the burner nozzle and flame scanner (BURN-NOZ-01, FLAME-SCAN-01), then re-tune the fuel-air ratio.",
  ["spine:SCN-046/correct_resolution", "SOP-12_furnace-burner-refractory.md"], [T_SOP, T_SPARE])

q("How do I clean a silted AGC servo valve safely?",
  "Switch AGC to backup/manual lock, perform high-pressure hydraulic LOTO (200-350 bar), remove the valve and ultrasonic bench-clean (replace if scored), match the null offset on reinstall, change the 3 um + 10 um filters, kidney-loop the oil back to ISO 15/13/10, then step-response test vs the OEM datasheet.",
  ["spine:SCN-048/correct_resolution", "SOP-11_agc-servo-valve-hydraulic-clean.md"], [T_SOP])

q("What is the procedure when a ladle-crane rope hits ISO 4309 discard?",
  "Take the crane out of service immediately (do not lift). If a load is suspended, lower it under control first. Then a Competent Person inspects and certifies, replace the rope, inspect drum/sheave grooves, keep fleet angle <4 deg, and terminate with a wedge socket (not clips).",
  ["spine:SCN-047/correct_resolution", "SOP-10_crane-wire-rope-brake.md"], [T_SOP])

q("How do I change a descale-pump mechanical seal?",
  "Switch to standby, isolate and LOTO, drain the casing, do a back-pullout seal change, inspect the shaft sleeve (replace if >0.1 mm scoring), install a new SiC/SiC seal with fingerprint-free faces, and confirm shaft runout < 0.05 mm TIR.",
  ["spine:SCN-040/correct_resolution", "SOP-04_pump-mechanical-seal.md"], [T_SOP])

q("How do I recover a seized caster-segment roll?",
  "Reduce casting speed if still in the liquid-core zone, end the heat and cool the strand 2-4h before bay entry, withdraw the segment with the handling crane, replace the seized roll and bearings, clean the nozzles, then set the segment gap per slab format and pressure-test.",
  ["spine:SCN-042/correct_resolution", "SOP-06_caster-segment-change.md"], [T_SOP])

q("What is the resolution for a work-roll spall on R1?",
  "Stop rolling on spall-printed product and segregate the affected strip, quick-change the work rolls (15-45 min using WR-HSS-PREP), send the roll to the roll shop to grind 3-5 mm below the spall, then UT-test after grinding and condemn if below minimum diameter.",
  ["spine:SCN-044/correct_resolution", "SOP-08_hot-strip-mill-roll-change.md", "spine:spare/WR-HSS-PREP"], [T_SOP, T_SPARE])

# ---- Active-alert / triage style questions ----------------------------------
q("F3 work-roll bearing AE is at 8 dBuV but vibration is still normal - is this an emergency?",
  "Not yet an emergency. 8 dBuV is between AE warning (6) and AE alarm (12) - stage-2 onset. AE is the leading indicator and crosses warning weeks before vibration. Plan a bearing change at the next window and trend envelope BPFO + bearing temp closely; it is not a controlled-stop trigger until BPFO climbs toward 3 g or temp toward 100 degC.",
  ["spine:SCN-037/sensor_signature", "spine:SCN-037/degradation_timeline"], [T_TREND, T_DIAG, T_KB])

q("Caster mould TC delta is 30 degC but friction and level are normal - do I stop the cast?",
  "No - do not stop on a single sensor. Breakout confirmation requires 3-sensor agreement (TC V-pattern + oscillator friction spike + mould-level wave); a single sensor has >40% false-alarm rate. Watch for friction crossing 10 kN and level deviation growing. 30 degC is above TC warning (25) but below alarm (50).",
  ["spine:SCN-043/root_cause", "spine:SCN-043/sensor_signature"], [T_TREND, T_DIAG])

q("The F1 motor MCSA sideband moved from -58 to -45 dBc. What does that mean and what should I do?",
  "It has reached the warning level (-45 dBc) for rotor-bar degradation - early-stage. Confirm with MCSA at steady load and trend it. Plan a motor swap within 2-4 weeks if it heads toward the -35 dBc alarm; the MTR-MV-6000 insurance spare has a 40-week lead so use the on-shelf unit and rewind the removed motor.",
  ["spine:SCN-039/sensor_signature", "spine:spare/MTR-MV-6000"], [T_TREND, T_DIAG, T_SPARE])

q("BF blower discharge pressure oscillation just hit 9% - what is the immediate action?",
  "That is above the 8% surge alarm. Verify the ASV auto-opened; if surge persists beyond 2-3 cycles, trip the blower immediately and do not restart until the cause (valve slam / inlet filter fouling) is found. Shaft displacement is also likely spiking toward the 127 um alarm.",
  ["spine:SCN-041/sensor_signature", "spine:SCN-041/correct_resolution"], [T_SENSOR, T_KB])

q("Idler ultrasound is +16 dBuV and idler temp is 100 degC on the ore conveyor - what now?",
  "This is a seized/failing idler bearing at the fire-risk threshold (US alarm 15, temp alarm 100). Stop the belt immediately, LOTO and belt-tension lock, and replace the idler (IDLER-STD-1600, on shelf). A seized idler under load is the top belt-fire cause.",
  ["spine:SCN-045/sensor_signature", "spine:SCN-045/correct_resolution"], [T_SENSOR, T_SPARE])

# Append asset-summary and misc grounded queries to reach ~150
def add_more_thresholds():
    extra = [
        ("What is the brake-drum temperature limit on the ladle crane?",
         "Brake-drum temp (JSR.MS.CRN01.BRAKE.TEMP) on MS.LDC.CRN01 is normal 25-90 degC, warning 110 degC, alarm 120 degC. Overheating indicates brake drag or slip.",
         ["spine:MS.LDC.CRN01/JSR.MS.CRN01.BRAKE.TEMP"], [T_THRESH]),
        ("What hoist-gearbox GMF level warns of gear wear on the ladle crane?",
         "Hoist-gearbox GMF (JSR.MS.CRN01.GBX.VIB.GMF) normal 0-0.5 g, warning 1.0 g, alarm 2.5 g.",
         ["spine:MS.LDC.CRN01/JSR.MS.CRN01.GBX.VIB.GMF"], [T_THRESH]),
        ("What strip-gauge deviation indicates AGC trouble on the cold mill?",
         "Strip-gauge deviation (JSR.CR.S2.AGC.GAUGE.DEV) normal -5 to +5 um, warning 10 um, alarm 20 um. A 22 um excursion with servo position hunt is the silting failure signature.",
         ["spine:CRM.AGC.SV01/JSR.CR.S2.AGC.GAUGE.DEV", "spine:SCN-048"], [T_THRESH]),
        ("What null leakage is acceptable on the AGC servo valve?",
         "Null leakage (JSR.CR.S2.AGC.SV.NULLLEAK) normal 0.0-0.5 L/min, warning 1.0, alarm 2.0. Rising null leak indicates spool wear.",
         ["spine:CRM.AGC.SV01/JSR.CR.S2.AGC.SV.NULLLEAK"], [T_THRESH]),
        ("What casing vibration is abnormal on the descale pump?",
         "Casing vibration (JSR.HR.DSC.PMP01.VIB.CAS.RMS) normal 0.5-1.5 mm/s, warning 2.5, alarm 5.0 (ISO 10816-7:2009). A rise to ~5.4 mm/s with bearing temp ~90 degC is the seal-failure signature.",
         ["spine:HSM.DSC.PMP01/JSR.HR.DSC.PMP01.VIB.CAS.RMS", "spine:SCN-040"], [T_THRESH]),
        ("What AE level indicates cavitation on the descale pump?",
         "Broadband AE RMS (JSR.HR.DSC.PMP01.AE.RMS) normal -2 to +2 dB, warning 8, alarm 15 (ASTM E2374-14, cavitation 100-500 kHz band).",
         ["spine:HSM.DSC.PMP01/JSR.HR.DSC.PMP01.AE.RMS"], [T_THRESH]),
        ("What thrust-bearing temperature warns on the BF blower?",
         "Thrust-bearing temp (JSR.BF.BLW.FAN01.THRUST.TEMP) normal 50-75 degC, warning 90, alarm 105.",
         ["spine:BF.BLW.FAN01/JSR.BF.BLW.FAN01.THRUST.TEMP"], [T_THRESH]),
        ("What 1x vibration alarm applies to the BF cooling-water pump?",
         "1x radial vibration (JSR.BF.CW.PMP02.VIB.1X) on BF.CW.PMP02 normal 0.5-1.8 mm/s, warning 2.8, alarm 5.6 (ISO 10816-7:2009).",
         ["spine:BF.CW.PMP02/JSR.BF.CW.PMP02.VIB.1X"], [T_THRESH]),
        ("What axial 2x ratio indicates misalignment on the sinter fan?",
         "Axial 2x ratio (JSR.SP.FAN01.VIB.AXIAL) on SP.SINT.FAN01 normal 0.0-0.3, warning 0.4, alarm 0.7. A rising axial 2x ratio points to shaft bow/misalignment.",
         ["spine:SP.SINT.FAN01/JSR.SP.FAN01.VIB.AXIAL"], [T_THRESH]),
        ("What duct DP indicates blade fouling/erosion on the sinter fan?",
         "Inlet-outlet DP (JSR.SP.FAN01.DP.DUCT) normal 8-14 kPa, warning 18, alarm 22. Rising DP signals performance degradation from blade deposit/erosion.",
         ["spine:SP.SINT.FAN01/JSR.SP.FAN01.DP.DUCT"], [T_THRESH]),
        ("What strand-bulge deviation is abnormal on caster segment 7?",
         "Strand bulge deviation (JSR.CC1.SEG07.BULGE) normal 0.0-1.0 mm, warning 2.0, alarm 4.0. Excess bulge indicates segment misalignment.",
         ["spine:CCM.SEG.07/JSR.CC1.SEG07.BULGE"], [T_THRESH]),
        ("What zone spray flow warns of nozzle blockage on segment 7?",
         "Zone spray flow (JSR.CC1.SEG07.SPRAY.FLOW) normal 180-220 L/min, warning 150, alarm 120. Low flow = spray-nozzle blockage in secondary cooling.",
         ["spine:CCM.SEG.07/JSR.CC1.SEG07.SPRAY.FLOW", "RCA-021-CCM-SEG07-spray-nozzle-blockage.md"], [T_THRESH]),
        ("What mould heat flux is too low on Caster 1?",
         "Mean mould heat flux (JSR.CC1.MOLD.HEATFLUX) normal 1.2-2.0 MW/m2, warning 1.0, alarm 0.8 (lower is worse). Falling heat flux indicates copper-plate wear or sticking.",
         ["spine:CCM.MOLD.01/JSR.CC1.MOLD.HEATFLUX"], [T_THRESH]),
        ("What mould-level deviation alarms on Caster 1?",
         "Mould-level deviation (JSR.CC1.MOLD.LEVEL.DEV) normal -2 to +2 mm, warning 5, alarm 12. A 13 mm level wave is part of the 3-sensor breakout signature.",
         ["spine:CCM.MOLD.01/JSR.CC1.MOLD.LEVEL.DEV", "spine:SCN-043"], [T_THRESH]),
        ("What chock vibration chatter alarms on roughing stand R1?",
         "Chock vibration chatter (JSR.HR.R1.WR.VIB.CHOCK) normal 0-1.0 mm/s, warning 4.0, alarm 10.0. A 5th-octave chatter spike points to roll chatter.",
         ["spine:HSM.STD.R1/JSR.HR.R1.WR.VIB.CHOCK", "RCA-022-HSM-STD-R1-roll-chatter.md"], [T_THRESH]),
        ("What strip-crown deviation is out of tolerance on R1?",
         "Strip-crown deviation (JSR.HR.R1.CROWN.DEV) normal -10 to +10 um, warning 25, alarm 40. Excess crown loss points to thermal camber loss / roll wear.",
         ["spine:HSM.STD.R1/JSR.HR.R1.CROWN.DEV"], [T_THRESH]),
        ("What belt-edge position warns of conveyor misalignment?",
         "Belt-edge position (JSR.RM.CONV1.BELT.EDGE) normal -15 to +15 mm, warning 25, alarm 50. Off-track belt risks spillage and edge damage; fit a training idler (IDLER-TRAIN-01).",
         ["spine:RM.CONV.ORE01/JSR.RM.CONV1.BELT.EDGE", "spine:spare/IDLER-TRAIN-01"], [T_THRESH, T_SPARE]),
        ("What drive-motor current indicates conveyor overload?",
         "Drive-motor current (JSR.RM.CONV1.MTR.CURR) normal 60-95 %FLA, warning 105, alarm 125. Above 105% suggests a blocked chute or belt overload.",
         ["spine:RM.CONV.ORE01/JSR.RM.CONV1.MTR.CURR"], [T_THRESH]),
        ("What shell IR temperature indicates refractory burnout on the furnace?",
         "Shell surface IR temp (JSR.RHF.Z3.SHELL.IR) normal 80-120 degC, warning 180, alarm 250. A localized hot spot above 180 degC indicates refractory thinning/burnout.",
         ["spine:RHF.ZONE.SOAK/JSR.RHF.Z3.SHELL.IR", "RCA-024-RHF-ZONE-SOAK-refractory-hotspot.md"], [T_THRESH]),
        ("What oil temperature is too high on the EAF hydraulic power unit?",
         "EAF HPU oil temp (JSR.MS.EAF1.HYD.OIL.TEMP) normal 40-50 degC, warning 60, alarm 70. High oil temp points to a cooler fault (replace COOL-CORE-01).",
         ["spine:EAF.AUX.HYD01/JSR.MS.EAF1.HYD.OIL.TEMP", "spine:spare/COOL-CORE-01"], [T_THRESH, T_SPARE]),
        ("What oil-film bearing outlet temperature warns on the F3 work roll?",
         "Oil-film bearing outlet temp (JSR.HR.STD3.WR.BRG01.OFB.OUT.TEMP) normal 50-65 degC, warning 75, alarm 85. Rising outlet temp indicates oil-film breakdown / lube starvation.",
         ["spine:HSM.F3.WR.BRG01/JSR.HR.STD3.WR.BRG01.OFB.OUT.TEMP", "RCA-013-HSM-F3-WR-BRG01-lube-starvation.md"], [T_THRESH]),
        ("What motor body vibration alarms on the F1 main motor?",
         "Motor body vibration (JSR.HR.STD1.MTR01.VIB.DE.RMS) normal 0.5-2.3 mm/s, warning 4.5, alarm 7.1 (ISO 20816-1:2016 Group 2).",
         ["spine:HSM.F1.MTR01/JSR.HR.STD1.MTR01.VIB.DE.RMS"], [T_THRESH]),
        ("What 2x-supply-frequency vibration indicates rotor eccentricity on the F1 motor?",
         "2x supply-frequency vibration (JSR.HR.STD1.MTR01.VIB.2XF1) normal 0.0-0.5 mm/s, warning 1.0, alarm 2.5 (IEEE 1415-2006 eccentricity).",
         ["spine:HSM.F1.MTR01/JSR.HR.STD1.MTR01.VIB.2XF1"], [T_THRESH]),
        ("What roll-bearing vibration alarms on caster segment 7?",
         "Roll-bearing vibration (JSR.CC1.SEG07.VIB.ROLL) normal 0.5-2.0 mm/s, warning 3.5, alarm 6.0.",
         ["spine:CCM.SEG.07/JSR.CC1.SEG07.VIB.ROLL"], [T_THRESH]),
        ("What roll-journal AE alarms on roughing stand R1?",
         "Roll-journal AE RMS (JSR.HR.R1.WR.AE.RMS) normal -3 to +3 dB, warning 8, alarm 15.",
         ["spine:HSM.STD.R1/JSR.HR.R1.WR.AE.RMS"], [T_THRESH]),
        ("What bearing temperature alarms on the descale pump?",
         "Descale-pump bearing temp (JSR.HR.DSC.PMP01.TEMP.BRG) normal 40-70 degC, warning 85, alarm 100 (ISO 15243:2017).",
         ["spine:HSM.DSC.PMP01/JSR.HR.DSC.PMP01.TEMP.BRG"], [T_THRESH]),
        ("What 1x vibration alarms on the BF turbo-blower?",
         "1x vibration RMS (JSR.BF.BLW.FAN01.VIB.1X) normal 1.0-2.3 mm/s, warning 4.5, alarm 7.1 (ISO 10816-3:2009 Group 3).",
         ["spine:BF.BLW.FAN01/JSR.BF.BLW.FAN01.VIB.1X"], [T_THRESH]),
        ("What bearing temperature alarms on the BF turbo-blower?",
         "Blower bearing outer-ring temp (JSR.BF.BLW.FAN01.TEMP.BRG) normal 45-65 degC, warning 80, alarm 95 (ISO 15243:2017 sec8).",
         ["spine:BF.BLW.FAN01/JSR.BF.BLW.FAN01.TEMP.BRG"], [T_THRESH]),
        ("What broadband vibration indicates seal trouble on the BF cooling-water pump?",
         "Broadband vibration (JSR.BF.CW.PMP02.VIB.BB) normal 0.5-1.5 mm/s, warning 2.5, alarm 5.0 (ISO 10816-7:2009 seal).",
         ["spine:BF.CW.PMP02/JSR.BF.CW.PMP02.VIB.BB"], [T_THRESH]),
        ("What bearing temperature alarms on the BF cooling-water pump?",
         "Bearing temp (JSR.BF.CW.PMP02.TEMP.BRG) normal 40-70 degC, warning 85, alarm 100 (ISO 15243:2017).",
         ["spine:BF.CW.PMP02/JSR.BF.CW.PMP02.TEMP.BRG"], [T_THRESH]),
        ("What bearing temperature alarms on the sinter main fan?",
         "Sinter-fan bearing temp (JSR.SP.FAN01.TEMP.BRG) normal 45-65 degC, warning 80, alarm 95 (ISO 15243:2017 sec8).",
         ["spine:SP.SINT.FAN01/JSR.SP.FAN01.TEMP.BRG", "RCA-020-SP-SINT-FAN01-bearing-overheat.md"], [T_THRESH]),
    ]
    for query, ans, refs, tools in extra:
        q(query, ans, refs, tools)

add_more_thresholds()

# A few cross-asset / agentic queries
q("List all assets that can suffer a mechanical-seal or impeller failure.",
  "The cooling_descaling_pump class assets - HSM.DSC.PMP01 (descale pump) and BF.CW.PMP02 (BF cooling-water pump) - have mechanical_seal_failure and impeller_wear_erosion failure modes. Spares SEAL-MECH-DSC, IMP-DSC-01, IMP-CW-01, WRING-CW-01 fit this class.",
  ["spine:asset_registry", "spine:spare_parts_master"], [T_ASSET, T_SPARE])

q("Which failures in this plant are safety class P1?",
  "P1 (highest) failures: compressor surge on the BF blower (SCN-041), caster breakout/sticking (SCN-043), conveyor idler-bearing seizure/belt-fire (SCN-045), and ladle-crane wire-rope failure (SCN-047). All carry catastrophic safety or massive cost potential.",
  ["spine:failure_scenario_catalog"], [T_KB])

q("What is the target failure rate for the generated dataset and why?",
  "Row-level failure rate must land in 0.5-5% (the sweet spot per domain quality Dimension 4). 15-40% is over-collected/warning, and >40% is unrealistic for synthetic data. The 12 failure archetypes (25% of the catalog) are a design ratio, not the row-level label rate.",
  ["spine:generation_contract"], [T_KB])

q("Which spares fit more than one equipment class?",
  "BRG-LRG-300 fits rolling_mill_work_roll_bearing + bf_sinter_fan_blower; SEAL-LAB-01 fits work-roll bearing + large_induction_motor_vfd; CPL-EL-01 fits work-roll bearing + mill_gearbox; ROLL-SEG-STD fits caster_segment + caster_mould; FLT-HYD-10 and KID-LOOP-01 fit eaf_bof_auxiliary + hydraulics_agc_servo.",
  ["spine:spare_parts_master"], [T_SPARE])

q("Is this dataset real Tata Steel plant data?",
  "No. It is SYNTHETIC but physics-grounded: all numeric values are representative industry estimates derived from cited standards (ISA-95, ISO 14224, ISO 10816/20816, ISO 15243, ISO 4406:2021, NEMA MG1, IEEE 43/1415, API 670, ISA-18.2) and the research briefs. Site-specific baseline calibration is mandatory before production. No proprietary Tata Steel data is used.",
  ["spine:disclaimer"], [T_KB])

# ---- Degradation-timeline / RUL / lead-indicator questions ------------------
q("How long does the F3 work-roll bearing take to go from first warning to failure?",
  "Per the SCN-037 RTF timeline: healthy weeks 0-6; AE crosses its 6 dBuV warning at weeks 6-8 (no vibration change yet); envelope BPFO climbs 1.0->3.0 g with temp drift over weeks 8-10; then all three sensors alarm and failure follows within hours. So roughly a 4-week actionable window from first AE warning.",
  ["spine:SCN-037/degradation_timeline"], [T_TREND, T_DIAG])

q("What is the warning-to-failure window for a broken rotor bar on the F1 motor?",
  "SCN-039: healthy weeks 0-3, MCSA sideband moves -50->-45 dBc at weeks 3-4 (warning), then -35 dBc with 2x-slip vibration at alarm; progressive bar cracking takes a further 2-4 weeks to failure. This gives a multi-week planning window to swap to the insurance spare.",
  ["spine:SCN-039/degradation_timeline"], [T_TREND, T_DIAG])

q("How much warning does the caster breakout-prediction system give before shell rupture?",
  "Very little - the SCN-043 timeline shows shell rupture roughly 60-90 seconds after the BPS breakout alarm. That is why the response (drop to 0.5 m/min, then emergency stop + evacuate) must be immediate and why 3-sensor confirmation logic is pre-tuned to minimise false alarms.",
  ["spine:SCN-043/degradation_timeline"], [T_DIAG, T_KB])

q("How fast can a compressor surge destroy the BF blower?",
  "Seconds, if sustained. SCN-041's timeline: warning = ASV cycling / surge margin <8%; alarm = discharge oscillation >8% + axial vibration burst; failure = seconds to destruction if surge continues. That is why the rule is trip immediately if surge persists beyond 2-3 cycles.",
  ["spine:SCN-041/degradation_timeline"], [T_DIAG])

q("Which single sensor gives the earliest warning of a conveyor idler-bearing failure?",
  "Idler ultrasound level (JSR.RM.CONV1.IDLER.US). In SCN-045 it rises +8 dBuV (warning) before idler surface temperature climbs to the 80/100 degC range. Ultrasound is the lead indicator; temperature confirms and signals imminent fire risk.",
  ["spine:SCN-045/degradation_timeline", "spine:RM.CONV.ORE01/JSR.RM.CONV1.IDLER.US"], [T_TREND, T_DIAG])

q("Why can't a single thermocouple confirm a caster breakout on its own?",
  "A single mould thermocouple has a >40% false-alarm rate. SCN-043 requires 3-sensor agreement - TC V-pattern (delta >50 degC) AND oscillator friction spike (>18 kN) AND mould-level wave (>12 mm) - before declaring a true sticking breakout. This is the core anti-false-alarm design of the BPS.",
  ["spine:SCN-043/root_cause", "spine:SCN-043/sensor_signature"], [T_DIAG, T_KB])

# ---- Mixed-input-context / agentic multi-tool questions ---------------------
q("Pull the latest readings for the F1 gearbox and tell me if it's healthy.",
  "Reading JSR.HR.STD1.GBX01.VIB.GMF.RMS, OIL.TEMP, OIL.FE.PPM and OIL.PRES against thresholds: if GMF <6 mm/s, oil temp <80 degC, Fe <15 ppm and pressure >2.2 bar, the gearbox is in its normal band (baseline GMF 2.8, oil 56 degC, Fe 3 ppm = SCN-002 healthy). Flag if GMF approaches 6 (warn)/10 (alarm), Fe approaches 15/40, or pressure falls toward 2.2/2.0.",
  ["spine:SCN-002", "spine:HSM.F1.GBX01"], [T_SENSOR, T_THRESH, T_DIAG])

q("Show me all active alerts and rank them by safety class.",
  "Query the active-alert feed, then rank by safety_class P1>P2>P3>P4. P1 events (compressor surge SCN-041, caster breakout SCN-043, conveyor idler fire SCN-045, ladle-crane wire-rope SCN-047) come first as life-safety/catastrophic, then P2 (bearing spall, gear crack, roll seizure/spall, burner, servo silting), then P3 (seal failure, broken rotor bar), then P4 (healthy).",
  ["spine:failure_scenario_catalog"], [T_ALERT, T_DIAG, T_KB])

q("The descale pump tripped overnight - investigate and tell me what happened.",
  "Pull the trend history for JSR.HR.DSC.PMP01 sensors around the trip. If casing vibration spiked toward 5.0+ mm/s with bearing temp >85 degC = mechanical seal failure (SCN-040). If suction pressure fell to ~70 kPa with AE broadband at 15 dB = cavitation/NPSH starvation (SCN-040 cavitation variant). Cross-check the work-order history and the relevant RCA before concluding.",
  ["spine:SCN-040", "RCA-004-HSM-DSC-PMP01-mechanical-seal.md", "RCA-016-HSM-DSC-PMP01-cavitation.md"], [T_TREND, T_HIST, T_DIAG, T_RCA])

q("Estimate the cost if we defer the F1 gearbox repair to the next shutdown and it fails first.",
  "A planned gearbox intervention avoids the SCN-038 unplanned event: ~USD 600k (range 500k-3M) and ~168h downtime, dominated by the 36-week lead on the GEAR-WHL-M20 gear wheel (0 stock). Deferring past a developing tooth crack risks tooth fracture and shaft damage, so the deferral exposure is the full unplanned figure plus secondary shaft repair.",
  ["spine:SCN-038/cost_impact", "spine:spare/GEAR-WHL-M20"], [T_COST, T_SPARE])

q("Which open work orders are blocked on long-lead spares?",
  "Cross-reference open work orders against spare lead times. The long-lead blockers are GEAR-WHL-M20 (36wk), MTR-MV-6000 (40wk), MOLD-CU-STD (14wk), ASV-VLV-01 / BRG-JRNL-PAD / BRG-THRUST-PAD / FAN-BLADE-SET / ROLL-SEG-STD (12wk), BELT-SEC-1600 (10wk), SERVO-VLV-D661 (10wk).",
  ["spine:spare_parts_master"], [T_HIST, T_SPARE])

q("Create a work order for the F3 work-roll bearing change and attach the SOP and parts.",
  "I can draft a CMMS work order for HSM.F3.WR.BRG01: task = bearing replacement per SOP-01; parts = BRG-LRG-300 (stock 1), SEAL-LAB-01 (stock 2), CPL-EL-01 (stock 1); estimated planned downtime 5h. Confirmation required before any CMMS write (Tier-3 action).",
  ["spine:SCN-037/correct_resolution", "spine:SCN-037/spares_required", "SOP-01_bearing-replacement.md"], [T_WO, T_SOP, T_SPARE])

q("Run the diagnostic model on the BF cooling-water pump and explain the output.",
  "The model reads JSR.BF.CW.PMP02 sensors: differential head deviation, 1x radial vibration, broadband vibration and bearing temp. A negative head deviation (toward -12%) with 1x vibration toward 5.6 mm/s indicates impeller/wear-ring erosion; rising broadband vibration alone points to seal trouble; high bearing temp points to a bearing/lube fault. The classifier outputs the most likely mode with the contributing sensors.",
  ["spine:BF.CW.PMP02"], [T_DIAG, T_SENSOR])

# ---- Cross-asset / portfolio / planning questions ---------------------------
q("Which assets share the large-bore roller bearing spare and what's the stocking risk?",
  "BRG-LRG-300 (>300mm roller bearing) fits both rolling_mill_work_roll_bearing (HSM.F3.WR.BRG01) and bf_sinter_fan_blower (BF.BLW.FAN01, SP.SINT.FAN01). Stock is only 1 with an 8-week lead, so a simultaneous bearing event on two of those critical assets would stock out - consider raising min stock.",
  ["spine:spare/BRG-LRG-300", "spine:asset_registry"], [T_SPARE, T_ASSET])

q("List every criticality-1 asset in the plant.",
  "Criticality-1 assets: HSM.F3.WR.BRG01, HSM.F1.GBX01, HSM.F1.MTR01 (hot rolling); BF.BLW.FAN01, BF.CW.PMP02 (blast furnace); CCM.SEG.07, CCM.MOLD.01 (casting); HSM.STD.R1 (roughing stand); SP.SINT.FAN01 (sinter plant); MS.LDC.CRN01 (ladle crane); CRM.AGC.SV01 (cold mill AGC). The descale pump (HSM.DSC.PMP01), ore conveyor (RM.CONV.ORE01) and reheat furnace (RHF.ZONE.SOAK) are criticality 2.",
  ["spine:asset_registry"], [T_ASSET])

q("Which failure modes can the F1 main motor exhibit?",
  "HSM.F1.MTR01 failure modes: broken_rotor_bar, stator_winding_turn_short, insulation_degradation_ground_fault, rotor_eccentricity, winding_overheat, and motor_bearing_spall_BPFO. Each maps to a distinct sensor (MCSA sideband, winding temp + current imbalance, PI, 2x supply-freq vibration, and body vibration respectively).",
  ["spine:HSM.F1.MTR01/failure_modes", "spine:HSM.F1.MTR01"], [T_ASSET, T_KB])

q("Which two pumps in the plant are the same equipment class and how do their duties differ?",
  "HSM.DSC.PMP01 (HP descaling pump, KSB Multitec, 1200 kW, ~200 bar service) and BF.CW.PMP02 (BF cooling-water pump, KSB Omega double-suction, 900 kW) are both class cooling_descaling_pump. The descaler is high-pressure scale-removal duty; the BF pump is high-flow cooling-water circulation. They share seal/impeller/wear-ring spares.",
  ["spine:HSM.DSC.PMP01", "spine:BF.CW.PMP02"], [T_ASSET])

q("What is the most expensive single failure event modelled in this plant?",
  "Compressor surge on the BF turbo-blower (SCN-041): ~USD 6,000,000 point estimate, range USD 4-8M, INR 500,000,000, with BF downtime around USD 500k/hr. It is the highest-cost and a P1 safety-class event.",
  ["spine:SCN-041/cost_impact"], [T_COST])

q("Which failures are catchable early enough to plan, and which are effectively sudden?",
  "Plannable (multi-day/week RTF): bearing spall (SCN-037, ~4wk from AE warning), gear crack (SCN-038, weeks), broken rotor bar (SCN-039, 2-4wk), seal failure (SCN-040, weeks), wire-rope fatigue (SCN-047, months). Effectively sudden (seconds-to-minutes): compressor surge (SCN-041) and caster breakout (SCN-043, 60-90s). Roll seizure (SCN-042) and idler fire (SCN-045) escalate within minutes-to-hours.",
  ["spine:failure_scenario_catalog"], [T_DIAG, T_KB])

q("What standards govern the wire-rope discard decision on the ladle crane?",
  "ISO 4309:2017 governs discard: the metrics are MFL/LMA (loss of metallic area), random broken-wire count per lay length, and rope-diameter reduction. The crane load thresholds use FEM 1.001 / BS EN 13135 with a stricter molten-metal ladle-crane profile (alarm 95% WLL, cut power 110%).",
  ["spine:MS.LDC.CRN01/JSR.MS.CRN01.ROPE.MFL", "spine:MS.LDC.CRN01/JSR.MS.CRN01.LOAD.SWL"], [T_KB, T_THRESH])

q("Why is the AGC servo oil cleanliness target stricter than the EAF hydraulic unit's?",
  "The Moog D661 servo spool has a 1-3 um annular clearance, so it needs ISO <=15/13/10. The EAF HPU is a coarser power unit, so ISO <=17/15/12 is acceptable. Silt that a power unit tolerates will plug a servo spool, which is exactly the SCN-048 silting failure.",
  ["spine:CRM.AGC.SV01/JSR.CR.S2.AGC.SV.ISO4406", "spine:EAF.AUX.HYD01/JSR.MS.EAF1.HYD.ISO4406", "spine:SCN-048"], [T_THRESH, T_KB])

q("If both the descale pump seal and the BF cooling pump impeller fail in the same week, can we cover the spares?",
  "Yes for the seal: SEAL-MECH-DSC has stock 2 (2-week lead). For the BF pump: IMP-CW-01 has stock 1 (6-week) and WRING-CW-01 stock 2 (4-week) - one impeller event is covered, a second concurrent impeller event would stock out. Both jobs can proceed on shelf stock for a single event each.",
  ["spine:spare/SEAL-MECH-DSC", "spine:spare/IMP-CW-01", "spine:spare/WRING-CW-01"], [T_SPARE])

q("What's the difference between the warning and alarm response for a bearing temperature?",
  "Per Playbook 01: in the warning/Zone-C band (e.g. bearing temp 85-95 degC) derate load ~30%, increase lube, and schedule inspection within ~4h - do not trip. In the alarm/Zone-D band (temp >95-100 degC or vibration in Zone D) initiate a controlled shutdown; only emergency-trip if fire/smoke is present, since a sudden trip can cause secondary thermal-shock damage.",
  ["19_repair_playbooks.md", "spine:HSM.F3.WR.BRG01/JSR.HR.STD3.WR.BRG01.TEMP.DE"], [T_KB, T_THRESH])

q("Give me the asset summary for the cold-rolling AGC servo valve.",
  "CRM.AGC.SV01 is a Moog D661 servo valve in the cold rolling mill stand-2 AGC hydraulic screwdown circuit, criticality 1, installed 2020-01-30, last overhaul 2024-09-14. Monitored by oil cleanliness (ISO4406), position error, null leakage and strip-gauge deviation. Failure modes: servo silting/spool wear, hysteresis increase, oil contamination.",
  ["spine:CRM.AGC.SV01"], [T_ASSET])

q("What sensors monitor the continuous caster mould and what do they detect?",
  "CCM.MOLD.01 sensors: adjacent-TC delta (V-pattern cold-spot / breakout precursor), oscillator friction force (sticking friction spike), mould-level deviation (level instability), and mean mould heat flux (copper-plate wear / sticking, lower is worse). Together they drive the breakout-prediction system.",
  ["spine:CCM.MOLD.01"], [T_ASSET, T_KB])

q("How do I tell a work-roll spall apart from roll chatter on R1?",
  "A work-roll spall (SCN-044) prints once per roll revolution - periodic force ripple at 1x roll (period = pi*D) with periodic strip marks. Roll chatter is regenerative self-excited vibration in a high-frequency band (5th-octave) on the chock, NOT locked to 1x roll. Spall needs a roll change/grind; chatter needs speed/tension/eccentricity tuning.",
  ["spine:SCN-044", "RCA-022-HSM-STD-R1-roll-chatter.md"], [T_DIAG, T_KB])

q("What does a rising flue-gas O2 with a falling flame signal mean on the reheat furnace?",
  "It means a fuel-side burner failure (SCN-046): the flame is unstable/failing (signal falling toward the 40% cutoff) so fuel is not burning completely, leaving excess O2 in the flue (rising toward the 5.0% high warning / 6.0% alarm). Auto fuel cutoff fires below 40% flame signal; purge before re-light.",
  ["spine:SCN-046/sensor_signature"], [T_DIAG, T_KB])

q("Which spares should be reviewed as insurance spares because of catastrophic-event lead time?",
  "GEAR-WHL-M20 (36wk, drives the USD 600k+ gearbox event) and MTR-MV-6000 (40wk - already held as a single insurance spare). The 12-week blower items (ASV-VLV-01, BRG-JRNL-PAD, BRG-THRUST-PAD, FAN-BLADE-SET) back the USD 4-8M surge event and the 14-week MOLD-CU-STD backs the breakout event - all candidates for higher min-stock review.",
  ["spine:spare_parts_master", "spine:SCN-038/cost_impact", "spine:SCN-041/cost_impact"], [T_SPARE, T_COST])

q("What standards backbone does this whole dataset follow?",
  "ISA-95 (asset/tag hierarchy), ISO 14224 (failure taxonomy), ISO 10816-3:2009 / ISO 20816-3:2022 (vibration zones), ISO 15243:2017 (rolling-bearing failure modes), ISO 4406:2021 (oil cleanliness), NEMA MG1-2021 / IEC 60034-1 (motors), IEEE 43-2013 / 1415-2006 (insulation, MCSA), API 670:2014 (machinery protection), and ISA-18.2-2016 (alarm priority tiers).",
  ["spine:standards_backbone"], [T_KB])

q("How does the tag naming convention work for this plant's sensors?",
  "Tags follow an ISA-95 style site.area.unit.equipment.measurement hierarchy, e.g. JSR.HR.STD3.WR.BRG01.VIB.DE.H.RMS = site JSR (Jamshedpur), area HR (hot rolling), STD3 (finishing stand 3), WR.BRG01 (work-roll bearing 1), VIB.DE.H.RMS (horizontal drive-end vibration velocity RMS). The suffix encodes the quantity and measurement point.",
  ["spine:HSM.F3.WR.BRG01", "17_common_sensors_placement_scada.md"], [T_KB, T_ASSET])


# ---------------------------------------------------------------------------
# (B) troubleshooting_prompts.jsonl  -- scenario-based diagnostic chains
# ---------------------------------------------------------------------------

def tprompt(prompt, asset_id, scn_id, reasoning_chain, diagnosis, resolution, parts, lead, refs, tools,
            cost=None, downtime=None, safety=None, cost_basis_note=None, mode=None):
    """Build a troubleshooting record.

    By default the failure_mode + cost/downtime/safety block are inherited from the
    parent spine scenario `scn_id`. For SIBLING failure modes (modes that share an
    asset with one of the 12 spine FAILURE archetypes but are NOT that archetype),
    pass explicit `mode` + `cost`/`downtime`/`safety` so the labelled mode AND its
    economics describe the ACTUAL mode, not the parent event-class. `cost_basis_note`
    records the grounding for the override.
    """
    scn = scenarios[scn_id]
    rec = {
        "prompt": prompt,
        "asset_id": asset_id,
        "scenario_id": scn_id,
        "failure_mode": mode if mode is not None else scn["failure_mode"],
        "safety_class": safety if safety is not None else scn["safety_class"],
        "diagnostic_reasoning_chain": reasoning_chain,
        "diagnosis": diagnosis,
        "correct_resolution": resolution,
        "parts_required": parts,
        "lead_time": lead,
        "downtime_hours": downtime if downtime is not None else scn["downtime_hours"],
        "cost_impact": dict(cost) if cost is not None else scn["cost_impact"],
        "grounding_refs": refs,
        "expected_tools": tools,
    }
    if cost_basis_note is not None:
        rec["cost_impact"]["note"] = cost_basis_note
    ts.append(rec)

# Helper to build a parts list with live lead times from the spare master
def parts_for(scn_id):
    out = []
    for p in scenarios[scn_id]["spares_required"]:
        sp = spares.get(p["part_id"])
        if sp:
            out.append({"part_id": p["part_id"], "name": p["name"],
                        "stock_qty": sp["stock_qty"], "lead_time_weeks": sp["lead_time_weeks"],
                        "unit_cost_usd": sp["unit_cost"]["usd"]})
        else:
            out.append({"part_id": p["part_id"], "name": p["name"]})
    return out

def lead_summary(scn_id):
    items = []
    for p in scenarios[scn_id]["spares_required"]:
        sp = spares.get(p["part_id"])
        if sp:
            items.append(f"{p['part_id']} {sp['lead_time_weeks']}wk (stock {sp['stock_qty']})")
    return "; ".join(items)

# SCN-037 bearing spall
tprompt(
  "F3 work-roll bearing JSR.HR.STD3.WR.BRG01: AE RMS rose from 0 to 8 dBuV over two weeks, envelope BPFO now 3.2 g, bearing temp 102 degC. Diagnose and advise.",
  "HSM.F3.WR.BRG01", "SCN-037",
  ["AE RMS crossed warning (6) first - leading indicator of bearing surface distress (RCA-001).",
   "Envelope BPFO 3.2 g is above the 3.0 g alarm -> energy at the outer-race ball-pass frequency = outer-race spall (ISO 15243).",
   "Bearing temp 102 degC exceeds the 100 degC trip -> stage-4, friction heating from advanced spall.",
   "Three-sensor agreement (AE -> BPFO -> temp) over weeks matches the SCN-037 RTF signature, not a transient."],
  "Outer-race rolling-contact fatigue spall (BPFO), advanced (stage 4). Root cause: subsurface fatigue accelerated by lube contamination.",
  scenarios["SCN-037"]["correct_resolution"],
  parts_for("SCN-037"), lead_summary("SCN-037"),
  ["spine:SCN-037", "RCA-001-HSM-F3-WR-BRG01-BPFO-spall.md", "SOP-01_bearing-replacement.md", "MAN-001_rolling_mill_work_roll_bearing.md"],
  [T_SENSOR, T_TREND, T_DIAG, T_RCA, T_SOP, T_SPARE])

# SCN-038 gearbox tooth fatigue
tprompt(
  "F1 gearbox JSR.HR.STD1.GBX01: GMF-band vibration jumped to 11 mm/s, oil ferrous count at 60 ppm, chip detector tripped. What is wrong and what do I do?",
  "HSM.F1.GBX01", "SCN-038",
  ["GMF vibration 11 mm/s is above the 10 mm/s alarm -> gross gear-mesh fault.",
   "Ferrous count 60 ppm vs 40 ppm alarm + chip-detector trip -> chunky spall debris, active metal loss (ASTM D5185).",
   "Combined GMF + chip + Fe ppm = tooth-root fatigue crack producing chunky spall (RCA-002), often after a high-torque cobble.",
   "Risk: tooth fracture can damage the shaft - no deferral permitted."],
  "Gear-tooth fatigue crack with active spalling. Immediate controlled stop required.",
  scenarios["SCN-038"]["correct_resolution"],
  parts_for("SCN-038"), lead_summary("SCN-038") + " - NOTE: GEAR-WHL-M20 is 0 stock / 36-week lead, the critical-path item",
  ["spine:SCN-038", "RCA-002-HSM-F1-GBX01-gear-tooth-fatigue.md", "SOP-02_gearbox-oil-gear-service.md", "spine:spare/GEAR-WHL-M20"],
  [T_SENSOR, T_DIAG, T_RCA, T_SOP, T_SPARE, T_COST])

# SCN-039 broken rotor bar
tprompt(
  "F1 main motor JSR.HR.STD1.MTR01: MCSA rotor-bar sideband at -34 dBc, body vibration 4.8 mm/s. Diagnose and give the action plan.",
  "HSM.F1.MTR01", "SCN-039",
  ["MCSA sideband -34 dBc is past the -35 dBc alarm -> broken rotor bar(s) at (1+/-2s)*f1 sidebands (IEEE 1415).",
   "Body vibration 4.8 mm/s above 4.5 warning -> 2x-slip modulation consistent with broken bar.",
   "Pattern matches SCN-039 RTF (sideband -50->-45->-35 over weeks), confirming progressive bar cracking (RCA-003).",
   "Not an instantaneous failure - 2-4 week window to plan a swap."],
  "Broken rotor bar, progressing. Plan a controlled motor swap within 2-4 weeks.",
  scenarios["SCN-039"]["correct_resolution"],
  parts_for("SCN-039"), lead_summary("SCN-039") + " - use the on-shelf insurance spare; do NOT order new (40wk lead)",
  ["spine:SCN-039", "RCA-003-HSM-F1-MTR01-broken-rotor-bar.md", "SOP-03_motor-rewind-swap.md", "spine:spare/MTR-MV-6000"],
  [T_DIAG, T_TREND, T_RCA, T_SOP, T_SPARE])

# SCN-040 mechanical seal
tprompt(
  "Descale pump JSR.HR.DSC.PMP01: casing vibration climbing to 5.4 mm/s, bearing temp 90 degC, visible spraying leak at the seal. Diagnose.",
  "HSM.DSC.PMP01", "SCN-040",
  ["Casing vibration 5.4 mm/s above 5.0 alarm + bearing temp 90 degC above 85 warning.",
   "Progression from weeping to spraying leak matches the seal-failure RTF (RCA-004).",
   "Abrasive scale-laden water wears the SiC seal faces; secondary O-ring degradation.",
   "Standby pump available -> no need for emergency stop."],
  "Mechanical seal face failure from abrasive scale-laden water.",
  scenarios["SCN-040"]["correct_resolution"],
  parts_for("SCN-040"), lead_summary("SCN-040"),
  ["spine:SCN-040", "RCA-004-HSM-DSC-PMP01-mechanical-seal.md", "SOP-04_pump-mechanical-seal.md"],
  [T_SENSOR, T_DIAG, T_RCA, T_SOP, T_SPARE])

# SCN-041 surge
tprompt(
  "BF turbo-blower JSR.BF.BLW.FAN01: discharge pressure oscillation 9%, shaft displacement 95 um, ASV cycling. Emergency? What do I do?",
  "BF.BLW.FAN01", "SCN-041",
  ["Pressure oscillation 9% above 8% surge alarm + shaft displacement 95 um (above 80 warning, below 127 alarm) = active surge.",
   "ASV cycling + operating point left of surge line (valve slam / inlet filter fouling) per RCA-005.",
   "Surge can destroy the machine in seconds if sustained - P1.",
   "BF downtime ~$500k/hr makes this the highest-cost event in the plant."],
  "Compressor surge - imminent catastrophic risk. Verify ASV opened; trip if it persists.",
  scenarios["SCN-041"]["correct_resolution"],
  parts_for("SCN-041"), lead_summary("SCN-041") + " - ASV-VLV-01 and journal pads are 12-week, 0-1 stock; expedite",
  ["spine:SCN-041", "RCA-005-BF-BLW-FAN01-compressor-surge.md", "MAN-005_bf_sinter_fan_blower.md"],
  [T_SENSOR, T_DIAG, T_RCA, T_COST])

# SCN-042 roll seizure
tprompt(
  "Caster segment 7 JSR.CC1.SEG07: roll rpm dropped to 0, clamping force 540 kN. Diagnose and advise (cast in progress).",
  "CCM.SEG.07", "SCN-042",
  ["Roll rpm 0 (alarm at 0) = roll no longer rotating = seizure.",
   "Clamping force 540 kN above 480 warning approaching 550 alarm -> the seized roll is dragging the strand.",
   "Thermal/water-scale ingress seized the roll bearing (RCA-006).",
   "Risk: transverse slab cracks and breakout if not managed -> P2 but can escalate."],
  "Roll-bearing seizure on segment 7.",
  scenarios["SCN-042"]["correct_resolution"],
  parts_for("SCN-042"), lead_summary("SCN-042"),
  ["spine:SCN-042", "RCA-006-CCM-SEG07-roll-seizure.md", "SOP-06_caster-segment-change.md"],
  [T_SENSOR, T_DIAG, T_RCA, T_SOP, T_SPARE])

# SCN-043 breakout
tprompt(
  "Caster mould CCM.MOLD.01: TC delta 55 degC in a downward-propagating V-pattern, oscillator friction 19 kN, mould-level deviation 13 mm. BPS just alarmed P1. What now?",
  "CCM.MOLD.01", "SCN-043",
  ["TC delta 55 degC above 50 alarm, V-pattern propagating downward = shell sticking cold spot.",
   "Oscillator friction 19 kN above 18 alarm + level deviation 13 mm above 12 alarm.",
   "All THREE sensors agree -> true sticking breakout (single sensor has >40% FAR), confirming the BPS P1 alarm (RCA-007).",
   "Shell will rupture ~60-90s after the BPS alarm if unaddressed - liquid steel hazard."],
  "Sticking breakout in progress (3-sensor confirmed). P1 life-safety event.",
  scenarios["SCN-043"]["correct_resolution"],
  parts_for("SCN-043"), lead_summary("SCN-043") + " - MOLD-CU-STD 14wk lead is the long pole",
  ["spine:SCN-043", "RCA-007-CCM-MOLD01-breakout-sticking.md", "SOP-07_mould-copper-change.md"],
  [T_SENSOR, T_DIAG, T_RCA, T_SOP])

# SCN-044 work-roll spall
tprompt(
  "Roughing stand R1 JSR.HR.R1.FORCE: rolling-force ripple at 8.5% periodic at 1x roll, chock vibration 6 mm/s, periodic marks on strip. Diagnose.",
  "HSM.STD.R1", "SCN-044",
  ["Force ripple 8.5% above 8% alarm, periodic at 1x roll (period = pi*D) = a defect printing once per roll revolution.",
   "Chock vibration 6 mm/s above 4 warning + periodic strip surface marks confirm a work-roll spall flat (RCA-008).",
   "Likely a subsurface defect activated by a cobble/thermal shock.",
   "Risk: spall fragment ejection -> quick-change is far cheaper than running to failure (16.4x)."],
  "Work-roll spall flat on R1.",
  scenarios["SCN-044"]["correct_resolution"],
  parts_for("SCN-044"), lead_summary("SCN-044") + " - WR-HSS-PREP on shelf enables 15-45min change",
  ["spine:SCN-044", "RCA-008-HSM-STD-R1-work-roll-spall.md", "SOP-08_hot-strip-mill-roll-change.md"],
  [T_SENSOR, T_DIAG, T_RCA, T_SOP, T_SPARE, T_COST])

# SCN-045 idler
tprompt(
  "Ore conveyor JSR.RM.CONV1: idler ultrasound +16 dBuV, idler surface temp 100 degC. Diagnose - is this urgent?",
  "RM.CONV.ORE01", "SCN-045",
  ["Ultrasound +16 dBuV above +15 alarm = bearing friction noise.",
   "Idler temp 100 degC at the fire-risk alarm threshold.",
   "Dry/failed idler bearing seizing under the loaded belt = #1 belt-fire initiator (RCA-009).",
   "P1 - belt fire risk, act immediately."],
  "Idler-bearing seizure at fire-risk threshold. Stop belt now.",
  scenarios["SCN-045"]["correct_resolution"],
  parts_for("SCN-045"), lead_summary("SCN-045") + " - IDLER-STD-1600 on shelf (40 in stock)",
  ["spine:SCN-045", "RCA-009-RM-CONV-ORE01-idler-bearing.md", "SOP-09_conveyor-idler-belt.md"],
  [T_SENSOR, T_DIAG, T_RCA, T_SOP, T_SPARE])

# SCN-046 burner
tprompt(
  "Reheat furnace soak zone JSR.RHF.Z3: flame scanner signal dropped to 38%, flue O2 risen to 5.8%. Diagnose and advise.",
  "RHF.ZONE.SOAK", "SCN-046",
  ["Flame signal 38% below the 40% cutoff -> auto fuel cutoff fires (lower is worse).",
   "Flue O2 5.8% near 6.0 alarm = excess air / unburnt fuel from an unstable flame.",
   "Burner nozzle fouling or gas-supply fluctuation (EN 746-2) per RCA-010.",
   "Safety: must purge before re-light to avoid unburnt-fuel explosion."],
  "Fuel-side burner failure (nozzle fouling / unstable flame).",
  scenarios["SCN-046"]["correct_resolution"],
  parts_for("SCN-046"), lead_summary("SCN-046"),
  ["spine:SCN-046", "RCA-010-RHF-ZONE-SOAK-burner-failure.md", "SOP-12_furnace-burner-refractory.md"],
  [T_SENSOR, T_DIAG, T_RCA, T_SOP, T_SPARE])

# SCN-047 wire rope
tprompt(
  "Ladle crane MS.LDC.CRN01: rope MFL signal 320 mV, load at 85% SWL. Diagnose against ISO 4309 and advise.",
  "MS.LDC.CRN01", "SCN-047",
  ["MFL 320 mV above the 300 mV alarm (~>15-20% LMA) -> rope at/over ISO 4309 discard.",
   "Load 85% SWL is within normal (alarm 95%) - the rope, not the load, is the problem.",
   "Discard criteria: MFL >15-20% LMA, OR >=12 random broken wires in one lay (>=4 in one strand), OR diameter -7% (RCA-011, SOP-10).",
   "P1 - molten-ladle drop is catastrophic / fatal."],
  "Wire-rope fatigue at ISO 4309 discard limit. Remove crane from service.",
  scenarios["SCN-047"]["correct_resolution"],
  parts_for("SCN-047"), lead_summary("SCN-047"),
  ["spine:SCN-047", "RCA-011-MS-LDC-CRN01-wire-rope-fatigue.md", "SOP-10_crane-wire-rope-brake.md"],
  [T_SENSOR, T_DIAG, T_RCA, T_SOP, T_SPARE])

# SCN-048 servo silting
tprompt(
  "Cold-mill AGC servo JSR.CR.S2.AGC.SV: oil at ISO 17/15/12, servo position error 3.2%, strip-gauge deviation 22 um. Diagnose.",
  "CRM.AGC.SV01", "SCN-048",
  ["Oil cleanliness ISO 17/15/12 at the alarm code (dirtier than 15/13/10 target).",
   "Position error 3.2% above 3.0 alarm + gauge deviation 22 um above 20 alarm = AGC losing precision.",
   "Silt (1-5 um) plugging the 1-3 um spool clearance -> sluggish small-amplitude response (RCA-012).",
   "Risk: AGC loss -> ~30% scrap increase + cobble (Rs 21L/cobble-hr)."],
  "Servo-valve silting / spool wear from dirty oil.",
  scenarios["SCN-048"]["correct_resolution"],
  parts_for("SCN-048"), lead_summary("SCN-048") + " - SERVO-VLV-D661 10wk/1 stock; bench-clean removed valve to protect stock",
  ["spine:SCN-048", "RCA-012-CRM-AGC-SV01-servo-silting.md", "SOP-11_agc-servo-valve-hydraulic-clean.md"],
  [T_SENSOR, T_DIAG, T_RCA, T_SOP, T_SPARE, T_COST])

# Additional troubleshooting variants (early-stage / ambiguous / secondary failure modes)
# to reach ~60. These reference secondary failure modes documented in the RCA index.
tprompt(
  "F3 work-roll bearing oil-film outlet temp climbing to 80 degC while DE bearing temp normal. AE slightly elevated. What is happening?",
  "HSM.F3.WR.BRG01", "SCN-037",
  ["Oil-film outlet temp 80 degC above 75 warning (alarm 85) while roller-neck DE temp still normal.",
   "Pattern points to oil-film breakdown / incipient lube starvation, a separate failure mode on this asset (RCA-013).",
   "AE elevation is consistent with boundary-lubrication metal contact.",
   "Catch it before it cascades into a full bearing spall."],
  "Oil-film bearing breakdown / lube starvation onset (early). Check lube supply/nozzles before it becomes a spall.",
  ["LOTO + confirm zero-energy", "Inspect oil-film bearing lube nozzles (LUBE-NOZ-01), clear/replace if blocked",
   "Verify oil supply pressure and flow to the chock", "Trend OFB outlet temp + AE; if rising, plan controlled stop"],
  [{"part_id":"LUBE-NOZ-01","name":"Oil-film bearing lube nozzle","stock_qty":4,"lead_time_weeks":1,"unit_cost_usd":120}],
  "LUBE-NOZ-01 1wk (stock 4)",
  ["spine:HSM.F3.WR.BRG01", "RCA-013-HSM-F3-WR-BRG01-lube-starvation.md", "MAN-001_rolling_mill_work_roll_bearing.md"],
  [T_SENSOR, T_TREND, T_RCA, T_SPARE],
  cost={"inr": 835000, "usd": 10000},
  downtime={"planned": 2, "unplanned": 4}, safety="P3", mode="oil_film_breakdown",
  cost_basis_note="ACTUAL-MODE economics (oil-film breakdown / lube-starvation onset, RCA-013), NOT the parent SCN-037 outer-race-spall block (USD 90,000 / P2). Caught early at the OFB outlet-temp warning: clear/replace lube nozzles (LUBE-NOZ-01) and restore oil supply before it cascades into a bearing spall. If left to progress into a spall, economics approach SCN-037; this record is the caught-early lube case.")

tprompt(
  "F1 gearbox oil viscosity drifting up to 265 cSt with darkening color, GMF vibration still normal. Diagnose.",
  "HSM.F1.GBX01", "SCN-038",
  ["Viscosity 265 cSt at the high alarm (normal 198-242) with oil darkening = oil oxidation / varnish (RCA-014).",
   "GMF vibration normal -> the gears are not yet damaged; this is a lubricant condition problem.",
   "Oxidized oil forms varnish that blocks filters and reduces heat transfer.",
   "Address the oil, not the gears - this is preventable degradation."],
  "Oil oxidation / varnish (lubricant condition, gears still healthy).",
  ["Schedule oil change to fresh ISO VG220 (OIL-VG220)", "Replace filter element (FLT-GBX-01)",
   "Investigate root cause: oil over-temp or extended service interval", "Resume ferrographic + viscosity trending"],
  [{"part_id":"OIL-VG220","name":"ISO VG220 EP gear oil (200L drum)","stock_qty":4,"lead_time_weeks":0,"unit_cost_usd":900},
   {"part_id":"FLT-GBX-01","name":"Gearbox oil filter element","stock_qty":3,"lead_time_weeks":0,"unit_cost_usd":180}],
  "OIL-VG220 0wk (stock 4); FLT-GBX-01 0wk (stock 3)",
  ["spine:HSM.F1.GBX01", "RCA-014-HSM-F1-GBX01-oil-oxidation-varnish.md", "SOP-02_gearbox-oil-gear-service.md"],
  [T_SENSOR, T_RCA, T_SOP, T_SPARE],
  cost={"inr": 250500, "usd": 3000},
  downtime={"planned": 4, "unplanned": 0}, safety="P4", mode="oil_oxidation_varnish",
  cost_basis_note="ACTUAL-MODE economics (oil oxidation / varnish - lubricant condition, gears healthy), NOT the parent SCN-038 tooth-fatigue-crack block (USD 600,000 / 168h / P2). A planned oil change (OIL-VG220) + filter; no gear damage, so cost is the oil/filter + a short drain window only.")

tprompt(
  "F1 motor stator winding temp at 150 degC, phase current imbalance 3%, PI dropping. Diagnose.",
  "HSM.F1.MTR01", "SCN-039",
  ["Winding temp 150 degC above 145 warning (alarm 155) - thermal stress on Class-F insulation.",
   "Current imbalance 3% above 2 warning + falling PI = winding turn-short / overheat (RCA-015).",
   "This is a different mode from broken-bar - it is insulation/winding thermal distress.",
   "Continued overheating accelerates insulation aging (every 10 degC halves life)."],
  "Winding overheat with incipient turn-short risk.",
  ["Reduce load / check VFD cooling and ventilation", "Verify phase balance at the supply",
   "Schedule offline PI + surge test; if insulation degraded, plan rewind (RWND-KIT-MV)",
   "Trend winding temp + imbalance; trip if temp reaches 155 degC alarm"],
  [{"part_id":"RWND-KIT-MV","name":"MV rewind materials","stock_qty":1,"lead_time_weeks":3,"unit_cost_usd":15000}],
  "RWND-KIT-MV 3wk (stock 1)",
  ["spine:HSM.F1.MTR01", "RCA-015-HSM-F1-MTR01-winding-overheat.md", "SOP-03_motor-rewind-swap.md"],
  [T_SENSOR, T_DIAG, T_RCA, T_SPARE],
  cost={"inr": 4175000, "usd": 50000},
  downtime={"planned": 10, "unplanned": 0}, safety="P2", mode="winding_overheat",
  cost_basis_note="ACTUAL-MODE economics (winding overheat with incipient turn-short risk, RCA-015), NOT the parent SCN-039 broken-rotor-bar block (USD 100,000 / P3). A load/cooling correction plus a planned rewind (RWND-KIT-MV) if insulation is degraded; the swap uses the reusable insurance spare like SCN-039, but this is an insulation-thermal mode (P2) distinct from a broken bar.")

tprompt(
  "Descale pump suction pressure dropped to 70 kPa, AE broadband at 15 dB, casing vibration rising. Diagnose.",
  "HSM.DSC.PMP01", "SCN-040",
  ["Suction pressure 70 kPa at the low alarm (NPSH starvation) - cavitation onset.",
   "AE broadband 15 dB at alarm = cavitation bubble-collapse energy in the 100-500 kHz band (RCA-016).",
   "This is cavitation, not seal failure - root is insufficient NPSH (clogged strainer / low supply).",
   "Sustained cavitation erodes the impeller (IMP-DSC-01)."],
  "Cavitation from NPSH starvation (low suction pressure).",
  ["Restore suction conditions: check strainer/supply, reduce speed if possible",
   "Inspect impeller for cavitation erosion (replace IMP-DSC-01 if pitted)",
   "Verify suction pressure back above 120 kPa before sustained running"],
  [{"part_id":"IMP-DSC-01","name":"Descale pump impeller","stock_qty":1,"lead_time_weeks":8,"unit_cost_usd":8000}],
  "IMP-DSC-01 8wk (stock 1)",
  ["spine:HSM.DSC.PMP01", "RCA-016-HSM-DSC-PMP01-cavitation.md", "SOP-04_pump-mechanical-seal.md"],
  [T_SENSOR, T_DIAG, T_RCA, T_SPARE],
  cost={"inr": 500000, "usd": 6000},
  downtime={"planned": 2, "unplanned": 6}, safety="P3", mode="cavitation",
  cost_basis_note="ACTUAL-MODE economics (cavitation / NPSH starvation, RCA-016), NOT the parent SCN-040 seal-failure block (USD 14,400). Cavitation caught early via suction-restore + strainer clean is a low-cost recovery; figure covers a short corrective stop plus impeller inspection (IMP-DSC-01 only if pitted). A run-on cavitation event that erodes the impeller would approach the SCN-040 seal range; this record is the caught-early case.")

tprompt(
  "BF cooling-water pump BF.CW.PMP02: differential head deviation -12%, 1x vibration 5 mm/s. Diagnose.",
  "BF.CW.PMP02", "SCN-041",
  ["Head deviation -12% at the alarm (negative = wear) -> the pump is losing head.",
   "1x vibration ~5 mm/s near 5.6 alarm consistent with impeller wear/erosion + unbalance (RCA-019).",
   "Wear-ring clearance opening reduces efficiency; abrasive cooling water erodes the impeller.",
   "Cooling-water loss endangers the BF - criticality 1."],
  "Impeller / wear-ring erosion causing head loss on the BF cooling-water pump.",
  ["Switch to standby pump, isolate + LOTO", "Replace impeller (IMP-CW-01) and wear-ring set (WRING-CW-01)",
   "Confirm head-vs-flow back on design curve before return"],
  [{"part_id":"IMP-CW-01","name":"Cooling pump impeller (double-suction)","stock_qty":1,"lead_time_weeks":6,"unit_cost_usd":6500},
   {"part_id":"WRING-CW-01","name":"Wear ring set","stock_qty":2,"lead_time_weeks":4,"unit_cost_usd":400}],
  "IMP-CW-01 6wk (stock 1); WRING-CW-01 4wk (stock 2)",
  ["spine:BF.CW.PMP02", "RCA-019-BF-CW-PMP02-impeller-wear.md", "SOP-04_pump-mechanical-seal.md"],
  [T_SENSOR, T_DIAG, T_RCA, T_SPARE],
  cost={"inr": 2500000, "usd": 29940},
  downtime={"planned": 4, "unplanned": 8}, safety="P2", mode="impeller_wear_erosion",
  cost_basis_note="ACTUAL-MODE economics (impeller/wear-ring erosion on BF.CW.PMP02, RCA-019), NOT the parent SCN-041 compressor-surge block (USD 6,000,000 / 96h / P1). Scaled to a standby-changeover + impeller/wear-ring rebuild on this cooling-water pump, comparable to the BF.CW.PMP02 bearing-failure scenario SCN-050 (USD 29,940 / 4+8h / P2). Criticality-1 asset but a planned standby swap, not a blower-destruction event.")

tprompt(
  "Sinter main fan SP.SINT.FAN01: bearing temp 95 degC, 1x vibration normal, duct DP normal. Diagnose.",
  "SP.SINT.FAN01", "SCN-041",
  ["Bearing temp 95 degC at the alarm while vibration and DP are normal.",
   "Isolated bearing-temp rise without vibration = lubrication/cooling problem -> bearing overheating (RCA-020).",
   "Likely grease degradation or cooling-water loss to the bearing, not an imbalance.",
   "Catch before it becomes a bearing seizure."],
  "Bearing overheating (lubrication/cooling), early stage.",
  ["Check bearing lubrication and cooling-water supply", "Re-grease/relubricate per schedule",
   "If temp persists, plan bearing replacement (BRG-LRG-300)", "Trend bearing temp + vibration"],
  [{"part_id":"BRG-LRG-300","name":"Large-bore roller bearing >300mm","stock_qty":1,"lead_time_weeks":8,"unit_cost_usd":12000}],
  "BRG-LRG-300 8wk (stock 1)",
  ["spine:SP.SINT.FAN01", "RCA-020-SP-SINT-FAN01-bearing-overheat.md", "MAN-005_bf_sinter_fan_blower.md"],
  [T_SENSOR, T_DIAG, T_RCA, T_SPARE],
  cost={"inr": 3340000, "usd": 40000},
  downtime={"planned": 8, "unplanned": 12}, safety="P2", mode="bearing_overheating",
  cost_basis_note="ACTUAL-MODE economics (early bearing overheating, lube/cooling, RCA-020), NOT the parent SCN-041 compressor-surge block (USD 6,000,000 / 96h / P1). Caught at the 95 degC bearing-temp alarm: re-lube/cooling fix plus a planned bearing change (BRG-LRG-300) if it persists - a planned bearing intervention, not a surge/machine-destruction event.")

tprompt(
  "Caster segment 7 zone spray flow dropped to 120 L/min, roll rpm and force normal. Diagnose.",
  "CCM.SEG.07", "SCN-042",
  ["Spray flow 120 L/min at the low alarm while roll rpm/force normal.",
   "Low secondary-cooling flow with healthy rolls = spray-nozzle blockage (RCA-021), not a seizure.",
   "Scale/debris plugs nozzles; under-cooling risks slab surface quality and bulging.",
   "Consumable nozzles (NOZ-SPRAY-01) are on shelf."],
  "Spray-nozzle blockage in segment-7 secondary cooling.",
  ["Plan a window to clean/replace blocked nozzles (NOZ-SPRAY-01)", "Verify zone flow back to 180-220 L/min",
   "Check water filtration upstream to prevent recurrence"],
  [{"part_id":"NOZ-SPRAY-01","name":"Secondary cooling spray nozzle (consumable)","stock_qty":50,"lead_time_weeks":0,"unit_cost_usd":35}],
  "NOZ-SPRAY-01 0wk (stock 50)",
  ["spine:CCM.SEG.07", "RCA-021-CCM-SEG07-spray-nozzle-blockage.md", "SOP-06_caster-segment-change.md"],
  [T_SENSOR, T_DIAG, T_RCA, T_SPARE],
  cost={"inr": 835000, "usd": 10000},
  downtime={"planned": 2, "unplanned": 0}, safety="P3", mode="spray_nozzle_blockage",
  cost_basis_note="ACTUAL-MODE economics (spray-nozzle blockage, RCA-021), NOT the parent SCN-042 roll-seizure block (USD 96,000 / 8h / P2). A nozzle clean/replace (NOZ-SPRAY-01, consumable on shelf) at a short window; under-cooling risks slab surface quality, but this is far below a roll-seizure strand-drag event.")

tprompt(
  "Roughing stand R1 chock vibration spiking to 9 mm/s with a 5th-octave chatter signature, force ripple moderate. Diagnose.",
  "HSM.STD.R1", "SCN-044",
  ["Chock vibration 9 mm/s near the 10 alarm with a 5th-octave chatter band = roll chatter (RCA-022), not a spall.",
   "Force ripple not strongly periodic at 1x roll, so it is regenerative chatter rather than a surface spall flat.",
   "Chatter leaves periodic gauge/finish marks and stresses chocks.",
   "Address via speed/tension/roll-eccentricity, not a roll grind."],
  "Roll chatter (5th-octave / regenerative), distinct from a work-roll spall.",
  ["Adjust rolling speed / interstand tension to leave the chatter band", "Check roll eccentricity and chock seating",
   "Inspect/replace chock seals (CHOCK-SEAL-01) if worn", "Monitor chock vibration spectrum"],
  [{"part_id":"CHOCK-SEAL-01","name":"Roll chock seals","stock_qty":4,"lead_time_weeks":6,"unit_cost_usd":350}],
  "CHOCK-SEAL-01 6wk (stock 4)",
  ["spine:HSM.STD.R1", "RCA-022-HSM-STD-R1-roll-chatter.md", "SOP-08_hot-strip-mill-roll-change.md"],
  [T_SENSOR, T_DIAG, T_RCA, T_SPARE],
  cost={"inr": 1670000, "usd": 20000},
  downtime={"planned": 0.5, "unplanned": 2}, safety="P3", mode="roll_chatter_5th_octave",
  cost_basis_note="ACTUAL-MODE economics (regenerative roll chatter, RCA-022), NOT the parent SCN-044 work-roll-spall block (USD 184,000 / P2). Chatter is a quality/process fault corrected by speed/tension/eccentricity adjustment plus chock-seal replacement if worn; cost is product gauge/finish marking on a short segment plus a brief stop, far below a spall quick-change-to-failure event.")

tprompt(
  "Ore conveyor belt-edge position drifting to 50 mm off-centre, motor current normal. Diagnose.",
  "RM.CONV.ORE01", "SCN-045",
  ["Belt-edge 50 mm at the alarm = belt mistracking (RCA-023), motor current normal so not an overload.",
   "Off-track belt risks edge damage, spillage, and structure contact.",
   "Cause: uneven loading, idler misalignment, or pulley lagging wear.",
   "Fit a self-aligning training idler to correct tracking."],
  "Belt misalignment / mistracking.",
  ["Install/adjust training idler (IDLER-TRAIN-01)", "Check load chute centring and pulley alignment",
   "Confirm belt-edge back within +/-15 mm"],
  [{"part_id":"IDLER-TRAIN-01","name":"Training/self-aligning idler","stock_qty":6,"lead_time_weeks":4,"unit_cost_usd":320}],
  "IDLER-TRAIN-01 4wk (stock 6)",
  ["spine:RM.CONV.ORE01", "RCA-023-RM-CONV-ORE01-belt-misalignment.md", "SOP-09_conveyor-idler-belt.md"],
  [T_SENSOR, T_DIAG, T_RCA, T_SPARE],
  cost={"inr": 167000, "usd": 2000},
  downtime={"planned": 1, "unplanned": 0}, safety="P3", mode="belt_misalignment",
  cost_basis_note="ACTUAL-MODE economics (belt mistracking, RCA-023), NOT the parent SCN-045 idler-bearing-failure block (USD 7,500 / P1 belt-fire). A training-idler install/adjust (IDLER-TRAIN-01) + load-point check; an alignment fix, not the fire-risk idler-seizure class (so P3, not P1).")

tprompt(
  "Reheat furnace shell IR temp shows a localized 250 degC hot spot, zone temp normal. Diagnose.",
  "RHF.ZONE.SOAK", "SCN-046",
  ["Shell IR 250 degC at the alarm in a localized spot while zone temp is normal = refractory thinning/burnout (RCA-024).",
   "A hot spot means lost insulation locally - heat is reaching the steel shell.",
   "Risk: shell warping / structural damage and energy loss if it grows.",
   "Plan refractory repair at the next furnace window (REFRAC-CAST-01)."],
  "Refractory hot-spot / local burnout.",
  ["Mark and monitor the hot spot; reduce local firing if possible",
   "Plan gunning/castable repair (REFRAC-CAST-01) at the next outage", "Recheck shell IR after repair"],
  [{"part_id":"REFRAC-CAST-01","name":"Refractory castable / gunning mix","stock_qty":10,"lead_time_weeks":2,"unit_cost_usd":1200}],
  "REFRAC-CAST-01 2wk (stock 10)",
  ["spine:RHF.ZONE.SOAK", "RCA-024-RHF-ZONE-SOAK-refractory-hotspot.md", "SOP-12_furnace-burner-refractory.md"],
  [T_SENSOR, T_DIAG, T_RCA, T_SPARE],
  cost={"inr": 2087500, "usd": 25000},
  downtime={"planned": 8, "unplanned": 0}, safety="P3", mode="refractory_hot_spot_burnout",
  cost_basis_note="ACTUAL-MODE economics (localized refractory hot-spot / burnout, RCA-024), NOT the parent SCN-046 burner-failure block (USD 12,000 / P2). A monitored hot-spot is repaired by planned gunning/castable patch (REFRAC-CAST-01) at the next furnace outage; cost reflects the planned repair window + energy loss, not an unplanned flame-safety trip.")

tprompt(
  "EAF hydraulic power unit: ISO 4406 at 19/17/14, water content 500 ppm, filter DP rising. Diagnose.",
  "EAF.AUX.HYD01", "SCN-048",
  ["Cleanliness 19/17/14 at alarm + water content 500 ppm at alarm = oil/water + particulate contamination (RCA-018).",
   "Filter DP rising shows the element is loading with contaminant.",
   "Water emulsifies, degrades film strength, and corrodes components.",
   "Kidney-loop filtration + filter change restores oil condition."],
  "Oil/water + particulate contamination of the EAF HPU.",
  ["Run kidney-loop filtration (KID-LOOP-01) to remove water + particulate",
   "Change filter element (FLT-HYD-10)", "Investigate water ingress source (cooler leak / seals)",
   "Confirm ISO back to <=17/15/12 and water <100 ppm"],
  [{"part_id":"KID-LOOP-01","name":"Kidney-loop filtration unit (portable)","stock_qty":1,"lead_time_weeks":3,"unit_cost_usd":8500},
   {"part_id":"FLT-HYD-10","name":"Hydraulic filter element 10um","stock_qty":6,"lead_time_weeks":0,"unit_cost_usd":120}],
  "KID-LOOP-01 3wk (stock 1); FLT-HYD-10 0wk (stock 6)",
  ["spine:EAF.AUX.HYD01", "RCA-018-EAF-AUX-HYD01-oil-water-contamination.md", "SOP-13_eaf-hydraulic-system.md"],
  [T_SENSOR, T_DIAG, T_RCA, T_SPARE],
  cost={"inr": 668000, "usd": 8000},
  downtime={"planned": 4, "unplanned": 0}, safety="P3", mode="oil_water_contamination",
  cost_basis_note="ACTUAL-MODE economics (oil/water + particulate contamination of the EAF HPU, RCA-018), NOT the parent SCN-048 servo-silting block (USD 137,700 / P2). Kidney-loop filtration (KID-LOOP-01) + filter change + fixing the water-ingress source; an oil-conditioning task on the HPU, not the AGC-loss/cobble economics of the cold-mill servo valve.")

tprompt(
  "Ladle crane brake-drum temp 120 degC, hoist-gearbox GMF 2.5 g. Diagnose.",
  "MS.LDC.CRN01", "SCN-047",
  ["Brake-drum temp 120 degC at alarm = brake drag/slip generating heat (RCA-025).",
   "Hoist-gearbox GMF 2.5 g at alarm = gear wear, a separate developing fault.",
   "Brake slip on a molten-metal crane is a P1 safety issue (load-holding).",
   "Address brake first (safety), then plan gearbox attention."],
  "Brake wear/slip (P1 safety) with concurrent hoist-gearbox gear wear.",
  ["Take crane out of service - brake load-holding suspect",
   "Replace brake pads (BRAKE-PAD-01); inspect/replace thruster (BRAKE-THR-01) if sticking",
   "Brake hold test before return", "Plan hoist-gearbox inspection for gear wear"],
  [{"part_id":"BRAKE-PAD-01","name":"Crane brake pads","stock_qty":4,"lead_time_weeks":4,"unit_cost_usd":450},
   {"part_id":"BRAKE-THR-01","name":"Brake thruster (electro-hydraulic)","stock_qty":1,"lead_time_weeks":8,"unit_cost_usd":2200}],
  "BRAKE-PAD-01 4wk (stock 4); BRAKE-THR-01 8wk (stock 1)",
  ["spine:MS.LDC.CRN01", "RCA-025-MS-LDC-CRN01-brake-wear.md", "SOP-10_crane-wire-rope-brake.md"],
  [T_SENSOR, T_DIAG, T_RCA, T_SPARE],
  cost={"inr": 626250, "usd": 7500},
  downtime={"planned": 8, "unplanned": 4}, safety="P1", mode="brake_wear_slip",
  cost_basis_note="ACTUAL-MODE economics (brake wear/slip + hoist-gearbox gear wear, RCA-025), NOT the parent SCN-047 wire-rope / ladle-drop block (USD 1,000,000 / P1). Safety_class stays P1 (brake load-holding on a molten-metal crane is life-safety), but the DIRECT job is a brake-pad/thruster replacement + hold test (~USD 7,500) - the $1M figure is the catastrophic ladle-drop event-class of SCN-047, not this brake-pad repair caught at the temperature alarm.")

# A few "is this normal?" baseline troubleshooting prompts (label NORMAL handling)
for (prompt, asset_id, scn_norm, vals, refs) in [
  ("F3 work-roll bearing: vibration 1.6 mm/s, bearing temp 58 degC. Anything to worry about?",
   "HSM.F3.WR.BRG01", "SCN-001", "vib 1.6 mm/s (band 0.5-2.3), temp 58 degC (band 40-70)",
   ["spine:SCN-001"]),
  ("F1 gearbox: GMF vibration 2.8 mm/s, oil temp 56 degC, Fe 3 ppm. Status?",
   "HSM.F1.GBX01", "SCN-002", "GMF 2.8 (band 0.5-4.0), oil 56 (45-65), Fe 3 ppm (0-5)",
   ["spine:SCN-002"]),
  ("BF blower: 1x vibration 1.8 mm/s, shaft displacement 35 um. Status?",
   "BF.BLW.FAN01", "SCN-005", "1x 1.8 (1.0-2.3), shaft 35 um (10-50)",
   ["spine:SCN-005"]),
]:
    ts.append({
        "prompt": prompt, "asset_id": asset_id, "scenario_id": scn_norm,
        "failure_mode": "none", "safety_class": "P4",
        "diagnostic_reasoning_chain": [
            f"Readings: {vals}.",
            "All monitored parameters are inside their normal bands - no threshold crossed.",
            "No degradation trend present; signature matches healthy steady-state."],
        "diagnosis": "NORMAL / healthy steady-state. No action beyond routine monitoring.",
        "correct_resolution": ["Continue routine condition monitoring", "Trend baseline to CMMS"],
        "parts_required": [], "lead_time": "n/a",
        "downtime_hours": {"planned": 0, "unplanned": 0},
        "cost_impact": {"inr": 0, "usd": 0},
        "grounding_refs": refs, "expected_tools": [T_SENSOR, T_THRESH, T_DIAG],
    })


# ---- Additional troubleshooting prompts (secondary modes + early-stage + differential) ----
# Each reuses its asset's failure scenario for the spine-anchored cost/downtime, but
# the reasoning/diagnosis/resolution are grounded in the specific failure mode + sensor.

def tprompt2(prompt, asset_id, scn_id, reasoning_chain, diagnosis, resolution, parts, lead, refs, tools,
             cost=None, downtime=None, safety=None, cost_basis_note=None, mode=None):
    """Like tprompt but allows custom parts/resolution for secondary failure modes.

    For SIBLING failure modes, pass explicit `mode` + `cost`/`downtime`/`safety` so the
    labelled mode AND economics describe the ACTUAL mode rather than being inherited
    from the parent spine archetype.
    """
    scn = scenarios[scn_id]
    rec = {
        "prompt": prompt, "asset_id": asset_id, "scenario_id": scn_id,
        "failure_mode": mode if mode is not None else scn["failure_mode"],
        "safety_class": safety if safety is not None else scn["safety_class"],
        "diagnostic_reasoning_chain": reasoning_chain, "diagnosis": diagnosis,
        "correct_resolution": resolution, "parts_required": parts, "lead_time": lead,
        "downtime_hours": downtime if downtime is not None else scn["downtime_hours"],
        "cost_impact": dict(cost) if cost is not None else scn["cost_impact"],
        "grounding_refs": refs, "expected_tools": tools,
    }
    if cost_basis_note is not None:
        rec["cost_impact"]["note"] = cost_basis_note
    ts.append(rec)

def sp(part_id):
    p = spares[part_id]
    return {"part_id": part_id, "name": p["name"], "stock_qty": p["stock_qty"],
            "lead_time_weeks": p["lead_time_weeks"], "unit_cost_usd": p["unit_cost"]["usd"]}

def lead1(part_id):
    p = spares[part_id]
    return f"{part_id} {p['lead_time_weeks']}wk (stock {p['stock_qty']})"

# (1) F1 motor rotor eccentricity (2x supply-freq vibration)
tprompt2(
  "F1 main motor JSR.HR.STD1.MTR01.VIB.2XF1 at 2.4 mm/s (alarm 2.5), MCSA sideband normal, winding temp normal. Diagnose.",
  "HSM.F1.MTR01", "SCN-039",
  ["2x supply-frequency vibration 2.4 mm/s near the 2.5 alarm while MCSA and winding temp are normal.",
   "2x-line-frequency vibration is the eccentricity signature (IEEE 1415), not a broken bar or winding fault.",
   "Static/dynamic air-gap eccentricity from bearing wear, soft foot, or rotor sag.",
   "Confirm with air-gap flux / vibration phase; not an instantaneous failure."],
  "Rotor eccentricity (air-gap), distinct from broken rotor bar or winding overheat.",
  ["Check soft foot and base bolting; re-shim if needed", "Measure air-gap symmetry at the four quadrants",
   "Inspect DE/NDE bearings for wear (BRG-MTR-SET) - worn bearing lets the rotor sag", "Re-align and re-balance; trend 2x-f1 vibration"],
  [sp("BRG-MTR-SET")], lead1("BRG-MTR-SET"),
  ["spine:HSM.F1.MTR01/JSR.HR.STD1.MTR01.VIB.2XF1", "spine:HSM.F1.MTR01/failure_modes", "MAN-003_large_induction_motor_vfd.md"],
  [T_SENSOR, T_DIAG, T_SPARE],
  cost={"inr": 1670000, "usd": 20000},
  downtime={"planned": 8, "unplanned": 0}, safety="P3", mode="rotor_eccentricity",
  cost_basis_note="ACTUAL-MODE economics (rotor / air-gap eccentricity, 2x-line-freq vibration), NOT the parent SCN-039 broken-rotor-bar block (USD 100,000 / P3). Corrected by soft-foot/base re-shim, re-align, and a DE/NDE bearing replacement (BRG-MTR-SET) if worn - a planned alignment+bearing job, not a motor swap.")

# (2) F1 motor insulation degradation (PI offline)
tprompt2(
  "F1 motor offline PI test reads 1.4 (alarm 1.5, normal 2.0-5.0). Winding temp and MCSA online normal. Diagnose.",
  "HSM.F1.MTR01", "SCN-039",
  ["Polarisation index 1.4 is below the 1.5 alarm (lower is worse, IEEE 43-2013).",
   "Low PI indicates moisture/contamination in the insulation - degradation toward ground-fault risk.",
   "Online sensors normal because this is an offline insulation-condition metric.",
   "Insulation degradation is a slow, plannable mode but a ground fault would be sudden."],
  "Insulation degradation (low PI) - moisture/contamination risk of eventual ground fault.",
  ["Dry out the winding (controlled heating) and re-test PI", "Run a surge/HiPot test to locate weak insulation",
   "If PI stays <1.5, plan a rewind (RWND-KIT-MV) at the next swap window", "Improve enclosure sealing / space-heater operation"],
  [sp("RWND-KIT-MV")], lead1("RWND-KIT-MV"),
  ["spine:HSM.F1.MTR01/JSR.HR.STD1.MTR01.INS.PI", "spine:HSM.F1.MTR01/failure_modes", "SOP-03_motor-rewind-swap.md"],
  [T_THRESH, T_DIAG, T_SPARE],
  cost={"inr": 4175000, "usd": 50000},
  downtime={"planned": 10, "unplanned": 0}, safety="P2", mode="insulation_degradation_ground_fault",
  cost_basis_note="ACTUAL-MODE economics (insulation degradation / low PI, moisture-contamination, ground-fault risk), NOT the parent SCN-039 broken-rotor-bar block (USD 100,000 / P3). Dry-out + surge/HiPot test, then a planned rewind (RWND-KIT-MV) at the next swap window if PI stays low - an insulation-condition mode (P2 ground-fault risk) distinct from a broken bar.")

# (3) Conveyor motor overload / blocked chute
tprompt2(
  "Ore conveyor JSR.RM.CONV1.MTR.CURR at 125 %FLA (alarm), belt-edge normal, idler readings normal. Diagnose.",
  "RM.CONV.ORE01", "SCN-045",
  ["Drive-motor current 125 %FLA at the alarm while tracking and idlers are normal.",
   "High current with normal idlers/tracking = motor overload, typically a blocked transfer chute or belt over-load.",
   "Not a bearing or alignment fault - it is a loading problem.",
   "Sustained overload risks motor thermal trip and belt-drive stress."],
  "Motor overload from a blocked chute / belt over-load (not a mechanical idler fault).",
  ["Stop and inspect/clear the transfer chute for blockage", "Check feed rate / belt loading vs design",
   "Verify motor current returns to 60-95 %FLA before sustained running", "Inspect drive coupling and pulley for drag"],
  [], "n/a (inspection/clearing; no spare consumed)",
  ["spine:RM.CONV.ORE01/JSR.RM.CONV1.MTR.CURR", "spine:RM.CONV.ORE01/failure_modes", "MAN-009_raw_material_conveyor.md"],
  [T_SENSOR, T_DIAG],
  cost={"inr": 167000, "usd": 2000},
  downtime={"planned": 0, "unplanned": 1}, safety="P3", mode="motor_overload_blocked_chute",
  cost_basis_note="ACTUAL-MODE economics (motor overload from a blocked chute / belt over-load), NOT the parent SCN-045 idler-bearing-failure block (USD 7,500 / P1 belt-fire). A chute clear + feed-rate check, no spare consumed; this is a loading problem, not the fire-risk idler-seizure class (so P3, not P1).")

# (4) Conveyor belt rip/tear (rip-loop open)
tprompt2(
  "Ore conveyor JSR.RM.CONV1.RIP.LOOP reads 0 mA (alarm; normal 60-80). Diagnose - is this real?",
  "RM.CONV.ORE01", "SCN-045",
  ["Rip-detector loop current 0 mA = an embedded loop is severed (open circuit).",
   "An open rip-loop indicates a longitudinal belt tear has cut the sensing loop (Fenner RipScan).",
   "Confirm by walk-down at the load point - tears usually start where tramp/oversize material penetrates.",
   "A propagating rip can destroy a long belt and is a major downtime event."],
  "Longitudinal belt rip/tear (rip-detector loop severed).",
  ["Stop the belt immediately and LOTO", "Locate the tear; if local, repair with the vulcanising kit (VULC-KIT-01)",
   "If a belt section is destroyed, splice in BELT-SEC-1600 (made-to-order, 10wk lead) - major outage",
   "Fix the load-point cause (tramp metal / chute wear) before restart"],
  [sp("VULC-KIT-01"), sp("BELT-SEC-1600")], lead1("VULC-KIT-01") + "; " + lead1("BELT-SEC-1600"),
  ["spine:RM.CONV.ORE01/JSR.RM.CONV1.RIP.LOOP", "spine:RM.CONV.ORE01/failure_modes", "SOP-09_conveyor-idler-belt.md"],
  [T_SENSOR, T_DIAG, T_SPARE],
  cost={"inr": 4175000, "usd": 50000},
  downtime={"planned": 0, "unplanned": 12}, safety="P2", mode="belt_rip_tear",
  cost_basis_note="ACTUAL-MODE economics (longitudinal belt rip/tear, rip-loop severed), NOT the parent SCN-045 idler-bearing-failure block (USD 7,500 / P1 belt-fire). A local tear is a vulcanised repair (VULC-KIT-01); a destroyed section needs a made-to-order belt splice (BELT-SEC-1600, 10wk) - a major downtime event of its own scale, distinct from the idler-seizure fire class.")

# (5) BF blower blade erosion/deposit (mass imbalance)
tprompt2(
  "BF turbo-blower JSR.BF.BLW.FAN01.VIB.1X rising to 6 mm/s, shaft displacement 60 um, surge oscillation normal. Diagnose.",
  "BF.BLW.FAN01", "SCN-041",
  ["1x vibration 6 mm/s (warning 4.5, alarm 7.1) and shaft displacement 60 um (warning 80) - both elevated, surge oscillation normal.",
   "Rising 1x synchronous vibration without surge = mass imbalance from blade erosion or deposit shedding (RCA-017).",
   "Dust-laden gas erodes/deposits on blades, shifting the balance plane.",
   "Plannable - balance/clean before it reaches the 7.1 alarm."],
  "Mass imbalance from blade erosion / deposit (not surge, not a bearing fault).",
  ["Inspect/borescope blades for erosion and deposit", "Field-balance using balancing weights (BAL-WT-01)",
   "If blades eroded beyond limits, plan a blade-set replacement (FAN-BLADE-SET, 12wk)", "Re-trend 1x vibration after balance"],
  [sp("BAL-WT-01"), sp("FAN-BLADE-SET")], lead1("BAL-WT-01") + "; " + lead1("FAN-BLADE-SET"),
  ["spine:BF.BLW.FAN01/JSR.BF.BLW.FAN01.VIB.1X", "spine:BF.BLW.FAN01/failure_modes", "RCA-017-BF-BLW-FAN01-blade-erosion.md"],
  [T_SENSOR, T_DIAG, T_SPARE],
  cost={"inr": 8000000, "usd": 95808},
  downtime={"planned": 0, "unplanned": 24}, safety="P2", mode="mass_imbalance_deposit_shedding",
  cost_basis_note="ACTUAL-MODE economics (mass imbalance from blade erosion/deposit, RCA-017), NOT the parent SCN-041 compressor-surge block (USD 6,000,000 / 96h / P1). Mirrors the spine's own fan mass-imbalance scenario SCN-051 (SP.SINT.FAN01, USD 95,808 / 24h / P2): a balance/clean (BAL-WT-01) or blade-set swap, not a surge-driven machine destruction.")

# (6) BF blower thrust-bearing overheat
tprompt2(
  "BF turbo-blower JSR.BF.BLW.FAN01.THRUST.TEMP at 92 degC (warning 90, alarm 105), 1x vibration normal. Diagnose.",
  "BF.BLW.FAN01", "SCN-041",
  ["Thrust-bearing temp 92 degC above the 90 warning while 1x vibration is normal.",
   "Isolated thrust-temp rise = thrust-bearing distress (lube/load), not surge or imbalance.",
   "Likely thrust-balance shift (process load) or lube film degradation on the tilting pads.",
   "Catch before pad wipe - thrust failure is severe on a 28 MW machine."],
  "Thrust-bearing overheating (lube/thrust-load), early stage.",
  ["Check thrust-bearing lube supply and oil temperature/cooling", "Verify process thrust load vs design (operating point)",
   "If temp climbs toward 105 degC alarm, plan thrust-pad inspection (BRG-THRUST-PAD, 12wk)", "Trend thrust temp + axial position"],
  [sp("BRG-THRUST-PAD")], lead1("BRG-THRUST-PAD"),
  ["spine:BF.BLW.FAN01/JSR.BF.BLW.FAN01.THRUST.TEMP", "spine:BF.BLW.FAN01/failure_modes", "MAN-005_bf_sinter_fan_blower.md"],
  [T_SENSOR, T_DIAG, T_SPARE],
  cost={"inr": 3340000, "usd": 40000},
  downtime={"planned": 8, "unplanned": 12}, safety="P2", mode="bearing_overheating",
  cost_basis_note="ACTUAL-MODE economics (early thrust-bearing overheating, lube/load), NOT the parent SCN-041 compressor-surge block (USD 6,000,000 / 96h / P1). Caught at the 92 degC warning before pad wipe: lube/cooling correction plus a planned tilting-pad inspection (BRG-THRUST-PAD). Cost is a planned bearing intervention on the 28 MW machine, escalating only if a pad wipes - well below a surge event.")

# (7) Sinter fan shaft bow / misalignment (axial 2x)
tprompt2(
  "Sinter main fan JSR.SP.FAN01.VIB.AXIAL ratio at 0.7 (alarm), 1x vibration moderate, bearing temp normal. Diagnose.",
  "SP.SINT.FAN01", "SCN-041",
  ["Axial 2x ratio 0.7 at the alarm (warning 0.4) with elevated 1x and normal bearing temp.",
   "High axial 2x ratio is the misalignment/shaft-bow signature.",
   "Thermal bow from uneven cooling or coupling misalignment after the last service.",
   "Correctable by alignment - not a bearing replacement yet."],
  "Shaft bow / misalignment (axial 2x signature).",
  ["Laser-align the coupling (target <0.05 mm); check for soft foot", "Inspect coupling element for wear",
   "Allow thermal stabilisation and re-check alignment hot", "Trend axial 2x ratio after correction"],
  [], "n/a (alignment; coupling element if worn)",
  ["spine:SP.SINT.FAN01/JSR.SP.FAN01.VIB.AXIAL", "spine:SP.SINT.FAN01/failure_modes", "MAN-005_bf_sinter_fan_blower.md"],
  [T_SENSOR, T_DIAG],
  cost={"inr": 1252500, "usd": 15000},
  downtime={"planned": 8, "unplanned": 0}, safety="P3", mode="shaft_bow_misalignment",
  cost_basis_note="ACTUAL-MODE economics (shaft bow / coupling misalignment, axial 2x), NOT the parent SCN-041 compressor-surge block (USD 6,000,000 / 96h / P1). Corrected by a planned laser-alignment / soft-foot fix (no major spare consumed); cost is the alignment window only.")

# (8) Sinter fan blade fouling (duct DP)
tprompt2(
  "Sinter main fan JSR.SP.FAN01.DP.DUCT at 22 kPa (alarm; normal 8-14), vibration normal. Diagnose.",
  "SP.SINT.FAN01", "SCN-041",
  ["Inlet-outlet DP 22 kPa at the alarm while vibration is normal.",
   "Rising DP across the fan with steady vibration = blade fouling/deposit reducing aerodynamic performance.",
   "Dust deposit on blades raises resistance and DP without unbalancing the rotor (yet).",
   "Clean before deposit sheds and causes a sudden imbalance step."],
  "Blade fouling / deposit (performance degradation, DP rise).",
  ["Plan a blade-cleaning window (water-wash / mechanical)", "Inspect blades for erosion under the deposit",
   "If eroded, plan FAN-BLADE-SET replacement (12wk)", "Re-trend DP + 1x vibration after cleaning"],
  [sp("FAN-BLADE-SET")], lead1("FAN-BLADE-SET"),
  ["spine:SP.SINT.FAN01/JSR.SP.FAN01.DP.DUCT", "spine:SP.SINT.FAN01/failure_modes", "MAN-005_bf_sinter_fan_blower.md"],
  [T_SENSOR, T_DIAG, T_SPARE],
  cost={"inr": 1002000, "usd": 12000},
  downtime={"planned": 6, "unplanned": 0}, safety="P3", mode="blade_erosion_deposit",
  cost_basis_note="ACTUAL-MODE economics (blade fouling / deposit, performance DP rise), NOT the parent SCN-041 compressor-surge block (USD 6,000,000 / 96h / P1). A planned blade-cleaning window (water-wash/mechanical), blade-set swap only if eroded; cost is the cleaning outage and minor efficiency loss.")

# (9) Caster segment misalignment / bulging
tprompt2(
  "Caster segment 7 JSR.CC1.SEG07.BULGE at 4 mm (alarm; normal 0-1), roll rpm/force normal. Diagnose.",
  "CCM.SEG.07", "SCN-042",
  ["Strand bulge deviation 4 mm at the alarm while rolls rotate normally.",
   "Excess bulge with healthy rolls = segment misalignment / roll-gap drift, not a seizure.",
   "Worn roll-gap setting or thermal distortion opens the gap, letting the strand bulge.",
   "Bulging causes internal cracks and centreline segregation in the slab."],
  "Segment misalignment / bulging (roll-gap drift), distinct from roll seizure.",
  ["Re-measure and reset the segment roll-gap per slab format", "Check segment clamping/positioning system",
   "Inspect rolls for uneven wear (ROLL-SEG-STD if worn)", "Pressure-test and verify bulge back within 1 mm"],
  [sp("ROLL-SEG-STD")], lead1("ROLL-SEG-STD"),
  ["spine:CCM.SEG.07/JSR.CC1.SEG07.BULGE", "spine:CCM.SEG.07/failure_modes", "SOP-06_caster-segment-change.md"],
  [T_SENSOR, T_DIAG, T_SPARE],
  cost={"inr": 5010000, "usd": 60000},
  downtime={"planned": 4, "unplanned": 0}, safety="P2", mode="segment_misalignment_bulging",
  cost_basis_note="ACTUAL-MODE economics (segment misalignment / roll-gap drift, bulging), NOT the parent SCN-042 roll-seizure block (USD 96,000 / 8h / P2). A planned roll-gap reset / segment realignment (ROLL-SEG-STD if worn) plus internal-quality yield loss from bulging; comparable scale to a segment job but planned rather than a seizure strand-drag.")

# (10) Caster mould copper-plate wear (heat flux low)
tprompt2(
  "Caster mould JSR.CC1.MOLD.HEATFLUX at 0.8 MW/m2 (alarm; lower is worse), TC delta and friction normal. Diagnose.",
  "CCM.MOLD.01", "SCN-043",
  ["Mean mould heat flux 0.8 MW/m2 at the low alarm (normal 1.2-2.0) while TC delta and friction are normal.",
   "Falling heat flux with no sticking signature = copper-plate wear / scaling reducing heat extraction.",
   "Worn or scaled copper plates conduct less heat to the cooling water.",
   "Low heat flux risks a thin shell - a breakout precursor if it worsens."],
  "Copper-plate wear (low heat flux), distinct from an active sticking breakout.",
  ["Inspect mould copper plates for wear/scaling at the next stop", "Plan copper-plate replacement (MOLD-CU-STD, 14wk) if below limit",
   "Check mould cooling-water flow and scaling", "Trend heat flux; watch for sticking signatures (TC/friction/level)"],
  [sp("MOLD-CU-STD")], lead1("MOLD-CU-STD"),
  ["spine:CCM.MOLD.01/JSR.CC1.MOLD.HEATFLUX", "spine:CCM.MOLD.01/failure_modes", "SOP-07_mould-copper-change.md"],
  [T_SENSOR, T_DIAG, T_SPARE],
  cost={"inr": 4175000, "usd": 50000},
  downtime={"planned": 12, "unplanned": 0}, safety="P3", mode="copper_plate_wear",
  cost_basis_note="ACTUAL-MODE economics (mould copper-plate wear / scaling, low heat flux), NOT the parent SCN-043 sticking-breakout block (USD 860,000 / 36h / P1). A PLANNED copper-plate replacement (MOLD-CU-STD) at a stop; a precursor that is monitored and addressed, not an active liquid-steel breakout, so it is far cheaper and not P1.")

# (11) Roll thermal camber / crown loss on R1
tprompt2(
  "Roughing stand R1 JSR.HR.R1.CROWN.DEV at 40 um (alarm; normal +/-10), force ripple normal. Diagnose.",
  "HSM.STD.R1", "SCN-044",
  ["Strip-crown deviation 40 um at the alarm while force ripple is normal (so not a spall).",
   "Crown drift with no force ripple = roll thermal-camber loss / roll wear over the campaign.",
   "Loss of thermal crown control changes the strip profile.",
   "Correct via roll cooling/bending or a roll change, not an emergency."],
  "Roll wear / thermal camber loss (crown deviation), distinct from a spall.",
  ["Adjust work-roll cooling and bending to restore crown", "Plan a work-roll change if camber unrecoverable (WR-HSS-PREP on shelf)",
   "Check roll-cooling header for blocked nozzles", "Trend crown deviation after correction"],
  [sp("WR-HSS-PREP")], lead1("WR-HSS-PREP"),
  ["spine:HSM.STD.R1/JSR.HR.R1.CROWN.DEV", "spine:HSM.STD.R1/failure_modes", "SOP-08_hot-strip-mill-roll-change.md"],
  [T_SENSOR, T_DIAG, T_SPARE],
  cost={"inr": 935200, "usd": 11200},
  downtime={"planned": 0.75, "unplanned": 0}, safety="P3", mode="roll_wear_thermal_camber_loss",
  cost_basis_note="ACTUAL-MODE economics (roll wear / thermal camber loss, crown drift), NOT the parent SCN-044 work-roll-SPALL block (USD 184,000 unplanned / P2). Corrected by roll-cooling/bending adjustment or a PLANNED quick-change (WR-HSS-PREP on shelf); matches the SCN-044 PLANNED roll-change cost (~USD 11,200), not the run-to-failure spall figure.")

# (12) EAF HPU filter clog
tprompt2(
  "EAF HPU JSR.MS.EAF1.HYD.FILT.DP at 4.5 bar (alarm), ISO4406 still in band, oil temp normal. Diagnose.",
  "EAF.AUX.HYD01", "SCN-048",
  ["Filter diff pressure 4.5 bar at the alarm while cleanliness is still in band and temp normal.",
   "High filter DP with clean downstream oil = the element has loaded with contaminant and is near bypass.",
   "If DP keeps rising the bypass opens and unfiltered oil reaches the valves.",
   "Simple element change - catch before bypass to protect the system."],
  "Filter clog (element loaded), pre-bypass. Change before cleanliness degrades.",
  ["Change the filter element (FLT-HYD-10, on shelf)", "Check why it loaded fast (ingress / overdue change)",
   "Verify DP back below 1.5 bar after change", "Resume inline ISO4406 trending"],
  [sp("FLT-HYD-10")], lead1("FLT-HYD-10"),
  ["spine:EAF.AUX.HYD01/JSR.MS.EAF1.HYD.FILT.DP", "spine:SCN-049/cost_impact", "spine:EAF.AUX.HYD01/failure_modes", "SOP-13_eaf-hydraulic-system.md"],
  [T_SENSOR, T_DIAG, T_SPARE],
  cost=dict(scenarios["SCN-049"]["cost_impact"]),
  downtime=scenarios["SCN-049"]["downtime_hours"], safety=scenarios["SCN-049"]["safety_class"],
  mode="filter_clog",
  cost_basis_note="ACTUAL-MODE economics taken from the spine's own filter-clog scenario SCN-049 (EAF.AUX.HYD01, USD 2,395 / 4+4h / P4), NOT the parent SCN-048 servo-silting block (USD 137,700 / P2). A filter-element change is a minor maintenance task, far below the AGC-loss/cobble economics of servo silting.")

# (13) EAF HPU oil over-temp / cooler fault
tprompt2(
  "EAF HPU JSR.MS.EAF1.HYD.OIL.TEMP at 70 degC (alarm; normal 40-50), cleanliness and water normal. Diagnose.",
  "EAF.AUX.HYD01", "SCN-048",
  ["Oil temp 70 degC at the alarm while cleanliness and water are normal.",
   "Rising oil temp with clean oil = cooler fault (lost cooling-water flow / fouled cooler core).",
   "Hot oil thins, reduces film strength and accelerates valve/seal wear.",
   "Restore cooling before contamination/wear follows."],
  "Oil over-temperature from a cooler fault (not contamination).",
  ["Check cooler cooling-water flow and temperature", "Inspect/replace the oil cooler core (COOL-CORE-01, 6wk) if fouled/leaking",
   "Verify oil temp back to 40-50 degC", "Confirm no water ingress from the cooler"],
  [sp("COOL-CORE-01")], lead1("COOL-CORE-01"),
  ["spine:EAF.AUX.HYD01/JSR.MS.EAF1.HYD.OIL.TEMP", "spine:EAF.AUX.HYD01/failure_modes", "SOP-13_eaf-hydraulic-system.md"],
  [T_SENSOR, T_DIAG, T_SPARE],
  cost={"inr": 668000, "usd": 8000},
  downtime={"planned": 4, "unplanned": 2}, safety="P3", mode="oil_temp_rise_cooler_fault",
  cost_basis_note="ACTUAL-MODE economics (oil over-temp from cooler fault), NOT the parent SCN-048 servo-silting block (USD 137,700 / P2). Restore cooling-water flow / swap the cooler core (COOL-CORE-01); cost is a cooler repair plus short HPU downtime, well below the AGC-loss/cobble economics of servo silting.")

# (14) AGC servo hysteresis / null leakage (spool wear)
tprompt2(
  "Cold-mill AGC servo JSR.CR.S2.AGC.SV.NULLLEAK at 2.0 L/min (alarm; normal 0-0.5), oil cleanliness in band. Diagnose.",
  "CRM.AGC.SV01", "SCN-048",
  ["Null leakage 2.0 L/min at the alarm while oil is clean.",
   "Rising null leakage with clean oil = mechanical spool wear (worn lands / sleeve), not silting.",
   "Worn spool increases internal leakage and hysteresis, degrading AGC precision.",
   "Cleaning won't fix wear - the valve needs bench-overhaul or replacement."],
  "Servo-valve hysteresis increase from spool wear (mechanical, not contamination).",
  ["Switch AGC to backup/manual lock", "High-pressure hydraulic LOTO (200-350 bar)",
   "Bench-test the valve; if spool/sleeve worn, replace (SERVO-VLV-D661, 10wk, stock 1)", "Match null offset and step-response test vs OEM"],
  [sp("SERVO-VLV-D661")], lead1("SERVO-VLV-D661"),
  ["spine:CRM.AGC.SV01/JSR.CR.S2.AGC.SV.NULLLEAK", "spine:CRM.AGC.SV01/failure_modes", "SOP-11_agc-servo-valve-hydraulic-clean.md"],
  [T_SENSOR, T_DIAG, T_SPARE],
  mode="servo_valve_hysteresis_increase",
  cost_basis_note="Cost/downtime/safety reuse the parent SCN-048 block (USD 137,700 / 2+6h / P2) DELIBERATELY: hysteresis from spool wear is a sibling mode to servo silting but the remediation is the SAME D661 valve bench-overhaul/replacement on the same AGC circuit, with the same AGC-loss/cobble exposure - so the event-class economics are genuinely equal. failure_mode is corrected to the actual spool-wear/hysteresis mode.")

# (15) F3 bearing inner-race spall (BPFI) - early differential
tprompt2(
  "F3 work-roll bearing AE elevated and envelope shows a BPFI tone (not BPFO), temp normal. Diagnose.",
  "HSM.F3.WR.BRG01", "SCN-037",
  ["AE elevated (leading indicator) with the envelope energy at the inner-race ball-pass frequency (BPFI), not BPFO.",
   "BPFI with sidebands at 1x shaft = inner-race fatigue spall (ISO 15243), a sibling mode to the outer-race spall.",
   "Temperature still normal = early stage, before friction heating.",
   "Same repair path as outer-race spall - bearing replacement."],
  "Inner-race fatigue spall (BPFI), early stage. Same remediation as outer-race spall.",
  ["Confirm BPFI vs BPFO in the envelope spectrum against the bearing geometry", "Trend AE + envelope; plan a controlled stop before temp rises",
   "Bearing replacement per SOP-01 (BRG-LRG-300, SEAL-LAB-01, CPL-EL-01)", "Verify <2.3 mm/s and <70 degC at 60 min"],
  [sp("BRG-LRG-300"), sp("SEAL-LAB-01")], lead1("BRG-LRG-300") + "; " + lead1("SEAL-LAB-01"),
  ["spine:HSM.F3.WR.BRG01/failure_modes", "spine:SCN-037", "SOP-01_bearing-replacement.md"],
  [T_TREND, T_DIAG, T_SPARE],
  mode="inner_race_fatigue_spall_BPFI",
  cost_basis_note="Cost/downtime/safety reuse the parent SCN-037 block (USD 90,000 / 5+12h / P2) DELIBERATELY: inner-race spall (BPFI) is a sibling fault mode to the outer-race spall but its remediation is the IDENTICAL bearing replacement (same spares, same SOP-01, same labour), so the event-class economics are genuinely equal - not an inherited mismatch. failure_mode is corrected to the actual BPFI mode.")

# (16) Gearbox scuffing/micropitting (early GMF + Fe rise)
tprompt2(
  "F1 gearbox GMF vibration 6.5 mm/s (warning 6), Fe 18 ppm (warning 15), oil temp 82 degC. Diagnose.",
  "HSM.F1.GBX01", "SCN-038",
  ["GMF vibration 6.5 mm/s just over the 6 warning, Fe 18 ppm over the 15 warning, oil temp 82 degC over the 80 warning.",
   "Mild GMF rise + fine ferrous particles + elevated oil temp = scuffing/micropitting, an early surface-distress mode.",
   "Driven by marginal lubrication (thin film at high oil temp), not yet a tooth crack.",
   "Catchable in the warning band - address lubrication before it escalates to fatigue cracking."],
  "Gear scuffing / micropitting (early surface distress), distinct from a tooth fatigue crack.",
  ["Investigate lubrication: oil viscosity, supply temp and flow", "Cool the oil / verify cooler; change to fresh OIL-VG220 if degraded",
   "Replace filter (FLT-GBX-01); increase ferrography frequency", "Trend GMF + Fe; if GMF heads to 10 or Fe to 40, treat as fatigue"],
  [sp("OIL-VG220"), sp("FLT-GBX-01")], lead1("OIL-VG220") + "; " + lead1("FLT-GBX-01"),
  ["spine:HSM.F1.GBX01/failure_modes", "spine:SCN-038", "SOP-02_gearbox-oil-gear-service.md"],
  [T_SENSOR, T_DIAG, T_SPARE],
  cost={"inr": 835000, "usd": 10000},
  downtime={"planned": 4, "unplanned": 0}, safety="P3", mode="gear_scuffing_micropitting",
  cost_basis_note="ACTUAL-MODE economics (early gear scuffing / micropitting), NOT the parent SCN-038 tooth-fatigue-crack block (USD 600,000 / 168h / P2). Caught in the warning band: a lubrication fix (oil change OIL-VG220 + filter, cool the oil) at a planned window prevents escalation; no gear-wheel replacement, so far below the custom-gear-swap economics of a tooth fatigue crack.")

# (17) Combustion imbalance / excess air (furnace)
tprompt2(
  "Reheat furnace flue O2 at 5.2% (high warning 5.0), flame signal 92% (still healthy), zone temp normal. Diagnose.",
  "RHF.ZONE.SOAK", "SCN-046",
  ["Flue O2 5.2% just over the 5.0 high warning while flame signal is healthy (92%) and zone temp normal.",
   "Excess O2 with a stable flame = combustion imbalance / excess air (too much air for the fuel), not a burner failure.",
   "Excess air wastes fuel and lowers efficiency but is not a flame-safety event.",
   "Re-tune the fuel-air ratio - no parts needed unless a damper/actuator is faulty."],
  "Combustion imbalance / excess air (efficiency, not safety). Re-tune fuel-air ratio.",
  ["Re-tune the burner fuel-air ratio toward 1.5-3.5% O2", "Check air-damper actuator calibration",
   "Verify flue O2 back into the 1.5-3.5% band", "Monitor specific fuel consumption"],
  [], "n/a (tuning; replace BURN-NOZ-01 only if a nozzle is faulty)",
  ["spine:RHF.ZONE.SOAK/JSR.RHF.Z3.FLUE.O2", "spine:RHF.ZONE.SOAK/failure_modes", "SOP-12_furnace-burner-refractory.md"],
  [T_SENSOR, T_DIAG],
  cost={"inr": 250500, "usd": 3000},
  downtime={"planned": 0, "unplanned": 0}, safety="P4", mode="combustion_imbalance_excess_air",
  cost_basis_note="ACTUAL-MODE economics (combustion imbalance / excess air - efficiency, not safety), NOT the parent SCN-046 burner-failure block (USD 12,000 / P2). A fuel-air ratio re-tune with no downtime and no parts; cost is marginal excess-fuel consumption only. Safety_class is P4 (efficiency), not the P2 flame-safety class of an actual burner failure.")

# (18) Ladle crane overload (load %SWL)
tprompt2(
  "Ladle crane JSR.MS.CRN01.LOAD.SWL reading 110 %SWL, rope MFL normal. What happens and what do I do?",
  "MS.LDC.CRN01", "SCN-047",
  ["Hoist load 110 %SWL is at the power-cut threshold for this molten-metal ladle crane (alarm 95, cut 110).",
   "At 110% the hoist drive cuts power automatically (FEM 1.001 / BS EN 13135 molten-metal profile).",
   "Rope MFL normal, so the rope is fine - this is an overload/load-data event, not a rope-discard case.",
   "P1 by asset class (molten metal), but the protection acted correctly."],
  "Hoist overload at the 110% power-cut limit (protection acted). Verify load data before any lift.",
  ["Do not override the power cut", "Verify the actual ladle weight vs the load-cell reading (calibration check)",
   "If genuinely overloaded, reduce load; if a sensor fault, recalibrate the load cell", "Competent Person sign-off before returning to molten-metal duty"],
  [], "n/a (load verification / load-cell calibration)",
  ["spine:MS.LDC.CRN01/JSR.MS.CRN01.LOAD.SWL", "spine:MS.LDC.CRN01", "SOP-10_crane-wire-rope-brake.md"],
  [T_SENSOR, T_THRESH, T_DIAG],
  cost={"inr": 167000, "usd": 2000},
  downtime={"planned": 1, "unplanned": 0}, safety="P1",
  cost_basis_note="ACTUAL-EVENT economics (hoist overload at the 110% power-cut: protection acted, a load-data / load-cell-calibration check), NOT the parent SCN-047 wire-rope / ladle-drop block (USD 1,000,000 / P1). Safety_class stays P1 (molten-metal crane), but the rope MFL is normal so this is NOT a rope-discard event - the direct cost is a load-cell calibration / load-verification stop, not a rope replacement or ladle drop.")

# (19-21) Early-warning-band triage prompts (plan, don't panic)
# Each carries CAUGHT-EARLY economics for the actual warning-band mode rather than the
# parent scenario's run-to-failure block (the warning-band action is monitor + pre-stage).
for (prompt, aid, scn, chain, diag, res, part, ref, mode, cost, dt, sfty, cbn) in [
  ("F3 work-roll bearing AE at 6.5 dBuV (warning 6), BPFO and temp normal. Action?",
   "HSM.F3.WR.BRG01", "SCN-037",
   ["AE 6.5 dBuV just over the 6 warning, the leading spall indicator.",
    "BPFO and temp normal = stage-1 onset, weeks before any vibration change.",
    "Per the SCN-037 RTF there's roughly a 4-week window from here."],
   "Stage-1 bearing surface distress (AE warning only). Plan, don't stop.",
   ["Increase AE + envelope BPFO trending frequency", "Plan a bearing change at the next window if BPFO starts rising",
    "Pre-stage spares (BRG-LRG-300, on shelf)"],
   "BRG-LRG-300", "RCA-001-HSM-F3-WR-BRG01-BPFO-spall.md",
   "outer_race_fatigue_spall_BPFO", {"inr": 0, "usd": 0}, {"planned": 0, "unplanned": 0}, "P3",
   "CAUGHT-EARLY economics: at AE-warning only the action is increased trending + spares pre-stage (no stop, no cost yet), NOT the parent SCN-037 run-to-failure block (USD 90,000 / P2). If BPFO + temp later confirm the spall, the SCN-037 controlled-stop economics apply; this record is the stage-1 monitoring case."),
  ("BF cooling-water pump head deviation -7% (warning), vibration normal. Action?",
   "BF.CW.PMP02", "SCN-041",
   ["Head deviation -7% at the warning (negative = wear) with normal vibration.",
    "Early impeller/wear-ring wear - efficiency dropping, no mechanical distress yet.",
    "Plannable on a criticality-1 asset; pre-stage spares."],
   "Early impeller/wear-ring wear (warning-band head loss).",
   ["Trend head deviation and efficiency", "Pre-stage IMP-CW-01 + WRING-CW-01",
    "Plan a standby changeover + rebuild before head deviation reaches -12%"],
   "IMP-CW-01", "RCA-019-BF-CW-PMP02-impeller-wear.md",
   "impeller_wear_erosion", {"inr": 2500000, "usd": 29940}, {"planned": 4, "unplanned": 0}, "P2",
   "ACTUAL-MODE economics (early impeller/wear-ring wear on BF.CW.PMP02, RCA-019), NOT the parent SCN-041 compressor-surge block (USD 6,000,000 / 96h / P1). A planned standby-changeover + impeller/wear-ring rebuild, comparable to the BF.CW.PMP02 bearing scenario SCN-050 (USD 29,940 / P2); caught in the warning band so lower-urgency than even that."),
  ("Cold-mill AGC oil at ISO 16/14/11 (warning), position error 1.4% (warning 1.5). Action?",
   "CRM.AGC.SV01", "SCN-048",
   ["Oil at ISO 16/14/11 (warning) and position error 1.4% just under the 1.5 warning.",
    "Early silting onset - oil dirtier than the 15/13/10 target, valve starting to hunt.",
    "Filter + kidney-loop now prevents the full silting failure."],
   "Early servo silting onset (warning-band cleanliness).",
   ["Change 3um + 10um filters (FLT-SERVO-3 on shelf)", "Kidney-loop the oil back to ISO 15/13/10",
    "Trend cleanliness + position error; protect the single spare valve"],
   "FLT-SERVO-3", "RCA-012-CRM-AGC-SV01-servo-silting.md",
   "servo_valve_silting_spool_wear", {"inr": 250500, "usd": 3000}, {"planned": 2, "unplanned": 0}, "P3",
   "CAUGHT-EARLY economics: at warning-band cleanliness the action is a filter change + kidney-loop (FLT-SERVO-3) with no AGC loss, NOT the parent SCN-048 full-silting block (USD 137,700 / P2). If silting progresses to a gauge excursion the SCN-048 economics apply; this record is the early-onset prevention case."),
]:
    tprompt2(prompt, aid, scn, chain, diag, res, [sp(part)], lead1(part),
             ["spine:" + scn, ref], [T_SENSOR, T_THRESH, T_DIAG, T_SPARE],
             cost=cost, downtime=dt, safety=sfty, mode=mode, cost_basis_note=cbn)

# (22-24) More NORMAL / healthy-baseline triage prompts
for (prompt, asset_id, scn_norm, vals, refs) in [
  ("F1 main motor: MCSA sideband -58 dBc, winding 118 degC, current imbalance 0.6%. Status?",
   "HSM.F1.MTR01", "SCN-003", "MCSA -58 dBc (band -70..-50), winding 118 (80-130), imbalance 0.6% (0-1)",
   ["spine:SCN-003"]),
  ("HP descale pump: discharge 200 bar, casing vibration 1.0 mm/s. Status?",
   "HSM.DSC.PMP01", "SCN-004", "discharge 200 bar (190-210), casing vib 1.0 (0.5-1.5)",
   ["spine:SCN-004"]),
  ("Caster mould: TC delta 12 degC, level deviation 1.0 mm, heat flux 1.6 MW/m2. Status?",
   "CCM.MOLD.01", "SCN-007", "TC delta 12 (0-20), level 1.0 (-2..2), heat flux 1.6 (1.2-2.0)",
   ["spine:SCN-007"]),
  ("Reheat furnace soak zone: zone temp 1240 degC, flue O2 2.4%, flame 96%. Status?",
   "RHF.ZONE.SOAK", "SCN-010", "zone 1240 (1180-1280), O2 2.4 (1.5-3.5), flame 96 (90-100)",
   ["spine:SCN-010"]),
  ("Ore conveyor: motor current 78 %FLA, idler temp 42 degC, belt-edge 5 mm. Status?",
   "RM.CONV.ORE01", "SCN-009", "current 78 (60-95), idler 42 (25-60), edge 5 (-15..15)",
   ["spine:SCN-009"]),
  ("EAF HPU: oil temp 46 degC, filter DP 1.0 bar. Status?",
   "EAF.AUX.HYD01", "SCN-011", "oil 46 (40-50), filter DP 1.0 (0-1.5)",
   ["spine:SCN-011"]),
]:
    ts.append({
        "prompt": prompt, "asset_id": asset_id, "scenario_id": scn_norm,
        "failure_mode": "none", "safety_class": "P4",
        "diagnostic_reasoning_chain": [
            f"Readings: {vals}.",
            "All monitored parameters are inside their normal bands - no threshold crossed.",
            "No degradation trend present; signature matches healthy steady-state."],
        "diagnosis": "NORMAL / healthy steady-state. No action beyond routine monitoring.",
        "correct_resolution": ["Continue routine condition monitoring", "Trend baseline to CMMS"],
        "parts_required": [], "lead_time": "n/a",
        "downtime_hours": {"planned": 0, "unplanned": 0},
        "cost_impact": {"inr": 0, "usd": 0},
        "grounding_refs": refs, "expected_tools": [T_SENSOR, T_THRESH, T_DIAG],
    })

# (25) Descale pump impeller wear/erosion (flow + head drop)
tprompt2(
  "HP descale pump JSR.HR.DSC.PMP01.FLOW.DIS at 352 m3/hr (alarm; normal 388-412), discharge pressure 175 bar (warning), suction normal. Diagnose.",
  "HSM.DSC.PMP01", "SCN-040",
  ["Discharge flow 352 m3/hr at the low alarm and discharge pressure 175 bar at the warning, with suction normal.",
   "Falling flow AND head with healthy suction (so not cavitation) = impeller wear/erosion from abrasive scale-laden water.",
   "Eroded impeller vanes lose the ability to develop head and flow.",
   "Plannable performance loss - replace impeller at a window."],
  "Impeller wear/erosion (performance loss), distinct from cavitation or seal failure.",
  ["Switch to standby; isolate + LOTO", "Inspect/replace the impeller (IMP-DSC-01, 8wk, stock 1)",
   "Check wear and clearances; confirm flow-vs-head back on the design curve"],
  [sp("IMP-DSC-01")], lead1("IMP-DSC-01"),
  ["spine:HSM.DSC.PMP01/JSR.HR.DSC.PMP01.FLOW.DIS", "spine:HSM.DSC.PMP01/failure_modes", "SOP-04_pump-mechanical-seal.md"],
  [T_SENSOR, T_DIAG, T_SPARE],
  cost={"inr": 1670000, "usd": 20000},
  downtime={"planned": 4, "unplanned": 0}, safety="P3", mode="impeller_wear_erosion",
  cost_basis_note="ACTUAL-MODE economics (impeller wear/erosion on HSM.DSC.PMP01), NOT the parent SCN-040 seal-failure block (USD 14,400 / P3). A planned standby-changeover + impeller replacement (IMP-DSC-01); performance loss rather than a seal blowout. Comparable order to the seal job but a distinct, planned impeller intervention.")

# (26) Descale pump bearing failure (vib + temp, no seal leak)
tprompt2(
  "HP descale pump JSR.HR.DSC.PMP01.TEMP.BRG at 100 degC (alarm), casing vibration 5.0 mm/s (alarm), no visible seal leak. Diagnose.",
  "HSM.DSC.PMP01", "SCN-040",
  ["Bearing temp 100 degC at the alarm and casing vibration 5.0 mm/s at the alarm, but no seal leak.",
   "High bearing temp + vibration WITHOUT a seal leak points to a pump bearing failure, not the mechanical seal.",
   "Bearing distress (lube/contamination/wear) raises both temp and vibration.",
   "Switch to standby; this is a bearing job (ISO 15243)."],
  "Pump bearing failure (vibration + temp, no seal leak), distinct from seal failure.",
  ["Switch to standby; isolate + LOTO", "Replace the pump bearing per Playbook 01 (hydraulic puller, induction-heat fit)",
   "Inspect lube and shaft journal; laser-align <0.05 mm", "Verify <1.5 mm/s and <70 degC before return"],
  [], "bearing per Playbook 01 (standard distributor bearing, 1-3 day if OOS)",
  ["spine:HSM.DSC.PMP01/JSR.HR.DSC.PMP01.TEMP.BRG", "spine:HSM.DSC.PMP01/failure_modes", "SOP-04_pump-mechanical-seal.md", "19_repair_playbooks.md"],
  [T_SENSOR, T_DIAG],
  cost={"inr": 2500000, "usd": 29940},
  downtime={"planned": 4, "unplanned": 8}, safety="P2", mode="pump_bearing_failure",
  cost_basis_note="ACTUAL-MODE economics (pump bearing failure on HSM.DSC.PMP01), NOT the parent SCN-040 seal-failure block (USD 14,400 / P3). Mirrors the spine's own pump-bearing scenario SCN-050 (BF.CW.PMP02, USD 29,940 / 4+8h / P2): a standby-changeover + bearing replacement per Playbook 01, distinct from the seal-only job.")

# (27) BF cooling pump mechanical seal (broadband vib)
tprompt2(
  "BF cooling-water pump JSR.BF.CW.PMP02.VIB.BB at 5.0 mm/s (alarm), head deviation normal, bearing temp normal. Diagnose.",
  "BF.CW.PMP02", "SCN-041",
  ["Broadband vibration 5.0 mm/s at the alarm while head deviation and bearing temp are normal.",
   "Broadband (not 1x) vibration with healthy head/temp points to a mechanical-seal problem (ISO 10816-7 seal band).",
   "Seal face distress generates broadband energy before head loss or bearing heating.",
   "Different mode from impeller wear (which shows head loss) - this is the seal."],
  "Mechanical seal distress (broadband vibration), distinct from impeller wear.",
  ["Switch to standby; isolate + LOTO", "Back-pullout seal change (SiC/SiC), inspect shaft sleeve",
   "Confirm shaft runout <0.05 mm TIR and broadband vibration back to <1.5 mm/s"],
  [sp("SEAL-MECH-DSC")], lead1("SEAL-MECH-DSC"),
  ["spine:BF.CW.PMP02/JSR.BF.CW.PMP02.VIB.BB", "spine:BF.CW.PMP02/failure_modes", "SOP-04_pump-mechanical-seal.md"],
  [T_SENSOR, T_DIAG, T_SPARE],
  cost={"inr": 1200000, "usd": 14400},
  downtime={"planned": 3, "unplanned": 8}, safety="P3", mode="mechanical_seal_failure",
  cost_basis_note="ACTUAL-MODE economics (mechanical-seal distress on BF.CW.PMP02), NOT the parent SCN-041 compressor-surge block (USD 6,000,000 / 96h / P1). Mirrors the spine's own pump mechanical-seal scenario SCN-040 (HSM.DSC.PMP01, USD 14,400 / 3+8h / P3): a back-pullout seal change on a standby-able pump, not a blower-destruction event.")

# (28) Caster segment roll-bearing failure (vibration, rolls still turning)
tprompt2(
  "Caster segment 7 JSR.CC1.SEG07.VIB.ROLL at 6.0 mm/s (alarm), roll rpm still ~12, force normal. Diagnose.",
  "CCM.SEG.07", "SCN-042",
  ["Roll-bearing vibration 6.0 mm/s at the alarm while the roll is still rotating (rpm ~12) and force normal.",
   "High roll-bearing vibration before seizure = roll-bearing failure in progress (not yet seized).",
   "Catching it before rpm drops to 0 avoids a strand-drag seizure event.",
   "Plan a segment change at the next opportunity."],
  "Segment roll-bearing failure (pre-seizure). Plan a change before it seizes.",
  ["Trend roll-bearing vibration; plan a segment swap before seizure", "Replace the roll bearing (BRG-SEG-01, 8wk, stock 4) and roll if scored",
   "Clean spray nozzles; set segment gap and pressure-test"],
  [sp("BRG-SEG-01")], lead1("BRG-SEG-01"),
  ["spine:CCM.SEG.07/JSR.CC1.SEG07.VIB.ROLL", "spine:CCM.SEG.07/failure_modes", "SOP-06_caster-segment-change.md"],
  [T_SENSOR, T_DIAG, T_SPARE],
  cost={"inr": 5010000, "usd": 60000},
  downtime={"planned": 8, "unplanned": 0}, safety="P2", mode="roll_bearing_failure",
  cost_basis_note="ACTUAL-MODE economics (segment roll-bearing failure caught PRE-seizure), distinct from the parent SCN-042 roll-SEIZURE block (USD 96,000 / 8h unplanned / P2). Caught at the vibration alarm before rpm drops to 0: a PLANNED segment swap (BRG-SEG-01) avoids the unplanned strand-drag seizure event, so it is cheaper and planned rather than the run-to-seizure figure.")

# (29) Mould level instability (level wave, TC/friction normal)
tprompt2(
  "Caster mould JSR.CC1.MOLD.LEVEL.DEV oscillating to 12 mm (alarm), TC delta and friction normal. Diagnose.",
  "CCM.MOLD.01", "SCN-043",
  ["Mould-level deviation oscillating to 12 mm at the alarm while TC delta and friction are normal.",
   "Level instability WITHOUT a TC V-pattern or friction spike is NOT a sticking breakout - it is a level-control problem.",
   "Causes: SEN clogging/erosion, stopper-rod control instability, or argon/bulging disturbance.",
   "Important: single-sensor level alarm alone must not trigger a breakout stop (FAR)."],
  "Mould level instability (level-control), distinct from a sticking breakout (no 3-sensor agreement).",
  ["Check stopper-rod / slide-gate control loop tuning", "Inspect SEN for clogging/erosion (replace SEN-NOZ-01 if eroded)",
   "Stabilise argon flow and casting speed", "Confirm level back within +/-2 mm; watch TC/friction for any sticking onset"],
  [sp("SEN-NOZ-01")], lead1("SEN-NOZ-01"),
  ["spine:CCM.MOLD.01/JSR.CC1.MOLD.LEVEL.DEV", "spine:CCM.MOLD.01/failure_modes", "SOP-07_mould-copper-change.md"],
  [T_SENSOR, T_DIAG, T_SPARE],
  cost={"inr": 2087500, "usd": 25000},
  downtime={"planned": 2, "unplanned": 0}, safety="P3", mode="mould_level_instability",
  cost_basis_note="ACTUAL-MODE economics (mould level-control instability - NO 3-sensor breakout agreement), NOT the parent SCN-043 sticking-breakout block (USD 860,000 / 36h / P1). A control-loop tune + SEN inspection/replace (SEN-NOZ-01); a level-control problem with surface-quality yield loss, explicitly NOT a P1 liquid-steel breakout (single-sensor level alarm must not trigger a breakout stop).")

# (30) R1 roll surface fatigue crack (AE on journal)
tprompt2(
  "Roughing stand R1 JSR.HR.R1.WR.AE.RMS at 15 dB (alarm), force ripple mildly elevated, no periodic strip marks yet. Diagnose.",
  "HSM.STD.R1", "SCN-044",
  ["Roll-journal AE 15 dB at the alarm with mildly elevated force ripple and no clear 1x periodic strip marks yet.",
   "High journal AE before a developed force-ripple/strip-mark pattern = roll surface fatigue crack initiation.",
   "AE detects sub-surface crack growth before it becomes a printing spall flat.",
   "Catch and grind before it develops into a full spall (SCN-044)."],
  "Roll surface fatigue crack (early, AE-detected), precursor to a spall flat.",
  ["Plan a work-roll change before the crack becomes a printing spall", "Quick-change rolls (WR-HSS-PREP on shelf)",
   "Roll shop: UT-inspect, grind below the crack, condemn if below min dia", "Trend journal AE + force ripple"],
  [sp("WR-HSS-PREP")], lead1("WR-HSS-PREP"),
  ["spine:HSM.STD.R1/JSR.HR.R1.WR.AE.RMS", "spine:HSM.STD.R1/failure_modes", "SOP-08_hot-strip-mill-roll-change.md"],
  [T_SENSOR, T_DIAG, T_SPARE],
  cost={"inr": 935200, "usd": 11200},
  downtime={"planned": 0.75, "unplanned": 0}, safety="P3", mode="roll_surface_fatigue_crack",
  cost_basis_note="ACTUAL-MODE economics (early AE-detected roll surface fatigue crack, precursor to a spall), distinct from the parent SCN-044 work-roll-SPALL block (USD 184,000 unplanned / P2). Caught before printing: a PLANNED quick-change + roll-shop grind below the crack equals the SCN-044 PLANNED cost (~USD 11,200) rather than the USD 184,000 run-to-failure figure (the 16.4x planned-vs-unplanned gap cited in SCN-044).")


# ---------------------------------------------------------------------------
# (C) multiturn_conversations.jsonl -- 3-6 turn engineer<->wizard dialogues
# ---------------------------------------------------------------------------

def convo(conv_id, asset_id, scn_id, turns):
    mt.append({
        "conversation_id": conv_id,
        "asset_id": asset_id,
        "scenario_id": scn_id,
        "turns": turns,
    })

def u(text): return {"role": "user", "content": text}
def a(text, tools, refs):
    return {"role": "assistant", "content": text, "tools_used": tools, "grounding_refs": refs}

# Build one multi-turn convo per FAILURE scenario (12) + variants to reach ~50.
# 1
convo("CONV-001", "HSM.F3.WR.BRG01", "SCN-037", [
  u("Hey wizard, I'm getting an AE warning on the F3 work-roll bearing. Should I be worried?"),
  a("Let me check. JSR.HR.STD3.WR.BRG01.AE.RMS is at 8 dBuV - between the AE warning (6) and alarm (12), so stage-2 onset. AE is the leading indicator here and crosses warning weeks before vibration. Not an emergency yet, but it warrants close watching.",
    [T_SENSOR, T_THRESH, T_KB], ["spine:SCN-037/sensor_signature", "RCA-001-HSM-F3-WR-BRG01-BPFO-spall.md"]),
  u("What about the vibration and temperature?"),
  a("Envelope BPFO is 3.2 g - above its 3.0 g alarm - and bearing temp is 102 degC, past the 100 degC trip. So all three sensors now agree: AE -> BPFO -> temp. That is the SCN-037 outer-race spall signature, now advanced (stage 4).",
    [T_SENSOR, T_TREND], ["spine:SCN-037"]),
  u("Okay so what do I actually do?"),
  a("This is now a controlled-stop condition (temp >100 degC), not an emergency trip. LOTO and confirm zero-energy per SOP-01, use a hydraulic puller (never strike the bearing), inspect the journal vs OEM H7/k6 and regrind if worn, induction-heat the new bearing to 80-100 degC, laser-align <0.05 mm, replace the labyrinth seal and coupling element, then verify <2.3 mm/s and <70 degC at 60 min.",
    [T_SOP, T_KB], ["spine:SCN-037/correct_resolution", "SOP-01_bearing-replacement.md"]),
  u("Do we have the parts?"),
  a("Yes: BRG-LRG-300 (large-bore roller bearing) - stock 1, 8-week lead, so we use our one on-shelf unit; SEAL-LAB-01 - stock 2, 2-week; CPL-EL-01 - stock 1, 2-week. All in stock for this job. Recommendation: schedule the controlled stop now; an unplanned spall failure runs ~USD 90k (range 80-250k). Want me to raise the work order?",
    [T_SPARE, T_COST, T_WO], ["spine:SCN-037/spares_required", "spine:SCN-037/cost_impact", "spine:spare/BRG-LRG-300"]),
])

# 2
convo("CONV-002", "HSM.F1.GBX01", "SCN-038", [
  u("F1 gearbox vibration alarm just came in. What's the reading?"),
  a("JSR.HR.STD1.GBX01.VIB.GMF.RMS is at 11 mm/s, above the 10 mm/s alarm. That is a gross gear-mesh fault. Let me pull the oil data too.",
    [T_SENSOR, T_THRESH], ["spine:SCN-038/sensor_signature"]),
  u("Yeah the chip detector also tripped."),
  a("That fits. Ferrous count is 60 ppm (alarm 40) and the chip-detector trip means chunky spall debris. GMF + chip + 60 ppm Fe is a tooth-root fatigue crack with active spalling - consistent with RCA-002, usually after a high-torque cobble.",
    [T_SENSOR, T_DIAG, T_RCA], ["spine:SCN-038/root_cause", "RCA-002-HSM-F1-GBX01-gear-tooth-fatigue.md"]),
  u("How urgent?"),
  a("Immediate controlled stop, no deferral - a fractured tooth can wreck the shaft. Crane the gearbox to the repair bay, replace the gear wheel + bearings, set backlash 0.1-0.3 mm, confirm Prussian-blue contact >70%, run-in at low load (SOP-02).",
    [T_SOP], ["spine:SCN-038/correct_resolution", "SOP-02_gearbox-oil-gear-service.md"]),
  u("Parts and timeline?"),
  a("Here's the problem: GEAR-WHL-M20 (custom large-module gear wheel) is 0 stock with a 36-week lead - the critical path. BRG-GBX-SET is stock 1, 3-week. Unplanned cost is ~USD 600k (range 500k-3M) with ~168h downtime, largely because of that gear-wheel lead time. Recommendation: stop now, and I'd flag raising the gear-wheel as a stocked insurance spare going forward. Shall I open the work order and a stocking review?",
    [T_SPARE, T_COST, T_WO], ["spine:SCN-038/cost_impact", "spine:spare/GEAR-WHL-M20"]),
])

# 3
convo("CONV-003", "HSM.F1.MTR01", "SCN-039", [
  u("MCSA flagged something on the F1 main motor. What's going on?"),
  a("JSR.HR.STD1.MTR01.MCSA.RBAR.SB is at -34 dBc, just past the -35 dBc alarm. That points to a broken rotor bar - sidebands at (1+/-2s)*f1 (IEEE 1415).",
    [T_DIAG, T_THRESH], ["spine:SCN-039/sensor_signature"]),
  u("Is the motor about to fail?"),
  a("Not instantly. Body vibration is 4.8 mm/s (above 4.5 warning) from 2x-slip modulation. Broken bars progress over 2-4 weeks (RCA-003), so you have a planning window - confirm with MCSA at steady load first.",
    [T_SENSOR, T_TREND, T_RCA], ["spine:SCN-039/degradation_timeline", "RCA-003-HSM-F1-MTR01-broken-rotor-bar.md"]),
  u("What's the plan, and do we have a spare motor?"),
  a("Plan a controlled swap within 2-4 weeks using our insurance spare MTR-MV-6000 (stock 1, on shelf). Do NOT order a new one - new lead is 40 weeks. Send the failed motor for a rotor-bar test + rewind (RWND-KIT-MV, 3-week) and return it to spare stock. Verify phase rotation before energising the spare (SOP-03). Swap is a planned 10h, ~USD 100k labour+lost-production. Want me to schedule it?",
    [T_SPARE, T_SOP, T_WO], ["spine:SCN-039/correct_resolution", "spine:spare/MTR-MV-6000", "SOP-03_motor-rewind-swap.md"]),
])

# 4
convo("CONV-004", "BF.BLW.FAN01", "SCN-041", [
  u("URGENT - BF blower is surging. Pressure oscillation just hit 9%."),
  a("Confirmed surge: pressure oscillation 9% is above the 8% alarm and shaft displacement is 95 um (warning 80). First - verify the anti-surge valve has auto-opened. Is the ASV open?",
    [T_SENSOR, T_THRESH], ["spine:SCN-041/sensor_signature", "spine:SCN-041/correct_resolution"]),
  u("ASV is cycling but surge isn't clearing."),
  a("If surge persists beyond 2-3 cycles you must TRIP the blower immediately - sustained surge can destroy the machine in seconds (P1). Do NOT restart until the cause is identified. Likely a downstream valve slam or inlet filter fouling pushing the operating point left of the surge line (RCA-005).",
    [T_DIAG, T_RCA], ["spine:SCN-041/root_cause", "RCA-005-BF-BLW-FAN01-compressor-surge.md"]),
  u("Trip done. Now what?"),
  a("Borescope the IGVs and impellers, run ferrography on the oil, and recalibrate the anti-surge line vs OEM data before any restart. Be aware: ASV-VLV-01 and journal pads (BRG-JRNL-PAD) are 12-week, 0-1 stock items, so inspect before assuming a swap. This event class is ~USD 6M (range 4-8M) with BF downtime ~USD 500k/hr - escalate to the BF manager now.",
    [T_SOP, T_SPARE, T_COST], ["spine:SCN-041/cost_impact", "spine:spare/ASV-VLV-01"]),
])

# 5
convo("CONV-005", "CCM.MOLD.01", "SCN-043", [
  u("BPS just threw a P1 breakout alarm on Caster 1 mould. TC delta is high. Real or false?"),
  a("Check all three. TC delta is 55 degC (alarm 50) in a downward-propagating V-pattern. But breakout confirmation needs 3-sensor agreement - what are oscillator friction and mould level?",
    [T_SENSOR, T_DIAG], ["spine:SCN-043/sensor_signature", "spine:SCN-043/root_cause"]),
  u("Friction is 19 kN and level deviation 13 mm."),
  a("All three are over alarm (friction 18, level 12). That is a TRUE sticking breakout - single-sensor FAR is >40%, but 3-sensor agreement is reliable (RCA-007). Shell rupture can follow ~60-90s after the BPS alarm. Act now.",
    [T_DIAG, T_RCA], ["spine:SCN-043", "RCA-007-CCM-MOLD01-breakout-sticking.md"]),
  u("What's the immediate action?"),
  a("Reduce casting speed to the minimum 0.5 m/min immediately. If it keeps escalating, full emergency stop - halt withdrawal and close the tundish gate - and EVACUATE the caster floor; liquid steel is fatal. Do not operate until steel has solidified 4-6h+.",
    [T_SOP], ["spine:SCN-043/correct_resolution", "SOP-07_mould-copper-change.md"]),
  u("And recovery afterward?"),
  a("After solidification: remove the skull, replace damaged segments and mould copper if scored (MOLD-CU-STD is stock 1 but 14-week lead - the long pole), replace consumable SEN (SEN-NOZ-01) and any damaged strand-guide roll (ROLL-SEG-STD). Run a 5-whys RCA within 48h. Event cost ~USD 860k (range 200k-3M+), 36h downtime. I'll log the incident and draft the RCA template.",
    [T_SPARE, T_COST, T_WO], ["spine:SCN-043/spares_required", "spine:SCN-043/cost_impact", "spine:spare/MOLD-CU-STD"]),
])

# 6
convo("CONV-006", "MS.LDC.CRN01", "SCN-047", [
  u("The ladle crane rope monitor is reading high. Is the rope still safe to use?"),
  a("No - JSR.MS.CRN01.ROPE.MFL is at 320 mV, above the 300 mV alarm (~>15-20% LMA). Per ISO 4309:2017 that is at/over discard. The crane should be taken out of service.",
    [T_SENSOR, T_THRESH, T_KB], ["spine:SCN-047/sensor_signature", "SOP-10_crane-wire-rope-brake.md"]),
  u("But the load was only 85%, isn't that fine?"),
  a("The load (85% SWL) is within normal - alarm is 95% - so the load isn't the issue; the ROPE is. Discard is independent of load: MFL >15-20% LMA, OR >=12 random broken wires in one lay length (>=4 in one strand), OR diameter reduction >-7% (RCA-011). Any one criterion = discard. On a molten-metal crane this is P1 - a ladle drop is catastrophic.",
    [T_DIAG, T_RCA], ["spine:SCN-047/root_cause", "RCA-011-MS-LDC-CRN01-wire-rope-fatigue.md"]),
  u("Okay, taking it offline. What's the replacement procedure?"),
  a("If any load is suspended, lower it under control first. Then a Competent Person inspects and certifies, replace the rope (ROPE-CRN-01, stock 1, 6-week), inspect drum/sheave grooves, keep fleet angle <4 deg, and terminate with a wedge socket (SOCK-WEDGE-01, on shelf) - not clips (SOP-10). I'll raise the out-of-service work order and the Competent Person request.",
    [T_SOP, T_SPARE, T_WO], ["spine:SCN-047/correct_resolution", "spine:spare/ROPE-CRN-01"]),
])

# 7
convo("CONV-007", "HSM.DSC.PMP01", "SCN-040", [
  u("Descale pump is vibrating and there's a leak at the seal area. Diagnose?"),
  a("Casing vibration JSR.HR.DSC.PMP01.VIB.CAS.RMS is 5.4 mm/s (alarm 5.0) and bearing temp is 90 degC (warning 85). With a spraying leak, that's mechanical seal failure - face wear from abrasive scale-laden water (RCA-004).",
    [T_SENSOR, T_DIAG, T_RCA], ["spine:SCN-040/sensor_signature", "RCA-004-HSM-DSC-PMP01-mechanical-seal.md"]),
  u("Can I keep running it?"),
  a("No - switch to the standby pump. This isn't an emergency trip (standby available) but the seal is failing. Isolate + LOTO, drain the casing, back-pullout seal change, inspect the shaft sleeve (replace if >0.1 mm scoring), fit a new SiC/SiC seal fingerprint-free, runout <0.05 mm TIR (SOP-04).",
    [T_SOP], ["spine:SCN-040/correct_resolution", "SOP-04_pump-mechanical-seal.md"]),
  u("Parts?"),
  a("SEAL-MECH-DSC (SiC/SiC cartridge) - stock 2, 2-week; SLV-SHAFT-01 (shaft sleeve) - stock 1, 3-week if scoring exceeds 0.1 mm. Event cost ~USD 14.4k, 8h unplanned / 3h planned. Both in stock - want the work order?",
    [T_SPARE, T_COST, T_WO], ["spine:SCN-040/spares_required", "spine:spare/SEAL-MECH-DSC"]),
])

# 8
convo("CONV-008", "CCM.SEG.07", "SCN-042", [
  u("Segment 7 roll rpm just dropped to zero and force is climbing. We're mid-cast."),
  a("Roll rpm 0 (alarm 0) = roll seizure, and clamping force 540 kN (warning 480, alarm 550) confirms the seized roll is dragging the strand - thermal/water-scale bearing seizure (RCA-006). Risk of transverse slab cracks and breakout.",
    [T_SENSOR, T_DIAG, T_RCA], ["spine:SCN-042/sensor_signature", "RCA-006-CCM-SEG07-roll-seizure.md"]),
  u("We're still in the liquid-core zone. What do I do first?"),
  a("Reduce casting speed first (you're in liquid-core), then end the heat and let the strand cool 2-4h before anyone enters the bay. Withdraw the segment with the handling crane (SOP-06).",
    [T_SOP], ["spine:SCN-042/correct_resolution", "SOP-06_caster-segment-change.md"]),
  u("Parts for the segment rebuild?"),
  a("ROLL-SEG-STD (strand guide roll) - stock 2, 12-week lead (use shelf stock); BRG-SEG-01 (segment roll bearing) - stock 4, 8-week; NOZ-SPRAY-01 (consumable nozzles) - on shelf. Set the segment gap per slab format and pressure-test before return. Event ~USD 96k, 8h unplanned. Logging the incident now.",
    [T_SPARE, T_COST, T_WO], ["spine:SCN-042/spares_required", "spine:spare/ROLL-SEG-STD"]),
])

# 9
convo("CONV-009", "HSM.STD.R1", "SCN-044", [
  u("R1 is leaving periodic marks on the strip every revolution. Force ripple looks high."),
  a("Force ripple JSR.HR.R1.FORCE is 8.5% (alarm 8) and it's periodic at 1x roll - period = pi*D. With chock vibration at 6 mm/s and periodic strip marks, that's a work-roll spall flat (RCA-008).",
    [T_SENSOR, T_DIAG, T_RCA], ["spine:SCN-044/sensor_signature", "RCA-008-HSM-STD-R1-work-roll-spall.md"]),
  u("Should I finish this coil or stop?"),
  a("Stop rolling on spall-printed product and segregate the affected strip - the marks are scrap-grade and there's a spall-fragment ejection risk. Then quick-change the work rolls (15-45 min).",
    [T_SOP], ["spine:SCN-044/correct_resolution", "SOP-08_hot-strip-mill-roll-change.md"]),
  u("Cost of doing it now vs waiting?"),
  a("Big difference: planned change ~USD 11.2k vs unplanned ~USD 184k - a 16.4x penalty. WR-HSS-PREP (prepared roll pair) is on shelf (stock 4), so a quick change now is cheap insurance. Send the spalled roll to the roll shop to grind 3-5 mm below the spall, UT-test, condemn if below min dia. Raising the roll-change order.",
    [T_SPARE, T_COST, T_WO], ["spine:SCN-044/cost_impact", "spine:spare/WR-HSS-PREP"]),
])

# 10
convo("CONV-010", "RM.CONV.ORE01", "SCN-045", [
  u("Conveyor idler ultrasound and temp alarms both came in. How bad?"),
  a("Bad - ultrasound is +16 dBuV (alarm +15) and idler temp is 100 degC, right at the fire-risk alarm. A dry/failed idler bearing seizing under the loaded belt is the #1 belt-fire initiator (RCA-009). P1.",
    [T_SENSOR, T_THRESH, T_RCA], ["spine:SCN-045/sensor_signature", "RCA-009-RM-CONV-ORE01-idler-bearing.md"]),
  u("Stopping the belt. Safe to send someone in?"),
  a("Stop the belt immediately (done - good), then LOTO and apply a belt-tension lock before anyone enters. Only then lift the belt and replace the idler with the correct width/trough/rating, and confirm free rotation before restart (SOP-09).",
    [T_SOP], ["spine:SCN-045/correct_resolution", "SOP-09_conveyor-idler-belt.md"]),
  u("Parts?"),
  a("IDLER-STD-1600 (standard carrying idler) - stock 40, zero lead, so swap immediately. Direct event cost ~USD 7.5k for an idler caught before fire propagation; a full conveyor-fire loss would be far higher. Logging it.",
    [T_SPARE, T_COST, T_WO], ["spine:SCN-045/cost_impact", "spine:spare/IDLER-STD-1600"]),
])

# 11
convo("CONV-011", "RHF.ZONE.SOAK", "SCN-046", [
  u("Flame signal on furnace soak zone is dropping and flickering. What's happening?"),
  a("Flame scanner signal JSR.RHF.Z3.FLAME.SIG is at 38% - below the 40% cutoff (lower is worse) - and flue O2 is 5.8% (alarm 6.0). That's a fuel-side burner failure: nozzle fouling or gas-supply fluctuation giving an unstable flame (RCA-010).",
    [T_SENSOR, T_DIAG, T_RCA], ["spine:SCN-046/sensor_signature", "RCA-010-RHF-ZONE-SOAK-burner-failure.md"]),
  u("The fuel cut off automatically. Can I just relight?"),
  a("Not directly - you MUST purge the furnace before re-light to clear unburnt fuel, or you risk an explosion (EN 746-2). After purge, clean/replace the burner nozzle and flame scanner, then re-tune the fuel-air ratio (SOP-12).",
    [T_SOP], ["spine:SCN-046/correct_resolution", "SOP-12_furnace-burner-refractory.md"]),
  u("Parts on hand?"),
  a("BURN-NOZ-01 (burner nozzle) - stock 4, 4-week; FLAME-SCAN-01 (flame scanner) - stock 2, 3-week. Both in stock. Event ~USD 12k, 6h unplanned. Want me to raise the burner-service order?",
    [T_SPARE, T_COST, T_WO], ["spine:SCN-046/spares_required", "spine:spare/BURN-NOZ-01"]),
])

# 12
convo("CONV-012", "CRM.AGC.SV01", "SCN-048", [
  u("Cold mill gauge is wandering and the AGC servo seems to be hunting. Ideas?"),
  a("Let me check the servo. Position error JSR.CR.S2.AGC.SV.POSERR is 3.2% (alarm 3.0) and strip-gauge deviation is 22 um (alarm 20). What's the oil cleanliness reading?",
    [T_SENSOR, T_DIAG], ["spine:SCN-048/sensor_signature"]),
  u("ISO is 17/15/12."),
  a("That's the alarm code - much dirtier than the 15/13/10 servo target. Silt (1-5 um) is plugging the spool's 1-3 um clearance, giving sluggish small-amplitude response = servo-valve silting/spool wear (RCA-012). The hunting + gauge excursion follow directly.",
    [T_KB, T_RCA], ["spine:SCN-048/root_cause", "RCA-012-CRM-AGC-SV01-servo-silting.md"]),
  u("How do I fix it without trashing my one spare valve?"),
  a("Good instinct - SERVO-VLV-D661 is stock 1, 10-week lead. Switch AGC to backup/manual lock, do a high-pressure hydraulic LOTO (200-350 bar), remove the valve and ultrasonic bench-clean it (only replace if scored), match the null offset on reinstall, change the 3 um + 10 um filters (FLT-SERVO-3 on shelf), kidney-loop the oil back to ISO 15/13/10, then step-response test vs OEM (SOP-11). That preserves the spare.",
    [T_SOP, T_SPARE], ["spine:SCN-048/correct_resolution", "spine:spare/SERVO-VLV-D661"]),
  u("And if I just left it running?"),
  a("Risky - AGC loss drives ~30% scrap increase plus cobble risk at roughly Rs 21 lakh per cobble-hour; the event class is ~USD 137.7k. Cleaning now is far cheaper. I'll raise the servo-clean + filter-change work order.",
    [T_COST, T_WO], ["spine:SCN-048/cost_impact"]),
])

# Secondary-failure-mode convos and variants to reach ~50
# 13 lube starvation
convo("CONV-013", "HSM.F3.WR.BRG01", "SCN-037", [
  u("F3 work-roll oil-film outlet temp is creeping up but the bearing vibration is fine. Concern?"),
  a("Outlet temp JSR.HR.STD3.WR.BRG01.OFB.OUT.TEMP is 80 degC (warning 75, alarm 85) while vibration is normal. That pattern is oil-film breakdown / incipient lube starvation (RCA-013), not yet a spall.",
    [T_SENSOR, T_RCA], ["RCA-013-HSM-F3-WR-BRG01-lube-starvation.md"]),
  u("Cause?"),
  a("Most likely a blocked/worn oil-film lube nozzle reducing film thickness, or low oil supply pressure to the chock. Boundary contact then raises AE and temp.",
    [T_DIAG, T_KB], ["MAN-001_rolling_mill_work_roll_bearing.md"]),
  u("Fix?"),
  a("Inspect and clear/replace the lube nozzle (LUBE-NOZ-01, stock 4, 1-week lead), verify oil supply pressure/flow to the chock, then trend OFB outlet temp + AE. If temp keeps rising toward 85 degC, escalate to a controlled stop before it cascades into a bearing spall. I can raise a lube-inspection task.",
    [T_SPARE, T_WO], ["spine:spare/LUBE-NOZ-01"]),
])

# 14 oil oxidation
convo("CONV-014", "HSM.F1.GBX01", "SCN-038", [
  u("Gearbox oil viscosity is reading high and the oil looks dark. Gears OK?"),
  a("Viscosity is 265 cSt - at the high alarm (normal 198-242) - and dark oil suggests oxidation/varnish (RCA-014). Importantly, GMF vibration is normal, so the gears themselves are healthy. This is a lubricant-condition issue.",
    [T_SENSOR, T_DIAG, T_RCA], ["RCA-014-HSM-F1-GBX01-oil-oxidation-varnish.md"]),
  u("What do I do?"),
  a("Change the oil to fresh ISO VG220 (OIL-VG220, stock 4, on shelf), replace the filter element (FLT-GBX-01, on shelf), and find the root cause - usually oil over-temperature or an over-extended service interval. Then resume ferrographic + viscosity trending.",
    [T_SOP, T_SPARE], ["SOP-02_gearbox-oil-gear-service.md", "spine:spare/OIL-VG220"]),
  u("So no gear damage?"),
  a("Correct - caught at the lubricant stage with healthy GMF, no gear/bearing replacement needed. Varnish would otherwise block filters and cut heat transfer. Cheap save. Want the oil-change task logged?",
    [T_WO], ["spine:HSM.F1.GBX01"]),
])

# 15 cavitation
convo("CONV-015", "HSM.DSC.PMP01", "SCN-040", [
  u("Descale pump suction pressure is low and there's a gravelly noise. Seal again?"),
  a("Different mode this time. Suction pressure is 70 kPa - at the low alarm (NPSH starvation) - and AE broadband is 15 dB (alarm). The gravelly noise + AE in the 100-500 kHz band is cavitation, not a seal failure (RCA-016).",
    [T_SENSOR, T_DIAG, T_RCA], ["RCA-016-HSM-DSC-PMP01-cavitation.md"]),
  u("Why is suction low?"),
  a("Insufficient NPSH - typically a clogged suction strainer or low supply level/pressure. The pump is flashing vapor and collapsing bubbles, which erodes the impeller over time.",
    [T_KB], ["MAN-004_cooling_descaling_pump.md"]),
  u("Action?"),
  a("Restore suction conditions first: check the strainer/supply and reduce speed if possible. Inspect the impeller for cavitation pitting - if eroded, replace IMP-DSC-01 (stock 1, 8-week lead). Confirm suction back above 120 kPa before sustained running. Raising the strainer-check task.",
    [T_SPARE, T_WO], ["spine:spare/IMP-DSC-01"]),
])

# 16 winding overheat
convo("CONV-016", "HSM.F1.MTR01", "SCN-039", [
  u("F1 motor winding temp is high and current looks unbalanced. Broken bar?"),
  a("Not this time. Winding temp is 150 degC (warning 145, alarm 155) and current imbalance is 3% (warning 2). MCSA sidebands are not at the broken-bar alarm. This is a winding overheat / incipient turn-short (RCA-015), a thermal/insulation issue.",
    [T_SENSOR, T_DIAG, T_RCA], ["RCA-015-HSM-F1-MTR01-winding-overheat.md"]),
  u("What's driving it?"),
  a("Likely VFD cooling/ventilation loss or a supply phase imbalance. Class-F insulation ages fast above 145 degC - roughly every extra 10 degC halves life.",
    [T_KB], ["MAN-003_large_induction_motor_vfd.md"]),
  u("Plan?"),
  a("Reduce load and check the VFD cooling and ventilation, verify phase balance at the supply, and schedule an offline PI + surge test. If insulation is degraded, plan a rewind (RWND-KIT-MV, stock 1, 3-week). Trend winding temp + imbalance and trip at the 155 degC alarm. Logging the cooling-check task.",
    [T_SPARE, T_SOP, T_WO], ["spine:spare/RWND-KIT-MV", "SOP-03_motor-rewind-swap.md"]),
])

# 17 BF cooling water impeller wear
convo("CONV-017", "BF.CW.PMP02", "SCN-041", [
  u("BF cooling-water pump head is down and it's vibrating. What's wrong?"),
  a("Differential head deviation JSR.BF.CW.PMP02.HEAD.DEV is -12% (alarm, negative = wear) and 1x vibration is ~5 mm/s (alarm 5.6). That's impeller/wear-ring erosion with some unbalance (RCA-019) - abrasive cooling water wears the impeller and opens wear-ring clearance.",
    [T_SENSOR, T_DIAG, T_RCA], ["RCA-019-BF-CW-PMP02-impeller-wear.md"]),
  u("This feeds the blast furnace cooling - how urgent?"),
  a("Criticality 1 - cooling-water loss endangers the BF. Switch to the standby pump and isolate + LOTO the affected unit before head loss compromises cooling.",
    [T_SOP], ["MAN-004_cooling_descaling_pump.md"]),
  u("Repair?"),
  a("Replace the impeller (IMP-CW-01, stock 1, 6-week) and wear-ring set (WRING-CW-01, stock 2, 4-week), then confirm head-vs-flow back on the design curve before return. Want me to schedule the standby changeover and the rebuild?",
    [T_SPARE, T_WO], ["spine:spare/IMP-CW-01", "spine:spare/WRING-CW-01"]),
])

# 18 sinter fan bearing overheat
convo("CONV-018", "SP.SINT.FAN01", "SCN-041", [
  u("Sinter main fan bearing temp alarm, but vibration is fine. Imbalance?"),
  a("No imbalance indicated - 1x vibration and duct DP are normal, only the bearing temp is at 95 degC (alarm). An isolated bearing-temp rise without vibration points to bearing overheating from a lubrication or cooling problem (RCA-020).",
    [T_SENSOR, T_DIAG, T_RCA], ["RCA-020-SP-SINT-FAN01-bearing-overheat.md"]),
  u("Likely cause?"),
  a("Grease degradation/over- or under-greasing, or loss of bearing cooling-water flow. Not a mechanical fault yet - catch it before seizure.",
    [T_KB], ["MAN-005_bf_sinter_fan_blower.md"]),
  u("Action?"),
  a("Check lubrication and cooling-water supply, re-grease per schedule. If temp persists, plan a bearing replacement (BRG-LRG-300, stock 1, 8-week lead). Keep trending bearing temp + vibration. I'll log the lube/cooling check.",
    [T_SPARE, T_WO], ["spine:spare/BRG-LRG-300"]),
])

# 19 spray nozzle blockage
convo("CONV-019", "CCM.SEG.07", "SCN-042", [
  u("Segment 7 zone spray flow dropped but the rolls are turning fine. Seizure?"),
  a("Not a seizure - roll rpm and force are normal. Spray flow is 120 L/min, at the low alarm. That's a spray-nozzle blockage in secondary cooling (RCA-021), usually scale/debris plugging nozzles.",
    [T_SENSOR, T_DIAG, T_RCA], ["RCA-021-CCM-SEG07-spray-nozzle-blockage.md"]),
  u("Does it matter if rolls are fine?"),
  a("Yes - under-cooling the slab risks surface-quality defects and bulging. It won't seize the roll, but it degrades product. Plan a window to clear/replace blocked nozzles.",
    [T_KB], ["MAN-006_continuous_caster_segment.md"]),
  u("Parts?"),
  a("NOZ-SPRAY-01 (consumable spray nozzles) - stock 50, zero lead. Replace blocked nozzles, verify zone flow back to 180-220 L/min, and check upstream water filtration to prevent recurrence. Logging the nozzle-clean task.",
    [T_SPARE, T_WO], ["spine:spare/NOZ-SPRAY-01"]),
])

# 20 roll chatter
convo("CONV-020", "HSM.STD.R1", "SCN-044", [
  u("R1 chock is vibrating hard with a high-frequency whine. Spall?"),
  a("Let me look at the signature. Chock vibration is 9 mm/s (alarm 10) with a 5th-octave chatter band, but force ripple is NOT strongly periodic at 1x roll. That points to roll chatter (RCA-022), not a work-roll spall flat.",
    [T_SENSOR, T_DIAG, T_RCA], ["RCA-022-HSM-STD-R1-roll-chatter.md"]),
  u("How is that different from a spall?"),
  a("A spall prints once per roll revolution (period = pi*D, periodic force ripple). Chatter is regenerative self-excited vibration in a chatter frequency band - it leaves periodic finish marks but isn't a localized roll defect.",
    [T_KB], ["MAN-008_hot_strip_mill_stand.md"]),
  u("Fix?"),
  a("Adjust rolling speed / interstand tension to leave the chatter band, check roll eccentricity and chock seating, and replace worn chock seals (CHOCK-SEAL-01, stock 4, 6-week) if needed. No roll grind required. Want me to log the process-tuning task?",
    [T_SPARE, T_WO], ["spine:spare/CHOCK-SEAL-01"]),
])

# 21 belt misalignment
convo("CONV-021", "RM.CONV.ORE01", "SCN-045", [
  u("Conveyor belt is drifting off to one side. Idler bearing again?"),
  a("No - belt-edge position is 50 mm off-centre (alarm) but motor current is normal and idler ultrasound/temp aren't alarming. That's belt misalignment/mistracking (RCA-023), not a bearing fault.",
    [T_SENSOR, T_DIAG, T_RCA], ["RCA-023-RM-CONV-ORE01-belt-misalignment.md"]),
  u("What causes the drift?"),
  a("Usually uneven loading (off-centre chute), idler frame misalignment, or pulley-lagging wear. Off-track belt risks edge damage, spillage, and structure contact.",
    [T_KB], ["MAN-009_raw_material_conveyor.md"]),
  u("Fix?"),
  a("Install/adjust a self-aligning training idler (IDLER-TRAIN-01, stock 6, 4-week), check load-chute centring and pulley alignment, and confirm belt-edge back within +/-15 mm. Logging the tracking-correction task.",
    [T_SPARE, T_WO], ["spine:spare/IDLER-TRAIN-01"]),
])

# 22 refractory hotspot
convo("CONV-022", "RHF.ZONE.SOAK", "SCN-046", [
  u("IR scan shows a hot spot on the furnace shell. Burner problem?"),
  a("Different from a burner failure. Shell IR temp is 250 degC at the alarm in a localized spot, but zone temp and flame signal are normal. That's refractory thinning/burnout (RCA-024) - lost insulation locally letting heat reach the steel shell.",
    [T_SENSOR, T_DIAG, T_RCA], ["RCA-024-RHF-ZONE-SOAK-refractory-hotspot.md"]),
  u("Is it dangerous?"),
  a("It can be if it grows - risk of shell warping/structural damage and energy loss. It's not an immediate trip, but it must be tracked and repaired at the next opportunity.",
    [T_KB], ["MAN-010_reheating_furnace.md"]),
  u("Plan?"),
  a("Mark and monitor the hot spot, reduce local firing if possible, and plan a gunning/castable repair (REFRAC-CAST-01, stock 10, 2-week) at the next outage. Recheck shell IR after repair. Logging the refractory-repair task for the next window.",
    [T_SPARE, T_WO], ["spine:spare/REFRAC-CAST-01"]),
])

# 23 EAF oil/water contamination
convo("CONV-023", "EAF.AUX.HYD01", "SCN-048", [
  u("EAF HPU cleanliness alarm and the oil looks milky. What's going on?"),
  a("Milky oil means water. ISO 4406 is 19/17/14 (alarm) and water content is 500 ppm (alarm), with filter DP rising. That's oil/water + particulate contamination of the HPU (RCA-018).",
    [T_SENSOR, T_DIAG, T_RCA], ["RCA-018-EAF-AUX-HYD01-oil-water-contamination.md"]),
  u("Where's the water coming from?"),
  a("Most likely a cooler-core leak or seal ingress. Emulsified water degrades film strength, corrodes components, and accelerates valve wear - serious for electrode-regulation precision.",
    [T_KB], ["MAN-011_eaf_bof_auxiliary_hydraulics.md"]),
  u("Fix?"),
  a("Run kidney-loop filtration (KID-LOOP-01, stock 1, 3-week) to strip water + particulate, change the filter element (FLT-HYD-10, on shelf), and find/repair the water-ingress source (check cooler core COOL-CORE-01). Confirm ISO back to <=17/15/12 and water <100 ppm (SOP-13). Logging the decontamination task.",
    [T_SPARE, T_SOP, T_WO], ["spine:spare/KID-LOOP-01", "SOP-13_eaf-hydraulic-system.md"]),
])

# 24 crane brake wear
convo("CONV-024", "MS.LDC.CRN01", "SCN-047", [
  u("Ladle crane brake drum is running hot and the hoist gearbox sounds rough. Rope issue?"),
  a("Two things, neither is the rope. Brake-drum temp is 120 degC (alarm) = brake drag/slip, and hoist-gearbox GMF is 2.5 g (alarm) = gear wear (RCA-025). The rope MFL isn't at discard here.",
    [T_SENSOR, T_DIAG, T_RCA], ["RCA-025-MS-LDC-CRN01-brake-wear.md"]),
  u("Which do I tackle first?"),
  a("Brake first - on a molten-metal crane, brake load-holding is P1 safety. A slipping brake can't hold the ladle. Take the crane out of service until the brake is sorted.",
    [T_KB], ["MAN-012_ladle_crane.md"]),
  u("Parts and steps?"),
  a("Replace brake pads (BRAKE-PAD-01, stock 4, 4-week); inspect/replace the electro-hydraulic thruster (BRAKE-THR-01, stock 1, 8-week) if sticking; run a brake hold test before return (SOP-10). Then plan a hoist-gearbox inspection for the gear wear. I'll raise the out-of-service + brake-service order.",
    [T_SPARE, T_SOP, T_WO], ["spine:spare/BRAKE-PAD-01", "SOP-10_crane-wire-rope-brake.md"]),
])

# 25 normal/false-alarm dialogue
convo("CONV-025", "HSM.F3.WR.BRG01", "SCN-001", [
  u("Quick check - F3 work-roll bearing, vibration 1.6 mm/s, temp 58 degC. All good?"),
  a("All good. Vibration 1.6 mm/s is inside the 0.5-2.3 normal band and temp 58 degC is inside 40-70. No threshold crossed, no degradation trend - healthy steady-state.",
    [T_SENSOR, T_THRESH, T_DIAG], ["spine:SCN-001"]),
  u("So nothing to do?"),
  a("Correct - just continue routine condition monitoring and trend the baseline to CMMS. I'd keep an eye on AE since it's the leading spall indicator on this bearing, but right now there's nothing actionable.",
    [T_KB], ["spine:SCN-001/correct_resolution", "RCA-001-HSM-F3-WR-BRG01-BPFO-spall.md"]),
])

# 26 - cross-asset planning dialogue
convo("CONV-026", "HSM.F1.GBX01", "SCN-038", [
  u("If the F1 gearbox gear wheel ever fails, what's our exposure?"),
  a("Significant. GEAR-WHL-M20 is the custom large-module gear wheel - 0 stock with a 36-week lead time, USD 120k each. A tooth-fatigue failure (SCN-038) runs ~USD 600k (range 500k-3M) with ~168h downtime, mostly because of that gear-wheel lead.",
    [T_SPARE, T_COST], ["spine:spare/GEAR-WHL-M20", "spine:SCN-038/cost_impact"]),
  u("So should we stock one?"),
  a("Given the 36-week lead and the 6000 kW criticality-1 duty, an insurance gear wheel is a strong candidate - the carrying cost (USD 120k) is small against a 3M downside and a 7-day-plus swap. I'd recommend a stocking review.",
    [T_KB], ["spine:HSM.F1.GBX01"]),
  u("What early-warning do we have meanwhile?"),
  a("GMF-band vibration (warn 6, alarm 10 mm/s), oil ferrous ppm (warn 15, alarm 40), and a chip detector. The RTF runs healthy -> cepstrum rahmonics + GMF sidebands -> chip/spall debris -> fracture, so trending GMF + Fe ppm gives weeks of notice. Want me to flag a stocking review and confirm the CM trending is active?",
    [T_DIAG, T_WO], ["spine:SCN-038/degradation_timeline"]),
])

# Generate further variant convos programmatically (early-warning two/three-turn) to reach ~50
early = [
  ("CONV-027", "HSM.F3.WR.BRG01", "SCN-037", "JSR.HR.STD3.WR.BRG01.AE.RMS", "7 dBuV", "AE warning (6) crossed, alarm 12", "outer-race spall", "trend AE + envelope BPFO weekly; plan bearing change at next window", "BRG-LRG-300 (8wk, stock 1)", "RCA-001-HSM-F3-WR-BRG01-BPFO-spall.md"),
  ("CONV-028", "HSM.F1.MTR01", "SCN-039", "JSR.HR.STD1.MTR01.MCSA.RBAR.SB", "-45 dBc", "rotor-bar warning (-45) reached, alarm -35", "broken rotor bar (early)", "confirm via MCSA at steady load; plan swap to insurance spare if it reaches -35 dBc", "MTR-MV-6000 (use on-shelf; new 40wk)", "RCA-003-HSM-F1-MTR01-broken-rotor-bar.md"),
  ("CONV-029", "HSM.DSC.PMP01", "SCN-040", "JSR.HR.DSC.PMP01.VIB.CAS.RMS", "2.6 mm/s", "casing-vib warning (2.5) crossed, alarm 5.0", "mechanical-seal wear (early)", "watch for weeping; switch to standby and change seal before vib reaches 5 mm/s", "SEAL-MECH-DSC (2wk, stock 2)", "RCA-004-HSM-DSC-PMP01-mechanical-seal.md"),
  ("CONV-030", "BF.BLW.FAN01", "SCN-041", "JSR.BF.BLW.FAN01.PRES.OSC", "6%", "surge warning (5) crossed, alarm 8", "incipient surge / ASV cycling", "check inlet filter + downstream valves; verify ASV; trip if it reaches 8%", "ASV-VLV-01 (12wk, 0 stock)", "RCA-005-BF-BLW-FAN01-compressor-surge.md"),
  ("CONV-031", "CCM.SEG.07", "SCN-042", "JSR.CC1.SEG07.FORCE.HYD", "490 kN", "clamp-force warning (480) crossed, alarm 550; roll rpm still >0", "roll-bearing distress (pre-seizure)", "trend rpm + force; plan segment change before rpm hits 0", "BRG-SEG-01 (8wk, stock 4)", "RCA-006-CCM-SEG07-roll-seizure.md"),
  ("CONV-032", "HSM.STD.R1", "SCN-044", "JSR.HR.R1.FORCE", "5%", "force-ripple warning (4) crossed, alarm 8; periodic at 1x roll", "work-roll spall (early)", "inspect strip for periodic marks; quick-change rolls before ripple reaches 8%", "WR-HSS-PREP (0wk, stock 4)", "RCA-008-HSM-STD-R1-work-roll-spall.md"),
  ("CONV-033", "RM.CONV.ORE01", "SCN-045", "JSR.RM.CONV1.IDLER.US", "+9 dBuV", "idler ultrasound warning (+8) crossed, alarm +15", "idler-bearing wear (early)", "IR-scan the idler; schedule swap before temp reaches 80 degC fire-risk", "IDLER-STD-1600 (0wk, stock 40)", "RCA-009-RM-CONV-ORE01-idler-bearing.md"),
  ("CONV-034", "RHF.ZONE.SOAK", "SCN-046", "JSR.RHF.Z3.FLAME.SIG", "68%", "flame warning (70) crossed (lower worse), cutoff 40", "burner instability (early)", "clean burner nozzle + check gas supply before signal drops to 40% cutoff", "BURN-NOZ-01 (4wk, stock 4)", "RCA-010-RHF-ZONE-SOAK-burner-failure.md"),
  ("CONV-035", "CRM.AGC.SV01", "SCN-048", "JSR.CR.S2.AGC.SV.ISO4406", "16/14/11", "servo-oil warning code crossed, alarm 17/15/12", "servo silting (early)", "kidney-loop + filter change to restore ISO 15/13/10 before position error grows", "FLT-SERVO-3 (0wk, stock 4)", "RCA-012-CRM-AGC-SV01-servo-silting.md"),
  ("CONV-036", "MS.LDC.CRN01", "SCN-047", "JSR.MS.CRN01.ROPE.MFL", "160 mV", "rope MFL warning (150) crossed (~8-12% LMA), discard 300", "wire-rope fatigue (early)", "schedule Competent Person inspection; plan rope replacement before MFL reaches 300 mV", "ROPE-CRN-01 (6wk, stock 1)", "RCA-011-MS-LDC-CRN01-wire-rope-fatigue.md"),
  ("CONV-037", "HSM.F1.GBX01", "SCN-038", "JSR.HR.STD1.GBX01.OIL.FE.PPM", "18 ppm", "oil Fe warning (15) crossed, alarm 40", "gear/bearing wear (early)", "increase oil-sample frequency + trend GMF; plan inspection before Fe reaches 40 ppm", "FLT-GBX-01 (0wk, stock 3)", "RCA-002-HSM-F1-GBX01-gear-tooth-fatigue.md"),
  ("CONV-038", "EAF.AUX.HYD01", "SCN-048", "JSR.MS.EAF1.HYD.FILT.DP", "3.2 bar", "filter-DP warning (3.0) crossed, alarm 4.5", "filter clog (early)", "change filter element FLT-HYD-10 before DP reaches 4.5 bar bypass", "FLT-HYD-10 (0wk, stock 6)", "RCA-018-EAF-AUX-HYD01-oil-water-contamination.md"),
]
for cid, aid, scn, tag, val, thresh_note, mode, advice, parts_note, rca in early:
    convo(cid, aid, scn, [
      u(f"Got a warning on {aid} for {tag}. How serious?"),
      a(f"{tag} is reading {val}. That has crossed warning but is not yet at alarm ({thresh_note}). It's an early indicator of {mode} on this asset - actionable but not an emergency.",
        [T_SENSOR, T_THRESH, T_DIAG], [f"spine:{scn}/sensor_signature", rca]),
      u("What should I do now versus later?"),
      a(f"Now: {advice}. The matching spare is {parts_note}. Catching it at the warning stage avoids the unplanned-failure cost - I can log a planned task and set a tighter trend alert. Want me to?",
        [T_KB, T_SPARE, T_WO], [f"spine:{scn}/correct_resolution", f"spine:{scn}"]),
    ])

# A few more 3-turn diagnostic confirmations across remaining assets to reach ~50
more = [
  ("CONV-039", "SP.SINT.FAN01", "SCN-041", "axial 2x ratio 0.5 (warn 0.4, alarm 0.7)", "shaft bow / misalignment", "laser-align the fan-motor train; check for shaft bow; balance if needed", "BAL-WT-01 (0wk, stock 5)", "MAN-005_bf_sinter_fan_blower.md"),
  ("CONV-040", "BF.CW.PMP02", "SCN-041", "head deviation -8% (warn -7, alarm -12)", "impeller wear (early)", "trend head-vs-flow; plan impeller/wear-ring renewal before -12%", "WRING-CW-01 (4wk, stock 2)", "MAN-004_cooling_descaling_pump.md"),
  ("CONV-041", "CCM.MOLD.01", "SCN-043", "mould heat flux 1.05 MW/m2 (warn 1.0, alarm 0.8; lower worse)", "copper-plate wear / heat-flux drop", "inspect mould copper for wear; plan copper change at next window (14wk lead spare)", "MOLD-CU-STD (14wk, stock 1)", "RCA-007-CCM-MOLD01-breakout-sticking.md"),
  ("CONV-042", "HSM.F1.MTR01", "SCN-039", "2x supply-freq vib 1.2 mm/s (warn 1.0, alarm 2.5)", "rotor eccentricity (early)", "check air-gap symmetry + bearing wear; trend 2x-f1 before it reaches 2.5", "BRG-MTR-SET (1wk, stock 1)", "MAN-003_large_induction_motor_vfd.md"),
]
for cid, aid, scn, reading, mode, advice, parts_note, ref in more:
    convo(cid, aid, scn, [
      u(f"What does this {aid} reading mean: {reading}?"),
      a(f"That's an early {mode} indicator - warning crossed, below alarm. Worth acting on at the next opportunity, not an emergency.",
        [T_SENSOR, T_THRESH, T_DIAG], [f"spine:{scn}", ref]),
      u("Recommended action and parts?"),
      a(f"{advice}. Matching spare: {parts_note}. I can log a planned task and tighten the trend alert. Shall I?",
        [T_KB, T_SPARE, T_WO], [ref, f"spine:{scn}"]),
    ])

# Two longer strategic/multi-asset convos to round out variety
convo("CONV-043", "BF.BLW.FAN01", "SCN-041", [
  u("Give me the top safety-critical (P1) risks across the plant and our spare readiness."),
  a("The P1 failures are: BF blower compressor surge (SCN-041), caster breakout (SCN-043), conveyor idler-bearing/belt-fire (SCN-045), and ladle-crane wire-rope failure (SCN-047).",
    [T_KB], ["spine:failure_scenario_catalog"]),
  u("Which of those have weak spare coverage?"),
  a("Surge is the weakest: ASV-VLV-01 is 0 stock / 12-week lead, journal + thrust pads also 12-week. Breakout depends on MOLD-CU-STD (stock 1, 14-week). The idler (stock 40, 0 lead) and crane rope (stock 1, 6-week) are better covered. So surge and breakout carry the most lead-time risk.",
    [T_SPARE, T_COST], ["spine:spare/ASV-VLV-01", "spine:spare/MOLD-CU-STD"]),
  u("Recommendation?"),
  a("Prioritise an anti-surge valve stocking decision (12-week lead vs USD 4-8M downside, BF ~USD 500k/hr) and confirm the breakout 3-sensor logic + an extra mould-copper set. I'd also verify the crane rope MFL and Competent-Person cycle are current. Want me to draft a spares-readiness memo?",
    [T_KB, T_WO], ["spine:SCN-041/cost_impact"]),
])

convo("CONV-044", "HSM.STD.R1", "SCN-044", [
  u("We keep losing product to periodic strip marks at R1. Help me root-cause it."),
  a("Periodic strip marks usually mean one of two things at R1: a work-roll spall (force ripple periodic at 1x roll, period = pi*D) or roll chatter (5th-octave band, not 1x-periodic). Let me check the signatures.",
    [T_SENSOR, T_DIAG], ["spine:SCN-044/sensor_signature"]),
  u("Force ripple is 8.5% and clearly periodic once per roll turn."),
  a("That's a work-roll spall flat (SCN-044 / RCA-008), not chatter - the once-per-revolution periodicity is the tell. Chock vibration confirms (6 mm/s).",
    [T_DIAG, T_RCA], ["RCA-008-HSM-STD-R1-work-roll-spall.md", "RCA-022-HSM-STD-R1-roll-chatter.md"]),
  u("Fix and cost?"),
  a("Quick-change the work rolls (WR-HSS-PREP on shelf, 15-45 min), segregate spall-printed strip, grind the roll 3-5 mm below the spall and UT-test. Doing it planned (~USD 11.2k) vs running to unplanned failure (~USD 184k) is a 16.4x saving (SOP-08). Want the roll-change work order?",
    [T_SOP, T_SPARE, T_COST, T_WO], ["spine:SCN-044/cost_impact", "spine:spare/WR-HSS-PREP", "SOP-08_hot-strip-mill-roll-change.md"]),
])

# Fill remaining to ~50 with concise 3-turn confirmations on remaining sensor angles
fill = [
  ("CONV-045", "HSM.F3.WR.BRG01", "SCN-037", "bearing temp 88 degC (warn 85, alarm 100)", "bearing distress (thermal)", "BRG-LRG-300 (8wk, stock 1)", "RCA-001-HSM-F3-WR-BRG01-BPFO-spall.md"),
  ("CONV-046", "HSM.F1.GBX01", "SCN-038", "lube oil pressure 2.15 bar (warn-low 2.2, alarm-low 2.0)", "forced-lube pressure loss", "FLT-GBX-01 (0wk, stock 3)", "RCA-002-HSM-F1-GBX01-gear-tooth-fatigue.md"),
  ("CONV-047", "HSM.DSC.PMP01", "SCN-040", "discharge flow 360 m3/hr (warn 372, alarm 352)", "performance drop (impeller/seal)", "IMP-DSC-01 (8wk, stock 1)", "RCA-016-HSM-DSC-PMP01-cavitation.md"),
  ("CONV-048", "BF.BLW.FAN01", "SCN-041", "thrust-bearing temp 92 degC (warn 90, alarm 105)", "thrust-bearing thermal distress", "BRG-THRUST-PAD (12wk, stock 1)", "RCA-017-BF-BLW-FAN01-blade-erosion.md"),
  ("CONV-049", "RHF.ZONE.SOAK", "SCN-046", "flue O2 5.2% (warn 5.0, alarm 6.0)", "combustion imbalance / excess air", "BURN-NOZ-01 (4wk, stock 4)", "RCA-010-RHF-ZONE-SOAK-burner-failure.md"),
  ("CONV-050", "CRM.AGC.SV01", "SCN-048", "strip-gauge deviation 12 um (warn 10, alarm 20)", "AGC precision loss (servo silting onset)", "FLT-SERVO-3 (0wk, stock 4)", "RCA-012-CRM-AGC-SV01-servo-silting.md"),
]
for cid, aid, scn, reading, mode, parts_note, ref in fill:
    convo(cid, aid, scn, [
      u(f"{aid}: I'm seeing {reading}. Diagnosis?"),
      a(f"That reading is in the warning band - an early sign of {mode}. Below alarm, so plan rather than panic.",
        [T_SENSOR, T_THRESH, T_DIAG], [f"spine:{scn}", ref]),
      u("What do you recommend?"),
      a(f"Trend it closely and address before it reaches alarm. Matching spare: {parts_note}. I can raise a planned task and a tightened alert - want me to?",
        [T_KB, T_SPARE, T_WO], [ref, f"spine:{scn}/correct_resolution"]),
    ])


# ---------------------------------------------------------------------------
# Write outputs
# ---------------------------------------------------------------------------
def write_jsonl(path, rows):
    with open(path, "w") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    return len(rows)

n_nl = write_jsonl(os.path.join(HERE, "nl_queries.jsonl"), nl)
n_ts = write_jsonl(os.path.join(HERE, "troubleshooting_prompts.jsonl"), ts)
n_mt = write_jsonl(os.path.join(HERE, "multiturn_conversations.jsonl"), mt)

print(f"nl_queries.jsonl: {n_nl}")
print(f"troubleshooting_prompts.jsonl: {n_ts}")
print(f"multiturn_conversations.jsonl: {n_mt}")
