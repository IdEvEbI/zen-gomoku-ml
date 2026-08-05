# 规格驱动开发 (Spec-Driven Development)

你口头说的「文档驱动开发」，在业界当前更常见的叫法是：

| 叫法                              | 含义                                                | 与我们的关系                          |
| --------------------------------- | --------------------------------------------------- | ------------------------------------- |
| **Spec-Driven Development (SDD)** | 先写清规格/验收，再实现；规格作为人与 AI 的共同真源 | **本仓主称呼**                        |
| Spec-first                        | 先写文档指导首轮实现，之后文档可能滞后              | 入门形态                              |
| Spec-anchored                     | 规格持续维护，与代码演进对齐                        | **我们目标**（合入功能时同步改 docs） |
| Design Doc / RFC                  | 较大变更先设计评审                                  | 复杂训练改动时使用 `docs/design/`     |

参考（公开资料）：IBM / Microsoft / Martin Fowler 等对 SDD 的讨论——强调 **先对齐意图与验收，再让人与 AI 编码**。

## 本仓实践

1. **Backlog**（`docs/project/issue-backlog.md`）拆可关闭的 Issue，含验收标准。
2. **需求规格**（`docs/requirements/`）描述「要什么」。
3. **设计**（`docs/design/`）描述「怎么训、数据与评测约定」。
4. **再开 feature 分支写代码**；PR 中核对验收清单。
5. 行为变更时 **同一 PR 更新文档**，避免规格漂移。

与产品仓 [alphazero-lite](https://github.com/IdEvEbI/zen-gomoku/blob/develop/docs/design/alphazero-lite.md) 的关系：路线与双规则决策在产品仓；本仓规格聚焦数据格式、训练/评测/ONNX 交付。
