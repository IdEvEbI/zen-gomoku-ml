#!/usr/bin/env bash
# Formal renju-cn-v1 imitation run (Backlog #4).
# Expects teacher JSONL under data/teacher/ (copy from zen-gomoku).
# Do NOT mix freestyle-v1 files into this run.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

shopt -s nullglob
DATA_FILES=(data/teacher/renju-cn-v1*.jsonl)
if [[ ${#DATA_FILES[@]} -eq 0 ]]; then
  echo "No data/teacher/renju-cn-v1*.jsonl found."
  echo "In zen-gomoku:"
  echo "  npm run generate:teacher-records -- --rules renju-cn-v1 --count 50 --difficulty zhu"
  echo "Then:"
  echo "  mkdir -p data/teacher && cp ../zen-gomoku/data/teacher/renju-cn-v1-*.jsonl data/teacher/"
  exit 1
fi

# Guard: refuse if freestyle files are accidentally passed via glob mistakes
for f in "${DATA_FILES[@]}"; do
  case "$f" in
    *freestyle*)
      echo "Refusing freestyle file in renju run: $f"
      exit 1
      ;;
  esac
done

echo "Using ${#DATA_FILES[@]} renju-cn-v1 JSONL file(s):"
printf '  %s\n' "${DATA_FILES[@]}"

uv run python -m gomoku_ml.train \
  --config configs/renju-cn-v1.json \
  --data "${DATA_FILES[@]}" \
  "$@"

echo "Done. Check artifacts/renju-cn-v1/<run_id>/meta.json"
