# zen-gomoku-ml

五子棋 **模仿学习** 训练仓（AlphaZero-lite **R2**）。  
产品仓：[zen-gomoku](https://github.com/IdEvEbI/zen-gomoku) 负责规则、唐僧互打导出棋谱与浏览器对弈；本仓只做 **训练 / 评测 / 导出 ONNX**。

对应产品仓 Issue：[#60](https://github.com/IdEvEbI/zen-gomoku/issues/60)。设计见产品仓 `docs/design/alphazero-lite.md`。

## 协作方式（与产品仓对齐）

本仓采用与 zen-gomoku 相同的工程约定：

- **规格驱动开发（Spec-Driven Development）**：先定 `docs/` 规格与 Backlog，再写代码。说明见 [docs/development/spec-driven-development.md](docs/development/spec-driven-development.md)。
- **分支**：`main` + `develop`；功能从 `develop` 拉 `feature/*`，PR 合回 `develop`。
- **文档**：`docs/` kebab-case；中英文混排加空格；Prettier 统一 Markdown / JSON。
- **提交门禁**：husky + lint-staged（文档格式）+ commitlint；CI 跑 `format:check` 与 unittest。
- **Cursor**：`.cursor/rules/feature-workflow.mdc`（合并 PR 后切 develop、删分支、开下一 Issue）。

详见 [CONTRIBUTING.md](CONTRIBUTING.md)、[docs/README.md](docs/README.md)、[issue-backlog](docs/project/issue-backlog.md)。

## 目标与非目标

| 做                                            | 不做                      |
| --------------------------------------------- | ------------------------- |
| 读取产品仓 JSONL `GameRecord`（含 `rules`）   | Vue / Pinia UI            |
| `freestyle-v1` / `renju-cn-v1` **分开**训模型 | 混规则训同一模型          |
| Top-1 / Top-3 命中老师着法                    | 一上来追平唐僧            |
| 导出 ONNX 供产品仓 R3 加载                    | 完整 MLOps / 自对弈（R4） |

## 环境

- [uv](https://docs.astral.sh/uv/)（管理 Python 版本、虚拟环境与依赖；本地 / CI / 云端同一套命令）
- Python **3.12+**（由 `uv` 按 `.python-version` 自动准备，无需手动 `venv` / conda）
- Node **20+**（仅文档格式与 git hooks，不参与训练计算）

```bash
cd zen-gomoku-ml
# 安装 uv：https://docs.astral.sh/uv/getting-started/installation/
uv sync
npm install
```

日常命令用 `uv run`，**不必**先 `source .venv/bin/activate`（Cursor / 终端均适用）：

```bash
uv run python -m gomoku_ml.train --help
npm run test   # 内部已走 uv run
```

## 棋谱从哪来

在 **zen-gomoku** 产品仓：

```bash
npm run generate:teacher-records -- --rules freestyle-v1 --count 10 --difficulty zhu
# 产物：data/teacher/freestyle-v1-*.jsonl
```

拷贝到本仓：

```bash
mkdir -p data/teacher
cp ../zen-gomoku/data/teacher/freestyle-v1-*.jsonl data/teacher/
```

**禁止**把 `renju-cn-v1` 与 `freestyle-v1` 混进同一次训练。

## 快速跑通（内置小样本）

```bash
uv run python -m gomoku_ml.train \
  --rules freestyle-v1 \
  --data data/sample/freestyle-v1.sample.jsonl \
  --epochs 3 \
  --batch-size 8 \
  --out artifacts/freestyle-smoke

uv run python -m gomoku_ml.eval \
  --rules freestyle-v1 \
  --data data/sample/freestyle-v1.sample.jsonl \
  --checkpoint artifacts/freestyle-smoke/model.pt
```

或：`bash scripts/smoke_train.sh`。

## 怎么评估模型

1. **模仿准不准**：Top-1 / Top-3（`gomoku_ml.eval`）。
2. **实战弱不弱**（后续）：对猪八戒级 Agent 胜率；或回灌产品仓人机试玩。
3. **不要只看 loss**。

## 与产品仓的衔接

| 阶段 | 仓库       | 做什么                              |
| ---- | ---------- | ----------------------------------- |
| R1   | zen-gomoku | 唐僧互打导出 JSONL（已完成）        |
| R2   | **本仓**   | 小样本跑通 → 大数据重训 → 两份 ONNX |
| R3   | zen-gomoku | `AlphaZeroAgent` 按规则加载 ONNX    |
