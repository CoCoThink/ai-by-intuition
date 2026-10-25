# 维护手册

本页给维护者：CI 做了什么、依赖怎样固定、哪些检查只是机器预检、来源怎样复核。编辑约定与生成内容入口见 [AGENTS.md](../AGENTS.md)，提交前的命令见 [CONTRIBUTING.md](../CONTRIBUTING.md)。读者版 PDF 只保留版本号、勘误入口、复现入口和带日期断言表，维护细节都放在这里。

## 工作流

| 工作流 | 触发 | 作用 |
|---|---|---|
| [Build one PDF book](../.github/workflows/build-latex.yml) | 改动 `book/`、`scripts/` 或该工作流 | 源码检查 → 最小 Tagged 冒烟测试 → 整书构建 → 成品检查 → MathML、灰度、色觉模拟、veraPDF；成功时上传 `ai-by-intuition-book` 与 `pdfua2-machine-audit` |
| [Review dated assertions](../.github/workflows/check-dated-claims.yml) | 每周一 03:17 UTC，以及改动断言、来源或正文 | 检查断言到期日，并比较 MCP 官方当前修订与书中版本 |
| [Check Markdown links](../.github/workflows/check-docs.yml) | 改动 Markdown | 本地链接目标存在、README 含许可声明 |
| [Real GPT-2 reproducibility experiment](../.github/workflows/gpt2-real-experiment.yml) | 手动，或改动该实验 | 下载固定修订的 GPT-2 权重做一次真实推理，结果见 [GPT2_REAL_RUN.md](GPT2_REAL_RUN.md)；不阻断 PDF 构建 |
| [Diagnose historical LuaMML compatibility](../.github/workflows/check-compatibility.yml) | 手动 | 复现原生 `align*` 的 LuaMML 断言失败（见下文限制） |
| [Publish validated book](../.github/workflows/publish-release.yml) | 手动 | 见 [PUBLISHING.md](PUBLISHING.md) |

路径过滤决定是否触发整书构建：只改 Markdown 不会编译 PDF。不要把“未触发”说成“已通过”。

## 构建与依赖固定

- 本地与 CI 都通过 `bash scripts/build_book.sh` 构建。提交号依次取 `BOOK_BUILD_SHA`、`GITHUB_SHA`、`git rev-parse HEAD`，印在版权页和附录 G；没有 Git 信息的源码包会省略整句来源说明。提交号变化时脚本强制刷新 PDF。
- 所有第三方 Action 固定到完整提交 SHA；veraPDF 1.30.2 按镜像摘要拉取：`verapdf/cli@sha256:d5ee329657cf9bc4b2400392dd54c7d0a0ce9980ff6fa2da5590eebeec007cdb`。
- 仍会浮动的部分：`texlive_version: 2026` 是年份选择而非镜像摘要，apt 安装的 Noto 字体与 Poppler 取决于当时的 Debian 索引。因此不声称字节级可复现；`pdfua2-machine-audit` 中的 `texlive-environment.txt`、`runner-environment.txt`、`verapdf-image.txt` 记录了每次实际使用的版本。
- Python 依赖版本以工作流为准（`pypdf`、`numpy`、`tokenizers`、`qrcode`、`Pillow`、`colorspacious`、`pypinyin`）。

**升级依赖时：**单独开 PR；Action 的 SHA 从上游官方标签重新获取；附上新旧环境记录；源码检查、成品检查、全部公式 MathML 关联和 veraPDF 零失败都要通过；页数或结构数量的意外变化要说明原因。

## 无障碍：机器验收与边界

`book/main.tex` 使用 `\DocumentMetadata{lang=zh-CN,tagging=on,pdfstandard=ua-2,tagging-setup={math/setup=mathml-AF}}`。CI 阻断以下任一失败：

- 结构树、标题层级、表头、Figure 与 Caption 的嵌套和中文替代文字（`validate_book.py --pdf`）；
- 每个公式都有可解析的 MathML 关联文件（`validate_mathml_af.py`）；
- veraPDF PDF/UA-2 零失败。

这些只覆盖机器可验证的规则。项目不安排真实读屏器体验测试，机器通过不代表辅助阅读器中的实际体验已经验证。

**已知限制：**TeX Live 2026 的 LuaMML 处理原生 `amsmath` 的 `align*` 时触发 `luamml-amsmath.lua:63: assertion failed`。正文改用 `aligned` 组合；`book/smoke-mathml*.tex` 由手动兼容工作流复现该问题，升级 LaTeX 或 LuaMML 后重新运行。

不要通过移除 `\DocumentMetadata`、关闭标签、删掉替代文字或降低阈值来让 CI 通过。

## 灰度与人工校样

CI 对每页做灰度预检（`audit_grayscale_pdf.py`：接近空白的页、贴边的深色像素），并对 Q/K/V 图做三种色觉模拟（`audit_color_roles.py`）。这只是粗筛，不能代替人工看页面。

人工校样用 `scripts/print_proof.py` 生成灰度页图、逐页检查表和来源摘要，不修改 PDF：

```bash
# 关键页
python3 scripts/print_proof.py book/build/main.pdf --pages 1-6,last --out-dir book/build/print-proof
# 发布前逐页
python3 scripts/print_proof.py book/build/main.pdf --all --scale 1100 --out-dir book/build/print-proof \
  --audit-json pdfua-audit/grayscale-audit.json
```

传入同一次 CI 的 `grayscale-audit.json` 时，PDF 哈希或源码提交不一致会直接拒绝生成，避免混用不同构建。逐页核对：

- 颜色之外仍能区分角色：Q/K/V、梯度正负、Mask 可见与否要有字母、数值、线型或位置提示；
- 中文、上下标和长 URL 不溢出，没有缺字；
- 图表的表头、单位、线型在灰度下可辨，图题与替代文字表达主要信息；
- 目录、交叉引用、脚本路径与本次构建一致；跨页的例子、题目和答案能追溯。

审阅记录要写明完整提交号、CI 运行号、审阅人和日期，不能沿用旧 PDF 的结论。

## 带日期断言与来源

- 断言清单的唯一来源是 [dated-claims.json](../book/dated-claims.json)，附录 G 的表格由 `python3 scripts/check_dated_claims.py --write` 生成。复查周期为“90 天或出现新修订，以先到者为准”。
- 每周的定时工作流与每次整书构建都会检查到期日期；MCP 官方入口指向新修订时也会失败。处理方式：先重新阅读规范、核对正文示例和请求字段，再更新版本与 `checked_utc`。编译日期、链接可访问或 CI 成功都不能替代内容核验，也不要为了解除门禁直接改日期。
- 附录 F 的逐条链接记录在 [source-audit.json](../book/source-audit.json)；网页清单 [REFERENCES.md](REFERENCES.md) 与二维码由 `python3 scripts/generate_reference_assets.py` 生成。

## 题号

C 题和 R 题按印刷顺序连续编号，由 `generate_exercise_bank.py` 校验。增删题目后整体重排，并同步正文、脚本和文档中对题号的引用；`legacy_id` 字段保留更早的 C1/C2/C3/C4 编号，作为隐藏锚点，不能重新在印刷版中显示。

## 复算入口

复算脚本总表在附录 B（`book/chapters/24e-pytorch-lab.tex`，标签 `app:reproduction-scripts`），`check_book_contract.py` 检查关键脚本都列在表中。默认只运行离线实验；Claude 等付费 API 的真实调用需要明确授权，中文分词器的 `--real` 只下载固定版本的分词器文件。
