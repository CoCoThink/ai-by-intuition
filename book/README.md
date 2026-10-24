# 全书阅读顺序 · AI by Intuition

**唯一入口：** [book/main.tex](main.tex)。读者只需要阅读一个 PDF；
源码按章节维护，正文编号由 LaTeX 自动生成，目录与书内引用应以编译 PDF 为准。

**教材授权：** 本书原创文字、LaTeX/TikZ 图形与正式 PDF（包括 v0.1.0）采用 [CC BY 4.0](../LICENSE)；Python 工具和 GitHub Actions 工作流采用 [MIT](../scripts/LICENSE)。转载、翻译或商业使用应署名及标明改动；第三方引用仍遵循其原有许可。详情见 [仓库许可说明](../README.md#开放许可证与转载)。

**从这里开始：**[目录前的阅读路线](chapters/00g-reading-routes.tex)与[单独版权页、约定](chapters/00h-colophon.tex)；必读主线结束后有[技术底座回顾](chapters/23f-foundation-recap.tex)。[勘误与版本记录](../docs/ERRATA.md)持续更新。

## 当前目录：八部分、36 章、附录 A–K

章节顺序、自动章号与附录定位以 [main.tex](main.tex) 为准。此次修订把图像专题前移，联想记忆置于正文结束后的提高附录；技术底座回顾成为正文最后一页。

| 部分 | 章节和源码 |
|---|---|
| I · 学习与训练 | [函数](chapters/00-functions.tex)、[损失与梯度](chapters/16-loss-gradient.tex)、[训练组织](chapters/18c-training-engineering.tex)、[反传](chapters/17-backpropagation.tex)、[泛化](chapters/18-generalization.tex) |
| II · 向量与矩阵 | [向量](chapters/01-vectors.tex)、[点积](chapters/02-dot-product.tex)、[矩阵](chapters/03-matrix-multiplication.tex)、[MLP](chapters/10-mlp.tex) |
| III · 文字与 Token | [Tokenizer](chapters/20a-tokenizer.tex)、[分类损失](chapters/20c-classification-loss.tex)、[Embedding](chapters/20-embeddings.tex)、[任务契约](chapters/20b-task-contract.tex) |
| IV · 上下文 | [RNN](chapters/21-rnn.tex)、[Q/K/V](chapters/21b-why-attention.tex)、[Self-Attention](chapters/11-softmax-memory.tex)、[位置与多头](chapters/22a-position-multihead.tex) |
| V · Transformer | [Block](chapters/22-transformer-architecture.tex)、[FFN](chapters/10b-ffn-output-head.tex)、[贯通前向](chapters/22b-token-to-output.tex)、[联合训练](chapters/22c-language-training.tex)、[生成](chapters/23-llm-systems.tex)、[玩具到 GPT](chapters/23a-from-toy-to-gpt.tex) |
| VI · 视觉桥接 | [CNN](chapters/19-cnn.tex) → [ViT 与多模态](chapters/19b-vit.tex) |
| VII · 助手与 Agent | [ICL](chapters/23aa-pretraining-icl.tex)、[后训练](chapters/23c-post-training.tex)、[RAG](chapters/23d-agent-systems.tex)、[Agent loop](chapters/23d-agent-tools.tex)、[协议与多 Agent](chapters/23d-agent-protocols.tex)、[部署](chapters/23b-deployment-and-ecosystem.tex) |
| VIII · 架构与判断 | [现代 Transformer](chapters/22d-modern-transformers.tex)、[评测与技术判断](chapters/23e-tech-judgement.tex)、[技术底座回顾](chapters/23f-foundation-recap.tex) |

**附录 A–G**：公式、实验、练习、参考答案、术语、文献与勘误；**附录 H–K**：外积记忆、串扰、Delta 更新、非线性检索与高维容量（[专题起点](chapters/04-key-value-outer-product.tex)）。

章节间跨引优先采用 `\\label`／`\\ref`，而非写死章号。 CI 在编译前运行 `scripts/check_chapter_crossrefs.py`，拦截写死的“第 N 章”，另由 `scripts/check_part_references.py` 禁止包括“第 VI 部分／第六部分／第6部分”在内的硬编码部分编号，并检查八个 `part:` 标签与实际部分标题、顺序匹配，并依 `main.tex` 的实际 `\\section` 顺序逐项校验附录 D 的章号；编译后仍由 `check_latex_references.py` 拦截未解析引用与 PDF 的 `??`。正文所有算例和教学实验仍以三维贯通参考脚本为数值基线。自测答案详解保留在附录 D，并按正文编号及提高专题排列。

## 自测题与答案的两级阅读

**45 组随堂／提高自测均有三道正文基础题，另外 50 道延伸题在附录 C**，每组提供预测、计算或形状推导、找错、比较、场景或方案等不同能力的检验，避免将同一数值的二次归一化冒充“迁移”。每一组保留原 `check:` 和 `answer:` 跳转标签；**正文不在题目下面直接剧透答案，完整推导集中在附录**，[附录 D.2](chapters/28-chapter-checks.tex)按 `题 1…题 N` 给出独立的解题过程与核验依据，支持从正文直接跳至对应题组。旧版集中在 `book/main.tex` 的 27 组第四题库和速答库已清理，CI 逐章核对题型不重复、编号齐全和答案数量一致。**机器校验不等于完成真实教学试做**：难度梯度、读者理解效果、打印版逐页审校及实际屏读体验仍需人工签核。

## 一次构建，一本 Tagged PDF

CI 使用 **TeX Live 2026 + LuaLaTeX**，启动时要求 Noto 中文及西文字体。可以从仓库根目录先检查源码，再构建整本书：

```bash
python3 scripts/validate_book.py
cd book
latexmk -lualatex -interaction=nonstopmode -halt-on-error -file-line-error -outdir=build main.tex
cd ..
python3 -m pip install pypdf==5.9.0
python3 scripts/validate_book.py --pdf book/build/main.pdf
```

生成文件为 `book/build/main.pdf`。已发布的正式 PDF 从 [v0.1.0 Release](https://github.com/CoCoThink/ai-by-intuition/releases/tag/v0.1.0) 下载；未来新版本通过显式版本号和已通过的构建发布。CI 的成功运行只上传一份 `ai-by-intuition-book` PDF 工件及一份机器审计，具体从 [GitHub Actions](https://github.com/CoCoThink/ai-by-intuition/actions/workflows/build-latex.yml) 获取。

2026 年 10 月 22 日的 [v0.1.0 正式成功构建](https://github.com/CoCoThink/ai-by-intuition/actions/runs/39699805713)生成 99 页 PDF，已通过七部分章节检查、数值例子、目录与文字边界、全部公式 MathML-AF 和 veraPDF PDF/UA-2 零失败的机器验收。

## Tagged PDF 与自动化验收

目前 `book/main.tex` 采用 `\DocumentMetadata{lang=zh-CN,tagging=on,pdfstandard=ua-2,tagging-setup={math/setup=mathml-AF}}`，不再使用旧版 `testphase` 或为 `tabularx` 关闭表格标签的实验性兼容补丁。

CI 用 `pypdf==5.9.0` 验证 `/MarkInfo /Marked true`、`/StructTreeRoot`、`/Document` 根节点和公式／图像／替代文字节点。v0.1.0 发布时的历史构建含 1,472 个公式节点、21 张表格与 59 个 TH 表头、16 个图像节点及 16 处替代文字、48 个 H1 与 180 个 H2 标题。M2 重排增加了词表尺度表和训练投影图，**上述旧统计不能代表新版构建**；已发布 PDF 通过了 veraPDF 的 PDF/UA-2 机器验证；实际读屏体验与人工无障碍验收不在项目维护范围。**

### 最小回归测试

`book/smoke-tagging.tex` 检验中文、公式、`tabularx` 和带中文替代文字的 TikZ 图。CI 先构建最小文件并检查 `Tagged: yes`，再构建整本书。手动复现：

```bash
cd book
mkdir -p build/smoke
latexmk -lualatex -interaction=nonstopmode -halt-on-error -file-line-error -outdir=build/smoke smoke-tagging.tex
pdfinfo build/smoke/smoke-tagging.pdf | grep '^Tagged:'
```

正式回归 CI 检查图注父子结构、超宽盒子和标题层级，防止这些已修复问题再次出现。公式 MathML 已在正式构建中启用，`scripts/validate_mathml_af.py` 对**实际生成的每一个公式节点**核对 MathML-AF 关联，而不是将旧版的 1,472 个节点误写为当前固定目标。当前正文与附录的页数、图数、题目链接数量随修订变化，均以最新的 GitHub Actions 构建报告和实际 PDF 检查为准，不把过去某次成功构建的统计数据当作永久指标。本书仍标为 v0.2.0-draft（未发布）。真实屏幕阅读器、纸质印刷与读者试做尚未人工签核，不能把机器合规等同于无障碍使用体验；详见[自动化验收说明](../docs/ACCESSIBILITY.md)。

**中文检索：**附录 E 还提供 136 项按拼音排序的中文索引，附正文页码链接。首次本地构建前运行 `python3 -m pip install pypinyin==0.55.0` 和 `python3 scripts/generate_chinese_index.py`；CI 会自动生成索引并核对全部 136 项链接。
