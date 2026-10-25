#!/usr/bin/env python3
"""Audit the book from source structure through the rendered PDF.

Tests cover reading order, cross references, vector conventions, worked numeric
examples, navigation, appendix separation and final PDF page/TOC content.
"""
from __future__ import annotations

import argparse
from html import unescape
import math
import os
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
BOOK = ROOT / "book"
from check_book_contract import PART_TITLES as PARTS, CHAPTER_COUNT, core_groups, validate_contract, visible_exercise_errors, chapter_opening_errors
from generate_exercise_bank import load_exercises
from generate_bilingual_glossary import entries as glossary_entries
from generate_chapter_navigation import argument
REQUIRED = re.findall(r"\\input\{chapters/([^}]+)\}", (BOOK / "main.tex").read_text())
CHECK_COUNT = CHAPTER_COUNT + 1
EXERCISE_COUNT = len(load_exercises()[0])
GLOSSARY_COUNT = len(glossary_entries("24-lexicon.tex")) + len(glossary_entries("24b-modern-lexicon.tex"))


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
    includes(chapter("23d-agent-tools"),
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
    # New independent exercise solutions: reverse Delta, batched Attention,
    # three-step warmup, and decoupled AdamW.
    s_b_first = ((0.0, 0.6), (0.0, 0.8))
    residual_a = (1.0 - s_b_first[0][0], 0.0 - s_b_first[0][1])
    s_after_a = ((s_b_first[0][0] + residual_a[0],
                  s_b_first[0][1] + residual_a[1]), s_b_first[1])
    assert s_after_a == ((1.0, 0.0), (0.0, 0.8))
    b_read = (0.6 * s_after_a[0][0] + 0.8 * s_after_a[1][0],
              0.6 * s_after_a[0][1] + 0.8 * s_after_a[1][1])
    assert b_read == (0.6, 0.6400000000000001) or all(
        math.isclose(x, y) for x, y in zip(b_read, (0.6, 0.64)))
    assert math.isclose(math.hypot(b_read[0], b_read[1] - 1),
                        math.sqrt(.4896), abs_tol=1e-12)
    score = ((math.log(2), 0., 0.), (0., math.log(3), 0.),
             (0., 0., math.log(4)))
    reference_a = ((.5, .25, .25), (.2, .6, .2),
                   (1/6, 1/6, 2/3))
    value = ((1, 0), (0, 1), (1, 1))
    for row, expected, expected_y in zip(
        score, reference_a, ((.75, .5), (.4, .8), (5/6, 5/6))):
        exps = [math.exp(v - max(row)) for v in row]
        weights = [v / sum(exps) for v in exps]
        assert all(math.isclose(a, b, abs_tol=1e-12)
                   for a, b in zip(weights, expected))
        output = [sum(weights[k] * value[k][j] for k in range(3))
                  for j in range(2)]
        assert all(math.isclose(a, b, abs_tol=1e-12)
                   for a, b in zip(output, expected_y))
    w = 1.
    for rate in (.01, .02, .03):
        w -= rate * 2.
    assert math.isclose(w, .88, abs_tol=1e-12)
    assert math.isclose((1 - .1 * .05) * 4 - .1 * .5, 3.93)
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
    test_numeric_examples()
    from check_book_regressions import validate_existing_regressions
    main = (BOOK / 'main.tex').read_text()
    sources = {name: chapter(name) for name in REQUIRED + ['24-lexicon', '24b-modern-lexicon']}
    validate_existing_regressions(main, sources)
    issues = validate_contract()
    if issues:
        fail("\n".join(issues))
    print(f"Source QA passed: {CHAPTER_COUNT} chapters, {CHECK_COUNT} self-checks, "
          f"{EXERCISE_COUNT} exercises and {GLOSSARY_COUNT} glossary rows")


def expected_subsection_bookmarks() -> dict[str, list[str]]:
    r"""Expected x.y bookmarks in typesetting order, not just PDF outline totals.

    The compact printed TOC stops at chapters; PDF bookmarks include subsections.
    Count numbered \section and \subsection commands across the actual
    main.tex input order; never derive expectations from the PDF being tested.
    """
    main = (BOOK / "main.tex").read_text(encoding="utf-8")
    includes(main, "bookmarksdepth=2", "PDF subsection bookmark depth")
    includes(main, r"\setcounter{tocdepth}{1}", "compact chapter-level printed TOC")

    def no_comments(body: str) -> str:
        return re.sub(r"(?<!\\)%[^\n]*", "", body)

    main = no_comments(main)
    events = re.compile(
        r"\\appendix\b|\\section\s*\{|\\input\{chapters/([^}]+)\}"
    )
    heads = re.compile(r"\\(section|subsection)\s*\{")
    chapter_id = 0
    appendix_id = 0
    appendix = False
    current: str | None = None
    expected: dict[str, list[str]] = {}

    def section_start() -> None:
        nonlocal chapter_id, appendix_id, current
        if appendix:
            appendix_id += 1
            current = chr(ord("A") + appendix_id - 1)
        else:
            chapter_id += 1
            current = str(chapter_id)
        if current in expected:
            fail(f"Repeated expected outline heading {current}")
        expected[current] = []

    for event in events.finditer(main):
        command = event.group(0)
        if command.startswith(r"\appendix"):
            appendix = True
            current = None
        elif command.startswith(r"\section"):
            section_start()
        else:
            lesson = no_comments(chapter(event.group(1)))
            for heading in heads.finditer(lesson):
                if heading.group(1) == "section":
                    section_start()
                elif current is not None:
                    expected[current].append(
                        f"{current}.{len(expected[current]) + 1}"
                    )

    if list(expected) != [str(i) for i in range(1, CHAPTER_COUNT + 1)] + list("ABCDEFG"):
        fail(f"Bookmark source reference must contain chapters 1..{CHAPTER_COUNT} and appendices A..G")
    if len([item for group in expected.values() for item in group]) < 150:
        fail("Suspiciously few numbered subsection headings in source")
    return expected


def validate_subsection_bookmarks(reader) -> None:
    """Compare every H2 bookmark's prefix, parent and order against source."""
    expected = expected_subsection_bookmarks()

    def nested(items):
        result = []
        for item in items:
            if isinstance(item, list):
                if not result or result[-1]["children"]:
                    fail("PDF bookmark has orphaned/duplicate nested levels")
                result[-1]["children"] = nested(item)
            elif hasattr(item, "title"):
                result.append({"title": str(item.title).strip(),
                               "entry": item, "children": []})
            else:
                fail(f"Unknown PDF bookmark node: {type(item).__name__}")
        return result

    roots = nested(reader.outline)
    if len(roots) != len(PARTS) + 1:
        fail("PDF bookmark tree must have 9 part roots and 1 appendix root")
    chapter_re = re.compile(r"^(?:第)?(\d+)(?:章)?\s+\S")
    appendix_re = re.compile(r"^(?:附录\s*)?([A-G])\s+\S")
    subsection_re = re.compile(r"^(\d+|[A-G])\.(\d+)\s+\S")
    by_parent = {}
    for root_number, root in enumerate(roots):
        for node in root["children"]:
            if subsection_re.match(node["title"]):
                fail(f"PDF subsection is at part level: {node['title']!r}")
            match = (appendix_re if root_number == len(PARTS) else chapter_re).match(
                node["title"])
            if match is None:
                continue  # The unnumbered reading guide/recap.
            key = match.group(1)
            if key in by_parent:
                fail(f"Duplicate PDF chapter/appendix bookmark: {key}")
            by_parent[key] = node

    if set(by_parent) != set(expected):
        fail(f"PDF numbered bookmark parents mismatch: "
             f"missing={sorted(set(expected)-set(by_parent))}, "
             f"extra={sorted(set(by_parent)-set(expected))}")

    checked = 0
    for chapter_name, required in expected.items():
        chapter_node = by_parent[chapter_name]
        parent_page = reader.get_destination_page_number(chapter_node["entry"])
        observed = []
        previous_page = parent_page
        for subsection in chapter_node["children"]:
            if subsection["children"]:
                fail(f"PDF subsection has children instead of being H2: "
                     f"{subsection['title']!r}")
            match = subsection_re.match(subsection["title"])
            if not match:
                fail(f"Missing x.y prefix in {chapter_name} subsection bookmark: "
                     f"{subsection['title']!r}")
            label = f"{match.group(1)}.{int(match.group(2))}"
            observed.append(label)
            page_number = reader.get_destination_page_number(subsection["entry"])
            if not 0 <= page_number < len(reader.pages):
                fail(f"PDF subsection destination outside page range: {label}")
            if page_number < previous_page:
                fail(f"PDF subsection destination goes backwards: {label}")
            previous_page = page_number
        if observed != required:
            fail(f"PDF subsection bookmarks missing/misnumbered/misnested "
                 f"under {chapter_name}: expected={required!r}; "
                 f"found={observed!r}")
        checked += len(observed)
    print(f"PDF subsection bookmark QA: {checked} x.y leaves match "
          f"{len(expected)} numbered chapters/appendices and source order")


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
    # Count source tables on the cover separately from included chapter files.
    expected_tables += len(re.findall(r"\\begin\{(?:tabularx|tabular|longtable)\}", (BOOK/'main.tex').read_text()))
    # The reusable part-map table is expanded once on each part opener.
    expected_tables += len(re.findall(r"(?m)^\\partmap[a-z]+\s*$",
                                     (BOOK / "main.tex").read_text()))
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
    # Nine numbered parts, CHAPTER_COUNT chapters and A--G appendices must
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
            elif not (title.startswith("序章：") or
                      title.startswith("终章：回到那四个 Token")):
                fail(f"Unnumbered PDF chapter bookmark: {title!r}")
    if chapter_numbers != list(range(1, CHAPTER_COUNT + 1)):
        fail(f"PDF chapter bookmark numbers must be 1--{CHAPTER_COUNT} in order; "
             f"found {chapter_numbers!r}")
    print(f"PDF bookmark QA: {len(PARTS)} numbered parts, "
          f"{len(chapter_numbers)} numbered chapters, 7 lettered appendices")
    validate_subsection_bookmarks(reader)


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
    from check_dated_claims import mcp_page_errors
    for error in mcp_page_errors(pages):
        fail(error)
    if "local-build" in text:
        fail("Rendered PDF still contains the unknown-revision placeholder")
    expected_sha = os.environ.get("BOOK_BUILD_SHA") or os.environ.get("GITHUB_SHA")
    if expected_sha and normalized(text).count(expected_sha[:12]) != 2:
        fail("Copyright page and Appendix G must both identify the actual build commit")
    # Specific illustrated explainer that previously split after only its
    # first sentence. The caption, body and Value comparison must stay together.
    diagram_intro = [i for i, body in enumerate(pages)
                     if "图解：为什么一会儿写" in body]
    diagram_body = [i for i, body in enumerate(pages)
                    if "Value 同理" in body]
    if (len(diagram_intro) != 1 or len(diagram_body) != 1
            or diagram_intro[0] != diagram_body[0]):
        fail(f"Key-transpose diagram split across pages: "
             f"intro={diagram_intro}, Value comparison={diagram_body}")

    # Verify *click destinations* rather than merely the existence of
    # labels. A previous bug sent all 43 "full answer" links to the start
    # of Appendix D.2 even while printing the correct per-answer folio.
    includes((BOOK / "main.tex").read_text(encoding="utf-8"),
             r"\hyperref[answer:#1]",
             "self-check answer links must use the chapter-specific anchor")

    # Reject an old regression where literal \s matched backslash+letter,
    # so real D.2/E.1 headings appeared missing despite a healthy PDF.
    test_headings = ("D.2 全书随堂自测参考解答\n"
                     "E.1 全量中英对照：146 项术语速查\n")
    if not re.search(r"(?m)^\s*D\.2\s+全书随堂自测参考解答\s*$", test_headings):
        fail("D.2 heading matching self-test failed")
    if not re.search(r"(?m)^\s*E\.1\s+全量中英对照[^\n]*$", test_headings):
        fail("E.1 heading matching self-test failed")
    # Match the actual standalone answer/glossary headings, independent of TOC depth.
    # Match only the actual standalone D.2/E.1 section header lines: TOC
    # entries carry dotted page leaders and must never count as appendix pages.
    answer_starts = [i for i, body in enumerate(pages)
                     if re.search(r"(?m)^\s*D\.2\s+全书随堂自测参考解答\s*$", body)]
    answer_ends = [i for i, body in enumerate(pages)
                   if re.search(r"(?m)^\s*E\.1\s+全量中英对照[^\n]*$", body)
                   and not any(" . . . " in line for line in body.splitlines()
                               if "E.1 全量中英对照" in line)]
    # A flowing self-check can share a page with another chapter. Count
    # headings rather than pages.
    question_pages = [i for i, body in enumerate(pages)
                      if "读完自测" in body]
    question_count = sum(body.count("读完自测：") for body in pages)
    if (len(answer_starts) != 1 or len(answer_ends) != 1
            or question_count != CHECK_COUNT):
        fail(f"Expected one self-check per chapter and prelude: rendered self-check boxes and unique D.2 / E.1; "
             f"found {question_count} checks")
    compact_selfchecks=normalized(text)
    if re.search(r'读完自测[（(]续[）)](?:附录C[^。]{0,100})?提示与解答',compact_selfchecks):
        fail("A self-check continuation contains only navigation, without a question")
    obsolete=visible_exercise_errors(text)
    if obsolete:fail("Printed PDF contains a legacy exercise ID: "+'; '.join(obsolete))
    if re.search(r"图\s*\d+[^\n]{0,12}全书路线",text):
        fail("Route micro-map occupies a numbered figure caption")
    if text.count("终章：回到那四个 Token")<2:
        fail("Final chapter bookend missing from contents/body")
    if "思路提示：" in normalized(text):
        fail("Hints must stay in Appendix D, not under self-check questions")
    rendered_metadata = re.findall(
        r"〔[^〕]+·(?:基础|标准|挑战)·约\d+分钟〕", normalized(text))
    if len(rendered_metadata) != EXERCISE_COUNT:
        fail(f"All exercise metadata labels must render: found {len(rendered_metadata)}")
    print(f"Exercise metadata QA: {EXERCISE_COUNT} visible chapter/difficulty/time labels")
    if "章末先核对：" in text:
        fail("Answer leaked immediately under self-check in reader PDF")
    start_answer, end_answer = answer_starts[0], answer_ends[0]
    if not 0 <= start_answer < end_answer < len(reader.pages):
        fail("Invalid Appendix D.2 answer pages")
    named_destinations = reader.named_destinations
    # D.1 can end above D.2 on the same physical page. Compare destination
    # coordinates as well as folios so valid bank links cannot masquerade as
    # chapter self-check links simply because they share that boundary page.
    answer_start_top = float(named_destinations['subsection.D.2'].top)
    def is_selfcheck_answer(destination):
        page = reader.get_destination_page_number(destination)
        if not start_answer <= page < end_answer:
            return False
        return page != start_answer or float(destination.top) <= answer_start_top
    question_page_set = set(question_pages)
    # Include the immediately following page only if it has no new exercise
    # heading: a breakable tcolorbox may place its answer link there.
    inspect_pages = set(question_pages)
    for question_page in question_pages:
        if (question_page + 1 < len(reader.pages)
                and question_page + 1 not in question_page_set):
            inspect_pages.add(question_page + 1)
    # Scan each candidate page only once, even when two self-checks share a
    # page or adjacent earlier boxes flow into the same continuation page.
    answer_links = []
    for page_index in sorted(inspect_pages):
        on_page_links = []
        for ref in reader.pages[page_index].get("/Annots", []):
            annot = ref.get_object()
            action = annot.get("/A")
            if action is None:
                continue
            if hasattr(action, "get_object"):
                action = action.get_object()
            if action.get("/S") != "/GoTo":
                continue
            dest_name = str(action.get("/D", ""))
            if dest_name not in named_destinations:
                continue
            target_page = reader.get_destination_page_number(
                named_destinations[dest_name])
            if is_selfcheck_answer(named_destinations[dest_name]):
                answer_links.append(dest_name)
                on_page_links.append(dest_name)
        # Questions may flow to the next page. The global check below still
        # requires exactly one correct answer destination per exercise group.
    if len(answer_links) != CHECK_COUNT or len(set(answer_links)) != CHECK_COUNT:
        fail(f"Every self-check must link to its unique answer: "
             f"{len(answer_links)} links to {len(set(answer_links))} "
             "distinct D.2 targets (expected one per self-check)")
    print("Chapter answer navigation QA: all self-check links resolve to "
          "distinct destinations within Appendix D.2")
    # Each answer-group title links back to its source self-check. Reject a
    # title sitting in the bottom 30 mm, where its first answer cannot follow.
    answer_heading_targets = set()
    for page_index in range(start_answer, end_answer):
        for ref in reader.pages[page_index].get("/Annots", []):
            annot = ref.get_object()
            action = annot.get("/A")
            if action is None:
                continue
            action = action.get_object()
            dest_name = str(action.get("/D", ""))
            if action.get("/S") != "/GoTo" or dest_name not in named_destinations:
                continue
            target = reader.get_destination_page_number(named_destinations[dest_name])
            if target in question_page_set:
                answer_heading_targets.add(dest_name)
                if float(annot["/Rect"][1]) < 85:
                    fail(f"Answer chapter heading stranded at bottom of PDF page {page_index + 1}")
    if len(answer_heading_targets) != CHECK_COUNT:
        fail("Expected one self-check per chapter and prelude: rendered answer chapter headings with links back to questions")
    print("Answer heading pagination QA: all answer titles leave room for their first answer")
    # Page-bottom regression: the "shape-first route" introduction may not be
    # stranded on a separate page from the first row of its table.
    route_pages = [i for i, page_text in enumerate(pages, 1)
                   if "本章运算路线" in page_text]
    if len(route_pages) != 1:
        fail(f"Expected one chapter 23 route caption, found pages {route_pages}")
    route_page = route_pages[0]
    if "查表与位置" not in pages[route_page - 1]:
        fail(f"Chapter 23 route heading stranded on PDF page {route_page}; "
             "the route table must start on the same page")

    # R01 explicit pagination regression: after compressing the two-line locator,
    # the MLP and prediction-task chapters (printed as 9 and 13 since the
    # vectors/dot-product and context-gap/RNN merges) must end with a self-check
    # AND a conclusion on the same substantive page. Never lower the generic orphan/blank-page thresholds.
    numbered_pages: dict[int, int] = {}
    chapter_tops: dict[int, float] = {}
    part_pages = [reader.get_destination_page_number(item)
                  for item in reader.outline if not isinstance(item, list)]
    for item in reader.outline:
        if isinstance(item, list):
            for bookmark in item:
                title = str(getattr(bookmark, "title", ""))
                match = re.match(r"^(?:第)?(\d+)(?:章)?\s+\S", title)
                if match:
                    chapter_tops[int(match.group(1))]=float(bookmark.top)
                    numbered_pages[int(match.group(1))] = (
                        reader.get_destination_page_number(bookmark)
                    )
    for chapter_number in (9, 13):
        if chapter_number not in numbered_pages or chapter_number + 1 not in numbered_pages:
            fail(f"Missing chapter bookmarks for R01 page regression: {chapter_number}")
        # A part's introduction can have its own page before its first chapter.
        # End the preceding chapter at that boundary, not at the next chapter.
        next_boundary = min([numbered_pages[chapter_number + 1]] + [
            p for p in part_pages
            if numbered_pages[chapter_number] < p < numbered_pages[chapter_number + 1]
        ])
        last_page_index = next_boundary - 1
        if last_page_index < numbered_pages[chapter_number]:
            fail(f"Chapter {chapter_number} has invalid physical page range")
        closing_page = pages[last_page_index]
        han_count = len(re.findall(r"[\u4e00-\u9fff]", closing_page))
        if ("读完自测" not in closing_page or "小结" not in closing_page
                or han_count < 260
                or closing_page.rfind("小结") < closing_page.rfind("读完自测")):
            fail(f"R01 chapter {chapter_number} stranded its conclusion on PDF "
                 f"page {last_page_index + 1} (Han={han_count}); "
                 "retain the compact locator and real orphan gate")
    print("R01 chapter-end pagination QA passed: chapters 9 and 13 retain "
          "self-check and substantive conclusion pages")

    compact = normalized(text)
    # A spilled cover can masquerade as an extra TOC page. Check both locations
    # before diagnosing the compact TOC, so the error identifies the cause.
    if any(item not in normalized(pages[0]) for item in (
            'CoCoThinkandcontributors', 'https://github.com/CoCoThink/ai-by-intuition',
            '原创内容·CCBY4.0')):
        fail('Cover must fit one page, including author, URL and licence')
    if '版权、致谢与版本' not in normalized(pages[1]):
        fail('Copyright page must immediately follow the single-page cover')
    # Search until the printed guide rather than guessing from TOC line counts.
    guide_index = next(
        (i for i, body in enumerate(pages) if i > 1 and
         "怎么读：路线与数学预备" in body),
        None)
    if guide_index is None:
        fail("Front-matter reading guide missing after table of contents")
    if guide_index > 4:
        fail("Printed chapter TOC must occupy no more than two pages before the reading guide")
    guide = normalized(pages[guide_index])
    for heading in ("速读", "标准", "动手", "数学预备与表示约定", "ID、位置和矩阵行列从1数", "图例：先判断这一块要你做什么"):
        if heading not in guide:
            fail(f"Reading routes, prerequisites and conventions must fit one page: {heading}")
    toc = normalized("".join(pages[1:guide_index]))
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
    # Dedicated part introductions are intentional short pages. Accept only
    # actual part bookmark destinations with both complete learning-bridge rows;
    # all ordinary chapter pages retain the same orphan thresholds below.
    part_openers = set()
    for item in reader.outline:
        if isinstance(item, list):
            continue
        if re.match(r"^第[一二三四五六七八九十]+部分", str(item.title)):
            index = reader.get_destination_page_number(item)
            if not all(label in pages[index] for label in ("从这里出发", "本部分你会学会",
                                                          "本部分地图", "全书路线", "你在这里",
                                                          "读完试试看")):
                fail(f"Part introduction incomplete on page {index + 1}")
            part_openers.add(index + 1)
    if len(part_openers) != len(PARTS):
        fail(f"Expected {len(PARTS)} dedicated part introductions, got {sorted(part_openers)}")
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
        if (i < len(pages) - 1 and i not in part_openers
                and han_count < 90 and latin_words < 80 and not math_dense_page):
            fail(f"Likely stranded content on interior page {i}: {han_count} Han chars")
    # Read only tag attributes: PDF text can contain literal control chars
    # that make pdftotext's XHTML *text nodes* invalid XML.
    bbox = subprocess.run(["pdftotext", "-bbox-layout", str(path), "-"],
                          capture_output=True, text=True, check=True).stdout
    pages_with_boxes = re.findall(r"<page\b([^>]*)>(.*?)</page>", bbox, re.S)
    if len(pages_with_boxes) != len(pages)-1:
        fail(f"PDF bbox page count mismatch: {len(pages_with_boxes)}")
    words_checked = 0
    page_body_words = []
    for pageno, (attrs, body) in enumerate(pages_with_boxes, 1):
        size = re.search(r'width="([\d.]+)"\s+height="([\d.]+)"', attrs)
        if not size:
            fail(f"PDF page {pageno} has no width/height")
        width, height = map(float, size.groups())
        body_words = []
        for word in re.finditer(r"<word\s+([^>]*)>(.*?)</word>", body, re.S):
            word_attrs = word[1]
            vals = []
            for key in ("xMin", "yMin", "xMax", "yMax"):
                m = re.search(key + r'="([\d.+-]+)"', word_attrs)
                if not m:
                    fail(f"Malformed word bounding box on page {pageno}")
                vals.append(float(m.group(1)))
            xmin, ymin, xmax, ymax = vals
            if 55 < ymin and ymax < height - 65:
                body_words.append((ymin, ymax, unescape(word[2])))
            words_checked += 1
            if not (-2 <= xmin <= xmax <= width + 2 and -2 <= ymin <= ymax <= height + 2):
                fail(f"Text outside PDF page bounds on page {pageno}: {vals}")
        page_body_words.append(body_words)
        if (body_words and pageno > guide_index + 1
                and pageno not in part_openers):
            body_text = "".join(word[2] for word in body_words)
            occupied = (max(word[1] for word in body_words) - 55) / (height - 120)
            self_check_tail = re.match(
                r"^(?:读完自测|[■]?\s*小结|提示与解答|提示与完整解答|完整解答与订正说明|本部分累积复习|附录C[·：]|"
                r"[123]\.(?:形状|手算|预测|找错|计算|区分|估算|比较|解释|定位|分工|证据|分类))",
                normalized(body_text))
            if self_check_tail and occupied < .5:
                fail(f"Sparse self-check/conclusion tail on page {pageno}: "
                     f"only {occupied:.0%} of the body height used")
            line_count = len({round(word[0] / 6) for word in body_words})
            if occupied < .35 and line_count <= 8:
                fail(f"Stranded short section on page {pageno}: "
                     f"{line_count} lines, {occupied:.0%} body height")
    if words_checked < 1000:
        fail(f"Suspiciously few PDF words checked: {words_checked}")
    print("Chapter ending density QA: no sparse self-check/conclusion tails or stranded short sections")

    # Chapter dividers are structural source commands, not repeated page locators.
    # Validate every numbered destination and require substantive page content;
    # the page-wide bounding-box and orphan-page checks above remain in effect.
    if sorted(numbered_pages) != list(range(1, CHAPTER_COUNT + 1)):
        fail(f"Opening guard requires chapter bookmarks 1..{CHAPTER_COUNT}")
    parameter_han_counts=[]
    for name in REQUIRED:
        source=chapter(name)
        for compass in re.finditer(r'\\chaptercompass\{',source):
            pos=compass.end()-1
            for _ in range(4):
                value,pos=argument(source,pos)
                while pos<len(source) and source[pos].isspace():pos+=1
            parameter_han_counts.append(len(re.findall(r'[\u4e00-\u9fff]',value)))
    if len(parameter_han_counts)!=CHAPTER_COUNT:
        fail("Opening guard requires one compass per numbered chapter")
    for chapter_number, opening_index in sorted(numbered_pages.items()):
        if not pages_with_boxes[opening_index][1].strip():
            fail(f"Empty chapter opening page for chapter {chapter_number}")
        height=float(reader.pages[opening_index].mediabox.height)
        # Exclude any preceding chapter on a shared page, including its compass.
        opening_text=''.join(word[2] for word in page_body_words[opening_index]
            if word[0]>=height-chapter_tops[chapter_number]-2)
        opening_errors=chapter_opening_errors(chapter_tops[chapter_number],
            height,opening_text,parameter_han_counts[chapter_number-1])
        if opening_errors:fail(f"Chapter {chapter_number} opening page {opening_index+1}: "+'; '.join(opening_errors))
    print(f"Chapter opening QA passed: {CHAPTER_COUNT}/{CHAPTER_COUNT} destinations above bottom third, with substantive text")
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
