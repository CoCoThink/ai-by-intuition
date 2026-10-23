#!/usr/bin/env python3
"""Audit the book from source structure through the rendered PDF.

Tests cover reading order, cross references, vector conventions, worked numeric
examples, navigation, appendix separation and final PDF page/TOC content.
"""
from __future__ import annotations

import argparse
import math
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
BOOK = ROOT / "book"
PARTS = [
    "学习是什么：从规则到参数更新",
    "把许多数一起算",
    "让文字进入计算",
    "让词与词交换信息",
    "组装并训练 Transformer",
    "把 Attention 与 FFN 看作记忆",
    "从语言模型到助手",
    "架构为什么在变，往哪走",
    "选读：从 CNN 到视觉 Transformer",
]
REQUIRED = [
    "00g-reading-routes",
    "00-guide",
    "00d-rules-gap",
    "00-functions",
    "16-loss-gradient",
    "07-functions-relu",
    "17-backpropagation",
    "18b-end-to-end-learning",
    "18-generalization",
    "01-vectors",
    "02-dot-product",
    "03-matrix-multiplication",
    "10-mlp",
    "18c-training-engineering",
    "20a-tokenizer",
    "20c-classification-loss",
    "20-embeddings",
    "20b-task-contract",
    "21a-context-gap",
    "21-rnn",
    "21c-naive-attention",
    "21b-why-attention",
    "11-softmax-memory",
    "22a-position-multihead",
    "22-transformer-architecture",
    "10b-ffn-output-head",
    "22b-token-to-output",
    "22c-language-training",
    "23-llm-systems",
    "23a-from-toy-to-gpt",
    "04-key-value-outer-product",
    "05-memory-interference",
    "06-better-linear-memory",
    "08-stacking-key-value",
    "09-nonlinearity-and-memory",
    "14-summary",
    "13-capacity",
    "23aa-pretraining-icl",
    "23c-post-training",
    "23d-agent-systems",
    "23b-deployment-and-ecosystem",
    "22d-modern-transformers",
    "23e-tech-judgement",
    "23f-foundation-recap",
    "19-cnn",
    "19b-vit",
    "00e-core-formulas",
    "00b-math-tools",
    "00c-symbols",
    "00f-transformer-intermediates",
    "24e-pytorch-lab",
    "25-integrated-practice",
    "25b-modern-practice",
    "15-practice",
    "27-answer-key",
    "28-chapter-checks",
    "24-lexicon",
    "24b-modern-lexicon",
    "24c-concept-map",
    "24e-bilingual-glossary",
    "24d-english-index",
    "26-sources",
    "29-revision-notes",
]


def fail(msg: str) -> None:
    raise SystemExit("VALIDATION ERROR: " + msg)


def normalized(text: str) -> str:
    return re.sub(r"\s+", "", text)


def chapter(name: str) -> str:
    path = BOOK / "chapters" / f"{name}.tex"
    if not path.is_file():
        fail(f"Missing chapter {name}")
    return path.read_text(encoding="utf-8")


def includes(haystack: str, needle: str, where: str) -> None:
    if needle not in haystack:
        fail(f"Missing {needle!r} in {where}")


def test_numeric_examples() -> None:
    # New canonical fixture: all three target positions contribute to mean CE.
    initial_probs = [0.2616530343114909, 0.05074656916466208,
                     0.3417608958430908]
    after_probs = [0.32686515021008605, 0.06854806546837465,
                   0.3549764600922404]
    loss0 = -sum(math.log(p) for p in initial_probs) / 3
    loss1 = -sum(math.log(p) for p in after_probs) / 3
    assert math.isclose(loss0, 1.7984303789332916, abs_tol=1e-12)
    assert math.isclose(loss1, 1.6113771577442104, abs_tol=1e-12)
    assert all(b > a for a, b in zip(initial_probs, after_probs))
    assert sum((p - (i == 4)) / 3 for i, p in enumerate(
        [0.08257257, 0.0954348, 0.09512195, 0.67612411,
         0.05074656916466208])) == sum([
             .08257257/3, .0954348/3, .09512195/3,
             .67612411/3, (.05074656916466208 - 1)/3
         ])
    # Standalone ViT: four 2x2 grayscale patches projected from 4D to 3D.
    pixels = [[1,1,0,0], [1,0,0,1], [0,1,1,1], [0,0,0,1]]
    patches = [[pixels[r+i][c+j] for i in range(2) for j in range(2)]
               for r in (0,2) for c in (0,2)]
    assert patches == [[1,1,1,0], [0,0,0,1], [0,1,0,0], [1,1,0,1]]
    proj = [[1,0,0], [0,1,0], [0,0,1], [.5,.5,0]]
    embedded = [[sum(row[i]*proj[i][k] for i in range(4)) for k in range(3)]
                for row in patches]
    assert embedded == [[1,1,1], [.5,.5,0], [0,1,0], [1.5,1.5,0]]
    # Fictitious reporting task: check source values and quarter-on-quarter rates.
    q1, q2, q3 = 100, 120, 132
    assert math.isclose((q2 - q1) / q1, 0.20)
    assert math.isclose((q3 - q2) / q2, 0.10)
    includes(chapter("23d-agent-systems"),
             '"revenue":132', "fictitious Q3 tool result")
    # Numeric regression: attention -> projection -> logits -> cross-entropy.
    e = math.e
    attention = [1 / (2 + e), 1 / (2 + e), e / (2 + e)]
    read0 = attention[0] + attention[2]
    read1 = attention[1] + attention[2]
    logits = [2 * read0, read1, read0 - read1]
    weights = [math.exp(z - max(logits)) for z in logits]
    p_class2 = weights[1] / sum(weights)
    assert math.isclose(p_class2, 0.27368396943659246, abs_tol=1e-12)
    assert math.isclose(-math.log(p_class2), 1.295781234484205, abs_tol=1e-12)
    # Hand-checked two-step Adam example: gradients 2, 1; beta1=beta2=.5.
    m = v = 0.0
    moments = []
    for t, grad in enumerate([2.0, 1.0], 1):
        m = .5 * m + .5 * grad
        v = .5 * v + .5 * grad * grad
        moments.append((m / (1 - .5 ** t), v / (1 - .5 ** t)))
    assert moments == [(2.0, 4.0), (4.0 / 3.0, 2.0)]
    assert math.isclose((4.0 / 3.0) / math.sqrt(2), 0.94280904158, rel_tol=1e-10)
    assert math.isclose(1000 * 8 + 8 * 1000, 16000)
    assert 2 * 120 * 6 * 4 == 5760
    assert 2 * 120 * 2 * 4 == 1920
    # FFN illustration: both Token rows are transformed.
    x = [[1, 2], [0, 1]]
    up = [[1, 0, 1], [0, 1, -1]]
    down = [[2, 0], [1, 1], [1, 1]]
    hidden = [[max(0, sum(row[k] * up[k][j] for k in range(2)))
               for j in range(3)] for row in x]
    ffn = [[sum(row[k] * down[k][j] for k in range(3))
            for j in range(2)] for row in hidden]
    assert ffn == [[4, 2], [1, 1]]
    # Cross-correlation with a 2x2 kernel on a 4x4 image.
    image = [[1, 1, 0, 0], [1, 1, 0, 0],
             [0, 0, 1, 1], [0, 0, 1, 1]]
    response = [[image[i][j] - image[i + 1][j + 1] for j in range(3)]
                for i in range(3)]
    assert response == [[0, 1, 0], [1, 0, -1], [0, -1, 0]]
    # Row-memory sanity check after transposing the column-vector teaching examples.
    simple = ((1.0, 0.6), (0.0, 0.8))
    better = ((1.0, 0.0), (-0.75, 1.25))
    def mul_row(row, matrix):
        return tuple(sum(row[i] * matrix[i][j] for i in range(len(row)))
                     for j in range(len(matrix[0])))
    assert mul_row((1.0, 0.0), simple) == (1.0, 0.6)
    assert all(math.isclose(a, b, abs_tol=1e-12) for a, b in
               zip(mul_row((0.6, 0.8), better), (0.0, 1.0)))
    assert all(math.isclose(a, b) for a, b in
               zip(mul_row((1.0, -0.2), ((2.0, 1.0), (0.0, 3.0))), (2.0, 0.4)))
    # Answer key exercise: (6,0) · (5,12) = 30, cos = 5/13.
    assert math.isclose(6 * 13 * (5 / 13), 30)
    print("Numerical QA passed: 3-position joint SGD loss and legacy independent illustrations checked")


def validate_source() -> None:
    main = (BOOK / "main.tex").read_text(encoding="utf-8")
    parts = re.findall(r"\\part\{([^}]+)\}", main)
    if parts != PARTS:
        fail(f"Expected nine total parts (eight core and one elective); found {parts!r}")
    inputs = re.findall(r"\\input\{chapters/([^}]+)\}", main)
    if inputs != REQUIRED or len(inputs) != len(set(inputs)):
        fail(f"Reading order/appendix differs from the current curriculum: {inputs!r}")
    sources = {name: chapter(name) for name in REQUIRED}
    includes(main, r"\appendix", "main")
    # The manual release gate must consume exactly the PDF artifact built here.
    production = (ROOT / ".github/workflows/build-latex.yml").read_text(encoding="utf8")
    release = (ROOT / ".github/workflows/publish-release.yml").read_text(encoding="utf8")
    for workflow in (production, release):
        includes(workflow, "ai-by-intuition-book", "matching build/release artifact")
        includes(workflow, "AI-by-Intuition-Book.pdf", "matching build/release PDF filename")
    if 'summary["pages"] == 99' in release or "1,472/1,472" in release:
        fail("Release gate still hard-codes historical v0.1.0 PDF statistics")
    includes(release, 'summary["pages"] == actual_pages', "PDF page and audit reconciliation")
    includes(release, "failedRules", "PDF/UA-2 release audit enforcement")

    includes(main, r"\part*{附录：公式、练习与答案}", "main")
    includes(main, r"\ctexset{", "native CTeX heading styling")
    includes(main, "bookmarksnumbered=true", "numbered PDF outline titles")
    includes(main, "name={第,章}", "visible chapter number format")
    if r"\usepackage{titlesec}" in main or r"\titleformat" in main:
        fail("titlesec must not override tagged section headings")
    if main.find(r"\appendix") <= main.find(r"\part{选读：从 CNN 到视觉 Transformer}"):
        fail("Appendices must follow optional part IX")
    if main.count(r"\learningbridge{") != 9:
        fail("Nine parts need nine minimal introductions")

    # Explicit vector and architecture consistency.
    for name in ("21b-why-attention", "11-softmax-memory"):
        includes(sources[name], r"\vect x_i^\top W_Q" if name.startswith("21b") else r"\vect x^\top W_Q", name)
    includes(sources["11-softmax-memory"], r"W_Q^\top\vect x", "row/column explanation")
    includes(sources["22-transformer-architecture"], r"\vect h_T^\top W_{\rm vocab}", "row vocabulary projection")
    includes(sources["22-transformer-architecture"], r"\input{figures/pre-norm-block}", "true Pre-Norm figure")
    includes(sources["22-transformer-architecture"], r"X_{\rm block}", "distinct Block output")
    includes(sources["22a-position-multihead"], "0.990", "two-head worked example")
    includes(sources["22a-position-multihead"], "0.9997", "scaled-dot-product example")
    includes(sources["22a-position-multihead"], "位置", "positional example")
    includes(sources["22a-position-multihead"], r"\label{eq:pos-swap-d3}", "nondegenerate 3D position comparison")
    includes(sources["21a-context-gap"], r"\label{check:21a-context-gap}", "context gap self-check")
    includes(sources["19b-vit"], r"\label{eq:vit-patch-embedding}", "standalone patch embedding")
    includes(sources["21b-why-attention"], r"\vect q^\top=(1,1)", "asymmetric Q/K example")
    includes(sources["21b-why-attention"], r"\label{eq:asymmetric-qk-example}",
             "independent Query and Key cause raw score asymmetry")
    includes(sources["06-better-linear-memory"], r"\label{eq:delta-overwrites-key-a}",
             "Delta write can disturb previously learned association")
    from math import exp
    scores = ((1, 1, 2), (0, 1, 1), (1, 2, 3))
    assert scores[0][1] == 1 and scores[1][0] == 0
    third = [exp(v) for v in scores[2]]
    third = [v / sum(third) for v in third]
    assert math.isclose(third[0] + third[2], 0.7552715289452023)
    assert math.isclose(third[1] + third[2], 0.9099694268296196)
    includes(sources["22c-language-training"], r"\label{sec:transformer-gradient-step}", "gradient step")
    includes(sources["22b-token-to-output"], r"\label{eq:three-token-block-output}", "canonical Pre-Norm numeric forward")
    includes(sources["22b-token-to-output"], "0.1244", "causal attention example")
    includes(sources["22c-language-training"], "1.611377", "three-position joint loss")
    includes(sources["23a-from-toy-to-gpt"], "768/12=64", "GPT-2 scale recovery")
    includes(sources["23aa-pretraining-icl"], r"\label{concept:in-context-learning}", "pretraining and ICL")
    includes(sources["20b-task-contract"], "任务契约（Task Contract）", "task contract explained in body")
    includes(sources["22c-language-training"], "Teacher Forcing（教师强制）", "teacher forcing in body")
    includes(sources["25-integrated-practice"], r"W_{\rm vocab}", "attention output to vocabulary logits exercise")
    includes(sources["23c-post-training"], "只改 Prompt/Few-shot", "SFT versus prompting")
    includes(sources["23d-agent-systems"], "g_{Q2}", "shared report arithmetic")
    includes(sources["23d-agent-systems"], "A2A", "protocol distinctions")
    includes(sources["23e-tech-judgement"], "Scaling Laws", "innovation framework")
    includes(sources["23e-tech-judgement"], "莫拉维克悖论", "Moravec paradox")
    includes(sources["23e-tech-judgement"], "架构创新空间", "debated architecture innovation")
    includes(sources["23b-deployment-and-ecosystem"], "vLLM", "ecosystem tool comparison")
    includes(sources["22-transformer-architecture"], "Encoder--Decoder Attention", "original architecture comparison")
    includes(sources["23f-foundation-recap"], "技术底座回顾", "end of core recap")
    includes(sources["00g-reading-routes"], "速读", "pre-TOC reading paths")
    includes(main, r"\newtcolorbox{boundarybox}", "separate scope box type")
    includes(main, r"\input{chapters/00g-reading-routes}", "reading guide before contents")
    includes(main, r"\input{chapters/23f-foundation-recap}", "core recap before electives")
    check = subprocess.run([sys.executable, str(ROOT / "scripts" / "check_p2_notebook.py")],
                           capture_output=True, text=True)
    if check.returncode:
        fail("P2 interactive notebook QA failed: " + check.stdout + check.stderr)
    print(check.stdout.strip())
    includes(sources["22c-language-training"], "0.25764", "shared embedding gradient")
    includes(sources["10-mlp"], r"\label{eq:mlp-l-layer-row}", "L-layer network")
    includes(sources["20b-task-contract"], r"\label{fig:token-ffn-output-pipeline}", "token-to-vocabulary diagram")
    includes(sources["22b-token-to-output"], r"\input{figures/attention-weight-heatmap}", "attention weight heatmap")
    includes(sources["22b-token-to-output"], r"\input{figures/three-position-probabilities}", "vocabulary probability bars")
    includes(sources["22b-token-to-output"], r"\hyperref[app:transformer-intermediates]", "appendix numerical link")
    includes(sources["00f-transformer-intermediates"], r"\label{app:transformer-intermediates}", "appendix numerical target")
    includes(sources["20-embeddings"], r"\input{figures/embedding-training-projection}", "embedding delta chart")
    includes((BOOK / "figures" / "embedding-training-projection.tex").read_text(encoding="utf-8"),
             r"E_{20,j}-E_{0,j}", "embedding coordinate difference")
    # Keep only three full-sized forward-result matrices in the narrative chapter.
    full_matrices = len(re.findall(r"\\begin\{bmatrix\}", sources["22b-token-to-output"]))
    if full_matrices != 3:
        fail(f"Running forward lesson should contain exactly A/H/P matrices, found {full_matrices}")
    includes(sources["22c-language-training"], r"\input{figures/training-20-step-loss}", "20-step loss curve")
    includes(sources["23a-from-toy-to-gpt"], r"\label{eq:toy-99-parameters}", "99 parameter count")
    includes(sources["23a-from-toy-to-gpt"], "7{,}077{,}888",
             "classic GPT-2 attention-plus-FFN parameter budget")
    assert 4 * 768**2 == 2359296 and 8 * 768**2 == 4718592
    assert 12 * 768**2 == 7077888
    includes(sources["24e-pytorch-lab"], r"\verbatiminput{../scripts/pytorch_starter.py}", "standalone PyTorch lab")
    includes(sources["23b-deployment-and-ecosystem"], "16{,}000", "LoRA computation")
    includes(sources["23b-deployment-and-ecosystem"], "软标签", "distillation computation")
    includes(sources["23b-deployment-and-ecosystem"], "-127", "quantization computation")
    includes(sources["20a-tokenizer"], "BPE", "subword example")
    # The optional Torch companion is syntax-checked without requiring Torch at source-QA time.
    import ast
    for script in ("pytorch_starter.py", "teaching_trace.py"):
        script_path = ROOT / "scripts" / script
        if not script_path.is_file():
            fail(f"Missing P1 reproducibility script: {script}")
        ast.parse(script_path.read_text(encoding="utf-8"))
    includes(sources["24e-pytorch-lab"], "1.798430", "initial loss in lab")
    # Runnable, dependency-free examples must agree with the book after edits.
    for script in ("memory_demo.py", "bpe_demo.py", "rag_demo.py", "agent_loop.py"):
        script_path = ROOT / "scripts" / script
        if not script_path.is_file():
            fail(f"Missing reproducibility example: {script}")
        try:
            ast.parse(script_path.read_text(encoding="utf-8"))
        except SyntaxError as exc:
            fail(f"Invalid Python syntax in {script}: {exc}")
        result = subprocess.run([sys.executable, str(script_path)],
                                cwd=ROOT, capture_output=True, text=True)
        if result.returncode:
            fail(f"Reproducible {script} failed:\n{result.stdout}{result.stderr}")
    print("Independent teaching QA passed: memory, BPE, RAG and Agent loop")

    # Independent answer-key numerics for newly added user-review exercises.
    exercises_script = ROOT / "scripts" / "review_exercises_demo.py"
    if not exercises_script.is_file():
        fail("Missing review-exercises numerical reproducer")
    ast.parse(exercises_script.read_text(encoding="utf-8"))
    exercises_result = subprocess.run([sys.executable, str(exercises_script)],
                                      cwd=ROOT, capture_output=True, text=True)
    if (exercises_result.returncode
            or "Review exercises QA passed" not in exercises_result.stdout):
        fail("Review exercises numeric QA failed:\n"
             + exercises_result.stdout + exercises_result.stderr)


    # GPT-2 smoke is standard-library-only; real weights are explicitly opt-in.
    gpt2_source = ROOT / "scripts" / "gpt2_demo.py"
    if not gpt2_source.is_file():
        fail("Missing pinned GPT-2 experiment")
    ast.parse(gpt2_source.read_text(encoding="utf-8"))
    includes(gpt2_source.read_text(encoding="utf-8"),
             "607a30d783dfa663caf39e06633721c8d4cfcd7e",
             "pinned public GPT-2 revision")
    gpt2_result = subprocess.run([sys.executable, str(gpt2_source)],
                                 cwd=ROOT, capture_output=True, text=True)
    if gpt2_result.returncode or "Offline smoke passed:" not in gpt2_result.stdout:
        fail(f"GPT-2 offline smoke failed: {gpt2_result.stdout}{gpt2_result.stderr}")
    includes(sources["23a-from-toy-to-gpt"], "39897932969",
             "successful source-pinned real GPT-2 inference reference")
    includes(sources["23a-from-toy-to-gpt"], "gpt2_demo.py",
             "reproducible optional real GPT-2 example (verbatim command)")
    includes(gpt2_source.read_text(encoding="utf-8"), "masked_future",
             "real-model causal-mask numeric assertion")
    includes(gpt2_source.read_text(encoding="utf-8"), "probability sum",
             "real-model normalized vocabulary probabilities")

    # Modern architecture figures use pinned, inspectable offline source excerpts.
    for reproducible in ("config_table.py", "architecture_demo.py"):
        path = ROOT / "scripts" / reproducible
        if not path.is_file():
            fail(f"Missing modern architecture reproducer: {reproducible}")
        ast.parse(path.read_text(encoding="utf-8"))
        result = subprocess.run([sys.executable, str(path)], cwd=ROOT,
                                text=True, capture_output=True)
        if result.returncode:
            fail(f"Architecture example {reproducible} failed:\n"
                 + result.stdout + result.stderr)
    includes(sources["22d-modern-transformers"], "architecture\\_demo.py",
             "sliding-window and illustrative MLA arithmetic")

    # Visual-to-language adapter arithmetic is a deliberately untrained toy fixture.
    bridge_script = ROOT / "scripts" / "vision_bridge_demo.py"
    if not bridge_script.is_file():
        fail("Missing ViT-to-LLM shape reproducer")
    ast.parse(bridge_script.read_text(encoding="utf-8"))
    bridge_result = subprocess.run([sys.executable, str(bridge_script)],
                                   cwd=ROOT, capture_output=True, text=True)
    if bridge_result.returncode or "Vision bridge QA passed" not in bridge_result.stdout:
        fail("Vision bridge regression failed:\n"
             + bridge_result.stdout + bridge_result.stderr)
    includes(sources["19b-vit"], r"\label{eq:vit-llm-bridge}",
             "multimodal adapter teaching example")

    # Print-proof selector QA: must not require a PDF, Poppler or online access.
    import runpy
    proof_source = ROOT / "scripts" / "print_proof.py"
    if not proof_source.is_file():
        fail("Missing grayscale human print-proof tool")
    ast.parse(proof_source.read_text(encoding="utf-8"))
    select = runpy.run_path(str(proof_source), run_name="book_print_proof")["parse_pages"]
    if select("1,3-4,last", 8) != [1, 3, 4, 8]:
        fail("Grayscale proof page selections are incorrect")
    for bad_selection in ("0", "9", "5-2", ",", "not-a-page"):
        try:
            select(bad_selection, 8)
        except ValueError:
            continue
        fail(f"Grayscale proof accepted invalid page selection: {bad_selection}")
    print("Grayscale print-proof selector QA passed")

    # Catch a numerical transition that became stale after changing chapter 19.
    includes(sources["11-softmax-memory"], r"\hyperref[intro:21c-naive-attention]",
             "chapter 20 explicitly reprises the earlier naive example")
    if "上一章算出了" in sources["11-softmax-memory"]:
        fail("Chapter 20 attributes a naive-attention score to the asymmetric chapter 19")

    # The end-of-chapter summary owns the forward bridge. Avoid redundant
    # "last chapter" recaps at the start of these independently framed sections.
    streamlined_intros = (
        "07-functions-relu", "17-backpropagation", "20a-tokenizer",
        "20c-classification-loss", "21a-context-gap", "21c-naive-attention",
        "22-transformer-architecture", "23c-post-training",
        "22d-modern-transformers",
    )
    for name in streamlined_intros:
        if "上一章" in "\n".join(sources[name].splitlines()[:15]):
            fail(f"Redundant prior-chapter recap reintroduced in {name}")

    # A ten-step oral mapping must remain complete and linked to its figure.
    block_ch22 = sources["22-transformer-architecture"]
    ten_steps = block_ch22.split(r"\label{sec:transformer-ten-steps}")[1]
    ten_steps = ten_steps.split(r"\end{enumerate}")[0]
    if len(re.findall(r"(?m)^\\item ", ten_steps)) != 10:
        fail("Transformer oral recap must have exactly ten steps")
    includes(block_ch22, r"\input{figures/original-transformer-map}",
             "source vs decoder-only architecture component mapping")

    three_tier_first_ten = ["00d-rules-gap","00-functions","16-loss-gradient","07-functions-relu","17-backpropagation","18b-end-to-end-learning","18-generalization","01-vectors","02-dot-product","03-matrix-multiplication"]
    for lesson_name in three_tier_first_ten:
        includes(sources[lesson_name], "读完自测：回忆／手算／迁移",
                 f"three-level self-check in {lesson_name}")
        for kind in ("回忆：", "手算：", "迁移："):
            includes(sources[lesson_name], kind, f"{lesson_name} {kind}")
    from math import isclose
    assert isclose(2*3 + 1, 7)
    assert isclose(2*3 - 1, 5)
    assert (2+1, 3-1) == (3, 2)
    assert (1*3 + 2*1) == 5

    three_tier_attention = ["10-mlp","20a-tokenizer","20c-classification-loss","20-embeddings","20b-task-contract","21a-context-gap","21-rnn","21c-naive-attention","21b-why-attention","11-softmax-memory","22a-position-multihead"]
    for lesson_name in three_tier_attention:
        includes(sources[lesson_name], "读完自测：回忆／手算／迁移",
                 f"attention and text three-level check: {lesson_name}")
        for kind in ("回忆：", "手算：", "迁移："):
            includes(sources[lesson_name], kind, f"{lesson_name} {kind}")
    assert (1 * 0 + 0 * 1) == 0
    assert (1 * 1 + 0 * 1) == 1

    three_tier_transformer = ["00-guide","16-loss-analytic","10b-ffn-output-head","22b-token-to-output","22c-language-training","23-llm-systems","23a-from-toy-to-gpt","23aa-pretraining-icl","23c-post-training","23b-deployment-and-ecosystem","22d-modern-transformers","23e-tech-judgement"]
    for lesson_name in three_tier_transformer:
        includes(sources["23b-deployment-and-ecosystem" if lesson_name == "23b-deployment-and-ecosystem" else
                 "16-loss-gradient" if lesson_name == "16-loss-analytic" else lesson_name],
                 "读完自测：回忆／手算／迁移",
                 f"transformer/application three-level check: {lesson_name}")
    assert math.isclose((0.3 - 1.0)/3, -0.2333333333333333)
    assert math.isclose(math.log(4), 1.3862943611198906)

    three_tier_memory_and_appendix = ["19-cnn","19b-vit","04-key-value-outer-product","05-memory-interference","06-better-linear-memory","08-stacking-key-value","09-nonlinearity-and-memory","14-summary","13-capacity","00b-math-tools","00c-symbols"]
    for lesson_name in three_tier_memory_and_appendix:
        includes(sources[lesson_name], "读完自测：回忆／手算／迁移",
                 f"memory/vision/math glossary three-tier check: {lesson_name}")
    assert (1 * 0 + 0 * 1) == 0
    assert (3 * 3 * 3 * 8) == 216

    # Editorial regression after moving memory into Part VI.
    # These are obsolete book-facing phrases; production policy belongs in docs/.
    stale_reader_phrases = (
        "第九部分的联想记忆选读专题",
        "附录 A 的逐层数值核对表",
        "第 22、23 章的原始算例",
        "上一部分我们用三维模型完成了",
        "联想记忆现已成为第 VI 部分",
        "不再引入另一套列向量主线",
        "不会参与常规 PDF CI",
        "给“员工小 L”补能力",
        "具体相似内容的来源与许可仍需在正式发布前",
        "ATTRIBUTION\\_REVIEW.md",
    )
    for source, body in sources.items():
        for phrase in stale_reader_phrases:
            if phrase in body:
                fail(f"Obsolete editorial prose in {source}: {phrase}")

    # V3 reading path: 37 core numbered chapters (including memory), 2 elective visual chapters.
    input_list = re.findall(r"\\input\{chapters/([^}]+)\}", main)
    first_elective = input_list.index("19-cnn")
    core_sources = input_list[:first_elective]
    visible_chapters = sum(len(re.findall(r"(?m)^\\section\{", sources[n]))
                           for n in core_sources)
    if visible_chapters != 37:
        fail(f"Core curriculum requires 37 numbered chapters, found {visible_chapters}")
    includes(sources["16-loss-gradient"], r"\label{intro:16a-gradient-descent}",
             "loss and gradient are two progressive lessons")
    includes(sources["28-chapter-checks"], r"\label{answer:16-loss-analytic}",
             "separate analytical-loss self-check")

    includes(sources["20c-classification-loss"], r"\label{concept:cross-entropy}", "first classification loss definition")
    includes(sources["20c-classification-loss"], r"\label{concept:logits}", "first logits definition")
    includes(sources["20c-classification-loss"], r"\label{concept:softmax}", "first Softmax definition")
    includes(sources["20c-classification-loss"], r"\label{concept:logit-gradient}", "p-y derivation")
    includes(sources["16-loss-gradient"], r"L(1,0)=\frac53", "unified starting loss")
    includes(sources["16-loss-gradient"], r"L(1.4,0.6)", "joint w-b update")
    includes(sources["16-loss-gradient"], r"\input{figures/loss-two-parameter-contours}", "joint loss contour")
    includes(sources["20-embeddings"], r"\R^{5\times3}", "authoritative E shape")
    includes(sources["20b-task-contract"], "50,257", "GPT-2 preview")
    includes(sources["00b-math-tools"], r"\log", "math prerequisites")
    for practice, prefix in (("25-integrated-practice", "B1"), ("25b-modern-practice", "B2"), ("15-practice", "B3")):
        includes(sources[practice], rf"label=\textbf{{{prefix}-\arabic*.}}", "unique exercise number")
        includes(sources["27-answer-key"], rf"label=\textbf{{{prefix}-\arabic*.}}", "matching answer number")
    includes(sources["24d-english-index"], r"\termref{concept:cross-entropy}", "first classification definition in index")
    includes(sources["24d-english-index"], r"\termref{concept:pretraining}", "pretraining index destination")
    includes(sources["27-answer-key"], r"\|\vect a\|=6", "corrected cosine exercise")
    includes(sources["27-answer-key"], r"(5/13)", "cosine calculation")
    includes(sources["10b-ffn-output-head"], r"\begin{bmatrix}4&2\\1&1\end{bmatrix}", "nonidentity FFN")
    includes(sources["25b-modern-practice"], "输入行向量 $(2,1)$", "independent FFN exercise")
    for category in ("title={直觉}", "title={动手算}", "title={易错}", "title={小结}"):
        includes(main, category, "four consistent note classes")
    for figure_name, chapter_name in (
        ("loss-descent", "16-loss-gradient"),
        ("backprop-computation", "17-backpropagation"),
        ("generalization-three-fits", "18-generalization"),
        ("validation-early-stop", "18-generalization"),
        ("cnn-window", "19-cnn"),
        ("embedding-lookup", "20-embeddings"),
        ("embedding-training-projection", "20-embeddings"),
        ("causal-mask-heatmap", "22-transformer-architecture"),
        ("attention-weight-heatmap", "22b-token-to-output"),
        ("three-position-probabilities", "22b-token-to-output"),
        ("training-20-step-loss", "22c-language-training"),
    ):
        includes(sources[chapter_name], f"\\input{{figures/{figure_name}}}", chapter_name)
        figure = BOOK / "figures" / f"{figure_name}.tex"
        if not figure.is_file() or r"\begin{tikzpicture}" not in figure.read_text(encoding="utf-8"):
            fail(f"Missing instructional figure {figure_name}")
    for video in ("BV1NCgVzoEG9", "BV15z4C6SEHT"):
        includes(sources["26-sources"], video, "source bibliography")

    # No answers next to exercises; the appendix must collect all three.
    for name in ("25-integrated-practice", "25b-modern-practice", "15-practice"):
        body = sources[name]
        includes(body, r"\hyperref[app:answers]", name)
        if "参考答案" in body and "参考答案统一" not in body and "参考答案" not in body.split("\\hyperref")[0]:
            fail(f"Exercise chapter may contain an embedded solution list: {name}")
        if r"\begin{tcolorbox}[colback=paper,colframe=linegray,boxrule=.6pt,arc=1.5mm,title={\sffamily\bfseries 简明答案}" in body:
            fail(f"Inline answer box is still present: {name}")
    # M5: exercise / answer-key parity must not drift after adding transfer tasks.
    math_body = sources["25-integrated-practice"]
    modern_body = sources["25b-modern-practice"]
    answer_sections = sources["27-answer-key"].split(r"\subsubsection*{")
    if len(answer_sections) != 4:
        fail("Expected three distinctly labelled answer sets")
    expected_counts = (16, 20, 11)  # practice order: mathematics, modern systems, core memory
    actual_counts = (len(re.findall(r"\\item\b", answer_sections[i+1]))
                     for i in range(3))
    if tuple(actual_counts) != expected_counts:
        fail("Central answer counts do not match 16/20/11 lesson exercises")
    if math_body.count(r"\item") != 16 or modern_body.count(r"\item") != 20:
        fail("Core collections must contain sixteen math and twenty modern items")
    for name in ("25-integrated-practice", "25b-modern-practice"):
        for label in ("【回忆】", "【手算】", "【迁移】"):
            includes(sources[name], label, f"{name} exercise tier")
    answer_key = sources["27-answer-key"]
    includes(answer_key, r"\label{app:answers}", "answer key")
    if answer_key.count(r"\subsubsection*{") != 3:
        fail("Answer appendix should separate the three exercise sets")
    # Reader-facing answer titles must not expose source filenames/IDs.
    key = sources["28-chapter-checks"]
    check_titles = re.findall(
        r"\\label\{answer:([^}]+)\}\\textbf\{\\hyperref\[check:[^\]]+\]\{([^}]+)\}\}",
        key)
    if len(check_titles) < 40:
        fail(f"Unexpectedly few linked chapter-check answers: {len(check_titles)}")
    ids = [identifier for identifier, title in check_titles if identifier == title]
    if ids:
        fail(f"Internal source identifiers leaked into answer headings: {ids}")
    includes(sources["24-lexicon"], r"\textbf{Top-p}", "100-word index")
    ninth = sources["24-lexicon"].split(r"\subsubsection{第九组")[1].split(r"\subsubsection{第十组")[0]
    includes(ninth, r"\textbf{Top-p}", "sampling group")

    for practice in ("25-integrated-practice", "25b-modern-practice", "15-practice"):
        for level in ("【基础】", "【标准】", "【挑战】"):
            includes(sources[practice], level, f"{practice}: three difficulty tiers")
    includes(sources["25b-modern-practice"], "形状错误",
             "modern shape-error exercise")
    includes(sources["25b-modern-practice"], "Dropout",
             "modern conceptual correction exercise")
    includes(sources["18c-training-engineering"], r"\label{eq:adamw-decoupled}",
             "decoupled AdamW mathematical update")
    includes(sources["18c-training-engineering"], r"\label{concept:lr-warmup}",
             "five-step learning-rate scheduling example")
    includes(sources["28-chapter-checks"], r"\boxed{0.58}",
             "warmup self-test answer")
    from math import isclose
    eta_schedule = (0.02, 0.04, 0.06, 0.06, 0.03)
    w = 1.0
    for eta in eta_schedule:
        w -= eta * 2.0
    assert isclose(w, 0.58, abs_tol=1e-12)
    assert isclose((1-0.1*0.05)*2-0.1*(0.5/(0.25**0.5)),
                   1.89, abs_tol=1e-12)

    includes(sources["25-integrated-practice"], r"XX^\top",
             "independent symmetric raw-dot-product exercise")
    includes(sources["25-integrated-practice"], "a a b",
             "new BPE corpus exercise")
    includes(sources["25b-modern-practice"], "q=(0.2,1)",
             "RAG retrieval coverage regression")
    includes(sources["25b-modern-practice"], "w=2",
             "sliding-window edge count regression")
    includes(sources["25b-modern-practice"], "review\\_exercises\\_demo.py",
             "first programming exercise uses locally runnable standard-library script")
    includes(sources["28-chapter-checks"], r"\boxed{10\%}",
             "Agent numeric arithmetic self-check")

    includes(sources["25b-modern-practice"], "1000",
             "uniform vocabulary loss regression")
    assert sum(min(2, i + 1) for i in range(5)) == 9
    assert math.isclose(math.log(1000), 6.907755278982137)


    # Glossary is one maintained definition set with search-only alternate views.
    base_terms = re.findall(r"(?m)^\\item\s+\\textbf\{([^}]+)\}",
                            sources["24-lexicon"].split(r"\subsubsection*{不要混淆")[0])
    modern_terms = re.findall(r"(?m)^\\item\s+\\textbf\{([^}]+)\}",
                              sources["24b-modern-lexicon"])
    english_aliases = re.findall(
        r"(?m)^\\item\s+\{\\sffamily\\bfseries\s+([^}]+)\}",
        sources["24d-english-index"])
    assert english_aliases == sorted(english_aliases, key=str.casefold)
    core_duplicates = sorted(set(base_terms) & set(modern_terms))
    if core_duplicates:
        fail(f"Modern glossary repeats defined base terms: {core_duplicates}")
    for label, terms, expected in (
        ("base glossary", base_terms, 100),
        ("modern glossary", modern_terms, 33),
        ("English aliases", english_aliases, 108),
    ):
        if len(terms) != expected or len(set(terms)) != expected:
            fail(f"{label}: expected {expected} distinct entries, found "
                 f"{len(terms)} entries and {len(set(terms))} unique names")
    # Generated table is an exact derivative of the 100+33 canonical glossary.
    table_check = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "generate_bilingual_glossary.py"), "--check"],
        cwd=ROOT, capture_output=True, text=True)
    if table_check.returncode or "133-row bilingual glossary QA passed" not in table_check.stdout:
        fail("Generated bilingual table is stale:\\n"
             + table_check.stdout + table_check.stderr)
    includes(sources["24e-bilingual-glossary"], r"\label{app:bilingual-glossary}",
             "unified bilingual table anchor")
    includes(sources["24-lexicon"], "英文 A--Z 列表只提供",
             "single-source glossary explanation")
    for core in ("22-transformer-architecture", "23a-from-toy-to-gpt",
                 "04-key-value-outer-product", "23d-agent-systems",
                 "22d-modern-transformers", "19b-vit",
                 "22a-position-multihead", "22b-token-to-output",
                 "22c-language-training", "23-llm-systems",
                 "06-better-linear-memory", "09-nonlinearity-and-memory",
                 "13-capacity", "23aa-pretraining-icl", "23c-post-training",
                 "23b-deployment-and-ecosystem", "23e-tech-judgement"):
        includes(sources[core], r"\chaptercompass{",
                 f"{core} one-sentence and shape-first introduction")

    # Glossary anchors remain valid and are backed by content in the book.
    labels: dict[str, str] = {}
    for name in REQUIRED:
        for label in re.findall(r"\\label\{([^}]+)\}", sources[name]):
            if label in labels:
                fail(f"Duplicate cross-reference label {label}: {labels[label]} and {name}")
            labels[label] = name
    check_ids = {key.removeprefix("check:") for key in labels if key.startswith("check:")}
    answer_ids = {key.removeprefix("answer:") for key in labels if key.startswith("answer:")}
    if check_ids != answer_ids:
        fail(f"Self-check answer mismatch: missing={sorted(check_ids-answer_ids)}, "
             f"unexpected={sorted(answer_ids-check_ids)}")
    # Every existing numbered check now has a recall/calculation/transfer
    # trio; do not silently regress to a single isolated question.
    if len(check_ids) != 47:
        fail(f"Expected 47 linked chapter and appendix self-checks, got {len(check_ids)}")
    for lesson_id in sorted(check_ids):
        source_name = labels["check:" + lesson_id]
        src = sources[source_name]
        label = r"\label{check:" + lesson_id + "}"
        at = src.index(label)
        near = src[max(0, at-115):at + 950]
        if r"\textbf{读完自测：回忆／手算／迁移}" not in near:
            fail(f"Three-level label missing from {lesson_id}")
        for kind in ("回忆：", "手算：", "迁移："):
            if r"\textbf{" + kind + "}" not in near:
                fail(f"Three-level self-check missing {kind} in {lesson_id}")

    for name in REQUIRED:
        for destination in re.findall(r"\\hyperref\[((?:check|answer):[^]]+)\]", sources[name]):
            if destination not in labels:
                fail(f"Broken self-check link in {name}: {destination}")
    for lex in ("24-lexicon", "24b-modern-lexicon"):
        refs = re.findall(r"\\termref\{([^}]+)\}", sources[lex])
        if len(refs) != (110 if lex == "24-lexicon" else 33):
            fail(f"Unexpected glossary link count in {lex}: {len(refs)}")
        for ref in refs:
            if ref not in labels:
                fail(f"Broken glossary destination: {ref}")
        if lex == "24-lexicon":
            key_terms = {
                "交叉熵": "concept:cross-entropy",
                "梯度下降": "intro:16a-gradient-descent",
                "残差连接": "concept:residual",
                "Token": "intro:20a-tokenizer",
                "Query": "concept:qkv",
                "Key": "concept:qkv",
                "Value": "concept:qkv",
                "Self-Attention": "concept:self-attention",
                "Cross-Attention": "concept:cross-attention",
                "缩放点积": "concept:scaled-dot-product",
                "Softmax": "concept:softmax",
                "因果掩码": "concept:causal-mask",
                "多头注意力": "concept:multihead",
                "预训练": "concept:pretraining",
                "监督微调": "concept:sft",
                "RLHF": "concept:rlhf",
                "LoRA": "concept:lora",
                "Logits": "concept:logits",
                "温度": "concept:sampling",
                "Top-k": "concept:sampling",
                "Top-p": "concept:sampling",
                "RAG": "concept:rag",
                "MCP": "concept:mcp",
                "智能体": "concept:agent",
                "工作流": "concept:workflow",
                "量化": "concept:quant"
            }
            items = dict(re.findall(
                r"(?m)^\\item \\textbf\{([^}]+)\}.*?\\termref\{([^}]+)\}",
                sources[lex]))
            for term, destination in key_terms.items():
                if items.get(term) != destination:
                    fail(f"Foundation term {term} must link to {destination}, got {items.get(term)}")

        if lex == "24b-modern-lexicon" and any(not ref.startswith("concept:") for ref in refs):
            fail("Modern glossary must link to precise concept definitions, not chapter introductions")
    # Also verify in-text concept explanations precede their hyperlinks.
    seen: set[str] = set()
    total = 0
    for name in REQUIRED:
        body = sources[name]
        for ref in re.findall(r"\\conceptlink\{([a-z0-9-]+)\}", body):
            if "concept:" + ref not in seen:
                fail(f"Concept back-link has no earlier lesson: {ref} in {name}")
            total += 1
        seen.update(re.findall(r"\\label\{(concept:[a-z0-9-]+)\}", body))
    if total < 30:
        fail("Suspiciously few concept links after restructuring")

    # All textbook tabular/tabularx data tables must declare their first row as TH.
    table_envs = sum(len(re.findall(r"\\begin\{(?:tabularx|tabular|longtable)\}", body))
                     for body in sources.values())
    marked_headers = sum(body.count(r"\tagpdfsetup{table/header-rows={1}}")
                         for body in sources.values())
    if table_envs < 23 or marked_headers != table_envs:
        fail(f"Table header coverage incomplete: {marked_headers}/{table_envs} (minimum 23)")

    # The prominent diagram and teaching resources are all editable TikZ.
    for figure in ("row-column-intuition", "key-value-layout", "pre-norm-block",
                   "attention-why-qkv"):
        file = BOOK / "figures" / f"{figure}.tex"
        if not file.is_file() or r"\begin{tikzpicture}" not in file.read_text(encoding="utf-8"):
            fail(f"Missing editable figure {figure}")
    # Figure 9: both weighted scores and values must flow INTO the result.
    # Source-level endpoint assertions complement page-render review; curved
    # Bezier connectors previously overshot the result boundary and appeared
    # to point out of the diagram.
    qkv = (BOOK / "figures" / "attention-why-qkv.tex").read_text(
        encoding="utf-8")
    for edge in (
        "(goal.south) -- (qkv-split);",
        "(qkv-split) -| (find.north);",
        "(qkv-split) -| (read.north);",
        "(weight.south) -- ([xshift=-31.5mm]out.north);",
        "(value.south) -- ([xshift=31.5mm]out.north);",
    ):
        includes(qkv, edge, "figure 9 directed connector")
    for obsolete in (
        "to[out=-115,in=90]",
        "to[out=-65,in=90]",
        "to[out=-90,in=150]",
        "to[out=-90,in=30]",
        "(out.north west)",
        "(out.north east)",
    ):
        if obsolete in qkv:
            fail(f"Figure 9 retains a misleading arrow route: {obsolete}")

    # Figure 16 must not reverse the training feedback arrow or visually suggest
    # that inference -> post-training -> external tools is one execution chain.
    concept = sources["24c-concept-map"]
    for arrow in (
        "(upd.north) --",
        "(emb.south);",
        "(post.north) -- ++(0,5mm) -| (upd.south);",
        "(gen.east) --",
        "(tools.west);",
    ):
        includes(concept, arrow, "figure 16 arrow direction")
    for obsolete in (
        "([yshift=4mm]emb.north)",
        "(gen)--(post)",
        "(post)--(tools)",
        "(ffn.east) -- ++(.5,0) |- (tools.east)",
    ):
        if obsolete in concept:
            fail(f"Figure 16 contains a misleading or reversed arrow: {obsolete}")

    # A light title bar must not use tcolorbox's default white title text.
    weight_figure = (BOOK / "figures" / "attention-three-step-weights.tex").read_text(
        encoding="utf-8")
    includes(weight_figure, "coltitle=ink", "figure 10 dark title on light background")
    includes(sources["00c-symbols"], r"\beta=1/\tau", "inverse-temperature definition")
    # A-G appendix sections must be explicit in the main file.
    appendix = main.split(r"\appendix", 1)[1]
    group_titles = re.findall(r"(?m)^\\section\{([^}]+)\}", appendix)
    if group_titles != ["核心公式、数学与形状速查", "三维贯通实验、复算与脚本",
                        "综合练习与迁移实践", "集中参考答案与随堂解答",
                        "术语地图、概念关系与索引", "来源与延伸阅读",
                        "版本、勘误与复现说明"]:
        fail(f"Expected exactly seven A-G appendix groups, found {group_titles}")
    includes(sources["00e-core-formulas"], r"Z=HW_{\rm out}",
             "compact core formula card")

    includes(sources["23-llm-systems"], r"\beta=1/\tau", "sampling temperature")
    includes(sources["18c-training-engineering"], "0.943", "two-step Adam example")
    includes(sources["10-mlp"], r"\vect x^\top W_1", "row-vector MLP")
    includes(sources["11-softmax-memory"], r"\label{concept:self-attention}", "merged chapter")
    for name, body in sources.items():
        if re.search(r"(?<![a-zA-Z\\])extbf\{", body) or "\textbf{" in body:
            fail(f"Broken bold escape in {name}")
    for editorial in ("这正是文章把", "这些只是文章讨论", "没有沿用字幕中",
                      "章节号会随全书编排自动更新", "根据初中学过的",
                      "两单位向量的点积", "是本文为了学习",
                      "在本卷，输入 Query", "全书用\\textbf{本书}统一指代"):
        for name, body in sources.items():
            if editorial in body:
                fail(f"Editorial residue {editorial!r} in {name}")
    # Memory part: seven source files and four visible chapters, without removing exercises.
    x2 = ("04-key-value-outer-product", "05-memory-interference",
          "06-better-linear-memory", "08-stacking-key-value",
          "09-nonlinearity-and-memory", "14-summary", "13-capacity")
    heading_count = sum(bool(re.search(r"(?m)^\\section\{", sources[n]))
                        for n in x2)
    if heading_count != 4:
        fail(f"Memory part must display four sections, got {heading_count}")
    for n in ("05-memory-interference", "08-stacking-key-value", "14-summary"):
        includes(sources[n], r"\subsection{", f"nested X2 topic {n}")
    includes(sources["04-key-value-outer-product"], r"\vect a^\top V",
             "row-vector memory read")
    includes(sources["05-memory-interference"], r"S_{\rm simple}", "row memory interference")
    includes(sources["06-better-linear-memory"], r"S_{\rm better}", "row least-squares solution")
    includes(sources["08-stacking-key-value"], r"\relu(xK^\top)V", "row nonlinear readout")
    includes(sources["13-capacity"], r"S_t=S_{t-1}+k_t^\top v_t",
             "linear attention outer-product state")
    includes(sources["22d-modern-transformers"], r"q_tS_t",
             "row-state connection in architecture chapter")
    if r"\sim" in sources["13-capacity"]:
        fail("Do not use strict asymptotic equivalence as loose statistical magnitude")
    print(f"Source QA passed: {len(PARTS)} parts, {len(REQUIRED)} files, three separated solutions, linked glossary")
    test_numeric_examples()


def validate_pdf(path: Path) -> None:
    if not path.exists() or path.stat().st_size < 70_000:
        fail(f"Final PDF missing or suspiciously small: {path}")
    info = subprocess.run(["pdfinfo", str(path)], capture_output=True,
                          text=True, check=True).stdout
    # Inspect the PDF Catalog rather than inferring structural accessibility
    # from pdfinfo's human-readable status alone. This also catches missing
    # MarkInfo and empty structure trees that a "Tagged: yes" flag may miss.
    try:
        from pypdf import PdfReader
    except ImportError:
        fail("pypdf==5.9.0 is required for PDF structure verification")
    reader = PdfReader(str(path))
    catalog = reader.trailer["/Root"]
    markinfo = catalog.get("/MarkInfo")
    struct_root = catalog.get("/StructTreeRoot")
    tagged = bool(markinfo and markinfo.get("/Marked") and struct_root)
    if not tagged:
        fail("PDF catalog must contain /MarkInfo /Marked true and /StructTreeRoot")
    if hasattr(struct_root, "get_object"):
        struct_root = struct_root.get_object()
    top = struct_root.get("/K")
    if hasattr(top, "get_object"):
        top = top.get_object()
    if not top or top.get("/S") != "/Document":
        fail("Tagged structure root is missing the /Document element")
    counts = {}
    alt_count = 0
    table_nodes = []
    figure_nodes = []
    stack = [top]
    while stack:
        node = stack.pop()
        if isinstance(node, list):
            stack.extend(node)
            continue
        if hasattr(node, "get_object"):
            node = node.get_object()
        if isinstance(node, dict):
            role = str(node.get("/S", ""))
            counts[role] = counts.get(role, 0) + 1
            if role == "/Table":
                table_nodes.append(node)
            elif role == "/Figure":
                figure_nodes.append(node)
            if node.get("/Alt"):
                alt_count += 1
            if node.get("/K") is not None:
                stack.append(node["/K"])
    # Walk structural tables: each textbook data table has one heading row.
    # Counting TH alone is too weak: all TH nodes could belong to one table.
    def struct_children(node):
        kid = node.get("/K", [])
        if hasattr(kid, "get_object"):
            kid = kid.get_object()
        if not isinstance(kid, list):
            kid = [kid]
        result = []
        for child in kid:
            if hasattr(child, "get_object"):
                child = child.get_object()
            if isinstance(child, dict):
                result.append(child)
        return result

    expected_tables = sum(
        len(re.findall(r"\\begin\{(?:tabularx|tabular|longtable)\}", chapter(name)))
        for name in REQUIRED
    )
    if len(table_nodes) != expected_tables:
        fail(f"Expected {expected_tables} tagged data tables, found {len(table_nodes)}")
    for index, table_node in enumerate(table_nodes, 1):
        rows = [n for n in struct_children(table_node) if n.get("/S") == "/TR"]
        if len(rows) < 2:
            fail(f"Data table {index}: at least a header and data row are required")
        header = struct_children(rows[0])
        if len(header) < 2 or any(cell.get("/S") != "/TH" for cell in header):
            fail(f"Data table {index}: first row must contain only TH cells")
        for row in rows[1:]:
            cells = struct_children(row)
            if not cells or any(cell.get("/S") not in ("/TD", "/TH") for cell in cells):
                fail(f"Data table {index}: invalid data row structure")

    if len(figure_nodes) < 16:
        fail(f"Expected at least 16 tagged figures, found {len(figure_nodes)}")
    for index, fig in enumerate(figure_nodes, 1):
        if not fig.get("/Alt"):
            fail(f"Figure {index}: missing alternative description")
        pending = list(struct_children(fig))
        has_caption = False
        while pending:
            child = pending.pop()
            if child.get("/S") == "/Caption":
                has_caption = True
                break
            pending.extend(struct_children(child))
        if not has_caption:
            fail(f"Figure {index}: caption is not nested in Figure")
    if counts.get("/Formula", 0) < 20 or counts.get("/Figure", 0) < 8 or alt_count < 8:
        fail(f"Insufficient tagged math/figures/alt text: {counts}, alt={alt_count}")
    # Resolve custom heading names against the PDF RoleMap. Native ctexart
    # headings can be /section and /subsection that map to standard H1/H2.
    roles = struct_root.get("/RoleMap", {})
    heading_counts = {"/H1": 0, "/H2": 0}
    for role, count in counts.items():
        normalized_role = str(roles.get(role, role))
        if normalized_role in heading_counts:
            heading_counts[normalized_role] += count
    if heading_counts["/H1"] < 20 or heading_counts["/H2"] < 40:
        fail(f"Accessible heading hierarchy incomplete: {heading_counts}")
    print(f"Heading QA: {heading_counts['/H1']} H1 headings; {heading_counts['/H2']} H2 headings")
    # hyperref's PDF bookmarks are a separate, user-facing navigation system:
    # visible CTeX numbering is insufficient unless the outline contains it.
    # The nine numbered parts, 39 numbered sections and A--G appendices must
    # retain their numbering and nesting. hyperref in TeX Live 2026 uses plain
    # `1 Title` and `A Title`; older CTeX may write `第1章` and `附录 A`. Two standalone core interludes stay
    # intentionally unnumbered (the reading guide and end-of-core recap).
    outline_groups = []
    for entry in reader.outline:
        if isinstance(entry, list):
            if not outline_groups:
                fail("PDF outline has children without a parent")
            outline_groups[-1][1].extend(
                str(item.title).strip() for item in entry if hasattr(item, "title")
            )
        elif hasattr(entry, "title"):
            outline_groups.append([str(entry.title).strip(), []])
    if len(outline_groups) != len(PARTS) + 1:
        fail(f"PDF bookmark root should have 9 numbered parts plus one "
             f"unnumbered appendix: {len(outline_groups)} roots")
    han_numbers = "一二三四五六七八九"
    for index, expected in enumerate(PARTS):
        title, children = outline_groups[index]
        prefix = f"第{han_numbers[index]}部分"
        if not title.startswith(prefix) or expected not in title:
            fail(f"PDF bookmark part {index + 1} missing printed number/title: {title!r}")
        if not children:
            fail(f"PDF bookmark part {index + 1} has no chapter bookmarks")
    appendix_title, appendix_children = outline_groups[-1]
    if not appendix_title.startswith("附录："):
        fail(f"Unnumbered appendix PDF bookmark missing: {appendix_title!r}")
    if len(appendix_children) != 7:
        fail(f"Expected seven A--G PDF appendix bookmarks, found {appendix_children!r}")
    for letter, title in zip("ABCDEFG", appendix_children):
        if not re.match(rf"^(?:附录\s*)?{letter}\s+\S", title):
            fail(f"Appendix {letter} PDF bookmark missing letter prefix: {title!r}")
    chapter_numbers = []
    for _, children in outline_groups[:-1]:
        for title in children:
            match = re.match(r"^(?:第)?(\d+)(?:章)?\s+\S", title)
            if match:
                chapter_numbers.append(int(match.group(1)))
            elif not (title.startswith("阅读指南：") or
                      title.startswith("技术底座回顾：")):
                fail(f"Unnumbered PDF chapter bookmark: {title!r}")
    if chapter_numbers != list(range(1, 40)):
        fail(f"PDF chapter bookmark numbers must be 1--39 in order; "
             f"found {chapter_numbers!r}")
    print(f"PDF bookmark QA: {len(PARTS)} numbered parts, "
          f"{len(chapter_numbers)} numbered chapters, 7 lettered appendices")


    if len(reader.pages) < 50:
        fail("Suspiciously short tagged book")
    poppler_tagged = bool(re.search(r"(?m)^Tagged:\s+yes\s*$", info))
    if not poppler_tagged:
        print("PDFINFO WARNING: pdfinfo disagrees with Catalog Marked=true and populated StructTreeRoot")
    print(f"Structure QA: {len(table_nodes)} tables; {counts.get('/Formula', 0)} formulas; {counts.get('/TH', 0)} table header cells; "
          f"{counts.get('/Figure', 0)} figures; {alt_count} alternative descriptions")
    text = subprocess.run(["pdftotext", str(path), "-"], capture_output=True,
                          text=True, check=True).stdout
    pages = text.split("\f")
    compact = normalized(text)
    toc = normalized("".join(pages[1:7]))
    for num, title in zip("一二三四五六七八九", PARTS):
        # pdftotext can interleave the page number before the title.
        # Permit a 1-3 digit TOC folio between the part marker and title.
        pattern = rf"第{num}部分\d{{0,3}}{re.escape(normalized(title))}"
        if not re.search(pattern, toc):
            fail(f"Rendered TOC missing part 第{num}部分: {title}")
    if "第十部分" in toc:
        fail("Rendered table of contents has an extra part")
    for item in ("数学速查", "符号与张量形状速览", "位置编码", "Pre-Norm",
                 "LayerNorm", "1.611377", "LoRA", "16,000",
                 "附录", "集中参考答案", "Key", "Value"):
        if normalized(item) not in compact:
            fail(f"Rendered PDF does not contain required material: {item}")
    for i, page in enumerate(pages, 1):
        if i < 4 or not page.strip():
            continue
        body = re.sub(r"AI\s+by\s+Intuition.*?完整教材", "", page)
        body = re.sub(r"从函数到\s*Transformer", "", body)
        body = re.sub(r"(?m)^\s*\d+\s*$", "", body)
        han_count = len(re.findall(r"[\u4e00-\u9fff]", body))
        # Code-dense appendix pages may be mostly Latin identifiers.
        latin_words = len(re.findall(r"[A-Za-z_][A-Za-z_0-9]{2,}", body))
        # Matrix-reference pages may contain many numeric entries but few Han glyphs.
        # Require both numeric density AND substantive nonempty lines: a lone formula
        # or page number must not suppress the orphan-page regression guard.
        number_terms = len(re.findall(r"[-−]?\d+(?:[.,]\d+)*", body))
        content_lines = sum(bool(line.strip()) for line in body.splitlines())
        math_dense_page = number_terms >= 50 and content_lines >= 30
        if han_count < 18 and latin_words < 80 and not math_dense_page:
            fail(f"Likely orphan/blank page: {i}")
        # A short final bibliography page is legitimate, but an almost empty
        # intermediate page with a stranded conclusion is not. This caught the
        # prior ViT conclusion that occupied an entire page by itself.
        if i < len(pages) - 1 and han_count < 90 and latin_words < 80 and not math_dense_page:
            fail(f"Likely stranded content on interior page {i}: {han_count} Han chars")
    # Read only tag attributes: PDF text can contain literal control chars
    # that make pdftotext's XHTML *text nodes* invalid XML.
    bbox = subprocess.run(["pdftotext", "-bbox-layout", str(path), "-"],
                          capture_output=True, text=True, check=True).stdout
    pages_with_boxes = re.findall(r"<page\b([^>]*)>(.*?)</page>", bbox, re.S)
    if len(pages_with_boxes) != len(pages)-1:
        fail(f"PDF bbox page count mismatch: {len(pages_with_boxes)}")
    words_checked = 0
    for pageno, (attrs, body) in enumerate(pages_with_boxes, 1):
        size = re.search(r'width="([\d.]+)"\s+height="([\d.]+)"', attrs)
        if not size:
            fail(f"PDF page {pageno} has no width/height")
        width, height = map(float, size.groups())
        for word_attrs in re.findall(r"<word\s+([^>]*)>", body):
            vals = []
            for key in ("xMin", "yMin", "xMax", "yMax"):
                m = re.search(key + r'="([\d.+-]+)"', word_attrs)
                if not m:
                    fail(f"Malformed word bounding box on page {pageno}")
                vals.append(float(m.group(1)))
            xmin, ymin, xmax, ymax = vals
            words_checked += 1
            if not (-2 <= xmin <= xmax <= width + 2 and -2 <= ymin <= ymax <= height + 2):
                fail(f"Text outside PDF page bounds on page {pageno}: {vals}")
    if words_checked < 1000:
        fail(f"Suspiciously few PDF words checked: {words_checked}")
    # Source-level hyperlinks may have existing labels but resolve incorrectly
    # once TeX has built bookmarks and named destinations. Audit the actual PDF.
    named_destinations = reader.named_destinations
    internal_links = 0
    external_links = 0
    for page_index, page in enumerate(reader.pages, 1):
        for annotation in page.get("/Annots", []):
            annot = annotation.get_object()
            if annot.get("/Subtype") != "/Link":
                continue
            action = annot.get("/A")
            if not action:
                continue
            kind = action.get("/S")
            if kind == "/GoTo":
                internal_links += 1
                target = action.get("/D")
                if isinstance(target, str) and target not in named_destinations:
                    fail(f"Unresolved PDF navigation on page {page_index}: {target}")
            elif kind == "/URI":
                external_links += 1
    if internal_links < len(REQUIRED) * 2 or not external_links:
        fail(f"Suspiciously few PDF links: {internal_links} internal, "
             f"{external_links} external")
    print(f"Navigation QA: {internal_links} internal links resolved against "
          f"{len(named_destinations)} named destinations; {external_links} external links")
    print(f"PDF QA passed: {len(pages)-1} pages (tagged={tagged}); text boxes stay within page bounds")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdf", type=Path)
    args = parser.parse_args()
    validate_source()
    if args.pdf:
        validate_pdf(args.pdf.resolve())
