# V3 候选 143 页灰度技术预检（SHA 固定）

> **性质：已完成的机器渲染和技术筛查；未完成发行人工逐页校样。**
> 本文件只描述以下已成功构建的**原始 PDF**，不能沿用到更晚的源码提交。

## 证据与复现口径

| 字段 | 本次记录 |
| --- | --- |
| 源码 SHA | [`3800ab9e2470939db7b93f047bebfd0176556e7a`](https://github.com/CoCoThink/ai-by-intuition/commit/3800ab9e2470939db7b93f047bebfd0176556e7a) |
| 构建 | [Build one PDF book #39913269593](https://github.com/CoCoThink/ai-by-intuition/actions/runs/39913269593)（成功） |
| 原始 PDF | `ai-by-intuition-book` 工件内的 `AI-by-Intuition-Book.pdf` |
| PDF SHA-256 | `ce67b0bfdd9aaf361ed7ade53eaf9c208ca8f96887873e8961c1525ced46b2a7` |
| 页数 / 页面大小 | **143 页 / A4** |
| 机器无障碍基线 | 2,134/2,134 MathML-AF；PDF/UA-2 failedChecks=0 |
| 灰度技术处理 | **143/143 页**全部以 500px 最大边渲染；阈值深灰像素小于 220/255 |
| 粗略“近空页”阈值 | 灰度深像素比例低于 0.5% |
| 粗略“像素贴边”阈值 | 灰度图边缘 4px 内有超过 4 个深色像素 |

## 运行结果

- 143 页全部可以由 Poppler 渲染；PDF 元数据和 PyMuPDF 读取的页数一致。
- 所有页深灰像素比例至少 **2.2435%**，因此近空页嫌疑：**0 页**。
- 500px 灰度渲染图，四周 4px 中未发现深色内容贴边；此项嫌疑：**0 页**。
- 墨量最少的物理页为 **52**（2.2435%）、**81**（3.3209%）、**113**（3.5209%）；PDF 文本检查均非空白。
- 已制作九组按页码排序的缩略总览，抽看开篇、Transformer 部件／第 22 章流程、现代架构、视觉部分及附录。缩略图未观察到明显的整页缺失或整块裁切。
- **此结论只覆盖上述分辨率和像素规则。** 复杂图的最小字号、灰度反差、文本阅读顺序、标签替代文字是否准确、授权许可和最终作者签核均**尚未完成**。

## 怎样对同一 PDF 复算

先在 [原成功工作流](https://github.com/CoCoThink/ai-by-intuition/actions/runs/39913269593)
下载名为 `ai-by-intuition-book` 的工件，解压 PDF，再按如下命令执行：


```bash
sha256sum AI-by-Intuition-Book.pdf
python3 scripts/audit_grayscale_pdf.py AI-by-Intuition-Book.pdf \
  --scale 500 --json proof-3800ab9.json

# 准备真正可逐页人工复核的高清图片与未勾选检查表：
python3 scripts/print_proof.py AI-by-Intuition-Book.pdf \
  --all --scale 1100 --out-dir proof-3800ab9-human

```

审计脚本独立于人工检查表，只报告机器预检，不会擅自勾选
`CHECKLIST.md` 或将“页面被渲染”写作“作者已审阅”。

## 人工待签核项目

| 位置与重点 | 人工检查内容 | 当前状态 |
| --- | --- | --- |
| P1–P4 封面、目录 | 整机图、标题层级、长链接、页码可辨 | 未人工签核 |
| P52、P81、P113 留白较多页 | 检查是否属于章末自然留白、段落断页是否易读 | 未人工签核 |
| P53–P59 Transformer 图文 | 逐框核对 Encoder、Cross-Attention、FFN 的原理论文映射与小字号 | 未人工签核 |
| P90–P104 现代架构 | 检查复杂表格宽度、窗宽图灰度区分和引文 | 未人工签核 |
| P121–P143 练习、答案和 133 词四列表 | 数学符号、分行、字号、跳转、词条定义和长表页眉 | 未人工签核 |
| 全部 143 页 | 高分辨率阅读顺序、替代文字及屏读体验 | 未人工签核 |
| 来源／版权 | [讲稿来源核对](ATTRIBUTION_REVIEW.md)所列许可和表达复用 | 待作者 |

**发布前决策：不签核。** 准备进入发布流程时，应以最终待发布
源码 SHA 重新生成并审核 PDF；以上记录不可顶替新 PDF 的签核。
