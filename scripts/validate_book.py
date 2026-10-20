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
    "从问题到数字",
    "一个网络怎样学会预测",
    "让模型利用图片和语言的结构",
    "重新理解 Attention 与 Transformer",
    "模型怎样生成和使用信息",
    "进阶思考与学习工具",
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

    print("Matrix layout PDF QA passed: both diagram headings extracted")

    print(f"PDF QA passed: {pdf_path.name}; six uniquely numbered parts in rendered TOC")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdf", type=Path, help="Additionally validate the rendered PDF")
    args = parser.parse_args()
    validate_source()
    if args.pdf is not None:
        validate_pdf(args.pdf.resolve())
