# 全书阅读顺序 · AI by Intuition

**唯一入口：** [book/main.tex](main.tex)。读者只需要阅读一个 PDF；
源码按章节维护，正文编号由 LaTeX 自动生成，目录与书内引用应以编译 PDF 为准。

## 前五部分：必读主线

### I · 把文字变成可计算的数字
- [阅读指南](chapters/00-guide.tex)：先明确要解决什么问题
- [数学速查](chapters/00b-math-tools.tex)和[全书符号表](chapters/00c-symbols.tex)：高中三角函数、导数、指数对数与矩阵
- [函数](chapters/00-functions.tex)、[向量](chapters/01-vectors.tex)、[点积](chapters/02-dot-product.tex)、[矩阵乘法](chapters/03-matrix-multiplication.tex)
- [Token、One-hot 与 Embedding](chapters/20-embeddings.tex)
- [输入、目标与形状契约](chapters/20b-task-contract.tex)

### II · 让神经网络学会预测
- [ReLU 与非线性](chapters/07-functions-relu.tex)
- [MLP](chapters/10-mlp.tex)
- [损失与梯度下降](chapters/16-loss-gradient.tex)
- [反向传播](chapters/17-backpropagation.tex)
- [完整的两层学习例子](chapters/18b-end-to-end-learning.tex)
- [泛化、过拟合与正则化](chapters/18-generalization.tex)、[小批次与训练工程](chapters/18c-training-engineering.tex)

### III · 让词与词交换信息
- [RNN](chapters/21-rnn.tex) 与 [Attention 的需求来源](chapters/21b-why-attention.tex)
- [从单 Query 到批量 Self-Attention](chapters/11-softmax-memory.tex)，并比较 Linear / MLP / Attention

### IV · 组装、训练并使用 Transformer
- [位置、缩放与双头注意力的数字例子](chapters/22a-position-multihead.tex)
- [Pre-Norm Block、残差图与 LayerNorm](chapters/22-transformer-architecture.tex)
- [FFN 与词表输出头](chapters/10b-ffn-output-head.tex)
- [两个 Token 完整前向计算](chapters/22b-token-to-output.tex)
- [因果训练、输出头与前层参数的梯度更新](chapters/22c-language-training.tex)
- [推理、缓存与生成](chapters/23-llm-systems.tex)

### V · 改进模型并构建可靠应用
- [现代 Transformer 架构](chapters/22d-modern-transformers.tex)
- [后训练与推理策略](chapters/23c-post-training.tex)
- [Agent 系统设计](chapters/23d-agent-systems.tex)
- [量化、蒸馏、LoRA 与部署](chapters/23b-deployment-and-ecosystem.tex)

## 第六、七部分：独立选读专题（不影响必读主线）

- [CNN](chapters/19-cnn.tex)
- [联想记忆与外积](chapters/04-key-value-outer-product.tex)、[记忆干扰](chapters/05-memory-interference.tex)、[改善](chapters/06-better-linear-memory.tex)
- [Key/Value 行列堆叠](chapters/08-stacking-key-value.tex) 与 [非线性记忆](chapters/09-nonlinearity-and-memory.tex)
- [Linear / MLP / Attention 关系](chapters/14-summary.tex)
- [高维容量假设](chapters/13-capacity.tex)

## 附录：练习、查阅与集中解答（建议完成）

- [数学与神经网络练习](chapters/25-integrated-practice.tex)
- [现代模型与 Agent 练习](chapters/25b-modern-practice.tex)
- [联想记忆练习](chapters/15-practice.tex)
- [100 词术语地图](chapters/24-lexicon.tex)
- [现代架构术语导航](chapters/24b-modern-lexicon.tex)
- [知识关系图](chapters/24c-concept-map.tex)与[英中文术语 A–Z 索引](chapters/24d-english-index.tex)
- [集中参考答案](chapters/27-answer-key.tex)及[分章随堂自测解答](chapters/28-chapter-checks.tex)：所有题目先做后查
- [参考与延伸阅读](chapters/26-sources.tex)

## 一次构建，一本 PDF

```bash
cd book
latexmk -lualatex -interaction=nonstopmode -halt-on-error -outdir=build main.tex
```

最新版本也可以在 [GitHub Actions](https://github.com/CoCoThink/ai-by-intuition/actions/workflows/build-latex.yml) 下载。
构建会检查目录、课程序列、交叉引用、公式数值和独立答案。

## 无障碍与视觉验收

正式构建已转为 LuaLaTeX 并启用 `DocumentMetadata` 的结构标签试验模式。CI 严格要求 `pdfinfo` 显示 `Tagged: yes`，并检查页面文字边界；TikZ 图有中文替代描述。**Tagged: yes 不等于通过 PDF/UA 验证**，数学公式的语义朗读、嵌套表格和读屏顺序仍需专项审核。
