"""
wizard.knowledge.fmea_graph
============================
Hand-authored ISO-14224 FMEA DiGraph for steel-plant equipment.

Graph schema (node types and edge labels):
    Nodes (typed via 'node_type' attribute):
        EquipmentFamily  → EquipmentUnit → Subsystem → Component →
        FailureMode → RootCause → Effect → Action

    Edges (directed, typed via 'relation' attribute):
        HAS_UNIT          EquipmentFamily → EquipmentUnit
        HAS_SUBSYSTEM     EquipmentUnit → Subsystem
        HAS_COMPONENT     Subsystem → Component
        CAN_FAIL_AS       Component → FailureMode
        CAUSED_BY         FailureMode → RootCause
        LEADS_TO          FailureMode → Effect
        DETECTED_BY       FailureMode → Sensor (sensor signal descriptor)
        RESOLVED_BY       FailureMode → Action
        REQUIRES_PART     Action → SparePart
        FOLLOWS_SOP       Action → SOPReference
        CONFIRMED_BY_ENGINEER  (written at runtime when engineer confirms RCA)
        OVERRIDDEN_BY_ENGINEER (written at runtime when engineer overrides RCA)

The graph is serialized to data/kg/steel_plant_fmea.json using NetworkX's
node_link_data format. This file is loaded by wizard.rag.kg_retriever at
startup (lazy, <100ms for this graph size).

Usage::

    from wizard.knowledge.fmea_graph import build_fmea_graph, save_fmea_graph

    G = build_fmea_graph()
    print(f"Nodes: {G.number_of_nodes()}, Edges: {G.number_of_edges()}")
    save_fmea_graph(G, Path("data/kg/steel_plant_fmea.json"))
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import networkx as nx

# ---------------------------------------------------------------------------
# NODE HELPER
# ---------------------------------------------------------------------------

def _node(
    G: nx.DiGraph,
    node_id: str,
    node_type: str,
    label: str,
    **attrs: Any,
) -> str:
    """Add a node to G if not present; return node_id."""
    if node_id not in G:
        G.add_node(node_id, node_type=node_type, label=label, **attrs)
    return node_id


def _edge(
    G: nx.DiGraph,
    src: str,
    dst: str,
    relation: str,
    **attrs: Any,
) -> None:
    """Add a directed edge with relation label."""
    G.add_edge(src, dst, relation=relation, **attrs)


# ---------------------------------------------------------------------------
# MAIN BUILDER
# ---------------------------------------------------------------------------

def build_fmea_graph() -> nx.DiGraph:
    """
    Build and return the full steel-plant FMEA DiGraph.

    Node count target: 200-350 nodes.
    Edge count target: 300-500 edges.

    Returns
    -------
    nx.DiGraph
        The populated FMEA graph.
    """
    G = nx.DiGraph(
        name="steel_plant_fmea",
        standard="ISO-14224 (adapted for integrated steel plant)",
        schema_version="1.0",
    )

    _build_blast_furnace_fan(G)
    _build_centrifugal_pump(G)
    _build_roller_conveyor_bearing(G)
    _build_hydraulic_power_unit(G)
    _build_hot_strip_mill_conveyor(G)
    _build_shared_sop_nodes(G)
    _build_spare_part_nodes(G)
    _build_sensor_nodes(G)

    return G


# ---------------------------------------------------------------------------
# BLAST FURNACE FAN
# ---------------------------------------------------------------------------

def _build_blast_furnace_fan(G: nx.DiGraph) -> None:
    # Equipment family
    fam = _node(G, "FAM:BF_FAN", "EquipmentFamily",
                "Blast Furnace Fan",
                iso14224_class="rotating.centrifugal_fan",
                description="High-volume blast air delivery fans")

    for unit_id, unit_label in [
        ("UNIT:BF-FAN-01", "BF Fan Unit 1"),
        ("UNIT:BF-FAN-02", "BF Fan Unit 2"),
        ("UNIT:BF-FAN-03", "BF Fan Unit 3"),
        ("UNIT:EAF-04",    "EAF Fan Unit 4 (Demo Asset)"),
    ]:
        unit = _node(G, unit_id, "EquipmentUnit", unit_label,
                     asset_id=unit_label.split("(")[0].strip(),
                     criticality="critical" if "EAF-04" in unit_id else "high")
        _edge(G, fam, unit, "HAS_UNIT")

        # Subsystem: impeller
        ss_imp = _node(G, f"{unit_id}:SS:IMPELLER", "Subsystem",
                       "Impeller Assembly", unit_ref=unit_id)
        _edge(G, unit, ss_imp, "HAS_SUBSYSTEM")

        # Component: impeller disc
        comp_disc = _node(G, f"{unit_id}:COMP:IMP_DISC", "Component",
                          "Impeller Disc", unit_ref=unit_id)
        comp_blades = _node(G, f"{unit_id}:COMP:IMP_BLADES", "Component",
                            "Impeller Blades", unit_ref=unit_id)
        comp_wear_rings = _node(G, f"{unit_id}:COMP:WEAR_RINGS", "Component",
                                "Wear Rings", unit_ref=unit_id)
        _edge(G, ss_imp, comp_disc, "HAS_COMPONENT")
        _edge(G, ss_imp, comp_blades, "HAS_COMPONENT")
        _edge(G, ss_imp, comp_wear_rings, "HAS_COMPONENT")

        # FM-BF-001: Impeller blade erosion
        fm_ero = _node(G, f"{unit_id}:FM:BF-ERO-001", "FailureMode",
                       "Impeller Blade Erosion",
                       fault_code="BF-ERO-001", severity="high",
                       iso14224_code="ERO", mtbf_days=540)
        _edge(G, comp_blades, fm_ero, "CAN_FAIL_AS")

        rc_abrasive = _node(G, "RC:ABRASIVE_PARTICLES", "RootCause",
                            "Abrasive particles in blast air",
                            category="process_contamination")
        rc_filter = _node(G, "RC:INADEQUATE_FILTERING", "RootCause",
                          "Inadequate air inlet filtering")
        _edge(G, fm_ero, rc_abrasive, "CAUSED_BY")
        _edge(G, fm_ero, rc_filter, "CAUSED_BY")

        eff_pressure = _node(G, "EFF:REDUCED_DISCHARGE_PRESSURE", "Effect",
                             "Reduced discharge pressure",
                             severity="high",
                             impact="Blast furnace tuyere insufficient air supply")
        _edge(G, fm_ero, eff_pressure, "LEADS_TO")

        act_replace_imp = _node(G, "ACT:REPLACE_IMPELLER_BF", "Action",
                                "Replace impeller assembly (BF Fan)",
                                maintenance_type="corrective",
                                estimated_hours=16.0)
        act_upgrade_filter = _node(G, "ACT:UPGRADE_AIR_FILTER", "Action",
                                   "Inspect and upgrade inlet air filter",
                                   maintenance_type="corrective",
                                   estimated_hours=4.0)
        _edge(G, fm_ero, act_replace_imp, "RESOLVED_BY")
        _edge(G, fm_ero, act_upgrade_filter, "RESOLVED_BY")

        # FM-BF-002: Bearing overheating (CRITICAL — the demo alert)
        fm_brg_ovht = _node(G, f"{unit_id}:FM:BF-BRG-002", "FailureMode",
                            "Bearing Overheating",
                            fault_code="BF-BRG-002", severity="critical",
                            iso14224_code="OVH", mtbf_days=720,
                            is_demo_fault=(unit_id == "UNIT:EAF-04"))
        _edge(G, comp_disc, fm_brg_ovht, "CAN_FAIL_AS")

        rc_lube_cont = _node(G, "RC:LUBE_CONTAMINATION", "RootCause",
                             "Lubricant contamination (water/particles)")
        rc_overload_rpm = _node(G, "RC:OVERLOAD_RPM", "RootCause",
                                "Overloading beyond design RPM")
        rc_cooling_water = _node(G, "RC:COOLING_WATER_INTERRUPT", "RootCause",
                                 "Cooling water flow interruption")
        _edge(G, fm_brg_ovht, rc_lube_cont, "CAUSED_BY")
        _edge(G, fm_brg_ovht, rc_overload_rpm, "CAUSED_BY")
        _edge(G, fm_brg_ovht, rc_cooling_water, "CAUSED_BY")

        eff_brg_fail = _node(G, "EFF:BEARING_SEIZURE", "Effect",
                             "Bearing seizure / shaft lock",
                             severity="critical",
                             impact="Unplanned BF fan shutdown — blast furnace airflow loss",
                             downtime_hours_min=24.0)
        _edge(G, fm_brg_ovht, eff_brg_fail, "LEADS_TO")

        act_isolate = _node(G, "ACT:ISOLATE_BF_FAN", "Action",
                            "Isolate fan immediately per SOP-BF-AF-07",
                            maintenance_type="emergency",
                            safety_critical=True)
        act_replace_brg = _node(G, "ACT:REPLACE_BRG_SKF6310", "Action",
                                "Replace bearing SKF-6310-2RS1",
                                maintenance_type="corrective",
                                estimated_hours=8.0,
                                part_ref="BRG-SKF-6310-2RS1")
        act_flush_lube = _node(G, "ACT:FLUSH_LUBE_SYSTEM_BF", "Action",
                               "Flush lubrication system, refill ISO VG 100",
                               maintenance_type="corrective",
                               estimated_hours=4.0)
        act_check_cooling = _node(G, "ACT:CHECK_COOLING_CIRCUIT", "Action",
                                  "Check and restore cooling water circuit",
                                  maintenance_type="corrective",
                                  estimated_hours=2.0)
        _edge(G, fm_brg_ovht, act_isolate, "RESOLVED_BY")
        _edge(G, fm_brg_ovht, act_replace_brg, "RESOLVED_BY")
        _edge(G, fm_brg_ovht, act_flush_lube, "RESOLVED_BY")
        _edge(G, fm_brg_ovht, act_check_cooling, "RESOLVED_BY")

        # FM-BF-003: Shaft misalignment
        comp_shaft = _node(G, f"{unit_id}:COMP:SHAFT", "Component",
                           "Drive Shaft + Coupling", unit_ref=unit_id)
        _edge(G, ss_imp, comp_shaft, "HAS_COMPONENT")

        fm_misalign = _node(G, f"{unit_id}:FM:BF-ALN-003", "FailureMode",
                            "Shaft Misalignment",
                            fault_code="BF-ALN-003", severity="medium",
                            iso14224_code="ALN", mtbf_days=365)
        _edge(G, comp_shaft, fm_misalign, "CAN_FAIL_AS")

        rc_thermal = _node(G, "RC:THERMAL_EXPANSION", "RootCause",
                           "Thermal expansion causing shaft growth")
        rc_foundation = _node(G, "RC:FOUNDATION_SETTLEMENT", "RootCause",
                              "Foundation settlement post-installation")
        _edge(G, fm_misalign, rc_thermal, "CAUSED_BY")
        _edge(G, fm_misalign, rc_foundation, "CAUSED_BY")

        eff_vib_high = _node(G, "EFF:HIGH_VIBRATION_1X2X", "Effect",
                             "1× and 2× RPM vibration elevation",
                             severity="medium",
                             impact="Accelerated bearing wear, noise")
        _edge(G, fm_misalign, eff_vib_high, "LEADS_TO")

        act_laser_align = _node(G, "ACT:LASER_ALIGNMENT", "Action",
                                "Laser alignment check and correction per SOP-BF-AF-11",
                                maintenance_type="corrective",
                                estimated_hours=6.0,
                                tolerance_mm=0.05)
        _edge(G, fm_misalign, act_laser_align, "RESOLVED_BY")

        # Subsystem: lubrication
        ss_lube = _node(G, f"{unit_id}:SS:LUBE", "Subsystem",
                        "Lubrication System", unit_ref=unit_id)
        _edge(G, unit, ss_lube, "HAS_SUBSYSTEM")

        comp_oil_pump = _node(G, f"{unit_id}:COMP:OIL_PUMP", "Component",
                              "Oil Pump", unit_ref=unit_id)
        comp_oil_filter = _node(G, f"{unit_id}:COMP:OIL_FILTER", "Component",
                                "Oil Filter Element", unit_ref=unit_id)
        _edge(G, ss_lube, comp_oil_pump, "HAS_COMPONENT")
        _edge(G, ss_lube, comp_oil_filter, "HAS_COMPONENT")

        fm_oil_cont = _node(G, f"{unit_id}:FM:BF-LUB-004", "FailureMode",
                            "Lubrication Oil Contamination",
                            fault_code="BF-LUB-004", severity="medium",
                            iso14224_code="CON", mtbf_days=180)
        _edge(G, comp_oil_filter, fm_oil_cont, "CAN_FAIL_AS")

        rc_worn_filter = _node(G, "RC:WORN_FILTER_ELEMENT", "RootCause",
                               "Worn/clogged filter element (dP > 2 bar)")
        _edge(G, fm_oil_cont, rc_worn_filter, "CAUSED_BY")

        eff_bearing_oil = _node(G, "EFF:BEARING_OIL_STARVATION", "Effect",
                                "Bearing oil film breakdown → overheating",
                                severity="high")
        _edge(G, fm_oil_cont, eff_bearing_oil, "LEADS_TO")

        act_change_filter = _node(G, "ACT:CHANGE_OIL_FILTER_BF", "Action",
                                  "Replace oil filter element per SOP-BF-LUB-03",
                                  maintenance_type="preventive",
                                  estimated_hours=1.5)
        act_drain_refill = _node(G, "ACT:DRAIN_REFILL_OIL_BF", "Action",
                                 "Drain and refill lube oil (ISO VG 100)",
                                 maintenance_type="corrective",
                                 estimated_hours=3.0)
        _edge(G, fm_oil_cont, act_change_filter, "RESOLVED_BY")
        _edge(G, fm_oil_cont, act_drain_refill, "RESOLVED_BY")


# ---------------------------------------------------------------------------
# CENTRIFUGAL PUMP
# ---------------------------------------------------------------------------

def _build_centrifugal_pump(G: nx.DiGraph) -> None:
    fam = _node(G, "FAM:CENT_PUMP", "EquipmentFamily",
                "Centrifugal Pump",
                iso14224_class="rotating.centrifugal_pump")

    for uid, label in [
        ("UNIT:PUMP-CW-01", "Cooling Water Pump 1"),
        ("UNIT:PUMP-CW-02", "Cooling Water Pump 2"),
        ("UNIT:PUMP-PW-03", "Process Water Pump 3"),
    ]:
        unit = _node(G, uid, "EquipmentUnit", label,
                     criticality="high")
        _edge(G, fam, unit, "HAS_UNIT")

        ss_seal = _node(G, f"{uid}:SS:SEAL", "Subsystem",
                        "Mechanical Seal Assembly", unit_ref=uid)
        ss_brg = _node(G, f"{uid}:SS:BEARING", "Subsystem",
                       "Pump Bearing Set", unit_ref=uid)
        ss_imp = _node(G, f"{uid}:SS:IMPELLER", "Subsystem",
                       "Impeller Assembly", unit_ref=uid)
        _edge(G, unit, ss_seal, "HAS_SUBSYSTEM")
        _edge(G, unit, ss_brg, "HAS_SUBSYSTEM")
        _edge(G, unit, ss_imp, "HAS_SUBSYSTEM")

        # Seal components
        comp_seal_face = _node(G, f"{uid}:COMP:SEAL_FACE", "Component",
                               "Mechanical Seal Face", unit_ref=uid)
        comp_seal_flush = _node(G, f"{uid}:COMP:SEAL_FLUSH", "Component",
                                "Seal Flush Piping", unit_ref=uid)
        _edge(G, ss_seal, comp_seal_face, "HAS_COMPONENT")
        _edge(G, ss_seal, comp_seal_flush, "HAS_COMPONENT")

        # FM: Seal leakage
        fm_seal_leak = _node(G, f"{uid}:FM:PMP-SEAL-001", "FailureMode",
                             "Mechanical Seal Leakage",
                             fault_code="PMP-SEAL-001", severity="high",
                             iso14224_code="LEK", mtbf_days=480)
        _edge(G, comp_seal_face, fm_seal_leak, "CAN_FAIL_AS")

        rc_seal_wear = _node(G, "RC:SEAL_FACE_WEAR", "RootCause",
                             "Seal face wear beyond 0.5 mm flatness limit")
        rc_dry_run = _node(G, "RC:DRY_RUNNING", "RootCause",
                           "Dry running episode (cavitation / air ingestion)")
        _edge(G, fm_seal_leak, rc_seal_wear, "CAUSED_BY")
        _edge(G, fm_seal_leak, rc_dry_run, "CAUSED_BY")

        eff_leak = _node(G, "EFF:FLUID_LEAKAGE", "Effect",
                         "Process fluid leakage to environment",
                         severity="high",
                         impact="Safety hazard, process fluid loss")
        _edge(G, fm_seal_leak, eff_leak, "LEADS_TO")

        act_replace_seal = _node(G, "ACT:REPLACE_MECH_SEAL", "Action",
                                 "Replace mechanical seal per SOP-PMP-SEAL-02",
                                 maintenance_type="corrective",
                                 estimated_hours=6.0,
                                 part_ref="SEAL-MECH-CW-01")
        _edge(G, fm_seal_leak, act_replace_seal, "RESOLVED_BY")

        # FM: Cavitation
        comp_impeller = _node(G, f"{uid}:COMP:IMPELLER", "Component",
                              "Pump Impeller", unit_ref=uid)
        comp_strainer = _node(G, f"{uid}:COMP:SUCTION_STRAINER", "Component",
                              "Suction Strainer", unit_ref=uid)
        _edge(G, ss_imp, comp_impeller, "HAS_COMPONENT")
        _edge(G, ss_imp, comp_strainer, "HAS_COMPONENT")

        fm_cav = _node(G, f"{uid}:FM:PMP-CAV-002", "FailureMode",
                       "Cavitation",
                       fault_code="PMP-CAV-002", severity="high",
                       iso14224_code="CAV", mtbf_days=300)
        _edge(G, comp_impeller, fm_cav, "CAN_FAIL_AS")

        rc_npsh = _node(G, "RC:NPSH_INSUFFICIENT", "RootCause",
                        "NPSH available < NPSH required")
        rc_blocked_strainer = _node(G, "RC:BLOCKED_SUCTION_STRAINER", "RootCause",
                                    "Suction strainer blocked (dP > 0.3 bar)")
        _edge(G, fm_cav, rc_npsh, "CAUSED_BY")
        _edge(G, fm_cav, rc_blocked_strainer, "CAUSED_BY")

        eff_impeller_pit = _node(G, "EFF:IMPELLER_PITTING", "Effect",
                                 "Impeller vane pitting and material loss",
                                 severity="high",
                                 impact="Reduced pump efficiency, eventual failure")
        _edge(G, fm_cav, eff_impeller_pit, "LEADS_TO")

        act_clean_strainer = _node(G, "ACT:CLEAN_SUCTION_STRAINER", "Action",
                                   "Clean suction strainer per SOP-PMP-SUMP-01",
                                   maintenance_type="corrective",
                                   estimated_hours=2.0)
        _edge(G, fm_cav, act_clean_strainer, "RESOLVED_BY")

        # FM: Bearing fatigue
        comp_de_bearing = _node(G, f"{uid}:COMP:DE_BEARING", "Component",
                                "Drive-End Bearing", unit_ref=uid)
        comp_nde_bearing = _node(G, f"{uid}:COMP:NDE_BEARING", "Component",
                                 "Non-Drive-End Bearing", unit_ref=uid)
        _edge(G, ss_brg, comp_de_bearing, "HAS_COMPONENT")
        _edge(G, ss_brg, comp_nde_bearing, "HAS_COMPONENT")

        fm_brg_fat = _node(G, f"{uid}:FM:PMP-BRG-003", "FailureMode",
                           "Bearing Fatigue Failure",
                           fault_code="PMP-BRG-003", severity="critical",
                           iso14224_code="FAT", mtbf_days=900)
        _edge(G, comp_de_bearing, fm_brg_fat, "CAN_FAIL_AS")

        rc_l10_exceeded = _node(G, "RC:L10_LIFE_EXCEEDED", "RootCause",
                                "Bearing L10 life exceeded (>25,000 operating hours)")
        _edge(G, fm_brg_fat, rc_l10_exceeded, "CAUSED_BY")

        eff_pump_trip = _node(G, "EFF:PUMP_UNPLANNED_TRIP", "Effect",
                              "Unplanned pump shutdown",
                              severity="critical",
                              impact="Loss of cooling water supply to critical equipment")
        _edge(G, fm_brg_fat, eff_pump_trip, "LEADS_TO")

        act_replace_both_brg = _node(G, "ACT:REPLACE_PUMP_BEARINGS", "Action",
                                     "Replace both DE+NDE bearings simultaneously",
                                     maintenance_type="corrective",
                                     estimated_hours=8.0,
                                     part_ref="BRG-SKF-6207")
        _edge(G, fm_brg_fat, act_replace_both_brg, "RESOLVED_BY")


# ---------------------------------------------------------------------------
# ROLLER CONVEYOR BEARING
# ---------------------------------------------------------------------------

def _build_roller_conveyor_bearing(G: nx.DiGraph) -> None:
    fam = _node(G, "FAM:ROLLER_BRG", "EquipmentFamily",
                "Roller/Conveyor Bearing",
                iso14224_class="rotating.rolling_element_bearing")

    for uid, label in [
        ("UNIT:BRG-HRM-01", "Hot Rolling Mill Bearing 1"),
        ("UNIT:BRG-HRM-02", "Hot Rolling Mill Bearing 2"),
        ("UNIT:BRG-CVR-03", "Conveyor Bearing 3"),
    ]:
        unit = _node(G, uid, "EquipmentUnit", label, criticality="high")
        _edge(G, fam, unit, "HAS_UNIT")

        ss_brg_asm = _node(G, f"{uid}:SS:BRG_ASM", "Subsystem",
                           "Bearing Assembly", unit_ref=uid)
        _edge(G, unit, ss_brg_asm, "HAS_SUBSYSTEM")

        comp_inner_race = _node(G, f"{uid}:COMP:INNER_RACE", "Component",
                                "Inner Race", unit_ref=uid)
        comp_outer_race = _node(G, f"{uid}:COMP:OUTER_RACE", "Component",
                                "Outer Race", unit_ref=uid)
        comp_rolling_el = _node(G, f"{uid}:COMP:ROLLING_ELEMENTS", "Component",
                                "Rolling Elements", unit_ref=uid)
        comp_cage = _node(G, f"{uid}:COMP:CAGE", "Component",
                          "Cage", unit_ref=uid)
        _edge(G, ss_brg_asm, comp_inner_race, "HAS_COMPONENT")
        _edge(G, ss_brg_asm, comp_outer_race, "HAS_COMPONENT")
        _edge(G, ss_brg_asm, comp_rolling_el, "HAS_COMPONENT")
        _edge(G, ss_brg_asm, comp_cage, "HAS_COMPONENT")

        # FM: Spalling
        fm_spall = _node(G, f"{uid}:FM:BRG-SPALL-001", "FailureMode",
                         "Inner Race Spalling",
                         fault_code="BRG-SPALL-001", severity="critical",
                         iso14224_code="SPL", mtbf_days=1200)
        _edge(G, comp_inner_race, fm_spall, "CAN_FAIL_AS")

        rc_fatigue = _node(G, "RC:CONTACT_FATIGUE", "RootCause",
                           "Subsurface fatigue from cyclic rolling contact stress")
        rc_lube_film = _node(G, "RC:LUBE_FILM_BREAKDOWN", "RootCause",
                             "Lubricant film breakdown at high temperature")
        _edge(G, fm_spall, rc_fatigue, "CAUSED_BY")
        _edge(G, fm_spall, rc_lube_film, "CAUSED_BY")

        eff_spall = _node(G, "EFF:CONVEYOR_SHUTDOWN", "Effect",
                          "Conveyor/roller table shutdown required",
                          severity="critical",
                          impact="Strip production halt, cobble risk")
        _edge(G, fm_spall, eff_spall, "LEADS_TO")

        act_replace_srb = _node(G, "ACT:REPLACE_SRB_22320", "Action",
                                "Replace spherical roller bearing SRB-22320-E",
                                maintenance_type="corrective",
                                estimated_hours=12.0,
                                part_ref="BRG-SRB-22320-E")
        _edge(G, fm_spall, act_replace_srb, "RESOLVED_BY")

        # FM: Lube starvation
        fm_lube_starv = _node(G, f"{uid}:FM:BRG-LUB-002", "FailureMode",
                              "Lubricant Starvation",
                              fault_code="BRG-LUB-002", severity="high",
                              iso14224_code="LUB", mtbf_days=365)
        _edge(G, comp_cage, fm_lube_starv, "CAN_FAIL_AS")

        rc_missed_relube = _node(G, "RC:MISSED_RELUBRICATION", "RootCause",
                                 "Relubrication interval exceeded by >20%")
        _edge(G, fm_lube_starv, rc_missed_relube, "CAUSED_BY")

        eff_lube_heat = _node(G, "EFF:OVERHEATING_DRY_BEARING", "Effect",
                              "Dry bearing overheating → seizure",
                              severity="high")
        _edge(G, fm_lube_starv, eff_lube_heat, "LEADS_TO")

        act_emergency_grease = _node(G, "ACT:EMERGENCY_GREASE_BEARING", "Action",
                                     "Apply emergency grease (Shell Alvania R3, 45g)",
                                     maintenance_type="emergency",
                                     estimated_hours=0.5,
                                     part_ref="LUB-SHELL-ALVANIA-R3")
        _edge(G, fm_lube_starv, act_emergency_grease, "RESOLVED_BY")

        # FM: False brinelling
        fm_brln = _node(G, f"{uid}:FM:BRG-BRLN-003", "FailureMode",
                        "False Brinelling",
                        fault_code="BRG-BRLN-003", severity="medium",
                        iso14224_code="WEA", mtbf_days=1800)
        _edge(G, comp_rolling_el, fm_brln, "CAN_FAIL_AS")

        rc_standstill_vib = _node(G, "RC:STANDSTILL_VIBRATION", "RootCause",
                                  "External vibration during plant shutdown")
        _edge(G, fm_brln, rc_standstill_vib, "CAUSED_BY")

        eff_pitting = _node(G, "EFF:RACEWAY_INDENTATION", "Effect",
                            "Equally-spaced indentations on raceway",
                            severity="medium")
        _edge(G, fm_brln, eff_pitting, "LEADS_TO")

        act_vci = _node(G, "ACT:APPLY_VCI_CORROSION_INHIBITOR", "Action",
                        "Apply VCI corrosion inhibitor before extended shutdown",
                        maintenance_type="preventive",
                        estimated_hours=1.0,
                        part_ref="COMP-VCI-001")
        _edge(G, fm_brln, act_vci, "RESOLVED_BY")


# ---------------------------------------------------------------------------
# HYDRAULIC POWER UNIT
# ---------------------------------------------------------------------------

def _build_hydraulic_power_unit(G: nx.DiGraph) -> None:
    fam = _node(G, "FAM:HPU", "EquipmentFamily",
                "Hydraulic Power Unit",
                iso14224_class="fluid_system.hydraulic_unit")

    for uid, label in [
        ("UNIT:HPU-RM-01", "Rolling Mill HPU 1"),
        ("UNIT:HPU-RM-02", "Rolling Mill HPU 2"),
        ("UNIT:HPU-LDL-03", "Ladle Tilter HPU 3"),
    ]:
        unit = _node(G, uid, "EquipmentUnit", label, criticality="critical")
        _edge(G, fam, unit, "HAS_UNIT")

        ss_pump = _node(G, f"{uid}:SS:HYD_PUMP", "Subsystem",
                        "Hydraulic Pump", unit_ref=uid)
        ss_oil_cond = _node(G, f"{uid}:SS:OIL_COND", "Subsystem",
                            "Oil Conditioning System", unit_ref=uid)
        _edge(G, unit, ss_pump, "HAS_SUBSYSTEM")
        _edge(G, unit, ss_oil_cond, "HAS_SUBSYSTEM")

        comp_piston_barrel = _node(G, f"{uid}:COMP:PISTON_BARREL", "Component",
                                   "Piston Barrel", unit_ref=uid)
        comp_swashplate = _node(G, f"{uid}:COMP:SWASHPLATE", "Component",
                                "Swashplate", unit_ref=uid)
        comp_prv = _node(G, f"{uid}:COMP:PRV", "Component",
                         "Pressure Relief Valve", unit_ref=uid)
        comp_filter = _node(G, f"{uid}:COMP:HYD_FILTER", "Component",
                            "Return-Line Filter", unit_ref=uid)
        comp_reservoir = _node(G, f"{uid}:COMP:RESERVOIR", "Component",
                               "Oil Reservoir", unit_ref=uid)
        _edge(G, ss_pump, comp_piston_barrel, "HAS_COMPONENT")
        _edge(G, ss_pump, comp_swashplate, "HAS_COMPONENT")
        _edge(G, ss_pump, comp_prv, "HAS_COMPONENT")
        _edge(G, ss_oil_cond, comp_filter, "HAS_COMPONENT")
        _edge(G, ss_oil_cond, comp_reservoir, "HAS_COMPONENT")

        # FM: Internal leakage
        fm_int_leak = _node(G, f"{uid}:FM:HPU-LEAK-001", "FailureMode",
                            "Pump Internal Leakage (Swashplate Wear)",
                            fault_code="HPU-LEAK-001", severity="high",
                            iso14224_code="INT-LEAK", mtbf_days=1080)
        _edge(G, comp_swashplate, fm_int_leak, "CAN_FAIL_AS")

        rc_swash_wear = _node(G, "RC:SWASHPLATE_CLEARANCE", "RootCause",
                              "Swashplate/piston barrel clearance >0.02 mm")
        rc_oil_cont_hpu = _node(G, "RC:OIL_CONTAMINATION_HPU", "RootCause",
                                "Oil contamination NAS Class >8")
        _edge(G, fm_int_leak, rc_swash_wear, "CAUSED_BY")
        _edge(G, fm_int_leak, rc_oil_cont_hpu, "CAUSED_BY")

        eff_press_drop = _node(G, "EFF:SYSTEM_PRESSURE_DROP", "Effect",
                               "System pressure drops below minimum (240 bar)",
                               severity="high",
                               impact="Actuator stall, production stop")
        _edge(G, fm_int_leak, eff_press_drop, "LEADS_TO")

        act_measure_drain = _node(G, "ACT:MEASURE_CASE_DRAIN_FLOW", "Action",
                                  "Measure pump case drain flow (alarm if >5 L/min)",
                                  maintenance_type="predictive",
                                  estimated_hours=1.0)
        act_overhaul_pump = _node(G, "ACT:OVERHAUL_PISTON_PUMP", "Action",
                                  "Overhaul pump — replace piston/barrel set",
                                  maintenance_type="corrective",
                                  estimated_hours=24.0,
                                  part_ref="KIT-HPU-RBL-001")
        _edge(G, fm_int_leak, act_measure_drain, "RESOLVED_BY")
        _edge(G, fm_int_leak, act_overhaul_pump, "RESOLVED_BY")

        # FM: PRV stuck open
        fm_prv = _node(G, f"{uid}:FM:HPU-PRV-002", "FailureMode",
                       "Pressure Relief Valve Stuck Open",
                       fault_code="HPU-PRV-002", severity="critical",
                       iso14224_code="PRV-FAIL", mtbf_days=720)
        _edge(G, comp_prv, fm_prv, "CAN_FAIL_AS")

        rc_prv_dirt = _node(G, "RC:PRV_CONTAMINATION_PARTICLE", "RootCause",
                            "Contamination particle lodged in valve seat")
        rc_prv_spring = _node(G, "RC:PRV_SPRING_FATIGUE", "RootCause",
                              "PRV spring fatigue (set pressure drift >15%)")
        _edge(G, fm_prv, rc_prv_dirt, "CAUSED_BY")
        _edge(G, fm_prv, rc_prv_spring, "CAUSED_BY")

        eff_actuator_disable = _node(G, "EFF:ALL_ACTUATORS_DISABLED", "Effect",
                                     "All downstream actuators disabled",
                                     severity="critical",
                                     impact="Mill production complete stop")
        _edge(G, fm_prv, eff_actuator_disable, "LEADS_TO")

        act_isolate_hpu = _node(G, "ACT:ISOLATE_HPU_EMERGENCY", "Action",
                                "EMERGENCY: Isolate HPU, notify shift supervisor",
                                maintenance_type="emergency",
                                safety_critical=True)
        act_replace_prv = _node(G, "ACT:REPLACE_PRV_280B", "Action",
                                "Replace relief valve per SOP-HPU-PRV-02",
                                maintenance_type="corrective",
                                estimated_hours=4.0,
                                part_ref="VLV-PRV-HPU-280B")
        _edge(G, fm_prv, act_isolate_hpu, "RESOLVED_BY")
        _edge(G, fm_prv, act_replace_prv, "RESOLVED_BY")

        # FM: Oil contamination
        fm_oil_cont = _node(G, f"{uid}:FM:HPU-OIL-003", "FailureMode",
                            "Oil Contamination — High Particle Count",
                            fault_code="HPU-OIL-003", severity="medium",
                            iso14224_code="CON", mtbf_days=270)
        _edge(G, comp_filter, fm_oil_cont, "CAN_FAIL_AS")

        rc_worn_pump_metal = _node(G, "RC:PUMP_WEAR_PARTICLES", "RootCause",
                                   "Worn pump generating metallic particles")
        rc_breather_bypass = _node(G, "RC:BREATHER_BYPASS", "RootCause",
                                   "Breather filter bypassing (clogged element)")
        _edge(G, fm_oil_cont, rc_worn_pump_metal, "CAUSED_BY")
        _edge(G, fm_oil_cont, rc_breather_bypass, "CAUSED_BY")

        eff_servo_stick = _node(G, "EFF:SERVO_VALVE_STICKING", "Effect",
                                "Servo valve spool sticking — erratic positioning",
                                severity="high")
        _edge(G, fm_oil_cont, eff_servo_stick, "LEADS_TO")

        act_kidney_filter = _node(G, "ACT:INSTALL_KIDNEY_LOOP", "Action",
                                  "Install offline kidney-loop filter (10 micron, 24h)",
                                  maintenance_type="corrective",
                                  estimated_hours=2.0)
        _edge(G, fm_oil_cont, act_kidney_filter, "RESOLVED_BY")


# ---------------------------------------------------------------------------
# HOT STRIP MILL CONVEYOR
# ---------------------------------------------------------------------------

def _build_hot_strip_mill_conveyor(G: nx.DiGraph) -> None:
    fam = _node(G, "FAM:HSM_CONV", "EquipmentFamily",
                "Hot Strip Mill Conveyor",
                iso14224_class="mechanical.belt_conveyor_roller_table")

    for uid, label in [
        ("UNIT:CONV-ROT-01", "Run-Out Table Conveyor 1"),
        ("UNIT:CONV-ROT-02", "Run-Out Table Conveyor 2"),
        ("UNIT:CONV-FBL-04", "Flying Shear Feed Conveyor 4"),
    ]:
        unit = _node(G, uid, "EquipmentUnit", label, criticality="high")
        _edge(G, fam, unit, "HAS_UNIT")

        ss_drive = _node(G, f"{uid}:SS:DRIVE_ROLLER", "Subsystem",
                         "Drive Roller Assembly", unit_ref=uid)
        ss_water = _node(G, f"{uid}:SS:WATER_COOLING", "Subsystem",
                         "Water Cooling System", unit_ref=uid)
        _edge(G, unit, ss_drive, "HAS_SUBSYSTEM")
        _edge(G, unit, ss_water, "HAS_SUBSYSTEM")

        comp_barrel = _node(G, f"{uid}:COMP:ROLLER_BARREL", "Component",
                            "Roller Barrel", unit_ref=uid)
        comp_coupling = _node(G, f"{uid}:COMP:DRIVE_COUPLING", "Component",
                              "Drive Coupling", unit_ref=uid)
        comp_nozzles = _node(G, f"{uid}:COMP:SPRAY_NOZZLES", "Component",
                             "Spray Nozzles", unit_ref=uid)
        comp_spray_pump = _node(G, f"{uid}:COMP:SPRAY_PUMP", "Component",
                                "Spray Water Pump", unit_ref=uid)
        _edge(G, ss_drive, comp_barrel, "HAS_COMPONENT")
        _edge(G, ss_drive, comp_coupling, "HAS_COMPONENT")
        _edge(G, ss_water, comp_nozzles, "HAS_COMPONENT")
        _edge(G, ss_water, comp_spray_pump, "HAS_COMPONENT")

        # FM: Roller barrel spalling
        fm_barrel_spall = _node(G, f"{uid}:FM:CVR-SPALL-001", "FailureMode",
                                "Roller Barrel Surface Spalling",
                                fault_code="CVR-SPALL-001", severity="high",
                                iso14224_code="SPL", mtbf_days=450)
        _edge(G, comp_barrel, fm_barrel_spall, "CAN_FAIL_AS")

        rc_thermal_fatigue = _node(G, "RC:THERMAL_FATIGUE_ROLLER", "RootCause",
                                   "Thermal fatigue from repeated hot slab contact")
        rc_insufficient_cooling = _node(G, "RC:INSUFFICIENT_ROLLER_COOLING", "RootCause",
                                        "Inadequate water cooling flow on roller surface")
        _edge(G, fm_barrel_spall, rc_thermal_fatigue, "CAUSED_BY")
        _edge(G, fm_barrel_spall, rc_insufficient_cooling, "CAUSED_BY")

        eff_strip_defects = _node(G, "EFF:STRIP_SURFACE_DEFECTS", "Effect",
                                  "Strip surface quality defects (marks at roller pitch)",
                                  severity="high",
                                  impact="Product rejection, customer complaints")
        _edge(G, fm_barrel_spall, eff_strip_defects, "LEADS_TO")

        act_resurface = _node(G, "ACT:RESURFACE_ROLLER_BARREL", "Action",
                              "Remove and resurface roller (turning to minimum dia.)",
                              maintenance_type="corrective",
                              estimated_hours=20.0,
                              min_diameter_mm=320)
        act_replace_roller = _node(G, "ACT:REPLACE_ROLLER_BARREL", "Action",
                                   "Replace roller barrel if OD < 320 mm",
                                   maintenance_type="corrective",
                                   estimated_hours=12.0,
                                   part_ref="ROLL-ROT-001")
        _edge(G, fm_barrel_spall, act_resurface, "RESOLVED_BY")
        _edge(G, fm_barrel_spall, act_replace_roller, "RESOLVED_BY")

        # FM: Coupling failure
        fm_coup_fail = _node(G, f"{uid}:FM:CVR-COUP-002", "FailureMode",
                             "Drive Coupling Failure",
                             fault_code="CVR-COUP-002", severity="critical",
                             iso14224_code="FRC-FAIL", mtbf_days=540)
        _edge(G, comp_coupling, fm_coup_fail, "CAN_FAIL_AS")

        rc_torque_overload = _node(G, "RC:TORQUE_OVERLOAD_COBBLE", "RootCause",
                                   "Torque overload during strip cobble / jam event")
        rc_coupling_aged = _node(G, "RC:COUPLING_RUBBER_AGED", "RootCause",
                                 "Coupling rubber element aged beyond 3-year service")
        _edge(G, fm_coup_fail, rc_torque_overload, "CAUSED_BY")
        _edge(G, fm_coup_fail, rc_coupling_aged, "CAUSED_BY")

        eff_conv_stop = _node(G, "EFF:CONVEYOR_STRIP_STOP", "Effect",
                              "Conveyor strip jam — production stop",
                              severity="critical",
                              impact="Strip jam hazard, fire risk from hot slab stopping")
        _edge(G, fm_coup_fail, eff_conv_stop, "LEADS_TO")

        act_stop_conv = _node(G, "ACT:STOP_CONVEYOR_EMERGENCY", "Action",
                              "STOP conveyor drive immediately — strip jam hazard",
                              maintenance_type="emergency",
                              safety_critical=True)
        act_replace_spider = _node(G, "ACT:REPLACE_COUPLING_SPIDER", "Action",
                                   "Replace coupling spider element per SOP-CONV-COUP-01",
                                   maintenance_type="corrective",
                                   estimated_hours=4.0,
                                   part_ref="COUP-CONV-SPIDER")
        _edge(G, fm_coup_fail, act_stop_conv, "RESOLVED_BY")
        _edge(G, fm_coup_fail, act_replace_spider, "RESOLVED_BY")

        # FM: Nozzle blockage
        fm_nozzle = _node(G, f"{uid}:FM:CVR-NZL-003", "FailureMode",
                          "Spray Nozzle Blockage",
                          fault_code="CVR-NZL-003", severity="medium",
                          iso14224_code="BLK", mtbf_days=90)
        _edge(G, comp_nozzles, fm_nozzle, "CAN_FAIL_AS")

        rc_scale = _node(G, "RC:SCALE_PRECIPITATION", "RootCause",
                         "Scale precipitation in process water (hardness >200 ppm CaCO3)")
        _edge(G, fm_nozzle, rc_scale, "CAUSED_BY")

        eff_hot_spots = _node(G, "EFF:UNEVEN_STRIP_COOLING", "Effect",
                              "Uneven strip cooling — hot spots on finished strip",
                              severity="medium",
                              impact="Strip flatness and property non-conformance")
        _edge(G, fm_nozzle, eff_hot_spots, "LEADS_TO")

        act_clean_nozzles = _node(G, "ACT:CLEAN_SPRAY_NOZZLES", "Action",
                                  "Clean nozzles with descalant per SOP-CONV-NZL-01",
                                  maintenance_type="preventive",
                                  estimated_hours=4.0)
        act_replace_nozzles = _node(G, "ACT:REPLACE_SPRAY_NOZZLES", "Action",
                                    "Replace nozzles if erosion >20% orifice diameter",
                                    maintenance_type="corrective",
                                    estimated_hours=2.0,
                                    part_ref="NZL-CONV-SS316")
        _edge(G, fm_nozzle, act_clean_nozzles, "RESOLVED_BY")
        _edge(G, fm_nozzle, act_replace_nozzles, "RESOLVED_BY")


# ---------------------------------------------------------------------------
# SHARED SOP REFERENCE NODES
# ---------------------------------------------------------------------------

def _build_shared_sop_nodes(G: nx.DiGraph) -> None:
    sops = [
        ("SOP:BF-AF-07", "SOP-BF-AF-07", "BF Fan bearing inspection and isolation", "blast_furnace_fan"),
        ("SOP:BF-AF-11", "SOP-BF-AF-11", "BF Fan laser alignment procedure", "blast_furnace_fan"),
        ("SOP:BF-LUB-03", "SOP-BF-LUB-03", "BF Fan lubrication oil change", "blast_furnace_fan"),
        ("SOP:PMP-SEAL-02", "SOP-PMP-SEAL-02", "Centrifugal pump mechanical seal replacement", "centrifugal_pump"),
        ("SOP:PMP-SUMP-01", "SOP-PMP-SUMP-01", "Pump suction strainer cleaning", "centrifugal_pump"),
        ("SOP:PMP-BRG-05", "SOP-PMP-BRG-05", "Pump bearing replacement and greasing", "centrifugal_pump"),
        ("SOP:BRG-SRB-03", "SOP-BRG-SRB-03", "Spherical roller bearing replacement on roller table", "roller_conveyor_bearing"),
        ("SOP:BRG-LUBE-01", "SOP-BRG-LUBE-01", "Bearing lubrication and auto-lube system check", "roller_conveyor_bearing"),
        ("SOP:HPU-PMP-04", "SOP-HPU-PMP-04", "Hydraulic pump piston/barrel replacement", "hydraulic_power_unit"),
        ("SOP:HPU-PRV-02", "SOP-HPU-PRV-02", "HPU pressure relief valve replacement", "hydraulic_power_unit"),
        ("SOP:CONV-COUP-01", "SOP-CONV-COUP-01", "Conveyor coupling spider replacement", "hot_strip_mill_conveyor"),
        ("SOP:CONV-NZL-01", "SOP-CONV-NZL-01", "Conveyor spray nozzle cleaning and replacement", "hot_strip_mill_conveyor"),
        ("SOP:CONV-WTR-02", "SOP-CONV-WTR-02", "Conveyor water cooling circuit check", "hot_strip_mill_conveyor"),
        ("SOP:ELEC-LOTO-01", "SOP-ELEC-LOTO-01", "Electrical LOTO procedure (all equipment)", "all"),
    ]

    for node_id, sop_num, title, equipment_class in sops:
        _node(G, node_id, "SOPReference", sop_num,
              sop_number=sop_num, title=title, equipment_class=equipment_class)

    # Link actions to SOPs
    sop_links = [
        ("ACT:ISOLATE_BF_FAN", "SOP:BF-AF-07"),
        ("ACT:REPLACE_BRG_SKF6310", "SOP:BF-AF-07"),
        ("ACT:LASER_ALIGNMENT", "SOP:BF-AF-11"),
        ("ACT:CHANGE_OIL_FILTER_BF", "SOP:BF-LUB-03"),
        ("ACT:DRAIN_REFILL_OIL_BF", "SOP:BF-LUB-03"),
        ("ACT:REPLACE_MECH_SEAL", "SOP:PMP-SEAL-02"),
        ("ACT:CLEAN_SUCTION_STRAINER", "SOP:PMP-SUMP-01"),
        ("ACT:REPLACE_PUMP_BEARINGS", "SOP:PMP-BRG-05"),
        ("ACT:REPLACE_SRB_22320", "SOP:BRG-SRB-03"),
        ("ACT:EMERGENCY_GREASE_BEARING", "SOP:BRG-LUBE-01"),
        ("ACT:OVERHAUL_PISTON_PUMP", "SOP:HPU-PMP-04"),
        ("ACT:REPLACE_PRV_280B", "SOP:HPU-PRV-02"),
        ("ACT:REPLACE_COUPLING_SPIDER", "SOP:CONV-COUP-01"),
        ("ACT:CLEAN_SPRAY_NOZZLES", "SOP:CONV-NZL-01"),
        ("ACT:REPLACE_SPRAY_NOZZLES", "SOP:CONV-NZL-01"),
    ]
    for act_id, sop_id in sop_links:
        if act_id in G and sop_id in G:
            _edge(G, act_id, sop_id, "FOLLOWS_SOP")


# ---------------------------------------------------------------------------
# SPARE PART NODES
# ---------------------------------------------------------------------------

def _build_spare_part_nodes(G: nx.DiGraph) -> None:
    parts = [
        ("PART:BRG-SKF-6310-2RS1", "SKF Deep Groove Ball Bearing 6310-2RS1",
         0, 4, 14, "critical",
         "OUT OF STOCK — 14-day lead time. Critical for BF fan bearing replacement."),
        ("PART:BRG-SKF-6207", "SKF Deep Groove Ball Bearing 6207",
         8, 4, 3, "standard", None),
        ("PART:BRG-SRB-22320-E", "FAG Spherical Roller Bearing 22320-E",
         2, 6, 7, "critical", "Low stock — below minimum."),
        ("PART:SEAL-MECH-CW-01", "Burgmann M7N Mechanical Seal DN50",
         3, 2, 5, "critical", None),
        ("PART:SEAL-BF-001", "Labyrinthe Seal Assembly BF Fan Type-B",
         1, 2, 21, "critical", "Low stock. Long lead time 21 days."),
        ("PART:FILT-BF-010", "Oil Filter Element BF Fan (25 micron)",
         12, 6, 2, "standard", None),
        ("PART:FILT-HPU-010", "Hydraulic Return-Line Filter (10 micron)",
         8, 4, 3, "standard", None),
        ("PART:LUB-SHELL-ALVANIA-R3", "Shell Alvania R3 Grease 50kg",
         4, 2, 2, "standard", None),
        ("PART:OIL-ISO46-1000L", "Hydraulic Oil ISO VG 46 (1000L IBC)",
         3, 2, 4, "standard", None),
        ("PART:KIT-HPU-RBL-001", "Rexroth A10V100 Pump Rebuild Kit",
         0, 1, 14, "critical",
         "OUT OF STOCK — 14-day lead time. Critical for HPU pump overhaul."),
        ("PART:COUP-CONV-SPIDER", "Jaw Coupling Spider (Polyurethane 94A)",
         20, 10, 1, "standard", None),
        ("PART:ROLL-ROT-001", "Run-Out Table Drive Roller Barrel 340mm OD",
         1, 3, 14, "critical", "Low stock. 14-day lead time."),
        ("PART:NZL-CONV-SS316", "Spray Nozzle SS316 Full-Cone (per unit)",
         150, 50, 2, "standard", None),
        ("PART:VLV-PRV-HPU-280B", "Pressure Relief Valve 280 bar (Parker)",
         2, 2, 5, "critical", None),
        ("PART:COMP-VCI-001", "VCI Corrosion Inhibitor Compound",
         20, 5, 2, "standard", None),
    ]

    for (part_id, part_name, stock_qty, min_stock, lead_days,
         criticality, note) in parts:
        attrs = dict(
            part_name=part_name,
            stock_qty=stock_qty,
            min_stock_qty=min_stock,
            lead_time_days=lead_days,
            criticality_override=criticality,
        )
        if note:
            attrs["procurement_note"] = note
        _node(G, part_id, "SparePart", part_name, **attrs)

    # Link actions to spare parts
    part_links = [
        ("ACT:REPLACE_BRG_SKF6310",    "PART:BRG-SKF-6310-2RS1"),
        ("ACT:ISOLATE_BF_FAN",         "PART:SEAL-BF-001"),
        ("ACT:REPLACE_MECH_SEAL",      "PART:SEAL-MECH-CW-01"),
        ("ACT:REPLACE_PUMP_BEARINGS",  "PART:BRG-SKF-6207"),
        ("ACT:REPLACE_SRB_22320",      "PART:BRG-SRB-22320-E"),
        ("ACT:EMERGENCY_GREASE_BEARING", "PART:LUB-SHELL-ALVANIA-R3"),
        ("ACT:OVERHAUL_PISTON_PUMP",   "PART:KIT-HPU-RBL-001"),
        ("ACT:REPLACE_PRV_280B",       "PART:VLV-PRV-HPU-280B"),
        ("ACT:REPLACE_COUPLING_SPIDER", "PART:COUP-CONV-SPIDER"),
        ("ACT:REPLACE_ROLLER_BARREL",  "PART:ROLL-ROT-001"),
        ("ACT:REPLACE_SPRAY_NOZZLES",  "PART:NZL-CONV-SS316"),
        ("ACT:APPLY_VCI_CORROSION_INHIBITOR", "PART:COMP-VCI-001"),
    ]
    for act_id, part_id in part_links:
        if act_id in G and part_id in G:
            _edge(G, act_id, part_id, "REQUIRES_PART")


# ---------------------------------------------------------------------------
# SENSOR SIGNAL NODES (detected-by links)
# ---------------------------------------------------------------------------

def _build_sensor_nodes(G: nx.DiGraph) -> None:
    sensors = [
        ("SENSOR:TEMP_BEARING", "Bearing Temperature Sensor", "temperature_c",
         "OHM-type PT100, 4-20mA output"),
        ("SENSOR:VIB_CASING", "Casing Vibration Sensor", "vibration_mm_s",
         "Piezoelectric accelerometer, ICP-type"),
        ("SENSOR:PRESSURE_DISCHARGE", "Discharge Pressure Transducer", "pressure_bar",
         "Piezoresistive, 4-20mA"),
        ("SENSOR:RPM_PROXIMITY", "Shaft Speed Proximity Sensor", "rpm",
         "Inductive proximity switch, 24V DC"),
        ("SENSOR:CURRENT_CT", "Motor Current Transformer", "current_a",
         "Clip-on CT, 4-20mA output"),
    ]
    for sid, label, measured_variable, technology in sensors:
        _node(G, sid, "Sensor", label,
              measured_variable=measured_variable, technology=technology)

    # DETECTED_BY links for key failure modes (shared nodes, not per-unit)
    detect_links = [
        # FailureMode node pattern → sensor
        ("FM:BF-BRG-002", "SENSOR:TEMP_BEARING"),
        ("FM:BF-BRG-002", "SENSOR:VIB_CASING"),
        ("FM:BF-ERO-001", "SENSOR:PRESSURE_DISCHARGE"),
        ("FM:BF-ERO-001", "SENSOR:VIB_CASING"),
        ("FM:BF-ALN-003", "SENSOR:VIB_CASING"),
        ("FM:PMP-SEAL-001", "SENSOR:TEMP_BEARING"),
        ("FM:PMP-CAV-002", "SENSOR:PRESSURE_DISCHARGE"),
        ("FM:PMP-BRG-003", "SENSOR:TEMP_BEARING"),
        ("FM:PMP-BRG-003", "SENSOR:VIB_CASING"),
        ("FM:BRG-SPALL-001", "SENSOR:TEMP_BEARING"),
        ("FM:BRG-SPALL-001", "SENSOR:VIB_CASING"),
        ("FM:BRG-LUB-002", "SENSOR:TEMP_BEARING"),
        ("FM:HPU-LEAK-001", "SENSOR:PRESSURE_DISCHARGE"),
        ("FM:HPU-PRV-002", "SENSOR:PRESSURE_DISCHARGE"),
        ("FM:CVR-COUP-002", "SENSOR:CURRENT_CT"),
    ]

    # These are global FM nodes (not per-unit), link DETECTED_BY from all matching
    for fm_suffix, sensor_id in detect_links:
        for node_id in G.nodes():
            if node_id.endswith(f":{fm_suffix}") and G.nodes[node_id].get("node_type") == "FailureMode":
                if sensor_id in G:
                    _edge(G, node_id, sensor_id, "DETECTED_BY")


# ---------------------------------------------------------------------------
# SERIALIZATION
# ---------------------------------------------------------------------------

def save_fmea_graph(G: nx.DiGraph, path: Path) -> None:
    """
    Serialize the FMEA DiGraph to JSON (NetworkX node_link_data format).
    Creates parent directories as needed.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    data = nx.node_link_data(G)
    # Add graph-level metadata
    data["graph_metadata"] = {
        "node_count": G.number_of_nodes(),
        "edge_count": G.number_of_edges(),
        "standard": G.graph.get("standard"),
        "schema_version": G.graph.get("schema_version"),
    }
    path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")


def load_fmea_graph(path: Path) -> nx.DiGraph:
    """
    Load a previously saved FMEA DiGraph from JSON.
    """
    path = Path(path)
    data = json.loads(path.read_text(encoding="utf-8"))
    return nx.node_link_graph(data, directed=True)


def get_rca_path(
    G: nx.DiGraph,
    fault_code: str,
) -> dict:
    """
    Given a fault_code string, find the FailureMode node and return
    the full RCA evidence chain: FailureMode → RootCause(s), → Effect(s),
    → Action(s), → SparePart(s), → SOPReference(s).

    Returns a dict suitable for populating a CauseChainStep list.
    """
    fm_nodes = [
        n for n, d in G.nodes(data=True)
        if d.get("node_type") == "FailureMode" and d.get("fault_code") == fault_code
    ]
    if not fm_nodes:
        return {"found": False, "fault_code": fault_code, "chain": []}

    # Use first match (deterministic for a given fault_code)
    fm_node = fm_nodes[0]
    fm_data = G.nodes[fm_node]

    _fm_label = fm_data.get("label", fm_node)
    chain: list[dict] = [{
        "node_id": fm_node,
        # CauseChainStep field names (wizard.core.schemas)
        "node_label": _fm_label,
        "edge_relation": "is_fault",
        # Legacy aliases kept for backward-compat (smoke test reads these)
        "label": _fm_label,
        "relation": "is_fault",
        "node_type": "FailureMode",
        "attributes": {k: v for k, v in fm_data.items()
                       if k not in ("label", "node_type")},
    }]

    for relation_type in ("CAUSED_BY", "LEADS_TO", "RESOLVED_BY", "DETECTED_BY"):
        for _, neighbor, edge_data in G.out_edges(fm_node, data=True):
            if edge_data.get("relation") == relation_type:
                n_data = G.nodes[neighbor]
                _nb_label = n_data.get("label", neighbor)
                chain.append({
                    "node_id": neighbor,
                    # CauseChainStep field names
                    "node_label": _nb_label,
                    "edge_relation": relation_type,
                    # Legacy aliases
                    "label": _nb_label,
                    "relation": relation_type,
                    "node_type": n_data.get("node_type", "unknown"),
                    "attributes": {k: v for k, v in n_data.items()
                                   if k not in ("label", "node_type")},
                })
                # Follow RESOLVED_BY → REQUIRES_PART and FOLLOWS_SOP
                if relation_type == "RESOLVED_BY":
                    for _, deep_nb, deep_ed in G.out_edges(neighbor, data=True):
                        if deep_ed.get("relation") in ("REQUIRES_PART", "FOLLOWS_SOP"):
                            dn_data = G.nodes[deep_nb]
                            _dn_label = dn_data.get("label", deep_nb)
                            chain.append({
                                "node_id": deep_nb,
                                # CauseChainStep field names
                                "node_label": _dn_label,
                                "edge_relation": deep_ed["relation"],
                                # Legacy aliases
                                "label": _dn_label,
                                "relation": deep_ed["relation"],
                                "node_type": dn_data.get("node_type", "unknown"),
                                "attributes": {
                                    k: v for k, v in dn_data.items()
                                    if k not in ("label", "node_type")
                                },
                            })

    return {
        "found": True,
        "fault_code": fault_code,
        "fm_node": fm_node,
        "severity": fm_data.get("severity", "unknown"),
        "chain": chain,
    }


__all__ = [
    "build_fmea_graph",
    "save_fmea_graph",
    "load_fmea_graph",
    "get_rca_path",
]
