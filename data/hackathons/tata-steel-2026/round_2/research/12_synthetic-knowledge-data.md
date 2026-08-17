# Component 12: Synthetic Steel-Plant Knowledge-Data Generation

**Maintenance Wizard — Tata Steel AI Hackathon 2026, Round 2**
**Research date:** 2026-06-06

---

## 1. Recommended Approach

**Layered Template + LLM Elaboration Pipeline with Instructor + Pydantic v2, seeded by a curated Steel-Domain Ontology, validated by a self-consistency judge pass.**

The pipeline works in four stages:

1. **Ontology seed layer** — hand-author a compact JSON ontology (~200 lines) covering 5 steel-plant asset families (blast-furnace fans, centrifugal pumps, roller/conveyor bearings, hydraulic power units, hot-strip-mill conveyors), their subsystems, ~30 failure modes per asset, ~15 error codes per asset, and maintenance action taxonomy. This is the domain-grounding anchor that prevents hallucinated sensor ranges and fictional part numbers.

2. **Jinja2 skeleton templates** — for each document type (Equipment Manual section, SOP, Maintenance Log entry, Failure Analysis Report, Incident Summary, Spare Parts record), author a structural skeleton with typed variable slots (e.g., `{{ equipment_id }}`, `{{ fault_code }}`, `{{ temperature_reading_degC }}`). Faker + Mimesis fill deterministic fields (timestamps, IDs, part numbers, personnel names). This guarantees structural variety without LLM cost on every field.

3. **LLM elaboration via Instructor 1.8+ / Pydantic v2** — an LLM (GPT-4o-mini or local Llama-3.1-8B-Instruct via Ollama) takes the skeleton + ontology context and fills the free-text narrative sections (RCA paragraph, corrective action narrative, symptom description). Instructor enforces the output schema; Pydantic v2 validates ranges (temperature within plausible bounds, RUL > 0, fault severity in {low, medium, high, critical}).

4. **Quality + diversity gate** — a self-consistency judge pass (second LLM call, same model) checks three things: (a) no hallucinated equipment models inconsistent with the ontology, (b) no repeated boilerplate across the batch (embedding cosine similarity < 0.85 between any two documents of same type), (c) all referenced spare part numbers exist in the generated spare-parts catalog. Documents failing any gate are regenerated with temperature = 1.2 (higher diversity).

Target corpus size: ~500 documents across 6 types, generated in under 15 minutes on a laptop using GPT-4o-mini. At ~$0.002/1K output tokens, estimated cost under $3 total.

---

## 2. Why This Approach Wins

### Grounded Realism via Ontology Seeding

Research on LLM-based industrial SOP generation (chemengconsulting.com, Feb 2025) demonstrates that the single biggest differentiator between generic and realistic industrial documents is specificity: CAS numbers, precise tolerances (`±0.1g`), named control-point thresholds (`"If hydraulic pressure drops below 180 bar, isolate pump and notify shift supervisor"`), and equipment-specific identifiers. None of this emerges naturally from a plain LLM prompt — it requires a grounding anchor. The ontology seed layer provides exactly this: the LLM can only reference failure modes and error codes that actually exist in the steel domain ontology, eliminating hallucinated sensor ranges or fictional equipment models.

### Instructor + Pydantic v2 for Schema-Enforced Generation

Instructor (1.8.1, PyPI 2025) is the dominant structured-output library with 3M+ monthly downloads and official support for OpenAI, Anthropic, and Ollama backends. It guarantees the LLM cannot produce a maintenance log with a missing `equipment_id` or a temperature outside the defined range. This is non-negotiable for a demo: a judge who asks the system to fetch a maintenance log and gets a malformed JSON will immediately mark the system as "breaks." Pydantic v2 validation catches type errors before they reach the RAG index.

### Controlled Noise for Realistic Log Diversity

Research from "Cleaning Maintenance Logs with LLM Agents" (arXiv:2511.05311, Nov 2025) formalizes six noise categories observed in real industrial maintenance logs: identifier misalignment, out-of-fleet references, invalid values/typos, missing values, test-system entries, and date inconsistencies. Injecting controlled noise into 15–20% of generated maintenance logs makes the corpus realistic — a system that only ever sees clean logs will fail on real data. The AgenticPdmDataCleaner framework (open-source, GitHub) provides the exact noise injection code, adapted here for steel-plant fields instead of automotive.

### Jinja2 Skeletons Separate Structure from Cost

Every LLM call on boilerplate fields (timestamp formatting, part number generation, shift-rotation names) wastes tokens and money. Jinja2 templates with Faker/Mimesis filling structural slots reduce LLM elaboration to only the narrative sections that require domain reasoning. Mimesis 19.0 is ~12x faster than Faker for high-volume deterministic generation and provides a Schema API for nested structured objects — ideal for generating 500 spare-parts records.

### Self-Consistency Quality Gate Prevents Batch Drift

In a 9-day solo build, there is no human reviewer for 500 synthetic documents. The automated quality gate (embedding cosine similarity check + ontology cross-reference) is the engineering substitute. Without it, the LLM tends to converge on 3–4 templates after 50 documents, producing a corpus that looks diverse but causes RAG recall to cluster unhelpfully. The threshold of < 0.85 cosine similarity (using `sentence-transformers/all-MiniLM-L6-v2`, which runs CPU-only in ~50ms/doc) is empirically calibrated from FineWeb-Edu's deduplication research (2025).

---

## 3. Exact Stack

| Library/Tool | Version | Role |
|---|---|---|
| `instructor` | 1.8.1 | Structured LLM output enforcement, retry logic, Pydantic integration |
| `pydantic` | 2.7.x | Schema definition and field-level validation for all document types |
| `jinja2` | 3.1.x | Skeleton templates for each document type; variable slot injection |
| `faker` | 26.x | Deterministic field generation: timestamps, names, work-order IDs |
| `mimesis` | 19.0 | Fast structured fake data for spare-parts catalog, equipment IDs, serial numbers |
| `sentence-transformers` | 3.x | `all-MiniLM-L6-v2` CPU-only embeddings for deduplication cosine check |
| `openai` | 1.x (SDK) | GPT-4o-mini backend for LLM elaboration (primary, API-based) |
| `ollama` | 0.3.x (Python client) | Local Llama-3.1-8B-Instruct fallback for offline/judge-machine scenarios |
| `ragas` | 0.2.x | Optional: auto-generate QA pairs grounded to the synthetic docs for RAG evaluation |
| Python | 3.11+ | Runtime; all above install via `pip install` |

No Docker required. No GPU required. Full `pip install instructor pydantic jinja2 faker mimesis sentence-transformers openai ragas` on a cold machine in under 2 minutes.

---

## 4. Alternatives Considered

### Alternative A: Pure-LLM "Generate me 500 maintenance logs" Prompt
**Why it loses:** Without an ontology seed or template scaffold, the LLM produces stylistically similar documents after ~20 outputs. Diversity collapses. The model invents plausible-sounding but internally inconsistent equipment models (e.g., "BF-3 Fan Motor Model X900" on page 1, "Fan Motor X-900A" on page 3 — the RAG index treats these as different entities). No validation means malformed outputs silently enter the corpus. This is the 2022-tier approach.

### Alternative B: Real-World Web-Scraped Industrial Documents
**Why it loses:** Virtually no public steel-plant manuals or maintenance SOPs exist at the required specificity. General industrial maintenance docs (ISO 13374, IEC 61511 references) are too abstract for a steel-specific RAG system. Scraping what little exists produces a corpus of ~20–30 documents — insufficient for meaningful retrieval diversity. Worse, the judge machine cannot verify license compliance on scraped documents, adding legal risk.

### Alternative C: SDV (Synthetic Data Vault) / GANs for Tabular Data Only
**Why it loses:** SDV and GAN-based synthesizers (CTGAN, TVAE) are excellent for tabular sensor records but cannot generate free-text narrative fields — the RCA paragraph, symptom description, corrective action narrative that the RAG system must retrieve. A hybrid approach using SDV for sensor tables and pure LLM for narratives with no schema enforcement produces a split corpus with mismatched schemas across document types.

### Alternative D: Distilabel / Augmentoolkit Pipeline
**Why it loses as primary (but valid as secondary):** Distilabel (argilla-io, 2025) and Augmentoolkit are powerful pipelines for converting raw text into fine-tuning datasets and QA pairs. However, they require an existing document corpus as input — they amplify, not originate. Since there is no real steel corpus, these tools have no input to process. They are useful as a **secondary step** after the primary synthetic corpus is generated: run Augmentoolkit on the 500 generated docs to produce QA pairs for RAG evaluation and potential fine-tuning data.

---

## 5. Anti-Patterns — What Screams "Amateur / 2022-tier"

- **Asking ChatGPT to write "10 maintenance logs" in a single chat turn and copy-pasting the output.** The resulting documents have identical structure (same paragraph order, same phrasing patterns, same fictional equipment names). A judge who runs a similarity check or reads 3 documents will notice immediately.

- **No schema validation on generated documents.** Maintenance logs with `temperature: "hot"` instead of `temperature: 92.3` (°C), or `timestamp: "yesterday"` instead of ISO-8601 — these break any downstream pipeline that tries to parse them.

- **Generic industrial language with no steel-plant specificity.** Terms like "the machine overheated" instead of "BF-2 auxiliary blast air fan measured 142°C at bearing housing T3, exceeding SOP-BF-AF-07 threshold of 120°C." The former is useless for RAG; the latter enables precise retrieval.

- **No noise injection in maintenance logs.** Real logs have typos, missing fields, date inconsistencies. A corpus of 500 perfectly formatted logs looks synthetic and doesn't test the system's robustness to real-world data quality issues.

- **Inventing failure modes without grounding.** Steel plant equipment has specific, well-documented failure taxonomy (ISO 14224 RCM taxonomy for rotating equipment). Generating failure modes from raw LLM imagination produces physically implausible descriptions that a domain expert (judge) will immediately flag.

- **Reusing the same failure mode description across multiple pieces of equipment.** "Bearing wear due to lubrication failure" appearing identically in a blast-furnace fan log AND a hydraulic pump log AND a conveyor bearing log signals zero domain awareness.

---

## 6. Integration Notes

### Inputs Consumed
- The steel-domain ontology JSON (authored once, ~200 lines; describes equipment families, subsystems, failure modes, error codes, sensor ranges, maintenance action taxonomy, spare parts catalog structure)
- Jinja2 template files, one per document type (6 templates total)
- LLM API key (OpenAI) or local Ollama endpoint

### Outputs Produced
- **500 synthetic documents** in structured JSON + plain-text (Markdown/plain) dual format:
  - ~100 Equipment Manual sections (one per subsystem across 5 asset families)
  - ~100 Maintenance SOPs (procedure-level, with step-by-step actions and safety precautions)
  - ~150 Maintenance Log entries (with controlled noise in ~20%)
  - ~80 Failure Analysis Reports (RCA format: timeline, probable causes, contributing factors)
  - ~40 Incident/Breakdown Summaries (event narrative format)
  - ~30 Spare Parts records (availability, lead time, minimum stock levels)
- **Metadata index** (JSON) mapping each document to: equipment ID, asset family, document type, failure mode(s) referenced, timestamp range, document hash (for dedup tracking)
- **RAGAS-compatible QA test set** (~200 QA pairs grounded to the synthetic corpus, for RAG component evaluation)

### Components This Talks To
- **Component 4 (RAG Architecture)** — The 500 synthetic documents are the primary knowledge corpus ingested into the vector store. The dual JSON+plain-text format ensures the embedding component can process cleanly.
- **Component 7 (Embeddings + VectorStore)** — Chunk strategy should be coordinated: SOP steps (numbered lists) chunk naturally at step boundaries; Manual sections at H2/H3 boundaries; Logs as atomic records.
- **Component 6 (Explainability + Traceability)** — The metadata index enables source attribution: when the RAG system cites a finding, it can point to the specific synthetic document title, section, and timestamp, satisfying the "traceable to input data" requirement.
- **Component 9 (Anomaly Detection)** and **Component 10 (Failure Prediction)** — Failure Analysis Reports and Incident Summaries provide historical failure context that these components use for pattern matching and few-shot examples.
- **Component 5 (GraphRAG / Knowledge Graph)** — The ontology JSON is the direct input for building the entity graph: equipment → subsystem → component → failure mode → maintenance action nodes and edges.

### Generation Script Architecture
```
scripts/
  generate_knowledge_base.py   # main orchestrator
  ontology/
    steel_plant_ontology.json  # domain seed
  templates/
    equipment_manual.j2
    maintenance_sop.j2
    maintenance_log.j2
    failure_analysis_report.j2
    incident_summary.j2
    spare_parts_record.j2
  schemas/
    document_schemas.py        # Pydantic v2 models
  output/
    synthetic_kb/              # generated corpus
    metadata_index.json
    qa_testset.json
```

One command: `python scripts/generate_knowledge_base.py --count 500 --seed 42 --backend openai`

---

## 7. Open Risks / Unknowns

**Risk 1: LLM API Rate Limits During Generation**
Generating 500 documents with GPT-4o-mini at ~800 tokens per elaboration = ~400K tokens. At 500K TPM rate limit (Tier-1 OpenAI), this runs in ~1 minute. At free-tier (60 RPM), it takes ~8 minutes. Risk: judge machine may not have API access. **Mitigation:** pre-generate the corpus locally before submission; include the generated files in the ZIP. Also include the Ollama local-model fallback path in the script.

**Risk 2: Ontology Accuracy — Steel-Plant Failure Modes May Be Physically Incorrect** [unverified]
The ontology will be authored by prompting an LLM with references to publicly available sources (ISO 14224 for rotating equipment reliability taxonomy, general blast-furnace operation references). However, actual Tata Steel-specific failure codes and sensor thresholds are proprietary. The generated corpus may contain plausible but not precisely accurate engineering parameters. **Mitigation:** frame the ontology as "representative of a typical integrated steel plant" and document this assumption clearly. Judges are evaluating the system architecture, not the accuracy of synthetic sensor threshold values.

**Risk 3: Corpus Diversity Collapse at Scale**
At 500 documents, even with diversity gating, the LLM may converge on ~10 structural patterns. **Mitigation:** implement 5 ontology "scenarios" (normal operation, degradation onset, acute failure, post-repair, seasonal maintenance) and distribute generation evenly across them; seed the quality gate with at-least-50%-new-sentences check per document.

**Risk 4: Deduplication Threshold Calibration** [unverified]
The 0.85 cosine similarity threshold for `all-MiniLM-L6-v2` is adapted from web-crawl deduplication research. For short maintenance log entries (200–400 words), this threshold may be too permissive. **Mitigation:** run a pilot generation of 50 docs, plot the similarity distribution, adjust threshold empirically before full generation run.

**Risk 5: RAGAS QA Pair Groundedness**
RAGAS `TestsetGenerator` produces QA pairs by evolving questions from source documents — but if the source documents are themselves LLM-generated, there is a risk of circularity (model grades its own output). **Mitigation:** use the QA pairs only for retrieval evaluation (does the RAG system return the right chunk?), not for answer quality evaluation.

---

## References

- [SOP-Bench: Complex Industrial SOPs for Evaluating LLM Agents (arXiv, Jun 2025)](https://arxiv.org/html/2506.08119v1)
- [Cleaning Maintenance Logs with LLM Agents for Improved Predictive Maintenance (arXiv:2511.05311, Nov 2025)](https://arxiv.org/html/2511.05311v1)
- [Instructor — Structured LLM Outputs (useinstructor.com)](https://python.useinstructor.com/)
- [Mimesis 19.0 Docs — Schema API](https://mimesis.name/)
- [Synthetic Data for RAG: Safe Generation, Deduplication and Drift-Aware Curation (DEV Community, 2025)](https://dev.to/kuldeep_paul/synthetic-data-for-rag-safe-generation-deduplication-and-drift-aware-curation-in-2025-3298)
- [RAGAS Testset Generation Docs](https://docs.ragas.io/en/stable/getstarted/rag_testset_generation/)
- [What Makes LLMs Effective for Chemical Industry SOP Generation? (ChemEngConsulting, Feb 2025)](https://www.chemengconsulting.com/blog/2025/02/28/llm-effective-tools-chemical-industry-sop-generation/1152/)
- [Synthetic Data Generation Using LLMs: Advances in Text and Code (arXiv:2503.14023, 2025)](https://arxiv.org/html/2503.14023v1)
- [Augmentoolkit — Domain-Specific Synthetic Data Pipeline (GitHub)](https://github.com/e-p-armstrong/augmentoolkit)
- [distilabel — Argilla Synthetic Data Framework (GitHub)](https://github.com/argilla-io/distilabel)
- [LLM Data Auditor: Quality Survey (arXiv:2601.17717, 2025)](https://arxiv.org/html/2601.17717v1)
- [Synthetic Datasets for RAG in 2026: Methods, QA, and Tools (FutureAGI)](https://futureagi.com/blog/synthetic-datasets-rag-2025/)
