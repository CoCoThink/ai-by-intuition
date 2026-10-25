# 正式发布流程

CI 成功不等于发布。主分支的构建只产生草稿工件；正式版本由维护者签核后手动运行发布工作流，生成不可覆盖的 Release。已发布的 [v0.1.0](https://github.com/CoCoThink/ai-by-intuition/releases/tag/v0.1.0) 保持原样，修订一律用新版本号。

## 发布前签核

对拟发布的那一次构建逐项确认，并在发布说明或 Issue 中留下记录（提交号、CI 运行号、负责人、日期）：

1. **选定构建：**`main` 分支上一次成功的 [Build one PDF book](../.github/workflows/build-latex.yml)，同时具备 `ai-by-intuition-book` 与 `pdfua2-machine-audit` 两份工件。PR 上的绿灯不能替代。
2. **机器检查：**源码与数值检查、成品排版检查、全部公式 MathML 关联、veraPDF PDF/UA-2 零失败。
3. **人工校样：**按 [维护手册](MAINTENANCE.md#灰度与人工校样)用同一份 PDF 生成灰度校样并逐页审阅；重点看新改动的算例、图表和分页。
4. **来源与授权：**
   - 讲解路径受飞天闪客两部公开课程启发（[从函数到 Transformer](https://www.bilibili.com/video/BV1NCgVzoEG9/)、[从 Transformer 到大模型](https://www.bilibili.com/video/BV15z4C6SEHT/)），课程页面注明未经授权禁止转载。致谢不能代替授权：发布前需对照原课程，确认助手与 Agent 各章（以及其他借鉴了讲解顺序的章节）没有沿用受保护的具体表达、图示或例子；有疑问的段落重写，或取得书面授权并记录条件。
   - 联想记忆部分借鉴 Alex Wang 文章的讲解框架，署名与链接集中在附录 F；核对没有复制原文文字或图片。
   - 引用的模型配置、JSON 片段和第三方图示，核对其使用条款；能在网上查看不等于可以再出版。
5. **带日期断言：**附录 G 中没有到期或落后于官方新修订的条目（`python3 scripts/check_dated_claims.py --self-test --online --check-due`）。
6. **版本信息：**确定新的语义化版本号，写好发布说明，并核对封面、版权页与附录 G 中的版本与提交号。

## 运行发布工作流

在 GitHub Actions 中选择 [Publish validated book](../.github/workflows/publish-release.yml)，从 `main` 手动运行，填写：

- `version`：尚不存在的新版本号，如 `v0.2.0`；
- `build_run_id`：第 1 步选定的成功运行编号。

工作流会拒绝：已存在的标签或 Release；不属于本仓库、未成功或不在 `main` 上的构建；构建提交之后 `main` 又改动了 `book/`、`scripts/` 或构建工作流却没有重新构建的情况。

通过后，它直接下载该次构建的 PDF 与机器审计，复核页数、MathML 关联、veraPDF 结果和环境记录，再创建 Release，附件为：

- `AI-by-Intuition-Book.pdf`
- `SHA256SUMS`
- `build-audit.zip`

Release 说明会标明源码提交和原始构建。发布后在 [CHANGELOG](../CHANGELOG.md) 中把草稿条目改为正式版本号与日期。
