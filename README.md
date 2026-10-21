# AI by Intuition · 从函数到 Transformer 的直觉之旅

> **先有问题，再有直觉，然后才有公式。**

一本从**“计算机怎样学会生成有用的语言回答？”**出发的中文 AI 原理教程。我们先解释为什么可以用原始文本构造“预测下一个 Token”的训练题——**它是学习语言规律的一种具体方法，不是 AI 的终极目标**——再从函数、向量、矩阵和 MLP 出发，走到反向传播、RNN、Attention、Transformer 的训练与生成。最后解释模型为什么还需要后训练、检索、工具以及部署系统。

**读者阅读一个完整 PDF，作者维护分开的 LaTeX 章节源码。**

[**全书顺序与可点击目录**](book/README.md) · [学习路线设计](ROADMAP.md) · [GitHub Actions 下载最新版 PDF](https://github.com/CoCoThink/ai-by-intuition/actions/workflows/build-latex.yml)

## 为什么这样组织？

| 学习阶段 | 自然产生的问题 |
|---|---|
| Ⅰ 表示 | 文字怎样成为可以计算的数字？ |
| Ⅱ 学习 | 预测错了，网络怎样修改权重？ |
| Ⅲ 上下文 | 词与词怎样交换信息，为什么要 Attention？ |
| Ⅳ Transformer | 各个部件怎样连成完整的训练与生成过程？ |
| Ⅴ 拓展到系统 | 为什么需要 KV Cache 优化、后训练和 Agent？ |
| Ⅵ 选读 | CNN、联想记忆和记忆容量可以提供什么其他直觉？ |

**前五部分连续阅读，第六部分仅供选读；练习、术语与集中答案统一放在附录。** 以前放在 Attention 之前的外积、记忆干扰与最小二乘，现在完整保留为选读；让读者无需中途换数学视角就能从 RNN 直达 Self-Attention。

书中提供数学速查、位置编码/双头 Attention 的数字例子、Pre-Norm 残差示意，以及从 $p-\mathrm{onehot}$ 到输出头 SGD 的一次训练计算。2026 年 10 月的复核还增加了 **Embedding 查表、损失下降、梯度计算图、欠拟合／过拟合、验证损失、CNN 窗口扫描与因果 Mask 热力图**，并修复了向量长度和练习答案等遗留错误。

书中反复使用教学用序列“春天 / 花 / 开了 / 。”（假设 Token ID 为 `[1,3,4,2]`），再用小矩阵展示隐藏表示、预测目标、行列转置与损失计算。例子不是任何现成模型的真实参数。

## 本地编译

安装 XeLaTeX、中文字体、PGF/TikZ 等依赖后运行：

```bash
cd book
latexmk -xelatex -interaction=nonstopmode -halt-on-error -outdir=build main.tex
```

生成 `book/build/main.pdf`。CI 还会检查 PDF 目录、术语链接、教学图卡和章节结构。

## 原视频与研究参考

- [飞天闪客：《一小时从函数到 Transformer》](https://www.bilibili.com/video/BV1NCgVzoEG9/)
- [飞天闪客：《一小时从 Transformer 到大模型》](https://www.bilibili.com/video/BV15z4C6SEHT/)
- [Alex Wang：You could have invented transformers from memory](https://alexwang.ai/posts/associative-memory/)
- [Attention Is All You Need](https://arxiv.org/abs/1706.03762)

视频启发了选题和问题意识；教材根据学习依赖重新安排内容，不按分集照抄。更多引文见 [参考与延伸阅读](book/chapters/26-sources.tex)。

欢迎通过 Issue 提供计算核对、未解释的符号及跨章衔接建议。仓库尚未设置正式 LICENSE，请勿默认可任意再授权。
