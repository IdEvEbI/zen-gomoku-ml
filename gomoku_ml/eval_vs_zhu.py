"""Headless PolicyNet vs 猪八戒 (zhu heuristic) match evaluation."""

from __future__ import annotations

import argparse
import json
import random
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np

from .board_game import BOARD_SIZE, empty_board, next_player, place
from .policy_agent import PolicyAgent
from .zhu_heuristic import ZhuHeuristicAgent


@dataclass
class MatchStats:
    games: int
    model_wins: int
    zhu_wins: int
    draws: int
    model_as_black: int
    model_as_white: int

    @property
    def model_win_rate(self) -> float:
        return self.model_wins / self.games if self.games else 0.0

    @property
    def model_score_rate(self) -> float:
        """Win=1, draw=0.5 (common match scoring)."""
        if not self.games:
            return 0.0
        return (self.model_wins + 0.5 * self.draws) / self.games


def play_one(
    model: PolicyAgent,
    zhu: ZhuHeuristicAgent,
    *,
    model_is_black: bool,
    max_moves: int = BOARD_SIZE * BOARD_SIZE,
) -> str:
    """Return 'model' | 'zhu' | 'draw'."""
    board = empty_board()
    # Opening: tengen as black (same as teacher gen default seed)
    mid = BOARD_SIZE // 2
    winner = place(board, mid, mid, 1)
    moves = 1
    if winner is not None:
        return "model" if (winner == 1 and model_is_black) or (
            winner == 2 and not model_is_black
        ) else "zhu"

    while moves < max_moves:
        player = next_player(board)
        model_to_move = (player == 1 and model_is_black) or (
            player == 2 and not model_is_black
        )
        agent = model if model_to_move else zhu
        move = agent.get_next_move(board)
        if move is None:
            return "draw"
        row, col = move
        if board[row, col] != 0:
            # Illegal / bug: treat as loss for the side to move
            return "zhu" if model_to_move else "model"
        winner = place(board, row, col, player)
        moves += 1
        if winner is not None:
            model_won = (winner == 1 and model_is_black) or (
                winner == 2 and not model_is_black
            )
            return "model" if model_won else "zhu"
        if not np.any(board == 0):
            return "draw"
    return "draw"


def run_matches(
    checkpoint: Path,
    *,
    games: int = 50,
    seed: int = 42,
) -> MatchStats:
    rng = random.Random(seed)
    model = PolicyAgent.from_checkpoint(checkpoint)
    zhu = ZhuHeuristicAgent(rng=random.Random(seed + 1))

    stats = MatchStats(
        games=0,
        model_wins=0,
        zhu_wins=0,
        draws=0,
        model_as_black=0,
        model_as_white=0,
    )
    for i in range(games):
        model_is_black = i % 2 == 0
        if model_is_black:
            stats.model_as_black += 1
        else:
            stats.model_as_white += 1
        # re-seed zhu slightly per game for opening diversity
        zhu._rng = random.Random(rng.randint(0, 10**9))
        result = play_one(model, zhu, model_is_black=model_is_black)
        stats.games += 1
        if result == "model":
            stats.model_wins += 1
        elif result == "zhu":
            stats.zhu_wins += 1
        else:
            stats.draws += 1
        if (i + 1) % 10 == 0 or i + 1 == games:
            print(
                f"[{i + 1}/{games}] model={stats.model_wins} "
                f"zhu={stats.zhu_wins} draw={stats.draws} "
                f"win_rate={stats.model_win_rate:.3f}"
            )
    return stats


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Evaluate PolicyNet win rate vs 猪八戒 (zhu heuristic)"
    )
    p.add_argument("--checkpoint", required=True, help="Path to model.pt")
    p.add_argument("--games", type=int, default=50)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument(
        "--out",
        type=str,
        default=None,
        help="Optional JSON report path",
    )
    return p.parse_args()


def main() -> None:
    args = parse_args()
    ckpt = Path(args.checkpoint)
    if not ckpt.is_file():
        raise SystemExit(f"checkpoint not found: {ckpt}")
    stats = run_matches(ckpt, games=args.games, seed=args.seed)
    report = {
        **asdict(stats),
        "model_win_rate": stats.model_win_rate,
        "model_score_rate": stats.model_score_rate,
        "checkpoint": str(ckpt.resolve()),
        "opponent": "zhu-heuristic (ported from zen-gomoku HeuristicAgent)",
        "rules": "freestyle-v1",
        "seed": args.seed,
    }
    print(
        f"done games={stats.games} model_wins={stats.model_wins} "
        f"zhu_wins={stats.zhu_wins} draws={stats.draws} "
        f"win_rate={stats.model_win_rate:.3f} "
        f"score_rate={stats.model_score_rate:.3f}"
    )
    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(f"wrote {out}")


if __name__ == "__main__":
    main()
