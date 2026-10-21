# Tagged PDF 机器验收状态

**状态更新：2026-10-21。** 项目将验收范围限定为可重复的机器验证：Tagged PDF 结构、MathML-AF 关联、自动化布局检查及 veraPDF 1.30.2 PDF/UA-2 规则。**不安排真实屏读体验或人工无障碍验收**，机器结果不代表具体辅助技术体验的保证。

## 已确认的构建结果

- 使用 **TeX Live 2026 + LuaLaTeX**；`book/main.tex` 的入口为 `\DocumentMetadata{lang=zh-CN,tagging=on,pdfstandard=ua-2,tagging-setup={math/setup=mathml-AF}}`。
- [成功的 GitHub Actions 运行](https://github.com/CoCoThink/ai-by-intuition/actions/runs/39609436412) 生成 **99 页** `AI-by-Intuition-Volume-01.pdf`；正式下载工件为 `ai-by-intuition-volume-01`。
- 最小样例（中文、数学、`tabularx`、带替代文字的 TikZ）和整本书均可编译；CI 容器的 `pdfinfo` 显示 `Tagged: yes`。
- 验收器使用固定版 `pypdf==5.9.0`，确认 PDF Catalog 中 `/MarkInfo` 的 `/Marked=true`、`/StructTreeRoot` 和 `/Document` 结构根。最新统计为 **48 个 H1、180 个 H2、21 个 Table、59 个 TH、1,472 个 Formula、16 个 Figure、16 个带替代文字的节点**。
- `scripts/validate_book.py` 还检查七个部分、47 个章节输入文件、数值算例、目录页、目标内容、可疑空页以及全书文字边界。

这些计数是**该次成功构建的快照**；以后修改文稿、引擎和标签选项，需重新核验。

## 已完成的机器验收与后续维护

| 检查范围 | 已验证结果 | 后续回归 |
|---|---|---|
| 标签与标题 | 48 个 H1、180 个 H2，中文目录与引用均保留（[Issue #3](https://github.com/CoCoThink/ai-by-intuition/issues/3) 已关闭） | 由 CI 检查结构节点、标题层级及链接 |
| 图形结构 | 16 个主要 Figure 节点，均有中文替代描述 | CI 检查 `/Alt` 与 `/Caption` 层级 |
| 数据表格 | 21 张数据表、59 个 TH 表头 | CI 验证首行 TH 与结构树，保持 PDF/UA-2 机器验证 |
| 数学语义 | 1,472 个 Formula 均关联可解析的 MathML-AF（933 份不同 MathML） | `scripts/validate_mathml_af.py` 保持公式关联与 XML 完整性检查 |
| PDF/UA-2 | veraPDF 1.30.2：1,727 项规则、736,481 项检查全部通过，失败 0 | CI 失败即阻断发布 |
| 页面排版 | 99 页，自动检查文字边界和溢出日志 | 保留版面与源码检查 |

**范围约定：**不维护真实屏读体验、辅助技术实测或人工无障碍验收任务。[原人工验收 Issue #4](https://github.com/CoCoThink/ai-by-intuition/issues/4) 已按项目范围调整关闭。机器检查的成功不能单独推断所有阅读器的实际表现。

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
4. 修复 PDF/UA 机器告警时记录验证器版本、规则 ID、复现页面、结构差异及回归测试结果。
5. PDF 工件从 Actions 获取，不把编译文件或中间文件提交到 Git。

相关入口：[仓库说明](../README.md) · [阅读顺序](../book/README.md) · [教学与工程规划](../ROADMAP.md) · [贡献指南](../CONTRIBUTING.md)。

## 2026-10-21 后续结构回归

- [成功的表格/图注/版面修复 CI](https://github.com/CoCoThink/ai-by-intuition/actions/runs/39581822953) 验证了 **21 张数据表**、**59 个 TH 表头单元格**、**16 张语义图形及其中文替代文字**；所有页均无文字越界，编译日志不再有非法图注父子关系或溢出盒子警告。
- 现在在 `scripts/validate_book.py` 检查每张表的首行 TH 结构和 Figure→Caption 层级，并在 CI 检查编译日志，防止后续回归。
- `book/smoke-mathml.tex` 用同一段点积推导复现潜在 LuaMML 断言；该测试**允许失败**且不能用来证明 PDF/UA 合规。正式教材仍优先稳定生成 Tagged PDF。

## LuaMML 对齐公式复现实验

[成功的 CI（正式出版不受影响）](https://github.com/CoCoThink/ai-by-intuition/actions/runs/39583710518) 证实 `smoke-mathml.tex` 在 `\\end{align*}` 复现 `luamml-amsmath.lua:63: assertion failed`。这是独立精简文件中的错误，不再假定来自整书排版；`smoke-mathml-aligned.tex` 继续验证 `\\[\\begin{aligned}...\\end{aligned}\\]` 变体。这些实验均不会阻断稳定成书，日志作为 `experimental-mathml-logs` 工件保存。

## 标题语义修复（已通过 main 分支 CI）

此前 99 页 PDF 虽有目录，却缺少正文 H1/H2。根因是 `titlesec` 的标题命令覆盖使语义结构丢失，而不是中文字体本身。实验分支移除 `titlesec`，改用 `\\ctexset` 配合 `\\EditInstance{heading}{section/subsection}` 的原生标题模板，并保留“第 X 部分／第 X 章／附录”等视觉编号。[main CI #39596178812](https://github.com/CoCoThink/ai-by-intuition/actions/runs/39609436412) 的**全书**结构检查确认 **48 个 H1、180 个 H2**，99 页、21 张语义表格与全部图形均通过。该改动已并入 `main`，并由 `scripts/validate_book.py` 强制检查 H1/H2 数量。

注意：H1/H2 存在不等于所有结构规则都正确；本项目已经通过独立 veraPDF PDF/UA-2 机器验证，持续由 CI 监测结构回归。上游兼容性分析：[latex3/tagging-project #673](https://github.com/latex3/tagging-project/issues/673)。问题跟踪：[Issue #3](https://github.com/CoCoThink/ai-by-intuition/issues/3)。

## 独立标题结构标签实验（2026-10-21）

CI 增加两份不阻断正式出版的测试：`smoke-heading-article.tex`（标准 `article` 基线）与 `smoke-heading-chinese.tex`（`article + ctex[heading=false]` 中文组合）。`scripts/inspect_heading_tags.py` 遍历真实 PDF 结构树，核查 H1/H2 或 section/subsection 节点，而不是仅看目录或 RoleMap。结果归档在 `experimental-heading-results` 工件中。`main` 已直接采用经过完整 CI 验证的 `ctexart` 原生标题模板方案，无需为了此问题切换到 `article` 文档类；这些独立实验保留作为回归对照。

## 数学字体替代方案实验（2026-10-21）

新增非阻断 `book/smoke-mathml-lua-unicode.tex`，将传统 `unicode-math` 换成 TeX Live 2026 支持的 `lua-unicode-math`，保留同一段 `align*` 点积公式，比较是否能够生成 MathML 而不触发 LuaMML 断言。CI #39596178812 已证明该方案仍在 `align*` 触发 `luamml-amsmath.lua:63` 断言；不要误以为改用 `lua-unicode-math` 可以单独修复问题。

## 全书 MathML 可行性分支

早期实验分支 [`experiment/full-book-mathml`](https://github.com/CoCoThink/ai-by-intuition/tree/experiment/full-book-mathml) 把引起 LuaMML 断言的 `align`／`align*` 改为 `aligned`，编号推导使用 `equation` 包裹。最初 `mathml-SE` 方案触发 56 条非法父子结构警告，**未获通过**；改用 `mathml-AF` 后，实验版实现 99 页正常构建、1,472 个有效公式关联、veraPDF 零失败。经过与最新版 `main` 合并的集成分支复测，修改已并入正式源码：[成功 CI #39613800415](https://github.com/CoCoThink/ai-by-intuition/actions/runs/39613800415)。真实屏读与人工无障碍验收不再列为项目待办，[Issue #4](https://github.com/CoCoThink/ai-by-intuition/issues/4) 已按范围调整关闭。

## PDF/UA-2 自动验收（已达到零失败）

[main CI #39609436412](https://github.com/CoCoThink/ai-by-intuition/actions/runs/39609436412) 的 99 页正式 PDF 经固定版本 **veraPDF 1.30.2**（`--flavour ua2`）验证：`isCompliant=true`，**1,727 项通过规则、736,481 项通过检查，0 失败规则、0 失败检查**。该结果仅针对验证器覆盖的机器规则，不是独立第三方认证；项目不计划辅助技术实测。

问题根因与修复如下：

1. 在 `\\DocumentMetadata` 中补充 `pdfstandard=ua-2`，生成 PDF/UA-2 标准识别 XMP 元数据。
2. 两张带长篇图解的复杂插图（RNN/Attention 路径、Key/Value 排布）曾将 `Caption` 留在 `Figure` 的中间位置。把图注放在图形上方，使其成为该标签的首子节点；其余教学图的图注仍按语义结构正常嵌套。
3. 调整后检查了第 34、39 页的可视布局：两张图标题与对应图解位于同页，未导致新的页面溢出，仍保持 **99 页**。

CI 的独立 veraPDF 规则已经由“仅报告”升级为**发布失败阻断**，XML 结果仍作为 `pdfua2-machine-audit` 工件上传。若验证器报告失败，`scripts/summarize_verapdf.py` 将返回非零状态，使正式发布失败。

**维护边界：**继续保障 MathML-AF、表格与标题结构和 PDF/UA-2 机器验证，不把真实屏读、人工判读或跨页朗读顺序列为发布任务；机器零失败不代表在所有软件中体验一致。

验证工具：[veraPDF CLI 官方文档](https://docs.verapdf.org/cli/validation/)。

## MathML-AF 正式集成（2026-10-21）

- [集成 CI #39613800415](https://github.com/CoCoThink/ai-by-intuition/actions/runs/39613800415) 在保留正式标题、图注、表格与 PDF/UA-2 门槛的基础上，成功生成 99 页含 MathML 的 PDF。
- `scripts/validate_mathml_af.py` 在发布前遍历所有公式结构节点，逐一检查 PDF 的 `/AF`、`/AFRelationship /Supplement`、嵌入的 MathML XML 及其根节点；**1,472/1,472** 全部通过，933 份不同 MathML 内容。任何公式缺失或损坏都会使 CI 失败。
- `book/main.tex` 使用 `unicode-math`、Latin Modern Math 与 `math/setup=mathml-AF`。源码中的多行公式由 `align`／`align*` 转成 `aligned` 组合，以绕开 TeX Live 2026 的 LuaMML 断言。
- 完整集成构建的 veraPDF 1.30.2 PDF/UA-2 为 `isCompliant=true`，零失败；完整文字边界检查和版面溢出检查也通过。机器验证结果仅声明结构、关联和规则层面的正确性，不对具体屏读效果作保证。
