#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

cd "$REPO_ROOT"
uv sync
uv pip install -e packages/distill_lib

echo "distill_lib editable install ready"
