# 项目文档索引

本目录存放开发规范与项目相关文档，按子目录与命名规则组织。

## 命名与结构约定

- **文件名**：统一使用 **kebab-case**（小写 + 连字符）。
- **目录**：
  - **development/**：开发流程、分支、规格驱动约定
  - **project/**：需求入口、设计入口、Issue Backlog
  - **requirements/**：需求规格
  - **design/**：技术设计

写作风格：中英文混排时，**中文与英文/数字之间加空格**（如「使用 PyTorch 训练」）；表格与列表由 Prettier 统一格式。

## 目录结构

```txt
docs/
├── README.md
├── development/
│   ├── branch-strategy.md
│   ├── feature-workflow.md
│   └── spec-driven-development.md
├── project/
│   ├── issue-backlog.md
│   ├── requirements.md
│   └── design.md
├── requirements/
│   └── training-spec.md
└── design/
    ├── training-pipeline.md
    ├── onnx-delivery.md
    └── teacher-distill-roadmap.md
```

## 开发文档

| 文档                                                                 | 说明                       |
| -------------------------------------------------------------------- | -------------------------- |
| [branch-strategy.md](development/branch-strategy.md)                 | 分支策略（main / develop） |
| [feature-workflow.md](development/feature-workflow.md)               | PR 合并后与开新 Issue 流程 |
| [spec-driven-development.md](development/spec-driven-development.md) | 规格驱动开发（SDD）约定    |

## 项目文档

| 文档                                         | 说明                 |
| -------------------------------------------- | -------------------- |
| [issue-backlog.md](project/issue-backlog.md) | Issue 清单与开发路线 |
| [requirements.md](project/requirements.md)   | 需求入口             |
| [design.md](project/design.md)               | 设计入口             |

## 需求与设计

| 文档                                                            | 说明                      |
| --------------------------------------------------------------- | ------------------------- |
| [training-spec.md](requirements/training-spec.md)               | 训练仓功能规格            |
| [training-pipeline.md](design/training-pipeline.md)             | 数据与训练管线设计        |
| [onnx-delivery.md](design/onnx-delivery.md)                     | ONNX 交付与 R3 接口       |
| [teacher-distill-roadmap.md](design/teacher-distill-roadmap.md) | 唐僧蒸馏 → 自对弈（草案） |

与产品仓 [zen-gomoku](https://github.com/IdEvEbI/zen-gomoku) 的 `docs/design/alphazero-lite.md` 互补：产品仓定路线与对弈规则，本仓定训练实现。
