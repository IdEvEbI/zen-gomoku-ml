#!/usr/bin/env bash
# Smoke: train a few epochs on bundled sample and print Top-k.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
python -m gomoku_ml.train \
  --rules freestyle-v1 \
  --data data/sample/freestyle-v1.sample.jsonl \
  --epochs 2 \
  --batch-size 16 \
  --out artifacts/freestyle-smoke
python -m gomoku_ml.eval \
  --rules freestyle-v1 \
  --data data/sample/freestyle-v1.sample.jsonl \
  --checkpoint artifacts/freestyle-smoke/model.pt
