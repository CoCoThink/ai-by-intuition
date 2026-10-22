# AI by Intuition · V2 候选发布前验收

> **状态：内容修订 P0–P2 已合入 `main`；正式版本尚未签核或发布。**
> 最终候选 PDF 必须由同一个 `main` 提交的完整成功构建和两个原始审计工件证明，不复用历史版统计。

## 版本与构建证据

| 项目 | 当前事实与可核查证据 |
| --- | --- |
| 正式历史版本 | [v0.1.0 Release](https://github.com/CoCoThink/ai-by-intuition/releases/tag/v0.1.0)，历史工件保留，不覆盖 |
| P0 修订 | [PR #12](https://github.com/CoCoThink/ai-by-intuition/pull/12) 已合入 `main` |
| P1 / P2 内容 | [P1 完成记录](P1_COMPLETION.md)、[P2 完成记录](P2_COMPLETION.md)，均已直接合入 `main` |
| 已签核候选的机器构建 | **教材源码 SHA `2cad92cdca4fa9f9bf773015afb4195b143cc842`**；[Build one PDF book #39816203928](https://github.com/CoCoThink/ai-by-intuition/actions/runs/39816203928)，全部 CI 步骤成功，PDF 与机器审计两份工件均已上传（*机器通过不代表作者签核*） |
| 该次 PDF 统计 | **126 页**、Tagged PDF 2.0；MathML-AF **1,836 / 1,836**，独立 MathML 文档 1,128 |
| 该次 veraPDF | **PDF/UA-2 compliant**；`passedRules=1727`、`failedRules=0`、`passedChecks=949653`、`failedChecks=0`，veraPDF 1.30.2 |
| 本次视觉抽查 | 已查看封面、阅读路线、目录、原论文结构对照、生态表、技术争议、正文技术回顾与参考文献；最终 **125–126 页**已渲染复核，不再有孤立的第 127 页 |
| 视觉修复 | [`2cad92cd`](https://github.com/CoCoThink/ai-by-intuition/commit/2cad92cdca4fa9f9bf773015afb4195b143cc842) 删去导致参考文献孤页的重复总结；**其 PDF 构建已通过并经末两页目视核对** |
| 最新候选代码提交 | `2cad92cdca4fa9f9bf773015afb4195b143cc842`（最后一次改变 `book/` 的提交）；后续仅更新发布说明/验收记录，不影响选定源码 |
| 最终候选 CI | [Build one PDF book #39816203928](https://github.com/CoCoThink/ai-by-intuition/actions/runs/39816203928)，**success**；工件为 `ai-by-intuition-book` 与 `pdfua2-machine-audit` |
| 建议发行版本 | `v0.2.0`，**仅建议，尚未获得作者确认**；见 [发行说明草稿](V2_RELEASE_NOTES_DRAFT.md) |
| 作者签核 / 正式 Release | **尚未完成 / 尚未创建** |

### 机器验收与人工验收的区分

候选源码提交 `2cad92cd` 的 [完整 CI #39816203928](https://github.com/CoCoThink/ai-by-intuition/actions/runs/39816203928) 已成功。已下载并解析**同次构建**的两份工件，确认 126 页 PDF、1,836 个有效 MathML-AF 关联，以及 veraPDF 1.30.2 对 PDF/UA-2 的 `isCompliant=true` 和零失败规则/检查。该构建使用 TeX Live 2026 + LuaHBTeX 1.24.0。
最后两页已经渲染核查：参考文献从第 125 页延续至第 126 页，原先第 127 页的孤立总结不再存在。

人工视觉抽查覆盖代表性页面而非逐页全文校对；机器 PDF/UA-2 合规也不等于完成真实屏幕阅读器用户体验测试。

## 发布阻断项

- [x] P0/P1/P2 主要文本、概念首次定义、术语索引和练习/答案编号修改已经合入主分支。
- [x] 最终教材源码 `2cad92cd` 的完整主分支构建通过章节、数值、PDF 排版与标签、MathML-AF、PDF/UA-2 全部机器规则，证据为 [#39816203928](https://github.com/CoCoThink/ai-by-intuition/actions/runs/39816203928)。
- [x] 已对关键 P2 页面进行代表性视觉抽查，发现的参考文献末页孤立段落已在源码中修复。
- [x] 新的发行说明、勘误入口、Notebook 与官方资料链接已准备。
- [x] 已核对 `2cad92cd` 的同次完整构建、126 页 PDF、1,836 个公式 MathML-AF 关联、veraPDF XML 与两份工件。
- [x] 已渲染检查最终 PDF 末两页（第 125–126 页）和目录前后，原参考文献孤页已解决；其他代表性 P2 页面见上面的抽查范围。
- [ ] 作者确认新版本名称、发行内容、剩余风险与最终签核。
- [ ] 通过 `workflow_dispatch` 手动执行正式 [Publish validated book](../.github/workflows/publish-release.yml)，填写选定的成功构建 run ID；不复用旧版本标签。

## 正式签核记录（作者/维护者填写）

- **候选版本号：**待确认，建议 `v0.2.0`
- **最终选定的主分支教材提交 SHA：**`2cad92cdca4fa9f9bf773015afb4195b143cc842`
- **Build one PDF book 运行 ID / URL：**[#39816203928](https://github.com/CoCoThink/ai-by-intuition/actions/runs/39816203928)
- **PDF 页数 / 公式关联 / veraPDF 结果：**126 页；1,836/1,836 MathML-AF；PDF/UA-2 compliant，失败规则和检查数均为 0
- **PDF 与机器审计工件：**同次 CI 的 `ai-by-intuition-book` 与 `pdfua2-machine-audit`
- **最终目视检查记录：**2026-10-23 已由 AI 辅助抽查指定关键页面与末两页，未发现此前的孤立尾页；正式作者目视签核仍待填写
- **作者签核及日期：**尚未签核
- **遗留问题、是否阻断发布：**机器与抽查阶段无已知阻断项；版本确认及作者签核仍属发布前必要审批
- **正式 Release：**尚未创建

操作顺序及权限边界见 [出版流程](PUBLISHING.md)。机器无障碍声明见 [ACCESSIBILITY.md](ACCESSIBILITY.md)，构建环境与复现性见 [BUILD-REPRODUCIBILITY.md](BUILD-REPRODUCIBILITY.md)。
