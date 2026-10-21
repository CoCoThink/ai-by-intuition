#!/usr/bin/env python3
"""Inspect actual PDF heading tags (not TOC/bookmarks or RoleMap declarations).

Designed for separate heading experiments and eventual full-book regression.
The checker prints observed tag counts. Exit code 1 with --require-headings
when both H1 and H2 nodes are not found.
"""
import argparse
from collections import Counter
from pathlib import Path
from pypdf import PdfReader


def roles_in_pdf(path):
    reader = PdfReader(str(path))
    root = reader.trailer["/Root"].get("/StructTreeRoot")
    if not root:
        return Counter()
    root = root.get_object() if hasattr(root, "get_object") else root
    roles = Counter()
    stack = [root.get("/K")]
    while stack:
        node = stack.pop()
        if hasattr(node, "get_object"):
            node = node.get_object()
        if isinstance(node, list):
            stack.extend(node)
        elif isinstance(node, dict):
            role = node.get("/S")
            if role:
                roles[str(role)] += 1
            if "/K" in node:
                stack.append(node["/K"])
    return roles


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf", type=Path)
    parser.add_argument("--require-headings", action="store_true")
    args = parser.parse_args()
    counts = roles_in_pdf(args.pdf)
    print(f"{args.pdf.name}: H1={counts['/H1']}, H2={counts['/H2']}, "
          f"section={counts['/section']}, subsection={counts['/subsection']}, "
          f"Sect={counts['/Sect']}, TOCI={counts['/TOCI']}")
    heading_1 = counts["/H1"] + counts["/section"]
    heading_2 = counts["/H2"] + counts["/subsection"]
    if args.require_headings and not (heading_1 >= 1 and heading_2 >= 1):
        parser.exit(1, "Missing H1/H2-equivalent structure nodes\n")


if __name__ == "__main__":
    main()
