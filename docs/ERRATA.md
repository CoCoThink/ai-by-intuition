# AI by Intuition · 勘误与版本记录

本页用于登记对读者有影响的正文、公式、图表、练习答案和可复现实验修订；以带版本号的 [GitHub Releases](https://github.com/CoCoThink/ai-by-intuition/releases) 作为已发布 PDF 的权威入口。

## 报告问题

请在 [GitHub Issues](https://github.com/CoCoThink/ai-by-intuition/issues) 提交发现，建议包含 PDF 版本或 main 的提交 SHA、章节或页码、错误内容、建议修正以及可复算的依据。涉及隐私或安全信息时请勿在公开 Issue 粘贴敏感数据。

## 已整理的修订批次

| 批次 | 修订范围 | 状态 |
| --- | --- | --- |
| P0 | 概念首次定义、双参数训练数据、练习编号、术语导航与数值例身份 | 已合入 main，见 [PR #12](https://github.com/CoCoThink/ai-by-intuition/pull/12) |
| P1 | 表示动机、MLP 与 Transformer 数值图、20 步训练、PyTorch 复现、Agent 缺口链及架构对照 | 已合入 main，详见 [P1 记录](P1_COMPLETION.md) |
| P2 | 技术生态、2017 原论文对照、技术判断、阅读路线及交互实验 | 修订中，以最终通过 CI 的提交为准 |

表中状态仅说明源码分支，不表示相应内容已经发布为新版本，也不能代替带版本号的 PDF 发布审核。

## 发布版本

- [v0.1.0](https://github.com/CoCoThink/ai-by-intuition/releases/tag/v0.1.0)：历史正式版本，不覆盖其归档 PDF。
- 后续版本：在 [V2 发布前验收](V2_RELEASE_READINESS.md) 完成全部签核后登记版本号、构建运行及 Release 链接。

若修订改变了数值基线、插图标注、代码输入或输出，请在同一个源码变更中同步更新教材、脚本与自动检查，避免“图表版本”和“公式版本”不一致。
