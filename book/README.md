# 第一卷｜从矩阵乘法到 MLP 与 Attention

- **入口：** [main.tex](main.tex)，编译后是一份完整、连续分页、含目录的中文 PDF。
- **范围：** 向量、点积、矩阵乘法、Key-Value、ReLU、MLP、Softmax、Attention、干扰和容量。
- **对象：** 数学基础较弱或非科班读者；无需微积分预备知识。

## 源码章节（依次阅读）

| 文件 | 重点 |
|---|---|
| [00-guide](chapters/00-guide.tex) | 五个真实问题与阅读方法 |
| [01-vectors](chapters/01-vectors.tex) | 数字列表、向量和长度 |
| [02-dot-product](chapters/02-dot-product.tex) | 点积、投影与余弦定理推导 |
| [03-matrix-multiplication](chapters/03-matrix-multiplication.tex) | **行乘列、列的加权和、尺寸检查** |
| [04-key-value-outer-product](chapters/04-key-value-outer-product.tex) | Key、Value、外积与关联记忆 |
| [05-memory-interference](chapters/05-memory-interference.tex) | 多条记忆造成的干扰 |
| [06-better-linear-memory](chapters/06-better-linear-memory.tex) | 线性记忆的优化思路 |
| [07-functions-relu](chapters/07-functions-relu.tex) | **为什么 ReLU 能放在两个乘法之间** |
| [08-stacking-key-value](chapters/08-stacking-key-value.tex) | **K 与 V 的行列选择，以及从 $Kx$ 到读出 Value 的手算** |
| [09-nonlinearity-and-memory](chapters/09-nonlinearity-and-memory.tex) | 非线性如何降低干扰 |
| [10-mlp](chapters/10-mlp.tex) | MLP、偏置、隐藏层和参数 |
| [11-softmax-memory](chapters/11-softmax-memory.tex) | Softmax 与单列 Query 到多行 Query 的推导 |
| [12-self-attention-matrices](chapters/12-self-attention-matrices.tex) | Q 与输入 x 的关系、QKV 投影、标准 Attention |
| [13-capacity](chapters/13-capacity.tex) | 高维、随机噪声与容量 |
| [14-summary](chapters/14-summary.tex) | Linear / MLP / Attention 的共同点 |
| [15-practice](chapters/15-practice.tex) | 练习、答案与最终回顾 |

所有文件按阅读顺序编号；以主文件 `main.tex` 中的 `\input` 列表为准。

## 一键构建

到仓库 [Actions 页面](https://github.com/CoCoThink/ai-by-intuition/actions/workflows/build-latex.yml) 下载构建产物 `ai-by-intuition-volume-01`，里面只有一本 PDF；或本地运行：

```bash
cd book
latexmk -xelatex -interaction=nonstopmode -halt-on-error -outdir=build main.tex
```

本轮针对读者实际阅读后的四个问题增加了几何证明、Q 与 x 的区分、K/V 排布解释及 Attention 公式推导。章节源码仍单独维护，最终始终只编译一本 PDF。
