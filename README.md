# AI by Intuition · 从函数到 Transformer 的直觉之旅

> **先有问题，再有直觉，然后才有公式。**

一本以**“模型怎样根据前文预测下一个 Token？”**为主线的中文 AI 原理教程。阅读从函数、向量和矩阵开始，经过 MLP 的训练，发现上下文建模的需要，依次推导 Attention、Transformer、语言模型训练和自回归生成。最后学习现代架构、后训练与工具系统。

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
| Ⅵ 选读与复习 | CNN、联想记忆和记忆容量可以提供什么其他直觉？ |

**前五部分连续阅读，第六部分不作为主线先修。** 以前放在 Attention 之前的外积、记忆干扰与最小二乘，现在完整保留为选读；让读者无需中途换数学视角就能从 RNN 直达 Self-Attention。

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
