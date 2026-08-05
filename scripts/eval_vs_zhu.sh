#!/usr/bin/env bash
# Evaluate freestyle PolicyNet vs 猪八戒 (zhu heuristic).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

CKPT="${1:-}"
if [[ -z "$CKPT" ]]; then
  # Latest freestyle run under artifacts/freestyle-v1/*/model.pt
  CKPT=$(ls -1dt artifacts/freestyle-v1/*/model.pt 2>/dev/null | head -1 || true)
fi
if [[ -z "$CKPT" || ! -f "$CKPT" ]]; then
  echo "Usage: bash scripts/eval_vs_zhu.sh [path/to/model.pt]"
  echo "Or place a freestyle run under artifacts/freestyle-v1/<run_id>/model.pt"
  exit 1
fi

GAMES="${GAMES:-50}"
OUT_DIR=$(dirname "$CKPT")
echo "checkpoint=$CKPT games=$GAMES"
uv run python -m gomoku_ml.eval_vs_zhu \
  --checkpoint "$CKPT" \
  --games "$GAMES" \
  --out "$OUT_DIR/vs_zhu.json"
