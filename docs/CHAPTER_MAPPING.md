# V3 文本修订映射与实施记录

> 状态：**正在逐批修订 main；本文件是实施工作台，不代表教材已完成 V3 或已发布。**
> 原始设计：[REVIEW.md](REVIEW.md)。现有准确阅读顺序以 [book/main.tex](../book/main.tex) 为准。
> 源文件层面的最新完整编辑复查及未闭合事项见 [全文编辑审校记录](FULL_TEXT_AUDIT.md)。
> 历史基线：七个必读部分（32 个显示章节）+ 两组选读（2 个视觉章节、4 个记忆章节）= 38 章；附录 A–E。
> 当前 main 结构：九部分、39 章、附录 A–G；新增朴素 Attention 独立章，记忆专题已移到助手之前。内容和 CI 验收仍在推进。
> **不要以源文件编号推断印刷章号**：印刷章号由 LaTeX 的 \`\\section\` 顺序生成。

## 目标阅读序列与现有源码

| 目标章节 | 主题与目标状态 | 当前章节源码（保持稳定文件名） |
| --- | --- | --- |
| 1–7 | 学习是什么：规则、参数、损失、梯度、反传、泛化 | \`00d-rules-gap\`、\`00-functions\`、\`16-loss-gradient\`、\`07-functions-relu\`、\`17-backpropagation\`、\`18b-end-to-end-learning\`、\`18-generalization\` |
| 8–11 | 向量、点积、矩阵、MLP 与训练工程 | \`01-vectors\`、\`02-dot-product\`、\`03-matrix-multiplication\`、\`10-mlp\`、\`18c-training-engineering\`（其中有合并在同一显示章的源文件） |
| 12–15 | Tokenizer、分类损失、Embedding、任务契约 | \`20a-tokenizer\`、\`20c-classification-loss\`、\`20-embeddings\`、\`20b-task-contract\` |
| 16–21 | 上下文、RNN、**新增朴素注意力**、Q/K/V、批量、位置与多头 | \`21a-context-gap\`、\`21-rnn\`、\`21c-naive-attention\`、\`21b-why-attention\`、\`11-softmax-memory\`、\`22a-position-multihead\` |
| 22–27 | Transformer Block、FFN/输出头、贯通计算、联合训练、生成、真实 GPT-2 | \`22-transformer-architecture\`、\`10b-ffn-output-head\`、\`22b-token-to-output\`、\`22c-language-training\`、\`23-llm-systems\`、\`23a-from-toy-to-gpt\` |
| 28–31 | **记忆视角升为核心**：外积、串扰与改善、矩阵读出、高维容量 | \`04-key-value-outer-product\`、\`05-memory-interference\`、\`06-better-linear-memory\`、\`08-stacking-key-value\`、\`09-nonlinearity-and-memory\`、\`14-summary\`、\`13-capacity\`（七份源码、四个显示章） |
| 32–35 | ICL、后训练、Agent、部署 | \`23aa-pretraining-icl\`、\`23c-post-training\`、\`23d-agent-systems\`、\`23b-deployment-and-ecosystem\` |
| 36–37 | 现代架构、技术判断 | \`22d-modern-transformers\`、\`23e-tech-judgement\` |
| 38–39 | 选读视觉：CNN、ViT 到多模态 | \`19-cnn\`、\`19b-vit\` |

目前 **I–VIII** 为核心主线、**IX** 为视觉选读；已在 `main.tex` 完成重排。尚未 Release；`3800ab9` 机器基线已通过，进一步修改应按新 SHA 再验收。

## 实施关卡

- [x] R00：建立章节迁移映射和版本基线
- [ ] R01：已完成重点章节导引卡、第 22 章十步口述和原创 Encoder／Decoder 对照图，并清理九处重复章首回顾；尚待全书固定位置的小型整机图与人工视觉审校
- [x] R02：行向量记忆与线性 Attention 已连接；第 29 章新增 A/B 残差写入与旧记忆损伤的逐项复算，交替重访收敛回归已加脚本；完整 PDF 复核归 R08。
- [ ] R03：Agent 已改用报表任务约束／证据／计算／审计的独立叙事，七行图改为核对关口；保留 loop、二维 RAG 与 MCP 实例，仍须人工对照讲稿与发布授权复核
- [x] R04：第 18 章朴素注意力与第 19 章独立 W_Q/W_K 的非对称原始分数形成真正对照，矩阵、图卡和测试已同步
- [x] R05：真实 GPT-2 已由 [独立运行 #39897932969](https://github.com/CoCoThink/ai-by-intuition/actions/runs/39897932969) 实测 5 个 Token、全 logits 形状、温度概率和及零上三角掩码；模型 revision 与完整依赖存档，PDF 构建不加载模型权重
- [x] R06：CoT/GRPO、线性状态、公开模型 config、MLA 假设缓存、窗口掩码以及 ViT→LLM 投影算例均已落地；待整本视觉/数值验收
- [ ] R07：术语附录已形成 100 基础＋33 现代的 133 行中文／English／定义／章节统一四列表，表格自动派生并有防漂移门禁；原有 47 处自测全部扩为回忆／手算／迁移，附录答案同步，B2 增标准库编程练习。内容实现已到位；仍待最终人工审校与原课程授权签核
- [ ] R08：`3800ab9` 的 [CI #39913269593](https://github.com/CoCoThink/ai-by-intuition/actions/runs/39913269593) 验证 143 页、2,134/2,134 MathML-AF、PDF/UA-2 机器合规、63 章节文件、133 项中英四列表与 47 处自测通过；灰度技术预检不能代替最终高分辨率逐页审校、来源授权与发行签核

## 改动必须遵守的边界

1. 主三维示例仍以 \`scripts/teaching_reference.py\` 为数值唯一真源，局部二维、四维例明确标注；数值修订须同步答案。
2. 主线统一每 Token 一行的行向量约定。对原列向量记忆专题应先证明转置等价，再更新正文、附录与代码；改公式不意味着可跳过数值验算。
3. 对比线性 Attention 和 Softmax Attention 时注明它们一般不等价；比较 Delta 规则与最小二乘时只能在明确条件下说明关系。
4. GPT-2 在线模型下载是可选扩展，不能成为每次构建 Tagged PDF 的网络阻断项；锁定来源、版本及缓存/离线方案。
5. 各批改动要保持 \`book/main.tex\` 与 \`scripts/validate_book.py\` 对同一阅读顺序的判断一致；旧验证中的 32 章、38 章和 A–E 附录断言必须在正式重排时同步更新。
6. 不照搬视频中特有的表达；引用原观点应记录出处并核对授权。不得把未核实型号或百分比当作事实。
