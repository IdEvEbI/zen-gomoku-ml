# Issue 清单与开发路线（Backlog）

本文档是训练仓的 **Issue Backlog**。工作方式与产品仓相同：规格 → Issue → feature 分支 → PR 合入 `develop`。

上游产品仓 Issue：[zen-gomoku#60](https://github.com/IdEvEbI/zen-gomoku/issues/60)（新建本仓）。

---

## 一、脚手架与工程约定（当前）

| #   | 标题                            | 描述                                                                   | 状态   |
| --- | ------------------------------- | ---------------------------------------------------------------------- | ------ |
| 1   | **chore: 仓库脚手架与训练冒烟** | 读 JSONL、训几步、Top-1/3、导出 ONNX；sample 数据可跑通                | 已落地 |
| 2   | **chore: 迁移产品仓协作约定**   | develop、docs、SDD、Prettier/husky/commitlint、Cursor feature-workflow | 已落地 |

---

## 二、训练能力（按优先级）

| #   | 标题                                         | 描述                                                              | 对应    | 状态   |
| --- | -------------------------------------------- | ----------------------------------------------------------------- | ------- | ------ |
| 3   | **feat: 正式自由规则模仿训练**               | 接入产品仓大批量 `freestyle-v1` JSONL；可复现实验配置与 meta.json | R2      | 已落地 |
| 4   | **feat: 正式禁手规则模仿训练**               | 同流水线、`renju-cn-v1` 独立模型；禁止混规则                      | R2      | 已落地 |
| 5   | **feat: 评测增强（对猪八戒级 Agent 胜率）**  | headless 对弈评测脚本；与 Top-k 互补                              | R2      | 已落地 |
| 6   | **docs: ONNX 交付约定与产品仓 R3 接口说明**  | 输入输出张量、规则绑定、版本目录结构                              | R2 → R3 | 已落地 |
| 7   | **feat: freestyle 增强与加宽（冲对局胜率）** | 8 向对称增强 + `channels` 64；现有 1000 局对照，勿先堆更大 JSONL  | R2      | 已落地 |

### Backlog #3 验收标准

- [x] `configs/freestyle-v1.json` 可驱动训练；CLI 可覆盖超参
- [x] 产物写入 `artifacts/freestyle-v1/<run_id>/`，含 `meta.json`（seed、超参、数据、环境）与 `config.snapshot.json`
- [x] 支持 `data/teacher/freestyle-v1*.jsonl`；`scripts/train_freestyle.sh` 可一键跑
- [x] `npm run test` 通过；sample 或 teacher 数据可完成至少一次正式配置训练并导出 ONNX

> 注：大批量棋谱在产品仓加大 `--count` 后拷贝再训。管线已就绪（GitHub #4 / PR #5）。

### Backlog #4 验收标准

- [x] `configs/renju-cn-v1.json` 可驱动独立训练；产物在 `artifacts/renju-cn-v1/<run_id>/`
- [x] `scripts/train_renju.sh` 只吃 `renju-cn-v1*.jsonl`；混入 freestyle 数据会失败
- [x] sample / teacher 至少完成一次 renju 配置训练并导出 ONNX
- [x] `npm run test` 通过；文档说明 freestyle / renju 分训、禁止混规则

> 注：大批量同样需产品仓加大 `--count` 后拷贝；本项打通独立 renju 管线。

### Backlog #5 验收标准

- [x] headless：PolicyNet（checkpoint）对阵猪八戒级启发 Agent（移植自产品仓 `HeuristicAgent`）
- [x] 黑白互换、统计 W/D/L 与胜率；结果可写入 `vs_zhu.json`
- [x] `scripts/eval_vs_zhu.sh` 可对最新 freestyle 产物一键评测
- [x] `npm run test` 通过

> 注：当前启发 Agent 为 Python 移植，与产品仓逻辑对齐；后续可用产品仓 Node 对局做交叉校验。R2 管线目标是「对猪八戒量级不崩、可量化」，**不是**「可上线人机」。  
> 本地对照实验与提升阶梯见 [training-pipeline.md §7](../design/training-pipeline.md)。

### Backlog #6 验收标准

- [x] 文档写清 ONNX 输入（`planes` 3×15×15）/ 输出（225 logits）、规则与产物目录绑定
- [x] 产品仓 R3 加载约定（按 `rules` 选模型、版本目录）可被产品仓直接引用
- [x] 与 `training-pipeline` / README 交叉链接，无规格漂移

> 真源：[onnx-delivery.md](../design/onnx-delivery.md)。可与实力提升并行；ONNX 约定不依赖高胜率。实力不足时，产品侧文案应标为实验级 AI。

### Backlog #7 验收标准

- [x] freestyle 训练支持 **8 向**（旋转 / 镜像）样本增强；可配置开关；`renju` 默认关闭（禁手不对称）
- [x] 支持 `channels` 32→64（配置 / CLI）；checkpoint 与 ONNX 仍可读
- [x] 用现有 **单一** tang≈1000 局（不混异源 JSONL）跑对照：基线 vs 增强+加宽；`epochs=30`，`GAMES=40` 写 `vs_zhu.json`
- [x] `npm run test` 通过；结论写入 [training-pipeline.md §7](../design/training-pipeline.md)
- [x] **关闭条件**：文档与 PR 说明决策——增强有效（~7.5%→~12.5%）但仍不可玩；下一步以 Policy+搜索为主，而非堆 JSONL

> 对照产物（本地）：`artifacts/freestyle-v1/20260806T020543Z/`（aug + ch64）。基线 `20260806T013945Z`（1000-only / ch32）。  
> 配置：`configs/freestyle-v1-aug64.json`。应用向目标（>30–40%）与 R2「不崩」分开看。

---

## 三、后续（可选）

| #   | 标题                    | 描述                                                                          |
| --- | ----------------------- | ----------------------------------------------------------------------------- |
| —   | 自对弈数据闭环          | 属 alphazero-lite R4，勿抢跑                                                  |
| —   | Policy + 浅层搜索       | §7 增强仍不够时：产品仓 Minimax / 先验排序包装 Policy；本仓可先只提供更强先验 |
| —   | 更大网络 / 更多同质数据 | 仅当 §7 对照显示胜率随增强/加宽上升后再做                                     |

创建 GitHub Issue 时复制标题与验收标准，并在描述中注明「Backlog §x」。
