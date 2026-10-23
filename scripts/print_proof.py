#!/usr/bin/env python3
"""Render a grayscale page proof for human inspection without modifying the PDF.

Requires Poppler's pdfinfo and pdftoppm, but no pip packages or internet.
Examples:
  python3 scripts/print_proof.py book/build/main.pdf --pages 1,2,3,last
  python3 scripts/print_proof.py book/build/main.pdf --pages 64-68,79,89
  python3 scripts/print_proof.py book/build/main.pdf --all --scale 900
"""
from __future__ import annotations

import argparse
import html
import re
import shutil
import subprocess
from pathlib import Path


def count_pages(pdf: Path) -> int:
    run = subprocess.run(["pdfinfo", str(pdf)], check=True,
                         text=True, capture_output=True)
    match = re.search(r"(?m)^Pages:\s*(\d+)\s*$", run.stdout)
    if not match:
        raise RuntimeError("pdfinfo returned no page count")
    return int(match.group(1))


def parse_pages(text: str, count: int) -> list[int]:
    pages: set[int] = set()
    for part in text.split(","):
        part = part.strip().lower()
        if part == "last":
            pages.add(count)
        elif re.fullmatch(r"\d+", part):
            pages.add(int(part))
        elif re.fullmatch(r"\d+-\d+", part):
            start, end = (int(v) for v in part.split("-", 1))
            if end < start:
                raise ValueError(f"Descending page range: {part}")
            pages.update(range(start, end + 1))
        else:
            raise ValueError(f"Unsupported page selector: {part!r}")
    if not pages or min(pages) < 1 or max(pages) > count:
        raise ValueError(f"Page selection must be between 1 and {count}")
    return sorted(pages)


def render_pages(pdf: Path, out: Path, pages: list[int], scale: int) -> None:
    out.mkdir(parents=True, exist_ok=True)
    for page in pages:
        prefix = out / f"page-{page:03d}"
        subprocess.run([
            "pdftoppm", "-f", str(page), "-l", str(page),
            "-singlefile", "-gray", "-scale-to", str(scale),
            "-png", str(pdf), str(prefix)
        ], check=True, capture_output=True, text=True)
        if not prefix.with_suffix(".png").is_file():
            raise RuntimeError(f"Missing output PNG for page {page}")


def write_review_materials(pdf: Path, out: Path, pages: list[int]) -> None:
    title = html.escape(pdf.name)
    gallery = "\n".join(
        f'<section><h2>PDF page {n}</h2><img loading="lazy" '
        f'src="page-{n:03d}.png" alt="Grayscale page {n}"></section>'
        for n in pages
    )
    html_doc = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<title>Print proof — {title}</title>
<style>
body {{font:16px/1.5 system-ui,sans-serif;background:#ddd;color:#111;
       max-width:1040px;margin:auto;padding:1rem}}
section {{margin:2rem 0;padding:1rem;background:white}}
img {{max-width:100%;height:auto;display:block;margin:auto}}
@media print {{body {{background:white}} section {{break-after:page}}}}
</style></head><body>
<h1>Grayscale proof: {title}</h1>
<p>Human-review aid only. PDF/UA-2 compliance and screen-reader behavior are
not established by grayscale rendering. The source PDF was not modified.</p>
{gallery}</body></html>
'''
    (out / "index.html").write_text(html_doc, encoding="utf-8")
    checklist = [
        f"# Manual grayscale proof — {pdf.name}", "",
        "Rendering is not a manual review or release approval.", "",
        "Review labels without color, contrast, tables, images, equations,",
        "visible citations, clipping and logical reading order.", "",
    ]
    for n in pages:
        checklist += [
            f"## PDF page {n}",
            "- [ ] Critical distinctions are clear without relying on color",
            "- [ ] Formulas, tables, figures, and references are not clipped",
            "- [ ] Labels and intended reading flow remain understandable",
            "- [ ] Source/copyright issues recorded where relevant",
            "- [ ] Reviewer, date and evidence: ______", "",
        ]
    (out / "CHECKLIST.md").write_text("\n".join(checklist), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdf", type=Path)
    parser.add_argument("--out-dir", type=Path, default=Path("build/print-proof"))
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--pages", default="1,2,3,last",
                       help="comma-separated pages, inclusive ranges and last")
    group.add_argument("--all", action="store_true", help="render every page")
    parser.add_argument("--scale", type=int, default=1100,
                        help="maximum image dimension, pixels (300–2400)")
    args = parser.parse_args()
    if not args.pdf.is_file():
        parser.error(f"PDF not found: {args.pdf}")
    if not 300 <= args.scale <= 2400:
        parser.error("--scale must be between 300 and 2400")
    for tool in ("pdfinfo", "pdftoppm"):
        if shutil.which(tool) is None:
            parser.error(f"Missing Poppler tool: {tool}")
    try:
        total = count_pages(args.pdf)
        pages = list(range(1, total + 1)) if args.all else parse_pages(args.pages, total)
        render_pages(args.pdf, args.out_dir, pages, args.scale)
        write_review_materials(args.pdf, args.out_dir, pages)
    except (ValueError, RuntimeError, subprocess.CalledProcessError) as exc:
        parser.error(str(exc))
    print(f"Rendered {len(pages)}/{total} grayscale pages to {args.out_dir}")
    print("Review index.html and CHECKLIST.md; do not treat output as sign-off")


if __name__ == "__main__":
    main()
