# V2 出版候选 · 当前状态与验收

> **唯一活跃的 V2 发布前状态文档。候选版尚未正式发布。**
> 2026-10-22 最后一次通过完整 PDF 验收的源码：`b352e833ad64e0bed711d7e498754f7349ff3bc8`。
> 其后截至本次清理仅修改 Markdown 说明与过程文件；若此后改动教材、脚本或 PDF 构建工作流，必须重新验收。

## 已完成的教材结构与内容

- 主线 **七个必读部分、31 个显示章节**；另有 CNN→ViT 和联想记忆两组选读，第九部分联想记忆由七个维护文件组成四个显示章节。
- 书末 **A–E 附录**：公式与数学、迁移练习、术语与索引、集中答案、参考资料；`book/main.tex` 当前读取 **55 个物理源码文件**，不等于显示章节数。
- 教学动机按“前一方法缺口→新方法→计算→限制”组织，标量学习先于向量矩阵。数值主线以 `scripts/teaching_reference.py` 为唯一可复算基线：`[1,3,4] → [3,4,2]`，独立三维 Q/K/V、因果 Mask、完整 Pre-Norm Block、三位置联合梯度；一次更新使平均损失 **1.7984303789 → 1.6113771577**。双头例独立使用四维，不混用参数。
- 模型应用部分区分预训练/Few-shot、SFT/偏好、检索、工具、Agent、MCP/A2A、部署与架构判断。ViT 有 Patch 手算，联想记忆说明行／列向量的转置关系；迁移题及答案已对应。
- 出版候选相对 [v0.1.0](https://github.com/CoCoThink/ai-by-intuition/releases/tag/v0.1.0) 的上述变化是**候选版变更说明**；真实发行时从此摘要编写 Release 文案，不另维护易过期的发布说明草稿。

## 技术验收证据（限定到具体源码）

| 检查 | 验证结果 |
|---|---|
| [完整 PDF 构建 #39777688357](https://github.com/CoCoThink/ai-by-intuition/actions/runs/39777688357) | 源码 `b352e833`；**110 页** Tagged PDF；结构/数字/排版检查通过 |
| 公式与无障碍 | **1,589/1,589** 个 Formula 有 MathML-AF；veraPDF **PDF/UA-2 零失败** |
| 图表结构 | 23 张表（65 个 TH）；17 幅图（17 个 Alt），44 个 H1 与 182 个 H2 |
| PDF 实际导航 | **422** 条内部 GoTo 全部可解析、31 条外部 URI、1,078 个命名目标 |
| 同次构建 PDF SHA-256 | `7541c309edb63c3009c67ce6293caece4b394680d308194b4e57c573e9ea27db` |
| Markdown／工作流 CI | [#39778266724](https://github.com/CoCoThink/ai-by-intuition/actions/runs/39778266724) 已通过；本次清理另行验证 |

以上为已核验候选快照，**不是**历史 v0.1.0 的 99 页／1,472 个公式。机器通过不等于所有阅读器的人工无障碍体验认证，也不代替对内容事实的编辑审查。

先前目视抽查覆盖封面、目录、损失、Embedding、Attention、完整 Transformer、Agent、ViT、术语、练习、参考资料等代表页面；发现的 ViT 小结孤页已通过精简正文修复，PDF 从 111 页收敛到 110 页。此为**抽样**而非宣称逐页、逐公式的人工专家校对。

## 尚未完成：出版门槛

- [x] 七部分／31 章主线、两组选读、A–E 附录与数值主线已入书。
- [x] 来源提交 `b352e833` 已通过完整 Tagged PDF、MathML-AF、PDF/UA-2 和 PDF 导航机器验收。
- [ ] 作者对重要公式、中文叙事、出版版式与可访问阅读路径进行**最终签核**。
- [ ] 明确新版版本号（例如 `v0.2.0`，**尚未选定**）和最后一个成功 `main` 构建 ID；必要时按正式发布流程重新运行完整 CI。
- [ ] **人工触发** [发布工作流](../.github/workflows/publish-release.yml)，校验资产 `AI-by-Intuition-Book.pdf`、`SHA256SUMS`、`build-audit.zip`。禁止覆盖旧 `v0.1.0`。

具体执行步骤在 [PUBLISHING.md](PUBLISHING.md)；验证规范在 [ACCESSIBILITY.md](ACCESSIBILITY.md) 与 [BUILD-REPRODUCIBILITY.md](BUILD-REPRODUCIBILITY.md)。

## 历史过程材料：Git 历史保留，不再作为当前入口

重构期间的 M0–M6 勾选日志、47 文件迁移表、原始 31 章先修草案、旧交接记录和独立的发布说明草稿已完成其阶段用途；为避免与当前教材和发布门槛产生冲突，不再留在主分支的活动文档列表。**原文可通过固定提交检索，未抹除版本历史：**

- [重构实施计划及 M0–M6 日志](https://github.com/CoCoThink/ai-by-intuition/blob/27a1ee5cc16353ef4568e2af47b4c499bc9a0fab/docs/STRUCTURE_REDESIGN_PLAN.md)
- [47 个历史源码的迁移台账](https://github.com/CoCoThink/ai-by-intuition/blob/27a1ee5cc16353ef4568e2af47b4c499bc9a0fab/docs/RESTRUCTURING_BASELINE.md) 与 [先修依赖草案](https://github.com/CoCoThink/ai-by-intuition/blob/27a1ee5cc16353ef4568e2af47b4c499bc9a0fab/docs/CURRICULUM_DEPENDENCIES.md)
- [历史交接记录](https://github.com/CoCoThink/ai-by-intuition/blob/27a1ee5cc16353ef4568e2af47b4c499bc9a0fab/docs/HANDOVER.md) 与 [发布说明草稿](https://github.com/CoCoThink/ai-by-intuition/blob/27a1ee5cc16353ef4568e2af47b4c499bc9a0fab/docs/V2_RELEASE_NOTES_DRAFT.md)

需要追溯教学动机时仍可读 [原始评审](REVIEW.md) 和 [文字稿](从函数到Transformer再到大模型_文字稿.md)；它们是**研究参考材料**，不是新的待办或发布状态来源。
