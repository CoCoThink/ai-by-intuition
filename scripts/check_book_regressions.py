#!/usr/bin/env python3
"""Existing reproduction, accessibility, figure and release regressions.

Kept separate from the canonical inventory checks so curriculum changes do not
remove independent mathematical and publication regression coverage.
"""
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import quote
ROOT = Path(__file__).resolve().parents[1]
BOOK = ROOT / 'book'

def fail(message):
    raise SystemExit('REGRESSION ERROR: '+message)

def includes(body, needle, where):
    if needle not in body: fail(f'Missing {needle!r} in {where}')

def validate_existing_regressions(main, sources):
    # The manual release gate must consume exactly the PDF artifact built here.
    production = (ROOT / ".github/workflows/build-latex.yml").read_text(encoding="utf8")
    includes(production, "export BOOK_BUILD_SHA='${{ github.sha }}'", "container source SHA")
    includes(production, "bash ../scripts/build_book.sh", "shared build entry point")
    release = (ROOT / ".github/workflows/publish-release.yml").read_text(encoding="utf8")
    for workflow in (production, release):
        includes(workflow, "ai-by-intuition-book", "matching build/release artifact")
        includes(workflow, "AI-by-Intuition-Book.pdf", "matching build/release PDF filename")
    if 'summary["pages"] == 99' in release or "1,472/1,472" in release:
        fail("Release gate still hard-codes obsolete PDF statistics")
    includes(release, 'summary["pages"] == actual_pages', "PDF page and audit reconciliation")
    includes(release, "failedRules", "PDF/UA-2 release audit enforcement")
    # Regression gate: each build must check the *last* latexmk log and
    # extracted full PDF, not merely the presence of source-level labels.
    includes(production, "python3 scripts/check_latex_references.py --self-test",
             "reference-gate positive/negative fixture test")
    includes(production, "python3 scripts/check_chapter_crossrefs.py --self-test",
             "stale chapter-number regression tests")
    includes(production, "python3 scripts/check_part_references.py --self-test",
             "Roman/Chinese/Arabic part-reference regression canaries")
    includes(production, "python3 scripts/check_part_references.py\n",
             "mandatory semantic part reference gate")

    includes(production, "python3 scripts/check_chapter_crossrefs.py\n",
             "mandatory source-order chapter reference check")

    includes(production, "Reject unresolved cross-references in final LaTeX log and PDF",
             "mandatory final cross-reference gate")
    includes(production, "--log book/build/main.log",
             "reference-gate final LaTeX log")
    includes(production, "--pdf book/build/AI-by-Intuition-Book.pdf",
             "reference-gate rendered PDF")
    gate_source = ROOT / "scripts" / "check_latex_references.py"
    if not gate_source.is_file():
        fail("Missing final-log/PDF unresolved-reference gate")
    import ast
    ast.parse(gate_source.read_text(encoding="utf-8"))


    notebook = subprocess.run([sys.executable, str(ROOT / 'scripts/check_p2_notebook.py')],
                              cwd=ROOT, capture_output=True, text=True)
    if notebook.returncode:
        fail('Interactive notebook regression: '+notebook.stdout+notebook.stderr)

    # The optional Torch companion is syntax-checked without requiring Torch at source-QA time.
    import ast
    for script in ("pytorch_starter.py", "teaching_trace.py"):
        script_path = ROOT / "scripts" / script
        if not script_path.is_file():
            fail(f"Missing P1 reproducibility script: {script}")
        ast.parse(script_path.read_text(encoding="utf-8"))
    includes(sources["24e-pytorch-lab"], "1.798430", "initial loss in lab")
    # Runnable, dependency-free examples must agree with the book after edits.
    for script in ("memory_demo.py", "bpe_demo.py", "rag_demo.py", "agent_loop.py"):
        script_path = ROOT / "scripts" / script
        if not script_path.is_file():
            fail(f"Missing reproducibility example: {script}")
        try:
            ast.parse(script_path.read_text(encoding="utf-8"))
        except SyntaxError as exc:
            fail(f"Invalid Python syntax in {script}: {exc}")
        result = subprocess.run([sys.executable, str(script_path)],
                                cwd=ROOT, capture_output=True, text=True)
        if result.returncode:
            fail(f"Reproducible {script} failed:\n{result.stdout}{result.stderr}")
    print("Independent teaching QA passed: memory, BPE, RAG and Agent loop")

    # Independent answer-key numerics for newly added user-review exercises.
    exercises_script = ROOT / "scripts" / "review_exercises_demo.py"
    if not exercises_script.is_file():
        fail("Missing review-exercises numerical reproducer")
    ast.parse(exercises_script.read_text(encoding="utf-8"))
    exercises_result = subprocess.run([sys.executable, str(exercises_script)],
                                      cwd=ROOT, capture_output=True, text=True)
    if (exercises_result.returncode
            or "Review exercises QA passed" not in exercises_result.stdout):
        fail("Review exercises numeric QA failed:\n"
             + exercises_result.stdout + exercises_result.stderr)


    # GPT-2 smoke is standard-library-only; real weights are explicitly opt-in.
    gpt2_source = ROOT / "scripts" / "gpt2_demo.py"
    if not gpt2_source.is_file():
        fail("Missing pinned GPT-2 experiment")
    ast.parse(gpt2_source.read_text(encoding="utf-8"))
    includes(gpt2_source.read_text(encoding="utf-8"),
             "607a30d783dfa663caf39e06633721c8d4cfcd7e",
             "pinned public GPT-2 revision")
    gpt2_result = subprocess.run([sys.executable, str(gpt2_source)],
                                 cwd=ROOT, capture_output=True, text=True)
    if gpt2_result.returncode or "Offline smoke passed:" not in gpt2_result.stdout:
        fail(f"GPT-2 offline smoke failed: {gpt2_result.stdout}{gpt2_result.stderr}")
    # Run IDs are maintainer provenance: keep them in the archived run record,
    # and keep the reader appendix pointing at that record.
    includes((ROOT / "CONTRIBUTING.md").read_text(encoding="utf-8"), "39897932969",
             "successful source-pinned real GPT-2 inference reference")
    run_record_anchor = quote("gpt-2-真实权重实验").replace("%", r"\%")
    includes(sources["29-revision-notes"], r"CONTRIBUTING.md\#" + run_record_anchor,
             "reader pointer to the archived real GPT-2 run record")
    includes(sources["23a-from-toy-to-gpt"], "gpt2_demo.py",
             "reproducible optional real GPT-2 example (verbatim command)")
    includes(gpt2_source.read_text(encoding="utf-8"), "masked_future",
             "real-model causal-mask numeric assertion")
    includes(gpt2_source.read_text(encoding="utf-8"), "probability sum",
             "real-model normalized vocabulary probabilities")

    # Modern architecture figures use pinned, inspectable offline source excerpts.
    for reproducible in ("config_table.py", "architecture_demo.py"):
        path = ROOT / "scripts" / reproducible
        if not path.is_file():
            fail(f"Missing modern architecture reproducer: {reproducible}")
        ast.parse(path.read_text(encoding="utf-8"))
        result = subprocess.run([sys.executable, str(path)], cwd=ROOT,
                                text=True, capture_output=True)
        if result.returncode:
            fail(f"Architecture example {reproducible} failed:\n"
                 + result.stdout + result.stderr)
    includes(sources["22d-modern-transformers"], "architecture\\_demo.py",
             "sliding-window and illustrative MLA arithmetic")

    # Visual-to-language adapter arithmetic is a deliberately untrained toy fixture.
    bridge_script = ROOT / "scripts" / "vision_bridge_demo.py"
    if not bridge_script.is_file():
        fail("Missing ViT-to-LLM shape reproducer")
    ast.parse(bridge_script.read_text(encoding="utf-8"))
    bridge_result = subprocess.run([sys.executable, str(bridge_script)],
                                   cwd=ROOT, capture_output=True, text=True)
    if bridge_result.returncode or "Vision bridge QA passed" not in bridge_result.stdout:
        fail("Vision bridge regression failed:\n"
             + bridge_result.stdout + bridge_result.stderr)
    includes(sources["19b-vit"], r"\label{eq:vit-llm-bridge}",
             "multimodal adapter teaching example")

    # Print-proof selector QA: must not require a PDF, Poppler or online access.
    import runpy
    proof_source = ROOT / "scripts" / "print_proof.py"
    if not proof_source.is_file():
        fail("Missing grayscale human print-proof tool")
    ast.parse(proof_source.read_text(encoding="utf-8"))
    select = runpy.run_path(str(proof_source), run_name="book_print_proof")["parse_pages"]
    if select("1,3-4,last", 8) != [1, 3, 4, 8]:
        fail("Grayscale proof page selections are incorrect")
    for bad_selection in ("0", "9", "5-2", ",", "not-a-page"):
        try:
            select(bad_selection, 8)
        except ValueError:
            continue
        fail(f"Grayscale proof accepted invalid page selection: {bad_selection}")
    # Human review provenance is not a substitute for a human approval.
    import hashlib
    import tempfile
    proof_helpers = runpy.run_path(str(proof_source), run_name="book_print_proof")
    with tempfile.TemporaryDirectory(prefix="proof-sha-qa-") as tmp:
        fixture = Path(tmp) / "fixture.pdf"
        fixture.write_bytes(b"%PDF-1.7\nsha-test-data\n")
        manifest = proof_helpers["build_manifest"](fixture, [1, 3], 1100,
                                                    "a" * 40)
        if (manifest["pdf_sha256"] != hashlib.sha256(fixture.read_bytes()).hexdigest()
                or manifest["source_commit_sha"] != "a" * 40
                or manifest["manual_review_completed"] is not False):
            fail("Proof provenance data did not match input bytes")
        # Reconcile the actual PDF digest and CI source/run provenance.
        reconcile = proof_helpers["bind_machine_audit"]
        audit_fixture = {
            "pdf_sha256": manifest["pdf_sha256"],
            "source_commit_sha": "a" * 40,
            "github_actions_run_id": 123456,
        }
        bound = reconcile(manifest, audit_fixture)
        if (bound["source_commit_sha"] != "a" * 40
                or bound["machine_audit_run_id"] != 123456
                or bound["machine_audit_pdf_hash_verified"] is not True
                or bound["manual_review_completed"] is not False):
            fail("Bound PDF audit provenance is incomplete or marked reviewed")
        for corrupted in (
            {**audit_fixture, "pdf_sha256": "b" * 64},
            {**audit_fixture, "source_commit_sha": "b" * 40},
            {**audit_fixture, "source_commit_sha": "invalid"},
            {**audit_fixture, "github_actions_run_id": 0},
        ):
            try:
                reconcile(manifest, corrupted)
            except ValueError:
                pass
            else:
                fail("Proof accepted audit with mismatched PDF/source/run provenance")
        try:
            proof_helpers["build_manifest"](fixture, [1], 1100, "abc")
        except ValueError:
            pass
        else:
            fail("Proof accepted a truncated commit SHA")

    print("Grayscale print-proof selector QA passed")

    # Machine grayscale preflight is distinct from the human proof checklist.
    audit_source = ROOT / "scripts" / "audit_grayscale_pdf.py"
    if not audit_source.is_file():
        fail("Missing grayscale full-PDF audit tool")
    ast.parse(audit_source.read_text(encoding="utf-8"))
    audit_test = subprocess.run(
        [sys.executable, str(audit_source), "--self-test"], cwd=ROOT,
        capture_output=True, text=True,
    )
    if audit_test.returncode or "Grayscale PDF audit self-test passed" not in audit_test.stdout:
        fail("Grayscale PDF audit self-test failed:\n"
             + audit_test.stdout + audit_test.stderr)


    # A ten-step oral mapping must remain complete and linked to its figure.
    block_ch22 = sources["22-transformer-architecture"]
    ten_steps = block_ch22.split(r"\label{sec:transformer-ten-steps}")[1]
    ten_steps = ten_steps.split(r"\end{enumerate}")[0]
    if len(re.findall(r"(?m)^\\item ", ten_steps)) != 10:
        fail("Transformer oral recap must have exactly ten steps")
    includes(block_ch22, r"\input{figures/original-transformer-map}",
             "source vs decoder-only architecture component mapping")
    original_map = (BOOK / "figures" / "original-transformer-map.tex").read_text(
        encoding="utf-8"
    )
    if not all(term in original_map.split(r"\tagstructbegin", 1)[1].split(
            r"\begin{center}", 1)[0]
            for term in ("Encoder", "Decoder", "Cross-Attention",
                         "FFN", "归一化", "因果")):
        fail("Original Transformer figure alt text lacks source/target or FFN detail")

    # These numbered chapters span two or more .tex files. Source checks and
    # recaps belong after their final subsection in every merged chapter.
    for early, late, check_id in (
        ("00-functions", "16-loss-gradient", "00-functions"),
        ("21c-naive-attention", "21b-why-attention", "21c-naive-attention"),
        ("23c-post-training", "23cc-test-time-compute", "23c-post-training"),
        ("04-key-value-outer-product", "06-better-linear-memory", "04-key-value-outer-product"),
        ("17-backpropagation", "18b-end-to-end-learning", "17-backpropagation"),
        ("08-stacking-key-value", "13-capacity", "09-nonlinearity-and-memory"),
        ("09-nonlinearity-and-memory", "13-capacity", "09-nonlinearity-and-memory"),
    ):
        marker = r"\chapterchecktasks{" + check_id + "}"
        if marker in sources[early] or marker not in sources[late]:
            fail(f"Chapter self-check not relocated to final subsection: {check_id}")
    labels = {label for source in sources.values() for label in re.findall(r"\\label\{([^}]+)\}", source)}
    REQUIRED = re.findall(r"\\input\{chapters/([^}]+)\}", main)
    for lex in ("24-lexicon", "24b-modern-lexicon"):
        refs = re.findall(r"\\termref\{([^}]+)\}", sources[lex])
        if lex == "24-lexicon":
            key_terms = {
                "交叉熵": "concept:cross-entropy",
                "梯度下降": "concept:gradient-descent",
                "残差连接": "concept:residual",
                "Token": "concept:token",
                "Query": "concept:qkv",
                "Key": "concept:qkv",
                "Value": "concept:qkv",
                "Self-Attention": "concept:self-attention",
                "Cross-Attention": "concept:cross-attention",
                "缩放点积": "concept:scaled-dot-product",
                "Softmax": "concept:softmax",
                "因果掩码": "concept:causal-mask",
                "多头注意力": "concept:multihead",
                "预训练": "concept:pretraining",
                "监督微调": "concept:sft",
                "RLHF": "concept:rlhf",
                "LoRA": "concept:lora",
                "Logits": "concept:logits",
                "温度": "concept:sampling",
                "Top-k": "concept:sampling",
                "Top-p": "concept:sampling",
                "RAG": "concept:rag",
                "MCP": "concept:mcp",
                "智能体": "concept:agent",
                "工作流": "concept:workflow",
                "量化": "concept:quant"
            }
            items = dict(re.findall(
                r"(?m)^\\item \\textbf\{([^}]+)\}.*?\\termref\{([^}]+)\}",
                sources[lex]))
            for term, destination in key_terms.items():
                if items.get(term) != destination:
                    fail(f"Foundation term {term} must link to {destination}, got {items.get(term)}")

        if lex == "24b-modern-lexicon" and any(not ref.startswith("concept:") for ref in refs):
            fail("Modern glossary must link to precise concept definitions, not chapter introductions")
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
    if table_envs < 23 or marked_headers != table_envs:
        fail(f"Table header coverage incomplete: {marked_headers}/{table_envs} (minimum 23)")

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
    print("Existing regressions passed: reproducible examples, proof provenance, directed figures, glossary targets and release gates")
