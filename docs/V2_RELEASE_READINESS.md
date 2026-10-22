# V2 · 发布前验收台账（候选，尚未发布）

> **性质：**编审与构建证据记录，而非 GitHub Release，也不是实际屏读软件体验认证。
> **历史正式版：**[v0.1.0](https://github.com/CoCoThink/ai-by-intuition/releases/tag/v0.1.0)，99 页，保持原样。
> **最新已核验的预发布基线：**2026-10-22 源码提交 `2d9fc7e9bc864cbb315287ed6cec64d3898a8950`。本台账不自动证明此后提交也合格。

## 1. 源码与教学目标

新版从五个必读部分改成 **七个必读部分、31 个显示章节**，另有 CNN→ViT 与联想记忆两个独立选读专题。第九部分 X2 以四个显示章节整理七个旧源文件；A–E 五组附录包含公式速查、练习、术语、答案和参考文献。物理 `\\input{chapters/}` 源文件数量为 **55**（并不等于显示章节数）。

统一三维单头 Pre-Norm Transformer 使用 `[1,3,4] → [3,4,2]`，三位置联合损失从 **1.7984303789** 变为 **1.6113771577**；独立四维双头例和早期二维局部例均有单独界限，避免读者误以为共享同一组参数。

## 2. 可复核的 CI 证据

- [成功的整书构建 #39773683708](https://github.com/CoCoThink/ai-by-intuition/actions/runs/39772869124)（上述源码 `2d9fc7e`）：包含源码结构、可复算 NumPy 数值例、Tagged PDF、公式 MathML-AF 与 veraPDF PDF/UA-2。
- [成功的 Markdown / 工作流安全检查 #39771283849](https://github.com/CoCoThink/ai-by-intuition/actions/runs/39771283849)：包括本地 Markdown 链接、GitHub Actions YAML 和必须手动发布、仅允许 `main` 正式构建等门槛。
- 成功的 110 页 PDF 构建中，`validate_book.py` 报告 **9 个显示部分（七必读+两选读）、55 个输入源文件、23 张带 TH 表头的结构化表格、65 个表头单元格、17 幅 Figure 和 17 个 Alt、44 个 H1 与 182 个 H2 标题**。
- 同一构建的机器审计报告 **110 页、1,589 个 Formula / 1,589 个 MathML-AF 关联、1,009 种不同 MathML 文档**。veraPDF 报告 `PDF/UA-2: compliant=true; failedRules=0; failedChecks=0`。
- 对渲染完成的 PDF 附注执行独立检查：**422 条内部 GoTo、31 条外部 URI 链接、1,076 个命名位置**，422 条内链目标均可解析；正式 PDF CI 已加入自动目标验证且本基线通过。
- 发布工作流已改为下载 `ai-by-intuition-book` 工件，并通过 `pypdf` 验证**真实 PDF 页数与同次 MathML 审计一致**，不再要求旧版固定的 99 页或 1,472 个公式；产物名为 `AI-by-Intuition-Book.pdf`，历史 `Volume-01` 资产不变。

**独立发布演练：**从该次构建的 PDF 与同次 `pdfua2-machine-audit` 工件解压到独立目录，用 `pypdf`、JSON 和 XML 检查真实页数 110、公式 1,589/1,589、veraPDF `compliant=true` 且 `failedRules=failedChecks=0`；交付候选 PDF 的 SHA-256 为 `680b97484ce380cf40ce9b6f460844c2e63be64210e307b1cd422a965405b057`。演练只进行验证，**未创建 GitHub Release**。本 SHA-256 属于 `2d9fc7e` 审核快照，后续版式改动需重新计算。

**后续术语审稿：**`b352e833` 已将 26 条基础术语改为首次定义链接并补充测试；其完整构建 [#39777688357](https://github.com/CoCoThink/ai-by-intuition/actions/runs/39777688357) 尚需按最终 CI 结果验收。暂不将其视为本表机器通过的版本。

构建通过仅覆盖工具检查的规则；**不等于真人审稿、实机屏读体验或所有数学断言的独立形式化证明**。

## 3. PDF 目视抽查与已经修正的问题

从构建工件提取实际 PDF、渲染页面并检查：封面与目录（1–4）、标量优化（8–9）、反传（14）、Tokenizer/Embedding（26–30）、RNN/Attention（34、41）、Block 与联合训练（48、52）、预训练（58）、Agent（62、66）、现代架构与判断（69、72）、CNN/ViT（74–79）、附录公式和练习（90–93）、术语（96）、答案（104–105）及末尾参考资料（109–110）。这里是**抽样检查，不是声称每一页都已放大人工审读**。

审读时发现 ViT 最后一块“小结”单独落在几乎空白的第 78 页。通过精简重复解释、保留矩阵和数值，在 [修复提交](https://github.com/CoCoThink/ai-by-intuition/commit/23bdac760a73fd1e9aba6ffbd73cc26ca392aef8) 后合并回第 77 页：PDF 从 111 页变为 **110 页**。`scripts/validate_book.py` 新增**非末页中文字符过少即阻断**的布局回归规则，已在此版本通过；末页参考资料自然留白不按孤立内页误判。

同时修复旧目录“第七部分（联想记忆）”和“第五部分现代架构”的过期说法，改为可点击到正文定义的引用；分章自测标题不再展示旧文件名。

## 4. 正式发布前仍需满足的条件

- [x] 七必读部分与 31 章、两组扩展、A–E 附录结构及术语／习题基本回链进入可编译 PDF。
- [x] 统一 NumPy 示例、55 个源码输入、31 个显示章节、练习—答案一致性由脚本检查。
- [x] 基线 `2d9fc7e` 的 Tagged PDF、MathML-AF、PDF/UA-2、PDF 内链目标机器审计全绿；文档链接与工作流安全检查另在 [#39774141425](https://github.com/CoCoThink/ai-by-intuition/actions/runs/39774141425) 通过。
- [x] 对代表性篇章、图表、公式、目录、ViT 和附录做视觉抽样，解决 ViT 孤立小结页。
- [ ] **在任何后续影响 PDF 的改动之后**，重新取得同一提交的完整成功构建及审计；确认交付页数与记录一致。
- [ ] 完成出版前的作者审读，包括重要公式、中文语句、抽样无障碍阅读路径；机器合规不应被描述成实机体验认证。
- [ ] 明确选择新版本号（可用 `v0.2.0`，但尚未选定）、成功的主分支 `build_run_id`，再**手动**运行 [发布工作流](../.github/workflows/publish-release.yml)。
- [ ] 核对新 Release 的 PDF、`SHA256SUMS` 和 `build-audit.zip` 三项资产；旧版保持不可变。

完整步骤及 [候选版变更说明](V2_RELEASE_NOTES_DRAFT.md) 见 [PDF 出版与版本发布](PUBLISHING.md)，教学重构各阶段见 [V2 计划](STRUCTURE_REDESIGN_PLAN.md)。
