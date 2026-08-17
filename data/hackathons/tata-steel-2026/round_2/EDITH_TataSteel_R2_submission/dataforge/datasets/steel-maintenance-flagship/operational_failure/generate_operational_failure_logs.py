"""
generate_operational_failure_logs.py
=====================================
Generates two synthetic-but-physics-accurate operational log files for the
steel-maintenance-flagship dataset (Tata Steel R2 Hackathon).

Outputs
-------
equipment_delay_logs.csv   ~800 rows
    timestamp, asset_id, line, delay_minutes, delay_reason_code, description

fault_error_messages.csv   ~1000 rows
    timestamp, asset_id, source_system, fault_code, severity, message

Design rules
------------
* Every asset_id and fault_code comes directly from ground_truth_spine.json.
* Failure events are rare (well under 5% of total log row volume).
* Delay rows tied to failure scenarios reference the scenario's correct fault,
  downtime_hours, and root-cause description.
* Fault messages mimic ISA-18.2-2016 alarm-management style:
  PLC messages are terse / single-line; DCS messages include tag + value;
  SCADA messages include trend context.
* Timestamps span 2025-01-01 to 2025-12-31 (one full calendar year).
* Random seed is fixed (42) for reproducibility.
* SYNTHETIC – no proprietary Tata Steel data.
"""

import csv
import random
import math
from datetime import datetime, timedelta

# ---------------------------------------------------------------------------
# Seed
# ---------------------------------------------------------------------------
random.seed(42)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
START_DT = datetime(2025, 1, 1, 0, 0, 0)
END_DT   = datetime(2025, 12, 31, 23, 59, 59)
TOTAL_SECONDS = int((END_DT - START_DT).total_seconds())

OUTPUT_DIR = "/home/ujjwal/Documents/J.A.R.V.I.S./data/hackathons/tata-steel-2026/round_2/dataforge/datasets/steel-maintenance-flagship/operational_failure"

# ---------------------------------------------------------------------------
# Asset master (from spine)
# ---------------------------------------------------------------------------
ASSETS = [
    # (asset_id, equipment_class, area/line, process_stage, criticality)
    ("HSM.F3.WR.BRG01", "rolling_mill_work_roll_bearing", "HOT_ROLLING",        "hot_rolling",          1),
    ("HSM.F1.GBX01",    "mill_gearbox",                   "HOT_ROLLING",        "hot_rolling",          1),
    ("HSM.F1.MTR01",    "large_induction_motor_vfd",       "HOT_ROLLING",        "hot_rolling",          1),
    ("HSM.DSC.PMP01",   "cooling_descaling_pump",          "HOT_ROLLING",        "hot_rolling",          2),
    ("BF.BLW.FAN01",    "bf_sinter_fan_blower",            "BLAST_FURNACE",      "iron_making",          1),
    ("CCM.SEG.07",      "continuous_caster_segment",       "CASTER_1",           "casting",              1),
    ("CCM.MOLD.01",     "continuous_caster_mould",         "CASTER_1",           "casting",              1),
    ("HSM.STD.R1",      "hot_strip_mill_stand",            "HOT_ROLLING",        "hot_rolling",          1),
    ("RM.CONV.ORE01",   "raw_material_conveyor",           "RAW_MATERIAL",       "raw_material_handling",2),
    ("RHF.ZONE.SOAK",   "reheating_furnace",               "REHEAT_FURNACE",     "reheating",            2),
    ("EAF.AUX.HYD01",   "eaf_bof_auxiliary",               "MELT_SHOP",          "steelmaking",          1),
    ("BF.CW.PMP02",     "cooling_descaling_pump",          "BLAST_FURNACE",      "iron_making",          1),
    ("SP.SINT.FAN01",   "bf_sinter_fan_blower",            "SINTER_PLANT",       "sintering",            1),
    ("MS.LDC.CRN01",    "ladle_crane",                     "MELT_SHOP",          "steelmaking",          1),
    ("CRM.AGC.SV01",    "hydraulics_agc_servo",            "COLD_ROLLING",       "cold_rolling",         1),
]

ASSET_IDS = [a[0] for a in ASSETS]
ASSET_LINE = {a[0]: a[2] for a in ASSETS}
ASSET_CRIT = {a[0]: a[4] for a in ASSETS}

# ---------------------------------------------------------------------------
# Failure scenario catalog (from spine SCN-037 to SCN-048)
# Maps: scenario_id -> dict with all needed fields
# ---------------------------------------------------------------------------
FAILURE_SCENARIOS = [
    {
        "scenario_id":  "SCN-037",
        "asset_id":     "HSM.F3.WR.BRG01",
        "failure_mode": "outer_race_fatigue_spall_BPFO",
        "fault_codes":  ["VIB-BPFO-DANGER", "TEMP-TRIP-100C"],
        "downtime_h":   {"planned": 5, "unplanned": 12},
        "delay_reason": "BEARING_SPALL_BPFO",
        "delay_desc":   "Outer-race BPFO spall; envelope alarm + temp trip; bearing replacement (LOTO + hydraulic puller)",
        "safety_class": "P2",
        "source_sys":   "SCADA",
    },
    {
        "scenario_id":  "SCN-038",
        "asset_id":     "HSM.F1.GBX01",
        "failure_mode": "gear_tooth_fatigue_crack",
        "fault_codes":  ["GMF-DANGER", "CHIP-DETECT-ALARM"],
        "downtime_h":   {"planned": 0, "unplanned": 168},
        "delay_reason": "GEAR_TOOTH_CRACK",
        "delay_desc":   "Gear-tooth fatigue crack; GMF sideband alarm + chip detector; gearbox removed to repair bay",
        "safety_class": "P2",
        "source_sys":   "PLC",
    },
    {
        "scenario_id":  "SCN-039",
        "asset_id":     "HSM.F1.MTR01",
        "failure_mode": "broken_rotor_bar",
        "fault_codes":  ["MCSA-RBAR-ALARM"],
        "downtime_h":   {"planned": 10, "unplanned": 0},
        "delay_reason": "ROTOR_BAR_FRACTURE",
        "delay_desc":   "MCSA rotor-bar sideband >-35 dBc; planned motor swap to insurance spare",
        "safety_class": "P3",
        "source_sys":   "DCS",
    },
    {
        "scenario_id":  "SCN-040",
        "asset_id":     "HSM.DSC.PMP01",
        "failure_mode": "mechanical_seal_failure",
        "fault_codes":  ["VIB-SEAL-DANGER"],
        "downtime_h":   {"planned": 3, "unplanned": 8},
        "delay_reason": "MECH_SEAL_FAILURE",
        "delay_desc":   "Mechanical seal blowout; vib >5mm/s; back-pullout seal cartridge change",
        "safety_class": "P3",
        "source_sys":   "SCADA",
    },
    {
        "scenario_id":  "SCN-041",
        "asset_id":     "BF.BLW.FAN01",
        "failure_mode": "compressor_surge",
        "fault_codes":  ["SURGE-ALARM", "ASV-CYCLING"],
        "downtime_h":   {"planned": 0, "unplanned": 96},
        "delay_reason": "COMPRESSOR_SURGE",
        "delay_desc":   "BF turbo-blower surge; discharge pressure oscillation >8%; trip + borescope inspection",
        "safety_class": "P1",
        "source_sys":   "DCS",
    },
    {
        "scenario_id":  "SCN-042",
        "asset_id":     "CCM.SEG.07",
        "failure_mode": "roll_seizure",
        "fault_codes":  ["ROLL-SEIZE", "SEG-FORCE-HIGH"],
        "downtime_h":   {"planned": 0, "unplanned": 8},
        "delay_reason": "ROLL_SEIZURE",
        "delay_desc":   "Strand-guide roll bearing seizure; RPM->0 + clamp force 540 kN; end heat, withdraw segment",
        "safety_class": "P2",
        "source_sys":   "PLC",
    },
    {
        "scenario_id":  "SCN-043",
        "asset_id":     "CCM.MOLD.01",
        "failure_mode": "breakout_sticking",
        "fault_codes":  ["BPS-BREAKOUT-P1", "TC-VPATTERN", "OSC-FRICTION-SPIKE"],
        "downtime_h":   {"planned": 0, "unplanned": 36},
        "delay_reason": "MOLD_BREAKOUT",
        "delay_desc":   "BPS breakout alarm; TC V-pattern delta 55C + oscillator friction 19 kN; emergency stop + floor evacuation",
        "safety_class": "P1",
        "source_sys":   "DCS",
    },
    {
        "scenario_id":  "SCN-044",
        "asset_id":     "HSM.STD.R1",
        "failure_mode": "work_roll_spall_flat",
        "fault_codes":  ["FORCE-RIPPLE-HIGH", "SURFACE-DEFECT-PERIODIC"],
        "downtime_h":   {"planned": 1, "unplanned": 4},
        "delay_reason": "WORK_ROLL_SPALL",
        "delay_desc":   "Work-roll spall; force ripple 8.5% + chock vib 6.0mm/s; quick-change roll + strip segregation",
        "safety_class": "P2",
        "source_sys":   "PLC",
    },
    {
        "scenario_id":  "SCN-045",
        "asset_id":     "RM.CONV.ORE01",
        "failure_mode": "idler_bearing_failure",
        "fault_codes":  ["IDLER-US-ALARM", "IDLER-TEMP-FIRE"],
        "downtime_h":   {"planned": 1, "unplanned": 2},
        "delay_reason": "IDLER_BEARING_SEIZURE",
        "delay_desc":   "Idler bearing seizure; US alarm 16 dBuV + temp 100C (fire risk); belt stop + LOTO + idler swap",
        "safety_class": "P1",
        "source_sys":   "SCADA",
    },
    {
        "scenario_id":  "SCN-046",
        "asset_id":     "RHF.ZONE.SOAK",
        "failure_mode": "burner_failure_fuelside",
        "fault_codes":  ["FLAME-FAIL-CUTOFF", "FLUE-O2-HIGH"],
        "downtime_h":   {"planned": 2, "unplanned": 6},
        "delay_reason": "BURNER_FLAME_FAIL",
        "delay_desc":   "Burner flame-out; flame signal 38% < cutoff threshold; auto fuel cutoff + purge + nozzle replacement",
        "safety_class": "P2",
        "source_sys":   "DCS",
    },
    {
        "scenario_id":  "SCN-047",
        "asset_id":     "MS.LDC.CRN01",
        "failure_mode": "wire_rope_fatigue_broken_wire",
        "fault_codes":  ["ROPE-MFL-RETIRE", "ROPE-DISCARD-ISO4309"],
        "downtime_h":   {"planned": 0, "unplanned": 24},
        "delay_reason": "WIRE_ROPE_DISCARD",
        "delay_desc":   "Wire rope MFL 320 mV > ISO 4309 discard criteria; crane OOS; rope replaced + drum/sheave inspection",
        "safety_class": "P1",
        "source_sys":   "SCADA",
    },
    {
        "scenario_id":  "SCN-048",
        "asset_id":     "CRM.AGC.SV01",
        "failure_mode": "servo_valve_silting_spool_wear",
        "fault_codes":  ["SERVO-HUNT", "GAUGE-EXCURSION", "ISO4406-SERVO-DIRTY"],
        "downtime_h":   {"planned": 2, "unplanned": 6},
        "delay_reason": "SERVO_SILT_HUNT",
        "delay_desc":   "AGC servo valve silt hunt; position error 3.2% + gauge excursion 22 um; swap valve + kidney-loop clean",
        "safety_class": "P2",
        "source_sys":   "PLC",
    },
]

# ---------------------------------------------------------------------------
# Routine (non-failure) delay reason codes and descriptions per asset class
# These are the *normal* operational-inefficiency causes in a steel plant
# ---------------------------------------------------------------------------
ROUTINE_DELAYS = {
    "rolling_mill_work_roll_bearing": [
        ("SCH-LUBE-CHANGE",   "Scheduled oil-film bearing lube change; brief stop for sample + top-up"),
        ("SCH-VIB-SURVEY",    "Scheduled vibration survey (route-based); 5-min isolation for burst acquisition"),
        ("PROD-COBBLE-MINOR", "Minor cobble recovery; finishing stand F3 stopped for strip threading"),
        ("ROLL-CHANGE-SCHED", "Scheduled work-roll change; chock + roll swap, laser-align"),
        ("INSP-CHOCK-VISUAL", "Visual chock inspection; brief stop for clearance check"),
    ],
    "mill_gearbox": [
        ("SCH-OIL-SAMPLE",    "Monthly oil sample draw from F1 gearbox sump; production hold ~10 min"),
        ("SCH-FILTER-CHANGE", "Gearbox oil filter element change (scheduled PM)"),
        ("SCH-VISC-CHECK",    "Kinematic viscosity field check; top-up with fresh ISO VG220"),
        ("PROD-VIBRATION-HI", "GMF vibration elevated advisory; stand slowed for trend check"),
        ("SCH-COUPLING-INSP", "Coupling element inspection; brief outage for cover removal"),
    ],
    "large_induction_motor_vfd": [
        ("SCH-MCSA-SURVEY",   "Scheduled MCSA measurement; steady-load run for sideband acquisition"),
        ("SCH-WIND-TEMP-CHK", "Winding temperature probe calibration check"),
        ("SCH-BEARING-REGREASE", "Motor bearing re-grease; brief stop for relief-plug purge"),
        ("VFD-PARAM-UPDATE",  "VFD parameter update by E&I team; motor stopped for safe access"),
        ("SCH-PI-OFFLINE",    "Offline PI (polarisation index) test; motor de-energised"),
    ],
    "cooling_descaling_pump": [
        ("SCH-SEAL-FLUSH",    "Scheduled mechanical seal flush water inspection"),
        ("SCH-IMPELLER-INSP", "Planned impeller clearance check via back-pullout"),
        ("PUMP-SWAP-ROUTINE", "Routine pump-standby changeover; both pumps cycled for equal wear"),
        ("SCH-BRG-TEMP-CAL",  "Bearing temperature probe calibration; pump isolated"),
        ("PROD-DESCALE-PRES-ADJ", "Descale pressure adjustment for new steel grade; brief flow trim"),
    ],
    "bf_sinter_fan_blower": [
        ("SCH-VIBRATION-SURVEY", "Route vibration survey on blower/fan; burst acquisition at running speed"),
        ("SCH-LUBE-TOPUP",    "Lube oil top-up + filter change on blower/fan"),
        ("SCH-INLET-FILTER",  "Inlet filter element inspection + cleaning"),
        ("SCH-ASV-TEST",      "Anti-surge valve partial-stroke test (functional check)"),
        ("SCH-IGV-POSITION",  "Inlet guide vane position calibration"),
    ],
    "continuous_caster_segment": [
        ("SCH-SPRAY-FLUSH",   "Scheduled spray nozzle flush + blockage check; reduced casting speed"),
        ("SCH-SEGMENT-SWAP",  "Planned segment withdrawal for roll inspection + re-gap"),
        ("PROD-CASTING-SCHED","Ladle turret turn-around; caster stopped between heats"),
        ("SCH-ROLL-LUBRICATION", "Roll-bearing lubrication check; brief stop for nipple access"),
        ("PROD-TUNDISH-CHANGE","Tundish change; caster stop + re-start sequence"),
    ],
    "continuous_caster_mould": [
        ("SCH-OSC-LUBE",      "Mould oscillation bearing lubrication; stop for access"),
        ("SCH-TC-CALIBRATION","Thermocouple array calibration verification; stop + ice-point check"),
        ("PROD-GRADE-CHANGE", "Steel grade change; mould powder and taper adjust; brief stop"),
        ("SCH-MOLD-COPPER-INSP","Scheduled copper plate thickness measurement; brief cooldown"),
        ("SCH-BPS-TEST",      "Breakout prevention system (BPS) functional test; test-signal injection"),
    ],
    "hot_strip_mill_stand": [
        ("SCH-ROLL-CHANGE",   "Scheduled work-roll change, R1; prepared rolls from roll shop"),
        ("PROD-COBBLE-MAJOR", "Major cobble at R1; rolled section jammed; clear + threading sequence"),
        ("SCH-AGC-CALIB",     "Screwdown AGC load-cell calibration; production hold"),
        ("SCH-CHOCK-SEAL-CHK","Chock seal inspection; brief isolation for cover check"),
        ("PROD-THICKNESS-ADJ","Thickness (gauge) adjustment for new order; operator intervention"),
    ],
    "raw_material_conveyor": [
        ("SCH-IDLER-PATROL",  "Scheduled idler patrol route; IR + ultrasound walk-down; brief belt slow-down"),
        ("SCH-BELT-INSPECT",  "Belt surface + splice inspection; belt stopped for visual access"),
        ("BELT-TRACK-ADJUST", "Belt mis-tracking correction; training idler adjusted"),
        ("SCH-TENSIONER-CHK", "Belt tensioner pressure check + take-up adjustment"),
        ("PROD-ORE-BLOCKAGE", "Ore blockage at transfer chute; belt stopped for clearing"),
    ],
    "reheating_furnace": [
        ("SCH-FLAME-SCAN-CHK","Flame scanner cleaning + response test; burner isolated"),
        ("SCH-O2-PROBE-CAL",  "Flue O2 probe calibration; 30-min purge + reference gas check"),
        ("SCH-REFRACTORY-INSP","IR shell scan refractory inspection (online)"),
        ("SCH-BURNER-TUNE",   "Burner fuel-air ratio trim for new coal GCV; brief hold"),
        ("PROD-SLAB-DISCHARGE","Slab discharge delay due to downstream HSM schedule change"),
    ],
    "eaf_bof_auxiliary": [
        ("SCH-OIL-CLEANLINESS","Hydraulic oil cleanliness ISO 4406 lab sample; production hold"),
        ("SCH-FILTER-REPLACE", "HPU filter element replacement (scheduled PM)"),
        ("SCH-COOLER-CLEAN",   "Hydraulic oil cooler tube-side cleaning; HPU isolated"),
        ("SCH-WATER-PURITY",   "Water content (Karl-Fischer) test on hydraulic oil"),
        ("PROD-ELECTRODE-ADJ", "EAF electrode position hold; HPU in slow-mode for regulation"),
    ],
    "cooling_descaling_pump_bf": [  # BF.CW.PMP02 variant
        ("SCH-PUMP-ROTATION",  "BF cooling pump standby rotation (equal-wear policy)"),
        ("SCH-SEAL-INSPECT",   "Mechanical seal inspection; pump isolated"),
        ("SCH-IMPELLER-CLEARANCE","Impeller clearance + wear-ring check"),
        ("SCH-BRG-VIBRATION",  "Bearing vibration survey; burst acquisition"),
        ("PROD-BF-SCHEDULE",   "BF tap schedule change; cooling load adjusted + pump trim"),
    ],
    "ladle_crane": [
        ("SCH-ROPE-MFL-INSP",  "Scheduled MFL rope inspection; crane OOS for rope feed through sensor"),
        ("SCH-BRAKE-HOLD-TEST","Brake holding capacity test (200% rated load, static)"),
        ("SCH-GBX-OIL-CHANGE", "Hoist gearbox oil change + filter; crane ground-level hold"),
        ("SCH-LIMIT-SWITCH-CHK","Upper/lower limit switch verification; hoist jogged to check"),
        ("PROD-LADLE-EXCHANGE", "Ladle preparation delay; crane idle wait between heats"),
    ],
    "hydraulics_agc_servo": [
        ("SCH-ISO4406-SAMPLE", "Servo circuit oil cleanliness sample (inline + lab); brief hold"),
        ("SCH-FILTER-3UM",     "3 µm servo filter element replacement (scheduled PM)"),
        ("SCH-POSERR-CHECK",   "Position error step-response test after maintenance"),
        ("SCH-VALVE-FLUSH",    "Servo valve null-leakage check; pressure isolated"),
        ("PROD-GAUGE-TRIM",    "Strip gauge trim for new coil order; AGC setpoint change"),
    ],
}

# Map asset_id -> routine delay pool
ASSET_DELAY_POOL = {
    "HSM.F3.WR.BRG01": ROUTINE_DELAYS["rolling_mill_work_roll_bearing"],
    "HSM.F1.GBX01":    ROUTINE_DELAYS["mill_gearbox"],
    "HSM.F1.MTR01":    ROUTINE_DELAYS["large_induction_motor_vfd"],
    "HSM.DSC.PMP01":   ROUTINE_DELAYS["cooling_descaling_pump"],
    "BF.BLW.FAN01":    ROUTINE_DELAYS["bf_sinter_fan_blower"],
    "CCM.SEG.07":      ROUTINE_DELAYS["continuous_caster_segment"],
    "CCM.MOLD.01":     ROUTINE_DELAYS["continuous_caster_mould"],
    "HSM.STD.R1":      ROUTINE_DELAYS["hot_strip_mill_stand"],
    "RM.CONV.ORE01":   ROUTINE_DELAYS["raw_material_conveyor"],
    "RHF.ZONE.SOAK":   ROUTINE_DELAYS["reheating_furnace"],
    "EAF.AUX.HYD01":   ROUTINE_DELAYS["eaf_bof_auxiliary"],
    "BF.CW.PMP02":     ROUTINE_DELAYS["cooling_descaling_pump_bf"],
    "SP.SINT.FAN01":   ROUTINE_DELAYS["bf_sinter_fan_blower"],
    "MS.LDC.CRN01":    ROUTINE_DELAYS["ladle_crane"],
    "CRM.AGC.SV01":    ROUTINE_DELAYS["hydraulics_agc_servo"],
}

# ---------------------------------------------------------------------------
# Normal PLC/DCS/SCADA fault messages (informational / transient)
# Used to pad the fault log with realistic background noise
# ---------------------------------------------------------------------------
def _r(lo, hi, decimals=2):
    """Return a lambda that samples uniform [lo,hi] rounded to `decimals`."""
    return lambda: round(random.uniform(lo, hi), decimals)

# Each template entry:  (source_system, severity, fault_code, message_template, [value_generators...])
# Value generators are callables returning a numeric value with correct physical range.
NORMAL_FAULT_TEMPLATES = {
    "HSM.F3.WR.BRG01": [
        ("PLC",   "INFO",    "MTR-STRT-OK",      "Motor start sequence complete; run-permissive set",            []),
        ("SCADA", "INFO",    "BASELINE-UPDATE",   "Tag JSR.HR.STD3.WR.BRG01.VIB.DE.H.RMS baseline updated to {:.2f} mm/s",
                                                                                                                   [_r(0.5, 2.3)]),
        ("DCS",   "WARNING", "VIB-WARN-TREND",    "Vibration trending +{:.1f}% over 24h; advisory only",          [_r(3.0, 8.0, 1)]),
        ("SCADA", "INFO",    "LUBE-FLOW-OK",      "Oil-film bearing lube flow nominal {:.1f} L/min",              [_r(8.0, 14.0, 1)]),
        ("PLC",   "INFO",    "TEMP-NORMAL",       "BRG01.TEMP.DE normal: {:.1f} degC",                           [_r(40.0, 70.0, 1)]),
    ],
    "HSM.F1.GBX01": [
        ("PLC",   "INFO",    "OIL-TEMP-OK",       "Sump temp JSR.HR.STD1.GBX01.OIL.TEMP: {:.1f} degC (normal)",  [_r(45.0, 65.0, 1)]),
        ("SCADA", "WARNING", "OIL-FE-TREND",      "Ferritic particle count rising; schedule oil sample. Fe={:.0f} ppm",
                                                                                                                   [_r(5.0, 14.0, 0)]),
        ("DCS",   "INFO",    "GMF-BAND-NORMAL",   "GMF band RMS: {:.2f} mm/s within baseline",                   [_r(0.5, 4.0)]),
        ("PLC",   "INFO",    "OIL-PRES-OK",       "Lube pressure JSR.HR.STD1.GBX01.OIL.PRES: {:.2f} bar",        [_r(2.5, 4.0)]),
        ("DCS",   "WARNING", "VISC-LOW-WARN",     "Viscosity approaching lower limit: {:.0f} cSt; schedule oil change",
                                                                                                                   [_r(180.0, 198.0, 0)]),
    ],
    "HSM.F1.MTR01": [
        ("DCS",   "INFO",    "WIND-TEMP-OK",      "Stator winding temp: {:.0f} degC (Class F headroom OK)",       [_r(80.0, 130.0, 0)]),
        ("PLC",   "INFO",    "CURR-IMBAL-OK",     "Phase current imbalance: {:.2f}% (< 1% normal)",               [_r(0.1, 0.9)]),
        ("SCADA", "INFO",    "VIB-DE-NORMAL",     "Motor body vib DE: {:.2f} mm/s",                               [_r(0.5, 2.3)]),
        ("DCS",   "WARNING", "WIND-TEMP-RISING",  "Winding temp trending up {:.1f} degC over 4h; advisory",       [_r(2.0, 8.0, 1)]),
        ("PLC",   "INFO",    "VFD-RUN-OK",        "VFD ACS6000 running normally; DC-link voltage stable",         []),
    ],
    "HSM.DSC.PMP01": [
        ("PLC",   "INFO",    "PRES-DIS-OK",       "Discharge pressure JSR.HR.DSC.PMP01.PRES.DIS: {:.0f} bar (normal)",
                                                                                                                   [_r(190.0, 210.0, 0)]),
        ("DCS",   "INFO",    "FLOW-OK",           "Discharge flow: {:.0f} m3/hr (design point)",                  [_r(388.0, 412.0, 0)]),
        ("SCADA", "WARNING", "VIB-CAS-TREND",     "Casing vib trending; current {:.2f} mm/s; monitor",            [_r(1.5, 2.4)]),
        ("PLC",   "INFO",    "SEAL-FLUSH-OK",     "Seal flush water flow normal",                                  []),
        ("DCS",   "INFO",    "BRG-TEMP-OK",       "Bearing temp: {:.0f} degC (normal range 40-70)",               [_r(40.0, 70.0, 0)]),
    ],
    "BF.BLW.FAN01": [
        ("DCS",   "INFO",    "SHAFT-DISP-OK",     "Shaft displacement: {:.0f} um pp (API 670 Zone A)",            [_r(10.0, 50.0, 0)]),
        ("SCADA", "INFO",    "VIB-1X-OK",         "Blower 1x vibration: {:.2f} mm/s (nominal)",                  [_r(1.0, 2.3)]),
        ("PLC",   "INFO",    "PRES-OSC-LOW",      "Discharge pressure oscillation: {:.1f}% (< 2% normal)",        [_r(0.1, 1.9, 1)]),
        ("DCS",   "WARNING", "THRUST-TEMP-TREND", "Thrust bearing temp trending: {:.0f} degC; advisory",          [_r(75.0, 89.0, 0)]),
        ("SCADA", "INFO",    "SURGE-MARGIN-OK",   "Anti-surge margin adequate; ASV closed",                       []),
    ],
    "CCM.SEG.07": [
        ("PLC",   "INFO",    "ROLL-RPM-OK",       "Segment 07 roll rotation: {:.0f} rpm (normal)",                [_r(3.0, 25.0, 0)]),
        ("DCS",   "INFO",    "FORCE-HYD-OK",      "Clamping force: {:.0f} kN (within 200-400 kN range)",         [_r(200.0, 400.0, 0)]),
        ("SCADA", "INFO",    "SPRAY-FLOW-OK",     "Zone spray flow: {:.0f} L/min (normal)",                       [_r(180.0, 220.0, 0)]),
        ("PLC",   "WARNING", "BULGE-RISING",      "Strand bulge deviation: {:.1f} mm; monitor casting speed",     [_r(1.1, 1.9, 1)]),
        ("DCS",   "INFO",    "ROLL-VIB-OK",       "Roll bearing vib: {:.2f} mm/s (normal)",                      [_r(0.5, 2.0)]),
    ],
    "CCM.MOLD.01": [
        ("DCS",   "INFO",    "TC-DELTA-OK",       "Adjacent TC delta: {:.0f} degC (normal < 20)",                 [_r(0.0, 20.0, 0)]),
        ("SCADA", "INFO",    "LEVEL-STABLE",      "Mould level deviation: {:.1f} mm (stable)",                    [_r(-2.0, 2.0, 1)]),
        ("PLC",   "INFO",    "HEATFLUX-OK",       "Mean mould heat flux: {:.2f} MW/m2 (normal)",                  [_r(1.2, 2.0)]),
        ("DCS",   "WARNING", "OSC-FRICTION-ADV",  "Oscillation friction: {:.1f} kN; powder addition recommended", [_r(8.0, 9.9, 1)]),
        ("SCADA", "INFO",    "BPS-ARMED",         "BPS breakout prevention system armed; no alarms",              []),
    ],
    "HSM.STD.R1": [
        ("PLC",   "INFO",    "FORCE-RIPPLE-OK",   "Rolling force ripple: {:.1f}% (< 2% normal)",                  [_r(0.2, 2.0, 1)]),
        ("DCS",   "INFO",    "CROWN-DEV-OK",      "Strip crown deviation: {:.0f} um (normal ±10 um)",             [_r(-10.0, 10.0, 0)]),
        ("SCADA", "WARNING", "AE-TREND-R1",       "Roll journal AE trending +{:.0f} dB; schedule visual check",   [_r(2.0, 7.0, 0)]),
        ("PLC",   "INFO",    "CHOCK-VIB-OK",      "Chock vibration: {:.2f} mm/s (normal < 1.0)",                  [_r(0.1, 0.9)]),
        ("DCS",   "INFO",    "AGC-FORCE-OK",      "AGC roll-force load cell balanced; screwdown nominal",         []),
    ],
    "RM.CONV.ORE01": [
        ("PLC",   "INFO",    "MTR-CURR-OK",       "Drive motor current: {:.0f}%FLA (normal 60-95%)",              [_r(60.0, 95.0, 0)]),
        ("SCADA", "INFO",    "BELT-TRACK-OK",     "Belt edge position: {:+.0f} mm (centred)",                     [_r(-15.0, 15.0, 0)]),
        ("DCS",   "WARNING", "IDLER-US-RISING",   "Idler ultrasound advisory: {:.0f} dBuV above baseline",        [_r(0.0, 7.0, 0)]),
        ("PLC",   "INFO",    "RIP-LOOP-OK",       "Rip detector loop current: {:.0f} mA (intact)",                [_r(60.0, 80.0, 0)]),
        ("SCADA", "INFO",    "IDLER-TEMP-NORMAL", "Idler IR temp: {:.0f} degC (normal < 60)",                     [_r(25.0, 60.0, 0)]),
    ],
    "RHF.ZONE.SOAK": [
        ("DCS",   "INFO",    "ZONE-TEMP-OK",      "Soak zone temp: {:.0f} degC (SP nominal 1240)",                [_r(1180.0, 1280.0, 0)]),
        ("SCADA", "INFO",    "FLAME-OK",          "Flame scanner signal: {:.0f}% (> 90% good)",                   [_r(90.0, 100.0, 0)]),
        ("PLC",   "INFO",    "FLUE-O2-OK",        "Flue O2: {:.1f}% (normal 1.5-3.5%)",                          [_r(1.5, 3.5, 1)]),
        ("DCS",   "WARNING", "SHELL-TEMP-ADV",    "Shell IR temp advisory: {:.0f} degC; refractory inspection due",
                                                                                                                   [_r(120.0, 179.0, 0)]),
        ("SCADA", "INFO",    "COMBUSTION-TRIM",   "Auto combustion trim active; fuel-air ratio balanced",         []),
    ],
    "EAF.AUX.HYD01": [
        ("DCS",   "INFO",    "OIL-TEMP-OK",       "HPU oil temp: {:.0f} degC (normal 40-50)",                     [_r(40.0, 50.0, 0)]),
        ("PLC",   "INFO",    "FILT-DP-OK",        "Filter DP: {:.1f} bar (< 1.5 bar normal)",                     [_r(0.1, 1.5, 1)]),
        ("SCADA", "WARNING", "ISO4406-ADV",       "ISO 4406 cleanliness advisory: borderline 17/15/12 detected",  []),
        ("DCS",   "INFO",    "WATER-PPM-OK",      "Water content: {:.0f} ppm (< 100 normal)",                     [_r(5.0, 99.0, 0)]),
        ("PLC",   "INFO",    "HYD-PRESSURE-OK",   "System pressure nominal at 350 bar",                           []),
    ],
    "BF.CW.PMP02": [
        ("PLC",   "INFO",    "VIB-1X-OK",         "BF CW pump 1x vib: {:.2f} mm/s (normal 0.5-1.8)",             [_r(0.5, 1.8)]),
        ("DCS",   "INFO",    "HEAD-DEV-OK",        "Differential head deviation: {:.1f}% (normal ±3%)",           [_r(-3.0, 3.0, 1)]),
        ("SCADA", "INFO",    "BRG-TEMP-OK",       "BF pump bearing temp: {:.0f} degC (normal 40-70)",             [_r(40.0, 70.0, 0)]),
        ("PLC",   "WARNING", "VIB-BB-TREND",      "Broadband vib trending up: {:.2f} mm/s; advisory",             [_r(1.6, 2.4)]),
        ("DCS",   "INFO",    "SEAL-FLUSH-OK",     "Mechanical seal flush water flowing normally",                  []),
    ],
    "SP.SINT.FAN01": [
        ("DCS",   "INFO",    "VIB-1X-OK",         "Sinter fan 1x vib: {:.2f} mm/s (nominal)",                    [_r(1.0, 2.3)]),
        ("SCADA", "INFO",    "BRG-TEMP-OK",       "Fan bearing temp: {:.0f} degC (normal 45-65)",                 [_r(45.0, 65.0, 0)]),
        ("PLC",   "INFO",    "DP-DUCT-OK",        "Inlet-outlet DP: {:.0f} kPa (normal 8-14 kPa)",               [_r(8.0, 14.0, 0)]),
        ("DCS",   "WARNING", "AXIAL-RATIO-ADV",   "Axial/2x ratio {:.2f}; approaching advisory limit 0.4",        [_r(0.31, 0.39)]),
        ("SCADA", "INFO",    "DUST-PURGE-OK",     "Inlet filter dust purge complete; DP returned to normal",      []),
    ],
    "MS.LDC.CRN01": [
        ("SCADA", "INFO",    "ROPE-MFL-OK",       "Wire rope MFL: {:.0f} mV (< 150 mV advisory)",                 [_r(30.0, 149.0, 0)]),
        ("DCS",   "INFO",    "LOAD-SWL-OK",       "Hoist load: {:.0f}%SWL (normal < 95%)",                        [_r(20.0, 94.0, 0)]),
        ("PLC",   "INFO",    "BRAKE-TEMP-OK",     "Brake drum temp: {:.0f} degC (normal 25-90)",                  [_r(25.0, 90.0, 0)]),
        ("SCADA", "WARNING", "GBX-GMF-TREND",     "Hoist gearbox GMF trending: {:.2f} g; advisory",               [_r(0.5, 0.99)]),
        ("DCS",   "INFO",    "LIMIT-SW-OK",       "Upper/lower limit switches verified; healthy",                  []),
    ],
    "CRM.AGC.SV01": [
        ("PLC",   "INFO",    "POSERR-OK",         "AGC servo position error: {:.2f}% (< 0.5% normal)",            [_r(0.05, 0.49)]),
        ("DCS",   "INFO",    "GAUGE-DEV-OK",      "Strip gauge deviation: {:.0f} um (normal ±5 um)",              [_r(-5.0, 5.0, 0)]),
        ("SCADA", "WARNING", "ISO4406-ADV-SERVO", "Servo oil cleanliness advisory: 16/14/11; schedule filter change", []),
        ("PLC",   "INFO",    "NULL-LEAK-OK",      "Null leakage: {:.2f} L/min (< 0.5 normal)",                    [_r(0.01, 0.49)]),
        ("DCS",   "INFO",    "AGC-RESPONSE-OK",   "Step-response bandwidth nominal; AGC tracking well",           []),
    ],
}

# ---------------------------------------------------------------------------
# Failure fault message templates (ISA-18.2 CRITICAL / HIGH)
# One template per fault_code from the failure scenarios
# ---------------------------------------------------------------------------
FAILURE_FAULT_TEMPLATES = {
    "VIB-BPFO-DANGER": (
        "SCADA", "CRITICAL",
        "BEARING ALARM: Tag JSR.HR.STD3.WR.BRG01.VIB.DE.ENV.BPFO = {:.2f} g >> ALARM 3.0 g. "
        "BPFO outer-race spall pattern confirmed. Temp DE = {:.0f} degC. Initiate controlled stop per Playbook 01."
    ),
    "TEMP-TRIP-100C": (
        "PLC", "CRITICAL",
        "TRIP: JSR.HR.STD3.WR.BRG01.TEMP.DE >= 100 degC (value={:.0f}). "
        "Bearing outer-ring over-temperature. Zone-D stop initiated. Do NOT emergency-trip."
    ),
    "GMF-DANGER": (
        "PLC", "CRITICAL",
        "ALARM: JSR.HR.STD1.GBX01.VIB.GMF.RMS = {:.1f} mm/s >> ALARM 10.0. "
        "Gear-mesh frequency band DANGER. Fe particles = {:.0f} ppm. Immediate controlled stop."
    ),
    "CHIP-DETECT-ALARM": (
        "DCS", "HIGH",
        "CHIP DETECTOR ACTIVE: HSM.F1.GBX01 magnetic plug positive for ferrous fragments. "
        "Particle count >= {:.0f} ppm. Gearbox shutdown required. Do not defer."
    ),
    "MCSA-RBAR-ALARM": (
        "DCS", "HIGH",
        "MCSA ALARM: JSR.HR.STD1.MTR01.MCSA.RBAR.SB = {:.0f} dBc (>> ALARM -35 dBc). "
        "Rotor-bar sideband at (1-2s)f1. Confirm at steady load. Plan motor swap in 2-4 weeks."
    ),
    "VIB-SEAL-DANGER": (
        "SCADA", "CRITICAL",
        "SEAL ALARM: JSR.HR.DSC.PMP01.VIB.CAS.RMS = {:.2f} mm/s >> ALARM 5.0. "
        "BRG temp = {:.0f} degC. Mechanical seal blowout risk. Switch to standby pump + LOTO."
    ),
    "SURGE-ALARM": (
        "DCS", "CRITICAL",
        "SURGE EVENT: JSR.BF.BLW.FAN01.PRES.OSC = {:.1f}% >> ALARM 8%. "
        "Shaft displacement = {:.0f} um. ASV auto-open initiated. If >2-3 cycles: TRIP IMMEDIATELY."
    ),
    "ASV-CYCLING": (
        "PLC", "HIGH",
        "ASV CYCLING: BF.BLW.FAN01 anti-surge valve cycling detected ({} actuations in 10 min). "
        "Surge margin < 8%. Reduce load or isolate downstream valve."
    ),
    "ROLL-SEIZE": (
        "PLC", "CRITICAL",
        "ROLL SEIZURE: JSR.CC1.SEG07.ROLL.RPM = 0 (encoder pulse loss). "
        "SEG07 roll no rotation. Reduce casting speed. Prepare to end heat."
    ),
    "SEG-FORCE-HIGH": (
        "DCS", "HIGH",
        "FORCE HIGH: JSR.CC1.SEG07.FORCE.HYD = {:.0f} kN >> ALARM 550 kN. "
        "Segment clamping pressure abnormal. Roll seizure confirmed. Segment withdrawal required."
    ),
    "BPS-BREAKOUT-P1": (
        "DCS", "CRITICAL",
        "*** BPS BREAKOUT P1 ALARM *** JSR.CC1.MOLD.TC.DELTA = {:.0f} degC >> ALARM 50. "
        "V-pattern confirmed. Reduce casting speed to 0.5 m/min IMMEDIATELY. Prepare emergency stop."
    ),
    "TC-VPATTERN": (
        "SCADA", "CRITICAL",
        "TC V-PATTERN DETECTED: Adjacent TC delta = {:.0f} degC. Cold spot propagating downward. "
        "Shell sticking to mould wall. BPS algorithm active."
    ),
    "OSC-FRICTION-SPIKE": (
        "DCS", "HIGH",
        "OSCILLATOR FRICTION SPIKE: JSR.CC1.MOLD.OSC.FRICTION = {:.1f} kN >> ALARM 18 kN. "
        "Poor lubrication or shell sticking. Increase mould powder addition."
    ),
    "FORCE-RIPPLE-HIGH": (
        "PLC", "HIGH",
        "FORCE RIPPLE ALARM: JSR.HR.R1.FORCE = {:.1f}% >> ALARM 8%. "
        "Periodic at 1x roll frequency = spall printing. Stop rolling; segregate last coil."
    ),
    "SURFACE-DEFECT-PERIODIC": (
        "SCADA", "HIGH",
        "PERIODIC SURFACE DEFECT detected on R1 product (period = pi*D). "
        "Chock vib = {:.1f} mm/s. Work-roll spall confirmed. Quick-change rolls. Strip q-hold."
    ),
    "IDLER-US-ALARM": (
        "SCADA", "HIGH",
        "IDLER ULTRASOUND ALARM: JSR.RM.CONV1.IDLER.US = {:.0f} dBuV >> ALARM 15. "
        "Idler bearing seizure risk. Belt fire hazard. Stop belt + LOTO immediately."
    ),
    "IDLER-TEMP-FIRE": (
        "PLC", "CRITICAL",
        "IDLER TEMPERATURE FIRE RISK: JSR.RM.CONV1.IDLER.TEMP = {:.0f} degC >> ALARM 100. "
        "Seized idler under loaded belt. EMERGENCY STOP. Evacuate area."
    ),
    "FLAME-FAIL-CUTOFF": (
        "DCS", "CRITICAL",
        "FLAME FAIL + FUEL CUTOFF: JSR.RHF.Z3.FLAME.SIG = {:.0f}% << ALARM 40%. "
        "Fuel automatically isolated (EN 746-2). PURGE FURNACE before re-light attempt."
    ),
    "FLUE-O2-HIGH": (
        "SCADA", "HIGH",
        "FLUE O2 HIGH: JSR.RHF.Z3.FLUE.O2 = {:.1f}% >> alarm 6.0%. "
        "Excess air; possible burner flame-out. Combustion efficiency compromised."
    ),
    "ROPE-MFL-RETIRE": (
        "SCADA", "CRITICAL",
        "WIRE ROPE RETIREMENT THRESHOLD: JSR.MS.CRN01.ROPE.MFL = {:.0f} mV >> ALARM 300 mV. "
        "LMA exceeds ISO 4309 discard criteria. CRANE OUT OF SERVICE. Do not lift."
    ),
    "ROPE-DISCARD-ISO4309": (
        "DCS", "CRITICAL",
        "ISO 4309 DISCARD: MS.LDC.CRN01 MFL signal {:.0f} mV indicates >15% LMA or >= 12 broken wires per lay. "
        "Competent Person inspection required. Replace rope before any lift."
    ),
    "SERVO-HUNT": (
        "PLC", "HIGH",
        "AGC SERVO HUNT: JSR.CR.S2.AGC.SV.POSERR = {:.1f}% >> ALARM 3.0%. "
        "Spool silt/wear causing position instability. Switch AGC to backup/manual lock."
    ),
    "GAUGE-EXCURSION": (
        "SCADA", "HIGH",
        "STRIP GAUGE EXCURSION: JSR.CR.S2.AGC.GAUGE.DEV = {:.0f} um >> ALARM 20 um. "
        "AGC unable to hold gauge. Servo valve silting confirmed. CRM coil on quality hold."
    ),
    "ISO4406-SERVO-DIRTY": (
        "DCS", "HIGH",
        "ISO 4406 SERVO DIRTY: JSR.CR.S2.AGC.SV.ISO4406 = 17/15/12 >> alarm 17/15/12. "
        "Servo oil contamination confirmed. Replace 3um+10um filters; kidney-loop to 15/13/10."
    ),
}

# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------
def rand_dt(start=START_DT, end=END_DT):
    """Random datetime uniformly in [start, end]."""
    delta = int((end - start).total_seconds())
    return start + timedelta(seconds=random.randint(0, delta))


def fmt_dt(dt):
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def jitter(base, pct=0.05):
    """Add ±pct noise to a float value."""
    return round(base * (1.0 + random.uniform(-pct, pct)), 3)


# ---------------------------------------------------------------------------
# 1. Generate equipment_delay_logs.csv
# ---------------------------------------------------------------------------
def generate_delay_logs(target=800):
    rows = []

    # --- Failure-linked delay rows (rare) ---
    # Each failure scenario fires 2-4 times over the year (repeat episodes)
    failure_delay_rows = []
    for scn in FAILURE_SCENARIOS:
        n_episodes = random.randint(2, 4)
        used_offsets = set()
        for _ in range(n_episodes):
            while True:
                dt = rand_dt()
                day_key = dt.toordinal()
                if day_key not in used_offsets:
                    used_offsets.add(day_key)
                    break
            is_unplanned = scn["downtime_h"]["unplanned"] > 0
            base_mins = (scn["downtime_h"]["unplanned"] if is_unplanned
                         else scn["downtime_h"]["planned"]) * 60
            delay_mins = max(10, int(base_mins * random.uniform(0.7, 1.3)))
            failure_delay_rows.append({
                "timestamp":        fmt_dt(dt),
                "asset_id":         scn["asset_id"],
                "line":             ASSET_LINE[scn["asset_id"]],
                "delay_minutes":    delay_mins,
                "delay_reason_code":scn["delay_reason"],
                "description":      scn["delay_desc"],
            })

    # --- Routine delay rows (bulk) ---
    n_routine = target - len(failure_delay_rows)
    routine_rows = []
    for _ in range(n_routine):
        asset = random.choice(ASSET_IDS)
        pool  = ASSET_DELAY_POOL[asset]
        code, desc = random.choice(pool)
        crit  = ASSET_CRIT[asset]
        # Critical assets: short delays (5-90 min); non-critical: 5-240 min
        if crit == 1:
            delay_mins = random.randint(5, 90)
        else:
            delay_mins = random.randint(5, 240)
        # Scheduled PMs have narrow delay bands (10-45 min)
        if code.startswith("SCH-"):
            delay_mins = random.randint(10, 45)
        routine_rows.append({
            "timestamp":        fmt_dt(rand_dt()),
            "asset_id":         asset,
            "line":             ASSET_LINE[asset],
            "delay_minutes":    delay_mins,
            "delay_reason_code":code,
            "description":      desc,
        })

    all_rows = failure_delay_rows + routine_rows
    # Sort by timestamp
    all_rows.sort(key=lambda r: r["timestamp"])
    return all_rows


# ---------------------------------------------------------------------------
# 2. Generate fault_error_messages.csv
# ---------------------------------------------------------------------------
def generate_fault_messages(target=1000):
    rows = []

    # --- Failure fault messages (rare but realistic) ---
    # Each failure scenario fires 2-4 episodes; each episode emits 2-5 messages
    failure_fault_rows = []
    for scn in FAILURE_SCENARIOS:
        n_episodes = random.randint(2, 4)
        used_offsets = set()
        for _ in range(n_episodes):
            while True:
                base_dt = rand_dt()
                day_key = base_dt.toordinal()
                if day_key not in used_offsets:
                    used_offsets.add(day_key)
                    break
            for i, fc in enumerate(scn["fault_codes"]):
                template = FAILURE_FAULT_TEMPLATES.get(fc)
                if template is None:
                    continue
                src, sev, msg_tpl = template
                # Stagger messages by 30-300 seconds each
                msg_dt = base_dt + timedelta(seconds=i * random.randint(30, 300))

                # Fill numeric placeholders depending on fault_code
                try:
                    if fc == "VIB-BPFO-DANGER":
                        msg = msg_tpl.format(jitter(3.2, 0.15), jitter(102, 0.08))
                    elif fc == "TEMP-TRIP-100C":
                        msg = msg_tpl.format(jitter(102, 0.05))
                    elif fc == "GMF-DANGER":
                        msg = msg_tpl.format(jitter(11.0, 0.1), jitter(60, 0.2))
                    elif fc == "CHIP-DETECT-ALARM":
                        msg = msg_tpl.format(jitter(60, 0.2))
                    elif fc == "MCSA-RBAR-ALARM":
                        msg = msg_tpl.format(jitter(-34, 0.05))
                    elif fc == "VIB-SEAL-DANGER":
                        msg = msg_tpl.format(jitter(5.4, 0.1), jitter(90, 0.05))
                    elif fc == "SURGE-ALARM":
                        msg = msg_tpl.format(jitter(9, 0.1), jitter(95, 0.08))
                    elif fc == "ASV-CYCLING":
                        msg = msg_tpl.format(random.randint(4, 9))
                    elif fc == "ROLL-SEIZE":
                        msg = msg_tpl
                    elif fc == "SEG-FORCE-HIGH":
                        msg = msg_tpl.format(jitter(540, 0.05))
                    elif fc == "BPS-BREAKOUT-P1":
                        msg = msg_tpl.format(jitter(55, 0.1))
                    elif fc == "TC-VPATTERN":
                        msg = msg_tpl.format(jitter(55, 0.1))
                    elif fc == "OSC-FRICTION-SPIKE":
                        msg = msg_tpl.format(jitter(19, 0.08))
                    elif fc == "FORCE-RIPPLE-HIGH":
                        msg = msg_tpl.format(jitter(8.5, 0.1))
                    elif fc == "SURFACE-DEFECT-PERIODIC":
                        msg = msg_tpl.format(jitter(6.0, 0.1))
                    elif fc == "IDLER-US-ALARM":
                        msg = msg_tpl.format(jitter(16, 0.1))
                    elif fc == "IDLER-TEMP-FIRE":
                        msg = msg_tpl.format(jitter(100, 0.05))
                    elif fc == "FLAME-FAIL-CUTOFF":
                        msg = msg_tpl.format(jitter(38, 0.1))
                    elif fc == "FLUE-O2-HIGH":
                        msg = msg_tpl.format(jitter(5.8, 0.05))
                    elif fc == "ROPE-MFL-RETIRE":
                        msg = msg_tpl.format(jitter(320, 0.08))
                    elif fc == "ROPE-DISCARD-ISO4309":
                        msg = msg_tpl.format(jitter(320, 0.08))
                    elif fc == "SERVO-HUNT":
                        msg = msg_tpl.format(jitter(3.2, 0.1))
                    elif fc == "GAUGE-EXCURSION":
                        msg = msg_tpl.format(jitter(22, 0.1))
                    elif fc == "ISO4406-SERVO-DIRTY":
                        msg = msg_tpl
                    else:
                        msg = msg_tpl
                except Exception:
                    msg = msg_tpl  # fallback if format fails

                failure_fault_rows.append({
                    "timestamp":     fmt_dt(msg_dt),
                    "asset_id":      scn["asset_id"],
                    "source_system": src,
                    "fault_code":    fc,
                    "severity":      sev,
                    "message":       msg,
                })

    # --- Normal/routine fault messages (bulk) ---
    n_normal = target - len(failure_fault_rows)
    normal_rows = []
    for _ in range(n_normal):
        asset = random.choice(ASSET_IDS)
        templates = NORMAL_FAULT_TEMPLATES[asset]
        src, sev, code, msg_tpl, val_gens = random.choice(templates)
        # Use asset-specific value generators for realistic physical values
        try:
            if len(val_gens) == 0:
                msg = msg_tpl
            else:
                vals = [g() for g in val_gens]
                msg = msg_tpl.format(*vals)
        except Exception:
            msg = msg_tpl

        normal_rows.append({
            "timestamp":     fmt_dt(rand_dt()),
            "asset_id":      asset,
            "source_system": src,
            "fault_code":    code,
            "severity":      sev,
            "message":       msg,
        })

    all_rows = failure_fault_rows + normal_rows
    all_rows.sort(key=lambda r: r["timestamp"])
    return all_rows


# ---------------------------------------------------------------------------
# Write CSVs
# ---------------------------------------------------------------------------
def write_csv(filepath, fieldnames, rows):
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return len(rows)


if __name__ == "__main__":
    import os

    delay_rows = generate_delay_logs(target=800)
    fault_rows = generate_fault_messages(target=1000)

    delay_path = os.path.join(OUTPUT_DIR, "equipment_delay_logs.csv")
    fault_path = os.path.join(OUTPUT_DIR, "fault_error_messages.csv")

    n_delay = write_csv(
        delay_path,
        ["timestamp", "asset_id", "line", "delay_minutes", "delay_reason_code", "description"],
        delay_rows,
    )
    n_fault = write_csv(
        fault_path,
        ["timestamp", "asset_id", "source_system", "fault_code", "severity", "message"],
        fault_rows,
    )

    print(f"equipment_delay_logs.csv  : {n_delay} rows  -> {delay_path}")
    print(f"fault_error_messages.csv  : {n_fault} rows  -> {fault_path}")

    # Quick sanity checks
    failure_delay  = sum(1 for r in delay_rows if r["delay_reason_code"] not in
                         [code for asset in ASSET_DELAY_POOL.values() for code, _ in asset])
    failure_faults = sum(1 for r in fault_rows if r["severity"] in ("CRITICAL", "HIGH") and
                         r["fault_code"] not in [t[2] for tpls in NORMAL_FAULT_TEMPLATES.values() for t in tpls])
    failure_rate_faults = failure_faults / n_fault if n_fault else 0

    print(f"\nSanity checks:")
    print(f"  Failure-linked delay rows   : {failure_delay}")
    print(f"  CRITICAL/HIGH fault rows    : {failure_faults}")
    print(f"  Failure fault rate (approx) : {failure_rate_faults:.2%} (target 0.5-5%)")
