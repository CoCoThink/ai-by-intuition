# Tagged PDF 无障碍现状与验收清单

**状态更新：2026-10-21。** 本文记录已经由 CI 复现的事实、尚未通过的项目，以及贡献者如何验证。这里的 `Tagged: yes` 是**技术构建状态**，不是 PDF/UA 合规证明。

## 已确认的构建结果

- 使用 **TeX Live 2026 + LuaLaTeX**；`book/main.tex` 的入口为 `\\DocumentMetadata{lang=zh-CN,tagging=on}`。
- [成功的 GitHub Actions 运行](https://github.com/CoCoThink/ai-by-intuition/actions/runs/39575409381) 生成 **99 页** `AI-by-Intuition-Volume-01.pdf`；正式下载工件为 `ai-by-intuition-volume-01`。
- 最小样例（中文、数学、`tabularx`、带替代文字的 TikZ）和整本书均可编译；CI 容器的 `pdfinfo` 显示 `Tagged: yes`。
- 验收器使用固定版 `pypdf==5.9.0`，确认 PDF Catalog 中 `/MarkInfo` 的 `/Marked=true`、`/StructTreeRoot` 和 `/Document` 结构根。最新统计为 **1,471** 个 `/Formula`、**17** 个 `/Figure`、**17** 个带替代文字的节点。
- `scripts/validate_book.py` 还检查七个部分、47 个章节输入文件、数值算例、目录页、目标内容、可疑空页以及全书文字边界。

这些计数是**该次成功构建的快照**；以后修改文稿、引擎和标签选项，需重新核验。

## 已知风险与待办

| 项目 | 当前情况 | 下一步验收 |
|---|---|---|
| 文档结构标签 | 已有真实结构树、Document 根及正文/公式/图像节点 | 审核各级标题和段落标签，检查跳转顺序 |
| 图形替代文本 | 17 处标签有替代描述 | 检查信息完整度及与可视图对应关系 |
| 表格无障碍 | `tabularx` 在 TeX Live 2026 上已能编译 | 检查表头 `TH` / 行列关联、跨行跨列与实际朗读 |
| 数学语义 | 结构树含 Formula 节点 | 最新 CI 有 `unicode-math` / `lua-unicode-math` 缺失时无法生成 MathML 的警告；应验证可用的 MathML 或可靠的辅助阅读方式 |
| 图注结构 | 能生成 PDF | `tagpdf` 仍出现 Document 到 Caption 的父子关系警告；应调整宏包交互并复核结构树 |
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
