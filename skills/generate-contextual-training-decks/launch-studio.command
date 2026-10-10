#!/bin/bash
set -euo pipefail

cd "$(dirname "$0")"
PYTHON_BIN="${PYTHON_BIN:-python3}"

if [[ ! -x .venv/bin/python ]]; then
  "$PYTHON_BIN" -m venv .venv
  .venv/bin/pip install -r scripts/requirements.txt
fi

exec .venv/bin/python scripts/studio.py --open --data-dir ./studio-runs
