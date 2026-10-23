# AI by Intuition · 从函数到 Transformer 的直觉之旅

> **先有问题，再有直觉，然后才有公式。**

一本从**“计算机怎样学会生成有用的语言回答？”**出发的中文 AI 原理教程。我们先解释为什么可以用原始文本构造“预测下一个 Token”的训练题——**它是学习语言规律的一种具体方法，不是 AI 的终极目标**——再从函数、向量、矩阵和 MLP 出发，走到反向传播、RNN、Attention、Transformer 的训练与生成。最后解释模型为什么还需要后训练、检索、工具以及部署系统。

**读者阅读一个完整 PDF，作者维护分开的 LaTeX 章节源码。** 最新验证构建采用 **TeX Live 2026 + LuaLaTeX**，生成带结构标签的 PDF。

[**下载正式版 PDF · v0.1.0**](https://github.com/CoCoThink/ai-by-intuition/releases/tag/v0.1.0) · [新版发布流程](docs/PUBLISHING.md) · [全书顺序与可点击目录](book/README.md) · [学习路线设计](ROADMAP.md) · [无障碍现状及验收](docs/ACCESSIBILITY.md) · [最新构建工件](https://github.com/CoCoThink/ai-by-intuition/actions/workflows/build-latex.yml)

## 主分支修订候选（尚未发布）

**v0.1.0 的正式 Release 不变。**
当前 \`main\` 根据 [REVIEW.md](docs/REVIEW.md) 已建立
**九部分、39 章、A–G 附录**的新目录：I–VIII 为必读主线，
IX 为视觉选读。原联想记忆选读已统一行向量并升为第 VI 部分，
朴素点积 Attention 已独立成章；RAG、Agent、BPE 也有可复算新例。

修订候选已存在可追溯的[成功全量 PDF/UA-2 构建 #39913269593](https://github.com/CoCoThink/ai-by-intuition/actions/runs/39913269593)
（对应 `3800ab9`、143 页、2,134／2,134 个公式关联）。
**这只是该提交的机器基线，后续修改仍需重新验收，作者人工审校和发行签核未完成。**
请参见 [V3 发布前验收](docs/V3_RELEASE_READINESS.md)与
[灰度逐页校样流程](docs/PRINT_PROOF.md)。
具体参见 [修订映射](docs/CHAPTER_MAPPING.md)、
[实际章节顺序](book/README.md) 与
[最新 PDF 构建](https://github.com/CoCoThink/ai-by-intuition/actions/workflows/build-latex.yml)。
原 V2 候选的历史成功构建
[39816203928](https://github.com/CoCoThink/ai-by-intuition/actions/runs/39816203928)
仅对应当时提交 \`2cad92cd\`，不是本次修订版的正式发布证据。

## 开放许可证与转载

**教材与阅读材料：** 本仓库的原创 `book/` 教材正文、LaTeX 排版源码、TikZ 教学图、仓库说明文档及正式发布的 **AI by Intuition** PDF（包括 v0.1.0）以 [Creative Commons Attribution 4.0 International（CC BY 4.0）](LICENSE) 授权。允许复制、修改、翻译及商业使用，须按许可要求署名、提供许可证链接并标明修改；本许可不要求衍生作品沿用相同许可证。

**软件与自动化：** `scripts/` 下的 Python 工具及 `.github/workflows/` 下的 GitHub Actions 工作流，以 [MIT License](scripts/LICENSE) 授权。复用代码时应保留 MIT 版权与许可声明。

**建议署名：** AI by Intuition · CoCoThink and contributors；项目地址：<https://github.com/CoCoThink/ai-by-intuition>；许可：[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)。改编或翻译时请注明变更。仅对项目权利人拥有或有权授权的原创部分授予以上许可；引用的第三方文本、图像、品牌及依赖库仍受各自权利或许可约束，引用链接本身不构成再授权。

**版本说明：** v0.1.0 于加入许可证前发布，历史 Release 资产和当时的说明保留原样；本次授权同样覆盖本项目有权授权的该版本 PDF。后续 PDF 应随发布说明一并提供许可与署名信息。

## 为什么这样组织？

| 部分 | 从上一步留下的问题 |
|---|---|
| I · 学习 | 函数怎样从样本、损失和梯度中学出参数？ |
| II · 多维计算 | 怎样把许多特征和样本放进矩阵？ |
| III · 文字 | Token 怎样进入可训练的数字表示？ |
| IV · 上下文 | 朴素点积有何限制，为什么要引入 Q/K/V？ |
| V · Transformer | 如何组装 Block、FFN、输出头并共同训练？ |
| VI · 关联记忆 | 外积、串扰、MLP、线性状态如何连成一条主线？ |
| VII · 助手与 Agent | 后训练、检索、工具、权限和部署分别解决什么问题？ |
| VIII · 架构判断 | 怎样权衡长上下文、KV Cache、效率与质量？ |
| IX · 选读视觉 | CNN、ViT 如何处理图片表示？ |

附录 A–G 包含数学与形状、复算实验、练习、答案、术语、文献、版本与勘误。
三维主例仍用 \`[1,3,4]\` 预测 \`[3,4,2]\`；
一次联合训练的损失为 **1.798430 → 1.611377**。
[teaching_reference.py](scripts/teaching_reference.py) 是主例数值的唯一基线，
二维记忆、Agent 与 BPE 均独立标注，不能混用参数。

## 最新 PDF 与构建状态

**v0.1.0 已于 2026-10-22 正式发布。** [主分支全量 CI #39699805713](https://github.com/CoCoThink/ai-by-intuition/actions/runs/39699805713) 通过，生成 **99 页 Tagged PDF**，检测到 **1,472 个公式节点、21 张表格（59 个 TH 表头单元格）、16 个 Figure 及 16 处替代文字、48 个 H1 和 180 个 H2**，并通过章节、数值、页面边界及机器无障碍验证。请从 [正式 Release（PDF、SHA256SUMS、审计工件）](https://github.com/CoCoThink/ai-by-intuition/releases/tag/v0.1.0) 下载归档版；仓库不提交编译后的 PDF。

**PDF/UA-2 与 MathML 机器验收均已通过：**正式构建使用 `mathml-AF`，CI 验证 **1,472 个 Formula 均带有效的 MathML 关联文件**（933 种不同内容），veraPDF 1.30.2 的 PDF/UA-2 检查报告零失败。两项检查都阻断不达标的 PDF 发布。**项目仅设置自动化验收门槛**：持续检查 PDF/UA-2、MathML-AF、结构标签和页面布局；真实屏读体验测试与人工无障碍验收不列入待办。机器检查的通过仅代表验证工具覆盖的规则，详见[自动化验收说明](docs/ACCESSIBILITY.md)。

## 本地编译

推荐使用 **TeX Live 2026、LuaLaTeX**，安装中文/西文字体 **Noto Serif CJK SC、Noto Sans CJK SC、Noto Serif、Noto Sans**，并具备 `latexmk`、TikZ/PGF、`poppler-utils` 和 `pypdf==5.9.0`。CI 选择 TeX Live 2026 并固定执行 Action 的 commit SHA，但 TeX Live 基础镜像和 apt 软件包尚未达到字节级冻结；详见[构建复现说明](docs/BUILD-REPRODUCIBILITY.md)。旧版本内核不保证能正确处理 Tagged PDF。

```bash
python3 scripts/validate_book.py
cd book
latexmk -lualatex -interaction=nonstopmode -halt-on-error -file-line-error -outdir=build main.tex
cd ..
python3 -m pip install pypdf==5.9.0
python3 scripts/validate_book.py --pdf book/build/main.pdf
```

PDF 生成于 `book/build/main.pdf`；如需复现带中文、数学、`tabularx` 和 TikZ 的最小测试，请参阅 [book/README.md](book/README.md)。常见贡献流程参阅 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 原视频与研究参考

- [飞天闪客：《一小时从函数到 Transformer》](https://www.bilibili.com/video/BV1NCgVzoEG9/)
- [飞天闪客：《一小时从 Transformer 到大模型》](https://www.bilibili.com/video/BV15z4C6SEHT/)
- [Alex Wang：You could have invented transformers from memory](https://alexwang.ai/posts/associative-memory/)
- [Attention Is All You Need](https://arxiv.org/abs/1706.03762)

视频启发了选题和问题意识；教材根据学习依赖重新安排内容，不按分集照抄。更多引文见 [参考与延伸阅读](book/chapters/26-sources.tex)。

欢迎通过 Issue 提供计算核对、未解释的符号及跨章衔接建议。转载、改编及代码复用请遵循上文按目录划分的授权范围。
