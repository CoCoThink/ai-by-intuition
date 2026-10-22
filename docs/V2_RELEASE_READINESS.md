# AI by Intuition · V2 候选发布前验收

> **状态：内容修订 P0–P2 已合入 `main`；正式版本尚未签核或发布。**
> 最终候选 PDF 必须由同一个 `main` 提交的完整成功构建和两个原始审计工件证明，不复用历史版统计。

## 版本与构建证据

| 项目 | 当前事实与可核查证据 |
| --- | --- |
| 正式历史版本 | [v0.1.0 Release](https://github.com/CoCoThink/ai-by-intuition/releases/tag/v0.1.0)，历史工件保留，不覆盖 |
| P0 修订 | [PR #12](https://github.com/CoCoThink/ai-by-intuition/pull/12) 已合入 `main` |
| P1 / P2 内容 | [P1 完成记录](P1_COMPLETION.md)、[P2 完成记录](P2_COMPLETION.md)，均已直接合入 `main` |
| 已验证的 P2 完整构建 | `29590d6ea5e5d095f4eccd897be3132b60e95722`；[Build one PDF book #39813979873](https://github.com/CoCoThink/ai-by-intuition/actions/runs/39813979873)；所有步骤成功，产出 PDF 与机器审计两个工件 |
| 该次 PDF 统计 | **127 页**、Tagged PDF 2.0；MathML-AF **1,836 / 1,836**，独立 MathML 文档 1,128 |
| 该次 veraPDF | **PDF/UA-2 compliant**；`passedRules=1727`、`failedRules=0`、`failedChecks=0`，veraPDF 1.30.2 |
| 该次人工视觉抽查 | 已查看封面、阅读路线、目录、原论文结构对照、生态表、技术争议、正文技术回顾和最后参考文献页；发现尾页仅有一段冗余总结 |
| 视觉修复 | [`2cad92cd`](https://github.com/CoCoThink/ai-by-intuition/commit/2cad92cdca4fa9f9bf773015afb4195b143cc842) 删去导致参考文献孤页的重复总结；**需单独完成对应提交的 PDF 验证** |
| 最新候选代码提交 | `2cad92cdca4fa9f9bf773015afb4195b143cc842`（最后一次改变 `book/` 的提交）；后续仅更新发布说明/验收记录，不影响选定源码 |
| 最新候选 CI | [Build one PDF book #39816203928](https://github.com/CoCoThink/ai-by-intuition/actions/runs/39816203928)，**待确认最终结论与产出** |
| 建议发行版本 | `v0.2.0`，**仅建议，尚未获得作者确认**；见 [发行说明草稿](V2_RELEASE_NOTES_DRAFT.md) |
| 作者签核 / 正式 Release | **尚未完成 / 尚未创建** |

### 机器验收与人工验收的区分

已验证的 `29590d6e` 构建成功通过源码章节、数值参考、PDF 页面/标签、公式 MathML-AF、veraPDF PDF/UA-2 检查，并保留两份工作流工件。
上述事实**不自动继承**到之后改动过 `book/` 的提交。
特别是 `2cad92cd` 的最后一页修复，需以 [#39816203928](https://github.com/CoCoThink/ai-by-intuition/actions/runs/39816203928) 成功并提供同次工件为依据，才能更新最终发布证据。

人工视觉抽查覆盖代表性页面而非逐页全文校对；机器 PDF/UA-2 合规也不等于完成真实屏幕阅读器用户体验测试。

## 发布阻断项

- [x] P0/P1/P2 主要文本、概念首次定义、术语索引和练习/答案编号修改已经合入主分支。
- [x] 至少一次 P2 主分支完整构建通过章节、数值、PDF 排版与标签、MathML-AF、PDF/UA-2 全部机器规则，证据为 [#39813979873](https://github.com/CoCoThink/ai-by-intuition/actions/runs/39813979873)。
- [x] 已对关键 P2 页面进行代表性视觉抽查，发现的参考文献末页孤立段落已在源码中修复。
- [x] 新的发行说明、勘误入口、Notebook 与官方资料链接已准备。
- [ ] **最新教材源码提交 `2cad92cd` 的单次完整构建成功**，并确认 PDF 页数、公式 MathML-AF、veraPDF XML 和两个工件准确对应此 SHA。
- [ ] 抽查最终候选 PDF 末两页和目录前后，确保参考文献不再出现独占一页的冗余总结，也没有新出现的孤行。
- [ ] 作者确认新版本名称、发行内容、剩余风险与最终签核。
- [ ] 通过 `workflow_dispatch` 手动执行正式 [Publish validated book](../.github/workflows/publish-release.yml)，填写选定的成功构建 run ID；不复用旧版本标签。

## 正式签核记录（作者/维护者填写）

- **候选版本号：**待确认，建议 `v0.2.0`
- **最终选定的主分支提交 SHA：**待最新成功构建确认
- **Build one PDF book 运行 ID / URL：**待填写
- **PDF 页数 / 公式关联 / veraPDF 结果：**待从同次工件填写
- **PDF 与机器审计工件：**待填写
- **最终目视检查人、日期与结论：**待填写
- **作者签核及日期：**尚未签核
- **遗留问题、是否阻断发布：**待填写
- **正式 Release：**尚未创建

操作顺序及权限边界见 [出版流程](PUBLISHING.md)。机器无障碍声明见 [ACCESSIBILITY.md](ACCESSIBILITY.md)，构建环境与复现性见 [BUILD-REPRODUCIBILITY.md](BUILD-REPRODUCIBILITY.md)。
