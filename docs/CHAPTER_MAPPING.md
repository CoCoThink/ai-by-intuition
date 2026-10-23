# V3 文本修订映射与实施记录

> 状态：**正在逐批修订 main；本文件是实施工作台，不代表教材已完成 V3 或已发布。**
> 原始设计：[REVIEW.md](REVIEW.md)。现有准确阅读顺序以 [book/main.tex](../book/main.tex) 为准。
> 当前基线：七个必读部分（32 个显示章节）+ 两组选读（2 个视觉章节、4 个记忆章节）= 38 章；附录 A–E。
> 目标：九个部分、39 章（新增朴素 Attention 一章）、附录 A–G；将记忆专题移到助手之前。
> **不要以源文件编号推断印刷章号**：印刷章号由 LaTeX 的 \`\\section\` 顺序生成。

## 目标阅读序列与现有源码

| 目标章节 | 主题与目标状态 | 当前章节源码（保持稳定文件名） |
| --- | --- | --- |
| 1–7 | 学习是什么：规则、参数、损失、梯度、反传、泛化 | \`00d-rules-gap\`、\`00-functions\`、\`16-loss-gradient\`、\`07-functions-relu\`、\`17-backpropagation\`、\`18b-end-to-end-learning\`、\`18-generalization\` |
| 8–11 | 向量、点积、矩阵、MLP 与训练工程 | \`01-vectors\`、\`02-dot-product\`、\`03-matrix-multiplication\`、\`10-mlp\`、\`18c-training-engineering\`（其中有合并在同一显示章的源文件） |
| 12–15 | Tokenizer、分类损失、Embedding、任务契约 | \`20a-tokenizer\`、\`20c-classification-loss\`、\`20-embeddings\`、\`20b-task-contract\` |
| 16–21 | 上下文、RNN、**新增朴素注意力**、Q/K/V、批量、位置与多头 | \`21a-context-gap\`、\`21-rnn\`、**待新增文件**、\`21b-why-attention\`、\`11-softmax-memory\`、\`22a-position-multihead\` |
| 22–27 | Transformer Block、FFN/输出头、贯通计算、联合训练、生成、真实 GPT-2 | \`22-transformer-architecture\`、\`10b-ffn-output-head\`、\`22b-token-to-output\`、\`22c-language-training\`、\`23-llm-systems\`、\`23a-from-toy-to-gpt\` |
| 28–31 | **记忆视角升为核心**：外积、串扰与改善、矩阵读出、高维容量 | \`04-key-value-outer-product\`、\`05-memory-interference\`、\`06-better-linear-memory\`、\`08-stacking-key-value\`、\`09-nonlinearity-and-memory\`、\`14-summary\`、\`13-capacity\`（七份源码、四个显示章） |
| 32–35 | ICL、后训练、Agent、部署 | \`23aa-pretraining-icl\`、\`23c-post-training\`、\`23d-agent-systems\`、\`23b-deployment-and-ecosystem\` |
| 36–37 | 现代架构、技术判断 | \`22d-modern-transformers\`、\`23e-tech-judgement\` |
| 38–39 | 选读视觉：CNN、ViT 到多模态 | \`19-cnn\`、\`19b-vit\` |

目标中 **I–VIII** 为核心主线，**IX** 为视觉选读。先把正文与测试基线稳定，再整体移动章节；不提前在 README 声称 39 章已实现。

## 实施关卡

- [x] R00：建立章节迁移映射和版本基线
- [ ] R01：首页整机预览、四个核心部件章首卡、其余章节体例
- [ ] R02：记忆专题统一行向量；联通线性 Attention 和 DeltaNet；重新复算答案
- [ ] R03：已补七阶段累计图、loop 消息追踪、二维 RAG 检索与 MCP 请求；仍须数值/排版与来源复核
- [ ] R04：已在当前 Q/K/V 章补朴素点积反例、未缩放标签；待正式拆成第 18 章及更新编号
- [ ] R05：已补初始损失基准；待真实 GPT-2 实验与锁定依赖
- [ ] R06：CoT/GRPO、现代架构、ViT 接口
- [ ] R07：习题层级、术语、版本与来源
- [ ] R08：更新校验脚本中的旧结构断言；验证 Tagged PDF、MathML-AF、PDF/UA-2

## 改动必须遵守的边界

1. 主三维示例仍以 \`scripts/teaching_reference.py\` 为数值唯一真源，局部二维、四维例明确标注；数值修订须同步答案。
2. 主线统一每 Token 一行的行向量约定。对原列向量记忆专题应先证明转置等价，再更新正文、附录与代码；改公式不意味着可跳过数值验算。
3. 对比线性 Attention 和 Softmax Attention 时注明它们一般不等价；比较 Delta 规则与最小二乘时只能在明确条件下说明关系。
4. GPT-2 在线模型下载是可选扩展，不能成为每次构建 Tagged PDF 的网络阻断项；锁定来源、版本及缓存/离线方案。
5. 各批改动要保持 \`book/main.tex\` 与 \`scripts/validate_book.py\` 对同一阅读顺序的判断一致；旧验证中的 32 章、38 章和 A–E 附录断言必须在正式重排时同步更新。
6. 不照搬视频中特有的表达；引用原观点应记录出处并核对授权。不得把未核实型号或百分比当作事实。
