#!/usr/bin/env python3
"""Validate the single-PDF textbook's structure before and after building.

This intentionally checks the final *rendered PDF text*, not just TeX syntax:
a successful LaTeX compilation does not guarantee a correct table of contents.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
PART_TITLES = [
    "把文字变成可计算的数字",
    "让神经网络学会预测",
    "让词与词交换信息",
    "组装、训练并使用 Transformer",
    "改进模型并构建可靠应用",
    "选读专题与知识回溯",
]
ORDINALS = "一二三四五六"


def fail(message: str) -> None:
    raise SystemExit("VALIDATION ERROR: " + message)


def validate_source() -> None:
    source = (ROOT / "book/main.tex").read_text(encoding="utf-8")
    parts = re.findall(r"\\part\{([^}]+)\}", source)
    if parts != PART_TITLES:
        fail(f"Expected exactly six correctly ordered parts, got {parts!r}")

    for ordinal in ORDINALS:
        if re.search(r"\\part\{第" + ordinal + r"部分", source):
            fail("Part titles must NOT include explicit '第X部分' prefixes; ctex adds these")

    if re.search(r"\\part\{从函数到矩阵：让知识变成计算\}", source):
        fail("Found legacy duplicate opening part")

    if r"\setcounter{tocdepth}{1}" not in source:
        fail("TOC must show parts and chapters, not an overwhelming subsection dump")

    inputs = re.findall(r"\\input\{([^}]+)\}", source)
    if len(inputs) != len(set(inputs)):
        fail("A chapter is included more than once")
    if len(inputs) < 20:
        fail("Unexpectedly few chapters in the complete book")
    for item in inputs:
        if not (ROOT / "book" / (item + ".tex")).is_file():
            fail(f"Missing chapter source: {item}.tex")

    for name in inputs:
        text = (ROOT / "book" / (name + ".tex")).read_text(encoding="utf-8")
        if re.search(r"\\section\{改进[一二三四五六][：:]", text):
            fail(f"Editor-process heading leaked into chapter: {name}")

    glossary = (ROOT / "book/chapters/24-lexicon.tex").read_text(encoding="utf-8")
    core = glossary.split(r"\subsection*{不要混淆的五对概念}")[0]
    entries = re.findall(r"\\item\s+\\textbf\{([^}]+)\}：", core)
    targets = re.findall(r"\\termref\{(intro:[^}]+)\}", core)
    if len(entries) != 100 or len(targets) != 100:
        fail(f"Expected 100 glossary concepts and 100 links, got {len(entries)} and {len(targets)}")
    if len(set(targets)) < 15:
        fail("Glossary links are suspiciously concentrated in too few chapters")
    for target in targets:
        chapter = target.removeprefix("intro:")
        path = ROOT / "book/chapters" / (chapter + ".tex")
        if not path.is_file():
            fail(f"Glossary destination is not a chapter: {target}")
        if (r"\label{" + target + "}") not in path.read_text(encoding="utf-8"):
            fail(f"Missing glossary destination label: {target}")
    if r"\newcommand{\termref}" not in source:
        fail("Glossary link macro is missing from book/main.tex")
    print(f"Glossary QA passed: 100 internal links, {len(set(targets))} chapter destinations")

    figures = {
        "book/chapters/03-matrix-multiplication.tex": (
            r"\input{figures/row-column-intuition}",
            r"\label{sec:layout-matrix-card}",
        ),
        "book/chapters/12-self-attention-matrices.tex": (
            r"\input{figures/key-value-layout}",
            r"\label{sec:key-layout-card}",
        ),
    }
    for chapter, (input_directive, label) in figures.items():
        text = (ROOT / chapter).read_text(encoding="utf-8")
        if input_directive not in text or label not in text:
            fail(f"Missing matrix-layout figure or anchor in {chapter}")
    for figure in ["row-column-intuition", "key-value-layout"]:
        fig = ROOT / "book/figures" / (figure + ".tex")
        if not fig.is_file() or r"\begin{tikzpicture}" not in fig.read_text(encoding="utf-8"):
            fail(f"Missing editable matrix diagram: {fig}")
    print("Matrix layout QA passed: introductory and QKV diagrams present")

    expected_new = {
        "20b-task-contract", "10b-ffn-output-head", "22c-language-training",
        "22d-modern-transformers", "23c-post-training", "23d-agent-systems",
        "24b-modern-lexicon", "25b-modern-practice",
    }
    chapter_names = {item.removeprefix("chapters/") for item in inputs}
    if not expected_new.issubset(chapter_names):
        fail("Advanced language model learning path is incomplete")
    for filename in ("20b-task-contract", "22c-language-training"):
        text = (ROOT / "book/chapters" / (filename + ".tex")).read_text(encoding="utf-8")
        if "7,3,9" in text or "7,\\ 3,\\ 9" in text:
            fail("Example token ID exceeds the five-token teaching vocabulary")
    source_refs = (ROOT / "book/chapters/26-sources.tex").read_text(encoding="utf-8")
    for video_id in ("BV1NCgVzoEG9", "BV15z4C6SEHT"):
        if video_id not in source_refs:
            fail("Original reference video is missing: " + video_id)
    modern = (ROOT / "book/chapters/24b-modern-lexicon.tex").read_text(encoding="utf-8")
    term_links = re.findall(r"\\termref\{(intro:[^}]+)\}", modern)
    if len(term_links) < 20:
        fail("Modern terminology index should have at least 20 linked concepts")
    for target in term_links:
        target_file = ROOT / "book/chapters" / (target.removeprefix("intro:") + ".tex")
        if not target_file.is_file() or (r"\label{" + target + "}") not in target_file.read_text(encoding="utf-8"):
            fail("Modern glossary destination is missing: " + target)
    print(f"Advanced curriculum QA passed: 8 new chapters and {len(term_links)} internal index links")

    # Enforce pedagogical dependency order, not merely that the book compiles.
    expected_groups = [
        ["00-guide", "00-functions", "01-vectors", "02-dot-product",
         "03-matrix-multiplication", "20-embeddings", "20b-task-contract"],
        ["07-functions-relu", "10-mlp", "16-loss-gradient",
         "17-backpropagation", "18b-end-to-end-learning", "18-generalization"],
        ["21-rnn", "21b-why-attention", "11-softmax-memory",
         "12-self-attention-matrices"],
        ["22-transformer-architecture", "10b-ffn-output-head",
         "22b-token-to-output", "22c-language-training", "23-llm-systems"],
        ["22d-modern-transformers", "23c-post-training",
         "23d-agent-systems", "23b-deployment-and-ecosystem"],
        ["19-cnn", "04-key-value-outer-product", "05-memory-interference",
         "06-better-linear-memory", "08-stacking-key-value",
         "09-nonlinearity-and-memory", "14-summary", "15-practice",
         "13-capacity", "24-lexicon", "24b-modern-lexicon",
         "25-integrated-practice", "25b-modern-practice", "26-sources"],
    ]
    expected = [f"chapters/{name}" for group in expected_groups for name in group]
    if inputs != expected:
        fail("Chapter reading order breaks the representation-to-generation learning path")
    if len(expected) != 40:
        fail("Expected 40 unique chapter source files")
    # Optional memory/CNN chapters must not interrupt the RNN-to-Attention path.
    for core in ("21-rnn", "21b-why-attention", "11-softmax-memory",
                 "12-self-attention-matrices", "22-transformer-architecture"):
        if expected.index(f"chapters/{core}") >= expected.index("chapters/04-key-value-outer-product"):
            fail("Optional memory chapter interrupts the core Transformer derivation")
    guide = (ROOT / "book/chapters/00-guide.tex").read_text(encoding="utf-8")
    task = (ROOT / "book/chapters/20b-task-contract.tex").read_text(encoding="utf-8")
    training = (ROOT / "book/chapters/22c-language-training.tex").read_text(encoding="utf-8")
    for document in (guide, task, training):
        if "(1,3,4,2)" not in document and "[1,3,4,2]" not in document:
            fail("Running Token ID example is inconsistent across teaching stages")
    # Pedagogical framing: the book must explain why we train the model,
    # before treating next-token prediction as a concrete exercise.
    if not (guide.find("为什么 AI 能接住我们说的话") >= 0 and
            guide.find("为什么 AI 能接住我们说的话") < guide.find("为什么偏偏练习") and
            "这是一种可训练的设计选择，而不是 AI 的终极目标" in guide and
            "文字充当自己的练习题和答案" in guide):
        fail("Book opening must motivate the language-learning task before next-token exercises")
    cover = (ROOT / "book/main.tex").read_text(encoding="utf-8")
    if "下一 Token 预测" not in cover or "训练一类语言模型" not in cover:
        fail("Cover no longer distinguishes user motivation from the training objective")
    matrix = (ROOT / "book/chapters/01-vectors.tex").read_text(encoding="utf-8")
    if "x=2.6cm,y=2.6cm" not in matrix or "(0,0)--(1,0)" not in matrix:
        fail("Vector diagram arrow coordinates do not match its stated unit vectors")
    if "图解：同一批向量" not in (ROOT / "book/figures/row-column-intuition.tex").read_text(encoding="utf-8"):
        fail("Original row/column intuition graphic is missing")
    print("Pedagogy QA passed: reader motivation, next-token rationale and correct vector illustration")

    print("Learning-path QA passed: five linear learning parts, optional extensions last")

    # The two crucial first-time lessons must begin with an intuitive example.
    rnn = (ROOT / "book/chapters/21-rnn.tex").read_text(encoding="utf-8")
    attn = (ROOT / "book/chapters/21b-why-attention.tex").read_text(encoding="utf-8")
    matrix_bridge = (ROOT / "book/chapters/11-softmax-memory.tex").read_text(encoding="utf-8")
    if not (rnn.find("RNN（循环神经网络）") >= 0 and
            rnn.find("RNN（循环神经网络）") < rnn.find(r"\boxed{\vect h_t") and
            "h_t=x_t+0.5h_{t-1}" in rnn and
            rnn.find("h_1=1+0.5") < rnn.find(r"\boxed{\vect h_t")):
        fail("RNN chapter must explain state and compute three steps before general matrix notation")
    for phrase in ("Query（查询", "Key（索引", "Value（内容", "(2,0,1)", "0.665", "0.910", "0.335"):
        if phrase not in attn:
            fail("Attention beginner walkthrough is missing: " + phrase)
    if not ("从单次查询到批量计算" in matrix_bridge and
            "0.910" in matrix_bridge and
            "矩阵转置" in matrix_bridge):
        fail("The following chapter no longer builds on the same Attention example")
    print("Teaching-sequence QA passed: RNN intuition and Attention hand calculation")

    # Inline concept back-links must land on a precise, previously taught explanation.
    anchors: dict[str, int] = {}
    usages: list[tuple[int, str, str]] = []
    for index, chapter in enumerate(inputs):
        body = (ROOT / "book" / (chapter + ".tex")).read_text(encoding="utf-8")
        for target in re.findall(r"\\label\{concept:([a-z0-9-]+)\}", body):
            if target in anchors:
                fail("Duplicate concept explanation anchor: " + target)
            anchors[target] = index
        for target in re.findall(r"\\conceptlink\{([a-z0-9-]+)\}", body):
            usages.append((index, target, chapter))
    if len(anchors) < 25 or len(usages) < 35:
        fail(f"Too few concept cross-references: {len(anchors)} anchors, {len(usages)} links")
    for index, target, chapter in usages:
        if target not in anchors:
            fail(f"Broken concept hyperlink {target} in {chapter}")
        if anchors[target] >= index:
            fail(f"Concept hyperlink is not backward-looking: {target} in {chapter}")
    if r"\newcommand{\conceptlink}" not in source:
        fail("Concept hyperlink macro missing in book/main.tex")
    print(f"Concept navigation QA passed: {len(usages)} in-text links to {len(anchors)} precise explanations")

    print(f"Source QA passed: {len(parts)} parts, {len(inputs)} unique chapter files")


def validate_pdf(pdf_path: Path) -> None:
    if not pdf_path.is_file() or pdf_path.stat().st_size < 50_000:
        fail(f"PDF missing or suspiciously small: {pdf_path}")

    proc = subprocess.run(
        ["pdftotext", "-f", "2", "-l", "4", "-layout", str(pdf_path), "-"],
        capture_output=True,
        text=True,
        check=True,
    )
    toc = proc.stdout
    # PDF extraction can insert or omit spaces around mixed Chinese/Latin titles.
    # Compare whitespace-normalized labels, not typesetting line breaks.
    toc_compact = re.sub(r"\s+", "", toc)
    for ordinal, title in zip(ORDINALS, PART_TITLES):
        expected = "第" + ordinal + "部分" + re.sub(r"\s+", "", title)
        if expected not in toc_compact:
            fail(f"Rendered TOC is missing or mislabels part: 第{ordinal}部分 {title}")

    if "第七部分" in toc:
        fail("Rendered TOC incorrectly contains a seventh part")
    if re.search(r"第[一二三四五六]部分[：:]", toc):
        fail("Rendered TOC contains a duplicated part prefix inside the title")

    text_proc = subprocess.run(
        ["pdftotext", str(pdf_path), "-"],
        capture_output=True, text=True, check=True,
    )
    book_text = re.sub(r"\s+", "", text_proc.stdout)
    for phrase in ["同一批向量", "为什么一会儿写"]:
        if re.sub(r"\s+", "", phrase) not in book_text:
            fail(f"Rendered PDF is missing a matrix-layout diagram title: {phrase}")
    pages_text = text_proc.stdout.split("\f")
    normalized_pages = [re.sub(r"\s+", "", page) for page in pages_text]
    for title, contents in [
        ("图解：同一批向量", ["每行一条向量", "每列一条向量"]),
        ("图解：为什么一会儿写", ["每行一条Key", "每列一条Key", "Value同理"]),
    ]:
        if not any(title in page and all(piece in page for piece in contents)
                   for page in normalized_pages):
            fail(f"Matrix figure was split across pages: {title}")
    print("Matrix layout pagination QA passed: both complete cards stay on a page")

    for topic in ("把语言练习变成一道可计算的预测题", "前馈网络与输出头", "现代Transformer",
                  "RLVR", "MoE", "Agent", "标签"):
        if re.sub(r"\s+", "", topic) not in book_text:
            fail("Rendered PDF does not include advanced curriculum topic: " + topic)
    # Page-break regression: a trailing sentence must not occupy its own page.
    for page_no, page in enumerate(pages_text, start=1):
        if page_no <= 3 or not page.strip():
            continue
        body = re.sub(r"AI\s+by\s+Intuition\s*[·・]\s*完整教材", "", page)
        body = re.sub(r"从函数到\s*Transformer", "", body)
        body = re.sub(r"(?m)^\s*\d+\s*$", "", body)
        hanzi = re.findall(r"[\u4e00-\u9fff]", body)
        if len(hanzi) < 22:
            fail(f"Nearly blank body page (possible orphan): {page_no}, {len(hanzi)} Chinese characters")
    print("Page-density QA passed: no nearly blank body pages")

    print("Advanced curriculum PDF QA passed: new topics are present")

    print("Matrix layout PDF QA passed: both diagram headings extracted")

    print(f"PDF QA passed: {pdf_path.name}; six uniquely numbered parts in rendered TOC")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdf", type=Path, help="Additionally validate the rendered PDF")
    args = parser.parse_args()
    validate_source()
    if args.pdf is not None:
        validate_pdf(args.pdf.resolve())
