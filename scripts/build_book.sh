#!/usr/bin/env bash
# One entry point for local and CI builds; source archives may have no Git metadata.
set -euo pipefail
book_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
book_source_sha="${BOOK_BUILD_SHA:-${GITHUB_SHA:-}}"
if [[ -z "$book_source_sha" ]] && command -v git >/dev/null 2>&1; then
  book_source_sha="$(git -C "$book_root" rev-parse HEAD 2>/dev/null || true)"
fi
if [[ -n "$book_source_sha" && ! "$book_source_sha" =~ ^[[:xdigit:]]{7,64}$ ]]; then
  echo 'BOOK_BUILD_SHA must be a hexadecimal Git commit ID' >&2
  exit 1
fi
export BOOK_BUILD_SHA="$book_source_sha"
cd -- "$book_root/book"
mkdir -p build
book_provenance_flags=()
if [[ ! -f build/.source-revision ]] || [[ "$(< build/.source-revision)" != "$BOOK_BUILD_SHA" ]]; then
  printf '%s\n' "$BOOK_BUILD_SHA" > build/.source-revision
  # Environment changes alone are invisible to latexmk's dependency graph.
  book_provenance_flags=(-g)
fi
exec latexmk "${book_provenance_flags[@]}" -lualatex -interaction=nonstopmode -halt-on-error \
  -file-line-error -outdir=build "$@" main.tex
