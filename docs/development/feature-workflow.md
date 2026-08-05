# Feature 开发与 PR 合并后流程

与产品仓约定一致，保证 Agent / 协作者操作可重复。

## PR 合并后的标准步骤

1. **切到 develop 并拉取**：`git checkout develop` → `git pull origin develop`
2. **删除已合并本地分支**：确认一致后 `git branch -d feature/<分支名>`
3. **按 Backlog 开下一 Issue 分支**：读 `docs/project/issue-backlog.md`，`git checkout -b feature/<新分支名>`

## 开始新 Issue 开发时

1. 确认在正确的 feature 分支。
2. **规格先行**：阅读 Backlog 与 `docs/requirements/`、`docs/design/`；必要时先改文档再写代码（见 [spec-driven-development.md](./spec-driven-development.md)）。
3. **实现 → 自测**：`npm run test`；涉及训练时跑 `scripts/smoke_train.sh` 或等价命令。
4. **文档格式**：改 Markdown 后 `npm run format:check`（失败则 `npm run format`）。
5. **提交与推送**：Conventional Commits，含 Issue 编号；husky + lint-staged 会格式化暂存的 md/json；勿随意 `--no-verify`。
6. **开 PR**：Base 选 **`develop`**，可写 `Closes #<Issue>`。

## 分支命名建议

| 类型      | 示例                        |
| --------- | --------------------------- |
| 新功能    | `feature/policy-net-deeper` |
| 文档/修复 | `docs/xxx`、`bugfix/xxx`    |
