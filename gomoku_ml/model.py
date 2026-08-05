"""Small policy network: board planes → 225 move logits."""

from __future__ import annotations

import torch
import torch.nn as nn
import torch.nn.functional as F

from .dataset import BOARD_SIZE, N_INTERSECTIONS


class PolicyNet(nn.Module):
    """Lite CNN policy head for imitation learning."""

    def __init__(self, channels: int = 32) -> None:
        super().__init__()
        self.conv1 = nn.Conv2d(3, channels, kernel_size=3, padding=1)
        self.conv2 = nn.Conv2d(channels, channels, kernel_size=3, padding=1)
        self.conv3 = nn.Conv2d(channels, channels, kernel_size=3, padding=1)
        self.head = nn.Conv2d(channels, 1, kernel_size=1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: (B, 3, 15, 15)
        h = F.relu(self.conv1(x))
        h = F.relu(self.conv2(h))
        h = F.relu(self.conv3(h))
        logits = self.head(h).view(-1, N_INTERSECTIONS)
        return logits


def export_onnx(
    model: PolicyNet,
    path: str,
    *,
    board_size: int = BOARD_SIZE,
) -> None:
    model.eval()
    dummy = torch.zeros(1, 3, board_size, board_size)
    torch.onnx.export(
        model,
        dummy,
        path,
        input_names=["planes"],
        output_names=["logits"],
        dynamic_axes={"planes": {0: "batch"}, "logits": {0: "batch"}},
        opset_version=18,
    )
