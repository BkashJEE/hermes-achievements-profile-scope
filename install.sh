#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
DEFAULT_HERMES_DIR="${HERMES_AGENT_ROOT:-$HOME/.hermes/hermes-agent}"

if [[ -x "$DEFAULT_HERMES_DIR/venv/bin/python" ]]; then
  PYTHON="$DEFAULT_HERMES_DIR/venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON="$(command -v python3)"
elif command -v python >/dev/null 2>&1; then
  PYTHON="$(command -v python)"
else
  echo "Error: Python was not found. Install Hermes Agent first, then try again." >&2
  exit 1
fi

exec "$PYTHON" "$SCRIPT_DIR/install.py" "$@"
