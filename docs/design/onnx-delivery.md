# ONNX 交付约定与产品仓 R3 接口

本文档是 **zen-gomoku-ml → zen-gomoku（R3）** 的接口真源：张量约定、规则绑定、产物目录与推理侧义务。  
产品仓实现 `AlphaZeroAgent` / ONNX Runtime Web 时应直接引用本页；总路线仍见产品仓 [alphazero-lite.md](https://github.com/IdEvEbI/zen-gomoku/blob/develop/docs/design/alphazero-lite.md)。

训练数据流与评测见 [training-pipeline.md](training-pipeline.md)。Backlog §6。

---

## 1. 范围与非承诺

| 做                                              | 不做                                                                                                  |
| ----------------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| 按规则交付独立 `model.onnx` + `meta.json`       | 保证对猪八戒 / 人类可玩强度（当前纯模仿约 10% 量级，见 [training-pipeline §7](training-pipeline.md)） |
| 固定输入 / 输出名与形状，供 ORT Web / Node 加载 | 在 ONNX 内做禁手合法性或占用点 mask                                                                   |
| 规则切换 = 换模型文件，不混用权重               | 一份 ONNX 同时服务 freestyle 与 renju                                                                 |

产品 UI 接入时建议标注为 **实验级 AI**，直至对局胜率达到应用向目标。

---

## 2. 张量约定（契约）

导出实现：`gomoku_ml/model.py` → `export_onnx`（opset **18**）。

| 项       | 约定                                                               |
| -------- | ------------------------------------------------------------------ |
| 输入名   | `planes`                                                           |
| 输入形状 | `float32`，`(N, 3, 15, 15)`；`N` 为 batch（导出时 `dynamic_axes`） |
| 输出名   | `logits`                                                           |
| 输出形状 | `float32`，`(N, 225)`；未做 softmax                                |
| 棋盘     | 仅 **15×15**；行列下标均 `0..14`                                   |

### 2.1 特征通道（与训练一致）

`board[r][c]`：`0` 空、`1` 黑、`2` 白。行棋方由双方子数推断（黑先；子数相等则黑走）。

| Channel | 含义       | 取值                       |
| ------- | ---------- | -------------------------- |
| 0       | 黑子       | 有子 `1`，否则 `0`         |
| 1       | 白子       | 有子 `1`，否则 `0`         |
| 2       | 行棋方平面 | 黑走整盘 `1`，白走整盘 `0` |

编码参考：本仓 `gomoku_ml.dataset.encode_planes`；产品仓须 **逐通道对齐**，勿对调黑白或改 to-play 语义。

### 2.2 着法下标

```txt
index = row * 15 + col    // 行优先
row, col = divmod(index, 15)
```

`logits[i]` 对应交叉点 `(row, col)`。数值为 **未归一化 logit**；采样或 argmax 前由调用方处理。

### 2.3 合法性（调用方义务）

ONNX **不**屏蔽已占点，也 **不**处理 renju 禁手。

推荐（与本仓 `PolicyAgent` 一致）：

1. 对占用点（及 renju 下当前方禁手点）将对应 logit 置为很大的负数（如 `-1e9`），再 `argmax` 或 softmax 采样。
2. 若无合法点，返回认输 / 和棋，勿强行落子。

---

## 3. 规则绑定

| `rules`        | 含义       | 训练数据                 | 交付模型        |
| -------------- | ---------- | ------------------------ | --------------- |
| `freestyle-v1` | 自由五子棋 | 仅 `freestyle-v1*.jsonl` | 仅 freestyle 权 |
| `renju-cn-v1`  | 中国禁手   | 仅 `renju-cn-v1*.jsonl`  | 仅 renju 权     |

硬性约定：

- **一 run 一规则**：混规则训练会被本仓拒绝；产品仓也不得用 A 规则模型下 B 规则对局。
- **切换规则 = 切换 ONNX 会话**（卸载旧模型，加载对应 `rules` 文件）。
- `meta.json` / `config.snapshot.json` 中的 `rules` 必须与文件路径上的规则目录一致。

---

## 4. 产物目录与版本

训练落盘（可复现，Backlog #3）：

```txt
artifacts/<rules>/<run_id>/
  model.pt              # PyTorch；本仓评测 / 续训
  model.onnx            # R3 交付物
  meta.json             # 规则、超参、数据、Top-k、环境、git
  config.snapshot.json  # 当次有效配置快照
  vs_zhu.json           # 可选；对猪八戒评测结果
```

| 字段 / 路径段 | 说明                                                                                                            |
| ------------- | --------------------------------------------------------------------------------------------------------------- |
| `<rules>`     | `freestyle-v1` 或 `renju-cn-v1`                                                                                 |
| `<run_id>`    | UTC 时间戳，如 `20260806T020543Z`（`YYYYMMDDTHHMMSSZ`）                                                         |
| `channels`    | 在 `meta.json` → `hyperparams.channels` 与 checkpoint 内；**ONNX 图已含宽度**，加载 ONNX 时不必再建 `PolicyNet` |
| `augment`     | 仅影响训练；不改变推理张量契约                                                                                  |

### 4.1 交付给产品仓的推荐方式

1. 选定已评测的 `run_id`（看 `meta.json` / `vs_zhu.json`）。
2. 拷贝至少 `model.onnx` + `meta.json` 到产品仓静态资源，例如：

   ```txt
   zen-gomoku/public/models/<rules>/<run_id>/
     model.onnx
     meta.json
   ```

   或发布到 CDN / Release Asset，路径仍带 `<rules>/<run_id>`。

3. 产品配置指向该路径；**默认不要**静默使用「最新目录」，避免未评测产物进生产。

### 4.2 契约版本

当前契约记为 **`onnx-policy-v1`**（15×15、3 通道、`planes`/`logits`、opset 18）。

若未来变更通道数、棋盘大小、输入输出名或着法编码：

1. 递增契约版本号（如 `onnx-policy-v2`）；
2. 在 `meta.json` 增加 `onnx_contract` 字段（建议后续训练写入）；
3. 产品仓按版本分支加载逻辑，旧模型可并存。

加宽 `channels`（32→64）**不**破坏本契约（输入输出形状不变）。

---

## 5. 产品仓 R3 加载伪代码

```ts
// 按当前对局 rules 选择模型；勿混用
async function loadPolicy(rules: 'freestyle-v1' | 'renju-cn-v1', runId: string) {
  const base = `/models/${rules}/${runId}`
  const meta = await fetch(`${base}/meta.json`).then((r) => r.json())
  if (meta.rules !== rules) throw new Error('rules mismatch')
  const session = await ort.InferenceSession.create(`${base}/model.onnx`)
  return { session, meta }
}

function encodePlanes(board: number[][], toPlay: 1 | 2): Float32Array {
  // channel0 black, channel1 white, channel2 toPlay==1 ? 1 : 0
  // layout: NCHW → length 3*15*15, row-major within each channel
}

async function pickMove(session: ort.InferenceSession, board: number[][]) {
  const toPlay = /* 由子数推断 */ 1
  const planes = encodePlanes(board, toPlay)
  const feeds = { planes: new ort.Tensor('float32', planes, [1, 3, 15, 15]) }
  const out = await session.run(feeds)
  const logits = out.logits.data as Float32Array // length 225
  // mask occupied (+ renju forbidden), then argmax → (row, col)
}
```

与现有 `IAgent.getNextMove(board)` 对齐即可；会话勿放进 Pinia，由 Agent 实例持有。

浏览器端建议：ONNX Runtime Web（WASM）。体积与单步时延由产品仓自行验收（见 alphazero-lite §6）。

---

## 6. 自检清单（交付前）

- [ ] `meta.rules` 与目录 `<rules>` 一致
- [ ] 输入名 `planes`、输出名 `logits`；形状 `(1,3,15,15)` → `(1,225)`
- [ ] 产品侧通道顺序、to-play、下标与 §2 一致
- [ ] 推理侧已 mask 非法点（占用 / 禁手）
- [ ] freestyle / renju 各有独立文件，切换规则换会话
- [ ] UI 文案符合实力预期（实验级 vs 可玩）

---

## 7. 相关链接

| 文档                                                                                                  | 用途                   |
| ----------------------------------------------------------------------------------------------------- | ---------------------- |
| [training-pipeline.md](training-pipeline.md)                                                          | 训练 / 评测 / 提升阶梯 |
| [issue-backlog.md](../project/issue-backlog.md)                                                       | Backlog §6 验收        |
| [training-spec.md](../requirements/training-spec.md)                                                  | 功能规格               |
| [alphazero-lite.md](https://github.com/IdEvEbI/zen-gomoku/blob/develop/docs/design/alphazero-lite.md) | 产品仓总路线 / R3      |
