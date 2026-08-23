#!/usr/bin/env bash
# Tiện ích chạy debug_figure_matching.py bằng đúng venv của backend (đã có fitz/pydantic_ai/openai).
set -euo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$DIR/../../.." && pwd)"
PYTHON_BIN="$REPO_ROOT/backend/services/api/.venv/bin/python"

if [ ! -x "$PYTHON_BIN" ]; then
  echo "Không thấy venv backend tại $PYTHON_BIN — xem README.md để biết cách tạo venv." >&2
  exit 1
fi

exec "$PYTHON_BIN" "$DIR/debug_figure_matching.py" "$@"
