#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

REQ_FILE="requirements.txt"

# Ensure a usable Python is available
if command -v python3 >/dev/null 2>&1; then
  PYTHON=python3
elif command -v python >/dev/null 2>&1; then
  PYTHON=python
else
  echo "No Python interpreter found. Install Python 3." >&2
  exit 1
fi

# Create virtualenv if missing
if [[ ! -d ".venv" ]]; then
  echo "Creating virtual environment in .venv..."
  "$PYTHON" -m venv .venv
fi

# If `uv` is available, use it to install/run the project
if command -v uv >/dev/null 2>&1; then
  echo "Detected 'uv' — using 'uv' to manage and run the project."
  if [[ -f "pyproject.toml" ]]; then
    echo "Running: uv sync"
    uv sync
  fi
  exec uv run main.py "$@"
fi

# Activate the venv
# shellcheck disable=SC1091
source ".venv/bin/activate"

# Upgrade pip and install requirements if present
if [[ -f "$REQ_FILE" ]]; then
  echo "Installing dependencies from $REQ_FILE..."
  python -m pip install --upgrade pip
  python -m pip install -r "$REQ_FILE"
fi

exec python main.py "$@"
