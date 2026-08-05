# 训练仓功能规格 (Training Spec)

- **项目**：zen-gomoku-ml
- **版本**：v0.1（脚手架）
- **方法**：规格驱动开发（Spec-Driven Development），见 `docs/development/spec-driven-development.md`

## 1. 范围

- **做**：从产品仓 JSONL 棋谱做监督学习；按规则分训；Top-1/Top-3 评测；导出 ONNX。
- **不做**：产品 UI、混规则训练、本阶段自对弈闭环。

## 2. 功能需求

| 编号      | 功能         | 描述                                           | 优先级 | 状态   |
| --------- | ------------ | ---------------------------------------------- | ------ | ------ |
| T-REQ-001 | 加载老师棋谱 | 读取 JSONL `GameRecord`；校验 `rules` 一致     | P0     | 已实现 |
| T-REQ-002 | 模仿训练     | PolicyNet + cross-entropy；可配置 epochs/batch | P0     | 已实现 |
| T-REQ-003 | Top-k 评测   | 测试集 Top-1 / Top-3                           | P0     | 已实现 |
| T-REQ-004 | ONNX 导出    | 训练结束写出 `model.onnx`                      | P0     | 已实现 |
| T-REQ-005 | 双规则隔离   | `freestyle-v1` / `renju-cn-v1` 分跑、禁止混训  | P0     | 已实现 |
| T-REQ-006 | 对战胜率评测 | 对猪八戒级 Agent 的 headless 胜率              | P1     | 未实现 |
| T-REQ-007 | 大规模可复现 | 固定 seed、配置落盘、产物版本目录              | P1     | 已实现 |

## 3. 数据约定

- 来源：产品仓 `npm run generate:teacher-records`
- 格式：每行一个 JSON；字段含 `version`、`boardSize`、`moves`、`rules`、`status`
- 样本：每个老师着法前局面 → 着法下标 `row * 15 + col`
- 正式训练：拷贝到本仓 `data/teacher/`（gitignore）；用 `configs/<rules>.json` + `artifacts/<rules>/<run_id>/`

## 4. 验收（脚手架）

- [x] sample JSONL 可 `uv run python -m gomoku_ml.train` 跑通并导出 onnx
- [x] `npm run test`（unittest）通过
- [x] 协作约定（develop / docs / husky）与产品仓对齐
