# Tagged PDF 无障碍现状与验收清单

**状态更新：2026-10-21。** 本文记录已经由 CI 复现的事实、尚未通过的项目，以及贡献者如何验证。这里的 `Tagged: yes` 是**技术构建状态**，不是 PDF/UA 合规证明。

## 已确认的构建结果

- 使用 **TeX Live 2026 + LuaLaTeX**；`book/main.tex` 的入口为 `\\DocumentMetadata{lang=zh-CN,tagging=on}`。
- [成功的 GitHub Actions 运行](https://github.com/CoCoThink/ai-by-intuition/actions/runs/39596178812) 生成 **99 页** `AI-by-Intuition-Volume-01.pdf`；正式下载工件为 `ai-by-intuition-volume-01`。
- 最小样例（中文、数学、`tabularx`、带替代文字的 TikZ）和整本书均可编译；CI 容器的 `pdfinfo` 显示 `Tagged: yes`。
- 验收器使用固定版 `pypdf==5.9.0`，确认 PDF Catalog 中 `/MarkInfo` 的 `/Marked=true`、`/StructTreeRoot` 和 `/Document` 结构根。最新统计为 **48 个 H1、180 个 H2、21 个 Table、59 个 TH、1,471 个 Formula、16 个 Figure、16 个带替代文字的节点**。
- `scripts/validate_book.py` 还检查七个部分、47 个章节输入文件、数值算例、目录页、目标内容、可疑空页以及全书文字边界。

这些计数是**该次成功构建的快照**；以后修改文稿、引擎和标签选项，需重新核验。

## 已知风险与待办

| 项目 | 当前情况 | 下一步验收 |
|---|---|---|
| 文档结构标签与标题 | **已修复并合并 `main`**：正文包含 48 个 H1、180 个 H2，保留中文章节显示与目录；见 [成功的构建](https://github.com/CoCoThink/ai-by-intuition/actions/runs/39596178812) | 持续检查标题层级和辅助技术的真实导航体验（[#3](https://github.com/CoCoThink/ai-by-intuition/issues/3)） |
| 图形替代文本 | 16 个主要图形结构有替代描述 | 检查信息完整度及与可视图对应关系 |
| 表格无障碍 | 21 张教学数据表均设置首行 `TH`，最近 CI 验证 59 个表头节点 | 检查表头 `TH` / 行列关联、跨行跨列与实际朗读 |
| 数学语义 | 结构树含 Formula 节点 | 经典字体的 `main` 构建稳定；`align`/`align*` 的 LuaMML 断言可通过改为 `aligned` 避开，但实验全书的 `mathml-SE` 方案仍报告非法 MathML 父子结构，正在 `experiment/full-book-mathml` 分支测试 `mathml-AF`；不能将 Formula 节点等同于 MathML |
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

[成功的 CI（正式出版不受影响）](https://github.com/CoCoThink/ai-by-intuition/actions/runs/39583710518) 证实 `smoke-mathml.tex` 在 `\\end{align*}` 复现 `luamml-amsmath.lua:63: assertion failed`。这是独立精简文件中的错误，不再假定来自整书排版；`smoke-mathml-aligned.tex` 继续验证 `\\[\\begin{aligned}...\\end{aligned}\\]` 变体。这些实验均不会阻断稳定成书，日志作为 `experimental-mathml-logs` 工件保存。

## 标题语义修复（已通过 main 分支 CI）

此前 99 页 PDF 虽有目录，却缺少正文 H1/H2。根因是 `titlesec` 的标题命令覆盖使语义结构丢失，而不是中文字体本身。实验分支移除 `titlesec`，改用 `\\ctexset` 配合 `\\EditInstance{heading}{section/subsection}` 的原生标题模板，并保留“第 X 部分／第 X 章／附录”等视觉编号。[main CI #39596178812](https://github.com/CoCoThink/ai-by-intuition/actions/runs/39596178812) 的**全书**结构检查确认 **48 个 H1、180 个 H2**，99 页、21 张语义表格与全部图形均通过。该改动已并入 `main`，并由 `scripts/validate_book.py` 强制检查 H1/H2 数量。

注意：H1/H2 存在并不等于阅读顺序正确，更不能代表 PDF/UA 已通过。下一步仍需检查标题嵌套、目录与实际读屏导航，并独立跑 PDF/UA 验证器。上游兼容性分析：[latex3/tagging-project #673](https://github.com/latex3/tagging-project/issues/673)。问题跟踪：[Issue #3](https://github.com/CoCoThink/ai-by-intuition/issues/3)。

## 独立标题结构标签实验（2026-10-21）

CI 增加两份不阻断正式出版的测试：`smoke-heading-article.tex`（标准 `article` 基线）与 `smoke-heading-chinese.tex`（`article + ctex[heading=false]` 中文组合）。`scripts/inspect_heading_tags.py` 遍历真实 PDF 结构树，核查 H1/H2 或 section/subsection 节点，而不是仅看目录或 RoleMap。结果归档在 `experimental-heading-results` 工件中。`main` 已直接采用经过完整 CI 验证的 `ctexart` 原生标题模板方案，无需为了此问题切换到 `article` 文档类；这些独立实验保留作为回归对照。

## 数学字体替代方案实验（2026-10-21）

新增非阻断 `book/smoke-mathml-lua-unicode.tex`，将传统 `unicode-math` 换成 TeX Live 2026 支持的 `lua-unicode-math`，保留同一段 `align*` 点积公式，比较是否能够生成 MathML 而不触发 LuaMML 断言。CI #39596178812 已证明该方案仍在 `align*` 触发 `luamml-amsmath.lua:63` 断言；不要误以为改用 `lua-unicode-math` 可以单独修复问题。

## 全书 MathML 可行性分支

实验分支 [`experiment/full-book-mathml`](https://github.com/CoCoThink/ai-by-intuition/tree/experiment/full-book-mathml) 已将所有触发断言的 `align`／`align*` 推导转换为 `aligned`，对需要编号的展示公式使用 `equation` 包裹；原先 LuaMML 的致命断言不再触发，CI #39598374009 能输出 99 页实验 PDF，但 `mathml-SE` 结构产生 **56 条 `mathml:mo → mathml:math` 父子关系警告**，因此**并未通过无障碍验收**。随后单独测试 `mathml-AF` 关联文件输出，不阻断 `main` 的稳定发布。只有检查公式的实际关联文件、结构规范性、版面和辅助技术读序后才考虑合并。

## 独立 PDF/UA-2 机器验收

在稳定的 99 页发布工作流中新增非阻断审计：固定 `verapdf/cli:v1.30.2`，使用 `--flavour ua2` 检查实际 PDF，并上传 `pdfua2-machine-audit` XML 工件。机器报告通过 `scripts/summarize_verapdf.py` 输出失败规则和数量，便于逐项修复。该检查**不替代**人工校对及实际读屏测试，且在消除全部机器规则告警前不会宣称 PDF/UA-2 合规。工具参见 [veraPDF CLI 官方说明](https://docs.verapdf.org/cli/validation/)。
