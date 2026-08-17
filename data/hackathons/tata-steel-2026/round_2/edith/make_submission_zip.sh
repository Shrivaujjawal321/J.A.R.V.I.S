#!/usr/bin/env bash
# Build the HackerEarth submission ZIP for THE EDITH.
# Usage: bash make_submission_zip.sh [slim]
#   default: full dataset + prebuilt RAG/ML artifacts (run-out-of-the-box)
#   slim   : drops the two derivable mega-CSVs + vectordb (rebuild scripts included)
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"     # .../round_2/edith
R2="$(cd "$HERE/.." && pwd)"              # .../round_2
OUT="$R2/EDITH_TataSteel_R2_submission.zip"
MODE="${1:-full}"

cd "$R2"
rm -f "$OUT"

EXCLUDES=(
  "edith/frontend/node_modules/*" "edith/frontend/.next/*"
  "edith/data/logs/*" "edith/data/reports/*" "edith/data/feedback.jsonl"
  "edith/data/alerts_history.jsonl" "edith/data/logbook.jsonl"
  "edith/rank1_audit_workflow.js" "edith/demo/narration/*" "edith/demo/EDITH_demo_final.webm" "edith/demo/page@*"
  "vulcan/vulcan/__pycache__/*" "vulcan/**/__pycache__/*" "vulcan/.pytest_cache/*"
  "vulcan/vulcan.egg-info/*" "vulcan/data/demo/*.tmp"
  "vulcan/data/sessions/*" "vulcan/data/feedback.db" "vulcan/data/alerts.db"
  "dataforge/datasets/*BACKUP*" "dataforge/web/*" "dataforge/api/__pycache__/*"
  "**/__pycache__/*" "**/.DS_Store" "**/*.pyc"
)
if [ "$MODE" = "slim" ]; then
  EXCLUDES+=(
    "dataforge/datasets/steel-maintenance-flagship/condition_monitoring/sensor_timeseries_long.csv"
    "dataforge/datasets/steel-maintenance-flagship/condition_monitoring/raw_sensor_timeseries.csv"
    "vulcan/data/vectordb/*"
  )
fi

# lean = HackerEarth-submittable (< 50 MB cap): ships code + dataset + prebuilt RAG
# index; ML models train on first launch (run.sh auto-builds). Demo video lives on
# the YouTube demo link, not in the ZIP.
ZIP_MODELS=(vulcan/data/models)
if [ "$MODE" = "lean" ]; then
  ZIP_MODELS=()
  EXCLUDES+=(
    "edith/demo/*.mp4" "edith/demo/*.webm" "edith/demo/narration/*"
    "vulcan/data/models/*"
  )
fi

X=(); for e in "${EXCLUDES[@]}"; do X+=( -x "$e" ); done

zip -r -q "$OUT" \
  edith \
  vulcan/vulcan vulcan/requirements.txt vulcan/pyproject.toml vulcan/README.md \
  "${ZIP_MODELS[@]}" vulcan/data/vectordb vulcan/data/demo \
  dataforge/datasets/steel-maintenance-flagship \
  dataforge/gen_condition_monitoring_v2.py dataforge/gen_operational_v2.py \
  dataforge/gen_structural_v2.py dataforge/gen_manifest_v2.py \
  official_PS/OFFICIAL_PS.md \
  QUICKSTART.md \
  "${X[@]}"

SIZE=$(du -h "$OUT" | cut -f1)
echo "ZIP: $OUT ($SIZE, mode=$MODE)"
echo "--- top-level contents ---"
unzip -l "$OUT" | awk '{print $4}' | grep -oE "^[^/]+/" | sort | uniq -c | sort -rn | head
echo "--- sanity: EDITH + document + dataset present? ---"
unzip -l "$OUT" | grep -cE "edith/SUBMISSION_DOCUMENT.md|edith/backend/main.py|edith/start.sh" || true
unzip -l "$OUT" | grep -c "steel-maintenance-flagship/SPEC/ground_truth_spine.json" || true
