"""PolicyNet agent: legal argmax over empty cells."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import torch

from .board_game import BOARD_SIZE, list_empty, next_player
from .dataset import encode_planes, index_to_move, move_to_index
from .model import PolicyNet


class PolicyAgent:
    def __init__(
        self,
        model: PolicyNet,
        *,
        device: torch.device | None = None,
    ) -> None:
        self.model = model
        self.device = device or torch.device("cpu")
        self.model.to(self.device)
        self.model.eval()

    @classmethod
    def from_checkpoint(
        cls, path: str | Path, *, device: torch.device | None = None
    ) -> PolicyAgent:
        try:
            ckpt = torch.load(path, map_location="cpu", weights_only=True)
        except TypeError:
            ckpt = torch.load(path, map_location="cpu")
        channels = int(ckpt.get("channels", 32))
        model = PolicyNet(channels=channels)
        model.load_state_dict(ckpt["state_dict"])
        return cls(model, device=device)

    @torch.no_grad()
    def get_next_move(self, board: np.ndarray) -> tuple[int, int] | None:
        empty = list_empty(board)
        if not empty:
            return None
        player = next_player(board)
        planes = encode_planes(board, player)
        x = torch.from_numpy(planes).unsqueeze(0).to(self.device)
        logits = self.model(x)[0].detach().cpu().numpy()
        # Mask illegal (occupied) cells
        mask = np.full(BOARD_SIZE * BOARD_SIZE, -1e9, dtype=np.float32)
        for r, c in empty:
            mask[move_to_index(r, c)] = 0.0
        scored = logits + mask
        idx = int(scored.argmax())
        return index_to_move(idx)
