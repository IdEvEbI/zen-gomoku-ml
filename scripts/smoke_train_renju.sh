#!/usr/bin/env bash
# Smoke: renju sample train + Top-k eval (rules isolation check).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
uv run python -m gomoku_ml.train \
  --config configs/renju-cn-v1.json \
  --data data/sample/renju-cn-v1.sample.jsonl \
  --epochs 2 \
  --batch-size 16 \
  --out artifacts/renju-smoke
uv run python -m gomoku_ml.eval \
  --rules renju-cn-v1 \
  --data data/sample/renju-cn-v1.sample.jsonl \
  --checkpoint artifacts/renju-smoke/model.pt
