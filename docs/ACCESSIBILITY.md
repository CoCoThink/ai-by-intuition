# Tagged PDF 无障碍现状与验收清单

**状态更新：2026-10-21。** 本文记录已经由 CI 复现的事实、尚未通过的项目，以及贡献者如何验证。这里的 `Tagged: yes` 是**技术构建状态**，不是 PDF/UA 合规证明。

## 已确认的构建结果

- 使用 **TeX Live 2026 + LuaLaTeX**；`book/main.tex` 的入口为 `\\DocumentMetadata{lang=zh-CN,tagging=on}`。
- [成功的 GitHub Actions 运行](https://github.com/CoCoThink/ai-by-intuition/actions/runs/39575409381) 生成 **99 页** `AI-by-Intuition-Volume-01.pdf`；正式下载工件为 `ai-by-intuition-volume-01`。
- 最小样例（中文、数学、`tabularx`、带替代文字的 TikZ）和整本书均可编译；CI 容器的 `pdfinfo` 显示 `Tagged: yes`。
- 验收器使用固定版 `pypdf==5.9.0`，确认 PDF Catalog 中 `/MarkInfo` 的 `/Marked=true`、`/StructTreeRoot` 和 `/Document` 结构根。最新统计为 **1,471** 个 `/Formula`、**16** 个 `/Figure`、**16** 个带替代文字的节点。
- `scripts/validate_book.py` 还检查七个部分、47 个章节输入文件、数值算例、目录页、目标内容、可疑空页以及全书文字边界。

这些计数是**该次成功构建的快照**；以后修改文稿、引擎和标签选项，需重新核验。

## 已知风险与待办

| 项目 | 当前情况 | 下一步验收 |
|---|---|---|
| 文档结构标签与标题 | 已有 Document 根和正文结构，但逐节点核验**没有发现 H1/H2 或 section/subsection 标记**，正文标题导航不合格（[#3](https://github.com/CoCoThink/ai-by-intuition/issues/3)） | 在实验分支验证替代 ctexart/titlesec 的标题实现，再核验语义和版式 |
| 图形替代文本 | 16 个主要图形结构有替代描述 | 检查信息完整度及与可视图对应关系 |
| 表格无障碍 | 21 张教学数据表均设置首行 `TH`，最近 CI 验证 59 个表头节点 | 检查表头 `TH` / 行列关联、跨行跨列与实际朗读 |
| 数学语义 | 结构树含 Formula 节点 | 完整启用 `unicode-math` 曾在 `align*` 触发 `luamml-amsmath.lua` 断言；保留经典数学字体的稳定出版配置，通过 `book/smoke-mathml.tex` 独立实验，不得将 Formula 节点等同于 MathML |
| 图注结构 | 能生成 PDF | 最新完整构建无 Document 到 Caption 非法父子警告；仍应核验图注及链接锚点 |
| 读屏顺序 | 尚无端到端辅助技术验收记录 | 用至少一种主流 PDF 阅读器／读屏器检查目录、表格、公式和跨页提示框 |
| PDF/UA 标准 | **尚未认证** | 使用独立 PDF/UA 验证器并修复报告中的结构、语言、字体或注释问题 |

> **不要**把 Formula 节点数量等同于 MathML 可用性，也不要把 `Tagged: yes` 等同于 PDF/UA 合规。

## 在本地复现 CI

环境：TeX Live **2026**、LuaLaTeX、`latexmk`、Noto Serif / Sans（包括 CJK SC）、TikZ/PGF、`poppler-utils`、Python 3 及 `pypdf==5.9.0`。

从仓库根目录：

```bash
python3 scripts/validate_book.py
cd book
mkdir -p build/smoke
latexmk -lualatex -interaction=nonstopmode -halt-on-error -file-line-error -outdir=build/smoke smoke-tagging.tex
pdfinfo build/smoke/smoke-tagging.pdf | grep '^Tagged:'
latexmk -lualatex -interaction=nonstopmode -halt-on-error -file-line-error -outdir=build main.tex
cd ..
python3 -m pip install pypdf==5.9.0
python3 scripts/validate_book.py --pdf book/build/main.pdf
```

最小样例的 PDF 检查属于烟雾测试；正式验收必须以**整本书**为对象。当前代码对旧版 `pdfinfo` 的状态差异只打印警告，实际阻断依据是 PDF 内部结构。

## 维护规则

1. 更改 `DocumentMetadata`、文档类、`caption`、`tabularx`、`tcolorbox` 或 TikZ 标签后，先运行最小样例，再完整编译。
2. 每新增语义图，补充与视觉传达信息等价的替代文字，并实际检查标题/图注的阅读顺序。
3. 不得为追求无警告而直接删除公式、隐藏标签或放宽关键 PDF 结构校验。
4. 修复 PDF/UA 的每一项告警时记录其来源、复现页面、生成前后的结构差异及辅助技术结果。
5. PDF 工件从 Actions 获取，不把编译文件或中间文件提交到 Git。

相关入口：[仓库说明](../README.md) · [阅读顺序](../book/README.md) · [教学与工程规划](../ROADMAP.md) · [贡献指南](../CONTRIBUTING.md)。

## 2026-10-21 后续结构回归

- [成功的表格/图注/版面修复 CI](https://github.com/CoCoThink/ai-by-intuition/actions/runs/39581822953) 验证了 **21 张数据表**、**59 个 TH 表头单元格**、**16 张语义图形及其中文替代文字**；所有页均无文字越界，编译日志不再有非法图注父子关系或溢出盒子警告。
- 现在在 `scripts/validate_book.py` 检查每张表的首行 TH 结构和 Figure→Caption 层级，并在 CI 检查编译日志，防止后续回归。
- `book/smoke-mathml.tex` 用同一段点积推导复现潜在 LuaMML 断言；该测试**允许失败**且不能用来证明 PDF/UA 合规。正式教材仍优先稳定生成 Tagged PDF。

## LuaMML 对齐公式复现实验

[成功的 CI（正式出版不受影响）](https://github.com/CoCoThink/ai-by-intuition/actions/runs/39583710518) 证实 `smoke-mathml.tex` 在 `\\end{align*}` 复现 `luamml-amsmath.lua:63: assertion failed`。这是独立精简文件中的错误，不再假定来自整书排版；`smoke-mathml-aligned.tex` 继续验证 `\\[\\begin{aligned}...\\end{aligned}\\]` 变体。两项实验均不会阻断稳定成书，日志作为 `experimental-mathml-logs` 工件保存。

## 已确认的标题标签缺口（高优先级）

直接遍历 [99 页成功构建](https://github.com/CoCoThink/ai-by-intuition/actions/runs/39581822953) 的 PDF 结构树，发现 `/Sect` 分组与正常目录的 `/TOCI`，但没有生成正文的 `/H1`、`/H2` 或预期的 `/section`、`/subsection` 角色。结构树 `RoleMap` 尽管包含 `/section → /H1` 映射，仍没有实际节点使用它。这个问题会影响读屏器标题导航，**不能因 Tagged: yes 而忽略**。

上游已确认 [ctex 相关类重写标题命令导致标题标签丢失](https://github.com/latex3/tagging-project/issues/673)，[titlesec 当前也标记为 Tagged PDF 不兼容](https://www.ctan.org/pkg/titlesec)。因此不能只删除 `titlesec` 就假定问题解决。下一步在实验分支验证 `article + ctex(heading=false)` 与 LaTeX 2026 标题模板接口，并同时保持中文排版、章节编号、目录和页面版式。问题跟踪：[仓库 Issue #3](https://github.com/CoCoThink/ai-by-intuition/issues/3)。
