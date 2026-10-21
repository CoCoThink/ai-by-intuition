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

ROOT = Path(__file__).resolve().parents[1]
BOOK = ROOT / "book"
PARTS = [
    "把文字变成可计算的数字",
    "让神经网络学会预测",
    "让词与词交换信息",
    "组装、训练并使用 Transformer",
    "改进模型并构建可靠应用",
    "选读：图像与联想记忆",
]
REQUIRED = [
    "00-guide", "00b-math-tools", "00-functions", "01-vectors", "02-dot-product",
    "03-matrix-multiplication", "20-embeddings", "20b-task-contract",
    "07-functions-relu", "10-mlp", "16-loss-gradient", "17-backpropagation",
    "18b-end-to-end-learning", "18-generalization",
    "21-rnn", "21b-why-attention", "11-softmax-memory", "12-self-attention-matrices",
    "22a-position-multihead", "22-transformer-architecture",
    "10b-ffn-output-head", "22b-token-to-output", "22c-language-training",
    "23-llm-systems", "22d-modern-transformers", "23c-post-training",
    "23d-agent-systems", "23b-deployment-and-ecosystem",
    "19-cnn", "04-key-value-outer-product", "05-memory-interference",
    "06-better-linear-memory", "08-stacking-key-value",
    "09-nonlinearity-and-memory", "14-summary", "13-capacity",
    "25-integrated-practice", "25b-modern-practice", "15-practice",
    "24-lexicon", "24b-modern-lexicon", "27-answer-key", "26-sources",
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
    # End-to-end two-token model: last hidden row and designed vocabulary head.
    h = [0.495, 2.505]
    z = [0., h[0], 0., 0., h[1]]
    exps = [math.exp(v) for v in z]
    p = [v / sum(exps) for v in exps]
    assert abs(p[4] - 0.725155) < 0.0001
    grad_z = [p[i] - int(i == 4) for i in range(5)]
    # W_vocab has columns [0, h0, 0, 0, h1] before update.
    step = 0.1
    norm_sq = sum(x*x for x in h)
    z_new = [z[i] - step * norm_sq * grad_z[i] for i in range(5)]
    new_e = [math.exp(v) for v in z_new]
    p_new = [v / sum(new_e) for v in new_e]
    assert abs(p_new[4] - 0.767932) < 0.0001
    assert -math.log(p_new[4]) < -math.log(p[4])
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
    # Answer key exercise: (6,0) · (5,12) = 30, cos = 5/13.
    assert math.isclose(6 * 13 * (5 / 13), 30)
    print("Numerical QA passed: SGD improves correct probability; LoRA and KV math checked")


def validate_source() -> None:
    main = (BOOK / "main.tex").read_text(encoding="utf-8")
    parts = re.findall(r"\\part\{([^}]+)\}", main)
    if parts != PARTS:
        fail(f"Expected six reading parts; found {parts!r}")
    inputs = re.findall(r"\\input\{chapters/([^}]+)\}", main)
    if inputs != REQUIRED or len(inputs) != len(set(inputs)):
        fail(f"Reading order/appendix differs from the reviewed 43-file curriculum: {inputs!r}")
    sources = {name: chapter(name) for name in REQUIRED}
    includes(main, r"\appendix", "main")
    includes(main, r"\part*{附录：练习、术语与答案}", "main")
    includes(main, r"\ctexset{section={name={,},number=\arabic{section}}}", "main")
    if main.find(r"\appendix") <= main.find(r"\part{选读：图像与联想记忆}"):
        fail("Appendices must follow optional part VI")
    if main.count(r"\learningbridge{") != 6:
        fail("Six sections need six minimal part introductions")

    # Explicit vector and architecture consistency.
    for name in ("21b-why-attention", "12-self-attention-matrices"):
        includes(sources[name], r"\vect x_i^\top W_Q" if name.startswith("21b") else r"\vect x^\top W_Q", name)
    includes(sources["12-self-attention-matrices"], r"W_Q^\top\vect x", "row/column explanation")
    includes(sources["22-transformer-architecture"], r"\vect h_T^\top W_{\rm vocab}", "row vocabulary projection")
    includes(sources["22-transformer-architecture"], r"\input{figures/pre-norm-block}", "true Pre-Norm figure")
    includes(sources["22-transformer-architecture"], r"X_{\rm block}", "distinct Block output")
    includes(sources["22a-position-multihead"], "0.990", "two-head worked example")
    includes(sources["22a-position-multihead"], "0.9997", "scaled-dot-product example")
    includes(sources["22a-position-multihead"], "位置", "positional example")
    includes(sources["22a-position-multihead"], r"\vect x_{\text{春天}}^\top=(1,0)", "position example uses embedding table")
    includes(sources["22a-position-multihead"], r"\vect x_{\text{花}}^\top=(0,1)", "position example uses embedding table")
    includes(sources["21b-why-attention"], "没有指定生成它们的投影矩阵", "independent Q/K example")
    includes(sources["22c-language-training"], r"\label{sec:transformer-gradient-step}", "gradient step")
    includes(sources["22c-language-training"], "0.768", "measured SGD improvement")
    includes(sources["23b-deployment-and-ecosystem"], "16{,}000", "LoRA computation")
    includes(sources["23b-deployment-and-ecosystem"], "软标签", "distillation computation")
    includes(sources["23b-deployment-and-ecosystem"], "-127", "quantization computation")
    includes(sources["00b-math-tools"], r"\log", "math prerequisites")
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
        ("causal-mask-heatmap", "22-transformer-architecture"),
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
    answer_key = sources["27-answer-key"]
    includes(answer_key, r"\label{app:answers}", "answer key")
    if answer_key.count(r"\subsection*{") != 3:
        fail("Answer appendix should separate the three exercise sets")
    includes(sources["24-lexicon"], r"\textbf{Top-p}", "100-word index")
    ninth = sources["24-lexicon"].split(r"\subsection{第九组")[1].split(r"\subsection{第十组")[0]
    includes(ninth, r"\textbf{Top-p}", "sampling group")

    # Glossary anchors remain valid and are backed by content in the book.
    labels: set[str] = set()
    for name in REQUIRED:
        labels.update(re.findall(r"\\label\{([^}]+)\}", sources[name]))
    for lex in ("24-lexicon", "24b-modern-lexicon"):
        refs = re.findall(r"\\termref\{([^}]+)\}", sources[lex])
        if len(refs) != (100 if lex == "24-lexicon" else 27):
            fail(f"Unexpected glossary link count in {lex}: {len(refs)}")
        for ref in refs:
            if ref not in labels:
                fail(f"Broken glossary destination: {ref}")
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

    # The prominent diagram and teaching resources are all editable TikZ.
    for figure in ("row-column-intuition", "key-value-layout", "pre-norm-block",
                   "rnn-unrolled-flow", "attention-why-qkv"):
        file = BOOK / "figures" / f"{figure}.tex"
        if not file.is_file() or r"\begin{tikzpicture}" not in file.read_text(encoding="utf-8"):
            fail(f"Missing editable figure {figure}")
    for editorial in ("这正是文章把", "这些只是文章讨论", "没有沿用字幕中",
                      "章节号会随全书编排自动更新", "根据初中学过的",
                      "两单位向量的点积", "是本文为了学习",
                      "在本卷，输入 Query", "全书用\\textbf{本书}统一指代"):
        for name, body in sources.items():
            if editorial in body:
                fail(f"Editorial residue {editorial!r} in {name}")
    if r"\sim" in sources["13-capacity"]:
        fail("Do not use strict asymptotic equivalence as loose statistical magnitude")
    print(f"Source QA passed: {len(PARTS)} parts, {len(REQUIRED)} files, three separated solutions, linked glossary")
    test_numeric_examples()


def validate_pdf(path: Path) -> None:
    if not path.exists() or path.stat().st_size < 70_000:
        fail(f"Final PDF missing or suspiciously small: {path}")
    text = subprocess.run(["pdftotext", str(path), "-"], capture_output=True,
                          text=True, check=True).stdout
    pages = text.split("\f")
    compact = normalized(text)
    toc = normalized("".join(pages[1:6]))
    for num, title in zip("一二三四五六", PARTS):
        if normalized("第" + num + "部分" + title) not in toc:
            fail(f"Rendered TOC missing part 第{num}部分: {title}")
    if "第七部分" in toc:
        fail("Rendered table of contents has an extra part")
    for item in ("数学速查", "位置编码与多头注意力", "Pre-Norm",
                 "LayerNorm", "0.768", "LoRA", "16,000",
                 "附录", "集中参考答案", "Key", "Value"):
        if normalized(item) not in compact:
            fail(f"Rendered PDF does not contain required material: {item}")
    for i, page in enumerate(pages, 1):
        if i < 4 or not page.strip():
            continue
        body = re.sub(r"AI\s+by\s+Intuition.*?完整教材", "", page)
        body = re.sub(r"从函数到\s*Transformer", "", body)
        body = re.sub(r"(?m)^\s*\d+\s*$", "", body)
        if len(re.findall(r"[\u4e00-\u9fff]", body)) < 18:
            fail(f"Likely orphan/blank page: {i}")
    print(f"PDF QA passed: {len(pages)-1} pages; sections, numbers and appendix present")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdf", type=Path)
    args = parser.parse_args()
    validate_source()
    if args.pdf:
        validate_pdf(args.pdf.resolve())
