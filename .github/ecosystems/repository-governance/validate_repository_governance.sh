#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VALIDATOR_PY="${SCRIPT_DIR}/validate_repository_governance.py"

if [[ ! -f "${VALIDATOR_PY}" ]]; then
  echo "Validator script not found: ${VALIDATOR_PY}" >&2
  exit 1
fi

if command -v python3 >/dev/null 2>&1; then
  PYTHON_CMD="python3"
elif command -v python >/dev/null 2>&1; then
  PYTHON_CMD="python"
else
  echo "python interpreter not found" >&2
  exit 1
fi

"${PYTHON_CMD}" "${VALIDATOR_PY}" "$@"