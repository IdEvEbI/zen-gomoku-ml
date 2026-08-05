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

| #   | 标题                                        | 描述                                                              | 对应    | 状态   |
| --- | ------------------------------------------- | ----------------------------------------------------------------- | ------- | ------ |
| 3   | **feat: 正式自由规则模仿训练**              | 接入产品仓大批量 `freestyle-v1` JSONL；可复现实验配置与 meta.json | R2      | 进行中 |
| 4   | **feat: 正式禁手规则模仿训练**              | 同流水线、`renju-cn-v1` 独立模型；禁止混规则                      | R2      | 待开始 |
| 5   | **feat: 评测增强（对猪八戒级 Agent 胜率）** | headless 对弈评测脚本；与 Top-k 互补                              | R2      | 待开始 |
| 6   | **docs: ONNX 交付约定与产品仓 R3 接口说明** | 输入输出张量、规则绑定、版本目录结构                              | R2 → R3 | 待开始 |

### Backlog #3 验收标准

- [x] `configs/freestyle-v1.json` 可驱动训练；CLI 可覆盖超参
- [x] 产物写入 `artifacts/freestyle-v1/<run_id>/`，含 `meta.json`（seed、超参、数据、环境）与 `config.snapshot.json`
- [x] 支持 `data/teacher/freestyle-v1*.jsonl`；`scripts/train_freestyle.sh` 可一键跑
- [x] `npm run test` 通过；sample 或 teacher 数据可完成至少一次正式配置训练并导出 ONNX

> 注：当前本地 teacher 仅少量对局；「大批量」需在产品仓加大 `--count` 后拷贝再训。管线已就绪。

---

## 三、后续（可选）

| #   | 标题                | 描述                          |
| --- | ------------------- | ----------------------------- |
| —   | 自对弈数据闭环      | 属 alphazero-lite R4，勿抢跑  |
| —   | 更强网络 / 数据增强 | 在 Top-k 与对战胜率瓶颈后再做 |

创建 GitHub Issue 时复制标题与验收标准，并在描述中注明「Backlog §x」。
