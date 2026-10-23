# 全书灰度校样与人工视觉审校

> **目标：**让彩色教材在黑白打印与低彩度条件下仍可辨识，
> 并让维护者记录字体、表格、图形和引用等机器 QA 不保证的内容。
> 这是 PDF/UA-2 机器审计之外的**人工检查**，不是自动合规认证。

## 生成不改变源 PDF 的校样

需先从 **同一 SHA 对应的成功 CI** 下载 \`ai-by-intuition-book\`，
或在本地按 [构建流程](BUILD-REPRODUCIBILITY.md)产生 \`book/build/main.pdf\`。
本工具只依赖 Python 标准库与 Poppler 的 \`pdfinfo\`、\`pdftoppm\`：

\`\`\`bash
# 默认渲染封面、阅读路线、目录与末页
python3 scripts/print_proof.py book/build/main.pdf \
  --out-dir book/build/print-proof

# 按 PDF 物理页码指定关键跨章区域（页码随版本变化）
python3 scripts/print_proof.py book/build/main.pdf \
  --pages 1-5,65-70,79-90,last --out-dir book/build/print-proof

# 正式出版前逐页检查：所有页面
python3 scripts/print_proof.py book/build/main.pdf \
  --all --out-dir book/build/print-proof --scale 1100
\`\`\`

输出 \`index.html\`（灰度图浏览索引）、\`page-NNN.png\`
（单页图片）与 \`CHECKLIST.md\`（逐页审阅栏）。
命令仅渲染并产生空白检查表，不会自动标记任何人工验收为通过。
按页码重新运行会覆盖同名渲染页；更换 SHA 时建议使用不同输出目录。

## 逐页核对

- **非颜色语义：**Q/K/V、梯度正负、掩码可见与否必须仍有字母、数值、箭头形状或位置提示，不能仅靠颜色
- **字形与排版：**中文与上下标可读，粗体括号无异常空白，公式与长 URL 不溢出，不出现 \`.notdef\` 缺字形
- **图表：**表头与单位可见，灰度对比仍能看出不同线型与连接关系，图注／替代文字表达主要信息
- **目录与引用：**印刷章号、附录字母、脚本路径及来源网址与本次编译版本相符
- **阅读连续性：**跨页段落与图表不产生难以辨认的断裂；同一例子的题目、复算路径和答案能追溯

## 实施和证据保留

将审阅时间、审阅者、审阅所对应的 **完整 commit SHA、构建 ID、实际 PDF**、
标注截图和问题处理提交记录写入此步骤的检查表；
不能只记录“检查过了”或沿用更早 PDF 的审核结论。

技术机器审计仍按 [ACCESSIBILITY.md](ACCESSIBILITY.md) 执行。
作者或维护者在 [V3 发布验收](V3_RELEASE_READINESS.md)
勾选最终人工审核完成后，才具备进入发行签核的条件。
