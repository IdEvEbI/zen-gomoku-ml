#!/usr/bin/env bash
# Formal freestyle-v1 imitation run (Backlog #3).
# Expects teacher JSONL under data/teacher/ (copy from zen-gomoku).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

shopt -s nullglob
DATA_FILES=(data/teacher/freestyle-v1*.jsonl)
if [[ ${#DATA_FILES[@]} -eq 0 ]]; then
  echo "No data/teacher/freestyle-v1*.jsonl found."
  echo "In zen-gomoku:"
  echo "  npm run generate:teacher-records -- --rules freestyle-v1 --count 50 --difficulty zhu"
  echo "Then:"
  echo "  mkdir -p data/teacher && cp ../zen-gomoku/data/teacher/freestyle-v1-*.jsonl data/teacher/"
  exit 1
fi

echo "Using ${#DATA_FILES[@]} freestyle JSONL file(s):"
printf '  %s\n' "${DATA_FILES[@]}"

uv run python -m gomoku_ml.train \
  --config configs/freestyle-v1.json \
  --data "${DATA_FILES[@]}" \
  "$@"

echo "Done. Check artifacts/freestyle-v1/<run_id>/meta.json"
