# V2 候选：发布前验收与作者签核

> **状态：尚未正式发布；作者最终签核未记录。** 已正式发行的版本仍为 [v0.1.0](https://github.com/CoCoThink/ai-by-intuition/releases/tag/v0.1.0)。
> 本页作为 **V2 历史记录** 保留。当前 39 章源码已转入
> [V3 发布前验收](V3_RELEASE_READINESS.md)，请勿使用本页的历史数字或步骤作为当前版本的签核。

## 当前基线与修订分流

- V2 当时的候选采用七个必读部分、两个选读专题和 A–E 附录；该历史目录已不等于**当前** [book/main.tex](../book/main.tex) 的 V3 顺序。
- README 记录的**上一次完整成功候选构建证据**为源码 \`2cad92cd\`、[GitHub Actions #39816203928](https://github.com/CoCoThink/ai-by-intuition/actions/runs/39816203928)：126 页 Tagged PDF、1,836/1,836 MathML-AF 公式关联及 PDF/UA-2 compliant。**这些统计只适用于该次构建，不证明后续 main 修订通过。**
- 主分支已根据 [REVIEW.md](REVIEW.md) 完成 39 章、九部分与 A–G 附录的重排；特定提交的机器证据与剩余人工阻断项见 [V3_RELEASE_READINESS.md](V3_RELEASE_READINESS.md)，迁移详情见 [CHAPTER_MAPPING.md](CHAPTER_MAPPING.md)。

## 历史 V2 工作台（不用于签核当前 V3）

- [ ] 指定一个与拟发布源码对应的成功 [main 分支 PDF 完整构建](../.github/workflows/build-latex.yml)，记录完整 commit SHA 和运行编号。
- [ ] \`scripts/validate_book.py\` 的源码序列、数值核对、章节引用、目录、练习与答案检查通过。
- [ ] PDF 目录和书签连续、页面内容不越界；作者目视抽查重要算例、复杂图与表格的实际排版。
- [ ] 结构化标题、TH 表头、Figure 替代文字、MathML-AF 全量关联和 veraPDF PDF/UA-2 机器审计通过。
- [ ] 核对外部来源、文本复用授权、许可声明和参考资料。
- [ ] 记录作者最终签核、拟发版本号、发布日期与允许发布的准确 commit。

机器规则通过不代表已经对真实屏读体验做过人工无障碍验收；该项不是本项目现有发布流程的阻断门槛。

## 发布证据（每次候选需重填）

| 项目 | 目前记录 |
| --- | --- |
| 最近一次此前成功的候选构建 | [#39816203928](https://github.com/CoCoThink/ai-by-intuition/actions/runs/39816203928)（对应 \`2cad92cd\`，仅作历史基线） |
| 当前 main 候选构建 | [Build one PDF book](../.github/workflows/build-latex.yml)（以最新对应 SHA 的实际运行结果为准） |
| 出版签核 | **尚未签核** |
| 正式发布 | **尚未执行** |

## 发布程序

依据 [PUBLISHING.md](PUBLISHING.md)，仅由维护者对已成功的 main 构建进行人工签核，再运行手动发布工作流。不能覆盖 v0.1.0 PDF 或引用它的校验结果充当新版本质量证明。
