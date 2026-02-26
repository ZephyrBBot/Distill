#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_PYTHON="${VENV_PYTHON:-$REPO_ROOT/.venv/bin/python}"

if [[ ! -x "$VENV_PYTHON" ]]; then
  echo "VENV_PYTHON not found: $VENV_PYTHON" >&2
  echo "Set VENV_PYTHON to your virtualenv python (or run uv sync first)." >&2
  exit 1
fi

cd "$REPO_ROOT"
if command -v uv >/dev/null 2>&1; then
  uv sync
fi

if ! "$VENV_PYTHON" -m pip --version >/dev/null 2>&1; then
  echo "pip is unavailable in $VENV_PYTHON" >&2
  echo "Use a virtualenv with pip/uv support, then rerun this script." >&2
  exit 1
fi

"$VENV_PYTHON" -m pip install -e packages/distill_lib

"$VENV_PYTHON" - <<'PY'
import json
import distill_lib
from distill_lib.api import run_workflow_from_articles

print(json.dumps({
    "distill_lib_file": distill_lib.__file__,
    "has_run_workflow_from_articles": callable(run_workflow_from_articles),
}))
PY

echo "distill_lib editable install ready"
