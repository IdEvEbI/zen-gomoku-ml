"""Tests for experiment config / meta helpers."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from gomoku_ml.experiment import (
    build_meta,
    default_out_dir,
    load_json_config,
    write_meta,
)

ROOT = Path(__file__).resolve().parents[1]


class ExperimentTests(unittest.TestCase):
    def test_load_freestyle_config(self) -> None:
        cfg = load_json_config(ROOT / "configs" / "freestyle-v1.json")
        self.assertEqual(cfg["rules"], "freestyle-v1")
        self.assertIn("seed", cfg)
        self.assertIn("epochs", cfg)

    def test_default_out_dir(self) -> None:
        p = default_out_dir("freestyle-v1", run_id="20260101T000000Z")
        self.assertEqual(p, Path("artifacts/freestyle-v1/20260101T000000Z"))

    def test_write_meta_roundtrip(self) -> None:
        meta = build_meta(
            repo_root=ROOT,
            rules="freestyle-v1",
            data_files=["data/sample/freestyle-v1.sample.jsonl"],
            config_path="configs/freestyle-v1.json",
            args={
                "epochs": 2,
                "batch_size": 8,
                "lr": 1e-3,
                "val_ratio": 0.2,
                "seed": 42,
                "channels": 32,
            },
            samples=10,
            train_n=8,
            val_n=2,
            checkpoint="artifacts/x/model.pt",
            onnx="artifacts/x/model.onnx",
            final_metrics={"top1": 0.1, "top3": 0.2},
        )
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "meta.json"
            write_meta(path, meta)
            loaded = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(loaded["rules"], "freestyle-v1")
        self.assertEqual(loaded["hyperparams"]["seed"], 42)
        self.assertIn("environment", loaded)


if __name__ == "__main__":
    unittest.main()
