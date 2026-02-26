#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PACKAGE_DIR="$REPO_ROOT/packages/distill_lib"

TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT

python3 -m venv "$TMP_DIR/venv"
PY="$TMP_DIR/venv/bin/python"
PIP="$TMP_DIR/venv/bin/pip"

"$PY" -m pip install -q --upgrade pip

# Editable install flow (skill/path consumption)
"$PIP" install -q --no-deps -e "$PACKAGE_DIR"
"$PY" - <<'PY'
import json
import distill_lib
from distill_lib.api import run_workflow_from_articles

print("editable=" + json.dumps({
    "distill_lib_file": distill_lib.__file__,
    "has_run_workflow_from_articles": callable(run_workflow_from_articles),
}))
PY

"$PIP" uninstall -y -q distill-lib

# Standalone path install flow
"$PIP" install -q --no-deps "$PACKAGE_DIR"
"$PY" - <<'PY'
import json
import distill_lib
from distill_lib.api import run_workflow_from_articles

print("path=" + json.dumps({
    "distill_lib_file": distill_lib.__file__,
    "has_run_workflow_from_articles": callable(run_workflow_from_articles),
}))
PY

echo "distill_lib package verification passed"
