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

| 指标     | 用途                                               |
| -------- | -------------------------------------------------- |
| Top-1    | 是否猜中老师着法                                   |
| Top-3    | 老师着法是否在前三候选                             |
| 对战胜率 | PolicyNet vs 猪八戒启发（`gomoku_ml.eval_vs_zhu`） |

入口：`bash scripts/eval_vs_zhu.sh [path/to/model.pt]`（默认取最新 `artifacts/freestyle-v1/*/model.pt`）。

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

## 7. 快速验证与提升阶梯（R2）

经验量级（freestyle / tang，约 80 局面/局，生成约 10 局/分钟）：

| 对局数  | 约局面   | 生成耗时    | 用途                              |
| ------- | -------- | ----------- | --------------------------------- |
| 20      | ~1.6k    | ~2 分钟     | 只验管线，实力不可当真            |
| 100     | ~8k      | ~10 分钟    | 第一档认真实验，看 Top-k 是否起来 |
| 200–300 | ~16k–24k | ~20–30 分钟 | 推荐起步档；再谈对猪八戒胜率      |
| 500     | ~40k     | ~50 分钟    | 冲胜率前较舒服的一档              |
| 1000    | ~80k     | ~100 分钟   | 确认曲线在涨后再上                |

**短时间验证「还有没有提升空间」**（优先用现有数据，不必先开 1000）：

1. **加长训练（约 1–2 分钟）**：同一 JSONL，`epochs` 10→30（或 50），对比 val Top-1/Top-3，并对猪八戒打 20 局（`GAMES=20 bash scripts/eval_vs_zhu.sh <ckpt>`）。
   - Top-k 与胜率都升 → 多训有用，值得加数据。
   - 仅 Top-k 升、胜率几乎不动 → 需加数据或改结构，而非只加 epoch。
2. **小步加数据（约 10–15 分钟生成）**：再生成约 100 局 tang，合并重训后同一套 `eval_vs_zhu` 对比。
   - 胜率明显上升 → 可继续堆到 500。
   - 几乎不动 → 考虑加深网络 / 非法点 mask / 旋转增强，再堆数据。

**中期手段**（确认曲线在涨之后）：500 局；`channels` 32→64 或多一层 conv；freestyle 旋转/镜像增强；评测固定 seed、黑白各半，并看 `score_rate`（胜 + 0.5 和）。

R2 评测口径：Top-k + 对猪八戒「不崩、可量化」；不要求追平唐僧。
