# V3 文本修订映射与实施记录

> 状态：**主分支修订持续进行；本文件记录结构与历史工作，不代表正式 Release。**
> 原始设计：[REVIEW.md](REVIEW.md)。现有准确阅读顺序以 [book/main.tex](../book/main.tex) 为准。
> 源文件层面的最新完整编辑复查及未闭合事项见 [全文编辑审校记录](FULL_TEXT_AUDIT.md)。
> 历史基线：七个必读部分（32 个显示章节）+ 两组选读（2 个视觉章节、4 个记忆章节）= 38 章；附录 A–E。
> 当前 main 结构：八部分、36 章、附录 A–K。视觉专题在助手之前，联想记忆在正文收束后的提高附录；Agent 拆为三章，章号由 LaTeX 自动生成。
> **不要以源文件编号推断印刷章号**：印刷章号由 LaTeX 的 \`\\section\` 顺序生成。

## 当前正文与附录映射（以 `book/main.tex` 为准）

| 正文章号 | 主线与稳定源码 |
|---|---|
| 1–6 | 学习：`00-functions`、`16-loss-gradient`、`18c-training-engineering`、`07-functions-relu`、`17-backpropagation`、`18b-end-to-end-learning`、`18-generalization` |
| 7–10 | 向量／点积／矩阵／MLP：`01-vectors`、`02-dot-product`、`03-matrix-multiplication`、`10-mlp` |
| 11–14 | Tokenizer、分类、Embedding、任务契约 |
| 15–20 | 上下文、RNN、朴素 Attention、Q/K/V、Self-Attention、位置与多头 |
| 21–26 | Transformer Block、FFN、三位置贯通、训练、生成、从玩具到 GPT |
| 27–28 | **视觉正文**：`19-cnn`、`19b-vit`（视觉前缀与多模态桥接） |
| 29–34 | ICL、后训练、`23d-agent-systems`（RAG）、`23d-agent-tools`（Agent 循环）、`23d-agent-protocols`（协议／多 Agent）、部署 |
| 35–36 | 现代 Transformer（必读先行、选读集中）、评测与技术判断；其后以`23f-foundation-recap` 收束正文 |
| 附录 A–G | 公式、实验、练习、答案、术语、文献、勘误 |
| 附录 H–K | `04-key-value-outer-product` 到 `13-capacity`：联想记忆与线性状态提高专题 |

新增核心解释包括多 GPU、混合精度、FlashAttention、从交叉熵到困惑度、Benchmark 污染、Best-of-N 测试时计算、提示注入、模型偏见及 Softmax 稳定计算。章末保留短结果提示和附录 D 的完整答案。

**历史里程碑号和旧版构建统计仅对应各自旧提交，不作为当前发布结论。**

## 实施关卡

- [x] R00：建立章节迁移映射和版本基线
- [x] R01：39/39 章均采用紧凑整机定位条；`07b368c` 的 144 页成功 PDF 已通过第 11／15 章结尾孤页专项回归。正在扩展章首定位条的实际页码及垂直位置检测；人工逐页签核仍属 R08
- [x] R02：行向量记忆与线性 Attention 已连接；第 29 章新增 A/B 残差写入与旧记忆损伤的逐项复算，交替重访收敛回归已加脚本；完整 PDF 复核归 R08。
- [ ] R03：Agent 已改用报表任务约束／证据／计算／审计的独立叙事，七行图改为核对关口；保留 loop、二维 RAG 与 MCP 实例，仍须人工对照讲稿与发布授权复核
- [x] R04：第 18 章朴素注意力与第 19 章独立 W_Q/W_K 的非对称原始分数形成真正对照，矩阵、图卡和测试已同步
- [x] R05：真实 GPT-2 已由 [独立运行 #39897932969](https://github.com/CoCoThink/ai-by-intuition/actions/runs/39897932969) 实测 5 个 Token、全 logits 形状、温度概率和及零上三角掩码；模型 revision 与完整依赖存档，PDF 构建不加载模型权重
- [x] R06：CoT/GRPO、线性状态、公开模型 config、MLA 假设缓存、窗口掩码以及 ViT→LLM 投影算例均已落地；待整本视觉/数值验收
- [ ] R07：术语附录已形成 100 基础＋33 现代的 133 行中文／English／定义／章节统一四列表，表格自动派生并有防漂移门禁；原有 47 处自测全部扩为回忆／手算／迁移，附录答案同步，B2 增标准库编程练习。内容实现已到位；仍待最终人工审校与原课程授权签核
- [ ] R08：成功基线 [#39929702902](https://github.com/CoCoThink/ai-by-intuition/actions/runs/39929702902)（`07b368c`）为 144 页、2,366/2,366 MathML-AF 和 PDF/UA-2 零失败；[哈希固定的灰度与章末证据](PRINT_PROOF_07B368C.md)已入库。下一 CI 将自带源码 SHA/运行号；真正的人工高清逐页、屏读、来源授权及作者发行签核仍未完成

## 改动必须遵守的边界

1. 主三维示例仍以 \`scripts/teaching_reference.py\` 为数值唯一真源，局部二维、四维例明确标注；数值修订须同步答案。
2. 主线统一每 Token 一行的行向量约定。对原列向量记忆专题应先证明转置等价，再更新正文、附录与代码；改公式不意味着可跳过数值验算。
3. 对比线性 Attention 和 Softmax Attention 时注明它们一般不等价；比较 Delta 规则与最小二乘时只能在明确条件下说明关系。
4. GPT-2 在线模型下载是可选扩展，不能成为每次构建 Tagged PDF 的网络阻断项；锁定来源、版本及缓存/离线方案。
5. 各批改动要保持 \`book/main.tex\` 与 \`scripts/validate_book.py\` 对同一阅读顺序的判断一致；旧验证中的 32 章、38 章和 A–E 附录断言必须在正式重排时同步更新。
6. 不照搬视频中特有的表达；引用原观点应记录出处并核对授权。不得把未核实型号或百分比当作事实。
