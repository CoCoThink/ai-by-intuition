# AI by Intuition · 从函数到 Transformer，再到助手与 Agent

> **先有问题，再有直觉，然后才有公式。**

一本中文 AI 原理教材。全书从“计算机怎样学会生成有用的语言回答？”出发，用一组可以手算、也能用脚本复算的小例子，从函数、损失和梯度一路讲到矩阵、Attention、Transformer 的训练与生成，最后讲清后训练、检索、工具调用和 Agent 系统怎样把模型变成助手。

主线例子是四个 Token“春天 / 花 / 开了 / 。”：三维 Transformer 用 `[2,4,5]` 预测 `[4,5,3]`，一次联合训练把平均损失从 **1.798430** 降到 **1.611377**。数值基线是 [teaching_reference.py](scripts/teaching_reference.py)。

## 获取 PDF

当前维护的是**主分支草稿，尚未发布正式 Release**。从 [Build one PDF book](https://github.com/CoCoThink/ai-by-intuition/actions/workflows/build-latex.yml) 中对应提交的成功运行下载 `ai-by-intuition-book` 工件；同次运行的 `pdfua2-machine-audit` 工件提供机器审计。

仓库不提交编译后的 PDF。

## 全书结构

正文共九部分。前七部分是主线，第八、九部分是主线之后的两条扩展路径；章号由 LaTeX 自动生成，以 [book/main.tex](book/main.tex) 为准。

| 部分 | 回答的问题 |
|---|---|
| 一 · 学习 | 函数怎样从样本、损失和梯度中学出参数？ |
| 二 · 矩阵 | 怎样把许多特征和样本放进向量与矩阵？ |
| 三 · 文字 | Token 怎样变成可训练的数字表示？ |
| 四 · 上下文 | 为什么需要 Attention，Q/K/V 和因果 Mask 各做什么？ |
| 五 · Transformer | Block、FFN、输出头怎样组装、一起训练并逐词生成？ |
| 六 · 助手 | 后训练、测试时计算、RAG、工具、协议和部署怎样分工？ |
| 七 · 架构 | RoPE、GQA、MoE、KV Cache 改了哪一步，怎样判断值不值得？ |
| 八 · 视觉（扩展） | CNN 和 ViT 怎样把图像接到同一个 Transformer 主干？ |
| 九 · 联想记忆（扩展） | 外积、串扰和 Delta 规则怎样从“存入与取出”重看 Attention？ |

附录 A–G 依次是公式与符号速查、三维实验与复算脚本、按章题库与累积复习、参考答案、术语表与索引、来源、版本与带日期断言。源码与章节的对应见[源码导览](CONTRIBUTING.md#源码导览)。

## 本地构建

在仓库根目录运行 `bash scripts/build_book.sh`，产物为 `book/build/main.pdf`，版权页和附录 G 自动印出当前 Git 提交号。环境准备和检查命令见[构建说明](CONTRIBUTING.md#本地构建)。

## 修改与反馈

写作约定、源码对照、生成器、构建检查和发布流程统一见[编写与维护指南](CONTRIBUTING.md)。阅读中遇到问题，请通过 [Issues](https://github.com/CoCoThink/ai-by-intuition/issues) 反馈，并注明 PDF 提交号、章节及复算步骤。

## 开放许可证与转载

**教材与阅读材料：** 本仓库的原创 `book/` 教材正文、LaTeX 排版源码、TikZ 教学图、仓库说明文档及由这些源码构建的 **AI by Intuition** PDF，以 [Creative Commons Attribution 4.0 International（CC BY 4.0）](LICENSE) 授权。允许复制、修改、翻译及商业使用，须按许可要求署名、提供许可证链接并标明修改；本许可不要求衍生作品沿用相同许可证。

**软件与自动化：** `scripts/` 下的 Python 工具及 `.github/workflows/` 下的 GitHub Actions 工作流，以 [MIT License](scripts/LICENSE) 授权。复用代码时应保留 MIT 版权与许可声明。

**建议署名：** AI by Intuition · CoCoThink and contributors；项目地址：<https://github.com/CoCoThink/ai-by-intuition>；许可：[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)。改编或翻译时请注明变更。以上许可只覆盖项目权利人拥有或有权授权的原创部分；引用的第三方文本、图像、品牌及依赖库仍受各自权利或许可约束。

本授权同样覆盖本仓库历史版本中项目有权授权的内容。

## 启发与参考

- 飞天闪客：[《一小时从函数到 Transformer》](https://www.bilibili.com/video/BV1NCgVzoEG9/)、[《一小时从 Transformer 到大模型》](https://www.bilibili.com/video/BV15z4C6SEHT/)
- Alex Wang：[You could have invented transformers from memory](https://alexwang.ai/posts/associative-memory/)
- Vaswani et al.：[Attention Is All You Need](https://arxiv.org/abs/1706.03762)

这些资源启发了选题和讲解路径；教材按学习依赖重新组织，文字、图表、数值例题和实验独立编写。完整来源见附录 F。
