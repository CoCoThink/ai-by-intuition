# 全书目录 · AI by Intuition

**唯一入口：** [`main.tex`](main.tex)；按知识依赖而非视频分集顺序排列。读者使用一本完整 PDF，作者按独立 `.tex` 源文件维护各主题。

## Ⅰ · 把问题变成数字

1. [阅读指南](chapters/00-guide.tex)：一本书回答哪五个问题？
2. [从函数认识模型](chapters/00-functions.tex)：参数是什么、怎样拟合数据？
3. [向量](chapters/01-vectors.tex)：一串数字能表示什么？
4. [点积与几何意义](chapters/02-dot-product.tex)：余弦定理为什么出现在向量里？
5. [矩阵乘法](chapters/03-matrix-multiplication.tex)：行乘列与列加权为什么是同一回事？
6. [Embedding](chapters/20-embeddings.tex)：Token ID 如何变成向量？

## Ⅱ · 神经网络怎样学会预测

7. [激活函数与 ReLU](chapters/07-functions-relu.tex)：为什么矩阵之间还要放函数？
8. [MLP](chapters/10-mlp.tex)：两个矩阵和激活函数组成什么计算？
9. [损失与梯度下降](chapters/16-loss-gradient.tex)：模型怎么知道参数朝哪里改？
10. [反向传播](chapters/17-backpropagation.tex)：链式法则怎样传递梯度？
11. [一次完整的学习过程](chapters/18b-end-to-end-learning.tex)：一个网络从预测到更新的手算。
12. [泛化与训练技巧](chapters/18-generalization.tex)：为什么训练题做对了不代表新题会做？

## Ⅲ · 不同数据为什么需要不同结构

13. [CNN](chapters/19-cnn.tex)：局部卷积与权重共享如何利用图像的空间结构？
14. [RNN](chapters/21-rnn.tex)：隐藏状态如何在序列中传递？
15. [Attention 的问题来源](chapters/21b-why-attention.tex)：如果要直接读取上下文中的信息？

## Ⅳ · 从 Key-Value 到完整 Transformer

16. [一条关联怎样写入矩阵](chapters/04-key-value-outer-product.tex)
17. [为什么记忆会相互干扰](chapters/05-memory-interference.tex)
18. [线性记忆怎样改善](chapters/06-better-linear-memory.tex)
19. [Key/Value 怎样堆成矩阵](chapters/08-stacking-key-value.tex)
20. [从 MLP 视角看记忆检索](chapters/09-nonlinearity-and-memory.tex)
21. [Softmax 与 Attention](chapters/11-softmax-memory.tex)：从单个列 Query 到批量行 Query
22. [Self-Attention 的矩阵](chapters/12-self-attention-matrices.tex)：Q、K、V 的来源与形状
23. [线性记忆、MLP 与 Attention 对照](chapters/14-summary.tex)
24. [Key-Value 基础练习](chapters/15-practice.tex)
25. [Transformer 架构](chapters/22-transformer-architecture.tex)：多头、残差、位置与 Mask
26. [两个 Token 的贯通计算](chapters/22b-token-to-output.tex)：从矩阵到注意力和下一词

## Ⅴ · 模型生成与现实应用

27. [LLM 如何训练和生成](chapters/23-llm-systems.tex)：Loss、采样、RAG、Agent
28. [部署和多模态](chapters/23b-deployment-and-ecosystem.tex)：量化、硬件、推理引擎

## Ⅵ · 选读、索引与综合练习

29. [高维记忆容量（选读）](chapters/13-capacity.tex)：随机性和容量结论需要什么假设？
30. [100 个 AI 术语](chapters/24-lexicon.tex)：每个术语都能点击跳回对应章节，章节编号自动更新
31. [综合练习及答案](chapters/25-integrated-practice.tex)
32. [参考与延伸阅读](chapters/26-sources.tex)：[原始视频](https://www.bilibili.com/video/BV1NCgVzoEG9/)与研究资料

## 单个 PDF 的构建方式

```bash
cd book
latexmk -xelatex -interaction=nonstopmode -halt-on-error -outdir=build main.tex
```

也可直接在 [Actions 构建记录](https://github.com/CoCoThink/ai-by-intuition/actions/workflows/build-latex.yml) 下载完整 PDF。源码文件名沿用稳定的主题标识；最终章节顺序以 `main.tex` 中的 `\input` 为准。
