"""Evaluate checkpoint Top-1 / Top-3 on teacher JSONL."""

from __future__ import annotations

import argparse
from pathlib import Path

import torch

from .dataset import RuleId, load_jsonl_samples, train_val_split
from .metrics import topk_accuracy
from .model import PolicyNet


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Eval gomoku imitation policy")
    p.add_argument("--rules", required=True, choices=["freestyle-v1", "renju-cn-v1"])
    p.add_argument("--data", nargs="+", required=True)
    p.add_argument("--checkpoint", required=True)
    p.add_argument("--val-ratio", type=float, default=0.2)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--batch-size", type=int, default=64)
    return p.parse_args()


def main() -> None:
    args = parse_args()
    rules: RuleId = args.rules
    samples = load_jsonl_samples(args.data, rules=rules)
    _, val_s = train_val_split(
        samples, val_ratio=args.val_ratio, seed=args.seed
    )
    eval_set = val_s or samples

    try:
        ckpt = torch.load(args.checkpoint, map_location="cpu", weights_only=True)
    except TypeError:
        ckpt = torch.load(args.checkpoint, map_location="cpu")
    if ckpt.get("rules") and ckpt["rules"] != rules:
        raise SystemExit(
            f"checkpoint rules={ckpt['rules']} != --rules {rules}"
        )
    model = PolicyNet(channels=int(ckpt.get("channels", 32)))
    model.load_state_dict(ckpt["state_dict"])
    metrics = topk_accuracy(model, eval_set, batch_size=args.batch_size)
    print(
        f"rules={rules} n={len(eval_set)} "
        f"top1={metrics['top1']:.4f} top3={metrics['top3']:.4f}"
    )
    print(f"checkpoint={Path(args.checkpoint)}")


if __name__ == "__main__":
    main()
