# 参与改进 AI by Intuition

目标是让没有系统学过高等数学的读者，也能真正理解 AI 里的矩阵计算和推导，而不只是记住术语。

完整的编辑约定、生成内容入口和 CI 规则写在 [AGENTS.md](AGENTS.md)，人和编码助手共用。本页只列最常用的部分。

## 写作原则

- **先结论与直觉，再小数值例子，最后推广为公式。**交代输入、输出、形状，以及哪些参数参与训练。
- **同一组数据贯穿推导。**三维主例的参数只取自 [teaching_reference.py](scripts/teaching_reference.py)；二维、四维或其他局部例子用 `\localfixture` 标为“独立例”，不借用主线的词名和参数。
- **行向量约定：**每个 Token 占一行，投影写 `XW`；教学词表 ID、位置和矩阵行列从 1 起，Python 索引减 1。符号以[符号表](book/chapters/00c-symbols.tex)为准。
- **区分等式、近似、启发式解释与真实系统行为。**保留会改变结论的限制，合并重复提醒。
- **不写死章号、页码和题号。**用 `\ref`、`\pageref`、`\hyperref`；CI 会拦截“第 3 章”“第三章”“第 24.10 节”这类字面编号。
- 新增数学、术语或算法时给出可复算的检查；练习和答案保持一一对应。

## 修改流程

1. 正文在 `book/chapters/`，图在 `book/figures/`，章节顺序只由 [book/main.tex](book/main.tex) 的 `\input` 决定。
2. 题库、答案、章末导航、术语表、参考清单和附录 G 断言表都是**生成内容**：改源文件（如 `book/exercises.json`），再运行对应生成器。入口表见 [AGENTS.md](AGENTS.md#生成内容修改来源再运行生成器)。
3. 时效性断言（协议、API、模型配置）要查官方来源，同步正文、[dated-claims.json](book/dated-claims.json) 和 [source-audit.json](book/source-audit.json)；`checked_utc` 只在实际复核内容后更新。

## 提交前检查

源码检查（不需要 TeX）：

```bash
python3 scripts/generate_exercise_bank.py --check
python3 scripts/generate_chapter_navigation.py --check
python3 scripts/generate_bilingual_glossary.py --check
python3 scripts/check_book_contract.py --self-test
python3 scripts/check_source_hygiene.py --self-test
python3 scripts/validate_book.py
python3 scripts/check_teaching_claims.py
python3 scripts/check_chapter_crossrefs.py
python3 scripts/check_part_references.py
```

改动影响排版时，构建并检查成品：

```bash
bash scripts/build_book.sh
python3 scripts/validate_book.py --pdf book/build/main.pdf
python3 scripts/check_latex_references.py --log book/build/main.log --pdf book/build/main.pdf
python3 scripts/check_section_navigation.py --pdf book/build/main.pdf --aux book/build/main.aux
python3 scripts/validate_mathml_af.py book/build/main.pdf --minimum 1000
```

构建日志中不能出现 `Overfull \hbox`、缺字（`Missing character`）或 tagpdf 父子关系警告。veraPDF 的 PDF/UA-2 检查在 CI 中运行。图形或版式改动后，渲染相关页目视检查。

只改 Markdown 时运行 `python3 scripts/check_markdown_links.py` 和 `git diff --check` 即可；改工作流时另运行 `python3 scripts/check_workflows.py`。

不要提交 `book/build/`、编译 PDF、日志或 LaTeX 中间文件。不要为了通过 CI 关闭 `\DocumentMetadata`、结构标签或 MathML-AF，也不要降低检查阈值；能稳定识别的新错误，应补一条回归检查。

## Issue 与 PR

优先报告：哪一段看不懂、跳过了哪一步、哪个数字或形状不对。提交 PR 时说明改善了哪一种初学者困惑，附上手算核对步骤，并确认上面的检查通过。

## 贡献与许可

教材正文、LaTeX/TikZ、文档及正式 PDF 采用 [CC BY 4.0](LICENSE)；`scripts/` 与 `.github/workflows/` 采用 [MIT](scripts/LICENSE)，范围和建议署名见 [README](README.md#开放许可证与转载)。提交前请确认你有权按对应许可证贡献这些内容；引用第三方材料时标明来源和原始许可，未经授权的内容不要并入仓库。
