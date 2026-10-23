# 全书阅读顺序 · AI by Intuition

**唯一入口：** [book/main.tex](main.tex)。读者只需要阅读一个 PDF；
源码按章节维护，正文编号由 LaTeX 自动生成，目录与书内引用应以编译 PDF 为准。

**教材授权：** 本书原创文字、LaTeX/TikZ 图形与正式 PDF（包括 v0.1.0）采用 [CC BY 4.0](../LICENSE)；Python 工具和 GitHub Actions 工作流采用 [MIT](../scripts/LICENSE)。转载、翻译或商业使用应署名及标明改动；第三方引用仍遵循其原有许可。详情见 [仓库许可说明](../README.md#开放许可证与转载)。

**从这里开始：**[目录前阅读路线与时间参考](chapters/00g-reading-routes.tex)；必读主线结束后有[技术底座回顾](chapters/23f-foundation-recap.tex)。[勘误与版本记录](../docs/ERRATA.md)持续更新。

## 当前修订目录：八个必读部分、视觉选读（38 章）

本目录以 [\`book/main.tex\`](main.tex) 的实际输入顺序为准。
下列旧文件名用于稳定链接；印刷章节号由 LaTeX 生成。

### I–III：从函数到文字（第 1–14 章）
I：[函数](chapters/00-functions.tex)、[损失](chapters/16-loss-gradient.tex)、
[反传](chapters/17-backpropagation.tex)、[泛化](chapters/18-generalization.tex)。

II：[向量](chapters/01-vectors.tex)、[点积](chapters/02-dot-product.tex)、
[矩阵](chapters/03-matrix-multiplication.tex)、[MLP](chapters/10-mlp.tex)、
[优化器](chapters/18c-training-engineering.tex)。

III：[BPE](chapters/20a-tokenizer.tex)、[分类损失](chapters/20c-classification-loss.tex)、
[Embedding](chapters/20-embeddings.tex)、[任务契约](chapters/20b-task-contract.tex)。

### IV：上下文与 Attention（第 15–20 章）
[上下文缺口](chapters/21a-context-gap.tex) →
[RNN](chapters/21-rnn.tex) →
[朴素点积 Attention](chapters/21c-naive-attention.tex) →
[Q/K/V](chapters/21b-why-attention.tex) →
[矩阵式 Self-Attention](chapters/11-softmax-memory.tex) →
[位置与多头](chapters/22a-position-multihead.tex)。

### V：Transformer 训练（第 21–26 章）
[Block](chapters/22-transformer-architecture.tex)、
[FFN 与输出头](chapters/10b-ffn-output-head.tex)、
[贯通前向](chapters/22b-token-to-output.tex)、
[联合训练](chapters/22c-language-training.tex)、
[生成](chapters/23-llm-systems.tex)、
[从玩具到 GPT-2](chapters/23a-from-toy-to-gpt.tex)。

### VI：Attention 与 FFN 的记忆视角（第 27–30 章）
[外积](chapters/04-key-value-outer-product.tex)、
[串扰](chapters/05-memory-interference.tex)、
[减少干扰](chapters/06-better-linear-memory.tex)、
[矩阵读出](chapters/08-stacking-key-value.tex)、
[非线性与 MLP](chapters/09-nonlinearity-and-memory.tex)、
[高维容量](chapters/13-capacity.tex)。
本部分统一使用行向量；[memory_demo.py](../scripts/memory_demo.py) 验证二维结果。

### VII–VIII：助手与架构判断（第 31–36 章）
VII：[ICL](chapters/23aa-pretraining-icl.tex)、
[后训练](chapters/23c-post-training.tex)、
[Agent/RAG](chapters/23d-agent-systems.tex)、
[部署](chapters/23b-deployment-and-ecosystem.tex)。

VIII：[现代 Transformer](chapters/22d-modern-transformers.tex)、
[新技术判断](chapters/23e-tech-judgement.tex)、
[技术底座回顾](chapters/23f-foundation-recap.tex)。

### IX：视觉选读（第 37–38 章）
[CNN](chapters/19-cnn.tex) → [ViT](chapters/19b-vit.tex)。

## 附录 A–G

A · [公式和数学](chapters/00e-core-formulas.tex)；
B · [三维数值与实验](chapters/00f-transformer-intermediates.tex)；
C · [综合练习](chapters/25-integrated-practice.tex)；
D · [集中答案](chapters/27-answer-key.tex)；
E · [术语](chapters/24-lexicon.tex)；
F · [参考文献](chapters/26-sources.tex)；
G · [版本与复现](chapters/29-revision-notes.tex)。

这份目录属于正在修订的 \`main\`，不是正式发布版本清单。

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

正式回归 CI 检查图注父子结构、超宽盒子和标题层级，防止这些已修复问题再次出现。公式 MathML 已在正式构建中启用，并以 `scripts/validate_mathml_af.py` 对 1,472 个公式的关联文件逐一验收；后续保留结构、MathML-AF 与 PDF/UA-2 的自动化回归检查，不再安排屏读测试或人工无障碍验收；详见仓库根目录的 [自动化验收说明](../docs/ACCESSIBILITY.md)。
