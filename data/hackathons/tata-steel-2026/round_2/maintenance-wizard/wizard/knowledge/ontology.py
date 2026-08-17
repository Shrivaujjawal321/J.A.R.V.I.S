"""
wizard.knowledge.ontology
=========================
Steel-plant ISO-14224 ontology definition.

The ONTOLOGY dict is the domain-grounding anchor for all synthetic
knowledge generation. It encodes 5 asset families with:
  - subsystems
  - failure modes (with severity, fault codes, symptoms, sensor signatures)
  - error codes
  - sensor ranges (min/max for temperature_c, pressure_bar, vibration_mm_s, rpm)
  - spare parts catalog stubs

This module is import-only (no side effects, no file I/O).
Call `get_ontology()` to get the dict; call `save_ontology(path)` to write it.

Usage::

    from wizard.knowledge.ontology import get_ontology, save_ontology, ONTOLOGY

    data = get_ontology()
    save_ontology(Path("data/kg/steel_plant_ontology.json"))
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# THE ONTOLOGY — ISO-14224 grounded, 5 asset families
# ---------------------------------------------------------------------------

ONTOLOGY: dict[str, Any] = {
    "schema_version": "1.0",
    "standard": "ISO-14224 (RCM taxonomy for rotating equipment, adapted for steel plant)",
    "plant": "Integrated Steel Plant (ISP) — representative configuration",
    "asset_families": {

        # ================================================================
        # 1. BLAST FURNACE FANS (BF Fan)
        # ================================================================
        "blast_furnace_fan": {
            "iso14224_class": "rotating.centrifugal_fan",
            "description": "High-volume blast air delivery fans for blast furnace hot-blast stoves",
            "equipment_ids": ["BF-FAN-01", "BF-FAN-02", "BF-FAN-03", "EAF-04"],
            "design_parameters": {
                "rated_rpm": 1480,
                "rated_flow_m3h": 180000,
                "rated_pressure_bar": 3.8,
                "motor_power_kw": 4500,
                "bearing_type": "SKF angular contact double row",
            },
            "sensor_ranges": {
                "temperature_c": {
                    "normal_min": 35.0, "normal_max": 85.0,
                    "warning_min": 25.0, "warning_max": 110.0,
                    "critical_min": 15.0, "critical_max": 140.0,
                    "description": "Bearing housing temperature"
                },
                "pressure_bar": {
                    "normal_min": 3.2, "normal_max": 4.2,
                    "warning_min": 2.8, "warning_max": 4.6,
                    "critical_min": 2.0, "critical_max": 5.0,
                    "description": "Discharge pressure"
                },
                "vibration_mm_s": {
                    "normal_min": 0.5, "normal_max": 4.5,
                    "warning_min": 0.0, "warning_max": 7.1,
                    "critical_min": 0.0, "critical_max": 11.2,
                    "description": "Casing vibration RMS velocity (ISO 10816-3)"
                },
                "rpm": {
                    "normal_min": 1440, "normal_max": 1520,
                    "warning_min": 1380, "warning_max": 1560,
                    "critical_min": 1200, "critical_max": 1600,
                    "description": "Shaft rotational speed"
                },
                "current_a": {
                    "normal_min": 380.0, "normal_max": 450.0,
                    "warning_min": 340.0, "warning_max": 500.0,
                    "critical_min": 300.0, "critical_max": 550.0,
                    "description": "Motor stator current"
                }
            },
            "subsystems": [
                {
                    "name": "impeller_assembly",
                    "components": ["impeller_disc", "impeller_blades", "wear_rings"],
                    "failure_modes": [
                        {
                            "id": "FM-BF-001",
                            "name": "Impeller blade erosion",
                            "fault_code": "BF-ERO-001",
                            "iso14224_code": "ERO",
                            "severity": "high",
                            "symptoms": [
                                "Gradual reduction in discharge pressure >0.3 bar/week",
                                "Increased vibration at blade-pass frequency",
                                "Reduced flow rate at same motor current"
                            ],
                            "sensor_signature": {
                                "pressure_bar": "trending_down",
                                "vibration_mm_s": "trending_up",
                                "rpm": "stable"
                            },
                            "root_causes": ["Abrasive particles in blast air", "Inadequate air filtering"],
                            "corrective_actions": ["Replace impeller assembly", "Inspect and upgrade air filter"],
                            "mtbf_days": 540,
                            "requires_parts": ["IMPL-BF-001", "SEAL-BF-001"]
                        },
                        {
                            "id": "FM-BF-002",
                            "name": "Bearing overheating",
                            "fault_code": "BF-BRG-002",
                            "iso14224_code": "OVH",
                            "severity": "critical",
                            "symptoms": [
                                "Bearing temperature >120°C at housing T3",
                                "Lubricant discoloration (darkening)",
                                "High-frequency vibration spike 200-500 Hz"
                            ],
                            "sensor_signature": {
                                "temperature_c": "above_warning",
                                "vibration_mm_s": "spike",
                                "rpm": "stable"
                            },
                            "root_causes": [
                                "Lubricant contamination",
                                "Overloading beyond design RPM",
                                "Cooling water flow interruption"
                            ],
                            "corrective_actions": [
                                "Isolate fan, inspect bearing per SOP-BF-AF-07",
                                "Replace bearing SKF-6310-2RS1",
                                "Flush lubrication system",
                                "Check cooling water circuit"
                            ],
                            "mtbf_days": 720,
                            "requires_parts": ["BRG-SKF-6310", "LUB-GR-002"]
                        },
                        {
                            "id": "FM-BF-003",
                            "name": "Shaft misalignment",
                            "fault_code": "BF-ALN-003",
                            "iso14224_code": "ALN",
                            "severity": "medium",
                            "symptoms": [
                                "1× and 2× RPM vibration peaks",
                                "Elevated axial vibration",
                                "Coupling wear pattern"
                            ],
                            "sensor_signature": {
                                "vibration_mm_s": "above_warning",
                                "temperature_c": "trending_up"
                            },
                            "root_causes": ["Thermal expansion", "Foundation settlement", "Improper reassembly"],
                            "corrective_actions": [
                                "Laser alignment check per SOP-BF-AF-11",
                                "Realign to ±0.05 mm tolerance",
                                "Check and grout foundation anchors"
                            ],
                            "mtbf_days": 365,
                            "requires_parts": ["COUP-BF-001"]
                        }
                    ]
                },
                {
                    "name": "lubrication_system",
                    "components": ["oil_reservoir", "oil_pump", "oil_cooler", "filter_unit"],
                    "failure_modes": [
                        {
                            "id": "FM-BF-004",
                            "name": "Lubrication oil contamination",
                            "fault_code": "BF-LUB-004",
                            "iso14224_code": "CON",
                            "severity": "medium",
                            "symptoms": [
                                "Oil particle count NAS > Class 9",
                                "Oil temperature rising >5°C above baseline",
                                "Filter differential pressure alarm"
                            ],
                            "root_causes": ["Worn filter element", "Seal degradation", "Water ingress"],
                            "corrective_actions": [
                                "Replace filter element per SOP-BF-LUB-03",
                                "Drain and refill with fresh oil (Grade ISO VG 100)",
                                "Inspect all seals"
                            ],
                            "mtbf_days": 180,
                            "requires_parts": ["FILT-BF-010", "OIL-ISO100-200L"]
                        }
                    ]
                }
            ],
            "error_codes": {
                "BF-ERO-001": "Impeller erosion — reduce load, schedule inspection",
                "BF-BRG-002": "Bearing overtemperature CRITICAL — isolate immediately",
                "BF-ALN-003": "Shaft misalignment — schedule laser realignment",
                "BF-LUB-004": "Oil contamination — change filter and oil",
                "BF-VIB-005": "High vibration trip — check balance and alignment",
                "BF-PRE-006": "Low discharge pressure — check inlet and impeller",
                "BF-MOT-007": "Motor overcurrent — check for mechanical overload",
                "BF-COOL-008": "Cooling water flow low — check circuit and pump"
            }
        },

        # ================================================================
        # 2. CENTRIFUGAL PUMPS
        # ================================================================
        "centrifugal_pump": {
            "iso14224_class": "rotating.centrifugal_pump",
            "description": "Process water, cooling water, and hydraulic pumps across ISP",
            "equipment_ids": ["PUMP-CW-01", "PUMP-CW-02", "PUMP-PW-03", "PUMP-BF-04", "PUMP-BOF-05"],
            "design_parameters": {
                "rated_rpm": 1480,
                "rated_flow_m3h": 800,
                "rated_head_m": 65,
                "rated_pressure_bar": 6.4,
                "motor_power_kw": 250,
                "impeller_material": "Cast iron / SS316L for process water"
            },
            "sensor_ranges": {
                "temperature_c": {
                    "normal_min": 20.0, "normal_max": 65.0,
                    "warning_min": 10.0, "warning_max": 80.0,
                    "critical_min": 5.0, "critical_max": 95.0,
                    "description": "Bearing + seal chamber temperature"
                },
                "pressure_bar": {
                    "normal_min": 5.5, "normal_max": 7.2,
                    "warning_min": 4.5, "warning_max": 8.0,
                    "critical_min": 3.0, "critical_max": 9.5,
                    "description": "Discharge pressure"
                },
                "vibration_mm_s": {
                    "normal_min": 0.3, "normal_max": 3.5,
                    "warning_min": 0.0, "warning_max": 6.3,
                    "critical_min": 0.0, "critical_max": 10.0,
                    "description": "Pump casing vibration (ISO 10816-1)"
                },
                "rpm": {
                    "normal_min": 1455, "normal_max": 1505,
                    "warning_min": 1400, "warning_max": 1550,
                    "critical_min": 1200, "critical_max": 1600
                },
                "current_a": {
                    "normal_min": 28.0, "normal_max": 42.0,
                    "warning_min": 22.0, "warning_max": 52.0,
                    "critical_min": 15.0, "critical_max": 65.0
                }
            },
            "subsystems": [
                {
                    "name": "mechanical_seal",
                    "components": ["stationary_seat", "rotating_face", "spring_assembly", "flush_piping"],
                    "failure_modes": [
                        {
                            "id": "FM-PMP-001",
                            "name": "Mechanical seal leakage",
                            "fault_code": "PMP-SEAL-001",
                            "iso14224_code": "LEK",
                            "severity": "high",
                            "symptoms": [
                                "Visible fluid drip at stuffing box >5 drops/min",
                                "Seal chamber temperature rise >15°C",
                                "Increased vibration from seal face contact"
                            ],
                            "root_causes": [
                                "Seal face wear beyond service limit (0.5 mm flatness)",
                                "Dry running episode (cavitation, air ingestion)",
                                "Chemical attack from process fluid"
                            ],
                            "corrective_actions": [
                                "Replace mechanical seal per SOP-PMP-SEAL-02",
                                "Check seal flush circuit, ensure Plan-11 flow 0.5 L/min",
                                "Inspect impeller for cavitation damage"
                            ],
                            "mtbf_days": 480,
                            "requires_parts": ["SEAL-MECH-CW-01", "GSKT-PMP-001"]
                        },
                        {
                            "id": "FM-PMP-002",
                            "name": "Cavitation",
                            "fault_code": "PMP-CAV-002",
                            "iso14224_code": "CAV",
                            "severity": "high",
                            "symptoms": [
                                "Crackling/rattling noise at impeller",
                                "Pressure fluctuation ±1.5 bar at discharge",
                                "Reduced flow with unchanged motor current",
                                "Pitting marks on impeller vanes (visual at overhaul)"
                            ],
                            "root_causes": [
                                "NPSH available < NPSH required",
                                "Suction strainer blocked (dP > 0.3 bar)",
                                "Operating far left of pump curve"
                            ],
                            "corrective_actions": [
                                "Check and clean suction strainer per SOP-PMP-SUMP-01",
                                "Verify suction head, adjust valve position",
                                "Trim impeller per curve if operating off-design"
                            ],
                            "mtbf_days": 300,
                            "requires_parts": ["STRN-PMP-001", "IMPL-PMP-001"]
                        }
                    ]
                },
                {
                    "name": "pump_bearing_set",
                    "components": ["drive_end_bearing", "non_drive_end_bearing", "bearing_housing"],
                    "failure_modes": [
                        {
                            "id": "FM-PMP-003",
                            "name": "Bearing fatigue failure",
                            "fault_code": "PMP-BRG-003",
                            "iso14224_code": "FAT",
                            "severity": "critical",
                            "symptoms": [
                                "Bearing temperature >85°C (threshold: 80°C alarm)",
                                "High-frequency vibration peaks at BPFO/BPFI",
                                "Audible rumbling at low speed"
                            ],
                            "root_causes": [
                                "Exceeded L10 service life (>25,000 operating hours)",
                                "Improper preload or clearance",
                                "Lubricant breakdown (water contamination, oxidation)"
                            ],
                            "corrective_actions": [
                                "Replace both bearings (drive + non-drive end simultaneously)",
                                "Grease with Mobilux EP-2, quantity per SOP-PMP-BRG-05",
                                "Measure shaft runout: max 0.05 mm TIR"
                            ],
                            "mtbf_days": 900,
                            "requires_parts": ["BRG-SKF-6207", "BRG-SKF-6310-2RS1", "LUB-MOB-EP2"]
                        }
                    ]
                }
            ],
            "error_codes": {
                "PMP-SEAL-001": "Seal leakage — monitor and schedule replacement",
                "PMP-CAV-002": "Cavitation detected — check NPSH and strainer",
                "PMP-BRG-003": "Bearing fatigue — urgent replacement required",
                "PMP-VIB-004": "High vibration — check alignment and balance",
                "PMP-FLW-005": "Low flow rate — check strainer and wear rings",
                "PMP-OVC-006": "Motor overcurrent — check for solids in process fluid",
                "PMP-PRE-007": "Low suction pressure — check sump level",
                "PMP-HMR-008": "Water hammer event — check valve operation sequence"
            }
        },

        # ================================================================
        # 3. ROLLER / CONVEYOR BEARINGS
        # ================================================================
        "roller_conveyor_bearing": {
            "iso14224_class": "rotating.rolling_element_bearing",
            "description": "Rolling element bearings on hot-strip-mill roller tables and conveyor drives",
            "equipment_ids": ["BRG-HRM-01", "BRG-HRM-02", "BRG-CVR-03", "BRG-CVR-04", "BRG-CVR-05"],
            "design_parameters": {
                "rated_rpm": 200,
                "radial_load_capacity_kn": 420,
                "axial_load_capacity_kn": 85,
                "bearing_type": "Spherical roller bearing (SRB)",
                "relubrication_interval_hours": 500
            },
            "sensor_ranges": {
                "temperature_c": {
                    "normal_min": 30.0, "normal_max": 70.0,
                    "warning_min": 20.0, "warning_max": 90.0,
                    "critical_min": 15.0, "critical_max": 110.0,
                    "description": "Bearing housing contact temperature"
                },
                "vibration_mm_s": {
                    "normal_min": 0.2, "normal_max": 5.0,
                    "warning_min": 0.0, "warning_max": 8.0,
                    "critical_min": 0.0, "critical_max": 14.0,
                    "description": "Roller table bearing housing vibration"
                },
                "rpm": {
                    "normal_min": 150, "normal_max": 250,
                    "warning_min": 100, "warning_max": 300,
                    "critical_min": 50, "critical_max": 350
                }
            },
            "subsystems": [
                {
                    "name": "bearing_assembly",
                    "components": ["inner_race", "outer_race", "rolling_elements", "cage", "seals"],
                    "failure_modes": [
                        {
                            "id": "FM-BRG-001",
                            "name": "Spalling (pitting) on inner race",
                            "fault_code": "BRG-SPALL-001",
                            "iso14224_code": "SPL",
                            "severity": "critical",
                            "symptoms": [
                                "BPFI harmonic series in vibration spectrum",
                                "Temperature rise >20°C above baseline",
                                "Intermittent metal-on-metal impact noise"
                            ],
                            "root_causes": [
                                "Subsurface fatigue from cyclic rolling contact stress",
                                "Inadequate lubrication (lubricant film breakdown at high temperature)",
                                "Overloading (hot slab weight exceeds bearing rated load)"
                            ],
                            "corrective_actions": [
                                "Immediate shutdown — bearing failure risk",
                                "Replace spherical roller bearing per SOP-BRG-SRB-03",
                                "Inspect shaft for fretting, measure journal diameter",
                                "Verify slab weight compliance with design specification"
                            ],
                            "mtbf_days": 1200,
                            "requires_parts": ["BRG-SRB-22320-E", "LUB-SHELL-ALVANIA-R3", "SEAL-BRG-001"]
                        },
                        {
                            "id": "FM-BRG-002",
                            "name": "Lubricant starvation",
                            "fault_code": "BRG-LUB-002",
                            "iso14224_code": "LUB",
                            "severity": "high",
                            "symptoms": [
                                "Temperature ramp >2°C/hour with no load increase",
                                "Squealing or screeching at bearing",
                                "Dry grease (waxy, discolored) at relubrication nipple"
                            ],
                            "root_causes": [
                                "Missed relubrication (interval exceeded by >20%)",
                                "Blocked grease nipple or distribution line",
                                "Wrong lubricant grade applied"
                            ],
                            "corrective_actions": [
                                "Apply emergency grease (Shell Alvania R3), 45 g per nipple",
                                "Verify auto-lube system operation per SOP-BRG-LUBE-01",
                                "Schedule bearing removal and inspection at next outage"
                            ],
                            "mtbf_days": 365,
                            "requires_parts": ["LUB-SHELL-ALVANIA-R3", "NIPL-BRG-001"]
                        },
                        {
                            "id": "FM-BRG-003",
                            "name": "False brinelling from standstill vibration",
                            "fault_code": "BRG-BRLN-003",
                            "iso14224_code": "WEA",
                            "severity": "medium",
                            "symptoms": [
                                "Equally-spaced indentations on raceway (visual at overhaul)",
                                "Increased starting torque after long standstill",
                                "Reddish-brown powder (iron oxide) at bearing seals"
                            ],
                            "root_causes": [
                                "External vibration during plant shutdown periods",
                                "No anti-fretting compound applied at installation"
                            ],
                            "corrective_actions": [
                                "Apply VCI corrosion inhibitor before extended shutdown",
                                "Rotate shaft quarterly during maintenance windows",
                                "Replace if indentation depth >0.1 mm"
                            ],
                            "mtbf_days": 1800,
                            "requires_parts": ["COMP-VCI-001", "BRG-SRB-22320-E"]
                        }
                    ]
                }
            ],
            "error_codes": {
                "BRG-SPALL-001": "Inner race spalling — CRITICAL, shutdown required",
                "BRG-LUB-002": "Lubrication starvation — apply grease immediately",
                "BRG-BRLN-003": "False brinelling — inspect at next outage",
                "BRG-SEAT-004": "Bearing seat fretting — rebore or sleeve",
                "BRG-CAGE-005": "Cage fracture — emergency replacement",
                "BRG-CORR-006": "Corrosion pitting — check seals and moisture ingress",
                "BRG-THERM-007": "Thermal gradient spalling — check operating temperature"
            }
        },

        # ================================================================
        # 4. HYDRAULIC POWER UNITS
        # ================================================================
        "hydraulic_power_unit": {
            "iso14224_class": "fluid_system.hydraulic_unit",
            "description": "Hydraulic HPUs for rolling mill screwdown, press brakes, and ladle tilters",
            "equipment_ids": ["HPU-RM-01", "HPU-RM-02", "HPU-LDL-03", "HPU-BF-04", "HPU-CCM-05"],
            "design_parameters": {
                "system_pressure_bar": 280,
                "reservoir_volume_l": 2000,
                "pump_type": "Axial piston variable-displacement",
                "pump_rated_flow_l_min": 400,
                "motor_power_kw": 185,
                "filter_micron_rating": 10
            },
            "sensor_ranges": {
                "temperature_c": {
                    "normal_min": 35.0, "normal_max": 55.0,
                    "warning_min": 25.0, "warning_max": 65.0,
                    "critical_min": 15.0, "critical_max": 75.0,
                    "description": "Hydraulic oil reservoir temperature"
                },
                "pressure_bar": {
                    "normal_min": 240.0, "normal_max": 300.0,
                    "warning_min": 200.0, "warning_max": 320.0,
                    "critical_min": 160.0, "critical_max": 340.0,
                    "description": "System pressure at accumulator"
                },
                "vibration_mm_s": {
                    "normal_min": 0.5, "normal_max": 4.0,
                    "warning_min": 0.0, "warning_max": 7.0,
                    "critical_min": 0.0, "critical_max": 12.0,
                    "description": "HPU pump/motor assembly vibration"
                },
                "rpm": {
                    "normal_min": 1450, "normal_max": 1510,
                    "warning_min": 1400, "warning_max": 1560,
                    "critical_min": 1200, "critical_max": 1600
                }
            },
            "subsystems": [
                {
                    "name": "hydraulic_pump",
                    "components": ["piston_barrel", "valve_plate", "swashplate", "port_block"],
                    "failure_modes": [
                        {
                            "id": "FM-HPU-001",
                            "name": "Pump internal leakage (swashplate wear)",
                            "fault_code": "HPU-LEAK-001",
                            "iso14224_code": "INT-LEAK",
                            "severity": "high",
                            "symptoms": [
                                "System pressure drops below 240 bar at full stroke",
                                "Pump case drain flow >5 L/min (design: <2 L/min)",
                                "Oil temperature rising despite normal cooling circuit"
                            ],
                            "root_causes": [
                                "Swashplate/piston barrel wear (clearance >0.02 mm)",
                                "Oil contamination NAS Class >8 accelerating wear",
                                "Operating over 300 bar intermittently"
                            ],
                            "corrective_actions": [
                                "Measure case drain flow, if >5 L/min: overhaul pump",
                                "Replace piston/barrel set per SOP-HPU-PMP-04",
                                "Flush system and change hydraulic oil (ISO VG 46)",
                                "Check and replace return-line filter element"
                            ],
                            "mtbf_days": 1080,
                            "requires_parts": ["KIT-HPU-RBL-001", "OIL-ISO46-1000L", "FILT-HPU-010"]
                        },
                        {
                            "id": "FM-HPU-002",
                            "name": "Pressure relief valve stuck open",
                            "fault_code": "HPU-PRV-002",
                            "iso14224_code": "PRV-FAIL",
                            "severity": "critical",
                            "symptoms": [
                                "System pressure cannot build above 180 bar",
                                "PRV bypass flow heating oil rapidly",
                                "Control system unable to actuate downstream cylinders"
                            ],
                            "root_causes": [
                                "Contamination particle lodged in valve seat",
                                "Spring fatigue (set pressure drift >15%)",
                                "Corrosion on valve poppet"
                            ],
                            "corrective_actions": [
                                "EMERGENCY: all actuators disabled — notify shift supervisor",
                                "Isolate HPU, clean/replace relief valve per SOP-HPU-PRV-02",
                                "Flush system, change filter, take oil sample"
                            ],
                            "mtbf_days": 720,
                            "requires_parts": ["VLV-PRV-HPU-280B", "GSKT-HPU-001"]
                        }
                    ]
                },
                {
                    "name": "oil_conditioning_system",
                    "components": ["reservoir", "heat_exchanger", "return_filter", "breather_filter"],
                    "failure_modes": [
                        {
                            "id": "FM-HPU-003",
                            "name": "Oil contamination — high particle count",
                            "fault_code": "HPU-OIL-003",
                            "iso14224_code": "CON",
                            "severity": "medium",
                            "symptoms": [
                                "ISO 4406 cleanliness: 21/19/16 (target: 18/16/13)",
                                "Return filter bypass indicator popped",
                                "Servo valve spool sticking intermittently"
                            ],
                            "root_causes": [
                                "Worn pump generating metallic particles",
                                "Breather filter bypassing (clogged element)",
                                "Water ingress from condensation (Karl Fischer >300 ppm)"
                            ],
                            "corrective_actions": [
                                "Install offline kidney-loop filter (10 micron) for 24h",
                                "Replace breather cartridge (annual regardless)",
                                "Oil analysis — if water >500 ppm, drain and refill"
                            ],
                            "mtbf_days": 270,
                            "requires_parts": ["FILT-HPU-010", "BRTH-HPU-001"]
                        }
                    ]
                }
            ],
            "error_codes": {
                "HPU-LEAK-001": "Pump internal leakage — measure drain flow",
                "HPU-PRV-002": "Relief valve failure CRITICAL — isolate HPU",
                "HPU-OIL-003": "Oil contamination — filter and sample",
                "HPU-TEMP-004": "Oil overtemperature — check heat exchanger",
                "HPU-PRE-005": "System pressure loss — check pump and accumulators",
                "HPU-FLW-006": "Low flow rate — check pump displacement control",
                "HPU-CAV-007": "Pump cavitation — check suction strainer and oil level",
                "HPU-SRV-008": "Servo valve fault — clean or replace"
            }
        },

        # ================================================================
        # 5. HOT STRIP MILL CONVEYORS (Run-out table conveyors)
        # ================================================================
        "hot_strip_mill_conveyor": {
            "iso14224_class": "mechanical.belt_conveyor_roller_table",
            "description": "Hot-strip run-out table driven roller conveyors for slab/coil transport",
            "equipment_ids": ["CONV-ROT-01", "CONV-ROT-02", "CONV-ROT-03", "CONV-FBL-04", "CONV-CCM-05"],
            "design_parameters": {
                "belt_width_mm": 2050,
                "drive_roller_diameter_mm": 340,
                "roller_pitch_mm": 250,
                "max_strip_temp_c": 900,
                "max_strip_weight_t": 35,
                "drive_power_kw_per_roller": 22
            },
            "sensor_ranges": {
                "temperature_c": {
                    "normal_min": 40.0, "normal_max": 120.0,
                    "warning_min": 30.0, "warning_max": 150.0,
                    "critical_min": 20.0, "critical_max": 200.0,
                    "description": "Drive roller bearing temperature (ambient + radiation)"
                },
                "vibration_mm_s": {
                    "normal_min": 1.0, "normal_max": 7.0,
                    "warning_min": 0.0, "warning_max": 10.0,
                    "critical_min": 0.0, "critical_max": 18.0,
                    "description": "Roller table structural vibration"
                },
                "rpm": {
                    "normal_min": 80, "normal_max": 400,
                    "warning_min": 50, "warning_max": 500,
                    "critical_min": 20, "critical_max": 600,
                    "description": "Drive roller speed (varies with strip speed)"
                },
                "current_a": {
                    "normal_min": 8.0, "normal_max": 22.0,
                    "warning_min": 5.0, "warning_max": 32.0,
                    "critical_min": 2.0, "critical_max": 40.0,
                    "description": "Per-roller drive motor current"
                }
            },
            "subsystems": [
                {
                    "name": "drive_roller_assembly",
                    "components": ["roller_barrel", "drive_shaft", "flange_couplings", "roller_bearing_set"],
                    "failure_modes": [
                        {
                            "id": "FM-CVR-001",
                            "name": "Roller barrel surface spalling",
                            "fault_code": "CVR-SPALL-001",
                            "iso14224_code": "SPL",
                            "severity": "high",
                            "symptoms": [
                                "Surface pitting visible on roller barrel (>10 pits per 300mm)",
                                "Strip surface quality defects (marks at roller pitch interval)",
                                "Irregular vibration pattern synchronous with roller rotation"
                            ],
                            "root_causes": [
                                "Thermal fatigue from repeated hot slab contact",
                                "Inadequate water cooling flow on roller surface",
                                "Overloading from cobbling events"
                            ],
                            "corrective_actions": [
                                "Remove and resurface roller (turning to minimum diameter)",
                                "Replace if barrel OD < 320 mm (out-of-tolerance)",
                                "Verify water cooling flow rate per SOP-CONV-WTR-02"
                            ],
                            "mtbf_days": 450,
                            "requires_parts": ["ROLL-ROT-001", "SEAL-ROLL-001", "BRG-ROLL-001"]
                        },
                        {
                            "id": "FM-CVR-002",
                            "name": "Drive coupling failure",
                            "fault_code": "CVR-COUP-002",
                            "iso14224_code": "FRC-FAIL",
                            "severity": "critical",
                            "symptoms": [
                                "Motor current spikes then drops to zero — coupling shear",
                                "Strip stops advancing on table section",
                                "Coupling spider rubber in pieces (visual)"
                            ],
                            "root_causes": [
                                "Torque overload during strip cobble or jam",
                                "Coupling rubber element aged beyond 3-year service limit",
                                "Misalignment >0.3 mm causing uneven load"
                            ],
                            "corrective_actions": [
                                "STOP conveyor drive — strip jam hazard",
                                "Replace coupling spider element per SOP-CONV-COUP-01",
                                "Check and correct shaft alignment to ±0.05 mm"
                            ],
                            "mtbf_days": 540,
                            "requires_parts": ["COUP-CONV-SPIDER", "COUP-CONV-HUB"]
                        }
                    ]
                },
                {
                    "name": "water_cooling_system",
                    "components": ["spray_headers", "spray_nozzles", "water_pump", "flow_control_valve"],
                    "failure_modes": [
                        {
                            "id": "FM-CVR-003",
                            "name": "Spray nozzle blockage",
                            "fault_code": "CVR-NZL-003",
                            "iso14224_code": "BLK",
                            "severity": "medium",
                            "symptoms": [
                                "Uneven strip cooling (pyrometer shows hot spots >±30°C)",
                                "Reduced water flow on affected header section",
                                "Scale buildup visible on nozzle tips"
                            ],
                            "root_causes": [
                                "Scale precipitation in process water (hardness >200 ppm CaCO3)",
                                "No chemical dosing for scale inhibition",
                                "Nozzle tip erosion reducing orifice size"
                            ],
                            "corrective_actions": [
                                "Clean nozzles with descalant per SOP-CONV-NZL-01",
                                "Check and calibrate chemical dosing system",
                                "Replace nozzles if erosion >20% of orifice diameter"
                            ],
                            "mtbf_days": 90,
                            "requires_parts": ["NZL-CONV-SS316", "CHEM-DESCALANT"]
                        }
                    ]
                }
            ],
            "error_codes": {
                "CVR-SPALL-001": "Roller spalling — check strip surface quality, schedule resurface",
                "CVR-COUP-002": "Coupling failure CRITICAL — stop conveyor immediately",
                "CVR-NZL-003": "Nozzle blockage — clean nozzles, check water quality",
                "CVR-BRG-004": "Roller bearing overheat — check lubrication and load",
                "CVR-SLIP-005": "Belt slip detected — check tension and drive pinion",
                "CVR-VIB-006": "Structural resonance — check roller balance and foundation",
                "CVR-MOT-007": "Drive motor overcurrent — check for roller jam",
                "CVR-CRK-008": "Roller crack detected — immediate replacement required"
            }
        }
    },

    # ================================================================
    # CROSS-FAMILY SPARE PARTS CATALOG
    # ================================================================
    "spare_parts_catalog": [
        # Bearings
        {
            "part_number": "BRG-SKF-6310-2RS1",
            "part_name": "SKF Deep Groove Ball Bearing 6310-2RS1",
            "compatible_families": ["blast_furnace_fan", "centrifugal_pump"],
            "stock_qty": 0,
            "min_stock_qty": 4,
            "unit_cost_inr": 4800,
            "lead_time_days": 14,
            "supplier": "SKF India Ltd, Pune",
            "criticality_override": "critical",
            "note": "OUT OF STOCK — 14-day lead time. Critical path for BF-BRG-002."
        },
        {
            "part_number": "BRG-SKF-6207",
            "part_name": "SKF Deep Groove Ball Bearing 6207",
            "compatible_families": ["centrifugal_pump"],
            "stock_qty": 8,
            "min_stock_qty": 4,
            "unit_cost_inr": 1200,
            "lead_time_days": 3,
            "supplier": "SKF India Ltd, Pune",
            "criticality_override": "standard"
        },
        {
            "part_number": "BRG-SRB-22320-E",
            "part_name": "FAG Spherical Roller Bearing 22320-E",
            "compatible_families": ["roller_conveyor_bearing"],
            "stock_qty": 2,
            "min_stock_qty": 6,
            "unit_cost_inr": 22500,
            "lead_time_days": 7,
            "supplier": "Schaeffler India Pvt Ltd",
            "criticality_override": "critical"
        },
        # Seals
        {
            "part_number": "SEAL-MECH-CW-01",
            "part_name": "Burgmann M7N Mechanical Seal DN50",
            "compatible_families": ["centrifugal_pump"],
            "stock_qty": 3,
            "min_stock_qty": 2,
            "unit_cost_inr": 18500,
            "lead_time_days": 5,
            "supplier": "EagleBurgmann India",
            "criticality_override": "critical"
        },
        {
            "part_number": "SEAL-BF-001",
            "part_name": "Labyrinthe Seal Assembly BF Fan Type-B",
            "compatible_families": ["blast_furnace_fan"],
            "stock_qty": 1,
            "min_stock_qty": 2,
            "unit_cost_inr": 35000,
            "lead_time_days": 21,
            "supplier": "BHEL Hyderabad",
            "criticality_override": "critical",
            "note": "Low stock — reorder required. Long lead time 21 days."
        },
        # Filters
        {
            "part_number": "FILT-BF-010",
            "part_name": "Oil Filter Element BF Fan Lube System (25 micron)",
            "compatible_families": ["blast_furnace_fan"],
            "stock_qty": 12,
            "min_stock_qty": 6,
            "unit_cost_inr": 2200,
            "lead_time_days": 2,
            "supplier": "Pall India Pvt Ltd",
            "criticality_override": "standard"
        },
        {
            "part_number": "FILT-HPU-010",
            "part_name": "Hydraulic Return-Line Filter Element (10 micron)",
            "compatible_families": ["hydraulic_power_unit"],
            "stock_qty": 8,
            "min_stock_qty": 4,
            "unit_cost_inr": 4500,
            "lead_time_days": 3,
            "supplier": "Bosch Rexroth India",
            "criticality_override": "standard"
        },
        # Lubricants
        {
            "part_number": "LUB-SHELL-ALVANIA-R3",
            "part_name": "Shell Alvania R3 Lithium Grease 50kg",
            "compatible_families": ["roller_conveyor_bearing", "blast_furnace_fan"],
            "stock_qty": 4,
            "min_stock_qty": 2,
            "unit_cost_inr": 8500,
            "lead_time_days": 2,
            "supplier": "Shell India Markets Pvt Ltd",
            "criticality_override": "standard"
        },
        {
            "part_number": "OIL-ISO46-1000L",
            "part_name": "Hydraulic Oil ISO VG 46 Mineral (1000L IBC)",
            "compatible_families": ["hydraulic_power_unit"],
            "stock_qty": 3,
            "min_stock_qty": 2,
            "unit_cost_inr": 95000,
            "lead_time_days": 4,
            "supplier": "Total Energies India",
            "criticality_override": "standard"
        },
        # Rebuild kits
        {
            "part_number": "KIT-HPU-RBL-001",
            "part_name": "Rexroth A10V100 Axial Piston Pump Rebuild Kit",
            "compatible_families": ["hydraulic_power_unit"],
            "stock_qty": 0,
            "min_stock_qty": 1,
            "unit_cost_inr": 185000,
            "lead_time_days": 14,
            "supplier": "Bosch Rexroth India",
            "criticality_override": "critical",
            "note": "OUT OF STOCK — 14-day lead time. Critical for HPU-LEAK-001 repair."
        },
        # Conveyor parts
        {
            "part_number": "COUP-CONV-SPIDER",
            "part_name": "Jaw Coupling Spider Element (Polyurethane 94A)",
            "compatible_families": ["hot_strip_mill_conveyor"],
            "stock_qty": 20,
            "min_stock_qty": 10,
            "unit_cost_inr": 3200,
            "lead_time_days": 1,
            "supplier": "Rathi Transmissions Pvt Ltd, Nagpur",
            "criticality_override": "standard"
        },
        {
            "part_number": "ROLL-ROT-001",
            "part_name": "Run-Out Table Drive Roller Barrel 340mm OD",
            "compatible_families": ["hot_strip_mill_conveyor"],
            "stock_qty": 1,
            "min_stock_qty": 3,
            "unit_cost_inr": 125000,
            "lead_time_days": 14,
            "supplier": "Steel Strips India, Ludhiana",
            "criticality_override": "critical",
            "note": "Low stock. Lead time 14 days for new supply."
        },
        {
            "part_number": "NZL-CONV-SS316",
            "part_name": "Spray Nozzle SS316 Full-Cone 90deg (per unit)",
            "compatible_families": ["hot_strip_mill_conveyor"],
            "stock_qty": 150,
            "min_stock_qty": 50,
            "unit_cost_inr": 850,
            "lead_time_days": 2,
            "supplier": "Lechler India Pvt Ltd",
            "criticality_override": "standard"
        },
        {
            "part_number": "VLV-PRV-HPU-280B",
            "part_name": "Pressure Relief Valve 280 bar (Parker PD Series)",
            "compatible_families": ["hydraulic_power_unit"],
            "stock_qty": 2,
            "min_stock_qty": 2,
            "unit_cost_inr": 28000,
            "lead_time_days": 5,
            "supplier": "Parker Hannifin India",
            "criticality_override": "critical"
        }
    ],

    # ================================================================
    # MAINTENANCE ACTION TAXONOMY
    # ================================================================
    "maintenance_action_taxonomy": {
        "corrective": [
            "Replace bearing", "Replace mechanical seal", "Replace impeller",
            "Realign shaft", "Replace coupling", "Rebuild pump", "Replace valve",
            "Flush lubrication system", "Replace filter element", "Weld repair"
        ],
        "preventive": [
            "Lubrication top-up", "Filter change", "Oil sample analysis",
            "Vibration baseline check", "Thermal imaging survey", "Alignment check",
            "Coupling inspection", "Seal inspection", "Pump performance test",
            "Bearing visual inspection"
        ],
        "predictive": [
            "Online vibration monitoring", "Oil analysis (wear debris)",
            "Thermography scan", "Motor current signature analysis",
            "Acoustic emission monitoring", "Ultrasonic thickness measurement"
        ],
        "emergency": [
            "Emergency shutdown — isolate equipment",
            "Immediate bearing replacement", "Emergency coupling replacement",
            "Emergency PRV replacement", "Emergency oil change"
        ]
    },

    # ================================================================
    # EAF-04 DEMO ASSET — the scripted 90-second CRITICAL alert target
    # ================================================================
    "demo_asset": {
        "asset_id": "EAF-04",
        "asset_family": "blast_furnace_fan",
        "description": (
            "BF Fan Unit 4 — auxiliary blast air fan for EAF area. "
            "Demo asset for the scripted 90-second CRITICAL alert sequence."
        ),
        "scripted_failure_scenario": {
            "fault_code": "BF-BRG-002",
            "failure_mode": "Bearing overheating",
            "trigger_seconds": 90,
            "sensor_ramp": {
                "temperature_c": {"start": 78.0, "at_trigger": 142.0, "rate_per_s": 0.71},
                "vibration_mm_s": {"start": 3.2, "at_trigger": 9.8, "rate_per_s": 0.072},
                "rpm": {"start": 1480, "at_trigger": 1465, "rate_per_s": -0.17}
            },
            "critical_part": "BRG-SKF-6310-2RS1",
            "part_status": "out_of_stock",
            "part_lead_time_days": 14,
            "alert_message": (
                "CRITICAL: EAF-04 bearing temperature 142°C exceeds SOP-BF-AF-07 "
                "threshold (120°C). Failure imminent. Replacement bearing BRG-SKF-6310-2RS1 "
                "OUT OF STOCK — 14-day lead time. ORDER NOW and schedule emergency shutdown."
            )
        }
    }
}


def get_ontology() -> dict:
    """Return the complete ontology dict (pure function, no I/O)."""
    return ONTOLOGY


def save_ontology(path: Path) -> None:
    """Serialize the ontology to JSON at the given path. Creates parent dirs."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(ONTOLOGY, indent=2, default=str), encoding="utf-8")
