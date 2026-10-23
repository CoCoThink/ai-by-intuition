# GPT-2 真实权重实验：固定版本与结果记录

本实验是教材第 27 章可选的真实模型复算，**不阻断 Tagged PDF 构建**。

## 输入与依赖约定

- 模型：\`openai-community/gpt2\`
- 固定权重 revision：\`607a30d783dfa663caf39e06633721c8d4cfcd7e\`
- 默认 Prompt：\`The capital of France is\`
- 运行平台：Ubuntu 24.04、独立 Python 虚拟环境，CPU 推理
- 主依赖：PyTorch 2.5.1、Transformers 4.46.3、NumPy 1.26.4、Matplotlib 3.9.2
- Attention 后端：\`eager\`；输出第一层首头热图

## GitHub Actions 入口

在 [可选 GPT-2 真实实验](../.github/workflows/gpt2-real-experiment.yml)
对应的 GitHub Actions 工作流中选择 **Run workflow**。
工作流文件或实验脚本在主分支发生修改时，也会独立触发运行；不属于 PDF 主 CI。

成功工件 \`gpt2-real-repro-report\` 应含：

- \`revision.txt\`：本次源码 SHA；
- \`python-packages.txt\`：实际安装的完整依赖版本；
- \`gpt2-console.txt\`：Token 数和 ID、完整 logits 形状、三种温度的 Top-5 和概率和；
- \`gpt2-attention.png\`：第一层第零个头的因果 Attention 灰度热图。

程序会检查最后一位词表宽度为 50,257，概率和接近 1，
Attention 上三角（未来 Key）最大绝对值小于 1e-6，
每行权重和接近 1。

**证据边界：**预跑必须由完成的真实权重工作流报告支持，
离线公式自检不足以给出真实 Token 数或 Top-5。
这里只锁定四个顶层依赖，运行时保存实际的完整传递依赖清单。
这是英文 Prompt 的数学与模型接口 sanity check，不涉及正式模型质量评测。
下载公开权重需要联网，网络或依赖故障不会影响独立的 PDF 构建。
