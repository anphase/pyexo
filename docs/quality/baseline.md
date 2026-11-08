# Quality baselines

Measured 2026-11-08 on `exo/` (Python 3.15, pytest-cov, radon). `scripts/ci-local.sh` fails if
either number gets worse; raise the bar here and in the script's `MIN_COVERAGE` / `MAX_CC` when
it improves, never lower it.

| Measure | Baseline | Ratchet |
|---|---|---|
| Line coverage (`pytest --cov=exo`) | 100% (387 statements, 0 missed) | `MIN_COVERAGE=100` |
| Highest cyclomatic complexity of any function | 11 (`Credentials.__init__`, rank C) | `MAX_CC=11` |
| Average cyclomatic complexity | 2.48 (rank A, 73 blocks) | not gated |

Next highest: `_send` 10, `_pages` 8, `_sleep` 6, `_request` 6 (all in `exo/basemanager.py`).

Reproduce: `pip install -e '.[dev]'`, then `pytest --cov=exo` and `radon cc exo -s -a`.
