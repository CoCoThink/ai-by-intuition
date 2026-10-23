# 07b368c：144 页 PDF 校验与定向排版回归

> **机器验证通过；人工高清逐页、真实屏读、第三方授权与发行签核尚未完成。**
> 仅对应下列成功 Actions 工件，未采用失败构建或推测页码。

| 证据项 | 已核实的值 |
| --- | --- |
| 源码提交 | [`07b368c3c2c8d7e1c597fe88dddaf3cf20ac8650`](https://github.com/CoCoThink/ai-by-intuition/commit/07b368c3c2c8d7e1c597fe88dddaf3cf20ac8650) |
| 完整构建 | [Build one PDF book #39929702902](https://github.com/CoCoThink/ai-by-intuition/actions/runs/39929702902)：success |
| PDF | `ai-by-intuition-book` 工件中的 `AI-by-Intuition-Book.pdf` |
| PDF SHA-256 | `1d8c85eb3d6ee3ed84994cf1ed8f9d21e0a6c97c7791180327150bf56f7290b6` |
| 结构 | 9 部分、39 章、A–G 七附录、63 个章节输入 |
| Tagged PDF | **144 页** |
| MathML-AF | **2,366／2,366** 公式关联；1,305 份 MathML 文档 |
| PDF/UA-2 | veraPDF `compliant=true`、`failedRules=0`、`failedChecks=0` |
| 灰度机检 | **144／144** 页渲染；`blank_suspects=[]`、`edge_touch_suspects=[]` |
| 最低墨量 | 第 114 页，深色比例 **3.5198%**，高于 0.5% 近空白阈值 |
| 人工高分辨率及屏读测试 | **未签核** |

上表 PDF 哈希用成功 ZIP 内 PDF 的实际字节计算，且与该成功 CI
`pdfua2-machine-audit/grayscale-audit.json` 的 `pdf_sha256` 完全一致。
这份审计在自动写入源码 SHA 与运行号功能实施前生成，
所以提交和运行编号来自 Actions 页面；不把后来新加的 JSON 字段假装为原工件内容。

## 第 11、15 章的实际物理结尾页

| 显示章号 | 物理页 | 书签定位的定向检查 | 结果 |
| --- | --- | --- | --- |
| 11：MLP／训练工程 | 29 | 完整训练算例、自测与小结位于章末同页，页内正文不少于 260 汉字 | 通过 |
| 15：任务契约 | 37 | 预测目标、三层自测与小结位于章末同页，页内正文不少于 260 汉字 | 通过 |

以上来自本次 `scripts/validate_book.py --pdf` 在实际 PDF 上运行的检查。
此外对这 144 页 PDF 的 39 个章首书签与定位条作了本地几何排查：
**39／39 章**的定位条在对应标题的同一物理页。
第 13 章的定位条在约 **604／842 pt** 的高度，仍有正文空间；
此项检查已准备并入后续机器回归，不能冒充原构建当时执行的校验。

## 严格发布边界

物理页灰度初筛只检测接近空白及边缘触墨，不检查微小公式、
行间阅读次序或第三方表达许可；作者仍须按
[人工审阅协议](SCREEN_READER_ACCEPTANCE.md)、[灰度校样](PRINT_PROOF.md)、
[来源比对表](AGENT_SOURCE_EVIDENCE.md)完成最终签核。
