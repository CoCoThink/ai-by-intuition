# 编写与维护指南

本页集中维护教材的写作、源码、生成器、构建、CI、发布与实验记录。编码助手执行约定见 [AGENTS.md](AGENTS.md)。

- 修改教材：[写作原则](#写作原则)、[修改流程](#修改流程)、[生成文件](#生成文件)、[部分开篇与收尾](#部分开篇与收尾)。
- 查找与构建：[源码导览](#源码导览)、[本地构建](#本地构建)、[提交前检查](#提交前检查)。
- 验收与发布：[工作流](#工作流)、[无障碍验收](#无障碍机器验收与边界)、[来源复核](#带日期断言与来源)、[正式发布](#正式发布)。
- 反馈与证据：[勘误与反馈](#勘误与反馈)、[GPT-2 实验记录](#gpt-2-真实权重实验)、[后续计划](#后续计划)。

## 写作原则

- **先结论与直觉，再小数值例子，最后推广为公式。**交代输入、输出、形状，以及哪些参数参与训练。
- **同一组数据贯穿推导。**三维主例的参数只取自 [teaching_reference.py](scripts/teaching_reference.py)。切换算例时，直接在问题或计算旁给出所需数据、维度与假设；避免“独立例”提示条和反复声明与主线无关。
- **行向量约定：**每个 Token 占一行，投影写 `XW`；教学词表 ID、位置和矩阵行列从 1 起，Python 索引减 1。符号以[符号表](book/chapters/00c-symbols.tex)为准。
- **区分等式、近似、启发式解释与真实系统行为。**保留会改变结论的限制，合并重复提醒。版本与核验记录集中在来源附录，正文只保留影响理解或复算的版本条件。
- **不写死章号、页码和题号。**用 `\ref`、`\pageref`、`\hyperref`；CI 会拦截“第 3 章”“第三章”“第 24.10 节”这类字面编号。
- 新增数学、术语或算法时给出可复算的检查；练习和答案保持一一对应。

## 修改流程

1. 正文在 `book/chapters/`，图在 `book/figures/`，章节顺序只由 [book/main.tex](book/main.tex) 的 `\input` 决定。
2. 题库、答案、章末导航、术语表、参考清单和附录 G 断言表都是**生成内容**：改源文件，再运行对应生成器，命令见[生成文件](#生成文件)。
3. 时效性断言（协议、API、模型配置）要查官方来源，同步正文、[dated-claims.json](book/dated-claims.json) 和 [source-audit.json](book/source-audit.json)；`checked_utc` 只在实际复核内容后更新。

阅读路线的页数预算由 [00g-reading-routes.tex](book/chapters/00g-reading-routes.tex) 中 `\setroutebudget` 指定的起止标签自动统计，同页去重。调整阅读范围时同步文字指引与这些标签；成品导航检查会核对实际目标页和表中预算，不手填旧版页数。

## 本地构建

需要 TeX Live 2026（LuaLaTeX、latexmk）、Noto Serif/Sans CJK SC 与 Noto Serif/Sans 字体、Poppler，以及已有的 Python 环境。在仓库根目录运行：

```bash
python3 -m pip install -r requirements-book.txt
python3 scripts/validate_book.py
bash scripts/build_book.sh
python3 scripts/validate_book.py --pdf book/build/main.pdf
```

产物为 `book/build/main.pdf`。等 `latexmk` 全部轮次完成后再读取 PDF 与 `.aux`；改动后的本地预览不作为对应提交的最终 CI 产物。依赖维护与机器审计见[构建与依赖固定](#构建与依赖固定)。

源码检查、生成器与 PDF 审计的 Python 依赖统一列在 [requirements-book.txt](requirements-book.txt)。其中 `pypinyin` 用于术语表排序，`check_book_contract.py` 通过术语表生成器间接使用它；运行下列源码检查前也需要先安装该清单。

## 提交前检查

源码检查（不需要 TeX）：

```bash
python3 scripts/generate_exercise_bank.py --check
python3 scripts/generate_chapter_navigation.py --check
python3 scripts/generate_bilingual_glossary.py --check
python3 scripts/check_book_contract.py --self-test
python3 scripts/check_notebook.py
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

## 源码导览

读者只读一个 PDF；作者按章节维护 LaTeX 源码。[main.tex](book/main.tex) 是唯一入口，**章节顺序和章号只由其中的 `\input` 与 `\section` 决定**，文件名前缀不代表章号（多数文件名沿用了早期编号）。

### 前置部分

| 内容 | 源码 |
|---|---|
| 封面、目录 | [main.tex](book/main.tex) |
| 版权页 | [00h-colophon.tex](book/chapters/00h-colophon.tex) |
| 阅读路线与表示约定 | [00g-reading-routes.tex](book/chapters/00g-reading-routes.tex) |
| 开读前：五题入门自检 | [00j-entry-check.tex](book/chapters/00j-entry-check.tex) |
| 序章（在第一部分之前） | [00-guide.tex](book/chapters/00-guide.tex) |
| 部分开篇与收尾 | [part-maps.tex](book/part-maps.tex)，累积复习生成到 [part-reviews.tex](book/part-reviews.tex)；设计见[下文](#部分开篇与收尾) |

### 正文

正文共 34 章。前七部分为主线，第八、九部分为扩展路径。一个文件可能只是某章的后半部分（表中标“含”“续”）。

| 部分 | 章节源码（按印刷顺序） |
|---|---|
| 一 · 学习 | [函数与损失](book/chapters/00-functions.tex)（续 [损失](book/chapters/16-loss-gradient.tex)）；[梯度下降](book/chapters/16-loss-gradient.tex)（续 [训练组织](book/chapters/18c-training-engineering.tex)）、[非线性](book/chapters/07-functions-relu.tex)、[反向传播](book/chapters/17-backpropagation.tex)（含[完整一步](book/chapters/18b-end-to-end-learning.tex)）、[泛化](book/chapters/18-generalization.tex) |
| 二 · 矩阵 | [向量与点积](book/chapters/01-vectors.tex)（续 [02](book/chapters/02-dot-product.tex)）、[矩阵乘法](book/chapters/03-matrix-multiplication.tex)、[MLP](book/chapters/10-mlp.tex) |
| 三 · 文字 | [Tokenizer](book/chapters/20a-tokenizer.tex)、[预测任务](book/chapters/20b-task-contract.tex)、[分类损失](book/chapters/20c-classification-loss.tex)、[Embedding](book/chapters/20-embeddings.tex) |
| 四 · 上下文 | [上下文缺口与 RNN](book/chapters/21a-context-gap.tex)（续 [21](book/chapters/21-rnn.tex)）、[Attention 与 Q/K/V](book/chapters/21c-naive-attention.tex)（续 [投影对照](book/chapters/21b-why-attention.tex)）、[批量与因果注意力](book/chapters/11-softmax-memory.tex)、[位置与多头](book/chapters/22a-position-multihead.tex) |
| 五 · Transformer | [Block](book/chapters/22-transformer-architecture.tex)、[FFN 与输出头](book/chapters/10b-ffn-output-head.tex)、[三维前向](book/chapters/22b-token-to-output.tex)、[联合训练](book/chapters/22c-language-training.tex)、[逐词生成](book/chapters/23-llm-systems.tex)、[真实尺度](book/chapters/23a-from-toy-to-gpt.tex) |
| 六 · 助手 | [ICL](book/chapters/23aa-pretraining-icl.tex)、[训练反馈与推理时计算](book/chapters/23c-post-training.tex)（续 [固定权重选答](book/chapters/23cc-test-time-compute.tex)）、[RAG](book/chapters/23d-agent-systems.tex)、[工具与 Agent 循环](book/chapters/23d-agent-tools.tex)、[协议与多 Agent](book/chapters/23d-agent-protocols.tex)、[数据、训练与部署](book/chapters/23b-deployment-and-ecosystem.tex) |
| 七 · 架构 | [现代 Transformer](book/chapters/22d-modern-transformers.tex)、[技术判断](book/chapters/23e-tech-judgement.tex) |
| 八 · 视觉（扩展） | [CNN](book/chapters/19-cnn.tex)、[ViT 与视觉桥接](book/chapters/19b-vit.tex) |
| 九 · 联想记忆（扩展） | [线性写入与误差修正](book/chapters/04-key-value-outer-product.tex)（续 [串扰](book/chapters/05-memory-interference.tex)、[修正](book/chapters/06-better-linear-memory.tex)）、[非线性检索与容量](book/chapters/08-stacking-key-value.tex)（续 [非线性](book/chapters/09-nonlinearity-and-memory.tex)、[统一视角](book/chapters/14-summary.tex)、[★ 容量](book/chapters/13-capacity.tex)） |
| 终章 | [回到那四个 Token](book/chapters/23f-foundation-recap.tex) |

### 附录

| 附录 | 源码 |
|---|---|
| A 公式、数学与符号速查 | [00e](book/chapters/00e-core-formulas.tex)、[00b](book/chapters/00b-math-tools.tex)、[00c 符号表](book/chapters/00c-symbols.tex)、[30 优化器](book/chapters/30-optimizer-appendix.tex)、[00i 数据地图](book/chapters/00i-data-map.tex) |
| B 三维实验、复算与脚本 | [00f 中间量](book/chapters/00f-transformer-intermediates.tex)、[24e PyTorch 与脚本总表](book/chapters/24e-pytorch-lab.tex) |
| C 题库 · D 答案 | 由 [exercises.json](book/exercises.json) 生成 [25](book/chapters/25-exercise-bank.tex)、[27](book/chapters/27-answer-key.tex)；随堂自测答案 [28](book/chapters/28-chapter-checks.tex) 手写 |
| E 术语表与索引 | 源：[24-lexicon](book/chapters/24-lexicon.tex)、[24b](book/chapters/24b-modern-lexicon.tex)、[24d 英文映射](book/chapters/24d-english-index.tex)；生成：[24e 拼音主表](book/chapters/24e-bilingual-glossary.tex)、[24f 英文简表](book/chapters/24f-english-index.tex)；手写：[24c 概念图](book/chapters/24c-concept-map.tex) |
| F 来源 | [26-sources](book/chapters/26-sources.tex)，链接记录 [source-audit.json](book/source-audit.json) |
| G 版本与带日期断言 | [29-revision-notes](book/chapters/29-revision-notes.tex)，断言表由 [dated-claims.json](book/dated-claims.json) 生成 |

### 其他文件

- `book/figures/`：TikZ 教学图，每张有语义的图都带 Figure、Caption 与中文替代文字。
- `book/smoke-tagging.tex`：CI 在整书构建前编译的最小 Tagged PDF 冒烟测试。
- `book/smoke-mathml*.tex`：仅由手动兼容性工作流使用，复现 LuaMML 的已知限制（见[无障碍验收](#无障碍机器验收与边界)）。

## 生成文件

下列文件不要手改；修改维护来源，并在正文修改完成后运行对应生成器：

- `book/chapters/25-exercise-bank.tex`、`book/chapters/27-answer-key.tex`、`book/part-reviews.tex`、`book/chapter-practice.tex`
- `book/chapters/24e-bilingual-glossary.tex`、`book/chapters/24f-english-index.tex`、`docs/TERM_OCCURRENCES.md`
- `book/figures/reference-qr.tex`、`docs/REFERENCES.md`
- `book/chapters/29-revision-notes.tex` 中的断言表

| 内容 | 维护来源 | 生成命令（仓库根目录） |
|---|---|---|
| 题库、D.1 解答、部分复习 | [exercises.json](book/exercises.json) | `python3 scripts/generate_exercise_bank.py` |
| 各章练习指针与答案导航 | 题库、正文标签和答案标题 | `python3 scripts/generate_chapter_navigation.py` |
| 拼音术语主表与[出现章节表](docs/TERM_OCCURRENCES.md) | [基础词条](book/chapters/24-lexicon.tex)、[现代词条](book/chapters/24b-modern-lexicon.tex)、[英文映射](book/chapters/24d-english-index.tex)及生成器映射 | `python3 scripts/generate_bilingual_glossary.py` |
| 英文简表 | 已生成的术语主表 | `python3 scripts/generate_english_index.py` |
| 二维码与[网页参考清单](docs/REFERENCES.md) | [source-audit.json](book/source-audit.json) | `python3 scripts/generate_reference_assets.py` |
| 带日期断言表 | [dated-claims.json](book/dated-claims.json) | `python3 scripts/check_dated_claims.py --write` |

题库、章末导航、双语术语和参考资产生成器支持 `--check`。英文简表生成器直接写文件，应检查生成后的差异，不支持 `--check`；断言复核见[带日期断言与来源](#带日期断言与来源)。

## 部分开篇与收尾

文案维护在 [part-maps.tex](book/part-maps.tex)，累积复习 R 题维护在 [exercises.json](book/exercises.json)。序章放在第一部分之前；开篇引入问题，收尾回答问题并串联本部分的章节。

| 位置 | 内容与写法 |
|---|---|
| 开篇：为什么从这里开始 | 1–2 句承接上一部分或序章，提出具体问题；扩展路径注明“主线不依赖”。 |
| 开篇：先想一想 | 一道凭直觉可答的题，只用已知词语；浅蓝框提示“凭直觉答就行，本部分末尾会给出答案”。 |
| 开篇：学完你能做到 | 两条，用“算出、判断、说明、写出”等动作描述。 |
| 开篇：地图与路线 | 每个实际章节只列一次，兼容标签不另列；路线用“（你在这里）”标出当前位置，完整九格图只在“怎么读”页出现。 |
| 收尾：回到开篇 | 复述问题并给出简答，链接到本部分的答案小节。 |
| 收尾：累积复习与下一步 | 接生成的两道 R 题，再交代下一部分；主线结束处说明后面是两条扩展路径。 |

问题、地图与答案的当前内容直接查源码，不另维护副本。每部分用 `\partthink<键>` 共用首尾问题，`\partentry<键>` 和 `\partexit<键>` 调用通用宏；收尾再调用生成的 `\partreview<键>`。答案处标 `\phantomsection\label{partq:<部分键>}`，保证读到该处时能认出它在回答开篇问题。

[main.tex](book/main.tex) 中的顺序为 `\part{…}\label{part:<键>}` → `\partentry<键>` → 章节 `\input` → `\partexit<键>`。第九部分的框架来源署名紧跟开篇；跨部分引用使用部分名称及 `\hyperref[part:<键>]`，不写死编号。

`check_book_contract.py --self-test` 检查序章位置、首尾配对与答案归属；`validate_book.py --pdf` 检查开篇元素和收尾所在部分。开篇须在一页内；增加文字后渲染九个开篇页检查。收尾前保留 `\Needspace`，可独占部分结束页；同时检查章末留白，避免与固定小结重复。部分收尾页与章节自身的尾页分别验收。

## 工作流

| 工作流 | 触发 | 作用 |
|---|---|---|
| [Build one PDF book](.github/workflows/build-latex.yml) | 改动 `book/`、`scripts/` 或该工作流 | 源码检查 → 最小 Tagged 冒烟测试 → 整书构建 → 成品检查 → MathML、灰度、色觉模拟、veraPDF；成功时上传 `ai-by-intuition-book` 与 `pdfua2-machine-audit` |
| [Review dated assertions](.github/workflows/check-dated-claims.yml) | 每周一 03:17 UTC，以及改动断言、来源或正文 | 检查断言到期日，并比较 MCP 官方当前修订与书中版本 |
| [Check Markdown links](.github/workflows/check-docs.yml) | 改动 Markdown | 本地链接目标存在、README 含许可声明 |
| [Real GPT-2 reproducibility experiment](.github/workflows/gpt2-real-experiment.yml) | 手动，或改动该实验 | 下载固定修订的 GPT-2 权重做一次真实推理，结果见[下方记录](#gpt-2-真实权重实验)；不阻断 PDF 构建 |
| [Diagnose historical LuaMML compatibility](.github/workflows/check-compatibility.yml) | 手动 | 复现原生 `align*` 的 LuaMML 断言失败（见下文限制） |
| [Publish validated book](.github/workflows/publish-release.yml) | 手动 | 从选定的成功构建创建新 Release，见[正式发布](#正式发布) |

路径过滤决定是否触发整书构建：只改 Markdown 不会编译 PDF。不要把“未触发”说成“已通过”。

## 构建与依赖固定

- 本地与 CI 都通过 `bash scripts/build_book.sh` 构建。提交号依次取 `BOOK_BUILD_SHA`、`GITHUB_SHA`、`git rev-parse HEAD`，印在版权页和附录 G；没有 Git 信息的源码包会省略整句来源说明。提交号变化时脚本强制刷新 PDF。
- 所有第三方 Action 固定到完整提交 SHA；veraPDF 1.30.2 按镜像摘要拉取：`verapdf/cli@sha256:d5ee329657cf9bc4b2400392dd54c7d0a0ce9980ff6fa2da5590eebeec007cdb`。
- 仍会浮动的部分：`texlive_version: 2026` 是年份选择而非镜像摘要，apt 安装的 Noto 字体与 Poppler 取决于当时的 Debian 索引。因此不声称字节级可复现；`pdfua2-machine-audit` 中的 `texlive-environment.txt`、`runner-environment.txt`、`verapdf-image.txt` 记录了每次实际使用的版本。
- 构建检查的 Python 依赖版本以 [requirements-book.txt](requirements-book.txt) 为准，本地与工作流共用同一清单；CI 在首次源码检查前选择 Python 3.12 并安装这些依赖。PyTorch 教学实验另见 [requirements-teaching.txt](requirements-teaching.txt)。

三处 NumPy 固定版本对应不同的验证基线，分别维护：

| 用途 | NumPy 与环境 | 保留该版本的原因与验证范围 |
|---|---|---|
| 整书构建与检查 | [requirements-book.txt](requirements-book.txt)：NumPy `2.3.5`；CI 使用 Python `3.12` | 沿用完整 PDF 构建流水线的数值复算与审计基线；这一环境不安装 PyTorch。 |
| PyTorch 教学实验 | [requirements-teaching.txt](requirements-teaching.txt)：NumPy `2.5.0`、PyTorch `2.14.0`；已验证 Python `3.14.6` | 与附录 B、Notebook 的 CPU/float64 前向和梯度对照记录一致。 |
| 固定 GPT-2 真实实验 | [实验工作流](.github/workflows/gpt2-real-experiment.yml)：NumPy `1.26.4`、PyTorch `2.5.1`、Transformers `4.46.3` | 保留已完成真实实验的依赖组合，复跑时另存完整安装记录；细节见[GPT-2 实验记录](#gpt-2-真实权重实验)。 |

这些是已验证组合，不是 NumPy 版本之间必然不兼容的声明。选择任务对应的环境安装清单，不把两份清单连续装进同一环境。若要统一版本，先分别重跑整书 CI、教学梯度对照与固定 GPT-2 真实实验，再更新清单和验证记录；个人环境的绝对路径不写入仓库。

**升级依赖时：**单独开 PR；Action 的 SHA 从上游官方标签重新获取；附上新旧环境记录；源码检查、成品检查、全部公式 MathML 关联和 veraPDF 零失败都要通过；页数或结构数量的意外变化要说明原因。

## 无障碍：机器验收与边界

`book/main.tex` 使用 `\DocumentMetadata{lang=zh-CN,tagging=on,pdfstandard=ua-2,tagging-setup={math/setup=mathml-AF}}`。CI 阻断以下任一失败：

- 结构树、标题层级、表头、Figure 与 Caption 的嵌套和中文替代文字（`validate_book.py --pdf`）；
- 每个公式都有可解析的 MathML 关联文件（`validate_mathml_af.py`）；
- veraPDF PDF/UA-2 零失败。

这些只覆盖机器可验证的规则。项目不安排真实读屏器体验测试，机器通过不代表辅助阅读器中的实际体验已经验证。

**已知限制：**TeX Live 2026 的 LuaMML 处理原生 `amsmath` 的 `align*` 时触发 `luamml-amsmath.lua:63: assertion failed`。正文改用 `aligned` 组合；`book/smoke-mathml*.tex` 由手动兼容工作流复现该问题，升级 LaTeX 或 LuaMML 后重新运行。

不要通过移除 `\DocumentMetadata`、关闭标签、删掉替代文字或降低阈值来让 CI 通过。

## 灰度与人工校样

CI 对每页做灰度预检（`audit_grayscale_pdf.py`：接近空白的页、贴边的深色像素），并对 Q/K/V 图做三种色觉模拟（`audit_color_roles.py`）。这只是粗筛，不能代替人工看页面。

人工校样用 `scripts/print_proof.py` 生成灰度页图、逐页检查表和来源摘要，不修改 PDF：

```bash
# 关键页
python3 scripts/print_proof.py book/build/main.pdf --pages 1-6,last --out-dir book/build/print-proof
# 发布前逐页
python3 scripts/print_proof.py book/build/main.pdf --all --scale 1100 --out-dir book/build/print-proof \
  --audit-json pdfua-audit/grayscale-audit.json
```

传入同一次 CI 的 `grayscale-audit.json` 时，PDF 哈希或源码提交不一致会直接拒绝生成，避免混用不同构建。逐页核对：

- 颜色之外仍能区分角色：Q/K/V、梯度正负、Mask 可见与否要有字母、数值、线型或位置提示；
- 中文、上下标和长 URL 不溢出，没有缺字；
- 图表的表头、单位、线型在灰度下可辨，图题与替代文字表达主要信息；
- 目录、交叉引用、脚本路径与本次构建一致；跨页的例子、题目和答案能追溯。

审阅记录要写明完整提交号、CI 运行号、审阅人和日期，不能沿用旧 PDF 的结论。

## 带日期断言与来源

- 断言清单的唯一来源是 [dated-claims.json](book/dated-claims.json)，附录 G 的表格由 `python3 scripts/check_dated_claims.py --write` 生成。复查周期为“90 天或出现新修订，以先到者为准”。
- 每周的定时工作流与每次整书构建都会检查到期日期；MCP 官方入口指向新修订时也会失败。处理方式：先重新阅读规范、核对正文示例和请求字段，再更新版本与 `checked_utc`。编译日期、链接可访问或 CI 成功都不能替代内容核验，也不要为了解除门禁直接改日期。
- 附录 F 的逐条链接记录在 [source-audit.json](book/source-audit.json)；网页清单 [REFERENCES.md](docs/REFERENCES.md) 与二维码由 `python3 scripts/generate_reference_assets.py` 生成。

## 复算与题号

复算脚本总表在[附录 B 源码](book/chapters/24e-pytorch-lab.tex)（标签 `app:reproduction-scripts`），`check_book_contract.py` 检查关键脚本都列在表中。默认只运行离线实验；Claude 等付费 API 的真实调用需要明确授权，中文分词器的 `--real` 只下载固定版本的分词器文件。

C 题和 R 题按印刷顺序连续编号，由 `generate_exercise_bank.py` 校验。增删题目后整体重排，并同步正文、脚本和文档中的引用；`legacy_id` 中的旧编号只作隐藏锚点，不在印刷版显示。

## 正式发布

主分支构建产生草稿工件；正式版本由维护者签核后手动创建 Release。使用尚不存在的语义化版本号和 Git 标签，修订已发布内容时另发新版本。

对拟发布的同一次构建完成签核，记录完整提交号、CI 运行号、负责人和日期：

1. 选定 `main` 上成功的 [Build one PDF book](.github/workflows/build-latex.yml)，同时取得 `ai-by-intuition-book` 与 `pdfua2-machine-audit`。核对源码、数值、成品排版、全部公式 MathML 关联和 veraPDF PDF/UA-2 零失败；PR 的绿灯不能替代。
2. 按[灰度与人工校样](#灰度与人工校样)逐页审阅同一份 PDF，重点核对改动的算例、图表和分页。
3. 核对附录 F 中飞天闪客课程及 Alex Wang 文章的集中署名与链接，确认没有复制原文或图片；逐项核对引用的模型配置、JSON 片段和第三方图示的使用条款。
4. 运行 `python3 scripts/check_dated_claims.py --self-test --online --check-due`，确认附录 G 没有到期或落后于官方新修订的条目。
5. 写好新版本的发布说明，核对封面、版权页与附录 G 中的版本和提交号。

在 [Publish validated book](.github/workflows/publish-release.yml) 中从 `main` 手动运行，填写 `version`（新版本号，如 `vMAJOR.MINOR.PATCH`）和 `build_run_id`（选定的成功运行编号）。工作流会拒绝已有标签或 Release，以及不属于本仓库、未成功或不在 `main` 上的构建；构建后若 `main` 又改动了 `book/`、`scripts/` 或构建工作流，须重新构建。

工作流下载该次构建的 PDF 与机器审计，复核页数、MathML、veraPDF 和环境记录后，创建 Release 并附上 `AI-by-Intuition-Book.pdf`、`SHA256SUMS`、`build-audit.zip`。发布说明包含版本、日期、源码提交及原始构建；发布后同步 README 与[勘误与反馈](#勘误与反馈)的版本信息。

## 勘误与反馈

本节只记录已确认、会影响读者理解或计算的问题。排版小问题和措辞改进直接在主分支修订，不逐条列出。

请在 [Issues](https://github.com/CoCoThink/ai-by-intuition/issues) 中写明：

- PDF 的版本与提交号（印在版权页和附录 G）、页码和章节；
- 原文、算出的结果和期望结果，最好附上输入数据或复算步骤；
- 图形问题附截图。

发现的问题直接在源码中修正，并由 CI 回归检查防止再次出现；需要保留读者提醒时，在本节登记。

提交 PR 时说明改善了哪一种初学者困惑，附上手算核对步骤，并确认相关检查通过。

## GPT-2 真实权重实验

本实验对应“从三维到真实模型”一章的 ★ 选读复算（附录 G 引用其结果），**不阻断 PDF 构建**。

### 输入与依赖约定

- 模型：`openai-community/gpt2`
- 固定权重 revision：`607a30d783dfa663caf39e06633721c8d4cfcd7e`
- 默认 Prompt：`The capital of France is`
- 运行平台：Ubuntu 24.04、独立 Python 虚拟环境、CPU 推理
- 主依赖：PyTorch 2.5.1、Transformers 4.46.3、NumPy 1.26.4、Matplotlib 3.9.2
- Attention 后端：`eager`；输出第一层首头热图

### 已完成的固定版本真实实验（2026-10-23）

成功工作流：[Real GPT-2 reproducibility experiment #39897932969](https://github.com/CoCoThink/ai-by-intuition/actions/runs/39897932969)。对应源码提交：[`a20a0c15f3c46b6102c8ac5222b5607ee731a46a`](https://github.com/CoCoThink/ai-by-intuition/commit/a20a0c15f3c46b6102c8ac5222b5607ee731a46a)。[下载该运行的工件](https://github.com/CoCoThink/ai-by-intuition/actions/runs/39897932969/artifacts/12477398540)。

| 检查 | 真实输出 |
|---|---|
| 模型 commit | `607a30d783dfa663caf39e06633721c8d4cfcd7e` |
| 运行环境 | torch `2.5.1+cpu`、transformers `4.46.3`、numpy `1.26.4` |
| 英文 Prompt | `The capital of France is` |
| 真实分词 | 5 个；`[464, 3139, 286, 4881, 318]` |
| 模型 logits | `(1, 5, 50257)`，全部有限 |
| Softmax 总和 | `T=0.7/1.0/1.5` 均为 `1.00000000` |
| 首层首头因果掩码 | 未来位置权重最大绝对值 `0` |
| T=1.0 的候选示例 | `' the'` 概率 `0.08459`；`' Paris'` 概率 `0.03224` |

这组真实数据来自上述运行下载的 `gpt2-console.txt`，热图来自 `gpt2-attention.png`。最初用 float32 对五万多个概率求和时曾得到 `1.00001204` 的舍入结果；改用 float64 后通过了同一模型的概率归一化检查。这属于**数值审计精度修正**，并未调整模型权重。

### GitHub Actions 入口

在[可选 GPT-2 真实实验](.github/workflows/gpt2-real-experiment.yml)对应的 GitHub Actions 工作流中选择 **Run workflow**。工作流文件或实验脚本在主分支发生修改时，也会独立触发运行；不属于 PDF 主 CI。

成功工件 `gpt2-real-repro-report` 应含：

- `revision.txt`：本次源码 SHA；
- `python-packages.txt`：实际安装的完整依赖版本；
- `gpt2-console.txt`：Token 数和 ID、完整 logits 形状、三种温度的 Top-5 和概率和；
- `gpt2-attention.png`：第一层第零个头的因果 Attention 灰度热图。

程序会检查最后一位词表宽度为 50,257，概率和接近 1；概率归一化检查使用 float64 累加，避免大词表的 float32 求和舍入误差；Attention 上三角（未来 Key）最大绝对值小于 1e-6，每行权重和接近 1。

**证据边界：**预跑必须由完成的真实权重工作流报告支持，离线公式自检不足以给出真实 Token 数或 Top-5。这里只锁定四个顶层依赖，运行时保存实际的完整传递依赖清单。这是英文 Prompt 的数学与模型接口 sanity check，不涉及正式模型质量评测。下载公开权重需要联网，网络或依赖故障不会影响独立的 PDF 构建。

## 后续计划

以下内容尚未实施，拟在助手部分的证据与工具讨论之后，整合为两章：

| 拟设章节 | 整合已有内容 | 需要补齐的教学闭环 |
|---|---|---|
| 评测：怎样知道助手变好了？ | 技术判断中的基准、评测污染、LLM 评审；RAG、工具与协议中的证据和工具核对 | 用季度报告任务建立固定测试集，手算正确率与任务完成率；比较检索、工具及权限检查的消融结果，配复算脚本、开放设计题和解答。 |
| 幻觉与校准：什么时候该查证或拒答？ | 校准选读、RAG 的证据缺口与来源核验、工具结果的可信边界 | 用同一组问题区分事实错误与置信度偏差，手算置信度分组及拒答后的覆盖率和准确率；加入检索、查证、拒答的流程图与练习。 |

先完成可复算案例，再调整章节顺序；提示注入与权限设计继续衔接协议章，避免把“有来源”写成“已经核验”。验收覆盖正文、习题、提示与解答，并运行既有数值、引用、排版与无障碍 CI。

## 贡献与许可

教材正文、LaTeX/TikZ、文档及正式 PDF 采用 [CC BY 4.0](LICENSE)；`scripts/` 与 `.github/workflows/` 采用 [MIT](scripts/LICENSE)，范围和建议署名见 [README](README.md#开放许可证与转载)。提交前请确认你有权按对应许可证贡献这些内容；引用第三方材料时标明来源和原始许可，未经授权的内容不要并入仓库。

教学 Notebook 与本 PDF 的代码版本分别核对，运行前填写版权页提交号；固定依赖见 [requirements-teaching.txt](requirements-teaching.txt)。本地复算仍使用已有 Python 环境，以该环境解释器执行 `-m pip install -r requirements-teaching.txt`。
