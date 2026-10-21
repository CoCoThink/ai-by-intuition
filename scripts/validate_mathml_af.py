#!/usr/bin/env python3
"""Check every Formula in an experimental tagged PDF has parseable MathML via AF.

This tests PDF attachment integrity, not mathematical correctness or PDF/UA
conformance. It is intended for experiment/full-book-mathml only.
"""
from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

from pypdf import PdfReader

MATHML_NS = "http://www.w3.org/1998/Math/MathML"


def walk(root):
    stack = [root]
    while stack:
        node = stack.pop()
        if hasattr(node, "get_object"):
            node = node.get_object()
        if isinstance(node, list):
            stack.extend(node)
        elif isinstance(node, dict):
            if "/S" in node:
                yield node
            if "/K" in node:
                stack.append(node["/K"])


def verify(pdf: Path, minimum: int) -> dict:
    reader = PdfReader(str(pdf))
    catalog = reader.trailer["/Root"]
    if "/StructTreeRoot" not in catalog:
        raise ValueError("PDF lacks StructTreeRoot")
    formulas = [n for n in walk(catalog["/StructTreeRoot"]["/K"])
                if n.get("/S") == "/Formula"]
    if len(formulas) < minimum:
        raise ValueError(f"Expected at least {minimum} Formula nodes; found {len(formulas)}")
    cached = {}
    digests = set()
    relations = Counter()
    failures = []
    for index, formula in enumerate(formulas, 1):
        associated = formula.get("/AF")
        if not isinstance(associated, list) or not associated:
            failures.append(f"Formula {index}: missing AF")
            continue
        for item in associated:
            key = (item.idnum, item.generation) if hasattr(item, "idnum") else id(item)
            if key not in cached:
                try:
                    spec = item.get_object() if hasattr(item, "get_object") else item
                    embedded = spec["/EF"]["/F"].get_object().get_data()
                    math = ET.fromstring(embedded)
                    if math.tag != f"{{{MATHML_NS}}}math" or len(math) == 0:
                        raise ValueError("missing MathML math root or expression")
                    cached[key] = (sha256(embedded).hexdigest(),
                                   str(spec.get("/AFRelationship", "")))
                except (ET.ParseError, KeyError, ValueError, TypeError) as exc:
                    failures.append(f"Formula {index}: broken associated MathML: {exc}")
                    continue
            digest, relationship = cached[key]
            digests.add(digest)
            relations[relationship] += 1
            if relationship != "/Supplement":
                failures.append(f"Formula {index}: AFRelationship {relationship} != /Supplement")
    if failures:
        raise ValueError("; ".join(failures[:8]) +
                         (f" (+{len(failures)-8} further errors)" if len(failures) > 8 else ""))
    return {"pages": len(reader.pages), "formulas": len(formulas),
            "associations": sum(relations.values()),
            "unique_mathml_documents": len(digests),
            "relationships": dict(relations)}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("pdf", type=Path)
    ap.add_argument("--minimum", type=int, default=1000)
    ap.add_argument("--json-output", type=Path)
    args = ap.parse_args()
    try:
        outcome = verify(args.pdf, args.minimum)
    except (OSError, ValueError) as exc:
        print(f"MathML-AF QA FAILED: {exc}", file=sys.stderr)
        return 1
    print("MathML-AF QA PASSED: " + json.dumps(outcome, ensure_ascii=False))
    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(json.dumps(outcome, ensure_ascii=False, indent=2)+"\n",
                                    encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
