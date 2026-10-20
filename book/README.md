# 全书目录 · AI by Intuition

**以下按阅读顺序排列，PDF 的章节编号自动生成。**

**唯一入口：** [`main.tex`](main.tex)；按知识依赖而非视频分集顺序排列。读者使用一本完整 PDF，作者按独立 `.tex` 源文件维护各主题。

## Ⅰ · 把问题变成数字

- [阅读指南](chapters/00-guide.tex)：一本书回答哪五个问题？
- [从函数认识模型](chapters/00-functions.tex)：参数是什么、怎样拟合数据？
- [向量](chapters/01-vectors.tex)：一串数字能表示什么？
- [点积与几何意义](chapters/02-dot-product.tex)：余弦定理为什么出现在向量里？
- [矩阵乘法](chapters/03-matrix-multiplication.tex)：行乘列、列加权，以及按行/按列的双色矩阵图卡
- [Embedding](chapters/20-embeddings.tex)：Token ID 如何变成向量？
- [任务输入与输出契约](chapters/20b-task-contract.tex)：Tokenizer、标签与词表输出的形状

## Ⅱ · 神经网络怎样学会预测

- [激活函数与 ReLU](chapters/07-functions-relu.tex)：为什么矩阵之间还要放函数？
- [MLP](chapters/10-mlp.tex)：两个矩阵和激活函数组成什么计算？
- [FFN 与词表输出头](chapters/10b-ffn-output-head.tex)：为什么这两类矩阵层用途不同
- [损失与梯度下降](chapters/16-loss-gradient.tex)：模型怎么知道参数朝哪里改？
- [反向传播](chapters/17-backpropagation.tex)：链式法则怎样传递梯度？
- [一次完整的学习过程](chapters/18b-end-to-end-learning.tex)：一个网络从预测到更新的手算。
- [泛化与训练技巧](chapters/18-generalization.tex)：为什么训练题做对了不代表新题会做？

## Ⅲ · 不同数据为什么需要不同结构

- [CNN](chapters/19-cnn.tex)：局部卷积与权重共享如何利用图像的空间结构？
- [RNN](chapters/21-rnn.tex)：隐藏状态如何在序列中传递？
- [Attention 的问题来源](chapters/21b-why-attention.tex)：如果要直接读取上下文中的信息？

## Ⅳ · 从 Key-Value 到完整 Transformer

- [一条关联怎样写入矩阵](chapters/04-key-value-outer-product.tex)
- [为什么记忆会相互干扰](chapters/05-memory-interference.tex)
- [线性记忆怎样改善](chapters/06-better-linear-memory.tex)
- [Key/Value 怎样堆成矩阵](chapters/08-stacking-key-value.tex)
- [从 MLP 视角看记忆检索](chapters/09-nonlinearity-and-memory.tex)
- [Softmax 与 Attention](chapters/11-softmax-memory.tex)：从单个列 Query 到批量行 Query
- [Self-Attention 的矩阵](chapters/12-self-attention-matrices.tex)：Q、K、V 的来源、两种行列摆放的图卡与形状
- [线性记忆、MLP 与 Attention 对照](chapters/14-summary.tex)
- [Key-Value 基础练习](chapters/15-practice.tex)
- [Transformer 架构](chapters/22-transformer-architecture.tex)：多头、残差、位置与 Mask
- [两个 Token 的贯通计算](chapters/22b-token-to-output.tex)：从矩阵到注意力和下一词
- [因果训练与标签对齐](chapters/22c-language-training.tex)：掩码、Shifted Targets、交叉熵
- [现代 Transformer 架构](chapters/22d-modern-transformers.tex)：RoPE、RMSNorm、SwiGLU、MoE、GQA 与长上下文

## Ⅴ · 模型生成与现实应用

- [LLM 如何训练和生成](chapters/23-llm-systems.tex)：Loss、采样、RAG、Agent
- [后训练与推理能力](chapters/23c-post-training.tex)：SFT、RLHF、RLVR 和 CoT
- [Agent 系统设计](chapters/23d-agent-systems.tex)：工具、工作流、MCP、Skill 与权限边界
- [部署和多模态](chapters/23b-deployment-and-ecosystem.tex)：量化、硬件、推理引擎

## Ⅵ · 选读、索引与综合练习

- [高维记忆容量（选读）](chapters/13-capacity.tex)：随机性和容量结论需要什么假设？
- [100 个 AI 术语](chapters/24-lexicon.tex)：每个术语都能点击跳回对应章节，章节编号自动更新
- [现代术语补充导航](chapters/24b-modern-lexicon.tex)：可点击返回对应的现代架构与 Agent 章节
- [综合练习及答案](chapters/25-integrated-practice.tex)
- [现代训练与 Agent 练习](chapters/25b-modern-practice.tex)：含缓存和模型训练数值题、工具安全情景题
- [参考与延伸阅读](chapters/26-sources.tex)：[第一套视频](https://www.bilibili.com/video/BV1NCgVzoEG9/)、[第二套视频](https://www.bilibili.com/video/BV15z4C6SEHT/)与研究资料

## 单个 PDF 的构建方式

```bash
cd book
latexmk -xelatex -interaction=nonstopmode -halt-on-error -outdir=build main.tex
```

也可直接在 [Actions 构建记录](https://github.com/CoCoThink/ai-by-intuition/actions/workflows/build-latex.yml) 下载完整 PDF。源码文件名沿用稳定的主题标识；最终章节顺序以 `main.tex` 中的 `\input` 为准。
