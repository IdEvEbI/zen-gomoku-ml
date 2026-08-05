"""猪八戒级启发 Agent（移植 zen-gomoku HeuristicAgent，仅 freestyle）。"""

from __future__ import annotations

import random
from dataclasses import dataclass

import numpy as np

from .board_game import BOARD_SIZE, Player, list_empty, next_player

OPPONENT_SCORE = (0, 200, 400, 2000, 10000)
SELF_SCORE = (0, 220, 420, 2400, 20000)
DEFAULT_NEIGHBOR_RADIUS = 2


def build_wins_table(board_size: int = BOARD_SIZE) -> tuple[list[list[list[bool]]], int]:
    wins: list[list[list[bool]]] = [
        [[] for _ in range(board_size)] for _ in range(board_size)
    ]
    # Pre-size each cell's list lazily via append index — use fixed list of bools
    # We'll grow winsCount and assign wins[r][c][k] = True by expanding lists.
    # Simpler: first count, then allocate.
    patterns: list[list[tuple[int, int]]] = []

    for row in range(board_size):
        for col in range(board_size - 4):
            patterns.append([(row, col + k) for k in range(5)])
    for col in range(board_size):
        for row in range(board_size - 4):
            patterns.append([(row + k, col) for k in range(5)])
    for row in range(board_size - 4):
        for col in range(board_size - 4):
            patterns.append([(row + k, col + k) for k in range(5)])
    for row in range(board_size - 4):
        for col in range(board_size - 1, 3, -1):
            patterns.append([(row + k, col - k) for k in range(5)])

    wins_count = len(patterns)
    wins = [
        [[False] * wins_count for _ in range(board_size)] for _ in range(board_size)
    ]
    for k, cells in enumerate(patterns):
        for r, c in cells:
            wins[r][c][k] = True
    return wins, wins_count


def build_wins_counts(
    board: np.ndarray,
    wins: list[list[list[bool]]],
    wins_count: int,
    player: Player,
) -> list[int]:
    counts = [0] * wins_count
    size = board.shape[0]
    for row in range(size):
        for col in range(size):
            cell = int(board[row, col])
            if cell not in (1, 2):
                continue
            for k in range(wins_count):
                if not wins[row][col][k]:
                    continue
                if cell == player:
                    if counts[k] != -1:
                        counts[k] += 1
                else:
                    counts[k] = -1
    return counts


def has_neighbor(
    board: np.ndarray, row: int, col: int, radius: int = DEFAULT_NEIGHBOR_RADIUS
) -> bool:
    size = board.shape[0]
    for dr in range(-radius, radius + 1):
        for dc in range(-radius, radius + 1):
            if dr == 0 and dc == 0:
                continue
            r, c = row + dr, col + dc
            if r < 0 or c < 0 or r >= size or c >= size:
                continue
            if int(board[r, c]) in (1, 2):
                return True
    return False


def list_neighbor_candidates(
    board: np.ndarray, radius: int = DEFAULT_NEIGHBOR_RADIUS
) -> list[tuple[int, int]]:
    empty = list_empty(board)
    stone_count = board.size - len(empty)
    if stone_count == 0:
        mid = board.shape[0] // 2
        return [(mid, mid)]
    if stone_count <= 2:
        return empty
    near = [(r, c) for r, c in empty if has_neighbor(board, r, c, radius)]
    return near if near else empty


def score_empty_cell(
    row: int,
    col: int,
    self_counts: list[int],
    opp_counts: list[int],
    wins: list[list[list[bool]]],
    wins_count: int,
    board_size: int,
) -> int:
    self_score = 0
    opp_score = 0
    for k in range(wins_count):
        if not wins[row][col][k]:
            continue
        oc = opp_counts[k]
        sc = self_counts[k]
        if 0 < oc <= 4:
            opp_score += OPPONENT_SCORE[oc]
        if 0 < sc <= 4:
            self_score += SELF_SCORE[sc]
    mid = (board_size - 1) / 2
    dist = abs(row - mid) + abs(col - mid)
    center = max(0, int(50 - dist * 3))
    return max(self_score, opp_score) + center


@dataclass
class ZhuHeuristicAgent:
    """Port of zen-gomoku HeuristicAgent for freestyle-v1."""

    board_size: int = BOARD_SIZE
    rng: random.Random | None = None

    def __post_init__(self) -> None:
        self.wins, self.wins_count = build_wins_table(self.board_size)
        self._rng = self.rng or random.Random()

    def get_next_move(self, board: np.ndarray) -> tuple[int, int] | None:
        empty = list_empty(board)
        if not empty:
            return None

        player = next_player(board)
        stone_count = self.board_size * self.board_size - len(empty)
        if stone_count == 0:
            mid = self.board_size // 2
            return mid, mid

        opp: Player = 2 if player == 1 else 1
        self_counts = build_wins_counts(board, self.wins, self.wins_count, player)
        opp_counts = build_wins_counts(board, self.wins, self.wins_count, opp)
        pool = list_neighbor_candidates(board)

        max_score = -1
        best: list[tuple[int, int]] = []
        for row, col in pool:
            total = score_empty_cell(
                row,
                col,
                self_counts,
                opp_counts,
                self.wins,
                self.wins_count,
                self.board_size,
            )
            if total > max_score:
                max_score = total
                best = [(row, col)]
            elif total == max_score:
                best.append((row, col))

        if not best or max_score <= 0:
            return self._rng.choice(empty)

        critical = min(OPPONENT_SCORE[4], SELF_SCORE[4])
        if stone_count < 8 and max_score < critical:
            scored = [
                (
                    score_empty_cell(
                        r,
                        c,
                        self_counts,
                        opp_counts,
                        self.wins,
                        self.wins_count,
                        self.board_size,
                    ),
                    (r, c),
                )
                for r, c in pool
            ]
            scored = [(s, m) for s, m in scored if s > 0]
            scored.sort(key=lambda x: x[0], reverse=True)
            top_n = scored[: min(3, len(scored))]
            if top_n:
                return self._rng.choice([m for _, m in top_n])

        return self._rng.choice(best)
