#!/usr/bin/env python3
"""Reject unresolved cross-references in the FINAL latexmk log and built PDF."""
from __future__ import annotations

import argparse
from pathlib import Path
import re
import subprocess
import sys

# An unresolved reference is a LaTeX warning, not a -halt-on-error failure.
# Check only the final main.log after latexmk's automatic reruns.
LOG_FAILURES = (
    ("undefined reference", re.compile(
        r"LaTeX Warning: Reference\b(?:[^\n]|\n(?!LaTeX Warning:)){0,260}?\bundefined\b", re.I)),
    ("undefined citation", re.compile(
        r"LaTeX Warning: Citation\b(?:[^\n]|\n(?!LaTeX Warning:)){0,260}?\bundefined\b", re.I)),
    ("undefined references summary", re.compile(
        r"LaTeX Warning: There were undefined references", re.I)),
    ("undefined citations summary", re.compile(
        r"LaTeX Warning: There were undefined citations", re.I)),
    ("duplicate labels", re.compile(
        r"LaTeX Warning: (?:There were multiply-defined labels|Label[^\n]{0,160}multiply defined)", re.I)),
    ("rerun required", re.compile(
        r"LaTeX Warning: Label\(s\) may have changed", re.I)),
    ("auxiliary rerun required", re.compile(
        r"Package rerunfilecheck Warning: File\b[^\n]*\bhas changed", re.I)),
)

# The book has no intentional double question marks. Catch spaces/newlines
# inserted by pdftotext, including 〔第 ?? 章〕 and 〔第 ? ? 章〕.
UNRESOLVED_PDF = re.compile(r"\?[\t \r\n\u00a0]{0,6}\?")


def log_errors(log_text: str) -> list[str]:
    problems = []
    for label, pattern in LOG_FAILURES:
        for match in pattern.finditer(log_text):
            line = log_text.count("\n", 0, match.start()) + 1
            excerpt = " ".join(match.group(0).split())[:160]
            problems.append(f"main.log:{line}: {label}: {excerpt}")
    return problems


def pdf_errors(pages: list[str]) -> list[str]:
    problems = []
    for page_no, page in enumerate(pages, 1):
        for match in UNRESOLVED_PDF.finditer(page):
            excerpt = " ".join(page[max(0, match.start() - 35):
                                    match.end() + 35].split())[:150]
            problems.append(f"PDF page {page_no}: unresolved '??': {excerpt}")
            if len(problems) >= 30:
                problems.append("Additional unresolved PDF placeholders omitted")
                return problems
    return problems


def self_test() -> None:
    assert not log_errors("Output written on main.pdf.\n")
    bad_logs = (
        "LaTeX Warning: Reference missing on page 132 undefined on input line 10.",
        "LaTeX Warning: Reference a-very-long-label on page 132\n"
        " undefined on input line 10.",
        "LaTeX Warning: Citation missing on page 30 undefined on input line 10.",
        "LaTeX Warning: There were undefined references.",
        "LaTeX Warning: Label(s) may have changed. Rerun.",
        "LaTeX Warning: There were multiply-defined labels.",
        "Package rerunfilecheck Warning: File main.out has changed.",
    )
    for example in bad_logs:
        assert log_errors(example), example
    assert not pdf_errors(["第 18 章", "一个问号？是正常的。"])
    assert len(pdf_errors(["前言", "〔第 ?? 章〕 B3-4", "第 ? ? 章"])) == 2
    print("LaTeX reference gate self-test passed")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--log", type=Path, help="Final build/main.log")
    parser.add_argument("--pdf", type=Path, help="Final PDF; uses pdftotext -layout")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        self_test()
    if not args.log and not args.pdf:
        if args.self_test:
            return 0
        parser.error("provide both --log and --pdf or --self-test")
    if not args.log or not args.pdf:
        parser.error("production validation requires both --log and --pdf")
    if not args.log.is_file() or not args.pdf.is_file():
        parser.error("final LaTeX log and PDF must both exist")

    problems = log_errors(args.log.read_text(encoding="utf-8", errors="replace"))
    extracted = subprocess.run(
        ["pdftotext", "-layout", "-enc", "UTF-8", str(args.pdf), "-"],
        check=True, capture_output=True, text=True,
    ).stdout
    pages = extracted.split("\f")
    if pages and not pages[-1].strip():
        pages.pop()
    if len(pages) < 50:
        raise SystemExit(f"Reference gate: suspicious PDF page count {len(pages)}")
    problems.extend(pdf_errors(pages))
    if problems:
        print(f"REFERENCE QA FAILED: {len(problems)} problems", file=sys.stderr)
        for problem in problems:
            print("::error::" + problem, file=sys.stderr)
        return 1
    print(f"Reference QA passed: no LaTeX unresolved/rerun warnings; "
          f"no '??' in {len(pages)} PDF pages")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
