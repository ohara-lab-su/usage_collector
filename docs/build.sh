#!/usr/bin/env bash
set -euo pipefail
DOCS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "$DOCS_DIR/.." && pwd)"
export LANG=C.UTF-8
export PYTHONPATH="$REPO_DIR/src${PYTHONPATH:+:$PYTHONPATH}"
if [ ! -d "$REPO_DIR/src/usage_collector" ]; then
    echo "Python package not found: $REPO_DIR/src/usage_collector" >&2
    exit 1
fi
# 共通形式: Sphinx + MyST、英語 / と /en/、日本語 /ja/。
python -m sphinx --version >/dev/null 2>&1 || python -m pip install 'sphinx>=7' 'myst-parser>=2' 'sphinx-rtd-theme>=2'
rm -rf "$DOCS_DIR/_build/html"
mkdir -p "$DOCS_DIR/_build/html/en" "$DOCS_DIR/_build/html/ja"
python -m sphinx.ext.apidoc -f -o "$DOCS_DIR/en/generated_api" "$REPO_DIR/src/usage_collector"
python -m sphinx.ext.apidoc -f -o "$DOCS_DIR/ja/generated_api" "$REPO_DIR/src/usage_collector"
python -m sphinx -b html -c "$DOCS_DIR" -D language=en "$DOCS_DIR/en" "$DOCS_DIR/_build/html/en"
python -m sphinx -b html -c "$DOCS_DIR" -D language=ja "$DOCS_DIR/ja" "$DOCS_DIR/_build/html/ja"
python -m sphinx -b html -c "$DOCS_DIR" -D language=en "$DOCS_DIR/en" "$DOCS_DIR/_build/html"
