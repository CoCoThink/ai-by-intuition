#!/usr/bin/env bash
# CI-only cache staging: never restore a PDF or latexmk's up-to-date state.
set -euo pipefail

if [[ "${1:-}" == environment && "$#" == 1 ]]; then
  book_tex_root="$(kpsewhich -var-value=TEXMFROOT)"
  {
    lualatex --version
    latexmk -v
    sha256sum "$book_tex_root/tlpkg/texlive.tlpdb"
    dpkg-query -W -f='${binary:Package}=${Version}\n' fonts-noto-cjk fonts-noto-core
  } | sha256sum | cut -d ' ' -f 1
  exit 0
fi

if [[ "$#" != 4 || ! "$4" =~ ^[[:xdigit:]]{64}$ ]]; then
  echo 'Usage: book_build_cache.sh environment | {restore|save} CACHE_DIR BUILD_DIR ENVIRONMENT_SHA256' >&2
  exit 1
fi
book_cache_mode="$1"
book_cache_dir="$2"
book_build_dir="$3"
book_cache_environment="$4"
book_aux_files=(
  main.aux main.toc main.out main.lof main.lot main-luamml-mathml.html
  smoke/smoke-tagging.aux smoke/smoke-tagging.toc smoke/smoke-tagging.out
  smoke/smoke-tagging-luamml-mathml.html
)

case "$book_cache_mode" in
  restore)
    if [[ ! -f "$book_cache_dir/.environment" ]] || \
        [[ "$(< "$book_cache_dir/.environment")" != "$book_cache_environment" ]]; then
      echo 'Auxiliary cache miss: no matching TeX/font environment'
      exit 0
    fi
    book_restored=0
    for book_aux in "${book_aux_files[@]}"; do
      if [[ -f "$book_cache_dir/$book_aux" ]]; then
        mkdir -p -- "$(dirname -- "$book_build_dir/$book_aux")"
        cp -p -- "$book_cache_dir/$book_aux" "$book_build_dir/$book_aux"
        book_restored=$((book_restored + 1))
      fi
    done
    echo "Auxiliary cache restored: $book_restored files; PDF will be rebuilt"
    ;;
  save)
    mkdir -p -- "$book_cache_dir"
    # Invalidate the manifest until every copy has succeeded.
    rm -f -- "$book_cache_dir/.environment"
    for book_aux in "${book_aux_files[@]}"; do
      if [[ -f "$book_build_dir/$book_aux" ]]; then
        mkdir -p -- "$(dirname -- "$book_cache_dir/$book_aux")"
        cp -p -- "$book_build_dir/$book_aux" "$book_cache_dir/$book_aux"
      else
        rm -f -- "$book_cache_dir/$book_aux"
      fi
    done
    printf '%s\n' "$book_cache_environment" > "$book_cache_dir/.environment"
    echo 'Auxiliary cache staged; GitHub saves it only after all gates succeed'
    ;;
  *)
    echo "Unknown cache operation: $book_cache_mode" >&2
    exit 1
    ;;
esac
