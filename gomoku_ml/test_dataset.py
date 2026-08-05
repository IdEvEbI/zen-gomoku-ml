"""Minimal unit tests (stdlib unittest; run: python -m unittest)."""

from __future__ import annotations

import unittest
from pathlib import Path

from gomoku_ml.dataset import load_jsonl_samples, encode_planes
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "data" / "sample" / "freestyle-v1.sample.jsonl"


class DatasetTests(unittest.TestCase):
    def test_load_sample_freestyle(self) -> None:
        samples = load_jsonl_samples([SAMPLE], rules="freestyle-v1")
        self.assertGreater(len(samples), 10)
        self.assertEqual(samples[0].planes.shape, (3, 15, 15))
        self.assertGreaterEqual(samples[0].move_index, 0)
        self.assertLess(samples[0].move_index, 225)

    def test_rules_mismatch_raises(self) -> None:
        with self.assertRaises(ValueError):
            load_jsonl_samples([SAMPLE], rules="renju-cn-v1")

    def test_encode_planes(self) -> None:
        board = np.zeros((15, 15), dtype=np.int8)
        board[7, 7] = 1
        planes = encode_planes(board, to_play=2)
        self.assertEqual(planes.shape, (3, 15, 15))
        self.assertEqual(planes[0, 7, 7], 1.0)
        self.assertEqual(planes[2, 0, 0], 0.0)


if __name__ == "__main__":
    unittest.main()
