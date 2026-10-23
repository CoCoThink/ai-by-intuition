# V3 修订候选：发布前验收与人工签核

> **状态：39 章修订的机器基线已通过；人工逐页审校、来源授权和发布签核未完成。**
> 当前正式 Release 仍是 [v0.1.0](https://github.com/CoCoThink/ai-by-intuition/releases/tag/v0.1.0)。
> 本页仅用于 V3 候选；[V2 的历史验收](V2_RELEASE_READINESS.md)不应被当作当前版本的证据。

## 可追溯机器基线（不是持续自动有效的状态）

| 项目 | 成功验证的明确来源 |
|---|---|
| 源码 SHA | [3800ab9e2470939db7b93f047bebfd0176556e7a](https://github.com/CoCoThink/ai-by-intuition/commit/d4f45cd7630239750adb0c71cbec3718fe705aae) |
| 成功的 main 构建 | [Build one PDF book #39913269593](https://github.com/CoCoThink/ai-by-intuition/actions/runs/39913269593) |
| 内容结构 | 9 部分、39 个编号章节、A–G 共 7 个附录 |
| PDF | **143 页** Tagged PDF；页面文字边界检查通过 |
| Formula | **2,134 / 2,134** 具有可解析的 MathML-AF 关联 |
| MathML | 1,308 份不同的 MathML 文档 |
| veraPDF | PDF/UA-2 **compliant=true、failedRules=0、failedChecks=0** |
| 源码与数值 | 63 个章节输入文件、133 项中英四列表、47 处三层次自测、统一三维训练及独立数值回归全部通过 |
| 审计资产 | 此次 CI 的 `ai-by-intuition-book` 和 `pdfua2-machine-audit` |

**重要：上述机器数字仅对该 SHA 的 PDF 有效。**
任何在此之后对 `book/`、`scripts/` 或构建配置的修改，
必须以新 SHA 的成功全量工作流重新验收；本文件不得自行宣称后续主分支已通过。

## 全书灰度技术预检（区别于人工签核）

已从 [完整成功构建 #39906433306](https://github.com/CoCoThink/ai-by-intuition/actions/runs/39906433306)
取得对应 `a5fb466b` 的 **137 页 PDF**，
将 **137／137 页**渲染为灰度图并制作七张缩略总览。
技术抽查未发现整页缺失或明显大面积裁切；
实看页 28 的 Warmup/AdamW 算例和页 56 的 Transformer 十步及架构图，
未见明显文字重叠或图形截断。

最终通过的 [#39907188928](https://github.com/CoCoThink/ai-by-intuition/actions/runs/39907188928)
对应 `d4f45cd`，在 Encoder 框内进一步补足了
FFN／归一化等部件，并已通过新的 PDF/UA-2 机器验收。
**上述全书灰度渲染的确切文件属于先前的 `a5fb466b`，
不能视作对最终源码 SHA 的人工高分辨率逐页签核。**
发行前仍须按 [人工逐页流程](PRINT_PROOF.md)
核对图形辨识度、细线与文字、替代文字、屏读顺序和版权复用。

## 尚需人工确认的发布阻断项

- [ ] 运行 [灰度逐页审校](PRINT_PROOF.md)，检查所有页面的阅读顺序、版心、对比度、图形标签、表格、长链接和数学排印，并记录日期及审校者
- [ ] 检查重要图的替代文字是否与实际图示一致；机器检测到替代文字不保证质量充分
- [ ] 完成 [Agent 教学来源与复用核对](ATTRIBUTION_REVIEW.md)，记录必要授权或独立改写依据
- [x] 固定版本 GPT-2 真实权重实验由 [成功运行 #39897932969](https://github.com/CoCoThink/ai-by-intuition/actions/runs/39897932969) 验证；[完整日志、依赖和热图](GPT2_REAL_RUN.md) 已归档。该结果属于单独模型实验，与本书 PDF/UA-2 机器验收分别记录
- [ ] 选取待发布版本**最终 SHA**，重新运行一次成功的完整 PDF + MathML-AF + PDF/UA-2 工作流
- [ ] 记录作者明确的最终发布签核、版本号与日期，并确认没有未解决阻断问题

机器审计与灰度图不能替代真实屏读设备的用户体验验证；
本项目当前将人工阅读/视觉核对设为发布门槛，
不暗示已经完成真实屏幕阅读器测试。

## 发布与维护

源码目录和修订映射见 [CHAPTER_MAPPING.md](CHAPTER_MAPPING.md)。
发行步骤见 [PUBLISHING.md](PUBLISHING.md)；
正式发布只能使用审核通过、绑定 SHA 的构建工件，
不能直接复用较早成功版本的 PDF 或审计统计。
