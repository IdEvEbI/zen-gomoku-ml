# 训练管线设计

## 1. 数据流

```txt
zen-gomoku generate:teacher-records
        ↓ JSONL (rules 分文件)
gomoku_ml.dataset.load_jsonl_samples
        ↓ Sample(planes 3×15×15, move_index)
PolicyNet → CE loss → checkpoint + ONNX
        ↓
gomoku_ml.eval Top-1 / Top-3
        ↓（R3）
zen-gomoku AlphaZeroAgent 按规则加载
```

## 2. 特征

- Channel 0：黑子
- Channel 1：白子
- Channel 2：行棋方（黑行棋为 1，否则 0）

## 3. 模型

轻量 CNN + 1×1 得到 225 logits（见 `gomoku_ml/model.py`）。后续可加深，但须保持 ONNX 输入输出约定或做版本号。

## 4. 评测

| 指标     | 用途                       |
| -------- | -------------------------- |
| Top-1    | 是否猜中老师着法           |
| Top-3    | 老师着法是否在前三候选     |
| 对战胜率 | P1：对启发级 Agent（待做） |

## 5. 规则隔离

一次训练 run 只接受一种 `rules`；数据中出现另一种直接报错。

## 6. 实验产物（可复现）

正式训练（Backlog #3）约定：

| 项       | 约定                                                          |
| -------- | ------------------------------------------------------------- |
| 配置     | `configs/<rules>.json`；CLI 可覆盖                            |
| 数据     | `data/teacher/<rules>-*.jsonl`（从产品仓拷贝，勿提交大文件）  |
| 产物目录 | `artifacts/<rules>/<UTC 时间戳>/`                             |
| 落盘     | `model.pt`、`model.onnx`、`meta.json`、`config.snapshot.json` |

`meta.json` 含 seed、超参、数据路径、样本数、Top-k、Python/torch 版本与 git revision。

入口脚本：

- freestyle：`bash scripts/train_freestyle.sh`
- renju：`bash scripts/train_renju.sh`（**禁止**与 freestyle JSONL 混训）
