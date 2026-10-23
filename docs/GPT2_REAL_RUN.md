# GPT-2 真实权重实验：固定版本与结果记录

本实验是教材第 27 章可选的真实模型复算，**不阻断 Tagged PDF 构建**。

## 输入与依赖约定

- 模型：`openai-community/gpt2`
- 固定权重 revision：`607a30d783dfa663caf39e06633721c8d4cfcd7e`
- 默认 Prompt：`The capital of France is`
- 运行平台：Ubuntu 24.04、独立 Python 虚拟环境，CPU 推理
- 主依赖：PyTorch 2.5.1、Transformers 4.46.3、NumPy 1.26.4、Matplotlib 3.9.2
- Attention 后端：`eager`；输出第一层首头热图

## 已完成的固定版本真实实验（2026-10-23）

成功工作流：[Real GPT-2 reproducibility experiment #39897932969](https://github.com/CoCoThink/ai-by-intuition/actions/runs/39897932969)。
对应源码提交：
[`a20a0c15f3c46b6102c8ac5222b5607ee731a46a`](https://github.com/CoCoThink/ai-by-intuition/commit/a20a0c15f3c46b6102c8ac5222b5607ee731a46a)。
[下载该运行的工件](https://github.com/CoCoThink/ai-by-intuition/actions/runs/39897932969/artifacts/12477398540)。

实测结果：

| 检查 | 真实输出 |
|---|---|
| 模型 commit | `607a30d783dfa663caf39e06633721c8d4cfcd7e` |
| 运行环境 | torch `2.5.1+cpu`、transformers `4.46.3`、numpy `1.26.4` |
| 英文 Prompt | `The capital of France is` |
| 真实分词 | 5 个；`[464, 3139, 286, 4881, 318]` |
| 模型 logits | `(1, 5, 50257)`，全部有限 |
| Softmax 总和 | `T=0.7/1.0/1.5` 均为 `1.00000000` |
| 首层首头因果掩码 | 未来位置权重最大绝对值 `0` |
| T=1.0 的候选示例 | `' the'` 概率 `0.08459`；`' Paris'` 概率 `0.03224` |

这组真实数据来自上述运行下载的 `gpt2-console.txt`，
热图则来自 `gpt2-attention.png`。
最初用 float32 对五万多个概率求和时曾得到 `1.00001204` 的舍入结果；
改用 float64 后通过了同一模型的概率归一化检查。
这属于**数值审计精度修正**，并未调整模型权重。

## GitHub Actions 入口

在 [可选 GPT-2 真实实验](../.github/workflows/gpt2-real-experiment.yml)
对应的 GitHub Actions 工作流中选择 **Run workflow**。
工作流文件或实验脚本在主分支发生修改时，也会独立触发运行；不属于 PDF 主 CI。

成功工件 `gpt2-real-repro-report` 应含：

- `revision.txt`：本次源码 SHA；
- `python-packages.txt`：实际安装的完整依赖版本；
- `gpt2-console.txt`：Token 数和 ID、完整 logits 形状、三种温度的 Top-5 和概率和；
- `gpt2-attention.png`：第一层第零个头的因果 Attention 灰度热图。

程序会检查最后一位词表宽度为 50,257，概率和接近 1，
概率归一化检查使用 float64 累加，避免大词表的 float32 求和舍入误差；
Attention 上三角（未来 Key）最大绝对值小于 1e-6，
每行权重和接近 1。

**证据边界：**预跑必须由完成的真实权重工作流报告支持，
离线公式自检不足以给出真实 Token 数或 Top-5。
这里只锁定四个顶层依赖，运行时保存实际的完整传递依赖清单。
这是英文 Prompt 的数学与模型接口 sanity check，不涉及正式模型质量评测。
下载公开权重需要联网，网络或依赖故障不会影响独立的 PDF 构建。
