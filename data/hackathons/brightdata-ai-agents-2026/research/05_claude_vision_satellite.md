# Claude Vision API for Satellite Imagery Analysis

## Quick Answer

Claude Vision (Sonnet 4.6 / Opus 4.7) excels at scene-level interpretation + change-signal narratives, but has weaknesses in precise object counting (MAPE 30–60% vs YOLO 5–15%). Sweet spot for alt-data agent: structured JSON tool-use for counts with mandatory confidence + abstention fields, plus Claude's strong natural-language reasoning for investment narrative. Batch API at $1.50/MTok → ~$1.75/day for 500 tiles.

---

## API Mechanics

**Three input methods:**
- `base64` — bytes in-memory
- `url` — hosted image
- Files API (`file_id`) — upload once, reference many times

**Token formula:** `tokens ≈ (width_px × height_px) / 750`

**Per-model resolution:**

| Model | Max long edge | Max tokens/image |
|-------|--------------|-----------------|
| Sonnet 4.6, Haiku 4.5, Opus 4.6 | 1,568 px | ~1,568 |
| Opus 4.7 (new high-res) | 2,576 px | ~4,784 |

**Max images per request:** 600 (standard) / 100 (200k context). Hard payload: 32 MB.
**Per-file:** 5 MB API, 10 MB UI.
**Formats:** JPEG, PNG, GIF (1st frame), WebP.

**Prompt placement:** Image blocks BEFORE text instructions in `content` array.

---

## Pricing

| Model | Input $/MTok | Output $/MTok | Batch Input | Batch Output |
|-------|---|---|---|---|
| Haiku 4.5 | $1.00 | $5.00 | $0.50 | $2.50 |
| Sonnet 4.6 | $3.00 | $15.00 | $1.50 | $7.50 |
| Opus 4.7 | $5.00 | $25.00 | $2.50 | $12.50 |

**Opus 4.7 gotcha:** New tokenizer ~35% more tokens on identical text.

**Prompt Caching:** Write 1.25× input (5min) / 2× (1h); Read 0.10× input.

**Production estimate — 500 tiles/day, 1000×1000 px, Sonnet 4.6 Batch:**
- Image tokens: 500 × 1,334 = 667K → $1.00/day
- Output ~200 tok: 100K → $0.75/day
- **Total: ~$1.75/day**

---

## Accuracy Benchmarks

**Source:** Zhang & Wang (2024). "Good at captioning, bad at counting." arxiv:2401.17600. ICLR 2024 Workshop.

**Vehicle counting (COWC dataset):**

| Model | MAE ↓ | MAPE ↓ | R² ↑ |
|-------|---|---|---|
| LLaVA (best zero-shot VLM) | 2.695 | 0.467 | ~0.35 |
| InstructBLIP | ~2.8 | 0.510 | ~0.25 |
| GPT-4V | ~4.1 | ~0.65 | ~0.20 |
| Specialist CNN | **0.248** | **~0.08** | **>0.90** |

**Task-by-task:**

| Task | Claude Vision | Traditional CV |
|------|--------------|----------------|
| Parking lot vehicles | MAPE 30-60% | MAPE 5-15% (YOLO) |
| Ships/vessels | Moderate count, good type | mAP 85-88% (YOLOv8) |
| Construction (binary) | High — semantic strength | mAP 80-90% |
| Crop health (RGB) | Categorical only | Multispectral required |
| SAR imagery | **Not feasible** | Specialized models |
| Thermal/IR | **Not feasible** | IR fusion models |
| Investment narrative | **Excellent** | N/A |
| Temporal change (binary) | Good for large changes | 90%+ bi-temporal CNN |

---

## Prompting Patterns

**Always use tool use, not prompt-for-JSON.** Set `tool_choice: {type: "tool", name: ...}`.

**Multi-image labeling:**
```
"Image 1 (2025-11-01):" → [image] → "Image 2 (2026-04-15):" → [image] → "Compare..."
```

**Grid sub-counting:** System prompt: "Mentally divide into 3×3 grid. Count vehicles per cell, then sum."

**Role assignment:** "You are a remote sensing analyst specializing in commodity market intelligence..."

**Chain of thought:** "Note any factors reducing confidence before providing counts."

---

## Prompt Template — Parking Lot Vehicle Count

```python
tools = [{
    "name": "parking_lot_analysis",
    "input_schema": {
        "type": "object",
        "properties": {
            "vehicle_count_estimate": {"type": "integer"},
            "vehicle_count_range": {
                "type": "object",
                "properties": {"low": {"type": "integer"}, "high": {"type": "integer"}}
            },
            "lot_occupancy_pct": {"type": "number"},
            "confidence": {"type": "string", "enum": ["high", "medium", "low"]},
            "limiting_factors": {"type": "array", "items": {"type": "string"}},
            "analyst_notes": {"type": "string"}
        },
        "required": ["vehicle_count_estimate", "confidence", "limiting_factors"]
    }
}]

system = """You are a satellite imagery analyst providing alt-data signals.
Methodology: Mentally divide image into a 3x3 grid. Count vehicles in each cell, then sum.
For ambiguous objects, include in low estimate, exclude from high estimate."""

response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    system=system,
    tools=tools,
    tool_choice={"type": "tool", "name": "parking_lot_analysis"},
    messages=[{"role": "user", "content": user_content}]
)
```

---

## Temporal Change Detection (2 images)

```python
content = [
    {"type": "text", "text": f"Image 1 ({date_t1}, baseline):"},
    {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": img_b64_t1}},
    {"type": "text", "text": f"Image 2 ({date_t2}, current):"},
    {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": img_b64_t2}},
    {"type": "text", "text": f"Compare these satellite images. Identify investment-relevant changes."}
]
```

Schema: `change_detected, change_magnitude, investment_signal (bullish/bearish/neutral), signal_rationale, confidence, abstain_reason`.

---

## Confidence-Aware Abstention

```python
def process_with_abstention(result: dict, threshold: str = "medium") -> dict:
    thresholds = {"high": 3, "medium": 2, "low": 1}
    if thresholds.get(result.get("confidence", "low"), 0) < thresholds[threshold]:
        return {"signal": "ABSTAIN", "reason": result.get("abstain_reason"), "raw": result}
    return result
```

Always include `abstain_reason` in schema. VLMs prone to overconfidence.

---

## SAR + Thermal — Hard Limits

VLMs trained on RGB cannot reliably interpret SAR (weak texture, high noise, ambiguous boundaries). For SAR/thermal, route to SARDet, LiM-YOLO, or YOLOv9-SAR. **Do not call Claude.**

---

## Alternative Models

**Open-source VLMs (at scale, when Claude expensive):**
- **Qwen2.5-VL 7B** — strong spatial reasoning, consumer GPU
- **Pixtral 12B** — native-res, 128K context, beats Llama 3.2 11B
- **Llama 3.2 Vision 90B** — wider deployment but inferior at 7B scale

**Domain-specific satellite:**
- **Prithvi-EO-2.0** (IBM + NASA) — change detection, 600M params, deployed in-orbit
- **Clay** — flexible EO foundation model
- **GeoChat** (MBZUAI) — RS VQA, CVPR 2024, 84.43% UCMerced

---

## Decision Framework

| Criterion | Claude Vision | YOLO / Detectron2 |
|-----------|--------------|-------------------|
| Setup time | Minutes | Days–weeks |
| Counting accuracy | MAPE 30-60% | MAPE 5-15% |
| Scene classification | Excellent | Good (with labels) |
| Investment narrative | Native | None |
| Zero labeled data | Works immediately | Needs dataset |
| SAR/thermal | No | Yes |
| Cost @ 10K images/day | ~$35/day (Sonnet Batch) | ~$5/day (GPU post-training) |

**Hackathon architecture:**
1. Claude Vision for scene-level + change narrative
2. GeoChat / traditional CV for precise counts when accuracy matters
3. Abstain + flag when confidence low — never propagate bad counts

For demo, Claude Vision alone compelling — judges respond to natural language investment reasoning, not raw counts.

---

## Sources

- [Anthropic Vision Docs](https://platform.claude.com/docs/en/build-with-claude/vision)
- [Anthropic Pricing](https://platform.claude.com/docs/en/about-claude/pricing)
- [Zhang & Wang 2024 — counting benchmark](https://arxiv.org/abs/2401.17600)
- [LiM-YOLO Ship Detection](https://arxiv.org/pdf/2512.09700)
- [GeoChat CVPR 2024](https://arxiv.org/pdf/2311.15826)
- [SARLANG-1M SAR VLM](https://arxiv.org/pdf/2504.03254)
- [NASA: Prithvi in orbit](https://science.nasa.gov/science-research/ai-foundation-model-in-orbit/)
- [IBM Prithvi-EO-2.0](https://research.ibm.com/blog/prithvi2-geospatial)
- [Pixtral 12B](https://arxiv.org/html/2410.07073v2)
- [VLM Confidence Calibration](https://arxiv.org/pdf/2505.20236)

**Confidence: Medium-High** — API mechanics + pricing: High (Anthropic docs). Counting accuracy: High (peer-reviewed benchmark) but Claude-specific [unverified].
