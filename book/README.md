# 全书目录 · AI by Intuition

**唯一编译入口：** [main.tex](main.tex)。LaTeX 的 `\input` 顺序决定读者看到的章节顺序；文件名中的数字只是源码标识。

**交付格式：** 一本连续页码、带目录的中文 PDF。教材包含六部分、可手算的矩阵和训练例子、图示、100 个术语与两组练习。

## I. 从函数到矩阵

- [函数与模型](chapters/00-functions.tex)：选择函数、猜测参数与拟合数据
- [向量](chapters/01-vectors.tex)：一列数字意味着什么
- [点积](chapters/02-dot-product.tex)：投影、余弦定理和方向相似度
- [矩阵乘法](chapters/03-matrix-multiplication.tex)：逐行点积、按列加权和与维度检查

## II. 从联想记忆到 MLP

- [外积与关联记忆](chapters/04-key-value-outer-product.tex)：如何写入一条 Key--Value
- [记忆干扰](chapters/05-memory-interference.tex)：其他 Key 如何影响召回
- [更好的线性记忆](chapters/06-better-linear-memory.tex)：为什么可以优化权重
- [函数与 ReLU](chapters/07-functions-relu.tex)：逐元素操作与非线性
- [堆叠 K/V](chapters/08-stacking-key-value.tex)：**M、dk、dv、转置与完整数字例子**
- [非线性与记忆](chapters/09-nonlinearity-and-memory.tex)：激活函数怎样改变干扰
- [MLP](chapters/10-mlp.tex)：隐藏层、偏置与参数

## III. 神经网络如何学习

- [损失与梯度下降](chapters/16-loss-gradient.tex)：MSE、导数、梯度与学习率
- [反向传播](chapters/17-backpropagation.tex)：通过链式法则亲手算梯度
- [泛化与训练技巧](chapters/18-generalization.tex)：过拟合、数据增强、正则化和 Dropout

## IV. 图片与序列

- [CNN](chapters/19-cnn.tex)：局部卷积、共享权重和池化
- [Embedding](chapters/20-embeddings.tex)：One-hot、嵌入矩阵与 Token
- [RNN](chapters/21-rnn.tex)：隐藏状态、时间步与长期依赖

## V. Attention 与 Transformer

- [Softmax Attention](chapters/11-softmax-memory.tex)：单列 Query 到多行 Query 的推导
- [Self-Attention](chapters/12-self-attention-matrices.tex)：QKV 投影、矩阵形状与输出
- [记忆容量](chapters/13-capacity.tex)：高维统计规律与限制
- [记忆方法总结](chapters/14-summary.tex) 和 [基础练习](chapters/15-practice.tex)
- [完整 Transformer](chapters/22-transformer-architecture.tex)：多头、位置编码、残差、FFN、Mask 和生成

## VI. 大模型与应用

- [模型训练、解码与工具](chapters/23-llm-systems.tex)：交叉熵、温度、Top-k/Top-p、RAG 与 Agent
- [模型部署与效率](chapters/23b-deployment-and-ecosystem.tex)：量化、蒸馏、剪枝、LoRA、GPU/TPU/NPU 与多模态
- [AI 的 100 个基础术语](chapters/24-lexicon.tex)：十类按知识依赖组织的术语
- [综合练习与答案](chapters/25-integrated-practice.tex)
- [参考与阅读说明](chapters/26-sources.tex)

## 如何编译

```bash
cd book
latexmk -xelatex -interaction=nonstopmode -halt-on-error -outdir=build main.tex
```

GitHub Actions 也自动编译全部章节，只上传一个 PDF 文件。若只需要阅读，请下载 [构建结果](https://github.com/CoCoThink/ai-by-intuition/actions/workflows/build-latex.yml)。
