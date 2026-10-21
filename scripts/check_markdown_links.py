#!/usr/bin/env python3
"""Check repository-local file targets in Markdown links (not remote URLs/anchors).

Only file existence is checked; network links and heading fragments are out of scope.
"""
from __future__ import annotations

from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
LINK = re.compile(r"""!?\[[^\]]*\]\((?P<dest><[^>]+>|[^\s)]+)(?:\s+['"][^'"]+['"])?\)""")


def check_file(markdown: Path) -> list[str]:
    errors: list[str] = []
    for number, line in enumerate(markdown.read_text(encoding="utf-8").splitlines(), 1):
        for match in LINK.finditer(line):
            raw = match.group("dest").strip("<>")
            if raw.startswith(("#", "//")):
                continue
            parsed = urlsplit(raw)
            if parsed.scheme or not parsed.path:
                continue
            path = unquote(parsed.path)
            target = (ROOT / path.lstrip("/")) if path.startswith("/") else (markdown.parent / path)
            if not target.exists():
                errors.append(f"{markdown.relative_to(ROOT)}:{number}: missing local link: {raw}")
    return errors


def main() -> int:
    markdown_files = sorted(p for p in ROOT.rglob("*.md") if ".git" not in p.parts)
    errors = [error for path in markdown_files for error in check_file(path)]
    for error in errors:
        print(error)
    print(f"Checked local link targets in {len(markdown_files)} Markdown files; errors={len(errors)}")
    return int(bool(errors))


if __name__ == "__main__":
    raise SystemExit(main())
