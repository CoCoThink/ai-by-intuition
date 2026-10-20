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
    for ordinal, title in zip(ORDINALS, PART_TITLES):
        pattern = re.escape("第" + ordinal + "部分") + r"\s+" + re.escape(title)
        if not re.search(pattern, toc):
            fail(f"Rendered TOC is missing or mislabels part: 第{ordinal}部分 {title}")

    if "第七部分" in toc:
        fail("Rendered TOC incorrectly contains a seventh part")
    if re.search(r"第[一二三四五六]部分[：:]", toc):
        fail("Rendered TOC contains a duplicated part prefix inside the title")

    print(f"PDF QA passed: {pdf_path.name}; six uniquely numbered parts in rendered TOC")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdf", type=Path, help="Additionally validate the rendered PDF")
    args = parser.parse_args()
    validate_source()
    if args.pdf is not None:
        validate_pdf(args.pdf.resolve())
