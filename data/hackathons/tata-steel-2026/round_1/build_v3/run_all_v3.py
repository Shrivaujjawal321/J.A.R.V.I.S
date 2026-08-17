"""
V3 Master Runner — runs all 6 steps in sequence, captures output.
Usage: python run_all_v3.py
"""

import subprocess
import sys
import os
import time

BASE_DIR = "/home/ujjwal/Documents/J.A.R.V.I.S./data/hackathons/tata-steel-2026/round_1/build_v3"
PYTHON   = "/home/ujjwal/Documents/J.A.R.V.I.S./.venv/bin/python"

STEPS = [
    ("01_shap_feature_selection.py",  "SHAP feature ranking (top 30)"),
    ("02_polynomial_features.py",     "Polynomial interactions (top 5, degree=2)"),
    ("03_base_models_oof.py",         "Base model OOF: LightGBM + XGBoost + CatBoost"),
    ("04_meta_learner.py",            "Meta-learner + Platt calibration"),
    ("05_score_aware_threshold.py",   "Score-aware threshold optimization"),
    ("06_predict_and_submit.py",      "Generate final submission"),
]

print("="*70)
print("V3 BUILD — TATA STEEL AI HACKATHON 2026 ROUND 1")
print("="*70)

results = []
t_global_start = time.time()

for script, desc in STEPS:
    script_path = BASE_DIR + "/" + script
    print(f"\n{'─'*70}")
    print(f"STEP: {desc}")
    print(f"{'─'*70}")
    t_start = time.time()

    result = subprocess.run(
        [PYTHON, script_path],
        capture_output=False,   # print live output
        text=True,
    )

    elapsed = time.time() - t_start
    ok = (result.returncode == 0)
    results.append((script, desc, ok, elapsed))

    if ok:
        print(f"\nSTEP OK  ({elapsed:.0f}s)")
    else:
        print(f"\nSTEP FAILED  (rc={result.returncode}, {elapsed:.0f}s)")
        print("STOPPING — fix error before continuing")
        break

total_elapsed = time.time() - t_global_start
print(f"\n{'='*70}")
print("V3 BUILD SUMMARY")
print(f"{'='*70}")
for script, desc, ok, elapsed in results:
    status = "OK" if ok else "FAILED"
    print(f"  [{status:6s}] {desc:<50} {elapsed:.0f}s")

n_ok = sum(1 for _, _, ok, _ in results if ok)
print(f"\n{n_ok}/{len(STEPS)} steps completed  |  Total: {total_elapsed:.0f}s")

if n_ok == len(STEPS):
    print("\nBUILD V3 COMPLETE. Check submission_v3.zip and BUILD_V3_REPORT.md")
