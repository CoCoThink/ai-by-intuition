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
| `actions/download-artifact` | v6 | `018cc2cf5baa6db3ef3c5f8a56943fffe632ef53` |

**剩余浮动边界：** `texlive_version: 2026` 是年份选择而非容器内容摘要；veraPDF 1.30.2 **已按镜像摘要固定**（见本文末尾）；apt 安装的 Noto/Poppler 依赖受当时 Debian 镜像索引影响。不能声称已实现完全字节级可重复构建。

## 自动保存的审计证据

本地与 CI 统一通过 `bash scripts/build_book.sh` 构建。脚本优先使用 `BOOK_BUILD_SHA`，其次使用 `GITHUB_SHA`，最后读取当前仓库的 `git rev-parse HEAD`。TeX 容器在启动编译时显式传入 `${{ github.sha }}`，版权页与附录 G 印出其前 12 位。提交号变化时脚本强制刷新 PDF，避免 latexmk 沿用上一提交的产物。没有 Git 信息的源码包可直接编译；未获得合法提交号时，整句来源说明自动省略。

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

## 正式发布的可复核证据

[主分支全量 CI #39699805713](https://github.com/CoCoThink/ai-by-intuition/actions/runs/39699805713) 和 [Release v0.1.0](https://github.com/CoCoThink/ai-by-intuition/releases/tag/v0.1.0) 对应提交 `55b55e4308028763a0b1952f1a02642e4d9829d8`。官方 PDF 文件 SHA-256：`211a1144770e9f712f2714b4652d30ee7643c5f8390fbb78cbbd39965ff95520`。完整机器审计随 Release 归档；若要升级 TeX Live 镜像或系统包，仍应比较新旧审计环境再决定是否锁定更底层的不可变镜像。

### 本轮新增的复算与结构检查

- `scripts/check_book_contract.py --self-test` 覆盖“旧锚点有效但可见题号过时”、规范题号与目标不符、R 题混入章末导航、部分小地图误用编号图注、章首位于页底及只剩定位框等回归。
- `scripts/icl_policy_demo.py` 用 NumPy 核对前缀匹配与复制，以及固定采样动作、固定优势下的策略梯度；该简化不替代完整 GRPO。
- `scripts/chinese_tokenizer_demo.py --real` 运行固定完整修订的中文分词器，检查文件 SHA-256、ID、逐项解码与正文数值；依赖 `tokenizers==0.22.1`，首次下载约 7 MB 分词器文件。
- `scripts/generate_reference_assets.py --check` 比对参考链接网页和 TikZ 二维码，依赖 `qrcode==8.2`；二维码目标是仓库 `docs/REFERENCES.md`。
- `scripts/teaching_trace.py --attention` 打印第 0、20 步的注意力矩阵；`check_teaching_claims.py` 将真实训练结果与正文权重表比较。

沿用现有 Python 环境，缺包用 pip 安装；本轮没有另装 Python 或更换 TeX 引擎。完整 PDF 仍需通过 MathML 关联、PDF/UA-2、最终引用、章节导航及分页密度检查。

### 开篇、页码与色觉模拟门禁

- `scripts/beginner_training_demo.py` 使用同一数据集复算解析解、0–10 步、有限差分梯度与学习率收敛边界。
- `scripts/check_section_navigation.py --self-test` 拦截有效图目标误作小节目标、写死页码、图题跨页及无目录页码链接；`--pdf book/build/main.pdf --aux book/build/main.aux` 检查实际 PDF 目的页、`.toc` 右列页码链接及所有 Figure 的 MCR 页面归属。
- `scripts/audit_color_roles.py --pdf book/build/main.pdf --aux book/build/main.aux --output book/build/color-audit` 保存色板及三页 QKV 实际页的四种模拟对照。使用 `Pillow==11.3.0` 和 `colorspacious==1.1.2`；项目距离回归阈值不作为无障碍认证。CI 审计工件保留 PNG、JSON 和 PDF 哈希。
- `scripts/claude_function_call_demo.py` 默认验证离线消息关联与宿主拒绝案例，无网络或 API 调用。在线模式不会在 CI 自动运行。
- 中英术语生成器同时维护 `docs/TERM_OCCURRENCES.md`；CI 检查生成结果，避免正文移动后索引漂移。
