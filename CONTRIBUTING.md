# 参与改进 AI by Intuition

目标是让没有系统学习过高等数学的读者也能真正理解 AI 中的矩阵计算和推导，而不是只记住术语。

## 内容原则

- 先展示一个可手算的二维例子，再给一般数学形式。
- 首次出现矩阵乘法时，写出逐行与逐列的计算过程。
- 明确输入、输出、矩阵尺寸与每一维的含义。
- 区分等式、近似、启发式解释与实际模型。
- 不使用「神经元必然对应单条事实」一类过度简化表述。
- 引用原作者和研究结论，并尽量提供原始参考链接。

## 目录与编译

新增教程文件写入 `book/chapters/NN-name.tex`，并将 `\input{chapters/NN-name}` 加入 `book/main.tex` 的正确阅读顺序。

全书唯一 PDF 由 `book/main.tex` 编译：

```bash
cd book
latexmk -xelatex -interaction=nonstopmode -halt-on-error -outdir=build main.tex
```

请勿逐章提交 PDF，也勿提交 LaTeX 中间文件。CI 为整个仓库产生**一个** PDF 构建产物。

## Issue / PR

优先报告：哪一段无法理解、跳过了哪个步骤、某次形状检查是否有问题。提交 PR 时请写明你改进了哪一种初学者困惑，附上手算核验步骤，并确认 XeLaTeX 能通过。

尚未设置开源许可证；版权仍默认保留。后续明确授权后将更新本说明。
