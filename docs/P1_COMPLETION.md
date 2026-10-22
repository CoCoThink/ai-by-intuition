# P1 评审修订与验收记录

日期：2026-10-22。范围：对照 [REVIEW.md](REVIEW.md) 和 P0 后续计划中的 P1 工作包。**所有源码直接提交到 `main`**，没有独立 PR。此页记录完成内容；PDF 正式发布仍需按 [PUBLISHING.md](PUBLISHING.md) 手动办理。

| 工作包 | 本轮落地内容 | 追踪位置 |
| --- | --- | --- |
| P1-01 表示与 Embedding | 一维不可线性阈值分隔的小例子、二维映射；ID/One-hot/人工特征/可训练嵌入四方案；随机初始化、对称性与零偏置例外；20 步九坐标变化条形图 | [向量](../book/chapters/01-vectors.tex)、[Embedding](../book/chapters/20-embeddings.tex)、[坐标变化图](../book/figures/embedding-training-projection.tex) |
| P1-02 神经网络基础 | 具备替代文字的输入/隐藏/输出神经元图、行向量版 `L` 层通式、形状与激活说明 | [MLP](../book/chapters/10-mlp.tex) |
| P1-03 输入/输出总览 | 提前区分网络内部的 Attention 上下文读取与外部工具；标出 ID → Embedding → Attention → FFN → logits 的逐步形状 | [任务契约](../book/chapters/20b-task-contract.tex) |
| P1-04 Transformer 可读性 | 正文只留 `A`、`H`、`P-hat` 三份关键矩阵；其余完整参数及中间矩阵移附录 A；补实际 Attention 热力图、每位置概率柱图 | [正文](../book/chapters/22b-token-to-output.tex)、[数值附录](../book/chapters/00f-transformer-intermediates.tex)、[Attention 图](../book/figures/attention-weight-heatmap.tex)、[概率图](../book/figures/three-position-probabilities.tex) |
| P1-05 训练与动手 | 单步与 20 步损失、贪心预测完整轨迹；99 参数计算；可运行 PyTorch 自动求导脚本和 Colab Notebook | [训练正文](../book/chapters/22c-language-training.tex)、[损失曲线](../book/figures/training-20-step-loss.tex)、[实践附录](../book/chapters/24e-pytorch-lab.tex)、[PyTorch 脚本](../scripts/pytorch_starter.py)、[NumPy 轨迹](../scripts/teaching_trace.py)、[Notebook](../notebooks/pytorch_starter.ipynb) |
| P1-06 Agent 缺口链 | 同一虚构季度报告任务，按 Prompt/Context → Memory → RAG → Function Calling → MCP → Workflow/Agent → Skill/Subagent 改写 | [Agent](../book/chapters/23d-agent-systems.tex) |
| P1-07 现代架构 | GPT-2 各部件替换表；YaRN/NoPE、QK-Norm、HC/mHC、Gated DeltaNet/Mamba 等的定位；同一向量的 LayerNorm 与 RMSNorm 三维数值对照 | [架构](../book/chapters/22d-modern-transformers.tex)、[GPT 规模与 99 参数](../book/chapters/23a-from-toy-to-gpt.tex) |

## 可独立复算的数据基线

- 分类三位置输入为 `[1,3,4]`，目标 `[3,4,2]`；模型为三维、单头、一层、固定 LayerNorm 仿射参数的教学版，九组权重总计 99 个可训练元素。
- 初始平均交叉熵约 `1.798430`；一次学习率 0.04 的全参数 SGD 后约 `1.611377`；二十次更新后约 `0.483173`。同一份参数与数据，不另造训练结果。
- 第一次更新后贪心预测为 `[3,3,2]`；第九次更新后为 `[3,4,2]`。完整零到二十步轨迹应以 [NumPy 参考实现](../scripts/teaching_reference.py) 生成，不可修改标准数字以迎合图表。
- 在仓库根目录运行 `python3 scripts/teaching_reference.py`、`python3 scripts/teaching_trace.py`；安装 NumPy、PyTorch 后运行 `python3 scripts/pytorch_starter.py`。Notebook 使用相同脚本。

## 发布级质量门槛

- [x] 源码级章节、示例、交叉引用和关键图表检查已经纳入 `scripts/validate_book.py`；相关 CI 已通过源码结构阶段。
- [x] 已修复过去把新增数据表硬编码为旧数量的问题，新增数据表仍必须具有 `TH` 表头。
- [x] 近期独立的 Markdown 链接检查通过。
- [ ] **最新版本**完整 LuaLaTeX Tagged PDF 编译、页面与标签检查、所有公式 MathML-AF、PDF/UA-2 veraPDF 全部通过——以对应主分支提交的 CI 结果为准；尚未成功时不标记完成。
- [ ] 新增数值附录、Embedding 坐标变化图、三张关键矩阵及代码页完成最终 PDF 目视抽查。

P1 源码与文字修订已覆盖七个工作包；上述最后两项属于发布级验收，不能因为之前其他提交成功而自动判定本次版本通过。P2 另行规划，不纳入本页。
