"""Minimal freestyle board helpers for headless match eval."""

from __future__ import annotations

from typing import Literal

import numpy as np

BOARD_SIZE = 15
Player = Literal[1, 2]
DIRECTIONS = ((0, 1), (1, 0), (1, 1), (1, -1))


def empty_board(size: int = BOARD_SIZE) -> np.ndarray:
    return np.zeros((size, size), dtype=np.int8)


def next_player(board: np.ndarray) -> Player:
    n1 = int((board == 1).sum())
    n2 = int((board == 2).sum())
    return 1 if n1 == n2 else 2


def list_empty(board: np.ndarray) -> list[tuple[int, int]]:
    rows, cols = np.where(board == 0)
    return list(zip(rows.tolist(), cols.tolist(), strict=True))


def _count_dir(board: np.ndarray, row: int, col: int, dr: int, dc: int) -> int:
    player = int(board[row, col])
    if player not in (1, 2):
        return 0
    size = board.shape[0]
    n = 0
    r, c = row, col
    while 0 <= r < size and 0 <= c < size and int(board[r, c]) == player:
        n += 1
        r += dr
        c += dc
    return n


def line_length(board: np.ndarray, row: int, col: int) -> int:
    best = 0
    for dr, dc in DIRECTIONS:
        forward = _count_dir(board, row, col, dr, dc)
        backward = _count_dir(board, row, col, -dr, -dc)
        best = max(best, forward + backward - 1)
    return best


def check_winner_freestyle(
    board: np.ndarray, last_row: int, last_col: int
) -> Player | None:
    player = int(board[last_row, last_col])
    if player not in (1, 2):
        return None
    if line_length(board, last_row, last_col) >= 5:
        return player  # type: ignore[return-value]
    return None


def place(
    board: np.ndarray, row: int, col: int, player: Player
) -> Player | None:
    """Place stone; return winner or None if game continues (draw checked by caller)."""
    if board[row, col] != 0:
        raise ValueError(f"occupied cell {(row, col)}")
    board[row, col] = player
    return check_winner_freestyle(board, row, col)
