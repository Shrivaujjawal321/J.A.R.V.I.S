# Catalog & Listing Generation / Optimisation Agent — Build-Ready Blueprint (India)

> **Agentic multi-marketplace listing system** — ingest a product master, generate platform-tuned listings (Amazon, Flipkart, Meesho, Nykaa, Myntra, ONDC), QC for compliance, and continuously optimise CTR/conversion per SKU.
>
> *Investor-grade blueprint. India-first, ONDC-aware. Composite opportunity score: 8.05/10.*

---

## 0. One-line pitch

**"List once, sell everywhere — and keep winning."** An agentic platform that turns a single product master into compliant, ranking-optimised listings across every Indian marketplace in minutes (not 72 hours), then runs a self-optimising loop that rewrites underperformers and closes the size/spec gaps that drive 41–48% of fashion returns.

---

## 1. Problem & Business Case

### 1.1 The problem, sharpened

A multi-marketplace seller/brand in India must publish the **same SKU** with **different content rules** on each channel:

| Surface | Title length | Attributes | Rich content | Ranking signal that matters |
|---|---|---|---|---|
| Amazon.in | ~200 char, brand-first | 30–50 structured attrs | A+ / Brand Story | Search-term relevance + sales velocity + conversion |
| Flipkart | ~150 char | Category-specific spec sheet | Rich media | Flipkart "Listing Quality Index" + price + FAssured |
| Meesho | Short, price-led, vernacular-friendly | Minimal | Image-led | Price + supplier rating + image quality |
| Nykaa | Beauty taxonomy, ingredient/claims-heavy | INCI, shade, claims | Editorial-style | Brand authenticity + claim compliance |
| Myntra | Fashion attributes (fit, fabric, occasion) | Size chart critical | Lookbook imagery | Style score + size-chart completeness |
| ONDC | Schema-bound (ONDC catalog spec) | Strict attribute schema | Limited | Protocol-compliant attributes + serviceability |

Today this is done **manually** by in-house catalog ops or agencies. "Fast" onboarding is **72 hours per batch**; agency cataloguing costs **₹50–300 per SKU** [estimate, from opportunity brief — consistent with India agency rate cards]. And critically, **bad/incomplete size & spec data is a direct returns driver**: India fashion return rates run **25–35%**, with **~53% of apparel returns attributable to size/fit** ([Prime-AI](https://www.prime-ai.com/en/media/clothing-return-rates-by-category-and-country-csf-a/), [bepragma](https://www.bepragma.ai/blogs/top-return-triggers-in-indian-e-commerce)). COD RTO runs **20–40%** of COD orders ([bepragma](https://www.bepragma.ai/blogs/top-return-triggers-in-indian-e-commerce)).

### 1.2 Why existing approaches fail

- **PIM tools (Inriver, BlueMeteor, Pimcore)** *centralise* product data but do **not generate** platform-tuned, ranking-aware content. They are systems of record, not systems of action.
- **Cataloguing agencies (imarc, tamdigi, local studios)** are **manual, batch, one-shot**. They publish once and walk away — no continuous optimisation, no A/B testing, no auto-fix of attribute gaps.
- **Marketplace ad tools / channel managers (ChannelEngine, Unicommerce, Vinculum)** sync inventory & orders but treat *content* as static.
- **No system reasons over each marketplace's ranking rules, auto-fills attribute gaps from competitor patterns, screens prohibited claims, and runs a closed CTR→rewrite loop.**

### 1.3 Quantified cost of inaction (per seller archetype)

Take a mid-size brand: **5,000 SKUs × 6 channels = 30,000 listings**.

| Cost driver | Calculation | Annual cost |
|---|---|---|
| Initial cataloguing labour | 30,000 listings × ₹120/listing [estimate] | **₹36 L** |
| Re-cataloguing / refresh (2×/yr) | 30,000 × ₹60 × 2 | **₹36 L** |
| Lost conversion from weak listings | 5% of GMV uplift foregone on ₹50 Cr GMV [estimate] | **₹2.5 Cr** (opportunity) |
| Spec-driven RTO/returns | If 30% of ₹50 Cr GMV is fashion, 30% return rate, 53% size-driven, 60% addressable, ₹250 reverse-logistics/unit on ~₹900 AOV [estimate] | **₹1.3 Cr+** |

**Total quantified drag for one mid-brand: ₹4–5 Cr/yr [estimate]**, of which ~₹70 L is hard labour cost and the rest is conversion + returns opportunity cost. For a large catalog (50k+ SKUs), the discoverability opportunity cost alone runs into **tens of crores [estimate]**.

> India e-commerce hit **$400B in 2025**, projected **$500B+ by 2027** ([Yahoo Finance / Reports](https://finance.yahoo.com/news/india-b2c-ecommerce-market-report-095000318.html)). **3.5M+ sellers** compete for visibility; Amazon India alone has **10 lakh+ sellers**; ONDC has onboarded **1.16 lakh+ retail sellers across 630+ cities** as of Dec 2025 ([SellingOS](https://sellingos.com/amazon-vs-flipkart-vs-meesho-best-platform-for-new-sellers-in-2026/), [Digital Dawn](https://www.digitaldawn.in/amazon-vs-flipkart-vs-meesho-best-platform-indian-sellers-2025/)).

---

## 2. Agent Architecture

### 2.1 Design philosophy

A **planner → router → specialist workers → critic** topology with a **persistent optimisation loop**. The system is *event-driven* (new SKU, performance threshold breach, ranking-rule change) and *human-gated* only at brand-voice and claims approval.

### 2.2 The agents

| # | Agent | Role | Key tools | Memory |
|---|---|---|---|---|
| 1 | **Orchestrator (Planner)** | Decomposes "list SKU X on channels [..]" into a DAG; routes; handles retries & escalation | LangGraph state machine, task queue | Episodic (job state) |
| 2 | **Catalog-Ingest Agent** | Normalises product master (from PIM/sheet/ERP); extracts attributes from images (OCR/VLM); fills gaps | Vision model, PIM connector, attribute schema validator | Product master (structured) |
| 3 | **Competitor-Intel Agent** | Scrapes/ingests winning listings per category per channel; mines title patterns, keyword clusters, attribute coverage | Marketplace search APIs, scraper, keyword tool, embeddings | Vector store of winning patterns |
| 4 | **Listing-Generator Agents (×6, one per channel)** | Generate channel-tuned title/bullets/keywords/description/A+ from product master + winning patterns + channel ruleset | LLM + channel-rule RAG, keyword API | Channel ruleset (RAG) |
| 5 | **Compliance & QC Agent (Critic)** | Catalog QC, prohibited-claims screen, schema/attribute completeness, image policy, ONDC schema validation | Rule engine + LLM classifier, regex/claim lexicon, image policy model | Compliance rulebook, claim lexicon |
| 6 | **Publisher Agent** | Pushes approved listings via marketplace catalog APIs; handles ONDC protocol; tracks publish status | Amazon SP-API, Flipkart Seller API, Meesho/Nykaa/Myntra APIs, ONDC adapter | Publish ledger |
| 7 | **Performance-Optimiser Agent** | Monitors CTR/conversion/search-term reports; flags underperformers; triggers rewrite; runs A/B | Reports APIs, stats engine, scheduler | Long-term performance memory per SKU×channel |
| 8 | **Brand-Voice Guardian** | Enforces brand tone, banned/required phrases; the HITL gate surfaces here | Style RAG, diff viewer | Brand style guide (RAG) |

### 2.3 Orchestration pattern

- **Planner-Workers-Critic** with a **revise loop**: Generator → Critic (Compliance) → if fail, return with reasons → Generator revises (max N=3) → Brand-Voice Guardian → **HITL gate** → Publisher.
- **Continuous loop** (separate scheduled graph): Performance-Optimiser → detect underperformer → Competitor-Intel refresh → Generator (rewrite variant) → Critic → A/B publish → measure → keep winner.

### 2.4 Memory design

- **Working/episodic**: per-job state (LangGraph checkpointer → Postgres).
- **Semantic (RAG)**: channel rulesets, brand style guides, compliance lexicons, winning-competitor patterns (pgvector / Qdrant).
- **Long-term performance**: time-series of CTR/conversion per SKU×channel (Postgres/Timescale) — the optimiser's "what worked" memory.

### 2.5 Text diagram

```
                          ┌─────────────────────────────┐
   Trigger:               │      ORCHESTRATOR (Planner)  │
   • new SKU              │   build DAG · route · retry  │
   • perf threshold ◄─────┤   · escalate to human        │
   • rule change          └──────────────┬───────────────┘
                                         │
            ┌────────────────────────────┼───────────────────────────┐
            ▼                            ▼                            ▼
   ┌─────────────────┐        ┌──────────────────┐         ┌──────────────────┐
   │ Catalog-Ingest  │        │ Competitor-Intel │         │ Performance-     │
   │ normalise+VLM   │        │ winning patterns │         │ Optimiser (loop) │
   │ attr gap-fill   │        │ keyword clusters │         │ CTR/conv monitor │
   └────────┬────────┘        └────────┬─────────┘         └────────┬─────────┘
            │   product master          │ patterns/RAG               │ rewrite signal
            └──────────────┬────────────┴──────────────┬─────────────┘
                           ▼                            │
              ┌────────────────────────────┐           │
              │  LISTING-GENERATORS  ×6     │◄──────────┘
              │ Amazon│Flipkart│Meesho      │
              │ Nykaa │Myntra  │ONDC        │
              └──────────────┬─────────────┘
                             ▼
              ┌────────────────────────────┐   fail+reasons
              │  COMPLIANCE / QC  (Critic)  │──────────────┐
              │ claims · schema · images    │              │ revise (≤3)
              └──────────────┬─────────────┘◄─────────────┘
                             ▼
              ┌────────────────────────────┐
              │  BRAND-VOICE GUARDIAN       │
              │  ███ HUMAN-IN-THE-LOOP ███  │  ← approve / edit / reject
              └──────────────┬─────────────┘
                             ▼
              ┌────────────────────────────┐
              │  PUBLISHER (catalog APIs)   │ → Amazon SP-API · Flipkart · Meesho
              │  + ONDC protocol adapter    │   · Nykaa · Myntra · ONDC network
              └──────────────┬─────────────┘
                             ▼
                    [ live listings ] → metrics flow back to Performance-Optimiser
```

---

## 3. Multi-Agent Workflow (step-by-step)

**A. Initial listing flow**

1. **Trigger** — new SKU added to PIM / CSV upload / ERP webhook.
2. **Ingest** — Catalog-Ingest normalises fields; VLM extracts attributes from product images; flags missing **mandatory** attributes (size chart, material, dimensions). ▣ *If critical spec missing → auto-request from seller (HITL micro-checkpoint).*
3. **Intel** — Competitor-Intel pulls top-ranked listings for the category per channel; extracts title patterns, high-value keywords, attribute-coverage benchmark.
4. **Generate** — 6 channel Generators produce channel-specific drafts in parallel (title/bullets/keywords/description/A+/ONDC schema).
5. **QC (Critic)** — Compliance agent checks: prohibited claims, schema completeness, char limits, image policy, ONDC validation. Failures bounce to Generator with structured reasons (≤3 revise cycles).
6. **▓ HITL CHECKPOINT 1 — Brand & Claims approval** — Brand-Voice Guardian surfaces a diff; human approves / edits / rejects tone + any regulated claims (esp. beauty/Nykaa, food, health).
7. **Publish** — Publisher pushes via APIs; ONDC adapter handles protocol; records publish ledger + status.
8. **Baseline** — Performance-Optimiser starts tracking CTR/conversion.

**B. Continuous optimisation loop (scheduled)**

9. **Monitor** — Optimiser reads search-term reports + CTR/conversion vs category benchmark.
10. **Detect** — SKU×channel below threshold (e.g., CTR < p25 for 14 days) → flagged.
11. **Diagnose & rewrite** — Competitor-Intel refresh → Generator produces a challenger variant.
12. **QC + ▓ HITL CHECKPOINT 2** (lightweight — only if claims/tone change; pure keyword tweaks can be auto-approved per policy).
13. **A/B** — Publish challenger (where the channel supports experiment, else time-sliced), measure, **keep the winner**, log to performance memory.

> **What's gated:** brand voice, regulated claims, first publish of a new claim. **What's autonomous:** keyword refresh, attribute gap-fill from verified sources, format compliance, A/B variant generation.

---

## 4. Data Sources & Integrations

### 4.1 Systems to connect

| Layer | System | What it provides | Where it's siloed today |
|---|---|---|---|
| Product master | **PIM** (Inriver, BlueMeteor, Pimcore) or **ERP** (SAP, Oracle NetSuite, **Tally** for SMBs), or Google Sheets/Excel | SKU attributes, images, pricing | Locked in PIM; SMBs in spreadsheets |
| Channel content | **Amazon SP-API** (Catalog Items, Listings, A+ Content API) | Publish + ranking signals | Per-seller-central, manual |
| Channel content | **Flipkart Seller API** (Listings, FLuid) | Publish + Listing Quality Index | Seller hub |
| Channel content | **Meesho Supplier API**, **Nykaa**, **Myntra (Myntra Partner Portal/Stylumia feeds)** | Publish | Each portal separate |
| Network | **ONDC** (catalog/`on_search` schema, Seller App adapter) | Protocol-bound catalog | Requires ONDC-compliant seller app |
| Performance | **Amazon Brand Analytics / Search-Term Reports**, **Flipkart Insights**, marketplace ad consoles | CTR, conversion, search terms | Per-console, manual export |
| Competitor | Marketplace search results / scraping / 3rd-party (Stylumia, Helium10-style for India) | Winning patterns, keywords | Not systematised |

### 4.2 Data contracts

- **Inbound product master** → canonical internal schema (Pydantic v2 model): `sku, brand, category, mandatory_attrs{}, optional_attrs{}, images[], size_chart, price`.
- **Channel ruleset** (versioned YAML/JSON in RAG): char limits, required attrs, banned terms, image specs, ONDC schema map.
- **Outbound listing payload** per channel API spec + idempotency key (sku×channel×content-hash).
- **Performance contract**: normalised `{sku, channel, date, impressions, clicks, ctr, conversion, search_terms[]}`.

### 4.3 Siloing reality

Today the product master, the six channel consoles, and the six performance dashboards are **12+ disconnected silos** with no content-generation glue. The wedge is being the **action layer that spans all of them**.

---

## 5. Automation vs Human

| Fully automated | Human-in-the-loop | Human-owned |
|---|---|---|
| Attribute normalisation & VLM extraction | Brand voice/tone approval | Brand strategy & positioning |
| Channel-tuned generation | Regulated-claims sign-off (beauty/food/health) | Legal interpretation of new regulations |
| Format/schema compliance, char limits | First publish of a *new* claim type | Pricing strategy |
| Keyword refresh & A/B variant gen | Edge-case escalations | Supplier/sourcing decisions |
| Underperformer detection & rewrite trigger | Bulk-action confirmation (>X SKUs) | — |
| Publish via APIs (with idempotency) | — | — |

**Automation potential: High.** Realistic target: **85–90% of listing operations** hands-off, with humans on the ~10–15% claims/tone/edge cases.

---

## 6. Tech Stack (2026)

| Concern | Choice | Why |
|---|---|---|
| **Reasoning model** | Claude (Opus/Sonnet tier) or GPT-class for generation; **VLM** (Claude vision / Gemini) for image attribute extraction | Strong structured generation + multilingual (Hindi/vernacular for Meesho) |
| **Cheap/bulk model** | Sonnet/Haiku-class or Llama-3.3/Mistral for QC classification & bulk keyword work | Cost control at 30k-listing scale |
| **Orchestration** | **LangGraph** (stateful DAG, checkpointer, human-in-loop interrupts) | Native HITL interrupts + durable state fit this planner-critic-loop perfectly |
| **Retrieval/RAG** | **pgvector** (start) → **Qdrant** at scale; hybrid (BM25 + dense) | Channel rulesets, brand guides, competitor patterns |
| **Eval/guardrails** | Promptfoo / Ragas for gen quality; custom claim-lexicon rule engine; **OWASP-LLM** prompt-injection defenses on scraped competitor content | Compliance is the moat — must be testable |
| **Structured output** | Pydantic v2 schemas, JSON-mode | Deterministic channel payloads |
| **Queue/runtime** | Temporal or Celery + Redis; FastAPI control plane | Long-running, retryable, idempotent publishes |
| **Storage** | Postgres + Timescale (performance), S3/object store (images), Qdrant (vectors) | — |
| **Deployment** | **VPC/cloud-native default; on-prem/VPC option for large enterprises** (data residency, brand IP) | Indian enterprises often demand VPC; SMB SaaS multi-tenant |
| **Observability** | OpenTelemetry + LangSmith/Langfuse traces | Every reasoning trace auditable for compliance |

> **On-prem note:** Brand catalog + pricing is sensitive IP for large enterprises. Offer **single-tenant VPC** (their cloud) for enterprise tier; multi-tenant SaaS for SMB. Models via API by default; **self-hostable open-weights path** (Llama/Mistral on their GPU) for data-residency-strict clients.

---

## 7. Expected ROI & Payback

**For the 5,000-SKU / 6-channel mid-brand (from §1.3):**

| Lever | Annual value |
|---|---|
| Cataloguing labour saved (80%) | ~₹58 L (of ₹72 L) |
| Conversion uplift (3–5% on GMV) | ₹1.5–2.5 Cr [estimate] |
| Spec-driven RTO reduction (20–30% of addressable returns) | ₹30–60 L [estimate] |
| **Total annual value** | **₹2.4–3.7 Cr [estimate]** |

**Pricing model** (see §11): blended **₹15–40/SKU/channel/yr** + platform fee, or **₹50K–5L/mo** enterprise tier. For the mid-brand, annual platform cost ≈ **₹25–60 L**.

**Payback: 3–6 months** — driven first by labour displacement (immediate, hard) then conversion + RTO (cumulative). Anchors to the brief's "payback 3–6 months."

---

## 8. Implementation Complexity, Risks, Mitigations

**Overall complexity: Medium** (the brief is right). Generation is solved by LLMs; the hard parts are **integrations breadth** and **compliance reliability**, not the AI.

| Risk | Severity | Mitigation |
|---|---|---|
| **Marketplace API churn / rate limits / scraping bans** | High | Abstract behind adapter layer; official APIs first; respectful rate-limiting; fallback feeds (Stylumia/partner data) |
| **ONDC schema complexity & evolving spec** | Med-High | Dedicated ONDC adapter; track spec versions in RAG; partner with an ONDC Seller App |
| **Hallucinated/false claims → legal/policy strike** | High | Hard rule-engine claim screen + HITL gate; never auto-publish a new claim; full audit trace |
| **Wrong attributes worsening RTO (the thing we sell against)** | High | Verified-source-only gap-fill; confidence thresholds; flag low-confidence to human |
| **Generic output = sounds AI / hurts brand** | Med | Brand-voice RAG + competitor-pattern grounding + brand guardian gate |
| **Cost at 30k-listing scale** | Med | Tiered models, caching, batch; regenerate only on real signal, not blindly |
| **Channel ToS on automated content/AI** | Med | Stay within official Seller API terms; HITL preserves "seller-authored" posture |

---

## 9. TAM / SAM / SOM (India) — with math

> All figures **[estimate]**, triangulated from $400B India e-comm (2025), 3.5M+ sellers, agency rate cards ₹50–300/SKU.

**TAM — total India cataloguing + listing-ops spend**
- Addressable sellers running structured catalogs: ~**150k–250k** mid+ sellers (subset of 3.5M; most micro-sellers won't pay).
- Avg annual catalog/listing-ops spend (labour + agency + tools): **₹60K–1L/seller** [estimate].
- TAM ≈ 200k × ₹0.8L ≈ **₹1,600 Cr/yr** → brief's **₹1,000–1,800 Cr/yr** band. ✔

**SAM — multi-marketplace sellers + brands (the real buyers)**
- Sellers actively on 3+ marketplaces + D2C brands: ~**40k–60k** [estimate].
- Willing spend on an automation platform: **₹60K–1.2L/yr** [estimate].
- SAM ≈ 50k × ₹0.9L ≈ **₹450 Cr/yr** → brief's **₹300–500 Cr**. ✔

**SOM — realistic 3-year capture**
- Target 2–4% of SAM by Year 3: capture **1,500–3,500 paying sellers** at avg **₹2–2.5L ARPA** (mix of SMB + enterprise) ≈ **₹30–70 Cr ARR** → brief's **₹30–70 Cr**. ✔

| | India figure [estimate] |
|---|---|
| **TAM** | ₹1,000–1,800 Cr/yr |
| **SAM** | ₹300–500 Cr/yr |
| **SOM (3-yr)** | ₹30–70 Cr ARR |

---

## 10. Competitive Landscape

| Player | Type | Strength | Gap we exploit |
|---|---|---|---|
| **Inriver, BlueMeteor, Pimcore** | PIM (global) | System of record | No generation, no per-channel tuning, no optimisation loop |
| **ChannelEngine, Unicommerce, Vinculum, EasyEcom, Browntape** | Channel/OMS (global + India) | Inventory/order sync | Content is static; no agentic generation or A/B |
| **Cataloguing agencies (imarc, tamdigi, GreenHonchos)** | Service | Human quality | Manual, batch, one-shot, no continuous optimisation, ₹50–300/SKU |
| **Helium10 / Jungle Scout** | Amazon-only tools | Keyword research | Single-channel, US-centric, no ONDC, no auto-publish loop |
| **Stylumia, Fractal/retail-AI** | Analytics/AI | Demand intel | Not a listing-action layer |
| **Generic GPT wrappers** | New AI startups | Cheap copy gen | No compliance engine, no multi-channel publish, no closed loop, no ONDC |

### The wedge
**Agentic, multi-marketplace *generation + continuous self-optimisation*, India/ONDC-native, with a hard compliance engine.** Nobody combines: (a) generate platform-tuned content from a master, (b) auto-fix attribute gaps that cause RTO, (c) screen claims, (d) publish via API, and (e) run a CTR→rewrite loop — across **Amazon + Flipkart + Meesho + Nykaa + Myntra + ONDC**. ONDC-readiness is a structural moat global players will be slow to build.

---

## 11. Startup Verdict

### Is it fundable? **YES — build. Probability of success: Medium-High (~60–65%).**

**Why fundable**
- **Composite 8.05/10**; AI-feasibility 9 (generation is solved); pain severity 8 (real ₹ — labour + RTO + conversion).
- Large, growing market ($400B→$500B), structural seller pain, and a clear "system of action" gap above incumbent PIMs/OMS.
- ROI is **hard-dollar provable** (labour displaced day one), which shortens sales cycles.

**Why not a slam-dunk (the 35–40% risk)**
- **Integrations breadth is a grind** (6 marketplaces + ONDC + PIMs/ERPs) — this is the real moat *and* the real cost.
- Marketplace API/ToS dependence; channels could build native AI listing tools (Amazon already nudges here) — but cross-channel + ONDC + brand IP defensibility blunts that.
- Compliance reliability is existential — one false-claim incident at scale hurts trust.

### GTM motion
1. **Wedge channel: Fashion + Beauty multi-marketplace D2C brands** (highest RTO pain, highest claim complexity → highest willingness to pay).
2. **Land** with the "list once across 6 channels in minutes + cut size-driven returns" promise; **expand** into the optimisation loop (recurring value, stickiness).
3. **Bottom-up SaaS (SMB self-serve)** + **top-down enterprise** (VPC, brand catalogs). Channel partnerships with ONDC Seller Apps and 3PLs (returns angle).
4. Land-and-expand by SKU count and channel count → net-revenue-retention engine.

### Ideal ICP
**D2C fashion/beauty brand or aggregator, 2,000–50,000 SKUs, live on 3+ marketplaces + ONDC, ₹20–500 Cr GMV, with a catalog-ops team or agency spend they want to cut.**

### Moat
1. **ONDC-native + 6-channel integration depth** (years to replicate).
2. **Compliance/claims engine** (regulated-category trust).
3. **Performance memory flywheel** — every A/B across thousands of SKUs teaches the optimiser what wins per category/channel; data network effect.

### Verdict
**BUILD.** Strong founder-investor story: provable ROI, defensible integration + ONDC moat, data flywheel, and a real gap above PIM/OMS incumbents. The discipline that decides winners is **integration breadth + compliance reliability**, not model quality.

---

### Sources
- [India B2C Ecommerce Market Report 2025-2029 (Yahoo Finance)](https://finance.yahoo.com/news/india-b2c-ecommerce-market-report-095000318.html)
- [Amazon vs Flipkart vs Meesho — sellers 2026 (SellingOS)](https://sellingos.com/amazon-vs-flipkart-vs-meesho-best-platform-for-new-sellers-in-2026/)
- [Indian sellers guide 2026 (Digital Dawn)](https://www.digitaldawn.in/amazon-vs-flipkart-vs-meesho-best-platform-indian-sellers-2025/)
- [Top Return Triggers in Indian E-commerce (bepragma)](https://www.bepragma.ai/blogs/top-return-triggers-in-indian-e-commerce)
- [Clothing return rates by category & country (Prime-AI)](https://www.prime-ai.com/en/media/clothing-return-rates-by-category-and-category-csf-a/)
- [Ecommerce Return Rates 2026 (Richpanel)](https://www.richpanel.com/learn/ecommerce-return-rates)

*Figures tagged [estimate] are analytical triangulations, not measured data.*
