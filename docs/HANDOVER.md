# AI by Intuition · 当前维护状态

> 更新日期：2026-10-22。本页只列出当前工作约定，历史交接原文保留在 [2026-10-22 整理前的 Git 记录](https://github.com/CoCoThink/ai-by-intuition/blob/ad239e83e96fcb71647f278e456078d0fc66571e/docs/HANDOVER.md)，无需让旧事项反复成为新的待办。

## 正式交付基线

- [Release v0.1.0](https://github.com/CoCoThink/ai-by-intuition/releases/tag/v0.1.0) 已完成发布，不允许原地覆盖历史 PDF 或其 SHA-256。
- 正式发布对应主分支提交 `55b55e4308028763a0b1952f1a02642e4d9829d8`，[完整 PDF CI](https://github.com/CoCoThink/ai-by-intuition/actions/runs/39699805713) 和 [发布工作流](https://github.com/CoCoThink/ai-by-intuition/actions/runs/39700328180) 都成功。
- 已验证 99 页 Tagged PDF、1,472/1,472 MathML-AF、933 个不同 MathML 文档、48 个 H1、180 个 H2、21 张表格、16 张语义图；veraPDF 1.30.2 PDF/UA-2 失败数为 0。
- 官方 PDF SHA-256 为 `211a1144770e9f712f2714b4652d30ee7643c5f8390fbb78cbbd39965ff95520`。

## 交接事项处理结论

| 项目 | 当前结论 |
|---|---|
| H-01 CI 路径覆盖 | 已完成。验证脚本改变会触发完整 PDF 构建；Markdown 和工作流配置有独立检查 |
| H-02 过时 MathML/veraPDF 说明 | 已完成，正式版开启 `unicode-math` + `mathml-AF`，veraPDF 是发布阻断门槛 |
| H-03 原生 `align*` 不兼容 | 已绕行，非阻断。使用 [手动兼容诊断工作流](../.github/workflows/check-compatibility.yml) 跟踪 |
| H-04 构建依赖复现 | Action SHA 与 veraPDF digest 固定，保留环境审计；TeX Live 基础镜像及 apt 软件包仍需升级核对 |
| H-05 重复小标题 | 已修复且完整 PDF 回归通过 |
| H-06 视觉 QA 与 Release | 已发布 v0.1.0；新版本采取显式版本号 + 指定已验证构建的手动发布，不自动替换历史资产 |

历史标题实验已验证并被正式的 `scripts/validate_book.py` 结构测试取代；无需每次正式构建重复实验。过去实验日志仍能通过历史 Actions 获取，受 GitHub 工件保留期限制。

## 日常维护方式

1. 正文 LaTeX 或验证脚本变更，必须通过 [正式完整构建](../.github/workflows/build-latex.yml)：源码、数值、99 页结构/版面、MathML-AF、veraPDF PDF/UA-2。
2. Markdown 或工作流配置变更运行 [轻量 CI](../.github/workflows/check-docs.yml)，包含链接检查和工作流语法/安全约束检查。
3. `align*` 上游兼容问题只在需要升级 LuaMML/TeX Live 时通过 [手动实验](../.github/workflows/check-compatibility.yml) 复查，不影响生产 PDF。
4. 发布新版见 [PUBLISHING.md](PUBLISHING.md)，复现/依赖升级见 [BUILD-REPRODUCIBILITY.md](BUILD-REPRODUCIBILITY.md)。
5. 公开仓库无开放 Issue 不是“未来没有 bug”的保证；任何新缺陷按实际证据立项。项目不承诺已通过真实屏读软件体验测试。
