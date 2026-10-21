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

请勿逐章提交 PDF，也勿提交 LaTeX 中间文件。CI 会发布**一个**正式 PDF 构建产物。仅编辑 Markdown 文档时，工作流不会自动触发；可在 GitHub Actions 手动运行 `workflow_dispatch`。

## 图形与内容验收

- 每次修改公式，核对维度、样例数字和最终答案，并运行 `scripts/validate_book.py`。
- 新增有语义的 TikZ 图时，在现有图形标签方案下补充准确的中文替代文字，并核查图与图注的阅读顺序。
- 新增表格时检查列标题、合并单元格和读屏语义；“编译成功”不代表表格标签已符合 PDF/UA。
- 不要随意删除 `\DocumentMetadata`、回退编译引擎，或重新使用旧版 `latex-lab-testphase-table` 兼容补丁。
- 图表和文字不得超出版心；复杂页面仍需人工目视检查。

## Issue / PR

优先报告：哪一段无法理解、跳过了哪个步骤、某次形状检查是否有问题。提交 PR 时请写明你改进了哪一种初学者困惑，附上手算核验步骤，并确认 LuaLaTeX 构建与相关验收可通过。

尚未设置开源许可证；版权仍默认保留。后续明确授权后将更新本说明。
