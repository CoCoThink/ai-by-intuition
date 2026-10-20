# AI by Intuition · 从函数到大语言模型

> **先有问题，再有直觉；先算一个例子，再写一般公式。**

一份面向数学基础较弱、非科班读者的中文 AI 原理教材。从“函数为什么能够拟合数据”出发，逐步学习矩阵、MLP、梯度下降、反向传播、CNN、Embedding、RNN、Attention、Transformer 和大语言模型。

**唯一正式交付物是一本完整 PDF**；章节 LaTeX 源码拆开管理，只是为了便于校对和维护。

## 阅读与下载

- **[查看全书主文件（LaTeX）](book/main.tex)**
- **[章节索引与学习目标](book/README.md)**
- **[全书知识路线图](ROADMAP.md)**
- **[GitHub Actions：下载最新完整 PDF](https://github.com/CoCoThink/ai-by-intuition/actions/workflows/build-latex.yml)**

打开最近一次成功的构建，在 Artifacts 中下载 `ai-by-intuition-volume-01`，其中只有 `AI-by-Intuition-Volume-01.pdf`。

## 六个部分

| 部分 | 主要内容 | 关键问题 |
|---|---|---|
| I · 从函数到矩阵 | 函数、参数、向量、点积、矩阵乘法 | 不会公式也能先看懂计算在做什么吗？ |
| II · 记忆与 MLP | 外积、关联记忆、激活函数、MLP | 为什么 K 与 V 堆成矩阵以后，还能插入 ReLU？ |
| III · 模型训练 | 损失、导数、梯度下降、反向传播、泛化 | 网络怎么知道参数该改多少？ |
| IV · 图像与序列 | CNN、One-hot、Embedding、RNN | 为什么图片需要局部特征，文字需要顺序？ |
| V · Transformer | Softmax、Q/K/V、Self-Attention、多头与掩码 | 从单个 Query 怎样得到标准 Attention？ |
| VI · LLM 与应用 | 预训练、生成策略、RAG、Agent、100 个术语、综合练习 | 一个能预测 Token 的模型怎样变成应用？ |

## 教学原则

每个新概念尽量按“**问题 → 手算数字 → 一般公式 → 维度检查 → 真实模型 → 局限与练习**”展开。特别强调矩阵的行列与转置：不把一个抽象符号视作“显然”。

一些技巧属于普遍经验而非严格定理。书中会区别数学恒等式、统计直觉、模型设计选择和工程系统能力，避免过度类比。

## 本地编译

需要 XeLaTeX 和中文字体。Ubuntu 可使用：

```bash
sudo apt-get install latexmk texlive-xetex texlive-lang-chinese \
  texlive-latex-extra texlive-pictures texlive-fonts-recommended \
  fonts-noto-cjk fonts-noto-core lmodern
cd book
latexmk -xelatex -interaction=nonstopmode -halt-on-error -outdir=build main.tex
```

最终文件为 `book/build/main.pdf`。不需要安装 LaTeX 也可以直接从 Actions 下载 PDF。

## 教学资料与引用

内容组织参考了提供的七份《从函数到神经网络》《计算神经网络的参数》《调教神经网络的方法》《从矩阵到 CNN》《从词嵌入到 RNN》《简单而强大的 Transformer》《速览大模型 100 词》的中文字幕资料。教材使用独立重写的数学推导、图解与练习，**并未逐字转载字幕**。联想记忆部分的数学组织还参考了 Alex Wang 的文章 [You could have invented transformers from memory](https://alexwang.ai/posts/associative-memory/)；详细资料见 [参考章节](book/chapters/26-sources.tex)。

欢迎通过 Issue 指出符号未解释、推导跳步和计算错误；贡献说明见 [CONTRIBUTING.md](CONTRIBUTING.md)。仓库目前尚未选定正式 LICENSE，请勿默认任意转载或再授权。
