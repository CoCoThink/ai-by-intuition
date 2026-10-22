# V2 重构 · M0 现有教学资产与校验基线

> 采集日期：2026-10-22；来源：[book/main.tex](../book/main.tex)、[book/README.md](../book/README.md)、[ROADMAP.md](../ROADMAP.md) 和 [scripts/validate_book.py](../scripts/validate_book.py)。这是**迁移台账，不是新目录已完成的证明**。详见 [V2 实施计划](STRUCTURE_REDESIGN_PLAN.md)。

## 1. 当前状态（重排之前）

- **可出版基线：** v0.1.0（2026-10-22）的 99 页 PDF；正式版本、已发布的 SHA256SUMS、Tag/MathML/PDF/UA 机器验收详情见仓库 README；后续不能修改历史发布资产。
- **正文：** 5 个必读部分、2 个选读部分、附录；`main.tex` 引入 **47 个章节源文件**（下表逐条列出）。
- **图示：** 当前 GitHub 源树包含 14 个 `book/figures/` 图示源文件；已发布 PDF 自述包含 16 个 Figure/替代文字节点，两者口径不同，不应混用。
- **数学与排版：** 主线行向量；联想记忆为选读列向量；当前有显式 Pre-Norm、LayerNorm、双头和三步 SGD 样例，但“完整前向”省略了位置编码与 Norm。
- **工具与验证：** `scripts/validate_book.py` 的 `PARTS`、`REQUIRED`、`21` 张数据表、图示、`0.427` 和若干旧 LaTeX 公式字面值是当前版本约束，**重排时必须同步改验收，而非删掉相关质量检查**。
- **新实验资产：** `scripts/teaching_reference.py` 使用 NumPy 构建 d_model=3、完整一层 Pre-Norm Block、3 个位置联合交叉熵、全参数手写反传和有限差分检查；是 V2 教材写作基线，**尚未被当前 PDF 正文采用**。

## 2. 47 个源文件的去向（以当前 PDF 顺序）

| 当前顺序 | 源文件 | V2 目标位置 |
|---:|---|---|
| 1 | `book/chapters/00-guide.tex` | 序章 |
| 2 | `book/chapters/00b-math-tools.tex` | 附录 A |
| 3 | `book/chapters/00c-symbols.tex` | 附录 A |
| 4 | `book/chapters/00-functions.tex` | 1–2 |
| 5 | `book/chapters/01-vectors.tex` | 8 |
| 6 | `book/chapters/02-dot-product.tex` | 9 |
| 7 | `book/chapters/03-matrix-multiplication.tex` | 10 |
| 8 | `book/chapters/20-embeddings.tex` | 12–13 |
| 9 | `book/chapters/20b-task-contract.tex` | 14 |
| 10 | `book/chapters/07-functions-relu.tex` | 5 |
| 11 | `book/chapters/10-mlp.tex` | 6、11 |
| 12 | `book/chapters/16-loss-gradient.tex` | 3–4 |
| 13 | `book/chapters/17-backpropagation.tex` | 6 |
| 14 | `book/chapters/18b-end-to-end-learning.tex` | 6 |
| 15 | `book/chapters/18-generalization.tex` | 7 |
| 16 | `book/chapters/18c-training-engineering.tex` | 11 |
| 17 | `book/chapters/21-rnn.tex` | 16 |
| 18 | `book/chapters/21b-why-attention.tex` | 17 |
| 19 | `book/chapters/11-softmax-memory.tex` | 18 |
| 20 | `book/chapters/22a-position-multihead.tex` | 19 |
| 21 | `book/chapters/22-transformer-architecture.tex` | 18（掩码）、20（Block）、21（输出头） |
| 22 | `book/chapters/10b-ffn-output-head.tex` | 20–21 |
| 23 | `book/chapters/22b-token-to-output.tex` | 22 |
| 24 | `book/chapters/22c-language-training.tex` | 23 |
| 25 | `book/chapters/23-llm-systems.tex` | 24 |
| 26 | `book/chapters/22d-modern-transformers.tex` | 30 |
| 27 | `book/chapters/23c-post-training.tex` | 27 |
| 28 | `book/chapters/23d-agent-systems.tex` | 28 |
| 29 | `book/chapters/23b-deployment-and-ecosystem.tex` | 29 |
| 30 | `book/chapters/19-cnn.tex` | X1 |
| 31 | `book/chapters/04-key-value-outer-product.tex` | X2 |
| 32 | `book/chapters/05-memory-interference.tex` | X2 |
| 33 | `book/chapters/06-better-linear-memory.tex` | X2 |
| 34 | `book/chapters/08-stacking-key-value.tex` | X2 |
| 35 | `book/chapters/09-nonlinearity-and-memory.tex` | X2 |
| 36 | `book/chapters/14-summary.tex` | X2 |
| 37 | `book/chapters/13-capacity.tex` | X2 |
| 38 | `book/chapters/25-integrated-practice.tex` | 附录 B |
| 39 | `book/chapters/25b-modern-practice.tex` | 附录 B |
| 40 | `book/chapters/15-practice.tex` | 附录 B |
| 41 | `book/chapters/24-lexicon.tex` | 附录 D |
| 42 | `book/chapters/24b-modern-lexicon.tex` | 附录 D |
| 43 | `book/chapters/24c-concept-map.tex` | 序章图 / 附录 A |
| 44 | `book/chapters/24d-english-index.tex` | 附录 D |
| 45 | `book/chapters/27-answer-key.tex` | 附录 C |
| 46 | `book/chapters/28-chapter-checks.tex` | 附录 C |
| 47 | `book/chapters/26-sources.tex` | 附录 E |

**新写内容（目前尚无对应旧文件）：**第 1 章中的规则动机、第 15 章“孤立词与固定拼接的局限”、第 25 章完整尺度回收、第 26 章预训练与上下文学习、第 31 章整体技术判断，以及统一算例/扩展篇重组需要的新增段落。现有第 1 章可拆为新 1–2 章，不另造一套互相重复的文本。

## 3. 迁移时不得丢失的教学资产

| 资产 | 当前主要位置 | 后续目标与迁移检查 |
|---|---|---|
| “春天 / 花 / 开了 / 。”及 5 项词表 | `20-embeddings`、`20b-task-contract` | 新 12–14；保持 ID 和目标不变，初始向量改为三维 |
| 损失下降和参数更新 | `16-loss-gradient`、`17-backpropagation`、`18b-end-to-end-learning` | 新 3–6；去重复但保留从错误到更新的计算 |
| 过拟合与验证损失图 | `18-generalization` | 新 7；保留两类数据损失对照 |
| RNN 数值状态与 Attention Q/K/V 分配图 | `21-rnn`、`21b-why-attention` | 新 16–18；演示 RNN 局限与直接读取的改进 |
| 位置、缩放、两个头、因果 Mask | `22a-position-multihead`、`22-transformer-architecture` | 新 18–20；修退化位置向量，多头改独立四维例 |
| 输出头 SGD 翻转与前层 FFN/Value 联合更新 | `22b-token-to-output`、`22c-language-training` | 新 22–23；保留数学动机，主案例升级到三位置联合损失 |
| Agent 三泳道与授权、提示注入防护 | `23d-agent-systems` | 新 28；新故事链不牺牲真实执行边界 |
| RoPE、MoE、GQA/MLA、部署与量化/蒸馏/LoRA | `22d-modern-transformers`、`23b-deployment-and-ecosystem` | 新 29–31；按资源约束重新组织 |
| CNN/ViT 与联想记忆 | `19-cnn` 及原联想记忆 7 章 | X1 扩展 ViT；X2 压缩至 4 章并明确列向量 |
| 附录练习、答案、图谱、术语与索引 | `25*`、`24*`、`27*`、`28*` 等 | A–E 合并去重、精确小节回链、题目与答案顺序对应 |

## 4. 新版测试与自动出版的风险清单

1. `validate_book.py` 当前校验 **7 parts 和 47 个固定 input**；新 7 部分 + 2 扩展应改为新的结构定义与真实源文件清单。
2. 目前的表头机器校验严格写死 **21 张表**，重排可能增加 GPT 尺度表、减少附录表；改为新结构中的动态表数与每表首行 TH 约束，不能放松表头语义。
3. 源码检查中引用旧文件名、字面 Embedding 坐标 `(1,0)`、`(0,1)`、旧注意力数字、`0.427` 的断言，都需要在第 22–23 章启用新例时同步迁移到统一 NumPy 数据源；不能仅改教材而遗留不符的测试。
4. PDF 目前有完整公式关联、标签结构、图片替代文字、标题层级；调整 `main.tex`、`\part`、`\appendix`、图注时须编译并运行 PDF/UA-2 和 MathML-AF 验证。
5. 现有发布文件名和工作流仍含 `Volume-01`，除去封面字样需要审慎同步改 CI、发布说明及新版本号，不在本阶段随意重命名。
6. 重排必须保持**概念定义在首次引用之前**；不因把符号表挪到书末而制造悬空交叉链接。

## 5. M0 验收与下一步

- [x] 记录正式发布基线和当前 7 部分/47 源文件约束。
- [x] 每个旧源文件明确一个或多个新章去向；没有丢弃的旧章节。
- [x] 标出必须保留的数字资产、安全内容、链接和 CI 的硬编码风险。
- [x] NumPy 教学基线单独建档，与当前二维 PDF 并存，避免立即造成数字冲突。
- [ ] **实施中的动态核验：** 后续各批次迁移完成时，重新统计标签、章节顺序、图注、术语链接与新书统计量。

**继续按 M1→M2→M3 推进：**先把参考脚本接入 CI，之后改标量教学顺序，再迁移 d=3 词向量、Attention 与三位置联合训练。每批同步维护本台账与 [V2 计划](STRUCTURE_REDESIGN_PLAN.md) 的复选框。
