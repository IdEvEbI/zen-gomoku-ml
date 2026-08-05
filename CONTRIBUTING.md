# 参与开发 (Contributing)

## 开发前

1. Clone 本仓库。
2. 安装 [uv](https://docs.astral.sh/uv/getting-started/installation/)，然后 `uv sync`（自动创建 `.venv` 并安装依赖；日常用 `uv run …`，无需手动 activate）。
3. `npm install`（安装 Prettier / husky / commitlint；`prepare` 会装 git hooks）。
4. 阅读 [分支策略](docs/development/branch-strategy.md)、[规格驱动](docs/development/spec-driven-development.md)。

## 开发流程

1. 从 `develop` 拉最新，创建 `feature/<name>`。
2. **先文档/验收，再编码**（Spec-Driven）。
3. 自测：`npm run test`；训练相关可跑 `bash scripts/smoke_train.sh`。
4. 文档：`npm run format:check`（中英文空格与表格对齐等由 Prettier + 人工约定保证）。
5. Conventional Commits 提交；PR Base 为 **`develop`**。

## 提交信息

同产品仓：`feat` / `fix` / `docs` / `chore` 等。示例：`feat: add top-k eval CLI (Closes #3)`。

## 规范门禁

- **husky pre-commit** → lint-staged → Prettier（`*.md` / `*.mdc` / `*.json`）
- **husky commit-msg** → commitlint
- **CI**：`format:check` + `unittest`

不要随意 `--no-verify`。
