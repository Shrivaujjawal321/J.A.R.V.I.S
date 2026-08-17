"""
wizard.knowledge.generator
===========================
Synthetic knowledge-base generator for the Maintenance Wizard.

Generates ~500 documents across 6 document types:
    - Equipment Manual sections    (~100)
    - Maintenance SOPs             (~100)
    - Maintenance Log entries      (~150)
    - Failure Analysis Reports     (~80)
    - Incident Summaries           (~40)
    - Spare Parts records          (~30)

Architecture:
    1. Ontology seed → equipment families, failure modes, error codes, sensor ranges
    2. Faker + Mimesis → deterministic structured fields (timestamps, IDs, names)
    3. Template renderer → Jinja2 skeletons produce structural document text
    4. LLM elaboration (gated behind --use-llm / USE_LLM env var)
       → fills free-text narrative fields with domain-grounded detail
    5. Noise injection → 15-20% of maintenance logs get realistic noise
    6. Dedup gate → cosine similarity < 0.85 (requires sentence-transformers)
       Falls back to hash-based dedup if sentence-transformers unavailable
    7. Entity emission → KnowledgeDocument, SparePart, MaintenanceRecord,
       FaultLog entities written to SQLite via wizard.core.db

CLI:
    python -m wizard.knowledge.generator --count 50 --seed 42
    python -m wizard.knowledge.generator --count 500 --use-llm --seed 42
    python -m wizard.knowledge.generator --count 10  # smoke-test offline mode

Output:
    data/synthetic/docs/        — individual JSON + Markdown files per document
    data/synthetic/metadata_index.json  — metadata index
    data/kg/steel_plant_fmea.json       — FMEA NetworkX graph
    data/kg/steel_plant_ontology.json   — raw ontology JSON
    wizard.db                           — entities persisted via SQLModel
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import random
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Optional

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("wizard.knowledge.generator")

# ---------------------------------------------------------------------------
# Repo-root resolution (works whether called as script or module)
# ---------------------------------------------------------------------------
_THIS_FILE = Path(__file__).resolve()
_REPO_ROOT = _THIS_FILE.parents[2]  # wizard/knowledge/generator.py → repo root

# ---------------------------------------------------------------------------
# Inline imports from wizard.core (fail-safe for smoke runs)
# ---------------------------------------------------------------------------
try:
    from wizard.core.schemas import (
        KnowledgeDocument,
        SparePart,
        MaintenanceRecord,
        FaultLog,
        ingest_entity,
        QuarantineRecord,
    )
    from wizard.core.config import settings
    from wizard.core.db import init_db, get_session, session_scope
    _HAS_CORE = True
except ImportError as _e:
    log.warning("wizard.core not importable (%s) — entity persistence disabled", _e)
    _HAS_CORE = False
    settings = None  # type: ignore[assignment]

from wizard.knowledge.ontology import ONTOLOGY, save_ontology
from wizard.knowledge.templates import TemplateType, render_template
from wizard.knowledge.fmea_graph import build_fmea_graph, save_fmea_graph

# ---------------------------------------------------------------------------
# Optional deps — graceful degradation
# ---------------------------------------------------------------------------
try:
    from faker import Faker
    _HAS_FAKER = True
except ImportError:
    log.warning("faker not installed — using fallback name/ID generators")
    _HAS_FAKER = False
    Faker = None  # type: ignore[misc,assignment]

try:
    import mimesis
    from mimesis import Generic
    _HAS_MIMESIS = True
except ImportError:
    log.warning("mimesis not installed — using faker/random fallback")
    _HAS_MIMESIS = False
    Generic = None  # type: ignore[misc,assignment]

try:
    from sentence_transformers import SentenceTransformer
    import numpy as np
    _HAS_ST = True
except ImportError:
    log.warning("sentence-transformers not available — using hash dedup fallback")
    _HAS_ST = False
    SentenceTransformer = None  # type: ignore[misc,assignment]
    np = None  # type: ignore[assignment]


# ===========================================================================
# DATA CLASSES
# ===========================================================================

@dataclass
class GeneratedDoc:
    """Internal representation of a generated synthetic document."""
    doc_id: str
    doc_type: str          # equipment_manual | maintenance_sop | maintenance_log | etc.
    title: str
    asset_id: str
    asset_family: str      # blast_furnace_fan | centrifugal_pump | etc.
    equipment_class: str
    plant_area: str
    content_markdown: str
    content_json: dict[str, Any]
    failure_modes_referenced: list[str]
    fault_codes_referenced: list[str]
    revision: str
    has_noise: bool = False
    doc_hash: str = ""
    applicable_equipment_classes: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.doc_hash and self.content_markdown:
            self.doc_hash = hashlib.sha256(
                self.content_markdown.encode("utf-8")
            ).hexdigest()[:16]


@dataclass
class GeneratorStats:
    total_attempted: int = 0
    total_generated: int = 0
    deduped_out: int = 0
    noise_injected: int = 0
    llm_elaborated: int = 0
    entities_persisted: int = 0
    quarantined: int = 0
    by_type: dict[str, int] = field(default_factory=dict)


# ===========================================================================
# FAKER / MIMESIS HELPERS
# ===========================================================================

class FieldFactory:
    """
    Encapsulates deterministic fake-data generation.
    Falls back to random-based generation when Faker/Mimesis unavailable.
    """

    def __init__(self, seed: int = 42) -> None:
        self.seed = seed
        self.rng = random.Random(seed)

        if _HAS_FAKER:
            self.faker = Faker("en_IN")
            self.faker.seed_instance(seed)
        else:
            self.faker = None

        if _HAS_MIMESIS:
            self.generic = Generic("en", seed=seed)
        else:
            self.generic = None

    def equipment_id(self, family: str, seq: int) -> str:
        prefixes = {
            "blast_furnace_fan": "BF-FAN",
            "centrifugal_pump": "PUMP",
            "roller_conveyor_bearing": "BRG",
            "hydraulic_power_unit": "HPU",
            "hot_strip_mill_conveyor": "CONV",
        }
        prefix = prefixes.get(family, "EQP")
        return f"{prefix}-{seq:02d}"

    def person_name(self) -> str:
        indian_names = [
            "Rajesh Kumar", "Anil Sharma", "Priya Nair", "Suresh Patel",
            "Kavitha Menon", "Dinesh Rao", "Meena Verma", "Arjun Singh",
            "Lakshmi Iyer", "Sanjay Gupta", "Ramesh Tiwari", "Deepak Joshi",
            "Shweta Desai", "Vikram Reddy", "Pradeep Mishra", "Anita Pillai",
        ]
        return self.rng.choice(indian_names)

    def role(self) -> str:
        roles = [
            "Senior Maintenance Technician", "Maintenance Engineer",
            "Mechanical Engineer", "Reliability Engineer", "Shift Supervisor",
            "Maintenance Manager", "Maintenance Planner", "Instrument Engineer",
        ]
        return self.rng.choice(roles)

    def timestamp_recent(self, days_back: int = 365) -> datetime:
        base = datetime(2024, 1, 1)
        offset = self.rng.randint(0, days_back)
        return base + timedelta(days=offset, hours=self.rng.randint(0, 23),
                                minutes=self.rng.randint(0, 59))

    def work_order_id(self) -> str:
        prefix = self.rng.choice(["WO", "PM", "CM", "EM"])
        if self.generic is not None:
            # Use mimesis for a realistic numeric sequence
            seq = self.generic.numeric.integer_number(start=10000, end=99999)
        else:
            seq = self.rng.randint(10000, 99999)
        return f"{prefix}-2024-{seq}"

    def technician_id(self) -> str:
        if self.generic is not None:
            # Use mimesis for technician badge numbers
            num = self.generic.numeric.integer_number(start=1000, end=9999)
        else:
            num = self.rng.randint(1000, 9999)
        return f"TECH-{num}"

    def revision(self) -> str:
        year = self.rng.choice(["2023", "2024", "2025"])
        quarter = self.rng.choice(["Q1", "Q2", "Q3", "Q4"])
        return f"{year}-{quarter}"

    def plant_area(self, family: str) -> str:
        mapping = {
            "blast_furnace_fan": "BF-Area-1",
            "centrifugal_pump": "CW-Station-2",
            "roller_conveyor_bearing": "HSM-Bay-3",
            "hydraulic_power_unit": "HPU-Room-4",
            "hot_strip_mill_conveyor": "ROT-Area-5",
        }
        return mapping.get(family, "General-Area")

    def sensor_reading(self, sensor_key: str, family_data: dict,
                       condition: str = "normal") -> float:
        """Return a plausible sensor reading for given condition."""
        ranges = family_data.get("sensor_ranges", {}).get(sensor_key, {})
        if not ranges:
            return round(self.rng.uniform(50.0, 100.0), 1)

        if condition == "normal":
            lo, hi = ranges.get("normal_min", 30), ranges.get("normal_max", 80)
        elif condition == "warning":
            lo = ranges.get("normal_max", 80)
            hi = ranges.get("warning_max", 110)
        else:  # critical
            lo = ranges.get("warning_max", 110)
            hi = ranges.get("critical_max", 140)

        return round(self.rng.uniform(lo, hi), 1)

    def loss_inr(self) -> int:
        """Random production loss in INR (₹75,000/hr × downtime hours)."""
        hours = self.rng.randint(2, 48)
        return hours * 75_000

    def catalog_seq(self) -> str:
        return f"{self.rng.randint(1000, 9999)}"


# ===========================================================================
# NARRATIVE GENERATORS (template-only, deterministic, no LLM)
# ===========================================================================

class TemplateNarratives:
    """
    Deterministic narrative templates for the offline/fallback mode.
    Indexed by (doc_type, narrative_key). The LLM elaboration step replaces
    these with richer generated text when --use-llm is active.
    """

    _MANUAL_DESCRIPTIONS = [
        (
            "This equipment plays a critical role in maintaining continuous production "
            "in the {plant_area}. Routine inspection as per this manual ensures "
            "reliability targets of ≥98.5% availability are maintained."
        ),
        (
            "Designed to operate continuously under demanding thermal and mechanical "
            "loads, {equipment_name} requires strict adherence to preventive maintenance "
            "intervals defined in this document."
        ),
        (
            "As a key rotating asset in the {plant_area}, this equipment is classified "
            "under the 'critical' maintenance tier. All maintenance activities must be "
            "logged in the CMMS (SAP PM) within 24 hours of completion."
        ),
    ]

    _SOP_PURPOSES = [
        (
            "This procedure establishes a standardized, safe method for performing "
            "{sop_title} on {applicable_equipment}. It ensures compliance with "
            "OHSAS 18001 safety standards and ISO 14224 reliability requirements."
        ),
        (
            "The purpose of this SOP is to provide maintenance personnel with clear, "
            "step-by-step instructions for {sop_title}, minimizing equipment downtime "
            "and ensuring post-maintenance performance meets design specifications."
        ),
    ]

    _LOG_WORK_DESCRIPTIONS = [
        (
            "Routine preventive maintenance carried out as per scheduled PM plan. "
            "Equipment inspected, lubricated, and returned to service after "
            "verification of all parameters within specification."
        ),
        (
            "Corrective maintenance initiated following control room alarm. Equipment "
            "isolated per LOTO procedure. Fault identified and rectified. All safety "
            "checks completed before equipment restart."
        ),
        (
            "Predictive maintenance action triggered by vibration monitoring trend. "
            "On-site inspection confirmed early-stage fault. Preventive replacement "
            "performed to avoid unplanned failure."
        ),
    ]

    _FINDINGS_TEMPLATES = [
        "Visual inspection showed {fault_desc}. Sensor readings confirmed {condition}.",
        (
            "On opening the inspection cover, {fault_desc} was observed. Bearing "
            "temperature reading at the time of fault was {temp}°C. Vibration baseline "
            "exceeded by {vib_pct}%."
        ),
        (
            "Lab oil analysis results (sample taken {sample_days} days prior) showed "
            "ISO 4406 cleanliness code 21/19/16. {fault_desc} confirmed during "
            "physical inspection."
        ),
    ]

    _FAR_SUMMARIES = [
        (
            "This report documents the root cause analysis of {fault_code} on "
            "{equipment_name} ({equipment_id}). The incident resulted in {downtime}h "
            "of unplanned downtime. The root cause was identified as {root_cause}. "
            "Corrective and preventive actions have been defined to prevent recurrence."
        ),
        (
            "Failure of {equipment_name} occurred on {incident_date}. Analysis of "
            "operating data, visual evidence, and lab reports conclusively identified "
            "{root_cause} as the primary root cause. This report presents findings and "
            "a structured action plan."
        ),
    ]

    _FIVE_WHYS = {
        "BF-BRG-002": [
            "The blast furnace fan bearing overheated and seized.",
            "The bearing lubricant film broke down under the thermal load.",
            "The lubricant was contaminated with water from the cooling circuit, reducing its viscosity.",
            "The cooling water circuit had a micro-leak at the heat exchanger gland, undetected for 14 days.",
            "The preventive inspection schedule for the cooling circuit did not include gland seal checks.",
        ],
        "PMP-SEAL-001": [
            "The mechanical seal started leaking process fluid.",
            "The seal face flatness had degraded beyond the 0.5 mm service limit.",
            "The pump experienced a brief dry-running episode during the startup sequence.",
            "The suction strainer blockage caused a low-NPSH condition, leading to cavitation and air ingestion.",
            "The suction strainer cleaning interval (90 days) had been extended to 180 days without engineering review.",
        ],
        "BRG-SPALL-001": [
            "The inner race of the spherical roller bearing showed spalling.",
            "Fatigue crack initiated from a subsurface stress concentration point.",
            "The bearing was operating at 110% of its rated radial load due to slab overweight.",
            "The slab weight specification had been updated operationally without updating the bearing load calculation.",
            "No formal management-of-change process existed for operational parameter changes.",
        ],
        "HPU-PRV-002": [
            "The hydraulic system pressure relief valve stuck in the open position.",
            "A contamination particle became lodged in the valve poppet seat.",
            "The hydraulic oil ISO cleanliness level had degraded to NAS Class 11.",
            "The return-line filter bypass was active for 3 days due to a stuck bypass indicator (false positive).",
            "The filter bypass indicator was not included in the daily inspection checklist.",
        ],
        "CVR-COUP-002": [
            "The conveyor drive coupling spider element fractured.",
            "A torque spike occurred during a strip cobble event.",
            "The cobble event jammed the conveyor rollers, causing instantaneous torque to exceed coupling rating.",
            "The anti-cobble interlock was disabled for commissioning 6 months prior and never re-enabled.",
            "The interlock re-enablement step was missing from the commissioning completion checklist.",
        ],
    }

    def __init__(self, rng: random.Random) -> None:
        self.rng = rng

    def manual_description(self, equipment_name: str, plant_area: str) -> str:
        tmpl = self.rng.choice(self._MANUAL_DESCRIPTIONS)
        return tmpl.format(equipment_name=equipment_name, plant_area=plant_area)

    def sop_purpose(self, sop_title: str, applicable_equipment: str) -> str:
        tmpl = self.rng.choice(self._SOP_PURPOSES)
        return tmpl.format(sop_title=sop_title, applicable_equipment=applicable_equipment)

    def log_work_description(self, maintenance_type: str) -> str:
        tmpl = self.rng.choice(self._LOG_WORK_DESCRIPTIONS)
        return tmpl

    def log_findings(self, fault_desc: str, temp: float, condition: str = "abnormal") -> str:
        sample_days = self.rng.randint(5, 30)
        vib_pct = self.rng.randint(15, 80)
        tmpl = self.rng.choice(self._FINDINGS_TEMPLATES)
        return tmpl.format(
            fault_desc=fault_desc,
            condition=condition,
            temp=temp,
            vib_pct=vib_pct,
            sample_days=sample_days,
        )

    def far_summary(self, fault_code: str, equipment_name: str, equipment_id: str,
                    downtime: int, root_cause: str, incident_date: str) -> str:
        tmpl = self.rng.choice(self._FAR_SUMMARIES)
        return tmpl.format(
            fault_code=fault_code, equipment_name=equipment_name,
            equipment_id=equipment_id, downtime=downtime,
            root_cause=root_cause, incident_date=incident_date
        )

    def five_whys(self, fault_code: str) -> list[str]:
        if fault_code in self._FIVE_WHYS:
            return self._FIVE_WHYS[fault_code]
        # Fallback generic 5-whys
        return [
            "The equipment failed unexpectedly during normal operation.",
            "A component reached the end of its service life prematurely.",
            "The operating conditions were more severe than design basis.",
            "The maintenance interval was not adjusted for actual operating severity.",
            "The maintenance planning system does not account for condition-based interval adjustment.",
        ]


# ===========================================================================
# NOISE INJECTOR
# ===========================================================================

class NoiseInjector:
    """
    Injects realistic noise into maintenance log documents.

    Noise categories (from arXiv:2511.05311):
        1. Identifier misalignment (wrong equipment ID format)
        2. Invalid values (temperature as string "HOT")
        3. Missing values (blank fields)
        4. Date inconsistency (future date, wrong format)
        5. Abbreviations/typos (common maintenance log shortforms)
        6. Test entries ("TEST", "DO NOT USE")
    """

    _ABBREVS = {
        "bearing": "brg",
        "temperature": "temp",
        "vibration": "vib",
        "lubrication": "lube",
        "replacement": "repl",
        "inspection": "insp",
        "pressure": "press",
        "maintenance": "maint",
        "corrective": "corr",
        "preventive": "prev",
    }

    _TYPOS = {
        "bearing": "bearng",
        "mechanical": "mechancal",
        "lubrication": "lubricaton",
        "temperature": "temperture",
        "vibration": "vibr",
    }

    def __init__(self, rng: random.Random) -> None:
        self.rng = rng

    def inject(self, content: str, noise_level: str = "mild") -> str:
        """Apply a mix of realistic noise to log content."""
        noise_type = self.rng.choice([
            "abbreviation", "typo", "date_format", "partial_missing"
        ])

        if noise_type == "abbreviation":
            for full, abbrev in self._ABBREVS.items():
                if full in content and self.rng.random() < 0.4:
                    content = content.replace(full, abbrev, 1)

        elif noise_type == "typo":
            for correct, typo in self._TYPOS.items():
                if correct in content and self.rng.random() < 0.3:
                    content = content.replace(correct, typo, 1)
                    break

        elif noise_type == "date_format":
            # Replace ISO date with DD/MM/YYYY style
            content = re.sub(
                r"\d{4}-\d{2}-\d{2}",
                lambda m: "/".join(reversed(m.group(0).split("-"))),
                content,
                count=1,
            )

        elif noise_type == "partial_missing":
            # Replace a measurement value with "N/A" or blank
            content = re.sub(
                r"\|\s*\d+\.\d+\s*\|",
                "| N/A |",
                content,
                count=1,
            )

        return content


# ===========================================================================
# DEDUP GATE
# ===========================================================================

class DedupGate:
    """
    Cosine-similarity-based deduplication.
    Falls back to exact hash dedup if sentence-transformers unavailable.
    """

    THRESHOLD = 0.85

    def __init__(self, threshold: float = 0.85) -> None:
        self.threshold = threshold
        self._hashes: set[str] = set()
        self._embeddings: list = []
        self._model = None

        if _HAS_ST:
            try:
                log.info("Loading sentence-transformers/all-MiniLM-L6-v2 for dedup...")
                self._model = SentenceTransformer("all-MiniLM-L6-v2")
                log.info("Dedup model loaded.")
            except Exception as exc:
                log.warning("Failed to load dedup model: %s — using hash dedup", exc)

    def is_duplicate(self, text: str, doc_hash: str) -> bool:
        """Return True if this text is a near-duplicate of an already-seen doc."""
        # First: exact hash check (fast path)
        if doc_hash in self._hashes:
            return True

        # Then: embedding similarity if model available
        if self._model is not None and self._embeddings:
            try:
                emb = self._model.encode(text[:512], show_progress_bar=False)
                emb = emb / (np.linalg.norm(emb) + 1e-9)
                for seen_emb in self._embeddings[-100:]:  # check last 100 for speed
                    sim = float(np.dot(emb, seen_emb))
                    if sim > self.threshold:
                        return True
                self._embeddings.append(emb)
            except Exception:
                pass  # fall through to non-duplicate

        self._hashes.add(doc_hash)
        return False


# ===========================================================================
# DOCUMENT TYPE GENERATORS
# ===========================================================================

class KnowledgeBaseGenerator:
    """
    Orchestrates generation of all 6 document types.
    """

    # Document type distribution (counts sum to ~500)
    _DISTRIBUTION = {
        TemplateType.EQUIPMENT_MANUAL: 100,
        TemplateType.MAINTENANCE_SOP: 100,
        TemplateType.MAINTENANCE_LOG: 150,
        TemplateType.FAILURE_ANALYSIS: 80,
        TemplateType.INCIDENT_SUMMARY: 40,
        TemplateType.SPARE_PARTS_RECORD: 30,
    }

    _SCENARIOS = [
        "normal_operation",
        "degradation_onset",
        "acute_failure",
        "post_repair",
        "seasonal_maintenance",
    ]

    def __init__(
        self,
        seed: int = 42,
        noise_fraction: float = 0.15,
        use_llm: bool = False,
        output_dir: Optional[Path] = None,
    ) -> None:
        self.seed = seed
        self.noise_fraction = noise_fraction
        self.use_llm = use_llm

        # Output paths
        if output_dir is None:
            output_dir = _REPO_ROOT / "data" / "synthetic"
        self.output_dir = Path(output_dir)
        self.docs_dir = self.output_dir / "docs"
        self.docs_dir.mkdir(parents=True, exist_ok=True)

        self.rng = random.Random(seed)
        self.ff = FieldFactory(seed=seed)
        self.narr = TemplateNarratives(rng=self.rng)
        self.noise = NoiseInjector(rng=self.rng)
        self.dedup = DedupGate(threshold=0.85)
        self.stats = GeneratorStats()

        self._families = list(ONTOLOGY["asset_families"].keys())
        self._all_docs: list[GeneratedDoc] = []
        self._metadata_index: list[dict] = []

    # ------------------------------------------------------------------
    # TOP-LEVEL ENTRY POINT
    # ------------------------------------------------------------------

    def run(self, total: int = 500) -> list[GeneratedDoc]:
        """
        Generate `total` documents across all 6 types.
        Returns list of GeneratedDoc.
        """
        log.info("Starting synthetic KB generation: %d documents, seed=%d, use_llm=%s",
                 total, self.seed, self.use_llm)

        # Scale distribution proportionally
        distribution = self._scale_distribution(total)
        seq = 0

        for doc_type, count in distribution.items():
            log.info("Generating %d %s documents...", count, doc_type.value)
            generated = 0
            attempts = 0
            while generated < count and attempts < count * 3:
                attempts += 1
                family = self.rng.choice(self._families)
                scenario = self.rng.choice(self._SCENARIOS)
                doc = self._generate_document(doc_type, family, scenario, seq)
                seq += 1
                self.stats.total_attempted += 1

                if doc is None:
                    continue

                if self.dedup.is_duplicate(doc.content_markdown[:512], doc.doc_hash):
                    self.stats.deduped_out += 1
                    continue

                # Noise injection for maintenance logs
                if (doc_type == TemplateType.MAINTENANCE_LOG
                        and self.rng.random() < self.noise_fraction):
                    doc.content_markdown = self.noise.inject(doc.content_markdown)
                    doc.has_noise = True
                    self.stats.noise_injected += 1

                # LLM elaboration (optional)
                if self.use_llm:
                    doc = self._llm_elaborate(doc)

                self._all_docs.append(doc)
                self._save_doc(doc)
                generated += 1
                self.stats.total_generated += 1
                self.stats.by_type[doc_type.value] = (
                    self.stats.by_type.get(doc_type.value, 0) + 1
                )

        self._save_metadata_index()
        self._build_and_save_artifacts()
        self._persist_entities()

        log.info(
            "Generation complete: %d docs generated, %d deduped, %d noise, %d LLM",
            self.stats.total_generated,
            self.stats.deduped_out,
            self.stats.noise_injected,
            self.stats.llm_elaborated,
        )
        return self._all_docs

    # ------------------------------------------------------------------
    # DOCUMENT GENERATORS (one per type)
    # ------------------------------------------------------------------

    def _generate_document(
        self,
        doc_type: TemplateType,
        family: str,
        scenario: str,
        seq: int,
    ) -> Optional[GeneratedDoc]:
        try:
            dispatch = {
                TemplateType.EQUIPMENT_MANUAL: self._gen_equipment_manual,
                TemplateType.MAINTENANCE_SOP: self._gen_maintenance_sop,
                TemplateType.MAINTENANCE_LOG: self._gen_maintenance_log,
                TemplateType.FAILURE_ANALYSIS: self._gen_failure_analysis,
                TemplateType.INCIDENT_SUMMARY: self._gen_incident_summary,
                TemplateType.SPARE_PARTS_RECORD: self._gen_spare_parts_record,
            }
            return dispatch[doc_type](family, scenario, seq)
        except Exception as exc:
            log.debug("Document generation failed (seq=%d, type=%s): %s",
                      seq, doc_type.value, exc)
            return None

    def _gen_equipment_manual(
        self, family: str, scenario: str, seq: int
    ) -> Optional[GeneratedDoc]:
        fam_data = ONTOLOGY["asset_families"][family]
        eq_ids = fam_data.get("equipment_ids", ["EQP-01"])
        eq_id = self.rng.choice(eq_ids)
        subsystems = fam_data.get("subsystems", [])
        if not subsystems:
            return None
        subsystem = self.rng.choice(subsystems)
        failure_modes = subsystem.get("failure_modes", [])

        equipment_name = f"{eq_id} — {family.replace('_', ' ').title()}"
        plant_area = self.ff.plant_area(family)

        # Build design_params list for template
        dp_raw = fam_data.get("design_parameters", {})
        design_params = {
            k: type("P", (), {"value": v, "unit": _unit_for(k)})()
            for k, v in list(dp_raw.items())[:6]
        }

        # Build sensor_ranges dict
        sensor_ranges = {
            k: type("R", (), v)()
            for k, v in list(fam_data.get("sensor_ranges", {}).items())[:5]
        }

        # Subsystem list for template
        subsystem_list = [
            type("SS", (), {
                "name": ss["name"].replace("_", " ").title(),
                "description": f"{ss['name'].replace('_', ' ').title()} subsystem components",
            })()
            for ss in subsystems
        ]

        # Maintenance tasks
        maintenance_tasks = [
            type("T", (), {
                "task": f"Inspect {fm['name'].lower()}",
                "frequency": "Monthly" if fm["severity"] == "critical" else "Quarterly",
                "role": "Maintenance Engineer",
                "sop": f"SOP-{family[:2].upper()}-{fm['fault_code'][:6]}",
            })()
            for fm in failure_modes[:4]
        ]

        author_name = self.ff.person_name()
        approver_name = self.ff.person_name()
        ts = self.ff.timestamp_recent()

        vars_dict: dict[str, Any] = {
            "equipment_name": equipment_name,
            "equipment_id": eq_id,
            "equipment_class": fam_data["iso14224_class"],
            "doc_seq": seq,
            "revision": self.ff.revision(),
            "issue_date": ts.strftime("%Y-%m-%d"),
            "iso14224_class": fam_data["iso14224_class"],
            "work_center": f"WC-{plant_area}",
            "plant_area": plant_area,
            "plant_name": "Tata Steel Jamshedpur Integrated Steel Plant",
            "subsystem": subsystem["name"].replace("_", " ").title(),
            "narrative_description": self.narr.manual_description(equipment_name, plant_area),
            "design_params": design_params,
            "sensor_ranges": sensor_ranges,
            "narrative_subsystems": (
                f"The {equipment_name} consists of {len(subsystems)} main subsystem(s), "
                "each requiring periodic maintenance per the schedules defined below."
            ),
            "subsystems": subsystem_list,
            "failure_modes": failure_modes[:3],
            "narrative_maintenance_schedule": (
                "Preventive maintenance is structured around ISO 14224 reliability data "
                "and historical MTBF for each failure mode. Critical assets have monthly "
                "inspection cycles; standard assets are quarterly."
            ),
            "maintenance_tasks": maintenance_tasks,
            "author_name": author_name,
            "author_role": self.ff.role(),
            "prepared_date": ts.strftime("%Y-%m-%d"),
            "approver_name": approver_name,
            "approver_role": "Maintenance Manager",
        }

        content = render_template(TemplateType.EQUIPMENT_MANUAL, vars_dict)
        fm_codes = [fm["fault_code"] for fm in failure_modes[:3]]

        return GeneratedDoc(
            doc_id=f"MANUAL-{family[:3].upper()}-{seq:04d}",
            doc_type="manual",
            title=f"Equipment Manual — {equipment_name}",
            asset_id=eq_id,
            asset_family=family,
            equipment_class=fam_data["iso14224_class"],
            plant_area=plant_area,
            content_markdown=content,
            content_json=vars_dict,
            failure_modes_referenced=[fm["name"] for fm in failure_modes[:3]],
            fault_codes_referenced=fm_codes,
            revision=vars_dict["revision"],
            applicable_equipment_classes=[fam_data["iso14224_class"]],
        )

    def _gen_maintenance_sop(
        self, family: str, scenario: str, seq: int
    ) -> Optional[GeneratedDoc]:
        fam_data = ONTOLOGY["asset_families"][family]
        subsystems = fam_data.get("subsystems", [])
        if not subsystems:
            return None
        subsystem = self.rng.choice(subsystems)
        failure_modes = subsystem.get("failure_modes", [])
        if not failure_modes:
            return None
        fm = self.rng.choice(failure_modes)

        eq_ids = fam_data.get("equipment_ids", ["EQP-01"])
        eq_id = self.rng.choice(eq_ids)
        plant_area = self.ff.plant_area(family)
        ts = self.ff.timestamp_recent()

        sop_title = f"{fm['name']} — {subsystem['name'].replace('_', ' ').title()}"
        sop_number = f"SOP-{family[:2].upper()}-{fm['fault_code']}-{seq:03d}"

        # Build procedure steps from corrective actions
        steps = [
            type("S", (), {
                "number": i + 1,
                "title": action.split("—")[0].strip().split("(")[0].strip(),
                "instruction": action,
                "caution": (
                    f"Ensure LOTO (SOP-ELEC-LOTO-01) is active before proceeding"
                    if i == 0 else ""
                ),
                "torque_spec": ("120 Nm for M24 bolts" if "bolts" in action.lower() else ""),
                "measurement": ("Measure alignment to ±0.05 mm" if "align" in action.lower() else ""),
            })()
            for i, action in enumerate(fm["corrective_actions"][:6])
        ]

        parts = fm.get("requires_parts", [])
        tools_list = [
            "Torque wrench (0–300 Nm)",
            "Laser alignment tool (Prüftechnik Rotalign Ultra)",
            "Bearing puller and press",
            "Temperature gun (IR, ±1°C accuracy)",
            "Vibration analyzer (ADASH A4300)",
        ]

        acceptance_criteria = [
            f"Vibration ≤ {fam_data.get('sensor_ranges', {}).get('vibration_mm_s', {}).get('normal_max', 4.5)} mm/s RMS",
            f"Bearing temperature ≤ {fam_data.get('sensor_ranges', {}).get('temperature_c', {}).get('normal_max', 85)}°C",
            "No unusual noise during 30-minute run-in",
            "All bolts torqued to specification",
            "Work order signed off in CMMS (SAP PM)",
        ]

        vars_dict: dict[str, Any] = {
            "sop_title": sop_title,
            "sop_number": sop_number,
            "revision": self.ff.revision(),
            "effective_date": ts.strftime("%Y-%m-%d"),
            "applicable_equipment": eq_id,
            "equipment_class": family.replace("_", " ").title(),
            "plant_area": plant_area,
            "plant_name": "Tata Steel Jamshedpur",
            "narrative_purpose": self.narr.sop_purpose(sop_title, eq_id),
            "ppe_required": [
                "Safety helmet (IS 2925)", "Safety shoes (IS 1989)",
                "Safety glasses (ANSI Z87.1)", "Nitrile gloves",
                "High-visibility vest",
            ],
            "requires_isolation": True,
            "hot_work": False,
            "safety_warnings": [
                f"EQUIPMENT MUST BE ISOLATED AND LOCKED OUT BEFORE ANY WORK (SOP-ELEC-LOTO-01)",
                f"Verify zero energy state with approved test instrument before opening inspection covers.",
                f"Hot surfaces (>60°C) — use thermal gloves and allow to cool before contact.",
            ],
            "tools_required": tools_list[:4],
            "parts_required": parts[:3] or ["Refer to BOM in work order"],
            "estimated_duration_hours": self.rng.choice([4, 6, 8, 12, 16]),
            "min_crew": self.rng.choice([2, 2, 3]),
            "procedure_steps": steps,
            "acceptance_criteria": acceptance_criteria,
            "narrative_post_work": (
                "After completing all steps, conduct a 30-minute supervised run-in test. "
                "Monitor all sensor readings for the first 2 hours of production operation. "
                "Report any anomaly to the shift supervisor immediately."
            ),
            "work_order_prefix": f"{family[:3].upper()}-SOP",
            "work_order_seq": self.rng.randint(10000, 99999),
            "permit_seq": self.rng.randint(1000, 9999),
            "author_name": self.ff.person_name(),
            "author_role": self.ff.role(),
            "approver_name": self.ff.person_name(),
            "effective_date_repeat": ts.strftime("%Y-%m-%d"),
        }

        content = render_template(TemplateType.MAINTENANCE_SOP, vars_dict)

        return GeneratedDoc(
            doc_id=f"SOP-{family[:3].upper()}-{seq:04d}",
            doc_type="sop",
            title=f"SOP — {sop_title}",
            asset_id=eq_id,
            asset_family=family,
            equipment_class=fam_data["iso14224_class"],
            plant_area=plant_area,
            content_markdown=content,
            content_json=vars_dict,
            failure_modes_referenced=[fm["name"]],
            fault_codes_referenced=[fm["fault_code"]],
            revision=vars_dict["revision"],
            applicable_equipment_classes=[fam_data["iso14224_class"]],
        )

    def _gen_maintenance_log(
        self, family: str, scenario: str, seq: int
    ) -> Optional[GeneratedDoc]:
        fam_data = ONTOLOGY["asset_families"][family]
        subsystems = fam_data.get("subsystems", [])
        if not subsystems:
            return None
        subsystem = self.rng.choice(subsystems)
        failure_modes = subsystem.get("failure_modes", [])
        if not failure_modes:
            return None
        fm = self.rng.choice(failure_modes)

        eq_ids = fam_data.get("equipment_ids", ["EQP-01"])
        eq_id = self.rng.choice(eq_ids)
        plant_area = self.ff.plant_area(family)
        ts = self.ff.timestamp_recent()
        maint_types = ["corrective", "preventive", "predictive"]
        maint_type = (
            "corrective" if scenario == "acute_failure"
            else "preventive" if scenario == "seasonal_maintenance"
            else self.rng.choice(maint_types)
        )

        condition = "normal" if scenario == "normal_operation" else "warning"
        temp = self.ff.sensor_reading("temperature_c", fam_data, condition)
        vib = self.ff.sensor_reading("vibration_mm_s", fam_data, condition)
        pres = self.ff.sensor_reading("pressure_bar", fam_data, condition)
        normal_temp = fam_data.get("sensor_ranges", {}).get("temperature_c", {})
        normal_vib = fam_data.get("sensor_ranges", {}).get("vibration_mm_s", {})

        parts = fm.get("requires_parts", [])
        parts_consumed = [
            type("P", (), {
                "part_number": p,
                "part_name": f"Part {p}",
                "qty": self.rng.randint(1, 2),
                "batch": f"BT-{self.rng.randint(10000, 99999)}",
            })()
            for p in parts[:2]
        ] if maint_type == "corrective" else []

        measurements = [
            type("M", (), {
                "parameter": "Bearing Temperature (°C)",
                "before": f"{temp}",
                "after": f"{self.ff.sensor_reading('temperature_c', fam_data, 'normal')}",
                "range": (
                    f"{normal_temp.get('normal_min', 30)} – "
                    f"{normal_temp.get('normal_max', 85)}"
                ),
            })(),
            type("M", (), {
                "parameter": "Vibration (mm/s RMS)",
                "before": f"{vib}",
                "after": f"{self.ff.sensor_reading('vibration_mm_s', fam_data, 'normal')}",
                "range": (
                    f"{normal_vib.get('normal_min', 0.5)} – "
                    f"{normal_vib.get('normal_max', 4.5)}"
                ),
            })(),
        ]

        outcomes = ["resolved", "partial", "pending"]
        outcome = "resolved" if scenario in ("acute_failure", "post_repair") else "resolved"
        returned = ts.strftime("%Y-%m-%d %H:%M")

        vars_dict: dict[str, Any] = {
            "log_id": f"{family[:3].upper()}-{seq:06d}",
            "work_order_id": self.ff.work_order_id(),
            "performed_date": ts.strftime("%Y-%m-%d"),
            "shift": self.rng.choice(["A", "B", "C", "General"]),
            "crew_size": self.rng.randint(2, 5),
            "equipment_id": eq_id,
            "equipment_name": f"{eq_id} — {family.replace('_', ' ').title()}",
            "plant_area": plant_area,
            "maintenance_type": maint_type.capitalize(),
            "narrative_work_description": self.narr.log_work_description(maint_type),
            "narrative_findings": self.narr.log_findings(
                fm.get("name", "fault"), temp, condition
            ),
            "fault_codes": [fm.get("fault_code", "UNKNOWN")],
            "severity": fm.get("severity", "medium").upper(),
            "actions_taken": fm.get("corrective_actions", ["No action taken"])[:4],
            "parts_consumed": parts_consumed,
            "measurements": measurements,
            "outcome": outcome.capitalize(),
            "returned_to_service": returned,
            "narrative_outcome": (
                f"Equipment returned to normal operating parameters after {maint_type} maintenance. "
                f"Next scheduled maintenance: {(ts + timedelta(days=90)).strftime('%Y-%m-%d')}."
            ),
            "next_due_date": (ts + timedelta(days=self.rng.choice([30, 60, 90, 180]))).strftime("%Y-%m-%d"),
            "technician_name": self.ff.person_name(),
            "technician_id": self.ff.technician_id(),
            "supervisor_name": self.ff.person_name(),
            "signoff_time": (ts + timedelta(hours=self.rng.randint(1, 8))).strftime("%Y-%m-%d %H:%M"),
        }

        content = render_template(TemplateType.MAINTENANCE_LOG, vars_dict)

        return GeneratedDoc(
            doc_id=f"LOG-{family[:3].upper()}-{seq:04d}",
            doc_type="maintenance_record",
            title=f"Maintenance Log — {eq_id} {ts.strftime('%Y-%m-%d')}",
            asset_id=eq_id,
            asset_family=family,
            equipment_class=fam_data["iso14224_class"],
            plant_area=plant_area,
            content_markdown=content,
            content_json=vars_dict,
            failure_modes_referenced=[fm.get("name", "")],
            fault_codes_referenced=[fm.get("fault_code", "")],
            revision="N/A",
            applicable_equipment_classes=[fam_data["iso14224_class"]],
        )

    def _gen_failure_analysis(
        self, family: str, scenario: str, seq: int
    ) -> Optional[GeneratedDoc]:
        fam_data = ONTOLOGY["asset_families"][family]
        subsystems = fam_data.get("subsystems", [])
        if not subsystems:
            return None
        subsystem = self.rng.choice(subsystems)
        failure_modes = subsystem.get("failure_modes", [])
        if not failure_modes:
            return None
        fm = self.rng.choice(failure_modes)

        eq_ids = fam_data.get("equipment_ids", ["EQP-01"])
        eq_id = self.rng.choice(eq_ids)
        plant_area = self.ff.plant_area(family)
        ts = self.ff.timestamp_recent(days_back=730)
        report_ts = ts + timedelta(days=self.rng.randint(3, 14))
        downtime = self.rng.randint(4, 72)
        loss_inr = downtime * 75_000
        root_cause = self.rng.choice(fm.get("root_causes", ["Unknown root cause"]))

        five_whys = self.narr.five_whys(fm.get("fault_code", ""))

        # Build timeline
        timeline = [
            type("E", (), {
                "time": (ts - timedelta(hours=self.rng.randint(2, 48))).strftime("%H:%M"),
                "event": f"First alarm: {fm.get('symptoms', ['alarm'])[0] if fm.get('symptoms') else 'Sensor alarm'}",
                "sensor_reading": f"Temp={self.ff.sensor_reading('temperature_c', fam_data, 'warning')}°C",
                "action": "Control room notified shift supervisor",
            })(),
            type("E", (), {
                "time": ts.strftime("%H:%M"),
                "event": f"Equipment shutdown — {fm.get('fault_code', 'FAULT')} triggered",
                "sensor_reading": f"Temp={self.ff.sensor_reading('temperature_c', fam_data, 'critical')}°C",
                "action": "Maintenance team dispatched",
            })(),
            type("E", (), {
                "time": (ts + timedelta(hours=self.rng.randint(1, 4))).strftime("%H:%M"),
                "event": "Maintenance team arrived, isolation complete",
                "sensor_reading": "N/A (isolated)",
                "action": "LOTO applied, inspection commenced",
            })(),
        ]

        corrective_actions = [
            type("CA", (), {
                "action": ca,
                "owner": self.ff.person_name(),
                "due_date": (report_ts + timedelta(days=self.rng.randint(7, 30))).strftime("%Y-%m-%d"),
                "status": self.rng.choice(["Completed", "In Progress", "Scheduled"]),
            })()
            for ca in fm.get("corrective_actions", ["Inspect and repair"])[:4]
        ]

        evidence = [
            f"Oil/grease sample analysis showed contamination (NAS Class {self.rng.randint(9, 12)})",
            f"Vibration spectrum showed {fm.get('symptoms', ['anomaly'])[0] if fm.get('symptoms') else 'anomaly'}",
            f"Bearing contact temperature at failure: {self.ff.sensor_reading('temperature_c', fam_data, 'critical')}°C",
            f"Visual inspection confirmed {fm.get('name', 'fault')} on affected component",
        ]

        vars_dict: dict[str, Any] = {
            "equipment_name": f"{eq_id} — {family.replace('_', ' ').title()}",
            "report_seq": f"{seq:04d}",
            "incident_date": ts.strftime("%Y-%m-%d"),
            "report_date": report_ts.strftime("%Y-%m-%d"),
            "equipment_id": eq_id,
            "fault_code": fm.get("fault_code", "UNKNOWN"),
            "severity": fm.get("severity", "medium").upper(),
            "narrative_executive_summary": self.narr.far_summary(
                fm.get("fault_code", "FAULT"), f"{eq_id} {family}",
                eq_id, downtime, root_cause, ts.strftime("%Y-%m-%d")
            ),
            "incident_time": ts.strftime("%H:%M"),
            "operating_condition": self.rng.choice(["Full load", "Partial load", "Startup"]),
            "production_impact_hours": downtime,
            "production_loss_inr": loss_inr,
            "narrative_incident_description": (
                f"At {ts.strftime('%H:%M')} on {ts.strftime('%Y-%m-%d')}, the control room "
                f"received an alarm for {eq_id}. The fault code {fm.get('fault_code', 'FAULT')} "
                f"indicated {fm.get('name', 'fault condition')}. The equipment was shut down "
                f"after {self.rng.randint(5, 30)} minutes as the condition continued to deteriorate."
            ),
            "timeline": timeline,
            "narrative_physical_root_cause": (
                f"Physical inspection and lab analysis confirmed that the root cause was "
                f"{root_cause}. {fm.get('name', 'The fault')} resulted from the interaction of "
                f"operating conditions exceeding the equipment's design envelope over an extended period."
            ),
            "evidence": evidence,
            "contributing_factors": [
                type("CF", (), {
                    "factor": cf,
                    "explanation": (
                        f"This factor contributed to the failure by accelerating the "
                        f"degradation mechanism in the affected component."
                    ),
                })()
                for cf in fm.get("root_causes", ["Unknown"])[:3]
            ],
            "why1": five_whys[0] if len(five_whys) > 0 else "Equipment failed.",
            "why2": five_whys[1] if len(five_whys) > 1 else "Component degraded.",
            "why3": five_whys[2] if len(five_whys) > 2 else "Condition worsened.",
            "why4": five_whys[3] if len(five_whys) > 3 else "Maintenance was delayed.",
            "why5": five_whys[4] if len(five_whys) > 4 else "No proactive monitoring existed.",
            "root_cause_statement": root_cause,
            "corrective_actions": corrective_actions,
            "narrative_preventive_actions": (
                "To prevent recurrence, the following systemic changes are recommended: "
                "review of PM intervals based on actual MTBF data, implementation of "
                "condition-based monitoring, and revision of the management-of-change procedure."
            ),
            "preventive_actions": [
                f"Update PM interval for {fm.get('name', 'this failure mode')} based on MTBF analysis",
                "Implement online condition monitoring for early detection",
                "Train maintenance team on failure mode identification",
                f"Add {fm.get('fault_code', 'FAULT')} to predictive monitoring dashboard",
            ],
            "parts_cost_inr": self.rng.randint(5000, 200000),
            "labour_cost_inr": self.rng.randint(10000, 80000),
            "total_cost_inr": loss_inr + self.rng.randint(15000, 280000),
            "analyst_name": self.ff.person_name(),
            "analyst_role": "Reliability Engineer",
            "reviewer_name": self.ff.person_name(),
        }
        # Compute total_cost_inr correctly
        vars_dict["total_cost_inr"] = (
            vars_dict["parts_cost_inr"] + vars_dict["labour_cost_inr"]
            + vars_dict["production_loss_inr"]
        )

        content = render_template(TemplateType.FAILURE_ANALYSIS, vars_dict)

        return GeneratedDoc(
            doc_id=f"FAR-{family[:3].upper()}-{seq:04d}",
            doc_type="failure_analysis",
            title=f"Failure Analysis Report — {eq_id} {fm.get('fault_code', 'FAULT')}",
            asset_id=eq_id,
            asset_family=family,
            equipment_class=fam_data["iso14224_class"],
            plant_area=plant_area,
            content_markdown=content,
            content_json=vars_dict,
            failure_modes_referenced=[fm.get("name", "")],
            fault_codes_referenced=[fm.get("fault_code", "")],
            revision=report_ts.strftime("%Y-Q%m"),
            applicable_equipment_classes=[fam_data["iso14224_class"]],
        )

    def _gen_incident_summary(
        self, family: str, scenario: str, seq: int
    ) -> Optional[GeneratedDoc]:
        fam_data = ONTOLOGY["asset_families"][family]
        subsystems = fam_data.get("subsystems", [])
        if not subsystems:
            return None
        subsystem = self.rng.choice(subsystems)
        failure_modes = subsystem.get("failure_modes", [])
        if not failure_modes:
            return None
        fm = self.rng.choice(failure_modes)

        eq_ids = fam_data.get("equipment_ids", ["EQP-01"])
        eq_id = self.rng.choice(eq_ids)
        plant_area = self.ff.plant_area(family)
        ts = self.ff.timestamp_recent()

        condition = "critical" if scenario == "acute_failure" else "warning"
        temp = self.ff.sensor_reading("temperature_c", fam_data, condition)
        vib = self.ff.sensor_reading("vibration_mm_s", fam_data, condition)
        pres = self.ff.sensor_reading("pressure_bar", fam_data, condition)
        normal_temp = fam_data.get("sensor_ranges", {}).get("temperature_c", {}).get("normal_max", 85)
        normal_vib = fam_data.get("sensor_ranges", {}).get("vibration_mm_s", {}).get("normal_max", 4.5)
        normal_pres = fam_data.get("sensor_ranges", {}).get("pressure_bar", {}).get("normal_max", 5.0)
        stoppage_hours = self.rng.randint(2, 36)

        immediate_actions = [
            f"Control room acknowledged alarm at {ts.strftime('%H:%M')}",
            f"Shift supervisor notified — equipment isolation ordered",
            f"Maintenance technician dispatched to {plant_area}",
            f"LOTO applied per SOP-ELEC-LOTO-01",
            f"Condition assessment completed — {fm.get('name', 'fault')} confirmed",
        ]

        vars_dict: dict[str, Any] = {
            "incident_id": f"INC-{family[:2].upper()}-{seq:06d}",
            "incident_date": ts.strftime("%Y-%m-%d"),
            "shift": self.rng.choice(["A", "B", "C"]),
            "reporter_name": self.ff.person_name(),
            "reporter_role": self.rng.choice(["Shift Supervisor", "Control Room Operator",
                                              "Maintenance Technician"]),
            "equipment_name": f"{eq_id} — {family.replace('_', ' ').title()}",
            "equipment_id": eq_id,
            "plant_area": plant_area,
            "incident_type": self.rng.choice(["Equipment Failure", "Abnormal Condition",
                                              "Near-Miss", "Planned Shutdown"]),
            "alert_level": fm.get("severity", "medium").upper(),
            "narrative_incident_description": (
                f"At {ts.strftime('%H:%M')}, {eq_id} triggered a {fm.get('severity', 'medium').upper()} "
                f"alarm: fault code {fm.get('fault_code', 'FAULT')} — {fm.get('name', 'fault')}. "
                f"The control room operator observed {fm.get('symptoms', ['abnormal sensor readings'])[0] if fm.get('symptoms') else 'abnormal sensor readings'}. "
                f"The equipment was placed on hold pending maintenance assessment."
            ),
            "sensor_temp_c": temp,
            "sensor_temp_threshold_c": normal_temp,
            "sensor_vib_mm_s": vib,
            "sensor_vib_threshold_mm_s": normal_vib,
            "sensor_pres_bar": pres,
            "sensor_pres_normal_bar": f"{fam_data.get('sensor_ranges', {}).get('pressure_bar', {}).get('normal_min', 3.0)}–{normal_pres}",
            "narrative_immediate_response": (
                "Standard incident response protocol was activated. The shift supervisor "
                "assumed incident command and coordinated maintenance and operations teams."
            ),
            "immediate_actions": immediate_actions,
            "stoppage_hours": stoppage_hours,
            "affected_units": self.rng.randint(1, 5),
            "production_loss_inr": stoppage_hours * 75_000,
            "narrative_preliminary_cause": (
                f"Preliminary assessment indicates {fm.get('name', 'fault condition')}. "
                f"Root cause investigation per FAR procedure to follow within 5 working days."
            ),
            "fault_code": fm.get("fault_code", "FAULT"),
            "assigned_team": f"Mechanical Maintenance — {plant_area}",
            "current_status": self.rng.choice(["Under Repair", "Repaired — awaiting clearance",
                                               "Returned to service"]),
            "eta_return": (ts + timedelta(hours=stoppage_hours)).strftime("%Y-%m-%d %H:%M"),
            "logged_at": ts.strftime("%Y-%m-%d %H:%M:%S"),
        }

        content = render_template(TemplateType.INCIDENT_SUMMARY, vars_dict)

        return GeneratedDoc(
            doc_id=f"INC-{family[:3].upper()}-{seq:04d}",
            doc_type="incident_summary",
            title=f"Incident Summary — {eq_id} {ts.strftime('%Y-%m-%d')}",
            asset_id=eq_id,
            asset_family=family,
            equipment_class=fam_data["iso14224_class"],
            plant_area=plant_area,
            content_markdown=content,
            content_json=vars_dict,
            failure_modes_referenced=[fm.get("name", "")],
            fault_codes_referenced=[fm.get("fault_code", "")],
            revision="N/A",
            applicable_equipment_classes=[fam_data["iso14224_class"]],
        )

    def _gen_spare_parts_record(
        self, family: str, scenario: str, seq: int
    ) -> Optional[GeneratedDoc]:
        catalog = ONTOLOGY.get("spare_parts_catalog", [])
        if not catalog:
            return None

        # Rotate through catalog parts
        part = catalog[seq % len(catalog)]
        families = part.get("compatible_families", [family])
        family = families[0] if families else family

        try:
            fam_data = ONTOLOGY["asset_families"][family]
        except KeyError:
            fam_data = ONTOLOGY["asset_families"][self._families[0]]

        ts = self.ff.timestamp_recent()

        # Build usage history
        usage_history = [
            type("U", (), {
                "month": (ts - timedelta(days=30 * i)).strftime("%Y-%m"),
                "qty": self.rng.randint(0, 3),
                "work_orders": f"WO-{self.rng.randint(10000, 99999)}",
            })()
            for i in range(6)
        ]

        stock_qty = part.get("stock_qty", 0)
        min_stock = part.get("min_stock_qty", 1)
        lead_days = part.get("lead_time_days", 7)

        vars_dict: dict[str, Any] = {
            "part_number": part.get("part_number", f"PART-{seq:04d}"),
            "catalog_seq": self.ff.catalog_seq(),
            "last_updated": ts.strftime("%Y-%m-%d"),
            "part_name": part.get("part_name", "Generic Part"),
            "manufacturer": part.get("supplier", "Unknown").split(",")[0].strip(),
            "mfr_part_number": part.get("part_number", "N/A"),
            "material": self.rng.choice(["Steel", "Cast Iron", "SS316", "Polyurethane", "Bronze"]),
            "weight_kg": round(self.rng.uniform(0.5, 25.0), 2),
            "compatible_equipment": part.get("compatible_families", [family]),
            "function_class": fam_data.get("iso14224_class", "rotating.general"),
            "supplier": part.get("supplier", "TBD"),
            "supplier_contact": f"+91-{self.rng.randint(70000, 99999)}{self.rng.randint(10000, 99999)}",
            "unit_cost_inr": part.get("unit_cost_inr", 5000),
            "lead_time_days": lead_days,
            "criticality_override": part.get("criticality_override", "standard"),
            "payment_terms": "30 days net",
            "stock_qty": stock_qty,
            "min_stock_qty": min_stock,
            "storage_location": f"Store-{self.rng.choice(['A', 'B', 'C'])}-{self.rng.randint(1, 20):02d}",
            "storage_conditions": "Dry, covered, ambient temp 15–40°C, RH < 70%",
            "shelf_life": self.rng.choice(["5 years", "Indefinite", "3 years", "10 years"]),
            "usage_history": usage_history,
            "narrative_installation_notes": (
                f"Install as per equipment OEM manual. Apply anti-seize compound to fasteners. "
                f"Verify part number match before installation. "
                f"{'WARNING: ZERO STOCK — raise purchase order immediately.' if stock_qty == 0 else ''}"
            ),
            "catalog_manager": self.ff.person_name(),
            "approver_name": self.ff.person_name(),
        }

        content = render_template(TemplateType.SPARE_PARTS_RECORD, vars_dict)

        eq_ids = fam_data.get("equipment_ids", ["EQP-01"])

        return GeneratedDoc(
            doc_id=f"SPC-{seq:04d}",
            doc_type="spare_parts_record",
            title=f"Spare Parts Record — {part.get('part_name', 'Part')}",
            asset_id=self.rng.choice(eq_ids),
            asset_family=family,
            equipment_class=fam_data.get("iso14224_class", "general"),
            plant_area=self.ff.plant_area(family),
            content_markdown=content,
            content_json=vars_dict,
            failure_modes_referenced=[],
            fault_codes_referenced=[],
            revision=ts.strftime("%Y-Q%m"),
            applicable_equipment_classes=part.get("compatible_families", [family]),
        )

    # ------------------------------------------------------------------
    # LLM ELABORATION (gated)
    # ------------------------------------------------------------------

    def _llm_elaborate(self, doc: GeneratedDoc) -> GeneratedDoc:
        """
        Call LLM to enrich narrative fields in the document using Instructor
        for validated structured output.
        Falls back gracefully on error (or when use_llm=False). Requires
        litellm + instructor + a valid API key.
        """
        try:
            import instructor
            import litellm
            from pydantic import BaseModel as _BaseModel
            from wizard.core.config import settings as _settings

            class _ElaboratedDoc(_BaseModel):
                """Instructor response model — validated structured output."""
                improved_markdown: str

            prompt = (
                f"You are a steel plant reliability engineer. Enrich the following "
                f"synthetic maintenance document to sound more realistic and specific. "
                f"Keep all field values, IDs, and fault codes EXACTLY as they are. "
                f"Only improve the narrative text sections. Return the full improved "
                f"document text in the improved_markdown field.\n\n"
                f"DOCUMENT:\n{doc.content_markdown[:3000]}"
            )

            # Patch litellm client with Instructor for structured / validated output
            client = instructor.from_litellm(litellm.completion)
            result: _ElaboratedDoc = client.chat.completions.create(
                model=_settings.llm_model_light,
                response_model=_ElaboratedDoc,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2000,
                temperature=0.7,
                timeout=30,
            )
            if result.improved_markdown and len(result.improved_markdown) > 100:
                doc.content_markdown = result.improved_markdown
                self.stats.llm_elaborated += 1
        except Exception as exc:
            log.debug("LLM elaboration skipped for %s: %s", doc.doc_id, exc)
        return doc

    # ------------------------------------------------------------------
    # PERSISTENCE
    # ------------------------------------------------------------------

    def _save_doc(self, doc: GeneratedDoc) -> None:
        """Save document as JSON + Markdown files."""
        # JSON
        json_path = self.docs_dir / f"{doc.doc_id}.json"
        meta = {
            "doc_id": doc.doc_id,
            "doc_type": doc.doc_type,
            "title": doc.title,
            "asset_id": doc.asset_id,
            "asset_family": doc.asset_family,
            "equipment_class": doc.equipment_class,
            "plant_area": doc.plant_area,
            "failure_modes_referenced": doc.failure_modes_referenced,
            "fault_codes_referenced": doc.fault_codes_referenced,
            "revision": doc.revision,
            "has_noise": doc.has_noise,
            "doc_hash": doc.doc_hash,
            "applicable_equipment_classes": doc.applicable_equipment_classes,
            "content_markdown": doc.content_markdown,
        }
        json_path.write_text(json.dumps(meta, indent=2, default=str), encoding="utf-8")

        # Markdown
        md_path = self.docs_dir / f"{doc.doc_id}.md"
        md_path.write_text(doc.content_markdown, encoding="utf-8")

        # Add to metadata index
        self._metadata_index.append({
            "doc_id": doc.doc_id,
            "doc_type": doc.doc_type,
            "title": doc.title,
            "asset_id": doc.asset_id,
            "asset_family": doc.asset_family,
            "equipment_class": doc.equipment_class,
            "plant_area": doc.plant_area,
            "failure_modes_referenced": doc.failure_modes_referenced,
            "fault_codes_referenced": doc.fault_codes_referenced,
            "revision": doc.revision,
            "has_noise": doc.has_noise,
            "doc_hash": doc.doc_hash,
            "applicable_equipment_classes": doc.applicable_equipment_classes,
        })

    def _save_metadata_index(self) -> None:
        idx_path = self.output_dir / "metadata_index.json"
        idx_path.write_text(
            json.dumps(
                {
                    "generated_at": datetime.utcnow().isoformat(),
                    "total_docs": len(self._metadata_index),
                    "stats": {
                        "total_attempted": self.stats.total_attempted,
                        "total_generated": self.stats.total_generated,
                        "deduped_out": self.stats.deduped_out,
                        "noise_injected": self.stats.noise_injected,
                        "llm_elaborated": self.stats.llm_elaborated,
                        "by_type": self.stats.by_type,
                    },
                    "documents": self._metadata_index,
                },
                indent=2, default=str,
            ),
            encoding="utf-8",
        )
        log.info("Metadata index saved: %s (%d docs)", idx_path, len(self._metadata_index))

    def _build_and_save_artifacts(self) -> None:
        """Build FMEA graph + save ontology JSON."""
        # Honor output_dir: write to <output_dir>/kg/ (or _REPO_ROOT/data/kg/ as default)
        if self.output_dir != (_REPO_ROOT / "data" / "synthetic"):
            kg_dir = self.output_dir / "kg"
        else:
            kg_dir = _REPO_ROOT / "data" / "kg"
        kg_dir.mkdir(parents=True, exist_ok=True)

        # Save ontology
        save_ontology(kg_dir / "steel_plant_ontology.json")
        log.info("Ontology saved: %s", kg_dir / "steel_plant_ontology.json")

        # Build and save FMEA graph
        G = build_fmea_graph()
        save_fmea_graph(G, kg_dir / "steel_plant_fmea.json")
        log.info("FMEA graph saved: %d nodes, %d edges → %s",
                 G.number_of_nodes(), G.number_of_edges(),
                 kg_dir / "steel_plant_fmea.json")

    def _persist_entities(self) -> None:
        """Write KnowledgeDocument, SparePart, MaintenanceRecord, FaultLog to DB."""
        if not _HAS_CORE:
            log.info("Core not available — skipping entity persistence")
            return

        quarantine_path = _REPO_ROOT / "data" / "quarantine"
        quarantine_path.mkdir(parents=True, exist_ok=True)
        quarantine_file = quarantine_path / "invalid_entities.jsonl"

        try:
            init_db()
        except Exception as exc:
            log.warning("DB init failed — skipping persistence: %s", exc)
            return

        with session_scope() as session:
            for doc in self._all_docs:
                self._persist_one_doc(doc, session, quarantine_file)

        log.info("Entities persisted: %d, quarantined: %d",
                 self.stats.entities_persisted, self.stats.quarantined)

    def _persist_one_doc(self, doc: GeneratedDoc, session: Any, qfile: Path) -> None:
        """Persist entity for a single generated doc."""
        try:
            if doc.doc_type in ("manual", "sop", "failure_analysis", "incident_summary"):
                raw = {
                    "entity_type": "knowledge_doc",
                    "asset_id": doc.asset_id,
                    "plant_area": doc.plant_area,
                    "source_system": "generated",
                    "doc_type": doc.doc_type,
                    "title": doc.title,
                    "section": "",
                    "content_markdown": doc.content_markdown[:2000],  # truncate for DB
                    "revision": doc.revision,
                    "applicable_equipment_classes": doc.applicable_equipment_classes,
                }
                entity = ingest_entity(raw)
                session.add(entity)
                self.stats.entities_persisted += 1

            elif doc.doc_type == "spare_parts_record":
                jv = doc.content_json
                raw = {
                    "entity_type": "spare_part",
                    "asset_id": doc.asset_id,
                    "plant_area": doc.plant_area,
                    "source_system": "generated",
                    "part_number": jv.get("part_number", doc.doc_id),
                    "part_name": jv.get("part_name", ""),
                    "compatible_equipment": jv.get("compatible_equipment", []),
                    "stock_qty": jv.get("stock_qty", 0),
                    "min_stock_qty": jv.get("min_stock_qty", 1),
                    "unit_cost_inr": float(jv.get("unit_cost_inr", 0.0)),
                    "lead_time_days": jv.get("lead_time_days", 7),
                    "supplier": str(jv.get("supplier", "")),
                    "criticality_override": jv.get("criticality_override", "standard"),
                }
                entity = ingest_entity(raw)
                session.add(entity)
                self.stats.entities_persisted += 1

            elif doc.doc_type == "maintenance_record":
                jv = doc.content_json
                raw = {
                    "entity_type": "maintenance_record",
                    "asset_id": doc.asset_id,
                    "plant_area": doc.plant_area,
                    "source_system": "generated",
                    "work_order_id": jv.get("work_order_id", ""),
                    "maintenance_type": jv.get("maintenance_type", "preventive").lower(),
                    "description": jv.get("narrative_work_description", ""),
                    "technician_id": jv.get("technician_id", ""),
                    "outcome": jv.get("outcome", "resolved").lower(),
                    "rca_summary": jv.get("narrative_findings", ""),
                    "parts_used": [
                        p.part_number for p in jv.get("parts_consumed", [])
                        if hasattr(p, "part_number")
                    ],
                }
                entity = ingest_entity(raw)
                session.add(entity)
                self.stats.entities_persisted += 1

                # Also emit a FaultLog for each fault code referenced
                for fcode in doc.fault_codes_referenced:
                    if fcode:
                        fault_raw = {
                            "entity_type": "fault_log",
                            "asset_id": doc.asset_id,
                            "plant_area": doc.plant_area,
                            "source_system": "generated",
                            "fault_code": fcode,
                            "fault_description": doc.title,
                            "severity": jv.get("severity", "medium").lower(),
                            "source": "operator",
                            "confirmed": True,
                        }
                        fault_entity = ingest_entity(fault_raw)
                        session.add(fault_entity)
                        self.stats.entities_persisted += 1

            session.commit()

        except Exception as exc:
            session.rollback()
            qr = QuarantineRecord(
                raw_payload={"doc_id": doc.doc_id, "doc_type": doc.doc_type},
                validation_error=str(exc),
            )
            with qfile.open("a", encoding="utf-8") as f:
                f.write(qr.model_dump_json() + "\n")
            self.stats.quarantined += 1

    # ------------------------------------------------------------------
    # DISTRIBUTION SCALING
    # ------------------------------------------------------------------

    def _scale_distribution(self, total: int) -> dict[TemplateType, int]:
        base_total = sum(self._DISTRIBUTION.values())  # 500
        scaled = {}
        allocated = 0
        types = list(self._DISTRIBUTION.keys())
        for t in types[:-1]:
            n = max(1, round(self._DISTRIBUTION[t] / base_total * total))
            scaled[t] = n
            allocated += n
        # Last type gets the remainder
        scaled[types[-1]] = max(1, total - allocated)
        return scaled


# ===========================================================================
# UNIT HELPER
# ===========================================================================

def _unit_for(key: str) -> str:
    """Return a unit string for a design parameter key."""
    unit_map = {
        "rated_rpm": "RPM", "rpm": "RPM",
        "rated_flow_m3h": "m³/h", "flow_m3h": "m³/h",
        "rated_pressure_bar": "bar", "pressure_bar": "bar",
        "motor_power_kw": "kW", "power_kw": "kW",
        "rated_head_m": "m",
        "system_pressure_bar": "bar",
        "reservoir_volume_l": "L",
        "pump_rated_flow_l_min": "L/min",
        "filter_micron_rating": "μm",
        "belt_width_mm": "mm",
        "drive_roller_diameter_mm": "mm",
        "roller_pitch_mm": "mm",
        "max_strip_temp_c": "°C",
        "max_strip_weight_t": "t",
        "drive_power_kw_per_roller": "kW/roller",
        "relubrication_interval_hours": "h",
        "radial_load_capacity_kn": "kN",
        "axial_load_capacity_kn": "kN",
    }
    for k, u in unit_map.items():
        if k in key:
            return u
    return "—"


# ===========================================================================
# CLI ENTRY POINT
# ===========================================================================

def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate synthetic steel-plant knowledge base",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--count", type=int, default=500,
        help="Total number of documents to generate",
    )
    parser.add_argument(
        "--seed", type=int, default=42,
        help="Random seed for reproducibility",
    )
    parser.add_argument(
        "--use-llm", action="store_true", default=False,
        help="Enable LLM elaboration of narrative fields (requires API key)",
    )
    parser.add_argument(
        "--noise-fraction", type=float, default=0.15,
        help="Fraction of maintenance logs with injected noise (0.0–1.0)",
    )
    parser.add_argument(
        "--output-dir", type=Path, default=None,
        help="Output directory (default: data/synthetic/)",
    )
    args = parser.parse_args()

    gen = KnowledgeBaseGenerator(
        seed=args.seed,
        noise_fraction=args.noise_fraction,
        use_llm=args.use_llm,
        output_dir=args.output_dir,
    )
    docs = gen.run(total=args.count)
    print(f"\nGenerated {len(docs)} documents.")
    print(f"  By type: {gen.stats.by_type}")
    print(f"  Noise injected: {gen.stats.noise_injected}")
    print(f"  LLM elaborated: {gen.stats.llm_elaborated}")
    print(f"  Deduped out: {gen.stats.deduped_out}")
    print(f"  Entities persisted: {gen.stats.entities_persisted}")


if __name__ == "__main__":
    main()
