"""Train imitation policy from zen-gomoku teacher JSONL."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import torch
import torch.nn.functional as F
from torch.utils.data import DataLoader

from .dataset import (
    RuleId,
    load_jsonl_samples,
    train_val_split,
    PositionDataset,
)
from .metrics import topk_accuracy
from .model import PolicyNet, export_onnx


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Train gomoku imitation policy")
    p.add_argument(
        "--rules",
        required=True,
        choices=["freestyle-v1", "renju-cn-v1"],
        help="Must match every record in --data",
    )
    p.add_argument(
        "--data",
        nargs="+",
        required=True,
        help="One or more JSONL files from zen-gomoku export",
    )
    p.add_argument("--epochs", type=int, default=5)
    p.add_argument("--batch-size", type=int, default=32)
    p.add_argument("--lr", type=float, default=1e-3)
    p.add_argument("--val-ratio", type=float, default=0.2)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--out", type=str, default="artifacts/run")
    p.add_argument("--channels", type=int, default=32)
    return p.parse_args()


def main() -> None:
    args = parse_args()
    rules: RuleId = args.rules
    torch.manual_seed(args.seed)

    samples = load_jsonl_samples(args.data, rules=rules)
    if not samples:
        raise SystemExit("no samples loaded")
    train_s, val_s = train_val_split(
        samples, val_ratio=args.val_ratio, seed=args.seed
    )
    print(
        f"rules={rules} samples={len(samples)} "
        f"train={len(train_s)} val={len(val_s)}"
    )

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = PolicyNet(channels=args.channels).to(device)
    opt = torch.optim.Adam(model.parameters(), lr=args.lr)
    loader = DataLoader(
        PositionDataset(train_s),
        batch_size=args.batch_size,
        shuffle=True,
    )

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    for epoch in range(1, args.epochs + 1):
        model.train()
        total_loss = 0.0
        n = 0
        for x, y in loader:
            x, y = x.to(device), y.to(device)
            logits = model(x)
            loss = F.cross_entropy(logits, y)
            opt.zero_grad()
            loss.backward()
            opt.step()
            total_loss += loss.item() * y.size(0)
            n += y.size(0)
        avg = total_loss / max(n, 1)
        metrics = topk_accuracy(
            model, val_s or train_s, device=device, batch_size=args.batch_size
        )
        print(
            f"epoch {epoch}/{args.epochs} loss={avg:.4f} "
            f"top1={metrics['top1']:.3f} top3={metrics['top3']:.3f}"
        )

    ckpt = out / "model.pt"
    torch.save(
        {
            "rules": rules,
            "channels": args.channels,
            "state_dict": model.state_dict(),
        },
        ckpt,
    )
    onnx_path = out / "model.onnx"
    export_onnx(model.cpu(), str(onnx_path))
    meta = {
        "rules": rules,
        "samples": len(samples),
        "epochs": args.epochs,
        "checkpoint": str(ckpt),
        "onnx": str(onnx_path),
        "final_metrics": topk_accuracy(model, val_s or train_s),
    }
    (out / "meta.json").write_text(
        json.dumps(meta, indent=2) + "\n", encoding="utf-8"
    )
    print(f"wrote {ckpt} and {onnx_path}")


if __name__ == "__main__":
    main()
