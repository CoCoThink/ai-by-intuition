# AI by Intuition · 用直觉理解 AI

> **先有问题，再有直觉；先算一个例子，再写一般公式。**

面向数学基础较弱、非科班，以及想真正弄清 AI 底层数学的人。这里不要求先会线性代数：每个公式都从能手算的数值例子开始，逐步引入符号、矩阵维度和实际的模型结构。

## 读者从哪里开始？

### 第一卷｜从矩阵乘法到 MLP 与 Attention

**[进入全书 LaTeX 源码](book/main.tex)** · **[查看章节目录](book/README.md)**

这是一本连续编排的教程，重点回答：

- 点积的几何公式怎样由投影和余弦定理推出来？
- 矩阵乘法为什么既能看成「逐行点积」，又能看成「按列加权求和」？
- 为什么 K 按行排列、V 需要转置？为什么 $Kx$ 恰好返回每个 Key 的分数？
- 为什么可以对分数逐个应用 ReLU，再乘 $V^\top$？
- Q 是不是原来的 x？从单次查询 $V^\top\mathrm{softmax}(\beta Kx)$ 如何变成标准 Attention 的 $\mathrm{softmax}(QK^\top/\sqrt{d_k})V$？

**阅读时只需下载一份完整 PDF。** 仓库使用多个 `.tex` 文件维护章节，并由 `book/main.tex` 统一编译。

### 下载 PDF

打开 **[GitHub Actions → Build one PDF book](https://github.com/CoCoThink/ai-by-intuition/actions/workflows/build-latex.yml)**，进入最近一次成功的构建，在 **Artifacts** 下载 `ai-by-intuition-volume-01`。ZIP 中只有 `AI-by-Intuition-Volume-01.pdf`。

### 本地构建

需要 XeLaTeX、中文字体、TikZ 和 PGFPlots。Ubuntu 建议安装：

```bash
sudo apt-get install latexmk texlive-xetex texlive-lang-chinese \
  texlive-latex-extra texlive-pictures texlive-fonts-recommended \
  fonts-noto-cjk fonts-noto-core lmodern
cd book
latexmk -xelatex -interaction=nonstopmode -halt-on-error -outdir=build main.tex
```

产物是 `book/build/main.pdf`。如果只想阅读，不需要安装 LaTeX，直接下载 GitHub Actions 产物即可。

## 整套教程的学习方法

1. **先提出一个真实的困惑**，例如「为什么矩阵乘法就能查询记忆？」
2. **先手算二维案例**，确认没有任何神秘步骤。
3. **把算式写成一般矩阵形式**，在每个运算旁标明形状。
4. **最后才引入模型术语**，例如 MLP、ReLU、Softmax、Self-Attention。
5. **明确适用条件**，区分数学恒等式、理想模型和实际 LLM。

## 后续内容

见 [ROADMAP.md](ROADMAP.md)。优先补齐反向传播、概率、训练目标与 Transformer 其他模块，继续维护为单个整合版 PDF，而不是多份零散讲义。

欢迎在 Issues 指出难懂的数学跳步。内容参与规范见 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 参考

第一卷的「联想记忆」组织视角受到 Alex Wang 的 [*You could have invented transformers from memory*](https://alexwang.ai/posts/associative-memory/) 启发；本书针对初学者重新设计了章节顺序、手算例子和常见疑问的解释。

**许可说明：** 目前尚未选定正式开源许可证，先保留版权；确定许可后再添加 LICENSE。
