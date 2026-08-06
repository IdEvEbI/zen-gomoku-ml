"""Load zen-gomoku GameRecord JSONL into (board planes, move index) samples."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Iterator, Literal, Sequence

import numpy as np
import torch
from torch.utils.data import Dataset

RuleId = Literal["freestyle-v1", "renju-cn-v1"]
BOARD_SIZE = 15
N_INTERSECTIONS = BOARD_SIZE * BOARD_SIZE


@dataclass(frozen=True)
class Sample:
    """One supervised example: position before teacher move → flat move index."""

    planes: np.ndarray  # (3, 15, 15) float32 — black, white, to-play
    move_index: int  # row * 15 + col
    rules: str


def move_to_index(row: int, col: int, board_size: int = BOARD_SIZE) -> int:
    return row * board_size + col


def index_to_move(index: int, board_size: int = BOARD_SIZE) -> tuple[int, int]:
    return divmod(index, board_size)


def encode_planes(
    board: np.ndarray, to_play: int
) -> np.ndarray:
    """board: (15,15) with 0 empty, 1 black, 2 white."""
    black = (board == 1).astype(np.float32)
    white = (board == 2).astype(np.float32)
    play = np.full_like(black, 1.0 if to_play == 1 else 0.0)
    return np.stack([black, white, play], axis=0)


def iter_records(paths: Sequence[Path]) -> Iterator[dict]:
    for path in paths:
        text = path.read_text(encoding="utf-8")
        for line_no, line in enumerate(text.splitlines(), start=1):
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_no}: invalid JSON") from exc


def records_to_samples(
    records: Iterable[dict],
    *,
    rules: RuleId,
    board_size: int = BOARD_SIZE,
) -> list[Sample]:
    samples: list[Sample] = []
    for rec in records:
        rec_rules = rec.get("rules") or "freestyle-v1"
        if rec_rules != rules:
            raise ValueError(
                f"rules mismatch: expected {rules}, got {rec_rules}. "
                "Do not mix freestyle and renju in one training run."
            )
        size = int(rec.get("boardSize") or board_size)
        if size != board_size:
            raise ValueError(f"unsupported boardSize={size}")
        board = np.zeros((board_size, board_size), dtype=np.int8)
        moves = rec.get("moves") or []
        for move in moves:
            r = int(move["r"])
            c = int(move["c"])
            player = int(move["player"])
            if board[r, c] != 0:
                raise ValueError(f"occupied cell in record: ({r},{c})")
            planes = encode_planes(board, player)
            samples.append(
                Sample(
                    planes=planes,
                    move_index=move_to_index(r, c, board_size),
                    rules=rules,
                )
            )
            board[r, c] = player
    return samples


def load_jsonl_samples(
    data_paths: Sequence[str | Path],
    *,
    rules: RuleId,
) -> list[Sample]:
    paths = [Path(p) for p in data_paths]
    for p in paths:
        if not p.is_file():
            raise FileNotFoundError(p)
    return records_to_samples(iter_records(paths), rules=rules)


class PositionDataset(Dataset):
    def __init__(self, samples: Sequence[Sample]) -> None:
        self.samples = list(samples)

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, idx: int) -> tuple[torch.Tensor, torch.Tensor]:
        s = self.samples[idx]
        x = torch.from_numpy(s.planes)
        y = torch.tensor(s.move_index, dtype=torch.long)
        return x, y


def train_val_split(
    samples: Sequence[Sample],
    *,
    val_ratio: float = 0.2,
    seed: int = 42,
) -> tuple[list[Sample], list[Sample]]:
    rng = np.random.default_rng(seed)
    idx = np.arange(len(samples))
    rng.shuffle(idx)
    n_val = int(len(samples) * val_ratio) if len(samples) > 1 else 0
    val_idx = set(idx[:n_val].tolist())
    train, val = [], []
    for i, s in enumerate(samples):
        (val if i in val_idx else train).append(s)
    if not train:
        train = list(samples)
        val = []
    return train, val


def _transform_rc(
    row: int, col: int, *, k: int, flip: bool, n: int = BOARD_SIZE
) -> tuple[int, int]:
    """Map (row, col) under optional horizontal flip then k×90° CCW (np.rot90)."""
    r, c = row, col
    if flip:
        c = n - 1 - c
    for _ in range(k % 4):
        r, c = n - 1 - c, r
    return r, c


def transform_planes(
    planes: np.ndarray, *, k: int, flip: bool
) -> np.ndarray:
    """Apply D4 transform to (C, H, W) planes; matches `_transform_rc`."""
    out = planes
    if flip:
        out = np.flip(out, axis=2)
    if k % 4:
        out = np.rot90(out, k=k % 4, axes=(1, 2))
    return np.ascontiguousarray(out)


def augment_sample_d4(sample: Sample) -> list[Sample]:
    """Eight dihedral transforms (identity included). For freestyle only."""
    r0, c0 = index_to_move(sample.move_index)
    out: list[Sample] = []
    for flip in (False, True):
        for k in range(4):
            planes = transform_planes(sample.planes, k=k, flip=flip)
            r, c = _transform_rc(r0, c0, k=k, flip=flip)
            out.append(
                Sample(
                    planes=planes,
                    move_index=move_to_index(r, c),
                    rules=sample.rules,
                )
            )
    return out


def augment_samples_d4(samples: Sequence[Sample]) -> list[Sample]:
    expanded: list[Sample] = []
    for s in samples:
        expanded.extend(augment_sample_d4(s))
    return expanded
