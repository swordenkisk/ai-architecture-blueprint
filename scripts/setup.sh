#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

PYTHON_BIN="${PYTHON_BIN:-python3}"

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  echo "Error: Python 3.11 or newer is required." >&2
  exit 1
fi

"$PYTHON_BIN" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)' || {
  echo "Error: Python 3.11 or newer is required." >&2
  exit 1
}

"$PYTHON_BIN" -m venv .venv

if [[ -f .venv/bin/activate ]]; then
  # shellcheck disable=SC1091
  source .venv/bin/activate
else
  # shellcheck disable=SC1091
  source .venv/Scripts/activate
fi

python -m pip install --upgrade pip
python -m pip install -e .

echo
echo "Setup complete."
echo "Activate the environment with:"
echo "  source .venv/bin/activate"
echo "Then try:"
echo "  aibp build examples/architecture.json"
