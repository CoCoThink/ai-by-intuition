# AI by Intuition · 正式发布流程

本仓库将“通过测试”和“正式出版”分开处理：PR 和主分支 CI 成功不会自动创建 Release。出版必须由维护者明确签核并手动启动发布工作流。

## 当前发行基线

- 已正式发行的归档版本为 [v0.1.0](https://github.com/CoCoThink/ai-by-intuition/releases/tag/v0.1.0)；保留其 PDF、校验和及审计工件，不覆盖原版本。
- 新版候选在 [V2 发布前验收](V2_RELEASE_READINESS.md) 持续记录；在签核和手动发布之前，不将候选的最新构建称为正式版。
- 教材源码的唯一编排入口为 [book/main.tex](../book/main.tex)，自动验收基于 [Build one PDF book](../.github/workflows/build-latex.yml)。

## 发布前的必要检查

1. 将所有教材、练习、术语索引、LaTeX 图形和验证规则的变更合入 \`main\`；确认不存在遗漏的待处理审稿阻断项。
2. 选择一次在 **\`main\` 分支**成功完成的 **Build one PDF book** 运行。PR 检查即便全绿，也不能代替这个发布来源。
3. 确认该次运行生成的 \`ai-by-intuition-book\` 与 \`pdfua2-machine-audit\` 两份工件：前者包含单册 PDF，后者包含公式 MathML-AF、veraPDF PDF/UA-2 和构建环境记录。
4. 确认源码/数值、PDF 排版与页面边界、图表结构和替代文字、全部公式 MathML-AF、PDF/UA-2 检查均通过；新增排版仍应进行作者目视核对。机器通过不等于已做真实读屏体验测试。
5. 作者或维护者完成版本内容和发行说明签核，并在 [V2 发布前验收](V2_RELEASE_READINESS.md) 记录所选提交、运行链接、阻断项结论。

## 手动发布步骤

在 GitHub Actions 选择 [Publish validated book](../.github/workflows/publish-release.yml)，从 \`main\` 手动执行 \`workflow_dispatch\`，填写：

- \`version\`：尚不存在的新语义化版本号，如 \`v0.2.0\`；
- \`build_run_id\`：已成功的 \`main\` 分支“Build one PDF book”运行编号。

发布工作流将拒绝重复的标签或 Release，以及不属于本仓库、未成功或不是 \`main\` 的源构建。选用构建的提交必须属于 \`main\` 历史；从该提交到发布时的 \`main\`，不得再次改动 \`book/\`、\`scripts/\` 或构建工作流而未重建。

工作流会直接下载**所选同一次构建**的 PDF 和机器审计，再核对 PDF 页数、MathML-AF 关联、veraPDF PDF/UA-2 零失败结果及运行环境记录。通过后才创建**不可覆盖**的带版本号 Release，包含：

- \`AI-by-Intuition-Book.pdf\`；
- \`SHA256SUMS\`；
- \`build-audit.zip\`。

Release 描述将标明对应的源码 SHA 和原始成功构建。需要修订已发布内容时应使用新版本号，而非替换历史工件。

## 相关资料

- [阅读顺序与构建说明](../book/README.md)
- [无障碍机器验收及边界](ACCESSIBILITY.md)
- [构建可复现性与环境审计](BUILD-REPRODUCIBILITY.md)
- [候选状态与作者签核](V2_RELEASE_READINESS.md)
