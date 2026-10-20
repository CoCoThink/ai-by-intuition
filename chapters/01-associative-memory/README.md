# 01 · 为什么矩阵乘法可以检索记忆？

> **从二维向量与点积开始，把 Key / Value 堆成矩阵，逐步理解 ReLU、MLP 与 Attention。**

这不是一篇直接抛出 Transformer 公式的文章，而是尝试回答：

**为什么** `Kx` 能一次计算很多匹配分数？为什么把 ReLU 放在中间，右边还能接着乘 `Vᵀ`？为什么这就像在检索一组记忆？

## 阅读前需要什么？

只要能进行加减乘除，理解“一个数字乘另一个数字”即可。不要求事先掌握线性代数、求导或神经网络。

## 本章路线

1. 向量与长度：数字怎样表示一个对象？
2. 点积：方向相近为什么能表现为相似度？
3. 外积：为什么一组 Key–Value 能写入权重矩阵？
4. 线性召回：其他记忆为什么造成干扰？
5. **矩阵拆解重点：Kx → 逐元素 ReLU → Vᵀa。**
6. MLP：筛选机制为什么带来非线性？
7. Softmax Attention：怎样进一步集中检索权重？
8. 高维随机记忆的容量直觉、误区与练习。

## 阅读与编译

- [**LaTeX 完整正文**](main.tex)
- **PDF**：到仓库顶部的 *Actions → Build LaTeX PDF*，在成功运行的工作流底部下载 `ai-by-intuition-chapter-01-pdf`。
- 本地编译：

```bash
latexmk -xelatex -interaction=nonstopmode -halt-on-error main.tex
```

## 一个贯穿全篇的公式

```text
Query x
   │
   ▼
Kx               每一行 Key 与 Query 做点积 → 匹配分数
   │
   ▼
ReLU(Kx)         逐个筛选匹配分数
   │
   ▼
Vᵀ ReLU(Kx)      将每列 Value 按分数加权求和
   │
   ▼
输出
```

## 来源说明

本章的“把线性层、MLP 和注意力统一看成记忆系统”的思想受到 Alex Wang 的 [*You could have invented transformers from memory*](https://alexwang.ai/posts/associative-memory/) 启发。本文为帮助入门读者独立重新组织的中文讲义，特别加强了矩阵堆叠、维度检查、逐项手算与公式之间的桥梁。