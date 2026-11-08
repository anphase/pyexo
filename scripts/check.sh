#!/usr/bin/env bash
# Run lint, type checks and tests.
set -euo pipefail
cd "$(dirname "$0")/.."
ruff check exo tests examples
mypy --strict exo
pytest --cov=exo --cov-report=term-missing --cov-fail-under=90
