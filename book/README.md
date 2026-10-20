# 全书目录 · AI by Intuition

**先问计算机怎样学会回应文字，再解释为什么用下一 Token 预测训练自回归语言模型。** 这是贯穿数学计算的教学任务，不是 AI 的唯一目标。前五部分连续阅读，第六部分为选读和查阅区。PDF 中章节号由 LaTeX 自动生成。

**[唯一编译入口](main.tex)** · **[GitHub Actions 完整 PDF](https://github.com/CoCoThink/ai-by-intuition/actions/workflows/build-latex.yml)**

## Ⅰ · 把文字变成可计算的数字

- [阅读指南：先有贯穿问题，再看公式](chapters/00-guide.tex)
- [函数是怎样的可调计算规则](chapters/00-functions.tex)
- [为什么一个对象需要一列数字](chapters/01-vectors.tex)
- [点积怎样表示方向与匹配](chapters/02-dot-product.tex)
- [矩阵与行列转置图卡](chapters/03-matrix-multiplication.tex)
- [Token ID 怎样查成向量](chapters/20-embeddings.tex)
- [用“春天 / 花 / 开了 / 。”固定下一 Token 预测任务](chapters/20b-task-contract.tex)

## Ⅱ · 让神经网络学会预测

- [线性运算为什么需要非线性](chapters/07-functions-relu.tex)
- [两层 MLP 的手算和尺寸](chapters/10-mlp.tex)
- [损失、导数与梯度下降](chapters/16-loss-gradient.tex)
- [怎样沿计算图求梯度](chapters/17-backpropagation.tex)
- [一次完整参数更新](chapters/18b-end-to-end-learning.tex)
- [训练题做得好不等于泛化](chapters/18-generalization.tex)

## Ⅲ · 让词与词交换信息

- [RNN 是什么：逐词读取、传递状态并手算三步](chapters/21-rnn.tex)
- [Attention 是什么：算出 Query/Key 分数，再加权读取 Value](chapters/21b-why-attention.tex)
- [把刚才的 Attention 写成矩阵：从单个 Query 到批量计算](chapters/11-softmax-memory.tex)
- [Q/K/V 投影、行列图卡与整段 Self-Attention](chapters/12-self-attention-matrices.tex)

## Ⅳ · 组装、训练并使用 Transformer

- [位置、多头、残差、归一化与 Mask](chapters/22-transformer-architecture.tex)
- [FFN 与词表输出头不是同一层](chapters/10b-ffn-output-head.tex)
- [从两个 Token 到上下文化向量的手算](chapters/22b-token-to-output.tex)
- [错位标签、因果掩码和交叉熵](chapters/22c-language-training.tex)
- [从候选概率到自回归生成与 KV Cache](chapters/23-llm-systems.tex)

## Ⅴ · 改进模型并构建可靠应用

- [生成成本引出 GQA、RoPE、MoE 等取舍](chapters/22d-modern-transformers.tex)
- [SFT、RLHF、RLVR 与推理策略](chapters/23c-post-training.tex)
- [RAG、工具、工作流、权限和验证](chapters/23d-agent-systems.tex)
- [量化、硬件、部署与多模态](chapters/23b-deployment-and-ecosystem.tex)

## Ⅵ · 选读专题与知识回溯

- [选读：图片的局部结构与卷积](chapters/19-cnn.tex)
- [选读：从外积写入一条关联](chapters/04-key-value-outer-product.tex)
- [选读：多条记忆为什么互相干扰](chapters/05-memory-interference.tex)
- [选读：用最小二乘改善线性记忆](chapters/06-better-linear-memory.tex)
- [选读：堆叠 Key/Value 与维度](chapters/08-stacking-key-value.tex)
- [选读：从记忆角度重新看 MLP](chapters/09-nonlinearity-and-memory.tex)
- [选读：Linear、MLP 和 Attention 的联系与边界](chapters/14-summary.tex)
- [联想记忆手算练习](chapters/15-practice.tex)
- [选读：高维记忆的统计假设](chapters/13-capacity.tex)
- [100 个可点击回溯的基础术语](chapters/24-lexicon.tex)
- [现代模型与 Agent 的术语索引](chapters/24b-modern-lexicon.tex)
- [整书计算复习题](chapters/25-integrated-practice.tex)
- [现代模型和工具系统综合题](chapters/25b-modern-practice.tex)
- [原始视频与参考文献](chapters/26-sources.tex)

## 本书的阅读约定

读者先在主线中完成`Embedding → MLP → 训练 → RNN 的问题 → Attention → Transformer → 语言模型训练与生成`。联想记忆的外积推导、CNN 与高维记忆容量是独立拓展，**不会作为进入 Attention 的前置要求**。

文字、向量、张量和公式尽量用同一组可手算示例联系起来；重要的行列方向在矩阵章与 Self-Attention 章均有彩色对照图卡。术语地图保留正文内跳转，并随章节重新排序自动更新编号。

## 编译

```bash
cd book
latexmk -xelatex -interaction=nonstopmode -halt-on-error -outdir=build main.tex
```

最终始终生成**一份连续的中文 PDF**，不为章节分别发布 PDF。
