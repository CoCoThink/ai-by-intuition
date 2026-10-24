#!/usr/bin/env python3
"""Reject silently stale Roman/Chinese/Arabic part references before compiling."""
from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
BOOK = ROOT / "book"

# Exact section order is the reading contract, not a filename convention.
EXPECTED_PARTS = (
    ("learning", "学习是什么：从规则到参数更新"),
    ("matrices", "把许多数一起算"),
    ("tokens", "让文字进入计算"),
    ("context", "让词与词交换信息"),
    ("transformer", "组装并训练 Transformer"),
    ("vision", "换一种数据看 Transformer：从 CNN 到 ViT"),
    ("assistant", "从语言模型到助手"),
    ("architecture", "架构为什么在变，往哪走"),
    ("memory", "联想记忆与线性状态"),
)
PART_HEADING = re.compile(r"\\part\{([^}\n]+)\}\\label\{part:([^}\n]+)\}")
INPUT = re.compile(r"\\input\{chapters/([^}]+)\}")
NUMBER = r"(?:[IVX]+|[一二三四五六七八九十]+|\d+)"
# Includes "第 VI 部分", "第六部分", "第6部分" and "第一至第五部分".
HARDCODED = re.compile(
    r"第[ \t~]*" + NUMBER +
    r"(?:[ \t~]*(?:至|--|[-–—])[ \t~]*(?:第)?[ \t~]*" + NUMBER +
    r")?[ \t~]*部分"
)
PART_LINK = re.compile(r"\\hyperref\[part:([^]]+)\]")


def strip_comments(body: str) -> str:
    return re.sub(r"(?<!\\)%[^\n]*", "", body)


def lint(main: str, chapters: dict[str, str]) -> list[str]:
    errors: list[str] = []
    cleaned = strip_comments(main)
    observed = tuple((slug, title)
                     for title, slug in PART_HEADING.findall(cleaned))
    if observed != EXPECTED_PARTS:
        errors.append(
            "book/main.tex: part names, semantic anchors or order changed; "
            f"expected {EXPECTED_PARTS!r}, observed {observed!r}"
        )

    active = [m.group(1) for m in INPUT.finditer(cleaned)]
    allowed = {slug for slug, _ in EXPECTED_PARTS}
    texts = {"book/main.tex": cleaned}
    for name in active:
        if name not in chapters:
            errors.append(f"book/main.tex: missing chapters/{name}.tex")
        else:
            texts[f"chapters/{name}.tex"] = strip_comments(chapters[name])

    # Also reject stale prose in inline figure sources if they are included.
    for file in (BOOK / "figures").glob("*.tex"):
        texts[f"figures/{file.name}"] = strip_comments(
            file.read_text(encoding="utf-8")
        )

    for path, body in texts.items():
        for match in HARDCODED.finditer(body):
            line = body.count("\n", 0, match.start()) + 1
            errors.append(
                f"{path}:{line}: forbidden literal {match.group(0)!r}; "
                "use an actual part: anchor and topic name, or a semantic chapter/part link"
            )
        for match in PART_LINK.finditer(body):
            if match.group(1) not in allowed:
                errors.append(
                    f"{path}: invalid semantic part target part:{match.group(1)}"
                )

    # A valid link can still have the wrong semantic target: e.g. a link
    # labelled "associative memory" that silently jumps to CNN/ViT Part VI.
    for path, body in texts.items():
        if re.search(r"\\hyperref\[part:vision\]\{[^}]{0,100}联想记忆[^}]*\}", body):
            errors.append(
                f"{path}: associative-memory link incorrectly targets CNN/ViT Part VI"
            )

    # Memory is a teaching part before reference appendices, with a real part anchor.
    app = cleaned.find(r"\appendix")
    memory = cleaned.find(r"\input{chapters/04-key-value-outer-product}")
    memory_part = cleaned.find(r"\label{part:memory}")
    if memory >= 0 and not (0 <= memory_part < memory < app):
        errors.append("book/main.tex: associative memory must be inside Part IX before appendices")
    return errors


def self_test() -> None:
    parts = "".join(
        "\\part{" + title + "}\\label{part:" + slug + "}\\n"
        for slug, title in EXPECTED_PARTS
    )
    # Fixture matches the real appendix-position rule, too.
    base = parts + r"\appendix" + "\n" + r"\input{chapters/example}"
    assert lint(base, {"example": r"\hyperref[part:vision]{CNN 与 ViT}"}) == []
    for bad in (
        "第 VI 部分", "第VI部分", "第六部分", "第6部分",
        "第一至第五部分", "第 II--V 部分"
    ):
        issues = lint(base, {"example": "联想记忆推导见" + bad + "。"})
        assert any("forbidden literal" in e for e in issues), (bad, issues)
    incorrect = parts.replace("part:vision", "part:unknown")
    assert any("part names" in e for e in lint(
        incorrect + r"\appendix", {}
    ))
    assert any("invalid semantic part target" in e for e in lint(
        base, {"example": r"\hyperref[part:unknown]{记忆}"}
    ))
    misdirected = lint(base, {
        "example": r"\\hyperref[part:vision]{联想记忆}"
    })
    assert any("incorrectly targets" in issue for issue in misdirected)
    with_memory = parts + r"\input{chapters/04-key-value-outer-product}" + r"\appendix"
    assert lint(with_memory, {"04-key-value-outer-product": r"\section{Memory}"}) == []
    misordered = parts + r"\appendix\input{chapters/04-key-value-outer-product}"
    assert any("must be inside Part IX" in issue for issue in lint(
        misordered, {"04-key-value-outer-product": r"\section{Memory}"}))
    assert not HARDCODED.search(strip_comments("% 第 VI 部分\n普通文字"))
    print("Part reference regression QA passed: 6 invalid ordinals, "
          "wrong part order, wrong topic link and commented prose")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return 0
    main_text = (BOOK / "main.tex").read_text(encoding="utf-8")
    names = list(dict.fromkeys(INPUT.findall(strip_comments(main_text))))
    chapters = {}
    for name in names:
        path = BOOK / "chapters" / (name + ".tex")
        if not path.is_file():
            print(f"PART QA FAILED: missing {path}", file=sys.stderr)
            return 1
        chapters[name] = path.read_text(encoding="utf-8")
    issues = lint(main_text, chapters)
    if issues:
        for e in issues:
            print("::error::" + e, file=sys.stderr)
        print(f"PART QA FAILED: {len(issues)} issue(s)", file=sys.stderr)
        return 1
    print("Part reference QA passed: 9 anchored main parts, no "
          "hard-coded Roman/Chinese/Arabic part references")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
