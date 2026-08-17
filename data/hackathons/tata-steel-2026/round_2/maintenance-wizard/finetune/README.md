# Maintenance Wizard — QLoRA Fine-Tune Kit

Domain-specific fine-tune of **Qwen2.5-3B-Instruct** on 969 steel-plant maintenance
instruction examples. Built for Tata Steel Hackathon Round 2 — provides the
"Bonus Merit: domain-specific fine-tuning" evidence required by the design doc.

---

## Files

| File | Description |
|---|---|
| `build_dataset.py` | Builds `maintenance_sft.jsonl` + `maintenance_eval_50.jsonl` from raw data |
| `maintenance_sft.jsonl` | 969 instruction examples (train set) |
| `maintenance_eval_50.jsonl` | 50 held-out examples (eval set) |
| `Maintenance_Wizard_QLoRA_Colab.ipynb` | Colab notebook — runs end-to-end on free T4 |
| `eval_finetune.py` | Standalone before/after metric helper (ROUGE-1, domain coverage, composite) |

---

## Colab Run — Step by Step

### 1. Open the notebook in Colab

Go to [colab.research.google.com](https://colab.research.google.com) →
File → Upload notebook → select `Maintenance_Wizard_QLoRA_Colab.ipynb`.

### 2. Set Runtime to T4 GPU

Runtime → Change runtime type → Hardware accelerator → **T4 GPU** → Save.

Free Colab T4 has 15 GB VRAM — enough for Qwen2.5-3B in 4-bit + LoRA.

### 3. Upload the dataset files

Two ways:

**Option A — Files panel (simpler):**
- In the left sidebar click the folder icon
- Click the upload (cloud) icon
- Upload both `maintenance_sft.jsonl` and `maintenance_eval_50.jsonl`
- They land at `/content/maintenance_sft.jsonl`

**Option B — Google Drive:**
- Upload both files to your Drive
- Uncomment the Drive mount lines in cell "Step 3" of the notebook
- Update `SFT_PATH` / `EVAL_PATH` to point to your Drive paths

### 4. Run All

Runtime → Run All (or Ctrl+F9).

Expected runtime on free T4:
- Install: ~4 min
- Model download: ~2 min
- Training (2 epochs, 969 examples): **~90–150 min**
- Eval (50 examples, before + after): ~10 min
- GGUF export: ~15 min
- **Total: ~2–4 hours**

Watch the training loss in the output of the SFTTrainer cell — it should drop
steadily. If it plateaus early, increase `num_train_epochs` to 3.

### 5. Download artifacts

The final cell triggers browser downloads of:
- `maintenance_wizard_lora.zip` — LoRA adapter (safetensors)
- `maintenance_wizard_gguf/*.gguf` — GGUF q4_k_m (~2 GB, for Ollama)
- `Modelfile` — Ollama config
- `eval_results.json` — Before/after eval numbers

Alternatively use the Files panel → right-click any file → Download.

---

## What the Eval Produces

After training, the notebook runs generation on all 50 held-out examples with:
1. **Base model** (LoRA adapters disabled)
2. **Fine-tuned model** (LoRA adapters active)

Then scores both with three metrics:

| Metric | What it measures |
|---|---|
| ROUGE-1 F1 | Unigram overlap with reference answer |
| Domain Coverage | Fraction of steel/maintenance vocab present in output |
| Composite (0-100) | 0.5×ROUGE + 0.5×Domain — headline number |

`eval_results.json` contains the raw numbers and a verdict string.

---

## Using eval_results.json in the Design Doc

Copy this table into your **design document** under
_"Bonus Merit: Domain-Specific Fine-Tuning Evidence"_:

```
Model              ROUGE-1    Domain Cov    Composite
Base (Qwen2.5-3B)   0.XXX      0.XXX         XX.XX/100
Fine-tuned (QLoRA)  0.XXX      0.XXX         XX.XX/100
Delta               +0.XXX     +0.XXX        +X.XX pts
```

Replace the X values with the actual numbers from `eval_results.json`.
A composite gain of +5 to +20 pts on 50 held-out examples is strong evidence
that the model adapted to steel-plant maintenance vocabulary and answer patterns.

The verdict line (`"CLEAR IMPROVEMENT"` / `"MARGINAL IMPROVEMENT"`) can be
quoted verbatim in the doc.

---

## Local Ollama Inference (after downloading GGUF)

```bash
mkdir ~/maintenance-wizard
cp maintenance_wizard_q4_k_m.gguf ~/maintenance-wizard/
cp Modelfile ~/maintenance-wizard/
cd ~/maintenance-wizard
ollama create maintenance-wizard -f ./Modelfile
ollama run maintenance-wizard
```

Then:
```
>>> What are the common failure modes of a rolling mill bearing?
```

---

## Optional: Push to HuggingFace Hub

Uncomment the HF push cell in the notebook, fill in your `HF_TOKEN` and repo name.
The LoRA adapter (~100 MB) will be pushed to `your-username/maintenance-wizard-qwen25-3b-lora`.

---

## Standalone eval_finetune.py usage

If you already have output files from separate base + fine-tuned runs:

```bash
python eval_finetune.py \
  --before before_outputs.jsonl \
  --after  after_outputs.jsonl
```

Each JSONL line: `{"generated": "...", "reference": "..."}`

Outputs a comparison table + saves `eval_results.json`.
