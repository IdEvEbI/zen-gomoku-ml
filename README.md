# zen-gomoku-ml

五子棋 **模仿学习** 训练仓（AlphaZero-lite **R2**）。  
产品仓：[zen-gomoku](https://github.com/IdEvEbI/zen-gomoku) 负责规则、唐僧互打导出棋谱与浏览器对弈；本仓只做 **训练 / 评测 / 导出 ONNX**。

对应产品仓 Issue：[#60](https://github.com/IdEvEbI/zen-gomoku/issues/60)。设计见产品仓 `docs/design/alphazero-lite.md`。

## 目标与非目标

| 做 | 不做 |
|----|------|
| 读取产品仓 JSONL `GameRecord`（含 `rules`） | Vue / Pinia UI |
| `freestyle-v1` / `renju-cn-v1` **分开**训两个策略网 | 混规则训同一模型 |
| Top-1 / Top-3 命中老师着法 | 一上来追平唐僧 |
| 导出 ONNX 供产品仓 R3 加载 | 完整 MLOps / 自对弈闭环（R4） |

## 环境

- Python **3.11+**
- 建议虚拟环境

```bash
cd zen-gomoku-ml
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

CPU 即可跑通脚手架；有 GPU 时 PyTorch 会自动用。

## 棋谱从哪来

在 **zen-gomoku** 产品仓：

```bash
npm run generate:teacher-records -- --rules freestyle-v1 --count 10 --difficulty zhu
# 产物：data/teacher/freestyle-v1-*.jsonl
```

拷贝到本仓，例如：

```bash
mkdir -p data/teacher
cp ../zen-gomoku/data/teacher/freestyle-v1-*.jsonl data/teacher/
```

JSONL：每行一个 `GameRecord`：

```json
{"version":1,"boardSize":15,"moves":[{"r":7,"c":7,"player":1},...],"rules":"freestyle-v1","status":"black_win"}
```

**禁止**把 `renju-cn-v1` 与 `freestyle-v1` 混进同一次训练。

## 快速跑通（内置小样本）

仓库自带 `data/sample/freestyle-v1.sample.jsonl`（极小，仅用于冒烟）：

```bash
# 训练几步 + 导出 checkpoint / onnx
python -m gomoku_ml.train \
  --rules freestyle-v1 \
  --data data/sample/freestyle-v1.sample.jsonl \
  --epochs 3 \
  --batch-size 8 \
  --out artifacts/freestyle-smoke

# 评测 Top-1 / Top-3
python -m gomoku_ml.eval \
  --rules freestyle-v1 \
  --data data/sample/freestyle-v1.sample.jsonl \
  --checkpoint artifacts/freestyle-smoke/model.pt
```

正式数据换成 `data/teacher/*.jsonl`，加大 `--epochs` 即可。禁手同理：`--rules renju-cn-v1`。

## 怎么评估模型（小白说明）

1. **模仿准不准**：测试集上老师下一手是否落在模型 Top-1 / Top-3（本仓 `eval`）。
2. **实战弱不弱**（后续增强）：导出 ONNX 后在产品仓用人机对战猪八戒；或本仓加 headless 对弈脚本。
3. **不要只看 loss**：loss 下降只说明在拟合训练集。

## 目录

```
gomoku_ml/          # 数据、模型、训练、评测
configs/            # 规则相关默认超参（可选）
data/sample/        # 冒烟样本
data/teacher/       # 你从产品仓拷来的棋谱（gitignore）
artifacts/          # 训练产物（gitignore）
scripts/            # 辅助脚本
```

## 与产品仓的衔接

| 阶段 | 仓库 | 做什么 |
|------|------|--------|
| R1 | zen-gomoku | 唐僧互打导出 JSONL（已完成） |
| R2 | **本仓** | 小样本跑通 → 大数据重训 → 两份 ONNX |
| R3 | zen-gomoku | `AlphaZeroAgent` 按规则加载 ONNX |

## License

与产品仓对齐时再补；脚手架阶段保留私有/团队约定即可。
