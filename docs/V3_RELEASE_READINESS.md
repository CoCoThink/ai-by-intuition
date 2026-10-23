# V3 修订候选：发布前验收与人工签核

> **状态：39 章修订的机器基线已通过；人工逐页审校、来源授权和发布签核未完成。**
> 当前正式 Release 仍是 [v0.1.0](https://github.com/CoCoThink/ai-by-intuition/releases/tag/v0.1.0)。
> 本页仅用于 V3 候选；[V2 的历史验收](V2_RELEASE_READINESS.md)不应被当作当前版本的证据。

## 可追溯机器基线（不是持续自动有效的状态）

| 项目 | 成功验证的明确来源 |
|---|---|
| 源码 SHA | [36e37ff15417f35085bd3bbf9b616ae2ea3f41c9](https://github.com/CoCoThink/ai-by-intuition/commit/36e37ff15417f35085bd3bbf9b616ae2ea3f41c9) |
| 成功的 main 构建 | [Build one PDF book #39895186456](https://github.com/CoCoThink/ai-by-intuition/actions/runs/39895186456) |
| 内容结构 | 9 部分、39 个编号章节、A–G 共 7 个附录 |
| PDF | **135 页** Tagged PDF；页面文字边界检查通过 |
| Formula | **1,957 / 1,957** 具有可解析的 MathML-AF 关联 |
| MathML | 1,209 份不同的 MathML 文档 |
| veraPDF | PDF/UA-2 **compliant=true、failedRules=0、failedChecks=0** |
| 源码与数值 | 62 个章节输入文件、联合训练、独立 Q/K、Delta 写入与教学脚本回归通过 |
| 审计资产 | 此次 CI 的 \`ai-by-intuition-book\` 和 \`pdfua2-machine-audit\` |

**重要：上述机器数字仅对该 SHA 的 PDF 有效。**
任何在此之后对 \`book/\`、\`scripts/\` 或构建配置的修改，
必须以新 SHA 的成功全量工作流重新验收；本文件不得自行宣称后续主分支已通过。

## 当前 135 页版本的灰度技术预检

已从同一 SHA 的 [成功构建 #39895186456](https://github.com/CoCoThink/ai-by-intuition/actions/runs/39895186456)
下载 PDF，确认实际为 135 页；以灰度渲染工具生成 **135／135 页**图片，
并抽查第 19、29、34 章以及练习、术语和版本附录的代表页。
缩略校样未发现整页丢失或大幅裁切，**尚未完成全书高分辨率人工审校**。
这个技术预检不能代替作者核对正文细线对比、替代文本质量、屏读顺序及版权许可。

## 旧版灰度渲染预检（不等于当前人工审阅）

之前已对 [CI #39890022919](https://github.com/CoCoThink/ai-by-intuition/actions/runs/39890022919)
所生成的 **131 页 PDF** 使用 \`scripts/print_proof.py --all --scale 430\`
完成 **131／131 页**灰度图片生成，并浏览了按页码排序的六组缩略总览。
旧 131 页基线的技术预检未发现整页丢失或明显的大幅裁切；当前 135 页 PDF 仍需另行人工逐页审校。

**本记录不构成人工逐页审校或无障碍体验验收：**
430 像素缩略图无法检查小字号、公式、细线对比度、
屏读顺序及第三方素材授权。正式检查仍需用
[PRINT_PROOF.md](PRINT_PROOF.md) 所示更高分辨率的完整灰度校样
逐页记录审阅者、发现的问题及对应修改提交。

## 尚需人工确认的发布阻断项

- [ ] 运行 [灰度逐页审校](PRINT_PROOF.md)，检查所有页面的阅读顺序、版心、对比度、图形标签、表格、长链接和数学排印，并记录日期及审校者
- [ ] 检查重要图的替代文字是否与实际图示一致；机器检测到替代文字不保证质量充分
- [ ] 完成 [Agent 教学来源与复用核对](ATTRIBUTION_REVIEW.md)，记录必要授权或独立改写依据
- [ ] 通过 [固定版本真实 GPT-2 独立工作流](GPT2_REAL_RUN.md) 获取可追溯的真实输出；只有运行成功时才填入结果，PDF/UA-2 主 CI 与权重下载隔离
- [ ] 选取待发布版本**最终 SHA**，重新运行一次成功的完整 PDF + MathML-AF + PDF/UA-2 工作流
- [ ] 记录作者明确的最终发布签核、版本号与日期，并确认没有未解决阻断问题

机器审计与灰度图不能替代真实屏读设备的用户体验验证；
本项目当前将人工阅读/视觉核对设为发布门槛，
不暗示已经完成真实屏幕阅读器测试。

## 发布与维护

源码目录和修订映射见 [CHAPTER_MAPPING.md](CHAPTER_MAPPING.md)。
发行步骤见 [PUBLISHING.md](PUBLISHING.md)；
正式发布只能使用审核通过、绑定 SHA 的构建工件，
不能直接复用较早成功版本的 PDF 或审计统计。
