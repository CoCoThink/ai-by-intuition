# AI by Intuition — Handover / 遗留事项交接

> 交接快照：2026-10-21；基线 `main`：[`7c3e1f4`](https://github.com/CoCoThink/ai-by-intuition/commit/7c3e1f40c2b8bd26bc66b5725865c3033d9c730a)。最近一次已完成的全量 CI 对应源码提交 [`cc680b6`](https://github.com/CoCoThink/ai-by-intuition/commit/cc680b63425e)；[Actions #39615037750](https://github.com/CoCoThink/ai-by-intuition/actions/runs/39615037750) 为 **success**。后续只改过 Markdown 文档，不代表该文档提交又执行了全量 CI。

## 1. 一句话交接结论

**当前没有已知的发布阻断项（P0），也没有开放的 GitHub Issue。** 七部分教材已经稳定生成 99 页 Tagged PDF，整本书 MathML-AF 关联与 veraPDF PDF/UA-2 机器验证均通过。剩余事项主要是旧实验清理、自动化覆盖、构建复现性与内容/出版精校。请勿将先前修复的 MathML、标题结构、图注或 PDF/UA-2 机器验证重新标记为未完成。

项目验收范围以[无障碍说明](ACCESSIBILITY.md)为准：**只要求可重复的机器验证；不安排真实屏读体验或人工无障碍验收**。不得把该已明确排除的工作重新放入交付阻断清单。机器合规不保证所有阅读器的实际体验。

## 2. 已验证的基线（不是遗留问题）

| 维度 | 2026-10-21 全量 CI 已确认 |
|---|---|
| 编译 | TeX Live 2026 + LuaLaTeX；99 页；`Tagged: yes` |
| 教材结构 | 7 部分、47 个章节源文件；数值例子、目录与页面文字边界 QA 通过 |
| 结构标签 | 48 个 H1、180 个 H2、21 个 Table / 59 个 TH、16 个 Figure / 16 处替代文字 |
| 数学语义 | 1,472 个 Formula，1,472/1,472 个有效 MathML-AF 关联；933 份不同 MathML 文档 |
| 独立规则验证 | veraPDF 1.30.2，PDF/UA-2：`compliant=true`，`failedRules=0`，`failedChecks=0` |
| 排版 | 全书文本边界检查通过，正式主构建无 `Overfull \hbox` 和非法标签父子警告 |

权威证据：[最新成功的全量 CI](https://github.com/CoCoThink/ai-by-intuition/actions/runs/39615037750)、[成功的 MathML 集成 CI](https://github.com/CoCoThink/ai-by-intuition/actions/runs/39613800415)、[PDF/UA 机器验收说明](ACCESSIBILITY.md)。旧 Issue #2（LuaMML 断言）、#3（标题语义）已关闭；Issue #4（人工验收）按范围取消并关闭。

## 3. 剩余遗留事项（不含已关闭问题）

| ID / 优先级 | 遗留问题与证据 | 下一步动作及完成标准 |
|---|---|---|
| **H-01 · P1** | **CI 触发范围不完整。** `.github/workflows/build-latex.yml` 的 `push`/`pull_request` 只监听 `book/**/*.tex`、`scripts/validate_book.py`、`scripts/validate_mathml_af.py` 和工作流自身；`scripts/summarize_verapdf.py`、`scripts/inspect_heading_tags.py` 变更不会自动触发构建。纯文档提交也不会运行验证。 | 让所有承担验证逻辑的 `scripts/**/*.py` 进入 CI 路径过滤；文档变更可另配轻量链接/Markdown 检查，而不强制整本书编译。补一次手动 `workflow_dispatch`，确认工作流仍通过。 |
| **H-02 · P1** | **历史说明与当前实现不一致。** `book/smoke-mathml.tex` 的注释仍说正式教材使用旧数学字体；工作流注释称 MathML 尚在实验阶段。事实上生产源码已启用 `unicode-math`、`mathml-AF`，并通过全部关联验证。`scripts/summarize_verapdf.py` 文件头亦保留旧的 advisory 表述，而正式调用不带 `--advisory`，零失败是硬门槛。 | 更新注释与交接文档中的“实验 / 正式版”边界：**正式 MathML-AF 已完成；原生 `align*` 实验仍失败**。保留历史失败记录，但不得让其与最新发布能力混淆。 |
| **H-03 · P2** | **两项非阻断兼容性实验仍失败。** [CI #39615037750](https://github.com/CoCoThink/ai-by-intuition/actions/runs/39615037750) 的原生 `smoke-mathml.tex`（`align*`）及 `smoke-mathml-lua-unicode.tex` 仍会出现 `luamml-amsmath.lua:63: assertion failed`；`smoke-mathml-aligned.tex` 可生成 MathML，正式全书已使用绕行写法。 | 将旧实验明确标记为预期失败（或从每次正式构建迁移为单独诊断作业）；若 TeX Live/LuaMML 升级再尝试恢复原生 `align*`，必须同时通过 1,472/1,472 MathML-AF 与 veraPDF 门槛。**当前不阻断出版**。 |
| **H-04 · P2** | **依赖复现性仍可加强。** 已固定 TeX Live 年份、veraPDF 镜像标签和 `pypdf==5.9.0`，但 `xu-cheng/texlive-action@v3`、`actions/checkout@v4`、系统字体/apt 包及容器仍可能随上游内容变动；未见完整哈希/镜像摘要锁定清单。 | 记录运行环境与版本清单；对关键 Action 或容器采用 SHA/digest pin（或定期核验策略），针对新镜像单独跑全量回归并保留机器审计工件。 |
| **H-05 · P2** | **存在可定位的文字编辑瑕疵。** `book/chapters/02-dot-product.tex` 的小标题是“再用余弦定理，用余弦定理解释点积与角度”，重复表达未被自动规则检出。 | 改为简洁且与正文一致的标题；按同类规则抽查其他章节标题、重复过渡语和解释一致性。每次正文改动继续跑源码数值与全量 PDF 验收。 |
| **H-06 · P2 / 可选** | **系统化出版视觉精校与版本发布尚未产品化。** 自动 QA 能发现页面边界和 Overfull，但不等于所有图文比例、分页和排版细节均已逐页审看。GitHub 仓库当前未列出正式 Release；CI 只上传 `ai-by-intuition-volume-01` 工件。 | 如需正式发行，建立抽样/逐页视觉检查记录，并选择是否添加版本化 Release、变更说明和不可变 PDF 存档；该项为出版流程增强，不是当前机器验收缺陷。 |

优先级定义：**P1** = 应纳入近期工程整理；**P2** = 非阻断的兼容性、维护性或出版增强。上述状态均来自源码、当前仓库配置和最近成功日志；没有证据表明这些事项导致最新正式 PDF 失败。

## 4. 接手后推荐的执行顺序

1. **先做 H-01 / H-02**：修工作流路径过滤、清理过时说明；只改这些配置/文档，避免不必要地重构 LaTeX。
2. **再做 H-05**：修复点积小标题并运行全量回归，确认 PDF 数量、结构和内容数值没有退化。
3. **将 H-03 单独留为兼容性跟踪**：可以维持预期失败实验，不把已成功的生产 MathML-AF 改回不稳定写法。
4. **酌情推进 H-04 / H-06**：在发行冻结时再决定依赖锁定、长期版本归档与视觉精校范围。

## 5. 复现、检查与交付入口

从仓库根目录运行源码和正式 PDF 验收（依赖 TeX Live 2026、LuaLaTeX、Noto 中文字体、`latexmk`、Poppler，以及 Python 依赖）：

~~~bash
python3 scripts/validate_book.py
cd book
latexmk -lualatex -interaction=nonstopmode -halt-on-error -file-line-error -outdir=build main.tex
cd ..
python3 -m pip install pypdf==5.9.0
python3 scripts/validate_book.py --pdf book/build/main.pdf
python3 scripts/validate_mathml_af.py book/build/main.pdf --minimum 1000
~~~

正式验收还必须参考 [CI 工作流](../.github/workflows/build-latex.yml) 所执行的 **veraPDF 1.30.2 PDF/UA-2** 检查，不能只运行本地 `pdfinfo`、结构树计数或上述部分命令。工件：`ai-by-intuition-volume-01`（正式 PDF）、`pdfua2-machine-audit`（veraPDF XML 与 MathML JSON）、`experimental-mathml-logs`（历史兼容实验）。

核心文件：[`book/main.tex`](../book/main.tex) · [`scripts/validate_book.py`](../scripts/validate_book.py) · [`scripts/validate_mathml_af.py`](../scripts/validate_mathml_af.py) · [`scripts/summarize_verapdf.py`](../scripts/summarize_verapdf.py) · [`docs/ACCESSIBILITY.md`](ACCESSIBILITY.md) · [`ROADMAP.md`](../ROADMAP.md)。

## 6. 交付判据

接手者提交新代码后：① GitHub Actions 全量成功；② 正式 PDF 维持 Tagged/标题/表格/图形结构；③ 所有 Formula 有有效 MathML-AF；④ veraPDF PDF/UA-2 零失败；⑤ 页面和数值检查通过；⑥ 如有编辑性改动，更新影响章节及构建证据。**不因原生 `align*` 的非阻断诊断失败而判定生产 PDF 失败。**

---

最后核对：交接时公开 GitHub Issues **0 个开放项**。本文件为核查后的遗留事项清单，不假定已经存在对应的 Issue 或已有人负责。
