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
    "学习是什么：从规则到参数更新",
    "把许多数一起算，再让文字进入计算",
    "让词与词交换信息",
    "组装、训练并使用 Transformer",
    "改进模型并构建可靠应用",
    "选读专题一：从 CNN 到视觉 Transformer",
    "选读专题二：联想记忆与高维检索",
]
REQUIRED = [
    "00-guide",
    "00d-rules-gap",
    "00-functions",
    "16-loss-gradient",
    "07-functions-relu",
    "17-backpropagation",
    "18b-end-to-end-learning",
    "18-generalization",
    "01-vectors",
    "02-dot-product",
    "03-matrix-multiplication",
    "10-mlp",
    "18c-training-engineering",
    "20a-tokenizer",
    "20-embeddings",
    "20b-task-contract",
    "21a-context-gap",
    "21-rnn",
    "21b-why-attention",
    "11-softmax-memory",
    "22a-position-multihead",
    "22-transformer-architecture",
    "10b-ffn-output-head",
    "22b-token-to-output",
    "22c-language-training",
    "23-llm-systems",
    "23a-from-toy-to-gpt",
    "23aa-pretraining-icl",
    "23c-post-training",
    "23d-agent-systems",
    "23b-deployment-and-ecosystem",
    "22d-modern-transformers",
    "23e-tech-judgement",
    "19-cnn",
    "04-key-value-outer-product",
    "05-memory-interference",
    "06-better-linear-memory",
    "08-stacking-key-value",
    "09-nonlinearity-and-memory",
    "14-summary",
    "13-capacity",
    "00b-math-tools",
    "00c-symbols",
    "25-integrated-practice",
    "25b-modern-practice",
    "15-practice",
    "24-lexicon",
    "24b-modern-lexicon",
    "24c-concept-map",
    "24d-english-index",
    "27-answer-key",
    "28-chapter-checks",
    "26-sources",
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
    # Answer key exercise: (6,0) · (5,12) = 30, cos = 5/13.
    assert math.isclose(6 * 13 * (5 / 13), 30)
    print("Numerical QA passed: 3-position joint SGD loss and legacy independent illustrations checked")


def validate_source() -> None:
    main = (BOOK / "main.tex").read_text(encoding="utf-8")
    parts = re.findall(r"\\part\{([^}]+)\}", main)
    if parts != PARTS:
        fail(f"Expected seven reading parts; found {parts!r}")
    inputs = re.findall(r"\\input\{chapters/([^}]+)\}", main)
    if inputs != REQUIRED or len(inputs) != len(set(inputs)):
        fail(f"Reading order/appendix differs from the current curriculum: {inputs!r}")
    sources = {name: chapter(name) for name in REQUIRED}
    includes(main, r"\appendix", "main")
    includes(main, r"\part*{附录：练习、术语与答案}", "main")
    includes(main, r"\ctexset{", "native CTeX heading styling")
    includes(main, "name={第,章}", "visible chapter number format")
    if r"\usepackage{titlesec}" in main or r"\titleformat" in main:
        fail("titlesec must not override tagged section headings")
    if main.find(r"\appendix") <= main.find(r"\part{选读专题二：联想记忆与高维检索}"):
        fail("Appendices must follow optional part VII")
    if main.count(r"\learningbridge{") != 7:
        fail("Seven sections need seven minimal part introductions")

    # Explicit vector and architecture consistency.
    for name in ("21b-why-attention", "11-softmax-memory"):
        includes(sources[name], r"\vect x_i^\top W_Q" if name.startswith("21b") else r"\vect x^\top W_Q", name)
    includes(sources["11-softmax-memory"], r"W_Q^\top\vect x", "row/column explanation")
    includes(sources["22-transformer-architecture"], r"\vect h_T^\top W_{\rm vocab}", "row vocabulary projection")
    includes(sources["22-transformer-architecture"], r"\input{figures/pre-norm-block}", "true Pre-Norm figure")
    includes(sources["22-transformer-architecture"], r"X_{\rm block}", "distinct Block output")
    includes(sources["22a-position-multihead"], "0.990", "two-head worked example")
    includes(sources["22a-position-multihead"], "0.9997", "scaled-dot-product example")
    includes(sources["22a-position-multihead"], "位置", "positional example")
    includes(sources["22a-position-multihead"], r"\label{eq:pos-swap-d3}", "nondegenerate 3D position comparison")
    includes(sources["21a-context-gap"], r"\label{check:21a-context-gap}", "context gap self-check")
    includes(sources["21b-why-attention"], r"\vect q^\top=(1,1)", "Embedding-based Q/K example")
    includes(sources["22c-language-training"], r"\label{sec:transformer-gradient-step}", "gradient step")
    includes(sources["22b-token-to-output"], r"\label{eq:three-token-block-output}", "canonical Pre-Norm numeric forward")
    includes(sources["22b-token-to-output"], "0.1244", "causal attention example")
    includes(sources["22c-language-training"], "1.611377", "three-position joint loss")
    includes(sources["23a-from-toy-to-gpt"], "768/12=64", "GPT-2 scale recovery")
    includes(sources["23aa-pretraining-icl"], r"\label{concept:in-context-learning}", "pretraining and ICL")
    includes(sources["23c-post-training"], "只改 Prompt/Few-shot", "SFT versus prompting")
    includes(sources["23d-agent-systems"], "g_{Q2}", "shared report arithmetic")
    includes(sources["23d-agent-systems"], "A2A", "protocol distinctions")
    includes(sources["23e-tech-judgement"], "Scaling Laws", "innovation framework")
    includes(sources["22c-language-training"], "0.25764", "shared embedding gradient")
    includes(sources["23b-deployment-and-ecosystem"], "16{,}000", "LoRA computation")
    includes(sources["23b-deployment-and-ecosystem"], "软标签", "distillation computation")
    includes(sources["23b-deployment-and-ecosystem"], "-127", "quantization computation")
    includes(sources["20a-tokenizer"], "BPE", "subword example")
    includes(sources["20-embeddings"], r"\R^{5\times3}", "authoritative E shape")
    includes(sources["20b-task-contract"], "50,257", "GPT-2 preview")
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
        ("embedding-training-projection", "20-embeddings"),
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

    # All textbook tabular/tabularx data tables must declare their first row as TH.
    table_envs = sum(len(re.findall(r"\\begin\{(?:tabularx|tabular|longtable)\}", body))
                     for body in sources.values())
    marked_headers = sum(body.count(r"\tagpdfsetup{table/header-rows={1}}")
                         for body in sources.values())
    if table_envs != 23 or marked_headers != table_envs:
        fail(f"Table header coverage incomplete: {marked_headers}/{table_envs} (expected 23)")

    # The prominent diagram and teaching resources are all editable TikZ.
    for figure in ("row-column-intuition", "key-value-layout", "pre-norm-block",
                   "attention-why-qkv"):
        file = BOOK / "figures" / f"{figure}.tex"
        if not file.is_file() or r"\begin{tikzpicture}" not in file.read_text(encoding="utf-8"):
            fail(f"Missing editable figure {figure}")
    # Figure 9: both weighted scores and values must flow INTO the result.
    # Source-level endpoint assertions complement page-render review; curved
    # Bezier connectors previously overshot the result boundary and appeared
    # to point out of the diagram.
    qkv = (BOOK / "figures" / "attention-why-qkv.tex").read_text(
        encoding="utf-8")
    for edge in (
        "(goal.south) -- (qkv-split);",
        "(qkv-split) -| (find.north);",
        "(qkv-split) -| (read.north);",
        "(weight.south) -- ([xshift=-31.5mm]out.north);",
        "(value.south) -- ([xshift=31.5mm]out.north);",
    ):
        includes(qkv, edge, "figure 9 directed connector")
    for obsolete in (
        "to[out=-115,in=90]",
        "to[out=-65,in=90]",
        "to[out=-90,in=150]",
        "to[out=-90,in=30]",
        "(out.north west)",
        "(out.north east)",
    ):
        if obsolete in qkv:
            fail(f"Figure 9 retains a misleading arrow route: {obsolete}")

    # Figure 16 must not reverse the training feedback arrow or visually suggest
    # that inference -> post-training -> external tools is one execution chain.
    concept = sources["24c-concept-map"]
    for arrow in (
        "(upd.north) --",
        "(emb.south);",
        "(post.north) -- ++(0,5mm) -| (upd.south);",
        "(gen.east) --",
        "(tools.west);",
    ):
        includes(concept, arrow, "figure 16 arrow direction")
    for obsolete in (
        "([yshift=4mm]emb.north)",
        "(gen)--(post)",
        "(post)--(tools)",
        "(ffn.east) -- ++(.5,0) |- (tools.east)",
    ):
        if obsolete in concept:
            fail(f"Figure 16 contains a misleading or reversed arrow: {obsolete}")

    # A light title bar must not use tcolorbox's default white title text.
    weight_figure = (BOOK / "figures" / "attention-three-step-weights.tex").read_text(
        encoding="utf-8")
    includes(weight_figure, "coltitle=ink", "figure 10 dark title on light background")
    includes(sources["00c-symbols"], r"\beta=1/\tau", "inverse-temperature definition")
    includes(sources["23-llm-systems"], r"\beta=1/\tau", "sampling temperature")
    includes(sources["18c-training-engineering"], "0.943", "two-step Adam example")
    includes(sources["10-mlp"], r"\vect x^\top W_1", "row-vector MLP")
    includes(sources["11-softmax-memory"], r"\label{concept:self-attention}", "merged chapter")
    for name, body in sources.items():
        if re.search(r"(?<![a-zA-Z\\])extbf\{", body) or "\textbf{" in body:
            fail(f"Broken bold escape in {name}")
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

    if len(table_nodes) != 23:
        fail(f"Expected 23 tagged data tables, found {len(table_nodes)}")
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
    compact = normalized(text)
    toc = normalized("".join(pages[1:6]))
    for num, title in zip("一二三四五六七", PARTS):
        # pdftotext can interleave the page number before the title.
        # Permit a 1-3 digit TOC folio between the part marker and title.
        pattern = rf"第{num}部分\d{{0,3}}{re.escape(normalized(title))}"
        if not re.search(pattern, toc):
            fail(f"Rendered TOC missing part 第{num}部分: {title}")
    if "第八部分" in toc:
        fail("Rendered table of contents has an extra part")
    for item in ("数学速查", "符号与张量形状速览", "位置编码", "Pre-Norm",
                 "LayerNorm", "1.611377", "LoRA", "16,000",
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
    # Read only tag attributes: PDF text can contain literal control chars
    # that make pdftotext's XHTML *text nodes* invalid XML.
    bbox = subprocess.run(["pdftotext", "-bbox-layout", str(path), "-"],
                          capture_output=True, text=True, check=True).stdout
    pages_with_boxes = re.findall(r"<page\b([^>]*)>(.*?)</page>", bbox, re.S)
    if len(pages_with_boxes) != len(pages)-1:
        fail(f"PDF bbox page count mismatch: {len(pages_with_boxes)}")
    words_checked = 0
    for pageno, (attrs, body) in enumerate(pages_with_boxes, 1):
        size = re.search(r'width="([\d.]+)"\s+height="([\d.]+)"', attrs)
        if not size:
            fail(f"PDF page {pageno} has no width/height")
        width, height = map(float, size.groups())
        for word_attrs in re.findall(r"<word\s+([^>]*)>", body):
            vals = []
            for key in ("xMin", "yMin", "xMax", "yMax"):
                m = re.search(key + r'="([\d.+-]+)"', word_attrs)
                if not m:
                    fail(f"Malformed word bounding box on page {pageno}")
                vals.append(float(m.group(1)))
            xmin, ymin, xmax, ymax = vals
            words_checked += 1
            if not (-2 <= xmin <= xmax <= width + 2 and -2 <= ymin <= ymax <= height + 2):
                fail(f"Text outside PDF page bounds on page {pageno}: {vals}")
    if words_checked < 1000:
        fail(f"Suspiciously few PDF words checked: {words_checked}")
    print(f"PDF QA passed: {len(pages)-1} pages (tagged={tagged}); text boxes stay within page bounds")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdf", type=Path)
    args = parser.parse_args()
    validate_source()
    if args.pdf:
        validate_pdf(args.pdf.resolve())
