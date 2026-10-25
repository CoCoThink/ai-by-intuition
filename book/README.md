# 教材源码导览

读者只读一个 PDF；作者按章节维护 LaTeX 源码。[main.tex](main.tex) 是唯一入口，**章节顺序和章号只由其中的 `\input` 与 `\section` 决定**，文件名前缀不代表章号（多数文件名沿用了早期编号）。

构建方法见[仓库 README](../README.md#本地构建)，修改流程与检查命令见 [CONTRIBUTING.md](../CONTRIBUTING.md)。

## 前置部分

| 内容 | 源码 |
|---|---|
| 封面、目录 | [main.tex](main.tex) |
| 版权页 | [00h-colophon.tex](chapters/00h-colophon.tex) |
| 阅读路线与表示约定 | [00g-reading-routes.tex](chapters/00g-reading-routes.tex) |
| 开读前：五题入门自检 | [00j-entry-check.tex](chapters/00j-entry-check.tex) |
| 序章（在第一部分之前） | [00-guide.tex](chapters/00-guide.tex) |
| 部分开篇（为什么从这里开始、先想一想、地图）与收尾（回到开篇、累积复习、下一步） | [part-maps.tex](part-maps.tex)；累积复习 R 题由 [part-reviews.tex](part-reviews.tex) 生成；设计与维护见 [PART_BOOKENDS.md](../docs/PART_BOOKENDS.md) |

## 正文

前七部分为主线，第八、九部分为扩展路径。一个文件可能只是某章的后半部分（表中标“含”“续”）。

| 部分 | 章节源码（按印刷顺序） |
|---|---|
| 一 · 学习 | [函数](chapters/00-functions.tex)、[损失与梯度下降](chapters/16-loss-gradient.tex)（含[训练组织](chapters/18c-training-engineering.tex)）、[非线性](chapters/07-functions-relu.tex)、[反向传播](chapters/17-backpropagation.tex)（含[完整一步](chapters/18b-end-to-end-learning.tex)）、[泛化](chapters/18-generalization.tex) |
| 二 · 矩阵 | [向量与点积](chapters/01-vectors.tex)（续 [02](chapters/02-dot-product.tex)）、[矩阵乘法](chapters/03-matrix-multiplication.tex)、[MLP](chapters/10-mlp.tex) |
| 三 · 文字 | [Tokenizer](chapters/20a-tokenizer.tex)、[分类损失](chapters/20c-classification-loss.tex)、[Embedding](chapters/20-embeddings.tex)、[预测任务](chapters/20b-task-contract.tex) |
| 四 · 上下文 | [上下文缺口与 RNN](chapters/21a-context-gap.tex)（续 [21](chapters/21-rnn.tex)）、[Attention 的直觉](chapters/21c-naive-attention.tex)、[Q/K/V](chapters/21b-why-attention.tex)、[批量与因果注意力](chapters/11-softmax-memory.tex)、[位置与多头](chapters/22a-position-multihead.tex) |
| 五 · Transformer | [Block](chapters/22-transformer-architecture.tex)、[FFN 与输出头](chapters/10b-ffn-output-head.tex)、[三维前向](chapters/22b-token-to-output.tex)、[联合训练](chapters/22c-language-training.tex)、[逐词生成](chapters/23-llm-systems.tex)、[真实尺度](chapters/23a-from-toy-to-gpt.tex) |
| 六 · 助手 | [ICL](chapters/23aa-pretraining-icl.tex)、[后训练](chapters/23c-post-training.tex)、[测试时计算](chapters/23cc-test-time-compute.tex)、[RAG](chapters/23d-agent-systems.tex)、[工具与 Agent 循环](chapters/23d-agent-tools.tex)、[协议与多 Agent](chapters/23d-agent-protocols.tex)、[数据、训练与部署](chapters/23b-deployment-and-ecosystem.tex) |
| 七 · 架构 | [现代 Transformer](chapters/22d-modern-transformers.tex)、[技术判断](chapters/23e-tech-judgement.tex) |
| 八 · 视觉（扩展） | [CNN](chapters/19-cnn.tex)、[ViT 与视觉桥接](chapters/19b-vit.tex) |
| 九 · 联想记忆（扩展） | [外积与串扰](chapters/04-key-value-outer-product.tex)（续 [05](chapters/05-memory-interference.tex)）、[Delta 更新](chapters/06-better-linear-memory.tex)、[非线性读取](chapters/08-stacking-key-value.tex)（续 [09](chapters/09-nonlinearity-and-memory.tex)、[14](chapters/14-summary.tex)）、[容量](chapters/13-capacity.tex) |
| 终章 | [回到那四个 Token](chapters/23f-foundation-recap.tex) |

## 附录

| 附录 | 源码 |
|---|---|
| A 公式、数学与符号速查 | [00e](chapters/00e-core-formulas.tex)、[00b](chapters/00b-math-tools.tex)、[00c 符号表](chapters/00c-symbols.tex)、[30 优化器](chapters/30-optimizer-appendix.tex)、[00i 数据地图](chapters/00i-data-map.tex) |
| B 三维实验、复算与脚本 | [00f 中间量](chapters/00f-transformer-intermediates.tex)、[24e PyTorch 与脚本总表](chapters/24e-pytorch-lab.tex) |
| C 题库 · D 答案 | 由 [exercises.json](exercises.json) 生成 [25](chapters/25-exercise-bank.tex)、[27](chapters/27-answer-key.tex)；随堂自测答案 [28](chapters/28-chapter-checks.tex) 手写 |
| E 术语表与索引 | 源：[24-lexicon](chapters/24-lexicon.tex)、[24b](chapters/24b-modern-lexicon.tex)、[24d 英文映射](chapters/24d-english-index.tex)；生成：[24e 拼音主表](chapters/24e-bilingual-glossary.tex)、[24f 英文简表](chapters/24f-chinese-index.tex)；手写：[24c 概念图](chapters/24c-concept-map.tex) |
| F 来源 | [26-sources](chapters/26-sources.tex)，链接记录 [source-audit.json](source-audit.json) |
| G 版本与带日期断言 | [29-revision-notes](chapters/29-revision-notes.tex)，断言表由 [dated-claims.json](dated-claims.json) 生成 |

## 生成文件

下列文件不要手改；改源文件后运行生成器（命令表见 [AGENTS.md](../AGENTS.md#生成内容修改来源再运行生成器)）：

- `chapters/25-exercise-bank.tex`、`chapters/27-answer-key.tex`、`part-reviews.tex`、`chapter-practice.tex`
- `chapters/24e-bilingual-glossary.tex`、`chapters/24f-chinese-index.tex`、`../docs/TERM_OCCURRENCES.md`
- `figures/reference-qr.tex`、`../docs/REFERENCES.md`
- `chapters/29-revision-notes.tex` 中的断言表

## 其他文件

- `figures/`：TikZ 教学图，每张有语义的图都带 Figure、Caption 与中文替代文字。
- `smoke-tagging.tex`：CI 在整书构建前编译的最小 Tagged PDF 冒烟测试。
- `smoke-mathml*.tex`：仅由手动兼容性工作流使用，复现 LuaMML 的已知限制（见 [维护手册](../docs/MAINTENANCE.md#无障碍机器验收与边界)）。
