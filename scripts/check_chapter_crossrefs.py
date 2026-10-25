#!/usr/bin/env python3
r"""Prevent stale chapter numbers even when LaTeX cross-references still compile.

The ordinary LaTeX and PDF checks catch missing destinations and '??'. This
additional gate checks the SEMANTICS of manual chapter numbers against the
real \section order of the active book/main.tex input graph.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
BOOK = ROOT / "book"
INPUT_OR_APPENDIX = re.compile(r"\\appendix\b|\\input\{chapters/([^}]+)\}")
SECTION_OR_CHECK = re.compile(r"\\section\s*\{|\\chapterchecktasks\{([^}]+)\}")
# Also catch Chinese numerals ("第三章"), lists and ranges ("第 23、24 章",
# "第 1–10 章") and dotted section numbers ("第 24.10 节").
NUMERIC_CHAPTER = re.compile(
    r"第[ \t~]*([0-9]{1,2}|[一二三四五六七八九十]{1,3})"
    r"(?:[ \t~]*(?:--|[、，,–—-])[ \t~]*[0-9]{1,2})*[ \t~]*章"
    r"|第[ \t~]*([0-9]{1,2}\.[0-9]{1,2})[ \t~]*节")
ANSWER_CHAPTER = re.compile(
    r"\\item\s*\[\s*\\textbf\{第\s*(\d+)\s*章\}\s*\]"
    r"\s*\\phantomsection\s*\\label\{answer:([^}]+)\}"
)


def uncomment(tex: str) -> str:
    """Remove TeX comments without touching escaped percent signs."""
    return re.sub(r"(?<!\\)%[^\n]*", "", tex)


def check_crossrefs(main: str, chapters: dict[str, str]) -> list[str]:
    errors: list[str] = []
    main = uncomment(main)
    chapter_no = 0
    in_appendix = False
    core_checks: dict[str, int] = {}
    active: list[str] = []

    # Read chapter files in actual compilation order, not alphabetical filename order.
    # A single source may contain two numbered chapters, while one chapter can span
    # several files; count \section commands, not file names.
    for event in INPUT_OR_APPENDIX.finditer(main):
        if event.group(0) == r"\appendix":
            in_appendix = True
            continue
        name = event.group(1)
        if name not in chapters:
            errors.append(f"book/main.tex: missing input chapters/{name}.tex")
            continue
        active.append(name)
        if in_appendix:
            continue
        for token in SECTION_OR_CHECK.finditer(uncomment(chapters[name])):
            slug = token.group(1)
            if slug is None:
                chapter_no += 1
            elif chapter_no and slug not in core_checks:
                core_checks[slug] = chapter_no
            elif slug in core_checks:
                errors.append(f"chapters/{name}.tex: duplicate self-check ID {slug}")

    if chapter_no != 41:
        errors.append(f"core numbered chapters: expected 41, found {chapter_no}")

    # Unlinked literal numbers survive LaTeX compilation and can silently go
    # stale after a section is inserted, moved, or removed. The answer bank is
    # handled separately below because it intentionally prints chapter titles.
    for name in active:
        if name == "28-chapter-checks":
            continue
        body = uncomment(chapters[name])
        for found in NUMERIC_CHAPTER.finditer(body):
            line = body.count("\n", 0, found.start()) + 1
            errors.append(
                f"chapters/{name}.tex:{line}: hard-coded '{found.group(0)}'; "
                "use 第~\\ref*{intro:target}~章 instead"
            )

    if "28-chapter-checks" not in chapters:
        errors.append("missing appendix D chapter-answer source")
        return errors
    answers = uncomment(chapters["28-chapter-checks"])
    observed: dict[str, int] = {}
    for item in ANSWER_CHAPTER.finditer(answers):
        number, slug = int(item.group(1)), item.group(2)
        line = answers.count("\n", 0, item.start()) + 1
        if slug in observed:
            errors.append(f"28-chapter-checks.tex:{line}: duplicate answer ID {slug}")
        observed[slug] = number
        expected = core_checks.get(slug)
        if expected is None:
            errors.append(
                f"28-chapter-checks.tex:{line}: no numbered core self-check for {slug}"
            )
        elif number != expected:
            errors.append(
                f"28-chapter-checks.tex:{line}: answer {slug} says chapter {number}; "
                f"actual chapter is {expected} in book/main.tex order"
            )

    for slug in sorted(set(core_checks) - set(observed)):
        errors.append(f"28-chapter-checks.tex: missing numbered answer entry {slug}")
    if len(observed) != len(core_checks):
        errors.append(
            f"appendix D: expected {len(core_checks)} numbered answer headings, "
            f"found {len(observed)}"
        )
    return errors


def self_test() -> None:
    main = (r"\input{chapters/a}" "\n"
            r"\input{chapters/b}" "\n"
            r"\appendix" "\n"
            r"\input{chapters/28-chapter-checks}" "\n")
    a = r"\section{One}\label{intro:a}\chapterchecktasks{one}{A}{\item x}"
    b = r"\section{Two}\label{intro:b}\chapterchecktasks{two}{B}{\item y}"
    answers = (
        r"\item[\textbf{第 1 章}] \phantomsection\label{answer:one}" "\n"
        r"\item[\textbf{第 2 章}] \phantomsection\label{answer:two}" "\n"
    )
    inputs = {"a": a, "b": b, "28-chapter-checks": answers}
    # In this two-chapter fixture only the fixed-book cardinality warning is expected.
    assert check_crossrefs(main, inputs) == [
        "core numbered chapters: expected 41, found 2"
    ]
    wrong = dict(inputs, **{"28-chapter-checks": answers.replace(
        "第 2 章", "第 1 章"
    )})
    assert any("actual chapter is 2" in e for e in check_crossrefs(main, wrong))
    stale = dict(inputs, b=b + "\n更多信息见第 2 章。")
    assert any("hard-coded" in e for e in check_crossrefs(main, stale))
    for literal in ("见第三章。", "见第 23、24 章。", "见第 1–10 章。", "见第 17--19 章。", "见第 24.10 节。"):
        stale = dict(inputs, b=b + "\n" + literal)
        assert any("hard-coded" in e for e in check_crossrefs(main, stale)), literal
    linked = dict(inputs, b=b + r"见第~\ref*{intro:a}~章与第一部分。")
    assert check_crossrefs(main, linked) == check_crossrefs(main, inputs)
    missing = dict(inputs, **{"28-chapter-checks": answers.splitlines()[0]})
    assert any("missing numbered answer entry two" in e
               for e in check_crossrefs(main, missing))
    assert uncomment(r"A \% escaped" "\n" r"% 第 5 章 commented") == (
        r"A \% escaped" "\n"
    )
    print("Chapter cross-reference gate self-test passed (stale number, Chinese numeral, list/range, dotted section, wrong answer, missing answer)")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return 0
    source = (BOOK / "main.tex").read_text(encoding="utf-8")
    names = list(dict.fromkeys(
        match.group(1) for match in INPUT_OR_APPENDIX.finditer(uncomment(source))
        if match.group(1)
    ))
    chapters = {}
    for name in names:
        file = BOOK / "chapters" / f"{name}.tex"
        if not file.is_file():
            print(f"REFERENCE QA FAILED: missing {file}", file=sys.stderr)
            return 1
        chapters[name] = file.read_text(encoding="utf-8")
    issues = check_crossrefs(source, chapters)
    if issues:
        print(f"CHAPTER REFERENCE QA FAILED: {len(issues)} problem(s)", file=sys.stderr)
        for issue in issues:
            print("::error::" + issue, file=sys.stderr)
        return 1
    print("Chapter reference QA passed: 41 numbered chapters; "
          "all appendix D answer chapter numbers match source order; "
          "no hard-coded numbered chapter mentions")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
