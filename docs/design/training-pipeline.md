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

R3 张量 / 目录 / 加载约定见 **[onnx-delivery.md](onnx-delivery.md)**（契约 `onnx-policy-v1`）。

## 2. 特征

- Channel 0：黑子
- Channel 1：白子
- Channel 2：行棋方（黑行棋为 1，否则 0）

## 3. 模型

轻量 CNN + 1×1 得到 225 logits（见 `gomoku_ml/model.py`）。`channels` 可配（Backlog #7：32→64）。加宽/加深须保持 ONNX 输入输出约定，或在产物 meta 中标明版本。

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

### 7.1 数据量级（生成侧）

经验量级（freestyle / tang，约 40 局面/局量级，生成约 10 局/分钟）：

| 对局数 | 约局面 | 生成耗时  | 用途                           |
| ------ | ------ | --------- | ------------------------------ |
| 20     | ~0.8k  | ~2 分钟   | 只验管线，实力不可当真         |
| 200    | ~8k    | ~20 分钟  | 起步对照                       |
| 1000   | ~40k   | ~100 分钟 | 认真模仿档；**不够**当可玩人机 |

### 7.2 已跑对照结论（本地，2026-08）

同一评测：`eval_vs_zhu`，seed=42，黑白各半。推理侧已对占用点做 illegal mask。

| 设定                          | Val Top-1 | Val Top-3 | vs 猪八戒（40 局） |
| ----------------------------- | --------- | --------- | ------------------ |
| 200 tang / epochs=10          | ~20.5%    | ~41.9%    | ~2.5%              |
| 200 tang / epochs=30          | ~26.2%    | ~46.9%    | ~7.5%              |
| 1000 tang / epochs=30         | ~29.4%    | ~52.9%    | ~7.5%              |
| 200+1000 混训 / epochs=30     | ~30.4%    | ~53.9%    | ~2.5%（变差）      |
| 1000 + 8 向增强 + ch64 / ep30 | ~36.5%    | ~59.0%    | **~12.5%**         |

解读：

1. **加长 epochs**（10→30）对 Top-k 与胜率都有帮助。
2. **200→1000** 明显抬 Top-k，**胜率几乎不动** → 再堆同质 JSONL 性价比低。
3. **混入异源 / 未鉴定 teacher 文件** 可能伤胜率；正式对照应用单一、已鉴定批次。
4. **8 向增强 + channels 64**（Backlog #7）：Top-k 与胜率均升（7.5%→12.5%），结构手段有效，但仍远低于可玩门槛。
5. 纯 Policy + argmax 约 12% **仍不能投入可玩人机**；R2「不崩、可量化」≠ 应用向「稳定 >30–40%」。

### 7.3 Backlog #7 落地与后续决策

已落地：`configs/freestyle-v1-aug64.json`（`augment=true`、`channels=64`）；仅对 **train split** 做 8 向增强；`renju` 禁止 `--augment`。

```bash
uv run python -m gomoku_ml.train \
  --config configs/freestyle-v1-aug64.json \
  --data data/teacher/freestyle-v1-<tang-1000>.jsonl
GAMES=40 bash scripts/eval_vs_zhu.sh
```

决策：

- 增强+加宽 **有用**（胜率进入双位数）→ 可再小步试更深网络或轻微加同质数据。
- 距可玩（>30–40%）仍远 → **不要**指望再堆几千局模仿就上线；下一步见 Backlog **§8**（Policy 先验 + Minimax/αβ），ONNX 标实验级。
- 若 §8 后仍平台期 → 转 R4 自对弈（Policy+Value+MCTS），而非继续只加 JSONL。

### 7.4 口径

| 口径        | 含义                                                  |
| ----------- | ----------------------------------------------------- |
| R2 管线     | Top-k + 对猪八戒可量化；不要求追平唐僧                |
| 应用 / 可玩 | 对猪八戒稳定显著高于随机崩盘（目标 >30–40% 再谈体验） |
| R3 接入     | 可加载 ONNX；实力不足时 UI 标实验级即可               |

## 8. 跨仓中期路线（摘要）

详见 [teacher-distill-roadmap.md](teacher-distill-roadmap.md)。

1. **上游**唐僧威胁搜索人机 OK（[tang-seng-strength](https://github.com/IdEvEbI/zen-gomoku/blob/develop/docs/design/tang-seng-strength.md)）。
2. **本仓 §8**：Policy + αβ（现有弱模型也可先验证「搜索在外」）。
3. **本仓 §9**：强唐僧教师蒸馏（先小规模，再租机放大）。
4. **本仓 §10 / R4**：自对弈 MCTS；推理保持先验 + 搜索。
