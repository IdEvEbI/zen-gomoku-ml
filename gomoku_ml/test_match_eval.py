"""Tests for freestyle board + zhu heuristic smoke."""

from __future__ import annotations

import unittest

import numpy as np

from gomoku_ml.board_game import empty_board, place, check_winner_freestyle
from gomoku_ml.zhu_heuristic import ZhuHeuristicAgent, build_wins_table


class BoardGameTests(unittest.TestCase):
    def test_five_in_row(self) -> None:
        b = empty_board()
        for c in range(4):
            place(b, 7, c, 1)
        self.assertIsNone(check_winner_freestyle(b, 7, 3))
        w = place(b, 7, 4, 1)
        self.assertEqual(w, 1)


class ZhuHeuristicTests(unittest.TestCase):
    def test_wins_table_count(self) -> None:
        _, n = build_wins_table(15)
        # 15*11*2 + 11*11*2 = 330 + 242 = 572
        self.assertEqual(n, 572)

    def test_opening_center(self) -> None:
        agent = ZhuHeuristicAgent(rng=__import__("random").Random(0))
        move = agent.get_next_move(empty_board())
        self.assertEqual(move, (7, 7))

    def test_responds_on_nonempty(self) -> None:
        agent = ZhuHeuristicAgent(rng=__import__("random").Random(0))
        b = empty_board()
        b[7, 7] = 1
        move = agent.get_next_move(b)
        self.assertIsNotNone(move)
        r, c = move  # type: ignore[misc]
        self.assertEqual(int(b[r, c]), 0)


if __name__ == "__main__":
    unittest.main()
