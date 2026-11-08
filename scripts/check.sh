#!/usr/bin/env bash
# Run lint, type checks and tests (uses ./.venv if present).
set -euo pipefail
cd "$(dirname "$0")/.."
[ -d .venv ] && PATH="$PWD/.venv/bin:$PATH"
ruff check exo tests examples
ruff format --check exo tests examples
mypy --strict exo
pytest --cov=exo --cov-report=term-missing --cov-fail-under=90
