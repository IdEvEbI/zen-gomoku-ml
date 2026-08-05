"""Top-k accuracy against teacher moves."""

from __future__ import annotations

from typing import Sequence

import torch
from torch.utils.data import DataLoader

from .dataset import PositionDataset, Sample
from .model import PolicyNet


@torch.no_grad()
def topk_accuracy(
    model: PolicyNet,
    samples: Sequence[Sample],
    *,
    ks: tuple[int, ...] = (1, 3),
    batch_size: int = 64,
    device: torch.device | None = None,
) -> dict[str, float]:
    if not samples:
        return {f"top{k}": 0.0 for k in ks}
    device = device or torch.device("cpu")
    model.eval()
    loader = DataLoader(
        PositionDataset(samples), batch_size=batch_size, shuffle=False
    )
    hits = {k: 0 for k in ks}
    total = 0
    max_k = max(ks)
    for x, y in loader:
        x = x.to(device)
        y = y.to(device)
        logits = model(x)
        top = logits.topk(max_k, dim=1).indices
        total += y.size(0)
        for k in ks:
            hits[k] += (top[:, :k] == y.unsqueeze(1)).any(dim=1).sum().item()
    return {f"top{k}": hits[k] / total for k in ks}
