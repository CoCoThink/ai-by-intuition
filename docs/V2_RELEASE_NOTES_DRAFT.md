# V2 候选版发行说明（待作者确认，不是 Release）

> 建议发行标签：`v0.2.0`。此处仅为**草稿**，正式版本号、发行日期、作者签核和构建运行 ID 均以 [发布前验收表](V2_RELEASE_READINESS.md) 为准。不可从此文件推断版本已经发行。

## 一句话介绍

《AI by Intuition》新版将“标量学习—矩阵运算—Token 表示—注意力—完整 Transformer—助手系统—架构判断”组织成七个连续的必读部分，另含 CNN/ViT、联想记忆两个选读专题，及可复算的数学、练习与代码附录。

## 相对 v0.1.0 的主要变化

- **教学依赖顺序：** 先讲三分类 Logits、Softmax、交叉熵与 `p−onehot`，再用于语言模型训练；沿统一三点数据完整演示 MSE、`(w,b)` 解析解与同步梯度更新。
- **三维数值闭环：** 从 Token ID `[1,3,4]` 到目标 `[3,4,2]`，逐层给出注意力、输出概率与反向传播；正文只保留关键矩阵，完整中间数值移至附录。使用 `99` 个可训练参数的教学模型、一次损失 `1.798430 → 1.611377`、20 步下降至约 `0.483173` 的一致数值。
- **可阅读的工程地图：** 解释神经元、MLP 层、LayerNorm/RMSNorm、GPT-2 参数估算与架构组件替换；统一标记独立二维和四维局部例。
- **模型与系统的边界：** Prompt/Context/Memory、RAG、Function Calling、MCP、Workflow、Agent、Skill 和 Subagent 采用同一虚构季度报表任务分层解释；现代生态表区分 CUDA、PyTorch、Hugging Face、Ollama、vLLM。
- **原始论文与技术判断：** 对照 2017 Encoder–Decoder Transformer 的 Mask 和 Cross-Attention；将莫拉维克悖论及架构创新的争议作为可检验观点，而非绝对定论。
- **读者工具：** 目录前阅读路线、学习时间、统一向量约定、正文技术底座回顾、勘误页；B1/B2/B3 统一练习编号和术语精确小节引用。
- **实验：** [PyTorch/NumPy 复现 Notebook](../notebooks/pytorch_starter.ipynb) 和 [Softmax 温度、因果注意力、学习率交互 Notebook](../notebooks/p2-interactive-intuitions.ipynb)；源文件及脚本均保留在仓库。

## 质量与适用边界

候选 PDF 采用 LuaLaTeX/TeX Live 2026 生成结构化 Tagged PDF。候选构建包含 PDF/UA-2、MathML-AF、数值参考和 PDF 布局的机器检查；**具体页数、公式数及合规结果必须以最终签核的单次 GitHub Actions 运行工件为准**。机器校验不等同于真实屏幕阅读器用户体验测试。

教材所有数字是用于学习计算步骤的微型手算例，不能视为真实模型的泛化或商业性能证明。第三方服务与框架的 API、许可证、兼容平台以及版本可能变化，请优先检查原始文档。

## 正式发布前填写

- **最终版本标签：** 待作者确定（建议 `v0.2.0`）
- **审查提交 SHA：** 待最终 main 构建确认
- **成功的 Build one PDF book run ID：** 待最终 main 构建确认
- **PDF 页数与公式 MathML-AF 统计：** 待从对应审计工件填写
- **PDF/UA-2 结论：** 待从对应 veraPDF XML 填写
- **作者签核及日期：** 未完成
- **正式 Release 地址：** 尚未创建

完整核对流程见 [出版流程](PUBLISHING.md)，修订概览见 [勘误与版本记录](ERRATA.md)，发行状态见 [V2 验收表](V2_RELEASE_READINESS.md)。
