#!/usr/bin/env bash
# Full local gate: lint, types, tests, then the coverage and complexity ratchet
# (baselines in docs/quality/baseline.md; only ever raise the bar).
set -euo pipefail
cd "$(dirname "$0")/.."
[ -d .venv ] && PATH="$PWD/.venv/bin:$PATH"

MIN_COVERAGE=100
MAX_CC=11

scripts/check.sh
pytest -q --cov=exo --cov-report= --cov-fail-under="$MIN_COVERAGE"

radon cc exo -j | python3 -c '
import json, sys
limit = int(sys.argv[1])
bad = [(b["complexity"], f, b["name"]) for f, bs in json.load(sys.stdin).items()
       for b in bs if b["complexity"] > limit]
for c, f, n in sorted(bad, reverse=True):
    print(f"complexity {c} > {limit}: {f} {n}")
sys.exit(1 if bad else 0)
' "$MAX_CC"
echo "ci-local: ok (coverage >= ${MIN_COVERAGE}%, complexity <= ${MAX_CC})"
