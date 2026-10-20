# AI by Intuition · 用直觉理解人工智能

> **先提出问题，再计算例子，最后理解公式。**

一套适合希望从具体问题出发、逐步建立数学直觉的中文 AI 原理教材。你不需要先读完高等数学教材，也不需要记住一堆模型名称；我们会从几个数字、一小张矩阵、一条可训练的函数开始，逐步理解神经网络如何学习、怎样处理图像与文字，以及 Transformer 为什么使用 Attention。

**最终阅读制品只有一份完整 PDF。** LaTeX 分章节管理，主文件是 [`book/main.tex`](book/main.tex)。

## 开始阅读

**[完整章节目录](book/README.md)** · **[全书学习路线图](ROADMAP.md)** · **[GitHub Actions：获取最新版 PDF](https://github.com/CoCoThink/ai-by-intuition/actions/workflows/build-latex.yml)**

在最近一次成功构建的页面下方，下载 `ai-by-intuition-volume-01` 构建产物，其中是一本完整 PDF。

## 六个递进的问题

| 阅读阶段 | 核心问题 | 你会真正算什么？ |
|---|---|---|
| Ⅰ · 表示 | 怎样把一个问题变成可计算的数字？ | 函数、向量、点积、矩阵、Embedding |
| Ⅱ · 学习 | 神经网络凭什么能从错误中改进？ | MLP、ReLU、Loss、梯度、反向传播、泛化 |
| Ⅲ · 结构 | 图片和一串词有什么不同？ | 卷积扫描、序列隐藏状态、信息传递 |
| Ⅳ · Attention | 为什么模型要直接读取上下文中的相关信息？ | Key-Value、Softmax、QKᵀ、因果训练、现代 Transformer |
| Ⅴ · 应用 | 预测下一个 Token 怎么变成可用的 AI 系统？ | 解码、后训练、RAG、Agent、部署与权限 |
| Ⅵ · 巩固 | 哪些直觉有边界，怎样检查是否真正学会？ | 高维容量选读、术语表、综合练习 |

这不是照视频分集顺序展开的逐字讲义，而是按**问题之间的依赖关系**重新组织：先学会计算，再学参数如何训练；理解序列信息的困难后，再引出 Attention 的两条推导路径（直接读取上下文与联想记忆）。

## 写作约定

每个关键概念尽量按“**问题 → 可手算的数字 → 一般公式 → 维度检查 → 现实模型 → 适用条件**”讲解。第一次出现的新符号必须解释；公式的转置与矩阵尺寸不能以“显然”为由跳过。

练习与参考答案放在相应知识段落后，全书还有统一的术语表和综合复习题。书中例子使用人工构造的数据，旨在解释运算，不代表任何真实大模型的权重或性能。

## 本地编译

在安装 XeLaTeX、中文字体、TikZ 等依赖之后：

```bash
cd book
latexmk -xelatex -interaction=nonstopmode -halt-on-error -outdir=build main.tex
```

生成 `book/build/main.pdf`。Ubuntu 可以安装 `latexmk texlive-xetex texlive-lang-chinese texlive-latex-extra texlive-pictures texlive-fonts-recommended fonts-noto-cjk fonts-noto-core lmodern`。

## 延伸阅读与来源

- **[飞天闪客：从函数到 Transformer](https://www.bilibili.com/video/BV1NCgVzoEG9/)** — 数学与基本架构的参考。
- **[飞天闪客：从 Transformer 到大模型](https://www.bilibili.com/video/BV15z4C6SEHT/)** — 现代架构与应用设计的参考。
- [Alex Wang：You could have invented transformers from memory](https://alexwang.ai/posts/associative-memory/) — 联想记忆数学视角。
- [Attention Is All You Need](https://arxiv.org/abs/1706.03762) — Transformer 原始论文。

详细书目在 [参考与延伸阅读](book/chapters/26-sources.tex)。欢迎通过 Issue 反馈符号定义、数值计算和讲解跳步，参见 [CONTRIBUTING.md](CONTRIBUTING.md)。

**许可：** 当前尚未设置正式 LICENSE，请勿默认将内容视为可任意再授权的开源教材。
