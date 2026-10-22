# Tagged PDF · 当前机器验收状态

> 正式基线：2026-10-22 [v0.1.0](https://github.com/CoCoThink/ai-by-intuition/releases/tag/v0.1.0)；[完整成功 CI #39699805713](https://github.com/CoCoThink/ai-by-intuition/actions/runs/39699805713)。旧的实验与修复过程可查 [原始历史文档](https://github.com/CoCoThink/ai-by-intuition/blob/ad239e83e96fcb71647f278e456078d0fc66571e/docs/ACCESSIBILITY.md)，本页只记录现行要求。

## 当前已经验证

| 范围 | 正式版结果 | 自动验收 |
|---|---|---|
| 文档 | 99 页 Tagged PDF，中文目录、标题及图表结构 | `scripts/validate_book.py` |
| 标题/表格/图片 | 48 H1、180 H2、21 Table、59 TH、16 Figure 及 16 处替代文字 | 标签树计数、表头及图注层级 |
| 公式语义 | 1,472 / 1,472 个 Formula 有可解析 MathML-AF 关联，933 份不同的 MathML 文档 | `scripts/validate_mathml_af.py` |
| PDF/UA-2 | veraPDF 1.30.2 `compliant=true`、`failedRules=0`、`failedChecks=0` | 严格阻断构建/发布 |
| 页面/数值 | 7 部分、47 章节文件、页面文字边界和数值算例通过 | 正式工作流回归 |

正式源码入口为 [book/main.tex](../book/main.tex)，使用 TeX Live 2026 + LuaLaTeX，`unicode-math`、`pdfstandard=ua-2`、`math/setup=mathml-AF`。各项计数基于已发布 v0.1.0，源码升级后必须重新验收。

**范围限制：**只验证可重复的机器规则和布局检查。**不安排真实屏幕阅读器体验或人工无障碍验收**；机器符合 PDF/UA-2 规则，不代表任何辅助阅读器中的实际阅读体验已获保证。

## 正式 CI 与依赖

使用 [Build one PDF book](../.github/workflows/build-latex.yml) 检查：源码/数值 → 最小 Tagged `smoke-tagging.tex` → 全书编译 → 文字/标题/表格/图形结构 → 所有公式 MathML-AF → veraPDF PDF/UA-2。

完整 CI 成功时上传**一份 PDF**（`ai-by-intuition-volume-01`）和**一份机器审计**（`pdfua2-machine-audit`）；失败时按需附构建诊断。依赖版本及环境审计见 [BUILD-REPRODUCIBILITY.md](BUILD-REPRODUCIBILITY.md)。

本地主要验收命令：

```bash
python3 scripts/validate_book.py
cd book
latexmk -lualatex -interaction=nonstopmode -halt-on-error -file-line-error -outdir=build main.tex
cd ..
python3 -m pip install pypdf==5.9.0
python3 scripts/validate_book.py --pdf book/build/main.pdf
python3 scripts/validate_mathml_af.py book/build/main.pdf --minimum 1000
```

正式验收还必须以 CI 的 veraPDF 1.30.2 PDF/UA-2 规则报告为准，不能凭 `Tagged: yes` 或结构树计数直接宣布合规。

## 保留的非阻断兼容性限制

TeX Live 2026 的 LuaMML 在 **原生 `amsmath align*`** 兼容实验中触发 `luamml-amsmath.lua:63: assertion failed`。正式教材已使用 `aligned` 组合而通过全部数学语义检查。三份 `book/smoke-mathml*.tex` 案例仅由 [手动兼容诊断工作流](../.github/workflows/check-compatibility.yml) 运行；更换 LaTeX/LuaMML 版本前应重新执行。移除已修复的独立标题实验并不取消正式全书对 H1/H2 的强制检查。

## 维护准则

1. 不移除 `\DocumentMetadata`、公式的 MathML-AF、图形替代文字或表格语义；无障碍结构变化必须跑完整 CI。
2. 为新增图形提供与视觉内容等价的中文替代说明，并核验图注与结构树关系。
3. 升级字体、TeX Live、veraPDF、PDF 结构验证脚本必须留存对应 CI 链接与审计环境。
4. 保持 [正式 Release](https://github.com/CoCoThink/ai-by-intuition/releases/tag/v0.1.0) 不变；新版本必须重新验收与独立发布。
