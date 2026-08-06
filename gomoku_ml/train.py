"""Train imitation policy from zen-gomoku teacher JSONL."""

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F
from torch.utils.data import DataLoader

from .dataset import (
    PositionDataset,
    RuleId,
    augment_samples_d4,
    load_jsonl_samples,
    train_val_split,
)
from .experiment import (
    build_meta,
    default_out_dir,
    load_json_config,
    write_meta,
)
from .metrics import topk_accuracy
from .model import PolicyNet, export_onnx

REPO_ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    pre = argparse.ArgumentParser(add_help=False)
    pre.add_argument("--config", type=str, default=None)
    pre_args, _ = pre.parse_known_args()
    cfg = load_json_config(pre_args.config) if pre_args.config else {}

    p = argparse.ArgumentParser(description="Train gomoku imitation policy")
    p.add_argument(
        "--config",
        type=str,
        default=None,
        help="JSON experiment config (e.g. configs/freestyle-v1.json)",
    )
    p.add_argument(
        "--rules",
        choices=["freestyle-v1", "renju-cn-v1"],
        default=cfg.get("rules"),
        help="Must match every record in --data",
    )
    p.add_argument(
        "--data",
        nargs="+",
        required=True,
        help="One or more JSONL files from zen-gomoku export",
    )
    p.add_argument("--epochs", type=int, default=int(cfg.get("epochs", 5)))
    p.add_argument(
        "--batch-size", type=int, default=int(cfg.get("batch_size", 32))
    )
    p.add_argument("--lr", type=float, default=float(cfg.get("lr", 1e-3)))
    p.add_argument(
        "--val-ratio", type=float, default=float(cfg.get("val_ratio", 0.2))
    )
    p.add_argument("--seed", type=int, default=int(cfg.get("seed", 42)))
    p.add_argument(
        "--channels", type=int, default=int(cfg.get("channels", 32))
    )
    # freestyle: config may enable 8-fold aug; renju should stay off (asymmetric).
    default_aug = bool(cfg.get("augment", False))
    p.add_argument(
        "--augment",
        action=argparse.BooleanOptionalAction,
        default=default_aug,
        help="8-fold rotation/mirror augment on train split (freestyle only)",
    )
    p.add_argument(
        "--out",
        type=str,
        default=None,
        help="Output directory (default: artifacts/<rules>/<utc_timestamp>)",
    )
    args = p.parse_args()
    if not args.rules:
        p.error("--rules is required (pass CLI or set rules in --config)")
    if args.augment and args.rules != "freestyle-v1":
        p.error("--augment is only supported for freestyle-v1 (renju is asymmetric)")
    return args


def seed_everything(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def main() -> None:
    args = parse_args()
    rules: RuleId = args.rules
    seed_everything(args.seed)

    samples = load_jsonl_samples(args.data, rules=rules)
    if not samples:
        raise SystemExit("no samples loaded")
    train_s, val_s = train_val_split(
        samples, val_ratio=args.val_ratio, seed=args.seed
    )
    raw_train_n = len(train_s)
    if args.augment:
        train_s = augment_samples_d4(train_s)
    print(
        f"rules={rules} samples={len(samples)} "
        f"train={len(train_s)} val={len(val_s)} "
        f"augment={args.augment}"
        + (f" (raw_train={raw_train_n})" if args.augment else "")
    )

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = PolicyNet(channels=args.channels).to(device)
    opt = torch.optim.Adam(model.parameters(), lr=args.lr)
    loader = DataLoader(
        PositionDataset(train_s),
        batch_size=args.batch_size,
        shuffle=True,
    )

    out = Path(args.out) if args.out else default_out_dir(rules)
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
            "seed": args.seed,
            "state_dict": model.state_dict(),
        },
        ckpt,
    )
    onnx_path = out / "model.onnx"
    export_onnx(model.cpu(), str(onnx_path))
    final_metrics = topk_accuracy(model, val_s or train_s)
    meta = build_meta(
        repo_root=REPO_ROOT,
        rules=rules,
        data_files=list(args.data),
        config_path=args.config,
        args={
            "epochs": args.epochs,
            "batch_size": args.batch_size,
            "lr": args.lr,
            "val_ratio": args.val_ratio,
            "seed": args.seed,
            "channels": args.channels,
            "augment": args.augment,
            "raw_train_samples": raw_train_n,
        },
        samples=len(samples),
        train_n=len(train_s),
        val_n=len(val_s),
        checkpoint=str(ckpt),
        onnx=str(onnx_path),
        final_metrics=final_metrics,
    )
    write_meta(out / "meta.json", meta)
    # Also dump the effective config for the run
    (out / "config.snapshot.json").write_text(
        json.dumps(
            {
                "rules": rules,
                **meta["hyperparams"],
                "data": list(args.data),
                "source_config": args.config,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"wrote {ckpt} and {onnx_path}")
    print(f"meta={out / 'meta.json'}")


if __name__ == "__main__":
    main()
