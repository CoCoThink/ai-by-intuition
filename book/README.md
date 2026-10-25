# 全书阅读顺序 · AI by Intuition

**唯一入口：** [book/main.tex](main.tex)。读者只需要阅读一个 PDF；
源码按章节维护，正文编号由 LaTeX 自动生成，目录与书内引用应以编译 PDF 为准。

**教材授权：** 本书原创文字、LaTeX/TikZ 图形与正式 PDF（包括 v0.1.0）采用 [CC BY 4.0](../LICENSE)；Python 工具和 GitHub Actions 工作流采用 [MIT](../scripts/LICENSE)。转载、翻译或商业使用应署名及标明改动；第三方引用仍遵循其原有许可。详情见 [仓库许可说明](../README.md#开放许可证与转载)。

**从这里开始：**[目录后的阅读路线与表示约定](chapters/00g-reading-routes.tex)及[版权页](chapters/00h-colophon.tex)；必读主线结束后有[终章：回到那四个 Token](chapters/23f-foundation-recap.tex)。[勘误与版本记录](../docs/ERRATA.md)持续更新。

## 当前目录：九部分、41 章、附录 A–G

章节顺序、自动章号与附录定位以 [main.tex](main.tex) 为准。视觉桥接位于 Transformer 之后，联想记忆为第九部分；终章位于联想记忆部分之后，回顾全书。

| 部分 | 章节和源码 |
|---|---|
| I · 学习与训练 | [函数](chapters/00-functions.tex)、[损失与梯度](chapters/16-loss-gradient.tex)、[训练组织](chapters/18c-training-engineering.tex)、[反传](chapters/17-backpropagation.tex)、[泛化](chapters/18-generalization.tex) |
| II · 向量与矩阵 | [向量](chapters/01-vectors.tex)、[点积](chapters/02-dot-product.tex)、[矩阵](chapters/03-matrix-multiplication.tex)、[MLP](chapters/10-mlp.tex) |
| III · 文字与 Token | [Tokenizer](chapters/20a-tokenizer.tex)、[分类损失](chapters/20c-classification-loss.tex)、[Embedding](chapters/20-embeddings.tex)、[任务契约](chapters/20b-task-contract.tex) |
| IV · 上下文 | [RNN](chapters/21-rnn.tex)、[Q/K/V](chapters/21b-why-attention.tex)、[Self-Attention](chapters/11-softmax-memory.tex)、[位置与多头](chapters/22a-position-multihead.tex) |
| V · Transformer | [Block](chapters/22-transformer-architecture.tex)、[FFN](chapters/10b-ffn-output-head.tex)、[贯通前向](chapters/22b-token-to-output.tex)、[联合训练](chapters/22c-language-training.tex)、[生成](chapters/23-llm-systems.tex)、[玩具到 GPT](chapters/23a-from-toy-to-gpt.tex) |
| VI · 视觉桥接 | [CNN](chapters/19-cnn.tex) → [ViT 与多模态](chapters/19b-vit.tex) |
| VII · 助手与 Agent | [ICL](chapters/23aa-pretraining-icl.tex)、[后训练](chapters/23c-post-training.tex)、[测试时计算](chapters/23cc-test-time-compute.tex)、[RAG](chapters/23d-agent-systems.tex)、[Agent loop](chapters/23d-agent-tools.tex)、[协议与多 Agent](chapters/23d-agent-protocols.tex)、[部署](chapters/23b-deployment-and-ecosystem.tex) |
| VIII · 架构与判断 | [现代 Transformer](chapters/22d-modern-transformers.tex)、[评测与技术判断](chapters/23e-tech-judgement.tex) |
| IX · 联想记忆 | [外积与串扰](chapters/04-key-value-outer-product.tex)、[Delta 更新](chapters/06-better-linear-memory.tex)、[非线性读取](chapters/09-nonlinearity-and-memory.tex)、[容量](chapters/13-capacity.tex) |

**附录 A–G**：公式、实验、按章题库、参考答案、术语、文献与勘误。

章节间跨引优先采用 `\\label`／`\\ref`，而非写死章号。 CI 在编译前运行 `scripts/check_chapter_crossrefs.py`，拦截写死的“第 N 章”，另由 `scripts/check_part_references.py` 禁止包括“第 VI 部分／第六部分／第6部分”在内的硬编码部分编号，并检查九个 `part:` 标签与实际部分标题、顺序匹配，并依 `main.tex` 的实际 `\\section` 顺序逐项校验附录 D 的章号；编译后仍由 `check_latex_references.py` 拦截未解析引用与 PDF 的 `??`。正文所有算例和教学实验仍以三维贯通参考脚本为数值基线。自测答案详解保留在附录 D，并按正文编号及提高专题排列。

## 自测题与答案的分步阅读

**每章一个自测块，共 42 组**。正文只印题目，提示统一放在[附录 D.2](chapters/28-chapter-checks.tex)的“第一步”中，再展开解题过程。四对重复自测已合并，保留全部问题；一般章有三题，四个合并章有六题。每组保留唯一 `check:` 和 `answer:` 锚点。

附录 C 含 **104 道按章练习（C-001 至 C-104）和 18 道独立累积复习（R-01 至 R-18）**，逐题印难度、预计耗时和入口页码。R 题按部分分组，不再列入末章题号。题目、解答、章末导航和部分末复习都从 [exercises.json](exercises.json) 生成；编辑后依次运行 `scripts/generate_exercise_bank.py` 和 `scripts/generate_chapter_navigation.py`，CI 以 `--check` 验证。旧题号只作隐藏锚点，源码和成品 PDF 均拦截可见旧编号，并检查链接显示的题号是否与实际目标一致。

纸面目录仅列到章，控制在两页内；PDF 书签仍提供全部小节导航。自测允许接排和跨页，避免整块自测、小结被挤成稀疏尾页。

正文的教学词表 ID、位置与数学行列从 1 起，五项是“其他、春天、。、花、开了”；Python 索引减 1。数学符号统一为输出头 `W_out`、logits `Z`、词表概率 `Π`、位置 `P_pos` 与记忆状态 `𝓜`，脚本接口名在附录 A 对照。

新增的 `scripts/check_book_contract.py` 检查**引用用途**（第十步必须依次指向训练与生成）、每章唯一自测、题答对应、符号与帽子作用域、逐条 UTC 来源日期及生成题库。索引锚点还需紧随对应小节，防止继承枚举项号；图中配色与文字说明共同检查。`scripts/check_teaching_claims.py` 复算缓存字节、简化残差梯度、同 Token 上下文消融、带干扰的 Q/K 选择性和二维完整反传；已有 PDF 标签、MathML、引用、版面和 PDF/UA-2 检查继续运行。

第 24.10 节的第二级对照可用 `python3 scripts/attention_selection_demo.py` 独立复算：均匀读取损失为 `ln 2`；训练 Q/K 后约 `0.000502`，查询改变时重点读取的记录随之改变。脚本还会交换记录顺序、测试未见过的值组合，并逐项核对十个参数的梯度。

测试时计算的概率、候选相关性和核验器反例可用 `python3 scripts/test_time_compute_demo.py` 复算，无须安装额外依赖。

## 一次构建，一本 Tagged PDF

CI 使用 **TeX Live 2026 + LuaLaTeX**，启动时要求 Noto 中文及西文字体。可以从仓库根目录先检查源码，再构建整本书：

```bash
# 中文索引由双语术语表生成；先生成，避免直接编译占位页
python3 -m pip install pypinyin==0.55.0
python3 scripts/generate_chinese_index.py
python3 scripts/generate_exercise_bank.py --check
python3 scripts/generate_chapter_navigation.py --check
python3 scripts/validate_book.py
bash scripts/build_book.sh
python3 -m pip install pypdf==5.9.0
python3 scripts/validate_book.py --pdf book/build/main.pdf
```

生成文件为 `book/build/main.pdf`。构建脚本自动读取当前 Git 提交并写入版权页和附录 G；CI 显式传入构建提交号。脱离 Git 的源码包没有提交号时，整句来源说明自动省略。已发布的正式 PDF 从 [v0.1.0 Release](https://github.com/CoCoThink/ai-by-intuition/releases/tag/v0.1.0) 下载；未来新版本通过显式版本号和已通过的构建发布。CI 的成功运行只上传一份 `ai-by-intuition-book` PDF 工件及一份机器审计，具体从 [GitHub Actions](https://github.com/CoCoThink/ai-by-intuition/actions/workflows/build-latex.yml) 获取。

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

**中文检索：**附录 E 还提供 149 项按拼音排序的中文索引，附正文页码链接。首次本地构建前运行 `python3 -m pip install pypinyin==0.55.0` 和 `python3 scripts/generate_chinese_index.py`；CI 会自动生成索引并核对术语表实际条目数与全部链接；标题总数从规范术语表生成。

中文分词实测：`python3 scripts/chinese_tokenizer_demo.py --real` 下载固定修订的 Qwen2.5-0.5B 分词器并校验 SHA-256，不加载模型权重。需要 `tokenizers==0.22.1`。归纳读取与优势到 logits 的更新由 `python3 scripts/icl_policy_demo.py` 复算，需 NumPy。

附录 F 的二维码与网页参考索引由 `python3 scripts/generate_reference_assets.py` 从核验清单生成，需要 `qrcode==8.2`；CI 用 `--check` 比对两项产物。二维码是 TikZ 矢量路径，不依赖位图或 LaTeX 二维码宏的嵌套段落标签。

## 本轮开篇与导航修订

第 1–3 章补充双参数直接求解、迭代表及步长稳定区间；第 26 章专注规模和真实分词，数据工程移入训练系统章。参见 [完整修订记录](../docs/REVIEW-OPENING-AND-NAVIGATION.md)。目录标题、页码和章末答案均可点击；CI 检查实际目的页、双向答案链接与图/图题同页。术语的主要位置在附录 E，全部出现章节另见 [自动索引](../docs/TERM_OCCURRENCES.md)。
