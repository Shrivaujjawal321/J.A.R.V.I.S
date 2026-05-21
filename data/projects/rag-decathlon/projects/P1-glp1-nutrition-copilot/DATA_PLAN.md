# P1 glp1-nutrition-copilot — Data Plan

Ingestion pipeline + corpus design. Owned by `data-engineer-agent` in Phase 3.3.

---

## 1. Corpus composition (target)

| Source | Chunks | Size | Refresh |
|--------|--------|------|---------|
| PubMed abstracts (GLP-1 nutrition, 2022-2026) | ~600 | ~5MB | Weekly cron |
| PMC full-text (open-access subset of above) | ~150 | ~15MB | Monthly |
| USDA FoodData Central (Foundation + SR Legacy) | ~8,000 foods | ~8MB | Monthly |
| NIH ODS Fact Sheets (16 nutrients × ~4 sections) | ~64 | ~500KB | Monthly |
| **Total** | **~8,800** | **~28MB** | |

All chunks embedded with voyage-3-large 1024-dim int8 → ~9MB in Upstash Vector.

Fits comfortably in Upstash free tier (10K vectors) for MVP. PAYG kicks in only on heavy traffic.

---

## 2. PubMed ingestion

### Step 1 — Discovery (ESearch)

Query each subdomain separately to ensure coverage:

```python
QUERIES = {
    "micronutrient_deficiency": '(semaglutide[tiab] OR tirzepatide[tiab] OR "GLP-1 receptor agonist"[tiab]) AND (deficiency[tiab] OR micronutrient[tiab] OR "vitamin D"[tiab] OR iron[tiab] OR calcium[tiab])',
    "protein_muscle": '(semaglutide[tiab] OR tirzepatide[tiab] OR "GLP-1 receptor agonist"[tiab]) AND (protein[tiab] OR "lean mass"[tiab] OR sarcopenia[tiab] OR "muscle preservation"[tiab])',
    "weight_loss_nutrition": '(semaglutide[tiab] OR tirzepatide[tiab]) AND ("weight loss"[tiab] OR nutrition[tiab] OR dietary[tiab])',
    "supplements_glp1": '(semaglutide[tiab] OR tirzepatide[tiab]) AND (supplement[tiab] OR vitamin[tiab] OR mineral[tiab])',
    "side_effects_nutrition": '(semaglutide[tiab] OR tirzepatide[tiab]) AND (nausea[tiab] OR "gastric emptying"[tiab] OR satiety[tiab])',
}

for name, term in QUERIES.items():
    pmids = esearch(term, retmax=200, datetype="pdat", mindate="2024", maxdate="2026")
```

Date filter: 2024-2026 only. Older guidelines (e.g. RDA 0.8g/kg) are anti-evidence for our use case.

### Step 2 — Metadata fetch (ESummary + EFetch)

```python
# Batch fetch 200 PMIDs at a time, parse XML
for batch in chunks(all_pmids, 200):
    xml = efetch(ids=batch, db="pubmed", rettype="xml")
    records = parse_pubmed_xml(xml)
    # records: List[{ pmid, title, abstract, authors, journal, year, mesh_terms, doi, pmc_id }]
```

Rate: 10rps with NCBI API key. Total time for ~600 papers: ~30s.

### Step 3 — Full-text (PMC OA)

Only for papers with `pmc_id` in OA subset:

```python
for r in records_with_pmc_id:
    bioc_json = fetch(f"https://www.ncbi.nlm.nih.gov/research/bionlp/RESTful/pmcoa.cgi/BioC_json/{r.pmc_id}/unicode")
    sections = parse_bioc_sections(bioc_json)  # intro, methods, results, discussion
    r.full_text_sections = sections
```

### Step 4 — Chunking

Hierarchical small-to-big:

```python
def chunk_pubmed(record):
    # Parent: full abstract OR each section of full-text
    parents = []
    if record.full_text_sections:
        for section in record.full_text_sections:
            parents.append(Parent(
                text=f"Title: {record.title}. Section: {section.name}. MeSH: {','.join(record.mesh_terms)}. Content: {section.text}",
                metadata={**record.meta, "section": section.name}
            ))
    else:
        parents.append(Parent(
            text=f"Title: {record.title}. MeSH: {','.join(record.mesh_terms)}. Abstract: {record.abstract}",
            metadata=record.meta
        ))

    # Children: 128-token splits within parent
    children = []
    for parent in parents:
        splits = sentence_split(parent.text, target_tokens=128, overlap=20)
        for s in splits:
            children.append(Child(text=s, parent_id=parent.id, metadata=parent.metadata))

    return parents, children
```

We embed and store CHILDREN. At query time, we retrieve children but assemble PARENT context for the LLM. This is the small-to-big pattern.

### Step 5 — Embed + upsert

```python
embeddings = voyage.embed(
    input=[c.text for c in children],
    model="voyage-3-large",
    input_type="document",       # CRITICAL
    output_dtype="int8",
    output_dimension=1024,
)

upstash.upsert([
    {
        "id": f"pubmed:{c.parent_id}:{c.idx}",
        "vector": e.tolist(),
        "metadata": {
            "source_type": "pubmed",
            "pmid": c.metadata["pmid"],
            "title": c.metadata["title"],
            "journal": c.metadata["journal"],
            "year": c.metadata["year"],
            "section": c.metadata.get("section"),
            "parent_text": parents[c.parent_id].text,   # for context assembly at retrieval time
            "child_text": c.text,
            "url": f"https://pubmed.ncbi.nlm.nih.gov/{c.metadata['pmid']}/",
        }
    }
    for c, e in zip(children, embeddings)
])
```

---

## 3. USDA FoodData Central ingestion

```python
# Step 1 — search relevant foods for GLP-1 nutrition use case
RELEVANT_FOODS = [
    "egg", "chicken breast", "salmon", "greek yogurt", "cottage cheese",
    "lentil", "chickpea", "tofu", "tempeh", "almond",
    "spinach", "broccoli", "kale", "sardine", "tuna",
    "beef", "pork", "milk", "cheese", "quinoa",
    # ~100 high-protein / high-micronutrient foods
]

for food in RELEVANT_FOODS:
    results = fdc.search(food, dataType=["Foundation", "SR Legacy"])
    for r in results[:5]:
        food_detail = fdc.get_food(r.fdcId)
        chunks.append(format_usda_chunk(food_detail))

def format_usda_chunk(food):
    nutrients = ", ".join(
        f"{n.name} {n.amount}{n.unit}"
        for n in food.foodNutrients
        if n.id in {203, 301, 303, 324, 309, 418, 415, 401, 415, 415}  # protein, Ca, Fe, vit D, Zn, B12, etc.
    )
    return Chunk(
        text=f"Food: {food.description}. Category: {food.foodCategory}. Nutrients per 100g: {nutrients}.",
        metadata={
            "source_type": "usda",
            "fdc_id": food.fdcId,
            "food_name": food.description,
            "data_type": food.dataType,
            "url": f"https://fdc.nal.usda.gov/food-details/{food.fdcId}/nutrients",
        }
    )
```

Rate limit: 1000/hour. Total: ~500 chunks for MVP, ~5min.

---

## 4. NIH ODS ingestion

```python
GLP1_RELEVANT_SLUGS = [
    "VitaminD", "Iron", "Calcium", "Thiamin", "VitaminB12",
    "Zinc", "Magnesium", "Selenium", "VitaminK", "VitaminA",
    "VitaminC", "VitaminE", "Folate", "Riboflavin", "Niacin", "Protein",
]

for slug in GLP1_RELEVANT_SLUGS:
    xml = fetch(f"https://ods.od.nih.gov/api/factsheets/{slug}?languagecode=EN")
    sections = parse_ods_xml(xml)
    # sections: [{name: "Introduction"|"Sources"|"Recommended Intakes"|"Deficiency"|"Health Risks"|"Interactions"|...}]
    for section in sections:
        chunks.append(Chunk(
            text=f"NIH ODS Fact Sheet: {slug}. Section: {section.name}. Content: {section.text}",
            metadata={
                "source_type": "ods",
                "slug": slug,
                "section": section.name,
                "url": f"https://ods.od.nih.gov/factsheets/{slug}-HealthProfessional/",
            }
        ))
```

Total: 16 fact sheets × ~4 sections = ~64 chunks, ~30s ingest.

---

## 5. BM25 index

Built in-memory at serverless function cold start (one-time, ~50ms for 9K chunks):

```typescript
// lib/rag/bm25.ts
import { BM25 } from 'okapibm25'

let bm25Index: BM25 | null = null

export async function getBM25Index() {
  if (bm25Index) return bm25Index
  // Fetch all chunks' text + metadata from Upstash via paginated query (one-shot at cold start)
  const all = await upstashVector.fetchAll()
  const docs = all.map(c => c.metadata.child_text)
  bm25Index = new BM25(docs.map(tokenize))
  return bm25Index
}
```

Fluid Compute keeps the index warm across requests.

---

## 6. Ingestion scheduling

| Source | Frequency | Trigger |
|--------|-----------|---------|
| PubMed | Weekly | Vercel Cron `0 3 * * 1` (Mondays 3am UTC) |
| PMC full-text | Monthly | Vercel Cron `0 3 1 * *` |
| USDA | Monthly | Vercel Cron `0 4 1 * *` |
| NIH ODS | Monthly | Vercel Cron `0 5 1 * *` |

Each cron writes to `data/ingest-logs/` with chunk-count delta + Upstash size + errors.

---

## 7. Data quality gates

Every ingest run:
- ✅ At least 1 chunk per PubMed result (else fetch error)
- ✅ Sanity: `len(embeddings) == len(chunks)`
- ✅ All metadata URL strings 200 on HEAD check (sampled 5%)
- ✅ No empty `child_text`
- ✅ MeSH terms preserved on PubMed records
- ✅ Year metadata present (used for recency filtering)
- ✅ Idempotent upsert by stable chunk ID (no duplicates)

If any gate fails → ingest halts, Telegram alert to Boss.

---

## 8. Privacy + audit

- No user queries logged to disk; only hashed-query + retrieval metadata
- Upstash dataset is public-only public data (PubMed, USDA, NIH) — no PHI
- Vercel logs retained 7 days max; anything older auto-pruned
