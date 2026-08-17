"""
eval_finetune.py
----------------
Standalone before/after metric helper for the QLoRA fine-tune eval.

Usage (standalone):
    python eval_finetune.py \
        --before before_outputs.jsonl \
        --after  after_outputs.jsonl  \
        --eval   maintenance_eval_50.jsonl

Each *_outputs.jsonl line: {"generated": "...", "reference": "..."}
The eval JSONL line:        {"instruction": "...", "input": "...", "output": "..."}

The notebook calls score_outputs() directly after in-memory generation.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Optional


# ---------------------------------------------------------------------------
# Token-level metrics (no heavy deps — runs inside Colab free tier)
# ---------------------------------------------------------------------------

def _tokenize(text: str) -> list[str]:
    """Lowercase word tokenizer — no NLTK needed."""
    return re.findall(r"\b\w+\b", text.lower())


def _precision_recall_f1(pred: str, ref: str) -> tuple[float, float, float]:
    pred_toks = set(_tokenize(pred))
    ref_toks = set(_tokenize(ref))
    if not pred_toks or not ref_toks:
        return 0.0, 0.0, 0.0
    common = pred_toks & ref_toks
    p = len(common) / len(pred_toks)
    r = len(common) / len(ref_toks)
    f1 = 2 * p * r / (p + r) if (p + r) > 0 else 0.0
    return p, r, f1


def _rouge_1(pred: str, ref: str) -> float:
    """Unigram ROUGE-1 F1 (lightweight, no rouge_score lib)."""
    _, _, f1 = _precision_recall_f1(pred, ref)
    return f1


def _exact_match(pred: str, ref: str) -> float:
    return 1.0 if pred.strip().lower() == ref.strip().lower() else 0.0


def _length_ratio(pred: str, ref: str) -> float:
    """Pred length / ref length — values far from 1.0 indicate hallucination or truncation."""
    ref_words = len(_tokenize(ref))
    pred_words = len(_tokenize(pred))
    if ref_words == 0:
        return 0.0
    return pred_words / ref_words


# ---------------------------------------------------------------------------
# Domain-specific quality signals for steel maintenance text
# ---------------------------------------------------------------------------

DOMAIN_KEYWORDS = [
    # maintenance actions
    "inspect", "replace", "lubricate", "align", "calibrate", "clean",
    "check", "repair", "overhaul", "monitor", "tighten", "adjust",
    # failure modes
    "wear", "crack", "corrosion", "vibration", "overheating", "leakage",
    "fatigue", "spalling", "misalignment", "contamination",
    # components
    "bearing", "seal", "coupling", "gear", "roll", "motor", "sensor",
    "hydraulic", "pneumatic", "conveyor", "furnace", "coil",
    # maintenance types
    "preventive", "predictive", "corrective", "cbm", "tpm",
]


def _domain_coverage(text: str) -> float:
    """Fraction of domain keywords present in the generated text."""
    toks = set(_tokenize(text))
    hits = sum(1 for kw in DOMAIN_KEYWORDS if kw in toks)
    return hits / len(DOMAIN_KEYWORDS)


# ---------------------------------------------------------------------------
# Core scoring function — called from notebook + CLI
# ---------------------------------------------------------------------------

def score_outputs(
    generated_list: list[str],
    reference_list: list[str],
    label: str = "model",
    verbose: bool = True,
) -> dict:
    """
    Score a list of generated outputs against reference outputs.

    Parameters
    ----------
    generated_list : list[str]  — model outputs (same order as reference_list)
    reference_list : list[str]  — ground-truth outputs from eval JSONL
    label          : str        — display name ("base" or "finetuned")
    verbose        : bool       — print per-example comparison

    Returns
    -------
    dict with aggregate metrics
    """
    assert len(generated_list) == len(reference_list), (
        f"Length mismatch: {len(generated_list)} generated vs {len(reference_list)} reference"
    )

    rouge1_scores, em_scores, length_ratios, domain_scores = [], [], [], []

    for i, (gen, ref) in enumerate(zip(generated_list, reference_list)):
        r1 = _rouge_1(gen, ref)
        em = _exact_match(gen, ref)
        lr = _length_ratio(gen, ref)
        dc = _domain_coverage(gen)

        rouge1_scores.append(r1)
        em_scores.append(em)
        length_ratios.append(lr)
        domain_scores.append(dc)

        if verbose and i < 5:
            print(f"\n--- Example {i+1} [{label}] ---")
            print(f"REF  : {ref[:200]}...")
            print(f"GEN  : {gen[:200]}...")
            print(f"ROUGE-1={r1:.3f}  EM={em:.0f}  LenRatio={lr:.2f}  Domain={dc:.3f}")

    n = len(rouge1_scores)
    results = {
        "label": label,
        "n": n,
        "rouge1_mean": sum(rouge1_scores) / n,
        "em_mean": sum(em_scores) / n,
        "length_ratio_mean": sum(length_ratios) / n,
        "domain_coverage_mean": sum(domain_scores) / n,
        # composite quality score (0-100) — ROUGE + domain coverage weighted
        "composite_quality": (
            0.5 * (sum(rouge1_scores) / n)
            + 0.5 * (sum(domain_scores) / n)
        ) * 100,
    }

    if verbose:
        print(f"\n{'='*60}")
        print(f"RESULTS [{label}] — {n} examples")
        print(f"  ROUGE-1 (mean)          : {results['rouge1_mean']:.4f}")
        print(f"  Exact Match             : {results['em_mean']:.4f}")
        print(f"  Length Ratio (mean)     : {results['length_ratio_mean']:.4f}")
        print(f"  Domain Coverage (mean)  : {results['domain_coverage_mean']:.4f}")
        print(f"  Composite Quality Score : {results['composite_quality']:.2f} / 100")
        print(f"{'='*60}\n")

    return results


def compare_scores(base_results: dict, ft_results: dict) -> dict:
    """Print a side-by-side delta table and return delta dict."""
    metrics = ["rouge1_mean", "em_mean", "length_ratio_mean",
               "domain_coverage_mean", "composite_quality"]
    deltas = {}
    print(f"\n{'METRIC':<30} {'BASE':>10} {'FINETUNED':>12} {'DELTA':>10}")
    print("-" * 65)
    for m in metrics:
        b = base_results.get(m, 0.0)
        f = ft_results.get(m, 0.0)
        d = f - b
        deltas[m] = d
        print(f"{m:<30} {b:>10.4f} {f:>12.4f} {d:>+10.4f}")
    print("-" * 65)
    gain = deltas["composite_quality"]
    print(f"\nComposite quality GAIN: {gain:+.2f} pts")
    if gain > 5:
        print("=> Fine-tune shows CLEAR improvement over base model.")
    elif gain > 0:
        print("=> Fine-tune shows MARGINAL improvement over base model.")
    else:
        print("=> Fine-tune did NOT improve over base — check training or data.")
    return deltas


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def _load_jsonl(path: str) -> list[dict]:
    rows = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description="Before/after fine-tune quality comparison")
    parser.add_argument("--before", required=True, help="JSONL with {generated, reference} for base model")
    parser.add_argument("--after",  required=True, help="JSONL with {generated, reference} for fine-tuned model")
    parser.add_argument("--eval",   required=False, help="Original eval JSONL (for reference cross-check)")
    args = parser.parse_args()

    before_rows = _load_jsonl(args.before)
    after_rows  = _load_jsonl(args.after)

    before_gen = [r["generated"] for r in before_rows]
    after_gen  = [r["generated"] for r in after_rows]
    refs       = [r["reference"] for r in before_rows]

    base_results = score_outputs(before_gen, refs, label="base")
    ft_results   = score_outputs(after_gen,  refs, label="finetuned")
    compare_scores(base_results, ft_results)

    # Optionally dump results JSON
    out = {"base": base_results, "finetuned": ft_results}
    out_path = Path(args.before).parent / "eval_results.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"\nResults saved to {out_path}")


if __name__ == "__main__":
    main()
