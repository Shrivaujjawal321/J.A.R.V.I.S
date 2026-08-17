# wizard.knowledge — Steel-Plant ISO-14224 Knowledge Layer

Owner: knowledge-synth agent
Status: Complete

## What This Module Does

Three deliverables packaged as one importable sub-package:

### (a) Steel-Plant ISO-14224 Ontology (`ontology.py`)
JSON-serializable dict covering 5 asset families:
- Blast Furnace Fans
- Centrifugal Pumps
- Roller/Conveyor Bearings
- Hydraulic Power Units
- Hot Strip Mill Conveyors

Each family includes: subsystems, failure modes (fault code, severity, ISO 14224 code,
symptoms, root causes, corrective actions, MTBF), error code dictionary, sensor ranges
(normal/warning/critical for temperature, pressure, vibration, RPM, current), and spare
parts catalog. The `demo_asset` block encodes the EAF-04 scripted failure scenario
(BF-BRG-002 bearing overheating, BRG-SKF-6310-2RS1 out-of-stock, 14-day lead time).

### (b) Synthetic KB Generator (`generator.py`)
Generates ~500 documents across 6 types via a 4-stage pipeline:
1. Ontology seed → equipment-specific, grounded context
2. Faker + Mimesis → deterministic structured fields (timestamps, IDs, names)
3. Jinja2 templates → structural document rendering
4. LLM elaboration (optional, `--use-llm` flag) → richer narratives via LiteLLM

Quality gates:
- 15-20% noise injection in maintenance logs (6 noise categories per arXiv:2511.05311)
- Cosine-similarity dedup gate (< 0.85 threshold, sentence-transformers/all-MiniLM-L6-v2)
  — falls back to hash dedup if sentence-transformers unavailable
- Pydantic v2 validation on all emitted entities before DB write

Emits entities to `wizard.db`:
- `KnowledgeDocument` (manuals, SOPs, failure analyses, incident summaries)
- `SparePart` (catalog entries with stock/lead-time data)
- `MaintenanceRecord` (maintenance logs)
- `FaultLog` (fault events extracted from logs)

Includes at least 2 out-of-stock critical spares with 14-day lead time scenarios
(BRG-SKF-6310-2RS1 for BF fans; KIT-HPU-RBL-001 for HPU pump overhaul).

### (c) FMEA NetworkX DiGraph (`fmea_graph.py`)
Hand-authored ISO-14224 FMEA graph (~200-350 nodes, ~300-500 edges).

Node types: EquipmentFamily → EquipmentUnit → Subsystem → Component →
FailureMode → RootCause → Effect → Action → SparePart → SOPReference → Sensor

Edge types: HAS_UNIT, HAS_SUBSYSTEM, HAS_COMPONENT, CAN_FAIL_AS, CAUSED_BY,
LEADS_TO, DETECTED_BY, RESOLVED_BY, REQUIRES_PART, FOLLOWS_SOP

Powers RCA Layer-1 (deterministic graph traversal). The `get_rca_path(G, fault_code)`
function returns a structured evidence chain for any fault code.

Serialized to `data/kg/steel_plant_fmea.json` (NetworkX node_link_data format).

## Integration Contract

```python
# Used by wizard.rag and wizard.agents:
from wizard.knowledge import (
    ONTOLOGY,           # dict — full ontology for grounding
    get_ontology,       # () -> dict
    save_ontology,      # (path: Path) -> None
    build_fmea_graph,   # () -> nx.DiGraph
    save_fmea_graph,    # (G, path) -> None
    load_fmea_graph,    # (path) -> nx.DiGraph
    get_rca_path,       # (G, fault_code: str) -> dict
    TemplateType,       # enum of 6 document types
    render_template,    # (type, vars_dict) -> str
)

# CLI generation:
from wizard.knowledge.generator import KnowledgeBaseGenerator

gen = KnowledgeBaseGenerator(seed=42, use_llm=False)
docs = gen.run(total=500)

# Or from command line:
python -m wizard.knowledge.generator --count 500 --seed 42
python -m wizard.knowledge.generator --count 500 --use-llm --seed 42
```

## Outputs

| Path | Description |
|---|---|
| `data/synthetic/docs/*.json` | Per-document JSON (content + metadata) |
| `data/synthetic/docs/*.md` | Per-document Markdown (for RAG chunking) |
| `data/synthetic/metadata_index.json` | Document index with fault codes, types, hashes |
| `data/kg/steel_plant_ontology.json` | Raw ontology JSON |
| `data/kg/steel_plant_fmea.json` | FMEA DiGraph (NetworkX node_link_data) |

## Smoke Test

```bash
cd /path/to/maintenance-wizard
python -m wizard.knowledge.smoke_knowledge
```

Expected: all checks PASS. Runs in <30 seconds offline.

## Dependencies

All from requirements.txt. No heavy installs needed for offline/template mode:
- `networkx>=3.3` — graph library
- `jinja2>=3.1.4` — template rendering
- `faker>=26.0.0` — deterministic fake data
- `mimesis>=18.0.0` — fast structured fake data
- `sentence-transformers>=3.0.0` — dedup gate (optional; degrades to hash dedup)

For LLM mode (`--use-llm`):
- `litellm>=1.45.5` — LLM gateway
- Valid `GEMINI_API_KEY` or `OPENAI_API_KEY` in `.env`
