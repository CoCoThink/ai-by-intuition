#!/usr/bin/env python3
"""Machine-only grayscale preflight for a PDF; requires Poppler, not pip.

Inspect every page at the SAME rendering scale. Check pages exist, detect
near-empty pages and ink touching the image edge. This is NOT visual,
accessibility or copyright sign-off and must never mark manual review done.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile


def count_pages(pdf: Path) -> int:
    text = subprocess.run(
        ["pdfinfo", str(pdf)], check=True, capture_output=True, text=True
    ).stdout
    match = re.search(r"(?m)^Pages:\s*(\d+)\s*$", text)
    if not match:
        raise ValueError("pdfinfo provided no page count")
    return int(match.group(1))


def analyze_pgm(payload: bytes, cutoff: int = 220, margin: int = 4) -> dict:
    """Read Poppler's binary P5 output with an 8-bit grayscale max."""
    match = re.match(rb"\AP5\s+(\d+)\s+(\d+)\s+255\s", payload)
    if not match:
        raise ValueError("Expected binary 8-bit P5 PGM from pdftoppm -gray")
    width, height = map(int, match.groups())
    pixels = payload[match.end():]
    if len(pixels) != width * height:
        raise ValueError("Truncated or oversized grayscale page")
    ink = sum(pixel < cutoff for pixel in pixels)
    edge = 0
    for y in range(height):
        start = y * width
        if y < margin or y >= height - margin:
            edge += sum(pixel < cutoff for pixel in pixels[start:start + width])
        else:
            edge += sum(pixel < cutoff for pixel in pixels[start:start + margin])
            edge += sum(pixel < cutoff for pixel in pixels[start + width - margin:start + width])
    return {
        "width": width,
        "height": height,
        "ink_fraction": round(ink / (width * height), 6),
        "edge_ink_pixels": edge,
    }


def run_audit(pdf: Path, scale: int, min_ink: float, max_edge: int) -> dict:
    if not pdf.is_file():
        raise ValueError(f"Missing PDF: {pdf}")
    count = count_pages(pdf)
    if not count:
        raise ValueError("PDF has no pages")
    pages = []
    with tempfile.TemporaryDirectory(prefix="grayscale-audit-") as directory:
        prefix = Path(directory) / "page"
        for page in range(1, count + 1):
            subprocess.run(
                ["pdftoppm", "-f", str(page), "-l", str(page), "-singlefile",
                 "-gray", "-scale-to", str(scale), str(pdf), str(prefix)],
                check=True, capture_output=True, text=True,
            )
            pgm = prefix.with_suffix(".pgm")
            if not pgm.is_file():
                raise ValueError(f"Page {page} missing from renderer")
            data = analyze_pgm(pgm.read_bytes())
            pgm.unlink()
            pages.append({"page": page, **data})
    blank = [p["page"] for p in pages if p["ink_fraction"] < min_ink]
    touched = [p["page"] for p in pages if p["edge_ink_pixels"] > max_edge]
    return {
        "pdf_sha256": hashlib.sha256(pdf.read_bytes()).hexdigest(),
        "page_count": count,
        "renderer": "pdftoppm grayscale P5 at fixed scale",
        "scale": scale,
        "min_ink_fraction": min_ink,
        "max_allowed_edge_ink_pixels": max_edge,
        "lowest_ink_page": min(pages, key=lambda p: p["ink_fraction"]),
        "blank_suspects": blank,
        "edge_touch_suspects": touched,
        "rendered_pages": len(pages),
        "manual_review": "NOT COMPLETED - rendering and pixel checks are only preflight",
        "machine_preflight_ok": not blank and not touched,
        "pages": pages,
    }


def self_test() -> None:
    # Binary white 10x10 image, one dark pixel away from all borders.
    pixels = bytearray([255] * 100)
    pixels[55] = 0
    image = b"P5\n10 10\n255\n" + pixels
    data = analyze_pgm(image)
    assert data["ink_fraction"] == 0.01
    assert data["edge_ink_pixels"] == 0
    pixels[0] = 0
    assert analyze_pgm(b"P5\n10 10\n255\n" + pixels)["edge_ink_pixels"] >= 1
    for corrupt in (b"P2\n10 10\n255\n", b"P5\n10 10\n255\nbad"):
        try:
            analyze_pgm(corrupt)
        except ValueError:
            pass
        else:
            raise AssertionError("Invalid PGM was accepted")
    print("Grayscale PDF audit self-test passed")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdf", type=Path, nargs="?")
    parser.add_argument("--scale", type=int, default=500)
    parser.add_argument("--min-ink", type=float, default=0.005)
    parser.add_argument("--max-edge", type=int, default=4)
    parser.add_argument("--json", type=Path, help="write machine audit JSON")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return
    if args.pdf is None:
        parser.error("PDF is required unless --self-test is used")
    if not (300 <= args.scale <= 1200):
        parser.error("--scale must be 300..1200")
    if not (0 < args.min_ink < 1):
        parser.error("--min-ink must be between 0 and 1")
    if args.max_edge < 0:
        parser.error("--max-edge must not be negative")
    try:
        report = run_audit(args.pdf, args.scale, args.min_ink, args.max_edge)
    except (ValueError, subprocess.CalledProcessError) as exc:
        parser.error(str(exc))
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n",
                             encoding="utf-8")
    print(f"Rendered {report['rendered_pages']}/{report['page_count']} grayscale pages")
    print(f"Lowest ink: {report['lowest_ink_page']['page']}, "
          f"{report['lowest_ink_page']['ink_fraction']:.3%}")
    print(f"Blank suspects: {report['blank_suspects']}")
    print(f"Edge-touch suspects: {report['edge_touch_suspects']}")
    print("MANUAL REVIEW NOT COMPLETED")
    if not report["machine_preflight_ok"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
