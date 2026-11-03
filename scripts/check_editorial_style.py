#!/usr/bin/env python3
r"""Limit defensive disclaimers to three passages across the published book.

Follow literal \input/\include paths from main.tex, including figures and
generated appendices. Count included TeX rather than counting both an exercise's
JSON source and its generated TeX. These phrase families detect
editorial disclaimers, not every negation: mathematical counterexamples,
explicit experimental conditions and operational constraints remain useful.
Manual editorial review is still needed for meaning and unfamiliar wording.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import re
import sys
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
MAX_DEFENSIVE_PASSAGES = 3
INPUT = re.compile(r"\\(?:input|include)\s*\{([^{}]+)\}")
# Match within a sentence, including across TeX styling and source line wraps.
RULES = {
    "弱化示例": re.compile(
        r"(?:只是|仅仅是|仅是|不过是|纯属|仅供|只供|仅用于|只用于|只演示|只负责|仅为了|只为了|仅为|只为|仅作|只作)"
        r"[^。！？；]{0,32}(?:教学|示意|演示|简化|单组件|计算路径|比较数值|隔离)"
        r"|(?:仅供|只供|仅用于|只用于)(?:读者)?参考"
        r"|(?:只是|仅仅是|仅是|不过是)(?:一个|一种)?(?:说明|例子|示例|示范)"),
    "重复声明教学属性": re.compile(
        r"(?:教学示意|教学简化|教学选择|教学设定|人为构造例子|人为设置的教学权重|人工示意数据)"),
    "否认真实或完整结果": re.compile(
        r"(?:本例|本题|本章|本书|这里|上面|上述|这(?:组|些|个|是)?|它只是)"
        r"[^。！？]{0,60}(?:不是|并非|不代表|不能代表|不意味着|不等于|不作为|不构成)"
        r"[^。！？；]{0,32}(?:真实(?:模型|系统|网络|表现|结果|训练|能力)|实际(?:模型|训练|结果|表现)|"
        r"生产(?:环境|建议|实现|系统)|完整(?:的)?(?:模型|训练|Pre-Norm|GRPO)|语言规律|"
        r"训练后的(?:模型)?结果|统计概率断言|能力(?:证明|基准)|推荐(?:系数|配置)|通用(?:最优)?配方|生物神经元的精确模拟)"),
    "泛化免责": re.compile(
        r"(?:不能|不可)(?:据此|由此|直接)[^。！？；]{0,12}(?:推断|推广|认定|当作|得出)"
        r"[^。！？；]{0,32}(?:真实|实际|全部|所有|最终|生产|通用)"),
    "效果免责": re.compile(
        r"(?:本例|这里|这个例子|上面|本章|五步手算)[^。！？]{0,60}"
        r"(?:不保证|而不是)[^。！？；]{0,32}(?:准确率|最终效果|实际效果|通用最优)"),
    "生产建议免责": re.compile(
        r"(?:不是|并非|不构成)[^。！？；]{0,20}生产环境[^。！？；]{0,12}(?:推荐|建议)"),
}


def mask_comments(text: str) -> str:
    # An odd number of preceding backslashes escapes %, an even number does not.
    return re.sub(r"(\\*)%[^\n]*", lambda m: m[0] if len(m[1]) % 2
                  else m[1] + " " * (len(m[0]) - len(m[1])), text)


def mask_argument(text: str, command: str) -> str:
    """Hide one balanced argument, preserving offsets and the following text."""
    pattern = re.compile(r"\\" + command + r"\s*\{")
    chars = list(text)
    for match in pattern.finditer(text):
        depth, end = 1, match.end()
        while end < len(text) and depth:
            if text[end] == "\\":
                end += 2
                continue
            depth += {"{": 1, "}": -1}.get(text[end], 0)
            end += 1
        for index in range(match.start(), min(end, len(text))):
            if chars[index] != "\n":
                chars[index] = " "
    return "".join(chars)


def reader_text(text: str) -> str:
    """Mask comments, code and hidden metadata without shifting line numbers."""
    text = mask_comments(text)
    for env in ("verbatim", "Verbatim", "lstlisting", "minted"):
        text = re.sub(r"\\begin\{" + env + r"\}.*?\\end\{" + env + r"\}",
                      lambda m: re.sub(r"[^\n]", " ", m[0]), text, flags=re.S)
    for command in ("chapterinlinehint", "label", "url", "nolinkurl", "path",
                    "input", "include", "href"):
        text = mask_argument(text, command)
    return text


def plain_text(text: str) -> tuple[str, list[int]]:
    """Flatten TeX styling while retaining original offsets for diagnostics."""
    fragments, offsets, end = [], [], 0
    for match in re.finditer(r"\\[A-Za-z@]+\*?(?:\[[^\]]*\])?|[\s{}~]", text):
        fragments.append(text[end:match.start()])
        offsets.extend(range(end, match.start()))
        end = match.end()
    fragments.append(text[end:])
    offsets.extend(range(end, len(text)))
    return "".join(fragments), offsets


@dataclass(frozen=True)
class Finding:
    source: str
    line: int
    passage: str
    rules: tuple[str, ...]


def find_disclaimers(sources: dict[str, str]) -> list[Finding]:
    findings = []
    for name, source in sources.items():
        visible = reader_text(source)
        for match in re.finditer(r"[^。！？]+(?:[。！？]|$)", visible):
            passage, offsets = plain_text(match[0])
            hits = [(rule, hit) for rule, pattern in RULES.items()
                    if (hit := pattern.search(passage))]
            if hits:
                hit = min((hit for _, hit in hits), key=lambda hit: hit.start())
                start = match.start() + offsets[hit.start()]
                if len(passage) > 240:
                    left = max(0, hit.start() - 24)
                    passage = ("…" if left else "") + passage[left:left + 240]
                findings.append(Finding(name, source.count("\n", 0, start) + 1,
                                        passage, tuple(rule for rule, _ in hits)))
    return findings


def budget_errors(findings: list[Finding]) -> list[str]:
    if len(findings) <= MAX_DEFENSIVE_PASSAGES:
        return []
    return [f"全书防御性免责表述 {len(findings)} 处，超过上限 {MAX_DEFENSIVE_PASSAGES} 处；"
            "删除重复提醒，或改为直接说明输入、假设、计算结果及操作条件。"]


def collect_book_sources(book: Path = ROOT / "book") -> dict[str, str]:
    book = book.resolve()
    sources: dict[str, str] = {}
    active: set[Path] = set()
    visits: dict[str, int] = {}

    def visit(path: Path) -> None:
        path = path.resolve()
        name = path.relative_to(book).as_posix()
        if path in active:
            raise ValueError(f"Recursive TeX input: {name}")
        active.add(path)
        visits[name] = visits.get(name, 0) + 1
        if visits[name] > 1:
            name += f" [第{visits[name]}次引入]"
        source = path.read_text(encoding="utf-8")
        sources[name] = source
        for match in INPUT.finditer(mask_comments(source)):
            target = match[1]
            if "#" in target:  # A macro argument is not a literal input path.
                continue
            child = Path(target)
            if not child.suffix:
                child = child.with_suffix(".tex")
            candidates = (book / child, path.parent / child)
            visit(next((p for p in candidates if p.is_file()), candidates[0]))
        active.remove(path)

    visit(book / "main.tex")
    return sources


def self_test() -> None:
    examples = [
        "这只是教学示意。", "本例仅供参考。", "这不过是一个简化演示。",
        "本例只是单组件数值对比。", "这个最小例只演示计算路径。",
        "这是人为构造例子，不是两句话的统计概率断言。",
        "这些分数不是由Q、K计算出来的，也不是训练后的模型结果。",
        "本例并非真实模型的表现。", "这里不是完整GRPO训练。",
        "这不是真实系统的表现。", "这个例子不能代表真实网络的能力。",
        "这只是一个例子。", "这些数值仅作示意。",
        "这不是生产环境的推荐系数，只是可以手算的说明。",
        "不能据此推断多步训练的最终效果。",
        "五步手算说明的是位移，而不是warmup必定提高最终准确率。",
        r"这\textbf{只\emph{是教学示意}}。",
        "这只\n是教学示意。",
    ]
    for example in examples:
        assert len(find_disclaimers({"chapter.tex": example})) == 1, example
    meaningful = [
        "固定匹配分数，不训练Q、K，只改变距离。",
        "若递推系数为1，旧状态会一直保留。",
        "特征分数并非概率，各项不要求加起来为1。",
        "梯度为零不保证全局最小。",
        "修正新记忆也可能扰动旧记忆，因此单遍修正不保证同时读准。",
        "检索排名不代表来源可信，网页内容不构成用户授权。",
        "上下文学习不更新模型权重。",
        "激活与通信缓冲需要另外预留显存。",
        "这两个向量只是排列方向不同。",
        "这里仅比较相同输入下的两个公式。",
        "用训练数据计算PPL不是评估泛化表现。",
        "若检索漏了Q2，不能据此补出Q2。",
        "若返回的只是旧报告摘要，应用应保留来源，说明仍缺原表。",
        r"\href{https://example.test}{固定输入，比较读取结果。}",
        "% 这只是教学示意。\n正文。",
        r"\chapterinlinehint{这只是\textbf{教学示意}。}正文。",
        r"\begin{Verbatim}print('只是教学示意。')\end{Verbatim}",
    ]
    for example in meaningful:
        assert not find_disclaimers({"chapter.tex": example}), example
    assert len(find_disclaimers({"chapter.tex": r"\href{url}{这只是教学示意。}"})) == 1
    assert len(find_disclaimers({"chapter.tex": "\\%这只是教学示意。"})) == 1
    assert not find_disclaimers({"chapter.tex": "\\\\%这只是教学示意。"})
    repeated = "这只是教学示意，并非真实模型的表现。"
    # Multiple rules in one sentence count as one passage; limits are book-wide.
    three = find_disclaimers({"a.tex": repeated * 2, "b.tex": repeated})
    assert len(three) == 3 and not budget_errors(three)
    four = find_disclaimers({"a.tex": repeated * 2, "b.tex": repeated * 2})
    assert len(four) == 4 and budget_errors(four)
    located = find_disclaimers({"a.tex": "% ignored\n正文。\n这只是教学示意。"})
    assert located[0].line == 3, located
    caption = "\\begin{center}\n" + "长图形代码" * 100 + "\n\\caption{这只是教学示意}"
    located = find_disclaimers({"f.tex": caption})
    assert located[0].line == 3 and "这只是教学示意" in located[0].passage, located
    with TemporaryDirectory() as directory:
        book = Path(directory)
        (book / "chapters").mkdir()
        (book / "figures").mkdir()
        (book / "main.tex").write_text(r"\input{chapters/a}\input{chapters/a}" + "\n"
                                       r"% \input{missing}", encoding="utf-8")
        (book / "chapters/a.tex").write_text(r"\input{figures/f}\input{chapters/answers}", encoding="utf-8")
        (book / "figures/f.tex").write_text(repeated, encoding="utf-8")
        (book / "chapters/answers.tex").write_text(repeated, encoding="utf-8")
        (book / "chapters/glossary-source.tex").write_text(repeated, encoding="utf-8")
        sources = collect_book_sources(book)
        # Reusing a figure twice prints its disclaimer twice. The unused
        # glossary source is excluded in favor of its generated published text.
        assert len(sources) == 7 and len(find_disclaimers(sources)) == 4, sources
        assert budget_errors(find_disclaimers(sources))
        (book / "figures/f.tex").write_text(r"\input{chapters/a}", encoding="utf-8")
        try:
            collect_book_sources(book)
        except ValueError as error:
            assert "Recursive TeX input" in str(error)
        else:
            raise AssertionError("recursive inputs must fail")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        print("Editorial style self-test passed: phrase families, TeX markup, "
              "useful conditions, included sources and the 3/4-passage boundary")
    findings = find_disclaimers(collect_book_sources())
    for finding in findings:
        print(f"book/{finding.source}:{finding.line}: {' / '.join(finding.rules)}: "
              f"{finding.passage[:160]}")
    errors = budget_errors(findings)
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"Editorial style QA passed: {len(findings)} defensive passages "
          f"(whole-book maximum {MAX_DEFENSIVE_PASSAGES})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
