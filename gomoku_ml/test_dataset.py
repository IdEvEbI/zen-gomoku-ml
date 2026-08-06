"""Minimal unit tests (stdlib unittest; run: python -m unittest)."""

from __future__ import annotations

import unittest
from pathlib import Path

import numpy as np

from gomoku_ml.dataset import (
    Sample,
    augment_sample_d4,
    encode_planes,
    index_to_move,
    load_jsonl_samples,
    move_to_index,
    transform_planes,
    _transform_rc,
)

ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "data" / "sample" / "freestyle-v1.sample.jsonl"
RENJU_SAMPLE = ROOT / "data" / "sample" / "renju-cn-v1.sample.jsonl"


class DatasetTests(unittest.TestCase):
    def test_load_sample_freestyle(self) -> None:
        samples = load_jsonl_samples([SAMPLE], rules="freestyle-v1")
        self.assertGreater(len(samples), 10)
        self.assertEqual(samples[0].planes.shape, (3, 15, 15))
        self.assertGreaterEqual(samples[0].move_index, 0)
        self.assertLess(samples[0].move_index, 225)

    def test_load_sample_renju(self) -> None:
        samples = load_jsonl_samples([RENJU_SAMPLE], rules="renju-cn-v1")
        self.assertGreater(len(samples), 0)
        self.assertEqual(samples[0].planes.shape, (3, 15, 15))

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

    def test_d4_augment_count_and_consistency(self) -> None:
        board = np.zeros((15, 15), dtype=np.int8)
        board[2, 5] = 1
        board[4, 8] = 2
        planes = encode_planes(board, to_play=1)
        move_r, move_c = 6, 9
        sample = Sample(
            planes=planes,
            move_index=move_to_index(move_r, move_c),
            rules="freestyle-v1",
        )
        aug = augment_sample_d4(sample)
        self.assertEqual(len(aug), 8)
        self.assertTrue(np.allclose(aug[0].planes, planes))
        self.assertEqual(aug[0].move_index, sample.move_index)
        for flip in (False, True):
            for k in range(4):
                expect_planes = transform_planes(planes, k=k, flip=flip)
                er, ec = _transform_rc(move_r, move_c, k=k, flip=flip)
                br, bc = _transform_rc(2, 5, k=k, flip=flip)
                wr, wc = _transform_rc(4, 8, k=k, flip=flip)
                match = next(
                    s
                    for s in aug
                    if s.move_index == move_to_index(er, ec)
                    and np.allclose(s.planes, expect_planes)
                )
                self.assertEqual(match.planes[0, br, bc], 1.0)
                self.assertEqual(match.planes[1, wr, wc], 1.0)
                self.assertEqual(match.planes[0, er, ec], 0.0)


if __name__ == "__main__":
    unittest.main()
