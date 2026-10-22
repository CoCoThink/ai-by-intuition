# P2 修订完成记录（候选内容）

依据：[原始评审](REVIEW.md)、[P1 完成记录](P1_COMPLETION.md)。P2 源码已直接提交 `main`，正式 PDF Release 仍须遵守 [出版流程](PUBLISHING.md) 与 [V2 发布验收](V2_RELEASE_READINESS.md)。

## 五个工作包

| 项目 | 已完成的候选源码交付 | 验收依据 |
| --- | --- | --- |
| P2-01 技术生态 | [部署章节](../book/chapters/23b-deployment-and-ecosystem.tex)加入 CUDA、PyTorch、Hugging Face Hub、Ollama、vLLM 的职责对照，附官方文档并注明版本易变 | 表格 TH、官方链接、源文件检查 |
| P2-02 原论文对照 | [Transformer 架构](../book/chapters/22-transformer-architecture.tex)补 Encoder/Decoder/Cross-Attention、2017 原论文 Post-Norm 与本书 Pre-Norm 差异；中文到英语的右移训练目标和不同 Mask 边界 | 公式、术语与结构检查 |
| P2-03 争议与技术判断 | [技术判断](../book/chapters/23e-tech-judgement.tex)加入莫拉维克悖论、架构创新空间争论的支持和反方证据；不使用“已死/必然取代”等定论 | 区分历史观察、可检验假说、研究证据 |
| P2-04 阅读导引与总结 | [目录前阅读路线](../book/chapters/00g-reading-routes.tex)、[技术底座回顾](../book/chapters/23f-foundation-recap.tex)、[勘误记录](ERRATA.md)；新增“边界”框，与“易错”框区分 | 七部分知识表、时间为建议范围、全部章节链接和表头 |
| P2-05 交互层 | [Notebook](../notebooks/p2-interactive-intuitions.ipynb) 含 Softmax 温度、因果 Attention、三点回归学习率三套可独立调节的滑块；[纯标准库检查](../scripts/check_p2_notebook.py) 纳入教材源检查 | Notebook JSON/语法、三组数学基线、三个交互入口 |

## 不应破坏的教材基线

- 输入 Token 为 `[1,3,4]`、目标为 `[3,4,2]`，三维主例共有 99 个可训练参数。
- 平均交叉熵的标准数值为训练前 `1.798430`、一次联合 SGD 后 `1.611377`、20 步后约 `0.483173`。
- 交互实验的温度改变只重标定概率，学习率实验使用**独立的三点回归**，均不得冒称修改了原书三维网络权重。
- 已发布的 [v0.1.0](https://github.com/CoCoThink/ai-by-intuition/releases/tag/v0.1.0) 不覆盖；候选 `main` 与正式 Release 是不同的状态。

## 合并后的检查门槛

- [x] 五个 P2 工作包已经形成对应的正文/附录/Notebook 源码。
- [x] 源码校验扩展至阅读导引、原论文对照、生态表、技术争议和 Notebook。
- [x] P2 最终教材源码提交 `2cad92cd` 的 [完整 PDF CI #39816203928](https://github.com/CoCoThink/ai-by-intuition/actions/runs/39816203928) 为 success，包含编译、Tagged PDF 结构、排版文字边界、1,836/1,836 MathML-AF 和 veraPDF PDF/UA-2（零失败）。
- [x] 已渲染并抽查目录前导读、原论文表、技术生态表、技术底座页与最终参考文献末两页；此前尾页孤立段落已在 `2cad92cd` 修正。正式作者全面审阅与签核另列。
- [ ] 作者确认 V2 发布候选版本、审稿结论、Release 说明及签核信息。

更新这些复选框时需同时记录对应的完整主分支 SHA 和 CI URL，不能拿旧版成功记录代替最新构建。P2 的“源码完成”并不意味着已完成 V2 人工签核或正式发行。
