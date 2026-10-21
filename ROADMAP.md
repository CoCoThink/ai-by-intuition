# AI by Intuition · 教学结构与质量验收

## 一条明确的阅读路线

**问题：**一套数字运算为什么能学到语言中的规律并生成回答？

**学习方法：**提出问题 → 用小数字亲手计算 → 写出可推广公式 → 检查限制。
将自回归下一 Token 预测用作**贯穿的可训练任务**，并不将它当作所有 AI 的终极目标。

**先修知识：**建议具备高中代数基础；三角函数、导数、链式法则、
求和符号、指数对数和矩阵形状在数学速查页补充，并在正文反复配算例。

## 前五部分为必读

| 部分 | 学会的能力 | 应能手算的检查 |
|---|---|---|
| I 表示与数据契约 | 从 Token ID 到行向量、形状、目标 | 矩阵乘法和标签对齐 |
| II 参数学习 | ReLU、MLP、误差、梯度、反向传播 | 一次梯度下降 |
| III 上下文读取 | RNN、Attention、Q/K/V | 三条 Key 的权重与读出 |
| IV Transformer 闭环 | 位置、多头、Pre-Norm Block、输出头、训练 | 双头、LayerNorm、p−onehot 与输出头 SGD 与一次 Value/FFN 共同更新 |
| V 架构与系统 | RoPE、MoE、GQA、SFT、Agent、LoRA、量化与蒸馏 | 旋转、缓存、参数与概率 |

第六部分为 CNN/ViT 选读，第七部分为联想记忆/高维容量选读，两者可独立阅读。
所有习题、术语、英文索引、概念关系图与答案位于选读部分之后的**附录**，不要因为跳过选读而漏掉复习。

## 全书采用明确的矩阵约定

- Transformer、RNN 和 FFN 的主线：**每个 Token 占一行**，$X:T\times d$。
- 同一投影：$\boldsymbol q^\top=\boldsymbol x^\top W_Q$，
  改写为列向量必须写 $\boldsymbol q=W_Q^\top\boldsymbol x$。
- 输出头：$W_{\rm vocab}:d_{\rm model}\times|\mathcal V|$，
  logits 始终是隐藏表示乘这个矩阵。
- 联想记忆的选读部分可能采用**列向量检索**，必须显式说明是
  同一计算的转置表达，而不是把两种权重方向直接混用。
- 对 Block 统一使用 $X_{\rm att},X_{\rm block}$；
  单头输出、FFN 中层不再复用同一字母；符号与形状总表在数学速查之后。

## 评审可核验的新增算例

1. **位置编码：**“花 / 开了”交换位置，比较没有位置和加入位置向量后的结果。
2. **缩放：**64 维独立分量点积的标准差为 8，比较缩放前后的 Softmax。
3. **两个头：**分别计算两个 2 维头，拼接成 4 维，再经过输出投影。
4. **Pre-Norm 和 LayerNorm：**图中的捷径箭头对应计算式；$(2,4)$ 归一化得到 $(-1,1)$（简化假设）。
5. **交叉熵梯度：**从 $p-\mathrm{onehot}$ 更新输出头一列和其余列，正确 Token 概率约从 $0.059$ 升至 $0.427$，贪心预测从错误“花”翻转为正确“开了”。
6. **现代架构：**实际旋转 RoPE 向量；计算 LoRA 的 $16{,}000$ 个增量参数、8-bit 量化和软标签损失。
7. **习题：**答案集中到附录，避免同一页立刻看到。

## 编辑与工程约束

- 保持五个必读部分、两个选读部分、一个 PDF 和可编辑的 LaTeX/TikZ 插图。
- 主线中的所有重要公式附有形状或具体数字，区分等号、近似和统计量级。
- 减少“下一章预告”和重复免责声明；小结只记录本章结论。
- 提示框固定为四类：直觉、动手算、易错、小结；Q（蓝）／K（青）／V（橙）采用贯穿主线的角色配色。
- 视觉算例不只画流程方框：损失下降、反向计算图、三种拟合、验证集提前停止、CNN 扫描和因果掩码都有与公式核对过的数值图。
- 教材正文不出现视频字幕和编辑流程的修订说明。
- GitHub Actions 需要通过源码序列、术语超链接和数值结果检查；
  本地或 CI 编译后还需检查 PDF 的图表、目录、孤页与可见边界。

## 视频与研究启发

- [从函数到 Transformer](https://www.bilibili.com/video/BV1NCgVzoEG9/)
- [从 Transformer 到大模型](https://www.bilibili.com/video/BV15z4C6SEHT/)
- [联想记忆数学视角](https://alexwang.ai/posts/associative-memory/)

这些资源提供学习问题和参考背景；正文独立组织并独立推导。

## 工程构建与 Tagged PDF 验收（2026-10-21）

- **已通过：**固定 **TeX Live 2026 + LuaLaTeX**，使用 `\DocumentMetadata{lang=zh-CN,tagging=on}` 构建整本书；[GitHub Actions 成功记录](https://github.com/CoCoThink/ai-by-intuition/actions/runs/39609436412)为 99 页。
- **已通过：**CI 验证七部分和 47 个 `\input` 章节源文件、数值样例、目录提取、PDF 文字边界，并用 `pypdf==5.9.0` 核查 `/MarkInfo`、`/StructTreeRoot` 及结构树内容；上次统计为 1,471 个 Formula、21 张 Table／59 个 TH、16 个 Figure／16 处替代文字、48 个 H1／180 个 H2。
- **已修复：**正文标题 H1/H2 与图注父子标签的缺失／非法关系；保留继续抽查辅助技术标题导航和图注读序。
- **机器验收已通过：** [最新 veraPDF PDF/UA-2 验证](https://github.com/CoCoThink/ai-by-intuition/actions/runs/39609436412) 报告 1,727 项规则、736,481 项检查全部通过，CI 已提升为失败阻断。**仍未完成**实际读屏验收、数学公式 MathML、复杂表格读屏与阅读顺序。全书 MathML 在 `experiment/full-book-mathml` 分支隔离尝试，生产 `main` 仍采用已通过的经典数学字体，**不能**将 `Tagged: yes` 当作 PDF/UA 合规。
- **下一阶段：**持续运行独立 PDF/UA-2 机器验证，检查实验数学语义的实际嵌入与读屏表现，复核跨页图文阅读顺序，再开展辅助技术人工验收。

工程细节、目前已知限制与复现命令见 [无障碍现状及验收](docs/ACCESSIBILITY.md)；构建命令见 [README](README.md)。
