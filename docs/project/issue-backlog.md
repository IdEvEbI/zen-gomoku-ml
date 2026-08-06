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

## 三、实力提升（下一步）

| #   | 标题                                        | 描述                                                                           | 对应      | 状态   |
| --- | ------------------------------------------- | ------------------------------------------------------------------------------ | --------- | ------ |
| 8   | **feat: Policy 先验 + Minimax/αβ 浅层搜索** | ONNX/checkpoint 只出 logit；Python（及后续产品仓）用搜索选点，冲对猪八戒可用度 | R2 → 应用 | 待开始 |

### Backlog #8 验收标准

- [ ] 文档说明：ONNX **只**输出 225 维 logits（着法先验），**不含**搜索；搜索在推理侧完成
- [ ] 本仓 Python：`PolicyNet`/`model.pt` 作候选排序先验 + **Minimax + Alpha-Beta**（叶子可用现有赢法启发评估，对齐产品仓思路）
- [ ] CLI / 脚本可对指定 checkpoint 与局面（或完整对局）给出落子；`GAMES=40` 对猪八戒胜率相对纯 argmax 基线有对照表
- [ ] `npm run test` 通过（搜索与先验排序有单测或冒烟）
- [ ] 结论写入 training-pipeline：是否达到「可用」门槛（目标对猪八戒稳定 >30% 再谈体验）

> 注：沙/猪/孙/唐仍以**产品仓**为准；本仓猪八戒为 Python **移植**（评测用）。完整四级不必在本仓重做。  
> **推荐顺序**：产品仓先落地 [唐僧威胁搜索](https://github.com/IdEvEbI/zen-gomoku/blob/develop/docs/design/tang-seng-strength.md) 并人机验收 → 本仓 §8 原型可并行 → 大规模数据走 §9。自对弈见 §10，勿与本项混为一谈。

---

## 四、中期路线（唐僧教师 → 蒸馏 → 自对弈）

真源说明见 [teacher-distill-roadmap.md](../design/teacher-distill-roadmap.md)。  
**前提**：上游唐僧增强人机测试通过后再开大规模 §9。

| #   | 标题                                | 描述                                                                 | 对应  | 状态 |
| --- | ----------------------------------- | -------------------------------------------------------------------- | ----- | ---- |
| 9   | **feat: 强唐僧教师蒸馏（阶段 1）**  | 用增强唐僧产谱/软标签；Policy(+Value) 蒸馏；先 1 万～10 万验证再放大 | R2→R4 | 草案 |
| 10  | **feat: 自对弈闭环（阶段 2 / R4）** | Policy+Value+MCTS；可从小棋盘课程升 15×15；目标超越固定教师          | R4    | 草案 |

### Backlog #9 验收标准（草案）

- [ ] 依赖上游唐僧增强已合并；教师生成说明写入 README / roadmap
- [ ] 支持强唐僧 JSONL（及规划中的 π/z 扩展）训练；规则仍分训
- [ ] 小规模跑通并对照：vs 猪八戒（argmax 与 §8 搜索各一表）
- [ ] 文档写清：租机放大前必须看到曲线；禁止「只堆 CE、推理无搜索」当成功标准
- [ ] `npm run test` 通过

### Backlog #10 验收标准（草案）

- [ ] 自对弈数据管线 + Policy/Value 更新循环（设计对齐 alphazero-lite R4）
- [ ] 擂台：相对 §9 教师或固定基准胜率可量化
- [ ] 与 `onnx-delivery` 契约协调（若输出增加 Value，升级契约版本）
- [ ] 明确 H5 推理：ONNX 先验 + 搜索/MCTS，而非裸 argmax

---

## 五、更后（可选）

| #   | 标题               | 描述                                                 |
| --- | ------------------ | ---------------------------------------------------- |
| —   | 产品仓接入搜索 AI  | R3 加载 ONNX 后，用本仓 §8 同构或产品仓 Minimax+先验 |
| —   | 禁手规则同等两阶段 | renju 独立教师与自对弈，禁止与 freestyle 混数        |

创建 GitHub Issue 时复制标题与验收标准，并在描述中注明「Backlog §x」。
