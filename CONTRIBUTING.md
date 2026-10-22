# 参与改进 AI by Intuition

目标是让没有系统学习过高等数学的读者也能真正理解 AI 中的矩阵计算和推导，而不是只记住术语。

## 内容原则

- 先展示一个可手算的二维例子，再给一般数学形式。
- 首次出现矩阵乘法时，写出逐行与逐列的计算过程。
- 明确输入、输出、矩阵尺寸与每一维的含义。
- 区分等式、近似、启发式解释与实际模型。
- 不使用「神经元必然对应单条事实」一类过度简化表述。
- 引用原作者和研究结论，并尽量提供原始参考链接。

## 目录与编译

新增教程文件写入 `book/chapters/NN-name.tex`，并将 `\input{chapters/NN-name}` 加入 `book/main.tex` 的正确阅读顺序。主线保留五个必读部分，CNN 与联想记忆分别位于第六、七选读部分；练习和答案集中到附录。

全书唯一 PDF 由 `book/main.tex` 使用 **TeX Live 2026 + LuaLaTeX** 构建。安装 `latexmk`、Noto 中文/西文字体、`poppler-utils`、相应 TeX Live 宏包后，从仓库根目录运行：

```bash
python3 scripts/validate_book.py
cd book
mkdir -p build/smoke
latexmk -lualatex -interaction=nonstopmode -halt-on-error -file-line-error -outdir=build/smoke smoke-tagging.tex
pdfinfo build/smoke/smoke-tagging.pdf | grep '^Tagged:'
latexmk -lualatex -interaction=nonstopmode -halt-on-error -file-line-error -outdir=build main.tex
cd ..
python3 -m pip install pypdf==5.9.0
python3 scripts/validate_book.py --pdf book/build/main.pdf
```

不要单凭 `pdfinfo` 的 `Tagged:` 行宣布无障碍合规：最后一步还会检查 PDF 结构树、公式及图像节点、目录、正文内容与文字边界。相关背景见 [无障碍现状和验收清单](docs/ACCESSIBILITY.md)。

请勿逐章提交 PDF，也勿提交 LaTeX 中间文件。CI 每次完整成功构建只上传**一个**正式 PDF 工件；已发布版本则从 [GitHub Release](https://github.com/CoCoThink/ai-by-intuition/releases/tag/v0.1.0) 获取 PDF 与 SHA256SUMS。仅编辑 Markdown 文档时会运行轻量的站内 Markdown 链接检查，不会强制编译整本书。所有 `scripts/**/*.py` 验证脚本改动将触发完整 PDF CI；也可在 GitHub Actions 手动运行 `workflow_dispatch`。依赖固定与构建审计见 [构建复现说明](docs/BUILD-REPRODUCIBILITY.md)，出版版本流程见 [出版检查清单](docs/PUBLISHING.md)。

## 图形与内容验收

- 每次修改公式，核对维度、样例数字和最终答案，并运行 `scripts/validate_book.py`。
- 新增有语义的 TikZ 图时，补充中文替代文字，并由结构检查确认 `/Figure` 与 `/Caption` 的嵌套关系。
- 新增数据表格时设置 `TH` 表头并检查单元格结构；CI 的 veraPDF PDF/UA-2 验证为发布门槛。
- 不要随意删除 `\DocumentMetadata`、回退编译引擎，或重新使用旧版 `latex-lab-testphase-table` 兼容补丁。
- 图表和文字不得超出版心；复杂页面仍需人工目视检查。

## Issue / PR

优先报告：哪一段无法理解、跳过了哪个步骤、某次形状检查是否有问题。提交 PR 时请写明你改进了哪一种初学者困惑，附上手算核验步骤，并确认 LuaLaTeX 构建与相关验收可通过。

## 贡献与许可

项目采用双许可证：教材正文、LaTeX/TikZ、文档及正式 PDF 依照 [CC BY 4.0](LICENSE)；`scripts/` Python 工具及 `.github/workflows/` 工作流依照 [MIT](scripts/LICENSE)。具体范围和建议署名见 [README](README.md#开放许可证与转载)。

提交 PR 前请确认自己有权按对应许可证贡献原创内容与代码；引用第三方材料时标明来源和原始许可，未经授权的内容不要混入可再授权的项目文件。修改教材时保留必要的署名和变更说明，修改软件时保留适用的 MIT 许可和版权声明。
