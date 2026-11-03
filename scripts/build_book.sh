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
# Relative output paths are resolved from the repository, not the caller's cwd.
book_output_dir="${BOOK_BUILD_DIR:-book/build}"
if [[ "$book_output_dir" != /* ]]; then
  book_output_dir="$book_root/$book_output_dir"
fi
mkdir -p -- "$book_output_dir"
book_output_dir="$(cd -- "$book_output_dir" && pwd -P)"
for book_arg in "$@"; do
  case "$book_arg" in
    -outdir*|-output-directory*)
      echo 'Set BOOK_BUILD_DIR instead of passing an output-directory option' >&2
      exit 1
      ;;
  esac
done
cd -- "$book_root/book"
book_provenance_flags=()
if [[ ! -f "$book_output_dir/.source-revision" ]] || [[ "$(< "$book_output_dir/.source-revision")" != "$BOOK_BUILD_SHA" ]]; then
  # Environment changes alone are invisible to latexmk's dependency graph.
  book_provenance_flags=(-g)
fi
latexmk "${book_provenance_flags[@]}" -lualatex -interaction=nonstopmode -halt-on-error \
  -file-line-error "-outdir=$book_output_dir" "$@" main.tex
# A failed build must not mark a new revision as successfully compiled.
printf '%s\n' "$BOOK_BUILD_SHA" > "$book_output_dir/.source-revision"
