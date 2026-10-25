#!/usr/bin/env python3
r"""Catch source defects that compile cleanly but print wrong text.

Each rule reproduces a defect found in a rendered PDF review:

* a TAB (or other control character) where an escaped ``\top`` was expected;
* a full-width punctuation mark placed after a display formula ``\]``, which
  prints as an orphaned line starting with "。";
* a command-line option such as ``--attention`` in roman text, which TeX
  ligatures into an en dash so readers cannot copy the command;
* a breakable tcolorbox inside a minipage: tcolorbox still splits it against
  the main page's remaining height, and the stacked fragments painted over a
  matrix in the row/column figure (the text layer kept it, so PDF text checks
  passed while readers saw only a bracket).
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
BOOK = ROOT / "book"
CONTROL = re.compile(r"[\x00-\x09\x0b-\x1f\x7f]")
ORPHAN_PUNCT = re.compile(r"\\\]\s*[。，；：、]")
OPTION = re.compile(r"(?<![-\w{}\\])--[A-Za-z]")
CODE_ENVS = ("verbatim", "lstlisting", "tikzpicture", "minted")
# Book boxes declared ``breakable`` in book/main.tex.
BREAKABLE_ENVS = ("idea", "example", "casebox", "boundarybox", "warningbox")
MINIPAGE = re.compile(r"\\begin\{minipage\}.*?\\end\{minipage\}", re.S)
BOX = re.compile(r"\\begin\{(tcolorbox|%s)\}(\[(?:[^\[\]]|\[[^\]]*\])*\])?" % "|".join(BREAKABLE_ENVS))


def uncomment(tex: str) -> str:
    return re.sub(r"(?<!\\)%[^\n]*", "", tex)


def strip_balanced(text: str, command: str) -> str:
    """Remove ``\\command{...}`` arguments, honouring nested braces."""
    out, i, token = [], 0, "\\" + command + "{"
    while True:
        j = text.find(token, i)
        if j < 0:
            out.append(text[i:])
            return "".join(out)
        out.append(text[i:j])
        depth, k = 1, j + len(token)
        while k < len(text) and depth:
            if text[k] == "\\":
                k += 2
                continue
            depth += {"{": 1, "}": -1}.get(text[k], 0)
            k += 1
        i = k


def roman_text(tex: str) -> str:
    """Approximate the text typeset in a proportional (ligaturing) font."""
    tex = uncomment(tex)
    for env in CODE_ENVS:
        tex = re.sub(r"\\begin\{%s\}.*?\\end\{%s\}" % (env, env), "", tex, flags=re.S)
    # A \ttfamily switch lasts to the end of its group or environment.
    tex = re.sub(r"\\ttfamily.*?(?=\\end\{|\}|\n\s*\n)", "", tex, flags=re.S)
    for command in ("texttt", "path", "url", "href", "lstinline", "detokenize"):
        tex = strip_balanced(tex, command)
    # TikZ path syntax "(a)--(b)" is not prose.
    tex = re.sub(r"\\draw[^;]*;", "", tex, flags=re.S)
    return tex


def lint(sources: dict[str, str]) -> list[str]:
    errors: list[str] = []
    for name, text in sources.items():
        for found in CONTROL.finditer(text):
            line = text.count("\n", 0, found.start()) + 1
            errors.append(f"{name}:{line}: control character U+{ord(found.group()):04X} "
                          "(an escaped command such as \\top may have been mangled)")
        for found in ORPHAN_PUNCT.finditer(uncomment(text)):
            line = text.count("\n", 0, found.start()) + 1
            errors.append(f"{name}:{line}: punctuation after display math prints on "
                          "its own line; move it inside the formula")
        if name.endswith(".tex"):
            for page in MINIPAGE.finditer(uncomment(text)):
                for box in BOX.finditer(page.group()):
                    options = box.group(2) or ""
                    breakable = ("breakable" in options and "breakable=false" not in options) or (
                        box.group(1) != "tcolorbox" and "breakable=false" not in options)
                    if breakable:
                        line = text.count("\n", 0, page.start()) + 1
                        errors.append(f"{name}:{line}: breakable {box.group(1)} inside a minipage "
                                      "can be split and painted over; use breakable=false")
            prose = roman_text(text)
            for found in OPTION.finditer(prose):
                snippet = prose[found.start():found.start() + 24].split("\n")[0]
                errors.append(f"{name}: command option '{snippet}' is typeset in a "
                              "ligaturing font; wrap it in \\texttt{} or \\path{}")
    return errors


def collect() -> dict[str, str]:
    sources = {str(p.relative_to(ROOT)): p.read_text()
               for p in sorted(BOOK.glob("**/*.tex")) if "build" not in p.parts}
    for row in json.loads((BOOK / "exercises.json").read_text()):
        for key in ("question", "solution", "review_prompt"):
            if row.get(key):
                sources[f"book/exercises.json[{row['id']}].{key}"] = row[key]
    return sources


def self_test() -> None:
    bad = {
        "a.tex": "$XX^\top$",
        "b.tex": "\\[x=1.\\]。\n",
        "c.tex": "0--20 步；--attention 看权重",
        "f.tex": "\\begin{minipage}{5cm}\\begin{tcolorbox}[enhanced,breakable]$A^\\top$\\end{tcolorbox}\\end{minipage}",
        "g.tex": "\\begin{minipage}{5cm}\\begin{idea}x\\end{idea}\\end{minipage}",
    }
    found = lint(bad)
    assert any("control character" in e for e in found), found
    assert any("display math" in e for e in found), found
    assert any("--attention" in e for e in found), found
    assert any(e.startswith("f.tex") and "minipage" in e for e in found), found
    assert any(e.startswith("g.tex") and "minipage" in e for e in found), found
    good = {
        "d.tex": "运行 \\texttt{teaching\\_trace.py --attention}；0--20 步。\n"
                 "\\begin{center}\\small\\ttfamily\npython3 x.py --json\n\\end{center}\n"
                 "\\draw (a)--(b);\n\\[x=1.\\]\n下一句。",
        "e.tex": "\\path{--real} 与 \\texttt{-{}-real}",
        "h.tex": "\\begin{minipage}{5cm}\\begin{tcolorbox}[enhanced,breakable=false]x\\end{tcolorbox}\\end{minipage}"
                 "\\begin{tcolorbox}[breakable]outside\\end{tcolorbox}",
    }
    assert lint(good) == [], lint(good)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        print("Source hygiene self-test passed: control characters, orphaned "
              "punctuation, ligatured command options and breakable boxes in "
              "minipages are rejected")
    errors = lint(collect())
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print("Source hygiene QA passed: no control characters, orphaned display "
          "punctuation, ligatured command options or breakable boxes in minipages")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
