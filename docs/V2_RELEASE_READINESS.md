# AI by Intuition · V2 候选发布前验收

> **状态（2026-10-22）：候选尚未签核、尚未发布。**已正式发布的仍是 [v0.1.0](https://github.com/CoCoThink/ai-by-intuition/releases/tag/v0.1.0)。本页只记录新版候选需要满足的发布条件，不继承旧版 PDF 的机器统计为新版结论。

## 版本与证据入口

| 项目 | 现有状态／应填写的发布证据 |
| --- | --- |
| 已发布基线 | [v0.1.0 正式 Release](https://github.com/CoCoThink/ai-by-intuition/releases/tag/v0.1.0)，历史工件保留 |
| 新版源码 | [main 分支](https://github.com/CoCoThink/ai-by-intuition/tree/main)；以最终合并提交为准 |
| 文本评审 P0 | [P0 修订 PR #12](https://github.com/CoCoThink/ai-by-intuition/pull/12)；合并后重新核对 |
| 候选主分支提交 SHA | **待记录**（在所有变更合并后填写） |
| 候选成功构建 run ID / URL | **待记录**（必须是与候选提交相符的主分支完整成功构建） |
| PDF 页数、图表与公式统计 | **待本次构建生成并核对**，不得复用旧版 99 页／1,472 公式的统计 |
| 作者最终签核 | **未完成** |
| 新版 Release | **尚未发布**，不得使用尚未验证的版本号冒充发行状态 |

## 发布阻断项

- [ ] P0 文本正确性、术语索引、练习/答案编号及数值主线的修改合并完成。
- [ ] 全书章节顺序、概念首次定义、所有交叉引用与附录答案经源码检查通过。
- [ ] 在所选主分支提交上，[完整 PDF 构建](../.github/workflows/build-latex.yml)成功。
- [ ] 三维贯通参考计算、全书文字边界、目录、表格和图形结构检查通过。
- [ ] 所有 PDF Formula 均有可解析的 MathML-AF，PDF/UA-2 veraPDF 报告为 compliant 且失败数为零。
- [ ] 新增图表有中文替代文字、必要表头和图注；作者完成关键页面的目视排版核对。
- [ ] 保存同一次构建的 PDF、机器审计、软件环境、源码 SHA 和构建 URL。
- [ ] 版本号及发行说明由作者签核，明确标出与历史版不同的教学范围。

以上项目必须以最终候选构建的真实结果更新；本页的复选框不代表已执行验证。项目无障碍范围仅涵盖机器可验证的 PDF 规则，不承诺已开展真实屏幕阅读器体验或人工无障碍验收。

## 记录模板（正式发布前填写）

- **候选版本：**待定
- **作者签核人和日期：**待填写
- **主分支提交 SHA：**待填写
- **Build one PDF book 运行链接：**待填写
- **PDF 页数与图表／MathML-AF 统计：**待填写
- **veraPDF PDF/UA-2 报告与失败数：**待填写
- **环境审计与 PDF 工件链接：**待填写
- **遗留非阻断项及处理决定：**待填写
- **正式 Release 链接：**发布完成后填写

正式版操作按 [出版流程](PUBLISHING.md) 执行；机器合规的含义和边界见 [ACCESSIBILITY.md](ACCESSIBILITY.md)，环境固定程度见 [BUILD-REPRODUCIBILITY.md](BUILD-REPRODUCIBILITY.md)。
