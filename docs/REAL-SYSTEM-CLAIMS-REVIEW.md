# 真实系统行为与限定语复核

复核日期：2026-10-25。范围为 `adfeec8..e016f29` 中所有删除“通常”的句子及其相邻上下文，包括正文、答案和术语定义；同步检查 API 状态、KV Cache、权重绑定与硬件描述。生成的术语表与其源定义一并核对。保留数学机制的直接结论，对实现行为写明模型、模式或接口条件。

| 主题 | 复核结论与处理 | 源码入口 |
| --- | --- | --- |
| RAG 与核验 | 改回“检索来源与准确性仍需应用层核验，RAG 本身不提供这一保证”。检索材料进入上下文，不会自动完成事实核查。 | [预训练与 ICL](../book/chapters/23aa-pretraining-icl.tex) |
| API 是否有状态 | 原文已分别限定无状态请求接口与服务端会话 API，继续保留；不将某一种接口的行为推广到所有 API。[Claude Messages](https://platform.claude.com/docs/en/build-with-claude/working-with-messages) 与 [Gemini Interactions](https://ai.google.dev/gemini-api/docs/interactions-overview) 提供了两类具体例子。 | [RAG 与状态](../book/chapters/23d-agent-systems.tex) |
| 跨请求复用 KV | 保留“取决于具体接口和实现”；同一解码内复用历史 KV 的解释增加参数与位置规则固定的前提。[vLLM APC](https://docs.vllm.ai/en/latest/features/automatic_prefix_caching/) 的跨请求复用要求共享前缀并启用相应功能。 | [生成与 KV](../book/chapters/23-llm-systems.tex)、[状态边界](../book/chapters/23d-agent-systems.tex) |
| 输出头权重绑定 | 明确限定“原始 GPT-2”，其他模型须查配置与输出头实现。原始实现直接用输入嵌入矩阵转置生成 logits，见[固定提交的原始代码](https://github.com/openai/gpt-2/blob/9b63575ef42771a015060c964af2c3da4cf7c8ab/src/model.py)。 | [从算例到 GPT](../book/chapters/23a-from-toy-to-gpt.tex) |
| 固定参数推理 | 明确限定“本节”与“本书的推理流程”，不对包含在线适配或权重更新的所有服务作统一判断。 | [部署](../book/chapters/23b-deployment-and-ecosystem.tex) |
| GPU、TPU、NPU | 设备类别定义保留；在现有边界说明中补明算子、精度、带宽、延迟须按型号、运行时与负载核对。[CUDA 指南](https://docs.nvidia.com/cuda/cuda-c-programming-guide/)、[Cloud TPU 概述](https://cloud.google.com/tpu/docs/intro-to-tpu) 均按工作负载讨论适用性。 | [部署与硬件](../book/chapters/23b-deployment-and-ecosystem.tex) |
| Dropout | 改为“评估模式下关闭随机屏蔽”，补明 `model.eval()` 与关闭梯度记录是两回事，答案和术语表同步。[Dropout 定义](https://docs.pytorch.org/docs/2.14/generated/torch.nn.Dropout.html)、[评估模式说明](https://docs.pytorch.org/docs/2.14/notes/autograd.html#evaluation-mode-nn-module-eval)。 | [泛化](../book/chapters/18-generalization.tex)、[术语源](../book/chapters/24-lexicon.tex) |
| 参数初始化 | 将随机初始化写成从头训练的“常见做法”，避免推广为所有模型的必要条件。 | [Embedding](../book/chapters/20-embeddings.tex) |
| 多模态入口 | 明确模型可选择专用编码器或共享表示，避免暗示各模态必定采用不同编码器。 | [多模态](../book/chapters/23b-deployment-and-ecosystem.tex) |
| Token 粒度 | 将“更大片段需要更大词表”限定为用更大片段覆盖更多词形的需求，不声称粒度与词表大小一一对应。 | [Tokenizer](../book/chapters/20a-tokenizer.tex) |
| 卷积实现 | “PyTorch 的卷积层执行互相关”成立，见 [Conv2d 定义](https://docs.pytorch.org/docs/2.14/generated/torch.nn.Conv2d.html)；不推广到所有名为卷积的数学运算。 | [CNN](../book/chapters/19-cnn.tex) |
| Attention 与网络结构 | BERT 双向读取、原始 Encoder–Decoder 的可见性、标准 Transformer 的 Q/K/V 投影按各自结构说明；将答案中的“真实 Transformer”收紧为“标准 Transformer”。RNN 与共享 Patch 投影的结论均在本章所定义的网络中使用。 | [结构](../book/chapters/22-transformer-architecture.tex)、[答案](../book/chapters/27-answer-key.tex) |
| 数学与统计陈述 | 温度结论已限定正温度与非均匀 logits；非线性表述说明表达能力而非任意参数必然非线性；随机 Key 干扰保留独立性、归一化与统计规模条件。梯度更新的次序限定在本书训练步中。 | [生成](../book/chapters/23-llm-systems.tex)、[矩阵](../book/chapters/03-matrix-multiplication.tex)、[容量](../book/chapters/13-capacity.tex) |

后续改写实现行为时，应先核对适用条件，再决定删去或保留程度词；不以“通常”的出现次数作为文风质量目标。
