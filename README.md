# AI by Intuition · 用直觉理解 AI

> **先有问题，再有直觉；先算一个例子，再写一般公式。**

面向数学基础薄弱、非科班和希望重新建立底层直觉的读者。这里不是公式速查表，也不是只讲类比的科普：每一篇都会从一个实际问题出发，用可手算的小例子，逐步走到 AI 里真正使用的数学表达式。

**阅读顺序：问题 → 生活直觉 → 最小数学工具 → 手算例子 → 矩阵形式 → 模型中的作用 → 局限与练习。**

## 从这里开始

**第 01 篇：[为什么矩阵乘法可以检索记忆？——从点积、K/V 到 MLP 和 Attention](chapters/01-associative-memory/README.md)**

- [LaTeX 源码（XeLaTeX）](chapters/01-associative-memory/main.tex)
- PDF：在 GitHub Actions 的 `Build LaTeX PDF` 工作流中下载生成的构建产物；也可在本地编译。
- 背景问题：为何把很多 Key 堆成矩阵，乘完还能过 ReLU，再乘一个 Value 矩阵？

## 学习路线

完整的章节计划见 [ROADMAP.md](ROADMAP.md)。内容按**概念依赖**而不是 AI 热词排序：

1. **数学直觉**：向量、点积、矩阵乘法、导数、概率。
2. **神经网络**：线性层、激活函数、MLP、梯度下降、反向传播。
3. **Transformer**：Embedding、Self-Attention、位置编码、KV Cache。
4. **训练与推理**：Token、Loss、预训练、微调、采样、RAG。
5. **进一步探索**：MoE、扩散模型、强化学习、模型评估。

## 如何阅读

读到一个公式时，先回答三个问题：

- **输入是什么？** 每个向量或矩阵代表什么？
- **形状是什么？** 是单个数字、一个向量，还是一张数字表？
- **这一步在做什么？** 匹配、过滤、混合，还是更新？

不必第一次就记住所有符号。先自己算通二维的小例子，再看一般形式。

## 编译 LaTeX

需要 **XeLaTeX**，以及中文与 TikZ/PGFPlots 等 LaTeX 宏包。Ubuntu 可安装 `texlive-xetex`、`texlive-lang-chinese`、`texlive-latex-extra`、`texlive-pictures` 与 Noto CJK 字体。

```bash
cd chapters/01-associative-memory
latexmk -xelatex -interaction=nonstopmode -halt-on-error main.tex
```

生成 `main.pdf`。构建中间文件已被 `.gitignore` 排除，不需要加入版本控制。

## 参与改进

欢迎报告数学错误、难理解的跳步、印刷错误，或提交更好的手算例子。详见 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 内容来源与引用

本仓库第 01 篇的联想记忆主线受到 Alex Wang 的文章 [*You could have invented transformers from memory*](https://alexwang.ai/posts/associative-memory/) 启发；教程的中文讲解、数值算例、矩阵维度说明和练习是面向初学者重新组织的独立教学内容。相关结论的适用条件会在正文中说明。

> 许可：尚未选择正式开源许可证。在确定许可证前，版权默认保留；欢迎通过 Issue 讨论适合教育内容的授权方式。
