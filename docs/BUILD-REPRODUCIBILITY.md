# 构建依赖复现与升级审计

## 当前版本约束（2026-10-22）

正式发布必须运行 [全量 PDF CI](../.github/workflows/build-latex.yml)。基础环境为 GitHub Actions `ubuntu-24.04`、TeX Live **2026**（`os: debian`）、LuaLaTeX、Noto 字体、Poppler、Python **3.12**、`pypdf==5.9.0`、veraPDF CLI **1.30.2**（PDF/UA-2）。

下列 Action 在工作流中使用已从对应上游主版本标签核对的完整 commit SHA，防止主版本浮动：

| Action | 标签 | 固定提交 SHA |
|---|---|---|
| `actions/checkout` | v4 | `11d5960a326750d5838078e36cf38b85af677262` |
| `xu-cheng/texlive-action` | v3 | `22c04326a5d855880f9d39bb955138bf11c6df80` |
| `actions/setup-python` | v6 | `ece7cb06caefa5fff74198d8649806c4678c61a1` |
| `actions/upload-artifact` | v4 | `ea165f8d65b6e75b540449e92b4886f43607fa02` |

**剩余浮动边界：** `texlive_version: 2026` 是年份选择而非容器内容摘要；`verapdf/cli:v1.30.2` 也是可重新指向的镜像标签；apt 安装的 Noto/Poppler 依赖受当时 Debian 镜像索引影响。不能声称已实现完全字节级可重复构建。

## 自动保存的审计证据

`pdfua2-machine-audit` 工件除 veraPDF XML 和 MathML JSON 外，还保存：
- `texlive-environment.txt`：LuaLaTeX、latexmk、Noto/Poppler 包版本及字体匹配；
- `runner-environment.txt`：GitHub runner 镜像、Python/pypdf/Poppler 版本；
- `verapdf-image.txt`：实际拉取镜像的 image ID 与 registry RepoDigest（如果存在）。

保存关联的 CI run URL、commit SHA、工件与正式 PDF。升级时对比新旧镜像标识、规则失败数和 PDF 统计；仅凭镜像标签相同不足以证明依赖相同。

## 依赖升级准入

1. 从上游官方标签重新获取 Action 的完整提交 SHA，检查更新记录；禁止复制未验证的第三方哈希。
2. TeX Live、apt 包、veraPDF 镜像或 Action 更新必须通过单独 PR，附旧/新环境记录与构建审计工件。
3. 需要全部通过：源码数值验证、Tagged PDF 结构/页面 QA、全部 Formula 的 MathML-AF、veraPDF PDF/UA-2 零失败。原生 `align*` 诊断仍属于非阻断实验。
4. 如果升级无意引入页数或结构数量变化，必须说明原因；若无法复现旧状态，保留原始构建及 CI URL 作为审计基线。


## 2026-10-22 固定镜像更新

在 [修复后完整成功的 CI](https://github.com/CoCoThink/ai-by-intuition/actions/runs/39697175674) 核对到 `verapdf/cli:v1.30.2` 的仓库镜像摘要 `sha256:d5ee329657cf9bc4b2400392dd54c7d0a0ce9980ff6fa2da5590eebeec007cdb`，后续验收直接以 `verapdf/cli@sha256:d5ee329657cf9bc4b2400392dd54c7d0a0ce9980ff6fa2da5590eebeec007cdb` 拉取并运行。TeX Live Action 自身的容器镜像与 apt 索引仍由上游和镜像仓库管理：工作流保留摘要与实际软件包版本审计，而不是假设其每次都相同。升级需要新分支、记录环境漂移并运行整本书回归。