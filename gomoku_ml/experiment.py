"""Load experiment configs and write reproducible meta.json."""

from __future__ import annotations

import json
import platform
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import torch


def load_json_config(path: str | Path) -> dict[str, Any]:
    p = Path(path)
    if not p.is_file():
        raise FileNotFoundError(f"config not found: {p}")
    data = json.loads(p.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"config must be a JSON object: {p}")
    return data


def utc_run_id() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def default_out_dir(rules: str, run_id: str | None = None) -> Path:
    rid = run_id or utc_run_id()
    return Path("artifacts") / rules / rid


def git_revision(repo_root: Path) -> str | None:
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=repo_root,
            stderr=subprocess.DEVNULL,
            text=True,
        )
        return out.strip() or None
    except (OSError, subprocess.CalledProcessError):
        return None


def build_meta(
    *,
    repo_root: Path,
    rules: str,
    data_files: list[str],
    config_path: str | None,
    args: dict[str, Any],
    samples: int,
    train_n: int,
    val_n: int,
    checkpoint: str,
    onnx: str,
    final_metrics: dict[str, float],
) -> dict[str, Any]:
    return {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "rules": rules,
        "config": config_path,
        "data": [str(Path(p).resolve()) for p in data_files],
        "hyperparams": {
            "epochs": args["epochs"],
            "batch_size": args["batch_size"],
            "lr": args["lr"],
            "val_ratio": args["val_ratio"],
            "seed": args["seed"],
            "channels": args["channels"],
            "augment": bool(args.get("augment", False)),
            "raw_train_samples": args.get("raw_train_samples"),
        },
        "samples": samples,
        "train_samples": train_n,
        "val_samples": val_n,
        "checkpoint": checkpoint,
        "onnx": onnx,
        "final_metrics": final_metrics,
        "environment": {
            "python": platform.python_version(),
            "torch": torch.__version__,
            "cuda_available": torch.cuda.is_available(),
            "git": git_revision(repo_root),
        },
    }


def write_meta(path: Path, meta: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
