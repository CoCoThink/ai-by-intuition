# PDF 出版与版本发布

## 当前发行版

[**v0.1.0 正式 Release**](https://github.com/CoCoThink/ai-by-intuition/releases/tag/v0.1.0) 已于 2026-10-22 发布，版本资产包含 PDF、SHA256SUMS 和逐项机器审计文件（共 8 项）。该历史 Release **不会被精简工作流追溯修改**。

对应 [完整 CI #39699805713](https://github.com/CoCoThink/ai-by-intuition/actions/runs/39699805713) 与 [发布 CI #39700328180](https://github.com/CoCoThink/ai-by-intuition/actions/runs/39700328180) 均为 success。PDF 为 99 页、1,472/1,472 MathML-AF，veraPDF PDF/UA-2 零失败，原始 SHA-256 为 `211a1144770e9f712f2714b4652d30ee7643c5f8390fbb78cbbd39965ff95520`。

首次发行视觉 QA：对全部 99 页缩略图巡检，并放大检查部分复杂页；新旧正式候选的页面文字与缩略图渲染一致，未发现明显裁切或遮挡。详尽历史记录留存在[发布前原始文档](https://github.com/CoCoThink/ai-by-intuition/blob/ad239e83e96fcb71647f278e456078d0fc66571e/docs/PUBLISHING.md)。此检查不包括真实屏读软件的体验验收。

## 新版本（从 v0.2.0 开始）的发布步骤

发布前逐项核对 [V2 预发布验收台账](V2_RELEASE_READINESS.md) 与 [候选版变更说明](V2_RELEASE_NOTES_DRAFT.md)。手动发布须使用最后一次**包含全部实际源码和排版变更**、机器验收成功的 `main` 构建，而不能仅借用上一轮成功构建。

**M5/M6 候选说明：**新版 CI 不再使用 `Volume 01` 文件名；历史 v0.1.0 的资产仍保持原名称不变。`main` 上的完整 PDF 构建已引入七个必读部分、两个选读专题和 A–E 附录；**新的手动 Release 尚未触发**，不以旧版的 99 页或 1,472 条公式作为新版固定计数。

**许可证：** 教材/PDF 正式采用 [CC BY 4.0](../LICENSE)，Python/工作流采用 [MIT](../scripts/LICENSE)。Release 正文应提供项目来源、版权署名、许可地址以及适用的第三方材料声明。v0.1.0 发布于许可证正式加入前，保留其原始资产与发行日志不覆盖；当前公开授权同时涵盖项目有权授权的 v0.1.0 PDF。

**发布必须明确人工选择版本号和已验收的主分支构建，不再监听所有成功的 push 自动触发。**

1. 从 `main` 的 [Build one PDF book](../.github/workflows/build-latex.yml) 运行 `workflow_dispatch`，取得 **success** 的完整构建运行 ID（`build_run_id`）。PDF 工件有保留期限，过期后必须重新构建。
2. 完成变动页面的视觉 QA，确认 PDF 机器结构、公式语义、veraPDF PDF/UA-2 与数值计算均通过。
3. 在 `main` 的 [Publish validated book](../.github/workflows/publish-release.yml) 点击 **Run workflow**，输入新版本号（如 `v0.2.0`）和上一步的 `build_run_id`。
4. 发布工作流校验：版本格式为 `vX.Y.Z`、tag/Release 不存在、来源运行是本仓库 `main` 的成功 `push` 或手动完整构建、来源提交可追溯至当前 `main`，且构建之后没有改动 `book/`、`scripts/` 或正式 PDF 构建工作流。如验证失败则拒绝发布。
5. 工作流从指定同一次构建提取 PDF 和审计，用 `pypdf` 检查**实际页数与 MathML 审计一致**，核验 Formula/MathML-AF 全量关联、veraPDF 零失败与环境记录，计算 `SHA256SUMS`，将审计合并为 `build-audit.zip`，并在 Release 正文记录真实统计与验证来源。
6. 新版本只上传 **3 个资产**：`AI-by-Intuition-Book.pdf`、`SHA256SUMS`、`build-audit.zip`。不要覆盖旧版本、不要单独再附一份 `RELEASE-NOTES.md`，也不要发布未经同一成功 CI 验收的其他 PDF。

**注意：**手动选择版本号和成功构建仍是必要条件；此处更新发布脚本不意味着已经发布。发布工作流不得从 PR / fork 的产物直接发布；历史 Release 不可在原位重新编译替换。任何合规声明只代表机器验收，**不等于**人工屏读体验认证。

## 未来发行版视觉检查表

| 日期 | 版本/源码 SHA | 构建与视觉 QA 范围 | 发现问题与复核结果 |
|---|---|---|---|
| 2026-10-22 | v0.1.0 · `55b55e4` | 99 页抽样排版及全部页文字/缩略图回归 | 无明显遮挡裁切，已发布 |

涉及排版的修改，应重新审看封面、目录、部分首页、长公式、插图和变动前后页。出版检查不应被自动版面边界检查完全替代。
