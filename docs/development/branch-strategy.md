# 分支策略 (Branch Strategy)

与产品仓 [zen-gomoku](https://github.com/IdEvEbI/zen-gomoku) 对齐：基于 Git Flow 的简化模型。

## 常设分支

| 分支      | 说明                               | 保护                         |
| --------- | ---------------------------------- | ---------------------------- |
| `main`    | 生产就绪（可对外引用的训练脚手架） | 建议：仅 PR 合并，需 CI 通过 |
| `develop` | 集成开发分支                       | 建议：仅 PR 合并，需 CI 通过 |

## 临时分支

| 类型 | 命名规范             | 从何拉取  | 合并到                  |
| ---- | -------------------- | --------- | ----------------------- |
| 功能 | `feature/<简短描述>` | `develop` | `develop`               |
| 修复 | `bugfix/<简短描述>`  | `develop` | `develop`               |
| 文档 | `docs/<简短描述>`    | `develop` | `develop`               |
| 热修 | `hotfix/<简短描述>`  | `main`    | `main` + 同步 `develop` |

## 工作流简述

1. 从 `develop` 拉 `feature/xxx`，开发完成后 PR 合并回 `develop`。
2. 稳定后由 `develop` → `main`（release PR 或定期同步）。
3. Issue 在 GitHub 创建，Backlog 见 `docs/project/issue-backlog.md`；PR 描述写 `Closes #<编号>`（默认分支若为 `main`，合并到 `develop` 时可能需手动关 Issue）。
