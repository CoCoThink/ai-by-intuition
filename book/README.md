# 全书阅读顺序 · AI by Intuition

**唯一入口：** [book/main.tex](main.tex)。读者只需要阅读一个 PDF；
源码按章节维护，正文编号由 LaTeX 自动生成，目录与书内引用应以编译 PDF 为准。

**教材授权：** 本书原创文字、LaTeX/TikZ 图形与正式 PDF（包括 v0.1.0）采用 [CC BY 4.0](../LICENSE)；Python 工具和 GitHub Actions 工作流采用 [MIT](../scripts/LICENSE)。转载、翻译或商业使用应署名及标明改动；第三方引用仍遵循其原有许可。详情见 [仓库许可说明](../README.md#开放许可证与转载)。

## 前五部分：必读主线（M2 过渡编排，新版七部分目标尚未完成）

### I · 学习是什么：从规则到参数更新
- [阅读指南](chapters/00-guide.tex)和[手写规则的局限](chapters/00d-rules-gap.tex)
- [带参数函数](chapters/00-functions.tex)与[损失和梯度下降](chapters/16-loss-gradient.tex)
- [非线性](chapters/07-functions-relu.tex)、[反向传播](chapters/17-backpropagation.tex)、[四参数更新](chapters/18b-end-to-end-learning.tex)、[泛化](chapters/18-generalization.tex)

### II · 把许多数一起算，再让文字进入计算
- [向量](chapters/01-vectors.tex)、[点积](chapters/02-dot-product.tex)、[矩阵乘法](chapters/03-matrix-multiplication.tex)
- [矩阵 MLP](chapters/10-mlp.tex)、[Mini-batch 与 Adam](chapters/18c-training-engineering.tex)
- [Token、ID 与 BPE](chapters/20a-tokenizer.tex)、[统一三维 Embedding 与训练前后图](chapters/20-embeddings.tex)、[下一 Token 任务与 GPT-2 尺度预览](chapters/20b-task-contract.tex)

### III · 让词与词交换信息
- [RNN](chapters/21-rnn.tex) 与 [Attention 的需求来源](chapters/21b-why-attention.tex)
- [从单 Query 到批量 Self-Attention](chapters/11-softmax-memory.tex)，并比较 Linear / MLP / Attention

### IV · 组装、训练并使用 Transformer
- [位置、缩放与双头注意力的数字例子](chapters/22a-position-multihead.tex)
- [Pre-Norm Block、残差图与 LayerNorm](chapters/22-transformer-architecture.tex)
- [FFN 与词表输出头](chapters/10b-ffn-output-head.tex)
- [两个 Token 完整前向计算](chapters/22b-token-to-output.tex)
- [因果训练、输出头与前层参数的梯度更新](chapters/22c-language-training.tex)
- [推理、缓存与生成](chapters/23-llm-systems.tex)

### V · 改进模型并构建可靠应用
- [现代 Transformer 架构](chapters/22d-modern-transformers.tex)
- [后训练与推理策略](chapters/23c-post-training.tex)
- [Agent 系统设计](chapters/23d-agent-systems.tex)
- [量化、蒸馏、LoRA 与部署](chapters/23b-deployment-and-ecosystem.tex)

## 第六、七部分：独立选读专题（不影响必读主线）

- [CNN](chapters/19-cnn.tex)
- [联想记忆与外积](chapters/04-key-value-outer-product.tex)、[记忆干扰](chapters/05-memory-interference.tex)、[改善](chapters/06-better-linear-memory.tex)
- [Key/Value 行列堆叠](chapters/08-stacking-key-value.tex) 与 [非线性记忆](chapters/09-nonlinearity-and-memory.tex)
- [Linear / MLP / Attention 关系](chapters/14-summary.tex)
- [高维容量假设](chapters/13-capacity.tex)

## 附录：练习、查阅与集中解答（建议完成）

- [数学速查](chapters/00b-math-tools.tex)与[符号/张量形状速览](chapters/00c-symbols.tex)（需要时按链接回查，不再挡在学习路线开头）

- [数学与神经网络练习](chapters/25-integrated-practice.tex)
- [现代模型与 Agent 练习](chapters/25b-modern-practice.tex)
- [联想记忆练习](chapters/15-practice.tex)
- [100 词术语地图](chapters/24-lexicon.tex)
- [现代架构术语导航](chapters/24b-modern-lexicon.tex)
- [知识关系图](chapters/24c-concept-map.tex)与[英中文术语 A–Z 索引](chapters/24d-english-index.tex)
- [集中参考答案](chapters/27-answer-key.tex)及[分章随堂自测解答](chapters/28-chapter-checks.tex)：所有题目先做后查
- [参考与延伸阅读](chapters/26-sources.tex)

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

CI 用 `pypdf==5.9.0` 验证 `/MarkInfo /Marked true`、`/StructTreeRoot`、`/Document` 根节点和公式／图像／替代文字节点。最新成功构建含 1,472 个公式节点、21 张表格与 59 个 TH 表头、16 个图像节点及 16 处替代文字、48 个 H1 与 180 个 H2 标题。**当前 PDF 已通过 veraPDF 的 PDF/UA-2 机器验证；实际读屏体验与人工无障碍验收不在项目维护范围。**

### 最小回归测试

`book/smoke-tagging.tex` 检验中文、公式、`tabularx` 和带中文替代文字的 TikZ 图。CI 先构建最小文件并检查 `Tagged: yes`，再构建整本书。手动复现：

```bash
cd book
mkdir -p build/smoke
latexmk -lualatex -interaction=nonstopmode -halt-on-error -file-line-error -outdir=build/smoke smoke-tagging.tex
pdfinfo build/smoke/smoke-tagging.pdf | grep '^Tagged:'
```

正式回归 CI 检查图注父子结构、超宽盒子和标题层级，防止这些已修复问题再次出现。公式 MathML 已在正式构建中启用，并以 `scripts/validate_mathml_af.py` 对 1,472 个公式的关联文件逐一验收；后续保留结构、MathML-AF 与 PDF/UA-2 的自动化回归检查，不再安排屏读测试或人工无障碍验收；详见仓库根目录的 [自动化验收说明](../docs/ACCESSIBILITY.md)。
