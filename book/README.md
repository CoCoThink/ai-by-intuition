# 全书阅读顺序 · AI by Intuition

**唯一入口：** [book/main.tex](main.tex)。读者只需要阅读一个 PDF；
源码按章节维护，正文编号由 LaTeX 自动生成，目录与书内引用应以编译 PDF 为准。

**教材授权：** 本书原创文字、LaTeX/TikZ 图形与正式 PDF（包括 v0.1.0）采用 [CC BY 4.0](../LICENSE)；Python 工具和 GitHub Actions 工作流采用 [MIT](../scripts/LICENSE)。转载、翻译或商业使用应署名及标明改动；第三方引用仍遵循其原有许可。详情见 [仓库许可说明](../README.md#开放许可证与转载)。

## 七个必读部分（M5 正文合并与排版仍在实施）

### I · 学习是什么：从规则到参数更新
- [阅读指南](chapters/00-guide.tex) → [规则为什么写不尽](chapters/00d-rules-gap.tex) → [函数拟合](chapters/00-functions.tex)
- [损失与梯度](chapters/16-loss-gradient.tex)、[ReLU](chapters/07-functions-relu.tex)、[反向传播](chapters/17-backpropagation.tex)、[四参数训练](chapters/18b-end-to-end-learning.tex)、[泛化](chapters/18-generalization.tex)

### II · 把许多数一起算
- [向量](chapters/01-vectors.tex)、[点积](chapters/02-dot-product.tex)、[矩阵乘法](chapters/03-matrix-multiplication.tex)
- [矩阵 MLP](chapters/10-mlp.tex)、[Mini-batch 与 Adam](chapters/18c-training-engineering.tex)

### III · 让文字进入计算
- [Tokenizer 与 BPE](chapters/20a-tokenizer.tex) → [统一三维 Embedding](chapters/20-embeddings.tex) → [下一 Token 任务和 GPT-2 规模](chapters/20b-task-contract.tex)

### IV · 让词与词交换信息
- [逐 Token MLP 的上下文缺口](chapters/21a-context-gap.tex)、[RNN](chapters/21-rnn.tex)、[为什么需要 Attention](chapters/21b-why-attention.tex)
- [Self-Attention 与因果 Mask](chapters/11-softmax-memory.tex)、[位置与独立双头例](chapters/22a-position-multihead.tex)

### V · 组装并训练 Transformer
- [Pre-Norm Block](chapters/22-transformer-architecture.tex)、[FFN 和输出头](chapters/10b-ffn-output-head.tex)
- [三维完整前向](chapters/22b-token-to-output.tex)、[三位置联合训练](chapters/22c-language-training.tex)
- [自回归生成](chapters/23-llm-systems.tex)、[从三维教学例到 GPT-2](chapters/23a-from-toy-to-gpt.tex)

### VI · 从语言模型到助手
- [预训练与 ICL](chapters/23aa-pretraining-icl.tex)、[SFT／偏好／RLVR](chapters/23c-post-training.tex)
- [季度报告任务中的 RAG、工具、MCP、Agent、A2A](chapters/23d-agent-systems.tex)
- [部署、LoRA、量化与蒸馏](chapters/23b-deployment-and-ecosystem.tex)

### VII · 架构为什么在变，往哪走
- [现代架构的五问](chapters/22d-modern-transformers.tex) → [如何评价新技术](chapters/23e-tech-judgement.tex)

## VIII–IX：两个独立选读专题

- VIII · [CNN 局部卷积](chapters/19-cnn.tex) → [独立 ViT Patch 手算](chapters/19b-vit.tex)
- IX · [外积写入与干扰](chapters/04-key-value-outer-product.tex)、[改善与矩阵读出](chapters/06-better-linear-memory.tex)、[非线性与 Attention 视角](chapters/09-nonlinearity-and-memory.tex)、[高维容量](chapters/13-capacity.tex)。四个显示章节保留原有七个源码的推导和练习，并在开篇说明列向量约定

## 附录 A–E：公式、练习、术语与答案

- A · [核心公式卡](chapters/00e-core-formulas.tex)、[数学速查](chapters/00b-math-tools.tex)与[符号形状](chapters/00c-symbols.tex)
- B · [数学与神经网络迁移题](chapters/25-integrated-practice.tex)、[现代模型与 Agent 迁移题](chapters/25b-modern-practice.tex)、[联想记忆练习](chapters/15-practice.tex)
- C · [100 个基础术语](chapters/24-lexicon.tex)、[现代术语](chapters/24b-modern-lexicon.tex)、[关系图](chapters/24c-concept-map.tex)与[英中索引](chapters/24d-english-index.tex)
- D · [集中参考答案](chapters/27-answer-key.tex)及[分章随堂解答](chapters/28-chapter-checks.tex)
- E · [引用与延伸阅读](chapters/26-sources.tex)

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

生成文件为 `book/build/main.pdf`。已发布的正式 PDF 从 [v0.1.0 Release](https://github.com/CoCoThink/ai-by-intuition/releases/tag/v0.1.0) 下载；未来新版本通过显式版本号和已通过的构建发布。CI 的成功运行只上传一份 `ai-by-intuition-volume-01` PDF 工件及一份机器审计，具体从 [GitHub Actions](https://github.com/CoCoThink/ai-by-intuition/actions/workflows/build-latex.yml) 获取。

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
