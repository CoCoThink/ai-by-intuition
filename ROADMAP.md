# AI by Intuition · 教学结构与质量验收

## 一条明确的阅读路线

**问题：**一套数字运算为什么能学到语言中的规律并生成回答？

**学习方法：**提出问题 → 用小数字亲手计算 → 写出可推广公式 → 检查限制。
将自回归下一 Token 预测用作**贯穿的可训练任务**，并不将它当作所有 AI 的终极目标。

**先修知识：**建议具备高中代数基础；三角函数、导数、链式法则、
求和符号、指数对数和矩阵形状在数学速查页补充，并在正文反复配算例。

## 当前主分支结构：八部分、36 章、附录 A–K

| 部分 | 关键主题 | 检查点 |
|---|---|---|
| I 学习 | 标量函数、梯度、反传、泛化 | 参数同步更新 |
| II 矩阵 | 点积、MLP、Adam | 形状与两步优化 |
| III 文字 | Tokenizer、分类、Embedding | 三维任务契约 |
| IV 上下文 | RNN、朴素注意力、Q/K/V | 因果 Mask、缩放与多头 |
| V Transformer | Block、FFN、训练、生成 | 1.798430 → 1.611377 |
| VI 视觉桥接 | CNN、ViT 和视觉前缀 | 图像 Patch 与视觉表示 |
| VII 助手 | ICL、SFT、RAG、Agent loop、协议和部署 | 来源、授权和工具追踪 |
| VIII 架构 | RoPE、GQA、长上下文等 | 性能与证据边界 |
| 附录 H–K 提高专题 | 外积、串扰、Delta、MLP | $S=\sum k^\top v$、$y=xS$ |

I–VIII 构成连续正文；附录 A–G 保留复算、练习、答案与来源，H–K 为联想记忆提高专题。
修订状态见 [CHAPTER_MAPPING.md](docs/CHAPTER_MAPPING.md)，最终发布仍需完整 CI 和作者签核。

## 全书采用明确的矩阵约定

- Transformer、RNN 和 FFN 的主线：**每个 Token 占一行**，$X:T\times d$。
- 同一投影：$\boldsymbol q^\top=\boldsymbol x^\top W_Q$，
  改写为列向量必须写 $\boldsymbol q=W_Q^\top\boldsymbol x$。
- 输出头：$W_{\rm vocab}:d_{\rm model}\times|\mathcal V|$，
  logits 始终是隐藏表示乘这个矩阵。
- 联想记忆也采用**行向量检索**：$S=\sum_i k_i^\top v_i$，$xS=\sum_i(xk_i^\top)v_i$。
- 对 Block 统一使用 $X_{\rm att},X_{\rm block}$；
  单头输出、FFN 中层不再复用同一字母；符号与形状总表在数学速查之后。

## 评审可核验的新增算例

1. **位置编码：**统一三维参数的“春天 / 花”交换实验；无位置时仅交换输出行，有位置时不再等于单纯换行。
2. **缩放：**64 维独立分量点积的标准差为 8，比较缩放前后的 Softmax。
3. **两个头：**分别计算两个 2 维头，拼接成 4 维，再经过输出投影。
4. **Pre-Norm 和 LayerNorm：**图中的捷径箭头对应计算式；$(2,4)$ 归一化得到 $(-1,1)$（简化假设）。
5. **交叉熵梯度：**三位置平均损失 $1.798430\to1.611377$；共享输出头与 Q/K/V、FFN、Embedding 一起更新，第二位置仍预测错，不能把一次更新误写成所有问题已解决。
6. **现代架构：**实际旋转 RoPE 向量；计算 LoRA 的 $16{,}000$ 个增量参数、8-bit 量化和软标签损失。
7. **习题：**章末提供简短结果提示，完整演算仍集中在附录 D。

## 编辑与工程约束

- 现有修订候选按八个连续正文部分以及 A–K 附录组织；以 `main.tex` 与 CI 实际输出为准。
- 主线中的所有重要公式附有形状或具体数字，区分等号、近似和统计量级。
- 减少“下一章预告”和重复免责声明；小结只记录本章结论。
- 提示框为直觉、动手算、易错、边界、小结五类；Q/K/V 除角色配色外始终有文字标签。
- 视觉算例不只画流程方框：损失下降、反向计算图、三种拟合、验证集提前停止、CNN 扫描和因果掩码都有与公式核对过的数值图。
- 教材正文不出现视频字幕和编辑流程的修订说明。
- GitHub Actions 需要通过源码序列、术语超链接和数值结果检查；
  本地或 CI 编译后还需检查 PDF 的图表、目录、孤页与可见边界。

## 视频与研究启发

- [从函数到 Transformer](https://www.bilibili.com/video/BV1NCgVzoEG9/)
- [从 Transformer 到大模型](https://www.bilibili.com/video/BV15z4C6SEHT/)
- [联想记忆数学视角](https://alexwang.ai/posts/associative-memory/)

这些资源提供学习问题和参考背景；正文独立组织并独立推导。

## 持续维护与验收

教材以缺口驱动、数值可复算、层次分明与正确声明适用边界为长期原则。当前正文结构由 [book/main.tex](book/main.tex) 与 [阅读顺序](book/README.md) 定义；具体编写和数值校验规范见 [CONTRIBUTING.md](CONTRIBUTING.md)，不再在路线图里维护 M0–M6 阶段日志。

- **编辑正文或数值脚本：**运行完整 [PDF 构建](.github/workflows/build-latex.yml) 与源码检查，保留 PDF/UA-2、MathML-AF、图表语义、边界和跳转验收。
- **升级依赖：**对照 [构建可复现性规范](docs/BUILD-REPRODUCIBILITY.md) 留存运行环境与镜像记录。
- **发行状态：**本轮尚未正式出版；历史候选资料见 [V2 发布前验收](docs/V2_RELEASE_READINESS.md)，已发布统计以 [v0.1.0](https://github.com/CoCoThink/ai-by-intuition/releases/tag/v0.1.0) 为准。
